# EPIC-40: Pipeline 节点完成语义与状态污染修复

**Epic ID**: EPIC-40  
**Epic 名称**: Pipeline 节点完成语义与状态污染修复  
**优先级**: P0（CRITICAL）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-28）  
**创建日期**: 2026-04-28  
**研究来源**: `docs/research/2026-04-28-winerror5-architecture-refactor/02-langgraph-completion-semantics-state-pollution.md`  
**预估工作量**: ~8 hours (~1 day)

---

## Epic 概述

当前 DocuSwarm 存在 **三处完成语义冲突**，导致即使所有节点都因 `WinError 5` 而失败，最终结果仍同时携带 `completed_nodes=['analyst',...]`、`status='completed'` 和 `error=...`，形成不可恢复的状态污染。

**核心问题**：
1. **R2**: `graph.py` 在 `PipelineAdapter` 转换后**无条件**将节点追加到 `completed_nodes`，覆盖了 adapter 的失败路由
2. **R3**: `finalize_pipeline_state()` **无条件**设置 `status=COMPLETED`，不检查 `failed_nodes` 或 `error`
3. **R4**: `orchestrator._determine_final_status()` 作为**事后修正**，无法消除 LangGraph checkpoint 和返回结果中的矛盾状态

**推荐方案**：建立单一的"节点完成门控"策略，禁止失败节点进入 `completed_nodes`，禁止 finalizer 盲目标记完成。

---

## 背景与技术分析

### 合法状态组合

| completed_nodes | failed_nodes | status | error | 合法性 |
|-----------------|--------------|--------|-------|--------|
| `['analyst']` | `[]` | `running` | `None` | ✅ 正常执行中 |
| `['analyst','pm']` | `[]` | `completed` | `None` | ✅ 全部成功 |
| `[]` | `['analyst']` | `failed` | `{...}` | ✅ 首节点失败 |
| `['analyst','pm','ux','architect','po']` | `['analyst',...]` | `completed` | `{...}` | ❌ **矛盾状态（当前出现）** |

### R2: graph.py 覆盖 adapter 的失败语义

`graph.py` 的 `_create_integrated_node_executor()` 在 adapter 转换之后：

```python
# graph.py ~lines 146-152（问题代码）
if node_id not in result_state["completed_nodes"]:
    result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

这段代码**完全不检查节点状态**，无论 `result_state` 中是否已经将该节点标记为失败，都强行追加到 `completed_nodes`。

### R3: finalize_pipeline_state() 盲目标记完成

```python
# pipeline/state.py ~lines 285-315（问题代码）
def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    result = copy.deepcopy(state)
    result["status"] = COMPLETED  # 无条件设置
    return result
```

### R4: 状态所有权的双重真相

DocuSwarm 的 pipeline 状态至少经过三个独立写入者：LangGraph checkpoint、graph.py finalize_executor、orchestrator._determine_final_status() + update_pipeline_state()。三者之间没有单一的派生规则。

---

## Stories

### Story 40.1: 修复 graph.py 无条件 completed_nodes 追加

**目标**：删除或条件化 `graph.py` 中覆盖 adapter 失败语义的 `completed_nodes` 追加逻辑。

**涉及文件**：1 个（`autoBMAD/docuswarm/pipeline/graph.py`）

#### 验收标准

- [ ] `graph.py` 的 `_create_integrated_node_executor()` 中，节点执行后追加 `completed_nodes` 前检查该节点是否在 `failed_nodes` 中
- [ ] 异常路径返回后，不再执行 `completed_nodes` 追加（修复 try/except 后的覆盖逻辑）
- [ ] 修复后，adapter 将 FAILED 节点路由到 `failed_nodes` 后，graph.py 不再覆盖
- [ ] `node_iterations` 仅在成功完成时递增（异常路径不递增）
- [ ] 向后兼容：不影响正常成功执行的语义

#### 技术规格

```python
# 修复后
current_iteration = result_state["node_iterations"].get(node_id, 0)
result_state["node_iterations"][node_id] = current_iteration + 1

# 仅当节点不在 failed_nodes 中时才加入 completed_nodes
if node_id not in result_state.get("failed_nodes", []):
    if node_id not in result_state["completed_nodes"]:
        result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_graph_completion_semantics.py`
  - 测试 `node_status == FAILED` 时节点不出现在 `completed_nodes`
  - 测试异常路径返回后 `completed_nodes` 不包含失败节点
  - 测试正常成功时 `completed_nodes` 正确追加
  - 测试 `node_iterations` 在失败时不递增

---

### Story 40.2: 修正 finalize_pipeline_state() 完成判断

**目标**：使 `finalize_pipeline_state()` 根据 `failed_nodes`、`error` 和 `completed_nodes` 的真实状态决定 pipeline status。

**涉及文件**：1 个（`autoBMAD/docuswarm/pipeline/state.py`）

#### 验收标准

- [ ] `finalize_pipeline_state()` 检查 `failed_nodes` 是否非空，非空时设置 `status=FAILED`
- [ ] 检查 `error` 是否存在，存在时设置 `status=FAILED`
- [ ] 仅在 `failed_nodes` 为空且 `completed_nodes` 包含全部 `PIPELINE_NODES` 时设置 `status=COMPLETED`
- [ ] 清理矛盾：`completed_nodes` 中移除同时存在于 `failed_nodes` 的节点
- [ ] 图提前结束（缺少节点）时设置 `status=FAILED` 并记录错误

#### 技术规格

```python
def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    import copy
    result = copy.deepcopy(state)

    failed_nodes = result.get("failed_nodes", [])
    error = result.get("error")
    completed = set(result.get("completed_nodes", []))
    required = set(PIPELINE_NODES)

    # 清理矛盾：失败节点不得出现在 completed_nodes
    if failed_nodes:
        result["completed_nodes"] = [n for n in result["completed_nodes"] if n not in failed_nodes]
        completed = set(result["completed_nodes"])

    if failed_nodes or error:
        result["status"] = FAILED
    elif required.issubset(completed):
        result["status"] = COMPLETED
    else:
        result["status"] = FAILED
        result["error"] = {
            "message": f"Pipeline ended with incomplete nodes: {required - completed}",
            "type": "IncompletePipeline",
        }

    return result
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_finalize_state.py`
  - 测试存在 `failed_nodes` 时 `status=FAILED`
  - 测试存在 `error` 时 `status=FAILED`
  - 测试全部成功时 `status=COMPLETED`
  - 测试 `completed_nodes` 中同时存在于 `failed_nodes` 的节点被清理
  - 测试不完整 pipeline 时 `status=FAILED`

---

### Story 40.3: 建立单一完成门控策略

**目标**：收敛完成判断到单一位置，禁止多个组件独立修改 `completed_nodes`。

**涉及文件**：2 个（`autoBMAD/docuswarm/node_execution/pipeline_adapter.py` + `autoBMAD/docuswarm/pipeline/graph.py`）

#### 验收标准

- [ ] `PipelineAdapter.convert_node_to_pipeline_state()` 成为 `completed_nodes` 和 `failed_nodes` 的**唯一写入者**
- [ ] `graph.py` 的 executor 不再直接修改 `completed_nodes`，仅负责调用 adapter 和传递 state
- [ ] 建立 `completion_gate.py` 模块（可选，如适配器已足够则无需新建）
- [ ] 所有节点状态转换通过 adapter 的单一接口完成

#### 技术规格

方案 A（推荐）：将完成语义完全收敛到 adapter，graph.py 不再修改 `completed_nodes`：

```python
# graph.py 修复后
# 删除以下代码块（~lines 146-152）：
# if node_id not in result_state["completed_nodes"]:
#     result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]

# adapter 已正确处理 completed_nodes / failed_nodes
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_completion_gate.py`
  - 测试 adapter 是唯一写入者（graph.py 不再直接修改）
  - 测试失败节点始终路由到 `failed_nodes`
  - 测试成功节点始终路由到 `completed_nodes`

---

## 依赖关系

```
Story 40.1 → Story 40.2  (graph.py 修复后，finalize 才能基于正确的 completed_nodes 判断)
Story 40.1 → Story 40.3  (单一门控依赖 graph.py 不再覆盖)
Story 40.2 和 Story 40.3 可并行实施
```

---

## 实施阶段划分

### 阶段 1（P0 修复，优先级最高）

- **Story 40.1**：修复 graph.py 无条件 completed_nodes 追加
- **Story 40.2**：修正 finalize_pipeline_state() 完成判断

**预期收益**：消除 `completed_nodes` 与 `failed_nodes` 的交集，`status='completed'` 不再与 `error` 并存。

### 阶段 2（边界重构）

- **Story 40.3**：建立单一完成门控策略

**预期收益**：从架构上防止未来出现类似的完成语义冲突。

---

## 验证标准

修复后，以下状态组合必须不再出现：

- `completed_nodes` 与 `failed_nodes` 的交集非空
- `status='completed'` 且 `failed_nodes` 非空
- `status='completed'` 且 `error` 非空
- `status='completed'` 且 `completed_nodes` 不包含全部 `PIPELINE_NODES`

---

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| graph.py 修改影响正常执行路径 | MEDIUM | 保留成功路径逻辑不变，仅增加条件判断 |
| finalize_pipeline_state 修改影响恢复 | MEDIUM | 恢复时重新计算状态，不依赖旧 status |
| 单一门控导致 adapter 职责过重 | LOW | adapter 本来就是节点状态的转换器，增加完成判断是合理扩展 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `autoBMAD/docuswarm/pipeline/graph.py` | Story 40.1 主战场（删除覆盖逻辑） |
| `autoBMAD/docuswarm/pipeline/state.py` | Story 40.2 主战场（修正 finalize） |
| `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` | Story 40.3 单一门控 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | 事后修正逻辑（后续由 EPIC-42 替代） |

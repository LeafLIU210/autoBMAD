# 研究报告 02：LangGraph 节点完成语义与状态污染分析

**日期**: 2026-04-28  
**研究对象**: `autoBMAD/docuswarm/pipeline/graph.py`, `pipeline/state.py`, `node_execution/pipeline_adapter.py`  
**关联问题**: `completed_nodes` 与 `failed_nodes` 同时包含全部节点；`status=completed` 与 `error` 并存  
**研究工具**: `tools/winerror5_architecture_research_tool.py --mode graph-semantics`

---

## 执行摘要

本报告通过静态代码审计和运行时日志分析，确认 DocuSwarm 存在 **三处完成语义冲突**：

1. **R2**: `graph.py` 在 `PipelineAdapter` 转换后**无条件**将节点追加到 `completed_nodes`，覆盖了 adapter 的失败路由。
2. **R3**: `finalize_pipeline_state()` **无条件**设置 `status=COMPLETED`，不检查 `failed_nodes` 或 `error`。
3. **R4**: `orchestrator._determine_final_status()` 作为**事后修正**，无法消除 LangGraph checkpoint 和返回结果中的矛盾状态。

这些冲突的直接后果是：即使所有节点都因 `WinError 5` 而失败，最终结果仍同时携带 `completed_nodes=['analyst',...]`、`status='completed'` 和 `error=...`，形成不可恢复的状态污染。

**核心建议**：建立单一的"节点完成门控"策略，禁止失败节点进入 `completed_nodes`，禁止 finalizer 盲目标记完成。

---

## 1. 状态字段定义与合法语义

### 1.1 PipelineState 字段

```python
class PipelineState(TypedDict):
    pipeline_id: str
    completed_nodes: list[str]      # 应当仅包含真正成功完成的节点
    failed_nodes: list[str]         # P0-F1: 追踪失败节点
    status: str                     # pending | running | completed | failed | paused | cancelled
    error: dict[str, Any] | None    # 首次失败的错误信息
    node_iterations: dict[str, int] # 每个节点的执行次数
```

### 1.2 合法状态组合

| completed_nodes | failed_nodes | status | error | 合法性 |
|-----------------|--------------|--------|-------|--------|
| `['analyst']` | `[]` | `running` | `None` | ✅ 正常执行中 |
| `['analyst','pm']` | `[]` | `completed` | `None` | ✅ 全部成功 |
| `[]` | `['analyst']` | `failed` | `{...}` | ✅ 首节点失败 |
| `['analyst','pm','ux','architect','po']` | `['analyst',...]` | `completed` | `{...}` | ❌ **矛盾状态** |
| `['analyst','pm','ux','architect','po']` | `[]` | `failed` | `{...}` | ❌ 完成但标记失败 |

当前运行时出现的正是第 4 种非法组合。

---

## 2. R2: graph.py 覆盖 adapter 的失败语义

### 2.1 Adapter 的正确逻辑

`pipeline_adapter.py` 的 `convert_node_to_pipeline_state()` 实现了 P0-F1：

```python
# pipeline_adapter.py ~lines 322-337
node_status = node_state.get("status", "")
if node_status == COMPLETED:
    if node_id not in new_state["completed_nodes"]:
        new_state["completed_nodes"] = new_state["completed_nodes"] + [str(node_id)]
    # Remove from failed_nodes if recovered
    if "failed_nodes" in new_state and node_id in new_state["failed_nodes"]:
        new_state["failed_nodes"] = [n for n in new_state["failed_nodes"] if n != node_id]
else:
    # P0-F1: Non-completed status => add to failed_nodes
    if "failed_nodes" not in new_state:
        new_state["failed_nodes"] = []
    if node_id not in new_state["failed_nodes"]:
        new_state["failed_nodes"] = new_state["failed_nodes"] + [str(node_id)]
```

**分析**: Adapter 的逻辑是正确的——只有 `node_status == COMPLETED` 才进入 `completed_nodes`；否则进入 `failed_nodes`。

### 2.2 Graph Executor 的覆盖逻辑

`graph.py` 的 `_create_integrated_node_executor()` 在 adapter 转换之后：

```python
# graph.py ~lines 146-152
current_iteration = result_state["node_iterations"].get(node_id, 0)
result_state["node_iterations"][node_id] = current_iteration + 1

if node_id not in result_state["completed_nodes"]:
    result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

**分析**: 这段代码**完全不检查节点状态**，无论 `result_state` 中是否已经将该节点标记为失败，都强行追加到 `completed_nodes`。这直接覆盖了 adapter 的 P0-F1 逻辑。

### 2.3 异常路径的双重处理

在异常路径中（`except Exception as e`），graph.py 已经做了部分正确处理：

```python
# graph.py ~lines 126-144
except Exception as e:
    result_state["deliverables"][node_id] = {}
    if "failed_nodes" not in result_state:
        result_state["failed_nodes"] = []
    if node_id not in result_state["failed_nodes"]:
        result_state["failed_nodes"] = result_state["failed_nodes"] + [node_id]
    result_state["error"] = {...}
    # Do NOT increment iteration or add to completed_nodes on error
    return result_state
```

**问题**: 异常路径返回后，第 146-152 行仍然执行（因为代码在 `try/except` 块之后），所以即使异常路径正确设置了 `failed_nodes`，后续代码仍然把节点加入 `completed_nodes`。

### 2.4 修复方案

**方案 A（推荐）**: 删除或条件化第 146-152 行的 `completed_nodes` 追加逻辑。

```python
# 修复后
if node_id not in result_state.get("failed_nodes", []):
    if node_id not in result_state["completed_nodes"]:
        result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

**方案 B**: 将完成语义完全收敛到 adapter，graph.py 不再修改 `completed_nodes`，只负责调用 adapter 和传递 state。

---

## 3. R3: finalize_pipeline_state() 盲目标记完成

### 3.1 当前实现

```python
# pipeline/state.py ~lines 285-315
def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    import copy
    result = copy.deepcopy(state)
    # Mark pipeline as completed
    result["status"] = COMPLETED
    return result
```

**分析**: `finalize_pipeline_state` 被 `graph.py` 的 `__finalize__` 节点调用，作为 LangGraph 的最后一个节点。它无条件设置 `status=COMPLETED`，不检查：

- `failed_nodes` 是否非空
- `error` 是否存在
- `completed_nodes` 是否真正包含所有 PIPELINE_NODES

### 3.2 事后修正的局限

`orchestrator.py` 的 `_determine_final_status()` 试图事后修正：

```python
# orchestrator.py ~lines 153-169
def _determine_final_status(self, result: dict[str, Any]) -> str:
    failed_nodes = result.get("failed_nodes", [])
    error = result.get("error")
    if failed_nodes or error:
        return FAILED
    return COMPLETED
```

**问题**:

1. **LangGraph checkpoint 已经被污染**: `finalize_pipeline_state` 写入的 `COMPLETED` 状态已经存入 `AsyncSqliteSaver` 的 checkpoint。恢复时读取的 checkpoint 将包含错误的 `status`。
2. **返回结果携带矛盾**: `graph.ainvoke()` 返回的 `result` 字典同时包含 `status='completed'` 和 `failed_nodes=[...]`。下游导出、日志分析、CLI 查询都会看到这个矛盾。
3. **DB 状态是第二重修正**: orchestrator 把修正后的 status 写入 DB，但 DB 的 `state_json` 字段仍保存着 LangGraph 返回的原始矛盾状态。

### 3.3 修复方案

```python
def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    import copy
    result = copy.deepcopy(state)

    failed_nodes = result.get("failed_nodes", [])
    error = result.get("error")
    completed = set(result.get("completed_nodes", []))
    required = set(PIPELINE_NODES)

    if failed_nodes or error:
        result["status"] = FAILED
    elif required.issubset(completed):
        # All required nodes completed successfully
        result["status"] = COMPLETED
    else:
        # Graph ended prematurely (should not happen with sequential edges)
        result["status"] = FAILED
        result["error"] = {
            "message": f"Pipeline ended with incomplete nodes: {required - completed}",
            "type": "IncompletePipeline",
        }

    return result
```

---

## 4. R4: 状态所有权的双重真相

### 4.1 当前状态写入路径

DocuSwarm 的 pipeline 状态至少经过三个独立写入者：

```text
1. LangGraph checkpoint (AsyncSqliteSaver)
   → 写入 checkpoints 表
   → 包含完整的 PipelineState

2. graph.py finalize_executor
   → 调用 finalize_pipeline_state()
   → 状态被 checkpoint 捕获

3. orchestrator._determine_final_status() + update_pipeline_state()
   → 写入 pipelines 表的 status, current_node 顶层字段
   → 同时更新 state_json

4. PipelineAdapter.convert_node_to_pipeline_state()
   → 在 graph 节点执行过程中更新 completed_nodes/failed_nodes
```

### 4.2 漂移场景

| 时序 | checkpoint 状态 | DB 顶层状态 | DB state_json | 结果 |
|------|-----------------|-------------|---------------|------|
| T1: analyst 失败 | status=running, failed_nodes=['analyst'] | running | 同 checkpoint | ✅ 一致 |
| T2: graph 继续执行 | status=running, failed_nodes=['analyst'] | running | 同 checkpoint | ⚠️ 图继续执行，但后续节点也会失败 |
| T3: finalize | status=COMPLETED, failed_nodes=[...] | running | 同 checkpoint | ❌ 矛盾 |
| T4: orchestrator 修正 | status=COMPLETED, failed_nodes=[...] | failed | 同 checkpoint | ❌ DB 与 checkpoint 矛盾 |

### 4.3 单一真相原则

建议建立状态所有权规则：

- **LangGraph checkpoint 是执行中恢复的事实来源**。
- **DB 顶层字段（status, current_node）是 checkpoint 的投影/索引**，而不是独立真相。
- **所有查询（status/list/export/resume/restart/cancel）必须通过统一的状态读取服务访问**。
- **写入时通过一个 mapper 从 checkpoint state 派生投影字段**，而不是让 graph、orchestrator、state manager 分别写自己的 status。

---

## 5. 修复优先级与验证矩阵

### 5.1 P0：立即修复

| 修复项 | 文件 | 行号 | 验证测试 |
|--------|------|------|----------|
| 删除/条件化 graph.py 的无条件 completed_nodes 追加 | `graph.py` | 146-152 | `test_failed_node_never_enters_completed_nodes_after_adapter` |
| finalize_pipeline_state 检查 failed_nodes/error | `state.py` | 285-315 | `test_finalize_failed_when_failed_nodes_present` |

### 5.2 P1：边界重构

| 修复项 | 文件 | 说明 | 验证测试 |
|--------|------|------|----------|
| 建立单一完成门控 | `pipeline_adapter.py` | 成为 completed_nodes 的唯一写入者 | `test_graph_result_status_matches_orchestrator_final_status` |
| 状态投影服务 | 新建 `status_projection.py` | checkpoint → DB/CLI 的统一 mapper | `test_status_projection_from_checkpoint` |

### 5.3 验证标准

修复后，以下状态组合必须不再出现：

- `completed_nodes` 与 `failed_nodes` 的交集非空
- `status='completed'` 且 `failed_nodes` 非空
- `status='completed'` 且 `error` 非空
- `status='completed'` 且 `completed_nodes` 不包含全部 `PIPELINE_NODES`

---

## 6. 结论

DocuSwarm 的状态污染不是"日志不准确"，而是 **完成语义在三个不同位置被重复实现且相互冲突** 的架构缺陷：

- `PipelineAdapter` 试图正确路由失败节点。
- `graph.py` 的 executor 事后无条件覆盖为完成。
- `finalize_pipeline_state()` 盲目标记 pipeline 完成。
- `orchestrator` 事后修正 DB 状态，但无法修复 checkpoint 和返回结果。

最小充分的修复是：

1. **收敛完成判断到单一位置**（推荐 `PipelineAdapter` 或新建 `completion_gate`）。
2. **删除 graph.py 的覆盖逻辑**。
3. **修正 finalize_pipeline_state()** 使其检查 `failed_nodes` 和 `error`。
4. **建立 checkpoint → DB 的投影映射**，禁止独立写入 status。

---

## 参考资料

- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `docs/evaluation/2026-04-28-docuswarm-winerror5-architecture-refactor-evaluation.md`

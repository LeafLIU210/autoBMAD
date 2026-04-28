# DocuSwarm P0 技术债深度研究报告

**报告日期**: 2026-04-27  
**研究对象**: `autoBMAD/docuswarm` 全部 P0 技术债问题  
**研究基础**: `docs-doc/evaluation/2026-04-27-docuswarm-deep-tech-debt-review.md`  
**研究方法**: 源码静态分析 + 运行时调试工具验证 + 合同测试  

---

## 执行摘要

本报告基于 `@docs-doc/evaluation/2026-04-27-docuswarm-deep-tech-debt-review.md` 中识别的全部 **P0 问题**，采用 4 套专门设计的调试工具进行了深度运行时验证和代码路径追踪。所有 P0 问题均通过自动化工具 **100% 复现并确认**。

**核心结论**: DocuSwarm 的运行时合同在三个关键边界层（状态传播、上下文传递、权限控制）存在系统性断裂。这些不是局部代码缺陷，而是多层组件之间的合同语义不一致导致的级联失效。

| P0 问题 | 确认状态 | 影响范围 | 修复复杂度 |
|--------|---------|---------|-----------|
| F1 节点失败被吞并标记完成 | ✅ 已确认 | Pipeline 状态机可信度 | 中 |
| F2 shared_context 传递链路断裂 | ✅ 已确认 | 跨节点协作记忆 | 高 |
| F3 工具权限被 SessionManager 放大 | ✅ 已确认 | Agent 执行安全边界 | 中 |
| F4 DatabaseManager 单例路径污染 | ✅ 已确认 | 测试隔离 / 多 Pipeline 数据污染 | 中 |

---

## 研究方法与调试工具

本次研究没有仅依赖代码走读，而是创建并运行了 4 套专用调试工具，覆盖静态代码提取、运行时行为验证和跨组件合同测试：

| 工具路径 | 研究目标 | 验证方式 |
|---------|---------|---------|
| `@tools/debug/p0_failure_propagation_debugger.py` | F1 失败传播链 | 源码提取 + 运行时状态转换验证 |
| `@tools/debug/p0_shared_context_debugger.py` | F2 shared_context 链路 | 运行时 PipelineState/NodeRunState 转换验证 |
| `@tools/debug/p0_database_singleton_debugger.py` | F4 数据库单例污染 | 临时文件 + 单例行为运行时验证 |
| `@tools/debug/p0_tool_permission_debugger.py` | F3 工具权限放大 | 配置读取 + 工具列表运行时对比 |

所有工具均可在仓库根目录直接运行，输出结构化 JSON 供后续自动化回归测试复用。

---

## F1: 节点失败会被流水线层吞掉，并被标记为已完成

**严重级别**: Critical  
**问题本质**: 状态机 dishonest —— 系统在内部检测到失败时，对外仍然报告成功。

### 根因分析

F1 不是一个单点 bug，而是由 **4 个独立但互补的失效模式** 组成的级联保护网，每一层都有机会阻止失败传播，但每一层都失败了：

```
DualAgentNode.execute_with_context()
    ↓ [抛出异常 或 返回 NEEDS_REVISION]
NodeExecutor._execute_node()
    ↓ [捕获异常，设置 FAILED，但不抛出，正常返回]
PipelineAdapter.convert_node_to_pipeline_state()
    ↓ [不检查 status，直接加入 completed_nodes]
graph.py _create_integrated_node_executor()
    ↓ [若异常穿透，捕获后仍加入 completed_nodes]
HybridOrchestrator.start_pipeline()
    ↓ [graph.ainvoke() 返回后无条件写 completed]
Pipeline 最终状态 = "completed" ❌
```

#### 失效模式 1: NodeExecutor 捕获异常后正常返回

**位置**: `autoBMAD/docuswarm/node_execution/executor.py:235-246`

```python
except Exception as e:
    logger.error(...)
    new_state["status"] = FAILED

return new_state  # ← 正常返回，没有 raise
```

**研究发现**: 异常被完全消化。调用方 `PipelineAdapter` 和 `graph.py` 看到的只是一个带有 `status='failed'` 的普通字典，但程序控制流继续沿着"成功路径"前进。

#### 失效模式 2: PipelineAdapter 不检查节点状态即加入 completed_nodes

**位置**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:294-298`

**调试工具运行结果**:

```
Input node_state['status'] = 'failed'
Output completed_nodes contains 'analyst': True
VERDICT: BUG CONFIRMED
```

代码逻辑：

```python
# Add node to completed_nodes
if node_id is not None and node_id not in new_state["completed_nodes"]:
    new_state["completed_nodes"] = new_state["completed_nodes"] + [str(node_id)]
```

**关键发现**: 这里没有任何 `if node_state.get("status") == COMPLETED` 的前置检查。`FAILED`、`BLOCKED`、`RUNNING` 状态的节点都会被加入 `completed_nodes`。

#### 失效模式 3: graph.py 的 integrated executor 异常后仍标记完成

**位置**: `autoBMAD/docuswarm/pipeline/graph.py:126-141`

```python
except Exception as e:
    logger.error(...)
    result_state["deliverables"][node_id] = {}  # 空交付物

# 以下代码无论是否发生异常都会执行：
result_state["node_iterations"][node_id] = current_iteration + 1
if node_id not in result_state["completed_nodes"]:
    result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

**关键发现**: 即使 `async_node_executor` 抛出异常（比如 `NodeExecutor` 本身也抛出），`graph.py` 的异常处理仍然将节点加入 `completed_nodes`。这构成了**第二层失效保护网**——如果第一层（NodeExecutor 不抛出）失败了，第二层本应拦截，但它也失败了。

#### 失效模式 4: HybridOrchestrator 无条件将 pipeline 标记为 completed

**位置**: `autoBMAD/docuswarm/pipeline/orchestrator.py:459-464`

```python
result = await graph.ainvoke(initial_state, config)

# 无条件更新为 completed
await self._state_manager.update_pipeline_state(
    final_pipeline_id,
    {"status": "completed", "current_node": final_current_node},
)
```

**关键发现**: `result` 字典中包含所有节点的最终状态（包括 `completed_nodes`、`deliverables`、`evaluations`），但 `start_pipeline()` **完全没有检查**这些字段来判断是否有节点失败。同样的问题也出现在 `resume_pipeline()` (line 613) 和 `restart_from_node()` (line 752)。

### 影响评估

1. **假阳性完成**: 用户看到 "pipeline completed"，但核心交付物缺失或为空。
2. **下游污染**: 下游节点（如 `pm` 看到 `analyst` 在 `completed_nodes` 中）会继续执行，基于空/错误的交付物生成低质量文档。
3. **事故不可见**: 没有异常抛出，没有日志级别以上的告警，问题只能通过人工检查交付物质量发现。
4. **状态机腐蚀**: 一旦 `completed_nodes` 和 `deliverables` 被污染，resume/restart 操作会基于错误状态继续，错误被持久化。

### 修复建议

| 组件 | 修复动作 | 优先级 |
|-----|---------|-------|
| `PipelineAdapter.convert_node_to_pipeline_state()` | 仅当 `node_state["status"] == COMPLETED` 或 `FORCE_APPROVED` 时才加入 `completed_nodes` | P0 |
| `graph.py` `_create_integrated_node_executor()` | 异常后不应加入 `completed_nodes`；应设置 `error` 字段并考虑 pipeline 级失败 | P0 |
| `HybridOrchestrator` | `graph.ainvoke()` 返回后检查 `result["completed_nodes"]` 与预期的一致性，或引入 pipeline 级 `error` 字段检测 | P0 |
| `NodeExecutor` | 对不可恢复异常应抛出 `NodeExecutionError`，而不是静默返回 FAILED | P1 |

---

## F2/F4: shared_context 运行时传递链路断裂 + DatabaseManager 单例路径污染

**严重级别**: Critical  
**问题本质**: shared_context 的"持久化幻觉"——数据库表存在、工具接口存在，但端到端链路完全不通。

### 根因分析

shared_context 的问题同样是一个**级联断裂链**，涉及 5 个环节，每个环节都独立失效：

```
PipelineState (有 shared_context)
    ↓ [convert_pipeline_to_node_state]
NodeRunState (shared_context 字段完全缺失)
    ↓ [executor 读取 state.get("shared_context", {})]
ExecutionContext (得到 {})
    ↓ [Agent 执行，工具调用 update_context]
update_context_tool (创建 StateManager()，无 db_path)
    ↓ [写入可能错误的数据库]
_refresh_shared_context_from_db() (duck typing 全失败)
    ↓ [返回 None]
NodeRunState (shared_context 未被更新)
    ↓ [convert_node_to_pipeline_state]
PipelineState (shared_context 未被合并)
```

#### 断裂点 1: PipelineState → NodeRunState 转换丢失 shared_context

**位置**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:233-246`

**调试工具运行结果**:

```
Input PipelineState['shared_context'] = {'facts': {'market_scope': 'global'}, ...}
Output NodeRunState keys: ['run_id', 'pipeline_id', 'node_id', 'context_hash', ...]
Output has 'shared_context' key: False
VERDICT: BUG CONFIRMED
```

`convert_pipeline_to_node_state()` 的返回字典中**根本没有 `shared_context` 键**。这意味着无论 PipelineState 中有什么共享上下文数据，下游节点都看不到。

#### 断裂点 2: NodeRunState → PipelineState 合回时丢失 shared_context

**位置**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:249-303`

**调试工具运行结果**:

```
NodeRunState['shared_context'] = {'updated': 'by_tool', 'facts': {'new': 'fact'}}
Original PipelineState['shared_context'] = {'original': 'data'}
Result PipelineState['shared_context'] = {'original': 'data'}
VERDICT: BUG CONFIRMED
```

即使 NodeRunState 中包含更新后的 shared_context（比如通过其他途径注入），`convert_node_to_pipeline_state()` **完全不读取这个字段**，导致更新全部丢失。

#### 断裂点 3: _refresh_shared_context_from_db 的 duck typing 永远失败

**位置**: `autoBMAD/docuswarm/node_execution/executor.py:432-472`

该函数尝试通过 4 种 duck typing 方式从 `SessionManager` 获取 `StateManager`：

1. `session_manager.get_pipeline` — SessionManager **没有**此方法
2. `session_manager._state_manager` — SessionManager **没有**此属性
3. `session_manager.storage` — SessionManager **没有**此属性
4. `session_manager.state_manager` — SessionManager **没有**此属性

**调试工具运行结果**:

```
SessionManager analysis:
  Has get_pipeline method: False
  Has _state_manager attribute: False
  Has storage attribute: False

RESULT: _refresh_shared_context_from_db will ALWAYS return None
```

这意味着 `Story 35.1` 中实现的 DB 刷新逻辑**在真实运行中永远不会成功**。

#### 断裂点 4: update_context_sdk 自行创建默认 StateManager

**位置**: `autoBMAD/docuswarm/tools/update_context_sdk.py:98-102`

```python
tool = UpdateContextTool(
    state_manager=StateManager(),  # ← 无 db_path 参数
    pipeline_id=pipeline_id,
    allowed_keys=allowed_keys,
)
```

`StateManager()` 默认实例化会使用 `DatabaseManager.get_instance()`，而该单例的 db_path 可能**与当前 pipeline 的数据库路径完全不同**。

#### 断裂点 5: DatabaseManager 单例按路径污染（F4）

**位置**: `autoBMAD/docuswarm/storage/database.py:64-78`

**调试工具运行结果**:

```
First get_instance(db_one='...\one.db')
  Returned instance.db_path = '...\one.db'

Second get_instance(db_two='...\two.db')
  Returned instance.db_path = '...\one.db'

instance_one is instance_two: True
path_one == path_two: True
BUG CONFIRMED
```

`DatabaseManager.get_instance()` 使用单一类属性 `_instance`，第一次调用的 `db_path` 永远决定了所有后续调用的数据库路径。

**复合影响**: 如果 orchestrator 使用 `db_path="pipeline_A.db"` 创建 `StateManager`，而 `update_context_tool` 调用 `StateManager()`（无参数），则：
1. `DatabaseManager.get_instance()` 返回的可能是之前某个测试留下的实例
2. 如果这是第一次调用，它使用默认路径 `"docuswarm.db"`
3. update_context 的写入进入了一个数据库，而 pipeline 的读取试图从另一个数据库刷新
4. **数据永远对不上**

### 影响评估

1. **跨节点协作记忆失效**: `analyst` 调用 `update_context` 写入的关键事实，`pm` 节点看不到。
2. **多 Pipeline 数据污染**: 并行运行或测试中使用不同 db_path 的 pipeline 会互相覆盖数据库状态。
3. **测试不可靠**: 运行顺序会影响数据库实例指向，导致 flaky tests。
4. **产品债**: 界面和文档声称支持协作记忆，但真实运行时行为不稳定，难以调试。

### 修复建议

| 组件 | 修复动作 | 优先级 |
|-----|---------|-------|
| `PipelineAdapter.convert_pipeline_to_node_state()` | 在返回字典中包含 `shared_context=pipeline_state.get("shared_context", {})` | P0 |
| `PipelineAdapter.convert_node_to_pipeline_state()` | 将 `node_state.get("shared_context")` 合并回 `new_state["shared_context"]` | P0 |
| `DatabaseManager` | 改为按 `resolved_db_path` 缓存实例，或取消全局单例 | P0 |
| `update_context_sdk.py` | 通过 MCP server factory 接收当前 pipeline 的 `db_path` 或 `state_manager` 实例 | P0 |
| `NodeExecutor` | 将 `session_manager` 与 `state_manager` 的关联改为显式注入，而非 duck typing | P1 |
| `SessionManager` | 可选地持有 `_state_manager` 引用，用于工具回调 | P1 |

---

## F3: 工具权限配置被 SessionManager 放大，节点白名单没有成为真实边界

**严重级别**: Critical  
**问题本质**: 配置层声明的权限边界在运行层被系统性突破。

### 根因分析

#### 放大路径 1: SessionManager._get_builtin_tools() 固定返回 5 个工具

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:168-175`

```python
def _get_builtin_tools(self) -> list[str]:
    return ["Read", "Glob", "Grep", "Edit", "Bash"]
```

**调试工具运行结果**（读取全部 5 个 node.yaml）：

```
Node configuration allowed_builtin_tools:
  analyst: ['Read', 'Glob']
  pm: ['Read', 'Glob']
  ux: ['Read', 'Glob']
  architect: ['Read', 'Glob']
  po: ['Read', 'Glob']
```

**所有节点**都只声明了 `["Read", "Glob"]`，但 `SessionManager` 无条件提供全部 5 个工具。

#### 放大路径 2: _build_allowed_tools() 从不咨询节点配置

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:177-227`

```python
def _build_allowed_tools(self) -> list[str]:
    tools = []
    # ... Skill tool ...
    tools.extend(self._get_builtin_tools())  # ← 无条件加入全部 5 个
    # ... MCP tools ...
    return tools
```

**调试工具验证**: `_build_allowed_tools()` **从未读取** `self._tool_permissions.allowed_builtin_tools`。节点配置在此函数中完全不被参考。

**实际运行时工具列表**（以 analyst 为例）：

```
Expected builtin tools (from config): ['Read', 'Glob']
Actual allowed_tools: ['Skill', 'Read', 'Glob', 'Grep', 'Edit', 'Bash', ...mcp_tools...]
Unexpected tools granted: ['Grep', 'Edit', 'Bash']
VERDICT: BUG CONFIRMED
```

#### 放大路径 3: yolo=True 设置 permission_mode="bypassPermissions"

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:245-246`

```python
permission_mode = "bypassPermissions" if yolo else "default"
```

`SessionManager.create_session()` 和 `single_prompt()` 的默认参数都是 `yolo=True`。这意味着：
- 即使 `allowed_tools` 列表正确配置，Claude Agent SDK 在 `bypassPermissions` 模式下**可能完全忽略该列表**
- Agent 获得了 SDK 级别的权限绕过

### 影响评估

1. **安全边界失效**: 配置层声明"只读"，运行层实际可 `Edit` 文件、`Bash` 执行任意 shell。
2. **Agent 行为不可预测**: 文档生成 Agent 可能在生成过程中修改源代码、删除文件或执行外部命令。
3. **审计失真**: 安全审计会基于 node.yaml 判断权限，但真实运行时权限远大于配置。
4. **多租户风险**: 如果有隔离预期（不同 pipeline 使用不同工作目录），`Bash` 工具可能突破目录限制。

### 修复建议

| 组件 | 修复动作 | 优先级 |
|-----|---------|-------|
| `SessionManager._get_builtin_tools()` | 改为从 `self._tool_permissions.allowed_builtin_tools` 派生，而非硬编码 | P0 |
| `SessionManager._build_allowed_tools()` | 在添加 builtin tools 前检查节点配置，或直接使用 NodeToolFilter 的过滤结果 | P0 |
| `SessionManager._create_options()` | `yolo=True` 时不应使用 `bypassPermissions`；高危工具（Edit/Bash）需要单独 allowlist | P0 |
| `NodeToolFilter` | 确保 `allowed_builtin_tools` 配置正确传递到最终 options | P1 |
| 回归测试 | 为每个节点增加权限快照测试：读取 `node.yaml`，断言 SDK options 中 `allowed_tools` 等于配置展开结果 | P1 |

---

## 交叉影响与复合风险

上述四个 P0 问题并非孤立存在，它们会在真实运行中产生**复合失效**:

### 场景：Analyst 节点执行出错

1. `analyst` 节点内部抛出异常（如 LLM API 超时）
2. **F1**: `NodeExecutor` 捕获异常，返回 `status=FAILED`，但不抛出
3. **F1**: `PipelineAdapter` 将 `analyst` 加入 `completed_nodes`
4. **F1**: `HybridOrchestrator` 将 pipeline 标记为 `completed`
5. 用户收到"成功完成"通知，但 `analyst` 交付物为空

### 场景：PM 节点读取 Analyst 的 shared_context 更新

1. `analyst` 执行中调用 `update_context` 写入关键事实
2. **F4**: `update_context_tool` 的 `StateManager()` 因单例污染写入错误的数据库
3. **F2**: `PipelineAdapter` 没有把 `shared_context` 传给 `pm` 的 NodeRunState
4. **F2**: `_refresh_shared_context_from_db` 的 duck typing 失败，返回 None
5. **F2**: `PipelineAdapter` 没有把任何 shared_context 合回 PipelineState
6. `pm` 节点完全看不到 `analyst` 的上下文更新，生成低质量文档

### 场景：恶意/误操作的工具调用

1. 节点配置只允许 `Read`、`Glob`
2. **F3**: `SessionManager` 实际授予 `Edit`、`Bash`、`Grep`
3. **F3**: `yolo=True` 设置 `bypassPermissions`
4. Agent 在执行中误调用 `Bash` 删除文件或 `Edit` 修改配置
5. **F1**: 即使工具调用导致节点失败，pipeline 仍报告 completed

---

## 修复路线图建议

基于研究发现，建议按以下顺序修复，以确保每一步都有可验证的改进：

### 阶段 1: 阻止假阳性（1-2 天）

目标：让系统在失败时确实报告失败。

1. **修复 `PipelineAdapter.convert_node_to_pipeline_state()`**
   - 添加 `if node_state.get("status") in (COMPLETED, FORCE_APPROVED)` 检查
   - 对其他状态，将节点加入 `failed_nodes` 或设置 `pipeline_state["error"]`

2. **修复 `graph.py` 的异常处理**
   - 异常后不应加入 `completed_nodes`
   - 设置 `result_state["error"]` 记录失败信息

3. **修复 `HybridOrchestrator`**
   - `graph.ainvoke()` 返回后检查 pipeline state 中是否有 error/failed 节点
   - 仅在确认所有关键节点成功后才标记 `completed`

4. **增加 F1 回归测试**
   - 模拟节点返回 `FAILED`、`BLOCKED`、`NEEDS_REVISION`
   - 断言 pipeline 最终状态不是 `completed`

### 阶段 2: 恢复 shared_context 链路（2-3 天）

1. **修复 `PipelineAdapter` 双向传递**
   - `convert_pipeline_to_node_state()`: 传递 `shared_context`
   - `convert_node_to_pipeline_state()`: 合并 `shared_context`

2. **修复 `DatabaseManager` 单例**
   - 方案 A: 按路径缓存实例 `_instances: dict[str, DatabaseManager]`
   - 方案 B: 完全取消单例，由调用方管理实例生命周期
   - 推荐方案 A，因为改动面更小

3. **修复 `update_context_sdk.py`**
   - `create_update_context_server()` 接收 `state_manager` 或 `db_path` 参数
   - 使用传入的实例/路径创建 `UpdateContextTool`

4. **修复 `_refresh_shared_context_from_db()`**
   - 将 `StateManager` 显式注入 `SessionManager`，或
   - 让 `NodeExecutor` 直接持有 `StateManager` 引用

5. **增加 F2/F4 回归测试**
   - PipelineState 带 shared_context -> NodeRunState 保留 shared_context
   - 两个不同 db_path 的 DatabaseManager.get_instance() 返回不同实例
   - `update_context` 写入后，下游节点读取到同一值

### 阶段 3: 收紧工具权限（1-2 天）

1. **修复 `SessionManager._get_builtin_tools()`**
   - 如果 `self._tool_permissions` 存在，返回 `self._tool_permissions.allowed_builtin_tools`
   - 否则返回安全默认值（如 `["Read", "Glob"]`）

2. **修复 `_build_allowed_tools()`**
   - 移除无条件 `tools.extend(self._get_builtin_tools())`
   - 改为基于节点配置构建工具列表

3. **修复 `yolo` 与 `bypassPermissions` 的耦合**
   - `yolo=True` 仅用于自动批准已知安全工具
   - `Edit`、`Bash` 需要单独 `dangerous_tools_allowlist` 或用户确认

4. **增加 F3 回归测试**
   - 加载每个 `node.yaml`，断言 `_build_allowed_tools()` 结果等于配置声明的工具集合

---

## 附录 A: 调试工具使用说明

所有调试工具位于 `@tools/debug/` 目录，可直接运行：

```bash
# F1 失败传播调试
python tools/debug/p0_failure_propagation_debugger.py
# 输出: tools/debug/p0_failure_propagation_results.json

# F2 shared_context 链路调试
python tools/debug/p0_shared_context_debugger.py
# 输出: tools/debug/p0_shared_context_results.json

# F4 数据库单例污染调试
python tools/debug/p0_database_singleton_debugger.py
# 输出: tools/debug/p0_database_singleton_results.json

# F3 工具权限放大调试
python tools/debug/p0_tool_permission_debugger.py
# 输出: tools/debug/p0_tool_permission_results.json
```

这些工具不仅可以用于本次研究，还可以在修复后作为**回归测试套件**运行，验证修复是否有效。

---

## 附录 B: 关键代码引用索引

| 问题 | 文件 | 行号 | 代码语义 |
|-----|------|------|---------|
| F1 | `node_execution/executor.py` | 235-246 | 异常捕获后不抛出 |
| F1 | `node_execution/pipeline_adapter.py` | 294-298 | 不检查 status 加入 completed_nodes |
| F1 | `pipeline/graph.py` | 126-141 | 异常后仍加入 completed_nodes |
| F1 | `pipeline/orchestrator.py` | 459-464 | 无条件标记 pipeline completed |
| F2 | `node_execution/pipeline_adapter.py` | 233-246 | convert_pipeline_to_node_state 丢失 shared_context |
| F2 | `node_execution/pipeline_adapter.py` | 249-303 | convert_node_to_pipeline_state 不合并 shared_context |
| F2 | `node_execution/executor.py` | 432-472 | _get_state_manager_from_session duck typing 全失败 |
| F2 | `tools/update_context_sdk.py` | 98-102 | StateManager() 无 db_path |
| F4 | `storage/database.py` | 64-78 | get_instance() 单例忽略 db_path |
| F3 | `llm/session_manager.py` | 168-175 | _get_builtin_tools() 硬编码 5 个工具 |
| F3 | `llm/session_manager.py` | 199-200 | _build_allowed_tools() 无条件加入全部内置工具 |
| F3 | `llm/session_manager.py` | 245-246 | yolo=True -> bypassPermissions |

---

## 结论

DocuSwarm 的 P0 技术债不是孤立的代码错误，而是**运行时合同在多个边界层同时失效**的系统性问题：

- **状态传播合同失效**（F1）：失败状态在 4 个转换层中被逐级消化
- **上下文传递合同失效**（F2）：shared_context 在 5 个链路环节中被逐级丢弃
- **权限边界合同失效**（F3）：配置声明在 3 个放大路径中被逐级突破
- **资源隔离合同失效**（F4）：数据库单例破坏了多实例隔离假设

这些问题共同导致了一个核心后果：**系统对外呈现的行为与内部真实状态严重不一致**。用户看到的是"成功"，内部可能是"失败"；用户看到的是"协作记忆"，内部可能是"空上下文"；用户看到的是"只读权限"，内部可能是"完全控制"。

**修复这些 P0 问题不应被视为可选的技术优化，而应被视为恢复系统基本可信度的必要前提**。在这些问题修复之前，任何新增功能都会建立在不可靠的运行时合同之上，增加的是产品层面的不稳定和不可解释输出。

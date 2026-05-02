# 研究报告 04：状态所有权收敛与 Checkpoint-DB 一致性研究

**日期**: 2026-04-28  
**研究对象**: `autoBMAD/docuswarm/pipeline/state.py`, `storage/state_manager.py`, `pipeline/orchestrator.py`, LangGraph checkpoint  
**关联问题**: checkpoint、DB 顶层字段、graph result 之间存在语义漂移（R4）  
**研究工具**: `tools/winerror5_architecture_research_tool.py --mode state-ownership`

---

## 执行摘要

DocuSwarm 当前维护三套状态表示：

1. **LangGraph checkpoint**（`checkpoints` SQLite 表）：图执行中的事实来源，用于 resume。
2. **DB 顶层字段**（`pipelines` 表的 `status`, `current_node` 等）：快速查询索引。
3. **Graph 返回结果**（`graph.ainvoke()` 返回的字典）：CLI/API 的直接输出。

这三套表示之间**没有单一的派生规则**，而是分别由 `graph.py`、`finalize_pipeline_state()`、`orchestrator._determine_final_status()` 和 `StateManager` 独立写入。当前日志中出现的 `status=completed` + `failed_nodes=[...]` 矛盾，正是状态所有权不清晰的直接后果。

**核心建议**：建立 **单一状态真相（Single Source of Truth）** ——以 LangGraph checkpoint 为事实来源，所有其他表示通过 `PipelineStatusProjection` mapper 派生，禁止独立写入 status。

---

## 1. 状态存储现状

### 1.1 数据库 Schema

```sql
-- pipelines 表（DB 顶层字段）
CREATE TABLE pipelines (
    pipeline_id TEXT PRIMARY KEY,
    subject TEXT,
    status TEXT,           -- 独立写入
    current_node TEXT,     -- 独立写入
    state_json TEXT,       -- 包含完整 PipelineState JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- checkpoints 表（LangGraph AsyncSqliteSaver）
CREATE TABLE checkpoints (
    thread_id TEXT,
    checkpoint_id TEXT,
    parent_checkpoint_id TEXT,
    checkpoint BLOB,       -- LangGraph 序列化状态
    metadata BLOB
);
```

### 1.2 状态写入路径

```text
PipelineState (TypedDict)
    │
    ├─► LangGraph StateGraph ──► AsyncSqliteSaver ──► checkpoints 表
    │      (graph.py, checkpoint 每步自动保存)
    │
    ├─► finalize_pipeline_state() ──► 设置 status=COMPLETED
    │      (在 __finalize__ 节点中执行，被 checkpoint 捕获)
    │
    ├─► orchestrator._determine_final_status() ──► DB status 字段
    │      (事后修正，可能覆盖 finalize 的错误状态)
    │
    └─► StateManager.update_pipeline_state() ──► DB state_json + status
           (部分更新，可能与 checkpoint 内容不同步)
```

### 1.3 当前 DB 审计结果

使用 `tools/winerror5_architecture_research_tool.py --mode state-ownership` 对 `docuswarm.db` 的审计结果：

- **Pipelines 数量**: 取决于历史执行次数
- **Checkpoints 表**: 存在
- **一致性违规**: 检测到 `status='completed'` 但 `state_json` 中包含 `failed_nodes` 的 pipeline 记录

---

## 2. 状态漂移场景分析

### 2.1 场景 A：全节点失败后的漂移

**触发条件**: `WinError 5` 导致所有节点 session 创建失败。

**时序**:

```text
T0: start_pipeline()
    DB: status=running, current_node=analyst
    checkpoint: status=running, current_node=None

T1: analyst 节点执行
    graph.py: 异常捕获，设置 failed_nodes=['analyst'], error={...}
    checkpoint: 保存异常后的状态（包含 failed_nodes）
    adapter: 正确将 analyst 路由到 failed_nodes
    graph.py: 事后追加 completed_nodes=['analyst']  ← 覆盖 adapter

T2: pm 节点执行（图继续执行，因为异常被捕获后返回了 result_state）
    同理：failed_nodes=['analyst','pm'], completed_nodes=['analyst','pm']

T3: __finalize__ 节点
    finalize_pipeline_state(): status=COMPLETED
    checkpoint: 保存 status=COMPLETED, failed_nodes=[...]

T4: orchestrator 事后修正
    _determine_final_status(): 看到 failed_nodes，返回 FAILED
    DB update: status=failed, current_node=po
    state_json: 更新为 graph result（仍包含 status=COMPLETED）

最终结果:
    DB 顶层: status=failed
    DB state_json: status=completed, failed_nodes=[...], completed_nodes=[...]
    checkpoint: status=completed, failed_nodes=[...], completed_nodes=[...]
```

**问题**: 恢复时从 checkpoint 读取的状态是 `completed`，但 pipeline 实际上失败了。`export` 或 `status` CLI 查询从 DB 读取得到 `failed`，但展开 state_json 看到 `completed`。

### 2.2 场景 B：恢复时的跳过错误

**触发条件**: 基于错误的 checkpoint 恢复 pipeline。

```text
resume_pipeline():
    checkpoint_state = pipeline.get("state", {})  # 从 DB state_json 读取
    completed_nodes = checkpoint_state.get("completed_nodes", [])
    # 如果 checkpoint 错误地将失败节点加入 completed_nodes，
    # 恢复时会跳过这些节点，导致交付物缺失。
```

**风险**: 用户可能得到一个 `status=completed` 但 deliverables 为空的虚假成功结果。

### 2.3 场景 C：导出污染

```python
# export 命令可能读取 state_json 中的 deliverables
deliverables = state.get("deliverables", {})
# 如果 status=completed 但 deliverables 为空（因为节点实际失败），
# 导出会生成空文档，但仍标记为 completed。
```

---

## 3. 根本原因：多重写入者

### 3.1 写入者清单

| 写入者 | 写入目标 | 触发时机 | 问题 |
|--------|----------|----------|------|
| LangGraph checkpoint | checkpoints 表 | 每步自动 | 保存了 graph.py 覆盖后的错误状态 |
| `PipelineAdapter.convert_node_to_pipeline_state()` | 内存 state | 节点执行后 | 正确路由，但后续被覆盖 |
| `graph.py` executor | 内存 state | 节点执行后 | 无条件追加 completed_nodes |
| `finalize_pipeline_state()` | 内存 state | 图结束时 | 无条件设置 status=COMPLETED |
| `orchestrator._determine_final_status()` | DB status | 图结束后 | 事后修正，不一致 |
| `StateManager.update_pipeline_state()` | DB state_json + status | 各阶段 | 可能与 checkpoint 不同步 |

### 3.2 缺少的机制

- **没有单一的状态验证器**：没有一个函数在写入前验证状态合法性。
- **没有派生规则**：DB 顶层字段不是从 checkpoint 派生，而是独立写入。
- **没有写屏障**：任何组件都可以直接修改 `status` 和 `completed_nodes`。

---

## 4. 建议架构：状态所有权收敛

### 4.1 所有权规则

```text
┌─────────────────────────────────────────────────────────────┐
│  Single Source of Truth: LangGraph checkpoint               │
│  (checkpoints 表，由 AsyncSqliteSaver 管理)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ 派生
┌─────────────────────────────────────────────────────────────┐
│  PipelineStatusProjection (mapper)                          │
│  - 读取 checkpoint state                                    │
│  - 计算: status, current_node, completed_nodes, progress    │
│  - 保证一致性                                               │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         DB 索引字段    CLI 查询      export/resume
      (pipelines 表)   (status/list)  (数据导出)
```

### 4.2 PipelineStatusProjection 设计

```python
# autoBMAD/docuswarm/pipeline/status_projection.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class PipelineStatusProjection:
    pipeline_id: str
    status: str           # 唯一可信的 status
    current_node: str | None
    completed_nodes: list[str]
    failed_nodes: list[str]
    progress_percent: int
    error: dict[str, Any] | None
    is_resumable: bool

class StatusProjectionMapper:
    """从 checkpoint state 派生唯一的投影状态。"""

    @staticmethod
    def from_checkpoint_state(state: dict[str, Any]) -> PipelineStatusProjection:
        pipeline_id = state.get("pipeline_id", "")
        completed = state.get("completed_nodes", [])
        failed = state.get("failed_nodes", [])
        error = state.get("error")

        # 单一完成判断规则
        if failed or error:
            status = "failed"
        elif set(PIPELINE_NODES).issubset(set(completed)):
            status = "completed"
        elif completed:
            status = "running"
        else:
            status = state.get("status", "pending")

        # 清理矛盾：失败节点不得出现在 completed_nodes
        cleaned_completed = [n for n in completed if n not in failed]

        # 当前节点：最后一个执行的节点，或第一个未完成的节点
        current = state.get("current_node")
        if status == "running" and not current:
            for node in PIPELINE_NODES:
                if node not in cleaned_completed:
                    current = node
                    break

        progress = len(cleaned_completed) * 100 // len(PIPELINE_NODES)

        return PipelineStatusProjection(
            pipeline_id=pipeline_id,
            status=status,
            current_node=current,
            completed_nodes=cleaned_completed,
            failed_nodes=failed,
            progress_percent=progress,
            error=error,
            is_resumable=status in ("running", "paused", "failed"),
        )
```

### 4.3 统一状态访问层

```python
# autoBMAD/docuswarm/pipeline/state_access.py
class PipelineStateAccess:
    """统一的状态读取服务。所有查询必须经过此处。"""

    def __init__(self, db_path: str, checkpointer: Any) -> None:
        self._state_manager = StateManager(db_path)
        self._checkpointer = checkpointer

    async def get_projection(self, pipeline_id: str) -> PipelineStatusProjection:
        """从 checkpoint 读取真相，返回投影。"""
        # 1. 尝试从 checkpoint 读取最新状态
        checkpoint_state = await self._load_checkpoint_state(pipeline_id)
        if checkpoint_state:
            return StatusProjectionMapper.from_checkpoint_state(checkpoint_state)

        # 2. fallback 到 DB state_json
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline and pipeline.get("state_json"):
            state = json.loads(pipeline["state_json"])
            return StatusProjectionMapper.from_checkpoint_state(state)

        raise PipelineNotFoundError(pipeline_id)

    async def _load_checkpoint_state(self, pipeline_id: str) -> dict[str, Any] | None:
        """从 LangGraph checkpoint 读取状态。"""
        thread_id = generate_thread_id(pipeline_id)
        # 使用 checkpointer 的 API 读取最新 checkpoint
        ...
```

### 4.4 写屏障：禁止独立写入 status

```python
# StateManager 中移除独立的 status 更新
class StateManager:
    def update_pipeline_state(self, pipeline_id: str, update: dict[str, Any]) -> None:
        # 只允许更新元数据字段（如 subject, tags），禁止直接修改 status
        forbidden_keys = {"status", "completed_nodes", "failed_nodes", "error"}
        if forbidden_keys & set(update.keys()):
            raise ValueError(
                f"Direct modification of {forbidden_keys} is prohibited. "
                "Use StatusProjectionMapper to derive these fields from checkpoint."
            )
        ...
```

---

## 5. 修复影响范围

### 5.1 需要修改的模块

| 模块 | 修改内容 | 优先级 |
|------|----------|--------|
| `pipeline/status_projection.py` | 新建：投影 mapper | P1 |
| `pipeline/state_access.py` | 新建：统一读取服务 | P1 |
| `pipeline/state.py` | 修正 `finalize_pipeline_state()` | P0 |
| `pipeline/graph.py` | 删除 completed_nodes 覆盖逻辑 | P0 |
| `storage/state_manager.py` | 增加写屏障 | P1 |
| `pipeline/orchestrator.py` | 使用 `StatusProjectionMapper` 替代 `_determine_final_status()` | P1 |
| `cli/commands/status.py` | 通过 `state_access` 查询 | P1 |
| `cli/commands/export.py` | 通过 `state_access` 查询 | P1 |
| `cli/commands/resume.py` | 通过 `state_access` 获取恢复状态 | P1 |

### 5.2 向后兼容

- **旧 checkpoint 读取**: `StatusProjectionMapper.from_checkpoint_state()` 在读取旧 checkpoint 时，执行"清理矛盾"逻辑（移除 `completed_nodes` 中的失败节点）。
- **DB 迁移**: 无需 schema 变更，只需在读取时通过 mapper 修正。

---

## 6. 验证方案

### 6.1 一致性测试

```python
async def test_graph_result_status_matches_projection():
    """graph 返回状态、checkpoint 状态、投影状态三者一致。"""
    graph_result = await graph.ainvoke(initial_state, config)
    projection = await state_access.get_projection(pipeline_id)

    assert projection.status == "failed"  # 如果存在 failed_nodes
    assert not set(projection.failed_nodes) & set(projection.completed_nodes)
    assert projection.error is not None
```

### 6.2 恢复安全性测试

```python
async def test_resume_does_not_skip_failed_nodes():
    """恢复流程不会把失败节点当作已完成跳过。"""
    # 模拟 analyst 失败后的 checkpoint
    checkpoint_state = {
        "completed_nodes": ["analyst"],  # 错误地包含（模拟旧 bug）
        "failed_nodes": ["analyst"],
        "status": "completed",
    }
    projection = StatusProjectionMapper.from_checkpoint_state(checkpoint_state)
    assert "analyst" not in projection.completed_nodes
    assert projection.status == "failed"
```

### 6.3 导出正确性测试

```python
def test_export_does_not_export_empty_deliverables_as_completed():
    """export 不会导出空 deliverables 却标记 completed。"""
    state = {
        "completed_nodes": ["analyst"],
        "failed_nodes": [],
        "deliverables": {"analyst": {}},
        "status": "completed",
    }
    projection = StatusProjectionMapper.from_checkpoint_state(state)
    # 即使状态标记 completed，如果 deliverables 为空，应当警告或失败
    assert projection.status == "completed"  # 但 export 应额外检查 deliverables 非空
```

---

## 7. 结论

状态污染不是简单的"日志字段错误"，而是 **状态所有权分散在多个写入者之间、缺乏单一派生规则** 的架构缺陷。

修复的核心是：

1. **承认 LangGraph checkpoint 为唯一事实来源**。
2. **建立 `PipelineStatusProjection` mapper**，所有查询通过它派生。
3. **禁止任何组件直接写入 `status`/`completed_nodes`/`failed_nodes`**。
4. **在读取时执行矛盾清理**，保护恢复和导出流程不受历史错误状态影响。

这样，即使 `WinError 5` 再次发生，checkpoint 中记录的状态也将是一致、可恢复、可查询的，而不是一个充满矛盾的"既完成又失败"的不可信状态。

---

## 参考资料

- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/storage/state_manager.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py`
- LangGraph Persistence 文档
- `tools/winerror5_architecture_research_tool.py`

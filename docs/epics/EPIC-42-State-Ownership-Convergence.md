# EPIC-42: 状态所有权收敛与 Checkpoint-DB 一致性

**Epic ID**: EPIC-42  
**Epic 名称**: 状态所有权收敛与 Checkpoint-DB 一致性  
**优先级**: P1（HIGH）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-28）  
**创建日期**: 2026-04-28  
**研究来源**: `docs/research/2026-04-28-winerror5-architecture-refactor/04-state-ownership-convergence.md`  
**预估工作量**: ~4 days

---

## Epic 概述

DocuSwarm 当前维护三套状态表示：LangGraph checkpoint、DB 顶层字段、Graph 返回结果。这三套表示之间**没有单一的派生规则**，而是分别由 `graph.py`、`finalize_pipeline_state()`、`orchestrator._determine_final_status()` 和 `StateManager` 独立写入。当前日志中出现的 `status=completed` + `failed_nodes=[...]` 矛盾，正是状态所有权不清晰的直接后果。

**核心问题**：
- 多个组件独立写入 `status`/`completed_nodes`/`failed_nodes`，导致语义漂移
- checkpoint 中的错误状态无法被事后修正消除
- 恢复时可能基于错误的 checkpoint 跳过失败节点
- 导出可能生成空文档但仍标记为 completed

**推荐方案**：建立 **单一状态真相（Single Source of Truth）** ——以 LangGraph checkpoint 为事实来源，所有其他表示通过 `PipelineStatusProjection` mapper 派生，禁止独立写入 status。

---

## 背景与技术分析

### 状态写入路径

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
           (部分更新，可能与 checkpoint 不同步)
```

### 状态漂移场景

| 时序 | checkpoint 状态 | DB 顶层状态 | DB state_json | 结果 |
|------|-----------------|-------------|---------------|------|
| T1: analyst 失败 | status=running, failed_nodes=['analyst'] | running | 同 checkpoint | ✅ 一致 |
| T2: graph 继续执行 | status=running, failed_nodes=['analyst'] | running | 同 checkpoint | ⚠️ 图继续执行 |
| T3: finalize | status=COMPLETED, failed_nodes=[...] | running | 同 checkpoint | ❌ 矛盾 |
| T4: orchestrator 修正 | status=COMPLETED, failed_nodes=[...] | failed | 同 checkpoint | ❌ DB 与 checkpoint 矛盾 |

---

## Stories

### Story 42.1: 新建 PipelineStatusProjection Mapper

**目标**：新建 `status_projection.py`，实现从 checkpoint state 派生唯一投影状态的 mapper。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/pipeline/status_projection.py`）

#### 验收标准

- [ ] 定义 `PipelineStatusProjection` dataclass（frozen），包含 `pipeline_id`, `status`, `current_node`, `completed_nodes`, `failed_nodes`, `progress_percent`, `error`, `is_resumable`
- [ ] 定义 `StatusProjectionMapper` 类，包含 `from_checkpoint_state(state)` 静态方法
- [ ] 单一完成判断规则：
  - `failed_nodes` 或 `error` 存在 → `status="failed"`
  - `completed_nodes` 包含全部 `PIPELINE_NODES` → `status="completed"`
  - 有 completed 但不全 → `status="running"`
  - 否则 → `status="pending"`
- [ ] 清理矛盾：`completed_nodes` 中移除同时存在于 `failed_nodes` 的节点
- [ ] 计算 `progress_percent` 和 `is_resumable`

#### 技术规格

```python
# autoBMAD/docuswarm/pipeline/status_projection.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class PipelineStatusProjection:
    pipeline_id: str
    status: str
    current_node: str | None
    completed_nodes: list[str]
    failed_nodes: list[str]
    progress_percent: int
    error: dict[str, Any] | None
    is_resumable: bool

class StatusProjectionMapper:
    @staticmethod
    def from_checkpoint_state(state: dict[str, Any]) -> PipelineStatusProjection:
        pipeline_id = state.get("pipeline_id", "")
        completed = state.get("completed_nodes", [])
        failed = state.get("failed_nodes", [])
        error = state.get("error")

        if failed or error:
            status = "failed"
        elif set(PIPELINE_NODES).issubset(set(completed)):
            status = "completed"
        elif completed:
            status = "running"
        else:
            status = state.get("status", "pending")

        cleaned_completed = [n for n in completed if n not in failed]
        # ... current_node, progress, is_resumable
        return PipelineStatusProjection(...)
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_status_projection.py`
  - 测试全失败时 `status="failed"`
  - 测试全成功时 `status="completed"`
  - 测试部分完成时 `status="running"`
  - 测试 `completed_nodes` 中失败节点被清理
  - 测试旧 checkpoint 读取时矛盾清理

---

### Story 42.2: 新建 PipelineStateAccess 统一读取服务

**目标**：新建 `state_access.py`，提供统一的状态读取服务，所有查询必须经过此处。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/pipeline/state_access.py`）

#### 验收标准

- [ ] 新建 `PipelineStateAccess` 类，接受 `db_path` 和 `checkpointer`
- [ ] `get_projection(pipeline_id)` 方法：
  - 优先从 LangGraph checkpoint 读取最新状态
  - fallback 到 DB `state_json`
  - 返回 `PipelineStatusProjection`
- [ ] `list_pipelines()` 方法：返回所有 pipeline 的投影列表
- [ ] `get_pipeline_for_resume(pipeline_id)` 方法：返回恢复所需的清理后状态
- [ ] `get_pipeline_for_export(pipeline_id)` 方法：返回导出所需的清理后状态

#### 技术规格

```python
# autoBMAD/docuswarm/pipeline/state_access.py
class PipelineStateAccess:
    def __init__(self, db_path: str, checkpointer: Any) -> None:
        self._state_manager = StateManager(db_path)
        self._checkpointer = checkpointer

    async def get_projection(self, pipeline_id: str) -> PipelineStatusProjection:
        checkpoint_state = await self._load_checkpoint_state(pipeline_id)
        if checkpoint_state:
            return StatusProjectionMapper.from_checkpoint_state(checkpoint_state)
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline and pipeline.get("state_json"):
            state = json.loads(pipeline["state_json"])
            return StatusProjectionMapper.from_checkpoint_state(state)
        raise PipelineNotFoundError(pipeline_id)

    async def _load_checkpoint_state(self, pipeline_id: str) -> dict[str, Any] | None:
        thread_id = generate_thread_id(pipeline_id)
        ...
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_state_access.py`
  - 测试 checkpoint 优先读取
  - 测试 DB fallback
  - 测试投影一致性（checkpoint 与 DB 返回相同 projection）

---

### Story 42.3: StateManager 写屏障

**目标**：在 `StateManager` 中禁止直接修改 `status`/`completed_nodes`/`failed_nodes`/`error`。

**涉及文件**：1 个（`autoBMAD/docuswarm/storage/state_manager.py`）

#### 验收标准

- [ ] `update_pipeline_state()` 增加写屏障：禁止直接修改 `status`, `completed_nodes`, `failed_nodes`, `error`
- [ ] 直接修改上述字段时抛出 `ValueError`，提示使用 `StatusProjectionMapper`
- [ ] 允许更新元数据字段（如 `subject`, `tags`, `updated_at`）
- [ ] 保留 `state_json` 更新能力（用于 checkpoint 同步）

#### 技术规格

```python
# state_manager.py
class StateManager:
    def update_pipeline_state(self, pipeline_id: str, update: dict[str, Any]) -> None:
        forbidden_keys = {"status", "completed_nodes", "failed_nodes", "error"}
        if forbidden_keys & set(update.keys()):
            raise ValueError(
                f"Direct modification of {forbidden_keys} is prohibited. "
                "Use StatusProjectionMapper to derive these fields from checkpoint."
            )
        ...
```

#### 测试要求

- 单元测试：`tests/test_storage/test_state_manager_write_barrier.py`
  - 测试修改 `status` 时抛出 `ValueError`
  - 测试修改 `subject` 时正常通过
  - 测试批量更新包含禁止字段时抛出异常

---

### Story 42.4: Orchestrator 使用 StatusProjectionMapper

**目标**：`orchestrator.py` 使用 `StatusProjectionMapper` 替代 `_determine_final_status()`。

**涉及文件**：1 个（`autoBMAD/docuswarm/pipeline/orchestrator.py`）

#### 验收标准

- [ ] 删除或废弃 `_determine_final_status()` 方法
- [ ] `start_pipeline()` 结束时通过 `StatusProjectionMapper` 计算最终状态
- [ ] DB 更新时只写入 projection 的 `status`，不独立判断
- [ ] `get_pipeline_status()` 返回 `PipelineStatusProjection` 而非原始 state dict
- [ ] 恢复流程使用 `PipelineStateAccess` 获取清理后的状态

#### 技术规格

```python
# orchestrator.py
async def start_pipeline(self, ...):
    ...
    result = await graph.ainvoke(...)
    # 使用 projection mapper 替代 _determine_final_status
    projection = StatusProjectionMapper.from_checkpoint_state(result)
    await self._state_manager.update_pipeline_state(
        pipeline_id,
        {"status": projection.status, "state_json": json.dumps(result)},
    )
    return pipeline_id
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_orchestrator_projection.py`
  - 测试 graph result、projection、DB status 三者一致
  - 测试失败时 DB status 为 `failed`
  - 测试恢复时使用清理后的状态

---

### Story 42.5: CLI 命令通过 state_access 查询

**目标**：`status`、`export`、`resume`、`list` 等 CLI 命令统一通过 `PipelineStateAccess` 查询。

**涉及文件**：4 个（`cli/commands/status.py`、`cli/commands/export.py`、`cli/commands/resume.py`、`cli/commands/list.py`）

#### 验收标准

- [ ] `status` 命令通过 `PipelineStateAccess.get_projection()` 获取状态
- [ ] `export` 命令通过 `PipelineStateAccess` 获取状态，额外检查 deliverables 非空
- [ ] `resume` 命令通过 `PipelineStateAccess.get_pipeline_for_resume()` 获取恢复状态
- [ ] `list` 命令通过 `PipelineStateAccess.list_pipelines()` 获取列表
- [ ] 所有 CLI 命令不再直接读取 DB `state_json` 并独立解析

#### 测试要求

- 单元测试：`tests/test_cli/test_state_access_integration.py`
  - 测试 CLI status 返回投影状态
  - 测试 export 不导出空 deliverables 却标记 completed
  - 测试 resume 不会把失败节点当作已完成跳过

---

## 依赖关系

```
Story 42.1 → Story 42.2  (Mapper 先定义，StateAccess 才能使用)
Story 42.1 → Story 42.4  (Mapper 先定义，Orchestrator 才能使用)
Story 42.2 → Story 42.5  (StateAccess 先定义，CLI 才能使用)
Story 42.3 可与其他 Story 并行实施
```

---

## 实施阶段划分

### 阶段 1（核心基础设施）

- **Story 42.1**：新建 PipelineStatusProjection Mapper
- **Story 42.2**：新建 PipelineStateAccess 统一读取服务

### 阶段 2（集成与屏障）

- **Story 42.3**：StateManager 写屏障
- **Story 42.4**：Orchestrator 使用 StatusProjectionMapper
- **Story 42.5**：CLI 命令通过 state_access 查询

---

## 向后兼容

- **旧 checkpoint 读取**：`StatusProjectionMapper.from_checkpoint_state()` 在读取旧 checkpoint 时，执行"清理矛盾"逻辑（移除 `completed_nodes` 中的失败节点）。
- **DB 迁移**：无需 schema 变更，只需在读取时通过 mapper 修正。

---

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| 写屏障破坏现有代码 | MEDIUM | 分阶段引入，先警告后禁止 |
| StateAccess 性能问题（checkpoint 读取慢） | LOW | checkpoint 读取为本地 SQLite，通常 <10ms |
| CLI 命令行为变化 | MEDIUM | 保持输出格式兼容，仅修正状态语义 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `autoBMAD/docuswarm/pipeline/status_projection.py` | Story 42.1 新建 |
| `autoBMAD/docuswarm/pipeline/state_access.py` | Story 42.2 新建 |
| `autoBMAD/docuswarm/storage/state_manager.py` | Story 42.3 写屏障 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Story 42.4 集成点 |
| `cli/commands/status.py` | Story 42.5 CLI 接入 |
| `cli/commands/export.py` | Story 42.5 CLI 接入 |
| `cli/commands/resume.py` | Story 42.5 CLI 接入 |
| `cli/commands/list.py` | Story 42.5 CLI 接入 |

# Epic 12: CheckpointManager 提取重构

**Epic ID**: EPIC-12  
**关联方案**: [TDD-01-CheckpointManager-Refactor.md](../solution/TDD-01-CheckpointManager-Refactor.md)  
**Version**: 1.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 1-2 Days  
**Priority**: P0 - 关键

---

## 1. Epic Overview

### 1.1 Summary

提取 `HybridOrchestrator` 中的 checkpointer 创建逻辑，创建独立的 `CheckpointManager` 组件。消除 `orchestrator.py` 中 4 处的 DRY 违反，集中管理 `AsyncSqliteSaver` 的生命周期。

> **SDK 说明**: 本 Epic 与 SDK 选择无关，可与 Claude SDK Wrapper (EPIC-16) 并行实施。

### 1.2 Business Value

- **代码质量**: 消除重复代码，遵循 DRY 原则
- **可维护性**: 集中管理 checkpointer 配置（WAL 模式等）
- **可测试性**: 独立的组件便于单元测试
- **性能优化**: 支持 checkpointer 缓存复用

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| DRY 违反消除 | PRAGMA journal_mode 出现 0 次 |
| 代码行数减少 | orchestrator.py 减少 ~80 行 |
| 测试覆盖率 | CheckpointManager >= 90% |
| 缓存命中率 | 同一 pipeline_id 复用 checkpointer |

### 1.4 Dependencies

- **Requires**: 无（独立重构）
- **Blocks**: EPIC-13（可选优化，非阻塞）

---

## 2. Architecture Context

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CheckpointManager 组件架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HybridOrchestrator                                                         │
│  ├─→ CheckpointManager (新增，~150行)                                       │
│  │   ├─→ _cache: dict[pipeline_id, AsyncSqliteSaver]                       │
│  │   ├─→ get_or_create(pipeline_id) → (checkpointer, config)               │
│  │   ├─→ _create_checkpointer() → AsyncSqliteSaver                         │
│  │   └─→ close(pipeline_id?)                                               │
│  │                                                                          │
│  └─→ 原有方法简化：                                                         │
│      start_pipeline()                                                       │
│      resume_pipeline()                                                      │
│      restart_from_node()                                                    │
│      _restart_node()                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `pipeline/checkpoint_manager.py` | 新增：CheckpointManager 实现 |
| `pipeline/orchestrator.py` | 修改：重构 4 处重复代码 |
| `tests/unit/test_checkpoint_manager.py` | 新增：单元测试 |

---

## 3. User Stories

### Story 12.1: CheckpointManager 核心实现

**ID**: US-12.1  
**As a** developer  
**I want to** 创建 CheckpointManager 类  
**So that** checkpointer 生命周期管理集中化

**Acceptance Criteria**:
- [ ] `CheckpointManager` 类定义完成
- [ ] 支持 `db_path` 和 `external_checkpointer` 参数
- [ ] `_cache` 字典存储已创建的 checkpointer
- [ ] 集成 structlog 日志

**Technical Tasks**:
1. 创建 `pipeline/checkpoint_manager.py`
2. 实现 `__init__` 方法
3. 实现 `_create_checkpointer` 私有方法

**Implementation**:
```python
class CheckpointManager:
    def __init__(
        self,
        db_path: str,
        external_checkpointer: BaseCheckpointSaver[Any] | None = None,
    ) -> None:
        self._db_path = db_path
        self._external_checkpointer = external_checkpointer
        self._cache: dict[str, AsyncSqliteSaver] = {}
```

**Definition of Done**:
- [ ] 类结构完整
- [ ] 类型注解正确
- [ ] 日志绑定完成

---

### Story 12.2: get_or_create 方法实现

**ID**: US-12.2  
**As a** developer  
**I want to** 实现 get_or_create 方法  
**So that** 支持 checkpointer 的创建和复用

**Acceptance Criteria**:
- [ ] 返回 `(checkpointer, config)` 元组
- [ ] 相同 `pipeline_id` 返回相同 checkpointer 实例
- [ ] 不同 `pipeline_id` 返回不同实例
- [ ] 使用 `generate_thread_id` 生成 thread_id

**Technical Tasks**:
1. 实现 `get_or_create` 方法
2. 集成缓存逻辑
3. 集成外部 checkpointer 处理

**Implementation**:
```python
async def get_or_create(
    self,
    pipeline_id: str,
) -> tuple[BaseCheckpointSaver[Any], "RunnableConfig"]:
    if self._external_checkpointer is not None:
        checkpointer = self._external_checkpointer
    elif pipeline_id in self._cache:
        checkpointer = self._cache[pipeline_id]
    else:
        checkpointer = await self._create_checkpointer()
        self._cache[pipeline_id] = checkpointer
    
    thread_id = generate_thread_id(pipeline_id)
    config = create_checkpoint_config(thread_id)
    return checkpointer, config
```

**Definition of Done**:
- [ ] 缓存逻辑正确
- [ ] 外部 checkpointer 优先
- [ ] config 生成正确

---

### Story 12.3: WAL 模式配置

**ID**: US-12.3  
**As a** developer  
**I want to** 确保 WAL 模式正确配置  
**So that** 数据库支持并发访问

**Acceptance Criteria**:
- [ ] `PRAGMA journal_mode=WAL` 正确执行
- [ ] `PRAGMA synchronous=NORMAL` 正确执行
- [ ] `is_alive` 方法添加到 connection

**Technical Tasks**:
1. 在 `_create_checkpointer` 中执行 PRAGMA
2. 添加 `is_alive` lambda

**Implementation**:
```python
async def _create_checkpointer(self) -> AsyncSqliteSaver:
    conn = await aiosqlite.connect(self._db_path)
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    if not hasattr(conn, "is_alive"):
        conn.is_alive = lambda: True
    return AsyncSqliteSaver(conn=conn)
```

**Definition of Done**:
- [ ] WAL 模式验证测试通过
- [ ] 日志记录 checkpointer 创建

---

### Story 12.4: 生命周期管理

**ID**: US-12.4  
**As a** developer  
**I want to** 实现 close 方法  
**So that** 可以正确释放资源

**Acceptance Criteria**:
- [ ] `close(pipeline_id)` 关闭指定 pipeline 的 checkpointer
- [ ] `close()` 关闭所有缓存的 checkpointer
- [ ] 关闭后重新获取会创建新实例

**Technical Tasks**:
1. 实现 `close` 方法
2. 添加日志记录
3. 确保缓存清除

**Implementation**:
```python
async def close(self, pipeline_id: str | None = None) -> None:
    if pipeline_id is not None:
        if pipeline_id in self._cache:
            self._cache.pop(pipeline_id)
            self._logger.info("checkpointer_closed", pipeline_id=pipeline_id)
    else:
        count = len(self._cache)
        self._cache.clear()
        self._logger.info("all_checkpointers_closed", count=count)
```

**Definition of Done**:
- [ ] 单 pipeline 关闭测试通过
- [ ] 全部关闭测试通过
- [ ] 关闭后重建测试通过

---

### Story 12.5: Orchestrator 重构

**ID**: US-12.5  
**As a** developer  
**I want to** 重构 orchestrator.py  
**So that** 使用新的 CheckpointManager

**Acceptance Criteria**:
- [ ] 删除 4 处重复的 checkpointer 创建代码
- [ ] `start_pipeline` 使用 CheckpointManager
- [ ] `resume_pipeline` 使用 CheckpointManager
- [ ] `restart_from_node` 使用 CheckpointManager
- [ ] `_restart_node` 使用 CheckpointManager

**Technical Tasks**:
1. 在 `__init__` 中初始化 CheckpointManager
2. 替换 4 处 checkpointer 创建逻辑
3. 删除重复代码

**Implementation**:
```python
class HybridOrchestrator:
    def __init__(self, ...):
        ...
        self._checkpoint_manager = CheckpointManager(
            db_path=self._db_path,
            external_checkpointer=self._checkpointer,
        )
    
    async def start_pipeline(self, subject_context, pipeline_id=None):
        ...
        checkpointer, config = await self._checkpoint_manager.get_or_create(
            final_pipeline_id
        )
        ...
```

**Definition of Done**:
- [ ] orchestrator.py 行数减少 >= 60
- [ ] `PRAGMA journal_mode` 出现 0 次
- [ ] 所有方法使用 CheckpointManager

---

## 4. Technical Specifications

### 4.1 API Reference

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(db_path: str, external_checkpointer: BaseCheckpointSaver \| None = None)` | 初始化管理器 |
| `get_or_create` | `(pipeline_id: str) -> tuple[BaseCheckpointSaver, RunnableConfig]` | 获取或创建 checkpointer |
| `close` | `(pipeline_id: str \| None = None) -> None` | 关闭 checkpointer |

### 4.2 Performance Targets

| Metric | Target |
|--------|--------|
| Checkpointer 创建 | < 100ms |
| 缓存复用 | < 1ms |
| 关闭操作 | < 50ms |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test | Description | File |
|------|-------------|------|
| `test_get_or_create_returns_checkpointer_and_config` | 验证返回类型 | test_checkpoint_manager.py |
| `test_thread_id_generation` | 验证 thread_id 生成 | test_checkpoint_manager.py |
| `test_same_pipeline_returns_same_checkpointer` | 验证缓存复用 | test_checkpoint_manager.py |
| `test_different_pipelines_get_different_checkpointers` | 验证隔离 | test_checkpoint_manager.py |
| `test_external_checkpointer_is_used_directly` | 验证外部优先 | test_checkpoint_manager.py |
| `test_wal_mode_enabled` | 验证 WAL 模式 | test_checkpoint_manager.py |
| `test_close_single_pipeline` | 验证单关闭 | test_checkpoint_manager.py |
| `test_close_all` | 验证全部关闭 | test_checkpoint_manager.py |

### 5.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_pipeline_lifecycle_with_manager` | 完整 pipeline 使用 CheckpointManager |
| `test_multiple_pipelines_isolated` | 多 pipeline 隔离验证 |

### 5.3 Code Quality Gates

```bash
# 类型检查
basedpyright autoBMAD/docuswarm/pipeline/checkpoint_manager.py

# 代码风格
ruff check autoBMAD/docuswarm/pipeline/checkpoint_manager.py

# 覆盖率
pytest tests/unit/test_checkpoint_manager.py --cov=autoBMAD.docuswarm.pipeline.checkpoint_manager --cov-report=term-missing
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 缓存导致连接泄漏 | 中 | 高 | 添加 `close()` 方法，pipeline 完成时调用 |
| WAL 模式未正确设置 | 低 | 高 | 测试验证 WAL 模式 |
| 外部 checkpointer 处理错误 | 低 | 中 | 添加专门单元测试 |
| 重构引入回归 | 中 | 高 | 完整回归测试后再合并 |

---

## 7. Definition of Done (Epic Level)

- [ ] US-12.1 完成：CheckpointManager 核心实现
- [ ] US-12.2 完成：get_or_create 方法
- [ ] US-12.3 完成：WAL 模式配置
- [ ] US-12.4 完成：生命周期管理
- [ ] US-12.5 完成：Orchestrator 重构
- [ ] 单元测试覆盖率 >= 90%
- [ ] 集成测试 100% 通过
- [ ] orchestrator.py 行数减少 >= 60
- [ ] `PRAGMA journal_mode` 出现 0 次
- [ ] basedpyright 0 错误
- [ ] ruff 0 违反

---

## 8. References

| Document | Location |
|----------|----------|
| TDD 方案 | `docs/solution/TDD-01-CheckpointManager-Refactor.md` |
| Pipeline Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` |

---

**Epic End**

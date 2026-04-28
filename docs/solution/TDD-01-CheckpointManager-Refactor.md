# TDD 重构方案: CheckpointManager 提取

> **关联研究报告**: [DocuSwarm-重构详细研究报告.md](../research/DocuSwarm-重构详细研究报告.md) P0-2  
> **优先级**: P0 - 关键  
> **预估工期**: 1-2 天  
> **影响范围**: `pipeline/orchestrator.py`, `pipeline/checkpoint_manager.py` (新增)

---

## 1. 问题分析

### 1.1 当前代码问题

在 `orchestrator.py` 中，checkpointer 创建逻辑在三个方法中**完全重复**：

| 方法 | 行号范围 | 重复代码特征 |
|------|---------|-------------|
| `start_pipeline()` | 438-457 | `AsyncSqliteSaver` 创建 + WAL模式设置 |
| `resume_pipeline()` | 561-581 | 同上，完全一致 |
| `restart_from_node()` | 726-746 | 同上，完全一致 |
| `_restart_node()` | 892-912 | 同上，完全一致 |

**代码重复示例**（简化）：
```python
# 在 4 处出现完全相同的模式
checkpointer = self._checkpointer
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    aconn = await aiosqlite.connect(self._db_path)
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")
    if not hasattr(aconn, "is_alive"):
        aconn.is_alive = lambda: True
    checkpointer = AsyncSqliteSaver(conn=aconn)
```

### 1.2 违反原则

- **DRY (Don't Repeat Yourself)**: 相同逻辑在 4 处重复
- **单一职责原则 (SRP)**: Orchestrator 既负责流程控制又负责 checkpointer 生命周期管理

---

## 2. 目标设计

### 2.1 CheckpointManager 职责

```
┌─────────────────────────────────────────────────────────────┐
│                    CheckpointManager                         │
├─────────────────────────────────────────────────────────────┤
│  - 统一管理 AsyncSqliteSaver 的创建和复用                     │
│  - 维护 checkpointer 缓存（按 pipeline_id）                  │
│  - 生成 RunnableConfig（含 thread_id）                       │
│  - 提供连接生命周期管理（关闭、清理）                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 API 设计

```python
class CheckpointManager:
    """Manage LangGraph checkpointer lifecycle.
    
    This class centralizes checkpointer creation to eliminate DRY violations
    in the orchestrator.
    """
    
    def __init__(
        self, 
        db_path: str, 
        external_checkpointer: BaseCheckpointSaver | None = None
    ) -> None:
        """Initialize checkpoint manager.
        
        Args:
            db_path: Path to SQLite database for checkpointer storage
            external_checkpointer: Optional externally provided checkpointer
        """
    
    async def get_or_create(
        self, 
        pipeline_id: str
    ) -> tuple[BaseCheckpointSaver, RunnableConfig]:
        """Get or create checkpointer and config for pipeline.
        
        This is the ONLY method that should be called by orchestrator.
        All checkpointer creation logic is centralized here.
        
        Args:
            pipeline_id: The pipeline identifier
            
        Returns:
            Tuple of (checkpointer, config) ready for LangGraph
        """
    
    async def close(self, pipeline_id: str | None = None) -> None:
        """Close checkpointer connections.
        
        Args:
            pipeline_id: If provided, close only that pipeline's checkpointer.
                        If None, close all cached checkpointers.
        """
```

---

## 3. 测试驱动开发计划

### Phase 1: 编写测试（红阶段）

#### Test 1: 基础创建测试
```python
# tests/unit/test_checkpoint_manager.py

import pytest
from autoBMAD.docuswarm.pipeline.checkpoint_manager import CheckpointManager


class TestCheckpointManagerCreation:
    """Test CheckpointManager initialization and basic creation."""
    
    @pytest.mark.asyncio
    async def test_get_or_create_returns_checkpointer_and_config(self, tmp_path):
        """Test that get_or_create returns both checkpointer and config."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        
        # Act
        checkpointer, config = await manager.get_or_create("pipeline-123")
        
        # Assert
        assert checkpointer is not None
        assert config is not None
        assert "configurable" in config
        assert "thread_id" in config["configurable"]
    
    @pytest.mark.asyncio
    async def test_thread_id_generation(self, tmp_path):
        """Test that thread_id is correctly generated from pipeline_id."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        
        # Act
        _, config = await manager.get_or_create("my-pipeline")
        
        # Assert
        thread_id = config["configurable"]["thread_id"]
        assert "my-pipeline" in thread_id
        assert thread_id.startswith("thread-")
```

#### Test 2: 缓存复用测试（关键测试）
```python
class TestCheckpointManagerCaching:
    """Test that checkpointers are cached and reused correctly."""
    
    @pytest.mark.asyncio
    async def test_same_pipeline_returns_same_checkpointer(self, tmp_path):
        """CRITICAL: Same pipeline_id should return same checkpointer instance.
        
        This test ensures the DRY fix works - we don't create multiple
        checkpointers for the same pipeline.
        """
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        
        # Act
        checkpointer1, config1 = await manager.get_or_create("pipeline-123")
        checkpointer2, config2 = await manager.get_or_create("pipeline-123")
        
        # Assert - same instance
        assert checkpointer1 is checkpointer2, \
            "Same pipeline should reuse the same checkpointer instance"
        assert config1 == config2, \
            "Same pipeline should return identical config"
    
    @pytest.mark.asyncio
    async def test_different_pipelines_get_different_checkpointers(self, tmp_path):
        """Different pipelines should get separate checkpointers."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        
        # Act
        checkpointer1, _ = await manager.get_or_create("pipeline-1")
        checkpointer2, _ = await manager.get_or_create("pipeline-2")
        
        # Assert
        assert checkpointer1 is not checkpointer2, \
            "Different pipelines should have separate checkpointers"
```

#### Test 3: 外部 checkpointer 测试
```python
class TestCheckpointManagerExternal:
    """Test behavior with externally provided checkpointer."""
    
    @pytest.mark.asyncio
    async def test_external_checkpointer_is_used_directly(self, tmp_path):
        """If external checkpointer provided, use it without creating new one."""
        # Arrange
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        import aiosqlite
        
        db_path = str(tmp_path / "test.db")
        conn = await aiosqlite.connect(db_path)
        external = AsyncSqliteSaver(conn=conn)
        
        manager = CheckpointManager(
            db_path=db_path,
            external_checkpointer=external
        )
        
        # Act
        checkpointer, _ = await manager.get_or_create("pipeline-123")
        
        # Assert
        assert checkpointer is external, \
            "Should use the externally provided checkpointer"
```

#### Test 4: WAL 模式设置测试
```python
class TestCheckpointManagerWALMode:
    """Test that WAL mode is correctly configured."""
    
    @pytest.mark.asyncio
    async def test_wal_mode_enabled(self, tmp_path):
        """Verify that created checkpointer has WAL mode enabled."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        
        # Act
        await manager.get_or_create("pipeline-123")
        
        # Assert - check database file has WAL
        import aiosqlite
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("PRAGMA journal_mode")
            row = await cursor.fetchone()
            assert row[0].upper() == "WAL", "WAL mode should be enabled"
```

#### Test 5: 生命周期管理测试
```python
class TestCheckpointManagerLifecycle:
    """Test connection lifecycle management."""
    
    @pytest.mark.asyncio
    async def test_close_single_pipeline(self, tmp_path):
        """Test closing checkpointer for specific pipeline."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        checkpointer, _ = await manager.get_or_create("pipeline-123")
        
        # Act
        await manager.close("pipeline-123")
        
        # Assert - after close, new checkpointer should be created
        checkpointer2, _ = await manager.get_or_create("pipeline-123")
        assert checkpointer is not checkpointer2, \
            "After close, should create new checkpointer"
    
    @pytest.mark.asyncio
    async def test_close_all(self, tmp_path):
        """Test closing all checkpointers."""
        # Arrange
        db_path = str(tmp_path / "test.db")
        manager = CheckpointManager(db_path=db_path)
        cp1, _ = await manager.get_or_create("pipeline-1")
        cp2, _ = await manager.get_or_create("pipeline-2")
        
        # Act
        await manager.close()  # Close all
        
        # Assert
        cp1_new, _ = await manager.get_or_create("pipeline-1")
        cp2_new, _ = await manager.get_or_create("pipeline-2")
        assert cp1 is not cp1_new
        assert cp2 is not cp2_new
```

### Phase 2: 实现代码（绿阶段）

基于测试要求，实现 `checkpoint_manager.py`：

```python
"""Checkpoint Manager - Centralized checkpointer lifecycle management.

This module eliminates DRY violations in orchestrator.py by centralizing
all AsyncSqliteSaver creation logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiosqlite
import structlog
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langgraph.checkpoint.base import BaseCheckpointSaver

from autoBMAD.docuswarm.storage.checkpoints import (
    create_checkpoint_config,
    generate_thread_id,
)

logger = structlog.get_logger(__name__)


class CheckpointManager:
    """Manage LangGraph checkpointer lifecycle.
    
    Centralizes checkpointer creation to eliminate DRY violations.
    Maintains a cache of checkpointers by pipeline_id for reuse.
    
    Example:
        >>> manager = CheckpointManager(db_path="docuswarm.db")
        >>> checkpointer, config = await manager.get_or_create("pipeline-123")
        >>> # Use with LangGraph
        >>> graph = create_pipeline_graph(..., checkpointer=checkpointer)
        >>> result = await graph.ainvoke(state, config)
        >>> # Cleanup when done
        >>> await manager.close("pipeline-123")
    """
    
    def __init__(
        self,
        db_path: str,
        external_checkpointer: BaseCheckpointSaver[Any] | None = None,
    ) -> None:
        """Initialize checkpoint manager.
        
        Args:
            db_path: Path to SQLite database for checkpointer storage.
            external_checkpointer: Optional externally provided checkpointer.
                                  If provided, it will be used for all pipelines.
        """
        self._db_path = db_path
        self._external_checkpointer = external_checkpointer
        self._cache: dict[str, AsyncSqliteSaver] = {}
        self._logger = logger.bind(component="CheckpointManager")
    
    async def get_or_create(
        self,
        pipeline_id: str,
    ) -> tuple[BaseCheckpointSaver[Any], "RunnableConfig"]:
        """Get or create checkpointer and config for pipeline.
        
        This is the ONLY method that should be called for checkpointer access.
        It handles:
        - Creating AsyncSqliteSaver with proper configuration
        - Enabling WAL mode for better concurrency
        - Caching and reusing checkpointers by pipeline_id
        - Generating appropriate thread_id and config
        
        Args:
            pipeline_id: The pipeline identifier.
            
        Returns:
            Tuple of (checkpointer, config) ready for LangGraph.
        """
        # Use external checkpointer if provided
        if self._external_checkpointer is not None:
            checkpointer = self._external_checkpointer
        elif pipeline_id in self._cache:
            # Return cached checkpointer
            checkpointer = self._cache[pipeline_id]
        else:
            # Create new checkpointer
            checkpointer = await self._create_checkpointer()
            self._cache[pipeline_id] = checkpointer
            self._logger.info(
                "checkpointer_created",
                pipeline_id=pipeline_id,
                db_path=self._db_path,
            )
        
        # Generate thread_id and config
        thread_id = generate_thread_id(pipeline_id)
        config = create_checkpoint_config(thread_id)
        
        return checkpointer, config
    
    async def _create_checkpointer(self) -> AsyncSqliteSaver:
        """Create a new AsyncSqliteSaver with proper configuration.
        
        Returns:
            Configured AsyncSqliteSaver instance.
        """
        # Create async connection
        conn = await aiosqlite.connect(self._db_path)
        
        # Enable WAL mode for better concurrent access
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")
        
        # Add is_alive method for langgraph compatibility
        if not hasattr(conn, "is_alive"):
            conn.is_alive = lambda: True  # type: ignore[attr-defined]
        
        return AsyncSqliteSaver(conn=conn)
    
    async def close(self, pipeline_id: str | None = None) -> None:
        """Close checkpointer connections.
        
        Args:
            pipeline_id: If provided, close only that pipeline's checkpointer.
                        If None, close all cached checkpointers.
        """
        if pipeline_id is not None:
            # Close specific pipeline's checkpointer
            if pipeline_id in self._cache:
                checkpointer = self._cache.pop(pipeline_id)
                # Note: AsyncSqliteSaver doesn't have explicit close,
                # but the underlying connection will be closed on garbage collection
                self._logger.info("checkpointer_closed", pipeline_id=pipeline_id)
        else:
            # Close all checkpointers
            count = len(self._cache)
            self._cache.clear()
            self._logger.info("all_checkpointers_closed", count=count)
```

### Phase 3: 重构 Orchestrator（重构阶段）

**重构前**（orchestrator.py 中的重复代码）：
```python
# start_pipeline() 方法中
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    aconn = await aiosqlite.connect(self._db_path)
    await aconn.execute("PRAGMA journal_mode=WAL")
    ...
    checkpointer = AsyncSqliteSaver(conn=aconn)

# resume_pipeline() 方法中 - 完全相同的代码
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    ...

# restart_from_node() 方法中 - 完全相同的代码
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    ...
```

**重构后**：
```python
from autoBMAD.docuswarm.pipeline.checkpoint_manager import CheckpointManager

class HybridOrchestrator:
    def __init__(self, ...):
        ...
        # Initialize checkpoint manager
        self._checkpoint_manager = CheckpointManager(
            db_path=self._db_path,
            external_checkpointer=self._checkpointer,
        )
    
    async def start_pipeline(self, subject_context, pipeline_id=None):
        ...
        # Replace 20+ lines of checkpointer creation with 1 line
        checkpointer, config = await self._checkpoint_manager.get_or_create(
            final_pipeline_id
        )
        ...
    
    async def resume_pipeline(self, pipeline_id):
        ...
        # Same simple call
        checkpointer, config = await self._checkpoint_manager.get_or_create(
            pipeline_id
        )
        ...
    
    async def restart_from_node(self, pipeline_id, node_id):
        ...
        # Same simple call
        checkpointer, config = await self._checkpoint_manager.get_or_create(
            pipeline_id
        )
        ...
```

---

## 4. 验证清单

### 4.1 测试覆盖验证

```bash
# 运行所有 CheckpointManager 测试
pytest tests/unit/test_checkpoint_manager.py -v

# 验证覆盖率
pytest tests/unit/test_checkpoint_manager.py --cov=autoBMAD.docuswarm.pipeline.checkpoint_manager --cov-report=term-missing
```

**期望结果**:
- [ ] 所有测试通过
- [ ] 代码覆盖率 >= 90%
- [ ] 无类型检查错误 (`basedpyright`)
- [ ] 无代码风格错误 (`ruff`)

### 4.2 重构验证

```bash
# 验证 orchestrator.py 行数减少
wc -l autoBMAD/docuswarm/pipeline/orchestrator.py
# 期望: 从 ~1100 行减少 ~80 行（4处 × 每处约20行）

# 检查不再有重复代码模式
grep -n "PRAGMA journal_mode" autoBMAD/docuswarm/pipeline/orchestrator.py
# 期望: 0 处（原来有 4 处）
```

### 4.3 集成测试

```bash
# 运行现有集成测试确保没有破坏功能
pytest tests/integration/test_pipeline_lifecycle.py -v

# 手动测试
python -m autoBMAD.docuswarm start -c docs/test_context.md
```

---

## 5. 风险评估与缓解

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|---------|
| 缓存导致连接泄漏 | 中 | 高 | 添加 `close()` 方法，在 pipeline 完成时调用 |
| WAL 模式未正确设置 | 低 | 高 | 测试验证 WAL 模式 |
| 外部 checkpointer 处理错误 | 低 | 中 | 添加专门的单元测试 |
| 线程安全问题 | 低 | 高 | 确保每个 pipeline 有自己的 checkpointer |

---

## 6. 实施步骤

1. **Step 1**: 创建 `test_checkpoint_manager.py` 测试文件（所有测试应该失败）
2. **Step 2**: 创建 `checkpoint_manager.py` 实现（测试应该通过）
3. **Step 3**: 重构 `orchestrator.py`，使用 `CheckpointManager`
4. **Step 4**: 运行所有测试验证
5. **Step 5**: 运行集成测试验证
6. **Step 6**: 代码审查和合并

---

> **验收标准**: 
> - [ ] 所有单元测试通过
> - [ ] 所有集成测试通过  
> - [ ] orchestrator.py 行数减少 >= 60 行
> - [ ] 代码重复消除（PRAGMA journal_mode 出现 0 次）
> - [ ] basedpyright + ruff 检查通过

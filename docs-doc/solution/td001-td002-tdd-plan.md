# TD-001 + TD-002 测试驱动重构方案

> **目标**: 通过 TDD 方式重构 Checkpointer 创建逻辑，消除代码重复并统一 monkey-patch 实现
> **时间**: Week 1
> **范围**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

---

## 重构策略

### TDD 循环

```
1. RED   → 编写失败的测试
2. GREEN → 编写最小实现使测试通过
3. BLUE  → 重构优化代码
```

### 重构步骤

```
Step 1: 提取 _patch_aiosqlite_connection() 方法
Step 2: 提取 _create_checkpointer() 方法
Step 3: 替换 4 处重复代码
Step 4: 运行全部测试验证
```

---

## 详细实施计划

### Phase 1: 编写测试

创建 `tests/unit/test_checkpointer_refactor.py`:

```python
"""Tests for TD-001 + TD-002 checkpointer refactor.

TDD Cycle:
1. Write failing tests for _create_checkpointer and _patch_aiosqlite_connection
2. Implement the methods
3. Refactor 4 call sites
4. Verify all tests pass
"""
```

**测试用例清单**:

| # | 测试方法 | 测试目标 | 预期结果 |
|---|---------|---------|---------|
| 1 | `test_patch_aiosqlite_connection_adds_is_alive` | 验证 monkey-patch 添加 is_alive | conn 有 is_alive 方法 |
| 2 | `test_patch_aiosqlite_connection_idempotent` | 验证重复 patch 不会出错 | 第二次调用安全 |
| 3 | `test_create_checkpointer_returns_async_sqlite_saver` | 验证返回类型正确 | 返回 AsyncSqliteSaver |
| 4 | `test_create_checkpointer_enables_wal_mode` | 验证 WAL 模式启用 | PRAGMA 设置正确 |
| 5 | `test_create_checkpointer_applies_patch` | 验证 patch 被应用 | conn.is_alive 存在 |
| 6 | `test_start_pipeline_uses_create_checkpointer` | 验证 start_pipeline 使用新方法 | 调用 _create_checkpointer |
| 7 | `test_resume_pipeline_uses_create_checkpointer` | 验证 resume_pipeline 使用新方法 | 调用 _create_checkpointer |
| 8 | `test_restart_from_node_uses_create_checkpointer` | 验证 restart_from_node 使用新方法 | 调用 _create_checkpointer |
| 9 | `test_restart_node_uses_create_checkpointer` | 验证 _restart_node 使用新方法 | 调用 _create_checkpointer |

### Phase 2: 提取方法

#### Step 2.1: 添加 _patch_aiosqlite_connection

```python
def _patch_aiosqlite_connection(self, conn) -> None:
    """Add is_alive method for LangGraph compatibility (TD-002).
    
    LangGraph's AsyncSqliteSaver expects connection to have is_alive()
    method, but aiosqlite doesn't provide it. This method patches
    the connection with a simple implementation.
    
    FIXME: Track https://github.com/langchain-ai/langgraph/issues/XXX
    Remove this patch when LangGraph adds native aiosqlite support.
    
    Args:
        conn: The aiosqlite connection to patch.
    """
    if not hasattr(conn, "is_alive"):
        conn.is_alive = lambda: True  # type: ignore[attr-defined]
```

#### Step 2.2: 添加 _create_checkpointer

```python
async def _create_checkpointer(self) -> AsyncSqliteSaver:
    """Create an AsyncSqliteSaver checkpointer with proper configuration (TD-001).
    
    Centralizes checkpointer creation to eliminate duplication.
    Includes monkey-patch for LangGraph compatibility.
    
    Returns:
        Configured AsyncSqliteSaver instance.
    """
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    
    # Create async connection
    aconn = await aiosqlite.connect(self._db_path)
    
    # Enable WAL mode for better concurrent access
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")
    
    # Apply monkey-patch for LangGraph compatibility (TD-002)
    self._patch_aiosqlite_connection(aconn)
    
    return AsyncSqliteSaver(conn=aconn)
```

### Phase 3: 替换重复代码

#### 替换点 1: start_pipeline (行 437-457)

**Before**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    # Create async connection for the checkpointer
    aconn = await aiosqlite.connect(self._db_path)

    # Enable WAL mode
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")

    # Add is_alive method for langgraph compatibility
    if not hasattr(aconn, "is_alive"):
        def _is_alive() -> bool:
            return True
        aconn.is_alive = _is_alive  # type: ignore[attr-defined]

    checkpointer = AsyncSqliteSaver(conn=aconn)
```

**After**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    checkpointer = await self._create_checkpointer()
```

#### 替换点 2: resume_pipeline (行 561-581)

**Before**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    # Create async connection for the checkpointer
    aconn = await aiosqlite.connect(self._db_path)

    # Enable WAL mode
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")

    # Add is_alive method for langgraph compatibility
    if not hasattr(aconn, "is_alive"):
        def _is_alive() -> bool:
            return True
        aconn.is_alive = _is_alive  # type: ignore[attr-defined]

    checkpointer = AsyncSqliteSaver(conn=aconn)
```

**After**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    checkpointer = await self._create_checkpointer()
```

#### 替换点 3: restart_from_node (行 726-746)

**Before**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    # Create async connection for the checkpointer
    aconn = await aiosqlite.connect(self._db_path)

    # Enable WAL mode
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")

    # Add is_alive method for langgraph compatibility
    if not hasattr(aconn, "is_alive"):
        def _is_alive() -> bool:
            return True
        aconn.is_alive = _is_alive  # type: ignore[attr-defined]

    checkpointer = AsyncSqliteSaver(conn=aconn)
```

**After**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    checkpointer = await self._create_checkpointer()
```

#### 替换点 4: _restart_node (行 893-912)

**Before**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    # Create async connection for the checkpointer
    aconn = await aiosqlite.connect(self._db_path)

    # Enable WAL mode
    await aconn.execute("PRAGMA journal_mode=WAL")
    await aconn.execute("PRAGMA synchronous=NORMAL")

    # Add is_alive method for langgraph compatibility
    if not hasattr(aconn, "is_alive"):
        def _is_alive() -> bool:
            return True
        aconn.is_alive = _is_alive  # type: ignore[attr-defined]

    checkpointer = AsyncSqliteSaver(conn=aconn)
```

**After**:
```python
checkpointer = self._checkpointer
if checkpointer is None:
    checkpointer = await self._create_checkpointer()
```

### Phase 4: 验证

#### 测试命令

```bash
# 运行专项测试
python -m pytest tests/unit/test_checkpointer_refactor.py -v

# 运行现有测试确保不破坏
python -m pytest tests/unit/test_message_extraction.py -v

# 检查代码行数变化
wc -l autoBMAD/docuswarm/pipeline/orchestrator.py
```

#### 预期结果

- 所有新测试通过
- 所有现有测试通过
- 代码行数减少 ~60 行
- 无功能变更

---

## 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 重构引入 bug | 低 | 高 | 完整测试覆盖，小步提交 |
| 类型检查失败 | 中 | 低 | 确保 type: ignore 注释保留 |
| 性能退化 | 低 | 低 | 无额外 IO 操作，仅代码移动 |

---

## 提交计划

```
Commit 1: Add tests for _patch_aiosqlite_connection and _create_checkpointer
Commit 2: Implement _patch_aiosqlite_connection method
Commit 3: Implement _create_checkpointer method
Commit 4: Replace duplication in start_pipeline
Commit 5: Replace duplication in resume_pipeline
Commit 6: Replace duplication in restart_from_node
Commit 7: Replace duplication in _restart_node
Commit 8: Run all tests and verify
```

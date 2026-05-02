# TD-001 深度分析报告: Checkpointer 代码重复

## 问题概述

**问题**: aiosqlite 连接 + PRAGMA + monkey-patch 代码在 orchestrator.py 中重复 4 次
**影响**: ~60 行冗余代码，维护困难，容易遗漏修改
**位置**: 
- `start_pipeline()` (行 437-457)
- `resume_pipeline()` (行 561-581)
- `restart_from_node()` (行 726-746)
- `_restart_node()` (行 893-912)

## 重复代码分析

### Checkpointer Creation Block

**严重级别**: HIGH
**重复行数**: ~63 行

**出现位置**:
- `start_pipeline()` (行 438-458)
- `resume_pipeline()` (行 562-582)
- `restart_from_node()` (行 727-747)
- `_restart_node()` (行 893-913)

**代码样例**:
```python
                import aiosqlite
                from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
                aconn = await aiosqlite.connect(self._db_path)
                await aconn.execute("PRAGMA journal_mode=WAL")
                await aconn.execute("PRAGMA synchronous=NORMAL")
                # Add is_alive method for langgraph compatibility
                if not hasattr(aconn, "is_alive"):
                    def _is_alive() -> bool:
                    aconn.is_alive = ...
```

**修复建议**:
> Extract _create_checkpointer() private method to reduce ~60 lines of duplication

## 修复方案

### 推荐实现

```python
async def _create_checkpointer(self) -> AsyncSqliteSaver:
    """Create an AsyncSqliteSaver checkpointer with proper async support."""
    import aiosqlite
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    aconn = await aiosqlite.connect(self._db_path)
    await aconn.execute('PRAGMA journal_mode=WAL')
    await aconn.execute('PRAGMA synchronous=NORMAL')

    # Patch for langgraph compatibility (TD-002)
    self._patch_aiosqlite_connection(aconn)

    return AsyncSqliteSaver(conn=aconn)

def _patch_aiosqlite_connection(self, conn) -> None:
    """Add is_alive method for langgraph compatibility (TD-002)."""
    if not hasattr(conn, 'is_alive'):
        conn.is_alive = lambda: True  # noqa: E731
```

### 使用方式

将 4 处重复代码替换为:

```python
checkpointer = self._checkpointer
if checkpointer is None:
    checkpointer = await self._create_checkpointer()
```

## 预期收益

- **代码行数减少**: ~60 行 → ~15 行
- **维护成本降低**: 修改只需一处
- **可读性提升**: 意图更清晰
- **测试简化**: 只需测试一个方法

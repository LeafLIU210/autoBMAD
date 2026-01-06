# 修复实施方案：跨任务取消作用域与锁管理问题

## 执行摘要

本文档详细说明了修复 sdk_wrapper.py 和 state_manager.py 中异步取消和锁管理问题的实施方案。

## 1. 问题分析

### 核心问题

**问题 #1: sdk_wrapper.py:467 - 跨任务取消作用域冲突**
- 位置: autoBMAD/epic_automation/sdk_wrapper.py:467
- 代码: await asyncio.wait_for(close_coro, timeout=1.0)
- 原因: 在生成器清理过程中，当外部存在取消作用域时，wait_for 会创建新的取消作用域，导致嵌套取消作用域冲突

**问题 #2: sdk_wrapper.py:437, 469 - 取消异常被错误吞噬**
- CancelledError 被捕获但未正确重新抛出或传播，导致取消状态不一致

**问题 #3: state_manager.py - 锁管理不一致**
- 混用 wait_for+manual release 与 async with，可能导致锁泄漏

## 2. 修复策略

### 2.1 sdk_wrapper.py 修复策略

#### 策略 #1: 创建安全的生成器清理包装器

实现安全的生成器清理，避免在活动取消作用域内直接调用 wait_for：

```python
async def _safe_generator_cleanup(self, generator):
    """Safely cleanup generator without cross-task cancellation scope conflicts."""
    if generator is None:
        return
    
    aclose = getattr(generator, 'aclose', None)
    if not aclose or not callable(aclose):
        return
    
    try:
        # Create a cleanup task without waiting in the active cancellation scope
        cleanup_task = asyncio.create_task(aclose())
        
        # Wait for cleanup with timeout
        try:
            await asyncio.wait_for(cleanup_task, timeout=1.0)
        except asyncio.TimeoutError:
            # Cleanup timed out - cancel the task
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
            logger.debug("Generator cleanup task timed out and was cancelled")
        except asyncio.CancelledError:
            # Outer cancellation occurred during cleanup
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
            logger.debug("Generator cleanup was cancelled (propagation blocked)")
    except RuntimeError as e:
        error_msg = str(e)
        if "cancel scope" in error_msg:
            logger.debug(f"Expected cancel scope error during cleanup: {e}")
        elif "Event loop is closed" in error_msg:
            logger.debug(f"Event loop closed, generator cleanup skipped: {e}")
        else:
            logger.warning(f"Unexpected RuntimeError during generator cleanup: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error during generator cleanup: {e}")
```

#### 策略 #2: 统一取消异常处理

在边界点处理取消，阻止取消错误的传播，但记录日志：

```python
except asyncio.CancelledError:
    logger.warning("Claude SDK execution was cancelled")
    try:
        await self._cleanup_on_cancellation()
    except Exception as e:
        logger.debug(f"Error during cancellation cleanup: {e}")
    return False
```

### 2.2 state_manager.py 修复策略

#### 策略: 统一使用 async with 模式

将 wait_for + manual release 模式改为 async with + timeout 模式：

**update_story_status 方法 (lines 204-326):**

```python
# 旧代码:
try:
    await asyncio.wait_for(self._lock.acquire(), timeout=lock_timeout)
except asyncio.TimeoutError:
    logger.error(f"Lock timeout for {story_path} after {lock_timeout}s")
    return False, None

try:
    # ... work ...
finally:
    self._lock.release()

# 新代码:
try:
    async with asyncio.timeout(lock_timeout):
        async with self._lock:
            # ... work ...
except asyncio.TimeoutError:
    logger.error(f"Lock timeout for {story_path} after {lock_timeout}s")
    return False, None
```

**update_stories_status_batch 方法 (lines 1117-1216):**

应用相同的模式变更。

## 3. 实施顺序

### 阶段 1: 备份现有文件

```bash
mkdir -p /tmp/fix_backup_20260107
cp autoBMAD/epic_automation/sdk_wrapper.py /tmp/fix_backup_20260107/sdk_wrapper.py.backup
cp autoBMAD/epic_automation/state_manager.py /tmp/fix_backup_20260107/state_manager.py.backup
```

### 阶段 2: 修复 sdk_wrapper.py

**步骤 2.1**: 添加 _safe_generator_cleanup 方法 (line 479 之后)

**步骤 2.2**: 修改 _managed_query 方法 (lines 457-478)
- 替换生成器清理逻辑为调用 _safe_generator_cleanup

**步骤 2.3**: 改进 _execute_safely 中的取消处理 (lines 433-437)

**步骤 2.4**: 改进 _cleanup_on_cancellation 方法 (lines 480-501)

### 阶段 3: 修复 state_manager.py

**步骤 3.1**: 重构 update_story_status 方法 (lines 204-326)
- 使用 async with asyncio.timeout + async with self._lock

**步骤 3.2**: 重构 update_stories_status_batch 方法 (lines 1117-1216)
- 应用相同模式变更

### 阶段 4: 测试验证

```bash
# 单元测试
pytest tests/test_sdk_wrapper_cleanup.py -v
pytest tests/test_state_manager_lock.py -v

# 集成测试
pytest tests/test_end_to_end_cancellation.py -v
pytest tests/test_lock_contention.py -v

# 回归测试
pytest tests/test_regression.py -v

# 完整测试
pytest tests/ -v --cov=autoBMAD.epic_automation --cov-report=html
```

## 4. 验收标准

✅ 所有单元测试通过
✅ 所有集成测试通过  
✅ 所有回归测试通过
✅ 代码覆盖率 > 90%
✅ 无内存泄漏
✅ 无死锁或活锁
✅ 取消操作正确传播
✅ 锁正确释放

## 5. 风险评估

### 高风险项

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 异步锁语义变更 | 中 | 高 | 使用 asyncio.timeout 保持相同超时语义 |
| 取消处理回归 | 中 | 高 | 详细测试取消场景 |
| 向后兼容性破坏 | 低 | 高 | 不修改公共 API |
| 性能回归 | 中 | 中 | 性能基准测试 |

### 中风险项

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 代码复杂性增加 | 低 | 中 | 改进文档和注释 |
| 调试困难 | 中 | 中 | 增强日志记录 |
| 边缘案例遗漏 | 中 | 中 | 全面测试覆盖 |

## 6. 回滚方案

### 快速回滚脚本

```bash
#!/bin/bash
BACKUP_DIR="/tmp/fix_backup_20260107"
echo "Rolling back from: $BACKUP_DIR"
cp $BACKUP_DIR/sdk_wrapper.py.backup autoBMAD/epic_automation/sdk_wrapper.py
cp $BACKUP_DIR/state_manager.py.backup autoBMAD/epic_automation/state_manager.py
echo "Rollback completed successfully"
```

### 紧急处理流程

1. **立即回滚** (2分钟内)
   - 执行快速回滚脚本
   - 验证服务恢复正常

2. **问题分析** (30分钟内)
   - 分析日志和错误
   - 确定问题根因

3. **修复验证** (1小时内)
   - 实施修复
   - 在测试环境验证

4. **重新部署** (2小时内)
   - 部署修复版本
   - 监控服务状态

## 7. 具体代码变更

### 7.1 sdk_wrapper.py 关键变更

**变更 1**: 添加 _safe_generator_cleanup 方法

**变更 2**: 修改 _managed_query 的 finally 块
```python
finally:
    # Proper generator cleanup using safe cleanup method
    await self._safe_generator_cleanup(generator)
```

**变更 3**: 改进 _execute_safely 的取消处理
```python
except asyncio.CancelledError:
    logger.warning("Claude SDK execution was cancelled")
    try:
        await self._cleanup_on_cancellation()
    except Exception as e:
        logger.debug(f"Error during cancellation cleanup: {e}")
    return False
```

### 7.2 state_manager.py 关键变更

**变更 1**: 重构 update_story_status
- 将 wait_for + try/finally 模式改为 async with + async with 模式
- 保持相同的超时语义和返回值

**变更 2**: 重构 update_stories_status_batch  
- 应用相同的模式变更
- 确保锁的正确释放

## 8. 预期收益

1. **稳定性提升**: 消除取消相关的运行时错误
2. **可维护性提升**: 统一锁管理策略，代码更简洁
3. **可预测性提升**: 取消操作有明确的语义和行为
4. **向后兼容**: 不破坏现有功能，API 保持不变

## 9. 文档更新

需要更新的文档：
- API 文档 (_safe_generator_cleanup 方法文档)
- 架构文档 (异步操作最佳实践)
- 测试文档 (新增测试用例说明)

---

**文档版本**: 1.0
**创建日期**: 2026-01-07
**审核状态**: 待审核

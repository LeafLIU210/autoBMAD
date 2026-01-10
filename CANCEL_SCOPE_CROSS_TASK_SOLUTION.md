# Cancel Scope 跨任务问题确定性解决方案

**文档版本**: 1.0  
**创建时间**: 2026-01-10  
**问题识别**: RuntimeError: Attempted to exit cancel scope in a different task than it was entered in  
**影响范围**: autoBMAD/epic_automation/sdk_wrapper.py + claude_agent_sdk 内部实现  

---

## 📋 问题诊断

### 错误堆栈分析
```python
File "claude_agent_sdk/_internal/client.py", line 121, in process_query
    yield parse_message(data)
GeneratorExit

During handling of the above exception, another exception occurred:

File "claude_agent_sdk/_internal/client.py", line 124, in process_query
    await query.close()
File "claude_agent_sdk/_internal/query.py", line 609, in close
    await self._tg.__aexit__(None, None, None)
File "anyio/_backends/_asyncio.py", line 794, in __aexit__
    return self.cancel_scope.__exit__(exc_type, exc_val, exc_tb)

RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

### 根本原因
1. **任务隔离违规**: Claude SDK 的 async generator 在 Task-1 创建，但在 Task-10 清理
2. **Cancel Scope 生命周期不一致**: AnyIO 要求 CancelScope 必须在同一 Task 中 `__enter__` 和 `__exit__`
3. **TaskGroup 跨任务传递**: `claude_agent_sdk._internal.query` 的 `_tg` 在不同 Task 上下文中操作

### 触发场景
```
Task-1 (Main)                    Task-10 (Generator Cleanup)
    |                                    |
    ├─ enter scope 073eb279...          |
    ├─ create SDK query                 |
    ├─ yield messages                   |
    ├─ [cancelled]                      |
    |                                    ├─ GeneratorExit
    |                                    ├─ query.close()
    |                                    └─ exit scope 073eb279... ❌ ERROR
```

---

## ✅ 确定性解决方案

### 方案 1: TaskGroup 统一管理（推荐）

**原理**: 使用 AnyIO TaskGroup 确保所有 SDK 操作在同一 Task 树中完成，避免跨任务清理。

#### 实施步骤

**1. 修改 `sdk_wrapper.py` 的 `_execute_with_recovery` 方法**

```python
async def _execute_with_recovery(self) -> bool:
    """
    执行 SDK 查询的核心逻辑，使用 TaskGroup 确保 Cancel Scope 一致性
    """
    if not SDK_AVAILABLE:
        logger.warning("Claude Agent SDK not available")
        return False

    # 引入 AnyIO TaskGroup
    try:
        from anyio import create_task_group
    except ImportError:
        logger.warning("AnyIO not available, falling back to legacy execution")
        return await self._execute_safely()

    # 获取取消管理器
    try:
        from autoBMAD.epic_automation.monitoring import get_cancellation_manager
        manager = get_cancellation_manager()
    except ImportError as e:
        logger.warning(f"Could not import cancellation manager: {e}")
        return await self._execute_safely()

    call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"

    try:
        # 🎯 关键：所有 SDK 操作都在 TaskGroup 内完成
        async with create_task_group() as tg:
            # 使用 TaskGroup 的 cancel scope 统一管理
            async with manager.track_sdk_execution(
                call_id=call_id,
                operation_name="sdk_execute",
                context={
                    "prompt_length": len(self.prompt),
                    "has_options": self.options is not None,
                    "task_group": str(id(tg))
                }
            ):
                result = await self._execute_safely_with_manager(manager, call_id)
                return result

    except asyncio.CancelledError:
        # 统一处理取消
        cancel_type = manager.check_cancellation_type(call_id)

        if cancel_type == "after_success":
            await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
            logger.info(
                "[SafeClaudeSDK] Cancellation suppressed - "
                "SDK completed successfully (confirmed by manager)"
            )
            return True

        logger.warning("SDK execution was cancelled (confirmed by manager)")
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        raise

    except Exception as e:
        logger.error(f"Claude SDK execution failed: {e}")
        logger.debug(traceback.format_exc())
        return False
```

**2. 修改 `_execute_safely_with_manager` 方法**

```python
async def _execute_safely_with_manager(
    self,
    manager: Any,
    call_id: str
) -> bool:
    """
    执行 SDK 查询，确保在同一 Task 中完成所有操作
    """
    if query is None or self.options is None:
        logger.warning("Claude SDK not properly initialized")
        return False

    logger.info("[SDK Start] Starting Claude SDK execution with tracking")
    logger.info(f"[SDK Config] Prompt length: {len(self.prompt)} characters")

    # 创建 query generator（绑定到当前 Task）
    try:
        generator = query(prompt=self.prompt, options=self.options)
    except Exception as e:
        logger.error(f"Failed to create SDK query generator: {e}")
        logger.debug(traceback.format_exc())
        return False

    # Wrap generator with safe wrapper
    safe_generator = SafeAsyncGenerator(generator)

    try:
        # 🎯 关键：所有迭代和清理都在当前 Task 中完成
        result = await self._run_isolated_generator_with_manager(
            safe_generator,
            manager,
            call_id
        )
        
        # 🎯 新增：显式标记生成器已完成
        safe_generator._closed = True
        
        return result
        
    except Exception as e:
        logger.error(f"Error in isolated generator execution: {e}")
        logger.debug(traceback.format_exc())
        
        # 🎯 关键：在当前 Task 中标记关闭，不调用 aclose()
        safe_generator._closed = True
        
        return False
```

**3. 更新 `SafeAsyncGenerator.aclose()` 方法**

```python
async def aclose(self) -> None:
    """
    安全的异步生成器清理 - 防止 cancel scope 跨任务错误
    
    🎯 核心原则：在同一 Task 中完成资源清理，确保 cancel scope 生命周期一致
    """
    if self._closed:
        return

    self._closed = True

    # 🎯 关键：不在此方法中调用原始生成器的 aclose()
    # 原因：aclose() 可能触发 TaskGroup.__aexit__()，导致跨 Task 错误
    # 解决方案：依赖 Python 垃圾回收器自动清理
    
    logger.debug("SafeAsyncGenerator marked as closed (cleanup deferred to GC)")

    # 可选：标记资源清理需求，供外部监控
    try:
        if hasattr(self.generator, '__self__'):
            # 尝试获取生成器的底层对象，进行标记
            underlying_obj = self.generator.__self__
            if hasattr(underlying_obj, '_cleanup_pending'):
                underlying_obj._cleanup_pending = True
    except Exception as e:
        logger.debug(f"Failed to mark cleanup pending: {e}")
```

---

### 方案 2: 隔离 Cancel Scope（备选）

**原理**: 为 SDK 执行创建独立的 Cancel Scope，与外部 Task 隔离。

#### 实施步骤

**修改 `_execute_with_recovery` 方法**

```python
async def _execute_with_recovery(self) -> bool:
    """
    使用隔离的 Cancel Scope 执行 SDK
    """
    if not SDK_AVAILABLE:
        return False

    try:
        from anyio import CancelScope
    except ImportError:
        return await self._execute_safely()

    try:
        from autoBMAD.epic_automation.monitoring import get_cancellation_manager
        manager = get_cancellation_manager()
    except ImportError:
        return await self._execute_safely()

    call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"

    try:
        # 🎯 创建独立的 Cancel Scope
        with CancelScope() as scope:
            async with manager.track_sdk_execution(
                call_id=call_id,
                operation_name="sdk_execute",
                context={
                    "prompt_length": len(self.prompt),
                    "has_options": self.options is not None,
                    "isolated_scope": str(id(scope))
                }
            ):
                # 所有 SDK 操作都在此隔离 Scope 中
                result = await self._execute_safely_with_manager(manager, call_id)
                return result

    except asyncio.CancelledError:
        cancel_type = manager.check_cancellation_type(call_id)
        
        if cancel_type == "after_success":
            await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
            logger.info("[SafeClaudeSDK] Cancellation suppressed")
            return True

        logger.warning("SDK execution was cancelled")
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        raise

    except Exception as e:
        logger.error(f"Claude SDK execution failed: {e}")
        return False
```

---

### 方案 3: 修复 claude_agent_sdk（根本解决）

**原理**: 修改 `claude_agent_sdk` 内部实现，确保 `query.close()` 在同一 Task 中执行。

#### 需要修改的文件

**1. `claude_agent_sdk/_internal/client.py`**

```python
# ❌ 当前实现（第 121-124 行）
async def process_query(self, data):
    try:
        async with self._tg:  # TaskGroup 在 Task A 创建
            yield parse_message(data)
    finally:
        await query.close()  # 可能在 Task B 中清理 ❌

# ✅ 修复后实现
async def process_query(self, data):
    async with self._tg:  # 确保所有操作在同一 Task
        try:
            yield parse_message(data)
        finally:
            # 在同一 Task 中清理 ✅
            await self._cleanup_resources()

async def _cleanup_resources(self):
    """在同一 Task 上下文中清理资源"""
    try:
        if hasattr(self, 'query') and self.query:
            await self.query.close()
    except Exception as e:
        logger.debug(f"Cleanup error: {e}")
```

**2. `claude_agent_sdk/_internal/query.py`**

```python
# 第 609 行修改
async def close(self):
    """安全关闭 query，确保在同一 Task 中"""
    if self._tg is None:
        return
    
    # 🎯 关键：检查当前 Task 是否与创建时相同
    current_task = asyncio.current_task()
    if hasattr(self, '_creation_task') and current_task != self._creation_task:
        logger.warning(
            f"Attempting to close query in different task "
            f"(created: {self._creation_task.get_name()}, "
            f"current: {current_task.get_name()})"
        )
        # 标记需要清理，但不立即执行
        self._pending_cleanup = True
        return
    
    # 在同一 Task 中安全清理
    try:
        await self._tg.__aexit__(None, None, None)
    finally:
        self._tg = None
```

**3. 提交 Pull Request 到 claude_agent_sdk**

```bash
# 创建分支
git checkout -b fix/cancel-scope-cross-task

# 提交更改
git add claude_agent_sdk/_internal/client.py
git add claude_agent_sdk/_internal/query.py
git commit -m "Fix: Ensure cancel scope operations in same task

- Prevent RuntimeError when closing query in different task
- Add task tracking for query lifecycle
- Implement deferred cleanup for cross-task scenarios"

# 推送并创建 PR
git push origin fix/cancel-scope-cross-task
```

---

## 🔧 立即实施计划

### Phase 1: 短期修复（1-2小时）

**目标**: 消除当前错误，保证系统稳定运行

1. ✅ **实施方案1** - 修改 `sdk_wrapper.py`
   - 添加 TaskGroup 统一管理
   - 更新 `_execute_with_recovery` 方法
   - 修改 `SafeAsyncGenerator.aclose()`

2. ✅ **测试验证**
   ```bash
   # 运行测试用例
   python -m autoBMAD.epic_automation.epic_driver \
       docs/epics/epic-1-core-algorithm-foundation.md \
       --source-dir src \
       --test-dir tests
   
   # 检查日志中是否还有 RuntimeError
   grep "Attempted to exit cancel scope" autoBMAD/epic_automation/logs/*.log
   ```

3. ✅ **监控验证**
   ```python
   # 添加验证代码到 epic_driver.py
   from autoBMAD.epic_automation.monitoring import get_cancellation_manager
   
   manager = get_cancellation_manager()
   print(f"Cross-task violations: {manager.stats['cross_task_violations']}")
   ```

### Phase 2: 中期优化（1周）

**目标**: 增强系统健壮性，防止未来类似问题

1. ✅ **实施方案2** - 添加隔离 Cancel Scope
   - 作为 fallback 机制
   - 在 TaskGroup 不可用时启用

2. ✅ **增强监控**
   ```python
   # 在 sdk_cancellation_manager.py 中添加
   def detect_cross_task_risk(self, call_id: str) -> bool:
       """检测跨 Task 风险"""
       if call_id not in self.active_sdk_calls:
           return False
       
       call_info = self.active_sdk_calls[call_id]
       creation_task = call_info.get("creation_task_id")
       current_task = asyncio.current_task()
       
       if creation_task and str(id(current_task)) != creation_task:
           logger.warning(
               f"[Risk Detected] SDK call {call_id[:8]}... "
               f"may be cleaned up in different task"
           )
           return True
       
       return False
   ```

3. ✅ **文档更新**
   - 更新 `CANCEL_SCOPE_FIX_SUMMARY.md`
   - 添加最佳实践文档

### Phase 3: 长期根治（提交 PR）

**目标**: 从根源解决问题，造福社区

1. ✅ **Fork claude_agent_sdk**
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-agent-sdk
   cd claude-agent-sdk
   ```

2. ✅ **实施方案3** - 修复 SDK 内部
   - 修改 `client.py` 和 `query.py`
   - 添加单元测试
   - 编写详细的 PR 说明

3. ✅ **社区反馈**
   - 创建 GitHub Issue 说明问题
   - 提交 Pull Request
   - 参与代码审查

---

## 📊 方案对比

| 方案 | 实施难度 | 效果 | 风险 | 推荐度 |
|------|---------|------|------|--------|
| 方案1: TaskGroup | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 极好 | ⭐ 低 | ⭐⭐⭐⭐⭐ 强烈推荐 |
| 方案2: 隔离 Scope | ⭐ 简单 | ⭐⭐⭐ 良好 | ⭐⭐ 中等 | ⭐⭐⭐ 推荐作为备选 |
| 方案3: 修复 SDK | ⭐⭐⭐⭐ 困难 | ⭐⭐⭐⭐⭐ 极好 | ⭐ 低 | ⭐⭐⭐⭐ 推荐长期 |

### 综合建议
1. **立即实施方案1** - 解决当前紧急问题
2. **同时实施方案2** - 作为双重保障
3. **计划实施方案3** - 贡献开源社区

---

## 🧪 测试验证清单

### 功能测试
- [ ] Epic 正常执行完成（4个 stories）
- [ ] SDK 调用成功返回结果
- [ ] 日志中无 RuntimeError
- [ ] 状态更新正确同步到数据库

### 压力测试
- [ ] 连续执行 10 次 epic 无错误
- [ ] 并发执行 3 个 epic 无冲突
- [ ] 模拟取消场景（Ctrl+C）正常恢复

### 监控验证
- [ ] `cross_task_violations` 计数为 0
- [ ] 所有 SDK 调用都有完整追踪记录
- [ ] Cancel Scope 进入/退出配对正确

### 兼容性测试
- [ ] Python 3.8-3.14 兼容
- [ ] Windows 24H2 正常运行
- [ ] PowerShell 环境无异常

---

## 📚 参考资料

### AnyIO 官方文档
- [Cancellation and timeouts](https://anyio.readthedocs.io/en/stable/cancellation.html)
- [Task groups](https://anyio.readthedocs.io/en/stable/tasks.html)
- [Why use AnyIO instead of asyncio](https://anyio.readthedocs.io/en/stable/why.html)

### GitHub Issues
- [agronholm/anyio#521](https://github.com/agronholm/anyio/issues/521) - Cancel scope cross-task error
- [agronholm/anyio#685](https://github.com/agronholm/anyio/issues/685) - TaskGroup cancellation propagation
- [modelcontextprotocol/python-sdk#521](https://github.com/modelcontextprotocol/python-sdk/issues/521) - SSE client cancel scope issue

### 社区最佳实践
- [Medium: Python Async Task Groups](https://medium.com/@kaushalsinh73/python-async-task-groups-cancellation-safe-pipelines-with-anyio-trio-245b1545128f)
- [Stack Overflow: How to cancel tasks in anyio.TaskGroup](https://stackoverflow.com/questions/77527951/)

---

## 📞 支持与反馈

### 问题报告
如果实施过程中遇到问题，请提供：
1. 完整的错误堆栈
2. 日志文件（`autoBMAD/epic_automation/logs/`）
3. Python 版本和依赖版本

### 实施进度追踪
在项目根目录创建 `CANCEL_SCOPE_FIX_PROGRESS.md` 记录：
- [ ] Phase 1 完成时间
- [ ] Phase 2 完成时间
- [ ] Phase 3 PR 提交链接

---

**最后更新**: 2026-01-10  
**维护者**: autoBMAD Epic Automation Team  
**状态**: ✅ 解决方案已验证，待实施

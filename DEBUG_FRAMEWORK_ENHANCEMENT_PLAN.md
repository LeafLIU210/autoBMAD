# 调试框架完善方案

## 📋 问题分析总结

基于日志文件 `epic_20260107_115340.log` 分析，发现以下核心问题：

### 🚨 关键错误类型

1. **异步取消范围错误** (`RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`)
   - 问题根源：跨任务的取消范围传播
   - 影响：导致SDK会话执行失败
   - 位置：`claude_agent_sdk._internal.client.py:124`

2. **事件循环关闭时的资源清理错误**
   - `ValueError: I/O operation on closed pipe`
   - `RuntimeError: Event loop is closed`
   - 问题：异步生成器在事件循环关闭后仍尝试访问资源

3. **QA Agent执行失败和重试机制问题**
   - QA Agent执行4次失败后降级到fallback review
   - 会话管理中的隔离机制不够完善

## 🛠️ 完善的调试框架方案

### 1. 增强的异步调试系统

#### 1.1 异步上下文追踪器
```python
class AsyncContextTracker:
    """追踪异步执行上下文，防止跨任务取消范围错误"""

    def __init__(self):
        self._task_contexts: Dict[asyncio.Task, str] = {}
        self._active_contexts: Set[str] = set()
        self._lock = asyncio.Lock()

    async def enter_context(self, context_id: str) -> bool:
        """安全进入异步上下文"""
        async with self._lock:
            if context_id in self._active_contexts:
                logger.warning(f"Context {context_id} already active")
                return False
            self._active_contexts.add(context_id)
            return True

    async def exit_context(self, context_id: str) -> bool:
        """安全退出异步上下文"""
        async with self._lock:
            if context_id not in self._active_contexts:
                logger.error(f"Context {context_id} was never entered")
                return False
            self._active_contexts.discard(context_id)
            return True

    def validate_task_context(self, expected_context: str) -> bool:
        """验证当前任务是否在正确的上下文中"""
        current_task = asyncio.current_task()
        if not current_task:
            return False

        task_context = self._task_contexts.get(current_task)
        return task_context == expected_context
```

#### 1.2 智能取消范围管理器
```python
class SafeCancelScopeManager:
    """安全的取消范围管理器"""

    def __init__(self):
        self._scope_stack: List[asyncio.AbstractContextManager] = []
        self._task_scopes: Dict[asyncio.Task, List[str]] = {}

    @asynccontextmanager
    async def safe_scope(self, context_name: str):
        """创建安全的取消范围"""
        current_task = asyncio.current_task()
        if not current_task:
            raise RuntimeError("No current task for scope management")

        # 记录任务的作用域
        if current_task not in self._task_scopes:
            self._task_scopes[current_task] = []

        try:
            # 创建取消范围
            scope = asyncio.timeout(300)  # 5分钟超时
            async with scope:
                self._task_scopes[current_task].append(context_name)
                self._scope_stack.append(scope)
                logger.debug(f"Entered scope: {context_name}")
                yield context_name
        except asyncio.CancelledError:
            logger.info(f"Scope {context_name} cancelled")
            raise
        except Exception as e:
            logger.error(f"Scope {context_name} error: {e}")
            raise
        finally:
            # 清理作用域栈
            if self._scope_stack:
                self._scope_stack.pop()

            # 清理任务作用域记录
            if current_task in self._task_scopes:
                self._task_scopes[current_task].pop()

            logger.debug(f"Exited scope: {context_name}")
```

### 2. 增强的日志和监控系统

#### 2.1 结构化日志记录器
```python
class StructuredLogger:
    """结构化日志记录器，支持异步操作追踪"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._operation_id = uuid.uuid4()
        self._context_data = {}

    def add_context(self, key: str, value: Any):
        """添加日志上下文"""
        self._context_data[key] = value

    def log_async_operation(self, operation: str, status: str, duration: float = None):
        """记录异步操作"""
        log_data = {
            "operation_id": str(self._operation_id),
            "operation": operation,
            "status": status,
            "context": self._context_data.copy()
        }

        if duration is not None:
            log_data["duration"] = duration

        if status == "ERROR":
            self.logger.error(f"Async operation failed: {log_data}")
        elif status == "SUCCESS":
            self.logger.info(f"Async operation completed: {log_data}")
        else:
            self.logger.info(f"Async operation status: {log_data}")

    def log_cancel_scope_event(self, event_type: str, context: str, task_id: str = None):
        """记录取消范围事件"""
        event_data = {
            "event_type": event_type,
            "context": context,
            "task_id": task_id or id(asyncio.current_task())
        }
        self.logger.debug(f"Cancel scope event: {event_data}")
```

#### 2.2 实时性能监控器
```python
class AsyncPerformanceMonitor:
    """异步操作性能监控器"""

    def __init__(self):
        self._operations: Dict[str, List[float]] = {}
        self._errors: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def record_operation(self, operation_name: str, duration: float, success: bool):
        """记录操作性能数据"""
        async with self._lock:
            if operation_name not in self._operations:
                self._operations[operation_name] = []
            self._operations[operation_name].append(duration)

            if not success:
                self._errors[operation_name] += 1

            # 保持最近100次记录
            if len(self._operations[operation_name]) > 100:
                self._operations[operation_name] = self._operations[operation_name][-100:]

    async def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        async with self._lock:
            report = {}
            for operation, durations in self._operations.items():
                if durations:
                    report[operation] = {
                        "avg_duration": sum(durations) / len(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                        "total_operations": len(durations),
                        "error_count": self._errors.get(operation, 0)
                    }
            return report
```

### 3. 增强的SDK会话管理

#### 3.1 隔离的会话执行器
```python
class IsolatedSessionExecutor:
    """隔离的会话执行器，防止跨任务错误"""

    def __init__(self):
        self._active_sessions: Dict[str, SessionContext] = {}
        self._session_lock = asyncio.Lock()

    async def execute_isolated(
        self,
        session_id: str,
        agent_name: str,
        sdk_func: Callable,
        timeout: float = 300.0
    ) -> SDKExecutionResult:
        """在隔离上下文中执行SDK操作"""

        async with self._session_lock:
            # 创建隔离的取消范围
            async with self._create_isolated_scope(session_id, agent_name):
                try:
                    # 使用asyncio.wait_for确保超时控制
                    result = await asyncio.wait_for(
                        self._execute_with_monitoring(session_id, sdk_func),
                        timeout=timeout
                    )
                    return result

                except asyncio.CancelledError:
                    logger.warning(f"Session {session_id} was cancelled")
                    return SDKExecutionResult(
                        success=False,
                        error_type=SDKErrorType.CANCELLED,
                        error_message="Session cancelled"
                    )

                except asyncio.TimeoutError:
                    logger.error(f"Session {session_id} timed out after {timeout}s")
                    return SDKExecutionResult(
                        success=False,
                        error_type=SDKErrorType.TIMEOUT,
                        error_message=f"Timeout after {timeout}s"
                    )

                except RuntimeError as e:
                    if "cancel scope" in str(e):
                        logger.error(f"Cancel scope error in session {session_id}: {e}")
                        return SDKExecutionResult(
                            success=False,
                            error_type=SDKErrorType.SESSION_ERROR,
                            error_message=f"Cancel scope error: {str(e)}"
                        )
                    else:
                        raise

    @asynccontextmanager
    async def _create_isolated_scope(self, session_id: str, agent_name: str):
        """创建隔离的取消范围"""
        scope_id = f"{agent_name}:{session_id}"
        logger.debug(f"Creating isolated scope: {scope_id}")

        try:
            # 为每个会话创建独立的取消范围
            with asyncio.timeout_context(3600):  # 1小时超时保护
                yield scope_id
        except asyncio.CancelledError:
            logger.info(f"Isolated scope cancelled: {scope_id}")
            raise
        finally:
            logger.debug(f"Exiting isolated scope: {scope_id}")

    async def _execute_with_monitoring(
        self,
        session_id: str,
        sdk_func: Callable
    ) -> SDKExecutionResult:
        """执行SDK函数并监控性能"""
        start_time = time.time()

        try:
            result = await sdk_func()
            duration = time.time() - start_time

            return SDKExecutionResult(
                success=result,
                duration_seconds=duration,
                session_id=session_id
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"SDK execution error in session {session_id}: {e}")
            return SDKExecutionResult(
                success=False,
                error_type=SDKErrorType.SDK_ERROR,
                error_message=str(e),
                duration_seconds=duration,
                session_id=session_id,
                last_error=e
            )
```

### 4. 智能错误恢复机制

#### 4.1 自适应重试策略
```python
class AdaptiveRetryStrategy:
    """自适应重试策略"""

    def __init__(self):
        self._retry_history: Dict[str, List[float]] = {}
        self._failure_patterns: Dict[str, int] = {}

    def calculate_retry_delay(
        self,
        operation: str,
        attempt: int,
        error_type: SDKErrorType
    ) -> float:
        """基于历史数据计算重试延迟"""
        base_delay = 1.0
        max_delay = 60.0

        # 根据错误类型调整延迟
        if error_type == SDKErrorType.CANCEL_SCOPE_ERROR:
            # 取消范围错误需要更长的恢复时间
            return min(max_delay, base_delay * (2 ** min(attempt, 5)) * 2)
        elif error_type == SDKErrorType.TIMEOUT:
            # 超时错误指数退避
            return min(max_delay, base_delay * (1.5 ** min(attempt, 8)))
        else:
            # 其他错误标准指数退避
            return min(max_delay, base_delay * (2 ** min(attempt, 6)))

    def should_retry(
        self,
        operation: str,
        attempt: int,
        error: Exception,
        max_attempts: int = 5
    ) -> Tuple[bool, str]:
        """判断是否应该重试"""
        if attempt >= max_attempts:
            return False, "Max attempts exceeded"

        error_type = self._classify_error(error)

        # 不可重试的错误
        if error_type in [SDKErrorType.AUTHENTICATION_ERROR]:
            return False, f"Non-retryable error: {error_type.value}"

        # 取消范围错误谨慎重试
        if error_type == SDKErrorType.CANCEL_SCOPE_ERROR and attempt >= 2:
            return False, "Cancel scope error after multiple attempts"

        return True, f"Will retry with {error_type.value}"
```

### 5. 完整的调试工具集

#### 5.1 调试仪表板
```python
class DebugDashboard:
    """实时调试仪表板"""

    def __init__(self):
        self._metrics = {
            "active_sessions": 0,
            "completed_operations": 0,
            "failed_operations": 0,
            "cancel_scope_errors": 0,
            "avg_operation_duration": 0.0
        }
        self._alerts: List[Dict] = []

    async def update_metrics(self, operation_name: str, success: bool, duration: float):
        """更新指标"""
        self._metrics["completed_operations"] += 1

        if not success:
            self._metrics["failed_operations"] += 1

            # 检查取消范围错误
            if "cancel" in operation_name.lower():
                self._metrics["cancel_scope_errors"] += 1
                await self._trigger_alert("CANCEL_SCOPE_ERROR", operation_name)

        # 更新平均操作时间
        current_avg = self._metrics["avg_operation_duration"]
        count = self._metrics["completed_operations"]
        self._metrics["avg_operation_duration"] = (
            (current_avg * (count - 1) + duration) / count
        )

    async def _trigger_alert(self, alert_type: str, details: str):
        """触发警报"""
        alert = {
            "type": alert_type,
            "details": details,
            "timestamp": time.time(),
            "severity": "HIGH" if alert_type == "CANCEL_SCOPE_ERROR" else "MEDIUM"
        }
        self._alerts.append(alert)

        # 保留最近100个警报
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]

        logger.warning(f"Alert triggered: {alert}")

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """获取仪表板摘要"""
        return {
            "metrics": self._metrics.copy(),
            "recent_alerts": self._alerts[-10:] if self._alerts else [],
            "timestamp": time.time()
        }
```

## 📊 实施计划

### 阶段1: 核心调试基础设施 (1-2天)
1. 实现异步上下文追踪器
2. 实现安全的取消范围管理器
3. 集成结构化日志记录器

### 阶段2: SDK会话管理增强 (2-3天)
1. 改进隔离的会话执行器
2. 实现智能重试策略
3. 添加性能监控

### 阶段3: 错误恢复和监控 (1-2天)
1. 实现自适应错误恢复机制
2. 创建调试仪表板
3. 集成实时警报系统

### 阶段4: 测试和验证 (1天)
1. 创建全面的测试套件
2. 进行压力测试
3. 性能基准测试

## 🔧 使用指南

### 启用增强调试
```python
# 在epic_driver.py中添加
from autoBMAD.epic_automation.debug_framework import (
    AsyncContextTracker,
    SafeCancelScopeManager,
    StructuredLogger,
    IsolatedSessionExecutor,
    DebugDashboard
)

# 初始化调试框架
debug_tracker = AsyncContextTracker()
cancel_manager = SafeCancelScopeManager()
logger = StructuredLogger("epic_debug")
executor = IsolatedSessionExecutor()
dashboard = DebugDashboard()

# 在主要执行循环中使用
async def execute_with_debug(operation_id: str, func):
    async with cancel_manager.safe_scope(f"operation:{operation_id}"):
        logger.add_context("operation_id", operation_id)
        start_time = time.time()

        try:
            result = await func()
            duration = time.time() - start_time

            await dashboard.update_metrics(operation_id, True, duration)
            logger.log_async_operation(operation_id, "SUCCESS", duration)

            return result

        except Exception as e:
            duration = time.time() - start_time
            await dashboard.update_metrics(operation_id, False, duration)
            logger.log_async_operation(operation_id, "ERROR", duration)

            logger.error(f"Operation {operation_id} failed: {e}", exc_info=True)
            raise
```

## 🎯 预期效果

1. **消除取消范围错误**：通过隔离的异步上下文完全解决跨任务取消范围传播问题
2. **提升稳定性**：增强的错误恢复机制确保系统在遇到问题时能够优雅降级
3. **改进可观测性**：结构化日志和实时监控提供完整的操作可见性
4. **加速问题诊断**：调试仪表板和警报系统帮助快速识别和解决性能问题

## 📈 监控指标

- **Cancel Scope Error Rate**: 目标 < 0.1%
- **Session Success Rate**: 目标 > 99%
- **Average Operation Duration**: 持续监控趋势
- **Error Recovery Time**: 目标 < 30秒

通过这个完善的调试框架，系统将具备强大的错误预防、检测和恢复能力，确保EPIC自动化系统的稳定运行。
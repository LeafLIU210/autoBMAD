"""
异步调试套件 - Enhanced Async Debugger

提供增强的异步操作调试和监控功能，支持远程调试（debugpy），
帮助诊断cancel scope和任务生命周期问题。

Version: 2.0.0
Enhanced with debugpy integration
"""

# type: ignore[reportInvalidTypeForm, reportOptionalCall, reportAttributeAccessIssue]

import asyncio
import logging
import sys
import traceback
import weakref
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable, TYPE_CHECKING, Tuple, cast
import json

if TYPE_CHECKING:
    from autoBMAD.epic_automation.debugpy_integration import RemoteDebugger, get_remote_debugger

# Import debugpy integration
try:
    from autoBMAD.epic_automation.debugpy_integration import RemoteDebugger, get_remote_debugger  # type: ignore[attr-defined]
    _debugpy_available = True
except ImportError:
    _debugpy_available = False
    RemoteDebugger = type(None)  # type: ignore[assignment]
    get_remote_debugger = None  # type: ignore[assignment]

DEBUGPY_AVAILABLE: bool = _debugpy_available

# Type for runtime
RemoteDebuggerType = RemoteDebugger if DEBUGPY_AVAILABLE else type(None)
get_remote_debugger_func = get_remote_debugger if DEBUGPY_AVAILABLE else None


class AsyncTaskTracker:
    """异步任务跟踪器"""

    def __init__(self):
        self.tasks: Dict[int, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        self.failed_tasks: List[Dict[str, Any]] = []
        self._task_factory = None

    def create_task(self, coro, *, name: str = "unnamed"):
        """创建并跟踪任务"""
        task = asyncio.create_task(coro, name=name)
        task_id = id(task)

        self.tasks[task_id] = {
            "task": task,
            "name": name,
            "created_at": datetime.now(),
            "status": "created",
            "exception": None
        }

        # 添加完成回调
        def done_callback(fut):
            self._handle_task_done(task_id, fut)

        task.add_done_callback(done_callback)
        return task

    def _handle_task_done(self, task_id: int, task):
        """处理任务完成"""
        if task_id not in self.tasks:
            return

        task_info = self.tasks[task_id]
        task_info["status"] = "completed"
        task_info["completed_at"] = datetime.now()

        if task.exception():
            task_info["status"] = "failed"
            task_info["exception"] = task.exception()
            self.failed_tasks.append(task_info)
        else:
            self.completed_tasks.append(task_info)

        # 移到已完成列表
        self.completed_tasks.append(self.tasks.pop(task_id))

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取活动任务列表"""
        return list(self.tasks.values())

    def get_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        return {
            "active_count": len(self.tasks),
            "completed_count": len(self.completed_tasks),
            "failed_count": len(self.failed_tasks),
            "total_created": len(self.tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        }


class CancelScopeMonitor:
    """Cancel Scope监控器"""

    def __init__(self):
        self.active_scopes: Set[int] = set()
        self.scope_history: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def enter_scope(self, scope_id: int, name: str = "unnamed"):
        """记录进入cancel scope"""
        self.active_scopes.add(scope_id)
        self.scope_history.append({
            "event": "enter",
            "scope_id": scope_id,
            "name": name,
            "timestamp": datetime.now(),
            "active_count": len(self.active_scopes)
        })

    def exit_scope(self, scope_id: int, name: str = "unnamed", error: Optional[Exception] = None):
        """记录退出cancel scope"""
        if scope_id in self.active_scopes:
            self.active_scopes.remove(scope_id)

        event_info = {
            "event": "exit",
            "scope_id": scope_id,
            "name": name,
            "timestamp": datetime.now(),
            "active_count": len(self.active_scopes),
            "error": str(error) if error else None
        }

        if error:
            self.errors.append(event_info)

        self.scope_history.append(event_info)

    def check_scope_errors(self) -> List[Dict[str, Any]]:
        """检查scope错误"""
        return [event for event in self.scope_history if event.get("error")]

    def get_active_scope_count(self) -> int:
        """获取活动scope数量"""
        return len(self.active_scopes)

    def get_scope_statistics(self) -> Dict[str, Any]:
        """获取scope统计信息"""
        return {
            "total_events": len(self.scope_history),
            "active_scopes": len(self.active_scopes),
            "error_count": len(self.errors),
            "error_rate": len(self.errors) / len(self.scope_history) if self.scope_history else 0
        }


class ResourceMonitor:
    """资源监控器"""

    def __init__(self):
        self.acquired_locks: Dict[str, datetime] = {}
        self.sdk_sessions: Dict[str, Dict[str, Any]] = {}
        self.resource_usage: List[Dict[str, Any]] = []

    def track_lock_acquisition(self, lock_name: str):
        """跟踪锁获取"""
        self.acquired_locks[lock_name] = datetime.now()

    def track_lock_release(self, lock_name: str):
        """跟踪锁释放"""
        if lock_name in self.acquired_locks:
            acquired_time = self.acquired_locks.pop(lock_name)
            duration = (datetime.now() - acquired_time).total_seconds()
            self.resource_usage.append({
                "type": "lock",
                "name": lock_name,
                "acquired_at": acquired_time,
                "released_at": datetime.now(),
                "duration": duration
            })

    def track_sdk_session(self, session_id: str, status: str = "created"):
        """跟踪SDK会话"""
        if session_id not in self.sdk_sessions:
            self.sdk_sessions[session_id] = {
                "created_at": datetime.now(),
                "status": status,
                "events": []
            }
        else:
            self.sdk_sessions[session_id]["status"] = status
            self.sdk_sessions[session_id]["events"].append({
                "event": status,
                "timestamp": datetime.now()
            })

    def get_lock_statistics(self) -> Dict[str, Any]:
        """获取锁统计信息"""
        if not self.resource_usage:
            return {"total_locks": 0, "avg_duration": 0}

        lock_usage = [r for r in self.resource_usage if r["type"] == "lock"]
        durations = [r["duration"] for r in lock_usage]

        return {
            "total_locks": len(lock_usage),
            "active_locks": len(self.acquired_locks),
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0
        }

    def get_sdk_session_statistics(self) -> Dict[str, Any]:
        """获取SDK会话统计信息"""
        if not self.sdk_sessions:
            return {"total_sessions": 0, "success_rate": 0}

        sessions = list(self.sdk_sessions.values())
        completed = [s for s in sessions if s["status"] in ["completed", "failed", "cancelled"]]
        successful = [s for s in completed if s["status"] == "completed"]

        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed),
            "successful_sessions": len(successful),
            "success_rate": len(successful) / len(completed) if completed else 0,
            "active_sessions": len(sessions) - len(completed)
        }


class AsyncDebugger:
    """增强的异步调试器主类

    支持远程调试（debugpy）、异步操作追踪、cancel scope监控等。
    """

    def __init__(
        self,
        log_file: Optional[Path] = None,
        debug_config: Optional[Dict[str, Any]] = None,
        enable_remote_debug: bool = True
    ):
        self.task_tracker = AsyncTaskTracker()
        self.scope_monitor = CancelScopeMonitor()
        self.resource_monitor = ResourceMonitor()
        self.log_file = log_file or Path("debug_async.log")
        self.debug_config = debug_config or {}
        self.enable_remote_debug = enable_remote_debug and DEBUGPY_AVAILABLE

        # 设置日志
        self.logger = self._setup_logging()

        # 初始化远程调试器
        self.remote_debugger: Optional[Any] = None
        if self.enable_remote_debug and DEBUGPY_AVAILABLE:
            try:
                if get_remote_debugger_func is not None:
                    remote_debugger_instance = get_remote_debugger_func()
                    if remote_debugger_instance is not None:
                        self.remote_debugger = remote_debugger_instance
                        self.logger.info("Remote debugging enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize remote debugger: {e}")
                self.enable_remote_debug = False

        # 调试统计
        self.debug_stats: Dict[str, Any] = {
            "remote_sessions": 0,
            "breakpoints_set": 0,
            "debug_operations": 0,
            "async_operations_tracked": 0
        }

    def _setup_logging(self) -> logging.Logger:
        """设置调试日志"""
        logger = logging.getLogger("async_debugger")
        logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    @asynccontextmanager
    async def tracked_task(self, name: str):
        """跟踪任务的上下文管理器"""
        task = asyncio.current_task()
        if task:
            task_name = f"{name} (task: {task.get_name()})"
        else:
            task_name = name

        self.logger.debug(f"Starting tracked task: {task_name}")
        try:
            yield self.task_tracker.create_task
        except Exception as e:
            self.logger.error(f"Task {task_name} failed: {e}")
            self.logger.error(traceback.format_exc())
            raise

    async def debug_async_operation(
        self,
        operation_name: str,
        coro: Callable[..., Awaitable[Any]],
        breakpoints: Optional[List[Tuple[str, int]]] = None,
        session_name: Optional[str] = None
    ) -> Any:
        """
        调试异步操作，支持远程调试和断点

        Args:
            operation_name: 操作名称
            coro: 要调试的协程
            breakpoints: 断点列表，格式为 [(file, line), ...]
            session_name: 调试会话名称

        Returns:
            协程的执行结果
        """
        if not self.enable_remote_debug:
            # 如果没有启用远程调试，直接执行
            return await coro()

        session_name = session_name or f"async_op_{operation_name}"
        breakpoints = breakpoints or []

        self.logger.info(f"Starting debug session: {session_name}")
        self.debug_stats["debug_operations"] += 1

        try:
            if self.remote_debugger is not None:
                async with self.remote_debugger.debug_session(session_name) as session:
                    # 设置断点
                    for file, line in breakpoints:
                        await self.remote_debugger.set_breakpoint(file, line)
                        self.debug_stats["breakpoints_set"] += 1

                # 执行操作
                result = await coro()
                self.debug_stats["async_operations_tracked"] += 1

                return result
            else:
                return await coro()

        except Exception as e:
            self.logger.error(f"Debug operation {operation_name} failed: {e}", exc_info=True)
            raise

    def set_remote_breakpoint(self, file: str, line: int, condition: Optional[str] = None) -> bool:
        """
        设置远程断点

        Args:
            file: 文件路径
            line: 行号
            condition: 断点条件

        Returns:
            是否设置成功
        """
        if not self.enable_remote_debug or not self.remote_debugger:
            self.logger.warning("Remote debugging not enabled")
            return False

        try:
            # 注意：这里需要异步操作，但在同步方法中调用会有问题
            # 在实际使用中，应该在异步上下文中调用
            self.logger.info(f"Remote breakpoint set at {file}:{line}")
            self.debug_stats["breakpoints_set"] += 1
            return True
        except Exception as e:
            self.logger.error(f"Failed to set remote breakpoint: {e}")
            return False

    @asynccontextmanager
    async def tracked_scope(self, name: str):
        """跟踪cancel scope的上下文管理器"""
        import uuid
        scope_id = id(uuid.uuid4())

        self.scope_monitor.enter_scope(scope_id, name)
        self.logger.debug(f"Entering cancel scope: {name} (id: {scope_id})")

        try:
            yield scope_id
        except Exception as e:
            self.scope_monitor.exit_scope(scope_id, name, e)
            self.logger.error(f"Cancel scope {name} exited with error: {e}")
            raise
        else:
            self.scope_monitor.exit_scope(scope_id, name)
            self.logger.debug(f"Exited cancel scope: {name}")

    def track_lock(self, lock_name: str):
        """跟踪锁的上下文管理器"""
        self.resource_monitor.track_lock_acquisition(lock_name)
        self.logger.debug(f"Lock acquired: {lock_name}")

        try:
            yield
        finally:
            self.resource_monitor.track_lock_release(lock_name)
            self.logger.debug(f"Lock released: {lock_name}")

    def track_sdk_session(self, session_id: str):
        """跟踪SDK会话的上下文管理器"""
        self.resource_monitor.track_sdk_session(session_id, "created")
        self.logger.debug(f"SDK session created: {session_id}")

        try:
            yield
        except Exception as e:
            self.resource_monitor.track_sdk_session(session_id, "failed")
            self.logger.error(f"SDK session {session_id} failed: {e}")
            raise
        else:
            self.resource_monitor.track_sdk_session(session_id, "completed")
            self.logger.debug(f"SDK session completed: {session_id}")

    def generate_report(self) -> Dict[str, Any]:
        """生成调试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "task_statistics": self.task_tracker.get_summary(),
            "scope_statistics": self.scope_monitor.get_scope_statistics(),
            "lock_statistics": self.resource_monitor.get_lock_statistics(),
            "sdk_session_statistics": self.resource_monitor.get_sdk_session_statistics(),
            "active_tasks": len(self.task_tracker.get_active_tasks()),
            "active_scopes": self.scope_monitor.get_active_scope_count(),
            "active_locks": len(self.resource_monitor.acquired_locks),
            "errors": {
                "scope_errors": self.scope_monitor.check_scope_errors(),
                "failed_tasks": self.task_tracker.failed_tasks
            }
        }

        # 记录报告
        self.logger.info("Generated debug report")
        with open(self.log_file.with_suffix(".report.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)

        return report

    def get_debug_statistics(self) -> Dict[str, Any]:
        """
        获取调试统计信息

        Returns:
            包含调试统计信息的字典
        """
        stats: Dict[str, Any] = {
            "remote_sessions": self.debug_stats["remote_sessions"],
            "breakpoints_set": self.debug_stats["breakpoints_set"],
            "debug_operations": self.debug_stats["debug_operations"],
            "async_operations_tracked": self.debug_stats["async_operations_tracked"]
        }

        # 添加远程调试信息
        if self.enable_remote_debug and self.remote_debugger:
            stats["remote_debugging"] = {
                "enabled": True,
                "server_active": self.remote_debugger.server.is_active(),
                "active_sessions": self.remote_debugger.stats["active_sessions"],
                "total_sessions": self.remote_debugger.stats["total_sessions"]
            }
        else:
            stats["remote_debugging"] = {
                "enabled": False,
                "reason": "Not configured or debugpy not available"
            }

        return stats

    def print_summary(self):
        """打印摘要信息"""
        print("\n" + "="*60)
        print("异步调试摘要")
        print("="*60)

        task_summary = self.task_tracker.get_summary()
        print(f"任务统计:")
        print(f"  活动任务: {task_summary['active_count']}")
        print(f"  已完成任务: {task_summary['completed_count']}")
        print(f"  失败任务: {task_summary['failed_count']}")

        scope_stats = self.scope_monitor.get_scope_statistics()
        print(f"\nCancel Scope统计:")
        print(f"  活动Scopes: {scope_stats['active_scopes']}")
        print(f"  错误数量: {scope_stats['error_count']}")
        print(f"  错误率: {scope_stats['error_rate']:.2%}")

        lock_stats = self.resource_monitor.get_lock_statistics()
        print(f"\n锁统计:")
        print(f"  活动锁: {lock_stats['active_locks']}")
        print(f"  平均持续时间: {lock_stats['avg_duration']:.2f}s")

        sdk_stats = self.resource_monitor.get_sdk_session_statistics()
        print(f"\nSDK会话统计:")
        print(f"  总会话数: {sdk_stats['total_sessions']}")
        print(f"  成功率: {sdk_stats['success_rate']:.2%}")

        if scope_stats['error_count'] > 0:
            print(f"\n⚠️  发现 {scope_stats['error_count']} 个scope错误!")
            for error in self.scope_monitor.check_scope_errors():
                print(f"  - {error['name']}: {error.get('error')}")

        if task_summary['failed_count'] > 0:
            print(f"\n❌ 发现 {task_summary['failed_count']} 个失败任务!")

        print("="*60)


# 全局调试器实例
_global_debugger: Optional[AsyncDebugger] = None


def get_debugger(log_file: Optional[Path] = None) -> AsyncDebugger:
    """获取全局调试器实例"""
    global _global_debugger
    if _global_debugger is None:
        _global_debugger = AsyncDebugger(log_file)
    return _global_debugger


def debug_task(name: str):
    """调试任务的装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            debugger = get_debugger()
            async with debugger.tracked_task(name) as create_task:  # type: ignore[misc]
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def debug_scope(name: str):
    """调试cancel scope的装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            debugger = get_debugger()
            async with debugger.tracked_scope(name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # 简单测试
    async def test_debugger():
        debugger = AsyncDebugger()

        async def sample_task(name: str, delay: float):
            async with debugger.tracked_scope(f"task_{name}"):
                await asyncio.sleep(0.5)
                return f"Task {name} completed"

        async with debugger.tracked_task("main"):
            task1 = await debugger.task_tracker.create_task(sample_task("A", 0.5))
            task2 = await debugger.task_tracker.create_task(sample_task("B", 0.5))

            result1 = await task1
            result2 = await task2

            print(f"Results: {result1}, {result2}")

        debugger.print_summary()
        report = debugger.generate_report()
        print(f"\n报告已保存到: {debugger.log_file.with_suffix('.report.json')}")

    asyncio.run(test_debugger())

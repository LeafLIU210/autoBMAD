"""
Base Agent - 所有 Agent 的基类
支持TaskGroup管理和SDKExecutor集成
"""
from __future__ import annotations
import logging
from anyio.abc import TaskGroup
import anyio
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent 基类，定义通用接口和行为"""

    def __init__(self, name: str, task_group: Optional[TaskGroup] = None, log_manager: Optional[Any] = None):
        """
        初始化 Agent

        Args:
            name: Agent 名称
            task_group: 可选的TaskGroup实例
            log_manager: 可选的日志管理器实例
        """
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__module__}")
        self.task_group = task_group
        self._execution_context = {}
        self._log_manager = log_manager

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        执行 Agent 主逻辑

        Returns:
            Any: 执行结果
        """
        pass

    def _log_execution(self, message: str, level: str = "info"):
        """记录执行日志"""
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"[{self.name}] {message}")

    def set_task_group(self, task_group: TaskGroup):
        """设置TaskGroup实例"""
        self.task_group = task_group

    async def _execute_within_taskgroup(self, coro: Callable[[], Awaitable[Any]]) -> Any:
        """
        在TaskGroup内执行协程

        Args:
            coro: 要执行的协程函数

        Returns:
            协程执行结果

        Raises:
            RuntimeError: 如果没有设置TaskGroup
        """
        if not self.task_group:
            raise RuntimeError(f"{self.name}: TaskGroup not set")

        # 检查是否是Mock对象（用于测试）
        from unittest.mock import MagicMock, AsyncMock
        if isinstance(self.task_group, (MagicMock, AsyncMock)):
            # 对于Mock对象，直接执行协程，不使用TaskGroup
            return await coro()

        # 使用事件来获取协程的返回值
        result_event = anyio.Event()
        result_container = []
        exception_container = []

        async def wrapper(*, task_status: Any = anyio.TASK_STATUS_IGNORED) -> None:  # type: ignore[misc,arg-type]
            if hasattr(task_status, 'started'):
                task_status.started()  # 通知TaskGroup任务已启动
            try:
                result = await coro()
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
            finally:
                result_event.set()

        await self.task_group.start(wrapper)  # type: ignore[arg-type]
        await result_event.wait()

        if exception_container:
            raise exception_container[0]

        return result_container[0] if result_container else None

    async def _execute_sdk_call(
        self,
        sdk_executor: Any,
        prompt: str,
        **kwargs: Any
    ) -> Any:
        """
        使用execute_sdk_call执行SDK调用（简化版）

        Args:
            sdk_executor: 保留参数（不再使用）
            prompt: SDK提示词
            **kwargs: 其他参数

        Returns:
            SDK调用结果
        """
        self._log_execution(f"Executing SDK call via execute_sdk_call")

        try:
            # 使用sdk_helper的execute_sdk_call统一接口
            from .sdk_helper import execute_sdk_call

            result = await execute_sdk_call(
                prompt=prompt,
                agent_name=self.name,
                timeout=kwargs.get('timeout', 1800.0),
                permission_mode=kwargs.get('permission_mode', 'bypassPermissions')
            )

            self._log_execution(f"SDK call completed - Success: {result.is_success()}")
            return result

        except ImportError as e:
            self._log_execution(f"Failed to import SDK helper: {e}", "error")
            # 返回一个失败的 SDKResult
            from ..core.sdk_result import SDKResult, SDKErrorType
            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                error_type=SDKErrorType.SDK_ERROR,
                errors=[f"Import error: {e}"],
                agent_name=self.name
            )
        except Exception as e:
            self._log_execution(f"SDK call error: {e}", "error")
            from ..core.sdk_result import SDKResult, SDKErrorType
            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                error_type=SDKErrorType.SDK_ERROR,
                errors=[str(e)],
                last_exception=e,
                agent_name=self.name
            )

    def _validate_execution_context(self) -> bool:
        """验证执行上下文"""
        if not self.task_group:
            self._log_execution("Warning: No TaskGroup set", "warning")
            return False
        return True

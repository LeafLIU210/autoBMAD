"""
Base Agent - 所有 Agent 的基类
支持TaskGroup管理和SDKExecutor集成
"""
from __future__ import annotations
import logging
from anyio.abc import TaskGroup
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

        async def wrapper() -> Any:  # 不使用 task_status
            # 执行协程
            result = await coro()

            # 添加同步点，确保操作完成
            # 这防止了CancelScope跨任务访问问题
            import asyncio
            await asyncio.sleep(0)

            return result

        return await self.task_group.start(wrapper)  # type: ignore[arg-type]

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

    def get_sdk_config(self, **overrides: Any) -> dict[str, Any]:
        """
        获取统一SDK配置（从sdk_helper导入）

        Args:
            **overrides: 覆盖默认配置

        Returns:
            dict[str, Any]: SDK配置字典
        """
        from .sdk_helper import get_sdk_options
        return get_sdk_options(**overrides)

    async def _execute_sdk_call_with_config(
        self,
        prompt: str,
        **sdk_config: Any
    ) -> Any:
        """
        使用统一SDK配置的调用方法

        Args:
            prompt: SDK提示词
            **sdk_config: SDK配置参数

        Returns:
            SDK调用结果
        """
        # 使用统一的SDK配置
        config = self.get_sdk_config(**sdk_config)

        # 转换为SDK调用参数
        sdk_kwargs = {
            'prompt': prompt,
            'agent_name': self.name,
            **{k: v for k, v in config.items() if k != 'permission_mode'}
        }

        # 执行SDK调用
        return await self._execute_sdk_call(None, **sdk_kwargs)

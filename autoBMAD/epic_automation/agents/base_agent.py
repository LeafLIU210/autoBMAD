"""
Base Agent - 所有 Agent 的基类
支持TaskGroup管理和SDKExecutor集成
"""
from __future__ import annotations
import logging
import anyio
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent 基类，定义通用接口和行为"""

    def __init__(self, name: str, task_group: Optional[anyio.TaskGroup] = None):
        """
        初始化 Agent

        Args:
            name: Agent 名称
            task_group: 可选的TaskGroup实例
        """
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__module__}")
        self.task_group = task_group
        self._execution_context = {}

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

    def set_task_group(self, task_group: anyio.TaskGroup):
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

        async def wrapper(*, task_status: Any = anyio.TASK_STATUS_IGNORED) -> Any:  # type: ignore[misc,arg-type]
            if hasattr(task_status, 'started'):
                task_status.started()  # 通知TaskGroup任务已启动
            result = await coro()
            return result

        return await self.task_group.start(wrapper)  # type: ignore[arg-type]

    async def _execute_sdk_call(
        self,
        sdk_executor: Any,
        prompt: str,
        **kwargs: Any
    ) -> Any:
        """
        使用SDKExecutor执行SDK调用

        Args:
            sdk_executor: SDKExecutor实例
            prompt: SDK提示词
            **kwargs: 其他参数

        Returns:
            SDK调用结果
        """
        self._log_execution(f"Executing SDK call via SDKExecutor")
        result = await sdk_executor.execute_sdk_call(
            prompt=prompt,
            **kwargs
        )
        self._log_execution(f"SDK call completed")
        return result

    def _validate_execution_context(self) -> bool:
        """验证执行上下文"""
        if not self.task_group:
            self._log_execution("Warning: No TaskGroup set", "warning")
            return False
        return True

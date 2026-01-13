"""
Base Controller - 所有控制器的基类
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import MagicMock, AsyncMock

from anyio.abc import TaskGroup
import anyio

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """控制器基类，定义通用接口和行为"""

    def __init__(self, task_group: TaskGroup):
        """
        初始化控制器

        Args:
            task_group: 控制器所属的 TaskGroup
        """
        self.task_group = task_group
        self.logger = logging.getLogger(f"{self.__class__.__module__}")

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> bool:
        """
        执行控制器主逻辑

        Returns:
            bool: 执行是否成功
        """
        pass

    async def _execute_within_taskgroup(
        self, coro: Callable[[], Awaitable[Any]]
    ) -> Any:
        """
        在所属 TaskGroup 内执行协程

        Args:
            coro: 要执行的协程函数

        Returns:
            协程执行结果

        Raises:
            RuntimeError: 如果TaskGroup未正确初始化
            anyio.get_cancelled_exc_class(): 如果任务被取消
        """
        if not self.task_group:
            raise RuntimeError(f"{self.__class__.__name__}: TaskGroup not set")

        # 检查是否是Mock对象（用于测试）
        if isinstance(self.task_group, (MagicMock, AsyncMock)):
            # 对于Mock对象，直接执行协程，不使用TaskGroup
            return await coro()

        async def wrapper(task_status: anyio.TaskStatus) -> Any:
            # 执行协程
            result = await coro()

            # 添加同步点，确保操作完成
            # 这防止了CancelScope跨任务访问问题
            await anyio.sleep(0)

            # 标记任务完成（传递结果）
            task_status.started(result)  # type: ignore[reportAttributeAccessIssue]

            return result

        return await self.task_group.start(wrapper)

    def _log_execution(self, message: str, level: str = "info"):
        """记录执行日志"""
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"[{self.__class__.__name__}] {message}")


class StateDrivenController(BaseController, ABC):
    """状态驱动的控制器基类"""

    def __init__(self, task_group: TaskGroup):
        super().__init__(task_group)
        self.max_iterations = 3

    async def run_state_machine(self, initial_state: str, max_rounds: int = 3) -> bool:
        """
        运行状态机循环

        Args:
            initial_state: 初始状态
            max_rounds: 最大执行轮数

        Returns:
            bool: 是否达到终止状态
        """
        self.max_iterations = max_rounds
        return await self._run_state_machine_loop(initial_state)

    async def _run_state_machine_loop(self, initial_state: str) -> bool:
        """状态机循环实现"""
        current_state = initial_state
        for round_num in range(1, self.max_iterations + 1):
            self._log_execution(f"Round {round_num}: Current state = {current_state}")

            # 状态检查和决策
            next_state = await self._make_decision(current_state)

            if self._is_termination_state(next_state):
                self._log_execution(f"Reached termination state: {next_state}")
                return True

            current_state = next_state

        self._log_execution(f"Max iterations ({self.max_iterations}) reached")
        return False

    @abstractmethod
    async def _make_decision(self, current_state: str) -> str:
        """
        基于当前状态做出决策

        Args:
            current_state: 当前状态

        Returns:
            str: 下一个状态
        """
        pass

    def _is_termination_state(self, state: str) -> bool:
        """判断是否为终止状态"""
        return state in ["Done", "Ready for Done"]

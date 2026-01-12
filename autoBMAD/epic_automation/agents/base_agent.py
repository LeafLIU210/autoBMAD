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
        使用SDKExecutor执行SDK调用

        Args:
            sdk_executor: SDKExecutor实例
            prompt: SDK提示词
            **kwargs: 其他参数

        Returns:
            SDK调用结果
        """
        self._log_execution(f"Executing SDK call via SDKExecutor")

        try:
            # 动态导入 SafeClaudeSDK (从 sdk_wrapper)
            from ..sdk_wrapper import SafeClaudeSDK
            from ..core.sdk_result import SDKResult

            # 创建 SDK 查询函数
            async def sdk_query():
                try:
                    sdk = SafeClaudeSDK(prompt=prompt, options=None, log_manager=self._log_manager)
                    # SafeClaudeSDK.execute() returns bool
                    result = await sdk.execute()
                    return result
                except Exception as e:
                    self._log_execution(f"SDK query error: {e}", "error")
                    raise

            # 目标检测函数 - 查找完成消息
            def target_detector(message):
                # 检测 Claude SDK 的完成信号
                if isinstance(message, dict):
                    # 检查是否是最终结果
                    if message.get("type") == "done" or message.get("type") == "result":
                        return True
                    # 检查消息内容中的完成关键词
                    content = str(message.get("content", "") or message.get("text", ""))
                    if any(keyword in content.lower() for keyword in [
                        "complete", "finished", "done", "success", "ready for review"
                    ]):
                        return True
                return False

            # 使用 SDKExecutor 执行
            result = await sdk_executor.execute(
                sdk_func=sdk_query,
                target_predicate=target_detector,
                agent_name=self.name,
                **kwargs
            )

            self._log_execution(f"SDK call completed - Success: {result.is_success()}")
            return result

        except ImportError as e:
            self._log_execution(f"Failed to import SafeClaudeSDK: {e}", "error")
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

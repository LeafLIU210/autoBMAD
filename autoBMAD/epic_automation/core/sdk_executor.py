"""SDK执行器

该模块实现SDK执行器，在独立TaskGroup中执行SDK调用：
- SDKExecutor: SDK执行器类

核心功能：
1. 在独立TaskGroup中执行SDK调用
2. 收集流式ResultMessage
3. 检测目标ResultMessage
4. 请求取消并等待清理完成
5. 封装所有异常
"""

import anyio
import time
import uuid
import logging
from typing import Callable, Any, TYPE_CHECKING
from collections.abc import AsyncIterator

from .sdk_result import SDKResult, SDKErrorType
from .cancellation_manager import CancellationManager

if TYPE_CHECKING:
    from anyio.abc import TaskGroup


logger = logging.getLogger(__name__)


class SDKExecutor:
    """
    SDK执行器

    在独立的TaskGroup中执行SDK调用，确保Cancel Scope不会跨Task传播。

    使用流程：
    1. 创建SDKExecutor实例
    2. 调用execute方法，传入sdk_func和target_predicate
    3. 获取SDKResult结果
    """

    def __init__(self) -> None:
        """初始化SDK执行器"""
        self.cancel_manager = CancellationManager()
        logger.debug("SDKExecutor initialized")

    async def execute(
        self,
        sdk_func: Callable[[], AsyncIterator[Any]],
        target_predicate: Callable[[Any], bool],
        *,
        timeout: float | None = None,
        agent_name: str = "Unknown"
    ) -> SDKResult:
        """
        在独立TaskGroup中执行SDK调用

        Args:
            sdk_func: SDK调用函数，返回异步生成器
            target_predicate: 目标消息检测函数，返回True表示找到目标
            timeout: 超时时间（秒），None表示无超时
            agent_name: Agent名称，用于日志和跟踪

        Returns:
            SDKResult: 执行结果，包含所有必要信息

        Raises:
            Exception: 如果执行过程中发生未预期的异常，会封装到SDKResult中
        """
        call_id = str(uuid.uuid4())
        session_id = f"{agent_name}-{call_id[:8]}"
        start_time = time.time()

        logger.info(f"[{agent_name}] SDK call started: {session_id}")

        # 在独立TaskGroup中执行
        result: SDKResult | None = None
        duration = 0.0

        try:
            async with anyio.create_task_group() as sdk_tg:
                result = await self._execute_in_taskgroup(
                    sdk_tg,
                    sdk_func,
                    target_predicate,
                    call_id,
                    agent_name,
                    timeout
                )

        except Exception as e:
            # 所有异常都封装在结果中
            duration = time.time() - start_time
            logger.error(
                f"[{agent_name}] SDK call failed: {e}",
                exc_info=True
            )

            # 记录日志
            logger.info(
                f"[{agent_name}] SDK call finished: {session_id} "
                f"({duration:.2f}s)"
            )

            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                duration_seconds=duration,
                session_id=session_id,
                agent_name=agent_name,
                error_type=SDKErrorType.UNKNOWN,
                errors=[str(e)],
                last_exception=e
            )

        finally:
            duration = time.time() - start_time
            logger.info(
                f"[{agent_name}] SDK call finished: {session_id} "
                f"({duration:.2f}s)"
            )

        # 确保result不为None才返回
        if result is not None:
            return result

        # 如果result为None（不应该发生），返回错误结果
        return SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=duration,
            session_id=session_id,
            agent_name=agent_name,
            error_type=SDKErrorType.UNKNOWN,
            errors=["Internal error: result is None"],
            last_exception=None
        )

    async def _execute_in_taskgroup(
        self,
        task_group: 'TaskGroup',
        sdk_func: Callable[[], AsyncIterator[Any]],
        target_predicate: Callable[[Any], bool],
        call_id: str,
        agent_name: str,
        timeout: float | None
    ) -> SDKResult:
        """
        在TaskGroup中执行SDK调用（骨架实现）

        注意：这是骨架实现，完整实现将在Day 2完成。

        Args:
            task_group: TaskGroup实例
            sdk_func: SDK调用函数
            target_predicate: 目标检测函数
            call_id: 调用唯一标识符
            agent_name: Agent名称
            timeout: 超时时间

        Returns:
            SDKResult: 执行结果

        Raises:
            NotImplementedError: 当前为骨架实现，将在Day 2完整实现
        """
        # TODO: 在Day 2实现完整逻辑
        raise NotImplementedError(
            "完整实现将在Day 2完成。当前为骨架实现。"
        )

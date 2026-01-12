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
from typing import Callable, Any, TYPE_CHECKING, Union, Awaitable
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
        sdk_func: Union[Callable[[], AsyncIterator[Any]], Callable[[], Awaitable[Any]]],
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
        sdk_func: Union[Callable[[], AsyncIterator[Any]], Callable[[], Awaitable[Any]]],
        target_predicate: Callable[[Any], bool],
        call_id: str,
        agent_name: str,
        timeout: float | None
    ) -> SDKResult:
        """
        在TaskGroup中执行SDK调用

        Args:
            task_group: TaskGroup实例
            sdk_func: SDK调用函数
            target_predicate: 目标检测函数
            call_id: 调用唯一标识符
            agent_name: Agent名称
            timeout: 超时时间

        Returns:
            SDKResult: 执行结果
        """
        import anyio
        import time

        # 注册调用
        self.cancel_manager.register_call(call_id, agent_name)

        messages = []
        target_message = None
        errors = []
        start_time = time.time()

        try:
            # 检查sdk_func的类型来决定处理方式
            import inspect
            if inspect.isasyncgenfunction(sdk_func):
                # 原始的async generator逻辑
                sdk_generator = sdk_func()

                # 收集流式消息
                async for message in sdk_generator:
                    messages.append(message)
                    logger.debug(f"[{agent_name}] Received message: {type(message)}")

                    # 检测目标
                    try:
                        if target_predicate(message):
                            target_message = message
                            self.cancel_manager.mark_target_result_found(call_id)
                            logger.info(f"[{agent_name}] Target found, requesting cancel")

                            # 请求取消
                            self.cancel_manager.request_cancel(call_id)

                            # 注意：不break，继续收集消息直到生成器结束

                    except Exception as e:
                        errors.append(f"Target predicate error: {e}")
                        logger.error(f"[{agent_name}] Target predicate error: {e}")

                # 生成器正常结束，标记清理完成
                self.cancel_manager.mark_cleanup_completed(call_id)
            elif inspect.iscoroutinefunction(sdk_func):
                # 协程函数 - await并获取结果
                sdk_result: Any = await sdk_func()

                # 如果SDK返回bool，创建一个ynthetic消息
                if isinstance(sdk_result, bool):
                    message = {
                        "type": "result" if sdk_result else "error",
                        "content": f"SDK execution result: {sdk_result}",
                        "result": sdk_result
                    }
                    messages.append(message)

                    # 检测目标
                    try:
                        if target_predicate(message):
                            target_message = message
                            self.cancel_manager.mark_target_result_found(call_id)
                            logger.info(f"[{agent_name}] Target found, requesting cancel")

                            # 请求取消
                            self.cancel_manager.request_cancel(call_id)

                    except Exception as e:
                        errors.append(f"Target predicate error: {e}")
                        logger.error(f"[{agent_name}] Target predicate error: {e}")

                # 协程正常结束，标记清理完成
                self.cancel_manager.mark_cleanup_completed(call_id)
            else:
                # 其他类型，尝试直接调用
                raise TypeError(f"Unsupported sdk_func type: {type(sdk_func)}")

            # 等待确认可以安全进行
            safe = await self.cancel_manager.confirm_safe_to_proceed(call_id)

            duration = time.time() - start_time

            # 如果没有找到目标，添加默认错误信息
            if not target_message:
                errors.append("No target result found")

            # 确保变量有正确类型
            typed_messages: list[Any] = messages
            typed_target_message: Any = target_message
            typed_errors: list[str] = errors

            return SDKResult(
                has_target_result=typed_target_message is not None,
                cleanup_completed=safe,
                duration_seconds=duration,
                session_id=f"{agent_name}-{call_id[:8]}",
                agent_name=agent_name,
                messages=typed_messages,
                target_message=typed_target_message,
                error_type=SDKErrorType.SUCCESS if typed_target_message else SDKErrorType.UNKNOWN,
                errors=typed_errors
            )

        except anyio.get_cancelled_exc_class() as e:
            # 取消异常
            duration = time.time() - start_time
            errors.append(f"Cancelled: {e}")

            # 确保变量有正确类型 (重新赋值避免遮蔽)
            cancel_messages: list[Any] = messages
            cancel_errors: list[str] = errors

            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                duration_seconds=duration,
                session_id=f"{agent_name}-{call_id[:8]}",
                agent_name=agent_name,
                messages=cancel_messages,
                error_type=SDKErrorType.CANCELLED,
                errors=cancel_errors,
                last_exception=e
            )

        except Exception as e:
            # 其他异常 - 让异常传播到execute方法进行TaskGroup级别的处理
            raise

        finally:
            # 清理
            self.cancel_manager.unregister_call(call_id)

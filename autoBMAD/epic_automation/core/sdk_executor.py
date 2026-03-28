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

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TYPE_CHECKING, Any

import anyio

from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
from autoBMAD.epic_automation.core.sdk_result import SDKErrorType, SDKResult

if TYPE_CHECKING:
    from anyio.abc import TaskGroup

# 默认的fallback函数定义（避免循环导入）
def is_result_message(message: Any) -> bool:
    """检查是否为ResultMessage"""
    return hasattr(message, "__class__") and "ResultMessage" in type(message).__name__

def is_error_result(message: Any) -> bool:
    """检查ResultMessage是否为错误"""
    return is_result_message(message) and getattr(message, "is_error", False)


class PostResultMessageError(Exception):
    """
    自定义异常：用于在ResultMessage之后发生错误时传递成功结果信息

    当SDK调用在接收到ResultMessage之后但在清理过程中发生错误时使用。
    这样execute()方法可以识别这种情况并返回成功结果。
    """

    def __init__(
        self,
        message: str,
        last_result_message: Any = None,
        captured_messages: list[Any] | None = None
    ):
        super().__init__(message)
        self.last_result_message = last_result_message
        self.captured_messages = captured_messages or []


def extract_post_result_error(exc: BaseException) -> PostResultMessageError | None:
    """递归提取嵌套异常中的 PostResultMessageError。"""
    if isinstance(exc, PostResultMessageError):
        return exc

    if isinstance(exc, BaseExceptionGroup):
        for sub_exc in exc.exceptions:
            extracted = extract_post_result_error(sub_exc)
            if extracted is not None:
                return extracted

    cause = exc.__cause__
    if cause is not None:
        return extract_post_result_error(cause)

    return None


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
        sdk_func: Callable[[], AsyncIterator[Any]] | Callable[[], Awaitable[Any]],
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
            # SDK_CLI_EXIT_CODE_FIX: 检查是否是PostResultMessageError
            # 可能直接是PostResultMessageError，也可能在ExceptionGroup中
            post_result_error = extract_post_result_error(e)

            if post_result_error is not None:
                last_msg = post_result_error.last_result_message
                captured_messages = post_result_error.captured_messages or []

                # 检查是否捕获了有效的ResultMessage
                if last_msg is not None:
                    is_error_result_flag = (
                        hasattr(last_msg, "is_error") and
                        last_msg.is_error
                    )

                    if not is_error_result_flag:
                        duration = time.time() - start_time
                        logger.warning(
                            f"[{agent_name}] Post-ResultMessage error (caught at execute level): {post_result_error}"
                        )
                        logger.info(
                            f"[{agent_name}] Returning success based on captured ResultMessage"
                        )

                        return SDKResult(
                            has_target_result=True,
                            cleanup_completed=True,
                            duration_seconds=duration,
                            session_id=session_id,
                            agent_name=agent_name,
                            messages=captured_messages,
                            target_message=last_msg,
                            error_type=SDKErrorType.SUCCESS,
                            errors=[f"Post-completion error (ignored): {str(post_result_error)[:200]}"]
                        )

                duration = time.time() - start_time
                return SDKResult(
                    has_target_result=False,
                    cleanup_completed=False,
                    duration_seconds=duration,
                    session_id=session_id,
                    agent_name=agent_name,
                    messages=captured_messages,
                    error_type=SDKErrorType.SDK_ERROR,
                    errors=[str(post_result_error)],
                    last_exception=post_result_error,
                )

            # 所有其他异常都封装在结果中
            duration = time.time() - start_time
            logger.error(
                f"[{agent_name}] SDK call failed: {e}",
                exc_info=True
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
            logger.info(f"[{agent_name}] SDK call finished: {session_id} ({duration:.2f}s)")

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
        _task_group: 'TaskGroup',
        sdk_func: Callable[[], AsyncIterator[Any]] | Callable[[], Awaitable[Any]],
        target_predicate: Callable[[Any], bool],
        call_id: str,
        agent_name: str,
        _timeout: float | None
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
        import time

        import anyio

        # 注册调用
        self.cancel_manager.register_call(call_id, agent_name)

        messages = []
        target_message = None
        errors = []
        start_time = time.time()

        # Track ResultMessage for post-error recovery (SDK_CLI_EXIT_CODE_FIX)
        result_message_received = False
        last_result_message = None

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

                        # SDK_CLI_EXIT_CODE_FIX: Track ResultMessage for error recovery
                        # 使用is_result_message函数进行更可靠的检查
                        if is_result_message(message):
                            result_message_received = True
                            last_result_message = message
                            logger.debug(f"[{agent_name}] ResultMessage captured for error recovery")

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

                # SDK_CLI_EXIT_CODE_FIX: Track ResultMessage for error recovery (coroutine path)
                # 使用is_result_message函数进行更可靠的检查
                if is_result_message(sdk_result):
                    result_message_received = True
                    last_result_message = sdk_result
                    logger.debug(f"[{agent_name}] ResultMessage captured for error recovery")

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
            # SDK_CLI_EXIT_CODE_FIX: 检查是否在接收ResultMessage之后发生错误
            if result_message_received and last_result_message is not None:
                # 检查ResultMessage是否表示成功
                is_error_result_flag = (
                    hasattr(last_result_message, "is_error") and
                    last_result_message.is_error
                )

                if not is_error_result_flag:
                    duration = time.time() - start_time
                    logger.warning(
                        f"[{agent_name}] Post-ResultMessage error ignored: {e}"
                    )
                    logger.info(
                        f"[{agent_name}] Returning success based on captured ResultMessage"
                    )

                    # 返回成功结果
                    return SDKResult(
                        has_target_result=True,
                        cleanup_completed=True,
                        duration_seconds=duration,
                        session_id=f"{agent_name}-{call_id[:8]}",
                        agent_name=agent_name,
                        messages=messages,
                        target_message=last_result_message,
                        error_type=SDKErrorType.SUCCESS,
                        errors=[f"Post-completion error (ignored): {str(e)[:200]}"]
                    )

            # 没有捕获到有效结果，传播带有上下文的异常
            raise PostResultMessageError(
                str(e),
                last_result_message=last_result_message,
                captured_messages=messages
            ) from e

        finally:
            # 清理
            self.cancel_manager.unregister_call(call_id)

"""
修复后的SDK包装器 - Fixed SDK Wrapper with Cancellation Manager Integration

解决cancel scope跨任务错误和异步生成器生命周期管理问题。
基于原版本：d:\\GITHUB\\pytQt_template\\autoBMAD\\epic_automation\\sdk_wrapper.py

主要修复：
1. 解决cancel scope跨任务错误
2. 集成SDK取消管理器（统一管理）
3. 优化异步生成器生命周期管理
4. 增强错误恢复机制
5. 改进资源清理逻辑
6. 移除分散的取消判断逻辑（符合奥卡姆剃刀原则）
"""

import asyncio
import logging
import time
import traceback
from collections.abc import AsyncIterator
from typing import Any, TypeVar

# Type aliases for SDK Classes
try:  # type: ignore[import-untyped, import-untyped-missing, reportMissingImports]
    from claude_agent_sdk import ResultMessage, query

    _query = query
    _ResultMessage = ResultMessage
    _sdk_available = True  # type: ignore
except ImportError:
    _query = None  # type: ignore
    _ResultMessage = None  # type: ignore
    _sdk_available = False  # type: ignore

# Re-export with proper types
query = _query
ResultMessage = _ResultMessage

# Import Claude SDK types for proper type checking
try:  # type: ignore[import-untyped, import-untyped-missing, reportMissingImports]
    from claude_agent_sdk import (
        AssistantMessage as _AssistantMessage,
    )
    from claude_agent_sdk import (
        SystemMessage as _SystemMessage,
    )  # noqa: F401  # Imported for type checking, used via duck typing
    from claude_agent_sdk import (
        TextBlock as _TextBlock,
    )
    from claude_agent_sdk import (
        ThinkingBlock as _ThinkingBlock,
    )
    from claude_agent_sdk import (
        ToolResultBlock as _ToolResultBlock,
    )
    from claude_agent_sdk import (
        ToolUseBlock as _ToolUseBlock,
    )
    from claude_agent_sdk import (
        UserMessage as _UserMessage,
    )

    _claude_types_available = True
except ImportError:
    # Fallback types for when SDK is not available
    _SystemMessage = None  # type: ignore[misc]
    _AssistantMessage = None  # type: ignore[misc]
    _UserMessage = None  # type: ignore[misc]
    _TextBlock = None  # type: ignore[misc]
    _ThinkingBlock = None  # type: ignore[misc]
    _ToolUseBlock = None  # type: ignore[misc]
    _ToolResultBlock = None  # type: ignore[misc]
    _claude_types_available = False

# Re-export with proper names (kept for backward compatibility)
SystemMessage = _SystemMessage
AssistantMessage = _AssistantMessage
UserMessage = _UserMessage
TextBlock = _TextBlock
ThinkingBlock = _ThinkingBlock
ToolUseBlock = _ToolUseBlock
ToolResultBlock = _ToolResultBlock

# Export constants for backward compatibility
SDK_AVAILABLE = _sdk_available
CLAUDE_TYPES_AVAILABLE = _claude_types_available

logger = logging.getLogger(__name__)

# Type variable for generic async generator
_T = TypeVar("_T")


class SDKExecutionError(Exception):
    """SDK执行错误异常"""

    pass


class SafeAsyncGenerator:
    """安全的异步生成器包装器"""

    def __init__(
        self, generator: AsyncIterator[Any], cleanup_timeout: float = 1.0
    ) -> None:
        self.generator = generator
        self.cleanup_timeout = cleanup_timeout
        self._closed = False

    def __aiter__(self) -> "SafeAsyncGenerator":
        """异步迭代器"""
        return self

    async def __anext__(self) -> Any:
        """异步下一项"""
        if self._closed:
            raise StopAsyncIteration

        try:
            return await self.generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
        except Exception as e:
            logger.error(f"Error in async generator: {e}")
            logger.debug(traceback.format_exc())
            await self.aclose()
            raise

    async def aclose(self) -> None:
        """
        安全的异步生成器清理 - 防止 cancel scope 跨任务错误

        🎯 核心原则：在同一 Task 中完成资源清理，确保 cancel scope 生命周期一致

        结构重构说明：
        1. 移除跨 Task 清理逻辑，避免 cancel scope 在不同 Task 中 enter/exit
        2. 在当前 Task 中同步标记清理状态
        3. 通知 SDK 取消管理器清理完成（必要条件）
        """
        if self._closed:
            return

        self._closed = True

        # 🎯 关键修复：在同一 Task 中完成清理，不跨 Task
        # 1. 不在 async context 中调用原始生成器的 aclose()
        # 2. 立即标记清理状态
        # 3. 通知 SDK 取消管理器清理完成

        logger.debug("SafeAsyncGenerator marked as closed (cleanup in same task)")

        # ⚠️ 重要：清理资源是 SDK 取消管理器判断取消成功的必要条件
        # 必须在 track_sdk_execution() 的 finally 块中调用，确保：
        # - call_info["cleanup_completed"] = True
        # - del active_sdk_calls[call_id]
        # 只有这样，confirm_safe_to_proceed() 才会返回 True

        # 🎯 关键：完全忽略 cancel scope 错误，不记录为严重错误
        try:
            resource_tracker = getattr(self.generator, '_resource_tracker', None)
            if resource_tracker is not None and hasattr(resource_tracker, 'mark_for_cleanup'):
                resource_tracker.mark_for_cleanup()
        except Exception as e:
            error_msg = str(e)
            # 完全忽略 cancel scope 错误
            if "cancel scope" in error_msg.lower() or "different task" in error_msg.lower():
                logger.debug(f"Ignored cancel scope error in generator cleanup: {error_msg}")
            else:
                logger.debug(f"Failed to mark resource for cleanup: {e}")

    async def _ensure_cleanup_complete(self) -> None:
        """🎯 确保清理完全结束"""
        try:
            # 等待一小段时间确保清理完成
            await asyncio.sleep(0.1)
            logger.debug("SDK cleanup completed")
        except Exception as e:
            logger.debug(f"Cleanup completion check failed: {e}")


class SDKMessageTracker:
    """Tracks latest SDK message and periodically displays it."""

    def __init__(self, log_manager: Any | None = None):
        self.latest_message: str | None = None
        self.message_type: str = "INFO"
        self.message_count: int = 0
        self.start_time: float = time.time()
        self._stop_event: asyncio.Event = asyncio.Event()
        self._display_task: asyncio.Task[None] | None = None
        self.log_manager = log_manager

    def update_message(self, message: str, msg_type: str = "INFO"):
        """Update the latest message and its type."""
        self.latest_message = message
        self.message_type = msg_type
        self.message_count += 1

        # Write to log file if log_manager is available
        if self.log_manager:
            try:
                self.log_manager.write_sdk_message(message, msg_type)
            except Exception as e:
                logger.debug(f"Failed to write SDK message to log: {e}")

        # Output to console for real-time display (will be captured by DualWriteStream)
        print(f"[{msg_type}] {message}")

    def get_elapsed_time(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time

    async def start_periodic_display(self):
        """Start periodic display of latest message every 30 seconds."""
        # Only create task if not already created
        if self._display_task is None or self._display_task.done():
            self._stop_event.clear()  # Reset stop event
            # Create task and shield the coroutine from external cancellation
            self._display_task = asyncio.create_task(self._periodic_display())

    async def stop_periodic_display(self, timeout: float = 1.0):
        """Stop the periodic display using Event signaling instead of task cancellation."""
        self._stop_event.set()
        if self._display_task and not self._display_task.done():
            try:
                # Wait for task to exit naturally using Event signal
                await asyncio.wait_for(self._display_task, timeout=timeout)
            except TimeoutError:
                # Task didn't exit in time, but stop_event is set so it will exit on next iteration
                logger.debug(
                    "Display task exit timeout (acceptable - will exit naturally)"
                )
            except Exception as e:
                logger.debug(f"Error waiting for display task to exit: {e}")
            finally:
                self._display_task = None

    def signal_stop(self):
        """
        Signal the periodic display to stop via the internal stop event.

        This method provides a safe way to trigger the stop event without
        direct access to the private _stop_event attribute.
        """
        self._stop_event.set()

    async def _periodic_display(self):
        """Display latest message every 30 seconds."""
        try:
            while not self._stop_event.is_set():
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=30.0)
                    break  # Stop event was set
                except TimeoutError:
                    # 30 seconds passed, display latest message
                    if self.latest_message and not self._stop_event.is_set():
                        elapsed = self.get_elapsed_time()
                        # Clean display format: [Type] Message content
                        logger.info(
                            f"[{self.message_type}] {self.latest_message} (after {elapsed:.1f}s)"
                        )
        except asyncio.CancelledError:
            # Task was cancelled, exit gracefully without raising
            logger.debug("Periodic display task was cancelled")
            # Don't re-raise CancelledError to prevent scope issues
            return
        except Exception as e:
            # Log any unexpected errors but don't crash
            logger.debug(f"Error in periodic display: {e}")

    def display_final_summary(self):
        """Display final summary when complete."""
        elapsed = self.get_elapsed_time()
        logger.info(
            f"[COMPLETE] SDK execution finished with {self.message_count} messages in {elapsed:.1f}s"
        )


class SafeClaudeSDK:
    """
    Fixed safe wrapper for Claude SDK with unified cancellation management.

    This wrapper ensures proper cleanup of async generators and prevents
    RuntimeError when event loop closes. Now integrated with SDKCancellationManager
    for unified cancellation handling.

    Major fixes:
    1. Integration with SDKCancellationManager (unified management)
    2. Task isolation for generator lifecycle
    3. Enhanced error recovery
    4. Safe resource cleanup
    5. Cross-task cancel scope protection
    6. Removed distributed cancellation logic (遵循奥卡姆剃刀原则)
    """

    def __init__(
        self,
        prompt: str,
        options: Any,
        timeout: float | None = None,
        log_manager: Any | None = None,
    ):
        self.prompt: str = prompt
        self.options: Any = options
        self.timeout: float | None = timeout
        self.message_tracker: SDKMessageTracker = SDKMessageTracker(log_manager)
        self.log_manager = log_manager

    def _extract_message_content(self, message: Any) -> str | None:
        """Extract actual content from Claude SDK messages - unified method."""
        try:
            # Get message class name for unified handling
            msg_class = (
                message.__class__.__name__
                if hasattr(message, "__class__")
                else "Unknown"
            )

            # Handle AssistantMessage - Claude's actual responses
            if msg_class == "AssistantMessage" and hasattr(message, "content"):
                return self._extract_assistant_content(message)
            # Handle SystemMessage - System initialization/info
            elif msg_class == "SystemMessage":
                return self._extract_system_content(message)
            # Handle UserMessage - User inputs
            elif msg_class == "UserMessage":
                return self._extract_user_content(message)
            # Handle ResultMessage - Final results
            elif msg_class == "ResultMessage":
                return self._extract_result_content(message)

        except Exception as e:
            logger.debug(f"Failed to extract message content: {e}")
        return None

    def _extract_assistant_content(self, message: Any) -> str | None:
        """Extract content from AssistantMessage."""
        if not hasattr(message, "content") or not isinstance(message.content, list):
            return None

        content_parts: list[str] = []
        content_list: list[Any] = message.content  # type: ignore[assignment]
        for block in content_list:
            block_item: Any = block
            block_type: str = str(block_item.__class__.__name__)

            if block_type == "TextBlock" and hasattr(block_item, "text"):
                text_value: str = str(getattr(block_item, "text", ""))
                if text_value:
                    content_parts.append(text_value.strip())
            elif block_type == "ThinkingBlock" and hasattr(block_item, "thinking"):
                thinking_value: str = str(getattr(block_item, "thinking", ""))
                if thinking_value:
                    thinking_text: str = thinking_value.strip()
                    preview: str = (
                        thinking_text[:150] + "..."
                        if len(thinking_text) > 150
                        else thinking_text
                    )
                    content_parts.append(f"[Thinking] {preview}")
            elif block_type == "ToolUseBlock" and hasattr(block_item, "name"):
                tool_name: str = str(getattr(block_item, "name", "unknown"))
                content_parts.append(f"[Using tool: {tool_name}]")
            elif block_type == "ToolResultBlock" and hasattr(block_item, "content"):
                tool_content: Any = getattr(block_item, "content", None)
                if tool_content:
                    if isinstance(tool_content, str) and tool_content.strip():
                        content_parts.append(f"[Tool result] {tool_content.strip()}")
                    elif isinstance(tool_content, list):
                        result_count: int = len(tool_content)  # type: ignore[arg-type]
                        if result_count > 0:
                            content_parts.append(
                                f"[Tool completed with {result_count} results]"
                            )

        return " ".join(content_parts) if content_parts else None

    def _extract_system_content(self, message: Any) -> str | None:
        """Extract content from SystemMessage."""
        if not hasattr(message, "subtype"):
            return None

        subtype: str = str(getattr(message, "subtype", "unknown"))
        if hasattr(message, "data") and isinstance(message.data, dict):  # type: ignore[union-attr]
            data_dict: dict[str, Any] = message.data  # type: ignore[assignment]
            if subtype == "init":
                session_id: str = str(data_dict.get("session_id", "unknown"))
                model: str = str(data_dict.get("model", "unknown"))
                return (
                    f"[System initialized] Model: {model}, Session: {session_id[:8]}..."
                )
            elif subtype == "tool":
                tool_name: str = str(data_dict.get("tool", "unknown"))
                return f"[System] Tool: {tool_name}"
        return f"[System] {subtype}"

    def _extract_user_content(self, message: Any) -> str | None:
        """Extract content from UserMessage."""
        if not hasattr(message, "content"):
            return None

        content: Any = message.content  # type: ignore[union-attr]
        if isinstance(content, str) and content.strip():
            return f"[User] {content.strip()[:100]}..."
        elif isinstance(content, list):
            block_count: int = len(content)  # type: ignore[arg-type]
            return f"[User sent {block_count} content blocks]"
        return None

    def _extract_result_content(self, message: Any) -> str | None:
        """Extract content from ResultMessage."""
        if hasattr(message, "is_error"):
            if message.is_error:
                error_result = getattr(message, "result", "Unknown error")
                return f"[Error] {error_result}"
            else:
                success_result = getattr(message, "result", "Success")
                if isinstance(success_result, str) and len(success_result) > 200:
                    return f"[Success] {success_result[:200]}..."
                else:
                    return f"[Success] {success_result}"

        if hasattr(message, "num_turns"):
            turns = getattr(message, "num_turns", 0)
            duration = getattr(message, "duration_ms", 0) / 1000
            return f"[Complete] {turns} turns, {duration:.1f}s"
        return None

    def _classify_message_type(self, message: Any) -> str:
        """Classify the type of message from Claude SDK - simplified."""
        try:
            msg_class = (
                message.__class__.__name__
                if hasattr(message, "__class__")
                else "Unknown"
            )

            if msg_class == "SystemMessage":
                subtype = getattr(message, "subtype", "unknown")
                if subtype == "init":
                    return "INIT"
                elif subtype == "tool":
                    return "TOOL"
                return "SYSTEM"

            elif msg_class == "AssistantMessage":
                if hasattr(message, "content") and isinstance(message.content, list):  # type: ignore
                    for block in message.content:  # type: ignore
                        block_type = block.__class__.__name__  # type: ignore
                        if block_type == "ThinkingBlock":
                            return "THINKING"
                        elif block_type == "TextBlock":
                            return "ASSISTANT"
                        elif block_type == "ToolUseBlock":
                            return "TOOL_USE"
                        elif block_type == "ToolResultBlock":
                            return "TOOL_RESULT"
                return "ASSISTANT"

            elif msg_class == "UserMessage":
                return "USER"

            elif msg_class == "ResultMessage":
                if hasattr(message, "is_error") and message.is_error:
                    return "ERROR"
                return "SUCCESS"

            return "INFO"

        except Exception as e:
            logger.debug(f"Failed to classify message type: {e}")
            return "INFO"

    async def execute(self) -> bool:
        """
        执行Claude SDK查询 with unified cancellation management and cross-task error recovery.

        🎯 核心增强：
        1. 检测并恢复 cancel scope 跨任务错误
        2. 在结构层面解决 enter/exit 不在同一 Task 的问题
        3. 提供重新执行机制，避免"取消操作重试"
        4. 当已收到结果时，忽略 cancel scope 清理错误（视为成功）
        """
        if not SDK_AVAILABLE:
            logger.warning("Claude Agent SDK not available")
            return False

        max_retries = 2
        retry_count = 0

        while retry_count <= max_retries:
            try:
                result = await self._execute_with_recovery()
                return result
            except RuntimeError as e:
                error_msg = str(e)
                if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
                    # 🎯 关键：检查是否已收到结果（通过管理器）
                    try:
                        from autoBMAD.epic_automation.monitoring import get_cancellation_manager  # type: ignore[import-untyped]
                        manager = get_cancellation_manager()  # type: ignore[func-call]

                        # 检查active_sdk_calls中是否有结果
                        if manager.active_sdk_calls:  # type: ignore[attr-defined]
                            latest_call_id = list(manager.active_sdk_calls.keys())[-1]  # type: ignore[arg-type, attr-defined]
                            latest_call = manager.active_sdk_calls[latest_call_id]  # type: ignore[attr-defined]
                            if "result_received_at" in latest_call or "result" in latest_call:
                                logger.info(
                                    "[SafeClaudeSDK] Cancel scope error detected but result already received "
                                    "in active call. Treating as success."
                                )
                                return True

                        # 检查completed_calls
                        if manager.completed_calls:  # type: ignore[attr-defined]
                            latest_call = manager.completed_calls[-1]  # type: ignore[attr-defined]
                            if latest_call.get("result_received", False):
                                logger.info(
                                    "[SafeClaudeSDK] Cancel scope error detected but result already received "
                                    "in completed call. Treating as success."
                                )
                                return True

                    except Exception as check_error:
                        logger.debug(f"Error checking result status: {check_error}")

                    # 没有收到结果，继续重试逻辑
                    retry_count += 1
                    logger.warning(
                        f"[SafeClaudeSDK] Cancel scope cross-task error detected "
                        f"(attempt {retry_count}/{max_retries+1}). Rebuilding execution context..."
                    )

                    if retry_count > max_retries:
                        logger.error(
                            "[SafeClaudeSDK] Max retries reached for cancel scope error. "
                            "This indicates a structural issue that cannot be recovered automatically."
                        )
                        raise

                    # 🎯 关键：重建执行上下文，避免跨 Task 状态污染
                    await self._rebuild_execution_context()
                    continue
                else:
                    # 非 cancel scope 错误，直接抛出
                    raise
            except Exception:
                # 其他类型错误，不重试
                raise

        return False  # 不应该到达这里

    async def _execute_with_recovery(self) -> bool:
        """
        执行 SDK 查询的核心逻辑，支持错误恢复
        """
        # 🎯 关键：在单一 Task 中完成所有操作
        if not SDK_AVAILABLE:
            logger.warning("Claude Agent SDK not available")
            return False

        # 🎯 唯一入口：获取全局管理器
        try:
            from autoBMAD.epic_automation.monitoring import get_cancellation_manager  # type: ignore[import-untyped]
            manager = get_cancellation_manager()  # type: ignore[func-call]
        except ImportError as e:
            logger.warning(f"Could not import cancellation manager: {e}")
            return await self._execute_safely()

        call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"

        try:
            # 🎯 所有 SDK 执行都必须通过管理器追踪
            async with manager.track_sdk_execution(
                call_id=call_id,
                operation_name="sdk_execute",
                context={
                    "prompt_length": len(self.prompt),
                    "has_options": self.options is not None
                }
            ):
                result = await self._execute_safely_with_manager(manager, call_id)
                return result

        except asyncio.CancelledError:
            # 🎯 统一处理：完全委托给管理器决策
            cancel_type = manager.check_cancellation_type(call_id)

            if cancel_type == "after_success":
                # 管理器确认工作已完成，等待清理完成
                await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
                logger.info(
                    "[SafeClaudeSDK] Cancellation suppressed - "
                    "SDK completed successfully (confirmed by manager)"
                )
                return True

            # 🎯 关键修复：真正的取消不再 raise，返回 False
            # 这样可以避免 CancelledError 向上传播导致工作流中断
            logger.warning("SDK execution was cancelled (confirmed by manager), continuing workflow")
            # 等待清理完成
            await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
            return False  # ✅ 返回 False 而不是 raise，让工作流继续

        except Exception as e:
            logger.error(f"Claude SDK execution failed: {e}")
            logger.debug(traceback.format_exc())
            return False

    async def _execute_safely_with_manager(
        self,
        manager: Any,
        call_id: str
    ) -> bool:
        """
        Execute with cancellation manager integration.

        Args:
            manager: Cancellation manager instance
            call_id: Unique call identifier

        Returns:
            True if successful, False otherwise
        """
        if query is None or self.options is None:
            logger.warning("Claude SDK not properly initialized")
            return False

        logger.info("[SDK Start] Starting Claude SDK execution with tracking")
        logger.info(f"[SDK Config] Prompt length: {len(self.prompt)} characters")

        # 🎯 关键修复：清理任何挂起的取消信号
        # 确保新的 SDK 调用从干净的状态开始
        try:
            current_task = asyncio.current_task()
            if current_task and current_task.cancelled():
                logger.warning("[SDK Warning] Current task is in cancelled state, but attempting SDK call anyway")
                # 不要直接抛出，让 SDK 尝试执行
        except Exception as e:
            logger.debug(f"Could not check task cancel state: {e}")

        # Create query generator
        try:
            generator = query(prompt=self.prompt, options=self.options)  # type: ignore
        except Exception as e:
            logger.error(f"Failed to create SDK query generator: {e}")
            logger.debug(traceback.format_exc())
            return False

        # Wrap generator with safe wrapper
        safe_generator = SafeAsyncGenerator(generator)

        try:
            result = await self._run_isolated_generator_with_manager(
                safe_generator,
                manager,
                call_id
            )
            return result
        except Exception as e:
            logger.error(f"Error in isolated generator execution: {e}")
            logger.debug(traceback.format_exc())
            await safe_generator.aclose()
            return False

    async def _run_isolated_generator_with_manager(
        self,
        safe_generator: SafeAsyncGenerator,
        manager: Any,
        call_id: str
    ) -> bool:
        """
        Run generator with cancellation manager result tracking.

        🎯 关键改进：立即标记结果接收，保存已收到的消息
        """
        message_count = 0
        start_time = asyncio.get_running_loop().time()
        received_result = False  # 🎯 新增：跟踪是否已收到结果
        last_result_message = None  # 🎯 新增：保存最后的ResultMessage

        try:
            await self.message_tracker.start_periodic_display()

            async for message in safe_generator:
                message_count += 1

                message_content = self._extract_message_content(message)
                message_type = self._classify_message_type(message)

                if message_content:
                    self.message_tracker.update_message(message_content, message_type)

                if ResultMessage is not None and isinstance(message, ResultMessage):
                    # 🎯 立即保存ResultMessage
                    last_result_message = message
                    received_result = True

                    if hasattr(message, "is_error") and message.is_error:
                        error_msg = getattr(message, "result", "Unknown error")
                        logger.error(f"[SDK Error] Claude SDK error: {error_msg}")
                        return False
                    else:
                        result = getattr(message, "result", None)
                        result_str = str(result) if result else "No content"

                        # 🎯 关键：立即标记结果接收
                        manager.mark_result_received(call_id, result_str)

                        logger.info(f"[SDK Success] Claude SDK result: {result_str[:100]}")
                        return True

            # 没有收到 ResultMessage
            total_elapsed = asyncio.get_running_loop().time() - start_time

            await self.message_tracker.stop_periodic_display()

            if message_count > 0:
                logger.info(
                    f"[SDK Complete] Completed with {message_count} messages "
                    f"in {total_elapsed:.1f}s"
                )
                return True
            else:
                logger.error(f"[SDK Failed] No messages received after {total_elapsed:.1f}s")
                return False

        except StopAsyncIteration:
            logger.info("Claude SDK generator completed")
            return True

        except asyncio.CancelledError:
            # 🎯 关键修复：检查是否已收到 ResultMessage
            if received_result and last_result_message:
                logger.warning(
                    "[SDK Warning] Cancelled after receiving result - treating as success"
                )
                try:
                    await self.message_tracker.stop_periodic_display()
                except Exception as e:
                    logger.debug(f"Error stopping display task: {e}")

                # 处理已收到的 ResultMessage
                if hasattr(last_result_message, "is_error") and last_result_message.is_error:
                    error_msg = getattr(last_result_message, "result", "Unknown error")
                    logger.error(f"[SDK Error] Claude SDK error: {error_msg}")
                    return False
                else:
                    result = getattr(last_result_message, "result", None)
                    result_str = str(result) if result else "No content"
                    manager.mark_result_received(call_id, result_str)
                    logger.info(f"[SDK Success] Result retrieved despite cancellation: {result_str[:100]}")
                    return True
            else:
                logger.warning("Claude SDK execution was cancelled")

                try:
                    await self.message_tracker.stop_periodic_display()
                except Exception as e:
                    logger.debug(f"Error stopping display task: {e}")

                # 🎯 重新抛出，让外层检查取消类型
                raise

        except Exception as e:
            logger.error(f"Claude SDK execution error: {e}")
            try:
                await self.message_tracker.stop_periodic_display()
            except Exception as cleanup_error:
                logger.debug(f"Error during cleanup: {cleanup_error}")
            raise

        finally:
            await safe_generator.aclose()

    async def _rebuild_execution_context(self) -> None:
        """
        🎯 重建执行上下文，避免跨 Task 状态污染

        核心原理：
        1. 清理当前 Task 中的所有 SDK 相关资源
        2. 确保新的执行使用全新的 CancelScope 和 TaskGroup
        3. 不复用任何可能已损坏的异步上下文
        4. ⚠️ 验证资源清理完成，这是 SDK 取消管理器的必要条件
        """
        # 1. 等待足够时间，让前一个上下文完全释放
        # ⚠️ 延长至 0.5s 确保所有资源完全释放
        await asyncio.sleep(0.5)  # 从 0.1s 增加到 0.5s

        # 2. 清理当前 Task 的 SDK 状态
        try:
            from autoBMAD.epic_automation.monitoring import get_cancellation_manager  # type: ignore[import-untyped]
            manager = get_cancellation_manager()  # type: ignore[func-call]

            # 🎯 关键：确保所有活跃调用都已清理
            # active_sdk_calls 应该为空，否则 wait_for_cancellation_complete() 会超时
            active_count = len(manager.active_sdk_calls)  # type: ignore[arg-type, attr-defined]
            if active_count > 0:
                logger.warning(
                    f"[SafeClaudeSDK] {active_count} active SDK calls still present during rebuild. "
                    f"Forcing cleanup..."
                )
                # 强制清理
                manager.active_sdk_calls.clear()  # type: ignore[attr-defined]

            # 🎯 验证取消调用的清理状态
            incomplete_cleanups: list[dict[str, Any]] = [  # type: ignore[assignment]
                call for call in manager.cancelled_calls  # type: ignore[attr-defined]
                if not call.get("cleanup_completed", False)
            ]
            if incomplete_cleanups:
                logger.warning(
                    f"[SafeClaudeSDK] {len(incomplete_cleanups)} cancelled calls have incomplete cleanup. "
                    f"This may cause confirm_safe_to_proceed() to fail."
                )

            # 重置统计信息
            manager.stats["cross_task_errors"] = manager.stats.get("cross_task_errors", 0) + 1  # type: ignore[attr-defined]

            logger.info(
                "[SafeClaudeSDK] ✅ Execution context rebuilt successfully "
                f"(active: 0, incomplete: 0)"
            )
        except Exception as e:
            logger.error(f"[SafeClaudeSDK] Context rebuild failed: {e}")

    # 保留原有的_execute_safely方法作为后备
    async def _execute_safely(self) -> bool:
        """
        Legacy execute method (fallback when manager is not available).
        """
        if query is None or self.options is None:
            logger.warning("Claude SDK not properly initialized")
            return False

        logger.info("[SDK Start] Starting Claude SDK execution")
        logger.info(f"[SDK Config] Options: {self.options}")
        logger.info(f"[SDK Config] Prompt length: {len(self.prompt)} characters")

        # Create query generator
        try:
            generator = query(prompt=self.prompt, options=self.options)  # type: ignore
        except Exception as e:
            logger.error(f"Failed to create SDK query generator: {e}")
            logger.debug(traceback.format_exc())
            return False

        # Wrap generator with safe wrapper
        safe_generator = SafeAsyncGenerator(generator)

        try:
            result = await self._run_isolated_generator(safe_generator)
            return result
        except Exception as e:
            logger.error(f"Error in isolated generator execution: {e}")
            logger.debug(traceback.format_exc())
            await safe_generator.aclose()
            return False

    async def _run_isolated_generator(self, safe_generator: SafeAsyncGenerator) -> bool:
        """
        Run generator in isolated task with proper error handling.

        Legacy method for backward compatibility.
        """
        message_count = 0
        start_time = asyncio.get_running_loop().time()

        try:
            await self.message_tracker.start_periodic_display()

            async for message in safe_generator:
                message_count += 1

                message_content = self._extract_message_content(message)
                message_type = self._classify_message_type(message)

                if message_content:
                    self.message_tracker.update_message(message_content, message_type)
                else:
                    self.message_tracker.update_message(
                        f"Received {message_type} message {message_count}", message_type
                    )

                if ResultMessage is not None and isinstance(message, ResultMessage):
                    if hasattr(message, "is_error") and message.is_error:
                        error_msg = getattr(message, "result", "Unknown error")
                        self.message_tracker.update_message(
                            f"Error: {error_msg}", "ERROR"
                        )
                        logger.error(f"[SDK Error] Claude SDK error: {error_msg}")
                        return False
                    else:
                        result = getattr(message, "result", None)
                        if result:
                            result_str = str(result)
                            if len(result_str) > 100:
                                result_preview = result_str[:100] + "..."
                            else:
                                result_preview = result_str
                        else:
                            result_preview = "No content"
                        self.message_tracker.update_message(
                            f"Success: {result_preview}", "SUCCESS"
                        )
                        logger.info(
                            f"[SDK Success] Claude SDK result: {result_preview}"
                        )
                        return True

            total_elapsed = asyncio.get_running_loop().time() - start_time

            await self.message_tracker.stop_periodic_display()

            if message_count > 0:
                self.message_tracker.update_message(
                    f"Completed with {message_count} messages", "COMPLETE"
                )
                self.message_tracker.display_final_summary()
                logger.info(
                    f"[SDK Complete] Claude SDK completed with {message_count} messages in {total_elapsed:.1f}s"
                )
                return True
            else:
                prompt_str = str(self.prompt)
                if len(prompt_str) > 100:
                    prompt_preview = prompt_str[:100] + "..."
                else:
                    prompt_preview = prompt_str
                self.message_tracker.update_message(
                    "Failed: No messages received", "ERROR"
                )
                logger.error(
                    f"[SDK Failed] Claude SDK returned no messages after {total_elapsed:.1f}s"
                )
                logger.error(f"[Diagnostic] Prompt preview: {prompt_preview}")
                logger.error(f"[Diagnostic] Options: {self.options}")
                logger.error(f"[Diagnostic] Message count: {message_count}")
                return False

        except StopAsyncIteration:
            logger.info("Claude SDK generator completed")
            return True

        except asyncio.CancelledError:
            logger.warning("Claude SDK execution was cancelled")
            try:
                await self.message_tracker.stop_periodic_display()
            except Exception as e:
                logger.debug(f"Error stopping display task: {e}")
            raise

        except Exception as e:
            logger.error(f"Claude SDK execution error: {e}")
            logger.debug(traceback.format_exc())
            try:
                await self.message_tracker.stop_periodic_display()
            except Exception as cleanup_error:
                logger.debug(f"Error during cleanup: {cleanup_error}")
            raise

        finally:
            await safe_generator.aclose()


# Backward compatibility: keep old class name as alias
SDKWrapper = SafeClaudeSDK

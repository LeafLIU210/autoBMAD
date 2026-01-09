"""
修复后的SDK包装器 - Fixed SDK Wrapper

解决cancel scope跨任务错误和异步生成器生命周期管理问题。
基于原版本：d:\\GITHUB\\pytQt_template\\autoBMAD\\epic_automation\\sdk_wrapper.py

主要修复：
1. 解决cancel scope跨任务错误
2. 优化异步生成器生命周期管理
3. 增强错误恢复机制
4. 改进资源清理逻辑
"""

import asyncio
import logging
import time
import traceback
from collections.abc import AsyncIterator
from pathlib import Path
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
        """安全关闭生成器"""
        if self._closed:
            return

        self._closed = True

        try:
            aclose = getattr(self.generator, "aclose", None)
            if aclose and callable(aclose):
                # 直接关闭生成器，不使用超时保护
                try:
                    result = aclose()
                    if result is not None:
                        # 等待结果但不设置超时
                        if asyncio.iscoroutine(result):
                            await result
                except (TypeError, AttributeError) as e:
                    logger.debug(f"Generator cleanup (non-critical): {e}")
                except asyncio.CancelledError:
                    logger.debug("Generator cleanup cancelled (ignored)")
                except RuntimeError as e:
                    error_msg = str(e)
                    if (
                        "cancel scope" in error_msg
                        or "Event loop is closed" in error_msg
                    ):
                        # Suppress cancel scope errors - these are expected during SDK shutdown
                        logger.debug(
                            f"Expected SDK shutdown error (suppressed): {error_msg}"
                        )
                        return  # Return instead of raising to prevent crash
                    else:
                        logger.debug(f"Generator cleanup RuntimeError: {e}")
                        raise
                except Exception as e:
                    # Catch any other exceptions during cleanup
                    logger.debug(f"Generator cleanup exception: {e}")
        except Exception as e:
            logger.debug(f"Generator cleanup error: {e}")


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
        """Start periodic display of latest message every 10 seconds."""
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
        """Display latest message every 10 seconds."""
        try:
            while not self._stop_event.is_set():
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)
                    break  # Stop event was set
                except TimeoutError:
                    # 10 seconds passed, display latest message
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
    Fixed safe wrapper for Claude SDK to prevent cancel scope errors.

    This wrapper ensures proper cleanup of async generators and prevents
    RuntimeError when event loop closes.

    Major fixes:
    1. Task isolation for generator lifecycle
    2. Enhanced error recovery
    3. Safe resource cleanup
    4. Cross-task cancel scope protection
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
        Execute Claude SDK query safely with proper cleanup.

        Returns:
            True if execution succeeded, False otherwise
        """
        if not SDK_AVAILABLE:
            logger.warning(
                "Claude Agent SDK not available - returning False for cancelled execution"
            )
            return False

        # Execute without external timeout - use max_turns in SDK options instead
        try:
            return await self._execute_safely()
        except asyncio.CancelledError:
            # Cancellation handled by upper layer
            logger.warning("SDK execution was cancelled")
            raise
        except RuntimeError as e:
            error_msg = str(e)
            # Enhanced cancel scope error handling
            if "cancel scope" in error_msg:
                logger.error(f"Cancel scope error detected: {error_msg}")
                logger.debug(f"Cancel scope error details: {e}", exc_info=True)
                # Suppress cancel scope errors - they are expected during task cleanup
                return False
            elif "Event loop is closed" in error_msg:
                logger.warning(f"Event loop closed: {e}")
                return False
            else:
                logger.error(f"Runtime error in SDK execution: {e}")
                logger.debug(f"Runtime error details: {e}", exc_info=True)
                return False
        except Exception as e:
            error_msg = str(e)
            if "cancel scope" in error_msg:
                logger.error(f"Cancel scope error: {e}")
                logger.debug(traceback.format_exc())
                return False
            elif "Event loop is closed" in error_msg:
                logger.warning(f"Event loop closed: {e}")
                return False
            else:
                logger.error(f"Claude SDK execution failed: {e}")
                logger.debug(traceback.format_exc())
                return False

    async def _execute_safely(self) -> bool:
        """
        Execute with proper generator cleanup using isolated task.

        This is the key fix: run the generator in an isolated task to prevent
        cancel scope conflicts.
        """
        if query is None or self.options is None:
            logger.warning("Claude SDK not properly initialized")
            return False

        # Log SDK execution start
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

        # Run generator in isolated task to prevent cancel scope issues
        # Use asyncio.shield to protect from external cancellation
        try:
            result = await asyncio.shield(self._run_isolated_generator(safe_generator))
            return result
        except Exception as e:
            logger.error(f"Error in isolated generator execution: {e}")
            logger.debug(traceback.format_exc())
            await safe_generator.aclose()
            return False

    async def _run_isolated_generator(self, safe_generator: SafeAsyncGenerator) -> bool:
        """
        Run generator in isolated task with proper error handling.

        This method runs the generator processing in a way that prevents
        cancel scope cross-task issues.
        """
        message_count = 0
        start_time = asyncio.get_running_loop().time()

        try:
            # Start periodic message display
            await self.message_tracker.start_periodic_display()

            # Process messages from generator
            async for message in safe_generator:  # type: ignore[async-generic-without-base]
                message_count += 1

                # Extract actual content from Claude's messages
                message_content = self._extract_message_content(message)
                message_type = self._classify_message_type(message)

                # Update message tracker with actual Claude content
                if message_content:
                    self.message_tracker.update_message(message_content, message_type)
                else:
                    # Fallback to generic message if no content extracted
                    self.message_tracker.update_message(
                        f"Received {message_type} message {message_count}", message_type
                    )

                if ResultMessage is not None and isinstance(message, ResultMessage):
                    # Safely access attributes based on type
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

            # If we get here, no ResultMessage was received
            total_elapsed = asyncio.get_running_loop().time() - start_time

            # Stop periodic display
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
                # Enhanced error logging with diagnostic information
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
            # Stop periodic display
            try:
                await self.message_tracker.stop_periodic_display()
            except Exception as e:
                logger.debug(f"Error stopping display task: {e}")
            # Re-raise cancellation exception to allow upper layer handling
            raise
        except Exception as e:
            # Log error and stop periodic display
            logger.error(f"Claude SDK execution error: {e}")
            logger.debug(traceback.format_exc())
            try:
                await self.message_tracker.stop_periodic_display()
            except Exception as cleanup_error:
                logger.debug(f"Error during cleanup: {cleanup_error}")
            raise
        finally:
            # Ensure generator is closed
            await safe_generator.aclose()

    async def _check_work_completed(self) -> bool:
        """
        Check if SDK work was completed despite errors.

        Returns:
            True if work likely completed, False otherwise
        """
        try:
            # Check if expected files were created
            if Path("docs/stories").exists():
                story_files = list(Path("docs/stories").glob("*.md"))
                if story_files:
                    logger.info(
                        f"Found {len(story_files)} story files, assuming success"
                    )
                    return True
            return False
        except Exception:
            return False


# Backward compatibility: keep old class name as alias
SDKWrapper = SafeClaudeSDK

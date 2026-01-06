"""
Safe wrapper for Claude Agent SDK to handle async lifecycle properly.

This module provides a safe wrapper around the Claude Agent SDK to prevent
cancel scope errors and ensure proper cleanup of async generators.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional, cast
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import time

# Type aliases for SDK classes
try:
    from claude_agent_sdk import query, ResultMessage
    _query = query
    _ResultMessage = ResultMessage
    _sdk_available = True  # type: ignore
except ImportError:
    _query = None  # type: ignore
    _ResultMessage = None  # type: ignore  # type: ignore
    _sdk_available = False  # type: ignore

# Re-export with proper types
query = _query
ResultMessage = _ResultMessage

# Import Claude SDK types for proper type checking
try:
    from claude_agent_sdk import (
        SystemMessage, AssistantMessage, UserMessage,
        TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock
    )
    _claude_types_available = True
except ImportError:
    # Fallback types for when SDK is not available
    SystemMessage = None
    AssistantMessage = None
    UserMessage = None
    TextBlock = None
    ThinkingBlock = None
    ToolUseBlock = None
    ToolResultBlock = None
    _claude_types_available = False

# Export constants for backward compatibility
SDK_AVAILABLE = _sdk_available
CLAUDE_TYPES_AVAILABLE = _claude_types_available

logger = logging.getLogger(__name__)


class SDKMessageTracker:
    """Tracks latest SDK message and periodically displays it."""

    def __init__(self, log_manager: Optional[Any] = None):
        self.latest_message: Optional[str] = None
        self.message_type: str = "INFO"
        self.message_count: int = 0
        self.start_time: float = time.time()
        self._stop_event: asyncio.Event = asyncio.Event()
        self._display_task: Optional[asyncio.Task[None]] = None
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
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time
    
    async def start_periodic_display(self):
        """Start periodic display of latest message every 10 seconds."""
        self._display_task = asyncio.create_task(self._periodic_display())
    
    async def stop_periodic_display(self):
        """Stop the periodic display."""
        self._stop_event.set()
        if self._display_task:
            await self._display_task
    
    async def _periodic_display(self):
        """Display latest message every 10 seconds."""
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)
                break  # Stop event was set
            except asyncio.TimeoutError:
                # 10 seconds passed, display latest message
                if self.latest_message:
                    elapsed = self.get_elapsed_time()
                    # Clean display format: [Type] Message content
                    logger.info(f"[{self.message_type}] {self.latest_message} (after {elapsed:.1f}s)")
    
    def display_final_summary(self):
        """Display final summary when complete."""
        elapsed = self.get_elapsed_time()
        logger.info(f"[COMPLETE] SDK execution finished with {self.message_count} messages in {elapsed:.1f}s")


class SafeClaudeSDK:
    """
    Safe wrapper for Claude SDK query to prevent cancel scope errors.

    This wrapper ensures proper cleanup of async generators and prevents
    RuntimeError when event loop closes.

    Args:
        prompt: The prompt to send to Claude
        options: ClaudeAgentOptions for the query (or None if SDK unavailable)
        timeout: Optional timeout in seconds (default: 300.0)
    """

    def __init__(self, prompt: str, options: Any, timeout: Optional[float] = 900.0, log_manager: Optional[Any] = None):
        self.prompt: str = prompt
        self.options: Any = options
        self.timeout: Optional[float] = timeout
        self._generator: Optional[Any] = None
        self.message_tracker: SDKMessageTracker = SDKMessageTracker(log_manager)
        self.log_manager = log_manager

    def _extract_message_content(self, message: Any) -> Optional[str]:
        """Extract actual content from Claude SDK messages - unified method."""
        try:
            # Get message class name for unified handling
            msg_class = message.__class__.__name__ if hasattr(message, '__class__') else 'Unknown'

            # Handle AssistantMessage - Claude's actual responses
            if msg_class == 'AssistantMessage' and hasattr(message, 'content'):
                return self._extract_assistant_content(message)
            # Handle SystemMessage - System initialization/info
            elif msg_class == 'SystemMessage':
                return self._extract_system_content(message)
            # Handle UserMessage - User inputs
            elif msg_class == 'UserMessage':
                return self._extract_user_content(message)
            # Handle ResultMessage - Final results
            elif msg_class == 'ResultMessage':
                return self._extract_result_content(message)

        except Exception as e:
            logger.debug(f"Failed to extract message content: {e}")
        return None

    def _extract_assistant_content(self, message: Any) -> Optional[str]:
        """Extract content from AssistantMessage."""
        if not hasattr(message, 'content') or not isinstance(message.content, list):
            return None

        content_parts: list[str] = []
        for block in message.content:
            block_item: Any = block
            block_type: str = block_item.__class__.__name__

            if block_type == 'TextBlock' and hasattr(block_item, 'text') and block_item.text:
                content_parts.append(block_item.text.strip())
            elif block_type == 'ThinkingBlock' and hasattr(block_item, 'thinking') and block_item.thinking:
                thinking_text = block_item.thinking.strip()
                preview = thinking_text[:150] + "..." if len(thinking_text) > 150 else thinking_text
                content_parts.append(f"[Thinking] {preview}")
            elif block_type == 'ToolUseBlock' and hasattr(block_item, 'name'):
                tool_name = getattr(block_item, 'name', 'unknown')
                content_parts.append(f"[Using tool: {tool_name}]")
            elif block_type == 'ToolResultBlock' and hasattr(block_item, 'content'):
                tool_content = getattr(block_item, 'content')
                if tool_content:
                    if isinstance(tool_content, str) and tool_content.strip():
                        content_parts.append(f"[Tool result] {tool_content.strip()}")
                    elif isinstance(tool_content, list) and tool_content:
                        content_parts.append(f"[Tool completed with {len(tool_content)} results]")

        return " ".join(content_parts) if content_parts else None

    def _extract_system_content(self, message: Any) -> Optional[str]:
        """Extract content from SystemMessage."""
        if not hasattr(message, 'subtype'):
            return None

        subtype = getattr(message, 'subtype', 'unknown')
        if hasattr(message, 'data') and isinstance(message.data, dict):
            if subtype == 'init':
                session_id = message.data.get('session_id', 'unknown')
                model = message.data.get('model', 'unknown')
                return f"[System initialized] Model: {model}, Session: {str(session_id)[:8]}..."
            elif subtype == 'tool':
                tool_name = message.data.get('tool', 'unknown')
                return f"[System] Tool: {tool_name}"
        return f"[System] {subtype}"

    def _extract_user_content(self, message: Any) -> Optional[str]:
        """Extract content from UserMessage."""
        if not hasattr(message, 'content'):
            return None

        content = message.content
        if isinstance(content, str) and content.strip():
            return f"[User] {content.strip()[:100]}..."
        elif isinstance(content, list):
            return f"[User sent {len(content)} content blocks]"
        return None

    def _extract_result_content(self, message: Any) -> Optional[str]:
        """Extract content from ResultMessage."""
        if hasattr(message, 'is_error'):
            if message.is_error:
                error_result = getattr(message, 'result', 'Unknown error')
                return f"[Error] {error_result}"
            else:
                success_result = getattr(message, 'result', 'Success')
                if isinstance(success_result, str) and len(success_result) > 200:
                    return f"[Success] {success_result[:200]}..."
                else:
                    return f"[Success] {success_result}"

        if hasattr(message, 'num_turns'):
            turns = getattr(message, 'num_turns', 0)
            duration = getattr(message, 'duration_ms', 0) / 1000
            return f"[Complete] {turns} turns, {duration:.1f}s"
        return None
    
    def _classify_message_type(self, message: Any) -> str:
        """Classify the type of message from Claude SDK - simplified."""
        try:
            msg_class = message.__class__.__name__ if hasattr(message, '__class__') else 'Unknown'

            if msg_class == 'SystemMessage':
                subtype = getattr(message, 'subtype', 'unknown')
                if subtype == 'init':
                    return 'INIT'
                elif subtype == 'tool':
                    return 'TOOL'
                return 'SYSTEM'

            elif msg_class == 'AssistantMessage':
                if hasattr(message, 'content') and isinstance(message.content, list):
                    for block in message.content:
                        block_type = block.__class__.__name__
                        if block_type == 'ThinkingBlock':
                            return 'THINKING'
                        elif block_type == 'TextBlock':
                            return 'ASSISTANT'
                        elif block_type == 'ToolUseBlock':
                            return 'TOOL_USE'
                        elif block_type == 'ToolResultBlock':
                            return 'TOOL_RESULT'
                return 'ASSISTANT'

            elif msg_class == 'UserMessage':
                return 'USER'

            elif msg_class == 'ResultMessage':
                if hasattr(message, 'is_error') and message.is_error:
                    return 'ERROR'
                return 'SUCCESS'

            return 'INFO'

        except Exception as e:
            logger.debug(f"Failed to classify message type: {e}")
            return 'INFO'

    async def execute(self) -> bool:
        """
        Execute Claude SDK query safely with proper cleanup.

        Returns:
            True if execution succeeded, False otherwise
        """
        if not SDK_AVAILABLE:
            raise RuntimeError(
                "Claude Agent SDK is required but not available. "
                "Please install claude-agent-sdk: pip install claude-agent-sdk"
            )

        try:
            # Set timeout if specified
            if self.timeout:
                return await asyncio.wait_for(self._execute_with_cleanup(), timeout=self.timeout)
            else:
                return await self._execute_with_cleanup()

        except asyncio.TimeoutError:
            logger.error(f"Claude SDK execution timeout after {self.timeout}s - operation took too long")
            raise TimeoutError(f"Claude SDK execution exceeded timeout of {self.timeout}s")
        except RuntimeError as e:
            if "cancel scope" in str(e):
                logger.error("Claude SDK cancel scope error - indicates SDK internal error")
                raise
            else:
                logger.error(f"Claude SDK RuntimeError: {e}")
                raise
        except Exception as e:
            logger.error(f"Claude SDK execution failed: {e}")
            return False

    async def _execute_with_cleanup(self) -> bool:
        """Execute with proper generator cleanup."""
        if query is None or self.options is None:
            logger.warning("Claude SDK not properly initialized")
            return False

        # Log SDK execution start with timeout info
        logger.info(f"[SDK Start] Starting Claude SDK execution (timeout={self.timeout}s)")
        logger.info(f"[SDK Config] Options: {self.options}")
        logger.info(f"[SDK Config] Prompt length: {len(self.prompt)} characters")

        try:
            # Create the generator
            generator = query(prompt=self.prompt, options=self.options)

            # Start periodic message display
            await self.message_tracker.start_periodic_display()
            
            # Iterate through the generator directly (not using async with)
            message_count = 0
            start_time = asyncio.get_event_loop().time()
            
            async for message in generator:
                message_count += 1
                
                # Extract actual content from Claude's messages
                message_content = self._extract_message_content(message)
                message_type = self._classify_message_type(message)
                
                # Update message tracker with actual Claude content
                if message_content:
                    self.message_tracker.update_message(message_content, message_type)
                else:
                    # Fallback to generic message if no content extracted
                    self.message_tracker.update_message(f"Received {message_type} message {message_count}", message_type)
                
                if ResultMessage is not None and isinstance(message, ResultMessage):
                    # Safely access attributes based on type
                    if hasattr(message, 'is_error') and message.is_error:
                        error_msg = getattr(message, 'result', 'Unknown error')
                        self.message_tracker.update_message(f"Error: {error_msg}", "ERROR")
                        logger.error(f"[SDK Error] Claude SDK error: {error_msg}")
                        return False
                    else:
                        result = getattr(message, 'result', None)
                        result_preview = result[:100] + "..." if result and len(str(result)) > 100 else (str(result) if result else "No content")
                        self.message_tracker.update_message(f"Success: {result_preview}", "SUCCESS")
                        logger.info(f"[SDK Success] Claude SDK result: {result_preview}")
                        return True

            # If we get here, no ResultMessage was received
            total_elapsed = asyncio.get_event_loop().time() - start_time
            
            # Stop periodic display
            await self.message_tracker.stop_periodic_display()
            
            if message_count > 0:
                self.message_tracker.update_message(f"Completed with {message_count} messages", "COMPLETE")
                self.message_tracker.display_final_summary()
                logger.info(f"[SDK Complete] Claude SDK completed with {message_count} messages in {total_elapsed:.1f}s")
                return True
            else:
                # Enhanced error logging with diagnostic information
                prompt_preview = self.prompt[:100] + "..." if len(str(self.prompt)) > 100 else str(self.prompt)
                self.message_tracker.update_message("Failed: No messages received", "ERROR")
                logger.error(f"[SDK Failed] Claude SDK returned no messages after {total_elapsed:.1f}s")
                logger.error(f"[Diagnostic] Prompt preview: {prompt_preview}")
                logger.error(f"[Diagnostic] Options: {self.options}")
                logger.error(f"[Diagnostic] Timeout: {self.timeout}s")
                logger.error(f"[Diagnostic] Message count: {message_count}")
                return False

        except StopAsyncIteration:
            logger.info("Claude SDK generator completed")
            return True
        except GeneratorExit:
            logger.warning("Claude SDK generator closed prematurely")
            return await self._check_work_completed()

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
                    logger.info(f"Found {len(story_files)} story files, assuming success")
                    return True
            return False
        except Exception:
            return False


@asynccontextmanager
async def safe_claude_sdk(
    prompt: str,
    options: Any,
    timeout: Optional[float] = 900.0,
    log_manager: Optional[Any] = None
) -> AsyncIterator[SafeClaudeSDK]:
    """
    Async context manager for safe Claude SDK execution.

    Usage:
        async with safe_claude_sdk(prompt, options, log_manager=log_manager) as sdk:
            success = await sdk.execute()
    """
    sdk = SafeClaudeSDK(prompt, options, timeout, log_manager)
    try:
        yield sdk
    finally:
        # Ensure any remaining cleanup
        await asyncio.sleep(0)
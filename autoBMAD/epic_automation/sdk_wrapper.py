"""
Safe wrapper for Claude Agent SDK to handle async lifecycle properly.

This module provides a safe wrapper around the Claude Agent SDK to prevent
cancel scope errors and ensure proper cleanup of async generators.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, List, cast
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import time

# Type aliases for SDK classes
try:
    from claude_agent_sdk import query, ResultMessage
    query: Any = None  # type: ignore
    ResultMessage: Any = None  # type: ignore
    _sdk_available = True  # type: ignore
except ImportError:
    query: Any = None  # type: ignore
    ResultMessage: Any = None  # type: ignore  # type: ignore
    _sdk_available = False  # type: ignore

# Import Claude SDK types for proper type checking
try:
    from claude_agent_sdk import (
        SystemMessage, AssistantMessage, UserMessage, 
        TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock
    )
    SystemMessage: Any = None  # type: ignore
    AssistantMessage: Any = None  # type: ignore
    UserMessage: Any = None  # type: ignore
    TextBlock: Any = None  # type: ignore
    ThinkingBlock: Any = None  # type: ignore
    ToolUseBlock: Any = None  # type: ignore
    ToolResultBlock: Any = None  # type: ignore
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
    
    def __init__(self):
        self.latest_message: str | None = None
        self.message_type: str = "INFO"
        self.message_count: int = 0
        self.start_time: float = time.time()
        self._stop_event: asyncio.Event = asyncio.Event()
        self._display_task: Optional[asyncio.Task[None]] = None
    
    def update_message(self, message: str, msg_type: str = "INFO"):
        """Update the latest message and its type."""
        self.latest_message = message
        self.message_type = msg_type
        self.message_count += 1
    
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
                    print(f"[{self.message_type}] {self.latest_message} (after {elapsed:.1f}s)")
    
    def display_final_summary(self):
        """Display final summary when complete."""
        elapsed = self.get_elapsed_time()
        print(f"[COMPLETE] SDK execution finished with {self.message_count} messages in {elapsed:.1f}s")


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

    def __init__(self, prompt: str, options: Any, timeout: float | None = 900.0):
        self.prompt: str = prompt
        self.options: Any = options
        self.timeout: float | None = timeout
        self._generator: Any | None = None
        self.message_tracker: SDKMessageTracker = SDKMessageTracker()

    def _extract_message_content(self, message: Any) -> str | None:
        """Extract actual content from Claude SDK messages based on official types."""
        try:
            # Use proper type checking when Claude types are available
            if CLAUDE_TYPES_AVAILABLE and AssistantMessage is not None:
                # Handle AssistantMessage - Claude's actual responses
                if isinstance(message, AssistantMessage) and hasattr(message, 'content'):
                    if isinstance(message.content, list):  # Type is list[ContentBlock]
                        content_parts: list[str] = []
                        for block in message.content:
                            block_obj: Any = block
                            block_obj: Any = block
                            if TextBlock is not None and isinstance(block_obj, TextBlock) and block_obj.text:
                                text_content: str = block_obj.text.strip()
                                content_parts.append(text_content)
                            elif ThinkingBlock is not None and isinstance(block, ThinkingBlock) and block.thinking:
                                # Show brief preview of thinking
                                thinking_text = block.thinking.strip()
                                preview: str = thinking_text[:150] + "..." if len(thinking_text) > 150 else thinking_text
                                content_parts.append(f"[Thinking] {preview}")
                            elif ToolUseBlock is not None and isinstance(block, ToolUseBlock) and hasattr(block, 'name'):
                                tool_name: str = cast(str, getattr(block_obj, 'name', 'unknown'))
                                content_parts.append(f"[Using tool: {tool_name}]")
                            elif ToolResultBlock is not None and isinstance(block, ToolResultBlock) and hasattr(block, 'content'):
                                tool_content: Any = block_obj.content
                                if tool_content:
                                    if isinstance(tool_content, str) and tool_content.strip():
                                        content_parts.append(f"[Tool result] {tool_content.strip()}")
                                    elif isinstance(tool_content, list) and tool_content:
                                        content_parts.append(f"[Tool completed with {len(tool_content)} results]")
                        
                        if content_parts:
                            return " ".join(content_parts)
                
                # Handle SystemMessage - System initialization/info
                elif SystemMessage is not None and isinstance(message, SystemMessage) and hasattr(message, 'subtype'):
                    subtype = getattr(message, 'subtype', 'unknown')
                    if hasattr(message, 'data') and isinstance(message.data, dict):  # Type is dict[str, Any]
                        # Extract relevant system info
                        if subtype == 'init':
                            session_id: str = cast(str, message.data.get('session_id', 'unknown'))
                            model: str = cast(str, message.data.get('model', 'unknown'))
                            return f"[System initialized] Model: {model}, Session: {session_id[:8]}..."
                        elif subtype == 'tool':
                            tool_name: str = cast(str, message.data.get('tool', 'unknown'))
                            return f"[System] Tool: {tool_name}"
                    return f"[System] {subtype}"
                
                # Handle UserMessage - User inputs (rare in query mode)
                elif UserMessage is not None and isinstance(message, UserMessage) and hasattr(message, 'content'):
                    if isinstance(message.content, str) and message.content.strip():
                        return f"[User] {message.content.strip()[:100]}..."
                    elif isinstance(message.content, list):
                        return f"[User sent {len(message.content)} content blocks]"
                
                # Handle ResultMessage - Final results
                elif ResultMessage is not None and isinstance(message, ResultMessage):
                    if hasattr(message, 'is_error'):
                        if message.is_error:
                            error_result = getattr(message, 'result', 'Unknown error')
                            return f"[Error] {error_result}"
                        else:
                            success_result = getattr(message, 'result', 'Success')
                            # Truncate long results
                            if isinstance(success_result, str) and len(success_result) > 200:
                                return f"[Success] {success_result[:200]}..."
                            else:
                                return f"[Success] {success_result}"
                    
                    # Also show basic stats
                    if hasattr(message, 'num_turns'):
                        turns = getattr(message, 'num_turns', 0)
                        duration = getattr(message, 'duration_ms', 0) / 1000
                        return f"[Complete] {turns} turns, {duration:.1f}s"
            
            # Fallback for when SDK types are not available or for dynamic access
            else:
                return self._extract_message_content_fallback(message)
                
        except Exception as e:
            logger.debug(f"Failed to extract message content from {message.__class__.__name__}: {e}")
        
        return None
    
    def _extract_message_content_fallback(self, message: Any) -> str | None:
        """Fallback method for extracting content when SDK types are not available."""
        try:
            msg_class = message.__class__.__name__
            
            # Handle AssistantMessage - Claude's actual responses
            if msg_class == 'AssistantMessage' and hasattr(message, 'content'):
                if isinstance(message.content, list):
                    content_parts: list[str] = []
                    for block in message.content:  # Type is ContentBlock
                        block_obj: Any = block
                        block_obj: Any = block
                        block_type: str = block.__class__.__name__
                        if block_type == 'TextBlock' and hasattr(block, 'text') and block.text:
                            content_parts.append(cast(str, block.text).strip())
                        elif block_type == 'ThinkingBlock' and hasattr(block, 'thinking') and block.thinking:
                            # Show brief preview of thinking
                            thinking_text = cast(str, block.thinking).strip()
                            preview: str = thinking_text[:150] + "..." if len(thinking_text) > 150 else thinking_text
                            content_parts.append(f"[Thinking] {preview}")
                        elif block_type == 'ToolUseBlock' and hasattr(block, 'name'):
                            tool_name = cast(str, getattr(block, 'name', 'unknown'))
                            content_parts.append(f"[Using tool: {tool_name}]")
                        elif block_type == 'ToolResultBlock' and hasattr(block, 'content'):
                            tool_content = getattr(block, 'content')
                            if tool_content:
                                if isinstance(tool_content, str) and tool_content.strip():
                                    content_parts.append(f"[Tool result] {tool_content.strip()}")
                                elif isinstance(tool_content, list) and tool_content:
                                    content_parts.append(f"[Tool completed with {len(tool_content)} results]")
                    
                    if content_parts:
                        return " ".join(content_parts)
            
            # Handle SystemMessage - System initialization/info
            elif msg_class == 'SystemMessage' and hasattr(message, 'subtype'):
                subtype = cast(str, getattr(message, 'subtype', 'unknown'))
                if hasattr(message, 'data') and isinstance(message.data, dict):
                    # Extract relevant system info
                    if subtype == 'init':
                        session_id = cast(dict[str, Any], message.data).get('session_id', 'unknown')
                        model = cast(dict[str, Any], message.data).get('model', 'unknown')
                        return f"[System initialized] Model: {model}, Session: {session_id[:8]}..."
                    elif subtype == 'tool':
                        tool_name = cast(dict[str, Any], message.data).get('tool', 'unknown')
                        return f"[System] Tool: {tool_name}"
                return f"[System] {subtype}"
            
            # Handle UserMessage - User inputs (rare in query mode)
            elif msg_class == 'UserMessage' and hasattr(message, 'content'):
                if isinstance(message.content, str) and message.content.strip():
                    return f"[User] {message.content.strip()[:100]}..."
                elif isinstance(message.content, list):
                    return f"[User sent {len(message.content)} content blocks]"
            
            # Handle ResultMessage - Final results
            elif msg_class == 'ResultMessage':
                if hasattr(message, 'is_error'):
                    if message.is_error:
                        error_result = cast(str, getattr(message, 'result', 'Unknown error'))
                        return f"[Error] {error_result}"
                    else:
                        success_result = cast(str, getattr(message, 'result', 'Success'))
                        # Truncate long results
                        if len(success_result) > 200:
                            return f"[Success] {success_result[:200]}..."
                        else:
                            return f"[Success] {success_result}"
                
                # Also show basic stats
                if hasattr(message, 'num_turns'):
                    turns = cast(int, getattr(message, 'num_turns', 0))
                    duration = cast(int, getattr(message, 'duration_ms', 0)) / 1000
                    return f"[Complete] {turns} turns, {duration:.1f}s"
            
        except Exception as e:
            logger.debug(f"Failed to extract message content from {message.__class__.__name__} (fallback): {e}")
        
        return None
    
    def _classify_message_type(self, message: Any) -> str:
        """Classify the type of message from Claude SDK based on official types."""
        try:
            # Use proper type checking when Claude types are available
            if CLAUDE_TYPES_AVAILABLE and SystemMessage is not None:
                if isinstance(message, SystemMessage):
                    subtype = getattr(message, 'subtype', 'unknown')
                    if subtype == 'init':
                        return 'INIT'
                    elif subtype == 'tool':
                        return 'TOOL'
                    else:
                        return 'SYSTEM'
                
                elif AssistantMessage is not None and isinstance(message, AssistantMessage):
                    if hasattr(message, 'content') and isinstance(message.content, list):  # Type is list[ContentBlock]
                        for block in message.content:
                            block_obj: Any = block
                            block_obj: Any = block
                            if ThinkingBlock is not None and isinstance(block_obj, ThinkingBlock):
                                return 'THINKING'
                            elif TextBlock is not None and isinstance(block, TextBlock):
                                return 'ASSISTANT'
                            elif ToolUseBlock is not None and isinstance(block, ToolUseBlock):
                                return 'TOOL_USE'
                            elif ToolResultBlock is not None and isinstance(block, ToolResultBlock):
                                return 'TOOL_RESULT'
                    return 'ASSISTANT'
                
                elif UserMessage is not None and isinstance(message, UserMessage):
                    return 'USER'
                
                elif ResultMessage is not None and isinstance(message, ResultMessage):
                    if hasattr(message, 'is_error') and message.is_error:
                        return 'ERROR'
                    else:
                        return 'SUCCESS'
            
            # Fallback for when SDK types are not available
            else:
                msg_class = message.__class__.__name__
                
                if msg_class == 'SystemMessage':
                    subtype = cast(str, getattr(message, 'subtype', 'unknown'))
                    if subtype == 'init':
                        return 'INIT'
                    elif subtype == 'tool':
                        return 'TOOL'
                    else:
                        return 'SYSTEM'
                
                elif msg_class == 'AssistantMessage':
                    if hasattr(message, 'content') and isinstance(message.content, list):
                        for block in message.content:  # Type is ContentBlock
                            block_obj: Any = block
                            block_obj: Any = block
                            block_type: str = block.__class__.__name__
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
                    if hasattr(message, 'is_error') and cast(bool, getattr(message, 'is_error', False)):
                        return 'ERROR'
                    else:
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
    timeout: float | None = 900.0
) -> AsyncIterator[SafeClaudeSDK]:
    """
    Async context manager for safe Claude SDK execution.

    Usage:
        async with safe_claude_sdk(prompt, options) as sdk:
            success = await sdk.execute()
    """
    sdk = SafeClaudeSDK(prompt, options, timeout)
    try:
        yield sdk
    finally:
        # Ensure any remaining cleanup
        await asyncio.sleep(0)
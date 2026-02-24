"""
Kimi Session Manager Module

Provides a high-level wrapper around the Kimi Agent SDK Session API for agent interactions.
This module enables agents to interact with Kimi K2.5 through the SDK with proper session
management, exception handling, and structured logging.

Example:
    >>> from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
    >>> from kaos.path import KaosPath
    >>>
    >>> async with KimiSessionManager(work_dir=KaosPath.cwd()) as manager:
    ...     session = await manager.create_session(mode="agent", yolo=True)
    ...     messages = await manager.single_prompt("Hello, Kimi!")
"""

from __future__ import annotations

import os
import types
from pathlib import Path
from typing import Any

import structlog
from kaos.path import KaosPath
from kimi_agent_sdk import (
    ApprovalHandlerFn,
    ChatProviderError,
    Config,
    ConfigError,
    InvalidToolError,
    MaxStepsReached,
    Message,
    RunCancelled,
    Session,
    WireMessage,
)
from kimi_agent_sdk._aggregator import MessageAggregator

from autoBMAD.docuswarm.exceptions import ConfigurationError, LLMError

# Type alias for the config parameter
type ConfigParam = Any  # Config | Path | None

# Structured logger for this module
logger: structlog.BoundLogger = structlog.get_logger(__name__)


class KimiSessionManager:
    """
    Manages Kimi Agent SDK sessions for DocuSwarm agents.

    This class provides a high-level interface to create, resume, and manage
    Kimi K2.5 sessions through the SDK. It handles:
    - Session lifecycle (create, resume, close)
    - Exception mapping (SDK -> DocuSwarm exceptions)
    - Active session tracking
    - Structured logging for all operations

    Attributes:
        work_dir: Working directory for sessions (KaosPath).
        agent_file: Optional path to agent specification file.
        config: Optional configuration object or path.

    Example:
        >>> from kaos.path import KaosPath
        >>> from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
        >>>
        >>> async with KimiSessionManager(work_dir=KaosPath.cwd()) as manager:
        ...     # Create a new session
        ...     session = await manager.create_session(mode="agent", yolo=True)
        ...     # Or use single prompt for quick interactions
        ...     messages = await manager.single_prompt("What is 2+2?")
    """

    def __init__(
        self,
        work_dir: KaosPath,
        agent_file: Path | None = None,
        config: ConfigParam = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """
        Initialize the KimiSessionManager.

        Args:
            work_dir: Working directory for sessions (KaosPath).
            agent_file: Optional path to agent specification file.
            config: Optional configuration object or path to config file.
            api_key: Optional Kimi API key (from .env or environment).
            base_url: Optional Kimi API base URL (from .env or environment).
        """
        self._work_dir = work_dir
        self._agent_file = agent_file

        # Build SDK Config if api_key and/or base_url are provided
        if config is None and (api_key or base_url):
            # Read from environment as fallback
            effective_api_key = api_key or os.environ.get("KIMI_API_KEY", "")
            # Fix: base_url must include /v1
            effective_base_url = base_url or os.environ.get(
                "KIMI_BASE_URL", "https://api.kimi.com/coding/v1"
            )
            # Fix: use correct model name from environment or default
            effective_model = os.environ.get("KIMI_MODEL_NAME", "kimi-for-coding")

            # Create SDK Config object
            config = Config(
                providers={
                    effective_model: {
                        "type": "kimi",
                        "base_url": effective_base_url,
                        "api_key": effective_api_key,
                    }
                },
                models={
                    effective_model: {
                        "provider": effective_model,
                        "model": effective_model,
                        "max_context_size": int(
                            os.environ.get("KIMI_MODEL_MAX_CONTEXT_SIZE", "262144")
                        ),
                    }
                },
                default_model=effective_model,
            )

        self._config = config
        self._active_sessions: dict[str, Session] = {}
        self._logger = logger.bind(
            component="KimiSessionManager",
            work_dir=str(work_dir),
            agent_file=str(agent_file) if agent_file else None,
        )

    @property
    def work_dir(self) -> KaosPath:
        """Get the working directory."""
        return self._work_dir

    @property
    def agent_file(self) -> Path | None:
        """Get the agent file path."""
        return self._agent_file

    @property
    def config(self) -> ConfigParam:
        """Get the configuration."""
        return self._config

    async def create_session(
        self,
        mode: str = "agent",
        yolo: bool = True,
        max_steps: int | None = None,
        agent_file: Path | None = None,
        approval_handler_fn: ApprovalHandlerFn | None = None,
    ) -> Session:
        """
        Create a new Kimi session.

        Args:
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls (True for IndependentAgent).
            max_steps: Maximum steps per turn (optional).
            agent_file: Optional path to agent specification file. Overrides the
                agent_file set in the constructor if provided.
            approval_handler_fn: Optional approval handler callback for custom
                approval logic. If provided and yolo=False, this handler will
                be used instead of the default prompt-based approval.

        Returns:
            Session: A new SDK Session object.

        Raises:
            LLMError: On SDK errors (ChatProviderError, ConfigError, etc.).
            PromptValidationError: If neither yolo nor approval_handler_fn is provided.
        """
        try:
            self._logger.info(
                "creating_session",
                mode=mode,
                yolo=yolo,
                max_steps=max_steps,
            )

            # Map mode to SDK parameters
            # Fix: use environment variable or default to kimi-for-coding
            model = os.environ.get("KIMI_MODEL_NAME", "kimi-for-coding")
            thinking = False
            if mode == "thinking":
                thinking = True

            # Build kwargs for Session.create
            create_kwargs: dict[str, Any] = {
                "work_dir": self._work_dir,
                "model": model,
                "yolo": yolo,
            }

            # Use per-session agent_file if provided, otherwise fall back to constructor value
            effective_agent_file = agent_file if agent_file is not None else self._agent_file
            if effective_agent_file:
                create_kwargs["agent_file"] = effective_agent_file

            if self._config:
                create_kwargs["config"] = self._config

            if max_steps is not None:
                create_kwargs["max_steps_per_turn"] = max_steps

            if thinking:
                create_kwargs["thinking"] = True

            # Add approval handler if provided (only used when yolo=False)
            if approval_handler_fn is not None:
                create_kwargs["approval_handler_fn"] = approval_handler_fn

            session = await Session.create(**create_kwargs)

            # Track the session
            self._active_sessions[session.id] = session

            self._logger.info(
                "session_created",
                session_id=session.id,
                mode=mode,
            )

            return session

        except ChatProviderError as e:
            self._logger.error("session_creation_failed", error=str(e))
            raise LLMError(
                f"Failed to create session: {e}",
                api_error_type="ChatProviderError",
            ) from e

        except ConfigError as e:
            self._logger.error("session_config_error", error=str(e))
            raise ConfigurationError(
                f"SDK configuration error: {e}",
                config_source="kimi_agent_sdk",
            ) from e

        except Exception as e:
            self._logger.error("session_creation_error", error=str(e))
            raise LLMError(
                f"Failed to create session: {e}",
            ) from e

    async def resume_session(self, session_id: str | None = None) -> Session | None:
        """
        Resume an existing session.

        Args:
            session_id: Session ID to resume. If None, resumes the most recent.

        Returns:
            Session | None: The resumed session, or None if not found.

        Raises:
            LLMError: On SDK errors.
        """
        try:
            self._logger.info("resuming_session", session_id=session_id)

            session = await Session.resume(
                work_dir=self._work_dir,
                session_id=session_id,
                config=self._config,
                agent_file=self._agent_file,
            )

            if session is None:
                self._logger.warning("session_not_found", session_id=session_id)
                return None

            # Track the session
            self._active_sessions[session.id] = session

            self._logger.info(
                "session_resumed",
                session_id=session.id,
            )

            return session

        except ChatProviderError as e:
            self._logger.error("session_resume_failed", error=str(e))
            raise LLMError(
                f"Failed to resume session: {e}",
                api_error_type="ChatProviderError",
            ) from e

        except ConfigError as e:
            self._logger.error("session_resume_config_error", error=str(e))
            raise ConfigurationError(
                f"SDK configuration error: {e}",
                config_source="kimi_agent_sdk",
            ) from e

        except Exception as e:
            self._logger.error("session_resume_error", error=str(e))
            raise LLMError(
                f"Failed to resume session: {e}",
            ) from e

    async def resume_or_create(
        self,
        session_id: str | None = None,
        mode: str = "agent",
        yolo: bool = True,
        max_steps: int | None = None,
        approval_handler_fn: ApprovalHandlerFn | None = None,
    ) -> Session:
        """
        Resume an existing session or create a new one.

        This method first attempts to resume an existing session using the provided
        session_id. If the session is not found (returns None), it creates a fresh
        session with the same session_id. This ensures pipeline continuity after
        interruption.

        Args:
            session_id: Session ID to resume. If None, attempts resume then creates new.
            mode: Session mode ("instant", "thinking", or "agent") for new session.
            yolo: Whether to auto-approve tool calls for new session.
            max_steps: Maximum steps per turn for new session.
            approval_handler_fn: Optional approval handler callback for custom
                approval logic. Only used when creating a new session.

        Returns:
            Session: The resumed or newly created session.

        Raises:
            LLMError: On SDK errors.
        """
        # First try to resume the session
        session = await self.resume_session(session_id)

        if session is not None:
            self._logger.info(
                "session_resume_success",
                session_id=session.id,
                mode=mode,
            )
            return session

        # Session not found - log and create new one
        self._logger.warning(
            "session_not_found_creating_new",
            session_id=session_id,
            requested_mode=mode,
        )

        # Create new session
        new_session = await self.create_session(
            mode=mode,
            yolo=yolo,
            max_steps=max_steps,
            approval_handler_fn=approval_handler_fn,
        )

        # Log the fallback creation
        self._logger.info(
            "session_fallback_created",
            original_session_id=session_id,
            new_session_id=new_session.id,
            mode=mode,
        )

        return new_session

    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
    ) -> list[Message]:
        """
        Execute a single prompt and return messages (one-shot API).

        This is a convenience method for quick interactions without managing
        the session explicitly. Useful for EvaluatorAgent and other agents
        that need simple prompt/response without session persistence.

        Args:
            prompt: The prompt to send.
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls.

        Returns:
            list[Message]: List of Message objects from the response.
            Returns empty list if execution is cancelled.
            Returns partial messages if max steps reached.

        Raises:
            LLMError: On SDK errors (ChatProviderError, etc.).
            ConfigurationError: On SDK configuration errors.
        """
        self._logger.info("single_prompt_start", prompt_length=len(prompt), mode=mode)

        session: Session | None = None
        aggregator: MessageAggregator = MessageAggregator()
        try:
            # Create a temporary session
            session = await self.create_session(mode=mode, yolo=yolo)

            # Collect messages from the prompt using aggregator
            messages: list[Message] = []
            message_count = 0
            tool_call_count = 0
            wire_msg: WireMessage

            try:
                async for wire_msg in session.prompt(prompt):
                    message_count += 1
                    # Log progress for each wire message
                    role = getattr(wire_msg, "role", "unknown")

                    # Track tool calls for progress indication
                    tool_calls: list[Any] | None = getattr(wire_msg, "tool_calls", None)
                    if tool_calls:
                        tool_call_count += len(tool_calls)
                        self._logger.info(
                            "llm_tool_call",
                            message_index=message_count,
                            tool_count=len(tool_calls),
                            total_tools=tool_call_count,
                        )
                    elif role == "assistant":
                        # Log assistant response progress
                        text_preview = ""
                        extract_text_method = getattr(wire_msg, "extract_text", None)
                        if extract_text_method:
                            text: str = extract_text_method()
                            text_preview = text[:80] + "..." if len(text) > 80 else text
                        self._logger.debug(
                            "llm_response_chunk",
                            message_index=message_count,
                            role=role,
                            preview=text_preview,
                        )

                    # Use MessageAggregator to convert WireMessages to Messages
                    msgs = aggregator.feed(wire_msg)
                    messages.extend(msgs)
            except MaxStepsReached:
                # Return partial messages when max steps reached
                self._logger.warning(
                    "single_prompt_max_steps",
                    partial_message_count=len(messages),
                )
                return aggregator.flush()

            # Flush any remaining buffered messages
            final_messages = aggregator.flush()
            if final_messages:
                messages.extend(final_messages)

            self._logger.info(
                "single_prompt_complete",
                message_count=len(messages),
                wire_messages=message_count,
                tool_calls=tool_call_count,
            )

            return messages

        except ChatProviderError as e:
            self._logger.error("single_prompt_failed", error=str(e))
            raise LLMError(
                f"Single prompt failed: {e}",
                api_error_type="ChatProviderError",
            ) from e

        except RunCancelled:
            # Graceful handling - not an error, return empty list
            self._logger.info("single_prompt_cancelled")
            return []

        except ConfigurationError:
            # Re-raise ConfigurationError as-is (from create_session)
            raise

        except ConfigError as e:
            self._logger.error("single_prompt_config_error", error=str(e))
            raise ConfigurationError(
                f"SDK configuration error: {e}",
                config_source="kimi_agent_sdk",
            ) from e

        except InvalidToolError as e:
            # Log tool error details for debugging, then raise as LLMError
            self._logger.error(
                "single_prompt_invalid_tool",
                tool_name=getattr(e, "tool_name", "unknown"),
                error=str(e),
            )
            raise LLMError(
                f"Invalid tool error: {e}",
                api_error_type="InvalidToolError",
            ) from e

        except Exception as e:
            self._logger.error("single_prompt_error", error=str(e))
            raise LLMError(
                f"Single prompt failed: {e}",
            ) from e

        finally:
            # Clean up the temporary session
            if session is not None:
                await session.close()
                if session.id in self._active_sessions:
                    del self._active_sessions[session.id]

    async def close_all(self) -> None:
        """
        Close all active sessions.

        This method ensures all tracked sessions are properly closed and
        resources are released. Called automatically when exiting the
        async context manager.

        Example:
            >>> manager = KimiSessionManager(work_dir=KaosPath.cwd())
            >>> await manager.create_session(mode="agent")
            >>> await manager.create_session(mode="thinking")
            >>> await manager.close_all()  # Closes both sessions
        """
        self._logger.info(
            "closing_all_sessions",
            session_count=len(self._active_sessions),
        )

        # Close all tracked sessions
        for session_id, session in list(self._active_sessions.items()):
            try:
                await session.close()
                self._logger.debug("session_closed", session_id=session_id)
            except Exception as e:
                self._logger.error(
                    "session_close_error",
                    session_id=session_id,
                    error=str(e),
                )

        # Clear the active sessions dict
        self._active_sessions.clear()

        self._logger.info("all_sessions_closed")

    def get_active(self, session_id: str) -> Session | None:
        """
        Get an active session by ID.

        This method retrieves a currently tracked session for cancellation
        or inspection purposes (Story 9.4: Native Cancellation Integration).

        Args:
            session_id: The session ID to retrieve.

        Returns:
            Session | None: The session if found and active, None otherwise.
        """
        session = self._active_sessions.get(session_id)
        if session is not None:
            self._logger.debug("session_found_for_cancellation", session_id=session_id)
        else:
            self._logger.debug("session_not_found_for_cancellation", session_id=session_id)
        return session

    def get_active_session_ids(self) -> list[str]:
        """
        Get list of all active session IDs.

        Returns:
            list[str]: List of active session IDs.
        """
        return list(self._active_sessions.keys())

    async def __aenter__(self) -> KimiSessionManager:
        """
        Async context manager entry.

        Returns:
            KimiSessionManager: The manager instance.
        """
        self._logger.debug("context_manager_enter")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """
        Async context manager exit.

        Ensures all sessions are properly closed on exit.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Traceback if an exception was raised.
        """
        self._logger.debug("context_manager_exit", exc_type=exc_type)
        await self.close_all()


# Define public API
__all__ = [
    "KimiSessionManager",
]

"""
Remote Debugger

Provides high-level remote debugging functionality with session management,
async support, and integration with the BUGFIX_20260107 framework.
"""

import asyncio
import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Awaitable, Tuple

from .debugpy_server import DebugpyServer
from .debug_client import AsyncDebugClient, get_async_debug_client

T = TypeVar('T')


@dataclass
class DebugSession:
    """
    Represents a debugging session.

    Attributes:
        session_id: Unique identifier for the session
        name: Human-readable name for the session
        start_time: Session start timestamp
        active: Whether the session is currently active
        breakpoints: List of breakpoints set in this session
        events: List of debug events (breakpoints, exceptions, etc.)
        metadata: Additional session metadata
    """

    session_id: str
    name: str
    start_time: float
    active: bool = True
    breakpoints: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebugEvent:
    """
    Represents a debug event.

    Attributes:
        event_type: Type of event (breakpoint, exception, pause, etc.)
        timestamp: Event timestamp
        session_id: ID of the session that generated the event
        data: Event-specific data
        source_location: Source code location if applicable
    """

    event_type: str
    timestamp: float
    session_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    source_location: Optional[Dict[str, Any]] = None


class RemoteDebugger:
    """
    High-level remote debugger with session management.

    This class provides a high-level interface for remote debugging,
    including session management, async support, and integration with
    the BUGFIX_20260107 framework.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        server: Optional[DebugpyServer] = None,
        client: Optional[AsyncDebugClient] = None
    ):
        """
        Initialize the remote debugger.

        Args:
            config: Configuration dictionary
            server: Optional pre-configured DebugpyServer
            client: Optional pre-configured AsyncDebugClient
        """
        self.config = config or {}
        self.server = server or DebugpyServer(self.config.get("debugpy", {}))
        self.client = client or get_async_debug_client(
            host=self.config.get("host", "127.0.0.1"),
            port=self.config.get("port", 5678)
        )
        self.logger = logging.getLogger("remote_debugger")

        # Session management
        self._sessions: Dict[str, DebugSession] = {}
        self._active_session: Optional[str] = None
        self._event_handlers: Dict[str, List[Callable[[DebugEvent], Awaitable[None]]]] = {}

        # Statistics
        self.stats: Dict[str, Any] = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_breakpoints": 0,
            "total_events": 0,
            "sessions_created": []
        }

        # Auto-start server if configured
        if self.config.get("auto_start_server", True):
            asyncio.create_task(self._ensure_server_running())

    async def _ensure_server_running(self) -> None:
        """Ensure the debugpy server is running."""
        if not self.server.is_active():
            self.logger.info("Auto-starting debugpy server...")
            await self.server.start()

    @asynccontextmanager
    async def debug_session(
        self,
        name: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create and manage a debug session.

        Args:
            name: Human-readable name for the session
            session_id: Optional custom session ID
            metadata: Optional session metadata

        Example:
            async with debugger.debug_session("my_operation") as session:
                await debugger.set_breakpoint("file.py", 10)
                result = await some_async_operation()
        """
        session_id = session_id or str(uuid.uuid4())
        start_time = time.time()

        # Create session
        session = DebugSession(
            session_id=session_id,
            name=name,
            start_time=start_time,
            metadata=metadata or {}
        )

        self._sessions[session_id] = session
        self._active_session = session_id
        self.stats["total_sessions"] += 1
        self.stats["active_sessions"] += 1
        self.stats["sessions_created"].append({
            "session_id": session_id,
            "name": name,
            "timestamp": start_time
        })

        self.logger.info(f"Created debug session: {name} ({session_id})")

        try:
            yield session

        except Exception as e:
            # Log error event
            await self._log_event(
                DebugEvent(
                    event_type="exception",
                    timestamp=time.time(),
                    session_id=session_id,
                    data={
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "exception_traceback": self._format_exception(e)
                    }
                )
            )
            raise

        finally:
            # Cleanup session
            session.active = False
            duration = time.time() - start_time

            self.stats["active_sessions"] -= 1
            self.logger.info(
                f"Debug session ended: {name} ({session_id}, "
                f"duration: {duration:.2f}s)"
            )

            if self._active_session == session_id:
                self._active_session = None

    async def set_breakpoint(
        self,
        file: str,
        line: int,
        session_id: Optional[str] = None,
        condition: Optional[str] = None,
        hit_count: Optional[int] = None
    ) -> bool:
        """
        Set a breakpoint.

        Args:
            file: Path to the source file
            line: Line number for the breakpoint
            session_id: Optional session ID (uses active session if not provided)
            condition: Optional condition for the breakpoint
            hit_count: Optional hit count for the breakpoint

        Returns:
            True if breakpoint set successfully, False otherwise
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return False

        try:
            # Set breakpoint via client
            success = await self.client.set_breakpoint(
                file=file,
                line=line,
                condition=condition,
                hit_count=hit_count
            )

            if success:
                # Record breakpoint in session
                breakpoint_info = {
                    "file": file,
                    "line": line,
                    "condition": condition,
                    "hit_count": hit_count,
                    "set_at": time.time(),
                    "triggered": False
                }

                self._sessions[session_id].breakpoints.append(breakpoint_info)
                self.stats["total_breakpoints"] += 1

                self.logger.info(
                    f"Breakpoint set at {file}:{line} "
                    f"(session: {session_id})"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error setting breakpoint: {e}", exc_info=True)
            return False

    async def remove_breakpoint(
        self,
        file: str,
        line: int,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Remove a breakpoint.

        Args:
            file: Path to the source file
            line: Line number of the breakpoint
            session_id: Optional session ID

        Returns:
            True if breakpoint removed successfully, False otherwise
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return False

        try:
            success = await self.client.remove_breakpoint(file, line)

            if success:
                # Remove from session
                session = self._sessions[session_id]
                session.breakpoints = [
                    bp for bp in session.breakpoints
                    if not (bp["file"] == file and bp["line"] == line)
                ]

                self.logger.info(
                    f"Breakpoint removed from {file}:{line} "
                    f"(session: {session_id})"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error removing breakpoint: {e}", exc_info=True)
            return False

    async def evaluate_expression(
        self,
        expression: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Evaluate an expression in the debugged context.

        Args:
            expression: Python expression to evaluate
            session_id: Optional session ID
            **kwargs: Additional arguments for AsyncDebugClient.evaluate_expression

        Returns:
            Evaluation result or None if failed
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return None

        try:
            result = await self.client.evaluate_expression(expression, **kwargs)

            self.logger.debug(f"Evaluated expression: {expression}")
            return result

        except Exception as e:
            self.logger.error(f"Error evaluating expression: {e}", exc_info=True)
            return None

    async def pause(self, session_id: Optional[str] = None) -> bool:
        """
        Pause the debugged program.

        Args:
            session_id: Optional session ID

        Returns:
            True if pause command sent successfully, False otherwise
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return False

        try:
            success = await self.client.pause()

            if success:
                await self._log_event(
                    DebugEvent(
                        event_type="pause",
                        timestamp=time.time(),
                        session_id=session_id,
                        data={"reason": "manual"}
                    )
                )

            return success

        except Exception as e:
            self.logger.error(f"Error pausing: {e}", exc_info=True)
            return False

    async def continue_execution(self, session_id: Optional[str] = None) -> bool:
        """
        Continue program execution.

        Args:
            session_id: Optional session ID

        Returns:
            True if continue command sent successfully, False otherwise
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return False

        try:
            success = await self.client.continue_execution()

            if success:
                await self._log_event(
                    DebugEvent(
                        event_type="continue",
                        timestamp=time.time(),
                        session_id=session_id,
                        data={}
                    )
                )

            return success

        except Exception as e:
            self.logger.error(f"Error continuing: {e}", exc_info=True)
            return False

    async def get_stack_trace(
        self,
        session_id: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get the stack trace from the debugged program.

        Args:
            session_id: Optional session ID

        Returns:
            List of stack frames or None if failed
        """
        session_id = session_id or self._active_session

        if not session_id or session_id not in self._sessions:
            self.logger.error("No active debug session")
            return None

        try:
            stack_trace = await self.client.get_async_stack_trace()
            return stack_trace

        except Exception as e:
            self.logger.error(f"Error getting stack trace: {e}", exc_info=True)
            return None

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable[[DebugEvent], Awaitable[None]]
    ) -> None:
        """
        Register an event handler for debug events.

        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered event handler for {event_type}")

    async def _log_event(self, event: DebugEvent) -> None:
        """
        Log a debug event.

        Args:
            event: DebugEvent to log
        """
        # Add event to session
        if event.session_id in self._sessions:
            from dataclasses import asdict
            self._sessions[event.session_id].events.append(asdict(event))

        # Update statistics
        self.stats["total_events"] += 1

        # Call registered handlers
        if event.event_type in self._event_handlers:
            for handler in self._event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}", exc_info=True)

        # Log event
        self.logger.debug(f"Debug event: {event.event_type}")

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session info or None if session not found
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        return {
            "session_id": session.session_id,
            "name": session.name,
            "start_time": session.start_time,
            "active": session.active,
            "duration": time.time() - session.start_time,
            "breakpoint_count": len(session.breakpoints),
            "event_count": len(session.events),
            "metadata": session.metadata
        }

    def list_sessions(self) -> List[Optional[Dict[str, Any]]]:
        """
        List all sessions.

        Returns:
            List of session summaries
        """
        return [
            self.get_session_info(session_id)
            for session_id in self._sessions
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get debugger statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    async def close_all_sessions(self) -> None:
        """Close all active sessions."""
        self.logger.info(f"Closing {len(self._sessions)} sessions...")

        for session_id in list(self._sessions.keys()):
            session = self._sessions[session_id]
            if session.active:
                session.active = False
                self.stats["active_sessions"] -= 1

        self.logger.info("All sessions closed")

    def _format_exception(self, exception: Exception) -> str:
        """Format an exception for logging."""
        import traceback
        return "".join(traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__
        ))

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_server_running()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_all_sessions()

    def __repr__(self) -> str:
        """String representation of the debugger."""
        return (
            f"RemoteDebugger("
            f"sessions={len(self._sessions)}, "
            f"active={self.stats['active_sessions']}, "
            f"server={self.server.is_active()}"
            f")"
        )


class AsyncDebugDecorator:
    """
    Decorator for adding debugging to async functions.

    This class can be used to decorate async functions and automatically
    add debugging capabilities, including breakpoints, logging, and
    performance monitoring.
    """

    def __init__(
        self,
        debugger: RemoteDebugger,
        session_name: Optional[str] = None,
        breakpoints: Optional[List[Tuple[str, int]]] = None
    ):
        """
        Initialize the decorator.

        Args:
            debugger: RemoteDebugger instance
            session_name: Optional session name (uses function name if not provided)
            breakpoints: Optional list of (file, line) tuples for breakpoints
        """
        self.debugger = debugger
        self.session_name = session_name
        self.breakpoints = breakpoints or []

    def __call__(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """
        Decorate an async function.

        Args:
            func: Async function to decorate

        Returns:
            Decorated async function
        """
        async def wrapper(*args, **kwargs):
            session_name = self.session_name or func.__name__

            async with self.debugger.debug_session(session_name) as session:
                # Set breakpoints
                for file, line in self.breakpoints:
                    await self.debugger.set_breakpoint(file, line)

                # Execute function
                result = await func(*args, **kwargs)

                return result

        return wrapper

    def breakpoint(self, file: str, line: int):
        """
        Add a breakpoint to be set when the decorated function is called.

        Args:
            file: Path to the source file
            line: Line number for the breakpoint
        """
        self.breakpoints.append((file, line))


# Global remote debugger instance
_remote_debugger: Optional[RemoteDebugger] = None


def get_remote_debugger(
    config: Optional[Dict[str, Any]] = None
) -> RemoteDebugger:
    """
    Get the global remote debugger instance.

    Args:
        config: Optional configuration

    Returns:
        Global RemoteDebugger instance
    """
    global _remote_debugger
    if _remote_debugger is None:
        _remote_debugger = RemoteDebugger(config)
    return _remote_debugger


def debug_async(
    session_name_param: Optional[str] = None,
    breakpoints: Optional[List[Tuple[str, int]]] = None
):
    """
    Decorator for adding debugging to async functions.

    Args:
        session_name_param: Optional session name
        breakpoints: Optional list of (file, line) tuples for breakpoints

    Example:
        @debug_async("my_function", breakpoints=[("file.py", 10)])
        async def my_function():
            pass
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        debugger = get_remote_debugger()

        async def wrapper(*args, **kwargs):
            session_name = session_name_param or func.__name__

            async with debugger.debug_session(session_name) as session:
                # Set breakpoints
                for file, line in breakpoints or []:
                    await debugger.set_breakpoint(file, line)

                # Execute function
                result = await func(*args, **kwargs)

                return result

        return wrapper

    return decorator

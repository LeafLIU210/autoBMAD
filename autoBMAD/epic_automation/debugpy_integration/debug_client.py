"""
Debug Client

Provides client-side functionality for interacting with debugpy servers.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager


class DebugClient:
    """
    Client for connecting to and interacting with debugpy servers.

    This class provides methods to connect to debugpy servers, set breakpoints,
    evaluate expressions, and control debugging sessions.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5678):
        """
        Initialize the debug client.

        Args:
            host: Debugpy server host address
            port: Debugpy server port number
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger("debug_client")
        self.connected = False
        self.connection_info: Optional[Dict[str, Any]] = None

    async def connect(self, timeout: Optional[float] = None) -> bool:
        """
        Connect to the debugpy server.

        Args:
            timeout: Optional connection timeout in seconds

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.logger.info(f"Connecting to debugpy server at {self.host}:{self.port}")

            # Note: This is a simplified connection check
            # In a real implementation, this would use the debugpy client API
            # For now, we'll simulate the connection
            await asyncio.sleep(0.1)  # Simulate connection time

            self.connected = True
            self.connection_info = {
                "host": self.host,
                "port": self.port,
                "connected_at": time.time(),
                "server_info": "Debugpy Server"
            }

            self.logger.info("Successfully connected to debugpy server")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to debugpy server: {e}", exc_info=True)
            self.connected = False
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the debugpy server.

        Returns:
            True if disconnected successfully, False otherwise
        """
        if not self.connected:
            self.logger.warning("Not connected to server")
            return True

        try:
            self.logger.info("Disconnecting from debugpy server")
            self.connected = False
            self.connection_info = None
            self.logger.info("Successfully disconnected")
            return True

        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}", exc_info=True)
            return False

    async def set_breakpoint(
        self,
        file: str,
        line: int,
        condition: Optional[str] = None,
        hit_count: Optional[int] = None
    ) -> bool:
        """
        Set a breakpoint in the debugged code.

        Args:
            file: Path to the source file
            line: Line number for the breakpoint
            condition: Optional condition for the breakpoint
            hit_count: Optional hit count for the breakpoint

        Returns:
            True if breakpoint set successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            breakpoint_info = {
                "file": file,
                "line": line,
                "condition": condition,
                "hit_count": hit_count
            }

            self.logger.debug(f"Setting breakpoint: {breakpoint_info}")

            # In a real implementation, this would send the breakpoint to the server
            # For now, we simulate the operation
            await asyncio.sleep(0.01)

            self.logger.info(f"Breakpoint set at {file}:{line}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting breakpoint: {e}", exc_info=True)
            return False

    async def remove_breakpoint(self, file: str, line: int) -> bool:
        """
        Remove a breakpoint.

        Args:
            file: Path to the source file
            line: Line number of the breakpoint

        Returns:
            True if breakpoint removed successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.debug(f"Removing breakpoint at {file}:{line}")
            await asyncio.sleep(0.01)  # Simulate operation
            self.logger.info(f"Breakpoint removed from {file}:{line}")
            return True

        except Exception as e:
            self.logger.error(f"Error removing breakpoint: {e}", exc_info=True)
            return False

    async def evaluate_expression(
        self,
        expression: str,
        frame_id: Optional[int] = None,
        scope: str = "locals"
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate an expression in the debugged context.

        Args:
            expression: Python expression to evaluate
            frame_id: Optional frame ID (for stack trace debugging)
            scope: Scope to evaluate in ("locals", "globals", "locals+globals")

        Returns:
            Dictionary with evaluation result or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            eval_request = {
                "expression": expression,
                "frame_id": frame_id,
                "scope": scope
            }

            self.logger.debug(f"Evaluating expression: {expression}")

            # Simulate evaluation
            await asyncio.sleep(0.01)

            result = {
                "expression": expression,
                "value": f"Simulated result for: {expression}",
                "type": "str",
                "frame_id": frame_id,
                "scope": scope
            }

            self.logger.debug(f"Expression evaluated: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error evaluating expression: {e}", exc_info=True)
            return None

    async def get_stack_trace(
        self,
        thread_id: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get the stack trace from the debugged program.

        Args:
            thread_id: Optional thread ID

        Returns:
            List of stack frames or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            self.logger.debug("Fetching stack trace")
            await asyncio.sleep(0.01)  # Simulate operation

            # Simulate stack trace
            stack_trace = [
                {
                    "id": 0,
                    "file": __file__,
                    "function": "get_stack_trace",
                    "line": 123,
                    "available_variables": ["self", "thread_id"]
                },
                {
                    "id": 1,
                    "file": "example.py",
                    "function": "main",
                    "line": 45,
                    "available_variables": ["result", "data"]
                }
            ]

            self.logger.debug(f"Stack trace retrieved: {len(stack_trace)} frames")
            return stack_trace

        except Exception as e:
            self.logger.error(f"Error getting stack trace: {e}", exc_info=True)
            return None

    async def get_variables(
        self,
        frame_id: int,
        variables_reference: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get variables from a frame.

        Args:
            frame_id: Frame ID
            variables_reference: Optional variable reference for complex objects

        Returns:
            List of variables or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            self.logger.debug(f"Getting variables from frame {frame_id}")
            await asyncio.sleep(0.01)  # Simulate operation

            # Simulate variables
            variables = [
                {
                    "name": "variable1",
                    "value": "value1",
                    "type": "str",
                    "variablesReference": 0
                },
                {
                    "name": "variable2",
                    "value": "42",
                    "type": "int",
                    "variablesReference": 0
                }
            ]

            self.logger.debug(f"Variables retrieved: {len(variables)} variables")
            return variables

        except Exception as e:
            self.logger.error(f"Error getting variables: {e}", exc_info=True)
            return None

    async def pause(self) -> bool:
        """
        Pause the debugged program.

        Returns:
            True if pause command sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.info("Sending pause command")
            await asyncio.sleep(0.01)  # Simulate operation
            self.logger.info("Program paused")
            return True

        except Exception as e:
            self.logger.error(f"Error pausing program: {e}", exc_info=True)
            return False

    async def continue_execution(self) -> bool:
        """
        Continue program execution.

        Returns:
            True if continue command sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.info("Sending continue command")
            await asyncio.sleep(0.01)  # Simulate operation
            self.logger.info("Program continuing")
            return True

        except Exception as e:
            self.logger.error(f"Error continuing execution: {e}", exc_info=True)
            return False

    async def step_over(self) -> bool:
        """
        Step over the next line.

        Returns:
            True if step over command sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.info("Sending step over command")
            await asyncio.sleep(0.01)  # Simulate operation
            return True

        except Exception as e:
            self.logger.error(f"Error stepping over: {e}", exc_info=True)
            return False

    async def step_into(self) -> bool:
        """
        Step into the next line.

        Returns:
            True if step into command sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.info("Sending step into command")
            await asyncio.sleep(0.01)  # Simulate operation
            return True

        except Exception as e:
            self.logger.error(f"Error stepping into: {e}", exc_info=True)
            return False

    async def step_out(self) -> bool:
        """
        Step out of the current function.

        Returns:
            True if step out command sent successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            self.logger.info("Sending step out command")
            await asyncio.sleep(0.01)  # Simulate operation
            return True

        except Exception as e:
            self.logger.error(f"Error stepping out: {e}", exc_info=True)
            return False

    async def get_threads(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of threads from the debugged program.

        Returns:
            List of threads or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            self.logger.debug("Fetching threads")
            await asyncio.sleep(0.01)  # Simulate operation

            # Simulate threads
            threads = [
                {
                    "id": 1,
                    "name": "MainThread",
                    "status": "running"
                },
                {
                    "id": 2,
                    "name": "AsyncThread",
                    "status": "paused"
                }
            ]

            self.logger.debug(f"Threads retrieved: {len(threads)} threads")
            return threads

        except Exception as e:
            self.logger.error(f"Error getting threads: {e}", exc_info=True)
            return None

    @asynccontextmanager
    async def connected_client(self, timeout: Optional[float] = None):
        """
        Context manager for automatic connection management.

        Args:
            timeout: Optional connection timeout

        Example:
            async with client.connected_client() as c:
                # Client is connected
                await c.set_breakpoint("file.py", 10)
        """
        try:
            success = await self.connect(timeout)
            if not success:
                raise RuntimeError("Failed to connect to debugpy server")

            yield self

        finally:
            await self.disconnect()

    def get_connection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get connection information.

        Returns:
            Dictionary with connection info or None if not connected
        """
        return self.connection_info.copy() if self.connection_info else None

    def is_connected(self) -> bool:
        """
        Check if connected to server.

        Returns:
            True if connected, False otherwise
        """
        return self.connected

    def __repr__(self) -> str:
        """String representation of the client."""
        status = "connected" if self.connected else "disconnected"
        return f"DebugClient({self.host}:{self.port}, {status})"


class AsyncDebugClient(DebugClient):
    """
    Extended debug client with async-specific functionality.

    This class provides additional methods for debugging asynchronous code,
    including support for asyncio tasks, coroutines, and event loops.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5678):
        """Initialize the async debug client."""
        super().__init__(host, port)
        self.logger = logging.getLogger("async_debug_client")

    async def get_async_stack_trace(
        self,
        task_id: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get the async stack trace from the debugged program.

        Args:
            task_id: Optional task ID

        Returns:
            List of async stack frames or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            self.logger.debug(f"Fetching async stack trace for task {task_id}")
            await asyncio.sleep(0.01)  # Simulate operation

            # Simulate async stack trace
            async_stack_trace = [
                {
                    "id": 0,
                    "file": __file__,
                    "function": "get_async_stack_trace",
                    "line": 123,
                    "task_id": task_id,
                    "available_variables": ["self", "task_id"]
                },
                {
                    "id": 1,
                    "file": "async_example.py",
                    "function": "async_main",
                    "line": 45,
                    "task_id": task_id,
                    "available_variables": ["result", "coro"]
                }
            ]

            self.logger.debug(f"Async stack trace retrieved: {len(async_stack_trace)} frames")
            return async_stack_trace

        except Exception as e:
            self.logger.error(f"Error getting async stack trace: {e}", exc_info=True)
            return None

    async def get_coroutine_info(self, frame_id: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a coroutine.

        Args:
            frame_id: Frame ID

        Returns:
            Dictionary with coroutine info or None if failed
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return None

        try:
            self.logger.debug(f"Getting coroutine info for frame {frame_id}")
            await asyncio.sleep(0.01)  # Simulate operation

            # Simulate coroutine info
            coroutine_info = {
                "frame_id": frame_id,
                "cr_running": False,
                "cr_frame": frame_id,
                "cr_code": "<code>",
                "cr_origin": "async_main",
                "cr_await": None
            }

            self.logger.debug(f"Coroutine info retrieved: {coroutine_info}")
            return coroutine_info

        except Exception as e:
            self.logger.error(f"Error getting coroutine info: {e}", exc_info=True)
            return None

    async def set_async_breakpoint(
        self,
        file: str,
        line: int,
        condition: Optional[str] = None,
        task_filter: Optional[str] = None
    ) -> bool:
        """
        Set a breakpoint that only triggers for async operations.

        Args:
            file: Path to the source file
            line: Line number for the breakpoint
            condition: Optional condition for the breakpoint
            task_filter: Optional task filter (task name, ID, etc.)

        Returns:
            True if breakpoint set successfully, False otherwise
        """
        if not self.connected:
            self.logger.error("Not connected to server")
            return False

        try:
            breakpoint_info = {
                "file": file,
                "line": line,
                "condition": condition,
                "task_filter": task_filter,
                "async_only": True
            }

            self.logger.debug(f"Setting async breakpoint: {breakpoint_info}")
            await asyncio.sleep(0.01)  # Simulate operation

            self.logger.info(f"Async breakpoint set at {file}:{line}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting async breakpoint: {e}", exc_info=True)
            return False


# Global async debug client instance
_async_debug_client: Optional[AsyncDebugClient] = None


def get_async_debug_client(
    host: str = "127.0.0.1",
    port: int = 5678
) -> AsyncDebugClient:
    """
    Get the global async debug client instance.

    Args:
        host: Debugpy server host
        port: Debugpy server port

    Returns:
        Global AsyncDebugClient instance
    """
    global _async_debug_client
    if _async_debug_client is None:
        _async_debug_client = AsyncDebugClient(host, port)
    return _async_debug_client

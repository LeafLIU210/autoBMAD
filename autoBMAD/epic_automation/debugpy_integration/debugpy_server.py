"""
Debugpy Server Manager

Provides centralized management of debugpy remote debugging servers.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from contextlib import asynccontextmanager

try:
    import debugpy
except ImportError:
    debugpy = None


class DebugpyServer:
    """
    Manages debugpy remote debugging server instances.

    This class provides functionality to start, stop, and manage debugpy
    servers for remote debugging of asynchronous operations.
    """

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 5678
    DEFAULT_CONFIG = {
        "server": {
            "host": DEFAULT_HOST,
            "port": DEFAULT_PORT,
            "wait_for_client": True,
            "log_to_file": True
        },
        "features": {
            "async_debugging": True,
            "multiprocess": True,
            "Breakpoints": True,
            "property_evalupd": True
        },
        "logging": {
            "level": "DEBUG",
            "file": "debugpy_server.log"
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DebugpyServer.

        Args:
            config: Optional configuration dictionary. If None, uses DEFAULT_CONFIG.
        """
        self.config = config or self.DEFAULT_CONFIG.copy()
        self.logger = self._setup_logging()
        self.server_info: Optional[Dict[str, Any]] = None
        self._active = False

        if debugpy is None:
            self.logger.warning(
                "debugpy not installed. Remote debugging will be disabled. "
                "Install with: pip install debugpy"
            )

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("debugpy_server")
        logger.setLevel(
            logging.DEBUG if self.config.get("logging", {}).get("level") == "DEBUG"
            else logging.INFO
        )

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Also log to file if configured
        if self.config.get("logging", {}).get("file"):
            log_file_path = str(self.config["logging"]["file"])
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    async def start(self, host: Optional[str] = None, port: Optional[int] = None) -> bool:
        """
        Start the debugpy server.

        Args:
            host: Optional host address. Defaults to config or 127.0.0.1
            port: Optional port number. Defaults to config or 5678

        Returns:
            True if server started successfully, False otherwise
        """
        if debugpy is None:
            self.logger.error("Cannot start server: debugpy not installed")
            return False

        if self._active:
            self.logger.warning("Server already active")
            return True

        # Use provided host/port or config defaults
        server_config = self.config.get("server", {})
        host_value = server_config.get("host", self.DEFAULT_HOST)
        host = host if host is not None else (str(host_value) if host_value else self.DEFAULT_HOST)

        port_value = server_config.get("port", self.DEFAULT_PORT)
        port = port if port is not None else (int(port_value) if port_value else self.DEFAULT_PORT)

        try:
            self.logger.info(f"Starting debugpy server on {host}:{port}")

            # Configure debugpy
            debugpy.listen((host, port))

            # Store server info
            self.server_info = {
                "host": host,
                "port": port,
                "started_at": time.time(),
                "pid": self._get_process_id()
            }

            # Wait for client if configured
            if server_config.get("wait_for_client", True):
                self.logger.info(
                    f"Waiting for debugger to attach on {host}:{port}..."
                )
                if debugpy is not None:
                    debugpy.wait_for_client()
                    self.logger.info("Debugger attached successfully")

            self._active = True
            self.logger.info("Debugpy server started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start debugpy server: {e}", exc_info=True)
            self._active = False
            return False

    async def stop(self) -> bool:
        """
        Stop the debugpy server.

        Returns:
            True if server stopped successfully, False otherwise
        """
        if not self._active:
            self.logger.warning("Server not active")
            return True

        try:
            self.logger.info("Stopping debugpy server...")

            # Debugpy doesn't have an explicit stop method
            # The server will be stopped when the Python process exits
            # We just mark it as inactive
            self._active = False

            if self.server_info:
                duration = time.time() - self.server_info["started_at"]
                self.logger.info(
                    f"Server stopped (active for {duration:.2f} seconds)"
                )

            return True

        except Exception as e:
            self.logger.error(f"Error stopping debugpy server: {e}", exc_info=True)
            return False

    def is_active(self) -> bool:
        """
        Check if the server is active.

        Returns:
            True if server is active, False otherwise
        """
        return self._active

    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """
        Get server information.

        Returns:
            Dictionary with server info or None if server not started
        """
        return self.server_info.copy() if self.server_info else None

    def breakpoint(self) -> None:
        """
        Set a breakpoint in the code.

        This will pause execution when reached if a debugger is attached.
        """
        if debugpy and self._active:
            try:
                debugpy.breakpoint()
                self.logger.debug("Breakpoint triggered")
            except Exception as e:
                self.logger.error(f"Error setting breakpoint: {e}")

    async def wait_for_client(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for a debugger client to attach.

        Args:
            timeout: Optional timeout in seconds. None means wait indefinitely.

        Returns:
            True if client attached, False if timeout
        """
        if not self._active:
            self.logger.error("Server not active")
            return False

        try:
            if debugpy is not None:
                if timeout:
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, debugpy.wait_for_client
                        ),
                        timeout=timeout
                    )
                else:
                    debugpy.wait_for_client()

                self.logger.info("Debugger client attached")
            else:
                self.logger.warning("debugpy not available")
            return True

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for client after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for client: {e}", exc_info=True)
            return False

    def _get_process_id(self) -> int:
        """
        Get the current process ID.

        Returns:
            Process ID as an integer
        """
        try:
            return __import__("os").getpid()
        except Exception:
            return 0

    @asynccontextmanager
    async def managed_server(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Context manager for automatic server lifecycle management.

        Args:
            host: Optional host address
            port: Optional port number

        Example:
            async with server.managed_server() as s:
                # Server is running
                await some_async_operation()
            # Server is automatically stopped
        """
        try:
            success = await self.start(host, port)
            if not success:
                raise RuntimeError("Failed to start debugpy server")

            yield self

        finally:
            await self.stop()

    def __repr__(self) -> str:
        """String representation of the server."""
        status = "active" if self._active else "inactive"
        host = self.server_info.get("host", "N/A") if self.server_info else "N/A"
        port = self.server_info.get("port", "N/A") if self.server_info else "N/A"
        return f"DebugpyServer({host}:{port}, {status})"


class DebugpyServerManager:
    """
    Manager for multiple debugpy server instances.

    This class manages multiple debugpy servers, each on different ports,
    for multiprocess debugging scenarios.
    """

    def __init__(self):
        """Initialize the server manager."""
        self.servers: Dict[int, DebugpyServer] = {}
        self.logger = logging.getLogger("debugpy_server_manager")

    async def start_server(
        self,
        port: int,
        host: str = DebugpyServer.DEFAULT_HOST,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[DebugpyServer]:
        """
        Start a new debugpy server on the specified port.

        Args:
            port: Port number for the server
            host: Host address (default: 127.0.0.1)
            config: Optional configuration

        Returns:
            DebugpyServer instance or None if failed
        """
        if port in self.servers:
            self.logger.warning(f"Server already exists on port {port}")
            return self.servers[port]

        server = DebugpyServer(config)
        success = await server.start(host, port)

        if success:
            self.servers[port] = server
            self.logger.info(f"Started server on {host}:{port}")
            return server
        else:
            self.logger.error(f"Failed to start server on {host}:{port}")
            return None

    async def stop_server(self, port: int) -> bool:
        """
        Stop a debugpy server on the specified port.

        Args:
            port: Port number of the server to stop

        Returns:
            True if stopped successfully, False otherwise
        """
        if port not in self.servers:
            self.logger.warning(f"No server found on port {port}")
            return True

        server = self.servers[port]
        success = await server.stop()

        if success:
            del self.servers[port]
            self.logger.info(f"Stopped server on port {port}")

        return success

    async def stop_all(self) -> None:
        """Stop all managed servers."""
        self.logger.info(f"Stopping {len(self.servers)} servers...")
        for port in list(self.servers.keys()):
            await self.stop_server(port)
        self.logger.info("All servers stopped")

    def get_server(self, port: int) -> Optional[DebugpyServer]:
        """
        Get a server by port.

        Args:
            port: Port number

        Returns:
            DebugpyServer instance or None
        """
        return self.servers.get(port)

    def list_servers(self) -> Dict[int, Optional[Dict[str, Any]]]:
        """
        List all managed servers.

        Returns:
            Dictionary mapping port to server info
        """
        return {
            port: server.get_server_info()
            for port, server in self.servers.items()
        }


# Global server manager instance
_server_manager = DebugpyServerManager()


def get_server_manager() -> DebugpyServerManager:
    """
    Get the global server manager instance.

    Returns:
        Global DebugpyServerManager instance
    """
    return _server_manager

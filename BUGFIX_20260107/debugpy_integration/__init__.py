"""
DEBUGPY INTEGRATION MODULE

Provides remote debugging capabilities using debugpy for the BUGFIX_20260107 framework.
"""

from .debugpy_server import DebugpyServer
from .debug_client import DebugClient
from .remote_debugger import RemoteDebugger

__all__ = [
    "DebugpyServer",
    "DebugClient",
    "RemoteDebugger"
]

__version__ = "1.0.0"

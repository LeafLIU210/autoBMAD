"""Tool registry re-export for backward compatibility.

DEPRECATED: Use autoBMAD.docuswarm.tools.tool_registry directly.
This module will be removed in a future version.
"""

from __future__ import annotations

import warnings

from autoBMAD.docuswarm.tools.tool_registry import (
    ToolDefinition,
    ToolRegistry,
    get_tool_registry,
    list_registered_tools,
    register_tool,
)
from autoBMAD.docuswarm.tools.tool_result import ToolResult

# Emit deprecation warning on import
warnings.warn(
    "models.tool_registry is deprecated. Use tools.tool_registry instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "ToolResult",
    "get_tool_registry",
    "list_registered_tools",
    "register_tool",
]

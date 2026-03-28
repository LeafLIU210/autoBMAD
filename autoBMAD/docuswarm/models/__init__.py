"""Models module for DocuSwarm.

DEPRECATED: This module re-exports from tools for backward compatibility.
Use autoBMAD.docuswarm.tools directly instead.
"""

from __future__ import annotations

import warnings
from typing import Any


def __getattr__(name: str) -> Any:
    """Lazy import with deprecation warning.
    
    This function is called when an attribute is accessed on the module.
    It emits a DeprecationWarning and then returns the actual object from tools.
    """
    warnings.warn(
        f"models.{name} is deprecated. Use autoBMAD.docuswarm.tools directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    
    if name == "ToolResult":
        from autoBMAD.docuswarm.tools.tool_result import ToolResult
        return ToolResult
    if name == "ToolRegistry":
        from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
        return ToolRegistry
    
    raise AttributeError(f"module 'models' has no attribute '{name}'")


# __all__ is still needed for IDE autocompletion
__all__ = [
    "ToolResult",
    "ToolRegistry",
]

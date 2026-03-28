"""Tool model for DocuSwarm."""

# Re-export from tools module for backward compatibility
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
from autoBMAD.docuswarm.tools.tool_result import ToolResult

__all__ = ["ToolResult", "ToolRegistry"]

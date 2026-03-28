"""Public API for DocuSwarm.

This module defines the stable public API for DocuSwarm.
All symbols exported here are guaranteed to be backward compatible
across minor version updates.

Recommended import patterns:
    # Import specific types
    from autoBMAD.docuswarm.public_api import PipelineState, ToolRegistry

    # Import the whole public API namespace
    from autoBMAD.docuswarm import public_api

    # Direct submodule imports (for advanced use)
    from autoBMAD.docuswarm.pipeline.state import PipelineState

Note:
    This module is designed to be a stable facade over the internal
    implementation. Internal modules may change, but symbols exported
    here will remain compatible according to semantic versioning.
"""

from __future__ import annotations

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator

# Pipeline - Core workflow types
from autoBMAD.docuswarm.pipeline.state import PipelineState, create_initial_state

# Storage - State management
from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.tools.tool_registry import ToolDefinition, ToolRegistry

# Tools - Tool system types
from autoBMAD.docuswarm.tools.tool_result import ToolResult

__all__ = [
    # Pipeline types
    "PipelineState",
    "create_initial_state",
    "HybridOrchestrator",
    # Storage types
    "StateManager",
    # Tools types
    "ToolResult",
    "ToolRegistry",
    "ToolDefinition",
]

"""Permission classes for DocuSwarm context.

This module re-exports permission classes from nodes.loader for use in context management.
"""

from autoBMAD.nodes.loader import (
    NodeFilePermissions,
    NodeSearchPermissions,
    NodeToolPermissions,
)

# For backwards compatibility and cleaner imports
FilePermissions = NodeFilePermissions
SearchPermissions = NodeSearchPermissions

__all__ = [
    "NodeFilePermissions",
    "NodeSearchPermissions",
    "NodeToolPermissions",
    "FilePermissions",
    "SearchPermissions",
]

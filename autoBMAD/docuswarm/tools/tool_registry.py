"""Unified Tool Registry for DocuSwarm.

This module provides a single, unified tool registration API.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from autoBMAD.docuswarm.tools.tool_result import ToolResult


@dataclass
class ToolDefinition:
    """Definition of a registered tool.

    Attributes:
        name: Tool name
        func: Tool function
        description: Tool description
        schema: Optional JSON schema for the tool parameters
    """

    name: str
    func: Callable[..., ToolResult]
    description: str = ""
    schema: dict[str, Any] | None = None


class ToolRegistry:
    """Unified tool registry for managing tool definitions.

    This is the single source of truth for tool registration.
    All tool registration should go through this class.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        func: Callable[..., ToolResult],
        description: str = "",
        schema: dict[str, Any] | None = None,
    ) -> Callable[..., ToolResult]:
        """Register a tool.

        Args:
            name: Tool name
            func: Tool function
            description: Optional tool description
            schema: Optional JSON schema for parameters

        Returns:
            The registered function
        """
        self._tools[name] = ToolDefinition(
            name=name,
            func=func,
            description=description,
            schema=schema,
        )
        return func

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name.

        Args:
            name: Tool name

        Returns:
            ToolDefinition or None if not found
        """
        return self._tools.get(name)

    def execute(self, name: str, **kwargs: Any) -> ToolResult:
        """Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool execution result
        """
        tool_def = self.get(name)
        if tool_def is None:
            return ToolResult(success=False, error=f"Tool '{name}' not found")
        try:
            result = tool_def.func(**kwargs)
            # Type checker knows result is ToolResult from Callable[..., ToolResult] annotation,
            # but we keep runtime check for safety with potentially misannotated functions
            return (
                result
                if isinstance(cast(object, result), ToolResult)
                else ToolResult(success=True, result=result)
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def list_tools(self) -> list[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def export_schemas(self) -> dict[str, dict[str, Any]]:
        """Export all tool schemas.

        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {name: tool.schema for name, tool in self._tools.items() if tool.schema is not None}

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()


# Global registry instance
_global_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry.

    Returns:
        Global ToolRegistry instance (singleton)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(
    name: str,
    description: str = "",
    schema: dict[str, Any] | None = None,
) -> Callable[[Callable[..., ToolResult]], Callable[..., ToolResult]]:
    """Decorator to register a tool in the global registry.

    Args:
        name: Tool name
        description: Optional tool description
        schema: Optional JSON schema for parameters

    Returns:
        Decorator function

    Example:
        @register_tool(name="my_tool", description="Does something")
        def my_tool(param: str) -> ToolResult:
            ...
    """

    def decorator(func: Callable[..., ToolResult]) -> Callable[..., ToolResult]:
        get_tool_registry().register(name, func, description, schema)
        return func

    return decorator


def list_registered_tools() -> list[str]:
    """List all registered tool names.

    Returns:
        List of tool names from global registry
    """
    return get_tool_registry().list_tools()


__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "list_registered_tools",
]

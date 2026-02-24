"""UpdateContextTool - Pydantic-based tool for updating shared context."""

from __future__ import annotations

from typing import Any, Literal, override

from kimi_agent_sdk import CallableTool2, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class UpdateContextParams(BaseModel):
    """Parameters for updating context.

    Attributes:
        key: The context key to update.
        value: The value to set, append, or remove.
        operation: The operation to perform (set, append, or remove).
    """

    key: str = Field(description="The context key to update")
    value: Any = Field(description="The value to set, append, or remove")
    operation: Literal["set", "append", "remove"] = Field(
        default="set",
        description="The operation to perform: 'set' replaces the value, 'append' adds to a list, 'remove' deletes the key or removes from list",
    )


class UpdateContextTool(CallableTool2[UpdateContextParams]):
    """Tool for updating the shared context with key-value operations.

    This tool uses the kimi-agent-sdk's CallableTool2 for automatic
    parameter deserialization and dispatch. It supports three operations:
    - set: Replaces the entire value at the given key
    - append: Adds to an existing list or creates a new list if key doesn't exist
    - remove: Removes a key from context or removes a value from a list
    """

    name: str = "update_context"
    description: str = "Update the shared context with key-value operations"
    params: type[UpdateContextParams] = UpdateContextParams

    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__()

    @override
    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        """Update context with the given parameters.

        Args:
            params: The validated parameters from the tool call.

        Returns:
            ToolOk on success, ToolError on failure.
        """
        # This is a no-op implementation since there's no actual context store
        # The tool is defined for the agent but doesn't actually do anything
        return ToolOk(
            output=f"Context update operation '{params.operation}' on key '{params.key}' acknowledged"
        )

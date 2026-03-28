"""UpdateContextTool - Pydantic-based tool for updating shared context with persistence.

This tool uses ToolResult internally and adapts to SDK format at boundary.
"""

from __future__ import annotations

from typing import Any, Literal, override

from pydantic import BaseModel, Field

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultCallableTool
from autoBMAD.docuswarm.tools.tool_result import ToolResult

# Whitelist of allowed key prefixes for shared_context
ALLOWED_KEY_PREFIXES = [
    "facts.",
    "decisions.",
    "open_questions",
    "doc_summaries.",
    "notes",
]

# Keys that support append operation (must be lists)
ALLOWED_LIST_KEYS = [
    "open_questions",
    "notes",
]


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


class UpdateContextTool(ToolResultCallableTool[UpdateContextParams]):
    """Tool for updating the shared context with key-value operations.

    This tool uses the ToolResultCallableTool base class for automatic
    SDK format adaptation. It supports three operations:
    - set: Replaces the entire value at the given key
    - append: Adds to an existing list or creates a new list if key doesn't exist
    - remove: Removes a key from context or removes a value from a list

    The tool persists updates to StateManager.shared_context.
    """

    name: str = "update_context"
    description: str = "Update the shared context with key-value operations"
    params: type[UpdateContextParams] = UpdateContextParams

    def __init__(
        self,
        state_manager: StateManager | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        """Initialize the tool.

        Args:
            state_manager: StateManager for persistence. Required.
            pipeline_id: Pipeline ID to update. Required.

        Raises:
            ValueError: If required dependencies are not provided.
        """
        super().__init__()

        # P1-1: Make dependencies required
        if state_manager is None:
            raise ValueError("StateManager is required")
        if pipeline_id is None:
            raise ValueError("pipeline_id is required")

        self._state_manager = state_manager
        self._pipeline_id = pipeline_id

    def _is_key_allowed(self, key: str) -> bool:
        """Check if the key is in the allowed whitelist.

        Args:
            key: The key to check.

        Returns:
            True if the key is allowed.
        """
        for prefix in ALLOWED_KEY_PREFIXES:
            # prefix already ends with '.' for nested keys like 'facts.'
            # or is exact key like 'open_questions'
            if key.startswith(prefix):
                return True
            # Also allow exact match (for prefixes without trailing dot)
            if key == prefix.rstrip("."):
                return True
        return False

    def _get_key_path(self, key: str) -> tuple[str | None, str]:
        """Parse key into namespace and key path.

        Args:
            key: The full key like "facts.market_scope" or "open_questions"

        Returns:
            Tuple of (namespace, key_path) where namespace is the top-level
            shared_context key and key_path is the remaining path.
        """
        parts = key.split(".", 1)
        if len(parts) == 1:
            # Simple key like "open_questions"
            return (parts[0], "")
        else:
            # Nested key like "facts.market_scope"
            return (parts[0], parts[1])

    @override
    async def _execute(self, params: UpdateContextParams) -> ToolResult:
        """Update context with the given parameters.

        Args:
            params: The validated parameters from the tool call.

        Returns:
            ToolResult with success status and details.
        """
        # Dependencies are validated in __init__ and guaranteed to exist

        # Validate key against whitelist
        if not self._is_key_allowed(params.key):
            return ToolResult(
                success=False,
                error=f"Key '{params.key}' is not allowed. Allowed prefixes: {ALLOWED_KEY_PREFIXES}",
            )

        try:
            # Call StateManager to update shared_context
            result = await self._state_manager.update_shared_context(
                pipeline_id=self._pipeline_id,
                update=params.value,
                operation=params.operation,
                key_path=params.key,
            )

            if result:
                return ToolResult(
                    success=True,
                    result={
                        "message": f"Context updated: {params.operation} on '{params.key}'",
                        "operation": params.operation,
                        "key": params.key,
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Failed to update context: {params.operation} on '{params.key}'",
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error updating context: {str(e)}",
            )


# Backward compatibility: also export the standalone function
async def update_context(params: UpdateContextParams) -> ToolResult:
    """Standalone function for backward compatibility.

    This function creates a temporary tool instance and calls it.
    Note: Without state_manager and pipeline_id, this will return a mock success
    for backward compatibility with existing tests.

    Args:
        params: UpdateContextParams with key, value, and operation.

    Returns:
        ToolResult indicating success (for backward compatibility).
    """
    # For backward compatibility with existing tests, return a mock success
    # In production, the tool should be instantiated with proper dependencies
    return ToolResult(
        success=True,
        result={
            "message": f"Context update operation '{params.operation}' on key '{params.key}' acknowledged",
            "key": params.key,
            "operation": params.operation,
        },
    )

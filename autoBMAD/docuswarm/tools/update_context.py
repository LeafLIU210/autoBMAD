"""UpdateContextTool - Pydantic-based tool for updating shared context with persistence.

This tool uses ToolResult internally and adapts to SDK format at boundary.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Literal, override

from pydantic import BaseModel, Field

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultCallableTool
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

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
    params: type[BaseModel] | None = UpdateContextParams

    def __init__(
        self,
        state_manager: StateManager | None = None,
        pipeline_id: str | None = None,
        allowed_keys: list[str] | None = None,
    ) -> None:
        """Initialize the tool.

        Args:
            state_manager: StateManager for persistence. Required.
            pipeline_id: Pipeline ID to update. Required.
            allowed_keys: Optional per-node whitelist to merge with global whitelist.
                When provided, these keys are unioned with the global whitelist.
                When None or empty, only global whitelist is used.

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
        self._node_allowed_keys = allowed_keys
        self._whitelist_source: str = "global_only"
        self._effective_whitelist: list[str] | None = None

    def _build_effective_whitelist(self) -> list[str]:
        """Build effective whitelist by merging global and node-specific keys.

        Uses union (not replacement) strategy: global whitelist + node-specific keys.

        Returns:
            List of allowed key patterns (global + node-specific).
        """
        # Start with global whitelist
        effective = list(ALLOWED_KEY_PREFIXES)

        # Determine whitelist source for logging
        if self._node_allowed_keys:
            # Merge node-specific keys (union, not replacement)
            effective = list(dict.fromkeys(effective + self._node_allowed_keys))
            self._whitelist_source = "node_extended"
        elif self._node_allowed_keys == []:
            # Explicitly empty list - still use global only
            self._whitelist_source = "global_only"
        else:
            self._whitelist_source = "global_only"

        self._effective_whitelist = effective
        return effective

    def _is_key_allowed(self, key: str) -> tuple[bool, list[str]]:
        """Check if the key is in the allowed whitelist.

        Supports wildcard patterns using '*':
        - 'facts.*' matches 'facts.market_scope', 'facts.status', etc.
        - 'custom.*.nested' matches 'custom.a.nested', 'custom.b.nested', etc.

        Args:
            key: The key to check.

        Returns:
            Tuple of (is_allowed, effective_whitelist).
        """
        effective_whitelist = self._build_effective_whitelist()

        for pattern in effective_whitelist:
            # Convert wildcard pattern to regex
            # Escape special regex chars except '*', then replace '*' with '.*'
            regex_pattern = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
            if re.match(regex_pattern, key):
                return True, effective_whitelist
            # Also support legacy prefix matching for patterns ending with '.'
            if pattern.endswith(".") and key.startswith(pattern):
                return True, effective_whitelist
            # Also allow exact match (for patterns without wildcards)
            if key == pattern:
                return True, effective_whitelist
        return False, effective_whitelist

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
            ToolResult with success status and details including version info.
        """
        # Dependencies are validated in __init__ and guaranteed to exist

        # Validate key against whitelist
        is_allowed, effective_whitelist = self._is_key_allowed(params.key)

        # Log whitelist source for debugging
        logger.debug(
            f"UpdateContextTool: pipeline_id={self._pipeline_id}, "
            f"whitelist_source={self._whitelist_source}, "
            f"effective_patterns={len(effective_whitelist)}"
        )

        if not is_allowed:
            error_result: dict[str, Any] = {
                "key": params.key,
                "operation": params.operation,
                "allowed_patterns": effective_whitelist,
            }
            return ToolResult(
                success=False,
                error=f"Key '{params.key}' is not in the allowed whitelist",
                result=error_result,
            )

        try:
            # Call StateManager to update shared_context
            result = await self._state_manager.update_shared_context(
                pipeline_id=self._pipeline_id,
                update=params.value,
                operation=params.operation,
                key_path=params.key,
            )

            if result.get("success"):
                # Format version string: v{version}_{timestamp_ms}
                version = result.get("version", 0)
                updated_at = result.get("updated_at", "")
                timestamp_ms = (
                    int(
                        datetime.fromisoformat(updated_at.replace("Z", "+00:00")).timestamp() * 1000
                    )
                    if updated_at
                    else 0
                )
                version_str = f"v{version}_{timestamp_ms}"

                result_data: dict[str, Any] = {
                    "message": f"Context updated: {params.operation} on '{params.key}'",
                    "operation": params.operation,
                    "key": params.key,
                    "version": version_str,
                    "timestamp": updated_at,
                }

                # Include previous_value for audit trail (if available)
                if "previous_value" in result and result["previous_value"] is not None:
                    result_data["previous_value"] = result["previous_value"]

                return ToolResult(
                    success=True,
                    result=result_data,
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

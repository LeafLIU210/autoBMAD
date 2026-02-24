"""Context filtering module for removing private data before Evaluator input."""

import copy
import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ContextFilter:
    """Filters private data from output before it reaches the Evaluator.

    This is Layer 3 (Message-Level Filtering) in the three-layer isolation architecture.
    Works in conjunction with ContextManager (Layer 2) and Prompt Separation (Layer 1).
    """

    # Private field names to remove from output
    FIELDS_TO_REMOVE: list[str] = [
        "private_reasoning",
        "tool_call_history",
        "internal_notes",
        "iteration_feedback",
    ]

    # Private markers to remove from string content
    MARKERS_TO_REMOVE: list[str] = [
        "[PRIVATE]",
        "[/PRIVATE]",
        "[INTERNAL]",
        "[/INTERNAL]",
        "<!-- PRIVATE -->",
        "<!-- INTERNAL -->",
    ]

    # Critical fields that should still exist after filtering
    CRITICAL_FIELDS: list[str] = [
        "deliverable",
        "questions",
    ]

    def __init__(self) -> None:
        """Initialize the ContextFilter."""
        self._logger = logger.bind(component="ContextFilter")

    def filter_for_evaluator(self, output: dict[str, Any]) -> dict[str, Any]:
        """Filter private data from output before sending to Evaluator.

        Args:
            output: The output dictionary from the Independent Agent.

        Returns:
            A filtered dictionary with private fields removed.
        """
        # Use deep copy to avoid modifying the original
        filtered = copy.deepcopy(output)

        # Remove private fields from top-level
        for field in self.FIELDS_TO_REMOVE:
            if field in filtered:
                del filtered[field]
                self._logger.debug(
                    "removed_top_level_field",
                    field=field,
                )

        # Remove private fields from nested structures
        filtered = self._remove_nested_private(filtered)

        # Remove private markers from string content
        filtered = self._remove_markers(filtered)

        # Validate critical fields still exist
        self._validate_critical_fields(filtered, output)

        self._logger.info(
            "filtering_complete",
            original_keys=list(output.keys()),
            filtered_keys=list(filtered.keys()),
        )

        return filtered

    def _remove_nested_private(self, obj: Any) -> Any:
        """Recursively remove private fields from nested structures.

        Args:
            obj: The object to process (dict, list, or other).

        Returns:
            The object with private fields removed.
        """
        if isinstance(obj, dict):
            # Create new dict without private fields
            result: dict[str, Any] = {}
            for key, value in obj.items():
                if key not in self.FIELDS_TO_REMOVE:
                    result[key] = self._remove_nested_private(value)
            return result
        elif isinstance(obj, list):
            # Process each item in the list
            return [self._remove_nested_private(item) for item in obj]
        else:
            # Return primitives as-is
            return obj

    def _remove_markers(self, obj: Any) -> Any:
        """Remove private markers from string content.

        Args:
            obj: The object to process (can be dict, list, or string).

        Returns:
            The object with markers removed from strings.
        """
        if isinstance(obj, dict):
            return {key: self._remove_markers(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._remove_markers(item) for item in obj]
        elif isinstance(obj, str):
            result = obj
            for marker in self.MARKERS_TO_REMOVE:
                result = result.replace(marker, "")
            # Clean up any extra whitespace from marker removal
            result = re.sub(r"\s+", " ", result).strip()
            return result
        else:
            return obj

    def _validate_critical_fields(self, filtered: dict[str, Any], original: dict[str, Any]) -> None:
        """Validate that critical fields still exist after filtering.

        Args:
            filtered: The filtered output.
            original: The original output before filtering.
        """
        for field in self.CRITICAL_FIELDS:
            if field not in filtered and field in original:
                self._logger.warning(
                    "critical_field_missing_after_filtering",
                    field=field,
                )

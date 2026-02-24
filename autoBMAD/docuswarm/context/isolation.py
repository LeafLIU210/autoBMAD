"""Context isolation module for agent access control.

This module provides the ContextManager class for Layer 2 (Runtime Access Control)
of the three-layer isolation system. It controls context access for different
agent types, ensuring the Independent Agent receives full context while the
Evaluator Agent only receives public, non-private context.

Story: 4.1
"""

from __future__ import annotations

from typing import Any, cast

from autoBMAD.docuswarm.exceptions import ContextIsolationError
from autoBMAD.docuswarm.utils.logging import get_logger

# Private fields that must never be exposed to Evaluator agent
PRIVATE_FIELDS: list[str] = [
    "private_reasoning",
    "tool_call_history",
    "iteration_feedback",
    "internal_notes",
]


class ContextManager:
    """Manages context isolation between Independent and Evaluator agents.

    This class enforces the "dumb agent" isolation principle by:
    - Providing full context access for Independent agent
    - Restricting Evaluator agent to only public, non-private context
    - Validating that no private fields leak to the Evaluator

    Attributes:
        PRIVATE_FIELDS: List of field names that are considered private
            and must not be exposed to the Evaluator agent.

    Example:
        >>> manager = ContextManager()
        >>> # Independent agent gets full context
        >>> independent_ctx = manager.build_independent_context(
        ...     subject_context={"task": "Write code"},
        ...     previous_deliverables={"design": "..."},
        ...     iteration_feedback={"iterations": 2}
        ... )
        >>> # Evaluator gets restricted context
        >>> evaluator_ctx = manager.build_evaluator_context(
        ...     subject_context={"task": "Review code"},
        ...     deliverable={"content": "..."},
        ...     criteria={"quality": "high"}
        ... )
    """

    # Private fields that must not be exposed to Evaluator
    PRIVATE_FIELDS: list[str] = PRIVATE_FIELDS

    def __init__(self) -> None:
        """Initialize ContextManager with logger."""
        self._logger = get_logger(__name__)

    def build_independent_context(
        self,
        subject_context: dict[str, Any] | None = None,
        previous_deliverables: dict[str, Any] | None = None,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build context for Independent agent with full access.

        The Independent agent receives complete access to all context data
        including private reasoning, tool call history, and iteration feedback.

        Args:
            subject_context: The subject/task context for the agent.
            previous_deliverables: Previous deliverables from prior iterations.
            iteration_feedback: Feedback from previous iterations.

        Returns:
            Dictionary containing all context fields with access_level="full".
        """
        self._logger.info(
            "Building independent context",
            access_level="full",
        )

        context: dict[str, Any] = {
            "subject_context": subject_context,
            "previous_deliverables": previous_deliverables,
            "iteration_feedback": iteration_feedback,
            "access_level": "full",
        }

        return context

    def build_evaluator_context(
        self,
        subject_context: dict[str, Any] | None = None,
        deliverable: dict[str, Any] | None = None,
        criteria: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build context for Evaluator agent with restricted access.

        The Evaluator agent only receives public, non-private context.
        This method validates that no private fields are present in the
        deliverable before constructing the context.

        Args:
            subject_context: The subject/task context for evaluation.
            deliverable: The deliverable to evaluate (validated for private fields).
            criteria: Evaluation criteria to assess the deliverable.

        Returns:
            Dictionary containing only public fields with access_level="restricted".

        Raises:
            ContextIsolationError: If private fields are detected in the context.
        """
        self._logger.info(
            "Building evaluator context (restricted)",
            access_level="restricted",
        )

        # Validate deliverable doesn't contain private fields
        if deliverable is not None:
            self._validate_no_private_fields(deliverable, "deliverable")

        context: dict[str, Any] = {
            "subject_context": subject_context,
            "deliverable": deliverable,
            "criteria": criteria,
            "access_level": "restricted",
        }

        return context

    def _validate_no_private_fields(
        self,
        data: dict[str, Any],
        context_name: str,
    ) -> None:
        """Validate that no private fields are present in the data.

        Performs deep inspection to detect private fields at any nesting level.

        Args:
            data: The data dictionary to validate.
            context_name: Name of the context being validated (for error messages).

        Raises:
            ContextIsolationError: If any private field is detected.
        """
        _check_for_private_fields(data, context_name)


def _check_for_private_fields(
    data: Any,
    context_name: str,
    private_fields: list[str] = PRIVATE_FIELDS,
) -> None:
    """Recursively check for private fields in data structure.

    Args:
        data: The data to check (can be dict, list, or primitive).
        context_name: Name of context for error messages.
        private_fields: List of private field names to check for.

    Raises:
        ContextIsolationError: If a private field is found.
    """
    if isinstance(data, dict):
        # Check each key in the dictionary
        for key, value in data.items():
            if cast(str, key) in private_fields:
                raise ContextIsolationError(
                    f"Private field '{key}' found in {context_name}. "
                    + f"Private fields {private_fields} are not allowed in evaluator context.",
                    violation_type="private_field_leak",
                    resource=cast(str, key),
                    target_context=context_name,
                )
            # Recursively check nested values
            _check_for_private_fields(value, context_name, private_fields)
    elif isinstance(data, list):
        # Check each item in the list
        for item in data:
            _check_for_private_fields(item, context_name, private_fields)
    # Primitive types (str, int, float, bool, None) don't need checking


# Re-export ContextIsolationError for convenience
__all__ = ["ContextManager", "ContextIsolationError", "PRIVATE_FIELDS"]

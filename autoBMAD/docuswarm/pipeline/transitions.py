"""State transition logic for pipeline and node status changes - Story 3.9.

This module provides the StateTransitionManager class that:
- Defines valid state transitions for pipeline and node entities
- Validates transitions and raises descriptive errors for invalid ones
- Logs all state transitions with structured logging
- Provides pre-transition and post-transition hooks for extensions
"""

from __future__ import annotations

from collections.abc import Callable

from autoBMAD.docuswarm.utils.logging import get_logger

# Create module logger
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class TransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""

    pass


# ---------------------------------------------------------------------------
# Valid Transition Definitions
# ---------------------------------------------------------------------------

# Valid pipeline status transitions
# Format: {from_status: [to_status1, to_status2, ...]}
VALID_PIPELINE_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["running"],
    "running": ["completed", "failed", "paused"],
    "paused": ["running"],
    # Terminal states have no outgoing transitions
    "completed": [],
    "failed": [],
}

# Valid node status transitions
VALID_NODE_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["running"],
    "running": ["approved", "needs_revision", "blocked"],
    "needs_revision": ["running"],
    # Terminal states have no outgoing transitions
    "approved": [],
    "blocked": [],
}


# ---------------------------------------------------------------------------
# StateTransitionManager Class
# ---------------------------------------------------------------------------


class StateTransitionManager:
    """Manages state transitions for pipeline and node entities.

    This class enforces valid state transitions, provides structured logging,
    and supports pre/post transition hooks for extensibility.

    Attributes:
        pre_transition_hook: Callback called before transition (can abort).
            Receives (entity_type, from_status, to_status).
            Raise TransitionError to abort.
        post_transition_hook: Callback called after transition.
            Receives (entity_type, from_status, to_status, success).

    Example:
        >>> manager = StateTransitionManager()
        >>> manager.can_transition("pipeline", "pending", "running")
        True
        >>> manager.transition("pipeline", "pending", "running")
        >>> # Transition logged with structured logging
    """

    def __init__(
        self,
        pre_hook: Callable[[str, str, str], None] | None = None,
        post_hook: Callable[[str, str, str, bool], None] | None = None,
    ) -> None:
        """Initialize the StateTransitionManager.

        Args:
            pre_hook: Optional pre-transition hook.
            post_hook: Optional post-transition hook.
        """
        self.pre_transition_hook: Callable[[str, str, str], None] | None = pre_hook
        self.post_transition_hook: Callable[[str, str, str, bool], None] | None = post_hook

    def can_transition(self, entity_type: str, from_status: str, to_status: str) -> bool:
        """Check if a state transition is valid.

        Args:
            entity_type: The type of entity ('pipeline' or 'node').
            from_status: The current status.
            to_status: The desired target status.

        Returns:
            True if the transition is valid, False otherwise.
        """
        if entity_type == "pipeline":
            valid_transitions = VALID_PIPELINE_TRANSITIONS
        elif entity_type == "node":
            valid_transitions = VALID_NODE_TRANSITIONS
        else:
            return False

        # Check if from_status exists in the valid transitions
        if from_status not in valid_transitions:
            return False

        # Check if to_status is in the list of valid target statuses
        return to_status in valid_transitions[from_status]

    def transition(self, entity_type: str, from_status: str, to_status: str) -> None:
        """Execute a state transition with validation and logging.

        Args:
            entity_type: The type of entity ('pipeline' or 'node').
            from_status: The current status.
            to_status: The desired target status.

        Raises:
            TransitionError: If the transition is invalid.
        """
        # Call pre-transition hook (can abort by raising exception)
        if self.pre_transition_hook is not None:
            try:
                self.pre_transition_hook(entity_type, from_status, to_status)
            except Exception:
                # Call post-transition hook with success=False
                if self.post_transition_hook is not None:
                    self.post_transition_hook(entity_type, from_status, to_status, False)
                # Re-raise the exception
                raise

        # Validate the transition
        if not self.can_transition(entity_type, from_status, to_status):
            # Log the invalid transition attempt
            logger.error(
                "Invalid state transition attempted",
                entity_type=entity_type,
                from_status=from_status,
                to_status=to_status,
            )

            # Build error message
            if entity_type == "pipeline":
                error_msg = f"Invalid pipeline transition from '{from_status}' to '{to_status}'"
            elif entity_type == "node":
                error_msg = f"Invalid node transition from '{from_status}' to '{to_status}'"
            else:
                error_msg = f"Invalid transition from '{from_status}' to '{to_status}' for entity type '{entity_type}'"

            # Call post-transition hook with success=False
            if self.post_transition_hook is not None:
                self.post_transition_hook(entity_type, from_status, to_status, False)

            raise TransitionError(error_msg)

        # Log the successful transition
        logger.info(
            "State transition completed",
            entity_type=entity_type,
            from_status=from_status,
            to_status=to_status,
        )

        # Call post-transition hook with success=True
        if self.post_transition_hook is not None:
            self.post_transition_hook(entity_type, from_status, to_status, True)

    def get_valid_transitions(self, entity_type: str, from_status: str) -> list[str]:
        """Get list of valid target statuses from a given status.

        Args:
            entity_type: The type of entity ('pipeline' or 'node').
            from_status: The current status.

        Returns:
            List of valid target status strings, or empty list if unknown.
        """
        if entity_type == "pipeline":
            valid_transitions = VALID_PIPELINE_TRANSITIONS
        elif entity_type == "node":
            valid_transitions = VALID_NODE_TRANSITIONS
        else:
            return []

        return valid_transitions.get(from_status, [])


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------


# Singleton instance for convenience
_manager: StateTransitionManager | None = None


def get_transition_manager() -> StateTransitionManager:
    """Get the singleton StateTransitionManager instance.

    Returns:
        The singleton StateTransitionManager instance.
    """
    global _manager
    if _manager is None:
        _manager = StateTransitionManager()
    return _manager

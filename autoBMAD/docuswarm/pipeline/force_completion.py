"""Force Completion Implementation - Story 5.5.

This module provides force completion functionality for the pipeline:
- ForceCompletion: Dataclass for storing force completion records
- ForceCompletionHandler: Class for determining when to force complete
- create_force_completion: Function to generate force completion records with warnings

Force completion is the safety net to prevent infinite iteration loops when quality
cannot meet approval threshold but is still above the escalation floor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from structlog import BoundLogger as StructlogBoundLogger


@dataclass
class ForceCompletion:
    """Record of a force completion event.

    Attributes:
        node_id: The unique identifier for the node that was force completed.
        final_score: The final alignment score achieved.
        threshold: The escalation threshold used for comparison.
        iterations: The number of iterations executed before force completion.
        warning: A detailed warning message documenting quality concerns.
        issues_remaining: List of issues that were not resolved.
    """

    node_id: str = ""
    final_score: float = 0.0
    threshold: float = 0.0
    iterations: int = 0
    warning: str = ""
    issues_remaining: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize issues_remaining if None."""
        if self.issues_remaining is None:
            self.issues_remaining = []


class ForceCompletionHandler:
    """Handles force completion logic for pipeline nodes.

    Determines when to force complete based on iteration count and alignment score.
    Uses escalation threshold to decide if output is usable despite not meeting
    approval criteria.

    Attributes:
        max_iterations: Maximum number of iterations before force completion
        escalation_threshold: Minimum score for force completion (default: 0.50)
        approval_threshold: Score required for approval (default: 0.70)
    """

    DEFAULT_MAX_ITERATIONS = 3
    DEFAULT_ESCALATION_THRESHOLD = 0.50
    DEFAULT_APPROVAL_THRESHOLD = 0.70

    def __init__(
        self,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        escalation_threshold: float = DEFAULT_ESCALATION_THRESHOLD,
        approval_threshold: float = DEFAULT_APPROVAL_THRESHOLD,
    ) -> None:
        """Initialize ForceCompletionHandler.

        Args:
            max_iterations: Maximum iterations before force completion (default: 3)
            escalation_threshold: Minimum score for force completion (default: 0.50)
            approval_threshold: Score required for approval (default: 0.70)
        """
        self.max_iterations = max_iterations
        self.escalation_threshold = escalation_threshold
        self.approval_threshold = approval_threshold
        self.logger: StructlogBoundLogger = structlog.get_logger().bind(
            component=self.__class__.__name__
        )

    def should_force_complete(
        self,
        node_id: str,
        iteration: int,
        alignment_score: float,
    ) -> bool:
        """Determine if force completion should be triggered.

        Force complete triggers when:
        - Iteration count reaches maximum (or exceeds)
        - AND alignment score is greater than or equal to escalation threshold

        Args:
            node_id: The node identifier (for logging)
            iteration: Current iteration number
            alignment_score: The alignment score to evaluate

        Returns:
            True if force completion should occur, False otherwise
        """
        # Must be at or past max iterations
        if iteration < self.max_iterations:
            return False

        # Score must be at or above escalation threshold
        if alignment_score < self.escalation_threshold:
            return False

        # Force complete triggered
        self.logger.info(
            "force_complete_triggered",
            node_id=node_id,
            iteration=iteration,
            alignment_score=alignment_score,
            escalation_threshold=self.escalation_threshold,
        )
        return True


def create_force_completion(
    node_id: str,
    final_score: float,
    threshold: float,
    iterations: int,
    issues_remaining: list[str] | None = None,
    approval_threshold: float = ForceCompletionHandler.DEFAULT_APPROVAL_THRESHOLD,
) -> ForceCompletion:
    """Create a ForceCompletion record with detailed warning message.

    Generates a comprehensive warning that documents:
    - Node ID
    - Iteration count
    - Final score
    - Approval threshold
    - Escalation threshold
    - Unresolved issues

    Args:
        node_id: The node identifier
        final_score: The final alignment score achieved
        threshold: The escalation threshold used
        iterations: Number of iterations executed
        issues_remaining: List of unresolved issues
        approval_threshold: The approval threshold (default: 0.70)

    Returns:
        ForceCompletion record with populated fields
    """
    # Generate detailed warning message
    warning_lines = [
        f"⚠️ FORCE COMPLETION: Node '{node_id}'",
        "",
        "Quality warning: Output is usable but did not meet full approval criteria.",
        "",
        "Details:",
        f"  - Iterations: {iterations} (max: {ForceCompletionHandler.DEFAULT_MAX_ITERATIONS})",
        f"  - Final Score: {final_score:.2f}",
        f"  - Approval Threshold: {approval_threshold:.2f}",
        f"  - Escalation Threshold: {threshold:.2f}",
    ]

    if issues_remaining:
        warning_lines.append("")
        warning_lines.append(f"  - Unresolved Issues ({len(issues_remaining)}):")
        for issue in issues_remaining:
            warning_lines.append(f"    • {issue}")

    warning_message = "\n".join(warning_lines)

    return ForceCompletion(
        node_id=node_id,
        final_score=final_score,
        threshold=threshold,
        iterations=iterations,
        warning=warning_message,
        issues_remaining=issues_remaining or [],
    )


__all__ = [
    "ForceCompletion",
    "ForceCompletionHandler",
    "create_force_completion",
]

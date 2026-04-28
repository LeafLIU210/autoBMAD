"""Escalation Handling Implementation - Story 5.3.

This module provides escalation handling for nodes within the pipeline:
- EscalationReason: Enum for escalation trigger reasons
- Escalation: Dataclass for escalation records
- EscalationHandler: Handler for creating and resolving escalations

Escalations occur when:
- A node receives a BLOCKED verdict after max iterations
- Critical issues are detected
- User manually requests escalation
- Max iterations are reached without approval
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

import structlog

# Beijing timezone (UTC+8)
_BEIJING_TZ = timezone(timedelta(hours=8))

if TYPE_CHECKING:
    from structlog import BoundLogger as StructlogBoundLogger


class EscalationReason(Enum):
    """Reasons that can trigger an escalation.

    Attributes:
        MAX_ITERATIONS: Maximum iteration limit reached without approval
        BLOCKED_VERDICT: Node received a BLOCKED verdict from evaluator
        CRITICAL_ISSUE: Critical issue detected requiring human intervention
        USER_REQUESTED: User manually requested escalation
    """

    MAX_ITERATIONS = "max_iterations"
    BLOCKED_VERDICT = "blocked_verdict"
    CRITICAL_ISSUE = "critical_issue"
    USER_REQUESTED = "user_requested"


@dataclass
class Escalation:
    """Represents an escalation record for a node run.

    Attributes:
        run_id: The unique identifier for this node run.
        node_id: The identifier for the node that triggered escalation.
        reason: The reason for the escalation.
        details: Human-readable details about the escalation.
        alignment_score: The alignment score at time of escalation.
        issues: List of issues that triggered the escalation.
        created_at: When the escalation was created.
        resolved_at: When the escalation was resolved (None if unresolved).
        resolution: Resolution provided by the user (None if unresolved).
    """

    run_id: str
    node_id: str
    reason: EscalationReason
    details: str
    alignment_score: float
    issues: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(_BEIJING_TZ))
    resolved_at: datetime | None = None
    resolution: str | None = None


class EscalationHandler:
    """Handles escalation creation and resolution.

    This handler:
    - Creates escalation records when nodes cannot reach quality thresholds
    - Updates node run status to 'blocked' on escalation
    - Restores node run status to 'running' on resolution
    - Provides methods to query escalation status
    - Logs all key events via structlog

    Thread-safety: Uses a regular dict for escalations. For parallel node execution,
    consider adding threading.Lock for state dict access.

    Example:
        handler = EscalationHandler(state_manager=state_manager)

        # Create escalation
        handler.escalate(
            run_id="run-123",
            node_id="node-1",
            reason=EscalationReason.BLOCKED_VERDICT,
            evaluation={"verdict": "BLOCKED", "score": 0.45, "issues": ["Issue 1"]}
        )

        # Check escalation status
        if handler.has_escalation("run-123"):
            escalation = handler.get_escalation("run-123")
            print(f"Escalation: {escalation.details}")

        # Resolve escalation
        handler.resolve(
            run_id="run-123",
            resolution="Fixed the issues"
        )
    """

    def __init__(self, state_manager: Any) -> None:
        """Initialize the EscalationHandler.

        Args:
            state_manager: The state manager for updating node run status.
        """
        self._state_manager = state_manager
        self._escalations: dict[str, Escalation] = {}
        self._logger: StructlogBoundLogger = structlog.get_logger(component="EscalationHandler")

    def escalate(
        self,
        run_id: str,
        node_id: str,
        reason: EscalationReason,
        evaluation: dict[str, Any],
    ) -> Escalation:
        """Create an escalation and update node run status to 'blocked'.

        Args:
            run_id: The unique identifier for this node run.
            node_id: The identifier for the node that triggered escalation.
            reason: The reason for the escalation.
            evaluation: The evaluation data containing verdict, score, issues.

        Returns:
            The created Escalation record.

        Raises:
            Exception: If status update fails.
        """
        details = self._format_details(evaluation)
        alignment_score = evaluation.get("score", 0.0)
        issues = evaluation.get("issues", [])

        escalation = Escalation(
            run_id=run_id,
            node_id=node_id,
            reason=reason,
            details=details,
            alignment_score=alignment_score,
            issues=issues,
            created_at=datetime.now(_BEIJING_TZ),
        )

        self._escalations[run_id] = escalation

        # Update node run status to blocked
        self._state_manager.update_node_run(run_id=run_id, status="blocked")

        self._logger.info(
            "Escalation created",
            run_id=run_id,
            node_id=node_id,
            reason=reason.value,
            alignment_score=alignment_score,
        )

        return escalation

    def resolve(self, run_id: str, resolution: str) -> bool:
        """Clear escalation and restore node run status to 'running'.

        Args:
            run_id: The unique identifier for the node run.
            resolution: The resolution provided by the user.

        Returns:
            True if resolution was successful.

        Raises:
            ValueError: If no escalation exists for the given run_id.
        """
        if run_id not in self._escalations:
            raise ValueError(f"No escalation found for run_id: {run_id}")

        escalation = self._escalations[run_id]
        escalation.resolved_at = datetime.now(_BEIJING_TZ)
        escalation.resolution = resolution

        # Remove from active escalations
        del self._escalations[run_id]

        # Restore node run status to running
        self._state_manager.update_node_run(run_id=run_id, status="running")

        self._logger.info(
            "Escalation resolved",
            run_id=run_id,
            node_id=escalation.node_id,
            resolution=resolution,
        )

        return True

    def get_escalation(self, run_id: str) -> Escalation | None:
        """Get escalation record for a run_id.

        Args:
            run_id: The unique identifier for the node run.

        Returns:
            The Escalation record if exists, None otherwise.
        """
        return self._escalations.get(run_id)

    def has_escalation(self, run_id: str) -> bool:
        """Check if an escalation exists for a run_id.

        Args:
            run_id: The unique identifier for the node run.

        Returns:
            True if escalation exists, False otherwise.
        """
        return run_id in self._escalations

    def _format_details(self, evaluation: dict[str, Any]) -> str:
        """Format evaluation info for user display.

        Args:
            evaluation: The evaluation data containing verdict, score, issues, feedback.

        Returns:
            Formatted string with evaluation details.
        """
        parts: list[str] = []

        verdict = evaluation.get("verdict", "UNKNOWN")
        parts.append(f"Verdict: {verdict}")

        score = evaluation.get("score")
        if score is not None:
            parts.append(f"Score: {score}")

        issues = evaluation.get("issues", [])
        if issues:
            parts.append("Issues:")
            for issue in issues:
                parts.append(f"  - {issue}")

        feedback = evaluation.get("feedback")
        if feedback:
            parts.append(f"Feedback: {feedback}")

        return "\n".join(parts)

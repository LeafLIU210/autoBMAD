"""Escalation Handling - Story 5.3.

This module provides escalation handling for the pipeline:
- EscalationReason: Enum defining reasons for escalation
- Escalation: Dataclass storing escalation information
- EscalationHandler: Class managing pipeline escalation and resolution

Escalation occurs when:
- BLOCKED verdict with alignment score < 0.50 after max iterations (3)
- Critical issues that cannot be resolved through iteration
- User requests escalation

When escalated:
- Pipeline status changes to "paused"
- Escalation record is created with reason, details, and issues
- User can resolve via CLI with guidance, skip node, or abort pipeline
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
    """Reasons for pipeline escalation.

    Attributes:
        MAX_ITERATIONS: Maximum iteration count reached without resolution
        BLOCKED_VERDICT: BLOCKED verdict from evaluator with low alignment
        CRITICAL_ISSUE: Critical issue that blocks pipeline progress
        USER_REQUESTED: User explicitly requests escalation
    """

    MAX_ITERATIONS = "max_iterations"
    BLOCKED_VERDICT = "blocked_verdict"
    CRITICAL_ISSUE = "critical_issue"
    USER_REQUESTED = "user_requested"


@dataclass
class Escalation:
    """Stores escalation information for a pipeline.

    Attributes:
        pipeline_id: The unique identifier for the pipeline.
        node_id: The node that triggered the escalation.
        reason: The reason for escalation.
        details: Detailed description of the escalation.
        alignment_score: The alignment score at time of escalation.
        issues: List of issues identified.
        timestamp: When the escalation was created.
        resolution: How the escalation was resolved (user_guidance, skip_node, abort_pipeline).
        user_guidance: The user-provided guidance when resolution is "user_guidance".
    """

    pipeline_id: str = ""
    node_id: str = ""
    reason: EscalationReason | None = None
    details: str = ""
    alignment_score: float = 0.0
    issues: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(_BEIJING_TZ))
    resolution: str | None = None
    user_guidance: str | None = None


class EscalationHandler:
    """Handles pipeline escalation and resolution.

    This handler:
    - Creates escalation records when triggered
    - Pauses pipeline on escalation
    - Resumes pipeline on resolution
    - Tracks all escalations per pipeline

    The handler supports three resolution types:
    - user_guidance: Retry with user-provided guidance
    - skip_node: Bypass the current node
    - abort_pipeline: Stop the pipeline entirely

    Example:
        >>> handler = EscalationHandler(state_manager=state_manager)
        >>> # Trigger escalation
        >>> escalation = await handler.escalate(
        ...     pipeline_id="pipeline-1",
        ...     node_id="analyst",
        ...     reason=EscalationReason.MAX_ITERATIONS,
        ...     alignment_score=0.45,
        ...     issues=["Issue 1", "Issue 2"],
        ... )
        >>> # Resolve with user guidance
        >>> await handler.resolve(
        ...     pipeline_id="pipeline-1",
        ...     resolution="user_guidance",
        ...     user_guidance="Follow the standard format",
        ... )
    """

    def __init__(self, state_manager: Any) -> None:
        """Initialize EscalationHandler.

        Args:
            state_manager: StateManager instance for pipeline state updates.
        """
        self._state_manager = state_manager
        self._escalations: dict[str, Escalation] = {}
        self.logger: StructlogBoundLogger = structlog.get_logger().bind(
            component=self.__class__.__name__
        )

    async def escalate(
        self,
        pipeline_id: str,
        node_id: str,
        reason: EscalationReason,
        alignment_score: float,
        issues: list[str] | None = None,
    ) -> Escalation:
        """Create an escalation record and pause the pipeline.

        Args:
            pipeline_id: The pipeline ID to escalate.
            node_id: The node that triggered the escalation.
            reason: The reason for escalation.
            alignment_score: The alignment score at time of escalation.
            issues: Optional list of issues identified.

        Returns:
            The created Escalation record.
        """
        if issues is None:
            issues = []

        # Format details
        details = self._format_details(
            pipeline_id=pipeline_id,
            node_id=node_id,
            reason=reason,
            alignment_score=alignment_score,
            issues=issues,
        )

        # Create escalation record
        escalation = Escalation(
            pipeline_id=pipeline_id,
            node_id=node_id,
            reason=reason,
            details=details,
            alignment_score=alignment_score,
            issues=issues,
            timestamp=datetime.now(_BEIJING_TZ),
        )

        # Store in memory
        self._escalations[pipeline_id] = escalation

        # Pause the pipeline - use update_pipeline_state (async)
        await self._state_manager.update_pipeline_state(pipeline_id, {"status": "paused"})

        # Log the escalation
        self.logger.info(
            "escalation_created",
            pipeline_id=pipeline_id,
            node_id=node_id,
            reason=reason.value,
            alignment_score=alignment_score,
        )

        return escalation

    async def resolve(
        self,
        pipeline_id: str,
        resolution: str,
        user_guidance: str | None = None,
    ) -> Escalation:
        """Resolve an escalation and resume the pipeline.

        Args:
            pipeline_id: The pipeline ID to resolve.
            resolution: Resolution type (user_guidance, skip_node, abort_pipeline).
            user_guidance: Optional guidance from user for retry.

        Returns:
            The updated Escalation record.

        Raises:
            ValueError: If no active escalation exists for the pipeline.
        """
        if pipeline_id not in self._escalations:
            raise ValueError(f"No active escalation found for pipeline: {pipeline_id}")

        escalation = self._escalations[pipeline_id]
        escalation.resolution = resolution
        escalation.user_guidance = user_guidance

        # Determine new status based on resolution
        if resolution == "abort_pipeline":
            new_status = "failed"
        else:
            new_status = "running"

        # Resume the pipeline - use update_pipeline_state (async)
        await self._state_manager.update_pipeline_state(pipeline_id, {"status": new_status})

        # Log the resolution
        self.logger.info(
            "escalation_resolved",
            pipeline_id=pipeline_id,
            resolution=resolution,
            new_status=new_status,
        )

        return escalation

    def _format_details(
        self,
        pipeline_id: str,
        node_id: str,
        reason: EscalationReason,
        alignment_score: float,
        issues: list[str],
    ) -> str:
        """Format escalation details.

        Args:
            pipeline_id: The pipeline ID.
            node_id: The node that triggered escalation.
            reason: The escalation reason.
            alignment_score: The alignment score.
            issues: List of issues.

        Returns:
            Formatted details string.
        """
        lines = [
            f"Pipeline ID: {pipeline_id}",
            f"Node: {node_id}",
            f"Reason: {reason.value}",
            f"Alignment Score: {alignment_score:.2f}",
        ]

        if issues:
            lines.append("Issues:")
            for issue in issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)

    def has_active_escalation(self, pipeline_id: str) -> bool:
        """Check if a pipeline has an active escalation.

        Args:
            pipeline_id: The pipeline ID to check.

        Returns:
            True if an escalation exists for the pipeline.
        """
        return pipeline_id in self._escalations

    def get_escalation(self, pipeline_id: str) -> Escalation | None:
        """Get the escalation record for a pipeline.

        Args:
            pipeline_id: The pipeline ID.

        Returns:
            The Escalation record, or None if not found.
        """
        return self._escalations.get(pipeline_id)

"""Isolation audit logger module - Story 4.4.

Provides audit logging for context isolation verification:
- Log all context builds (independent and evaluator)
- Log all filtering operations with fields removed
- Log potential violations with details
- Generate audit reports for pipeline verification
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

# Beijing timezone (UTC+8)
_BEIJING_TZ = timezone(timedelta(hours=8))

# Event type constants
EVENT_TYPE_CONTEXT_BUILD = "context_build"
EVENT_TYPE_FILTER = "filter"
EVENT_TYPE_VIOLATION = "violation"

logger = structlog.get_logger(__name__)


@dataclass
class AuditEvent:
    """Dataclass representing an audit event for context isolation.

    Attributes:
        timestamp: When the event occurred.
        event_type: Type of event (context_build, filter, violation).
        agent_type: Type of agent (independent, evaluator).
        run_id: ID of the run this event belongs to.
        node_id: ID of the node that generated this event.
        context_keys: List of context keys provided to the agent.
        details: Additional event-specific details.
    """

    timestamp: datetime
    event_type: str
    agent_type: str
    run_id: str
    node_id: str
    context_keys: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class IsolationAuditLogger:
    """Logger for auditing context isolation operations.

    Tracks all context builds, filtering operations, and potential
    violations for compliance reporting.
    """

    def __init__(self) -> None:
        """Initialize the IsolationAuditLogger."""
        self._events: list[AuditEvent] = []
        self._logger = structlog.get_logger(__name__)

    @property
    def events(self) -> list[AuditEvent]:
        """Return the list of audit events."""
        return self._events

    def log_context_build(
        self,
        agent_type: str,
        run_id: str | None = None,
        node_id: str | None = None,
        context_keys: list[str] | None = None,
        pipeline_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a context building event.

        Args:
            agent_type: Type of agent (independent or evaluator).
            run_id: ID of the run (also accepts pipeline_id for compatibility).
            node_id: ID of the node.
            context_keys: List of context keys provided to the agent.
            pipeline_id: Alias for run_id (for compatibility with DualAgentNode).
            details: Additional details dict (for compatibility with DualAgentNode).
        """
        # Use pipeline_id as run_id if provided, for compatibility
        effective_run_id = run_id or pipeline_id or "unknown"
        effective_node_id = node_id or "unknown"
        effective_context_keys = context_keys or (list(details.keys()) if details else [])

        event = AuditEvent(
            timestamp=datetime.now(_BEIJING_TZ),
            event_type=EVENT_TYPE_CONTEXT_BUILD,
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            context_keys=effective_context_keys,
            details=details or {},
        )
        self._events.append(event)
        self._logger.debug(
            "context_build",
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            context_keys=effective_context_keys,
            details=details,
        )

    def log_filter_operation(
        self,
        agent_type: str,
        run_id: str | None = None,
        node_id: str | None = None,
        fields_removed: list[str] | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        """Record a filtering operation.

        Args:
            agent_type: Type of agent performing the filter.
            run_id: ID of the run (also accepts pipeline_id for compatibility).
            node_id: ID of the node.
            fields_removed: List of field names that were removed.
            pipeline_id: Alias for run_id (for compatibility with DualAgentNode).
        """
        # Use pipeline_id as run_id if provided, for compatibility
        effective_run_id = run_id or pipeline_id or "unknown"
        effective_node_id = node_id or "unknown"
        effective_fields_removed = fields_removed or []

        details = {"fields_removed": effective_fields_removed}
        event = AuditEvent(
            timestamp=datetime.now(_BEIJING_TZ),
            event_type=EVENT_TYPE_FILTER,
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            context_keys=[],
            details=details,
        )
        self._events.append(event)
        self._logger.debug(
            "filter_operation",
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            fields_removed=effective_fields_removed,
        )

    def log_potential_violation(
        self,
        agent_type: str,
        run_id: str | None = None,
        node_id: str | None = None,
        violation_type: str | None = None,
        details: dict[str, Any] | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        """Record a potential isolation violation.

        Args:
            agent_type: Type of agent that caused the potential violation.
            run_id: ID of the run (also accepts pipeline_id for compatibility).
            node_id: ID of the node.
            violation_type: Type of violation (e.g., "private_field_leak", "unauthorized_access").
            details: Details about the violation.
            pipeline_id: Alias for run_id (for compatibility with DualAgentNode).
        """
        # Use pipeline_id as run_id if provided, for compatibility
        effective_run_id = run_id or pipeline_id or "unknown"
        effective_node_id = node_id or "unknown"

        violation_details: dict[str, Any] = {}
        if violation_type:
            violation_details["violation_type"] = violation_type
        if details:
            violation_details.update(details)

        event = AuditEvent(
            timestamp=datetime.now(_BEIJING_TZ),
            event_type=EVENT_TYPE_VIOLATION,
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            context_keys=[],
            details=violation_details,
        )
        self._events.append(event)
        self._logger.warning(
            "potential_violation",
            agent_type=agent_type,
            run_id=effective_run_id,
            node_id=effective_node_id,
            violation_type=violation_type,
            details=details,
        )

    def generate_report(self, run_id: str) -> dict[str, Any]:
        """Generate a compliance report for a specific run.

        Args:
            run_id: ID of the run to generate report for.

        Returns:
            Dictionary containing:
                - run_id: The run ID
                - total_events: Total number of events
                - violations_count: Number of violation events
                - isolation_status: "CLEAN" or "VIOLATION"
                - events: List of events for this run
        """
        run_events = [e for e in self._events if e.run_id == run_id]

        violations_count = sum(1 for e in run_events if e.event_type == EVENT_TYPE_VIOLATION)

        isolation_status = "VIOLATION" if violations_count > 0 else "CLEAN"

        return {
            "run_id": run_id,
            "total_events": len(run_events),
            "violations_count": violations_count,
            "isolation_status": isolation_status,
            "events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "agent_type": e.agent_type,
                    "node_id": e.node_id,
                    "context_keys": e.context_keys,
                    "details": e.details,
                }
                for e in run_events
            ],
        }

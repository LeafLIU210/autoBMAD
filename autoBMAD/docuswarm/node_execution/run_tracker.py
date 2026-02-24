"""Node Run Tracker for per-node run tracking - Story 3.9.

This module provides the NodeRunTracker class for tracking multiple runs per node,
enabling users to execute nodes multiple times and view history.

Features:
- Unique run_id generation (8-character UUID prefix)
- Run history queryable by node_id with pagination
- Latest run retrieval with optional context_hash filter
- Run metadata: run_id, node_id, context_hash, start_time, end_time, status
- Run results persistence (deliverable, questions, evaluation)
"""

from __future__ import annotations

import uuid
from typing import Any

from autoBMAD.docuswarm.storage.state_manager import StateManager


class NodeRunTracker:
    """Tracks node execution runs.

    This class provides methods for tracking multiple runs per node,
    enabling users to execute nodes multiple times and view history.

    Args:
        state_manager: StateManager instance for database persistence.

    Example:
        >>> tracker = NodeRunTracker(state_manager=sm)
        >>> run_id = tracker.start_run(node_id="analyst", context_hash="abc")
        >>> tracker.complete_run(run_id=run_id, deliverable={"data": "value"})
        >>> runs = tracker.list_runs(node_id="analyst", limit=10)
        >>> latest = tracker.get_latest_run(node_id="analyst")
    """

    def __init__(self, state_manager: StateManager) -> None:
        """Initialize NodeRunTracker.

        Args:
            state_manager: StateManager instance for database persistence.
        """
        self.state_manager = state_manager

    def generate_run_id(self) -> str:
        """Generate 8-character run ID from UUID4.

        Returns:
            8-character alphanumeric string (first 8 chars of UUID4).
        """
        return str(uuid.uuid4())[:8]

    def list_runs(
        self,
        node_id: str,
        limit: int = 10,
        context_hash: str | None = None,
    ) -> list[dict[str, Any]]:
        """List run history for a node.

        Args:
            node_id: The node identifier to filter by.
            limit: Maximum number of runs to return (default 10).
            context_hash: Optional context hash to filter by.

        Returns:
            List of run dictionaries sorted by start_time DESC.
        """
        return self.state_manager.list_node_runs(
            node_id=node_id,
            context_hash=context_hash,
            limit=limit,
        )

    def get_latest_run(
        self,
        node_id: str,
        context_hash: str | None = None,
    ) -> dict[str, Any] | None:
        """Get latest run for a node.

        Args:
            node_id: The node identifier.
            context_hash: Optional context hash to filter by.

        Returns:
            Latest run dictionary or None if no runs exist.
        """
        runs = self.state_manager.list_node_runs(
            node_id=node_id,
            context_hash=context_hash,
            limit=1,
        )
        return runs[0] if runs else None

    def start_run(
        self,
        node_id: str,
        context_hash: str | None = None,
    ) -> str:
        """Start a new run for a node.

        Args:
            node_id: The node identifier.
            context_hash: Optional context hash for deduplication.

        Returns:
            The generated run_id.
        """
        run_id = self.generate_run_id()
        self.state_manager.create_node_run(
            run_id=run_id,
            node_id=node_id,
            context_hash=context_hash,
        )
        return run_id

    def complete_run(
        self,
        run_id: str,
        status: str = "completed",
        deliverable: dict[str, Any] | None = None,
        questions: list[dict[str, Any]] | None = None,
        evaluation: dict[str, Any] | None = None,
    ) -> bool:
        """Complete a run with results.

        Args:
            run_id: The run identifier.
            status: Final status (default 'completed').
            deliverable: Optional deliverable data.
            questions: Optional questions list.
            evaluation: Optional evaluation data.

        Returns:
            True if update was successful, False if run not found.
        """
        try:
            return self.state_manager.update_node_run(
                run_id=run_id,
                status=status,
                deliverable=deliverable,
                questions=questions,
                evaluation=evaluation,
            )
        except Exception:
            return False

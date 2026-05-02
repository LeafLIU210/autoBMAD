"""Pipeline lease and stale-running detection.

This module provides functionality to detect pipelines that are marked as
"running" in the database but have no alive owner process or expired heartbeat.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from autoBMAD.docuswarm.storage.state_manager import StateManager


def _pid_exists(pid: int) -> bool:
    """Check if a process with given PID exists.

    Args:
        pid: Process ID to check.

    Returns:
        True if process exists, False otherwise.
    """
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def detect_stale_pipelines(
    state_manager: StateManager,
    threshold_seconds: int = 300,
) -> list[dict[str, Any]]:
    """Find pipelines that are running but have no alive owner or expired heartbeat.

    Args:
        state_manager: StateManager instance to query pipelines.
        threshold_seconds: Heartbeat expiration threshold in seconds.

    Returns:
        List of stale pipeline dictionaries.
    """
    stale: list[dict[str, Any]] = []
    # Query directly to include lease columns not exposed by state_json
    with state_manager._db.acquire() as conn:
        cursor = conn.execute(
            "SELECT pipeline_id, subject, status, current_node, state_json, "
            "owner_pid, host, last_heartbeat_at, last_event_at, created_at, updated_at "
            "FROM pipelines WHERE status = 'running'"
        )
        rows = cursor.fetchall()

    for row in rows:
        pipeline = dict(row)
        owner_pid = pipeline.get("owner_pid")
        last_heartbeat = pipeline.get("last_heartbeat_at")

        # Check if owner process exists
        owner_alive = owner_pid is not None and _pid_exists(int(owner_pid))

        # Check heartbeat expiration
        heartbeat_expired = False
        if last_heartbeat:
            heartbeat_time = datetime.fromisoformat(last_heartbeat)
            elapsed = (datetime.now(UTC) - heartbeat_time).total_seconds()
            heartbeat_expired = elapsed > threshold_seconds
        else:
            # No heartbeat at all = stale
            heartbeat_expired = True

        if not owner_alive or heartbeat_expired:
            stale.append(pipeline)

    return stale

"""State Manager for pipeline state persistence - Story 1.5.

This module provides the StateManager class for managing pipeline state,
including creating pipelines, updating status, saving node results, and
querying pipeline state.

Features:
- Create pipelines with unique UUIDs
- Update pipeline status and current node
- Save node results with deliverable, questions, and evaluation
- Query pipelines with filters
- Transaction support with rollback
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from sqlite3 import Row
from typing import Any, cast

from autoBMAD.docuswarm.exceptions import StorageError
from autoBMAD.docuswarm.storage.database import DatabaseManager

# Valid pipeline status values
PIPELINE_STATUSES = ("pending", "running", "completed", "failed", "paused", "cancelled")

logger = logging.getLogger(__name__)


class StateManager:
    """Manages pipeline state persistence.

    This class provides CRUD operations for pipelines and node results,
    supporting pipeline pause/resume functionality and concurrent access.

    Args:
        db_path: Path to the SQLite database file.

    Example:
        >>> sm = StateManager(db_path=Path("docuswarm.db"))
        >>> pipeline_id = sm.create_pipeline(subject="My Subject")
        >>> sm.update_pipeline_status(pipeline_id, status="running")
        >>> pipeline = sm.get_pipeline(pipeline_id)
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize StateManager.

        Args:
            db_path: Path to the SQLite database file. Defaults to "docuswarm.db".

        Raises:
            StorageError: If database cannot be initialized.
        """
        self._db = DatabaseManager.get_instance(db_path=db_path or "docuswarm.db")

    @property
    def db(self) -> DatabaseManager:
        """Get the database manager instance.

        Returns:
            The DatabaseManager instance for direct database access.
        """
        return self._db

    @staticmethod
    def _generate_pipeline_id() -> str:
        """Generate a unique pipeline ID.

        Uses UUID4 combined with timestamp for unique, sortable IDs.

        Returns:
            Pipeline ID string in format: pipeline-{timestamp_ms}-{uuid4}
        """
        timestamp_ms = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"pipeline-{timestamp_ms}-{unique_id}"

    @staticmethod
    def _validate_status(status: str) -> None:
        """Validate pipeline status value.

        Args:
            status: Status string to validate.

        Raises:
            StorageError: If status is not valid.
        """
        if status not in PIPELINE_STATUSES:
            raise StorageError(
                f"Invalid status '{status}'. Must be one of: {PIPELINE_STATUSES}",
                operation_type="validate",
            )

    def create_pipeline(
        self,
        subject: str,
        subject_context: dict[str, Any] | None = None,
    ) -> str:
        """Create a new pipeline with pending status.

        Args:
            subject: The subject/topic for the pipeline.
            subject_context: Optional context dictionary to store as JSON.

        Returns:
            The newly created pipeline ID.

        Raises:
            StorageError: If pipeline creation fails.
        """
        from autoBMAD.docuswarm.pipeline.state import create_initial_state

        pipeline_id = self._generate_pipeline_id()
        # Create complete PipelineState (F1: state_json as single source of truth)
        initial_state = create_initial_state(pipeline_id, subject_context or {})
        state_json = json.dumps(initial_state)

        try:
            with self._db.acquire() as conn:
                _ = conn.execute(
                    "INSERT INTO pipelines (pipeline_id, subject, status, state_json) "
                    + "VALUES (?, ?, ?, ?)",
                    (pipeline_id, subject, "pending", state_json),
                )
        except Exception as e:
            raise StorageError(
                f"Failed to create pipeline: {e}",
                operation_type="create",
                pipeline_id=pipeline_id,
            ) from e

        return pipeline_id

    def update_pipeline_status(
        self,
        pipeline_id: str,
        status: str,
        current_node: str | None = None,
    ) -> bool:
        """Update pipeline status and optionally current node.

        Args:
            pipeline_id: The pipeline ID to update.
            status: New status (pending, running, completed, failed, paused).
            current_node: Optional current node identifier.

        Returns:
            True if update was successful.

        Raises:
            StorageError: If pipeline not found or status is invalid.
        """
        self._validate_status(status)

        # Check if pipeline exists
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="update",
                pipeline_id=pipeline_id,
            )

        try:
            with self._db.acquire() as conn:
                if current_node is not None:
                    _ = conn.execute(
                        "UPDATE pipelines SET status = ?, current_node = ?, "
                        + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                        (status, current_node, pipeline_id),
                    )
                else:
                    _ = conn.execute(
                        "UPDATE pipelines SET status = ?, "
                        + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                        (status, pipeline_id),
                    )
            return True
        except Exception as e:
            raise StorageError(
                f"Failed to update pipeline status: {e}",
                operation_type="update",
                pipeline_id=pipeline_id,
            ) from e

    def save_node_result(
        self,
        pipeline_id: str,
        node_id: str,
        deliverable: dict[str, Any] | None = None,
        questions: list[dict[str, Any]] | None = None,
        evaluation: dict[str, Any] | None = None,
    ) -> bool:
        """Save node result with deliverable, questions, and evaluation.

        Args:
            pipeline_id: The pipeline ID.
            node_id: The node identifier.
            deliverable: Optional deliverable data as dictionary.
            questions: Optional list of questions as dictionaries.
            evaluation: Optional evaluation data as dictionary.

        Returns:
            True if save was successful.

        Raises:
            StorageError: If pipeline not found or save fails.
        """
        # Check if pipeline exists
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="create",
                pipeline_id=pipeline_id,
            )

        # Get current iteration count for this node
        iteration = self._get_node_iteration(pipeline_id, node_id) + 1

        # Serialize to JSON
        deliverable_json = json.dumps(deliverable) if deliverable is not None else None
        questions_json = json.dumps(questions) if questions is not None else None
        evaluation_json = json.dumps(evaluation) if evaluation is not None else None

        try:
            with self._db.acquire() as conn:
                _ = conn.execute(
                    "INSERT INTO node_results "
                    + "(pipeline_id, node_id, iteration, deliverable_json, questions_json, evaluation_json, status) "
                    + "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        pipeline_id,
                        node_id,
                        iteration,
                        deliverable_json,
                        questions_json,
                        evaluation_json,
                        "completed",
                    ),
                )
            return True
        except Exception as e:
            raise StorageError(
                f"Failed to save node result: {e}",
                operation_type="create",
                pipeline_id=pipeline_id,
                node_id=node_id,
            ) from e

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
        """Get pipeline with all related node results.

        Args:
            pipeline_id: The pipeline ID to retrieve.

        Returns:
            Dictionary with pipeline data and node_results, or None if not found.
        """
        try:
            with self._db.acquire() as conn:
                # Get pipeline
                cursor = conn.execute(
                    "SELECT pipeline_id, subject, status, current_node, state_json, "
                    + "created_at, updated_at FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                )
                row: Row | None = cast(Row | None, cursor.fetchone())

                if row is None:
                    return None

                # Get node results
                node_cursor = conn.execute(
                    "SELECT id, node_id, iteration, deliverable_json, questions_json, "
                    + "evaluation_json, status, created_at FROM node_results "
                    + "WHERE pipeline_id = ? ORDER BY created_at",
                    (pipeline_id,),
                )

                node_results: list[dict[str, Any]] = []
                for node_row in cast(list[Row], node_cursor.fetchall()):
                    node_results.append(
                        {
                            "id": node_row["id"],
                            "node_id": node_row["node_id"],
                            "iteration": node_row["iteration"],
                            "deliverable": (
                                json.loads(cast(str, node_row["deliverable_json"]))
                                if node_row["deliverable_json"]
                                else None
                            ),
                            "questions": (
                                json.loads(cast(str, node_row["questions_json"]))
                                if node_row["questions_json"]
                                else None
                            ),
                            "evaluation": (
                                json.loads(cast(str, node_row["evaluation_json"]))
                                if node_row["evaluation_json"]
                                else None
                            ),
                            "status": node_row["status"],
                            "created_at": node_row["created_at"],
                        }
                    )

                return {
                    "pipeline_id": row["pipeline_id"],
                    "subject": row["subject"],
                    "status": row["status"],
                    "current_node": row["current_node"],
                    "state": json.loads(cast(str, row["state_json"])) if row["state_json"] else {},
                    "node_results": node_results,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
        except Exception as e:
            raise StorageError(
                f"Failed to get pipeline: {e}",
                operation_type="read",
                pipeline_id=pipeline_id,
            ) from e

    def list_pipelines(self, status: str | None = None) -> list[dict[str, Any]]:
        """List pipelines, optionally filtered by status.

        Args:
            status: Optional status to filter by.

        Returns:
            List of pipeline dictionaries sorted by created_at DESC.

        Raises:
            StorageError: If status is invalid.
        """
        if status is not None:
            self._validate_status(status)

        try:
            with self._db.acquire() as conn:
                if status:
                    cursor = conn.execute(
                        "SELECT pipeline_id, subject, status, current_node, "
                        + "created_at, updated_at FROM pipelines WHERE status = ? "
                        + "ORDER BY created_at DESC",
                        (status,),
                    )
                else:
                    cursor = conn.execute(
                        "SELECT pipeline_id, subject, status, current_node, "
                        + "created_at, updated_at FROM pipelines ORDER BY created_at DESC"
                    )

                pipelines: list[dict[str, Any]] = []
                for row in cast(list[Row], cursor.fetchall()):
                    pipelines.append(
                        {
                            "pipeline_id": row["pipeline_id"],
                            "subject": row["subject"],
                            "status": row["status"],
                            "current_node": row["current_node"],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                        }
                    )

                return pipelines
        except Exception as e:
            raise StorageError(
                f"Failed to list pipelines: {e}",
                operation_type="read",
            ) from e

    def _pipeline_exists(self, pipeline_id: str) -> bool:
        """Check if pipeline exists.

        Args:
            pipeline_id: The pipeline ID to check.

        Returns:
            True if pipeline exists.
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM pipelines WHERE pipeline_id = ?", (pipeline_id,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False

    def _get_node_iteration(self, pipeline_id: str, node_id: str) -> int:
        """Get current iteration count for a node.

        Args:
            pipeline_id: The pipeline ID.
            node_id: The node ID.

        Returns:
            Current iteration count (0 if no results yet).
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT MAX(iteration) as max_iter FROM node_results "
                    + "WHERE pipeline_id = ? AND node_id = ?",
                    (pipeline_id, node_id),
                )
                row: Row | None = cast(Row | None, cursor.fetchone())
                if row is not None and row["max_iter"] is not None:
                    return cast(int, row["max_iter"])
                return 0
        except Exception:
            return 0

    def update_subject_context(self, pipeline_id: str, context_update: dict[str, Any]) -> bool:
        """Update the subject context for a pipeline.

        Merges the provided context update into the existing pipeline state.

        Args:
            pipeline_id: The pipeline ID to update.
            context_update: Dictionary of context key-value pairs to merge.

        Returns:
            True if update was successful.

        Raises:
            StorageError: If pipeline not found or update fails.
        """
        # Check if pipeline exists
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="update",
                pipeline_id=pipeline_id,
            )

        try:
            with self._db.acquire() as conn:
                # Get current state
                cursor = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                )
                row: Row | None = cast(Row | None, cursor.fetchone())

                if row is None:
                    raise StorageError(
                        f"Pipeline not found: {pipeline_id}",
                        operation_type="update",
                        pipeline_id=pipeline_id,
                    )

                # Merge current state with update
                current_state = {}
                if row["state_json"]:
                    current_state = json.loads(cast(str, row["state_json"]))

                # Deep merge the context update
                current_state.update(context_update)
                updated_state_json = json.dumps(current_state)

                # Update the pipeline
                _ = conn.execute(
                    "UPDATE pipelines SET state_json = ?, "
                    + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (updated_state_json, pipeline_id),
                )

            return True
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(
                f"Failed to update subject context: {e}",
                operation_type="update",
                pipeline_id=pipeline_id,
            ) from e

    async def update_shared_context(
        self,
        pipeline_id: str,
        update: Any,
        operation: str = "set",
        key_path: str | None = None,
    ) -> bool:
        """Update shared_context within state_json.

        Updates the shared_context namespace in the pipeline's state_json.
        Supports set, append, and remove operations on nested keys.

        Args:
            pipeline_id: The pipeline to update.
            update: The value to set/append/remove.
            operation: One of "set", "append", "remove".
            key_path: Dot-separated path like "facts.market_scope" or "open_questions".

        Returns:
            True if successful.

        Raises:
            StorageError: If pipeline not found or update fails.
        """
        # Check if pipeline exists
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="update",
                pipeline_id=pipeline_id,
            )

        try:
            with self._db.acquire() as conn:
                # Get current state
                cursor = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                )
                row: Row | None = cast(Row | None, cursor.fetchone())

                if row is None:
                    raise StorageError(
                        f"Pipeline not found: {pipeline_id}",
                        operation_type="update",
                        pipeline_id=pipeline_id,
                    )

                # Parse current state
                current_state: dict[str, Any] = {}
                if row["state_json"]:
                    current_state = json.loads(cast(str, row["state_json"]))

                # Ensure shared_context exists
                if "shared_context" not in current_state:
                    current_state["shared_context"] = {}

                shared_context: dict[str, Any] = current_state["shared_context"]

                # Apply operation
                if operation == "set":
                    if key_path:
                        # Set at specific key path
                        keys = key_path.split(".")
                        target: dict[str, Any] = shared_context
                        for key in keys[:-1]:
                            if key not in target:
                                target[key] = {}
                            target = target[key]

                        final_key = keys[-1]
                        # If both existing and new values are dicts, merge them
                        if (
                            final_key in target
                            and isinstance(target[final_key], dict)
                            and isinstance(update, dict)
                        ):
                            update_dict: dict[str, Any] = update
                            self._deep_merge(target[final_key], update_dict)
                        else:
                            target[final_key] = update
                    else:
                        # Merge update into shared_context
                        if isinstance(update, dict):
                            update_dict_shared: dict[str, Any] = update
                            self._deep_merge(shared_context, update_dict_shared)
                        else:
                            raise StorageError(
                                "update must be a dict when merging into shared_context",
                                operation_type="update",
                                pipeline_id=pipeline_id,
                            )

                elif operation == "append":
                    if not key_path:
                        raise StorageError(
                            "key_path is required for append operation",
                            operation_type="update",
                            pipeline_id=pipeline_id,
                        )

                    keys = key_path.split(".")
                    append_target: dict[str, Any] = shared_context
                    for key in keys[:-1]:
                        if key not in append_target:
                            append_target[key] = {}
                        append_target = append_target[key]

                    final_key = keys[-1]
                    if final_key not in append_target:
                        append_target[final_key] = []

                    if not isinstance(append_target[final_key], list):
                        raise StorageError(
                            f"Cannot append to non-list at {key_path}",
                            operation_type="update",
                            pipeline_id=pipeline_id,
                        )

                    append_target[final_key].append(update)

                elif operation == "remove":
                    if not key_path:
                        raise StorageError(
                            "key_path is required for remove operation",
                            operation_type="update",
                            pipeline_id=pipeline_id,
                        )

                    keys = key_path.split(".")
                    target = shared_context
                    for key in keys[:-1]:
                        if key not in target:
                            return True  # Key doesn't exist, nothing to remove
                        target = target[key]

                    final_key = keys[-1]
                    if final_key in target:
                        del target[final_key]

                else:
                    raise StorageError(
                        f"Invalid operation: {operation}",
                        operation_type="update",
                        pipeline_id=pipeline_id,
                    )

                # Update the pipeline
                updated_state_json = json.dumps(current_state)
                conn.execute(
                    "UPDATE pipelines SET state_json = ?, "
                    + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (updated_state_json, pipeline_id),
                )

            return True
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(
                f"Failed to update shared context: {e}",
                operation_type="update",
                pipeline_id=pipeline_id,
            ) from e

    async def update_pipeline_state(
        self,
        pipeline_id: str,
        state_update: dict[str, Any],
    ) -> bool:
        """Update complete PipelineState in state_json.

        This method implements F1 requirement: state_json as single source of truth.
        It performs a deep merge of the update into the existing PipelineState.

        Args:
            pipeline_id: The pipeline ID to update.
            state_update: Dictionary of state fields to update.

        Returns:
            True if update was successful.

        Raises:
            StorageError: If pipeline not found or update fails.
        """
        # Check if pipeline exists
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="update",
                pipeline_id=pipeline_id,
            )

        try:
            with self._db.acquire() as conn:
                # Get current state
                cursor = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    raise StorageError(
                        f"Pipeline not found: {pipeline_id}",
                        operation_type="update",
                        pipeline_id=pipeline_id,
                    )

                # Parse current state
                current_state: dict[str, Any] = {}
                if row["state_json"]:
                    current_state = json.loads(cast(str, row["state_json"]))

                # Deep merge the update
                self._deep_merge(current_state, state_update)

                # Write back to database
                updated_state_json = json.dumps(current_state)
                conn.execute(
                    "UPDATE pipelines SET state_json = ?, "
                    + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (updated_state_json, pipeline_id),
                )

            return True
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(
                f"Failed to update pipeline state: {e}",
                operation_type="update",
                pipeline_id=pipeline_id,
            ) from e

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Deep merge source dict into target dict.

        Args:
            target: The dictionary to merge into (modified in place).
            source: The dictionary to merge from.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                value_dict: dict[str, Any] = value
                self._deep_merge(target[key], value_dict)
            else:
                target[key] = value

    def get_latest_successful_run(
        self,
        node_id: str,
        context_hash: str,
    ) -> dict[str, Any] | None:
        """Get the latest successful run for a node with matching context_hash.

        This method queries pipelines that have a matching context_hash in their
        state and retrieves the latest successful node result for the specified
        node_id.

        Args:
            node_id: The node identifier to search for.
            context_hash: The context hash to match against.

        Returns:
            Dictionary containing the node result with deliverable, or None if
            no successful run is found.
        """
        try:
            with self._db.acquire() as conn:
                # Query pipelines with matching context_hash in state_json
                cursor = conn.execute(
                    "SELECT pipeline_id, state_json FROM pipelines WHERE state_json LIKE ?",
                    (f'%"context_hash": "{context_hash}"%',),
                )
                rows = cursor.fetchall()

                if not rows:
                    return None

                # Find the latest successful run across all matching pipelines
                latest_result: dict[str, Any] | None = None
                latest_timestamp = None

                for row in rows:
                    pipeline_id = row["pipeline_id"]

                    # Get node results for this pipeline
                    result_cursor = conn.execute(
                        (
                            "SELECT id, node_id, iteration, deliverable_json, status, created_at "
                            "FROM node_results WHERE pipeline_id = ? AND node_id = ? AND status = ? "
                            "ORDER BY created_at DESC LIMIT 1"
                        ),
                        (pipeline_id, node_id, "completed"),
                    )
                    result_row = result_cursor.fetchone()

                    if result_row:
                        if latest_timestamp is None or result_row["created_at"] > latest_timestamp:
                            latest_timestamp = result_row["created_at"]
                            latest_result = {
                                "node_id": result_row["node_id"],
                                "iteration": result_row["iteration"],
                                "deliverable": (
                                    json.loads(result_row["deliverable_json"])
                                    if result_row["deliverable_json"]
                                    else None
                                ),
                                "status": result_row["status"],
                                "created_at": result_row["created_at"],
                            }

                return latest_result

        except Exception as e:
            logger.warning(
                "Error getting latest successful run for "
                + node_id
                + " with context_hash "
                + context_hash
                + ": "
                + str(e)
            )
            return None

    def list_node_runs(
        self,
        node_id: str,
        context_hash: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """List run history for a node with optional context_hash filter and pagination.

        Args:
            node_id: The node identifier to filter by.
            context_hash: Optional context hash to filter by.
            limit: Maximum number of runs to return (default 10).

        Returns:
            List of run dictionaries sorted by start_time DESC (newest first).

        Raises:
            StorageError: If query fails.
        """
        try:
            with self._db.acquire() as conn:
                if context_hash:
                    cursor = conn.execute(
                        "SELECT run_id, node_id, context_hash, start_time, end_time, "
                        + "status, deliverable_json, questions_json, evaluation_json "
                        + "FROM node_runs WHERE node_id = ? AND context_hash = ? "
                        + "ORDER BY start_time DESC LIMIT ?",
                        (node_id, context_hash, limit),
                    )
                else:
                    cursor = conn.execute(
                        "SELECT run_id, node_id, context_hash, start_time, end_time, "
                        + "status, deliverable_json, questions_json, evaluation_json "
                        + "FROM node_runs WHERE node_id = ? "
                        + "ORDER BY start_time DESC LIMIT ?",
                        (node_id, limit),
                    )

                runs: list[dict[str, Any]] = []
                for row in cast(list[Row], cursor.fetchall()):
                    runs.append(
                        {
                            "run_id": row["run_id"],
                            "node_id": row["node_id"],
                            "context_hash": row["context_hash"],
                            "start_time": row["start_time"],
                            "end_time": row["end_time"],
                            "status": row["status"],
                            "deliverable": (
                                json.loads(cast(str, row["deliverable_json"]))
                                if row["deliverable_json"]
                                else None
                            ),
                            "questions": (
                                json.loads(cast(str, row["questions_json"]))
                                if row["questions_json"]
                                else None
                            ),
                            "evaluation": (
                                json.loads(cast(str, row["evaluation_json"]))
                                if row["evaluation_json"]
                                else None
                            ),
                        }
                    )

                return runs
        except Exception as e:
            raise StorageError(
                f"Failed to list node runs: {e}",
                operation_type="read",
                node_id=node_id,
            ) from e

    def create_node_run(
        self,
        run_id: str,
        node_id: str,
        context_hash: str | None = None,
    ) -> bool:
        """Create a new node run record.

        Args:
            run_id: Unique run identifier (8-character UUID prefix).
            node_id: The node identifier.
            context_hash: Optional context hash for deduplication.

        Returns:
            True if creation was successful.

        Raises:
            StorageError: If creation fails.
        """
        try:
            with self._db.acquire() as conn:
                _ = conn.execute(
                    "INSERT INTO node_runs (run_id, node_id, context_hash, status) "
                    + "VALUES (?, ?, ?, ?)",
                    (run_id, node_id, context_hash, "running"),
                )
            return True
        except Exception as e:
            raise StorageError(
                f"Failed to create node run: {e}",
                operation_type="create",
                run_id=run_id,
                node_id=node_id,
            ) from e

    def update_node_run(
        self,
        run_id: str,
        status: str | None = None,
        deliverable: dict[str, Any] | None = None,
        questions: list[dict[str, Any]] | None = None,
        evaluation: dict[str, Any] | None = None,
    ) -> bool:
        """Update a node run with results.

        Args:
            run_id: The run identifier.
            status: Optional status update (default 'completed').
            deliverable: Optional deliverable data.
            questions: Optional questions list.
            evaluation: Optional evaluation data.

        Returns:
            True if update was successful.

        Raises:
            StorageError: If update fails.
        """
        try:
            with self._db.acquire() as conn:
                # Build update query dynamically
                updates: list[str] = []
                params: list[Any] = []

                if status is not None:
                    updates.append("status = ?")
                    params.append(status)

                if deliverable is not None:
                    updates.append("deliverable_json = ?")
                    params.append(json.dumps(deliverable))

                if questions is not None:
                    updates.append("questions_json = ?")
                    params.append(json.dumps(questions))

                if evaluation is not None:
                    updates.append("evaluation_json = ?")
                    params.append(json.dumps(evaluation))

                # Add end_time for completed runs
                if status == "completed":
                    updates.append("end_time = CURRENT_TIMESTAMP")

                if not updates:
                    return True

                params.append(run_id)
                query = f"UPDATE node_runs SET {', '.join(updates)} WHERE run_id = ?"

                cursor = conn.execute(query, params)
                if cursor.rowcount == 0:
                    return False
            return True
        except Exception as e:
            raise StorageError(
                f"Failed to update node run: {e}",
                operation_type="update",
                run_id=run_id,
            ) from e

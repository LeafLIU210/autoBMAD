"""Quality Metrics Collection module - Story 5.6.

This module provides database-backed metrics collection for node execution quality tracking.

Key components:
- NodeRunMetrics: Dataclass for individual node run metrics with database persistence
- MetricsCollector: Class for collecting metrics and generating quality reports

Features:
- Persists metrics to SQLite database
- Generates individual run reports
- Generates aggregate statistics per node_id
- Tracks force completion rates
"""

from dataclasses import dataclass
from statistics import mean
from typing import Any

from autoBMAD.docuswarm.exceptions import StorageError
from autoBMAD.docuswarm.storage.database import DatabaseManager


@dataclass
class NodeRunMetrics:
    """Metrics for a single node run.

    Attributes:
        run_id: Unique identifier for the node run
        node_id: The node identifier
        final_score: Final alignment score (0.0 to 1.0)
        iterations: Number of iterations executed
        verdict: Final verdict (APPROVED, FORCE_APPROVED, BLOCKED, NEEDS_REVISION)
        force_completed: Whether the node was force completed
    """

    run_id: str
    node_id: str
    final_score: float
    iterations: int
    verdict: str
    force_completed: bool = False


class MetricsCollector:
    """Collects and reports quality metrics with database persistence.

    Provides methods to record node run completion metrics, persist to database,
    and generate quality reports including aggregate statistics per node.

    Example:
        >>> collector = MetricsCollector()
        >>> collector.record_node_completion(
        ...     run_id="abc12345",
        ...     node_id="reviewer",
        ...     evaluation={"alignment_score": 0.85, "verdict": "APPROVED"},
        ...     iterations=3,
        ...     force_completed=False
        ... )
        >>> report = collector.generate_report("abc12345")
        >>> aggregate = collector.generate_node_aggregate_report("reviewer")
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize MetricsCollector with database connection.

        Args:
            db_path: Optional path to SQLite database. Defaults to "docuswarm.db".
        """
        self._db = DatabaseManager.get_instance(db_path=db_path or "docuswarm.db")

    def record_node_completion(
        self,
        run_id: str,
        node_id: str,
        evaluation: dict[str, Any],
        iterations: int,
        force_completed: bool = False,
    ) -> None:
        """Record node run completion metrics to database.

        Persists metrics including alignment score, iteration count, verdict,
        and force completion status to the node_run_metrics table.

        Args:
            run_id: Unique identifier for the node run
            node_id: The node identifier
            evaluation: Dictionary containing alignment_score and verdict
            iterations: Number of iterations executed
            force_completed: Whether the node was force completed

        Raises:
            StorageError: If metrics cannot be persisted to database
        """
        final_score = evaluation.get("alignment_score", 0.0)
        verdict = evaluation.get("verdict", "UNKNOWN")

        try:
            with self._db.acquire() as conn:
                _ = conn.execute(
                    "INSERT INTO node_run_metrics "
                    + "(run_id, node_id, final_score, iterations, verdict, force_completed) "
                    + "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        run_id,
                        node_id,
                        final_score,
                        iterations,
                        verdict,
                        1 if force_completed else 0,
                    ),
                )
        except Exception as e:
            raise StorageError(
                f"Failed to record node metrics: {e}",
                operation_type="create",
                run_id=run_id,
                node_id=node_id,
            ) from e

    def generate_report(self, run_id: str) -> dict[str, Any]:
        """Generate quality report for a specific node run.

        Args:
            run_id: The run identifier to generate report for

        Returns:
            Dictionary containing:
                - run_id: The run identifier
                - node_id: The node identifier
                - summary: Dictionary with iterations, final_score, verdict, force_completed
                - error: Error message if run not found
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT run_id, node_id, final_score, iterations, verdict, force_completed "
                    + "FROM node_run_metrics WHERE run_id = ?",
                    (run_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    return {"error": "Node run not found"}

                return {
                    "run_id": row["run_id"],
                    "node_id": row["node_id"],
                    "summary": {
                        "iterations": row["iterations"],
                        "final_score": round(row["final_score"], 3),
                        "verdict": row["verdict"],
                        "force_completed": bool(row["force_completed"]),
                    },
                }
        except Exception as e:
            return {"error": str(e)}

    def generate_node_aggregate_report(self, node_id: str) -> dict[str, Any]:
        """Generate aggregate report for all runs of a specific node.

        Calculates average score, average iterations, and force completion rate
        across all recorded runs for the specified node.

        Args:
            node_id: The node identifier to generate aggregate report for

        Returns:
            Dictionary containing:
                - node_id: The node identifier
                - total_runs: Total number of runs
                - average_score: Average final score across all runs
                - average_iterations: Average iterations per run
                - force_completions: Count of force completed runs
                - force_completion_rate: Percentage of force completed runs
                - error: Error message if no runs found
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT final_score, iterations, force_completed "
                    + "FROM node_run_metrics WHERE node_id = ?",
                    (node_id,),
                )
                rows = cursor.fetchall()

                if not rows:
                    return {"error": "No runs found for node"}

                total_runs = len(rows)
                scores = [row["final_score"] for row in rows]
                iterations_list = [row["iterations"] for row in rows]
                force_count = sum(1 for row in rows if row["force_completed"])

                return {
                    "node_id": node_id,
                    "total_runs": total_runs,
                    "average_score": round(mean(scores), 3),
                    "average_iterations": round(mean(iterations_list), 1),
                    "force_completions": force_count,
                    "force_completion_rate": round(force_count / total_runs * 100, 1),
                }
        except Exception as e:
            return {"error": str(e)}

    def get_node_run_metrics(self, run_id: str) -> NodeRunMetrics | None:
        """Retrieve NodeRunMetrics for a specific run.

        Args:
            run_id: The run identifier to retrieve metrics for

        Returns:
            NodeRunMetrics instance if found, None otherwise
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT run_id, node_id, final_score, iterations, verdict, force_completed "
                    + "FROM node_run_metrics WHERE run_id = ?",
                    (run_id,),
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                return NodeRunMetrics(
                    run_id=row["run_id"],
                    node_id=row["node_id"],
                    final_score=row["final_score"],
                    iterations=row["iterations"],
                    verdict=row["verdict"],
                    force_completed=bool(row["force_completed"]),
                )
        except Exception:
            return None

    def list_node_runs(self, node_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """List recent node runs with metrics for a specific node.

        Args:
            node_id: The node identifier
            limit: Maximum number of runs to return (default 10)

        Returns:
            List of run dictionaries sorted by created_at DESC
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT run_id, node_id, final_score, iterations, verdict, "
                    + "force_completed, created_at "
                    + "FROM node_run_metrics WHERE node_id = ? "
                    + "ORDER BY created_at DESC LIMIT ?",
                    (node_id, limit),
                )

                runs: list[dict[str, Any]] = []
                for row in cursor.fetchall():
                    runs.append(
                        {
                            "run_id": row["run_id"],
                            "node_id": row["node_id"],
                            "final_score": row["final_score"],
                            "iterations": row["iterations"],
                            "verdict": row["verdict"],
                            "force_completed": bool(row["force_completed"]),
                            "created_at": row["created_at"],
                        }
                    )

                return runs
        except Exception:
            return []

"""Quality Metrics Collection module - Story 5.6.

This module provides metrics collection for pipeline execution quality tracking.

Key components:
- NodeMetrics: Dataclass for individual node execution metrics
- PipelineMetrics: Dataclass for overall pipeline metrics
- MetricsCollector: Class for collecting and generating reports on pipeline metrics
- CompletionStatus: Enum for pipeline completion states
"""

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Any


class CompletionStatus(Enum):
    """Possible completion status values for pipeline execution.

    - PENDING: Pipeline has not yet completed
    - PASSED: Pipeline completed successfully
    - FAILED: Pipeline failed
    - BLOCKED: Pipeline was blocked
    """

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class NodeMetrics:
    """Metrics for a single node execution.

    Attributes:
        node_id: The unique identifier of the node
        final_score: The final alignment score (0.0 to 1.0)
        iterations: Number of iterations executed
        verdict: Final verdict (APPROVED, FORCE_APPROVED, BLOCKED, NEEDS_REVISION)
        force_completed: Whether the node was force completed
    """

    node_id: str
    final_score: float
    iterations: int
    verdict: str
    force_completed: bool = False


@dataclass
class PipelineMetrics:
    """Metrics for an entire pipeline execution.

    Attributes:
        nodes: Dictionary of node_id to NodeMetrics
        total_iterations: Total iterations across all nodes
        average_score: Average final score across all nodes
        completion_status: Current completion status
    """

    nodes: dict[str, NodeMetrics] = field(default_factory=dict)
    total_iterations: int = 0
    average_score: float = 0.0
    completion_status: str = "pending"


class MetricsCollector:
    """Collects and manages quality metrics for pipeline execution.

    Provides methods to record node completion metrics, finalize pipeline
    completion status, and generate structured quality reports.

    Example:
        collector = MetricsCollector()
        collector.record_node_completion(
            pipeline_id="pipeline-1",
            node_id="reviewer",
            final_score=0.85,
            iterations=3,
            verdict="APPROVED",
            force_completed=False
        )
        collector.finalize_pipeline("pipeline-1", "passed")
        report = collector.generate_report("pipeline-1")
    """

    def __init__(self) -> None:
        """Initialize MetricsCollector with empty metrics storage."""
        self._metrics: dict[str, PipelineMetrics] = {}

    def record_node_completion(
        self,
        pipeline_id: str,
        node_id: str,
        final_score: float,
        iterations: int,
        verdict: str,
        force_completed: bool = False,
    ) -> None:
        """Record metrics for a completed node.

        Creates a new PipelineMetrics if one doesn't exist for the pipeline,
        or updates existing metrics for the same node_id.

        Args:
            pipeline_id: Unique identifier for the pipeline
            node_id: Unique identifier for the node
            final_score: Final alignment score (0.0 to 1.0)
            iterations: Number of iterations executed
            verdict: Final verdict (APPROVED, FORCE_APPROVED, BLOCKED, NEEDS_REVISION)
            force_completed: Whether the node was force completed
        """
        # Create new pipeline metrics if needed
        if pipeline_id not in self._metrics:
            self._metrics[pipeline_id] = PipelineMetrics()

        pipeline_metrics = self._metrics[pipeline_id]

        # Create or update node metrics
        node_metrics = NodeMetrics(
            node_id=node_id,
            final_score=final_score,
            iterations=iterations,
            verdict=verdict,
            force_completed=force_completed,
        )
        pipeline_metrics.nodes[node_id] = node_metrics

        # Recalculate total iterations
        pipeline_metrics.total_iterations = sum(
            node.iterations for node in pipeline_metrics.nodes.values()
        )

        # Recalculate average score
        if pipeline_metrics.nodes:
            pipeline_metrics.average_score = mean(
                node.final_score for node in pipeline_metrics.nodes.values()
            )
        else:
            pipeline_metrics.average_score = 0.0

    def finalize_pipeline(
        self,
        pipeline_id: str,
        completion_status: str,
    ) -> None:
        """Mark pipeline as complete with the given status.

        Args:
            pipeline_id: Unique identifier for the pipeline
            completion_status: Final status (passed, failed, blocked)
        """
        # Create pipeline metrics if needed
        if pipeline_id not in self._metrics:
            self._metrics[pipeline_id] = PipelineMetrics()

        self._metrics[pipeline_id].completion_status = completion_status

    def generate_report(self, pipeline_id: str) -> dict[str, Any]:
        """Generate a quality report for the specified pipeline.

        Args:
            pipeline_id: Unique identifier for the pipeline

        Returns:
            Dictionary containing:
                - pipeline_id: The pipeline identifier
                - nodes: Dictionary of node metrics
                - total_iterations: Total iterations across all nodes
                - average_score: Average final score
                - completion_status: Pipeline completion status
                - force_completion_count: Number of force completed nodes
                - error: Error message if pipeline not found
        """
        if pipeline_id not in self._metrics:
            return {"error": "Pipeline not found"}

        metrics = self._metrics[pipeline_id]

        # Count force completions
        force_completion_count = sum(1 for node in metrics.nodes.values() if node.force_completed)

        return {
            "pipeline_id": pipeline_id,
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "final_score": node.final_score,
                    "iterations": node.iterations,
                    "verdict": node.verdict,
                    "force_completed": node.force_completed,
                }
                for node_id, node in metrics.nodes.items()
            },
            "total_iterations": metrics.total_iterations,
            "average_score": metrics.average_score,
            "completion_status": metrics.completion_status,
            "force_completion_count": force_completion_count,
        }

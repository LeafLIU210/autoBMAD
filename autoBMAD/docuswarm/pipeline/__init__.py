"""Pipeline orchestration module."""

from autoBMAD.docuswarm.pipeline.escalation import (
    Escalation,
    EscalationHandler,
    EscalationReason,
)
from autoBMAD.docuswarm.pipeline.force_completion import (
    ForceCompletion,
    ForceCompletionHandler,
    create_force_completion,
)
from autoBMAD.docuswarm.pipeline.graph import (
    PIPELINE_NODES,
    create_graph_config,
    create_pipeline_graph,
)
from autoBMAD.docuswarm.pipeline.orchestrator import (
    ContextValidationError,
    DependencyError,
    HybridOrchestrator,
    OrchestratorError,
    PipelineAlreadyCompletedError,
    PipelineNotFoundError,
)
from autoBMAD.docuswarm.pipeline.quality import (
    QualityConfig,
    QualityThresholds,
    Verdict,
    VerdictDeterminer,
)
from autoBMAD.docuswarm.pipeline.state import (
    APPROVED,
    BLOCKED,
    COMPLETED,
    FAILED,
    NEEDS_REVISION,
    NODE_STATUS,
    PAUSED,
    PENDING,
    PIPELINE_STATUS,
    RUNNING,
    NodeResult,
    PipelineState,
    create_initial_state,
    deserialize_state,
    serialize_state,
    validate_state,
)

__all__ = [
    # Escalation exports
    "Escalation",
    "EscalationHandler",
    "EscalationReason",
    # Force completion exports
    "ForceCompletion",
    "ForceCompletionHandler",
    "create_force_completion",
    # Graph exports
    "PIPELINE_NODES",
    "create_pipeline_graph",
    "create_graph_config",
    # Orchestrator exports
    "HybridOrchestrator",
    "OrchestratorError",
    "ContextValidationError",
    "DependencyError",
    "PipelineNotFoundError",
    "PipelineAlreadyCompletedError",
    # Quality exports
    "QualityConfig",
    "QualityThresholds",
    "Verdict",
    "VerdictDeterminer",
    # State exports
    "NodeResult",
    "PipelineState",
    "create_initial_state",
    "validate_state",
    "serialize_state",
    "deserialize_state",
    "PIPELINE_STATUS",
    "NODE_STATUS",
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "PAUSED",
    "APPROVED",
    "NEEDS_REVISION",
    "BLOCKED",
]

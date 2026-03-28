"""Node execution module for LangGraph individual node state management."""

from typing import TYPE_CHECKING, Any

# Single Context Protocol contracts (these have no dependencies)
from autoBMAD.docuswarm.node_execution.contracts import (
    DeliverableRequirements,
    EvaluatorAgentInput,
    EvaluatorOutput,
    IndependentAgentInput,
    IndependentOutput,
    NodeExecutionContext,
)


# Other imports are lazy to avoid circular dependencies
def __getattr__(name: str) -> Any:
    """Lazy import to avoid circular dependencies."""
    if name == "create_node_executor":
        from autoBMAD.docuswarm.node_execution.executor import create_node_executor

        return create_node_executor
    elif name == "NodeExecutionContextBuilder":
        from autoBMAD.docuswarm.node_execution.context_builder import NodeExecutionContextBuilder

        return NodeExecutionContextBuilder
    elif name == "create_context_builder":
        from autoBMAD.docuswarm.node_execution.context_builder import create_context_builder

        return create_context_builder
    elif name == "ContextChainer":
        from autoBMAD.docuswarm.node_execution.chaining import ContextChainer

        return ContextChainer
    elif name == "SEQUENCE":
        from autoBMAD.docuswarm.node_execution.chaining import SEQUENCE

        return SEQUENCE
    elif name == "get_sequence":
        from autoBMAD.docuswarm.node_execution.chaining import get_sequence

        return get_sequence
    elif name == "get_predecessors":
        from autoBMAD.docuswarm.node_execution.chaining import get_predecessors

        return get_predecessors
    elif name in [
        "execute_node_flow",
        "export_output",
        "generate_context_hash",
        "generate_run_id",
        "get_chained_context",
        "load_context_file",
        "save_node_run",
    ]:
        from autoBMAD.docuswarm.node_execution import flow

        return getattr(flow, name)
    elif name in [
        "create_node_execution_graph",
        "create_node_execution_config",
        "create_checkpoint_config",
    ]:
        from autoBMAD.docuswarm.node_execution import graph

        return getattr(graph, name)
    elif name in ["MetricsCollector", "NodeRunMetrics"]:
        from autoBMAD.docuswarm.node_execution import metrics

        return getattr(metrics, name)
    elif name == "NodeRunTracker":
        from autoBMAD.docuswarm.node_execution import run_tracker

        return run_tracker.NodeRunTracker
    elif name in [
        "BLOCKED",
        "COMPLETED",
        "FAILED",
        "NODE_STATUS",
        "PENDING",
        "RUNNING",
        "VALID_STATUSES",
        "NodeResult",
        "NodeRunState",
        "create_node_result",
        "create_node_run_state",
        "deserialize_node_result",
        "deserialize_node_run_state",
        "is_valid_status",
        "serialize_node_result",
        "serialize_node_run_state",
        "update_node_run_state",
        "validate_node_result",
        "validate_node_run_state",
    ]:
        from autoBMAD.docuswarm.node_execution import state

        return getattr(state, name)
    elif name == "ContextValidator":
        from autoBMAD.docuswarm.node_execution import validator

        return validator.ContextValidator
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# TYPE_CHECKING imports for static analysis only
if TYPE_CHECKING:
    # Import all dynamically loaded symbols for type checking
    from autoBMAD.docuswarm.node_execution.chaining import (
        SEQUENCE,
        ContextChainer,
        get_predecessors,
        get_sequence,
    )
    from autoBMAD.docuswarm.node_execution.context_builder import (
        NodeExecutionContextBuilder,
        create_context_builder,
    )
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor
    from autoBMAD.docuswarm.node_execution.flow import (
        execute_node_flow,
        export_output,
        generate_context_hash,
        generate_run_id,
        get_chained_context,
        load_context_file,
        save_node_run,
    )
    from autoBMAD.docuswarm.node_execution.graph import (
        create_checkpoint_config,
        create_node_execution_config,
        create_node_execution_graph,
    )
    from autoBMAD.docuswarm.node_execution.metrics import MetricsCollector, NodeRunMetrics
    from autoBMAD.docuswarm.node_execution.run_tracker import NodeRunTracker
    from autoBMAD.docuswarm.node_execution.state import (
        BLOCKED,
        COMPLETED,
        FAILED,
        NODE_STATUS,
        PENDING,
        RUNNING,
        VALID_STATUSES,
        NodeResult,
        NodeRunState,
        create_node_result,
        create_node_run_state,
        deserialize_node_result,
        deserialize_node_run_state,
        is_valid_status,
        serialize_node_result,
        serialize_node_run_state,
        update_node_run_state,
        validate_node_result,
        validate_node_run_state,
    )
    from autoBMAD.docuswarm.node_execution.validator import ContextValidator

__all__ = [
    # Single Context Protocol contracts
    "NodeExecutionContext",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
    "DeliverableRequirements",
    "IndependentOutput",
    "EvaluatorOutput",
    # Builder
    "NodeExecutionContextBuilder",
    "create_context_builder",
    # Graph factory functions
    "create_node_execution_graph",
    "create_node_execution_config",
    "create_checkpoint_config",
    # Node executor factory
    "create_node_executor",
    # Status constants
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "BLOCKED",
    "VALID_STATUSES",
    "NODE_STATUS",
    # TypedDicts
    "NodeResult",
    "NodeRunState",
    # Factory functions
    "create_node_result",
    "create_node_run_state",
    "update_node_run_state",
    # Validation helpers
    "validate_node_result",
    "validate_node_run_state",
    "is_valid_status",
    # Serialization
    "serialize_node_run_state",
    "deserialize_node_run_state",
    "serialize_node_result",
    "deserialize_node_result",
    # Context validator
    "ContextValidator",
    # Context chainer
    "ContextChainer",
    "SEQUENCE",
    "get_sequence",
    "get_predecessors",
    # Node execution flow
    "execute_node_flow",
    "export_output",
    "generate_context_hash",
    "generate_run_id",
    "get_chained_context",
    "load_context_file",
    "save_node_run",
    # Node run tracker
    "NodeRunTracker",
    # Quality metrics
    "NodeRunMetrics",
    "MetricsCollector",
]

"""LangGraph StateGraph Definition - Story 3.3.

This module defines the LangGraph StateGraph for the DocuSwarm pipeline with:
- 5 nodes: analyst, pm, ux, architect, po
- Sequential edges: analyst → pm → ux → architect → po
- START and END connections
- SqliteSaver checkpointer support
- Thread configuration for isolation
- Context accumulation and deliverable passing (Story 3.7)
- Node execution integration via node_execution.executor (Story 11.4)
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Any, TypeVar

import structlog
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import (  # type: ignore[import-untyped, reportMissingTypeStubs]
    END,
    StateGraph,
)

# Import StateGraph type only for type checking to avoid runtime issues
if TYPE_CHECKING:
    from langgraph.graph import StateGraph

from langgraph.checkpoint.base import BaseCheckpointSaver

from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import (
    PIPELINE_NODES,
    PipelineState,
    finalize_pipeline_state,
)
from autoBMAD.docuswarm.storage.checkpoints import (
    create_checkpoint_config,
    generate_thread_id,
)

# Configure module logger
logger = structlog.get_logger(__name__)

# Type variable for state
T = TypeVar("T", bound=Mapping[str, Any])


def _create_integrated_node_executor(
    node_id: str,
    session_manager: Any,
) -> Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]:
    """Create an integrated node executor that uses node_execution.executor.

    This function creates a node executor that:
    - Uses lazy import to avoid circular imports
    - Calls create_node_executor() from node_execution.executor module
    - Converts PipelineState to NodeRunState for execution
    - Converts NodeRunState back to PipelineState after execution
    - Saves deliverables via FileStorage after successful execution

    Args:
        node_id: The node identifier.
        session_manager: SessionManager instance for SDK interactions.

    Returns:
        An async callable that processes the state using the integrated executor.
    """
    # Lazy import to avoid circular imports
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor

    # Create the async node executor
    async_node_executor = create_node_executor(node_id, session_manager)

    async def executor(state: dict[str, Any]) -> dict[str, Any]:
        """Execute node logic using integrated node_execution.executor."""
        import copy as copy_module

        # Deep copy state to avoid mutation issues
        new_state: dict[str, Any] = copy_module.deepcopy(state)

        # Update current_node
        new_state["current_node"] = node_id

        # Initialize fields if not present
        if "completed_nodes" not in new_state:
            new_state["completed_nodes"] = []
        if "node_iterations" not in new_state:
            new_state["node_iterations"] = {}
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}
        if "questions" not in new_state:
            new_state["questions"] = {}
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}

        # Story 37.5: Extract docs_context_summary from pipeline state
        # and pass explicitly to PipelineAdapter for propagation to NodeRunState
        docs_context_summary = new_state.get("docs_context_summary", [])

        # CHANGED: Use PipelineAdapter for state conversion with explicit docs_context_summary
        node_run_state = PipelineAdapter.convert_pipeline_to_node_state(
            new_state, node_id, docs_context_summary=docs_context_summary
        )

        # Run the async executor
        result_state: dict[str, Any] = new_state  # Default to new_state for error case
        try:
            executed_node_state = await async_node_executor(node_run_state)

            # CHANGED: Use PipelineAdapter for reverse conversion
            converted_state = PipelineAdapter.convert_node_to_pipeline_state(
                executed_node_state, new_state
            )
            # Ensure we return a dict, not PipelineState
            result_state = (
                dict(converted_state) if hasattr(converted_state, "items") else converted_state
            )

            # P0 Single Truth: File is already saved by create_deliverable tool
            # No need to save again here. The deliverable in executed_node_state
            # should already be metadata-only (DeliverableArtifact format).
            # If additional file operations are needed, they should be handled
            # by the tool or node executor, not here.

        except Exception as e:
            logger.error(
                "integrated_executor_error",
                node_id=node_id,
                error=str(e),
            )
            # P0-F1: Set error and failed_nodes on exception
            result_state["status"] = "failed"
            result_state["deliverables"][node_id] = {}
            if "failed_nodes" not in result_state:
                result_state["failed_nodes"] = []
            if node_id not in result_state["failed_nodes"]:
                result_state["failed_nodes"] = result_state["failed_nodes"] + [node_id]
            if not result_state.get("first_failed_node"):
                result_state["first_failed_node"] = node_id
            result_state["error"] = {
                "node_id": node_id,
                "error_type": type(e).__name__,
                "message": str(e),
            }
            # Do NOT increment iteration or add to completed_nodes on error
            return result_state

        # P1-1 Fix: Use the iteration value reported by the node executor directly,
        # rather than incrementing unconditionally. This ensures node_iterations
        # reflects actual rounds executed by DualAgentNode.
        node_status = executed_node_state.get("status", "")
        if node_status != "failed":
            actual_iteration = executed_node_state.get("iteration", 1)
            result_state["node_iterations"][node_id] = actual_iteration
        else:
            if "failed_nodes" not in result_state:
                result_state["failed_nodes"] = []
            if node_id not in result_state["failed_nodes"]:
                result_state["failed_nodes"] = result_state["failed_nodes"] + [node_id]
            if not result_state.get("first_failed_node"):
                result_state["first_failed_node"] = node_id

        return result_state

    return executor


def create_pipeline_graph(
    checkpointer: BaseCheckpointSaver[Any] | None = None,
    compile_graph: bool = True,
    *,  # Force keyword-only argument for session_manager
    session_manager: Any,
) -> Any:
    """Create the pipeline StateGraph with all nodes and edges.

    This creates a LangGraph StateGraph with:
    - 5 nodes: analyst, pm, ux, architect, po
    - Sequential edges: analyst → pm → ux → architect → po
    - START and END connections
    - Integrated node execution via node_execution.executor (Story 11.4)

    Args:
        checkpointer: Optional existing checkpointer to use.
        compile_graph: If True (default), returns compiled graph. If False,
                      returns uncompiled StateGraph.
        session_manager: **REQUIRED** SessionManager for integrated node
            execution. The deprecated default executor has been removed.

    Returns:
        StateGraph (uncompiled) or CompiledStateGraph ready for execution.

    Raises:
        ValueError: If session_manager is None.

    Example:
        >>> # With session_manager for integrated execution (required)
        >>> from autoBMAD.docuswarm.llm.session_manager import SessionManager
        >>> session_manager = SessionManager(...)
        >>> graph = create_pipeline_graph(session_manager=session_manager)
        >>> compiled = graph.compile()
    """
    # NEW: Hard fail on missing session_manager
    if session_manager is None:
        raise ValueError(
            "session_manager is required for pipeline execution. "
            "The deprecated default executor was removed in Story 11.6. "
            "Please provide a valid SessionManager instance."
        )

    # Create the StateGraph with PipelineState schema
    graph = StateGraph(PipelineState)

    # Always use integrated executor now
    logger.info(
        "using_integrated_node_executor",
        message="Using integrated node_execution.executor for node execution",
    )

    # Add all 5 nodes to the graph using integrated executor
    for node_id in PIPELINE_NODES:
        node_executor = _create_integrated_node_executor(node_id, session_manager)
        # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
        graph.add_node(node_id, node_executor)

    # Add finalization node to mark pipeline as completed
    def finalize_executor(state: dict[str, Any]) -> PipelineState:
        """Finalize the pipeline state when all nodes complete."""
        return finalize_pipeline_state(state)

    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_node("__finalize__", finalize_executor)

    # P1 Fix: Add conditional edges for dependency failure short-circuit.
    # If any node has failed, skip directly to finalize.
    async def _route_after_node(state: dict[str, Any]) -> str:
        if state.get("failed_nodes"):
            return "__finalize__"
        return "__continue__"

    # Add conditional edges for each node
    for i, node_id in enumerate(PIPELINE_NODES):
        next_target = PIPELINE_NODES[i + 1] if i + 1 < len(PIPELINE_NODES) else "__finalize__"
        # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
        graph.add_conditional_edges(
            node_id,
            _route_after_node,
            {"__finalize__": "__finalize__", "__continue__": next_target},
        )

    # Connect START to analyst
    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_edge("__start__", "analyst")

    # Connect finalize to END
    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_edge("__finalize__", END)

    # If compile_graph is True, compile and return
    if compile_graph:
        # Compile the graph with optional checkpointer
        # type: ignore[reportUnknownMemberType]
        compiled: Runnable[dict[str, Any], dict[str, Any]] = graph.compile(
            checkpointer=checkpointer
        )
        return compiled

    return graph


def create_graph_config(pipeline_id: str) -> RunnableConfig:
    """Create a configuration dict for graph execution with thread isolation.

    Args:
        pipeline_id: The unique pipeline identifier.

    Returns:
        Configuration dict with thread_id for isolation.

    Example:
        >>> config = create_graph_config("pipeline-123")
        >>> result = await graph.ainvoke(state, config)
    """
    thread_id = generate_thread_id(pipeline_id)
    return create_checkpoint_config(thread_id)


# =============================================================================
# Test Utilities - MockNodeExecutor for unit testing without LLM
# =============================================================================


class MockNodeExecutor:
    """Mock node executor for unit testing pipeline flow without LLM.

    This class provides a test double for the integrated node executor,
    returning mock deliverables with placeholder content for testing
    pipeline flow without requiring actual LLM execution.

    Example:
        >>> mock_executor = MockNodeExecutor()
        >>> # Use with create_pipeline_graph
        >>> from autoBMAD.docuswarm.llm.session_manager import SessionManager
        >>> session_manager = SessionManager(...)  # or mock
        >>> # Create pipeline with mock
        >>> graph = create_pipeline_graph(session_manager=session_manager)
    """

    # Default mock deliverables by node type
    DEFAULT_MOCK_DELIVERABLES: dict[str, dict[str, Any]] = {
        "analyst": {
            "content": "Mock analysis deliverable for testing",
            "findings": ["Finding 1", "Finding 2"],
            "recommendations": ["Recommendation 1"],
        },
        "pm": {
            "content": "Mock requirements deliverable for testing",
            "requirements": ["Requirement 1", "Requirement 2"],
            "priorities": {"high": 1, "medium": 2, "low": 3},
        },
        "ux": {
            "content": "Mock design deliverable for testing",
            "wireframes": ["Wireframe 1"],
            "user_flows": ["User Flow 1"],
        },
        "architect": {
            "content": "Mock architecture deliverable for testing",
            "components": ["Component A", "Component B"],
            "technologies": ["Tech 1", "Tech 2"],
        },
        "po": {
            "content": "Mock product vision deliverable for testing",
            "vision": "Mock product vision statement",
            "success_metrics": ["Metric 1", "Metric 2"],
        },
    }

    def __init__(
        self,
        custom_deliverables: dict[str, dict[str, Any]] | None = None,
        mock_evaluation: dict[str, Any] | None = None,
        mock_questions: list[dict[str, str]] | None = None,
    ):
        """Initialize MockNodeExecutor.

        Args:
            custom_deliverables: Optional custom deliverable content by node_id.
                                 If not provided, uses DEFAULT_MOCK_DELIVERABLES.
            mock_evaluation: Optional mock evaluation result. Defaults to APPROVED.
            mock_questions: Optional mock questions to return.
        """
        self._deliverables = custom_deliverables or self.DEFAULT_MOCK_DELIVERABLES
        self._evaluation = mock_evaluation or {"verdict": "APPROVED", "alignment_score": 0.95}
        self._questions = mock_questions or []

    def __call__(self, node_state: dict[str, Any]) -> dict[str, Any]:
        """Execute mock node execution synchronously.

        This method can be used directly as a node executor function,
        or wrapped with functools.partial for use with create_pipeline_graph.

        Args:
            node_state: The node state dictionary (NodeRunState format).

        Returns:
            Updated node state with mock deliverable, evaluation, and questions.
        """
        node_id = node_state.get("node_id", "unknown")
        iteration = node_state.get("iteration", 1)

        # Get mock deliverable for this node, or create a generic one
        deliverable = self._deliverables.get(
            node_id,
            {
                "content": f"Mock deliverable for {node_id} at iteration {iteration}",
                "mock": True,
            },
        )

        # Return updated node state
        return {
            **node_state,
            "deliverable": deliverable,
            "evaluation": self._evaluation,
            "questions": self._questions,
            "iteration": iteration + 1,
            "status": "completed",
        }

    async def execute_async(self, node_state: dict[str, Any]) -> dict[str, Any]:
        """Execute mock node execution asynchronously.

        This async method provides compatibility with the async executor pattern.

        Args:
            node_state: The node state dictionary (NodeRunState format).

        Returns:
            Updated node state with mock deliverable, evaluation, and questions.
        """
        # Simulate async behavior
        import asyncio

        await asyncio.sleep(0)  # Yield to event loop
        return self(node_state)


def create_mock_node_executor(
    node_id: str,
    _session_manager: Any | None = None,
    custom_deliverable: dict[str, Any] | None = None,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create a mock node executor for testing without LLM.

    This factory function creates a mock executor that returns
    predictable mock deliverables for pipeline testing.

    Args:
        node_id: The node identifier this executor is for.
        session_manager: Optional session manager (ignored in mock).
        custom_deliverable: Optional custom deliverable to return.
                           If not provided, uses MockNodeExecutor defaults.

    Returns:
        A callable executor function that returns mock node states.

    Example:
        >>> executor = create_mock_node_executor("analyst")
        >>> result = executor(node_state)
        >>> assert result["deliverable"]["content"]
    """
    # Build custom deliverables dict if custom_deliverable provided
    deliverables = None
    if custom_deliverable:
        deliverables = {node_id: custom_deliverable}

    mock_executor = MockNodeExecutor(custom_deliverables=deliverables)
    return mock_executor


__all__ = [
    "PIPELINE_NODES",
    "create_pipeline_graph",
    "create_graph_config",
    # Story 11.6 - Test utilities
    "MockNodeExecutor",
    "create_mock_node_executor",
]

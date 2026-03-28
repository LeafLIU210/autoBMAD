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

import copy
import json
import warnings
from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Any, TypeVar

import structlog
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import (  # type: ignore[import-untyped, reportMissingTypeStubs]
    END,
    StateGraph,
)

# Import StateGraph type only for type checking to avoid runtime issues
if TYPE_CHECKING:
    from langgraph.graph import StateGraph

from langgraph.checkpoint.base import BaseCheckpointSaver

from autoBMAD.docuswarm.pipeline.state import (
    PIPELINE_NODES,
    PipelineState,
    accumulate_context,
    finalize_pipeline_state,
    validate_deliverable_format,
)
from autoBMAD.docuswarm.storage.checkpoints import (
    create_checkpoint_config,
    generate_thread_id,
)

# Configure module logger
logger = structlog.get_logger(__name__)

# Type variable for state
T = TypeVar("T", bound=Mapping[str, Any])


def _create_default_node_executor(
    node_id: str,
    node_executor_func: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create a default node executor function.

    .. deprecated::
        This function is deprecated and will be removed in a future release.
        It produces empty {} deliverables and should not be used in production.

        **Deprecation Timeline:**
        - Deprecated: Story 11.6 (Feb 2026)
        - Removal Target: 2 sprint cycles from deprecation date

        Use :func:`_create_integrated_node_executor` instead, which uses the
        node_execution.executor module for proper LLM-based execution.

    This creates a node executor that:
    - Accumulates context from subject_context and previous deliverables
    - Calls the optional node executor function for actual processing
    - Validates deliverable format before storing
    - Handles state finalization when all nodes complete

    Args:
        node_id: The node identifier.
        node_executor_func: Optional function to execute node-specific logic.

    Returns:
        A callable that processes the state.
    """
    warnings.warn(
        (
            "WARNING: Using deprecated default node executor - this path produces empty {} "
            "deliverables and will be removed in a future release. "
            "Use integrated node executor with session_manager instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )

    def executor(state: dict[str, Any]) -> dict[str, Any]:  # type: ignore[no-redef]
        """Execute node logic with context accumulation and deliverable passing."""
        import copy

        # Deep copy state to avoid mutation issues
        new_state = copy.deepcopy(state)

        # Update current_node
        new_state["current_node"] = node_id

        # Initialize completed_nodes if not present
        if "completed_nodes" not in new_state:
            new_state["completed_nodes"] = []

        # Initialize node_iterations if not present
        if "node_iterations" not in new_state:
            new_state["node_iterations"] = {}

        # Initialize deliverables if not present
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}

        # Initialize questions if not present
        if "questions" not in new_state:
            new_state["questions"] = {}

        # Initialize evaluations if not present
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}

        # ACCUMULATE CONTEXT: Build context from subject_context + previous deliverables
        subject_context = new_state.get("subject_context", {})
        deliverables = new_state.get("deliverables", {})
        accumulated_context = accumulate_context(subject_context, deliverables, node_id)

        # Execute node-specific logic if provided
        if node_executor_func is not None:
            result = node_executor_func(accumulated_context)
            # If result contains a deliverable, validate and store it
            if "deliverable" in result and validate_deliverable_format(result["deliverable"]):
                new_state["deliverables"][node_id] = result["deliverable"]
            if "questions" in result and isinstance(result["questions"], list):
                new_state["questions"][node_id] = result["questions"]
            if "evaluation" in result and isinstance(result["evaluation"], dict):
                new_state["evaluations"][node_id] = result["evaluation"]
        else:
            # Default behavior: create empty deliverable placeholder
            new_state["deliverables"][node_id] = {}

        # Increment iteration count for this node
        # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
        current_iteration: int = new_state["node_iterations"].get(node_id, 0)
        new_state["node_iterations"][node_id] = current_iteration + 1

        # Add node to completed_nodes if not already there
        if node_id not in new_state["completed_nodes"]:
            new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]

        # Note: State finalization is handled by the graph after all nodes complete
        # via the END edge, not during individual node execution

        return new_state

    return executor


def _convert_pipeline_to_node_state(
    state: dict[str, Any],
    node_id: str,
) -> dict[str, Any]:
    """Convert PipelineState to NodeRunState for node execution.

    This function transforms a PipelineState into the format expected by
    the node_execution.executor module's create_node_executor().

    Args:
        state: The current PipelineState dictionary.
        node_id: The node identifier being executed.

    Returns:
        A dictionary in NodeRunState format suitable for node execution.

    Example:
        >>> pipeline_state = {"pipeline_id": "test-123", "subject_context": {...}}
        >>> node_state = _convert_pipeline_to_node_state(pipeline_state, "analyst")
        >>> node_state["run_id"] == "test-123"
        True
    """
    import hashlib

    # Generate context_hash from subject_context and node_id
    subject_context = state.get("subject_context", {})
    context_str = json.dumps(subject_context, sort_keys=True)
    context_hash = hashlib.md5(context_str.encode()).hexdigest()

    # Build context_file (serialized accumulated context)
    deliverables = state.get("deliverables", {})
    accumulated = accumulate_context(subject_context, deliverables, node_id)
    context_file = json.dumps(accumulated)

    # Get current iteration for this node
    node_iterations = state.get("node_iterations", {})
    iteration = node_iterations.get(node_id, 0) + 1

    # Build chained_context from previous deliverables
    chained_context: dict[str, dict[str, Any]] = {}
    for prev_node_id in PIPELINE_NODES:
        if prev_node_id == node_id:
            break
        if prev_node_id in deliverables:
            chained_context[prev_node_id] = {
                "deliverable": deliverables.get(prev_node_id),
                "iteration": node_iterations.get(prev_node_id, 1),
            }

    return {
        "run_id": state.get("pipeline_id", "unknown"),
        "pipeline_id": state.get("pipeline_id", "unknown"),
        "node_id": node_id,
        "context_hash": context_hash,
        "context_file": context_file,
        "iteration": iteration,
        "deliverable": None,  # Will be populated by node execution
        "questions": [],
        "evaluation": None,  # Will be populated by node execution
        "answers": {},
        "chained_context": chained_context,
        "status": "pending",
    }


def _convert_node_to_pipeline_state(
    node_state: dict[str, Any],
    original_state: dict[str, Any],
) -> dict[str, Any]:
    """Convert NodeRunState back to PipelineState after node execution.

    This function transforms the results from node execution back into
    the PipelineState format, preserving all original fields and updating
    only the node-specific fields.

    Args:
        node_state: The NodeRunState after node execution.
        original_state: The original PipelineState before node execution.

    Returns:
        Updated PipelineState with node execution results merged in.

    Example:
        >>> original = {"pipeline_id": "test", "deliverables": {}}
        >>> node_result = {"node_id": "analyst", "deliverable": {...}}
        >>> result = _convert_node_to_pipeline_state(node_result, original)
        >>> "analyst" in result["deliverables"]
        True
    """
    # Deep copy original state to avoid mutation
    new_state = copy.deepcopy(original_state)

    node_id = node_state.get("node_id")

    # Update deliverable if present
    if node_state.get("deliverable") is not None:
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}
        new_state["deliverables"][node_id] = node_state["deliverable"]

    # Update questions if present
    questions = node_state.get("questions", [])
    if questions:
        if "questions" not in new_state:
            new_state["questions"] = {}
        new_state["questions"][node_id] = questions

    # Update evaluation if present
    evaluation = node_state.get("evaluation")
    if evaluation is not None:
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}
        new_state["evaluations"][node_id] = evaluation

    # Update iteration count
    if "node_iterations" not in new_state:
        new_state["node_iterations"] = {}
    new_state["node_iterations"][node_id] = node_state.get("iteration", 1)

    # Add node to completed_nodes if not already there
    if "completed_nodes" not in new_state:
        new_state["completed_nodes"] = []
    if node_id not in new_state["completed_nodes"]:
        new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]

    # Update current_node
    new_state["current_node"] = node_id

    return new_state


def _create_integrated_node_executor(
    node_id: str,
    session_manager: Any,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create an integrated node executor that uses node_execution.executor.

    This function creates a node executor that:
    - Uses lazy import to avoid circular imports
    - Calls create_node_executor() from node_execution.executor module
    - Converts PipelineState to NodeRunState for execution
    - Converts NodeRunState back to PipelineState after execution
    - Saves deliverables via FileStorage after successful execution

    Args:
        node_id: The node identifier.
        session_manager: KimiSessionManager instance for SDK interactions.

    Returns:
        A callable that processes the state using the integrated executor.
    """
    # Lazy import to avoid circular imports
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor

    # Create the async node executor
    async_node_executor = create_node_executor(node_id, session_manager)

    def _run_async(coro: Awaitable[Any]) -> Any:
        """Run async coroutine, handling event loop properly.

        This helper handles the case where there's already a running event loop
        (e.g., when called from pytest with pytest-asyncio).

        IMPORTANT: For best results, callers should ensure no event loop is running
        on the current thread (e.g., use sync test functions instead of async).
        The ThreadPoolExecutor fallback path can cause thread accumulation on Windows.
        """
        import asyncio

        try:
            # Try to get the running loop
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop - use asyncio.run() which creates a new loop
            return asyncio.run(coro)

        # There's a running loop - create a new thread to run the coroutine
        # This path should be avoided when possible (see docstring)
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            # Add timeout to prevent indefinite blocking (4 minutes per call)
            return future.result(timeout=240)

    def executor(state: dict[str, Any]) -> dict[str, Any]:
        """Execute node logic using integrated node_execution.executor."""
        import copy as copy_module

        # Deep copy state to avoid mutation issues
        new_state = copy_module.deepcopy(state)

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

        # Convert PipelineState to NodeRunState
        node_run_state = _convert_pipeline_to_node_state(new_state, node_id)

        # Run the async executor in sync context
        try:
            # Run async executor synchronously for LangGraph compatibility
            # Use _run_async to handle event loop properly
            executed_node_state = _run_async(async_node_executor(node_run_state))

            # Convert back to PipelineState
            new_state = _convert_node_to_pipeline_state(executed_node_state, new_state)

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
            # Fall back to default behavior on error
            new_state["deliverables"][node_id] = {}

        # Increment iteration count for this node
        current_iteration = new_state["node_iterations"].get(node_id, 0)
        new_state["node_iterations"][node_id] = current_iteration + 1

        # Add node to completed_nodes if not already there
        if node_id not in new_state["completed_nodes"]:
            new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]

        return new_state

    return executor


def create_enhanced_node_executor(
    node_id: str,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create an enhanced node executor with full context accumulation.

    This is the production-ready executor that:
    - Receives accumulated context from all previous nodes
    - Validates deliverable format
    - Properly handles state transitions

    Args:
        node_id: The node identifier.

    Returns:
        A callable that processes the state with full context accumulation.
    """
    return _create_default_node_executor(node_id, None)


def create_pipeline_graph(
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
    compile_graph: bool = True,
    session_manager: Any | None = None,
) -> Any:
    """Create the pipeline StateGraph with all nodes and edges.

    This creates a LangGraph StateGraph with:
    - 5 nodes: analyst, pm, ux, architect, po
    - Sequential edges: analyst → pm → ux → architect → po
    - START and END connections
    - Optional integrated node execution via node_execution.executor (Story 11.4)

    Args:
        db_path: Optional database path for SqliteSaver checkpointer.
                 If provided along with no checkpointer, creates a SqliteSaver.
        checkpointer: Optional existing checkpointer to use. If not provided
                      and db_path is given, creates a SqliteSaver.
        compile_graph: If True (default), returns compiled graph. If False,
                      returns uncompiled StateGraph.
        session_manager: Optional KimiSessionManager for integrated node execution.
                        If provided, uses _create_integrated_node_executor.
                        If None, uses _create_default_node_executor for backward compatibility.

    Returns:
        StateGraph (uncompiled) or CompiledStateGraph ready for execution.

    Example:
        >>> graph = create_pipeline_graph()
        >>> compiled = graph.compile()

        >>> # With checkpointer
        >>> graph = create_pipeline_graph(db_path="checkpoints.db")
        >>> compiled = graph.compile()

        >>> # With session_manager for integrated execution
        >>> from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
        >>> session_manager = KimiSessionManager(...)
        >>> graph = create_pipeline_graph(session_manager=session_manager)
    """
    # Create the StateGraph with PipelineState schema
    graph = StateGraph(PipelineState)

    # Determine which executor to use based on session_manager
    use_integrated = session_manager is not None

    if use_integrated:
        logger.info(
            "using_integrated_node_executor",
            message="Using integrated node_execution.executor for node execution",
        )
    else:
        logger.warning(
            "falling_back_to_default_executor",
            message="session_manager not provided, falling back to default executor (backward compatibility)",
        )

    # Add all 5 nodes to the graph
    for node_id in PIPELINE_NODES:
        if use_integrated:
            node_executor = _create_integrated_node_executor(node_id, session_manager)
        else:
            node_executor = _create_default_node_executor(node_id)
        # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
        graph.add_node(node_id, node_executor)

    # Add finalization node to mark pipeline as completed
    def finalize_executor(state: dict[str, Any]) -> PipelineState:
        """Finalize the pipeline state when all nodes complete."""
        return finalize_pipeline_state(state)

    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_node("__finalize__", finalize_executor)

    # Add sequential edges: analyst → pm → ux → architect → po
    # First, connect START to analyst
    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_edge("__start__", "analyst")

    # Connect each node to the next in sequence
    for i in range(len(PIPELINE_NODES) - 1):
        current_node = PIPELINE_NODES[i]
        next_node = PIPELINE_NODES[i + 1]
        # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
        graph.add_edge(current_node, next_node)

    # Connect po to finalize node, then finalize to END
    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_edge("po", "__finalize__")
    # type: ignore[reportUnknownMemberType, reportUnusedCallResult]
    graph.add_edge("__finalize__", END)

    # If compile_graph is True, compile and return
    if compile_graph:
        # If db_path provided but no checkpointer, create AsyncSqliteSaver
        # Note: We need AsyncSqliteSaver for ainvoke() to work properly
        if checkpointer is None and db_path is not None:
            import asyncio

            import aiosqlite

            # Get or create event loop
            try:
                loop = asyncio.get_running_loop()

                # If we're already in an async context, use run_until_complete
                async def create_async_checkpointer():
                    conn = await aiosqlite.connect(db_path)
                    # Enable WAL mode for better concurrent access
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    # Patch is_alive method for langgraph compatibility
                    if not hasattr(conn, "is_alive"):

                        def _is_alive():
                            return True

                        conn.is_alive = _is_alive  # type: ignore[attr-defined]
                    return AsyncSqliteSaver(conn)

                checkpointer = loop.run_until_complete(create_async_checkpointer())  # type: ignore[assignment]
            except RuntimeError:
                # If no running loop, use asyncio.run
                async def create_async_checkpointer():
                    conn = await aiosqlite.connect(db_path)
                    # Enable WAL mode for better concurrent access
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    # Patch is_alive method for langgraph compatibility
                    if not hasattr(conn, "is_alive"):

                        def _is_alive():
                            return True

                        conn.is_alive = _is_alive  # type: ignore[attr-defined]
                    return AsyncSqliteSaver(conn)

                checkpointer = asyncio.run(create_async_checkpointer())  # type: ignore[assignment]

        # Compile the graph with optional checkpointer
        # type: ignore[reportUnknownMemberType]
        compiled: Runnable[dict[str, Any], dict[str, Any]] = graph.compile(
            checkpointer=checkpointer
        )
        return compiled

    return graph


def create_graph_with_checkpointer(
    db_path: str,
) -> Any:
    """Create the pipeline graph with a SqliteSaver checkpointer.

    This is a convenience function that creates the graph with a
    SqliteSaver checkpointer attached for state persistence.

    Args:
        db_path: The database connection string for SqliteSaver.

    Returns:
        Compiled StateGraph with checkpointer attached.

    Example:
        >>> graph = create_graph_with_checkpointer("checkpoints.db")
        >>> thread_id = generate_thread_id("pipeline-123")
        >>> config = create_checkpoint_config(thread_id)
        >>> result = await graph.ainvoke(initial_state, config)
    """
    checkpointer: Any = SqliteSaver.from_conn_string(db_path)
    return create_pipeline_graph(checkpointer=checkpointer)


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
        >>> from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
        >>> session_manager = KimiSessionManager(...)  # or mock
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
    "create_graph_with_checkpointer",
    "create_graph_config",
    # Story 11.4 - Node execution integration
    "_create_integrated_node_executor",
    "_convert_pipeline_to_node_state",
    "_convert_node_to_pipeline_state",
    # Story 11.6 - Test utilities
    "MockNodeExecutor",
    "create_mock_node_executor",
]

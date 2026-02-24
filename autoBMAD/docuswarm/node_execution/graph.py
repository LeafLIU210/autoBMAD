"""LangGraph Node Execution Graph - Story 3.3.

This module defines the LangGraph StateGraph for individual node execution with:
- Single node execution: START → node_id → END flow
- SqliteSaver checkpointer for state persistence
- Thread configuration for per-run isolation using run_id
- Logging for graph creation and execution
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from autoBMAD.docuswarm.node_execution.state import NodeRunState

# Import StateGraph type only for type checking to avoid runtime issues
if TYPE_CHECKING:
    from langgraph.graph import StateGraph

# Configure module logger
logger = logging.getLogger(__name__)


def _create_default_node_executor(
    node_id: str,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create a default node executor function for the node.

    This creates a simple executor that updates the state with the current node_id
    and status. In production, this would be replaced by the actual node executor
    from Story 3.4.

    Args:
        node_id: The node identifier.

    Returns:
        A callable that processes the state.
    """

    def executor(state: dict[str, Any]) -> dict[str, Any]:
        """Execute node logic - default implementation."""
        import copy

        # Deep copy state to avoid mutation issues (required by LangGraph)
        new_state = copy.deepcopy(state)

        # Update current node
        new_state["current_node"] = node_id

        # Set status to running if not set
        if "status" not in new_state:
            new_state["status"] = "running"

        # Return updated state
        return new_state

    return executor


def create_node_execution_graph(
    node_id: str,
    db_path: str | None = None,
    checkpointer: SqliteSaver | None = None,
    compile_graph: bool = True,
) -> StateGraph | Runnable[dict[str, Any], dict[str, Any]]:
    """Create a LangGraph StateGraph for single-node execution.

    This creates a LangGraph StateGraph with a simple flow: START → node_id → END.
    The graph uses NodeRunState as its state schema and supports SqliteSaver
    checkpointing for state persistence.

    Args:
        node_id: The node identifier (e.g., 'analyst', 'pm').
        db_path: Optional database path for SqliteSaver checkpointer.
                 If provided and no checkpointer given, creates a SqliteSaver.
        checkpointer: Optional existing SqliteSaver to use. Takes precedence over db_path.
        compile_graph: If True (default), returns compiled graph. If False,
                      returns uncompiled StateGraph.

    Returns:
        StateGraph (uncompiled) or CompiledStateGraph ready for execution.

    Example:
        >>> graph = create_node_execution_graph(node_id="analyst")
        >>> config = create_node_execution_config(run_id="run-123")
        >>> result = graph.invoke(initial_state, config)
    """
    logger.info(f"Creating node execution graph for node: {node_id}")

    # Create the StateGraph with NodeRunState schema
    graph = StateGraph(NodeRunState)

    # Add the node executor
    node_executor = _create_default_node_executor(node_id)
    graph.add_node(node_id, node_executor)

    # Add edges: START → node_id → END
    graph.add_edge("__start__", node_id)
    graph.add_edge(node_id, END)

    logger.debug(f"Added edges: __start__ -> {node_id} -> END")

    # If compile_graph is True, compile and return
    if compile_graph:
        # If db_path provided but no checkpointer, create SqliteSaver
        if checkpointer is None and db_path is not None:
            logger.debug(f"Creating SqliteSaver checkpointer with db_path: {db_path}")
            # SqliteSaver requires a pre-opened SQLite connection
            # Use check_same_thread=False to allow LangGraph's thread pool to access the DB
            conn = sqlite3.connect(db_path, check_same_thread=False)
            checkpointer = SqliteSaver(conn=conn)

        # Compile the graph with optional checkpointer
        if checkpointer is not None:
            logger.debug("Compiling graph with checkpointer")
            compiled: Runnable[dict[str, Any], dict[str, Any]] = graph.compile(
                checkpointer=checkpointer
            )
        else:
            logger.debug("Compiling graph without checkpointer")
            compiled = graph.compile()

        logger.info(f"Node execution graph compiled for node: {node_id}")
        return compiled

    logger.info(f"Node execution graph created (uncompiled) for node: {node_id}")
    return graph


def create_node_execution_config(
    run_id: str | None = None,
) -> RunnableConfig:
    """Create a configuration dict for node execution with thread isolation.

    This creates a LangGraph configuration with thread_id set to the run_id,
    enabling per-run state isolation when using SqliteSaver checkpointer.

    Args:
        run_id: Optional run identifier. If not provided, generates a random UUID.

    Returns:
        Configuration dict with thread_id for isolation.

    Example:
        >>> config = create_node_execution_config(run_id="run-123")
        >>> result = graph.invoke(state, config)
    """
    if run_id is None:
        run_id = uuid.uuid4().hex
        logger.debug(f"Generated run_id: {run_id}")

    config: RunnableConfig = {
        "configurable": {
            "thread_id": run_id,
        }
    }

    logger.debug(f"Created node execution config with run_id: {run_id}")
    return config


# Alias for backward compatibility
def create_checkpoint_config(thread_id: str) -> RunnableConfig:
    """Create a checkpoint configuration dict (alias for compatibility).

    Args:
        thread_id: The unique thread identifier.

    Returns:
        Configuration dict with thread_id for isolation.
    """
    return create_node_execution_config(run_id=thread_id)


__all__ = [
    "create_node_execution_graph",
    "create_node_execution_config",
    "create_checkpoint_config",
]

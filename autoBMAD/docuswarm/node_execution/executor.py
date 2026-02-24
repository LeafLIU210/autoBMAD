"""Node Executor for LangGraph single-node execution - Story 3.4.

This module provides the create_node_executor factory function that:
- Creates an async node executor function for LangGraph
- Loads node configuration via NodeLoader
- Instantiates DualAgentNode with node_id and LLM client
- Updates NodeRunState with deliverable, questions, evaluation, and iteration
- Handles iteration counting and status transitions
"""

import copy
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

import structlog

from autoBMAD.docuswarm.config import Config
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
from autoBMAD.docuswarm.node_execution.state import (
    BLOCKED,
    COMPLETED,
    FAILED,
    RUNNING,
    NodeRunState,
)
from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
from autoBMAD.docuswarm.nodes.loader import NodeLoader

# Configure module logger
logger = structlog.get_logger(__name__)


def create_node_executor(
    node_id: str,
    session_manager: KimiSessionManager,
) -> Callable[[NodeRunState], Coroutine[Any, Any, NodeRunState]]:
    """Create a node executor function for LangGraph single-node execution.

    This factory function returns an async executor function that:
    1. Loads node configuration via NodeLoader.load(node_id)
    2. Creates a DualAgentNode instance with the node_id
    3. Executes the node with the current state
    4. Updates NodeRunState with deliverable, questions, evaluation, iteration
    5. Handles status transitions based on evaluation verdict

    Args:
        node_id: The node identifier (e.g., 'analyst', 'pm', 'ux', 'architect', 'po')
        session_manager: KimiSessionManager for SDK interactions.

    Returns:
        An async function that accepts NodeRunState and returns updated NodeRunState

    Example:
        >>> executor = create_node_executor("analyst", session_manager)
        >>> result_state = await executor(initial_state)
    """
    # Create logger with node_id bound
    executor_logger = structlog.get_logger().bind(node_id=node_id)

    async def node_executor(state: NodeRunState) -> NodeRunState:
        """Async node executor function for LangGraph.

        Args:
            state: The current NodeRunState

        Returns:
            Updated NodeRunState with execution results
        """
        return await _execute_node(state, node_id, session_manager, executor_logger)

    return node_executor


async def _execute_node(
    state: NodeRunState,
    node_id: str,
    session_manager: KimiSessionManager,
    logger: Any,
) -> NodeRunState:
    """Execute a node and update NodeRunState.

    Args:
        state: The current NodeRunState
        node_id: The node identifier to execute
        logger: Bound structlog logger

    Returns:
        Updated NodeRunState with execution results
    """
    run_id = state.get("run_id", "unknown")

    logger.info(
        "node_execution_started",
        node_id=node_id,
        run_id=run_id,
        iteration=state.get("iteration", 1),
    )

    # Create a copy of state to avoid mutation (required by LangGraph)
    new_state = copy.deepcopy(state)

    # Update status to running
    new_state["status"] = RUNNING

    try:
        # Step 1: Load node configuration via NodeLoader
        loader = NodeLoader()
        node_config = loader.load(node_id)

        logger.debug(
            "node_config_loaded",
            node_id=node_id,
            config_keys=[node_config.node_id] if node_config else [],
        )

        # Step 2: Create DualAgentNode instance
        # Create default config (in production, this would be injected)
        config = _get_config()

        # Get project_root from the location of this module
        # This ensures the correct path to nodes/ directory
        # Path: autoBMAD/docuswarm/node_execution/executor.py -> parent.parent.parent = autoBMAD root
        project_root = Path(__file__).parent.parent.parent.resolve()

        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id=node_id,
            project_root=project_root,
        )

        # Step 3: Execute the node
        # Get subject_context, task, and pipeline_id from state
        subject_context = state.get("context_file", "")
        # The task comes from chained_context or we use a default
        task = _extract_task_from_state(state)
        # Get pipeline_id from state for IndependentAgent
        pipeline_id = state.get("pipeline_id", "")

        result = await node.execute(
            subject_context=str(subject_context),
            task=task,
            pipeline_id=pipeline_id,
        )

        # Step 4: Update state with results
        new_state["deliverable"] = result.deliverable
        new_state["questions"] = result.questions
        new_state["evaluation"] = result.evaluation

        # Increment iteration count
        new_state["iteration"] = state.get("iteration", 1) + 1

        # Step 5: Handle status transition based on verdict
        verdict = result.evaluation.get("verdict") if result.evaluation else None

        if verdict == "APPROVED":
            new_state["status"] = COMPLETED
            logger.info(
                "node_approved",
                node_id=node_id,
                run_id=run_id,
                iteration=new_state["iteration"],
            )
        elif verdict == "BLOCKED":
            new_state["status"] = BLOCKED
            logger.warning(
                "node_blocked",
                node_id=node_id,
                run_id=run_id,
                iteration=new_state["iteration"],
            )
        elif verdict == "FORCE_APPROVED":
            # Force approved is also considered completed
            new_state["status"] = COMPLETED
            logger.warning(
                "node_force_approved",
                node_id=node_id,
                run_id=run_id,
                iteration=new_state["iteration"],
            )
        else:
            # NEEDS_REVISION or unknown - keep as running
            new_state["status"] = RUNNING
            logger.info(
                "node_needs_revision",
                node_id=node_id,
                run_id=run_id,
                iteration=new_state["iteration"],
                verdict=verdict,
            )

        logger.info(
            "node_execution_completed",
            node_id=node_id,
            run_id=run_id,
            iteration=new_state["iteration"],
            status=new_state["status"],
            verdict=verdict,
        )

    except Exception as e:
        logger.error(
            "node_execution_failed",
            node_id=node_id,
            run_id=run_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        # Set status to failed on exception
        new_state["status"] = FAILED

    return new_state


def _extract_task_from_state(state: NodeRunState) -> str:
    """Extract task from the node run state.

    Args:
        state: The current NodeRunState

    Returns:
        The task string
    """
    import json

    # First, try to get task from context_file (contains subject_context for first node)
    context_file = state.get("context_file", "")
    if context_file:
        try:
            context_data: Any = json.loads(context_file)
            # Check for subject_context which contains the initial task
            if isinstance(context_data, dict) and "subject_context" in context_data:
                subject: Any = context_data["subject_context"]
                # Extract content from subject
                if isinstance(subject, dict):
                    subject_dict: dict[str, Any] = subject
                    # Use content field as the task
                    if "content" in subject_dict:
                        return str(subject_dict["content"])
                    # Or use the whole subject as task
                    return str(subject_dict)
                elif isinstance(subject, str):
                    return subject
        except (json.JSONDecodeError, TypeError):
            # If context_file is not JSON, use it directly as task
            if context_file:
                return context_file

    # Try to get task from chained_context (previous node outputs)
    chained_context: dict[str, dict[str, Any]] = state.get("chained_context", {})

    # Look for task in any previous node's context
    for _node_id, context_data in chained_context.items():
        # context_data is dict[str, Any] per NodeRunState type definition
        if "task" in context_data:
            return context_data["task"]
        if "deliverable" in context_data:
            # Use deliverable as context
            return str(context_data["deliverable"])

    # Default empty task if not found
    return ""


def _get_config() -> Config:
    """Get the application config.

    Loads configuration from .env file and YAML with proper precedence.

    Returns:
        Config instance
    """
    from autoBMAD.docuswarm.config import load_config

    return load_config()


__all__ = [
    "create_node_executor",
]

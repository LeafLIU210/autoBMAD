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
    4. Updates NodeRunState with deliverable, questions, evaluations
    5. Tracks iteration count
    6. Adds node to completed_nodes on APPROVED verdict

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
    pipeline_id = state.get("pipeline_id", "")

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
        # ==== Single Context Protocol: 构建 NodeExecutionContext ====
        from .context_builder import create_context_builder

        context_builder = create_context_builder()

        # 解析原始上下文
        original_context = _parse_original_context(state.get("context_file", ""))

        # 构建统一的执行上下文
        execution_context = context_builder.build(
            pipeline_id=pipeline_id,
            node_id=node_id,
            original_context=original_context,
            chained_deliverables=_extract_chained_deliverables(state),
            shared_context=state.get("shared_context", {}),
        )

        logger.debug(
            "execution_context_built",
            node_id=node_id,
            task_name=execution_context["task_name"],
        )

        # Create DualAgentNode instance
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

        # ==== Single Context Protocol: 直接传入 execution_context ====
        result = await node.execute_with_context(execution_context)

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


def _parse_original_context(context_file: str) -> dict[str, Any]:
    """解析原始上下文文件内容。

    Args:
        context_file: JSON 字符串、context 文件路径，或原始内容

    Returns:
        解析后的字典
    """
    import json

    if not context_file:
        return {}

    raw_text = context_file
    context_path = Path(context_file)

    if context_path.exists() and context_path.is_file():
        raw_text = context_path.read_text(encoding="utf-8")

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"content": raw_text}

    return _normalize_original_context(data, fallback_text=raw_text)


def _extract_chained_deliverables(state: NodeRunState) -> list[dict[str, Any]]:
    """提取链式上游交付物。

    Args:
        state: 当前节点运行状态

    Returns:
        上游交付物列表
    """
    chained: dict[str, Any] = state.get("chained_context", {})
    deliverables = []

    for node_id, ctx in chained.items():
        context: Any = ctx
        if isinstance(context, dict) and "deliverable" in context:
            deliverables.append(
                {
                    "node_id": node_id,
                    "deliverable": context["deliverable"],
                }
            )

    return deliverables


def _normalize_original_context(data: Any, fallback_text: str = "") -> dict[str, Any]:
    """Normalize original context from pipeline JSON, file contents, or plain text."""
    import json

    if isinstance(data, dict):
        data_dict: dict[str, Any] = data
        normalized = dict(data_dict)
        content = _extract_original_context_content(data_dict)
        if not content and fallback_text:
            content = fallback_text
        if content:
            normalized["content"] = content
        return normalized

    if isinstance(data, list):
        if fallback_text:
            return {"content": fallback_text}
        return {"content": json.dumps(data, ensure_ascii=False)}

    return {"content": fallback_text or str(data)}


def _extract_original_context_content(data: dict[str, Any]) -> str:
    """Extract user-visible content from raw original context payloads."""
    import json

    content = data.get("content")
    if isinstance(content, str) and content:
        return content

    subject_context = data.get("subject_context")
    if isinstance(subject_context, dict):
        nested_content = subject_context.get("content")
        if isinstance(nested_content, str) and nested_content:
            return nested_content

    if "project_description" in data or "requirements" in data:
        return json.dumps(data, ensure_ascii=False, indent=2)

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

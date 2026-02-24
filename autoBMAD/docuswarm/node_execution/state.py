"""Node execution state schema for LangGraph individual node management.

This module defines the state schemas for managing individual node execution
in LangGraph, compatible with SqliteSaver checkpointing.
"""

import json
from typing import Any, TypedDict, cast

# Status constants
PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
BLOCKED = "blocked"

# Status dictionary for validation
NODE_STATUS = {
    "PENDING": PENDING,
    "RUNNING": RUNNING,
    "COMPLETED": COMPLETED,
    "FAILED": FAILED,
    "BLOCKED": BLOCKED,
}

# Valid status set for validation
VALID_STATUSES = {PENDING, RUNNING, COMPLETED, FAILED, BLOCKED}


class NodeResult(TypedDict):
    """Result from a single node execution.

    This TypedDict is designed to be fully serializable to JSON and
    compatible with SqliteSaver for checkpointing.
    """

    deliverable: dict[str, Any] | None
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any] | None
    iteration: int
    status: str


class NodeRunState(TypedDict):
    """State for individual node run in LangGraph.

    This TypedDict is designed to be fully serializable to JSON and
    compatible with SqliteSaver for checkpointing.
    """

    run_id: str
    node_id: str
    context_hash: str
    context_file: str | None
    iteration: int
    deliverable: dict[str, Any] | None
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any] | None
    answers: dict[str, Any]
    chained_context: dict[str, dict[str, Any]]
    status: str


def create_node_result(
    iteration: int,
    status: str,
    deliverable: dict[str, Any] | None = None,
    questions: list[dict[str, Any]] | None = None,
    evaluation: dict[str, Any] | None = None,
) -> NodeResult:
    """Create a NodeResult with default values for optional fields.

    Args:
        iteration: The iteration number for this result
        status: The status of the node execution
        deliverable: Optional deliverable from the node
        questions: Optional list of questions generated
        evaluation: Optional evaluation result

    Returns:
        A new NodeResult with specified values and defaults for others
    """
    return NodeResult(
        deliverable=deliverable,
        questions=questions if questions is not None else [],
        evaluation=evaluation,
        iteration=iteration,
        status=status,
    )


def create_node_run_state(
    run_id: str,
    node_id: str,
    context_hash: str,
    context_file: str | None = None,
    iteration: int = 1,
    deliverable: dict[str, Any] | None = None,
    questions: list[dict[str, Any]] | None = None,
    evaluation: dict[str, Any] | None = None,
    answers: dict[str, Any] | None = None,
    chained_context: dict[str, dict[str, Any]] | None = None,
    status: str = PENDING,
) -> NodeRunState:
    """Create a NodeRunState with default values for optional fields.

    Args:
        run_id: Unique identifier for this run
        node_id: Identifier for the node being executed
        context_hash: Hash of the context being processed
        context_file: Optional path to context file
        iteration: The iteration number (default 1)
        deliverable: Optional deliverable from the node
        questions: Optional list of questions generated
        evaluation: Optional evaluation result
        answers: Optional answers to questions
        chained_context: Optional chained context from predecessor nodes
        status: The status of the run (default PENDING)

    Returns:
        A new NodeRunState with specified values and defaults for others
    """
    return NodeRunState(
        run_id=run_id,
        node_id=node_id,
        context_hash=context_hash,
        context_file=context_file,
        iteration=iteration,
        deliverable=deliverable,
        questions=questions if questions is not None else [],
        evaluation=evaluation,
        answers=answers if answers is not None else {},
        chained_context=chained_context if chained_context is not None else {},
        status=status,
    )


def update_node_run_state(
    state: NodeRunState,
    **updates: Any,
) -> NodeRunState:
    """Create a copy of NodeRunState with updated fields.

    This maintains immutability required by LangGraph.

    Args:
        state: The original NodeRunState
        **updates: Fields to update

    Returns:
        A new NodeRunState with the specified updates
    """
    new_state = state.copy()
    new_state |= updates
    return cast(NodeRunState, cast(object, new_state))


def is_valid_status(status: str) -> bool:
    """Check if a status value is valid.

    Args:
        status: The status string to validate

    Returns:
        True if the status is valid, False otherwise
    """
    return status in VALID_STATUSES


def validate_node_result(result: NodeResult) -> bool:
    """Validate NodeResult integrity.

    Checks:
    - All required fields are present
    - Status value is valid

    Args:
        result: The NodeResult to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["deliverable", "questions", "evaluation", "iteration", "status"]

    # Check all required fields present
    for field in required_fields:
        if field not in result:
            return False

    # Validate status is in valid set
    if not is_valid_status(result["status"]):
        return False

    # Validate iteration is non-negative
    if result["iteration"] < 0:
        return False

    return True


def validate_node_run_state(state: NodeRunState) -> bool:
    """Validate NodeRunState integrity.

    Checks:
    - All required fields are present
    - Status value is valid

    Args:
        state: The NodeRunState to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "run_id",
        "node_id",
        "context_hash",
        "context_file",
        "iteration",
        "deliverable",
        "questions",
        "evaluation",
        "answers",
        "chained_context",
        "status",
    ]

    # Check all required fields present
    for field in required_fields:
        if field not in state:
            return False

    # Validate status is in valid set
    if not is_valid_status(state["status"]):
        return False

    # Validate iteration is non-negative
    if state["iteration"] < 0:
        return False

    return True


def serialize_node_run_state(state: NodeRunState) -> str:
    """Serialize NodeRunState to JSON string.

    Args:
        state: The NodeRunState to serialize

    Returns:
        JSON string representation of the state
    """
    return json.dumps(state)


def deserialize_node_run_state(json_str: str) -> NodeRunState:
    """Deserialize NodeRunState from JSON string.

    Args:
        json_str: JSON string to deserialize

    Returns:
        NodeRunState object
    """
    data = json.loads(json_str)
    return NodeRunState(**data)


def serialize_node_result(result: NodeResult) -> str:
    """Serialize NodeResult to JSON string.

    Args:
        result: The NodeResult to serialize

    Returns:
        JSON string representation of the result
    """
    return json.dumps(result)


def deserialize_node_result(json_str: str) -> NodeResult:
    """Deserialize NodeResult from JSON string.

    Args:
        json_str: JSON string to deserialize

    Returns:
        NodeResult object
    """
    data = json.loads(json_str)
    return NodeResult(**data)

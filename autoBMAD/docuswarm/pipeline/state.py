"""Pipeline state definitions for DocuSwarm.

This module defines the state schemas for LangGraph pipeline orchestration,
compatible with SqliteSaver checkpointing.
"""

from datetime import UTC
from typing import Any, TypedDict

# Pipeline-level status values
PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
PAUSED = "paused"
CANCELLED = "cancelled"  # Story 9.4: Native Cancellation Integration

# Node-level status values
APPROVED = "approved"
NEEDS_REVISION = "needs_revision"
BLOCKED = "blocked"

# Status dictionaries for validation
PIPELINE_STATUS = {
    "PENDING": PENDING,
    "RUNNING": RUNNING,
    "COMPLETED": COMPLETED,
    "FAILED": FAILED,
    "PAUSED": PAUSED,
    "CANCELLED": CANCELLED,
}

NODE_STATUS = {
    "APPROVED": APPROVED,
    "NEEDS_REVISION": NEEDS_REVISION,
    "BLOCKED": BLOCKED,
}

# Valid status sets for validation
VALID_PIPELINE_STATUSES = {PENDING, RUNNING, COMPLETED, FAILED, PAUSED, CANCELLED}
VALID_NODE_STATUSES = {APPROVED, NEEDS_REVISION, BLOCKED}

# Pipeline node order - must execute in sequence
PIPELINE_NODES: list[str] = ["analyst", "pm", "ux", "architect", "po"]


class NodeResult(TypedDict):
    """Result from a single node execution."""

    deliverable: dict[str, Any] | None
    questions: list[dict[str, Any]]
    evaluation: dict[str, Any] | None
    iteration: int
    status: str


class PipelineState(TypedDict):
    """Main pipeline state schema for LangGraph StateGraph.

    This TypedDict is designed to be fully serializable to JSON and
    compatible with SqliteSaver for checkpointing.
    """

    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]
    questions: dict[str, list[dict[str, Any]]]
    evaluations: dict[str, dict[str, Any]]
    node_iterations: dict[str, int]
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None  # Story 9.3: For pipeline resume recovery
    status: str
    error: dict[str, Any] | None
    shared_context: dict[str, Any]  # P1-1: Cross-node shared context


def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> PipelineState:
    """Create an initial PipelineState with default values.

    Args:
        pipeline_id: Unique identifier for the pipeline
        subject_context: Context information about the subject being processed

    Returns:
        A new PipelineState with all fields initialized to defaults
    """
    from autoBMAD.docuswarm.utils.session_ids import generate_session_id

    # Generate pipeline-level session ID
    pipeline_session_id = generate_session_id(pipeline_id)

    return PipelineState(
        pipeline_id=pipeline_id,
        subject_context=subject_context,
        current_node=None,
        completed_nodes=[],
        deliverables={},
        questions={},
        evaluations={},
        node_iterations={},
        session_ids={"pipeline": pipeline_session_id},
        session_metadata={},
        current_node_session_id=None,  # Story 9.3: No interrupted session initially
        status=PENDING,
        error=None,
        shared_context={},  # P1-1: Initialize shared_context
    )


def validate_state(state: PipelineState) -> bool:
    """Validate PipelineState integrity.

    Checks:
    - All required fields are present
    - Status values are valid
    - completed_nodes keys are a subset of deliverables keys

    Args:
        state: The PipelineState to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "pipeline_id",
        "subject_context",
        "current_node",
        "completed_nodes",
        "deliverables",
        "questions",
        "evaluations",
        "node_iterations",
        "session_ids",
        "status",
    ]

    # Check all required fields present
    for field in required_fields:
        if field not in state:
            return False

    # Validate status is in valid set
    if state["status"] not in VALID_PIPELINE_STATUSES:
        return False

    # Validate completed_nodes is subset of deliverables keys
    completed = set(state["completed_nodes"])
    deliverable_keys = set(state["deliverables"].keys())
    if not completed.issubset(deliverable_keys):
        return False

    return True


def serialize_state(state: PipelineState) -> str:
    """Serialize PipelineState to JSON string.

    Args:
        state: The PipelineState to serialize

    Returns:
        JSON string representation of the state
    """
    import json

    return json.dumps(state)


def deserialize_state(data: str) -> PipelineState:
    """Deserialize JSON string to PipelineState.

    Args:
        data: JSON string to deserialize

    Returns:
        PipelineState object
    """
    import json

    return json.loads(data)


def accumulate_context(
    subject_context: dict[str, Any],
    deliverables: dict[str, dict[str, Any]],
    current_node: str,
) -> dict[str, Any]:
    """Accumulate context by merging subject context with previous deliverables.

    Each node receives the initial subject_context PLUS all previous deliverable outputs.
    This function builds the accumulated context for a given node by including
    all deliverables from previous nodes in the pipeline.

    Args:
        subject_context: The initial subject/context of the pipeline.
        deliverables: Dictionary of node deliverables (key: node_id).
        current_node: The node that will receive this context.

    Returns:
        A new context dictionary containing subject_context and all previous deliverables.

    Example:
        >>> subject = {"task": "Build a website", "requirements": ["fast", "secure"]}
        >>> deliverables = {"analyst": {"analysis": "..."}, "pm": {"plan": "..."}}
        >>> context = accumulate_context(subject, deliverables, "ux")
        >>> # context now contains subject + analyst deliverable + pm deliverable
    """
    # Find the index of the current node
    try:
        current_index = PIPELINE_NODES.index(current_node)
    except ValueError:
        # If node not in pipeline, return just subject context
        return {"subject_context": subject_context}

    # Get all previous nodes that have completed
    previous_nodes = PIPELINE_NODES[:current_index]

    # Build accumulated context
    accumulated: dict[str, Any] = {
        "subject_context": subject_context.copy() if subject_context else {},
    }

    # Add each previous node's deliverable to the context
    for node_id in previous_nodes:
        if node_id in deliverables and deliverables[node_id]:
            # Use the deliverable key format as specified in story
            accumulated[f"{node_id}_deliverable"] = deliverables[node_id].copy()

    return accumulated


def merge_deliverable_into_context(
    context: dict[str, Any],
    deliverable: dict[str, Any],
    node_id: str,
) -> dict[str, Any]:
    """Merge a node's deliverable into the existing context.

    Args:
        context: The current context dictionary.
        deliverable: The deliverable to merge.
        node_id: The node identifier (e.g., 'analyst', 'pm').

    Returns:
        Updated context with the deliverable merged in.
    """
    result = context.copy()
    result[f"{node_id}_deliverable"] = deliverable.copy() if deliverable else {}
    return result


def validate_deliverable_format(deliverable: object) -> bool:
    """Validate that a deliverable has the expected format.

    Args:
        deliverable: The deliverable dictionary to validate.

    Returns:
        True if the deliverable format is valid, False otherwise.
    """
    # Deliverable can be empty dict or contain valid JSON-serializable content
    # This is intentionally permissive to allow flexibility
    return isinstance(deliverable, dict)


def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    """Finalize the pipeline state when all nodes have completed.

    This function:
    - Marks the pipeline status as completed
    - Captures final state with all accumulated data
    - Ensures all deliverables are preserved

    Args:
        state: The current PipelineState.

    Returns:
        Updated PipelineState with completed status.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state["completed_nodes"] = ["analyst", "pm", "ux", "architect", "po"]
        >>> finalized = finalize_pipeline_state(state)
        >>> # finalized["status"] == "completed"
    """
    import copy

    result = copy.deepcopy(state)

    # Mark pipeline as completed
    result["status"] = COMPLETED

    # Preserve current_node (the last executed node) - do not clear it
    # This allows users to see which node was last processed

    return result


def create_error_state(
    pipeline_id: str,
    error: Exception,
    current_state: PipelineState | None = None,
) -> PipelineState:
    """Create an error state capturing the failure information.

    Args:
        pipeline_id: The pipeline identifier.
        error: The exception that caused the error.
        current_state: The state at the time of failure (optional).

    Returns:
        PipelineState with error information captured.
    """
    if current_state is None:
        current_state = create_initial_state(pipeline_id, {})

    import copy

    result = copy.deepcopy(current_state)
    result["status"] = FAILED

    # Add error information
    if "error" not in result:
        result["error"] = {}

    result["error"] = {
        "message": str(error),
        "type": type(error).__name__,
        "current_node": result.get("current_node"),
    }

    return result


def update_node_session_id(
    state: PipelineState,
    node_id: str,
    iteration: int | None = None,
) -> PipelineState:
    """Update session IDs in pipeline state for a node.

    Generates and stores hierarchical session IDs:
    - Node-level: docuswarm-{pipeline_id}-{node_id}
    - Iteration-level: docuswarm-{pipeline_id}-{node_id}-iter{n}

    Args:
        state: The current PipelineState.
        node_id: The node identifier (e.g., 'analyst', 'pm').
        iteration: Optional iteration number. If provided, stores iteration-level ID.

    Returns:
        Updated PipelineState with new session ID(s) stored.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state = update_node_session_id(state, "analyst")
        >>> # state["session_ids"]["analyst"] == "docuswarm-pipeline-1-analyst"

        >>> state = update_node_session_id(state, "analyst", 3)
        >>> # state["session_ids"]["analyst_iter3"] == "docuswarm-pipeline-1-analyst-iter3"
    """
    import copy

    from autoBMAD.docuswarm.utils.session_ids import generate_session_id

    result = copy.deepcopy(state)
    pipeline_id = result["pipeline_id"]

    # Initialize session_ids dict if not present
    if "session_ids" not in result:
        result["session_ids"] = {}

    if iteration is not None:
        # Generate iteration-level session ID
        session_id = generate_session_id(pipeline_id, node_id, iteration)
        result["session_ids"][f"{node_id}_iter{iteration}"] = session_id
    else:
        # Generate node-level session ID
        session_id = generate_session_id(pipeline_id, node_id)
        result["session_ids"][node_id] = session_id

    return result


def get_session_id(
    state: PipelineState,
    node_id: str | None = None,
    iteration: int | None = None,
) -> str | None:
    """Retrieve a session ID from pipeline state.

    Args:
        state: The current PipelineState.
        node_id: Optional node identifier. If None, returns pipeline-level ID.
        iteration: Optional iteration number. If provided with node_id, returns iteration-level ID.

    Returns:
        The session ID string, or None if not found.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> get_session_id(state)  # pipeline-level
        'docuswarm-pipeline-1'

        >>> get_session_id(state, "analyst")  # node-level
        'docuswarm-pipeline-1-analyst'

        >>> get_session_id(state, "analyst", 3)  # iteration-level
        'docuswarm-pipeline-1-analyst-iter3'
    """
    _sentinel = object()
    session_ids = state.get("session_ids", _sentinel)
    if session_ids is _sentinel:
        return None

    if node_id is None:
        # Return pipeline-level session ID
        return session_ids.get("pipeline")
    if iteration is not None:
        # Return iteration-level session ID
        return session_ids.get(f"{node_id}_iter{iteration}")
    # Return node-level session ID
    return session_ids.get(node_id)


def update_session_metadata(
    state: PipelineState,
    node_id: str,
    session_id: str,
    mode: str,
    iteration: int | None = None,
) -> PipelineState:
    """Update session metadata in pipeline state for recovery.

    Stores session metadata including session_id, mode, and creation timestamp
    to enable session resumption after pipeline restart.

    Args:
        state: The current PipelineState.
        node_id: Node identifier (e.g., "analyst", "developer").
        session_id: The session ID to store.
        mode: Session mode ("instant", "thinking", or "agent").
        iteration: Optional iteration number. If provided, stores iteration-level metadata.

    Returns:
        Updated PipelineState with session metadata stored.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state = update_session_metadata(state, "analyst", "docuswarm-pipeline-1-analyst", "agent")
        >>> # state["session_metadata"]["analyst"]["mode"] == "agent"
    """
    import copy
    from datetime import datetime

    result = copy.deepcopy(state)

    # Initialize session_metadata dict if not present
    if "session_metadata" not in result:
        result["session_metadata"] = {}

    # Build the key for this session
    if iteration is not None:
        key = f"{node_id}_iter{iteration}"
    else:
        key = node_id

    # Store metadata
    result["session_metadata"][key] = {
        "session_id": session_id,
        "mode": mode,
        "created_at": datetime.now(UTC).isoformat(),
    }

    return result


def get_session_metadata(
    state: PipelineState,
    node_id: str,
    iteration: int | None = None,
) -> dict[str, Any] | None:
    """Retrieve session metadata from pipeline state.

    Args:
        state: The current PipelineState.
        node_id: Node identifier.
        iteration: Optional iteration number. If provided, returns iteration-level metadata.

    Returns:
        The session metadata dict, or None if not found.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> metadata = get_session_metadata(state, "analyst")
        >>> # Returns {"session_id": "...", "mode": "agent", "created_at": "..."}
    """
    if iteration is not None:
        key = f"{node_id}_iter{iteration}"
    else:
        key = node_id

    _sentinel = object()
    session_metadata = state.get("session_metadata", _sentinel)
    if session_metadata is _sentinel:
        return None
    return session_metadata.get(key)


# Story 9.3: Pipeline Resume with Session Recovery


def update_current_node_session_id(
    state: PipelineState,
    node_id: str,
    session_id: str,
) -> PipelineState:
    """Update the current node's session_id in pipeline state for recovery.

    This function tracks the currently executing node's session_id, enabling
    the pipeline to resume from the exact interruption point after an interrupt.

    Args:
        state: The current PipelineState.
        node_id: The node identifier (e.g., 'analyst', 'pm').
        session_id: The session ID to store for recovery.

    Returns:
        Updated PipelineState with current_node_session_id stored.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state = update_current_node_session_id(state, "analyst", "docuswarm-pipeline-1-analyst")
        >>> # state["current_node_session_id"] == "docuswarm-pipeline-1-analyst"
    """
    import copy

    result = copy.deepcopy(state)

    # Store the current node's session_id for recovery
    result["current_node_session_id"] = session_id
    result["current_node"] = node_id

    return result


def get_current_node_session_id(
    state: PipelineState,
) -> str | None:
    """Retrieve the current node's session_id from pipeline state.

    Args:
        state: The current PipelineState.

    Returns:
        The current node's session_id string, or None if not set.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state["current_node_session_id"] = "docuswarm-pipeline-1-analyst"
        >>> session_id = get_current_node_session_id(state)
        >>> # session_id == "docuswarm-pipeline-1-analyst"
    """
    return state.get("current_node_session_id")


def clear_current_node_session_id(state: PipelineState) -> PipelineState:
    """Clear the current node's session_id from pipeline state.

    This is typically called after a node successfully completes, to indicate
    that there's no interrupted session to resume.

    Args:
        state: The current PipelineState.

    Returns:
        Updated PipelineState with current_node_session_id cleared.

    Example:
        >>> state = create_initial_state("pipeline-1", {"task": "Build X"})
        >>> state["current_node_session_id"] = "docuswarm-pipeline-1-analyst"
        >>> state = clear_current_node_session_id(state)
        >>> # state.get("current_node_session_id") is None
    """
    import copy

    result = copy.deepcopy(state)

    # Clear the current node's session_id by setting to None
    # (cannot delete required TypedDict key)
    if "current_node_session_id" in result:
        result["current_node_session_id"] = None

    return result

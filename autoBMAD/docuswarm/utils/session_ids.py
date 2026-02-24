"""Session ID generation utilities for DocuSwarm.

This module provides utilities for generating hierarchical session IDs
that follow the naming convention: docuswarm-{pipeline_id}-{node_id}[-iter{n}]

Session IDs are:
- Unique: Each combination of pipeline/node/iteration produces a unique ID
- Deterministic: Same inputs always produce the same output
- Recoverable: Can be used to resume sessions at any level
"""


def generate_session_id(
    pipeline_id: str,
    node_id: str | None = None,
    iteration: int | None = None,
) -> str:
    """Generate a hierarchical session ID.

    Generates session IDs following the naming convention:
    - Pipeline-level: docuswarm-{pipeline_id}
    - Node-level: docuswarm-{pipeline_id}-{node_id}
    - Iteration-level: docuswarm-{pipeline_id}-{node_id}-iter{n}

    Args:
        pipeline_id: The unique identifier for the pipeline.
        node_id: Optional node identifier. If None, returns pipeline-level ID.
        iteration: Optional iteration number. If None, returns node-level ID.

    Returns:
        A session ID string following the docuswarm-{pipeline_id}-{node_id}[-iter{n}] format.

    Examples:
        >>> generate_session_id("pipeline-001")
        'docuswarm-pipeline-001'

        >>> generate_session_id("pipeline-001", "node-a")
        'docuswarm-pipeline-001-node-a'

        >>> generate_session_id("pipeline-001", "node-a", 3)
        'docuswarm-pipeline-001-node-a-iter3'

        >>> generate_session_id("pipeline-001", None)
        'docuswarm-pipeline-001'

        >>> generate_session_id("pipeline-001", "node-a", None)
        'docuswarm-pipeline-001-node-a'
    """
    # Build base session ID with pipeline_id
    session_id = f"docuswarm-{pipeline_id}"

    # Add node_id if provided
    if node_id is not None:
        session_id = f"{session_id}-{node_id}"

        # Add iteration if provided
        if iteration is not None:
            session_id = f"{session_id}-iter{iteration}"

    return session_id

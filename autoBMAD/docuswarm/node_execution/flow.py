"""Node execution flow module for DocuSwarm (Story 3.7).

This module provides the complete node execution flow from context file
to output persistence. It coordinates:
- Context loading and validation
- Context chaining with predecessor deliverables
- State persistence to database
- Output file export

The main entry point is execute_node_flow() which orchestrates the full
execution lifecycle.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from collections.abc import Coroutine
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, cast

import aiofiles

from autoBMAD.docuswarm.node_execution.chaining import ContextChainer
from autoBMAD.docuswarm.node_execution.state import PENDING, create_node_run_state
from autoBMAD.docuswarm.node_execution.validator import ContextValidator
from autoBMAD.docuswarm.storage.state_manager import StateManager

if TYPE_CHECKING:
    pass


# Default output directory
DEFAULT_OUTPUT_DIR = Path("output")

T = TypeVar("T")


def _run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from sync context.

    Handles both cases: when there's already a running event loop and when there isn't.

    Args:
        coro: An async coroutine to run.

    Returns:
        The result of the coroutine.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, we can use asyncio.run()
        return asyncio.run(coro)

    # There's a running loop, create a new event loop in a new thread
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def load_context_file(context_file: str | Path) -> dict[str, Any]:
    """Load and validate a context file.

    Args:
        context_file: Path to the context JSON file.

    Returns:
        The parsed and validated context dictionary.

    Raises:
        FileNotFoundError: If the context file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        ValueError: If required fields are missing.
    """
    context_file = Path(context_file)
    validator = ContextValidator()

    # Run the async validate_context in sync context
    context = _run_async(validator.validate_context(context_file))

    return context


def generate_context_hash(context_file: str | Path) -> str:
    """Generate a deterministic hash for a context file.

    The hash is used for context chaining to identify related runs.

    Args:
        context_file: Path to the context file.

    Returns:
        A 16-character hexadecimal hash string.

    Raises:
        FileNotFoundError: If the context file doesn't exist.
    """
    context_file = Path(context_file)

    if not context_file.exists():
        raise FileNotFoundError(f"Context file not found: {context_file}")

    # Read raw bytes for deterministic hashing
    file_bytes = context_file.read_bytes()

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(file_bytes)
    full_hash = hash_obj.hexdigest()

    # Return first 16 characters
    return full_hash[:16]


def generate_run_id() -> str:
    """Generate a unique run ID.

    Uses UUID4 combined with timestamp for unique, sortable IDs.

    Returns:
        Run ID string in format: run-{timestamp_ms}-{uuid4}
    """
    timestamp_ms = int(time.time() * 1000)
    unique_id = uuid.uuid4().hex[:8]
    return f"run-{timestamp_ms}-{unique_id}"


async def get_chained_context(
    node_id: str,
    context_hash: str,
    no_chain: bool,
    state_manager: StateManager | None = None,
) -> dict[str, Any]:
    """Get chained context from predecessor nodes.

    Args:
        node_id: The current node ID being executed.
        context_hash: The context hash to match against previous runs.
        no_chain: If True, skip chaining and return empty dict.
        state_manager: The state manager instance for querying previous runs.

    Returns:
        Dictionary containing predecessor deliverables.
    """
    if no_chain or state_manager is None:
        return {}

    chainer = ContextChainer(state_manager)
    return await chainer.get_chained_deliverables(node_id, context_hash, no_chain)


async def export_output(
    node_id: str,
    run_id: str,
    result: dict[str, Any],
    output_dir: Path | str | None = None,
) -> dict[str, Path]:
    """Export execution output to files.

    Creates output/{node_id}/{run_id}/ directory and writes:
    - deliverable.md: The node's deliverable content
    - questions.json: List of questions generated
    - evaluation.json: Evaluation results

    Args:
        node_id: The node identifier.
        run_id: The run identifier.
        result: The execution result containing deliverable, questions, evaluation.
        output_dir: The output directory. Defaults to "output".

    Returns:
        Dictionary mapping output type to file path.
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    else:
        output_dir = Path(output_dir)

    # Create output directory structure: output/{node_id}/{run_id}/
    output_path = output_dir / node_id / run_id
    output_path.mkdir(parents=True, exist_ok=True)

    output_files: dict[str, Path] = {}

    # Write deliverable.md
    deliverable = result.get("deliverable")
    if deliverable is not None:
        # Handle both string content and dict with 'content' key
        content = deliverable if isinstance(deliverable, str) else deliverable.get("content", "")
        deliverable_file = output_path / "deliverable.md"
        async with aiofiles.open(deliverable_file, "w", encoding="utf-8") as f:
            await f.write(content)
        output_files["deliverable"] = deliverable_file

    # Write questions.json
    questions = result.get("questions", [])
    questions_file = output_path / "questions.json"
    async with aiofiles.open(questions_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(questions, indent=2, ensure_ascii=False))
    output_files["questions"] = questions_file

    # Write evaluation.json
    evaluation = result.get("evaluation")
    eval_file = output_path / "evaluation.json"
    async with aiofiles.open(eval_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(evaluation, indent=2, ensure_ascii=False))
    output_files["evaluation"] = eval_file

    return output_files


async def execute_node_flow(
    node_id: str,
    context_file: str,
    run_id: str,
    no_chain: bool = False,
    output_dir: Path | str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute the complete node flow from context to output.

    This function orchestrates the full execution lifecycle:
    1. Load and validate context file
    2. Generate context hash for chaining
    3. Get chained context from predecessors
    4. Initialize node run state
    5. Execute node via LangGraph
    6. Persist state to database
    7. Export output files

    Args:
        node_id: The node identifier (e.g., "analyst", "pm", "ux").
        context_file: Path to the context JSON file.
        run_id: Unique identifier for this run.
        no_chain: If True, skip context chaining from predecessors.
        output_dir: The output directory. Defaults to "output".
        db_path: Path to the SQLite database. Defaults to "docuswarm.db".

    Returns:
        The execution result dictionary containing status, deliverable, etc.

    Raises:
        FileNotFoundError: If the context file doesn't exist.
        json.JSONDecodeError: If the context file contains invalid JSON.
        ValueError: If required context fields are missing.
    """
    context_file_path = Path(context_file)

    # Step 1: Validate context
    validator = ContextValidator()
    await validator.validate_context(context_file_path)
    context_hash = await validator.generate_context_hash(context_file_path)

    # Step 2: Initialize state manager and get chained context
    state_manager = StateManager(db_path=db_path)
    chained_context = await get_chained_context(
        node_id=node_id,
        context_hash=context_hash,
        no_chain=no_chain,
        state_manager=state_manager,
    )

    # Step 3: Initialize node run state
    initial_state = create_node_run_state(
        run_id=run_id,
        node_id=node_id,
        context_hash=context_hash,
        context_file=str(context_file_path),
        iteration=1,
        chained_context=chained_context,
        status=PENDING,
    )

    # Step 4: Execute node via LangGraph
    from autoBMAD.docuswarm.node_execution.graph import create_node_execution_graph

    graph = create_node_execution_graph(node_id)
    config = {"configurable": {"thread_id": run_id}}

    # Execute the graph
    result = cast(dict[str, Any], await graph.ainvoke(initial_state, config))

    # Step 5: Persist to database
    # Create a synthetic pipeline_id for this node run
    pipeline_id = f"node-{node_id}-{run_id}"

    # Ensure pipeline exists (or create it)
    try:
        pipeline = state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            pipeline_id = state_manager.create_pipeline(
                subject=f"Node: {node_id}",
                subject_context={
                    "run_id": run_id,
                    "node_id": node_id,
                    "context_hash": context_hash,
                },
            )
    except Exception:
        # Continue even if pipeline creation fails
        pass

    # Save the node result - cast to expected types for save_node_result
    deliverable = cast(dict[str, Any] | None, result.get("deliverable"))
    questions = cast(list[dict[str, Any]] | None, result.get("questions"))
    evaluation = cast(dict[str, Any] | None, result.get("evaluation"))

    state_manager.save_node_result(
        pipeline_id=pipeline_id,
        node_id=node_id,
        deliverable=deliverable,
        questions=questions,
        evaluation=evaluation,
    )

    # Step 6: Export output files
    await export_output(node_id, run_id, result, output_dir)

    return result


# Additional helper functions for the StateManager integration
async def save_node_run(
    state_manager: StateManager,
    run_id: str,
    node_id: str,
    context_hash: str,
    deliverable: dict[str, Any] | None = None,
    questions: list[dict[str, Any]] | None = None,
    evaluation: dict[str, Any] | None = None,
    iteration: int = 1,  # type: ignore[reportUnusedParameter]
    status: str = "completed",  # type: ignore[reportUnusedParameter]
) -> bool:
    """Save node run to database.

    This is a wrapper around StateManager.save_node_result that follows
    the Story 3.7 interface.

    Args:
        state_manager: The state manager instance.
        run_id: Unique identifier for this run.
        node_id: The node identifier.
        context_hash: The context hash for this run.
        deliverable: Optional deliverable data.
        questions: Optional list of questions.
        evaluation: Optional evaluation data.
        iteration: The iteration number.
        status: The run status.

    Returns:
        True if save was successful.
    """
    # Mark unused parameters as intentionally unused
    _ = iteration
    _ = status

    # Create a pipeline_id from run_id for state manager compatibility
    # The state manager expects pipeline_id, so we create a synthetic one
    # from the run_id
    pipeline_id = f"node-run-{run_id}"

    # Ensure pipeline exists in the state manager
    try:
        # Try to get the pipeline - if it doesn't exist, create it
        pipeline = state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            # Create a minimal pipeline entry for this node run
            pipeline_id = state_manager.create_pipeline(
                subject=f"Node run: {node_id}",
                subject_context={
                    "run_id": run_id,
                    "node_id": node_id,
                    "context_hash": context_hash,
                },
            )
    except Exception:
        # If we can't create pipeline, try to save directly
        pass

    # Save node result
    return state_manager.save_node_result(
        pipeline_id=pipeline_id,
        node_id=node_id,
        deliverable=deliverable,
        questions=questions,
        evaluation=evaluation,
    )


# Extend StateManager with run_id support if needed
def _patch_state_manager() -> None:
    """Patch StateManager to support run_id-based storage."""
    # This is handled in execute_node_flow by creating synthetic pipeline_id
    pass


# Keep function reference to avoid unused warning
_ = _patch_state_manager  # type: ignore[reportUnusedFunction]

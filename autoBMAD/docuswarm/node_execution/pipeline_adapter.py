"""Pipeline Adapter for node_execution to pipeline integration.

TD-4: This module provides a single boundary layer for adapting node_execution
to the pipeline interface. It centralizes synthetic ID creation and state
conversion to keep business logic clean.

All synthetic pipeline_id creation should go through this adapter.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import TYPE_CHECKING, Any

from autoBMAD.docuswarm.node_execution.state import COMPLETED

if TYPE_CHECKING:
    from autoBMAD.docuswarm.pipeline.state import PipelineState


def _deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries.

    For dict values, recursively merge.
    For list values, extend the base list with override items.
    For other values, override wins.

    Args:
        base: The base dictionary.
        override: The dictionary to merge into base.

    Returns:
        A new dictionary with merged values.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + [v for v in value if v not in result[key]]
        else:
            result[key] = copy.deepcopy(value)
    return result


class PipelineAdapter:
    """Adapter for node_execution to pipeline integration.

    This class centralizes the boundary between node_execution and pipeline
    modules, specifically:
    - Synthetic pipeline_id creation (TD-4)
    - State format conversion

    By centralizing these adaptations here, we prevent synthetic ID logic
    from spreading throughout the business logic layer.

    Example:
        >>> pipeline_id = PipelineAdapter.create_pipeline_id("analyst", "run-123")
        >>> pipeline_id
        'node-analyst-run-123'
    """

    @staticmethod
    def create_pipeline_id(node_id: str, run_id: str) -> str:
        """Create a synthetic pipeline_id for a node run.

        This is the single place where synthetic pipeline IDs are created.
        All code that needs a synthetic pipeline_id should use this method.

        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm').
            run_id: The run identifier.

        Returns:
            Synthetic pipeline_id in format: node-{node_id}-{run_id}
        """
        return f"node-{node_id}-{run_id}"

    @staticmethod
    def create_run_pipeline_id(run_id: str) -> str:
        """Create a run-level synthetic pipeline_id.

        Args:
            run_id: The run identifier.

        Returns:
            Synthetic pipeline_id in format: node-run-{run_id}
        """
        return f"node-run-{run_id}"

    @staticmethod
    def parse_pipeline_id(pipeline_id: str) -> dict[str, str] | None:
        """Parse a synthetic pipeline_id to extract components.

        Args:
            pipeline_id: The synthetic pipeline_id.

        Returns:
            Dictionary with 'node_id' and 'run_id' keys, or None if not a synthetic ID.
        """
        if not pipeline_id.startswith("node-"):
            return None

        # Remove 'node-' prefix
        rest = pipeline_id[5:]

        # Check for run-level format: node-run-{run_id}
        if rest.startswith("run-"):
            return {
                "node_id": "",
                "run_id": rest[4:],
                "type": "run",
            }

        # Check for node-level format: node-{node_id}-{run_id}
        parts = rest.split("-", 1)
        if len(parts) == 2:
            return {
                "node_id": parts[0],
                "run_id": parts[1],
                "type": "node",
            }

        return None

    @staticmethod
    def is_synthetic_pipeline_id(pipeline_id: str) -> bool:
        """Check if a pipeline_id is synthetic (created by this adapter).

        Args:
            pipeline_id: The pipeline_id to check.

        Returns:
            True if it's a synthetic pipeline_id.
        """
        return pipeline_id.startswith("node-")

    @staticmethod
    def adapt_state(node_execution_state: dict[str, Any]) -> PipelineState:
        """Convert node_execution state to PipelineState format.

        This method ensures that node_execution state is properly converted
        to the PipelineState format expected by the pipeline layer.

        Args:
            node_execution_state: State from node_execution.

        Returns:
            PipelineState compatible state dictionary.
        """
        from autoBMAD.docuswarm.pipeline.state import create_initial_state

        # Extract required fields with defaults
        pipeline_id = node_execution_state.get("run_id", "")
        node_id = node_execution_state.get("node_id", "")

        # Create synthetic pipeline_id if needed
        if pipeline_id and not pipeline_id.startswith("node-"):
            pipeline_id = PipelineAdapter.create_pipeline_id(node_id, pipeline_id)

        # Create initial state
        subject_context = node_execution_state.get("subject_context", {})
        state = create_initial_state(pipeline_id, subject_context)

        # Update with node_execution specific data
        state["current_node"] = node_id
        state["status"] = node_execution_state.get("status", "running")

        # Add deliverable if present
        if "deliverable" in node_execution_state:
            state["deliverables"][node_id] = node_execution_state["deliverable"]
            if node_id not in state["completed_nodes"]:
                state["completed_nodes"].append(node_id)

        return state

    @staticmethod
    def extract_node_id_from_pipeline(pipeline_id: str, default: str = "") -> str:
        """Extract node_id from a synthetic pipeline_id.

        Args:
            pipeline_id: The pipeline_id.
            default: Default value if not a synthetic ID.

        Returns:
            The node_id or default value.
        """
        parsed = PipelineAdapter.parse_pipeline_id(pipeline_id)
        if parsed and parsed["type"] == "node":
            return parsed["node_id"]
        return default

    # ==========================================================================
    # State Conversion (MOVED from pipeline/graph.py)
    # ==========================================================================

    @staticmethod
    def convert_pipeline_to_node_state(
        pipeline_state: PipelineState,
        node_id: str,
        docs_context_summary: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Convert PipelineState to NodeRunState for node execution.

        **RESPONSIBILITY TRANSFERRED**: This logic was previously in
        pipeline/graph.py:_convert_pipeline_to_node_state but has been moved here
        to centralize boundary crossing logic.

        Args:
            pipeline_state: The current PipelineState.
            node_id: The node identifier being executed.
            docs_context_summary: Optional list of document summaries to include
                in the node's original_context. If provided, takes precedence over
                the value in pipeline_state. If None, extracts from pipeline_state
                for backward compatibility.

        Returns:
            A dictionary in NodeRunState format suitable for node execution.
        """
        # Generate context_hash from subject_context and node_id
        subject_context = pipeline_state.get("subject_context", {})
        context_str = json.dumps(subject_context, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()

        # Build accumulated context
        deliverables = pipeline_state.get("deliverables", {})
        accumulated = PipelineAdapter._accumulate_context(subject_context, deliverables, node_id)

        # Story 37.5: Use explicitly passed docs_context_summary if provided,
        # otherwise fall back to extracting from pipeline_state for backward compatibility
        docs_summary = (
            docs_context_summary
            if docs_context_summary is not None
            else pipeline_state.get("docs_context_summary", [])
        )
        if docs_summary:
            accumulated["docs_context_summary"] = docs_summary

        context_file = json.dumps(accumulated)

        # Get current iteration for this node
        node_iterations = pipeline_state.get("node_iterations", {})
        iteration = node_iterations.get(node_id, 0) + 1

        # Build chained_context from previous deliverables
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

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
            "run_id": pipeline_state.get("pipeline_id", "unknown"),
            "pipeline_id": pipeline_state.get("pipeline_id", "unknown"),
            "node_id": node_id,
            "context_hash": context_hash,
            "context_file": context_file,
            "iteration": iteration,
            "deliverable": None,
            "questions": [],
            "evaluation": None,
            "answers": {},
            "chained_context": chained_context,
            "shared_context": pipeline_state.get("shared_context", {}),
            "status": "pending",
        }

    @staticmethod
    def convert_node_to_pipeline_state(
        node_state: dict[str, Any],
        original_state: PipelineState,
    ) -> PipelineState:
        """Convert NodeRunState back to PipelineState after node execution.

        **RESPONSIBILITY TRANSFERRED**: This logic was previously in
        pipeline/graph.py:_convert_node_to_pipeline_state but has been moved here
        to centralize boundary crossing logic.

        Args:
            node_state: The NodeRunState after node execution.
            original_state: The original PipelineState before node execution.

        Returns:
            Updated PipelineState with node execution results merged in.
        """
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

        # P0-F1: Only add to completed_nodes if status is COMPLETED
        node_status = node_state.get("status", "")
        if node_status == COMPLETED:
            if "completed_nodes" not in new_state:
                new_state["completed_nodes"] = []
            if node_id is not None and node_id not in new_state["completed_nodes"]:
                new_state["completed_nodes"] = new_state["completed_nodes"] + [str(node_id)]
            # Remove from failed_nodes if previously failed and now recovered
            if "failed_nodes" in new_state and node_id in new_state["failed_nodes"]:
                new_state["failed_nodes"] = [n for n in new_state["failed_nodes"] if n != node_id]
        else:
            # P0-F1: Non-completed status => add to failed_nodes
            if "failed_nodes" not in new_state:
                new_state["failed_nodes"] = []
            if node_id is not None and node_id not in new_state["failed_nodes"]:
                new_state["failed_nodes"] = new_state["failed_nodes"] + [str(node_id)]
            # Set error if not already set
            if not new_state.get("error"):
                new_state["error"] = {
                    "node_id": node_id,
                    "status": node_status,
                    "message": f"Node {node_id} finished with status {node_status}",
                }

        # P0-F2: Merge shared_context from node_state back to pipeline_state
        node_shared_context = node_state.get("shared_context")
        if node_shared_context is not None:
            if "shared_context" not in new_state:
                new_state["shared_context"] = {}
            # Deep merge: preserve existing keys, update with node changes
            new_state["shared_context"] = _deep_merge_dicts(
                new_state["shared_context"], node_shared_context
            )

        # Update current_node
        new_state["current_node"] = node_id

        return new_state

    @staticmethod
    def _accumulate_context(
        subject_context: dict[str, Any],
        deliverables: dict[str, dict[str, Any]],
        current_node: str,
    ) -> dict[str, Any]:
        """Accumulate context by merging subject context with previous deliverables.

        Private helper moved from pipeline.state module.

        Args:
            subject_context: The initial subject/context of the pipeline.
            deliverables: Dictionary of node deliverables (key: node_id).
            current_node: The node that will receive this context.

        Returns:
            A new context dictionary containing subject_context and all previous deliverables.
        """
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

        try:
            current_index = PIPELINE_NODES.index(current_node)
        except ValueError:
            return {"subject_context": subject_context}

        previous_nodes = PIPELINE_NODES[:current_index]

        accumulated: dict[str, Any] = {
            "subject_context": subject_context.copy() if subject_context else {},
        }

        for node_id in previous_nodes:
            if node_id in deliverables and deliverables[node_id]:
                accumulated[f"{node_id}_deliverable"] = deliverables[node_id].copy()

        return accumulated

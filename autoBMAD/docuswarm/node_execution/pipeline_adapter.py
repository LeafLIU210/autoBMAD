"""Pipeline Adapter for node_execution to pipeline integration.

TD-4: This module provides a single boundary layer for adapting node_execution
to the pipeline interface. It centralizes synthetic ID creation and state
conversion to keep business logic clean.

All synthetic pipeline_id creation should go through this adapter.
"""

from __future__ import annotations

from typing import Any

from autoBMAD.docuswarm.pipeline.state import PipelineState


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

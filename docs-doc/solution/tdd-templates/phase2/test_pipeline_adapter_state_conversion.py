"""Test PipelineAdapter state conversion methods.

TDD Phase 2.1: State conversion moved to PipelineAdapter.

Usage:
    1. Copy to tests/node_execution/test_pipeline_adapter_state_conversion.py
    2. Run: pytest tests/node_execution/test_pipeline_adapter_state_conversion.py -v
    3. Expected: 8 failed (Red phase)
    4. Implement methods in PipelineAdapter
    5. Update graph.py to use Adapter
    6. Run again: Expected 8 passed (Green phase)
"""

import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import create_initial_state, PipelineState


class TestPipelineAdapterStateConversion:
    """Test suite: State conversion is PipelineAdapter's responsibility."""

    def test_convert_pipeline_to_node_state_exists(self):
        """RED: PipelineAdapter must have convert_pipeline_to_node_state method."""
        assert hasattr(PipelineAdapter, 'convert_pipeline_to_node_state'), \\
            "PipelineAdapter must have convert_pipeline_to_node_state method"

    def test_convert_node_to_pipeline_state_exists(self):
        """RED: PipelineAdapter must have convert_node_to_pipeline_state method."""
        assert hasattr(PipelineAdapter, 'convert_node_to_pipeline_state'), \\
            "PipelineAdapter must have convert_node_to_pipeline_state method"

    def test_convert_pipeline_to_node_state_basic(self):
        """RED: Conversion must work for basic case."""
        # Arrange
        pipeline_state = create_initial_state("test-pipeline-123", {
            "task": "Build a website",
            "requirements": ["fast", "secure"]
        })
        
        # Act
        node_state = PipelineAdapter.convert_pipeline_to_node_state(
            pipeline_state, "analyst"
        )
        
        # Assert
        assert node_state["pipeline_id"] == "test-pipeline-123"
        assert node_state["node_id"] == "analyst"
        assert node_state["status"] == "pending"
        assert "context_hash" in node_state
        assert "context_file" in node_state
        assert "chained_context" in node_state

    def test_convert_pipeline_to_node_state_accumulates_context(self):
        """RED: Conversion must accumulate context from previous nodes."""
        # Arrange: Pipeline with some completed nodes
        pipeline_state = create_initial_state("test-pipeline-456", {
            "task": "Build an app"
        })
        pipeline_state["completed_nodes"] = ["analyst", "pm"]
        pipeline_state["deliverables"] = {
            "analyst": {"analysis": "Market research complete"},
            "pm": {"plan": "Project plan created"}
        }
        
        # Act: Convert for UX node (after analyst and pm)
        node_state = PipelineAdapter.convert_pipeline_to_node_state(
            pipeline_state, "ux"
        )
        
        # Assert
        assert "chained_context" in node_state
        chained = node_state["chained_context"]
        assert "analyst" in chained
        assert "pm" in chained
        assert "analysis" in chained["analyst"]["deliverable"]

    def test_convert_node_to_pipeline_state_basic(self):
        """RED: Reverse conversion must work."""
        # Arrange
        original_state = create_initial_state("test-pipeline-789", {"task": "Test"})
        node_state = {
            "node_id": "analyst",
            "deliverable": {"content": "Analysis complete"},
            "questions": [{"text": "What is the budget?"}],
            "evaluation": {"verdict": "APPROVED", "score": 0.95},
            "iteration": 2,
        }
        
        # Act
        result = PipelineAdapter.convert_node_to_pipeline_state(
            node_state, original_state
        )
        
        # Assert
        assert "analyst" in result["deliverables"]
        assert result["deliverables"]["analyst"]["content"] == "Analysis complete"
        assert "analyst" in result["questions"]
        assert result["questions"]["analyst"][0]["text"] == "What is the budget?"
        assert "analyst" in result["evaluations"]
        assert result["evaluations"]["analyst"]["verdict"] == "APPROVED"
        assert result["current_node"] == "analyst"
        assert "analyst" in result["completed_nodes"]

    def test_convert_node_to_pipeline_state_preserves_other_data(self):
        """RED: Conversion must preserve existing pipeline state data."""
        # Arrange
        original_state = create_initial_state("test-pipeline", {"task": "Test"})
        original_state["completed_nodes"] = ["pm"]
        original_state["deliverables"]["pm"] = {"plan": "Existing plan"}
        
        node_state = {
            "node_id": "analyst",
            "deliverable": {"analysis": "New analysis"},
            "questions": [],
            "evaluation": None,
            "iteration": 1,
        }
        
        # Act
        result = PipelineAdapter.convert_node_to_pipeline_state(
            node_state, original_state
        )
        
        # Assert: Existing data preserved
        assert "pm" in result["deliverables"]
        assert result["deliverables"]["pm"]["plan"] == "Existing plan"
        
        # Assert: New data added
        assert "analyst" in result["deliverables"]
        assert result["deliverables"]["analyst"]["analysis"] == "New analysis"

    def test_graph_py_uses_adapter_for_conversion(self):
        """RED: graph.py must call PipelineAdapter methods, not internal functions.
        
        This is an architectural test verifying the implementation uses the Adapter.
        """
        from autoBMAD.docuswarm.pipeline import graph as graph_module
        
        # Read the source
        import inspect
        source = inspect.getsource(graph_module)
        
        # Must import PipelineAdapter
        assert "from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter" in source
        
        # Must use Adapter methods (in _create_integrated_node_executor)
        assert "PipelineAdapter.convert_pipeline_to_node_state(" in source
        assert "PipelineAdapter.convert_node_to_pipeline_state(" in source
        
        # Should NOT have the old internal functions
        assert "def _convert_pipeline_to_node_state(" not in source
        assert "def _convert_node_to_pipeline_state(" not in source

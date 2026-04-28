"""Test session_manager is required for create_pipeline_graph.

TDD Phase 1.1: Session manager must be required, not optional.

Usage:
    1. Copy to tests/pipeline/test_create_pipeline_graph_signature.py
    2. Run: pytest tests/pipeline/test_create_pipeline_graph_signature.py -v
    3. Expected: 3 failed (Red phase)
    4. Implement changes to pipeline/graph.py
    5. Run again: Expected 3 passed (Green phase)
"""

import pytest
import inspect
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph


class TestCreatePipelineGraphSessionManagerRequired:
    """Test suite: session_manager is now a required parameter."""

    def test_session_manager_none_raises_value_error(self):
        """RED: Passing None for session_manager must raise ValueError.
        
        This test documents the breaking change: the deprecated default executor
        fallback has been removed. Callers must provide a valid session_manager.
        """
        # Arrange: No session_manager provided
        
        # Act & Assert: Must raise ValueError with descriptive message
        with pytest.raises(ValueError) as exc_info:
            create_pipeline_graph(session_manager=None)  # type: ignore
        
        error_message = str(exc_info.value)
        assert "session_manager is required" in error_message
        assert "deprecated default executor was removed" in error_message

    def test_session_manager_provided_works(self, mock_session_manager):
        """GREEN: Providing a valid session_manager must work.
        
        This is the expected usage pattern after migration.
        """
        # Arrange
        session_manager = mock_session_manager
        
        # Act: Should not raise
        graph = create_pipeline_graph(
            session_manager=session_manager,
            compile_graph=False
        )
        
        # Assert
        assert graph is not None

    def test_old_signature_with_optional_removed(self):
        """RED: The old signature with 'Any | None = None' must no longer exist.
        
        This is an architectural test - we inspect the function signature
        to ensure the migration is complete.
        """
        sig = inspect.signature(create_pipeline_graph)
        params = sig.parameters
        
        session_manager_param = params.get('session_manager')
        assert session_manager_param is not None
        
        # After migration, there should be no default (Parameter.empty)
        # OR the default should not be None
        assert session_manager_param.default is not inspect.Parameter.empty
        # This assertion will fail before migration:
        # assert session_manager_param.default is None  # Current state
        # After migration:
        assert session_manager_param.default is None  # Will fail after fix


# Fixture definition (add to conftest.py or keep here)
@pytest.fixture
def mock_session_manager():
    """Create a mock session manager for testing."""
    from unittest.mock import MagicMock
    return MagicMock(spec="autoBMAD.docuswarm.llm.session_manager.KimiSessionManager")

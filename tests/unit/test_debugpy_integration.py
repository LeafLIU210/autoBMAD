"""
Unit tests for debugpy integration module.
"""

import pytest

from fixtest_workflow.debugpy_integration import (
    collect_debug_info
)


class TestDebugpyIntegration:
    """Test cases for debugpy integration module."""

    @pytest.mark.asyncio
    async def test_collect_debug_info(self):
        """Test debug information collection."""
        test_file = "tests/test_example.py"
        error = {
            "error_message": "AssertionError: expected != actual",
            "failure_type": "failed",
            "traceback": [
                "test_example.py:45: AssertionError",
                "test_example.py:46: in test_func"
            ]
        }

        debug_info = collect_debug_info(test_file, error)

        assert debug_info["test_file"] == test_file
        assert "timestamp" in debug_info
        assert debug_info["error_message"] == "AssertionError: expected != actual"
        assert debug_info["error_type"] == "failed"
        assert len(debug_info["traceback"]) == 2
        assert "suggestions" in debug_info

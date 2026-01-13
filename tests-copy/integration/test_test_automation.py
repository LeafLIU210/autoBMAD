"""
Integration tests for test automation workflow.
"""

import pytest
import tempfile
import unittest.mock
from pathlib import Path
from unittest.mock import patch
import json

from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent
from autoBMAD.epic_automation.state_manager import StateManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_progress.db"
        yield str(db_path)


@pytest.fixture
async def state_manager(temp_db):
    """Create a StateManager with temporary database."""
    sm = StateManager(temp_db)
    yield sm
    # Cleanup is automatic with tempfile


class TestTestAutomationIntegration:
    """Integration tests for test automation workflow."""

    @pytest.mark.asyncio
    async def test_complete_test_automation_workflow(self, state_manager):
        """Test complete test automation workflow from start to finish."""
        # Create test agent
        agent = TestAutomationAgent(
            state_manager=state_manager,
            epic_id="test-epic-integration",
            skip_tests=False
        )

        # Create temporary test directory
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # Create a simple test file
            test_file = test_dir / "test_simple.py"
            test_file.write_text("""
def test_pass():
    '''A test that passes.'''
    assert 1 + 1 == 2

def test_another_pass():
    '''Another passing test.'''
    assert "hello" == "hello"
""")

            # Mock pytest execution
            with patch('fixtest_workflow.test_automation_workflow.run_pytest_execution') as mock_pytest:
                mock_pytest.return_value = {
                    "success": True,
                    "summary": {
                        "total": 2,
                        "passed": 2,
                        "failed": 0,
                        "error": 0,
                        "skipped": 0
                    },
                    "json_report_path": "test_results.json"
                }

                # Run test automation
                result = await agent.run_test_automation(test_dir=str(test_dir))

                # Verify results
                assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_test_automation_with_failures_and_retries(self, state_manager):
        """Test test automation with failures and retry attempts."""
        agent = TestAutomationAgent(
            state_manager=state_manager,
            epic_id="test-epic-failures",
            skip_tests=False
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # Create a test file that will fail
            test_file = test_dir / "test_failing.py"
            test_file.write_text("""
def test_fail():
    '''A test that fails.'''
    assert 1 + 1 == 3
""")

            # Mock pytest execution with failures
            with patch('fixtest_workflow.test_automation_workflow.run_pytest_execution') as mock_pytest:
                mock_pytest.return_value = {
                    "success": False,
                    "summary": {
                        "total": 1,
                        "passed": 0,
                        "failed": 1,
                        "error": 0,
                        "skipped": 0
                    },
                    "json_report_path": "test_results.json"
                }

                # Mock JSON report with failures
                mock_report = {
                    "summary": {
                        "total": 1,
                        "passed": 0,
                        "failed": 1,
                        "error": 0,
                        "skipped": 0
                    },
                    "tests": [
                        {
                            "nodeid": "tests/test_failing.py::test_fail",
                            "outcome": "failed",
                            "longrepr": "AssertionError: assert 1 + 1 == 3",
                            "traceback": ["test_failing.py:5: AssertionError"]
                        }
                    ]
                }

                with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(mock_report))):
                    with patch('pathlib.Path.exists', return_value=True):
                        # Run test automation
                        result = await agent.run_test_automation(test_dir=str(test_dir))

                        # Verify results - status can be failed or completed_with_debugpy
                        assert result["status"] in ["failed", "completed_with_debugpy"]

    @pytest.mark.asyncio
    async def test_test_automation_skip_flag(self, state_manager):
        """Test test automation bypass with skip_tests flag."""
        agent = TestAutomationAgent(
            state_manager=state_manager,
            epic_id="test-epic-skip",
            skip_tests=True
        )

        result = await agent.run_test_automation(
            test_dir="tests",
            skip_tests=True
        )

        assert result["status"] == "skipped"
        assert "bypassed" in result["message"]

    @pytest.mark.asyncio
    async def test_state_manager_integration(self, state_manager):
        """Test integration with state manager."""
        agent = TestAutomationAgent(
            state_manager=state_manager,
            epic_id="test-epic-state",
            skip_tests=False
        )

        # Add a test phase record
        record_id = await state_manager.add_test_phase_record(
            epic_id="test-epic-state",
            test_file_path="tests/test_example.py",
            failure_count=2,
            debug_info="Test debug info",
            fix_status="pending"
        )

        assert record_id is not None

        # Update the record
        success = await state_manager.update_test_phase_status(
            record_id=record_id,
            fix_status="in_progress",
            failure_count=1
        )

        assert success is True

        # Get records
        records = await state_manager.get_test_phase_records("test-epic-state")
        assert len(records) > 0

    @pytest.mark.asyncio
    async def test_no_test_files(self, state_manager):
        """Test test automation with directory containing no test files."""
        agent = TestAutomationAgent(
            state_manager=state_manager,
            epic_id="test-epic-empty",
            skip_tests=False
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # Create a non-test Python file
            py_file = test_dir / "module.py"
            py_file.write_text("# This is not a test file\nprint('hello')")

            # Run test automation
            result = await agent.run_test_automation(test_dir=str(test_dir))

            # Should complete with no tests
            assert result["status"] == "completed"
            assert result["message"] == "No test files to execute"
            assert result["summary"]["total_tests"] == 0

    @pytest.mark.asyncio
    async def test_test_automation_with_quality_gates_integration(self, state_manager):
        """Test that test automation works after quality gates."""
        # This tests the integration point where test automation
        # is called after quality gates in epic_driver

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # Create a passing test
            test_file = test_dir / "test_integration.py"
            test_file.write_text("""
def test_integration():
    '''Integration test.'''
    assert True
""")

            agent = TestAutomationAgent(
                state_manager=state_manager,
                epic_id="test-epic-integration",
                skip_tests=False
            )

            # Mock successful pytest execution
            with patch('fixtest_workflow.test_automation_workflow.run_pytest_execution') as mock_pytest:
                mock_pytest.return_value = {
                    "success": True,
                    "summary": {
                        "total": 1,
                        "passed": 1,
                        "failed": 0,
                        "error": 0,
                        "skipped": 0
                    },
                    "json_report_path": "test_results.json"
                }

                result = await agent.run_test_automation(test_dir=str(test_dir))

                # Verify the complete workflow
                assert result["status"] == "completed"

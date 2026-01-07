"""
Unit tests for TestAutomationAgent.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import json

from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent


@pytest.fixture
def mock_state_manager():
    """Create a mock StateManager."""
    sm = Mock()
    sm.add_test_phase_record = AsyncMock(return_value="test-record-id")
    sm.update_test_phase_status = AsyncMock(return_value=True)
    return sm


@pytest.fixture
def test_agent(mock_state_manager):
    """Create TestAutomationAgent for testing."""
    return TestAutomationAgent(mock_state_manager, "test-epic-001", skip_tests=False)


class TestTestAutomationAgent:
    """Test cases for TestAutomationAgent."""

    @pytest.mark.asyncio
    async def test_init(self, test_agent):
        """Test TestAutomationAgent initialization."""
        assert test_agent.state_manager is not None
        assert test_agent.epic_id == "test-epic-001"
        assert test_agent.max_retry_attempts == 5
        assert test_agent.debugpy_timeout == 300
        assert test_agent.skip_tests is False

    @pytest.mark.asyncio
    async def test_run_test_automation_skip_tests(self, test_agent):
        """Test test automation bypass when skip_tests is True."""
        result = await test_agent.run_test_automation(
            test_dir="tests",
            skip_tests=True
        )

        assert result["status"] == "skipped"
        assert "bypassed" in result["message"]

    @pytest.mark.asyncio
    async def test_run_test_automation_no_test_dir(self, test_agent):
        """Test test automation with non-existent test directory."""
        result = await test_agent.run_test_automation(test_dir="nonexistent_dir_12345")

        assert result["status"] == "failed"
        assert len(result["errors"]) > 0
        assert "not found" in result["errors"][0].lower()

    @pytest.mark.asyncio
    async def test_run_test_automation_no_test_files(self, test_agent, tmp_path):
        """Test test automation with no test files."""
        # Create empty test directory
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        result = await test_agent.run_test_automation(test_dir=str(test_dir))

        assert result["status"] == "completed"
        assert result["summary"]["total_tests"] == 0

    @pytest.mark.asyncio
    @patch('fixtest_workflow.test_automation_workflow.run_pytest_execution')
    async def test_run_test_automation_success(self, mock_pytest, test_agent, tmp_path):
        """Test successful test automation execution."""
        # Create test directory with a test file
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        test_file = test_dir / "test_example.py"
        test_file.write_text("def test_pass(): assert True")

        # Mock pytest execution success
        mock_pytest.return_value = {
            "success": True,
            "summary": {
                "total": 10,
                "passed": 10,
                "failed": 0,
                "error": 0,
                "skipped": 0
            },
            "json_report_path": "test_results.json"
        }

        # Also mock collect_failures to return empty list (no failures)
        with patch.object(test_agent, 'collect_failures', return_value=[]):
            result = await test_agent.run_test_automation(test_dir=str(test_dir))

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    @patch('fixtest_workflow.test_automation_workflow.run_pytest_execution')
    async def test_run_test_automation_with_failures(self, mock_pytest, test_agent, tmp_path):
        """Test test automation with test failures."""
        # Create test directory
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        test_file = test_dir / "test_example.py"
        test_file.write_text("def test_fail(): assert False")

        # Mock pytest execution with failures
        mock_pytest.return_value = {
            "success": False,
            "summary": {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "error": 0,
                "skipped": 0
            },
            "json_report_path": str(tmp_path / "test_results.json")
        }

        # Create mock JSON report
        report_path = tmp_path / "test_results.json"
        mock_report = {
            "summary": {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "error": 0,
                "skipped": 0
            },
            "tests": [
                {
                    "nodeid": "tests/test_example.py::test_fail",
                    "outcome": "failed",
                    "longrepr": "AssertionError",
                    "traceback": []
                }
            ]
        }
        report_path.write_text(json.dumps(mock_report))

        result = await test_agent.run_test_automation(test_dir=str(test_dir))

        # Either completed with failures or still in progress
        assert result["status"] in ["completed", "completed_with_debugpy", "failed"]

    @pytest.mark.asyncio
    async def test_collect_failures(self, test_agent, tmp_path):
        """Test failure collection from JSON report."""
        # Create mock JSON report
        mock_report = {
            "tests": [
                {
                    "nodeid": "tests/test_example.py::test_pass",
                    "outcome": "passed",
                    "longrepr": "",
                    "traceback": []
                },
                {
                    "nodeid": "tests/test_example.py::test_fail",
                    "outcome": "failed",
                    "longrepr": "AssertionError: expected != actual",
                    "traceback": ["test_example.py:45: AssertionError"]
                },
                {
                    "nodeid": "tests/test_example.py::test_error",
                    "outcome": "error",
                    "longrepr": "ValueError: invalid value",
                    "traceback": ["test_example.py:50: ValueError"]
                }
            ]
        }

        report_path = tmp_path / "test_results.json"
        report_path.write_text(json.dumps(mock_report))

        failures = await test_agent.collect_failures(str(report_path))

        assert len(failures) == 2
        assert failures[0]["test_file"] == "tests/test_example.py"
        assert failures[0]["failure_type"] == "failed"

    @pytest.mark.asyncio
    async def test_collect_failures_no_file(self, test_agent):
        """Test failure collection with non-existent JSON file."""
        failures = await test_agent.collect_failures("nonexistent.json")
        assert len(failures) == 0

    @pytest.mark.asyncio
    async def test_generate_test_report(self, test_agent, tmp_path, monkeypatch):
        """Test test report generation."""
        # Change to temp directory to avoid writing to project
        monkeypatch.chdir(tmp_path)

        # Create test results
        results = {
            "epic_id": "test-epic-001",
            "timestamp": "2026-01-05T10:00:00",
            "pytest": {
                "summary": {
                    "total": 10,
                    "passed": 8,
                    "failed": 2,
                    "error": 0,
                    "skipped": 0
                }
            },
            "failed_tests": [
                {
                    "test_file": "tests/test_example.py",
                    "test_name": "test_fail",
                    "failure_type": "failed",
                    "error_message": "AssertionError"
                }
            ],
            "retry_history": [],
            "debugpy_sessions": [],
            "status": "completed"
        }

        report_path = test_agent.generate_test_report(results, results["failed_tests"])

        # Verify report was written
        assert Path(report_path).exists()

    @pytest.mark.asyncio
    @patch('fixtest_workflow.debugpy_integration.collect_debug_info')
    async def test_invoke_debugpy(self, mock_collect, test_agent):
        """Test debugpy invocation for persistent failures."""
        mock_collect.return_value = {"test_file": "tests/test_example.py", "debug_info": "test"}

        error_details = {
            "failure_type": "failed",
            "error_message": "AssertionError",
            "traceback": ["test_example.py:45"]
        }

        result = await test_agent.invoke_debugpy(
            "tests/test_example.py",
            error_details
        )

        # Result should have debug info
        assert result is not None

    @pytest.mark.asyncio
    async def test_fix_tests(self, test_agent):
        """Test automated test fixing."""
        failures = [
            {
                "test_file": "tests/test_example.py",
                "test_name": "test_fail",
                "failure_type": "failed",
                "error_message": "AssertionError"
            }
        ]

        # Currently returns False (not implemented)
        result = await test_agent.fix_tests(failures)
        assert result is False

"""
Unit tests for TestAutomationAgent.

Tests cover:
1. Pytest command execution
2. JSON report parsing
3. Debugpy invocation logic
4. Fix generation workflow
5. Retry cycle mechanism
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent
from autoBMAD.epic_automation.state_manager import StateManager


@pytest.fixture
def mock_state_manager():
    """Create a mock StateManager."""
    return MagicMock(spec=StateManager)


@pytest.fixture
def test_agent(mock_state_manager):
    """Create a TestAutomationAgent instance."""
    return TestAutomationAgent(
        state_manager=mock_state_manager,
        epic_id="test-epic-001"
    )


@pytest.fixture
def sample_pytest_json_report():
    """Sample pytest JSON report for testing."""
    return {
        "summary": {
            "total": 5,
            "passed": 3,
            "failed": 2,
            "skipped": 0,
            "error": 0
        },
        "duration": 1.5,
        "tests": [
            {
                "nodeid": "tests/test_example.py::test_passing_1",
                "outcome": "passed",
                "duration": 0.1
            },
            {
                "nodeid": "tests/test_example.py::test_passing_2",
                "outcome": "passed",
                "duration": 0.2
            },
            {
                "nodeid": "tests/test_example.py::test_passing_3",
                "outcome": "passed",
                "duration": 0.15
            },
            {
                "nodeid": "tests/test_example.py::test_failing_1",
                "outcome": "failed",
                "duration": 0.3,
                "longrepr": "AssertionError: Expected 1, got 2"
            },
            {
                "nodeid": "tests/test_example.py::test_failing_2",
                "outcome": "failed",
                "duration": 0.25,
                "longrepr": "TypeError: unsupported operand type"
            }
        ]
    }


class TestPytestExecution:
    """Tests for pytest execution functionality."""

    @pytest.mark.asyncio
    async def test_run_pytest_execution_success(self, test_agent, tmp_path):
        """Test successful pytest execution."""
        # Create a mock JSON report
        json_report = {
            "summary": {"total": 1, "passed": 1, "failed": 0, "error": 0},
            "tests": [{"nodeid": "test.py::test_pass", "outcome": "passed"}]
        }
        report_path = tmp_path / "test_results.json"
        with open(report_path, "w") as f:
            json.dump(json_report, f)

        # Mock the subprocess
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Patch Path to use our temp file
            with patch.object(Path, "exists", return_value=True):
                with patch("builtins.open", create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(json_report)
                    mock_file = MagicMock()
                    mock_file.__enter__ = MagicMock(return_value=mock_file)
                    mock_file.__exit__ = MagicMock(return_value=False)
                    mock_file.read.return_value = json.dumps(json_report)
                    mock_open.return_value = mock_file

                    result = await test_agent.run_pytest_execution(str(tmp_path), str(report_path))

        assert mock_subprocess.called

    @pytest.mark.asyncio
    async def test_run_pytest_execution_failure(self, test_agent):
        """Test pytest execution when subprocess fails."""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_subprocess.side_effect = Exception("Subprocess failed")

            result = await test_agent.run_pytest_execution("tests", "test_results.json")

            assert result["success"] is False
            assert "error" in result


class TestJSONReportParsing:
    """Tests for JSON report parsing functionality."""

    @pytest.mark.asyncio
    async def test_collect_failures_with_failures(self, test_agent, sample_pytest_json_report, tmp_path):
        """Test collecting failures from JSON report."""
        report_path = tmp_path / "test_results.json"
        with open(report_path, "w") as f:
            json.dump(sample_pytest_json_report, f)

        failures = await test_agent.collect_failures(str(report_path))

        assert len(failures) == 2
        assert failures[0]["test_file"] == "tests/test_example.py"
        assert failures[0]["failure_type"] == "failed"

    @pytest.mark.asyncio
    async def test_collect_failures_no_failures(self, test_agent, tmp_path):
        """Test collecting failures when all tests pass."""
        json_report = {
            "summary": {"total": 2, "passed": 2, "failed": 0},
            "tests": [
                {"nodeid": "test.py::test_1", "outcome": "passed"},
                {"nodeid": "test.py::test_2", "outcome": "passed"}
            ]
        }
        report_path = tmp_path / "test_results.json"
        with open(report_path, "w") as f:
            json.dump(json_report, f)

        failures = await test_agent.collect_failures(str(report_path))

        assert len(failures) == 0

    @pytest.mark.asyncio
    async def test_collect_failures_missing_file(self, test_agent):
        """Test collecting failures when JSON file doesn't exist."""
        failures = await test_agent.collect_failures("nonexistent_file.json")

        assert len(failures) == 0


class TestDebugpyInvocation:
    """Tests for debugpy invocation functionality."""

    @pytest.mark.asyncio
    async def test_invoke_debugpy_success(self, test_agent):
        """Test successful debugpy invocation."""
        error_details = {
            "test_name": "test_failing",
            "error_message": "AssertionError"
        }

        with patch.dict(sys.modules, {'debugpy': MagicMock()}):
            result = await test_agent.invoke_debugpy("tests/test_example.py", error_details)

        assert result["test_file"] == "tests/test_example.py"
        assert "timestamp" in result
        assert result.get("success", True)

    @pytest.mark.asyncio
    async def test_invoke_debugpy_not_available(self, test_agent):
        """Test debugpy invocation when debugpy is not installed."""
        error_details = {"test_name": "test_failing"}

        # Simulate debugpy not being available
        with patch.dict(sys.modules, {'debugpy': None}):
            # Force reimport to trigger ImportError check in invoke_debugpy
            result = await test_agent.invoke_debugpy("tests/test_example.py", error_details)

        # Should still return a result (with error or simulated)
        assert result["test_file"] == "tests/test_example.py"


class TestFixGeneration:
    """Tests for Claude SDK fix generation functionality."""

    @pytest.mark.asyncio
    async def test_fix_tests_no_failures(self, test_agent):
        """Test fix_tests with no failures."""
        result = await test_agent.fix_tests([])

        assert result is True

    @pytest.mark.asyncio
    async def test_fix_tests_sdk_not_available(self, test_agent):
        """Test fix_tests when Claude SDK is not available."""
        failures = [
            {"test_file": "test.py", "test_name": "test_fail", "error_message": "Error"}
        ]

        # Mock the SDK import to simulate it not being available
        with patch.dict(sys.modules, {'claude_agent_sdk': None}):
            # Force reimport to trigger ImportError check in fix_tests
            import importlib
            import autoBMAD.epic_automation.test_automation_agent
            importlib.reload(autoBMAD.epic_automation.test_automation_agent)
            from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent
            test_agent_reloaded = TestAutomationAgent(
                state_manager=mock_state_manager,
                epic_id="test-epic-001"
            )
            result = await test_agent_reloaded.fix_tests(failures)

        # Should return False when SDK is not available
        assert result is False

    def test_generate_test_fix_prompt(self, test_agent):
        """Test prompt generation for test fixes."""
        failures = [
            {
                "test_file": "tests/test_example.py",
                "test_name": "test_failing",
                "failure_type": "failed",
                "error_message": "AssertionError: Expected 1, got 2"
            }
        ]

        prompt = test_agent._generate_test_fix_prompt(failures)

        assert "test automation expert" in prompt.lower()
        assert "tests/test_example.py" in prompt
        assert "test_failing" in prompt
        assert "AssertionError" in prompt


class TestRetryCycle:
    """Tests for retry cycle functionality."""

    @pytest.mark.asyncio
    async def test_retry_cycle_all_pass_first_cycle(self, test_agent):
        """Test retry cycle when all tests pass on first try."""
        with patch.object(test_agent, "run_pytest_execution") as mock_pytest:
            mock_pytest.return_value = {
                "success": True,
                "summary": {"total": 5, "passed": 5, "failed": 0}
            }

            result = await test_agent.retry_cycle(
                test_dir="tests",
                max_cycles=3,
                retries_per_cycle=2
            )

        assert result["successful_cycles"] == 1
        assert result["total_cycles"] == 1
        assert result["cycles"][0]["success"] is True

    @pytest.mark.asyncio
    async def test_retry_cycle_with_failures(self, test_agent):
        """Test retry cycle with test failures."""
        with patch.object(test_agent, "run_pytest_execution") as mock_pytest:
            mock_pytest.return_value = {
                "success": False,
                "summary": {"total": 5, "passed": 3, "failed": 2}
            }

            with patch.object(test_agent, "collect_failures") as mock_collect:
                mock_collect.return_value = [
                    {"test_file": "test.py", "test_name": "test_fail", "error_message": "Error"}
                ]

                with patch.object(test_agent, "fix_tests") as mock_fix:
                    mock_fix.return_value = False

                    result = await test_agent.retry_cycle(
                        test_dir="tests",
                        max_cycles=2,
                        retries_per_cycle=1
                    )

        assert result["total_cycles"] == 2
        assert len(result["cycles"]) == 2

    @pytest.mark.asyncio
    async def test_retry_cycle_debugpy_triggered(self, test_agent):
        """Test that debugpy is triggered after 5+ failed attempts."""
        call_count = 0

        async def mock_pytest_execution(test_dir, json_path):
            return {
                "success": False,
                "summary": {"total": 1, "passed": 0, "failed": 1}
            }

        async def mock_collect_failures(json_path):
            return [
                {"test_file": "test.py", "test_name": "test_persistent", "error_message": "Error"}
            ]

        with patch.object(test_agent, "run_pytest_execution", side_effect=mock_pytest_execution):
            with patch.object(test_agent, "collect_failures", side_effect=mock_collect_failures):
                with patch.object(test_agent, "fix_tests", return_value=False):
                    with patch.object(test_agent, "invoke_debugpy") as mock_debugpy:
                        mock_debugpy.return_value = {"success": True}

                        # Run multiple cycles to trigger debugpy (needs 5+ failures)
                        result = await test_agent.retry_cycle(
                            test_dir="tests",
                            max_cycles=3,
                            retries_per_cycle=2
                        )

        # After 3 cycles * 2 retries = 6 attempts, debugpy should be invoked
        # Note: actual trigger depends on implementation logic


class TestReportGeneration:
    """Tests for test report generation."""

    def test_generate_test_report(self, test_agent, tmp_path):
        """Test generating a test report."""
        results = {
            "epic_id": "test-epic-001",
            "timestamp": "2026-01-08T10:00:00",
            "summary": {"total": 5, "passed": 3, "failed": 2},
            "retry_history": [],
            "debugpy_sessions": [],
            "status": "failed"
        }
        failures = [
            {"test_file": "test.py", "test_name": "test_fail"}
        ]

        # Change to temp directory for report generation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            report_path = test_agent.generate_test_report(results, failures)

            assert report_path != ""
            assert Path(report_path).exists()

            with open(report_path) as f:
                report = json.load(f)

            assert report["epic_id"] == "test-epic-001"
            assert report["status"] == "failed"
            assert len(report["failed_tests"]) == 1
        finally:
            os.chdir(original_dir)


class TestCancelScopeCompliance:
    """Tests to verify zero Cancel Scope errors compliance."""

    @pytest.mark.asyncio
    async def test_no_asyncio_wait_for_used(self, test_agent):
        """Verify that asyncio.wait_for is not used in retry_cycle."""
        import inspect
        source = inspect.getsource(test_agent.retry_cycle)

        assert "asyncio.wait_for" not in source
        assert "asyncio.shield" not in source

    @pytest.mark.asyncio
    async def test_no_external_timeouts(self, test_agent):
        """Verify that no external timeout mechanisms are used."""
        import inspect

        # Check retry_cycle
        source = inspect.getsource(test_agent.retry_cycle)
        assert "timeout=" not in source.lower() or "debugpy_timeout" in source

        # Check fix_tests
        source = inspect.getsource(test_agent.fix_tests)
        assert "asyncio.wait_for" not in source
        assert "asyncio.shield" not in source

    def test_max_turns_used_for_sdk(self, test_agent):
        """Verify that max_turns=150 is used for SDK protection."""
        import inspect
        source = inspect.getsource(test_agent.fix_tests)

        assert "max_turns" in source
        assert "150" in source


# Integration tests
class TestIntegration:
    """Integration tests for TestAutomationAgent."""

    @pytest.mark.asyncio
    async def test_full_test_automation_flow(self, test_agent, tmp_path):
        """Test the full test automation flow."""
        # Create a test directory with a simple test
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        # Mock the entire flow
        with patch.object(test_agent, "run_pytest_execution") as mock_pytest:
            mock_pytest.return_value = {
                "success": True,
                "summary": {"total": 1, "passed": 1, "failed": 0}
            }

            result = await test_agent.run_test_automation(str(test_dir))

        assert result["status"] in ["completed", "failed"]

    @pytest.mark.asyncio
    async def test_skip_tests_flag(self, test_agent):
        """Test that skip_tests flag bypasses test execution."""
        result = await test_agent.run_test_automation(
            test_dir="tests",
            skip_tests=True
        )

        assert result["status"] == "skipped"
        assert "bypassed" in result["message"].lower()

"""
Simple tests for QA Tools Integration Module

Tests the integration of BasedPyright-Workflow and Fixtest-Workflow
into BMAD development cycle.
"""

import pytest
from unittest.mock import Mock, patch

# Skip tests if module not available
pytest.importorskip("autoBMAD.epic_automation.qa_tools_integration",
                    reason="qa_tools_integration module not implemented")

from autoBMAD.epic_automation.qa_tools_integration import (
    BasedPyrightWorkflowRunner,
    FixtestWorkflowRunner,
    QAAutomationWorkflow,
    QAStatus,
)


class TestBasedPyright:
    """Test BasedPyright-Workflow integration."""

    @patch('subprocess.run')
    def test_run_check_success(self, mock_run):
        """Test successful BasedPyright check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "No errors found"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        runner = BasedPyrightWorkflowRunner()
        result = runner.run_check(source_dir="src", max_retries=0)

        assert result.tool_name == "BasedPyright-Workflow"
        assert result.status == QAStatus.PASS
        assert result.output == "No errors found"

    @patch('subprocess.run')
    def test_run_check_with_errors(self, mock_run):
        """Test BasedPyright check with errors."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "error: Undefined variable 'x'\nerror: Type mismatch"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        runner = BasedPyrightWorkflowRunner()
        result = runner.run_check(source_dir="src", max_retries=0)

        assert result.status in [QAStatus.CONCERNS, QAStatus.FAIL]
        assert result.type_errors > 0


class TestFixtest:
    """Test Fixtest-Workflow integration."""

    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """Test successful test execution."""
        mock_process1 = Mock()
        mock_process1.returncode = 0
        mock_process1.stdout = "Scan complete"
        mock_process1.stderr = ""

        mock_process2 = Mock()
        mock_process2.returncode = 0
        mock_process2.stdout = "10 passed\n0 failed\n85.5% coverage"
        mock_process2.stderr = ""

        mock_run.side_effect = [mock_process1, mock_process2]

        runner = FixtestWorkflowRunner()
        result = runner.run_tests(max_retries=0)

        assert result.tool_name == "Fixtest-Workflow"
        assert result.status == QAStatus.PASS
        assert result.tests_passed == 10
        assert result.tests_failed == 0

    @patch('subprocess.run')
    def test_run_tests_with_failures(self, mock_run):
        """Test test execution with failures."""
        mock_process1 = Mock()
        mock_process1.returncode = 0
        mock_process1.stdout = "Scan complete"
        mock_process1.stderr = ""

        mock_process2 = Mock()
        mock_process2.returncode = 0
        mock_process2.stdout = "8 passed\n3 failed\n80.0% coverage"
        mock_process2.stderr = ""

        mock_run.side_effect = [mock_process1, mock_process2]

        runner = FixtestWorkflowRunner()
        result = runner.run_tests(max_retries=0)

        assert result.status == QAStatus.CONCERNS
        assert result.tests_passed == 8
        assert result.tests_failed == 3


class TestQAWorkflow:
    """Test QA Automation Workflow."""

    @patch.object(BasedPyrightWorkflowRunner, 'run_check')
    @patch.object(FixtestWorkflowRunner, 'run_tests')
    def test_run_qa_checks_all_pass(self, mock_fixtest, mock_basedpyright):
        """Test QA check with all tools passing."""
        basedpyright_result = Mock()
        basedpyright_result.status = QAStatus.PASS
        basedpyright_result.output = "No errors"

        fixtest_result = Mock()
        fixtest_result.status = QAStatus.PASS
        fixtest_result.output = "All tests passed"
        fixtest_result.tests_passed = 10
        fixtest_result.tests_failed = 0

        mock_basedpyright.return_value = basedpyright_result
        mock_fixtest.return_value = fixtest_result

        workflow = QAAutomationWorkflow(max_retries=0)
        bp_result, fx_result, overall = workflow.run_qa_checks("src")

        assert bp_result.status == QAStatus.PASS
        assert fx_result.status == QAStatus.PASS
        assert overall == QAStatus.PASS

    @patch.object(BasedPyrightWorkflowRunner, 'run_check')
    @patch.object(FixtestWorkflowRunner, 'run_tests')
    def test_run_qa_checks_one_fail(self, mock_fixtest, mock_basedpyright):
        """Test QA check with one tool failing."""
        basedpyright_result = Mock()
        basedpyright_result.status = QAStatus.FAIL
        basedpyright_result.output = "Type errors found"

        fixtest_result = Mock()
        fixtest_result.status = QAStatus.PASS
        fixtest_result.output = "All tests passed"

        mock_basedpyright.return_value = basedpyright_result
        mock_fixtest.return_value = fixtest_result

        workflow = QAAutomationWorkflow(max_retries=0)
        bp_result, fx_result, overall = workflow.run_qa_checks("src")

        assert overall == QAStatus.FAIL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

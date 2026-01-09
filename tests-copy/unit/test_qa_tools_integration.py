"""
Unit tests for QA Tools Integration module.
"""

from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.qa_tools_integration import (
    QAStatus, QAError, BasedPyrightWorkflowRunner,
    FixtestWorkflowRunner, QAAutomationWorkflow
)


class TestQAStatus:
    """Test QAStatus enum."""

    def test_enum_values(self):
        """Test QAStatus enum values."""
        assert QAStatus.PASS.value == "PASS"
        assert QAStatus.CONCERNS.value == "CONCERNS"
        assert QAStatus.FAIL.value == "FAIL"
        assert QAStatus.WAIVED.value == "WAIVED"


class TestQAError:
    """Test QAError class."""

    def test_init(self):
        """Test QAError initialization."""
        error = QAError("Test error", "ERROR_CODE")
        assert error.message == "Test error"
        assert error.code == "ERROR_CODE"


class TestBasedPyrightWorkflowRunner:
    """Test BasedPyrightWorkflowRunner class."""

    def test_init(self):
        """Test initialization."""
        runner = BasedPyrightWorkflowRunner("/test/dir")
        assert runner.basedpyright_dir == "/test/dir"

    @pytest.mark.asyncio
    async def test_run(self):
        """Test running basedpyright."""
        runner = BasedPyrightWorkflowRunner("/test/dir")

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = await runner.run()

            assert isinstance(result, dict)
            mock_run.assert_called()

    @pytest.mark.asyncio
    async def test_run_with_errors(self):
        """Test running with errors."""
        runner = BasedPyrightWorkflowRunner("/test/dir")

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            result = await runner.run()

            assert isinstance(result, dict)
            assert "errors" in result


class TestFixtestWorkflowRunner:
    """Test FixtestWorkflowRunner class."""

    def test_init(self):
        """Test initialization."""
        runner = FixtestWorkflowRunner("/test/dir")
        assert runner.fixtest_dir == "/test/dir"

    @pytest.mark.asyncio
    async def test_run(self):
        """Test running fixtest."""
        runner = FixtestWorkflowRunner("/test/dir")

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = await runner.run()

            assert isinstance(result, dict)
            mock_run.assert_called()

    @pytest.mark.asyncio
    async def test_run_fails(self):
        """Test running fails."""
        runner = FixtestWorkflowRunner("/test/dir")

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            result = await runner.run()

            assert isinstance(result, dict)
            assert "failed" in result


class TestQAAutomationWorkflow:
    """Test QAAutomationWorkflow class."""

    def test_init(self):
        """Test initialization."""
        workflow = QAAutomationWorkflow(
            basedpyright_dir="/test/basedpyright",
            fixtest_dir="/test/fixtest"
        )
        assert workflow.basedpyright_dir == "/test/basedpyright"
        assert workflow.fixtest_dir == "/test/fixtest"

    @pytest.mark.asyncio
    async def test_run_qa_checks(self):
        """Test running QA checks."""
        workflow = QAAutomationWorkflow(
            basedpyright_dir="/test/basedpyright",
            fixtest_dir="/test/fixtest"
        )

        result = await workflow.run_qa_checks(
            source_dir="/test/src",
            test_dir="/test/tests"
        )

        assert isinstance(result, dict)
        assert "overall_status" in result
        assert "basedpyright" in result
        assert "fixtest" in result

    @pytest.mark.asyncio
    async def test_run_qa_checks_with_timeout(self):
        """Test running QA checks with timeout."""
        workflow = QAAutomationWorkflow(
            basedpyright_dir="/test/basedpyright",
            fixtest_dir="/test/fixtest",
            timeout=600
        )

        result = await workflow.run_qa_checks(
            source_dir="/test/src",
            test_dir="/test/tests"
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_run_qa_checks_with_retries(self):
        """Test running QA checks with retries."""
        workflow = QAAutomationWorkflow(
            basedpyright_dir="/test/basedpyright",
            fixtest_dir="/test/fixtest",
            max_retries=5
        )

        result = await workflow.run_qa_checks(
            source_dir="/test/src",
            test_dir="/test/tests"
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_run_qa_checks_multiple_sources(self):
        """Test running QA checks on multiple source directories."""
        workflow = QAAutomationWorkflow(
            basedpyright_dir="/test/basedpyright",
            fixtest_dir="/test/fixtest"
        )

        # Run on multiple directories
        results = await asyncio.gather(*[
            workflow.run_qa_checks(f"/test/src{i}", "/test/tests")
            for i in range(3)
        ])

        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)

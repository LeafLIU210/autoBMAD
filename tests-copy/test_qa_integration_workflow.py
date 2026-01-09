"""
Integration tests for QA Tools Workflow

Tests the complete integration of QA tools with BMAD workflow,
including PowerShell script execution and story file updates.
"""

import pytest
import subprocess
from unittest.mock import patch, Mock

from autoBMAD.epic_automation.qa_tools_integration import QAAutomationWorkflow, QAStatus


class TestQAIntegrationWorkflow:
    """Test complete QA integration workflow."""

    def test_qa_workflow_integration(self, tmp_path):
        """Test complete QA workflow integration."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("""# Test Story

**Status**: Draft

## Acceptance Criteria

- [ ] QA Tools Integration

## Tasks / Subtasks

- [ ] Task 1: Implement integration
""")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        # Initialize QA workflow
        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir,
            max_retries=1
        )

        # Run QA checks (with mocked subprocess calls)
        with patch('subprocess.run') as mock_run:
            # Mock BasedPyright success
            mock_bp_process = Mock()
            mock_bp_process.returncode = 0
            mock_bp_process.stdout = "No errors found"
            mock_bp_process.stderr = ""

            # Mock Fixtest success (needs 2 commands)
            mock_ft_process1 = Mock()
            mock_ft_process1.returncode = 0
            mock_ft_process1.stdout = "Scan complete"
            mock_ft_process1.stderr = ""

            mock_ft_process2 = Mock()
            mock_ft_process2.returncode = 0
            mock_ft_process2.stdout = "10 passed\n0 failed\n90.0% coverage"
            mock_ft_process2.stderr = ""

            mock_run.side_effect = [mock_bp_process, mock_ft_process1, mock_ft_process2]

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Verify results
            assert bp_result.status == QAStatus.PASS
            assert ft_result.status == QAStatus.PASS
            assert overall == QAStatus.PASS

        # Update story file
        success = workflow.update_story_status(
            story_path,
            bp_result,
            ft_result,
            overall
        )

        assert success

        # Verify story file was updated
        content = story_path.read_text()
        assert "## QA Results" in content
        assert "PASS" in content

    def test_qa_workflow_with_failures(self, tmp_path):
        """Test QA workflow with tool failures."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir,
            max_retries=1
        )

        # Run QA checks with failures
        with patch('subprocess.run') as mock_run:
            # Mock BasedPyright failure
            mock_bp_process = Mock()
            mock_bp_process.returncode = 1
            mock_bp_process.stdout = ""
            mock_bp_process.stderr = "Type errors: 15"

            # Mock Fixtest failure
            mock_ft_process = Mock()
            mock_ft_process.returncode = 1
            mock_ft_process.stdout = "5 passed\n5 failed"
            mock_ft_process.stderr = ""

            mock_run.side_effect = [mock_bp_process, mock_ft_process]

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Verify overall status is FAIL
            assert overall == QAStatus.FAIL

    def test_qa_workflow_with_concerns(self, tmp_path):
        """Test QA workflow with concerns."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir,
            max_retries=1
        )

        # Run QA checks with concerns
        with patch('subprocess.run') as mock_run:
            # Mock BasedPyright with concerns
            mock_bp_process = Mock()
            mock_bp_process.returncode = 0
            mock_bp_process.stdout = "error: Minor type issue"
            mock_bp_process.stderr = ""

            # Mock Fixtest with minor failures
            mock_ft_process = Mock()
            mock_ft_process.returncode = 0
            mock_ft_process.stdout = "8 passed\n2 failed\n85.0% coverage"
            mock_ft_process.stderr = ""

            mock_run.side_effect = [mock_bp_process, mock_ft_process]

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Verify overall status
            assert overall in [QAStatus.CONCERNS, QAStatus.FAIL]

    def test_qa_workflow_retry_mechanism(self, tmp_path):
        """Test retry mechanism in QA workflow."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir,
            max_retries=2
        )

        # Run QA checks with retry
        with patch('subprocess.run') as mock_run:
            # First BasedPyright fails, second succeeds
            mock_bp_fail = Mock()
            mock_bp_fail.returncode = 1
            mock_bp_fail.stdout = ""
            mock_bp_fail.stderr = "Error"

            mock_bp_success = Mock()
            mock_bp_success.returncode = 0
            mock_bp_success.stdout = "No errors"
            mock_bp_success.stderr = ""

            # Fixtest always succeeds
            mock_ft = Mock()
            mock_ft.returncode = 0
            mock_ft.stdout = "10 passed\n0 failed"
            mock_ft.stderr = ""

            # First BasedPyright fails, then succeeds
            mock_run.side_effect = [mock_bp_fail, mock_bp_success, mock_ft]

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Should have retried and eventually passed
            assert bp_result.status == QAStatus.PASS
            assert mock_run.call_count == 3  # 2 for BasedPyright, 1 for Fixtest

    def test_qa_workflow_timeout_handling(self, tmp_path):
        """Test timeout handling in QA workflow."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir,
            max_retries=0
        )

        # Run QA checks with timeout
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("test", 300)

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Should handle timeout gracefully
            assert bp_result.status == QAStatus.FAIL
            assert "Timeout" in bp_result.output

    def test_qa_report_generation(self, tmp_path):
        """Test QA report generation."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir
        )

        # Run QA checks with mocked results
        with patch('subprocess.run') as mock_run:
            mock_bp = Mock()
            mock_bp.returncode = 0
            mock_bp.stdout = "No errors"
            mock_bp.stderr = ""

            mock_ft = Mock()
            mock_ft.returncode = 0
            mock_ft.stdout = "10 passed\n0 failed\n90.0% coverage"
            mock_ft.stderr = ""

            mock_run.side_effect = [mock_bp, mock_ft]

            bp_result, ft_result, overall = workflow.run_qa_checks(
                source_dir="src",
                story_path=story_path
            )

            # Generate report
            report = workflow.generate_qa_report(bp_result, ft_result, overall)

            # Verify report content
            assert "# QA Automation Report" in report
            assert "BasedPyright-Workflow Results" in report
            assert "Fixtest-Workflow Results" in report
            assert "PASS" in report
            assert "BasedPyright" in report
            assert "Fixtest" in report

    def test_story_file_not_found(self, tmp_path):
        """Test handling when story file doesn't exist."""
        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        workflow = QAAutomationWorkflow(
            basedpyright_dir=basedpyright_dir,
            fixtest_dir=fixtest_dir
        )

        # Try to update non-existent story file
        non_existent_path = tmp_path / "nonexistent.md"
        bp_result = Mock()
        ft_result = Mock()
        bp_result.status = QAStatus.PASS
        ft_result.status = QAStatus.PASS

        success = workflow.update_story_status(
            non_existent_path,
            bp_result,
            ft_result,
            QAStatus.PASS
        )

        assert not success

    def test_qa_workflow_max_retries(self, tmp_path):
        """Test that max retries is properly configured."""
        # Create temporary story file
        story_path = tmp_path / "test_story.md"
        story_path.write_text("# Test Story\n\n**Status**: Draft\n")

        # Create mock workflow directories
        basedpyright_dir = tmp_path / "basedpyright-workflow"
        fixtest_dir = tmp_path / "fixtest-workflow"
        basedpyright_dir.mkdir(exist_ok=True)
        fixtest_dir.mkdir(exist_ok=True)

        # Test with different retry counts
        for retries in [0, 1, 2, 5]:
            workflow = QAAutomationWorkflow(
                basedpyright_dir=basedpyright_dir,
                fixtest_dir=fixtest_dir,
                max_retries=retries
            )
            assert workflow.max_retries == retries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

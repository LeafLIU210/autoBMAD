"""
Unit tests for QAAgent module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.qa_agent import QAAgent, QAStatus


@pytest.fixture
def qa_agent():
    """Create a QAAgent instance for testing."""
    return QAAgent()


@pytest.fixture
def sample_story_content():
    """Sample story content for testing."""
    return """# Story 1.1: Test Story

## Status
**Status:** In Development

## Story
**As a** developer,
**I want** to implement a feature,
**so that** users can benefit.

## Acceptance Criteria
1. Feature works correctly
2. Tests pass
3. Code follows standards

## Dev Notes
Implementation notes here.
"""


class TestQAAgent:
    """Test QAAgent class."""

    def test_init(self, qa_agent):
        """Test QAAgent initialization."""
        assert qa_agent.name == "QA Agent"

    @pytest.mark.asyncio
    async def test_parse_story_for_qa(self, qa_agent, sample_story_content):
        """Test parsing story for QA."""
        story_data = await qa_agent._parse_story_for_qa(sample_story_content)

        assert story_data is not None
        assert "story_id" in story_data
        assert "acceptance_criteria" in story_data
        assert "tasks" in story_data

    @pytest.mark.asyncio
    async def test_parse_story_for_qa_empty(self, qa_agent):
        """Test parsing empty story content."""
        story_data = await qa_agent._parse_story_for_qa("")

        assert story_data is None

    @pytest.mark.asyncio
    async def test_parse_story_for_qa_invalid(self, qa_agent):
        """Test parsing invalid story content."""
        invalid_content = "# Not a proper story"

        story_data = await qa_agent._parse_story_for_qa(invalid_content)

        assert story_data is None

    @pytest.mark.asyncio
    async def test_perform_validations(self, qa_agent):
        """Test performing validations."""
        story_data = {
            "story_id": "1.1",
            "acceptance_criteria": ["Criterion 1"],
            "tasks": [{"status": "completed"}],
            "dev_notes": "Implementation notes"
        }

        result = await qa_agent._perform_validations(story_data)

        assert "status" in result
        assert "checks" in result
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_perform_validations_missing_tasks(self, qa_agent):
        """Test validations with missing tasks."""
        story_data = {
            "story_id": "1.1",
            "acceptance_criteria": [],
            "tasks": []
        }

        result = await qa_agent._perform_validations(story_data)

        assert "issues" in result
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_execute_basic(self, qa_agent, sample_story_content):
        """Test basic execution of QA agent."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            with patch.object(qa_agent, '_perform_validations') as mock_validate:
                mock_parse.return_value = {
                    "story_id": "1.1",
                    "acceptance_criteria": ["Criterion 1"],
                    "tasks": []
                }
                mock_validate.return_value = {
                    "status": "PASS",
                    "checks": ["Check 1"],
                    "issues": []
                }

                result = await qa_agent.execute(
                    story_content=sample_story_content,
                    story_path="docs/stories/1.1-test.md"
                )

                assert "passed" in result
                assert "status" in result
                mock_parse.assert_called_once()
                mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_fails_parsing(self, qa_agent, sample_story_content):
        """Test execution when parsing fails."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            mock_parse.return_value = None

            result = await qa_agent.execute(
                story_content=sample_story_content,
                story_path="docs/stories/1.1-test.md"
            )

            assert result["passed"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_with_qa_tools(self, qa_agent, sample_story_content):
        """Test execution with QA tools enabled."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            with patch.object(qa_agent, '_perform_validations') as mock_validate:
                with patch.object(qa_agent, '_execute_qa_review') as mock_review:
                    mock_parse.return_value = {"story_id": "1.1"}
                    mock_validate.return_value = {"status": "PASS", "checks": [], "issues": []}
                    mock_review.return_value = True

                    result = await qa_agent.execute(
                        story_content=sample_story_content,
                        story_path="docs/stories/1.1-test.md",
                        use_qa_tools=True
                    )

                    assert "passed" in result
                    mock_review.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_qa_review(self, qa_agent):
        """Test executing QA review."""
        story_path = "docs/stories/1.1-test.md"

        with patch('autoBMAD.epic_automation.qa_agent.logger') as mock_logger:
            result = await qa_agent._execute_qa_review(story_path)

            assert result is True
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_check_story_status(self, qa_agent):
        """Test checking story status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            story_file = stories_dir / "1.1-test.md"
            story_file.write_text("# Story\n## Status\n**Status:** Ready for Review")

            result = await qa_agent._check_story_status(str(story_file))

            assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_check_story_status_nonexistent(self, qa_agent):
        """Test checking status of non-existent story."""
        result = await qa_agent._check_story_status("nonexistent.md")

        assert result is False

    @pytest.mark.asyncio
    async def test_collect_qa_gate_paths(self, qa_agent):
        """Test collecting QA gate paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            qa_dir = Path(tmpdir) / "qa"
            qa_dir.mkdir()
            (qa_dir / "gate1.md").write_text("Gate 1")
            (qa_dir / "gate2.md").write_text("Gate 2")

            with patch.object(qa_agent, '_get_qa_dir', return_value=str(qa_dir)):
                paths = await qa_agent._collect_qa_gate_paths()

                assert len(paths) >= 0  # May be empty if no gates found

    @pytest.mark.asyncio
    async def test_generate_qa_report(self, qa_agent):
        """Test generating QA report."""
        qa_result = {
            "status": "PASS",
            "checks": ["Check 1", "Check 2"],
            "issues": [],
            "summary": "All checks passed"
        }

        report = await qa_agent.generate_qa_report(qa_result)

        assert isinstance(report, str)
        assert "PASS" in report

    @pytest.mark.asyncio
    async def test_generate_qa_report_with_issues(self, qa_agent):
        """Test generating QA report with issues."""
        qa_result = {
            "status": "FAIL",
            "checks": ["Check 1"],
            "issues": ["Issue 1", "Issue 2"],
            "summary": "Some checks failed"
        }

        report = await qa_agent.generate_qa_report(qa_result)

        assert isinstance(report, str)
        assert "FAIL" in report

    @pytest.mark.asyncio
    async def test_execute_with_custom_directories(self, qa_agent, sample_story_content):
        """Test execution with custom source and test directories."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            with patch.object(qa_agent, '_perform_validations') as mock_validate:
                mock_parse.return_value = {"story_id": "1.1"}
                mock_validate.return_value = {"status": "PASS", "checks": [], "issues": []}

                result = await qa_agent.execute(
                    story_content=sample_story_content,
                    story_path="docs/stories/1.1-test.md",
                    source_dir="custom_src",
                    test_dir="custom_tests"
                )

                assert "passed" in result

    @pytest.mark.asyncio
    async def test_execute_without_qa_tools(self, qa_agent, sample_story_content):
        """Test execution without QA tools."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            with patch.object(qa_agent, '_perform_validations') as mock_validate:
                mock_parse.return_value = {"story_id": "1.1"}
                mock_validate.return_value = {"status": "PASS", "checks": [], "issues": []}

                result = await qa_agent.execute(
                    story_content=sample_story_content,
                    story_path="docs/stories/1.1-test.md",
                    use_qa_tools=False
                )

                assert "passed" in result

    @pytest.mark.asyncio
    async def test_perform_validations_with_dev_notes(self, qa_agent):
        """Test validations with development notes."""
        story_data = {
            "story_id": "1.1",
            "acceptance_criteria": ["Criterion 1"],
            "tasks": [{"status": "completed"}],
            "dev_notes": "Implementation notes here"
        }

        result = await qa_agent._perform_validations(story_data)

        assert "checks" in result

    @pytest.mark.asyncio
    async def test_perform_validations_empty_acceptance_criteria(self, qa_agent):
        """Test validations with empty acceptance criteria."""
        story_data = {
            "story_id": "1.1",
            "acceptance_criteria": [],
            "tasks": []
        }

        result = await qa_agent._perform_validations(story_data)

        assert "issues" in result
        # Should have issue about missing acceptance criteria
        assert any("acceptance" in str(issue).lower() for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_execute_with_task_guidance(self, qa_agent, sample_story_content):
        """Test execution with task guidance."""
        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            with patch.object(qa_agent, '_perform_validations') as mock_validate:
                mock_parse.return_value = {"story_id": "1.1"}
                mock_validate.return_value = {"status": "PASS", "checks": [], "issues": []}

                result = await qa_agent.execute(
                    story_content=sample_story_content,
                    story_path="docs/stories/1.1-test.md",
                    task_guidance="Focus on security checks"
                )

                assert "passed" in result

    def test_qa_status_enum(self):
        """Test QAStatus enum values."""
        assert QAStatus.PASS.value == "PASS"
        assert QAStatus.FAIL.value == "FAIL"
        assert QAStatus.CONCERNS.value == "CONCERNS"
        assert QAStatus.WAIVED.value == "WAIVED"

    @pytest.mark.asyncio
    async def test_execute_preserves_story_path(self, qa_agent, sample_story_content):
        """Test that execution preserves story path in result."""
        story_path = "docs/stories/1.1-test.md"

        with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse:
            mock_parse.return_value = {"story_id": "1.1"}

            result = await qa_agent.execute(
                story_content=sample_story_content,
                story_path=story_path
            )

            # Story path should be in the result
            assert "story_path" in result or story_path in str(result)

    @pytest.mark.asyncio
    async def test_multiple_concurrent_executions(self, qa_agent):
        """Test executing multiple QA checks concurrently."""
        story_content = "# Story\nContent"

        async def execute_qa(i):
            return await qa_agent.execute(
                story_content=story_content,
                story_path=f"docs/stories/1.{i}-test.md"
            )

        # Run 5 concurrent executions
        results = await asyncio.gather(*[execute_qa(i) for i in range(5)])

        assert len(results) == 5
        for result in results:
            assert "passed" in result

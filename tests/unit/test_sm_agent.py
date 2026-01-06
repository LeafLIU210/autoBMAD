"""
Unit tests for SMAgent module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.sm_agent import SMAgent


@pytest.fixture
def sm_agent():
    """Create an SMAgent instance for testing."""
    return SMAgent(
        project_root="/test/project",
        tasks_path="/test/tasks",
        config={"test": True}
    )


@pytest.fixture
def sample_story_content():
    """Sample story content for testing."""
    return """# Story 1.1: Test Story

## Status
**Status:** Ready for Development

## Story
**As a** developer,
**I want** to test the system,
**so that** we can verify functionality.

## Acceptance Criteria
1. First criterion
2. Second criterion

## Tasks / Subtasks
- [ ] Task 1
- [ ] Task 2

## Dev Notes
Test notes
"""


class TestSMAgent:
    """Test SMAgent class."""

    def test_init_default(self):
        """Test SMAgent initialization with defaults."""
        agent = SMAgent()

        assert agent.name == "SM Agent"
        assert agent.agent_name == "SM Agent"
        assert agent.phase == "Story Management"
        assert agent.project_root is None
        assert agent.tasks_path is None
        assert agent.config == {}

    def test_init_with_params(self, sm_agent):
        """Test SMAgent initialization with parameters."""
        assert sm_agent.project_root == Path("/test/project")
        assert sm_agent.tasks_path == Path("/test/tasks")
        assert sm_agent.config == {"test": True}

    def test_find_story_file_preferred_format(self, sm_agent):
        """Test finding story file with preferred format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file with preferred format
            (stories_dir / "1.1-test-description.md").write_text("content")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            assert result == stories_dir / "1.1-test-description.md"

    def test_find_story_file_dot_format(self, sm_agent):
        """Test finding story file with dot format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file with dot format
            (stories_dir / "1.1.test.description.md").write_text("content")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            assert result == stories_dir / "1.1.test.description.md"

    def test_find_story_file_story_dash_format(self, sm_agent):
        """Test finding story file with story-dash format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file with story-dash format
            (stories_dir / "story-1-1-description.md").write_text("content")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            assert result == stories_dir / "story-1-1-description.md"

    def test_find_story_file_story_dot_format(self, sm_agent):
        """Test finding story file with story-dot format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file with story-dot format
            (stories_dir / "story-1.1-description.md").write_text("content")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            assert result == stories_dir / "story-1.1-description.md"

    def test_find_story_file_loose_match(self, sm_agent):
        """Test finding story file with loose match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file with loose match
            (stories_dir / "custom-1.1-file.md").write_text("content")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            assert result == stories_dir / "custom-1.1-file.md"

    def test_find_story_file_not_found(self, sm_agent):
        """Test finding story file when none exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)

            result = sm_agent._find_story_file(stories_dir, "9.9")

            assert result is None

    def test_find_story_file_priority(self, sm_agent):
        """Test that preferred format has priority."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create multiple files that could match
            (stories_dir / "1.1-test.md").write_text("preferred")
            (stories_dir / "1.1.other.md").write_text("dot format")
            (stories_dir / "story-1-1-test.md").write_text("dash format")

            result = sm_agent._find_story_file(stories_dir, "1.1")

            # Should pick the first matching preferred format
            assert result == stories_dir / "1.1-test.md"

    @pytest.mark.asyncio
    async def test_parse_story_metadata(self, sm_agent, sample_story_content):
        """Test parsing story metadata."""
        metadata = await sm_agent._parse_story_metadata(sample_story_content)

        assert metadata is not None
        assert "1.1" in metadata.get("story_id", "")

    @pytest.mark.asyncio
    async def test_parse_story_metadata_invalid(self, sm_agent):
        """Test parsing invalid story metadata."""
        invalid_content = "# Not a proper story"

        metadata = await sm_agent._parse_story_metadata(invalid_content)

        assert metadata is None

    @pytest.mark.asyncio
    async def test_validate_story_structure(self, sm_agent):
        """Test validating story structure."""
        story_data = {
            "story_id": "1.1",
            "title": "Test Story",
            "status": "Ready for Development",
            "acceptance_criteria": ["Criterion 1", "Criterion 2"]
        }

        result = await sm_agent._validate_story_structure(story_data)

        assert result["valid"] is True
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_validate_story_structure_invalid(self, sm_agent):
        """Test validating invalid story structure."""
        story_data = {
            "story_id": "",
            "title": "",
            "status": ""
        }

        result = await sm_agent._validate_story_structure(story_data)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_apply_task_guidance(self, sm_agent):
        """Test applying task guidance."""
        story_content = "# Story\n## Tasks\n- [ ] Task 1"
        guidance = "Add more details to tasks"

        result = await sm_agent._apply_task_guidance(story_content, guidance)

        assert result is not None
        assert isinstance(result, str)

    def test_extract_story_ids_from_epic(self, sm_agent):
        """Test extracting story IDs from epic."""
        epic_content = """
        # Epic 1

        ## Story 1.1
        Content

        ## Story 1.2
        Content

        ## Story 2.1
        Content
        """

        ids = sm_agent._extract_story_ids_from_epic(epic_content)

        assert "1.1" in ids
        assert "1.2" in ids
        assert "2.1" in ids

    def test_extract_story_ids_from_epic_no_stories(self, sm_agent):
        """Test extracting story IDs when none exist."""
        epic_content = "# Epic 1\n\nNo stories here"

        ids = sm_agent._extract_story_ids_from_epic(epic_content)

        assert len(ids) == 0

    def test_build_claude_prompt(self, sm_agent):
        """Test building Claude prompt."""
        epic_path = "/test/epic.md"
        story_ids = ["1.1", "1.2"]

        prompt = sm_agent._build_claude_prompt(epic_path, story_ids)

        assert "/test/epic.md" in prompt
        assert "1.1" in prompt
        assert "1.2" in prompt

    @pytest.mark.asyncio
    async def test_execute_basic(self, sm_agent, sample_story_content):
        """Test basic execution of SM agent."""
        # Mock the internal methods
        with patch.object(sm_agent, '_parse_story_metadata') as mock_parse:
            with patch.object(sm_agent, '_validate_story_structure') as mock_validate:
                with patch.object(sm_agent, '_apply_task_guidance') as mock_apply:
                    mock_parse.return_value = {"story_id": "1.1", "title": "Test"}
                    mock_validate.return_value = {"valid": True, "errors": []}
                    mock_apply.return_value = sample_story_content

                    result = await sm_agent.execute(
                        story_content=sample_story_content,
                        task_guidance="Test guidance",
                        story_path="docs/stories/1.1-test.md"
                    )

                    assert result is True
                    mock_parse.assert_called_once()
                    mock_validate.assert_called_once()
                    mock_apply.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_invalid_metadata(self, sm_agent, sample_story_content):
        """Test execution with invalid metadata."""
        with patch.object(sm_agent, '_parse_story_metadata') as mock_parse:
            mock_parse.return_value = None

            result = await sm_agent.execute(
                story_content=sample_story_content,
                task_guidance="Test guidance",
                story_path="docs/stories/1.1-test.md"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_execute_invalid_structure(self, sm_agent, sample_story_content):
        """Test execution with invalid structure."""
        with patch.object(sm_agent, '_parse_story_metadata') as mock_parse:
            with patch.object(sm_agent, '_validate_story_structure') as mock_validate:
                mock_parse.return_value = {"story_id": "1.1"}
                mock_validate.return_value = {"valid": False, "errors": ["Error 1"]}

                result = await sm_agent.execute(
                    story_content=sample_story_content,
                    task_guidance="Test guidance",
                    story_path="docs/stories/1.1-test.md"
                )

                assert result is False

    @pytest.mark.asyncio
    async def test_create_story(self, sm_agent):
        """Test creating a new story."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            story_content = "# Story 1.1\n\nTest content"

            with patch.object(sm_agent, 'project_root', stories_dir):
                result = await sm_agent.create_story("1.1", "Test Story", "Test content")

                # Verify file was created
                story_file = stories_dir / "docs" / "stories" / "1.1-test-story.md"
                assert story_file.exists()
                assert story_file.read_text() == story_content

    @pytest.mark.asyncio
    async def test_create_stories_from_epic(self, sm_agent):
        """Test creating stories from epic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            epic_path = Path(tmpdir) / "test_epic.md"
            epic_path.write_text("""
# Epic 1

## Story 1.1
Content

## Story 1.2
Content
""")

            with patch.object(sm_agent, '_call_claude_create_stories') as mock_create:
                mock_create.return_value = True

                result = await sm_agent.create_stories_from_epic(str(epic_path))

                assert result is True
                mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_story_files(self, sm_agent):
        """Test verifying story files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story file
            (stories_dir / "1.1-test.md").write_text("content")

            valid, invalid = sm_agent._verify_story_files(["1.1"], "/test/epic.md")

            assert valid == ["1.1"]
            assert invalid == []

    @pytest.mark.asyncio
    async def test_verify_story_files_missing(self, sm_agent):
        """Test verifying story files when some are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Only create one file
            (stories_dir / "1.1-test.md").write_text("content")

            valid, invalid = sm_agent._verify_story_files(["1.1", "1.2"], "/test/epic.md")

            assert valid == ["1.1"]
            assert invalid == ["1.2"]

    @pytest.mark.asyncio
    async def test_update_story_statuses(self, sm_agent):
        """Test updating story statuses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)
            # Create story files
            (stories_dir / "1.1-test.md").write_text("# Story 1.1\n## Status\n**Status:** Draft")
            (stories_dir / "1.2-test.md").write_text("# Story 1.2\n## Status\n**Status:** Draft")

            await sm_agent._update_story_statuses(["1.1", "1.2"], stories_dir)

            # Verify status was updated
            content1 = (stories_dir / "1.1-test.md").read_text()
            assert "Ready for Development" in content1

    @pytest.mark.asyncio
    async def test_check_existing_stories(self, sm_agent):
        """Test checking for existing stories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir) / "docs" / "stories"
            stories_dir.mkdir(parents=True)
            # Create existing story
            (stories_dir / "1.1-test.md").write_text("content")

            result = await sm_agent._check_existing_stories("/test/epic.md", ["1.1", "1.2"])

            assert result is True  # Found existing stories

    @pytest.mark.asyncio
    async def test_check_existing_stories_none(self, sm_agent):
        """Test checking when no existing stories."""
        result = await sm_agent._check_existing_stories("/test/epic.md", ["9.9"])

        assert result is False  # No existing stories

    @pytest.mark.asyncio
    async def test_execute_with_logging(self, sm_agent):
        """Test execution with proper logging."""
        with patch('autoBMAD.epic_automation.sm_agent.logger') as mock_logger:
            with patch.object(sm_agent, '_parse_story_metadata') as mock_parse:
                mock_parse.return_value = {"story_id": "1.1"}

                await sm_agent.execute("content")

                # Verify logging was called
                assert mock_logger.info.called

    def test_agent_name_consistency(self, sm_agent):
        """Test that agent name is consistent."""
        assert sm_agent.name == sm_agent.agent_name
        assert sm_agent.phase == "Story Management"

    @pytest.mark.asyncio
    async def test_create_story_with_special_characters(self, sm_agent):
        """Test creating story with special characters in title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stories_dir = Path(tmpdir)

            with patch.object(sm_agent, 'project_root', stories_dir):
                await sm_agent.create_story("1.1", "Test Story & More!", "Content")

                # Verify file was created with sanitized name
                files = list(stories_dir.glob("docs/stories/1.1-*.md"))
                assert len(files) == 1

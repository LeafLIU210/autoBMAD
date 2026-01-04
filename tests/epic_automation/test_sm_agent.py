"""
Tests for SMAgent class.

Tests the Story Management agent functionality including:
- Story preparation
- Task breakdown generation
- Technical context creation
- Story file creation
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from autoBMAD.epic_automation.sm_agent import SMAgent


class TestSMAgent:
    """Test cases for SMAgent"""

    @pytest.fixture
    def sample_task_guidance(self):
        """Sample task guidance content"""
        return """# Create Next Story Task

## Purpose
To identify the next logical story based on project progress.

## Task Execution
1. Identify next story
2. Gather requirements
3. Populate story template
"""

    @pytest.fixture
    def sm_agent(self, sample_task_guidance):
        """Create an SMAgent instance for testing"""
        return SMAgent(
            project_root="/test/root",
            tasks_path="/test/tasks",
            config={}
        )

    @pytest.fixture
    def sample_story(self):
        """Sample story object"""
        from dataclasses import dataclass

        @dataclass
        class Story:
            epic_num: int = 1
            story_num: int = 1
            title: str = "Test Story"
            path: str = "/test/story.md"
            status: str = "Draft"

        return Story()

    def test_init(self, sm_agent):
        """Test successful initialization"""
        assert sm_agent is not None
        assert sm_agent.project_root == Path("/test/root")
        assert sm_agent.tasks_path == Path("/test/tasks")
        assert sm_agent.agent_name == "SM Agent"
        assert sm_agent.phase == "Story Management"

    @pytest.mark.asyncio
    async def test_execute_success(self, sm_agent, sample_story, sample_task_guidance):
        """Test successful story management execution"""
        result = await sm_agent.execute(sample_story, sample_task_guidance)

        assert result[0] is True
        assert "SM phase completed" in result[1]

    @pytest.mark.asyncio
    async def test_execute_with_exception(self, sm_agent, sample_story):
        """Test handling of exceptions during execution"""
        # Mock to raise an exception
        with patch.object(sm_agent, 'project_root', None):
            result = await sm_agent.execute(sample_story, "")

            assert result[0] is False
            assert len(result[1]) > 0

    def test_parse_story_requirements(self, sm_agent, sample_story):
        """Test parsing story requirements"""
        # This would test the internal _parse_story_requirements method
        # if it were exposed or testable
        pass

    def test_generate_task_breakdown(self, sm_agent, sample_story):
        """Test generating task breakdown"""
        # This would test the internal _generate_task_breakdown method
        # if it were exposed or testable
        pass

    def test_generate_technical_context(self, sm_agent, sample_story):
        """Test generating technical context"""
        # This would test the internal _generate_technical_context method
        # if it were exposed or testable
        pass

    @pytest.mark.asyncio
    async def test_execute_with_empty_task_guidance(self, sm_agent, sample_story):
        """Test execution with empty task guidance"""
        result = await sm_agent.execute(sample_story, "")

        # Should still succeed with empty guidance
        assert result[0] is True

    @pytest.mark.asyncio
    async def test_execute_multiple_stories(self, sm_agent, sample_task_guidance):
        """Test executing SM phase for multiple stories"""
        from dataclasses import dataclass

        @dataclass
        class Story:
            epic_num: int
            story_num: int
            title: str
            path: str
            status: str

        stories = [
            Story(1, 1, "Story 1", "/test/1.md", "Draft"),
            Story(1, 2, "Story 2", "/test/2.md", "Draft"),
            Story(1, 3, "Story 3", "/test/3.md", "Draft"),
        ]

        results = []
        for story in stories:
            result = await sm_agent.execute(story, sample_task_guidance)
            results.append(result)

        # All should succeed
        assert all(r[0] for r in results)
        assert len(results) == 3

    def test_agent_properties(self, sm_agent):
        """Test agent properties"""
        assert sm_agent.agent_name == "SM Agent"
        assert sm_agent.phase == "Story Management"
        assert isinstance(sm_agent.project_root, Path)
        assert isinstance(sm_agent.tasks_path, Path)

    @pytest.mark.asyncio
    async def test_execute_preserves_config(self, sm_agent, sample_story):
        """Test that execution preserves configuration"""
        original_config = sm_agent.config

        await sm_agent.execute(sample_story, "")

        # Config should not be modified
        assert sm_agent.config == original_config

    @pytest.mark.asyncio
    async def test_execute_with_various_story_titles(self, sm_agent, sample_task_guidance):
        """Test execution with various story titles"""
        from dataclasses import dataclass

        @dataclass
        class Story:
            epic_num: int
            story_num: int
            title: str
            path: str
            status: str

        test_cases = [
            Story(1, 1, "Simple Title", "/test/1.md", "Draft"),
            Story(1, 2, "Title with (parentheses)", "/test/2.md", "Draft"),
            Story(1, 3, "Title with 'quotes'", "/test/3.md", "Draft"),
            Story(1, 4, "Title with special chars: @#$%", "/test/4.md", "Draft"),
        ]

        for story in test_cases:
            result = await sm_agent.execute(story, sample_task_guidance)
            assert result[0] is True, f"Failed for title: {story.title}"

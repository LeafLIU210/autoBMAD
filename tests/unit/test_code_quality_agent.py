"""
Unit tests for CodeQualityAgent module.
"""

from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.code_quality_agent import CodeQualityAgent


@pytest.fixture
def code_quality_agent():
    """Create a CodeQualityAgent instance for testing."""
    return CodeQualityAgent()


class TestCodeQualityAgent:
    """Test CodeQualityAgent class."""

    def test_init(self, code_quality_agent):
        """Test CodeQualityAgent initialization."""
        assert code_quality_agent.name == "Code Quality Agent"

    @pytest.mark.asyncio
    async def test_execute_basic(self, code_quality_agent):
        """Test basic execution."""
        story_content = "# Story\nContent"

        result = await code_quality_agent.execute(story_content)

        assert isinstance(result, dict)
        assert "status" in result or "passed" in result

    @pytest.mark.asyncio
    async def test_execute_with_path(self, code_quality_agent):
        """Test execution with story path."""
        story_content = "# Story\nContent"
        story_path = "docs/stories/1.1-test.md"

        result = await code_quality_agent.execute(
            story_content,
            story_path=story_path
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_with_guidance(self, code_quality_agent):
        """Test execution with task guidance."""
        story_content = "# Story\nContent"
        guidance = "Focus on code style"

        result = await code_quality_agent.execute(
            story_content,
            task_guidance=guidance
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_multiple_stories(self, code_quality_agent):
        """Test executing on multiple stories."""
        story_content = "# Story\nContent"

        results = await asyncio.gather(*[
            code_quality_agent.execute(story_content)
            for _ in range(3)
        ])

        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)

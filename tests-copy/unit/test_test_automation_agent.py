"""
Unit tests for TestAutomationAgent module.
"""

from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent


@pytest.fixture
def test_automation_agent():
    """Create a TestAutomationAgent instance for testing."""
    return TestAutomationAgent()


class TestTestAutomationAgent:
    """Test TestAutomationAgent class."""

    def test_init(self, test_automation_agent):
        """Test TestAutomationAgent initialization."""
        assert test_automation_agent.name == "Test Automation Agent"

    @pytest.mark.asyncio
    async def test_execute_basic(self, test_automation_agent):
        """Test basic execution."""
        story_content = "# Story\nContent"

        result = await test_automation_agent.execute(story_content)

        assert isinstance(result, dict)
        assert "status" in result or "passed" in result

    @pytest.mark.asyncio
    async def test_execute_with_path(self, test_automation_agent):
        """Test execution with story path."""
        story_content = "# Story\nContent"
        story_path = "docs/stories/1.1-test.md"

        result = await test_automation_agent.execute(
            story_content,
            story_path=story_path
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_runs_tests(self, test_automation_agent):
        """Test that execution runs tests."""
        story_content = "# Story\nContent"

        with patch('autoBMAD.epic_automation.test_automation_agent.logger') as mock_logger:
            result = await test_automation_agent.execute(story_content)

            assert isinstance(result, dict)
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_execute_with_custom_test_dir(self, test_automation_agent):
        """Test execution with custom test directory."""
        story_content = "# Story\nContent"
        test_dir = "custom_tests"

        result = await test_automation_agent.execute(
            story_content,
            test_dir=test_dir
        )

        assert isinstance(result, dict)

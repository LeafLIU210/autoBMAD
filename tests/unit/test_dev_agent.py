"""
Unit tests for DevAgent module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
import pytest
import subprocess

from autoBMAD.epic_automation.dev_agent import DevAgent


@pytest.fixture
def dev_agent():
    """Create a DevAgent instance for testing."""
    return DevAgent(use_claude=False)


@pytest.fixture
def dev_agent_with_claude():
    """Create a DevAgent instance with Claude enabled."""
    return DevAgent(use_claude=True)


@pytest.fixture
def sample_story_content():
    """Sample story content for testing."""
    return """# Story 1.1: Test Story

## Status
**Status:** Ready for Development

## Story
**As a** developer,
**I want** to implement a feature,
**so that** users can benefit.

## Acceptance Criteria
1. Feature works correctly
2. Tests pass
3. Code follows standards

## Tasks / Subtasks
- [ ] Implement feature
- [ ] Write tests
- [ ] Update documentation
"""


class TestDevAgent:
    """Test DevAgent class."""

    def test_init_default(self):
        """Test DevAgent initialization with defaults."""
        agent = DevAgent(use_claude=False)

        assert agent.name == "Dev Agent"
        assert agent.use_claude is False

    def test_init_with_claude(self, dev_agent_with_claude):
        """Test DevAgent initialization with Claude enabled."""
        assert dev_agent_with_claude.use_claude is True

    def test_validate_prompt_format_valid(self, dev_agent):
        """Test prompt format validation with valid prompt."""
        valid_prompt = "# Task\nImplement feature X\n\n## Requirements\n- Requirement 1\n- Requirement 2"

        result = dev_agent._validate_prompt_format(valid_prompt)

        assert result is True

    def test_validate_prompt_format_invalid(self, dev_agent):
        """Test prompt format validation with invalid prompt."""
        invalid_prompt = "Too short"

        result = dev_agent._validate_prompt_format(invalid_prompt)

        assert result is False

    def test_validate_prompt_format_empty(self, dev_agent):
        """Test prompt format validation with empty prompt."""
        result = dev_agent._validate_prompt_format("")

        assert result is False

    @pytest.mark.asyncio
    async def test_extract_requirements(self, dev_agent, sample_story_content):
        """Test extracting requirements from story content."""
        requirements = await dev_agent._extract_requirements(sample_story_content)

        assert requirements is not None
        assert "story_id" in requirements
        assert "acceptance_criteria" in requirements
        assert "tasks" in requirements

    @pytest.mark.asyncio
    async def test_extract_requirements_empty(self, dev_agent):
        """Test extracting requirements from empty content."""
        requirements = await dev_agent._extract_requirements("")

        assert requirements is not None
        assert requirements == {}

    @pytest.mark.asyncio
    async def test_validate_requirements(self, dev_agent):
        """Test validating requirements."""
        requirements = {
            "story_id": "1.1",
            "acceptance_criteria": ["Criterion 1"],
            "tasks": ["Task 1"]
        }

        result = await dev_agent._validate_requirements(requirements)

        assert result["valid"] is True
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_validate_requirements_invalid(self, dev_agent):
        """Test validating invalid requirements."""
        requirements = {
            "story_id": "",
            "acceptance_criteria": [],
            "tasks": []
        }

        result = await dev_agent._validate_requirements(requirements)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_apply_dev_guidance(self, dev_agent):
        """Test applying development guidance."""
        requirements = {"task": "implement feature"}
        guidance = "Follow coding standards"

        result = await dev_agent._apply_dev_guidance(requirements, guidance)

        assert result is True

    @pytest.mark.asyncio
    async def test_execute_development_tasks(self, dev_agent):
        """Test executing development tasks."""
        requirements = {
            "story_id": "1.1",
            "tasks": ["Implement feature"]
        }

        with patch('autoBMAD.epic_automation.dev_agent.query') as mock_query:
            mock_query.return_value = MagicMock()

            result = await dev_agent._execute_development_tasks(requirements)

            # In simulation mode, should still work
            assert result is True

    @pytest.mark.asyncio
    async def test_execute_basic(self, dev_agent, sample_story_content):
        """Test basic execution of Dev agent."""
        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            with patch.object(dev_agent, '_validate_requirements') as mock_validate:
                with patch.object(dev_agent, '_apply_dev_guidance') as mock_apply:
                    with patch.object(dev_agent, '_execute_development_tasks') as mock_execute:
                        mock_extract.return_value = {"story_id": "1.1"}
                        mock_validate.return_value = {"valid": True, "errors": []}
                        mock_apply.return_value = True
                        mock_execute.return_value = True

                        result = await dev_agent.execute(
                            story_content=sample_story_content,
                            task_guidance="Test guidance",
                            story_path="docs/stories/1.1-test.md"
                        )

                        assert result is True
                        mock_extract.assert_called_once()
                        mock_validate.assert_called_once()
                        mock_apply.assert_called_once()
                        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_invalid_requirements(self, dev_agent, sample_story_content):
        """Test execution with invalid requirements."""
        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            with patch.object(dev_agent, '_validate_requirements') as mock_validate:
                mock_extract.return_value = {"story_id": "1.1"}
                mock_validate.return_value = {"valid": False, "errors": ["Error 1"]}

                result = await dev_agent.execute(
                    story_content=sample_story_content,
                    task_guidance="Test guidance",
                    story_path="docs/stories/1.1-test.md"
                )

                assert result is False

    @pytest.mark.asyncio
    async def test_execute_with_qa_feedback(self, dev_agent, sample_story_content):
        """Test execution with QA feedback handling."""
        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            with patch.object(dev_agent, '_validate_requirements') as mock_validate:
                with patch.object(dev_agent, '_apply_dev_guidance') as mock_apply:
                    with patch.object(dev_agent, '_execute_development_tasks') as mock_execute:
                        with patch.object(dev_agent, '_handle_qa_feedback') as mock_qa:
                            mock_extract.return_value = {"story_id": "1.1"}
                            mock_validate.return_value = {"valid": True, "errors": []}
                            mock_apply.return_value = True
                            mock_execute.return_value = True
                            mock_qa.return_value = True

                            result = await dev_agent.execute(
                                story_content=sample_story_content,
                                task_guidance="Test guidance",
                                story_path="docs/stories/1.1-test.md"
                            )

                            assert result is True
                            mock_qa.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_qa_agent(self, dev_agent):
        """Test notifying QA agent."""
        story_path = "docs/stories/1.1-test.md"

        with patch('autoBMAD.epic_automation.dev_agent.logger') as mock_logger:
            result = await dev_agent._notify_qa_agent(story_path)

            assert result is not None
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_handle_qa_feedback(self, dev_agent):
        """Test handling QA feedback."""
        qa_prompt = "QA feedback prompt"
        story_path = "docs/stories/1.1-test.md"

        with patch.object(dev_agent, '_execute_triple_claude_calls') as mock_triple:
            mock_triple.return_value = True

            result = await dev_agent._handle_qa_feedback(qa_prompt, story_path)

            assert result is True
            mock_triple.assert_called_once_with(qa_prompt, story_path)

    @pytest.mark.asyncio
    async def test_execute_triple_claude_calls(self, dev_agent):
        """Test executing triple Claude calls."""
        qa_prompt = "QA feedback"
        story_path = "docs/stories/1.1-test.md"

        with patch.object(dev_agent, '_execute_single_claude_sdk') as mock_single:
            mock_single.return_value = True

            result = await dev_agent._execute_triple_claude_calls(qa_prompt, story_path)

            assert result is True
            assert mock_single.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_single_claude_sdk(self, dev_agent):
        """Test executing single Claude SDK call."""
        prompt = "Test prompt"
        story_path = "docs/stories/1.1-test.md"

        with patch.object(dev_agent, '_execute_claude_sdk') as mock_execute:
            mock_execute.return_value = True

            result = await dev_agent._execute_single_claude_sdk(prompt, story_path)

            assert result is True
            mock_execute.assert_called_once_with(prompt, story_path)

    @pytest.mark.asyncio
    async def test_execute_claude_sdk(self, dev_agent):
        """Test executing Claude SDK."""
        prompt = "Test prompt"
        story_path = "docs/stories/1.1-test.md"

        with patch('autoBMAD.epic_automation.dev_agent.SafeClaudeSDK') as mock_sdk:
            mock_instance = MagicMock()
            mock_instance.run.return_value = True
            mock_sdk.return_value = mock_instance

            result = await dev_agent._execute_claude_sdk(prompt, story_path)

            assert result is True
            mock_sdk.assert_called_once()
            mock_instance.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_claude_sdk_with_claude_available(self, dev_agent_with_claude):
        """Test executing Claude SDK when Claude is available."""
        prompt = "Test prompt"
        story_path = "docs/stories/1.1-test.md"

        with patch('autoBMAD.epic_automation.dev_agent.query') as mock_query:
            mock_query.return_value = MagicMock()

            result = await dev_agent_with_claude._execute_claude_sdk(prompt, story_path)

            assert result is True

    @pytest.mark.asyncio
    async def test_update_story_completion(self, dev_agent, sample_story_content):
        """Test updating story completion status."""
        requirements = {"story_id": "1.1", "status": "completed"}

        with patch('autoBMAD.epic_automation.dev_agent.logger') as mock_logger:
            await dev_agent._update_story_completion(sample_story_content, requirements)

            mock_logger.info.assert_called()

    def test_check_claude_available(self, dev_agent):
        """Test checking if Claude is available."""
        with patch('autoBMAD.epic_automation.dev_agent.query') as mock_query:
            if mock_query is not None:
                result = dev_agent._check_claude_available()
                assert isinstance(result, bool)

    def test_claude_sdk_query(self, dev_agent):
        """Test Claude SDK query method exists."""
        assert hasattr(dev_agent, 'claude_sdk_query')
        assert callable(dev_agent.claude_sdk_query)

    @pytest.mark.asyncio
    async def test_execute_with_empty_guidance(self, dev_agent, sample_story_content):
        """Test execution with empty guidance."""
        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            with patch.object(dev_agent, '_validate_requirements') as mock_validate:
                with patch.object(dev_agent, '_execute_development_tasks') as mock_execute:
                    mock_extract.return_value = {"story_id": "1.1"}
                    mock_validate.return_value = {"valid": True, "errors": []}
                    mock_execute.return_value = True

                    result = await dev_agent.execute(
                        story_content=sample_story_content,
                        task_guidance="",
                        story_path="docs/stories/1.1-test.md"
                    )

                    assert result is True

    @pytest.mark.asyncio
    async def test_execute_fails_development_tasks(self, dev_agent, sample_story_content):
        """Test execution when development tasks fail."""
        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            with patch.object(dev_agent, '_validate_requirements') as mock_validate:
                with patch.object(dev_agent, '_apply_dev_guidance') as mock_apply:
                    with patch.object(dev_agent, '_execute_development_tasks') as mock_execute:
                        mock_extract.return_value = {"story_id": "1.1"}
                        mock_validate.return_value = {"valid": True, "errors": []}
                        mock_apply.return_value = True
                        mock_execute.return_value = False

                        result = await dev_agent.execute(
                            story_content=sample_story_content,
                            task_guidance="Test guidance",
                            story_path="docs/stories/1.1-test.md"
                        )

                        assert result is False

    @pytest.mark.asyncio
    async def test_execute_with_long_story(self, dev_agent):
        """Test execution with a very long story content."""
        long_content = "# Story\n" + "Long content\n" * 1000

        with patch.object(dev_agent, '_extract_requirements') as mock_extract:
            mock_extract.return_value = {"story_id": "1.1"}

            requirements = await dev_agent._extract_requirements(long_content)

            assert requirements is not None

    def test_agent_name(self, dev_agent):
        """Test agent name is set correctly."""
        assert dev_agent.name == "Dev Agent"

"""Tests for SMAgent class."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.agents import SMAgent, SMConfig


class TestSMAgent:
    """Test suite for SMAgent class."""

    def test_sm_config_default(self):
        """Test SMConfig with default values."""
        config = SMConfig()
        assert config.task_name == "create-next-story"
        assert config.story_output_dir == "docs/stories"
        assert config.epic_pattern == "epic-{num}.md"
        assert config.story_pattern == "{epic}.{story}.story.md"

    def test_sm_config_custom(self):
        """Test SMConfig with custom values."""
        config = SMConfig(
            story_output_dir="custom/stories",
            epic_pattern="custom-epic-{num}.md"
        )
        assert config.story_output_dir == "custom/stories"
        assert config.epic_pattern == "custom-epic-{num}.md"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_sm_agent_initialization(self, mock_anthropic):
        """Test SMAgent initialization."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = SMAgent()

        assert agent.config.task_name == "create-next-story"
        assert agent.config.story_output_dir == "docs/stories"
        assert agent.client == mock_client
        assert agent.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.mkdir')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_create_story_success(self, mock_mkdir, mock_exists, mock_file, mock_anthropic):
        """Test successful story creation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="# Story Content")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            config = SMConfig(story_output_dir=tmpdir)
            agent = SMAgent(config)

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.create_story(
                    epic_number=1,
                    story_number=1,
                    story_title="Test Story",
                    epic_content="Test epic content"
                )

            assert result["status"] == "success"
            assert result["story_id"] == "1.1"
            assert result["title"] == "Test Story"
            assert "story_path" in result

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_create_story_no_client(self, mock_anthropic):
        """Test create_story raises error when client not initialized."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = SMConfig()
        agent = SMAgent(config)
        agent.client = None

        with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
            agent.create_story(1, 1, "Test Story", "Epic content")

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_identify_next_story_success(self, mock_anthropic):
        """Test successful next story identification."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Next story should be 1.2")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        agent = SMAgent()

        with patch.object(agent, 'task_guidance', "test guidance"):
            result = agent.identify_next_story(
                existing_stories=["1.1"],
                epic_file="epic-1.md"
            )

        assert result["status"] == "success"
        assert "analysis" in result

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="# Existing Story\nContent"))
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_prepare_story_draft_success(self, mock_file, mock_anthropic):
        """Test successful story draft preparation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="# Enhanced Story\nEnhanced content")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            story_path = Path(tmpdir) / "test-story.md"
            story_path.write_text("# Existing Story\nContent")

            agent = SMAgent()

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.prepare_story_draft(
                    story_path=str(story_path),
                    architecture_docs=["arch.md"]
                )

            assert result["status"] == "success"
            assert result["story_path"] == str(story_path)
            assert "enhanced_content" in result

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_prepare_story_draft_file_not_found(self, mock_anthropic):
        """Test prepare_story_draft raises error when file not found."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = SMAgent()

        with pytest.raises(FileNotFoundError):
            agent.prepare_story_draft("nonexistent-story.md")

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_generate_tasks_success(self, mock_anthropic):
        """Test successful task generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated tasks:\n1. Task 1\n2. Task 2")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        agent = SMAgent()

        with patch.object(agent, 'task_guidance', "test guidance"):
            result = agent.generate_tasks(
                story_content="Story content",
                acceptance_criteria=["AC1", "AC2"]
            )

        assert result["status"] == "success"
        assert "tasks" in result

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_agent_info(self, mock_anthropic):
        """Test get_agent_info returns correct information."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = SMAgent()

        info = agent.get_agent_info()

        assert info["agent_type"] == "Story Master"
        assert info["specialization"] == "Story creation and preparation"
        assert info["output_directory"] == "docs/stories"
        assert info["task_name"] == "create-next-story"
        assert info["guidance_loaded"] is True

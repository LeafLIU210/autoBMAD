"""
Tests for BaseAgent class.

This module contains unit tests for the BaseAgent class which provides
common functionality for all BMAD agents.
"""

import pytest
import os
import logging
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys

# Check if bmad_agents module exists
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
bmad_agents_path = src_path / "bmad_agents"
HAS_BMAD_AGENTS = bmad_agents_path.exists()

# Skip all tests if bmad_agents doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_BMAD_AGENTS,
    reason="bmad_agents module not found - skipping tests"
)

# Add src to path for imports
sys.path.insert(0, str(src_path))

if HAS_BMAD_AGENTS:
    from bmad_agents.base_agent import BaseAgent


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_init(self):
        """Test BaseAgent initialization."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            assert agent.agent_name == "test"
            assert agent.task_file == "test-task.md"
            assert agent.task_guidance is None
            assert agent.client is None

    def test_setup_logger(self):
        """Test logger setup."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            logger = agent._setup_logger()
            assert isinstance(logger, logging.Logger)
            assert logger.name == "bmad_agents.test"

    @patch('builtins.open', new_callable=mock_open, read_data="Test task guidance content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_task_guidance_success(self, mock_exists, mock_file):
        """Test successful task guidance loading."""
        with patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")
            agent._load_task_guidance()

            assert agent.task_guidance == "Test task guidance content"

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_task_guidance_file_not_found(self, mock_exists):
        """Test task guidance loading when file not found."""
        with patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "nonexistent.md")

            with pytest.raises(RuntimeError) as exc_info:
                agent._load_task_guidance()

            assert "Task file not found" in str(exc_info.value)

    @patch('builtins.open', side_effect=IOError("Read error"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_task_guidance_read_error(self, mock_exists, mock_file):
        """Test task guidance loading when read error occurs."""
        with patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            with pytest.raises(RuntimeError) as exc_info:
                agent._load_task_guidance()

            assert "Failed to load task guidance" in str(exc_info.value)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-api-key'})
    @patch('anthropic.Anthropic')
    def test_init_client_success(self, mock_anthropic):
        """Test successful client initialization."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'):
            agent = BaseAgent("test", "test-task.md")
            agent._init_client()

            assert agent.client is not None
            mock_anthropic.assert_called_once_with(api_key='test-api-key')

    @patch.dict(os.environ, {}, clear=True)
    def test_init_client_no_api_key(self):
        """Test client initialization without API key."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'):
            agent = BaseAgent("test", "test-task.md")

            with pytest.raises(RuntimeError) as exc_info:
                agent._init_client()

            assert "ANTHROPIC_API_KEY environment variable not set" in str(exc_info.value)

    def test_get_task_guidance_not_loaded(self):
        """Test getting task guidance when not loaded."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            with pytest.raises(RuntimeError) as exc_info:
                agent.get_task_guidance()

            assert "Task guidance not loaded" in str(exc_info.value)

    def test_get_task_guidance_success(self):
        """Test getting task guidance successfully."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")
            agent.task_guidance = "Test guidance"

            result = agent.get_task_guidance()
            assert result == "Test guidance"

    def test_get_client_not_initialized(self):
        """Test getting client when not initialized."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            with pytest.raises(RuntimeError) as exc_info:
                agent.get_client()

            assert "Claude SDK client not initialized" in str(exc_info.value)

    def test_get_client_success(self):
        """Test getting client successfully."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")
            mock_client = Mock()
            agent.client = mock_client

            result = agent.get_client()
            assert result == mock_client

    @pytest.mark.asyncio
    async def test_execute_with_claude_success(self):
        """Test successful execution with Claude."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'):
            agent = BaseAgent("test", "test-task.md")
            agent.task_guidance = "Test guidance"
            agent.client = Mock()

            # Mock the client response
            mock_response = Mock()
            mock_response.content = [Mock(text="Test response")]
            mock_response.usage = {"input_tokens": 10, "output_tokens": 20}
            agent.client.messages.create.return_value = mock_response

            result = await agent.execute_with_claude("Test prompt")

            assert result["success"] is True
            assert result["content"] == "Test response"
            assert result["usage"]["input_tokens"] == 10

    @pytest.mark.asyncio
    async def test_execute_with_claude_error(self):
        """Test execution with Claude when error occurs."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'):
            agent = BaseAgent("test", "test-task.md")
            agent.task_guidance = "Test guidance"
            agent.client = Mock()

            # Mock an exception
            agent.client.messages.create.side_effect = Exception("API error")

            result = await agent.execute_with_claude("Test prompt")

            assert result["success"] is False
            assert "error" in result
            assert result["error_type"] == "Exception"

    def test_repr(self):
        """Test string representation."""
        with patch('bmad_agents.base_agent.BaseAgent._load_task_guidance'), \
             patch('bmad_agents.base_agent.BaseAgent._init_client'):
            agent = BaseAgent("test", "test-task.md")

            assert repr(agent) == "BaseAgent(agent_name='test', task_file='test-task.md')"

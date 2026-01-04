"""Simplified tests for BaseAgent class."""

import pytest
import os
from unittest.mock import Mock, patch, mock_open

from src.agents import BaseAgent, AgentConfig


class TestBaseAgentSimple:
    """Simplified test suite for BaseAgent class."""

    def test_agent_config_creation(self):
        """Test AgentConfig creation with default values."""
        config = AgentConfig(task_name="test-task")
        assert config.task_name == "test-task"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.model == "claude-3-5-sonnet-20241022"

    def test_agent_config_custom_values(self):
        """Test AgentConfig with custom values."""
        config = AgentConfig(
            task_name="custom-task",
            max_tokens=8192,
            temperature=0.5,
            model="custom-model",
            api_key="test-key"
        )
        assert config.task_name == "custom-task"
        assert config.max_tokens == 8192
        assert config.temperature == 0.5
        assert config.model == "custom-model"
        assert config.api_key == "test-key"

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_base_agent_initialization(self, mock_exists, mock_file, mock_anthropic):
        """Test BaseAgent initialization with mocked client."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        assert agent.config == config
        assert agent.client == mock_client
        assert agent.task_guidance is not None
        assert agent.session_id is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_base_agent_missing_api_key(self):
        """Test BaseAgent raises error when API key is missing."""
        config = AgentConfig(task_name="test-task")

        with pytest.raises(RuntimeError, match="API key not found"):
            BaseAgent(config)

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_task_guidance_file_not_found(self, mock_exists):
        """Test task guidance loading raises error when file not found."""
        config = AgentConfig(task_name="nonexistent-task", api_key="test-key")

        with pytest.raises(FileNotFoundError):
            BaseAgent(config)

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_session_info(self, mock_exists, mock_file, mock_anthropic):
        """Test get_session_info returns correct information."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        info = agent.get_session_info()

        assert info["task_name"] == "test-task"
        assert info["session_id"] == agent.session_id
        assert info["model"] == config.model
        assert info["guidance_loaded"] is True
        assert info["client_initialized"] is True

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_close(self, mock_exists, mock_file, mock_anthropic):
        """Test close method cleans up resources."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        assert agent.client is not None
        assert agent.session_id is not None

        agent.close()

        assert agent.client is None
        assert agent.session_id is None

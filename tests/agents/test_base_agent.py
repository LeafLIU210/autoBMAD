"""Tests for BaseAgent class."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.agents import BaseAgent, AgentConfig


class TestBaseAgent:
    """Test suite for BaseAgent class."""

    def test_agent_config_creation(self):
        """Test AgentConfig creation with default values."""
        config = AgentConfig(task_name="test-task")
        assert config.task_name == "test-task"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.api_key is None

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
    @patch('builtins.open', mock_open(read_data="test guidance content"))
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

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {}, clear=True)
    def test_base_agent_missing_api_key(self, mock_anthropic):
        """Test BaseAgent raises error when API key is missing."""
        config = AgentConfig(task_name="test-task")

        with pytest.raises(RuntimeError, match="API key not found"):
            BaseAgent(config)

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance content"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_load_task_guidance_success(self, mock_exists, mock_file, mock_anthropic):
        """Test successful task guidance loading."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        assert agent.task_guidance == "test guidance content"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_load_task_guidance_file_not_found(self, mock_anthropic):
        """Test task guidance loading raises error when file not found."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="nonexistent-task", api_key="test-key")

        with pytest.raises(FileNotFoundError):
            BaseAgent(config)

    @patch('anthropic.Anthropic')
    @patch('builtins.open', side_effect=IOError("Read error"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_load_task_guidance_io_error(self, mock_exists, mock_file, mock_anthropic):
        """Test task guidance loading raises error on IO failure."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")

        with pytest.raises(IOError):
            BaseAgent(config)

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_process_request_success(self, mock_exists, mock_file, mock_anthropic):
        """Test successful request processing."""
        import asyncio
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        # Run async test
        async def run_test():
            result = await agent.process_request("test input")
            assert result["response"] == "test response"
            assert result["session_id"] == agent.session_id
            assert result["model"] == config.model

        asyncio.run(run_test())

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_process_request_no_client(self, mock_anthropic):
        """Test process_request raises error when client not initialized."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client = None

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)
        agent.client = None

        with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
            agent.process_request("test input")

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
    def test_context_manager(self, mock_exists, mock_file, mock_anthropic):
        """Test BaseAgent can be used as context manager."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")

        with BaseAgent(config) as agent:
            assert agent.client is not None
            assert agent.session_id is not None

        # After context exit, client should be closed
        assert agent.client is None

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="test guidance"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_repr(self, mock_exists, mock_file, mock_anthropic):
        """Test BaseAgent string representation."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        config = AgentConfig(task_name="test-task", api_key="test-key")
        agent = BaseAgent(config)

        repr_str = repr(agent)
        assert "BaseAgent" in repr_str
        assert "test-task" in repr_str
        assert agent.session_id in repr_str

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

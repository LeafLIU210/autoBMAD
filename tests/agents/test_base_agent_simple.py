"""Simplified tests for BaseAgent class."""

import pytest
import os
from unittest.mock import Mock, patch, mock_open

from autoBMAD.epic_automation.agents import BaseAgent, AgentConfig


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

    @patch('autoBMAD.epic_automation.agents.Anthropic')
    def test_base_agent_initialization(self, mock_anthropic):
        """Test BaseAgent initialization with mocked client."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        with patch('builtins.open', mock_open(read_data="test guidance")):
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
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
        """Test task guidance loading handles missing file gracefully."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="nonexistent-task", api_key="test-key")
            agent = BaseAgent(config)

            # Should not raise error, just log warning and set task_guidance to empty
            assert agent.task_guidance == ""
            assert agent.config == config

    @patch('autoBMAD.epic_automation.agents.Anthropic')
    def test_get_session_info(self, mock_anthropic):
        """Test get_session_info returns correct information."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        with patch('builtins.open', mock_open(read_data="test guidance")):
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
                    config = AgentConfig(task_name="test-task", api_key="test-key")
                    agent = BaseAgent(config)

                    info = agent.get_session_info()

                    assert info["task_name"] == "test-task"
                    assert info["session_id"] == agent.session_id
                    assert info["model"] == config.model
                    assert info["guidance_loaded"] is True
                    assert info["client_initialized"] is True

    @patch('autoBMAD.epic_automation.agents.Anthropic')
    def test_get_session_info_with_none_client(self, mock_anthropic):
        """Test get_session_info when client is None (SDK not installed)."""
        mock_anthropic.return_value = None

        with patch('builtins.open', mock_open(read_data="test guidance")):
            with patch('pathlib.Path.exists', return_value=True):
                with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
                    config = AgentConfig(task_name="test-task", api_key="test-key")
                    agent = BaseAgent(config)

                    info = agent.get_session_info()

                    assert info["task_name"] == "test-task"
                    assert info["session_id"] == agent.session_id
                    assert info["model"] == config.model
                    assert info["guidance_loaded"] is True
                    assert info["client_initialized"] is False  # Client is None

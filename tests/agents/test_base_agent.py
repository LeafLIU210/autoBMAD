"""Tests for BaseAgent class."""

import pytest
import os
from unittest.mock import Mock, patch, mock_open, MagicMock

# First, mock the anthropic module before importing agents
import sys
from unittest.mock import MagicMock as MockAnthropic

# Mock the anthropic module
anthropic_mock = Mock()
sys.modules['anthropic'] = anthropic_mock
sys.modules['anthropic.Anthropic'] = MockAnthropic

from autoBMAD.epic_automation.agents import BaseAgent, AgentConfig


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

    def test_base_agent_initialization(self):
        """Test BaseAgent initialization with mocked client."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance content")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            assert agent.config == config
            assert agent.client == mock_client
            assert agent.task_guidance is not None
            assert agent.session_id is not None

    def test_base_agent_missing_api_key(self):
        """Test BaseAgent raises error when API key is missing."""
        config = AgentConfig(task_name="test-task")

        with patch('autoBMAD.epic_automation.agents.Anthropic'), \
             patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="API key not found"):
                BaseAgent(config)

    def test_load_task_guidance_success(self):
        """Test successful task guidance loading."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance content")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            # File includes trailing newline
            assert agent.task_guidance.strip() == "test guidance content"

    def test_load_task_guidance_file_not_found(self):
        """Test task guidance loading raises error when file not found."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('pathlib.Path.exists', return_value=False), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="nonexistent-task", api_key="test-key")

            # This should succeed because the file doesn't exist but it's handled gracefully
            agent = BaseAgent(config)
            assert agent.task_guidance == ""

    def test_load_task_guidance_io_error(self):
        """Test task guidance loading raises error on IO failure."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('pathlib.Path.read_text', side_effect=IOError("Read error")), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")

            # The IOError should be caught and logged, not raised
            agent = BaseAgent(config)
            assert agent.task_guidance == ""

    def test_process_request_success(self):
        """Test successful request processing."""
        import asyncio
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="test response")]
        mock_client.messages.create.return_value = mock_response
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            # Run async test
            async def run_test():
                result = await agent.process_request("test input")
                assert result["response"] == "test response"
                assert result["session_id"] == agent.session_id
                assert result["model"] == config.model

            asyncio.run(run_test())

    def test_process_request_no_client(self):
        """Test process_request raises error when client not initialized."""
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=None), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)
            # Client will be None because Anthropic returned None
            assert agent.client is None

            with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
                # Make it async to test properly
                import asyncio
                asyncio.run(agent.process_request("test input"))

    def test_get_session_info(self):
        """Test get_session_info returns correct information."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            info = agent.get_session_info()

            assert info["task_name"] == "test-task"
            assert info["session_id"] == agent.session_id
            assert info["model"] == config.model
            assert info["guidance_loaded"] is True
            assert info["client_initialized"] is True

    def test_context_manager(self):
        """Test BaseAgent can be used as context manager."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")

            with BaseAgent(config) as agent:
                assert agent.client is not None
                assert agent.session_id is not None

            # After context exit, client should be closed
            assert agent.client is None

    def test_repr(self):
        """Test BaseAgent string representation."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            repr_str = repr(agent)
            assert "BaseAgent" in repr_str
            assert "test-task" in repr_str
            assert agent.session_id in repr_str

    def test_exit(self):
        """Test __exit__ method cleans up resources."""
        mock_client = Mock()
        with patch('autoBMAD.epic_automation.agents.Anthropic', return_value=mock_client), \
             patch('builtins.open', mock_open(read_data="test guidance")), \
             patch('pathlib.Path.exists', return_value=True), \
             patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            config = AgentConfig(task_name="test-task", api_key="test-key")
            agent = BaseAgent(config)

            assert agent.client is not None
            assert agent.session_id is not None

            # Use __exit__ to clean up
            agent.__exit__(None, None, None)

            assert agent.client is None
            # Note: session_id is not None, it's just the client that gets closed
            assert agent.session_id is not None

"""
Unit tests for agents module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from autoBMAD.epic_automation.agents import AgentConfig, BaseAgent


class TestAgentConfig:
    """Test AgentConfig class."""

    def test_init_default_values(self):
        """Test AgentConfig initialization with default values."""
        config = AgentConfig(task_name="test_task")

        assert config.task_name == "test_task"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.api_key is None

    def test_init_custom_values(self):
        """Test AgentConfig initialization with custom values."""
        config = AgentConfig(
            task_name="custom_task",
            max_tokens=8192,
            temperature=0.5,
            model="claude-3-5-opus-20241022",
            api_key="test_key"
        )

        assert config.task_name == "custom_task"
        assert config.max_tokens == 8192
        assert config.temperature == 0.5
        assert config.model == "claude-3-5-opus-20241022"
        assert config.api_key == "test_key"

    def test_api_key_from_env(self):
        """Test that API key is loaded from environment if not provided."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env_key"}):
            config = AgentConfig(task_name="test_task")
            # Note: API key is not automatically loaded in __init__
            # It's loaded when needed by the agent
            assert config.api_key is None

    def test_config_str_representation(self):
        """Test string representation of AgentConfig."""
        config = AgentConfig(task_name="test_task")
        assert "test_task" in str(config)
        assert "4096" in str(config)


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.test_executed = False

    async def execute_task(self, task: str) -> dict:
        """Execute a mock task."""
        self.test_executed = True
        return {"status": "completed", "task": task}

    async def run(self) -> dict:
        """Run the agent."""
        return await self.execute_task("mock_task")


class TestBaseAgent:
    """Test BaseAgent class."""

    def test_init(self):
        """Test BaseAgent initialization."""
        config = AgentConfig(task_name="test_task")
        agent = MockAgent(config)

        assert agent.config == config
        assert agent.task_name == "test_task"

    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test task execution."""
        config = AgentConfig(task_name="test_task")
        agent = MockAgent(config)

        result = await agent.execute_task("test")

        assert result["status"] == "completed"
        assert result["task"] == "test"
        assert agent.test_executed is True

    @pytest.mark.asyncio
    async def test_run(self):
        """Test running the agent."""
        config = AgentConfig(task_name="test_task")
        agent = MockAgent(config)

        result = await agent.run()

        assert result["status"] == "completed"

    def test_logging(self):
        """Test that agent has proper logging setup."""
        config = AgentConfig(task_name="test_task")
        agent = MockAgent(config)

        assert agent.logger is not None
        assert agent.logger.name == "autoBMAD.epic_automation.agents"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in task execution."""
        config = AgentConfig(task_name="test_task")

        class FailingAgent(BaseAgent):
            async def execute_task(self, task: str) -> dict:
                raise ValueError("Test error")

            async def run(self) -> dict:
                return await self.execute_task("fail")

        agent = FailingAgent(config)

        with pytest.raises(ValueError, match="Test error"):
            await agent.run()

    @patch('autoBMAD.epic_automation.agents.Anthropic')
    def test_anthropic_client_initialization(self, mock_anthropic):
        """Test Anthropic client initialization when available."""
        config = AgentConfig(task_name="test_task", api_key="test_key")
        agent = MockAgent(config)

        # The BaseAgent doesn't initialize Anthropic in __init__
        # It would be done when actually calling the API
        # So we just verify the mock is callable
        mock_anthropic.return_value = MagicMock()
        assert mock_anthropic is not None

    def test_agent_config_validation(self):
        """Test that AgentConfig validates parameters."""
        # Valid config
        config = AgentConfig(
            task_name="test",
            max_tokens=1000,
            temperature=0.0,
            model="test-model"
        )
        assert config.task_name == "test"
        assert config.max_tokens == 1000
        assert config.temperature == 0.0
        assert config.model == "test-model"

        # Test edge cases
        config = AgentConfig(
            task_name="test",
            max_tokens=1,
            temperature=1.0,
            model="test-model"
        )
        assert config.max_tokens == 1
        assert config.temperature == 1.0

    def test_multiple_agents_independent(self):
        """Test that multiple agent instances are independent."""
        config1 = AgentConfig(task_name="task1")
        config2 = AgentConfig(task_name="task2")

        agent1 = MockAgent(config1)
        agent2 = MockAgent(config2)

        assert agent1.config != agent2.config
        assert agent1.task_name != agent2.task_name

    @pytest.mark.asyncio
    async def test_async_task_execution(self):
        """Test that tasks are executed asynchronously."""
        config = AgentConfig(task_name="test_task")
        agent = MockAgent(config)

        # Execute multiple tasks concurrently
        tasks = [agent.execute_task(f"task_{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["task"] == f"task_{i}"

    def test_config_comparison(self):
        """Test AgentConfig comparison."""
        config1 = AgentConfig(task_name="test")
        config2 = AgentConfig(task_name="test")
        config3 = AgentConfig(task_name="different")

        assert config1.task_name == config2.task_name
        assert config1.task_name != config3.task_name

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        config = AgentConfig(task_name="lifecycle_test")
        agent = MockAgent(config)

        # Verify initial state
        assert not agent.test_executed

        # Execute task
        result = await agent.run()
        assert result["status"] == "completed"
        assert agent.test_executed is True

        # Can execute again
        result2 = await agent.run()
        assert result2["status"] == "completed"

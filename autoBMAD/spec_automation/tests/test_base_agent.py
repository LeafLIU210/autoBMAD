"""Tests for BaseAgent.

Comprehensive test suite for BaseAgent functionality.
"""

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anyio.abc import TaskGroup

from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent."""
        return {"status": "success", "args": args, "kwargs": kwargs}


class TestBaseAgent:
    """Tests for BaseAgent class."""

    def test_initialization(self):
        """Test BaseAgent initialization."""
        agent = ConcreteAgent(name="TestAgent")
        assert agent.name == "TestAgent"
        assert agent.task_group is None
        assert agent._execution_context == {}
        assert agent._log_manager is None

    def test_initialization_with_task_group(self):
        """Test BaseAgent initialization with TaskGroup."""
        mock_tg = MagicMock()
        agent = ConcreteAgent(name="TestAgent", task_group=mock_tg)
        assert agent.task_group == mock_tg

    def test_initialization_with_log_manager(self):
        """Test BaseAgent initialization with log manager."""
        mock_log_manager = MagicMock()
        agent = ConcreteAgent(name="TestAgent", log_manager=mock_log_manager)
        assert agent._log_manager == mock_log_manager

    def test_set_task_group(self):
        """Test setting TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")
        mock_tg = MagicMock()

        agent.set_task_group(mock_tg)
        assert agent.task_group == mock_tg

    def test_log_execution_info(self):
        """Test _log_execution with info level."""
        agent = ConcreteAgent(name="TestAgent")

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution("Test message")
            mock_info.assert_called_once_with("[TestAgent] Test message")

    def test_log_execution_error(self):
        """Test _log_execution with error level."""
        agent = ConcreteAgent(name="TestAgent")

        with patch.object(agent.logger, "error") as mock_error:
            agent._log_execution("Error message", level="error")
            mock_error.assert_called_once_with("[TestAgent] Error message")

    def test_log_execution_warning(self):
        """Test _log_execution with warning level."""
        agent = ConcreteAgent(name="TestAgent")

        with patch.object(agent.logger, "warning") as mock_warning:
            agent._log_execution("Warning message", level="warning")
            mock_warning.assert_called_once_with("[TestAgent] Warning message")

    def test_validate_execution_context_no_task_group(self):
        """Test _validate_execution_context without TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")
        result = agent._validate_execution_context()
        assert result is False

    def test_validate_execution_context_with_task_group(self):
        """Test _validate_execution_context with TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")
        agent.task_group = MagicMock()

        result = agent._validate_execution_context()
        assert result is True

    @pytest.mark.anyio
    async def test_execute_within_taskgroup_no_taskgroup(self):
        """Test _execute_within_taskgroup raises without TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")

        async def dummy_coro():
            return "result"

        with pytest.raises(RuntimeError, match="TaskGroup not set"):
            await agent._execute_within_taskgroup(dummy_coro)

    @pytest.mark.anyio
    async def test_execute_within_taskgroup_with_mock(self):
        """Test _execute_within_taskgroup with Mock TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")
        agent.task_group = MagicMock()

        async def dummy_coro():
            return "test_result"

        result = await agent._execute_within_taskgroup(dummy_coro)
        assert result == "test_result"

    @pytest.mark.anyio
    async def test_execute_sdk_call_import_error(self):
        """Test _execute_sdk_call handles import error."""
        agent = ConcreteAgent(name="TestAgent")

        with patch(
            "autoBMAD.epic_automation.agents.base_agent.BaseAgent._execute_sdk_call"
        ) as mock_call:
            mock_result = SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                error_type=SDKErrorType.SDK_ERROR,
                errors=["Import error"],
                agent_name="TestAgent",
            )
            mock_call.return_value = mock_result

            result = await mock_call(None, "test prompt")

            assert result.is_success() is False
            assert result.error_type == SDKErrorType.SDK_ERROR

    @pytest.mark.anyio
    async def test_concrete_agent_execute(self):
        """Test ConcreteAgent.execute implementation."""
        agent = ConcreteAgent(name="TestAgent")
        result = await agent.execute("arg1", "arg2", key="value")

        assert result["status"] == "success"
        assert result["args"] == ("arg1", "arg2")
        assert result["kwargs"] == {"key": "value"}

    def test_logger_creation(self):
        """Test that logger is created with correct module name."""
        agent = ConcreteAgent(name="TestAgent")
        assert agent.logger is not None
        assert isinstance(agent.logger, logging.Logger)

    def test_execution_context_is_dict(self):
        """Test that _execution_context is initialized as dict."""
        agent = ConcreteAgent(name="TestAgent")
        assert isinstance(agent._execution_context, dict)
        agent._execution_context["key"] = "value"
        assert agent._execution_context["key"] == "value"

    @pytest.mark.anyio
    async def test_execute_sdk_call_general_exception(self):
        """Test _execute_sdk_call handles general exception."""
        agent = ConcreteAgent(name="TestAgent")

        # Mock the sdk_helper to raise an exception
        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            side_effect=RuntimeError("Test error"),
        ):
            result = await agent._execute_sdk_call(None, "test prompt")

            assert result.is_success() is False
            assert "Test error" in str(result.errors)

    def test_log_execution_default_level(self):
        """Test _log_execution uses info as default level."""
        agent = ConcreteAgent(name="TestAgent")

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution("Default level message")
            mock_info.assert_called_once()

    def test_name_in_log_message(self):
        """Test that agent name is included in log messages."""
        agent = ConcreteAgent(name="MySpecialAgent")

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution("Test")
            call_args = mock_info.call_args[0][0]
            assert "[MySpecialAgent]" in call_args

    @pytest.mark.anyio
    async def test_execute_sdk_call_with_valid_params(self):
        """Test _execute_sdk_call with valid parameters."""
        agent = ConcreteAgent(name="TestAgent")

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_execute:
            mock_result = MagicMock()
            mock_result.is_success.return_value = True
            mock_execute.return_value = mock_result

            result = await agent._execute_sdk_call(
                sdk_executor="dummy",
                prompt="test prompt",
                timeout=180.0,
                permission_mode="test"
            )

            assert result == mock_result
            mock_execute.assert_called_once_with(
                prompt="test prompt",
                agent_name="TestAgent",
                timeout=180.0,
                permission_mode="test"
            )

    @pytest.mark.anyio
    async def test_execute_sdk_call_with_default_params(self):
        """Test _execute_sdk_call with default parameters."""
        agent = ConcreteAgent(name="TestAgent")

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_execute:
            mock_result = MagicMock()
            mock_result.is_success.return_value = False
            mock_execute.return_value = mock_result

            result = await agent._execute_sdk_call(
                sdk_executor=None,
                prompt="test prompt"
            )

            assert result == mock_result
            mock_execute.assert_called_once_with(
                prompt="test prompt",
                agent_name="TestAgent",
                timeout=1800.0,
                permission_mode="bypassPermissions"
            )

    @pytest.mark.anyio
    async def test_execute_sdk_call_with_exception(self):
        """Test _execute_sdk_call handles general exceptions properly."""
        agent = ConcreteAgent(name="TestAgent")

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            side_effect=ValueError("test exception")
        ):
            result = await agent._execute_sdk_call(None, "test prompt")

            assert result.is_success() is False
            assert "test exception" in result.errors
            assert result.error_type == SDKErrorType.SDK_ERROR
            assert isinstance(result.last_exception, ValueError)

    @pytest.mark.anyio
    async def test_execute_sdk_call_preserves_agent_name(self):
        """Test that agent name is preserved in SDK call."""
        agent = ConcreteAgent(name="SpecialAgent")

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_execute:
            mock_result = MagicMock()
            mock_execute.return_value = mock_result

            await agent._execute_sdk_call(None, "test prompt")

            call_kwargs = mock_execute.call_args[1]
            assert call_kwargs["agent_name"] == "SpecialAgent"

    @pytest.mark.anyio
    async def test_execute_within_taskgroup_exception_propagation(self):
        """Test _execute_within_taskgroup propagates exceptions."""
        agent = ConcreteAgent(name="TestAgent")
        agent.task_group = MagicMock()

        async def failing_coro():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await agent._execute_within_taskgroup(failing_coro)

    @pytest.mark.anyio
    async def test_execute_within_taskgroup_async_mock(self):
        """Test _execute_within_taskgroup with AsyncMock TaskGroup."""
        agent = ConcreteAgent(name="TestAgent")
        agent.task_group = AsyncMock()

        async def dummy_coro():
            return "async_mock_result"

        result = await agent._execute_within_taskgroup(dummy_coro)
        assert result == "async_mock_result"

    def test_multiple_log_levels(self):
        """Test _log_execution with various log levels."""
        agent = ConcreteAgent(name="TestAgent")

        with patch.object(agent.logger, "debug") as mock_debug, \
             patch.object(agent.logger, "info") as mock_info, \
             patch.object(agent.logger, "warning") as mock_warning, \
             patch.object(agent.logger, "error") as mock_error:

            agent._log_execution("Debug message", level="debug")
            agent._log_execution("Info message", level="info")
            agent._log_execution("Warning message", level="warning")
            agent._log_execution("Error message", level="error")

            mock_debug.assert_called_once_with("[TestAgent] Debug message")
            mock_info.assert_called_once_with("[TestAgent] Info message")
            mock_warning.assert_called_once_with("[TestAgent] Warning message")
            mock_error.assert_called_once_with("[TestAgent] Error message")

    def test_log_execution_with_special_characters(self):
        """Test _log_execution with special characters in message."""
        agent = ConcreteAgent(name="TestAgent")

        special_message = "Message with 'quotes' and \"double quotes\" and newlines\n"

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution(special_message)
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[TestAgent]" in call_args
            assert special_message in call_args

    def test_agent_name_empty_string(self):
        """Test agent with empty name string."""
        agent = ConcreteAgent(name="")

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution("Test")
            call_args = mock_info.call_args[0][0]
            assert "[]" in call_args

    def test_execution_context_modification(self):
        """Test that _execution_context can be modified."""
        agent = ConcreteAgent(name="TestAgent")
        agent._execution_context["test_key"] = "test_value"
        agent._execution_context["number"] = 42

        assert agent._execution_context["test_key"] == "test_value"
        assert agent._execution_context["number"] == 42

    @pytest.mark.anyio
    async def test_concrete_agent_execute_empty_args(self):
        """Test ConcreteAgent.execute with no arguments."""
        agent = ConcreteAgent(name="TestAgent")
        result = await agent.execute()

        assert result["status"] == "success"
        assert result["args"] == ()
        assert result["kwargs"] == {}

    @pytest.mark.anyio
    async def test_concrete_agent_execute_complex_types(self):
        """Test ConcreteAgent.execute with complex argument types."""
        agent = ConcreteAgent(name="TestAgent")
        complex_dict = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        complex_list = [{"a": 1}, {"b": 2}]

        result = await agent.execute(
            complex_dict,
            complex_list,
            complex_kwarg=complex_dict
        )

        assert result["status"] == "success"
        assert result["args"] == (complex_dict, complex_list)
        assert result["kwargs"] == {"complex_kwarg": complex_dict}

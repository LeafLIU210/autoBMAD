"""Integration tests for spec automation components.

Tests the interaction between BaseAgent, SDKExecutor, CancellationManager,
and StateManager to ensure they work together correctly.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType
from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager


class TestAgent(BaseAgent):
    """Test agent for integration testing."""

    async def execute(self, *args, **kwargs):
        """Execute the agent."""
        return {"status": "success", "args": args, "kwargs": kwargs}


class TestIntegration:
    """Integration tests for component interaction."""

    @pytest.mark.anyio
    async def test_base_agent_with_sdk_executor(self):
        """Test BaseAgent working with SDKExecutor."""
        # Create components
        agent = TestAgent(name="IntegrationAgent")
        executor = SDKExecutor()

        # Mock SDK execution
        async def mock_sdk_func():
            yield {"type": "progress", "step": 1}
            yield {"type": "result", "data": "test data"}

        def target_predicate(msg):
            return msg.get("type") == "result"

        # Execute SDK call through agent
        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_sdk:
            mock_result = SDKResult(
                has_target_result=True,
                cleanup_completed=True,
                messages=[{"type": "result", "data": "test"}],
                target_message={"type": "result", "data": "test"},
                agent_name="IntegrationAgent",
            )
            mock_sdk.return_value = mock_result

            result = await agent._execute_sdk_call(
                sdk_executor=executor,
                prompt="test prompt"
            )

            assert result.is_success() is True
            assert result.agent_name == "IntegrationAgent"

    @pytest.mark.anyio
    async def test_cancellation_with_sdk_executor(self):
        """Test cancellation management during SDK execution."""
        executor = SDKExecutor()
        assert executor.cancel_manager.get_active_calls_count() == 0

        # Start execution
        async def mock_sdk_func():
            await asyncio.sleep(0.1)
            yield {"type": "result"}

        def target_predicate(msg):
            return True

        # This should work
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent"
        )

        assert result.is_success() is True
        assert executor.cancel_manager.get_active_calls_count() == 0

    @pytest.mark.anyio
    async def test_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        agent = TestAgent(name="LifecycleAgent")

        # Test initialization
        assert agent.name == "LifecycleAgent"
        assert agent.task_group is None

        # Test context validation
        assert agent._validate_execution_context() is False

        # Set task group
        mock_tg = MagicMock()
        agent.set_task_group(mock_tg)
        assert agent._validate_execution_context() is True

        # Test execution
        result = await agent.execute("arg1", key="value")
        assert result["status"] == "success"

    @pytest.mark.anyio
    async def test_multiple_agents_concurrent(self):
        """Test multiple agents running concurrently."""
        agents = [
            TestAgent(name=f"Agent{i}")
            for i in range(5)
        ]

        async def run_agent(agent):
            return await agent.execute(f"arg_for_{agent.name}")

        results = await asyncio.gather(*[run_agent(agent) for agent in agents])

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["status"] == "success"
            assert f"arg_for_Agent{i}" in result["args"]

    @pytest.mark.anyio
    async def test_sdk_result_state_propagation(self):
        """Test that SDK result state is properly propagated."""
        agent = TestAgent(name="StateAgent")

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_sdk:
            # Test success case
            mock_sdk.return_value = SDKResult(
                has_target_result=True,
                cleanup_completed=True,
                duration_seconds=1.5,
                session_id="test-session",
                agent_name="StateAgent",
                messages=[{"type": "data"}],
                target_message={"type": "data"},
                error_type=SDKErrorType.SUCCESS,
                errors=[],
            )

            result = await agent._execute_sdk_call(None, "test prompt")

            assert result.is_success() is True
            assert result.duration_seconds == 1.5
            assert result.session_id == "test-session"
            assert len(result.messages) == 1

    @pytest.mark.anyio
    async def test_error_handling_across_components(self):
        """Test error handling across multiple components."""
        agent = TestAgent(name="ErrorAgent")

        # Simulate SDK error
        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
        ) as mock_sdk:
            mock_sdk.side_effect = RuntimeError("Simulated SDK error")

            result = await agent._execute_sdk_call(None, "test prompt")

            assert result.is_success() is False
            assert result.has_sdk_error() is True
            assert "Simulated SDK error" in result.errors

    @pytest.mark.anyio
    async def test_cancellation_manager_tracking(self):
        """Test CancellationManager properly tracks calls."""
        manager = CancellationManager()

        # Initially no active calls
        assert manager.get_active_calls_count() == 0

        # Register a call
        manager.register_call("call-1", "Agent1")
        assert manager.get_active_calls_count() == 1

        # Mark as cancelled
        manager.request_cancel("call-1")
        call_info = manager.get_call_info("call-1")
        assert call_info.cancel_requested is True

        # Mark cleanup completed
        manager.mark_cleanup_completed("call-1")
        call_info = manager.get_call_info("call-1")
        assert call_info.cleanup_completed is True

        # Unregister
        manager.unregister_call("call-1")
        assert manager.get_active_calls_count() == 0

    @pytest.mark.anyio
    async def test_executor_with_target_result(self):
        """Test SDKExecutor properly handles target results."""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "progress", "step": 1}
            yield {"type": "progress", "step": 2}
            yield {"type": "final_result", "value": 42}

        def target_predicate(msg):
            return msg.get("type") == "final_result"

        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TargetAgent"
        )

        assert result.is_success() is True
        assert result.has_target_result is True
        assert result.target_message["value"] == 42
        assert len(result.messages) == 3

    @pytest.mark.anyio
    async def test_executor_without_target_result(self):
        """Test SDKExecutor handles missing target result."""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "progress", "step": 1}
            yield {"type": "progress", "step": 2}

        def target_predicate(msg):
            return msg.get("type") == "final_result"

        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="NoTargetAgent"
        )

        assert result.is_success() is False
        assert result.has_target_result is False
        assert "No target result found" in result.errors

    @pytest.mark.anyio
    async def test_executor_records_timing(self):
        """Test SDKExecutor properly records execution timing."""
        executor = SDKExecutor()

        async def mock_sdk_func():
            await asyncio.sleep(0.05)
            yield {"type": "result"}

        def target_predicate(msg):
            return msg.get("type") == "result"

        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TimingAgent"
        )

        assert result.duration_seconds >= 0.05
        assert result.duration_seconds < 1.0

    @pytest.mark.anyio
    async def test_agent_logging_integration(self):
        """Test that agent logging works correctly in integration."""
        agent = TestAgent(name="LoggingAgent")

        with patch.object(agent.logger, "info") as mock_info:
            agent._log_execution("Test integration message")
            mock_info.assert_called_once_with("[LoggingAgent] Test integration message")

    @pytest.mark.anyio
    async def test_context_manager_cancellation(self):
        """Test CancellationManager context manager with cancellation."""
        manager = CancellationManager()

        async with manager.track_sdk_execution("call-1", "ContextAgent", "test-op"):
            assert manager.get_active_calls_count() == 1
            call_info = manager.get_call_info("call-1")
            assert call_info is not None

        # After context, cleanup should be marked
        call_info = manager.get_call_info("call-1")
        assert call_info.cleanup_completed is True

    @pytest.mark.anyio
    async def test_error_state_propagation(self):
        """Test that error states propagate correctly through components."""
        agent = TestAgent(name="ErrorPropagateAgent")

        # Test with different error types
        error_types = [
            SDKErrorType.CANCELLED,
            SDKErrorType.TIMEOUT,
            SDKErrorType.SDK_ERROR,
            SDKErrorType.UNKNOWN,
        ]

        for error_type in error_types:
            with patch(
                "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
            ) as mock_sdk:
                mock_sdk.return_value = SDKResult(
                    has_target_result=False,
                    cleanup_completed=True,
                    error_type=error_type,
                    errors=[f"Test error for {error_type.value}"],
                    agent_name="ErrorPropagateAgent",
                )

                result = await agent._execute_sdk_call(None, "test prompt")

                assert result.is_success() is False
                assert result.error_type == error_type

    @pytest.mark.anyio
    async def test_complex_scenario(self):
        """Test a complex scenario with multiple interacting components."""
        # Create multiple agents
        agents = [TestAgent(name=f"ComplexAgent{i}") for i in range(3)]

        # Create executor
        executor = SDKExecutor()

        # Create cancellation manager
        cancel_manager = CancellationManager()

        # Simulate a complex workflow
        async def workflow(agent):
            # Register call
            cancel_manager.register_call(f"call-{agent.name}", agent.name)

            # Execute SDK call
            with patch(
                "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call"
            ) as mock_sdk:
                mock_sdk.return_value = SDKResult(
                    has_target_result=True,
                    cleanup_completed=True,
                    agent_name=agent.name,
                    messages=[{"type": "result", "agent": agent.name}],
                    target_message={"type": "result", "agent": agent.name},
                )

                result = await agent._execute_sdk_call(
                    executor,
                    f"prompt for {agent.name}"
                )

                # Mark as done
                cancel_manager.mark_target_result_found(f"call-{agent.name}")
                cancel_manager.mark_cleanup_completed(f"call-{agent.name}")
                cancel_manager.unregister_call(f"call-{agent.name}")

                return result

        # Run workflow for all agents
        results = await asyncio.gather(*[workflow(agent) for agent in agents])

        # Verify all succeeded
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.is_success() is True
            assert f"ComplexAgent{i}" in result.agent_name

        # Verify cancellation manager is clean
        assert cancel_manager.get_active_calls_count() == 0

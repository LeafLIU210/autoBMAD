"""Tests for SDKExecutor.

Comprehensive test suite for SDK execution functionality.
"""

from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class TestSDKExecutor:
    """Tests for SDKExecutor class."""

    def test_initialization(self):
        """Test SDKExecutor initialization."""
        executor = SDKExecutor()
        assert executor.cancel_manager is not None
        assert executor.cancel_manager.get_active_calls_count() == 0

    @pytest.mark.anyio
    async def test_execute_with_async_generator_success(self):
        """Test execute with async generator that finds target."""

        async def mock_sdk_func() -> AsyncIterator[dict[str, Any]]:
            yield {"type": "progress", "content": "step1"}
            yield {"type": "progress", "content": "step2"}
            yield {"type": "result", "content": "final"}

        def target_predicate(msg: Any) -> bool:
            return isinstance(msg, dict) and msg.get("type") == "result"

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        assert result.has_target_result is True
        assert result.cleanup_completed is True
        assert result.is_success() is True
        assert len(result.messages) == 3
        assert result.target_message == {"type": "result", "content": "final"}
        assert result.agent_name == "TestAgent"

    @pytest.mark.anyio
    async def test_execute_with_async_generator_no_target(self):
        """Test execute with async generator that does not find target."""

        async def mock_sdk_func() -> AsyncIterator[dict[str, Any]]:
            yield {"type": "progress", "content": "step1"}
            yield {"type": "progress", "content": "step2"}

        def target_predicate(msg: Any) -> bool:
            return isinstance(msg, dict) and msg.get("type") == "result"

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        assert result.has_target_result is False
        assert result.target_message is None
        assert "No target result found" in result.errors

    @pytest.mark.anyio
    async def test_execute_with_coroutine_function_success(self):
        """Test execute with coroutine function returning bool True."""

        async def mock_sdk_func() -> bool:
            return True

        def target_predicate(msg: Any) -> bool:
            return isinstance(msg, dict) and msg.get("result") is True

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        assert result.has_target_result is True
        assert len(result.messages) == 1
        assert result.messages[0]["result"] is True

    @pytest.mark.anyio
    async def test_execute_with_coroutine_function_failure(self):
        """Test execute with coroutine function returning bool False."""

        async def mock_sdk_func() -> bool:
            return False

        def target_predicate(msg: Any) -> bool:
            return isinstance(msg, dict) and msg.get("result") is True

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        assert result.has_target_result is False
        assert len(result.messages) == 1
        assert result.messages[0]["result"] is False

    @pytest.mark.anyio
    async def test_execute_records_duration(self):
        """Test that execute records duration correctly."""

        async def mock_sdk_func() -> AsyncIterator[dict[str, Any]]:
            await anyio.sleep(0.1)
            yield {"type": "result"}

        def target_predicate(msg: Any) -> bool:
            return True

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        assert result.duration_seconds >= 0.1

    @pytest.mark.anyio
    async def test_execute_generates_session_id(self):
        """Test that execute generates proper session ID."""

        async def mock_sdk_func() -> AsyncIterator[dict[str, Any]]:
            yield {"type": "result"}

        def target_predicate(msg: Any) -> bool:
            return True

        executor = SDKExecutor()
        result = await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="MyAgent",
        )

        assert "MyAgent-" in result.session_id
        assert len(result.session_id) > len("MyAgent-")

    @pytest.mark.anyio
    async def test_execute_cancel_manager_state(self):
        """Test that cancel manager state is properly managed."""
        executor = SDKExecutor()
        assert executor.cancel_manager.get_active_calls_count() == 0

        async def mock_sdk_func() -> AsyncIterator[dict[str, Any]]:
            yield {"type": "result"}

        def target_predicate(msg: Any) -> bool:
            return True

        await executor.execute(
            mock_sdk_func,
            target_predicate,
            agent_name="TestAgent",
        )

        # Call should be unregistered after execution
        assert executor.cancel_manager.get_active_calls_count() == 0

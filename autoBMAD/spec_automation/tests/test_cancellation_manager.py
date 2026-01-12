"""Tests for CancellationManager and CallInfo.

Comprehensive test suite for cancellation management functionality.
"""

import time
from unittest.mock import patch, MagicMock

import anyio
import pytest

from autoBMAD.epic_automation.core.cancellation_manager import (
    CancellationManager,
    CallInfo,
)


class TestCallInfo:
    """Tests for CallInfo dataclass."""

    def test_default_values(self):
        """Test CallInfo default values."""
        info = CallInfo(
            call_id="test-id",
            agent_name="TestAgent",
            start_time=1000.0,
        )
        assert info.call_id == "test-id"
        assert info.agent_name == "TestAgent"
        assert info.start_time == 1000.0
        assert info.cancel_requested is False
        assert info.cleanup_completed is False
        assert info.has_target_result is False
        assert info.errors == []

    def test_full_initialization(self):
        """Test CallInfo with all fields initialized."""
        info = CallInfo(
            call_id="full-id",
            agent_name="FullAgent",
            start_time=2000.0,
            cancel_requested=True,
            cleanup_completed=True,
            has_target_result=True,
            errors=["error1", "error2"],
        )
        assert info.cancel_requested is True
        assert info.cleanup_completed is True
        assert info.has_target_result is True
        assert info.errors == ["error1", "error2"]


class TestCancellationManager:
    """Tests for CancellationManager class."""

    def test_initialization(self):
        """Test CancellationManager initialization."""
        manager = CancellationManager()
        assert manager.get_active_calls_count() == 0

    def test_register_call(self):
        """Test registering a new call."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")

        assert manager.get_active_calls_count() == 1
        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.call_id == "call-1"
        assert call_info.agent_name == "Agent1"
        assert call_info.cancel_requested is False
        assert call_info.cleanup_completed is False

    def test_register_multiple_calls(self):
        """Test registering multiple calls."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.register_call("call-2", "Agent2")
        manager.register_call("call-3", "Agent3")

        assert manager.get_active_calls_count() == 3

    def test_request_cancel(self):
        """Test requesting cancel for a call."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.request_cancel("call-1")

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.cancel_requested is True

    def test_request_cancel_nonexistent(self):
        """Test requesting cancel for nonexistent call (should not raise)."""
        manager = CancellationManager()
        # Should not raise
        manager.request_cancel("nonexistent-call")

    def test_mark_cleanup_completed(self):
        """Test marking cleanup as completed."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.mark_cleanup_completed("call-1")

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.cleanup_completed is True

    def test_mark_cleanup_completed_nonexistent(self):
        """Test marking cleanup for nonexistent call (should not raise)."""
        manager = CancellationManager()
        # Should not raise
        manager.mark_cleanup_completed("nonexistent-call")

    def test_mark_target_result_found(self):
        """Test marking target result as found."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.mark_target_result_found("call-1")

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.has_target_result is True

    def test_mark_target_result_found_nonexistent(self):
        """Test marking target for nonexistent call (should not raise)."""
        manager = CancellationManager()
        # Should not raise
        manager.mark_target_result_found("nonexistent-call")

    def test_unregister_call(self):
        """Test unregistering a call."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        assert manager.get_active_calls_count() == 1

        manager.unregister_call("call-1")
        assert manager.get_active_calls_count() == 0
        assert manager.get_call_info("call-1") is None

    def test_unregister_nonexistent_call(self):
        """Test unregistering nonexistent call (should not raise)."""
        manager = CancellationManager()
        # Should not raise
        manager.unregister_call("nonexistent-call")

    def test_get_call_info_nonexistent(self):
        """Test getting info for nonexistent call."""
        manager = CancellationManager()
        assert manager.get_call_info("nonexistent") is None

    @pytest.mark.anyio
    async def test_track_sdk_execution_context_manager(self):
        """Test track_sdk_execution as context manager."""
        manager = CancellationManager()

        async with manager.track_sdk_execution("call-1", "Agent1", "test-op"):
            # Inside context: call should be registered
            assert manager.get_active_calls_count() == 1
            call_info = manager.get_call_info("call-1")
            assert call_info is not None

        # After context: cleanup should be marked completed
        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.cleanup_completed is True

    @pytest.mark.anyio
    async def test_track_sdk_execution_with_exception(self):
        """Test track_sdk_execution marks cleanup even on exception."""
        manager = CancellationManager()

        with pytest.raises(ValueError):
            async with manager.track_sdk_execution("call-1", "Agent1"):
                raise ValueError("test error")

        # Cleanup should still be marked
        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.cleanup_completed is True

    @pytest.mark.anyio
    async def test_confirm_safe_to_proceed_success(self):
        """Test confirm_safe_to_proceed returns True when conditions met."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.request_cancel("call-1")
        manager.mark_cleanup_completed("call-1")

        result = await manager.confirm_safe_to_proceed("call-1", timeout=1.0)
        assert result is True

    @pytest.mark.anyio
    async def test_confirm_safe_to_proceed_timeout(self):
        """Test confirm_safe_to_proceed times out when conditions not met."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        # Only request cancel, don't mark cleanup

        manager.request_cancel("call-1")

        result = await manager.confirm_safe_to_proceed("call-1", timeout=0.3)
        assert result is False

    @pytest.mark.anyio
    async def test_confirm_safe_to_proceed_nonexistent_call(self):
        """Test confirm_safe_to_proceed for nonexistent call."""
        manager = CancellationManager()

        result = await manager.confirm_safe_to_proceed("nonexistent", timeout=0.3)
        assert result is False

    def test_call_timing(self):
        """Test that start_time is recorded correctly."""
        manager = CancellationManager()
        before = time.time()
        manager.register_call("call-1", "Agent1")
        after = time.time()

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert before <= call_info.start_time <= after

    def test_multiple_operations_on_same_call(self):
        """Test multiple operations on the same call."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")

        # Perform multiple operations
        manager.mark_target_result_found("call-1")
        manager.request_cancel("call-1")
        manager.mark_cleanup_completed("call-1")

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.has_target_result is True
        assert call_info.cancel_requested is True
        assert call_info.cleanup_completed is True

    def test_register_overwrites_existing(self):
        """Test that registering same call_id overwrites existing."""
        manager = CancellationManager()
        manager.register_call("call-1", "Agent1")
        manager.request_cancel("call-1")

        # Re-register with same ID
        manager.register_call("call-1", "Agent2")

        call_info = manager.get_call_info("call-1")
        assert call_info is not None
        assert call_info.agent_name == "Agent2"
        # Should be reset
        assert call_info.cancel_requested is False

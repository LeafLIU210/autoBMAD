"""
Test Suite for SDK Wrapper Cancel Fix (Event-based Signaling)
Tests the improved cancellation handling using Event signaling instead of task cancellation
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the modules to test
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK, SDKMessageTracker


class TestSDKWrapperCancelFix:
    """Test cases for SDK wrapper cancellation handling improvements."""

    @pytest.fixture
    def mock_options(self):
        """Create mock ClaudeAgentOptions."""
        mock = Mock()
        mock.permission_mode = "bypassPermissions"
        mock.cwd = str(Path.cwd())
        return mock

    @pytest.fixture
    def mock_log_manager(self):
        """Create mock log manager."""
        mock = Mock()
        mock.write_sdk_message = Mock()
        return mock

    @pytest.mark.asyncio
    async def test_cancelled_execution_handling(self, mock_options, mock_log_manager):
        """Test that cancelled executions are handled gracefully without exceptions."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=10.0, log_manager=mock_log_manager)

        # Mock the generator to raise CancelledError
        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        mock_generator.__anext__.side_effect = asyncio.CancelledError("Test cancellation")

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act
            result = await sdk.execute()

            # Assert
            assert result is False, "Cancelled execution should return False"
            # Verify no exception was raised

    @pytest.mark.asyncio
    async def test_cancel_scope_error_handling(self, mock_options, mock_log_manager):
        """Test that cancel scope errors are handled gracefully."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=10.0, log_manager=mock_log_manager)

        # Mock the generator to raise RuntimeError with cancel scope
        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        mock_generator.__anext__.side_effect = RuntimeError("Attempted to exit cancel scope in a different task")

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act
            result = await sdk.execute()

            # Assert
            assert result is False, "Cancel scope error should return False"
            # Verify no exception was raised

    @pytest.mark.asyncio
    async def test_event_loop_closed_handling(self, mock_options, mock_log_manager):
        """Test that event loop closed errors are handled gracefully."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=10.0, log_manager=mock_log_manager)

        # Mock the generator to raise RuntimeError with event loop closed
        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        mock_generator.__anext__.side_effect = RuntimeError("Event loop is closed")

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act
            result = await sdk.execute()

            # Assert
            assert result is False, "Event loop closed error should return False"
            # Verify no exception was raised

    @pytest.mark.asyncio
    async def test_graceful_cleanup_on_cancellation(self, mock_options, mock_log_manager):
        """Test that cleanup is performed gracefully on cancellation using Event signaling."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=10.0, log_manager=mock_log_manager)

        # Mock the message tracker
        mock_tracker = Mock()
        mock_tracker.update_message = Mock()
        mock_tracker._stop_event = Mock()
        mock_tracker._stop_event.is_set.return_value = False
        mock_tracker._display_task = Mock()
        mock_tracker._display_task.done.return_value = False

        sdk.message_tracker = mock_tracker

        # Mock the generator to raise CancelledError
        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        mock_generator.__anext__.side_effect = asyncio.CancelledError("Test cancellation")
        mock_generator.aclose = AsyncMock()

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act
            result = await sdk.execute()

            # Assert
            assert result is False
            # Verify cleanup was called
            mock_tracker.update_message.assert_called_with("Execution cancelled by user/system", "CANCELLED")
            mock_tracker._stop_event.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_normal_execution_not_affected(self, mock_options, mock_log_manager):
        """Test that normal execution is not affected by cancellation handling."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=10.0, log_manager=mock_log_manager)

        # Mock successful execution
        mock_result_message = Mock()
        mock_result_message.__class__.__name__ = "ResultMessage"
        mock_result_message.is_error = False
        mock_result_message.result = "Success result"

        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        mock_generator.__anext__.side_effect = [mock_result_message, StopAsyncIteration]

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act
            result = await sdk.execute()

            # Assert
            assert result is True, "Normal execution should return True"

    @pytest.mark.asyncio
    async def test_timeout_handling_still_works(self, mock_options, mock_log_manager):
        """Test that timeout handling still works with new cancellation logic."""
        # Arrange
        prompt = "test prompt"
        sdk = SafeClaudeSDK(prompt, mock_options, timeout=0.1, log_manager=mock_log_manager)  # Very short timeout

        # Mock slow execution
        mock_generator = AsyncMock()
        mock_generator.__aiter__.return_value = mock_generator
        async def slow_next():
            await asyncio.sleep(1)  # Longer than timeout
            return Mock()
        mock_generator.__anext__ = slow_next

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.return_value = mock_generator

            # Act & Assert
            with pytest.raises(TimeoutError):
                await sdk.execute()


class TestSDKMessageTrackerCancelFix:
    """Test cases for SDK message tracker cancellation improvements using Event signaling."""

    @pytest.mark.asyncio
    async def test_periodic_display_graceful_cancellation(self):
        """Test that periodic display task handles cancellation gracefully using Event signal."""
        # Arrange
        tracker = SDKMessageTracker()

        # Act - start periodic display
        await tracker.start_periodic_display()

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop it gracefully using Event signal
        await tracker.stop_periodic_display()

        # Assert - no exceptions should be raised
        assert tracker._display_task is None or tracker._display_task.done()

    @pytest.mark.asyncio
    async def test_stop_periodic_display_with_timeout(self):
        """Test stopping periodic display with timeout using Event signaling."""
        # Arrange
        tracker = SDKMessageTracker()

        # Create a task that won't complete immediately
        async def slow_task():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                await asyncio.sleep(0.5)  # Simulate cleanup delay
                raise

        tracker._display_task = asyncio.ensure_future(slow_task())

        # Act - stop with short timeout
        start_time = asyncio.get_event_loop().time()
        await tracker.stop_periodic_display(timeout=0.1)
        end_time = asyncio.get_event_loop().time()

        # Assert - should complete within timeout (Event signal allows natural exit)
        assert end_time - start_time < 0.3, "Stop should respect timeout"
        assert tracker._display_task is None, "Task should be cleaned up"

    @pytest.mark.asyncio
    async def test_event_signal_mechanism(self):
        """Test that Event signal mechanism works correctly."""
        # Arrange
        tracker = SDKMessageTracker()

        # Start periodic display
        await tracker.start_periodic_display()

        # Verify stop event is initially not set
        assert not tracker._stop_event.is_set()

        # Stop it using Event signal
        await tracker.stop_periodic_display()

        # Verify stop event is now set
        assert tracker._stop_event.is_set()

    @pytest.mark.asyncio
    async def test_rapid_start_stop_cycles(self):
        """Test rapid start/stop cycles without cancel scope errors."""
        # Arrange
        tracker = SDKMessageTracker()

        # Act - perform multiple start/stop cycles
        for i in range(10):
            await tracker.start_periodic_display()
            await asyncio.sleep(0.01)  # Brief run
            await tracker.stop_periodic_display()
            await asyncio.sleep(0.01)  # Brief pause

        # Assert - no exceptions should be raised
        assert tracker._display_task is None or tracker._display_task.done()

    @pytest.mark.asyncio
    async def test_ensure_future_vs_create_task(self):
        """Test that ensure_future is used instead of create_task."""
        # Arrange
        tracker = SDKMessageTracker()

        # Act - start periodic display
        await tracker.start_periodic_display()

        # Assert - verify task was created using ensure_future
        assert tracker._display_task is not None
        assert not tracker._display_task.done()

        # Verify it's a Task instance
        assert isinstance(tracker._display_task, asyncio.Task)

        # Clean up
        await tracker.stop_periodic_display()

    @pytest.mark.asyncio
    async def test_no_cancel_scope_error_in_rapid_cycles(self):
        """Test that no cancel scope errors occur in rapid start/stop cycles."""
        # Arrange
        tracker = SDKMessageTracker()
        errors = []

        # Custom error handler
        def handle_exception(loop, context):
            errors.append(context.get('exception'))

        # Act - perform many rapid cycles
        original_handler = asyncio.get_event_loop().get_exception_handler()
        asyncio.get_event_loop().set_exception_handler(handle_exception)

        try:
            for i in range(20):
                await tracker.start_periodic_display()
                await asyncio.sleep(0.001)  # Very brief
                await tracker.stop_periodic_display()
                await asyncio.sleep(0.001)

            # Wait a bit for any pending tasks
            await asyncio.sleep(0.1)

            # Assert - no cancel scope errors
            cancel_scope_errors = [e for e in errors if e and 'cancel scope' in str(e)]
            assert len(cancel_scope_errors) == 0, f"Found cancel scope errors: {cancel_scope_errors}"

        finally:
            # Restore original handler
            asyncio.get_event_loop().set_exception_handler(original_handler)

    @pytest.mark.asyncio
    async def test_stop_event_natural_exit(self):
        """Test that tasks exit naturally when stop_event is set."""
        # Arrange
        tracker = SDKMessageTracker()

        # Create a custom task that checks the event
        exit_count = 0

        async def custom_display():
            nonlocal exit_count
            while not tracker._stop_event.is_set():
                await asyncio.sleep(0.01)
            exit_count += 1

        # Start the task
        tracker._display_task = asyncio.ensure_future(custom_display())

        # Let it run briefly
        await asyncio.sleep(0.05)

        # Set stop event (simulating natural exit)
        tracker._stop_event.set()

        # Wait for task to exit naturally
        await asyncio.sleep(0.1)

        # Assert - task should exit naturally without cancellation
        assert tracker._display_task.done()
        assert exit_count == 1, "Task should have exited naturally"

    @pytest.mark.asyncio
    async def test_concurrent_stop_attempts(self):
        """Test multiple concurrent stop attempts don't cause issues."""
        # Arrange
        tracker = SDKMessageTracker()

        # Start periodic display
        await tracker.start_periodic_display()

        # Act - multiple concurrent stop attempts
        await asyncio.gather(
            tracker.stop_periodic_display(),
            tracker.stop_periodic_display(),
            tracker.stop_periodic_display()
        )

        # Assert - should complete without errors
        assert tracker._display_task is None or tracker._display_task.done()

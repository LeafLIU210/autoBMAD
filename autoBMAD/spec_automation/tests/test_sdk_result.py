"""Tests for SDKResult and SDKErrorType.

Comprehensive test suite for SDK execution result data structures.
"""

import pytest

from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class TestSDKErrorType:
    """Tests for SDKErrorType enum."""

    def test_error_type_values(self):
        """Test all SDKErrorType enum values."""
        assert SDKErrorType.SUCCESS.value == "success"
        assert SDKErrorType.CANCELLED.value == "cancelled"
        assert SDKErrorType.TIMEOUT.value == "timeout"
        assert SDKErrorType.SDK_ERROR.value == "sdk_error"
        assert SDKErrorType.CANCEL_SCOPE_ERROR.value == "cancel_scope_error"
        assert SDKErrorType.UNKNOWN.value == "unknown"

    def test_error_type_enum_members(self):
        """Test SDKErrorType has all expected members."""
        expected_members = {
            "SUCCESS",
            "CANCELLED",
            "TIMEOUT",
            "SDK_ERROR",
            "CANCEL_SCOPE_ERROR",
            "UNKNOWN",
        }
        actual_members = {member.name for member in SDKErrorType}
        assert actual_members == expected_members


class TestSDKResult:
    """Tests for SDKResult dataclass."""

    def test_default_values(self):
        """Test SDKResult default values."""
        result = SDKResult()
        assert result.has_target_result is False
        assert result.cleanup_completed is False
        assert result.duration_seconds == 0.0
        assert result.session_id == ""
        assert result.agent_name == ""
        assert result.messages == []
        assert result.target_message is None
        assert result.error_type == SDKErrorType.SUCCESS
        assert result.errors == []
        assert result.last_exception is None

    def test_is_success_both_true(self):
        """Test is_success() returns True when both conditions are met."""
        result = SDKResult(has_target_result=True, cleanup_completed=True)
        assert result.is_success() is True

    def test_is_success_only_target(self):
        """Test is_success() returns False when only has_target_result is True."""
        result = SDKResult(has_target_result=True, cleanup_completed=False)
        assert result.is_success() is False

    def test_is_success_only_cleanup(self):
        """Test is_success() returns False when only cleanup_completed is True."""
        result = SDKResult(has_target_result=False, cleanup_completed=True)
        assert result.is_success() is False

    def test_is_success_both_false(self):
        """Test is_success() returns False when both conditions are False."""
        result = SDKResult(has_target_result=False, cleanup_completed=False)
        assert result.is_success() is False

    def test_is_cancelled(self):
        """Test is_cancelled() method."""
        result = SDKResult(error_type=SDKErrorType.CANCELLED)
        assert result.is_cancelled() is True

        result_success = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result_success.is_cancelled() is False

    def test_is_timeout(self):
        """Test is_timeout() method."""
        result = SDKResult(error_type=SDKErrorType.TIMEOUT)
        assert result.is_timeout() is True

        result_success = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result_success.is_timeout() is False

    def test_has_cancel_scope_error(self):
        """Test has_cancel_scope_error() method."""
        result = SDKResult(error_type=SDKErrorType.CANCEL_SCOPE_ERROR)
        assert result.has_cancel_scope_error() is True

        result_success = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result_success.has_cancel_scope_error() is False

    def test_has_sdk_error(self):
        """Test has_sdk_error() method."""
        result = SDKResult(error_type=SDKErrorType.SDK_ERROR)
        assert result.has_sdk_error() is True

        result_success = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result_success.has_sdk_error() is False

    def test_is_unknown_error(self):
        """Test is_unknown_error() method."""
        result = SDKResult(error_type=SDKErrorType.UNKNOWN)
        assert result.is_unknown_error() is True

        result_success = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result_success.is_unknown_error() is False

    def test_get_error_summary_success(self):
        """Test get_error_summary() for successful result."""
        result = SDKResult(has_target_result=True, cleanup_completed=True)
        assert result.get_error_summary() == "Success"

    def test_get_error_summary_no_errors(self):
        """Test get_error_summary() with error type but no error messages."""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.TIMEOUT,
            errors=[],
        )
        assert result.get_error_summary() == "timeout"

    def test_get_error_summary_with_errors(self):
        """Test get_error_summary() with error messages."""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Error 1", "Error 2", "Error 3"],
        )
        assert result.get_error_summary() == "sdk_error (3 errors)"

    def test_str_representation_success(self):
        """Test __str__() for successful result."""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="TestAgent",
        )
        str_repr = str(result)
        assert "session=test-session" in str_repr
        assert "agent=TestAgent" in str_repr
        assert "success=True" in str_repr
        assert "duration=1.50s" in str_repr

    def test_str_representation_failure(self):
        """Test __str__() for failed result."""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.SDK_ERROR,
            session_id="test-session",
            agent_name="TestAgent",
        )
        str_repr = str(result)
        assert "success=False" in str_repr

    def test_messages_list(self):
        """Test messages list handling."""
        messages = ["msg1", {"type": "result"}, 123]
        result = SDKResult(messages=messages)
        assert result.messages == messages
        assert len(result.messages) == 3

    def test_target_message(self):
        """Test target_message field."""
        target = {"type": "ResultMessage", "content": "test"}
        result = SDKResult(target_message=target)
        assert result.target_message == target

    def test_last_exception(self):
        """Test last_exception field."""
        exc = ValueError("test error")
        result = SDKResult(last_exception=exc)
        assert result.last_exception == exc
        assert isinstance(result.last_exception, ValueError)

    def test_full_initialization(self):
        """Test SDKResult with all fields initialized."""
        exception = RuntimeError("test")
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=2.5,
            session_id="full-test-session",
            agent_name="FullTestAgent",
            messages=["m1", "m2"],
            target_message="target",
            error_type=SDKErrorType.SUCCESS,
            errors=["warning1"],
            last_exception=exception,
        )

        assert result.is_success() is True
        assert result.duration_seconds == 2.5
        assert result.session_id == "full-test-session"
        assert result.agent_name == "FullTestAgent"
        assert result.messages == ["m1", "m2"]
        assert result.target_message == "target"
        assert result.errors == ["warning1"]
        assert result.last_exception == exception

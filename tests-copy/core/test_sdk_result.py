"""SDKResult单元测试

测试SDKResult数据类的所有功能和边界条件。
"""

import pytest
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class TestSDKResult:
    """SDKResult测试类"""

    def test_sdk_result_creation_success(self) -> None:
        """测试成功的SDKResult创建"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="TestAgent"
        )

        assert result.has_target_result is True
        assert result.cleanup_completed is True
        assert result.duration_seconds == 1.5
        assert result.session_id == "test-session"
        assert result.agent_name == "TestAgent"
        assert result.is_success() is True

    def test_sdk_result_creation_failure(self) -> None:
        """测试失败的SDKResult创建"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=2.0,
            session_id="test-session",
            agent_name="TestAgent"
        )

        assert result.has_target_result is False
        assert result.cleanup_completed is False
        assert result.duration_seconds == 2.0
        assert result.is_success() is False

    def test_is_success_with_both_true(self) -> None:
        """测试is_success() - 两个条件都为True"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True
        )
        assert result.is_success() is True

    def test_is_success_with_target_false(self) -> None:
        """测试is_success() - has_target_result为False"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=True
        )
        assert result.is_success() is False

    def test_is_success_with_cleanup_false(self) -> None:
        """测试is_success() - cleanup_completed为False"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=False
        )
        assert result.is_success() is False

    def test_is_success_with_both_false(self) -> None:
        """测试is_success() - 两个条件都为False"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False
        )
        assert result.is_success() is False

    def test_is_cancelled(self) -> None:
        """测试is_cancelled()方法"""
        result = SDKResult(
            error_type=SDKErrorType.CANCELLED
        )
        assert result.is_cancelled() is True

        result.error_type = SDKErrorType.SUCCESS
        assert result.is_cancelled() is False

    def test_is_timeout(self) -> None:
        """测试is_timeout()方法"""
        result = SDKResult(
            error_type=SDKErrorType.TIMEOUT
        )
        assert result.is_timeout() is True

        result.error_type = SDKErrorType.SUCCESS
        assert result.is_timeout() is False

    def test_has_cancel_scope_error(self) -> None:
        """测试has_cancel_scope_error()方法"""
        result = SDKResult(
            error_type=SDKErrorType.CANCEL_SCOPE_ERROR
        )
        assert result.has_cancel_scope_error() is True

        result.error_type = SDKErrorType.SUCCESS
        assert result.has_cancel_scope_error() is False

    def test_has_sdk_error(self) -> None:
        """测试has_sdk_error()方法"""
        result = SDKResult(
            error_type=SDKErrorType.SDK_ERROR
        )
        assert result.has_sdk_error() is True

        result.error_type = SDKErrorType.SUCCESS
        assert result.has_sdk_error() is False

    def test_is_unknown_error(self) -> None:
        """测试is_unknown_error()方法"""
        result = SDKResult(
            error_type=SDKErrorType.UNKNOWN
        )
        assert result.is_unknown_error() is True

        result.error_type = SDKErrorType.SUCCESS
        assert result.is_unknown_error() is False

    def test_get_error_summary_success(self) -> None:
        """测试get_error_summary() - 成功情况"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            error_type=SDKErrorType.SUCCESS
        )
        assert result.get_error_summary() == "Success"

    def test_get_error_summary_with_errors(self) -> None:
        """测试get_error_summary() - 有错误情况"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Error 1", "Error 2"]
        )
        assert "sdk_error (2 errors)" in result.get_error_summary()

    def test_get_error_summary_no_errors_list(self) -> None:
        """测试get_error_summary() - 错误列表为空"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.CANCELLED
        )
        assert result.get_error_summary() == "cancelled"

    def test_str_representation_success(self) -> None:
        """测试__str__() - 成功情况"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="TestAgent"
        )
        result_str = str(result)
        assert "✓" in result_str
        assert "test-session" in result_str
        assert "TestAgent" in result_str

    def test_str_representation_failure(self) -> None:
        """测试__str__() - 失败情况"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=2.0,
            session_id="fail-session",
            agent_name="TestAgent"
        )
        result_str = str(result)
        assert "✗" in result_str
        assert "fail-session" in result_str

    def test_default_values(self) -> None:
        """测试默认值"""
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

    def test_messages_list(self) -> None:
        """测试消息列表"""
        messages = [{"type": "msg1"}, {"type": "msg2"}]
        result = SDKResult(messages=messages)

        assert result.messages == messages
        assert len(result.messages) == 2

    def test_target_message(self) -> None:
        """测试目标消息"""
        target = {"type": "result", "content": "important"}
        result = SDKResult(
            has_target_result=True,
            target_message=target
        )

        assert result.target_message == target
        assert result.has_target_result is True

    def test_last_exception(self) -> None:
        """测试最后一个异常"""
        exc = ValueError("Test error")
        result = SDKResult(
            has_target_result=False,
            last_exception=exc
        )

        assert result.last_exception is exc
        # last_exception不会自动添加到errors列表
        assert str(exc) not in result.errors
        assert result.errors == []  # errors初始为空列表

    def test_error_list_operations(self) -> None:
        """测试错误列表操作"""
        result = SDKResult()

        # 初始为空
        assert result.errors == []

        # 添加错误
        result.errors.append("Error 1")
        result.errors.append("Error 2")

        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors

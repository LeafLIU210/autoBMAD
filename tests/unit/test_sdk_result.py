"""
SDKResult 单元测试

测试 SDKResult 数据结构和所有方法的行为
"""

import pytest
import sys
from pathlib import Path

# 添加路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class TestSDKResult:
    """测试 SDKResult 数据类"""

    def test_init_default(self):
        """测试默认初始化"""
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

    def test_init_with_values(self):
        """测试带值的初始化"""
        test_message = {"type": "result", "content": "test"}
        test_exception = ValueError("test error")

        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="TestAgent",
            messages=[test_message],
            target_message=test_message,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["error1", "error2"],
            last_exception=test_exception
        )

        assert result.has_target_result is True
        assert result.cleanup_completed is True
        assert result.duration_seconds == 1.5
        assert result.session_id == "test-session"
        assert result.agent_name == "TestAgent"
        assert result.messages == [test_message]
        assert result.target_message == test_message
        assert result.error_type == SDKErrorType.SDK_ERROR
        assert result.errors == ["error1", "error2"]
        assert result.last_exception == test_exception

    def test_is_success_when_both_flags_true(self):
        """测试当两个标志都为True时，is_success返回True"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True
        )
        assert result.is_success() is True

    def test_is_success_when_has_target_result_false(self):
        """测试当has_target_result为False时，is_success返回False"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=True
        )
        assert result.is_success() is False

    def test_is_success_when_cleanup_completed_false(self):
        """测试当cleanup_completed为False时，is_success返回False"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=False
        )
        assert result.is_success() is False

    def test_is_success_when_both_flags_false(self):
        """测试当两个标志都为False时，is_success返回False"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False
        )
        assert result.is_success() is False

    def test_is_cancelled_when_error_type_cancelled(self):
        """测试当error_type为CANCELLED时，is_cancelled返回True"""
        result = SDKResult(error_type=SDKErrorType.CANCELLED)
        assert result.is_cancelled() is True

    def test_is_cancelled_when_error_type_success(self):
        """测试当error_type为SUCCESS时，is_cancelled返回False"""
        result = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result.is_cancelled() is False

    def test_is_cancelled_when_error_type_sdk_error(self):
        """测试当error_type为SDK_ERROR时，is_cancelled返回False"""
        result = SDKResult(error_type=SDKErrorType.SDK_ERROR)
        assert result.is_cancelled() is False

    def test_is_timeout_when_error_type_timeout(self):
        """测试当error_type为TIMEOUT时，is_timeout返回True"""
        result = SDKResult(error_type=SDKErrorType.TIMEOUT)
        assert result.is_timeout() is True

    def test_is_timeout_when_error_type_success(self):
        """测试当error_type为SUCCESS时，is_timeout返回False"""
        result = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result.is_timeout() is False

    def test_has_cancel_scope_error_when_error_type_cancel_scope_error(self):
        """测试当error_type为CANCEL_SCOPE_ERROR时，has_cancel_scope_error返回True"""
        result = SDKResult(error_type=SDKErrorType.CANCEL_SCOPE_ERROR)
        assert result.has_cancel_scope_error() is True

    def test_has_cancel_scope_error_when_error_type_success(self):
        """测试当error_type为SUCCESS时，has_cancel_scope_error返回False"""
        result = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result.has_cancel_scope_error() is False

    def test_has_sdk_error_when_error_type_sdk_error(self):
        """测试当error_type为SDK_ERROR时，has_sdk_error返回True"""
        result = SDKResult(error_type=SDKErrorType.SDK_ERROR)
        assert result.has_sdk_error() is True

    def test_has_sdk_error_when_error_type_success(self):
        """测试当error_type为SUCCESS时，has_sdk_error返回False"""
        result = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result.has_sdk_error() is False

    def test_is_unknown_error_when_error_type_unknown(self):
        """测试当error_type为UNKNOWN时，is_unknown_error返回True"""
        result = SDKResult(error_type=SDKErrorType.UNKNOWN)
        assert result.is_unknown_error() is True

    def test_is_unknown_error_when_error_type_success(self):
        """测试当error_type为SUCCESS时，is_unknown_error返回False"""
        result = SDKResult(error_type=SDKErrorType.SUCCESS)
        assert result.is_unknown_error() is False

    def test_get_error_summary_when_success(self):
        """测试当成功时，get_error_summary返回'Success'"""
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True
        )
        assert result.get_error_summary() == "Success"

    def test_get_error_summary_when_no_errors(self):
        """测试当有错误类型但无错误列表时"""
        result = SDKResult(error_type=SDKErrorType.CANCELLED)
        assert result.get_error_summary() == "cancelled"

    def test_get_error_summary_with_errors(self):
        """测试当有错误列表时"""
        result = SDKResult(
            error_type=SDKErrorType.SDK_ERROR,
            errors=["error1", "error2"]
        )
        assert result.get_error_summary() == "sdk_error (2 errors)"

    def test_str_representation_success(self):
        """测试成功时的字符串表示"""
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
        assert "True" in result_str
        assert "1.50s" in result_str

    def test_str_representation_failure(self):
        """测试失败时的字符串表示"""
        result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=2.0,
            session_id="fail-session",
            agent_name="FailAgent",
            error_type=SDKErrorType.SDK_ERROR
        )
        result_str = str(result)

        assert "✗" in result_str
        assert "fail-session" in result_str
        assert "FailAgent" in result_str
        assert "False" in result_str
        assert "2.00s" in result_str


class TestSDKErrorType:
    """测试 SDKErrorType 枚举"""

    def test_all_error_types_defined(self):
        """测试所有错误类型都已定义"""
        assert hasattr(SDKErrorType, "SUCCESS")
        assert hasattr(SDKErrorType, "CANCELLED")
        assert hasattr(SDKErrorType, "TIMEOUT")
        assert hasattr(SDKErrorType, "SDK_ERROR")
        assert hasattr(SDKErrorType, "CANCEL_SCOPE_ERROR")
        assert hasattr(SDKErrorType, "UNKNOWN")

    def test_error_type_values(self):
        """测试错误类型的值"""
        assert SDKErrorType.SUCCESS.value == "success"
        assert SDKErrorType.CANCELLED.value == "cancelled"
        assert SDKErrorType.TIMEOUT.value == "timeout"
        assert SDKErrorType.SDK_ERROR.value == "sdk_error"
        assert SDKErrorType.CANCEL_SCOPE_ERROR.value == "cancel_scope_error"
        assert SDKErrorType.UNKNOWN.value == "unknown"

    def test_error_type_enum_values(self):
        """测试错误类型是有效的枚举值"""
        # 确保所有值都是字符串
        for error_type in SDKErrorType:
            assert isinstance(error_type.value, str)
            assert len(error_type.value) > 0

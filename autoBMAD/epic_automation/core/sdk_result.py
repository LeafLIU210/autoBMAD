"""SDK执行结果数据结构

该模块定义了SDK执行结果的标准化数据结构，包含：
- SDKErrorType: SDK错误类型枚举
- SDKResult: SDK执行结果数据类
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SDKErrorType(Enum):
    """SDK错误类型枚举

    包含所有可能的SDK执行状态：
    - SUCCESS: 成功执行
    - CANCELLED: 被取消
    - TIMEOUT: 超时
    - SDK_ERROR: SDK内部错误
    - CANCEL_SCOPE_ERROR: Cancel Scope错误
    - UNKNOWN: 未知错误
    """
    SUCCESS = "success"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    SDK_ERROR = "sdk_error"
    CANCEL_SCOPE_ERROR = "cancel_scope_error"
    UNKNOWN = "unknown"


@dataclass
class SDKResult:
    """
    SDK执行结果数据类

    核心设计：
    1. has_target_result: 是否获得目标ResultMessage
    2. cleanup_completed: 是否完成资源清理
    3. errors: SDK底层错误（不影响业务判断）

    业务成功判断：
    - is_success() = has_target_result AND cleanup_completed

    Attributes:
        has_target_result: 是否获得目标结果消息
        cleanup_completed: 是否完成资源清理
        duration_seconds: 执行耗时（秒）
        session_id: 会话ID
        agent_name: Agent名称
        messages: 所有接收到的消息列表
        target_message: 目标消息（如果有）
        error_type: 错误类型
        errors: 错误信息列表
        last_exception: 最后一个异常
    """

    # 业务成功标志（Agent只关注这两个字段）
    has_target_result: bool = False
    cleanup_completed: bool = False

    # 执行信息
    duration_seconds: float = 0.0
    session_id: str = ""
    agent_name: str = ""

    # 结果数据
    messages: list[Any] = field(default_factory=list)
    target_message: Any = None

    # 错误信息（仅用于日志和调试）
    error_type: SDKErrorType = SDKErrorType.SUCCESS
    errors: list[str] = field(default_factory=list)
    last_exception: Exception | None = None

    def is_success(self) -> bool:
        """判断业务是否成功

        业务成功需要同时满足：
        1. 获得目标结果 (has_target_result)
        2. 完成资源清理 (cleanup_completed)

        Returns:
            bool: 业务是否成功
        """
        return self.has_target_result and self.cleanup_completed

    def is_cancelled(self) -> bool:
        """判断是否被取消

        Returns:
            bool: 是否被取消
        """
        return self.error_type == SDKErrorType.CANCELLED

    def is_timeout(self) -> bool:
        """判断是否超时

        Returns:
            bool: 是否超时
        """
        return self.error_type == SDKErrorType.TIMEOUT

    def has_cancel_scope_error(self) -> bool:
        """判断是否有Cancel Scope错误

        Returns:
            bool: 是否有Cancel Scope错误
        """
        return self.error_type == SDKErrorType.CANCEL_SCOPE_ERROR

    def has_sdk_error(self) -> bool:
        """判断是否有SDK内部错误

        Returns:
            bool: 是否有SDK错误
        """
        return self.error_type == SDKErrorType.SDK_ERROR

    def is_unknown_error(self) -> bool:
        """判断是否有未知错误

        Returns:
            bool: 是否有未知错误
        """
        return self.error_type == SDKErrorType.UNKNOWN

    def get_error_summary(self) -> str:
        """获取错误摘要信息

        Returns:
            str: 错误摘要，包含错误类型和错误数量
        """
        if self.is_success():
            return "Success"

        error_count = len(self.errors)
        if error_count == 0:
            return f"{self.error_type.value}"

        return f"{self.error_type.value} ({error_count} errors)"

    def __str__(self) -> str:
        """字符串表示

        Returns:
            str: 人类可读的字符串表示
        """
        status = "✓" if self.is_success() else "✗"
        return (
            f"{status} SDKResult("
            f"session={self.session_id}, "
            f"agent={self.agent_name}, "
            f"success={self.is_success()}, "
            f"target={self.has_target_result}, "
            f"cleanup={self.cleanup_completed}, "
            f"duration={self.duration_seconds:.2f}s, "
            f"error={self.get_error_summary()}"
            f")"
        )

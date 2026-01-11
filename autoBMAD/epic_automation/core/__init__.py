"""SDK执行层核心模块

该模块包含SDK执行层的核心组件：
- SDKResult: SDK执行结果数据结构
- SDKExecutor: SDK执行器
- CancellationManager: 取消管理器
- SafeClaudeSDK: 安全的Claude SDK封装
"""

from .sdk_result import SDKResult, SDKErrorType
from .sdk_executor import SDKExecutor
from .cancellation_manager import CancellationManager
from .safe_claude_sdk import SafeClaudeSDK

__all__ = [
    "SDKResult",
    "SDKErrorType",
    "SDKExecutor",
    "CancellationManager",
    "SafeClaudeSDK",
]

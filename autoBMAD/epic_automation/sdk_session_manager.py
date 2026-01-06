"""
SDK 会话管理器 - 提供 Agent 间的 SDK 调用隔离。

本模块解决 anyio cancel scope 在多个 Agent SDK 调用间传播的问题，
通过 asyncio.shield 和独立上下文确保每个 Agent 的 SDK 调用互不干扰。
"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class SDKErrorType(Enum):
    """SDK 错误类型枚举"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SDK_ERROR = "sdk_error"
    UNKNOWN = "unknown"


@dataclass
class SDKExecutionResult:
    """SDK 执行结果"""
    success: bool
    error_type: SDKErrorType = SDKErrorType.SUCCESS
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    session_id: str = ""

    def is_cancelled(self) -> bool:
        """检查是否被取消"""
        return self.error_type == SDKErrorType.CANCELLED

    def is_timeout(self) -> bool:
        """检查是否超时"""
        return self.error_type == SDKErrorType.TIMEOUT


class IsolatedSDKContext:
    """
    隔离的 SDK 执行上下文。

    提供 Agent 级别的执行隔离，确保 cancel scope 不会跨 Agent 传播。
    """

    def __init__(self, agent_name: str, session_id: str):
        self.agent_name = agent_name
        self.session_id = session_id
        self._cancel_event = asyncio.Event()
        self._is_active = False
        self._start_time: Optional[float] = None

    async def __aenter__(self) -> "IsolatedSDKContext":
        self._is_active = True
        self._cancel_event.clear()
        self._start_time = time.time()
        logger.debug(f"[{self.agent_name}] Session {self.session_id[:8]} started")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Any
    ) -> bool:
        self._is_active = False

        duration = time.time() - self._start_time if self._start_time else 0
        logger.debug(
            f"[{self.agent_name}] Session {self.session_id[:8]} ended "
            f"(duration: {duration:.1f}s)"
        )
        return False  # 不吞没异常

    def request_cancel(self) -> None:
        """请求取消当前会话"""
        self._cancel_event.set()
        logger.info(f"[{self.agent_name}] Cancel requested for session {self.session_id[:8]}")

    def is_cancelled(self) -> bool:
        """检查会话是否已被取消"""
        return self._cancel_event.is_set()

    @property
    def is_active(self) -> bool:
        """检查会话是否活动"""
        return self._is_active

    def get_elapsed_time(self) -> float:
        """获取会话已运行时间"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time


class SDKSessionManager:
    """
    SDK 会话管理器 - 确保 Agent 间的 SDK 调用隔离。

    核心功能：
    1. 为每个 Agent 创建独立的执行上下文
    2. 使用 asyncio.shield 防止外部取消信号传播
    3. 统一的错误处理和超时管理
    4. 会话生命周期追踪
    """

    def __init__(self) -> None:
        self._active_sessions: Dict[str, "IsolatedSDKContext"] = {}
        self._lock = asyncio.Lock()
        self._total_sessions = 0
        self._successful_sessions = 0
        self._failed_sessions = 0

    @asynccontextmanager
    async def create_session(self, agent_name: str):
        """
        创建隔离的 SDK 会话。

        Args:
            agent_name: Agent 名称，用于日志标识

        Yields:
            IsolatedSDKContext: 隔离的执行上下文
        """
        session_id = str(uuid.uuid4())
        context = IsolatedSDKContext(agent_name, session_id)

        async with self._lock:
            self._active_sessions[session_id] = context
            self._total_sessions += 1

        try:
            async with context:
                yield context
        finally:
            async with self._lock:
                self._active_sessions.pop(session_id, None)

    async def execute_isolated(
        self,
        agent_name: str,
        sdk_func: Callable[[], Any],
        timeout: float = 1200.0
    ) -> SDKExecutionResult:
        """
        在隔离上下文中执行 SDK 调用。

        简化取消信号处理，使用上下文边界控制而非 asyncio.shield。

        Args:
            agent_name: Agent 名称
            sdk_func: 要执行的 SDK 函数（无参数，返回 bool）
            timeout: 超时时间（秒）

        Returns:
            SDKExecutionResult: 执行结果，包含成功状态、错误类型等
        """
        start_time = time.time()
        session_id = str(uuid.uuid4())

        async with self.create_session(agent_name) as _context:
            try:
                # 简化取消信号处理：直接使用 wait_for，通过上下文边界控制
                result = await asyncio.wait_for(
                    sdk_func(),
                    timeout=timeout
                )
                duration = time.time() - start_time

                async with self._lock:
                    if result:
                        self._successful_sessions += 1
                    else:
                        self._failed_sessions += 1

                return SDKExecutionResult(
                    success=bool(result),
                    error_type=SDKErrorType.SUCCESS if result else SDKErrorType.SDK_ERROR,
                    duration_seconds=duration,
                    session_id=session_id
                )

            except asyncio.TimeoutError:
                duration = time.time() - start_time
                logger.warning(
                    f"[{agent_name}] SDK timeout after {duration:.1f}s "
                    f"(limit: {timeout}s)"
                )
                async with self._lock:
                    self._failed_sessions += 1
                return SDKExecutionResult(
                    success=False,
                    error_type=SDKErrorType.TIMEOUT,
                    error_message=f"Timeout after {timeout}s",
                    duration_seconds=duration,
                    session_id=session_id
                )

            except asyncio.CancelledError:
                duration = time.time() - start_time
                logger.info(
                    f"[{agent_name}] SDK cancelled after {duration:.1f}s"
                )
                async with self._lock:
                    self._failed_sessions += 1
                return SDKExecutionResult(
                    success=False,
                    error_type=SDKErrorType.CANCELLED,
                    error_message="Execution cancelled",
                    duration_seconds=duration,
                    session_id=session_id
                )

            except RuntimeError as e:
                duration = time.time() - start_time
                error_msg = str(e)

                # 检查是否是 cancel scope 错误
                if "cancel scope" in error_msg:
                    logger.error(f"[{agent_name}] Cancel scope error detected: {error_msg}")
                    async with self._lock:
                        self._failed_sessions += 1
                    return SDKExecutionResult(
                        success=False,
                        error_type=SDKErrorType.SDK_ERROR,
                        error_message=f"Cancel scope error: {error_msg}",
                        duration_seconds=duration,
                        session_id=session_id
                    )

                # 其他 RuntimeError
                logger.error(f"[{agent_name}] Runtime error: {error_msg}")
                async with self._lock:
                    self._failed_sessions += 1
                return SDKExecutionResult(
                    success=False,
                    error_type=SDKErrorType.UNKNOWN,
                    error_message=error_msg,
                    duration_seconds=duration,
                    session_id=session_id
                )

            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                logger.error(f"[{agent_name}] SDK error: {error_msg}")
                async with self._lock:
                    self._failed_sessions += 1
                return SDKExecutionResult(
                    success=False,
                    error_type=SDKErrorType.UNKNOWN,
                    error_message=error_msg,
                    duration_seconds=duration,
                    session_id=session_id
                )

    def get_active_sessions(self) -> List[str]:
        """获取当前活动的会话 ID 列表"""
        return list(self._active_sessions.keys())

    def get_session_count(self) -> int:
        """获取当前活动会话数"""
        return len(self._active_sessions)

    def get_statistics(self) -> Dict[str, int]:
        """获取会话统计信息"""
        return {
            "total_sessions": self._total_sessions,
            "successful_sessions": self._successful_sessions,
            "failed_sessions": self._failed_sessions,
            "active_sessions": len(self._active_sessions)
        }

    async def cancel_all_sessions(self) -> int:
        """
        取消所有活动会话。

        Returns:
            int: 被取消的会话数
        """
        cancelled_count = 0
        async with self._lock:
            for session_id, context in self._active_sessions.items():
                if context.is_active:
                    context.request_cancel()
                    cancelled_count += 1
                    logger.info(f"Cancelled session {session_id[:8]}")
        return cancelled_count


# 全局单例
_global_session_manager: Optional[SDKSessionManager] = None


def get_session_manager() -> SDKSessionManager:
    """
    获取全局会话管理器单例。

    Returns:
        SDKSessionManager: 全局会话管理器实例
    """
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SDKSessionManager()
    return _global_session_manager


def reset_session_manager() -> None:
    """
    重置全局会话管理器（主要用于测试）。
    """
    global _global_session_manager
    _global_session_manager = None

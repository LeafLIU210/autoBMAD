"""取消管理器

该模块实现双条件验证机制的取消管理器：
- CallInfo: SDK调用信息数据类
- CancellationManager: 取消管理器类

核心功能：
1. 跟踪活跃的SDK调用
2. 管理取消请求
3. 验证清理完成（双条件验证机制）
4. 提供异步上下文管理器track_sdk_execution
"""

import anyio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator


logger = logging.getLogger(__name__)


@dataclass
class CallInfo:
    """SDK调用信息数据类

    Attributes:
        call_id: 调用唯一标识符
        agent_name: Agent名称
        start_time: 开始时间戳
        cancel_requested: 是否已请求取消
        cleanup_completed: 是否已完成清理
        has_target_result: 是否已找到目标结果
        errors: 错误列表
    """
    call_id: str
    agent_name: str
    start_time: float
    cancel_requested: bool = False
    cleanup_completed: bool = False
    has_target_result: bool = False
    errors: list[str] = field(default_factory=list)


class CancellationManager:
    """
    取消管理器

    负责管理所有活跃的SDK调用，实现双条件验证机制：
    1. cancel_requested = True
    2. cleanup_completed = True

    只有同时满足这两个条件，才认为可以安全进行下一步。
    """

    def __init__(self) -> None:
        """初始化取消管理器"""
        self._active_calls: dict[str, CallInfo] = {}
        self._lock = anyio.Lock()

    def register_call(self, call_id: str, agent_name: str) -> None:
        """注册SDK调用

        Args:
            call_id: 调用唯一标识符
            agent_name: Agent名称
        """
        self._active_calls[call_id] = CallInfo(
            call_id=call_id,
            agent_name=agent_name,
            start_time=time.time()
        )
        logger.debug(f"[CancelManager] Registered call: {call_id}")

    def request_cancel(self, call_id: str) -> None:
        """请求取消

        Args:
            call_id: 调用唯一标识符
        """
        if call_id in self._active_calls:
            self._active_calls[call_id].cancel_requested = True
            logger.info(f"[CancelManager] Cancel requested: {call_id}")

    def mark_cleanup_completed(self, call_id: str) -> None:
        """标记清理完成

        Args:
            call_id: 调用唯一标识符
        """
        if call_id in self._active_calls:
            self._active_calls[call_id].cleanup_completed = True
            logger.info(f"[CancelManager] Cleanup completed: {call_id}")

    def mark_target_result_found(self, call_id: str) -> None:
        """标记找到目标结果

        Args:
            call_id: 调用唯一标识符
        """
        if call_id in self._active_calls:
            self._active_calls[call_id].has_target_result = True
            logger.info(f"[CancelManager] Target result found: {call_id}")

    @asynccontextmanager
    async def track_sdk_execution(
        self,
        call_id: str,
        agent_name: str,
        operation_name: str | None = None
    ) -> AsyncIterator[None]:
        """
        跟踪SDK执行（异步上下文管理器）

        用法:
            async with manager.track_sdk_execution(call_id, agent_name):
                # SDK 调用代码
                pass

        Args:
            call_id: 调用唯一标识符
            agent_name: Agent名称
            operation_name: 操作名称（可选）

        Yields:
            None: 供async with使用
        """
        # 进入上下文：注册调用
        self.register_call(call_id, agent_name)
        logger.debug(
            f"[CancelManager] Entering context: {call_id} "
            f"({agent_name}/{operation_name})"
        )

        try:
            yield  # 执行被包裹的代码块
        finally:
            # 退出上下文：标记清理完成
            self.mark_cleanup_completed(call_id)
            logger.debug(f"[CancelManager] Exiting context: {call_id}")


    async def confirm_safe_to_proceed(self, call_id: str, timeout: float = 30.0) -> bool:
        """Confirm safe to proceed"""
        import anyio
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if call_id in self._active_calls:
                call_info = self._active_calls[call_id]
                if call_info.cancel_requested and call_info.cleanup_completed:
                    return True
            await anyio.sleep(0.1)
        return False

    def unregister_call(self, call_id: str) -> None:
        """Unregister a call"""
        if call_id in self._active_calls:
            del self._active_calls[call_id]

    def get_active_calls_count(self) -> int:
        """获取活跃调用数量

        Returns:
            int: 当前活跃的SDK调用数量
        """
        return len(self._active_calls)

    def get_call_info(self, call_id: str) -> CallInfo | None:
        """获取调用信息

        Args:
            call_id: 调用唯一标识符

        Returns:
            CallInfo | None: 调用信息，如果不存在则返回None
        """
        return self._active_calls.get(call_id)

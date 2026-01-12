"""
CancellationManager 单元测试

测试 CancellationManager 的双条件验证机制和所有方法
"""

import pytest
import anyio
import sys
import time
from pathlib import Path

# 添加路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager, CallInfo


@pytest.mark.anyio
class TestCancellationManager:
    """测试 CancellationManager 类"""

    @pytest.fixture
    def manager(self):
        """创建 CancellationManager 实例"""
        return CancellationManager()

    @pytest.fixture
    def test_call_info(self):
        """创建测试 CallInfo 实例"""
        return CallInfo(
            call_id="test-call-123",
            agent_name="TestAgent",
            start_time=time.time()
        )

    def test_init(self, manager):
        """测试初始化"""
        assert isinstance(manager._active_calls, dict)
        assert len(manager._active_calls) == 0
        assert isinstance(manager._lock, anyio.Lock)

    def test_register_call(self, manager, test_call_info):
        """测试注册SDK调用"""
        manager.register_call("test-call-123", "TestAgent")

        assert "test-call-123" in manager._active_calls
        call_info = manager._active_calls["test-call-123"]
        assert call_info.call_id == "test-call-123"
        assert call_info.agent_name == "TestAgent"
        assert call_info.cancel_requested is False
        assert call_info.cleanup_completed is False
        assert call_info.has_target_result is False
        assert call_info.errors == []

    def test_register_call_multiple(self, manager):
        """测试注册多个SDK调用"""
        manager.register_call("call-1", "Agent1")
        manager.register_call("call-2", "Agent2")
        manager.register_call("call-3", "Agent3")

        assert len(manager._active_calls) == 3
        assert "call-1" in manager._active_calls
        assert "call-2" in manager._active_calls
        assert "call-3" in manager._active_calls

    def test_request_cancel(self, manager):
        """测试请求取消"""
        manager.register_call("test-call", "TestAgent")
        manager.request_cancel("test-call")

        call_info = manager._active_calls["test-call"]
        assert call_info.cancel_requested is True

    def test_request_cancel_nonexistent_call(self, manager):
        """测试请求取消不存在的调用"""
        # 不应该抛出异常
        manager.request_cancel("nonexistent-call")

        # 确保没有添加不存在的调用
        assert "nonexistent-call" not in manager._active_calls

    def test_mark_cleanup_completed(self, manager):
        """测试标记清理完成"""
        manager.register_call("test-call", "TestAgent")
        manager.mark_cleanup_completed("test-call")

        call_info = manager._active_calls["test-call"]
        assert call_info.cleanup_completed is True

    def test_mark_cleanup_completed_nonexistent(self, manager):
        """测试标记不存在的调用清理完成"""
        # 不应该抛出异常
        manager.mark_cleanup_completed("nonexistent-call")

    def test_mark_target_result_found(self, manager):
        """测试标记找到目标结果"""
        manager.register_call("test-call", "TestAgent")
        manager.mark_target_result_found("test-call")

        call_info = manager._active_calls["test-call"]
        assert call_info.has_target_result is True

    def test_mark_target_result_found_nonexistent(self, manager):
        """测试标记不存在的调用找到目标结果"""
        # 不应该抛出异常
        manager.mark_target_result_found("nonexistent-call")

    async def test_confirm_safe_to_proceed_both_conditions_met(self, manager):
        """测试当两个条件都满足时，确认可以安全进行"""
        manager.register_call("test-call", "TestAgent")
        manager.request_cancel("test-call")
        manager.mark_cleanup_completed("test-call")

        safe = await manager.confirm_safe_to_proceed("test-call", timeout=1.0)

        assert safe is True

    async def test_confirm_safe_to_proceed_cancel_requested_only(self, manager):
        """测试当只满足cancel_requested条件时，不应该确认安全"""
        manager.register_call("test-call", "TestAgent")
        manager.request_cancel("test-call")
        # 不标记 cleanup_completed

        # 使用很短的超时，避免长时间等待
        safe = await manager.confirm_safe_to_proceed("test-call", timeout=0.2)

        assert safe is False

    async def test_confirm_safe_to_proceed_cleanup_completed_only(self, manager):
        """测试当只满足cleanup_completed条件时，不应该确认安全"""
        manager.register_call("test-call", "TestAgent")
        manager.mark_cleanup_completed("test-call")
        # 不请求取消

        # 使用很短的超时
        safe = await manager.confirm_safe_to_proceed("test-call", timeout=0.2)

        assert safe is False

    async def test_confirm_safe_to_proceed_neither_condition(self, manager):
        """测试当两个条件都不满足时，不应该确认安全"""
        manager.register_call("test-call", "TestAgent")
        # 既不请求取消，也不标记清理完成

        # 使用很短的超时
        safe = await manager.confirm_safe_to_proceed("test-call", timeout=0.2)

        assert safe is False

    async def test_confirm_safe_to_proceed_timeout(self, manager):
        """测试超时场景"""
        manager.register_call("test-call", "TestAgent")
        # 不满足任何条件，等待超时

        start_time = time.time()
        safe = await manager.confirm_safe_to_proceed("test-call", timeout=0.3)
        elapsed = time.time() - start_time

        assert safe is False
        assert elapsed >= 0.3  # 确保确实等待了超时时间

    async def test_confirm_safe_to_proceed_nonexistent_call(self, manager):
        """测试确认不存在的调用"""
        safe = await manager.confirm_safe_to_proceed("nonexistent-call", timeout=1.0)

        assert safe is False

    async def test_confirm_safe_to_proceed_rapid_changes(self, manager):
        """测试快速变化的条件"""
        manager.register_call("test-call", "TestAgent")

        # 异步启动检查
        async def check_safe():
            return await manager.confirm_safe_to_proceed("test-call", timeout=1.0)

        # 几乎同时设置两个条件 - 使用异步包装器
        async def async_request_cancel():
            manager.request_cancel("test-call")

        async def async_mark_cleanup():
            manager.mark_cleanup_completed("test-call")

        async with anyio.create_task_group() as tg:
            tg.start_soon(async_request_cancel)
            tg.start_soon(async_mark_cleanup)
            result = await check_safe()

        assert result is True

    def test_unregister_call(self, manager):
        """测试注销SDK调用"""
        manager.register_call("test-call", "TestAgent")
        assert "test-call" in manager._active_calls

        manager.unregister_call("test-call")
        assert "test-call" not in manager._active_calls

    def test_unregister_call_nonexistent(self, manager):
        """测试注销不存在的调用"""
        # 不应该抛出异常
        manager.unregister_call("nonexistent-call")

    def test_get_active_calls_count_empty(self, manager):
        """测试获取活跃调用数量（空）"""
        count = manager.get_active_calls_count()
        assert count == 0

    def test_get_active_calls_count_with_calls(self, manager):
        """测试获取活跃调用数量（有调用）"""
        manager.register_call("call-1", "Agent1")
        manager.register_call("call-2", "Agent2")
        manager.register_call("call-3", "Agent3")

        count = manager.get_active_calls_count()
        assert count == 3

    def test_get_call_info_exists(self, manager):
        """测试获取存在的调用信息"""
        manager.register_call("test-call", "TestAgent")
        call_info = manager.get_call_info("test-call")

        assert call_info is not None
        assert call_info.call_id == "test-call"
        assert call_info.agent_name == "TestAgent"

    def test_get_call_info_nonexistent(self, manager):
        """测试获取不存在的调用信息"""
        call_info = manager.get_call_info("nonexistent-call")
        assert call_info is None

    async def test_lifecycle(self, manager):
        """测试完整的生命周期"""
        call_id = "lifecycle-test-call"

        # 1. 注册
        manager.register_call(call_id, "TestAgent")
        assert manager.get_active_calls_count() == 1

        # 2. 请求取消
        manager.request_cancel(call_id)
        call_info = manager.get_call_info(call_id)
        assert call_info.cancel_requested is True

        # 3. 标记找到目标
        manager.mark_target_result_found(call_id)
        call_info = manager.get_call_info(call_id)
        assert call_info.has_target_result is True

        # 4. 标记清理完成
        manager.mark_cleanup_completed(call_id)
        call_info = manager.get_call_info(call_id)
        assert call_info.cleanup_completed is True

        # 5. 确认安全进行
        safe = await manager.confirm_safe_to_proceed(call_id, timeout=1.0)
        assert safe is True

        # 6. 注销
        manager.unregister_call(call_id)
        assert manager.get_active_calls_count() == 0


class TestCallInfo:
    """测试 CallInfo 数据类"""

    def test_call_info_creation(self):
        """测试 CallInfo 创建"""
        start_time = time.time()
        call_info = CallInfo(
            call_id="test-123",
            agent_name="TestAgent",
            start_time=start_time
        )

        assert call_info.call_id == "test-123"
        assert call_info.agent_name == "TestAgent"
        assert call_info.start_time == start_time
        assert call_info.cancel_requested is False
        assert call_info.cleanup_completed is False
        assert call_info.has_target_result is False
        assert call_info.errors == []

    def test_call_info_with_all_flags(self):
        """测试 CallInfo 创建（带所有标志）"""
        start_time = time.time()
        call_info = CallInfo(
            call_id="test-456",
            agent_name="TestAgent2",
            start_time=start_time,
            cancel_requested=True,
            cleanup_completed=True,
            has_target_result=True,
            errors=["error1", "error2"]
        )

        assert call_info.cancel_requested is True
        assert call_info.cleanup_completed is True
        assert call_info.has_target_result is True
        assert call_info.errors == ["error1", "error2"]

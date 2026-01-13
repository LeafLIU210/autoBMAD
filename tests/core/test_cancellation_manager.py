"""CancellationManager单元测试

测试CancellationManager类的所有功能和双条件验证机制。
"""

import pytest
import asyncio
import time
from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager, CallInfo


class TestCancellationManager:
    """CancellationManager测试类"""

    def test_initialization(self) -> None:
        """测试初始化"""
        manager = CancellationManager()
        assert manager.get_active_calls_count() == 0
        assert len(manager._active_calls) == 0

    def test_register_call(self) -> None:
        """测试注册调用"""
        manager = CancellationManager()
        call_id = "test-call-1"
        agent_name = "TestAgent"

        manager.register_call(call_id, agent_name)

        # 验证调用已注册
        assert manager.get_active_calls_count() == 1
        call_info = manager.get_call_info(call_id)
        assert call_info is not None
        assert call_info.call_id == call_id
        assert call_info.agent_name == agent_name
        assert call_info.cancel_requested is False
        assert call_info.cleanup_completed is False
        assert call_info.has_target_result is False

    def test_register_multiple_calls(self) -> None:
        """测试注册多个调用"""
        manager = CancellationManager()

        manager.register_call("call-1", "Agent1")
        manager.register_call("call-2", "Agent2")
        manager.register_call("call-3", "Agent3")

        assert manager.get_active_calls_count() == 3

    def test_request_cancel(self) -> None:
        """测试请求取消"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        assert manager.get_call_info(call_id).cancel_requested is False

        manager.request_cancel(call_id)

        # 验证取消请求已设置
        assert manager.get_call_info(call_id).cancel_requested is True

    def test_mark_cleanup_completed(self) -> None:
        """测试标记清理完成"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        assert manager.get_call_info(call_id).cleanup_completed is False

        manager.mark_cleanup_completed(call_id)

        # 验证清理完成已标记
        assert manager.get_call_info(call_id).cleanup_completed is True

    def test_mark_target_result_found(self) -> None:
        """测试标记找到目标结果"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        assert manager.get_call_info(call_id).has_target_result is False

        manager.mark_target_result_found(call_id)

        # 验证目标结果已标记
        assert manager.get_call_info(call_id).has_target_result is True

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_both_conditions_met(self) -> None:
        """测试confirm_safe_to_proceed - 两个条件都满足"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        manager.request_cancel(call_id)
        manager.mark_cleanup_completed(call_id)

        # 应该立即返回True
        result = await manager.confirm_safe_to_proceed(call_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_cancel_only(self) -> None:
        """测试confirm_safe_to_proceed - 只有取消请求"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        manager.request_cancel(call_id)
        # 没有标记cleanup_completed

        # 需要等待，但应该超时
        result = await manager.confirm_safe_to_proceed(call_id, timeout=0.2)
        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_cleanup_only(self) -> None:
        """测试confirm_safe_to_proceed - 只有清理完成"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        manager.mark_cleanup_completed(call_id)
        # 没有请求取消

        # 需要等待，但应该超时
        result = await manager.confirm_safe_to_proceed(call_id, timeout=0.2)
        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_no_conditions(self) -> None:
        """测试confirm_safe_to_proceed - 两个条件都不满足"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        # 没有请求取消，没有标记清理

        # 应该超时
        result = await manager.confirm_safe_to_proceed(call_id, timeout=0.2)
        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_nonexistent_call(self) -> None:
        """测试confirm_safe_to_proceed - 不存在的调用"""
        manager = CancellationManager()

        # 不存在的call_id
        result = await manager.confirm_safe_to_proceed("nonexistent", timeout=0.2)
        assert result is False

    @pytest.mark.asyncio
    async def test_confirm_safe_to_proceed_timeout(self) -> None:
        """测试confirm_safe_to_proceed - 超时情况"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        manager.request_cancel(call_id)
        # 没有标记cleanup_completed，会超时

        start = time.time()
        result = await manager.confirm_safe_to_proceed(call_id, timeout=0.5)
        elapsed = time.time() - start

        assert result is False
        assert 0.4 < elapsed < 0.7  # 允许一些时间误差

    def test_unregister_call(self) -> None:
        """测试注销调用"""
        manager = CancellationManager()
        call_id = "test-call-1"

        manager.register_call(call_id, "TestAgent")
        assert manager.get_active_calls_count() == 1

        manager.unregister_call(call_id)

        assert manager.get_active_calls_count() == 0
        assert manager.get_call_info(call_id) is None

    def test_unregister_nonexistent_call(self) -> None:
        """测试注销不存在的调用"""
        manager = CancellationManager()

        # 不应该抛出异常
        manager.unregister_call("nonexistent")
        assert manager.get_active_calls_count() == 0

    def test_get_active_calls_count(self) -> None:
        """测试获取活跃调用数量"""
        manager = CancellationManager()

        assert manager.get_active_calls_count() == 0

        manager.register_call("call-1", "Agent1")
        assert manager.get_active_calls_count() == 1

        manager.register_call("call-2", "Agent2")
        assert manager.get_active_calls_count() == 2

        manager.unregister_call("call-1")
        assert manager.get_active_calls_count() == 1

        manager.unregister_call("call-2")
        assert manager.get_active_calls_count() == 0

    def test_get_call_info(self) -> None:
        """测试获取调用信息"""
        manager = CancellationManager()
        call_id = "test-call-1"
        agent_name = "TestAgent"

        # 不存在的调用
        info = manager.get_call_info(call_id)
        assert info is None

        # 注册后获取
        manager.register_call(call_id, agent_name)
        info = manager.get_call_info(call_id)

        assert info is not None
        assert info.call_id == call_id
        assert info.agent_name == agent_name

    @pytest.mark.asyncio
    async def test_double_condition_validation_flow(self) -> None:
        """测试双条件验证完整流程"""
        manager = CancellationManager()
        call_id = "test-call-1"

        # 步骤1: 注册调用
        manager.register_call(call_id, "TestAgent")
        assert manager.get_call_info(call_id).cancel_requested is False
        assert manager.get_call_info(call_id).cleanup_completed is False

        # 步骤2: 请求取消
        manager.request_cancel(call_id)
        assert manager.get_call_info(call_id).cancel_requested is True
        assert manager.get_call_info(call_id).cleanup_completed is False

        # 步骤3: 标记清理完成
        manager.mark_cleanup_completed(call_id)
        assert manager.get_call_info(call_id).cancel_requested is True
        assert manager.get_call_info(call_id).cleanup_completed is True

        # 步骤4: 验证可以安全进行
        result = await manager.confirm_safe_to_proceed(call_id)
        assert result is True

        # 步骤5: 注销调用
        manager.unregister_call(call_id)
        assert manager.get_active_calls_count() == 0

    def test_call_info_initial_state(self) -> None:
        """测试CallInfo初始状态"""
        call_info = CallInfo(
            call_id="test-id",
            agent_name="TestAgent",
            start_time=time.time()
        )

        assert call_info.call_id == "test-id"
        assert call_info.agent_name == "TestAgent"
        assert call_info.cancel_requested is False
        assert call_info.cleanup_completed is False
        assert call_info.has_target_result is False
        assert call_info.errors == []

    def test_call_info_with_errors(self) -> None:
        """测试CallInfo错误列表"""
        call_info = CallInfo(
            call_id="test-id",
            agent_name="TestAgent",
            start_time=time.time(),
            errors=["Error 1", "Error 2"]
        )

        assert len(call_info.errors) == 2
        assert "Error 1" in call_info.errors
        assert "Error 2" in call_info.errors

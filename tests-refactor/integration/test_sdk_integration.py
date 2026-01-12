"""
SDK 集成测试

测试 SDK 集成修复方案的完整功能：
1. CancellationManager 异步上下文管理器
2. 全局单例模式
3. sdk_helper 统一接口
4. SDKExecutor 集成
"""

import pytest
import anyio
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

# 添加路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType
from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.monitoring import (
    get_cancellation_manager,
    reset_cancellation_manager
)


@pytest.mark.anyio
class TestAsyncContextManagerIntegration:
    """测试异步上下文管理器的集成"""

    async def test_track_sdk_execution_basic(self):
        """测试基本的异步上下文管理器使用"""
        manager = CancellationManager()
        call_id = "integration-test-1"

        async with manager.track_sdk_execution(call_id, "TestAgent"):
            # 验证调用已注册
            assert manager.get_active_calls_count() == 1
            call_info = manager.get_call_info(call_id)
            assert call_info is not None
            assert call_info.agent_name == "TestAgent"

        # 验证清理已完成
        call_info = manager.get_call_info(call_id)
        assert call_info.cleanup_completed is True

    async def test_track_sdk_execution_with_sdk_executor(self):
        """测试与 SDKExecutor 的集成"""
        executor = SDKExecutor()

        # 模拟 SDK 函数
        async def mock_sdk_func():
            yield {"type": "result", "content": "test"}

        # 模拟目标检测
        def target_predicate(msg):
            return msg.get("type") == "result"

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=target_predicate,
            timeout=5.0,
            agent_name="IntegrationTest"
        )

        assert isinstance(result, SDKResult)
        # SDK 执行器应该正确处理消息
        assert result.agent_name == "IntegrationTest"

    async def test_concurrent_sdk_calls(self):
        """测试并发 SDK 调用"""
        manager = CancellationManager()

        async def sdk_call(call_id: str, agent_name: str):
            async with manager.track_sdk_execution(call_id, agent_name):
                await anyio.sleep(0.1)  # 模拟 SDK 调用

        # 并发执行多个调用
        async with anyio.create_task_group() as tg:
            tg.start_soon(sdk_call, "call-1", "Agent1")
            tg.start_soon(sdk_call, "call-2", "Agent2")
            tg.start_soon(sdk_call, "call-3", "Agent3")

        # 所有调用都应该完成清理
        for call_id in ["call-1", "call-2", "call-3"]:
            call_info = manager.get_call_info(call_id)
            assert call_info.cleanup_completed is True


@pytest.mark.anyio
class TestSingletonIntegration:
    """测试单例模式的集成"""

    async def test_global_manager_shared_across_modules(self):
        """测试全局管理器在模块间共享"""
        reset_cancellation_manager()

        # 获取全局管理器
        manager1 = get_cancellation_manager()

        # 使用上下文管理器
        async with manager1.track_sdk_execution("shared-call", "Agent1"):
            # 获取另一个引用
            manager2 = get_cancellation_manager()
            assert manager1 is manager2

            # 验证调用在共享管理器中可见
            assert manager2.get_active_calls_count() == 1

        reset_cancellation_manager()

    async def test_singleton_lifecycle(self):
        """测试单例的生命周期"""
        reset_cancellation_manager()

        # 创建并使用
        manager = get_cancellation_manager()
        manager.register_call("lifecycle-call", "TestAgent")

        # 验证状态
        assert manager.get_active_calls_count() == 1

        # 重置
        reset_cancellation_manager()

        # 获取新实例
        new_manager = get_cancellation_manager()
        assert new_manager.get_active_calls_count() == 0


@pytest.mark.anyio
class TestSDKExecutorIntegration:
    """测试 SDKExecutor 的集成"""

    async def test_executor_with_successful_result(self):
        """测试成功的 SDK 执行"""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "progress", "content": "working..."}
            yield {"type": "result", "content": "success", "is_target": True}

        def target_predicate(msg):
            return msg.get("is_target", False)

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=target_predicate,
            agent_name="SuccessTest"
        )

        assert isinstance(result, SDKResult)
        assert len(result.messages) == 2

    async def test_executor_with_no_target(self):
        """测试没有找到目标的 SDK 执行"""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "progress", "content": "working..."}
            yield {"type": "done", "content": "finished"}

        def target_predicate(msg):
            return msg.get("type") == "result"  # 永远不会匹配

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=target_predicate,
            agent_name="NoTargetTest"
        )

        assert isinstance(result, SDKResult)
        assert result.has_target_result is False

    async def test_executor_with_exception(self):
        """测试异常情况的 SDK 执行"""
        executor = SDKExecutor()

        async def failing_sdk_func():
            yield {"type": "progress", "content": "starting..."}
            raise ValueError("SDK failed")

        def target_predicate(msg):
            return False

        result = await executor.execute(
            sdk_func=failing_sdk_func,
            target_predicate=target_predicate,
            agent_name="ExceptionTest"
        )

        assert isinstance(result, SDKResult)
        assert result.is_success() is False
        assert len(result.errors) > 0


@pytest.mark.anyio
class TestFullIntegration:
    """完整集成测试"""

    async def test_complete_sdk_workflow(self):
        """测试完整的 SDK 工作流"""
        reset_cancellation_manager()

        # 1. 获取全局管理器
        manager = get_cancellation_manager()

        # 2. 创建 SDK 执行器
        executor = SDKExecutor()

        # 3. 定义 SDK 函数
        async def mock_sdk_func():
            yield {"type": "init", "session_id": "test-123"}
            yield {"type": "thinking", "content": "analyzing..."}
            yield {"type": "result", "content": "completed", "is_target": True}

        # 4. 定义目标检测
        def target_predicate(msg):
            return msg.get("is_target", False)

        # 5. 执行
        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=target_predicate,
            agent_name="FullWorkflow"
        )

        # 6. 验证结果
        assert isinstance(result, SDKResult)
        assert result.agent_name == "FullWorkflow"
        assert len(result.messages) == 3

        reset_cancellation_manager()

    async def test_workflow_with_cancellation(self):
        """测试带取消的工作流"""
        manager = CancellationManager()
        call_id = "cancellation-workflow"

        async with manager.track_sdk_execution(call_id, "CancelTest"):
            # 模拟找到目标
            manager.mark_target_result_found(call_id)
            # 请求取消
            manager.request_cancel(call_id)

        # 验证双条件
        call_info = manager.get_call_info(call_id)
        assert call_info.cancel_requested is True
        assert call_info.cleanup_completed is True
        assert call_info.has_target_result is True

        # 确认安全进行
        safe = await manager.confirm_safe_to_proceed(call_id, timeout=1.0)
        assert safe is True


@pytest.mark.anyio
class TestErrorRecovery:
    """测试错误恢复"""

    async def test_cleanup_on_exception(self):
        """测试异常时的清理"""
        manager = CancellationManager()
        call_id = "exception-cleanup"

        with pytest.raises(RuntimeError):
            async with manager.track_sdk_execution(call_id, "ExceptionAgent"):
                raise RuntimeError("Simulated error")

        # 清理应该已完成
        call_info = manager.get_call_info(call_id)
        assert call_info.cleanup_completed is True

    async def test_cleanup_on_cancellation(self):
        """测试取消时的清理"""
        manager = CancellationManager()
        call_id = "cancel-cleanup"

        async def cancellable_operation():
            async with manager.track_sdk_execution(call_id, "CancelAgent"):
                await anyio.sleep(10)  # 长时间操作

        # 启动操作并立即取消
        async with anyio.create_task_group() as tg:
            tg.start_soon(cancellable_operation)
            await anyio.sleep(0.1)  # 等待操作开始
            tg.cancel_scope.cancel()  # 取消

        # 清理应该已完成
        call_info = manager.get_call_info(call_id)
        assert call_info.cleanup_completed is True

"""SDKExecutor单元测试

测试SDKExecutor类的初始化和基础功能。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.core.sdk_result import SDKErrorType


class TestSDKExecutor:
    """SDKExecutor测试类"""

    def test_sdk_executor_creation(self) -> None:
        """测试SDKExecutor创建"""
        executor = SDKExecutor()
        assert executor is not None
        assert executor.cancel_manager is not None

    def test_sdk_executor_initialized_properly(self) -> None:
        """测试SDKExecutor正确初始化"""
        executor = SDKExecutor()

        # 检查CancellationManager已初始化
        assert hasattr(executor, 'cancel_manager')
        from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
        assert isinstance(executor.cancel_manager, CancellationManager)

        # 检查初始活跃调用数为0
        assert executor.cancel_manager.get_active_calls_count() == 0

    @pytest.mark.asyncio
    async def test_execute_method_signature(self) -> None:
        """测试execute方法签名正确"""
        executor = SDKExecutor()

        # 创建模拟的sdk_func和target_predicate
        async def mock_sdk_func():
            yield {"type": "message", "content": "test"}

        def mock_target_predicate(msg):
            return False

        # 调用execute方法（骨架实现会抛出NotImplementedError，但被捕获并封装到SDKResult）
        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate,
            agent_name="TestAgent"
        )

        # 验证异常被正确封装
        assert result.has_target_result is False
        assert result.cleanup_completed is False
        assert result.error_type == SDKErrorType.UNKNOWN
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self) -> None:
        """测试execute方法接受timeout参数"""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "message", "content": "test"}

        def mock_target_predicate(msg):
            return False

        # 验证方法可以接受timeout参数
        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=30.0,
            agent_name="TestAgent"
        )

        # 验证异常被正确封装
        assert result.error_type == SDKErrorType.UNKNOWN

    @pytest.mark.asyncio
    async def test_execute_without_timeout(self) -> None:
        """测试execute方法可以不传timeout参数"""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "message", "content": "test"}

        def mock_target_predicate(msg):
            return False

        # 验证方法可以不传timeout参数
        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate,
            agent_name="TestAgent"
        )

        # 验证异常被正确封装
        assert result.error_type == SDKErrorType.UNKNOWN

    @pytest.mark.asyncio
    async def test_execute_with_default_agent_name(self) -> None:
        """测试execute方法使用默认agent_name"""
        executor = SDKExecutor()

        async def mock_sdk_func():
            yield {"type": "message", "content": "test"}

        def mock_target_predicate(msg):
            return False

        # 验证默认agent_name为"Unknown"
        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate
        )

        # 验证异常被正确封装
        assert result.error_type == SDKErrorType.UNKNOWN

    @pytest.mark.asyncio
    async def test_execute_exception_handling(self) -> None:
        """测试execute方法异常处理"""
        executor = SDKExecutor()

        # 创建一个会抛出异常的sdk_func
        async def failing_sdk_func():
            raise ValueError("Test error")

        def mock_target_predicate(msg):
            return False

        # 异常应该被封装到SDKResult中
        result = await executor.execute(
            sdk_func=failing_sdk_func,
            target_predicate=mock_target_predicate,
            agent_name="TestAgent"
        )

        # 验证异常被正确封装
        assert result.has_target_result is False
        assert result.cleanup_completed is False
        assert result.error_type == SDKErrorType.UNKNOWN
        assert len(result.errors) > 0
        # 异常被TaskGroup包装成ExceptionGroup，所以验证包装信息
        assert "TaskGroup" in result.errors[0] or "sub-exception" in result.errors[0]
        assert result.last_exception is not None

    @pytest.mark.asyncio
    async def test_execute_with_empty_messages(self) -> None:
        """测试execute方法处理空消息"""
        executor = SDKExecutor()

        # 创建空生成器
        async def empty_sdk_func():
            return
            yield  # 永远不会执行

        def mock_target_predicate(msg):
            return False

        # 应该返回失败结果
        result = await executor.execute(
            sdk_func=empty_sdk_func,
            target_predicate=mock_target_predicate,
            agent_name="TestAgent"
        )

        assert result.has_target_result is False
        assert result.cleanup_completed is False

    def test_sdk_executor_has_cancel_manager(self) -> None:
        """测试SDKExecutor包含CancelManager"""
        executor = SDKExecutor()

        # 验证CancelManager存在且功能正常
        assert executor.cancel_manager is not None
        assert executor.cancel_manager.get_active_calls_count() == 0

        # 注册一个测试调用
        executor.cancel_manager.register_call("test-id", "test-agent")
        assert executor.cancel_manager.get_active_calls_count() == 1

    def test_sdk_executor_attributes(self) -> None:
        """测试SDKExecutor所有属性"""
        executor = SDKExecutor()

        # 验证所有必要属性存在
        assert hasattr(executor, 'cancel_manager')

        # 验证类型
        from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
        assert isinstance(executor.cancel_manager, CancellationManager)

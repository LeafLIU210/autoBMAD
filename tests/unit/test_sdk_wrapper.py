"""
sdk_wrapper.py 单元测试
测试 SafeClaudeSDK 和相关类的核心功能
"""
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from anyio.abc import TaskGroup

# Import the classes to test
from autoBMAD.epic_automation.sdk_wrapper import (
    SafeAsyncGenerator,
    SDKMessageTracker,
    SafeClaudeSDK,
)


class TestSafeAsyncGenerator:
    """测试 SafeAsyncGenerator 类"""

    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        async def mock_generator():
            yield "test"

        # 正确传递generator函数调用后的结果
        generator = SafeAsyncGenerator(mock_generator())
        assert generator is not None
        assert not generator._closed

    @pytest.mark.asyncio
    async def test_async_iteration(self):
        """测试异步迭代"""
        async def mock_generator():
            yield "message1"
            yield "message2"

        generator = SafeAsyncGenerator(mock_generator())
        messages = []
        async for msg in generator:
            messages.append(msg)

        assert messages == ["message1", "message2"]

    @pytest.mark.asyncio
    async def test_aclose(self):
        """测试异步关闭"""
        async def mock_generator():
            yield "test"

        generator = SafeAsyncGenerator(mock_generator())
        await generator.aclose()

        assert generator._closed

    @pytest.mark.asyncio
    async def test_aclose_idempotent(self):
        """测试异步关闭的幂等性"""
        async def mock_generator():
            yield "test"

        generator = SafeAsyncGenerator(mock_generator())
        await generator.aclose()
        await generator.aclose()  # 应该不报错

        assert generator._closed


class TestSDKMessageTracker:
    """测试 SDKMessageTracker 类"""

    @pytest.mark.asyncio
    async def test_message_update(self):
        """测试消息更新"""
        tracker = SDKMessageTracker()

        # 模拟消息
        mock_message = MagicMock()
        mock_message.content = "test message"
        mock_message.type = "assistant"

        tracker.update(mock_message)

        assert len(tracker.messages) == 1
        assert tracker.messages[0] == mock_message
        assert tracker.last_message == mock_message

    @pytest.mark.asyncio
    async def test_multiple_message_tracking(self):
        """测试多消息跟踪"""
        tracker = SDKMessageTracker()

        # 添加多个消息
        for i in range(3):
            mock_message = MagicMock()
            mock_message.content = f"message {i}"
            tracker.update(mock_message)

        assert len(tracker.messages) == 3
        assert tracker.last_message.content == "message 2"

    @pytest.mark.asyncio
    async def test_periodic_display(self):
        """测试定期显示功能"""
        tracker = SDKMessageTracker()
        mock_message = MagicMock()
        mock_message.content = "test"

        # 应该不报错
        tracker.update(mock_message)

        # 验证方法存在
        assert hasattr(tracker, 'display_periodic_update')

    @pytest.mark.asyncio
    async def test_final_summary(self):
        """测试最终摘要"""
        tracker = SDKMessageTracker()
        mock_message = MagicMock()
        mock_message.content = "test"

        tracker.update(mock_message)

        # 验证方法存在且可调用
        assert hasattr(tracker, 'finalize')
        summary = tracker.finalize()
        assert isinstance(summary, dict)


class TestSafeClaudeSDK:
    """测试 SafeClaudeSDK 类"""

    @pytest.mark.asyncio
    async def test_sdk_init(self):
        """测试SDK初始化"""
        sdk = SafeClaudeSDK(
            prompt="test prompt",
            options=MagicMock()
        )

        assert sdk.prompt == "test prompt"
        assert sdk.options is not None

    @pytest.mark.asyncio
    async def test_message_extraction(self):
        """测试消息提取"""
        sdk = SafeClaudeSDK(prompt="test")

        # 模拟不同类型的消息
        assistant_msg = MagicMock()
        assistant_msg.type = "assistant"
        assistant_msg.content = "assistant message"

        result_msg = MagicMock()
        result_msg.type = "result"
        result_msg.content = "result message"

        # 测试消息分类
        assert sdk._classify_message_type(assistant_msg) == "assistant"
        assert sdk._classify_message_type(result_msg) == "result"

    @pytest.mark.asyncio
    async def test_extract_message_content_various_types(self):
        """测试多种消息类型的内容提取"""
        sdk = SafeClaudeSDK(prompt="test")

        # 模拟Assistant消息
        assistant_msg = MagicMock()
        assistant_msg.type = "assistant"
        assistant_msg.content = "assistant content"

        # 模拟Result消息
        result_msg = MagicMock()
        result_msg.type = "result"
        result_msg.content = "result content"

        # 测试内容提取
        content1 = sdk._extract_message_content(assistant_msg)
        assert content1 == "assistant content"

        content2 = sdk._extract_message_content(result_msg)
        assert content2 == "result content"

    @pytest.mark.asyncio
    async def test_execute_success_flow(self):
        """测试成功执行流程"""
        sdk = SafeClaudeSDK(prompt="test prompt")

        # 模拟成功的SDK调用
        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            # 模拟异步生成器
            async def mock_generator():
                yield MagicMock(type="assistant", content="response")
                yield MagicMock(type="result", content="done")

            mock_query.return_value = mock_generator()

            # 模拟CancellationManager
            mock_manager = MagicMock()
            mock_manager.track_sdk_execution = MagicMock()
            mock_manager.track_sdk_execution.return_value.__aenter__ = AsyncMock()
            mock_manager.track_sdk_execution.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await sdk._execute_with_manager(mock_manager, "test_call_id")

            # 验证结果
            assert result is True

    @pytest.mark.asyncio
    async def test_execute_error_handling(self):
        """测试错误处理"""
        sdk = SafeClaudeSDK(prompt="test prompt")

        # 模拟SDK调用抛出异常
        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            mock_query.side_effect = Exception("Test error")

            # 模拟CancellationManager
            mock_manager = MagicMock()
            mock_manager.track_sdk_execution = MagicMock()
            mock_manager.track_sdk_execution.return_value.__aenter__ = AsyncMock()
            mock_manager.track_sdk_execution.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await sdk._execute_with_manager(mock_manager, "test_call_id")

            # 错误情况下应该返回False
            assert result is False

    @pytest.mark.asyncio
    async def test_cancel_scope_handling(self):
        """测试取消范围处理"""
        sdk = SafeClaudeSDK(prompt="test prompt")

        # 模拟CancellationManager
        mock_manager = MagicMock()
        mock_manager.check_cancellation_type.return_value = "after_success"
        mock_manager.wait_for_cancellation_complete = AsyncMock()

        # 模拟CancelledError
        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            async def mock_generator():
                yield MagicMock(type="assistant", content="response")

            mock_query.return_value = mock_generator()
            mock_manager.track_sdk_execution = MagicMock()
            mock_manager.track_sdk_execution.return_value.__aenter__ = AsyncMock()
            mock_manager.track_sdk_execution.return_value.__aexit__ = AsyncMock(
                side_effect=asyncio.CancelledError()
            )

            result = await sdk._execute_with_manager(mock_manager, "test_call_id")

            # 取消后应该返回True（根据管理器决策）
            assert result is True

    @pytest.mark.asyncio
    async def test_cross_task_cancel_scope_recovery(self):
        """测试跨任务取消范围恢复"""
        sdk = SafeClaudeSDK(prompt="test prompt")

        # 模拟CancellationManager确认工作已完成
        mock_manager = MagicMock()
        mock_manager.check_cancellation_type.return_value = "after_success"
        mock_manager.wait_for_cancellation_complete = AsyncMock()

        with patch('autoBMAD.epic_automation.sdk_wrapper.query') as mock_query:
            async def mock_generator():
                yield MagicMock(type="assistant", content="completed")

            mock_query.return_value = mock_generator()
            mock_manager.track_sdk_execution = MagicMock()
            mock_manager.track_sdk_execution.return_value.__aenter__ = AsyncMock()
            mock_manager.track_sdk_execution.return_value.__aexit__ = AsyncMock(
                side_effect=asyncio.CancelledError()
            )

            result = await sdk._execute_with_manager(mock_manager, "test_call_id")

            # 验证取消被正确处理
            assert result is True
            mock_manager.wait_for_cancellation_complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_result_extraction(self):
        """测试结果提取逻辑"""
        sdk = SafeClaudeSDK(prompt="test")

        # 模拟包含结果的响应
        result_message = MagicMock()
        result_message.type = "result"
        result_message.content = "Task completed successfully"

        # 测试结果提取
        extracted = sdk._extract_result_data(result_message)
        assert extracted == "Task completed successfully"

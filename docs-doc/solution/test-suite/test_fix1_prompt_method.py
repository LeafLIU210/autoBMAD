"""Fix-1: ClaudeSessionWrapper.prompt() 方法修复测试

测试目标:
1. 验证 prompt() 使用 query() 而非 send_message()
2. 验证 prompt() 使用 receive_messages() 而非 messages()
3. 验证 prompt() 是 async generator 函数
4. 验证 prompt() 正确 yield 消息对象
"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock


async def async_iter(items: list):
    """辅助函数：创建异步迭代器"""
    for item in items:
        yield item


class TestPromptMethodAPI:
    """测试 prompt() 方法使用正确的 SDK API"""
    
    @pytest.mark.asyncio
    async def test_prompt_calls_query_not_send_message(self, temp_test_dir: Path):
        """TEST-F1-001: prompt() 调用 query() 而非 send_message()"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-001",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt("hello world"):
            pass
        
        # 验证使用新API
        mock_client.query.assert_awaited_once_with("hello world")
        # 验证不使用旧API
        mock_client.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_prompt_uses_receive_messages_not_messages(self, temp_test_dir: Path):
        """TEST-F1-002: prompt() 使用 receive_messages() 而非 messages()"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        mock_client.messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-002",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt("test"):
            pass
        
        mock_client.receive_messages.assert_called_once()
        mock_client.messages.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_prompt_yields_all_messages(self, temp_test_dir: Path):
        """TEST-F1-003: prompt() 正确 yield 所有消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        expected_messages = [
            {"role": "assistant", "content": "Hello"},
            {"role": "assistant", "content": "World"},
        ]
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter(expected_messages))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-003",
            work_dir=temp_test_dir
        )
        
        received = []
        async for msg in wrapper.prompt("test"):
            received.append(msg)
        
        assert received == expected_messages


class TestPromptMethodSignature:
    """测试 prompt() 方法签名和类型"""
    
    def test_prompt_is_async_generator(self, temp_test_dir: Path):
        """TEST-F1-004: prompt() 是 async generator 函数"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = Mock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-004",
            work_dir=temp_test_dir
        )
        
        # 调用返回的是 async generator，不是 coroutine
        result = wrapper.prompt("test")
        assert inspect.isasyncgen(result), f"Expected async generator, got {type(result)}"
        assert not inspect.iscoroutine(result), "Should not be a coroutine"
    
    def test_prompt_accepts_message_param(self, temp_test_dir: Path):
        """TEST-F1-005: prompt() 接受 message 参数"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = Mock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-005",
            work_dir=temp_test_dir
        )
        
        # 验证可以接受消息参数
        gen = wrapper.prompt("test message")
        assert inspect.isasyncgen(gen)


class TestPromptMethodEdgeCases:
    """测试 prompt() 边界情况"""
    
    @pytest.mark.asyncio
    async def test_prompt_with_empty_message(self, temp_test_dir: Path):
        """TEST-F1-006: prompt() 处理空消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-006",
            work_dir=temp_test_dir
        )
        
        messages = []
        async for msg in wrapper.prompt(""):
            messages.append(msg)
        
        mock_client.query.assert_awaited_once_with("")
        assert messages == []
    
    @pytest.mark.asyncio
    async def test_prompt_with_large_message(self, temp_test_dir: Path):
        """TEST-F1-007: prompt() 处理大消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        large_message = "x" * 10000
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-007",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt(large_message):
            pass
        
        mock_client.query.assert_awaited_once_with(large_message)

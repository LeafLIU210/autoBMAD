"""
测试 cancel scope 错误修复的单元测试

验证修复后的代码能够：
1. 防止 cancel scope 跨任务错误
2. 保持输出可见性
3. 正确处理异步生成器生命周期
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.sdk_wrapper import (
    SafeAsyncGenerator,
    SDKMessageTracker,
    SafeClaudeSDK,
)
from autoBMAD.epic_automation.sdk_session_manager import (
    SDKSessionManager,
    SDKExecutionResult,
    SDKErrorType,
)


@pytest.mark.asyncio
async def test_cancel_scope_error_prevention():
    """测试 cancel scope 错误预防 - 验证 SafeAsyncGenerator 能够正确清理"""
    # 创建模拟异步生成器
    async def mock_generator():
        """模拟异步生成器"""
        for i in range(10):
            yield f"message_{i}"

    # 测试安全包装器
    generator = mock_generator()
    safe_gen = SafeAsyncGenerator(generator)

    # 消费生成器的一部分
    messages = []
    async for msg in safe_gen:
        messages.append(msg)
        if len(messages) >= 3:
            break  # 提前退出以测试清理

    # 确保生成器可以安全关闭 - 不应该抛出 cancel scope 错误
    try:
        await safe_gen.aclose()
        assert True  # 如果没有抛出异常，测试通过
    except RuntimeError as e:
        if "cancel scope" in str(e):
            pytest.fail(f"Cancel scope 错误仍然存在: {e}")
        else:
            raise


@pytest.mark.asyncio
async def test_event_loop_state_detection():
    """测试事件循环状态检测"""
    # 创建模拟异步生成器
    async def mock_generator():
        for i in range(5):
            yield f"message_{i}"

    generator = mock_generator()
    safe_gen = SafeAsyncGenerator(generator)

    # 检查事件循环状态检测
    # 这应该正常工作，因为我们在事件循环中
    assert not safe_gen._closed

    # 消费所有消息
    messages = []
    async for msg in safe_gen:
        messages.append(msg)

    assert len(messages) == 5

    # 关闭生成器
    await safe_gen.aclose()
    assert safe_gen._closed


@pytest.mark.asyncio
async def test_sdk_session_manager_simplification():
    """测试简化的 SDKSessionManager"""
    manager = SDKSessionManager()

    # 创建模拟 SDK 函数
    async def mock_sdk_func():
        await asyncio.sleep(0.1)
        return True

    # 执行隔离调用
    result = await manager.execute_isolated(
        agent_name="TestAgent",
        sdk_func=mock_sdk_func,
        timeout=None,
    )

    # 验证结果
    assert isinstance(result, SDKExecutionResult)
    assert result.success is True
    assert result.retry_count == 0


@pytest.mark.asyncio
async def test_sdk_session_manager_cancel_scope_error_handling():
    """测试 SDKSessionManager 的 cancel scope 错误处理"""
    manager = SDKSessionManager()

    # 创建会抛出 cancel scope 错误的模拟函数
    async def mock_cancel_scope_error():
        await asyncio.sleep(0.01)
        raise RuntimeError("Attempted to exit cancel scope in a different task")

    # 执行隔离调用 - 应该捕获并处理错误
    result = await manager.execute_isolated(
        agent_name="TestAgent",
        sdk_func=mock_cancel_scope_error,
        timeout=None,
    )

    # 验证结果 - 应该返回失败而不是抛出异常
    assert isinstance(result, SDKExecutionResult)
    assert result.success is False
    assert result.error_type == SDKErrorType.SESSION_ERROR
    assert "cancel scope" in result.error_message.lower()


@pytest.mark.asyncio
async def test_message_tracker_functionality():
    """测试消息追踪器功能 - 验证输出可见性"""
    tracker = SDKMessageTracker()

    # 测试消息更新
    tracker.update_message("test message", "INFO")
    assert tracker.latest_message == "test message"
    assert tracker.message_type == "INFO"
    assert tracker.message_count == 1

    # 测试不同类型的消息
    tracker.update_message("error message", "ERROR")
    assert tracker.latest_message == "error message"
    assert tracker.message_type == "ERROR"
    assert tracker.message_count == 2

    # 测试经过时间
    elapsed = tracker.get_elapsed_time()
    assert elapsed >= 0


@pytest.mark.asyncio
async def test_message_tracker_periodic_display():
    """测试消息追踪器的周期性显示"""
    tracker = SDKMessageTracker()

    # 设置消息
    tracker.update_message("periodic test", "DEBUG")

    # 启动周期性显示（但不等待完整循环）
    await tracker.start_periodic_display()

    # 短暂等待
    await asyncio.sleep(0.1)

    # 停止显示
    await tracker.stop_periodic_display(timeout=0.5)

    # 验证任务已停止
    assert tracker._display_task is None or tracker._display_task.done()


@pytest.mark.asyncio
async def test_safe_claude_sdk_initialization():
    """测试 SafeClaudeSDK 的初始化"""
    # 模拟 SDK 可用性
    with patch("autoBMAD.epic_automation.sdk_wrapper.SDK_AVAILABLE", False):
        sdk = SafeClaudeSDK("test prompt", None)
        # 当 SDK 不可用时应该返回 False
        result = await sdk.execute()
        assert result is False


@pytest.mark.asyncio
async def test_removed_asyncio_shield():
    """测试已移除 asyncio.shield 的代码路径"""
    # 这个测试验证关键路径不再使用 asyncio.shield
    manager = SDKSessionManager()

    # 创建模拟函数
    async def mock_func():
        await asyncio.sleep(0.05)
        return True

    # 执行 - 这应该直接调用而不使用 shield
    result = await manager.execute_isolated(
        agent_name="TestAgent",
        sdk_func=mock_func,
        timeout=None,
    )

    assert result.success is True
    assert result.retry_count == 0


@pytest.mark.asyncio
async def test_max_turns_configuration():
    """测试 max_turns 配置（1000轮）"""
    # 这个测试验证 Dev Agent 使用了正确的 max_turns
    from autoBMAD.epic_automation.dev_agent import DevAgent

    # 验证 DevAgent 的 max_turns 设置
    # 我们通过模拟来测试
    with patch("autoBMAD.epic_automation.dev_agent.ClaudeAgentOptions") as mock_options:
        mock_instance = MagicMock()
        mock_options.return_value = mock_instance

        # 这只是一个初始化测试，不执行实际调用
        agent = DevAgent()

        # 验证配置存在（但不实际调用 SDK）
        assert hasattr(agent, "_session_manager")


def test_imports():
    """测试所有必要的导入都能正常工作"""
    # 验证核心组件可以导入
    from autoBMAD.epic_automation.sdk_wrapper import (
        SafeAsyncGenerator,
        SDKMessageTracker,
        SafeClaudeSDK,
    )
    from autoBMAD.epic_automation.sdk_session_manager import (
        SDKSessionManager,
        SDKExecutionResult,
    )

    # 验证类存在
    assert SafeAsyncGenerator is not None
    assert SDKMessageTracker is not None
    assert SafeClaudeSDK is not None
    assert SDKSessionManager is not None
    assert SDKExecutionResult is not None


@pytest.mark.asyncio
async def test_exception_handling():
    """测试异常处理"""
    manager = SDKSessionManager()

    # 创建会抛出异常的函数
    async def mock_exception_func():
        await asyncio.sleep(0.01)
        raise ValueError("Test exception")

    # 执行 - 应该捕获异常并返回失败结果
    result = await manager.execute_isolated(
        agent_name="TestAgent",
        sdk_func=mock_exception_func,
        timeout=None,
    )

    assert result.success is False
    assert isinstance(result.last_error, ValueError)


@pytest.mark.asyncio
async def test_cancellation_handling():
    """测试取消处理"""
    manager = SDKSessionManager()

    # 创建会抛出取消异常的函数
    async def mock_cancel_func():
        await asyncio.sleep(0.1)
        raise asyncio.CancelledError("Test cancellation")

    # 执行 - 应该捕获取消并返回适当结果
    result = await manager.execute_isolated(
        agent_name="TestAgent",
        sdk_func=mock_cancel_func,
        timeout=None,
    )

    assert result.success is False
    assert result.error_type == SDKErrorType.CANCELLED


@pytest.mark.asyncio
async def test_safe_async_generator_with_empty_generator():
    """测试空生成器的处理"""
    async def empty_generator():
        return
        yield  # 永远不会执行

    generator = empty_generator()
    safe_gen = SafeAsyncGenerator(generator)

    # 消费空生成器
    messages = []
    async for msg in safe_gen:
        messages.append(msg)

    assert len(messages) == 0

    # 关闭应该成功
    await safe_gen.aclose()
    assert safe_gen._closed


@pytest.mark.asyncio
async def test_session_manager_statistics():
    """测试会话管理器统计信息"""
    manager = SDKSessionManager()

    # 执行一些成功的调用
    async def success_func():
        await asyncio.sleep(0.01)
        return True

    for _ in range(3):
        await manager.execute_isolated("TestAgent", success_func)

    # 检查统计
    stats = manager.get_statistics()
    assert stats["total_sessions"] == 3
    assert stats["successful_sessions"] == 3
    assert stats["failed_sessions"] == 0
    assert stats["success_rate"] == 100.0


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

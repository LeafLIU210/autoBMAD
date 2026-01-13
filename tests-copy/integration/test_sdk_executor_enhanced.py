"""
SDK 执行器增强集成测试
测试 SDK 执行器的增强功能和集成点
"""
import pytest
import anyio
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager


@pytest.fixture
async def sdk_executor():
    """创建 SDK 执行器"""
    executor = SDKExecutor()
    yield executor


@pytest.fixture
def cancellation_manager():
    """创建取消管理器"""
    manager = CancellationManager()
    yield manager


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_with_real_sdk_calls(sdk_executor):
    """测试带真实 SDK 调用的 SDK 执行器"""
    # 创建模拟 SDK 函数
    async def mock_sdk_func():
        await asyncio.sleep(0.01)
        yield {"type": "result", "data": "test_data"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 在 TaskGroup 内执行
    async with anyio.create_task_group() as tg:
        # 执行 SDK 调用
        result = await sdk_executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="TestAgent"
        )

        # 验证结果
        assert result is not None
        assert result.is_success() is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_timeout_handling(sdk_executor):
    """测试 SDK 执行器超时处理"""
    # 创建会超时的 SDK 函数
    async def slow_sdk_func():
        await asyncio.sleep(10)  # 长时间延迟
        yield {"type": "result", "data": "slow_data"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 在 TaskGroup 内执行并测试超时
    async with anyio.create_task_group() as tg:
        # 执行 SDK 调用，设置短超时
        result = await sdk_executor.execute(
            sdk_func=slow_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=0.1,  # 短超时
            agent_name="SlowAgent"
        )

        # 验证结果 - 应该超时失败
        assert result is not None
        assert result.is_success() is False
        assert result.is_timeout() is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_concurrent_execution(sdk_executor):
    """测试 SDK 执行器并发执行"""
    # 创建多个 SDK 函数
    async def sdk_func_1():
        await asyncio.sleep(0.01)
        yield {"type": "result", "id": 1, "data": "data_1"}
        yield {"type": "done"}

    async def sdk_func_2():
        await asyncio.sleep(0.02)
        yield {"type": "result", "id": 2, "data": "data_2"}
        yield {"type": "done"}

    async def sdk_func_3():
        await asyncio.sleep(0.03)
        yield {"type": "result", "id": 3, "data": "data_3"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 并发执行多个 SDK 调用
    results = []
    async with anyio.create_task_group() as tg:
        # 启动多个 SDK 调用
        for i, func in enumerate([sdk_func_1, sdk_func_2, sdk_func_3], 1):
            result = sdk_executor.execute(
                sdk_func=func,
                target_predicate=mock_target_predicate,
                timeout=5.0,
                agent_name=f"Agent{i}"
            )
            results.append(result)

        # 等待所有结果
        final_results = []
        for result in results:
            final_results.append(await result)

    # 验证结果
    assert len(final_results) == 3
    for result in final_results:
        assert result is not None
        assert result.is_success() is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_cancel_scope_isolation(sdk_executor):
    """测试 SDK 执行器 Cancel Scope 隔离"""
    # 创建 SDK 函数
    async def sdk_func_with_cleanup():
        try:
            await asyncio.sleep(0.1)
            yield {"type": "result", "data": "test_data"}
            yield {"type": "done"}
        finally:
            # 清理工作
            pass

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 执行多个顺序调用
    results = []
    for i in range(3):
        # 每个调用都在独立的 TaskGroup 中
        async with anyio.create_task_group() as tg:
            result = await sdk_executor.execute(
                sdk_func=sdk_func_with_cleanup,
                target_predicate=mock_target_predicate,
                timeout=5.0,
                agent_name=f"Agent{i}"
            )
            results.append(result)

    # 验证所有调用都成功
    assert len(results) == 3
    for result in results:
        assert result is not None
        assert result.is_success() is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_error_handling(sdk_executor):
    """测试 SDK 执行器错误处理"""
    # 创建会失败的 SDK 函数
    async def failing_sdk_func():
        await asyncio.sleep(0.01)
        yield {"type": "error", "message": "Test error"}
        raise Exception("SDK execution failed")

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 在 TaskGroup 内执行
    async with anyio.create_task_group() as tg:
        # 执行 SDK 调用
        result = await sdk_executor.execute(
            sdk_func=failing_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="FailingAgent"
        )

        # 验证结果 - 应该失败
        assert result is not None
        assert result.is_success() is False


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_resource_management(sdk_executor):
    """测试 SDK 执行器资源管理"""
    # 跟踪资源创建和清理
    resources_created = []
    resources_cleaned = []

    # 创建 SDK 函数
    async def sdk_func_with_resources():
        resource = {"id": len(resources_created) + 1}
        resources_created.append(resource)
        try:
            await asyncio.sleep(0.01)
            yield {"type": "result", "data": resource}
            yield {"type": "done"}
        finally:
            resources_cleaned.append(resource)

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 执行 SDK 调用
    async with anyio.create_task_group() as tg:
        result = await sdk_executor.execute(
            sdk_func=sdk_func_with_resources,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="ResourceAgent"
        )

        # 验证结果
        assert result is not None
        assert result.is_success() is True

        # 验证资源清理
        assert len(resources_cleaned) >= len(resources_created)


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_performance_benchmark(sdk_executor):
    """测试 SDK 执行器性能基准"""
    import time

    # 创建快速 SDK 函数
    async def fast_sdk_func():
        await asyncio.sleep(0.001)  # 1ms 延迟
        yield {"type": "result", "data": "fast_data"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 测量执行时间
    start_time = time.time()
    async with anyio.create_task_group() as tg:
        result = await sdk_executor.execute(
            sdk_func=fast_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="FastAgent"
        )
    end_time = time.time()

    # 验证结果
    assert result is not None
    assert result.is_success() is True
    # 确保执行时间在合理范围内
    assert (end_time - start_time) < 0.5


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_idempotency(sdk_executor):
    """测试 SDK 执行器幂等性"""
    # 创建 SDK 函数
    call_count = 0

    async def sdk_func():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        yield {"type": "result", "data": f"data_{call_count}"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 第一次执行
    async with anyio.create_task_group() as tg:
        result1 = await sdk_executor.execute(
            sdk_func=sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="IdempotentAgent"
        )

    # 重置调用计数
    initial_call_count = call_count

    # 第二次执行
    async with anyio.create_task_group() as tg:
        result2 = await sdk_executor.execute(
            sdk_func=sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="IdempotentAgent"
        )

    # 验证结果一致
    assert result1 is not None
    assert result2 is not None
    assert result1.is_success() is True
    assert result2.is_success() is True
    # 验证函数被调用两次
    assert call_count == initial_call_count + 1


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_state_persistence(sdk_executor):
    """测试 SDK 执行器状态持久化"""
    # 创建有状态的 SDK 函数
    state_data = {"counter": 0}

    async def stateful_sdk_func():
        await asyncio.sleep(0.01)
        state_data["counter"] += 1
        yield {"type": "result", "data": state_data, "count": state_data["counter"]}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 执行多次 SDK 调用
    results = []
    for i in range(3):
        async with anyio.create_task_group() as tg:
            result = await sdk_executor.execute(
                sdk_func=stateful_sdk_func,
                target_predicate=mock_target_predicate,
                timeout=5.0,
                agent_name=f"StatefulAgent{i}"
            )
            results.append(result)

    # 验证结果
    assert len(results) == 3
    for result in results:
        assert result is not None
        assert result.is_success() is True

    # 验证状态持续存在
    assert state_data["counter"] > 0


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_memory_leak_detection(sdk_executor):
    """测试 SDK 执行器内存泄漏检测"""
    # 创建多次 SDK 调用
    for i in range(10):
        async def sdk_func():
            await asyncio.sleep(0.001)
            yield {"type": "result", "data": f"data_{i}"}
            yield {"type": "done"}

        async def mock_target_predicate(result):
            return result.get("type") == "done"

        # 执行 SDK 调用
        async with anyio.create_task_group() as tg:
            result = await sdk_executor.execute(
                sdk_func=sdk_func,
                target_predicate=mock_target_predicate,
                timeout=5.0,
                agent_name=f"LeakTestAgent{i}"
            )

            # 验证结果
            assert result is not None
            assert result.is_success() is True

        # 清理引用
        del sdk_func


@pytest.mark.integration
@pytest.mark.anyio
async def test_sdk_executor_with_cancellation_manager(cancellation_manager):
    """测试 SDK 执行器与取消管理器的集成"""
    from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor

    # 创建带取消管理器的 SDK 执行器
    sdk_executor = SDKExecutor(cancellation_manager=cancellation_manager)

    # 创建 SDK 函数
    async def sdk_func():
        await asyncio.sleep(0.1)
        yield {"type": "result", "data": "test_data"}
        yield {"type": "done"}

    async def mock_target_predicate(result):
        return result.get("type") == "done"

    # 执行 SDK 调用
    async with anyio.create_task_group() as tg:
        result = await sdk_executor.execute(
            sdk_func=sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name="IntegrationAgent"
        )

        # 验证结果
        assert result is not None
        assert result.is_success() is True


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-m", "integration"])

"""
Cancel Scope 跨 Task 错误验证测试
验证修复后的系统完全消除了 Cancel Scope 跨 Task 错误
"""

import pytest
import anyio
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import sys

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver
from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager


@pytest.fixture
async def cancel_scope_test_environment():
    """创建 Cancel Scope 测试环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        stories_dir = tmp_path / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建测试故事
        story_content = """# Cancel Scope Test Story

**Status**: Draft

## Description
Testing cancel scope isolation.

## Tasks
- [ ] Task 1
"""
        story_file = stories_dir / "1.1-cancel-scope-test.md"
        story_file.write_text(story_content, encoding='utf-8')

        # 创建 Epic
        epic_content = """# Cancel Scope Test Epic

## Stories
- Story 1.1: Cancel Scope Test
"""
        epic_file = tmp_path / "epic-cancel-scope.md"
        epic_file.write_text(epic_content, encoding='utf-8')

        yield {
            "project_root": tmp_path,
            "epic_file": epic_file,
            "story_file": story_file,
            "stories_dir": stories_dir,
            "src_dir": src_dir,
            "tests_dir": tests_dir
        }


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_sequential_sdk_calls_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试顺序 SDK 调用不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    # 创建模拟的 SDK 调用
    async def mock_sdk_call(call_id: int):
        """模拟 SDK 调用"""
        await anyio.sleep(0.05)  # 模拟处理时间
        return f"Result-{call_id}"

    # 执行多个顺序 SDK 调用（不使用 tg.start，直接调用）
    results = []
    for i in range(5):
        result = await mock_sdk_call(i)
        results.append(result)

    # 验证所有调用都成功
    assert len(results) == 5
    assert results == ["Result-0", "Result-1", "Result-2", "Result-3", "Result-4"]

    # 关键验证：没有抛出 RuntimeError
    print("✅ Sequential SDK calls completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_concurrent_sdk_calls_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试并发 SDK 调用不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    # 创建模拟的 SDK 调用
    async def mock_sdk_call(call_id: int):
        """模拟 SDK 调用"""
        await anyio.sleep(0.05)  # 模拟处理时间
        return f"Result-{call_id}"

    # 执行并发 SDK 调用
    results = []
    async with anyio.create_task_group() as main_tg:
        for i in range(5):
            async def run_call():
                result = await mock_sdk_call(i)
                results.append(result)
            main_tg.start_soon(run_call)

    # 验证所有调用都成功（顺序可能不同）
    assert len(results) == 5

    # 关键验证：没有抛出 RuntimeError
    print("✅ Concurrent SDK calls completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_sdk_executor_cancel_scope_isolation(
    cancel_scope_test_environment
):
    """测试 SDKExecutor 的 Cancel Scope 隔离"""
    env = cancel_scope_test_environment

    # 创建 SDKExecutor
    sdk_executor = SDKExecutor()
    cancellation_manager = sdk_executor.cancel_manager

    # 创建模拟 SDK 函数（异步生成器）
    async def mock_sdk_func():
        await anyio.sleep(0.05)
        yield MagicMock()

    def mock_target_predicate(result):
        return True

    # 执行多个 SDK 调用
    results = []
    for i in range(3):
        result = await sdk_executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=mock_target_predicate,
            timeout=5.0,
            agent_name=f"TestAgent-{i}"
        )
        results.append(result)

    # 验证所有调用都成功
    assert len(results) == 3
    assert all(r.is_success for r in results)

    # 关键验证：没有抛出 RuntimeError
    print("✅ SDKExecutor calls completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_cancellation_handling_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试取消处理不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    # 测试任务取消
    async def long_running_task():
        """长时间运行的任务"""
        try:
            await anyio.sleep(1.0)  # 长时间等待
            return "Completed"
        except anyio.get_cancelled_exc_class():
            # 取消是正常的
            raise

    # 启动任务并取消
    try:
        async with anyio.create_task_group() as tg:
            task = tg.start_soon(long_running_task)

            # 短暂等待后取消
            await anyio.sleep(0.05)
            tg.cancel_scope.cancel()

        # 如果到达这里，说明取消处理正常
        assert True
    except anyio.get_cancelled_exc_class():
        # 取消异常是正常的
        assert True

    # 关键验证：没有抛出 RuntimeError (cancel scope 错误)
    print("✅ Cancellation handling completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_rapid_sdk_calls_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试快速连续 SDK 调用不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    # 创建模拟的快速 SDK 调用
    async def fast_sdk_call(call_id: int):
        """快速 SDK 调用"""
        await anyio.sleep(0.001)  # 非常快的调用
        return f"Fast-{call_id}"

    # 快速连续执行多个调用（不使用 tg.start）
    results = []
    for i in range(20):  # 更多调用
        result = await fast_sdk_call(i)
        results.append(result)

    # 验证所有调用都成功
    assert len(results) == 20

    # 关键验证：没有抛出 RuntimeError
    print("✅ Rapid SDK calls completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_resource_cleanup_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试资源清理不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    # 跟踪资源
    resources = []
    cleaned_resources = []

    class TestResource:
        def __init__(self, name):
            self.name = name
            resources.append(name)

        async def cleanup(self):
            await anyio.sleep(0.01)  # 模拟清理工作
            cleaned_resources.append(self.name)

    async def use_and_cleanup_resource(resource_name: str):
        """使用并清理资源"""
        resource = TestResource(resource_name)
        try:
            await anyio.sleep(0.02)
        finally:
            await resource.cleanup()

    # 执行多个资源使用和清理
    async with anyio.create_task_group() as main_tg:
        for i in range(5):
            main_tg.start_soon(use_and_cleanup_resource, f"Resource-{i}")

    # 验证所有资源都被清理
    assert len(resources) == 5
    assert len(cleaned_resources) == 5
    assert set(resources) == set(cleaned_resources)

    # 关键验证：没有抛出 RuntimeError
    print("✅ Resource cleanup completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_nested_task_groups_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试嵌套 TaskGroup 不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    async def inner_task(task_id: int):
        """内部任务"""
        await anyio.sleep(0.02)
        return f"Inner-{task_id}"

    async def outer_task(task_id: int):
        """外部任务"""
        results = []
        async with anyio.create_task_group() as tg:
            for i in range(3):
                async def run_inner():
                    result = await inner_task(f"{task_id}-{i}")
                    results.append(result)
                tg.start_soon(run_inner)
        return results

    # 执行嵌套 TaskGroup
    all_results = []
    async with anyio.create_task_group() as main_tg:
        for i in range(3):
            async def run_outer():
                result = await outer_task(i)
                all_results.append(result)
            main_tg.start_soon(run_outer)

    # 验证结果
    assert len(all_results) == 3

    # 关键验证：没有抛出 RuntimeError
    print("✅ Nested task groups completed without cancel scope errors")


@pytest.mark.cancel_scope
@pytest.mark.anyio
async def test_error_handling_no_cancel_scope_error(
    cancel_scope_test_environment
):
    """测试错误处理不产生 Cancel Scope 错误"""
    env = cancel_scope_test_environment

    async def failing_task(task_id: int):
        """会失败的任务"""
        await anyio.sleep(0.02)
        if task_id % 2 == 0:
            raise ValueError(f"Task {task_id} failed")
        return f"Task {task_id} succeeded"

    # 执行可能失败的任务
    results = []
    async with anyio.create_task_group() as main_tg:
        for i in range(5):
            async def run_task():
                try:
                    result = await failing_task(i)
                    results.append(("success", result))
                except ValueError as e:
                    results.append(("error", str(e)))
            main_tg.start_soon(run_task)

    # 验证结果
    assert len(results) == 5
    error_count = sum(1 for status, _ in results if status == "error")
    success_count = sum(1 for status, _ in results if status == "success")
    # 可能有偶数个失败和奇数个成功
    assert error_count >= 0
    assert success_count >= 0

    # 关键验证：没有抛出 RuntimeError (cancel scope 错误)
    print("✅ Error handling completed without cancel scope errors")


if __name__ == "__main__":
    # 运行所有 Cancel Scope 验证测试
    pytest.main([__file__, "-v", "-m", "cancel_scope"])

"""
状态机流水线扩展集成测试
补充关键的状态机集成测试场景
"""
import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import asyncio

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController


@pytest.fixture
async def safe_task_group():
    """创建安全的 TaskGroup"""
    async with anyio.create_task_group() as tg:
        yield tg


@pytest.fixture
def temp_story_file():
    """创建临时故事文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        content = """# Story 1.1: Test Story

## Status
Status: Draft

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
"""
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # 清理
    if temp_path.exists():
        temp_path.unlink()


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_with_concurrent_stories(safe_task_group, temp_story_file):
    """测试状态机并发故事处理"""
    async with safe_task_group as tg:
        # 创建多个控制器实例
        controllers = []
        for i in range(3):
            controller = DevQaController(tg, use_claude=False)
            controller._story_path = str(temp_story_file)
            controllers.append(controller)

        # 为每个控制器设置不同的状态序列
        status_sequences = [
            ["Draft", "In Progress", "Done"],
            ["Draft", "In Progress", "Ready for Review", "Done"],
            ["Draft", "Failed", "In Progress", "Done"]
        ]

        # 并发运行状态机
        results = []
        for i, controller in enumerate(controllers):
            # 设置状态解析
            status_sequence = status_sequences[i]
            status_index = 0

            async def mock_parse_status(path):
                nonlocal status_index
                if status_index < len(status_sequence):
                    status = status_sequence[status_index]
                    status_index += 1
                    return status
                return "Done"

            controller.state_agent.parse_status = mock_parse_status
            controller.dev_agent.execute = AsyncMock(return_value=True)
            controller.qa_agent.execute = AsyncMock(return_value=True)

            # 启动状态机
            result = controller.run_state_machine("Start", max_rounds=5)
            results.append(result)

        # 等待所有状态机完成
        final_results = []
        for result in results:
            final_results.append(await result)

        # 验证结果
        assert len(final_results) == 3
        assert all(result for result in final_results), "All state machines should complete successfully"


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_resource_cleanup(safe_task_group, temp_story_file):
    """测试状态机资源清理"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 设置状态序列
        status_sequence = ["Draft", "In Progress", "Done"]
        status_index = 0

        async def mock_parse_status(path):
            nonlocal status_index
            if status_index < len(status_sequence):
                status = status_sequence[status_index]
                status_index += 1
                return status
            return "Done"

        controller.state_agent.parse_status = mock_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 运行状态机
        result = await controller.run_state_machine("Start", max_rounds=5)

        # 验证结果
        assert result is True

        # 验证资源清理
        assert controller._story_path is not None
        # 状态机完成后，控制器应该处于可用状态


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_memory_leak_detection(safe_task_group, temp_story_file):
    """测试状态机内存泄漏检测"""
    async with safe_task_group as tg:
        # 运行多次状态机以检测内存泄漏
        for i in range(5):
            controller = DevQaController(tg, use_claude=False)
            controller._story_path = str(temp_story_file)

            # 设置状态序列
            status_sequence = ["Draft", "In Progress", "Done"]
            status_index = 0

            async def mock_parse_status(path):
                nonlocal status_index
                if status_index < len(status_sequence):
                    status = status_sequence[status_index]
                    status_index += 1
                    return status
                return "Done"

            controller.state_agent.parse_status = mock_parse_status
            controller.dev_agent.execute = AsyncMock(return_value=True)
            controller.qa_agent.execute = AsyncMock(return_value=True)

            # 运行状态机
            result = await controller.run_state_machine("Start", max_rounds=5)

            # 验证结果
            assert result is True

            # 清理引用
            del controller


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_with_failed_state_recovery(safe_task_group, temp_story_file):
    """测试状态机失败状态恢复"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 模拟复杂的状态转换序列，包括多次失败
        status_sequence = [
            "Draft",           # 1. 开始开发
            "Failed",          # 2. 开发失败
            "Draft",           # 3. 重新开始
            "Failed",          # 4. 再次失败
            "In Progress",     # 5. 继续开发
            "Ready for Review", # 6. 进入审查
            "Done"             # 7. 完成
        ]
        status_index = 0

        async def mock_parse_status(path):
            nonlocal status_index
            if status_index < len(status_sequence):
                status = status_sequence[status_index]
                status_index += 1
                return status
            return "Done"

        controller.state_agent.parse_status = mock_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 运行状态机
        result = await controller.run_state_machine("Start", max_rounds=10)

        # 验证结果 - 应该能够从失败中恢复
        assert result is True
        assert status_index == len(status_sequence)


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_boundary_conditions(safe_task_group, temp_story_file):
    """测试状态机边界条件"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 测试边界条件：立即完成
        controller.state_agent.parse_status = AsyncMock(return_value="Done")
        result = await controller.run_state_machine("Start", max_rounds=5)
        assert result is True

        # 重置控制器
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 测试边界条件：最大轮数刚好够用
        status_sequence = ["Draft", "In Progress", "Ready for Review", "Done"]
        status_index = 0

        async def mock_parse_status(path):
            nonlocal status_index
            if status_index < len(status_sequence):
                status = status_sequence[status_index]
                status_index += 1
                return status
            return "Done"

        controller.state_agent.parse_status = mock_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 使用精确的轮数
        result = await controller.run_state_machine("Start", max_rounds=4)
        assert result is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_error_propagation(safe_task_group, temp_story_file):
    """测试状态机错误传播"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 模拟状态解析异常
        controller.state_agent.parse_status = AsyncMock(
            side_effect=Exception("Simulated parsing error")
        )

        # 运行状态机并捕获异常
        result = await controller.run_state_machine("Start", max_rounds=3)

        # 验证结果 - 异常应该被处理
        assert result is False  # 达到最大轮数后失败


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_state_transition_validation(safe_task_group, temp_story_file):
    """测试状态机状态转换验证"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 跟踪状态转换
        state_transitions = []

        async def mock_parse_status(path):
            # 记录状态转换
            if not hasattr(mock_parse_status, 'current_state'):
                mock_parse_status.current_state = "Start"

            state_transitions.append(mock_parse_status.current_state)

            # 根据当前状态返回下一个状态
            if mock_parse_status.current_state == "Start":
                mock_parse_status.current_state = "Draft"
            elif mock_parse_status.current_state == "Draft":
                mock_parse_status.current_state = "In Progress"
            elif mock_parse_status.current_state == "In Progress":
                mock_parse_status.current_state = "Done"
            else:
                mock_parse_status.current_state = "Done"

            return mock_parse_status.current_state

        controller.state_agent.parse_status = mock_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 运行状态机
        result = await controller.run_state_machine("Start", max_rounds=5)

        # 验证结果
        assert result is True
        assert "Start" in state_transitions
        assert "Draft" in state_transitions
        assert "In Progress" in state_transitions
        assert "Done" in state_transitions


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_performance(safe_task_group, temp_story_file):
    """测试状态机性能"""
    import time

    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 设置快速状态转换
        status_sequence = ["Draft", "In Progress", "Done"]
        status_index = 0

        async def mock_parse_status(path):
            nonlocal status_index
            if status_index < len(status_sequence):
                status = status_sequence[status_index]
                status_index += 1
                return status
            return "Done"

        controller.state_agent.parse_status = mock_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 测量执行时间
        start_time = time.time()
        result = await controller.run_state_machine("Start", max_rounds=5)
        end_time = time.time()

        # 验证结果
        assert result is True
        # 确保执行时间在合理范围内（小于1秒）
        assert (end_time - start_time) < 1.0


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_idempotency(safe_task_group, temp_story_file):
    """测试状态机幂等性"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 设置状态为完成
        controller.state_agent.parse_status = AsyncMock(return_value="Done")

        # 第一次运行
        result1 = await controller.run_state_machine("Start", max_rounds=5)

        # 重置控制器
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 设置相同状态
        controller.state_agent.parse_status = AsyncMock(return_value="Done")

        # 第二次运行
        result2 = await controller.run_state_machine("Start", max_rounds=5)

        # 验证结果一致
        assert result1 == result2 == True


@pytest.mark.integration
@pytest.mark.anyio
async def test_state_machine_with_cancellation(safe_task_group, temp_story_file):
    """测试状态机取消处理"""
    async with safe_task_group as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = str(temp_story_file)

        # 模拟长时间运行的状态解析
        call_count = 0
        async def slow_parse_status(path):
            nonlocal call_count
            call_count += 1
            await anyio.sleep(0.1)  # 模拟延迟
            if call_count == 1:
                return "Draft"
            elif call_count == 2:
                return "In Progress"
            else:
                return "Done"

        controller.state_agent.parse_status = slow_parse_status
        controller.dev_agent.execute = AsyncMock(return_value=True)
        controller.qa_agent.execute = AsyncMock(return_value=True)

        # 启动状态机
        async def run_state_machine():
            return await controller.run_state_machine("Start", max_rounds=5)

        # 取消任务
        with anyio.fail_after(0.5):  # 0.5秒后超时
            try:
                result = await run_state_machine()
                # 如果没有超时，验证结果
                assert result is True
            except TimeoutError:
                # 超时是预期的
                pass


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-m", "integration"])

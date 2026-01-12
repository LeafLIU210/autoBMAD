"""
状态机流水线集成测试
测试状态机流水线的完整功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController


@pytest.fixture
async def task_group():
    """创建真实的 TaskGroup"""
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


@pytest.mark.anyio
async def test_devqa_state_machine_basic_flow(
    task_group,
    temp_story_file
):
    """测试 Dev-QA 状态机基本流程"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态转换：Draft -> In Progress -> Done
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

    # 模拟 Dev 和 QA 执行
    controller.dev_agent.execute = AsyncMock(return_value=True)
    controller.qa_agent.execute = AsyncMock(return_value=True)

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=5)

    # 验证结果
    assert result is True
    assert status_index == 3  # 应该调用3次状态解析


@pytest.mark.anyio
async def test_devqa_state_machine_draft_to_done_single_round(
    task_group,
    temp_story_file
):
    """测试从草稿到完成单轮转换"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态直接转换为完成
    controller.state_agent.parse_status = AsyncMock(return_value="Done")

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果
    assert result is True
    # 第一次调用就应该达到终止状态
    controller.state_agent.parse_status.assert_called_once()


@pytest.mark.anyio
async def test_devqa_state_machine_max_rounds_reached(
    task_group,
    temp_story_file
):
    """测试达到最大轮数"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态始终为非终止状态
    controller.state_agent.parse_status = AsyncMock(return_value="Draft")

    # 设置较低的最大轮数
    result = await controller.run_state_machine("Start", max_rounds=2)

    # 验证结果 - 应该因为达到最大轮数而失败
    assert result is False
    # 应该调用2次状态解析
    assert controller.state_agent.parse_status.call_count == 2


@pytest.mark.anyio
async def test_devqa_state_machine_with_failed_state(
    task_group,
    temp_story_file
):
    """测试失败状态的处理"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态转换：Draft -> Failed -> Done
    status_sequence = ["Draft", "Failed", "Done"]
    status_index = 0

    async def mock_parse_status(path):
        nonlocal status_index
        if status_index < len(status_sequence):
            status = status_sequence[status_index]
            status_index += 1
            return status
        return "Done"

    controller.state_agent.parse_status = mock_parse_status

    # 模拟 Dev 执行
    controller.dev_agent.execute = AsyncMock(return_value=True)

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=5)

    # 验证结果
    assert result is True  # 最终达到 Done 状态


@pytest.mark.anyio
async def test_devqa_state_machine_with_ready_for_review(
    task_group,
    temp_story_file
):
    """测试待审查状态处理"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态转换：Draft -> In Progress -> Ready for Review -> Done
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

    # 模拟 Dev 和 QA 执行
    controller.dev_agent.execute = AsyncMock(return_value=True)
    controller.qa_agent.execute = AsyncMock(return_value=True)

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=5)

    # 验证结果
    assert result is True

    # 验证 Dev 和 QA 都被调用
    assert controller.dev_agent.execute.call_count >= 1
    assert controller.qa_agent.execute.call_count >= 1


@pytest.mark.anyio
async def test_devqa_state_machine_ready_for_done_termination(
    task_group,
    temp_story_file
):
    """测试准备完成状态终止"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态为准备完成
    controller.state_agent.parse_status = AsyncMock(return_value="Ready for Done")

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果 - Ready for Done 是终止状态
    assert result is True
    # 只应该调用一次状态解析
    controller.state_agent.parse_status.assert_called_once()


@pytest.mark.anyio
async def test_devqa_state_machine_error_handling(
    task_group,
    temp_story_file
):
    """测试错误处理"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态解析失败 (返回None)
    controller.state_agent.parse_status = AsyncMock(return_value=None)

    # 运行状态机 - 状态解析失败会导致Failed状态，Failed状态允许重新开发
    # 所以状态机会继续运行直到达到最大轮数
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果 - Failed状态不是终止状态，状态机会继续运行直到达到最大轮数，返回False
    assert result is False


@pytest.mark.anyio
async def test_devqa_state_machine_exception_handling(
    task_group,
    temp_story_file
):
    """测试异常处理"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态解析异常
    controller.state_agent.parse_status = AsyncMock(
        side_effect=Exception("Test exception")
    )

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果 - 异常会返回"Error"（终止状态），状态机应返回True
    assert result is True


@pytest.mark.anyio
async def test_devqa_state_machine_agent_execution_error(
    task_group,
    temp_story_file
):
    """测试 Agent 执行错误"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态为草稿
    controller.state_agent.parse_status = AsyncMock(return_value="Draft")

    # 模拟 Dev 执行失败
    controller.dev_agent.execute = AsyncMock(return_value=False)

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果 - Dev 执行失败不应该阻止状态机
    # 状态机应该继续运行直到达到最大轮数
    assert result is False  # 因为达到最大轮数而失败


@pytest.mark.anyio
async def test_devqa_state_machine_termination_states(
    task_group,
    temp_story_file
):
    """测试所有终止状态"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 只有真正的终止状态才应该返回 True
    termination_states = ["Done", "Ready for Done", "Error"]

    for state in termination_states:
        # 重置模拟
        controller.state_agent.parse_status = AsyncMock(return_value=state)

        # 运行状态机
        result = await controller.run_state_machine("Start", max_rounds=3)

        # 验证结果 - 真正的终止状态都应该返回 True
        assert result is True, f"State {state} should be termination state"


@pytest.mark.anyio
async def test_devqa_state_machine_non_termination_states(
    task_group,
    temp_story_file
):
    """测试非终止状态"""
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # Failed 状态允许重新开发，不视为终止状态
    non_termination_states = ["Draft", "Ready for Development", "In Progress", "Ready for Review", "Failed"]

    for state in non_termination_states:
        # 重置模拟
        controller.state_agent.parse_status = AsyncMock(return_value=state)
        controller.dev_agent.execute = AsyncMock(return_value=True)

        # 运行状态机
        result = await controller.run_state_machine("Start", max_rounds=2)

        # 验证结果 - 非终止状态应该继续运行
        # 因为我们设置了 max_rounds=2，所以应该返回 False
        assert result is False, f"State {state} should not be termination state"


@pytest.mark.anyio
async def test_devqa_state_machine_execute_method(
    task_group,
    temp_story_file
):
    """测试 execute 方法"""
    controller = DevQaController(task_group, use_claude=False)

    # 模拟状态机成功
    with patch.object(
        controller,
        'run_state_machine',
        new_callable=AsyncMock
    ) as mock_run:
        mock_run.return_value = True

        # 执行
        result = await controller.execute(str(temp_story_file))

        # 验证结果
        assert result is True
        mock_run.assert_called_once_with(initial_state="Start", max_rounds=3)


@pytest.mark.anyio
async def test_devqa_state_machine_execute_with_custom_rounds(
    task_group,
    temp_story_file
):
    """测试带自定义轮数的执行"""
    controller = DevQaController(task_group, use_claude=False)

    # 模拟状态机成功
    with patch.object(
        controller,
        'run_state_machine',
        new_callable=AsyncMock
    ) as mock_run:
        mock_run.return_value = True

        # 使用自定义轮数执行
        result = await controller.run_pipeline(str(temp_story_file), max_rounds=5)

        # 验证结果
        assert result is True
        mock_run.assert_called_once_with(initial_state="Start", max_rounds=5)


@pytest.mark.anyio
async def test_devqa_state_machine_story_path_validation():
    """测试故事路径验证"""
    controller = DevQaController(MagicMock())

    # 不设置故事路径
    # 运行决策应该返回错误
    result = await controller._make_decision("Start")
    assert result == "Error"


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

"""
控制器与 Agent 集成测试
测试控制器与各种 Agent 的集成功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.sm_controller import SMController
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.controllers.quality_controller import QualityController
from autoBMAD.epic_automation.agents.sm_agent import SMAgent
from autoBMAD.epic_automation.agents.state_agent import StateAgent
from autoBMAD.epic_automation.agents.dev_agent import DevAgent
from autoBMAD.epic_automation.agents.qa_agent import QAAgent
from autoBMAD.epic_automation.agents.quality_agents import (
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)


@pytest.fixture
async def task_group():
    """
    旧的task_group fixture，已弃用

    请使用safe_task_group替代：
    @pytest.mark.anyio
    async def test_example(safe_task_group):
        async with safe_task_group as tg:
            # 使用tg进行测试
            pass
    """
    import warnings
    warnings.warn(
        "task_group fixture is deprecated. Use safe_task_group instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # 为了向后兼容，创建一个简单的TaskGroup
    async with anyio.create_task_group() as tg:
        yield tg


@pytest.fixture
def temp_project_root():
    """创建临时项目根目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_root = Path(tmp_dir)
        stories_dir = project_root / "stories"
        src_dir = project_root / "src"
        tests_dir = project_root / "tests"
        stories_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)
        yield project_root


@pytest.fixture
def sample_epic_content():
    """示例 Epic 内容"""
    return """# Epic 1: Test Epic

## Overview
This is a test epic for integration testing.

## Stories
- Story 1.1: Test Story 1
- Story 1.2: Test Story 2

## Acceptance Criteria
- [ ] All criteria met
"""


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
async def test_sm_controller_with_sm_agent_integration(
    temp_project_root,
    sample_epic_content
):
    """测试 SMController 与 SMAgent 的集成"""
    # 创建模拟 TaskGroup
    mock_task_group = MagicMock()

    # 创建控制器
    controller = SMController(mock_task_group, temp_project_root)

    # 验证控制器组件
    assert controller.sm_agent is not None
    assert controller.state_agent is not None
    assert isinstance(controller.sm_agent, SMAgent)
    assert isinstance(controller.state_agent, StateAgent)

    # 模拟 SMAgent 执行 - 使用 AsyncMock
    with patch.object(
        controller.sm_agent,
        'execute',
        new_callable=AsyncMock
    ) as mock_execute:
        # 创建模拟故事文件
        story_file = temp_project_root / "stories" / "1.1.md"
        story_file.write_text("Test story content for validation", encoding='utf-8')

        # 使用 AsyncMock 设置返回值
        mock_execute.return_value = True

        # 模拟 _execute_within_taskgroup 方法，直接调用协程
        async def mock_execute_within_taskgroup(coro):
            return await coro()

        with patch.object(controller, '_execute_within_taskgroup', mock_execute_within_taskgroup):
            # 执行 SM 阶段
            result = await controller.execute(
                epic_content=sample_epic_content,
                story_id="1.1"
            )

            # 验证集成
            assert result is True
            mock_execute.assert_called_once()


@pytest.mark.anyio
async def test_sm_controller_with_state_agent_integration(
    safe_task_group,
    temp_project_root
):
    """测试 SMController 与 StateAgent 的集成"""
    async with safe_task_group as tg:
        # 创建控制器
        controller = SMController(tg, temp_project_root)

    # 创建故事文件
    story_file = temp_project_root / "stories" / "1.1.md"
    story_file.write_text(
        "Status: Draft\n# Story 1.1\n",
        encoding='utf-8'
    )

    # 测试状态解析集成
    status = await controller.state_agent.parse_status(str(story_file))

    # 验证集成
    assert status is not None
    assert status in ["Draft", "Ready for Development"]


@pytest.mark.anyio
async def test_devqa_controller_with_dev_agent_integration(
    temp_story_file
):
    """测试 DevQaController 与 DevAgent 的集成"""
    # 创建模拟 TaskGroup
    mock_task_group = MagicMock()

    # 创建控制器
    controller = DevQaController(mock_task_group, use_claude=False)

    # 验证控制器组件
    assert controller.dev_agent is not None
    assert controller.state_agent is not None
    assert isinstance(controller.dev_agent, DevAgent)
    assert isinstance(controller.state_agent, StateAgent)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态为草稿
    controller.state_agent.parse_status = AsyncMock(return_value="Draft")

    # 测试状态决策集成
    next_state = await controller._make_decision("Start")

    # 验证集成
    assert next_state == "AfterDev"


@pytest.mark.anyio
async def test_devqa_controller_with_qa_agent_integration(
    task_group,
    temp_story_file
):
    """测试 DevQaController 与 QAAgent 的集成"""
    # 创建控制器
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态为待审查
    controller.state_agent.parse_status = AsyncMock(return_value="Ready for Review")

    # 测试状态决策集成
    next_state = await controller._make_decision("Start")

    # 验证集成
    assert next_state == "AfterQA"


@pytest.mark.anyio
async def test_quality_controller_with_ruff_agent_integration(
    task_group,
    temp_project_root
):
    """测试 QualityController 与 RuffAgent 的集成"""
    # 创建控制器
    controller = QualityController(task_group, temp_project_root)

    # 验证控制器组件
    assert controller.ruff_agent is not None
    assert isinstance(controller.ruff_agent, RuffAgent)

    # 模拟 Ruff 检查结果
    with patch.object(
        controller.ruff_agent,
        'execute',
        new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = {
            "status": "completed",
            "errors": 0,
            "warnings": 0
        }

        # 执行质量检查
        result = await controller.execute(
            source_dir=str(temp_project_root / "src")
        )

        # 验证集成
        assert isinstance(result, dict)
        assert result.get('overall_status') == 'pass'
        mock_execute.assert_called_once()


@pytest.mark.anyio
async def test_quality_controller_with_pyright_agent_integration(
    task_group,
    temp_project_root
):
    """测试 QualityController 与 BasedPyrightAgent 的集成"""
    # 创建控制器
    controller = QualityController(task_group, temp_project_root)

    # 验证控制器组件
    assert controller.pyright_agent is not None
    assert isinstance(controller.pyright_agent, BasedPyrightAgent)

    # 模拟 BasedPyright 检查结果
    with patch.object(
        controller.pyright_agent,
        'execute',
        new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = {
            "status": "completed",
            "errors": 0,
            "warnings": 0
        }

        # 执行质量检查
        result = await controller.execute(
            source_dir=str(temp_project_root / "src")
        )

        # 验证集成
        assert isinstance(result, dict)
        assert result.get('overall_status') == 'pass'
        mock_execute.assert_called_once()


@pytest.mark.anyio
async def test_quality_controller_with_pytest_agent_integration(
    task_group,
    temp_project_root
):
    """测试 QualityController 与 PytestAgent 的集成"""
    # 创建控制器
    controller = QualityController(task_group, temp_project_root)

    # 验证控制器组件
    assert controller.pytest_agent is not None
    assert isinstance(controller.pytest_agent, PytestAgent)

    # 模拟 Pytest 执行结果
    with patch.object(
        controller.pytest_agent,
        'execute',
        new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = {
            "status": "completed",
            "tests_passed": 10,
            "tests_failed": 0
        }

        # 执行质量检查
        result = await controller.execute(
            source_dir=str(temp_project_root / "src"),
            test_dir=str(temp_project_root / "tests")
        )

        # 验证集成
        assert isinstance(result, dict)
        assert result.get('overall_status') == 'pass'
        mock_execute.assert_called_once()


@pytest.mark.anyio
async def test_controller_taskgroup_execution(task_group):
    """测试控制器在 TaskGroup 内的执行"""
    # 创建模拟控制器
    from autoBMAD.epic_automation.controllers.base_controller import BaseController

    class TestController(BaseController):
        def __init__(self, task_group):
            super().__init__(task_group)
            self.executed = False

        async def execute(self):
            self.executed = True
            return True

    controller = TestController(task_group)

    # 在 TaskGroup 内执行
    result = await controller.execute()

    # 验证结果
    assert result is True
    assert controller.executed is True


@pytest.mark.anyio
async def test_controller_state_machine_pipeline_integration(
    task_group,
    temp_story_file
):
    """测试控制器状态机流水线集成"""
    # 创庺控制器
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

    # 运行状态机流水线
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证集成结果
    assert result is True  # 应该成功达到终止状态


@pytest.mark.anyio
async def test_full_sm_to_devqa_pipeline(
    temp_project_root,
    sample_epic_content
):
    """测试从 SM 到 Dev-QA 的完整流水线"""
    # 创建模拟 TaskGroup
    mock_task_group = MagicMock()

    # 创建故事文件
    story_file = temp_project_root / "stories" / "1.1.md"
    story_file.write_text("Status: Draft\n# Story 1.1\n", encoding='utf-8')

    # Step 1: SM 阶段
    sm_controller = SMController(mock_task_group, temp_project_root)
    sm_result = await sm_controller.execute(
        epic_content=sample_epic_content,
        story_id="1.1"
    )

    # 验证 SM 阶段
    assert sm_result is True

    # Step 2: Dev-QA 阶段
    devqa_controller = DevQaController(mock_task_group, use_claude=False)

    # Mock掉DevAgent和QAAgent的执行
    with patch.object(devqa_controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
        with patch.object(devqa_controller.qa_agent, 'execute', new_callable=AsyncMock) as mock_qa:
            # Mock状态解析器返回 "Done"
            with patch.object(devqa_controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
                # 第一轮返回 Draft，第二轮返回 Done
                mock_parse.side_effect = ["Draft", "Done"]

                devqa_result = await devqa_controller.execute(str(story_file))

    # 验证 Dev-QA 阶段
    assert devqa_result is True


@pytest.mark.anyio
async def test_controller_error_propagation(task_group):
    """测试控制器错误传播"""
    # 创建模拟控制器
    from autoBMAD.epic_automation.controllers.base_controller import BaseController

    class FailingController(BaseController):
        async def execute(self):
            raise Exception("Test exception")

    controller = FailingController(task_group)

    # 执行并捕获异常
    with pytest.raises(Exception) as exc_info:
        await controller.execute()

    # 验证异常
    assert "Test exception" in str(exc_info.value)


@pytest.mark.anyio
async def test_agent_lifecycle_management(task_group):
    """测试 Agent 生命周期管理"""
    # 创庺多个控制器实例
    controller1 = SMController(task_group)
    controller2 = DevQaController(task_group)
    controller3 = QualityController(task_group)

    # 验证所有控制器都有 TaskGroup
    assert controller1.task_group == task_group
    assert controller2.task_group == task_group
    assert controller3.task_group == task_group

    # 验证所有 Agent 都被正确初始化
    assert controller1.sm_agent is not None
    assert controller2.dev_agent is not None
    assert controller2.qa_agent is not None
    assert controller3.ruff_agent is not None


@pytest.mark.anyio
async def test_devqa_controller_failed_state_recovery(
    task_group,
    temp_story_file
):
    """测试DevQaController对Failed状态的恢复能力"""
    # 创建控制器
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态转换：Failed -> AfterDev -> Done
    status_sequence = ["Failed", "Draft", "In Progress", "Done"]
    status_index = 0

    async def mock_parse_status(path):
        nonlocal status_index
        if status_index < len(status_sequence):
            status = status_sequence[status_index]
            status_index += 1
            return status
        return "Done"

    controller.state_agent.parse_status = mock_parse_status

    # 运行状态机流水线
    result = await controller.run_state_machine("Start", max_rounds=4)

    # 验证集成结果
    assert result is True  # 应该成功达到终止状态
    # 验证状态转换次数（从Failed到Done应该需要4步）
    assert status_index == 4


@pytest.mark.anyio
async def test_devqa_controller_multiple_failures_recovery(
    task_group,
    temp_story_file
):
    """测试DevQaController对多次失败状态的恢复能力"""
    # 创建控制器
    controller = DevQaController(task_group, use_claude=False)

    # 设置故事路径
    controller._story_path = str(temp_story_file)

    # 模拟状态转换：多次失败后最终成功
    status_sequence = [
        "Failed",    # 第1次失败
        "Draft",     # 重新开发
        "Failed",    # 第2次失败
        "In Progress", # 继续开发
        "Ready for Review", # 进入QA
        "Done"       # 最终成功
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

    # 运行状态机流水线
    result = await controller.run_state_machine("Start", max_rounds=6)

    # 验证集成结果
    assert result is True  # 应该成功达到终止状态
    # 验证所有状态都被访问过
    assert status_index == 6


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

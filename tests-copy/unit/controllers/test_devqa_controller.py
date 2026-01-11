"""
DevQa Controller 单元测试
"""
import pytest
import anyio
from unittest.mock import Mock, AsyncMock, patch
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController


class MockAgent:
    """模拟 Agent"""
    def __init__(self, name: str):
        self.name = name
        self.executed = False

    async def execute(self, story_path: str):
        self.executed = True
        return True


@pytest.mark.anyio
async def test_devqa_controller_init():
    """测试 DevQaController 初始化"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)

        assert controller.task_group is not None
        assert controller.state_agent is not None
        assert controller.dev_agent is not None
        assert controller.qa_agent is not None
        assert controller.max_rounds == 3
        assert controller._story_path is None


@pytest.mark.anyio
async def test_execute():
    """测试执行流水线"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)

        with patch.object(controller, 'run_state_machine', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = True

            result = await controller.execute("test_story.md")

            assert result is True
            mock_run.assert_called_once()
            assert controller._story_path == "test_story.md"


@pytest.mark.anyio
async def test_run_pipeline():
    """测试 run_pipeline 方法"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)

        with patch.object(controller, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = True

            result = await controller.run_pipeline("test_story.md", max_rounds=5)

            assert result is True
            mock_execute.assert_called_once()


@pytest.mark.anyio
async def test_make_decision_draft():
    """测试 Draft 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Draft"

            with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                next_state = await controller._make_decision("Start")

                assert next_state == "AfterDev"
                mock_parse.assert_called_once_with("test_story.md")
                mock_dev.assert_called_once_with("test_story.md")


@pytest.mark.anyio
async def test_make_decision_ready_for_development():
    """测试 Ready for Development 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Ready for Development"

            with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                next_state = await controller._make_decision("Start")

                assert next_state == "AfterDev"
                mock_dev.assert_called_once()


@pytest.mark.anyio
async def test_make_decision_in_progress():
    """测试 In Progress 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "In Progress"

            with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                next_state = await controller._make_decision("Start")

                assert next_state == "AfterDev"
                mock_dev.assert_called_once()


@pytest.mark.anyio
async def test_make_decision_ready_for_review():
    """测试 Ready for Review 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Ready for Review"

            with patch.object(controller.qa_agent, 'execute', new_callable=AsyncMock) as mock_qa:
                next_state = await controller._make_decision("Start")

                assert next_state == "AfterQA"
                mock_qa.assert_called_once_with("test_story.md")


@pytest.mark.anyio
async def test_make_decision_done():
    """测试 Done 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Done"

            next_state = await controller._make_decision("Start")

            assert next_state == "Done"
            # Dev Agent 不应该被调用
            assert not hasattr(controller.dev_agent, 'executed') or not controller.dev_agent.executed


@pytest.mark.anyio
async def test_make_decision_ready_for_done():
    """测试 Ready for Done 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Ready for Done"

            next_state = await controller._make_decision("Start")

            assert next_state == "Ready for Done"


@pytest.mark.anyio
async def test_make_decision_failed():
    """测试 Failed 状态的决策"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Failed"

            with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                next_state = await controller._make_decision("Start")

                assert next_state == "AfterDev"
                mock_dev.assert_called_once()


@pytest.mark.anyio
async def test_make_decision_parse_error():
    """测试状态解析错误"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = None

            next_state = await controller._make_decision("Start")

            assert next_state == "Failed"


@pytest.mark.anyio
async def test_make_decision_no_story_path():
    """测试故事路径未设置"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)

        next_state = await controller._make_decision("Start")

        assert next_state == "Error"


@pytest.mark.anyio
async def test_make_decision_exception():
    """测试决策过程异常"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)
        controller._story_path = "test_story.md"

        with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.side_effect = Exception("Test error")

            next_state = await controller._make_decision("Start")

            assert next_state == "Error"


@pytest.mark.anyio
async def test_is_termination_state():
    """测试终止状态判断"""
    async with anyio.create_task_group() as tg:
        controller = DevQaController(tg, use_claude=False)

        assert controller._is_termination_state("Done") is True
        assert controller._is_termination_state("Ready for Done") is True
        assert controller._is_termination_state("Failed") is True
        assert controller._is_termination_state("Error") is True
        assert controller._is_termination_state("In Progress") is False
        assert controller._is_termination_state("Draft") is False

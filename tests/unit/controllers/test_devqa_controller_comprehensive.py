"""
DevQaController Comprehensive Test Suite

Tests for DevQAController including:
- Initialization
- Pipeline execution
- State machine decisions
- Status updates
- Error handling
"""
import pytest
import anyio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.state_manager import StateManager


class TestDevQaController:
    """Test suite for DevQAController"""

    @pytest.mark.anyio
    async def test_init_default(self):
        """测试默认初始化"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)

            assert controller.task_group is tg
            assert controller.state_agent is not None
            assert controller.dev_agent is not None
            assert controller.qa_agent is not None
            assert controller.state_manager is not None
            assert controller.max_rounds == 3
            assert controller._story_path is None

    @pytest.mark.anyio
    async def test_init_with_options(self):
        """测试带选项的初始化"""
        async with anyio.create_task_group() as tg:
            log_manager = Mock()
            state_manager = Mock(spec=StateManager)

            controller = DevQaController(
                task_group=tg,
                use_claude=False,
                log_manager=log_manager,
                state_manager=state_manager
            )

            assert controller.state_manager == state_manager

    @pytest.mark.anyio
    async def test_execute_basic_flow(self):
        """测试基本执行流程"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)

            # Mock StateAgent to return "Ready for Review"
            controller.state_agent.execute = AsyncMock(return_value="Ready for Review")
            controller.qa_agent.execute = AsyncMock(return_value=True)

            result = await controller.execute("test_story.md")

            assert result is True
            assert controller._story_path == "test_story.md"

    @pytest.mark.anyio
    async def test_execute_with_dev_failure(self):
        """测试开发失败的情况"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            # Mock to return "Draft" which triggers dev
            controller.state_agent.execute = AsyncMock(return_value="Draft")
            controller.dev_agent.execute = AsyncMock(return_value=False)

            result = await controller.execute("test_story.md")

            # Should return True because the pipeline completes even with dev failure
            assert result is True

    @pytest.mark.anyio
    async def test_execute_exception_handling(self):
        """测试异常处理"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)

            # Mock StateAgent to raise exception
            controller.state_agent.execute = AsyncMock(side_effect=Exception("Test error"))

            result = await controller.execute("test_story.md")

            # Exception is caught and returns False
            assert result is False

    @pytest.mark.anyio
    async def test_run_pipeline(self):
        """测试run_pipeline方法"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)

            # Mock execution
            with patch.object(controller, 'execute', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = True

                result = await controller.run_pipeline("test_story.md", max_rounds=5)

                assert result is True
                # max_rounds is temporarily set during execution
                assert controller.max_rounds == 3

    @pytest.mark.anyio
    async def test_make_decision_done_state(self):
        """测试Done状态决策"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(return_value="Done")

            result = await controller._make_decision("Start")

            assert result == "Done"

    @pytest.mark.anyio
    async def test_make_decision_ready_for_done(self):
        """测试Ready for Done状态决策"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(return_value="Ready for Done")

            result = await controller._make_decision("Start")

            assert result == "Ready for Done"

    @pytest.mark.anyio
    async def test_make_decision_failed_triggers_dev(self):
        """测试Failed状态触发开发"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            # First call returns "Failed", second call returns "Done"
            controller.state_agent.execute = AsyncMock(side_effect=["Failed", "Done"])
            controller.dev_agent.execute = AsyncMock(return_value=True)

            result = await controller._make_decision("Start")

            # Should recursively call and return "Done"
            assert result == "Done"
            assert controller.dev_agent.execute.called

    @pytest.mark.anyio
    async def test_make_decision_draft_triggers_dev(self):
        """测试Draft状态触发开发"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            # First call returns "Draft", second call returns "Done"
            controller.state_agent.execute = AsyncMock(side_effect=["Draft", "Done"])
            controller.dev_agent.execute = AsyncMock(return_value=True)

            result = await controller._make_decision("Start")

            assert result == "Done"
            assert controller.dev_agent.execute.called

    @pytest.mark.anyio
    async def test_make_decision_ready_for_development(self):
        """测试Ready for Development状态"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(side_effect=["Ready for Development", "Done"])
            controller.dev_agent.execute = AsyncMock(return_value=True)

            result = await controller._make_decision("Start")

            assert result == "Done"

    @pytest.mark.anyio
    async def test_make_decision_in_progress(self):
        """测试In Progress状态"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(side_effect=["In Progress", "Done"])
            controller.dev_agent.execute = AsyncMock(return_value=True)

            result = await controller._make_decision("Start")

            assert result == "Done"

    @pytest.mark.anyio
    async def test_make_decision_ready_for_review_triggers_qa(self):
        """测试Ready for Review状态触发QA"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            # First call returns "Ready for Review", second call returns "Done"
            controller.state_agent.execute = AsyncMock(side_effect=["Ready for Review", "Done"])
            controller.qa_agent.execute = AsyncMock(return_value=True)

            result = await controller._make_decision("Start")

            assert result == "Done"
            assert controller.qa_agent.execute.called

    @pytest.mark.anyio
    async def test_make_decision_unknown_status(self):
        """测试未知状态"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(return_value="UnknownStatus")

            result = await controller._make_decision("Start")

            # Should return the unknown status
            assert result == "UnknownStatus"

    @pytest.mark.anyio
    async def test_make_decision_no_story_path(self):
        """测试未设置story_path的情况"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            # Don't set _story_path

            result = await controller._make_decision("Start")

            assert result == "Error"

    @pytest.mark.anyio
    async def test_make_decision_state_agent_failure(self):
        """测试StateAgent失败的情况"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(return_value=None)

            result = await controller._make_decision("Start")

            assert result == "Error"

    @pytest.mark.anyio
    async def test_make_decision_exception(self):
        """测试决策过程中的异常"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            controller.state_agent.execute = AsyncMock(side_effect=Exception("Test error"))

            result = await controller._make_decision("Start")

            assert result == "Error"

    @pytest.mark.anyio
    async def test_is_termination_state(self):
        """测试终止状态判断"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)

            assert controller._is_termination_state("Done") is True
            assert controller._is_termination_state("Ready for Done") is True
            assert controller._is_termination_state("Error") is True

            # Failed is NOT a termination state (allows retry)
            assert controller._is_termination_state("Failed") is False
            assert controller._is_termination_state("In Progress") is False
            assert controller._is_termination_state("Draft") is False

    @pytest.mark.anyio
    async def test_update_processing_status_success(self):
        """测试状态更新成功"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            result = await controller._update_processing_status(
                story_id="test_story",
                processing_status="in_progress",
                context="Testing"
            )

            assert result is True
            state_manager.update_story_processing_status.assert_called_once()

    @pytest.mark.anyio
    async def test_update_processing_status_failure(self):
        """测试状态更新失败"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=False)

            controller = DevQaController(tg, state_manager=state_manager)

            result = await controller._update_processing_status(
                story_id="test_story",
                processing_status="in_progress",
                context="Testing"
            )

            assert result is False

    @pytest.mark.anyio
    async def test_update_processing_status_exception(self):
        """测试状态更新异常"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(
                side_effect=Exception("Database error")
            )

            controller = DevQaController(tg, state_manager=state_manager)

            result = await controller._update_processing_status(
                story_id="test_story",
                processing_status="in_progress",
                context="Testing"
            )

            assert result is False

    @pytest.mark.anyio
    async def test_update_processing_status_after_dev_success(self):
        """测试Dev完成后的状态更新 - 成功"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            await controller._update_processing_status_after_dev("test_story", True)

            # Should call update with 'review' status
            state_manager.update_story_processing_status.assert_called_once()
            call_args = state_manager.update_story_processing_status.call_args
            assert call_args[1]['processing_status'] == 'review'

    @pytest.mark.anyio
    async def test_update_processing_status_after_dev_failure(self):
        """测试Dev完成后的状态更新 - 失败"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            await controller._update_processing_status_after_dev("test_story", False)

            # Should call update with 'in_progress' status
            state_manager.update_story_processing_status.assert_called_once()
            call_args = state_manager.update_story_processing_status.call_args
            assert call_args[1]['processing_status'] == 'in_progress'

    @pytest.mark.anyio
    async def test_update_processing_status_after_qa_success(self):
        """测试QA完成后的状态更新 - 成功"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            await controller._update_processing_status_after_qa("test_story", True)

            # Should call update with 'completed' status
            state_manager.update_story_processing_status.assert_called_once()
            call_args = state_manager.update_story_processing_status.call_args
            assert call_args[1]['processing_status'] == 'completed'

    @pytest.mark.anyio
    async def test_update_processing_status_after_qa_failure(self):
        """测试QA完成后的状态更新 - 失败"""
        async with anyio.create_task_group() as tg:
            state_manager = Mock(spec=StateManager)
            state_manager.update_story_processing_status = AsyncMock(return_value=True)

            controller = DevQaController(tg, state_manager=state_manager)

            await controller._update_processing_status_after_qa("test_story", False)

            # Should call update with 'in_progress' status
            state_manager.update_story_processing_status.assert_called_once()
            call_args = state_manager.update_story_processing_status.call_args
            assert call_args[1]['processing_status'] == 'in_progress'

    @pytest.mark.anyio
    async def test_state_machine_max_iterations(self):
        """测试状态机达到最大迭代次数"""
        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg)
            controller._story_path = "test_story.md"

            # Mock to always return "In Progress" which triggers dev
            controller.state_agent.execute = AsyncMock(return_value="In Progress")
            controller.dev_agent.execute = AsyncMock(return_value=True)

            result = await controller.run_state_machine("Start", max_rounds=3)

            # Should return False when max iterations reached
            assert result is False

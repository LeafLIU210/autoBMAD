"""
Base Controller 单元测试
"""
import pytest
import anyio
from unittest.mock import Mock, AsyncMock
from autoBMAD.epic_automation.controllers.base_controller import BaseController, StateDrivenController


class TestController(BaseController):
    """测试用控制器"""
    def __init__(self, task_group):
        super().__init__(task_group)
        self.executed = False

    async def execute(self, *args, **kwargs):
        self.executed = True
        return True


class TestStateDrivenController(StateDrivenController):
    """测试用状态驱动控制器"""
    def __init__(self, task_group):
        super().__init__(task_group)
        self.decision_count = 0

    async def execute(self, *args, **kwargs):
        """实现抽象方法"""
        return True

    async def _make_decision(self, current_state: str) -> str:
        self.decision_count += 1
        if self.decision_count < 3:
            return f"State_{self.decision_count}"
        return "Done"


@pytest.mark.anyio
async def test_base_controller_init():
    """测试 BaseController 初始化"""
    async with anyio.create_task_group() as tg:
        controller = TestController(tg)

        assert controller.task_group is not None
        assert controller.logger is not None
        assert not controller.executed


@pytest.mark.anyio
async def test_execute_within_taskgroup():
    """测试 TaskGroup 内执行"""
    async with anyio.create_task_group() as tg:
        controller = TestController(tg)
        mock_coro = AsyncMock(return_value="test_result")

        result = await controller._execute_within_taskgroup(mock_coro())

        assert result == "test_result"
        mock_coro.assert_called_once()


@pytest.mark.anyio
async def test_log_execution():
    """测试日志记录"""
    async with anyio.create_task_group() as tg:
        controller = TestController(tg)

        # 记录日志（应该不会抛出异常）
        controller._log_execution("Test message")
        controller._log_execution("Warning message", "warning")
        controller._log_execution("Error message", "error")


@pytest.mark.anyio
async def test_state_driven_controller_init():
    """测试 StateDrivenController 初始化"""
    async with anyio.create_task_group() as tg:
        controller = TestStateDrivenController(tg)

        assert controller.task_group is not None
        assert controller.max_iterations == 3


@pytest.mark.anyio
async def test_state_machine_normal_flow():
    """测试状态机正常流程"""
    async with anyio.create_task_group() as tg:
        controller = TestStateDrivenController(tg)

        result = await controller.run_state_machine("Start", max_rounds=5)

        assert result is True
        assert controller.decision_count == 3


@pytest.mark.anyio
async def test_state_machine_max_iterations():
    """测试状态机达到最大迭代次数"""
    class LimitedController(TestStateDrivenController):
        async def _make_decision(self, current_state: str) -> str:
            self.decision_count += 1
            return "InProgress"  # 永远不返回终止状态

    async with anyio.create_task_group() as tg:
        controller = LimitedController(tg)

        result = await controller.run_state_machine("Start", max_rounds=3)

        assert result is False
        assert controller.decision_count == 3


@pytest.mark.anyio
async def test_is_termination_state():
    """测试终止状态判断"""
    async with anyio.create_task_group() as tg:
        controller = TestStateDrivenController(tg)

        assert controller._is_termination_state("Done") is True
        assert controller._is_termination_state("Ready for Done") is True
        assert controller._is_termination_state("In Progress") is False
        assert controller._is_termination_state("Draft") is False

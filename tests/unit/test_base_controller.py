"""
BaseController 单元测试
测试控制器基类的所有功能
"""

import pytest
import anyio
from unittest.mock import MagicMock, AsyncMock
import sys
from pathlib import Path

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.base_controller import (
    BaseController,
    StateDrivenController
)


class ConcreteTestController(BaseController):
    """测试用的具体控制器实现"""

    def __init__(self, task_group):
        super().__init__(task_group)
        self.executed = False

    async def execute(self, *args, **kwargs):
        self.executed = True
        return True


class ConcreteStateDrivenController(StateDrivenController):
    """测试用的状态驱动控制器"""

    def __init__(self, task_group):
        super().__init__(task_group)
        self.decisions = []
        self.executed_count = 0

    async def execute(self, *args, **kwargs):
        self.executed_count += 1
        return True

    async def _make_decision(self, current_state: str) -> str:
        self.decisions.append(current_state)
        # 简单的状态转换逻辑
        if current_state == "Start":
            return "InProgress"
        elif current_state == "InProgress":
            return "Done"
        else:
            return "Done"


@pytest.mark.anyio
async def test_base_controller_init():
    """测试 BaseController 初始化"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化控制器
    controller = ConcreteTestController(task_group)

    # 验证初始化
    assert controller.task_group == task_group
    assert controller.executed is False
    assert controller.logger is not None
    assert "test_base_controller" in controller.logger.name


@pytest.mark.anyio
async def test_base_controller_execute():
    """测试 BaseController 执行方法"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化控制器
    controller = ConcreteTestController(task_group)

    # 执行控制器
    result = await controller.execute()

    # 验证结果
    assert result is True
    assert controller.executed is True


@pytest.mark.anyio
async def test_base_controller_logging():
    """测试 BaseController 日志记录"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化控制器
    controller = ConcreteTestController(task_group)

    # 测试不同级别的日志
    controller._log_execution("Test info message")
    controller._log_execution("Test warning message", level="warning")
    controller._log_execution("Test error message", level="error")

    # 这些调用应该不会抛出异常
    assert True


@pytest.mark.anyio
async def test_state_driven_controller_init():
    """测试 StateDrivenController 初始化"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化状态驱动控制器
    controller = ConcreteStateDrivenController(task_group)

    # 验证初始化
    assert controller.task_group == task_group
    assert controller.max_iterations == 3
    assert controller.decisions == []


@pytest.mark.anyio
async def test_state_driven_controller_run_state_machine():
    """测试状态机运行"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化状态驱动控制器
    controller = ConcreteStateDrivenController(task_group)

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=3)

    # 验证结果
    assert result is True  # 应该达到终止状态
    assert len(controller.decisions) >= 1  # 应该有决策记录


@pytest.mark.anyio
async def test_state_driven_controller_max_iterations():
    """测试最大迭代次数限制"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化状态驱动控制器
    controller = ConcreteStateDrivenController(task_group)

    # 覆盖 _make_decision 方法以返回非终止状态
    async def infinite_decision(current_state):
        return "InProgress"

    controller._make_decision = infinite_decision

    # 运行状态机
    result = await controller.run_state_machine("Start", max_rounds=2)

    # 验证结果 - 应该因为达到最大迭代次数而返回 False
    assert result is False


@pytest.mark.anyio
async def test_termination_state_detection():
    """测试终止状态检测"""
    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 初始化状态驱动控制器
    controller = ConcreteStateDrivenController(task_group)

    # 测试终止状态
    assert controller._is_termination_state("Done") is True
    assert controller._is_termination_state("Ready for Done") is True

    # 测试非终止状态
    assert controller._is_termination_state("Start") is False
    assert controller._is_termination_state("InProgress") is False
    assert controller._is_termination_state("Draft") is False


@pytest.mark.anyio
async def test_base_controller_abstract_method():
    """测试抽象方法强制实现"""
    # 尝试直接实例化 BaseController 应该失败
    with pytest.raises(TypeError):
        controller = BaseController(MagicMock())


def test_log_execution_levels():
    """测试不同日志级别"""
    # 这个测试不需要异步上下文
    task_group = MagicMock(spec=anyio.abc.TaskGroup)
    controller = ConcreteTestController(task_group)

    # 测试各种日志级别（应该不会抛出异常）
    controller._log_execution("Info message")
    controller._log_execution("Debug message", level="debug")
    controller._log_execution("Warning message", level="warning")
    controller._log_execution("Error message", level="error")
    controller._log_execution("Critical message", level="critical")

    assert True


@pytest.mark.anyio
async def test_base_controller_inheritance():
    """测试控制器继承结构"""
    from autoBMAD.epic_automation.controllers.base_controller import (
        BaseController,
        StateDrivenController
    )

    # 验证继承关系
    assert issubclass(StateDrivenController, BaseController)

    # 创建模拟 TaskGroup
    task_group = MagicMock(spec=anyio.abc.TaskGroup)

    # 验证实例关系
    controller = ConcreteStateDrivenController(task_group)
    assert isinstance(controller, StateDrivenController)
    assert isinstance(controller, BaseController)


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

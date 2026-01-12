"""
Base Agent 单元测试
测试 BaseAgent 基类的功能
"""

import pytest
import anyio
from unittest.mock import MagicMock, AsyncMock
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """测试用的具体 Agent 实现"""

    async def execute(self, **kwargs):
        return "test_result"


@pytest.mark.anyio
async def test_base_agent_init():
    """测试 BaseAgent 初始化"""
    # 不带 TaskGroup 初始化
    agent = TestAgent("TestAgent")
    assert agent.name == "TestAgent"
    assert agent.task_group is None
    assert agent._execution_context == {}

    # 带 TaskGroup 初始化
    async with anyio.create_task_group() as tg:
        agent_with_tg = TestAgent("TestAgentWithTG", tg)
        assert agent_with_tg.name == "TestAgentWithTG"
        assert agent_with_tg.task_group == tg


@pytest.mark.anyio
async def test_base_agent_set_task_group():
    """测试 TaskGroup 设置"""
    agent = TestAgent("TestAgent")

    async with anyio.create_task_group() as tg:
        agent.set_task_group(tg)
        assert agent.task_group == tg


@pytest.mark.anyio
async def test_base_agent_validate_context():
    """测试执行上下文验证"""
    agent = TestAgent("TestAgent")

    # 没有 TaskGroup
    assert not agent._validate_execution_context()

    # 有 TaskGroup
    async with anyio.create_task_group() as tg:
        agent.set_task_group(tg)
        assert agent._validate_execution_context()


@pytest.mark.anyio
async def test_base_agent_log_execution():
    """测试执行日志记录"""
    agent = TestAgent("TestAgent")

    # 测试 info 日志
    with pytest.MonkeyPatch().context() as ctx:
        mock_log = MagicMock()
        ctx.setattr(agent.logger, 'info', mock_log)
        agent._log_execution("Test info message")
        mock_log.assert_called_once()
        assert "[TestAgent] Test info message" in mock_log.call_args[0][0]

    # 测试 warning 日志
    with pytest.MonkeyPatch().context() as ctx:
        mock_log = MagicMock()
        ctx.setattr(agent.logger, 'warning', mock_log)
        agent._log_execution("Test warning message", "warning")
        mock_log.assert_called_once()
        assert "[TestAgent] Test warning message" in mock_log.call_args[0][0]


@pytest.mark.anyio
async def test_base_agent_execute_without_taskgroup():
    """测试在没有 TaskGroup 的情况下执行"""
    agent = TestAgent("TestAgent")
    result = await agent.execute()
    assert result == "test_result"


@pytest.mark.anyio
async def test_base_agent_execute_with_taskgroup():
    """测试在有 TaskGroup 的情况下执行"""
    async with anyio.create_task_group() as tg:
        agent = TestAgent("TestAgent", tg)
        result = await agent.execute()
        assert result == "test_result"


@pytest.mark.anyio
async def test_base_agent_execute_with_kwargs():
    """测试带参数的执行"""
    agent = TestAgent("TestAgent")
    result = await agent.execute(param1="value1", param2="value2")
    assert result == "test_result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

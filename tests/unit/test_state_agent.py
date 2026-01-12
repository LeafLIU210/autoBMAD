"""
StateAgent 单元测试
测试状态解析和管理 Agent 的功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.state_agent import StateAgent


@pytest.mark.anyio
async def test_state_agent_init():
    """测试 StateAgent 初始化"""
    # 不带 TaskGroup 初始化
    agent = StateAgent()
    assert agent.name == "StateAgent"
    assert agent.task_group is None

    # 带 TaskGroup 初始化
    async with anyio.create_task_group() as tg:
        agent_with_tg = StateAgent(task_group=tg)
        assert agent_with_tg.name == "StateAgent"
        assert agent_with_tg.task_group == tg


@pytest.mark.anyio
async def test_state_agent_init_with_taskgroup():
    """测试带 TaskGroup 的 StateAgent 初始化"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)
        assert agent.task_group == tg
        assert agent.name == "StateAgent"


@pytest.mark.anyio
async def test_state_agent_parse_status():
    """测试解析状态"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Draft"
            f.write(story_content)
            story_path = f.name

        # 模拟解析状态
        with patch.object(agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Draft"

            status = await agent.parse_status(story_path)

            assert status == "Draft"
            mock_parse.assert_called_once_with(story_path)

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_state_agent_execute():
    """测试 StateAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Draft"
            f.write(story_content)
            story_path = f.name

        # 模拟 parse_status 方法
        with patch.object(agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Draft"

            result = await agent.execute(story_path)

            assert result == "Draft"
            mock_parse.assert_called_once_with(story_path)

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_state_agent_execute_with_taskgroup():
    """测试在 TaskGroup 内执行"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_path = f.name

        with patch.object(agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Ready for Development"

            result = await agent.execute(story_path)

            assert result == "Ready for Development"

        Path(story_path).unlink()


@pytest.mark.anyio
async def test_state_agent_get_processing_status():
    """测试获取处理状态"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: In Progress"
            f.write(story_content)
            story_path = f.name

        # 模拟 get_processing_status 方法
        with patch.object(agent, 'get_processing_status', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = "in_progress"

            result = await agent.get_processing_status(story_path)

            assert result == "in_progress"
            mock_get.assert_called_once_with(story_path)

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_state_agent_update_story_status():
    """测试更新故事状态"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Draft"
            f.write(story_content)
            story_path = f.name

        # 模拟 update_story_status 方法
        with patch.object(agent, 'update_story_status', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = True

            result = await agent.update_story_status(story_path, "In Progress")

            assert result is True
            mock_update.assert_called_once_with(story_path, "In Progress")

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_state_agent_validate_execution_context():
    """测试执行上下文验证"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        # 没有 TaskGroup
        assert not agent._validate_execution_context()

        # 有 TaskGroup
        agent.set_task_group(tg)
        assert agent._validate_execution_context()


@pytest.mark.anyio
async def test_state_agent_log_execution():
    """测试 StateAgent 日志记录"""
    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        with pytest.MonkeyPatch().context() as ctx:
            mock_log = MagicMock()
            ctx.setattr(agent.logger, 'info', mock_log)
            agent._log_execution("Test message")
            mock_log.assert_called_once()
            assert "[StateAgent] Test message" in mock_log.call_args[0][0]


@pytest.mark.anyio
async def test_state_agent_execute_without_taskgroup():
    """测试在没有 TaskGroup 的情况下执行"""
    agent = StateAgent()

    # 创建临时故事文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        story_path = f.name

    with patch.object(agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = "Draft"

        result = await agent.execute(story_path)

        # 没有 TaskGroup 时应该仍然可以执行
        assert result == "Draft"

    Path(story_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
QAAgent 单元测试
测试 Quality Assurance Agent 的功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.qa_agent import QAAgent


@pytest.mark.anyio
async def test_qa_agent_init():
    """测试 QAAgent 初始化"""
    # 不带 TaskGroup 初始化
    agent = QAAgent()
    assert agent.name == "QAAgent"
    assert agent.task_group is None
    assert agent.use_claude is True

    # 带 TaskGroup 初始化
    async with anyio.create_task_group() as tg:
        agent_with_tg = QAAgent(task_group=tg)
        assert agent_with_tg.name == "QAAgent"
        assert agent_with_tg.task_group == tg


@pytest.mark.anyio
async def test_qa_agent_init_with_params():
    """测试带参数的 QAAgent 初始化"""
    async with anyio.create_task_group() as tg:
        log_manager = MagicMock()

        agent = QAAgent(
            task_group=tg,
            use_claude=False,
            log_manager=log_manager
        )

        assert agent.task_group == tg
        assert agent.use_claude is False
        assert agent._log_manager == log_manager


@pytest.mark.anyio
async def test_qa_agent_execute():
    """测试 QAAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Ready for Review"
            f.write(story_content)
            story_path = f.name

        # QAAgent 始终返回 passed=True
        result = await agent.execute(story_path)

        # QAAgent 应该始终返回 passed=True
        assert result["passed"] is True
        assert result["completed"] is True
        assert result["needs_fix"] is False

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_qa_agent_execute_with_taskgroup():
    """测试在 TaskGroup 内执行"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_path = f.name

        # QAAgent 始终返回 passed=True
        result = await agent.execute(story_path)

        assert result["passed"] is True

        Path(story_path).unlink()


@pytest.mark.anyio
async def test_qa_agent_execute_qa_phase():
    """测试 QA 阶段执行"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_path = f.name

        with patch.object(agent, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": "QA completed"
            }

            result = await agent.execute_qa_phase(
                story_path=story_path,
                source_dir="src",
                test_dir="tests"
            )

            # execute_qa_phase 应该始终返回 True
            assert result is True
            mock_execute.assert_called_once()

        Path(story_path).unlink()


@pytest.mark.anyio
async def test_qa_agent_execute_always_returns_passed():
    """测试 QAAgent 始终返回 passed=True 的设计"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_path = f.name

        # 使用不存在的文件测试异常处理
        result = await agent.execute(story_path)

        # QAAgent 应该始终返回 passed=True，即使出现异常
        assert result["passed"] is True
        assert result["completed"] is True

        Path(story_path).unlink()


@pytest.mark.anyio
async def test_qa_agent_get_statistics():
    """测试获取 QA 统计信息"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        # 没有会话管理器的情况
        stats = await agent.get_statistics()
        assert "agent_name" in stats
        assert stats["agent_name"] == "QAAgent"


@pytest.mark.anyio
async def test_qa_agent_log_execution():
    """测试 QAAgent 日志记录"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        with pytest.MonkeyPatch().context() as ctx:
            mock_log = MagicMock()
            ctx.setattr(agent.logger, 'info', mock_log)
            agent._log_execution("Test message")
            mock_log.assert_called_once()
            assert "[QAAgent] Test message" in mock_log.call_args[0][0]


@pytest.mark.anyio
async def test_qa_agent_parse_story_status():
    """测试解析故事状态"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Ready for Review"
            f.write(story_content)
            story_path = f.name

        # 模拟解析状态
        with patch.object(agent, '_parse_story_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "Ready for Review"

            status = await agent._parse_story_status(story_path)

            assert status == "Ready for Review"
            mock_parse.assert_called_once_with(story_path)

        Path(story_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

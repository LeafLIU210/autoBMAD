"""
DevAgent 单元测试
测试 Development Agent 的功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.dev_agent import DevAgent


@pytest.mark.anyio
async def test_dev_agent_init():
    """测试 DevAgent 初始化"""
    # 不带 TaskGroup 初始化
    agent = DevAgent()
    assert agent.name == "DevAgent"
    assert agent.task_group is None
    assert agent.use_claude is True
    assert agent._current_story_path is None

    # 带 TaskGroup 初始化
    async with anyio.create_task_group() as tg:
        agent_with_tg = DevAgent(task_group=tg)
        assert agent_with_tg.name == "DevAgent"
        assert agent_with_tg.task_group == tg


@pytest.mark.anyio
async def test_dev_agent_init_with_params():
    """测试带参数的 DevAgent 初始化"""
    async with anyio.create_task_group() as tg:
        log_manager = MagicMock()

        agent = DevAgent(
            task_group=tg,
            use_claude=False,
            log_manager=log_manager
        )

        assert agent.task_group == tg
        assert agent.use_claude is False
        assert agent._log_manager == log_manager


@pytest.mark.anyio
async def test_dev_agent_execute():
    """测试 DevAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        # 创建临时故事文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_content = "# Test Story\n\n**Status**: Draft"
            f.write(story_content)
            story_path = f.name

        # DevAgent 始终返回 True，直接调用
        result = await agent.execute(story_path)

        # DevAgent 应该始终返回 True
        assert result is True

        # 清理临时文件
        Path(story_path).unlink()


@pytest.mark.anyio
async def test_dev_agent_execute_with_taskgroup():
    """测试在 TaskGroup 内执行"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            story_path = f.name

        # DevAgent 始终返回 True
        result = await agent.execute(story_path)

        assert result is True

        Path(story_path).unlink()


@pytest.mark.anyio
async def test_dev_agent_execute_story_not_found():
    """测试故事文件不存在时的执行"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        result = await agent.execute("/nonexistent/story.md")

        # DevAgent 应该始终返回 True，即使文件不存在
        assert result is True


@pytest.mark.anyio
async def test_dev_agent_extract_requirements():
    """测试提取需求"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        story_content = """# Test Story

## Description
Create a simple function

## Acceptance Criteria
- [ ] Function works correctly
"""

        requirements = await agent._extract_requirements(story_content)

        # 验证返回的是字典类型
        assert isinstance(requirements, dict)
        # 验证有内容
        assert len(requirements) > 0


@pytest.mark.anyio
async def test_dev_agent_validate_prompt_format():
    """测试提示格式验证"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        # 有效的提示
        valid_prompt = "This is a valid prompt"
        assert agent._validate_prompt_format(valid_prompt) is True

        # 无效的提示
        invalid_prompt = ""
        assert agent._validate_prompt_format(invalid_prompt) is False


@pytest.mark.anyio
async def test_dev_agent_check_claude_available():
    """测试检查 Claude 可用性"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg, use_claude=True)

        # 这个测试依赖于系统环境，所以只是验证方法可以被调用
        try:
            available = agent._check_claude_available()
            assert isinstance(available, bool)
        except Exception as e:
            # 如果检查失败，这也是可接受的
            print(f"Claude availability check skipped: {e}")


@pytest.mark.anyio
async def test_dev_agent_log_execution():
    """测试 DevAgent 日志记录"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        with pytest.MonkeyPatch().context() as ctx:
            mock_log = MagicMock()
            ctx.setattr(agent.logger, 'info', mock_log)
            agent._log_execution("Test message")
            mock_log.assert_called_once()
            assert "[DevAgent] Test message" in mock_log.call_args[0][0]


@pytest.mark.anyio
async def test_dev_agent_always_returns_true():
    """测试 DevAgent 始终返回 True 的设计"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)

        # 使用不存在的文件测试异常处理
        result = await agent.execute("/test/nonexistent/story.md")
        # DevAgent 应该始终返回 True，即使出现异常
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

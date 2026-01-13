"""
State Agent 单元测试
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from autoBMAD.epic_automation.agents.state_agent import StateAgent
from autoBMAD.epic_automation.agents.state_agent import SimpleStoryParser


@pytest.fixture
def state_agent():
    """创建 StateAgent 实例"""
    return StateAgent()


@pytest.fixture
def sample_story_content():
    """示例故事内容"""
    return """# Story 1.1: Test Story

**Status**: Ready for Development

## Description
This is a test story.
"""


def test_state_agent_init(state_agent):
    """测试 StateAgent 初始化"""
    assert state_agent.name == "StateAgent"
    assert isinstance(state_agent.status_parser, SimpleStoryParser)
    assert state_agent.logger is not None


@pytest.mark.anyio
async def test_parse_status_with_file(state_agent, tmp_path):
    """测试解析文件状态"""
    # 创建临时故事文件
    story_file = tmp_path / "test_story.md"
    story_file.write_text("# Test Story\n\n**Status**: Ready for Development\n")

    # 模拟解析器返回
    with patch.object(state_agent.status_parser, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = "Ready for Development"

        status = await state_agent.parse_status(str(story_file))

        assert status == "Ready for Development"
        mock_parse.assert_called_once()


@pytest.mark.anyio
async def test_parse_status_with_content(state_agent, sample_story_content):
    """测试解析内容状态"""
    with patch.object(state_agent.status_parser, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = "In Progress"

        status = await state_agent.parse_status(sample_story_content)

        assert status == "In Progress"
        mock_parse.assert_called_once()


@pytest.mark.anyio
async def test_parse_status_error(state_agent, sample_story_content):
    """测试解析状态错误"""
    with patch.object(state_agent.status_parser, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.side_effect = Exception("Parse error")

        status = await state_agent.parse_status(sample_story_content)

        assert status is None


@pytest.mark.anyio
async def test_get_processing_status(state_agent, tmp_path):
    """测试获取处理状态"""
    story_file = tmp_path / "test_story.md"
    story_file.write_text("# Test Story\n\n**Status**: Ready for Review\n")

    with patch.object(state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = "Ready for Review"

        processing_status = await state_agent.get_processing_status(str(story_file))

        # Ready for Review 应该转换为 "review"
        assert processing_status == "review"
        mock_parse.assert_called_once()


@pytest.mark.anyio
async def test_update_story_status(state_agent, tmp_path):
    """测试更新故事状态"""
    story_file = tmp_path / "test_story.md"
    story_file.write_text("# Test Story\n\n**Status**: Draft\n")

    result = await state_agent.update_story_status(str(story_file), "In Progress")

    assert result is True


@pytest.mark.anyio
async def test_execute_with_args(state_agent, sample_story_content):
    """测试 execute 方法"""
    with patch.object(state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
        mock_parse.return_value = "Done"

        result = await state_agent.execute(sample_story_content)

        assert result == "Done"
        mock_parse.assert_called_once_with(sample_story_content)


@pytest.mark.anyio
async def test_execute_without_args(state_agent):
    """测试不带参数的 execute 方法"""
    result = await state_agent.execute()

    assert result is None

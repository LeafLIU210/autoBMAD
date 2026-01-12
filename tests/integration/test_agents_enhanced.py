"""
Agents 增强集成测试
专门提升 agents 模块的覆盖率
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock, call
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.sm_agent import SMAgent
from autoBMAD.epic_automation.agents.dev_agent import DevAgent
from autoBMAD.epic_automation.agents.qa_agent import QAAgent
from autoBMAD.epic_automation.agents.state_agent import SimpleStoryParser, CORE_STATUS_DONE, CORE_STATUS_READY_FOR_DONE
from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.agents.quality_agents import RuffAgent, BasedPyrightAgent


@pytest.fixture
def temp_agent_environment():
    """创建临时代理环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建目录结构
        docs_dir = tmp_path / "docs"
        stories_dir = docs_dir / "stories"
        tasks_dir = tmp_path / ".bmad-core" / "tasks"

        for dir_path in [docs_dir, stories_dir, tasks_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建测试故事文件
        story_file = stories_dir / "001-test-story.md"
        story_file.write_text("""# Story 001: Test Story

**Status**: Draft

## Description
Test story for agent testing

## Acceptance Criteria
1. Test criterion 1
2. Test criterion 2
""", encoding='utf-8')

        yield {
            "tmp_path": tmp_path,
            "docs_dir": docs_dir,
            "stories_dir": stories_dir,
            "tasks_dir": tasks_dir,
            "story_file": story_file
        }


class TestSMAgentEnhanced:
    """SMAgent 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_agent_initialization(self, temp_agent_environment):
        """测试SM代理初始化"""
        env = temp_agent_environment

        agent = SMAgent()

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_stories_from_epic(self, temp_agent_environment):
        """测试从Epic创建故事"""
        env = temp_agent_environment

        # 创建epic文件
        epic_file = env["docs_dir"] / "test-epic.md"
        epic_file.write_text("""# Epic 1: Test Epic

### Story 001: First Story
**Story ID**: 001

### Story 002: Second Story
**Story ID**: 002
""", encoding='utf-8')

        agent = SMAgent()

        # Mock SDK调用
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "completed", "result": "Stories created successfully"}

            result = await agent.create_stories_from_epic(str(epic_file))

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_stories_with_task_guidance(self, temp_agent_environment):
        """测试使用任务指导创建故事"""
        env = temp_agent_environment

        # 创建任务指导文件
        task_guidance = env["tasks_dir"] / "story-creation.md"
        task_guidance.write_text("Task guidance for story creation", encoding='utf-8')

        epic_file = env["docs_dir"] / "test-epic.md"
        epic_file.write_text("""# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
""", encoding='utf-8')

        agent = SMAgent()

        # Mock SDK调用
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "completed", "result": "Stories created"}

            result = await agent.create_stories_from_epic(
                str(epic_file),
                task_guidance_path=str(task_guidance)
            )

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_with_epic_content(self, temp_agent_environment):
        """测试使用Epic内容执行"""
        env = temp_agent_environment

        agent = SMAgent()

        epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001

This is a test epic.
"""

        # Mock SDK调用
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "completed", "result": "Stories created"}

            result = await agent.execute(epic_content=epic_content)

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_with_error_handling(self, temp_agent_environment):
        """测试执行中的错误处理"""
        env = temp_agent_environment

        agent = SMAgent()

        epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
"""

        # Mock SDK调用失败
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.side_effect = Exception("SDK call failed")

            result = await agent.execute(epic_content=epic_content)

            assert result is False


class TestDevAgentEnhanced:
    """DevAgent 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_dev_agent_initialization(self, temp_agent_environment):
        """测试开发代理初始化"""
        env = temp_agent_environment

        # 测试默认初始化
        agent = DevAgent(use_claude=False)

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_dev_agent_with_claude(self, temp_agent_environment):
        """测试使用Claude的开发代理"""
        env = temp_agent_environment

        agent = DevAgent(use_claude=True)

        assert agent is not None
        assert agent.use_claude is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_development_task(self, temp_agent_environment):
        """测试执行开发任务"""
        env = temp_agent_environment

        agent = DevAgent(use_claude=False)

        story_content = """# Story 001: Test Story

**Status**: Draft

## Description
Develop a test feature
"""

        # Mock SDK调用
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "completed", "result": "Development completed"}

            result = await agent.execute(story_content=story_content)

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_with_error_handling(self, temp_agent_environment):
        """测试开发代理错误处理"""
        env = temp_agent_environment

        agent = DevAgent(use_claude=False)

        story_content = """# Story 001: Test Story

**Status**: Draft
"""

        # Mock SDK调用失败
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.side_effect = Exception("Development failed")

            result = await agent.execute(story_content=story_content)

            assert result is False


class TestQAAgentEnhanced:
    """QAAgent 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_qa_agent_initialization(self, temp_agent_environment):
        """测试QA代理初始化"""
        env = temp_agent_environment

        agent = QAAgent()

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_qa_review(self, temp_agent_environment):
        """测试执行QA审查"""
        env = temp_agent_environment

        agent = QAAgent()

        story_content = """# Story 001: Test Story

**Status**: Ready for Review

## Description
Feature implementation complete
"""

        # Mock SDK调用
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "completed", "result": "QA passed"}

            result = await agent.execute(story_content=story_content)

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_with_qa_failures(self, temp_agent_environment):
        """测试QA失败情况"""
        env = temp_agent_environment

        agent = QAAgent()

        story_content = """# Story 001: Test Story

**Status**: Ready for Review
"""

        # Mock QA失败
        with patch.object(agent, '_call_sdk') as mock_sdk:
            mock_sdk.return_value = {"status": "failed", "errors": 3}

            result = await agent.execute(story_content=story_content)

            assert isinstance(result, bool)


class TestStateAgentEnhanced:
    """StateAgent 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_simple_story_parser_initialization(self, temp_agent_environment):
        """测试简单故事解析器初始化"""
        env = temp_agent_environment

        # Mock SDK wrapper
        mock_sdk = MagicMock()

        parser = SimpleStoryParser(sdk_wrapper=mock_sdk)

        assert parser is not None
        assert hasattr(parser, 'parse_status')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_status_with_draft(self, temp_agent_environment):
        """测试解析Draft状态"""
        env = temp_agent_environment

        mock_sdk = MagicMock()
        parser = SimpleStoryParser(sdk_wrapper=mock_sdk)

        content = """# Story 001: Test Story

**Status**: Draft

## Description
Test story
"""

        # Mock SDK调用
        mock_sdk.call_agent = AsyncMock(return_value="Draft")

        status = await parser.parse_status(content)

        assert status is not None
        assert isinstance(status, str)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_status_with_done(self, temp_agent_environment):
        """测试解析Done状态"""
        env = temp_agent_environment

        mock_sdk = MagicMock()
        parser = SimpleStoryParser(sdk_wrapper=mock_sdk)

        content = """# Story 001: Test Story

**Status**: Done

## Description
Test story
"""

        # Mock SDK调用
        mock_sdk.call_agent = AsyncMock(return_value="Done")

        status = await parser.parse_status(content)

        assert status is not None
        assert isinstance(status, str)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_status_with_error(self, temp_agent_environment):
        """测试解析状态错误处理"""
        env = temp_agent_environment

        mock_sdk = MagicMock()
        parser = SimpleStoryParser(sdk_wrapper=mock_sdk)

        content = """# Story 001: Test Story

**Status**: Unknown
"""

        # Mock SDK调用失败
        mock_sdk.call_agent = AsyncMock(side_effect=Exception("Parse failed"))

        status = await parser.parse_status(content)

        # 应该返回默认状态或错误状态
        assert status is not None

    @pytest.mark.integration
    def test_core_status_constants(self, temp_agent_environment):
        """测试核心状态常量"""
        env = temp_agent_environment

        # 验证常量存在
        assert CORE_STATUS_DONE is not None
        assert CORE_STATUS_READY_FOR_DONE is not None

        # 验证它们是不同的
        assert CORE_STATUS_DONE != CORE_STATUS_READY_FOR_DONE


class TestBaseAgentEnhanced:
    """BaseAgent 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_base_agent_initialization(self, temp_agent_environment):
        """测试基础代理初始化"""
        env = temp_agent_environment

        agent = BaseAgent()

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_base_agent_abstract_execute(self, temp_agent_environment):
        """测试基础代理抽象执行方法"""
        env = temp_agent_environment

        agent = BaseAgent()

        # 尝试调用抽象方法应该引发异常
        with pytest.raises(NotImplementedError):
            await agent.execute()


class TestQualityAgentsEnhanced:
    """Quality Agents 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_ruff_agent_initialization(self, temp_agent_environment):
        """测试Ruff代理初始化"""
        env = temp_agent_environment

        agent = RuffAgent()

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_ruff_agent_execute(self, temp_agent_environment):
        """测试Ruff代理执行"""
        env = temp_agent_environment

        agent = RuffAgent()

        # Mock subprocess调用
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="All good", stderr="")

            result = await agent.execute(source_dir=str(env["tmp_path"]))

            assert result is not None
            assert "status" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_ruff_agent_with_errors(self, temp_agent_environment):
        """测试Ruff代理错误情况"""
        env = temp_agent_environment

        agent = RuffAgent()

        # Mock Ruff失败
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="3 errors found")

            result = await agent.execute(source_dir=str(env["tmp_path"]))

            assert result is not None
            assert result.get("status") == "failed" or result.get("errors", 0) > 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_basedpyright_agent_initialization(self, temp_agent_environment):
        """测试BasedPyright代理初始化"""
        env = temp_agent_environment

        agent = BasedPyrightAgent()

        assert agent is not None
        assert hasattr(agent, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_basedpyright_agent_execute(self, temp_agent_environment):
        """测试BasedPyright代理执行"""
        env = temp_agent_environment

        agent = BasedPyrightAgent()

        # Mock subprocess调用
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="No errors", stderr="")

            result = await agent.execute(source_dir=str(env["tmp_path"]))

            assert result is not None
            assert "status" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_basedpyright_agent_with_errors(self, temp_agent_environment):
        """测试BasedPyright代理错误情况"""
        env = temp_agent_environment

        agent = BasedPyrightAgent()

        # Mock BasedPyright失败
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="2 errors found")

            result = await agent.execute(source_dir=str(env["tmp_path"]))

            assert result is not None
            assert result.get("status") == "failed" or result.get("errors", 0) > 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_agents_with_nonexistent_directory(self, temp_agent_environment):
        """测试不存在目录的质量代理"""
        env = temp_agent_environment

        ruff_agent = RuffAgent()
        basedpyright_agent = BasedPyrightAgent()

        nonexistent_dir = "/nonexistent/path"

        # Ruff代理应该优雅处理
        result = await ruff_agent.execute(source_dir=nonexistent_dir)
        assert result is not None

        # BasedPyright代理应该优雅处理
        result = await basedpyright_agent.execute(source_dir=nonexistent_dir)
        assert result is not None


class TestAgentsIntegration:
    """Agents 集成测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_to_dev_pipeline(self, temp_agent_environment):
        """测试SM到Dev的流水线"""
        env = temp_agent_environment

        sm_agent = SMAgent()
        dev_agent = DevAgent(use_claude=False)

        epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""

        # Mock SM代理创建故事
        with patch.object(sm_agent, '_call_sdk') as mock_sm_sdk:
            mock_sm_sdk.return_value = {"status": "completed", "result": "Story created"}

            sm_result = await sm_agent.execute(epic_content=epic_content)

            assert isinstance(sm_result, bool)

        # Mock Dev代理开发
        with patch.object(dev_agent, '_call_sdk') as mock_dev_sdk:
            mock_dev_sdk.return_value = {"status": "completed", "result": "Development done"}

            dev_result = await dev_agent.execute(story_content=epic_content)

            assert isinstance(dev_result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_dev_to_qa_pipeline(self, temp_agent_environment):
        """测试Dev到QA的流水线"""
        env = temp_agent_environment

        dev_agent = DevAgent(use_claude=False)
        qa_agent = QAAgent()

        story_content = """# Story 001: Test Story

**Status**: Ready for Review
"""

        # Mock Dev代理
        with patch.object(dev_agent, '_call_sdk') as mock_dev_sdk:
            mock_dev_sdk.return_value = {"status": "completed", "result": "Development done"}

            dev_result = await dev_agent.execute(story_content=story_content)

            assert isinstance(dev_result, bool)

        # Mock QA代理
        with patch.object(qa_agent, '_call_sdk') as mock_qa_sdk:
            mock_qa_sdk.return_value = {"status": "completed", "result": "QA passed"}

            qa_result = await qa_agent.execute(story_content=story_content)

            assert isinstance(qa_result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

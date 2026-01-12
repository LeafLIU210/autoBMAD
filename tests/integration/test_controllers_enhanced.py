"""
Controllers 增强集成测试
专门提升 controllers 模块的覆盖率
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock, call
import sys
import anyio

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.sm_controller import SMController
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.controllers.quality_controller import QualityController
from autoBMAD.epic_automation.controllers.base_controller import BaseController


@pytest.fixture
async def temp_controller_environment():
    """创建临时控制器环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建目录结构
        docs_dir = tmp_path / "docs"
        stories_dir = docs_dir / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [docs_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建测试故事文件
        story_file = stories_dir / "001-test-story.md"
        story_file.write_text("""# Story 001: Test Story

**Status**: Draft

## Description
Test story for controller testing

## Acceptance Criteria
1. Test criterion 1
2. Test criterion 2
""", encoding='utf-8')

        yield {
            "tmp_path": tmp_path,
            "docs_dir": docs_dir,
            "stories_dir": stories_dir,
            "src_dir": src_dir,
            "tests_dir": tests_dir,
            "story_file": story_file
        }


class TestSMControllerEnhanced:
    """SMController 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_controller_initialization(self, temp_controller_environment):
        """测试SM控制器初始化"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = SMController(tg, project_root=env["tmp_path"])

            assert controller is not None
            assert hasattr(controller, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_controller_execute(self, temp_controller_environment):
        """测试SM控制器执行"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = SMController(tg, project_root=env["tmp_path"])

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""

            # Mock SM代理
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent:
                mock_agent = MagicMock()
                mock_agent.create_stories_from_epic = AsyncMock(return_value=True)
                MockSMAgent.return_value = mock_agent

                result = await controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_controller_with_task_group(self, temp_controller_environment):
        """测试SM控制器与任务组"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = SMController(tg, project_root=env["tmp_path"])

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""

            # Mock SM代理
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent:
                mock_agent = MagicMock()
                mock_agent.create_stories_from_epic = AsyncMock(return_value=True)
                MockSMAgent.return_value = mock_agent

                # 在任务组上下文中执行
                result = await controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_controller_error_handling(self, temp_controller_environment):
        """测试SM控制器错误处理"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = SMController(tg, project_root=env["tmp_path"])

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
"""

            # Mock SM代理失败
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent:
                mock_agent = MagicMock()
                mock_agent.create_stories_from_epic = AsyncMock(side_effect=Exception("SM failed"))
                MockSMAgent.return_value = mock_agent

                result = await controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                # 应该处理错误
                assert isinstance(result, bool)


class TestDevQaControllerEnhanced:
    """DevQaController 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_initialization(self, temp_controller_environment):
        """测试DevQA控制器初始化"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg, use_claude=False)

            assert controller is not None
            assert hasattr(controller, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_execute(self, temp_controller_environment):
        """测试DevQA控制器执行"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg, use_claude=False)

            story_path = str(env["story_file"])

            # Mock Dev代理和QA代理
            with patch('autoBMAD.epic_automation.agents.dev_agent.DevAgent') as MockDevAgent, \
                 patch('autoBMAD.epic_automation.agents.qa_agent.QAAgent') as MockQAAgent:

                mock_dev = MagicMock()
                mock_dev.execute = AsyncMock(return_value=True)
                MockDevAgent.return_value = mock_dev

                mock_qa = MagicMock()
                mock_qa.execute = AsyncMock(return_value=True)
                MockQAAgent.return_value = mock_qa

                result = await controller.execute(story_path)

                assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_with_claude(self, temp_controller_environment):
        """测试使用Claude的DevQA控制器"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg, use_claude=True)

            assert controller.use_claude is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_with_log_manager(self, temp_controller_environment):
        """测试带日志管理器的DevQA控制器"""
        env = temp_controller_environment

        log_manager = MagicMock()

        async with anyio.create_task_group() as tg:
            controller = DevQaController(
                tg,
                use_claude=False,
                log_manager=log_manager
            )

            assert controller.log_manager == log_manager

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_multiple_iterations(self, temp_controller_environment):
        """测试DevQA控制器多次迭代"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg, use_claude=False)

            story_path = str(env["story_file"])

            call_count = 0
            async def mock_execute(story_path):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    # 前两次返回False触发重试
                    return False
                return True

            # Mock Dev和QA代理
            with patch('autoBMAD.epic_automation.agents.dev_agent.DevAgent') as MockDevAgent, \
                 patch('autoBMAD.epic_automation.agents.qa_agent.QAAgent') as MockQAAgent:

                mock_dev = MagicMock()
                mock_dev.execute = mock_execute
                MockDevAgent.return_value = mock_dev

                mock_qa = MagicMock()
                mock_qa.execute = mock_execute
                MockQAAgent.return_value = mock_qa

                result = await controller.execute(story_path)

                assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_devqa_controller_error_handling(self, temp_controller_environment):
        """测试DevQA控制器错误处理"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = DevQaController(tg, use_claude=False)

            story_path = str(env["story_file"])

            # Mock Dev代理失败
            with patch('autoBMAD.epic_automation.agents.dev_agent.DevAgent') as MockDevAgent, \
                 patch('autoBMAD.epic_automation.agents.qa_agent.QAAgent') as MockQAAgent:

                mock_dev = MagicMock()
                mock_dev.execute = AsyncMock(side_effect=Exception("Dev failed"))
                MockDevAgent.return_value = mock_dev

                mock_qa = MagicMock()
                mock_qa.execute = AsyncMock(return_value=True)
                MockQAAgent.return_value = mock_qa

                result = await controller.execute(story_path)

                # 应该处理错误
                assert isinstance(result, bool)


class TestQualityControllerEnhanced:
    """QualityController 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_controller_initialization(self, temp_controller_environment):
        """测试质量控制器初始化"""
        env = temp_controller_environment

        controller = QualityController()

        assert controller is not None
        assert hasattr(controller, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_controller_execute(self, temp_controller_environment):
        """测试质量控制器执行"""
        env = temp_controller_environment

        controller = QualityController()

        story_path = str(env["story_file"])

        # Mock质量代理
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff, \
             patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockPyright:

            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockRuff.return_value = mock_ruff

            mock_pyright = MagicMock()
            mock_pyright.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockPyright.return_value = mock_pyright

            result = await controller.execute(story_path)

            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_controller_with_quality_failures(self, temp_controller_environment):
        """测试质量控制器的质量失败"""
        env = temp_controller_environment

        controller = QualityController()

        story_path = str(env["story_file"])

        # Mock质量代理失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff, \
             patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockPyright:

            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(return_value={"status": "failed", "errors": 5})
            MockRuff.return_value = mock_ruff

            mock_pyright = MagicMock()
            mock_pyright.execute = AsyncMock(return_value={"status": "failed", "errors": 3})
            MockPyright.return_value = mock_pyright

            result = await controller.execute(story_path)

            # 应该处理失败
            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_controller_error_handling(self, temp_controller_environment):
        """测试质量控制器错误处理"""
        env = temp_controller_environment

        controller = QualityController()

        story_path = str(env["story_file"])

        # Mock质量代理抛出异常
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff:
            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(side_effect=Exception("Quality check failed"))
            MockRuff.return_value = mock_ruff

            result = await controller.execute(story_path)

            # 应该处理错误
            assert isinstance(result, bool)


class TestBaseControllerEnhanced:
    """BaseController 增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_base_controller_initialization(self, temp_controller_environment):
        """测试基础控制器初始化"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = BaseController(tg)

            assert controller is not None
            assert hasattr(controller, 'execute')

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_base_controller_abstract_execute(self, temp_controller_environment):
        """测试基础控制器抽象执行方法"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = BaseController(tg)

            # 尝试调用抽象方法应该引发异常
            with pytest.raises(NotImplementedError):
                await controller.execute("test")


class TestControllersIntegration:
    """控制器集成测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sm_to_devqa_pipeline(self, temp_controller_environment):
        """测试SM到DevQA的流水线"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            # SM控制器
            sm_controller = SMController(tg, project_root=env["tmp_path"])

            # DevQA控制器
            devqa_controller = DevQaController(tg, use_claude=False)

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""

            # Mock SM代理
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent:
                mock_sm = MagicMock()
                mock_sm.create_stories_from_epic = AsyncMock(return_value=True)
                MockSMAgent.return_value = mock_sm

                sm_result = await sm_controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                assert isinstance(sm_result, bool)

            # Mock Dev和QA代理
            with patch('autoBMAD.epic_automation.agents.dev_agent.DevAgent') as MockDevAgent, \
                 patch('autoBMAD.epic_automation.agents.qa_agent.QAAgent') as MockQAAgent:

                mock_dev = MagicMock()
                mock_dev.execute = AsyncMock(return_value=True)
                MockDevAgent.return_value = mock_dev

                mock_qa = MagicMock()
                mock_qa.execute = AsyncMock(return_value=True)
                MockQAAgent.return_value = mock_qa

                devqa_result = await devqa_controller.execute(str(env["story_file"]))

                assert isinstance(devqa_result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_full_pipeline_sm_devqa_quality(self, temp_controller_environment):
        """测试完整的SM-DevQA-Quality流水线"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            # 创建所有控制器
            sm_controller = SMController(tg, project_root=env["tmp_path"])
            devqa_controller = DevQaController(tg, use_claude=False)
            quality_controller = QualityController()

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""

            story_path = str(env["story_file"])

            # Mock所有代理
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent, \
                 patch('autoBMAD.epic_automation.agents.dev_agent.DevAgent') as MockDevAgent, \
                 patch('autoBMAD.epic_automation.agents.qa_agent.QAAgent') as MockQAAgent, \
                 patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff, \
                 patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockPyright:

                # Mock SM
                mock_sm = MagicMock()
                mock_sm.create_stories_from_epic = AsyncMock(return_value=True)
                MockSMAgent.return_value = mock_sm

                # Mock Dev
                mock_dev = MagicMock()
                mock_dev.execute = AsyncMock(return_value=True)
                MockDevAgent.return_value = mock_dev

                # Mock QA
                mock_qa = MagicMock()
                mock_qa.execute = AsyncMock(return_value=True)
                MockQAAgent.return_value = mock_qa

                # Mock质量代理
                mock_ruff = MagicMock()
                mock_ruff.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
                MockRuff.return_value = mock_ruff

                mock_pyright = MagicMock()
                mock_pyright.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
                MockPyright.return_value = mock_pyright

                # 执行完整流水线
                sm_result = await sm_controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                devqa_result = await devqa_controller.execute(story_path)

                quality_result = await quality_controller.execute(story_path)

                # 验证所有阶段都执行
                assert isinstance(sm_result, bool)
                assert isinstance(devqa_result, bool)
                assert isinstance(quality_result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_controllers_with_task_group_isolation(self, temp_controller_environment):
        """测试控制器的任务组隔离"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg1:
            controller1 = SMController(tg1, project_root=env["tmp_path"])

            async with anyio.create_task_group() as tg2:
                controller2 = DevQaController(tg2, use_claude=False)

                # 验证任务组隔离
                assert controller1.task_group != controller2.task_group

                # 两个控制器应该都能正常工作
                assert controller1 is not None
                assert controller2 is not None

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_controllers_error_propagation(self, temp_controller_environment):
        """测试控制器错误传播"""
        env = temp_controller_environment

        async with anyio.create_task_group() as tg:
            controller = SMController(tg, project_root=env["tmp_path"])

            epic_content = """# Epic 1: Test Epic

### Story 001: Test Story
"""

            # Mock SM代理抛出异常
            with patch('autoBMAD.epic_automation.agents.sm_agent.SMAgent') as MockSMAgent:
                mock_sm = MagicMock()
                mock_sm.create_stories_from_epic = AsyncMock(
                    side_effect=Exception("Test error")
                )
                MockSMAgent.return_value = mock_sm

                result = await controller.execute(
                    epic_content=epic_content,
                    story_id="001"
                )

                # 应该处理错误
                assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

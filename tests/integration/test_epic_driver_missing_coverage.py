"""
EpicDriver 补充集成测试
专门针对 epic_driver.py 中未覆盖的代码行进行测试
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import (
    EpicDriver,
    QualityGateOrchestrator,
    _convert_core_to_processing_status,
    parse_arguments,
)


@pytest.fixture
def temp_missing_coverage_environment():
    """创建针对缺失覆盖率的临时测试环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建完整的目录结构
        epic_dir = tmp_path / "docs" / "epics"
        stories_dir = tmp_path / "docs" / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建测试 epic 文件
        epic_file = epic_dir / "test-epic-missing-coverage.md"
        epic_file.write_text("""# Epic 1: Missing Coverage Test Epic

### Story 1.1: Test Story 1
### Story 1.2: Test Story 2
""", encoding='utf-8')

        # 创建故事文件
        story1 = stories_dir / "1.1-test-story.md"
        story1.write_text("""# Story 1.1: Test Story 1

**Status**: Draft

## Description
Test story for missing coverage
""", encoding='utf-8')

        story2 = stories_dir / "1.2-test-story.md"
        story2.write_text("""# Story 1.2: Test Story 2

**Status**: In Progress

## Description
Test story 2 for missing coverage
""", encoding='utf-8')

        # 创建测试代码文件
        (src_dir / "test_module.py").write_text("def test(): pass\n")
        (tests_dir / "test_test_module.py").write_text("def test_test(): pass\n")

        yield {
            "epic_file": epic_file,
            "stories": [story1, story2],
            "src_dir": src_dir,
            "tests_dir": tests_dir,
            "tmp_path": tmp_path
        }


class TestQualityGateOrchestratorMissingCoverage:
    """QualityGateOrchestrator 缺失覆盖率测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_ruff_agent_with_failure(self, temp_missing_coverage_environment):
        """测试执行 Ruff 代理 - 失败场景"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False
        )

        # 模拟 RuffAgent 失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(return_value={
                "status": "failed",
                "errors": 5
            })

            result = await orchestrator.execute_ruff_agent(str(env["src_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_ruff_agent_with_exception(self, temp_missing_coverage_environment):
        """测试执行 Ruff 代理 - 异常场景"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False
        )

        # 模拟 RuffAgent 抛出异常
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(side_effect=Exception("Test exception"))

            result = await orchestrator.execute_ruff_agent(str(env["src_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_basedpyright_agent_with_failure(self, temp_missing_coverage_environment):
        """测试执行 BasedPyright 代理 - 失败场景"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False
        )

        # 模拟 BasedPyrightAgent 失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(return_value={
                "status": "failed",
                "errors": 10
            })

            result = await orchestrator.execute_basedpyright_agent(str(env["src_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_basedpyright_agent_with_exception(self, temp_missing_coverage_environment):
        """测试执行 BasedPyright 代理 - 异常场景"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False
        )

        # 模拟 BasedPyrightAgent 抛出异常
        with patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(side_effect=Exception("Test exception"))

            result = await orchestrator.execute_basedpyright_agent(str(env["src_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_pytest_agent_with_subprocess_failure(self, temp_missing_coverage_environment):
        """测试执行 Pytest 代理 - 子进程失败场景"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_tests=False
        )

        # 模拟 subprocess.run 返回失败
        with patch('subprocess.run') as MockRun:
            MockRun.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Tests failed"
            )

            result = await orchestrator.execute_pytest_agent(str(env["tests_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_pytest_agent_no_tests(self, temp_missing_coverage_environment):
        """测试执行 Pytest 代理 - 没有测试文件"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_tests=False
        )

        # 删除测试文件
        for test_file in env["tests_dir"].glob("*.py"):
            test_file.unlink()

        result = await orchestrator.execute_pytest_agent(str(env["tests_dir"]))
        # 应该跳过，因为没有测试文件
        assert result["success"] is True
        assert result["skipped"] is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_pytest_agent_subprocess_exception(self, temp_missing_coverage_environment):
        """测试执行 Pytest 代理 - 子进程异常"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_tests=False
        )

        # 模拟 subprocess.run 抛出异常
        with patch('subprocess.run') as MockRun:
            MockRun.side_effect = Exception("Subprocess error")

            result = await orchestrator.execute_pytest_agent(str(env["tests_dir"]))
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_ruff_failure(self, temp_missing_coverage_environment):
        """测试执行质量门控 - Ruff 失败"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=True
        )

        # 模拟 Ruff 失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(return_value={
                "status": "failed",
                "errors": 5
            })

            result = await orchestrator.execute_quality_gates("test-epic")
            assert result["success"] is False
            assert len(result["errors"]) > 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_basedpyright_failure(self, temp_missing_coverage_environment):
        """测试执行质量门控 - BasedPyright 失败"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=True
        )

        # 模拟 Ruff 成功，BasedPyright 失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuffAgent, \
             patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockBasedPyrightAgent:
            mock_ruff = MockRuffAgent.return_value
            mock_ruff.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0
            })

            mock_basedpyright = MockBasedPyrightAgent.return_value
            mock_basedpyright.execute = AsyncMock(return_value={
                "status": "failed",
                "errors": 10
            })

            result = await orchestrator.execute_quality_gates("test-epic")
            assert result["success"] is False
            assert len(result["errors"]) > 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_exception(self, temp_missing_coverage_environment):
        """测试执行质量门控 - 异常"""
        env = temp_missing_coverage_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=True
        )

        # 模拟 Ruff 抛出异常
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_instance = MockAgent.return_value
            mock_instance.execute = AsyncMock(side_effect=Exception("Test exception"))

            result = await orchestrator.execute_quality_gates("test-epic")
            # 质量门控错误是非阻塞的，所以返回 True
            assert result["success"] is False
            assert len(result["errors"]) > 0


class TestEpicDriverMissingCoverage:
    """EpicDriver 缺失覆盖率测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_epic_with_exception(self, temp_missing_coverage_environment):
        """测试解析 Epic - 异常场景"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟读取文件时抛出异常
        with patch('builtins.open', side_effect=IOError("Test error")):
            stories = await driver.parse_epic()
            assert len(stories) == 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_extract_story_ids_edge_cases(self, temp_missing_coverage_environment):
        """测试提取故事 ID - 边界情况"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试空内容
        story_ids = driver._extract_story_ids_from_epic("")
        assert len(story_ids) == 0

        # 测试只有标题的内容
        content = """# Epic 1
## Story 1.1
"""
        story_ids = driver._extract_story_ids_from_epic(content)
        assert len(story_ids) == 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_find_story_file_edge_cases(self, temp_missing_coverage_environment):
        """测试查找故事文件 - 边界情况"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试不存在的目录
        result = driver._find_story_file_with_fallback(
            Path("/nonexistent/path"), "1.1"
        )
        assert result is None

        # 测试空故事目录
        empty_dir = env["tmp_path"] / "empty"
        empty_dir.mkdir()
        result = driver._find_story_file_with_fallback(empty_dir, "1.1")
        assert result is None

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_sm_phase_with_exception(self, temp_missing_coverage_environment):
        """测试执行 SM 阶段 - 异常场景"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 SMController 抛出异常
        with patch('autoBMAD.epic_automation.controllers.sm_controller.SMController') as MockController:
            mock_instance = MockController.return_value
            mock_instance.execute = AsyncMock(side_effect=Exception("Test exception"))

            result = await driver.execute_sm_phase(str(env["stories"][0]))
            assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_phase_max_iterations_exceeded(self, temp_missing_coverage_environment):
        """测试执行 Dev 阶段 - 超过最大迭代次数"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            max_iterations=2
        )

        # 模拟状态管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=True)

        # 尝试超过 max_iterations 的迭代
        result = await driver.execute_dev_phase(str(env["stories"][0]), iteration=5)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_phase_with_exception(self, temp_missing_coverage_environment):
        """测试执行 Dev 阶段 - 异常场景"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 DevQaController 抛出异常
        with patch('autoBMAD.epic_automation.controllers.devqa_controller.DevQaController') as MockController:
            mock_instance = MockController.return_value
            mock_instance.execute = AsyncMock(side_effect=Exception("Test exception"))

            result = await driver.execute_dev_phase(str(env["stories"][0]), iteration=1)
            assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_runtime_error(self, temp_missing_coverage_environment):
        """测试处理故事 - RuntimeError"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 _process_story_impl 抛出 RuntimeError
        driver._process_story_impl = AsyncMock(side_effect=RuntimeError("Test error"))

        story = {
            "id": "1.1",
            "path": str(env["stories"][0]),
            "name": "1.1-test-story.md",
            "status": "Draft"
        }

        result = await driver.process_story(story)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_cancel_scope_error(self, temp_missing_coverage_environment):
        """测试处理故事 - Cancel Scope 错误"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 _process_story_impl 抛出 cancel scope 错误
        driver._process_story_impl = AsyncMock(
            side_effect=RuntimeError("cancel scope in a different task")
        )

        story = {
            "id": "1.1",
            "path": str(env["stories"][0]),
            "name": "1.1-test-story.md",
            "status": "Draft"
        }

        result = await driver.process_story(story)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_story_processing_with_cancelled_error(self, temp_missing_coverage_environment):
        """测试执行故事处理 - CancelledError"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟状态管理器
        driver.state_manager.get_story_status = AsyncMock(return_value=None)
        driver.state_manager.update_story_status = AsyncMock(return_value=True)

        # 模拟 _parse_story_status 抛出 CancelledError
        driver._parse_story_status = AsyncMock(side_effect=asyncio.CancelledError())

        story = {
            "id": "1.1",
            "path": str(env["stories"][0]),
            "name": "1.1-test-story.md",
            "status": "Draft"
        }

        # 应该能够处理 CancelledError 并使用 fallback
        result = await driver._execute_story_processing(story)
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_story_status_with_exception(self, temp_missing_coverage_environment):
        """测试解析故事状态 - 异常"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟打开文件时抛出异常
        with patch('builtins.open', side_effect=IOError("Test error")):
            status = await driver._parse_story_status(str(env["stories"][0]))
            # 应该返回默认值
            assert status == "Draft"

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_story_status_fallback_with_invalid_file(self, temp_missing_coverage_environment):
        """测试解析故事状态 fallback - 无效文件"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试不存在的文件
        status = driver._parse_story_status_fallback("/nonexistent/file.md")
        assert status == "ready_for_development"

        # 测试空文件
        empty_file = env["tmp_path"] / "empty.md"
        empty_file.write_text("", encoding='utf-8')
        status = driver._parse_story_status_fallback(str(empty_file))
        assert status == "ready_for_development"

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_is_story_ready_for_done_with_exception(self, temp_missing_coverage_environment):
        """测试检查故事是否准备完成 - 异常"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 _parse_story_status 抛出异常
        driver._parse_story_status = AsyncMock(side_effect=Exception("Test error"))

        result = await driver._is_story_ready_for_done(str(env["stories"][0]))
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_check_state_consistency_with_missing_path(self, temp_missing_coverage_environment):
        """测试检查状态一致性 - 缺失路径"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = await driver._check_state_consistency({})
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_validate_story_integrity_with_missing_path(self, temp_missing_coverage_environment):
        """测试验证故事完整性 - 缺失路径"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = await driver._validate_story_integrity({})
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_validate_story_integrity_with_nonexistent_file(self, temp_missing_coverage_environment):
        """测试验证故事完整性 - 不存在的文件"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = await driver._validate_story_integrity({
            "path": "/nonexistent/file.md"
        })
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_validate_story_integrity_with_short_content(self, temp_missing_coverage_environment):
        """测试验证故事完整性 - 内容过短"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        short_file = env["tmp_path"] / "short.md"
        short_file.write_text("Short", encoding='utf-8')

        result = await driver._validate_story_integrity({
            "path": str(short_file)
        })
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_resync_story_state_with_missing_path(self, temp_missing_coverage_environment):
        """测试重新同步故事状态 - 缺失路径"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        await driver._resync_story_state({})
        # 应该没有异常

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_handle_graceful_cancellation_with_missing_path(self, temp_missing_coverage_environment):
        """测试优雅取消 - 缺失路径"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        await driver._handle_graceful_cancellation({})
        # 应该没有异常

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_cancellation(self, temp_missing_coverage_environment):
        """测试执行 Dev-QA 循环 - 取消场景"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 process_story 抛出 CancelledError
        driver.process_story = AsyncMock(side_effect=asyncio.CancelledError())

        stories = [{"id": "1.1", "path": str(env["stories"][0])}]

        result = await driver.execute_dev_qa_cycle(stories)
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_runtime_error(self, temp_missing_coverage_environment):
        """测试执行 Dev-QA 循环 - RuntimeError"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 process_story 抛出 RuntimeError
        driver.process_story = AsyncMock(side_effect=RuntimeError("Test error"))

        stories = [{"id": "1.1", "path": str(env["stories"][0])}]

        result = await driver.execute_dev_qa_cycle(stories)
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_cancel_scope_error(self, temp_missing_coverage_environment):
        """测试执行 Dev-QA 循环 - Cancel Scope 错误"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 process_story 抛出 cancel scope 错误
        driver.process_story = AsyncMock(
            side_effect=RuntimeError("cancel scope in a different task")
        )

        stories = [{"id": "1.1", "path": str(env["stories"][0])}]

        result = await driver.execute_dev_qa_cycle(stories)
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_no_stories(self, temp_missing_coverage_environment):
        """测试运行 - 没有故事"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 返回空列表
        driver.parse_epic = AsyncMock(return_value=[])

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_phase_gate_failure(self, temp_missing_coverage_environment):
        """测试运行 - 阶段门控失败"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 返回故事
        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0]), "status": "Draft"}
        ])

        # 模拟 _validate_phase_gates 返回 False
        driver._validate_phase_gates = Mock(return_value=False)

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_dev_qa_failure(self, temp_missing_coverage_environment):
        """测试运行 - Dev-QA 失败"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 返回故事
        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0]), "status": "Draft"}
        ])

        # 模拟 execute_dev_qa_cycle 返回 False
        driver.execute_dev_qa_cycle = AsyncMock(return_value=False)

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_exception(self, temp_missing_coverage_environment):
        """测试运行 - 异常"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 抛出异常
        driver.parse_epic = AsyncMock(side_effect=Exception("Test exception"))

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_cancellation(self, temp_missing_coverage_environment):
        """测试运行 - 取消"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 抛出 CancelledError
        driver.parse_epic = AsyncMock(side_effect=asyncio.CancelledError())

        with pytest.raises(asyncio.CancelledError):
            await driver.run()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_exception(self, temp_missing_coverage_environment):
        """测试执行质量门控 - 异常"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 QualityGateOrchestrator 抛出异常
        with patch('autoBMAD.epic_automation.epic_driver.QualityGateOrchestrator') as MockOrchestrator:
            mock_instance = MockOrchestrator.return_value
            mock_instance.execute_quality_gates = AsyncMock(
                side_effect=Exception("Test exception")
            )

            result = await driver.execute_quality_gates()
            assert result is True  # 质量门控错误是非阻塞的

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_sync_story_statuses_error(self, temp_missing_coverage_environment):
        """测试同步故事状态 - 错误"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟 parse_epic 返回故事
        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0]), "status": "Draft"}
        ])

        # 模拟 execute_dev_qa_cycle 返回 True
        driver.execute_dev_qa_cycle = AsyncMock(return_value=True)

        # 模拟 execute_quality_gates 返回 True
        driver.execute_quality_gates = AsyncMock(return_value=True)

        # 模拟 sync_story_statuses_to_markdown 返回错误
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(
            return_value={"success_count": 0, "error_count": 1}
        )

        result = await driver.run()
        assert result is True  # 同步错误不应该影响整体结果

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_log_manager_cleanup(self, temp_missing_coverage_environment):
        """测试运行 - 日志管理器清理"""
        env = temp_missing_coverage_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 模拟所有方法
        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0]), "status": "Draft"}
        ])
        driver.execute_dev_qa_cycle = AsyncMock(return_value=True)
        driver.execute_quality_gates = AsyncMock(return_value=True)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(
            return_value={"success_count": 1, "error_count": 0}
        )

        # 模拟 log_manager 清理时抛出异常
        driver.log_manager.flush = Mock(side_effect=Exception("Cleanup error"))

        result = await driver.run()
        assert result is True


class TestMainFunction:
    """主函数测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_with_keyboard_interrupt(self):
        """测试主函数 - 键盘中断"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as MockParse, \
             patch('autoBMAD.epic_automation.EpicDriver') as MockDriver, \
             patch('asyncio.run') as MockRun:

            MockParse.return_value = Mock(
                epic_path="test.epic",
                max_iterations=3,
                retry_failed=False,
                verbose=False,
                concurrent=False,
                no_claude=False,
                source_dir="src",
                test_dir="tests",
                skip_quality=False,
                skip_tests=False
            )

            mock_driver_instance = MockDriver.return_value
            mock_driver_instance.run = AsyncMock(side_effect=KeyboardInterrupt())

            from autoBMAD.epic_automation.epic_driver import main

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 130

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_with_cancelled_error(self):
        """测试主函数 - 取消错误"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as MockParse, \
             patch('autoBMAD.epic_automation.EpicDriver') as MockDriver, \
             patch('asyncio.run') as MockRun:

            MockParse.return_value = Mock(
                epic_path="test.epic",
                max_iterations=3,
                retry_failed=False,
                verbose=False,
                concurrent=False,
                no_claude=False,
                source_dir="src",
                test_dir="tests",
                skip_quality=False,
                skip_tests=False
            )

            mock_driver_instance = MockDriver.return_value
            mock_driver_instance.run = AsyncMock(side_effect=asyncio.CancelledError())

            from autoBMAD.epic_automation.epic_driver import main

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_with_cancel_scope_error(self):
        """测试主函数 - Cancel Scope 错误"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as MockParse, \
             patch('autoBMAD.epic_automation.EpicDriver') as MockDriver, \
             patch('asyncio.run') as MockRun:

            MockParse.return_value = Mock(
                epic_path="test.epic",
                max_iterations=3,
                retry_failed=False,
                verbose=False,
                concurrent=False,
                no_claude=False,
                source_dir="src",
                test_dir="tests",
                skip_quality=False,
                skip_tests=False
            )

            mock_driver_instance = MockDriver.return_value
            mock_driver_instance.run = AsyncMock(side_effect=RuntimeError("cancel scope error"))

            from autoBMAD.epic_automation.epic_driver import main

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_with_unexpected_error(self):
        """测试主函数 - 意外错误"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as MockParse, \
             patch('autoBMAD.epic_automation.EpicDriver') as MockDriver, \
             patch('asyncio.run') as MockRun:

            MockParse.return_value = Mock(
                epic_path="test.epic",
                max_iterations=3,
                retry_failed=False,
                verbose=False,
                concurrent=False,
                no_claude=False,
                source_dir="src",
                test_dir="tests",
                skip_quality=False,
                skip_tests=False
            )

            mock_driver_instance = MockDriver.return_value
            mock_driver_instance.run = AsyncMock(side_effect=RuntimeError("Unexpected error"))

            from autoBMAD.epic_automation.epic_driver import main

            with pytest.raises(SystemExit) as exc_info:
                await main()

            assert exc_info.value.code == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

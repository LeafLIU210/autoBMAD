"""
EpicDriver 核心集成测试
覆盖 EpicDriver 的关键方法，确保高覆盖率
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver, QualityGateOrchestrator


@pytest.fixture
def temp_epic_environment():
    """创建临时 Epic 环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        epic_dir = tmp_path / "docs" / "epics"
        stories_dir = tmp_path / "docs" / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        epic_file = epic_dir / "test-epic.md"
        epic_file.write_text("""# Epic 1: Test Epic

### Story 1.1: Test Story 1
### Story 1.2: Test Story 2
""", encoding='utf-8')

        story1 = stories_dir / "1.1-test-story-1.md"
        story1.write_text("""# Story 1.1: Test Story 1

**Status**: Draft

## Description
Test story
""", encoding='utf-8')

        story2 = stories_dir / "1.2-test-story-2.md"
        story2.write_text("""# Story 1.2: Test Story 2

**Status**: Done

## Description
Test story
""", encoding='utf-8')

        (src_dir / "test.py").write_text("def hello(): pass\n")
        (tests_dir / "test_test.py").write_text("def test_hello(): pass\n")

        yield {
            "epic_file": epic_file,
            "stories": [story1, story2],
            "src_dir": src_dir,
            "tests_dir": tests_dir
        }


class TestEpicDriverCore:
    """核心功能测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_epic_driver_initialization(self, temp_epic_environment):
        """测试 EpicDriver 初始化"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        assert driver.epic_path == env["epic_file"]
        assert driver.use_claude is False
        assert driver.skip_quality is True
        assert driver.skip_tests is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_epic(self, temp_epic_environment):
        """测试 Epic 解析"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        stories = await driver.parse_epic()

        assert len(stories) >= 1
        assert all("id" in story for story in stories)
        assert all("path" in story for story in stories)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_extract_story_ids(self, temp_epic_environment):
        """测试故事 ID 提取"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        content = """# Epic 1

### Story 1.1: Title 1
### Story 1.2: Title 2
"""
        story_ids = driver._extract_story_ids_from_epic(content)

        assert len(story_ids) >= 2
        assert any("1.1" in sid for sid in story_ids)
        assert any("1.2" in sid for sid in story_ids)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_find_story_file(self, temp_epic_environment):
        """测试故事文件查找"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = driver._find_story_file_with_fallback(
            env["stories"][0].parent, "1.1"
        )

        assert result is not None
        assert "1.1" in result.name

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_status_parsing_sync(self, temp_epic_environment):
        """测试状态同步解析"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        status = driver._parse_story_status_sync(str(env["stories"][0]))
        assert status is not None

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_status_parsing_async(self, temp_epic_environment):
        """测试状态异步解析"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver.status_parser = MagicMock()
        driver.status_parser.parse_status = AsyncMock(return_value="Done")

        status = await driver._parse_story_status(str(env["stories"][0]))
        assert status == "Done"

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_status_parsing_fallback(self, temp_epic_environment):
        """测试状态解析 fallback"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        status = driver._parse_story_status_fallback(str(env["stories"][0]))
        assert status is not None

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_is_ready_for_done(self, temp_epic_environment):
        """测试完成检查"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver._parse_story_status = AsyncMock(return_value="Done")

        result = await driver._is_story_ready_for_done(str(env["stories"][0]))
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_state_consistency(self, temp_epic_environment):
        """测试状态一致性"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0])}
        driver.state_manager.get_story_status = AsyncMock(return_value={"status": "completed"})

        result = await driver._check_state_consistency(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_filesystem_state(self, temp_epic_environment):
        """测试文件系统状态"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0]), "expected_files": ["src", "tests"]}

        result = await driver._check_filesystem_state(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_story_integrity(self, temp_epic_environment):
        """测试故事完整性"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0])}

        result = await driver._validate_story_integrity(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_resync_state(self, temp_epic_environment):
        """测试状态重同步"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0]), "expected_status": "completed"}
        driver.state_manager.update_story_status = AsyncMock(return_value=True)
        driver.log_manager = MagicMock()

        await driver._resync_story_state(story)

        driver.state_manager.update_story_status.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_handle_cancellation(self, temp_epic_environment):
        """测试取消处理"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0])}
        driver.state_manager.update_story_status = AsyncMock(return_value=True)
        driver.log_manager = MagicMock()

        await driver._handle_graceful_cancellation(story)

        driver.state_manager.update_story_status.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_sm_phase(self, temp_epic_environment):
        """测试 SM 阶段执行"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        with patch('autoBMAD.epic_automation.controllers.sm_controller.SMController') as MockCtrl:
            mock_ctrl = AsyncMock()
            mock_ctrl.execute = AsyncMock(return_value=True)
            MockCtrl.return_value = mock_ctrl

            driver.state_manager.update_story_status = AsyncMock(return_value=True)
            driver.state_manager.get_story_status = AsyncMock(return_value=None)

            result = await driver.execute_sm_phase(str(env["stories"][0]))

            assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_phase(self, temp_epic_environment):
        """测试 Dev 阶段执行"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        with patch('autoBMAD.epic_automation.controllers.devqa_controller.DevQaController') as MockCtrl:
            mock_ctrl = AsyncMock()
            mock_ctrl.execute = AsyncMock(return_value=True)
            MockCtrl.return_value = mock_ctrl

            driver.state_manager.update_story_status = AsyncMock(return_value=True)
            driver.state_manager.get_story_status = AsyncMock(return_value=None)

            result = await driver.execute_dev_phase(str(env["stories"][0]), iteration=1)

            assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_qa_phase(self, temp_epic_environment):
        """测试 QA 阶段执行（已弃用）"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = await driver.execute_qa_phase(str(env["stories"][0]))
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_basic(self, temp_epic_environment):
        """测试故事处理基本流程"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}
        driver._process_story_impl = AsyncMock(return_value=True)

        result = await driver.process_story(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_cancellation(self, temp_epic_environment):
        """测试故事处理中的取消"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}
        driver._process_story_impl = AsyncMock(
            side_effect=RuntimeError("cancel scope in different task")
        )

        result = await driver.process_story(story)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_story_processing(self, temp_epic_environment):
        """测试故事处理循环"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}
        driver._parse_story_status = AsyncMock(return_value="Done")
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)
        driver.state_manager.get_story_status = AsyncMock(return_value=None)

        result = await driver._execute_story_processing(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle(self, temp_epic_environment):
        """测试 Dev-QA 循环"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        driver.process_story = AsyncMock(return_value=True)

        stories = [
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ]

        result = await driver.execute_dev_qa_cycle(stories)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_failures(self, temp_epic_environment):
        """测试 Dev-QA 循环中的失败"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            retry_failed=False,
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        call_count = 0
        async def mock_process_story(story):
            nonlocal call_count
            call_count += 1
            return call_count == 1

        driver.process_story = mock_process_story

        stories = [
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ]

        result = await driver.execute_dev_qa_cycle(stories)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_cancellation(self, temp_epic_environment):
        """测试 Dev-QA 循环中的取消"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        call_count = 0
        async def mock_process_story(story):
            nonlocal call_count
            call_count += 1
            # 第一次抛出取消，第二次成功
            if call_count == 1:
                raise asyncio.CancelledError("Cancelled")
            return True

        driver.process_story = mock_process_story

        stories = [
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ]

        result = await driver.execute_dev_qa_cycle(stories)
        # 由于第一个故事被取消，只有第二个成功，所以整体返回False
        assert result is False
        assert call_count == 2

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_basic(self, temp_epic_environment):
        """测试基本运行流程"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        driver.parse_epic = AsyncMock(return_value=[{"id": "1.1", "path": str(env["stories"][0])}])
        driver.execute_dev_qa_cycle = AsyncMock(return_value=True)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 1,
            "error_count": 0
        })

        result = await driver.run()
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_no_stories(self, temp_epic_environment):
        """测试无故事情况"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver.parse_epic = AsyncMock(return_value=[])

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_dev_qa_failure(self, temp_epic_environment):
        """测试 Dev-QA 失败"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        driver.parse_epic = AsyncMock(return_value=[{"id": "1.1", "path": str(env["stories"][0])}])
        driver.execute_dev_qa_cycle = AsyncMock(return_value=False)

        result = await driver.run()
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_quality_gates(self, temp_epic_environment):
        """测试带质量门控的运行"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=False,
            skip_tests=True
        )

        driver.parse_epic = AsyncMock(return_value=[{"id": "1.1", "path": str(env["stories"][0])}])
        driver.execute_dev_qa_cycle = AsyncMock(return_value=True)
        driver.execute_quality_gates = AsyncMock(return_value=True)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 1,
            "error_count": 0
        })

        result = await driver.run()
        assert result is True
        driver.execute_quality_gates.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_cancellation(self, temp_epic_environment):
        """测试运行取消"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver.parse_epic = AsyncMock(side_effect=asyncio.CancelledError("Cancelled"))

        with pytest.raises(asyncio.CancelledError):
            await driver.run()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_exception(self, temp_epic_environment):
        """测试运行异常"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver.parse_epic = AsyncMock(side_effect=Exception("Test error"))

        result = await driver.run()
        assert result is False


class TestQualityGateOrchestrator:
    """质量门控测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_init(self, temp_epic_environment):
        """测试质量门控初始化"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=True,
            skip_tests=True
        )

        assert orchestrator.source_dir == str(env["src_dir"])
        assert orchestrator.skip_quality is True
        assert orchestrator.skip_tests is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_ruff(self, temp_epic_environment):
        """测试 Ruff 执行"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=True
        )

        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockAgent.return_value = mock_agent

            result = await orchestrator.execute_ruff_agent(str(env["src_dir"]))
            assert result["success"] is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_basedpyright(self, temp_epic_environment):
        """测试 BasedPyright 执行"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=True
        )

        with patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockAgent:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockAgent.return_value = mock_agent

            result = await orchestrator.execute_basedpyright_agent(str(env["src_dir"]))
            assert result["success"] is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_pytest(self, temp_epic_environment):
        """测试 Pytest 执行"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=True,
            skip_tests=False
        )

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = await orchestrator.execute_pytest_agent(str(env["tests_dir"]))
            assert result["success"] is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_pytest_no_tests(self, temp_epic_environment):
        """测试 Pytest 执行 - 无测试"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["src_dir"]),
            skip_quality=True,
            skip_tests=False
        )

        result = await orchestrator.execute_pytest_agent(str(env["src_dir"]))
        assert result["success"] is True
        assert result.get("skipped") is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_execute_gates(self, temp_epic_environment):
        """测试完整质量门控执行"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=True,
            skip_tests=True
        )

        result = await orchestrator.execute_quality_gates("test-epic")

        assert "success" in result
        assert "errors" in result
        assert "total_duration" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_finalize(self, temp_epic_environment):
        """测试结果最终化"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"])
        )

        # 测试_duration计算方法
        duration = orchestrator._calculate_duration(1000.0, 1100.0)

        assert duration == 100.0
        assert isinstance(duration, float)

        # 测试_finalize_results的其他逻辑（不依赖时间）
        # 先设置一些测试数据
        orchestrator.results["errors"] = []  # 无错误
        orchestrator.results["success"] = True

        # 调用_finalize_results（会设置当前时间为end_time）
        result = orchestrator._finalize_results()

        # 验证返回结构
        assert "success" in result
        assert "errors" in result
        assert "total_duration" in result
        # 由于我们没有设置start_time，duration应该是0.0
        assert result["success"] is True
        assert len(result["errors"]) == 0


class TestUtilityFunctions:
    """工具函数测试"""

    @pytest.mark.integration
    def test_extract_epic_prefix(self, temp_epic_environment):
        """测试 epic 前缀提取"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        assert driver._extract_epic_prefix("epic-004-test.md") == "004"
        assert driver._extract_epic_prefix("no-prefix.md") == ""

    @pytest.mark.integration
    def test_convert_windows_path(self, temp_epic_environment):
        """测试 Windows 路径转换"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        unix_path = "/d/GITHUB/pytQt_template/test.md"
        windows_path = driver._convert_to_windows_path(unix_path)
        assert "D:" in windows_path

        normal_path = "docs/test.md"
        converted = driver._convert_to_windows_path(normal_path)
        assert "\\" in converted

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_progress(self, temp_epic_environment):
        """测试进度更新"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        await driver._update_progress("dev_qa", "in_progress", {"test": "data"})

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_initialize_epic(self, temp_epic_environment):
        """测试 epic 初始化"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        await driver._initialize_epic_processing(3)

    @pytest.mark.integration
    def test_generate_report(self, temp_epic_environment):
        """测试报告生成"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        report = driver._generate_final_report()

        assert "epic_id" in report
        assert "status" in report
        assert "phases" in report

    @pytest.mark.integration
    def test_validate_phase_gates(self, temp_epic_environment):
        """测试阶段门控验证"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = driver._validate_phase_gates()
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

@pytest.mark.integration
def test_parse_arguments():
    """测试命令行参数解析"""
    from autoBMAD.epic_automation.epic_driver import parse_arguments
    import sys
    from unittest.mock import patch
    
    # 测试基本参数解析
    with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md']):
        args = parse_arguments()
        assert args.epic_path == 'test.epic.md'
    
    # 测试带可选参数的解析
    with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md', '--max-iterations', '5']):
        args = parse_arguments()
        assert args.max_iterations == 5


@pytest.mark.integration
def test_convert_core_to_processing_status_utility():
    """测试状态转换工具函数"""
    from autoBMAD.epic_automation.epic_driver import _convert_core_to_processing_status

    # 测试各种状态转换
    # SM阶段：pending状态表示SM已完成，返回completed
    assert _convert_core_to_processing_status('Draft', 'sm') == 'completed'
    # Dev阶段：pending状态转换为in_progress
    assert _convert_core_to_processing_status('Ready for Development', 'dev') == 'in_progress'
    # QA阶段：review状态已完成
    assert _convert_core_to_processing_status('Ready for Review', 'qa') == 'completed'
    # QA阶段：completed状态保持
    assert _convert_core_to_processing_status('Done', 'qa') == 'completed'


@pytest.mark.integration
def test_quality_gate_orchestrator_calculate_duration():
    """测试质量门控持续时间计算"""
    from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        orchestrator = QualityGateOrchestrator(
            source_dir=str(Path(tmp_dir) / "src"),
            test_dir=str(Path(tmp_dir) / "tests")
        )
        
        duration = orchestrator._calculate_duration(1000.0, 1100.0)
        assert duration == 100.0
        assert isinstance(duration, float)


@pytest.mark.integration
def test_quality_gate_orchestrator_update_progress():
    """测试质量门控进度更新"""
    from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        orchestrator = QualityGateOrchestrator(
            source_dir=str(Path(tmp_dir) / "src"),
            test_dir=str(Path(tmp_dir) / "tests")
        )
        
        # 测试进度更新
        orchestrator._update_progress("phase_1_ruff", "in_progress", start=True)
        
        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "in_progress"


@pytest.mark.integration
@pytest.mark.anyio
async def test_quality_gate_orchestrator_error_handling():
    """测试质量门控错误处理"""
    from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator
    import tempfile
    from pathlib import Path
    from unittest.mock import patch, MagicMock

    with tempfile.TemporaryDirectory() as tmp_dir:
        orchestrator = QualityGateOrchestrator(
            source_dir=str(Path(tmp_dir) / "src"),
            test_dir=str(Path(tmp_dir) / "tests"),
            skip_quality=False,
            skip_tests=False
        )

        # Mock RuffAgent 抛出异常
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
            mock_agent = MagicMock()
            mock_agent.execute = MagicMock(side_effect=Exception("Test error"))
            MockAgent.return_value = mock_agent

            result = await orchestrator.execute_ruff_agent(str(Path(tmp_dir) / "src"))

            # 应该返回失败结果
            assert result["success"] is False
            assert "error" in result


@pytest.mark.integration
def test_main_function_exists():
    """测试 main 函数存在性"""
    from autoBMAD.epic_automation import epic_driver
    assert hasattr(epic_driver, 'main')


@pytest.mark.integration
def test_global_exception_handler_exists():
    """测试全局异常处理器存在性"""
    from autoBMAD.epic_automation import epic_driver
    # 检查是否定义了全局异常处理器
    import inspect
    source = inspect.getsource(epic_driver)
    assert 'global_exception_handler' in source or 'exception_handler' in source

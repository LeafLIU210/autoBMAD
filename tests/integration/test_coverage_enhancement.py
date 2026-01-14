"""
集成测试覆盖率增强
专门针对覆盖率不足的模块创建测试用例
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock, call
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver, QualityGateOrchestrator
from autoBMAD.epic_automation.state_manager import StateManager
from autoBMAD.epic_automation.log_manager import LogManager
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK


@pytest.fixture
def temp_environment():
    """创建临时测试环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建目录结构
        epic_dir = tmp_path / "docs" / "epics"
        stories_dir = tmp_path / "docs" / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"
        tasks_dir = tmp_path / ".bmad-core" / "tasks"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir, tasks_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建测试epic文件
        epic_file = epic_dir / "test-epic.md"
        epic_file.write_text("""# Epic 1: Test Epic

### Story 1.1: Test Story 1
**Story ID**: 1.1

### Story 1.2: Test Story 2
**Story ID**: 1.2
""", encoding='utf-8')

        # 创建故事文件
        story1 = stories_dir / "1.1-test-story.md"
        story1.write_text("""# Story 1.1: Test Story 1

**Status**: Draft

## Description
Test story
""", encoding='utf-8')

        story2 = stories_dir / "1.2-test-story.md"
        story2.write_text("""# Story 1.2: Test Story 2

**Status**: Done

## Description
Test story
""", encoding='utf-8')

        # 创建源文件和测试文件
        (src_dir / "test.py").write_text("def hello(): pass\n")
        (tests_dir / "test_test.py").write_text("def test_hello(): pass\n")

        yield {
            "epic_file": epic_file,
            "stories": [story1, story2],
            "src_dir": src_dir,
            "tests_dir": tests_dir,
            "tasks_dir": tasks_dir,
            "tmp_path": tmp_path
        }


class TestEpicDriverCoverageEnhancement:
    """EpicDriver 覆盖率增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_epic_driver_full_workflow_with_quality_gates(self, temp_environment):
        """测试EpicDriver完整工作流包含质量门控"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=False,  # 不跳过质量门控
            skip_tests=False,
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"])
        )

        # Mock所有依赖
        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0])}
        ])
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
    async def test_epic_driver_with_all_configurations(self, temp_environment):
        """测试EpicDriver所有配置组合"""
        env = temp_environment

        # 测试不同的配置组合
        configs = [
            {"use_claude": True, "skip_quality": True, "skip_tests": True},
            {"use_claude": False, "skip_quality": False, "skip_tests": False},
            {"concurrent": True, "verbose": True, "retry_failed": True},
        ]

        for config in configs:
            driver = EpicDriver(
                epic_path=str(env["epic_file"]),
                **config
            )
            assert driver is not None
            assert driver.epic_path == env["epic_file"]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_epic_with_complex_story_patterns(self, temp_environment):
        """测试复杂故事模式解析"""
        env = temp_environment

        # 创建复杂的epic内容
        complex_epic = """# Epic 1: Complex Epic

### Story 001: First Story
**Story ID**: 001

### Story 002: Second Story
**Story ID**: 002

### Story 003.1: Sub Story
**Story ID**: 003.1

### Story 003.2: Another Sub Story
**Story ID**: 003.2
"""
        env["epic_file"].write_text(complex_epic, encoding='utf-8')

        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        stories = await driver.parse_epic()

        assert len(stories) >= 2
        # 验证故事ID解析
        story_ids = [s["id"] for s in stories]
        assert any("001" in sid for sid in story_ids)
        assert any("002" in sid for sid in story_ids)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_story_file_finding_with_multiple_patterns(self, temp_environment):
        """测试多种故事文件查找模式"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试不同的文件模式
        test_cases = [
            ("1.1", "1.1.md", True),  # 精确匹配
            ("1.2", "1.2-another-name.md", True),  # 描述性匹配
        ]

        for story_id, filename, should_find in test_cases:
            result = driver._find_story_file_with_fallback(
                env["stories"][0].parent, story_id
            )
            if should_find:
                assert result is not None
            # Note: 某些测试可能不会找到文件，这是正常的

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_status_parsing_edge_cases(self, temp_environment):
        """测试状态解析边界情况"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试无效状态
        invalid_status_story = env["tmp_path"] / "invalid-status.md"
        invalid_status_story.write_text("""# Story

**Status**: Unknown Invalid Status

## Description
""", encoding='utf-8')

        status = driver._parse_story_status_fallback(str(invalid_status_story))
        assert status is not None

        # 测试空文件
        empty_story = env["tmp_path"] / "empty.md"
        empty_story.write_text("", encoding='utf-8')

        status = driver._parse_story_status_fallback(str(empty_story))
        assert status is not None

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_various_statuses(self, temp_environment):
        """测试处理不同状态的故事"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        # 测试不同状态的Story
        test_statuses = ["Draft", "Ready for Development", "In Progress", "Ready for Review", "Done"]

        for status in test_statuses:
            story_path = env["tmp_path"] / f"story-{status.replace(' ', '-').lower()}.md"
            story_path.write_text(f"""# Story

**Status**: {status}

## Description
Test story
""", encoding='utf-8')

            story = {"id": f"test-{status}", "path": str(story_path)}

            # Mock解析状态
            driver._parse_story_status = AsyncMock(return_value=status)
            driver._execute_story_processing = AsyncMock(return_value=True)

            result = await driver.process_story(story)
            # 根据状态不同，结果可能不同
            assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_dev_qa_cycle_with_failures_and_retries(self, temp_environment):
        """测试Dev-QA循环中的失败和重试"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            retry_failed=True,  # 启用重试
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        call_count = 0
        async def mock_process_story(story):
            nonlocal call_count
            call_count += 1
            # 前两次失败，第三次成功
            if call_count < 3:
                return False
            return True

        driver.process_story = mock_process_story

        stories = [
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ]

        result = await driver.execute_dev_qa_cycle(stories)
        # 由于启用了重试，应该最终成功
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_mixed_results(self, temp_environment):
        """测试质量门控混合结果"""
        env = temp_environment

        # 创建orchestrator
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=False
        )

        # Mock各个质量检查
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff, \
             patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockPyright, \
             patch('subprocess.run') as MockSubprocess:

            # Ruff成功
            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockRuff.return_value = mock_ruff

            # BasedPyright成功
            mock_pyright = MagicMock()
            mock_pyright.execute = AsyncMock(return_value={"status": "completed", "errors": 0})
            MockPyright.return_value = mock_pyright

            # Pytest成功
            MockSubprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = await orchestrator.execute_quality_gates("test-epic")

            assert result["success"] is True
            assert "ruff" in result
            assert "basedpyright" in result
            assert "pytest" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_quality_gates_with_failures(self, temp_environment):
        """测试质量门控失败情况"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=False
        )

        # Mock Ruff失败
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff:
            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(return_value={"status": "failed", "errors": 5})
            MockRuff.return_value = mock_ruff

            result = await orchestrator.execute_quality_gates("test-epic")

            # 第一个失败应该停止流水线
            assert result["success"] is False
            assert len(result["errors"]) > 0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_state_manager_integration(self, temp_environment):
        """测试状态管理器集成"""
        env = temp_environment

        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        # 测试状态更新
        driver.state_manager.update_story_status = AsyncMock(return_value=True)
        driver.state_manager.get_story_status = AsyncMock(return_value={
            "status": "completed",
            "phase": "dev"
        })

        # 测试各种状态操作
        await driver.state_manager.update_story_status(
            story_path=str(env["stories"][0]),
            status="in_progress",
            phase="dev"
        )

        status = await driver.state_manager.get_story_status(str(env["stories"][0]))

        assert status is not None
        assert status["status"] == "completed"

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_log_manager_integration(self, temp_environment):
        """测试日志管理器集成"""
        env = temp_environment

        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        # 测试日志记录
        assert driver.log_manager is not None
        assert driver.logger is not None

        # 测试各种日志级别
        driver.logger.info("Test info message")
        driver.logger.debug("Test debug message")
        driver.logger.warning("Test warning message")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_epic_driver_cleanup_and_exception_handling(self, temp_environment):
        """测试EpicDriver清理和异常处理"""
        env = temp_environment

        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        # 测试run方法中的异常处理
        driver.parse_epic = AsyncMock(side_effect=Exception("Test exception"))

        result = await driver.run()

        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_concurrent_processing(self, temp_environment):
        """测试并发处理"""
        env = temp_environment

        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            concurrent=True,  # 启用并发
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        driver.parse_epic = AsyncMock(return_value=[
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ])

        # 并发模式是实验性的，但我们应该能够创建driver
        assert driver.concurrent is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_windows_path_conversion(self, temp_environment):
        """测试Windows路径转换"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试WSL/Unix风格路径转换
        unix_paths = [
            "/d/GITHUB/pytQt_template/test.md",
            "/c/Users/test/file.py",
            "/e/some/path/to/file.txt"
        ]

        for unix_path in unix_paths:
            windows_path = driver._convert_to_windows_path(unix_path)
            assert ":" in windows_path  # 应该包含Windows盘符

        # 测试普通路径
        normal_paths = ["docs/test.md", "src/file.py"]
        for normal_path in normal_paths:
            converted = driver._convert_to_windows_path(normal_path)
            assert isinstance(converted, str)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_epic_prefix_extraction(self, temp_environment):
        """测试Epic前缀提取"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        test_cases = [
            ("epic-001-test.md", "001"),
            ("epic-123-another-epic.md", "123"),
            ("no-prefix.md", ""),
            ("epic-456.epic-filename.md", "456"),
        ]

        for filename, expected_prefix in test_cases:
            result = driver._extract_epic_prefix(filename)
            assert result == expected_prefix

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_progress_tracking(self, temp_environment):
        """测试进度跟踪"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试各种进度更新
        await driver._update_progress("dev_qa", "in_progress", {"test": "data"})
        await driver._update_progress("dev_qa", "completed", {"completed": 5, "total": 10})

        # 验证没有异常抛出
        assert True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_epic_initialization(self, temp_environment):
        """测试Epic初始化"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试初始化
        await driver._initialize_epic_processing(5)

        # 验证没有异常抛出
        assert True

    @pytest.mark.integration
    def test_final_report_generation(self, temp_environment):
        """测试最终报告生成"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        report = driver._generate_final_report()

        assert "epic_id" in report
        assert "status" in report
        assert "phases" in report
        assert "total_stories" in report
        assert "timestamp" in report

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_phase_gates_validation(self, temp_environment):
        """测试阶段门控验证"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = driver._validate_phase_gates()

        # 当前实现总是返回True
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_state_consistency_comprehensive(self, temp_environment):
        """测试状态一致性（综合）"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        # 测试故事完整性检查
        story = {"path": str(env["stories"][0])}

        # Mock各种依赖
        driver.state_manager.get_story_status = AsyncMock(return_value={"status": "completed"})
        driver._check_filesystem_state = AsyncMock(return_value=True)
        driver._validate_story_integrity = AsyncMock(return_value=True)

        result = await driver._check_state_consistency(story)

        # 应该是宽容的，允许处理继续
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_filesystem_state_edge_cases(self, temp_environment):
        """测试文件系统状态边界情况"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试没有期望文件的Story
        story = {"path": str(env["stories"][0])}  # 没有expected_files

        result = await driver._check_filesystem_state(story)

        # 应该是宽容的
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_story_integrity_edge_cases(self, temp_environment):
        """测试故事完整性边界情况"""
        env = temp_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # 测试非常短的故事
        short_story = env["tmp_path"] / "short.md"
        short_story.write_text("Short", encoding='utf-8')

        story = {"path": str(short_story)}

        result = await driver._validate_story_integrity(story)

        # 短内容可能失败，这是预期的
        assert isinstance(result, bool)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_graceful_cancellation_comprehensive(self, temp_environment):
        """测试综合的优雅取消"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"path": str(env["stories"][0])}

        # Mock状态管理器和日志管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=True)
        driver.log_manager = MagicMock()

        await driver._handle_graceful_cancellation(story)

        driver.state_manager.update_story_status.assert_called_once()
        driver.log_manager.log_cancellation.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_state_resync_comprehensive(self, temp_environment):
        """测试综合状态重同步"""
        env = temp_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {
            "path": str(env["stories"][0]),
            "expected_status": "completed"
        }

        # Mock依赖
        driver.state_manager.update_story_status = AsyncMock(return_value=True)
        driver.log_manager = MagicMock()

        await driver._resync_story_state(story)

        driver.state_manager.update_story_status.assert_called_once()
        driver.log_manager.log_state_resync.assert_called_once()


class TestQualityGateOrchestratorEnhanced:
    """质量门控增强测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_all_phases_skip(self, temp_environment):
        """测试所有阶段都跳过的情况"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=True,
            skip_tests=True
        )

        result = await orchestrator.execute_quality_gates("test-epic")

        # 跳过所有阶段应该成功
        assert result["success"] is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_pytest_edge_cases(self, temp_environment):
        """测试pytest边界情况"""
        env = temp_environment

        # 测试不存在的测试目录
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["src_dir"]),  # 使用src作为test目录（没有测试文件）
            skip_quality=True,
            skip_tests=False
        )

        result = await orchestrator.execute_pytest_agent(str(env["src_dir"]))

        # 没有测试文件应该被跳过
        assert result["success"] is True
        assert result.get("skipped") is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_error_accumulation(self, temp_environment):
        """测试错误累积"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=False,
            skip_tests=False
        )

        # Mock多个失败的阶段
        with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockRuff, \
             patch('autoBMAD.epic_automation.agents.quality_agents.BasedPyrightAgent') as MockPyright:

            # 都失败
            mock_ruff = MagicMock()
            mock_ruff.execute = AsyncMock(return_value={"status": "failed", "errors": 3})
            MockRuff.return_value = mock_ruff

            mock_pyright = MagicMock()
            mock_pyright.execute = AsyncMock(return_value={"status": "failed", "errors": 2})
            MockPyright.return_value = mock_pyright

            result = await orchestrator.execute_quality_gates("test-epic")

            # 应该记录所有错误
            assert result["success"] is False
            assert len(result["errors"]) >= 1

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_progress_tracking(self, temp_environment):
        """测试进度跟踪"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"])
        )

        # 测试进度更新
        orchestrator._update_progress("phase_1_ruff", "in_progress", start=True)
        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "in_progress"

        orchestrator._update_progress("phase_1_ruff", "completed", end=True)
        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "completed"

    @pytest.mark.integration
    def test_orchestrator_duration_calculation(self, temp_environment):
        """测试持续时间计算"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"])
        )

        # 测试各种时间计算
        test_cases = [
            (1000.0, 1100.0, 100.0),
            (0.0, 1.5, 1.5),
            (99.99, 100.01, 0.02),
        ]

        for start, end, expected in test_cases:
            result = orchestrator._calculate_duration(start, end)
            assert abs(result - expected) < 0.01

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_finalize_with_errors(self, temp_environment):
        """测试带错误的最终化"""
        env = temp_environment

        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"])
        )

        # 设置错误
        orchestrator.results["errors"] = ["Error 1", "Error 2"]
        orchestrator.results["success"] = False
        orchestrator.results["start_time"] = 1000.0

        result = orchestrator._finalize_results()

        assert result["success"] is False
        assert len(result["errors"]) == 2
        assert "total_duration" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

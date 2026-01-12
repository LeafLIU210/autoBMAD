"""
EpicDriver 最终覆盖率测试
添加更多测试用例以达到95%覆盖率
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


class TestEpicDriverFinalCoverage:
    """EpicDriver 最终覆盖率测试"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_story_processing_with_retry(self, temp_epic_environment):
        """测试故事处理的重试机制"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            max_iterations=5,
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}

        call_count = 0
        async def mock_parse_status(path):
            nonlocal call_count
            call_count += 1
            return "Done" if call_count >= 3 else "Draft"

        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)
        driver.state_manager.get_story_status = AsyncMock(return_value=None)

        result = await driver._execute_story_processing(story)
        assert result is True
        assert call_count >= 3

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_quality_gate_with_subprocess_error(self, temp_epic_environment):
        """测试质量门控中subprocess错误处理"""
        env = temp_epic_environment
        orchestrator = QualityGateOrchestrator(
            source_dir=str(env["src_dir"]),
            test_dir=str(env["tests_dir"]),
            skip_quality=True,
            skip_tests=False
        )

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Subprocess error")

            result = await orchestrator.execute_pytest_agent(str(env["tests_dir"]))
            assert result["success"] is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_qa_cycle_with_partial_success(self, temp_epic_environment):
        """测试Dev-QA循环部分成功的处理"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            retry_failed=False,
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        stories = [
            {"id": "1.1", "path": str(env["stories"][0])},
            {"id": "1.2", "path": str(env["stories"][1])}
        ]

        async def mock_process_story(story):
            return story["id"] == "1.2"

        driver.process_story = mock_process_story

        result = await driver.execute_dev_qa_cycle(stories)
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_run_with_state_sync_failure(self, temp_epic_environment):
        """测试状态同步失败时的整体处理"""
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
            "success_count": 0,
            "error_count": 1
        })

        result = await driver.run()
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_extract_story_ids_with_various_formats(self, temp_epic_environment):
        """测试各种格式的故事ID提取"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        content = """# Epic 1: Test Epic

### Story 1.1: First Story
**Story ID**: 1.2
### Story 1.3: Third Story
**Story ID**: 1.4
"""

        story_ids = driver._extract_story_ids_from_epic(content)
        assert len(story_ids) >= 3
        assert any("1.1" in sid for sid in story_ids)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_check_state_consistency_edge_cases(self, temp_epic_environment):
        """测试状态一致性的边界情况"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0])}
        driver.state_manager.get_story_status = AsyncMock(side_effect=Exception("DB Error"))

        result = await driver._check_state_consistency(story)
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_resync_story_state_with_error(self, temp_epic_environment):
        """测试状态重同步时的错误处理"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0]), "expected_status": "completed"}
        driver.state_manager.update_story_status = AsyncMock(return_value=False)
        driver.log_manager = MagicMock()

        await driver._resync_story_state(story)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_handle_graceful_cancellation_with_error(self, temp_epic_environment):
        """测试取消处理时的错误情况"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        story = {"path": str(env["stories"][0])}
        driver.state_manager.update_story_status = AsyncMock(return_value=False)
        driver.log_manager = MagicMock()

        await driver._handle_graceful_cancellation(story)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_progress_with_details(self, temp_epic_environment):
        """测试带详细信息的进度更新"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        details = {
            "completed_stories": 2,
            "total_stories": 3,
            "failed_stories": 1
        }

        await driver._update_progress("dev_qa", "in_progress", details)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_initialize_epic_processing_with_zero_stories(self, temp_epic_environment):
        """测试初始化零故事的处理"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        await driver._initialize_epic_processing(0)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_generate_final_report_with_empty_stories(self, temp_epic_environment):
        """测试空故事列表的报告生成"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        driver.stories = []

        report = driver._generate_final_report()

        assert "epic_id" in report
        assert report["total_stories"] == 0

    @pytest.mark.integration
    def test_extract_epic_prefix_various_formats(self, temp_epic_environment):
        """测试各种格式的epic前缀提取"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        test_cases = [
            ("epic-001-test.md", "001"),
            ("epic-123-important.md", "123"),
            ("no-prefix.md", ""),
            ("epic-.md", ""),
        ]

        for filename, expected in test_cases:
            result = driver._extract_epic_prefix(filename)
            assert result == expected

    @pytest.mark.integration
    def test_convert_to_windows_path_edge_cases(self, temp_epic_environment):
        """测试Windows路径转换的边界情况"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        test_paths = [
            ("/d/GITHUB/pytQt_template/src/test.py", "D:"),
            ("src/test.py", "\\"),
            ("./relative/path.md", "\\"),
        ]

        for path, expected_char in test_paths:
            result = driver._convert_to_windows_path(path)
            assert expected_char in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_cancelled_error(self, temp_epic_environment):
        """测试处理Cancel scope错误"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}

        # 抛出包含"cancel scope"的RuntimeError
        driver._process_story_impl = AsyncMock(
            side_effect=RuntimeError("cancel scope error occurred")
        )

        result = await driver.process_story(story)

        # 应该返回False
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_with_runtime_error(self, temp_epic_environment):
        """测试处理RuntimeError"""
        env = temp_epic_environment
        driver = EpicDriver(
            epic_path=str(env["epic_file"]),
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        story = {"id": "1.1", "path": str(env["stories"][0])}

        # 抛出RuntimeError
        driver._process_story_impl = AsyncMock(side_effect=RuntimeError("Test error"))

        result = await driver.process_story(story)

        # 应该返回False
        assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_with_nonexistent_directory(self, temp_epic_environment):
        """测试质量门控处理不存在的目录"""
        orchestrator = QualityGateOrchestrator(
            source_dir="/nonexistent/path",
            test_dir="/nonexistent/test",
            skip_quality=False,
            skip_tests=False
        )

        result = await orchestrator.execute_quality_gates("test")
        assert "success" in result

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_qa_phase_deprecated(self, temp_epic_environment):
        """测试已弃用的QA阶段执行"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        # QA阶段现在由DevQaController处理，此方法应返回True
        result = await driver.execute_qa_phase(str(env["stories"][0]))
        assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_validate_phase_gates_returns_true(self, temp_epic_environment):
        """测试阶段门控验证总是返回True"""
        env = temp_epic_environment
        driver = EpicDriver(epic_path=str(env["epic_file"]), use_claude=False)

        result = driver._validate_phase_gates()
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

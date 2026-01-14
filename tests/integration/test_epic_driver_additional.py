"""
EpicDriver 额外集成测试
覆盖之前未覆盖的函数和异常处理分支
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import argparse

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import (
    EpicDriver,
    QualityGateOrchestrator,
    parse_arguments,
    main,
    _convert_core_to_processing_status
)


class TestParseArguments:
    """测试命令行参数解析"""

    @pytest.mark.integration
    def test_parse_arguments_basic(self):
        """测试基本参数解析"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md']):
            args = parse_arguments()
            assert args.epic_path == 'test.epic.md'
            assert args.max_iterations == 3  # default value
            assert args.retry_failed is False
            assert args.verbose is False

    @pytest.mark.integration
    def test_parse_arguments_with_max_iterations(self):
        """测试带最大迭代次数的参数"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md', '--max-iterations', '5']):
            args = parse_arguments()
            assert args.max_iterations == 5

    @pytest.mark.integration
    def test_parse_arguments_with_all_options(self):
        """测试所有可选参数"""
        with patch.object(sys, 'argv', [
            'epic_driver.py', 'test.epic.md',
            '--max-iterations', '10',
            '--retry-failed',
            '--verbose',
            '--concurrent',
            '--no-claude',
            '--source-dir', 'my_src',
            '--test-dir', 'my_tests',
            '--skip-quality',
            '--skip-tests'
        ]):
            args = parse_arguments()
            assert args.epic_path == 'test.epic.md'
            assert args.max_iterations == 10
            assert args.retry_failed is True
            assert args.verbose is True
            assert args.concurrent is True
            assert args.no_claude is True
            assert args.source_dir == 'my_src'
            assert args.test_dir == 'my_tests'
            assert args.skip_quality is True
            assert args.skip_tests is True

    @pytest.mark.integration
    def test_parse_arguments_invalid_max_iterations(self):
        """测试无效的最大迭代次数"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md', '--max-iterations', '0']):
            with pytest.raises(SystemExit):
                parse_arguments()

    @pytest.mark.integration
    def test_parse_arguments_negative_max_iterations(self):
        """测试负数最大迭代次数"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md', '--max-iterations', '-5']):
            with pytest.raises(SystemExit):
                parse_arguments()


class TestConvertCoreToProcessingStatus:
    """测试状态转换函数"""

    @pytest.mark.integration
    def test_convert_core_to_processing_status_sm_phase(self):
        """测试SM阶段状态转换"""
        # 测试Draft状态 -> completed (SM完成)
        assert _convert_core_to_processing_status('Draft', 'sm') == 'completed'

        # 测试Ready for Development状态
        assert _convert_core_to_processing_status('Ready for Development', 'sm') == 'pending'

        # 测试其他状态
        assert _convert_core_to_processing_status('Review', 'sm') == 'pending'

    @pytest.mark.integration
    def test_convert_core_to_processing_status_dev_phase(self):
        """测试Dev阶段状态转换"""
        # 测试Draft状态 -> in_progress (Dev开始)
        assert _convert_core_to_processing_status('Draft', 'dev') == 'in_progress'

        # 测试Ready for Development状态 -> in_progress
        assert _convert_core_to_processing_status('Ready for Development', 'dev') == 'in_progress'

        # 测试Review状态 -> completed (Dev完成)
        assert _convert_core_to_processing_status('Review', 'dev') == 'completed'

    @pytest.mark.integration
    def test_convert_core_to_processing_status_qa_phase(self):
        """测试QA阶段状态转换"""
        # 测试Review状态 -> completed (QA完成)
        assert _convert_core_to_processing_status('Review', 'qa') == 'completed'

        # 测试Done状态 -> completed (QA已完成)
        assert _convert_core_to_processing_status('Done', 'qa') == 'completed'

    @pytest.mark.integration
    def test_convert_core_to_processing_status_unknown_phase(self):
        """测试未知阶段"""
        # 测试未知阶段，应该返回基础状态
        assert _convert_core_to_processing_status('Draft', 'unknown') == 'pending'


class TestMainFunction:
    """测试main函数"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_basic(self):
        """测试基本main函数执行"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as mock_parse:
            # Mock解析参数
            mock_args = MagicMock()
            mock_args.epic_path = 'test.epic.md'
            mock_args.max_iterations = 3
            mock_args.retry_failed = False
            mock_args.verbose = False
            mock_args.concurrent = False
            mock_args.no_claude = True
            mock_args.source_dir = 'src'
            mock_args.test_dir = 'tests'
            mock_args.skip_quality = True
            mock_args.skip_tests = True
            mock_parse.return_value = mock_args

            # Mock文件存在
            with patch('pathlib.Path.exists', return_value=True):
                with patch('autoBMAD.epic_automation.epic_driver.EpicDriver') as MockDriver:
                    mock_driver = AsyncMock()
                    mock_driver.run = AsyncMock(return_value=True)
                    MockDriver.return_value = mock_driver

                    with patch.object(sys, 'exit') as mock_exit:
                        await main()
                        mock_exit.assert_called_with(0)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_epic_file_not_found(self):
        """测试epic文件不存在的情况"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'nonexistent.epic.md']):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('autoBMAD.epic_automation.epic_driver.logger') as mock_logger:
                    with patch.object(sys, 'exit') as mock_exit:
                        await main()
                        mock_logger.error.assert_called()
                        mock_exit.assert_called_with(1)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_verbose_logging(self):
        """测试详细日志模式"""
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.epic.md', '--verbose']):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('autoBMAD.epic_automation.epic_driver.EpicDriver') as MockDriver:
                    mock_driver = AsyncMock()
                    mock_driver.run = AsyncMock(return_value=True)
                    MockDriver.return_value = mock_driver

                    with patch('logging.getLogger') as mock_get_logger:
                        mock_logger = MagicMock()
                        mock_get_logger.return_value = mock_logger

                        await main()
                        mock_get_logger.return_value.setLevel.assert_called_with(logging.DEBUG)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_main_driver_failure(self):
        """测试driver执行失败的情况"""
        with patch('autoBMAD.epic_automation.epic_driver.parse_arguments') as mock_parse:
            mock_args = MagicMock()
            mock_args.epic_path = 'test.epic.md'
            mock_args.max_iterations = 3
            mock_args.retry_failed = False
            mock_args.verbose = False
            mock_args.concurrent = False
            mock_args.no_claude = True
            mock_args.source_dir = 'src'
            mock_args.test_dir = 'tests'
            mock_args.skip_quality = True
            mock_args.skip_tests = True
            mock_parse.return_value = mock_args

            with patch('pathlib.Path.exists', return_value=True):
                with patch('autoBMAD.epic_automation.epic_driver.EpicDriver') as MockDriver:
                    mock_driver = AsyncMock()
                    mock_driver.run = AsyncMock(return_value=False)  # 模拟失败
                    MockDriver.return_value = mock_driver

                    with patch.object(sys, 'exit') as mock_exit:
                        await main()
                        mock_exit.assert_called_with(1)


class TestQualityGateOrchestratorAdditional:
    """测试质量门控的额外功能"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_calculate_duration(self):
        """测试持续时间计算"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )
        duration = orchestrator._calculate_duration(1000.0, 1100.0)
        assert duration == 100.0
        assert isinstance(duration, float)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_calculate_duration_edge_cases(self):
        """测试持续时间计算的边界情况"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )
        # 测试相同时间
        duration = orchestrator._calculate_duration(1000.0, 1000.0)
        assert duration == 0.0

        # 测试负数时间（不应该发生，但测试健壮性）
        duration = orchestrator._calculate_duration(1100.0, 1000.0)
        assert duration == -100.0

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_update_progress(self):
        """测试进度更新"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # 测试开始进度
        orchestrator._update_progress("phase_1_ruff", "in_progress", start=True)

        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "in_progress"
        assert "start_time" in orchestrator.results["progress"]["phase_1_ruff"]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_update_progress_end(self):
        """测试进度结束更新"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # 设置开始状态
        orchestrator.results["progress"]["phase_1_ruff"] = {
            "status": "in_progress",
            "start_time": 1000.0
        }

        # 测试结束进度
        orchestrator._update_progress("phase_1_ruff", "completed", end=True)

        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "completed"
        assert "end_time" in orchestrator.results["progress"]["phase_1_ruff"]
        assert "duration" in orchestrator.results["progress"]["phase_1_ruff"]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_error_handling(self):
        """测试质量门控错误处理"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            orchestrator = QualityGateOrchestrator(
                source_dir=tmp_dir,
                test_dir=tmp_dir,
                skip_quality=False,
                skip_tests=False
            )

            # Mock RuffAgent抛出异常
            with patch('autoBMAD.epic_automation.agents.quality_agents.RuffAgent') as MockAgent:
                mock_agent = MagicMock()
                mock_agent.execute = MagicMock(side_effect=Exception("Test error"))
                MockAgent.return_value = mock_agent

                result = await orchestrator.execute_ruff_agent(tmp_dir)

                # 应该返回失败结果
                assert result["success"] is False
                assert "error" in result
                assert result["error_count"] >= 1

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_orchestrator_finalize_results(self):
        """测试结果最终化"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # 设置开始和结束时间
        orchestrator.results["start_time"] = 1000.0
        orchestrator.results["end_time"] = 1100.0

        # Mock部分结果
        orchestrator.results["ruff"] = {"success": True, "errors": 0}
        orchestrator.results["basedpyright"] = {"success": True, "errors": 2}
        orchestrator.results["pytest"] = {"success": False, "errors": 5}

        result = orchestrator._finalize_results()

        assert "total_duration" in result
        assert result["total_duration"] == 100.0
        assert "total_errors" in result
        assert result["total_errors"] == 7


class TestEpicDriverAdditionalCoverage:
    """测试EpicDriver的额外覆盖率"""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_sm_phase_with_exception(self):
        """测试SM阶段执行异常处理"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("Test story", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            # Mock SMController抛出异常
            with patch('autoBMAD.epic_automation.controllers.sm_controller.SMController') as MockCtrl:
                mock_ctrl = MagicMock()
                mock_ctrl.execute = MagicMock(side_effect=Exception("Test exception"))
                MockCtrl.return_value = mock_ctrl

                driver.state_manager.update_story_status = AsyncMock(return_value=True)

                result = await driver.execute_sm_phase(str(story_file))

                # 应该返回False（异常情况）
                assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_execute_dev_phase_with_exception(self):
        """测试Dev阶段执行异常处理"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("Test story", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            # Mock DevQaController抛出异常
            with patch('autoBMAD.epic_automation.controllers.devqa_controller.DevQaController') as MockCtrl:
                mock_ctrl = MagicMock()
                mock_ctrl.execute = MagicMock(side_effect=Exception("Test exception"))
                MockCtrl.return_value = mock_ctrl

                driver.state_manager.update_story_status = AsyncMock(return_value=True)

                result = await driver.execute_dev_phase(str(story_file), iteration=1)

                # 应该返回False（异常情况）
                assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_process_story_exception_handling(self):
        """测试故事处理异常处理"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("Test story", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            story = {"path": str(story_file)}

            # Mock _process_story_impl抛出异常
            driver._process_story_impl = AsyncMock(side_effect=Exception("Test exception"))

            result = await driver.process_story(story)

            # 应该返回False（异常情况）
            assert result is False

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_parse_story_status_with_nonexistent_file(self):
        """测试解析不存在的故事文件"""
        driver = EpicDriver(
            epic_path="nonexistent.epic.md",
            use_claude=False
        )

        # 测试同步解析
        status = driver._parse_story_status_sync("/nonexistent/path.md")
        # 应该返回空字符串或默认值
        assert status == ""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_is_story_ready_for_done_with_various_statuses(self):
        """测试各种状态下的完成检查"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("Test story", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            # 测试Done状态
            driver._parse_story_status = AsyncMock(return_value="Done")
            result = await driver._is_story_ready_for_done(str(story_file))
            assert result is True

            # 测试Draft状态
            driver._parse_story_status = AsyncMock(return_value="Draft")
            result = await driver._is_story_ready_for_done(str(story_file))
            assert result is False

            # 测试Review状态
            driver._parse_story_status = AsyncMock(return_value="Review")
            result = await driver._is_story_ready_for_done(str(story_file))
            assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_check_filesystem_state_with_missing_files(self):
        """测试缺少文件时的文件系统状态检查"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("Test story", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            story = {
                "path": str(story_file),
                "expected_files": ["nonexistent_dir"]
            }

            result = await driver._check_filesystem_state(story)
            # 应该返回True（允许处理继续）
            assert result is True

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_validate_story_integrity_with_empty_file(self):
        """测试空文件的故事完整性验证"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_file = Path(tmp_dir) / "test_story.md"
            story_file.write_text("", encoding='utf-8')  # 空文件

            driver = EpicDriver(
                epic_path=str(story_file),
                use_claude=False
            )

            story = {"path": str(story_file)}

            result = await driver._validate_story_integrity(story)
            # 空文件应该返回False
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])

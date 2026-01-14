"""
PytestController Comprehensive Test Suite

Tests for PytestController including:
- Initialization
- Test file discovery
- Cycle management
- SDK fix execution
- Result building
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open

from autoBMAD.epic_automation.controllers.pytest_controller import PytestController


class TestPytestController:
    """Test suite for PytestController"""

    def test_init_default(self):
        """测试默认初始化"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        assert controller.source_dir == "src"
        assert controller.test_dir == "tests"
        assert controller.max_cycles == 3
        assert controller.summary_json_path == "pytest_summary.json"
        assert controller.current_cycle == 0
        assert controller.failed_files == []
        assert controller.initial_failed_files == []
        assert controller.sdk_fix_errors == []

    def test_init_with_custom_params(self):
        """测试自定义参数初始化"""
        controller = PytestController(
            source_dir="custom_src",
            test_dir="custom_tests",
            max_cycles=5,
            summary_json_path="custom_summary.json"
        )

        assert controller.max_cycles == 5
        assert controller.summary_json_path == "custom_summary.json"

    @pytest.mark.anyio
    async def test_run_no_failed_files(self):
        """测试无失败文件的成功场景"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        # Mock pytest agent to return no failed files
        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.return_value = {
                "files": [
                    {"test_file": "test_1.py", "status": "passed"},
                    {"test_file": "test_2.py", "status": "passed"}
                ]
            }

            result = await controller.run()

            assert result["status"] == "completed"
            assert result["cycles"] == 1
            assert result["sdk_fix_attempted"] is False
            assert result["initial_failed_files"] == []
            assert result["final_failed_files"] == []

    @pytest.mark.anyio
    async def test_run_with_failed_files_and_recovery(self):
        """测试有失败文件但能恢复的场景"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests",
            max_cycles=2
        )

        # Mock: first run has failures, second run has none
        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.side_effect = [
                {  # First cycle
                    "files": [
                        {"test_file": "test_1.py", "status": "failed"},
                        {"test_file": "test_2.py", "status": "passed"}
                    ]
                },
                {  # Second cycle (regression)
                    "files": [
                        {"test_file": "test_1.py", "status": "passed"}
                    ]
                }
            ]

            with patch.object(controller.pytest_agent, 'run_sdk_fix_for_file') as mock_sdk:
                mock_sdk.return_value = {"success": True}

                result = await controller.run()

                assert result["status"] == "completed"
                assert result["cycles"] == 2
                assert len(result["initial_failed_files"]) == 1
                assert len(result["final_failed_files"]) == 0

    @pytest.mark.anyio
    async def test_run_max_cycles_reached(self):
        """测试达到最大循环次数"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests",
            max_cycles=2
        )

        # Mock: always return failures
        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.return_value = {
                "files": [
                    {"test_file": "test_1.py", "status": "failed"}
                ]
            }

            with patch.object(controller.pytest_agent, 'run_sdk_fix_for_file') as mock_sdk:
                mock_sdk.return_value = {"success": True}

                result = await controller.run()

                assert result["status"] == "failed"
                assert result["cycles"] == 2  # max_cycles
                assert len(result["final_failed_files"]) == 1

    @pytest.mark.anyio
    async def test_run_exception_handling(self):
        """测试异常处理"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        # Mock to raise exception
        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.side_effect = Exception("Test error")

            result = await controller.run()

            assert result["status"] == "failed"
            assert "sdk_fix_errors" in result
            assert len(result["sdk_fix_errors"]) > 0

    def test_discover_test_files(self):
        """测试测试文件发现"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir).mkdir(parents=True, exist_ok=True)
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            (test_dir / "test_file1.py").write_text("# test")
            (test_dir / "test_file2.py").write_text("# test")
            (test_dir / "normal_file.py").write_text("# not a test")
            (test_dir / "other_test.py").write_text("# test")

            controller.test_dir = str(test_dir)

            files = controller._discover_test_files()

            # Should find test_*.py and *_test.py files
            assert len(files) == 3
            assert any("test_file1" in f for f in files)
            assert any("test_file2" in f for f in files)
            assert any("other_test" in f for f in files)
            assert not any("normal_file" in f for f in files)

    def test_discover_test_files_nonexistent(self):
        """测试发现不存在的测试目录"""
        controller = PytestController(
            source_dir="src",
            test_dir="nonexistent_tests"
        )

        files = controller._discover_test_files()

        assert files == []

    @pytest.mark.anyio
    async def test_run_test_phase_all_files(self):
        """测试全量测试阶段"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.return_value = {
                "files": [
                    {"test_file": "test_1.py", "status": "failed", "failures": []},
                    {"test_file": "test_2.py", "status": "passed", "failures": []}
                ]
            }

            with patch.object(controller, '_discover_test_files') as mock_discover:
                mock_discover.return_value = ["test_1.py", "test_2.py"]

                failed_files = await controller._run_test_phase_all_files(1)

                assert len(failed_files) == 1
                assert "test_1.py" in failed_files

    @pytest.mark.anyio
    async def test_run_test_phase_failed_files(self):
        """测试回归测试阶段"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with patch.object(controller.pytest_agent, 'run_tests_sequential') as mock_run:
            mock_run.return_value = {
                "files": [
                    {"test_file": "test_1.py", "status": "failed", "failures": []},
                    {"test_file": "test_2.py", "status": "passed", "failures": []}
                ]
            }

            failed_files = ["test_1.py", "test_2.py"]

            result = await controller._run_test_phase_failed_files(failed_files, 2)

            assert len(result) == 1
            assert "test_1.py" in result

    @pytest.mark.anyio
    async def test_run_sdk_phase_success(self):
        """测试SDK修复阶段成功"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with patch.object(controller.pytest_agent, 'run_sdk_fix_for_file') as mock_sdk:
            mock_sdk.return_value = {"success": True}

            await controller._run_sdk_phase(["test_1.py", "test_2.py"], 1)

            assert mock_sdk.call_count == 2
            assert len(controller.sdk_fix_errors) == 0

    @pytest.mark.anyio
    async def test_run_sdk_phase_with_failures(self):
        """测试SDK修复阶段有失败"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with patch.object(controller.pytest_agent, 'run_sdk_fix_for_file') as mock_sdk:
            mock_sdk.side_effect = [
                {"success": True},
                {"success": False, "error": "SDK error"}
            ]

            await controller._run_sdk_phase(["test_1.py", "test_2.py"], 1)

            assert mock_sdk.call_count == 2
            assert len(controller.sdk_fix_errors) == 1
            assert controller.sdk_fix_errors[0]["test_file"] == "test_2.py"

    @pytest.mark.anyio
    async def test_run_sdk_phase_exception(self):
        """测试SDK修复阶段异常"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )

        with patch.object(controller.pytest_agent, 'run_sdk_fix_for_file') as mock_sdk:
            mock_sdk.side_effect = Exception("SDK exception")

            await controller._run_sdk_phase(["test_1.py"], 1)

            assert len(controller.sdk_fix_errors) == 1
            assert "SDK phase exception" in controller.sdk_fix_errors[0]["error"]

    def test_append_round_to_summary_json_new_file(self):
        """测试追加轮次到新的汇总JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"
            controller = PytestController(
                source_dir="src",
                test_dir="tests",
                summary_json_path=str(summary_path)
            )

            round_result = {
                "files": [
                    {"test_file": "test_1.py", "status": "failed", "failures": []}
                ]
            }

            controller.current_cycle = 1
            controller._append_round_to_summary_json(1, "initial", round_result)

            # Check file was created
            assert summary_path.exists()

            with open(summary_path) as f:
                data = json.load(f)

            assert "summary" in data
            assert "rounds" in data
            assert len(data["rounds"]) == 1
            assert data["rounds"][0]["round_index"] == 1

    def test_append_round_to_summary_json_existing_file(self):
        """测试追加轮次到现有的汇总JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"

            # Create existing summary
            existing_data = {
                "summary": {"total_files": 2},
                "rounds": []
            }
            summary_path.write_text(json.dumps(existing_data))

            controller = PytestController(
                source_dir="src",
                test_dir="tests",
                summary_json_path=str(summary_path)
            )

            round_result = {
                "files": [
                    {"test_file": "test_1.py", "status": "failed", "failures": []}
                ]
            }

            controller.current_cycle = 1
            controller._append_round_to_summary_json(1, "initial", round_result)

            with open(summary_path) as f:
                data = json.load(f)

            assert len(data["rounds"]) == 1

    def test_load_summary_json_existing_valid(self):
        """测试加载现有的有效汇总JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"
            summary_path.write_text(json.dumps({
                "summary": {"total": 5},
                "rounds": []
            }))

            controller = PytestController(
                source_dir="src",
                test_dir="tests",
                summary_json_path=str(summary_path)
            )

            data = controller._load_summary_json()

            assert data["summary"]["total"] == 5

    def test_load_summary_json_existing_invalid(self):
        """测试加载现有的无效汇总JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"
            summary_path.write_text("invalid json{")

            controller = PytestController(
                source_dir="src",
                test_dir="tests",
                summary_json_path=str(summary_path)
            )

            data = controller._load_summary_json()

            # Should return new structure
            assert "summary" in data
            assert "rounds" in data

    def test_build_success_result(self):
        """测试构建成功结果"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )
        controller.current_cycle = 1

        result = controller._build_success_result()

        assert result["status"] == "completed"
        assert result["cycles"] == 1
        assert result["sdk_fix_attempted"] is False
        assert result["initial_failed_files"] == []
        assert result["final_failed_files"] == []

    def test_build_final_result_success(self):
        """测试构建最终结果 - 成功"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )
        controller.current_cycle = 2
        controller.failed_files = []

        result = controller._build_final_result()

        assert result["status"] == "completed"

    def test_build_final_result_failure(self):
        """测试构建最终结果 - 失败"""
        controller = PytestController(
            source_dir="src",
            test_dir="tests"
        )
        controller.current_cycle = 3
        controller.failed_files = ["test_1.py"]

        result = controller._build_final_result()

        assert result["status"] == "failed"
        assert len(result["final_failed_files"]) == 1

"""
PytestController 单元测试
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.epic_automation.controllers.pytest_controller import PytestController


class TestPytestController:
    """PytestController 单元测试"""

    @pytest.fixture
    def temp_test_dir(self):
        """创建临时测试目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # 创建测试文件
            (test_dir / "test_success.py").write_text("""
def test_pass():
    assert 1 == 1
""")

            (test_dir / "test_failure.py").write_text("""
def test_fail():
    assert 1 == 2
""")

            yield str(test_dir)

    @pytest.fixture
    def temp_source_dir(self):
        """创建临时源码目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "src"
            source_dir.mkdir()
            yield str(source_dir)

    def test_init(self, temp_source_dir, temp_test_dir):
        """测试初始化"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )

        assert controller.source_dir == temp_source_dir
        assert controller.test_dir == temp_test_dir
        assert controller.max_cycles == 2
        assert controller.current_cycle == 0
        assert controller.failed_files == []
        assert controller.initial_failed_files == []
        assert controller.sdk_fix_errors == []

    def test_discover_test_files(self, temp_test_dir):
        """测试测试文件发现"""
        controller = PytestController(
            source_dir="src",
            test_dir=temp_test_dir,
        )

        test_files = controller._discover_test_files()

        assert len(test_files) == 2
        assert any("test_success.py" in f for f in test_files)
        assert any("test_failure.py" in f for f in test_files)

    def test_discover_test_files_no_dir(self):
        """测试不存在的测试目录"""
        controller = PytestController(
            source_dir="src",
            test_dir="nonexistent",
        )

        test_files = controller._discover_test_files()

        assert test_files == []

    def test_build_success_result(self, temp_source_dir, temp_test_dir):
        """测试构造成功结果"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )
        controller.current_cycle = 1
        controller.initial_failed_files = []

        result = controller._build_success_result()

        assert result["status"] == "completed"
        assert result["cycles"] == 1
        assert result["initial_failed_files"] == []
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is False
        assert result["sdk_fix_errors"] == []

    def test_build_final_result(self, temp_source_dir, temp_test_dir):
        """测试构造最终结果"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )
        controller.current_cycle = 2
        controller.initial_failed_files = ["test_failure.py"]
        controller.failed_files = []
        controller.sdk_fix_errors = []

        result = controller._build_final_result()

        assert result["status"] == "completed"
        assert result["cycles"] == 2
        assert result["initial_failed_files"] == ["test_failure.py"]
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is True
        assert result["sdk_fix_errors"] == []

    def test_build_final_result_with_failures(self, temp_source_dir, temp_test_dir):
        """测试构造包含失败的最终结果"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )
        controller.current_cycle = 3
        controller.initial_failed_files = ["test_failure.py"]
        controller.failed_files = ["test_failure.py"]
        controller.sdk_fix_errors = [{"error": "SDK error", "round_index": 1}]

        result = controller._build_final_result()

        assert result["status"] == "failed"
        assert result["cycles"] == 3
        assert result["initial_failed_files"] == ["test_failure.py"]
        assert result["final_failed_files"] == ["test_failure.py"]
        assert result["sdk_fix_attempted"] is True
        assert len(result["sdk_fix_errors"]) == 1

    @pytest.mark.asyncio
    async def test_run_all_pass(self, temp_source_dir, temp_test_dir):
        """测试所有测试通过的情况"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )

        # Mock pytest_agent.run_tests_sequential
        controller.pytest_agent.run_tests_sequential = AsyncMock(return_value={
            "files": [
                {
                    "test_file": "test_success.py",
                    "status": "passed",
                    "failures": [],
                }
            ]
        })

        result = await controller.run()

        assert result["status"] == "completed"
        assert result["cycles"] == 1
        assert result["initial_failed_files"] == []
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is False

    @pytest.mark.asyncio
    async def test_run_with_failures(self, temp_source_dir, temp_test_dir):
        """测试有测试失败的情况"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )

        # Mock pytest_agent
        controller.pytest_agent.run_tests_sequential = AsyncMock(return_value={
            "files": [
                {
                    "test_file": "test_failure.py",
                    "status": "failed",
                    "failures": [
                        {
                            "nodeid": "test_failure.py::test_fail",
                            "failure_type": "failed",
                            "message": "AssertionError",
                            "short_tb": "test_failure.py:2",
                        }
                    ],
                }
            ]
        })

        # Mock SDK fix to succeed (no failures in retry)
        call_count = 0
        async def mock_run_tests_sequential(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call (initial)
                return {
                    "files": [
                        {
                            "test_file": "test_failure.py",
                            "status": "failed",
                            "failures": [
                                {
                                    "nodeid": "test_failure.py::test_fail",
                                    "failure_type": "failed",
                                    "message": "AssertionError",
                                    "short_tb": "test_failure.py:2",
                                }
                            ],
                        }
                    ]
                }
            else:
                # Retry call - all tests pass
                return {
                    "files": [
                        {
                            "test_file": "test_failure.py",
                            "status": "passed",
                            "failures": [],
                        }
                    ]
                }

        controller.pytest_agent.run_tests_sequential = mock_run_tests_sequential
        controller.pytest_agent.run_sdk_fix_for_file = AsyncMock(return_value={
            "success": True
        })

        result = await controller.run()

        assert result["status"] == "completed"
        assert result["cycles"] == 2
        assert result["initial_failed_files"] == ["test_failure.py"]
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is True

    @pytest.mark.asyncio
    async def test_run_max_cycles_exceeded(self, temp_source_dir, temp_test_dir):
        """测试超过最大循环次数"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )

        # Mock pytest_agent to always return failures
        controller.pytest_agent.run_tests_sequential = AsyncMock(return_value={
            "files": [
                {
                    "test_file": "test_failure.py",
                    "status": "failed",
                    "failures": [
                        {
                            "nodeid": "test_failure.py::test_fail",
                            "failure_type": "failed",
                            "message": "AssertionError",
                            "short_tb": "test_failure.py:2",
                        }
                    ],
                }
            ]
        })

        controller.pytest_agent.run_sdk_fix_for_file = AsyncMock(return_value={
            "success": False,
            "error": "SDK fix failed"
        })

        result = await controller.run()

        assert result["status"] == "failed"
        assert result["cycles"] == 3  # current_cycle will be 3 after max_cycles exceeded
        assert result["initial_failed_files"] == ["test_failure.py"]
        assert result["final_failed_files"] == ["test_failure.py"]
        assert result["sdk_fix_attempted"] is True
        assert len(result["sdk_fix_errors"]) > 0

    def test_load_summary_json_new(self, temp_source_dir, temp_test_dir):
        """测试加载新汇总JSON"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            summary_json_path="nonexistent.json",
        )

        summary = controller._load_summary_json()

        assert "summary" in summary
        assert "rounds" in summary
        assert summary["summary"]["total_files"] == 0
        assert summary["rounds"] == []

    def test_load_summary_json_existing(self, temp_source_dir, temp_test_dir):
        """测试加载现有汇总JSON"""
        summary_data = {
            "summary": {
                "total_files": 10,
                "failed_files_initial": 2,
                "failed_files_final": 0,
                "cycles": 3,
            },
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "timestamp": "2026-01-13T10:00:00Z",
                    "failed_files": []
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(summary_data, f)
            json_path = f.name

        try:
            controller = PytestController(
                source_dir=temp_source_dir,
                test_dir=temp_test_dir,
                summary_json_path=json_path,
            )

            summary = controller._load_summary_json()

            assert summary["summary"]["total_files"] == 10
            assert len(summary["rounds"]) == 1
        finally:
            Path(json_path).unlink(missing_ok=True)

    def test_append_round_to_summary_json(self, temp_source_dir, temp_test_dir):
        """测试追加轮次到汇总JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json_path = f.name

        try:
            controller = PytestController(
                source_dir=temp_source_dir,
                test_dir=temp_test_dir,
                summary_json_path=json_path,
            )

            # 初始空JSON
            controller._append_round_to_summary_json(
                round_index=1,
                round_type="initial",
                round_result={
                    "files": [
                        {
                            "test_file": "test_failure.py",
                            "status": "failed",
                            "failures": [
                                {
                                    "nodeid": "test_failure.py::test_fail",
                                    "failure_type": "failed",
                                    "message": "AssertionError",
                                    "short_tb": "test_failure.py:2",
                                }
                            ],
                        }
                    ]
                }
            )

            # 验证JSON文件内容
            with open(json_path, "r") as f:
                data = json.load(f)

            assert len(data["rounds"]) == 1
            assert data["rounds"][0]["round_index"] == 1
            assert data["rounds"][0]["round_type"] == "initial"
            assert len(data["rounds"][0]["failed_files"]) == 1
            assert data["summary"]["total_files"] == 1
            assert data["summary"]["failed_files_initial"] == 1

        finally:
            Path(json_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_run_sdk_phase(self, temp_source_dir, temp_test_dir):
        """测试SDK修复阶段"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )

        # Mock SDK修复调用
        controller.pytest_agent.run_sdk_fix_for_file = AsyncMock(return_value={
            "success": True
        })

        await controller._run_sdk_phase(
            failed_files=["test_failure.py"],
            round_index=1
        )

        assert len(controller.sdk_fix_errors) == 0
        controller.pytest_agent.run_sdk_fix_for_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_sdk_phase_with_error(self, temp_source_dir, temp_test_dir):
        """测试SDK修复阶段出现错误"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )

        # Mock SDK修复调用失败
        controller.pytest_agent.run_sdk_fix_for_file = AsyncMock(return_value={
            "success": False,
            "error": "SDK error"
        })

        await controller._run_sdk_phase(
            failed_files=["test_failure.py"],
            round_index=1
        )

        assert len(controller.sdk_fix_errors) == 1
        assert controller.sdk_fix_errors[0]["test_file"] == "test_failure.py"
        assert controller.sdk_fix_errors[0]["error"] == "SDK error"

    @pytest.mark.asyncio
    async def test_run_sdk_phase_with_exception(self, temp_source_dir, temp_test_dir):
        """测试SDK修复阶段出现异常"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
        )

        # Mock SDK修复调用抛出异常
        controller.pytest_agent.run_sdk_fix_for_file = AsyncMock(side_effect=Exception("Unexpected error"))

        await controller._run_sdk_phase(
            failed_files=["test_failure.py"],
            round_index=1
        )

        assert len(controller.sdk_fix_errors) == 1
        assert "SDK phase exception" in controller.sdk_fix_errors[0]["error"]

"""
质量门禁超限错误汇总机制测试

测试覆盖：
1. Controller层max_cycles字段返回
2. Orchestrator判定逻辑
3. JSON生成功能
4. 各种场景下的phase状态

作者: autoBMAD Team
日期: 2026-01-14
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator
from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController
from autoBMAD.epic_automation.controllers.pytest_controller import PytestController


class TestQualityCheckControllerMaxCycles:
    """测试QualityCheckController的max_cycles字段"""

    @pytest.fixture
    def mock_agent(self):
        """创建模拟的Agent"""
        agent = Mock()
        agent.execute = AsyncMock()
        agent.parse_errors_by_file = Mock()
        agent.build_fix_prompt = Mock(return_value="Mock prompt")
        return agent

    @pytest.mark.asyncio
    async def test_build_success_result_includes_max_cycles(self, mock_agent):
        """测试成功结果包含max_cycles字段"""
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir="src",
            max_cycles=5,
        )

        result = controller._build_success_result()

        assert "max_cycles" in result
        assert result["max_cycles"] == 5

    @pytest.mark.asyncio
    async def test_build_final_result_includes_max_cycles(self, mock_agent):
        """测试最终结果包含max_cycles字段"""
        controller = QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir="src",
            max_cycles=3,
        )

        controller.final_error_files = ["file1.py"]
        result = controller._build_final_result()

        assert "max_cycles" in result
        assert result["max_cycles"] == 3

    @pytest.mark.asyncio
    async def test_run_result_includes_max_cycles(self, mock_agent):
        """测试run()方法返回结果包含max_cycles字段"""
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir="src",
            max_cycles=2,
        )

        # 模拟检查阶段返回空错误（成功场景）
        controller._run_check_phase = AsyncMock(return_value={})

        result = await controller.run()

        assert "max_cycles" in result
        assert result["max_cycles"] == 2


class TestPytestControllerMaxCycles:
    """测试PytestController的max_cycles字段"""

    @pytest.fixture
    def controller(self):
        """创建PytestController实例"""
        return PytestController(
            source_dir="src",
            test_dir="tests",
            max_cycles=4,
        )

    def test_build_success_result_includes_max_cycles(self, controller):
        """测试成功结果包含max_cycles字段"""
        result = controller._build_success_result()

        assert "max_cycles" in result
        assert result["max_cycles"] == 4

    def test_build_final_result_includes_max_cycles(self, controller):
        """测试最终结果包含max_cycles字段"""
        controller.failed_files = ["test_file1.py"]
        result = controller._build_final_result()

        assert "max_cycles" in result
        assert result["max_cycles"] == 4

    def test_exception_result_includes_max_cycles(self, controller):
        """测试异常返回结果包含max_cycles字段"""
        try:
            raise Exception("Test exception")
        except Exception as e:
            result = controller._build_final_result()

        assert "max_cycles" in result
        assert result["max_cycles"] == 4


class TestQualityGateOrchestrator判定逻辑:
    """测试QualityGateOrchestrator的判定逻辑"""

    @pytest.fixture
    def orchestrator(self):
        """创建QualityGateOrchestrator实例"""
        return QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

    def test_is_max_cycles_exceeded_with_errors_true(self, orchestrator):
        """测试超限且有错误的情况"""
        result = {
            "status": "failed",
            "cycles": 3,
            "max_cycles": 3,
            "final_error_files": ["file1.py", "file2.py"],
        }

        assert orchestrator._is_max_cycles_exceeded_with_errors(result) is True

    def test_is_max_cycles_exceeded_with_errors_false_completed(self, orchestrator):
        """测试status为completed的情况"""
        result = {
            "status": "completed",
            "cycles": 3,
            "max_cycles": 3,
            "final_error_files": ["file1.py"],
        }

        assert orchestrator._is_max_cycles_exceeded_with_errors(result) is False

    def test_is_max_cycles_exceeded_with_errors_false_not_reached(self, orchestrator):
        """测试未达到max_cycles的情况"""
        result = {
            "status": "failed",
            "cycles": 2,
            "max_cycles": 3,
            "final_error_files": ["file1.py"],
        }

        assert orchestrator._is_max_cycles_exceeded_with_errors(result) is False

    def test_is_max_cycles_exceeded_with_errors_false_no_remaining_files(self, orchestrator):
        """测试超限但无残留文件的情况"""
        result = {
            "status": "failed",
            "cycles": 3,
            "max_cycles": 3,
            "final_error_files": [],
        }

        assert orchestrator._is_max_cycles_exceeded_with_errors(result) is False

    def test_is_max_cycles_exceeded_with_errors_pytest_format(self, orchestrator):
        """测试Pytest格式的最终失败文件"""
        result = {
            "status": "failed",
            "cycles": 3,
            "max_cycles": 3,
            "final_failed_files": ["test_file1.py"],
        }

        assert orchestrator._is_max_cycles_exceeded_with_errors(result) is True


class TestQualityGateOrchestratorJSON生成:
    """测试错误汇总JSON生成功能"""

    @pytest.fixture
    def orchestrator(self):
        """创建QualityGateOrchestrator实例"""
        return QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

    def test_write_error_summary_json_success(self, orchestrator):
        """测试成功生成JSON文件"""
        issues = [
            {
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["file1.py"],
            }
        ]

        json_path = orchestrator._write_error_summary_json("test-epic", issues)

        assert json_path is not None
        assert Path(json_path).exists()

        # 验证JSON内容
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["epic_id"] == "test-epic"
        assert "timestamp" in data
        assert data["source_dir"] == "src"
        assert data["test_dir"] == "tests"
        assert len(data["tools"]) == 1
        assert data["tools"][0]["tool"] == "ruff"

        # 清理
        os.unlink(json_path)

    def test_write_error_summary_json_empty_issues(self, orchestrator):
        """测试issues为空时不生成JSON"""
        json_path = orchestrator._write_error_summary_json("test-epic", [])

        assert json_path is None

    def test_write_error_summary_json_multiple_tools(self, orchestrator):
        """测试多个工具超限的情况"""
        issues = [
            {
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["file1.py"],
            },
            {
                "tool": "pytest",
                "phase": "phase_3_pytest",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["test_file1.py", "test_file2.py"],
            },
        ]

        json_path = orchestrator._write_error_summary_json("test-epic", issues)

        assert json_path is not None
        assert Path(json_path).exists()

        # 验证JSON内容
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["tools"]) == 2
        assert data["tools"][0]["tool"] == "ruff"
        assert data["tools"][1]["tool"] == "pytest"

        # 清理
        os.unlink(json_path)


class TestQualityGateOrchestrator完整流程:
    """测试完整质量门控流程"""

    @pytest.mark.asyncio
    async def test_execute_quality_gates_with_max_cycles_exceeded(self):
        """测试超限场景下的完整流程"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock QualityCheckController返回超限结果
        mock_result = {
            "status": "failed",
            "tool": "ruff",
            "cycles": 3,
            "max_cycles": 3,
            "final_error_files": ["file1.py"],
            "sdk_fix_attempted": True,
            "sdk_fix_errors": [],
        }

        with patch.object(orchestrator, 'execute_ruff_agent', new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": True,  # 超限场景返回True
                "warning": "Max cycles exceeded with errors",
                "duration": 10.0,
                "result": mock_result,
            }

            result = await orchestrator.execute_quality_gates("test-epic")

            # 验证整体成功
            assert result["success"] is True

            # 验证有质量警告
            assert len(result["quality_warnings"]) > 0

            # 验证生成了JSON
            assert result["error_summary_json"] is not None
            assert Path(result["error_summary_json"]).exists()

            # 验证JSON内容
            with open(result["error_summary_json"], "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["epic_id"] == "test-epic"
            assert len(data["tools"]) == 1

            # 清理
            os.unlink(result["error_summary_json"])

    @pytest.mark.asyncio
    async def test_execute_quality_gates_normal_success(self):
        """测试正常成功场景"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        with patch.object(orchestrator, 'execute_ruff_agent', new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": True,
                "duration": 5.0,
                "result": {
                    "status": "completed",
                    "tool": "ruff",
                    "cycles": 1,
                    "max_cycles": 3,
                    "final_error_files": [],
                },
            }

            result = await orchestrator.execute_quality_gates("test-epic")

            # 验证整体成功
            assert result["success"] is True

            # 验证无质量警告
            assert len(result.get("quality_warnings", [])) == 0

            # 验证未生成JSON
            assert result.get("error_summary_json") is None

    @pytest.mark.asyncio
    async def test_execute_quality_gates_system_error(self):
        """测试系统错误场景"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        with patch.object(orchestrator, 'execute_ruff_agent', new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": False,
                "error": "System error",
                "duration": 5.0,
            }

            result = await orchestrator.execute_quality_gates("test-epic")

            # 验证整体失败
            assert result["success"] is False

            # 验证有系统错误
            assert len(result["errors"]) > 0

            # 验证无质量警告
            assert len(result.get("quality_warnings", [])) == 0

            # 验证未生成JSON
            assert result.get("error_summary_json") is None


class TestQualityGateOrchestratorPhase状态:
    """测试phase状态映射"""

    @pytest.mark.asyncio
    async def test_ruff_max_cycles_phase_status_completed(self):
        """测试Ruff超限时phase状态为completed"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock QualityCheckController返回超限结果
        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.QualityCheckController') as MockController:
            mock_controller = MockController.return_value
            mock_controller.run = AsyncMock(return_value={
                "status": "failed",
                "tool": "ruff",
                "cycles": 3,
                "max_cycles": 3,
                "final_error_files": ["file1.py"],
            })

            result = await orchestrator.execute_ruff_agent("src")

            # 超限场景返回success=True
            assert result["success"] is True
            assert "warning" in result

            # 验证phase状态为completed
            assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "completed"


class Test质量警告数据结构:
    """测试质量警告的数据结构"""

    def test_quality_warning_structure(self):
        """测试质量警告的数据结构"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # 模拟收集到的质量警告
        warnings = [
            {
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "status": "max_cycles_exceeded",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["file1.py", "file2.py"],
            }
        ]

        # 写入JSON
        json_path = orchestrator._write_error_summary_json("test-epic", warnings)

        # 验证结构
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["tools"][0]["status"] == "max_cycles_exceeded"
        assert data["tools"][0]["cycles"] == 3
        assert data["tools"][0]["max_cycles"] == 3
        assert len(data["tools"][0]["remaining_files"]) == 2

        # 清理
        os.unlink(json_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

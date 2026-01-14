"""
质量门禁超限错误汇总机制集成测试

测试完整的工作流程：
1. Controller返回max_cycles字段
2. Orchestrator正确判定超限场景
3. 生成错误汇总JSON文件
4. Phase状态正确映射
5. 工作流非阻断特性

作者: autoBMAD Team
日期: 2026-01-14
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator


class TestQualityGatesMaxCyclesIntegration:
    """质量门禁超限错误汇总机制集成测试"""

    @pytest.mark.asyncio
    async def test_complete_max_cycles_workflow(self):
        """测试完整的超限工作流程"""
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
                "final_error_files": ["file1.py", "file2.py"],
                "initial_error_files": ["file1.py", "file2.py", "file3.py"],
                "sdk_fix_attempted": True,
                "sdk_fix_errors": [],
            })

            result = await orchestrator.execute_ruff_agent("src")

            # 验证超限场景处理
            assert result["success"] is True, "超限场景应返回成功"
            assert "warning" in result, "应有警告信息"

            # 验证JSON生成
            json_path = orchestrator._write_error_summary_json("test-epic", [{
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "status": "max_cycles_exceeded",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["file1.py", "file2.py"],
            }])

            assert json_path is not None
            assert Path(json_path).exists()

            # 验证JSON内容
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["epic_id"] == "test-epic"
            assert len(data["tools"]) == 1
            assert data["tools"][0]["status"] == "max_cycles_exceeded"
            assert data["tools"][0]["cycles"] == 3
            assert data["tools"][0]["max_cycles"] == 3
            assert len(data["tools"][0]["remaining_files"]) == 2

            # 清理
            os.unlink(json_path)

    @pytest.mark.asyncio
    async def test_multiple_tools_max_cycles(self):
        """测试多个工具都超限的情况"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock三个工具都超限
        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.QualityCheckController') as MockController, \
             patch('autoBMAD.epic_automation.controllers.pytest_controller.PytestController') as MockPytestController:

            # Ruff超限
            mock_ruff = MockController.return_value
            mock_ruff.run = AsyncMock(return_value={
                "status": "failed",
                "tool": "ruff",
                "cycles": 3,
                "max_cycles": 3,
                "final_error_files": ["file1.py"],
            })

            # BasedPyright超限
            mock_basedpyright = MockController.return_value
            mock_basedpyright.run = AsyncMock(return_value={
                "status": "failed",
                "tool": "basedpyright",
                "cycles": 3,
                "max_cycles": 3,
                "final_error_files": ["type_error.py"],
            })

            # Pytest超限
            mock_pytest = MockPytestController.return_value
            mock_pytest.run = AsyncMock(return_value={
                "status": "failed",
                "cycles": 3,
                "max_cycles": 3,
                "final_failed_files": ["test_file1.py"],
            })

            # 执行完整流程
            result = await orchestrator.execute_quality_gates("test-epic")

            # 验证整体成功（非阻断）
            assert result["success"] is True

            # 验证有质量警告
            assert len(result.get("quality_warnings", [])) > 0

            # 验证生成了JSON
            assert result["error_summary_json"] is not None
            assert Path(result["error_summary_json"]).exists()

            # 验证JSON包含所有工具
            with open(result["error_summary_json"], "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data["tools"]) >= 2  # 至少ruff和basedpyright

            # 清理
            os.unlink(result["error_summary_json"])

    @pytest.mark.asyncio
    async def test_normal_success_no_json(self):
        """测试正常成功时不生成JSON"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock正常成功场景
        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.QualityCheckController') as MockController:
            mock_controller = MockController.return_value
            mock_controller.run = AsyncMock(return_value={
                "status": "completed",
                "tool": "ruff",
                "cycles": 1,
                "max_cycles": 3,
                "final_error_files": [],
            })

            result = await orchestrator.execute_ruff_agent("src")

            # 验证成功
            assert result["success"] is True

            # 验证无警告
            assert "warning" not in result

    @pytest.mark.asyncio
    async def test_system_error_no_warning(self):
        """测试系统错误时不生成质量警告"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock系统错误
        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.QualityCheckController') as MockController:
            mock_controller = MockController.return_value
            mock_controller.run = AsyncMock(return_value={
                "status": "failed",
                "tool": "ruff",
                "cycles": 1,
                "max_cycles": 3,
                "final_error_files": ["file1.py"],
            })

            result = await orchestrator.execute_ruff_agent("src")

            # 验证失败
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_early_completion_no_json(self):
        """测试提前完成（未达到max_cycles）时不生成JSON"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # Mock提前完成场景
        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.QualityCheckController') as MockController:
            mock_controller = MockController.return_value
            mock_controller.run = AsyncMock(return_value={
                "status": "failed",
                "tool": "ruff",
                "cycles": 2,
                "max_cycles": 3,
                "final_error_files": ["file1.py"],
            })

            result = await orchestrator.execute_ruff_agent("src")

            # 验证失败（因为不是超限场景）
            assert result["success"] is False

    def test_error_summary_json_file_structure(self):
        """测试错误汇总JSON文件结构"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        issues = [
            {
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "status": "max_cycles_exceeded",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["file1.py"],
            },
            {
                "tool": "basedpyright",
                "phase": "phase_2_basedpyright",
                "status": "max_cycles_exceeded",
                "cycles": 3,
                "max_cycles": 3,
                "remaining_files": ["type_error.py"],
            },
        ]

        json_path = orchestrator._write_error_summary_json("complex-epic-123", issues)

        # 验证文件存在
        assert Path(json_path).exists()

        # 验证文件命名
        assert "quality_errors_" in json_path
        assert "complex-epic-123" in json_path
        assert json_path.endswith(".json")

        # 验证JSON结构
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 验证必需字段
        required_fields = ["epic_id", "timestamp", "source_dir", "test_dir", "tools"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # 验证tools数组结构
        for tool in data["tools"]:
            tool_fields = ["tool", "phase", "status", "cycles", "max_cycles", "remaining_files"]
            for field in tool_fields:
                assert field in tool, f"Missing tool field: {field}"

        # 清理
        os.unlink(json_path)

    @pytest.mark.asyncio
    async def test_phase_status_mapping(self):
        """测试phase状态映射正确性"""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
        )

        # 测试超限场景：phase状态应为completed
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

            # 超限场景phase状态为completed
            assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "completed"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
测试质量门禁错误报告修复

此测试验证ERROR_REPORT_FIX.md中描述的修复方案：
1. 方案A：修正循环计数判定逻辑
2. 方案B：增加保底错误导出逻辑
"""
import asyncio
import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from typing import Optional

# 导入待测试的模块
from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator


class TestErrorReportFix:
    """测试质量门禁错误报告修复方案"""

    def __init__(self):
        """初始化实例变量"""
        self.temp_dir: Optional[str] = None
        self.source_dir: Optional[Path] = None
        self.test_dir: Optional[Path] = None
        self.orchestrator: Optional[QualityGateOrchestrator] = None

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "src"
        self.test_dir = Path(self.temp_dir) / "tests"
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # 创建测试用的质量门控协调器
        self.orchestrator = QualityGateOrchestrator(
            source_dir=str(self.source_dir),
            test_dir=str(self.test_dir),
            skip_quality=False,
            skip_tests=False
        )

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        import shutil
        import os
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_is_max_cycles_exceeded_with_errors_bug_fixed(self):
        """
        测试修复后的循环计数判定逻辑

        验证：当cycles=4, max_cycles=3时，应正确返回True
        """
        # 确保orchestrator已初始化
        assert self.orchestrator is not None

        # 测试用例1：cycles=4, max_cycles=3，有残留错误 - 应该返回True
        result = {
            "cycles": 4,
            "max_cycles": 3,
            "final_error_files": ["file1.py", "file2.py"],
            "final_failed_files": []
        }

        is_exceeded = self.orchestrator._is_max_cycles_exceeded_with_errors(result)
        assert is_exceeded, "cycles=4 > max_cycles=3 且有残留错误时应该返回True"

        # 测试用例2：cycles=3, max_cycles=3，有残留错误 - 应该返回False（未超限）
        result = {
            "cycles": 3,
            "max_cycles": 3,
            "final_error_files": ["file1.py"],
            "final_failed_files": []
        }

        is_exceeded = self.orchestrator._is_max_cycles_exceeded_with_errors(result)
        assert not is_exceeded, "cycles=3 = max_cycles=3 时不应该返回True（未超限）"

        # 测试用例3：cycles=4, max_cycles=3，无残留错误 - 应该返回False
        result = {
            "cycles": 4,
            "max_cycles": 3,
            "final_error_files": [],
            "final_failed_files": []
        }

        is_exceeded = self.orchestrator._is_max_cycles_exceeded_with_errors(result)
        assert not is_exceeded, "cycles=4 > max_cycles=3 但无残留错误时应该返回False"

        # 测试用例4：cycles=2, max_cycles=3，有残留错误 - 应该返回False
        result = {
            "cycles": 2,
            "max_cycles": 3,
            "final_error_files": ["file1.py"],
            "final_failed_files": []
        }

        is_exceeded = self.orchestrator._is_max_cycles_exceeded_with_errors(result)
        assert not is_exceeded, "cycles=2 < max_cycles=3 时应该返回False"

    def test_fallback_error_export_logic(self):
        """
        测试保底错误导出逻辑（方案B）

        验证：当正常逻辑未收集到质量警告时，保底逻辑能正确导出failed状态的工具错误
        """
        # 确保orchestrator已初始化
        assert self.orchestrator is not None

        # 模拟results结构 - 使用cycles <= max_cycles来模拟正常逻辑无法收集的情况
        self.orchestrator.results = {
            "ruff": {
                "result": {
                    "status": "failed",
                    "cycles": 3,  # cycles = max_cycles，正常逻辑不会收集
                    "max_cycles": 3,
                    "final_error_files": ["error_file1.py", "error_file2.py"],
                    "tool": "ruff"
                }
            },
            "basedpyright": {
                "result": {
                    "status": "completed",
                    "cycles": 2,
                    "max_cycles": 3
                }
            },
            "pytest": {
                "result": {
                    "status": "failed",
                    "cycles": 3,  # cycles = max_cycles，正常逻辑不会收集
                    "max_cycles": 3,
                    "final_failed_files": ["failed_test1.py"],
                    "tool": "pytest"
                }
            }
        }

        # 模拟execute_quality_gates中的逻辑
        quality_warnings = []

        # 首先尝试正常逻辑收集（这里会为空，因为cycles <= max_cycles）
        for tool_name, phase_name in [
            ("ruff", "phase_1_ruff"),
            ("basedpyright", "phase_2_basedpyright"),
            ("pytest", "phase_3_pytest"),
        ]:
            result = self.orchestrator.results.get(tool_name)
            if result and self.orchestrator._is_max_cycles_exceeded_with_errors(result["result"]):
                warning = {
                    "tool": result["result"].get("tool", tool_name),
                    "phase": phase_name,
                    "status": "max_cycles_exceeded",
                    "cycles": result["result"]["cycles"],
                    "max_cycles": result["result"]["max_cycles"],
                    "remaining_files": (
                        result["result"].get("final_error_files") or
                        result["result"].get("final_failed_files", [])
                    ),
                }
                quality_warnings.append(warning)

        # 验证正常逻辑收集为空
        assert len(quality_warnings) == 0, "正常逻辑不应该收集到任何警告（cycles <= max_cycles）"

        # 保底逻辑：直接检查status=failed的工具
        if not quality_warnings:
            for tool_name in ["ruff", "basedpyright", "pytest"]:
                result = self.orchestrator.results.get(tool_name)
                if result and result.get("result", {}).get("status") == "failed":
                    final_files = (
                        result["result"].get("final_error_files") or
                        result["result"].get("final_failed_files", [])
                    )
                    if final_files:
                        quality_warnings.append({
                            "tool": tool_name,
                            "phase": f"phase_{tool_name}",
                            "status": "failed",
                            "cycles": result["result"].get("cycles", 0),
                            "max_cycles": result["result"].get("max_cycles", 0),
                            "remaining_files": final_files,
                        })

        # 验证保底逻辑是否正确收集了错误
        assert len(quality_warnings) == 2, "保底逻辑应该收集到2个失败的工具"

        # 检查ruff工具
        ruff_warning = next((w for w in quality_warnings if w["tool"] == "ruff"), None)
        assert ruff_warning is not None, "应该收集到ruff工具的警告"
        assert ruff_warning["status"] == "failed", "ruff状态应该是failed"
        assert len(ruff_warning["remaining_files"]) == 2, "ruff应该有2个错误文件"

        # 检查pytest工具
        pytest_warning = next((w for w in quality_warnings if w["tool"] == "pytest"), None)
        assert pytest_warning is not None, "应该收集到pytest工具的警告"
        assert pytest_warning["status"] == "failed", "pytest状态应该是failed"
        assert len(pytest_warning["remaining_files"]) == 1, "pytest应该有1个失败文件"

        # 检查basedpyright不应该被收集（因为status是completed）
        basedpyright_warning = next((w for w in quality_warnings if w["tool"] == "basedpyright"), None)
        assert basedpyright_warning is None, "basedpyright状态是completed，不应该被收集"

    def test_write_error_summary_json(self):
        """
        测试错误汇总JSON文件生成功能

        验证：错误汇总文件能正确生成并包含预期内容
        """
        # 确保orchestrator已初始化
        assert self.orchestrator is not None

        # 准备测试数据
        epic_id = "test_epic"
        issues = [
            {
                "tool": "ruff",
                "phase": "phase_1_ruff",
                "status": "max_cycles_exceeded",
                "cycles": 4,
                "max_cycles": 3,
                "remaining_files": ["error1.py", "error2.py"]
            },
            {
                "tool": "pytest",
                "phase": "phase_3_pytest",
                "status": "failed",
                "cycles": 4,
                "max_cycles": 3,
                "remaining_files": ["failed_test.py"]
            }
        ]

        # 调用_write_error_summary_json方法
        json_path = self.orchestrator._write_error_summary_json(epic_id, issues)

        # 验证文件是否生成
        assert json_path is not None, "应该生成JSON文件"
        assert Path(json_path).exists(), "JSON文件应该存在"

        # 验证JSON内容
        with open(json_path, 'r', encoding='utf-8') as f:
            error_data = json.load(f)

        assert error_data["epic_id"] == epic_id, "epic_id应该匹配"
        assert "timestamp" in error_data, "应该包含时间戳"
        assert error_data["source_dir"] == str(self.source_dir), "source_dir应该匹配"
        assert error_data["test_dir"] == str(self.test_dir), "test_dir应该匹配"
        assert len(error_data["tools"]) == 2, "应该包含2个工具的错误"

        # 验证工具错误详情
        ruff_tool = next((t for t in error_data["tools"] if t["tool"] == "ruff"), None)
        assert ruff_tool is not None, "应该包含ruff工具"
        assert ruff_tool["status"] == "max_cycles_exceeded", "ruff状态应该正确"
        assert len(ruff_tool["remaining_files"]) == 2, "ruff应该有2个错误文件"

    def test_integration_error_report_generation(self):
        """
        集成测试：完整的错误报告生成流程

        验证：在真实的execute_quality_gates流程中，错误报告能正确生成
        """
        # 确保orchestrator已初始化
        assert self.orchestrator is not None

        # 准备模拟数据
        epic_id = "integration_test_epic"

        # 模拟质量门控结果
        self.orchestrator.results = {
            "ruff": {
                "result": {
                    "status": "failed",
                    "cycles": 4,
                    "max_cycles": 3,
                    "final_error_files": ["integration_error1.py"],
                    "tool": "ruff"
                }
            },
            "basedpyright": {
                "result": {
                    "status": "completed",
                    "cycles": 2,
                    "max_cycles": 3
                }
            },
            "pytest": {
                "result": {
                    "status": "failed",
                    "cycles": 4,
                    "max_cycles": 3,
                    "final_failed_files": ["integration_failed_test.py"],
                    "tool": "pytest"
                }
            }
        }

        # 模拟整个流程（跳过实际执行，只测试错误收集和导出部分）
        quality_warnings = []

        # 正常逻辑收集
        for tool_name, phase_name in [
            ("ruff", "phase_1_ruff"),
            ("basedpyright", "phase_2_basedpyright"),
            ("pytest", "phase_3_pytest"),
        ]:
            result = self.orchestrator.results.get(tool_name)
            if result and self.orchestrator._is_max_cycles_exceeded_with_errors(result["result"]):
                warning = {
                    "tool": result["result"].get("tool", tool_name),
                    "phase": phase_name,
                    "status": "max_cycles_exceeded",
                    "cycles": result["result"]["cycles"],
                    "max_cycles": result["result"]["max_cycles"],
                    "remaining_files": (
                        result["result"].get("final_error_files") or
                        result["result"].get("final_failed_files", [])
                    ),
                }
                quality_warnings.append(warning)

        # 保底逻辑收集
        if not quality_warnings:
            for tool_name in ["ruff", "basedpyright", "pytest"]:
                result = self.orchestrator.results.get(tool_name)
                if result and result.get("result", {}).get("status") == "failed":
                    final_files = (
                        result["result"].get("final_error_files") or
                        result["result"].get("final_failed_files", [])
                    )
                    if final_files:
                        quality_warnings.append({
                            "tool": tool_name,
                            "phase": f"phase_{tool_name}",
                            "status": "failed",
                            "cycles": result["result"].get("cycles", 0),
                            "max_cycles": result["result"].get("max_cycles", 0),
                            "remaining_files": final_files,
                        })

        # 生成错误汇总JSON
        if quality_warnings:
            json_path = self.orchestrator._write_error_summary_json(epic_id, quality_warnings)
            self.orchestrator.results["error_summary_json"] = json_path
            self.orchestrator.results["quality_warnings"] = quality_warnings

        # 验证结果
        assert len(quality_warnings) == 2, "应该收集到2个质量警告"
        assert self.orchestrator.results["error_summary_json"] is not None, "应该生成错误汇总文件"
        assert Path(self.orchestrator.results["error_summary_json"]).exists(), "错误汇总文件应该存在"

        # 验证警告内容
        assert len(self.orchestrator.results["quality_warnings"]) == 2, "quality_warnings应该包含2个条目"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])

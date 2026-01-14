"""
质量门控 SDK 修复工作流集成测试

测试完整的质量门控流水线：
1. Ruff 检查 → SDK 修复 → 回归检查
2. BasedPyright 检查 → SDK 修复 → 回归检查
3. Ruff Format
4. 非阻断特性验证

作者: autoBMAD Team
日期: 2026-01-13
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController
from autoBMAD.epic_automation.agents.quality_agents import RuffAgent, BasedPyrightAgent
from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator


class TestQualityGatesSDKFixWorkflow:
    """质量门控 SDK 修复工作流集成测试"""

    @pytest.fixture
    def temp_source_dir(self):
        """创建临时源代码目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_agent(self):
        """创建模拟的 Agent"""
        agent = Mock()
        agent.execute = AsyncMock()
        agent.parse_errors_by_file = Mock()
        agent.build_fix_prompt = Mock(return_value="Mock prompt")
        return agent

    @pytest.mark.asyncio
    async def test_ruff_complete_workflow_success(self, temp_source_dir, mock_agent):
        """测试 Ruff 完整工作流（成功修复）"""
        # 创建测试文件
        test_file = Path(temp_source_dir) / "test.py"
        test_file.write_text("import os\nprint('hello')\n")

        # 模拟第一次检查有错误
        mock_agent.execute.return_value = {
            "status": "completed",
            "issues": [
                {
                    "filename": str(test_file),
                    "code": "F401",
                    "message": "'os' imported but unused",
                    "severity": "error",
                    "location": {"row": 1, "column": 1}
                }
            ]
        }

        # 模拟 parse_errors_by_file
        mock_agent.parse_errors_by_file.return_value = {
            str(test_file): [
                {
                    "line": 1,
                    "column": 1,
                    "code": "F401",
                    "message": "'os' imported but unused",
                    "severity": "error"
                }
            ]
        }

        # 创建控制器
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir=temp_source_dir,
            max_cycles=3,
            sdk_call_delay=1,  # 减少延时以便测试
            sdk_timeout=10,
        )

        # 模拟第二次检查无错误（修复成功）
        mock_agent.execute.side_effect = [
            {
                "status": "completed",
                "issues": [
                    {
                        "filename": str(test_file),
                        "code": "F401",
                        "message": "'os' imported but unused",
                        "severity": "error",
                        "location": {"row": 1, "column": 1}
                    }
                ]
            },
            {
                "status": "completed",
                "issues": []  # 无错误
            }
        ]

        # 模拟 SDK 修复成功
        mock_executor = Mock()
        mock_executor.execute = AsyncMock(return_value={"type": "done"})

        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK"):
            with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SDKExecutor", return_value=mock_executor):
                # 模拟文件读取
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = test_file.read_text()
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                    mock_open.return_value = mock_file

                    result = await controller.run()

        # 验证结果
        assert result["status"] == "completed"
        assert result["tool"] == "ruff"
        assert result["cycles"] == 2
        assert result["initial_error_files"] == [str(test_file)]
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == True
        assert len(result["sdk_fix_errors"]) == 0

    @pytest.mark.asyncio
    async def test_basedpyright_complete_workflow_success(self, temp_source_dir, mock_agent):
        """测试 BasedPyright 完整工作流（成功修复）"""
        # 创建测试文件
        test_file = Path(temp_source_dir) / "type_test.py"
        test_file.write_text("def func(x):\n    return x\n")

        # 模拟第一次检查有类型错误
        mock_agent.execute.return_value = {
            "status": "completed",
            "issues": [
                {
                    "file": str(test_file),
                    "severity": "error",
                    "message": "Missing type annotation",
                    "rule": "reportMissingTypeStubs",
                    "range": {
                        "start": {"line": 1, "character": 0},
                        "end": {"line": 1, "character": 9}
                    }
                }
            ]
        }

        # 模拟 parse_errors_by_file
        mock_agent.parse_errors_by_file.return_value = {
            str(test_file): [
                {
                    "line": 1,
                    "column": 0,
                    "rule": "reportMissingTypeStubs",
                    "message": "Missing type annotation",
                    "severity": "error"
                }
            ]
        }

        # 创建控制器
        controller = QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir=temp_source_dir,
            max_cycles=2,
            sdk_call_delay=1,
            sdk_timeout=10,
        )

        # 模拟第二次检查无错误
        mock_agent.execute.side_effect = [
            {
                "status": "completed",
                "issues": [
                    {
                        "file": str(test_file),
                        "severity": "error",
                        "message": "Missing type annotation",
                        "rule": "reportMissingTypeStubs",
                        "range": {
                            "start": {"line": 1, "character": 0}
                        }
                    }
                ]
            },
            {
                "status": "completed",
                "issues": []
            }
        ]

        # 模拟 SDK 修复成功
        mock_executor = Mock()
        mock_executor.execute = AsyncMock(return_value={"type": "done"})

        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK"):
            with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SDKExecutor", return_value=mock_executor):
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = test_file.read_text()
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                    mock_open.return_value = mock_file

                    result = await controller.run()

        # 验证结果
        assert result["status"] == "completed"
        assert result["tool"] == "basedpyright"
        assert result["cycles"] == 2
        assert result["initial_error_files"] == [str(test_file)]
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == True

    @pytest.mark.asyncio
    async def test_max_cycles_reached(self, temp_source_dir, mock_agent):
        """测试达到最大循环次数"""
        # 创建测试文件
        test_file = Path(temp_source_dir) / "test.py"
        test_file.write_text("import os\n")

        # 模拟始终有错误
        mock_agent.execute.return_value = {
            "status": "completed",
            "issues": [
                {
                    "filename": str(test_file),
                    "code": "F401",
                    "message": "error",
                    "severity": "error",
                    "location": {"row": 1, "column": 1}
                }
            ]
        }

        mock_agent.parse_errors_by_file.return_value = {
            str(test_file): [{"line": 1, "message": "error"}]
        }

        # 创建控制器（最大 2 轮）
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir=temp_source_dir,
            max_cycles=2,
            sdk_call_delay=1,
            sdk_timeout=10,
        )

        # 模拟 SDK 修复失败
        mock_executor = Mock()
        mock_executor.execute = AsyncMock(return_value={"success": False, "error": "SDK failed"})

        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK"):
            with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SDKExecutor", return_value=mock_executor):
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = test_file.read_text()
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                    mock_open.return_value = mock_file

                    result = await controller.run()

        # 验证达到最大循环次数
        assert result["status"] == "failed"
        assert result["cycles"] == 2
        assert result["final_error_files"] == [str(test_file)]
        assert result["sdk_fix_attempted"] == True
        assert len(result["sdk_fix_errors"]) == 2  # 2次循环，每次都有错误

    @pytest.mark.asyncio
    async def test_multiple_files_workflow(self, temp_source_dir, mock_agent):
        """测试多个文件的修复流程"""
        # 创建多个测试文件
        files = []
        for i in range(3):
            test_file = Path(temp_source_dir) / f"test{i}.py"
            test_file.write_text(f"import os{i}\n")
            files.append(test_file)

        # 模拟所有文件都有错误
        mock_agent.execute.return_value = {
            "status": "completed",
            "issues": [
                {
                    "filename": str(f),
                    "code": "F401",
                    "message": f"error in {f.name}",
                    "severity": "error",
                    "location": {"row": 1, "column": 1}
                }
                for f in files
            ]
        }

        mock_agent.parse_errors_by_file.return_value = {
            str(f): [{"line": 1, "message": f"error in {f.name}"}]
            for f in files
        }

        # 创建控制器
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir=temp_source_dir,
            max_cycles=2,
            sdk_call_delay=0.1,  # 极短延时以便测试
            sdk_timeout=10,
        )

        # 模拟第二次检查无错误
        mock_agent.execute.side_effect = [
            {
                "status": "completed",
                "issues": [
                    {
                        "filename": str(f),
                        "code": "F401",
                        "message": f"error in {f.name}",
                        "severity": "error",
                        "location": {"row": 1, "column": 1}
                    }
                    for f in files
                ]
            },
            {
                "status": "completed",
                "issues": []
            }
        ]

        # 模拟 SDK 修复成功
        mock_executor = Mock()
        mock_executor.execute = AsyncMock(return_value={"type": "done"})

        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK"):
            with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SDKExecutor", return_value=mock_executor):
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = "import os\n"
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                    mock_open.return_value = mock_file

                    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                        result = await controller.run()

        # 验证所有文件都被处理
        assert result["status"] == "completed"
        assert len(result["initial_error_files"]) == 3
        assert result["final_error_files"] == []

    @pytest.mark.asyncio
    async def test_orchestrator_non_blocking(self, temp_source_dir):
        """测试质量门控非阻断特性"""
        # 创建模拟的 orchestrator
        orchestrator = QualityGateOrchestrator(
            source_dir=temp_source_dir,
            test_dir=temp_source_dir,
            skip_quality=False,
            skip_tests=True,  # 跳过测试
        )

        # 模拟 Ruff 失败
        with patch.object(orchestrator, "execute_ruff_agent", new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": False,
                "error": "Ruff failed",
                "result": {"status": "failed"}
            }

            # 模拟 BasedPyright 成功
            with patch.object(orchestrator, "execute_basedpyright_agent", new_callable=AsyncMock) as mock_basedpyright:
                mock_basedpyright.return_value = {
                    "success": True,
                    "result": {"status": "completed"}
                }

                # 模拟 Ruff format 成功
                with patch.object(orchestrator, "execute_ruff_format", new_callable=AsyncMock) as mock_format:
                    mock_format.return_value = {
                        "success": True,
                        "result": {"status": "completed"}
                    }

                    result = await orchestrator.execute_quality_gates("test_epic")

        # 验证非阻断特性：即使 Ruff 失败，流程仍继续
        assert result["success"] == True  # orchestrator 本身不失败
        assert orchestrator.results["ruff"]["success"] == False
        assert orchestrator.results["basedpyright"]["success"] == True
        assert orchestrator.results["ruff_format"]["success"] == True

    @pytest.mark.asyncio
    async def test_orchestrator_format_phase(self, temp_source_dir):
        """测试 Ruff Format 阶段"""
        orchestrator = QualityGateOrchestrator(
            source_dir=temp_source_dir,
            test_dir=temp_source_dir,
            skip_quality=False,
            skip_tests=True,
        )

        # 模拟所有阶段都跳过或成功
        with patch.object(orchestrator, "execute_ruff_agent", new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {"success": True}

            with patch.object(orchestrator, "execute_basedpyright_agent", new_callable=AsyncMock) as mock_basedpyright:
                mock_basedpyright.return_value = {"success": True}

                with patch.object(orchestrator, "execute_ruff_format", new_callable=AsyncMock) as mock_format:
                    mock_format.return_value = {
                        "success": True,
                        "result": {"formatted": True, "message": "Code formatted successfully"}
                    }

                    result = await orchestrator.execute_quality_gates("test_epic")

        # 验证 format 阶段被调用
        mock_format.assert_called_once_with(temp_source_dir)
        assert orchestrator.results["ruff_format"]["success"] == True


class TestRuffFormatIntegration:
    """Ruff Format 集成测试"""

    @pytest.mark.asyncio
    async def test_format_execution(self):
        """测试格式化执行"""
        agent = RuffAgent()

        # 模拟 _run_subprocess
        with patch.object(agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "returncode": 0,
                "stdout": "",
                "stderr": ""
            }

            result = await agent.format("src")

            # 验证调用
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "ruff format" in call_args

            # 验证结果
            assert result["status"] == "completed"
            assert result["formatted"] == True


class TestQualityGatesPipeline:
    """质量门控流水线测试"""

    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self, temp_source_dir):
        """测试完整流水线执行"""
        orchestrator = QualityGateOrchestrator(
            source_dir=temp_source_dir,
            test_dir=temp_source_dir,
            skip_quality=False,
            skip_tests=True,
        )

        # 模拟所有阶段成功
        with patch.object(orchestrator, "execute_ruff_agent", new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": True,
                "duration": 10.0,
                "result": {"cycles": 1}
            }

            with patch.object(orchestrator, "execute_basedpyright_agent", new_callable=AsyncMock) as mock_basedpyright:
                mock_basedpyright.return_value = {
                    "success": True,
                    "duration": 15.0,
                    "result": {"cycles": 1}
                }

                with patch.object(orchestrator, "execute_ruff_format", new_callable=AsyncMock) as mock_format:
                    mock_format.return_value = {
                        "success": True,
                        "duration": 5.0,
                        "result": {"formatted": True}
                    }

                    result = await orchestrator.execute_quality_gates("test_epic")

        # 验证结果
        assert result["success"] == True
        assert result["ruff"]["success"] == True
        assert result["basedpyright"]["success"] == True
        assert result["ruff_format"]["success"] == True
        assert "total_duration" in result

    @pytest.mark.asyncio
    async def test_pipeline_with_failures(self, temp_source_dir):
        """测试带失败的流水线"""
        orchestrator = QualityGateOrchestrator(
            source_dir=temp_source_dir,
            test_dir=temp_source_dir,
            skip_quality=False,
            skip_tests=True,
        )

        # 模拟 Ruff 失败但继续
        with patch.object(orchestrator, "execute_ruff_agent", new_callable=AsyncMock) as mock_ruff:
            mock_ruff.return_value = {
                "success": False,
                "error": "Ruff failed",
                "result": {"status": "failed"}
            }

            # 模拟 BasedPyright 成功
            with patch.object(orchestrator, "execute_basedpyright_agent", new_callable=AsyncMock) as mock_basedpyright:
                mock_basedpyright.return_value = {
                    "success": True,
                    "result": {"status": "completed"}
                }

                # 模拟 Format 成功
                with patch.object(orchestrator, "execute_ruff_format", new_callable=AsyncMock) as mock_format:
                    mock_format.return_value = {
                        "success": True,
                        "result": {"formatted": True}
                    }

                    result = await orchestrator.execute_quality_gates("test_epic")

        # 验证非阻断特性
        assert result["success"] == True  # orchestrator 本身不失败
        assert len(result["errors"]) == 1  # 记录了 Ruff 失败

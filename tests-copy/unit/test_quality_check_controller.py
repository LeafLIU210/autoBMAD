"""
QualityCheckController 单元测试

测试质量检查控制器的完整功能：
1. 初始化和配置
2. 检查 → SDK修复 → 回归循环
3. 错误分组和处理
4. 循环终止条件

作者: autoBMAD Team
日期: 2026-01-13
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController


class TestQualityCheckController:
    """QualityCheckController 单元测试"""

    @pytest.fixture
    def mock_agent(self):
        """创建模拟的 Agent"""
        agent = Mock()
        agent.execute = AsyncMock()
        agent.parse_errors_by_file = Mock()
        agent.build_fix_prompt = Mock(return_value="Mock prompt")
        return agent

    @pytest.fixture
    def controller(self, mock_agent):
        """创建 QualityCheckController 实例"""
        return QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir="src",
            max_cycles=3,
            sdk_call_delay=60,
            sdk_timeout=600,
        )

    def test_initialization(self, controller):
        """测试初始化"""
        assert controller.tool == "ruff"
        assert controller.source_dir == "src"
        assert controller.max_cycles == 3
        assert controller.sdk_call_delay == 60
        assert controller.sdk_timeout == 600
        assert controller.current_cycle == 0
        assert controller.error_files == {}
        assert controller.initial_error_files == []
        assert controller.final_error_files == []
        assert controller.sdk_fix_errors == []

    @pytest.mark.asyncio
    async def test_run_no_errors(self, controller):
        """测试无错误情况"""
        # 模拟检查阶段返回空错误
        controller._run_check_phase = AsyncMock(return_value={})

        result = await controller.run()

        assert result["status"] == "completed"
        assert result["tool"] == "ruff"
        assert result["cycles"] == 1
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == False
        assert result["sdk_fix_errors"] == []

    @pytest.mark.asyncio
    async def test_run_with_errors_success(self, controller):
        """测试有错误但成功修复的情况"""
        # 模拟第一次检查有错误
        controller._run_check_phase = AsyncMock(return_value={
            "file1.py": [{"line": 1, "message": "error"}]
        })

        # 模拟第二次检查无错误（修复成功）
        controller._run_check_phase.side_effect = [
            {"file1.py": [{"line": 1, "message": "error"}]},  # 第一次检查
            {}  # 第二次检查 - 无错误
        ]

        # 模拟 SDK 修复
        controller._execute_sdk_fix = AsyncMock(return_value={"success": True})

        # 模拟文件读取
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "file content"
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=False)
            mock_open.return_value = mock_file

            result = await controller.run()

        assert result["status"] == "completed"
        assert result["cycles"] == 2
        assert result["initial_error_files"] == ["file1.py"]
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == True
        assert len(result["sdk_fix_errors"]) == 0

    @pytest.mark.asyncio
    async def test_run_with_errors_failure(self, controller):
        """测试有错误且修复失败的情况"""
        # 模拟检查阶段始终有错误
        controller._run_check_phase = AsyncMock(return_value={
            "file1.py": [{"line": 1, "message": "error"}]
        })

        # 设置最大循环为3次
        controller.max_cycles = 3

        # 模拟 SDK 修复失败
        controller._execute_sdk_fix = AsyncMock(return_value={"success": False, "error": "SDK failed"})

        # 模拟文件读取
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "file content"
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=False)
            mock_open.return_value = mock_file

            result = await controller.run()

        assert result["status"] == "failed"
        # 注意：current_cycle 在循环后会自增，所以实际值是 max_cycles + 1
        assert result["cycles"] == 4  # 达到最大循环次数后自增
        assert result["initial_error_files"] == ["file1.py"]
        assert result["final_error_files"] == ["file1.py"]
        assert result["sdk_fix_attempted"] == True
        assert len(result["sdk_fix_errors"]) == 3  # 3次循环，每次都有错误

    @pytest.mark.asyncio
    async def test_run_check_phase_error(self, controller):
        """测试检查阶段出错的情况"""
        # 模拟检查阶段抛出异常
        controller._run_check_phase = AsyncMock(side_effect=Exception("Check failed"))

        result = await controller.run()

        assert result["status"] == "completed"
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == False

    @pytest.mark.asyncio
    async def test_run_sdk_fix_phase_with_read_error(self, controller):
        """测试 SDK 修复阶段文件读取错误"""
        # 模拟检查阶段有错误
        controller._run_check_phase = AsyncMock(return_value={
            "nonexistent.py": [{"line": 1, "message": "error"}]
        })

        # 模拟文件读取失败
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            controller._run_sdk_fix_phase({
                "nonexistent.py": [{"line": 1, "message": "error"}]
            })

        assert len(controller.sdk_fix_errors) == 1
        assert "File read error" in controller.sdk_fix_errors[0]["error"]

    @pytest.mark.asyncio
    async def test_run_sdk_fix_phase_multiple_files(self, controller):
        """测试 SDK 修复阶段处理多个文件"""
        # 模拟检查阶段有多个错误文件
        controller._run_check_phase = AsyncMock(return_value={
            "file1.py": [{"line": 1, "message": "error1"}],
            "file2.py": [{"line": 2, "message": "error2"}],
            "file3.py": [{"line": 3, "message": "error3"}]
        })

        # 模拟所有 SDK 调用成功
        controller._execute_sdk_fix = AsyncMock(return_value={"success": True})

        # 模拟文件读取
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "file content"
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=False)
            mock_open.return_value = mock_file

            # 模拟延时
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await controller._run_sdk_fix_phase({
                    "file1.py": [{"line": 1, "message": "error1"}],
                    "file2.py": [{"line": 2, "message": "error2"}],
                    "file3.py": [{"line": 3, "message": "error3"}]
                })

        # 验证每个文件都被处理
        assert controller._execute_sdk_fix.call_count == 3
        assert len(controller.sdk_fix_errors) == 0

    @pytest.mark.asyncio
    async def test_execute_sdk_fix_success(self, controller):
        """测试 SDK 调用成功"""
        # 模拟 SafeClaudeSDK 和 SDKExecutor
        mock_sdk = Mock()
        mock_sdk.execute = AsyncMock()

        mock_executor = Mock()
        mock_executor.execute = AsyncMock(return_value={"type": "done"})

        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK", return_value=mock_sdk):
            with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SDKExecutor", return_value=mock_executor):
                result = await controller._execute_sdk_fix("test prompt", "test.py")

        assert result["success"] == True
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_sdk_fix_failure(self, controller):
        """测试 SDK 调用失败"""
        # 模拟 SDK 抛出异常
        with patch("autoBMAD.epic_automation.controllers.quality_check_controller.SafeClaudeSDK") as mock_sdk:
            mock_sdk.side_effect = Exception("SDK error")

            result = await controller._execute_sdk_fix("test prompt", "test.py")

        assert result["success"] == False
        assert "SDK error" in result["error"]

    def test_build_success_result(self, controller):
        """测试构造成功结果"""
        controller.current_cycle = 1

        result = controller._build_success_result()

        assert result["status"] == "completed"
        assert result["tool"] == "ruff"
        assert result["cycles"] == 1
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == []
        assert result["sdk_fix_attempted"] == False
        assert result["sdk_fix_errors"] == []

    def test_build_final_result_success(self, controller):
        """测试构造最终结果（成功）"""
        controller.current_cycle = 2
        controller.final_error_files = []

        result = controller._build_final_result()

        assert result["status"] == "completed"
        assert result["cycles"] == 2
        assert result["sdk_fix_attempted"] == True

    def test_build_final_result_failure(self, controller):
        """测试构造最终结果（失败）"""
        controller.current_cycle = 3
        controller.final_error_files = ["file1.py", "file2.py"]

        result = controller._build_final_result()

        assert result["status"] == "failed"
        assert result["cycles"] == 3
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == ["file1.py", "file2.py"]
        assert result["sdk_fix_attempted"] == True
        assert len(result["sdk_fix_errors"]) == 0

    @pytest.mark.parametrize("tool_name", ["ruff", "basedpyright"])
    def test_tool_parameter(self, mock_agent, tool_name):
        """测试工具参数"""
        controller = QualityCheckController(
            tool=tool_name,
            agent=mock_agent,
            source_dir="src",
        )

        assert controller.tool == tool_name


class TestQualityCheckControllerBasedPyright:
    """BasedPyright 专用测试"""

    @pytest.fixture
    def mock_agent(self):
        """创建模拟的 BasedPyright Agent"""
        agent = Mock()
        agent.execute = AsyncMock()
        agent.parse_errors_by_file = Mock()
        agent.build_fix_prompt = Mock(return_value="Mock prompt")
        return agent

    @pytest.mark.asyncio
    async def test_basedpyright_run(self, mock_agent):
        """测试 BasedPyright 流程"""
        controller = QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir="src",
            max_cycles=2,
        )

        # 模拟检查阶段返回错误
        controller._run_check_phase = AsyncMock(return_value={
            "type_error.py": [{"line": 10, "rule": "reportGeneralTypeIssues"}]
        })

        # 模拟第二次检查无错误
        controller._run_check_phase.side_effect = [
            {"type_error.py": [{"line": 10, "rule": "reportGeneralTypeIssues"}]},  # 第一次检查
            {}  # 第二次检查
        ]

        # 模拟 SDK 修复成功
        controller._execute_sdk_fix = AsyncMock(return_value={"success": True})

        # 模拟文件读取
        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "file content"
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=False)
            mock_open.return_value = mock_file

            result = await controller.run()

        assert result["tool"] == "basedpyright"
        assert result["cycles"] == 2
        assert result["sdk_fix_attempted"] == True

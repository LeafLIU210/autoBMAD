"""
QualityCheckController Comprehensive Test Suite

Tests for QualityCheckController including:
- Initialization
- Check phase execution
- SDK fix phase execution
- Result building
- Cycle management
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, mock_open
import tempfile
from pathlib import Path

from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController
from autoBMAD.epic_automation.agents.quality_agents import BaseQualityAgent


class MockQualityAgent(BaseQualityAgent):
    """Mock quality agent for testing"""

    def __init__(self):
        self.executed = False
        self.parse_errors_called = False

    async def execute(self, source_dir: str):
        self.executed = True
        return {
            "status": "completed",
            "issues": [
                {"file": "src/test.py", "line": 1, "message": "Error 1", "code": "E001"},
                {"file": "src/test.py", "line": 2, "message": "Error 2", "code": "E002"}
            ]
        }

    def parse_errors_by_file(self, issues):
        self.parse_errors_called = True
        return {
            "src/test.py": [
                {"line": 1, "message": "Error 1", "code": "E001"},
                {"line": 2, "message": "Error 2", "code": "E002"}
            ]
        }

    def build_fix_prompt(self, tool: str, file_path: str, file_content: str, errors):
        return f"Fix {len(errors)} errors in {file_path}"


class TestQualityCheckController:
    """Test suite for QualityCheckController"""

    def test_init_ruff(self):
        """测试Ruff工具初始化"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src",
            max_cycles=5
        )

        assert controller.tool == "ruff"
        assert controller.agent == agent
        assert controller.source_dir == "src"
        assert controller.max_cycles == 5
        assert controller.sdk_call_delay == 60
        assert controller.sdk_timeout == 600
        assert controller.current_cycle == 0

    def test_init_basedpyright(self):
        """测试BasedPyright工具初始化"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="basedpyright",
            agent=agent,
            source_dir="src",
            max_cycles=3,
            sdk_call_delay=30,
            sdk_timeout=300
        )

        assert controller.tool == "basedpyright"
        assert controller.sdk_call_delay == 30
        assert controller.sdk_timeout == 300

    @pytest.mark.anyio
    async def test_run_no_errors(self):
        """测试无错误的成功场景"""
        agent = MockQualityAgent()
        # Override to return no issues
        agent.execute = AsyncMock(return_value={
            "status": "completed",
            "issues": []
        })

        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        result = await controller.run()

        assert result["status"] == "completed"
        assert result["tool"] == "ruff"
        assert result["cycles"] == 1
        assert result["sdk_fix_attempted"] is False
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == []

    @pytest.mark.anyio
    async def test_run_with_errors_and_recovery(self):
        """测试有错误但能恢复的场景"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src",
            max_cycles=2
        )

        # First call has errors, second call has none
        agent.execute = AsyncMock(side_effect=[
            {
                "status": "completed",
                "issues": [
                    {"file": "src/test.py", "line": 1, "message": "Error", "code": "E001"}
                ]
            },
            {
                "status": "completed",
                "issues": []
            }
        ])

        with patch.object(controller, '_execute_sdk_fix') as mock_sdk:
            mock_sdk.return_value = {"success": True}

            result = await controller.run()

            assert result["status"] == "completed"
            assert result["cycles"] == 2
            assert len(result["initial_error_files"]) == 1
            assert len(result["final_error_files"]) == 0

    @pytest.mark.anyio
    async def test_run_max_cycles_reached(self):
        """测试达到最大循环次数"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src",
            max_cycles=2
        )

        # Always return errors
        agent.execute = AsyncMock(return_value={
            "status": "completed",
            "issues": [
                {"file": "src/test.py", "line": 1, "message": "Error", "code": "E001"}
            ]
        })

        with patch.object(controller, '_execute_sdk_fix') as mock_sdk:
            mock_sdk.return_value = {"success": True}

            result = await controller.run()

            assert result["status"] == "failed"
            assert result["cycles"] == 2
            assert len(result["final_error_files"]) == 1

    @pytest.mark.anyio
    async def test_run_check_failed(self):
        """测试检查阶段失败"""
        agent = MockQualityAgent()
        agent.execute = AsyncMock(return_value={
            "status": "failed",
            "error": "Check failed"
        })

        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        result = await controller.run()

        assert result["status"] == "completed"  # Still completes, just with no errors
        assert result["initial_error_files"] == []

    @pytest.mark.anyio
    async def test_run_check_exception(self):
        """测试检查阶段异常"""
        agent = MockQualityAgent()
        agent.execute = AsyncMock(side_effect=Exception("Check error"))

        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        result = await controller.run()

        # Should complete even with exception
        assert result["status"] == "completed"
        assert result["initial_error_files"] == []

    @pytest.mark.anyio
    async def test_run_sdk_fix_phase(self):
        """测试SDK修复阶段"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        error_files = {
            "src/test1.py": [{"line": 1, "code": "E001"}],
            "src/test2.py": [{"line": 2, "code": "E002"}]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir).src = Path(tmpdir) / "src"
            Path(tmpdir).src.mkdir()
            (Path(tmpdir).src / "test1.py").write_text("# test1")
            (Path(tmpdir).src / "test2.py").write_text("# test2")

            controller.source_dir = str(Path(tmpdir).src)

            with patch.object(controller, '_execute_sdk_fix') as mock_sdk:
                mock_sdk.return_value = {"success": True}

                await controller._run_sdk_fix_phase(error_files)

                # Should be called twice (once per file)
                assert mock_sdk.call_count == 2

    @pytest.mark.anyio
    async def test_run_sdk_fix_phase_file_read_error(self):
        """测试SDK修复阶段文件读取错误"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="nonexistent"
        )

        error_files = {
            "nonexistent/test.py": [{"line": 1, "code": "E001"}]
        }

        await controller._run_sdk_fix_phase(error_files)

        # Should record error but not crash
        assert len(controller.sdk_fix_errors) == 1
        assert "File read error" in controller.sdk_fix_errors[0]["error"]

    @pytest.mark.anyio
    async def test_execute_sdk_fix_success(self):
        """测试SDK修复执行成功"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        # Mock the SDK helper
        mock_sdk_result = Mock()
        mock_sdk_result.is_success = Mock(return_value=True)
        mock_sdk_result.duration_seconds = 5.0

        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.execute_sdk_call') as mock_call:
            mock_call.return_value = mock_sdk_result

            result = await controller._execute_sdk_fix("test prompt", "test.py")

            assert result["success"] is True
            assert result["duration"] == 5.0

    @pytest.mark.anyio
    async def test_execute_sdk_fix_failure(self):
        """测试SDK修复执行失败"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        # Mock the SDK helper
        mock_sdk_result = Mock()
        mock_sdk_result.is_success = Mock(return_value=False)
        mock_sdk_result.error_type.value = "timeout"
        mock_sdk_result.errors = ["SDK timeout"]

        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.execute_sdk_call') as mock_call:
            mock_call.return_value = mock_sdk_result

            result = await controller._execute_sdk_fix("test prompt", "test.py")

            assert result["success"] is False
            assert "timeout" in result["error"]

    @pytest.mark.anyio
    async def test_execute_sdk_fix_exception(self):
        """测试SDK修复执行异常"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )

        with patch('autoBMAD.epic_automation.controllers.quality_check_controller.execute_sdk_call') as mock_call:
            mock_call.side_effect = Exception("SDK error")

            result = await controller._execute_sdk_fix("test prompt", "test.py")

            assert result["success"] is False
            assert "SDK error" in result["error"]

    @pytest.mark.anyio
    async def test_sdk_fix_delay_between_calls(self):
        """测试SDK调用间的延时"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src",
            sdk_call_delay=1
        )

        error_files = {
            "src/test1.py": [{"line": 1, "code": "E001"}],
            "src/test2.py": [{"line": 2, "code": "E002"}]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).src = Path(tmpdir) / "src"
            Path(tmpdir).src.mkdir()
            (Path(tmpdir).src / "test1.py").write_text("# test1")
            (Path(tmpdir).src / "test2.py").write_text("# test2")

            controller.source_dir = str(Path(tmpdir).src)

            with patch.object(controller, '_execute_sdk_fix') as mock_sdk:
                mock_sdk.return_value = {"success": True}
                with patch('asyncio.sleep') as mock_sleep:
                    await controller._run_sdk_fix_phase(error_files)

                    # Should call sleep between files
                    assert mock_sleep.called

    def test_build_success_result(self):
        """测试构建成功结果"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )
        controller.current_cycle = 1

        result = controller._build_success_result()

        assert result["status"] == "completed"
        assert result["tool"] == "ruff"
        assert result["cycles"] == 1
        assert result["sdk_fix_attempted"] is False
        assert result["initial_error_files"] == []
        assert result["final_error_files"] == []

    def test_build_final_result_success(self):
        """测试构建最终结果 - 成功"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="basedpyright",
            agent=agent,
            source_dir="src"
        )
        controller.current_cycle = 2
        controller.final_error_files = []

        result = controller._build_final_result()

        assert result["status"] == "completed"
        assert result["tool"] == "basedpyright"
        assert len(result["final_error_files"]) == 0

    def test_build_final_result_failure(self):
        """测试构建最终结果 - 失败"""
        agent = MockQualityAgent()
        controller = QualityCheckController(
            tool="ruff",
            agent=agent,
            source_dir="src"
        )
        controller.current_cycle = 3
        controller.final_error_files = ["src/test.py"]

        result = controller._build_final_result()

        assert result["status"] == "failed"
        assert len(result["final_error_files"]) == 1

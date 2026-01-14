"""
QualityController Comprehensive Test Suite

Tests for QualityController including:
- Initialization
- Quality gate execution
- Ruff, BasedPyright, Pytest integration
- Overall status evaluation
- Error handling
"""
import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.epic_automation.controllers.quality_controller import QualityController


class TestQualityController:
    """Test suite for QualityController"""

    @pytest.mark.anyio
    async def test_init_default(self):
        """测试默认初始化"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            assert controller.task_group is tg
            assert controller.project_root is None
            assert controller.ruff_agent is not None
            assert controller.pyright_agent is not None
            assert controller.pytest_agent is not None

    @pytest.mark.anyio
    async def test_init_with_project_root(self):
        """测试带项目根目录的初始化"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)

                controller = QualityController(tg, project_root=project_root)

                assert controller.project_root == project_root

    @pytest.mark.anyio
    async def test_execute_all_checks_pass(self):
        """测试所有检查都通过的场景"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            # Mock all agents to return successful results
            controller.ruff_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pyright_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pytest_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })

            result = await controller.execute()

            assert result["overall_status"] == "pass"
            assert "checks" in result
            assert "ruff" in result["checks"]
            assert "pyright" in result["checks"]
            assert "pytest" in result["checks"]

    @pytest.mark.anyio
    async def test_execute_with_warnings(self):
        """测试有警告但无错误的场景"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            # Mock agents with warnings
            controller.ruff_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 5
            })
            controller.pyright_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pytest_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })

            result = await controller.execute()

            assert result["overall_status"] == "pass_with_warnings"

    @pytest.mark.anyio
    async def test_execute_with_errors(self):
        """测试有错误的场景"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            # Mock agents with errors
            controller.ruff_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 3,
                "warnings": 0
            })
            controller.pyright_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pytest_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })

            result = await controller.execute()

            assert result["overall_status"] == "fail"

    @pytest.mark.anyio
    async def test_execute_with_source_and_test_dirs(self):
        """测试指定源码和测试目录"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            with tempfile.TemporaryDirectory() as tmpdir:
                source_dir = Path(tmpdir) / "src"
                test_dir = Path(tmpdir) / "tests"
                source_dir.mkdir()
                test_dir.mkdir()

                controller.ruff_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })
                controller.pyright_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })
                controller.pytest_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })

                result = await controller.execute(
                    source_dir=str(source_dir),
                    test_dir=str(test_dir)
                )

                assert result["overall_status"] == "pass"

    @pytest.mark.anyio
    async def test_execute_no_source_dir_specified(self):
        """测试未指定源码目录的情况"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            result = await controller.execute()

            assert result["overall_status"] == "error"
            assert "No source directory specified" in result["error"]

    @pytest.mark.anyio
    async def test_execute_with_project_root(self):
        """测试使用项目根目录"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                src_dir = project_root / "src"
                tests_dir = project_root / "tests"
                src_dir.mkdir()
                tests_dir.mkdir()

                controller = QualityController(tg, project_root=project_root)

                controller.ruff_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })
                controller.pyright_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })
                controller.pytest_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })

                result = await controller.execute()

                assert result["overall_status"] == "pass"

    @pytest.mark.anyio
    async def test_execute_no_test_dir(self):
        """测试没有测试目录的场景"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                src_dir = project_root / "src"
                src_dir.mkdir()

                controller = QualityController(tg, project_root=project_root)

                controller.ruff_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })
                controller.pyright_agent.execute = AsyncMock(return_value={
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0
                })

                result = await controller.execute()

                # Should skip pytest
                assert "pytest" in result["checks"]
                assert result["checks"]["pytest"]["status"] == "skipped"
                assert "No test directory provided" in result["checks"]["pytest"]["message"]

    @pytest.mark.anyio
    async def test_execute_exception_handling(self):
        """测试异常处理"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            # Mock Ruff to raise exception
            controller.ruff_agent.execute = AsyncMock(side_effect=Exception("Test error"))

            result = await controller.execute()

            assert result["overall_status"] == "error"
            assert "Test error" in result["error"]

    @pytest.mark.anyio
    async def test_execute_uses_taskgroup(self):
        """测试使用TaskGroup执行"""
        async with anyio.create_task_group() as tg:
            controller = QualityController(tg)

            controller.ruff_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pyright_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })
            controller.pytest_agent.execute = AsyncMock(return_value={
                "status": "completed",
                "errors": 0,
                "warnings": 0
            })

            result = await controller.execute()

            # Verify execute_within_taskgroup was called
            assert controller.ruff_agent.execute.called
            assert controller.pyright_agent.execute.called
            assert controller.pytest_agent.execute.called

    def test_evaluate_overall_status_all_pass(self):
        """测试评估整体状态 - 全部通过"""
        controller = QualityController(Mock())

        checks = {
            "ruff": {"errors": 0, "warnings": 0},
            "pyright": {"errors": 0, "warnings": 0},
            "pytest": {"errors": 0, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "pass"

    def test_evaluate_overall_status_with_warnings(self):
        """测试评估整体状态 - 有警告"""
        controller = QualityController(Mock())

        checks = {
            "ruff": {"errors": 0, "warnings": 5}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "pass_with_warnings"

    def test_evaluate_overall_status_with_errors(self):
        """测试评估整体状态 - 有错误"""
        controller = QualityController(Mock())

        checks = {
            "ruff": {"errors": 3, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "fail"

    def test_evaluate_overall_status_mixed(self):
        """测试评估整体状态 - 混合情况"""
        controller = QualityController(Mock())

        # Mix of pass, warnings, and errors
        checks = {
            "ruff": {"errors": 0, "warnings": 5},
            "pyright": {"errors": 2, "warnings": 0},
            "pytest": {"errors": 0, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        # Errors take precedence
        assert status == "fail"

    def test_evaluate_overall_status_all_warnings(self):
        """测试评估整体状态 - 全部警告"""
        controller = QualityController(Mock())

        checks = {
            "ruff": {"errors": 0, "warnings": 3},
            "pyright": {"errors": 0, "warnings": 2}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "pass_with_warnings"

    def test_evaluate_overall_status_empty_checks(self):
        """测试评估整体状态 - 空检查结果"""
        controller = QualityController(Mock())

        checks = {}

        status = controller._evaluate_overall_status(checks)

        # Empty checks means no errors or warnings
        assert status == "pass"

    def test_evaluate_overall_status_invalid_check_format(self):
        """测试评估整体状态 - 无效检查格式"""
        controller = QualityController(Mock())

        checks = {
            "ruff": "invalid"
        }

        # Should not crash, should be treated as no errors
        status = controller._evaluate_overall_status(checks)

        assert status == "pass"

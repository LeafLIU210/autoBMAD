"""
Quality Controller 单元测试
"""
import pytest
import anyio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from autoBMAD.epic_automation.controllers.quality_controller import QualityController
from autoBMAD.epic_automation.agents.quality_agents import RuffAgent, BasedPyrightAgent, PytestAgent


@pytest.mark.anyio
async def test_quality_controller_init():
    """测试 QualityController 初始化"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        assert controller.task_group is not None
        assert isinstance(controller.ruff_agent, RuffAgent)
        assert isinstance(controller.pyright_agent, BasedPyrightAgent)
        assert isinstance(controller.pytest_agent, PytestAgent)


@pytest.mark.anyio
async def test_execute_quality_gate_success():
    """测试质量门控执行成功"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        # 模拟所有检查都通过
        with patch.object(controller, '_execute_within_taskgroup') as mock_execute:
            mock_execute.side_effect = [
                # Ruff 结果
                {
                    "status": "completed",
                    "errors": 0,
                    "warnings": 2,
                    "files_checked": 10,
                    "message": "Found 2 warnings"
                },
                # BasedPyright 结果
                {
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0,
                    "files_checked": 10,
                    "message": "No type issues found"
                },
                # Pytest 结果
                {
                    "status": "completed",
                    "tests_passed": 50,
                    "tests_failed": 0,
                    "tests_errors": 0,
                    "coverage": 85.5,
                    "total_tests": 50,
                    "message": "50 tests passed"
                }
            ]

            result = await controller.execute()

            assert result["overall_status"] == "pass_with_warnings"
            assert "ruff" in result["checks"]
            assert "pyright" in result["checks"]
            assert "pytest" in result["checks"]


@pytest.mark.anyio
async def test_execute_quality_gate_fail():
    """测试质量门控执行失败"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        # 模拟 Ruff 有错误
        with patch.object(controller, '_execute_within_taskgroup') as mock_execute:
            mock_execute.side_effect = [
                # Ruff 结果（有错误）
                {
                    "status": "completed",
                    "errors": 5,
                    "warnings": 0,
                    "files_checked": 10,
                    "message": "Found 5 errors"
                },
                # BasedPyright 结果
                {
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0,
                    "files_checked": 10,
                    "message": "No type issues found"
                },
                # Pytest 结果
                {
                    "status": "completed",
                    "tests_passed": 50,
                    "tests_failed": 0,
                    "tests_errors": 0,
                    "coverage": 85.5,
                    "total_tests": 50,
                    "message": "50 tests passed"
                }
            ]

            result = await controller.execute()

            assert result["overall_status"] == "fail"
            assert result["checks"]["ruff"]["errors"] == 5


@pytest.mark.anyio
async def test_execute_quality_gate_error():
    """测试质量门控执行异常"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        # 模拟执行异常
        with patch.object(controller, '_execute_within_taskgroup') as mock_execute:
            mock_execute.side_effect = Exception("Test error")

            result = await controller.execute()

            assert result["overall_status"] == "error"
            assert "Test error" in result["error"]


@pytest.mark.anyio
async def test_execute_with_custom_dirs():
    """测试使用自定义目录执行"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        with patch.object(controller, '_execute_within_taskgroup') as mock_execute:
            mock_execute.side_effect = [
                {"status": "completed", "errors": 0, "warnings": 0, "files_checked": 10, "message": "OK"},
                {"status": "completed", "errors": 0, "warnings": 0, "files_checked": 10, "message": "OK"},
                {"status": "completed", "tests_passed": 10, "tests_failed": 0, "tests_errors": 0, "coverage": 90.0, "total_tests": 10, "message": "OK"}
            ]

            result = await controller.execute(
                source_dir="/custom/src",
                test_dir="/custom/tests"
            )

            assert result["overall_status"] == "pass"
            # 验证目录参数传递
            calls = mock_execute.call_args_list
            assert "/custom/src" in str(calls[0])
            assert "/custom/tests" in str(calls[2])


@pytest.mark.anyio
async def test_evaluate_overall_status_all_pass():
    """测试评估状态：全部通过"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        checks = {
            "ruff": {"errors": 0, "warnings": 0},
            "pyright": {"errors": 0, "warnings": 0},
            "pytest": {"errors": 0, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "pass"


@pytest.mark.anyio
async def test_evaluate_overall_status_with_warnings():
    """测试评估状态：有警告但无错误"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        checks = {
            "ruff": {"errors": 0, "warnings": 5},
            "pyright": {"errors": 0, "warnings": 2}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "pass_with_warnings"


@pytest.mark.anyio
async def test_evaluate_overall_status_with_errors():
    """测试评估状态：有错误"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        checks = {
            "ruff": {"errors": 5, "warnings": 0},
            "pyright": {"errors": 0, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "fail"


@pytest.mark.anyio
async def test_evaluate_overall_status_mixed():
    """测试评估状态：混合错误和警告"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        checks = {
            "ruff": {"errors": 3, "warnings": 2},
            "pyright": {"errors": 0, "warnings": 1},
            "pytest": {"errors": 0, "warnings": 0}
        }

        status = controller._evaluate_overall_status(checks)

        assert status == "fail"  # 有错误优先于警告


@pytest.mark.anyio
async def test_evaluate_overall_status_empty():
    """测试评估状态：空结果"""
    async with anyio.create_task_group() as tg:
        controller = QualityController(tg)

        checks = {}

        status = controller._evaluate_overall_status(checks)

        assert status == "pass"  # 默认通过

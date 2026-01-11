"""
控制器与 Agent 集成测试
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import anyio

from autoBMAD.epic_automation.controllers.sm_controller import SMController
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.controllers.quality_controller import QualityController
from autoBMAD.epic_automation.agents.state_agent import StateAgent
from autoBMAD.epic_automation.agents.quality_agents import RuffAgent, BasedPyrightAgent, PytestAgent


@pytest.mark.anyio
async def test_sm_controller_with_sm_agent():
    """测试 SMController 与 SMAgent 的集成"""
    async with anyio.create_task_group() as tg:
        # 创建临时目录
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stories_dir = project_root / "stories"
            stories_dir.mkdir()

            # 创建故事文件
            story_file = stories_dir / "1.1.md"
            story_content = """# Story 1.1: Test Story

**Status**: Draft

## Description
This is a test story for integration testing.
"""
            story_file.write_text(story_content)

            # 初始化控制器
            controller = SMController(tg, project_root=project_root)

            # 模拟 SMAgent 执行
            with patch.object(controller.sm_agent, 'execute', new_callable=AsyncMock) as mock_sm_agent:
                mock_sm_agent.return_value = True

                # 执行 SM 阶段
                result = await controller.execute(
                    epic_content="Test Epic",
                    story_id="1.1"
                )

                assert result is True
                mock_sm_agent.assert_called_once()


@pytest.mark.anyio
async def test_devqa_controller_with_agents():
    """测试 DevQaController 与 Dev/QA Agents 的集成"""
    async with anyio.create_task_group() as tg:
        # 创建临时故事文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Test Story

**Status**: Ready for Development

## Description
Test story for integration testing.
""")
            story_path = f.name

        try:
            # 初始化控制器
            controller = DevQaController(tg, use_claude=False)

            # 模拟状态解析和 Agent 执行
            with patch.object(controller.state_agent, 'parse_status', new_callable=AsyncMock) as mock_parse:
                mock_parse.side_effect = [
                    "Ready for Development",  # 第一次解析：需要开发
                    "Ready for Review",        # 开发后状态
                    "Ready for Done"          # QA 后状态（终止）
                ]

                with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                    with patch.object(controller.qa_agent, 'execute', new_callable=AsyncMock) as mock_qa:
                        mock_dev.return_value = True
                        mock_qa.return_value = True

                        # 执行 Dev-QA 流水线
                        result = await controller.execute(story_path)

                        assert result is True
                        assert mock_dev.call_count >= 1
                        assert mock_qa.call_count >= 1

        finally:
            # 清理临时文件
            Path(story_path).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_quality_controller_with_quality_agents():
    """测试 QualityController 与 Quality Agents 的集成"""
    async with anyio.create_task_group() as tg:
        # 初始化控制器
        controller = QualityController(tg)

        # 模拟质量检查执行
        with patch.object(controller, '_execute_within_taskgroup') as mock_execute:
            mock_execute.side_effect = [
                # Ruff 结果
                {
                    "status": "completed",
                    "errors": 0,
                    "warnings": 2,
                    "files_checked": 10,
                    "message": "2 warnings found"
                },
                # BasedPyright 结果
                {
                    "status": "completed",
                    "errors": 0,
                    "warnings": 0,
                    "files_checked": 10,
                    "message": "No issues"
                },
                # Pytest 结果
                {
                    "status": "completed",
                    "tests_passed": 50,
                    "tests_failed": 0,
                    "tests_errors": 0,
                    "coverage": 85.5,
                    "total_tests": 50,
                    "message": "All tests passed"
                }
            ]

            # 执行质量门控
            result = await controller.execute()

            # 验证结果
            assert result["overall_status"] == "pass_with_warnings"
            assert "checks" in result
            assert "ruff" in result["checks"]
            assert "pyright" in result["checks"]
            assert "pytest" in result["checks"]

            # 验证每个检查项都被调用
            assert mock_execute.call_count == 3


@pytest.mark.anyio
async def test_state_agent_integration():
    """测试 StateAgent 集成"""
    # 创建临时故事文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test Story

**Status**: In Progress

## Description
Test story for state parsing.
""")
        story_path = f.name

    try:
        # 初始化 StateAgent
        state_agent = StateAgent()

        # 模拟状态解析器
        with patch.object(state_agent.status_parser, 'parse_status', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = "In Progress"

            # 解析状态
            status = await state_agent.parse_status(story_path)

            assert status == "In Progress"
            mock_parse.assert_called_once()

            # 获取处理状态
            processing_status = await state_agent.get_processing_status(story_path)

            assert processing_status == "in_progress"

    finally:
        # 清理临时文件
        Path(story_path).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_quality_agents_integration():
    """测试 Quality Agents 集成"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = tmpdir
        test_dir = tmpdir

        # 测试 Ruff Agent
        ruff_agent = RuffAgent()
        with patch.object(ruff_agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "stdout": '[]',
                "stderr": "",
                "returncode": 0,
                "success": True
            }

            result = await ruff_agent.execute(source_dir=source_dir)

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0

        # 测试 BasedPyright Agent
        pyright_agent = BasedPyrightAgent()
        with patch.object(pyright_agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "stdout": '{"generalDiagnostics": []}',
                "stderr": "",
                "returncode": 0,
                "success": True
            }

            result = await pyright_agent.execute(source_dir=source_dir)

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0

        # 测试 Pytest Agent
        pytest_agent = PytestAgent()
        with patch.object(pytest_agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "stdout": "50 passed in 2.50s",
                "stderr": "",
                "returncode": 0,
                "success": True
            }

            result = await pytest_agent.execute(source_dir=source_dir, test_dir=test_dir)

            assert result["status"] == "completed"
            assert result["tests_passed"] == 50
            assert result["tests_failed"] == 0


@pytest.mark.anyio
async def test_taskgroup_isolation():
    """测试 TaskGroup 隔离机制"""
    async with anyio.create_task_group() as outer_tg:
        # 在外层 TaskGroup 中创建控制器
        controller = SMController(outer_tg)

        # 验证控制器有 task_group 引用
        assert controller.task_group is outer_tg

        # 验证 _execute_within_taskgroup 方法存在
        assert hasattr(controller, '_execute_within_taskgroup')
        assert callable(controller._execute_within_taskgroup)


@pytest.mark.anyio
async def test_controller_logging():
    """测试控制器日志记录"""
    import logging
    logging.basicConfig(level=logging.DEBUG)

    async with anyio.create_task_group() as tg:
        # 创建控制器
        controller = SMController(tg)

        # 记录日志（应该不会抛出异常）
        controller._log_execution("Test message")
        controller._log_execution("Warning message", "warning")
        controller._log_execution("Error message", "error")

        # 验证日志被记录
        assert controller.logger is not None

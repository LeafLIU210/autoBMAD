"""
DevQaController 单元测试（最终修复版）

测试 DevQaController 的各种功能：
1. 初始化和依赖注入
2. 状态机循环
3. 状态决策逻辑
4. 错误处理
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.agents.dev_agent import DevAgent
from autoBMAD.epic_automation.agents.qa_agent import QAAgent
from autoBMAD.epic_automation.agents.state_agent import StateAgent


class TestDevQaController:
    """DevQaController 测试类"""

    @pytest.mark.anyio
    async def test_init_basic(self):
        """测试基本初始化"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器
        controller = DevQaController(mock_task_group)

        # 验证初始化
        assert controller.task_group == mock_task_group
        assert controller.dev_agent is not None
        assert controller.qa_agent is not None
        assert controller.state_agent is not None
        assert isinstance(controller.dev_agent, DevAgent)
        assert isinstance(controller.qa_agent, QAAgent)
        assert isinstance(controller.state_agent, StateAgent)
        assert controller.max_rounds == 3
        assert controller._story_path is None

    @pytest.mark.anyio
    async def test_init_with_options(self):
        """测试带选项的初始化"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器
        controller = DevQaController(
            mock_task_group,
            use_claude=False,
            log_manager="test_logger"
        )

        # 验证初始化
        assert controller.task_group == mock_task_group
        assert controller.dev_agent is not None
        assert controller.qa_agent is not None
        assert controller.state_agent is not None

    @pytest.mark.anyio
    async def test_execute_basic(self):
        """测试基本执行"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)

            # 模拟状态机执行
            with patch.object(controller, 'run_state_machine', new_callable=AsyncMock) as mock_run:
                mock_run.return_value = True

                # 测试执行
                result = await controller.execute(str(story_path))

                # 验证结果
                assert result is True
                assert controller._story_path == str(story_path)
                mock_run.assert_called_once()

    @pytest.mark.anyio
    async def test_execute_exception(self):
        """测试执行异常处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)

            # 模拟状态机执行抛出异常
            with patch.object(controller, 'run_state_machine', new_callable=AsyncMock) as mock_run:
                mock_run.side_effect = Exception("Test error")

                # 测试执行
                result = await controller.execute(str(story_path))

                # 验证结果
                assert result is False

    @pytest.mark.anyio
    async def test_run_pipeline(self):
        """测试流水线执行"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)

            # 模拟状态机执行
            with patch.object(controller, 'run_state_machine', new_callable=AsyncMock) as mock_run:
                mock_run.return_value = True

                # 测试执行
                result = await controller.run_pipeline(str(story_path), max_rounds=5)

                # 验证结果
                assert result is True
                # 注意：max_rounds 会在 finally 块中恢复，所以这里不检查

    @pytest.mark.anyio
    async def test_make_decision_no_story_path(self):
        """测试没有故事路径的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器
        controller = DevQaController(mock_task_group, use_claude=False)
        controller._story_path = None

        # 测试决策
        result = await controller._make_decision("Start")

        # 验证结果
        assert result == "Error"

    @pytest.mark.anyio
    async def test_make_decision_parse_status_failed(self):
        """测试状态解析失败的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析返回None
            with patch.object(controller.state_agent, 'execute', return_value=None):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该返回Error）
                assert result == "Error"

    @pytest.mark.anyio
    async def test_make_decision_done_state(self):
        """测试已完成状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Done", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析返回Done
            with patch.object(controller.state_agent, 'execute', return_value="Done"):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该保持Done状态）
                assert result == "Done"

    @pytest.mark.anyio
    async def test_make_decision_ready_for_done_state(self):
        """测试Ready for Done状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Ready for Done", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析返回Ready for Done
            with patch.object(controller.state_agent, 'execute', return_value="Ready for Done"):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该保持Ready for Done状态）
                assert result == "Ready for Done"

    @pytest.mark.anyio
    async def test_make_decision_draft_state(self):
        """测试Draft状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Draft"  # 第一次调用返回Draft
                elif call_count[0] == 2:
                    return "Ready for Review"  # Dev执行后返回Ready for Review
                elif call_count[0] == 3:
                    return "Ready for Done"  # QA执行后返回Ready for Done
                else:
                    return "Done"  # 第四次调用返回Done（终止状态）

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True) as mock_dev:
                    with patch.object(controller.qa_agent, 'execute', return_value=True) as mock_qa:
                        # 测试决策
                        result = await controller._make_decision("Start")

                        # 验证结果（应该返回Done，表示完成整个流程）
                        assert result == "Done"
                        mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_ready_for_development_state(self):
        """测试Ready for Development状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Ready for Development", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Ready for Development"  # 第一次调用
                elif call_count[0] == 2:
                    return "Ready for Review"  # Dev执行后返回Ready for Review
                elif call_count[0] == 3:
                    return "Ready for Done"  # QA执行后返回Ready for Done
                else:
                    return "Done"  # 第四次调用返回Done（终止状态）

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True) as mock_dev:
                    with patch.object(controller.qa_agent, 'execute', return_value=True) as mock_qa:
                        # 测试决策
                        result = await controller._make_decision("Start")

                        # 验证结果
                        assert result == "Done"
                        mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_failed_state(self):
        """测试Failed状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Failed", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Failed"  # 第一次调用
                elif call_count[0] == 2:
                    return "Ready for Review"  # Dev执行后返回Ready for Review
                elif call_count[0] == 3:
                    return "Ready for Done"  # QA执行后返回Ready for Done
                else:
                    return "Done"  # 第四次调用返回Done（终止状态）

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True) as mock_dev:
                    with patch.object(controller.qa_agent, 'execute', return_value=True) as mock_qa:
                        # 测试决策
                        result = await controller._make_decision("Start")

                        # 验证结果
                        assert result == "Done"
                        mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_failed_state_with_logging(self):
        """测试Failed状态的决策（带日志验证）"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Failed", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Failed"  # 第一次调用
                elif call_count[0] == 2:
                    return "Done"  # Dev执行后直接返回Done（表示修复成功）

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True) as mock_dev:
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果
                    assert result == "Done"
                    mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_failed_state_within_max_rounds(self):
        """测试在最大轮数内失败状态的处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Failed", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)
            controller.max_rounds = 2

            # 使用 call_count 来追踪调用次数，但只允许最多2次调用
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                # 只返回2次Failed，第3次抛出异常阻止递归
                if call_count[0] <= 2:
                    return "Failed"
                else:
                    raise RecursionError("Too many calls")

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True):
                    # 测试决策（应该因为达到最大轮数而停止）
                    result = await controller._make_decision("Start")

                    # 验证结果（超过轮数后会返回Failed）
                    assert result == "Failed"

    @pytest.mark.anyio
    async def test_make_decision_in_progress_state(self):
        """测试In Progress状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: In Progress", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "In Progress"  # 第一次调用
                elif call_count[0] == 2:
                    return "Ready for Review"  # Dev执行后返回Ready for Review
                elif call_count[0] == 3:
                    return "Ready for Done"  # QA执行后返回Ready for Done
                else:
                    return "Done"  # 第四次调用返回Done（终止状态）

            # 模拟Dev Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.dev_agent, 'execute', return_value=True) as mock_dev:
                    with patch.object(controller.qa_agent, 'execute', return_value=True) as mock_qa:
                        # 测试决策
                        result = await controller._make_decision("Start")

                        # 验证结果
                        assert result == "Done"
                        mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_ready_for_review_state(self):
        """测试Ready for Review状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Ready for Review", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 使用 call_count 来追踪调用次数
            call_count = [0]

            async def mock_state_agent_execute(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Ready for Review"  # 第一次调用
                elif call_count[0] == 2:
                    return "Ready for Done"  # QA执行后返回Ready for Done
                else:
                    return "Done"  # 第三次调用返回Done（终止状态）

            # 模拟QA Agent执行
            with patch.object(controller.state_agent, 'execute', side_effect=mock_state_agent_execute):
                with patch.object(controller.qa_agent, 'execute', return_value=True) as mock_qa:
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（Ready for Done 是终止状态）
                    assert result == "Ready for Done"
                    mock_qa.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_unknown_state(self):
        """测试未知状态的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Unknown", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析返回未知状态
            with patch.object(controller.state_agent, 'execute', return_value="Unknown"):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该返回Unknown）
                assert result == "Unknown"

    @pytest.mark.anyio
    async def test_make_decision_exception(self):
        """测试决策异常处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析抛出异常
            with patch.object(controller.state_agent, 'execute', side_effect=Exception("Test error")):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该返回Error）
                assert result == "Error"

    @pytest.mark.anyio
    async def test_is_termination_state(self):
        """测试终止状态判断"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器
        controller = DevQaController(mock_task_group, use_claude=False)

        # 验证终止状态
        assert controller._is_termination_state("Done") is True
        assert controller._is_termination_state("Ready for Done") is True
        assert controller._is_termination_state("Error") is True

        # 验证非终止状态
        assert controller._is_termination_state("Draft") is False
        assert controller._is_termination_state("Ready for Development") is False
        assert controller._is_termination_state("In Progress") is False
        assert controller._is_termination_state("Ready for Review") is False
        assert controller._is_termination_state("Failed") is False

"""
DevQaController 单元测试

测试 DevQaController 的各种功能：
1. 初始化和依赖注入
2. 状态机循环
3. 状态决策逻辑
4. 错误处理
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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
            with patch.object(controller, 'run_state_machine', side_effect=Exception("Test error")):
                # 测试执行
                result = await controller.execute(str(story_path))

                # 验证结果（异常应该导致失败）
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

            # 模拟execute方法
            with patch.object(controller, 'execute', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = True

                # 测试流水线执行
                result = await controller.run_pipeline(str(story_path), max_rounds=5)

                # 验证结果
                assert result is True
                mock_execute.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_no_story_path(self):
        """测试没有故事路径时的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器（不设置故事路径）
        controller = DevQaController(mock_task_group, use_claude=False)

        # 测试决策
        result = await controller._make_decision("Start")

        # 验证结果（应该返回Error）
        assert result == "Error"

    @pytest.mark.anyio
    async def test_make_decision_parse_status_failed(self):
        """测试状态解析失败时的决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态解析返回None
            with patch.object(controller.state_agent, 'parse_status', return_value=None):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该返回Failed）
                assert result == "Failed"

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
            with patch.object(controller.state_agent, 'parse_status', return_value="Done"):
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
            with patch.object(controller.state_agent, 'parse_status', return_value="Ready for Done"):
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

            # 模拟Dev Agent执行
            with patch.object(controller.dev_agent, 'execute') as mock_dev:
                async def mock_execute(*args, **kwargs):
                    return True
                mock_dev.side_effect = mock_execute

                # 模拟状态解析返回Draft
                with patch.object(controller.state_agent, 'parse_status', return_value="Draft"):
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（应该调用Dev Agent）
                    assert result == "AfterDev"
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

            # 模拟Dev Agent执行
            with patch.object(controller.dev_agent, 'execute') as mock_dev:
                async def mock_execute(*args, **kwargs):
                    return True
                mock_dev.side_effect = mock_execute

                # 模拟状态解析返回Ready for Development
                with patch.object(controller.state_agent, 'parse_status', return_value="Ready for Development"):
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（应该调用Dev Agent）
                    assert result == "AfterDev"
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

            # 模拟Dev Agent执行
            with patch.object(controller.dev_agent, 'execute') as mock_dev:
                async def mock_execute(*args, **kwargs):
                    return True
                mock_dev.side_effect = mock_execute

                # 模拟状态解析返回Failed
                with patch.object(controller.state_agent, 'parse_status', return_value="Failed"):
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（应该调用Dev Agent）
                    assert result == "AfterDev"
                    mock_dev.assert_called_once_with(str(story_path))

    @pytest.mark.anyio
    async def test_make_decision_failed_state_with_logging(self):
        """测试Failed状态的日志记录和消息"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Failed", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟日志记录
            with patch.object(controller, '_log_execution') as mock_log:
                # 模拟Dev Agent执行
                with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                    mock_dev.return_value = True

                    # 模拟状态解析返回Failed
                    with patch.object(controller.state_agent, 'parse_status', return_value="Failed"):
                        # 执行决策
                        result = await controller._make_decision("Start")

                        # 验证日志记录
                        mock_log.assert_called()
                        # 查找包含"retrying development"的日志调用
                        log_calls = [call.args[0] for call in mock_log.call_args_list]
                        assert any("retrying development" in msg for msg in log_calls)

                        # 验证结果
                        assert result == "AfterDev"

    @pytest.mark.anyio
    async def test_failed_state_within_max_rounds(self):
        """测试Failed状态在最大轮次内的处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Failed", encoding='utf-8')

            # 创建控制器
            controller = DevQaController(mock_task_group, use_claude=False)
            controller._story_path = str(story_path)

            # 模拟状态序列：Failed -> Draft -> Done
            status_sequence = ["Failed", "Draft", "Done"]
            status_index = 0

            async def mock_parse_status(path):
                nonlocal status_index
                if status_index < len(status_sequence):
                    status = status_sequence[status_index]
                    status_index += 1
                    return status
                return "Done"

            # 模拟Dev Agent执行
            with patch.object(controller.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev:
                mock_dev.return_value = True

                # 模拟状态解析
                with patch.object(controller.state_agent, 'parse_status', side_effect=mock_parse_status):
                    # 运行状态机
                    result = await controller.run_state_machine("Start", max_rounds=3)

                    # 验证结果
                    assert result is True
                    assert status_index == 3  # 应该经过3个状态

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

            # 模拟Dev Agent执行
            with patch.object(controller.dev_agent, 'execute') as mock_dev:
                async def mock_execute(*args, **kwargs):
                    return True
                mock_dev.side_effect = mock_execute

                # 模拟状态解析返回In Progress
                with patch.object(controller.state_agent, 'parse_status', return_value="In Progress"):
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（应该调用Dev Agent）
                    assert result == "AfterDev"
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

            # 模拟QA Agent执行
            with patch.object(controller.qa_agent, 'execute') as mock_qa:
                async def mock_execute(*args, **kwargs):
                    return True
                mock_qa.side_effect = mock_execute

                # 模拟状态解析返回Ready for Review
                with patch.object(controller.state_agent, 'parse_status', return_value="Ready for Review"):
                    # 测试决策
                    result = await controller._make_decision("Start")

                    # 验证结果（应该调用QA Agent）
                    assert result == "AfterQA"
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
            with patch.object(controller.state_agent, 'parse_status', return_value="UnknownState"):
                # 测试决策
                result = await controller._make_decision("Start")

                # 验证结果（应该返回原始状态）
                assert result == "UnknownState"

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
            with patch.object(controller.state_agent, 'parse_status', side_effect=Exception("Test error")):
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
        controller = DevQaController(mock_task_group)

        # 测试终止状态
        assert controller._is_termination_state("Done") is True
        assert controller._is_termination_state("Ready for Done") is True
        assert controller._is_termination_state("Error") is True

        # 测试非终止状态
        assert controller._is_termination_state("Failed") is False
        assert controller._is_termination_state("Draft") is False
        assert controller._is_termination_state("Ready for Development") is False
        assert controller._is_termination_state("In Progress") is False
        assert controller._is_termination_state("Ready for Review") is False
        assert controller._is_termination_state("Start") is False
        assert controller._is_termination_state("AfterDev") is False
        assert controller._is_termination_state("AfterQA") is False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])

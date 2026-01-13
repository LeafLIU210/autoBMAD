"""
SMController 单元测试

测试 SMController 的各种功能：
1. 初始化和依赖注入
2. 故事内容验证
3. 状态解析集成
4. 错误处理
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.controllers.sm_controller import SMController
from autoBMAD.epic_automation.agents.sm_agent import SMAgent
from autoBMAD.epic_automation.agents.state_agent import StateAgent


class TestSMController:
    """SMController 测试类"""

    @pytest.mark.anyio
    async def test_init_basic(self):
        """测试基本初始化"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        # 创建控制器
        controller = SMController(mock_task_group)

        # 验证初始化
        assert controller.task_group == mock_task_group
        assert controller.sm_agent is not None
        assert controller.state_agent is not None
        assert isinstance(controller.sm_agent, SMAgent)
        assert isinstance(controller.state_agent, StateAgent)

    @pytest.mark.anyio
    async def test_init_with_project_root(self):
        """测试带项目根目录的初始化"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 验证初始化
            assert controller.project_root == project_root
            assert controller.sm_agent is not None
            assert controller.state_agent is not None

    @pytest.mark.anyio
    async def test_build_sm_config(self):
        """测试SM配置构建"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()
        controller = SMController(mock_task_group)

        # 测试配置构建
        config = controller._build_sm_config(
            epic_content="Test Epic",
            story_id="1.1",
            tasks_path="/test/tasks"
        )

        # 验证配置
        assert config["epic_content"] == "Test Epic"
        assert config["story_id"] == "1.1"
        assert config["tasks_path"] == "/test/tasks"

    @pytest.mark.anyio
    async def test_build_sm_config_default(self):
        """测试默认配置构建"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()
        controller = SMController(mock_task_group)

        # 测试默认配置（传入None作为tasks_path）
        config = controller._build_sm_config(
            epic_content="Test Epic",
            story_id="1.1",
            tasks_path=None
        )

        # 验证默认配置
        assert config["epic_content"] == "Test Epic"
        assert config["story_id"] == "1.1"
        assert "tasks" in config["tasks_path"]

    @pytest.mark.anyio
    async def test_find_story_file_exists(self):
        """测试查找存在的故事文件"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            stories_dir = project_root / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            # 创建测试故事文件
            story_file = stories_dir / "1.1.md"
            story_file.write_text("Test story", encoding='utf-8')

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 查找文件
            result = controller._find_story_file("1.1")

            # 验证结果
            assert result == story_file

    @pytest.mark.anyio
    async def test_find_story_file_not_exists(self):
        """测试查找不存在的故事文件"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 查找不存在的文件
            result = controller._find_story_file("999.999")

            # 验证结果
            assert result is None

    @pytest.mark.anyio
    async def test_find_story_file_no_project_root(self):
        """测试没有项目根目录时查找文件"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()
        controller = SMController(mock_task_group)  # 没有project_root

        # 查找文件
        result = controller._find_story_file("1.1")

        # 验证结果
        assert result is None

    @pytest.mark.anyio
    async def test_validate_story_content_success(self):
        """测试成功验证故事内容"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 创建测试故事文件
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Status: Draft\n# Test Story\n\nSome content here", encoding='utf-8')

            # 测试验证
            result = await controller._validate_story_content(story_path)

            # 验证结果
            assert result is True

    @pytest.mark.anyio
    async def test_validate_story_content_short(self):
        """测试内容过短的验证"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 创建过短的故事文件
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("Short", encoding='utf-8')

            # 测试验证
            result = await controller._validate_story_content(story_path)

            # 验证结果（内容过短）
            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_empty(self):
        """测试空内容验证"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 创建空故事文件
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("", encoding='utf-8')

            # 测试验证
            result = await controller._validate_story_content(story_path)

            # 验证结果（空内容）
            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_no_status(self):
        """测试无状态的故事验证"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 创建没有状态的故事文件
            story_path = Path(tmp_dir) / "test.md"
            story_path.write_text("# Test Story\n\nNo status here", encoding='utf-8')

            # 模拟状态解析返回None
            with patch.object(controller.state_agent, 'parse_status', return_value=None):
                # 测试验证
                result = await controller._validate_story_content(story_path)

                # 验证结果 - 无状态故事被允许（新故事）
                assert result is True

    @pytest.mark.anyio
    async def test_validate_story_content_exception(self):
        """测试验证时的异常处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 创建不存在的文件路径（将引发异常）
            story_path = Path(tmp_dir) / "nonexistent.md"

            # 测试验证（应该返回False）
            result = await controller._validate_story_content(story_path)

            # 验证结果
            assert result is False

    @pytest.mark.anyio
    async def test_make_decision(self):
        """测试状态决策"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()
        controller = SMController(mock_task_group)

        # 测试决策
        result = await controller._make_decision("Start")

        # 验证结果
        assert result == "Completed"

    @pytest.mark.anyio
    async def test_execute_success(self):
        """测试成功执行"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            stories_dir = project_root / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            # 创建测试故事文件
            story_file = stories_dir / "1.1.md"
            story_file.write_text("Status: Draft\n# Test Story\n\nContent", encoding='utf-8')

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 模拟SM Agent执行
            with patch.object(controller.sm_agent, 'execute', new_callable=AsyncMock) as mock_execute:
                # 测试执行
                result = await controller.execute(
                    epic_content="Test Epic",
                    story_id="1.1"
                )

                # 验证结果
                assert result is True
                mock_execute.assert_called_once()

    @pytest.mark.anyio
    async def test_execute_no_story_file(self):
        """测试故事文件不存在时的执行"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 模拟SM Agent执行
            with patch.object(controller.sm_agent, 'execute', new_callable=AsyncMock):
                # 测试执行（故事ID不存在）
                result = await controller.execute(
                    epic_content="Test Epic",
                    story_id="999.999"
                )

                # 验证结果
                assert result is False

    @pytest.mark.anyio
    async def test_execute_validation_failed(self):
        """测试验证失败时的执行"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            stories_dir = project_root / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            # 创建短故事文件（将导致验证失败）
            story_file = stories_dir / "1.1.md"
            story_file.write_text("Short", encoding='utf-8')

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 模拟SM Agent执行
            with patch.object(controller.sm_agent, 'execute', new_callable=AsyncMock):
                # 测试执行
                result = await controller.execute(
                    epic_content="Test Epic",
                    story_id="1.1"
                )

                # 验证结果
                assert result is False

    @pytest.mark.anyio
    async def test_execute_exception(self):
        """测试执行时异常处理"""
        # 创建模拟TaskGroup
        mock_task_group = MagicMock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建控制器
            controller = SMController(mock_task_group, project_root)

            # 模拟SM Agent执行抛出异常
            with patch.object(controller.sm_agent, 'execute', side_effect=Exception("Test error")):
                # 测试执行
                result = await controller.execute(
                    epic_content="Test Epic",
                    story_id="1.1"
                )

                # 验证结果（异常应该导致失败）
                assert result is False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])

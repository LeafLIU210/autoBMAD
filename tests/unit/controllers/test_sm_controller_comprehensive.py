"""
SMController Comprehensive Test Suite

Tests for SMController including:
- Initialization
- Story management execution
- File finding
- Content validation
- Error handling
"""
import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.epic_automation.controllers.sm_controller import SMController


class TestSMController:
    """Test suite for SMController"""

    @pytest.mark.anyio
    async def test_init_default(self):
        """测试默认初始化"""
        async with anyio.create_task_group() as tg:
            controller = SMController(tg)

            assert controller.task_group is tg
            assert controller.project_root is None
            assert controller.sm_agent is not None
            assert controller.state_agent is not None

    @pytest.mark.anyio
    async def test_init_with_project_root(self):
        """测试带项目根目录的初始化"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)

                controller = SMController(tg, project_root=project_root)

                assert controller.project_root == project_root

    @pytest.mark.anyio
    async def test_execute_success(self):
        """测试成功执行"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                stories_dir = project_root / "stories"
                stories_dir.mkdir()

                controller = SMController(tg, project_root=project_root)

                # Mock agents
                controller.sm_agent.execute = AsyncMock(return_value=True)

                # Create a valid story file
                story_file = stories_dir / "1.1.md"
                story_file.write_text("# Story 1.1\n\nThis is a test story with sufficient content.\n\nStatus: Draft\n")

                result = await controller.execute(
                    epic_content="Test epic",
                    story_id="1.1"
                )

                assert result is True
                assert controller.sm_agent.execute.called

    @pytest.mark.anyio
    async def test_execute_story_not_found(self):
        """测试故事文件未找到"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)

                controller = SMController(tg, project_root=project_root)

                controller.sm_agent.execute = AsyncMock(return_value=True)

                result = await controller.execute(
                    epic_content="Test epic",
                    story_id="1.1"
                )

                # Should fail because story file doesn't exist
                assert result is False

    @pytest.mark.anyio
    async def test_execute_validation_failure(self):
        """测试验证失败"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                stories_dir = project_root / "stories"
                stories_dir.mkdir()

                controller = SMController(tg, project_root=project_root)

                controller.sm_agent.execute = AsyncMock(return_value=True)

                # Create an empty story file (will fail validation)
                story_file = stories_dir / "1.1.md"
                story_file.write_text("")

                result = await controller.execute(
                    epic_content="Test epic",
                    story_id="1.1"
                )

                assert result is False

    @pytest.mark.anyio
    async def test_execute_sm_agent_failure(self):
        """测试SM Agent执行失败"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)

                controller = SMController(tg, project_root=project_root)

                # Mock SM agent to fail
                controller.sm_agent.execute = AsyncMock(return_value=False)

                result = await controller.execute(
                    epic_content="Test epic",
                    story_id="1.1"
                )

                assert result is False

    @pytest.mark.anyio
    async def test_execute_exception_handling(self):
        """测试异常处理"""
        async with anyio.create_task_group() as tg:
            controller = SMController(tg)

            # Mock to raise exception
            controller.sm_agent.execute = AsyncMock(side_effect=Exception("Test error"))

            result = await controller.execute(
                epic_content="Test epic",
                story_id="1.1"
            )

            assert result is False

    @pytest.mark.anyio
    async def test_execute_with_tasks_path(self):
        """测试带任务路径的执行"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                stories_dir = project_root / "stories"
                stories_dir.mkdir()

                controller = SMController(tg, project_root=project_root)

                controller.sm_agent.execute = AsyncMock(return_value=True)

                # Create valid story
                story_file = stories_dir / "1.1.md"
                story_file.write_text("# Story 1.1\n\nContent here.\n\nStatus: Draft\n")

                result = await controller.execute(
                    epic_content="Test epic",
                    story_id="1.1",
                    tasks_path="/custom/tasks/path"
                )

                assert result is True

    @pytest.mark.anyio
    async def test_execute_no_project_root(self):
        """测试没有项目根目录"""
        async with anyio.create_task_group() as tg:
            controller = SMController(tg)

            controller.sm_agent.execute = AsyncMock(return_value=True)

            result = await controller.execute(
                epic_content="Test epic",
                story_id="1.1"
            )

            # Should fail when trying to find story file
            assert result is False

    def test_build_sm_config(self):
        """测试构建SM配置"""
        controller = SMController(Mock())

        config = controller._build_sm_config(
            epic_content="Test epic",
            story_id="1.1",
            tasks_path="/custom/tasks"
        )

        assert config["epic_content"] == "Test epic"
        assert config["story_id"] == "1.1"
        assert config["tasks_path"] == "/custom/tasks"

    def test_build_sm_config_default_tasks_path(self):
        """测试构建SM配置默认任务路径"""
        controller = SMController(Mock())

        config = controller._build_sm_config(
            epic_content="Test epic",
            story_id="1.1",
            tasks_path=None
        )

        assert config["epic_content"] == "Test epic"
        assert config["story_id"] == "1.1"
        assert "tasks" in config["tasks_path"]

    def test_find_story_file_found(self):
        """测试找到故事文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stories_dir = project_root / "stories"
            stories_dir.mkdir()

            # Create a story file
            story_file = stories_dir / "1.1.md"
            story_file.write_text("test")

            controller = SMController(Mock(), project_root=project_root)

            result = controller._find_story_file("1.1")

            assert result == story_file

    def test_find_story_file_not_found(self):
        """测试未找到故事文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            controller = SMController(Mock(), project_root=project_root)

            result = controller._find_story_file("1.1")

            assert result is None

    def test_find_story_file_no_project_root(self):
        """测试没有项目根目录"""
        controller = SMController(Mock())

        result = controller._find_story_file("1.1")

        assert result is None

    def test_find_story_file_no_stories_dir(self):
        """测试没有故事目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            controller = SMController(Mock(), project_root=project_root)

            result = controller._find_story_file("1.1")

            assert result is None

    @pytest.mark.anyio
    async def test_validate_story_content_valid(self):
        """测试验证故事内容 - 有效"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("# Story\n\nThis is a valid story with sufficient content.\n\nStatus: Draft\n")

            controller = SMController(Mock())

            # Mock state agent to return status
            controller.state_agent.parse_status = AsyncMock(return_value="Draft")

            result = await controller._validate_story_content(story_file)

            assert result is True

    @pytest.mark.anyio
    async def test_validate_story_content_short(self):
        """测试验证故事内容 - 内容太短"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("short")  # Less than 20 chars

            controller = SMController(Mock())

            result = await controller._validate_story_content(story_file)

            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_empty(self):
        """测试验证故事内容 - 空内容"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("")

            controller = SMController(Mock())

            result = await controller._validate_story_content(story_file)

            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_whitespace_only(self):
        """测试验证故事内容 - 仅空白字符"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("   \n\n   \t  \n")

            controller = SMController(Mock())

            result = await controller._validate_story_content(story_file)

            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_no_status(self):
        """测试验证故事内容 - 无状态（新故事）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("# Story\n\nThis is a valid story.\n")

            controller = SMController(Mock())

            # Mock state agent to return None (no status)
            controller.state_agent.parse_status = AsyncMock(return_value=None)

            result = await controller._validate_story_content(story_file)

            # Should allow new stories without status
            assert result is True

    @pytest.mark.anyio
    async def test_validate_story_content_exception(self):
        """测试验证故事内容 - 异常"""
        with tempfile.TemporaryDirectory() as tmpdir:
            story_file = Path(tmpdir) / "story.md"
            story_file.write_text("# Story\n\nContent.\n")

            controller = SMController(Mock())

            # Mock to raise exception
            controller.state_agent.parse_status = AsyncMock(
                side_effect=Exception("Parse error")
            )

            result = await controller._validate_story_content(story_file)

            assert result is False

    @pytest.mark.anyio
    async def test_validate_story_content_file_read_error(self):
        """测试验证故事内容 - 文件读取错误"""
        controller = SMController(Mock())

        # Use non-existent file
        story_file = Path("/nonexistent/story.md")

        result = await controller._validate_story_content(story_file)

        assert result is False

    @pytest.mark.anyio
    async def test_make_decision(self):
        """测试状态决策"""
        async with anyio.create_task_group() as tg:
            controller = SMController(tg)

            result = await controller._make_decision("Start")

            # SM controller returns "Completed" for any state
            assert result == "Completed"

    @pytest.mark.anyio
    async def test_execute_with_valid_content_edge_case(self):
        """测试执行边缘情况 - 正好20字符的内容"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                stories_dir = project_root / "stories"
                stories_dir.mkdir()

                controller = SMController(tg, project_root=project_root)

                controller.sm_agent.execute = AsyncMock(return_value=True)

                # Create a story with exactly 20 characters
                story_file = stories_dir / "1.1.md"
                story_file.write_text("12345678901234567890\n")

                result = await controller._validate_story_content(story_file)

                # 20 characters should pass
                assert result is True

    @pytest.mark.anyio
    async def test_execute_with_valid_content_just_under_limit(self):
        """测试执行边缘情况 - 19字符的内容"""
        async with anyio.create_task_group() as tg:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)
                stories_dir = project_root / "stories"
                stories_dir.mkdir()

                controller = SMController(tg, project_root=project_root)

                # Create a story with 19 characters
                story_file = stories_dir / "1.1.md"
                story_file.write_text("1234567890123456789\n")

                result = await controller._validate_story_content(story_file)

                # 19 characters should fail
                assert result is False

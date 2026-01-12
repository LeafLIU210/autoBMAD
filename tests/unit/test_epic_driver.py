"""
EpicDriver 单元测试

测试 EpicDriver 的核心功能：
1. 初始化和配置
2. Epic 解析
3. 故事处理
4. 状态机流水线
5. 质量门控
6. 错误处理
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver, QualityGateOrchestrator


class TestQualityGateOrchestrator:
    """QualityGateOrchestrator 测试类"""

    @pytest.mark.anyio
    async def test_init(self):
        """测试初始化"""
        orchestrator = QualityGateOrchestrator(use_claude=False)
        assert orchestrator.use_claude is False
        assert orchestrator.skip_quality is False
        assert orchestrator.skip_tests is False

    @pytest.mark.anyio
    async def test_init_with_flags(self):
        """测试带标志的初始化"""
        orchestrator = QualityGateOrchestrator(
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )
        assert orchestrator.use_claude is False
        assert orchestrator.skip_quality is True
        assert orchestrator.skip_tests is True

    @pytest.mark.anyio
    async def test_execute_ruff_agent(self):
        """测试 Ruff Agent 执行"""
        orchestrator = QualityGateOrchestrator(use_claude=False)
        result = await orchestrator.execute_ruff_agent("test_dir")
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.anyio
    async def test_execute_basedpyright_agent(self):
        """测试 BasedPyright Agent 执行"""
        orchestrator = QualityGateOrchestrator(use_claude=False)
        result = await orchestrator.execute_basedpyright_agent("test_dir")
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.anyio
    async def test_execute_pytest_agent(self):
        """测试 Pytest Agent 执行"""
        orchestrator = QualityGateOrchestrator(use_claude=False)
        result = await orchestrator.execute_pytest_agent("test_dir")
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.anyio
    async def test_execute_quality_gates(self):
        """测试质量门控执行"""
        orchestrator = QualityGateOrchestrator(use_claude=False)
        result = await orchestrator.execute_quality_gates("epic_id")
        assert isinstance(result, dict)
        assert "success" in result


class TestEpicDriver:
    """EpicDriver 测试类"""

    @pytest.fixture
    def temp_epic_file(self):
        """创建临时 Epic 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Epic 1: 测试 Epic

## Story 1.1: 测试故事 1
**Status**: Draft
**Description**: 这是一个测试故事

## Story 1.2: 测试故事 2
**Status**: Draft
**Description**: 这是另一个测试故事
""")
            return f.name

    @pytest.mark.anyio
    async def test_init_basic(self, temp_epic_file):
        """测试基本初始化"""
        driver = EpicDriver(temp_epic_file, use_claude=False)

        assert driver.epic_path == Path(temp_epic_file).resolve()
        assert driver.use_claude is False
        assert driver.verbose is False
        assert driver.concurrent is False
        assert driver.max_iterations == 3
        assert driver.retry_failed is False
        assert len(driver.stories) == 0
        assert driver.current_story_index == 0

    @pytest.mark.anyio
    async def test_init_with_options(self, temp_epic_file):
        """测试带选项的初始化"""
        driver = EpicDriver(
            temp_epic_file,
            max_iterations=5,
            retry_failed=True,
            verbose=True,
            concurrent=True,
            use_claude=False,
            skip_quality=True,
            skip_tests=True
        )

        assert driver.max_iterations == 5
        assert driver.retry_failed is True
        assert driver.verbose is True
        assert driver.concurrent is True
        assert driver.use_claude is False
        assert driver.skip_quality is True
        assert driver.skip_tests is True

    @pytest.mark.anyio
    async def test_init_with_custom_paths(self, temp_epic_file):
        """测试自定义路径"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_dir = Path(tmp_dir) / "custom_src"
            test_dir = Path(tmp_dir) / "custom_tests"
            source_dir.mkdir()
            test_dir.mkdir()

            driver = EpicDriver(
                temp_epic_file,
                source_dir=str(source_dir),
                test_dir=str(test_dir),
                use_claude=False
            )

            assert driver.source_dir == str(source_dir.resolve())
            assert driver.test_dir == str(test_dir.resolve())

    @pytest.mark.anyio
    async def test_parse_epic_empty_file(self):
        """测试解析空的 Epic 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Epic 1\n")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            stories = await driver.parse_epic()

            assert isinstance(stories, list)
            assert len(stories) == 0

    @pytest.mark.anyio
    async def test_parse_epic_basic(self, temp_epic_file):
        """测试基本 Epic 解析"""
        driver = EpicDriver(temp_epic_file, use_claude=False)
        stories = await driver.parse_epic()

        assert isinstance(stories, list)
        assert len(stories) == 2
        assert stories[0]["id"] == "1.1"
        assert stories[0]["title"] == "测试故事 1"
        assert stories[0]["status"] == "Draft"
        assert stories[1]["id"] == "1.2"
        assert stories[1]["title"] == "测试故事 2"

    @pytest.mark.anyio
    async def test_parse_epic_with_different_statuses(self):
        """测试解析不同状态的 Epic"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Epic 1: 测试 Epic

## Story 1.1: 故事 1
**Status**: Draft
**Description**: Draft 状态故事

## Story 1.2: 故事 2
**Status**: In Progress
**Description**: In Progress 状态故事

## Story 1.3: 故事 3
**Status**: Done
**Description**: Done 状态故事
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            stories = await driver.parse_epic()

            assert len(stories) == 3
            assert stories[0]["status"] == "Draft"
            assert stories[1]["status"] == "In Progress"
            assert stories[2]["status"] == "Done"

    @pytest.mark.anyio
    async def test_parse_epic_with_complex_formatting(self):
        """测试解析复杂格式的 Epic"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Epic 1: 复杂 Epic

## Story 1.1: 故事 1
**Status**: Draft
**Description**: 这是一个带有**粗体**和*斜体*的故事

### Tasks
- [ ] 任务 1
- [ ] 任务 2

## Story 1.2: 故事 2
**Status**: Ready for Development
**Description**: 另一个故事
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            stories = await driver.parse_epic()

            assert len(stories) == 2
            assert "**粗体**" in stories[0]["description"]
            assert "*斜体*" in stories[0]["description"]

    @pytest.mark.anyio
    async def test_extract_story_ids(self):
        """测试故事 ID 提取"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Epic 1

## Story 1.1: 故事 1

## Story 1.2: 故事 2

## Story 2.1: 故事 3
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            story_ids = driver._extract_story_ids_from_epic()

            assert "1.1" in story_ids
            assert "1.2" in story_ids
            assert "2.1" in story_ids

    @pytest.mark.anyio
    async def test_find_story_file_with_fallback(self):
        """测试故事文件查找与回退"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_dir = Path(tmp_dir) / "epic"
            epic_dir.mkdir()

            # 创建 epic 文件
            epic_file = epic_dir / "epic-1.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            # 创建故事文件
            story_file = epic_dir / "story-1.1.md"
            story_file.write_text("# Story 1.1\n")

            driver = EpicDriver(str(epic_file), use_claude=False)
            found_path = driver._find_story_file_with_fallback("1.1", epic_dir)

            assert found_path == str(story_file)

    @pytest.mark.anyio
    async def test_find_story_file_multiple_patterns(self):
        """测试多种故事文件查找模式"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_dir = Path(tmp_dir) / "epic"
            epic_dir.mkdir()

            epic_file = epic_dir / "epic-1.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            # 创建多个匹配的文件
            story_file1 = epic_dir / "story-1.1.md"
            story_file1.write_text("# Story 1.1\n")

            story_file2 = epic_dir / "1.1.md"
            story_file2.write_text("# Story 1.1\n")

            driver = EpicDriver(str(epic_file), use_claude=False)
            found_path = driver._find_story_file_with_fallback("1.1", epic_dir)

            # 应该找到其中一个文件
            assert found_path in [str(story_file1), str(story_file2)]

    @pytest.mark.anyio
    async def test_parse_story_status(self):
        """测试故事状态解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Story 1.1

**Status**: In Progress

## Description
这是一个测试故事
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            status = await driver._parse_story_status(f.name)

            assert status == "In Progress"

    @pytest.mark.anyio
    async def test_parse_story_status_default(self):
        """测试故事状态解析默认值"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Story 1.1

## Description
这是一个测试故事
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            status = await driver._parse_story_status(f.name)

            assert status == "Draft"

    @pytest.mark.anyio
    async def test_is_story_ready_for_done(self):
        """测试故事完成准备检查"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Story 1.1

**Status**: Done
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            ready = driver._is_story_ready_for_done(f.name)

            assert ready is True

    @pytest.mark.anyio
    async def test_is_story_ready_for_done_not_ready(self):
        """测试故事未准备完成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Story 1.1

**Status**: In Progress
""")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            ready = driver._is_story_ready_for_done(f.name)

            assert ready is False

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.controllers.sm_controller.SMController')
    async def test_execute_sm_phase(self, mock_controller_class):
        """测试 SM 阶段执行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Story 1.1\n\n**Status**: Draft\n")
            f.flush()

            mock_controller = AsyncMock()
            mock_controller_class.return_value = mock_controller
            mock_controller.execute.return_value = True

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.execute_sm_phase(f.name)

            assert result is True

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.controllers.devqa_controller.DevQaController')
    async def test_execute_dev_phase(self, mock_controller_class):
        """测试 Dev 阶段执行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Story 1.1\n\n**Status**: Draft\n")
            f.flush()

            mock_controller = AsyncMock()
            mock_controller_class.return_value = mock_controller
            mock_controller.execute.return_value = True

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.execute_dev_phase(f.name)

            assert result is True

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.controllers.quality_controller.QualityController')
    async def test_execute_qa_phase(self, mock_controller_class):
        """测试 QA 阶段执行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Story 1.1\n\n**Status**: Done\n")
            f.flush()

            mock_controller = AsyncMock()
            mock_controller_class.return_value = mock_controller
            mock_controller.execute.return_value = True

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.execute_qa_phase(f.name)

            assert result is True

    @pytest.mark.anyio
    async def test_process_story_basic(self):
        """测试基本故事处理"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_file = Path(tmp_dir) / "epic.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            story_file = Path(tmp_dir) / "story-1.1.md"
            story_file.write_text("# Story 1.1\n\n**Status**: Draft\n")

            driver = EpicDriver(str(epic_file), use_claude=False)
            driver.stories = [{"id": "1.1", "path": str(story_file)}]

            # Mock 所有阶段
            with patch.object(driver, 'execute_sm_phase', return_value=True), \
                 patch.object(driver, 'execute_dev_phase', return_value=True), \
                 patch.object(driver, 'execute_qa_phase', return_value=True):

                result = await driver.process_story(driver.stories[0])
                assert result is True

    @pytest.mark.anyio
    async def test_process_story_with_retry(self):
        """测试故事处理重试"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_file = Path(tmp_dir) / "epic.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            story_file = Path(tmp_dir) / "story-1.1.md"
            story_file.write_text("# Story 1.1\n\n**Status**: Draft\n")

            driver = EpicDriver(str(epic_file), use_claude=False, retry_failed=True)
            driver.stories = [{"id": "1.1", "path": str(story_file)}]

            # Mock 第一次失败，第二次成功
            with patch.object(driver, 'execute_sm_phase', side_effect=[False, True]), \
                 patch.object(driver, 'execute_dev_phase', return_value=True), \
                 patch.object(driver, 'execute_qa_phase', return_value=True):

                result = await driver.process_story(driver.stories[0])
                assert result is True

    @pytest.mark.anyio
    async def test_process_story_max_iterations(self):
        """测试故事处理最大迭代次数"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_file = Path(tmp_dir) / "epic.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            story_file = Path(tmp_dir) / "story-1.1.md"
            story_file.write_text("# Story 1.1\n\n**Status**: Draft\n")

            driver = EpicDriver(str(epic_file), use_claude=False, retry_failed=True, max_iterations=2)
            driver.stories = [{"id": "1.1", "path": str(story_file)}]

            # Mock 总是失败
            with patch.object(driver, 'execute_sm_phase', return_value=False):
                result = await driver.process_story(driver.stories[0])
                assert result is False

    @pytest.mark.anyio
    async def test_execute_story_processing(self):
        """测试故事处理实现"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            epic_file = Path(tmp_dir) / "epic.md"
            epic_file.write_text("# Epic 1\n\n## Story 1.1\n")

            story_file = Path(tmp_dir) / "story-1.1.md"
            story_file.write_text("# Story 1.1\n\n**Status**: Draft\n")

            driver = EpicDriver(str(epic_file), use_claude=False)
            driver.stories = [{"id": "1.1", "path": str(story_file)}]

            # Mock 所有阶段
            with patch.object(driver, 'execute_sm_phase', return_value=True), \
                 patch.object(driver, 'execute_dev_phase', return_value=True), \
                 patch.object(driver, 'execute_qa_phase', return_value=True):

                result = await driver._execute_story_processing(driver.stories[0])
                assert result is True

    @pytest.mark.anyio
    async def test_initialize_epic_processing(self):
        """测试初始化 Epic 处理"""
        driver = EpicDriver("dummy.md", use_claude=False)
        await driver._initialize_epic_processing(5)

        # 验证日志记录等初始化操作
        assert driver.current_story_index == 0

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.parse_epic')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver._initialize_epic_processing')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.process_story')
    async def test_run_basic(self, mock_process, mock_init, mock_parse):
        """测试基本运行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Epic 1\n\n## Story 1.1\n")
            f.flush()

            mock_parse.return_value = [{"id": "1.1", "path": f.name}]
            mock_process.return_value = True

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.run()

            assert result is True
            mock_init.assert_called_once_with(1)

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.parse_epic')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.process_story')
    async def test_run_multiple_stories(self, mock_process, mock_parse):
        """测试多故事运行"""
        with tempfile.TemporaryFile(mode='w', suffix='.md', delete=False) as f:
            mock_parse.return_value = [
                {"id": "1.1", "path": "path1"},
                {"id": "1.2", "path": "path2"},
                {"id": "1.3", "path": "path3"}
            ]
            mock_process.side_effect = [True, True, True]

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.run()

            assert result is True
            assert mock_process.call_count == 3

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.parse_epic')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.process_story')
    async def test_run_with_failures(self, mock_process, mock_parse):
        """测试运行中的失败处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            mock_parse.return_value = [
                {"id": "1.1", "path": "path1"},
                {"id": "1.2", "path": "path2"}
            ]
            # 第一个故事成功，第二个失败
            mock_process.side_effect = [True, False]

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.run()

            # 即使有失败，也应该返回 True（部分成功）
            assert result is True

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.parse_epic')
    async def test_run_no_stories(self, mock_parse):
        """测试没有故事时的运行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            mock_parse.return_value = []

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.run()

            assert result is True

    @pytest.mark.anyio
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.parse_epic')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver._initialize_epic_processing')
    @patch('autoBMAD.epic_automation.epic_driver.EpicDriver.process_story')
    async def test_run_exception_handling(self, mock_process, mock_init, mock_parse):
        """测试运行异常处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            mock_parse.return_value = [{"id": "1.1", "path": f.name}]
            mock_process.side_effect = Exception("Test error")

            driver = EpicDriver(f.name, use_claude=False)
            result = await driver.run()

            assert result is False

    @pytest.mark.anyio
    async def test_execute_quality_gates(self):
        """测试质量门控执行"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            driver = EpicDriver(f.name, use_claude=False)

            # Mock quality gate orchestrator
            with patch.object(driver, 'quality_gate_orchestrator') as mock_orchestrator:
                mock_orchestrator.execute_quality_gates = AsyncMock(return_value={"success": True})

                result = await driver.execute_quality_gates()

                assert result is True
                mock_orchestrator.execute_quality_gates.assert_called_once()

    @pytest.mark.anyio
    async def test_execute_quality_gates_skip(self):
        """测试跳过质量门控"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            driver = EpicDriver(f.name, use_claude=False, skip_quality=True)

            result = await driver.execute_quality_gates()

            assert result is True

    @pytest.mark.anyio
    async def test_convert_core_to_processing_status(self):
        """测试核心状态到处理状态转换"""
        from autoBMAD.epic_automation.epic_driver import _convert_core_to_processing_status

        # 测试各种状态转换
        assert _convert_core_to_processing_status("draft", "sm") == "Draft"
        assert _convert_core_to_processing_status("in_progress", "dev") == "In Progress"
        assert _convert_core_to_processing_status("done", "qa") == "Done"

    @pytest.mark.anyio
    async def test_epic_file_not_found(self):
        """测试 Epic 文件不存在"""
        driver = EpicDriver("nonexistent.md", use_claude=False)

        # 应该能初始化，但解析时会失败
        assert driver.epic_path.name == "nonexistent.md"

    @pytest.mark.anyio
    async def test_parse_epic_with_invalid_markdown(self):
        """测试解析无效的 Markdown"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("这不是有效的 Markdown")
            f.flush()

            driver = EpicDriver(f.name, use_claude=False)
            stories = await driver.parse_epic()

            # 应该返回空列表而不是崩溃
            assert isinstance(stories, list)
            assert len(stories) == 0

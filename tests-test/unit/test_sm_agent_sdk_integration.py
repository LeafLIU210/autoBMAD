"""
SM Agent SDK集成单元测试
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil

from autoBMAD.epic_automation.agents.sm_agent import SMAgent


class TestSMAgentSDKIntegration:
    """SM Agent SDK集成测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sm_agent(self, temp_dir):
        """创建SM Agent实例用于测试"""
        return SMAgent(
            project_root=temp_dir,
            tasks_path=temp_dir / "docs" / "stories"
        )

    @pytest.fixture
    def sample_epic_content(self):
        """示例Epic内容"""
        return """# Test Epic

## Stories

### Story 1.1: User Authentication System
As a user, I want to log in securely.
This feature includes login, logout, and session management.

### Story 1.2: Dashboard Widgets
As a user, I want customizable dashboard widgets.
This includes widget management and personalization features.
"""

    def test_create_blank_story_template_basic(self, sm_agent, temp_dir):
        """测试空白模板创建基本功能"""
        story_file = temp_dir / "stories" / "1.1.md"
        epic_content = "### Story 1.1: Test Story Title\nSome content..."

        # 创建stories目录
        (temp_dir / "stories").mkdir(parents=True, exist_ok=True)

        # 测试方法调用
        result = sm_agent._create_blank_story_template(story_file, "1.1", epic_content)

        # 验证结果
        assert result is True
        assert story_file.exists()

        content = story_file.read_text(encoding="utf-8")
        assert "# Story 1.1: Test Story Title" in content
        assert "**Status**: Draft" in content
        assert "## Story" in content
        assert "**As a** [user type]" in content

    def test_create_blank_story_template_missing_title(self, sm_agent, temp_dir):
        """测试空白模板创建 - 缺失标题处理"""
        story_file = temp_dir / "stories" / "2.1.md"
        epic_content = "No story section here"

        (temp_dir / "stories").mkdir(parents=True, exist_ok=True)

        result = sm_agent._create_blank_story_template(story_file, "2.1", epic_content)

        assert result is True
        content = story_file.read_text(encoding="utf-8")
        assert "Story Title Placeholder" in content

    def test_create_blank_story_template_error_handling(self, sm_agent, temp_dir):
        """测试空白模板创建 - 错误处理"""
        # 使用不存在的目录路径
        story_file = temp_dir / "nonexistent" / "dir" / "1.1.md"

        result = sm_agent._create_blank_story_template(story_file, "1.1", "content")

        # 应该失败并返回False
        assert result is False

    def test_extract_story_section_from_epic_basic(self, sm_agent, sample_epic_content):
        """测试从Epic提取故事章节基本功能"""
        section = sm_agent._extract_story_section_from_epic(sample_epic_content, "1.1")

        assert "Story 1.1: User Authentication System" in section
        assert "As a user, I want to log in securely" in section
        assert "session management" in section

    def test_extract_story_section_from_epic_missing_story(self, sm_agent, sample_epic_content):
        """测试从Epic提取故事章节 - 缺失故事"""
        section = sm_agent._extract_story_section_from_epic(sample_epic_content, "999.999")

        assert section == "Story 999.999 section not found in Epic"

    def test_extract_story_section_from_epic_story_2(self, sm_agent, sample_epic_content):
        """测试从Epic提取第二个故事"""
        section = sm_agent._extract_story_section_from_epic(sample_epic_content, "1.2")

        assert "Story 1.2: Dashboard Widgets" in section
        assert "customizable dashboard widgets" in section
        # 确保没有包含其他故事的内容
        assert "User Authentication System" not in section

    def test_extract_story_section_from_epic_error_handling(self, sm_agent):
        """测试从Epic提取故事章节 - 错误处理"""
        # 传入无效内容
        section = sm_agent._extract_story_section_from_epic("", "1.1")
        assert section == "Story 1.1 section not found in Epic"

        # 传入None
        section = sm_agent._extract_story_section_from_epic(None, "1.1")
        assert section == "Story 1.1 section not found in Epic"

    def test_verify_single_story_file_basic(self, sm_agent, temp_dir):
        """测试单个故事文件验证基本功能"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建完整的故事文件
        content = """# Story 1.1: Test Story

## Status
**Status**: Ready for Development

## Story
**As a** developer,
**I want** to test verification,
**So that** it works correctly.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Tasks / Subtasks
- [ ] Task 1

## Dev Notes
- Note 1

## Testing
### Unit Tests
- [ ] Test 1
"""

        story_file.write_text(content, encoding="utf-8")

        result = sm_agent._verify_single_story_file(story_file, "1.1")

        assert result is True

    def test_verify_single_story_file_missing_sections(self, sm_agent, temp_dir):
        """测试单个故事文件验证 - 缺失章节"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建不完整的故事文件
        content = "# Story 1.1: Incomplete Story\n\nOnly title"

        story_file.write_text(content, encoding="utf-8")

        result = sm_agent._verify_single_story_file(story_file, "1.1")

        assert result is False

    def test_verify_single_story_file_too_short(self, sm_agent, temp_dir):
        """测试单个故事文件验证 - 内容太短"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建太短的故事文件
        content = "# Story 1.1\n\nToo short"

        story_file.write_text(content, encoding="utf-8")

        result = sm_agent._verify_single_story_file(story_file, "1.1")

        assert result is False

    def test_verify_single_story_file_draft_status(self, sm_agent, temp_dir):
        """测试单个故事文件验证 - Draft状态（应通过但有警告）"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建包含Draft状态的故事文件
        content = """# Story 1.1: Test Story

## Status
**Status**: Draft

## Story
**As a** user,
**I want** to test,
**So that** it works.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Tasks / Subtasks
- [ ] Task 1

## Dev Notes
- Note 1

## Testing
### Unit Tests
- [ ] Test 1
"""

        story_file.write_text(content, encoding="utf-8")

        # Draft状态应该通过验证（非致命）
        result = sm_agent._verify_single_story_file(story_file, "1.1")
        assert result is True

    def test_verify_single_story_file_nonexistent(self, sm_agent, temp_dir):
        """测试单个故事文件验证 - 文件不存在"""
        story_file = temp_dir / "stories" / "nonexistent.md"

        result = sm_agent._verify_single_story_file(story_file, "1.1")

        assert result is False

    @pytest.mark.asyncio
    async def test_fill_story_with_sdk_mock_success(self, sm_agent, temp_dir):
        """测试SDK填充流程（模拟成功）"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建空白模板
        sm_agent._create_blank_story_template(story_file, "1.1", "### Story 1.1: Test")

        # 模拟SDK和Manager
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=True)

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 使用patch来模拟SafeClaudeSDK（在导入位置）
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent._fill_story_with_sdk(
                story_file, "1.1", "epic_path", "epic_content", mock_manager
            )

        assert result is True
        mock_sdk.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_fill_story_with_sdk_mock_failure(self, sm_agent, temp_dir):
        """测试SDK填充流程（模拟失败）"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        sm_agent._create_blank_story_template(story_file, "1.1", "### Story 1.1: Test")

        # 模拟SDK返回失败
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=False)

        mock_manager = MagicMock()

        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent._fill_story_with_sdk(
                story_file, "1.1", "epic_path", "epic_content", mock_manager
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_fill_story_with_sdk_import_error(self, sm_agent, temp_dir):
        """测试SDK填充流程 - 导入错误处理"""
        story_file = temp_dir / "stories" / "1.1.md"
        story_file.parent.mkdir(parents=True, exist_ok=True)

        sm_agent._create_blank_story_template(story_file, "1.1", "### Story 1.1: Test")

        # 模拟SafeClaudeSDK导入失败
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', side_effect=ImportError):
            result = await sm_agent._fill_story_with_sdk(
                story_file, "1.1", "epic_path", "epic_content", None
            )

        assert result is False

    def test_build_sdk_prompt_for_story_basic(self, sm_agent, temp_dir):
        """测试构建SDK prompt基本功能"""
        story_file = temp_dir / "stories" / "1.1.md"
        epic_path = temp_dir / "epic.md"
        epic_content = "### Story 1.1: Test Epic\nTest content"

        prompt = sm_agent._build_sdk_prompt_for_story("1.1", story_file, str(epic_path), epic_content)

        # 验证prompt包含关键元素
        assert "Based on the Epic document" in prompt
        assert "fill the story file" in prompt
        assert "Story 1.1" in prompt
        assert "Test Epic" in prompt
        assert str(story_file.resolve()) in prompt

    def test_build_sdk_prompt_for_story_missing_section(self, sm_agent, temp_dir):
        """测试构建SDK prompt - 缺失故事章节"""
        story_file = temp_dir / "stories" / "1.1.md"
        epic_path = temp_dir / "epic.md"
        epic_content = "No story section here"

        prompt = sm_agent._build_sdk_prompt_for_story("1.1", story_file, str(epic_path), epic_content)

        # 应该包含警告信息
        assert "section not found in Epic" in prompt
        assert "Story 1.1" in prompt

    def test_build_sdk_prompt_for_story_error_handling(self, sm_agent, temp_dir):
        """测试构建SDK prompt - 错误处理"""
        story_file = temp_dir / "stories" / "1.1.md"
        epic_path = temp_dir / "epic.md"

        # 传入无效的epic_content
        prompt = sm_agent._build_sdk_prompt_for_story("1.1", story_file, str(epic_path), None)

        assert prompt == ""

    @pytest.mark.asyncio
    async def test_create_stories_from_epic_full_flow_with_mocks(self, temp_dir):
        """测试完整Epic处理流程（使用模拟）"""
        # 创建正确的项目结构
        epic_file = temp_dir / "docs" / "epics" / "test_epic.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)

        epic_content = """# Test Epic

## Stories

### Story 1.1: First Story
As a user, I want feature 1.

### Story 1.2: Second Story
As a user, I want feature 2.
"""
        epic_file.write_text(epic_content, encoding="utf-8")

        # 创建SM Agent with correct project_root
        sm_agent = SMAgent(
            project_root=temp_dir,
            tasks_path=temp_dir / "docs" / "stories"
        )

        # 模拟SDK调用
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=True)

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock(return_value=True)
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            with patch('autoBMAD.epic_automation.monitoring.get_cancellation_manager', return_value=mock_manager):
                result = await sm_agent._create_stories_from_epic(str(epic_file))

        # 验证结果
        assert result is True  # 容错机制：只要有一个成功就返回True

        # 检查故事文件是否创建
        story_1 = temp_dir / "docs" / "stories" / "1.1.md"
        story_2 = temp_dir / "docs" / "stories" / "1.2.md"

        assert story_1.exists()
        assert story_2.exists()

        # 验证SDK调用次数（每个故事一次）
        assert mock_sdk.execute.call_count >= 1

    @pytest.mark.asyncio
    async def test_create_stories_from_epic_no_stories_found(self, sm_agent, temp_dir):
        """测试Epic处理流程 - 未找到故事"""
        # 创建没有故事的Epic文件
        epic_file = temp_dir / "empty_epic.md"
        epic_content = "# Empty Epic\nNo stories here"
        epic_file.write_text(epic_content, encoding="utf-8")

        result = await sm_agent._create_stories_from_epic(str(epic_file))

        assert result is False

    @pytest.mark.asyncio
    async def test_create_stories_from_epic_error_handling(self, sm_agent, temp_dir):
        """测试Epic处理流程 - 错误处理"""
        # 传入不存在的文件路径
        result = await sm_agent._create_stories_from_epic("nonexistent_file.md")

        assert result is False
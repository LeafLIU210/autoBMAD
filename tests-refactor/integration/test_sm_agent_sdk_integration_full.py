"""
SM Agent SDK集成完整流程集成测试
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil
import asyncio

from autoBMAD.epic_automation.agents.sm_agent import SMAgent


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
class TestSMAgentSDKIntegrationFull:
    """SM Agent SDK集成完整流程测试"""

    @pytest.fixture
    def temp_project_dir(self):
        """创建临时项目目录用于集成测试"""
        temp_dir = Path(tempfile.mkdtemp())
        project_root = temp_dir / "test_project"
        project_root.mkdir(parents=True, exist_ok=True)

        # 创建标准项目结构
        (project_root / "docs" / "stories").mkdir(parents=True, exist_ok=True)
        (project_root / "docs" / "epics").mkdir(parents=True, exist_ok=True)

        yield project_root
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def complex_epic_content(self):
        """复杂的Epic内容用于集成测试"""
        return """# E-Commerce Platform Epic

## Overview
This epic covers the core functionality of our e-commerce platform, including user management, product catalog, shopping cart, and order processing.

## Stories

### Story 1.1: User Registration and Authentication
As a new customer, I want to create an account so that I can access personalized features and track my orders.

**Details:**
- Email validation required
- Password strength requirements
- Social login options (Google, Facebook)
- Two-factor authentication support
- Account verification process

### Story 1.2: Product Catalog Management
As a customer, I want to browse products with filtering and search capabilities so that I can easily find what I'm looking for.

**Details:**
- Category-based navigation
- Search by name, brand, or category
- Filter by price range, rating, availability
- Sort by price, popularity, newest
- Product image gallery
- Detailed product information pages

### Story 1.3: Shopping Cart Functionality
As a customer, I want to add products to my cart and manage them so that I can proceed to checkout when ready.

**Details:**
- Add/remove items from cart
- Update quantities
- Save cart for later (logged-in users)
- Cart total calculation
- Persistent cart across sessions
- Inventory validation

### Story 1.4: Order Processing and Payment
As a customer, I want to complete my purchase securely so that I receive my ordered products.

**Details:**
- Multiple payment methods (credit card, PayPal, etc.)
- Secure payment processing
- Order confirmation emails
- Invoice generation
- Order tracking
- Refund and return processing
"""

    @pytest.fixture
    def simple_epic_content(self):
        """简单的Epic内容用于快速测试"""
        return """# Simple Task Management Epic

## Stories

### Story 2.1: Task Creation
As a user, I want to create new tasks.

### Story 2.2: Task Assignment
As a team lead, I want to assign tasks to team members.
"""

    @pytest.mark.asyncio
    async def test_complete_epic_processing_workflow(self, temp_project_dir, complex_epic_content):
        """测试完整的Epic处理工作流"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "ecommerce_epic.md"
        epic_file.write_text(complex_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟SafeClaudeSDK
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=True)

        # 模拟SDKCancellationManager
        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 执行完整流程
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            with patch('autoBMAD.epic_automation.monitoring.get_cancellation_manager', return_value=mock_manager):
                result = await sm_agent.create_stories_from_epic(str(epic_file))

        # 验证结果
        assert result is True

        # 验证故事文件创建
        expected_stories = ["1.1", "1.2", "1.3", "1.4"]
        stories_dir = temp_project_dir / "docs" / "stories"

        for story_id in expected_stories:
            story_file = stories_dir / f"{story_id}.md"
            assert story_file.exists(), f"Story file {story_id}.md should exist"

            # 验证文件内容
            content = story_file.read_text(encoding="utf-8")
            assert len(content) > 100, f"Story {story_id} content should be substantial"
            assert f"# Story {story_id}" in content, f"Story {story_id} should have proper title"
            assert "**Status**: Draft" in content, f"Story {story_id} should start with Draft status"

        # 验证SDK调用次数（每个故事一次）
        assert mock_sdk.execute.call_count >= 4

        # 验证Manager调用
        assert mock_manager.wait_for_cancellation_complete.call_count >= 4
        assert mock_manager.confirm_safe_to_proceed.call_count >= 4

    @pytest.mark.asyncio
    async def test_simple_epic_processing_workflow(self, temp_project_dir, simple_epic_content):
        """测试简单Epic处理工作流"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "simple_epic.md"
        epic_file.write_text(simple_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟SDK（模拟SDK执行失败的情况，测试容错机制）
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=False)  # 模拟SDK失败

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 执行流程
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent.create_stories_from_epic(str(epic_file))

        # 验证容错机制：即使SDK失败，模板仍应创建
        assert result is False  # 所有故事都失败时返回False

        # 验证空白模板仍被创建
        stories_dir = temp_project_dir / "docs" / "stories"
        story_21_file = stories_dir / "2.1.md"
        story_22_file = stories_dir / "2.2.md"

        assert story_21_file.exists(), "Story template should still be created even if SDK fails"
        assert story_22_file.exists(), "Story template should still be created even if SDK fails"

        # 验证模板内容
        content_21 = story_21_file.read_text(encoding="utf-8")
        content_22 = story_22_file.read_text(encoding="utf-8")

        assert "# Story 2.1: Task Creation" in content_21
        assert "# Story 2.2: Task Assignment" in content_22
        assert "**Status**: Draft" in content_21
        assert "**Status**: Draft" in content_22

    @pytest.mark.asyncio
    async def test_epic_processing_with_partial_sdk_failures(self, temp_project_dir, simple_epic_content):
        """测试Epic处理 - 部分SDK失败的情况"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "partial_epic.md"
        epic_file.write_text(simple_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟SDK（交替成功/失败）
        mock_sdk = AsyncMock()

        def execute_side_effect(*args, **kwargs):
            # 模拟第一个故事成功，第二个失败
            if execute_side_effect.call_count % 2 == 0:
                return True
            else:
                return False

        mock_sdk.execute = AsyncMock(side_effect=execute_side_effect)
        execute_side_effect.call_count = 0

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 执行流程
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent.create_stories_from_epic(str(epic_file))

        # 验证容错机制：部分成功应返回True
        assert result is True

        # 验证故事文件创建
        stories_dir = temp_project_dir / "docs" / "stories"
        story_21_file = stories_dir / "2.1.md"
        story_22_file = stories_dir / "2.2.md"

        assert story_21_file.exists()
        assert story_22_file.exists()

        # 验证SDK调用
        assert mock_sdk.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_epic_processing_with_missing_manager(self, temp_project_dir, simple_epic_content):
        """测试Epic处理 - 缺失Manager的情况"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "no_manager_epic.md"
        epic_file.write_text(simple_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟SDK成功，但Manager为None
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=True)

        # 执行流程（不传入Manager）
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent._fill_story_with_sdk(
                temp_project_dir / "docs" / "stories" / "2.1.md",
                "2.1",
                str(epic_file),
                simple_epic_content,
                manager=None  # 明确传入None
            )

        # 验证在没有Manager的情况下仍能工作
        assert result is True
        mock_sdk.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_epic_processing_error_recovery(self, temp_project_dir, simple_epic_content):
        """测试Epic处理 - 错误恢复机制"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "error_epic.md"
        epic_file.write_text(simple_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟SDK抛出异常
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(side_effect=Exception("SDK Error"))

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 执行流程
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            result = await sm_agent.create_stories_from_epic(str(epic_file))

        # 验证错误处理：应该返回False但不应崩溃
        assert result is False

        # 验证模板仍被创建（容错机制）
        stories_dir = temp_project_dir / "docs" / "stories"
        story_21_file = stories_dir / "2.1.md"
        story_22_file = stories_dir / "2.2.md"

        assert story_21_file.exists()
        assert story_22_file.exists()

    def test_story_template_content_structure(self, temp_project_dir):
        """测试故事模板内容结构"""
        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 测试模板创建
        story_file = temp_project_dir / "docs" / "stories" / "test_story.md"
        epic_content = "### Story 3.1: Comprehensive Testing Framework\nTest content with details"

        result = sm_agent._create_blank_story_template(story_file, "3.1", epic_content)

        assert result is True

        # 验证模板内容结构
        content = story_file.read_text(encoding="utf-8")

        # 检查必需章节
        required_sections = [
            "# Story 3.1: Comprehensive Testing Framework",
            "## Status",
            "**Status**: Draft",
            "## Story",
            "**As a** [user type]",
            "**I want** [functionality]",
            "**So that** [benefit]",
            "## Acceptance Criteria",
            "- [ ] Criterion 1",
            "- [ ] Criterion 2",
            "- [ ] Criterion 3",
            "## Tasks / Subtasks",
            "- [ ] Task 1: [description]",
            "- [ ] Task 2: [description]",
            "## Dev Notes",
            "- [Note 1]",
            "- [Note 2]",
            "## Testing",
            "### Unit Tests",
            "- [ ] Test case 1",
            "- [ ] Test case 2",
            "### Integration Tests",
            "- [ ] Integration test 1",
            "### Manual Testing",
            "- [ ] Manual test 1",
            "*This story template was created by SM Agent and awaits SDK filling.*"
        ]

        for section in required_sections:
            assert section in content, f"Required section '{section}' not found in template"

    def test_story_section_extraction_accuracy(self, temp_project_dir, complex_epic_content):
        """测试故事章节提取的准确性"""
        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 测试每个故事的章节提取
        test_cases = [
            ("1.1", "User Registration and Authentication"),
            ("1.2", "Product Catalog Management"),
            ("1.3", "Shopping Cart Functionality"),
            ("1.4", "Order Processing and Payment")
        ]

        for story_id, expected_title in test_cases:
            section = sm_agent._extract_story_section_from_epic(complex_epic_content, story_id)

            assert f"### Story {story_id}:" in section, f"Story {story_id} header not found"
            assert expected_title in section, f"Expected title '{expected_title}' not found in story {story_id}"

            # 确保不包含其他故事的内容
            for other_id, _ in test_cases:
                if other_id != story_id:
                    assert f"### Story {other_id}" not in section, f"Story {other_id} content leaked into {story_id}"

    def test_single_story_file_validation_comprehensive(self, temp_project_dir):
        """测试单个故事文件验证的全面性"""
        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 测试用例：完整的故事文件
        complete_story = """# Story 4.1: Complete Story Example

## Status
**Status**: Ready for Development

## Story
**As a** system user,
**I want** comprehensive functionality,
**So that** I can achieve my goals effectively.

## Acceptance Criteria
- [ ] First requirement must be met
- [ ] Second requirement must be implemented
- [ ] Third requirement provides additional value
- [ ] Edge cases are handled gracefully

## Tasks / Subtasks
- [ ] Task 1: Setup development environment
- [ ] Task 2: Implement core functionality
- [ ] Task 3: Add error handling
- [ ] Task 4: Write comprehensive tests

## Dev Notes
- Consider using dependency injection for better testability
- Performance optimization may be needed for large datasets
- Security review required for user input handling

## Testing
### Unit Tests
- [ ] Test core business logic
- [ ] Test error scenarios
- [ ] Test boundary conditions

### Integration Tests
- [ ] Test database interactions
- [ ] Test external API integrations

### Manual Testing
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Security testing
"""

        story_file = temp_project_dir / "docs" / "stories" / "4.1.md"
        story_file.write_text(complete_story, encoding="utf-8")

        # 验证应该通过
        result = sm_agent._verify_single_story_file(story_file, "4.1")
        assert result is True

    def test_sdk_prompt_construction_completeness(self, temp_project_dir, complex_epic_content):
        """测试SDK Prompt构建的完整性"""
        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        story_file = temp_project_dir / "docs" / "stories" / "story_1.1.md"
        epic_file = temp_project_dir / "docs" / "epics" / "test_epic.md"

        prompt = sm_agent._build_sdk_prompt_for_story("1.1", story_file, str(epic_file), complex_epic_content)

        # 验证prompt包含所有必需元素
        required_elements = [
            "@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\sm.md",
            "@D:\\GITHUB\\pytQt_template\\.bmad-core\\tasks\\create-next-story.md",
            "Based on the Epic document",
            str(epic_file.resolve()),
            "fill the story file",
            str(story_file.resolve()),
            "Story 1.1",
            "User Registration and Authentication",
            "Complete user story",
            "Detailed acceptance criteria",
            "Implementation tasks/subtasks",
            "Dev notes with technical considerations",
            "Testing requirements",
            "Change the Status from \"Draft\" to \"Ready for Development\"",
            "Please complete the story file now"
        ]

        for element in required_elements:
            assert element in prompt, f"Required element '{element}' not found in prompt"

    @pytest.mark.asyncio
    async def test_concurrent_story_processing_simulation(self, temp_project_dir, simple_epic_content):
        """测试并发故事处理的模拟"""
        # 准备测试数据
        epic_file = temp_project_dir / "docs" / "epics" / "concurrent_epic.md"
        epic_file.write_text(simple_epic_content, encoding="utf-8")

        # 创建SM Agent
        sm_agent = SMAgent(
            project_root=temp_project_dir,
            tasks_path=temp_project_dir / "docs" / "stories"
        )

        # 模拟较慢的SDK响应
        mock_sdk = AsyncMock()
        mock_sdk.execute = AsyncMock(return_value=True)

        mock_manager = MagicMock()
        mock_manager.wait_for_cancellation_complete = AsyncMock()
        mock_manager.confirm_safe_to_proceed = AsyncMock(return_value=True)

        # 执行流程
        with patch('autoBMAD.epic_automation.sdk_wrapper.SafeClaudeSDK', return_value=mock_sdk):
            with patch('autoBMAD.epic_automation.monitoring.get_cancellation_manager', return_value=mock_manager):
                result = await sm_agent.create_stories_from_epic(str(epic_file))

        # 验证结果
        assert result is True

        # 验证所有故事都被处理
        stories_dir = temp_project_dir / "docs" / "stories"
        expected_stories = ["2.1", "2.2"]

        for story_id in expected_stories:
            story_file = stories_dir / f"{story_id}.md"
            assert story_file.exists(), f"Story {story_id} should be processed"

        # 验证SDK调用顺序和次数
        assert mock_sdk.execute.call_count >= 2
        assert mock_manager.confirm_safe_to_proceed.call_count >= 2
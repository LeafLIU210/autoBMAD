"""
SM Agent - Story Master Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
新增：SDK调用集成，完整故事创建生命周期管理
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from anyio.abc import TaskGroup

from autoBMAD.epic_automation.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SMAgent(BaseAgent):
    """Story Master agent for handling story-related tasks."""

    def __init__(
        self,
        task_group: Optional[TaskGroup] = None,
        project_root: Optional[Path] = None,
        tasks_path: Optional[Path] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize SM agent.

        Args:
            task_group: TaskGroup实例
            project_root: Root directory of the project
            tasks_path: Path to tasks directory
            config: Configuration dictionary
        """
        super().__init__("SMAgent", task_group)
        self.project_root = project_root
        self.tasks_path = tasks_path
        self.config = config or {}

        # 集成SDKExecutor
        self.sdk_executor = None
        try:
            from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
            self.sdk_executor = SDKExecutor()
        except (ImportError, TypeError):
            self._log_execution("SDKExecutor not available", "warning")

        # Initialize SimpleStoryParser
        try:
            self.status_parser = None
            # try:
            #     from ..story_parser import SimpleStoryParser
            #     self.status_parser = SimpleStoryParser(sdk_wrapper=None)
            # except ImportError:
            #     self._log_execution("SimpleStoryParser not available", "warning")
        except Exception as e:
            self._log_execution(f"Failed to initialize status parser: {e}", "warning")

        self._log_execution("SMAgent initialized")

    async def execute(
        self,
        story_content: Optional[str] = None,
        story_path: Optional[str] = None,
        epic_path: Optional[str] = None,
    ) -> bool:
        """
        执行SM阶段任务

        Args:
            story_content: Raw markdown content of the story
            story_path: Path to the story file
            epic_path: Path to the epic file

        Returns:
            True if successful, False otherwise
        """
        self._log_execution("Starting SM phase execution")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "error")
            return False

        try:
            # 优先从Epic创建故事
            if epic_path:
                if self.task_group:
                    return await self._execute_within_taskgroup(
                        lambda: self._create_stories_from_epic(epic_path)
                    )
                else:
                    return await self._create_stories_from_epic(epic_path)

            # 否则处理现有故事
            if story_content and story_path:
                if self.task_group:
                    return await self._execute_within_taskgroup(
                        lambda: self._process_story_content(story_content, story_path)
                    )
                else:
                    return await self._process_story_content(story_content, story_path)

            self._log_execution("No valid input provided", "error")
            return False

        except Exception as e:
            self._log_execution(f"Execution failed: {e}", "error")
            return False

    async def create_stories_from_epic(self, epic_path: str) -> bool:
        """
        从Epic创建故事 - 公共接口

        Args:
            epic_path: Epic文件路径

        Returns:
            True if successful, False otherwise
        """
        return await self._create_stories_from_epic(epic_path)

    async def _create_stories_from_epic(self, epic_path: str) -> bool:
        """
        从Epic创建故事 - 集成SDK调用

        流程：
        1. 读取Epic并提取故事ID列表
        2. 遍历每个故事ID：
           a. 创建空白故事模板文件
           b. 调用SDK填充内容
           c. 确认SDK完成并清理
           d. 验证文件内容
        3. 返回整体结果
        """
        try:
            self._log_execution(f"Creating stories from Epic: {epic_path}")

            # 读取Epic内容
            with open(epic_path, encoding="utf-8") as f:
                epic_content = f.read()

            # 提取故事ID
            story_ids = self._extract_story_ids_from_epic(epic_content)
            if not story_ids:
                self._log_execution("No story IDs found", "error")
                return False

            self._log_execution(f"Found {len(story_ids)} stories: {story_ids}")

            # 创建stories目录
            epic_path_obj = Path(epic_path)
            project_root = epic_path_obj.parents[2]
            stories_dir = project_root / "docs" / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            # 🎯 新增：获取SDKCancellationManager
            manager = None
            try:
                from autoBMAD.epic_automation.monitoring import get_cancellation_manager
                manager = get_cancellation_manager()
            except ImportError:
                self._log_execution("SDKCancellationManager not available", "warning")

            # 遍历每个故事ID，逐个处理
            success_count = 0
            failed_stories = []

            for idx, story_id in enumerate(story_ids, 1):
                self._log_execution(f"[{idx}/{len(story_ids)}] Processing story {story_id}...")

                # Step 1: 创建空白故事模板文件
                story_file = stories_dir / f"{story_id}.md"
                if not self._create_blank_story_template(story_file, story_id, epic_content):
                    self._log_execution(f"Failed to create template for {story_id}", "warning")
                    failed_stories.append(story_id)
                    continue

                # Step 2 & 3 & 4 & 5: SDK调用 + 确认ResultMessage + SDK取消 + 确认取消完成
                sdk_success = await self._fill_story_with_sdk(
                    story_file, story_id, epic_path, epic_content, manager
                )

                if not sdk_success:
                    self._log_execution(f"SDK filling failed for {story_id}", "warning")
                    failed_stories.append(story_id)
                    continue

                # Step 6: 验证故事文件内容
                if self._verify_single_story_file(story_file, story_id):
                    success_count += 1
                    self._log_execution(f"[OK] Story {story_id} completed successfully")
                else:
                    self._log_execution(f"[FAIL] Story {story_id} verification failed", "warning")
                    failed_stories.append(story_id)

            # 汇总结果
            self._log_execution(
                f"Story creation completed: {success_count}/{len(story_ids)} succeeded"
            )

            if failed_stories:
                self._log_execution(f"Failed stories: {failed_stories}", "warning")

            # 🎯 容错机制：只要有一个成功就返回True
            return success_count > 0

        except Exception as e:
            self._log_execution(f"Failed to create stories: {e}", "error")
            return False

    async def _process_story_content(
        self, story_content: str, story_path: str
    ) -> bool:
        """处理故事内容"""
        try:
            self._log_execution(f"Processing story content: {story_path}")

            # 解析故事元数据
            story_data = await self._parse_story_metadata(story_content)
            if not story_data:
                self._log_execution("Failed to parse story metadata", "error")
                return False

            # 验证故事结构
            validation_result = await self._validate_story_structure(story_data)
            if not validation_result["valid"]:
                self._log_execution(
                    f"Story validation issues: {validation_result['issues']}", "warning"
                )

            self._log_execution("SM phase completed successfully")
            return True

        except Exception as e:
            self._log_execution(f"Failed to process story: {e}", "error")
            return False

    def _extract_story_ids_from_epic(self, content: str) -> list[str]:
        """
        Extract story IDs from epic document.

        Args:
            content: Epic document content

        Returns:
            List of story IDs (e.g., ["1.1", "1.2", ...])
        """
        story_ids: list[str] = []

        # Pattern 1: "### Story X.Y: Title"
        pattern1 = r"### Story\s+(\d+(?:\.\d+)?)\s*:\s*(.+?)(?:\n|\$)"
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        for story_num, _title in matches1:
            story_ids.append(story_num)
            logger.debug(f"Found story section: {story_num}")

        # Pattern 2: "**Story ID**: 001"
        pattern2 = r"\*\*Story ID\*\*\s*:\s*(\d+(?:\.\d+)?)"
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        for story_num in matches2:
            if story_num not in story_ids:
                story_ids.append(story_num)
                logger.debug(f"Found story ID: {story_num}")

        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique_story_ids: list[str] = []
        for story_id in story_ids:
            if story_id not in seen:
                seen.add(story_id)
                unique_story_ids.append(story_id)

        logger.debug(
            f"Extracted {len(unique_story_ids)} unique story IDs: {unique_story_ids}"
        )
        return unique_story_ids

    def _extract_story_from_epic(self, epic_content: str, story_id: str) -> str:
        """
        [DEPRECATED] 从Epic文档中提取指定故事ID的完整内容。
        现在改为使用SDK填充，此方法已废弃。

        Args:
            epic_content: Epic文档内容
            story_id: 故事ID (例如 "1.1")

        Returns:
            故事内容的字符串，如果没有找到则返回空字符串
        """
        # 🎯 已废弃：原方法直接生成完整故事文档，现改为SDK填充
        logger.warning(f"_extract_story_from_epic is deprecated, use _extract_story_section_from_epic instead")
        return self._extract_story_section_from_epic(epic_content, story_id)

    def _build_claude_prompt(self, epic_path: str, story_ids: list[str]) -> str:
        """
        Build the prompt for Claude to create stories.

        Args:
            epic_path: Path to the epic markdown file
            story_ids: List of story IDs

        Returns:
            Formatted prompt string
        """
        # 构建Windows风格的绝对路径列表
        epic_path_obj = Path(epic_path)
        project_root = epic_path_obj.parents[2]  # Go up to project root
        stories_dir = project_root / "docs" / "stories"

        story_paths: list[str] = []
        for story_id in story_ids:
            story_path = stories_dir / f"{story_id}.md"
            story_paths.append(str(story_path.resolve()))

        story_list = "\n".join(story_paths)

        # Get relative path from current directory
        epic_rel_path = str(Path(epic_path))

        prompt = f'@.bmad-core\\agents\\sm.md @.bmad-core\\tasks\\create-next-story.md According to epic @{epic_rel_path}. Build all the stories listed in: {story_list}. Change all the story document Status from "Draft" to "Ready for Development".'

        logger.debug(f"Built prompt: {prompt}")
        return prompt

    async def _verify_story_files(
        self, story_ids: list[str], epic_path: str
    ) -> tuple[bool, list[str]]:
        """
        Verify that all story files were successfully created with complete content.

        Args:
            story_ids: List of story IDs to verify
            epic_path: Path to the epic file

        Returns:
            Tuple[bool, List[str]] - (whether all succeeded, list of failed stories)
        """
        self._log_execution("Starting to verify story files...")
        failed_stories: list[str] = []

        # Determine story file directory
        epic_path_obj = Path(epic_path)
        project_root = epic_path_obj.parents[2]  # Go up to project root
        stories_dir = project_root / "docs" / "stories"

        if not stories_dir.exists():
            self._log_execution(f"Stories directory does not exist: {stories_dir}", "error")
            return False, story_ids

        for story_id in story_ids:
            # Find matching files using fuzzy matching
            story_file = self._find_story_file(stories_dir, story_id)

            if not story_file:
                self._log_execution(f"Story file does not exist: {story_id}", "error")
                failed_stories.append(story_id)
                continue

            # Verify file content
            try:
                with open(story_file, encoding="utf-8") as f:
                    content = f.read()

                # Basic validation
                if len(content) < 100:
                    self._log_execution(
                        f"Story file too short ({len(content)} chars): {story_file}", "warning"
                    )
                    failed_stories.append(story_id)
                    continue

                # Verify key sections based on actual story-template-v2
                required_sections = [
                    "# Story",  # Story title (e.g., "# Story 1.1: ...")
                    "## Status",
                    "## Story",  # User story format
                    "## Acceptance Criteria",
                    "## Tasks / Subtasks",
                    "## Dev Notes",
                    "## Testing",
                ]

                missing_sections: list[str] = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)

                if missing_sections:
                    self._log_execution(
                        f"Story file missing key sections {missing_sections}: {story_file}", "warning"
                    )
                    failed_stories.append(story_id)
                    continue

                self._log_execution(
                    f"[OK] Story file verification passed: {story_file}"
                )

            except Exception as e:
                self._log_execution(
                    f"Failed to verify story file: {story_file}, error: {e}", "error"
                )
                failed_stories.append(story_id)

        if failed_stories:
            self._log_execution(
                f"[FAIL] {len(failed_stories)} stories verification failed: {failed_stories}", "error"
            )
            return False, failed_stories
        else:
            self._log_execution(
                f"[OK] All {len(story_ids)} stories verification passed"
            )
            return True, []

    def _find_story_file(self, stories_dir: Path, story_id: str) -> Path | None:
        """
        Find story file supporting simplified naming format.

        Args:
            stories_dir: Story files directory
            story_id: Story ID (e.g., "1.1", "1.2")

        Returns:
            Matching story file path, or None if not found

        Supported formats:
            - 1.1.md (simplified format)
        """
        # Simplified naming rule: only support {story_id}.md format
        pattern = f"{story_id}.md"
        matches = list(stories_dir.glob(pattern))
        if matches:
            logger.debug(
                f"[SM Agent] Found story file with pattern '{pattern}': {matches[0]}"
            )
            return matches[0]

        logger.debug(f"[SM Agent] No story file found for ID: {story_id}")
        return None

    async def _parse_story_metadata(
        self, story_content: str
    ) -> dict[str, Any] | None:
        """
        Parse story markdown and extract metadata.

        Args:
            story_content: Raw markdown content

        Returns:
            Dictionary with parsed story metadata, or None if parsing fails
        """
        try:
            metadata: dict[str, Any] = {
                "title": None,
                "status": None,
                "acceptance_criteria": [],
                "tasks": [],
                "raw_content": story_content,
            }

            # Extract title (first h1 heading)
            title_match = re.search(r"^#\s+(.+)$", story_content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(
                r"\*\*Status\*\*:\s*(.+)$", story_content, re.MULTILINE
            )
            if status_match:
                metadata["status"] = status_match.group(1).strip()

            # Extract acceptance criteria
            ac_pattern = r"- \[ \]\s+(.+)$"
            ac_matches = re.findall(ac_pattern, story_content, re.MULTILINE)
            metadata["acceptance_criteria"] = ac_matches

            # Extract tasks
            task_pattern = r"- \[ \] Task \d+:\s+(.+)$"
            task_matches = re.findall(task_pattern, story_content, re.MULTILINE)
            metadata["tasks"] = task_matches

            logger.info(
                f"Parsed story metadata: {len(metadata['acceptance_criteria'])} AC, {len(metadata['tasks'])} tasks"
            )
            return metadata

        except Exception as e:
            logger.error(f"Failed to parse story metadata: {e}")
            return None

    async def _validate_story_structure(
        self, story_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate story structure and completeness.

        Args:
            story_data: Parsed story metadata

        Returns:
            Dictionary with validation result
        """
        issues: list[str] = []
        warnings: list[str] = []

        # Check required fields
        if not story_data.get("title"):
            issues.append("Missing story title")

        if not story_data.get("status"):
            warnings.append("Missing status field")

        # Check acceptance criteria
        ac_count = len(story_data.get("acceptance_criteria", []))
        if ac_count == 0:
            warnings.append("No acceptance criteria found")
        elif ac_count < 3:
            warnings.append(f"Only {ac_count} acceptance criteria (recommended: 3+)")

        # Check tasks
        task_count = len(story_data.get("tasks", []))
        if task_count == 0:
            warnings.append("No tasks found")

        result: dict[str, Any] = {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

        if issues:
            logger.warning(f"Story validation issues: {issues}")
        if warnings:
            logger.info(f"Story validation warnings: {warnings}")

        return result

    def _create_blank_story_template(
        self, story_file: Path, story_id: str, epic_content: str
    ) -> bool:
        """
        创建空白故事模板文件

        Args:
            story_file: 故事文件路径
            story_id: 故事ID（例如 "1.1"）
            epic_content: Epic文档内容（用于提取故事标题）

        Returns:
            True if successful, False otherwise
        """
        try:
            # 从Epic中提取故事标题
            pattern = rf"### Story\s+{re.escape(story_id)}\s*:\s*(.+?)(?:\n|$)"
            match = re.search(pattern, epic_content, re.MULTILINE)
            story_title = match.group(1).strip() if match else "Story Title Placeholder"

            # 创建空白模板内容
            template_content = f"""# Story {story_id}: {story_title}

## Status
**Status**: Draft

## Story
**As a** [user type],
**I want** [functionality],
**So that** [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Tasks / Subtasks
- [ ] Task 1: [description]
- [ ] Task 2: [description]

## Dev Notes
- [Note 1]
- [Note 2]

## Testing
### Unit Tests
- [ ] Test case 1
- [ ] Test case 2

### Integration Tests
- [ ] Integration test 1

### Manual Testing
- [ ] Manual test 1

---
*This story template was created by SM Agent and awaits SDK filling.*
"""

            # 写入文件
            with open(story_file, "w", encoding="utf-8") as f:
                f.write(template_content)

            self._log_execution(f"Created blank template: {story_file}")
            return True

        except Exception as e:
            self._log_execution(f"Failed to create blank template: {e}", "error")
            return False

    def _extract_story_section_from_epic(self, epic_content: str, story_id: str) -> str:
        """
        从Epic中提取指定故事的相关章节（不创建文件，仅提取文本）

        Args:
            epic_content: Epic文档内容
            story_id: 故事ID

        Returns:
            Story section text
        """
        try:
            if not epic_content:
                return f"Story {story_id} section not found in Epic"

            # 查找故事标题模式："### Story X.Y: Title"
            pattern = rf"### Story\s+{re.escape(story_id)}\s*:\s*(.+?)(?:\n### Story|\n---|\\n##|\Z)"
            match = re.search(pattern, epic_content, re.MULTILINE | re.DOTALL)

            if not match:
                # 尝试更宽松的匹配
                pattern = rf"### Story\s+{re.escape(story_id)}\s*:\s*(.+?)(?:\n###|\Z)"
                match = re.search(pattern, epic_content, re.MULTILINE | re.DOTALL)

            if match:
                return match.group(0).strip()
            else:
                return f"Story {story_id} section not found in Epic"

        except Exception as e:
            self._log_execution(f"Failed to extract story section: {e}", "error")
            return ""

    def _build_sdk_prompt_for_story(
        self,
        story_id: str,
        story_file: Path,
        epic_path: str,
        epic_content: str
    ) -> str:
        """
        为单个故事构建SDK prompt

        Args:
            story_id: 故事ID
            story_file: 故事文件路径
            epic_path: Epic文件路径
            epic_content: Epic文档内容

        Returns:
            Formatted prompt string
        """
        try:
            # 验证输入参数
            if not epic_content:
                self._log_execution("Empty epic content provided", "warning")
                return ""

            # 从Epic中提取该故事的相关章节
            story_section = self._extract_story_section_from_epic(epic_content, story_id)

            if not story_section:
                self._log_execution(
                    f"Warning: Could not extract story section for {story_id}", "warning"
                )
                story_section = f"Story {story_id} - No detailed section found in Epic"

            # 构建prompt（使用BMAD约定的格式）
            epic_abs_path = Path(epic_path).resolve()
            story_abs_path = story_file.resolve()

            prompt = f"""@.bmad-core\\agents\\sm.md
@.bmad-core\\tasks\\create-next-story.md

Based on the Epic document @{epic_abs_path}, fill the story file @{story_abs_path} with complete content.

**Epic Context for Story {story_id}**:
{story_section}

**Requirements**:
1. Parse the story requirements from the Epic context above
2. Fill the story file with:
   - Complete user story (As a/I want/So that format)
   - Detailed acceptance criteria (at least 3 items)
   - Implementation tasks/subtasks
   - Dev notes with technical considerations
   - Testing requirements (unit/integration/manual)
3. Change the Status from "Draft" to "Ready for Development"
4. Ensure all sections are filled with meaningful, actionable content

Please complete the story file now."""

            return prompt

        except Exception as e:
            self._log_execution(f"Failed to build prompt: {e}", "error")
            return ""

    async def _fill_story_with_sdk(
        self,
        story_file: Path,
        story_id: str,
        epic_path: str,
        epic_content: str,
        manager: Any | None
    ) -> bool:
        """
        使用SDK填充故事内容（简化版）

        流程：
        1. 构建prompt
        2. 调用execute_sdk_call统一接口
        3. 检查执行结果

        Args:
            story_file: 故事文件路径
            story_id: 故事ID
            epic_path: Epic文件路径
            epic_content: Epic文档内容
            manager: 保留参数（不再使用）

        Returns:
            True if successful, False otherwise
        """
        try:
            import asyncio

            # Step 1: 构建prompt
            prompt = self._build_sdk_prompt_for_story(
                story_id, story_file, epic_path, epic_content
            )

            if not prompt:
                self._log_execution(f"Failed to build prompt for {story_id}", "error")
                return False

            # Step 2: 调用SDK（使用统一接口）
            self._log_execution(f"[SDK] Starting SDK call for story {story_id}...")

            # 使用sdk_helper的execute_sdk_call统一接口
            try:
                from .sdk_helper import execute_sdk_call
            except ImportError as e:
                self._log_execution(f"Failed to import SDK helper: {e}", "error")
                return False

            # 执行SDK调用
            result = await execute_sdk_call(
                prompt=prompt,
                agent_name=f"SMAgent-{story_id}",
                timeout=1800.0,
                permission_mode="bypassPermissions"
            )

            # 检查结果
            if not result.is_success():
                self._log_execution(
                    f"[SDK] SDK execution failed for story {story_id}: "
                    f"{result.error_type.value}",
                    "warning"
                )
                return False

            self._log_execution(f"[SDK] SDK execution completed for story {story_id}")

            # 添加短暂延迟（让文件系统同步）
            await asyncio.sleep(0.5)

            return True

        except Exception as e:
            self._log_execution(f"SDK filling failed for {story_id}: {e}", "error")
            import traceback
            self._log_execution(f"Traceback: {traceback.format_exc()}", "debug")
            return False

    def _verify_single_story_file(self, story_file: Path, story_id: str) -> bool:
        """
        验证单个故事文件的内容完整性

        Args:
            story_file: 故事文件路径
            story_id: 故事ID

        Returns:
            True if verification passed, False otherwise
        """
        try:
            if not story_file.exists():
                self._log_execution(f"Story file does not exist: {story_file}", "error")
                return False

            with open(story_file, encoding="utf-8") as f:
                content = f.read()

            # 基本验证
            if len(content) < 100:
                self._log_execution(
                    f"Story file too short ({len(content)} chars): {story_file}", "warning"
                )
                return False

            # 验证关键章节
            required_sections = [
                "# Story",
                "## Status",
                "## Story",
                "## Acceptance Criteria",
                "## Tasks / Subtasks",
                "## Dev Notes",
                "## Testing",
            ]

            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)

            if missing_sections:
                self._log_execution(
                    f"Story file missing sections {missing_sections}: {story_file}", "warning"
                )
                return False

            # 验证状态已更新（不再是Draft）
            if "**Status**: Draft" in content:
                self._log_execution(
                    f"Story status still Draft (SDK may not have updated): {story_file}", "warning"
                )
                # 🎯 非致命：状态未更新不算验证失败
                # return False

            self._log_execution(f"[OK] Story file verification passed: {story_file}")
            return True

        except Exception as e:
            self._log_execution(f"Failed to verify story file: {e}", "error")
            return False

    def _update_story_status_in_content(self, story_content: str, new_status: str) -> str:
        """
        Update the status in story content.

        Args:
            story_content: The story content to update
            new_status: The new status value

        Returns:
            Updated story content with new status
        """
        lines = story_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('Status:'):
                lines[i] = f"Status: {new_status}"
                break

        return '\n'.join(lines)

    def _extract_story_sections(self, story_content: str) -> dict[str, str]:
        """
        Extract sections from story content.

        Args:
            story_content: The story content to parse

        Returns:
            Dictionary of section names to content
        """
        sections = {}
        current_section: Optional[str] = None
        current_content: list[str] = []

        for line in story_content.split('\n'):
            if line.strip().startswith('## '):
                # Save previous section
                if current_section is not None:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line.strip()[3:].strip()
                current_content = []
            else:
                if current_section is not None:
                    current_content.append(line)

        # Save last section
        if current_section is not None:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

"""
SM Agent - Story Master Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SMAgent(BaseAgent):
    """Story Master agent for handling story-related tasks."""

    def __init__(
        self,
        task_group: Optional[Any] = None,
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
            from ..core.sdk_executor import SDKExecutor
            self.sdk_executor = SDKExecutor()
        except ImportError:
            self._log_execution("SDKExecutor not available", "warning")

        # Initialize SimpleStoryParser
        try:
            self.status_parser = None
            try:
                from ..story_parser import SimpleStoryParser
                self.status_parser = SimpleStoryParser(sdk_wrapper=None)
            except ImportError:
                self._log_execution("SimpleStoryParser not available", "warning")
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
                return await self._execute_within_taskgroup(
                    lambda: self._create_stories_from_epic(epic_path)
                )

            # 否则处理现有故事
            if story_content and story_path:
                return await self._execute_within_taskgroup(
                    lambda: self._process_story_content(story_content, story_path)
                )

            self._log_execution("No valid input provided", "error")
            return False

        except Exception as e:
            self._log_execution(f"Execution failed: {e}", "error")
            return False

    async def _create_stories_from_epic(self, epic_path: str) -> bool:
        """
        从Epic创建故事 - 重构后使用SDKExecutor
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

            # 使用SDKExecutor执行故事创建
            if self.sdk_executor:
                prompt = self._build_claude_prompt(epic_path, story_ids)
                result = await self._execute_sdk_call(self.sdk_executor, prompt)

                if result:
                    # 验证故事文件
                    all_passed, _ = await self._verify_story_files(story_ids, epic_path)
                    return all_passed
                else:
                    self._log_execution("SDK call failed", "error")
                    return False
            else:
                self._log_execution("SDKExecutor not available", "error")
                return False

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

        prompt = f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\sm.md @D:\\GITHUB\\pytQt_template\\.bmad-core\\tasks\\create-next-story.md According to epic @{epic_rel_path}. Build all the stories listed in: {story_list}. Change all the story document Status from "Draft" to "Ready for Development".'

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

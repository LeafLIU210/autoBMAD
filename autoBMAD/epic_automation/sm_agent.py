"""
SM Agent - Story Master Agent

Handles story creation, planning, and management tasks.
Integrates with task guidance for SM-specific operations.
"""

import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import re

# Import SafeClaudeSDK wrapper
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

# Import SDK session manager for isolated execution
from .sdk_session_manager import get_session_manager, SDKErrorType

try:
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
except ImportError:
    # For development without SDK installed
    query = None
    ClaudeAgentOptions = None
    ResultMessage = None

logger = logging.getLogger(__name__)


class SMAgent:
    """Story Master agent for handling story-related tasks."""

    def __init__(self, project_root: Optional[str] = None, tasks_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SM agent.

        Args:
            project_root: Root directory of the project
            tasks_path: Path to tasks directory
            config: Configuration dictionary
        """
        self.name = "SM Agent"
        self.agent_name = "SM Agent"
        self.phase = "Story Management"
        self.project_root = Path(project_root) if project_root else None
        self.tasks_path = Path(tasks_path) if tasks_path else None
        self.config = config or {}
        logger.info(f"{self.name} initialized")

    @staticmethod
    def _find_story_file(stories_dir: Path, story_id: str) -> Optional[Path]:
        """
        模糊匹配故事文件，支持多种命名格式。

        Args:
            stories_dir: 故事文件目录
            story_id: 故事ID (如 "1.1", "1.2")

        Returns:
            匹配的故事文件路径，如果未找到则返回None

        支持的格式:
            - 1.1-description.md (推荐格式)
            - 1.1.description.md
            - story-1-1-description.md
            - story-1.1-description.md
        """
        # 按优先级顺序尝试匹配
        patterns = [
            f"{story_id}-*.md",                          # 1.1-xxx.md (推荐)
            f"{story_id}.*.md",                          # 1.1.xxx.md
            f"story-{story_id.replace('.', '-')}-*.md",  # story-1-1-xxx.md
            f"story-{story_id}-*.md",                    # story-1.1-xxx.md
        ]

        for pattern in patterns:
            matches = list(stories_dir.glob(pattern))
            if matches:
                logger.debug(f"[SM Agent] Found story file with pattern '{pattern}': {matches[0]}")
                return matches[0]

        # 最后尝试更宽松的匹配：任意包含story_id的文件
        loose_pattern = f"*{story_id}*.md"
        matches = list(stories_dir.glob(loose_pattern))
        if matches:
            logger.debug(f"[SM Agent] Found story file with loose pattern '{loose_pattern}': {matches[0]}")
            return matches[0]

        logger.debug(f"[SM Agent] No story file found for ID: {story_id}")
        return None

    async def execute(
        self,
        story_content: str,
        story_path: str = ""
    ) -> bool:
        """
        Execute SM phase for a story.

        Args:
            story_content: Raw markdown content of the story
            story_path: Path to the story file (for status update)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"{self.name} executing SM phase")

        try:
            # Parse story metadata
            story_data = await self._parse_story_metadata(story_content)

            if not story_data:
                logger.error("Failed to parse story metadata")
                return False

            # Validate story structure
            validation_result = await self._validate_story_structure(story_data)
            if not validation_result['valid']:
                logger.warning(f"Story validation issues: {validation_result['issues']}")
                # Continue anyway, as validation issues don't block SM phase

            logger.info(f"{self.name} SM phase completed successfully")
            return True

        except Exception as e:
            logger.error(f"{self.name} execution failed: {e}")
            return False

    async def _parse_story_metadata(self, story_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse story markdown and extract metadata.

        Args:
            story_content: Raw markdown content

        Returns:
            Dictionary with parsed story metadata, or None if parsing fails
        """
        try:
            metadata: Dict[str, Any] = {
                'title': None,
                'status': None,
                'acceptance_criteria': [],
                'tasks': [],
                'raw_content': story_content
            }

            # Extract title (first h1 heading)
            title_match = re.search(r'^#\s+(.+)$', story_content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status\*\*:\s*(.+)$', story_content, re.MULTILINE)
            if status_match:
                metadata['status'] = status_match.group(1).strip()

            # Extract acceptance criteria
            ac_pattern = r'- \[ \]\s+(.+)$'
            ac_matches = re.findall(ac_pattern, story_content, re.MULTILINE)
            metadata['acceptance_criteria'] = ac_matches

            # Extract tasks
            task_pattern = r'- \[ \] Task \d+:\s+(.+)$'
            task_matches = re.findall(task_pattern, story_content, re.MULTILINE)
            metadata['tasks'] = task_matches

            logger.info(f"Parsed story metadata: {len(metadata['acceptance_criteria'])} AC, {len(metadata['tasks'])} tasks")
            return metadata

        except Exception as e:
            logger.error(f"Failed to parse story metadata: {e}")
            return None

    async def _validate_story_structure(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate story structure and completeness.

        Args:
            story_data: Parsed story metadata

        Returns:
            Dictionary with validation result
        """
        issues: List[str] = []
        warnings: List[str] = []

        # Check required fields
        if not story_data.get('title'):
            issues.append("Missing story title")

        if not story_data.get('status'):
            warnings.append("Missing status field")

        # Check acceptance criteria
        ac_count = len(story_data.get('acceptance_criteria', []))
        if ac_count == 0:
            warnings.append("No acceptance criteria found")
        elif ac_count < 3:
            warnings.append(f"Only {ac_count} acceptance criteria (recommended: 3+)")

        # Check tasks
        task_count = len(story_data.get('tasks', []))
        if task_count == 0:
            warnings.append("No tasks found")

        result: Dict[str, Any] = {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

        if issues:
            logger.warning(f"Story validation issues: {issues}")
        if warnings:
            logger.info(f"Story validation warnings: {warnings}")

        return result

    async def create_story(
        self,
        title: str,
        description: str,
        epic_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new story.

        Args:
            title: Story title
            description: Story description (user story format)
            epic_path: Path to epic file

        Returns:
            Created story metadata or None if failed
        """
        try:
            story_data: Dict[str, Any] = {
                'title': title,
                'description': description,
                'epic_path': epic_path,
                'status': 'draft',
                'acceptance_criteria': [],
                'tasks': []
            }

            logger.info(f"Created story: {title}")
            return story_data

        except Exception as e:
            logger.error(f"Failed to create story: {e}")
            return None

    async def create_stories_from_epic(self, epic_path: str) -> bool:
        """
        Create stories from an epic document using Claude.
        MANDATORY REQUIREMENT: All story documents must be created successfully to proceed.

        Args:
            epic_path: Path to the epic markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[SM Agent] Starting to create stories from Epic: {epic_path}")

        try:
            # Read epic content
            with open(epic_path, 'r', encoding='utf-8') as f:
                epic_content = f.read()

            # Extract story IDs from epic
            story_ids = self._extract_story_ids_from_epic(epic_content)
            logger.info(f"[SM Agent] Extracted {len(story_ids)} story IDs: {story_ids}")

            if not story_ids:
                logger.error("[SM Agent] No story IDs found")
                return False

            # Pre-check: verify if all story files already exist
            if await self._check_existing_stories(epic_path, story_ids):
                logger.info("[SM Agent] All story files already exist, skipping creation")
                return True

            # Build prompt
            prompt = self._build_claude_prompt(epic_path, story_ids)

            # Call Claude to create stories (retry logic is handled in _execute_claude_sdk)
            success = await self._execute_claude_sdk(prompt)

            if success:
                # Verify all story files
                all_passed, failed_stories = await self._verify_story_files(story_ids, epic_path)

                if all_passed:
                    logger.info("[SM Agent] [OK] All stories created successfully")
                    return True
                else:
                    logger.error(f"[SM Agent] [FAIL] Story verification failed: {failed_stories}")
                    return False
            else:
                logger.error("[SM Agent] Failed to create stories")
                return False

        except Exception as e:
            logger.error(f"[SM Agent] Exception during story creation: {type(e).__name__}: {e}")
            return False

    def _extract_story_ids_from_epic(self, content: str) -> List[str]:
        """
        Extract story IDs from epic document.

        Args:
            content: Epic document content

        Returns:
            List of story IDs (e.g., ["1.1", "1.2", ...])
        """
        story_ids: List[str] = []

        # Pattern 1: "### Story X.Y: Title"
        pattern1 = r'### Story\s+(\d+(?:\.\d+)?)\s*:\s*(.+?)(?:\n|\$)'
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        for story_num, _title in matches1:
            story_ids.append(story_num)
            logger.debug(f"Found story section: {story_num}")

        # Pattern 2: "**Story ID**: 001"
        pattern2 = r'\*\*Story ID\*\*\s*:\s*(\d+(?:\.\d+)?)'
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        for story_num in matches2:
            if story_num not in story_ids:
                story_ids.append(story_num)
                logger.debug(f"Found story ID: {story_num}")

        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique_story_ids: List[str] = []
        for story_id in story_ids:
            if story_id not in seen:
                seen.add(story_id)
                unique_story_ids.append(story_id)

        logger.debug(f"Extracted {len(unique_story_ids)} unique story IDs: {unique_story_ids}")
        return unique_story_ids

    async def _call_claude_create_stories(self, epic_path: str, story_ids: List[str]) -> bool:
        """
        Call Claude to create stories from epic.

        Args:
            epic_path: Path to the epic markdown file
            story_ids: List of story IDs to create

        Returns:
            True if successful, False otherwise
        """
        logger.info("Calling Claude to create stories")

        try:
            # Build prompt
            prompt = self._build_claude_prompt(epic_path, story_ids)

            # Execute Claude SDK call
            success = await self._execute_claude_sdk(prompt)

            return success

        except Exception as e:
            logger.error(f"Failed to call Claude for story creation: {e}")
            return False

    def _build_claude_prompt(self, epic_path: str, story_ids: List[str]) -> str:
        """
        Build the prompt for Claude to create stories.

        Args:
            epic_path: Path to the epic markdown file
            story_ids: List of story IDs

        Returns:
            Formatted prompt string
        """
        # Convert story IDs to comma-separated string
        story_list = ", ".join(story_ids)

        # Get relative path from current directory
        epic_rel_path = str(Path(epic_path))

        prompt = f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\sm.md @D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\sm.md {epic_rel_path} Create all story documents from epic: {story_list}. Save to @docs/stories. Change story document Status from "Draft" to "Approved".'

        logger.debug(f"Built prompt: {prompt}")
        return prompt

    async def _execute_claude_sdk(self, prompt: str) -> bool:
        """
        Execute Claude SDK call to create stories with timeout and retry logic.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            True if successful, False otherwise
        """
        max_retries = 1
        retry_delay = 1.0
        timeout_seconds = 1200

        for attempt in range(max_retries):
            try:
                logger.info(f"[SM Agent] Claude SDK call attempt {attempt + 1}/{max_retries}")
                start_time = time.time()

                # Check if SDK is available
                if query is None or ClaudeAgentOptions is None:
                    raise RuntimeError(
                        "Claude Agent SDK is required but not available. "
                        "Please install claude-agent-sdk."
                    )

                # Use asyncio.wait_for to implement timeout
                result = await asyncio.wait_for(
                    self._execute_sdk_with_logging(prompt),
                    timeout=timeout_seconds
                )

                elapsed = time.time() - start_time
                logger.info(f"[SM Agent] Call successful, took {elapsed:.2f} seconds")
                return result

            except asyncio.TimeoutError:
                logger.warning(f"[SM Agent] Call timeout (>{timeout_seconds} seconds), attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    logger.info(f"[SM Agent] Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(1.0)
                else:
                    logger.error(f"[SM Agent] Call failed, reached max retries ({max_retries})")
                    return False

            except Exception as e:
                logger.error(f"[SM Agent] Call exception: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"[SM Agent] Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(1.0)
                else:
                    logger.error("[SM Agent] Call failed, reached max retries")
                    return False

        return False

    async def _execute_sdk_with_logging(self, prompt: str) -> bool:
        """
        Execute SDK call with safe wrapper, session isolation, and logging.

        Uses SDKSessionManager to ensure SDK calls are isolated from other agents,
        preventing cancel scope propagation issues.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            bool - Whether the execution was successful
        """
        if query is None or ClaudeAgentOptions is None or ResultMessage is None:
            logger.error("Claude Agent SDK not installed. Please install claude-agent-sdk")
            return False

        # Get session manager for isolated execution
        session_manager = get_session_manager()

        async def sdk_call() -> bool:
            """Inner SDK call wrapped for isolation"""
            if ClaudeAgentOptions is None:
                logger.error("ClaudeAgentOptions is not available")
                return False

            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd())
            )
            sdk = SafeClaudeSDK(prompt, options, timeout=1200.0)
            # Execute SDK call and ensure it returns a bool
            result = await sdk.execute()
            return bool(result)

        # Execute with session isolation
        # Shield the SDK call to prevent external cancellation from affecting cancel scope
        try:
            result = await asyncio.wait_for(
                asyncio.shield(session_manager.execute_isolated(
                    agent_name="SMAgent",
                    sdk_func=sdk_call,
                    timeout=1200.0
                )),
                timeout=1300.0  # Slightly longer than SDK timeout
            )
        except asyncio.TimeoutError:
            logger.warning("[SM Agent] SDK call timed out after 1300s")
            return False
        except asyncio.CancelledError:
            logger.info("[SM Agent] SDK call was cancelled")
            return False

        if result.success:
            logger.info(f"[SM Agent] SDK call succeeded in {result.duration_seconds:.1f}s")
            return True
        elif result.error_type == SDKErrorType.CANCELLED:
            logger.info("[SM Agent] SDK call cancelled")
            return False
        elif result.error_type == SDKErrorType.TIMEOUT:
            logger.warning("[SM Agent] SDK call timed out")
            return False
        else:
            logger.warning(f"[SM Agent] SDK call failed: {result.error_message}")
            return False

    async def _verify_story_files(self, story_ids: List[str], epic_path: str) -> Tuple[bool, List[str]]:
        """
        Verify that all story files were successfully created with complete content.
        Based on the actual story template structure (story-template-v2)

        Args:
            story_ids: List of story IDs to verify
            epic_path: Path to the epic file

        Returns:
            Tuple[bool, List[str]] - (whether all succeeded, list of failed stories)
        """
        logger.info("[SM Agent] Starting to verify story files...")
        failed_stories: List[str] = []

        # Determine story file directory
        # Stories are in docs/stories, not docs/epics/stories
        epic_path_obj = Path(epic_path)
        project_root = epic_path_obj.parents[2]  # Go up to project root
        stories_dir = project_root / "docs" / "stories"

        if not stories_dir.exists():
            logger.error(f"[SM Agent] Stories directory does not exist: {stories_dir}")
            return False, story_ids

        for story_id in story_ids:
            # Find matching files using fuzzy matching
            story_file = self._find_story_file(stories_dir, story_id)

            if not story_file:
                logger.error(f"[SM Agent] Story file does not exist: {story_id}")
                failed_stories.append(story_id)
                continue

            # Verify file content
            try:
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Basic validation
                if len(content) < 100:
                    logger.warning(f"[SM Agent] Story file too short ({len(content)} chars): {story_file}")
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
                    "## Testing"
                ]

                missing_sections: List[str] = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)

                if missing_sections:
                    logger.warning(f"[SM Agent] Story file missing key sections {missing_sections}: {story_file}")
                    failed_stories.append(story_id)
                    continue

                logger.info(f"[SM Agent] [OK] Story file verification passed: {story_file}")

            except Exception as e:
                logger.error(f"[SM Agent] Failed to verify story file: {story_file}, error: {e}")
                failed_stories.append(story_id)

        if failed_stories:
            logger.error(f"[SM Agent] [FAIL] {len(failed_stories)} stories verification failed: {failed_stories}")
            return False, failed_stories
        else:
            logger.info(f"[SM Agent] [OK] All {len(story_ids)} stories verification passed")
            # Update story status from Draft to Ready for Development
            await self._update_story_statuses(story_ids, stories_dir)
            return True, []

    async def _update_story_statuses(self, story_ids: List[str], stories_dir: Path) -> None:
        """
        Update story status from Draft to Ready for Development.

        Args:
            story_ids: List of story IDs to update
            stories_dir: Directory containing story files
        """
        logger.info("[SM Agent] Updating story statuses to 'Ready for Development'")

        for story_id in story_ids:
            try:
                # Find matching story file using fuzzy matching
                story_file = self._find_story_file(stories_dir, story_id)

                if not story_file:
                    logger.warning(f"[SM Agent] Story file not found for ID: {story_id}")
                    continue

                # Read current content
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Update status from Draft to Ready for Development
                # Pattern 1: "**Status**: Draft"
                updated_content = re.sub(
                    r'(\*\*Status\*\*:\s*)Draft',
                    r'\1Ready for Development',
                    content
                )

                # Pattern 2: "## Status\n**Draft**"
                updated_content = re.sub(
                    r'(## Status\s*\n\*\*)(Draft)(\*\*)',
                    r'\1Ready for Development\3',
                    updated_content
                )

                # Write updated content back to file
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                logger.info(f"[SM Agent] Updated status for story {story_id}: Draft → Ready for Development")

            except Exception as e:
                logger.error(f"[SM Agent] Failed to update status for story {story_id}: {e}")

    async def _check_existing_stories(self, epic_path: str, story_ids: List[str]) -> bool:
        """
        Check if all story files already exist to avoid redundant creation.

        Args:
            epic_path: Path to the epic markdown file
            story_ids: List of story IDs to check

        Returns:
            True if all stories exist, False otherwise
        """
        try:
            # Determine story file directory
            epic_path_obj = Path(epic_path)
            # Epic is in docs/epics/, so stories should be in docs/stories
            docs_dir = epic_path_obj.parents[1]  # Go up to docs directory
            stories_dir = docs_dir / "stories"

            if not stories_dir.exists():
                logger.debug(f"[SM Agent] Stories directory does not exist: {stories_dir}")
                return False

            # Check each story file using fuzzy matching
            for story_id in story_ids:
                story_file = self._find_story_file(stories_dir, story_id)

                if not story_file:
                    logger.debug(f"[SM Agent] Story file not found: {story_id}")
                    return False  # At least one file is missing

            logger.info(f"[SM Agent] All {len(story_ids)} story files already exist")
            return True

        except Exception as e:
            logger.error(f"[SM Agent] Error checking existing stories: {e}")
            return False  # If check fails, assume files don't exist

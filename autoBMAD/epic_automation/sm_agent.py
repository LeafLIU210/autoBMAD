"""
SM Agent - Story Master Agent

Handles story creation, planning, and management tasks.
Integrates with task guidance for SM-specific operations.
"""

import logging
from typing import Dict, Any, Optional, List
import re

logger = logging.getLogger(__name__)


class SMAgent:
    """Story Master agent for handling story-related tasks."""

    def __init__(self):
        """Initialize SM agent."""
        self.name = "SM Agent"
        logger.info(f"{self.name} initialized")

    async def execute(
        self,
        story_content: str,
        task_guidance: str = ""
    ) -> bool:
        """
        Execute SM phase for a story.

        Args:
            story_content: Raw markdown content of the story
            task_guidance: Task guidance from .bmad-core/tasks/create-next-story.md

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

            # Process story according to task guidance
            if task_guidance:
                processed = await self._apply_task_guidance(story_data, task_guidance)
                if not processed:
                    logger.warning("Failed to apply task guidance")

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

    async def _apply_task_guidance(
        self,
        story_data: Dict[str, Any],
        task_guidance: str
    ) -> bool:
        """
        Apply task guidance to story processing.

        Args:
            story_data: Parsed story metadata
            task_guidance: Task guidance content

        Returns:
            True if guidance applied successfully, False otherwise
        """
        try:
            # Check for specific guidance patterns
            if "acceptance criteria" in task_guidance.lower():
                logger.info("Applying acceptance criteria guidance")

            if "task" in task_guidance.lower():
                logger.info("Applying task guidance")

            if "status" in task_guidance.lower():
                logger.info("Applying status guidance")

            # In a real implementation, this would use the guidance to
            # modify story processing logic
            # For now, we just log that we applied it

            return True

        except Exception as e:
            logger.error(f"Failed to apply task guidance: {e}")
            return False

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

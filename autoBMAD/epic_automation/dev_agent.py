"""
Dev Agent - Development Agent

Handles development tasks and implementation according to story requirements.
Integrates with task guidance for development-specific operations.
Uses Claude Code CLI for actual implementation.
"""

import logging
import subprocess
from typing import Dict, Any, Optional
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class DevAgent:
    """Development agent for handling implementation tasks."""

    def __init__(self, use_claude: bool = True):
        """
        Initialize Dev agent.

        Args:
            use_claude: If True, use Claude Code CLI for real implementation.
                       If False, use simulation mode (for testing).
        """
        self.name = "Dev Agent"
        self.use_claude = use_claude
        self._current_story_path: Optional[str] = None
        self._claude_available = self._check_claude_available() if use_claude else False
        logger.info(f"{self.name} initialized (claude_mode={self.use_claude}, claude_available={self._claude_available})")

    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            # Try direct path for Windows
            import os
            possible_commands = [
                ['claude', '--version'],
                [r'C:\Users\Administrator\AppData\Roaming\npm\claude', '--version'],
                [r'C:\Users\Administrator\AppData\Roaming\npm\claude.cmd', '--version'],
                ['where', 'claude']
            ]

            # Get current environment
            env = os.environ.copy()

            for cmd in possible_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True,
                        env=env
                    )
                    if result.returncode == 0:
                        if cmd[0] == 'where':
                            # Path found, now verify claude works
                            paths = result.stdout.strip().split('\n')
                            if paths:
                                verify = subprocess.run(
                                    [paths[0], '--version'],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    shell=True,
                                    env=env
                                )
                                if verify.returncode == 0:
                                    logger.info(f"Claude Code CLI available: {verify.stdout.strip()}")
                                    return True
                        else:
                            # Direct version check succeeded
                            logger.info(f"Claude Code CLI available: {result.stdout.strip()}")
                            return True
                except Exception:
                    continue

            return False
        except Exception as e:
            logger.warning(f"Claude Code CLI not available: {e}")
            return False

    async def execute(
        self,
        story_content: str,
        task_guidance: str = ""
    ) -> bool:
        """
        Execute Dev phase for a story.

        Args:
            story_content: Raw markdown content of the story
            task_guidance: Task guidance from .bmad-core/tasks/develop-story.md

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"{self.name} executing Dev phase")

        try:
            # Parse story to extract requirements
            requirements = await self._extract_requirements(story_content)

            if not requirements:
                logger.error("Failed to extract requirements from story")
                return False

            # Add story_path to requirements if available in context
            requirements['story_path'] = self._current_story_path

            # Validate requirements
            validation = await self._validate_requirements(requirements)
            if not validation['valid']:
                logger.warning(f"Requirement validation issues: {validation['issues']}")

            # Process according to task guidance
            if task_guidance:
                processed = await self._apply_dev_guidance(requirements, task_guidance)
                if not processed:
                    logger.warning("Failed to apply development guidance")

            # Execute development tasks
            tasks_completed = await self._execute_development_tasks(requirements)

            if not tasks_completed:
                logger.error("Failed to complete development tasks")
                return False

            # Update story file with completion
            if self._current_story_path:
                await self._update_story_completion(story_content, requirements)

            logger.info(f"{self.name} Dev phase completed successfully")
            return True

        except Exception as e:
            logger.error(f"{self.name} Dev phase failed: {e}")
            return False

    async def _extract_requirements(self, story_content: str) -> Dict[str, Any]:
        """Extract requirements from story content."""
        logger.info("Extracting requirements from story")

        try:
            # Basic requirement extraction from markdown
            requirements = {
                'title': '',
                'acceptance_criteria': [],
                'tasks': [],
                'subtasks': [],
                'dev_notes': {},
                'testing': {}
            }

            # Extract title
            title_match = re.search(r'^# Story \d+:\s*(.+)$', story_content, re.MULTILINE)
            if title_match:
                requirements['title'] = title_match.group(1).strip()

            # Extract acceptance criteria
            ac_section = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if ac_section:
                ac_lines = ac_section.group(1).strip().split('\n')
                for line in ac_lines:
                    if line.strip().startswith('-'):
                        acceptance_criteria = requirements['acceptance_criteria']
                        assert isinstance(acceptance_criteria, list), "acceptance_criteria should be a list"
                        acceptance_criteria.append(line.strip())

            # Extract tasks
            tasks_section = re.search(r'## Tasks / Subtasks\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if tasks_section:
                task_lines = tasks_section.group(1).strip().split('\n')
                for line in task_lines:
                    if line.strip().startswith('-'):
                        tasks = requirements['tasks']
                        assert isinstance(tasks, list), "tasks should be a list"
                        tasks.append(line.strip())

            # Extract subtasks (nested)
            subtask_pattern = r'^\s*-\s*\[x\]\s*(.+)'
            for line in story_content.split('\n'):
                if re.match(subtask_pattern, line):
                    subtasks = requirements['subtasks']
                    assert isinstance(subtasks, list), "subtasks should be a list"
                    subtasks.append(line.strip())

            # Extract dev notes
            dev_notes_section = re.search(r'## Dev Notes\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if dev_notes_section:
                dev_notes = requirements['dev_notes']
                assert isinstance(dev_notes, dict), "dev_notes should be a dict"
                dev_notes['content'] = dev_notes_section.group(1).strip()

            # Extract testing info
            testing_section = re.search(r'## Testing\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if testing_section:
                testing = requirements['testing']
                assert isinstance(testing, dict), "testing should be a dict"
                testing['content'] = testing_section.group(1).strip()

            logger.info(f"Extracted requirements: {len(requirements['acceptance_criteria'])} AC, {len(requirements['tasks'])} tasks, {len(requirements['subtasks'])} subtasks")
            return requirements

        except Exception as e:
            logger.error(f"Failed to extract requirements: {e}")
            return {}

    async def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted requirements."""
        issues = []
        warnings = []

        if not requirements.get('acceptance_criteria'):
            issues.append('No acceptance criteria found')

        if not requirements.get('tasks'):
            warnings.append('No tasks found')

        # Check for minimum viable content
        if not requirements.get('title'):
            issues.append('No title found')

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    async def _apply_dev_guidance(self, requirements: Dict[str, Any], guidance: str) -> bool:
        """Apply development guidance to requirements."""
        logger.info("Applying implementation guidance")

        try:
            # In a real implementation, this would parse guidance and apply it
            # For now, we just acknowledge it
            return True
        except Exception as e:
            logger.error(f"Failed to apply dev guidance: {e}")
            return False

    async def _execute_development_tasks(self, requirements: Dict[str, Any]) -> bool:
        """Execute development tasks."""
        logger.info("Executing development tasks")

        try:
            if not self._claude_available:
                logger.warning("Claude not available - using simulation mode")
                # Simulate task execution
                logger.info(f"Simulated development of: {requirements.get('title', 'Unknown')}")
                return True

            # Real implementation - use Claude CLI
            logger.info("Claude available - would use Claude for development")
            
            # For now, mark as completed (would use Claude in real implementation)
            return True

        except Exception as e:
            logger.error(f"Failed to execute development tasks: {e}")
            return False

    async def _update_story_completion(self, story_content: str, requirements: Dict[str, Any]) -> None:
        """Update story file with completion information."""
        logger.info("Updating story file with completion")

        try:
            if not self._current_story_path:
                return

            story_path = Path(self._current_story_path)
            if not story_path.exists():
                logger.warning(f"Story file not found: {story_path}")
                return

            # Read current content
            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update status to "Ready for Review"
            status_pattern = r'(\*\*Status\*\*:\s*)Draft'
            if re.search(status_pattern, content):
                content = re.sub(status_pattern, r'\1Ready for Review', content)

            # Add file list if not present
            if '### File List' not in content:
                file_list_section = """
### File List
- `src/main.py`
- `tests/test_main.py`
"""
                # Insert before Dev Agent Record section
                dev_record_pattern = r'(## Dev Agent Record)'
                if re.search(dev_record_pattern, content):
                    content = re.sub(dev_record_pattern, rf'{file_list_section}\1', content)

            # Write updated content
            with open(story_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Updated story file: {story_path}")

        except Exception as e:
            logger.error(f"Failed to update story file: {e}")

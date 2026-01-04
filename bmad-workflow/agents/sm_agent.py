"""
SM Agent for BMAD Story Creation

This agent is responsible for preparing comprehensive, actionable story documents
based on epic definitions. It loads create-next-story.md guidance and uses
Claude SDK for intelligent story creation.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from anthropic.types import MessageParam

from .base_agent import BaseAgent


class SMAgent(BaseAgent):
    """
    Scrum Master Agent for BMAD Story Creation.

    Extends BaseAgent to provide story creation capabilities,
    loading create-next-story.md guidance and implementing
    comprehensive story preparation workflows.
    """

    def __init__(self):
        """Initialize the SM Agent with create-next-story task type."""
        super().__init__(agent_name="sm", task_type="create-next-story")
        self.logger = logging.getLogger("bmad.sm_agent")
        self.story_template_path = None
        self._reset_session_state()

    def _reset_session_state(self) -> None:
        """Reset agent session state."""
        self.current_epic: Optional[str] = None
        self.current_story_num: Optional[int] = None
        self.story_title: Optional[str] = None
        self.story_path: Optional[Path] = None

    def prepare_next_story(self, epic_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare the next story based on project progress.

        Args:
            epic_id: Optional epic ID to work on. If not provided,
                    will identify the next story automatically.

        Returns:
            Dictionary with story preparation results.

        Raises:
            Exception: If story preparation fails.
        """
        try:
            self.logger.info("Starting story preparation workflow")
            self.reset_session()
            self._reset_session_state()

            # Load task guidance
            task_guidance = self.load_task_guidance()

            # Get system prompt
            system_prompt = self.get_system_prompt()

            # Prepare the story creation prompt
            story_creation_prompt = self._build_story_creation_prompt(epic_id)

            # Call Claude API
            messages: List[MessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": story_creation_prompt}
            ]

            response = self.call_claude(messages, max_tokens=8192)

            # Parse the response and create the story file
            story_content = self._extract_story_content(response)
            story_path = self._write_story_file(story_content)

            result = {
                "status": "success",
                "story_path": str(story_path),
                "story_id": self._get_story_id_from_path(story_path),
                "guidance_used": len(task_guidance),
                "response_content_length": len(str(response.get('content', ''))),
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Story preparation completed successfully: {story_path}")
            return result

        except Exception as e:
            self.logger.error(f"Story preparation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_story_creation_prompt(self, epic_id: Optional[str] = None) -> str:
        """
        Build the prompt for story creation.

        Args:
            epic_id: Optional epic ID to work on.

        Returns:
            The story creation prompt.
        """
        prompt_parts = [
            "Please prepare the next story for implementation based on the task guidance.",
            "",
            "Instructions:",
            "1. Load and analyze the core configuration (.bmad-core/core-config.yaml)",
            "2. Identify the next story to create (or use provided epic_id if given)",
            "3. Review existing stories and epic definitions",
            "4. Gather architecture context from relevant documents",
            "5. Create a comprehensive, actionable story file using the story template",
            "6. Ensure all technical details are cited with source references",
            "7. Generate detailed, sequential tasks based on epic requirements",
            "8. Execute the story-draft-checklist",
            "",
            f"Working epic: {epic_id if epic_id else 'Auto-detect next story'}",
            "",
            "Please proceed with story preparation and provide:",
            "- The created story file path",
            "- A summary of key technical components included",
            "- Any deviations or conflicts noted",
            "- Checklist execution results"
        ]

        return "\n".join(prompt_parts)

    def _extract_story_content(self, response: Dict[str, Any]) -> str:
        """
        Extract story content from Claude response.

        Args:
            response: The response from Claude API.

        Returns:
            The story content as a string.

        Raises:
            Exception: If content extraction fails.
        """
        try:
            content_blocks = response.get('content', [])
            if not content_blocks:
                raise Exception("No content blocks in response")

            # Extract text from content blocks
            story_content = ""
            for block in content_blocks:
                if hasattr(block, 'text'):
                    story_content += block.text
                elif isinstance(block, dict) and 'text' in block:
                    story_content += block['text']

            if not story_content:
                raise Exception("No story content extracted from response")

            self.logger.info(f"Extracted story content: {len(story_content)} characters")
            return story_content

        except Exception as e:
            self.logger.error(f"Failed to extract story content: {e}")
            raise Exception(f"Content extraction failed: {e}")

    def _write_story_file(self, story_content: str) -> Path:
        """
        Write story content to file.

        Args:
            story_content: The story content to write.

        Returns:
            Path to the created story file.

        Raises:
            Exception: If file writing fails.
        """
        try:
            # Determine story location from config
            project_root = Path(__file__).parent.parent.parent
            stories_dir = project_root / "docs" / "stories"

            # Ensure stories directory exists
            stories_dir.mkdir(parents=True, exist_ok=True)

            # Generate story filename (using timestamp for uniqueness in draft mode)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            story_filename = f"story-draft-{timestamp}.md"
            story_path = stories_dir / story_filename

            # Write the story file
            with open(story_path, 'w', encoding='utf-8') as f:
                f.write(story_content)

            self.logger.info(f"Story file written: {story_path}")
            self.story_path = story_path
            return story_path

        except Exception as e:
            self.logger.error(f"Failed to write story file: {e}")
            raise Exception(f"File writing failed: {e}")

    def _get_story_id_from_path(self, story_path: Path) -> str:
        """
        Extract story ID from story file path.

        Args:
            story_path: Path to the story file.

        Returns:
            Story ID string.
        """
        # For draft stories, use filename-based ID
        return story_path.stem

    def validate_story(self, story_path: Path) -> Dict[str, Any]:
        """
        Validate a created story for completeness and quality.

        Args:
            story_path: Path to the story file to validate.

        Returns:
            Dictionary with validation results.
        """
        try:
            self.logger.info(f"Validating story: {story_path}")

            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic validation checks
            checks = {
                "has_title": "# " in content,
                "has_story_section": "## Story" in content,
                "has_acceptance_criteria": "## Acceptance Criteria" in content,
                "has_tasks": "## Tasks / Subtasks" in content,
                "has_dev_notes": "## Dev Notes" in content,
                "has_testing_section": "## Testing" in content,
                "has_file_list": "## File List" in content
            }

            passed = sum(checks.values())
            total = len(checks)
            validation_score = (passed / total) * 100 if total > 0 else 0

            result = {
                "status": "success" if validation_score >= 80 else "warnings",
                "validation_score": validation_score,
                "checks": checks,
                "passed_checks": passed,
                "total_checks": total,
                "story_path": str(story_path),
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Validation completed: {validation_score}% ({passed}/{total} checks passed)")
            return result

        except Exception as e:
            self.logger.error(f"Story validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "story_path": str(story_path),
                "timestamp": datetime.now().isoformat()
            }

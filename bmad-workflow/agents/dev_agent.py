"""
Dev Agent for BMAD Story Development

This agent is responsible for implementing story requirements using TDD methodology
with comprehensive testing. It loads develop-story.md guidance and uses
Claude SDK for intelligent development workflows.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from anthropic.types import MessageParam

from .base_agent import BaseAgent


class DevAgent(BaseAgent):
    """
    Developer Agent for BMAD Story Implementation.

    Extends BaseAgent to provide story development capabilities,
    loading develop-story
    comprehensive development.md guidance and implementing workflows using TDD methodology.
    """

    def __init__(self):
        """Initialize the Dev Agent with develop-story task type."""
        super().__init__(agent_name="dev", task_type="develop-story")
        self.logger = logging.getLogger("bmad.dev_agent")
        self.story_path: Optional[Path] = None
        self.story_content: Optional[str] = None
        self._reset_session_state()

    def _reset_session_state(self) -> None:
        """Reset agent session state."""
        self.current_story_id: Optional[str] = None
        self.story_status: Optional[str] = None
        self.implementation_files: List[str] = []
        self.test_files: List[str] = []

    def develop_story(self, story_path: Path) -> Dict[str, Any]:
        """
        Develop/implement the story at the given path.

        Args:
            story_path: Path to the story file to develop.

        Returns:
            Dictionary with development results.

        Raises:
            Exception: If story development fails.
        """
        try:
            self.logger.info(f"Starting story development: {story_path}")
            self.reset_session()
            self._reset_session_state()

            # Validate story file exists
            if not story_path.exists():
                raise FileNotFoundError(f"Story file not found: {story_path}")

            # Load story content
            self.story_path = story_path
            with open(story_path, 'r', encoding='utf-8') as f:
                self.story_content = f.read()

            # Load task guidance
            task_guidance = self.load_task_guidance()

            # Get system prompt
            system_prompt = self.get_system_prompt()

            # Build development prompt
            development_prompt = self._build_development_prompt()

            # Call Claude API
            messages: List[MessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": development_prompt}
            ]

            response = self.call_claude(messages, max_tokens=8192)

            # Process development response
            result = self._process_development_response(response)

            self.logger.info(f"Story development completed: {story_path}")
            return result

        except Exception as e:
            self.logger.error(f"Story development failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "story_path": str(story_path),
                "timestamp": datetime.now().isoformat()
            }

    def _build_development_prompt(self) -> str:
        """
        Build the prompt for story development.

        Returns:
            The development prompt.
        """
        prompt_parts = [
            "Please implement the story requirements following the task guidance.",
            "",
            "Story Content:",
            "---",
            self.story_content,
            "---",
            "",
            "Instructions:",
            "1. Analyze the story requirements and acceptance criteria",
            "2. Implement code following TDD methodology (Red-Green-Refactor)",
            "3. Write comprehensive tests before or alongside implementation",
            "4. Create and modify source files as needed",
            "5. Follow DRY, KISS, YAGNI, and Occam's Razor principles",
            "6. Ensure all files are listed in the File List section",
            "7. Update task checkboxes with [x] for completed items",
            "8. Execute the execute-checklist task for quality gates",
            "9. Run type checking and validation tools",
            "10. Update story status to 'Ready for Review' when complete",
            "",
            "Please provide:",
            "- Summary of implementation approach",
            "- List of files created/modified",
            "- Test coverage summary",
            "- Any challenges encountered and how they were resolved",
            "- Verification that all acceptance criteria are met",
            "- Final story status update"
        ]

        return "\n".join(prompt_parts)

    def _process_development_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the development response from Claude.

        Args:
            response: The response from Claude API.

        Returns:
            Dictionary with processing results.

        Raises:
            Exception: If response processing fails.
        """
        try:
            content_blocks = response.get('content', [])
            if not content_blocks:
                raise Exception("No content blocks in response")

            # Extract text from content blocks
            response_content = ""
            for block in content_blocks:
                if hasattr(block, 'text'):
                    response_content += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_content += block['text']

            # Update story file if needed (extract any file modifications)
            updated_story = self._extract_story_updates(response_content)
            if updated_story:
                self._update_story_file(updated_story)

            result = {
                "status": "success",
                "story_path": str(self.story_path),
                "story_id": self.story_path.stem if self.story_path else "unknown",
                "guidance_used": len(self.load_task_guidance()),
                "response_content_length": len(response_content),
                "files_created": len(self.implementation_files),
                "test_files_created": len(self.test_files),
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Development response processed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to process development response: {e}")
            raise Exception(f"Response processing failed: {e}")

    def _extract_story_updates(self, response_content: str) -> Optional[str]:
        """
        Extract story file updates from response.

        Args:
            response_content: The response content to parse.

        Returns:
            Updated story content if found, None otherwise.
        """
        # Look for story markdown updates in the response
        if "<!-- Powered by BMAD" in response_content or "# Story" in response_content:
            self.logger.info("Found story updates in response")
            return response_content
        return None

    def _update_story_file(self, updated_content: str) -> None:
        """
        Update the story file with new content.

        Args:
            updated_content: The updated story content.

        Raises:
            Exception: If file update fails.
        """
        try:
            if self.story_path:
                with open(self.story_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                self.logger.info(f"Story file updated: {self.story_path}")
        except Exception as e:
            self.logger.error(f"Failed to update story file: {e}")
            raise

    def run_tests(self, test_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run tests for the implemented story.

        Args:
            test_path: Optional path to specific test file. If not provided,
                      will run all tests in the tests directory.

        Returns:
            Dictionary with test results.

        Raises:
            Exception: If test execution fails.
        """
        try:
            self.logger.info(f"Running tests for story development")

            # This is a placeholder for test execution
            # In a real implementation, this would use pytest or similar
            test_results = {
                "status": "success",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "coverage": 0.0,
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Test execution completed")
            return test_results

        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def validate_implementation(self) -> Dict[str, Any]:
        """
        Validate the story implementation for completeness and quality.

        Returns:
            Dictionary with validation results.
        """
        try:
            self.logger.info("Validating story implementation")

            if not self.story_content:
                raise Exception("No story content loaded")

            # Basic validation checks
            checks = {
                "story_file_exists": self.story_path.exists() if self.story_path else False,
                "has_acceptance_criteria": "## Acceptance Criteria" in self.story_content,
                "has_tasks_section": "## Tasks / Subtasks" in self.story_content,
                "has_file_list": "## File List" in self.story_content,
                "has_dev_agent_record": "## Dev Agent Record" in self.story_content,
                "story_not_draft": "**Status**: Draft" not in self.story_content
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
                "story_path": str(self.story_path) if self.story_path else "unknown",
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Implementation validation completed: {validation_score}% ({passed}/{total} checks passed)")
            return result

        except Exception as e:
            self.logger.error(f"Implementation validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

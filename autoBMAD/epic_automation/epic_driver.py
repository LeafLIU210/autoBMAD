"""
Epic Driver - Self-Contained BMAD Automation

Main orchestrator for the BMAD automation system.
Reads epic markdown files and drives SM-Dev-QA cycle.
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EpicDriver:
    """Main orchestrator for BMAD epic automation."""

    def __init__(self, epic_path: str, tasks_dir: str = ".bmad-core/tasks",
                 max_iterations: int = 3, retry_failed: bool = False,
                 verbose: bool = False, concurrent: bool = False,
                 use_claude: bool = True):
        """
        Initialize EpicDriver.

        Args:
            epic_path: Path to the epic markdown file
            tasks_dir: Directory containing task guidance files
            max_iterations: Maximum retry attempts for failed stories
            retry_failed: Enable automatic retry of failed stories
            verbose: Enable detailed logging output
            concurrent: Process stories in parallel (experimental)
            use_claude: Use Claude Code CLI for real implementation (default True)
        """
        self.epic_path = Path(epic_path)
        self.tasks_dir = Path(tasks_dir)
        self.stories = []
        self.current_story_index = 0
        self.max_iterations = max_iterations
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.concurrent = concurrent
        self.use_claude = use_claude
        self.task_guidance = {}

        # Import agent classes
        try:
            from sm_agent import SMAgent  # type: ignore
            from dev_agent import DevAgent  # type: ignore
            from qa_agent import QAAgent  # type: ignore
            from state_manager import StateManager  # type: ignore

            self.sm_agent = SMAgent()
            self.dev_agent = DevAgent(use_claude=use_claude)
            self.qa_agent = QAAgent()
            self.state_manager = StateManager()
        except ImportError as e:
            logger.error(f"Failed to import agent classes: {e}")
            sys.exit(1)

    async def load_task_guidance(self) -> None:
        """
        Load task guidance from .bmad-core/tasks/*.md files.

        Reads task files and extracts prompt knowledge for agents.
        """
        logger.info(f"Loading task guidance from {self.tasks_dir}")

        if not self.tasks_dir.exists():
            logger.warning(f"Tasks directory not found: {self.tasks_dir}")
            return

        task_files = {
            "create-next-story": "sm_agent",
            "develop-story": "dev_agent",
            "review-story": "qa_agent"
        }

        for task_file, agent_name in task_files.items():
            task_path = self.tasks_dir / f"{task_file}.md"
            if task_path.exists():
                try:
                    with open(task_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.task_guidance[agent_name] = content
                        logger.info(f"Loaded {task_file}.md for {agent_name}")
                except Exception as e:
                    logger.error(f"Failed to load {task_path}: {e}")
            else:
                logger.warning(f"Task file not found: {task_path}")

    def parse_epic(self) -> List[Dict[str, Any]]:
        """
        Parse epic markdown file and extract story information.

        Supports implicit numbering association:
        - Extracts story IDs from Epic document
        - Searches for story files by filename pattern (e.g., 001.xxx.md)
        - No explicit Markdown links required

        Returns:
            List of story dictionaries with path and metadata
        """
        logger.info(f"Parsing epic: {self.epic_path}")

        if not self.epic_path.exists():
            logger.error(f"Epic file not found: {self.epic_path}")
            return []

        try:
            with open(self.epic_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Step 1: Extract story IDs from Epic document
            story_ids = self._extract_story_ids_from_epic(content)

            if not story_ids:
                logger.warning("No stories found in epic document")
                return []

            # Step 2: Search for story files in docs-copy/stories/ directory
            stories_dir = self.epic_path.parent.parent / "docs-copy" / "stories"

            # Fallback: try relative to epic path
            if not stories_dir.exists():
                stories_dir = self.epic_path.parent / "stories"

            # Fallback: try autoBMAD/stories
            if not stories_dir.exists():
                autoBMAD_dir = self.epic_path.parent.parent
                if autoBMAD_dir.name == "autoBMAD":
                    stories_dir = autoBMAD_dir / "stories"
                elif (autoBMAD_dir.parent / "autoBMAD").exists():
                    stories_dir = autoBMAD_dir.parent / "autoBMAD" / "stories"

            logger.debug(f"Searching for story files in: {stories_dir}")

            stories = []
            found_stories = []

            if stories_dir.exists():
                # Find all story files matching pattern 001.*.md, 002.*.md, etc.
                story_files = list(stories_dir.glob("*.md"))
                logger.debug(f"Found {len(story_files)} markdown files in stories directory")

                # Create a mapping of story numbers to files
                story_file_map = {}
                for story_file in story_files:
                    # Extract story number from filename: 001.xxx.md -> 001
                    match = re.match(r'^(\d{3})\.', story_file.name)
                    if match:
                        story_number = match.group(1)
                        story_file_map[story_number] = story_file

                # Match story IDs to files
                for story_id in story_ids:
                    # Extract story number: "001" or "001: Title" -> "001"
                    story_number = story_id.split(':')[0].strip().zfill(3)

                    if story_number in story_file_map:
                        story_file = story_file_map[story_number]
                        stories.append({
                            'id': story_id,
                            'path': str(story_file.resolve()),
                            'name': story_file.name
                        })
                        found_stories.append(story_id)
                        logger.info(f"Found story: {story_id} at {story_file}")
                    else:
                        # Story file not found
                        logger.warning(f"Story file not found for ID: {story_id} (looking for {stories_dir}/*{story_number}*.md)")

            else:
                logger.warning(f"Stories directory not found: {stories_dir}")
                logger.info("Tried searching in:")
                logger.info(f"  - {self.epic_path.parent.parent / 'docs-copy' / 'stories'}")
                logger.info(f"  - {self.epic_path.parent / 'stories'}")
                logger.info(f"  - {(self.epic_path.parent.parent / 'autoBMAD' / 'stories') if self.epic_path.parent.parent.name != 'autoBMAD' else 'N/A'}")

            # Warn about stories not found
            missing_stories = set(story_ids) - set(found_stories)
            if missing_stories:
                logger.warning(f"Missing story files for IDs: {missing_stories}")

            # Sort stories by story ID
            stories.sort(key=lambda x: x['id'])

            self.stories = stories
            logger.info(f"Epic parsing complete: {len(stories)}/{len(story_ids)} stories found")

            return stories

        except Exception as e:
            logger.error(f"Failed to parse epic: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    def _extract_story_ids_from_epic(self, content: str) -> List[str]:
        """
        Extract story IDs from epic document.

        Looks for story sections like:
        ### Story 1: Title
        **Story ID**: 001

        Args:
            content: Epic document content

        Returns:
            List of story IDs (e.g., ["001", "001: Title", ...])
        """
        story_ids = []

        # Pattern 1: "### Story X: Title"
        pattern1 = r'### Story\s+(\d+)\s*:\s*(.+?)(?:\n|$)'
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        for story_num, title in matches1:
            story_id = f"{story_num}: {title}"
            story_ids.append(story_id)
            logger.debug(f"Found story section: {story_id}")

        # Pattern 2: "**Story ID**: 001"
        pattern2 = r'\*\*Story ID\*\*\s*:\s*(\d+)'
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        for story_num in matches2:
            # Check if already added
            story_id = f"{story_num}"
            if story_id not in story_ids:
                story_ids.append(story_id)
                logger.debug(f"Found story ID: {story_id}")

        # Remove duplicates while preserving order
        seen = set()
        unique_story_ids = []
        for story_id in story_ids:
            # Use story number as uniqueness key
            key = story_id.split(':')[0].strip().zfill(3)
            if key not in seen:
                seen.add(key)
                unique_story_ids.append(story_id)

        logger.debug(f"Extracted {len(unique_story_ids)} unique story IDs: {unique_story_ids}")

        return unique_story_ids

    def _create_missing_story(self, story_path: Path, story_id: str) -> bool:
        """
        Create a missing story file with a basic template.

        Args:
            story_path: Path where the story file should be created
            story_id: Story identifier from the epic

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            story_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract story title from the ID
            # Format: "001: User Registration API" -> Title: "User Registration API"
            title = story_id.split(':', 1)[1].strip() if ':' in story_id else story_id

            # Create basic story template
            story_content = f"""# Story {story_id}

**Epic**: {self.epic_path.name}

---

## Status
**Status**: Draft

---

## Story
**As a** [user type],
**I want to** [action],
**So that** [benefit]

---

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Tasks / Subtasks
- [ ] Task 1: Description
  - [ ] Subtask 1.1: Detail
  - [ ] Subtask 1.2: Detail

---

## Dev Notes
### Implementation Notes
- Key technical details
- Architecture decisions
- Dependencies

### Technical Details
- Specific technical implementation guidance
- API specifications
- Data models
- Component structure

---

## Testing
### Testing Standards
- Framework used
- Coverage requirements
- Test types

### Specific Testing Requirements
- Unit tests
- Integration tests
- E2E tests

---

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-04 | 1.0 | Initial story creation | Epic Driver |

---

## Dev Agent Record
*Populated during implementation*

### Agent Model Used
{{agent_model_name_version}}

### Debug Log References
*Links to debug logs*

### Completion Notes List
*Implementation notes*

### File List
*Files created/modified*

### Change Log
*Detailed change log*

---

## QA Results
*Populated by QA agent*
"""

            # Write the story file
            with open(story_path, 'w', encoding='utf-8') as f:
                f.write(story_content)

            logger.info(f"Successfully created story file: {story_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create story file {story_path}: {e}")
            return False

    async def execute_sm_phase(self, story_path: str) -> bool:
        """
        Execute SM (Story Master) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing SM phase for {story_path}")

        try:
            # Get task guidance for SM agent
            guidance = self.task_guidance.get("sm_agent", "")

            # Read story content
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()

            # Execute SM phase
            result = await self.sm_agent.execute(story_content, guidance)

            # Update state
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="sm_completed",
                phase="sm"
            )

            logger.info(f"SM phase completed for {story_path}")
            return result

        except Exception as e:
            logger.error(f"SM phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="error",
                error=str(e)
            )
            return False

    async def execute_dev_phase(self, story_path: str, iteration: int = 1) -> bool:
        """
        Execute Dev (Development) phase for a story.

        Args:
            story_path: Path to the story markdown file
            iteration: Current iteration count (for safety)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing Dev phase for {story_path} (iteration {iteration})")

        # Safety guard against infinite loops
        if iteration > self.max_iterations:
            logger.error(f"Max iterations ({self.max_iterations}) reached for {story_path}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="failed",
                error="Max iterations exceeded"
            )
            return False

        try:
            # Get task guidance for Dev agent
            guidance = self.task_guidance.get("dev_agent", "")

            # Read story content
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()

            # Set current story path for dev agent
            self.dev_agent._current_story_path = story_path

            # Execute Dev phase
            result = await self.dev_agent.execute(story_content, guidance)

            # Update state
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="dev_completed",
                phase="dev",
                iteration=iteration
            )

            logger.info(f"Dev phase completed for {story_path}")
            return result

        except Exception as e:
            logger.error(f"Dev phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="error",
                error=str(e)
            )
            return False

    async def execute_qa_phase(self, story_path: str) -> bool:
        """
        Execute QA (Quality Assurance) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if QA passes, False otherwise
        """
        logger.info(f"Executing QA phase for {story_path}")

        try:
            # Get task guidance for QA agent
            guidance = self.task_guidance.get("qa_agent", "")

            # Read story content
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()

            # Execute QA phase with tools integration
            qa_result = await self.qa_agent.execute(
                story_content,
                task_guidance=guidance,
                use_qa_tools=True,
                source_dir="src",
                test_dir="tests"
            )

            # Update state with QA result
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="qa_completed",
                phase="qa",
                qa_result=qa_result
            )

            if qa_result.get("passed", False):
                logger.info(f"QA phase passed for {story_path}")
                await self.state_manager.update_story_status(
                    story_path=story_path,
                    status="completed"
                )
                return True
            else:
                logger.warning(f"QA phase failed for {story_path}: {qa_result}")
                return False

        except Exception as e:
            logger.error(f"QA phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="error",
                error=str(e)
            )
            return False

    async def process_story(self, story: Dict[str, Any]) -> bool:
        """
        Process a single story through SM-Dev-QA cycle.

        Args:
            story: Story dictionary with path and metadata

        Returns:
            True if story completed successfully, False otherwise
        """
        story_path = story['path']
        story_id = story['id']
        logger.info(f"Processing story {story_id}: {story_path}")

        try:
            # Check if story already completed
            existing_status = await self.state_manager.get_story_status(story_path)
            if existing_status and existing_status.get('status') == 'completed':
                logger.info(f"Story already completed: {story_path}")
                return True

            # Execute phases
            # SM Phase
            sm_success = await self.execute_sm_phase(story_path)
            if not sm_success:
                logger.error(f"SM phase failed for {story_path}")
                return False

            # Dev Phase (with iteration support based on retry_failed flag)
            iteration = 1
            while True:
                dev_success = await self.execute_dev_phase(story_path, iteration)
                if not dev_success:
                    logger.error(f"Dev phase failed for {story_path}")
                    return False

                # QA Phase
                qa_passed = await self.execute_qa_phase(story_path)

                if qa_passed:
                    logger.info(f"Story {story_id} completed successfully")
                    return True
                else:
                    # QA failed, decide whether to retry based on retry_failed flag
                    if not self.retry_failed:
                        logger.warning(f"QA failed for {story_path}. Use --retry-failed to enable automatic retries")
                        return False

                    # QA failed but retry is enabled
                    iteration += 1
                    if iteration > self.max_iterations:
                        logger.error(f"Max iterations ({self.max_iterations}) reached for {story_path}")
                        return False

                    logger.info(f"QA failed, retrying Dev phase (iteration {iteration}/{self.max_iterations})")

        except Exception as e:
            logger.error(f"Failed to process story {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="error",
                error=str(e)
            )
            return False

    async def run(self) -> bool:
        """
        Main execution loop for the epic driver.

        Returns:
            True if all stories completed successfully, False otherwise
        """
        logger.info("Starting Epic Driver")

        # Log configuration
        if self.verbose:
            logger.debug(f"Configuration: max_iterations={self.max_iterations}, "
                        f"retry_failed={self.retry_failed}, verbose={self.verbose}, "
                        f"concurrent={self.concurrent}")

        if self.concurrent:
            logger.warning("Concurrent processing is experimental and not yet implemented")

        try:
            # Load task guidance
            await self.load_task_guidance()

            # Parse epic
            stories = self.parse_epic()
            if not stories:
                logger.error("No stories found in epic")
                return False

            # Process each story
            success_count = 0
            for story in stories:
                if self.verbose:
                    logger.debug(f"Processing story: {story['id']}")

                if await self.process_story(story):
                    success_count += 1
                elif not self.retry_failed:
                    # If retry is disabled and a story fails, we could continue or stop
                    # For now, we'll continue to the next story
                    if self.verbose:
                        logger.debug(f"Continuing to next story after failure: {story['id']}")

            # Summary
            total_stories = len(stories)
            logger.info(f"Processing complete: {success_count}/{total_stories} stories succeeded")

            return success_count == total_stories

        except Exception as e:
            logger.error(f"Epic driver execution failed: {e}")
            return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='BMAD Epic Automation - Process epic markdown files through SM-Dev-QA cycle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python epic_driver.py docs/epics/my-epic.md
  python epic_driver.py docs/epics/my-epic.md --max-iterations 5
  python epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
        """
    )

    # Positional argument
    parser.add_argument(
        'epic_path',
        type=str,
        help='Path to epic markdown file (required)'
    )

    # Optional arguments
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        metavar='N',
        help='Maximum retry attempts for failed stories (default: 3, must be positive)'
    )

    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Enable automatic retry of failed stories'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging output'
    )

    parser.add_argument(
        '--concurrent',
        action='store_true',
        help='Process stories in parallel (experimental feature)'
    )

    parser.add_argument(
        '--no-claude',
        action='store_true',
        help='Disable Claude Code CLI integration (use simulation mode)'
    )

    args = parser.parse_args()

    # Validate max_iterations
    if args.max_iterations <= 0:
        parser.error('--max-iterations must be a positive integer')

    return args


async def main():
    """Main entry point."""
    args = parse_arguments()

    # Configure logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Check if epic file exists
    epic_path = Path(args.epic_path)
    if not epic_path.exists():
        logger.error(f"Epic file not found: {epic_path}")
        sys.exit(1)

    # Create driver with CLI options
    driver = EpicDriver(
        epic_path=str(epic_path),
        max_iterations=args.max_iterations,
        retry_failed=args.retry_failed,
        verbose=args.verbose,
        concurrent=args.concurrent,
        use_claude=not args.no_claude
    )

    success = await driver.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

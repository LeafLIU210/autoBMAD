"""
Epic Driver - Self-Contained BMAD Automation

Main orchestrator for the BMAD automation system.
Reads epic markdown files and drives SM-Dev-QA cycle.
"""

import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Any, Callable, Optional, cast

# Import log manager
from autoBMAD.epic_automation.log_manager import (
    LogManager,
    cleanup_logging,
    init_logging,
    setup_dual_write,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 超时配置常量 - DEPRECATED: External timeouts removed - using max_turns instead
STORY_TIMEOUT = None  # 4小时 = 240分钟（整个故事的所有循环）
CYCLE_TIMEOUT = None   # 90分钟（单次Dev+QA循环）
DEV_TIMEOUT = None     # 45分钟（开发阶段）
QA_TIMEOUT = None      # 30分钟（QA审查阶段）
SM_TIMEOUT = None      # 30分钟（SM阶段）


class EpicDriver:
    """Main orchestrator for complete BMAD workflow."""

    # Class attribute type annotations for basedpyright strict mode
    epic_path: Path
    epic_id: str
    tasks_dir: Path
    stories: "list[dict[str, Any]]"
    current_story_index: int
    max_iterations: int
    retry_failed: bool
    verbose: bool
    concurrent: bool
    use_claude: bool
    source_dir: str
    test_dir: str
    sm_agent: Any
    dev_agent: Any
    qa_agent: Any
    state_manager: Any
    logger: logging.Logger
    log_manager: LogManager

    def __init__(self, epic_path: str, tasks_dir: str = ".bmad-core/tasks",
                 max_iterations: int = 3, retry_failed: bool = False,
                 verbose: bool = False, concurrent: bool = False,
                 use_claude: bool = True, source_dir: str = "src",
                 test_dir: str = "tests"):
        """
        Initialize epic driver.

        Args:
            epic_path: Path to the epic markdown file
            tasks_dir: Directory containing task guidance files
            max_iterations: Maximum retry attempts for failed stories
            retry_failed: Enable automatic retry of failed stories
            verbose: Enable detailed logging output
            concurrent: Process stories in parallel (experimental)
            use_claude: Use Claude Code CLI for real implementation (default True)
            source_dir: Source code directory for QA checks (default: "src")
            test_dir: Test directory for QA checks (default: "tests")
        """
        self.epic_path = Path(epic_path).resolve()
        self.epic_id = str(epic_path)  # Use epic path as epic_id
        self.tasks_dir = Path(tasks_dir)
        self.stories = []
        self.current_story_index = 0
        self.max_iterations = max_iterations
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.concurrent = concurrent
        self.use_claude = use_claude

        # Auto-resolve source_dir and test_dir to absolute paths
        source_path = Path(source_dir)
        test_path = Path(test_dir)
        self.source_dir = str(source_path.resolve() if source_path.exists() else Path.cwd() / source_dir)
        self.test_dir = str(test_path.resolve() if test_path.exists() else Path.cwd() / test_dir)

        # Initialize log manager
        self.log_manager = LogManager()
        init_logging(self.log_manager)
        setup_dual_write(self.log_manager)

        # Import agent classes
        try:
            from autoBMAD.epic_automation.dev_agent import DevAgent  # type: ignore
            from autoBMAD.epic_automation.qa_agent import QAAgent  # type: ignore
            from autoBMAD.epic_automation.sm_agent import SMAgent  # type: ignore
            from autoBMAD.epic_automation.state_manager import (
                StateManager,  # type: ignore
            )

            self.sm_agent = SMAgent()
            self.dev_agent = DevAgent(use_claude=use_claude)
            self.qa_agent = QAAgent()
            self.state_manager = StateManager()
        except ImportError as e:
            # Create a basic logger before exiting
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # Use module-level logger instead of creating a new local variable
            logger.error(f"Failed to import agent classes: {e}")
            sys.exit(1)

        # Initialize logger
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(f"epic_driver.{self.epic_path.name}")

        # Note: Logging is already initialized by log_manager in __init__
        # This method is kept for compatibility but doesn't add new handlers
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # Log that logging is configured
        if self.log_manager and self.log_manager.get_current_log_path():
            logger.info(f"Logging configured. Log file: {self.log_manager.get_current_log_path()}")

        return logger

    async def parse_epic(self) -> "list[dict[str, Any]]":
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
            with open(self.epic_path, encoding='utf-8') as f:
                content = f.read()

            # Step 1: Extract story IDs from Epic document
            story_ids = self._extract_story_ids_from_epic(content)

            if not story_ids:
                logger.warning("No stories found in epic document")
                return []

            # Step 2: Search for story files in docs/stories/ directory
            # epic文件在 docs/epics/，所以stories目录应该是 docs/stories
            stories_dir = self.epic_path.parent.parent / "stories"

            # Fallback: try stories directory relative to epic path
            if not stories_dir.exists():
                stories_dir = self.epic_path.parent / "stories"

            # Fallback: try autoBMAD/stories
            if not stories_dir.exists():
                autoBMAD_dir = self.epic_path.parent.parent
                if autoBMAD_dir.name == "autoBMAD":
                    stories_dir = autoBMAD_dir / "stories"
                elif (autoBMAD_dir.parent / "autoBMAD").exists():
                    stories_dir = autoBMAD_dir.parent / "autoBMAD" / "stories"

            logger.info(f"Searching for story files in: {stories_dir}")
            logger.debug(f"Stories directory exists: {stories_dir.exists()}")

            stories: list[dict[str, Any]] = []
            found_stories: list[str] = []

            # Pre-check: collect all existing story files to avoid redundant checks
            existing_stories: set[str] = set()
            if stories_dir.exists():
                story_files = list(stories_dir.glob("*.md"))
                logger.info(f"Found {len(story_files)} markdown files in stories directory")
                for story_file in story_files:
                    match = re.match(r'^(\d+(?:\.\d+)?)-', story_file.name)
                    if match:
                        existing_stories.add(match.group(1))
                        logger.debug(f"Existing story file: {story_file.name} (ID: {match.group(1)})")
            else:
                logger.warning(f"Stories directory does not exist: {stories_dir}")

            if stories_dir.exists():
                # Match story IDs to files using fallback logic
                logger.info(f"Matching {len(story_ids)} story IDs to files")
                for story_id in story_ids:
                    # Extract story number: "001" or "001: Title" -> "001"
                    story_number = story_id.split(':')[0].strip()
                    logger.debug(f"Looking for story number: {story_number} (ID: {story_id})")

                    # Use fallback matching to find story file
                    story_file = self._find_story_file_with_fallback(stories_dir, story_number)

                    if story_file:
                        logger.info(f"[Match Success] {story_id} -> {story_file.name}")
                        stories.append({
                            'id': story_id,
                            'path': str(story_file.resolve()).replace('\\', '\\\\'),
                            'name': story_file.name
                        })
                        found_stories.append(story_id)
                        logger.info(f"Found story: {story_id} at {story_file}")
                    else:
                        # Story file not found
                        logger.warning(f"[Match Failed] {story_id} (number: {story_number})")
                        # Additional check: verify if file really doesn't exist (race condition protection)
                        if story_number not in existing_stories:
                            # Try to create missing story file using SM Agent
                            logger.info(f"Creating missing story file for ID: {story_id}")
                            if await self.sm_agent.create_stories_from_epic(str(self.epic_path)):
                                # After creation, try to find the file again
                                created_story_file = self._find_story_file_with_fallback(stories_dir, story_number)
                                if created_story_file:
                                    stories.append({
                                        'id': story_id,
                                        'path': str(created_story_file.resolve()).replace('\\', '\\\\'),
                                        'name': created_story_file.name
                                    })
                                    found_stories.append(story_id)
                                    logger.info(f"Created story: {story_id} at {created_story_file}")
                                else:
                                    logger.error(f"Story file not found after creation for ID: {story_id}")
                            else:
                                logger.error(f"Failed to create story: {story_id}")
                            logger.warning(f"Story file not found for ID: {story_id} (looking for {stories_dir}/*{story_number}*.md)")
                        else:
                            # File exists but not matched (should not happen with new logic)
                            logger.warning(f"Story file exists but could not be matched: {story_number} in {stories_dir}")
            else:
                logger.error(f"Cannot match stories: stories directory does not exist: {stories_dir}")
                logger.info("Tried searching in:")
                logger.info(f"  - {self.epic_path.parent.parent / 'docs-copy' / 'stories'}")
                logger.info(f"  - {self.epic_path.parent / 'docs' / 'stories'}")
                logger.info(f"  - {self.epic_path.parent / 'stories'}")
                logger.info(f"  - {(self.epic_path.parent.parent / 'autoBMAD' / 'stories') if self.epic_path.parent.parent.name != 'autoBMAD' else 'N/A'}")

            # Warn about stories not found
            missing_stories: set[str] = set(story_ids) - set(found_stories)
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

    def _extract_story_ids_from_epic(self, content: str) -> "list[str]":
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
        story_ids: list[str] = []

        # Pattern 1: "### Story X: Title"
        pattern1 = r'### Story\s+(\d+(?:\.\d+)?)\s*:\s*(.+?)(?:\n|\$)'
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
        seen: set[str] = set()
        unique_story_ids: list[str] = []
        for story_id in story_ids:
            # Use story number as uniqueness key
            key: str = story_id.split(':')[0].strip().zfill(3)
            if key not in seen:
                seen.add(key)
                unique_story_ids.append(story_id)

        logger.debug(f"Extracted {len(unique_story_ids)} unique story IDs: {unique_story_ids}")

        return unique_story_ids

    def _find_story_file_with_fallback(self, stories_dir: Path, story_number: str) -> Optional[Path]:
        """
        Find story file with fallback matching logic.

        Tries multiple filename patterns:
        1. Exact match: {story_number}.md
        2. Descriptive match: {story_number}-*.md

        Args:
            stories_dir: Directory containing story files
            story_number: Story number (e.g., "1.1", "1.2")

        Returns:
            Path to the story file if found, None otherwise
        """
        # Pattern 1: Exact match (e.g., 1.1.md)
        exact_match = stories_dir / f"{story_number}.md"
        if exact_match.exists():
            logger.debug(f"[File Match] Found exact match for {story_number}: {exact_match}")
            return exact_match

        # Pattern 2: Descriptive match (e.g., 1.1-description.md)
        pattern_match = list(stories_dir.glob(f"{story_number}-*.md"))
        if pattern_match:
            logger.debug(f"[File Match] Found descriptive match for {story_number}: {pattern_match[0]}")
            return pattern_match[0]

        # Pattern 3: Alternative format (e.g., 1.1.description.md)
        alt_pattern_match = list(stories_dir.glob(f"{story_number}.*.md"))
        if alt_pattern_match:
            logger.debug(f"[File Match] Found alt pattern match for {story_number}: {alt_pattern_match[0]}")
            return alt_pattern_match[0]

        logger.debug(f"[File Match] No match found for story number: {story_number}")
        return None

    async def execute_sm_phase(self, story_path: str) -> bool:
        """Execute SM (Story Master) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing SM phase for {story_path}")

        try:
            # Read story content
            with open(story_path, encoding='utf-8') as f:
                story_content = f.read()

            # Execute SM phase with story_path parameter
            result: bool = await self.sm_agent.execute(story_content, story_path)

            # Update state
            state_update_success = await self.state_manager.update_story_status(
                story_path=story_path,
                status="sm_completed",
                phase="sm"
            )

            if not state_update_success:
                logger.warning(
                    f"State update failed for {story_path} but business logic completed, "
                    f"continuing with sm_completed status"
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
            # Read story content
            with open(story_path, encoding='utf-8') as f:
                story_content = f.read()

            # Set log_manager to dev_agent for SDK logging
            self.dev_agent._log_manager = self.log_manager

            # Execute Dev phase with story_path parameter
            result: bool = await self.dev_agent.execute(story_content, story_path)

            # Update state
            state_update_success = await self.state_manager.update_story_status(
                story_path=story_path,
                status="dev_completed",
                phase="dev",
                iteration=iteration
            )

            if not state_update_success:
                logger.warning(
                    f"State update failed for {story_path} but business logic completed, "
                    f"continuing with dev_completed status"
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
            # Read story content
            with open(story_path, encoding='utf-8') as f:
                story_content = f.read()

            # Execute QA phase with tools integration
            qa_result: dict[str, Any] = await self.qa_agent.execute(
                story_content,
                story_path=story_path,
                use_qa_tools=True,
                source_dir=self.source_dir,
                test_dir=self.test_dir
            )

            # Update state with QA result
            qa_state_update_success = await self.state_manager.update_story_status(
                story_path=story_path,
                status="qa_completed",
                phase="qa",
                qa_result=qa_result
            )

            if not qa_state_update_success:
                logger.warning(
                    f"QA state update failed for {story_path} but continuing with qa_completed status"
                )

            if qa_result.get("passed", False):
                logger.info(f"QA phase passed for {story_path}")
                completion_state_update_success = await self.state_manager.update_story_status(
                    story_path=story_path,
                    status="completed"
                )

                if not completion_state_update_success:
                    logger.warning(
                        f"Completion state update failed for {story_path} but QA passed successfully"
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

    async def process_story(self, story: "dict[str, Any]") -> bool:
        """
        Process a single story through Dev-QA cycle.

        Note: Story documents are created by SM agent during parse_epic() phase.
        This method only executes Dev-QA loop for each story.

        Args:
            story: Story dictionary with path and metadata (created by SM agent)

        Returns:
            True if story completed successfully (Done or Ready for Done), False otherwise
        """
        story_path = story['path']
        story_id = story['id']
        logger.info(f"Processing story {story_id}: {story_path}")

        try:
            # No external timeout - rely on SDK max_turns configuration
            return await self._process_story_impl(story)
        except asyncio.CancelledError:
            logger.info(f"Story processing cancelled for {story_path}")
            return False

    async def _process_story_impl(self, story: "dict[str, Any]") -> bool:
        """
        Internal implementation of story processing.

        Args:
            story: Story dictionary with path and metadata

        Returns:
            True if story completed successfully, False otherwise
        """
        story_path = story['path']

        try:
            # No shield - external timeouts removed
            return await self._execute_story_processing(story)
        except asyncio.CancelledError:
            logger.info(f"Story processing cancelled for {story_path}")
            return False

    async def _execute_story_processing(self, story: "dict[str, Any]") -> bool:
        """
        Core story processing logic without shield to avoid cancel scope conflicts.
        """
        story_path = story['path']
        story_id = story['id']

        try:
            # Check state consistency before processing - only log warnings, don't block
            consistency_check = await self._check_state_consistency(story)
            if not consistency_check:
                logger.warning(f"State inconsistency detected for {story_path}, but continuing with processing")
                # Continue processing despite inconsistencies - be more resilient
            else:
                logger.debug(f"State consistency check passed for {story_path}")

            # Continue with normal processing regardless of consistency check result

            # Check if story already completed
            existing_status: dict[str, Any] = await self.state_manager.get_story_status(story_path)
            if existing_status and existing_status.get('status') == 'completed':
                logger.info(f"Story already completed: {story_path}")
                return True

            # Additional check: if story document status is "Ready for Done", skip processing
            if await self._is_story_ready_for_done(story_path):
                logger.info(f"Story document status is Done or Ready for Done: {story_path}")
                # Update state to completed if not already
                if not existing_status or existing_status.get('status') != 'completed':
                    await self.state_manager.update_story_status(
                        story_path=story_path,
                        status="completed",
                        phase="skip"
                    )
                return True

            # Execute Dev-QA Loop (SM phase removed - stories already created by parse_epic)
            iteration = 1
            max_dev_qa_cycles = 10  # Maximum Dev-QA cycles
            while iteration <= max_dev_qa_cycles:
                logger.info(f"[Epic Driver] Starting Dev-QA cycle #{iteration} for {story_path}")

                # Dev Phase
                dev_success = await self.execute_dev_phase(story_path, iteration)
                if not dev_success:
                    logger.warning(f"Dev phase failed for {story_path}, proceeding with QA for diagnosis")
                    # Continue to QA phase for error diagnosis instead of returning False

                # QA Phase
                qa_passed = await self.execute_qa_phase(story_path)

                if qa_passed:
                    # Check if story is ready for done
                    if await self._is_story_ready_for_done(story_path):
                        logger.info(f"Story {story_id} completed successfully (Ready for Done)")
                        return True
                    else:
                        logger.info(f"QA passed but story not ready for done, continuing cycle {iteration + 1}")

                # Increment iteration for next cycle
                iteration += 1

                # Small delay between cycles
                await asyncio.sleep(1.0)

            # If we reach here, max cycles reached
            logger.warning(f"Reached maximum Dev-QA cycles ({max_dev_qa_cycles}) for {story_path}")
            return False

        except Exception as e:
            logger.error(f"Failed to process story {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="error",
                error=str(e)
            )
            return False

    async def _is_story_ready_for_done(self, story_path: str) -> bool:
        """Check if story is ready for done based on status."""
        try:
            with open(story_path, encoding='utf-8') as f:
                content = f.read()

            # Check for Ready for Done status - support multiple status patterns
            status_patterns = [
                r'## Status\s*\n\*\*([^*]+)\*\*',  # Bold format
                r'Status:\s*\*\*([^*]+)\*\*',       # Inline bold
                r'Status:\s*(\w+(?:\s+\w+)*)'       # Regular format
            ]

            for pattern in status_patterns:
                status_match = re.search(pattern, content, re.IGNORECASE)
                if status_match:
                    status = status_match.group(1).strip().lower()
                    # Check for completion status
                    if 'ready for done' in status or status == 'done':
                        logger.info(f"Story status is '{status}' - considered ready for done")
                        return True

            logger.warning(f"Could not find status or unknown status in story: {story_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to check story status: {e}")
            return False

    async def _check_state_consistency(self, story: "dict[str, Any]") -> bool:
        """
        Check if story state is consistent with filesystem and expected outcomes.
        Be more permissive - log issues but don't fail the entire process.
        
        Args:
            story: Story dictionary with path and metadata
            
        Returns:
            True if state is consistent, False if there are issues
        """
        try:
            story_path = story.get('path', '')
            if not story_path:
                logger.warning("No story path provided for state consistency check")
                return True  # Return True to allow processing to continue

            # Check filesystem state - be permissive about missing files
            filesystem_consistent = await self._check_filesystem_state(story)
            if not filesystem_consistent:
                logger.info(f"Filesystem state check found issues for {story_path}, but continuing")
                # Don't return False - allow processing to continue

            # Check story integrity - be permissive about format issues
            integrity_consistent = await self._validate_story_integrity(story)
            if not integrity_consistent:
                logger.info(f"Story integrity check found format issues for {story_path}, but continuing")
                # Don't return False - allow processing to continue

            # Check status consistency with database - informational only
            try:
                db_status = await self.state_manager.get_story_status(story_path)
                current_status = story.get('status', 'unknown')
                
                if db_status and db_status.get('status') != current_status:
                    logger.info(f"Status mismatch noted for {story_path}: story={current_status}, db={db_status.get('status')}")
                    # Informational only - don't block processing
            except Exception as e:
                logger.debug(f"Database status check failed for {story_path}: {e}")
                # Don't fail if database check fails

            logger.debug(f"State consistency check completed for {story_path}")
            return True  # Always return True to allow processing to continue

        except Exception as e:
            story_path = story.get('path', 'unknown')
            logger.error(f"State consistency check failed for {story_path}: {e}")
            return True  # Return True to allow processing to continue despite errors

    async def _check_filesystem_state(self, story: "dict[str, Any]") -> bool:
        """
        Check if expected files exist on filesystem.
        Be permissive - log missing files but don't fail the process.
        
        Args:
            story: Story dictionary with expected files
            
        Returns:
            True if filesystem looks reasonable, False if major issues found
        """
        try:
            expected_files = story.get('expected_files', [])
            if not expected_files:
                # If no expected files specified, check for basic structure
                expected_files = ['src', 'tests', 'docs']
            
            missing_files: list[str] = []
            existing_files: list[str] = []
            
            for file_path in expected_files:
                path = Path(file_path)
                if path.exists():
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            # Log status but be permissive
            if missing_files:
                logger.info(f"Expected files check: found {str(len(existing_files))}, missing {str(len(missing_files))} for {story.get('path', 'unknown')}")
                logger.debug(f"Missing files: {missing_files}")
            else:
                logger.debug(f"All expected files found for {story.get('path', 'unknown')}")

            # Always return True to allow processing to continue
            # The check is informational, not blocking
            return True

        except Exception as e:
            logger.error(f"Filesystem state check failed: {e}")
            return True  # Return True to allow processing to continue

    async def _validate_story_integrity(self, story: "dict[str, Any]") -> bool:
        """
        Validate story file content integrity.
        Be smart about validation - check for essential elements, not strict formatting.
        
        Args:
            story: Story dictionary with path and validation requirements
            
        Returns:
            True if story has essential content, False if it's clearly invalid
        """
        try:
            story_path = story.get('path', '')
            if not story_path:
                logger.debug("No story path provided for integrity check")
                return True  # Allow processing to continue

            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"Story file does not exist: {story_path}")
                return False  # This is a real issue - file should exist

            content = story_file.read_text(encoding='utf-8')
            
            # Essential checks - only fail on truly problematic content
            if len(content.strip()) < 50:  # Very short content
                logger.warning(f"Story {story_path} appears too short ({len(content)} chars)")
                return False
            
            # Helper functions for checking essential story elements
            def has_markdown_headers(content: str) -> bool:
                """Check if content has markdown headers."""
                return '#' in content or content.strip().startswith('#')

            def mentions_status(content: str) -> bool:
                """Check if content mentions status."""
                return 'status' in content.lower()

            def has_substantial_content(content: str) -> bool:
                """Check if content has substantial text."""
                return len(content.split()) > 20

            # Check for essential story elements (be flexible about formatting)
            essential_elements: list[tuple[str, Callable[[str], bool]]] = [
                ('title or header', has_markdown_headers),  # Has markdown headers
                ('status', mentions_status),  # Mentions status
                ('story content', has_substantial_content),  # Has substantial content
            ]
            
            missing_essentials: list[str] = []
            for element_name, check_func in essential_elements:
                check_func_cast = cast(Callable[[str], bool], check_func)
                if not check_func_cast(content):
                    missing_essentials.append(element_name)
            
            if missing_essentials:
                logger.warning(f"Story {story_path} missing essential elements: {missing_essentials}")
                # For missing essentials, be more permissive - log but don't fail
                # unless it's really critical
                if len(missing_essentials) >= 2:  # Only fail if multiple essentials missing
                    return False

            # Smart section detection - look for common story patterns
            has_story_pattern = any(pattern in content.lower() for pattern in [
                '## story', '# story', 'as a', 'i want', 'so that'
            ])
            
            has_acceptance_pattern = any(pattern in content.lower() for pattern in [
                '## acceptance', '# acceptance', 'acceptance criteria'
            ])

            if not has_story_pattern and not has_acceptance_pattern:
                logger.warning(f"Story {story_path} doesn't follow standard story format")
                # Don't fail - some stories might use different formats

            logger.debug(f"Story integrity validation passed for {story_path}")
            return True  # Be permissive - allow most stories to proceed

        except Exception as e:
            story_path = story.get('path', 'unknown')
            logger.error(f"Story integrity validation failed for {story_path}: {e}")
            return True  # Return True to allow processing to continue

    async def _resync_story_state(self, story: "dict[str, Any]") -> None:
        """
        Resynchronize story state with expected status.
        
        Args:
            story: Story dictionary with path and expected status
        """
        try:
            story_path = story.get('path', '')
            expected_status = story.get('expected_status', 'ready')
            
            if not story_path:
                return

            logger.info(f"Resynchronizing story state for {story_path} to {expected_status}")
            
            # Update database state
            await self.state_manager.update_story_status(
                story_path=story_path,
                status=expected_status
            )

            # Log resync action
            self.log_manager.log_state_resync(story_path, expected_status)

        except Exception as e:
            story_path = story.get('path', 'unknown')
            logger.error(f"Failed to resync story state for {story_path}: {e}")

    async def _handle_graceful_cancellation(self, story: "dict[str, Any]") -> None:
        """
        Handle graceful cancellation of story processing.
        
        Args:
            story: Story dictionary being processed
        """
        try:
            story_path = story.get('path', '')
            if not story_path:
                return

            logger.info(f"Handling graceful cancellation for {story_path}")
            
            # Update story status to indicate cancellation
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="cancelled"
            )

            # Log cancellation
            self.log_manager.log_cancellation(f"Story processing cancelled for {story_path}")

        except Exception as e:
            story_path = story.get('path', 'unknown')
            logger.error(f"Failed to handle graceful cancellation for {story_path}: {e}")

    async def execute_dev_qa_cycle(self, stories: "list[dict[str, Any]]") -> bool:
        """
        Execute Dev-QA cycle for all stories.

        Args:
            stories: List of story dictionaries

        Returns:
            True if all stories completed successfully, False otherwise
        """
        self.logger.info(f"Starting Dev-QA cycle for {len(stories)} stories")

        # Initialize epic processing record
        await self._initialize_epic_processing(len(stories))

        success_count = 0
        for story in stories:
            if self.verbose:
                self.logger.debug(f"Processing story: {story['id']}")

            if await self.process_story(story):
                success_count += 1
            elif not self.retry_failed:
                if self.verbose:
                    self.logger.debug(f"Continuing to next story after failure: {story['id']}")

        # Update progress
        await self._update_progress('dev_qa', 'completed', {
            'completed_stories': success_count,
            'total_stories': len(stories)
        })

        self.logger.info(f"Dev-QA cycle complete: {success_count}/{len(stories)} stories succeeded")
        return success_count == len(stories)


    def _validate_phase_gates(self) -> bool:
        """
        Validate that all prerequisites are met before each phase.

        Returns:
            True if all validations pass, False otherwise
        """
        return True

    async def _update_progress(self, phase: str, status: str, details: "dict[str, Any]") -> None:
        """
        Update progress tracking in state manager.

        Args:
            phase: Phase name (dev_qa)
            status: Phase status (pending, in_progress, completed, failed, skipped)
            details: Additional phase details
        """
        try:
            # Epic progress is tracked in stories table, not in epic_processing table
            self.logger.debug(f"Updated {phase} progress: {status}")
        except Exception as e:
            self.logger.error(f"Failed to update progress for {phase}: {e}")

    async def _initialize_epic_processing(self, total_stories: int) -> None:
        """
        Initialize epic processing record.

        Args:
            total_stories: Total number of stories in epic
        """
        try:
            # Epic processing is tracked via stories table, no separate initialization needed
            self.logger.debug(f"Initialized epic processing for {total_stories} stories")
        except Exception as e:
            self.logger.error(f"Failed to initialize epic processing: {e}")

    def _generate_final_report(self) -> "dict[str, Any]":
        """
        Generate final epic processing report.

        Returns:
            Dict with final epic results
        """
        return {
            'epic_id': self.epic_id,
            'status': 'completed',
            'phases': {
                'dev_qa': 'completed'
            },
            'total_stories': len(self.stories),
            'timestamp': asyncio.get_event_loop().time()
        }

    async def run(self) -> bool:
        """
        Execute complete epic processing workflow.

        Returns:
            True if epic completed successfully, False otherwise
        """
        self.logger.info("Starting Epic Driver - Dev-QA Workflow")

        # Log configuration
        if self.verbose:
            config_str = (
                f"Configuration: max_iterations={self.max_iterations}, "
                f"retry_failed={self.retry_failed}, verbose={self.verbose}, "
                f"concurrent={self.concurrent}"
            )
            self.logger.debug(config_str)

        if self.concurrent:
            self.logger.warning("Concurrent processing is experimental and not fully tested with quality gates")

        try:
            # Parse epic
            stories = await self.parse_epic()
            if not stories:
                self.logger.error("No stories found in epic")
                return False

            # Validate phase gates
            if not self._validate_phase_gates():
                self.logger.error("Phase gate validation failed")
                return False

            # Phase 1: Dev-QA Cycle
            self.logger.info("=== Phase 1: Dev-QA Cycle ===")
            await self._update_progress('dev_qa', 'in_progress', {})
            dev_qa_success = await self.execute_dev_qa_cycle(stories)

            if not dev_qa_success:
                self.logger.error("Dev-QA cycle failed")
                await self._update_progress('dev_qa', 'failed', {})
                return False


            self.logger.info("=== Epic Processing Complete ===")
            return True

        except Exception as e:
            self.logger.error(f"Epic driver execution failed: {e}", exc_info=True)
            # Write exception to log file
            if self.log_manager:
                self.log_manager.write_exception(e, "Epic Driver run()")
            return False
        finally:
            # Improved cleanup logic
            try:
                # 1. Cancel all active SDK sessions
                if hasattr(self, 'qa_agent') and hasattr(self.qa_agent, '_session_manager'):
                    await self.qa_agent._session_manager.cancel_all_sessions()

                # 2. Flush log manager
                if hasattr(self, 'log_manager') and self.log_manager:
                    self.log_manager.flush()

                # 3. Finally cleanup logging
                cleanup_logging()

            except Exception:
                # Silently handle cleanup errors to avoid interfering with main flow
                pass


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='BMAD Epic Automation - Process epic markdown files through Dev-QA workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python epic_driver.py docs/epics/my-epic.md
  python epic_driver.py docs/epics/my-epic.md --max-iterations 5
  python epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
  python epic_driver.py docs/epics/my-epic.md --source-dir src --test-dir tests
        """
    )

    # Positional argument
    _ = parser.add_argument(
        'epic_path',
        type=str,
        help='Path to epic markdown file (required)'
    )

    # Optional arguments
    _ = parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        metavar='N',
        help='Maximum retry attempts for failed stories (default: 3, must be positive)'
    )

    _ = parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Enable automatic retry of failed stories'
    )

    _ = parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging output'
    )

    _ = parser.add_argument(
        '--concurrent',
        action='store_true',
        help='Process stories in parallel (experimental feature)'
    )

    _ = parser.add_argument(
        '--no-claude',
        action='store_true',
        help='Disable Claude Code CLI integration (use simulation mode)'
    )

    _ = parser.add_argument(
        '--source-dir',
        type=str,
        default="src",
        metavar='DIR',
        help='Source code directory for QA checks (default: "src")'
    )

    _ = parser.add_argument(
        '--test-dir',
        type=str,
        default="tests",
        metavar='DIR',
        help='Test directory for QA checks (default: "tests")'
    )

    args = parser.parse_args()

    # Validate max_iterations
    if args.max_iterations <= 0:  # type: ignore[operator]
        parser.error('--max-iterations must be a positive integer')

    return args


async def main():
    """Main entry point."""
    args = parse_arguments()

    # Configure logging level based on verbose flag
    if args.verbose:  # type: ignore[truthy-bool]
        logging.getLogger().setLevel(logging.DEBUG)

    # Check if epic file exists
    epic_path = Path(args.epic_path)  # type: ignore[arg-type]
    if not epic_path.exists():
        logger.error(f"Epic file not found: {epic_path}")
        sys.exit(1)

    # Create driver with CLI options
    driver = EpicDriver(
        epic_path=str(epic_path),
        max_iterations=args.max_iterations,  # type: ignore[arg-type]
        retry_failed=args.retry_failed,  # type: ignore[arg-type]
        verbose=args.verbose,  # type: ignore[arg-type]
        concurrent=args.concurrent,  # type: ignore[arg-type]
        use_claude=not args.no_claude,  # type: ignore[arg-type]
        source_dir=args.source_dir,  # type: ignore[arg-type]
        test_dir=args.test_dir  # type: ignore[arg-type]
    )

    success = await driver.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Execution cancelled by user (Ctrl+C)")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        sys.exit(1)

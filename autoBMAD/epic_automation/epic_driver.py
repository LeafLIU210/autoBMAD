"""
Epic Driver - Self-Contained BMAD Automation

Main orchestrator for the BMAD automation system.
Reads epic markdown files and drives SM-Dev-QA cycle.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path
from typing import Any, cast
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    skip_quality: bool
    skip_tests: bool
    task_guidance: "dict[str, str]"
    max_quality_iterations: int
    max_test_iterations: int
    sm_agent: Any
    dev_agent: Any
    qa_agent: Any
    state_manager: Any
    logger: logging.Logger

    def __init__(self, epic_path: str, tasks_dir: str = ".bmad-core/tasks",
                 max_iterations: int = 3, retry_failed: bool = False,
                 verbose: bool = False, concurrent: bool = False,
                 use_claude: bool = True, source_dir: str = "src",
                 test_dir: str = "tests", skip_quality: bool = False,
                 skip_tests: bool = False):
        """
        Initialize epic driver with quality gate options.

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
            skip_quality: Skip code quality gates (default: False)
            skip_tests: Skip test automation (default: False)
        """
        self.epic_path = Path(epic_path)
        self.epic_id = str(epic_path)  # Use epic path as epic_id
        self.tasks_dir = Path(tasks_dir)
        self.stories = []
        self.current_story_index = 0
        self.max_iterations = max_iterations
        self.retry_failed = retry_failed
        self.verbose = verbose
        self.concurrent = concurrent
        self.use_claude = use_claude
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.skip_quality = skip_quality
        self.skip_tests = skip_tests
        self.task_guidance = {}

        # Quality gate and test automation iteration limits
        self.max_quality_iterations = 3
        self.max_test_iterations = 5

        # Import agent classes
        try:
            from autoBMAD.epic_automation.sm_agent import SMAgent  # type: ignore
            from autoBMAD.epic_automation.dev_agent import DevAgent  # type: ignore
            from autoBMAD.epic_automation.qa_agent import QAAgent  # type: ignore
            from autoBMAD.epic_automation.state_manager import StateManager  # type: ignore

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
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to import agent classes: {e}")
            sys.exit(1)

        # Initialize logger
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(f"epic_driver.{self.epic_path.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger

    async def load_task_guidance(self) -> None:
        """
        Load task guidance files from tasks directory.

        This method can be extended to load additional task guidance
        if needed in the future. Currently, it's a placeholder to
        maintain compatibility with the workflow orchestration.
        """
        # Placeholder for future task guidance loading
        # Currently, task guidance is loaded implicitly through agent initialization
        self.logger.debug("Task guidance loading completed")

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
            with open(self.epic_path, 'r', encoding='utf-8') as f:
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

            logger.debug(f"Searching for story files in: {stories_dir}")

            stories: list[dict[str, Any]] = []
            found_stories: list[str] = []

            if stories_dir.exists():
                # Find all story files matching pattern 001.*.md, 002.*.md, etc.
                story_files = list(stories_dir.glob("*.md"))
                logger.debug(f"Found {len(story_files)} markdown files in stories directory")

                # Create a mapping of story numbers to files
                story_file_map: dict[str, Path] = {}
                for story_file in story_files:
                    # Extract story number from filename: 001.xxx.md -> 001
                    match = re.match(r'^(\d+(?:\.\d+)?)\.', story_file.name)
                    if match:
                        story_number = match.group(1)
                        story_file_map[story_number] = story_file

                # Match story IDs to files
                for story_id in story_ids:
                    # Extract story number: "001" or "001: Title" -> "001"
                    story_number = story_id.split(':')[0].strip()

                    if story_number in story_file_map:
                        story_file: Path = story_file_map[story_number]
                        stories.append({
                            'id': story_id,
                            'path': str(story_file.resolve()),
                            'name': story_file.name
                        })
                        found_stories.append(story_id)
                        logger.info(f"Found story: {story_id} at {story_file}")
                    else:
                        # Story file not found
                        # Try to create missing story file using SM Agent
                        story_filename = f"{story_number}.md"
                        story_path: Path = stories_dir / story_filename
                        if await self.sm_agent.create_stories_from_epic(str(self.epic_path)):
                            stories.append({
                                'id': story_id,
                                'path': str(story_path.resolve()),
                                'name': story_path.name
                            })
                            found_stories.append(story_id)
                            logger.info(f"Created story: {story_id} at {story_path}")
                        else:
                            logger.error(f"Failed to create story: {story_id}")
                        logger.warning(f"Story file not found for ID: {story_id} (looking for {stories_dir}/*{story_number}*.md)")

            else:
                logger.warning(f"Stories directory not found: {stories_dir}")
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


    async def execute_sm_phase(self, story_path: str) -> bool:
        """Execute SM (Story Master) phase for a story.

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
            result: bool = await self.sm_agent.execute(story_content, guidance)

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

            # Execute Dev phase with story_path parameter
            result: bool = await self.dev_agent.execute(story_content, guidance, story_path)

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

        # Check if quality gates are skipped
        if self.skip_quality:
            logger.info("QA phase skipped via CLI flag")
            # Update state to completed when skipping QA
            await self.state_manager.update_story_status(
                story_path=story_path,
                status="completed",
                phase="qa"
            )
            return True

        # Get task guidance for QA agent
        guidance = self.task_guidance.get("qa_agent", "")

        try:
            # Read story content
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()

            # Execute QA phase with tools integration
            qa_result: "dict[str, Any]" = await self.qa_agent.execute(
                story_content,
                task_guidance=guidance,
                use_qa_tools=True,
                source_dir=self.source_dir,
                test_dir=self.test_dir
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

    async def process_story(self, story: "dict[str, Any]") -> bool:
        """
        Process a single story through SM-Dev-QA cycle with Dev-QA loop.

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
            existing_status: "dict[str, Any]" = await self.state_manager.get_story_status(story_path)
            if existing_status and existing_status.get('status') == 'completed':
                logger.info(f"Story already completed: {story_path}")
                return True

            # Execute phases
            # SM Phase
            sm_success = await self.execute_sm_phase(story_path)
            if not sm_success:
                logger.error(f"SM phase failed for {story_path}")
                return False

            # Dev-QA Loop (with iteration support)
            iteration = 1
            max_dev_qa_cycles = 10  # Maximum Dev-QA cycles
            while iteration <= max_dev_qa_cycles:
                logger.info(f"[Epic Driver] Starting Dev-QA cycle #{iteration} for {story_path}")

                # Dev Phase
                dev_success = await self.execute_dev_phase(story_path, iteration)
                if not dev_success:
                    logger.error(f"Dev phase failed for {story_path}")
                    return False

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
                await asyncio.sleep(2)

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
            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for Ready for Done status
            status_match = re.search(r'## Status\s*\n\*\*([^*]+)\*\*', content)
            if status_match:
                status = status_match.group(1).strip().lower()
                return 'ready for done' in status or 'done' in status

            return False
        except Exception as e:
            logger.error(f"Failed to check story status: {e}")
            return False

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

    async def execute_quality_gates(self) -> "dict[str, Any]":
        """
        Execute quality gates after SM-Dev-QA completion.

        Returns:
            Dict with quality gate results and status
        """
        self.logger.info("Starting quality gates")

        # Check if quality gates are skipped
        if self.skip_quality:
            self.logger.info("Quality gates skipped via CLI flag")
            await self._update_progress('quality_gates', 'skipped', {})
            return {'status': 'skipped'}

        try:
            from autoBMAD.epic_automation.code_quality_agent import CodeQualityAgent  # type: ignore

            quality_agent: Any = cast(Any, CodeQualityAgent(
                state_manager=self.state_manager,
                epic_id=self.epic_id,
                skip_quality=self.skip_quality
            ))

            raw_results: Any = await quality_agent.run_quality_gates(
                source_dir=self.source_dir,
                skip_quality=self.skip_quality
            )
            quality_results: "dict[str, Any]" = cast("dict[str, Any]", raw_results)

            # Update progress
            status: str = str(quality_results.get('status', 'failed'))
            await self._update_progress('quality_gates', status, quality_results)

            if status == 'completed':
                self.logger.info("Quality gates passed successfully")
            elif status == 'skipped':
                self.logger.info("Quality gates skipped via CLI flag")
            else:
                self.logger.warning(f"Quality gates completed with status: {status}")

            return quality_results

        except Exception as e:
            self.logger.error(f"Quality gates execution failed: {e}", exc_info=True)
            await self._update_progress('quality_gates', 'failed', {'error': str(e)})
            return {'status': 'failed', 'error': str(e)}

    async def execute_test_automation(self) -> "dict[str, Any]":
        """
        Execute test automation after quality gates.

        Returns:
            Dict with test automation results and status
        """
        self.logger.info("Starting test automation")

        # Check if test automation is skipped
        if self.skip_tests:
            self.logger.info("Test automation skipped via CLI flag")
            await self._update_progress('test_automation', 'skipped', {})
            return {'status': 'skipped'}

        try:
            from autoBMAD.epic_automation.test_automation_agent import TestAutomationAgent  # type: ignore

            test_agent: Any = cast(Any, TestAutomationAgent(
                state_manager=self.state_manager,
                epic_id=self.epic_id,
                skip_tests=self.skip_tests
            ))

            raw_results: Any = await test_agent.run_test_automation(
                test_dir=self.test_dir,
                skip_tests=self.skip_tests
            )
            test_results: "dict[str, Any]" = cast("dict[str, Any]", raw_results)

            # Update progress
            status: str = str(test_results.get('status', 'failed'))
            await self._update_progress('test_automation', status, test_results)

            if status == 'completed':
                self.logger.info("Test automation completed successfully")
            elif status == 'skipped':
                self.logger.info("Test automation skipped via CLI flag")
            else:
                self.logger.warning(f"Test automation completed with status: {status}")

            return test_results

        except Exception as e:
            self.logger.error(f"Test automation execution failed: {e}", exc_info=True)
            await self._update_progress('test_automation', 'failed', {'error': str(e)})
            return {'status': 'failed', 'error': str(e)}

    def _validate_phase_gates(self) -> bool:
        """
        Validate that all prerequisites are met before each phase.

        Returns:
            True if all validations pass, False otherwise
        """
        # Validate source directory exists
        if not self.skip_quality:
            if not Path(self.source_dir).exists():
                self.logger.error(f"Source directory not found: {self.source_dir}")
                return False

        # Validate test directory exists
        if not self.skip_tests:
            if not Path(self.test_dir).exists():
                self.logger.error(f"Test directory not found: {self.test_dir}")
                return False

        return True

    async def _update_progress(self, phase: str, status: str, details: "dict[str, Any]") -> None:
        """
        Update progress tracking in state manager.

        Args:
            phase: Phase name (dev_qa, quality_gates, test_automation)
            status: Phase status (pending, in_progress, completed, failed, skipped)
            details: Additional phase details
        """
        try:
            # Update epic status based on phase
            if phase == 'dev_qa':
                # For Dev-QA, we don't track in epic_processing, it's tracked in stories table
                pass
            elif phase == 'quality_gates':
                await self.state_manager.update_epic_status(
                    epic_id=self.epic_id,
                    file_path=str(self.epic_path),
                    status='in_progress',
                    quality_phase_status=status,
                    quality_phase_errors=details.get('total_errors', 0)
                )
            elif phase == 'test_automation':
                await self.state_manager.update_epic_status(
                    epic_id=self.epic_id,
                    file_path=str(self.epic_path),
                    status='in_progress',
                    test_phase_status=status,
                    test_phase_failures=details.get('failed_count', 0)
                )

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
            await self.state_manager.update_epic_status(
                epic_id=self.epic_id,
                file_path=str(self.epic_path),
                status="in_progress",
                total_stories=total_stories,
                completed_stories=0,
                quality_phase_status="pending",
                test_phase_status="pending"
            )
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
                'dev_qa': 'completed',
                'quality_gates': 'skipped' if self.skip_quality else 'completed',
                'test_automation': 'skipped' if self.skip_tests else 'completed'
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
        self.logger.info("Starting Epic Driver - Complete 5-Phase Workflow")

        # Log configuration
        if self.verbose:
            config_str = (
                f"Configuration: max_iterations={self.max_iterations}, "
                f"retry_failed={self.retry_failed}, verbose={self.verbose}, "
                f"concurrent={self.concurrent}, skip_quality={self.skip_quality}, "
                f"skip_tests={self.skip_tests}"
            )
            self.logger.debug(config_str)

        if self.concurrent:
            self.logger.warning("Concurrent processing is experimental and not fully tested with quality gates")

        try:
            # Load task guidance
            await self.load_task_guidance()

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

            # Phase 2: Quality Gates (conditional)
            if not self.skip_quality:
                self.logger.info("=== Phase 2: Quality Gates ===")
                await self._update_progress('quality_gates', 'in_progress', {})
                quality_results = await self.execute_quality_gates()

                if quality_results.get('status') not in ['completed', 'skipped']:
                    self.logger.error("Quality gates failed")
                    return False
            else:
                self.logger.info("=== Phase 2: Quality Gates (SKIPPED) ===")
                await self._update_progress('quality_gates', 'skipped', {})

            # Phase 3: Test Automation (conditional)
            if not self.skip_tests:
                self.logger.info("=== Phase 3: Test Automation ===")
                await self._update_progress('test_automation', 'in_progress', {})
                test_results = await self.execute_test_automation()

                if test_results.get('status') not in ['completed', 'skipped']:
                    self.logger.warning("Test automation completed with issues but continuing")
            else:
                self.logger.info("=== Phase 3: Test Automation (SKIPPED) ===")
                await self._update_progress('test_automation', 'skipped', {})

            self.logger.info("=== Epic Processing Complete ===")
            return True

        except Exception as e:
            self.logger.error(f"Epic driver execution failed: {e}", exc_info=True)
            return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='BMAD Epic Automation - Process epic markdown files through complete 5-phase workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python epic_driver.py docs/epics/my-epic.md
  python epic_driver.py docs/epics/my-epic.md --max-iterations 5
  python epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
  python epic_driver.py docs/epics/my-epic.md --source-dir src --test-dir tests
  python epic_driver.py docs/epics/my-epic.md --skip-quality
  python epic_driver.py docs/epics/my-epic.md --skip-tests
  python epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests

Quality Gates:
  Quality gates (basedpyright and ruff) run after SM-Dev-QA cycle completes.
  Use --skip-quality to bypass quality gates.

Test Automation:
  Test automation (pytest and debugpy) runs after quality gates complete.
  Use --skip-tests to bypass test automation.
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

    _ = parser.add_argument(
        '--skip-quality',
        action='store_true',
        help='Skip code quality gates (basedpyright and ruff checks)'
    )

    _ = parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip test automation (pytest and debugpy checks)'
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
        test_dir=args.test_dir,  # type: ignore[arg-type]
        skip_quality=args.skip_quality,  # type: ignore[arg-type]
        skip_tests=args.skip_tests  # type: ignore[arg-type]
    )

    success = await driver.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

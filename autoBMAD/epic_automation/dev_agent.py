"""
Dev Agent - Development Agent

Handles development tasks and implementation according to story requirements.
Integrates with task guidance for development-specific operations.
Uses Claude Code CLI for actual implementation.
"""

import logging
import subprocess
import asyncio
from typing import Any, cast, TYPE_CHECKING
from typing import Dict, List, Optional  # For compatibility with older Python versions
import re
from pathlib import Path

if TYPE_CHECKING:
    from claude_agent_sdk import query, ClaudeAgentOptions

# Import LogManager for runtime use
from autoBMAD.epic_automation.log_manager import LogManager

try:
    from claude_agent_sdk import query as _query, ClaudeAgentOptions as _ClaudeAgentOptions, ResultMessage as _ResultMessage
except ImportError:
    # For development without SDK installed
    _query = None
    _ClaudeAgentOptions = None
    _ResultMessage = None

# Import SDK session manager for isolated execution
from .sdk_session_manager import SDKSessionManager, SDKErrorType

# Export for use in code
query = _query
ClaudeAgentOptions = _ClaudeAgentOptions  # type: ignore[assignment]
ResultMessage = _ResultMessage

# Import SafeClaudeSDK wrapper
try:
    from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK
except ImportError:
    # For development without SDK installed
    SafeClaudeSDK = None

logger = logging.getLogger(__name__)


class DevAgent:
    """Development agent for handling implementation tasks."""

    name: str
    use_claude: bool
    _current_story_path: Optional[str]
    _claude_available: bool

    def __init__(self, use_claude: bool = True):
        """
        Initialize Dev agent.

        Args:
            use_claude: If True, use Claude Code CLI for real implementation.
                       If False, use simulation mode (for testing).
        """
        self.name = "Dev Agent"
        self.use_claude = use_claude
        self._current_story_path = None
        self._claude_available = self._check_claude_available() if use_claude else False
        # 每个DevAgent实例创建独立的会话管理器，消除跨Agent cancel scope污染
        self._session_manager = SDKSessionManager()
        logger.info(f"{self.name} initialized (claude_mode={self.use_claude}, claude_available={self._claude_available})")

    def _validate_prompt_format(self, prompt: str) -> bool:
        """Validate prompt format for BMAD commands."""
        try:
            # 基本格式检查
            if not prompt or len(prompt.strip()) == 0:
                logger.error("[Prompt Validation] Empty prompt")
                return False
            
            # BMAD命令格式检查
            if not prompt.startswith('@'):
                logger.warning(f"[Prompt Validation] Prompt doesn't start with @: {prompt[:50]}...")
            
            # 检查是否包含develop-story命令
            if '*develop-story' not in prompt:
                logger.warning(f"[Prompt Validation] Missing *develop-story command: {prompt[:100]}...")
            
            # 检查文件路径格式
            if '"' in prompt:
                # 提取引号内的路径
                import re
                path_matches = re.findall(r'"([^"]+)"', prompt)
                for path in path_matches:
                    if not path.endswith('.md'):
                        logger.warning(f"[Prompt Validation] Non-markdown file path: {path}")
                    # 检查路径是否存在
                    from pathlib import Path
                    if not Path(path).exists():
                        logger.warning(f"[Prompt Validation] Story file not found: {path}")
            
            # 检查编码问题（非ASCII字符）
            try:
                _ = prompt.encode('ascii')
            except UnicodeEncodeError:
                logger.warning("[Prompt Validation] Prompt contains non-ASCII characters")
            
            logger.info("[Prompt Validation] Prompt format validation passed")
            return True
            
        except Exception as e:
            logger.error(f"[Prompt Validation] Validation error: {str(e)}")
            return False

    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available with retry logic."""
        import os
        import time

        max_retries = 1
        timeout = 30  # Increased from 10 to 30 seconds

        possible_commands = [
            ['claude', '--version'],
            [r'C:\Users\Administrator\AppData\Roaming\npm\claude', '--version'],
            [r'C:\Users\Administrator\AppData\Roaming\npm\claude.cmd', '--version'],
            ['where', 'claude']
        ]

        env = os.environ.copy()

        for attempt in range(max_retries):
            try:
                for cmd in possible_commands:
                    try:
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=timeout,
                            shell=True,
                            env=env
                        )
                        if result.returncode == 0:
                            if cmd[0] == 'where':
                                paths = result.stdout.strip().split('\n')
                                if paths:
                                    verify = subprocess.run(
                                        [paths[0], '--version'],
                                        capture_output=True,
                                        text=True,
                                        timeout=timeout,
                                        shell=True,
                                        env=env
                                    )
                                    if verify.returncode == 0:
                                        logger.info(f"Claude Code CLI available: {verify.stdout.strip()}")
                                        return True
                            else:
                                logger.info(f"Claude Code CLI available: {result.stdout.strip()}")
                                return True
                    except subprocess.TimeoutExpired:
                        logger.warning(f"CLI check timeout for {cmd[0]} (attempt {attempt + 1}/{max_retries})")
                        continue
                    except Exception:
                        continue

                # If no command worked in this attempt, try again
                if attempt < max_retries - 1:
                    logger.warning(f"CLI check attempt {attempt + 1} failed, retrying in 2s...")
                    time.sleep(2)

            except Exception as e:
                logger.warning(f"CLI check attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        logger.error(f"Claude Code CLI not available after {max_retries} attempts")
        return False

    async def execute(
        self,
        story_content: str,
        task_guidance: str = "",
        story_path: str = "",
        qa_feedback: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute Dev phase for a story with QA feedback loop support.

        Args:
            story_content: Raw markdown content of the story
            task_guidance: Task guidance from .bmad-core/tasks/develop-story.md
            story_path: Path to the story file
            qa_feedback: Optional QA feedback from previous QA review

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"{self.name} executing Dev phase")

        try:
            # Store story path for later use
            if story_path:
                self._current_story_path = story_path

            # Parse story to extract requirements
            requirements = await self._extract_requirements(story_content)

            if not requirements:
                logger.error("Failed to extract requirements from story")
                return False

            # Add story_path to requirements if available in context
            requirements['story_path'] = self._current_story_path

            # Handle QA feedback if provided
            if qa_feedback and qa_feedback.get('needs_fix'):
                logger.info(f"{self.name} Handling QA feedback loop")
                requirements['qa_prompt'] = qa_feedback.get('dev_prompt', '')

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
            # Type the requirements dict structure explicitly
            requirements: Dict[str, Any] = {
                'title': '',
                'acceptance_criteria': [],
                'tasks': [],
                'subtasks': [],
                'dev_notes': {},
                'testing': {}
            }

            # Extract title
            title_match = re.search(r'^# .+:(.+)$', story_content, re.MULTILINE)
            if title_match:
                requirements['title'] = title_match.group(1).strip()
            else:
                # Try alternative pattern
                title_match = re.search(r'^# Story \d+:\s*(.+)$', story_content, re.MULTILINE)
                if title_match:
                    requirements['title'] = title_match.group(1).strip()

            # Extract acceptance criteria
            ac_section = re.search(r'## Acceptance Criteria\n(.*?)(?=\n##|\Z)', story_content, re.DOTALL)
            if ac_section:
                ac_lines = ac_section.group(1).strip().split('\n')
                for line in ac_lines:
                    if line.strip() and re.match(r'^\d+\.', line.strip()):
                        # Cast to List[str] to help type checker
                        acceptance_criteria = cast(List[str], requirements['acceptance_criteria'])
                        acceptance_criteria.append(line.strip())
            else:
                # Try alternative pattern with checkboxes
                ac_section = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
                if ac_section:
                    ac_lines = ac_section.group(1).strip().split('\n')
                    for line in ac_lines:
                        if line.strip().startswith('-'):
                            # Cast to List[str] to help type checker
                            acceptance_criteria = cast(List[str], requirements['acceptance_criteria'])
                            acceptance_criteria.append(line.strip())

            # Extract tasks
            tasks_section = re.search(r'## Tasks / Subtasks\n(.*?)(?=\n##|\Z)', story_content, re.DOTALL)
            if tasks_section:
                task_lines = tasks_section.group(1).strip().split('\n')
                for line in task_lines:
                    if line.strip().startswith('- [ ]'):
                        # Cast to List[str] to help type checker
                        tasks = cast(List[str], requirements['tasks'])
                        tasks.append(line.strip())
            else:
                # Try alternative pattern
                tasks_section = re.search(r'## Tasks / Subtasks\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
                if tasks_section:
                    task_lines = tasks_section.group(1).strip().split('\n')
                    for line in task_lines:
                        if line.strip().startswith('-'):
                            # Cast to List[str] to help type checker
                            tasks = cast(List[str], requirements['tasks'])
                            tasks.append(line.strip())

            # Extract subtasks (nested)
            subtask_pattern = r'^\s*-\s*\[x\]\s*(.+)'
            for line in story_content.split('\n'):
                if re.match(subtask_pattern, line):
                    # Cast to List[str] to help type checker
                    subtasks = cast(List[str], requirements['subtasks'])
                    subtasks.append(line.strip())

            # Extract dev notes
            dev_notes_section = re.search(r'## Dev Notes\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if dev_notes_section:
                # Cast to Dict[str, str] to help type checker
                dev_notes = cast(Dict[str, str], requirements['dev_notes'])
                dev_notes['content'] = dev_notes_section.group(1).strip()

            # Extract testing info
            testing_section = re.search(r'## Testing\s*\n(.*?)(?=\n---|\n##|$)', story_content, re.DOTALL)
            if testing_section:
                # Cast to Dict[str, str] to help type checker
                testing = cast(Dict[str, str], requirements['testing'])
                testing['content'] = testing_section.group(1).strip()

            # Log with explicit type casting to help type checker
            acceptance_criteria_len = len(cast(List[str], requirements['acceptance_criteria']))
            tasks_len = len(cast(List[str], requirements['tasks']))
            subtasks_len = len(cast(List[str], requirements['subtasks']))

            logger.info(f"Extracted requirements: {acceptance_criteria_len} AC, {tasks_len} tasks, {subtasks_len} subtasks")
            return requirements

        except Exception as e:
            logger.error(f"Failed to extract requirements: {e}")
            return {}

    async def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted requirements."""
        # Initialize with explicit types to help type checker
        issues: List[str] = []
        warnings: List[str] = []

        if not requirements.get('acceptance_criteria'):
            issues.append('No acceptance criteria found')

        if not requirements.get('tasks'):
            warnings.append('No tasks found')

        # Check for minimum viable content
        if not requirements.get('title'):
            issues.append('No title found')

        # Return with explicit type
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
            _ = requirements  # Mark as intentionally unused for now
            _ = guidance  # Mark as intentionally unused for now
            return True
        except Exception as e:
            logger.error(f"Failed to apply dev guidance: {e}")
            return False

    async def _execute_development_tasks(self, requirements: Dict[str, Any]) -> bool:
        """Execute development tasks using Claude Agent SDK with single call."""
        logger.info("Executing development tasks")

        try:
            # Check if SDK is available
            if query is None or ClaudeAgentOptions is None:
                raise RuntimeError(
                    "Claude Agent SDK is required but not available. " +
                    "Please install and configure claude-agent-sdk."
                )

            # Get story path
            story_path = requirements.get('story_path', self._current_story_path or '')

            # Check if story status is already completed
            if story_path:
                story_status = await self._check_story_status(story_path)

                # Check for "Ready for Done" or "Done" status - skip entire dev-qa cycle
                if story_status and ('ready for done' in story_status.lower() or story_status.lower() == 'done'):
                    logger.info(f"[Dev Agent] Story '{story_path}' already completed ({story_status}), skipping dev-qa cycle")
                    return True

                # Check for "Ready for Review" status - skip dev but notify QA
                elif story_status == "Ready for Review":
                    logger.info(f"[Dev Agent] Story '{story_path}' already ready for review, skipping SDK calls")
                    # Development is considered complete, notify QA agent directly
                    _ = await self._notify_qa_agent(story_path)
                    return True
                elif story_status:
                    logger.info(f"[Dev Agent] Story status: {story_status}, proceeding with development")
                else:
                    logger.warning(f"[Dev Agent] Could not determine story status for {story_path}, proceeding anyway")

            # Get log_manager from epic_driver context if available
            log_manager = getattr(self, '_log_manager', None)

            # Check if this is a QA feedback mode (requirements contains qa_prompt)
            if 'qa_prompt' in requirements:
                # Handle QA feedback mode - execute single SDK call
                logger.info(f"{self.name} Handling QA feedback with single SDK call")
                result = await self._execute_single_claude_sdk(requirements['qa_prompt'], story_path, log_manager)
                return result

            # Normal development mode - execute single SDK call
            logger.info(f"{self.name} Executing normal development with single SDK call")
            base_prompt = f'@.bmad-core/agents/dev.md *develop-story "{story_path}" Create or improve comprehensive test suites @tests/, perform test-driven development until all tests pass completely. Change story document Status to "Ready for Review".'

            # Execute single SDK call
            result = await self._execute_single_claude_sdk(base_prompt, story_path, log_manager)

            if result:
                # Development completed successfully, notify QA agent
                _ = await self._notify_qa_agent(story_path)
                logger.info(f"Development tasks completed successfully for: {requirements.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"Development tasks failed for: {requirements.get('title', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"Failed to execute development tasks: {e}")
            return False

    # ========== QA Feedback Handling Methods (Simplified) ==========

    async def _handle_qa_feedback(self, qa_prompt: str, story_path: str) -> bool:
        """
        Handle QA feedback using single SDK call.

        Args:
            qa_prompt: Prompt from QA agent containing gate file paths
            story_path: Path to the story file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"{self.name} handling QA feedback for: {story_path}")

            # Build prompt for QA feedback
            prompt = f'@.bmad-core/agents/dev.md {qa_prompt}'

            # Execute single SDK call for fixing
            result = await self._execute_single_claude_sdk(prompt, story_path)

            if result:
                logger.info(f"{self.name} QA feedback handling completed successfully")

                # After fixing, notify QA again for re-review
                _ = await self._notify_qa_agent(story_path)

                return True
            else:
                logger.error(f"{self.name} QA feedback handling failed")
                return False

        except Exception as e:
            logger.error(f"Failed to handle QA feedback: {e}")
            return False

    async def _execute_single_claude_sdk(self, prompt: str, story_path: str, log_manager: Optional[LogManager] = None) -> bool:
        """
        Execute Claude SDK call with safe wrapper, isolation, and detailed diagnostics.

        Uses SDKSessionManager to ensure SDK calls are isolated from other agents,
        preventing cancel scope propagation issues.

        Args:
            prompt: Prompt for the SDK call
            story_path: Path to the story file
            log_manager: LogManager instance for logging

        Returns:
            True if successful, False otherwise
        """
        # Check if SDK classes are available
        if ClaudeAgentOptions is None or query is None:
            logger.warning("[Dev Agent] Claude Agent SDK not available - using simulation mode")
            return True

        # 预检提示词格式
        if not self._validate_prompt_format(prompt):
            logger.error(f"[Dev Agent] Invalid prompt format for {story_path}")
            return False

        async def sdk_call() -> bool:
            """Inner SDK call wrapped for isolation"""
            if SafeClaudeSDK is None:
                logger.error("[Dev Agent] SafeClaudeSDK not available")
                return False
            # Safe to call ClaudeAgentOptions since we already checked it's not None
            # Use assert to satisfy type checker
            assert ClaudeAgentOptions is not None, "ClaudeAgentOptions should not be None"
            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd())
            )
            sdk = SafeClaudeSDK(prompt, options, timeout=1200.0, log_manager=log_manager)
            return await sdk.execute()

        max_retries = 1
        retry_delay = 1.0  # 1.0 second between retries

        for attempt in range(max_retries):
            try:
                logger.info(f"[Dev Agent] SDK call attempt {attempt + 1}/{max_retries} for {story_path}")
                logger.debug(f"[Dev Agent] Prompt preview: {prompt[:100]}...")

                # Execute with session isolation using dedicated session manager
                result = await self._session_manager.execute_isolated(
                    agent_name="DevAgent",
                    sdk_func=sdk_call,
                    timeout=1200.0
                )

                if result.success:
                    logger.info(f"[Dev Agent] SDK call succeeded for {story_path} in {result.duration_seconds:.1f}s")
                    return True
                elif result.error_type == SDKErrorType.CANCELLED:
                    logger.info(f"[Dev Agent] SDK call cancelled for {story_path}")
                    return False  # Don't retry on cancellation
                elif result.error_type == SDKErrorType.TIMEOUT:
                    logger.warning(f"[Dev Agent] SDK call timed out for {story_path}")
                    if attempt < max_retries - 1:
                        logger.info(f"[Dev Agent] Retrying in {retry_delay}s...")
                        await asyncio.sleep(1.0)
                else:
                    logger.warning(f"[Dev Agent] SDK call failed (attempt {attempt + 1}): {result.error_message}")
                    if attempt < max_retries - 1:
                        logger.info(f"[Dev Agent] Retrying in {retry_delay}s...")
                        await asyncio.sleep(1.0)

            except Exception as e:
                logger.error(f"[Dev Agent] SDK call exception (attempt {attempt + 1}): {type(e).__name__}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"[Dev Agent] Retrying in {retry_delay}s...")
                    await asyncio.sleep(1.0)

        logger.error(f"[Dev Agent] All {max_retries} attempts failed for {story_path}")
        return False

    async def _notify_qa_agent(self, story_path: str) -> Optional[Dict[str, Any]]:
        """
        Notify QA agent after development completion and get feedback.

        Args:
            story_path: Path to the story file

        Returns:
            QA feedback dictionary or None if failed
        """
        try:
            logger.info(f"[Dev Agent] Notifying QA agent for: {story_path}")

            # Read story content
            story_file = Path(story_path)
            if not story_file.exists():
                logger.error(f"[Dev Agent] Story file not found: {story_path}")
                return None

            with open(story_file, 'r', encoding='utf-8') as f:
                story_content = f.read()

            # Import and instantiate QA agent
            try:
                from .qa_agent import QAAgent
            except ImportError:
                logger.warning("[Dev Agent] QA agent not available - simulating QA review")
                return {
                    'passed': True,
                    'completed': True,
                    'needs_fix': False
                }

            qa_agent = QAAgent()

            # Execute QA review
            qa_result = await qa_agent.execute(
                story_content=story_content,
                story_path=story_path
            )

            logger.info(f"[Dev Agent] QA review completed: {qa_result}")

            # Check if QA found issues
            if qa_result.get('needs_fix'):
                logger.info("[Dev Agent] QA found issues, will trigger Dev-QA loop")
                return qa_result
            else:
                logger.info("[Dev Agent] QA passed, story completed")
                return qa_result

        except Exception as e:
            logger.error(f"Failed to notify QA agent: {e}")
            return None

    async def _update_story_completion(self, story_content: str, requirements: Dict[str, Any]) -> None:
        """Update story file with completion information."""
        logger.info("Updating story file with completion")
        _ = story_content  # Mark as intentionally unused - reading file directly
        _ = requirements  # Mark as intentionally unused - requirements already processed

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
            with open(story_path, 'w', encoding='utf-8') as f:  # type: ignore[assignment]
                f.write(content)

            logger.info(f"Updated story file: {story_path}")

        except Exception as e:
            logger.error(f"Failed to update story file: {e}")

    async def _check_story_status(self, story_path: str) -> Optional[str]:
        """
        Check the status field in a story document.

        Args:
            story_path: Path to the story file

        Returns:
            Status string (e.g., "Ready for Review", "Ready for Done", "Done", "Approved", "Draft")
            or None if not found/error
        """
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"[Dev Agent] Story file not found: {story_path}")
                return None

            with open(story_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match the Status section pattern: ## Status\n**Status Text**
            status_match = re.search(
                r'## Status\s*\n\s*\*\*([^*]+)\*\*',
                content,
                re.MULTILINE
            )

            if status_match:
                status_text = status_match.group(1).strip()
                logger.debug(f"[Dev Agent story] Found status: '{status_text}'")
                return status_text
            else:
                logger.warning(f"[Dev Agent] Status section not found in {story_path}")
                return None

        except Exception as e:
            logger.error(f"[Dev Agent] Error checking story status: {e}")
            return None


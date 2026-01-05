"""
Dev Agent - Development Agent

Handles development tasks and implementation according to story requirements.
Integrates with task guidance for development-specific operations.
Uses Claude Code CLI for actual implementation.
"""

import logging
import subprocess
import asyncio
from typing import Dict, Any, Optional, List, cast, TYPE_CHECKING
import re
from pathlib import Path

if TYPE_CHECKING:
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

try:
    from claude_agent_sdk import query as _query, ClaudeAgentOptions as _ClaudeAgentOptions, ResultMessage as _ResultMessage
except ImportError:
    # For development without SDK installed
    _query = None
    _ClaudeAgentOptions = None
    _ResultMessage = None

# Export for use in code
query = _query
ClaudeAgentOptions = _ClaudeAgentOptions
ResultMessage = _ResultMessage

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
        task_guidance: str = "",
        story_path: str = ""
    ) -> bool:
        """
        Execute Dev phase for a story.

        Args:
            story_content: Raw markdown content of the story
            task_guidance: Task guidance from .bmad-core/tasks/develop-story.md
            story_path: Path to the story file

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
            return True
        except Exception as e:
            logger.error(f"Failed to apply dev guidance: {e}")
            return False

    async def _execute_development_tasks(self, requirements: Dict[str, Any]) -> bool:
        """Execute development tasks using Claude Agent SDK."""
        logger.info("Executing development tasks")

        try:
            # Check if SDK is available
            if query is None or ClaudeAgentOptions is None:
                logger.warning("Claude Agent SDK not available - using simulation mode")
                logger.info(f"Simulated development of: {requirements.get('title', 'Unknown')}")
                return True

            # Get story path
            story_path = requirements.get('story_path', self._current_story_path or '')

            # Check if this is a QA feedback mode (requirements contains qa_prompt)
            if 'qa_prompt' in requirements:
                # Handle QA feedback mode
                return await self._handle_qa_feedback(requirements['qa_prompt'], story_path)

            # Normal development mode
            # Build the prompt for SDK
            prompt = f'@.bmad-core\\agents\\dev.md *develop-story "{story_path}" 创建或完善测试套件 @tests\\，执行测试驱动开发，直至所有测试完全通过'

            # Execute SDK calls
            result = await self._execute_claude_sdk(prompt, story_path)

            if result:
                logger.info(f"Development tasks completed successfully for: {requirements.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"Development tasks failed for: {requirements.get('title', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"Failed to execute development tasks: {e}")
            return False

    # ========== NEW: QA Feedback Handling Methods (奥卡姆剃刀原则 - 极简方案) ==========

    async def _handle_qa_feedback(self, qa_prompt: str, story_path: str) -> bool:
        """
        Handle QA feedback and execute triple Claude SDK calls.

        Args:
            qa_prompt: Prompt from QA agent containing gate file paths
            story_path: Path to the story file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"{self.name} handling QA feedback for: {story_path}")

            # Execute triple independent Claude SDK calls
            success = await self._execute_triple_claude_calls(qa_prompt, story_path)

            if success:
                # Notify QA agent after completion
                await self._notify_qa_agent(story_path)
                logger.info(f"{self.name} QA feedback handling completed successfully")
                return True
            else:
                logger.error(f"{self.name} QA feedback handling failed")
                return False

        except Exception as e:
            logger.error(f"Failed to handle QA feedback: {e}")
            return False

    async def _execute_triple_claude_calls(self, qa_prompt: str, story_path: str) -> bool:
        """
        Execute three independent Claude SDK calls with bypasspermissions.

        Args:
            qa_prompt: Prompt from QA agent
            story_path: Path to the story file

        Returns:
            True if all three calls succeeded, False otherwise
        """
        try:
            logger.info(f"{self.name} executing triple Claude SDK calls for: {story_path}")

            # Build the combined prompt
            base_prompt = f'@.bmad-core\\agents\\dev.md {qa_prompt}'

            # Execute three independent calls (not retries - three separate calls)
            for i in range(3):
                round_number = i + 1
                try:
                    logger.info(f"[Dev Agent] Executing {round_number}/3 independent SDK call for {story_path}")

                    # Create round-specific prompt
                    round_prompt = f"{base_prompt} 第{round_number}轮修复"

                    # Execute the SDK call without retry logic (these are independent calls)
                    # Use the existing _execute_claude_sdk but call it three times independently
                    result = await self._execute_single_claude_sdk(round_prompt, story_path)

                    if not result:
                        logger.error(f"[Dev Agent] {round_number}/3 call failed for {story_path}")
                        return False

                    logger.info(f"[Dev Agent] {round_number}/3 call succeeded for {story_path}")

                except Exception as e:
                    logger.error(f"[Dev Agent] {round_number}/3 call exception: {str(e)}")
                    return False

            logger.info(f"{self.name} All three SDK calls completed successfully for: {story_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute triple Claude SDK calls: {e}")
            return False

    async def _execute_single_claude_sdk(self, prompt: str, story_path: str) -> bool:
        """
        Execute a single Claude SDK call (for triple call mode).

        Args:
            prompt: Prompt for the SDK call
            story_path: Path to the story file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if SDK classes are available
            if ClaudeAgentOptions is None or query is None:
                logger.warning("Claude Agent SDK not available - using simulation mode")
                return True

            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd())
            )

            # Execute single SDK call (no retry logic for independent calls)
            message_count = 0
            async for message in query(prompt=prompt, options=options):
                message_count += 1
                # Check if ResultMessage is available before isinstance
                if ResultMessage is not None and isinstance(message, ResultMessage):
                    if message.is_error:
                        logger.error(f"[Dev Agent] SDK call failed: {message.result}")
                        return False
                    else:
                        # Ensure result is not None before slicing
                        result_str = message.result if message.result is not None else ""
                        logger.info(f"[Dev Agent] SDK call succeeded: {result_str[:200]}...")
                        return True

            # If we received messages, return success
            if message_count > 0:
                return True

            logger.warning(f"[Dev Agent] No messages received for: {story_path}")
            return False

        except Exception as e:
            logger.error(f"[Dev Agent] SDK call exception: {str(e)}")
            return False

    async def _notify_qa_agent(self, story_path: str) -> None:
        """
        Notify QA agent after development completion.

        Args:
            story_path: Path to the story file
        """
        try:
            logger.info(f"[Dev Agent] Notifying QA agent for: {story_path}")
            # This is a placeholder for actual notification logic
            # In a real implementation, this might send a message to a queue,
            # call a callback, or update a shared state
            # For now, we just log that notification would be sent

        except Exception as e:
            logger.error(f"Failed to notify QA agent: {str(e)}")


    async def _execute_claude_sdk(self, prompt: str, story_path: str) -> bool:
        """Execute Claude SDK call with retry logic."""
        try:
            # Check if SDK classes are available
            if ClaudeAgentOptions is None or query is None:
                logger.warning("Claude Agent SDK not available - using simulation mode")
                return True

            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd())
            )

            max_retries = 3
            retry_delay = 60  # 60 seconds between retries

            for attempt in range(max_retries):
                try:
                    logger.info(f"[Dev Agent] 尝试调用SDK (第{attempt + 1}次) for {story_path}")

                    message_count = 0
                    async for message in query(prompt=prompt, options=options):
                        message_count += 1
                        # Check if ResultMessage is available before isinstance
                        if ResultMessage is not None and isinstance(message, ResultMessage):
                            # Type narrowing: message is ResultMessage
                            # type: ignore[union-attr] - is_error and result are ResultMessage attributes
                            if message.is_error:
                                logger.error(f"[Dev Agent] SDK调用失败: {message.result}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                                    break
                                return False
                            else:
                                # Ensure result is not None before slicing
                                result_str = message.result if message.result is not None else ""
                                logger.info(f"[Dev Agent] SDK调用成功: {result_str[:200]}...")
                                return True

                    # If we received messages, break from retry loop
                    if message_count > 0:
                        break

                except Exception as e:
                    logger.error(f"[Dev Agent] SDK调用异常: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        return False

            return True

        except Exception as e:
            logger.error(f"[Dev Agent] SDK初始化失败: {str(e)}")
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

"""
Dev Agent - Development Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Optional, cast

from anyio.abc import TaskGroup

from .base_agent import BaseAgent

# Import LogManager for runtime use
from autoBMAD.epic_automation.log_manager import LogManager

logger = logging.getLogger(__name__)


class DevAgent(BaseAgent):
    """Development agent for handling implementation tasks."""

    def __init__(
        self,
        task_group: Optional[TaskGroup] = None,
        use_claude: bool = True,
        log_manager: Optional[LogManager] = None,
    ):
        """
        Initialize Dev agent.

        Args:
            task_group: TaskGroup实例
            use_claude: If True, use Claude Code CLI for real implementation
            log_manager: Optional LogManager instance for logging
        """
        super().__init__("DevAgent", task_group, log_manager)
        self.use_claude = use_claude
        self._claude_available = (
            self._check_claude_available() if use_claude else False
        )
        self._current_story_path = None

        # 集成SDKExecutor
        self.sdk_executor = None
        try:
            from ..core.sdk_executor import SDKExecutor
            self.sdk_executor = SDKExecutor()
        except ImportError:
            self._log_execution("SDKExecutor not available", "warning")

        # Initialize SimpleStoryParser
        try:
            self.status_parser = None
            try:
                from .state_agent import SimpleStoryParser
                from ..sdk_wrapper import SafeClaudeSDK

                if SafeClaudeSDK:
                    from claude_agent_sdk import ClaudeAgentOptions

                    options = ClaudeAgentOptions(
                        permission_mode="bypassPermissions", cwd=str(Path.cwd())
                    )
                    sdk_instance = SafeClaudeSDK(
                        prompt="Parse story status",
                        options=options,
                        timeout=None,
                        log_manager=log_manager,
                    )
                    self.status_parser = SimpleStoryParser(sdk_wrapper=sdk_instance)
                else:
                    self.status_parser = None
            except ImportError:
                self.status_parser = None
                self._log_execution("SimpleStoryParser not available", "warning")
        except Exception as e:
            self.status_parser = None
            self._log_execution(f"Failed to initialize status parser: {e}", "warning")

        self._log_execution(
            f"DevAgent initialized (claude_mode={use_claude}, "
            f"claude_available={self._claude_available})"
        )

    async def execute(self, story_path: str) -> bool:
        """
        执行开发任务

        Args:
            story_path: 故事文件路径

        Returns:
            固定返回 True
        """
        self._log_execution(f"Executing development for {story_path}")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            # 即使没有TaskGroup也继续执行
            return await self._execute_development(story_path)

        # 使用_execute_within_taskgroup来执行
        async def _execute():
            return await self._execute_development(story_path)

        return await self._execute_within_taskgroup(_execute)

    async def _execute_development(self, story_path: str) -> bool:
        """执行开发任务的核心逻辑"""
        try:
            self._log_execution(
                f"Epic Driver has determined this story needs development"
            )

            # 读取故事内容
            story_file = Path(story_path)
            if story_file.exists():
                story_content = story_file.read_text(encoding="utf-8")
                requirements = await self._extract_requirements(story_content)

                # 执行开发任务
                development_success = await self._execute_development_tasks(
                    requirements, story_path
                )
                self._log_execution(
                    f"Development tasks executed (result={development_success})"
                )
            else:
                self._log_execution(f"Story file not found: {story_path}", "warning")

            self._log_execution(
                "Development execution completed, "
                "Epic Driver will re-parse status to determine next step"
            )
            return True

        except Exception as e:
            self._log_execution(
                f"Exception during development: {e}, continuing workflow",
                "warning",
            )
            return True

    async def _execute_development_tasks(
        self, requirements: dict[str, Any], story_path: str
    ) -> bool:
        """执行开发任务 - 使用SDKExecutor"""
        try:
            # 检查QA反馈模式
            if "qa_prompt" in requirements:
                self._log_execution("Handling QA feedback with single SDK call")
                prompt = f"@.bmad-core/agents/dev.md {requirements['qa_prompt']}"
                if self.sdk_executor:
                    await self._execute_sdk_call(self.sdk_executor, prompt)
                return True

            # 正常开发模式
            self._log_execution(f"Executing normal development mode for '{story_path}'")
            base_prompt = (
                f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\dev.md '
                f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\tasks\\develop-story.md '
                f'According to Story @{story_path}, '
                f'Create or improve comprehensive test suites '
                f'@D:\\GITHUB\\pytQt_template\\autoBMAD\\spec_automation\\tests. '
                f'Perform Test-Driven Development (TDD) iteratively until achieving '
                f'100% tests pass with comprehensive coverage. '
                f'Run "pytest -v --tb=short --cov" to verify tests and coverage. '
                f'Change story Status to "Ready for Review" when complete.'
            )

            if self.sdk_executor:
                await self._execute_sdk_call(self.sdk_executor, base_prompt)

            self._log_execution(
                f"Development execution completed, "
                f"Epic Driver will re-parse status to determine next step"
            )
            return True

        except Exception as e:
            self._log_execution(
                f"Exception during development tasks: {e}, continuing workflow",
                "warning",
            )
            return True

    async def _extract_requirements(self, story_content: str) -> dict[str, Any]:
        """提取需求 - 保持现有实现"""
        try:
            # Basic requirement extraction from markdown
            requirements: dict[str, Any] = {
                "title": "",
                "acceptance_criteria": [],
                "tasks": [],
                "subtasks": [],
                "dev_notes": {},
                "testing": {},
            }

            # Extract title
            title_match = re.search(r"^# .+:(.+)$", story_content, re.MULTILINE)
            if title_match:
                requirements["title"] = title_match.group(1).strip()
            else:
                # Try alternative pattern
                title_match = re.search(
                    r"^# Story \d+:\s*(.+)$", story_content, re.MULTILINE
                )
                if title_match:
                    requirements["title"] = title_match.group(1).strip()

            # Extract acceptance criteria
            ac_section = re.search(
                r"## Acceptance Criteria\n(.*?)(?=\n##|\Z)", story_content, re.DOTALL
            )
            if ac_section:
                ac_lines = ac_section.group(1).strip().split("\n")
                for line in ac_lines:
                    if line.strip() and re.match(r"^\d+\.", line.strip()):
                        acceptance_criteria = cast(
                            list[str], requirements["acceptance_criteria"]
                        )
                        acceptance_criteria.append(line.strip())
            else:
                # Try alternative pattern with checkboxes
                ac_section = re.search(
                    r"## Acceptance Criteria\s*\n(.*?)(?=\n---|\n##|$)",
                    story_content,
                    re.DOTALL,
                )
                if ac_section:
                    ac_lines = ac_section.group(1).strip().split("\n")
                    for line in ac_lines:
                        if line.strip().startswith("-"):
                            acceptance_criteria = cast(
                                list[str], requirements["acceptance_criteria"]
                            )
                            acceptance_criteria.append(line.strip())

            # Extract tasks
            tasks_section = re.search(
                r"## Tasks / Subtasks\n(.*?)(?=\n##|\Z)", story_content, re.DOTALL
            )
            if tasks_section:
                task_lines = tasks_section.group(1).strip().split("\n")
                for line in task_lines:
                    if line.strip().startswith("- [ ]"):
                        tasks = cast(list[str], requirements["tasks"])
                        tasks.append(line.strip())
            else:
                # Try alternative pattern
                tasks_section = re.search(
                    r"## Tasks / Subtasks\s*\n(.*?)(?=\n---|\n##|$)",
                    story_content,
                    re.DOTALL,
                )
                if tasks_section:
                    task_lines = tasks_section.group(1).strip().split("\n")
                    for line in task_lines:
                        if line.strip().startswith("-"):
                            tasks = cast(list[str], requirements["tasks"])
                            tasks.append(line.strip())

            # Extract subtasks (nested)
            subtask_pattern = r"^\s*-\s*\[x\]\s*(.+)"
            for line in story_content.split("\n"):
                if re.match(subtask_pattern, line):
                    subtasks = cast(list[str], requirements["subtasks"])
                    subtasks.append(line.strip())

            # Extract dev notes
            dev_notes_section = re.search(
                r"## Dev Notes\s*\n(.*?)(?=\n---|\n##|$)", story_content, re.DOTALL
            )
            if dev_notes_section:
                dev_notes = cast(dict[str, str], requirements["dev_notes"])
                dev_notes["content"] = dev_notes_section.group(1).strip()

            # Extract testing info
            testing_section = re.search(
                r"## Testing\s*\n(.*?)(?=\n---|\n##|$)", story_content, re.DOTALL
            )
            if testing_section:
                testing = cast(dict[str, str], requirements["testing"])
                testing["content"] = testing_section.group(1).strip()

            # Log with explicit type casting to help type checker
            acceptance_criteria_len = len(
                cast(list[str], requirements["acceptance_criteria"])
            )
            tasks_len = len(cast(list[str], requirements["tasks"]))
            subtasks_len = len(cast(list[str], requirements["subtasks"]))

            self._log_execution(
                f"Extracted requirements: {acceptance_criteria_len} AC, {tasks_len} tasks, {subtasks_len} subtasks"
            )
            return requirements

        except Exception as e:
            self._log_execution(f"Failed to extract requirements: {e}", "error")
            return {}

    def _validate_prompt_format(self, prompt: str) -> bool:
        """Validate prompt format for BMAD commands."""
        try:
            # 基本格式检查
            if not prompt or len(prompt.strip()) == 0:
                self._log_execution("[Prompt Validation] Empty prompt", "error")
                return False

            # BMAD命令格式检查
            if not prompt.startswith("@"):
                self._log_execution(
                    f"[Prompt Validation] Prompt doesn't start with @: {prompt[:50]}...", "warning"
                )

            # 检查是否包含develop-story命令
            if "*develop-story" not in prompt:
                self._log_execution(
                    f"[Prompt Validation] Missing *develop-story command: {prompt[:100]}...", "warning"
                )

            # 检查文件路径格式
            if '"' in prompt:
                # 提取引号内的路径
                path_matches = re.findall(r'"([^"]+)"', prompt)
                for path in path_matches:
                    if not path.endswith(".md"):
                        self._log_execution(
                            f"[Prompt Validation] Non-markdown file path: {path}", "warning"
                        )
                    # 检查路径是否存在
                    path_obj = Path(path)
                    if not path_obj.exists():
                        self._log_execution(
                            f"[Prompt Validation] Story file not found: {path}", "warning"
                        )

            # 检查编码问题（非ASCII字符）
            try:
                _ = prompt.encode("ascii")
            except UnicodeEncodeError:
                self._log_execution(
                    "[Prompt Validation] Prompt contains non-ASCII characters", "warning"
                )

            self._log_execution("[Prompt Validation] Prompt format validation passed")
            return True

        except Exception as e:
            self._log_execution(f"[Prompt Validation] Validation error: {str(e)}", "error")
            return False

    def _check_claude_available(self) -> bool:
        """Check if Claude Code CLI is available with retry logic."""
        import os
        import time

        max_retries = 1
        timeout = 30  # Increased from 10 to 30 seconds

        possible_commands = [
            ["claude", "--version"],
            [r"C:\Users\Administrator\AppData\Roaming\npm\claude", "--version"],
            [r"C:\Users\Administrator\AppData\Roaming\npm\claude.cmd", "--version"],
            ["where", "claude"],
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
                            env=env,
                        )
                        if result.returncode == 0:
                            if cmd[0] == "where":
                                paths = result.stdout.strip().split("\n")
                                if paths:
                                    verify = subprocess.run(
                                        [paths[0], "--version"],
                                        capture_output=True,
                                        text=True,
                                        timeout=timeout,
                                        shell=True,
                                        env=env,
                                    )
                                    if verify.returncode == 0:
                                        self._log_execution(
                                            f"Claude Code CLI available: {verify.stdout.strip()}"
                                        )
                                        return True
                            else:
                                self._log_execution(
                                    f"Claude Code CLI available: {result.stdout.strip()}"
                                )
                                return True
                    except subprocess.TimeoutExpired:
                        self._log_execution(
                            f"CLI check timeout for {cmd[0]} (attempt {attempt + 1}/{max_retries})", "warning"
                        )
                        continue
                    except Exception:
                        continue

                # If no command worked in this attempt, try again
                if attempt < max_retries - 1:
                    self._log_execution(
                        f"CLI check attempt {attempt + 1} failed, retrying in 2s...", "warning"
                    )
                    time.sleep(2)

            except Exception as e:
                self._log_execution(f"CLI check attempt {attempt + 1} failed: {e}", "warning")
                if attempt < max_retries - 1:
                    time.sleep(2)

        self._log_execution(f"Claude Code CLI not available after {max_retries} attempts", "error")
        return False

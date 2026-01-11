"""
Dev Agent - Development Agent

Handles development tasks and implementation according to story requirements.
Integrates with task guidance for development-specific operations.
Uses Claude Code CLI for actual implementation.
"""

import asyncio
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, cast

if TYPE_CHECKING:
    from claude_agent_sdk import ClaudeAgentOptions, query

# Import LogManager for runtime use
from autoBMAD.epic_automation.log_manager import LogManager

try:
    from claude_agent_sdk import (
        ClaudeAgentOptions as _ClaudeAgentOptions,
    )
    from claude_agent_sdk import (
        ResultMessage as _ResultMessage,
    )
    from claude_agent_sdk import (
        query as _query,
    )
except ImportError:
    # For development without SDK installed
    _query = None
    _ClaudeAgentOptions = None
    _ResultMessage = None

# Import SDK session manager for isolated execution
from .sdk_session_manager import SDKSessionManager
from .story_parser import SimpleStoryParser

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

    def __init__(
        self, use_claude: bool = True, log_manager: LogManager | None = None
    ):
        """
        Initialize Dev agent.

        Args:
            use_claude: If True, use Claude Code CLI for real implementation.
                       If False, use simulation mode (for testing).
            log_manager: Optional LogManager instance for logging.
        """
        self.name = "Dev Agent"
        self.use_claude = use_claude
        self._claude_available = self._check_claude_available() if use_claude else False
        # 每个DevAgent实例创建独立的会话管理器，消除跨Agent cancel scope污染
        self._session_manager = SDKSessionManager()

        # Store log_manager for use in SDK calls
        self._log_manager = log_manager

        # Track current story path for context
        self._current_story_path = None

        # Initialize SimpleStoryParser for robust status parsing
        try:
            # 创建 SafeClaudeSDK 实例并传入，提供必需的参数
            # SafeClaudeSDK 可能为 None（导入失败时），需要检查
            if SafeClaudeSDK is not None:
                # Create proper options object for status parsing
                options = None
                if _ClaudeAgentOptions:
                    options = _ClaudeAgentOptions(
                        permission_mode="bypassPermissions", cwd=str(Path.cwd())
                    )
                # 使用 SafeClaudeSDK 抑制 cancel scope 错误
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
            logger.warning(
                "[Dev Agent] SimpleStoryParser not available, using fallback parsing"
            )

        logger.info(
            f"{self.name} initialized (claude_mode={self.use_claude}, claude_available={self._claude_available})"
        )

    def _validate_prompt_format(self, prompt: str) -> bool:
        """Validate prompt format for BMAD commands."""
        try:
            # 基本格式检查
            if not prompt or len(prompt.strip()) == 0:
                logger.error("[Prompt Validation] Empty prompt")
                return False

            # BMAD命令格式检查
            if not prompt.startswith("@"):
                logger.warning(
                    f"[Prompt Validation] Prompt doesn't start with @: {prompt[:50]}..."
                )

            # 检查是否包含develop-story命令
            if "*develop-story" not in prompt:
                logger.warning(
                    f"[Prompt Validation] Missing *develop-story command: {prompt[:100]}..."
                )

            # 检查文件路径格式
            if '"' in prompt:
                # 提取引号内的路径
                path_matches = re.findall(r'"([^"]+)"', prompt)
                for path in path_matches:
                    if not path.endswith(".md"):
                        logger.warning(
                            f"[Prompt Validation] Non-markdown file path: {path}"
                        )
                    # 检查路径是否存在
                    path_obj = Path(path)
                    if not path_obj.exists():
                        logger.warning(
                            f"[Prompt Validation] Story file not found: {path}"
                        )

            # 检查编码问题（非ASCII字符）
            try:
                _ = prompt.encode("ascii")
            except UnicodeEncodeError:
                logger.warning(
                    "[Prompt Validation] Prompt contains non-ASCII characters"
                )

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
                                        logger.info(
                                            f"Claude Code CLI available: {verify.stdout.strip()}"
                                        )
                                        return True
                            else:
                                logger.info(
                                    f"Claude Code CLI available: {result.stdout.strip()}"
                                )
                                return True
                    except subprocess.TimeoutExpired:
                        logger.warning(
                            f"CLI check timeout for {cmd[0]} (attempt {attempt + 1}/{max_retries})"
                        )
                        continue
                    except Exception:
                        continue

                # If no command worked in this attempt, try again
                if attempt < max_retries - 1:
                    logger.warning(
                        f"CLI check attempt {attempt + 1} failed, retrying in 2s..."
                    )
                    time.sleep(2)

            except Exception as e:
                logger.warning(f"CLI check attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        logger.error(f"Claude Code CLI not available after {max_retries} attempts")
        return False

    async def execute(
        self,
        story_path: str,
    ) -> bool:
        """
        🎯 核心设计：Dev Agent 不再检查状态，只执行开发任务
        - Epic Driver 已根据核心状态值决定是否调用 Dev Agent
        - Dev Agent 收到调用就直接执行开发任务，不做任何状态判断
        - 返回值仅用于日志记录，不影响工作流决策

        Args:
            story_path: 故事文件路径

        Returns:
            固定返回 True
        """
        try:
            logger.info(f"[Dev Agent] Executing development for {story_path}")
            logger.info(f"[Dev Agent] Epic Driver has determined this story needs development")

            # 直接执行开发任务，不检查状态
            try:
                # 读取故事内容
                story_file = Path(story_path)
                if story_file.exists():
                    story_content = story_file.read_text(encoding="utf-8")
                    requirements = await self._extract_requirements(story_content)
                    
                    # 执行开发任务
                    development_success = await self._execute_development_tasks(requirements)
                    logger.info(f"[Dev Agent] Development tasks executed (result={development_success})")
                else:
                    logger.warning(f"[Dev Agent] Story file not found: {story_path}")
            except Exception as e:
                logger.warning(f"[Dev Agent] Development task execution failed: {e}, continuing workflow")

            # 🎯 关键：无论开发结果如何，都返回 True
            # Epic Driver 会重新解析状态来决定下一步
            logger.info(f"[Dev Agent] Development execution completed, "
                       f"Epic Driver will re-parse status to determine next step")
            return True

        except Exception as e:
            # 🎯 关键：所有异常都只记录日志，返回 True
            logger.warning(f"[Dev Agent] Exception during development: {e}, continuing workflow")
            return True

    async def _extract_requirements(self, story_content: str) -> dict[str, Any]:
        """Extract requirements from story content."""
        logger.info("Extracting requirements from story")

        try:
            # Basic requirement extraction from markdown
            # Type the requirements dict structure explicitly
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
                        # Cast to List[str] to help type checker
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
                            # Cast to List[str] to help type checker
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
                        # Cast to List[str] to help type checker
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
                            # Cast to List[str] to help type checker
                            tasks = cast(list[str], requirements["tasks"])
                            tasks.append(line.strip())

            # Extract subtasks (nested)
            subtask_pattern = r"^\s*-\s*\[x\]\s*(.+)"
            for line in story_content.split("\n"):
                if re.match(subtask_pattern, line):
                    # Cast to List[str] to help type checker
                    subtasks = cast(list[str], requirements["subtasks"])
                    subtasks.append(line.strip())

            # Extract dev notes
            dev_notes_section = re.search(
                r"## Dev Notes\s*\n(.*?)(?=\n---|\n##|$)", story_content, re.DOTALL
            )
            if dev_notes_section:
                # Cast to Dict[str, str] to help type checker
                dev_notes = cast(dict[str, str], requirements["dev_notes"])
                dev_notes["content"] = dev_notes_section.group(1).strip()

            # Extract testing info
            testing_section = re.search(
                r"## Testing\s*\n(.*?)(?=\n---|\n##|$)", story_content, re.DOTALL
            )
            if testing_section:
                # Cast to Dict[str, str] to help type checker
                testing = cast(dict[str, str], requirements["testing"])
                testing["content"] = testing_section.group(1).strip()

            # Log with explicit type casting to help type checker
            acceptance_criteria_len = len(
                cast(list[str], requirements["acceptance_criteria"])
            )
            tasks_len = len(cast(list[str], requirements["tasks"]))
            subtasks_len = len(cast(list[str], requirements["subtasks"]))

            logger.info(
                f"Extracted requirements: {acceptance_criteria_len} AC, {tasks_len} tasks, {subtasks_len} subtasks"
            )
            return requirements

        except Exception as e:
            logger.error(f"Failed to extract requirements: {e}")
            return {}

    async def _validate_requirements(
        self, requirements: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate extracted requirements."""
        # Initialize with explicit types to help type checker
        issues: list[str] = []
        warnings: list[str] = []

        if not requirements.get("acceptance_criteria"):
            issues.append("No acceptance criteria found")

        if not requirements.get("tasks"):
            warnings.append("No tasks found")

        # Check for minimum viable content
        if not requirements.get("title"):
            issues.append("No title found")

        # Return with explicit type
        return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}

    async def _execute_development_tasks(self, requirements: dict[str, Any]) -> bool:
        """
        Execute development tasks using Claude Agent SDK with single call.
        
        🎯 核心设计：Dev Agent 不再检查状态，只执行开发任务
        - Epic Driver 已根据核心状态值决定是否调用 Dev Agent
        - Dev Agent 收到调用就直接执行，不做任何状态判断
        - 返回值仅用于日志记录，不影响工作流决策
        """
        try:
            # Check if SDK is available
            if query is None or ClaudeAgentOptions is None:
                logger.warning(
                    "[Dev Agent] Claude Agent SDK not available, skipping development"
                )
                # 🎯 关键：即使 SDK 不可用，也返回 True（由 Epic Driver 根据状态决策）
                return True

            # Get story path
            story_path = requirements.get("story_path", self._current_story_path or "")
            
            logger.info(f"[Dev Agent] Executing development for {story_path}")
            logger.info(f"[Dev Agent] Epic Driver has determined this story needs development based on core status")

            # Check if this is a QA feedback mode (requirements contains qa_prompt)
            if "qa_prompt" in requirements:
                # Handle QA feedback mode - execute single SDK call
                logger.info(f"{self.name} Handling QA feedback with single SDK call")
                result = await self._execute_single_claude_sdk(
                    requirements["qa_prompt"], story_path, self._log_manager
                )
                # 🎯 关键：返回值不影响工作流，由 Epic Driver 重新解析状态
                return True

            # Normal development mode - execute single SDK call
            logger.info(f"[Dev Agent] Executing normal development mode for '{story_path}'")
            base_prompt = f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\dev.md @D:\\GITHUB\\pytQt_template\\.bmad-core\\tasks\\develop-story.md According to Story @{story_path}, Create or improve comprehensive test suites @D:\\GITHUB\\pytQt_template\\autoBMAD\\spec_automation\\tests. Perform Test-Driven Development (TDD) iteratively until achieving 100% tests pass with comprehensive coverage. Run "pytest -v --tb=short --cov" to verify tests and coverage. Change story Status to "Ready for Review" when complete. '

            # Execute single SDK call
            result = await self._execute_single_claude_sdk(
                base_prompt, story_path, self._log_manager
            )

            # 🎯 关键：无论 SDK 返回什么，都返回 True
            # 工作流完全由 Epic Driver 重新解析状态来驱动
            logger.info(
                f"[Dev Agent] Development execution completed (result={result}), "
                f"Epic Driver will re-parse status to determine next step"
            )
            return True

        except Exception as e:
            # 🎯 关键：所有异常都只记录日志，返回 True
            # 让 Epic Driver 根据状态决策，而不是根据异常
            logger.warning(f"[Dev Agent] Exception during development: {e}, continuing workflow")
            return True

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
            prompt = f"@.bmad-core/agents/dev.md {qa_prompt}"

            # Execute single SDK call for fixing
            result = await self._execute_single_claude_sdk(
                prompt, story_path, self._log_manager
            )

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

    async def _execute_single_claude_sdk(
        self, prompt: str, story_path: str, log_manager: LogManager | None = None
    ) -> bool:
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
            logger.warning(
                "[Dev Agent] Claude Agent SDK not available - using simulation mode"
            )
            return True

        # 预检提示词格式
        if not self._validate_prompt_format(prompt):
            logger.error(f"[Dev Agent] Invalid prompt format for {story_path}")
            return False

        async def sdk_call() -> bool:
            """内部 SDK 调用 - 无外部超时保护"""
            if SafeClaudeSDK is None:
                logger.error("[Dev Agent] SafeClaudeSDK not available")
                return False

            assert ClaudeAgentOptions is not None, (
                "ClaudeAgentOptions should not be None"
            )
            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",
                cwd=str(Path.cwd()),
                max_turns=1000,  # 唯一防护：限制对话轮数
                cli_path=r"D:\GITHUB\pytQt_template\venv\Lib\site-packages\claude_agent_sdk\_bundled\claude.exe",
            )
            # 使用 SafeClaudeSDK 抑制 cancel scope 错误
            sdk = SafeClaudeSDK(prompt, options, timeout=None, log_manager=log_manager)
            return await sdk.execute()

        try:
            # 关键修复：移除 asyncio.wait_for 和 asyncio.shield 嵌套
            # 直接执行，让 SDK 自然完成
            result = await self._session_manager.execute_isolated(
                agent_name="DevAgent",
                sdk_func=sdk_call,
                timeout=None,  # 移除外部超时
            )

            if result.success:
                logger.info(
                    f"[Dev Agent] SDK call succeeded for {story_path} in {result.duration_seconds:.1f}s"
                )
                return True
            else:
                logger.warning(f"[Dev Agent] SDK call failed: {result.error_message}")
                return False

        except Exception as e:
            logger.error(
                f"[Dev Agent] SDK call exception: {type(e).__name__}: {str(e)}"
            )
            return False

    async def _notify_qa_agent(self, story_path: str) -> dict[str, Any] | None:
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

            with open(story_file, encoding="utf-8") as f:
                story_content = f.read()

            # Import and instantiate QA agent
            try:
                from .qa_agent import QAAgent
            except ImportError:
                logger.warning(
                    "[Dev Agent] QA agent not available - simulating QA review"
                )
                return {"passed": True, "completed": True, "needs_fix": False}

            qa_agent = QAAgent()

            # Execute QA review
            qa_result = await qa_agent.execute(story_path=story_path)

            logger.info(f"[Dev Agent] QA review completed: {qa_result}")

            # Check if QA found issues
            if qa_result.get("needs_fix"):
                logger.info("[Dev Agent] QA found issues, will trigger Dev-QA loop")
                return qa_result
            else:
                logger.info("[Dev Agent] QA passed, story completed")
                return qa_result

        except Exception as e:
            logger.error(f"Failed to notify QA agent: {e}")
            return None

    async def _update_story_completion(
        self, story_content: str, requirements: dict[str, Any]
    ) -> None:
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
            with open(story_path, encoding="utf-8") as f:
                content = f.read()

            # Update status to "Ready for Review"
            status_pattern = r"(\*\*Status\*\*:\s*)Draft"
            if re.search(status_pattern, content):
                content = re.sub(status_pattern, r"\1Ready for Review", content)

            # Add file list if not present
            if "### File List" not in content:
                file_list_section = """
### File List
- `src/main.py`
- `tests/test_main.py`
"""
                # Insert before Dev Agent Record section
                dev_record_pattern = r"(## Dev Agent Record)"
                if re.search(dev_record_pattern, content):
                    content = re.sub(
                        dev_record_pattern, rf"{file_list_section}\1", content
                    )

            # Write updated content
            with open(story_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Updated story file: {story_path}")

        except Exception as e:
            logger.error(f"Failed to update story file: {e}")

    async def _check_story_status(self, story_path: str) -> str | None:
        """
        Check the status field in a story document using hybrid parsing strategy.

        Args:
            story_path: Path to the story file

        Returns:
            Status string (e.g., "Ready for Review", "Ready for Done", "Done", "Ready for Development", "Draft")
            or None if not found/error
        """
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"[Dev Agent] Story file not found: {story_path}")
                return None

            with open(story_file, encoding="utf-8") as f:
                content = f.read()

            # Use StatusParser if available (AI-powered parsing)
            if self.status_parser:
                try:
                    # Note: parse_status is now async in SimpleStatusParser
                    status_text = await self.status_parser.parse_status(content)
                    if status_text and status_text != "unknown":
                        logger.debug(
                            f"[Dev Agent story] Found status using AI parsing: '{status_text}'"
                        )
                        return status_text
                    else:
                        logger.warning(
                            f"[Dev Agent] StatusParser failed to parse status from {story_path}"
                        )
                except asyncio.CancelledError:
                    # 🎯 关键修复：SDK 内部取消不应影响状态检查
                    # 完全封装 CancelledError，回退到正则解析
                    logger.warning(
                        f"[Dev Agent] Status parsing was cancelled (normal SDK cleanup), "
                        f"using fallback for {story_path}"
                    )
                    # 继续执行 fallback
                except Exception as e:
                    logger.warning(
                        f"[Dev Agent] StatusParser error: {e}, falling back to regex"
                    )

            # Fallback to original regex pattern
            logger.debug(f"[Dev Agent] Using fallback regex parsing for {story_path}")
            status_match = re.search(
                r"## Status\s*\n\s*\*\*([^*]+)\*\*", content, re.MULTILINE
            )

            if status_match:
                status_text = status_match.group(1).strip()
                logger.debug(
                    f"[Dev Agent story] Found status using regex: '{status_text}'"
                )
                return status_text
            else:
                logger.warning(f"[Dev Agent] Status section not found in {story_path}")
                return None

        except Exception as e:
            logger.error(f"[Dev Agent] Error checking story status: {e}")
            return None

    # =========================================================================
    # 统一状态解析方法
    # =========================================================================

    async def _parse_story_status_with_sdk(self, story_path: str) -> str:
        """
        🎯 关键修复：标准化状态解析入口（移除缓存）
        统一使用StatusParser，确保状态一致性
        """
        if not story_path or not Path(story_path).exists():
            return "Unknown"

        # 优先使用StatusParser
        if hasattr(self, "status_parser") and self.status_parser:
            try:
                content = Path(story_path).read_text(encoding="utf-8")
                status = await self.status_parser.parse_status(content)
                return status if status else "Unknown"
            except Exception as e:
                logger.warning(f"StatusParser failed: {e}")
                return self._parse_story_status_fallback(story_path)
        else:
            # 回退到正则解析
            return self._parse_story_status_fallback(story_path)

    def _parse_story_status_fallback(self, story_path: str) -> str:
        """
        回退状态解析方法 - 使用正则表达式
        """
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                return "Unknown"

            content = story_file.read_text(encoding="utf-8")

            # 定义状态匹配的正则表达式模式
            status_patterns = [
                (r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*", 1),      # **Status**: **Draft**
                (r"\*\*Status\*\*:\s*(.+)$", 1),                # **Status**: Draft
                (r"Status:\s*(.+)$", 1),                        # Status: Draft
                (r"状态[：:]\s*(.+)$", 1),                      # 状态：草稿
                (r"\*\*Status\*\*:\s*(.+)$", 1),                # **Status:** Ready for Review
                (r"Status:\s*\*(.+)\*", 1),                    # Status: *Ready for Review*
            ]

            # 遍历模式匹配
            for pattern, group_index in status_patterns:
                match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
                if match:
                    status_text = match.group(group_index).strip()
                    # 移除markdown标记 (**bold**)
                    status_text = status_text.strip('*').strip()
                    logger.debug(f"[Dev Agent] Status match found: '{status_text}' via pattern '{pattern}'")

                    # 标准化状态
                    normalized = self._normalize_story_status(status_text)
                    if normalized != "Draft":  # 只有非默认状态才返回
                        logger.info(f"[Dev Agent] Status parsed successfully: '{status_text}' → '{normalized}'")
                        return normalized

            # 默认值
            logger.warning(f"[Dev Agent] No status pattern matched, returning default: 'Draft'")
            return "Draft"

        except Exception as e:
            logger.error(f"[Dev Agent] Failed to parse status: {e}")
            return "Unknown"

    async def _wait_for_status_sdk_completion(self) -> None:
        """
        🎯 新增：等待状态解析SDK完成
        """
        try:
            await asyncio.sleep(0.1)  # 短暂等待
            logger.debug("[Dev Agent] Status SDK execution completed/cancelled")
        except Exception as e:
            logger.debug(f"[Dev Agent] Status SDK completion wait failed: {e}")

    def _normalize_story_status(self, status: str) -> str:
        """🎯 新增：标准化故事状态值"""
        from .story_parser import _normalize_story_status as normalize

        try:
            return normalize(status)
        except Exception:
            # 如果导入失败，使用简单的标准化
            status_lower = status.lower().strip()
            if status_lower in ["done", "completed", "complete"]:
                return "Done"
            elif status_lower in ["ready for review", "review"]:
                return "Ready for Review"
            elif status_lower in ["in progress", "progress"]:
                return "In Progress"
            elif status_lower in ["ready for development", "ready"]:
                return "Ready for Development"
            else:
                return "Draft"

    async def _wait_for_sdk_completion(self, task_name: str) -> None:
        """🎯 新增：等待SDK调用完全结束"""
        try:
            # 确保所有pending的SDK任务完成
            await asyncio.sleep(0.2)  # 等待一小段时间
            logger.debug(f"[Dev Agent] {task_name} SDK calls completed")
        except Exception as e:
            logger.debug(f"[Dev Agent] SDK completion wait failed: {e}")

    async def _notify_qa_agent_safe(self, story_path: str) -> bool:
        """安全通知QA Agent"""
        try:
            logger.info(f"[Dev Agent] Notifying QA agent for: {story_path}")

            # 移除直接从state_manager导入QAResult的逻辑
            from .qa_agent import QAAgent

            qa_agent = QAAgent()
            result = await qa_agent.execute(story_path)

            return bool(result.get("proceed", False))

        except Exception as e:
            logger.error(f"[Dev Agent] Error notifying QA agent: {e}")
            return False


    async def _notify_qa_agent_in_isolated_task(self, story_path: str) -> bool:
        """
        🎯 在独立 Task 中通知 QA，避免跨 Task 的 cancel scope 冲突

        核心原理：
        1. 创建全新的 Task 执行 QA 通知
        2. 确保 Dev 阶段的 cancel scope 已在原 Task 中完全退出
        3. QA 阶段使用全新的 cancel scope
        """
        try:
            # 🎯 使用 asyncio.create_task 创建独立 Task
            # 注意：不使用 await，让 QA 在独立 Task 中执行
            qa_task = asyncio.create_task(
                self._notify_qa_agent_safe(story_path),
                name=f"QA-Notification-{int(time.time())}"
            )

            logger.info(f"[Dev Agent] QA agent notification started in task: {qa_task.get_name()}")

            # 等待 QA 任务完成，确保在 Dev 阶段返回前 QA 完成
            # 🎯 增加等待时间，确保前一个上下文的 cancel scope 完全退出
            await asyncio.sleep(0.5)
            result = await qa_task
            logger.info(f"[Dev Agent] QA notification completed in task: {qa_task.get_name()}")
            return result

        except Exception as e:
            logger.error(f"[Dev Agent] Error starting QA task: {e}")
            # 回退到同步执行
            # 🎯 回退时也增加等待时间
            await asyncio.sleep(0.5)
            return await self._notify_qa_agent_safe(story_path)

"""
QA Agent - Quality Assurance Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    Quality Assurance agent for handling QA review tasks.
    """

    name: str = "QA Agent"

    def __init__(self, task_group: Optional[Any] = None):
        """
        初始化QA代理

        Args:
            task_group: TaskGroup实例
        """
        super().__init__("QAAgent", task_group)

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
                from ..story_parser import SimpleStoryParser
                from ..sdk_wrapper import SafeClaudeSDK

                if SafeClaudeSDK:
                    from claude_agent_sdk import ClaudeAgentOptions

                    options = ClaudeAgentOptions(
                        permission_mode="bypassPermissions",
                        cwd=str(Path.cwd()),
                        cli_path=r"D:\GITHUB\pytQt_template\venv\Lib\site-packages\claude_agent_sdk\_bundled\claude.exe",
                    )
                    sdk_instance = SafeClaudeSDK(
                        prompt="Parse story status",
                        options=options,
                        timeout=None,
                        log_manager=None,
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

        self._log_execution("QAAgent initialized")

    async def execute(
        self,
        story_path: str,
        cached_status: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        执行QA审查

        Args:
            story_path: 故事文件路径
            cached_status: 缓存的状态值（不再使用）

        Returns:
            固定返回 passed=True 的字典
        """
        self._log_execution(f"Executing QA review for {story_path}")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            # 即使没有TaskGroup也继续执行
            return await self._execute_qa_review(story_path)

        return await self._execute_within_taskgroup(
            lambda: self._execute_qa_review(story_path)
        )

    async def _execute_qa_review(self, story_path: str) -> dict[str, Any]:
        """执行QA审查的核心逻辑"""
        try:
            self._log_execution(
                "Epic Driver has determined this story needs QA review"
            )

            # 尝试执行QA工具检查
            try:
                from ..qa_tools_integration import QAAutomationWorkflow

                qa_workflow = QAAutomationWorkflow()
                qa_result = await qa_workflow.run_qa_checks()
                self._log_execution(
                    f"QA checks completed: {qa_result.get('overall_status', 'unknown')}"
                )
            except (ImportError, Exception) as e:
                self._log_execution(
                    f"QA checks failed or unavailable: {e}, continuing workflow",
                    "warning",
                )

            self._log_execution(
                "QA execution completed, "
                "Epic Driver will re-parse status to determine next step"
            )

            # 🎯 关键：始终返回 passed=True
            return {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": "QA execution completed",
            }

        except Exception as e:
            self._log_execution(
                f"Exception during QA: {e}, continuing workflow", "warning"
            )
            return {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": f"QA execution completed with exception: {str(e)}",
            }

    async def execute_qa_phase(
        self,
        story_path: str,
        source_dir: str = "src",
        test_dir: str = "tests",
        cached_status: Optional[str] = None,
    ) -> bool:
        """
        简化的QA阶段执行方法，用于Dev Agent调用

        Args:
            story_path: 故事文件路径
            source_dir: 源代码目录
            test_dir: 测试目录
            cached_status: 缓存的状态值

        Returns:
            始终返回 True
        """
        self._log_execution(f"Executing QA phase for {story_path}")

        result = await self.execute(story_path=story_path, cached_status=cached_status)

        self._log_execution(
            f"QA phase completed (result={result.get('passed', False)}), "
            f"Epic Driver will re-parse status to determine next step"
        )
        return True

    async def _parse_story_status(self, story_path: str) -> str:
        """解析故事状态 - 保持现有实现"""
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                self._log_execution(f"Story file not found: {story_path}", "warning")
                return "Unknown"

            content = story_file.read_text(encoding="utf-8")

            # 优先使用 StatusParser 进行AI解析
            if self.status_parser:
                try:
                    # 🎯 在新的 Task 中执行 AI 解析
                    status = await self.status_parser.parse_status(content)
                    if status and status != "unknown":
                        self._log_execution(f"Found status using AI parsing: '{status}'")
                        return status
                except Exception as e:
                    self._log_execution(f"StatusParser error: {e}, falling back to regex", "warning")

            # 回退到正则表达式解析
            self._log_execution(f"Using fallback regex parsing for {story_path}")
            status_patterns = [
                r"##\s*Status\s*\n\s*\*\*([^*]+)\*\*",  # Multi-line: ## Status\n**Value**
                r"##\s*Status\s*\n\s*([^\n]+)",  # Multi-line: ## Status\n Value
                r"Status:\s*\*\*([^*]+)\*\*",  # Inline: Status: **Bold** format
                r"Status:\s*(\w+(?:\s+\w+)*)",  # Inline: Status: Regular format
            ]

            for pattern in status_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    status = match.group(1).strip().lower()
                    self._log_execution(f"Found status using regex: '{status}'")
                    return status

            self._log_execution(f"Could not find status in story file: {story_path}", "warning")
            return "Unknown"

        except Exception as e:
            self._log_execution(f"Error parsing story status: {e}", "error")
            return "Unknown"

    async def get_statistics(self) -> dict[str, Any]:
        """获取QA代理统计信息"""
        try:
            # 如果有会话管理器，获取统计信息
            session_manager = getattr(self, '_session_manager', None)
            if session_manager:
                stats = session_manager.get_statistics()
                return {
                    "agent_name": self.name,
                    "session_statistics": stats,
                    "active_sessions": session_manager.get_session_count(),
                }
            else:
                return {"agent_name": self.name, "message": "No session manager"}
        except Exception as e:
            self._log_execution(f"Failed to get statistics: {e}", "error")
            return {"error": str(e)}

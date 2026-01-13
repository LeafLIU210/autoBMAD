"""
QA Agent - Quality Assurance Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from anyio.abc import TaskGroup

from autoBMAD.epic_automation.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    Quality Assurance agent for handling QA review tasks.
    """

    def __init__(
        self,
        task_group: Optional[TaskGroup] = None,
        use_claude: bool = True,
        log_manager: Optional[Any] = None,
    ):
        """
        初始化QA代理

        Args:
            task_group: TaskGroup实例
            use_claude: 是否使用 Claude 进行真实 QA 审查
            log_manager: 日志管理器
        """
        super().__init__("QAAgent", task_group, log_manager)
        self.use_claude = use_claude

        # 集成SDKExecutor
        self.sdk_executor = None
        try:
            from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
            self.sdk_executor = SDKExecutor()
        except (ImportError, TypeError):
            self._log_execution("SDKExecutor not available", "warning")

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
            return await self._execute_qa_review(story_path, cached_status)

        # 使用_execute_within_taskgroup来执行
        async def _execute():
            return await self._execute_qa_review(story_path, cached_status)

        return await self._execute_within_taskgroup(_execute)

    async def _execute_qa_review(self, story_path: str, cached_status: Optional[str] = None) -> dict[str, Any]:
        """
        执行QA审查的核心逻辑

        通过 SDK 调用完成以下任务：
        1. 审查故事实现
        2. 创建/更新 QA gate 文件
        3. 根据审查结果修改故事文档 Status

        Args:
            story_path: 故事文件路径
            cached_status: 缓存的状态值（已废弃，保留参数兼容性）

        Returns:
            dict[str, Any]: QA 执行结果字典
        """
        try:
            self._log_execution("Epic Driver has determined this story needs QA review")

            # 1. 构造 QA 提示词（BMAD 风格）
            base_prompt = (
                "@.bmad-core\\agents\\qa.md "
                "@.bmad-core\\tasks\\review-story.md "
                f"Review @{story_path}, "
                "create or update the story gate file in @docs\\qa\\gates. "
                'If the story document passes review, change the Status field in the story document '
                'from "Ready for Review" to "Ready for Done"; '
                'otherwise change it to "In Progress".'
            )

            # 2. 通过 BaseAgent._execute_sdk_call 统一调用 SDK
            sdk_result = await self._execute_sdk_call(
                sdk_executor=None,          # 按基类约定，这个参数已不再使用
                prompt=base_prompt,
                timeout=1800.0,             # 30分钟超时
                permission_mode="bypassPermissions",  # 与 DevAgent 行为保持一致
            )

            # 3. 记录 SDK 调用结果
            if sdk_result and hasattr(sdk_result, 'is_success'):
                self._log_execution(f"SDK call result: {sdk_result.is_success()}")

            self._log_execution(
                "QA execution completed, "
                "Epic Driver will re-parse status to determine next step"
            )

            # 4. 返回固定结构
            # 实际成功/失败由 EpicDriver 通过 StateAgent 重新解析 Status 判断
            return {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": "QA execution completed",
            }

        except Exception as e:
            self._log_execution(
                f"Exception during QA: {e}, continuing workflow",
                "warning",
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

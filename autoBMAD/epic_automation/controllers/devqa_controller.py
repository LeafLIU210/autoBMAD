"""
DevQa Controller - Dev-QA 流水线控制器
控制开发-测试-审查的循环流程
"""
from __future__ import annotations
import logging
from typing import Any

import anyio

from .base_controller import StateDrivenController
from ..agents.state_agent import StateAgent
from ..agents.dev_agent import DevAgent
from ..agents.qa_agent import QAAgent

logger = logging.getLogger(__name__)


class DevQaController(StateDrivenController):
    """Dev-QA 流水线控制器"""

    def __init__(
        self,
        task_group: anyio.TaskGroup,
        use_claude: bool = True,
        log_manager: Any = None
    ):
        """
        初始化 DevQa 控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            use_claude: 是否使用 Claude 进行真实开发
            log_manager: 日志管理器
        """
        super().__init__(task_group)
        self.state_agent = StateAgent()
        self.dev_agent = DevAgent(use_claude=use_claude, log_manager=log_manager)
        self.qa_agent = QAAgent()  # QAAgent不接受参数
        self.max_rounds = 3
        self._story_path = None
        self._log_execution("DevQaController initialized")

    async def execute(self, story_path: str) -> bool:
        """
        执行 Dev-QA 流水线

        Args:
            story_path: 故事文件路径

        Returns:
            bool: 执行是否成功
        """
        self._story_path = story_path
        self._log_execution(f"Starting Dev-QA pipeline for {story_path}")

        try:
            # 启动状态机循环
            result = await self.run_state_machine(
                initial_state="Start",
                max_rounds=self.max_rounds
            )

            if result:
                self._log_execution("Dev-QA pipeline completed successfully")
            else:
                self._log_execution("Dev-QA pipeline did not complete within max rounds", "warning")

            return result

        except Exception as e:
            self._log_execution(f"Dev-QA pipeline failed: {e}", "error")
            return False

    async def run_pipeline(self, story_path: str, max_rounds: int = 3) -> bool:
        """
        运行 Dev-QA 流水线（别名方法）

        Args:
            story_path: 故事文件路径
            max_rounds: 最大轮数

        Returns:
            bool: 执行是否成功
        """
        return await self.execute(story_path)

    async def _make_decision(self, current_state: str) -> str:
        """
        基于当前状态做出 Dev-QA 决策

        Args:
            current_state: 当前状态

        Returns:
            str: 下一个状态
        """
        try:
            if not self._story_path:
                self._log_execution("Story path not set", "error")
                return "Error"

            # 重新读取当前状态
            current_status = await self.state_agent.parse_status(self._story_path)

            if not current_status:
                self._log_execution("Failed to parse current status", "error")
                return "Failed"

            self._log_execution(f"Current status: {current_status}")

            # 状态决策逻辑
            if current_status in ["Done", "Ready for Done"]:
                self._log_execution("Story already completed")
                return current_status

            elif current_status in ["Draft", "Ready for Development", "Failed"]:
                # 需要开发
                self._log_execution("Development required")
                story_path = self._story_path
                await self._execute_within_taskgroup(
                    lambda: self.dev_agent.execute(story_path)
                )
                return "AfterDev"

            elif current_status == "In Progress":
                # 继续开发或进入 QA
                self._log_execution("Development in progress")
                story_path = self._story_path
                await self._execute_within_taskgroup(
                    lambda: self.dev_agent.execute(story_path)
                )
                return "AfterDev"

            elif current_status == "Ready for Review":
                # 需要 QA
                self._log_execution("QA required")
                story_path = self._story_path
                await self._execute_within_taskgroup(
                    lambda: self.qa_agent.execute(story_path)
                )
                return "AfterQA"

            else:
                self._log_execution(f"Unknown status: {current_status}", "warning")
                return current_status

        except Exception as e:
            self._log_execution(f"Decision error: {e}", "error")
            return "Error"

    def _is_termination_state(self, state: str) -> bool:
        """判断是否为 Dev-QA 的终止状态"""
        return state in ["Done", "Ready for Done", "Failed", "Error"]

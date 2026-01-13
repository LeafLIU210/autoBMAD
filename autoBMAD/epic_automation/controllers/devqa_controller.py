"""
DevQa Controller - Dev-QA 流水线控制器
控制开发-测试-审查的循环流程
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any

from anyio.abc import TaskGroup

from .base_controller import StateDrivenController
from ..agents.state_agent import StateAgent
from ..agents.dev_agent import DevAgent
from ..agents.qa_agent import QAAgent
from ..state_manager import StateManager

logger = logging.getLogger(__name__)


class DevQaController(StateDrivenController):
    """Dev-QA 流水线控制器"""

    def __init__(
        self,
        task_group: TaskGroup,
        use_claude: bool = True,
        log_manager: Any = None,
        state_manager: StateManager | None = None
    ):
        """
        初始化 DevQa 控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            use_claude: 是否使用 Claude 进行真实开发
            log_manager: 日志管理器
            state_manager: 状态管理器实例（可选）
        """
        super().__init__(task_group)
        self.state_agent = StateAgent(task_group=task_group)
        self.dev_agent = DevAgent(task_group=task_group, use_claude=use_claude, log_manager=log_manager)
        self.qa_agent = QAAgent(task_group=task_group, use_claude=use_claude, log_manager=log_manager)
        # 添加状态管理器（方案2要求）
        self.state_manager = state_manager or StateManager()
        self.max_rounds = 3
        self._story_path: str | None = None
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
            # 方案2：标记开始处理（写入数据库状态）
            await self._update_processing_status(
                story_id=story_path,
                processing_status='in_progress',
                context='Dev-QA cycle started'
            )

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
        # 保存原始max_rounds
        original_rounds = self.max_rounds
        self.max_rounds = max_rounds
        try:
            return await self.execute(story_path)
        finally:
            self.max_rounds = original_rounds

    async def _make_decision(self, current_state: str) -> str:
        """
        基于 StateAgent 解析的核心状态值做出 Dev-QA 决策
        
        循环模式：State → Dev/QA → State
        每次循环开始和结束都通过 StateAgent 获取最新核心状态

        Args:
            current_state: 上一次的状态（仅用于日志）

        Returns:
            str: 下一个状态
        """
        try:
            if not self._story_path:
                self._log_execution("Story path not set", "error")
                return "Error"

            # 🎯 关键：每次决策前，先通过 StateAgent 获取核心状态值
            self._log_execution("[State-Dev-QA Cycle] Querying StateAgent for current status")
            
            async def query_state():
                return await self.state_agent.execute(self._story_path)
            
            current_status = await self._execute_within_taskgroup(query_state)

            if not current_status:
                self._log_execution("StateAgent failed to parse status", "error")
                return "Error"

            self._log_execution(f"[State Result] Core status: {current_status}")

            # 🎯 状态决策逻辑：基于核心状态值，不依赖数据库
            if current_status in ["Done", "Ready for Done"]:
                self._log_execution(f"Story reached terminal state: {current_status}")
                return current_status

            elif current_status == "Failed":
                # 允许重新开发失败的故事
                self._log_execution("[Decision] Failed → Dev phase")
                story_path = self._story_path

                async def call_dev_agent():
                    return await self.dev_agent.execute(story_path)

                dev_result = await self._execute_within_taskgroup(call_dev_agent)

                # 方案2：Dev完成后更新处理状态
                await self._update_processing_status_after_dev(story_path, dev_result)

                # 🎯 Dev 完成后，再次查询状态
                self._log_execution("[Post-Dev] Querying StateAgent for updated status")
                return await self._make_decision("AfterDev")

            elif current_status in ["Draft", "Ready for Development"]:
                # 需要开发
                self._log_execution(f"[Decision] {current_status} → Dev phase")
                story_path = self._story_path

                async def call_dev_agent():
                    return await self.dev_agent.execute(story_path)

                dev_result = await self._execute_within_taskgroup(call_dev_agent)

                # 方案2：Dev完成后更新处理状态
                await self._update_processing_status_after_dev(story_path, dev_result)

                # 🎯 Dev 完成后，再次查询状态
                self._log_execution("[Post-Dev] Querying StateAgent for updated status")
                return await self._make_decision("AfterDev")

            elif current_status == "In Progress":
                # 继续开发
                self._log_execution("[Decision] In Progress → Continue Dev phase")
                story_path = self._story_path

                async def call_dev_agent():
                    return await self.dev_agent.execute(story_path)

                dev_result = await self._execute_within_taskgroup(call_dev_agent)

                # 方案2：Dev完成后更新处理状态
                await self._update_processing_status_after_dev(story_path, dev_result)

                # 🎯 Dev 完成后，再次查询状态
                self._log_execution("[Post-Dev] Querying StateAgent for updated status")
                return await self._make_decision("AfterDev")

            elif current_status == "Ready for Review":
                # 需要 QA
                self._log_execution("[Decision] Ready for Review → QA phase")
                story_path = self._story_path

                async def call_qa_agent():
                    return await self.qa_agent.execute(story_path)

                qa_result = await self._execute_within_taskgroup(call_qa_agent)

                # 方案2：QA完成后更新处理状态
                await self._update_processing_status_after_qa(story_path, qa_result)

                # 🎯 QA 完成后，再次查询状态
                self._log_execution("[Post-QA] Querying StateAgent for updated status")
                return await self._make_decision("AfterQA")

            else:
                self._log_execution(f"Unknown status: {current_status}", "warning")
                return current_status

        except Exception as e:
            self._log_execution(f"Decision error: {e}", "error")
            return "Error"

    def _is_termination_state(self, state: str) -> bool:
        """判断是否为 Dev-QA 的终止状态"""
        # Failed 状态允许重新开发，不视为终止状态
        return state in ["Done", "Ready for Done", "Error"]

    async def _update_processing_status(
        self,
        story_id: str,
        processing_status: str,
        context: str | None = None
    ) -> bool:
        """
        更新Story的处理状态（方案2实现）

        Args:
            story_id: Story标识
            processing_status: 处理状态值
            context: 上下文信息（用于日志）

        Returns:
            是否更新成功
        """
        try:
            timestamp = datetime.now()
            success = await self.state_manager.update_story_processing_status(
                story_id=story_id,
                processing_status=processing_status,
                timestamp=timestamp,
                metadata={'context': context} if context else None
            )

            if success:
                self._log_execution(
                    f"[StateTransition] Story {story_id}: "
                    f"processing_status = '{processing_status}' ({context or 'update'})"
                )
            else:
                self._log_execution(
                    f"[StateTransition] Failed to update processing_status for {story_id}",
                    "error"
                )

            return success

        except Exception as e:
            self._log_execution(
                f"[StateTransition] Error updating processing_status: {e}",
                "error"
            )
            return False

    async def _update_processing_status_after_dev(
        self,
        story_id: str,
        dev_result: bool
    ) -> None:
        """
        Dev阶段完成后更新处理状态（方案2实现）

        Args:
            story_id: Story标识
            dev_result: Dev执行结果
        """
        if dev_result:
            # Dev成功 → 进入评审阶段
            await self._update_processing_status(
                story_id=story_id,
                processing_status='review',
                context='Dev completed successfully'
            )
        else:
            # Dev失败 → 继续开发
            await self._update_processing_status(
                story_id=story_id,
                processing_status='in_progress',
                context='Dev failed, continuing development'
            )

    async def _update_processing_status_after_qa(
        self,
        story_id: str,
        qa_result: bool
    ) -> None:
        """
        QA阶段完成后更新处理状态（方案2实现）

        Args:
            story_id: Story标识
            qa_result: QA执行结果
        """
        if qa_result:
            # QA通过 → 完成
            await self._update_processing_status(
                story_id=story_id,
                processing_status='completed',
                context='QA passed, story completed'
            )
        else:
            # QA不通过 → 返工
            await self._update_processing_status(
                story_id=story_id,
                processing_status='in_progress',
                context='QA rejected, returning to development'
            )

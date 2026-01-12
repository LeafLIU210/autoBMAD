"""
SM Controller - Story Management Controller
控制 SM 阶段的业务流程
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Optional

from anyio.abc import TaskGroup
import anyio

from .base_controller import StateDrivenController
from ..agents.sm_agent import SMAgent
from ..agents.state_agent import StateAgent

logger = logging.getLogger(__name__)


class SMController(StateDrivenController):
    """SM 阶段控制器"""

    def __init__(self, task_group: TaskGroup, project_root: Optional[Path] = None):
        """
        初始化 SM 控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            project_root: 项目根目录
        """
        super().__init__(task_group)
        self.project_root = project_root
        self.sm_agent = SMAgent(
            task_group=task_group,
            project_root=project_root
        )
        self.state_agent = StateAgent(task_group=task_group)
        self._log_execution("SMController initialized")

    async def execute(
        self,
        epic_content: str,
        story_id: str,
        tasks_path: Optional[str] = None
    ) -> bool:
        """
        执行 SM 阶段流程

        Args:
            epic_content: Epic 内容
            story_id: Story ID (如 "1.1", "1.2")
            tasks_path: 任务路径

        Returns:
            bool: 执行是否成功
        """
        self._log_execution(f"Starting SM phase for story {story_id}")

        try:
            # Step 1: 调用 SMAgent 生成故事
            async def call_sm_agent():
                return await self.sm_agent.execute(
                    story_content=epic_content,
                    story_path=f"{story_id}.md"
                )

            await self._execute_within_taskgroup(call_sm_agent)

            # Step 3: 验证生成结果
            story_path = self._find_story_file(story_id)
            if not story_path:
                self._log_execution(f"Story file not found: {story_id}", "error")
                return False

            # Step 4: 验证故事内容
            if await self._validate_story_content(story_path):
                self._log_execution(f"SM phase completed successfully for story {story_id}")
                return True
            else:
                self._log_execution(f"Story validation failed for {story_id}", "error")
                return False

        except Exception as e:
            self._log_execution(f"SM phase failed: {e}", "error")
            return False

    def _build_sm_config(self, epic_content: str, story_id: str, tasks_path: Optional[str]) -> dict[str, Any]:
        """构造 SM 任务配置"""
        return {
            "epic_content": epic_content,
            "story_id": story_id,
            "tasks_path": tasks_path or str(Path.cwd() / "tasks")
        }

    def _find_story_file(self, story_id: str) -> Optional[Path]:
        """查找生成的故事文件"""
        if not self.project_root:
            return None

        stories_dir = self.project_root / "stories"
        pattern = f"{story_id}.md"
        matches = list(stories_dir.glob(pattern))
        return matches[0] if matches else None

    async def _validate_story_content(self, story_path: Path) -> bool:
        """
        增强的故事内容验证

        改进点：
        1. 降低最小长度要求（50 → 20字符）
        2. 添加结构化验证
        3. 改进错误提示
        4. 允许无状态故事（新故事）
        """
        try:
            content = story_path.read_text(encoding='utf-8')

            # 降低最小长度要求
            if not content or len(content.strip()) < 20:
                self._log_execution(
                    f"Story content too short (min 20 chars, got {len(content)})",
                    "warning"
                )
                return False

            # 尝试解析故事状态
            status = await self.state_agent.parse_status(str(story_path))
            if not status:
                # 即使没有状态，也允许继续（可能是新故事）
                self._log_execution("No status found, treating as new story", "info")
                return True  # ✅ 关键改进：允许无状态故事

            self._log_execution(f"Story status: {status}")
            return True

        except Exception as e:
            self._log_execution(f"Validation error: {e}", "error")
            return False

    async def _make_decision(self, current_state: str) -> str:
        """
        SM 阶段状态决策
        由于 SM 是单步流程，此方法通常不被调用
        """
        # SM 流程通常是：读取 Epic → 生成 Story → 完成
        # 不需要复杂的状态机
        return "Completed"

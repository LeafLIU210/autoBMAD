"""状态更新Agent

通过SDK调用更新故事文档状态，替代StateManager直接修改文档的方式。

遵循单一职责原则：StateManager只管理数据库状态，文档修改通过SDK完成。
"""

import logging
from pathlib import Path
from typing import Any, TypedDict, List, Tuple

from anyio.abc import TaskGroup
from .base_agent import BaseAgent
from .sdk_helper import execute_sdk_call

logger = logging.getLogger(__name__)


class BatchUpdateResults(TypedDict):
    """批量更新结果类型"""
    success_count: int
    error_count: int
    errors: List[str]


class StatusUpdateAgent(BaseAgent):
    """专门负责通过SDK更新故事状态的Agent

    职责：
    - 当需要更新故事状态时，通过SDK执行
    - 封装状态映射逻辑（数据库状态 → 文档状态）
    - 确保文档修改的统一性和可追溯性
    """

    # 数据库处理状态 → 文档核心状态映射
    DATABASE_TO_MARKDOWN_MAPPING = {
        # 故事状态
        "pending": "Draft",
        "in_progress": "In Progress",
        "review": "Ready for Review",
        "completed": "Done",
        "failed": "Failed",
        "cancelled": "Draft",

        # QA状态
        "qa_pass": "Done",
        "qa_concerns": "Ready for Review",
        "qa_fail": "Failed",
        "qa_waived": "Done",

        # 特殊状态
        "error": "Failed",
    }

    def __init__(self, task_group: TaskGroup | None = None, name: str = "StatusUpdateAgent"):
        """初始化状态更新Agent

        Args:
            task_group: 异步任务组，用于并发执行
            name: Agent名称
        """
        super().__init__(config_or_name=name, task_group=task_group)

    async def update_story_status_via_sdk(
        self,
        story_path: str,
        target_status: str
    ) -> bool:
        """
        通过SDK更新单个故事的状态

        Args:
            story_path: 故事文件路径
            target_status: 目标状态（核心状态值，如 "Done", "In Progress"）

        Returns:
            True if successful, False otherwise
        """
        try:
            story_file = Path(story_path)

            # 验证文件存在
            if not story_file.exists():
                logger.warning(f"Story file does not exist: {story_path}")
                return False

            # 构建SDK调用提示词
            prompt = f"""@{story_path}

Update the Status field in this story document to: **{target_status}**

Requirements:
- Locate the Status section (format: ## Status or ### Status)
- Replace the current status value with: **{target_status}**
- Do NOT modify any other content
- Preserve the document formatting
- Do not add or remove any other fields

Example format:
## Status
**Status**: {target_status}
"""

            # 使用统一的SDK调用接口
            result = await execute_sdk_call(
                prompt=prompt,
                agent_name=f"StatusUpdateAgent-{story_file.stem}",
                timeout=60.0,
                permission_mode="bypassPermissions"
            )

            if result.is_success():
                logger.info(
                    f"Successfully updated {story_path} status to {target_status}"
                )
                return True
            else:
                logger.error(
                    f"Failed to update {story_path} status: {result.errors}"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error updating story status for {story_path}: {str(e)}",
                exc_info=True
            )
            return False

    async def batch_update_statuses(
        self,
        status_mappings: List[Tuple[str, str]]
    ) -> BatchUpdateResults:
        """
        批量更新故事状态

        Args:
            status_mappings: [(story_path, target_status), ...]

        Returns:
            统计结果字典，包含：
            - success_count: 成功数量
            - error_count: 失败数量
            - errors: 错误列表
        """
        results: BatchUpdateResults = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }

        logger.info(f"Starting batch update of {len(status_mappings)} stories")

        # 并发执行更新任务
        if self.task_group:
            # 如果提供了task_group，使用它进行并发控制
            tasks: List[Any] = []
            for story_path, target_status in status_mappings:
                task = self.task_group.create_task(  # type: ignore[attr-defined, reportAttributeAccessIssue]
                    self._update_single_story(story_path, target_status, results)
                )
                tasks.append(task)

            # 等待所有任务完成
            for task in tasks:
                try:
                    await task
                except Exception as e:
                    logger.error(f"Task failed: {str(e)}")
                    results["error_count"] += 1
                    results["errors"].append(f"Task error: {str(e)}")
        else:
            # 否则顺序执行
            for story_path, target_status in status_mappings:
                await self._update_single_story(story_path, target_status, results)

        logger.info(
            f"Batch update completed: "
            f"{results['success_count']} succeeded, "
            f"{results['error_count']} failed"
        )

        return results

    async def _update_single_story(
        self,
        story_path: str,
        target_status: str,
        results: BatchUpdateResults
    ) -> None:
        """更新单个故事状态的内部方法

        Args:
            story_path: 故事文件路径
            target_status: 目标状态
            results: 结果统计字典（通过引用修改）
        """
        try:
            success = await self.update_story_status_via_sdk(
                story_path, target_status
            )

            if success:
                results["success_count"] += 1
            else:
                results["error_count"] += 1
                results["errors"].append(f"Failed to update {story_path}")

        except Exception as e:
            results["error_count"] += 1
            error_msg = f"Error updating {story_path}: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg, exc_info=True)

    async def sync_from_database(
        self,
        state_manager: Any,
        filter_statuses: List[str] | None = None,
        epic_id: str | None = None,
        story_ids: List[str] | None = None
    ) -> BatchUpdateResults:
        """
        从数据库同步状态到文档

        Args:
            state_manager: StateManager实例，用于获取数据库状态
            filter_statuses: 可选，要同步的状态列表，如果为None则同步所有状态
            epic_id: 可选，Epic标识，用于限制同步范围
            story_ids: 可选，Story ID 列表，用于限制同步范围

        Returns:
            同步结果统计字典

        Note:
            如果提供了 epic_id 和 story_ids，则只同步指定 Epic 的指定 Story，
            这显著提高了性能，避免同步全库记录。
        """
        try:
            # 根据是否提供了范围限制参数来决定查询策略
            if epic_id and story_ids:
                # 新功能：范围限制同步 - 只同步指定的 Story
                logger.info(
                    f"Using scoped sync for epic '{epic_id}' with {len(story_ids)} stories: {story_ids}"
                )
                stories = await state_manager.get_stories_by_ids(epic_id, story_ids)
            else:
                # 传统方式：全库同步（仅用于向后兼容）
                logger.warning(
                    "Using full database sync (no scope limit). "
                    "This may be slow for large databases. "
                    "Consider passing epic_id and story_ids for better performance."
                )
                stories = await state_manager.get_all_stories()

            # 构建状态映射列表
            status_mappings: List[Tuple[str, str]] = []
            for story in stories:
                story_path = story.get("story_path")
                db_status = story.get("status")

                if not story_path or not db_status:
                    continue

                # 如果指定了过滤列表，只处理匹配的状态
                if filter_statuses and db_status not in filter_statuses:
                    continue

                # 获取对应的markdown状态
                markdown_status = self.DATABASE_TO_MARKDOWN_MAPPING.get(
                    db_status, "Draft"
                )

                status_mappings.append((story_path, markdown_status))

            logger.info(
                f"Found {len(status_mappings)} stories to sync from database"
            )

            # 批量更新
            if status_mappings:
                return await self.batch_update_statuses(status_mappings)
            else:
                return BatchUpdateResults(
                    success_count=0,
                    error_count=0,
                    errors=[]
                )

        except Exception as e:
            logger.error(f"Failed to sync from database: {str(e)}", exc_info=True)
            return BatchUpdateResults(
                success_count=0,
                error_count=1,
                errors=[f"Database sync failed: {str(e)}"]
            )

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        执行Agent主逻辑

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            执行结果
        """
        # StatusUpdateAgent 主要通过具体方法调用执行
        # 不需要独立的execute逻辑
        return {"status": "ready"}

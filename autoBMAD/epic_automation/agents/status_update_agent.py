"""状态更新Agent

通过SDK调用更新故事文档状态，替代StateManager直接修改文档的方式。

遵循方案3：单一真源原则
- 只从数据库 processing_status 字段读取状态
- 通过映射表转换为核心状态
- 不使用其他数据源（历史记录、Markdown当前状态等）
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict, override

from anyio.abc import TaskGroup

from .base_agent import BaseAgent
from .sdk_helper import execute_sdk_call

logger = logging.getLogger(__name__)


class BatchUpdateResults(TypedDict):
    """批量更新结果类型"""
    success_count: int
    error_count: int
    errors: list[str]


class StatusUpdateAgent(BaseAgent):
    """专门负责通过SDK更新故事状态的Agent

    职责：
    - 当需要更新故事状态时，通过SDK执行
    - 封装状态映射逻辑（数据库processing_status → 核心状态 → Markdown状态）
    - 确保文档修改的统一性和可追溯性

    遵循方案3：单一真源原则
    - 只从数据库 processing_status 字段读取状态
    - 通过映射表转换为核心状态
    - 不使用其他数据源（历史记录、Markdown当前状态等）
    """

    @property
    @override
    def agent_type(self) -> str:
        return "status_update"

    # 状态映射表：处理状态（processing_status） → 核心状态
    PROCESSING_TO_CORE_STATUS = {
        'ready_for_development': 'Ready for Development',
        'in_progress': 'Ready for Development',
        'review': 'Ready for Review',
        'completed': 'Ready for Done',
        'cancelled': 'Ready for Development',  # 容错：支持重新开始
        'error': 'Ready for Development',      # 容错：支持重试
    }

    # 反向映射（用于验证和调试）
    CORE_TO_PROCESSING_STATUS = {
        'Ready for Development': 'in_progress',
        'Ready for Review': 'review',
        'Ready for Done': 'completed',
        'Done': 'completed',  # 别名支持
    }

    def __init__(self, task_group: TaskGroup | None = None, name: str = "StatusUpdateAgent"):
        """初始化状态更新Agent

        Args:
            task_group: 异步任务组，用于并发执行
            name: Agent名称
        """
        super().__init__(config_or_name=name, task_group=task_group)

    def _map_to_core_status(self, processing_status: str) -> str:
        """
        将处理状态映射为核心状态（方案3核心方法）

        Args:
            processing_status: 数据库中的处理状态值

        Returns:
            对应的核心状态文本

        Raises:
            ValueError: 处理状态值非法
        """
        if processing_status not in self.PROCESSING_TO_CORE_STATUS:
            logger.warning(f"Unknown processing_status '{processing_status}', defaulting to 'Ready for Development'")
            return 'Ready for Development'  # 默认值（容错）

        return self.PROCESSING_TO_CORE_STATUS[processing_status]

    def _generate_status_markdown(self, core_status: str) -> str:
        """
        根据核心状态生成 Markdown Status 段落

        Args:
            core_status: 核心状态（如 'Ready for Review'）

        Returns:
            完整的 Status 段落文本
        """
        return f"""## Status

**Status**: {core_status}

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    async def update_story_status_via_sdk(
        self,
        story_path: str,
        target_status: str
    ) -> bool:
        """
        通过SDK更新单个故事的状态

        Args:
            story_path: 故事文件路径
            target_status: 目标状态（核心状态值，如 "Ready for Done"）

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
            status_text = self._generate_status_markdown(target_status)
            prompt = f"""@{story_path}

Update the Status section in this story document to:

{status_text}

Requirements:
- Locate the Status section (format: ## Status or ### Status)
- Replace the entire Status section with the content above
- Do NOT modify any other content
- Preserve the document formatting
- Do not add or remove any other fields
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
        status_mappings: list[tuple[str, str]]
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
            tasks: list[Any] = []
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

        logger.info(f"Batch update completed: {results['success_count']} succeeded, {results['error_count']} failed")

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

    def validate_processing_statuses(
        self,
        _epic_id: str,
        _story_ids: list[str],
        records: list[dict[str, Any]]
    ) -> tuple[int, list[dict[str, Any]]]:
        """
        验证数据库中的处理状态值是否合法（方案3方法）

        Args:
            epic_id: Epic标识
            story_ids: Story ID列表
            records: 数据库记录列表

        Returns:
            (valid_count, invalid_records)
        """
        valid_statuses = set(self.PROCESSING_TO_CORE_STATUS.keys())
        invalid_records: list[dict[str, Any]] = []

        for record in records:
            status = record.get('status')  # processing_status存储在status字段中
            if status not in valid_statuses:
                invalid_records.append({
                    'story_id': record.get('story_path'),
                    'processing_status': status,
                    'file_path': record.get('story_path')
                })

        if invalid_records:
            logger.warning(
                f"Found {len(invalid_records)} stories with invalid processing_status"
            )
            for rec in invalid_records:
                logger.warning(f"  - {rec['story_id']}: {rec['processing_status']}")

        return len(records) - len(invalid_records), invalid_records

    async def sync_from_database(
        self,
        state_manager: Any,
        filter_statuses: list[str] | None = None,
        epic_id: str | None = None,
        story_ids: list[str] | None = None,
        prevent_downgrade: bool = True,
    ) -> BatchUpdateResults:
        """
        从数据库同步状态到文档（方案3实现 + 防降级保护）

        核心流程：
        1. 从数据库查询最新处理状态（processing_status）
        2. 通过映射表转换为核心状态
        3. 【新增】防降级检查
        4. 生成 Markdown Status 文本
        5. 调用 SDK 更新 Story 文档

        Args:
            state_manager: StateManager实例，用于获取数据库状态
            filter_statuses: 可选，要同步的状态列表，如果为None则同步所有状态
            epic_id: 可选，Epic标识，用于限制同步范围
            story_ids: 可选，Story ID 列表，用于限制同步范围
            prevent_downgrade: 【新增】如果为 True，禁止将终态降级为非终态

        Returns:
            同步结果统计字典

        Note:
            如果提供了 epic_id 和 story_ids，则只同步指定 Epic 的指定 Story，
            这显著提高了性能，避免同步全库记录。
            
            🆕 Fix for EPIC-012: Added downgrade prevention to protect terminal states
        """
        try:
            # Step 1: 查询数据库（方案1 保证范围限制）
            if epic_id and story_ids:
                # 范围限制同步 - 只同步指定的 Story
                logger.info(
                    f"Using scoped sync for epic '{epic_id}' with {len(story_ids)} stories: {story_ids}"
                )
                stories = await state_manager.get_stories_by_ids(epic_id, story_ids)
            else:
                # 传统方式：全库同步（仅用于向后兼容）
                logger.warning("Using full database sync (no scope limit). This may be slow for large databases. Consider passing epic_id and story_ids for better performance.")
                stories = await state_manager.get_all_stories()

            # Step 1.5: 验证数据合法性（可选）
            if epic_id and story_ids:
                valid_count, invalid = self.validate_processing_statuses(
                    epic_id, story_ids, stories
                )
                if invalid:
                    logger.warning(f"Proceeding with {valid_count} valid stories")

            # Step 2-5: 逐个处理
            status_mappings: list[tuple[str, str]] = []
            downgrade_prevented: list[tuple[str, str, str]] = []  # 【新增】记录被阻止的降级
            
            for record in stories:
                try:
                    story_path = record.get("story_path")
                    processing_status = record.get("status")  # processing_status存储在status字段中

                    if not story_path or not processing_status:
                        continue

                    # 如果指定了过滤列表，只处理匹配的状态
                    if filter_statuses and processing_status not in filter_statuses:
                        continue

                    # Step 2: 映射处理状态 → 核心状态
                    core_status = self._map_to_core_status(processing_status)

                    # Step 3: 【新增】防降级检查
                    if prevent_downgrade:
                        current_markdown_status = await self._get_current_markdown_status(story_path)
                        
                        if self._is_downgrade(current_markdown_status, core_status):
                            logger.warning(
                                f"[Downgrade Prevention] Blocked: {story_path} "
                                f"({current_markdown_status} -> {core_status})"
                            )
                            downgrade_prevented.append((story_path, current_markdown_status, core_status))
                            continue  # 跳过这个更新

                    # Step 4: 记录映射日志
                    logger.info(f"[StatusUpdate] {record.get('story_path')}: {processing_status} → {core_status}")

                    status_mappings.append((story_path, core_status))

                except Exception as e:
                    logger.error(
                        f"[StatusUpdate] Failed to process {record.get('story_path')}: {e}"
                    )
                    # 单条失败不中断整个同步流程
                    continue

            # 【新增】输出防降级统计
            if downgrade_prevented:
                logger.warning(f"[Downgrade Prevention] Total blocked: {len(downgrade_prevented)}")
                for story_path, current, new in downgrade_prevented:
                    logger.warning(f"  - {story_path}: {current} -> {new}")

            logger.info(
                f"Found {len(status_mappings)} stories to sync from database "
                f"({len(downgrade_prevented)} downgrade(s) prevented)"
            )

            # Step 5: 批量更新
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
    
    def _is_downgrade(self, current_status: str, new_status: str) -> bool:
        """
        检查是否为降级操作
        
        终态列表：Ready for Done, Done
        如果当前是终态，新状态不是终态，则为降级
        
        Args:
            current_status: 当前 Markdown 中的状态
            new_status: 数据库准备同步的新状态
            
        Returns:
            True 如果是降级操作，否则 False
        """
        terminal_states = ["Ready for Done", "Done"]
        return current_status in terminal_states and new_status not in terminal_states
    
    async def _get_current_markdown_status(self, story_path: str) -> str:
        """
        读取当前 Markdown 文档中的状态
        
        Args:
            story_path: 故事文件路径
            
        Returns:
            当前 Markdown 中的状态值，如果读取失败返回 "Unknown"
        """
        try:
            from pathlib import Path
            content = Path(story_path).read_text(encoding='utf-8')
            
            # 使用正则提取状态（与 epic_driver 中的解析逻辑一致）
            patterns = [
                r'\*\*Status\*\*:\s*\*\*([^*]+)\*\*',      # **Status**: **Value**
                r'\*\*Status\*\*:\s*([^\n*]+?)(?:\s*$|\s*\n)',  # **Status**: Value
                r'Status:\s*(.+?)(?:\s*$|\s*\n)',             # Status: Value
            ]
            
            # 只解析前20行
            lines = content.split('\n')[:20]
            status_section = '\n'.join(lines)
            
            for pattern in patterns:
                import re
                match = re.search(pattern, status_section, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip()
            
            return "Unknown"
        except Exception as e:
            logger.error(f"Failed to read current status from {story_path}: {e}")
            return "Unknown"

    @override
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

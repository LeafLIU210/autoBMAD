"""
State Agent - 状态解析和管理 Agent
增强后支持TaskGroup管理
"""
from __future__ import annotations
import logging
from anyio.abc import TaskGroup
import re
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


# =============================================================================
# 状态常量定义
# =============================================================================

# 核心状态值：用于文档和人类可读
CORE_STATUS_DRAFT = "Draft"
CORE_STATUS_READY_FOR_DEVELOPMENT = "Ready for Development"
CORE_STATUS_IN_PROGRESS = "In Progress"
CORE_STATUS_READY_FOR_REVIEW = "Ready for Review"
CORE_STATUS_READY_FOR_DONE = "Ready for Done"
CORE_STATUS_DONE = "Done"
CORE_STATUS_FAILED = "Failed"

# 核心状态值集合
CORE_STATUS_VALUES = {
    CORE_STATUS_DRAFT,
    CORE_STATUS_READY_FOR_DEVELOPMENT,
    CORE_STATUS_IN_PROGRESS,
    CORE_STATUS_READY_FOR_REVIEW,
    CORE_STATUS_READY_FOR_DONE,
    CORE_STATUS_DONE,
    CORE_STATUS_FAILED,
}


class ProcessingStatus(Enum):
    """统一的处理状态值系统"""

    # === 故事处理状态 ===
    PENDING = "pending"           # 故事未开始/草稿
    IN_PROGRESS = "in_progress"   # 故事进行中
    REVIEW = "review"            # 故事审查中
    COMPLETED = "completed"       # 故事已完成
    FAILED = "failed"           # 故事失败
    CANCELLED = "cancelled"     # 故事取消

    # === QA 相关处理状态 ===
    QA_PASS = "qa_pass"          # QA 验证通过
    QA_CONCERNS = "qa_concerns"  # QA 发现非关键问题
    QA_FAIL = "qa_fail"         # QA 发现关键问题
    QA_WAIVED = "qa_waived"     # QA 豁免

    # === 特殊状态 ===
    ERROR = "error"            # 系统错误
    UNKNOWN = "unknown"        # 未知状态


# 核心状态值 → 处理状态值映射（单向）
CORE_TO_PROCESSING_MAPPING = {
    CORE_STATUS_DRAFT: "pending",
    CORE_STATUS_READY_FOR_DEVELOPMENT: "pending",
    CORE_STATUS_IN_PROGRESS: "in_progress",
    CORE_STATUS_READY_FOR_REVIEW: "review",
    CORE_STATUS_READY_FOR_DONE: "completed",
    CORE_STATUS_DONE: "completed",
    CORE_STATUS_FAILED: "failed",
}

# 处理状态值 → 核心状态值（用于 Markdown 显示和自动恢复）
PROCESSING_TO_CORE_MAPPING = {
    "pending": CORE_STATUS_DRAFT,
    "in_progress": CORE_STATUS_IN_PROGRESS,
    "review": CORE_STATUS_READY_FOR_REVIEW,
    "completed": CORE_STATUS_DONE,
    "failed": CORE_STATUS_FAILED,
    "cancelled": CORE_STATUS_READY_FOR_DEVELOPMENT,  # ✅ 改为可继续开发
    "error": CORE_STATUS_READY_FOR_DEVELOPMENT,      # ✅ 改为可继续开发
}


def core_status_to_processing(core_status: str) -> str:
    """
    核心状态值 → 处理状态值转换（单向）

    Args:
        core_status: 核心状态值

    Returns:
        对应的处理状态值
    """
    return CORE_TO_PROCESSING_MAPPING.get(core_status, "unknown")


def processing_status_to_core(processing_status: str) -> str:
    """
    处理状态值 → 核心状态值（反向映射）

    用于将处理状态（如 "cancelled"、"error"）转换为核心状态，
    以便在 Markdown 文件中显示和驱动 Dev-QA 循环。

    Args:
        processing_status: 处理状态值

    Returns:
        对应的核心状态值
    """
    return PROCESSING_TO_CORE_MAPPING.get(processing_status, CORE_STATUS_DRAFT)


@dataclass
class StoryData:
    """故事文档解析结果"""

    title: str = ""
    status: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    subtasks: list[str] = field(default_factory=list)
    dev_notes: str = ""
    testing: str = ""
    raw_content: str = ""


class SimpleStoryParser:
    """
    统一故事/Epic解析器 - AI优先，正则回退

    根据奥卡姆剃刀原则，本类提供统一的Markdown解析入口：
    - parse_status(): 解析状态字段（保持兼容）
    - parse_story(): 解析完整故事文档
    - parse_epic(): 解析Epic文档，提取story IDs

    解析策略：AI优先，正则回退
    """

    def __init__(self, sdk_wrapper: Optional[Any] = None):
        """
        初始化统一解析器

        Args:
            sdk_wrapper: SDK实例，用于AI智能解析
        """
        self.sdk_wrapper = sdk_wrapper

    async def parse_status(self, content: str) -> str:
        """
        使用Claude SDK AI智能解析故事状态 - 增强版本

        增强点:
        1. 添加内容摘要日志
        2. 改进错误处理
        3. 记录解析过程

        Args:
            content: 故事文档内容

        Returns:
            标准状态字符串，如果解析失败返回 "unknown"
        """
        # 记录开始解析
        content_preview = content[:100].replace('\n', ' ')
        logger.info(f"Starting status parsing for: '{content_preview}...'")

        # 如果没有提供SDK包装器，使用正则表达式回退
        if not self.sdk_wrapper:
            return self._parse_status_with_regex(content)

        # 尝试使用AI解析
        try:
            # 这里应该调用Claude SDK进行AI解析
            # 目前使用正则表达式作为回退
            return await self._parse_status_with_ai(content)
        except Exception as e:
            logger.warning(f"AI parsing failed, falling back to regex: {e}")
            return self._parse_status_with_regex(content)

    def _parse_status_with_regex(self, content: str) -> str:
        """
        使用正则表达式解析状态 - 增强版本

        增强点:
        1. 更强的正则表达式匹配
        2. 更好的日志记录
        3. 支持多种状态格式

        Args:
            content: 故事文档内容

        Returns:
            标准状态字符串
        """
        # 改进的正则表达式，支持多种格式
        status_patterns = {
            CORE_STATUS_DRAFT: [
                r'(?i)status\s*:\s*draft\b',
                r'(?i)\*\*status\*\*\s*:\s*draft\b',
                r'\bdraft\b',
            ],
            CORE_STATUS_READY_FOR_DEVELOPMENT: [
                r'(?i)status\s*:\s*ready\s+for\s+development\b',
                r'(?i)\*\*status\*\*\s*:\s*ready\s+for\s+development\b',
                r'\bready\s+for\s+development\b',
            ],
            CORE_STATUS_IN_PROGRESS: [
                r'(?i)status\s*:\s*(in\s+progress|active)\b',
                r'(?i)\*\*status\*\*\s*:\s*(in\s+progress|active)\b',
                r'\bin\s+progress\b',
                r'\bactive\b',
            ],
            CORE_STATUS_READY_FOR_REVIEW: [
                r'(?i)status\s*:\s*ready\s+for\s+review\b',
                r'(?i)\*\*status\*\*\s*:\s*ready\s+for\s+review\b',
                r'\bready\s+for\s+review\b',
            ],
            CORE_STATUS_READY_FOR_DONE: [
                r'(?i)status\s*:\s*ready\s+for\s+done\b',
                r'(?i)\*\*status\*\*\s*:\s*ready\s+for\s+done\b',
                r'\bready\s+for\s+done\b',
            ],
            CORE_STATUS_DONE: [
                r'(?i)status\s*:\s*done\b',
                r'(?i)\*\*status\*\*\s*:\s*done\b',
                r'\bdone\b',
                r'\bcompleted\b',
            ],
            CORE_STATUS_FAILED: [
                r'(?i)status\s*:\s*failed\b',
                r'(?i)\*\*status\*\*\s*:\s*failed\b',
                r'\bfailed\b',
                r'\berror\b',
            ],
        }

        # 尝试多个模式
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    logger.debug(f"Status matched with regex: {status} (pattern: {pattern})")
                    return status

        # 没有匹配时返回默认值
        logger.debug("No status pattern matched, returning default: Draft")
        return CORE_STATUS_DRAFT

    async def _parse_status_with_ai(self, content: str) -> str:
        """
        使用AI解析状态 - 占位符

        Args:
            content: 故事文档内容

        Returns:
            标准状态字符串
        """
        # TODO: 实现AI解析逻辑
        # 目前使用正则表达式作为占位符
        return self._parse_status_with_regex(content)


class StateAgent(BaseAgent):
    """状态解析和管理 Agent"""

    def __init__(self, task_group: Optional[TaskGroup] = None):
        """
        初始化状态 Agent

        Args:
            task_group: TaskGroup实例
        """
        super().__init__("StateAgent", task_group)
        self.status_parser = SimpleStoryParser()
        self._log_execution("StateAgent initialized")

    async def parse_status(self, story_path: str) -> Optional[str]:
        """
        解析故事文件的状态

        Args:
            story_path: 故事文件路径

        Returns:
            Optional[str]: 解析出的核心状态值，失败返回 None
        """
        try:
            if isinstance(story_path, Path):
                content = story_path.read_text(encoding='utf-8')
            else:
                # story_path是字符串路径，需读取文件内容
                with open(story_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            status = await self.status_parser.parse_status(content)
            if status:
                self.logger.debug(f"Parsed status: {status}")
                return status
            else:
                self.logger.warning("Status parser returned None")
                return None

        except Exception as e:
            self.logger.error(f"Failed to parse status: {e}")
            return None

    async def get_processing_status(self, story_path: str) -> Optional[str]:
        """
        获取处理状态值（数据库存储格式）

        Args:
            story_path: 故事文件路径

        Returns:
            Optional[str]: 处理状态值，失败返回 None
        """
        core_status = await self.parse_status(story_path)
        if core_status:
            return core_status_to_processing(core_status)
        return None

    async def update_story_status(self, story_path: str, status: str) -> bool:
        """
        更新故事状态（如果需要）

        Args:
            story_path: 故事文件路径
            status: 新的状态值

        Returns:
            bool: 更新是否成功
        """
        # StateAgent 主要用于解析，实际的状态更新由其他组件处理
        # 这里保留接口，便于扩展
        self.logger.info(f"Status update requested: {story_path} -> {status}")
        return True

    async def execute(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """
        执行状态解析

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Optional[str]: 解析出的状态值
        """
        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            # 即使没有TaskGroup也继续执行
            if len(args) > 0:
                return await self.parse_status(args[0])
            return None

        async def _task_coro() -> Optional[str]:
            """TaskGroup内的协程函数"""
            if len(args) > 0:
                return await self.parse_status(args[0])
            return None

        return await self._execute_within_taskgroup(_task_coro)

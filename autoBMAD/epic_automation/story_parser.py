"""
统一故事/Epic解析器 - 基于奥卡姆剃刀原则

根据奥卡姆剃刀原则，本模块实现统一的AI智能解析策略，
替代分散在 dev_agent.py, sm_agent.py, epic_driver.py 中的正则表达式。

设计原则：
- 统一入口：所有Markdown解析集中在此模块
- AI优先：使用Claude SDK进行语义理解
- 正则回退：AI失败时使用正则表达式
- 向后兼容：保留原有StatusParser接口
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional

# Import SafeClaudeSDK with proper type checking to avoid circular imports
if TYPE_CHECKING:
    from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

logger = logging.getLogger(__name__)


# =============================================================================
# 数据结构定义
# =============================================================================


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


@dataclass
class EpicData:
    """Epic文档解析结果"""

    title: str = ""
    story_ids: list[str] = field(default_factory=list)
    raw_content: str = ""


# =============================================================================
# 标准状态值常量
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
    CORE_STATUS_READY_FOR_DONE: "review",
    CORE_STATUS_DONE: "completed",
    CORE_STATUS_FAILED: "failed",
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


def is_core_status_valid(core_status: str) -> bool:
    """
    检查核心状态值是否有效

    Args:
        core_status: 状态值字符串

    Returns:
        True 如果状态值有效，False 否则
    """
    return core_status in CORE_STATUS_VALUES


# =============================================================================
# AI解析提示词模板
# =============================================================================

# 状态解析提示词（保留原有）
STATUS_PROMPT_TEMPLATE = """
你是一个专业的故事状态解析器。请从以下故事文档中提取标准状态值。

标准状态选项：
- Draft (草稿)
- Ready for Development (准备开发)
- In Progress (进行中)
- Ready for Review (准备审查)
- Ready for Done (准备完成)
- Done (已完成)
- Failed (失败)

分析要求：
1. 仔细阅读整个文档内容
2. 关注 Status 字段或相关描述
3. 根据上下文判断当前真实状态
4. 只返回标准状态值，不要解释

故事文档内容：
{content}

只返回状态值，例如：Ready for Review
"""

# 向后兼容别名
PROMPT_TEMPLATE = STATUS_PROMPT_TEMPLATE

# 故事解析提示词
STORY_PARSING_PROMPT = """
你是Markdown故事文档解析器。从以下内容提取结构化信息。

需要提取的字段：
- title: 故事标题（从第一个#标题提取）
- status: 状态值（从Status字段提取，如 Draft, Ready for Development, In Progress, Ready for Review, Ready for Done, Done, Failed）
- acceptance_criteria: 验收标准列表（数组，从 ## Acceptance Criteria 部分提取）
- tasks: 任务列表（数组，从 ## Tasks 部分提取未完成的任务）
- subtasks: 已完成子任务（数组，提取已勾选的checkbox项）
- dev_notes: 开发笔记内容（从 ## Dev Notes 部分提取）
- testing: 测试信息（从 ## Testing 部分提取）

故事文档内容：
{content}

请以JSON格式返回，示例：
{{"title": "故事标题", "status": "Draft", "acceptance_criteria": ["AC1", "AC2"], "tasks": ["Task1"], "subtasks": [], "dev_notes": "", "testing": ""}}
"""

# Epic解析提示词
EPIC_PARSING_PROMPT = """
你是Markdown Epic文档解析器。从以下内容提取故事ID列表。

提取规则：
- 从 "### Story X.Y: Title" 格式提取 X.Y
- 从 "**Story ID**: X.Y" 格式提取 X.Y
- 返回所有唯一的故事ID，保持原始格式（如 "001.1" 或 "1.1"）

Epic文档内容：
{content}

请以JSON格式返回，示例：
{{"title": "Epic标题", "story_ids": ["001.1", "001.2", "001.3"]}}
"""


# =============================================================================
# 解析器类
# =============================================================================


class SimpleStoryParser:
    """
    统一故事/Epic解析器 - AI优先，正则回退

    根据奥卡姆剃刀原则，本类提供统一的Markdown解析入口：
    - parse_status(): 解析状态字段（保持兼容）
    - parse_story(): 解析完整故事文档
    - parse_epic(): 解析Epic文档，提取story IDs

    解析策略：AI优先，正则回退
    """

    def __init__(self, sdk_wrapper: Optional["SafeClaudeSDK"] = None):
        """
        初始化统一解析器

        Args:
            sdk_wrapper: SafeClaudeSDK实例，用于AI智能解析
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

        # 如果没有提供SDK包装器，无法执行AI解析
        if not self.sdk_wrapper:
            logger.warning(
                "SimpleStatusParser: No SDK wrapper provided, cannot perform AI parsing. "
                "StatusParser将回退到正则表达式解析。SDK包装器状态: None. "
                "这可能是由于SDK初始化失败或参数不正确导致的。"
            )
            # 回退到正则解析
            return self._regex_fallback_parse_status(content)

        try:
            # 构建AI提示词
            prompt = PROMPT_TEMPLATE.format(
                content=content[:1000]
            )

            logger.debug(f"AI prompt length: {len(prompt)} characters")

            # 直接使用提供的sdk_wrapper
            sdk = self.sdk_wrapper

            # 更新提示词（如果SDK支持动态更新）
            if hasattr(sdk, "prompt"):
                sdk.prompt = prompt

            # 执行查询
            success = await sdk.execute()

            if success:
                # 从message_tracker获取结果，添加安全检查
                if not hasattr(sdk, "message_tracker"):
                    logger.warning(
                        "SimpleStatusParser: SDK does not have message_tracker attribute"
                    )
                    return self._regex_fallback_parse_status(content)

                latest_message = sdk.message_tracker.latest_message
                if latest_message:
                    # 清理AI响应，提取状态值
                    extracted_status = self._extract_status_from_response(latest_message)

                    logger.info(
                        f"Status parsing completed: '{extracted_status}' "
                        f"(raw: '{latest_message[:50]}...')"
                    )

                    return extracted_status

            logger.warning("SimpleStatusParser: AI parsing returned no result")
            return self._regex_fallback_parse_status(content)

        except TimeoutError:
            logger.error(
                f"SimpleStatusParser: AI parsing timed out after 30 seconds "
                f"for content '{content_preview}...'"
            )
            return self._regex_fallback_parse_status(content)
        except Exception as e:
            logger.error(
                f"SimpleStatusParser: AI parsing failed for content "
                f"'{content_preview}...': {e}",
                exc_info=True
            )
            return self._regex_fallback_parse_status(content)

    def _regex_fallback_parse_status(self, content: str) -> str:
        """
        正则表达式回退解析

        当AI解析失败或不可用时，使用传统的正则表达式方法

        Args:
            content: 故事文档内容

        Returns:
            标准状态字符串
        """
        logger.info("Using regex fallback for status parsing")

        # 定义状态匹配的正则表达式模式
        status_patterns = [
            (r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*", 1),      # **Status**: **Draft**
            (r"\*\*Status\*\*:\s*(.+)$", 1),                # **Status**: Draft
            (r"Status:\s*(.+)$", 1),                        # Status: Draft
            (r"状态[：:]\s*(.+)$", 1),                      # 状态：草稿
        ]

        # 遍历模式匹配
        for pattern, group_index in status_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                status_text = match.group(group_index).strip()
                logger.debug(f"Regex match found: '{status_text}' via pattern '{pattern}'")

                # 使用 _normalize_story_status 标准化
                try:
                    normalized = _normalize_story_status(status_text)

                    if normalized in CORE_STATUS_VALUES:
                        logger.info(
                            f"Regex fallback success: '{status_text}' → '{normalized}'"
                        )
                        return normalized
                except Exception as e:
                    logger.warning(f"Regex fallback normalization failed: {e}")

        # 默认值
        logger.info("Regex fallback returned default: 'Draft'")
        return "Draft"

    def _clean_response_string(self, response: str) -> str:
        """
        深度清理SDK响应中的各种前缀和标记

        Args:
            response: SDK原始响应字符串

        Returns:
            清理后的字符串，包含核心状态信息

        示例:
            "[SUCCESS] Ready for Review" → "Ready for Review"
            "Success: Ready for Review" → "Ready for Review"
            "Status: **Ready for Review**" → "Ready for Review"
        """
        if not response:
            return ""

        cleaned = response.strip()

        # 步骤1: 处理多层级冒号
        # 输入: "Status: Analysis Result: Ready for Review"
        # 输出: "Ready for Review"
        while ":" in cleaned:
            parts = cleaned.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                # 检查后半部分是否包含有效内容
                second_part = parts[1].strip()
                if len(second_part) > 2:  # 至少3个字符（避免": x"这类）
                    cleaned = second_part
                else:
                    break
            else:
                break

        # 步骤2: 移除方括号标记
        # [SUCCESS], [ERROR], [Thinking] 等
        import re
        cleaned = re.sub(r'^\[[^\]]+\]\s*', '', cleaned)

        # 步骤3: 移除冒号前缀
        # Success:, Error:, Result: 等
        cleaned = re.sub(r'^\w+:\s*', '', cleaned)

        # 步骤4: 移除其他标记
        cleaned = cleaned.replace("[Thinking]", "")
        cleaned = cleaned.replace("[Tool result]", "")
        cleaned = cleaned.replace("**", "")  # 粗体
        cleaned = cleaned.replace("*", "")   # 斜体
        cleaned = cleaned.replace("`", "")   # 代码标记

        # 步骤5: 最终清理
        cleaned = cleaned.strip()

        # 记录清理过程（用于调试）
        logger.debug(
            f"Response cleaning: '{response[:50]}...' → '{cleaned}'"
        )

        return cleaned

    def _extract_status_from_response(self, response: str) -> str:
        """
        从AI响应中提取状态值 - 重构版本

        重构要点:
        1. 利用成熟的 _normalize_story_status 逻辑
        2. 确保只返回7种标准状态之一
        3. 增强错误处理和日志记录

        Args:
            response: AI响应字符串

        Returns:
            标准状态字符串 (7种之一)，或 "unknown" 如果解析失败
        """
        # 步骤1: 输入验证
        if not response:
            logger.warning("SimpleStatusParser: Received empty response from AI")
            return "unknown"

        # 步骤2: 深度清理响应
        cleaned = self._clean_response_string(response)

        # 步骤3: 验证清理结果
        if not cleaned:
            logger.warning(
                f"SimpleStatusParser: Response became empty after cleaning: '{response[:50]}...'"
            )
            return "unknown"

        # 步骤4: 委托给 _normalize_story_status 进行标准化
        try:
            # 执行标准化
            normalized = _normalize_story_status(cleaned)

            # 步骤5: 验证结果
            if normalized in CORE_STATUS_VALUES:
                logger.debug(
                    f"Status extraction: '{response[:50]}...' → '{cleaned}' → '{normalized}'"
                )
                return normalized
            else:
                logger.warning(
                    f"SimpleStatusParser: Normalization returned invalid status '{normalized}' "
                    f"from input '{response[:50]}...'"
                )
                return "unknown"

        except ImportError as e:
            logger.error(
                f"SimpleStatusParser: Cannot import _normalize_story_status: {e}"
            )
            # 回退到内置的简单匹配
            return self._simple_fallback_match(cleaned)
        except Exception as e:
            logger.error(
                f"SimpleStatusParser: Unexpected error during normalization: {e}",
                exc_info=True
            )
            return "unknown"

    def _simple_fallback_match(self, cleaned: str) -> str:
        """
        简单的状态匹配回退方案

        当无法使用 _normalize_story_status 时，使用内置的简单匹配逻辑
        仅支持基本的关键词匹配，不处理复杂变体

        Args:
            cleaned: 清理后的响应字符串

        Returns:
            标准状态字符串或 "unknown"
        """
        cleaned_lower = cleaned.lower().strip()

        # 定义基本关键词匹配
        status_patterns = {
            "Draft": ["draft", "草稿"],
            "Ready for Development": ["ready for development", "development", "准备开发"],
            "In Progress": ["in progress", "progress", "进行", "进行中"],
            "Ready for Review": ["ready for review", "review", "审查", "准备审查"],
            "Ready for Done": ["ready for done", "done", "完成", "准备完成"],
            "Done": ["done", "completed", "complete", "已完成"],
            "Failed": ["failed", "fail", "failure", "失败"]
        }

        # 遍历匹配
        for status, keywords in status_patterns.items():
            for keyword in keywords:
                if keyword in cleaned_lower:
                    logger.debug(
                        f"Fallback match: '{cleaned}' → '{status}' (via '{keyword}')"
                    )
                    return status

        # 无匹配
        logger.warning(
            f"SimpleStatusParser: No fallback match for status: '{cleaned}'"
        )
        return "unknown"

    # =========================================================================
    # 故事解析方法
    # =========================================================================

    async def parse_story(self, content: str) -> StoryData:
        """
        解析完整故事文档

        策略：AI优先，正则回退

        Args:
            content: 故事文档内容

        Returns:
            StoryData 数据结构
        """
        if self.sdk_wrapper:
            try:
                result = await self._ai_parse_story(content)
                if result.title or result.status or result.acceptance_criteria:
                    return result
            except Exception as e:
                logger.warning(f"AI story parsing failed, falling back to regex: {e}")

        return self._regex_parse_story(content)

    async def _ai_parse_story(self, content: str) -> StoryData:
        """使用AI解析故事文档"""
        if not self.sdk_wrapper:
            return StoryData(raw_content=content)

        prompt = STORY_PARSING_PROMPT.format(content=content[:3000])

        sdk = self.sdk_wrapper
        if hasattr(sdk, "prompt"):
            sdk.prompt = prompt

        success = await sdk.execute()

        if success and hasattr(sdk, "message_tracker"):
            latest_message = sdk.message_tracker.latest_message
            if latest_message:
                return self._parse_story_json(latest_message, content)

        return StoryData(raw_content=content)

    def _parse_story_json(self, response: str, original_content: str) -> StoryData:
        """从AI的JSON响应中解析StoryData"""
        try:
            # 清理响应，提取JSON
            cleaned = response.strip()
            # 尝试找到JSON块
            if "```json" in cleaned:
                start = cleaned.find("```json") + 7
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()
            elif "```" in cleaned:
                start = cleaned.find("```") + 3
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()

            # 尝试解析JSON
            data = json.loads(cleaned)

            return StoryData(
                title=data.get("title", ""),
                status=data.get("status", ""),
                acceptance_criteria=data.get("acceptance_criteria", []),
                tasks=data.get("tasks", []),
                subtasks=data.get("subtasks", []),
                dev_notes=data.get("dev_notes", ""),
                testing=data.get("testing", ""),
                raw_content=original_content,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            return StoryData(raw_content=original_content)

    def _regex_parse_story(self, content: str) -> StoryData:
        """使用正则表达式解析故事文档（回退方案）"""
        result = StoryData(raw_content=content)

        # 提取标题
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            result.title = title_match.group(1).strip()

        # 提取状态
        status_patterns = [
            r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*",
            r"\*\*Status\*\*:\s*(.+)$",
            r"Status:\s*(.+)$",
        ]
        for pattern in status_patterns:
            status_match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if status_match:
                result.status = status_match.group(1).strip()
                break

        # 提取验收标准
        ac_section = re.search(
            r"## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if ac_section:
            ac_lines = ac_section.group(1).strip().split("\n")
            for line in ac_lines:
                line = line.strip()
                if line and (re.match(r"^\d+\.", line) or line.startswith("- ")):
                    result.acceptance_criteria.append(line)

        # 提取任务
        tasks_section = re.search(
            r"## Tasks?(?:\s*/\s*Subtasks?)?\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if tasks_section:
            task_lines = tasks_section.group(1).strip().split("\n")
            for line in task_lines:
                line = line.strip()
                if line.startswith("- [ ]"):
                    result.tasks.append(line)
                elif line.startswith("- [x]") or line.startswith("- [X]"):
                    result.subtasks.append(line)

        # 提取开发笔记
        dev_notes_section = re.search(
            r"## Dev Notes?\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if dev_notes_section:
            result.dev_notes = dev_notes_section.group(1).strip()

        # 提取测试信息
        testing_section = re.search(
            r"## Testing\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if testing_section:
            result.testing = testing_section.group(1).strip()

        return result

    # =========================================================================
    # Epic解析方法
    # =========================================================================

    async def parse_epic(self, content: str) -> EpicData:
        """
        解析Epic文档，提取story IDs

        策略：AI优先，正则回退

        Args:
            content: Epic文档内容

        Returns:
            EpicData 数据结构
        """
        if self.sdk_wrapper:
            try:
                result = await self._ai_parse_epic(content)
                if result.story_ids:
                    return result
            except Exception as e:
                logger.warning(f"AI epic parsing failed, falling back to regex: {e}")

        return self._regex_parse_epic(content)

    async def _ai_parse_epic(self, content: str) -> EpicData:
        """使用AI解析Epic文档"""
        if not self.sdk_wrapper:
            return EpicData(raw_content=content)

        prompt = EPIC_PARSING_PROMPT.format(content=content[:3000])

        sdk = self.sdk_wrapper
        if hasattr(sdk, "prompt"):
            sdk.prompt = prompt

        success = await sdk.execute()

        if success and hasattr(sdk, "message_tracker"):
            latest_message = sdk.message_tracker.latest_message
            if latest_message:
                return self._parse_epic_json(latest_message, content)

        return EpicData(raw_content=content)

    def _parse_epic_json(self, response: str, original_content: str) -> EpicData:
        """从AI的JSON响应中解析EpicData"""
        try:
            # 清理响应，提取JSON
            cleaned = response.strip()
            if "```json" in cleaned:
                start = cleaned.find("```json") + 7
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()
            elif "```" in cleaned:
                start = cleaned.find("```") + 3
                end = cleaned.find("```", start)
                cleaned = cleaned[start:end].strip()

            data = json.loads(cleaned)

            return EpicData(
                title=data.get("title", ""),
                story_ids=data.get("story_ids", []),
                raw_content=original_content,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse AI epic response as JSON: {e}")
            return EpicData(raw_content=original_content)

    def _regex_parse_epic(self, content: str) -> EpicData:
        """使用正则表达式解析Epic文档（回退方案）"""
        result = EpicData(raw_content=content)

        # 提取标题
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            result.title = title_match.group(1).strip()

        story_ids: list[str] = []

        # 模式1: "### Story X.Y: Title"
        pattern1 = r"###\s+Story\s+(\d+(?:\.\d+)?)\s*:"
        matches1 = re.findall(pattern1, content, re.MULTILINE)
        story_ids.extend(matches1)

        # 模式2: "**Story ID**: X.Y"
        pattern2 = r"\*\*Story ID\*\*\s*:\s*(\d+(?:\.\d+)?)"
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        for story_id in matches2:
            if story_id not in story_ids:
                story_ids.append(story_id)

        result.story_ids = story_ids
        return result


# =============================================================================
# 向后兼容性别名
# =============================================================================

# 类别名
StatusParser = SimpleStoryParser
SimpleStatusParser = SimpleStoryParser


def create_status_parser(
    sdk_wrapper: Optional["SafeClaudeSDK"] = None,
) -> SimpleStoryParser:
    """
    创建状态解析器实例的工厂函数（向后兼容）

    Args:
        sdk_wrapper: SafeClaudeSDK实例

    Returns:
        SimpleStatusParser实例
    """
    return SimpleStatusParser(sdk_wrapper=sdk_wrapper)


def parse_story_status(
    content: str, sdk_wrapper: Optional["SafeClaudeSDK"] = None
) -> str:
    """
    便捷函数：直接解析故事状态（向后兼容）

    注意：这是一个同步函数，会创建新的事件循环来执行异步解析。
    在异步上下文中，建议直接使用 SimpleStatusParser 实例的 parse_status 方法。

    Args:
        content: 故事文档内容
        sdk_wrapper: SafeClaudeSDK实例

    Returns:
        解析后的状态字符串
    """
    parser = SimpleStatusParser(sdk_wrapper=sdk_wrapper)

    # 执行异步解析
    try:
        return asyncio.run(parser.parse_status(content))
    except Exception as e:
        logger.error(f"parse_story_status failed: {e}")
        return "unknown"


# =============================================================================
# 独立函数
# =============================================================================


def _normalize_story_status(status: str) -> str:
    """
    标准化故事状态值

    重要: 此函数现在只处理核心状态值
    禁止处理状态值反向影响核心状态值

    Args:
        status: 输入的状态值

    Returns:
        标准化的核心状态值
    """
    # 1. 标准化为标题格式
    status = status.strip().title()

    # 2. 如果已经是标准核心状态值，直接返回
    if status in CORE_STATUS_VALUES:
        return status

    # 3. 处理各种格式变体（小写匹配）
    status_lower = status.lower()

    # 草稿变体
    if status_lower in ["draft", "草稿"]:
        return CORE_STATUS_DRAFT

    # 开发就绪变体
    if status_lower in ["ready for development", "ready"]:
        return CORE_STATUS_READY_FOR_DEVELOPMENT

    # 进行中变体
    if status_lower in ["in progress", "in_progress", "进行中", "开发中"]:
        return CORE_STATUS_IN_PROGRESS

    # 审查就绪变体
    if status_lower in ["ready for review", "review", "待审查"]:
        return CORE_STATUS_READY_FOR_REVIEW

    # 完成就绪变体
    if status_lower in ["ready for done", "ready for completion"]:
        return CORE_STATUS_READY_FOR_DONE

    # 已完成变体
    if status_lower in ["done", "completed", "已完成", "完成"]:
        return CORE_STATUS_DONE

    # 失败变体
    if status_lower in ["failed", "error", "失败", "错误"]:
        return CORE_STATUS_FAILED

    # 4. 默认返回草稿状态
    return CORE_STATUS_DRAFT


# =============================================================================
# 向后兼容性别名
# =============================================================================


if __name__ == "__main__":
    # 简单测试
    test_content = """
    ## Status
    **Status**: Ready for Review
    **Priority**: High
    **Description**: This is a test story for status parsing
    """

    print("Testing SimpleStatusParser...")
    print(f"Test content: {test_content[:100]}...")
    print("\nNote: AI parsing requires SDK wrapper, running basic test only")

    # 验证类可以正常实例化
    parser = SimpleStatusParser()
    print("[OK] SimpleStatusParser instantiated successfully")
    print(
        f"[OK] SDK wrapper: {'provided' if parser.sdk_wrapper else 'not provided (AI parsing will be skipped)'}"
    )

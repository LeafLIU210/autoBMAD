"""
简化状态解析器 - 基于奥卡姆剃刀原则

根据奥卡姆剃刀原则，本模块实现单一AI智能解析策略，
移除复杂的启发式解析和语义归一化逻辑，
完全依赖Claude SDK进行状态解析。

设计原则：
- 单一职责：仅使用AI解析
- 简洁高效：无冗余代码
- 高准确性：AI语义理解优于正则匹配
- 易维护：只需维护一个解析策略
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

# Import SafeClaudeSDK with proper type checking to avoid circular imports
if TYPE_CHECKING:
    from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

logger = logging.getLogger(__name__)

# 标准状态值常量
# 核心状态值：用于文档和人类可读
CORE_STATUS_DRAFT = "Draft"
CORE_STATUS_READY_FOR_DEVELOPMENT = "Ready for Development"
CORE_STATUS_IN_PROGRESS = "In Progress"
CORE_STATUS_READY_FOR_REVIEW = "Ready for Review"
CORE_STATUS_READY_FOR_DONE = "Ready for Done"
CORE_STATUS_DONE = "Done"
CORE_STATUS_FAILED = "Failed"

# 处理状态值：用于数据库和内部状态跟踪
PROCESSING_STATUS_PENDING = "pending"
PROCESSING_STATUS_IN_PROGRESS = "in_progress"
PROCESSING_STATUS_REVIEW = "review"
PROCESSING_STATUS_COMPLETED = "completed"
PROCESSING_STATUS_FAILED = "failed"
PROCESSING_STATUS_CANCELLED = "cancelled"
PROCESSING_STATUS_ERROR = "error"

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

# 处理状态值集合
PROCESSING_STATUS_VALUES = {
    PROCESSING_STATUS_PENDING,
    PROCESSING_STATUS_IN_PROGRESS,
    PROCESSING_STATUS_REVIEW,
    PROCESSING_STATUS_COMPLETED,
    PROCESSING_STATUS_FAILED,
    PROCESSING_STATUS_CANCELLED,
    PROCESSING_STATUS_ERROR,
}

# 核心状态值 → 处理状态值映射
CORE_TO_PROCESSING_MAPPING = {
    CORE_STATUS_DRAFT: PROCESSING_STATUS_PENDING,
    CORE_STATUS_READY_FOR_DEVELOPMENT: PROCESSING_STATUS_PENDING,
    CORE_STATUS_IN_PROGRESS: PROCESSING_STATUS_IN_PROGRESS,
    CORE_STATUS_READY_FOR_REVIEW: PROCESSING_STATUS_REVIEW,
    CORE_STATUS_READY_FOR_DONE: PROCESSING_STATUS_REVIEW,
    CORE_STATUS_DONE: PROCESSING_STATUS_COMPLETED,
    CORE_STATUS_FAILED: PROCESSING_STATUS_FAILED,
}

# 处理状态值 → 核心状态值映射（反向映射）
PROCESSING_TO_CORE_MAPPING = {
    PROCESSING_STATUS_PENDING: CORE_STATUS_DRAFT,
    PROCESSING_STATUS_IN_PROGRESS: CORE_STATUS_IN_PROGRESS,
    PROCESSING_STATUS_REVIEW: CORE_STATUS_READY_FOR_REVIEW,
    PROCESSING_STATUS_COMPLETED: CORE_STATUS_DONE,
    PROCESSING_STATUS_FAILED: CORE_STATUS_FAILED,
    PROCESSING_STATUS_CANCELLED: CORE_STATUS_DRAFT,  # cancelled 映射为 Draft
    PROCESSING_STATUS_ERROR: CORE_STATUS_DRAFT,  # error 映射为 Draft
}


def core_status_to_processing(core_status: str) -> str:
    """
    将核心状态值转换为处理状态值（用于StateManager数据库存储）

    Args:
        core_status: 核心状态值（Draft, Ready for Development, In Progress, Ready for Review, Ready for Done, Done, Failed）

    Returns:
        处理状态值（pending, in_progress, review, completed, failed）
    """
    return CORE_TO_PROCESSING_MAPPING.get(core_status, PROCESSING_STATUS_PENDING)


def processing_status_to_core(processing_status: str) -> str:
    """
    将处理状态值转换为核心状态值（用于显示和业务逻辑）

    Args:
        processing_status: 处理状态值（pending, in_progress, review, completed, failed, cancelled, error）

    Returns:
        核心状态值（Draft, Ready for Development, In Progress, Ready for Review, Ready for Done, Done, Failed）
    """
    return PROCESSING_TO_CORE_MAPPING.get(processing_status, CORE_STATUS_DRAFT)


def is_core_status_valid(core_status: str) -> bool:
    """
    检查核心状态值是否有效

    Args:
        core_status: 状态值字符串

    Returns:
        True 如果状态值有效，False 否则
    """
    return core_status in CORE_STATUS_VALUES


def is_processing_status_valid(processing_status: str) -> bool:
    """
    检查处理状态值是否有效

    Args:
        processing_status: 状态值字符串

    Returns:
        True 如果状态值有效，False 否则
    """
    return processing_status in PROCESSING_STATUS_VALUES


# AI解析提示词模板
PROMPT_TEMPLATE = """
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


class SimpleStatusParser:
    """
    简化状态解析器 - 仅使用Claude SDK AI智能解析

    根据奥卡姆剃刀原则，移除所有复杂的启发式解析和语义归一化逻辑，
    专注于单一的AI智能解析策略，提供更高的准确性和更低的维护成本。
    """

    def __init__(self, sdk_wrapper: Optional["SafeClaudeSDK"] = None):
        """
        初始化简化状态解析器

        Args:
            sdk_wrapper: SafeClaudeSDK实例，用于AI智能解析
        """
        self.sdk_wrapper = sdk_wrapper

    async def parse_status(self, content: str) -> str:
        """
        使用Claude SDK AI智能解析故事状态

        这是唯一的解析策略，完全依赖AI的语义理解能力，
        避免正则表达式匹配的局限性和歧义性。

        Args:
            content: 故事文档内容

        Returns:
            解析后的标准状态字符串，如果解析失败返回 "unknown"
        """
        # 如果没有提供SDK包装器，无法执行AI解析
        if not self.sdk_wrapper:
            logger.warning("SimpleStatusParser: No SDK wrapper provided, cannot perform AI parsing")
            return "unknown"

        try:
            # 构建AI提示词
            prompt = PROMPT_TEMPLATE.format(content=content[:1000])  # 限制内容长度避免过长

            # 直接使用提供的sdk_wrapper
            sdk = self.sdk_wrapper

            # 更新提示词（如果SDK支持动态更新）
            if hasattr(sdk, 'prompt'):
                sdk.prompt = prompt

            # 执行查询
            success = await sdk.execute()

            if success:
                # 从message_tracker获取结果，添加安全检查
                if not hasattr(sdk, 'message_tracker'):
                    logger.warning("SimpleStatusParser: SDK does not have message_tracker attribute")
                    return "unknown"

                latest_message = sdk.message_tracker.latest_message
                if latest_message:
                    # 清理AI响应，提取状态值
                    return self._extract_status_from_response(latest_message)

            logger.warning("SimpleStatusParser: AI parsing returned no result")
            return "unknown"

        except asyncio.TimeoutError:
            logger.error("SimpleStatusParser: AI parsing timed out after 30 seconds")
            return "unknown"
        except Exception as e:
            logger.error(f"SimpleStatusParser: AI parsing failed: {e}")
            return "unknown"

    def _extract_status_from_response(self, response: str) -> str:
        """
        从AI响应中提取状态值

        Args:
            response: AI响应字符串

        Returns:
            提取的状态字符串，如果无法提取返回 "unknown"
        """
        # 处理None或空字符串响应
        if not response:
            logger.warning("SimpleStatusParser: Received empty response from AI")
            return "unknown"

        # 清理响应，移除标记和多余字符
        cleaned = response.strip()

        # 移除常见的AI响应标记
        cleaned = cleaned.replace("[Thinking]", "").replace("[Tool result]", "")
        cleaned = cleaned.replace("**", "").replace("*", "")

        # 移除前后缀文字
        cleaned = cleaned.strip()

        # 验证是否为已知状态值
        # 检查清理后的值是否匹配标准状态
        cleaned_lower = cleaned.lower()

        # 直接与标准状态值比较
        for core_status in CORE_STATUS_VALUES:
            if cleaned_lower == core_status.lower():
                return core_status

        # 如果无法匹配，返回原始清理后的值
        return cleaned if cleaned else "unknown"


# 向后兼容性别名
StatusParser = SimpleStatusParser


def create_status_parser(sdk_wrapper: Optional["SafeClaudeSDK"] = None) -> SimpleStatusParser:
    """
    创建状态解析器实例的工厂函数（向后兼容）

    Args:
        sdk_wrapper: SafeClaudeSDK实例

    Returns:
        SimpleStatusParser实例
    """
    return SimpleStatusParser(sdk_wrapper=sdk_wrapper)


def parse_story_status(content: str, sdk_wrapper: Optional["SafeClaudeSDK"] = None) -> str:
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
    print(f"[OK] SimpleStatusParser instantiated successfully")
    print(f"[OK] SDK wrapper: {'provided' if parser.sdk_wrapper else 'not provided (AI parsing will be skipped)'}")

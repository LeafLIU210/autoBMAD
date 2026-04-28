"""
LLM Response Parsing Module

Provides functions for extracting and validating JSON from LLM responses,
specifically for Independent and Evaluator agent outputs.
"""

import json
import re
from typing import Any, Literal, Protocol, cast

# Type aliases for clarity
QuestionPriority = Literal["low", "medium", "high", "critical"]
Verdict = Literal["APPROVED", "NEEDS_REVISION", "BLOCKED"]

# Structured types for better type inference
QuestionDict = dict[str, Any]
CriterionScores = dict[str, float]


# Protocol for message objects from LLM SDKs
class MessageLike(Protocol):
    """Protocol for message objects with role and content attributes."""

    role: str
    content: Any

    def extract_text(self) -> str: ...


# Protocol for content parts (like TextPart, ThinkingPart, etc.)
class ContentPartLike(Protocol):
    """Protocol for content part objects that may have text and type attributes."""

    text: str
    type: str


class ResponseParseError(Exception):
    """Raised when JSON extraction fails."""

    pass


class ValidationError(Exception):
    """Raised when schema validation fails."""

    pass


def extract_json(response: str) -> dict[str, Any]:
    """
    Extract JSON from an LLM response.

    Handles various formats:
    - Direct JSON: '{"key": "value"}'
    - Markdown code blocks: '```json\n{"key": "value"}\n```'
    - Embedded JSON: 'Here is the result: {"key": "value"}'

    Args:
        response: Raw LLM response string

    Returns:
        Parsed JSON as dictionary

    Raises:
        ResponseParseError: If JSON cannot be extracted
    """
    if not response or not response.strip():
        raise ResponseParseError("Empty response provided")

    # Try direct parsing first
    try:
        return cast(dict[str, Any], json.loads(response))
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    try:
        return extract_json_from_markdown(response)
    except ResponseParseError:
        pass

    # Aggressive extraction: find any line starting with { and balance braces
    lines = response.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("{"):
            json_str = ""
            brace_count = 0
            for char in "\n".join(lines[i:]):
                json_str += char
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            return cast(dict[str, Any], json.loads(json_str))
                        except json.JSONDecodeError:
                            break  # Try next occurrence

    # If all else fails, raise the appropriate error
    raise ResponseParseError("No JSON found in response")


def extract_json_from_markdown(text: str) -> dict[str, Any]:
    """
    Extract JSON from markdown code blocks.

    Args:
        text: Text containing markdown code blocks

    Returns:
        Parsed JSON as dictionary

    Raises:
        ResponseParseError: If no valid JSON found in code blocks
    """
    # Pattern to match code blocks with optional language specifier
    code_block_pattern = r"```(?:json|python)?\s*\n?([\s\S]*?)\n?```"
    matches: list[str] = re.findall(code_block_pattern, text)

    for match in matches:
        cleaned: str = match.strip()
        if cleaned:
            try:
                return cast(dict[str, Any], json.loads(cleaned))
            except json.JSONDecodeError:
                continue

    # If no code blocks worked, try parsing the whole text as JSON
    try:
        return cast(dict[str, Any], json.loads(text))
    except json.JSONDecodeError:
        pass

    raise ResponseParseError("No valid JSON found in markdown code blocks")


__all__ = [
    "extract_json",
    "extract_json_from_markdown",
    "extract_text_from_messages",
    "ResponseParseError",
    "ValidationError",
]


def extract_text_from_messages(messages: list[MessageLike]) -> str:
    """Extract text content from the last assistant Message.

    Fix: 使用 isinstance 判断 AssistantMessage，而非 role 属性。
    官方文档推荐模式：isinstance(msg, AssistantMessage)。

    Handles all content types returned by Kimi SDK:
    - list[ContentPart]: Multiple content parts (text, thinking, media)
    - str: Direct string content (legacy or simplified response)
    - ContentPart: Single content part

    Priority: SDK extract_text() > manual TextPart extraction > str conversion

    Args:
        messages: List of Message objects from LLM response.

    Returns:
        Extracted text content, or empty string if no text found.

    Example:
        >>> messages = await session_manager.single_prompt("Hello")
        >>> text = extract_text_from_messages(messages)
    """
    import structlog

    logger = structlog.get_logger(__name__)

    logger.debug("extract_text_debug", total_messages=len(messages))

    # Try to import SDK types for isinstance checks
    try:
        from claude_agent_sdk.types import AssistantMessage, TextBlock

        sdk_types_available = True
    except ImportError:
        sdk_types_available = False
        AssistantMessage = None  # type: ignore[misc]
        TextBlock = None  # type: ignore[misc]

    for idx, msg in enumerate(reversed(messages)):
        # Fix: Handle both dict and object type messages
        if isinstance(msg, dict):
            msg_content: Any = msg.get("content")
        else:
            msg_content = getattr(msg, "content", None)

        # Fix: 优先使用 isinstance 检查，fallback 到 role 字符串和 duck typing
        is_assistant = False
        if sdk_types_available and AssistantMessage is not None:
            is_assistant = isinstance(msg, AssistantMessage)

        # Fallback: 如果 isinstance 检查失败，尝试 role 属性（兼容旧格式）
        if not is_assistant:
            # Handle dict type messages (legacy format)
            if isinstance(msg, dict):
                is_assistant = msg.get("role") == "assistant"
            else:
                is_assistant = getattr(msg, "role", "") == "assistant"

        # Fix: 额外的 fallback - 通过 duck typing 识别 AssistantMessage
        # AssistantMessage 有 content 和 model 属性，但没有 subtype (SystemMessage 有)
        if not is_assistant and hasattr(msg, "content"):
            # 如果有 model 属性，很可能是 AssistantMessage
            if hasattr(msg, "model"):
                is_assistant = True
            # 如果类名包含 AssistantMessage
            elif "AssistantMessage" in type(msg).__name__:
                is_assistant = True

        msg_role = getattr(msg, "role", "unknown") if hasattr(msg, "role") else "(no role attr)"

        logger.debug(
            "message_analysis",
            idx=idx,
            msg_type=type(msg).__name__,
            is_assistant=is_assistant,
            role_attr=msg_role,
            has_content=hasattr(msg, "content"),
            content_type=type(msg_content).__name__,
        )

        if not is_assistant:
            logger.debug("skip_message", reason="not_assistant")
            continue

        # Check content after extracting - allow empty list to pass through
        if msg_content is None:
            logger.debug("skip_message", reason="content_is_none")
            continue

        # Priority 1: Use SDK's extract_text() method (most reliable)
        if hasattr(msg, "extract_text"):
            text: str = msg.extract_text()
            # Use cast to help type checker understand the list type
            msg_content_list: list[Any] = cast("list[Any]", msg_content)
            content_list_len: int | str = (
                len(msg_content_list) if isinstance(msg_content, list) else "N/A"
            )
            logger.debug(
                "sdk_extract_text",
                text_length=len(text) if text else 0,
                content_list_len=content_list_len,
            )
            if text:
                return text

        # Priority 2: Manual extraction from content
        content_raw: Any = msg_content

        # Case A: String content (legacy or simplified response)
        if isinstance(content_raw, str):
            logger.debug("string_content", length=len(content_raw))
            return content_raw

        # Case B: list[ContentPart] - iterate and extract text
        if hasattr(content_raw, "__iter__") and not isinstance(content_raw, str):
            text_parts: list[str] = []
            for part_idx, part in enumerate(content_raw):
                # Fix: Handle dict type content parts (legacy format)
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        part_text = part.get("text", "")
                        text_parts.append(part_text)
                        logger.debug("extracted_text_from_dict", text_length=len(part_text))
                    continue

                logger.debug(
                    "content_part_analysis",
                    part_idx=part_idx,
                    part_type=type(part).__name__,
                    has_text=hasattr(part, "text"),
                )

                # Fix: 使用 isinstance 检查 TextBlock，而非 type 属性
                if sdk_types_available and TextBlock is not None:
                    if isinstance(part, TextBlock):
                        part_text: str = part.text
                        text_parts.append(part_text)
                        logger.debug("extracted_text_from_textblock", text_length=len(part_text))
                    elif hasattr(part, "text"):
                        # Fallback for other objects with text attribute
                        part_text = part.text
                        text_parts.append(part_text)
                        logger.debug("extracted_text_from_part", text_length=len(part_text))
                else:
                    # Fallback: extract text from any part that has text attribute
                    if hasattr(part, "text"):
                        part_text = part.text
                        text_parts.append(part_text)
                        logger.debug("extracted_text_from_part", text_length=len(part_text))

                if isinstance(part, str):
                    text_parts.append(part)

            combined: str = "".join(text_parts)
            logger.debug("combined_text", length=len(combined))
            if combined:
                return combined
            # If no text found, continue to next message
            continue

        # Case C: Single ContentPart (not a list)
        if hasattr(content_raw, "text") and not isinstance(content_raw, list | tuple):
            content_text: str = getattr(content_raw, "text", "")
            logger.debug("single_content_part", text_length=len(content_text))
            return content_text

        # Case D: Unknown type - convert to string (only for non-iterable types)
        logger.debug("fallback_to_str")
        # Convert any remaining type to string as fallback
        content_raw_str: str = content_raw  # type: ignore[assignment]
        return str(content_raw_str)

    # P2 Fix: 升级为 warning 并包含诊断信息
    role_list = []
    assistant_found = False
    for msg in messages:
        if sdk_types_available and AssistantMessage is not None:
            if isinstance(msg, AssistantMessage):
                assistant_found = True
                role_list.append("assistant(via isinstance)")
            else:
                role_list.append(getattr(msg, "role", type(msg).__name__))
        else:
            role = getattr(msg, "role", "unknown")
            role_list.append(role)
            if role == "assistant":
                assistant_found = True

    logger.warning(
        "no_text_extracted",
        message_count=len(messages),
        role_list=role_list,
        has_assistant_message=assistant_found,
        hint="Check if LLM returned valid assistant messages with text content",
    )
    return ""

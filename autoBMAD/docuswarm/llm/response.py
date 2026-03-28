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


def validate_independent_output(data: dict[str, Any]) -> None:
    """
    Validate Independent Agent output against schema.

    Schema:
        - deliverable: {title: str, content: str, file_path: str, sha256: str, metadata: dict}
        - questions: List[{priority: str, question: str, context: str}]
        - private_reasoning: Optional[str]

    P0 Single Truth: file_path and sha256 are now included in deliverable.

    Args:
        data: Output from Independent Agent

    Raises:
        ValidationError: If validation fails
    """
    # Validate deliverable (required)
    if "deliverable" not in data:
        raise ValidationError("deliverable: required field missing")

    deliverable: dict[str, Any] = data["deliverable"]

    # Validate deliverable.title (required, must be string)
    if "title" not in deliverable:
        raise ValidationError("deliverable.title: required field missing")
    if not isinstance(deliverable["title"], str):
        raise ValidationError("deliverable.title: must be a string")

    # P0-3: Validate file_path (now REQUIRED)
    if "file_path" not in deliverable:
        raise ValidationError("deliverable.file_path: required field missing")
    if not isinstance(deliverable["file_path"], str):
        raise ValidationError("deliverable.file_path: must be a string")

    # P0-3: Validate sha256 (now REQUIRED)
    if "sha256" not in deliverable:
        raise ValidationError("deliverable.sha256: required field missing")
    if not isinstance(deliverable["sha256"], str):
        raise ValidationError("deliverable.sha256: must be a string")

    # P0-3: Validate summary (preferred over content)
    if "summary" in deliverable and not isinstance(deliverable["summary"], str):
        raise ValidationError("deliverable.summary: must be a string")

    # P0-3: content is now optional (deprecated, use summary instead)
    if "content" in deliverable and not isinstance(deliverable["content"], str):
        raise ValidationError("deliverable.content: must be a string")

    # Validate deliverable.metadata (optional, but if present must be dict)
    if "metadata" in deliverable and not isinstance(deliverable["metadata"], dict):
        raise ValidationError("deliverable.metadata: must be a dict")

    # Validate questions (required)
    if "questions" not in data:
        raise ValidationError("questions: required field missing")
    if not isinstance(data["questions"], list):
        raise ValidationError("questions: must be a list")

    valid_priorities = {"blocking", "clarifying", "optional"}

    questions: list[dict[str, Any]] = cast("list[dict[str, Any]]", data["questions"])
    for i, question_dict in enumerate(questions):
        # Validate priority (required)
        if "priority" not in question_dict:
            raise ValidationError(f"questions[{i}].priority: required field missing")
        if question_dict["priority"] not in valid_priorities:
            raise ValidationError(
                f"questions[{i}].priority: invalid value '{question_dict['priority']}'. Must be one of: {', '.join(valid_priorities)}"
            )

        # Validate question (required, must be string)
        if "question" not in question_dict:
            raise ValidationError(f"questions[{i}].question: required field missing")
        if not isinstance(question_dict["question"], str):
            raise ValidationError(f"questions[{i}].question: must be a string")

        # Validate context (required, must be string)
        if "context" not in question_dict:
            raise ValidationError(f"questions[{i}].context: required field missing")
        if not isinstance(question_dict["context"], str):
            raise ValidationError(f"questions[{i}].context: must be a string")

    # Validate private_reasoning (optional, but if present must be string)
    if "private_reasoning" in data and data["private_reasoning"] is not None:
        if not isinstance(data["private_reasoning"], str):
            raise ValidationError("private_reasoning: must be a string")


def validate_evaluator_output(data: dict[str, Any]) -> None:
    """
    Validate Evaluator Agent output against schema.

    Schema:
        - criterion_scores: Dict[str, float] (values 0.0-1.0)
        - alignment_score: float (0.0-1.0)
        - verdict: Literal["APPROVED", "NEEDS_REVISION", "BLOCKED"]
        - issues_found: List[str]
        - suggestions: List[str]

    Args:
        data: Output from Evaluator Agent

    Raises:
        ValidationError: If validation fails
    """
    valid_verdicts = {"APPROVED", "NEEDS_REVISION", "BLOCKED"}

    # Validate criterion_scores (required, must be dict)
    if "criterion_scores" not in data:
        raise ValidationError("criterion_scores: required field missing")
    if not isinstance(data["criterion_scores"], dict):
        raise ValidationError("criterion_scores: must be a dict")

    criterion_scores: dict[str, float] = cast("dict[str, float]", data["criterion_scores"])
    for key, value in criterion_scores.items():
        # Validation: ensure value is a number
        if not isinstance(value, int | float):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValidationError(
                f"criterion_scores['{key}']: must be a number, got {type(value).__name__}"
            )
        # Validation: ensure value is in valid range
        if not (0.0 <= value <= 1.0):
            raise ValidationError(
                f"criterion_scores['{key}']: must be between 0.0 and 1.0, got {value}"
            )

    # Validate alignment_score (required, must be number)
    if "alignment_score" not in data:
        raise ValidationError("alignment_score: required field missing")
    if not isinstance(data["alignment_score"], int | float):
        raise ValidationError("alignment_score: must be a number")
    if not (0.0 <= data["alignment_score"] <= 1.0):
        raise ValidationError(
            f"alignment_score: must be between 0.0 and 1.0, got {data['alignment_score']}"
        )

    # Validate verdict (required, must be one of valid values)
    if "verdict" not in data:
        raise ValidationError("verdict: required field missing")
    if data["verdict"] not in valid_verdicts:
        raise ValidationError(
            f"verdict: invalid value '{data['verdict']}'. Must be one of: APPROVED, NEEDS_REVISION, BLOCKED"
        )

    # Validate issues_found (required, must be list of strings)
    if "issues_found" not in data:
        raise ValidationError("issues_found: required field missing")
    if not isinstance(data["issues_found"], list):
        raise ValidationError("issues_found: must be a list")
    issues_found: list[str] = cast("list[str]", data["issues_found"])
    # Validation: ensure list contains strings
    for i, issue in enumerate(issues_found):
        if not isinstance(issue, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValidationError(f"issues_found[{i}]: must be a string")

    # Validate suggestions (required, must be list of strings)
    if "suggestions" not in data:
        raise ValidationError("suggestions: required field missing")
    if not isinstance(data["suggestions"], list):
        raise ValidationError("suggestions: must be a list")
    suggestions: list[str] = cast("list[str]", data["suggestions"])
    # Validation: ensure list contains strings
    for i, suggestion in enumerate(suggestions):
        if not isinstance(suggestion, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValidationError(f"suggestions[{i}]: must be a string")


__all__ = [
    "extract_json",
    "extract_json_from_markdown",
    "extract_text_from_messages",
    "validate_independent_output",
    "validate_evaluator_output",
    "ResponseParseError",
    "ValidationError",
]


def extract_text_from_messages(messages: list[MessageLike]) -> str:
    """Extract text content from the last assistant Message.

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

    for idx, msg in enumerate(reversed(messages)):
        msg_role: str = getattr(msg, "role", "")
        msg_content: Any = getattr(msg, "content", None)
        logger.debug(
            "message_analysis",
            idx=idx,
            has_role=hasattr(msg, "role"),
            has_content=hasattr(msg, "content"),
            role=msg_role,
            content_type=type(msg_content).__name__,
        )

        if not hasattr(msg, "role") or not hasattr(msg, "content"):
            continue

        if msg_role != "assistant":
            logger.debug("skip_message", reason=f"not_assistant_role={msg_role}")
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

        # Case B: list[ContentPart] - iterate and extract ALL text (including thinking)
        if hasattr(content_raw, "__iter__") and not isinstance(content_raw, str):
            text_parts: list[str] = []
            for part_idx, part in enumerate(content_raw):
                part_typed: ContentPartLike = part  # type: ignore[assignment]
                logger.debug(
                    "content_part_analysis",
                    part_idx=part_idx,
                    part_type=type(part).__name__,
                    has_text=hasattr(part, "text"),
                    has_type_attr=hasattr(part, "type"),
                    type_value=getattr(part, "type", None),
                )
                # Extract text from any part that has text attribute
                if hasattr(part, "text"):
                    part_text: str = part_typed.text
                    text_parts.append(part_text)
                    logger.debug("extracted_text_from_part", text_length=len(part_text))
                elif isinstance(part, str):
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

    logger.debug("no_text_extracted")
    return ""

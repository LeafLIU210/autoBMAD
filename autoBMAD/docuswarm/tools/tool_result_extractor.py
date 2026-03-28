"""Tool result extractor for DocuSwarm."""

import re
from dataclasses import dataclass
from typing import Any

from autoBMAD.docuswarm.tools.tool_result import ToolResult


class ToolExtractionError(Exception):
    """Error extracting tool result."""

    pass


@dataclass
class DeliverableMetadata:
    """Metadata for a deliverable."""

    title: str
    filename: str
    content_type: str = "text/markdown"


class ToolResultExtractor:
    """Extract tool results from responses."""

    @staticmethod
    def _slugify(title: str) -> str:
        """Convert title to filename-safe slug.

        Args:
            title: Title string

        Returns:
            Slugified string
        """
        # Convert to lowercase and replace non-alphanumeric with hyphens
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower())
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        # Collapse multiple hyphens
        slug = re.sub(r"-+", "-", slug)
        return slug

    @staticmethod
    def _create_metadata(title: str) -> DeliverableMetadata:
        """Create metadata from title.

        Args:
            title: Deliverable title

        Returns:
            DeliverableMetadata
        """
        filename = ToolResultExtractor._slugify(title) + ".md"
        return DeliverableMetadata(
            title=title,
            filename=filename,
        )

    @staticmethod
    def extract_from_messages(messages: list[dict[str, Any]]) -> ToolResult:
        """Extract tool result from messages.

        Args:
            messages: List of message dicts

        Returns:
            ToolResult
        """
        try:
            # Find assistant message with tool calls
            for msg in messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "tool_use":
                                input_data = item.get("input", {})
                                return ToolResult(
                                    success=True,
                                    result={
                                        "title": input_data.get("title", "Untitled"),
                                        "content": input_data.get("content", ""),
                                        "metadata": input_data.get("metadata", {}),
                                    },
                                )
            return ToolResult(success=False, error="No tool result found in messages")
        except Exception as e:
            raise ToolExtractionError(f"Failed to extract tool result: {e}") from e


def extract_tool_result(response: ToolResult | dict[str, Any] | Any) -> ToolResult:
    """Extract tool result from response.

    Args:
        response: Response from tool execution

    Returns:
        ToolResult
    """
    if isinstance(response, ToolResult):
        return response

    if isinstance(response, dict):
        typed_response: dict[str, Any] = response
        return ToolResult.from_dict(typed_response)

    return ToolResult(success=True, result=response)


def extract_tool_calls(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract tool calls from messages.

    Args:
        messages: List of message dicts

    Returns:
        List of tool call dicts
    """
    tool_calls = []
    for msg in messages:
        content = msg.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_calls.append(item)
    return tool_calls


def extract_text_content(messages: list[dict[str, Any]]) -> str:
    """Extract text content from messages.

    Args:
        messages: List of message dicts

    Returns:
        Concatenated text content
    """
    texts: list[str] = []
    for msg in messages:
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        item_dict: dict[str, Any] = item
                        if item_dict.get("type") == "text":
                            text_value: str = str(item_dict.get("text", ""))
                            texts.append(text_value)
    return "\n".join(texts)

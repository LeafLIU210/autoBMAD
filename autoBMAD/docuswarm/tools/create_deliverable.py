"""CreateDeliverableTool - Pydantic-based tool for creating deliverables.

P0 Single Truth (Plan B): Tool returns metadata only, not full content.
- File layer is the single source of truth
- State layer stores only metadata

This tool uses ToolResult internally and adapts to SDK format at boundary.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field
from typing_extensions import override

from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultCallableTool
from autoBMAD.docuswarm.tools.tool_result import ToolResult


class CreateDeliverableParams(BaseModel):
    """Parameters for creating a deliverable.

    Attributes:
        title: The deliverable title.
        content: The deliverable content in Markdown format.
        metadata: Additional metadata for the deliverable.
    """

    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


def _slugify_filename(title: str) -> str:
    """Convert title to a valid filename slug.

    Args:
        title: The deliverable title.

    Returns:
        A slugified filename with .md extension.
    """
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    # Remove special characters (keep only alphanumeric and hyphens)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return f"{slug}.md"


def _extract_section_index(content: str) -> list[str]:
    """Extract section headings (##) from markdown content.

    Args:
        content: Markdown content.

    Returns:
        List of section titles (without #).
    """
    # Match ## headings (not ### or more)
    pattern = r"^##\s+(.+)$"
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def _count_words(content: str) -> int:
    """Count words in content.

    Args:
        content: Text content.

    Returns:
        Word count.
    """
    return len(content.split())


def _compute_sha256(content: str) -> str:
    """Compute SHA256 hash of content.

    Args:
        content: Text content.

    Returns:
        Hex digest of SHA256 hash (64 characters).
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CreateDeliverableTool(ToolResultCallableTool[CreateDeliverableParams]):
    """Tool for creating node deliverable documents.

    This tool uses the ToolResultCallableTool base class for automatic
    SDK format adaptation.

    The tool writes markdown files to the specified output directory.

    P0 Single Truth: Returns metadata only, full content is in the file.
    """

    name: str = "create_deliverable"
    description: str = """Create a node deliverable document and return metadata.

Returns metadata including:
- file_path: Path to the saved file
- sha256: SHA256 hash of the content
- word_count: Number of words
- section_index: List of ## section headings
- title: Document title

The full content is saved to disk and can be read from file_path.
"""
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize the tool with optional output directory.

        Args:
            output_dir: Directory for output files. Defaults to Path.cwd() for backward compatibility.
        """
        super().__init__()
        self.output_dir = output_dir or Path.cwd()

    @override
    async def _execute(self, params: CreateDeliverableParams) -> ToolResult:
        """Create a deliverable with the given parameters.

        Args:
            params: The validated parameters from the tool call.

        Returns:
            ToolResult with metadata on success, error on failure.
        """
        try:
            filename = _slugify_filename(params.title)
            file_path = self.output_dir / filename

            # Write content to file
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)

            # Compute metadata (Single Truth: metadata only, not full content)
            sha256_hash = _compute_sha256(params.content)
            word_count = _count_words(params.content)
            section_index = _extract_section_index(params.content)

            # Build metadata (Single Truth: metadata only)
            metadata = {
                "title": params.title,
                "file_path": str(file_path),
                "sha256": sha256_hash,
                "word_count": word_count,
                "section_index": section_index,
                "content_type": "markdown",
            }

            # ✅ 返回结构化 ToolResult（不再使用 METADATA: 字符串）
            return ToolResult(
                success=True,
                result=metadata,
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )


# Backward compatibility: function-style API for tests
# Creates a tool instance and calls it
async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    """Backward-compatible function API for creating deliverables.

    This function creates a CreateDeliverableTool instance and calls it,
    providing compatibility with code that uses the old function-style API.

    Args:
        params: Parameters for creating the deliverable.

    Returns:
        ToolResult with success status and metadata.
    """
    tool = CreateDeliverableTool()
    return await tool._execute(params)

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
from typing import Any, override

import aiofiles
from pydantic import BaseModel, Field, field_validator, model_validator

from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultCallableTool
from autoBMAD.docuswarm.tools.tool_result import ToolResult


class CreateDeliverableParams(BaseModel):
    """Parameters for creating a deliverable.

    Supports both single-document and multi-document workflows.
    For multi-document sets (e.g., Architect nodes with 2-4 documents,
    PO nodes with 3-5 documents), use document_index, document_total,
    and document_type fields to track document position and type.

    Attributes:
        title: The deliverable title.
        content: The deliverable content in Markdown format.
        metadata: Additional metadata for the deliverable.
        document_index: 1-based position of this document in a multi-document set.
            Must be >= 1 when provided. Must be <= document_total when both are provided.
        document_total: Total number of documents in the multi-document set.
            Must be >= 1 when provided.
        document_type: Type identifier for this document (e.g., "system-architecture",
            "api-design", "prd"). Used for typed documents in multi-document sets.
    """

    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    document_index: int | None = Field(
        default=None,
        description="1-based position of this document in a multi-document set (>= 1)",
    )
    document_total: int | None = Field(
        default=None,
        description="Total number of documents in the multi-document set (>= 1)",
    )
    document_type: str | None = Field(
        default=None,
        description="Type identifier for this document (e.g., 'system-architecture', 'api-design')",
    )

    @field_validator("document_index")
    @classmethod
    def validate_document_index(cls, v: int | None) -> int | None:
        """Validate that document_index >= 1 when provided."""
        if v is not None and v < 1:
            msg = "document_index must be >= 1 (1-based indexing)"
            raise ValueError(msg)
        return v

    @field_validator("document_total")
    @classmethod
    def validate_document_total(cls, v: int | None) -> int | None:
        """Validate that document_total >= 1 when provided."""
        if v is not None and v < 1:
            msg = "document_total must be >= 1"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_index_not_exceed_total(self) -> CreateDeliverableParams:
        """Validate that document_index <= document_total when both are provided."""
        if (
            self.document_index is not None
            and self.document_total is not None
            and self.document_index > self.document_total
        ):
            msg = f"document_index ({self.document_index}) cannot exceed document_total ({self.document_total})"
            raise ValueError(msg)
        return self


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
    params: type[BaseModel] | None = CreateDeliverableParams

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
            metadata: dict[str, Any] = {
                "title": params.title,
                "file_path": str(file_path),
                "sha256": sha256_hash,
                "word_count": word_count,
                "section_index": section_index,
                "content_type": "markdown",
            }

            # Add multi-document metadata if provided (Story 33.1)
            if params.document_index is not None:
                metadata["document_index"] = params.document_index
            if params.document_total is not None:
                metadata["document_total"] = params.document_total
            if params.document_type is not None:
                metadata["document_type"] = params.document_type

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

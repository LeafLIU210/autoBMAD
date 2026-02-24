"""CreateDeliverableTool - Pydantic-based tool for creating deliverables."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


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


class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    """Tool for creating node deliverable documents.

    This tool uses the kimi-agent-sdk's CallableTool2 for automatic
    parameter deserialization and dispatch.

    The tool writes markdown files to the SDK's work_dir, which is set
    as the current working directory when executing the agent.
    """

    name: str = "create_deliverable"
    description: str = "Create a node deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__()

    @override
    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        """Create a deliverable with the given parameters.

        Args:
            params: The validated parameters from the tool call.

        Returns:
            ToolOk on success, ToolError on failure.
        """
        # Write to work_dir (Path.cwd())
        try:
            filename = _slugify_filename(params.title)
            file_path = Path.cwd() / filename

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)

            return ToolOk(output=f"Deliverable '{params.title}' saved to {file_path}")
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to write deliverable",
            )

"""ListDocsFilesTool - 列出 @docs 目录文件的工具.

This module provides a tool for listing files in the @docs directory
with glob pattern support.
"""

from __future__ import annotations

from pathlib import Path
from typing import override

from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ListDocsFilesParams(BaseModel):
    """Parameters for listing docs files.

    Attributes:
        directory: Relative directory path from docs root.
        pattern: Glob pattern for filtering files.
        recursive: Whether to search recursively.
    """

    directory: str = Field(
        default=".", description="Relative directory path from docs root, e.g., 'architecture'"
    )
    pattern: str = Field(
        default="*.md", description="Glob pattern for filtering files, e.g., '*.md' or '*.yaml'"
    )
    recursive: bool = Field(
        default=True, description="Whether to search recursively in subdirectories"
    )


class ListDocsFilesTool(CallableTool2[ListDocsFilesParams]):
    """Tool for listing files in @docs directory.

    This tool helps agents discover available documentation files.

    Features:
    - Glob pattern support
    - Recursive/non-recursive search
    - Path traversal prevention
    """

    name: str = "list_docs_files"
    description: str = "List files in the @docs directory with glob pattern support"
    params: type[ListDocsFilesParams] = ListDocsFilesParams

    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        self.docs_root = project_root / "docs"

    @override
    async def __call__(self, params: ListDocsFilesParams) -> ToolReturnValue:
        """List files in docs directory.

        Args:
            params: Validated parameters.

        Returns:
            ToolOk with file list or ToolError if failed.
        """
        try:
            # Construct target directory
            target_dir = self.docs_root / params.directory

            # Security check: Path traversal prevention
            resolved_dir = target_dir.resolve()
            docs_root_resolved = self.docs_root.resolve()

            if not str(resolved_dir).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.directory} is outside docs/",
                    brief="Access denied",
                )

            if not resolved_dir.exists():
                return ToolError(
                    output="",
                    message=f"Directory not found: {params.directory}",
                    brief="Directory not found",
                )

            if not resolved_dir.is_dir():
                return ToolError(
                    output="",
                    message=f"Not a directory: {params.directory}",
                    brief="Not a directory",
                )

            # Build glob pattern
            if params.recursive:
                glob_pattern = f"**/{params.pattern}"
            else:
                glob_pattern = params.pattern

            # Collect files
            files = sorted(resolved_dir.glob(glob_pattern))

            # Convert to relative paths from docs root (use forward slashes for consistency)
            relative_files = [
                f.relative_to(self.docs_root).as_posix() for f in files if f.is_file()
            ]

            if not relative_files:
                return ToolOk(
                    output=f"No files found matching pattern '{params.pattern}' in {params.directory}"
                )

            file_list = "\n".join(f"- {f}" for f in relative_files)
            return ToolOk(
                output=f"Found {len(relative_files)} file(s) in {params.directory}:\n\n{file_list}"
            )

        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Failed to list files")

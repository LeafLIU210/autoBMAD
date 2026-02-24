"""ReadDocsFileTool - 读取 @docs 目录文件的工具.

This module provides a tool for reading files from the @docs directory
with security checks to prevent path traversal attacks.
"""

from __future__ import annotations

from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ReadDocsFileParams(BaseModel):
    """Parameters for reading docs file.

    Attributes:
        file_path: Relative path from docs root (e.g., 'architecture/system-design.md')
    """

    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )


class ReadDocsFileTool(CallableTool2[ReadDocsFileParams]):
    """Tool for reading files from @docs directory.

    This tool provides read-only access to project documentation.
    It only allows reading files within the docs/ directory for safety.

    Security features:
    - Path traversal prevention (resolve + startswith check)
    - Symlink resolution
    - File existence and type validation
    """

    name: str = "read_docs_file"
    description: str = "Read content from a file in the @docs directory"
    params: type[ReadDocsFileParams] = ReadDocsFileParams

    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        # Compute docs root: tools/ → docuswarm/ → autoBMAD/ → DocuSwarm/ → docs/
        self.docs_root = self._compute_docs_root()

    def _compute_docs_root(self) -> Path:
        """Compute docs root directory.

        Returns:
            Path to docs/ directory.
        """
        current_file = Path(__file__)
        # Navigate: tools/ → docuswarm/ → autoBMAD/ → DocuSwarm/
        project_root = current_file.parent.parent.parent.parent
        return project_root / "docs"

    @override
    async def __call__(self, params: ReadDocsFileParams) -> ToolReturnValue:
        """Read file from docs directory.

        Args:
            params: Validated parameters with file_path.

        Returns:
            ToolOk with file content or ToolError if failed.
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path

            # Security check 1: Resolve symlinks and check it's under docs/
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()

            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/ directory",
                    brief="Access denied - path traversal attempt",
                )

            # Security check 2: File must exist
            if not resolved_path.exists():
                return ToolError(
                    output="", message=f"File not found: {params.file_path}", brief="File not found"
                )

            # Security check 3: Must be a file (not directory)
            if not resolved_path.is_file():
                return ToolError(
                    output="", message=f"Not a file: {params.file_path}", brief="Not a file"
                )

            # Read file content
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                content = await f.read()

            return ToolOk(output=f"Content of {params.file_path}:\n\n{content}")

        except PermissionError:
            return ToolError(
                output="",
                message=f"Permission denied: {params.file_path}",
                brief="Permission denied",
            )
        except UnicodeDecodeError:
            return ToolError(
                output="",
                message=f"Cannot decode file (not UTF-8): {params.file_path}",
                brief="Encoding error",
            )
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Failed to read file")

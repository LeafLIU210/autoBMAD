"""UpdateDocsFileTool - 更新 @docs 目录文件的工具.

This module provides a tool for updating files in the @docs directory
with security checks, content verification, and automatic backup.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class UpdateDocsFileParams(BaseModel):
    """Parameters for updating docs file.

    Attributes:
        file_path: Relative path from docs root.
        old_content: Original content snippet for verification (first 500 chars).
        new_content: Complete new content to write.
        create_backup: Whether to create backup before updating.
    """

    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )
    old_content: str = Field(
        description="Original content snippet (for verification, should match file's first 500 chars)"
    )
    new_content: str = Field(description="Complete new content to write to the file")
    create_backup: bool = Field(
        default=True, description="Whether to create a backup before updating"
    )


class UpdateDocsFileTool(CallableTool2[UpdateDocsFileParams]):
    """Tool for updating files in @docs directory.

    This tool provides controlled write access to project documentation.

    Safety features:
    - Path traversal prevention
    - Content verification before update
    - Automatic backup creation
    - Atomic write operation (temp file + rename)
    """

    name: str = "update_docs_file"
    description: str = "Update content of a file in the @docs directory"
    params: type[UpdateDocsFileParams] = UpdateDocsFileParams

    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        # Compute docs root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        self.docs_root = project_root / "docs"
        self.backup_dir = self.docs_root / ".backups"

    @override
    async def __call__(self, params: UpdateDocsFileParams) -> ToolReturnValue:
        """Update file in docs directory.

        Args:
            params: Validated parameters.

        Returns:
            ToolOk if successful, ToolError if failed.
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path

            # Security check: Path traversal prevention
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()

            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/",
                    brief="Access denied",
                )

            # Check file exists
            if not resolved_path.exists():
                return ToolError(
                    output="", message=f"File not found: {params.file_path}", brief="File not found"
                )

            if not resolved_path.is_file():
                return ToolError(
                    output="", message=f"Not a file: {params.file_path}", brief="Not a file"
                )

            # Read current content for verification
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                current_content = await f.read()

            # Verify old_content matches (first 500 chars)
            current_preview = current_content[:500]
            if params.old_content not in current_preview:
                return ToolError(
                    output="",
                    message=(
                        "Content verification failed. "
                        "The file may have been modified by another process. "
                        "Please read the file again and retry."
                    ),
                    brief="Content verification failed",
                )

            # Create backup if requested
            backup_name = ""
            if params.create_backup:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                backup_name = f"{Path(params.file_path).stem}_{timestamp}.bak"
                backup_path = self.backup_dir / backup_name

                async with aiofiles.open(backup_path, "w", encoding="utf-8") as f:
                    await f.write(current_content)

            # Atomic write: write to temp file, then rename
            temp_path = resolved_path.with_suffix(resolved_path.suffix + ".tmp")

            try:
                async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                    await f.write(params.new_content)

                # Atomic rename
                temp_path.replace(resolved_path)

                backup_info = f" (backup: {backup_name})" if backup_name else ""
                return ToolOk(output=f"Successfully updated {params.file_path}{backup_info}")
            finally:
                # Cleanup temp file if it still exists (on error)
                if temp_path.exists():
                    temp_path.unlink()

        except PermissionError:
            return ToolError(
                output="",
                message=f"Permission denied: {params.file_path}",
                brief="Permission denied",
            )
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Failed to update file")

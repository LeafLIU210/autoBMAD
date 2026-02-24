"""File storage module for DocuSwarm pipeline deliverables.

This module provides file-based storage for pipeline outputs including
markdown deliverables and metadata JSON files.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiofiles
import yaml

from autoBMAD.docuswarm.exceptions import StorageError

# Filename mapping from node types to markdown filenames
# Includes both canonical names and pipeline node IDs
FILENAME_MAP: dict[str, str] = {
    "analyst": "analyst-report.md",
    "prd": "prd.md",
    "pm": "prd.md",
    "ux": "ux-design.md",
    "architecture": "architecture.md",
    "architect": "architecture.md",
    "epics": "epics-stories.md",
    "po": "epics-stories.md",
}

# Default output directory
DEFAULT_OUTPUT_DIR = "output"

# Pattern to validate pipeline_id and prevent path traversal
_INVALID_PATH_PATTERN = re.compile(r"[./\\]")


class FileStorage:
    """Manages file storage for pipeline deliverables.

    This class provides async methods for saving markdown deliverables
    and metadata JSON files to the output directory structure.

    Attributes:
        output_root: Root directory for all pipeline outputs.
    """

    def __init__(self, output_root: Path | str | None = None) -> None:
        """Initialize FileStorage with output directory.

        Args:
            output_root: Root directory for outputs. Defaults to "output".
        """
        self.output_root = Path(output_root) if output_root else Path(DEFAULT_OUTPUT_DIR)
        # Create output root if it doesn't exist
        self.output_root.mkdir(parents=True, exist_ok=True)

    def _validate_pipeline_id(self, pipeline_id: str) -> None:
        """Validate pipeline_id to prevent path traversal attacks.

        Args:
            pipeline_id: The pipeline identifier to validate.

        Raises:
            StorageError: If pipeline_id contains invalid characters.
        """
        if not pipeline_id or not pipeline_id.strip():
            raise StorageError(
                "pipeline_id cannot be empty",
                pipeline_id=pipeline_id,
            )

        # Check for path traversal attempts
        if _INVALID_PATH_PATTERN.search(pipeline_id):
            raise StorageError(
                f"Invalid pipeline_id: contains path traversal characters: {pipeline_id}",
                pipeline_id=pipeline_id,
            )

        # Check for absolute paths
        if pipeline_id.startswith("/") or (len(pipeline_id) > 1 and pipeline_id[1] == ":"):
            raise StorageError(
                f"Invalid pipeline_id: absolute paths not allowed: {pipeline_id}",
                pipeline_id=pipeline_id,
            )

    async def _ensure_output_dir(self, pipeline_id: str) -> Path:
        """Ensure output directory exists for a pipeline.

        Creates the output root and pipeline-specific subdirectory
        if they don't exist.

        Args:
            pipeline_id: The pipeline identifier.

        Returns:
            Path to the pipeline's output directory.
        """
        self._validate_pipeline_id(pipeline_id)

        pipeline_dir = self.output_root / pipeline_id
        pipeline_dir.mkdir(parents=True, exist_ok=True)
        return pipeline_dir

    async def save_deliverable(
        self,
        pipeline_id: str,
        node_type: str,
        content: str,
        add_frontmatter: bool = False,
        evaluation_score: float | None = None,
    ) -> Path:
        """Save a deliverable markdown file.

        Writes the deliverable content to a properly named markdown file
        with optional YAML frontmatter. Uses atomic write pattern (temp file + rename).

        Args:
            pipeline_id: The pipeline identifier.
            node_type: The type of node (e.g., "analyst", "prd", "ux").
            content: The markdown content to save.
            add_frontmatter: Whether to add YAML frontmatter with metadata.
            evaluation_score: Optional evaluation score for the deliverable.

        Returns:
            Path to the saved file.

        Raises:
            StorageError: If node_type is unknown or file operation fails.
        """
        # Validate node type
        filename = FILENAME_MAP.get(node_type)
        if not filename:
            raise StorageError(
                f"Unknown node type: {node_type}",
                node_type=node_type,
                pipeline_id=pipeline_id,
            )

        # Ensure directory exists
        pipeline_dir = await self._ensure_output_dir(pipeline_id)
        file_path = pipeline_dir / filename

        # Build content with optional frontmatter
        final_content = content
        if add_frontmatter:
            frontmatter = {
                "pipeline_id": pipeline_id,
                "node": node_type,
                "created_at": datetime.now(UTC).isoformat(),
            }
            if evaluation_score is not None:
                frontmatter["evaluation_score"] = evaluation_score

            frontmatter_str = yaml.dump(frontmatter, default_flow_style=False)
            final_content = f"---\n{frontmatter_str}---\n\n{content}"

        # Atomic write: write to temp file then rename
        temp_path = file_path.with_suffix(".tmp")
        try:
            async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                _ = await f.write(final_content)

            # Atomic rename
            _ = temp_path.replace(file_path)
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise StorageError(
                f"Failed to save deliverable: {e}",
                pipeline_id=pipeline_id,
                node_type=node_type,
                filename=str(file_path),
            ) from e

        return file_path

    async def save_metadata(
        self,
        pipeline_id: str,
        deliverables_info: list[dict[str, Any]],
    ) -> Path:
        """Save metadata JSON file for a pipeline.

        Creates or updates the _metadata.json file with pipeline information,
        timestamps, and deliverable details.

        Args:
            pipeline_id: The pipeline identifier.
            deliverables_info: List of deliverable information dicts with
                keys: node_type, filename, evaluation_score.

        Returns:
            Path to the saved metadata file.
        """
        self._validate_pipeline_id(pipeline_id)

        # Ensure directory exists
        pipeline_dir = await self._ensure_output_dir(pipeline_id)
        metadata_file = pipeline_dir / "_metadata.json"

        # Build metadata
        now = datetime.now(UTC).isoformat()
        metadata = {
            "pipeline_id": pipeline_id,
            "created_at": now,
            "updated_at": now,
            "deliverables": deliverables_info,
        }

        # Atomic write
        temp_path = metadata_file.with_suffix(".tmp.json")
        try:
            async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                _ = await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))

            _ = temp_path.replace(metadata_file)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise StorageError(
                f"Failed to save metadata: {e}",
                pipeline_id=pipeline_id,
            ) from e

        return metadata_file

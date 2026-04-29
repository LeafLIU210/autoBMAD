"""P1: Deliverable tool tests (H4).

Ensures create_deliverable preserves metadata, avoids overwrites,
and handles non-ASCII titles safely.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from autoBMAD.docuswarm.tools.create_deliverable_sdk import (
    _slugify_filename,
    create_deliverable,
)


class TestSlugifyFilename:
    """T4.1: _slugify_filename must handle edge cases."""

    def test_english_title(self) -> None:
        assert _slugify_filename("Hello World") == "hello-world.md"

    def test_chinese_title_fallback(self) -> None:
        """Pure Chinese title must use fallback, not empty slug."""
        assert _slugify_filename("需求分析", fallback="node-123") == "node-123.md"

    def test_empty_title_with_fallback(self) -> None:
        assert _slugify_filename("!!!", fallback="hash-abc") == "hash-abc.md"

    def test_empty_title_without_fallback(self) -> None:
        assert _slugify_filename("!!!") == "deliverable.md"


class TestCreateDeliverableMetadata:
    """T4.2: create_deliverable must include metadata in result."""

    def test_metadata_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metadata = {"document_index": 1, "document_total": 3, "document_type": "analysis"}
            result = create_deliverable(
                title="Test Deliverable",
                content="# Test\n\nContent here.",
                output_dir=tmpdir,
                metadata=metadata,
            )
            assert result.success is True
            assert result.result is not None
            assert result.result["document_index"] == 1
            assert result.result["document_total"] == 3
            assert result.result["document_type"] == "analysis"

    def test_filename_collision_does_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result1 = create_deliverable(
                title="Same Title",
                content="First version",
                output_dir=tmpdir,
            )
            result2 = create_deliverable(
                title="Same Title",
                content="Second version",
                output_dir=tmpdir,
            )
            assert result1.success is True
            assert result2.success is True
            assert result1.result["file_path"] != result2.result["file_path"]
            # Both files should exist
            assert Path(result1.result["file_path"]).exists()
            assert Path(result2.result["file_path"]).exists()

    def test_chinese_title_creates_valid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_deliverable(
                title="需求分析",
                content="# 需求分析\n\n内容",
                output_dir=tmpdir,
            )
            assert result.success is True
            path = Path(result.result["file_path"])
            assert path.exists()
            assert path.suffix == ".md"
            assert path.name != ".md"

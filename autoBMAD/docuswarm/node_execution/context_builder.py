"""Node Execution Context Builder - Single Context Protocol.

This module provides the NodeExecutionContextBuilder for building unified
NodeExecutionContext instances from node configurations and runtime state.

Based on: P0 Single Context Protocol Implementation Design
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog

from autoBMAD.nodes.loader import NodeLoader

from .contracts import NodeExecutionContext

logger = structlog.get_logger(__name__)

# Constants for reference document resolution
ALLOWED_REF_EXTENSIONS = frozenset([".md", ".txt", ".yaml", ".yml", ".json"])
MAX_DOC_CONTENT_LENGTH = 10000
TRUNCATION_NOTICE = "\n\n[内容已截断]"


class NodeExecutionContextBuilder:
    """Builds unified NodeExecutionContext from node configurations."""

    def __init__(self, loader: NodeLoader | None = None) -> None:
        self.loader = loader or NodeLoader()

    def build(
        self,
        pipeline_id: str,
        node_id: str,
        original_context: dict[str, Any],
        chained_deliverables: list[dict[str, Any]] | None = None,
        shared_context: dict[str, Any] | None = None,
        iteration_feedback: dict[str, Any] | None = None,
        repo_root: Path | None = None,
    ) -> NodeExecutionContext:
        """Build NodeExecutionContext with runtime fields only.

        Args:
            pipeline_id: Pipeline identifier
            node_id: Node identifier
            original_context: Original context from pipeline/prompt
            chained_deliverables: Optional upstream deliverables
            shared_context: Optional shared context across nodes
            iteration_feedback: Optional feedback from previous iteration
            repo_root: Optional repository root path for resolving reference docs
        """
        node_config = self.loader.load(node_id)

        # Resolve reference documents - prioritize cached summary, fallback to disk
        docs_context: list[dict[str, Any]] = []

        # NEW: Prioritize cached summary (injected by PipelineAdapter)
        if "docs_context_summary" in original_context and original_context["docs_context_summary"]:
            docs_context = original_context["docs_context_summary"]
            logger.info(
                "using_cached_docs_summary",
                node_id=node_id,
                count=len(docs_context),
            )
        elif repo_root is not None:
            # Fallback: rare case when no cache available
            docs_context = self._resolve_reference_docs(original_context, node_id, repo_root)
            logger.warning(
                "missing_cached_docs_summary_using_fallback",
                node_id=node_id,
                count=len(docs_context),
            )

        return NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=node_id,
            node_name=node_config.name,
            node_order=node_config.sequence,
            original_context=original_context,
            chained_deliverables=chained_deliverables or [],
            shared_context=shared_context or {},
            iteration_feedback=iteration_feedback,
            docs_context=docs_context,
        )

    def _resolve_reference_docs(
        self,
        original_context: dict[str, Any],
        node_id: str,
        repo_root: Path,
    ) -> list[dict[str, Any]]:
        """Extract and read referenced documents from original_context.

        Search strategy:
        1. Extract filenames from content field (backtick format and bare filenames)
        2. Recursively search in docs/ directory
        3. For same-named files, prefer shallowest path
        4. Truncate content exceeding MAX_DOC_CONTENT_LENGTH

        Args:
            original_context: Original context dictionary
            node_id: Node ID (for logging/permissions)
            repo_root: Repository root path

        Returns:
            List of referenced documents, each with filename, path, content
        """
        content = original_context.get("content", "")
        if not content:
            return []

        # Extract filenames: backtick format `filename.md` and bare filenames
        patterns = [
            r"`([^`]+\.(?:md|txt|yaml|yml|json))`",  # backtick format
            r"\b([\w.-]+\.(?:md|txt|yaml|yml|json))\b",  # bare filename
        ]

        referenced_files: set[str] = set()
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter to only allowed extensions
            for match in matches:
                match_lower = match.lower()
                if any(match_lower.endswith(ext) for ext in ALLOWED_REF_EXTENSIONS):
                    referenced_files.add(match)

        if not referenced_files:
            return []

        # Search in docs/ directory recursively
        docs_dir = repo_root / "docs"
        if not docs_dir.exists():
            return []

        docs_context: list[dict[str, Any]] = []

        for filename in referenced_files:
            # Find all matching files (sorted by path depth, shallow first)
            candidates = sorted(docs_dir.rglob(filename), key=lambda p: len(p.parts))

            for candidate in candidates:
                if not candidate.is_file():
                    continue

                # Check extension is allowed
                if candidate.suffix.lower() not in ALLOWED_REF_EXTENSIONS:
                    continue

                try:
                    file_content = candidate.read_text(encoding="utf-8")

                    # Truncate protection
                    if len(file_content) > MAX_DOC_CONTENT_LENGTH:
                        file_content = file_content[:MAX_DOC_CONTENT_LENGTH] + TRUNCATION_NOTICE

                    docs_context.append(
                        {
                            "filename": filename,
                            "path": candidate.relative_to(repo_root).as_posix(),
                            "content": file_content,
                        }
                    )
                    break  # Found shallowest version, stop

                except (OSError, UnicodeDecodeError):
                    continue  # Read failed, try next

        return docs_context


def create_context_builder(loader: NodeLoader | None = None) -> NodeExecutionContextBuilder:
    """Factory function to create NodeExecutionContextBuilder instance."""
    return NodeExecutionContextBuilder(loader=loader)

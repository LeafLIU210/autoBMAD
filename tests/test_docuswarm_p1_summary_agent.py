"""P1-T3: SummaryAgent context_file Parsing Tests.

Ensures SummaryAgent includes context_file in documents_summarized.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


class TestSummaryAgentIncludesContextFile:
    """T3.1: SummaryAgent must include context_file in referenced_files."""

    def test_summary_agent_extracts_context_file(self, tmp_path: Path) -> None:
        """When subject_context has context_file, _extract_referenced_files must include it."""
        from autoBMAD.docuswarm.agents.summary import SummaryAgent

        agent = SummaryAgent(
            config=MagicMock(),
            session_manager=MagicMock(),
            project_root=tmp_path,
        )

        subject_context = {
            "context_file": "docs/calc-one-plus-one/calc-context.md",
            "content": "calc 1+1",
        }
        files = agent._extract_referenced_files(subject_context)
        assert any("calc-context.md" in f for f in files)


class TestReferencedFilesParsingShared:
    """T3.2: Parsing logic should be shared between SummaryAgent and ContextBuilder."""

    def test_referenced_files_parsing_exists(self) -> None:
        """Both classes should have file extraction methods."""
        from autoBMAD.docuswarm.agents.summary import SummaryAgent
        from autoBMAD.docuswarm.node_execution.context_builder import (
            NodeExecutionContextBuilder,
        )

        assert callable(getattr(NodeExecutionContextBuilder, "_resolve_reference_docs", None))
        assert callable(getattr(SummaryAgent, "_extract_referenced_files", None))

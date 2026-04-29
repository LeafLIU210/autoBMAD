"""P1-T2: CLI Failure State Exposure Tests.

Ensures CLI reports real failure and returns non-zero exit code.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest


class TestCliStartShowsFailedOnSyncFailure:
    """T2.1: CLI start must show failed and return non-zero on failure."""

    def test_cli_start_shows_failed_on_sync_failure(self) -> None:
        """Mock orchestrator returning failed status; CLI must exit non-zero."""
        from click.testing import CliRunner

        from autoBMAD.docuswarm.cli.commands.start import start

        runner = CliRunner()

        with patch(
            "autoBMAD.docuswarm.cli.commands.start.PipelineService"
        ) as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service

            async def mock_start(*args: Any, **kwargs: Any) -> dict[str, Any]:
                return {
                    "pipeline_id": "pipe-123",
                    "status": "failed",
                    "failed_nodes": ["analyst"],
                    "error": {"message": "analyst failed"},
                }

            mock_service.start = mock_start

            # Create a temporary context file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write("# Test context")
                context_file = f.name

            import os

            try:
                result = runner.invoke(start, ["--context", context_file])
                assert result.exit_code != 0
                assert "Pipeline failed" in result.output or "failed" in result.output
            finally:
                os.unlink(context_file)


class TestStartPipelineReturnsStatusDict:
    """T2.2: start_pipeline must return a status dict."""

    @pytest.mark.asyncio
    async def test_start_pipeline_returns_status_dict(self) -> None:
        """Mock graph execution and verify return type."""
        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        orchestrator = HybridOrchestrator(db_path=":memory:")
        # Patch _create_checkpointer to avoid aiosqlite issues
        with patch.object(
            orchestrator, "_create_checkpointer", new_callable=AsyncMock
        ) as mock_cp:
            mock_cp.return_value = MagicMock()
            with patch.object(
                orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock
            ):
                with patch.object(
                    orchestrator._state_manager, "create_pipeline", return_value="pipe-123"
                ):
                    with patch.object(
                        orchestrator._state_manager,
                        "update_pipeline_state",
                        new_callable=AsyncMock,
                    ):
                        with patch(
                            "autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph"
                        ) as mock_graph:
                            mock_graph.return_value.ainvoke = AsyncMock(
                                return_value={
                                    "failed_nodes": ["analyst"],
                                    "error": {"message": "fail"},
                                    "completed_nodes": [],
                                    "deliverables": {},
                                    "current_node": "analyst",
                                }
                            )
                            result = await orchestrator.start_pipeline(
                                {"subject": "test", "content": "x"}
                            )
                            assert isinstance(result, dict)
                            assert "pipeline_id" in result
                            assert "status" in result
                            assert "failed_nodes" in result
                            assert "error" in result


class TestCliDoesNotPrintStartedWhenFailed:
    """T2.3: CLI must not print 'started successfully' when failed."""

    def test_cli_does_not_print_started_when_failed(self) -> None:
        """Output must not contain 'started successfully' or 'completed' on failure."""
        from click.testing import CliRunner

        from autoBMAD.docuswarm.cli.commands.start import start

        runner = CliRunner()

        with patch(
            "autoBMAD.docuswarm.cli.commands.start.PipelineService"
        ) as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service

            async def mock_start(*args: Any, **kwargs: Any) -> dict[str, Any]:
                return {
                    "pipeline_id": "pipe-123",
                    "status": "failed",
                    "failed_nodes": ["analyst"],
                    "error": {"message": "analyst failed"},
                }

            mock_service.start = mock_start

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write("# Test context")
                context_file = f.name

            try:
                result = runner.invoke(start, ["--context", context_file])
                assert "started successfully" not in result.output.lower()
                assert "completed" not in result.output.lower() or "failed" in result.output.lower()
            finally:
                os.unlink(context_file)

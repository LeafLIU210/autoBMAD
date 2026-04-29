"""Pipeline service for CLI commands.

This module provides business logic for pipeline operations.
It separates the CLI interface from the business logic for better testability.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autoBMAD.docuswarm.config import load_config
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.storage.state_manager import StateManager


class PipelineService:
    """Service for pipeline operations.

    This service encapsulates the business logic for pipeline management,
    allowing CLI commands to delegate operations while remaining thin.

    Args:
        db_path: Optional database path. If not provided, uses config default.
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize the pipeline service."""
        config = load_config()
        self._db_path = db_path or str(config.db_path)
        self._state_manager = StateManager(db_path=self._db_path)

    async def start(self, context_file: str) -> dict[str, Any]:
        """Start a new pipeline.

        Args:
            context_file: Path to the context file.

        Returns:
            Dict with pipeline_id, status, failed_nodes, error.

        Raises:
            FileNotFoundError: If context file doesn't exist.
            ValueError: If context file is invalid.
        """
        context_path = Path(context_file)
        if not context_path.exists():
            raise FileNotFoundError(f"Context file not found: {context_file}")

        content = context_path.read_text(encoding="utf-8")
        subject = context_path.stem

        subject_context = {
            "subject": subject,
            "context_file": str(context_path),
            "content": content,
        }

        config = load_config()

        # Create session_manager for LLM validation
        # Use output directory as work_dir for SessionManager
        work_dir = Path(config.output_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        session_manager = SessionManager(work_dir=work_dir)

        orchestrator = HybridOrchestrator(
            db_path=self._db_path,
            api_key=config.api_key,
            base_url=config.base_url,
            session_manager=session_manager,
        )

        try:
            return await orchestrator.start_pipeline(subject_context)
        finally:
            await session_manager.close_all()

    def status(self, pipeline_id: str) -> dict[str, Any] | None:
        """Get pipeline status.

        Args:
            pipeline_id: The pipeline ID.

        Returns:
            Pipeline data or None if not found.
        """
        return self._state_manager.get_pipeline(pipeline_id)

    async def resume(self, pipeline_id: str) -> dict[str, Any]:
        """Resume a pipeline.

        Args:
            pipeline_id: The pipeline ID.

        Returns:
            The pipeline result.
        """
        orchestrator = HybridOrchestrator(db_path=self._db_path)
        return await orchestrator.resume_pipeline(pipeline_id)

    async def restart_from_node(self, pipeline_id: str, node_id: str) -> dict[str, Any]:
        """Restart pipeline from a specific node.

        Args:
            pipeline_id: The pipeline ID.
            node_id: The node ID to restart from.

        Returns:
            The pipeline result.
        """
        orchestrator = HybridOrchestrator(db_path=self._db_path)
        return await orchestrator.restart_from_node(pipeline_id, node_id)

    async def cancel(self, pipeline_id: str) -> bool:
        """Cancel a pipeline.

        Args:
            pipeline_id: The pipeline ID.

        Returns:
            True if cancelled successfully.
        """
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        if pipeline["status"] == "completed":
            raise ValueError(f"Cannot cancel completed pipeline: {pipeline_id}")

        return await self._state_manager.update_pipeline_state(
            pipeline_id=pipeline_id,
            state_update={"status": "cancelled"},
        )

    def list_pipelines(self, status: str | None = None) -> list[dict[str, Any]]:
        """List pipelines.

        Args:
            status: Optional status filter.

        Returns:
            List of pipeline data.
        """
        return self._state_manager.list_pipelines(status=status)

    async def cancel_all(self, status: str | None = None) -> tuple[list[dict[str, Any]], int]:
        """Cancel all pipelines (optionally filtered by status).

        Args:
            status: Optional status filter.

        Returns:
            Tuple of (list of cancellable pipelines, number cancelled).
        """
        # Get all pipelines
        pipelines = self._state_manager.list_pipelines(status=status)

        if not pipelines:
            return [], 0

        # Filter out already cancelled and completed
        cancellable = [p for p in pipelines if p["status"] not in ["cancelled", "completed"]]

        if not cancellable:
            return [], 0

        # Cancel each pipeline
        cancelled_count = 0
        for p in cancellable:
            try:
                await self._state_manager.update_pipeline_state(
                    pipeline_id=p["pipeline_id"],
                    state_update={"status": "cancelled"},
                )
                cancelled_count += 1
            except Exception:
                pass  # Continue with next pipeline

        return cancellable, cancelled_count

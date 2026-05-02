"""Hybrid Orchestrator for pipeline execution - Story 3.5.

This module provides the HybridOrchestrator class that combines:
- LLM-based context validation (Kimi Instant) via ContextValidator
- Rule-based dependency checking
- LangGraph StateGraph with SqliteSaver for checkpoint/resume
"""

from __future__ import annotations

import asyncio
import hashlib
import json as _json
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import structlog

from autoBMAD.docuswarm.agents.summary import SummaryAgent
from autoBMAD.docuswarm.context import ContextValidator
from autoBMAD.docuswarm.exceptions import ContextValidationError, OrchestratorError
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.pipeline.graph import (
    PIPELINE_NODES,
    create_pipeline_graph,
)
from autoBMAD.docuswarm.pipeline.state import (
    CANCELLED,
    COMPLETED,
    FAILED,
    PAUSED,
    RUNNING,
    create_initial_state,
)
from autoBMAD.docuswarm.storage.checkpoints import (
    create_checkpoint_config,
    generate_thread_id,
)
from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.utils.logging import set_log_context

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.checkpoint.sqlite import SqliteSaver

logger = structlog.get_logger(__name__)

# Decision outcomes
DECISION_PROCEED = "proceed"
DECISION_PAUSE = "pause"
DECISION_HALT = "halt"


class DependencyError(OrchestratorError):
    """Raised when dependency checking fails."""

    pass


class PipelineNotFoundError(OrchestratorError):
    """Raised when pipeline is not found."""

    pass


class PipelineAlreadyCompletedError(OrchestratorError):
    """Raised when trying to resume a completed pipeline."""

    pass


class HybridOrchestrator:
    """Hybrid orchestrator combining LLM-based validation with rule-based control.

    This orchestrator manages pipeline execution with:
    - LLM-based context validation using Kimi Instant
    - Rule-based dependency checking
    - LangGraph StateGraph with SqliteSaver for checkpoint/resume
    - Thread isolation for concurrent pipeline execution
    - Session-aware resume for interrupted pipelines (Story 9.3)

    Args:
        db_path: Path to the SQLite database for state persistence.
        checkpointer: Optional SqliteSaver checkpointer. If not provided, creates one.
        session_manager: Optional SessionManager for session resume and LLM calls. If not provided, creates one.
        work_dir: Optional working directory for sessions. Defaults to current directory.

    Example:
        >>> orchestrator = HybridOrchestrator(db_path="checkpoints.db")
        >>> pipeline_id = await orchestrator.start_pipeline(subject_context)
        >>> status = await orchestrator.get_pipeline_status(pipeline_id)
    """

    def __init__(
        self,
        db_path: str | None = None,
        checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
        session_manager: SessionManager | None = None,
        work_dir: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        context_validator: ContextValidator | None = None,
        config: Any | None = None,
    ) -> None:
        """Initialize HybridOrchestrator.

        Args:
            db_path: Path to SQLite database. Defaults to "docuswarm.db".
            checkpointer: Optional checkpointer for LangGraph.
            session_manager: Optional SessionManager for session resume and LLM calls.
            work_dir: Optional working directory for sessions.
            api_key: Optional Kimi API key (from .env or environment).
            base_url: Optional Kimi API base URL (from .env or environment).
            context_validator: Optional ContextValidator for context validation.
                If not provided, creates one with the session_manager.
            config: Optional configuration object for agents.
                If not provided, a default config will be created when needed.
        """
        # Ensure .env is loaded before any SDK operations
        from autoBMAD.docuswarm.config import load_config as _load_config

        _ = _load_config()

        self._db_path = db_path or "docuswarm.db"
        self._checkpointer = checkpointer
        self._session_manager = session_manager
        # Initialize work_dir, default to project_root/output
        if work_dir is None:
            # Calculate project root: navigate up until we find .git or pyproject.toml
            current = Path(__file__).resolve().parent
            project_root = current
            while project_root.parent != project_root:
                if (project_root / ".git").exists() or (project_root / "pyproject.toml").exists():
                    break
                project_root = project_root.parent
            self._work_dir = str(project_root / "output")
        else:
            self._work_dir = work_dir
        self._api_key = api_key
        self._base_url = base_url
        self._config = config

        # Initialize state manager for pipeline metadata
        self._state_manager = StateManager(db_path=self._db_path)

        # Initialize context validator (injected or created)
        if context_validator is not None:
            self._context_validator = context_validator
        else:
            self._context_validator = ContextValidator(session_manager=session_manager)

        logger.info(
            "hybrid_orchestrator_initialized",
            db_path=self._db_path,
            work_dir=self._work_dir,
        )

    @property
    def session_manager(self) -> SessionManager | None:
        """Get the session manager instance."""
        return self._session_manager

    def _determine_final_status(self, result: dict[str, Any]) -> str:
        """Determine pipeline final status from graph result.

        P0-F1: Checks for failed_nodes or error in result to avoid
        falsely marking a pipeline as completed when nodes failed.

        Args:
            result: The state dict returned by graph.ainvoke().

        Returns:
            "completed" if no failures, "failed" otherwise.
        """
        failed_nodes = result.get("failed_nodes", [])
        error = result.get("error")
        if failed_nodes or error:
            return FAILED
        return COMPLETED

    def _get_or_create_session_manager(
        self,
        pipeline_id: str | None = None,
    ) -> SessionManager:
        """Get existing session manager or create a new one.

        Args:
            pipeline_id: Optional pipeline ID for pipeline-specific work_dir.

        Returns:
            SessionManager instance.

        Raises:
            OrchestratorError: If session manager cannot be created.
        """
        # Return cached manager if no pipeline_id specified
        if self._session_manager is not None and pipeline_id is None:
            return self._session_manager

        try:
            if pipeline_id:
                # Pipeline-specific work_dir
                work_dir = Path(self._work_dir) / pipeline_id
            else:
                # Global work_dir (never falls back to cwd)
                work_dir = Path(self._work_dir)

            session_manager = SessionManager(
                work_dir=work_dir,
                config=None,  # Credentials are now read from environment by Config
                db_path=self._state_manager.db_path,  # H1 Fix: 传递数据库路径
            )

            # Only cache global session_manager
            if pipeline_id is None:
                self._session_manager = session_manager

            logger.info(
                "session_manager_created",
                work_dir=str(work_dir),
                pipeline_id=pipeline_id,
            )
            return session_manager
        except Exception as e:
            logger.error("failed_to_create_session_manager", error=str(e))
            raise OrchestratorError(f"Failed to create session manager: {e}") from e

    def _patch_aiosqlite_connection(self, conn: Any) -> None:
        """Add is_alive method for LangGraph compatibility (TD-002).

        LangGraph's AsyncSqliteSaver expects connection to have is_alive()
        method, but aiosqlite doesn't provide it. This method patches
        the connection with a simple implementation.

        FIXME: Track https://github.com/langchain-ai/langgraph/issues/XXX
        Remove this patch when LangGraph adds native aiosqlite support.

        Args:
            conn: The aiosqlite connection to patch.
        """
        if not hasattr(conn, "is_alive"):
            conn.is_alive = lambda: True  # type: ignore[attr-defined]

    async def _create_checkpointer(self) -> Any:
        """Create an AsyncSqliteSaver checkpointer with proper configuration (TD-001).

        Centralizes checkpointer creation to eliminate duplication.
        Includes monkey-patch for LangGraph compatibility.

        Returns:
            Configured AsyncSqliteSaver instance.
        """
        import aiosqlite
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        # Create async connection
        aconn = await aiosqlite.connect(self._db_path)

        # Enable WAL mode for better concurrent access
        await aconn.execute("PRAGMA journal_mode=WAL")
        await aconn.execute("PRAGMA synchronous=NORMAL")

        # Apply monkey-patch for LangGraph compatibility (TD-002)
        self._patch_aiosqlite_connection(aconn)

        return AsyncSqliteSaver(conn=aconn)

    async def _summarize_referenced_documents(
        self,
        subject_context: dict[str, Any],
        repo_root: Path,
        session_manager: SessionManager,
        timeout: int = 120,
    ) -> list[dict[str, Any]]:
        """Run SummaryAgent with timeout protection.

        Generates document summaries for files referenced in subject_context.
        Returns empty list on timeout or error to allow pipeline to continue
        without cached summaries (nodes will use fallback processing).

        Args:
            subject_context: Context information containing document references.
            repo_root: Root directory for file discovery.
            session_manager: SessionManager for LLM interactions.
            timeout: Maximum time in seconds to wait for summary generation.
                Defaults to 120 seconds.

        Returns:
            List of document summary dictionaries, or empty list on failure.
        """
        try:
            # Get or create config for SummaryAgent
            agent_config = self._config
            if agent_config is None:
                from autoBMAD.docuswarm.config import Config

                agent_config = Config()

            # Instantiate SummaryAgent with config, session_manager, and project_root
            summary_agent = SummaryAgent(
                config=agent_config,
                session_manager=session_manager,
                project_root=repo_root,
            )

            # Wrap summarize_context call with asyncio.wait_for() for timeout handling
            result = await asyncio.wait_for(
                summary_agent.summarize_context(subject_context),
                timeout=timeout,
            )

            # F5: Convert DocumentSummary objects to dicts for PipelineState storage
            docs_context_summary = [d.to_dict() for d in result]

            # Structured logging: documents_summarized count and total_tokens
            total_tokens = sum(d.get("llm_tokens_used", 0) for d in docs_context_summary)
            logger.info(
                "documents_summarized",
                count=len(docs_context_summary),
                total_tokens=total_tokens,
            )

            return docs_context_summary

        except TimeoutError:
            logger.warning(
                "summary_generation_timeout",
                timeout_seconds=timeout,
            )
            return []

        except Exception as e:
            logger.error(
                "summary_generation_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            return []

    def _check_dependencies(
        self,
        current_node: str,
        completed_nodes: list[str],
        deliverables: dict[str, dict[str, Any]],
    ) -> bool:
        """Check if dependencies are met for the current node using rule-based logic.

        Dependencies are satisfied when:
        - All previous nodes in the workflow have completed
        - Previous nodes have produced deliverables

        Args:
            current_node: The node to check dependencies for.
            completed_nodes: List of already completed node IDs.
            deliverables: Dictionary of node deliverables.

        Returns:
            True if all dependencies are met, False otherwise.
        """
        logger.info(
            "checking_dependencies",
            current_node=current_node,
            completed_nodes=completed_nodes,
        )

        # Find current node index in workflow
        if current_node not in PIPELINE_NODES:
            logger.warning("unknown_node", node=current_node)
            return False

        current_index = PIPELINE_NODES.index(current_node)

        # Check all previous nodes
        for i in range(current_index):
            required_node = PIPELINE_NODES[i]

            # Check if node is in completed list
            if required_node not in completed_nodes:
                logger.info(
                    "dependency_not_met",
                    required=required_node,
                    reason="node_not_completed",
                )
                return False

            # Check if node has deliverables (optional but recommended)
            if required_node not in deliverables:
                logger.warning(
                    "dependency_warning",
                    required=required_node,
                    reason="no_deliverables",
                )

        logger.info("dependencies_met", current_node=current_node)
        return True

    async def start_pipeline(
        self,
        subject_context: dict[str, Any],
        pipeline_id: str | None = None,
    ) -> dict[str, Any]:
        """Start a new pipeline with validated context.

        This method:
        1. Validates the subject context using LLM
        2. Creates the pipeline in the database
        3. Executes the pipeline using LangGraph

        Args:
            subject_context: Context information about the subject being processed.
            pipeline_id: Optional custom pipeline ID. If not provided, generates one.

        Returns:
            Dict with pipeline_id, status, failed_nodes, error, completed_nodes, deliverables.

        Raises:
            ContextValidationError: If context validation fails.
        """
        # ISSUE-8: Log redacted metadata instead of full subject_context
        subject = subject_context.get("subject", "Untitled")
        context_keys = list(subject_context.keys())
        context_json = _json.dumps(subject_context, sort_keys=True)
        logger.info(
            "starting_pipeline",
            subject=subject,
            context_keys=context_keys,
            context_length=len(context_json),
            context_hash=hashlib.sha256(context_json.encode()).hexdigest()[:16],
        )

        # Step 1: Validate context using LLM (delegates to ContextValidator)
        await self._context_validator.validate_context_with_llm(subject_context)

        # Step 2: Create pipeline in database
        # ISSUE-4: If caller provides pipeline_id and it already exists, reuse it.
        # Otherwise create new (with explicit id if provided).
        if pipeline_id and self._state_manager.get_pipeline(pipeline_id) is not None:
            final_pipeline_id = pipeline_id
        else:
            final_pipeline_id = self._state_manager.create_pipeline(
                subject=subject,
                subject_context=subject_context,
                pipeline_id=pipeline_id,
            )

        # Step 3: Update status to running
        _ = await self._state_manager.update_pipeline_state(
            final_pipeline_id,
            {"status": RUNNING, "current_node": PIPELINE_NODES[0]},  # Start with first node
        )

        # Step 4: Set logging context for this pipeline
        set_log_context(run_id=final_pipeline_id, node_id="orchestrator")

        # Step 4.5: Ensure pipeline output directory exists
        pipeline_work_dir = Path(self._work_dir) / final_pipeline_id
        pipeline_work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "pipeline_work_dir_created",
            path=str(pipeline_work_dir),
            pipeline_id=final_pipeline_id,
        )

        # Step 4.6: Generate document summaries before graph execution (Story 36.3)
        # ISSUE-6: Make summaries optional — catch timeout/failure and continue.
        session_manager = self._get_or_create_session_manager()
        try:
            docs_context_summary = await self._summarize_referenced_documents(
                subject_context=subject_context,
                repo_root=Path(self._work_dir).parent,  # Project root
                session_manager=session_manager,
            )
        except Exception as e:
            logger.warning(
                "summary_failed_skipping",
                pipeline_id=final_pipeline_id,
                error_type=type(e).__name__,
            )
            docs_context_summary = []

        # Sync docs_context_summary to StateManager before graph execution
        current_pipeline = self._state_manager.get_pipeline(final_pipeline_id)
        if current_pipeline:
            state_json = current_pipeline.get("state", {})
            state_json["docs_context_summary"] = docs_context_summary
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                state_json,
            )

        # Step 5: Create and execute the pipeline graph
        try:
            # Generate thread ID from pipeline ID
            thread_id = generate_thread_id(final_pipeline_id)
            config = create_checkpoint_config(thread_id)

            # Create initial state with docs_context_summary (Story 36.3)
            initial_state = create_initial_state(
                final_pipeline_id,
                subject_context,
                docs_context_summary=docs_context_summary,
            )

            # Create pipeline graph with checkpointer
            checkpointer = self._checkpointer
            if checkpointer is None:
                checkpointer = await self._create_checkpointer()

            graph: Runnable[dict[str, Any], dict[str, Any]] = create_pipeline_graph(
                checkpointer=checkpointer,
                session_manager=session_manager,
            )

            # Execute the graph
            result: dict[str, Any] = await graph.ainvoke(initial_state, config)

            # P0-F1: Determine final status based on result, not blindly completed
            final_status = self._determine_final_status(result)
            final_current_node = result.get("current_node", "po")
            # H2 Fix: Persist the FULL result state back to StateManager
            result["status"] = final_status
            result["current_node"] = final_current_node
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                result,
            )

            logger.info(
                "pipeline_completed",
                pipeline_id=final_pipeline_id,
                result=result,
            )

            # P1 Fix: Return full status dict instead of just pipeline_id
            return {
                "pipeline_id": final_pipeline_id,
                "status": final_status,
                "failed_nodes": result.get("failed_nodes", []),
                "error": result.get("error"),
                "completed_nodes": result.get("completed_nodes", []),
                "deliverables": result.get("deliverables", {}),
            }

        except asyncio.CancelledError as e:
            logger.warning(
                "pipeline_cancelled",
                pipeline_id=final_pipeline_id,
                error_type=type(e).__name__,
            )
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                {
                    "status": "cancelled",
                    "error": {"message": str(e), "type": type(e).__name__},
                },
            )
            raise

        except KeyboardInterrupt:
            logger.warning(
                "pipeline_interrupted",
                pipeline_id=final_pipeline_id,
                error_type="KeyboardInterrupt",
            )
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                {
                    "status": "interrupted",
                    "error": {"message": "User interrupted", "type": "KeyboardInterrupt"},
                },
            )
            raise

        except Exception as e:
            logger.error("pipeline_execution_error", error=str(e))
            _ = await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                {"status": "failed"},
            )
            return {
                "pipeline_id": final_pipeline_id,
                "status": FAILED,
                "failed_nodes": [],
                "error": {"message": str(e), "type": type(e).__name__},
                "completed_nodes": [],
                "deliverables": {},
            }
        finally:
            # Close checkpointer connection to prevent process hang
            if checkpointer is not None and hasattr(checkpointer, "conn"):
                try:
                    await checkpointer.conn.close()
                except Exception:
                    pass

    async def resume_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Resume a paused pipeline from its last checkpoint with session recovery.

        This method implements Story 9.3: Pipeline Resume with Session Recovery.
        It retrieves the checkpoint state and attempts to resume the SDK session
        for the last interrupted node. If the session is not found, it falls back
        to restarting the node.

        Args:
            pipeline_id: The ID of the pipeline to resume.

        Returns:
            The final pipeline state after execution.

        Raises:
            PipelineNotFoundError: If pipeline doesn't exist.
            PipelineAlreadyCompletedError: If pipeline is already completed.
        """
        logger.info("resuming_pipeline", pipeline_id=pipeline_id)

        # Set logging context for this pipeline
        set_log_context(run_id=pipeline_id, node_id="orchestrator")

        # Get pipeline from database
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")

        # Check if already completed
        if pipeline["status"] == "completed":
            raise PipelineAlreadyCompletedError(f"Pipeline already completed: {pipeline_id}")

        # Get the current node and session_id from checkpoint state
        checkpoint_state = pipeline.get("state", {})
        last_node = checkpoint_state.get("current_node")
        session_id = checkpoint_state.get("current_node_session_id")

        # Story 37.6: Extract docs_context_summary from checkpoint state for resume
        # This preserves the cached document summary across pipeline resume operations
        docs_context_summary = checkpoint_state.get("docs_context_summary", [])

        # Log warning if docs_context_summary is missing from checkpoint (backward compatibility)
        # Empty list indicates missing or uninitialized summary - context_builder will rebuild from disk
        if not docs_context_summary:
            logger.warning(
                "docs_context_summary_missing_from_checkpoint",
                pipeline_id=pipeline_id,
                fallback_behavior="context_builder will rebuild from disk",
            )
        else:
            logger.info(
                "docs_context_summary_restored_from_checkpoint",
                pipeline_id=pipeline_id,
                summary_count=len(docs_context_summary),
            )

        logger.info(
            "resume_pipeline_checking_session",
            pipeline_id=pipeline_id,
            last_node=last_node,
            session_id=session_id,
        )

        # Update status to running
        await self._state_manager.update_pipeline_state(
            pipeline_id,
            {"status": RUNNING},
        )

        try:
            # Step 1: Attempt SDK session resume if session_id exists
            session_resumed = False
            if session_id and last_node:
                session_resumed = await self._attempt_session_resume(
                    pipeline_id=pipeline_id,
                    session_id=session_id,
                    last_node=last_node,
                )

            # Step 2: Continue with pipeline execution
            # Generate thread ID and config
            thread_id = generate_thread_id(pipeline_id)
            config = create_checkpoint_config(thread_id)

            # Create checkpointer
            checkpointer = self._checkpointer
            if checkpointer is None:
                checkpointer = await self._create_checkpointer()

            # Create pipeline graph
            # Get session_manager for integrated node execution (Story 11.4)
            session_manager = self._get_or_create_session_manager()

            graph: Runnable[dict[str, Any], dict[str, Any]] = create_pipeline_graph(
                checkpointer=checkpointer,
                session_manager=session_manager,
            )

            # Get subject context from checkpoint
            subject_context = checkpoint_state.get("subject_context", {})

            # Create initial state from checkpoint (preserves all progress)
            initial_state = create_initial_state(pipeline_id, subject_context)

            # Restore state from checkpoint
            initial_state["current_node"] = checkpoint_state.get("current_node")
            initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])
            initial_state["deliverables"] = checkpoint_state.get("deliverables", {})
            initial_state["questions"] = checkpoint_state.get("questions", {})
            initial_state["evaluations"] = checkpoint_state.get("evaluations", {})
            initial_state["node_iterations"] = checkpoint_state.get("node_iterations", {})
            initial_state["session_ids"] = checkpoint_state.get("session_ids", {})
            initial_state["session_metadata"] = checkpoint_state.get("session_metadata", {})
            initial_state["current_node_session_id"] = session_id if session_resumed else None
            initial_state["status"] = RUNNING
            # Story 37.6: Restore docs_context_summary from checkpoint to preserve cache across resume
            # This ensures pipeline resume uses the cached summary instead of rebuilding from disk
            initial_state["docs_context_summary"] = docs_context_summary

            logger.info(
                "resume_pipeline_executing",
                pipeline_id=pipeline_id,
                last_node=last_node,
                session_resumed=session_resumed,
                completed_nodes=initial_state["completed_nodes"],
            )

            # Execute from checkpoint
            result: dict[str, Any] = await graph.ainvoke(initial_state, config)

            # P0-F1: Determine final status based on result
            final_status = self._determine_final_status(result)
            await self._state_manager.update_pipeline_state(
                pipeline_id,
                {"status": final_status},
            )

            logger.info(
                "pipeline_resumed",
                pipeline_id=pipeline_id,
                session_resumed=session_resumed,
                result=result,
            )

            return result

        except Exception as e:
            logger.error("pipeline_resume_error", error=str(e))
            await self._state_manager.update_pipeline_state(
                pipeline_id,
                {"status": "failed"},
            )
            raise

    async def restart_from_node(
        self,
        pipeline_id: str,
        node_id: str,
    ) -> dict[str, Any]:
        """Restart pipeline from a specific node, clearing subsequent nodes.

        This method allows restarting from any node in the pipeline, clearing
        all results from that node onwards while preserving deliverables from
        earlier nodes.

        Args:
            pipeline_id: The ID of the pipeline to restart.
            node_id: The node ID to restart from (must be a valid PIPELINE_NODE).

        Returns:
            The final pipeline state after execution.

        Raises:
            PipelineNotFoundError: If pipeline doesn't exist.
            ValueError: If node_id is not a valid pipeline node.
        """
        logger.info("restarting_from_node", pipeline_id=pipeline_id, node_id=node_id)

        # Validate node_id
        if node_id not in PIPELINE_NODES:
            raise ValueError(f"Invalid node_id: {node_id}. Must be one of: {PIPELINE_NODES}")

        # Set logging context for this pipeline
        set_log_context(run_id=pipeline_id, node_id=node_id)

        # Get pipeline from database
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")

        # Get the current checkpoint state
        checkpoint_state = pipeline.get("state", {})
        subject_context = checkpoint_state.get("subject_context", {})

        # Get completed nodes and deliverables from checkpoint
        completed_nodes: list[str] = checkpoint_state.get("completed_nodes", [])
        deliverables: dict[str, Any] = checkpoint_state.get("deliverables", {})
        questions: dict[str, Any] = checkpoint_state.get("questions", {})
        evaluations: dict[str, Any] = checkpoint_state.get("evaluations", {})
        node_iterations: dict[str, int] = checkpoint_state.get("node_iterations", {})

        # Find the index of restart node
        try:
            restart_index = PIPELINE_NODES.index(node_id)
        except ValueError:
            restart_index = 0

        # Clear deliverables from restart node onwards
        nodes_to_clear = PIPELINE_NODES[restart_index:]
        for node in nodes_to_clear:
            if node in deliverables:
                del deliverables[node]
            if node in questions:
                del questions[node]
            if node in evaluations:
                del evaluations[node]

        # Update completed nodes to only include nodes before restart
        new_completed_nodes = [
            n for n in completed_nodes if PIPELINE_NODES.index(n) < restart_index
        ]

        # Update status to running
        await self._state_manager.update_pipeline_state(
            pipeline_id,
            {"status": RUNNING, "current_node": node_id},
        )

        try:
            # Generate thread ID and config
            thread_id = generate_thread_id(pipeline_id)
            config = create_checkpoint_config(thread_id)

            # Create checkpointer
            checkpointer = self._checkpointer
            if checkpointer is None:
                checkpointer = await self._create_checkpointer()

            # Create pipeline graph
            # Get session_manager for integrated node execution (Story 11.4)
            session_manager = self._get_or_create_session_manager()

            graph: Runnable[dict[str, Any], dict[str, Any]] = create_pipeline_graph(
                checkpointer=checkpointer,
                session_manager=session_manager,
            )

            # Create initial state for restart
            initial_state = create_initial_state(pipeline_id, subject_context)

            # Restore state with cleared values
            initial_state["current_node"] = node_id
            initial_state["completed_nodes"] = new_completed_nodes
            initial_state["deliverables"] = deliverables
            initial_state["questions"] = questions
            initial_state["evaluations"] = evaluations
            initial_state["node_iterations"] = node_iterations
            initial_state["status"] = RUNNING

            logger.info(
                "restart_from_node_executing",
                pipeline_id=pipeline_id,
                node_id=node_id,
                completed_nodes=new_completed_nodes,
                cleared_nodes=nodes_to_clear,
            )

            # Execute from restart node
            result: dict[str, Any] = await graph.ainvoke(initial_state, config)

            # P0-F1: Determine final status based on result
            final_status = self._determine_final_status(result)
            await self._state_manager.update_pipeline_state(
                pipeline_id,
                {"status": final_status},
            )

            logger.info(
                "pipeline_restarted_from_node",
                pipeline_id=pipeline_id,
                node_id=node_id,
                result=result,
            )

            return result

        except Exception as e:
            logger.error("pipeline_restart_from_node_error", error=str(e))
            await self._state_manager.update_pipeline_state(
                pipeline_id,
                {"status": "failed"},
            )
            raise

    async def _attempt_session_resume(
        self,
        pipeline_id: str,
        session_id: str,
        last_node: str,
    ) -> bool:
        """Attempt to resume the SDK session for the interrupted node.

        Args:
            pipeline_id: The pipeline ID.
            session_id: The session ID to resume.
            last_node: The last node that was executing.

        Returns:
            True if session was successfully resumed, False otherwise.
        """
        logger.info(
            "attempting_session_resume",
            pipeline_id=pipeline_id,
            session_id=session_id,
            last_node=last_node,
        )

        try:
            # Get or create session manager
            session_manager = self._get_or_create_session_manager()

            # Attempt to resume the session
            session = await session_manager.resume_session(session_id=session_id)

            if session is not None:
                logger.info(
                    "session_resume_success",
                    pipeline_id=pipeline_id,
                    session_id=session_id,
                    last_node=last_node,
                    resumed_session_id=session.id,
                )
                return True
            else:
                logger.warning(
                    "session_not_found_will_restart",
                    pipeline_id=pipeline_id,
                    session_id=session_id,
                    last_node=last_node,
                )
                return False

        except Exception as e:
            logger.warning(
                "session_resume_failed_will_restart",
                pipeline_id=pipeline_id,
                session_id=session_id,
                last_node=last_node,
                error=str(e),
            )
            return False

    async def _restart_node(
        self,
        pipeline_id: str,
        node_id: str,
        checkpoint_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Restart a node from its last checkpoint when session resume fails.

        This is the fallback method when the SDK session is not found.
        It restarts the node execution from the last checkpoint state.

        Args:
            pipeline_id: The pipeline ID.
            node_id: The node ID to restart.
            checkpoint_state: The checkpoint state to restart from.

        Returns:
            The result of the restarted node execution.
        """
        logger.info(
            "restarting_node",
            pipeline_id=pipeline_id,
            node_id=node_id,
        )

        # Generate thread ID and config
        thread_id = generate_thread_id(pipeline_id)
        config = create_checkpoint_config(thread_id)

        # Create checkpointer
        checkpointer = self._checkpointer
        if checkpointer is None:
            checkpointer = await self._create_checkpointer()

        # Create pipeline graph
        # Get session_manager for integrated node execution (Story 11.4)
        session_manager = self._get_or_create_session_manager()

        graph: Runnable[dict[str, Any], dict[str, Any]] = create_pipeline_graph(
            checkpointer=checkpointer,
            session_manager=session_manager,
        )

        # Get subject context
        subject_context = checkpoint_state.get("subject_context", {})

        # Create initial state from checkpoint
        initial_state = create_initial_state(pipeline_id, subject_context)

        # Restore state (without session_id since we're restarting)
        initial_state["current_node"] = checkpoint_state.get("current_node")
        initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])
        initial_state["deliverables"] = checkpoint_state.get("deliverables", {})
        initial_state["questions"] = checkpoint_state.get("questions", {})
        initial_state["evaluations"] = checkpoint_state.get("evaluations", {})
        initial_state["node_iterations"] = checkpoint_state.get("node_iterations", {})
        initial_state["session_ids"] = checkpoint_state.get("session_ids", {})
        initial_state["session_metadata"] = checkpoint_state.get("session_metadata", {})
        initial_state["current_node_session_id"] = None  # Clear session_id for restart
        initial_state["status"] = RUNNING

        logger.info(
            "node_restarting",
            pipeline_id=pipeline_id,
            node_id=node_id,
        )

        # Execute from checkpoint
        result: dict[str, Any] = await graph.ainvoke(initial_state, config)

        logger.info(
            "node_restarted",
            pipeline_id=pipeline_id,
            node_id=node_id,
        )

        return result

    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Pause a running pipeline, preserving its state.

        Args:
            pipeline_id: The ID of the pipeline to pause.

        Returns:
            True if pause was successful.

        Raises:
            PipelineNotFoundError: If pipeline doesn't exist.
        """
        logger.info("pausing_pipeline", pipeline_id=pipeline_id)

        # Verify pipeline exists
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")

        # Update status to paused
        await self._state_manager.update_pipeline_state(
            pipeline_id,
            {"status": PAUSED},
        )

        logger.info("pipeline_paused", pipeline_id=pipeline_id)
        return True

    async def cancel_current_node(
        self,
        pipeline_id: str,
        cancellation_reason: str = "user_request",
    ) -> bool:
        """Cancel the currently running node in a pipeline.

        This method implements Story 9.4: Native Cancellation Integration.
        It retrieves the active session for the current node and calls session.cancel()
        to trigger the RunCancelled exception in the agent execution.

        Args:
            pipeline_id: The ID of the pipeline to cancel.
            cancellation_reason: Reason for cancellation (user_request, timeout, error).

        Returns:
            True if cancellation was successful, False if no active session found.

        Raises:
            PipelineNotFoundError: If pipeline doesn't exist.
        """
        logger.info(
            "canceling_pipeline",
            pipeline_id=pipeline_id,
            reason=cancellation_reason,
        )

        # Get pipeline from database
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")

        # Get the current node and session_id from state
        state = pipeline.get("state", {})
        current_node = state.get("current_node")
        session_id = state.get("current_node_session_id")

        if not current_node:
            logger.warning(
                "cancel_no_current_node",
                pipeline_id=pipeline_id,
            )
            return False

        if not session_id:
            logger.warning(
                "cancel_no_session_id",
                pipeline_id=pipeline_id,
                current_node=current_node,
            )
            return False

        # Get session manager
        session_manager = self._get_or_create_session_manager()

        # Get the active session
        session = session_manager.get_active(session_id)

        if session is None:
            logger.warning(
                "cancel_session_not_active",
                pipeline_id=pipeline_id,
                session_id=session_id,
            )
            return False

        # Cancel the session - this triggers RunCancelled in agent execution
        # Type cast: we've already verified session is not None above
        try:
            await cast(Any, session).cancel()
            logger.info(
                "cancel_session_called",
                pipeline_id=pipeline_id,
                session_id=session_id,
                current_node=current_node,
            )
        except Exception as e:
            logger.error(
                "cancel_session_error",
                pipeline_id=pipeline_id,
                session_id=session_id,
                error=str(e),
            )
            return False

        # Update pipeline status to CANCELLED
        await self._state_manager.update_pipeline_state(
            pipeline_id,
            {
                "status": CANCELLED,
                "current_node": current_node,
            },  # Preserve current_node for debugging
        )

        logger.info(
            "pipeline_cancelled",
            pipeline_id=pipeline_id,
            current_node=current_node,
            reason=cancellation_reason,
        )

        return True

    async def get_pipeline_status(self, pipeline_id: str) -> dict[str, Any]:
        """Get the current status of a pipeline.

        Args:
            pipeline_id: The ID of the pipeline to query.

        Returns:
            Dictionary with pipeline status information.

        Raises:
            PipelineNotFoundError: If pipeline doesn't exist.
        """
        logger.info("getting_pipeline_status", pipeline_id=pipeline_id)

        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")

        return {
            "pipeline_id": pipeline["pipeline_id"],
            "subject": pipeline["subject"],
            "status": pipeline["status"],
            "current_node": pipeline.get("current_node"),
            "state": pipeline.get("state", {}),
            "created_at": pipeline.get("created_at"),
            "updated_at": pipeline.get("updated_at"),
        }

    async def close(self) -> None:
        """Close the orchestrator and cleanup resources."""
        if self._session_manager:
            await self._session_manager.close_all()
        logger.info("orchestrator_closed")


__all__ = [
    "HybridOrchestrator",
    "OrchestratorError",
    "ContextValidationError",
    "DependencyError",
    "PipelineNotFoundError",
    "PipelineAlreadyCompletedError",
    "DECISION_PROCEED",
    "DECISION_PAUSE",
    "DECISION_HALT",
]

"""P0: Graph state transition tests (C5 + C1).

Ensures blocked/running/needs_revision nodes are NOT added to completed_nodes,
and that async conditional routing works correctly.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
from autoBMAD.docuswarm.pipeline.state import (
    COMPLETED,
    FAILED,
    PIPELINE_NODES,
    create_initial_state,
)


class TestGraphBlockedNodeIsFailedNotCompleted:
    """T5.1: BLOCKED node must be in failed_nodes, NOT completed_nodes."""

    @pytest.mark.asyncio
    async def test_blocked_node_is_failed_not_completed(self) -> None:
        """First node returns BLOCKED; must appear in failed_nodes only."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)

        def fake_create_node_executor(node_id: str, session_manager: Any) -> Any:
            async def executor(state: dict[str, Any]) -> dict[str, Any]:
                new_state = dict(state)
                if node_id == "analyst":
                    new_state["status"] = "blocked"
                    new_state["evaluation"] = {"verdict": "BLOCKED", "alignment_score": 0.3}
                else:
                    new_state["deliverable"] = {"content": f"FAKE_{node_id}"}
                    new_state["evaluation"] = {"verdict": "APPROVED"}
                    new_state["status"] = "completed"
                return new_state
            return executor

        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            side_effect=fake_create_node_executor,
        ):
            graph = create_pipeline_graph(
                compile_graph=True,
                session_manager=mock_session,
            )
            initial_state = create_initial_state("fake-pipe", {"content": "test"})
            result = await graph.ainvoke(initial_state, {"configurable": {"thread_id": "fake-pipe"}})
            assert "analyst" in result.get("failed_nodes", [])
            assert "analyst" not in result.get("completed_nodes", [])


class TestGraphRunningNodeIsNotCompleted:
    """T5.2: RUNNING (needs_revision) node must NOT be in completed_nodes."""

    @pytest.mark.asyncio
    async def test_needs_revision_node_is_not_completed(self) -> None:
        """First node returns NEEDS_REVISION; must NOT be in completed_nodes."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)

        def fake_create_node_executor(node_id: str, session_manager: Any) -> Any:
            async def executor(state: dict[str, Any]) -> dict[str, Any]:
                new_state = dict(state)
                if node_id == "analyst":
                    new_state["status"] = "running"
                    new_state["evaluation"] = {"verdict": "NEEDS_REVISION", "alignment_score": 0.6}
                else:
                    new_state["deliverable"] = {"content": f"FAKE_{node_id}"}
                    new_state["evaluation"] = {"verdict": "APPROVED"}
                    new_state["status"] = "completed"
                return new_state
            return executor

        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            side_effect=fake_create_node_executor,
        ):
            graph = create_pipeline_graph(
                compile_graph=True,
                session_manager=mock_session,
            )
            initial_state = create_initial_state("fake-pipe", {"content": "test"})
            result = await graph.ainvoke(initial_state, {"configurable": {"thread_id": "fake-pipe"}})
            assert "analyst" not in result.get("completed_nodes", [])

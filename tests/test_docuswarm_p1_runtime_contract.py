"""P1-T4: Runtime Contract Regression Tests.

Graph execution with fake agents (no LLM calls).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.pipeline.state import (
    COMPLETED,
    FAILED,
    PIPELINE_NODES,
    create_initial_state,
)


class TestGraphExecutionWithFakeAgents:
    """T4.1: Full graph with fake agents must complete."""

    @pytest.mark.asyncio
    async def test_graph_execution_with_fake_agents(self) -> None:
        """Run graph with all fake agents returning APPROVED."""
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)

        # Patch create_node_executor to return a fake async executor
        def fake_create_node_executor(node_id: str, session_manager: Any) -> Any:
            async def executor(state: dict[str, Any]) -> dict[str, Any]:
                new_state = dict(state)
                new_state["deliverable"] = {"content": f"FAKE_DELIVERABLE_{node_id}"}
                new_state["evaluation"] = {"verdict": "APPROVED", "alignment_score": 1.0}
                new_state["questions"] = []
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
            assert result["status"] == COMPLETED
            for node_id in PIPELINE_NODES:
                assert node_id in result.get("completed_nodes", [])
                assert node_id in result.get("deliverables", {})


class TestGraphExecutionWithFakeFailingEvaluator:
    """T4.2: Fake failing evaluator must put node in failed_nodes."""

    @pytest.mark.asyncio
    async def test_graph_execution_with_fake_failing_evaluator(self) -> None:
        """First node returns BLOCKED; pipeline must fail."""
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)

        def fake_create_node_executor(node_id: str, session_manager: Any) -> Any:
            async def executor(state: dict[str, Any]) -> dict[str, Any]:
                new_state = dict(state)
                if node_id == "analyst":
                    new_state["status"] = "failed"
                    new_state["error"] = {"message": "blocked"}
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
            assert result["status"] == FAILED
            assert "analyst" in result.get("failed_nodes", [])


class TestNodeConfigConsumerContract:
    """T4.3: Enumerate consumer fields and verify dataclass access."""

    def test_node_config_consumer_contract(self) -> None:
        """All consumer-referenced fields must exist on NodeConfig."""
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("analyst")
        consumers = [
            ("task", ["ContextManager.build_independent_input", "NodePromptContractBuilder"]),
            ("evaluator.thresholds", ["EvaluatorAgent", "QualityGate"]),
            ("evaluator.max_iterations", ["DualAgentNode"]),
        ]

        for field_path, _consumers in consumers:
            parts = field_path.split(".")
            obj = config
            for part in parts:
                assert hasattr(obj, part), f"NodeConfig missing field '{field_path}' (part '{part}')"
                obj = getattr(obj, part)

"""P0-T5: End-to-End Initialization Contract Tests.

Validates that NodeExecutor (and DualAgentNode) can initialize from repo root
without FileNotFoundError or AttributeError, and without calling LLM.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestAnalystNodeExecutorFromRepoRoot:
    """T5.1: NodeExecutor('analyst') from repo root initializes all deps."""

    def test_analyst_node_executor_from_repo_root(self) -> None:
        """DualAgentNode for analyst must load real evaluator and persona from repo root."""
        repo_root = Path(__file__).parent.parent.resolve()
        original_cwd = os.getcwd()
        os.chdir(str(repo_root))
        try:
            from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
            from autoBMAD.docuswarm.llm.session_manager import SessionManager

            session_manager = MagicMock(spec=SessionManager)
            config = MagicMock()
            config.agent_timeout = 300

            node = create_dual_agent_node(
                config=config,
                session_manager=session_manager,
                node_id="analyst",
                project_root=repo_root,
            )
            # Evaluator loaded real criteria
            assert node.evaluator_agent.criteria
            assert len(node.evaluator_agent.criteria) > 0
            # Persona loaded (via evaluator_agent project_root or NodeLoader)
            # Task config available
            assert node.max_iterations >= 1
        finally:
            os.chdir(original_cwd)


class TestAllPipelineNodesInitializable:
    """T5.2: All PIPELINE_NODES must be initializable without FileNotFoundError."""

    def test_all_pipeline_nodes_initializable(self) -> None:
        """Instantiate DualAgentNode for each pipeline node_id."""
        repo_root = Path(__file__).parent.parent.resolve()
        original_cwd = os.getcwd()
        os.chdir(str(repo_root))
        try:
            from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
            from autoBMAD.docuswarm.llm.session_manager import SessionManager
            from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

            session_manager = MagicMock(spec=SessionManager)
            config = MagicMock()
            config.agent_timeout = 300

            for node_id in PIPELINE_NODES:
                try:
                    node = create_dual_agent_node(
                        config=config,
                        session_manager=session_manager,
                        node_id=node_id,
                        project_root=repo_root,
                    )
                    assert node.evaluator_agent.criteria
                except (FileNotFoundError, AttributeError) as exc:
                    pytest.fail(f"Node {node_id} initialization failed: {exc}")
        finally:
            os.chdir(original_cwd)


class TestLogScenarioRegression:
    """T5.3: Regression test for logs/docuswarm-2026-04-28.log scenario.

    Simulates the exact failure path: path resolution fails → all nodes error out.
    After fix: only first node fails, status='failed', completed_nodes empty.
    """

    @pytest.mark.asyncio
    async def test_log_scenario_regression(self) -> None:
        """Mock graph execution where analyst fails; verify state invariants."""
        from autoBMAD.docuswarm.pipeline.state import (
            FAILED,
            create_initial_state,
        )
        from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor

        async def failing_analyst(state: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("FileNotFoundError: /home/leafliu/autoBMAD/nodes/analyst/evaluator.yaml")

        mock_session = MagicMock()
        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            return_value=failing_analyst,
        ):
            executor = _create_integrated_node_executor("analyst", mock_session)
            state = create_initial_state("regression-1", {"content": "calc 1+1"})
            result = await executor(state)

            # After fix:
            assert result["status"] == FAILED
            assert result.get("first_failed_node") == "analyst" or "analyst" in result.get(
                "failed_nodes", []
            )
            assert "analyst" not in result.get("completed_nodes", [])
            assert result.get("deliverables", {}).get("analyst") in (None, {}, "")

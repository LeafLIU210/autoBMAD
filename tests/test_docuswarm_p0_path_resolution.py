"""P0-T1: Path Resolution Unified Tests.

Tests that loaders resolve paths correctly from repo root and do not
implicitly fall back to Path.cwd().
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestCriteriaLoaderFromRepoRoot:
    """T1.1: CriteriaLoader must find files from repo root."""

    def test_criteria_loader_from_repo_root_fails_before_fix(self, repo_root: Path) -> None:
        """Before fix: load_criteria from repo root raises FileNotFoundError.

        After fix: succeeds and returns criteria dict.
        """
        from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import (
            load_criteria,
        )

        # repo_root points to /home/leafliu/autoBMAD
        # File lives at autoBMAD/nodes/analyst/evaluator.yaml
        # If CriteriaLoader still appends 'nodes' to repo_root it will fail.
        try:
            result = load_criteria("analyst", project_root=repo_root)
            # After fix path
            assert result["node_id"] == "analyst"
            assert len(result["criteria"]) > 0
            assert "thresholds" in result
        except FileNotFoundError as exc:
            pytest.fail(
                f"CriteriaLoader still cannot resolve from repo_root: {exc}"
            )


class TestPersonaLoaderFromRepoRoot:
    """T1.2: PersonaLoader must return real persona from repo root."""

    def test_persona_loader_from_repo_root_returns_real_persona(
        self, repo_root: Path
    ) -> None:
        """PersonaLoader.load from repo root must return the real analyst persona."""
        from autoBMAD.docuswarm.agents.persona import PersonaLoader

        persona = PersonaLoader.load("analyst", project_root=repo_root)
        assert persona.name == "Analyst"
        assert "Data Analyst" in persona.role or "Analyst" in persona.role


class TestNodeExecutorInitialization:
    """T1.3: NodeExecutor initialization must load real evaluator and persona."""

    def test_node_executor_initialization_loads_real_evaluator_and_persona(
        self, repo_root: Path
    ) -> None:
        """create_node_executor('analyst') from repo root must initialize without FileNotFoundError."""
        import os

        original_cwd = os.getcwd()
        os.chdir(str(repo_root))
        try:
            from autoBMAD.docuswarm.node_execution.executor import create_node_executor
            from autoBMAD.docuswarm.llm.session_manager import SessionManager

            session_manager = MagicMock(spec=SessionManager)
            executor = create_node_executor("analyst", session_manager)
            assert callable(executor)
        finally:
            os.chdir(original_cwd)

    def test_dual_agent_node_from_repo_root_loads_real_persona_and_evaluator(
        self, repo_root: Path
    ) -> None:
        """create_dual_agent_node from repo root must not raise FileNotFoundError."""
        import os

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
            assert node.evaluator_agent.criteria is not None
            assert len(node.evaluator_agent.criteria) > 0
            assert node.evaluator_agent.approval_threshold == 0.70
            assert node.evaluator_agent.blocked_threshold == 0.50
        finally:
            os.chdir(original_cwd)


class TestNoImplicitPathFallback:
    """T1.4: Production code must not silently fall back to Path.cwd().

    After P2 convergence, loaders delegate to NodeLoader which resolves paths
    based on module location, not cwd. Calling without project_root must succeed.
    """

    def test_criteria_loader_without_project_root_uses_node_loader(self) -> None:
        """Calling load_criteria without project_root must succeed via NodeLoader."""
        from unittest.mock import patch

        from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import (
            load_criteria,
        )

        with patch("autoBMAD.nodes.loader.NodeLoader.load") as mock_load:
            mock_evaluator = MagicMock()
            mock_evaluator.criteria = [
                {"name": "quality", "description": "Quality", "weight": 1.0}
            ]
            mock_evaluator.thresholds = {"approval": 0.7, "escalation": 0.5}
            mock_node_config = MagicMock()
            mock_node_config.evaluator = mock_evaluator
            mock_load.return_value = mock_node_config

            result = load_criteria("analyst")
            mock_load.assert_called_once_with("analyst")
            assert result["node_id"] == "analyst"

    def test_persona_loader_without_project_root_uses_node_loader(self) -> None:
        """Calling PersonaLoader.load without project_root must succeed via NodeLoader."""
        from unittest.mock import patch

        from autoBMAD.docuswarm.agents.persona import PersonaLoader

        PersonaLoader.clear_cache()
        with patch("autoBMAD.nodes.loader.NodeLoader.load") as mock_load:
            mock_load.return_value = MagicMock(
                persona={
                    "name": "Analyst",
                    "role": "Data Analyst",
                    "identity": "You are an analyst.",
                    "expertise": [],
                    "principles": [],
                }
            )
            persona = PersonaLoader.load("analyst")
            mock_load.assert_called_once_with("analyst")
            assert persona.name == "Analyst"

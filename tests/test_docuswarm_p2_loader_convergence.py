"""P2-T1: Loader Convergence & Single Source of Truth Tests.

Ensures PersonaLoader and CriteriaLoader delegate to NodeLoader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestPersonaLoaderUsesNodeLoader:
    """T1.1: PersonaLoader.load must internally call NodeLoader.load."""

    def test_persona_loader_uses_node_loader(self) -> None:
        """Mock NodeLoader.load and verify PersonaLoader calls it."""
        from autoBMAD.docuswarm.agents.persona import PersonaLoader

        PersonaLoader.clear_cache()
        with patch("autoBMAD.nodes.loader.NodeLoader.load") as mock_load:
            mock_load.return_value = MagicMock(
                persona={
                    "name": "Test",
                    "role": "Role",
                    "identity": "ID",
                    "expertise": [],
                    "principles": [],
                }
            )
            persona = PersonaLoader.load("analyst")
            mock_load.assert_called_once_with("analyst")
            assert persona.name == "Test"


class TestCriteriaLoaderUsesNodeLoader:
    """T1.2: CriteriaLoader.load must internally call NodeLoader.load."""

    def test_criteria_loader_uses_node_loader(self) -> None:
        """Mock NodeLoader.load and verify CriteriaLoader calls it."""
        from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import (
            CriteriaLoader,
        )

        with patch("autoBMAD.nodes.loader.NodeLoader.load") as mock_load:
            mock_evaluator = MagicMock()
            mock_evaluator.criteria = [
                {"name": "quality", "description": "Q", "weight": 1.0}
            ]
            mock_evaluator.thresholds = {"approval": 0.7, "escalation": 0.5}
            mock_load.return_value = MagicMock(evaluator=mock_evaluator)

            loader = CriteriaLoader()
            result = loader.load("analyst")
            mock_load.assert_called_once_with("analyst")
            assert result["node_id"] == "analyst"


class TestNoDuplicatePathJoinLogic:
    """T1.3: Only NodeLoader should contain 'nodes' / node_id path logic."""

    def test_no_duplicate_path_join_logic(self) -> None:
        """Search source for Path(...) / 'nodes' / node_id outside NodeLoader."""
        import ast
        import inspect

        from autoBMAD.nodes.loader import NodeLoader

        # NodeLoader is allowed to have the logic
        node_loader_source = inspect.getsource(NodeLoader)
        assert '"nodes"' in node_loader_source or "'nodes'" in node_loader_source

        # PersonaLoader and CriteriaLoader should NOT directly join 'nodes' path
        from autoBMAD.docuswarm.agents.persona import PersonaLoader
        from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import (
            CriteriaLoader,
        )

        persona_source = inspect.getsource(PersonaLoader)
        criteria_source = inspect.getsource(CriteriaLoader)

        # After fix, they should not contain '/ "nodes"' or "/ 'nodes'" path joins
        # (They may still contain the string 'nodes' in docstrings/comments)
        # We check for the specific pattern: Path(...) / "nodes"
        assert ' / "nodes"' not in persona_source
        assert " / 'nodes'" not in persona_source
        assert ' / "nodes"' not in criteria_source
        assert " / 'nodes'" not in criteria_source

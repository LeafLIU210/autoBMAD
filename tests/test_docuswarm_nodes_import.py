"""Test that autoBMAD.docuswarm.nodes and submodules import successfully."""

from __future__ import annotations

import pytest


class TestDocuswarmNodesImportChain:
    """Verify the import chain from orchestrator down to dual_agent is unblocked."""

    def test_docuswarm_nodes_package_imports(self) -> None:
        """The __init__.py must not raise on import."""
        import autoBMAD.docuswarm.nodes as nodes_pkg

        assert hasattr(nodes_pkg, "DualAgentNode")
        assert hasattr(nodes_pkg, "NodeResult")
        assert hasattr(nodes_pkg, "create_dual_agent_node")
        assert hasattr(nodes_pkg, "IterationController")
        assert hasattr(nodes_pkg, "NodeConfig")
        assert hasattr(nodes_pkg, "NodeLoader")

    def test_dual_agent_direct_import(self) -> None:
        from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node

        assert callable(create_dual_agent_node)

    def test_iteration_direct_import(self) -> None:
        from autoBMAD.docuswarm.nodes.iteration import IterationController

        assert IterationController is not None

    def test_executor_imports_dual_agent(self) -> None:
        from autoBMAD.docuswarm.node_execution.executor import create_node_executor

        assert callable(create_node_executor)

    def test_graph_uses_integrated_executor(self) -> None:
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph

        assert callable(create_pipeline_graph)

    def test_permissions_reexport(self) -> None:
        from autoBMAD.docuswarm.context.permissions import (
            NodeFilePermissions,
            NodeSearchPermissions,
            NodeToolPermissions,
        )

        assert NodeFilePermissions is not None
        assert NodeSearchPermissions is not None
        assert NodeToolPermissions is not None

    def test_tool_filter_imports(self) -> None:
        from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

        assert NodeToolFilter is not None

    def test_session_manager_imports(self) -> None:
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        assert SessionManager is not None

    def test_independent_agent_imports(self) -> None:
        from autoBMAD.docuswarm.agents.independent import IndependentAgent

        assert IndependentAgent is not None

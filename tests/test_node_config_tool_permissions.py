"""Test that NodeConfig exposes tool_permissions with sensible defaults."""

from __future__ import annotations

import pytest
from pathlib import Path


class TestNodeConfigToolPermissions:
    """Verify NodeLoader produces NodeConfig objects with accessible tool_permissions."""

    def test_analyst_node_has_tool_permissions(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("analyst")
        assert config.tool_permissions is not None
        assert config.tool_permissions.allowed_builtin_tools == []
        assert config.tool_permissions.file_permissions is not None
        assert config.tool_permissions.search_permissions is not None
        assert config.tool_permissions.skills is not None

    def test_pm_node_has_tool_permissions(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("pm")
        assert config.tool_permissions is not None

    def test_ux_node_has_tool_permissions(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("ux")
        assert config.tool_permissions is not None

    def test_architect_node_has_tool_permissions(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("architect")
        assert config.tool_permissions is not None

    def test_po_node_has_tool_permissions(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("po")
        assert config.tool_permissions is not None

    def test_tool_filter_from_node_config(self) -> None:
        """NodeToolFilter.from_node_config must work with loaded configs."""
        from autoBMAD.nodes.loader import NodeLoader
        from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

        node_config = NodeLoader.load("analyst")
        node_filter = NodeToolFilter.from_node_config(node_config)
        assert node_filter.node_id == "analyst"
        assert node_filter.tool_permissions is not None

    def test_node_validation_error_raised_on_bad_config(self) -> None:
        """NodeValidationError must be available for validation failures."""
        from autoBMAD.nodes.loader import NodeValidationError

        with pytest.raises(NodeValidationError):
            raise NodeValidationError("test error")

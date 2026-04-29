"""P0: NodeToolPermissions shared_context schema tests (C2).

Ensures NodeToolFilter.get_allowed_tools() does not raise AttributeError
when loaded from default node config.
"""

from __future__ import annotations

import pytest

from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter


class TestNodeToolFilterDefaultPermissions:
    """T2.1: Default node config must not raise on get_allowed_tools."""

    def test_analyst_tool_filter_default_permissions_do_not_raise(self) -> None:
        """NodeToolFilter.from_node_config(NodeLoader.load('analyst')).get_allowed_tools() must not raise."""
        config = NodeLoader.load("analyst")
        filter_obj = NodeToolFilter.from_node_config(config)
        allowed = filter_obj.get_allowed_tools()
        assert isinstance(allowed, list)

    @pytest.mark.parametrize("node_id", ["analyst", "pm", "ux", "architect", "po"])
    def test_all_nodes_tool_filter_default_permissions_do_not_raise(self, node_id: str) -> None:
        """All five nodes must produce allowed tools list without error."""
        config = NodeLoader.load(node_id)
        filter_obj = NodeToolFilter.from_node_config(config)
        allowed = filter_obj.get_allowed_tools()
        assert isinstance(allowed, list)


class TestNodeToolPermissionsSharedContextSchema:
    """T2.2: shared_context field must exist with sensible defaults."""

    def test_default_shared_context_is_disabled(self) -> None:
        """Default node configs have shared_context.enabled=False."""
        config = NodeLoader.load("analyst")
        assert config.tool_permissions is not None
        assert hasattr(config.tool_permissions, "shared_context")
        assert config.tool_permissions.shared_context.enabled is False
        assert config.tool_permissions.shared_context.operations == []
        assert config.tool_permissions.shared_context.allowed_keys == []

    def test_shared_context_can_be_enabled(self) -> None:
        """Manually enabling shared_context must reflect in get_allowed_tools."""
        config = NodeLoader.load("analyst")
        assert config.tool_permissions is not None
        config.tool_permissions.shared_context.enabled = True
        config.tool_permissions.shared_context.operations = ["set", "append"]
        filter_obj = NodeToolFilter.from_node_config(config)
        allowed = filter_obj.get_allowed_tools()
        assert any("update_context" in name for name in allowed)

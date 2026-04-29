"""Test that autoBMAD.nodes.loader exports all required symbols."""

from __future__ import annotations

import pytest


class TestNodesLoaderSymbols:
    """Verify symbol completeness of the canonical nodes.loader module."""

    def test_node_validation_error_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeValidationError

        assert issubclass(NodeValidationError, Exception)
        assert NodeValidationError.__name__ == "NodeValidationError"

    def test_node_config_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeConfig

        assert NodeConfig.__name__ == "NodeConfig"

    def test_node_loader_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeLoader

        assert NodeLoader.__name__ == "NodeLoader"

    def test_node_file_permissions_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeFilePermissions

        assert NodeFilePermissions.__name__ == "NodeFilePermissions"
        inst = NodeFilePermissions()
        assert inst.allowed_read_dirs == []
        assert inst.allowed_write_dirs == []

    def test_node_search_permissions_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeSearchPermissions

        assert NodeSearchPermissions.__name__ == "NodeSearchPermissions"
        inst = NodeSearchPermissions()
        assert inst.search_dirs == []

    def test_node_tool_permissions_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeToolPermissions

        assert NodeToolPermissions.__name__ == "NodeToolPermissions"
        inst = NodeToolPermissions()
        assert inst.allowed_builtin_tools == []
        assert inst.file_permissions is not None
        assert inst.search_permissions is not None
        assert inst.skills is not None

    def test_node_skills_config_exists(self) -> None:
        from autoBMAD.nodes.loader import NodeSkillsConfig

        assert NodeSkillsConfig.__name__ == "NodeSkillsConfig"
        inst = NodeSkillsConfig()
        assert inst.sdk_native is False
        assert inst.whitelist == []
        assert inst.quick_reference_enabled is False

    def test_node_tool_permissions_with_values(self) -> None:
        from autoBMAD.nodes.loader import (
            NodeFilePermissions,
            NodeSearchPermissions,
            NodeSkillsConfig,
            NodeToolPermissions,
        )

        tp = NodeToolPermissions(
            allowed_builtin_tools=["Read", "Glob"],
            file_permissions=NodeFilePermissions(allowed_read_dirs=["docs/"]),
            search_permissions=NodeSearchPermissions(search_dirs=["src/"]),
            skills=NodeSkillsConfig(sdk_native=True, whitelist=["skill1"]),
        )
        assert tp.allowed_builtin_tools == ["Read", "Glob"]
        assert tp.file_permissions.allowed_read_dirs == ["docs/"]
        assert tp.search_permissions.search_dirs == ["src/"]
        assert tp.skills.sdk_native is True
        assert tp.skills.whitelist == ["skill1"]

    def test_all_expected_symbols_importable(self) -> None:
        """Smoke test: import every symbol that production code expects."""
        from autoBMAD.nodes.loader import (
            NodeAgentConfig,
            NodeConfig,
            NodeDeliverableConfig,
            NodeDependenciesConfig,
            NodeEvaluatorConfig,
            NodeFilePermissions,
            NodeLoader,
            NodeQuestionConfig,
            NodeQuestionsConfig,
            NodeSearchPermissions,
            NodeSkillsConfig,
            NodeTaskConfig,
            NodeToolPermissions,
            NodeValidationError,
        )

        assert NodeAgentConfig is not None
        assert NodeConfig is not None
        assert NodeDeliverableConfig is not None
        assert NodeDependenciesConfig is not None
        assert NodeEvaluatorConfig is not None
        assert NodeFilePermissions is not None
        assert NodeLoader is not None
        assert NodeQuestionConfig is not None
        assert NodeQuestionsConfig is not None
        assert NodeSearchPermissions is not None
        assert NodeSkillsConfig is not None
        assert NodeTaskConfig is not None
        assert NodeToolPermissions is not None
        assert NodeValidationError is not None

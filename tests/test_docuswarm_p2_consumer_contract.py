"""P2-T2: NodeConfig Consumer Contract Tests.

Ensures dataclass fields match YAML sources and consumer references.
"""

from __future__ import annotations

from typing import Any

import pytest


class TestAllNodeConfigFieldsHaveYamlSource:
    """T2.1: Every non-optional dataclass field must have YAML source or fallback."""

    def test_all_node_config_fields_have_yaml_source(self) -> None:
        """node.yaml must contain keys for all NodeConfig fields (or loader fallback)."""
        import yaml

        from autoBMAD.nodes.loader import NodeConfig

        # Get dataclass annotations
        annotations = NodeConfig.__annotations__

        # Load a sample node.yaml
        sample_yaml_path = __import__(
            "autoBMAD.nodes.loader", fromlist=["NodeLoader"]
        ).NodeLoader._get_base_path() / "nodes" / "analyst" / "node.yaml"
        yaml_data = yaml.safe_load(sample_yaml_path.read_text(encoding="utf-8"))

        # Fields with defaults or loaded from other files are acceptable
        optional_or_external = {
            "evaluator",  # loaded from evaluator.yaml
            "persona",  # loaded from persona.json
            "tool_permissions",  # built from tools section with defaults
            "task",  # now added to node.yaml
        }

        missing_in_yaml = []
        for field_name in annotations:
            if field_name in optional_or_external:
                continue
            if field_name not in yaml_data:
                missing_in_yaml.append(field_name)

        assert not missing_in_yaml, f"Fields missing in node.yaml: {missing_in_yaml}"


class TestAllConsumerReferencesExistOnDataclass:
    """T2.2: Every consumer attribute access must exist on NodeConfig."""

    def test_consumer_references_exist(self) -> None:
        """Statically verify common consumer access patterns."""
        from autoBMAD.nodes.loader import NodeConfig, NodeLoader

        config = NodeLoader.load("analyst")

        # Common consumer access patterns
        accesses = [
            ("task.name", lambda c: c.task.name),
            ("task.description", lambda c: c.task.description),
            ("evaluator.criteria", lambda c: c.evaluator.criteria),
            ("evaluator.thresholds", lambda c: c.evaluator.thresholds),
            ("evaluator.max_iterations", lambda c: c.evaluator.max_iterations),
            ("deliverable.required_sections", lambda c: c.deliverable.required_sections),
            ("agent.model", lambda c: c.agent.model),
            ("persona", lambda c: c.persona),
            ("tool_permissions.allowed_builtin_tools", lambda c: c.tool_permissions.allowed_builtin_tools),
        ]

        for path, getter in accesses:
            try:
                getter(config)
            except (AttributeError, TypeError) as e:
                pytest.fail(f"Consumer access '{path}' failed: {e}")

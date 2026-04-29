"""P0-T2: NodeConfig Schema Completeness Tests.

Ensures NodeConfig contains task, evaluator.thresholds, evaluator.max_iterations.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml


class TestNodeConfigTaskAttribute:
    """T2.1: NodeConfig must expose task attribute."""

    def test_node_config_has_task_attribute(self, mock_project_root: Any) -> None:
        """Loaded analyst config must have task with non-empty name."""
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("analyst")
        assert hasattr(config, "task"), "NodeConfig missing 'task' attribute"
        assert config.task is not None
        assert config.task.name, "task.name must be non-empty"

    def test_all_pipeline_nodes_have_task(self) -> None:
        """Every pipeline node config must have a task."""
        from autoBMAD.nodes.loader import NodeLoader
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

        for node_id in PIPELINE_NODES:
            config = NodeLoader.load(node_id)
            assert hasattr(config, "task"), f"{node_id}: missing task"
            assert config.task is not None, f"{node_id}: task is None"
            assert config.task.name, f"{node_id}: task.name is empty"


class TestContextManagerBuildIndependentInput:
    """T2.2: build_independent_input must not raise AttributeError on task."""

    def test_context_manager_build_independent_input_does_not_raise_on_task(
        self, mock_project_root: Any
    ) -> None:
        """ContextManager.build_independent_input must work with real NodeConfig."""
        from autoBMAD.docuswarm.context.isolation import ContextManager
        from autoBMAD.docuswarm.node_execution.context_builder import (
            create_context_builder,
        )

        ctx = create_context_builder().build(
            pipeline_id="pipeline-1",
            node_id="analyst",
            original_context={"content": "x"},
            repo_root=mock_project_root,
        )
        result = ContextManager().build_independent_input(ctx)
        assert isinstance(result, dict)
        assert result.get("task_name"), "task_name must be present and non-empty"


class TestNodeEvaluatorConfigFields:
    """T2.3: NodeEvaluatorConfig must have thresholds and max_iterations."""

    def test_node_evaluator_config_has_thresholds_and_max_iterations(self) -> None:
        """Loaded analyst config must have evaluator.thresholds and max_iterations."""
        from autoBMAD.nodes.loader import NodeLoader

        config = NodeLoader.load("analyst")
        assert hasattr(config, "evaluator"), "NodeConfig missing evaluator"
        assert config.evaluator is not None
        assert hasattr(
            config.evaluator, "thresholds"
        ), "NodeEvaluatorConfig missing thresholds"
        assert hasattr(
            config.evaluator, "max_iterations"
        ), "NodeEvaluatorConfig missing max_iterations"
        assert config.evaluator.max_iterations >= 1

    def test_all_pipeline_nodes_have_evaluator_fields(self) -> None:
        """Every pipeline node must have evaluator thresholds and max_iterations."""
        from autoBMAD.nodes.loader import NodeLoader
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

        for node_id in PIPELINE_NODES:
            config = NodeLoader.load(node_id)
            assert config.evaluator is not None, f"{node_id}: missing evaluator"
            assert hasattr(
                config.evaluator, "thresholds"
            ), f"{node_id}: missing thresholds"
            assert hasattr(
                config.evaluator, "max_iterations"
            ), f"{node_id}: missing max_iterations"
            assert config.evaluator.max_iterations >= 1, f"{node_id}: max_iterations < 1"


class TestThresholdsLoadedFromEvaluatorYaml:
    """T2.4: Thresholds in dataclass must match evaluator.yaml."""

    def test_thresholds_loaded_from_evaluator_yaml(self, mock_project_root: Any) -> None:
        """NodeLoader thresholds must match raw evaluator.yaml values."""
        from autoBMAD.nodes.loader import NodeLoader

        evaluator_yaml = yaml.safe_load(
            (mock_project_root / "nodes" / "analyst" / "evaluator.yaml").read_text(
                encoding="utf-8"
            )
        )
        config = NodeLoader.load("analyst")
        yaml_thresholds = evaluator_yaml.get("thresholds", {})
        assert (
            config.evaluator.thresholds.get("approval") == yaml_thresholds.get("approval")
        )
        assert (
            config.evaluator.thresholds.get("escalation")
            == yaml_thresholds.get("escalation")
        )

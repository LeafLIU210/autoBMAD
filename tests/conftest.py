"""Shared fixtures for DocuSwarm TDD test suite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def autoBMAD_root(repo_root: Path) -> Path:
    """Return the autoBMAD package root (where nodes/ lives)."""
    return repo_root / "autoBMAD"


@pytest.fixture
def mock_project_root(autoBMAD_root: Path) -> Path:
    """Project root that points to autoBMAD/ directory (where nodes/ lives)."""
    return autoBMAD_root


@pytest.fixture
def temp_nodes_dir(tmp_path: Path) -> Path:
    """Create a temporary nodes directory with a minimal fake node."""
    nodes_dir = tmp_path / "nodes"
    node_dir = nodes_dir / "test_node"
    node_dir.mkdir(parents=True)

    node_yaml = {
        "node_id": "test_node",
        "name": "Test Node",
        "description": "A test node",
        "sequence": 1,
        "deliverable_type": "test-report",
        "task": {
            "name": "Test Task",
            "description": "Task description",
            "role_supplement": "Role supplement",
        },
        "deliverable": {"required_sections": ["summary"]},
        "agent": {"type": "independent", "model": "sonnet", "temperature": 0.7},
        "questions": [],
        "dependencies": [],
    }
    (node_dir / "node.yaml").write_text(
        "\n".join(f"{k}: {v}" if not isinstance(v, dict) else f"{k}:\n" + "\n".join(f"  {kk}: {vv}" for kk, vv in v.items()) for k, v in node_yaml.items()),
        encoding="utf-8",
    )
    # Actually use yaml dump for correctness
    import yaml
    (node_dir / "node.yaml").write_text(yaml.safe_dump(node_yaml), encoding="utf-8")

    persona = {
        "name": "Test Persona",
        "role": "Test Role",
        "identity": "You are a test agent.",
        "expertise": ["testing"],
        "principles": ["be thorough"],
    }
    (node_dir / "persona.json").write_text(json.dumps(persona), encoding="utf-8")

    evaluator = {
        "criteria": [
            {"name": "quality", "description": "Quality of output", "weight": 1.0}
        ],
        "thresholds": {"approval": 0.7, "escalation": 0.5},
        "max_iterations": 3,
    }
    (node_dir / "evaluator.yaml").write_text(yaml.safe_dump(evaluator), encoding="utf-8")

    return nodes_dir


@pytest.fixture
def fake_node_config(temp_nodes_dir: Path) -> Any:
    """Load the fake node config using NodeLoader with overridden base path."""
    from autoBMAD.nodes.loader import NodeLoader

    NodeLoader.set_base_path(temp_nodes_dir.parent)
    try:
        return NodeLoader.load("test_node")
    finally:
        NodeLoader.set_base_path(None)


@pytest.fixture
def mock_llm() -> MagicMock:
    """Return a mock LLM/session manager."""
    return MagicMock()

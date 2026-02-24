"""Node Configuration Loader - Story 3.2.

This module provides functionality to load node configurations from YAML files
for the 5 pipeline nodes (Analyst, PM, UX, Architect, PO).

Each node has:
- node.yaml: Node-specific configuration (node_id, name, sequence, deliverable_type)
- persona.json: Independent Agent persona configuration
- evaluator.yaml: Evaluator Agent evaluation criteria
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class NodeValidationError(Exception):
    """Raised when node configuration validation fails."""

    pass


@dataclass
class NodeConfig:
    """Configuration for a pipeline node.

    Attributes:
        node_id: Unique identifier for the node (e.g., 'analyst', 'pm')
        name: Human-readable name of the node
        sequence: Execution order (1-5)
        deliverable_type: Type of deliverable this node produces
        persona: Persona configuration for the Independent Agent
        evaluator: Evaluation criteria configuration for the Evaluator Agent
    """

    node_id: str
    name: str
    sequence: int
    deliverable_type: str
    persona: dict[str, Any]
    evaluator: dict[str, Any]

    def __post_init__(self):
        """Validate node configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate required fields are present."""
        if not self.node_id:
            raise NodeValidationError("node_id is required")
        if not self.name:
            raise NodeValidationError("name is required")
        if not (1 <= self.sequence <= 5):
            raise NodeValidationError("sequence must be between 1 and 5")
        if not self.deliverable_type:
            raise NodeValidationError("deliverable_type is required")
        if not self.persona:
            raise NodeValidationError("persona is required")
        if "name" not in self.persona:
            raise NodeValidationError("persona must contain 'name' field")
        if "role" not in self.persona:
            raise NodeValidationError("persona must contain 'role' field")
        if not self.evaluator:
            raise NodeValidationError("evaluator is required")
        if "criteria" not in self.evaluator:
            raise NodeValidationError("evaluator must contain 'criteria' field")


class NodeLoader:
    """Loads and caches node configurations.

    Loads configuration files from nodes/{node_id}/ directory:
    - node.yaml: Node-specific configuration
    - persona.json: Independent Agent persona
    - evaluator.yaml: Evaluator Agent criteria

    Uses caching to avoid repeated file I/O during pipeline execution.
    """

    VALID_NODE_IDS = {"analyst", "pm", "ux", "architect", "po"}

    def __init__(self, nodes_dir: Path | None = None):
        """Initialize the NodeLoader.

        Args:
            nodes_dir: Path to the nodes directory. Defaults to project root / nodes.
        """
        if nodes_dir is None:
            # Get autoBMAD root: loader.py -> nodes/ -> docuswarm/ -> autoBMAD/
            autoBMAD_root = Path(__file__).parent.parent.parent
            nodes_dir = autoBMAD_root / "nodes"

        self._nodes_dir = nodes_dir
        self._cache: dict[str, NodeConfig] = {}

    def _get_node_dir(self, node_id: str) -> Path:
        """Get the directory path for a node.

        Args:
            node_id: The node identifier

        Returns:
            Path to the node directory
        """
        return self._nodes_dir / node_id

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """Load YAML file with safe loading.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        """Load JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON content as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def load(self, node_id: str) -> NodeConfig:
        """Load configuration for a specific node.

        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm', 'ux', 'architect', 'po')

        Returns:
            NodeConfig object with loaded configuration

        Raises:
            FileNotFoundError: If node or configuration files don't exist
            NodeValidationError: If configuration validation fails
        """
        # Check cache first
        if node_id in self._cache:
            return self._cache[node_id]

        node_dir = self._get_node_dir(node_id)

        # Load node.yaml
        node_yaml_path = node_dir / "node.yaml"
        node_data = self._load_yaml(node_yaml_path)

        # Load persona.json
        persona_json_path = node_dir / "persona.json"
        persona_data = self._load_json(persona_json_path)

        # Load evaluator.yaml
        evaluator_yaml_path = node_dir / "evaluator.yaml"
        evaluator_data = self._load_yaml(evaluator_yaml_path)

        # Create NodeConfig
        config = NodeConfig(
            node_id=node_data.get("node_id", node_id),
            name=node_data.get("name", ""),
            sequence=node_data.get("sequence", 0),
            deliverable_type=node_data.get("deliverable_type", ""),
            persona=persona_data,
            evaluator=evaluator_data,
        )

        # Cache the configuration
        self._cache[node_id] = config

        return config

    def load_all(self) -> dict[str, NodeConfig]:
        """Load configurations for all 5 nodes.

        Returns:
            Dictionary mapping node_id to NodeConfig
        """
        configs: dict[str, NodeConfig] = {}
        for node_id in self.VALID_NODE_IDS:
            configs[node_id] = self.load(node_id)
        return configs

    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()

    def get_available_nodes(self) -> list[str]:
        """Get list of available node IDs.

        Returns:
            List of node IDs that have valid configurations
        """
        available: list[str] = []
        for node_id in self.VALID_NODE_IDS:
            node_dir = self._get_node_dir(node_id)
            if node_dir.exists() and (node_dir / "node.yaml").exists():
                available.append(node_id)
        return available

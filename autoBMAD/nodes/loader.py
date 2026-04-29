"""Node Configuration Loader - Story 3.2

This module provides the NodeLoader class for loading node configurations from YAML files.
It also defines all the dataclasses for strongly-typed configuration objects.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Type definitions for nested configuration objects


@dataclass
class NodeAgentConfig:
    """Configuration for the node's agent."""
    type: str
    model: str
    temperature: float
    persona_file: str = "persona.json"


@dataclass
class NodeTaskConfig:
    """Configuration for the node's task (new schema)."""
    name: str
    description: str = ""
    role_supplement: str = ""


@dataclass
class NodeDeliverableConfig:
    """Configuration for the node's deliverable."""
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)


@dataclass
class NodeQuestionConfig:
    """Configuration for a single question."""
    id: str
    text: str
    required: bool


@dataclass
class NodeQuestionsConfig:
    """Configuration for node questions."""
    questions: list[NodeQuestionConfig] = field(default_factory=list)


@dataclass
class NodeDependenciesConfig:
    """Configuration for node dependencies."""
    predecessors: list[str] = field(default_factory=list)


class NodeValidationError(Exception):
    """Raised when node configuration validation fails."""


@dataclass
class NodeFilePermissions:
    """Configuration for file access permissions."""
    allowed_read_dirs: list[str] = field(default_factory=list)
    allowed_write_dirs: list[str] = field(default_factory=list)


@dataclass
class NodeSearchPermissions:
    """Configuration for search permissions."""
    search_dirs: list[str] = field(default_factory=list)


@dataclass
class NodeSkillsConfig:
    """Configuration for skills introduction."""
    sdk_native: bool = False
    whitelist: list[str] = field(default_factory=list)
    quick_reference_enabled: bool = False
    quick_reference_include_descriptions: bool = False


@dataclass
class NodeSharedContextPermissions:
    """Configuration for shared context permissions."""
    enabled: bool = False
    operations: list[str] = field(default_factory=list)
    allowed_keys: list[str] = field(default_factory=list)


@dataclass
class NodeToolPermissions:
    """Configuration for tool permissions."""
    allowed_builtin_tools: list[str] = field(default_factory=list)
    file_permissions: NodeFilePermissions = field(default_factory=NodeFilePermissions)
    search_permissions: NodeSearchPermissions = field(default_factory=NodeSearchPermissions)
    skills: NodeSkillsConfig = field(default_factory=NodeSkillsConfig)
    shared_context: NodeSharedContextPermissions = field(default_factory=NodeSharedContextPermissions)


@dataclass
class NodeEvaluatorConfig:
    """Configuration for the evaluator agent."""
    criteria: list[dict[str, Any]] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)
    max_iterations: int = 3


@dataclass
class NodeConfig:
    """Complete node configuration."""
    node_id: str
    name: str
    description: str
    sequence: int
    deliverable_type: str
    deliverable: NodeDeliverableConfig
    agent: NodeAgentConfig
    questions: NodeQuestionsConfig
    dependencies: NodeDependenciesConfig
    task: NodeTaskConfig | None = None
    evaluator: NodeEvaluatorConfig | None = None
    persona: dict[str, Any] | None = None
    tool_permissions: NodeToolPermissions | None = None


class NodeLoader:
    """Loads node configurations from YAML/JSON files.

    Loads node_id configuration from nodes/{node_id}/ directory containing:
    - node.yaml: Main node configuration
    - persona.json: Independent Agent persona definition
    - evaluator.yaml: Evaluator Agent configuration
    """

    _base_path: Path | None = None

    @classmethod
    def set_base_path(cls, base_path: Path) -> None:
        """Set the base path for node configuration files."""
        cls._base_path = base_path

    @classmethod
    def _get_base_path(cls) -> Path:
        """Get the base path for node configuration files."""
        if cls._base_path is not None:
            return cls._base_path
        # Default to autoBMAD directory (parent of nodes/)
        return Path(__file__).parent.parent

    @classmethod
    def load(cls, node_id: str) -> NodeConfig:
        """Load configuration for a specific node.

        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm', 'ux', 'architect', 'po')

        Returns:
            NodeConfig object with all configuration properties

        Raises:
            FileNotFoundError: If node directory or required files don't exist
            ValueError: If configuration validation fails
        """
        base_path = cls._get_base_path()
        node_dir = base_path / "nodes" / node_id

        if not node_dir.exists():
            raise FileNotFoundError(
                f"Node directory not found: {node_dir}. "
                f"Expected nodes: analyst, pm, ux, architect, po"
            )

        # Load all configuration files
        node_config = cls._load_yaml(node_dir / "node.yaml")
        persona = cls._load_json(node_dir / "persona.json")
        evaluator = cls._load_yaml(node_dir / "evaluator.yaml")

        # Validate required fields
        cls._validate(node_config)

        # Build NodeConfig object
        return cls._build_node_config(node_config, persona, evaluator)

    @classmethod
    def _load_yaml(cls, file_path: Path) -> dict[str, Any]:
        """Load and parse a YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Parsed YAML as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML parsing fails
        """
        import yaml

        try:
            with open(file_path, encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")

    @classmethod
    def _load_json(cls, file_path: Path) -> dict[str, Any]:
        """Load and parse a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON parsing fails
        """
        try:
            with open(file_path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")

    @classmethod
    def _validate(cls, config: dict[str, Any]) -> None:
        """Validate required configuration fields.

        Args:
            config: The node configuration dictionary

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = [
            "node_id", "name", "sequence", "deliverable_type",
            "deliverable", "agent", "questions", "dependencies"
        ]

        for field_name in required_fields:
            if field_name not in config:
                raise ValueError(f"Missing required field: {field_name}")

        # Validate node_id matches
        if "node_id" in config and "node_id" in required_fields:
            pass  # Already checked

        # Validate sequence is an integer
        if not isinstance(config.get("sequence"), int):
            raise ValueError(
                f"Invalid sequence: expected integer, got {type(config.get('sequence')).__name__}"
            )

        # Validate deliverable has required_sections
        deliverable = config.get("deliverable", {})
        if not isinstance(deliverable, dict):
            raise ValueError("deliverable must be a dictionary")
        if "required_sections" not in deliverable:
            raise ValueError("deliverable must have required_sections")

        # Validate agent config
        agent = config.get("agent", {})
        if not isinstance(agent, dict):
            raise ValueError("agent must be a dictionary")
        required_agent_fields = ["type", "model", "temperature"]
        for field_name in required_agent_fields:
            if field_name not in agent:
                raise ValueError(f"agent must have {field_name}")

        # Validate questions is a list
        if not isinstance(config.get("questions"), list):
            raise ValueError("questions must be a list")

        # Validate dependencies is a list
        if not isinstance(config.get("dependencies"), list):
            raise ValueError("dependencies must be a list")

    @classmethod
    def _build_node_config(
        cls,
        config: dict[str, Any],
        persona: dict[str, Any],
        evaluator: dict[str, Any]
    ) -> NodeConfig:
        """Build NodeConfig object from parsed configuration.

        Args:
            config: Parsed node.yaml configuration
            persona: Parsed persona.json configuration
            evaluator: Parsed evaluator.yaml configuration

        Returns:
            Complete NodeConfig object
        """
        # Build agent config
        agent_data = config["agent"]
        agent_config = NodeAgentConfig(
            type=agent_data["type"],
            model=agent_data["model"],
            temperature=agent_data["temperature"]
        )

        # Build deliverable config
        deliverable_data = config["deliverable"]
        deliverable_config = NodeDeliverableConfig(
            type=config["deliverable_type"],
            required_sections=deliverable_data.get("required_sections", [])
        )

        # Build questions config
        questions_data = config["questions"]
        question_configs = [
            NodeQuestionConfig(
                id=q["id"],
                text=q["text"],
                required=q.get("required", False)
            )
            for q in questions_data
        ]
        questions_config = NodeQuestionsConfig(questions=question_configs)

        # Build dependencies config
        dependencies_config = NodeDependenciesConfig(
            predecessors=config.get("dependencies", [])
        )

        # Build task config
        task_data = config.get("task", {})
        task_config = NodeTaskConfig(
            name=task_data.get("name", config.get("name", "")),
            description=task_data.get("description", config.get("description", "")),
            role_supplement=task_data.get("role_supplement", ""),
        )

        # Build evaluator config
        evaluator_config = NodeEvaluatorConfig(
            criteria=evaluator.get("criteria", []),
            thresholds=evaluator.get("thresholds", {}),
            max_iterations=evaluator.get("max_iterations", 3),
        )

        # Build tool permissions config
        tools_data = config.get("tools", {})
        skills_data = tools_data.get("skills", {})
        skills_config = NodeSkillsConfig(
            sdk_native=skills_data.get("sdk_native", False),
            whitelist=skills_data.get("whitelist", []),
            quick_reference_enabled=skills_data.get("quick_reference_enabled", False),
            quick_reference_include_descriptions=skills_data.get("quick_reference_include_descriptions", False),
        )
        shared_context_data = tools_data.get("shared_context", {})
        shared_context_config = NodeSharedContextPermissions(
            enabled=shared_context_data.get("enabled", False),
            operations=shared_context_data.get("operations", []),
            allowed_keys=shared_context_data.get("allowed_keys", []),
        )
        tool_permissions = NodeToolPermissions(
            allowed_builtin_tools=tools_data.get("allowed_builtin_tools", []),
            file_permissions=NodeFilePermissions(
                allowed_read_dirs=tools_data.get("file_permissions", {}).get("allowed_read_dirs", []),
            ),
            search_permissions=NodeSearchPermissions(
                search_dirs=tools_data.get("search_permissions", {}).get("search_dirs", []),
            ),
            skills=skills_config,
            shared_context=shared_context_config,
        )

        # Build main NodeConfig
        return NodeConfig(
            node_id=config["node_id"],
            name=config["name"],
            description=config.get("description", ""),
            sequence=config["sequence"],
            deliverable_type=config["deliverable_type"],
            deliverable=deliverable_config,
            agent=agent_config,
            questions=questions_config,
            dependencies=dependencies_config,
            task=task_config,
            evaluator=evaluator_config,
            persona=persona,
            tool_permissions=tool_permissions,
        )

"""Summary Agent Configuration module - Story 36.2.

This module provides:
- SummaryAgentConfig dataclass for structured configuration
- SummaryAgentConfigLoader for loading config from YAML file
- Validation of configuration values
- Default values for missing configuration

Example:
    >>> from autoBMAD.docuswarm.config.summary_agent_config import SummaryAgentConfigLoader
    >>> loader = SummaryAgentConfigLoader()
    >>> config = loader.load()
    >>> print(config.llm.temperature)
    0.3
    >>> print(config.performance.max_concurrent_documents)
    3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)

# Default config file path (relative to this module)
DEFAULT_CONFIG_PATH = Path(__file__).parent / "summary_agent.yaml"


class SummaryAgentConfigError(Exception):
    """Exception raised for SummaryAgent configuration errors."""

    pass


@dataclass
class CachingConfig:
    """Caching configuration for SummaryAgent.

    Attributes:
        enable: Whether caching is enabled.
        ttl_hours: Time-to-live for cached summaries in hours.
        invalidate_on_doc_change: Whether to invalidate cache when document changes.
        backend: Cache storage backend (memory, sqlite, redis).
    """

    enable: bool = True
    ttl_hours: int = 24
    invalidate_on_doc_change: bool = True
    backend: str = "memory"

    def __post_init__(self) -> None:
        """Validate caching configuration."""
        if self.ttl_hours < 1:
            raise ValueError("ttl_hours must be at least 1")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> CachingConfig:
        """Create CachingConfig from dictionary.

        Args:
            data: Dictionary containing caching configuration.

        Returns:
            CachingConfig instance with values from dict or defaults.
        """
        if data is None:
            return cls()

        return cls(
            enable=data.get("enable", True),
            ttl_hours=data.get("ttl_hours", 24),
            invalidate_on_doc_change=data.get("invalidate_on_doc_change", True),
            backend=data.get("backend", "memory"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "enable": self.enable,
            "ttl_hours": self.ttl_hours,
            "invalidate_on_doc_change": self.invalidate_on_doc_change,
            "backend": self.backend,
        }


@dataclass
class PerformanceConfig:
    """Performance configuration for SummaryAgent.

    Attributes:
        max_concurrent_documents: Maximum number of concurrent document processing.
        batch_size: Number of documents to process in a single batch.
        timeout_per_document_seconds: Timeout for processing a single document.
        max_retries: Maximum number of retries for failed operations.
        max_file_size_bytes: Maximum file size in bytes.
    """

    max_concurrent_documents: int = 3
    batch_size: int = 10
    timeout_per_document_seconds: int = 30
    max_retries: int = 2
    max_file_size_bytes: int = 512000  # 500KB

    def __post_init__(self) -> None:
        """Validate performance configuration."""
        if self.max_concurrent_documents < 1:
            raise ValueError("max_concurrent_documents must be at least 1")
        if self.batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if self.timeout_per_document_seconds < 1:
            raise ValueError("timeout_per_document_seconds must be at least 1")
        if self.max_retries < 0:
            raise ValueError("max_retries must be at least 0")
        if self.max_file_size_bytes < 1024:
            raise ValueError("max_file_size_bytes must be at least 1024")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PerformanceConfig:
        """Create PerformanceConfig from dictionary.

        Args:
            data: Dictionary containing performance configuration.

        Returns:
            PerformanceConfig instance with values from dict or defaults.
        """
        if data is None:
            return cls()

        return cls(
            max_concurrent_documents=data.get("max_concurrent_documents", 3),
            batch_size=data.get("batch_size", 10),
            timeout_per_document_seconds=data.get("timeout_per_document_seconds", 30),
            max_retries=data.get("max_retries", 2),
            max_file_size_bytes=data.get("max_file_size_bytes", 512000),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "max_concurrent_documents": self.max_concurrent_documents,
            "batch_size": self.batch_size,
            "timeout_per_document_seconds": self.timeout_per_document_seconds,
            "max_retries": self.max_retries,
            "max_file_size_bytes": self.max_file_size_bytes,
        }


@dataclass
class LLMConfig:
    """LLM configuration for SummaryAgent.

    Attributes:
        type: Type of LLM provider (anthropic, openai, etc.).
        mode: SDK mode (agent, yolo, etc.).
        temperature: Sampling temperature (0.0 - 2.0).
        max_tokens: Maximum tokens to generate.
        model: Model identifier.
    """

    type: str = "anthropic"
    mode: str = "agent"
    temperature: float = 0.3
    max_tokens: int = 1000
    model: str = "claude-3-5-sonnet-20241022"

    def __post_init__(self) -> None:
        """Validate LLM configuration."""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> LLMConfig:
        """Create LLMConfig from dictionary.

        Args:
            data: Dictionary containing LLM configuration.

        Returns:
            LLMConfig instance with values from dict or defaults.
        """
        if data is None:
            return cls()

        return cls(
            type=data.get("type", "anthropic"),
            mode=data.get("mode", "agent"),
            temperature=data.get("temperature", 0.3),
            max_tokens=data.get("max_tokens", 1000),
            model=data.get("model", "claude-3-5-sonnet-20241022"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "type": self.type,
            "mode": self.mode,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model": self.model,
        }


@dataclass
class FileDiscoveryConfig:
    """File discovery configuration for SummaryAgent.

    Attributes:
        search_dirs: List of directories to search for files.
        allowed_extensions: List of allowed file extensions.
        prefer_shallowest_path: Whether to prefer shallowest path for duplicates.
        critical_file_pattern: Pattern to identify critical files.
    """

    search_dirs: list[str] = field(default_factory=lambda: ["docs"])
    allowed_extensions: list[str] = field(
        default_factory=lambda: [".md", ".txt", ".yaml", ".yml", ".json"]
    )
    prefer_shallowest_path: bool = True
    critical_file_pattern: str = "requirement"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> FileDiscoveryConfig:
        """Create FileDiscoveryConfig from dictionary.

        Args:
            data: Dictionary containing file discovery configuration.

        Returns:
            FileDiscoveryConfig instance with values from dict or defaults.
        """
        if data is None:
            return cls()

        return cls(
            search_dirs=data.get("search_dirs", ["docs"]),
            allowed_extensions=data.get(
                "allowed_extensions",
                [".md", ".txt", ".yaml", ".yml", ".json"],
            ),
            prefer_shallowest_path=data.get("prefer_shallowest_path", True),
            critical_file_pattern=data.get("critical_file_pattern", "requirement"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "search_dirs": self.search_dirs,
            "allowed_extensions": self.allowed_extensions,
            "prefer_shallowest_path": self.prefer_shallowest_path,
            "critical_file_pattern": self.critical_file_pattern,
        }


@dataclass
class OutputSchemaConfig:
    """Output schema configuration for SummaryAgent.

    Attributes:
        required_fields: List of required fields in the output.
        structure_fields: List of fields in the structure object.
    """

    required_fields: list[str] = field(
        default_factory=lambda: ["summary", "key_points", "structure"]
    )
    structure_fields: list[str] = field(default_factory=lambda: ["sections", "concepts"])

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> OutputSchemaConfig:
        """Create OutputSchemaConfig from dictionary.

        Args:
            data: Dictionary containing output schema configuration.

        Returns:
            OutputSchemaConfig instance with values from dict or defaults.
        """
        if data is None:
            return cls()

        return cls(
            required_fields=data.get(
                "required_fields",
                ["summary", "key_points", "structure"],
            ),
            structure_fields=data.get("structure_fields", ["sections", "concepts"]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "required_fields": self.required_fields,
            "structure_fields": self.structure_fields,
        }


@dataclass
class SummaryAgentConfig:
    """Complete configuration for SummaryAgent.

    This dataclass holds all configuration values for the SummaryAgent,
    including LLM settings, performance tuning, caching, and file discovery.

    Attributes:
        agent_id: Unique identifier for the agent.
        name: Human-readable name of the agent.
        description: Description of the agent's purpose.
        version: Configuration version.
        llm: LLM configuration.
        tools: List of allowed builtin tools.
        performance: Performance configuration.
        caching: Caching configuration.
        file_discovery: File discovery configuration.
        output_schema: Output schema configuration.
    """

    agent_id: str = "summary_agent"
    name: str = "Summary Agent"
    description: str = "Generates structured LLM summaries of referenced documents"
    version: str = "1.0"
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: list[str] = field(default_factory=lambda: ["ListDocuments", "ReadDocument"])
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)
    file_discovery: FileDiscoveryConfig = field(default_factory=FileDiscoveryConfig)
    output_schema: OutputSchemaConfig = field(default_factory=OutputSchemaConfig)

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SummaryAgentConfig:
        """Create SummaryAgentConfig from dictionary.

        Args:
            data: Dictionary containing complete agent configuration.

        Returns:
            SummaryAgentConfig instance with values from dict or defaults.
        """
        # Handle nested structures
        agent_metadata = data.get("agent_metadata", {})
        llm_config = data.get("llm_config", {})
        tools_config = data.get("tools", {})
        perf_config = data.get("performance", {})
        caching_config = data.get("caching", {})
        discovery_config = data.get("file_discovery", {})
        schema_config = data.get("output_schema", {})

        # Handle tools - can be a list directly or nested in allowed_builtin_tools
        tools: list[str] = ["ListDocuments", "ReadDocument"]  # Default
        if isinstance(tools_config, list):
            tools = tools_config
        elif isinstance(tools_config, dict):
            tools = tools_config.get("allowed_builtin_tools", ["ListDocuments", "ReadDocument"])

        return cls(
            agent_id=agent_metadata.get("agent_id", "summary_agent"),
            name=agent_metadata.get("name", "Summary Agent"),
            description=agent_metadata.get(
                "description",
                "Generates structured LLM summaries of referenced documents",
            ),
            version=str(agent_metadata.get("version", "1.0")),
            llm=LLMConfig.from_dict(llm_config),
            tools=tools,
            performance=PerformanceConfig.from_dict(perf_config),
            caching=CachingConfig.from_dict(caching_config),
            file_discovery=FileDiscoveryConfig.from_dict(discovery_config),
            output_schema=OutputSchemaConfig.from_dict(schema_config),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation of the complete configuration.
        """
        return {
            "agent_metadata": {
                "agent_id": self.agent_id,
                "name": self.name,
                "description": self.description,
                "version": self.version,
            },
            "llm_config": self.llm.to_dict(),
            "tools": {"allowed_builtin_tools": self.tools},
            "performance": self.performance.to_dict(),
            "caching": self.caching.to_dict(),
            "file_discovery": self.file_discovery.to_dict(),
            "output_schema": self.output_schema.to_dict(),
        }


class SummaryAgentConfigLoader:
    """Loader for SummaryAgent configuration from YAML file.

    This class handles loading and validation of SummaryAgent configuration
    from a YAML file. It provides default values for missing fields and
    validates the configuration.

    Attributes:
        config_path: Path to the YAML configuration file.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the config loader.

        Args:
            config_path: Path to the YAML configuration file.
                        Defaults to DEFAULT_CONFIG_PATH.
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._logger = logger.bind(loader=self.__class__.__name__)

    def load(self) -> SummaryAgentConfig:
        """Load configuration from YAML file.

        Returns:
            SummaryAgentConfig instance with loaded configuration.

        Raises:
            SummaryAgentConfigError: If the configuration file cannot be loaded
                                    or contains invalid data.
        """
        if not self.config_path.exists():
            self._logger.warning(
                "config_file_not_found",
                path=str(self.config_path),
                using_defaults=True,
            )
            raise SummaryAgentConfigError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self._logger.error("yaml_parse_error", error=str(e))
            raise SummaryAgentConfigError(f"Failed to parse YAML: {e}") from e
        except OSError as e:
            self._logger.error("file_read_error", error=str(e))
            raise SummaryAgentConfigError(f"Failed to read config file: {e}") from e

        if raw_data is None:
            raw_data = {}

        # Convert to SummaryAgentConfig
        try:
            config = SummaryAgentConfig.from_dict(raw_data)
        except ValueError as e:
            self._logger.error("config_validation_error", error=str(e))
            raise SummaryAgentConfigError(f"Invalid configuration: {e}") from e

        self._logger.info(
            "config_loaded",
            path=str(self.config_path),
            agent_id=config.agent_id,
        )

        return config

    def load_with_defaults(self) -> SummaryAgentConfig:
        """Load configuration with fallback to defaults on error.

        Returns:
            SummaryAgentConfig instance. If loading fails, returns default config.
        """
        try:
            return self.load()
        except SummaryAgentConfigError:
            self._logger.warning("using_default_config")
            return SummaryAgentConfig()


__all__ = [
    "CachingConfig",
    "FileDiscoveryConfig",
    "LLMConfig",
    "OutputSchemaConfig",
    "PerformanceConfig",
    "SummaryAgentConfig",
    "SummaryAgentConfigError",
    "SummaryAgentConfigLoader",
    "DEFAULT_CONFIG_PATH",
]

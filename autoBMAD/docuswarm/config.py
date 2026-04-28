"""Configuration management for DocuSwarm - Story 1.2.

Features:
- Environment variables loaded from .env file using python-dotenv
- ANTHROPIC_API_KEY required and validated on startup
- Optional configuration loaded from docuswarm.yaml with pyyaml
- Config class with full type hints using Python dataclass (frozen=True)
- Sensible defaults for all optional settings
- Precedence: env > yaml > defaults
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv as dotenv_load_dotenv

from autoBMAD.docuswarm.exceptions import ConfigurationError

# Default configuration values
DEFAULT_DB_PATH = "docuswarm.db"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MAX_ITERATIONS = 100
DEFAULT_BASE_URL = "https://api.anthropic.com/v1/"


def load_dotenv(env_path: Path | str | None = None) -> Path:
    """Load environment variables from .env file.

    Args:
        env_path: Path to .env file. If None, looks for .env in project root.

    Returns:
        Path to the .env file that was loaded (empty Path if not found).
    """
    if env_path is None:
        env_path = Path(".env")
    else:
        env_path = Path(env_path)

    if env_path.exists():
        # Use override=True to ensure the loaded values replace any existing env vars
        _ = dotenv_load_dotenv(env_path, override=True)
        return env_path

    return Path("")


def load_yaml_config(yaml_path: Path | str | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        yaml_path: Path to YAML config file. If None, returns empty dict.

    Returns:
        Dictionary of configuration values from YAML file.
    """
    if yaml_path is None:
        return {}

    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        return {}

    try:
        with open(yaml_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        # Return empty dict on parse error
        return {}


@dataclass(frozen=True)
class Config:
    """Application configuration dataclass.

    Uses frozen=True for immutability as per story requirements.
    All fields have full type hints.

    Environment variables take precedence over YAML config,
    which takes precedence over defaults.
    """

    api_key: str | None = field(default=None)
    base_url: str = field(default=DEFAULT_BASE_URL)
    db_path: Path = field(default_factory=lambda: Path(DEFAULT_DB_PATH))
    output_dir: Path = field(default_factory=lambda: Path(DEFAULT_OUTPUT_DIR))
    log_level: str = field(default=DEFAULT_LOG_LEVEL)
    max_iterations: int = field(default=DEFAULT_MAX_ITERATIONS)
    agent_timeout: int = field(default=7200)
    yaml_config: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate required ANTHROPIC_API_KEY
        # Can come from init parameter or environment

        # Explicitly reject empty string - must provide a valid key
        if self.api_key is not None and self.api_key == "":
            raise ConfigurationError(
                "ANTHROPIC_API_KEY cannot be empty. Please provide a valid API key."
            )

        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY is required. Please set it in your .env file "
                + "or as an environment variable."
            )

        # Use the validated api_key
        # Note: frozen=True means we can't modify, but we can use the value
        object.__setattr__(self, "api_key", api_key)

    @classmethod
    def from_env_and_yaml(
        cls,
        yaml_path: Path | str | None = None,
    ) -> Config:
        """Create Config from environment and YAML sources.

        Args:
            yaml_path: Path to YAML config file.

        Returns:
            Config instance with values from env > yaml > defaults.
        """
        # Load YAML config
        yaml_config = load_yaml_config(yaml_path)

        # Get API key from environment (highest precedence)
        # Never from YAML for security
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        # Get base_url from environment (highest precedence)
        base_url = os.environ.get("ANTHROPIC_BASE_URL") or yaml_config.get(
            "base_url", DEFAULT_BASE_URL
        )

        # Get other values from YAML with env override capability
        db_path = Path(
            os.environ.get("DOCUSWARM_DB_PATH") or yaml_config.get("db_path", DEFAULT_DB_PATH)
        )
        output_dir = Path(
            os.environ.get("DOCUSWARM_OUTPUT_DIR")
            or yaml_config.get("output_dir", DEFAULT_OUTPUT_DIR)
        )
        log_level = os.environ.get("DOCUSWARM_LOG_LEVEL") or yaml_config.get(
            "log_level", DEFAULT_LOG_LEVEL
        )
        max_iterations = int(
            os.environ.get("DOCUSWARM_MAX_ITERATIONS")
            or yaml_config.get("max_iterations", DEFAULT_MAX_ITERATIONS)
        )
        agent_timeout = int(
            os.environ.get("DOCUSWARM_AGENT_TIMEOUT") or yaml_config.get("agent_timeout", 7200)
        )

        return cls(
            api_key=api_key,
            base_url=base_url,
            db_path=db_path,
            output_dir=output_dir,
            log_level=log_level,
            max_iterations=max_iterations,
            agent_timeout=agent_timeout,
            yaml_config=yaml_config,
        )


def load_config(
    yaml_path: Path | str | None = None,
    env_path: Path | str | None = None,
) -> Config:
    """Load configuration from all sources.

    Loads .env file first, then YAML config, then applies defaults.
    Precedence: env vars > .env file > YAML config > defaults.

    Args:
        yaml_path: Path to YAML config file (default: docuswarm.yaml in same directory).
        env_path: Path to .env file (default: .env in project root).

    Returns:
        Validated Config instance.

    Raises:
        ConfigurationError: If required ANTHROPIC_API_KEY is missing.
    """
    # Load .env file
    _ = load_dotenv(env_path)

    # Determine YAML path
    if yaml_path is None:
        # YAML config file in same directory as config.py
        yaml_path = Path(__file__).parent / "docuswarm.yaml"

    # Create config from env and yaml
    return Config.from_env_and_yaml(yaml_path=yaml_path)

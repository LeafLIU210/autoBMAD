"""Configuration management for DocuSwarm.

Features:
- Environment variables loaded from .env file using python-dotenv
- ANTHROPIC_API_KEY required and validated on startup
- Config class with full type hints using Python dataclass (frozen=True)
- Sensible defaults for all optional settings

Precedence (highest to lowest):
1. .env file
2. System environment variables
3. Built-in defaults

Note:
The .env file takes precedence over pre-existing system environment
variables. This is achieved by calling python-dotenv with
``override=True``. YAML-based configuration (``docuswarm.yaml``) is no
longer supported and will not be loaded under any circumstances.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv as dotenv_load_dotenv

from autoBMAD.docuswarm.exceptions import ConfigurationError

# Default configuration values
DEFAULT_DB_PATH = "docuswarm.db"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MAX_ITERATIONS = 100
DEFAULT_BASE_URL = "https://api.anthropic.com/v1/"
DEFAULT_AGENT_TIMEOUT = 7200


def _find_project_root() -> Path:
    """Find project root by looking for .git or pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current.parent != current:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_dotenv(env_path: Path | str | None = None) -> Path:
    """Load environment variables from .env file.

    The .env file takes precedence over pre-existing system environment
    variables (``override=True``).

    Args:
        env_path: Path to .env file. If None, looks for .env in the
            current working directory first, then the project root.

    Returns:
        Path to the .env file that was loaded (empty Path if not found).
    """
    if env_path is not None:
        env_path = Path(env_path)
        if env_path.exists():
            _ = dotenv_load_dotenv(env_path, override=True)
            return env_path
        return Path("")

    # Try current working directory first
    cwd_env = Path(".env")
    if cwd_env.exists():
        _ = dotenv_load_dotenv(cwd_env, override=True)
        return cwd_env.resolve()

    # Fall back to project root
    project_root = _find_project_root()
    root_env = project_root / ".env"
    if root_env.exists():
        _ = dotenv_load_dotenv(root_env, override=True)
        return root_env.resolve()

    return Path("")


@dataclass(frozen=True)
class Config:
    """Application configuration dataclass.

    Uses ``frozen=True`` for immutability. All fields have full type
    hints.

    Values are resolved with the precedence:
    ``.env file > system environment variables > defaults``. Because
    ``python-dotenv`` is invoked with ``override=True``, values from the
    .env file are pushed into ``os.environ`` and therefore override
    pre-existing system environment variables when the config is built.
    """

    api_key: str | None = field(default=None)
    base_url: str = field(default=DEFAULT_BASE_URL)
    db_path: Path = field(default_factory=lambda: Path(DEFAULT_DB_PATH))
    output_dir: Path = field(default_factory=lambda: Path(DEFAULT_OUTPUT_DIR))
    log_level: str = field(default=DEFAULT_LOG_LEVEL)
    max_iterations: int = field(default=DEFAULT_MAX_ITERATIONS)
    agent_timeout: int = field(default=DEFAULT_AGENT_TIMEOUT)

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
    def from_env(cls) -> Config:
        """Create Config from environment variables and defaults.

        Reads values from ``os.environ`` (which already includes values
        loaded from ``.env`` with override semantics) and falls back to
        built-in defaults when unset.

        Returns:
            Config instance populated from environment and defaults.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", DEFAULT_BASE_URL)
        db_path = Path(os.environ.get("DOCUSWARM_DB_PATH", DEFAULT_DB_PATH))
        output_dir = Path(os.environ.get("DOCUSWARM_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
        log_level = os.environ.get("DOCUSWARM_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        max_iterations = int(
            os.environ.get("DOCUSWARM_MAX_ITERATIONS", str(DEFAULT_MAX_ITERATIONS))
        )
        agent_timeout = int(
            os.environ.get("DOCUSWARM_AGENT_TIMEOUT", str(DEFAULT_AGENT_TIMEOUT))
        )

        return cls(
            api_key=api_key,
            base_url=base_url,
            db_path=db_path,
            output_dir=output_dir,
            log_level=log_level,
            max_iterations=max_iterations,
            agent_timeout=agent_timeout,
        )


def load_config(env_path: Path | str | None = None) -> Config:
    """Load configuration from .env file and environment variables.

    The YAML-based ``docuswarm.yaml`` file is intentionally not loaded.

    Precedence: ``.env file > system environment variables > defaults``.

    Args:
        env_path: Optional explicit path to a .env file. When omitted,
            the loader searches the current working directory and then
            the project root.

    Returns:
        Validated Config instance.

    Raises:
        ConfigurationError: If required ANTHROPIC_API_KEY is missing.
    """
    # Load .env file (with override=True so .env wins over existing env vars)
    _ = load_dotenv(env_path)

    return Config.from_env()

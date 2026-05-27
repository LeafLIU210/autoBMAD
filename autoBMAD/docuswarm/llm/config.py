"""
LLM Configuration Module

Defines configuration for Kimi K2.5 API with three modes:
- Instant: Fast responses for simple queries
- Thinking: Reasoning for complex problems
- Agent: Tool-calling capability for agents
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# Kimi Code API base URL
API_BASE = "https://api.kimi.com/coding/"

# Rate limiting constants
RATE_LIMIT_RPM = 200  # Requests per minute
RATE_LIMIT_CONCURRENT = 20  # Max concurrent requests
BURST_LIMIT = 5  # Token bucket burst capacity

# Model configurations for each mode.
# Model name is no longer hardcoded here; it is resolved from ``Config.model_name``
# (which reads ANTHROPIC_MODEL_NAME / ANTHROPIC_MODEL from the environment).
# Only temperature / max_tokens are mode-specific.
MODELS: dict[str, dict[str, Any]] = {
    "instant": {
        "model": None,
        "temperature": 0.3,
        "max_tokens": 4096,
    },
    "thinking": {
        "model": None,
        "temperature": 0.5,
        "max_tokens": 8000,
    },
    "agent": {
        "model": None,
        "temperature": 0.7,
        "max_tokens": 32768,
    },
}


class ChatMode(StrEnum):
    """Chat mode for Kimi client."""

    INSTANT = "instant"
    THINKING = "thinking"
    AGENT = "agent"


class LLMConfig(BaseModel):
    """Configuration for LLM API requests."""

    model: str | None = Field(default=None, description="Model name to use (None defers to CLI/env)")
    temperature: float = Field(description="Sampling temperature")
    max_tokens: int = Field(description="Maximum tokens to generate")
    api_key: str | None = Field(default=None, description="API key for authentication")
    base_url: str = Field(default=API_BASE, description="API base URL")
    timeout: int = Field(default=300, description="Request timeout in seconds")

    @classmethod
    def from_mode(
        cls,
        mode: ChatMode,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
    ) -> LLMConfig:
        """
        Create LLMConfig from a chat mode.

        Args:
            mode: The chat mode (instant, thinking, or agent)
            api_key: Optional API key override
            base_url: Optional base URL override
            model_name: Optional explicit model name. When None, resolves from
                ``Config.model_name`` (ANTHROPIC_MODEL_NAME / ANTHROPIC_MODEL env).

        Returns:
            LLMConfig configured for the specified mode
        """
        config = MODELS[mode.value]
        resolved_model = model_name if model_name is not None else _resolve_model_name()
        return cls(
            model=resolved_model,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=api_key,
            base_url=base_url or API_BASE,
        )

    def __init__(self, mode: ChatMode = ChatMode.INSTANT, **data: Any):
        """Initialize LLMConfig with mode or explicit parameters."""
        if "model" not in data:
            # Use mode-based configuration; resolve model from env-backed Config.
            config = MODELS[mode.value]
            data.setdefault("model", _resolve_model_name())
            data.setdefault("temperature", config["temperature"])
            data.setdefault("max_tokens", config["max_tokens"])
        super().__init__(**data)


def _resolve_model_name() -> str | None:
    """Resolve model name from :class:`Config` (env-backed).

    Returns None when neither ``ANTHROPIC_MODEL_NAME`` nor ``ANTHROPIC_MODEL``
    is set, letting the CLI subprocess fall back to its own defaults.
    """
    # Local import to avoid circular imports at module load time.
    from autoBMAD.docuswarm.config import Config

    try:
        cfg = Config.from_env()
    except Exception:
        return None
    return cfg.model_name

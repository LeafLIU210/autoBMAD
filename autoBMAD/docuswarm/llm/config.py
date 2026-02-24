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
API_BASE = "https://api.kimi.com/coding/v1"

# Rate limiting constants
RATE_LIMIT_RPM = 200  # Requests per minute
RATE_LIMIT_CONCURRENT = 20  # Max concurrent requests
BURST_LIMIT = 5  # Token bucket burst capacity

# Model configurations for each mode
# Fix: use kimi-for-coding for all modes (Kimi Code platform)
MODELS = {
    "instant": {
        "model": "kimi-for-coding",
        "temperature": 0.3,
        "max_tokens": 4096,
    },
    "thinking": {
        "model": "kimi-for-coding",
        "temperature": 0.5,
        "max_tokens": 8000,
    },
    "agent": {
        "model": "kimi-for-coding",
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

    model: str = Field(description="Model name to use")
    temperature: float = Field(description="Sampling temperature")
    max_tokens: int = Field(description="Maximum tokens to generate")
    api_key: str | None = Field(default=None, description="API key for authentication")
    base_url: str = Field(default=API_BASE, description="API base URL")
    timeout: int = Field(default=60, description="Request timeout in seconds")

    @classmethod
    def from_mode(
        cls, mode: ChatMode, api_key: str | None = None, base_url: str | None = None
    ) -> LLMConfig:
        """
        Create LLMConfig from a chat mode.

        Args:
            mode: The chat mode (instant, thinking, or agent)
            api_key: Optional API key override
            base_url: Optional base URL override

        Returns:
            LLMConfig configured for the specified mode
        """
        config = MODELS[mode.value]
        return cls(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=api_key,
            base_url=base_url or API_BASE,
        )

    def __init__(self, mode: ChatMode = ChatMode.INSTANT, **data: Any):
        """Initialize LLMConfig with mode or explicit parameters."""
        if "model" not in data:
            # Use mode-based configuration
            config = MODELS[mode.value]
            data.setdefault("model", config["model"])
            data.setdefault("temperature", config["temperature"])
            data.setdefault("max_tokens", config["max_tokens"])
        super().__init__(**data)

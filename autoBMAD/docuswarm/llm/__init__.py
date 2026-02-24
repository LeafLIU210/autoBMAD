"""
LLM Integration Module

Provides Kimi K2.5 client with support for:
- Three modes: Instant, Thinking, Agent
- Token bucket rate limiting
- Response parsing and validation

Note: Retry logic is handled by SDK's built-in max_retries_per_step parameter.
"""

from autoBMAD.docuswarm.llm.config import (
    API_BASE,
    BURST_LIMIT,
    MODELS,
    RATE_LIMIT_CONCURRENT,
    RATE_LIMIT_RPM,
    ChatMode,
    LLMConfig,
)
from autoBMAD.docuswarm.llm.response import (
    ResponseParseError,
    ValidationError,
    extract_json,
    extract_json_from_markdown,
    extract_text_from_messages,
    validate_evaluator_output,
    validate_independent_output,
)

__all__ = [
    # Config
    "API_BASE",
    "MODELS",
    "RATE_LIMIT_RPM",
    "RATE_LIMIT_CONCURRENT",
    "BURST_LIMIT",
    "ChatMode",
    "LLMConfig",
    # Response parsing
    "extract_json",
    "extract_json_from_markdown",
    "extract_text_from_messages",
    "validate_independent_output",
    "validate_evaluator_output",
    "ResponseParseError",
    "ValidationError",
]

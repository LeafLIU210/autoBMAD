"""
ModeMapper Module

Maps ChatMode enum values to SDK parameters for Kimi K2.5 API.

This module provides:
- SDKModeParams: Dataclass holding SDK configuration parameters
- MODE_MAP: Dictionary mapping ChatMode to SDKModeParams
- map_mode(): Function to safely translate ChatMode to SDK parameters
- get_supported_modes(): Helper to list supported modes
"""

from __future__ import annotations

from dataclasses import dataclass

from autoBMAD.docuswarm.llm.config import ChatMode


@dataclass(frozen=True)
class SDKModeParams:
    """
    SDK configuration parameters for Kimi K2.5 API.

    Attributes:
        model: Model identifier to use. None means the concrete model should be
            resolved from :class:`autoBMAD.docuswarm.config.Config` (which reads
            ``ANTHROPIC_MODEL_NAME`` / ``ANTHROPIC_MODEL`` env vars).
        thinking: Whether to enable thinking/reasoning mode
        max_steps_per_turn: Maximum steps per turn for agent mode
    """

    model: str | None
    thinking: bool
    max_steps_per_turn: int | None


# Mode mapping dictionary: ChatMode -> SDKModeParams
# Model names are intentionally left as None; callers should resolve the
# concrete model from ``Config.model_name`` at runtime.
MODE_MAP: dict[ChatMode, SDKModeParams] = {
    ChatMode.INSTANT: SDKModeParams(
        model=None,
        thinking=False,
        max_steps_per_turn=5,
    ),
    ChatMode.THINKING: SDKModeParams(
        model=None,
        thinking=True,
        max_steps_per_turn=10,
    ),
    ChatMode.AGENT: SDKModeParams(
        model=None,
        thinking=False,
        max_steps_per_turn=50,
    ),
}


def map_mode(mode: ChatMode) -> SDKModeParams:
    """
    Map a ChatMode to SDK configuration parameters.

    Args:
        mode: The ChatMode to translate

    Returns:
        SDKModeParams with the corresponding SDK configuration

    Raises:
        ValueError: If the ChatMode is not recognized
    """
    if mode not in MODE_MAP:
        raise ValueError(f"Unknown ChatMode: {mode}")
    return MODE_MAP[mode]


def get_supported_modes() -> list[ChatMode]:
    """
    Get list of all supported ChatModes.

    Returns:
        List of supported ChatMode values
    """
    return list(MODE_MAP.keys())


__all__ = [
    "SDKModeParams",
    "MODE_MAP",
    "map_mode",
    "get_supported_modes",
]

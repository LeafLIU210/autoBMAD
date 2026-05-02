"""Persona Loader - Story 2.5.

This module provides functionality to load BMAD personas from configuration files
and format them into system prompts for LLM agents.

Persona files are located at `nodes/{node_id}/persona.json` relative to project root.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import structlog
from structlog import BoundLogger

# Configure module logger
logger: BoundLogger = structlog.get_logger(__name__)

# Default persona used when file not found
DEFAULT_PERSONA: dict[str, Any] = {
    "name": "Default Agent",
    "role": "General Assistant",
    "identity": "You are a helpful AI assistant.",
    "expertise": [],
    "principles": [],
}


@dataclass
class Persona:
    """Represents a BMAD persona configuration.

    Attributes:
        name: The persona's name.
        role: The role/title of the persona.
        identity: The identity statement describing who the persona is.
        expertise: List of expertise areas.
        principles: List of guiding principles.
    """

    name: str
    role: str
    identity: str
    expertise: list[str] = field(default_factory=list)
    principles: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Persona:
        """Create Persona from a dictionary.

        Args:
            data: Dictionary containing persona data.

        Returns:
            Persona instance.

        Raises:
            ValueError: If required fields are missing.
        """
        # Validate required fields
        required_fields = ["name", "role", "identity"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            raise ValueError(f"Missing required persona fields: {missing}")

        return cls(
            name=cast(str, data["name"]),
            role=cast(str, data["role"]),
            identity=cast(str, data["identity"]),
            expertise=cast(list[str], data.get("expertise", [])),
            principles=cast(list[str], data.get("principles", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert Persona to dictionary.

        Returns:
            Dictionary representation of the persona.
        """
        return {
            "name": self.name,
            "role": self.role,
            "identity": self.identity,
            "expertise": self.expertise,
            "principles": self.principles,
        }


class PersonaLoader:
    """Loads and manages BMAD personas from JSON configuration files.

    This class handles:
    - Loading persona from JSON files
    - Validating persona schema
    - Formatting personas into system prompts
    - Caching loaded personas
    - Handling missing files gracefully
    """

    # Class-level cache for loaded personas
    _cache: dict[str, Persona] = {}

    @staticmethod
    def load(
        node_id: str,
        project_root: Path | None = None,
        use_cache: bool = True,
    ) -> Persona:
        """Load persona from node configuration for a given node.

        P2 Fix: Delegates to NodeLoader for unified path resolution.

        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm', 'ux', 'architect', 'po').
            project_root: Deprecated, kept for backward compatibility. Ignored.
            use_cache: Whether to use cached persona if available.

        Returns:
            Persona object loaded from the node configuration.

        Raises:
            FileNotFoundError: If persona data is not found in node config.
            ValueError: If persona data is invalid or missing required fields.
        """
        # Determine cache key
        cache_key = node_id

        # Return cached version if available
        if use_cache and cache_key in PersonaLoader._cache:
            logger.debug("Using cached persona", node_id=node_id)
            return PersonaLoader._cache[cache_key]

        # P2 Fix: Use NodeLoader for unified path resolution
        from autoBMAD.nodes.loader import NodeLoader

        node_config = NodeLoader.load(node_id)
        persona_data = node_config.persona

        if not persona_data:
            raise FileNotFoundError(
                f"Persona data not found for node '{node_id}' in node configuration"
            )

        logger.info("Loaded persona from node config", node_id=node_id)

        # Parse and validate persona
        try:
            persona = Persona.from_dict(persona_data)
        except ValueError as e:
            logger.error(
                "Invalid persona schema",
                node_id=node_id,
                error=str(e),
            )
            raise

        # Cache the loaded persona
        PersonaLoader._cache[cache_key] = persona
        logger.debug("Persona cached", node_id=node_id)

        return persona

    @staticmethod
    def format_system_prompt(persona: Persona, max_tokens: int = 2000) -> str:
        """Format persona into a system prompt for LLM.

        Compiles the persona's name, role, identity, expertise, and principles
        into a coherent system prompt. Trims expertise list if necessary to
        stay within token limits.

        Args:
            persona: The Persona object to format.
            max_tokens: Maximum tokens (approximate) for the prompt.

        Returns:
            Formatted system prompt string.
        """
        # Build the prompt sections
        sections: list[str] = []

        # Header with name and role
        sections.append(f"# Persona: {persona.name}")
        sections.append(f"**Role**: {persona.role}")
        sections.append("")

        # Identity statement
        sections.append("## Identity")
        sections.append(persona.identity)
        sections.append("")

        # Expertise (with trimming if needed)
        if persona.expertise:
            # Estimate: each expertise item ~10 tokens, plus overhead
            # Start with all, trim from end if over limit
            expertise = list(persona.expertise)
            estimated = len(expertise) * 10 + 100  # rough estimate

            # If likely over limit, trim expertise list
            if estimated > max_tokens * 0.3:  # Assume expertise is ~30% of prompt
                # Keep first 10 expertise items as safe limit
                expertise = expertise[:10]
                logger.warning(
                    "Expertise list trimmed to fit token limit",
                    original_count=len(persona.expertise),
                    trimmed_count=len(expertise),
                )

            sections.append("## Expertise")
            for item in expertise:
                sections.append(f"- {item}")
            sections.append("")

        # Principles
        if persona.principles:
            sections.append("## Guiding Principles")
            for principle in persona.principles:
                sections.append(f"- {principle}")
            sections.append("")

        # Join sections into prompt
        prompt = "\n".join(sections)

        # Log warning if prompt seems long
        estimated_tokens = len(prompt) // 4  # Rough token estimate
        if estimated_tokens > max_tokens:
            logger.warning(
                "System prompt may exceed token limit",
                estimated_tokens=estimated_tokens,
                max_tokens=max_tokens,
            )

        return prompt

    @staticmethod
    def load_and_format(
        node_id: str,
        project_root: Path | None = None,
        max_tokens: int = 2000,
    ) -> str:
        """Load persona and format as system prompt in one call.

        Convenience method that loads a persona and returns the formatted
        system prompt directly.

        Args:
            node_id: The node identifier.
            project_root: Root directory of the project.
            max_tokens: Maximum tokens for the prompt.

        Returns:
            Formatted system prompt string.
        """
        persona = PersonaLoader.load(node_id, project_root)
        return PersonaLoader.format_system_prompt(persona, max_tokens)

    @staticmethod
    def clear_cache() -> None:
        """Clear the persona cache.

        Useful for testing or when forcing reload of persona files.
        """
        PersonaLoader._cache.clear()
        logger.debug("Persona cache cleared")

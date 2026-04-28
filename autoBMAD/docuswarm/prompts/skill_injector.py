"""BMAD Skill Injector - Story 31.3.

This module provides the SkillInjector class for generating quick reference
documentation for available BMAD skills. It reads skill descriptions from
SKILL.md files and formats them for inclusion in system prompts.

Architecture: Layer 4 of the Four-Layer System Prompt Architecture.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import ClassVar, Final

#: Logger instance for skill injector
logger = logging.getLogger(__name__)

#: Mapping of node IDs to their respective BMAD skill commands.
#: Each node receives relevant skills based on their role in the workflow.
#: DEPRECATED: Use SkillInjector.build_skills_quick_reference() with whitelist instead.
NODE_SKILL_MAP: Final[dict[str, list[str]]] = {
    "analyst": [
        "agent-analyst",
        "domain-research",
        "market-research",
        "advanced-elicitation",
    ],
    "pm": [
        "agent-pm",
        "create-prd",
        "create-epics-and-stories",
        "validate-prd",
    ],
    "ux": [
        "agent-ux-designer",
        "create-ux-design",
        "advanced-elicitation",
        "review-edge-case-hunter",
    ],
    "architect": [
        "agent-architect",
        "create-architecture",
        "technical-research",
        "review-adversarial-general",
        "check-implementation-readiness",
    ],
    "po": [
        "create-epics-and-stories",
        "validate-prd",
        "check-implementation-readiness",
        "sprint-planning",
        "distillator",
    ],
}


class SkillInjector:
    """Injects BMAD skill descriptions into system prompts.

    The SkillInjector reads skill descriptions from SKILL.md files located
    at `.claude/skills/{skill-name}/SKILL.md`, extracts the description from
    the YAML frontmatter, and formats them for quick reference.

    Example:
        >>> whitelist = ["agent-dev", "create-prd"]
        >>> ref = SkillInjector.build_skills_quick_reference(whitelist)
        >>> print(ref)
        ## Available BMAD Skills

        - **agent-dev**: Senior software engineer for story execution...
        - **create-prd**: Create a PRD from scratch...
    """

    #: Maximum length for skill descriptions (150 characters).
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 150

    #: Skills root directory path.
    SKILLS_ROOT: ClassVar[str] = ".claude/skills"

    @staticmethod
    def build_skills_quick_reference(whitelist: list[str] | None) -> str:
        """Build quick reference Markdown for whitelisted BMAD skills.

        Reads SKILL.md files for each whitelisted skill, extracts descriptions
        from YAML frontmatter, and formats them as a Markdown section.

        Args:
            whitelist: List of skill names to include (e.g., ["agent-dev"]).
                If None or empty, returns an empty string.

        Returns:
            Markdown formatted string with "## Available BMAD Skills" header
            followed by bullet list of skills. Returns empty string if
            whitelist is None or empty.

        Example:
            >>> whitelist = ["agent-dev", "create-prd"]
            >>> ref = SkillInjector.build_skills_quick_reference(whitelist)
            >>> assert "## Available BMAD Skills" in ref
            >>> assert "**agent-dev**:" in ref
        """
        if not whitelist:
            return ""

        skills_root = Path(SkillInjector.SKILLS_ROOT)
        lines: list[str] = ["## Available BMAD Skills\n"]

        for skill_name in whitelist:
            description = SkillInjector._read_skill_description(skill_name, skills_root)
            if description:
                lines.append(f"- **{skill_name}**: {description}")
            else:
                lines.append(f"- **{skill_name}**:")

        return "\n".join(lines)

    @staticmethod
    def _read_skill_description(skill_name: str, skills_root: Path) -> str:
        """Read and extract skill description from SKILL.md file.

        Reads the SKILL.md file for the given skill, extracts the
        description from YAML frontmatter if present.

        Args:
            skill_name: The skill name (e.g., "agent-dev").
            skills_root: Path to the skills directory.

        Returns:
            The skill description, truncated to MAX_DESCRIPTION_LENGTH
            characters with ellipsis if exceeded. Returns empty string
            if file not found or no description available.
        """
        skill_dir = skill_name if skill_name.startswith("bmad-") else f"bmad-{skill_name}"
        skill_path = skills_root / skill_dir / "SKILL.md"

        try:
            content = skill_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(
                "SKILL.md not found for skill '%s' at %s",
                skill_name,
                skill_path,
            )
            return ""
        except (PermissionError, UnicodeDecodeError, OSError) as e:
            logger.warning(
                "Error reading SKILL.md for skill '%s': %s",
                skill_name,
                e,
            )
            return ""

        # Try to extract description from YAML frontmatter
        description = SkillInjector._extract_description_from_frontmatter(content, skill_name)

        return SkillInjector._truncate_description(description)

    @staticmethod
    def _extract_description_from_frontmatter(content: str, skill_name: str) -> str:
        """Extract description from YAML frontmatter.

        Args:
            content: The full content of the SKILL.md file.
            skill_name: The skill name for logging purposes.

        Returns:
            The description from frontmatter if found, empty string otherwise.
        """
        # Match YAML frontmatter: ---\n...\n---
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            logger.warning(
                "No YAML frontmatter found for skill '%s'",
                skill_name,
            )
            return ""

        frontmatter = match.group(1)

        # Look for description field (handle both quoted and unquoted)
        # Match description: 'value' or description: "value" or description: value
        desc_pattern = r'^description:\s*(?:["\']?(.*?)["\']?\s*)?$'
        desc_match = re.search(desc_pattern, frontmatter, re.MULTILINE)

        if desc_match:
            description = desc_match.group(1) or ""
            return description.strip()

        logger.warning(
            "No 'description' field found in YAML frontmatter for skill '%s'",
            skill_name,
        )
        return ""

    @staticmethod
    def _truncate_description(description: str) -> str:
        """Truncate description to MAX_DESCRIPTION_LENGTH with ellipsis.

        Args:
            description: The description to truncate.

        Returns:
            Truncated description. If original exceeds MAX_DESCRIPTION_LENGTH,
            returns first 147 characters followed by "...".
        """
        if not description:
            return ""

        if len(description) <= SkillInjector.MAX_DESCRIPTION_LENGTH:
            return description

        return description[:147] + "..."

"""Prompt Template Engine - Story 29.6.

This module provides the PromptTemplateEngine class for building prompts using
the Four-Layer System Prompt Architecture:

Layer 1: claude_code preset (SDK built-in)
Layer 2: Persona (identity, role, expertise) - personas/{id}.json
Layer 3: Task Context (task name, deliverables) - node.yaml
Layer 4: Skills (BMAD commands) - .claude/skills/

User Prompt: Pure task content (context, deliverables, feedback)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector

# Configure module logger
logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class PromptBuildConfig:
    """Configuration for building prompts.

    This dataclass contains all the information needed to build both
    the system prompt append (Layers 2+3+4) and the user prompt.

    Attributes:
        persona_id: The identifier for the persona to load (e.g., 'analyst', 'pm').
        task_name: The name of the task to be performed.
        deliverables: List of deliverable items required for the task.
        skills: List of skill command names available to the agent.
        context_summary: Optional summary of context information.
    """

    persona_id: str
    task_name: str
    deliverables: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    context_summary: str | None = None


class PromptTemplateEngine:
    """Engine for building prompts using the Four-Layer Architecture.

    This engine constructs prompts by assembling layers 2, 3, and 4 into
    the system prompt append, while keeping the user prompt focused on
    pure task content without any persona or identity instructions.

    Args:
        project_root: Path to the project root directory.
        skill_injector: Optional SkillInjector instance. If not provided,
            a default SkillInjector will be created.

    Example:
        >>> engine = PromptTemplateEngine(Path("/project"))
        >>> config = PromptBuildConfig(
        ...     persona_id="analyst",
        ...     task_name="create-product-brief",
        ...     deliverables=["executive_summary", "core_vision"],
        ...     skills=["agent-analyst", "domain-research"],
        ... )
        >>> system_append = engine.build_system_prompt_append(config)
        >>> user_prompt = engine.build_user_prompt(config, {"user_input": "Create it"})
    """

    #: Maximum token budget for system_prompt_append (Layer 2+3+4).
    MAX_TOKEN_BUDGET: int = 3200

    #: Warning threshold for token budget.
    WARNING_TOKEN_THRESHOLD: int = 3000

    def __init__(
        self,
        project_root: Path | str,
        skill_injector: SkillInjector | None = None,
    ) -> None:
        """Initialize the PromptTemplateEngine.

        Args:
            project_root: Path to the project root directory.
            skill_injector: Optional SkillInjector instance. If None, creates
                a default SkillInjector.
        """
        self.project_root = Path(project_root)
        self.skill_injector = skill_injector or SkillInjector()

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using character/4 approximation.

        This is a simple estimation suitable for budget checking.
        More accurate tokenization would require tiktoken or similar.

        Args:
            text: The text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        return len(text) // 4

    def _load_persona(self, persona_id: str) -> dict[str, Any]:
        """Load persona data from JSON file.

        Args:
            persona_id: The persona identifier (e.g., 'analyst', 'pm').

        Returns:
            Dictionary containing persona data, or empty dict if not found.
        """
        persona_file = self.project_root / "nodes" / persona_id / "persona.json"

        try:
            with open(persona_file, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            logger.warning(
                "Failed to load persona file",
                persona_id=persona_id,
                path=str(persona_file),
                error=str(e),
            )
            return {}

    def _build_persona_section(self, config: PromptBuildConfig) -> str:
        """Build Layer 2: Persona section.

        Args:
            config: The prompt build configuration.

        Returns:
            Formatted persona section string.
        """
        persona = self._load_persona(config.persona_id)
        if not persona:
            return ""

        sections: list[str] = []

        # Header
        sections.append(f"## Persona: {persona.get('name', 'Unknown')}")
        sections.append("")

        # Role
        sections.append(f"**Role**: {persona.get('role', 'Unknown')}")
        sections.append("")

        # Identity statement
        sections.append("### Identity")
        sections.append(persona.get("identity", ""))
        sections.append("")

        # Expertise
        expertise = persona.get("expertise", [])
        if expertise:
            sections.append("### Expertise")
            for item in expertise:
                sections.append(f"- {item}")
            sections.append("")

        # Principles
        principles = persona.get("principles", [])
        if principles:
            sections.append("### Guiding Principles")
            for principle in principles:
                sections.append(f"- {principle}")
            sections.append("")

        return "\n".join(sections)

    def _build_task_section(self, config: PromptBuildConfig) -> str:
        """Build Layer 3: Task Context section.

        Args:
            config: The prompt build configuration.

        Returns:
            Formatted task section string.
        """
        sections: list[str] = []

        # Header with task name
        sections.append(f"## Task: {config.task_name}")
        sections.append("")

        # Context summary if provided
        if config.context_summary:
            sections.append("### Context Summary")
            sections.append(config.context_summary)
            sections.append("")

        # Deliverables
        if config.deliverables:
            sections.append("### Deliverables")
            sections.append("Create the following:")
            sections.append("")
            for deliverable in config.deliverables:
                sections.append(f"- {deliverable}")
            sections.append("")

        return "\n".join(sections)

    def _build_skills_section(self, config: PromptBuildConfig) -> str:
        """Build Layer 4: Skills section.

        Args:
            config: The prompt build configuration.

        Returns:
            Formatted skills section string from SkillInjector.
        """
        return self.skill_injector.build_skill_section(config.persona_id)

    def build_system_prompt_append(self, config: PromptBuildConfig) -> str:
        """Build the system prompt append (Layers 2+3+4).

        This method assembles the persona (Layer 2), task context (Layer 3),
        and skills (Layer 4) sections into a single string to be appended
        to the claude_code preset (Layer 1).

        Args:
            config: The prompt build configuration.

        Returns:
            Formatted system prompt append string containing Layers 2+3+4.
            Token count is checked against MAX_TOKEN_BUDGET and skills
            section may be truncated if exceeded.
        """
        # Build each layer
        persona_section = self._build_persona_section(config)
        task_section = self._build_task_section(config)
        skills_section = self._build_skills_section(config)

        # Combine sections
        sections: list[str] = []
        if persona_section:
            sections.append(persona_section)
        if task_section:
            sections.append(task_section)
        if skills_section:
            sections.append(skills_section)

        result = "\n".join(sections)

        # Check token budget
        token_count = self._estimate_tokens(result)

        if token_count > self.WARNING_TOKEN_THRESHOLD:
            logger.warning(
                "System prompt append approaching token limit",
                token_count=token_count,
                max_budget=self.MAX_TOKEN_BUDGET,
                persona_id=config.persona_id,
            )

        if token_count > self.MAX_TOKEN_BUDGET:
            logger.warning(
                "System prompt append exceeds token budget, truncating skills section",
                token_count=token_count,
                max_budget=self.MAX_TOKEN_BUDGET,
                persona_id=config.persona_id,
            )
            # Truncate skills section to fit within budget
            max_skills_tokens = self.MAX_TOKEN_BUDGET - self._estimate_tokens(
                persona_section + task_section
            )
            max_skills_chars = max_skills_tokens * 4
            truncated_skills = skills_section[:max_skills_chars]

            # Rebuild result with truncated skills
            sections = []
            if persona_section:
                sections.append(persona_section)
            if task_section:
                sections.append(task_section)
            if truncated_skills:
                sections.append(truncated_skills)

            result = "\n".join(sections)

            # Log final token count
            final_token_count = self._estimate_tokens(result)
            logger.info(
                "System prompt append truncated to fit budget",
                final_token_count=final_token_count,
                max_budget=self.MAX_TOKEN_BUDGET,
                persona_id=config.persona_id,
            )

        return result

    def build_user_prompt(
        self,
        config: PromptBuildConfig,
        context: dict[str, Any],
    ) -> str:
        """Build the user prompt with pure task content.

        This method constructs a user prompt that contains ONLY task-related
        content: context documents, deliverable requirements, iteration feedback,
        and user input. It explicitly excludes any persona or identity instructions.

        Args:
            config: The prompt build configuration.
            context: Dictionary containing task context including:
                - user_input: The main user request/instruction
                - context_docs: List of context documents
                - iteration_feedback: Optional feedback from previous iterations
                - additional_context: Any additional context information

        Returns:
            Formatted user prompt string containing pure task content.
        """
        sections: list[str] = []

        # User input (primary task instruction)
        user_input = context.get("user_input", "")
        if user_input:
            sections.append("## User Request")
            sections.append(user_input)
            sections.append("")

        # Context documents
        context_docs = context.get("context_docs", [])
        if context_docs:
            sections.append("## Context Documents")
            sections.append("")
            for i, doc in enumerate(context_docs, 1):
                title = doc.get("title", f"Document {i}")
                content = doc.get("content", "")
                sections.append(f"### {title}")
                sections.append(content)
                sections.append("")

        # Deliverable requirements (reiterated from config)
        if config.deliverables:
            sections.append("## Deliverable Requirements")
            sections.append("")
            sections.append(f"Task: {config.task_name}")
            sections.append("")
            sections.append("Required sections:")
            for deliverable in config.deliverables:
                sections.append(f"- {deliverable}")
            sections.append("")

        # Iteration feedback
        iteration_feedback = context.get("iteration_feedback")
        if iteration_feedback:
            sections.append("## Iteration Feedback")
            sections.append("")
            if isinstance(iteration_feedback, dict):
                score = iteration_feedback.get("score")
                if score is not None:
                    sections.append(f"Previous iteration score: {score}")
                    sections.append("")
                issues = iteration_feedback.get("issues", [])
                if issues:
                    sections.append("Issues to address:")
                    for issue in issues:
                        sections.append(f"- {issue}")
                    sections.append("")
                feedback_text = iteration_feedback.get("feedback", "")
                if feedback_text:
                    sections.append("Feedback:")
                    sections.append(feedback_text)
                    sections.append("")
            else:
                sections.append(str(iteration_feedback))
                sections.append("")

        # Additional context
        additional = context.get("additional_context", {})
        if isinstance(additional, dict) and additional:
            sections.append("## Additional Context")
            sections.append("")
            for key, value in additional.items():
                sections.append(f"**{key}**: {value}")
            sections.append("")

        return "\n".join(sections)


__all__ = [
    "PromptBuildConfig",
    "PromptTemplateEngine",
]

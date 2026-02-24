"""Evaluator Agent Implementation - Story 2.7, Updated for Story 7.3 and 7.5.

This module provides the EvaluatorAgent class which:
- Loads evaluation criteria from nodes/{node_id}/evaluator.yaml
- Calls LLM with Kimi K2.5 Thinking mode (temperature 0.5, max_tokens 8000)
- Scores deliverables against criteria (0.0-1.0 scale)
- Calculates weighted alignment score using criterion weights
- Returns verdict (APPROVED | NEEDS_REVISION | BLOCKED) based on thresholds
- Maintains context isolation - NO access to private_reasoning from Independent Agent
- Updated to support KimiSessionManager (Story 7.3)
- Updated to use session_manager.single_prompt() SDK API (Story 7.5)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast, override

import structlog
import yaml
from kimi_agent_sdk import Message

from autoBMAD.docuswarm.agents.base import BaseAgent
from autoBMAD.docuswarm.llm.response import (
    ResponseParseError,
    ValidationError,
    extract_json,
    validate_evaluator_output,
)
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

if TYPE_CHECKING:
    from autoBMAD.docuswarm.config import Config as AgentConfig

# Type alias for evaluator agent output
EvaluatorOutput = dict[str, Any]


class EvaluatorAgentError(Exception):
    """Base exception for EvaluatorAgent errors."""

    pass


class CriteriaLoadError(EvaluatorAgentError):
    """Raised when criteria loading fails."""

    pass


class EvaluationError(EvaluatorAgentError):
    """Raised when evaluation fails."""

    pass


class EvaluatorAgent(BaseAgent):
    """Evaluator Agent for reviewing and scoring deliverables.

    This agent evaluates deliverables against defined criteria and provides
    actionable feedback with weighted alignment scores.

    Attributes:
        node_id: The node identifier for criteria loading.
        criteria: List of evaluation criteria with name, description, and weight.
    """

    # Verdict thresholds
    APPROVAL_THRESHOLD = 0.70
    BLOCKED_THRESHOLD = 0.50

    def __init__(
        self,
        config: AgentConfig,
        session_manager: KimiSessionManager,
        node_id: str = "dev",
        project_root: Path | None = None,
    ) -> None:
        """Initialize the EvaluatorAgent.

        Args:
            config: Agent configuration object.
            session_manager: KimiSessionManager for SDK interactions.
            node_id: The node identifier for loading criteria from nodes/{node_id}/evaluator.yaml.
            project_root: Root directory of the project. If None, uses cwd.

        Raises:
            CriteriaLoadError: If criteria loading fails.
        """
        super().__init__(config, session_manager=session_manager)
        self.node_id = node_id
        self.project_root = project_root or Path.cwd()

        # Load criteria
        self.criteria = self._load_criteria()

        # Rebind logger with agent name
        self.logger: structlog.stdlib.BoundLogger = structlog.get_logger().bind(
            agent=self.__class__.__name__,
            node_id=node_id,
        )

    def _load_criteria(self) -> list[dict[str, Any]]:
        """Load evaluation criteria from evaluator.yaml file.

        Returns:
            List of criteria dictionaries with name, description, and weight.

        Raises:
            CriteriaLoadError: If criteria cannot be loaded or are invalid.
        """
        criteria_path = self.project_root / "nodes" / self.node_id / "evaluator.yaml"

        if not criteria_path.exists():
            raise CriteriaLoadError(f"Criteria file not found: {criteria_path}")

        try:
            with open(criteria_path, encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise CriteriaLoadError(f"Invalid YAML in criteria file: {e}") from e
        except OSError as e:
            raise CriteriaLoadError(f"Failed to read criteria file: {e}") from e

        if not data or "criteria" not in data:
            raise CriteriaLoadError("Criteria file must contain 'criteria' key")

        criteria: list[dict[str, Any]] = cast(list[dict[str, Any]], data["criteria"])

        if len(criteria) == 0:
            raise CriteriaLoadError("At least one criterion is required")

        # Validate each criterion
        total_weight = 0.0
        for i, criterion in enumerate(criteria):
            if "name" not in criterion:
                raise CriteriaLoadError(f"Criteria[{i}]: 'name' is required")
            if "description" not in criterion:
                raise CriteriaLoadError(f"Criteria[{i}]: 'description' is required")
            if "weight" not in criterion:
                raise CriteriaLoadError(f"Criteria[{i}]: 'weight' is required")

            weight: float = criterion["weight"]
            if weight < 0 or weight > 1:
                raise CriteriaLoadError(f"Criteria[{i}]: 'weight' must be between 0 and 1")

            total_weight += weight

        # Validate weights sum to 1.0
        if not abs(total_weight - 1.0) < 0.001:
            raise CriteriaLoadError(f"Criteria weights must sum to 1.0, got {total_weight}")

        return criteria

    def _format_evaluation_prompt(
        self,
        subject_context: str,
        deliverable: dict[str, Any],
    ) -> str:
        """Format the evaluation prompt with criteria and deliverable.

        Args:
            subject_context: The subject/context of the task.
            deliverable: The deliverable to evaluate (dict with title and content).

        Returns:
            Formatted prompt string for LLM evaluation.
        """
        # Build criteria section
        criteria_section = "\n".join(
            f"- **{c['name']}**: {c['description']} (weight: {c['weight']})" for c in self.criteria
        )

        # Build deliverable section
        deliverable_title: str = deliverable.get("title", "Untitled")
        deliverable_content: str = deliverable.get("content", "")

        prompt = f"""## Task Evaluation

You are an expert evaluator reviewing a deliverable against defined criteria.

### Subject Context
{subject_context}

### Deliverable to Evaluate
**Title**: {deliverable_title}

**Content**:
{deliverable_content}

### Evaluation Criteria
{criteria_section}

## Your Task

Evaluate the deliverable against each criterion and provide:
1. A score (0.0 to 1.0) for each criterion
2. An overall alignment score (weighted average of criterion scores)
3. A verdict: APPROVED, NEEDS_REVISION, or BLOCKED
4. Any issues found
5. Suggestions for improvement

### Scoring Guidelines
- 0.0-0.3: Does not meet criterion at all
- 0.4-0.6: Partially meets criterion
- 0.7-0.8: Meets criterion well
- 0.9-1.0: Exceeds criterion

### Verdict Thresholds
- APPROVED: Alignment score >= 0.70
- NEEDS_REVISION: 0.50 < Alignment score < 0.70
- BLOCKED: Alignment score <= 0.50

## Output Format

Respond ONLY with a JSON object in this format:
```json
{{
    "criterion_scores": {{"criterion_name": score, ...}},
    "alignment_score": overall_weighted_score,
    "verdict": "APPROVED" | "NEEDS_REVISION" | "BLOCKED",
    "issues_found": ["issue1", "issue2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...]
}}
```

Do not include any other text in your response.
"""
        return prompt

    def _clamp_scores(self, scores: dict[str, float]) -> dict[str, float]:
        """Clamp scores to valid range (0.0-1.0).

        Args:
            scores: Dictionary of criterion names to scores.

        Returns:
            Dictionary with clamped scores.
        """
        clamped: dict[str, float] = {}
        for name, score in scores.items():
            if score > 1.0:
                clamped[name] = 1.0
            elif score < 0.0:
                clamped[name] = 0.0
            else:
                clamped[name] = score
        return clamped

    def _calculate_alignment_score(self, scores: dict[str, float]) -> float:
        """Calculate weighted alignment score from criterion scores.

        Args:
            scores: Dictionary of criterion names to scores.

        Returns:
            Weighted alignment score (0.0-1.0).
        """
        alignment: float = 0.0
        for criterion in self.criteria:
            name: str = criterion["name"]
            weight: float = criterion["weight"]
            score: float = scores.get(name, 0.5)  # Default to 0.5 if missing
            alignment += score * weight
        return alignment

    def _determine_verdict(self, alignment_score: float) -> str:
        """Determine verdict based on alignment score.

        Args:
            alignment_score: The weighted alignment score.

        Returns:
            Verdict string: APPROVED, NEEDS_REVISION, or BLOCKED.
        """
        if alignment_score >= self.APPROVAL_THRESHOLD:
            return "APPROVED"
        elif alignment_score <= self.BLOCKED_THRESHOLD:
            return "BLOCKED"
        else:
            return "NEEDS_REVISION"

    async def _call_llm(
        self,
        subject_context: str,
        deliverable: dict[str, Any],
    ) -> list[Message]:
        """Call the LLM with the evaluation prompt.

        Uses session_manager.single_prompt() (SDK API - Story 7.5).

        Args:
            subject_context: The subject/context of the task.
            deliverable: The deliverable to evaluate.

        Returns:
            list[Message] from the LLM.

        Raises:
            EvaluationError: If the LLM call fails.
        """
        # Build the full prompt with system instructions and evaluation context
        system_prompt = """You are an expert evaluator agent. Your role is to review deliverables
against defined criteria and provide fair, actionable feedback. Always respond with
valid JSON in the specified format."""

        user_prompt = self._format_evaluation_prompt(subject_context, deliverable)

        try:
            # Use session_manager (SDK API - Story 7.5)
            # session_manager is guaranteed non-None by BaseAgent __init__
            assert self.session_manager is not None

            # Combine system and user prompts for single_prompt API
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Use session_manager.single_prompt() with:
            # - mode="thinking" for Kimi K2.5 thinking mode
            # - yolo=True for evaluator (no tools to approve, read-only agent)
            sdk_response: list[Message] = await self.session_manager.single_prompt(
                prompt=full_prompt,
                mode="thinking",
                yolo=True,
            )
            return sdk_response
        except EvaluationError:
            # Re-raise EvaluationError as-is
            raise
        except Exception as e:
            self.logger.error("llm_call_failed", error=str(e))
            raise EvaluationError(f"LLM call failed: {e}") from e

    def _parse_response(self, response: list[Message]) -> dict[str, Any]:
        """Parse and validate LLM response against EvaluatorOutput schema.

        Uses list[Message] from session_manager.single_prompt() (SDK API - Story 7.5).

        Args:
            response: The list[Message] from the LLM.

        Returns:
            Parsed and validated output dictionary.

        Raises:
            EvaluationError: If parsing or validation fails.
        """
        # SDK API: list[Message]
        if not response:
            raise EvaluationError("Empty response from LLM")

        # Get content from the last assistant message with content
        content_raw = None
        for msg in reversed(response):
            if msg.role == "assistant" and msg.content:
                content_raw = msg.content
                break

        # Handle different content types from SDK
        # content can be: str, ContentPart, or list[ContentPart]
        if content_raw is None:
            raise EvaluationError("Empty response from LLM")

        # Convert content to string if needed
        # Declare content variable upfront to avoid redeclaration
        content: str
        if isinstance(content_raw, str):
            content = content_raw
        else:
            # After str check, remaining types are list[ContentPart] or single ContentPart
            # Use hasattr to check for iterability without isinstance check
            if hasattr(content_raw, "__iter__") and not isinstance(content_raw, str):
                # content_raw is a list of ContentPart objects
                content = ""
                for part in cast("list[Any]", content_raw):
                    if hasattr(part, "text"):
                        content += part.text
                    elif isinstance(part, str):
                        content += part
            else:
                # Single ContentPart object
                if hasattr(content_raw, "text"):
                    content = content_raw.text
                else:
                    content = str(content_raw)

        if not content or not content.strip():
            raise EvaluationError("Empty response from LLM")

        # Try to extract JSON from the response
        try:
            data: dict[str, Any] = extract_json(cast(str, content))
        except ResponseParseError as e:
            self.logger.error("response_parse_failed", error=str(e), content=content[:200])
            raise EvaluationError(f"Failed to parse response: {e}") from e

        # Add default scores for missing criteria
        for criterion in self.criteria:
            if criterion["name"] not in data.get("criterion_scores", {}):
                data.setdefault("criterion_scores", {})[criterion["name"]] = 0.5

        # Clamp scores to valid range BEFORE validation
        data["criterion_scores"] = self._clamp_scores(
            cast(dict[str, float], data["criterion_scores"])
        )

        # Recalculate alignment score from clamped criterion_scores BEFORE validation
        data["alignment_score"] = self._calculate_alignment_score(data["criterion_scores"])

        # Clamp alignment_score to valid range
        if data["alignment_score"] > 1.0:
            data["alignment_score"] = 1.0
        elif data["alignment_score"] < 0.0:
            data["alignment_score"] = 0.0

        # Validate against EvaluatorOutput schema
        try:
            validate_evaluator_output(data)
        except ValidationError as e:
            self.logger.error("response_validation_failed", error=str(e), data=data)
            raise EvaluationError(f"Response validation failed: {e}") from e

        # Ensure verdict matches calculated score
        data["verdict"] = self._determine_verdict(data["alignment_score"])

        return data

    @override
    async def execute(self, context: dict[str, Any]) -> EvaluatorOutput:
        """Execute the Evaluator Agent to evaluate a deliverable.

        Args:
            context: Execution context containing:
                - subject_context: The context/subject of the task
                - deliverable: The deliverable to evaluate (dict with title, content)

        Returns:
            Dict containing:
                - criterion_scores: Dict[str, float] - scores per criterion
                - alignment_score: float - weighted alignment score
                - verdict: str - APPROVED | NEEDS_REVISION | BLOCKED
                - issues_found: List[str]
                - suggestions: List[str]

        Raises:
            EvaluatorAgentError: If execution fails.
            ValueError: If context contains private_reasoning (context isolation violation).
        """
        # CRITICAL: Validate context isolation - reject private_reasoning
        # The Evaluator Agent must NEVER have access to private_reasoning from Independent Agent
        if "private_reasoning" in context:
            raise ValueError(
                "Context isolation violation: private_reasoning must not be passed to Evaluator Agent. "
                + "The Evaluator must only receive subject_context and deliverable."
            )

        # Extract required parameters
        subject_context_raw: Any = context.get("subject_context")
        if not subject_context_raw:
            raise EvaluatorAgentError("subject_context is required in context")

        # Normalize subject_context to string (may arrive as dict from ContextManager)
        subject_context: str = str(subject_context_raw)

        deliverable: dict[str, Any] = context.get("deliverable")  # type: ignore[assignment]
        if not deliverable:
            raise EvaluatorAgentError("deliverable is required in context")

        # Ensure deliverable has required fields
        if "title" not in deliverable or "content" not in deliverable:
            raise EvaluatorAgentError("deliverable must have 'title' and 'content'")

        self.logger.info(
            "executing_evaluator_agent",
            node_id=self.node_id,
            subject=subject_context[:50],
        )

        # Call LLM for evaluation
        response = await self._call_llm(subject_context, deliverable)

        # Parse and validate response
        output = self._parse_response(response)

        self.logger.info(
            "evaluator_agent_completed",
            verdict=output["verdict"],
            alignment_score=output["alignment_score"],
        )

        return output


# Convenience function for creating EvaluatorAgent
def create_evaluator_agent(
    config: AgentConfig,
    session_manager: KimiSessionManager,
    node_id: str = "dev",
    project_root: Path | None = None,
) -> EvaluatorAgent:
    """Create an EvaluatorAgent with configured session manager.

    Args:
        config: Agent configuration.
        session_manager: KimiSessionManager for SDK interactions.
        node_id: The node identifier for criteria loading.
        project_root: Root directory of the project.

    Returns:
        Configured EvaluatorAgent instance.
    """
    return EvaluatorAgent(
        config=config,
        session_manager=session_manager,
        node_id=node_id,
        project_root=project_root,
    )


__all__ = [
    "EvaluatorAgent",
    "EvaluatorAgentError",
    "CriteriaLoadError",
    "EvaluationError",
    "EvaluatorOutput",
    "create_evaluator_agent",
]

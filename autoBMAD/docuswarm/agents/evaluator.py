"""Evaluator Agent Implementation - Story 2.7, Updated for Story 7.3 and 7.5.

This module provides the EvaluatorAgent class which:
- Loads evaluation criteria from nodes/{node_id}/evaluator.yaml
- Calls LLM with Claude Thinking mode (temperature 0.5, max_tokens 8000)
- Scores deliverables against criteria (0.0-1.0 scale)
- Calculates weighted alignment score using criterion weights
- Returns verdict (APPROVED | NEEDS_REVISION | BLOCKED) based on thresholds
- Maintains context isolation - NO access to private_reasoning from Independent Agent
- Updated to support SessionManager (Story 7.3)
- Updated to use session_manager.single_prompt() SDK API (Story 7.5)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, override

import structlog
import yaml

from autoBMAD.docuswarm.agents.base import AgentConfig, BaseAgent
from autoBMAD.docuswarm.agents.evaluator_config.schemas import EVALUATOR_OUTPUT_SCHEMA
from autoBMAD.docuswarm.llm.response import (
    ResponseParseError,
    extract_json,
)
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.prompts.contract_builder import create_contract_builder

if TYPE_CHECKING:
    from autoBMAD.docuswarm.node_execution.contracts import EvaluatorAgentInput

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
        approval_threshold: Minimum score for APPROVED verdict (from node config).
        blocked_threshold: Maximum score for BLOCKED verdict (from node config).
    """

    # P0 Fix: Default thresholds now serve as fallback only
    # Actual thresholds are loaded from node evaluator.yaml configuration
    DEFAULT_APPROVAL_THRESHOLD = 0.70
    DEFAULT_BLOCKED_THRESHOLD = 0.50

    def __init__(
        self,
        config: AgentConfig,
        session_manager: SessionManager,
        node_id: str = "dev",
        project_root: Path | None = None,
        # P0 Fix: Add explicit threshold parameters with defaults
        approval_threshold: float | None = None,
        blocked_threshold: float | None = None,
    ) -> None:
        """Initialize the EvaluatorAgent.

        Args:
            config: Agent configuration object.
            session_manager: SessionManager for SDK interactions.
            node_id: The node identifier for loading criteria from nodes/{node_id}/evaluator.yaml.
            project_root: Root directory of the project. If None, uses cwd.
            approval_threshold: Minimum score for APPROVED verdict (overrides node config).
            blocked_threshold: Maximum score for BLOCKED verdict (overrides node config).

        Raises:
            CriteriaLoadError: If criteria loading fails.
        """
        super().__init__(config, session_manager=session_manager)
        self.node_id = node_id
        self.project_root = project_root or Path.cwd()

        # Initialize contract builder (P0: Node Prompt Contract Builder)
        self.contract_builder = create_contract_builder()

        # Load criteria and threshold configuration from node config
        self.criteria = self._load_criteria()

        # P0 Fix: Load thresholds from node evaluator.yaml configuration
        node_thresholds = self._load_thresholds()

        # Use explicitly provided thresholds, fall back to node config, then to defaults
        self.approval_threshold = (
            approval_threshold
            if approval_threshold is not None
            else node_thresholds.get("approval", self.DEFAULT_APPROVAL_THRESHOLD)
        )
        self.blocked_threshold = (
            blocked_threshold
            if blocked_threshold is not None
            else node_thresholds.get("escalation", self.DEFAULT_BLOCKED_THRESHOLD)
        )

        # Rebind logger with agent name
        self.logger: structlog.stdlib.BoundLogger = structlog.get_logger().bind(
            agent=self.__class__.__name__,
            node_id=node_id,
            approval_threshold=self.approval_threshold,
            blocked_threshold=self.blocked_threshold,
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

        criteria: list[dict[str, Any]] = data["criteria"]

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

    def _load_thresholds(self) -> dict[str, float]:
        """Load evaluation thresholds from evaluator.yaml or node.yaml configuration.

        P0 Fix: Load threshold configuration from node evaluator.yaml to ensure
        runtime behavior matches node configuration.

        Returns:
            Dictionary with 'approval' and 'escalation' threshold values.
        """
        from autoBMAD.nodes.loader import NodeLoader

        try:
            # Use NodeLoader to get full node configuration
            # Need to ensure NodeLoader base path is set correctly
            node_config = NodeLoader.load(self.node_id)

            if node_config.evaluator and node_config.evaluator.threshold:
                return {
                    "approval": node_config.evaluator.threshold.get(
                        "approval", self.DEFAULT_APPROVAL_THRESHOLD
                    ),
                    "escalation": node_config.evaluator.threshold.get(
                        "escalation", self.DEFAULT_BLOCKED_THRESHOLD
                    ),
                }
        except Exception as e:
            # Log but don't fail - fall back to defaults
            self.logger.warning(
                "failed_to_load_thresholds_from_node_config",
                node_id=self.node_id,
                error=str(e),
            )

        # Fall back to defaults
        return {
            "approval": self.DEFAULT_APPROVAL_THRESHOLD,
            "escalation": self.DEFAULT_BLOCKED_THRESHOLD,
        }

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

        P0 Fix: Uses instance thresholds loaded from node config instead of class constants.

        Args:
            alignment_score: The weighted alignment score.

        Returns:
            Verdict string: APPROVED, NEEDS_REVISION, or BLOCKED.
        """
        if alignment_score >= self.approval_threshold:
            return "APPROVED"
        elif alignment_score <= self.blocked_threshold:
            return "BLOCKED"
        else:
            return "NEEDS_REVISION"

    # TDD-09: System prompt for evaluator role context
    EVALUATOR_SYSTEM_PROMPT = (
        "You are an expert evaluator agent. Your role is to review deliverables "
        "against defined criteria and provide fair, actionable feedback. "
        "You MUST always respond with valid JSON in the specified format. "
        "Never respond with markdown tables, narrative text, or any non-JSON format."
    )

    async def _call_llm_with_prompt(
        self,
        prompt: str,
    ) -> list[dict[str, Any]]:
        """Call LLM with pre-built prompt (P0: Contract Builder).

        Uses session_manager.single_prompt() (SDK API - Story 7.5).

        P0: This method receives a pre-built prompt from NodePromptContractBuilder,
        enabling structured prompt contracts with explicit criteria and deliverable
        requirements.

        TDD-09: Now passes system_prompt to single_prompt() for role context.

        Story 38.1: Passes output_format=EVALUATOR_OUTPUT_SCHEMA for structured output
        validation via SDK's native output_format mechanism.

        Args:
            prompt: The complete prompt (from contract).

        Returns:
            list[dict[str, Any]] from the LLM.

        Raises:
            EvaluationError: If the LLM call fails.
        """
        try:
            # Use session_manager (SDK API - Story 7.5)
            # session_manager is guaranteed non-None by BaseAgent __init__
            assert self.session_manager is not None

            # Use session_manager.single_prompt() with:
            # - mode="thinking" for Claude thinking mode
            # - yolo=True for evaluator (no tools to approve, read-only agent)
            # - system_prompt for evaluator role context (TDD-09)
            # - output_format for structured output (Story 38.1)
            sdk_response: list[dict[str, Any]] = await self.session_manager.single_prompt(
                prompt=prompt,
                mode="thinking",
                yolo=True,
                system_prompt=self.EVALUATOR_SYSTEM_PROMPT,
                output_format=EVALUATOR_OUTPUT_SCHEMA,
            )
            return sdk_response
        except EvaluationError:
            # Re-raise EvaluationError as-is
            raise
        except Exception as e:
            self.logger.error("llm_call_failed", error=str(e))
            raise EvaluationError(f"LLM call failed: {e}") from e

    async def _call_llm(
        self,
        subject_context: str,
        deliverable: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Call the LLM with the evaluation prompt.

        Uses session_manager.single_prompt() (SDK API - Story 7.5).

        Args:
            subject_context: The subject/context of the task.
            deliverable: The deliverable to evaluate.

        Returns:
            list[dict[str, Any]] from the LLM.

        Raises:
            EvaluationError: If the LLM call fails.
        """
        # Build the full prompt with system instructions and evaluation context
        system_prompt = """You are an expert evaluator agent. Your role is to review deliverables
against defined criteria and provide fair, actionable feedback. Always respond with
valid JSON in the specified format."""

        user_prompt = self._format_evaluation_prompt(subject_context, deliverable)

        # P0: Use contract builder for legacy calls too
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        return await self._call_llm_with_prompt(full_prompt)

    def _extract_text_from_content(self, content: Any) -> str:
        """Extract text from content which may be str or list of dicts.

        Args:
            content: Content from message (str or list of content parts).

        Returns:
            Extracted text string.
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text", ""))
                elif isinstance(part, str):
                    texts.append(part)
            return " ".join(texts)
        else:
            return str(content)

    def _parse_response(self, response: list[dict[str, Any]]) -> dict[str, Any]:
        """Parse and validate LLM response against EvaluatorOutput schema.

        Uses list[dict[str, Any]] from session_manager.single_prompt() (SDK API - Story 7.5).

        Story 38.1: Prioritizes structured_output from SDK when available (type="structured"),
        falls back to extract_json() for backward compatibility.

        Args:
            response: The list[dict[str, Any]] from the LLM.

        Returns:
            Parsed and validated output dictionary.

        Raises:
            EvaluationError: If parsing or validation fails.
        """
        # SDK API: list[dict[str, Any]]
        if not response:
            raise EvaluationError("Empty response from LLM")

        # Story 38.1: Check for structured output from SDK (type="structured")
        for msg in response:
            if isinstance(msg, dict) and msg.get("type") == "structured" and "data" in msg:
                structured_data = msg["data"]
                if isinstance(structured_data, dict):
                    self.logger.debug("using_structured_output_from_sdk")
                    data: dict[str, Any] = structured_data
                    # Skip to validation logic (same as JSON extracted path)
                    return self._validate_and_finalize_parsed_data(data)

        # Fallback: Extract JSON from the response text
        # Get content from the last assistant message with content
        content_str = None
        for msg in reversed(response):
            if msg.get("role") == "assistant":
                content = msg.get("content")
                if content:
                    content_str = self._extract_text_from_content(content)
                    break

        if not content_str or not content_str.strip():
            raise EvaluationError("Empty response from LLM")

        # Try to extract JSON from the response
        try:
            data = extract_json(content_str)
        except ResponseParseError as e:
            self.logger.error("response_parse_failed", error=str(e), content=content_str[:200])
            raise EvaluationError(f"Failed to parse response: {e}") from e

        return self._validate_and_finalize_parsed_data(data)

    def _validate_and_finalize_parsed_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate and finalize parsed data from either structured output or JSON extraction.

        Story 38.1: Extracted validation logic to avoid duplication between
        structured output path and JSON extraction path.

        Args:
            data: Parsed data dictionary (from structured output or JSON extraction).

        Returns:
            Validated and finalized output dictionary.

        Raises:
            EvaluationError: If validation fails.
        """

        # Add default scores for missing criteria
        for criterion in self.criteria:
            if criterion["name"] not in data.get("criterion_scores", {}):
                data.setdefault("criterion_scores", {})[criterion["name"]] = 0.5

        # Clamp scores to valid range BEFORE validation
        data["criterion_scores"] = self._clamp_scores(data["criterion_scores"])

        # Recalculate alignment score from clamped criterion_scores BEFORE validation
        data["alignment_score"] = self._calculate_alignment_score(data["criterion_scores"])

        # Clamp alignment_score to valid range
        if data["alignment_score"] > 1.0:
            data["alignment_score"] = 1.0
        elif data["alignment_score"] < 0.0:
            data["alignment_score"] = 0.0

        # Validate against EvaluatorOutput schema using ContextValidator
        from autoBMAD.docuswarm.context import ContextValidator

        validator = ContextValidator()
        validation_result = validator.validate_evaluator_output(data, node_id=self.node_id)
        if not validation_result.valid:
            # Log the first error for debugging
            if validation_result.issues:
                first_issue = validation_result.issues[0]
                self.logger.error(
                    "response_validation_failed",
                    field=first_issue.field,
                    message=first_issue.message,
                    code=first_issue.code,
                )
            raise EvaluationError(
                f"Response validation failed: {validation_result.issues[0].message if validation_result.issues else 'Unknown error'}"
            )

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

        deliverable: dict[str, Any] = context.get("deliverable")
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

    async def execute_with_input(self, agent_input: EvaluatorAgentInput) -> EvaluatorOutput:
        """Execute the Evaluator Agent with structured input (Single Context Protocol).

        This method receives a structured EvaluatorAgentInput instead of a raw context dict,
        eliminating the need for guessing and parsing.

        P0: Uses NodePromptContractBuilder to build structured prompts with criteria
        and deliverable requirements explicitly injected.

        F3: 修复 Evaluator 输入契约 - 确保 original_context_summary 被正确传递到 prompt.

        Args:
            agent_input: Structured input containing task_name, task_description,
                original_context_summary, deliverable_artifact, deliverable_body, and criteria.

        Returns:
            Dict containing:
                - criterion_scores: Dict[str, float] - scores per criterion
                - alignment_score: float - weighted alignment score
                - verdict: str - APPROVED | NEEDS_REVISION | BLOCKED
                - issues_found: List[str]
                - suggestions: List[str]

        Raises:
            EvaluatorAgentError: If execution fails.
        """
        # Single Context Protocol: 直接从结构化输入读取字段
        # 使用 .get() 安全访问 TypedDict 的可选字段 (基于类型安全修复)
        task_name = agent_input.get("task_name", "")
        _ = agent_input.get("task_description", "")
        # deliverable_artifact reserved for future use
        _ = agent_input.get("deliverable_artifact", {})
        deliverable_body = agent_input.get("deliverable_body", "")

        # F3: 修复 - 读取原始上下文摘要（关键修复）
        original_context_summary = agent_input.get("original_context_summary", "")

        self.logger.info(
            "executing_evaluator_agent_with_input",
            node_id=self.node_id,
            task_name=task_name,
            has_original_context=bool(original_context_summary),  # F3: 日志记录是否有原始上下文
        )

        # P0: Build NodeExecutionContext from agent_input
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext

        context = NodeExecutionContext(
            pipeline_id="",
            node_id=self.node_id,
            node_name=task_name or self.node_id,
            node_order=0,
            original_context={"content": original_context_summary}
            if original_context_summary
            else {},
            chained_deliverables=[],
            shared_context={},
            iteration_feedback=None,
            docs_context=[],
        )

        # P0: Build contract from context using NodePromptContractBuilder
        contract = self.contract_builder.build_evaluator_contract(
            context,
            deliverable_body=deliverable_body,
        )

        # P0: Render full prompt from contract
        prompt = self.contract_builder.render_evaluator_prompt(contract)

        # P0: Call LLM with contract-based prompt
        response = await self._call_llm_with_prompt(prompt)

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
    session_manager: SessionManager,
    node_id: str = "dev",
    project_root: Path | None = None,
) -> EvaluatorAgent:
    """Create an EvaluatorAgent with configured session manager.

    Args:
        config: Agent configuration.
        session_manager: SessionManager for SDK interactions.
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

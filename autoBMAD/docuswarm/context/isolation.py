"""Context isolation module for agent access control.

This module provides the ContextManager class for Layer 2 (Runtime Access Control)
of the three-layer isolation system. It controls context access for different
agent types, ensuring the Independent Agent receives full context while the
Evaluator Agent only receives public, non-private context.

Story: 4.1, Updated for Single Context Protocol
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from autoBMAD.docuswarm.exceptions import ContextIsolationError
from autoBMAD.docuswarm.node_execution.contracts import (
    EvaluatorAgentInput,
    IndependentAgentInput,
    NodeExecutionContext,
)
from autoBMAD.docuswarm.utils.logging import get_logger

# Import for type hints only to avoid circular imports
if TYPE_CHECKING:
    from autoBMAD.docuswarm.context.validator import ContextValidator

# Private fields that must never be exposed to Evaluator agent
PRIVATE_FIELDS: list[str] = [
    "private_reasoning",
    "tool_call_history",
    "iteration_feedback",
    "internal_notes",
]


class ContextManager:
    """Manages context isolation between Independent and Evaluator agents.

    This class enforces the "dumb agent" isolation principle by:
    - Providing full context access for Independent agent
    - Restricting Evaluator agent to only public, non-private context
    - Validating that no private fields leak to the Evaluator

    Attributes:
        PRIVATE_FIELDS: List of field names that are considered private
            and must not be exposed to the Evaluator agent.

    Example:
        >>> manager = ContextManager()
        >>> # Independent agent gets full context
        >>> independent_ctx = manager.build_independent_context(
        ...     subject_context={"task": "Write code"},
        ...     previous_deliverables={"design": "..."},
        ...     iteration_feedback={"iterations": 2}
        ... )
        >>> # Evaluator gets restricted context
        >>> evaluator_ctx = manager.build_evaluator_context(
        ...     subject_context={"task": "Review code"},
        ...     deliverable={"content": "..."},
        ...     criteria={"quality": "high"}
        ... )
    """

    # Private fields that must not be exposed to Evaluator
    PRIVATE_FIELDS: list[str] = PRIVATE_FIELDS

    def __init__(self, validator: ContextValidator | None = None) -> None:
        """Initialize ContextManager with logger and optional validator.

        Args:
            validator: Optional ContextValidator instance. If not provided,
                a new one will be created for isolation validation.
        """
        self._logger = get_logger(__name__)
        self._validator: ContextValidator | None = validator
        self._validator_initialized = validator is not None

    @property
    def _validator_instance(self) -> ContextValidator:
        """Get the validator instance, creating it lazily if needed.

        This property defers the import of ContextValidator until first use,
        avoiding circular import issues at module load time.

        Returns:
            ContextValidator instance.
        """
        if not self._validator_initialized or self._validator is None:
            # Delayed import to avoid circular imports at module level
            from autoBMAD.docuswarm.context.validator import ContextValidator

            self._validator = ContextValidator()
            self._validator_initialized = True
        return self._validator

    # ==== Single Context Protocol: 新方法 ====
    def build_independent_input(
        self,
        execution_context: NodeExecutionContext,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> IndependentAgentInput:
        """构建 IndependentAgent 的输入。

        从 NodeExecutionContext 和 NodeConfig 中提取必要字段，组装为 AgentInput。
        任务相关字段从 node_config 读取（单来源原则），不再从 context 重复传递。

        Args:
            execution_context: 统一的节点执行上下文（仅含运行时字段）
            iteration_feedback: 可选的迭代反馈

        Returns:
            IndependentAgentInput 结构
        """
        # 从 node_config 加载任务字段（单来源原则）
        from autoBMAD.nodes.loader import NodeLoader

        node_id = execution_context.get("node_id")
        if not node_id:
            raise ValueError("node_id is required in execution_context")

        node_config = NodeLoader.load(node_id)

        # 构建原始上下文摘要
        original = execution_context.get("original_context", {})
        summary = _extract_original_context_summary(original)

        # 构建上游交付物摘要
        chained_summary: list[dict[str, Any]] = []
        for item in execution_context.get("chained_deliverables", []):
            deliverable = item.get("deliverable", {})
            chained_summary.append(
                {
                    "node_id": item.get("node_id"),
                    "title": deliverable.get("title", "Untitled"),
                    "summary": deliverable.get("summary", "")[:200],
                }
            )

        # 构建交付物要求
        deliverable_reqs: dict[str, Any] = {}
        if node_config.deliverable.required_sections:
            deliverable_reqs["required_sections"] = node_config.deliverable.required_sections
        if (
            hasattr(node_config.deliverable, "template_title")
            and node_config.deliverable.template_title
        ):
            deliverable_reqs["template_title"] = node_config.deliverable.template_title
        if (
            hasattr(node_config.deliverable, "output_filename")
            and node_config.deliverable.output_filename
        ):
            deliverable_reqs["output_filename"] = node_config.deliverable.output_filename
        if (
            hasattr(node_config.deliverable, "format_hints")
            and node_config.deliverable.format_hints
        ):
            deliverable_reqs["format_hints"] = node_config.deliverable.format_hints
        if "template_title" not in deliverable_reqs:
            deliverable_reqs["template_title"] = node_config.deliverable_type

        # P1-1: Get shared_context from execution_context
        shared_context = execution_context.get("shared_context", {})

        # F4: Get docs_context from execution_context
        docs_context = execution_context.get("docs_context", [])

        return IndependentAgentInput(
            task_name=node_config.task.name,
            task_description=node_config.task.description,
            role_supplement=node_config.task.role_supplement,
            deliverable_requirements=deliverable_reqs,
            original_context_summary=summary,
            chained_deliverables_summary=chained_summary,
            iteration_feedback=iteration_feedback,
            shared_context=shared_context,
            docs_context=docs_context,  # F4: 传递 docs_context
        )

    def build_evaluator_input(
        self,
        execution_context: NodeExecutionContext,
        deliverable: dict[str, Any] | None,
    ) -> EvaluatorAgentInput:
        """构建 EvaluatorAgent 的输入。

        P0-3: Evaluator 必须评审工具写盘后的正式文档正文，
        不允许退回到 deliverable.summary。

        Args:
            execution_context: 统一的节点执行上下文
            deliverable: 交付物字典 (必须包含 file_path)

        Returns:
            EvaluatorAgentInput 结构

        Raises:
            ValueError: If file_path is missing or None
            FileNotFoundError: If file_path doesn't exist
        """
        if not deliverable:
            raise ValueError("deliverable is required for evaluation")

        # P0-3: file_path is REQUIRED, no fallback
        file_path = deliverable.get("file_path")
        if not file_path:
            raise ValueError("file_path is required for evaluation")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Deliverable file not found: {file_path}")

        # P0-3: Always read full content from file
        deliverable_body = path.read_text(encoding="utf-8")

        # P0-2: Extract original context summary
        original_context = execution_context.get("original_context", {})
        original_summary = _extract_original_context_summary(original_context)

        # Story 25.3: Load criteria directly from NodeLoader instead of context
        node_id = execution_context.get("node_id")
        if not node_id:
            raise ValueError("node_id is required in execution_context")

        # Lazy import to avoid circular imports
        from autoBMAD.nodes.loader import NodeLoader

        node_config = NodeLoader.load(node_id)
        criteria = node_config.evaluator.criteria if node_config.evaluator else []

        return EvaluatorAgentInput(
            task_name=node_config.task.name,
            task_description=node_config.task.description,
            original_context_summary=original_summary,
            deliverable_artifact=deliverable,
            deliverable_body=deliverable_body,
            criteria=criteria,
        )

    # ==== 旧方法：保持向后兼容 ====
    def build_independent_context(
        self,
        subject_context: dict[str, Any] | None = None,
        previous_deliverables: dict[str, Any] | None = None,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build context for Independent agent with full access.

        The Independent agent receives complete access to all context data
        including private reasoning, tool call history, and iteration feedback.

        Args:
            subject_context: The subject/task context for the agent.
            previous_deliverables: Previous deliverables from prior iterations.
            iteration_feedback: Feedback from previous iterations.

        Returns:
            Dictionary containing all context fields with access_level="full".
        """
        self._logger.info(
            "Building independent context",
            access_level="full",
        )

        context: dict[str, Any] = {
            "subject_context": subject_context,
            "previous_deliverables": previous_deliverables,
            "iteration_feedback": iteration_feedback,
            "access_level": "full",
        }

        return context

    def build_evaluator_context(
        self,
        subject_context: dict[str, Any] | None = None,
        deliverable: dict[str, Any] | None = None,
        criteria: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build context for Evaluator agent with restricted access.

        The Evaluator agent only receives public, non-private context.
        This method validates that no private fields are present in the
        deliverable before constructing the context.

        Args:
            subject_context: The subject/task context for evaluation.
            deliverable: The deliverable to evaluate (validated for private fields).
            criteria: Evaluation criteria to assess the deliverable.

        Returns:
            Dictionary containing only public fields with access_level="restricted".

        Raises:
            ContextIsolationError: If private fields are detected in the context.
        """
        self._logger.info(
            "Building evaluator context (restricted)",
            access_level="restricted",
        )

        # Validate deliverable doesn't contain private fields using ContextValidator
        if deliverable is not None:
            result = self._validator_instance.validate_isolation(deliverable)
            if not result.valid:
                # Build error message from validation issues
                issues_str = "; ".join(f"{issue.field}: {issue.message}" for issue in result.issues)
                raise ContextIsolationError(
                    f"Private fields found in deliverable: {issues_str}",
                    violation_type="private_field_leak",
                    resource=result.issues[0].field if result.issues else "unknown",
                    target_context="evaluator",
                )

        context: dict[str, Any] = {
            "subject_context": subject_context,
            "deliverable": deliverable,
            "criteria": criteria,
            "access_level": "restricted",
        }

        return context


def _extract_original_context_summary(original_context: Any) -> str:
    """Extract a stable summary from normalized or legacy original context."""
    if isinstance(original_context, str):
        return original_context

    if not isinstance(original_context, dict):
        return str(original_context)

    raw_content = original_context.get("content")
    if isinstance(raw_content, str) and raw_content:
        return raw_content

    subject_context = original_context.get("subject_context")
    if isinstance(subject_context, dict):
        nested_content = subject_context.get("content")
        if isinstance(nested_content, str) and nested_content:
            return nested_content

    if original_context:
        return json.dumps(original_context, ensure_ascii=False)

    return ""


# Re-export ContextIsolationError for convenience
__all__ = [
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
]

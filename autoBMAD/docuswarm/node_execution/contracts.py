"""Node Execution Contracts - Single Context Protocol.

This module defines the core data structures for the unified NodeExecutionContext
protocol, eliminating guesswork and wrapping between executor, DualAgentNode,
and Agents.

Based on: P0 Single Context Protocol Implementation Design
"""

from typing import Any, TypedDict


class DeliverableArtifact(TypedDict):
    """交付物元数据 - 文件层为唯一真相。"""

    title: str
    summary: str
    file_path: str
    sha256: str
    word_count: int
    section_index: list[str]
    content_type: str


class NodeExecutionContext(TypedDict, total=False):
    """统一节点执行上下文 - 仅包含运行时动态字段。"""

    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]
    iteration_feedback: dict[str, Any] | None
    docs_context: list[dict[str, Any]]
    deliverable_requirements: dict[str, Any]
    deliverable_type: str


class IndependentAgentInput(TypedDict, total=False):
    """IndependentAgent 输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""

    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: dict[str, Any]
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    shared_context: dict[str, Any]
    docs_context: list[dict[str, Any]]  # F4: docs_context 传递链


class EvaluatorAgentInput(TypedDict, total=False):
    """EvaluatorAgent 输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""

    task_name: str
    task_description: str
    original_context_summary: str
    deliverable_artifact: dict[str, Any]
    deliverable_body: str
    criteria: list[dict[str, Any]]


IndependentOutput = dict[str, Any]
EvaluatorOutput = dict[str, Any]
__all__ = [
    "NodeExecutionContext",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
    "DeliverableArtifact",
    "IndependentOutput",
    "EvaluatorOutput",
]

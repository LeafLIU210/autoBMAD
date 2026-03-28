"""Node Execution Contracts - Single Context Protocol.

This module defines the core data structures for the unified NodeExecutionContext
protocol, eliminating guesswork and wrapping between executor, DualAgentNode,
and Agents.

Based on: P0 Single Context Protocol Implementation Design
"""

from typing import Any, TypedDict


class DeliverableRequirements(TypedDict, total=False):
    """交付物要求"""

    required_sections: list[str]
    template_title: str
    output_filename: str
    format_hints: dict[str, Any]


class DeliverableArtifact(TypedDict):
    """
    交付物元数据 - 文件层为唯一真相。

    状态层只保存 metadata，完整内容通过 file_path 从磁盘读取。
    这是方案 B (Single Truth) 的核心数据结构。
    """

    title: str
    summary: str  # 简短摘要 (1-2句)，不是完整内容
    file_path: str  # 指向磁盘文件的路径
    sha256: str  # 文件内容的 SHA256 哈希 (64字符)
    word_count: int  # 字数统计
    section_index: list[str]  # 章节索引 (提取的 ## 标题列表)
    content_type: str  # 内容类型: "markdown"


class NodeExecutionContextRequired(TypedDict):
    """
    统一节点执行上下文。

    这是跨越 executor -> DualAgentNode -> IndependentAgent/EvaluatorAgent 的单一协议。
    不允许在层间传 str(context_json) 作为主协议。
    不允许 agent 端再去"猜字段"。
    不允许 task 与 subject_context 重复承载同一含义。
    """

    # === 身份标识 ===
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int

    # === 任务契约 ===
    task_name: str
    task_description: str
    role_supplement: str

    # === 交付物契约 ===
    deliverable_type: str
    deliverable_requirements: DeliverableRequirements

    # === 上下文数据 ===
    original_context: dict[str, Any]  # 用户输入的原始上下文
    chained_deliverables: list[dict[str, Any]]  # 上游节点交付物
    shared_context: dict[str, Any]  # 跨节点共享上下文

    # === 迭代状态 ===
    iteration_feedback: dict[str, Any] | None

    # === 扩展上下文 ===
    docs_context: list[dict[str, Any]]


class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    """Extended execution context fields that are optional during migration."""

    evaluator_criteria: list[dict[str, Any]]


class IndependentAgentInput(TypedDict, total=False):
    """
    IndependentAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。
    """

    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: DeliverableRequirements
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    persona_context: dict[str, Any]  # persona 加载的额外上下文
    shared_context: dict[str, Any]  # P1-1: 跨节点共享上下文


class EvaluatorAgentInput(TypedDict, total=False):
    """
    EvaluatorAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。
    """

    task_name: str
    task_description: str
    original_context_summary: str  # P0-2: 原始需求摘要
    deliverable_artifact: dict[str, Any]  # 交付物元数据
    deliverable_body: str  # 交付物正文（从文件读取）
    criteria: list[dict[str, Any]]


# Type aliases for backward compatibility
IndependentOutput = dict[str, Any]
EvaluatorOutput = dict[str, Any]


__all__ = [
    "DeliverableRequirements",
    "DeliverableArtifact",
    "NodeExecutionContext",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
    "IndependentOutput",
    "EvaluatorOutput",
]

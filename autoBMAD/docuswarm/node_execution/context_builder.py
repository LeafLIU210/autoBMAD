"""Node Execution Context Builder - Single Context Protocol.

This module provides the NodeExecutionContextBuilder for building unified
NodeExecutionContext instances from node configurations and runtime state.

Based on: P0 Single Context Protocol Implementation Design
"""

from typing import Any

from autoBMAD.docuswarm.nodes.loader import NodeConfig, NodeLoader

from .contracts import DeliverableRequirements, NodeExecutionContext


class NodeExecutionContextBuilder:
    """
    构建统一的 NodeExecutionContext。

    兼容旧 node.yaml schema，同时支持未来新 schema。
    """

    def __init__(self, loader: NodeLoader | None = None) -> None:
        self.loader = loader or NodeLoader()

    def build(
        self,
        pipeline_id: str,
        node_id: str,
        original_context: dict[str, Any],
        chained_deliverables: list[dict[str, Any]] | None = None,
        shared_context: dict[str, Any] | None = None,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> NodeExecutionContext:
        """
        构建 NodeExecutionContext。

        Args:
            pipeline_id: 流水线ID
            node_id: 节点ID
            original_context: 原始上下文（用户输入）
            chained_deliverables: 链式上游交付物
            shared_context: 共享上下文
            iteration_feedback: 迭代反馈

        Returns:
            完整的 NodeExecutionContext
        """
        # 1. 加载节点配置
        node_config = self.loader.load(node_id)

        # 2. 构建 DeliverableRequirements
        deliverable_reqs = self._build_deliverable_requirements(node_config)

        # 3. 组装上下文
        return NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=node_id,
            node_name=node_config.name,
            node_order=node_config.sequence,
            # 任务契约 - 从 task 部分读取
            task_name=node_config.task.get("name", node_config.name),
            task_description=node_config.description or node_config.task.get("description", ""),
            role_supplement=node_config.task.get("role_supplement", ""),
            # 交付物契约
            deliverable_type=node_config.deliverable_type,
            deliverable_requirements=deliverable_reqs,
            # 上下文数据
            original_context=original_context,
            chained_deliverables=chained_deliverables or [],
            shared_context=shared_context or {},
            # 迭代状态
            iteration_feedback=iteration_feedback,
            # 扩展上下文（默认空，由上层填充）
            docs_context=[],
            evaluator_criteria=node_config.evaluator.get("criteria", []),
        )

    def _build_deliverable_requirements(
        self,
        node_config: NodeConfig,
    ) -> DeliverableRequirements:
        """
        从 NodeConfig 构建 DeliverableRequirements。

        从 deliverable 部分读取:
        - required_sections
        - template_title
        - output_filename
        - format_hints
        """
        reqs: DeliverableRequirements = {}

        # 从 node_config 的 deliverable 字段提取
        if node_config.deliverable:
            if "required_sections" in node_config.deliverable:
                reqs["required_sections"] = node_config.deliverable["required_sections"]
            if "template_title" in node_config.deliverable:
                reqs["template_title"] = node_config.deliverable["template_title"]
            if "output_filename" in node_config.deliverable:
                reqs["output_filename"] = node_config.deliverable["output_filename"]
            if "format_hints" in node_config.deliverable:
                reqs["format_hints"] = node_config.deliverable["format_hints"]

        # 默认 template_title (回退到 deliverable_type)
        if "template_title" not in reqs:
            reqs["template_title"] = node_config.deliverable_type

        return reqs


def create_context_builder(loader: NodeLoader | None = None) -> NodeExecutionContextBuilder:
    """工厂函数，创建 NodeExecutionContextBuilder 实例。"""
    return NodeExecutionContextBuilder(loader=loader)

"""Node Prompt Contract Builder - 节点 Prompt 契约构建器.

This module provides the NodePromptContractBuilder for building structured
prompt contracts from NodeExecutionContext.

Based on: P0 Node Prompt Injection Plan - 方案 B
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from autoBMAD.docuswarm.node_execution.contracts import (
        NodeExecutionContext,
    )


class PromptSection(TypedDict):
    """Prompt 章节."""

    title: str
    content: str


class IndependentPromptContract(TypedDict):
    """Independent Agent 的 Prompt 契约."""

    persona_section: str
    task_section: str
    deliverable_section: str
    context_section: str
    instructions_section: str


class EvaluatorPromptContract(TypedDict):
    """Evaluator Agent 的 Prompt 契约."""

    task_section: str
    criteria_section: str
    deliverable_section: str
    context_section: str
    deliverable_body: str  # P0 Single Truth: 完整的交付物正文


class NodePromptContractBuilder:
    """构建 Independent/Evaluator Agent 的 Prompt 契约.

    从 NodeExecutionContext 提取节点契约，渲染为结构化的 prompt 章节。
    兼容旧 schema（当前 node.yaml），同时支持未来新 schema。

    Example:
        >>> builder = NodePromptContractBuilder()
        >>> context = build_node_execution_context(...)
        >>> contract = builder.build_independent_contract(context)
        >>> system_prompt = builder.render_independent_system_prompt(contract)
        >>> user_prompt = builder.render_independent_user_prompt(contract)
    """

    def __init__(self) -> None:
        """初始化 builder."""
        pass

    def build_independent_contract(
        self,
        context: NodeExecutionContext,
    ) -> IndependentPromptContract:
        """构建 IndependentPromptContract.

        Args:
            context: 节点执行上下文.

        Returns:
            IndependentPromptContract with all sections.
        """
        return {
            "persona_section": self._build_persona_section(context),
            "task_section": self._build_task_section(context),
            "deliverable_section": self._build_deliverable_section(context),
            "context_section": self._build_context_section(context),
            "instructions_section": self._build_instructions_section(),
        }

    def build_evaluator_contract(
        self,
        context: NodeExecutionContext,
        deliverable_body: str,
    ) -> EvaluatorPromptContract:
        """构建 EvaluatorPromptContract.

        Args:
            context: 节点执行上下文.
            deliverable_body: 待评审的交付物正文.

        Returns:
            EvaluatorPromptContract with all sections.
        """
        return {
            "task_section": self._build_evaluator_task_section(context),
            "criteria_section": self._build_criteria_section(context),
            "deliverable_section": self._build_evaluator_deliverable_section(deliverable_body),
            "context_section": self._build_evaluator_context_section(context),
            "deliverable_body": deliverable_body,  # P0 Single Truth
        }

    # ============= Independent Agent Sections =============

    def _build_persona_section(self, context: NodeExecutionContext) -> str:
        """构建 persona 章节."""
        # 延迟导入以避免循环导入
        from autoBMAD.docuswarm.agents.persona import PersonaLoader

        # 从 node_id 加载 persona
        node_id = context["node_id"]
        try:
            persona = PersonaLoader.load(node_id=node_id, use_cache=True)
            return PersonaLoader.format_system_prompt(persona, max_tokens=2000)
        except Exception:
            # 如果加载失败，返回基础 persona
            node_name = context.get("node_name", "Agent")
            task_name = context.get("task_name", "任务")
            return f"""## 角色身份

你是一位专业的{node_name}，负责{task_name}。
"""

    def _build_task_section(self, context: NodeExecutionContext) -> str:
        """构建任务章节.

        优先使用新 schema 字段 (task_name, task_description, role_supplement)，
        如果不存在则回退到旧字段 (node_name, description)。
        """
        # 字段映射（新 schema -> 旧 schema 回退）
        task_name = context.get("task_name") or context.get("node_name", "未知任务")
        task_description = context.get("task_description") or context.get("description", "")
        role_supplement = context.get("role_supplement", "")

        sections = [f"## 任务: {task_name}"]

        if task_description:
            sections.append(task_description)

        if role_supplement:
            sections.append(f"\n**角色补充**: {role_supplement}")

        return "\n".join(sections)

    def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
        """构建交付物章节."""
        reqs = context.get("deliverable_requirements", {})
        deliverable_type = context.get("deliverable_type", "")

        sections: list[str] = ["## 交付物要求"]

        # template_title (回退到 deliverable_type)
        template_title = reqs.get("template_title") or deliverable_type
        if template_title:
            sections.append(f"\n**文档标题**: {template_title}")

        # required_sections
        required_sections = reqs.get("required_sections", [])
        if required_sections:
            sections.append("\n**必须包含以下章节**:")
            for section in required_sections:
                sections.append(f"- {section}")

        # output_filename
        output_filename = reqs.get("output_filename", "")
        if output_filename:
            sections.append(f"\n**输出文件名**: {output_filename}")

        # format_hints
        format_hints = reqs.get("format_hints", {})
        if format_hints:
            sections.append("\n**格式要求**:")
            for key, value in format_hints.items():
                sections.append(f"- {key}: {value}")

        return "\n".join(sections) if len(sections) > 1 else ""

    def _build_context_section(self, context: NodeExecutionContext) -> str:
        """构建上下文章节."""
        sections: list[str] = []

        # 原始上下文
        original_context = context.get("original_context", {})
        if original_context:
            content = original_context.get("content", "")
            if content:
                sections.append(f"## 原始上下文\n{content}")

        # 上游交付物摘要
        chained = context.get("chained_deliverables", [])
        if chained:
            sections.append("\n## 上游交付物摘要")
            for item in chained:
                node_id = item.get("node_id", "unknown")
                title = item.get("title", "未命名")
                sections.append(f"- **{node_id}**: {title}")

        # 迭代反馈
        feedback = context.get("iteration_feedback")
        if feedback:
            sections.append("\n## 迭代反馈")
            score = feedback.get("alignment_score", 0)
            sections.append(f"上一轮评分: {score}")
            issues = feedback.get("issues_found", [])
            if issues:
                sections.append("需要改进的问题:")
                for issue in issues:
                    sections.append(f"- {issue}")

        return "\n".join(sections)

    def _build_instructions_section(self) -> str:
        """构建固定指令章节."""
        return """## Agent Instructions

You are an Independent Agent that creates deliverables and generates questions.

## Execution Workflow

1. **Create Deliverable**: Use the 'create_deliverable' tool to save your document
   - The tool accepts: title (string) and content (Markdown string)
   - This writes the deliverable to a .md file

2. **Generate Questions**: Formulate follow-up questions with priorities

3. **Return Execution Report**: After using tools, you MUST return a JSON response

## CRITICAL: Output Format

After executing tools, you MUST respond with ONLY this exact JSON structure:

```json
{
  "deliverable": {
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)"
  },
  "questions": [
    {
      "question": "Question text?",
      "priority": "blocking | clarifying | optional",
      "context": "Context or rationale for this question"
    }
  ],
  "action": "create_deliverable"
}
```

**Question Priorities**:
- **blocking**: Must be answered before proceeding
- **clarifying**: Help refine the deliverable
- **optional**: Nice-to-have for future consideration
"""

    # ============= Evaluator Agent Sections =============

    def _build_evaluator_task_section(self, context: NodeExecutionContext) -> str:
        """构建 Evaluator 的任务章节."""
        task_name = context.get("task_name") or context.get("node_name", "未知任务")
        task_description = context.get("task_description") or context.get("description", "")

        return f"""## 评审任务

你正在评审 **{task_name}** 节点的交付物。

{task_description}
"""

    def _build_criteria_section(self, context: NodeExecutionContext) -> str:
        """构建评分 criteria 章节."""
        # 从 context 或从 evaluator.yaml 加载
        criteria = context.get("evaluator_criteria", [])

        if not criteria:
            return "## 评分标准\n\n未配置评分标准。"

        sections: list[str] = ["## 评分标准"]
        for c in criteria:
            name = c.get("name", "未命名")
            description = c.get("description", "")
            weight = c.get("weight", 0)
            sections.append(f"\n- **{name}** (权重: {weight}): {description}")

        sections.append("\n### 评分指南")
        sections.append("- 0.0-0.3: 完全不满足标准")
        sections.append("- 0.4-0.6: 部分满足")
        sections.append("- 0.7-0.8: 良好满足")
        sections.append("- 0.9-1.0: 超出预期")

        return "\n".join(sections)

    def _build_evaluator_deliverable_section(self, deliverable_body: str) -> str:
        """构建 Evaluator 的交付物章节."""
        return f"""## 待评审交付物

{deliverable_body}
"""

    def _build_evaluator_context_section(self, context: NodeExecutionContext) -> str:
        """构建 Evaluator 的最小上下文章节."""
        # Evaluator 只需要最小上下文
        original_context = context.get("original_context", {})
        content = original_context.get("content", "") if original_context else ""

        if content:
            # 截断到合理长度（Evaluator 不需要完整上下文）
            max_len = 500
            if len(content) > max_len:
                content = content[:max_len] + "..."
            return f"""## 原始需求摘要

{content}
"""
        return ""

    # ============= Prompt 渲染 =============

    def render_independent_system_prompt(self, contract: IndependentPromptContract) -> str:
        """渲染 Independent Agent 的 system prompt.

        System prompt 包含稳定的角色身份和固定指令。
        """
        sections = [
            contract["persona_section"],
            contract["instructions_section"],
        ]
        return "\n\n".join(filter(None, sections))

    def render_independent_user_prompt(self, contract: IndependentPromptContract) -> str:
        """渲染 Independent Agent 的 user prompt.

        User prompt 包含动态的执行契约（任务、交付物要求、上下文）。
        """
        sections = [
            contract["task_section"],
            contract["deliverable_section"],
            contract["context_section"],
        ]
        return "\n\n".join(filter(None, sections))

    def render_evaluator_prompt(self, contract: EvaluatorPromptContract) -> str:
        """渲染 Evaluator Agent 的完整 prompt."""
        sections = [
            contract["task_section"],
            contract["criteria_section"],
            contract["context_section"],
            contract["deliverable_section"],
        ]
        return "\n\n".join(filter(None, sections))


def create_contract_builder() -> NodePromptContractBuilder:
    """工厂函数，创建 NodePromptContractBuilder 实例."""
    return NodePromptContractBuilder()

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
    from autoBMAD.nodes.loader import NodeDeliverableConfig


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
    skill_hint_section: str


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
        # F8 Fix: Initialize template loader for template loading
        from autoBMAD.docuswarm.prompts.template_loader import TemplateLoader

        self.template_loader = TemplateLoader()

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
        node_id = context.get("node_id", "")

        # Story 33.8: Load deliverable config for document count guidance
        deliverable_config = self._load_deliverable_config(node_id)

        return {
            "persona_section": self._build_persona_section(context),
            "task_section": self._build_task_section(context),
            "deliverable_section": self._build_deliverable_section(context),
            "context_section": self._build_context_section(context),
            "instructions_section": self._build_instructions_section(
                node_id=node_id, deliverable_config=deliverable_config
            ),
            "skill_hint_section": self._build_skill_hint_section(node_id),
        }

    def _load_deliverable_config(self, node_id: str) -> NodeDeliverableConfig | None:
        """Load deliverable config from NodeLoader for document count guidance.

        Story 33.8: Helper method to load deliverable configuration including
        max_deliverables for generating document count guidance.

        Args:
            node_id: The node identifier.

        Returns:
            NodeDeliverableConfig if loaded successfully, None otherwise.
        """
        if not node_id:
            return None

        try:
            from autoBMAD.nodes.loader import NodeLoader

            node_config = NodeLoader.load(node_id)
            return node_config.deliverable
        except Exception:
            # Graceful fallback: if loading fails, return None
            return None

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
        node_id = context.get("node_id")
        try:
            persona = PersonaLoader.load(node_id=node_id, use_cache=True)
            return PersonaLoader.format_system_prompt(persona, max_tokens=2000)
        except Exception:
            # Story 28.4: 如果加载失败，从 NodeLoader 读取 task_name
            node_name = context.get("node_name", "Agent")
            task_name = "任务"

            # 尝试从 NodeLoader 获取 task_name
            if node_id:
                try:
                    from autoBMAD.nodes.loader import NodeLoader

                    node_config = NodeLoader.load(node_id)
                    task_name = node_config.task.name
                except Exception:
                    pass  # 使用默认值

            return f"""## 角色身份

你是一位专业的{node_name}，负责{task_name}。
"""

    def _build_task_section(self, context: NodeExecutionContext) -> str:
        """构建任务章节.

        从 NodeLoader 直接读取任务配置（单来源原则），
        不再从 execution_context 中读取 task 字段。
        """
        # Story 28.4: 从 NodeLoader 直接读取任务配置
        node_id = context.get("node_id")

        if node_id:
            try:
                from autoBMAD.nodes.loader import NodeLoader

                node_config = NodeLoader.load(node_id)
                task_name = node_config.task.name
                task_description = node_config.task.description
                role_supplement = node_config.task.role_supplement
            except Exception:
                # 如果加载失败，回退到 node_name
                task_name = context.get("node_name", "未知任务")
                task_description = ""
                role_supplement = ""
        else:
            task_name = context.get("node_name", "未知任务")
            task_description = ""
            role_supplement = ""

        sections = [f"## 任务: {task_name}"]

        if task_description:
            sections.append(task_description)

        if role_supplement:
            sections.append(f"\n**角色补充**: {role_supplement}")

        return "\n".join(sections)

    def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
        """构建交付物章节.

        F8 Fix: Now loads template definitions from YAML files and injects
        structured template sections into the prompt.
        """
        reqs = context.get("deliverable_requirements", {})
        deliverable_type = context.get("deliverable_type", "")
        node_id = context.get("node_id", "")

        sections: list[str] = ["## 交付物要求"]

        # template_title (回退到 deliverable_type)
        template_title = reqs.get("template_title") or deliverable_type
        if template_title:
            sections.append(f"\n**文档标题**: {template_title}")

        # F8 Fix: Load and inject template sections from template file
        template_data = None
        if node_id:
            try:
                template_data = self._load_node_template(node_id, template_title)
                if template_data:
                    formatted_template = self._format_template_sections(template_data)
                    if formatted_template:
                        sections.append(formatted_template)
            except Exception:
                # Graceful fallback: if template loading fails, continue with basic config
                pass

        # required_sections (only if no template data was loaded)
        required_sections = reqs.get("required_sections", [])
        if required_sections and not template_data:
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

    def _load_node_template(
        self,
        node_id: str,
        template_id: str | None,
    ) -> dict | None:
        """Load template from docuswarm/templates/{node_id}_templates.yaml.

        F4 Fix: 支持模板 ID 映射和模糊匹配，提高模板查找成功率
        F8 Fix: Loads structured template definitions from node-specific
        template YAML files.

        Args:
            node_id: Node ID (e.g., "analyst", "pm")
            template_id: Template ID to find (e.g., "market_research")

        Returns:
            Matching template data dict, or None if not found.
        """
        from pathlib import Path

        # F4 Fix: 应用模板 ID 映射
        mapped_template_id = self._apply_template_mapping(node_id, template_id)
        if mapped_template_id:
            template_id = mapped_template_id

        template_file = f"{node_id}_templates.yaml"
        templates_dir = Path(__file__).parent.parent / "templates"
        template_path = templates_dir / template_file

        try:
            import yaml

            with open(template_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                return None

            templates = data.get("templates", [])

            # Find matching template
            if template_id:
                for template in templates:
                    if template.get("template_id") == template_id:
                        return template
                    # Also match by title (case-insensitive)
                    if template.get("title", "").lower().replace(" ", "-") == template_id.lower().replace("_", "-"):
                        return template
                    # F4 Fix: 使用模糊匹配
                    if self._template_id_matches(template_id, template):
                        return template
            else:
                # If no template_id specified, return first template
                return templates[0] if templates else None

            # F4 Fix: 如果精确匹配失败，尝试模糊匹配查找最佳匹配
            if template_id:
                best_match = self._find_best_template_match(template_id, templates)
                if best_match:
                    return best_match

        except FileNotFoundError:
            # Template file doesn't exist - graceful fallback
            return None
        except Exception:
            # Any other error - graceful fallback
            return None

        return None

    def _apply_template_mapping(
        self, node_id: str, template_id: str | None
    ) -> str | None:
        """应用模板 ID 映射.

        F4 Fix: 将 deliverable_type 映射到 template_id

        Args:
            node_id: Node ID
            template_id: 输入的 template_id 或 deliverable_type

        Returns:
            映射后的 template_id，如果没有映射则返回 None
        """
        if not template_id:
            return None

        from pathlib import Path

        mapping_file = Path(__file__).parent.parent / "templates" / "template_mapping.yaml"

        if not mapping_file.exists():
            return None

        try:
            import yaml

            with open(mapping_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not config:
                return None

            mappings = config.get("mappings", {})
            node_mappings = mappings.get(node_id, {})

            # 直接查找映射
            mapped = node_mappings.get(template_id)
            if mapped:
                return mapped

            # 尝试标准化后的匹配
            template_id_normalized = template_id.lower().replace("-", "_")
            mapped = node_mappings.get(template_id_normalized)
            if mapped:
                return mapped

        except Exception:
            pass

        return None

    def _template_id_matches(self, lookup_id: str, template: dict) -> bool:
        """检查 template_id 是否匹配模板.

        F4 Fix: 支持模糊匹配

        Args:
            lookup_id: 要查找的 template_id
            template: 模板数据

        Returns:
            是否匹配
        """
        template_id = template.get("template_id", "")
        title = template.get("title", "")

        # 标准化比较
        lookup_normalized = lookup_id.lower().replace("-", "_").replace(" ", "_")
        template_id_normalized = template_id.lower().replace("-", "_").replace(" ", "_")
        title_normalized = title.lower().replace("-", "_").replace(" ", "_")

        # 直接匹配
        if lookup_normalized == template_id_normalized:
            return True

        # 标题包含匹配
        if lookup_normalized in title_normalized or title_normalized in lookup_normalized:
            return True

        # 关键词匹配
        lookup_parts = set(lookup_normalized.split("_"))
        template_parts = set(template_id_normalized.split("_"))
        title_parts = set(title_normalized.split("_"))

        # 如果有一半以上的关键词匹配，认为是匹配的
        if len(lookup_parts) > 0:
            template_match_ratio = len(lookup_parts & template_parts) / len(lookup_parts)
            title_match_ratio = len(lookup_parts & title_parts) / len(lookup_parts)
            if template_match_ratio >= 0.5 or title_match_ratio >= 0.5:
                return True

        return False

    def _find_best_template_match(
        self, lookup_id: str, templates: list[dict]
    ) -> dict | None:
        """查找最佳匹配的模板.

        F4 Fix: 当精确匹配失败时，使用启发式算法查找最佳匹配

        Args:
            lookup_id: 要查找的 template_id
            templates: 模板列表

        Returns:
            最佳匹配的模板，如果没有则返回 None
        """
        if not templates:
            return None

        lookup_normalized = lookup_id.lower().replace("-", "_")

        # 首先尝试完全匹配 template_id
        for template in templates:
            template_id = template.get("template_id", "").lower().replace("-", "_")
            if template_id == lookup_normalized:
                return template

        # 然后尝试包含匹配
        for template in templates:
            template_id = template.get("template_id", "").lower().replace("-", "_")
            title = template.get("title", "").lower().replace("-", "_").replace(" ", "_")

            if lookup_normalized in template_id or template_id in lookup_normalized:
                return template
            if lookup_normalized in title or title in lookup_normalized:
                return template

        # 最后返回第一个模板作为兜底
        return templates[0]

    def _format_template_sections(self, template_data: dict) -> str:
        """Format template sections into prompt text.

        F8 Fix: Formats structured template data into readable prompt sections.

        Args:
            template_data: Template data dict with sections, standards, etc.

        Returns:
            Formatted template guidance text.
        """
        sections: list[str] = []

        # Template sections
        template_sections = template_data.get("sections", [])
        if template_sections:
            sections.append("\n**文档结构要求**:")

            for section in template_sections:
                heading = section.get("heading", "")
                required = section.get("required", False)
                description = section.get("description", "")
                note = section.get("note", "")

                marker = "【必须】" if required else "【可选】"
                line = f"\n{marker} {heading}"

                if description:
                    line += f"\n   {description}"
                if note:
                    line += f"\n   注: {note}"

                sections.append(line)

        # Template standards
        standards = template_data.get("standards", {})
        if standards:
            sections.append("\n**文档标准**:")

            if standards.get("style_guide"):
                sections.append(f"- 风格指南: {standards['style_guide']}")
            if standards.get("diagram_format"):
                sections.append(f"- 图表格式: {standards['diagram_format']}")
            if standards.get("no_time_estimates"):
                sections.append("- 请勿包含时间估算")
            if standards.get("commonmark_strict"):
                sections.append("- 使用标准 CommonMark 格式")

        # Filename pattern
        filename_pattern = template_data.get("filename_pattern")
        if filename_pattern:
            sections.append(f"\n**文件名格式**: {filename_pattern}")

        return "\n".join(sections)

    def _build_context_section(self, context: NodeExecutionContext) -> str:
        """构建上下文章节."""
        sections: list[str] = []

        # 原始上下文
        original_context = context.get("original_context", {})
        if original_context:
            content = original_context.get("content", "")
            if content:
                sections.append(f"## 原始上下文\n{content}")

        # 引用文档（新增）
        docs = context.get("docs_context", [])
        if docs:
            sections.append("\n## 引用文档")
            for doc in docs:
                sections.append(f"\n### {doc.get('filename', 'unknown')}\n")
                # SummaryAgent produces 'summary' field; fallback resolver produces 'content'
                sections.append(doc.get("content") or doc.get("summary", ""))

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

    def build_document_count_guidance(
        self,
        deliverable_config: NodeDeliverableConfig | None = None,
        max_deliverables: int | None = None,
    ) -> str:
        """Build document count guidance based on max_deliverables configuration.

        Story 33.8: Generates explicit guidance text for LLM agents about how many
        documents they need to create for each node type, preventing constraint
        violations and ensuring proper multi-document workflow execution.

        Args:
            deliverable_config: NodeDeliverableConfig containing max_deliverables.
            max_deliverables: Optional direct max_deliverables value.

        Returns:
            Guidance text formatted with visual emphasis for LLM visibility.
            Returns empty string if config is missing or invalid.
        """
        # Extract max_deliverables from config or use provided value
        max_deliv = None
        if deliverable_config is not None:
            max_deliv = getattr(deliverable_config, "max_deliverables", None)
        if max_deliverables is not None:
            max_deliv = max_deliverables

        # Handle edge cases gracefully
        if max_deliv is None:
            return ""

        # Ensure we have a valid integer
        try:
            max_count = int(max_deliv)
        except (TypeError, ValueError):
            return ""

        # Handle invalid values gracefully (should be >= 1 per validation)
        if max_count < 1:
            max_count = 1

        # Generate appropriate guidance based on document count
        if max_count == 1:
            # Single-document nodes (analyst, pm, ux)
            return """## Document Count Guidance

**IMPORTANT**: You must create **exactly 1 deliverable** for this task.

Use the `create_deliverable` tool once to save your complete document.
"""
        else:
            # Multi-document nodes (architect: 2-4, po: 3-5)
            # Calculate minimum (half of max, rounded up, minimum 2)
            min_count = max(2, (max_count + 1) // 2)

            return f"""## Document Count Guidance

**IMPORTANT**: You must create **{min_count}-{max_count} deliverables** for this task.

Use the `create_deliverable` tool for each document you create. Ensure you create
at least {min_count} and no more than {max_count} deliverables to complete this task properly.
"""

    def _build_instructions_section(
        self,
        node_id: str = "",
        deliverable_config: NodeDeliverableConfig | None = None,
    ) -> str:
        """构建固定指令章节.

        Args:
            node_id: Node identifier for MCP tool name generation.
            deliverable_config: Optional deliverable config for document count guidance.
        """
        # TDD-07: Generate correct MCP tool name for create_deliverable
        if node_id:
            tool_name = f"mcp__docuswarm-deliverable-{node_id}__create_deliverable"
        else:
            tool_name = "create_deliverable"

        # Story 33.8: Build document count guidance
        doc_count_guidance = self.build_document_count_guidance(deliverable_config)
        if doc_count_guidance:
            doc_count_guidance = doc_count_guidance + "\n"

        return f"""## Agent Instructions

{doc_count_guidance}You are an Independent Agent that creates deliverables and generates questions.

## Available Tools

You have access to the following tools for document operations:

- `read_document`: Read file content from allowed directories
  - Use when: You need to examine existing files, reference documentation, or analyze source content
  - Typical parameters: file_path (path to the file within allowed directories)

- `list_documents`: List files in a specified directory
  - Use when: You need to discover what files exist, explore directory structure, or find relevant documents
  - Typical parameters: directory (path to list, must be within allowed directories)

- `grep_search`: Search for text patterns across files
  - Use when: You need to find specific content, search for keywords, or locate references across multiple files
  - Typical parameters: pattern (search regex/text), directory (where to search)

- `glob_search`: Find files matching a glob pattern
  - Use when: You need to find files by name pattern (e.g., all .md files), or discover files matching specific naming conventions
  - Typical parameters: pattern (glob pattern like "**/*.md"), directory (where to search)

- `create_deliverable`: Create output documents in the designated output directory
  - Use when: You need to save your work product, create the final deliverable document
  - Parameters: title (document title), content (full markdown content)

**Tool Selection Guidance**:
- Use `glob_search` to find files by name pattern, `grep_search` to find content within files
- Use `read_document` after finding relevant files to examine their contents
- Use `list_documents` to explore directories when you're unsure what files exist
- Always use `create_deliverable` to save your final output (never include full documents in JSON response)

## Execution Workflow

1. **Create Deliverable**: Use the '{tool_name}' tool to save your document
   - The tool accepts: title (string) and content (Markdown string)
   - This writes the deliverable to a .md file
   - The tool returns metadata including: file_path, sha256, word_count, section_index

2. **Generate Questions**: Formulate follow-up questions with priorities

3. **Return Execution Report**: After using tools, you MUST return a JSON response

## CRITICAL: Output Format

After executing tools, you MUST respond with ONLY this exact JSON structure:

```json
{{
  "deliverable": {{
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)",
    "file_path": "path/returned/by/tool.md",
    "sha256": "hash_returned_by_tool"
  }},
  "questions": [
    {{
      "question": "Question text?",
      "priority": "blocking | clarifying | optional",
      "context": "Context or rationale for this question"
    }}
  ],
  "action": "create_deliverable"
}}
```

**IMPORTANT**:
- The entire response must be valid JSON parseable by json.loads()
- Do NOT include markdown formatting outside the JSON
- You MUST include "file_path" and "sha256" from the {tool_name} tool output

**Question Priorities**:
- **blocking**: Must be answered before proceeding
- **clarifying**: Help refine the deliverable
- **optional**: Nice-to-have for future consideration
"""

    def _build_skill_hint_section(self, node_id: str) -> str:
        """构建 skill hint 章节.

        Story 32.7: 当 node_config.task.skill_ref 配置时，
        在 system prompt 中添加 skill 调用提示。

        Args:
            node_id: 节点标识符，用于加载节点配置。

        Returns:
            Skill hint 字符串，如果没有配置 skill_ref 则返回空字符串。
        """
        if not node_id:
            return ""

        try:
            from autoBMAD.nodes.loader import NodeLoader

            node_config = NodeLoader.load(node_id)
            skill_ref = node_config.task.skill_ref

            # Only add hint if skill_ref is truthy (not None, not empty string)
            if skill_ref:
                return f"Use the `{skill_ref}` skill to complete this task."
        except Exception:
            # Graceful handling: if anything fails, return empty string
            pass

        return ""

    # ============= Evaluator Agent Sections =============

    def _build_evaluator_task_section(self, context: NodeExecutionContext) -> str:
        """构建 Evaluator 的任务章节.

        从 NodeLoader 直接读取任务配置（单来源原则）。
        """
        # Story 28.4: 从 NodeLoader 直接读取任务配置
        node_id = context.get("node_id")

        if node_id:
            try:
                from autoBMAD.nodes.loader import NodeLoader

                node_config = NodeLoader.load(node_id)
                task_name = node_config.task.name
                task_description = node_config.task.description
            except Exception:
                # 如果加载失败，回退到 node_name
                task_name = context.get("node_name", "未知任务")
                task_description = ""
        else:
            task_name = context.get("node_name", "未知任务")
            task_description = ""

        return f"""## 评审任务

你正在评审 **{task_name}** 节点的交付物。

{task_description}
"""

    def _build_criteria_section(self, context: NodeExecutionContext) -> str:
        """构建评分 criteria 章节."""
        # Story 25.3: Load criteria directly from NodeLoader instead of context
        node_id = context.get("node_id")
        if node_id:
            try:
                # Lazy import to avoid circular imports
                from autoBMAD.nodes.loader import NodeLoader

                node_config = NodeLoader.load(node_id)
                criteria = node_config.evaluator.criteria if node_config.evaluator else []
            except Exception:
                criteria = []
        else:
            criteria = []

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

        System prompt 包含稳定的角色身份、skill hint 和固定指令。
        Skill hint 在配置时显示在 persona 之后、instructions 之前。
        """
        sections = [
            contract["persona_section"],
            contract["skill_hint_section"],
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

    def _build_evaluator_output_format(self) -> str:
        """构建 Evaluator 的 JSON 输出格式指令.

        TDD-09: 添加缺失的 JSON 输出格式，确保 LLM 返回可解析的 JSON。
        """
        return """## Output Format

You MUST respond with ONLY a JSON object. Do NOT include any other text,
markdown formatting, or explanation outside the JSON.

Respond with this exact JSON structure:

```json
{
    "criterion_scores": {"criterion_name": 0.0, "another_criterion": 0.0},
    "alignment_score": 0.0,
    "verdict": "APPROVED",
    "issues_found": ["issue description"],
    "suggestions": ["suggestion description"]
}
```

**Rules**:
- `criterion_scores`: A score (0.0-1.0) for EACH criterion listed above
- `alignment_score`: Weighted average of criterion scores
- `verdict`: One of "APPROVED", "NEEDS_REVISION", or "BLOCKED"
- `issues_found`: List of specific issues (empty list if none)
- `suggestions`: List of improvement suggestions (empty list if none)
- The response must be valid JSON parseable by json.loads()
- Do NOT wrap the JSON in markdown code blocks in your final response"""

    def render_evaluator_prompt(self, contract: EvaluatorPromptContract) -> str:
        """渲染 Evaluator Agent 的完整 prompt.

        TDD-09: 添加 output_format 章节确保 JSON 响应。
        """
        sections = [
            contract["task_section"],
            contract["criteria_section"],
            contract["context_section"],
            contract["deliverable_section"],
            self._build_evaluator_output_format(),
        ]
        return "\n\n".join(filter(None, sections))


def create_contract_builder() -> NodePromptContractBuilder:
    """工厂函数，创建 NodePromptContractBuilder 实例."""
    return NodePromptContractBuilder()

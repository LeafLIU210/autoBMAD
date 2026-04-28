# TDD 方案: NodePromptContractBuilder 实现 (方案 B)

> **关联研究报告**: [P0-node-prompt-injection-plan.md](../research/2026-03-13-p0-node-prompt-injection-plan.md)  
> **优先级**: P0 - 关键  
> **预估工期**: 2-3 天  
> **影响范围**: 
> - 新增: `prompts/contract_builder.py`
> - 修改: `agents/independent.py`, `agents/evaluator.py`
> - 修改: `node_execution/context_builder.py`

---

## 1. 问题分析

### 1.1 当前问题

当前 prompt 注入的主要问题不是"没 persona"，而是"只有 persona"。Independent Agent 目前稳定收到的是:
- persona
- 通用工具说明
- 原始任务文本

**但没有稳定收到:**
- 节点任务名称
- 节点任务描述
- 角色补充说明
- 交付物章节要求
- 输出标题或文件命名约束

### 1.2 代码问题示例

在 `independent.py` 中，`_format_system_prompt()` 只包含 persona 和通用指令：

```python
def _format_system_prompt(self) -> str:
    persona_prompt = PersonaLoader.format_system_prompt(self.persona, max_tokens=2000)
    instructions = """## Agent Instructions
You are an Independent Agent that creates deliverables...
"""
    return f"{persona_prompt}\n\n{instructions}"
```

**问题**: 节点契约（任务名称、描述、交付物要求）被埋在 `execute()` 方法的动态构建中，而不是显式注入。

### 1.3 目标

引入 `NodePromptContractBuilder`，将节点契约作为显式 prompt 输入：
- 兼容旧 schema（当前 node.yaml）
- 支持未来新 schema
- 让五个节点的 prompt 差异来自节点契约，而非仅 persona

---

## 2. 设计方案

### 2.1 核心架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NodePromptContractBuilder                         │
├─────────────────────────────────────────────────────────────────────┤
│  职责:                                                              │
│  - 从 NodeExecutionContext 提取节点契约                              │
│  - 构建 IndependentPromptContract / EvaluatorPromptContract         │
│  - 渲染最终 prompt 字符串                                            │
├─────────────────────────────────────────────────────────────────────┤
│  输入: NodeExecutionContext                                         │
│  输出:                                                              │
│    - IndependentAgent: persona_section + task_section + ...         │
│    - EvaluatorAgent: task_section + criteria_section + ...          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据契约

```python
# prompts/contract_builder.py

from typing import TypedDict


class PromptSection(TypedDict):
    """Prompt 章节"""
    title: str
    content: str


class IndependentPromptContract(TypedDict):
    """Independent Agent 的 Prompt 契约"""
    persona_section: str          # 角色身份
    task_section: str             # 任务契约（名称、描述、角色补充）
    deliverable_section: str      # 交付物要求（必选章节、标题约束）
    context_section: str          # 上下文摘要（原始+上游）
    instructions_section: str     # 固定指令（输出格式、工具规则）


class EvaluatorPromptContract(TypedDict):
    """Evaluator Agent 的 Prompt 契约"""
    task_section: str             # 节点身份和任务目标
    criteria_section: str         # 评分 criteria
    deliverable_section: str      # 待评审文档正文
    context_section: str          # 最小必要上下文
```

### 2.3 Prompt 结构分离

| 层级 | 内容 | 稳定性 | 所在位置 |
|------|------|--------|----------|
| **System Prompt** | 角色身份、工具规则、输出格式、安全约束 | 稳定 | `_format_system_prompt()` |
| **User Prompt** | 当前节点任务、原始上下文、上游摘要、交付要求 | 动态 | `_build_user_message()` |

---

## 3. 测试驱动开发计划

### Phase 1: 编写测试（红阶段）

#### Test 1: NodePromptContractBuilder 基础创建测试

```python
# tests/unit/test_contract_builder.py

import pytest
from autoBMAD.docuswarm.prompts.contract_builder import (
    NodePromptContractBuilder,
    IndependentPromptContract,
    EvaluatorPromptContract,
)
from autoBMAD.docuswarm.node_execution.contracts import (
    NodeExecutionContext,
    DeliverableRequirements,
)


class TestNodePromptContractBuilderCreation:
    """测试 NodePromptContractBuilder 初始化和基本功能."""
    
    def test_builder_initialization(self):
        """Test that builder can be initialized."""
        builder = NodePromptContractBuilder()
        assert builder is not None
    
    def test_build_independent_contract_returns_correct_type(self):
        """Test that build_independent_contract returns IndependentPromptContract."""
        # Arrange
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        # Act
        contract = builder.build_independent_contract(context)
        
        # Assert
        assert isinstance(contract, dict)
        assert "persona_section" in contract
        assert "task_section" in contract
        assert "deliverable_section" in contract
        assert "context_section" in contract
        assert "instructions_section" in contract
    
    def test_build_evaluator_contract_returns_correct_type(self):
        """Test that build_evaluator_contract returns EvaluatorPromptContract."""
        # Arrange
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        deliverable_body = "Sample deliverable content"
        
        # Act
        contract = builder.build_evaluator_contract(context, deliverable_body)
        
        # Assert
        assert isinstance(contract, dict)
        assert "task_section" in contract
        assert "criteria_section" in contract
        assert "deliverable_section" in contract
        assert "context_section" in contract


def create_sample_node_execution_context() -> NodeExecutionContext:
    """Helper function to create sample context for testing."""
    return {
        "pipeline_id": "test-pipeline-123",
        "node_id": "analyst",
        "node_name": "需求分析师",
        "node_order": 1,
        "task_name": "需求分析",
        "task_description": "分析用户需求，提取功能性和非功能性需求",
        "role_supplement": "专注于企业级软件系统的需求分析",
        "deliverable_type": "requirements_document",
        "deliverable_requirements": DeliverableRequirements(
            required_sections=["背景", "功能性需求", "非功能性需求", "约束条件"],
            template_title="需求分析文档",
            output_filename="requirements.md",
        ),
        "original_context": {"content": "用户想要一个电商系统"},
        "chained_deliverables": [],
        "shared_context": {},
        "iteration_feedback": None,
        "docs_context": [],
    }
```

#### Test 2: Independent Contract 内容测试

```python
class TestIndependentContractContent:
    """测试 IndependentPromptContract 各章节内容正确性."""
    
    def test_task_section_contains_task_name(self):
        """任务章节必须包含任务名称."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        assert context["task_name"] in contract["task_section"]
    
    def test_task_section_contains_task_description(self):
        """任务章节必须包含任务描述."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        assert context["task_description"] in contract["task_section"]
    
    def test_task_section_contains_role_supplement(self):
        """任务章节必须包含角色补充说明."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        assert context["role_supplement"] in contract["task_section"]
    
    def test_deliverable_section_contains_required_sections(self):
        """交付物章节必须包含所有必选章节."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        for section in context["deliverable_requirements"]["required_sections"]:
            assert section in contract["deliverable_section"]
    
    def test_deliverable_section_contains_template_title(self):
        """交付物章节必须包含模板标题."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        assert context["deliverable_requirements"]["template_title"] in contract["deliverable_section"]
    
    def test_context_section_contains_original_context(self):
        """上下文章节必须包含原始上下文."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_independent_contract(context)
        
        assert "原始上下文" in contract["context_section"]
    
    def test_context_section_contains_chained_deliverables(self):
        """上下文章节必须包含上游交付物摘要."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        context["chained_deliverables"] = [
            {"node_id": "pm", "title": "产品规划文档"}
        ]
        
        contract = builder.build_independent_contract(context)
        
        assert "上游交付物" in contract["context_section"]
        assert "pm" in contract["context_section"]
```

#### Test 3: Evaluator Contract 内容测试

```python
class TestEvaluatorContractContent:
    """测试 EvaluatorPromptContract 各章节内容正确性."""
    
    def test_task_section_contains_node_identity(self):
        """任务章节必须包含节点身份."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        
        contract = builder.build_evaluator_contract(context, "deliverable body")
        
        assert context["task_name"] in contract["task_section"]
    
    def test_criteria_section_contains_criteria_list(self):
        """评分章节必须包含 criteria 列表."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        # 添加 mock criteria
        context["evaluator_criteria"] = [
            {"name": "完整性", "description": "文档是否完整", "weight": 0.5},
            {"name": "准确性", "description": "内容是否准确", "weight": 0.5},
        ]
        
        contract = builder.build_evaluator_contract(context, "deliverable body")
        
        assert "完整性" in contract["criteria_section"]
        assert "准确性" in contract["criteria_section"]
    
    def test_deliverable_section_contains_body(self):
        """交付物章节必须包含待评审文档正文."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        deliverable_body = "这是待评审的文档内容"
        
        contract = builder.build_evaluator_contract(context, deliverable_body)
        
        assert deliverable_body in contract["deliverable_section"]
```

#### Test 4: Schema 兼容性测试（关键测试）

```python
class TestSchemaCompatibility:
    """测试旧 schema 和新 schema 的兼容性."""
    
    def test_old_schema_without_task_section(self):
        """CRITICAL: 旧 schema（没有 task 字段）应该能正常工作.
        
        旧 node.yaml 可能没有 task 字段，需要从其他字段回退。
        """
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        # 模拟旧 schema: 清空 task 相关字段
        context["task_name"] = ""
        context["task_description"] = ""
        context["role_supplement"] = ""
        # 但 node_name 和 description 有值
        context["node_name"] = "需求分析师"
        context["description"] = "从旧字段读取的描述"
        
        contract = builder.build_independent_contract(context)
        
        # 应该从旧字段回退
        assert context["node_name"] in contract["task_section"]
        assert context["description"] in contract["task_section"]
    
    def test_old_schema_deliverable_mapping(self):
        """CRITICAL: 旧 schema 的 deliverable 字段映射正确.
        
        旧 node.yaml 可能只有 deliverable_type，没有 deliverable 字段。
        """
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        # 模拟旧 schema
        context["deliverable_requirements"] = DeliverableRequirements(
            template_title=context["deliverable_type"],  # 回退到 deliverable_type
        )
        
        contract = builder.build_independent_contract(context)
        
        assert context["deliverable_type"] in contract["deliverable_section"]
```

#### Test 5: Prompt 渲染测试

```python
class TestPromptRendering:
    """测试最终 prompt 字符串渲染."""
    
    def test_render_independent_system_prompt(self):
        """渲染 Independent Agent 的 system prompt."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        contract = builder.build_independent_contract(context)
        
        system_prompt = builder.render_independent_system_prompt(contract)
        
        # System prompt 应该包含 persona 和固定指令
        assert "persona" in system_prompt.lower() or "角色" in system_prompt
        assert "json" in system_prompt.lower() or "输出格式" in system_prompt
    
    def test_render_independent_user_prompt(self):
        """渲染 Independent Agent 的 user prompt."""
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        contract = builder.build_independent_contract(context)
        
        user_prompt = builder.render_independent_user_prompt(contract)
        
        # User prompt 应该包含动态内容
        assert context["task_name"] in user_prompt
        assert context["task_description"] in user_prompt
    
    def test_system_prompt_excludes_dynamic_content(self):
        """System prompt 不应该包含频繁变化的内容.
        
        这是关键设计原则：system prompt 稳定，user prompt 动态。
        """
        builder = NodePromptContractBuilder()
        context = create_sample_node_execution_context()
        contract = builder.build_independent_contract(context)
        
        system_prompt = builder.render_independent_system_prompt(contract)
        
        # 不应该包含可能频繁变化的内容
        assert context["task_description"] not in system_prompt
        assert "原始上下文" not in system_prompt
```

#### Test 6: Snapshot 测试（节点差异化）

```python
class TestNodeDifferentiation:
    """Snapshot 测试: 验证五个节点的 prompt 差异."""
    
    @pytest.mark.parametrize("node_id", ["analyst", "pm", "ux", "architect", "po"])
    def test_each_node_has_distinct_contract(self, node_id, snapshot):
        """CRITICAL: 每个节点应该有独特的 prompt 契约.
        
        这个测试确保五个节点不再只是"一个通用写作 agent 的五个角色外观"，
        而是五个有明确业务契约的专用节点。
        """
        builder = NodePromptContractBuilder()
        context = create_sample_node_context_for_node(node_id)
        
        contract = builder.build_independent_contract(context)
        user_prompt = builder.render_independent_user_prompt(contract)
        
        # 使用 snapshot 测试验证每个节点的 prompt
        assert user_prompt == snapshot


def create_sample_node_context_for_node(node_id: str) -> NodeExecutionContext:
    """为指定节点创建上下文."""
    node_configs = {
        "analyst": {
            "node_name": "需求分析师",
            "task_name": "需求分析",
            "task_description": "分析业务需求，提取功能性需求",
            "role_supplement": "专注于需求挖掘",
            "required_sections": ["背景", "功能性需求", "非功能性需求"],
        },
        "pm": {
            "node_name": "产品经理",
            "task_name": "产品规划",
            "task_description": "制定产品策略和路线图",
            "role_supplement": "专注于产品思维",
            "required_sections": ["市场分析", "产品定位", "路线图"],
        },
        "ux": {
            "node_name": "UX设计师",
            "task_name": "用户体验设计",
            "task_description": "设计用户界面和交互流程",
            "role_supplement": "专注于用户体验",
            "required_sections": ["用户画像", "信息架构", "交互设计"],
        },
        "architect": {
            "node_name": "架构师",
            "task_name": "系统设计",
            "task_description": "设计系统架构和技术方案",
            "role_supplement": "专注于技术架构",
            "required_sections": ["架构概览", "技术选型", "模块设计"],
        },
        "po": {
            "node_name": "产品负责人",
            "task_name": "PRD编写",
            "task_description": "编写产品需求文档",
            "role_supplement": "专注于需求文档化",
            "required_sections": ["产品概述", "功能需求", "验收标准"],
        },
    }
    
    config = node_configs.get(node_id, node_configs["analyst"])
    return {
        "pipeline_id": "test-pipeline",
        "node_id": node_id,
        "node_name": config["node_name"],
        "node_order": 1,
        "task_name": config["task_name"],
        "task_description": config["task_description"],
        "role_supplement": config["role_supplement"],
        "deliverable_type": f"{node_id}_document",
        "deliverable_requirements": DeliverableRequirements(
            required_sections=config["required_sections"],
            template_title=f"{config['node_name']}文档",
        ),
        "original_context": {"content": "测试上下文"},
        "chained_deliverables": [],
        "shared_context": {},
        "iteration_feedback": None,
        "docs_context": [],
    }
```

### Phase 2: 实现代码（绿阶段）

基于测试要求，实现 `contract_builder.py`：

```python
"""Node Prompt Contract Builder - 节点 Prompt 契约构建器.

This module provides the NodePromptContractBuilder for building structured
prompt contracts from NodeExecutionContext.

Based on: P0 Node Prompt Injection Plan - 方案 B
"""

from typing import TypedDict

from autoBMAD.docuswarm.agents.persona import PersonaLoader
from autoBMAD.docuswarm.node_execution.contracts import (
    DeliverableRequirements,
    NodeExecutionContext,
)


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
            "deliverable_section": self._build_evaluator_deliverable_section(
                deliverable_body
            ),
            "context_section": self._build_evaluator_context_section(context),
        }

    # ============= Independent Agent Sections =============

    def _build_persona_section(self, context: NodeExecutionContext) -> str:
        """构建 persona 章节."""
        # 从 node_id 加载 persona
        node_id = context["node_id"]
        try:
            persona = PersonaLoader.load(node_id=node_id, use_cache=True)
            return PersonaLoader.format_system_prompt(persona, max_tokens=2000)
        except Exception:
            # 如果加载失败，返回基础 persona
            return f"""## 角色身份

你是一位专业的{context['node_name']}，负责{context['task_name']}。
"""

    def _build_task_section(self, context: NodeExecutionContext) -> str:
        """构建任务章节.

        优先使用新 schema 字段 (task_name, task_description, role_supplement)，
        如果不存在则回退到旧字段 (node_name, description)。
        """
        # 字段映射（新 schema -> 旧 schema 回退）
        task_name = context.get("task_name") or context.get("node_name", "未知任务")
        task_description = (
            context.get("task_description") or context.get("description", "")
        )
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

        sections = ["## 交付物要求"]

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
        sections = []

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
        task_description = (
            context.get("task_description") or context.get("description", "")
        )

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

        sections = ["## 评分标准"]
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

    def render_independent_system_prompt(
        self, contract: IndependentPromptContract
    ) -> str:
        """渲染 Independent Agent 的 system prompt.

        System prompt 包含稳定的角色身份和固定指令。
        """
        sections = [
            contract["persona_section"],
            contract["instructions_section"],
        ]
        return "\n\n".join(filter(None, sections))

    def render_independent_user_prompt(
        self, contract: IndependentPromptContract
    ) -> str:
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
```

### Phase 3: 重构 Agent（重构阶段）

#### 重构 IndependentAgent

**重构前** (`independent.py`):
```python
@override
def _format_system_prompt(self) -> str:
    """Format system prompt with persona details."""
    persona_prompt = PersonaLoader.format_system_prompt(self.persona, max_tokens=2000)
    instructions = """## Agent Instructions
You are an Independent Agent that creates deliverables...
"""
    return f"{persona_prompt}\n\n{instructions}"

def _build_user_message(self, ...):
    """手动构建 user message."""
    sections = []
    sections.append(f"## 任务: {task_name}")
    ...
```

**重构后**:
```python
from autoBMAD.docuswarm.prompts.contract_builder import (
    NodePromptContractBuilder,
    create_contract_builder,
)

class IndependentAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(config, session_manager=session_manager)
        self.contract_builder = create_contract_builder()
        # ...

    @override
    def _format_system_prompt(
        self,
        contract: IndependentPromptContract | None = None,
    ) -> str:
        """Format system prompt with contract.
        
        Args:
            contract: Optional pre-built contract. If not provided,
                     will use legacy persona-only format.
        """
        if contract:
            return self.contract_builder.render_independent_system_prompt(contract)
        
        # Legacy fallback
        persona_prompt = PersonaLoader.format_system_prompt(self.persona, max_tokens=2000)
        instructions = """## Agent Instructions..."""
        return f"{persona_prompt}\n\n{instructions}"
    
    async def execute_with_input(
        self,
        agent_input: "IndependentAgentInput",
        pipeline_id: str,
    ) -> IndependentOutput:
        """Execute with structured input using contract builder."""
        # ... setup code ...
        
        # Build contract from agent_input
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
        
        context = NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=self.node_id,
            node_name=agent_input["task_name"],
            node_order=0,
            task_name=agent_input["task_name"],
            task_description=agent_input["task_description"],
            role_supplement=agent_input["role_supplement"],
            deliverable_type="",
            deliverable_requirements=agent_input["deliverable_requirements"],
            original_context={"content": agent_input["original_context_summary"]},
            chained_deliverables=agent_input["chained_deliverables_summary"],
            shared_context={},
            iteration_feedback=agent_input["iteration_feedback"],
            docs_context=[],
        )
        
        contract = self.contract_builder.build_independent_contract(context)
        
        # Use contract to format prompts
        system_prompt = self._format_system_prompt(contract)
        user_prompt = self.contract_builder.render_independent_user_prompt(contract)
        
        # ... rest of execution ...
```

#### 重构 EvaluatorAgent

**重构后**:
```python
class EvaluatorAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(config, session_manager=session_manager)
        self.contract_builder = create_contract_builder()
        # ...
    
    async def execute_with_input(
        self,
        agent_input: "EvaluatorAgentInput",
    ) -> EvaluatorOutput:
        """Execute with structured input using contract builder."""
        # Build context from agent_input
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
        
        context = NodeExecutionContext(
            pipeline_id="",
            node_id=self.node_id,
            node_name=agent_input["task_name"],
            node_order=0,
            task_name=agent_input["task_name"],
            task_description=agent_input["task_description"],
            role_supplement="",
            deliverable_type="",
            deliverable_requirements={},
            original_context={},
            chained_deliverables=[],
            shared_context={},
            iteration_feedback=None,
            docs_context=[],
            evaluator_criteria=agent_input["criteria"],
        )
        
        contract = self.contract_builder.build_evaluator_contract(
            context,
            deliverable_body=agent_input["deliverable_body"],
        )
        
        prompt = self.contract_builder.render_evaluator_prompt(contract)
        
        # ... call LLM with prompt ...
```

---

## 4. 验证清单

### 4.1 单元测试验证

```bash
# 运行所有 ContractBuilder 测试
pytest tests/unit/test_contract_builder.py -v

# 验证覆盖率
pytest tests/unit/test_contract_builder.py --cov=autoBMAD.docuswarm.prompts.contract_builder --cov-report=term-missing
```

**期望结果**:
- [ ] 所有测试通过
- [ ] 代码覆盖率 >= 90%
- [ ] 无类型检查错误 (`basedpyright`)
- [ ] 无代码风格错误 (`ruff`)

### 4.2 Snapshot 测试验证

```bash
# 运行 snapshot 测试
pytest tests/unit/test_contract_builder.py::TestNodeDifferentiation -v --snapshot-update

# 验证五个节点的 prompt 差异
pytest tests/unit/test_contract_builder.py::TestNodeDifferentiation -v
```

**期望结果**:
- [ ] analyst/pm/ux/architect/po 五个节点的 prompt 都有差异
- [ ] 差异不仅来自 persona，还来自 task_section 和 deliverable_section

### 4.3 旧 Schema 兼容性验证

```bash
# 使用旧 node.yaml 运行集成测试
pytest tests/integration/test_pipeline_with_old_schema.py -v
```

**期望结果**:
- [ ] 当前旧 node.yaml 不改写也能注入 prompt
- [ ] required_sections 被正确渲染为稳定清单

### 4.4 集成测试

```bash
# 运行完整 pipeline 测试
pytest tests/integration/test_pipeline_lifecycle.py -v

# 手动测试
python -m autoBMAD.docuswarm start -c docs/test_context.md
```

---

## 5. 验收标准

### 5.1 功能验收

- [ ] Independent prompt 中明确出现节点名称、任务描述、必选章节
- [ ] Evaluator prompt 中明确出现 criteria 和正式待评审文档
- [ ] 五个节点的 prompt 差异不再只来自 persona，而是来自节点契约
- [ ] 旧 schema（无 task 字段）能正常工作，自动回退到旧字段

### 5.2 代码验收

- [ ] 新增 `prompts/contract_builder.py` 文件
- [ ] 新增 `tests/unit/test_contract_builder.py` 测试文件
- [ ] `IndependentAgent._format_system_prompt()` 支持 contract 参数
- [ ] `IndependentAgent.execute_with_input()` 使用 contract builder
- [ ] `EvaluatorAgent.execute_with_input()` 使用 contract builder
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] basedpyright + ruff 检查通过

### 5.3 性能验收

- [ ] Prompt 构建时间 < 10ms（单次调用）
- [ ] Persona 加载使用缓存（不重复读取文件）

---

## 6. 风险评估与缓解

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|---------|
| 旧 schema 兼容性问题 | 中 | 高 | 完整的兼容性测试；字段回退机制 |
| Prompt 长度超限 | 低 | 高 | 上下文自动截断；长度监控日志 |
| Persona 加载性能下降 | 低 | 中 | 使用缓存；延迟加载 |
| 五个节点差异化不明显 | 中 | 中 | Snapshot 测试；人工审核 prompt |

---

## 7. 实施步骤

### Step 1: 创建测试文件（红）
1. 创建 `tests/unit/test_contract_builder.py`
2. 运行测试，确保全部失败

### Step 2: 实现 ContractBuilder（绿）
1. 创建 `prompts/contract_builder.py`
2. 实现所有方法，使测试通过

### Step 3: 重构 IndependentAgent（重构）
1. 修改 `_format_system_prompt()` 支持 contract
2. 修改 `execute_with_input()` 使用 contract builder
3. 运行测试确保通过

### Step 4: 重构 EvaluatorAgent（重构）
1. 修改 `execute_with_input()` 使用 contract builder
2. 运行测试确保通过

### Step 5: 验证与优化
1. 运行所有单元测试
2. 运行所有集成测试
3. 运行 snapshot 测试
4. 代码审查和优化

---

## 8. 相关文档

- [NodeExecutionContext 深度研究报告](../research/2026-03-13-p0-single-context-protocol-deep-research-report.md)
- [方案B实施设计](../research/2026-03-13-p0-single-context-protocol-implementation-design.md)
- [单一上下文协议计划](../research/2026-03-13-p0-single-context-protocol-plan.md)
- [Architecture Document](../architecture.md)
- [Design Document](../design.md)

---

> **备注**: 本方案基于测试驱动开发（TDD）原则，先写测试再实现代码，确保每个功能都有测试覆盖，并在重构过程中保持测试通过。

# Epic 22: Persona 角色上下文与 System Prompt 重构

**Epic ID**: EPIC-22  
**Version**: 1.0  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days

---

## 1. Epic Overview

### 1.1 Summary

重构 Persona 系统和 IndependentAgent 的 System Prompt 构建，实现 BMM 角色上下文的完整嵌入。

### 1.2 Business Value

- **角色丰富化**: 为每个节点提供详细的 BMM 角色上下文
- **个性化表达**: 通过 communication_style 实现角色差异化
- **System Prompt 重构**: 构建更丰富的 LLM 提示

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Persona 扩展 | 支持 communication_style 字段 |
| System Prompt | 包含 Persona、Task、Deliverable、Instructions 四部分 |
| 五节点配置 | analyst、pm、ux、architect、po 都有完整 persona.json |
| 向后兼容 | 旧 persona.json 无新字段时仍可加载 |

### 1.4 Dependencies

- **Prerequisites**: EPIC-21 完成 (NodeConfig 结构稳定)
- **Blocks**: EPIC-23 (废弃代码移除), EPIC-24 (集成测试)

---

## 2. Stories

### Story 22.1: 扩展 Persona 数据类

As a developer,  
I want to extend the Persona dataclass with communication_style,  
So that agents can have unique communication personalities.

**Acceptance Criteria:**

**Given** the Persona dataclass in persona.py  
**When** I add the communication_style field with default empty string  
**Then** existing persona.json files without this field still load successfully  
**And** new persona.json files can include rich communication style descriptions

**Given** a Persona instance with communication_style set  
**When** I access the communication_style property  
**Then** it returns the configured style text

**Technical Details:**

```python
@dataclass
class Persona:
    """BMM-aligned agent persona.
    
    All content is pre-processed from _bmad/bmm/agents/*.md <persona> blocks
    and embedded in persona.json. Runtime zero external dependency.
    """
    name: str
    role: str
    identity: str
    communication_style: str = ""  # 新增，默认空字符串保持兼容
    expertise: list[str] = field(default_factory=list)
    principles: list[str] = field(default_factory=list)
    output_format: dict[str, Any] = field(default_factory=dict)
    # 移除: tools (统一使用 IndependentAgent tool)
```

---

### Story 22.2: 实现 _format_persona_section()

As a developer,  
I want to implement a method to format the persona section of system prompt,  
So that it displays BMM-aligned role context.

**Acceptance Criteria:**

**Given** a Persona instance with all fields populated  
**When** I call _format_persona_section(persona)  
**Then** it returns a formatted string containing:
  - "# Persona: {name}" header
  - "**Role**: {role}" line
  - "## Identity" section with identity text
  - "## Communication Style" section (if not empty)
  - "## Expertise" section with bullet list
  - "## Guiding Principles" section with bullet list

**Given** a Persona without communication_style  
**When** the section is formatted  
**Then** the Communication Style section is omitted

**Technical Details:**

```python
@staticmethod
def _format_persona_section(persona: Persona) -> str:
    """Format persona section with BMM role context."""
    expertise_list = "\n".join(f"- {e}" for e in persona.expertise)
    principles_list = "\n".join(f"- {p}" for p in persona.principles)
    
    communication_section = ""
    if persona.communication_style:
        communication_section = f"""
## Communication Style
{persona.communication_style}
"""
    
    return f"""# Persona: {persona.name}
**Role**: {persona.role}

## Identity
{persona.identity}
{communication_section}
## Expertise
{expertise_list}

## Guiding Principles
{principles_list}
"""
```

---

### Story 22.3: 实现 _format_task_section()

As a developer,  
I want to implement a method to format the task section of system prompt,  
So that agents understand their specific task assignments.

**Acceptance Criteria:**

**Given** a NodeTaskConfig instance  
**When** I call _format_task_section(task)  
**Then** it returns a formatted string containing:
  - "## Task Assignment" header
  - Task name reference
  - Task description
  - "### Role Context" subsection (if role_supplement exists)

**Given** a task with role_supplement  
**When** the section is formatted  
**Then** the Role Context subsection includes the supplement text

**Technical Details:**

```python
@staticmethod
def _format_task_section(task: NodeTaskConfig | None) -> str:
    """Format task assignment section."""
    if task is None:
        return "## Task Assignment\nCreate the required deliverable."
    
    role_context = ""
    if task.role_supplement:
        role_context = f"""
### Role Context
{task.role_supplement}
"""
    
    return f"""## Task Assignment
You are executing the '{task.name}' task.

{task.description}
{role_context}
"""
```

---

### Story 22.4: 实现 _format_deliverable_section()

As a developer,  
I want to implement a method to format the deliverable section of system prompt,  
So that agents understand deliverable requirements.

**Acceptance Criteria:**

**Given** a NodeDeliverableConfig instance  
**When** I call _format_deliverable_section(deliverable)  
**Then** it returns a formatted string containing:
  - "## Deliverable Requirements" header
  - Type specification
  - Title template (if configured)
  - Required sections list

**Given** a deliverable with template_title  
**When** the section is formatted  
**Then** the title is included with placeholder preserved

**Technical Details:**

```python
@staticmethod
def _format_deliverable_section(deliverable: NodeDeliverableConfig) -> str:
    """Format deliverable requirements section."""
    sections_list = "\n".join(f"- {s}" for s in deliverable.required_sections)
    
    template_info = ""
    if deliverable.template_title:
        template_info = f"\nTitle: {deliverable.template_title}\n"
    
    return f"""## Deliverable Requirements
Type: {deliverable.type}{template_info}
Required sections:
{sections_list}
"""
```

---

### Story 22.5: 重构 _format_system_prompt()

As a developer,  
I want to refactor the system prompt building method,  
So that it assembles all sections in the correct order.

**Acceptance Criteria:**

**Given** all section formatting methods implemented  
**When** I call _format_system_prompt()  
**Then** it returns a complete prompt with sections in order:
  1. Persona Section
  2. Task Assignment
  3. Deliverable Requirements
  4. Execution Instructions

**Given** the complete system prompt  
**When** I examine its structure  
**Then** all placeholders in template_title are preserved for runtime substitution

**Technical Details:**

```python
def _format_system_prompt(self) -> str:
    """Build complete system prompt with BMM persona and task context.
    
    Structure:
    1. Persona Section (BMM role context)
    2. Task Assignment (from node.yaml.task)
    3. Deliverable Requirements (from node.yaml.deliverable)
    4. Execution Instructions
    """
    sections = [
        self._format_persona_section(self.persona),
        self._format_task_section(self.task_config),
        self._format_deliverable_section(self.deliverable_config),
        self._format_execution_instructions(),
    ]
    return "\n\n".join(sections)

@staticmethod
def _format_execution_instructions() -> str:
    """Format execution instructions."""
    return """## Execution Instructions
1. Use the 'create_deliverable' tool to save your deliverable
2. Include all required sections
3. Generate at least 3 clarifying questions
4. Document your reasoning in 'private_reasoning'
"""
```

---

### Story 22.6: 创建 analyst Persona 配置

As a developer,  
I want to create the BMM-aligned persona.json for the analyst node,  
So that Mary (Analyst) has complete role context.

**Acceptance Criteria:**

**Given** the analyst persona requirements from BMM  
**When** I create nodes/analyst/persona.json  
**Then** it contains:
  - name: "Mary"
  - role: "Strategic Business Analyst + Requirements Expert"
  - identity: Rich description of analyst expertise
  - communication_style: Treasure hunter excitement style
  - expertise: Array including Porter's Five Forces, SWOT analysis, etc.
  - principles: Array of guiding principles
  - output_format: {type: "product-brief", format: "markdown"}

**Technical Details:**

```json
{
  "name": "Mary",
  "role": "Strategic Business Analyst + Requirements Expert",
  "identity": "Senior analyst with deep expertise in market research, competitive analysis, and requirements elicitation. Specializes in translating vague needs into actionable specs.",
  "communication_style": "Speaks with the excitement of a treasure hunter - thrilled by every clue, energized when patterns emerge. Structures insights with precision while making analysis feel like discovery.",
  "expertise": [
    "Market research and competitive analysis",
    "Requirements elicitation and specification",
    "Porter's Five Forces and SWOT analysis",
    "Root cause analysis and competitive intelligence",
    "Stakeholder interview facilitation",
    "Business domain knowledge synthesis"
  ],
  "principles": [
    "Every business challenge has root causes waiting to be discovered",
    "Ground findings in verifiable evidence",
    "Articulate requirements with absolute precision",
    "Ensure all stakeholder voices heard"
  ],
  "output_format": {
    "type": "product-brief",
    "format": "markdown"
  }
}
```

---

### Story 22.7: 创建 pm Persona 配置

As a developer,  
I want to create the BMM-aligned persona.json for the pm node,  
So that John (Product Manager) has complete role context.

**Acceptance Criteria:**

**Given** the pm persona requirements from BMM  
**When** I create nodes/pm/persona.json  
**Then** it contains:
  - name: "John"
  - role: "Product Manager specializing in collaborative PRD creation..."
  - identity: PM veteran description
  - communication_style: Detective asking WHY relentlessly
  - expertise: Array including JTBD, opportunity scoring, etc.
  - principles: Array including "PRDs emerge from user interviews"
  - output_format: {type: "prd", format: "markdown"}

**Technical Details:**

```json
{
  "name": "John",
  "role": "Product Manager specializing in collaborative PRD creation through user interviews, requirement discovery, and stakeholder alignment.",
  "identity": "Product management veteran with 8+ years launching B2B and consumer products. Expert in market research, competitive analysis, and user behavior insights.",
  "communication_style": "Asks 'WHY?' relentlessly like a detective on a case. Direct and data-sharp, cuts through fluff to what actually matters.",
  "expertise": [
    "User-centered design and Jobs-to-be-Done framework",
    "Opportunity scoring and prioritization",
    "Market research and competitive analysis",
    "User behavior insights and requirement discovery",
    "PRD creation through structured facilitation",
    "Stakeholder alignment and communication"
  ],
  "principles": [
    "PRDs emerge from user interviews, not template filling",
    "Ship the smallest thing that validates the assumption",
    "Iteration over perfection",
    "Technical feasibility is a constraint, not the driver - user value first"
  ],
  "output_format": {
    "type": "prd",
    "format": "markdown"
  }
}
```

---

### Story 22.8: 创建 ux Persona 配置

As a developer,  
I want to create the BMM-aligned persona.json for the ux node,  
So that Sally (UX Designer) has complete role context.

**Acceptance Criteria:**

**Given** the ux persona requirements from BMM  
**When** I create nodes/ux/persona.json  
**Then** it contains:
  - name: "Sally"
  - role: "User Experience Designer + UI Specialist"
  - identity: Senior UX Designer description
  - communication_style: Painting pictures with words, empathetic
  - expertise: Array including user research, interaction design, etc.
  - principles: Array including "Every decision serves genuine user needs"
  - output_format: {type: "ux-design", format: "markdown"}

**Technical Details:**

```json
{
  "name": "Sally",
  "role": "User Experience Designer + UI Specialist",
  "identity": "Senior UX Designer with 7+ years creating intuitive experiences across web and mobile. Expert in user research, interaction design, AI-assisted tools.",
  "communication_style": "Paints pictures with words, telling user stories that make you FEEL the problem. Empathetic advocate with creative storytelling flair.",
  "expertise": [
    "User research and persona development",
    "Interaction design and wireframing",
    "AI-assisted design tools",
    "Design systems and component libraries",
    "Responsive design and accessibility (WCAG)",
    "Emotional design and user journey mapping"
  ],
  "principles": [
    "Every decision serves genuine user needs",
    "Start simple, evolve through feedback",
    "Balance empathy with edge case attention",
    "AI tools accelerate human-centered design",
    "Data-informed but always creative"
  ],
  "output_format": {
    "type": "ux-design",
    "format": "markdown"
  }
}
```

---

### Story 22.9: 创建 architect Persona 配置

As a developer,  
I want to create the BMM-aligned persona.json for the architect node,  
So that Winston (System Architect) has complete role context.

**Acceptance Criteria:**

**Given** the architect persona requirements from BMM  
**When** I create nodes/architect/persona.json  
**Then** it contains:
  - name: "Winston"
  - role: "System Architect + Technical Design Leader"
  - identity: Senior architect description
  - communication_style: Calm, pragmatic tones
  - expertise: Array including distributed systems, cloud patterns, etc.
  - principles: Array including "User journeys drive technical decisions"
  - output_format: {type: "architecture", format: "markdown"}

**Technical Details:**

```json
{
  "name": "Winston",
  "role": "System Architect + Technical Design Leader",
  "identity": "Senior architect with expertise in distributed systems, cloud infrastructure, and API design. Specializes in scalable patterns and technology selection.",
  "communication_style": "Speaks in calm, pragmatic tones, balancing 'what could be' with 'what should be.'",
  "expertise": [
    "Distributed systems and cloud patterns",
    "API design and scalability trade-offs",
    "Technology selection and evaluation",
    "Lean architecture methodologies",
    "Developer productivity optimization",
    "Security architecture"
  ],
  "principles": [
    "User journeys drive technical decisions",
    "Embrace boring technology for stability",
    "Design simple solutions that scale when needed",
    "Developer productivity is architecture",
    "Connect every decision to business value and user impact"
  ],
  "output_format": {
    "type": "architecture",
    "format": "markdown"
  }
}
```

---

### Story 22.10: 创建 po Persona 配置

As a developer,  
I want to create the BMM-aligned persona.json for the po node,  
So that the Product Owner has complete role context.

**Acceptance Criteria:**

**Given** the po persona requirements from BMM  
**When** I create nodes/po/persona.json  
**Then** it contains:
  - name: "PO"
  - role: "Product Owner - Epics & Stories Specialist"
  - identity: Product management veteran description
  - communication_style: Detective asking WHY relentlessly
  - expertise: Array including requirements decomposition, story mapping, etc.
  - principles: Array including "Ship the smallest thing that validates"
  - output_format: {type: "epics-stories", format: "markdown"}

**Technical Details:**

```json
{
  "name": "PO",
  "role": "Product Owner - Epics & Stories Specialist. Specializes in collaborative requirement decomposition through PRD analysis, architecture context, and stakeholder alignment.",
  "identity": "Product management veteran with 8+ years launching B2B and consumer products. Expert in requirements decomposition, technical implementation context, and acceptance criteria writing.",
  "communication_style": "Asks 'WHY?' relentlessly like a detective on a case. Direct and data-sharp, cuts through fluff to what actually matters.",
  "expertise": [
    "Requirements decomposition and story mapping",
    "Epic design and user story creation",
    "Acceptance criteria writing (Given/When/Then)",
    "Prioritization frameworks (MoSCoW, RICE, Kano)",
    "PRD to implementation-ready story conversion",
    "Technical feasibility assessment"
  ],
  "principles": [
    "PRDs emerge from user interviews, not template filling",
    "Ship the smallest thing that validates the assumption",
    "Iteration over perfection",
    "Technical feasibility is a constraint, not the driver - user value first"
  ],
  "output_format": {
    "type": "epics-stories",
    "format": "markdown"
  }
}
```

---

### Story 22.11: 编写验证测试

As a developer,  
I want to write tests for the Persona and System Prompt refactoring,  
So that we can verify correctness and backward compatibility.

**Acceptance Criteria:**

**Given** the new Persona structure  
**When** I run pytest on tests/agents/test_persona_communication_style.py  
**Then** all tests pass verifying the new field works correctly

**Given** the System Prompt formatting  
**When** I run tests on tests/agents/test_system_prompt_sections.py  
**Then** all sections are formatted correctly  
**And** the complete prompt contains all required sections in order

**Given** the backward compatibility requirement  
**When** I test with old persona.json files  
**Then** they load successfully with communication_style defaulting to empty string

**Technical Details:**

```python
# tests/agents/test_persona_communication_style.py
class TestPersonaCommunicationStyle:
    def test_persona_with_communication_style(self):
        persona = Persona(
            name="Mary",
            role="Strategic Business Analyst",
            identity="Senior analyst...",
            communication_style="Speaks with excitement...",
            expertise=["Market research"],
            principles=["Evidence-based"]
        )
        assert persona.communication_style == "Speaks with excitement..."

    def test_persona_backward_compatibility(self):
        old_data = {
            "name": "Analyst",
            "role": "Data Analyst",
            "identity": "Expert data analyst",
            "expertise": ["SQL"],
            "principles": ["Data quality first"]
        }
        persona = Persona(**old_data)
        assert persona.communication_style == ""  # 默认值

# tests/agents/test_system_prompt_sections.py
class TestSystemPromptSections:
    def test_persona_section_formatting(self, mary_persona):
        section = IndependentAgent._format_persona_section(mary_persona)
        assert "# Persona: Mary" in section
        assert "## Communication Style" in section
        assert "## Expertise" in section

    def test_task_section_formatting(self, analyst_task):
        section = IndependentAgent._format_task_section(analyst_task)
        assert "## Task Assignment" in section
        assert "### Role Context" in section

    def test_deliverable_section_formatting(self, analyst_deliverable):
        section = IndependentAgent._format_deliverable_section(analyst_deliverable)
        assert "## Deliverable Requirements" in section
        assert "Required sections:" in section
```

---

## 3. 测试验证清单

| 测试文件 | 测试内容 | 状态 |
|----------|----------|------|
| `tests/agents/test_persona_communication_style.py` | communication_style 字段测试 | ⬜ |
| `tests/agents/test_persona_loader.py` | PersonaLoader 加载测试 | ⬜ |
| `tests/agents/test_system_prompt_sections.py` | Prompt Section 构建测试 | ⬜ |
| `tests/agents/test_complete_system_prompt.py` | 完整 Prompt 测试 | ⬜ |
| `tests/nodes/test_five_node_personas.py` | 五节点 Persona 配置测试 | ⬜ |

---

## 4. 验证命令

```bash
# 运行 Persona 相关测试
pytest tests/agents/test_persona_communication_style.py -v
pytest tests/agents/test_persona_loader.py -v
pytest tests/agents/test_system_prompt_sections.py -v
pytest tests/agents/test_complete_system_prompt.py -v
pytest tests/nodes/test_five_node_personas.py -v

# 类型检查
basedpyright autoBMAD/docuswarm/agents/persona.py
basedpyright autoBMAD/docuswarm/agents/independent.py

# 代码风格检查
ruff check autoBMAD/docuswarm/agents/

# 验证配置文件格式
python -c "import json; json.load(open('nodes/analyst/persona.json'))"
```

---

## 5. 风险与缓解

| 风险 | 严重度 | 缓解策略 |
|------|--------|----------|
| Persona 加载失败 | 高 | 保持向后兼容，新字段有默认值 |
| BMM 内容不完整 | 中 | 对照 _bmad/bmm/ 源文件检查 |
| Prompt 格式错误 | 中 | 使用测试验证格式正确性 |

---

## 6. 相关文档

- [TDD-BMM-02: Persona 角色上下文与 System Prompt 重构](../solution/TDD-BMM-02-Persona-SystemPrompt-Refactor.md)
- [EPIC-21: NodeLoader 配置加载系统重构](./EPIC-21-NodeLoader-Config-Refactor.md)
- [EPIC-23: 废弃代码移除与功能精简](./EPIC-23-Deprecated-Code-Removal.md)

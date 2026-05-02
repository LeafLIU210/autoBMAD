# TDD-BMM-02: Persona 角色上下文与 System Prompt 重构

## 文档信息

| 属性 | 值 |
|------|-----|
| **方案编号** | TDD-BMM-02 |
| **关联研究** | Part 2 (节点角色与任务映射), Part 3 (双代理流程) |
| **优先级** | P0 - Critical |
| **状态** | 待实施 |

---

## 1. 目标

重构 Persona 系统和 IndependentAgent 的 System Prompt 构建，实现：
1. 新增 `communication_style` 字段到 Persona 数据类
2. 重写5个节点的 persona.json 嵌入 BMM 角色上下文
3. 重构 `_format_system_prompt()` 使用 BMM 角色上下文 + task 说明
4. 将交付物模板结构传递到 prompt

---

## 2. 当前状态分析

### 2.1 现有 Persona 结构

```python
@dataclass
class Persona:
    name: str                    # "Analyst" (通用)
    role: str                    # "Data Analyst & BI Specialist"
    identity: str                # 通用描述
    expertise: list[str]         # 通用技能
    principles: list[str]        # 通用原则
    tools: list[str]             # 将被移除
    output_format: dict          # 包含 sections (与 node.yaml 重复)
```

### 2.2 目标 Persona 结构 (BMM 对齐)

```python
@dataclass
class Persona:
    name: str                    # "Mary" (人格化)
    role: str                    # "Strategic Business Analyst + Requirements Expert"
    identity: str                # BMM 丰富身份描述
    communication_style: str     # 新增: "Speaks with excitement of treasure hunter..."
    expertise: list[str]         # BMM 专业技能 (Porter五力, SWOT等)
    principles: list[str]        # BMM 方法论原则
    output_format: dict          # 简化，移除 sections
```

### 2.3 System Prompt 重构对比

**重构前**:
```
# Persona Section (通用)
You are Analyst, a Data Analyst & Business Intelligence Specialist.
Expertise: Statistical analysis, Data visualization...

# Instructions (通用)
You are an Independent Agent that creates deliverables...
```

**重构后**:
```
# Persona Section (BMM 角色上下文)
# Persona: Mary
**Role**: Strategic Business Analyst + Requirements Expert

## Identity
Senior analyst with deep expertise in market research...

## Communication Style
Speaks with the excitement of a treasure hunter...

## Expertise
- Market research and competitive analysis
- Porter's Five Forces and SWOT analysis
...

## Guiding Principles
- Every business challenge has root causes waiting to be discovered
...

# Task Assignment (来自 node.yaml.task)
You are executing the 'create-product-brief' task.
Create comprehensive product briefs through collaborative...

### Role Context
You are a product-focused Business Analyst collaborating...

# Deliverable Requirements (来自 node.yaml.deliverable)
Type: product-brief
Title: Product Brief: {project_name}

Required sections:
- executive_summary
- core_vision
- problem_statement
...
```

---

## 3. 测试先行的重构计划

### Phase 1: Persona 数据类扩展测试

#### Test 1.1: Communication Style 字段测试

```python
# tests/agents/test_persona_communication_style.py
"""Tests for Persona communication_style field."""

import pytest
from autoBMAD.docuswarm.agents.persona import Persona


class TestPersonaCommunicationStyle:
    """Test communication_style field in Persona dataclass."""

    def test_persona_with_communication_style(self):
        """Test creating persona with communication_style."""
        persona = Persona(
            name="Mary",
            role="Strategic Business Analyst",
            identity="Senior analyst with deep expertise...",
            communication_style="Speaks with the excitement of a treasure hunter",
            expertise=["Market research", "SWOT analysis"],
            principles=["Ground findings in evidence"]
        )
        assert persona.communication_style == "Speaks with the excitement of a treasure hunter"

    def test_persona_backward_compatibility(self):
        """Test old persona.json without communication_style still works."""
        # 模拟从旧格式JSON加载
        old_data = {
            "name": "Analyst",
            "role": "Data Analyst",
            "identity": "Expert data analyst",
            "expertise": ["SQL", "Python"],
            "principles": ["Data quality first"]
            # 注意: 没有 communication_style
        }
        persona = Persona(**old_data)
        assert persona.communication_style == ""  # 默认值
        assert persona.name == "Analyst"

    def test_persona_from_bmm_format(self):
        """Test loading persona from BMM-aligned JSON."""
        bmm_persona = {
            "name": "Mary",
            "role": "Strategic Business Analyst + Requirements Expert",
            "identity": "Senior analyst with deep expertise in market research...",
            "communication_style": "Speaks with the excitement of a treasure hunter - thrilled by every clue...",
            "expertise": [
                "Market research and competitive analysis",
                "Porter's Five Forces and SWOT analysis",
                "Requirements elicitation and specification"
            ],
            "principles": [
                "Every business challenge has root causes waiting to be discovered",
                "Ground findings in verifiable evidence"
            ],
            "output_format": {"type": "product-brief", "format": "markdown"}
        }
        persona = Persona(**bmm_persona)
        assert persona.name == "Mary"
        assert "Porter's Five Forces" in persona.expertise
```

#### Test 1.2: PersonaLoader 加载测试

```python
# tests/agents/test_persona_loader.py
"""Tests for PersonaLoader with BMM personas."""

import pytest
import json
from pathlib import Path
from autoBMAD.docuswarm.agents.persona import PersonaLoader


class TestPersonaLoader:
    """Test loading BMM-aligned persona.json files."""

    @pytest.fixture
    def bmm_persona_file(self, tmp_path):
        """Create BMM-aligned persona.json file."""
        persona_data = {
            "name": "Mary",
            "role": "Strategic Business Analyst + Requirements Expert",
            "identity": "Senior analyst with deep expertise...",
            "communication_style": "Speaks with the excitement of a treasure hunter",
            "expertise": ["Market research", "SWOT analysis"],
            "principles": ["Evidence-based findings"],
            "output_format": {"type": "product-brief"}
        }
        persona_path = tmp_path / "persona.json"
        persona_path.write_text(json.dumps(persona_data))
        return persona_path

    def test_load_bmm_persona(self, bmm_persona_file):
        """Test loading BMM persona with all fields."""
        persona = PersonaLoader.load(bmm_persona_file.parent, "analyst")
        
        assert persona.name == "Mary"
        assert persona.communication_style == "Speaks with the excitement of a treasure hunter"
        assert "Strategic Business Analyst" in persona.role
```

### Phase 2: System Prompt 构建测试

#### Test 2.1: Prompt Section 构建测试

```python
# tests/agents/test_system_prompt_sections.py
"""Tests for system prompt section building."""

import pytest
from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.agents.persona import Persona
from autoBMAD.docuswarm.nodes.loader import NodeTaskConfig, NodeDeliverableConfig


class TestSystemPromptSections:
    """Test individual prompt section building."""

    @pytest.fixture
    def mary_persona(self):
        """Create Mary (Analyst) persona."""
        return Persona(
            name="Mary",
            role="Strategic Business Analyst + Requirements Expert",
            identity="Senior analyst with deep expertise in market research...",
            communication_style="Speaks with the excitement of a treasure hunter",
            expertise=["Market research", "SWOT analysis"],
            principles=["Evidence-based findings"]
        )

    @pytest.fixture
    def analyst_task(self):
        """Create analyst task config."""
        return NodeTaskConfig(
            name="create-product-brief",
            description="Create comprehensive product briefs",
            role_supplement="You are a product-focused Business Analyst"
        )

    @pytest.fixture
    def analyst_deliverable(self):
        """Create analyst deliverable config."""
        return NodeDeliverableConfig(
            type="product-brief",
            template_title="Product Brief: {project_name}",
            required_sections=["executive_summary", "core_vision"],
            output_filename="product-brief-{project_name}.md"
        )

    def test_persona_section_formatting(self, mary_persona):
        """Test persona section formatting."""
        section = IndependentAgent._format_persona_section(mary_persona)
        
        assert "# Persona: Mary" in section
        assert "**Role**: Strategic Business Analyst + Requirements Expert" in section
        assert "## Communication Style" in section
        assert "Speaks with the excitement of a treasure hunter" in section
        assert "## Expertise" in section
        assert "- Market research" in section
        assert "## Guiding Principles" in section

    def test_task_section_formatting(self, analyst_task):
        """Test task section formatting."""
        section = IndependentAgent._format_task_section(analyst_task)
        
        assert "## Task Assignment" in section
        assert "create-product-brief" in section
        assert "Create comprehensive product briefs" in section
        assert "### Role Context" in section
        assert "product-focused Business Analyst" in section

    def test_deliverable_section_formatting(self, analyst_deliverable):
        """Test deliverable section formatting."""
        section = IndependentAgent._format_deliverable_section(analyst_deliverable)
        
        assert "## Deliverable Requirements" in section
        assert "Type: product-brief" in section
        assert "Title: Product Brief: {project_name}" in section
        assert "Required sections:" in section
        assert "- executive_summary" in section
        assert "- core_vision" in section
```

#### Test 2.2: 完整 System Prompt 测试

```python
# tests/agents/test_complete_system_prompt.py
"""Tests for complete system prompt assembly."""

import pytest
from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestCompleteSystemPrompt:
    """Test complete system prompt assembly."""

    def test_full_prompt_contains_all_sections(self, mary_persona, analyst_task, analyst_deliverable):
        """Test that full prompt contains all required sections."""
        # 使用模拟的agent实例
        agent = IndependentAgent.__new__(IndependentAgent)
        agent.persona = mary_persona
        agent.task_config = analyst_task
        agent.deliverable_config = analyst_deliverable
        
        prompt = agent._format_system_prompt()
        
        # 验证所有部分都存在
        assert "# Persona: Mary" in prompt
        assert "## Communication Style" in prompt
        assert "## Task Assignment" in prompt
        assert "create-product-brief" in prompt
        assert "## Deliverable Requirements" in prompt
        assert "Required sections:" in prompt
        assert "## Execution Instructions" in prompt

    def test_prompt_order(self, mary_persona, analyst_task, analyst_deliverable):
        """Test that prompt sections are in correct order."""
        agent = IndependentAgent.__new__(IndependentAgent)
        agent.persona = mary_persona
        agent.task_config = analyst_task
        agent.deliverable_config = analyst_deliverable
        
        prompt = agent._format_system_prompt()
        
        # 验证顺序: Persona -> Task -> Deliverable -> Instructions
        persona_pos = prompt.find("# Persona:")
        task_pos = prompt.find("## Task Assignment")
        deliverable_pos = prompt.find("## Deliverable Requirements")
        instructions_pos = prompt.find("## Execution Instructions")
        
        assert persona_pos < task_pos < deliverable_pos < instructions_pos
```

### Phase 3: 五节点 Persona 配置测试

#### Test 3.1: 五节点 BMM Persona 验证

```python
# tests/nodes/test_five_node_personas.py
"""Tests for all five node personas with BMM alignment."""

import pytest
import json
from pathlib import Path


class TestFiveNodePersonas:
    """Test that all five nodes have BMM-aligned personas."""

    EXPECTED_PERSONAS = {
        "analyst": {
            "name": "Mary",
            "role_contains": ["Strategic Business Analyst", "Requirements Expert"],
            "expertise_contains": ["Porter", "SWOT", "market research"],
            "communication_style_required": True
        },
        "pm": {
            "name": "John",
            "role_contains": ["Product Manager"],
            "expertise_contains": ["Jobs-to-be-Done", "PRD"],
            "communication_style_required": True
        },
        "ux": {
            "name": "Sally",
            "role_contains": ["User Experience Designer"],
            "expertise_contains": ["user research", "interaction design"],
            "communication_style_required": True
        },
        "architect": {
            "name": "Winston",
            "role_contains": ["System Architect", "Technical Design"],
            "expertise_contains": ["distributed systems", "cloud"],
            "communication_style_required": True
        },
        "po": {
            "name": "PO",  # 名称保持PO，但角色上下文同PM
            "role_contains": ["Product Owner"],
            "expertise_contains": ["requirements decomposition", "story"],
            "communication_style_required": True
        }
    }

    @pytest.mark.parametrize("node_id,expected", EXPECTED_PERSONAS.items())
    def test_persona_structure(self, node_id, expected, nodes_dir):
        """Test each node's persona.json structure."""
        persona_path = nodes_dir / node_id / "persona.json"
        
        if not persona_path.exists():
            pytest.skip(f"Persona file not found for {node_id}")
        
        with open(persona_path) as f:
            persona = json.load(f)
        
        # 验证基本结构
        assert persona.get("name") == expected["name"]
        
        # 验证 role 包含预期内容
        role = persona.get("role", "")
        for keyword in expected["role_contains"]:
            assert keyword in role, f"Role should contain '{keyword}' for {node_id}"
        
        # 验证 communication_style 存在
        if expected["communication_style_required"]:
            assert "communication_style" in persona
            assert len(persona["communication_style"]) > 20  # 应该有内容
        
        # 验证 expertise 包含预期内容
        expertise = persona.get("expertise", [])
        for keyword in expected["expertise_contains"]:
            found = any(keyword.lower() in e.lower() for e in expertise)
            assert found, f"Expertise should contain '{keyword}' for {node_id}"
```

### Phase 4: 实现

#### Implementation 4.1: 扩展 Persona 数据类

```python
# autoBMAD/docuswarm/agents/persona.py

@dataclass
class Persona:
    """BMM-aligned agent persona.
    
    All content is pre-processed from _bmad/bmm/agents/*.md <persona> blocks
    and embedded in persona.json. Runtime zero external dependency.
    
    Attributes:
        name: Persona name (e.g., "Mary", "John")
        role: Professional role description
        identity: Rich identity narrative
        communication_style: Unique communication style (NEW)
        expertise: List of expertise areas
        principles: List of guiding principles
        output_format: Output format preferences
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

#### Implementation 4.2: 重构 System Prompt 构建

```python
# autoBMAD/docuswarm/agents/independent.py

class IndependentAgent(BaseAgent):
    """Independent Agent with BMM-aligned system prompt."""

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

## 4. 五节点 Persona 配置文件

### analyst/persona.json

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

### pm/persona.json

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

### ux/persona.json

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

### architect/persona.json

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

### po/persona.json

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

## 5. 实施清单

| 步骤 | 任务 | 测试文件 | 实现文件 | 状态 |
|------|------|----------|----------|------|
| 1 | communication_style 字段测试 | `test_persona_communication_style.py` | `persona.py` | ⬜ |
| 2 | PersonaLoader 加载测试 | `test_persona_loader.py` | `persona.py` | ⬜ |
| 3 | Prompt Section 构建测试 | `test_system_prompt_sections.py` | `independent.py` | ⬜ |
| 4 | 完整 Prompt 测试 | `test_complete_system_prompt.py` | `independent.py` | ⬜ |
| 5 | 五节点 Persona 配置测试 | `test_five_node_personas.py` | 配置文件 | ⬜ |
| 6 | 扩展 Persona 数据类 | - | `persona.py` | ⬜ |
| 7 | 重构 System Prompt 构建 | - | `independent.py` | ⬜ |
| 8 | 创建五节点 persona.json | - | `nodes/*/persona.json` | ⬜ |

---

## 6. 验证命令

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

# 验证配置文件格式
python -c "import json; json.load(open('autoBMAD/nodes/analyst/persona.json'))"
```

---

**文档结束**

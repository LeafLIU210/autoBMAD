# BMM NodeExecutor 重构研究报告 Part 1: 配置加载与模板交付物系统

**文档编号**: BMM-Research-01
**日期**: 2026-03-02
**范围**: NodeExecutor配置加载重构 + 模板交付物文档创建系统
**修订**: v2 - 确保 `autoBMAD/docuswarm` 无 `_bmad` 外部依赖

---

## 0. 核心约束

> **`autoBMAD/docuswarm` 运行时绝不引用 `_bmad` 或任何外部文件夹。**

- `_bmad/bmm/` 是BMM方法论源文件，供人机交互式IDE代理使用
- `autoBMAD/` 是自动化管道，必须**自包含**
- BMM内容通过**预处理提取**嵌入到 `autoBMAD/nodes/` 配置文件中
- 运行时 `NodeLoader` 只从 `autoBMAD/nodes/` 加载

---

## 1. 问题陈述

### 1.1 当前配置加载机制的缺陷

当前 `NodeLoader`（[loader.py](autoBMAD/nodes/loader.py)）加载三类配置文件：

| 文件 | 用途 | 问题 |
|------|------|------|
| `nodes/{id}/node.yaml` | 节点主配置 | 角色/交付物与BMM不一致 |
| `nodes/{id}/persona.json` | 独立Agent人格 | 通用角色，缺少BMM的communication_style |
| `nodes/{id}/evaluator.yaml` | 评估Agent配置 | 结构合理，评估标准描述需微调 |

**核心缺陷（非外部依赖问题，而是内容对齐问题）**:

1. `persona.json` 内容是**通用IT角色**（Data Analyst、Project Manager等），而非BMM定义的**专业角色上下文**（Mary/John/Sally/Winston，带communication_style和principles）
2. `node.yaml` 的 `deliverable_type` / `required_sections` 与BMM workflow交付物不对齐
3. `node.yaml` 包含无用字段（`questions`、`dependencies`）
4. 没有嵌入BMM workflow的任务说明和模板结构
5. `autoBMAD/docuswarm/templates/*_templates.yaml` 中的 `standards.style_guide` 引用了 `_bmad/_memory/` 路径（**已有的外部依赖违规**）

### 1.2 已有的 `_bmad` 外部依赖违规

`autoBMAD/docuswarm/templates/` 中5个模板配置文件均包含：

```yaml
standards:
  style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
```

**这是当前唯一的运行时 `_bmad` 引用**，必须移除。

### 1.3 当前配置加载链路

```
create_pipeline_graph()
  → _create_integrated_node_executor("analyst", session_manager)
    → create_node_executor("analyst", session_manager)  # node_execution/executor.py
      → NodeLoader.load("analyst")                       # 仅加载 autoBMAD/nodes/analyst/
        → node.yaml (通用描述 + 无用questions/dependencies)
        → persona.json (通用角色，缺少communication_style)
        → evaluator.yaml (评估标准，描述需微调)
      → create_dual_agent_node(config, sm, "analyst", project_root)
        → IndependentAgent → PersonaLoader.load() → 通用persona
        → EvaluatorAgent → _load_criteria() → evaluator.yaml
```

---

## 2. BMM源文件分析（用于预处理提取）

以下分析 `_bmad/bmm/` 中需提取到 `autoBMAD/nodes/` 的内容：

### 2.1 BMM Agent 定义 (`_bmad/bmm/agents/*.md`)

每个agent.md文件包含三部分：
- **activation/menu/handlers**: 交互式IDE使用 → **不提取**（自动化不需要）
- **`<persona>`块**: role, identity, communication_style, principles → **提取到persona.json**
- **agent元数据**: name, title, icon, capabilities → **提取到persona.json/node.yaml**

**提取映射表**:

| 字段 | BMM位置 | 提取到 | 示例 |
|------|---------|--------|------|
| name | `<agent name="Mary">` | `persona.json.name` | "Mary" |
| title | `<agent title="Business Analyst">` | `persona.json.role` 的补充 | "Business Analyst" |
| capabilities | `<agent capabilities="...">` | `persona.json.expertise` | "market research, competitive analysis..." |
| role | `<persona><role>` | `persona.json.role` | "Strategic Business Analyst + Requirements Expert" |
| identity | `<persona><identity>` | `persona.json.identity` | "Senior analyst with deep expertise..." |
| communication_style | `<persona><communication_style>` | `persona.json.communication_style` | "Speaks with the excitement of a treasure hunter..." |
| principles | `<persona><principles>` | `persona.json.principles` | "Channel expert business analysis frameworks..." |

### 2.2 BMM Workflow 定义 (`_bmad/bmm/workflows/*/workflow.md`)

每个workflow.md包含：
- **name/description**: 任务说明 → **提取到 `node.yaml.task`**
- **WORKFLOW ARCHITECTURE**: 步骤文件架构规则 → **提取为精简版task_instructions**
- **INITIALIZATION**: 加载 `_bmad/bmm/config.yaml` → **不提取**（自动化不需要从 `_bmad` 加载）
- **step文件路径**: 指向 `_bmad/` → **不提取**（自动化不使用步骤文件架构）

### 2.3 BMM 模板文件 (`_bmad/bmm/workflows/*/templates/*.md`)

每个模板包含：
- **frontmatter**: `stepsCompleted`, `inputDocuments`, `workflowType` → **按需提取**
- **标题/占位符**: `# Product Brief: {{project_name}}` → **提取到 `node.yaml.deliverable.template`**
- **section结构**: 从模板中提取sections列表 → **提取到 `node.yaml.deliverable.required_sections`**

### 2.4 BMM Config (`_bmad/bmm/config.yaml`)

```yaml
project_name: ClawTeams
user_name: 你
communication_language: Chinese
document_output_language: English
```

**处理方式**: 这些是**用户项目级配置**，不属于 `autoBMAD/nodes/` 的静态配置。应通过以下方式传入：
- `PipelineState.subject_context` 中携带 `project_name`
- `Config`（`.env`/环境变量）中携带 `communication_language`
- 或在 `autoBMAD/` 自身的配置文件中定义

---

## 3. 重构方案（自包含设计）

### 3.1 设计原则

```
┌───────────────────────────────────────────────────┐
│  _bmad/bmm/  (BMM源文件)                           │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐   │
│  │agents/*.md │  │workflows/│  │templates/*.md│   │
│  └─────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│        │              │               │            │
│  ══════╪══════════════╪═══════════════╪══ 预处理边界 │
│        ↓              ↓               ↓            │
│  autoBMAD/nodes/  (自包含配置)                      │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐   │
│  │persona.json│  │node.yaml │  │evaluator.yaml│   │
│  │(BMM角色)   │  │(BMM任务) │  │(评估标准)     │   │
│  └───────────┘  └──────────┘  └──────────────┘   │
└───────────────────────────────────────────────────┘
```

- **预处理**: 人工（或脚本）将BMM内容提取后写入 `autoBMAD/nodes/` 配置文件
- **运行时**: `NodeLoader` 只读 `autoBMAD/nodes/{id}/` 目录，零外部依赖
- **BMM同步**: 当 `_bmad/bmm/` 更新时，需手动同步到 `autoBMAD/nodes/`

### 3.2 node.yaml 重构

以analyst为例，**重构前** vs **重构后**:

**重构前**:
```yaml
node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist
sequence: 1
deliverable_type: analyst-report
deliverable:
  required_sections: [executive_summary, data_sources, ...]
agent:
  type: independent
  model: sonnet
  temperature: 0.7
questions: [...]        # 无用
dependencies: []        # 无用
```

**重构后**:
```yaml
node_id: analyst
name: Analyst
sequence: 1
agent:
  type: independent
  model: sonnet
  temperature: 0.7

# BMM任务对齐（预处理从 _bmad/bmm/workflows 提取）
task:
  name: create-product-brief
  description: >
    Create comprehensive product briefs through collaborative step-by-step
    discovery as creative Business Analyst working with the user as peers.
  role_supplement: >
    You are a product-focused Business Analyst. You bring structured thinking
    and facilitation skills. Work together with the user as equals.

# 交付物对齐（预处理从 _bmad/bmm/workflows/templates 提取）
deliverable:
  type: product-brief
  template_title: "Product Brief: {project_name}"
  required_sections:
    - executive_summary
    - core_vision
    - problem_statement
    - proposed_solution
    - key_differentiators
    - target_users
    - success_metrics
    - mvp_scope
  output_filename: "product-brief-{project_name}.md"
```

### 3.3 persona.json 重构

以analyst为例，**重构前** vs **重构后**:

**重构前**（通用角色）:
```json
{
  "name": "Analyst",
  "role": "Data Analyst & Business Intelligence Specialist",
  "identity": "You are an expert data analyst who transforms raw data...",
  "expertise": ["Statistical analysis...", "Data visualization...", ...],
  "principles": ["Always verify data quality...", ...],
  "tools": [...],
  "output_format": {...}
}
```

**重构后**（BMM角色上下文，预处理从 `_bmad/bmm/agents/analyst.md` 的 `<persona>` 块提取）:
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
    "Root cause analysis",
    "Competitive intelligence methodologies",
    "Stakeholder interview facilitation"
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

**关键变化**:
- `tools` 字段移除（IndependentAgent使用统一的 `create_deliverable` tool）
- `output_format.sections` 移除（改由 `node.yaml.deliverable.required_sections` 统一管理，消除DRY）
- 新增 `communication_style`（从BMM `<persona><communication_style>` 提取）

### 3.4 模板交付物创建流程（自包含）

NodeExecutor在完成配置加载后创建初始交付物文档：

```
1. NodeLoader.load("analyst") → 加载 node.yaml (含 deliverable.template_title, required_sections)
2. 从 PipelineState.subject_context 获取 {project_name}
3. 替换模板变量:
   - {project_name} → subject_context中的项目名
   - {date} → 当前日期
4. 构建初始Markdown文档结构（基于 required_sections）
5. 将模板结构传递给 IndependentAgent 的 system prompt
6. IndependentAgent 基于模板结构生成交付物内容
```

**注意**: 模板结构信息完全来自 `node.yaml`，不从 `_bmad` 读取。

### 3.5 配置加载重构后的执行链路

```
create_pipeline_graph()
  → _create_integrated_node_executor("analyst", session_manager)
    → create_node_executor("analyst", session_manager)
      → NodeLoader.load("analyst")
        → 加载 autoBMAD/nodes/analyst/node.yaml (含BMM任务+交付物定义)
        → 加载 autoBMAD/nodes/analyst/persona.json (含BMM角色上下文)
        → 加载 autoBMAD/nodes/analyst/evaluator.yaml (评估标准)
        → 不访问任何 _bmad/ 路径
      → 构建初始交付物文档结构
      → create_dual_agent_node(config, sm, "analyst", project_root)
        → IndependentAgent: BMM persona + task说明 + 模板结构
        → EvaluatorAgent: evaluator.yaml 评估标准
```

---

## 4. NodeConfig 数据结构重构

### 4.1 移除字段

```python
# 删除
NodeQuestionConfig     # 预定义问题在自动化中无用
NodeQuestionsConfig    # 同上
NodeDependenciesConfig # 由graph.py边定义管理
```

### 4.2 修改字段

```python
@dataclass
class NodeDeliverableConfig:
    type: str                        # "product-brief" (替代 "analyst-report")
    required_sections: list[str]     # 保留，内容对齐BMM模板
    template_title: str = ""         # 新增: 模板标题 "Product Brief: {project_name}"
    output_filename: str = ""        # 新增: 输出文件名模式

@dataclass
class NodeTaskConfig:                # 新增 dataclass
    name: str                        # "create-product-brief"
    description: str                 # 任务描述（从BMM workflow提取）
    role_supplement: str = ""        # 角色补充说明（从BMM workflow的 "Your Role" 提取）

@dataclass
class NodeConfig:
    node_id: str
    name: str
    sequence: int
    deliverable: NodeDeliverableConfig
    agent: NodeAgentConfig
    task: NodeTaskConfig | None = None       # 新增: BMM任务配置
    evaluator: NodeEvaluatorConfig | None = None
    persona: dict[str, Any] | None = None
    # 删除: questions, dependencies
```

---

## 5. 已有外部依赖违规修复

### 5.1 templates/*.yaml 中的 _bmad 引用

**5个文件均需修复**:

| 文件 | 当前值 | 修复方案 |
|------|--------|----------|
| `analyst_templates.yaml:62` | `style_guide: "_bmad/_memory/..."` | 删除此字段或内联标准 |
| `pm_templates.yaml:54` | 同上 | 同上 |
| `ux_templates.yaml:67` | 同上 | 同上 |
| `architect_templates.yaml:59` | 同上 | 同上 |
| `po_templates.yaml:66` | 同上 | 同上 |

**修复方案**: 将文档标准内联到 `autoBMAD/docuswarm/templates/` 的公共配置中，或直接删除（如果运行时不使用此字段）。

### 5.2 templates/*.yaml 内容对齐

当前 `autoBMAD/docuswarm/templates/*_templates.yaml` 的模板定义（market_research、user_personas等）与BMM workflow交付物不一致。重构时需决定：

- **方案A**: 替换内容 → 对齐BMM交付物（product-brief、prd、ux-design、architecture、epics-stories）
- **方案B**: 移除整个templates目录 → 模板信息统一由 `node.yaml.deliverable` 管理

**建议方案B**：遵循KISS原则，`node.yaml` 已包含 `deliverable.required_sections`，templates/*.yaml 属于重复配置。

---

## 6. 移除清单

### 6.1 node.yaml 字段精简

| 字段 | 当前状态 | 建议 | 理由 |
|------|---------|------|------|
| `description` | 通用描述 | **移除** | 角色描述由persona.json.role管理 |
| `questions` | 预定义问题 | **移除** | 自动化不使用 |
| `dependencies` | 依赖列表 | **移除** | 由graph.py边定义管理 |

### 6.2 persona.json 字段精简

| 字段 | 当前状态 | 建议 | 理由 |
|------|---------|------|------|
| `tools` | 工具列表 | **移除** | Agent使用统一tool，不需要per-persona定义 |
| `output_format.sections` | section列表 | **移除** | 与node.yaml.deliverable.required_sections重复(DRY) |

### 6.3 废弃代码清理

| 代码位置 | 函数/类 | 建议 |
|----------|---------|------|
| `pipeline/graph.py` | `_create_default_node_executor()` | **移除** (deprecated) |
| `pipeline/graph.py` | `create_enhanced_node_executor()` | **移除** (调用deprecated) |
| `loader.py` | `NodeQuestionConfig` | **移除** |
| `loader.py` | `NodeQuestionsConfig` | **移除** |
| `loader.py` | `NodeDependenciesConfig` | **移除** |
| `templates/*_templates.yaml` | `standards.style_guide` | **修复** (移除_bmad引用) |

---

## 7. 预处理同步机制

### 7.1 BMM → autoBMAD 数据流

```
_bmad/bmm/agents/analyst.md
    │
    │ 手动提取 <persona> 块
    ↓
autoBMAD/nodes/analyst/persona.json
    (name, role, identity, communication_style, expertise, principles)

_bmad/bmm/workflows/1-analysis/create-product-brief/workflow.md
    │
    │ 手动提取 name, description, "Your Role"
    ↓
autoBMAD/nodes/analyst/node.yaml → task: {name, description, role_supplement}

_bmad/bmm/workflows/1-analysis/create-product-brief/product-brief.template.md
    │
    │ 手动提取 标题、sections
    ↓
autoBMAD/nodes/analyst/node.yaml → deliverable: {type, template_title, required_sections}
```

### 7.2 五节点预处理映射总表

| node_id | BMM Agent源 | BMM Workflow源 | BMM Template源 |
|---------|-------------|----------------|----------------|
| analyst | `agents/analyst.md` → persona.json | `1-analysis/create-product-brief/workflow.md` → node.yaml.task | `product-brief.template.md` → node.yaml.deliverable |
| pm | `agents/pm.md` → persona.json | `2-plan-workflows/create-prd/workflow-create-prd.md` → node.yaml.task | `templates/prd-template.md` → node.yaml.deliverable |
| ux | `agents/ux-designer.md` → persona.json | `2-plan-workflows/create-ux-design/workflow.md` → node.yaml.task | `ux-design-template.md` → node.yaml.deliverable |
| architect | `agents/architect.md` → persona.json | `3-solutioning/create-architecture/workflow.md` → node.yaml.task | `architecture-decision-template.md` → node.yaml.deliverable |
| po | `agents/pm.md` (名称PO) → persona.json | `3-solutioning/create-epics-and-stories/workflow.md` → node.yaml.task | `templates/epics-template.md` → node.yaml.deliverable |

---

## 8. 风险评估

| 风险 | 严重度 | 缓解策略 |
|------|--------|----------|
| BMM源文件更新后 autoBMAD 配置未同步 | 中 | 可编写同步脚本（不属于运行时依赖）或文档化同步流程 |
| persona.json 中 communication_style 提取困难（XML in MD） | 低 | 一次性手动提取，内容稳定 |
| 现有测试依赖 NodeConfig 旧字段结构 | 中 | 渐进式重构，先添加新字段再移除旧字段 |
| templates/*.yaml 中的 _bmad 引用被运行时使用 | 低 | 先确认是否有代码引用此字段，再决定内联或删除 |

---

## 9. 实施优先级

| 步骤 | 内容 | 优先级 |
|------|------|--------|
| P0 | 修复 templates/*.yaml 中的 `_bmad` 引用违规 | 最高 |
| P0 | 移除 node.yaml 中的 questions/dependencies | 最高 |
| P1 | 重写5个 persona.json（提取BMM角色上下文） | 高 |
| P1 | 重构5个 node.yaml（新增 task + deliverable对齐） | 高 |
| P1 | 扩展 NodeConfig/Persona dataclass | 高 |
| P2 | 清理 deprecated 代码 | 中 |
| P2 | 评估 templates/*.yaml 是否整体移除 | 中 |
| P3 | 编写 BMM→autoBMAD 同步脚本（可选） | 低 |


---

## 10. 解决方案文档

本文档的研究结果已转化为测试驱动的实施方案：

| 方案文档 | 内容 | 位置 |
|----------|------|------|
| **TDD-BMM-01** | NodeLoader 配置加载系统重构 | [`docs/solution/TDD-BMM-01-NodeLoader-Config-Refactor.md`](../solution/TDD-BMM-01-NodeLoader-Config-Refactor.md) |
| **TDD-BMM-02** | Persona 角色上下文与 System Prompt 重构 | [`docs/solution/TDD-BMM-02-Persona-SystemPrompt-Refactor.md`](../solution/TDD-BMM-02-Persona-SystemPrompt-Refactor.md) |
| **TDD-BMM-03** | 废弃代码移除与功能精简 | [`docs/solution/TDD-BMM-03-Deprecated-Code-Removal.md`](../solution/TDD-BMM-03-Deprecated-Code-Removal.md) |
| **TDD-BMM-04** | 双代理流程集成与端到端测试 | [`docs/solution/TDD-BMM-04-DualAgent-Integration-E2E.md`](../solution/TDD-BMM-04-DualAgent-Integration-E2E.md) |
| **TDD-BMM-05** | BMM NodeExecutor 重构主实施指南 | [`docs/solution/TDD-BMM-05-Master-Implementation-Guide.md`](../solution/TDD-BMM-05-Master-Implementation-Guide.md) |

**架构文档更新**:
- [`docs/architecture/01_SYSTEM_ARCHITECTURE.md`](../architecture/01_SYSTEM_ARCHITECTURE.md) - 系统架构 (v3.0)
- [`docs/architecture/02_AGENT_ARCHITECTURE.md`](../architecture/02_AGENT_ARCHITECTURE.md) - Agent架构 (v5.1)
- [`docs/architecture/03_PIPELINE_ARCHITECTURE.md`](../architecture/03_PIPELINE_ARCHITECTURE.md) - 节点执行架构 (v2.3)

---

**文档结束**

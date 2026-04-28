# 节点配置体系改造方案研究报告

**日期**: 2026-03-26  
**编写者**: Jason (Backend Dev Agent)  
**任务 ID**: #5  
**关联报告**: 重构路线图 #7  

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [BMAD 核心角色职责分析](#2-bmad-核心角色职责分析)
3. [当前节点配置审计](#3-当前节点配置审计)
4. [差距分析](#4-差距分析)
5. [统一配置 Schema 设计](#5-统一配置-schema-设计)
6. [每个节点的具体改造方案](#6-每个节点的具体改造方案)
7. [实施步骤](#7-实施步骤)
8. [风险评估](#8-风险评估)

---

## 1. 执行摘要

### 1.1 节点配置现状

DocuSwarm 的五节点流水线（analyst → pm → ux → architect → po）当前采用**三文件分离**的配置体系：

| 文件 | 职责 | 格式 |
|------|------|------|
| `node.yaml` | 流水线元数据、交付物定义、Agent 参数、问题列表、依赖关系 | YAML |
| `persona.json` | Agent 角色身份、专业技能、工作原则、工具列表、输出格式 | JSON |
| `evaluator.yaml` | 评审标准权重、通过/升级阈值 | YAML |

配置完整度诊断（`node_config_completeness_checker.py`）显示所有 5 个节点的"表面完整度"均为 **100%**——即所有**已定义的必填字段**都存在。然而，这个评分掩盖了以下真实问题：

1. **浅层完整性陷阱**：诊断工具的 schema 定义本身存在遗漏，导致实际缺失的字段未被标记为 `required`
2. **代码期望与配置声明的隐形断层**：`context_builder.py` 中调用 `node_config.task.get("name", ...)` 但 `NodeConfig` 数据类中根本没有 `task` 字段
3. **配置碎片化**：节点元数据分散在 3 个文件中，无法作为整体理解单个节点的完整行为定义
4. **BMAD 角色定义与节点 persona 的双轨脱节**：`_bmad/_config/agents/` 中的 customize.yaml 是空模板，未承载任何 DocuSwarm 特有的角色增强
5. **评估器字段命名不一致**：`evaluator.yaml` 使用 `thresholds`（复数），但工具期望 `threshold`（单数），后者被标记为 `missing_optional`

### 1.2 改造目标

1. **建立单一真相配置文件**：将 3 个配置文件合并或强关联为统一 schema
2. **填补代码-配置断层**：补充 `task` 字段，与 `context_builder.py` 期望对齐
3. **规范字段命名**：解决 `thresholds` vs `threshold` 的命名不一致
4. **补充可选但重要的字段**：`timeout`、`retry`、`communication_style`、`critical_actions`、`memories`
5. **增强与 BMAD 角色的关联性**：在 customize.yaml 中填充项目专属内容

### 1.3 核心改进方向

```
当前状态：
  [node.yaml] + [persona.json] + [evaluator.yaml] → 松散耦合，各自为政

改造后：
  [node.yaml (v2)] ─── 引用 ──→ [persona.json (v2)]  ← 已有双向一致性
       │                              └── 新增: communication_style
       │                                        critical_actions
       │                                        memories
       │
       ├── 新增 task: section          ← 解决 context_builder.py 调用断层
       │    name, description, role_supplement
       │
       ├── 新增 runtime: section       ← 统一 timeout / retry
       │
       └── evaluator: section         ← 内联引用 evaluator.yaml
            └── 修正 thresholds → threshold
```

---

## 2. BMAD 核心角色职责分析

### 2.1 BMAD Master（核心编排角色）

`_bmad/core/agents/bmad-master.md` 定义了 BMAD Master 是整个体系的元编排者：

| 维度 | 内容 |
|------|------|
| **角色** | Master Task Executor + BMad Expert + Guiding Facilitator Orchestrator |
| **身份** | BMAD Core Platform 专家，运行时资源管理，直接任务执行引擎 |
| **沟通风格** | 直接、全面；用第三人称指代自己；结构化数字列表呈现 |
| **核心原则** | 运行时加载资源（never pre-load）；始终展示编号列表 |
| **工具** | workflow 执行、task 查找、party-mode 协作 |
| **核心职责** | 管理 config.yaml，加载 `{user_name}`、`{communication_language}`、`{output_folder}` |

**与 DocuSwarm 的关联**：BMAD Master 在 DocuSwarm 中的对应是 `HybridOrchestrator`——负责流水线编排、上下文验证、会话恢复。

### 2.2 BMAD 方法论定义的核心角色

根据 `_bmad/_config/agents/` 目录，以下角色是 DocuSwarm 五节点流水线的直接来源：

#### 2.2.1 bmm-analyst（需求分析师）

| 维度 | BMAD 定义（customize.yaml 结构） | DocuSwarm 实现（persona.json） |
|------|----------------------------------|-------------------------------|
| **核心任务** | 市场分析、需求发现、竞品研究 | 数据分析、BI 报告、统计分析 |
| **主要工具** | 用户访谈、数据挖掘、产品需求提炼 | data_analysis, statistical_tests, visualization, query_database, generate_report |
| **输出物** | 市场调研报告、需求分析文档、竞品分析 | analyst-report（6 个必需章节） |
| **协作关系** | 上游：用户需求 → 下游：PM | 上游：用户 context → 下游：PM |

**关键职责**：将模糊需求转化为可操作的业务分析，为后续所有节点提供需求基线。

#### 2.2.2 bmm-pm（产品经理）

| 维度 | BMAD 定义 | DocuSwarm 实现 |
|------|-----------|---------------|
| **核心任务** | 产品定义、路线图规划、需求优先级 | 项目计划、风险管理、利益相关者沟通 |
| **主要工具** | PRD 编写、用户故事、验收标准 | create_schedule, risk_assessment, stakeholder_management, generate_prd |
| **输出物** | PRD（产品需求文档）、路线图 | prd（8 个必需章节） |
| **协作关系** | 上游：Analyst → 下游：UX + Architect | 依赖：analyst |

**关键职责**：将分析洞见转化为具体产品需求，定义成功标准。

#### 2.2.3 bmm-ux-designer（用户体验设计师）

| 维度 | BMAD 定义 | DocuSwarm 实现 |
|------|-----------|---------------|
| **核心任务** | 用户研究、交互设计、原型制作 | 用户体验设计、可及性检查、可用性测试 |
| **主要工具** | Figma/Sketch、用户测试、设计系统 | create_personas, design_flows, create_wireframes, accessibility_check |
| **输出物** | 线框图、用户流程图、设计规范 | ux-design（6 个必需章节） |
| **协作关系** | 上游：PM → 下游：Architect | 依赖：analyst, pm |

**关键职责**：确保产品以用户为中心，为开发团队提供可执行的设计规范。

#### 2.2.4 bmm-architect（系统架构师）

| 维度 | BMAD 定义 | DocuSwarm 实现 |
|------|-----------|---------------|
| **核心任务** | 系统设计、技术选型、架构评审 | 分布式系统、微服务、API 设计 |
| **主要工具** | 架构图、ADR、技术原型 | system_design, api_design, database_design, security_analysis, performance_analysis |
| **输出物** | 架构文档、技术决策记录 | architecture（9 个必需章节）|
| **协作关系** | 上游：UX + PM → 下游：Dev + PO | 依赖：analyst, pm, ux |

**关键职责**：平衡技术卓越与业务约束，为实施团队提供明确的技术蓝图。

#### 2.2.5 bmm-sm（Scrum Master）/ po → DocuSwarm PO

| 维度 | BMAD 定义（bmm-sm + pm 共同映射） | DocuSwarm 实现（po 节点） |
|------|----------------------------------|--------------------------|
| **核心任务** | 产品 Backlog 管理、冲刺规划、发布管理 | 产品愿景、Epic 拆分、用户故事创建 |
| **主要工具** | Jira/Linear、优先级框架（MoSCoW, RICE） | roadmap_planning, epic_creation, story_creation, prioritization, release_planning |
| **输出物** | 已排优先级的 Backlog、冲刺计划 | epics-stories（7 个必需章节） |
| **协作关系** | 上游：Architect + PM → 下游：Dev | 依赖：analyst, pm, ux, architect（全部前置节点）|

**关键职责**：将所有前期工作转化为可执行的开发计划，实现需求到任务的完整映射。

### 2.3 BMAD 角色协作关系图

```
用户需求 (context_file)
    │
    ▼
[Analyst] ──────────────────────────────────────────────────────────────┐
  输出: analyst-report                                                    │
    │                                                                     │
    ▼                                                                     │
[PM] ← 依赖 analyst                                                      │
  输出: prd                                                               │
    │                                                                     │
    ▼                                                                     │
[UX] ← 依赖 analyst + pm                                                 │
  输出: ux-design                                                         │
    │                                                                     │
    ▼                                                                     │
[Architect] ← 依赖 analyst + pm + ux                                     │
  输出: architecture                                                      │
    │                                                                     │
    ▼                                                                     │
[PO] ← 依赖 analyst + pm + ux + architect ◄──────────────────────────────┘
  输出: epics-stories（最终交付物）
```

---

## 3. 当前节点配置审计

### 3.1 analyst 节点配置审计

#### node.yaml

```yaml
# 当前内容（完整）
node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist - transforms raw data into actionable business insights
sequence: 1
deliverable_type: analyst-report
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
agent:
  type: independent
  model: sonnet
  temperature: 0.7
questions:
  - id: q1
    text: "What is the business context and objectives for this analysis?"
    required: true
  - id: q2
    text: "What data sources are available for this analysis?"
    required: true
  - id: q3
    text: "What specific questions should the analysis answer?"
    required: true
dependencies: []
```

**问题发现**：
- 缺少 `task` section（但 `context_builder.py` 第 62 行调用 `node_config.task.get("name", ...)`）
- 缺少 `runtime` section（`timeout`, `retry`）
- `description` 描述的是角色而非任务，与 `context_builder.py` 将其用作 `task_description` 的期望不符

#### persona.json

```json
// 当前内容（完整）
{
  "name": "Analyst",
  "role": "Data Analyst & Business Intelligence Specialist",
  "identity": "You are an expert data analyst who transforms raw data into actionable business insights...",
  "expertise": [7 条专业技能],
  "principles": [5 条工作原则],
  "tools": ["data_analysis", "statistical_tests", "visualization", "query_database", "generate_report"],
  "output_format": {
    "type": "analyst-report",
    "sections": [6 个章节],
    "format": "markdown"
  }
}
```

**问题发现**：
- 缺少 `communication_style`（BMAD customize.yaml 定义了此字段）
- 缺少 `memories`（持久记忆，对 Agent 角色扮演一致性有价值）
- 缺少 `critical_actions`（关键行动清单，确保 Agent 不遗漏核心步骤）
- `role` 字段与 `node.yaml` 的 `description` 重复（均为"Data Analyst & Business Intelligence Specialist"）

#### evaluator.yaml

```yaml
# 当前内容（完整）
criteria:
  - name: evidence_quality
    weight: 0.40
  - name: actionability
    weight: 0.30
  - name: completeness
    weight: 0.15
  - name: clarity
    weight: 0.10
  - name: consistency
    weight: 0.05
thresholds:          # ← 此字段名为 thresholds（复数）
  approval: 0.70
  escalation: 0.50
```

**问题发现**：
- 字段名为 `thresholds`（复数），但诊断工具的 schema 期望 `threshold`（单数）
- 缺少 `max_iterations`（最大迭代次数，应为 2-3 次）
- 缺少 `model`（评估器使用的模型，可能需要与 Independent Agent 使用不同模型）
- `thresholds` 被诊断工具标记为 `extra_field`，属于**非标准字段**

#### 与代码执行对齐度

| 代码层面的期望 | 配置中是否满足 | 差距说明 |
|--------------|--------------|---------|
| `node_config.task.get("name")` | ❌ 不满足 | `NodeConfig` 无 `task` 属性 |
| `node_config.description` 作为任务描述 | ⚠️ 部分满足 | 值描述的是角色而非任务 |
| `node_config.evaluator.get("criteria", [])` | ✅ 满足 | evaluator.yaml 中存在 `criteria` |
| `deliverable_requirements` 含 `template_title` | ❌ 不满足 | `node.yaml` 无 `template_title` 字段 |
| `deliverable_requirements` 含 `output_filename` | ❌ 不满足 | `node.yaml` 无 `output_filename` 字段 |

---

### 3.2 pm 节点配置审计

#### 配置现状摘要

| 文件 | 字段完整度 | 关键内容 |
|------|-----------|---------|
| node.yaml | 缺 task/runtime/template_title/output_filename | sequence=2, deliverable_type=prd, 8 个章节, 4 个问题（1 个可选）|
| persona.json | 缺 communication_style/memories/critical_actions | role="Project Manager", 7 项专业技能, 5 条原则 |
| evaluator.yaml | 同 analyst | completeness(0.40), clarity(0.30), actionability(0.15) |

**特有问题**：
- `pm` 节点的 `persona.role` 定义为 "Project Manager"，但按 BMAD 方法论，产品经理（Product Manager）与项目经理（Project Manager）有本质区别。DocuSwarm 目标是生成产品文档，应该是 **Product Manager**
- pm 节点的 `questions` 包含 4 个问题（其中 q4 为非必填），而其他节点均为 3-4 个问题

---

### 3.3 ux 节点配置审计

#### 配置现状摘要

| 文件 | 字段完整度 | 关键内容 |
|------|-----------|---------|
| node.yaml | 缺 task/runtime/template_title/output_filename | sequence=3, deliverable_type=ux-design, 6 个章节, 4 个问题（1 个可选）|
| persona.json | 缺 communication_style/memories/critical_actions | role="User Experience Designer", 7 项专业技能 |
| evaluator.yaml | 同 analyst | actionability(0.40), clarity(0.30), completeness(0.15) |

**特有问题**：
- ux 节点 `agent.temperature=0.7`（与 architect/po 的 `0.5` 不一致），对于设计类节点，更高的创造性参数合理，但应明确文档化
- `tools` 列表中的 `create_wireframes` 在当前实现中实际上是文本描述工具，并不真正生成图形化线框，这是语义上的误导

---

### 3.4 architect 节点配置审计

#### 配置现状摘要

| 文件 | 字段完整度 | 关键内容 |
|------|-----------|---------|
| node.yaml | 缺 task/runtime/template_title/output_filename | sequence=4, deliverable_type=architecture, **9 个章节**（最多的节点）, 4 个问题（全必填）|
| persona.json | 缺 communication_style/memories/critical_actions | role="Software Architect", 7 项专业技能 |
| evaluator.yaml | 同 analyst | completeness(0.35), consistency(0.30), actionability(0.20) |

**特有问题**：
- architect 节点有 9 个必需章节（最多），但 `evaluator.yaml` 的 `approval` 阈值仍为 0.70，与其他节点相同，未体现其复杂性
- `agent.temperature=0.5`（更保守），对于需要严格逻辑的架构设计合理，但未在配置中注释说明原因

---

### 3.5 po 节点配置审计

#### 配置现状摘要

| 文件 | 字段完整度 | 关键内容 |
|------|-----------|---------|
| node.yaml | 缺 task/runtime/template_title/output_filename | sequence=5, deliverable_type=epics-stories, 7 个章节, 4 个问题（全必填）|
| persona.json | 缺 communication_style/memories/critical_actions | role="Product Owner", 7 项专业技能 |
| evaluator.yaml | 同 analyst | completeness(0.40), actionability(0.30), clarity(0.15) |

**特有问题**：
- po 节点映射到 `_bmad/_config/agents/bmm-pm.customize.yaml`（与 pm 节点共用同一 BMAD 配置）——诊断工具的 `bmad_vs_node_alignment` 显示 `po → bmm-pm`，这意味着 PO 没有独立的 BMAD Agent 定义
- po 节点依赖所有4个前置节点，是流水线中拥有最多依赖的节点，但其 `evaluator.yaml` 阈值（approval=0.70）与其他节点无差异

---

## 4. 差距分析

### 4.1 诊断工具输出的配置完整度报告解读

诊断工具报告所有节点完整度为 **100%**，但这是一个**假阳性结果**，原因：

```
诊断工具 schema 定义的必填字段集（仅9个）：
  node.yaml:     [node_id, name, description, sequence, deliverable_type, 
                  deliverable, agent, questions, dependencies]
  
  被遗漏的真实必需字段（代码层面期望）：
  ├── deliverable.template_title     ← context_builder.py L98
  ├── deliverable.output_filename    ← context_builder.py L100
  └── task.*                         ← context_builder.py L62-64（整个 section）

诊断工具识别的可选字段（实际是重要缺失）：
  node.yaml:     [evaluator, timeout, retry]
  persona.json:  [communication_style, memories, critical_actions]
  evaluator.yaml:[threshold, max_iterations, model]
```

### 4.2 _bmad 角色定义 vs autoBMAD 节点配置的差距矩阵

| 差距维度 | _bmad customize.yaml 定义 | autoBMAD persona.json 现状 | 缺口 |
|---------|--------------------------|--------------------------|------|
| `communication_style` | 声明为 persona 核心字段 | ❌ 所有节点缺失 | 高优先级 |
| `memories` | 声明为 Agent 持久记忆 | ❌ 所有节点缺失 | 中优先级 |
| `critical_actions` | 声明为 Agent 关键行动 | ❌ 所有节点缺失 | 中优先级 |
| `menu` | Agent 交互菜单 | N/A（流水线无交互菜单） | 不适用 |
| `prompts` | 自定义提示模板 | N/A（使用独立 prompts/ 目录） | 不适用 |
| 角色身份专化 | 需要 DocuSwarm 项目专属化 | 通用定义，无项目上下文 | 高优先级 |

### 4.3 缺失的配置字段汇总

#### node.yaml 层面缺失字段

| 字段 | 类型 | 所有节点缺失 | 代码层影响 |
|------|------|-------------|-----------|
| `task.name` | `str` | ✅ 5/5 节点 | `context_builder.py:62` 回退到 `node_name` |
| `task.description` | `str` | ✅ 5/5 节点 | `context_builder.py:63` 回退到 `description`（语义错误） |
| `task.role_supplement` | `str` | ✅ 5/5 节点 | `context_builder.py:64` 返回空字符串 |
| `deliverable.template_title` | `str` | ✅ 5/5 节点 | `context_builder.py:107` 回退到 `deliverable_type` |
| `deliverable.output_filename` | `str` | ✅ 5/5 节点 | 无强制要求，但影响文件命名 |
| `deliverable.format_hints` | `dict` | ✅ 5/5 节点 | 无当前影响，未来扩展需要 |
| `runtime.timeout` | `int (秒)` | ✅ 5/5 节点 | 无超时保护 |
| `runtime.retry.max_attempts` | `int` | ✅ 5/5 节点 | 无重试限制 |
| `runtime.retry.backoff` | `float` | ✅ 5/5 节点 | 无退避控制 |

#### persona.json 层面缺失字段

| 字段 | 类型 | 所有节点缺失 | 功能影响 |
|------|------|-------------|---------|
| `communication_style` | `str` | ✅ 5/5 节点 | Agent 的沟通风格无明确定义 |
| `memories` | `list[str]` | ✅ 5/5 节点 | 无项目相关持久记忆 |
| `critical_actions` | `list[str]` | ✅ 5/5 节点 | 无核心步骤强制清单 |

#### evaluator.yaml 层面问题

| 问题 | 节点 | 描述 |
|------|------|------|
| `thresholds` vs `threshold` 命名不一致 | 5/5 节点 | 字段名歧义，诊断工具报告为 `extra_field` |
| 缺少 `max_iterations` | 5/5 节点 | 无迭代上限控制 |
| 缺少 `model` | 5/5 节点 | 评估器无法指定专用模型 |

### 4.4 冗余/过时的配置字段

| 字段 | 位置 | 冗余原因 |
|------|------|---------|
| `persona.json.role` | 所有节点 | 与 `node.yaml.description` 内容重复（均为角色标题）|
| `persona.json.output_format` | 所有节点 | 与 `node.yaml.deliverable` 完全重复（类型+章节+格式）|
| `node.yaml.name` | 所有节点 | 与 `node.yaml.node_id` 信息重复（只是首字母大写版本）|

### 4.5 节点实际执行的任务 vs 配置声明的任务不一致

根据 `context_builder.py` 的分析：

```
实际任务声明来源（context_builder.py 第62行）：
  task_name = node_config.task.get("name", node_config.name)
                                   ↑ task section 不存在
                                              ↑ 回退到 node_name（如 "Analyst"）
  
问题：IndependentAgent 收到的 task_name 是 "Analyst"（角色名）而非
       "create-product-brief"（任务名），语义完全错误。
       
       "Analyst" 回答的是"我是谁"，而非"我要做什么"。
```

| 节点 | 当前 task_name（回退值） | 语义正确的 task_name |
|------|------------------------|---------------------|
| analyst | "Analyst" | "create-business-analysis-report" |
| pm | "PM" | "create-product-requirements-document" |
| ux | "UX" | "create-ux-design-specification" |
| architect | "Architect" | "create-system-architecture-document" |
| po | "PO" | "create-epics-and-user-stories" |

---

## 5. 统一配置 Schema 设计

### 5.1 设计原则

1. **向后兼容**：现有的 `loader.py` 中的 `NodeConfig` 数据类是稳定的 Python API，schema 变更不能破坏它
2. **单一真相**：尽量将分散的配置汇聚，减少跨文件引用时的不一致风险
3. **代码-配置对齐**：新 schema 必须与 `context_builder.py` 的实际字段访问路径完全对应
4. **渐进式升级**：通过 `schema_version` 字段实现平滑迁移

### 5.2 node.yaml v2 完整 Schema 定义

```yaml
# ================================================================
# DocuSwarm Node Configuration Schema v2
# ================================================================

# --- 元数据 ---
schema_version: "2.0"          # 必填; str; Schema 版本，用于向后兼容判断

node_id: <string>              # 必填; str; 节点唯一标识符（如 "analyst"）
name: <string>                 # 必填; str; 节点显示名称（如 "Analyst"）
description: <string>          # 必填; str; 节点功能描述（用于人类阅读）
sequence: <int>                # 必填; int; 流水线执行顺序（1-based）

# --- 任务契约（新增，解决 context_builder.py 调用断层） ---
task:
  name: <string>               # 必填(v2); str; 任务名（如 "create-business-analysis-report"）
  description: <string>        # 必填(v2); str; 任务描述（注入 IndependentAgent 的 task_description）
  role_supplement: <string>    # 可选; str; 角色补充说明（默认: ""）

# --- 交付物定义 ---
deliverable_type: <string>     # 必填; str; 交付物类型标识（如 "analyst-report"）
deliverable:
  required_sections:           # 必填; list[str]; 必需章节列表
    - <section_name>
  template_title: <string>     # 可选; str; 模板标题（默认: deliverable_type 值）
  output_filename: <string>    # 可选; str; 输出文件名（默认: "{deliverable_type}.md"）
  format_hints:                # 可选; dict; 格式提示（默认: {}）
    max_words: <int>
    target_audience: <string>
    tone: <string>

# --- Agent 配置 ---
agent:
  type: independent            # 必填; str; 固定为 "independent"
  model: <string>              # 必填; str; LLM 模型标识（如 "sonnet"）
  temperature: <float>         # 必填; float; 生成温度（0.0-1.0）
  persona_file: persona.json   # 可选; str; persona 文件名（默认: "persona.json"）

# --- Evaluator 配置（内联引用，规范化字段名） ---
evaluator:
  criteria_file: evaluator.yaml  # 可选; str; 评估标准文件（默认: "evaluator.yaml"）
  threshold: <float>             # 可选; float; 通过阈值（默认: 0.70）
  max_iterations: <int>          # 可选; int; 最大迭代次数（默认: 3）
  model: <string>                # 可选; str; 评估器使用的模型（默认: 与 agent.model 相同）

# --- 运行时配置（新增） ---
runtime:
  timeout: <int>                 # 可选; int; 执行超时（秒，默认: 300）
  retry:
    max_attempts: <int>          # 可选; int; 最大重试次数（默认: 2）
    backoff: <float>             # 可选; float; 退避系数（默认: 1.5）

# --- 问题列表 ---
questions:
  - id: <string>               # 必填; str; 问题唯一 ID
    text: <string>             # 必填; str; 问题文本
    required: <bool>           # 必填; bool; 是否必答

# --- 依赖关系 ---
dependencies:
  - <node_id>                  # list[str]; 前置节点 ID 列表
```

### 5.3 persona.json v2 完整 Schema 定义

```json
{
  "schema_version": "2.0",           // 必填; str; Schema 版本

  "name": "<string>",                // 必填; str; 角色名称
  "role": "<string>",                // 必填; str; 角色职称
  "identity": "<string>",            // 必填; str; 角色身份描述（注入系统提示）
  
  "communication_style": "<string>", // 新增必填; str; 沟通风格描述
  
  "expertise": ["<string>"],         // 必填; list[str]; 专业技能列表
  "principles": ["<string>"],        // 必填; list[str]; 工作原则列表
  
  "critical_actions": ["<string>"],  // 新增可选; list[str]; 关键行动清单（每次执行必须完成）
  "memories": ["<string>"],          // 新增可选; list[str]; 持久记忆（项目相关背景）
  
  "tools": ["<string>"],             // 必填; list[str]; 工具列表
  
  "output_format": {                 // 建议保留（独立于 node.yaml 的 deliverable）
    "type": "<string>",
    "sections": ["<string>"],
    "format": "markdown"
  }
}
```

### 5.4 evaluator.yaml v2 完整 Schema 定义（规范化）

```yaml
# ================================================================
# DocuSwarm Evaluator Configuration Schema v2
# ================================================================

schema_version: "2.0"

# 评审标准（权重之和必须为 1.0）
criteria:
  - name: <string>             # 必填; str; 标准名称
    description: <string>      # 必填; str; 标准描述
    weight: <float>            # 必填; float; 权重（0.0-1.0）

# 通过阈值（规范化字段名：threshold，单数）
threshold:                     # 原字段名 thresholds 改为 threshold（单数）
  approval: <float>            # 必填; float; 批准阈值（默认: 0.70）
  escalation: <float>          # 必填; float; 升级阈值（默认: 0.50）

# 运行时控制（新增）
max_iterations: <int>          # 可选; int; 最大评估迭代次数（默认: 3）
model: <string>                # 可选; str; 评估模型（默认: 继承自 node.yaml agent.model）
```

### 5.5 向后兼容的 Schema 版本策略

```
版本判断逻辑（NodeLoader._build_node_config 中实现）：

  if schema_version == "2.0":
    # 读取新字段
    task_name = config["task"]["name"]
    threshold = evaluator_config["threshold"]
  else:  # v1 或无版本（兼容旧 schema）
    # 使用回退逻辑
    task_name = config["name"]  # 回退到 node name
    threshold = evaluator_config.get("thresholds", {})  # 兼容旧字段名

迁移路径：
  阶段 1：loader.py 同时支持 v1/v2（向后兼容）
  阶段 2：所有节点配置升级到 v2
  阶段 3：移除 v1 兼容代码
```

### 5.6 NodeConfig 数据类升级方案

```python
@dataclass
class NodeTaskConfig:
    """v2: 任务契约配置（新增）"""
    name: str
    description: str = ""
    role_supplement: str = ""

@dataclass  
class NodeRuntimeConfig:
    """v2: 运行时配置（新增）"""
    timeout: int = 300
    retry_max_attempts: int = 2
    retry_backoff: float = 1.5

@dataclass
class NodeConfig:
    """Complete node configuration v2"""
    node_id: str
    name: str
    description: str
    sequence: int
    deliverable_type: str
    deliverable: NodeDeliverableConfig
    agent: NodeAgentConfig
    questions: NodeQuestionsConfig
    dependencies: NodeDependenciesConfig
    evaluator: NodeEvaluatorConfig | None = None
    persona: dict[str, Any] | None = None
    # === v2 新增字段 ===
    schema_version: str = "1.0"
    task: NodeTaskConfig | None = None          # 新增
    runtime: NodeRuntimeConfig | None = None    # 新增
```

---

## 6. 每个节点的具体改造方案

### 6.1 analyst 节点改造方案

#### node.yaml 改造（Before → After）

**Before (v1)**：
```yaml
node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist - transforms raw data into actionable business insights
sequence: 1
deliverable_type: analyst-report
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
agent:
  type: independent
  model: sonnet
  temperature: 0.7
questions:
  - id: q1
    text: "What is the business context and objectives for this analysis?"
    required: true
  - id: q2
    text: "What data sources are available for this analysis?"
    required: true
  - id: q3
    text: "What specific questions should the analysis answer?"
    required: true
dependencies: []
```

**After (v2)**：
```yaml
schema_version: "2.0"

node_id: analyst
name: Analyst
description: Transforms raw requirements into structured business analysis, providing evidence-based insights as the foundation for all downstream nodes.
sequence: 1

# 新增: 任务契约（解决 context_builder.py task.get() 调用断层）
task:
  name: create-business-analysis-report
  description: |
    Conduct a comprehensive business analysis of the provided requirements.
    Identify key stakeholders, business objectives, data requirements, and
    analytical frameworks. Produce an evidence-based analyst report that
    serves as the factual foundation for PM, UX, Architect, and PO nodes.
  role_supplement: |
    As a Business Analyst, prioritize evidence quality and actionability.
    Every finding must be traceable to specific data sources or user inputs.
    Clearly distinguish between facts, inferences, and assumptions.

deliverable_type: analyst-report
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
  template_title: "Business Analysis Report"          # 新增
  output_filename: "analyst-report.md"               # 新增
  format_hints:                                       # 新增
    max_words: 3000
    target_audience: "Product and Engineering teams"
    tone: "analytical, evidence-based"

agent:
  type: independent
  model: sonnet
  temperature: 0.7

# 新增: Evaluator 内联引用
evaluator:
  criteria_file: evaluator.yaml
  threshold: 0.70
  max_iterations: 3

# 新增: 运行时配置
runtime:
  timeout: 300
  retry:
    max_attempts: 2
    backoff: 1.5

questions:
  - id: q1
    text: "What is the business context and objectives for this analysis?"
    required: true
  - id: q2
    text: "What data sources are available for this analysis?"
    required: true
  - id: q3
    text: "What specific questions should the analysis answer?"
    required: true

dependencies: []
```

#### persona.json 改造（Before → After）

**Before (v1)**：(无 communication_style, memories, critical_actions)

**After (v2)**：
```json
{
  "schema_version": "2.0",
  "name": "Analyst",
  "role": "Business Analyst & Intelligence Specialist",
  "identity": "You are an expert business analyst who transforms raw requirements and data into actionable insights. You bridge the gap between business needs and technical solutions through systematic analysis, evidence-based reasoning, and clear communication of findings.",
  
  "communication_style": "Analytical and precise. Present findings with supporting evidence and confidence levels. Use structured formats (tables, bullet points) for clarity. Acknowledge uncertainty explicitly rather than overstating conclusions.",
  
  "expertise": [
    "Business requirements analysis and elicitation",
    "Stakeholder identification and needs assessment",
    "Data analysis and statistical interpretation",
    "Business intelligence reporting",
    "Trend identification and forecasting",
    "Risk and assumption documentation",
    "Data quality assessment and gap analysis"
  ],
  "principles": [
    "Every claim must be supported by evidence from the provided context",
    "Clearly label assumptions vs. facts vs. inferences",
    "Focus on actionable insights that drive downstream decisions",
    "Document what is unknown as explicitly as what is known",
    "Prioritize findings by business impact"
  ],
  
  "critical_actions": [
    "Explicitly state all data sources used in the analysis",
    "Document assumptions made due to missing information",
    "Include limitations section with concrete gaps identified",
    "Ensure all recommendations are traceable to specific findings",
    "Cross-reference with provided context for every major claim"
  ],
  
  "memories": [
    "DocuSwarm produces project documentation through a 5-stage pipeline",
    "My output (analyst-report) is the factual baseline for PM, UX, Architect, and PO nodes",
    "Analysis depth should be proportional to the detail provided in the original context"
  ],
  
  "tools": [
    "data_analysis",
    "statistical_tests",
    "visualization",
    "query_database",
    "generate_report"
  ],
  
  "output_format": {
    "type": "analyst-report",
    "sections": [
      "executive_summary",
      "data_sources",
      "analysis_methodology",
      "findings",
      "recommendations",
      "limitations"
    ],
    "format": "markdown"
  }
}
```

#### evaluator.yaml 改造（Before → After）

**Before (v1)**：
```yaml
criteria:
  - name: evidence_quality
    weight: 0.40
  ...
thresholds:          # ← 字段名错误（复数）
  approval: 0.70
  escalation: 0.50
```

**After (v2)**：
```yaml
schema_version: "2.0"

criteria:
  - name: evidence_quality
    description: "Quality and reliability of evidence, sources, and data supporting conclusions"
    weight: 0.40
  - name: actionability
    description: "Degree to which recommendations can be directly used by PM, UX, and Architect nodes"
    weight: 0.30
  - name: completeness
    description: "Extent to which all required sections and business questions are addressed"
    weight: 0.15
  - name: clarity
    description: "Clear and unambiguous communication of findings and recommendations"
    weight: 0.10
  - name: consistency
    description: "Logical coherence and internal consistency across the analysis"
    weight: 0.05

threshold:           # ← 修正为单数
  approval: 0.70
  escalation: 0.50

max_iterations: 3    # ← 新增
```

---

### 6.2 pm 节点改造方案

#### 关键改造点（增量说明）

1. **角色名称修正**：`persona.role` 从 "Project Manager" 改为 "Product Manager"（业务语义修正）
2. **task section 新增**：
   ```yaml
   task:
     name: create-product-requirements-document
     description: |
       Define comprehensive product requirements based on the business analysis.
       Transform stakeholder needs into specific, measurable, and achievable product
       requirements. Produce a PRD that aligns all downstream nodes on what to build.
     role_supplement: |
       As a Product Manager, prioritize clarity and completeness of requirements.
       Every requirement must have clear acceptance criteria and business justification.
   ```
3. **deliverable 补充**：
   ```yaml
   template_title: "Product Requirements Document"
   output_filename: "prd.md"
   format_hints:
     max_words: 4000
     target_audience: "Engineering and Design teams"
     tone: "precise, requirements-focused"
   ```
4. **critical_actions 新增**：
   ```json
   "critical_actions": [
     "Ensure every functional requirement has explicit acceptance criteria",
     "Document all constraints (technical, budget, timeline, regulatory)",
     "Validate requirements against the analyst-report findings",
     "Include at least 5 user stories with clear personas and goals",
     "Risk register must include mitigation strategies, not just identification"
   ]
   ```
5. **memories 新增**：
   ```json
   "memories": [
     "My PRD is the primary input for UX Designer and System Architect nodes",
     "Requirements must be technically feasible for the technology stack context",
     "Previous analyst-report provides factual basis—do not contradict it without justification"
   ]
   ```
6. **evaluator.yaml 字段名修正**：`thresholds` → `threshold`，新增 `max_iterations: 3`

---

### 6.3 ux 节点改造方案

#### 关键改造点（增量说明）

1. **task section 新增**：
   ```yaml
   task:
     name: create-ux-design-specification
     description: |
       Design the user experience for the product defined in the PRD.
       Create comprehensive UX documentation including user personas, interaction
       flows, wireframe descriptions, and accessibility guidelines.
     role_supplement: |
       As a UX Designer, advocate for users at every decision point.
       Ground all design decisions in user research or explicitly stated assumptions.
   ```
2. **deliverable 补充**：
   ```yaml
   template_title: "UX Design Specification"
   output_filename: "ux-design.md"
   format_hints:
     max_words: 3500
     target_audience: "Development team and stakeholders"
     tone: "user-centered, descriptive"
   ```
3. **tools 语义修正**：将 `create_wireframes` 注释更名为 `describe_wireframes`（因当前实现为文本描述，非图形生成），或在 `critical_actions` 中说明：
   ```json
   "critical_actions": [
     "Create at least 3 distinct user personas with specific goals and pain points",
     "Document wireframes as detailed text descriptions (no image generation available)",
     "Include WCAG 2.1 AA compliance checklist",
     "Define error states and edge cases for every key user flow",
     "Ensure design decisions are traceable to PRD requirements"
   ]
   ```
4. **evaluator.yaml 字段名修正**：`thresholds` → `threshold`，新增 `max_iterations: 3`

---

### 6.4 architect 节点改造方案

#### 关键改造点（增量说明）

1. **task section 新增**：
   ```yaml
   task:
     name: create-system-architecture-document
     description: |
       Design the technical architecture for the system described in PRD and UX spec.
       Define component boundaries, data flows, API contracts, security model,
       and technology choices. Provide a blueprint that development teams can
       directly implement.
     role_supplement: |
       As a Software Architect, balance technical excellence with practical constraints.
       Every architectural decision must document the trade-offs considered.
       Prefer simplicity and proven patterns over novel approaches unless justified.
   ```
2. **deliverable 补充**：
   ```yaml
   template_title: "System Architecture Document"
   output_filename: "architecture.md"
   format_hints:
     max_words: 5000
     target_audience: "Engineering teams and technical stakeholders"
     tone: "technical, precise, decision-focused"
   ```
3. **evaluator.yaml 阈值调整**：鉴于 architect 节点有 9 个必需章节（最多），建议提高 `approval` 阈值：
   ```yaml
   threshold:
     approval: 0.75   # 从 0.70 提高到 0.75（复杂度补偿）
     escalation: 0.55 # 从 0.50 提高到 0.55
   max_iterations: 3
   ```
4. **critical_actions 新增**（架构节点特殊关注点）：
   ```json
   "critical_actions": [
     "Document every major architectural decision with explicit trade-off rationale",
     "Define API contracts with request/response schemas for all integration points",
     "Include threat model covering authentication, authorization, and data protection",
     "Specify database schema with relationships and indexing strategy",
     "Technology choices must align with the implied stack from original context"
   ]
   ```

---

### 6.5 po 节点改造方案

#### 关键改造点（增量说明）

1. **BMAD Agent 映射修正**：当前 po 节点映射到 `bmm-pm.customize.yaml`。建议：
   - 方案 A：为 po 节点创建独立的 `_bmad/_config/agents/bmm-po.customize.yaml`
   - 方案 B：保持当前映射，但在 persona.json 中明确区分 PM vs PO 职责

2. **task section 新增**：
   ```yaml
   task:
     name: create-epics-and-user-stories
     description: |
       Synthesize all upstream deliverables (analysis, PRD, UX design, architecture)
       into a prioritized product backlog. Define epics, user stories with acceptance
       criteria, story point estimates, dependencies, and release plan.
     role_supplement: |
       As a Product Owner, you are the final step before development begins.
       Your output must be immediately actionable by development teams.
       Every story must have clear acceptance criteria testable by QA.
   ```
3. **deliverable 补充**：
   ```yaml
   template_title: "Product Backlog: Epics & User Stories"
   output_filename: "epics-stories.md"
   format_hints:
     max_words: 6000
     target_audience: "Development teams, QA, and stakeholders"
     tone: "action-oriented, implementation-ready"
   ```
4. **evaluator.yaml 字段名修正**：`thresholds` → `threshold`，新增 `max_iterations: 3`
5. **memories 新增**（po 节点作为最终汇总节点有特殊需求）：
   ```json
   "memories": [
     "I am the final node—my output directly feeds into development sprint planning",
     "All upstream deliverables (analyst-report, PRD, UX design, architecture) must be reflected",
     "User stories should follow the format: As a [persona], I want [goal], so that [benefit]",
     "Each epic should map to at least one specific PRD functional requirement"
   ]
   ```

---

## 7. 实施步骤

### 7.1 分步骤操作清单

#### Phase 1：基础 Schema 升级（1-2 天）

- [ ] **P1-1** 更新 `autoBMAD/nodes/loader.py`：
  - 新增 `NodeTaskConfig`、`NodeRuntimeConfig` 数据类
  - 更新 `NodeConfig` 新增 `task`、`runtime`、`schema_version` 字段
  - 在 `_build_node_config()` 中实现 v1/v2 双版本解析逻辑
  - 修正 `NodeEvaluatorConfig` 支持 `threshold`（单数）和向后兼容 `thresholds`（复数）

- [ ] **P1-2** 更新 `autoBMAD/docuswarm/node_execution/context_builder.py`：
  - 修正 `node_config.task.get(...)` 访问：从 `NodeTaskConfig` 对象读取，非 dict
  - 当 `task` 为 `None` 时（v1 schema）使用现有回退逻辑

- [ ] **P1-3** 更新 `tools/node_config_completeness_checker.py`：
  - 将 `task.name`、`task.description` 加入 `required` 字段列表
  - 将 `deliverable.template_title`、`deliverable.output_filename` 加入 `optional` 字段列表
  - 修正 `threshold` vs `thresholds` 的检测逻辑，v2 期望 `threshold`（单数）

#### Phase 2：节点配置文件升级（2-3 天）

- [ ] **P2-1** 升级 `analyst/node.yaml`（按本报告 §6.1 的 After 版本）
- [ ] **P2-2** 升级 `analyst/persona.json`（新增 communication_style, critical_actions, memories）
- [ ] **P2-3** 升级 `analyst/evaluator.yaml`（修正 thresholds→threshold，新增 max_iterations）
- [ ] **P2-4** 升级 `pm/node.yaml`、`pm/persona.json`、`pm/evaluator.yaml`
- [ ] **P2-5** 升级 `ux/node.yaml`、`ux/persona.json`、`ux/evaluator.yaml`
- [ ] **P2-6** 升级 `architect/node.yaml`、`architect/persona.json`、`architect/evaluator.yaml`
- [ ] **P2-7** 升级 `po/node.yaml`、`po/persona.json`、`po/evaluator.yaml`

#### Phase 3：BMAD 角色关联修正（1 天）

- [ ] **P3-1** 创建 `_bmad/_config/agents/bmm-po.customize.yaml`（为 PO 节点建立独立 BMAD Agent 定义）
- [ ] **P3-2** 在 `bmm-analyst.customize.yaml` 中填充 DocuSwarm 专属内容（persona 覆盖）
- [ ] **P3-3** 更新诊断工具的 `bmad_vs_node_alignment` 逻辑（po → bmm-po）

#### Phase 4：验证与测试（1 天）

- [ ] **P4-1** 运行升级后的诊断工具：`python tools/node_config_completeness_checker.py`
  - 验证：所有 5 个节点的 `task.name`、`task.description` 字段存在
  - 验证：`evaluator.yaml` 的 `threshold`（单数）字段存在
  - 验证：`persona.json` 的 `communication_style` 字段存在
- [ ] **P4-2** 运行单元测试：
  ```bash
  python -m pytest tests/ -k "loader or config or context_builder" -v
  ```
- [ ] **P4-3** 验证向后兼容性：确保 v1 格式的旧配置文件仍能被 `NodeLoader.load()` 正确解析

### 7.2 配置迁移脚本设计

```python
#!/usr/bin/env python3
"""
DocuSwarm Node Configuration Migration Script
从 Schema v1 迁移到 Schema v2

用法：
  python scripts/migrate_node_config_v1_to_v2.py [--dry-run] [--node <node_id>]
"""

import yaml
import json
from pathlib import Path
from typing import Any

NODES_DIR = Path("autoBMAD/nodes")

TASK_DEFAULTS = {
    "analyst": {
        "name": "create-business-analysis-report",
        "description": "Conduct comprehensive business analysis...",
        "role_supplement": "As a Business Analyst, prioritize evidence quality..."
    },
    "pm": {
        "name": "create-product-requirements-document",
        "description": "Define comprehensive product requirements...",
        "role_supplement": "As a Product Manager, prioritize clarity..."
    },
    "ux": {
        "name": "create-ux-design-specification",
        "description": "Design the user experience...",
        "role_supplement": "As a UX Designer, advocate for users..."
    },
    "architect": {
        "name": "create-system-architecture-document",
        "description": "Design the technical architecture...",
        "role_supplement": "As a Software Architect, balance excellence with constraints..."
    },
    "po": {
        "name": "create-epics-and-user-stories",
        "description": "Synthesize all upstream deliverables...",
        "role_supplement": "As a Product Owner, ensure output is immediately actionable..."
    }
}

TEMPLATE_TITLES = {
    "analyst": "Business Analysis Report",
    "pm": "Product Requirements Document",
    "ux": "UX Design Specification",
    "architect": "System Architecture Document",
    "po": "Product Backlog: Epics & User Stories"
}

def migrate_node_yaml(node_id: str, dry_run: bool = False) -> dict[str, Any]:
    """迁移 node.yaml 从 v1 到 v2"""
    node_dir = NODES_DIR / node_id
    node_yaml_path = node_dir / "node.yaml"
    
    with open(node_yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 添加 schema_version
    config["schema_version"] = "2.0"
    
    # 添加 task section
    if "task" not in config:
        config["task"] = TASK_DEFAULTS[node_id]
    
    # 补充 deliverable 字段
    if "deliverable" in config:
        deliverable = config["deliverable"]
        if "template_title" not in deliverable:
            deliverable["template_title"] = TEMPLATE_TITLES[node_id]
        if "output_filename" not in deliverable:
            deliverable["output_filename"] = f"{config['deliverable_type']}.md"
    
    # 添加 runtime section
    if "runtime" not in config:
        config["runtime"] = {
            "timeout": 300,
            "retry": {"max_attempts": 2, "backoff": 1.5}
        }
    
    # 添加 evaluator section（引用）
    if "evaluator" not in config:
        config["evaluator"] = {
            "criteria_file": "evaluator.yaml",
            "threshold": 0.70,
            "max_iterations": 3
        }
    
    if not dry_run:
        with open(node_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, indent=2)
        print(f"[MIGRATED] {node_yaml_path}")
    else:
        print(f"[DRY-RUN] Would migrate {node_yaml_path}")
    
    return config


def migrate_evaluator_yaml(node_id: str, dry_run: bool = False) -> None:
    """迁移 evaluator.yaml：修正 thresholds → threshold"""
    eval_path = NODES_DIR / node_id / "evaluator.yaml"
    
    with open(eval_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    config["schema_version"] = "2.0"
    
    # 修正字段名
    if "thresholds" in config and "threshold" not in config:
        config["threshold"] = config.pop("thresholds")
    
    # 新增 max_iterations
    if "max_iterations" not in config:
        config["max_iterations"] = 3
    
    if not dry_run:
        with open(eval_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, indent=2)
        print(f"[MIGRATED] {eval_path}")


def migrate_all(dry_run: bool = False) -> None:
    """迁移所有节点"""
    for node_id in ["analyst", "pm", "ux", "architect", "po"]:
        print(f"\n=== Migrating {node_id} ===")
        migrate_node_yaml(node_id, dry_run)
        migrate_evaluator_yaml(node_id, dry_run)
```

---

## 8. 风险评估

### 8.1 风险矩阵

| 风险 | 可能性 | 影响度 | 综合等级 | 缓解措施 |
|------|--------|--------|---------|---------|
| `context_builder.py` 的 `node_config.task.get()` 调用在 v1 schema 节点上抛出 `AttributeError` | 高（已存在） | 高（阻断节点执行） | **严重** | 立即在 `context_builder.py` 加防御性判断 `if node_config.task else` |
| `evaluator.yaml` 的 `thresholds`（复数）字段被读取为 `None`（因代码期望 `threshold` 单数） | 中 | 中（评估逻辑静默失败） | **高** | 在 `NodeLoader` 中同时支持两种字段名，优先读取 `threshold` |
| `schema_version` 字段不存在时的向后兼容性破坏 | 低（新字段可选） | 中（解析异常） | **中** | `schema_version` 默认为 "1.0"，使用 `.get("schema_version", "1.0")` |
| persona.json 新增字段（memories, critical_actions）被 IndependentAgent 忽略 | 中（取决于实现） | 低（功能退化，非中断） | **低** | 验证 `IndependentAgent` 中 `persona_context` 的加载逻辑是否包含新字段 |
| `pm.persona.role` 从 "Project Manager" 改为 "Product Manager" 导致已有测试失败 | 高 | 低（测试修复代价小） | **低** | 更新对应测试的断言值 |
| architect 节点 evaluator 阈值提高（0.70→0.75）导致更多 NEEDS_REVISION 循环 | 中 | 中（执行时间增加） | **中** | 配合 `max_iterations: 3` 上限，避免无限循环；监控迭代次数指标 |

### 8.2 回滚策略

```
触发回滚条件：
  1. 超过 20% 的流水线执行因 schema 变更而失败
  2. NodeLoader 解析错误率 > 5%
  3. context_builder 抛出 AttributeError（task 相关）

回滚步骤：
  1. git revert <migration_commit>   # 回滚配置文件修改
  2. git revert <loader_commit>      # 回滚 loader.py 修改
  3. 验证回滚后流水线恢复正常执行
  4. 分析失败原因后重新设计迁移方案
```

### 8.3 监控指标

改造完成后，应监控以下指标以验证效果：

| 指标 | 基线（改造前） | 目标（改造后） |
|------|--------------|--------------|
| `task_name` 为角色名（如 "Analyst"）而非任务名的比例 | 100% | 0% |
| IndependentAgent 中 `role_supplement` 非空的比例 | 0%（字段缺失） | 100% |
| 评估通过率（APPROVED/NEEDS_REVISION 比） | 未测量 | 建立基线 |
| 节点配置诊断完整度分 | 100%（假阳性） | 100%（真实满足） |
| 节点平均执行时间 | 未测量 | 建立基线 |

---

## 附录 A：配置文件路径参考

```
autoBMAD/nodes/
├── analyst/
│   ├── node.yaml          （主配置，v2 后新增 task/runtime/evaluator sections）
│   ├── persona.json       （角色定义，v2 后新增 communication_style/critical_actions/memories）
│   └── evaluator.yaml     （评估标准，v2 后修正 thresholds→threshold）
├── pm/       （同上结构）
├── ux/       （同上结构）
├── architect/ （同上结构）
└── po/        （同上结构）

_bmad/_config/agents/
├── bmm-analyst.customize.yaml      （BMAD Agent 定制，建议填充 DocuSwarm 专属内容）
├── bmm-pm.customize.yaml           （被 pm 和 po 节点共用，建议 po 独立）
├── bmm-ux-designer.customize.yaml
├── bmm-architect.customize.yaml
└── bmm-po.customize.yaml           （新建，为 po 节点建立独立 BMAD Agent）

autoBMAD/nodes/
└── loader.py                       （需更新以支持 v2 schema 字段）

autoBMAD/docuswarm/node_execution/
└── context_builder.py              （需修正 node_config.task.get() 调用方式）
```

## 附录 B：诊断工具输出说明

当前诊断工具（`tools/node_config_completeness_checker.py`）报告的"100% 完整度"是基于旧的 v1 schema 定义，其 `required` 字段列表不包含 `task.*` 字段。完成本报告建议的改造后，诊断工具也需要同步升级（Phase 4 - P4-1），使其 schema 定义与 v2 对齐。

升级后，诊断工具应能检测：
- `task.name` 是否存在且非空
- `task.description` 是否足够详细（字符数 > 50）
- `evaluator.yaml` 是否使用 `threshold`（单数）字段名
- `persona.json` 是否包含 `communication_style` 字段

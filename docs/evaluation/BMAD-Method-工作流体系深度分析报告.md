## BMAD 工作流体系深度分析报告

### 一、文档信息

| 属性 | 值 |
|------|----|
| 版本 | 1.0 |
| 创建日期 | 2026-03-01 |
| 分析对象 | `_bmad` 目录下 BMAD 核心模块与工作流体系 |
| 关联文档 | 《BMAD 开发方法论详细说明》、autoBMAD Epic 自动化工作流文档、质量门控相关文档 |
| 使用场景 | 需要理解 DocuSwarm 项目中 BMAD 工作流如何组织、如何与 autoBMAD 与 TEA 流程协同时 |

---

### 二、执行摘要

- **BMAD 模块化安装状态**：本项目已安装并启用 **core、bmm、bmb、cis、tea** 五大 BMAD 模块，通过 [`_bmad/_config/manifest.yaml`](file:///d:/GITHUB/DocuSwarm/_bmad/_config/manifest.yaml) 统一管理版本与来源。
- **工作流总览**：所有可用工作流集中登记在 [`workflow-manifest.csv`](file:///d:/GITHUB/DocuSwarm/_bmad/_config/workflow-manifest.csv) 中，覆盖从 **产品分析、PRD、架构与故事分解、实现与 QA、测试架构与质量门控、创意设计与叙事** 到 **自定义模块/工作流构建** 的完整链路。
- **执行模型**：BMAD 工作流采用统一的 **step-file 微文件架构**，通过 `steps-c`（Create）、`steps-e`（Edit）、`steps-v`（Validate） 等目录划分模式，强制顺序执行、单步加载和状态跟踪，确保 LLM 执行过程可控、可恢复、可验证。
- **与 DocuSwarm 的关系**：`_bmad` 提供的是 **方法论层面的交互工作流**（在 IDE / Chat 中驱动代理工作），而 `autoBMAD/epic_automation` 则提供 **基于同一方法论的 Python 自动化流水线**；二者在 DocuSwarm 中共同构成从文档 → 工作流 → 代码 → 质量门控的闭环。
- **测试与质量支撑**：`tea` 模块的 Test Architecture Enterprise 工作流（如 `testarch-test-review`、`testarch-trace`）为 DocuSwarm 的测试策略、质量门控和评估报告（`docs/qa/gates`、`docs/evaluation`）提供系统化支撑。

---

### 三、BMAD 模块与 `_bmad` 目录结构总览

#### 3.1 模块安装与来源

根据 [`_bmad/_config/manifest.yaml`](file:///d:/GITHUB/DocuSwarm/_bmad/_config/manifest.yaml)：

- **core 模块**
  - **角色**：BMAD 核心运行时，提供主控代理 **bmad-master**、通用任务（help、index-docs、shard-doc 等）与基础工作流（如 brainstorming、party-mode）。
  - **来源**：built-in，版本 `6.0.1`。
- **bmm 模块**（BMAD Method Module）
  - **角色**：完整 BMAD 方法论工作流集合，负责 **分析（Analysis）→ 规划（Plan）→ 解决方案设计（Solutioning）→ 实施与回顾（Implementation & Retrospective）** 等阶段。
  - **来源**：built-in，版本 `6.0.1`。
- **cis 模块**（Creative Intelligence Suite）
  - **角色**：创意与创新类工作流模块，包含 design-thinking、innovation-strategy、storytelling 等，支持构思、叙事和创新策略。
  - **来源**：外部 npm 包 `bmad-creative-intelligence-suite`，版本 `0.1.6`。
- **bmb 模块**（BMAD Builder）
  - **角色**：**BMAD 内容构建器**，用于创建/编辑/校验自定义的 agents、modules、workflows，自身也遵循 BMAD step-file 架构。
  - **来源**：外部 npm 包 `bmad-builder`，版本 `0.1.6`。
- **tea 模块**（Test Architecture Enterprise）
  - **角色**：测试架构与质量门控工作流集合，聚焦 **ATDD、自动化测试、CI 质量管道、测试框架搭建、NFR 评估、测试设计、测试评审、需求–测试追踪矩阵** 等。
  - **来源**：外部 npm 包 `bmad-method-test-architecture-enterprise`，版本 `1.2.1`。

这些模块在各自目录下均有独立的 `config.yaml`（例如 [`_bmad/bmm/config.yaml`](file:///d:/GITHUB/DocuSwarm/_bmad/bmm/config.yaml)），统一约定：

- **user_name**：你
- **communication_language**：Chinese
- **document_output_language**：English
- **output_folder**：`{project-root}/_bmad-output`

这保证了各模块工作流在运行时采用一致的输出路径与语言策略（中文交互、英文交付物为主）。

#### 3.2 `_bmad` 目录功能分区

- **`_config/`**
  - `manifest.yaml`：模块安装元数据。
  - `agent-manifest.csv`：所有已安装代理清单及其 persona 文件位置。
  - `workflow-manifest.csv`：所有工作流清单（名称、描述、所属模块、入口文件路径）。
  - `task-manifest.csv`：核心任务清单（如 editorial-review、index-docs、shard-doc 等）。
  - `tool-manifest.csv`：工具清单（当前为空，可扩展）。
- **`_memory/`**
  - 侧车记忆（storyteller-sidecar、tech-writer-sidecar 等）及配置，用于长期偏好和知识持久化。
- **`core/`**
  - 提供 `bmad-master` 代理与基础工作流（brainstorming、party-mode 等），作为 BMAD 系统的“总控台”。
- **`bmm/`**
  - 存放 BMAD 方法论的主体工作流（分析、规划、解决方案、实施、文档化、QA 自动化等），并定义核心团队代理（analyst、architect、dev、pm、qa、sm、ux-designer 等）。
- **`bmb/`**
  - 提供 agent/module/workflow 构建工作流与模板，是扩展 `_bmad` 内容的“元工作流”。
- **`cis/`**
  - 创意与叙事类工作流，用于需求澄清、创新构思、故事化表达等。
- **`tea/`**
  - 测试架构 Enterprise（TEA）系列工作流，支撑 DocuSwarm 的质量门控与测试策略。

---

### 四、工作流清单与分层结构

#### 4.1 统一注册：`workflow-manifest.csv`

所有可用工作流均在 [`_bmad/_config/workflow-manifest.csv`](file:///d:/GITHUB/DocuSwarm/_bmad/_config/workflow-manifest.csv) 中注册，结构为：

```text
name,description,module,path
```

典型条目示例：

- **core 模块**
  - **brainstorming** → `_bmad/core/workflows/brainstorming/workflow.md`
  - **party-mode** → `_bmad/core/workflows/party-mode/workflow.md`
- **bmm 模块 – Analysis & Plan**
  - **create-product-brief**：分析阶段创建产品简报。
  - **domain-research / market-research / technical-research**：领域/市场/技术研究工作流。
  - **create-prd / edit-prd / validate-prd**：PRD 创建、编辑与验证。
  - **create-ux-design**：UX 设计规划。
- **bmm 模块 – Solutioning & Implementation**
  - **check-implementation-readiness**：检查 PRD + 架构 + 故事集是否具备实现准备度。
  - **create-architecture**：架构文档创建工作流。
  - **create-epics-and-stories**：从 PRD + 架构派生 epics 与 stories。
  - **create-story / dev-story**：故事创建与开发执行。
  - **code-review**：对某个故事进行“对抗式高级代码审查”。
  - **correct-course / sprint-planning / sprint-status / retrospective**：实施过程中的纠偏、规划、进度汇总与回顾。
  - **quick-dev / quick-spec**：Quick Flow 快速开发/规格工作流。
  - **document-project / generate-project-context / qa-automate**：项目文档化、project-context 生成、测试快速自动化工作流。
- **bmb 模块 – 构建工具型工作流**
  - **create-agent / edit-agent / validate-agent**：BMAD 代理创建/编辑/验证。
  - **create-module-brief / create-module / edit-module / validate-module**：BMAD 模块创建与治理。
  - **create-workflow / edit-workflow / rework-workflow / validate-workflow / validate-max-parallel-workflow**：BMAD 工作流创建、编辑、迁移到 v6 与并行校验。
- **cis 模块 – 创意工作流**
  - **design-thinking / innovation-strategy / problem-solving / storytelling**：围绕设计思维、创新策略、系统化问题求解和故事创作的工作流。
- **tea 模块 – 测试架构工作流（testarch）**
  - **testarch-atdd / testarch-automate / testarch-ci / testarch-framework / testarch-nfr**：ATDD、自动化扩展、CI 质量管道、测试框架搭建与 NFR 评估。
  - **teach-me-testing**：多会话测试学习工作流。
  - **testarch-test-design / testarch-test-review / testarch-trace**：测试设计、测试评审和需求–测试追踪矩阵与质量门控决策。

通过该清单，外层工具（如 `bmad-master` 或外部脚本）可以在不知道具体路径的情况下，按 `name` 精确定位和调用工作流。

#### 4.2 按模块与开发阶段的分层

从 BMAD 方法论视角，结合 [`claude_docs/bmad_methodology.md`](file:///d:/GITHUB/DocuSwarm/claude_docs/bmad_methodology.md)，可以将 `_bmad` 中的工作流按“阶段 × 模块”划分为：

- **分析阶段（Analysis） – bmm + cis**
  - 通过 **create-product-brief** 和 **各种 research 工作流** 收集业务、市场与技术信息。
  - 可选使用 **cis 模块**的 design-thinking / problem-solving 进行创意与问题澄清。
- **规划阶段（Plan） – bmm**
  - 使用 **create-prd / create-ux-design** 产出完整 PRD 与 UX 方案。
  - 配合 **validate-prd** 等工作流进行规范性验证。
- **解决方案设计与准备度验证（Solutioning） – bmm**
  - **create-architecture** 生成架构文档。
  - **create-epics-and-stories** 将需求拆解为 epics/stories。
  - **check-implementation-readiness** 检查“PRD + 架构 + 故事集合”是否达标。
- **实施与 QA（Implementation & QA） – bmm + tea**
  - **create-story / dev-story** 驱动实现过程（结合 IDE / Chat 中的 dev 代理）。
  - **code-review / qa-automate** 支撑代码审查与快速测试生成。
  - **testarch-* 工作流** 提供测试设计、执行、评审与质量门控。
- **文档化与项目认知（Documentation & Project Understanding） – bmm + core**
  - **document-project / generate-project-context** 针对 brownfield 代码库进行结构化文档化。
  - **index-docs / shard-doc** 等核心任务用于索引与分片已有文档。
- **扩展与元工作流（Meta） – bmb**
  - 使用 **create-agent / create-module / create-workflow** 等工作流扩展 `_bmad` 自身能力。

---

### 五、BMAD step-file 架构与执行规则

#### 5.1 工作流模板与统一结构

[`_bmad/bmb/workflows/workflow/templates/workflow-template.md`](file:///d:/GITHUB/DocuSwarm/_bmad/bmb/workflows/workflow/templates/workflow-template.md) 给出了 BMAD 工作流的标准结构：

- 顶部 YAML frontmatter：
  - `name`：工作流展示名。
  - `description`：简要描述目标。
  - `web_bundle`：是否打包到 web bundle。
- 正文的核心部分：
  - **Goal**：用一句话描述工作流最终目标。
  - **Your Role**：约定代理在该工作流中的额外角色定位。
  - **WORKFLOW ARCHITECTURE**：详细说明 step-file 架构与执行规则。

#### 5.2 step-file 架构核心原则

在诸如 [`workflow-create-agent.md`](file:///d:/GITHUB/DocuSwarm/_bmad/bmb/workflows/agent/workflow-create-agent.md)、[`workflow-edit-agent.md`](file:///d:/GITHUB/DocuSwarm/_bmad/bmb/workflows/agent/workflow-edit-agent.md) 等文件中，BMAD 反复强调相同的架构原则：

- **Micro-file Design（微文件设计）**：
  - 每一步是一个独立的 Markdown 文件，位于 `steps-c/`、`steps-e/`、`steps-v/` 等目录。
  - 便于审查、版本控制和局部重构。
- **Just-In-Time Loading（即时加载）**：
  - **任何时候只加载当前 step 文件**，禁止预读后续步骤。
  - 避免 LLM 一次性“看完全部流程”导致跳步或信息泄露。
- **Sequential Enforcement（顺序强制）**：
  - 按照文件中的编号和菜单顺序执行步骤。
  - 任何跳过或“优化路径”都是违背工作流规范的。
- **State Tracking（状态跟踪）**：
  - 通过输出文档 frontmatter 中的 `stepsCompleted` 数组，记录已完成步骤。
  - 某些工作流还使用专门的 plan 文件（如 `workflow-plan.md`）记录整体结构和完成情况。
- **Append-Only Building（追加式构建）**：
  - 工作流产出的文档应以“追加”方式构建，而不是反复重写整个文件。
  - 便于回溯每步贡献的内容与决策。

#### 5.3 执行规则与菜单交互

典型规则（节选自 create/edit-agent 工作流）：

- **READ COMPLETELY**：在采取任何行动前，必须完整阅读当前 step 文件。
- **FOLLOW SEQUENCE**：严格按编号依次执行步骤。
- **WAIT FOR INPUT**：遇到菜单时，必须暂停等待用户选择，不得自作主张。
- **CHECK CONTINUATION**：仅在用户明确选择“继续/下一步”选项后再加载下一 step。
- **SAVE STATE**：在切换 step 前必须更新状态（如 `stepsCompleted` 或计划文件）。
- **NEVER PRE-LOAD**：禁止提前加载后续 step 文件，也禁止一次性加载多个 step。

这些规则保证了 BMAD 工作流在与 LLM 交互时的 **可预测性与可追踪性**，特别适合 DocuSwarm 这类多代理、长流程项目。

#### 5.4 多模式工作流：Create / Edit / Validate

在诸如 `bmb` 与 `bmm` 模块中，常见的模式是：

- `steps-c/`：**Create 模式** – 从零创建文档/模块/工作流/代理。
- `steps-e/`：**Edit 模式** – 针对已有产物进行结构化修改。
- `steps-v/`：**Validate 模式** – 针对已有产物进行标准化校验，输出问题清单与修复建议。

`tea` 模块的 testarch 工作流在逻辑上也遵循类似思想：

- create/assessment 步骤：拉取上下文、发现现状。
- evaluation/validate 步骤：评估质量、生成评分/门控结论。
- apply/edit 步骤：根据评审结果调整测试或质量配置。

---

### 六、典型端到端开发流程中的 `_bmad` 工作流链路

本节从“一个新特性/史诗”的角度，串联 `_bmad` 工作流的典型使用路径。

#### 6.1 需求与产品视角 – Analysis & Plan（bmm + cis）

1. **需求与机会识别**
   - 使用 `bmm` 模块的 **create-product-brief** 工作流，生成产品简报，明确目标用户、核心价值、业务场景。
   - 若需求模糊或创新性强，可通过 `cis` 模块的 **design-thinking / innovation-strategy / problem-solving / storytelling** 工作流进行发散与收敛，形成更具故事性的产品视角。

2. **研究支撑**
   - 调用 **domain-research / market-research / technical-research**，分别形成行业、市场与技术维度的研究报告，为后续 PRD 与架构决策提供事实基础。

3. **PRD 与 UX**
   - 使用 **create-prd** 工作流创建完整 PRD，结合 PRD 工作流中的菜单与 step-file 指导，逐步补齐背景、需求、用户故事与验收标准。
   - 若涉及用户界面/体验，可通过 **create-ux-design** 工作流制定 UX 方案。

4. **校验与对齐**
   - 借助 **validate-prd** 和 **check-implementation-readiness** 等工作流，对 PRD、架构草案、早期故事集进行一致性与完整性校验。

#### 6.2 架构与故事分解 – Solutioning（bmm）

1. **架构创建**
   - 使用 **create-architecture** 工作流，结合 PRD 与研究材料，生成完整架构文档（包含系统组件、边界、集成点、质量属性等）。

2. **从 PRD 到 Epics & Stories**
   - 调用 **create-epics-and-stories**，将 PRD 中的功能需求分解为 epics 与 stories，并补充验收标准与技术约束。

3. **实施准备度验证**
   - 在进入真正的实现周期前，通过 **check-implementation-readiness** 检查：
     - PRD 是否完整且无重大空缺；
     - 架构是否覆盖关键场景与约束；
     - epics/stories 是否可执行、可测试；
     - 是否存在明显的风险或依赖项未解决。

#### 6.3 实施与 QA – Implementation（bmm + tea）

1. **故事创建与开发**
   - 使用 **create-story** 为每个要实现的需求生成 story 文件，明确任务拆分与验收标准。
   - 通过 IDE / Chat 中的 `dev` 代理，结合 **dev-story** 工作流执行开发任务。

2. **代码审查与纠偏**
   - 应用 **code-review** 工作流，对某个 story 的代码进行对抗式高级审查，确保：
     - 代码质量、测试覆盖、架构符合性、安全与性能等多个维度均被检查；
     - 至少发现 3–10 个具体问题，杜绝“看起来不错”式的浅层审查。
   - 若发现较大偏差，可通过 **correct-course** 工作流进行方向纠偏。

3. **测试生成与执行**
   - 通过 **qa-automate** 工作流，为现有功能生成标准化测试用例。
   - 配合 `tea` 模块的 **testarch-atdd / testarch-automate / testarch-ci / testarch-framework / testarch-nfr** 等工作流，建立从 ATDD → 自动化测试 → CI → NFR 评估的完整测试体系。

4. **测试评审与追踪矩阵**
   - 使用 **testarch-test-design** 进行测试设计与规划。
   - 通过 **testarch-test-review** 工作流，对测试质量进行系统评审，生成评分与改进建议。
   - 借助 **testarch-trace**，生成需求–测试追踪矩阵与质量门控决策（PASS / CONCERNS / FAIL / WAIVED），并将结果与 `docs/qa/gates` 中的质量门控报告相呼应。

5. **冲刺管理与回顾**
   - **sprint-planning / sprint-status** 工作流用于生成和维护冲刺状态文件，追踪 story 状态流转（Draft → Approved → InProgress → Review → Done）。
   - **retrospective** 支持在史诗完成后进行系统性回顾，沉淀经验与改进点。

#### 6.4 文档化与项目认知 – Documentation（bmm + core）

- **document-project**：针对 brownfield 项目，通过扫描代码、架构和模式，生成结构化文档，为 AI 辅助开发提供“项目导览图”。
- **generate-project-context**：生成简明的 `project-context.md`，提炼 AI 代理在编码时必须遵守的关键规则与模式，为 DocuSwarm 的 day-to-day 开发提供轻量级入口。
- **index-docs / shard-doc**（core 任务）：用于对 `docs/` 下的文档进行索引与分片，帮助 LLM 更高效地利用已有文档。

---

### 七、TEA 工作流与质量门控体系

`tea` 模块在 `_bmad/tea` 下提供了丰富的测试架构工作流，与项目中 `docs/qa/gates` 以及 `docs/evaluation` 下的质量分析报告形成闭环。

#### 7.1 核心 testarch 工作流

- **testarch-atdd**：在实现前生成失败的验收测试（ATDD），驱动红–绿–重构循环。
- **testarch-automate**：在实现后扩展自动化测试覆盖，或在现有代码库上生成系统化测试集。
- **testarch-ci**：搭建 CI 质量管道，配置测试执行、burn-in 循环与工件收集。
- **testarch-framework**：初始化生产级测试框架（Playwright 或 Cypress），包含 fixtures、helpers、配置等。
- **testarch-nfr**：针对性能、安全、可靠性、可维护性等非功能需求进行评估与验证。
- **teach-me-testing**：通过多 Session 渐进式教学，引导团队成员学习测试方法论。
- **testarch-test-design**：在 Solutioning 或 Implementation 阶段进行系统级或 Epic 级测试规划。
- **testarch-test-review**：对测试质量进行综合评估，生成打分与建议。
- **testarch-trace**：生成需求–测试追踪矩阵，输出覆盖率分析与质量门控结论。

#### 7.2 质量门控与决策状态

结合项目中的《质量门控概述》和《BMAD-Workflow 质量门控》知识文档，TEA 工作流通常输出以下内容：

- **门控状态枚举**：`PASS / CONCERNS / FAIL / WAIVED`。
- **P0 / P1 / P2/P3 维度**：在如 [`trace-template.md`](file:///d:/GITHUB/DocuSwarm/_bmad/tea/workflows/testarch/trace/trace-template.md) 中，对必须通过的 P0 条件（如安全问题、关键 NFR）、强烈推荐的 P1 条件以及信息性 P2/P3 条件进行区分。
- **决策矩阵**：结合测试通过率、覆盖率、质量问题数量、安全缺陷等指标，给出门控决策。

这些输出与：

- `docs/qa/gates/*.yml` 中的质量门控报告；
- `docs/evaluation/*.md` 中的评估与回顾文档；

共同构成 DocuSwarm 的质量管理与可视化体系。

---

### 八、BMAD 工作流与 autoBMAD Epic 自动化的关系

DocuSwarm 中存在两条互补的“BMAD 工作流路径”：

1. **交互式 BMAD 工作流 – `_bmad` 目录**
   - 通过 `_bmad` 内的 Markdown 工作流文件，在 IDE / Chat 中由代理逐步执行。
   - 优点：高度交互、可灵活选择路径、适合探索与复杂决策。
   - 典型场景：一次性的架构设计讨论、specific story 的代码审查、针对某个问题的深度分析等。

2. **自动化 Epic 工作流 – `autoBMAD/epic_automation`**
   - 通过 `epic_driver.py` 等脚本，将一个 Epic 文件（`docs/epics/*.md`）作为输入，驱动完整的 5 阶段开发与质量门控流水线。
   - 优点：高度自动化、可重复执行、适合大批量故事与持续质量管理。

二者共享的核心：

- **同一套 BMAD 方法论与开发轨道**（Quick Flow / BMAD Method / Enterprise Method）。
- **相同的质量门控理念**：基于 Ruff、BasedPyright、Pytest、TEA 工作流等工具链。
- **统一的状态与文档输出约定**：如 story 状态流转、门控状态、评估报告等。

对 DocuSwarm 来说，可以采用如下实践策略：

- 使用 `_bmad` 工作流 **设计与调整方法论层级的流程**（如如何拆分故事、如何配置质量门控）。
- 使用 `autoBMAD` Epic 流水线 **批量执行** 已确认的图谱（即基于 `_bmad` 设计好的开发/质量流程）。

---

### 九、在 DocuSwarm 中使用 `_bmad` 工作流的推荐实践

#### 9.1 新特性/史诗从零开始

1. **用 bmm 工作流完成端到端规划**
   - create-product-brief → 各类 research → create-prd → create-ux-design → create-architecture → create-epics-and-stories → check-implementation-readiness。
2. **用 tea 工作流提前设计测试架构**
   - 在 Solutioning 阶段尽早运行 testarch-test-design / testarch-nfr，确保可测试性与质量属性被纳入设计。
3. **进入实施阶段时，切换到 autoBMAD 或 dev-story 工作流**
   - 简单场景可使用 quick-dev / quick-spec；
   - 复杂场景可结合 autoBMAD Epic 流水线与 testarch-* 工作流。

#### 9.2 Brownfield / 现有项目接管

1. 使用 **document-project** 工作流扫描现有代码与文档，生成项目概览。
2. 通过 **generate-project-context** 生成轻量级 `project-context.md`，供日常 AI 开发会话使用。
3. 利用 **testarch-automate / testarch-test-review / testarch-trace** 分析当前测试与质量状况，并在 `docs/qa/gates` 与 `docs/evaluation` 中生成对齐的质量报告。

#### 9.3 扩展 `_bmad` 本身

- 使用 `bmb` 模块工作流：
  - **create-agent**：为 DocuSwarm 项目创建专用专家代理（例如针对某个子系统）。
  - **create-module**：打包一组代理 + 工作流为独立 BMAD 模块，便于复用与分享。
  - **create-workflow / validate-workflow / validate-max-parallel-workflow**：按 BMAD 规范创建新工作流，并对其结构与并行执行能力进行验证。

---

### 十、结论与后续演进建议

- **方法论与实现已高度完备**：当前 `_bmad` 安装的五大模块覆盖了从产品构思、需求与架构设计、实现与测试、质量门控到文档化与元工作流构建的完整闭环，配合 autoBMAD 形成端到端自动化能力。
- **质量与测试能力特别突出**：TEA 工作流与 `docs/qa/gates`、`docs/evaluation` 中的分析报告共同构建了一套严密的质量门控体系，适合持续改进与回归分析。
- **建议的演进方向**：
  - 为 DocuSwarm 特有的子系统（如 orchestrator、pipeline、RAG 等）创建定制化 BMAD 工作流和代理；
  - 将关键 `_bmad` 工作流（如 check-implementation-readiness、testarch-trace）纳入日常提交前/发布前的标准检查清单；
  - 结合项目实际经验，在 `docs/evaluation` 中补充“BMAD 工作流使用回顾与改进”类文档，形成方法论级的持续迭代闭环。

# Spec Automation Workflow - Brownfield Enhancement PRD

**文档版本**: v1.0
**创建日期**: 2026-01-09
**作者**: John (Product Manager)
**状态**: Draft

---

## 1. 项目分析与上下文

### 1.1 分析来源

- IDE-based fresh analysis
- 参考实现: `autoBMAD/epic_automation`

### 1.2 现有项目状态

`autoBMAD/epic_automation` 是一个多代理工作流编排系统，用于 AI 驱动的敏捷开发：

- **DevAgent**: 处理开发任务，执行 TDD
- **QAAgent**: 执行质量审查和验证
- **SMAgent**: 创建和管理故事文档
- **EpicDriver**: 主编排器，协调整个工作流
- **QualityAgents**: 自动化代码质量检查（Ruff、BasedPyright、Pytest）

**关键依赖**: 当前系统严重依赖 `.bmad-core` 目录的任务指导文件。

### 1.3 可用文档

| 文档类型 | 状态 |
|---------|------|
| Tech Stack Documentation | ✓ Python, Claude SDK, SQLite |
| Source Tree/Architecture | ✓ 完整的模块结构 |
| Coding Standards | ✓ PEP 8, Type Hints |
| API Documentation | ✓ 模块级文档字符串 |
| README/SETUP | ✓ 完整 |

---

## 2. 增强范围定义

### 2.1 增强类型

- [x] New Feature Addition
- [ ] Major Feature Modification
- [ ] Integration with New Systems
- [ ] Performance/Scalability Improvements
- [ ] UI/UX Overhaul
- [ ] Technology Stack Upgrade
- [ ] Bug Fix and Stability Improvements

### 2.2 增强描述

创建全新的 `spec_automation` 工作流模块，用于处理非 Epic/Story 格式的规划文档（如 Sprint Change Proposal、Plan 文档、Spec 文档）。该模块不依赖 `.bmad-core`，采用独立的提示词系统，以文档为中心进行开发和审查。

### 2.3 影响评估

- [x] Minimal Impact (isolated additions)
- [ ] Moderate Impact (some existing code changes)
- [ ] Significant Impact (substantial existing code changes)
- [ ] Major Impact (architectural changes required)

**说明**: 这是一个独立的新模块，不修改现有 `epic_automation` 代码。

---

## 3. 目标与背景

### 3.1 目标

- 支持非 BMAD 格式的规划文档驱动开发
- 提供独立于 `.bmad-core` 的工作流系统
- 实现以文档为中心的 QA 审查机制
- 保持与现有质量门禁工具的兼容性
- 简化工作流，移除不必要的文档创建步骤

### 3.2 背景

现有的 `epic_automation` 模块专门针对 BMAD 方法论创建的 Epic/Story 文档。然而，许多开发场景使用不同格式的规划文档：

- **Sprint Change Proposal**: 详细的变更提案文档
- **Functional Spec**: 功能规格说明书
- **Technical Plan**: 技术实现计划

这些文档包含完整的需求、验收标准和实施步骤，但格式与 BMAD Story 不同。`spec_automation` 模块将填补这一空白。

---

## 4. 需求

### 4.1 功能需求

| ID | 需求描述 |
|----|---------|
| FR1 | 系统应能解析多种格式的规划文档（Markdown），提取需求、验收标准和实施步骤 |
| FR2 | SpecDevAgent 应使用 TDD 方法进行开发，确保测试覆盖率，最终通过全部测试 |
| FR3 | SpecQAAgent 应以文档为中心进行审查，验证源代码是否符合文档提及的全部需求 |
| FR4 | SpecDriver 应协调 Dev-QA 循环，直到所有验收标准满足 |
| FR5 | 系统应集成现有的 Ruff、BasedPyright、Pytest 质量门禁 |
| FR6 | 系统应支持文档状态追踪（Draft → In Progress → Review → Done） |
| FR7 | 系统应生成执行报告，记录开发和审查过程 |

### 4.2 非功能需求

| ID | 需求描述 |
|----|---------|
| NFR1 | 模块应完全独立，不依赖 `.bmad-core` 目录 |
| NFR2 | 应复用 `epic_automation` 的基础设施（SDK wrapper、session manager、state manager） |
| NFR3 | 代码应符合项目现有编码标准（PEP 8、Type Hints） |
| NFR4 | 应提供完整的日志记录，便于调试和监控 |
| NFR5 | 应支持 Windows 路径格式 |

### 4.3 兼容性需求

| ID | 需求描述 |
|----|---------|
| CR1 | 应与现有 `quality_agents.py` 模块兼容 |
| CR2 | 应使用相同的 Claude Agent SDK 集成模式 |
| CR3 | 应支持相同的状态管理机制 |
| CR4 | 应与现有日志系统集成 |

---

## 5. 技术约束与集成需求

### 5.1 现有技术栈

| 类别 | 技术 |
|------|------|
| **Languages** | Python 3.10+ |
| **Frameworks** | Claude Agent SDK, asyncio |
| **Database** | SQLite (状态管理) |
| **Tools** | Ruff, BasedPyright, Pytest |
| **External Dependencies** | anthropic, claude-agent-sdk |

### 5.2 集成方法

**SDK 集成策略**: 复用 `SafeClaudeSDK` 和 `SDKSessionManager`

**测试集成策略**: 复用 `quality_agents.py` 中的 `RuffAgent`、`BasedpyrightAgent`、`PytestAgent`

**日志集成策略**: 复用 `log_manager.py`

### 5.3 代码组织

**文件结构**:
```
autoBMAD/spec_automation/
├── __init__.py           # 包初始化
├── spec_driver.py        # 主编排器
├── spec_dev_agent.py     # 开发代理（TDD 聚焦）
├── spec_qa_agent.py      # QA 代理（文档中心审查）
├── doc_parser.py         # 文档解析器
├── prompts.py            # 独立提示词定义
└── README.md             # 模块文档
```

**命名规范**: 使用 `spec_` 前缀区分于 `epic_automation`

**编码标准**: PEP 8, Type Hints, Google-style docstrings

---

## 6. 风险评估与缓解

### 6.1 技术风险

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| 文档格式多样性导致解析困难 | 中 | 中 | 提供灵活的解析器，支持自定义规则 |
| Claude SDK 调用失败 | 低 | 高 | 复用已验证的 SafeClaudeSDK wrapper |
| 提示词效果不佳 | 中 | 中 | 迭代优化提示词，收集反馈 |

### 6.2 集成风险

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| 与质量门禁集成问题 | 低 | 中 | 直接复用现有模块，最小修改 |
| 状态管理冲突 | 低 | 中 | 使用独立的数据库表/文件 |

---

## 7. Epic 与 Story 结构

### 7.1 Epic 方法

**Epic 结构决策**: 单一 Epic，包含 5 个顺序故事

**理由**: 这是一个聚焦的新模块开发，各组件有明确的依赖关系，适合单一 Epic 管理。

---

## Epic 1: Spec Automation Workflow

**Epic Goal**: 创建独立的 spec_automation 工作流模块，支持非 BMAD 格式文档的开发自动化

**Integration Requirements**: 复用 epic_automation 的基础设施，与质量门禁工具集成

### Story 1.1: 创建模块基础结构和文档解析器

**As a** 开发者,
**I want** 一个能解析多种规划文档格式的解析器,
**so that** 系统能从不同格式的文档中提取需求和验收标准。

**Acceptance Criteria**:
1. 创建 `autoBMAD/spec_automation/` 目录结构
2. 实现 `doc_parser.py`，支持提取：标题、需求列表、验收标准、实施步骤
3. 支持 Markdown 格式的规划文档
4. 提供清晰的解析结果数据结构

**Integration Verification**:
- IV1: 模块可独立导入，无 `.bmad-core` 依赖
- IV2: 解析器能处理 `docs/examples/` 中的示例文档
- IV3: 单元测试覆盖率 > 80%

---

### Story 1.2: 实现 SpecDevAgent（TDD 聚焦）

**As a** 开发者,
**I want** 一个以 TDD 为核心的开发代理,
**so that** 代码开发遵循测试驱动方法，确保质量。

**Acceptance Criteria**:
1. 创建 `spec_dev_agent.py`，继承 SDK 执行能力
2. 提示词强调：先写测试、确保覆盖率、最终通过全部测试
3. 支持从解析的文档中获取开发任务
4. 实现状态更新机制

**SDK Prompt 核心要点**:
```
You are a TDD-focused developer. Your workflow:
1. Read the specification document carefully
2. Write comprehensive tests FIRST based on requirements
3. Implement code to pass all tests
4. Ensure test coverage meets requirements
5. All tests must pass before completion
```

**Integration Verification**:
- IV1: 代理能独立执行，使用 SafeClaudeSDK
- IV2: 开发过程产生测试文件
- IV3: 测试通过后才标记完成

---

### Story 1.3: 实现 SpecQAAgent（文档中心审查）

**As a** QA 工程师,
**I want** 一个以文档为中心的审查代理,
**so that** 能验证代码是否符合文档的全部需求。

**Acceptance Criteria**:
1. 创建 `spec_qa_agent.py`，实现文档中心审查
2. 提示词强调：对照文档逐项验证、检查门禁和验收标准
3. 生成详细的审查报告
4. 返回明确的 PASS/FAIL/CONCERNS 状态

**SDK Prompt 核心要点**:
```
You are a document-centric QA reviewer. Your workflow:
1. Read the specification document thoroughly
2. Extract ALL requirements, gates, and acceptance criteria
3. Verify source code implements EACH requirement
4. Check test coverage for each acceptance criterion
5. Report any missing implementations or discrepancies
```

**Integration Verification**:
- IV1: 审查结果与文档需求一一对应
- IV2: 能识别未实现的需求
- IV3: 生成可追溯的审查报告

---

### Story 1.4: 实现 SpecDriver 编排器

**As a** 自动化工程师,
**I want** 一个工作流编排器,
**so that** Dev-QA 循环能自动运行直到满足所有验收标准。

**Acceptance Criteria**:
1. 创建 `spec_driver.py`，实现主编排逻辑
2. 支持：文档解析 → Dev 开发 → QA 审查 → 质量门禁
3. 实现 Dev-QA 循环，直到 QA 通过
4. 集成 Ruff、BasedPyright、Pytest 质量门禁
5. 生成执行摘要报告

**Integration Verification**:
- IV1: 能端到端执行完整工作流
- IV2: 质量门禁正确集成
- IV3: 循环控制防止无限执行

---

### Story 1.5: 集成测试与文档

**As a** 用户,
**I want** 完整的文档和测试,
**so that** 我能正确使用 spec_automation 模块。

**Acceptance Criteria**:
1. 创建 `README.md`，包含使用说明和示例
2. 编写集成测试，覆盖主要工作流
3. 提供示例规划文档和预期输出
4. 所有测试通过，覆盖率 > 80%

**Integration Verification**:
- IV1: 文档清晰可用
- IV2: 示例可运行
- IV3: 测试覆盖关键路径

---

## 8. 变更日志

| 变更 | 日期 | 版本 | 描述 | 作者 |
|------|------|------|------|------|
| 初始创建 | 2026-01-09 | 1.0 | PRD 初稿 | John (PM) |

---

## 9. 审批

- [ ] Product Owner 审批
- [ ] Tech Lead 审批
- [ ] QA Lead 审批

---

**下一步**: 审批后，可使用 `spec_automation` 工作流开始 Story 1.1 的开发。

# Claude Code 指导文档

**项目名称**: DocuSwarm Multi-Agent Orchestration System
**版本**: 3.1
**最后更新**: 2026-04-05

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [快速导航](#2-快速导航)
3. [核心开发原则](#3-核心开发原则)
4. [AI助手工作流程](#4-ai助手工作流程)
5. [开发工作流](#5-开发工作流)
6. [常用命令](#6-常用命令)
7. [质量保证](#7-质量保证)
8. [更新记录](#8-更新记录)

---

## 1. 项目概述

### 1.1 项目性质

DocuSwarm是一个**多代理文档编排系统**,基于BMAD方法论,集成了:

- **LangGraph** - 多代理工作流的状态机框架
- **Claude Agent SDK** - Anthropic 官方 SDK
- **Claude 3.5/4 Sonnet** - 大上下文窗口LLM(200K tokens)
- **BMAD (Breakthrough Method of Agile AI-driven Development)** - AI驱动的敏捷开发方法论
- **Dual-Agent Pattern** - 双代理模式(Independent + Evaluator)
- **Context Isolation** - 三层上下文隔离机制
- **Sequential Pipeline** - 5个BMAD阶段的顺序执行

### 1.2 核心理念

本项目采用 **"Occam's Razor"** 原则:

- **简单优先**: 使用LangGraph而非自定义NodeExecutor(节省8-12周)
- **双代理模式**: Independent Agent + Evaluator(比三代理模式简化33%)
- **顺序执行**: MVP使用顺序流程,DAG并行延迟到Phase 2
- **单一LLM**: 仅使用Claude Sonnet,无需多provider抽象
- **无RAG系统**: 256K上下文窗口足够,移除向量数据库复杂度

### 1.3 架构演进

当前系统已完成核心重构，详见 [TDD重构方案](docs/solution/README.md):

| 阶段 | 内容 | 状态 |
|------|------|------|
| **Phase 1 (P0)** | CheckpointManager + ContextValidator 提取 | ✅ 已完成 |
| **Phase 2 (P1)** | SDK统一异常处理 + 消息格式切换 | ✅ 已完成 |
| **Phase 3 (P2)** | 质量保障增强 + 测试覆盖提升 | 🔄 进行中 |

**关键TDD方案**:
- [TDD-01](docs/solution/TDD-01-CheckpointManager-Refactor.md) - CheckpointManager提取 (DRY修复)
- [TDD-02](docs/solution/TDD-02-ContextValidator-Refactor.md) - ContextValidator提取 (职责拆分)
- [TDD-03](docs/solution/TDD-03-ToolResultExtractor-Refactor.md) - 纯工具输出模式 (12-Factor对齐)
- [TDD-04](docs/solution/TDD-04-ContextResolver-Refactor.md) - @路径注入系统
- [TDD-05](docs/solution/TDD-05-SDKWrapper-Refactor.md) - SDK替换 (kimi→claude)

### 1.3 项目依赖

核心技术栈:
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - 状态机和工作流编排
- **[claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk)** - Claude Agent SDK（通过 Kimi Code API）
- **[Kimi K2.5](https://platform.moonshot.cn/)** - 主要LLM提供商（256K上下文窗口）
- **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** - 方法论来源
- **SQLite with WAL** - 状态持久化
- **Python 3.12+** - 实现语言

---

## 2. 快速导航

### 2.1 详细文档位置

📖 **完整文档位于 `claude_docs/` 目录**：

| 文档 | 描述 | 何时使用 |
|------|------|----------|
| **[core_principles.md](claude_docs/core_principles.md)** | 四大开发原则详解（DRY、KISS、YAGNI、奥卡姆剃刀） | 需要理解核心原则时 |
| **[bmad_methodology.md](claude_docs/bmad_methodology.md)** | BMAD开发方法论完整说明 | 团队协作、敏捷开发时 |
| **[ai_workflow.md](claude_docs/ai_workflow.md)** | AI助手三阶段工作流程 | 任何开发任务的开始 |
| **[development_rules.md](claude_docs/development_rules.md)** | 编码规范、代码风格 | 编写代码时 |
| **[testing_guide.md](claude_docs/testing_guide.md)** | 测试规范和实践 | 编写和运行测试时 |
| **[quality_assurance.md](claude_docs/quality_assurance.md)** | 质量保证流程和工具 | QA审查、质量门控 |
| **[technical_specs.md](claude_docs/technical_specs.md)** | 技术规范和配置 | 技术决策、配置管理 |
| **[workflow_tools.md](claude_docs/workflow_tools.md)** | autoBMAD工作流详解 | 自动化任务时 |
| **[quick_reference.md](claude_docs/quick_reference.md)** | 常用命令速查 | 快速查找命令时 |
| **[project_tree.md](claude_docs/project_tree.md)** | 项目结构说明 | 了解项目布局时 |
| **[venv.md](claude_docs/venv.md)** | 虚拟环境管理 | **运行任何py程序时** |

### 2.2 重构与架构文档

📋 **重构方案位于 `docs-test/solution/` 目录**：

| 文档 | 描述 | 何时使用 |
|------|------|----------|
| **[solution/README.md](docs-test/solution/README.md)** | TDD重构方案总览和实施路线图 | 规划重构工作时 |
| **[TDD-SDK-Migration](docs-test/solution/TDD-SDK-Migration-2026-03-25.md)** | SDK迁移方案 | kimi→claude迁移 |

📊 **研究文档位于 `docs-test/research/` 目录**：

| 文档 | 描述 | 何时使用 |
|------|------|----------|
| **[Context Refactor Overview](docs-test/research/2026-03-13-docuswarm-context-refactor-overview.md)** | 上下文重构概览 | 理解重构背景时 |
| **[Dependency Drift](docs-test/research/dependency-drift-2026-03-25/README.md)** | 依赖漂移分析 | 了解SDK迁移时 |

🏗️ **架构文档位于 `docs-test/architecture/` 目录**：

| 文档 | 描述 | 何时使用 |
|------|------|----------|
| **[Project Structure](docs-test/architecture/project-structure.md)** | 项目结构规范 | 理解项目布局时 |
| **[Tech Stack](docs-test/architecture/tech-stack.md)** | 技术栈规范 | 理解技术选型时 |
| **[Pipeline Architecture](docs-test/architecture/03_PIPELINE_ARCHITECTURE.md)** | 管道执行架构 | 理解节点执行时 |

### 2.3 核心目录结构

```
project/
├── autoBMAD/                 # 主源代码
│   ├── docuswarm/            # DocuSwarm系统 ⭐
│   │   ├── agents/           # Agent实现
│   │   ├── cli/              # CLI命令
│   │   ├── context/          # 上下文管理
│   │   ├── llm/              # LLM集成
│   │   ├── node_execution/   # 节点执行
│   │   ├── nodes/            # 节点定义
│   │   ├── pipeline/         # 管道编排
│   │   ├── prompts/          # 提示模板
│   │   ├── storage/          # 存储层
│   │   ├── tools/            # 工具系统
│   │   ├── utils/            # 工具函数
│   │   ├── README.md         # DocuSwarm文档
│   │   └── CONFIGURATION.md  # 配置说明
│   └── epic_automation/      # Epic自动化系统
├── nodes/                    # 节点配置（BMAD personas）
├── tests/                    # 测试代码
├── docs/                     # 示例文档
│   └── bubble-sort/          # Bubble Sort测试示例
├── docs-test/                # 测试与架构文档 ⭐
│   ├── architecture/         # 架构文档
│   ├── research/             # 研究报告
│   └── solution/             # TDD方案
├── claude_docs/              # 开发规范文档 ⭐
├── pyproject.toml            # 项目配置
└── README.md                 # 项目概览
```

---

## 3. 核心开发原则

### 3.1 四大黄金法则

#### **DRY - Don't Repeat Yourself (不要重复你自己)**
- **目标**: 消除知识或逻辑在系统中的重复
- **实践**: 重复逻辑提取为函数、配置集中化

#### **KISS - Keep It Simple, Stupid (保持简单和直接)**
- **目标**: 设计尽可能简单的解决方案
- **实践**: 单一职责、清晰命名、提前返回

#### **YAGNI - You Aren't Gonna Need It (你不会需要它)**
- **目标**: 只实现当前明确需要的功能
- **实践**: 基于需求开发、拒绝猜测性抽象

#### **奥卡姆剃刀原则 (如无必要,勿增实体)**
- **目标**: 在多个解决方案中，选择假设最少、最简单的那个
- **实践**: 优先选择简单方案、减少不必要抽象层

### 3.2 原则关系

- **奥卡姆剃刀**是哲学基础
- **KISS**是奥卡姆剃刀在软件设计中的具体体现
- **YAGNI**是从时间维度应用奥卡姆剃刀
- **DRY**通过消除重复来减少不必要的实体

**详细说明**: [core_principles.md](claude_docs/core_principles.md)

---

## 4. AI助手工作流程

### 4.1 三阶段工作流

#### **阶段一：分析问题** `【分析问题】`

**必须做的事**:
- 深入理解需求本质
- 搜索所有相关代码
- 识别问题根因
- 发现并指出重复代码

**阶段转换**: 本阶段结束时要向用户提问

#### **阶段二：制定方案** `【制定方案】`

**必须做的事**:
- 列出变更（新增、修改、删除）的文件
- 消除重复逻辑：通过复用或抽象来消除重复代码
- 确保修改后的代码符合DRY原则和良好的架构设计

#### **阶段三：执行方案** `【执行方案】`

**必须做的事**:
- 严格按照选定方案实现
- 修改后运行类型检查

**详细说明**: [ai_workflow.md](claude_docs/ai_workflow.md)

## 5. 开发工作流

### 5.1 BMAD开发方法论

#### 开发轨道选择

```
Quick Flow ──────→ 快速实施（技术规范）
     ↓
BMad Method ─────→ 完整规划（PRD + 架构 + UX）
     ↓
Enterprise Method → 扩展规划（安全 + DevOps + 测试）
```

#### 四阶段开发周期 (BMM)

1. **Phase 1: Analysis** (分析) - 可选
2. **Phase 2: Planning** (规划) - 必需
3. **Phase 3: Solutioning** (解决方案) - 依赖轨道
4. **Phase 4: Implementation** (实施) - 必需

#### 核心代理团队

| 代理 | 角色 | 关键命令 |
|------|------|----------|
| `sm` | 敏捷大师 | `@sm *create` |
| `dev` | 开发者 | `@dev` |
| `qa` | QA专家 | `@qa *review` |
| `po` | 产品负责人 | `@po` |
| `architect` | 解决方案架构师 | `/architect create-doc architecture` |

**详细说明**: [bmad_methodology.md](claude_docs/bmad_methodology.md)

### 5.2 autoBMAD Epic自动化工作流

#### 核心工作流系统

**autoBMAD Epic Automation** - 完整的5阶段BMAD开发自动化
- SM-Dev-QA循环
- 质量门控（Basedpyright + Ruff）
- 测试自动化（Pytest）
- Claude Agent SDK集成
- 状态管理与持久化

**详细说明**: [workflow_tools.md](claude_docs/workflow_tools.md)

### 5.3 Claude Code Skills集成

autoBMAD系统可以作为Claude Code的Skill安装和使用：

#### 安装Skill

```bash
# Windows PowerShell
.\autoBMAD\Skill\install_autoBMAD_skill.ps1

# Linux/macOS
./autoBMAD/Skill/install_autoBMAD_skill.sh
```

#### Skill文档

- **[SKILL.md](autoBMAD/Skill/SKILL.md)** - 完整的Skill参考和使用指南
- **[SKILL_INSTALLATION_GUIDE.md](autoBMAD/Skill/SKILL_INSTALLATION_GUIDE.md)** - 详细安装说明

#### 使用Skill

在Claude Code中直接调用autoBMAD工作流：

```
请使用autoBMAD工作流处理epic文件 docs/epics/my-epic.md
```

## 6. 常用命令

### 6.1 开发环境

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m autoBMAD.docuswarm --help
```

### 6.2 测试

```bash
# 运行测试
pytest -v --tb=short

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# GUI测试
pytest tests/gui/ -v
```

### 6.3 代码质量

```bash
# 类型检查
basedpyright docuswarm/

# 代码风格
ruff check --fix docuswarm/
```

### 6.4 构建

```bash
# Nuitka构建
python build/build.py

# Pre-commit检查
pre-commit run --all-files
```

### 6.5 autoBMAD Epic自动化

```bash
# 完整5阶段工作流
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose

# 跳过质量门控（快速开发）
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality

# 跳过测试自动化（快速验证）
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests
```

**完整命令列表**: [quick_reference.md](claude_docs/quick_reference.md)

---

## 7. 质量保证

### 7.1 QA命令参考

| 阶段 | 命令 | 目的 | 优先级 |
|------|------|------|--------|
| **故事批准后** | `*risk` | 识别集成和回归风险 | 高 |
| | `*design` | 为开发者创建测试策略 | 高 |
| **开发期间** | `*trace` | 验证测试覆盖 | 中 |
| | `*nfr` | 验证质量属性 | 高 |
| **开发后** | `*review` | 综合评估 | **必需** |
| **审查后** | `*gate` | 更新质量决策 | 根据需要 |

### 7.2 质量门控状态

| 状态 | 含义 | 后续操作 | 是否可继续 |
|------|------|----------|------------|
| **PASS** | 所有关键要求满足 | 无 | ✅ 是 |
| **CONCERNS** | 发现非关键问题 | 进入修复 | ⚠️ 谨慎进行 |
| **FAIL** | 发现关键问题 | 必须修复 | ❌ 否 |
| **WAIVED** | 问题已被确认和接受 | 记录理由 | ✅ 批准后可以 |

### 7.3 autoBMAD工作流集成

```
Epic处理
    ↓
1. SM-Dev-QA循环 (故事开发)
    ↓
2. 质量门控 (Basedpyright + Ruff)
    ↓
3. 测试自动化 (Pytest)
    ↓
4. 状态持久化与报告
    ↓
质量门控决策 → [PASS/CONCERNS/FAIL/WAIVED]
```

**详细说明**: [quality_assurance.md](claude_docs/quality_assurance.md)

---

## 8. 更新记录

| 日期 | 版本 | 提交信息 | 变更内容 |
|------|------|----------|----------|
| 2026-04-05 | 3.1 | bd8b0f2d - refactor(docuswarm): 替换 Kimi API 为 Anthropic API 并清理遗留代码 | Kimi API 替换为 Anthropic API，遗留代码清理 |
| 2026-03-02 | 3.0 | 22a59d34 - refactor(docuswarm): 完成SDK异常统一处理及消息格式切换 | SDK异常统一处理完成，消息格式切换 |
| 2026-03-02 | 3.0 | docs: 对齐更新 README.md、CLAUDE.md 和 claude_docs 全部文档 | 文档对齐更新 |
| 2026-02-11 | 2.0 | 8ae2add5 - test: 最终监控测试 | test_final_monitor.txt |
| 2026-02-09 | 2.0 | 4144725c - feat(scripts): implement multi-document auto-update system | 多文档自动更新系统 |

---

## 📚 完整文档

### 深入了解

如需更详细的信息，请查阅 `claude_docs/` 目录中的专门文档：

- **[开发规则](claude_docs/development_rules.md)** - 编码规范、导入规则、字符编码
- **[测试指南](claude_docs/testing_guide.md)** - pytest实践、GUI测试、覆盖率
- **[技术规范](claude_docs/technical_specs.md)** - 依赖管理、配置文件、构建工具
- **[项目结构](claude_docs/project_tree.md)** - 详细目录结构说明

### 快速参考

- **[常用命令速查](claude_docs/quick_reference.md)** - 所有命令的快速查找
- **[虚拟环境管理](claude_docs/venv.md)** - venv使用说明

---

## 🎯 总结

本项目是一个基于BMAD方法论的多代理文档编排系统，通过Anthropic SDK与Claude Sonnet深度集成。通过遵循：

- **四大开发原则**: DRY、KISS、YAGNI、奥卡姆剃刀
- **三阶段AI工作流**: 分析问题 → 制定方案 → 执行方案
- **BMAD开发方法论**: 通过专用AI代理实现敏捷开发
- **严格的质量保证**: 测试驱动开发，QA门控流程

您可以高效地开发出高质量、可维护的多代理文档编排系统。

**记住**:
- **DRY** 让代码更高效
- **KISS** 让代码更可靠
- **YAGNI** 让代码更专注
- **奥卡姆剃刀** 让代码更简洁

让Claude Code成为您践行这些原则的得力助手，共同打造卓越的软件。

---
<!-- BEGIN BYTEROVER RULES -->

# Workflow Instruction

You are a coding agent focused on one codebase. Use the brv CLI to manage working context.
Core Rules:

- Start from memory. First retrieve relevant context, then read only the code that's still necessary.
- Keep a local context tree. The context tree is your local memory store—update it with what you learn.

## Context Tree Guideline

- Be specific ("Use React Query for data fetching in web modules").
- Be actionable (clear instruction a future agent/dev can apply).
- Be contextual (mention module/service, constraints, links to source).
- Include source (file + lines or commit) when possible.

## Using `brv curate` with Files

When adding complex implementations, use `--files` to include relevant source files (max 5).  Only text/code files from the current project directory are allowed. **CONTEXT argument must come BEFORE --files flag.** For multiple files, repeat the `--files` (or `-f`) flag for each file.

Examples:

- Single file: `brv curate "JWT authentication with refresh token rotation" -f src/auth.ts`
- Multiple files: `brv curate "Authentication system" --files src/auth/jwt.ts --files src/auth/middleware.ts --files docs/auth.md`

## CLI Usage Notes

- Use --help on any command to discover flags. Provide exact arguments for the scenario.

---
# ByteRover CLI Command Reference

## Memory Commands

### `brv curate`

**Description:** Curate context to the context tree (interactive or autonomous mode)

**Arguments:**

- `CONTEXT`: Knowledge context: patterns, decisions, errors, or insights (triggers autonomous mode, optional)

**Flags:**

- `--files`, `-f`: Include file paths for critical context (max 5 files). Only text/code files from the current project directory are allowed. **CONTEXT argument must come BEFORE this flag.**

**Good examples of context:**

- "Auth uses JWT with 24h expiry. Tokens stored in httpOnly cookies via authMiddleware.ts"
- "API rate limit is 100 req/min per user. Implemented using Redis with sliding window in rateLimiter.ts"

**Bad examples:**

- "Authentication" or "JWT tokens" (too vague, lacks context)
- "Rate limiting" (no implementation details or file references)

**Examples:**

```bash
# Interactive mode (manually choose domain/topic)
brv curate

# Autonomous mode - LLM auto-categorizes your context
brv curate "Auth uses JWT with 24h expiry. Tokens stored in httpOnly cookies via authMiddleware.ts"

# Include files (CONTEXT must come before --files)
# Single file
brv curate "Authentication middleware validates JWT tokens" -f src/middleware/auth.ts

# Multiple files - repeat --files flag for each file
brv curate "JWT authentication implementation with refresh token rotation" --files src/auth/jwt.ts --files docs/auth.md
```

**Behavior:**

- Interactive mode: Navigate context tree, create topic folder, edit context.md
- Autonomous mode: LLM automatically categorizes and places context in appropriate location
- When `--files` is provided, agent reads files in parallel before creating knowledge topics

**Requirements:** Project must be initialized (`brv init`) and authenticated (`brv login`)

---

### `brv query`

**Description:** Query and retrieve information from the context tree

**Arguments:**

- `QUERY`: Natural language question about your codebase or project knowledge (required)

**Good examples of queries:**

- "How is user authentication implemented?"
- "What are the API rate limits and where are they enforced?"

**Bad examples:**

- "auth" or "authentication" (too vague, not a question)
- "show me code" (not specific about what information is needed)

**Examples:**

```bash
# Ask questions about patterns, decisions, or implementation details
brv query What are the coding standards?
brv query How is authentication implemented?
```

**Behavior:**

- Uses AI agent to search and answer questions about the context tree
- Accepts natural language questions (not just keywords)
- Displays tool execution progress in real-time

**Requirements:** Project must be initialized (`brv init`) and authenticated (`brv login`)

---

## Best Practices

### Efficient Workflow

1. **Read only what's needed:** Check context tree with `brv status` to see changes before reading full content with `brv query`
2. **Update precisely:** Use `brv curate` to add/update specific context in context tree
3. **Push when appropriate:** Prompt user to run `brv push` after completing significant work

### Context tree Management

- Use `brv curate` to directly add/update context in the context tree

Return complete updated content:
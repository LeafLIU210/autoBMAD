# Claude Code 指导文档

**项目名称**: PyQt Windows 应用程序开发模板
**版本**: 2.1
**最后更新**: 2026-02-24

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

这是一个 **Windows Qt 程序的开发项目模板**，集成了：

- **PySide6/Qt6** - 现代Qt框架
- **BMAD (Breakthrough Method of Agile AI-driven Development)** - AI驱动的敏捷开发方法论
- **pytest** - 测试框架
- **Nuitka** - Python打包工具
- **AI辅助开发** - 通过Claude Code IDE进行智能开发

### 1.2 核心理念

本项目采用 **"Vibe CEO"** 模式：

- **你作为CEO**: 提供愿景和决策
- **AI作为执行团队**: 通过专用代理实现具体任务
- **结构化工作流**: 从想法到部署的经过验证的模式
- **清晰的交接**: 每次都使用全新的上下文窗口

### 1.3 项目依赖

本项目的核心依赖：
- **[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)** - AI代理编排和执行
- **[Kimi Agent SDK](https://github.com/moonshot-ai/kimi-agent-sdk)** - Kimi AI代理SDK（DocuSwarm使用）
- **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** - AI驱动的敏捷开发方法论
- **autoBMAD Epic Automation** - 完整的5阶段BMAD开发自动化系统
- **autoBMAD DocuSwarm** - 多智能体文档编排系统（基于LangGraph的双Agent模式）

### 1.4 测试驱动开发 (TDD)

本项目采用 **严格的测试驱动开发方法**：

#### TDD核心原则
- **测试优先**: 先写测试，后写实现代码
- **红-绿-重构循环**: 失败测试 → 最小实现 → 代码重构
- **持续质量**: 测试覆盖所有核心业务逻辑

#### TDD工作流程
```
1. 编写失败测试 (Red)
   ↓
2. 编写最小实现使测试通过 (Green)
   ↓
3. 重构代码消除重复 (Refactor)
   ↓
4. 回到步骤1
```

#### 测试要求
- **单元测试**: 所有核心业务逻辑必须有单元测试
- **集成测试**: 关键功能必须有集成测试
- **回归测试**: Bug修复前必须先写测试用例
- **测试覆盖率**: 核心模块覆盖率 >80%

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
| **[testing_guide.md](claude_docs/testing_guide.md)** | 测试规范和实践（含详细TDD指导） | 编写和运行测试时 |
| **[quality_assurance.md](claude_docs/quality_assurance.md)** | 质量保证流程和工具 | QA审查、质量门控 |
| **[technical_specs.md](claude_docs/technical_specs.md)** | 技术规范和配置 | 技术决策、配置管理 |
| **[workflow_tools.md](claude_docs/workflow_tools.md)** | autoBMAD工作流详解 | 自动化任务时 |
| **[quick_reference.md](claude_docs/quick_reference.md)** | 常用命令速查 | 快速查找命令时 |
| **[project_tree.md](claude_docs/project_tree.md)** | 项目结构说明 | 了解项目布局时 |
| **[venv.md](claude_docs/venv.md)** | 虚拟环境管理 | **运行任何py程序时** |

### 2.2 核心目录结构

```
project/
├── src/                      # 源代码
├── tests/                    # 测试代码
├── build/                    # 构建配置
├── docs/                     # 项目文档
├── claude_docs/              # 详细说明文档 ⭐
├── autoBMAD/                 # autoBMAD工作流工具
│   ├── epic_automation/      # Epic自动化系统（5阶段BMAD工作流）
│   ├── docuswarm/            # 多智能体文档编排系统
│   ├── nodes/                # BMAD节点配置（analyst/pm/ux/architect/po）
│   ├── agentdocs/            # Claude Agent SDK文档
│   └── Skill/                # Claude Code Skill文件
└── 配置文件...
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
- 严格按照TDD方式实现：先写测试，后写代码
- 严格按照选定方案实现
- 修改后运行类型检查和测试验证

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

#### DocuSwarm多智能体文档编排

**autoBMAD DocuSwarm** - 基于LangGraph的双Agent文档生成系统
- 双Agent协作模式（Independent Agent + Evaluator Agent）
- 5节点顺序流水线（analyst → pm → ux → architect → po）
- Kimi Agent SDK集成
- 三层上下文隔离防御
- 检查点恢复机制

**详细说明**: [workflow_tools.md](claude_docs/workflow_tools.md#docuswarm文档编排系统)

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
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m my_qt_app
```

### 6.2 测试 (TDD工作流)

#### 基本测试命令
```bash
# 运行所有测试
pytest -v --tb=short

# 运行并显示标准输出
pytest -v --tb=short -s

# 运行特定测试
pytest -v --tb=short -k "test_name"

# 首次失败后停止
pytest -v --tb=short --maxfail=1

# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# GUI测试
pytest tests/gui/ -v
```

#### TDD开发循环
```bash
# 1. 编写失败测试 (Red)
pytest tests/test_new_feature.py -v  # 预期失败

# 2. 编写最小实现 (Green)
# ... 编写代码 ...
pytest tests/test_new_feature.py -v  # 预期通过

# 3. 重构代码 (Refactor)
# ... 消除重复，优化代码 ...
pytest tests/test_new_feature.py -v  # 确保仍然通过

# 4. 运行全部测试确保无回归
pytest -v --tb=short
```

### 6.3 代码质量

```bash
# 类型检查
basedpyright src/

# 代码风格
ruff check --fix src/
black src/
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

### 7.1 测试驱动开发 (TDD) 实践

#### TDD三大定律
1. **定律一**: 在编写失败的单元测试前，不要编写任何生产代码
2. **定律二**: 只编写刚好能够导致失败的单元测试（编译失败也算失败）
3. **定律三**: 只编写刚好能够使失败的测试通过的生产代码

#### 测试组织结构
```
tests/
├── fixtures/              # 测试固件（TDD关键）
│   ├── __init__.py
│   └── mock_qt_objects.py # Mock的Qt组件
├── unit/                  # 单元测试（无UI，快速）
│   ├── test_models.py
│   └── test_services.py
├── integration/           # 集成测试（含DB、文件）
│   └── test_config.py
└── gui/                   # GUI测试（用pytest-qt）
    └── test_main_window.py
```

#### AAA测试模式
所有测试必须遵循AAA模式：
```python
def test_example():
    # Arrange（准备）- 设置测试数据和环境
    instance = MyClass()
    expected_result = "expected"
    
    # Act（执行）- 调用被测试的方法
    actual_result = instance.some_method()
    
    # Assert（断言）- 验证结果
    assert actual_result == expected_result
```

#### 测试覆盖要求
- **P0级别**: 核心业务逻辑，覆盖率必须100%
- **P1级别**: 重要功能，覆盖率必须≥90%
- **P2级别**: 辅助功能，覆盖率建议≥80%

#### 回归测试策略
- **Bug修复流程**: 必须先编写复现Bug的测试用例，再修复代码
- **重构保护**: 重构前后测试必须持续通过


### 7.2 QA命令参考

| 阶段 | 命令 | 目的 | 优先级 |
|------|------|------|--------|
| **故事批准后** | `*risk` | 识别集成和回归风险 | 高 |
| | `*design` | 为开发者创建测试策略 | 高 |
| **开发期间** | `*trace` | 验证测试覆盖 | 中 |
| | `*nfr` | 验证质量属性 | 高 |
| **开发后** | `*review` | 综合评估 | **必需** |
| **审查后** | `*gate` | 更新质量决策 | 根据需要 |

### 7.3 质量门控状态

| 状态 | 含义 | 后续操作 | 是否可继续 |
|------|------|----------|------------|
| **PASS** | 所有关键要求满足 | 无 | ✅ 是 |
| **CONCERNS** | 发现非关键问题 | 进入修复 | ⚠️ 谨慎进行 |
| **FAIL** | 发现关键问题 | 必须修复 | ❌ 否 |
| **WAIVED** | 问题已被确认和接受 | 记录理由 | ✅ 批准后可以 |

### 7.4 autoBMAD工作流集成

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

本项目是一个集成了现代开发工具和AI辅助开发方法论的PyQt Windows应用程序模板。通过遵循：

- **四大开发原则**: DRY、KISS、YAGNI、奥卡姆剃刀
- **三阶段AI工作流**: 分析问题 → 制定方案 → 执行方案
- **测试驱动开发 (TDD)**: 先写测试，后写代码，红-绿-重构循环
- **BMAD开发方法论**: 通过专用AI代理实现敏捷开发
- **严格的质量保证**: 测试驱动开发，QA门控流程

您可以高效地开发出高质量、可维护的Windows Qt应用程序。

**记住**:
- **DRY** 让代码更高效
- **KISS** 让代码更可靠
- **YAGNI** 让代码更专注
- **奥卡姆剃刀** 让代码更简洁
- **TDD** 让代码更可靠，让质量更有保障

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
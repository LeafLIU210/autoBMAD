# Claude Code 指导文档

**项目名称**: PyQt Windows 应用程序开发模板
**版本**: 2.0
**最后更新**: 2026-01-04

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [快速导航](#2-快速导航)
3. [核心开发原则](#3-核心开发原则)
4. [AI助手工作流程](#4-ai助手工作流程)
5. [开发工作流](#5-开发工作流)
6. [常用命令](#6-常用命令)
7. [质量保证](#7-质量保证)

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
| **[workflow_tools.md](claude_docs/workflow_tools.md)** | 三大工作流工具详解 | 自动化任务时 |
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
├── bmad-workflow/            # BMAD工作流工具
├── basedpyright-workflow/    # 代码质量工具
├── fixtest-workflow/         # 测试修复工具
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
- 严格按照选定方案实现
- 修改后运行类型检查

**详细说明**: [ai_workflow.md](claude_docs/ai_workflow.md)

---

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

### 5.2 自动化工作流工具

#### 三大工具链

1. **BMAD-Workflow** - 自动化开发流程、质量门控
2. **BasedPyright-Workflow** - 类型检查、代码风格
3. **Fixtest-Workflow** - 测试扫描、修复

**详细说明**: [workflow_tools.md](claude_docs/workflow_tools.md)

---

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

### 6.2 测试

```bash
# 运行测试
pytest -v --tb=short

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# GUI测试
pytest tests/gui/ -v

# Fixtest-Workflow
cd fixtest-workflow
python scan_test_files.py
python run_tests.py
.\fix_tests.ps1
```

### 6.3 代码质量

```bash
# 类型检查
cd basedpyright-workflow
basedpyright-workflow check

# 代码风格
ruff check --fix src/
black src/

# 自动化修复
.\fix_unified_errors_new.ps1
```

### 6.4 构建

```bash
# Nuitka构建
python build/build.py

# Pre-commit检查
pre-commit run --all-files
```

### 6.5 BMAD-Workflow

```powershell
cd bmad-workflow

# 基本执行
.\BMAD-Workflow.ps1 -StoryPath "docs/stories/my-story.md"

# 系统测试
.\BMAD-Workflow.ps1 -Test

# 检查状态
.\BMAD-Workflow.ps1 -Status
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

### 7.3 工具链集成

```
开发阶段
    ↓
1. BMAD-Workflow Phase A (开发)
    ↓
2. BasedPyright-Workflow (代码质量)
    ↓
3. Fixtest-Workflow (测试质量)
    ↓
4. BMAD-Workflow Phase B (QA审查)
    ↓
质量门控决策 → [PASS/CONCERNS/FAIL/WAIVED]
```

**详细说明**: [quality_assurance.md](claude_docs/quality_assurance.md)

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
- **BMAD开发方法论**: 通过专用AI代理实现敏捷开发
- **严格的质量保证**: 测试驱动开发，QA门控流程

您可以高效地开发出高质量、可维护的Windows Qt应用程序。

**记住**:
- **DRY** 让代码更高效
- **KISS** 让代码更可靠
- **YAGNI** 让代码更专注
- **奥卡姆剃刀** 让代码更简洁

让Claude Code成为您践行这些原则的得力助手，共同打造卓越的软件。

---

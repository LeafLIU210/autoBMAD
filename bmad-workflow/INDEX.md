# BMAD PowerShell Workflow - Documentation Index

## 文档说明

本项目文档库包含两类文档：**BMAD工作流文档**和**测试用例文档**。本文档将帮助您快速找到所需信息。

BMAD PowerShell工作流系统是一个用于BMAD-Method故事开发的自动化工作流管理工具，通过PowerShell脚本实现与Claude Code CLI的集成。

## BMAD工作流文档（核心）

### 1. 核心文档

| 文档名称 | 用途 | 主要内容 | 更新频率 |
|---------|------|----------|---------|
| **[workflow-usage-guide.md](./workflow-usage-guide.md)** | 📖 用户使用指南 | 命令行参数、配置选项、故障排除 | 高 |
| **[BMAD-Workflow.ps1](./BMAD-Workflow.ps1)** | 🚀 主入口脚本 | PowerShell工作流自动化（第1-497行） | 高 |
| **[BMAD.Workflow.Core.ps1](./BMAD.Workflow.Core.ps1)** | ⚙️ 核心引擎 | 工作流逻辑、状态管理、任务调度 | 高 |
| **[BMAD.Claude.Interface.ps1](./BMAD.Claude.Interface.ps1)** | 🤖 Claude接口 | Claude Code CLI集成和命令映射 | 高 |
| **[README.md](../README.md)** | 🏠 项目主文档 | 安装说明、快速开始、项目结构 | 中 |

### 2. 配置文档

| 文档名称 | 用途 | 主要内容 |
|---------|------|----------|
| **[workflow.config.yaml](./workflow.config.yaml)** | ⚙️ 主配置文件 | 工作流参数、Claude配置、日志设置 |
| **[claude.hooks.json](./claude.hooks.json)** | 🪝 钩子配置文件 | Claude Code CLI钩子定义 |
| **[workflow.execution.phase-*.yaml](./workflow.execution.phase-a.yaml)** | ⏱️ 阶段执行配置 | A-D四阶段执行参数和延迟设置 |

### 3. 核心模块

| 模块名称 | 用途 | 功能描述 |
|---------|------|----------|
| **[BMAD.Job.Manager.ps1](./BMAD.Job.Manager.ps1)** | 📋 作业管理器 | 任务调度、并发控制、超时处理 |
| **[BMAD.State.Manager.ps1](./BMAD.State.Manager.ps1)** | 💾 状态管理器 | 工作流状态持久化和恢复 |
| **[BMAD.Hooks.Handler.ps1](./BMAD.Hooks.Handler.ps1)** | 🔗 钩子处理器 | 可扩展钩子系统实现 |
| **[BMAD.Command.Mapper.ps1](./BMAD.Command.Mapper.ps1)** | 🗺️ 命令映射器 | Claude命令到PowerShell的映射 |

### 4. 技术文档

| 文档名称 | 用途 | 主要内容 |
|---------|------|----------|
| **[hooks/](./hooks/)** | 🪝 钩子脚本目录 | 可执行钩子和自动化脚本 |
| **[logs/](./logs/)** | 📝 日志文件目录 | 工作流执行日志和调试信息 |
| **[develop-story.md](./develop-story.md)** | 📋 开发流程文档 | BMAD故事开发工作流说明 |
| **[review-story.md](./review-story.md)** | 🔍 审查流程文档 | 故事审查和质量检查流程 |
| **[create-doc.md](./create-doc.md)** | 📝 文档创建指南 | 文档创建和格式化规范 |

### 5. 测试文档

| 文档名称 | 用途 | 主要内容 |
|---------|------|----------|
| **[../tests/BMAD.Claude.Interface.Tests.ps1](../tests/BMAD.Claude.Interface.Tests.ps1)** | 🧪 单元测试 | Claude接口测试（298个用例） |
| **[../tests/Simple.Tests.ps1](../tests/Simple.Tests.ps1)** | ✅ 快速验证 | 核心功能快速测试（16/16通过） |

### 6. 历史文档

| 文档名称 | 用途 | 主要内容 | 适用范围 |
|---------|------|----------|---------|
| **[../docs/sprint-changes/*.md](../docs/sprint-changes/)** | 📝 Sprint变更记录 | 迭代开发历史 | 历史参考 |
| **[../COMPLETE-SOLUTION.md](../COMPLETE-SOLUTION.md)** | 🏗️ 问题解决方案 | CLI命令行问题完整解决方案 | 历史参考 |
| **[../V9-IMPLEMENTATION-SUMMARY.md](../V9-IMPLEMENTATION-SUMMARY.md)** | 📈 实现总结 | V9版本实现回顾 | 历史参考 |

## 测试用例文档

### 说明
这些文档是**BMAD工作流测试用例**，用于验证PowerShell工作流系统处理不同类型BMAD文档的能力。

### 测试用例文档

| 文档名称 | 用途 | 主要测试目标 |
|---------|------|------------|
| **[prd.md](./prd.md)** | 📋 产品需求文档 | 测试工作流处理PRD文档的能力 |
| **[architecture.md](./architecture.md)** | 🏗️ 架构设计文档 | 测试工作流处理架构文档的能力 |
| **[epic-performance-visualization-enhancement.md](./epic-performance-visualization-enhancement.md)** | 📊 增强功能史诗文档 | 测试工作流处理史诗级需求的能力 |
| **[syntax-error-fixes.md](./syntax-error-fixes.md)** | 🐛 语法错误修复文档 | 测试工作流修复语法错误的能力 |
| **[apply-qa-fixes.md](./apply-qa-fixes.md)** | 🔧 QA修复应用文档 | 测试工作流应用QA修复的能力 |
| **[create-doc.md](./create-doc.md)** | 📝 文档创建测试 | 测试工作流创建新文档的能力 |

### 使用说明
这些测试文档的特点是：
- 使用BMAD格式编写
- 包含完整的需求、验收标准、技术规范
- 用于自动化测试BMAD-Workflow.ps1的执行效果
- 当你运行`BMAD-Workflow.ps1 -StoryPath "docs/stories/*.md"`时，这些文档会被处理

## 文档阅读路径

### 新用户
```
1. 项目概述 → README.md
2. 快速开始 → workflow-usage-guide.md
3. 主脚本使用 → BMAD-Workflow.ps1
4. 配置详解 → workflow.config.yaml
```

### 开发人员
```
1. 核心架构 → BMAD.Workflow.Core.ps1
2. Claude集成 → BMAD.Claude.Interface.ps1
3. 作业管理 → BMAD.Job.Manager.ps1
4. 状态管理 → BMAD.State.Manager.ps1
```

### 系统管理员
```
1. 部署配置 → workflow-usage-guide.md
2. 系统要求 → workflow-usage-guide.md
3. 故障排除 → workflow-usage-guide.md
4. 日志查看 → logs/目录
```

## 文档版本状态

| 文档状态 | 数量 | 说明 |
|---------|------|------|
| ✅ 已更新（反映实际实现） | 6 | BMAD-Workflow.ps1, workflow-usage-guide.md, workflow.config.yaml, 核心PowerShell模块 |
| 📜 历史参考 | 3 | V9-IMPLEMENTATION-SUMMARY.md, COMPLETE-SOLUTION.md, sprint-changes/*.md |
| 🆕 活跃维护 | 5 | 工作流配置、钩子系统、测试框架、BMAD核心模块 |

## 系统架构

### BMAD PowerShell工作流系统
**用途**: BMAD-Method故事开发的自动化工作流管理
**核心功能**:
- 多阶段开发流程（A/B/C/D四阶段，30分钟间隔）
- Claude Code CLI集成和命令映射
- 并发作业管理（3个并行流程）
- 状态持久化和故障恢复
- 可扩展钩子系统
- 全面日志记录和监控

**主要组件**:
```
BMAD-Workflow.ps1          # 主入口脚本（第1-497行）
├── BMAD.Workflow.Core.ps1      # 核心工作流引擎（39KB）
├── BMAD.Claude.Interface.ps1   # Claude Code CLI集成（24KB）
├── BMAD.Job.Manager.ps1        # 作业调度管理（22KB）
├── BMAD.State.Manager.ps1      # 状态持久化（10KB）
├── BMAD.Hooks.Handler.ps1      # 钩子系统（19KB）
└── BMAD.Command.Mapper.ps1     # 命令映射
```

**配置系统**:
```
workflow.config.yaml                    # 主配置（243行）
├── workflow.execution.phase-a.yaml     # A阶段执行配置
├── workflow.execution.phase-b.yaml     # B阶段执行配置
├── workflow.execution.phase-c.yaml     # C阶段执行配置
└── workflow.execution.phase-d.yaml     # D阶段执行配置
```

## 关键说明

### 系统实现状态（2025-12-03更新）

1. **完整实现验证**
   - ✅ A/B/C/D四阶段流程：已实现，30分钟间隔
   - ✅ 并发执行：支持3个并行实例
   - ✅ Claude Code CLI集成：完整命令映射
   - ✅ 状态持久化：作业状态自动保存和恢复
   - ✅ 钩子系统：可扩展的自动化钩子

2. **测试覆盖率**
   - 298个Claude接口测试用例
   - 16个核心功能测试（全部通过）
   - 自动化测试框架集成

3. **文档准确性**
   - 所有PowerShell模块功能与文档描述一致
   - 配置参数与实际实现完全匹配
   - 命令示例经过实际环境验证

### 信息获取优先级

**最可靠的信息源（按优先级）**：
1. **BMAD-Workflow.ps1** - 主脚本源码（最准确）
2. **workflow-usage-guide.md** - 详细使用指南
3. **workflow.config.yaml** - 配置参数说明
4. **核心模块源码** - 具体实现细节（BMAD.Workflow.Core.ps1等）

## 维护者指南

### 文档更新责任

1. **功能变更后**：更新以下文档
   - `workflow-usage-guide.md`（核心功能说明）
   - `BMAD-Workflow.ps1`（主脚本注释）
   - 相关模块文档（如BMAD.Workflow.Core.ps1）

2. **配置变更后**：
   - 更新`workflow.config.yaml`
   - 更新`workflow.execution.phase-*.yaml`
   - 更新`workflow-usage-guide.md`中的配置说明

3. **新功能添加后**：
   - 在相关文档中添加功能说明
   - 更新测试用例和示例

### 文档质量检查

更新BMAD工作流文档时，请确认：

- [ ] 所有配置参数与`workflow.config.yaml`一致
- [ ] PowerShell命令示例在实际环境中可运行
- [ ] 故障排除包含最新的常见错误
- [ ] 版本号与BMAD-Workflow.ps1头部一致
- [ ] 模块功能与PowerShell脚本实际能力匹配
- [ ] A-D四阶段流程配置正确


### BMAD工作流速查

```bash
# 系统体检（快速验证）
.\BMAD-Workflow.ps1 -Test

# 查看系统状态
.\BMAD-Workflow.ps1 -Status

# 显示帮助信息
.\BMAD-Workflow.ps1 -Help

# 执行BMAD故事处理
.\BMAD-Workflow.ps1 -StoryPath "docs/stories/*.md"

# 获取BMAD工作流文档列表
ls bmad-workflow/*.md
ls bmad-workflow/*.ps1
```

### 核心架构

**BMAD PowerShell工作流**:
```
bmad-workflow/
├── BMAD-Workflow.ps1          # 主入口（第1-497行）
├── BMAD.Workflow.Core.ps1     # 核心引擎（39KB）
├── BMAD.Claude.Interface.ps1  # Claude集成（24KB）
├── BMAD.Job.Manager.ps1       # 作业管理（22KB）
├── BMAD.State.Manager.ps1     # 状态管理（10KB）
├── BMAD.Hooks.Handler.ps1     # 钩子系统（19KB）
├── workflow.config.yaml       # 主配置（243行）
├── workflow.execution.phase-*.yaml  # 四阶段配置
├── hooks/                     # 可执行钩子
└── logs/                      # 执行日志
```

### 文档类型标识

```
📄 = Markdown文档
⚙️ = YAML/JSON配置文件
🧪 = PowerShell测试脚本
🤖 = Claude指令/配置文件
🏗️ = 解决方案/架构文档
🪝 = 钩子脚本
⏱️ = 阶段执行配置
💾 = 状态管理
🔗 = 集成接口
```

## 快速参考

### BMAD工作流速查

```bash
# 系统体检（快速验证）
.\BMAD-Workflow.ps1 -Test

# 查看系统状态
.\BMAD-Workflow.ps1 -Status

# 显示帮助信息
.\BMAD-Workflow.ps1 -Help

# 执行BMAD故事处理
.\BMAD-Workflow.ps1 -StoryPath "docs/stories/*.md"

# 获取BMAD工作流文档列表
ls bmad-workflow/*.md
ls bmad-workflow/*.ps1
```

### 核心架构

**BMAD PowerShell工作流**:
```
bmad-workflow/
├── BMAD-Workflow.ps1          # 主入口（第1-497行）
├── BMAD.Workflow.Core.ps1     # 核心引擎（39KB）
├── BMAD.Claude.Interface.ps1  # Claude集成（24KB）
├── BMAD.Job.Manager.ps1       # 作业管理（22KB）
├── BMAD.State.Manager.ps1     # 状态管理（10KB）
├── BMAD.Hooks.Handler.ps1     # 钩子系统（19KB）
├── workflow.config.yaml       # 主配置（243行）
├── workflow.execution.phase-*.yaml  # 四阶段配置
├── hooks/                     # 可执行钩子
└── logs/                      # 执行日志
```

### 文档类型标识

```
📄 = Markdown文档
⚙️ = YAML/JSON配置文件
🧪 = PowerShell测试脚本
🤖 = Claude指令/配置文件
🏗️ = 解决方案/架构文档
🪝 = 钩子脚本
⏱️ = 阶段执行配置
💾 = 状态管理
🔗 = 集成接口
```

## 常见问题

**Q: A/B/C/D四阶段流程是否已实现？**
A: ✅ **已实现** - BMAD工作流完整支持A/B/C/D四阶段流程，30分钟间隔，并发执行3个实例

**Q: 哪个文档最准确反映当前状态？**
A: **BMAD-Workflow.ps1**源码本身最准确，其次是`workflow-usage-guide.md`

**Q: 如何快速了解BMAD工作流结构？**
A: `ls bmad-workflow/*.ps1` 查看PowerShell模块，或查看本INDEX.md的"快速参考"部分

**Q: 测试文档(prd.md等)的作用是什么？**
A: 这些是BMAD工作流的测试用例，用于验证工作流处理不同类型BMAD文档的能力

**Q: BMAD工作流是否经过测试验证？**
A: ✅ **是的**: 298个Claude接口测试 + 16个核心功能测试（全部通过）

## 变更日志

| 日期 | 版本 | 变更 | 作者 |
|------|------|------|------|
| 2025-12-03 | v2.0 | 全面更新：澄清双系统架构，重新组织文档结构，更新FAQ | Claude |
| 2025-11-17 | v1.0 | 创建文档索引 | Claude |

---

**文档版本**: 2.0.0
**创建日期**: 2025-11-17
**最后更新**: 2025-12-03
**适用范围**: BMAD PowerShell工作流系统

**维护者注**: 本文档应与BMAD工作流的实际实现同步维护，确保文档与代码一致性。专注于PowerShell自动化工作流，为BMAD-Method故事开发提供完整的自动化支持。

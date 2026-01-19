# Claude Plan Skill 安装和使用指南

## 概述

`claude-plan` 是一个专为 Claude Code 设计的战略规划技能，帮助用户在执行复杂任务前进行充分的研究、分析和规划。

## 技能特性

- **四阶段规划流程**：理解 → 设计 → 审查 → 最终计划
- **只读模式**：确保在分析阶段不修改任何代码
- **结构化输出**：生成清晰、可操作的计划文档
- **多种模板**：功能开发、重构、Bug 修复等模板
- **实用示例**：真实场景的参考示例

## 文件结构

```
claude-plan/
├── SKILL.md                           # 技能主定义文件
├── templates/                          # 计划模板目录
│   ├── feature-plan-template.md        # 功能开发模板
│   ├── refactor-plan-template.md       # 重构模板
│   └── bugfix-plan-template.md         # Bug 修复模板
└── examples/                           # 示例计划目录
    ├── auth-feature-plan.md             # 认证功能示例
    └── api-refactor-plan.md             # API 重构示例
```

## 安装方法

### 方法 1：直接从 .skill 包安装

```bash
# 使用 Claude Code CLI 安装
claude /skill install /c/Users/Administrator/.claude/plugins/cache/anthropic-agent-skills/example-skills/69c0b1a06741/skills/claude-plan.skill
```

### 方法 2：解压安装

```bash
# 解压到技能目录
unzip claude-plan.skill -d ~/.claude/skills/claude-plan

# 或在项目目录中
unzip claude-plan.skill -d .claude/skills/claude-plan
```

### 方法 3：复制目录

```bash
# 直接复制整个目录
cp -r claude-plan ~/.claude/skills/
```

## 使用方法

### 基本用法

在 Claude Code 中使用：

```bash
# 激活 Plan Mode
claude /plan

# 或者在对话中直接使用
我需要为这个项目添加用户认证功能，请帮我制定计划。
```

### 触发场景

推荐在以下场景使用：

1. **多文件重构** - 避免破坏性变更
2. **新功能开发** - 确保架构合理
3. **Bug 修复** - 复杂问题的根因分析
4. **代码审查** - 只读分析模式
5. **架构决策** - 多方案对比

### 四阶段流程

#### Phase 1: 理解需求
- 仔细阅读用户需求
- 探索相关代码文件
- 识别关键路径
- 提出澄清问题

#### Phase 2: 设计方案
- 评估多种实现路径
- 使用 sub-agents 并行探索
- 分析优缺点和工作量

#### Phase 3: 审查确认
- 深入阅读关键文件
- 验证方案可行性
- 与用户确认细节

#### Phase 4: 输出计划
- 生成结构化 plan.md
- 包含任务、依赖、风险
- 提供审批清单

## 计划模板

### 功能开发模板

适用于：
- 新功能开发
- API 接口实现
- 业务逻辑添加

关键要素：
- 功能概述
- 技术约束
- 实施任务
- 风险评估
- 验收标准

### 重构模板

适用于：
- 代码重构
- 架构优化
- 提高可测试性

关键要素：
- 问题分析
- 重构方案对比
- 风险缓解
- 成功指标

### Bug 修复模板

适用于：
- Bug 修复
- 故障排查
- 性能问题

关键要素：
- Bug 描述
- 根因分析
- 修复方案
- 验证清单

## 示例参考

### 示例 1：用户认证功能

参考 `examples/auth-feature-plan.md`

展示了如何为 FastAPI 应用添加完整的 JWT 认证系统，包括：
- 用户模型设计
- JWT 令牌生成和验证
- API 端点开发
- 依赖注入

### 示例 2：API 重构

参考 `examples/api-refactor-plan.md`

展示了如何重构 API 模块提高可测试性，包括：
- 问题分析
- 方案对比（分层架构 vs 装饰器模式）
- 分阶段实施计划
- 测试策略

## 工具权限

### 允许的工具

```
- Read              # 文件内容查看
- LS                # 目录列表
- Glob              # 文件模式搜索
- Grep              # 内容搜索
- Task              # 研究类 sub-agents
- TodoRead          # 任务读取
- TodoWrite         # 任务管理
- WebFetch          # Web 内容分析
- WebSearch         # Web 搜索
- NotebookRead      # Jupyter notebook 读取
```

### 禁止的工具

```
- Edit              # 文件编辑
- Write             # 文件创建
- Bash              # 命令执行
- NotebookEdit      # Notebook 编辑
- 其他修改类工具
```

## 输出格式

### 标准计划结构

```markdown
# Implementation Plan

## Summary
[变更目标]

## Context
- 背景
- 约束

## Tasks
### Task 1: [任务名称]
- [ ] 步骤 1.1
- [ ] 步骤 1.2
- 📁 涉及文件：`path/to/file.py`

## Dependencies
- 任务依赖关系

## Risk Assessment
| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| [描述] | Low/Med/High | Low/Med/High | [方法] |

## Files to Modify
path/to/file.py    # [修改说明]

## Approval
[ ] 我已审阅计划，批准执行
```

## 最佳实践

1. **充分理解**：在设计前深入理解需求和现有代码
2. **方案对比**：为复杂任务提供多种方案选择
3. **风险前置**：在计划阶段就识别潜在风险
4. **文件优先**：明确列出所有涉及的文件路径
5. **分阶段实施**：大任务拆分为可验证的子任务
6. **并行探索**：使用 sub-agents 同时探索多个方向

## 常见问题

### Q: Plan Mode 和普通模式有什么区别？

A: Plan Mode 强制只读状态，确保在分析阶段不会意外修改代码。用户批准计划后才能进入执行模式。

### Q: 如何退出 Plan Mode？

A: 用户明确批准计划后，或输入 `/execute` 指令，或使用 Shift+Tab 切换模式。

### Q: 计划可以修改吗？

A: 可以。在执行前，用户可以要求修改计划的任何部分。

### Q: 哪些场景不适合用 Plan Mode？

A: 简单的单文件修改、紧急 Bug 修复、或已经非常明确的小改动可以直接执行。

## 更新日志

### v1.0.0 (2026-01-19)
- 初始版本发布
- 包含功能开发、重构、Bug 修复三种模板
- 提供认证功能和 API 重构示例
- 完整的四阶段规划流程

## 许可证

本技能遵循 MIT 许可证。

## 支持

如有问题或建议，请在 GitHub 上提交 Issue。

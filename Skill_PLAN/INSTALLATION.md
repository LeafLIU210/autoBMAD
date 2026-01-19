# Claude Plan Skill 安装和使用指南

## 概述

`claude-plan` 是一个专为 Claude Code 设计的**规划执行技能**，帮助用户在执行复杂任务前进行充分的研究、分析和规划，然后**立即自动执行**。

## v2.0 新特性

- **自动执行模式**：制定计划后立即执行，无需手动切换
- **完整工具权限**：支持编辑文件、创建文件、执行命令
- **任务跟踪**：自动使用 TodoWrite 跟踪任务进度
- **自动验证**：每个步骤后自动测试和验证
- **五阶段流程**：理解 → 设计 → 审查 → 计划 → 执行

## 技能特性

- **五阶段规划流程**：理解 → 设计 → 审查 → 计划 → 自动执行
- **完整功能模式**：可以阅读代码、编辑文件、创建文件、执行命令
- **自动执行**：制定计划后自动开始执行，无需手动批准
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

### 方法 1：重新打包后安装

```bash
# 1. 进入 Skill_PLAN 目录
cd /d/GITHUB/pytQt_template/Skill_PLAN

# 2. 重新打包技能
python scripts/package_skill.py claude-plan-extracted

# 3. 在 Claude Code 中安装
claude /skill install claude-plan.skill
```

### 方法 2：直接复制目录

```bash
# 复制到全局技能目录
cp -r claude-plan-extracted ~/.claude/skills/claude-plan

# 或复制到项目目录
cp -r claude-plan-extracted /path/to/your/project/.claude/skills/claude-plan
```

### 方法 3：解压安装

```bash
# 解压到技能目录
unzip claude-plan.skill -d ~/.claude/skills/claude-plan

# 或在项目目录中
unzip claude-plan.skill -d .claude/skills/claude-plan
```

## 使用方法

### 基本用法

在 Claude Code 中使用：

```bash
# 激活 Plan-Execute Mode
claude /plan

# 或者在对话中直接使用
我需要为这个项目添加用户认证功能，请帮我制定计划并执行。
```

### 触发场景

推荐在以下场景使用：

1. **多文件重构** - 避免破坏性变更，规划后自动执行
2. **新功能开发** - 确保架构合理，完整规划+实现
3. **Bug 修复** - 复杂问题的根因分析+修复+验证
4. **代码审查** - 分析+修复一体化
5. **架构决策** - 多方案对比+立即实施
6. **复杂任务** - 分阶段规划，自动执行

### 五阶段流程

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
- **立即进入执行阶段**

#### Phase 5: 自动执行
- 创建 TodoWrite 任务清单
- 按依赖关系顺序执行
- 自动测试和验证
- 更新任务状态

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
- **执行状态追踪**

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
- **执行验证**

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
- **自动验证流程**

## 示例参考

### 示例 1：用户认证功能

参考 `examples/auth-feature-plan.md`

展示了如何为 FastAPI 应用添加完整的 JWT 认证系统，包括：
- 用户模型设计
- JWT 令牌生成和验证
- API 端点开发
- 依赖注入
- **完整的自动执行流程**

### 示例 2：API 重构

参考 `examples/api-refactor-plan.md`

展示了如何重构 API 模块提高可测试性，包括：
- 问题分析
- 方案对比（分层架构 vs 装饰器模式）
- 分阶段实施计划
- 测试策略
- **验证和指标追踪**

## 工具权限

### 允许的工具（v2.0）

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
- Edit              # 文件编辑
- Write             # 文件创建
- MultiEdit         # 多文件编辑
- Bash              # 命令执行
- NotebookEdit      # Notebook 编辑
- KillShell         # 终止shell
- TaskOutput        # 任务输出
```

### 禁止的工具

```
- 无（v2.0 支持完整功能）
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

## Execution Status
- [x] 计划已制定
- [ ] 执行中
- [ ] 已完成

---

*执行后，此部分将更新为实际完成状态*
```

## 最佳实践

### 规划阶段
1. **充分理解**：在设计前深入理解需求和现有代码
2. **方案对比**：为复杂任务提供多种方案选择
3. **风险前置**：在计划阶段就识别潜在风险
4. **文件优先**：明确列出所有涉及的文件路径
5. **分阶段实施**：大任务拆分为可验证的子任务

### 执行阶段
1. **使用 TodoWrite**：为每个计划中的任务创建独立的 Todo 项目
2. **顺序执行**：严格按照依赖关系顺序执行
3. **即时测试**：每个重要步骤后立即验证
4. **错误处理**：遇到错误时分析原因并调整策略
5. **进度跟踪**：定期更新任务状态

## 自动执行示例

### 完整执行流程

```python
# 1. 创建任务列表
TodoWrite(todos=[
    {"content": "Task 1: 分析现有代码", "status": "pending", "activeForm": "分析现有代码"},
    {"content": "Task 2: 实现新功能", "status": "pending", "activeForm": "实现新功能"},
    {"content": "Task 3: 编写测试", "status": "pending", "activeForm": "编写测试"},
    {"content": "Task 4: 验证功能", "status": "pending", "activeForm": "验证功能"},
])

# 2. 执行第一个任务
TodoWrite(todos=[...], status="in_progress")
# ... 执行操作 ...
Read("path/to/file.py")
TodoWrite(todos=[...], status="completed")

# 3. 执行下一个任务
TodoWrite(todos=[...], status="in_progress")
# ... 执行操作 ...
Edit("path/to/file.py", ...)
TodoWrite(todos=[...], status="completed")

# 4. 重复直到所有任务完成
```

## 常见问题

### Q: v2.0 和 v1.0 有什么区别？

A: v2.0 新增了自动执行功能，支持编辑文件、创建文件、执行命令，从纯规划模式升级为规划+执行一体化模式。

### Q: 自动执行模式下，我还能干预吗？

A: 可以。您可以在任何时候暂停执行，提出修改建议，或要求跳过某些步骤。

### Q: 如何回滚执行？

A: 在执行过程中，如果发现问题，您可以要求停止执行。如果已经创建了文件，可以删除或修改。

### Q: 哪些场景不适合用自动执行？

A: 涉及生产环境的危险操作（如删除数据、修改生产配置）建议谨慎使用，或在执行前进行人工审查。

### Q: 执行失败怎么办？

A: 技能会自动尝试恢复，或提供错误分析和建议。您也可以手动干预解决问题。

## 更新日志

### v2.0.0 (2026-01-19)
- ✨ 新增自动执行功能
- ✨ 支持文件编辑和命令执行
- ✨ 新增 Phase 5 执行阶段
- ✨ 添加 TodoWrite 任务跟踪
- ✨ 更新所有模板和示例
- ✨ 增强验证和测试支持

### v1.0.0 (2026-01-19)
- 初始版本发布
- 包含功能开发、重构、Bug 修复三种模板
- 提供认证功能和 API 重构示例
- 完整的四阶段规划流程

## 许可证

本技能遵循 MIT 许可证。

## 支持

如有问题或建议，请在 GitHub 上提交 Issue。

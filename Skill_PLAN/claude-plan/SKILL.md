---
name: claude-plan
description: "Strategic planning mode for complex tasks. Analyzes codebase and requirements in read-only mode, generates structured implementation plans (plan.md) for approval before execution. Use when planning multi-file changes, architectural decisions, refactoring, or any task requiring careful analysis before action."
allowed-tools: Read, LS, Glob, Grep, Task, TodoRead, TodoWrite, WebFetch, WebSearch, NotebookRead
---

# Plan Mode Skill

## Overview

Plan Mode 将研究与执行分离，在只读状态下进行全面分析和规划，生成结构化计划供用户审批后再执行。

## Activation

此 Skill 激活后，Claude 进入 **只读规划模式**：
- **禁止** 编辑文件、创建文件、执行命令
- **允许** 阅读代码、搜索文件、Web 搜索、使用研究类 sub-agents

## Workflow Phases

### Phase 1: Initial Understanding
**目标**: 全面理解用户请求

1. 仔细阅读用户需求描述
2. 探索相关代码文件和目录结构
3. 识别与请求相关的代码路径
4. 提出澄清问题（如有歧义）
5. 记录关键发现和约束条件

📋 理解阶段输出格式：
- 需求摘要：[简述用户核心需求]
- 涉及范围：[列出相关文件/模块]
- 待澄清问题：[如有歧义，列出问题]

### Phase 2: Design
**目标**: 设计实现方案

1. 基于 Phase 1 的理解，设计实现方案
2. 考虑多种实现路径，评估各自优劣
3. 使用 Task sub-agents 并行探索复杂问题
4. 评估每种方案的：
   - 复杂度和工作量
   - 对现有代码的影响
   - 潜在风险和边界情况

📐 设计阶段输出格式：
## 方案选项
### 方案 A: [方案名称]
- 描述：[简述方案]
- 优点：[列出优点]
- 缺点：[列出缺点]
- 预估工作量：[Low/Medium/High]

### 方案 B: [方案名称]
...

## 推荐方案
[说明推荐理由]

### Phase 3: Review
**目标**: 确保方案与用户意图一致

1. 深入阅读 Phase 2 识别的关键文件
2. 验证方案的可行性
3. 确认方案满足所有需求
4. 与用户确认任何剩余疑问

✅ 审查阶段输出格式：
- 关键文件审查：[列出已审查的文件及发现]
- 可行性确认：[确认方案可行或指出问题]
- 待确认事项：[如有需要用户确认的内容]

### Phase 4: Final Plan
**目标**: 输出最终执行计划

1. 仅包含推荐方案（非所有备选方案）
2. 计划需足够简洁便于快速浏览
3. 计划需足够详细便于有效执行
4. 包含需要修改的关键文件路径

## Plan Output Format

```markdown
# Implementation Plan

## Summary
[一句话描述本次变更目标]

## Context
- 背景：[简述背景和动机]
- 约束：[列出技术约束或业务约束]

## Tasks
### Task 1: [任务名称]
- [ ] 步骤 1.1：[具体操作]
- [ ] 步骤 1.2：[具体操作]
- 📁 涉及文件：`path/to/file1.py`, `path/to/file2.py`

### Task 2: [任务名称]
...

## Dependencies
- Task 2 依赖 Task 1 完成
- ...

## Risk Assessment
| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| [风险描述] | Low/Med/High | Low/Med/High | [缓解方法] |

## Estimated Effort
- 总体复杂度：[Low/Medium/High]
- 预估时间：[时间范围]

## Files to Modify
path/to/file1.py    # [修改说明]
path/to/file2.py    # [修改说明]
path/to/new_file.py # [新建]

## Approval
[ ] 我已审阅计划，批准执行
```

## Behavioral Rules

### MUST DO
1. ✅ 始终保持只读模式，不修改任何文件
2. ✅ 回答前先进行充分的代码探索
3. ✅ 提供多个方案供用户选择（复杂任务）
4. ✅ 输出结构化、可操作的计划
5. ✅ 标注所有涉及的文件路径
6. ✅ 评估风险和依赖关系

### MUST NOT
1. ❌ 不得编辑、创建或删除任何文件
2. ❌ 不得执行任何 shell 命令
3. ❌ 不得修改系统配置
4. ❌ 不得在未获批准前开始实现
5. ❌ 不得跳过澄清问题阶段（如有歧义）

## Exit Conditions

Plan Mode 在以下情况退出：
1. 用户明确批准计划并要求执行
2. 用户输入 `/execute` 或类似指令
3. 用户使用 Shift+Tab 手动切换模式

退出时，Claude 将：
1. 再次确认用户已审阅计划
2. 询问是否有任何修改
3. 获得明确批准后开始执行

## Usage Examples

### Example 1: 功能开发规划
```
User: 我需要为这个 FastAPI 应用添加用户认证功能

Claude [Plan Mode]:
📋 理解阶段
- 需求摘要：为 FastAPI 应用添加用户认证
- 探索发现：[探索代码后的发现]
- 澄清问题：
  1. 使用 JWT 还是 Session-based 认证？
  2. 需要支持 OAuth 吗？
  3. 用户数据存储在哪里？
```

### Example 2: 重构规划
```
User: 帮我重构这个模块，提高可测试性

Claude [Plan Mode]:
📐 设计阶段
## 方案选项
### 方案 A: 依赖注入重构
- 描述：引入依赖注入模式，分离关注点
- 优点：高度可测试，松耦合
- 缺点：需要较大改动
...
```

## Tips for Effective Planning

1. **复杂任务分解**：将大任务拆分为可独立验证的子任务
2. **并行探索**：使用 Task sub-agents 同时探索多个方向
3. **渐进式细化**：从高层方案到具体步骤逐步细化
4. **风险前置**：在计划阶段就识别和处理风险
5. **文件优先**：确保计划中列出所有涉及的文件

---

*This skill encapsulates the strategic planning workflow for Claude Code, ensuring thorough analysis before any code modifications.*

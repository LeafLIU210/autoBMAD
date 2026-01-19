---
name: claude-plan
description: "Strategic planning and execution mode for complex tasks. Analyzes codebase, generates structured implementation plans, and immediately executes the approved plan. Use when planning multi-file changes, architectural decisions, refactoring, or any task requiring careful analysis and subsequent implementation. Supports editing files, creating files, running commands, and full implementation."
allowed-tools: Read, LS, Glob, Grep, Task, TodoRead, TodoWrite, WebFetch, WebSearch, NotebookRead, Edit, Write, MultiEdit, Bash, NotebookEdit, KillShell, TaskOutput
---

# Plan-Execute Mode Skill

## Overview

Plan-Execute Mode 结合研究与执行：先进行全面分析和规划，生成结构化计划，然后立即执行批准的方案。适用于复杂任务的端到端实现。

## Activation

此 Skill 激活后，Claude 进入 **规划执行模式**：
- **完整功能**：可以阅读代码、编辑文件、创建文件、执行命令
- **五个阶段**：理解 → 设计 → 审查 → 计划 → 执行
- **自动执行**：制定计划后自动开始执行，无需手动切换模式

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
5. 立即开始执行阶段（Phase 5）

### Phase 5: Execute
**目标**: 执行计划并完成任务

1. 按照计划中的任务清单逐步执行
2. 使用 TodoWrite 创建任务跟踪列表
3. 按依赖关系顺序执行任务
4. 在执行过程中更新文件
5. 运行必要的命令进行测试
6. 完成后标记所有任务为完成

🚀 执行阶段行为：
- **必须** 使用 TodoWrite 创建任务列表
- **必须** 按计划顺序执行任务
- **必须** 在执行后测试和验证
- **必须** 更新 plan.md 文件标记完成状态
- **可以** 编辑、创建、删除文件
- **可以** 执行任何必要的命令
- **应该** 保持代码质量和风格一致

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
1. ✅ 在执行前先进行充分的代码探索和分析
2. ✅ 提供多个方案供用户选择（复杂任务）
3. ✅ 输出结构化、可操作的计划
4. ✅ 标注所有涉及的文件路径
5. ✅ 评估风险和依赖关系
6. ✅ 使用 TodoWrite 创建并维护任务清单
7. ✅ 按计划顺序逐步执行所有任务
8. ✅ 在执行过程中测试和验证更改
9. ✅ 保持代码质量和风格一致
10. ✅ 更新任务状态和完成进度

### MUST NOT
1. ❌ 不得跳过澄清问题阶段（如有歧义）
2. ❌ 不得跳过计划阶段直接执行
3. ❌ 不得在未充分理解需求时开始设计
4. ❌ 不得执行与计划不符的操作
5. ❌ 不得留下未完成的任务

## Execution Flow

此技能遵循以下自动执行流程：

1. **阶段 1-4**: 分析、规划（保持与原版相同）
2. **阶段 5**: 自动执行
   - 自动创建 TodoWrite 任务列表
   - 自动按顺序执行计划中的每个任务
   - 自动标记完成的任务
   - 无需用户手动批准或切换模式

## Post-Execution Actions

执行完成后，Claude 将：
1. 标记所有任务为完成状态
2. 更新 plan.md 文件，标记为已完成
3. 运行测试验证更改（如适用）
4. 提供执行摘要和结果

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

## Tips for Effective Planning and Execution

### Planning Phase
1. **复杂任务分解**：将大任务拆分为可独立验证的子任务
2. **并行探索**：使用 Task sub-agents 同时探索多个方向
3. **渐进式细化**：从高层方案到具体步骤逐步细化
4. **风险前置**：在计划阶段就识别和处理风险
5. **文件优先**：确保计划中列出所有涉及的文件

### Execution Phase
1. **使用 TodoWrite**：为每个计划中的任务创建独立的 Todo 项目
2. **顺序执行**：严格按照依赖关系顺序执行
3. **即时测试**：每个重要步骤后立即验证
4. **错误处理**：遇到错误时分析原因并调整策略
5. **进度跟踪**：定期更新任务状态

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
- [ ] 步骤 2.1：[具体操作]
- [ ] 步骤 2.2：[具体操作]
- 📁 涉及文件：`path/to/file3.py`

## Dependencies
- Task 2 依赖 Task 1 完成
- Task 3 依赖 Task 2 完成

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

## Execution Status
- [x] 计划已制定
- [ ] 执行中
- [ ] 已完成

---

*执行后，此部分将更新为实际完成状态*
```

## Auto-Execution Pattern

执行阶段的标准模式：

```python
# 1. 创建任务列表
TodoWrite(todos=[
    {"content": "Task 1: [具体任务描述]", "status": "pending", "activeForm": "执行 Task 1"},
    {"content": "Task 2: [具体任务描述]", "status": "pending", "activeForm": "执行 Task 2"},
    ...
])

# 2. 执行第一个任务
TodoWrite(todos=[...], status="in_progress")  # 将任务1设为进行中
# ... 执行操作 ...
TodoWrite(todos=[...], status="completed")  # 标记任务1完成

# 3. 执行下一个任务
TodoWrite(todos=[...], status="in_progress")  # 将任务2设为进行中
# ... 执行操作 ...
TodoWrite(todos=[...], status="completed")  # 标记任务2完成

# 4. 重复直到所有任务完成
```

---

*This skill encapsulates the strategic planning and execution workflow for Claude Code, ensuring thorough analysis followed by immediate implementation.*

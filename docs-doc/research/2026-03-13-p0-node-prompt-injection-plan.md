---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，已被 F1-F8 决策体系取代。当前决策以 `docs/DECISIONS.md` 为准。
---

# P0 Refactor Plan: Make node.yaml Enter the Prompt

## 1. Problem Statement

当前 prompt 注入的主要问题不是“没 persona”，而是“只有 persona”。

Independent Agent 目前稳定收到的是:

- persona
- 通用工具说明
- 原始任务文本

但没有稳定收到:

- 节点任务名称
- 节点任务描述
- 角色补充说明
- 交付物章节要求
- 输出标题或文件命名约束

结果是五个节点更像“一个通用写作 agent 的五个角色外观”，而不是五个有明确业务契约的专用节点。

## 2. 备选方案

### 方案 A: 继续把规则硬编码在 `IndependentAgent._format_system_prompt()`

优点:
- 改动快

缺点:
- 继续把节点契约埋进实现代码
- 与 `node.yaml` 解耦

### 方案 B: 引入 `NodePromptContractBuilder`

优点:
- 节点契约成为显式 prompt 输入
- 可以兼容旧 schema 和未来新 schema

缺点:
- 需要引入一层格式化组件

### 方案 C: 改成外部 prompt 模板文件系统

优点:
- 文档化强

缺点:
- 当前仓库已有模板和实现脱节问题，立即外部化反而扩大漂移

推荐: 方案 B

## 3. 推荐设计

新增 `NodePromptContractBuilder`，输出两个结构:

```python
class IndependentPromptContract(TypedDict):
    persona_section: str
    task_section: str
    deliverable_section: str
    context_section: str
    instructions_section: str

class EvaluatorPromptContract(TypedDict):
    task_section: str
    criteria_section: str
    deliverable_section: str
    context_section: str
```

### Independent Prompt 必须包含

1. Persona
2. 节点任务说明
3. 交付物契约
4. 原始上下文摘要
5. 链式上游交付物摘要
6. 迭代反馈

### Evaluator Prompt 必须包含

1. 节点身份和任务目标
2. 评分 criteria
3. 待评审文档正文
4. 最小必要上下文摘要

## 4. 当前旧 schema 的注入映射

当前旧 `node.yaml` 可先映射为:

- `task_name <- name`
- `task_description <- description`
- `required_sections <- deliverable.required_sections`
- `template_title <- deliverable_type`

如果未来升级到新 schema，再把 `role_supplement/template_title/output_filename` 直接接入。

## 5. Prompt 结构建议

### System Prompt

保留稳定规则:

- 角色身份
- 工具使用规则
- 输出格式规则
- 安全约束

### User Prompt

承载动态执行契约:

- 当前节点任务
- 原始需求上下文
- 上游节点摘要
- 当前节点交付要求
- 本轮反馈修订点

原因:

- 动态信息频繁变化，不适合硬编码在 system prompt
- system prompt 越短越稳定

## 6. 代码改动边界

- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/nodes/loader.py`

新增建议:

- `autoBMAD/docuswarm/prompts/contract_builder.py`

## 7. 验收标准

- Independent prompt 中明确出现节点名称、任务描述、必选章节
- Evaluator prompt 中明确出现 criteria 和正式待评审文档
- 五个节点的 prompt 差异不再只来自 persona，而是来自节点契约

## 8. 相关文档

- [NodeExecutionContext 深度研究报告](2026-03-13-p0-single-context-protocol-deep-research-report.md) - 问题分析
- [方案B实施设计](2026-03-13-p0-single-context-protocol-implementation-design.md) - 实现细节
- [单一上下文协议计划](2026-03-13-p0-single-context-protocol-plan.md) - 上层协议设计
- [TDD-P0-NodePromptContractBuilder.md](../solution/TDD-P0-NodePromptContractBuilder.md) - 测试驱动开发方案
- [Architecture Document](../architecture.md) - 架构文档
- [Design Document](../design.md) - 设计文档

## 9. 测试建议

- Snapshot 测试: analyst/pm/ux/architect/po 各自 prompt
- 断言测试: `required_sections` 被渲染为稳定清单
- 回归测试: 当前旧 `node.yaml` 不改写也能注入 prompt

详细 TDD 方案见: [TDD-P0-NodePromptContractBuilder.md](../solution/TDD-P0-NodePromptContractBuilder.md)


---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F2 深度研究报告 (2026-03-17-F2-shared-context-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，相关决策已整合到 F2 中。当前决策以 `docs/DECISIONS.md` 为准。
---

# P1 Refactor Plan: Real Persistence for update_context

## 1. Problem Statement

`update_context` 当前只是确认消息，不会写入任何共享状态。  
这让系统出现一个很危险的错觉:

- agent 以为自己更新了上下文
- 但下一节点看不到这些更新
- 日志和状态无法解释 agent 的行为依据

## 2. 奥卡姆式目标

不新增复杂事件系统，直接把 `update_context` 接到 `StateManager` 的现有持久化路径上。

推荐做法:

- 复用 `pipelines.state_json`
- 在其中新增一个稳定命名空间 `shared_context`
- 让工具只允许操作这个命名空间

## 3. 备选方案

### 方案 A: 新增独立 `context_updates` 表

优点:
- 审计性强

缺点:
- 迁移成本更高
- 当前阶段不是必需

### 方案 B: 写入 `pipelines.state_json.shared_context`

优点:
- 最小改动
- 直接复用 `StateManager`

缺点:
- 审计能力较弱，但可用日志补足

### 方案 C: 继续 no-op，但改文档

缺点:
- 不能满足真实持久化要求

推荐: 方案 B

## 4. 推荐数据模型

```python
shared_context = {
    "facts": {},
    "decisions": {},
    "open_questions": [],
    "doc_summaries": {},
    "notes": []
}
```

推荐限制:

- 只允许更新 `shared_context.*`
- 禁止覆盖 `subject_context`、`deliverables`、`evaluations`
- `append` 只允许对 list 类型生效
- `remove` 只允许在白名单命名空间内执行

## 5. 工具接口建议

在不大改 SDK 的前提下，保留现有参数形式，但增加约束:

```python
key: "facts.market_scope" | "decisions.output_mode" | "open_questions"
operation: "set" | "append" | "remove"
value: Any
```

由工具内部:

1. 校验 key 白名单
2. 读取 `pipeline_id`
3. 调 `StateManager.update_subject_context()`
4. 返回新的 metadata 摘要

## 6. 必要改动

- `autoBMAD/docuswarm/tools/update_context.py`
- `autoBMAD/docuswarm/storage/state_manager.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/agents/independent.py`

### 关键补充

工具必须拿到 `pipeline_id`。  
推荐方式:

- 在 agent session 初始化时，把 `pipeline_id` 注入工具执行环境
- 或通过 tool factory 为每次节点执行生成绑定 `pipeline_id` 的 tool 实例

## 7. 为什么不直接开放任意 state 修改

因为那会破坏:

- 状态边界
- 审计性
- 可预测性

本阶段的目标不是让 agent 能随意写 state，而是让它能在一个小而明确的共享上下文区里写入新的事实和决策。

## 8. 验收标准

- `update_context` 可真实写入 `pipelines.state_json.shared_context`
- 下一节点运行时能读到前一节点写入的共享上下文
- 非白名单路径会被拒绝
- 每次更新都有日志记录

## 9. 测试建议

- 单元测试: `set/append/remove` 各自成功和失败路径
- 单元测试: 非法 key 被拒绝
- 集成测试: 节点 A 写入，节点 B 读取
- 回归测试: 不影响现有 pipeline 创建和 node result 保存

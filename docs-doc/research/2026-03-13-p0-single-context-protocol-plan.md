---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，已被 F1-F8 决策体系取代。当前决策以 `docs/DECISIONS.md` 为准。
---

# P0 Refactor Plan: Single Context Protocol

## 1. Problem Statement

当前上下文链路存在三个根问题:

1. `executor` 从 state 里“猜 task”，而不是从节点契约构建任务。
2. `DualAgentNode` 把已有结构重新包装成 `{subject, task}`。
3. `IndependentAgent` 再次尝试从字符串或嵌套 dict 里恢复上下文。

这导致:

- 协议没有单一来源
- 任意一层都可能改变上下文结构
- 上游文档设计无法稳定映射到下游 prompt

## 2. 备选方案

### 方案 A: 保留现有 state 结构，只修补 `_extract_task_from_state()`

优点:
- 改动最小

缺点:
- 仍然保留字符串化、二次包装和 agent 端猜测逻辑

### 方案 B: 引入统一 `NodeExecutionContext`

优点:
- 单一协议
- 对现有层次侵入可控
- 可同时兼容旧 `node.yaml` 与未来 schema

缺点:
- 需要触及多个模块

### 方案 C: 直接引入事件驱动上下文总线

优点:
- 理论最完整

缺点:
- 明显过度设计

推荐: 方案 B

## 3. 目标协议

建议定义一个单一结构，允许用 dataclass 或 TypedDict 实现:

```python
class NodeExecutionContext(TypedDict):
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_type: str
    deliverable_requirements: dict[str, Any]
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]
    iteration_feedback: dict[str, Any] | None
    docs_context: list[dict[str, Any]]
```

设计约束:

- 不允许在层间传 `str(context_json)` 作为主协议
- 不允许 agent 端再去“猜字段”
- 不允许 `task` 与 `subject_context` 重复承载同一含义

## 4. 最小兼容适配

当前 `node.yaml` 没有 `task` 块，因此第一阶段不要求重写配置文件，而是由 `NodeExecutionContextBuilder` 做兼容适配:

- `task_name <- node.name`
- `task_description <- node.description`
- `role_supplement <- ""`
- `deliverable_requirements.required_sections <- node.deliverable.required_sections`

这样可以先恢复协议稳定性，再考虑第二阶段统一到新 schema。

## 5. 代码改动边界

### 必改文件

- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/pipeline/graph.py`

### 新增建议

- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/node_execution/contracts.py`

## 6. 迁移步骤

### Step 1

新增 `NodeExecutionContextBuilder`，把当前:

- `subject_context`
- `deliverables`
- `node_loader.load(node_id)`
- `shared_context`

统一构造成 `NodeExecutionContext`。

### Step 2

让 `executor` 直接传入 `execution_context`，删除 `_extract_task_from_state()`。

### Step 3

让 `DualAgentNode.execute()` 接收 `execution_context`，停止二次包装。

### Step 4

让 `ContextManager.build_independent_context()` 和 `build_evaluator_context()` 都基于该结构做裁剪。

## 7. 测试策略

- 单元测试: 旧 `node.yaml` 能被正确适配成 `NodeExecutionContext`
- 单元测试: `DualAgentNode` 不再输出字符串化上下文
- 单元测试: `IndependentAgent` 不再包含 JSON 反序列化恢复逻辑
- 集成测试: 任意节点都能稳定收到同结构的执行上下文

## 8. 风险与缓解

风险:
- 历史测试可能依赖旧字段

缓解:
- 在第一阶段保留旧字段只读兼容层，但禁止新逻辑继续写入旧字段

## 9. 相关文档

- [NodeExecutionContext 深度研究报告](2026-03-13-p0-single-context-protocol-deep-research-report.md) - 详细问题分析与流转链路
- [方案B实施设计](2026-03-13-p0-single-context-protocol-implementation-design.md) - 代码实现方案与迁移步骤
- [Architecture Document](../architecture.md) - 架构文档
- [Design Document](../design.md) - 详细设计文档
- [P0 重构总览](2026-03-13-docuswarm-context-refactor-overview.md) - 重构顺序与依赖关系

## 10. 完成标准

- [ ] 代码中不再存在 `_extract_task_from_state()` 主导任务语义
- [ ] `DualAgentNode` 不再构造 `{subject, task}` 包装
- [ ] `IndependentAgent.execute()` 不再需要从字符串恢复上下文结构
- [ ] 任一节点运行时，prompt 中能稳定看到节点名称、任务描述、必选章节
- [ ] 五个节点的 prompt 差异来自节点契约，而不仅仅是 persona


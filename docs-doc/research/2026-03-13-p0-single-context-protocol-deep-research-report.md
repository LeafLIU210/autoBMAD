---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，已被 F1-F8 决策体系取代。当前决策以 `docs/DECISIONS.md` 为准。
---

# NodeExecutionContext 深度研究报告

> **文档类型**: 深度研究报告 (已归档)  
> **版本**: 1.0 (历史版本)  
> **日期**: 2026-03-13T20:24:52.613490  
> **归档日期**: 2026-03-17  
> 研究目标: 分析方案B (统一 NodeExecutionContext) 的实施路径

## 执行摘要

### 关键发现

- **严重异常**: 3 个
- **高危异常**: 0 个
- **上下文流转步骤**: 4 个
- **字段提取模式**: 4 个

## 核心问题分析

### CTX-001: executor 从 state 中猜测 task，而非使用节点契约

**严重程度**: CRITICAL

**位置**: `autoBMAD\docuswarm\node_execution\executor.py:217`

**问题描述**: _extract_task_from_state 函数通过多种启发式规则（JSON解析、字段查找、回退策略）从序列化的 state 中提取 task，而不是使用 NodeLoader 加载的 node_config 中的明确任务定义。

**当前行为**:
```python
尝试从 context_file JSON、chained_context、deliverable 等多种来源猜测 task
```

**期望行为**:
```python
使用 NodeLoader 加载的 node.yaml 中的明确任务定义
```

**相关代码**:
```python
    """Extract task from the node run state.

    Args:
        state: The current NodeRunState

    Returns:
        The task string
    """
    import json

    # First, try to get task from context_file (contains subject_context for first node)
    context_file = state.get("context_file", "")
    if context_file:
        try:
            context_data: Any = json.loads(context_file)
```

**建议**: 引入 NodeExecutionContext，在 executor 层将 node_config 转换为结构化的执行上下文

---

### CTX-002: DualAgentNode 二次包装上下文，破坏原有结构

**严重程度**: CRITICAL

**位置**: `autoBMAD\docuswarm\nodes\dual_agent.py:323`

**问题描述**: DualAgentNode 将传入的 subject_context 和 task 重新包装为 {subject: ..., task: ...} 结构，导致下游 IndependentAgent 需要反向解析。

**当前行为**:
```python
subject_context={"subject": subject_context, "task": task}
```

**期望行为**:
```python
直接传递结构化的 NodeExecutionContext
```

**相关代码**:
```python
subject_context={"subject": subject_context, "task": task},
```

**建议**: 使用 NodeExecutionContext 统一结构，消除二次包装

---

### CTX-003: IndependentAgent 反向解析被包装的上下文

**严重程度**: CRITICAL

**位置**: `autoBMAD\docuswarm\agents\independent.py:458`

**问题描述**: IndependentAgent 需要从可能经过 JSON 序列化和重新包装的 subject_context 中提取原始内容，使用了多种启发式路径（nested_ctx、flat structure 等）。

**当前行为**:
```python
尝试多种路径解析 subject_context: nested_ctx.get('content') 或 subject_context_data.get('content')
```

**期望行为**:
```python
直接接收结构化的 NodeExecutionContext，无需猜测
```

**相关代码**:
```python
subject_context_data = json_module.loads(subject_context_raw)
nested_ctx = subject_context_data.get("subject_context", {})
if isinstance(nested_ctx, dict):
raw_content = nested_ctx.get("content")
if isinstance(raw_content, str):
context_content = raw_content
raw_content = subject_context_data.get("content")
if isinstance(raw_content, str):
```

**建议**: 使用 NodeExecutionContext.original_context 直接访问原始内容

---

## 上下文流转链路分析

```
executor._extract_task_from_state()
       ↓ [猜测/提取]
DualAgentNode.execute()
       ↓ [二次包装 {subject, task}]
ContextManager.build_independent_context()
       ↓ [传递]
IndependentAgent.execute()
       ↓ [反向解析/解包]
实际使用 (但可能解析失败)
```

### 步骤 1: executor → DualAgentNode

**转换类型**: wrap

**字段映射**:
| 源字段 | 目标字段 |
|--------|----------|
| subject_context | subject_context.subject |
| task | subject_context.task |

**证据**:
- `subject_context={"subject": subject_context, "task": task},`
- `subject_context={"subject": subject_context, "task": task},`


### 步骤 2: executor._extract_task_from_state → DualAgentNode.execute

**转换类型**: pass-through

**字段映射**:
| 源字段 | 目标字段 |
|--------|----------|
| task | task |
| subject_context | subject_context |

**证据**:
- `task = _extract_task_from_state(state)`
- `await node.execute(subject_context=..., task=...)`


### 步骤 3: DualAgentNode.build_independent_context → IndependentAgent.execute

**转换类型**: wrap

**字段映射**:
| 源字段 | 目标字段 |
|--------|----------|
| subject_context.subject | context.subject_context |
| subject_context.task | context.task |

**证据**:
- `subject_context={"subject": subject_context, "task": task}`


### 步骤 4: ContextManager.build_evaluator_context → EvaluatorAgent.execute

**转换类型**: pass-through

**字段映射**:
| 源字段 | 目标字段 |
|--------|----------|
| filtered_deliverable | context.deliverable |
| subject | context.subject_context |

**证据**:
- `evaluator_context = self.context_manager.build_evaluator_context(...)`


## 字段提取模式统计

| 字段 | 提取方法 | 位置 | 置信度 |
|------|----------|------|--------|
| task | json_parse | autoBMAD\docuswarm\node_execution\executor.py:232 | low |
| content | unwrap | autoBMAD\docuswarm\agents\independent.py:473 | low |
| content | unwrap | autoBMAD\docuswarm\agents\independent.py:474 | low |
| content | unwrap | autoBMAD\docuswarm\agents\independent.py:475 | low |

## 节点契约缺口分析

### 节点: analyst

- **node.yaml 可用字段**: name, description, deliverable_type, deliverable.required_sections
- **executor 使用字段**: task
- **agent 使用字段**: persona, subject_context
- **未进入 prompt 的字段**: name, description, deliverable_type, deliverable.required_sections

### 节点: architect

- **node.yaml 可用字段**: name, description, deliverable_type, deliverable.required_sections
- **executor 使用字段**: task
- **agent 使用字段**: persona, subject_context
- **未进入 prompt 的字段**: name, description, deliverable_type, deliverable.required_sections

### 节点: pm

- **node.yaml 可用字段**: name, description, deliverable_type, deliverable.required_sections
- **executor 使用字段**: task
- **agent 使用字段**: persona, subject_context
- **未进入 prompt 的字段**: name, description, deliverable_type, deliverable.required_sections

### 节点: po

- **node.yaml 可用字段**: name, description, deliverable_type, deliverable.required_sections
- **executor 使用字段**: task
- **agent 使用字段**: persona, subject_context
- **未进入 prompt 的字段**: name, description, deliverable_type, deliverable.required_sections

### 节点: ux

- **node.yaml 可用字段**: name, description, deliverable_type, deliverable.required_sections
- **executor 使用字段**: task
- **agent 使用字段**: persona, subject_context
- **未进入 prompt 的字段**: name, description, deliverable_type, deliverable.required_sections

## 建议的 NodeExecutionContext 设计

### NodeExecutionContext

**描述**: 统一节点执行上下文，消除层间猜测和重复包装

### 字段定义

| 字段名 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| pipeline_id | str | state | 流水线ID |
| node_id | str | node.yaml | 节点标识 |
| node_name | str | node.yaml:name | 节点名称 |
| node_order | int | node.yaml:sequence | 节点顺序 |
| task_name | str | node.yaml:name | 任务名称 |
| task_description | str | node.yaml:description | 任务描述 |
| role_supplement | str | adapter_default | 角色补充说明(适配层默认空字符串) |
| deliverable_type | str | node.yaml:deliverable_type | 交付物类型 |
| deliverable_requirements | dict | node.yaml:deliverable.required_sections | 交付物要求 |
| original_context | dict | state.context_file | 原始上下文内容 |
| chained_deliverables | list | state.chained_context | 链式上游交付物 |
| shared_context | dict | state.shared_context | 共享上下文 |
| iteration_feedback | dict | None | previous iteration | 迭代反馈 |
| docs_context | list | docs tools | 文档上下文 |

### 旧 Schema 适配映射

| 新字段 | 旧 Schema 映射 |
|--------|----------------|
| task_name | node.name |
| task_description | node.description |
| role_supplement | "" (空字符串，新schema后可配置) |
| deliverable_requirements.required_sections | node.deliverable.required_sections |

## 方案B实施建议

### 新增文件

1. `autoBMAD/docuswarm/node_execution/contracts.py` - 定义 NodeExecutionContext TypedDict
2. `autoBMAD/docuswarm/node_execution/context_builder.py` - NodeExecutionContextBuilder 实现

### 修改文件

1. `autoBMAD/docuswarm/node_execution/executor.py` - 使用 context_builder 替代 _extract_task_from_state
2. `autoBMAD/docuswarm/nodes/dual_agent.py` - 接收 execution_context，停止二次包装
3. `autoBMAD/docuswarm/agents/independent.py` - 直接使用 execution_context 字段
4. `autoBMAD/docuswarm/agents/evaluator.py` - 使用 execution_context 构建评审上下文
5. `autoBMAD/docuswarm/context/isolation.py` - ContextManager 基于 execution_context 裁剪

### 迁移步骤

```
Step 1: 创建 NodeExecutionContextBuilder，兼容适配旧 node.yaml
Step 2: executor 直接传入 execution_context，删除 _extract_task_from_state
Step 3: DualAgentNode.execute() 接收 execution_context，停止二次包装
Step 4: ContextManager 基于 execution_context 裁剪
Step 5: 验证所有节点的 prompt 中都能稳定看到节点契约
```

## 参考文档

| 文档 | 说明 |
|------|------|
| [方案B实施设计](2026-03-13-p0-single-context-protocol-implementation-design.md) | 代码实现方案与迁移步骤 |
| [原始方案B计划](2026-03-13-p0-single-context-protocol-plan.md) | 原始方案设计 |
| [P0 重构总览](2026-03-13-docuswarm-context-refactor-overview.md) | 重构顺序与依赖关系 |
| [上下文注入审计](2026-03-13-context-injection-audit.md) | 审计发现 (F001-F007) |
| [Architecture Document](../architecture.md) | 架构文档 |
| [Design Document](../design.md) | 详细设计文档 |
| [PRD](../plan/PRD.md) | 产品需求文档 |

## 完成标准

- [ ] 代码中不再存在 `_extract_task_from_state()` 主导任务语义
- [ ] `DualAgentNode` 不再构造 `{subject, task}` 包装
- [ ] `IndependentAgent.execute()` 不再需要从字符串恢复上下文结构
- [ ] 任一节点运行时，prompt 中能稳定看到节点名称、任务描述、必选章节
- [ ] 五个节点的 prompt 差异来自节点契约，而不仅仅是 persona

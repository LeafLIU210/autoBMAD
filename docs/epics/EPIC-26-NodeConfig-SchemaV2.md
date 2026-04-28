# Epic 26: 节点配置 Schema v2 全量升级

**Epic ID**: EPIC-26  
**关联方案**: [04-node-configuration-reform.md](../research/refactor-2026-03-26/04-node-configuration-reform.md)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 4-5 Days  
**Priority**: P0 - 关键路径（所有后续 Epic 的共同前置依赖）  
**取代**: EPIC-21-NodeLoader-Config-Refactor  

---

## 1. Epic Overview

### 1.1 Summary

将 NodeConfig 数据类和全部 5 个节点的配置文件直接升级到 Schema v2。新增 `task`（解决 `context_builder.py` 调用断层）、`runtime`（超时/重试）段落；修正 `evaluator.yaml` 字段名（`thresholds` → `threshold`）；为 `persona.json` 补充 `communication_style`、`critical_actions`、`memories` 字段。**不实现 v1/v2 双版本兼容**，所有配置直接升级为 v2 格式。

### 1.2 Business Value

- **消除代码-配置断层**: `context_builder.py` 调用 `node_config.task.get("name")` 不再回退到角色名
- **语义正确性**: `task_name` 从 "Analyst"（我是谁）变为 "create-business-analysis-report"（我要做什么）
- **配置一致性**: `threshold` 字段名全局统一，消除 5 处歧义
- **Agent 行为增强**: 新增 `communication_style`、`critical_actions`、`memories` 提升角色扮演一致性

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| `task_name` 为角色名的比例 | 0%（当前 100%） |
| 所有节点 `task.name` 非空 | 5/5 |
| `evaluator.yaml` 使用 `threshold`（单数） | 5/5 |
| `persona.json` 含 `communication_style` | 5/5 |
| 诊断工具真实完整度 | 95%+（当前假阳性 100%） |
| 代码-配置断层数 | 0（当前 3 处） |

### 1.4 Dependencies

- **Requires**: 无（Phase 1 起始任务）
- **Blocks**: EPIC-27（ContextValidator 依赖 NodeConfig.task）、EPIC-28（Task 契约消除依赖 NodeConfig）、EPIC-29（SDK 工具依赖 node.yaml tools 配置）

---

## 2. Architecture Context

### 2.1 Component Overview

```
NodeConfig v2 数据类:
  ┌─────────────────────────────────────┐
  │ NodeConfig                          │
  │  node_id, name, description, ...    │
  │  + task: NodeTaskConfig             │  ← 新增（解决 context_builder 断层）
  │  + runtime: NodeRuntimeConfig       │  ← 新增（超时/重试控制）
  │  + schema_version: "2.0"            │  ← 新增
  └─────────────────────────────────────┘

每个节点 3 文件升级:
  node.yaml     → + task{}, + runtime{}, + evaluator{inline}, + schema_version
  persona.json  → + communication_style, + critical_actions, + memories
  evaluator.yaml → thresholds→threshold, + max_iterations, + description per criteria
```

### 2.2 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `autoBMAD/nodes/loader.py` | **修改** | 新增 NodeTaskConfig、NodeRuntimeConfig 数据类；更新 NodeConfig 和解析逻辑 |
| `autoBMAD/nodes/{analyst,pm,ux,architect,po}/node.yaml` | **修改** | 升级到 v2 Schema |
| `autoBMAD/nodes/{analyst,pm,ux,architect,po}/persona.json` | **修改** | 新增 BMAD 字段 |
| `autoBMAD/nodes/{analyst,pm,ux,architect,po}/evaluator.yaml` | **修改** | 修正字段名，新增描述 |
| `tools/node_config_completeness_checker.py` | **修改** | 将 `task.name` 加入必填检查 |
| `autoBMAD/docuswarm/node_execution/context_builder.py` | **修改** | 从 NodeTaskConfig 对象读取（非 dict.get） |

---

## 3. User Stories

### Story 26.1: NodeConfig 数据类 v2 升级

**Story Points**: 3  
**Priority**: P0  
**Description**: As a developer, I want NodeConfig to have `task`, `runtime`, and `schema_version` fields, so that the data model matches what the code actually needs.

**Acceptance Criteria**:

- [ ] `loader.py` 新增 `NodeTaskConfig` 数据类（`name: str`, `description: str`, `role_supplement: str`）
- [ ] `loader.py` 新增 `NodeRuntimeConfig` 数据类（`timeout: int`, `retry_max_attempts: int`, `retry_backoff: float`）
- [ ] `NodeConfig` 新增 `schema_version: str`、`task: NodeTaskConfig`、`runtime: NodeRuntimeConfig` 字段
- [ ] `_build_node_config()` 直接解析 v2 格式（无 v1 兼容分支）
- [ ] `NodeEvaluatorConfig` 使用 `threshold`（单数）字段名
- [ ] `context_builder.py` 从 `node_config.task.name` 读取任务名（非 `dict.get`）
- [ ] 所有 loader、config 相关测试通过

**Technical Notes**:

- `NodeTaskConfig.name` 为必填字段，`description` 和 `role_supplement` 有默认值
- `context_builder.py` 第 62 行 `node_config.task.get("name", ...)` 改为 `node_config.task.name`
- 不实现 v1 回退逻辑：如果 `task` section 不存在，直接抛出配置错误

---

### Story 26.2: analyst 节点配置 v2 升级

**Story Points**: 2  
**Priority**: P0  
**Description**: As the pipeline, I want the analyst node fully configured with Schema v2, so that task semantics are correct and evaluation is properly parameterized.

**Acceptance Criteria**:

- [ ] `analyst/node.yaml` 包含 `schema_version: "2.0"`、`task.name: create-business-analysis-report`、`task.description`、`runtime`、`evaluator` 内联引用
- [ ] `analyst/persona.json` 包含 `communication_style`（分析型、精准型）、`critical_actions`（5 条）、`memories`（3 条）
- [ ] `analyst/evaluator.yaml` 字段名为 `threshold`（单数），每个 criteria 含 `description`，新增 `max_iterations: 3`
- [ ] `NodeLoader().load("analyst").task.name == "create-business-analysis-report"`

---

### Story 26.3: pm 节点配置 v2 升级

**Story Points**: 2  
**Priority**: P0

**Acceptance Criteria**:

- [ ] `pm/node.yaml` 包含 `task.name: create-product-requirements-document`
- [ ] `pm/persona.json` 的 `role` 从 "Project Manager" 修正为 "Product Manager"
- [ ] `pm/persona.json` 包含 `communication_style`、`critical_actions`、`memories`
- [ ] `pm/evaluator.yaml` 修正为 `threshold`（单数），新增 `max_iterations: 3`

---

### Story 26.4: ux 节点配置 v2 升级

**Story Points**: 2  
**Priority**: P0

**Acceptance Criteria**:

- [ ] `ux/node.yaml` 包含 `task.name: create-ux-design-specification`
- [ ] `ux/persona.json` 包含 `communication_style`、`critical_actions`（含线框图文本描述说明）、`memories`
- [ ] `ux/evaluator.yaml` 修正为 `threshold`（单数），新增 `max_iterations: 3`

---

### Story 26.5: architect 节点配置 v2 升级

**Story Points**: 2  
**Priority**: P0

**Acceptance Criteria**:

- [ ] `architect/node.yaml` 包含 `task.name: create-system-architecture-document`
- [ ] `architect/evaluator.yaml` 阈值调整：`approval: 0.75`（从 0.70 提高，9 章节复杂度补偿）
- [ ] `architect/persona.json` 包含 `communication_style`、`critical_actions`（含 trade-off 文档化要求）、`memories`

---

### Story 26.6: po 节点配置 v2 升级

**Story Points**: 2  
**Priority**: P0

**Acceptance Criteria**:

- [ ] `po/node.yaml` 包含 `task.name: create-epics-and-user-stories`
- [ ] `po/persona.json` 包含 `communication_style`、`critical_actions`、`memories`（含"最终节点"角色认知）
- [ ] `po/evaluator.yaml` 修正为 `threshold`（单数），新增 `max_iterations: 3`
- [ ] 创建 `_bmad/_config/agents/bmm-po.customize.yaml`（PO 独立 BMAD Agent 定义，不再与 PM 共用）

---

### Story 26.7: 诊断工具升级

**Story Points**: 1  
**Priority**: P1  
**Description**: As a developer, I want the config completeness checker to validate v2 schema fields, so that "100% completeness" is genuine, not false-positive.

**Acceptance Criteria**:

- [ ] `node_config_completeness_checker.py` 将 `task.name`、`task.description` 加入必填检查
- [ ] 检测 `evaluator.yaml` 使用 `threshold`（单数）而非 `thresholds`（复数）
- [ ] 检测 `persona.json` 包含 `communication_style` 字段
- [ ] 运行后所有 5 节点的真实完整度 ≥ 95%

---

## 4. 质量门禁

```bash
# 全部 Story 完成后执行
python -c "from autoBMAD.nodes.loader import NodeLoader; c = NodeLoader().load('analyst'); print(c.task.name)"
# 预期: "create-business-analysis-report"

python tools/node_config_completeness_checker.py
# 预期: 所有节点 task.name 存在且非空

python -m pytest tests/ -k "loader or config or context_builder" -v
basedpyright autoBMAD/nodes/loader.py
```

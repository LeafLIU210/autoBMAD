# Epic 28: Task 契约完全消除

**Epic ID**: EPIC-28  
**关联方案**: [03-task-contract-removal.md](../research/refactor-2026-03-26/03-task-contract-removal.md)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days  
**Priority**: P1 - Phase 2 核心架构重构  

---

## 1. Epic Overview

### 1.1 Summary

从 `NodeExecutionContext` 中彻底移除全部 6 个 Task 相关字段（`task_name`、`task_description`、`role_supplement`、`deliverable_type`、`deliverable_requirements`、`evaluator_criteria`），以 `persona.json` + `node.yaml` 作为单一配置真相源。所有消费端直接通过 `NodeLoader` 从配置文件读取。**不使用双读机制、不添加 DEPRECATED 注释、不保留 `NodeExecutionContextRequired` 基类**。

### 1.2 Business Value

- **消除三重 DRY 违反**: 修改节点配置只需改 1 个文件（当前需同步 3 处）
- **协议精简 44%**: `NodeExecutionContext` 从 16 字段缩减至 9 字段
- **代码精简 52%**: `contracts.py` 从 125 行缩减至约 60 行
- **语义纯净**: `NodeExecutionContext` 仅包含运行时动态数据，不含可静态配置的冗余

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| `NodeExecutionContext` 字段数 | 9（从 16 减少） |
| `contracts.py` 代码行数 | ≤ 70（从 125 减少） |
| 语义等价字段重复数 | 0（从 6 减少） |
| 修改节点配置需同步文件数 | 1（从 3 减少） |
| 完整端到端流水线通过 | Yes |

### 1.4 Dependencies

- **Requires**: EPIC-25（死字段 `persona_context` 和 `evaluator_criteria` 先清理）、EPIC-26（NodeConfig v2 提供 `task` 字段读取能力）
- **Blocks**: EPIC-30（集成验证）

---

## 2. Architecture Context

### 2.1 Component Overview

```
消除前:
  NodeExecutionContextBuilder.build()
    → 从 NodeConfig 读取 task_name, task_description 等
    → 写入 NodeExecutionContext（中间层）
    → isolation.py 从 NodeExecutionContext 取出
    → 传给 IndependentAgentInput / EvaluatorAgentInput

消除后:
  NodeExecutionContextBuilder.build()
    → 仅写入运行时字段（pipeline_id, node_id, contexts...）
  isolation.py / contract_builder.py / dual_agent.py
    → 需要 task 信息时直接 NodeLoader().load(node_id)
```

### 2.2 精简后的 NodeExecutionContext

```python
class NodeExecutionContext(TypedDict):
    # === 身份标识（运行时生成）===
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    # === 运行时上下文数据 ===
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]
    # === 迭代状态 ===
    iteration_feedback: dict[str, Any] | None
    # === 扩展上下文 ===
    docs_context: list[dict[str, Any]]
```

### 2.3 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `node_execution/contracts.py` | **修改** | 移除 6 个 Task 字段、删除 `NodeExecutionContextRequired` 基类、删除 `DeliverableRequirements` 类 |
| `node_execution/context_builder.py` | **修改** | 移除 Task 字段构建逻辑、删除 `_build_deliverable_requirements()` |
| `context/isolation.py` | **修改** | `build_independent_input` 和 `build_evaluator_input` 从 NodeLoader 直接读取 |
| `nodes/dual_agent.py` | **修改** | `task_name` 访问改为从 NodeConfig 读取 |
| `node_execution/executor.py` | **修改** | 日志中 `task_name` 改用 `node_name` |
| `prompts/contract_builder.py` | **修改** | `_build_task_section` 从 NodeLoader 直接读取 |

---

## 3. User Stories

### Story 28.1: NodeExecutionContext 精简为 9 字段

**Story Points**: 3  
**Priority**: P0  
**Description**: As a developer, I want NodeExecutionContext to only contain runtime-dynamic fields, so that static configuration is not redundantly passed through the protocol.

**Acceptance Criteria**:

- [ ] `contracts.py` 中 `NodeExecutionContextRequired` 基类**删除**
- [ ] `NodeExecutionContext` 合并为单一 TypedDict（9 字段）
- [ ] 已删除字段：`task_name`, `task_description`, `role_supplement`, `deliverable_type`, `deliverable_requirements`, `evaluator_criteria`
- [ ] `DeliverableRequirements` TypedDict **删除**
- [ ] `contracts.py` 行数 ≤ 70
- [ ] basedpyright 类型检查通过

**Technical Notes**:

- `DeliverableArtifact` 保留（运行时产物）
- `IndependentAgentInput` 和 `EvaluatorAgentInput` 保留（中间传递结构）
- `IndependentOutput` 和 `EvaluatorOutput` 类型别名保留

---

### Story 28.2: context_builder 移除 Task 字段构建

**Story Points**: 2  
**Priority**: P0  
**Description**: As the context builder, I want to stop constructing task-related fields, so that the builder only creates runtime context.

**Acceptance Criteria**:

- [ ] `NodeExecutionContextBuilder.build()` 不再构建 `task_name`, `task_description`, `role_supplement`, `deliverable_type`, `deliverable_requirements` 字段
- [ ] `_build_deliverable_requirements()` 方法**删除**
- [ ] 返回值仅包含 9 个运行时字段
- [ ] 相关单元测试更新

---

### Story 28.3: isolation.py 消费端迁移

**Story Points**: 3  
**Priority**: P0  
**Description**: As the isolation layer, I want to read task configuration directly from NodeLoader, so that I'm no longer dependent on NodeExecutionContext carrying redundant fields.

**Acceptance Criteria**:

- [ ] `build_independent_input` 中 `task_name`、`task_description`、`role_supplement`、`deliverable_requirements` 从 `NodeLoader().load(node_id)` 直接读取
- [ ] `build_evaluator_input` 中 `criteria` 从 `NodeLoader().load(node_id).evaluator` 读取（EPIC-25 Story 25.3 的延续确认）
- [ ] 不使用双读机制（无 `execution_context.get("task_name")` 回退）
- [ ] `tests/unit/context/test_isolation.py` 更新并全部通过

---

### Story 28.4: dual_agent 和 executor 消费端迁移

**Story Points**: 2  
**Priority**: P0  
**Description**: As the node execution layer, I want all task_name references updated to read from NodeConfig, so that the protocol change propagates to all consumers.

**Acceptance Criteria**:

- [ ] `dual_agent.py` 中 `execution_context["task_name"]` 的 3 处访问改为从 `NodeConfig.task.name` 读取
- [ ] `executor.py` 中日志记录的 `task_name=execution_context["task_name"]` 改为 `node_name=execution_context["node_name"]`
- [ ] `contract_builder.py` 的 `_build_task_section` 从 `NodeLoader` 直接读取 `task_name`、`task_description`、`role_supplement`
- [ ] 所有相关测试更新：`test_dual_agent.py`、`test_contract_builder.py` 中硬编码 `task_name` 断言移除或更新

---

## 4. 质量门禁

```bash
python -m pytest tests/ -k "isolation or contract or context_builder or dual_agent or executor" -v
basedpyright autoBMAD/docuswarm/node_execution/contracts.py
# 验证 contracts.py 行数
python -c "print(sum(1 for _ in open('autoBMAD/docuswarm/node_execution/contracts.py')))"
# 预期: ≤ 70
```

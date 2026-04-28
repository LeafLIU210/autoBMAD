# Epic 25: 死代码与死字段消除

**Epic ID**: EPIC-25  
**关联方案**: [02-memory-manager-removal.md](../research/refactor-2026-03-26/02-memory-manager-removal.md), [03-task-contract-removal.md](../research/refactor-2026-03-26/03-task-contract-removal.md)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 1 Day  
**Priority**: P0 - Phase 1 快速清理（无风险，立即执行）  
**取代**: EPIC-23-Deprecated-Code-Removal（部分覆盖）  

---

## 1. Epic Overview

### 1.1 Summary

消除代码库中已确认的死代码和无效字段。MemoryManager（179 行，外部调用数为 0）彻底删除；`IndependentAgentInput.persona_context`（始终为 `{}`）字段删除；`evaluator_criteria` 中转传递改为直接从 `evaluator.yaml` 加载。**不保留任何向后兼容代码**。

### 1.2 Business Value

- **代码库净化**: 移除 179 行死代码，消除对未来开发者的误导
- **协议精简**: 减少 `NodeExecutionContext` 无效字段传递
- **维护成本降低**: 消除对从未使用的三层内存模型的认知负担

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| MemoryManager 代码行数 | 0（文件删除） |
| `from ... import MemoryManager` 可用性 | `ImportError` |
| `IndependentAgentInput` 中 `persona_context` 字段 | 不存在 |
| `evaluator_criteria` 通过 NodeExecutionContext 传递 | 不存在（直接从 evaluator.yaml 加载） |
| 全量测试通过率 | 100% |

### 1.4 Dependencies

- **Requires**: 无（Phase 1 起始任务，可立即执行）
- **Blocks**: EPIC-28（Task 契约完全消除依赖死字段先清理）

---

## 2. Architecture Context

### 2.1 Component Overview

```
删除前:
  context/__init__.py ──import──→ context/memory.py (MemoryManager, MemoryScope)
  context_builder.py ──构建──→ evaluator_criteria ──传递──→ isolation.py ──写入──→ EvaluatorAgentInput
  isolation.py ──赋值 {}──→ IndependentAgentInput.persona_context

删除后:
  context/__init__.py             (memory.py 不存在，import 删除)
  isolation.py ──直接加载──→ NodeLoader → evaluator.yaml → criteria
  IndependentAgentInput           (无 persona_context 字段)
```

### 2.2 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `autoBMAD/docuswarm/context/memory.py` | **删除** | 179 行死代码，外部调用 0 |
| `autoBMAD/docuswarm/context/__init__.py` | **修改** | 移除 MemoryManager/MemoryScope 导入和 `__all__` 条目 |
| `autoBMAD/docuswarm/node_execution/contracts.py` | **修改** | 删除 `persona_context` 字段 |
| `autoBMAD/docuswarm/context/isolation.py` | **修改** | 删除 `persona_context={}` 赋值；`evaluator_criteria` 改为直接从 NodeLoader 加载 |
| `tests/architecture/test_context_exports.py` | **新增** | 保护性测试：验证导出完整性和 MemoryManager 不可导入 |

---

## 3. User Stories

### Story 25.1: MemoryManager 彻底删除

**Story Points**: 1  
**Priority**: P0  
**Description**: As a developer, I want MemoryManager completely removed from the codebase, so that dead code no longer misleads future contributors.

**Acceptance Criteria**:

- [ ] `autoBMAD/docuswarm/context/memory.py` 文件已物理删除
- [ ] `context/__init__.py` 中不再包含 `MemoryManager` 和 `MemoryScope` 的导入或 `__all__` 条目
- [ ] `python -c "from autoBMAD.docuswarm.context import MemoryManager"` 抛出 `ImportError`
- [ ] `python -c "from autoBMAD.docuswarm.context import ContextManager, ContextFilter"` 正常返回
- [ ] `grep -r "MemoryManager" autoBMAD/ --include="*.py"` 结果为空（诊断脚本除外）
- [ ] 全量测试套件通过

**Technical Notes**:

- 操作顺序：先修改 `__init__.py` 移除导入，再删除 `memory.py`（顺序不可颠倒）
- 137 个文件扫描确认外部调用数为 0，无级联风险
- 通过 git history 可随时恢复

---

### Story 25.2: persona_context 死字段删除

**Story Points**: 1  
**Priority**: P0  
**Description**: As a developer, I want the `persona_context` field removed from `IndependentAgentInput`, so that the protocol doesn't carry permanently empty data.

**Acceptance Criteria**:

- [ ] `contracts.py` 中 `IndependentAgentInput` 不再包含 `persona_context` 字段
- [ ] `isolation.py` 中 `build_independent_input` 不再赋值 `persona_context={}`
- [ ] 相关测试更新并通过
- [ ] basedpyright 类型检查通过

**Technical Notes**:

- `persona_context` 在 `isolation.py` 第 113 行被始终赋值为 `{}`
- 注释声明"由 IndependentAgent 自行加载"但实际从未消费
- 直接删除，不保留任何注释或占位符

---

### Story 25.3: evaluator_criteria 直接加载

**Story Points**: 2  
**Priority**: P0  
**Description**: As a developer, I want `evaluator_criteria` loaded directly from `evaluator.yaml` at the consumption point, so that it's no longer unnecessarily relayed through `NodeExecutionContext`.

**Acceptance Criteria**:

- [ ] `context/isolation.py` 的 `build_evaluator_input` 中 `criteria` 从 `NodeLoader().load(node_id).evaluator` 直接读取
- [ ] `context_builder.py` 中不再构建 `evaluator_criteria` 字段
- [ ] `NodeExecutionContext` 中不再包含 `evaluator_criteria` 可选字段
- [ ] 所有涉及 isolation、contract、context_builder 的测试通过
- [ ] basedpyright 类型检查通过

**Technical Notes**:

- `NodeLoader` 已有缓存机制（`_cache`），重复加载无性能影响
- `evaluator.yaml` 路径通过 `NodeLoader` 内部解析，无需消费端关心

---

### Story 25.4: 保护性测试

**Story Points**: 1  
**Priority**: P1  
**Description**: As a developer, I want architecture-level tests that verify the removal is complete, so that future changes don't accidentally re-introduce dead code.

**Acceptance Criteria**:

- [ ] `tests/architecture/test_context_exports.py` 验证 `context` 模块导出的所有必要符号
- [ ] 验证 `MemoryManager` 和 `MemoryScope` 不可从 `context` 模块导入
- [ ] 验证 `memory.py` 文件不存在于文件系统

---

## 4. 质量门禁

```bash
# Story 25.1-25.3 完成后执行
python -c "from autoBMAD.docuswarm.context import ContextManager, ContextFilter; print('context OK')"
python -m pytest tests/ -x -q --tb=short
basedpyright autoBMAD/docuswarm/context/
```

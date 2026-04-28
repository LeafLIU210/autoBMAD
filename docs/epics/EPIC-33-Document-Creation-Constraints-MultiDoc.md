# EPIC-33: Document Creation Constraints and Multi-Document Support

**Epic ID**: EPIC-33  
**Source Research**: `docs/research/docuswarm-deep-reform/03-document-creation-constraints.md`  
**Recommended Solution**: Method C - Validator-based constraint enforcement + backward-compatible multi-document wrapping  
**Priority**: P0 (Phase 1-3 mandatory) / P1 (Phase 4-5 optional)  
**Estimated Effort**: 9.5 weeks (Phase 1-3: 3-4w, Phase 4-5: 4-5w, Phase 6: 1w)  
**Status**: ❌ NOT STARTED (0% complete as of 2026-04-07)  
**Research Baseline**: `docs/research/2026-04-07-nodes-tech-debt-dependency-analysis.md`

---

## Overview

DocuSwarm's five nodes have different document creation requirements: Analyst/PM/UX should each create exactly 1 document, while Architect and PO need to create 2-5 related documents. Currently, `CreateDeliverableTool` is single-document by design with no count constraints. This epic implements document count constraints (Method C: Validator-level checks) and multi-document support (backward-compatible wrapping).

> **⚠️ 2026-04-07 技术债分析结论（TD-003）**：本 Epic 是 8 个 EPIC 中**实现进度最低**（0%）、**架构改动最重**的一个。`NodeResult.deliverable` 当前是单一 `dict[str, Any]`，架构层面完全不支持多文档。必须从 `NodeDeliverableConfig`（数据层）→ `CreateDeliverableParams`（工具层）→ `Validator`（验证层）→ `NodeResult`（合约层）→ `orchestrator.py`（流水线层）逐层扩展，**不可跳过任意层级**。
>
> **关键路径约束**：`NodeDeliverableConfig` 扩展必须在 `autoBMAD/nodes/loader.py`（权威版）完成，旧版 `nodes/loader.py` 已废弃，不得修改。

## Problem Statement

| Node | Required Documents | Current System |
|------|-------------------|---------------|
| analyst | 1 (product brief) | No constraint ❌ |
| pm | 1 (PRD) | No constraint ❌ |
| ux | 1 (UX design spec) | No constraint ❌ |
| architect | 2-4 (arch doc, API design, DB schema, etc.) | No multi-doc ❌ |
| po | 3-5 (product vision, roadmap, epics, stories) | No multi-doc ❌ |

**Current Weaknesses**:
- `CreateDeliverableTool` is single-document design
- `NodeResult` can only return one deliverable object
- `node.yaml` cannot declare count constraints
- `Validator` cannot check document count

**2026-04-07 实际代码状态确认（逐 Story）**：

| Story | 文件 | 状态 | 备注 |
|-------|------|------|------|
| 33.1 | `autoBMAD/docuswarm/tools/create_deliverable.py` | ❌ 未实现 | `CreateDeliverableParams` 无 `document_index`, `document_total`, `document_type` |
| 33.2 | `autoBMAD/docuswarm/context/validator.py` | ❌ 未实现 | 无 `max_deliverables` 验证规则 |
| 33.3 | `autoBMAD/nodes/*/node.yaml` | ❌ 未实现 | 所有 5 个节点无 `deliverable.max_deliverables` 配置 |
| 33.4 | `autoBMAD/docuswarm/templates/` | ❌ 未实现 | 无 `architect_templates.yaml`, `po_templates.yaml` |
| 33.5 | `autoBMAD/docuswarm/node_execution/contracts.py` | ❌ 未实现 | `NodeResult` 无多文档字段 |
| 33.6 | `autoBMAD/docuswarm/pipeline/orchestrator.py` | ❌ 未实现 | 无多文档收集逻辑 |
| 33.7 | `autoBMAD/nodes/architect/node.yaml`, `po/node.yaml` | ❌ 未实现 | 无 `max_deliverables` 和 `document_types` |
| 33.8 | `autoBMAD/docuswarm/prompts/contract_builder.py` | ❌ 未实现 | 无文档数量引导提示 |
| 33.9 | `tests/test_document_creation_constraints.py` | ❌ 未实现 | 测试文件不存在 |

## Goals

### Phase 1-3 (Mandatory - Low Risk)
1. Add `max_deliverables` parameter to `CreateDeliverableParams`
2. Add `max_deliverables` rule to Validator
3. Add `deliverable.max_deliverables` config to `node.yaml` for analyst/pm/ux
4. End-to-end test for single-document constraint enforcement

### Phase 4-5 (Optional - Medium Risk)
5. Add `document_index`, `document_total`, `document_type` to `CreateDeliverableParams`
6. Extend `NodeResult` with `is_multi_document`, `all_documents`, `total_word_count`
7. Implement backward-compatible multi-document wrapping
8. Support multi-document workflow for architect/po nodes

### Phase 6 (Supporting)
9. Template alignment and developer documentation

## Recommended Solution: Method C (Three-Layer Constraint)

**Three-Layer Architecture**:
1. **Config Layer**: `node.yaml` declares `deliverable.max_deliverables: 1`
2. **Validation Layer**: Validator checks deliverable count against `max_deliverables`
3. **Execution Layer**: SDK auto-enforces on tool call

**Multi-Document Format** (backward-compatible wrapping):
```json
{
  "deliverable": {
    "title": "Deliverables Set",
    "type": "multi-document",
    "documents": [
      {"index": 1, "type": "epic-list", "file_path": "...", "sha256": "..."},
      {"index": 2, "type": "story-prioritization", "file_path": "...", "sha256": "..."}
    ]
  }
}
```

## Stories

### Story 33.1: Extend CreateDeliverableParams
**File**: `autoBMAD/docuswarm/tools/create_deliverable.py`  
**Changes**:
- Add optional fields to `CreateDeliverableParams`:
  - `document_index: int | None = None` - position in document set
  - `document_total: int | None = None` - total documents in set
  - `document_type: str | None = None` - document type identifier

**Acceptance Criteria**:
- [ ] New optional fields added with defaults `None`
- [ ] Existing callers without these fields still work
- [ ] Unit tests verify parameter validation
- [ ] Returned metadata includes new fields when provided

### Story 33.2: Add max_deliverables Validation to Validator
**File**: `autoBMAD/docuswarm/context/validator.py`  
**Changes**:
- Add `max_deliverables` rule check in deliverable validation
- Read `max_deliverables` from node config
- If deliverable count exceeds limit, return validation failure
- Run new/old validation rules in parallel (not replacing existing)

**Acceptance Criteria**:
- [ ] Validator reads `node.yaml`'s `deliverable.max_deliverables`
- [ ] Single-doc nodes (analyst/pm/ux) fail on 2nd deliverable
- [ ] Multi-doc nodes (architect/po) pass with multiple deliverables
- [ ] Existing `file_path`/`sha256` validation still works
- [ ] Integration test verifies constraint enforcement

### Story 33.3: Update node.yaml for Single-Document Constraint Nodes
**Files**: `autoBMAD/nodes/analyst/node.yaml`, `autoBMAD/nodes/pm/node.yaml`, `autoBMAD/nodes/ux/node.yaml`  

> **⚠️ 路径修正（TD-001）**：原文档指向 `nodes/*/node.yaml`（已废弃目录）。实际 `NodeLoader` 从 `autoBMAD/nodes/` 读取配置，**必须修改 `autoBMAD/nodes/` 下的文件**。`nodes/` 目录的任何修改均不影响实际执行行为。

**Changes**:
```yaml
deliverable:
  max_deliverables: 1
  required_sections:
    - [node-specific sections]
```

**前置条件**：Story 33.1（`NodeDeliverableConfig` 扩展）必须先完成，否则 `autoBMAD/nodes/loader.py` 无法解析 `max_deliverables` 字段。

**Acceptance Criteria**:
- [ ] `autoBMAD/nodes/analyst/node.yaml` has `deliverable.max_deliverables: 1`
- [ ] `autoBMAD/nodes/pm/node.yaml` has `deliverable.max_deliverables: 1`
- [ ] `autoBMAD/nodes/ux/node.yaml` has `deliverable.max_deliverables: 1`
- [ ] YAML validation passes for all files
- [ ] System prompt clearly guides LLM: "Create exactly 1 deliverable"

### Story 33.4: Add Template Files for Architect and PO
**Files**: 
- `autoBMAD/docuswarm/templates/architect_templates.yaml` (new)
- `autoBMAD/docuswarm/templates/po_templates.yaml` (new)  
**Changes**:
- Create template definitions for architect's multiple deliverables (system architecture, API design, database schema)
- Create template definitions for PO's multiple deliverables (product vision, roadmap, epic list, story list)

**Acceptance Criteria**:
- [ ] `architect_templates.yaml` defines 2-4 document types with required sections
- [ ] `po_templates.yaml` defines 3-5 document types with required sections
- [ ] Templates follow existing YAML format
- [ ] Template loader can read new files

### Story 33.5: Extend NodeResult for Multi-Document Support
**File**: `autoBMAD/docuswarm/node_execution/contracts.py` or equivalent NodeResult location  
**Changes** (backward-compatible):
- Add convenience properties to NodeResult:
  - `is_multi_document: bool` - True if deliverable is multi-document type
  - `all_documents: list[dict]` - flattened list of all document entries
  - `total_word_count: int` - sum of all documents' word counts

**Acceptance Criteria**:
- [ ] Existing single-doc consumers still work (existing `deliverable` field unchanged)
- [ ] Multi-doc consumers can use `all_documents` to iterate documents
- [ ] `is_multi_document` correctly identifies multi-doc format
- [ ] Unit tests cover both single and multi-doc cases

### Story 33.6: Implement Multi-Document Collection in Orchestrator
**File**: `autoBMAD/docuswarm/pipeline/orchestrator.py`  
**Changes**:
- Update orchestrator to collect multiple deliverables per node
- Handle multi-document wrapping format in pipeline state
- Update downstream node's `chained_deliverables` to include all documents

**Acceptance Criteria**:
- [ ] Orchestrator collects all documents when `type: "multi-document"`
- [ ] `chained_deliverables` for next node includes all preceding documents
- [ ] Pipeline state correctly stores multi-doc format
- [ ] Integration test with architect node producing 2 documents

### Story 33.7: Update Architect and PO node.yaml for Multi-Document
**Files**: `autoBMAD/nodes/architect/node.yaml`, `autoBMAD/nodes/po/node.yaml`  

> **⚠️ 路径修正（TD-001）**：原文档指向 `nodes/architect/node.yaml` 和 `nodes/po/node.yaml`（废弃目录）。权威配置文件位于 `autoBMAD/nodes/`。

**Changes**:
```yaml
# architect
deliverable:
  max_deliverables: 4
  document_types:
    - system-architecture
    - api-design
    - database-schema

# po
deliverable:
  max_deliverables: 5
  document_types:
    - product-vision
    - roadmap
    - epic-list
    - story-list
```

**Acceptance Criteria**:
- [ ] `autoBMAD/nodes/architect/node.yaml` allows multiple deliverables
- [ ] `autoBMAD/nodes/po/node.yaml` allows multiple deliverables
- [ ] Document types are defined and validated
- [ ] System prompt guides LLM to create appropriate number of documents

### Story 33.8: System Prompt Guidance for Document Counts
**Files**: `autoBMAD/docuswarm/prompts/contract_builder.py`  
**Changes**:
- Add document count guidance to system prompt based on `deliverable.max_deliverables`
- For single-doc: "Create exactly 1 deliverable using create_deliverable tool"
- For multi-doc: "Create {min}-{max} deliverables using create_deliverable tool for each"

**Acceptance Criteria**:
- [ ] System prompt includes document count guidance
- [ ] Guidance is clear and actionable for LLM
- [ ] Unit test verifies prompt content

### Story 33.9: End-to-End Tests for Constraints
**File**: `tests/test_document_creation_constraints.py` (new)  
**Test cases**:
- Single-doc: analyst/pm/ux fail gracefully on 2nd deliverable
- Multi-doc: architect/po succeed with multiple deliverables
- Backward compat: existing single-doc flow unchanged

**Acceptance Criteria**:
- [ ] All constraint tests pass
- [ ] No regression in existing single-doc flow
- [ ] Multi-doc wrapping format validates correctly

## Implementation Phases

### Phase 1: Parameter Extension (Week 1-2)
- Story 33.1: Extend `CreateDeliverableParams`
- Unit tests for parameter validation
- **Checkpoint**: Unit tests pass by end of Week 2

### Phase 2: Validator Enhancement (Week 2-3)
- Story 33.2: Add `max_deliverables` rule to Validator
- **Checkpoint**: Validator integration tests pass by end of Week 4

### Phase 3: Single-Document Constraint (Week 3-5)
- Story 33.3: Update analyst/pm/ux node.yaml
- Story 33.8: Add system prompt guidance
- **Checkpoint**: Single-doc constraint end-to-end test passes by end of Week 5

### Phase 4: Multi-Document Support (Week 5-8)
- Story 33.4: Template files for architect/po
- Story 33.5: Extend NodeResult
- Story 33.6: Orchestrator multi-doc collection
- Story 33.7: Update architect/po node.yaml
- **Checkpoint**: Multi-doc workflow (at least PO node) working by end of Week 7

### Phase 5: Template Alignment (Week 8-9)
- Story 33.9: End-to-end tests
- Documentation and training
- **Checkpoint**: Template alignment and docs complete by end of Week 9

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Backward compatibility break | High | Use wrapping approach (never change existing `deliverable` field) |
| Validator complexity increase | Medium | Separate validation logic into distinct rules |
| LLM confused by new parameters | Medium | Clear system prompt guidance; provide JSON format examples |
| Database query performance | Low | Limit document count; add index |

## Key Success Factors

1. **Clear System Prompt Guidance**: Explicitly tell LLM how many documents each node creates
2. **Progressive Validator Extension**: Run new rules alongside old ones, not replacing
3. **Comprehensive Test Coverage**: Single-doc, multi-doc, constraint violation, retry scenarios

## Files Changed

> **⚠️ 路径说明（TD-001）**：所有 `node.yaml` 修改均需在 `autoBMAD/nodes/` 目录下进行。`nodes/` 目录已废弃，`NodeLoader` 不会读取其配置。

**架构层扩展顺序（必须严格按序）**：
1. `autoBMAD/nodes/loader.py`：扩展 `NodeDeliverableConfig`（新增 `max_deliverables: int = 1`）
2. `autoBMAD/docuswarm/tools/create_deliverable.py`：扩展 `CreateDeliverableParams`
3. `autoBMAD/docuswarm/context/validator.py`：添加 `max_deliverables` 验证规则
4. `autoBMAD/nodes/*/node.yaml`：添加 `deliverable.max_deliverables` 配置
5. `autoBMAD/docuswarm/node_execution/contracts.py`：扩展 `NodeResult`
6. `autoBMAD/docuswarm/pipeline/orchestrator.py`：添加多文档收集逻辑

| File | Change Type | Priority |
|------|------------|------|
| `autoBMAD/nodes/loader.py` | **Extend（新增 max_deliverables 字段）** | **P0（前置依赖）** |
| `autoBMAD/docuswarm/tools/create_deliverable.py` | Extend | P0 |
| `autoBMAD/docuswarm/context/validator.py` | Enhance | P0 |
| `autoBMAD/docuswarm/prompts/contract_builder.py` | Update | P1 |
| `autoBMAD/docuswarm/node_execution/contracts.py` | Extend | P1 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Update | P1 |
| `autoBMAD/docuswarm/templates/architect_templates.yaml` | New | P1 |
| `autoBMAD/docuswarm/templates/po_templates.yaml` | New | P1 |
| `autoBMAD/nodes/analyst/node.yaml` | Config | P0 |
| `autoBMAD/nodes/pm/node.yaml` | Config | P0 |
| `autoBMAD/nodes/ux/node.yaml` | Config | P0 |
| `autoBMAD/nodes/architect/node.yaml` | Config | P1 |
| `autoBMAD/nodes/po/node.yaml` | Config | P1 |
| `tests/test_document_creation_constraints.py` | New | P1 |

## 已废弃路径（勿修改）

| 废弃路径 | 原因 | 正确路径 |
|---------|------|--------|
| `nodes/analyst/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/analyst/node.yaml` |
| `nodes/pm/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/pm/node.yaml` |
| `nodes/ux/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/ux/node.yaml` |
| `nodes/architect/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/architect/node.yaml` |
| `nodes/po/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/po/node.yaml` |

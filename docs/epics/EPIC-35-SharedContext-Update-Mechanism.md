# EPIC-35: Shared Context Update Mechanism Enhancement

**Epic ID**: EPIC-35  
**Source Research**: `docs/research/docuswarm-deep-reform/05-shared-context-update-mechanism.md`  
**Recommended Solution**: Method A - Retain and enhance existing `update_context` tool; add DB refresh in executor.py; add version control  
**Priority**: P0 (DB refresh) / P1 (version control) / P2 (change history)  
**Estimated Effort**: 8-12 days  
**Status**: ⚠️ P0 已完成，P1/P2 未实现（~30% complete as of 2026-04-07）  
**Research Baseline**: `docs/research/2026-04-07-nodes-tech-debt-dependency-analysis.md`

---

## Overview

DocuSwarm's `shared_context` is a cross-node shared dictionary in `PipelineState`. The existing `update_context.py` tool provides set/append/remove operations with whitelist protection. This epic enhances the mechanism by: (1) fixing a critical issue where executor.py doesn't refresh `shared_context` from DB after tool calls, (2) adding version control for optimistic locking, and (3) making the whitelist configurable per-node.

> **⚠️ 2026-04-07 实现状态汇总（逐 Story）**：
>
> | Story | 文件 | 状态 | 备注 |
> |-------|------|------|------|
> | 35.1 | `autoBMAD/docuswarm/node_execution/executor.py` | ✅ **P0 已完成** | `_refresh_shared_context_from_db()` 已在第360行实现 |
> | 35.2 | `autoBMAD/nodes/*/node.yaml` | ❌ 未实现 | 5个节点均无 `tools.shared_context` 配置段 |
> | 35.3 | `autoBMAD/nodes/loader.py` | ❌ 未实现 | 无 `NodeSharedContextConfig` dataclass |
> | 35.4 | `autoBMAD/docuswarm/tools/update_context.py` | ❌ 未实现 | 无版本控制逻辑 |
> | 35.5 | `autoBMAD/docuswarm/tools/update_context.py` | ❌ 未实现 | whitelist 仍为硬编码 |
> | 35.6 | `autoBMAD/docuswarm/storage/state_manager.py` | ❌ 未实现 | 无 `shared_context_history` 表 |
> | 35.7 | `tests/test_shared_context.py` | ❌ 未实现 | 测试文件不存在 |

## Problem Statement

**Current State**:
- `shared_context` is persisted in SQLite (WAL mode) via `StateManager.update_shared_context()`
- `update_context` tool writes directly to SQLite (not in-memory)
- **Critical Bug**: When a node completes, `graph.py` returns the in-memory state which may not contain the tool's DB writes
- Whitelist is hardcoded: `facts.*`, `decisions.*`, `open_questions`, `doc_summaries.*`, `notes`
- No version control → concurrent/retry scenarios can lose updates

**Data Flow Issue**:
```
IndependentAgent calls update_context tool
    ↓ Tool writes to SQLite directly
    ↓ (In-memory state NOT updated)
Node completes, graph.py returns in-memory state
    ↓ shared_context = OLD value (before tool calls)
Next node receives stale shared_context
```

## Goals

### P0 (Immediate - 1 week)
1. Fix `executor.py`: refresh `shared_context` from DB after node execution
2. Add `shared_context` configuration section to all node.yaml files
3. Write integration tests for shared context persistence

### P1 (Short-term - 1 week)
4. Add version control (timestamp + version number) to `UpdateContextTool`
5. Make whitelist configurable per-node via node.yaml

### P2 (Medium-term - 1 month)
6. Implement change history table in StateManager
7. Add fine-grained permission control (tool-level, data-level, operation-level)
8. Performance optimization (caching latest state)

## Recommended Solution: Method A (Retain and Enhance)

**Core Improvements**:
1. **DB Refresh** (P0): In `executor.py`, after node execution, read latest `shared_context` from DB
2. **Version Control** (P1): Add `_metadata.version` and `_metadata.updated_at` tracking
3. **Configurable Whitelist** (P1): Allow per-node configuration of allowed keys
4. **Change History** (P2): Record all operations for audit and rollback

## Stories

### Story 35.1: Fix executor.py - Refresh shared_context from DB
**File**: `autoBMAD/docuswarm/node_execution/executor.py`  

> **✅ 已完成（P0）**：`_refresh_shared_context_from_db()` 函数已存在（第360行），吸收 DB 刺新逻辑已实现。仅需验证其行为正确性即可。

**Changes**:
```python
# After node execution, refresh shared_context from DB
try:
    latest_state = state_manager.get_pipeline(pipeline_id)
    if latest_state and "state_json" in latest_state:
        persisted = json.loads(latest_state["state_json"])
        new_state["shared_context"] = persisted.get("shared_context", {})
except Exception:
    pass  # Use in-memory version as fallback
```

**Acceptance Criteria** (已完成，验证项):
- [x] executor.py refreshes `shared_context` from DB after node completes
- [x] Fallback to in-memory version if DB read fails
- [ ] Integration test: node A updates context → node B receives updated context
- [ ] Performance impact < 10ms per node (single DB read)

### Story 35.2: Add shared_context Configuration to node.yaml Files
**Files**: All 5 `autoBMAD/nodes/*/node.yaml`  

> **⚠️ 路径修正（TD-001）**：原文描述指向 `nodes/*/node.yaml`（废弃）。**必须修改 `autoBMAD/nodes/*/node.yaml`**。
> **前置条件**：Story 35.3（`NodeSharedContextConfig` dataclass）必须先完成，否则 `autoBMAD/nodes/loader.py` 无法解析此配置段。

**Changes**:
```yaml
tools:
  # ... existing tools config ...
  shared_context:
    enabled: true
    operations: ["set", "append", "remove"]
    # Optional: per-node whitelist override (default: uses global whitelist)
    # allowed_keys:
    #   - "facts.*"
    #   - "decisions.*"
```

**Acceptance Criteria**:
- [ ] All 5 `autoBMAD/nodes/*/node.yaml` have `tools.shared_context` section
- [ ] `enabled: true` flag controls whether node can update shared context
- [ ] YAML validation passes
- [ ] NodeLoader correctly parses shared_context permissions

### Story 35.3: Extend NodeToolPermissions with SharedContext Config
**File**: `autoBMAD/nodes/loader.py`  

> **注意**：必须修改 `autoBMAD/nodes/loader.py`（权威版），而非 `nodes/loader.py`（废弃旧版）。

**Changes**:
- Add `NodeSharedContextConfig` dataclass with `enabled`, `operations`, `allowed_keys`
- Add `shared_context: NodeSharedContextConfig` to `NodeToolPermissions`
- Parse from node.yaml `tools.shared_context` section

**Acceptance Criteria**:
- [ ] `NodeSharedContextConfig` dataclass exists in `autoBMAD/nodes/loader.py`
- [ ] Default: `enabled=True`, all operations allowed, uses global whitelist
- [ ] Backward compatible (nodes without `shared_context` config use defaults)
- [ ] Unit tests verify parsing

### Story 35.4: Add Version Control to UpdateContextTool
**File**: `autoBMAD/docuswarm/tools/update_context.py`  
**Changes**:
- After successful update, increment `shared_context._metadata.version`
- Add `_metadata.updated_at` timestamp
- Return new version info in `ToolResult`

```python
# Tool return value enhanced
{
  "success": True,
  "operation": "set",
  "key": "facts.market_scope",
  "previous_value": {...},
  "new_value": {...},
  "message": "Context updated",
  "timestamp": "2026-04-06T10:30:45Z",
  "version": "v1_1712404245123"
}
```

**Acceptance Criteria**:
- [ ] Each update increments `_metadata.version`
- [ ] `_metadata.updated_at` is set to current ISO timestamp
- [ ] Version info is returned in ToolResult
- [ ] Unit tests verify version increment behavior
- [ ] Backward compatible (existing `shared_context` without `_metadata` still works)

### Story 35.5: Make Whitelist Configurable in UpdateContextTool
**File**: `autoBMAD/docuswarm/tools/update_context.py`  
**Changes**:
- Accept optional `allowed_keys` parameter from node config
- If node provides `allowed_keys`, merge with global whitelist
- Log which whitelist is active

**Current Global Whitelist**:
- `facts.*`
- `decisions.*`
- `open_questions`
- `doc_summaries.*`
- `notes`

**Acceptance Criteria**:
- [ ] `UpdateContextTool` accepts configurable `allowed_keys`
- [ ] Node-specific keys are merged with global whitelist (not replacing)
- [ ] Attempts to update non-whitelisted keys fail with clear error
- [ ] Unit tests cover: global whitelist, node-specific keys, rejection

### Story 35.6: Add Change History Table in StateManager (P2)
**File**: `autoBMAD/docuswarm/storage/state_manager.py`  
**Changes**:
- New table `shared_context_history` with: `pipeline_id`, `node_id`, `operation`, `key`, `old_value`, `new_value`, `timestamp`, `version`
- Record every successful `update_shared_context()` call
- Provide `get_context_history(pipeline_id)` query method

**Acceptance Criteria**:
- [ ] Schema migration creates `shared_context_history` table
- [ ] Every successful context update is recorded
- [ ] History query returns sorted results (newest first)
- [ ] Unit tests for history recording and retrieval

### Story 35.7: Integration Tests for Shared Context
**File**: `tests/test_shared_context.py` (new)  
**Test cases**:
- `test_shared_context_persists_across_nodes()` - node A writes → node B reads
- `test_whitelist_blocks_unauthorized_keys()` - writes to non-whitelisted keys fail
- `test_version_increments_on_update()` - version number increments
- `test_context_refresh_from_db()` - executor refreshes from DB correctly
- `test_concurrent_writes_safe()` - multiple writes don't corrupt data

**Acceptance Criteria**:
- [ ] All 5 test cases pass
- [ ] Cross-node context propagation verified
- [ ] Whitelist enforcement verified
- [ ] Version control verified

## Concurrency Safety Analysis

**Current execution model**: 5 nodes execute strictly sequentially (no parallelism)

| Scenario | Concurrency | Risk | Notes |
|---------|------------|------|-------|
| Single pipeline retry | No | Low | Same thread, sequential |
| Multiple pipelines | Yes | Low | Different DB rows, no conflict |
| Pipeline pause/resume | No | Medium | Need checkpoint consistency |

**Conclusion**: Short-term keep current design; medium-term add version control.

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| DB refresh introduces latency | Medium | < 10ms; add caching if needed |
| Version control adds new logic complexity | Medium | Separate version logic from business logic |
| Whitelist configuration error | Medium | Schema validation; clear error messages |
| Privacy leak (all agents can read) | Medium | Whitelist for writes; structured data format |

## Implementation Phases

### Phase 1: Critical Fix (Week 1)
- Story 35.1: executor.py DB refresh (P0)
- Story 35.2: node.yaml shared_context config (P0)
- Story 35.3: NodeToolPermissions extension (P0)
- Story 35.7: Integration tests

### Phase 2: Version Control (Week 2)
- Story 35.4: Version control in UpdateContextTool (P1)
- Story 35.5: Configurable whitelist (P1)
- Updated unit tests

### Phase 3: Change History (Month 2)
- Story 35.6: Change history table (P2)
- Performance optimization
- Complete audit documentation

## Files Changed

> **⚠️ 路径说明（TD-001）**：所有 `node.yaml` 修改均需在 `autoBMAD/nodes/` 目录下进行。`nodes/` 目录已废弃，`NodeLoader` 不会读取其配置。

| File | Change Type | Priority |
|------|------------|------|
| `autoBMAD/docuswarm/node_execution/executor.py` | Fix | **✅ P0 已完成** |
| `autoBMAD/docuswarm/tools/update_context.py` | Enhance | P1 |
| `autoBMAD/docuswarm/storage/state_manager.py` | Extend | P2 |
| `autoBMAD/nodes/loader.py` | Extend | P0 |
| `autoBMAD/nodes/analyst/node.yaml` | Config | P1 |
| `autoBMAD/nodes/pm/node.yaml` | Config | P1 |
| `autoBMAD/nodes/ux/node.yaml` | Config | P1 |
| `autoBMAD/nodes/architect/node.yaml` | Config | P1 |
| `autoBMAD/nodes/po/node.yaml` | Config | P1 |
| `tests/test_shared_context.py` | New | P0 |

## 已废弃路径（勿修改）

| 废弃路径 | 原因 | 正确路径 |
|---------|------|--------|
| `nodes/analyst/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/analyst/node.yaml` |
| `nodes/pm/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/pm/node.yaml` |
| `nodes/ux/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/ux/node.yaml` |
| `nodes/architect/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/architect/node.yaml` |
| `nodes/po/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/po/node.yaml` |

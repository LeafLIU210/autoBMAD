# EPIC-34: Tool Permissions Full Open Access

**Epic ID**: EPIC-34  
**Source Research**: `docs/research/docuswarm-deep-reform/04-tool-permissions-configuration.md`  
**Recommended Solution**: Update all 5 node.yaml files with unified tools configuration; keep EvaluatorAgent tool-free  
**Priority**: P0  
**Estimated Effort**: 5-7 days  
**Status**: ⚠️ PARTIAL (~70% complete as of 2026-04-07) — analyst/architect 配置不完整  
**Depends On**: EPIC-31 (for skills config section), EPIC-32 (for node.yaml structure)  
**Research Baseline**: `docs/research/2026-04-07-nodes-tech-debt-dependency-analysis.md`

---

## Overview

Currently, all 5 nodes (analyst, pm, ux, architect, po) may lack proper `tools` configuration in their `node.yaml`, causing only `create_deliverable` to be available while the other 4 tools (`read_document`, `list_documents`, `grep_search`, `glob_search`) remain inaccessible. This epic upgrades all nodes to full tool access, while keeping EvaluatorAgent in its "tool-free" design for security isolation.

> **⚠️ 2026-04-07 关键发现（TD-001 + TD-002）**：
> - 本 Epic 所有 Stories 原文指向 `nodes/*/node.yaml`（已废弃目录），**实际 `NodeLoader` 从 `autoBMAD/nodes/` 读取配置**。所有修改必须在 `autoBMAD/nodes/` 下进行。
> - `autoBMAD/nodes/analyst/node.yaml` 和 `autoBMAD/nodes/architect/node.yaml` 已有完整 tools 配置；而 `nodes/analyst/node.yaml` 和 `nodes/architect/node.yaml`（废弃）仅有 `tools.skills`，**缺少 `allowed_builtin_tools` 和 `file_permissions`**。

## Problem Statement

**2026-04-07 实际代码状态确认**：

**`autoBMAD/nodes/`（权威目录）实际状态**：

| 节点 | allowed_builtin_tools | file_permissions | search_permissions | 状态 |
|------|----------------------|-----------------|--------------------|---------|
| analyst | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |
| pm | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |
| ux | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |
| architect | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |
| po | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |

**`nodes/`（废弃目录）实际状态**（仅供参考，不影响执行）：

| 节点 | allowed_builtin_tools | file_permissions | search_permissions | 状态 |
|------|----------------------|-----------------|--------------------|---------|
| analyst | ❌ 缺失 | ❌ 缺失 | ❌ 缺失 | ❌ 不完整 |
| pm | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |
| ux | ⚠️ 部分 | ⚠️ 部分 | ⚠️ 部分 | ⚠️ 需验证 |
| architect | ❌ 缺失 | ❌ 缺失 | ❌ 缺失 | ❌ 不完整 |
| po | ✅ 已配置 | ✅ 已配置 | ✅ 已配置 | ✅ 完整 |

> **核心问题**：`NodeLoader` 实际执行时读取 `autoBMAD/nodes/` 配置。`autoBMAD/nodes/` 中所有层已有完整 tools 配置，但 `nodes/` 中的 analyst/architect 缺配置可能导致调试时路径混淡。Story 34.6（工具日志）和 Story 34.7（系统提示）未确认完成。

**Current State** (per original research):
| Node | allowed_builtin_tools | file_read_dirs | search_dirs | Status |
|------|----------------------|----------------|------------|---------|
| analyst | ["Read", "Glob"] | docs/, docs/research/ | docs/ | Configured |
| pm | ["Read", "Glob"] | docs/ | docs/ | Configured |
| ux | ["Read", "Glob"] | docs/ | docs/ | Configured |
| architect | ["Read", "Glob"] | docs/ | docs/ | Configured |
| po | ["Read", "Glob"] | docs/ | docs/ | Configured |

**Issues**:
- If nodes lack `tools` config, only `create_deliverable` is available via `output_dir` auto-enable
- Missing read/search tools reduces Agent's context understanding ability
- No explicit system prompt guidance about available tools

**Key Decision**: EvaluatorAgent remains tool-free (no changes needed):
- Context isolation is easier to verify
- Evaluator's job is scoring, not document collection
- Avoids introducing security risks

## Goals

1. Ensure all 5 node.yaml files have complete, correct `tools` configuration
2. Simplify file_permissions to use root `docs/` covering all subdirectories
3. Update system prompt to mention all available tools
4. Add verification that tool configuration is logged at startup
5. Maintain EvaluatorAgent's tool-free design (no changes)

## Recommended Solution: Unified Full Access Configuration

```yaml
# All nodes: unified configuration
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]  # Simplified: root covers all subdirs
  search_permissions:
    search_dirs: ["docs/"]
```

**Security preserved by**:
- PathValidator: directory whitelist + symlink resolution + prefix matching
- File type whitelist (allowed extensions)
- File type blacklist (blocked extensions: .db, .sqlite, .key, .pem, etc.)
- Directory pattern blocking (.git, .env, node_modules, __pycache__)

## Stories

### Story 34.1: Verify and Update Analyst node.yaml Tools Config
**File**: `autoBMAD/nodes/analyst/node.yaml`  

> **⚠️ 路径修正（TD-001）**：原文指向 `nodes/analyst/node.yaml`（废弃）。**权威配置文件在 `autoBMAD/nodes/analyst/node.yaml`**。
> **⚠️ 状态更新（TD-002）**：`autoBMAD/nodes/analyst/node.yaml` 已有完整 tools 配置，可能已完成。仅需验证 `allowed_builtin_tools` 和 `file_permissions` 是否匹配预期格式。

**Changes**:
```yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs:
      - "docs/"
  search_permissions:
    search_dirs:
      - "docs/"
```
**Notes**: Simplify from `["docs/", "docs/research/"]` to just `["docs/"]` - PathValidator handles subdirectory access.

**Acceptance Criteria**:
- [ ] `node.yaml` has correct `tools` section
- [ ] YAML validation passes
- [ ] NodeLoader correctly parses file and search permissions
- [ ] Integration test: agent can read a file in `docs/research/`

### Story 34.2: Verify and Update PM node.yaml Tools Config
**File**: `autoBMAD/nodes/pm/node.yaml`  

> **⚠️ 路径修正（TD-001）**：权威配置文件在 `autoBMAD/nodes/pm/node.yaml`。已完成，仅需验证。

**Changes**: Ensure `tools` section exists with unified configuration.

**Acceptance Criteria**:
- [ ] `node.yaml` has correct `tools` section
- [ ] YAML validation passes
- [ ] Agent can access `docs/` directory contents

### Story 34.3: Verify and Update UX node.yaml Tools Config
**File**: `autoBMAD/nodes/ux/node.yaml`  

> **⚠️ 路径修正（TD-001）**：权威配置文件在 `autoBMAD/nodes/ux/node.yaml`。已完成，仅需验证。

**Changes**: Ensure `tools` section exists with unified configuration.

**Acceptance Criteria**:
- [ ] `node.yaml` has correct `tools` section
- [ ] YAML validation passes
- [ ] Agent can access `docs/` directory contents

### Story 34.4: Verify and Update Architect node.yaml Tools Config
**File**: `autoBMAD/nodes/architect/node.yaml`  

> **⚠️ 路径修正（TD-001）**：权威配置文件在 `autoBMAD/nodes/architect/node.yaml`。
> **⚠️ 状态更新（TD-002）**：`autoBMAD/nodes/architect/node.yaml` 已有完整 tools 配置，可能已完成。需验证。

**Changes**: Ensure `tools` section exists with unified configuration.

**Acceptance Criteria**:
- [ ] `node.yaml` has correct `tools` section
- [ ] YAML validation passes
- [ ] Agent can access `docs/` directory contents

### Story 34.5: Verify and Update PO node.yaml Tools Config
**File**: `autoBMAD/nodes/po/node.yaml`  

> **⚠️ 路径修正（TD-001）**：权威配置文件在 `autoBMAD/nodes/po/node.yaml`。已完成，仅需验证。

**Changes**: Ensure `tools` section exists with unified configuration.

**Acceptance Criteria**:
- [ ] `node.yaml` has correct `tools` section
- [ ] YAML validation passes
- [ ] Agent can access `docs/` directory contents

### Story 34.6: Add Tool Availability Logging in SessionManager
**File**: `autoBMAD/docuswarm/llm/session_manager.py`  
**Changes**:
- Log configured tools at session creation
- Include: MCP server count, allowed tools list, file permissions dirs

**Acceptance Criteria**:
- [ ] Startup logs show: `tools_configured: {mcp_servers: N, allowed_tools: [...]}`
- [ ] Log includes file permission directories
- [ ] Logging uses structured format (structlog)

### Story 34.7: Add Tool Awareness to IndependentAgent System Prompt
**File**: `autoBMAD/docuswarm/agents/independent.py`  
**Changes**:
- Add tool listing section to system prompt (Layer 3 or Layer 4)
- List available tools with brief usage guidance:
  - `read_document`: Read file content from docs/
  - `list_documents`: List files in a directory
  - `grep_search`: Search for patterns in files
  - `glob_search`: Find files matching a pattern
  - `create_deliverable`: Create output document

**Acceptance Criteria**:
- [ ] System prompt includes tool listing section
- [ ] Tool descriptions are accurate and actionable
- [ ] Does not duplicate with existing tool descriptions

### Story 34.8: Tool Access Integration Tests
**File**: `tests/test_tool_permissions.py` (new or extend existing)  
**Test cases**:
- `test_agent_can_read_docs_file()` - verify read_document works
- `test_agent_can_list_docs_directory()` - verify list_documents works
- `test_agent_can_grep_search()` - verify grep_search works
- `test_agent_can_glob_search()` - verify glob_search works
- `test_sensitive_file_blocked()` - verify .env, .db files are blocked
- `test_evaluator_has_no_tools()` - verify EvaluatorAgent remains tool-free

**Acceptance Criteria**:
- [ ] All 6 test cases pass
- [ ] Cross-directory access within docs/ works
- [ ] Sensitive files outside allowed dirs are blocked

## Security Validation

The existing multi-layer defense is sufficient:

```
Layer 1: PathValidator (node level)
  - Directory whitelist
  - Symlink resolution (realpath)
  - Prefix matching check

Layer 2: File type restrictions
  - Extension whitelist (allowed)
  - Extension blacklist (blocked: .db, .sqlite, .key, .pem, .exe, .dll)
  - Size limit (50000 chars)

Layer 3: Directory pattern blocking
  - .git, .env, node_modules, __pycache__
  - .DS_Store, .svn

Layer 4: Application-level checks
  - Binary file detection
  - Encoding validation
  - Access logging
```

**No new security risks introduced** - PathValidator whitelist is sufficient.

## EvaluatorAgent: No Changes

**Decision**: Keep EvaluatorAgent tool-free.

**Reasons**:
1. Context isolation is more verifiable
2. Evaluator's responsibility is scoring, not information collection
3. Avoids security risk introduction
4. Cleaner design

**Current isolation**: `isolation.py` checks `private_reasoning` field - verified and complete.

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Config changes cause access control failure | Low | PathValidator whitelist sufficient |
| Broad file access increases attack surface | Medium | PathValidator fully covers main attack vectors |
| node.yaml misconfiguration | Medium | Permission audit tools; access logging |

## Implementation Phases

### Phase 1: Preparation (Day 1-2)
- Review all 5 node.yaml files for current `tools` configuration
- Write unit tests for PathValidator and NodeLoader
- Prepare test environment

### Phase 2: Configuration Changes (Day 2-3)
- Stories 34.1-34.5: Update all 5 node.yaml files
- Verify YAML format for each
- NodeLoader parsing tests

### Phase 3: System Prompt Update (Day 3-4)
- Story 34.7: Add tool listing to IndependentAgent system prompt
- Story 34.6: Add configuration logging to SessionManager
- Documentation

### Phase 4: Testing (Day 4-7)
- Story 34.8: Integration tests
- Cross-directory access tests
- Security boundary tests: sensitive file blocking
- Monitor and adjust

## Files Changed

> **⚠️ 路径说明（TD-001）**：所有 `node.yaml` 修改均需在 `autoBMAD/nodes/` 目录下进行。`nodes/` 目录已废弃，`NodeLoader` 不会读取其配置。

| File | Change Type | Priority |
|------|------------|------|
| `autoBMAD/nodes/analyst/node.yaml` | Verify/Update | P0 |
| `autoBMAD/nodes/pm/node.yaml` | Verify/Update | P0 |
| `autoBMAD/nodes/ux/node.yaml` | Verify/Update | P0 |
| `autoBMAD/nodes/architect/node.yaml` | Verify/Update | P0 |
| `autoBMAD/nodes/po/node.yaml` | Verify/Update | P0 |
| `autoBMAD/docuswarm/agents/independent.py` | Update | P1 |
| `autoBMAD/docuswarm/llm/session_manager.py` | Update | P1 |
| `tests/test_tool_permissions.py` | New/Extend | P1 |

## 已废弃路径（勿修改）

| 废弃路径 | 原因 | 正确路径 |
|---------|------|--------|
| `nodes/analyst/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/analyst/node.yaml` |
| `nodes/pm/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/pm/node.yaml` |
| `nodes/ux/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/ux/node.yaml` |
| `nodes/architect/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/architect/node.yaml` |
| `nodes/po/node.yaml` | `NodeLoader` 不读取此目录 | `autoBMAD/nodes/po/node.yaml` |

## No Changes Needed

| File | Reason |
|------|--------|
| `autoBMAD/docuswarm/tools/tool_registry.py` | Not responsible for permission management |
| `autoBMAD/docuswarm/agents/evaluator.py` | Keep tool-free design |
| `autoBMAD/docuswarm/agents/base.py` | No base class changes needed |
| `autoBMAD/docuswarm/tools/file_tools.py` | Implementation unchanged |
| `autoBMAD/docuswarm/tools/search_tools.py` | Implementation unchanged |
| `autoBMAD/docuswarm/llm/tool_filter.py` | Already supports full permissions |
| `autoBMAD/docuswarm/context/isolation.py` | Isolation checks already complete |

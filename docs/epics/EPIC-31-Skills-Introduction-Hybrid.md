# EPIC-31: Skills Introduction Mechanism (Hybrid Approach)

**Epic ID**: EPIC-31  
**Source Research**: `docs/research/docuswarm-deep-reform/01-skills-introduction-mechanism.md`  
**Recommended Solution**: Method C - Hybrid (SDK Native + System Prompt Quick Reference + node.yaml Whitelist)  
**Priority**: P0  
**Estimated Effort**: 4 days  
**Status**: Ready for Implementation

---

## Overview

Enable the Claude Agent SDK's native Skills mechanism in DocuSwarm's IndependentAgent. Currently, 50+ BMAD skills exist in `.claude/skills/` but are not utilized because `setting_sources` and `"Skill"` are not configured in `ClaudeAgentOptions`. This epic implements the hybrid approach (Method C) that combines SDK native auto-discovery, system prompt quick reference, and per-node whitelist control.

## Problem Statement

- `setting_sources` is not configured → SDK auto-discovery of skills is disabled
- `"Skill"` is not in `allowed_tools` → Claude cannot invoke any skills
- Skills content is manually injected via system prompt → inefficient, context-heavy
- No per-node skill isolation → no security boundary for skill usage

## Goals

1. Enable SDK native Skills auto-discovery via `setting_sources: ["project"]`
2. Add `"Skill"` to `allowed_tools` in `SessionManager`
3. Add `tools.skills` configuration to `node.yaml` for all 5 nodes
4. Implement `SkillInjector` class for quick reference generation
5. Integrate quick reference into `IndependentAgent` system prompt (Layer 4)

## Recommended Solution: Method C (Hybrid)

**Core Layers**:
1. **SDK Layer**: Enable `setting_sources=["project"]` + `allowed_tools=["Skill", ...]` for auto-discovery and lazy loading
2. **Quick Reference Layer**: Inject skill names + short descriptions into system prompt for faster Claude decision-making
3. **Config Layer**: Per-node `tools.skills.whitelist` in `node.yaml` for security isolation

**Key Advantages**:
- Fully utilizes SDK's lazy loading (no context waste)
- Claude can see available skill list for quick selection
- Per-node whitelist prevents unauthorized skill access
- Gradual migration path to full SDK native approach

## Stories

### Story 31.1: Extend NodeToolPermissions with Skills Config
**File**: `autoBMAD/nodes/loader.py`  
**Changes**:
- Add `NodeSkillsConfig` dataclass with `sdk_native`, `whitelist`, `quick_reference_enabled`, `quick_reference_include_descriptions`
- Add `skills: NodeSkillsConfig` field to `NodeToolPermissions`
- Parse `tools.skills` section in `_build_node_config()`

**Acceptance Criteria**:
- [ ] `NodeSkillsConfig` dataclass exists with all fields
- [ ] `NodeToolPermissions.skills` field is populated from `node.yaml`
- [ ] Backward compatible (nodes without `skills` config still work)
- [ ] Unit tests pass for config loading

### Story 31.2: Update SessionManager to Enable SDK Skills
**File**: `autoBMAD/docuswarm/llm/session_manager.py`  
**Changes**:
- Add `setting_sources=["project"]` to `_create_options()`
- Add `"Skill"` to `_build_allowed_tools()` as first entry
- Extract `_get_builtin_tools()` from tool permissions

**Acceptance Criteria**:
- [ ] `ClaudeAgentOptions.setting_sources` equals `["project"]`
- [ ] `ClaudeAgentOptions.allowed_tools` contains `"Skill"`
- [ ] Existing MCP tools still work
- [ ] Unit test verifies SDK options

### Story 31.3: Implement SkillInjector Class
**File**: `autoBMAD/docuswarm/prompts/skill_injector.py` (new file)  
**Changes**:
- Create `SkillInjector` class with `build_skills_quick_reference()` static method
- Read SKILL.md YAML frontmatter to extract `description` field
- Format as "## Available BMAD Skills" section
- Truncate descriptions to 150 chars max

**Acceptance Criteria**:
- [ ] `SkillInjector.build_skills_quick_reference()` returns valid Markdown
- [ ] Only lists skills in node's whitelist
- [ ] Gracefully handles missing SKILL.md files
- [ ] Unit tests cover: normal case, empty whitelist, missing files

### Story 31.4: Update node.yaml for All 5 Nodes
**Files**: `nodes/analyst/node.yaml`, `nodes/pm/node.yaml`, `nodes/ux/node.yaml`, `nodes/architect/node.yaml`, `nodes/po/node.yaml`  
**Changes** (add `tools.skills` section to each):

```yaml
# analyst
skills:
  sdk_native: true
  whitelist:
    - bmad-product-brief
    - bmad-domain-research
    - bmad-market-research
    - bmad-advanced-elicitation
  quick_reference_enabled: true
  quick_reference_include_descriptions: true

# pm
skills:
  sdk_native: true
  whitelist:
    - bmad-create-prd
    - bmad-edit-prd
    - bmad-validate-prd
    - bmad-advanced-elicitation

# ux
skills:
  sdk_native: true
  whitelist:
    - bmad-create-ux-design
    - bmad-advanced-elicitation

# architect
skills:
  sdk_native: true
  whitelist:
    - bmad-create-architecture
    - bmad-technical-research
    - bmad-advanced-elicitation

# po
skills:
  sdk_native: true
  whitelist:
    - bmad-create-epics-and-stories
    - bmad-sprint-planning
    - bmad-advanced-elicitation
```

**Acceptance Criteria**:
- [ ] All 5 node.yaml files have valid `tools.skills` configuration
- [ ] Each node's whitelist matches its role responsibility
- [ ] YAML validation passes for all files

### Story 31.5: Integrate SkillInjector into IndependentAgent
**File**: `autoBMAD/docuswarm/agents/independent.py`  
**Changes**:
- Import `SkillInjector` in `_call_llm_with_prompts()`
- Load node config and extract `tool_permissions.skills`
- Build quick reference and append to `system_prompt_append`

**Acceptance Criteria**:
- [ ] System prompt contains "## Available BMAD Skills" section
- [ ] Section contains only whitelisted skills for that node
- [ ] Quick reference appended after Layer 3 (task section)
- [ ] Integration test passes end-to-end

### Story 31.6: Integration Tests
**File**: `tests/test_skills_integration.py` (new file)  
**Test cases**:
- `test_skill_injector_builds_quick_reference()`
- `test_node_config_loads_skills()`
- `test_session_manager_enables_skill_tool()`
- `test_independent_agent_with_skills()`

**Acceptance Criteria**:
- [ ] All 4 test cases pass
- [ ] Tests verify SDK `setting_sources` and `allowed_tools`
- [ ] Tests verify system prompt contains skill reference

## Technical Dependencies

| Dependency | Required By |
|-----------|-------------|
| EPIC-32 (Node Task Refactor) | node.yaml skill_ref field must be added first |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| SDK `setting_sources` fails to load | Medium | High | Verify cwd points to project root; add fallback logging |
| Skills index too large → context overflow | Medium | High | Strict whitelist (≤10 skills per node) |
| Claude selects wrong skill | Medium | Medium | Optimize SKILL.md description fields |
| Existing system prompt conflict | Low | High | Maintain backward compat; gradual migration |

## Implementation Phases

### Phase 1: Infrastructure (Day 1-2)
- Story 31.1: Extend `NodeToolPermissions`
- Story 31.2: Update `SessionManager`
- Story 31.3: Implement `SkillInjector`

### Phase 2: Configuration (Day 3)
- Story 31.4: Update all 5 `node.yaml` files
- Story 31.5: Integrate into `IndependentAgent`

### Phase 3: Validation (Day 4)
- Story 31.6: Write integration tests
- Performance testing (context size, load time)
- Security audit (whitelist isolation)

## Files Changed

| File | Change Type | Priority |
|------|------------|---------|
| `autoBMAD/nodes/loader.py` | Extend | P0 |
| `autoBMAD/docuswarm/llm/session_manager.py` | Update | P0 |
| `autoBMAD/docuswarm/prompts/skill_injector.py` | New | P0 |
| `autoBMAD/docuswarm/agents/independent.py` | Update | P1 |
| `nodes/analyst/node.yaml` | Config | P0 |
| `nodes/pm/node.yaml` | Config | P0 |
| `nodes/ux/node.yaml` | Config | P0 |
| `nodes/architect/node.yaml` | Config | P0 |
| `nodes/po/node.yaml` | Config | P0 |
| `tests/test_skills_integration.py` | New | P1 |

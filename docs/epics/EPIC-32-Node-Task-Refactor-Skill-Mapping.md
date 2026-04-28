# EPIC-32: Node Task Refactor and Skill Mapping

**Epic ID**: EPIC-32  
**Source Research**: `docs/research/docuswarm-deep-reform/02-node-task-skill-mapping.md`, `docs/research/docuswarm-deep-reform/02-node-configurations-reference.md`  
**Recommended Solution**: Add `task.skill_ref` field to node.yaml; refactor Analyst node role; enhance persona.json for all 5 nodes  
**Priority**: P0  
**Estimated Effort**: 5-6 days  
**Status**: Ready for Implementation  
**Depends On**: EPIC-31

---

## Overview

Refactor the task configuration of all 5 nodes (analyst, pm, ux, architect, po) to align with their corresponding BMAD skills. The most significant change is the Analyst node which must be repositioned from a "business analysis report" creator to a "product brief" creator. All 5 nodes need `task.skill_ref` added and `persona.json` enhanced.

## Problem Statement

| Node | Current task.name | Target Skill | Alignment |
|------|------------------|-------------|----------|
| analyst | create-business-analysis-report | bmad-product-brief | ⚠️ Needs refactoring |
| pm | create-product-requirements-document | bmad-create-prd | ✅ Aligned |
| ux | create-ux-design-specification | bmad-create-ux-design | ✅ Aligned |
| architect | create-system-architecture-document | bmad-create-architecture | ✅ Aligned |
| po | create-epics-and-user-stories | bmad-create-epics-and-stories | ✅ Aligned |

**Key Issue**: Analyst node currently focuses on "data analysis report" but the target BMAD skill `bmad-product-brief` creates "product briefs" through collaborative discovery. The role must be repositioned.

## Goals

1. Add `task.skill_ref` field to all 5 node.yaml files
2. Refactor Analyst node: task.name → `create-product-brief`, persona → Mary
3. Enhance PM, UX, Architect, PO personas with BMAD-aligned names and expertise
4. Update `NodeTaskConfig` dataclass to support `skill_ref` field
5. Integrate `skill_ref` into `IndependentAgent` system prompt construction

## Stories

### Story 32.1: Extend NodeTaskConfig with skill_ref
**File**: `autoBMAD/nodes/loader.py`  
**Changes**:
- Add `skill_ref: str | None = None` to `NodeTaskConfig` dataclass
- Parse `task.skill_ref` in `_build_node_config()`

**Acceptance Criteria**:
- [ ] `NodeTaskConfig.skill_ref` field exists as optional string
- [ ] `loader.py` correctly parses `skill_ref` from YAML
- [ ] Backward compatible (nodes without `skill_ref` still work with `None`)
- [ ] Unit test verifies parsing

### Story 32.2: Refactor Analyst Node Configuration
**Files**: `nodes/analyst/node.yaml`, `nodes/analyst/persona.json`  
**Changes to node.yaml**:
```yaml
task:
  name: create-product-brief
  description: Create compelling product briefs through collaborative discovery. Transform product vision into 1-2 page executive summary with market context and value proposition.
  role_supplement: Act as product-focused facilitator and peer collaborator. Understand product intent BEFORE scanning artifacts. Capture everything the user shares for synthesis into persuasive narrative.
  skill_ref: bmad-product-brief
deliverable_type: product-brief
```

**Changes to persona.json**:
- `name`: "Mary"
- `role`: "Strategic Business Analyst & Product Discovery Expert"
- `communication_style`: add `"treasure_hunter_energy"`, `"structured_insight"`, `"collaborative_discovery"`
- `expertise`: Product discovery, Porter's Five Forces, SWOT analysis, Requirements elicitation, Market positioning, Value proposition development
- `principles`: Add "Understand product intent BEFORE scanning artifacts"

**Acceptance Criteria**:
- [ ] node.yaml has `task.skill_ref: bmad-product-brief`
- [ ] persona.json has `name: "Mary"`
- [ ] persona.json has updated role and expertise
- [ ] YAML/JSON validation passes
- [ ] Existing pipeline still processes analyst node correctly

### Story 32.3: Enhance PM Node Configuration
**Files**: `nodes/pm/node.yaml`, `nodes/pm/persona.json`  
**Changes to node.yaml**:
```yaml
task:
  skill_ref: bmad-create-prd
  role_supplement: Translate analyst's product brief into actionable, testable requirements. Ensure all functional requirements are clearly defined with acceptance criteria.
```

**Changes to persona.json**:
- `name`: "John"
- `role`: "Product Manager - PRD Creation Expert"
- `expertise`: Add "Jobs-to-be-Done framework", "RICE prioritization methodology", "Acceptance criteria specification"

**Acceptance Criteria**:
- [ ] node.yaml has `task.skill_ref: bmad-create-prd`
- [ ] persona.json has `name: "John"` and enhanced expertise
- [ ] YAML/JSON validation passes

### Story 32.4: Enhance UX Node Configuration
**Files**: `nodes/ux/node.yaml`, `nodes/ux/persona.json`  
**Changes to node.yaml**:
```yaml
task:
  skill_ref: bmad-create-ux-design
  role_supplement: Act as user advocate. Create intuitive, accessible interfaces based on user research. Provide detailed wireframes with textual descriptions. Validate designs against WCAG 2.1 AA.
```

**Changes to persona.json**:
- `name`: "Sally"
- `role`: "User Experience Designer & Interaction Specialist"
- `principles`: Add "Mobile-first design is non-negotiable", "Accessibility is not optional"

**Acceptance Criteria**:
- [ ] node.yaml has `task.skill_ref: bmad-create-ux-design`
- [ ] persona.json has `name: "Sally"` and mobile-first principles
- [ ] YAML/JSON validation passes

### Story 32.5: Enhance Architect Node Configuration
**Files**: `nodes/architect/node.yaml`, `nodes/architect/persona.json`  
**Changes to node.yaml**:
```yaml
task:
  skill_ref: bmad-create-architecture
  role_supplement: Balance technical excellence with business constraints. Make implicit knowledge explicit. Document all trade-off decisions with options compared, rationale, risks, and mitigation.
```

**Changes to persona.json**:
- `name`: "Winston"
- `role`: "System Architect & Technical Design Leader"
- `principles`: Add "Simplicity over complexity", "Embrace boring technology for stability"

**Acceptance Criteria**:
- [ ] node.yaml has `task.skill_ref: bmad-create-architecture`
- [ ] persona.json has `name: "Winston"` and architect principles
- [ ] YAML/JSON validation passes

### Story 32.6: Enhance PO Node Configuration
**Files**: `nodes/po/node.yaml`, `nodes/po/persona.json`  
**Changes to node.yaml**:
```yaml
task:
  skill_ref: bmad-create-epics-and-stories
  role_supplement: Act as product strategist. Define epics aligned with product vision. Create detailed user stories with clear acceptance criteria. Prioritize using RICE or MoSCoW framework.
```

**Changes to persona.json**:
- `name`: "David"
- `role`: "Product Owner & Epic Planning Expert"
- `expertise`: RICE, MoSCoW, Kano frameworks; Story point estimation; Release planning

**Acceptance Criteria**:
- [ ] node.yaml has `task.skill_ref: bmad-create-epics-and-stories`
- [ ] persona.json has `name: "David"` and PO expertise
- [ ] YAML/JSON validation passes

### Story 32.7: Integrate skill_ref into IndependentAgent
**File**: `autoBMAD/docuswarm/agents/independent.py`  
**Changes**:
- Read `node_config.task.skill_ref` in prompt construction
- When `skill_ref` is set, add skill invocation hint to user prompt
- Example: "Use the `{skill_ref}` skill to complete this task."

**Acceptance Criteria**:
- [ ] System prompt references the skill when `skill_ref` is configured
- [ ] Skill hint is clear and actionable for Claude
- [ ] Nodes without `skill_ref` work without errors

### Story 32.8: Update evaluator.yaml Criteria for Analyst Node
**File**: `nodes/analyst/evaluator.yaml`  
**Changes**:
- Update criteria to align with product brief (not business analysis report)
- Adjust weight for `evidence_quality` (market research focus)
- Ensure `actionability` criteria covers PM handoff readiness

**Acceptance Criteria**:
- [ ] evaluator.yaml criteria weights sum to 1.0
- [ ] Criteria names reflect product brief evaluation
- [ ] YAML validation passes

## Configuration Validation Checklist

- [ ] node.yaml: task.name and task.skill_ref are consistent
- [ ] node.yaml: skill_ref points to existing Skill (in .claude/skills/)
- [ ] node.yaml: tools.skills.whitelist includes skill_ref skill
- [ ] persona.json: `name` field matches BMAD template expectation
- [ ] persona.json: expertise includes key methodologies for the role
- [ ] evaluator.yaml: weights sum to 1.0
- [ ] All node.yaml files pass YAML validation
- [ ] All persona.json files pass JSON validation

## Technical Dependencies

| Dependency | Required By |
|-----------|-------------|
| EPIC-31 (Skills Introduction) | Story 32.7 needs SkillInjector from EPIC-31 |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Analyst role change breaks pipeline flow | Medium | High | Maintain backward compat; test full pipeline run |
| skill_ref not recognized by loader | Low | High | Full unit tests with clear error messages |
| persona.json changes affect prompts unexpectedly | Low | Medium | Test each node independently before pipeline test |

## Implementation Phases

### Phase 1: Code Framework (Day 1-2)
- Story 32.1: Extend `NodeTaskConfig` with `skill_ref`
- Story 32.7: Integrate `skill_ref` into `IndependentAgent`
- Unit tests for config loading

### Phase 2: Node Configuration Migration (Day 3-4)
- Story 32.2: Refactor Analyst node (most complex)
- Stories 32.3-32.6: Enhance PM, UX, Architect, PO nodes
- Story 32.8: Update Analyst evaluator.yaml

### Phase 3: Integration Testing (Day 5-6)
- End-to-end pipeline test with all updated nodes
- Verify skill_ref hint appears in system prompt
- Validate BMAD skill invocation works correctly

## Files Changed

| File | Change Type | Priority |
|------|------------|---------|
| `autoBMAD/nodes/loader.py` | Extend | P0 |
| `autoBMAD/docuswarm/agents/independent.py` | Update | P1 |
| `nodes/analyst/node.yaml` | Refactor | P0 |
| `nodes/analyst/persona.json` | Refactor | P0 |
| `nodes/analyst/evaluator.yaml` | Update | P1 |
| `nodes/pm/node.yaml` | Enhance | P0 |
| `nodes/pm/persona.json` | Enhance | P0 |
| `nodes/ux/node.yaml` | Enhance | P0 |
| `nodes/ux/persona.json` | Enhance | P0 |
| `nodes/architect/node.yaml` | Enhance | P0 |
| `nodes/architect/persona.json` | Enhance | P0 |
| `nodes/po/node.yaml` | Enhance | P0 |
| `nodes/po/persona.json` | Enhance | P0 |

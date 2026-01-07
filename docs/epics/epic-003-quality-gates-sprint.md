# Epic: Quality Agents Integration for autoBMAD

**Epic ID**: EPIC-003
**Version**: 2.0
**Date**: 2026-01-07
**Priority**: High
**Epic Owner**: Product Owner (Sarah)
**Status**: Ready for Implementation

---

## 📋 Executive Summary

This epic implements the sprint-change-proposal.md specifications by integrating three sequential automated quality agents (ruff, basedpyright, pytest) into the autoBMAD epic_automation workflow. This is a planned feature implementation that directly executes Epic-003 as defined in the project documentation.

### Key Outcomes

- ✅ Zero negative impact - positive enhancement only
- ✅ Perfect alignment with Epic-003 specifications
- ✅ Full PRD v1.0 approval (dated 2026-01-05)
- ✅ 100% backward compatibility maintained

---

## 🎯 Epic Objectives

### Primary Objectives

1. **Integrate Ruff Agent** - Code linting with auto-fix capabilities
   - Activation: After execute_dev_qa_cycle() returns True
   - Process: Check → Parse JSON → Claude SDK fixes → Re-check (max 3 cycles)
   - Command: `ruff check --fix --output-format=json {source_dir}`

2. **Integrate Basedpyright Agent** - Type checking and validation
   - Activation: After ruff Agent completes
   - Process: Check → Parse JSON → Claude SDK fixes → Re-check (max 3 cycles)
   - Command: `basedpyright --outputjson {source_dir}`

3. **Integrate Pytest Agent** - Test automation with debugging
   - Activation: After basedpyright Agent completes
   - Process: Check → Parse JSON → Claude SDK fixes → Re-check (max 3 cycles)
   - Command: `pytest -v --tb=short --json-report {test_dir}`

### Success Criteria

- [ ] All three quality agents execute sequentially after QA completion
- [ ] Each agent performs up to 3 fix cycles with 2 retries per cycle (using SDK internal max_turns protection)
- [ ] Quality gates can be bypassed via CLI flags
- [ ] 100% backward compatibility with existing epic_automation
- [ ] Zero Cancel Scope errors (no external asyncio.wait_for or asyncio.shield)
- [ ] Zero errors after quality gate execution

---

## 🏗️ Implementation Architecture

### Technical Specifications

#### Agent Activation Sequence

```
Epic Processing
    ↓
execute_dev_qa_cycle() == True
    ↓
┌─────────────────────────────────────┐
│  QUALITY GATES PIPELINE            │
│                                     │
│  1. Ruff Agent (Code Linting)      │
│  2. Basedpyright Agent (Type Check)│
│  3. Pytest Agent (Test Execution)  │
│                                     │
│  Each: Check → Fix → Re-check      │
│  Max: 3 cycles, 2 retries each     │
└─────────────────────────────────────┘
    ↓
Quality Gates Complete
```

#### Core Components

1. **CodeQualityAgent**
   - Integrates ruff and basedpyright execution
   - JSON parsing for error collection
   - Claude SDK integration for automated fixes
   - Retry logic with exponential backoff

2. **TestAutomationAgent**
   - Manages pytest execution workflow
   - Collects test failure information
   - Integrates debugpy for persistent failures
   - Automated test fix workflow

3. **Epic Driver Enhancement**
   - Extended with quality gate orchestration
   - CLI flags: --skip-quality, --skip-tests
   - Progress tracking across all phases

---

## 📋 Stories Breakdown

### Story 1: Ruff Agent Integration
**Story ID**: 003.1
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** integrate ruff code linting with auto-fix capabilities,
**So that** code quality can be validated and automatically corrected after QA completion.

**Acceptance Criteria**:
- [ ] Ruff added as pip dependency
- [ ] CodeQualityAgent class created
- [ ] Ruff execution: `ruff check --fix --output-format=json {source_dir}`
- [ ] JSON error parsing implemented
- [ ] Claude SDK fixes for identified issues
- [ ] Max 3 cycles with 2 retries each
- [ ] Virtual environment: venv\Scripts

### Story 2: Basedpyright Agent Integration
**Story ID**: 003.2
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** integrate basedpyright type checking with validation,
**So that** code type safety can be verified and automatically corrected.

**Acceptance Criteria**:
- [ ] Basedpyright added as pip dependency
- [ ] Type checking execution: `basedpyright --outputjson {source_dir}`
- [ ] JSON error parsing implemented
- [ ] Claude SDK fixes for type errors
- [ ] Max 3 cycles with 2 retries each
- [ ] Integration with ruff agent workflow

### Story 3: Pytest Agent Integration
**Story ID**: 003.3
**Priority**: High
**Estimated Effort**: 3 days

**As a** BMAD automation system,
**I want to** integrate pytest test automation with debugpy,
**So that** test execution can be automated with debugging for persistent failures.

**Acceptance Criteria**:
- [ ] Pytest and debugpy added as pip dependencies
- [ ] TestAutomationAgent class created
- [ ] Pytest execution: `pytest -v --tb=short --json-report {test_dir}`
- [ ] JSON report parsing for test failures
- [ ] Debugpy invocation for persistent failures
- [ ] Claude SDK fixes for test issues
- [ ] Max 3 cycles with 2 retries each

### Story 4: Epic Driver Orchestration
**Story ID**: 003.4
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** extend epic_driver.py to orchestrate quality gates,
**So that** complete workflow executes seamlessly with proper error handling.

**Acceptance Criteria**:
- [ ] Quality gates integrate after execute_dev_qa_cycle()
- [ ] Sequential execution: Ruff → Basedpyright → Pytest
- [ ] CLI flags: --skip-quality, --skip-tests
- [ ] Progress tracking across all phases
- [ ] Error handling with clear feedback
- [ ] Timeout controls: 1 min between calls, 10-20 min SDK timeout

### Story 5: Documentation & Integration
**Story ID**: 003.5
**Priority**: Medium
**Estimated Effort**: 1 day

**As a** BMAD automation system,
**I want to** document the quality gate workflow,
**So that** users understand the new automated quality processes.

**Acceptance Criteria**:
- [ ] README.md updated with quality gate workflow
- [ ] CLI help text updated with new flags
- [ ] Integration tests for complete pipeline
- [ ] Troubleshooting guide for quality gates
- [ ] Example epic demonstrating quality agents

---

## 🔄 Workflow Implementation

### Phase Activation Logic

```python
# Epic Driver Enhancement (Simplified - No External Timeouts)
def execute_quality_gates(epic_id, skip_quality=False, skip_tests=False):
    """
    Execute quality gates with SDK internal max_turns protection only.
    No external asyncio.wait_for or asyncio.shield to avoid Cancel Scope errors.
    """
    if not skip_quality:
        # Phase 1: Ruff Agent (SDK max_turns=150 protection)
        ruff_result = execute_ruff_agent(source_dir)
        if not ruff_result.success:
            retry_with_sdk_fixes(ruff_result, max_cycles=3)

        # Phase 2: Basedpyright Agent (SDK max_turns=150 protection)
        basedpyright_result = execute_basedpyright_agent(source_dir)
        if not basedpyright_result.success:
            retry_with_sdk_fixes(basedpyright_result, max_cycles=3)

    if not skip_tests:
        # Phase 3: Pytest Agent (SDK max_turns=150 protection)
        pytest_result = execute_pytest_agent(test_dir)
        if not pytest_result.success:
            retry_with_debugpy(pytest_result, max_cycles=3)

    return QualityGateResult(
        ruff_passed=ruff_result.success,
        basedpyright_passed=basedpyright_result.success,
        pytest_passed=pytest_result.success
    )
```

### Agent Execution Pattern

Each quality agent follows this pattern:

1. **Check Phase**: Execute tool, capture JSON output
2. **Parse Phase**: Extract errors/warnings from JSON
3. **Fix Phase**: Use Claude SDK to fix issues
4. **Re-check Phase**: Re-run tool to verify fixes
5. **Retry Logic**: Max 3 cycles, 2 retries per cycle

### Timeout & Resource Management

- **SDK Protection**: Use `max_turns=150` in Claude SDK options for protection against infinite loops
- **Between Calls**: No external timeout - let SDK sessions complete naturally
- **Virtual Environment**: venv\Scripts activation
- **Error Handling**: Simple exception handling, no external cancellation or asyncio nesting
- **Cancel Scope Safety**: No `asyncio.wait_for` or `asyncio.shield` to prevent cross-Task scope conflicts

---

## 📊 Success Metrics

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Quality Gate Pass Rate** | ≥90% for clean code | Basedpyright + ruff validation success |
| **Test Automation Success** | ≥85% test pass rate | Pytest execution with fixes |
| **Error Recovery** | ≥95% from failures | Retry and recovery success rate |
| **Processing Time** | < 30 min typical epic | Complete 5-phase pipeline timing |

### Technical Metrics

- **Backward Compatibility**: 100% maintained
- **CLI Flag Functionality**: All flags operational
- **Database Integrity**: 100% during schema migration
- **Code Coverage**: ≥80% for new code

---

## 🔐 Risk Assessment

### Risk Assessment

**Medium Risk Profile** ⚠️ (mitigated through design changes)

**Risk Source:**
- Cancel Scope errors from asyncio.wait_for and asyncio.shield nesting
- External timeout mechanisms conflicting with SDK session lifecycle
- Cross-Task cancel scope cleanup causing RuntimeError

**Mitigations (Implemented):**
- ✅ **Removed External Timeouts**: No `asyncio.wait_for` wrapping SDK calls
- ✅ **Removed Shield Nesting**: No `asyncio.shield` to prevent scope conflicts
- ✅ **SDK Internal Protection**: Use `max_turns=150` for infinite loop prevention
- ✅ **Sequential Execution**: Clear scope lifecycle without concurrent complexity
- ✅ **Simple Error Handling**: Basic exception catching without external cancellation

**Additional Safety:**
- Backward compatibility maintained
- Retry mechanisms (3 cycles, 2 retries) with SDK protection
- Optional bypass flags (--skip-quality, --skip-tests)
- Clear success criteria (Epic-003 acceptance criteria)

---

## 🚀 Implementation Timeline

### Phase 1: Core Agent Integration (Days 1-4)
- Day 1: Ruff Agent implementation
- Day 2: Basedpyright Agent implementation
- Day 3: Pytest Agent implementation
- Day 4: Agent testing and validation

### Phase 2: Orchestration (Days 5-6)
- Day 5: Epic driver extension
- Day 6: CLI flags and error handling

### Phase 3: Documentation & Testing (Days 7-8)
- Day 7: Documentation updates
- Day 8: Integration tests and validation

**Total Duration**: 8 working days

---

## ✅ Definition of Done

### Epic Completion Criteria

- [ ] All 5 stories implemented and tested
- [ ] Three quality agents functioning sequentially
- [ ] 100% backward compatibility maintained
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] CLI flags operational
- [ ] Zero errors after quality gate execution

### Quality Gates Validation

- **Ruff**: Auto-fix applied, remaining errors fixable
- **Basedpyright**: Strict type checking, zero errors
- **Pytest**: All tests pass after automated fixes
- **Debugpy**: Invoked after 5 failed fix attempts

---

## 📞 Stakeholder Sign-off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| **Product Owner** | Sarah | ✅ Approved | 2026-01-07 | Proceed with implementation |
| **Story Master** | | Pending | | |
| **Developer** | | Pending | | |
| **QA Engineer** | | Pending | | |

---

## 📝 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0 | 2026-01-07 | Product Owner | Updated to prevent Cancel Scope errors: removed external timeouts, added SDK max_turns protection, simplified error handling |
| 2.0 | 2026-01-07 | Product Owner | Updated to Ready for Implementation based on sprint-change-proposal.md |
| 1.0 | 2026-01-05 | Product Owner | Initial epic creation |

---

**Epic Status**: ✅ **APPROVED FOR IMPLEMENTATION**

**Next Action**: Begin Story 1 (Ruff Agent Integration)

**⚠️ Critical Implementation Note**: All SDK calls must use `max_turns=150` protection only. Do NOT use `asyncio.wait_for`, `asyncio.shield`, or external timeout mechanisms. See `docs/evaluation/cancel-scope-error-analysis.md` for details.

---

*Powered by BMAD™ Method - Breaking Through Agile AI-Driven Development*

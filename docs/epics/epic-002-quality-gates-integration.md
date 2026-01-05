# Epic: Integration of Code Quality and Test Automation into autoBMAD

**Epic ID**: EPIC-002
**Version**: 1.0
**Date**: 2026-01-05
**Priority**: High
**Epic Owner**: Product Owner
**Status**: Ready for Planning

---

## 📋 Epic Overview

### Business Objective

Integrate basedpyright-workflow and fixtest-workflow functionality into the autoBMAD epic automation system to create a unified quality assurance pipeline that processes multi-story epics through complete SM-Dev-QA cycles followed by automated code quality checks and test execution, ensuring 100% backward compatibility with existing epic_automation functionality.

### Success Criteria

- ✅ **Unified Workflow**: Complete pipeline from story creation through quality gates (SM → Dev → QA → Code Quality → Test Automation)
- ✅ **Backward Compatibility**: All existing CLI options and functionality preserved without changes
- ✅ **Quality Gates**: Automated basedpyright type checking and ruff linting with auto-fix capabilities
- ✅ **Test Automation**: Integrated pytest execution with debugpy for persistent failure diagnosis
- ✅ **State Tracking**: Extended SQLite database schema tracks all workflow phases without data loss
- ✅ **Self-Contained**: No external workflow installations required - all dependencies via pip
- ✅ **Error Recovery**: Comprehensive retry mechanisms across all workflow phases
- ✅ **Optional Bypass**: Quality gates can be bypassed via --skip-quality and --skip-tests flags

### Scope

**In Scope**:
- Extend state management database schema for quality and test automation phases
- Integrate basedpyright type checking as native dependency
- Integrate ruff linting with auto-fix capabilities
- Integrate pytest test execution framework
- Integrate debugpy for persistent test failure diagnosis
- Extend epic_driver.py orchestration for quality gates
- Create CodeQualityAgent and TestAutomationAgent classes
- Update documentation and create integration tests
- Maintain 100% backward compatibility

**Out of Scope**:
- Multi-epic coordination across quality gates
- Advanced analytics for quality gate results
- Custom quality rule configuration beyond basedpyright/ruff defaults
- Integration with external CI/CD systems

---

## 🎯 Stories

### Story 1.1: Extend State Management for Quality Gates
**Story ID**: 001
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** extend the SQLite database schema to track code quality and test automation phases,
**So that** progress can be tracked across all workflow phases without losing existing epic data.

**Acceptance Criteria**:
- [ ] Extend progress.db schema with code_quality_phase table (epic_id, file_path, error_count, fix_status, timestamp, basedpyright_errors, ruff_errors)
- [ ] Extend progress.db schema with test_automation_phase table (epic_id, test_file_path, failure_count, fix_status, debug_info, timestamp)
- [ ] State manager can read existing epic records without errors
- [ ] New schema additions are backward compatible with existing data
- [ ] Database backup mechanism implemented before schema changes
- [ ] All database operations use parameterized queries for security

**Integration Verification**:
- IV1: Existing epic processing continues to work without database modifications
- IV2: New schema additions don't interfere with existing SM-Dev-QA workflow
- IV3: Database integrity is maintained across all read/write operations

**Implementation Notes**:
- Schema migration with backward compatibility
- SQLite foreign key constraints for data integrity
- Backup mechanism: progress.db.backup before schema changes
- Add indexes for performance on epic_id columns

---

### Story 1.2: Integrate Basedpyright and Ruff Code Quality Checks
**Story ID**: 002
**Priority**: High
**Estimated Effort**: 3 days

**As a** BMAD automation system,
**I want to** natively integrate basedpyright type checking and ruff linting with auto-fix capabilities,
**So that** code quality can be validated automatically after QA completion without external tool dependencies.

**Acceptance Criteria**:
- [ ] Basedpyright added as direct dependency in requirements.txt (>=1.1.0)
- [ ] Ruff added as direct dependency in requirements.txt (>=0.1.0)
- [ ] CodeQualityAgent class created to wrap basedpyright and ruff execution
- [ ] Basedpyright_workflow.py module integrated to execute type checking on all .py files
- [ ] Ruff_workflow.py module integrated to execute linting with --fix auto-correction
- [ ] JSON error reports generated for each .py file with identified issues
- [ ] Claude agents automatically invoked to fix identified basedpyright and ruff issues
- [ ] System repeats quality checks until zero errors remain or max iterations reached (3)
- [ ] Quality gate can be bypassed via --skip-quality CLI flag
- [ ] Progress tracking updates state_manager with quality phase results

**Integration Verification**:
- IV1: Existing SM-Dev-QA workflow continues to function without quality gates
- IV2: Code quality checks only execute after all stories pass QA
- IV3: Basedpyright and ruff execution doesn't interfere with existing CLI interface

**Implementation Notes**:
- basedpyright execution: `--outputjson --level error` for strict type checking
- ruff execution: `check --output-format json --fix` for auto-correction
- JSON parsing for error collection and reporting
- Claude SDK integration for automated issue fixing
- Retry logic with exponential backoff for fix attempts

---

### Story 1.3: Integrate Test Automation with Debugpy
**Story ID**: 003
**Priority**: High
**Estimated Effort**: 3 days

**As a** BMAD automation system,
**I want to** natively integrate pytest test execution with debugpy for persistent failure diagnosis,
**So that** test automation can be performed automatically after code quality validation without external workflow dependencies.

**Acceptance Criteria**:
- [ ] Pytest added as direct dependency in requirements.txt (>=7.0.0)
- [ ] Debugpy added as direct dependency in requirements.txt (>=1.6.0)
- [ ] TestAutomationAgent class created to manage test execution workflow
- [ ] Test_automation_workflow.py module integrated to execute all tests in @tests directory
- [ ] Failed/errored test file paths and failure information collected in JSON format
- [ ] Summary JSON report generated for all test execution results
- [ ] Claude agents automatically invoked to fix identified test issues
- [ ] System re-executes tests after each fix attempt
- [ ] Debugpy invoked for tests that fail repeatedly, providing test path, error details, and debug information to Claude agents
- [ ] Test automation gate can be bypassed via --skip-tests CLI flag

**Integration Verification**:
- IV1: Existing epic processing continues without test automation when skipped
- IV2: Test execution only occurs after successful code quality validation
- IV3: Debugpy integration doesn't interfere with normal test execution flow

**Implementation Notes**:
- pytest execution: `--tb=short --json-report --json-report-file=test_results.json`
- JSON report parsing for failure collection
- debugpy integration: `debugpy.listen(('localhost', 5678))` with timeout controls
- Claude SDK integration for automated test fixing
- Maximum retry count: 5 attempts before debugpy invocation

---

### Story 1.4: Extend Epic Driver with Quality Gate Orchestration
**Story ID**: 004
**Priority**: High
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** extend epic_driver.py to orchestrate the complete workflow from story creation through quality gates,
**So that** the entire multi-phase workflow executes seamlessly with proper error handling and progress tracking.

**Acceptance Criteria**:
- [ ] Epic driver processes epics through complete workflow: SM → Dev → QA → Code Quality → Test Automation
- [ ] State manager tracks progress across all workflow phases
- [ ] Quality gates execute only after all epic stories complete SM-Dev-QA cycle
- [ ] Retry mechanisms work across all workflow phases without corrupting progress database
- [ ] Error handling provides clear, actionable feedback for failures in any phase
- [ ] CLI interface extended with --skip-quality and --skip-tests flags
- [ ] Verbose logging includes all quality gate operations
- [ ] Concurrent processing mode (experimental) is compatible with quality gates
- [ ] Maximum iteration limits enforced (quality: 3, tests: 5)

**Integration Verification**:
- IV1: Existing CLI options continue to function as documented
- IV2: New quality gates integrate seamlessly with existing workflow
- IV3: Progress tracking is accurate across all workflow phases
- IV4: Error recovery mechanisms work without manual intervention

**Implementation Notes**:
- Sequential orchestration: quality gates only after all stories pass QA
- Phase-gated execution: test automation only after quality gates pass
- Comprehensive error handling with phase-specific error types
- Progress indicators: show phase completion percentage
- CLI flags: maintain backward compatibility, add new optional flags

---

### Story 1.5: Documentation and Testing Integration
**Story ID**: 005
**Priority**: Medium
**Estimated Effort**: 2 days

**As a** BMAD automation system,
**I want to** update all documentation and create integration tests for the complete workflow,
**So that** users understand the new workflow phases and the system can be validated end-to-end.

**Acceptance Criteria**:
- [ ] README.md updated to document new quality gate workflow phases
- [ ] SETUP.md updated with basedpyright, ruff, pytest, and debugpy dependencies
- [ ] Integration tests verify complete workflow: story creation → development → QA → code quality → test automation
- [ ] Example epic created demonstrating multi-story processing with quality gates
- [ ] Troubleshooting guide added for common quality gate issues
- [ ] Performance benchmarks established for typical epic processing times
- [ ] CLI help text updated with new --skip-quality and --skip-tests options

**Integration Verification**:
- IV1: Documentation accurately reflects actual system behavior
- IV2: New users can successfully set up and run the complete workflow
- IV3: Integration tests validate all workflow phases work together correctly

**Implementation Notes**:
- Documentation: Clear separation of existing and new functionality
- Integration tests: End-to-end scenarios with quality gates
- Example epic: 3-5 stories demonstrating complete pipeline
- Troubleshooting: Common issues and solutions for quality gates
- Performance: Baseline metrics for each workflow phase

---

## 🏗️ Technical Architecture

### Design Principle: Unified Quality Assurance Pipeline

Extending the existing autoBMAD architecture with quality gates follows the principle of **Sequential Validation with Optional Bypasses**:

| Aspect | Existing System | Enhanced System | Change |
|--------|-----------------|-----------------|--------|
| **Workflow Phases** | 3 phases (SM-Dev-QA) | 5 phases (SM-Dev-QA-Quality-Tests) | +2 phases |
| **State Tracking** | 2 tables (epic_processing, story_processing) | 4 tables (+ code_quality_phase, test_automation_phase) | +2 tables |
| **Dependencies** | 1 (anthropic) | 5 (+ basedpyright, ruff, pytest, debugpy) | +4 tools |
| **CLI Options** | 4 options | 6 options (+ --skip-quality, --skip-tests) | +2 flags |
| **Backward Compatibility** | N/A | 100% maintained | ✅ Guaranteed |

### Architecture Diagram

```
autoBMAD/epic_automation/ (Enhanced)
├── epic_driver.py (350-400 lines)          # ✅ Extended orchestrator
│   - Epic parsing & story extraction
│   - SM-Dev-QA cycle coordination
│   - Quality gate orchestration (NEW)
│   - Test automation orchestration (NEW)
│   - CLI: --skip-quality, --skip-tests (NEW)
├── state_manager.py (150-200 lines)        # ✅ Extended schema
│   - SQLite state persistence (progress.db)
│   - epic_processing & story_processing tables (existing)
│   - code_quality_phase table (NEW)
│   - test_automation_phase table (NEW)
├── sm_agent.py (80-100 lines)              # ✅ Story Master
├── dev_agent.py (80-100 lines)             # ✅ Development
├── qa_agent.py (80-100 lines)              # ✅ Quality Assurance
├── code_quality_agent.py (120-150 lines)   # ✅ NEW: Quality gates
│   - Basedpyright execution & JSON parsing
│   - Ruff linting & auto-fix
│   - Claude agent integration for fixes
├── test_automation_agent.py (120-150 lines) # ✅ NEW: Test automation
│   - Pytest execution & result collection
│   - Debugpy integration for persistent failures
│   - Claude agent integration for test fixes
└── workflows/
    ├── basedpyright_workflow.py (80-100 lines)  # ✅ NEW: Type checking
    ├── ruff_workflow.py (80-100 lines)          # ✅ NEW: Linting
    └── test_automation_workflow.py (100-120 lines) # ✅ NEW: Test execution

Workflow Pipeline:
┌─────────────────────────────────────────────────────────────┐
│  Epic → SM → Dev → QA → [Quality Gates] → [Test Automation]  │
│                     ↓              ↓              ↓           │
│              Story Complete   Code Quality   Tests Pass     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **epic_driver.py (Extended)** - Complete workflow orchestrator
   - Parse CLI arguments (existing + new quality gate flags)
   - Coordinate SM-Dev-QA cycle (existing)
   - Orchestrate quality gates after QA completion (NEW)
   - Orchestrate test automation after quality gates (NEW)
   - Comprehensive error handling across all phases

2. **state_manager.py (Extended)** - Complete state tracking
   - epic_processing & story_processing tables (existing)
   - code_quality_phase table (NEW) - track quality gate results
   - test_automation_phase table (NEW) - track test automation results
   - Schema migration with backward compatibility
   - Database backup mechanism

3. **CodeQualityAgent (NEW)** - Quality gate orchestrator
   - Execute basedpyright on all .py files
   - Execute ruff with --fix auto-correction
   - Parse JSON error reports
   - Invoke Claude agents to fix issues
   - Retry until zero errors or max iterations

4. **TestAutomationAgent (NEW)** - Test automation orchestrator
   - Execute pytest on all test files
   - Collect failed/errored test information
   - Generate JSON summary reports
   - Invoke debugpy for persistent failures
   - Invoke Claude agents to fix test issues

### Database Schema Extensions

```sql
-- Code quality phase table (NEW)
CREATE TABLE code_quality_phase (
    record_id TEXT PRIMARY KEY,
    epic_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    error_count INTEGER DEFAULT 0,
    fix_status TEXT DEFAULT 'pending',
    basedpyright_errors TEXT,
    ruff_errors TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (epic_id) REFERENCES epic_processing(epic_id)
);

-- Test automation phase table (NEW)
CREATE TABLE test_automation_phase (
    record_id TEXT PRIMARY KEY,
    epic_id TEXT NOT NULL,
    test_file_path TEXT NOT NULL,
    failure_count INTEGER DEFAULT 0,
    fix_status TEXT DEFAULT 'pending',
    debug_info TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (epic_id) REFERENCES epic_processing(epic_id)
);

-- Indexes for performance
CREATE INDEX idx_quality_epic ON code_quality_phase(epic_id);
CREATE INDEX idx_test_epic ON test_automation_phase(epic_id);
```

### Why This Architecture?

**Sequential Quality Gates**: Quality gates execute only after all stories pass QA, ensuring epic-level quality validation

**Self-Contained Integration**: basedpyright, ruff, pytest, and debugpy integrated as native pip dependencies, not external tools

**Optional Bypasses**: --skip-quality and --skip-tests flags allow emergency bypasses while maintaining workflow integrity

**100% Backward Compatibility**: All existing CLI options, database records, and functionality preserved without changes

---

## 📊 Implementation Timeline

### Phase 1: Database Schema Extension (Days 1-2)
**Story**: Story 1.1 (Extend State Management for Quality Gates)
**Deliverable**: Extended database schema with quality and test automation tracking

- Day 1: Design schema extensions, implement state_manager.py methods
- Day 2: Database migration with backward compatibility, backup mechanism

### Phase 2: Quality Gate Integration (Days 3-5)
**Story**: Story 1.2 (Integrate Basedpyright and Ruff Code Quality Checks)
**Deliverable**: Complete code quality validation system

- Day 3: CodeQualityAgent class, basedpyright integration
- Day 4: Ruff integration with auto-fix, JSON error reporting
- Day 5: Claude agent integration for automated fixes, retry logic

### Phase 3: Test Automation Integration (Days 6-8)
**Story**: Story 1.3 (Integrate Test Automation with Debugpy)
**Deliverable**: Complete test automation system

- Day 6: TestAutomationAgent class, pytest integration
- Day 7: Debugpy integration for persistent failures
- Day 8: Claude agent integration for test fixes, retry logic

### Phase 4: Workflow Orchestration (Days 9-10)
**Story**: Story 1.4 (Extend Epic Driver with Quality Gate Orchestration)
**Deliverable**: Complete workflow orchestration across all phases

- Day 9: Extend epic_driver.py with quality gate orchestration
- Day 10: Error handling, progress tracking, CLI flag integration

### Phase 5: Documentation and Testing (Days 11-12)
**Story**: Story 1.5 (Documentation and Testing Integration)
**Deliverable**: Complete documentation and integration tests

- Day 11: Update README.md, SETUP.md, CLI help text
- Day 12: Integration tests, example epic, troubleshooting guide

**Total Duration**: 12 working days (2.5 weeks)

---

## ✅ Quality Assurance

### Testing Strategy

1. **Unit Tests** (Stories 1.1, 1.2, 1.3)
   - Database schema extension operations
   - Basedpyright and ruff integration
   - Pytest and debugpy integration
   - State manager CRUD operations

2. **Integration Tests** (Stories 1.2, 1.3, 1.4)
   - Complete SM-Dev-QA-Quality-Tests pipeline
   - Quality gate execution flow
   - Test automation workflow
   - Error recovery across phases

3. **End-to-End Tests** (Story 1.5)
   - Complete epic processing with quality gates
   - Backward compatibility verification
   - Performance benchmarks
   - CLI flag functionality

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Backward Compatibility** | 100% | All existing CLI options function without changes |
| **Quality Gate Pass Rate** | ≥90% for clean code | Basedpyright + ruff validation success rate |
| **Test Automation Success** | ≥85% test pass rate | Pytest execution with automated fixes |
| **Epic Completion Time** | < 30 min (typical) | Total time for complete 5-phase pipeline |
| **Error Recovery Rate** | ≥95% from failures | Successful retry and recovery across phases |
| **Database Integrity** | 100% | No data loss during schema migration |
| **Code Quality** | Zero basedpyright errors | Strict type checking validation |
| **Code Coverage** | ≥80% for new code | Unit and integration test coverage |

### Quality Gates Validation

**Basedpyright**: Strict type checking mode, zero errors tolerated
**Ruff**: Auto-fix applied, remaining errors must be fixable or waived
**Pytest**: All tests must pass after automated fixes
**Debugpy**: Invoked only after 5 failed fix attempts

---

## 🔄 Risks & Mitigations

### High Priority Risks

1. **Database Schema Migration Breaking Existing Data**
   - **Probability**: Medium
   - **Impact**: High
   - **Mitigation**: Implement progress.db.backup before migration, extensive backward compatibility testing

2. **Quality Gates Extending Epic Processing Time**
   - **Probability**: High
   - **Impact**: Medium
   - **Mitigation**: Implement --skip-quality and --skip-tests flags, optimize tool execution

3. **Claude Agent Fix Failures for Quality Issues**
   - **Probability**: Medium
   - **Impact**: Medium
   - **Mitigation**: Implement max iteration limits (3), detailed error reporting, manual override capability

### Medium Priority Risks

1. **Debugpy Integration Causing System Hangs**
   - **Probability**: Low
   - **Impact**: Medium
   - **Mitigation**: Timeout controls (5 minutes), only invoke after multiple failed attempts

2. **Basedpyright False Positives Blocking Progress**
   - **Probability**: Medium
   - **Impact**: Low
   - **Mitigation**: Configure strict mode appropriately, allow waivable quality gates

3. **Resource Exhaustion During Quality Gates**
   - **Probability**: Low
   - **Impact**: Low
   - **Mitigation**: Monitor system resources, implement backpressure controls

---

## 📚 Dependencies

### External Dependencies

**New Dependencies** (via pip requirements.txt):
- **basedpyright** (>=1.1.0) - Type checking and code quality
- **ruff** (>=0.1.0) - Fast linting with auto-fix capability
- **pytest** (>=7.0.0) - Test execution framework
- **debugpy** (>=1.6.0) - Remote debugging for persistent failures

**Existing Dependencies**:
- **anthropic** (>=0.7.0) - Claude SDK for agent communication
- **Python 3.8+** - Core runtime environment

### Internal Dependencies

- **autoBMAD/epic_automation/** - Core automation system
- **.bmad-core/** - BMAD methodology framework
- **progress.db** - SQLite state management database

### Dependency Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installations
basedpyright --version
ruff --version
pytest --version
debugpy --version
```

---

## 📈 Success Metrics

### Quantitative Metrics

- **Epic Processing Time**: < 30 minutes for typical 5-story epic (with quality gates)
- **Quality Gate Execution**: < 10 seconds per .py file for basedpyright, < 5 seconds for ruff
- **Test Automation**: < 5 minutes for typical test suite
- **Retry Success Rate**: ≥90% for quality gate issues, ≥85% for test failures
- **Database Migration**: 100% success rate with zero data loss

### Qualitative Metrics

- **Seamless Integration**: Quality gates feel like natural extension of existing workflow
- **Clear Error Messages**: Actionable feedback for all failure scenarios
- **Optional Execution**: Quality gates can be bypassed when needed
- **Comprehensive Logging**: Full visibility into all workflow phases

---

## 🎯 Definition of Done

### For Epic Completion

- [ ] All 5 stories implemented and tested
- [ ] Database schema extended with quality and test automation tables
- [ ] Basedpyright and ruff integrated as native dependencies
- [ ] Pytest and debugpy integrated as native dependencies
- [ ] CodeQualityAgent and TestAutomationAgent classes implemented
- [ ] Epic driver orchestrates complete 5-phase workflow
- [ ] 100% backward compatibility verified
- [ ] Documentation updated (README.md, SETUP.md, CLI help)
- [ ] Integration tests pass with sample epic
- [ ] Performance benchmarks met
- [ ] CLI flags --skip-quality and --skip-tests functional

### For Each Story

- [ ] Acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code reviewed by peer
- [ ] Documentation updated
- [ ] No critical or high severity bugs
- [ ] Backward compatibility maintained

---

## 📞 Stakeholder Sign-off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| **Product Owner** | Sarah | Pending | | |
| **Tech Lead** | | Pending | | |
| **QA Lead** | | Pending | | |
| **Dev Team** | | Pending | | |

---

## 📝 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-05 | Product Owner | Initial epic creation based on PRD for code quality and test automation integration |

---

**Epic Status**: 📋 Draft → Ready for Planning
**Next Step**: Story breakdown and task assignment

---

*Powered by BMAD™ Method - Breaking Through Agile AI-Driven Development*

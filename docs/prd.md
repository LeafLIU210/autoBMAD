# autoBMAD/epic_automation Brownfield Enhancement PRD

**Version**: 1.0
**Date**: 2026-01-05
**Project**: Integration of Code Quality and Test Automation into autoBMAD

---

## 1. Intro Project Analysis and Context

### 1.1 Existing Project Overview

**Analysis Source**: IDE-based fresh analysis (direct code examination)

**Current Project State**:
autoBMAD/epic_automation is a self-contained Python automation system for the BMAD (Breakthrough Method of Agile AI-driven Development) workflow. It processes epic markdown files through an automated SM-Dev-QA cycle. The system consists of:

- **Core Driver** (`epic_driver.py`): Main orchestrator with CLI interface, handles epic parsing and story processing
- **Three Agent Types**: SM Agent (story creation/refinement), Dev Agent (implementation), QA Agent (validation)
- **State Management** (`state_manager.py`): SQLite-based progress tracking in `progress.db`
- **Task Guidance**: Reads from `.bmad-core/tasks/*.md` files for agent prompts
- **CLI Options**: Supports retry logic, verbose logging, concurrent processing (experimental), and custom source/test directories

### 1.2 Available Documentation

- ✅ Tech Stack Documentation (README.md comprehensive)
- ✅ Source Tree/Architecture (README.md architecture section)
- ✅ Coding Standards (informal, following Python best practices)
- ✅ API Documentation (CLI interface documented)
- ✅ Setup Guide (SETUP.md with installation instructions)

### 1.3 Enhancement Scope Definition

**Enhancement Type**: Integration with New Systems + Major Feature Modification

**Enhancement Description**:
Integrate basedpyright-workflow (code quality) and fixtest-workflow (test automation) into the autoBMAD epic automation system to create a unified workflow that processes multi-story epics through complete SM-Dev-QA cycles, followed by automated code quality checks and test execution.

**Impact Assessment**: Major Impact - requires architectural changes to incorporate two additional workflow phases after the existing SM-Dev-QA cycle, with new agent integrations and state management for quality gates.

### 1.4 Goals and Background Context

**Goals**:
- Create a unified BMAD workflow that combines story development with automated quality assurance
- Enable multi-story epic processing through complete automation: story creation → development → QA → code quality → test automation
- Maintain backward compatibility with existing epic_automation functionality
- Provide seamless integration of basedpyright-workflow and fixtest-workflow as post-QA quality gates
- Establish clear retry mechanisms and error handling across all three workflow phases

**Background Context**:
The current autoBMAD/epic_automation system handles the SM-Dev-QA cycle for individual stories within an epic. However, it lacks integration with the project's code quality and test automation workflows. By integrating basedpyright-workflow (which provides type checking, linting, and code quality reports) and fixtest-workflow (which provides automated test execution and fixing), we can create a comprehensive development pipeline that ensures code quality at the epic level rather than just the individual story level.

### 1.5 Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial PRD Creation | 2026-01-05 | 1.0 | Complete PRD for basedpyright and fixtest integration | Product Manager |

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1**: The system shall process multi-story epics through a sequential workflow: SM story creation → DEV development → QA validation → integrated code quality checks → integrated test automation

**FR2**: The SM agent shall create individual story documents, verify successful creation before proceeding to DEV development phase

**FR3**: The DEV agent shall implement story features, and upon completion trigger automatic QA validation through the QA agent

**FR4**: The QA agent shall review completed stories; if validation fails, the system shall repeat the DEV-QA cycle until the story passes QA acceptance criteria

**FR5**: After all stories in an epic complete the SM-Dev-QA cycle, the system shall execute integrated code quality checks on all .py files in the source directory

**FR6**: The integrated code quality checks shall include both basedpyright type checking and ruff linting with automatic fix capabilities, generating JSON error reports for each .py file containing errors

**FR7**: The system shall automatically invoke Claude agents to fix identified basedpyright and ruff issues, then re-execute checks until zero .py files contain errors

**FR8**: Following successful code quality validation, the system shall execute integrated test automation to run all tests in the @tests directory

**FR9**: The integrated test automation shall collect failed/errored test file paths and failure information, generating a summary JSON report

**FR10**: For each test file with errors, the system shall invoke Claude agents to fix the identified issues

**FR11**: The system shall re-execute tests after each fix attempt; if tests still fail, it shall invoke debugpy with test file path, error details, and debug information provided to Claude agents for resolution

**FR12**: The state manager shall track progress across all workflow phases (SM-Dev-QA → code quality → test automation) in the progress.db database

**FR13**: All code quality and test automation functionality shall be natively integrated into autoBMAD without requiring external workflow installations

**FR14**: The system shall only depend on .bmad-core directory and pip-installed libraries required by autoBMAD code

### 2.2 Non-Functional Requirements

**NFR1**: The integration shall maintain backward compatibility with existing epic_automation CLI interface and functionality

**NFR2**: All workflow phases shall support retry mechanisms and error handling without corrupting the progress database

**NFR3**: The system shall support concurrent processing of multiple stories within an epic when experimental concurrent mode is enabled

**NFR4**: Code quality and test automation phases shall complete within reasonable time bounds (target: under 10 minutes for typical epics)

**NFR5**: Error messages and progress reporting shall be clear and actionable throughout all workflow phases

**NFR6**: The system shall preserve existing logging and verbose output capabilities across all integrated workflows

**NFR7**: Basedpyright and ruff shall be installed as part of autoBMAD's pip dependencies, not as separate external tools

**NFR8**: Test automation shall use pytest natively integrated into autoBMAD, not requiring external test workflow installations

### 2.3 Compatibility Requirements

**CR1**: The integration shall maintain existing API compatibility - all current CLI options and arguments shall continue to function as documented

**CR2**: The database schema shall extend existing progress.db structure without breaking backward compatibility with existing epic records

**CR3**: UI/UX consistency shall be maintained - existing command-line interface behavior and output formatting shall remain unchanged

**CR4**: Integration compatibility shall ensure basedpyright and ruff checks can be disabled or bypassed if needed without affecting core epic automation functionality

**CR5**: Test automation shall maintain compatibility with existing test structure and pytest conventions without requiring external workflow dependencies

---

## 3. Technical Constraints and Integration Requirements

### 3.1 Existing Technology Stack

**Languages**: Python 3.x
**Frameworks**: Standard library + BMAD methodology framework
**Database**: SQLite (progress.db for state management)
**Infrastructure**: CLI-based tool, cross-platform compatible
**External Dependencies**:
- BMAD core templates (.bmad-core/)
- pip-installed packages: basedpyright, ruff, pytest, debugpy
- Virtual environment (venv) for dependency isolation

### 3.2 Integration Approach

**Database Integration Strategy**: Extend existing SQLite schema in progress.db to include new workflow phases:
- Add code_quality_phase table with fields: epic_id, file_path, error_count, fix_status, timestamp
- Add test_automation_phase table with fields: epic_id, test_file_path, failure_count, fix_status, debug_info, timestamp
- Maintain backward compatibility with existing epic_processing table

**API Integration Strategy**:
- Extend epic_driver.py CLI to add new workflow phases after QA completion
- Create CodeQualityAgent class that wraps basedpyright and ruff execution
- Create TestAutomationAgent class that wraps pytest execution and debugpy integration
- Maintain existing CLI interface with optional flags to skip quality gates

**Frontend Integration Strategy**:
- N/A - CLI tool only
- Preserve existing command-line interface patterns
- Add progress indicators for new workflow phases

**Testing Integration Strategy**:
- Integrate pytest execution directly into autoBMAD core
- Collect test results in JSON format for analysis
- Implement debugpy integration for failing test diagnosis
- Generate test execution reports in existing logging format

### 3.3 Code Organization and Standards

**File Structure Approach**:
```
autoBMAD/
├── epic_driver.py (extended with quality gates)
├── agents/
│   ├── sm_agent.py (existing)
│   ├── dev_agent.py (existing)
│   ├── qa_agent.py (existing)
│   ├── code_quality_agent.py (NEW)
│   └── test_automation_agent.py (NEW)
├── workflows/
│   ├── basedpyright_workflow.py (NEW - integrated from basedpyright-workflow)
│   ├── ruff_workflow.py (NEW - integrated ruff checks)
│   └── test_automation_workflow.py (NEW - integrated from fixtest-workflow)
└── state_manager.py (extended schema)
```

**Naming Conventions**: Follow existing autoBMAD patterns (snake_case for modules, PascalCase for classes)

**Coding Standards**:
- Basedpyright for type checking (strict mode)
- Ruff for linting (using existing project's ruff configuration if available)
- Black for code formatting (maintain consistency)

**Documentation Standards**:
- Update README.md to document new workflow phases
- Add inline comments for complex quality gate logic
- Maintain existing docstring format

### 3.4 Deployment and Operations

**Build Process Integration**:
- Add basedpyright, ruff, pytest, debugpy to requirements.txt
- Update SETUP.md with new dependencies
- Ensure virtual environment activation includes all quality tools

**Deployment Strategy**:
- Self-contained package - no external workflow installations required
- Single pip install command installs all dependencies
- .bmad-core directory contains all methodology templates

**Monitoring and Logging**:
- Extend existing logging to include quality gate phases
- Add structured logging for basedpyright/ruff results
- Track test execution metrics and debugpy usage

**Configuration Management**:
- Add configuration section in epic_driver.py for quality gate settings
- Allow bypassing quality gates via CLI flags (--skip-quality, --skip-tests)
- Maintain existing configuration patterns

### 3.5 Risk Assessment and Mitigation

**Technical Risks**:
- **Risk**: Basedpyright and ruff may conflict with existing code style
- **Mitigation**: Start with lenient rules and gradually tighten, allow per-file rule overrides

- **Risk**: Debugpy integration may cause performance issues
- **Mitigation**: Only invoke debugpy for persistent test failures, add timeout controls

**Integration Risks**:
- **Risk**: New workflow phases may extend execution time beyond acceptable limits
- **Mitigation**: Implement parallel execution where possible, add progress indicators

- **Risk**: State management database schema changes may corrupt existing progress
- **Mitigation**: Always create database backups before schema modifications, implement rollback mechanisms

**Deployment Risks**:
- **Risk**: New dependencies may conflict with user's existing Python environment
- **Mitigation**: Recommend using isolated venv, provide clear dependency documentation

- **Risk**: Quality gate failures may block epic completion unnecessarily
- **Mitigation**: Implement waivable quality gates, allow epic completion with known issues

**Mitigation Strategies**:
- Implement --skip-quality and --skip-tests flags for emergency bypasses
- Add detailed logging for all quality gate operations
- Create comprehensive error recovery mechanisms
- Maintain backward compatibility with existing epic processing

---

## 4. Epic and Story Structure

### 4.1 Epic Approach

**Epic Structure Decision**: Single epic with multiple coordinated stories, each delivering a distinct workflow phase while maintaining system integrity throughout the integration process.

**Rationale**: The basedpyright-workflow and fixtest-workflow integration represents a unified quality assurance system that builds upon the existing SM-Dev-QA cycle. The workflow phases are sequential and interdependent, making them most effective as a cohesive epic rather than separate features.

---

## 5. Epic 1: Integration of Code Quality and Test Automation into autoBMAD

**Epic Goal**: Integrate basedpyright and ruff code quality checks, along with pytest test automation with debugpy, into the autoBMAD epic automation system to create a unified workflow that processes multi-story epics through complete SM-Dev-QA cycles followed by automated quality assurance gates.

**Integration Requirements**:
- Maintain 100% backward compatibility with existing epic_automation functionality
- Ensure all new workflow phases can be bypassed via CLI flags
- Preserve existing state management and progress tracking
- Integrate basedpyright and ruff as native dependencies, not external tools
- Implement pytest and debugpy integration without external workflow dependencies

### Story 1.1: Extend State Management for Quality Gates

As a **BMAD automation system**,
I want to **extend the SQLite database schema to track code quality and test automation phases**,
so that **progress can be tracked across all workflow phases without losing existing epic data**.

**Acceptance Criteria**:
1. The progress.db schema is extended with code_quality_phase table (epic_id, file_path, error_count, fix_status, timestamp, basedpyright_errors, ruff_errors)
2. The progress.db schema is extended with test_automation_phase table (epic_id, test_file_path, failure_count, fix_status, debug_info, timestamp)
3. State manager can read existing epic records without errors
4. New schema additions are backward compatible with existing data
5. Database backup mechanism is implemented before schema changes

**Integration Verification**:
- IV1: Existing epic processing continues to work without database modifications
- IV2: New schema additions don't interfere with existing SM-Dev-QA workflow
- IV3: Database integrity is maintained across all read/write operations

---

### Story 1.2: Integrate Basedpyright and Ruff Code Quality Checks

As a **BMAD automation system**,
I want to **natively integrate basedpyright type checking and ruff linting with auto-fix capabilities**,
so that **code quality can be validated automatically after QA completion without external tool dependencies**.

**Acceptance Criteria**:
1. Basedpyright is added as a direct dependency in requirements.txt
2. Ruff is added as a direct dependency in requirements.txt
3. CodeQualityAgent class is created to wrap basedpyright and ruff execution
4. Basedpyright_workflow.py module is integrated to execute type checking on all .py files
5. Ruff_workflow.py module is integrated to execute linting with --fix auto-correction
6. JSON error reports are generated for each .py file with identified issues
7. Claude agents are automatically invoked to fix identified basedpyright and ruff issues
8. System repeats quality checks until zero errors remain or max iterations reached
9. Quality gate can be bypassed via --skip-quality CLI flag

**Integration Verification**:
- IV1: Existing SM-Dev-QA workflow continues to function without quality gates
- IV2: Code quality checks only execute after all stories pass QA
- IV3: Basedpyright and ruff execution doesn't interfere with existing CLI interface

---

### Story 1.3: Integrate Test Automation with Debugpy

As a **BMAD automation system**,
I want to **natively integrate pytest test execution with debugpy for persistent failure diagnosis**,
so that **test automation can be performed automatically after code quality validation without external workflow dependencies**.

**Acceptance Criteria**:
1. Pytest is added as a direct dependency in requirements.txt
2. Debugpy is added as a direct dependency in requirements.txt
3. TestAutomationAgent class is created to manage test execution workflow
4. Test_automation_workflow.py module is integrated to execute all tests in @tests directory
5. Failed/errored test file paths and failure information are collected in JSON format
6. Summary JSON report is generated for all test execution results
7. Claude agents are automatically invoked to fix identified test issues
8. System re-executes tests after each fix attempt
9. Debugpy is invoked for tests that fail repeatedly, providing test path, error details, and debug information to Claude agents
10. Test automation gate can be bypassed via --skip-tests CLI flag

**Integration Verification**:
- IV1: Existing epic processing continues without test automation when skipped
- IV2: Test execution only occurs after successful code quality validation
- IV3: Debugpy integration doesn't interfere with normal test execution flow

---

### Story 1.4: Extend Epic Driver with Quality Gate Orchestration

As a **BMAD automation system**,
I want to **extend epic_driver.py to orchestrate the complete workflow from story creation through quality gates**,
so that **the entire multi-phase workflow executes seamlessly with proper error handling and progress tracking**.

**Acceptance Criteria**:
1. Epic driver processes epics through complete workflow: SM → Dev → QA → Code Quality → Test Automation
2. State manager tracks progress across all workflow phases
3. Quality gates execute only after all epic stories complete SM-Dev-QA cycle
4. Retry mechanisms work across all workflow phases without corrupting progress database
5. Error handling provides clear, actionable feedback for failures in any phase
6. CLI interface is extended with --skip-quality and --skip-tests flags
7. Verbose logging includes all quality gate operations
8. Concurrent processing mode (experimental) is compatible with quality gates

**Integration Verification**:
- IV1: Existing CLI options continue to function as documented
- IV2: New quality gates integrate seamlessly with existing workflow
- IV3: Progress tracking is accurate across all workflow phases
- IV4: Error recovery mechanisms work without manual intervention

---

### Story 1.5: Documentation and Testing Integration

As a **BMAD automation system**,
I want to **update all documentation and create integration tests for the complete workflow**,
so that **users understand the new workflow phases and the system can be validated end-to-end**.

**Acceptance Criteria**:
1. README.md is updated to document new quality gate workflow phases
2. SETUP.md is updated with basedpyright, ruff, pytest, and debugpy dependencies
3. Integration tests verify complete workflow: story creation → development → QA → code quality → test automation
4. Example epic is created demonstrating multi-story processing with quality gates
5. Troubleshooting guide is added for common quality gate issues
6. Performance benchmarks are established for typical epic processing times

**Integration Verification**:
- IV1: Documentation accurately reflects actual system behavior
- IV2: New users can successfully set up and run the complete workflow
- IV3: Integration tests validate all workflow phases work together correctly

---

## Summary

This PRD outlines the complete integration of basedpyright-workflow and fixtest-workflow functionality into autoBMAD/epic_automation. The enhancement follows a structured approach:

1. **Database Schema Extension** - Track quality gates without breaking existing functionality
2. **Code Quality Integration** - Native basedpyright and ruff with automatic fixing
3. **Test Automation Integration** - Pytest and debugpy for comprehensive testing
4. **Orchestration Enhancement** - Seamless workflow across all phases
5. **Documentation and Testing** - Complete validation and user guidance

The integration maintains 100% backward compatibility while adding powerful quality assurance capabilities to the BMAD workflow.

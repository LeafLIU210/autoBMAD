"""
Shared fixtures for spec_automation tests.

This module provides common fixtures used across all test files in the spec_automation test suite.
"""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_sdk():
    """Create a mock SDK instance."""
    sdk = Mock()
    sdk.query = AsyncMock(return_value="Mocked response")
    return sdk


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_progress.db"


@pytest.fixture
def sample_story_path(temp_dir):
    """Create a sample story file for testing."""
    story_content = """# Story 1.5: Integration Testing and Documentation

## Status
**In Progress**

---

## Story

**As a** developer integrating and validating the complete spec_automation module,
**I want** to implement comprehensive integration testing, documentation, and examples,
**so that** the module is production-ready with complete documentation, validated workflows, example usage, and >80% test coverage across all components.

---

## Acceptance Criteria

1. Create comprehensive `README.md` with usage instructions and examples
2. Develop integration tests covering main workflow scenarios
3. Create example planning documents demonstrating capabilities
4. Verify all tests pass with >80% coverage
5. Add docstrings and code documentation throughout
6. Validate against real-world planning document formats
7. Performance testing and optimization
8. Final code review and quality gate validation

---

## Tasks / Subtasks

- [ ] Task 1: Create comprehensive module documentation
- [ ] Task 2: Develop integration test suite
- [ ] Task 3: Create example planning documents
- [ ] Task 4: Verify test coverage and quality
- [ ] Task 5: Add comprehensive code documentation
- [ ] Task 6: Validate real-world document formats
- [ ] Task 7: Performance testing and optimization
- [ ] Task 8: Final validation and code review

"""
    story_file = temp_dir / "test_story.md"
    story_file.write_text(story_content)
    return story_file


@pytest.fixture
def sample_sprint_change_proposal_path(temp_dir):
    """Create a sample Sprint Change Proposal document."""
    content = """# Sprint Change Proposal: Enhanced Testing Framework

## Status
**Proposed**

---

## Overview

**Sprint:** 2026.01
**Requester:** Development Team
**Date:** 2026-01-09

This proposal outlines enhancements to the testing framework to improve coverage, reliability, and developer productivity.

---

## Problem Statement

Current testing framework lacks:
- Comprehensive integration tests
- Real-world scenario validation
- Performance benchmarking
- Documentation and examples

---

## Proposed Solution

Implement comprehensive testing suite including:
1. Integration tests for complete workflows
2. Example documents for common use cases
3. Performance benchmarks
4. Complete API documentation

---

## Requirements

### Functional Requirements

1. **Integration Test Suite**
   - Test complete Dev-QA workflow
   - Validate state management
   - Test error handling scenarios

2. **Example Documents**
   - Sprint Change Proposal template
   - Functional Specification example
   - Technical Plan example

3. **Documentation**
   - Comprehensive README.md
   - API reference documentation
   - Usage examples

### Non-Functional Requirements

1. **Performance**
   - Document parsing: <5 seconds
   - Complete workflow: <5 minutes

2. **Quality**
   - Test coverage: >80%
   - All quality gates pass

---

## Acceptance Criteria

1. [ ] Create integration test suite with >80% coverage
2. [ ] Generate 3 example planning documents
3. [ ] Complete README.md with examples
4. [ ] All quality gates pass (Ruff, BasedPyright, Pytest)
5. [ ] Performance benchmarks documented

---

## Implementation Plan

### Phase 1: Test Suite Development
- Create conftest.py with shared fixtures
- Develop integration tests
- Add unit tests for all modules

### Phase 2: Example Documents
- Create Sprint Change Proposal example
- Create Functional Specification example
- Create Technical Plan example

### Phase 3: Documentation
- Write comprehensive README.md
- Add docstrings throughout codebase
- Create API reference

### Phase 4: Validation
- Run quality gates
- Verify coverage metrics
- Performance testing

---

## Success Metrics

- Test coverage: >80%
- Quality gates: 100% pass rate
- Documentation: Complete and actionable
- Performance: Within specified limits

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Test execution time | Medium | Optimize test fixtures |
| Documentation drift | Low | Automated validation |
| Quality gate failures | High | Early integration |

"""
    file_path = temp_dir / "sprint_change_proposal.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_functional_spec_path(temp_dir):
    """Create a sample Functional Specification document."""
    content = """# Functional Specification: Document Parser Module

## Status
**Approved**

---

## Overview

**Module:** spec_automation.doc_parser
**Version:** 1.0
**Date:** 2026-01-09

The Document Parser module extracts structured data from Markdown planning documents, supporting Sprint Change Proposals, Functional Specifications, and Technical Plans.

---

## Purpose

Parse and extract structured information from planning documents to enable automated workflow processing and requirement tracking.

---

## Functional Requirements

### FR-1: Document Parsing
**Priority:** High
**Description:** Parse Markdown documents and extract structured data

**Details:**
- Support common Markdown structures (headers, lists, tables)
- Extract document title from H1 headers
- Parse requirements lists
- Extract acceptance criteria
- Parse implementation tasks/subtasks

**Acceptance Criteria:**
- [ ] Correctly parse document title from `#` header
- [ ] Extract requirements from bulleted lists under "Requirements" section
- [ ] Parse acceptance criteria from numbered lists
- [ ] Handle edge cases (empty sections, malformed markdown)

### FR-2: Data Structure
**Priority:** High
**Description:** Return structured data dictionary

**Details:**
- Consistent output format
- Type-safe data extraction
- Error handling for missing sections

**Acceptance Criteria:**
- [ ] Return dictionary with keys: title, requirements, acceptance_criteria, tasks
- [ ] All extracted text preserved accurately
- [ ] Handle missing sections gracefully (return empty lists)

### FR-3: Error Handling
**Priority:** Medium
**Description:** Handle malformed or invalid documents

**Details:**
- Validate file existence
- Handle encoding issues
- Log parsing errors

**Acceptance Criteria:**
- [ ] Raise appropriate exceptions for missing files
- [ ] Log parsing warnings
- [ ] Return partial results when possible

---

## Non-Functional Requirements

### Performance
- Parse typical document (<5KB): <1 second
- Parse large document (<50KB): <5 seconds
- Memory usage: Reasonable for document size

### Reliability
- 99% success rate for valid documents
- Graceful degradation for edge cases
- Comprehensive error logging

### Usability
- Simple API (single function call)
- Clear error messages
- Type hints for all functions

---

## Technical Specification

### Class: DocumentParser

```python
class DocumentParser:
    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        \"\"\"Parse document and return structured data.\"\"\"
        pass

    def parse_string(self, content: str) -> Dict[str, Any]:
        \"\"\"Parse document content from string.\"\"\"
        pass
```

### Data Model

```python
{
    "title": str,
    "requirements": List[str],
    "acceptance_criteria": List[str],
    "tasks": List[str],
    "metadata": Dict[str, Any]
}
```

---

## Testing Requirements

### Unit Tests
- Test all extraction methods
- Test edge cases
- Test error handling

### Integration Tests
- Test with real planning documents
- Test complete workflow integration
- Test state manager integration

### Performance Tests
- Benchmark parsing time
- Test with large documents
- Memory usage profiling

---

## Constraints

- Python 3.10+
- No external dependencies beyond standard library
- Must work offline
- No .bmad-core dependency

---

## Assumptions

- Documents use standard Markdown formatting
- UTF-8 encoding
- File system access available
- No encrypted or protected documents

---

## Dependencies

- Python standard library
- pathlib (file handling)
- re (regular expressions)
- logging (error tracking)

---

## Open Issues

1. Should we support YAML frontmatter?
2. How to handle nested requirements?
3. Extensibility for custom document types?

---

## Approval

**Author:** Development Team
**Reviewer:** QA Team
**Approved:** 2026-01-09

"""
    file_path = temp_dir / "functional_spec.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_technical_plan_path(temp_dir):
    """Create a sample Technical Plan document."""
    content = """# Technical Plan: Testing Framework Enhancement

## Status
**Planning**

---

## Overview

**Project:** Testing Framework Enhancement
**Version:** 1.0
**Date:** 2026-01-09
**Owner:** Development Team

This technical plan outlines the implementation strategy for enhancing the spec_automation testing framework with comprehensive integration tests, documentation, and examples.

---

## Executive Summary

### Objectives
- Achieve >80% test coverage across all components
- Create production-ready documentation
- Provide real-world example documents
- Implement performance benchmarking

### Success Criteria
- All tests pass (100% pass rate)
- Documentation complete and actionable
- Performance within specified limits
- Quality gates enforce standards

---

## Technical Approach

### Architecture Overview

The spec_automation system consists of the following components:
- SpecDriver (main orchestrator)
- Dev Agent (development agent)
- QA Agent (quality assurance agent)
- State Manager (state tracking)
- Document Parser (parsing component)
- Quality Gates (quality enforcement)

### Component Design

#### 1. Test Suite Architecture
**Technology:** pytest with async support
**Structure:**
- Unit tests for each module
- Integration tests for workflows
- End-to-end tests with real documents

#### 2. Fixture Management
**Implementation:** conftest.py
**Features:**
- Shared fixtures across test files
- Automatic cleanup
- Mock SDK for isolated testing

#### 3. Documentation System
**Format:** Markdown + docstrings
**Structure:**
- README.md for user guide
- API reference from docstrings
- Examples with code samples

---

## Implementation Details

### Phase 1: Test Infrastructure (Week 1)

#### Task 1.1: Fixture Framework
**Implementation:**
```python
@pytest.fixture
def mock_sdk():
    # Create mock SDK with async support
    # Configure for isolated testing
    pass

@pytest.fixture
def sample_documents():
    # Create test document templates
    # Validate document structure
    pass
```

#### Task 1.2: Unit Test Coverage
**Target Modules:**
- doc_parser.py: 100%
- spec_state_manager.py: 100%
- prompts.py: 90%
- quality_gates.py: 90%

**Test Structure:**
```python
class TestDocumentParser:
    def test_parse_title(self, sample_doc):
        assert parser.parse_document(sample_doc)['title'] == "Expected"
```

### Phase 2: Integration Testing (Week 2)

#### Task 2.1: Workflow Tests
**Test Scenarios:**
1. Complete Dev-QA cycle
2. Error handling and recovery
3. State management persistence
4. Quality gate enforcement

#### Task 2.2: Cross-Module Integration
**Test Cases:**
- SpecDevAgent → SpecStateManager
- SpecQAAgent → SpecStateManager
- SpecDriver → All components

### Phase 3: Documentation (Week 3)

#### Task 3.1: README.md Structure
```markdown
# spec_automation

- Installation
- Quick Start
- API Reference
- Examples
- Testing
```

#### Task 3.2: Docstring Enhancement
**Format:** Google style
**Coverage:** All public functions/classes

### Phase 4: Performance & Validation (Week 4)

#### Task 4.1: Benchmark Suite
**Metrics:**
- Document parsing time
- TDD cycle duration
- Database operations
- Memory usage

#### Task 4.2: Quality Gates
**Tools:**
- Ruff: Code style
- BasedPyright: Type checking
- Pytest: Test execution

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Test execution time | Medium | Medium | Optimize fixtures, parallel execution |
| Mock SDK limitations | Low | High | Implement comprehensive mocks |
| Documentation drift | Medium | Low | Automated validation |
| Quality gate failures | High | High | Early integration, continuous testing |

### Mitigation Strategies

1. **Continuous Integration**
   - Run tests on every commit
   - Automated quality gate checks
   - Coverage reporting

2. **Test Data Management**
   - Centralized fixture repository
   - Version-controlled test documents
   - Automated cleanup

3. **Documentation Quality**
   - Docstring validation
   - Example code testing
   - User feedback loop

---

## Resource Requirements

### Development
- 1 Developer (4 weeks)
- Test automation tools
- Documentation platform

### Infrastructure
- CI/CD pipeline
- Test environment
- Documentation hosting

### Budget
- Development time: 160 hours
- Tool licenses: None (all open source)
- Infrastructure: Existing

---

## Timeline

### Milestones

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1 | Test Infrastructure | conftest.py, unit tests |
| 2 | Integration Tests | Workflow tests, E2E tests |
| 3 | Documentation | README.md, API docs |
| 4 | Validation | Performance benchmarks |

### Critical Path
1. Test infrastructure setup
2. Unit test completion
3. Integration test development
4. Documentation review
5. Quality gate validation

---

## Success Metrics

### Quantitative
- Test coverage: >80%
- Test pass rate: 100%
- Documentation completeness: 100%
- Performance: Within limits

### Qualitative
- Code maintainability
- Documentation clarity
- User adoption
- Developer satisfaction

---

## Open Questions

1. Should we implement test parallelization?
2. How to handle flaky tests?
3. Performance regression detection?
4. Documentation deployment strategy?

---

## Approval and Sign-off

**Prepared by:** Development Team
**Technical Review:** TBD
**Project Approval:** TBD

**Signatures:**
- Development Lead: ________________
- QA Lead: ________________
- Product Owner: ________________

"""
    file_path = temp_dir / "technical_plan.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

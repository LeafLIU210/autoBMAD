# Epic: Example Epic with Quality Gates

**Status**: Approved
**Version**: 1.0
**Date**: 2026-01-05

---

## Overview

This epic demonstrates the complete 5-phase workflow with quality gates and test automation. It includes multiple stories that showcase different scenarios:

- Story 001: Simple function implementation
- Story 002: Class with type hints
- Story 003: Error handling
- Story 004: Testing patterns

## Cancel Scope Safety Requirements

This epic runs with **Cancel Scope safety measures** enabled to prevent anyio-related async errors:

### Safety Features
- **No External Timeouts**: System uses SDK's built-in `max_turns` (150 turns) instead of external timeouts
- **Sequential Execution**: Quality gates run one after another (Ruff → BasedPyright → Pytest)
- **Error Suppression**: Cancel Scope errors are caught and don't interrupt execution

### What You'll See
- Quality gates execute sequentially without concurrent processing
- Cancel Scope errors (if any) appear in logs but are suppressed automatically
- System continues normally even if Cancel Scope errors are logged
- No timeout configuration needed - SDK handles all timing internally

### For Developers
If you're studying this epic to understand the codebase:
- No `asyncio.wait_for()` wrappers around SDK calls
- No external timeout configuration
- Sequential processing within quality gates
- Errors are caught and logged, not propagated

See `docs/evaluation/cancel-scope-error-analysis.md` for technical details.

## Expected Quality Gate Behavior

### Phase 2: Quality Gates

After all stories complete the SM-Dev-QA cycle, quality gates will execute:

1. **Basedpyright Type Checking**
   - Validates all type hints are correct
   - Checks for missing type annotations
   - Reports any type inconsistencies

2. **Ruff Linting**
   - Automatically fixes PEP 8 violations
   - Reports unused imports and variables
   - Checks code complexity
   - Enforces import sorting

3. **Retry Logic**
   - Quality gates have max 3 retry attempts
   - Failed checks trigger automated fixes
   - Persistent failures are reported

### Phase 3: Test Automation

After quality gates pass:

1. **Pytest Execution**
   - Runs all tests in the test suite
   - Generates coverage reports
   - Reports test failures with details

2. **Debugpy Integration**
   - Activates for persistent test failures
   - Provides 300-second debugging session
   - Helps diagnose complex issues

3. **Retry Logic**
   - Test automation has max 5 retry attempts
   - Debugpy used after 3 failures
   - Final status reported

---

## Stories

### Story 001: Create a Simple Function

**As a** developer,
**I want to** create a simple function with proper type hints,
**So that** I can demonstrate quality gate functionality.

**Acceptance Criteria**:
- [ ] Function is created with correct name
- [ ] Function has proper type hints
- [ ] Function passes basedpyright type checking
- [ ] Function passes ruff linting
- [ ] Function has corresponding test

**Tasks / Subtasks**:
- [ ] Task 1: Create function in src/utils.py
- [ ] Task 2: Add type hints (str -> str)
- [ ] Task 3: Add docstring
- [ ] Task 4: Create test in tests/test_utils.py
- [ ] Task 5: Verify quality gates pass

**Dev Notes**:
- Function should be simple and straightforward
- Quality gates will check for type hints
- Ruff will check formatting and imports

---

### Story 002: Implement a Data Class

**As a** developer,
**I want to** create a data class with proper type annotations,
**So that** I can demonstrate advanced type checking.

**Acceptance Criteria**:
- [ ] Class is defined with @dataclass decorator
- [ ] All fields have type annotations
- [ ] Class includes validation logic
- [ ] Basedpyright validates all types
- [ ] Tests cover class functionality

**Tasks / Subtasks**:
- [ ] Task 1: Create User class in src/models.py
- [ ] Task 2: Add dataclass fields with types
- [ ] Task 3: Add field validation
- [ ] Task 4: Create comprehensive tests
- [ ] Task 5: Verify quality gates

**Dev Notes**:
- Use dataclasses module
- Include Optional fields to test basedpyright
- Add validation in __post_init__

---

### Story 003: Add Error Handling

**As a** developer,
**I want to** add proper error handling to functions,
**So that** the code is robust and maintainable.

**Acceptance Criteria**:
- [ ] Functions handle common exceptions
- [ ] Custom exceptions are defined
- [ ] Error messages are clear and helpful
- [ ] Ruff checks for exception handling patterns
- [ ] Tests verify error scenarios

**Tasks / Subtasks**:
- [ ] Task 1: Define custom exceptions
- [ ] Task 2: Add try-except blocks
- [ ] Task 3: Add logging for errors
- [ ] Task 4: Create error scenario tests
- [ ] Task 5: Verify quality gates

**Dev Notes**:
- Use specific exception types
- Include context in error messages
- Log errors appropriately

---

### Story 004: Implement Testing Patterns

**As a** developer,
**I want to** demonstrate advanced testing patterns,
**So that** I can show pytest capabilities.

**Acceptance Criteria**:
- [ ] Tests use fixtures
- [ ] Parametrized tests are included
- [ ] Mock objects are used appropriately
- [ ] Test coverage is comprehensive
- [ ] Tests pass consistently

**Tasks / Subtasks**:
- [ ] Task 1: Create pytest fixtures
- [ ] Task 2: Add parametrized tests
- [ ] Task 3: Use mock for external dependencies
- [ ] Task 4: Add test for edge cases
- [ ] Task 5: Run test automation

**Dev Notes**:
- Use pytest fixtures for setup
- Parametrize similar test cases
- Mock external API calls
- Test both happy path and edge cases

---

## Step-by-Step Execution Guide

### Prerequisites

1. **Install Dependencies**
   ```bash
   pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0
   ```

2. **Verify Installation**
   ```bash
   basedpyright --version
   ruff --version
   pytest --version
   ```

3. **Create Virtual Environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Execution Steps

#### Step 1: Run Complete Workflow

Execute the epic through all 5 phases:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/examples/example-epic-with-quality-gates.md
```

**Expected Output**:
```
Phase 1: SM-Dev-QA Cycle
├── Story 001: Processing...
├── Story 002: Processing...
├── Story 003: Processing...
└── Story 004: Processing...

Phase 2: Quality Gates
├── Basedpyright: Checking types...
├── Ruff: Linting code...
└── Status: PASSED

Phase 3: Test Automation
├── Pytest: Running tests...
├── Coverage: Generating report...
└── Status: PASSED

Phase 4: Orchestration
└── Epic completed successfully

Phase 5: Documentation
└── All tasks marked complete
```

#### Step 2: Verify Quality Gates

After the workflow completes, verify quality gates:

```bash
# Check basedpyright results
basedpyright src/

# Check ruff results
ruff check --diff src/
```

**Expected Results**:
- No type errors from basedpyright
- No linting errors from ruff
- Any auto-fixed issues shown by ruff

#### Step 3: Run Tests Manually

Verify test automation results:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Expected Results**:
- All tests pass
- Coverage report generated in htmlcov/
- No failing tests

#### Step 4: Check with Skip Options

Test skipping quality gates:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/examples/example-epic-with-quality-gates.md --skip-quality
```

**Expected Behavior**:
- Phases 1, 3, 4, 5 execute
- Phase 2 (Quality Gates) is skipped
- Test automation still runs

Test skipping test automation:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/examples/example-epic-with-quality-gates.md --skip-tests
```

**Expected Behavior**:
- Phases 1, 2, 4, 5 execute
- Phase 3 (Test Automation) is skipped
- Quality gates still run

Test skipping both:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/examples/example-epic-with-quality-gates.md --skip-quality --skip-tests
```

**Expected Behavior**:
- Only Phase 1 (SM-Dev-QA) and Phases 4-5 execute
- Quality gates and test automation are skipped

### Troubleshooting Quality Gates

#### Issue: Basedpyright Reports Type Errors

**Symptom**: Quality gates fail with type errors

**Solution**:
1. Check the specific error messages
2. Add missing type hints
3. Fix type inconsistencies
4. Re-run the epic

Example fix:
```python
# Before
def process_data(data):
    return data.strip()

# After
def process_data(data: str) -> str:
    return data.strip()
```

#### Issue: Ruff Reports Linting Errors

**Symptom**: Quality gates fail with linting errors

**Solution**:
1. Run ruff with auto-fix: `ruff check --fix src/`
2. Review any remaining issues
3. Fix manually if needed
4. Re-run the epic

Example auto-fix:
```bash
# Ruff will automatically fix:
# - Import sorting
# - Code formatting
# - Unused variables
ruff check --fix src/
```

#### Issue: Tests Fail

**Symptom**: Test automation phase reports failures

**Solution**:
1. Review test failure messages
2. Check if failures are consistent
3. Fix the underlying code issues
4. Debugpy will activate after 3 attempts
5. Re-run the epic

**Debugpy Usage**:
```bash
# Debugpy activates automatically
# Or run manually:
pytest tests/ --pdb
```

### Quality Gate Metrics

After running the epic, you can check quality metrics:

```bash
# Basedpyright statistics
basedpyright src/ --output-format=json | jq '.diagnostics | length'

# Ruff statistics
ruff check src/ --output-format=json | jq '. | length'

# Test coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Expected Quality Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Type Errors** | 0 | Basedpyright should report no type errors |
| **Linting Errors** | 0 | Ruff should report no linting errors |
| **Test Pass Rate** | 100% | All tests should pass |
| **Code Coverage** | >80% | Tests should cover most code |
| **Retry Attempts** | <3 | Quality gates should pass in <3 attempts |

---

## Configuration Files

This epic expects the following configuration in `pyproject.toml`:

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
reportMissingImports = true
reportMissingTypeStubs = true

[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "F", "W", "I", "N", "UP", "ANN", "S", "B", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PT", "Q", "RSE", "RET", "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PL", "TRY", "FLY", "NPY", "PERF", "FURB", "LOG", "RUF"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=src"
```

---

## Learning Objectives

By running this epic, you will learn:

1. **How quality gates integrate** into the BMAD workflow
2. **How to write code** that passes type checking
3. **How to use ruff** for code quality and auto-fix
4. **How pytest** works for test automation
5. **How to debug** persistent failures with debugpy
6. **How to configure** quality tools via pyproject.toml
7. **How to skip phases** when needed with CLI flags

---

## Next Steps

After completing this epic:

1. **Experiment with Quality Gates**
   - Try introducing type errors and see basedpyright catch them
   - Run ruff without auto-fix to see violations
   - Adjust pyproject.toml settings

2. **Explore Test Patterns**
   - Add more test cases
   - Try different pytest features
   - Experiment with fixtures and parametrization

3. **Use Quality Gates in Your Projects**
   - Copy this epic structure
   - Adapt the stories to your needs
   - Run quality gates on your own code

---

## Support

If you encounter issues:

1. Check the [troubleshooting guide](../../troubleshooting/quality-gates.md)
2. Review the [user guide](../../user-guide/quality-gates.md)
3. Run with `--verbose` for detailed logs
4. Check quality gate tools documentation:
   - [Basedpyright docs](https://github.com/ethanhs/basedpyright)
   - [Ruff docs](https://github.com/charliermarsh/ruff)
   - [Pytest docs](https://docs.pytest.org/)
   - [Debugpy docs](https://github.com/microsoft/debugpy)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-08 | 1.1 | Added Cancel Scope safety requirements section explaining SDK max_turns, sequential execution, and error handling | Dev Agent |
| 2026-01-05 | 1.0 | Initial example epic creation | BMAD Team |

---

## License

This example epic is part of the autoBMAD system and follows the same license terms.

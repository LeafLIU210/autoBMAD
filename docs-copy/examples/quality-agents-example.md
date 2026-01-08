# Example Epic: Quality Gates Integration

This example demonstrates the complete workflow of an epic with integrated quality gates, showing how the Dev-QA cycle works with automatic quality validation.

## Overview

This epic implements a simple data processing utility and demonstrates:
- Complete Dev-QA cycle execution
- Quality gates integration (Ruff → BasedPyright → Pytest)
- CLI flag usage for different scenarios
- Quality gate output interpretation
- Error handling and troubleshooting

---

## Epic: Implement Data Processing Utility

### Story 1: Create Data Processor Module
**As a** developer,
**I want to** create a data processor module with type hints,
**So that** I can process user data with proper validation.

**Acceptance Criteria**:
- [ ] Create `src/data_processor.py` with data processing functions
- [ ] Add type hints to all functions
- [ ] Include proper error handling
- [ ] Pass Ruff linting
- [ ] Pass BasedPyright type checking
- [ ] Include comprehensive tests

**Dev Notes**:
- Write functions with type annotations
- Use proper docstrings
- Include error handling
- Follow PEP 8 style guidelines

---

### Story 2: Add Data Validation
**As a** developer,
**I want to** add data validation to the processor,
**So that** invalid data is rejected before processing.

**Acceptance Criteria**:
- [ ] Add validation functions to data processor
- [ ] Validate input parameters
- [ ] Return appropriate error messages
- [ ] Include validation tests
- [ ] Pass all quality gates

**Dev Notes**:
- Implement validation logic
- Use type hints for validation functions
- Test edge cases
- Ensure good error messages

---

### Story 3: Create CLI Interface
**As a** user,
**I want to** use the data processor from command line,
**So that** I can process files easily.

**Acceptance Criteria**:
- [ ] Create CLI script `src/cli.py`
- [ ] Accept file input and output paths
- [ ] Display processing results
- [ ] Handle errors gracefully
- [ ] Include CLI tests
- [ ] Pass quality gates

**Dev Notes**:
- Use argparse for CLI
- Add help text
- Handle file I/O errors
- Test with sample data

---

## Quality Gates Execution

When this epic is processed, quality gates execute automatically after the Dev-QA cycle completes for each story.

### Expected Quality Gate Flow

```
=== Phase 1: Dev-QA Cycle ===
Processing story 1: Create Data Processor Module
  ✓ Dev phase completed
  ✓ QA phase passed
  → Story status: Ready for Done

Processing story 2: Add Data Validation
  ✓ Dev phase completed
  ✓ QA phase passed
  → Story status: Ready for Done

Processing story 3: Create CLI Interface
  ✓ Dev phase completed
  ✓ QA phase passed
  → Story status: Ready for Done

=== Phase 2: Quality Gates ===

=== Quality Gate 1/3: Ruff Linting ===
Starting Ruff quality check...
Ruff: Checking src/data_processor.py
Ruff: Checking src/cli.py
Ruff: Found 3 issues (2 auto-fixable)
✓ Ruff quality gate PASSED in 2.3s

Auto-fixed issues:
- F401: Removed unused import in src/cli.py
- E501: Formatted long lines in src/data_processor.py

=== Quality Gate 2/3: BasedPyright Type Checking ===
Starting BasedPyright quality check...
BasedPyright: Type checking src/data_processor.py
BasedPyright: Type checking src/cli.py
BasedPyright: Found 1 issue
✓ BasedPyright quality gate PASSED in 4.1s

Issues found and fixed:
- Missing type annotation for parameter 'config' in data_processor.py
  → Added: def process_data(data: dict, config: dict) -> dict:

=== Quality Gate 3/3: Pytest Execution ===
Starting pytest execution...
Pytest: Collected 5 tests
Pytest: Running tests in tests/
Pytest: test_data_processor.py::test_process_valid_data PASSED
Pytest: test_data_processor.py::test_process_invalid_data PASSED
Pytest: test_data_processor.py::test_validation PASSED
Pytest: test_cli.py::test_cli_help PASSED
Pytest: test_cli.py::test_cli_process PASSED
Pytest: 5 passed in 1.2s
✓ Pytest quality gate PASSED in 1.2s

=== Quality Gates Pipeline COMPLETED SUCCESSFULLY in 7.6s ===

Epic Processing Complete: 3/3 stories succeeded
```

---

## Running This Epic

### Full Pipeline (All Quality Gates)

```bash
# Process the epic with all quality gates enabled
python -m autoBMAD.epic_automation.epic_driver docs/examples/quality-agents-example.md

# With verbose output
python -m autoBMAD.epic_automation.epic_driver docs/examples/quality-agents-example.md --verbose
```

### Development Mode (Skip Quality Gates)

For faster iteration during development:

```bash
# Skip quality gates for rapid Dev-QA cycling
python -m autoBMAD.epic_automation.epic_driver docs/examples/quality-agents-example.md --skip-quality

# Or skip just pytest
python -m autoBMAD.epic_automation.epic_driver docs/examples/quality-agents-example.md --skip-tests
```

### Quality Check Only

Run quality gates without tests:

```bash
# Skip pytest only (run Ruff and BasedPyright)
python -m autoBMAD.epic_automation.epic_driver docs/examples/quality-agents-example.md --skip-tests
```

---

## Expected Output Examples

### Quality Gates Success Output

```
=== Quality Gates Pipeline ===
Starting quality gates pipeline for epic: quality-agents-example.md

Quality Gate 1/3: Ruff Linting
  Status: PASSED
  Duration: 2.3s
  Issues found: 3
  Issues auto-fixed: 2

Quality Gate 2/3: BasedPyright Type Checking
  Status: PASSED
  Duration: 4.1s
  Issues found: 1
  Issues fixed: 1

Quality Gate 3/3: Pytest Execution
  Status: PASSED
  Duration: 1.2s
  Tests run: 5
  Tests passed: 5

Overall Status: ✓ SUCCESS
Total Duration: 7.6s
```

### Quality Gates Failure Output

```
=== Quality Gates Pipeline ===
Starting quality gates pipeline for epic: quality-agents-example.md

Quality Gate 1/3: Ruff Linting
  Status: PASSED
  Duration: 2.1s

Quality Gate 2/3: BasedPyright Type Checking
  Status: FAILED
  Duration: 3.8s
  Error: Type annotation missing for function 'process_data'

Quality Gate 3/3: Pytest Execution
  Status: SKIPPED (due to previous failure)

✗ Quality gates pipeline FAILED with 1 error(s)

Error Details:
  - BasedPyright: Missing type annotation for function 'process_data'
    → Fix: Add type hints to function parameters and return type

Note: Quality gate failures are non-blocking. Epic processing continues.
```

### Cancel Scope Error (Suppressed)

If you see Cancel Scope errors in logs:

```
2026-01-08 10:15:23 - epic_driver - ERROR - Cancel scope error detected: Attempted to exit cancel scope in a different task than it was entered in
2026-01-08 10:15:23 - epic_driver - INFO - Quality gates pipeline COMPLETED SUCCESSFULLY in 7.6s
```

**This is expected and can be ignored:**
- Error is automatically suppressed
- Processing continues normally
- Quality gates still function correctly
- No action required

See `docs/troubleshooting/quality-gates.md` for details.

---

## Quality Gate Details

### Ruff Agent

**Purpose**: Fast linting and auto-fixing of code style issues

**Checks**:
- Code style (PEP 8)
- Unused imports
- Undefined variables
- Code formatting
- Import sorting

**Auto-fixable Issues**:
- F401: Unused imports
- E501: Line too long
- I001: Import in wrong order
- E701: Multiple statements on one line

**Example Output**:
```bash
# Manual execution
ruff check --fix src/

# Results
Found 3 issues (2 auto-fixable)
1. F401: Unused import 'os' (src/cli.py:5)
2. E501: Line too long (src/data_processor.py:23)
3. I001: Import in wrong order (src/data_processor.py:1)

✓ Fixed 2 issues automatically
✗ 1 issue requires manual fix
```

### BasedPyright Agent

**Purpose**: Static type checking to catch type errors

**Checks**:
- Missing type annotations
- Incorrect type usage
- Unknown types
- Optional type handling

**Common Fixes**:
```python
# Before
def process_data(data, config):
    return data.strip()

# After
def process_data(data: str, config: dict[str, str]) -> str:
    return data.strip()
```

**Example Output**:
```bash
# Manual execution
basedpyright src/

# Results
BasedPyright: Found 2 issues in 2 files
1. Missing type annotation for 'data' (src/data_processor.py:10)
2. Missing return type annotation (src/data_processor.py:10)

✓ Fixed 1 issue automatically
✗ 1 issue requires manual fix
```

### Pytest Agent

**Purpose**: Execute test suite with debugging support

**Features**:
- Automatic test discovery
- Coverage reporting
- Debugpy integration (after 3 failures)
- Parallel execution support

**Test Structure**:
```
tests/
├── test_data_processor.py
│   ├── test_process_valid_data()
│   ├── test_process_invalid_data()
│   └── test_validation()
└── test_cli.py
    ├── test_cli_help()
    └── test_cli_process()
```

**Example Output**:
```bash
# Manual execution
pytest tests/ -v

# Results
collected 5 items

tests/test_data_processor.py::test_process_valid_data PASSED
tests/test_data_processor.py::test_process_invalid_data PASSED
tests/test_data_processor.py::test_validation PASSED
tests/test_cli.py::test_cli_help PASSED
tests/test_cli.py::test_cli_process PASSED

5 passed in 1.2s
Coverage: 95% line coverage
```

---

## CLI Flag Combinations

### Development Workflow

```bash
# Rapid iteration - skip quality gates
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-quality

# Run quality gates only (skip tests)
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-tests

# Full pipeline with verbose logging
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --verbose
```

### Testing Different Scenarios

```bash
# Test with custom directories
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md \
  --source-dir my_src \
  --test-dir my_tests

# Enable retry for failed stories
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md \
  --retry-failed

# Maximum iterations for stubborn stories
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md \
  --max-iterations 5
```

### Quality Gate Isolation

```bash
# Test just Ruff
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-tests

# Test just type checking
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-tests

# Test just pytest
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-quality
```

---

## Troubleshooting Quality Gates

### Ruff Issues

**Problem**: Ruff fails with style errors

```bash
# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# Check specific file
ruff check src/data_processor.py
```

### BasedPyright Issues

**Problem**: Type checking errors

```bash
# Check with detailed output
basedpyright src/ --output-format=json

# Check specific file
basedpyright src/data_processor.py

# Ignore specific error
# Add to file: # type: ignore[return-value]
```

### Pytest Issues

**Problem**: Test failures

```bash
# Run with verbose output
pytest tests/ -v --tb=long

# Run specific test file
pytest tests/test_data_processor.py -v

# Debug failing test
pytest tests/test_data_processor.py::test_process_valid_data -s --pdb
```

### Cancel Scope Errors

**Problem**: Cancel scope errors in logs

**Solution**: **Ignore - these are expected and handled automatically**

The system suppresses these errors and continues normal operation. No action required.

---

## Next Steps

After running this example:

1. **Review Generated Code**
   - Check `src/data_processor.py`
   - Check `src/cli.py`
   - Review test files in `tests/`

2. **Examine Quality Reports**
   - Ruff: Check for any remaining issues
   - BasedPyright: Review type checking results
   - Pytest: Check test coverage report

3. **Experiment with Flags**
   - Try different CLI flag combinations
   - Test with `--skip-quality` for faster iteration
   - Use `--verbose` for detailed logs

4. **Modify and Re-run**
   - Add intentional errors to test quality gates
   - Remove type hints to test BasedPyright
   - Break tests to verify pytest agent

5. **Review Documentation**
   - `docs/troubleshooting/quality-gates.md`
   - `docs/evaluation/cancel-scope-error-analysis.md`
   - `README.md` quality gates section

---

## Learn More

- **Quality Gates Overview**: `README.md` section "Quality Gates"
- **CLI Reference**: `README.md` section "CLI Reference"
- **Troubleshooting**: `docs/troubleshooting/quality-gates.md`
- **Technical Details**: `docs/evaluation/cancel-scope-error-analysis.md`
- **User Guide**: `docs/user-guide/quality-gates.md`

---

## Example Commands Reference

```bash
# Full pipeline
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md

# Skip quality gates
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-quality

# Skip tests
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --skip-tests

# Verbose mode
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md --verbose

# Custom directories
python -m autoBMAD.epic_automation.epic_driver quality-agents-example.md \
  --source-dir src --test-dir tests

# Help
python -m autoBMAD.epic_automation.epic_driver --help
```

---

*This example demonstrates the complete quality gates integration. Modify and experiment to learn how quality agents work in practice.*

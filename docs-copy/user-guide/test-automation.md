# Test Automation User Guide

This guide explains how to use test automation in the autoBMAD system.

## Overview

Test automation is Phase 3 of the 5-phase workflow. It runs after quality gates complete and executes:

1. **Pytest** - Test execution
2. **Debugpy** - Debugging persistent failures

Test automation ensures that all tests pass and code behaves correctly.

---

## Quick Start

### Running with Test Automation

By default, test automation runs automatically after quality gates:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

Test automation will:
1. Find all test files in the test directory
2. Run pytest with coverage
3. Report test results
4. Retry failed tests (up to 5 times)
5. Activate debugpy for persistent failures

### Skipping Test Automation

For faster iteration during development:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests
```

**When to skip:**
- During initial development
- When iterating on non-testable features
- When tests are slow or unreliable

**When not to skip:**
- Before committing code
- In CI/CD pipelines
- Before releases
- After code changes

---

## Understanding Test Automation

### Phase 3: Test Automation Workflow

```
Quality Gates Complete
         ↓
Test Automation Starts
         ↓
Find Test Files
         ↓
Run Pytest
         ↓
Check Results
         ↓
Failed Tests? → Retry (max 5 attempts)
         ↓
Persistent Failures? → Activate Debugpy (300s timeout)
         ↓
All Tests Pass? → Continue to Orchestration
         ↓
Test Automation Complete
```

### Test Automation Components

#### Pytest Test Execution

**Purpose:**
- Run all tests in the test suite
- Generate coverage reports
- Provide detailed test results

**What it does:**
- Discovers test files (test_*.py, *_test.py)
- Executes test functions
- Collects pass/fail/skip statistics
- Generates coverage reports
- Provides detailed failure information

**Example output:**
```
Test Automation: Starting test execution
Test directory: tests/
Found 15 test files
Running pytest...

tests/test_module1.py::test_basic PASSED           [  5%]
tests/test_module1.py::test_advanced PASSED       [ 10%]
tests/test_module2.py::test_validation PASSED     [ 15%]
tests/test_module3.py::test_process FAILED        [ 20%]
...

========================= FAILURES =========================
tests/test_module3.py::test_process
AssertionError: assert 5 == 3

========================= summary =========================
45 passed, 2 failed, 3 skipped in 45.2s
Coverage: 85% (45/52 statements)
```

#### Debugpy Integration

**Purpose:**
- Debug persistent test failures
- Help diagnose complex issues
- Provide interactive debugging

**When it activates:**
- After 3 consecutive failures of the same test
- When test automation needs deeper investigation
- Manual activation via pytest --pdb

**Example output:**
```
Test Automation: Test failed 3 times, activating debugpy
Debugpy server listening on port 5678
Waiting for debugger to attach...

[DEBUGPY] Debugger attached
Test execution paused at tests/test_module3.py:45
> test_module3.py(45): assert result == expected
(Pdb) print(result)
5
(Pdb) print(expected)
3
(Pdb) continue
```

---

## Test Structure

### Test File Naming

Test files must follow naming conventions:

```
✓ test_*.py           # Recommended
✓ *_test.py           # Alternative
✗ tests.py            # Not found
✗ testfile.py         # Not found
```

Examples:
```
✓ tests/test_user.py
✓ tests/test_models.py
✓ tests/integration/test_api.py
✓ user_test.py
```

### Test Function Naming

Test functions must follow naming conventions:

```
✓ test_*              # Recommended
✓ Test* (in class)    # Alternative
✗ my_test()           # Not found
✗ testFunction()      # Not found
```

Examples:
```python
# Recommended
def test_user_creation():
    pass

def test_user_validation():
    pass

# With test class
class TestUser:
    def test_creation(self):
        pass

    def test_validation(self):
        pass
```

### Test Directory Structure

Recommended test directory structure:

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_models.py
│   └── test_utils.py
├── integration/          # Integration tests
│   └── test_api.py
└── e2e/                  # End-to-end tests
    └── test_workflow.py
```

---

## Writing Tests

### Basic Test Example

```python
# tests/test_calculator.py
import pytest
from src.calculator import Calculator

def test_calculator_addition():
    """Test addition functionality."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

def test_calculator_subtraction():
    """Test subtraction functionality."""
    calc = Calculator()
    result = calc.subtract(5, 3)
    assert result == 2

def test_calculator_multiplication():
    """Test multiplication functionality."""
    calc = Calculator()
    result = calc.multiply(4, 3)
    assert result == 12

def test_calculator_division():
    """Test division functionality."""
    calc = Calculator()
    result = calc.divide(10, 2)
    assert result == 5

    # Test division by zero
    with pytest.raises(ZeroDivisionError):
        calc.divide(10, 0)
```

### Using Fixtures

```python
# tests/conftest.py
import pytest
from src.database import Database

@pytest.fixture
def test_db():
    """Create a test database."""
    db = Database(":memory:")  # In-memory database
    db.create_tables()
    yield db
    db.cleanup()

@pytest.fixture
def sample_user(test_db):
    """Create a sample user."""
    user = test_db.create_user("test@example.com", "password")
    return user
```

```python
# tests/test_user.py
def test_create_user(test_db):
    """Test user creation."""
    user = test_db.create_user("new@example.com", "password")
    assert user.email == "new@example.com"
    assert user.is_active is True

def test_user_login(sample_user):
    """Test user login."""
    result = sample_user.login("password")
    assert result is True

    # Test wrong password
    result = sample_user.login("wrong")
    assert result is False
```

### Parametrized Tests

```python
# tests/test_calculator.py
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (10, 20, 30),
])
def test_add_parametrized(a, b, expected):
    """Test addition with various inputs."""
    calc = Calculator()
    result = calc.add(a, b)
    assert result == expected

@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 4, 3, 12),
    ("divide", 10, 2, 5),
])
def test_operations_parametrized(operation, a, b, expected):
    """Test all operations with parametrization."""
    calc = Calculator()
    method = getattr(calc, operation)
    result = method(a, b)
    assert result == expected
```

### Mocking and Patching

```python
# tests/test_api.py
import pytest
from unittest.mock import Mock, patch
from src.api import APIClient

def test_api_client_fetch(mocker):
    """Test API client fetch with mocking."""
    # Mock the requests module
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_response.status_code = 200

    mocker.patch('requests.get', return_value=mock_response)

    client = APIClient()
    result = client.fetch("/api/data")

    assert result["status"] == "success"

@patch('src.api.requests.get')
def test_api_client_fetch_with_context_manager(mock_get):
    """Test API client fetch using context manager."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    client = APIClient()
    result = client.fetch("/api/data")

    assert result["data"] == "test"
    mock_get.assert_called_once_with("/api/data")
```

---

## Configuration

### pytest.ini Settings

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Output
addopts = "-v --tb=short --strict-markers --strict-config"
testmon_ignore_dep = true

# Markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end tests",
]

# Coverage
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

### Running Tests

#### Run All Tests

```bash
# From project root
pytest

# With coverage
pytest --cov=src --cov-report=html

# With verbose output
pytest -v
```

#### Run Specific Tests

```bash
# Run specific file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::test_addition

# Run tests matching pattern
pytest -k "test_add"

# Run tests with marker
pytest -m "unit"
pytest -m "not slow"
```

#### Run with Debugpy

```bash
# Run all tests with debugpy
pytest --pdb

# Run failing tests with debugpy
pytest --pdbcls=IPython.terminal.debugger:Pdb

# Drop into debugger on failure
pytest --lf --pdb
```

---

## Common Workflows

### Development Workflow

**Step 1: Write tests**
```python
def test_new_feature():
    calc = Calculator()
    result = calc.new_function(2, 3)
    assert result == 5
```

**Step 2: Run test automation**
```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

**Step 3: Review results**
```
Test Automation: 45 passed, 2 failed, 3 skipped
```

**Step 4: Fix failures**
```python
def test_new_feature():
    calc = Calculator()
    result = calc.new_function(2, 3)
    assert result == 6  # Fixed expected value
```

**Step 5: Re-run tests**
```bash
pytest tests/test_calculator.py::test_new_feature -v
```

### Test-Driven Development (TDD)

**Step 1: Write failing test**
```python
def test_calculator_power():
    calc = Calculator()
    result = calc.power(2, 3)
    assert result == 8
```

**Step 2: Run test (should fail)**
```bash
pytest tests/test_calculator.py::test_calculator_power -v
```

**Step 3: Implement feature**
```python
class Calculator:
    def power(self, a, b):
        return a ** b
```

**Step 4: Run test (should pass)**
```bash
pytest tests/test_calculator.py::test_calculator_power -v
```

### Debugging Workflow

**Step 1: Identify failing test**
```bash
pytest -v
```

**Step 2: Run with debugpy**
```bash
pytest tests/test_module.py::test_function --pdb
```

**Step 3: Debug interactively**
```bash
(Pdb) print(variable_name)
(Pdb) list
(Pdb) where
(Pdb) continue
```

**Step 4: Fix issue**
```python
# Fix the code
```

**Step 5: Verify fix**
```bash
pytest tests/test_module.py::test_function -v
```

---

## Best Practices

### 1. Follow Test Naming Conventions

```python
# Good
def test_user_can_register():
    pass

def test_user_cannot_register_with_duplicate_email():
    pass

# Avoid
def test_registration():
    pass
```

### 2. Use Descriptive Test Names

```python
# Good - describes what is being tested
def test_user_cannot_login_with_wrong_password():
    pass

# Avoid - too generic
def test_login():
    pass
```

### 3. Write Isolated Tests

```python
# Good - each test is independent
def test_user_creation():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_user_deletion():
    user = create_user("test2@example.com")
    delete_user("test2@example.com")
    assert not user_exists("test2@example.com")

# Avoid - tests depend on each other
def test_user_creation():
    user = create_user("test@example.com")
    assert user_exists("test@example.com")

def test_user_deletion():
    # Depends on test_user_creation running first
    delete_user("test@example.com")
    assert not user_exists("test@example.com")
```

### 4. Use Fixtures for Setup

```python
# Good - fixtures handle setup
@pytest.fixture
def user():
    return create_user("test@example.com")

def test_user_has_email(user):
    assert user.email == "test@example.com"

def test_user_can_login(user):
    assert user.login("password") is True

# Avoid - repeating setup
def test_user_has_email():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_user_can_login():
    user = create_user("test@example.com")
    assert user.login("password") is True
```

### 5. Test Edge Cases

```python
def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ZeroDivisionError):
        calc.divide(10, 0)

def test_empty_list():
    result = process_list([])
    assert result == []

def test_none_input():
    result = process_value(None)
    assert result is None
```

### 6. Use Markers for Test Categorization

```python
import pytest

@pytest.mark.unit
def test_simple_calculation():
    calc = Calculator()
    assert calc.add(2, 3) == 5

@pytest.mark.integration
def test_api_integration():
    client = APIClient()
    result = client.fetch("/api/data")
    assert result.status == 200

@pytest.mark.slow
def test_complex_calculation():
    calc = Calculator()
    result = calc.calculate_prime(1000000)
    assert result is not None
```

Run with markers:
```bash
# Run only unit tests
pytest -m unit

# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

### 7. Keep Tests Fast

```python
# Good - fast test
def test_simple_calculation():
    assert 2 + 2 == 4

# Avoid - slow test
def test_slow_calculation():
    # Don't do this in unit tests
    import time
    time.sleep(10)
    assert complex_calculation() == expected
```

### 8. Assert Specific Errors

```python
# Good - specific assertion
with pytest.raises(ValueError, match="Invalid email"):
    create_user("invalid-email")

# Avoid - generic assertion
with pytest.raises(Exception):
    create_user("invalid-email")
```

---

## Troubleshooting

### Tests Not Found

**Problem:** "collected 0 items"

**Solutions:**
1. Check test file naming:
   ```bash
   # Must be test_*.py or *_test.py
   mv testfile.py test_file.py
   ```

2. Check test function naming:
   ```python
   # Must start with test_
   def my_test():  # Wrong
   def test_my():  # Correct
   ```

3. Check pytest configuration in pyproject.toml

4. Run from correct directory:
   ```bash
   cd /path/to/project
   pytest
   ```

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'src'"

**Solutions:**
1. Use relative imports:
   ```python
   # In tests/test_module.py
   from src.module import function
   ```

2. Set PYTHONPATH:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

3. Run from project root:
   ```bash
   cd /path/to/project
   pytest tests/
   ```

### Flaky Tests

**Problem:** Tests sometimes pass, sometimes fail

**Solutions:**
1. Remove time dependencies:
   ```python
   # Avoid
   import time
   time.sleep(1)
   assert function() == expected

   # Use mocking
   with patch('time.sleep'):
       assert function() == expected
   ```

2. Use proper teardown:
   ```python
   @pytest.fixture
   def resource():
       res = acquire_resource()
       yield res
       release_resource(res)
   ```

3. Use fixed random seeds:
   ```python
   @pytest.fixture(autouse=True)
   def set_random_seed():
       random.seed(42)
   ```

### Slow Tests

**Problem:** Tests take too long

**Solutions:**
1. Mark slow tests:
   ```python
   @pytest.mark.slow
   def test_slow_operation():
       # This test is slow
       pass
   ```

2. Skip slow tests in development:
   ```bash
   pytest -m "not slow"
   ```

3. Use faster alternatives:
   ```python
   # Use in-memory database
   db = Database(":memory:")

   # Use mocks instead of real API
   with patch('requests.get'):
       result = api_call()
   ```

### Coverage Too Low

**Problem:** Code coverage < 80%

**Solutions:**
1. Generate coverage report:
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

2. Identify uncovered code:
   - Review the HTML report
   - Look for uncovered branches

3. Add missing tests:
   ```python
   def test_edge_case():
       # Test the uncovered branch
       result = function(edge_case_input)
       assert result.expected_value
   ```

### Debugpy Not Working

**Problem:** Debugpy doesn't activate

**Solutions:**
1. Check if test fails multiple times:
   - Debugpy activates after 3 failures
   - Check retry count in logs

2. Manually activate:
   ```bash
   pytest tests/test_failing.py --pdb
   ```

3. Check debugpy installation:
   ```bash
   python -c "import debugpy; print(debugpy.__version__)"
   ```

---

## Integration Examples

### With CI/CD

**GitHub Actions:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### With Pre-commit

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### With Make

```makefile
.PHONY: test test-unit test-integration coverage

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

test-fast:
	pytest -m "not slow"
```

---

## Advanced Topics

### Custom Fixtures

```python
# tests/conftest.py
import pytest
import tempfile
import os

@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture(scope="session")
def database():
    """Create a test database (session scope)."""
    db = setup_test_database()
    yield db
    cleanup_test_database(db)

@pytest.fixture
def client(database):
    """Create a test client."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
```

### Test Parametrization from Files

```python
# tests/test_data.py
import pytest

@pytest.mark.parametrize(
    "input,expected",
    [
        ("test1", "result1"),
        ("test2", "result2"),
        ("test3", "result3"),
    ]
)
def test_process_input(input, expected):
    result = process(input)
    assert result == expected

# Or load from JSON
import json

@pytest.mark.parametrize(
    "case",
    json.loads(Path("tests/data/cases.json").read_text())
)
def test_from_file(case):
    result = process(case["input"])
    assert result == case["expected"]
```

### Custom Markers

```python
# tests/conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration"
    )

# Usage
@pytest.mark.slow
def test_complex_calculation():
    pass
```

### Test Isolation and Parallelization

```python
# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Isolate tests with unique databases
@pytest.fixture
def unique_db():
    db_name = f"test_db_{uuid.uuid4()}"
    db = Database(db_name)
    yield db
    db.delete()
```

---

## Examples

### Example 1: Unit Test

```python
# tests/test_calculator.py
import pytest
from src.calculator import Calculator

def test_calculator_addition():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_calculator_subtraction():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2

def test_calculator_multiplication():
    calc = Calculator()
    assert calc.multiply(4, 3) == 12

def test_calculator_division():
    calc = Calculator()
    assert calc.divide(10, 2) == 5

    with pytest.raises(ZeroDivisionError):
        calc.divide(10, 0)
```

### Example 2: Integration Test

```python
# tests/integration/test_api.py
import pytest
from unittest.mock import patch
from src.api import APIClient

@pytest.mark.integration
def test_api_client_fetch_success():
    with patch('src.api.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = APIClient()
        result = client.fetch("/api/data")

        assert result["status"] == "success"
        mock_get.assert_called_once_with("/api/data")
```

### Example 3: End-to-End Test

```python
# tests/e2e/test_workflow.py
import pytest
from src.workflow import Workflow

@pytest.mark.e2e
def test_complete_workflow():
    workflow = Workflow()
    result = workflow.run()

    assert result.status == "completed"
    assert len(result.steps) > 0
    assert all(step.status == "completed" for step in result.steps)
```

---

## Quick Reference

### Common Commands

```bash
# Run test automation with epic
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md

# Skip test automation
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific file
pytest tests/test_module.py

# Run failing tests
pytest --lf

# Run with debugpy
pytest --pdb

# Run with markers
pytest -m unit
pytest -m "not slow"

# Parallel execution
pytest -n auto
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All tests passed | No action needed |
| 1 | Tests failed | Fix failing tests |
| 2 | Execution error | Check configuration |
| 3 | Internal error | Report bug |

### Test Markers

| Marker | Purpose | Usage |
|--------|---------|-------|
| unit | Unit tests | `pytest -m unit` |
| integration | Integration tests | `pytest -m integration` |
| e2e | End-to-end tests | `pytest -m e2e` |
| slow | Slow tests | `pytest -m "not slow"` |

---

## Support

If you need help:

1. Check [troubleshooting guide](../troubleshooting/quality-gates.md)
2. Review [example epics](../examples/example-epic-with-quality-gates.md)
3. Check the [API documentation](../api/README.md)
4. Run with `--verbose` for detailed logs
5. Check pytest documentation: https://docs.pytest.org/
6. Check debugpy documentation: https://github.com/microsoft/debugpy/

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-05 | 1.0 | Initial test automation user guide | BMAD Team |

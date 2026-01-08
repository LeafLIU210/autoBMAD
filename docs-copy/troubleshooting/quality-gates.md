# Quality Gates Troubleshooting Guide

This guide helps you resolve common issues with the quality gates phase in autoBMAD.

## Overview

Quality gates include:
1. **Basedpyright** - Type checking
2. **Ruff** - Linting and formatting
3. **Pytest** - Test execution
4. **Debugpy** - Debugging persistent failures

## Cancel Scope Error Prevention

Quality gates are designed with **Cancel Scope Safety** to prevent timeout-related errors:

### Critical Safety Requirements

**NO External Timeouts**: Quality gates use SDK max_turns=150 protection only
- ❌ Do NOT use `asyncio.wait_for()` or `asyncio.shield()`
- ✅ Use SDK's built-in `max_turns` parameter for timeout protection
- ✅ Use simplified retry mechanisms without external timeout wrappers

### Why Cancel Scope Errors Occur

Cancel scope errors typically happen when:
1. **External timeout wrappers** conflict with SDK's internal timeout handling
2. **Nested async operations** with different timeout configurations
3. **Shield usage** that interferes with proper cancellation propagation

### Prevention Strategy

**Use SDK max_turns only**:
```python
# ✅ CORRECT: Use SDK max_turns
options = _ClaudeAgentOptions(max_turns=150)
response = _query(prompt=prompt, options=options)

# ❌ WRONG: External timeout wrapper
await asyncio.wait_for(
    _query(prompt=prompt, options=options),
    timeout=300
)
```

**Implement simplified retry logic**:
```python
# ✅ CORRECT: Simple retry without external timeouts
async def retry_cycle(self, source_dir: Path, max_cycles: int = 3):
    for cycle_num in range(1, max_cycles + 1):
        result = await self.execute_check(source_dir)
        if result.success:
            return result
    return final_result

# ❌ WRONG: Retry with external timeouts
async def retry_cycle(self, source_dir: Path, max_cycles: int = 3):
    for cycle_num in range(1, max_cycles + 1):
        result = await asyncio.wait_for(
            self.execute_check(source_dir),
            timeout=60
        )
        if result.success:
            return result
    return final_result
```

### Technical Details

For complete technical analysis, see:
- [Cancel Scope Error Analysis](../evaluation/cancel-scope-error-analysis.md)

**Key Implementation Points**:
1. Remove all `asyncio.wait_for()` and `asyncio.shield()` calls
2. Use SDK's `max_turns` parameter for session protection
3. Implement retry logic with simple loops, not timeout-based retry
4. Track progress and timing without external timeout mechanisms

### Testing Cancel Scope Safety

To verify Cancel Scope safety in your implementation:

```python
# Test that no external timeouts are used
import inspect

def verify_no_external_timeouts():
    source = inspect.getsource(quality_agent.retry_cycle)
    assert "asyncio.wait_for" not in source
    assert "asyncio.shield" not in source

# Test that max_turns is used
def verify_max_turns_protection():
    options = _ClaudeAgentOptions(max_turns=150)
    assert options.max_turns == 150
```

---

## Basedpyright Type Checking Issues

### Issue: Missing Type Annotations

**Error Message**:
```
error: Function "process_data" is missing a type annotation
```

**Problem**: Function parameters or return type lacks type hints

**Solution**:
```python
# Before
def process_data(data):
    return data.strip()

# After
def process_data(data: str) -> str:
    return data.strip()
```

**Additional Examples**:
```python
# List type annotation
def process_list(items: list[str]) -> list[str]:
    return [item.strip() for item in items]

# Dict type annotation
def get_config(config: dict[str, str]) -> str:
    return config.get('key', 'default')

# Optional type annotation
def get_user(user_id: int) -> str | None:
    return db.get_user(user_id)
```

### Issue: Incorrect Type Annotation

**Error Message**:
```
error: Argument of type "str" cannot be assigned to parameter of type "int"
```

**Problem**: Function called with wrong type

**Solution**:
```python
# Before
def calculate_total(price: int, quantity: int) -> int:
    return price * quantity

total = calculate_total("10", 5)  # Wrong types

# After
total = calculate_total(10, 5)  # Correct types
```

### Issue: Import Type Not Found

**Error Message**:
```
error: Cannot find implementation of library "typing"
```

**Problem**: Missing import or wrong import

**Solution**:
```python
# Add proper imports
from typing import List, Dict, Optional, Union, Any

# Use in function signatures
def process_data(data: List[str]) -> Optional[str]:
    pass
```

### Issue: Module Not Indexed

**Error Message**:
```
error: Module "src" is not indexed
```

**Problem**: Basedpyright can't find source files

**Solution**:
1. Check `pyproject.toml` configuration:
```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
```

2. Verify file structure:
```
project/
├── pyproject.toml
├── src/
│   └── *.py
```

3. Run basedpyright from project root:
```bash
basedpyright src/
```

### Issue: Union Type Syntax Error (Python <3.10)

**Error Message**:
```
error: Syntax error in type annotation
```

**Problem**: Using `|` syntax for unions (Python 3.10+)

**Solution**:
```python
# Python 3.10+
def process(value: str | int) -> str:
    return str(value)

# Python 3.8-3.9
from typing import Union

def process(value: Union[str, int]) -> str:
    return str(value)
```

### Issue: Type Checking Performance

**Symptom**: Basedpyright runs very slowly

**Solution**:
1. **Enable incremental checking**:
   ```toml
   [tool.basedpyright]
   incremental = true
   ```

2. **Exclude test files**:
   ```toml
   [tool.basedpyright]
   exclude = ["tests/*"]
   ```

3. **Use weaker type checking mode**:
   ```toml
   [tool.basedpyright]
   typeCheckingMode = "off"  # or "basic"
   ```

---

## Ruff Linting Issues

### Issue: Line Too Long

**Error Message**:
```
E501 line too long (100 > 88 characters)
```

**Problem**: Code line exceeds configured line length

**Solution**:
```python
# Before
result = some_function_name_that_is_very_long(parameter_one, parameter_two, parameter_three, parameter_four)

# After - split into multiple lines
result = some_function_name_that_is_very_long(
    parameter_one,
    parameter_two,
    parameter_three,
    parameter_four,
)
```

**Auto-fix**:
```bash
ruff check --fix src/
```

### Issue: Unused Import

**Error Message**:
```
F401 'os' imported but unused
```

**Problem**: Import statement without usage

**Solution**:
```python
# Before
import os
import sys

def main():
    print("Hello")

# After
import sys

def main():
    print("Hello")
```

**Auto-fix**:
```bash
ruff check --fix src/
```

### Issue: Undefined Variable

**Error Message**:
```
F821 undefined name 'variable_name'
```

**Problem**: Variable used before definition or typo

**Solution**:
```python
# Before
def process():
    print(result)  # result not defined
    result = "value"

# After
def process():
    result = "value"
    print(result)
```

### Issue: Import Not Sorted

**Error Message**:
```
I001 import in wrong order
```

**Problem**: Imports not in expected order

**Solution**:
```python
# Before
import sys
import os
from typing import Dict

# After - standard library, third-party, local
import os
import sys
from typing import Dict

from mymodule import myfunction
```

**Auto-fix**:
```bash
ruff check --fix src/
```

### Issue: Code Format Issues

**Error Message**:
```
E701 multiple statements on one line (colon)
```

**Problem**: Poor formatting

**Solution**:
```python
# Before
if condition: print("yes")

# After
if condition:
    print("yes")
```

**Auto-fix**:
```bash
ruff format src/
```

### Issue: Type Annotation Missing

**Error Message**:
```
ANN101 missing type annotation for self
```

**Problem**: Method parameter lacks type hint

**Solution**:
```python
# Before
class MyClass:
    def method(self, value):
        self.value = value

# After
class MyClass:
    def method(self, value: str) -> None:
        self.value = value
```

### Issue: Mutable Default Argument

**Error Message**:
```
B006 do not use mutable data structures as default argument
```

**Problem**: Using mutable object as default argument

**Solution**:
```python
# Before
def process(items=[]):
    items.append(1)
    return items

# After
def process(items: list | None = None):
    if items is None:
        items = []
    items.append(1)
    return items
```

### Issue: Slow Ruff Performance

**Symptom**: Ruff takes too long to run

**Solution**:
1. **Only check changed files**:
   ```bash
   ruff check src/modified_file.py
   ```

2. **Use faster rules**:
   ```bash
   ruff check --select E,F,W src/
   ```

3. **Ignore specific files**:
   ```toml
   [tool.ruff]
   exclude = [
       ".bzr",
       ".direnv",
       ".eggs",
       ".git",
       ".mypy_cache",
   ]
   ```

---

## Pytest Test Failures

### Issue: Test Not Found

**Error Message**:
```
collected 0 items
```

**Problem**: Test files not discovered

**Solution**:
1. **Check test file naming**:
   ```
   tests/
   ├── test_*.py      ✓ Found
   └── *_test.py      ✓ Found
   └── testfile.py    ✗ Not found
   ```

2. **Check test function naming**:
   ```python
   def test_function():  ✓ Found
   def my_test():       ✗ Not found
   ```

3. **Configure pytest discovery** in `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py", "*_test.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   ```

### Issue: AssertionError

**Error Message**:
```
AssertionError: assert 2 == 1
```

**Problem**: Test assertion fails

**Solution**:
```python
# Before
def test_addition():
    result = add(2, 3)
    assert result == 1  # Wrong expected value

# After
def test_addition():
    result = add(2, 3)
    assert result == 5  # Correct expected value
```

### Issue: Import Error in Tests

**Error Message**:
```
ModuleNotFoundError: No module named 'mymodule'
```

**Problem**: Test can't import the module

**Solution**:
1. **Check PYTHONPATH**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   pytest
   ```

2. **Use relative imports**:
   ```python
   # In tests/test_module.py
   from src.module import myfunction
   ```

3. **Run from project root**:
   ```bash
   cd /path/to/project
   pytest tests/
   ```

### Issue: Fixture Not Found

**Error Message**:
```
fixture 'my_fixture' not found
```

**Problem**: Fixture not defined or accessible

**Solution**:
```python
# Define fixture in conftest.py or test file
import pytest

@pytest.fixture
def my_fixture():
    return {"key": "value"}

# Use in test
def test_with_fixture(my_fixture):
    assert my_fixture["key"] == "value"
```

### Issue: Parametrized Test Failures

**Error Message**:
```
FAILED tests/test_module.py::test_process[input2-expected2]
```

**Problem**: One parametrized test fails

**Solution**:
```python
# Before
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),  # This might fail
    (3, 4),
])
def test_process(input, expected):
    assert process(input) == expected

# After - add ids for clarity
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (3, 4),
], ids=["case1", "case2", "case3"])
def test_process(input, expected):
    assert process(input) == expected

# Run specific case
pytest tests/test_module.py::test_process[case2] -v
```

### Issue: Slow Test Execution

**Symptom**: Tests take too long

**Solution**:
1. **Mark slow tests**:
   ```python
   @pytest.mark.slow
   def test_slow_operation():
       # This test is slow
       pass

   # Run without slow tests
   pytest -m "not slow"
   ```

2. **Use parallel execution**:
   ```bash
   pytest -n auto
   ```

3. **Use pytest-xdist**:
   ```bash
   pip install pytest-xdist
   pytest -n 4  # Use 4 workers
   ```

### Issue: Coverage Too Low

**Error Message**:
```
Coverage report: Coverage < 80%
```

**Problem**: Not enough code covered by tests

**Solution**:
1. **Generate coverage report**:
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

2. **Identify uncovered code**:
   - Review the HTML report
   - Add tests for missing branches

3. **Add missing tests**:
   ```python
   def test_edge_case():
       # Test the uncovered branch
       result = function_with_branches(input_value)
       assert result.expected_value
   ```

---

## Debugpy Debugging Issues

### Issue: Debugpy Not Activating

**Symptom**: Persistent test failures but no debugpy session

**Problem**: Debugpy only activates after 3+ failures

**Solution**:
1. **Check failure count**:
   - Debugpy activates after 3 consecutive failures
   - Check test logs for retry attempts

2. **Manually activate debugpy**:
   ```bash
   pytest tests/test_failing.py --pdb
   ```

3. **Configure debugpy timeout**:
   ```python
   # In test_automation_agent.py
   debugpy_timeout = 300  # 5 minutes
   ```

### Issue: Debugpy Session Timeout

**Error Message**:
```
Debugpy session timeout after 300 seconds
```

**Problem**: Debugpy session ran too long

**Solution**:
1. **Increase timeout**:
   ```python
   # In epic_driver.py
   debugpy_timeout = 600  # 10 minutes
   ```

2. **Attach debugger manually**:
   ```python
   import debugpy
   debugpy.listen(5678)
   debugpy.wait_for_client()
   ```

3. **Set breakpoints selectively**:
   ```python
   def test_function():
       # Only break on specific condition
       if complex_condition:
           import pdb; pdb.set_trace()
       result = function()
       assert result
   ```

### Issue: Can't Connect to Debugpy

**Error Message**:
```
Could not connect to debugpy server
```

**Problem**: Debugpy server not accessible

**Solution**:
1. **Check debugpy is listening**:
   ```python
   import debugpy
   print(debugpy.listening())  # Should be True
   ```

2. **Verify port is open**:
   ```bash
   netstat -an | grep 5678
   ```

3. **Use VS Code debugger**:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Attach",
               "type": "python",
               "request": "attach",
               "connect": {
                   "host": "localhost",
                   "port": 5678
               }
           }
       ]
   }
   ```

### Issue: Debugpy Hangs

**Symptom**: Debugpy session hangs indefinitely

**Problem**: Breakpoint reached but no input

**Solution**:
1. **Use conditional breakpoints**:
   ```python
   # Instead of pdb.set_trace()
   import debugpy
   debugpy.breakpoint()
   ```

2. **Set timeout**:
   ```python
   import signal

   def timeout_handler(signum, frame):
       raise TimeoutError("Debug session timeout")

   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(300)  # 5 minute timeout
   ```

3. **Kill debugpy process**:
   ```bash
   pkill -f debugpy
   ```

---

## Common Quality Gate Patterns

### Pattern: Quality Gates Pass on Retry

**Scenario**: Quality gates fail initially but pass on retry

**Explanation**:
- Ruff auto-fixes some issues on first run
- Second run finds no issues
- This is normal behavior

**Solution**: Accept this as expected behavior

### Pattern: Type Errors in Third-Party Code

**Scenario**: Basedpyright reports errors in imported modules

**Solution**:
```toml
[tool.basedpyright]
exclude = [
    "venv/*",
    ".venv/*",
    "site-packages/*",
]
```

### Pattern: Ruff vs Black Conflict

**Scenario**: Ruff format differs from Black

**Solution**: Use only Ruff for formatting
```bash
# Use Ruff for both linting and formatting
ruff check --fix src/
ruff format src/
```

### Pattern: Slow Type Checking

**Scenario**: Basedpyright takes too long

**Solution**:
```toml
[tool.basedpyright]
typeCheckingMode = "basic"  # Instead of "strict"
reportOptionalMemberAccess = false
reportOptionalSubscript = false
```

---

## Prevention Strategies

### 1. Write Code with Type Hints from Start

```python
def function(param: type) -> return_type:
    """Docstring."""
    pass
```

### 2. Format Code Before Committing

```bash
ruff check --fix src/
ruff format src/
```

### 3. Run Tests Before Pushing

```bash
pytest tests/ -v
```

### 4. Use Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - ruff
      - ruff-format
  - repo: https://github.com/pre-commit/mirrors-basedpyright
    rev: v1.1.0
    hooks:
      - basedpyright
```

### 5. Configure Quality Gates Properly

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"

[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "F", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

---

## Cancel Scope Error Prevention

### What are Cancel Scope Errors?

Cancel Scope errors are related to anyio's asynchronous context management used internally by the Claude Agent SDK. These errors occur when attempting to exit a cancel scope in a different task than it was entered:

```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

### Why They Happen

The autoBMAD system uses the Claude Agent SDK which internally uses anyio for async operations. Cancel scopes are tied to specific asyncio tasks, and errors can occur when:
- External `asyncio.wait_for()` timeouts interrupt async generators
- Multiple SDK calls happen in the same async context
- Shield protection and wait_for are nested improperly

### autoBMAD's Safety Measures

The system implements several safety measures to prevent these errors:

#### 1. Removed External Timeouts
- External `asyncio.wait_for()` timeouts have been removed
- System relies solely on SDK's built-in `max_turns` limit (150 turns)
- No external timeout flags in CLI (all removed)

#### 2. Sequential Execution
- Quality gates execute sequentially (Ruff → BasedPyright → Pytest)
- No concurrent execution within quality gates
- Each phase completes fully before the next begins

#### 3. Error Suppression
- Cancel Scope errors are caught and suppressed
- Errors are logged but don't propagate
- System continues execution after errors

### For Users: What This Means

**You can safely ignore Cancel Scope errors if you see them in logs:**

1. **They are handled automatically** - System suppresses and continues
2. **No action required** - Don't try to fix these errors yourself
3. **Normal operation continues** - Quality gates still function
4. **Check logs for actual issues** - Cancel Scope errors mask real problems

**If you see Cancel Scope errors:**
```bash
# Check logs for the error (expected and suppressed)
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose

# Look for ACTUAL quality gate failures (not Cancel Scope errors)
# Check BasedPyright, Ruff, and Pytest results separately
basedpyright src/
ruff check src/
pytest tests/
```

### For Developers

If you're working on the codebase:

1. **Don't add external timeouts** - Use SDK's max_turns only
2. **Avoid asyncio.wait_for with SDK calls** - Causes scope conflicts
3. **Don't use asyncio.shield with wait_for** - Creates nested cancellation issues
4. **Let SDK handle timing** - It manages its own async context

### Technical Details

See `docs/evaluation/cancel-scope-error-analysis.md` for:
- Detailed root cause analysis
- Code examples showing the problem
- Previous mitigation attempts
- Recommended solutions

---

## Getting Help

### Check Logs

Run with verbose logging:
```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

### Run Tools Individually

```bash
# Test basedpyright
basedpyright src/

# Test ruff
ruff check src/
ruff format src/

# Test pytest
pytest tests/ -v
```

### Review Documentation

- [Basedpyright README](https://github.com/ethanhs/basedpyright)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Debugpy Documentation](https://github.com/microsoft/debugpy)

---

## Quick Reference

### Common Commands

```bash
# Fix ruff issues
ruff check --fix src/

# Format with ruff
ruff format src/

# Type check with basedpyright
basedpyright src/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Debug failing tests
pytest tests/ --pdb

# Skip quality gates
python epic_driver.py my-epic.md --skip-quality

# Skip tests
python epic_driver.py my-epic.md --skip-tests
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | No issues |
| 1 | General error | Check logs |
| 2 | Configuration error | Fix config |
| 3 | Quality gate failed | Fix code issues |
| 4 | Test failure | Fix tests |

---

## Support

If issues persist:

1. **Check logs** with `--verbose`
2. **Run tools individually** to isolate issues
3. **Review configuration** in `pyproject.toml`
4. **Check examples** in `docs/examples/`
5. **Create minimal reproduction** case
6. **Open issue** with logs and configuration

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-05 | 1.0 | Initial troubleshooting guide | BMAD Team |

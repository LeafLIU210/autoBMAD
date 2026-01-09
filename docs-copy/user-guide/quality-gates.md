# Quality Gates User Guide

This guide explains how to use quality gates in the autoBMAD system.

## Overview

Quality gates are automated checks that run after the SM-Dev-QA cycle completes. They ensure code quality by running:

1. **Basedpyright** - Type checking
2. **Ruff** - Linting and formatting

Quality gates help maintain code quality and catch issues early in the development process.

---

## Quick Start

### Running with Quality Gates

By default, quality gates run automatically:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

Quality gates will:
1. Find all Python files in the source directory
2. Run basedpyright type checking
3. Run ruff linting
4. Auto-fix issues where possible
5. Report results

### Skipping Quality Gates

For faster development, skip quality gates:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality
```

**When to skip:**
- During initial development
- When iterating quickly on features
- When working on non-production code

**When not to skip:**
- Before committing code
- In production builds
- During code reviews

---

## Understanding Quality Gates

### Phase 2: Quality Gates Workflow

```
SM-Dev-QA Cycle Complete
         ↓
Quality Gates Start
         ↓
Find Python Files
         ↓
Run Basedpyright
         ↓
Run Ruff Linting
         ↓
Auto-fix Issues
         ↓
Report Results
         ↓
Retry if Needed (max 3 attempts)
         ↓
Quality Gates Complete
         ↓
Test Automation Starts
```

### Quality Gate Components

#### Basedpyright Type Checking

**Purpose:**
- Validates type annotations
- Catches type-related errors
- Ensures consistency

**What it checks:**
- Function parameter types
- Function return types
- Variable type annotations
- Import types
- Generic types

**Example output:**
```
Basedpyright: Checking 15 files...
✓ src/module1.py - No errors
✓ src/module2.py - No errors
⚠ src/module3.py - 2 errors
   - Missing type annotation for 'value'
   - Incompatible type for 'result'

Basedpyright completed in 12.5s
```

#### Ruff Linting

**Purpose:**
- Enforces code style
- Catches potential bugs
- Auto-fixes issues

**What it checks:**
- PEP 8 compliance
- Code complexity
- Unused imports
- Import sorting
- Code formatting

**Example output:**
```
Ruff: Checking 15 files...
✓ src/module1.py - No issues
✓ src/module2.py - No issues
⚠ src/module3.py - 5 issues fixed
   - F401: Unused import 'os' (auto-fixed)
   - E501: Line too long (88 > 80) (auto-fixed)
   - E203: Whitespace before ':' (auto-fixed)

Ruff completed in 2.3s
Fixed 5 issues automatically
```

---

## Configuration

### pyproject.toml Settings

Create or update `pyproject.toml` in your project root:

```toml
[tool.basedpyright]
# Python version
pythonVersion = "3.8"

# Type checking mode
# Options: "off", "basic", "strict"
typeCheckingMode = "basic"

# Report settings
reportMissingImports = true
reportMissingTypeStubs = true
reportOptionalSubscript = false
reportOptionalMemberAccess = false

# Exclude patterns
exclude = [
    "tests/*",
    "venv/*",
    ".venv/*",
    "__pycache__/*"
]

[tool.ruff]
# Target Python version
target-version = "py38"

# Line length
line-length = 88

# Select rules
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "W",    # pycodestyle warnings
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "ANN",  # flake8-annotations
    "S",    # flake8-bandit
    "BLE",  # flake8-blind-except
    "FBT",  # flake8-boolean-trap
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "COM",  # flake8-commas
    "C4",   # flake8-comprehensions
    "DTZ",  # flake8-datetimez
    "T10",  # flake8-debugger
    "EM",   # flake8-errmsg
    "EXE",  # flake8-executable
    "FA",   # flake8-future-annotations
    "ISC",  # flake8-implicit-str-concat
    "ICN",  # flake8-import-conventions
    "G",    # flake8-logging-format
    "INP",  # flake8-naming
    "PIE",  # flake8-pie
    "T20",  # flake8-print
    "PT",   # flake8-pytest-style
    "Q",    # flake8-quotes
    "RSE",  # flake8-raise
    "RET",  # flake8-return
    "SLF",  # flake8-self
    "SIM",  # flake8-simplify
    "TID",  # flake8-tidy-imports
    "TCH",  # flake8-type-checking
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
    "ERA",  # eradicate
    "PGH",  # pygrep-hooks
    "PL",   # pylint
    "TRY",  # tryceratops
    "FLY",  # flynt
    "NPY",  # numpy
    "PERF",  # perflint
    "FURB", # refurb
    "LOG",  # flake8-logging-format
    "RUF",  # ruff-specific rules
]

# Ignore specific rules
ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
]

# Per-file ignores
[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101", "ANN"]
```

### Configuration Examples

#### Basic Configuration (Recommended)

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
reportMissingImports = true

[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "F", "W", "I"]
```

#### Strict Configuration

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "strict"
reportMissingImports = true
reportOptionalSubscript = true
reportOptionalMemberAccess = true

[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "F", "W", "I", "N", "ANN", "S", "BLE", "B", "A"]
```

#### Relaxed Configuration

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "off"

[tool.ruff]
target-version = "py38"
line-length = 100
select = ["E", "F"]
```

---

## Using Quality Gates

### Running Quality Gates Manually

You can run quality gates independently:

```bash
# Run basedpyright only
basedpyright src/

# Run ruff only
ruff check src/
ruff format src/  # Also format code

# Run both
basedpyright src/
ruff check --fix src/
```

### Interpreting Results

#### Basedpyright Results

**Exit codes:**
- 0: No errors
- 1: Errors found

**Common error types:**

| Code | Description | Example | Fix |
|------|-------------|---------|-----|
| Missing type annotation | Function missing type hints | `def func(x):` | `def func(x: int) -> str:` |
| Incompatible type | Wrong type used | `def func(x: int): func("str")` | `func(123)` |
| Missing import | Module not imported | `Path("file")` | `from pathlib import Path` |
| Undefined variable | Variable not defined | `print(var)` | Define or fix typo |

**Severity levels:**
- Error: Must be fixed
- Warning: Should be fixed
- Information: Optional fix

#### Ruff Results

**Exit codes:**
- 0: No issues or only auto-fixable issues
- 1: Issues found that require manual fixes

**Common issue types:**

| Code | Description | Example | Fix |
|------|-------------|---------|-----|
| E501 | Line too long | Code > 88 chars | Split line |
| F401 | Unused import | `import os` not used | Remove import |
| E203 | Whitespace before ':' | `x[ :2]` | `x[:2]` |
| W291 | Trailing whitespace | Code with spaces at end | Remove spaces |
| I001 | Import not sorted | `import sys, os` | Use isort order |

**Auto-fixable:**
- Most Ruff issues can be auto-fixed with `--fix`

---

## Common Workflows

### Development Workflow

**Step 1: Write code**
```python
def process(value):
    return value.strip()
```

**Step 2: Run quality gates**
```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

**Step 3: Review errors**
```
Basedpyright: Missing type annotation for 'value' and return type
Ruff: No issues
```

**Step 4: Fix errors**
```python
def process(value: str) -> str:
    return value.strip()
```

**Step 5: Verify fixes**
```bash
basedpyright src/  # Should pass
```

### Pre-Commit Workflow

**Setup pre-commit hooks:**

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - name: Ruff
        args: [--fix, --exit-non-zero-on-fix]
      - name: Ruff format
  - repo: https://github.com/pre-commit/mirrors-basedpyright
    rev: v1.1.0
    hooks:
      - name: Basedpyright
```

Install hooks:

```bash
pre-commit install
```

Now quality gates run automatically on commit!

### CI/CD Workflow

**GitHub Actions example:**

```yaml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install basedpyright ruff

      - name: Run quality gates
        run: |
          basedpyright src/
          ruff check src/
```

---

## Best Practices

### 1. Write Code with Types from Start

```python
# Good
def calculate_total(price: float, quantity: int) -> float:
    """Calculate total cost."""
    return price * quantity

# Avoid
def calculate_total(price, quantity):
    return price * quantity
```

### 2. Use Type Hints for Public APIs

```python
# Good
def process_data(data: list[str]) -> dict[str, int]:
    """Process a list of strings into a frequency dict."""
    return {item: data.count(item) for item in set(data)}

# Public function without type hints
def public_function():
    """Public API function."""
    pass
```

### 3. Configure IDE Integration

**VS Code:**

Install extensions:
- Basedpyright extension
- Ruff extension

Settings in `.vscode/settings.json`:

```json
{
    "python.languageServer": "Basedpyright",
    "basedpyright.config": {
        "typeCheckingMode": "basic"
    },
    "ruff.args": ["--config=pyproject.toml"]
}
```

**PyCharm:**

Enable Basedpyright:
- Settings → Tools → External Tools
- Add Basedpyright as external tool

### 4. Run Quality Gates Regularly

```bash
# During development
basedpyright src/
ruff check --fix src/

# Before committing
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md

# In CI/CD
basedpyright src/
ruff check src/
```

### 5. Fix Issues Promptly

Don't let issues accumulate:

```bash
# Check for issues
ruff check src/

# Auto-fix
ruff check --fix src/

# Check again
ruff check src/
```

---

## Troubleshooting

### Quality Gates Failing

**Problem:** Quality gates fail repeatedly

**Solutions:**
1. Check error messages carefully
2. Fix one issue at a time
3. Re-run quality gates after each fix
4. Use `--skip-quality` for rapid iteration
5. Check pyproject.toml configuration

**Example:**
```bash
# See detailed errors
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose

# Skip quality gates temporarily
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality
```

### Type Errors

**Problem:** Basedpyright reports many type errors

**Solutions:**
1. Start with basic mode, not strict
2. Add missing type annotations
3. Use `Any` for complex types initially
4. Gradually improve type coverage

```toml
[tool.basedpyright]
typeCheckingMode = "basic"  # Start here
```

### Ruff Too Strict

**Problem:** Ruff reports too many issues

**Solutions:**
1. Use auto-fix first: `ruff check --fix`
2. Ignore specific rules if needed
3. Gradually enable more rules
4. Use per-file ignores for test files

```toml
[tool.ruff]
select = ["E", "F", "W"]  # Start with basic rules
ignore = ["E501"]  # Ignore line length for now
```

### Performance Issues

**Problem:** Quality gates run slowly

**Solutions:**
1. Exclude test files
2. Use incremental checking
3. Run on specific files only

```toml
[tool.basedpyright]
exclude = ["tests/*"]
incremental = true
```

### Configuration Not Working

**Problem:** Changes to pyproject.toml don't take effect

**Solutions:**
1. Check file location (must be in project root)
2. Check TOML syntax
3. Restart IDE/terminal
4. Verify path to config file

---

## Integration Examples

### With GitHub Actions

```yaml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: pip install basedpyright ruff

      - name: Run Basedpyright
        run: basedpyright src/

      - name: Run Ruff
        run: |
          ruff check src/
          ruff format --check src/
```

### With Pre-commit

```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - name: Ruff
        args: [--fix, --exit-non-zero-on-fix]
      - name: Ruff format
        args: [--check]

  - repo: https://github.com/pre-commit/mirrors-basedpyright
    rev: v1.1.0
    hooks:
      - name: Basedpyright
```

### With Make

Create `Makefile`:

```makefile
.PHONY: quality format lint test

quality:
	basedpyright src/
	ruff check src/

format:
	ruff format src/
	ruff check --fix src/

lint:
	ruff check src/
	basedpyright src/

test:
	pytest tests/
```

Usage:

```bash
make quality  # Run quality gates
make format   # Auto-fix and format
make lint     # Check without auto-fix
```

---

## Advanced Topics

### Custom Type Checking Rules

Create custom rules in `pyproject.toml`:

```toml
[tool.basedpyright]
# Custom type checking settings
reportMissingTypeStubs = true
reportIncompatibleMethodOverride = true
reportIncompatibleVariableOverride = true
```

### Selective File Checking

Check specific files:

```bash
# Check single file
basedpyright src/module.py

# Check multiple files
basedpyright src/module1.py src/module2.py

# Use patterns
basedpyright src/models/*.py
```

### Ignoring Specific Errors

For basedpyright:

```python
# Ignore specific error
def func(x):  # type: ignore[no-untyped-def]
    return x
```

For Ruff:

```python
# Ignore specific line
x = 1  # noqa: E501
```

Or in pyproject.toml:

```toml
[tool.ruff]
ignore = ["E501", "F401"]
```

### Integrating with IDE

**VS Code integration:**

1. Install extensions:
   - Basedpyright
   - Ruff

2. Configure in `.vscode/settings.json`:

```json
{
    "python.languageServer": "Basedpyright",
    "basedpyright.config": {
        "typeCheckingMode": "basic"
    },
    "ruff.args": ["--config=pyproject.toml"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

---

## Examples

### Example 1: Simple Function

```python
# src/utils.py
def greet(name: str) -> str:
    """Greet a person."""
    return f"Hello, {name}!"
```

**Quality gate results:**
- Basedpyright: ✓ No errors
- Ruff: ✓ No issues

### Example 2: Class with Types

```python
# src/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User model."""
    name: str
    email: str
    age: Optional[int] = None

    def validate(self) -> bool:
        """Validate user data."""
        return "@" in self.email
```

**Quality gate results:**
- Basedpyright: ✓ No errors
- Ruff: ✓ No issues

### Example 3: Function with Errors

```python
# src/processor.py
import os
import json  # Unused - will be flagged

def process(data):  # Missing type annotations
    result = data.upper()  # Assumes string
    return result

result = process(123)  # Will fail at runtime
```

**Quality gate results:**
- Basedpyright: 2 errors
  - Missing type annotation for 'data' parameter
  - Missing type annotation for return type
- Ruff: 1 issue
  - F401: Unused 'json' import (auto-fixable)

**Fixed version:**
```python
# src/processor.py
import os

def process(data: str) -> str:
    """Process string data."""
    return data.upper()

result = process("hello")  # Type-safe
```

---

## Quick Reference

### Common Commands

```bash
# Run quality gates with epic
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md

# Skip quality gates
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality

# Run basedpyright manually
basedpyright src/

# Run ruff manually
ruff check --fix src/
ruff format src/

# Check specific files
basedpyright src/module.py
ruff check src/module.py
```

### Exit Codes

| Tool | Code | Meaning |
|------|------|---------|
| basedpyright | 0 | No errors |
| basedpyright | 1 | Errors found |
| ruff | 0 | No issues or auto-fixed |
| ruff | 1 | Issues need manual fix |

### Configuration File Location

- **pyproject.toml** - Project root (required)
- **.basedpyrightconfig** - Alternative to pyproject.toml
- **ruff.toml** - Alternative to pyproject.toml

---

## Support

If you need help:

1. Check [troubleshooting guide](../troubleshooting/quality-gates.md)
2. Review [example epics](../examples/example-epic-with-quality-gates.md)
3. Check the [API documentation](../api/README.md)
4. Run with `--verbose` for detailed logs
5. Check tool documentation:
   - [Basedpyright](https://github.com/ethanhs/basedpyright)
   - [Ruff](https://docs.astral.sh/ruff/)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-05 | 1.0 | Initial quality gates user guide | BMAD Team |

# Ruff Linting Fix Prompt

You are a code expert specializing in fixing linting issues found by ruff.

## Task

Fix the linting errors in the provided Python files to ensure they pass ruff linting checks.

## Ruff Rules Applied

- **E, W**: pycodestyle errors and warnings (formatting, style)
- **F**: pyflakes (unused imports, undefined names)
- **I**: isort (import sorting)
- **B**: flake8-bugbear (common bugs and anti-patterns)
- **C4**: flake8-comprehensions (list/dict/set comprehensions)
- **UP**: pyupgrade (modern Python features)

## Common Fixes

1. **Unused imports**:
   ```python
   # Wrong
   import os
   import sys  # unused

   # Correct
   import os
   ```

2. **Import sorting**:
   ```python
   # Wrong
   import sys
   import os

   # Correct
   import os
   import sys
   ```

3. **List comprehensions**:
   ```python
   # Wrong
   result = []
   for x in items:
       if x > 0:
           result.append(x * 2)

   # Correct
   result = [x * 2 for x in items if x > 0]
   ```

4. **Format strings**:
   ```python
   # Wrong
   name = "World"
   msg = "Hello " + name

   # Correct
   name = "World"
   msg = f"Hello {name}"
   ```

5. **Type checking**:
   ```python
   # Wrong
   if type(x) is str:

   # Correct
   if isinstance(x, str):
   ```

## Instructions

For each file with linting errors:
1. Read the current code
2. Identify all linting issues
3. Apply automatic fixes where possible
4. Make minimal manual changes for complex issues
5. Maintain the original code logic and functionality
6. Preserve docstrings and comments

## Output Format

For each file, provide:
- File path
- Explanation of changes made
- The corrected code (only if manual changes were needed)

## Example Response

**File: src/example.py**

**Issues Fixed:**
- Removed unused import `json`
- Sorted imports alphabetically
- Replaced string concatenation with f-string
- Used list comprehension instead of loop

**Corrected Code:**
```python
import os

def greet(name: str) -> str:
    """Greet a person by name."""
    names = ["Alice", "Bob", "Charlie"]
    return [f"Hello, {n}" for n in names if n != name]
```

Please fix all linting errors in the provided files.

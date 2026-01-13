# autoBMAD Coding Standards

**Version**: 2.0
**Date**: 2026-01-05
**Project**: autoBMAD Epic Automation System

---

## Overview

This document defines the coding standards for the autoBMAD epic automation system. These standards ensure code quality, maintainability, and consistency across all agents and workflow phases.

---

## Core Principles

### 1. DRY (Don't Repeat Yourself)
- **Rule**: Every piece of knowledge must have a single, authoritative representation
- **Application**: Extract common logic into shared functions, avoid code duplication
- **Example**: Create a shared error handling utility instead of duplicating try-catch blocks

### 2. KISS (Keep It Simple, Stupid)
- **Rule**: Design should be as simple as possible
- **Application**: Prefer simple, clear solutions over complex abstractions
- **Example**: Use a dictionary for configuration instead of creating a complex config class

### 3. YAGNI (You Aren't Gonna Need It)
- **Rule**: Only implement what is explicitly needed
- **Application**: Avoid adding functionality until it's necessary
- **Example**: Don't add a factory pattern for creating agents until you have multiple agent types

### 4. Single Responsibility Principle
- **Rule**: Each module/function should have one reason to change
- **Application**: Keep functions focused on a single task
- **Example**: Separate file reading logic from parsing logic

---

## Code Style Standards

### Python Style Guide
**Primary Standard**: PEP 8
**Formatter**: Black (line-length: 88)
**Linter**: Ruff (comprehensive rule set)

### Line Length
- **Maximum**: 88 characters (Black default)
- **Rationale**: Better readability on standard monitors, fits with GitHub diff views

### Indentation
- **Use**: 4 spaces (no tabs)
- **Rationale**: PEP 8 standard, consistent across editors

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| **Modules** | snake_case | `epic_driver.py` |
| **Classes** | PascalCase | `EpicDriver` |
| **Functions/Methods** | snake_case | `run_epic()` |
| **Variables** | snake_case | `epic_path` |
| **Constants** | UPPER_CASE | `MAX_ITERATIONS` |
| **Private Methods** | _leading_underscore | `_validate_epic()` |
| **Private Variables** | _leading_underscore | `_internal_state` |
| **Database Tables** | snake_case | `epic_processing` |
| **Database Columns** | snake_case | `created_at` |
| **Configuration Keys** | snake_case | `max_iterations` |

---

## Documentation Standards

### Docstrings
**Format**: Google Style

```python
def run_epic(epic_path: str) -> Dict[str, Any]:
    """
    Execute the complete epic processing workflow.

    This function orchestrates the SM-Dev-QA cycle for all stories
    in the epic, followed by code quality gates and test automation.

    Args:
        epic_path: Path to the epic markdown file

    Returns:
        Dict containing:
            - epic_id: Unique identifier for the processed epic
            - status: Final status ('completed' or 'failed')
            - total_stories: Total number of stories in epic
            - completed_stories: Number of stories that passed QA

    Raises:
        FileNotFoundError: If epic_path does not exist
        ValueError: If epic file is malformed

    Example:
        >>> result = run_epic('docs/epics/my-epic.md')
        >>> print(result['status'])
        'completed'
    """
    pass
```

### Module Docstrings
```python
"""
Epic Driver - Self-Contained BMAD Automation

Main orchestrator for the BMAD automation system.
Reads epic markdown files and drives SM-Dev-QA cycle.

Author: BMAD Development Team
Version: 2.0
"""

import argparse
import asyncio
...
```

### Class Docstrings
```python
class EpicDriver:
    """
    Main orchestrator for BMAD epic automation.

    This class coordinates the complete workflow from story creation
    through quality gates, managing state and error handling.

    Attributes:
        epic_path: Path to the epic markdown file
        tasks_dir: Directory containing task guidance files
        max_iterations: Maximum retry attempts for failed stories

    Example:
        >>> driver = EpicDriver('my-epic.md')
        >>> await driver.run_epic()
    """
```

### Inline Comments
**When to use**:
- Explain complex algorithms
- Document non-obvious decisions
- Note important assumptions

**Format**:
```python
# Good: Explains WHY
# Sort stories by priority to ensure critical paths are developed first
stories.sort(key=lambda s: s.priority, reverse=True)

# Bad: Explains WHAT (code is self-explanatory)
# Sort stories by priority
stories.sort(key=lambda s: s.priority, reverse=True)
```

---

## Type Hints Standards

### Required Type Hints
All functions and methods MUST have type hints for:
- Parameters
- Return values
- Class attributes (when possible)

### Type Hint Examples

```python
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

def process_stories(
    stories: List[Dict[str, Any]],
    max_iterations: int = 3
) -> Tuple[int, int]:
    """Process list of stories and return completion statistics."""
    pass

def get_epic_progress(epic_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve epic progress from database."""
    pass

def validate_file(file_path: Union[str, Path]) -> bool:
    """Validate that file exists and is readable."""
    pass
```

### Complex Type Hints
```python
from typing import TypedDict, Literal

class StoryStatus(TypedDict):
    """Type definition for story status tracking."""
    story_id: str
    title: str
    status: Literal['pending', 'in_progress', 'completed', 'failed']
    created_at: str

def update_story(story: StoryStatus) -> bool:
    """Update story status in database."""
    pass
```

### Generic Types
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Result(Generic[T]):
    """Generic result container."""
    def __init__(self, value: T):
        self.value = value

def create_result(value: T) -> Result[T]:
    """Create a result container."""
    return Result(value)
```

---

## Error Handling Standards

### Exception Hierarchy
```python
class BMADError(Exception):
    """Base exception for all BMAD-related errors."""
    pass

class EpicProcessingError(BMADError):
    """Raised when epic processing fails."""
    pass

class StoryValidationError(BMADError):
    """Raised when story validation fails."""
    pass

class QualityGateError(BMADError):
    """Raised when quality gate checks fail."""
    pass

class TestAutomationError(BMADError):
    """Raised when test automation fails."""
    pass
```

### Error Handling Pattern
```python
def process_story(story_id: str) -> bool:
    """
    Process a single story through SM-Dev-QA cycle.

    Returns:
        True if story passed QA, False otherwise

    Raises:
        StoryValidationError: If story data is invalid
        EpicProcessingError: If processing fails unexpectedly
    """
    try:
        # Validate input
        if not story_id:
            raise ValueError("story_id cannot be empty")

        # Attempt processing
        result = _process_story_internal(story_id)

        # Log success
        logger.info(f"Story {story_id} processed successfully")
        return result

    except ValueError as e:
        # Input validation errors - these are programming errors
        logger.error(f"Invalid input for story {story_id}: {e}")
        raise StoryValidationError(f"Invalid story data: {e}") from e

    except Exception as e:
        # Unexpected errors - log and continue
        logger.error(f"Unexpected error processing story {story_id}: {e}", exc_info=True)
        raise EpicProcessingError(f"Failed to process story {story_id}") from e
```

### Context Managers for Resources
```python
from contextlib import contextmanager

@contextmanager
def database_transaction(db_path: str):
    """Context manager for database transactions."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with database_transaction('progress.db') as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE stories SET status = ?", ('completed',))
```

---

## Async/Await Standards

### Async Function Naming
- Use `async def` for asynchronous functions
- Use descriptive names ending with action verbs
- Example: `process_stories_async()`, `validate_epic_async()`

### Async Error Handling
```python
async def process_stories(stories: List[Dict]) -> List[Dict]:
    """Process stories concurrently."""
    tasks = [process_story_async(story) for story in stories]
    results = []

    try:
        # Gather results with individual exception handling
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"Story processing failed: {e}")
                # Continue processing other stories

        return results

    except Exception as e:
        logger.error(f"Critical error in story processing: {e}")
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
        raise
```

### Async Context Managers
```python
class AsyncResourceManager:
    async def __aenter__(self):
        await self._acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._release()

# Usage
async with AsyncResourceManager() as resource:
    await resource.process()
```

---

## Database Standards

### SQLite Connection Management
```python
import sqlite3
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database connections."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        if not self.db_path.exists():
            self._create_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
```

### Query Patterns
```python
def create_epic_record(epic_path: str, db_manager: DatabaseManager) -> str:
    """Create new epic record and return epic_id."""
    epic_id = str(uuid.uuid4())

    with db_manager.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO epic_processing
            (epic_id, file_path, status, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (epic_id, epic_path, 'pending', datetime.utcnow().isoformat())
        )

    return epic_id

def get_stories_for_epic(epic_id: str, db_manager: DatabaseManager) -> List[Dict]:
    """Retrieve all stories for an epic."""
    with db_manager.get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM story_processing
            WHERE epic_id = ?
            ORDER BY created_at
            """,
            (epic_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
```

### Parameterized Queries
```python
# Good: Use parameterized queries
cursor.execute(
    "SELECT * FROM stories WHERE epic_id = ?",
    (epic_id,)
)

# Bad: String concatenation (SQL injection risk)
cursor.execute(
    f"SELECT * FROM stories WHERE epic_id = '{epic_id}'"
)
```

---

## Logging Standards

### Logger Configuration
```python
import logging
from typing import Optional

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    format_string = (
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('epic_automation.log')
        ]
    )

    return logging.getLogger(__name__)
```

### Logger Usage
```python
class EpicDriver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run_epic(self, epic_path: str):
        """Execute epic processing."""
        self.logger.info(f"Starting epic processing: {epic_path}")

        try:
            # Processing logic
            self.logger.debug(f"Loaded {len(stories)} stories")
            self.logger.info("Epic processing completed successfully")

        except Exception as e:
            self.logger.error(
                f"Epic processing failed: {e}",
                exc_info=True
            )
            raise
```

### Log Levels
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Something unexpected happened, but software still working
- **ERROR**: Serious problem, software not able to perform function
- **CRITICAL**: Very serious error, program may abort

---

## Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from autoBMAD.epic_automation.epic_driver import EpicDriver

class TestEpicDriver:
    """Test suite for EpicDriver."""

    @pytest.fixture
    def driver(self):
        """Create EpicDriver instance for testing."""
        return EpicDriver(
            epic_path='test_epic.md',
            max_iterations=3
        )

    def test_init(self, driver):
        """Test EpicDriver initialization."""
        assert driver.epic_path == 'test_epic.md'
        assert driver.max_iterations == 3
        assert driver.verbose is False

    @pytest.mark.asyncio
    async def test_run_epic_success(self, driver):
        """Test successful epic processing."""
        with patch.object(driver, 'load_task_guidance'):
            result = await driver.run_epic()
            assert result['status'] == 'completed'

    def test_run_epic_file_not_found(self, driver):
        """Test handling of missing epic file."""
        driver.epic_path = 'nonexistent.md'
        with pytest.raises(FileNotFoundError):
            driver.run_epic()
```

### Mocking Standards
```python
# Mock external dependencies
@patch('autoBMAD.epic_automation.state_manager.StateManager')
def test_with_mocked_state_manager(mock_state_manager):
    """Test with mocked state manager."""
    mock_instance = Mock()
    mock_instance.get_epic_progress.return_value = {'status': 'completed'}
    mock_state_manager.return_value = mock_instance

    # Test logic
    driver = EpicDriver()
    progress = driver.state_manager.get_epic_progress('epic-123')
    assert progress['status'] == 'completed'
```

### Test Coverage
- **Minimum Coverage**: 80% for critical paths
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows

---

## Code Quality Standards

### Basedpyright Configuration
```toml
[tool.basedpyright]
pythonVersion = "3.8"
pythonPlatform = "All"
typeCheckingMode = "strict"
reportGeneralTypeIssues = true
reportOptionalMemberAccess = true
reportOptionalSubscript = true
reportPrivateImportUsage = true
exclude = [
    "**/__pycache__",
    "**/.venv",
    "**/venv",
    "build/",
    "dist/"
]
```

### Ruff Configuration
```toml
[tool.ruff]
target-version = "py38"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]
```

### Pre-commit Hooks
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

---

## File Organization Standards

### Import Order
```python
"""
Module docstring
"""

# Standard library imports
import argparse
import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Third-party imports
import pytest

# Local application imports
from sm_agent import SMAgent
from dev_agent import DevAgent
from state_manager import StateManager
```

### Module-Level Variables
```python
# Constants (UPPER_CASE)
MAX_ITERATIONS = 3
DEFAULT_SOURCE_DIR = "src"
DEFAULT_TEST_DIR = "tests"

# Module-level configuration
logger = logging.getLogger(__name__)

# Public exports
__all__ = [
    'EpicDriver',
    'SMAgent',
    'DevAgent',
    'QAAgent'
]
```

---

## Configuration Standards

### Environment Variables
```python
import os
from typing import Optional

# Environment-based configuration
CLAUDE_API_KEY: Optional[str] = os.getenv('CLAUDE_API_KEY')
MAX_CONCURRENT_STORIES: int = int(os.getenv('MAX_CONCURRENT_STORIES', '4'))
VERBOSE_LOGGING: bool = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'

def get_config() -> Dict[str, Any]:
    """Get application configuration."""
    return {
        'claude_api_key': CLAUDE_API_KEY,
        'max_concurrent': MAX_CONCURRENT_STORIES,
        'verbose': VERBOSE_LOGGING,
    }
```

### Configuration Classes
```python
@dataclass
class QualityGateConfig:
    """Configuration for quality gates."""
    max_retries: int = 3
    timeout_seconds: int = 300
    basedpyright_strict: bool = True
    ruff_auto_fix: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
```

---

## Security Standards

### Input Validation
```python
from pathlib import Path
from typing import Union

def validate_epic_path(path: Union[str, Path]) -> Path:
    """
    Validate epic file path for security.

    Raises:
        ValueError: If path is invalid or unsafe
    """
    path = Path(path)

    # Check if path exists
    if not path.exists():
        raise FileNotFoundError(f"Epic file not found: {path}")

    # Check if it's a file
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    # Check file extension
    if path.suffix.lower() != '.md':
        raise ValueError(f"Epic file must be markdown (.md): {path}")

    # Check for directory traversal
    if '..' in str(path):
        raise ValueError(f"Invalid path (directory traversal): {path}")

    return path
```

### SQL Injection Prevention
```python
# Always use parameterized queries
def get_story(story_id: str, db_path: str) -> Optional[Dict]:
    """Get story by ID - safely."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM story_processing WHERE story_id = ?",
            (story_id,)  # Parameterized - safe!
        )
        row = cursor.fetchone()
        return dict(row) if row else None
```

### Secure Subprocess Execution
```python
import subprocess
import shlex

async def run_command(command: str, timeout: int = 30) -> str:
    """Run shell command safely."""
    # Validate command (whitelist allowed commands)
    allowed_commands = {'basedpyright', 'ruff', 'pytest'}
    cmd_parts = shlex.split(command)
    if not cmd_parts or cmd_parts[0] not in allowed_commands:
        raise ValueError(f"Command not allowed: {command}")

    # Use subprocess with timeout
    process = await asyncio.create_subprocess_exec(
        *cmd_parts,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        return stdout.decode()
    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError(f"Command timed out after {timeout}s")
```

---

## Performance Standards

### Async/Await for I/O
```python
# Good: Use async for I/O operations
async def load_epic_file(epic_path: Path) -> str:
    """Load epic file asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        epic_path.read_text,
        encoding='utf-8'
    )

# Bad: Blocking I/O in async context
async def load_epic_file_bad(epic_path: Path) -> str:
    """Blocking I/O - don't do this."""
    return epic_path.read_text()  # Blocks event loop!
```

### Efficient Database Queries
```python
# Good: Use transactions for multiple operations
def update_epic_status(epic_id: str, status: str, db_path: str):
    """Update epic status efficiently."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("BEGIN TRANSACTION")
        try:
            conn.execute(
                "UPDATE epic_processing SET status = ? WHERE epic_id = ?",
                (status, epic_id)
            )
            conn.execute(
                "UPDATE epic_processing SET updated_at = ? WHERE epic_id = ?",
                (datetime.utcnow().isoformat(), epic_id)
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
```

### Resource Cleanup
```python
# Use context managers for automatic cleanup
def process_file(file_path: Path) -> str:
    """Process file with automatic cleanup."""
    with open(file_path, 'r') as f:
        content = f.read()
    # File automatically closed

# Or use async context managers
async def process_resources():
    """Process resources with async cleanup."""
    async with AsyncResource() as resource:
        await resource.process()
    # Resource automatically cleaned up
```

---

## Code Review Checklist

### General
- [ ] Code follows DRY, KISS, and YAGNI principles
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] No duplicate code
- [ ] Code is self-documenting with clear names
- [ ] No commented-out code
- [ ] No TODOs without tracking issues

### Error Handling
- [ ] Specific exceptions are raised
- [ ] Exceptions are logged appropriately
- [ ] Resources are cleaned up on errors
- [ ] No bare except clauses
- [ ] Finally blocks used for cleanup

### Testing
- [ ] Unit tests for all public functions
- [ ] Tests cover edge cases
- [ ] Tests are isolated (no dependencies between tests)
- [ ] Mocks are used appropriately
- [ ] Test coverage ≥ 80%

### Security
- [ ] All inputs are validated
- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] Sensitive data not logged
- [ ] File paths are validated

### Performance
- [ ] I/O operations are async
- [ ] Database queries are efficient
- [ ] Resources are cleaned up
- [ ] No blocking operations in async context
- [ ] Appropriate data structures used

---

## Tools and Commands

### Code Formatting
```bash
# Format code with Black
black autoBMAD/

# Sort imports with isort
isort autoBMAD/

# Run both
black autoBMAD/ && isort autoBMAD/
```

### Linting
```bash
# Run Ruff linting
ruff check autoBMAD/

# Fix auto-fixable issues
ruff check --fix autoBMAD/

# Run Basedpyright
basedpyright autoBMAD/
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=autoBMAD tests/

# Run specific test file
pytest tests/unit/test_epic_driver.py -v
```

### Pre-commit
```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

---

## Summary

These coding standards ensure:
- **Consistency**: Uniform code style across the project
- **Quality**: Type safety, testing, and error handling
- **Maintainability**: Clear, simple, well-documented code
- **Security**: Safe handling of inputs and resources
- **Performance**: Efficient execution patterns

All developers working on the autoBMAD project must follow these standards to ensure code quality and project maintainability.

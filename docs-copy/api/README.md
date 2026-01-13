# API Documentation

This document provides detailed API documentation for the autoBMAD Epic Automation System.

## Overview

The autoBMAD system consists of several core components:

1. **EpicDriver** - Main orchestrator
2. **CodeQualityAgent** - Quality gates execution
3. **TestAutomationAgent** - Test automation
4. **StateManager** - State persistence

---

## EpicDriver

Main orchestrator for the complete BMAD workflow.

### Class: EpicDriver

```python
class EpicDriver:
    """Main orchestrator for complete BMAD workflow."""
```

#### Constructor

```python
def __init__(
    self,
    epic_path: str,
    tasks_dir: str = ".bmad-core/tasks",
    max_iterations: int = 3,
    retry_failed: bool = False,
    verbose: bool = False,
    concurrent: bool = False,
    use_claude: bool = True,
    source_dir: str = "src",
    test_dir: str = "tests",
    skip_quality: bool = False,
    skip_tests: bool = False
)
```

**Parameters:**
- `epic_path` (str): Path to the epic markdown file
- `tasks_dir` (str): Directory containing task guidance files (default: ".bmad-core/tasks")
- `max_iterations` (int): Maximum retry attempts for failed stories (default: 3)
- `retry_failed` (bool): Enable automatic retry of failed stories (default: False)
- `verbose` (bool): Enable detailed logging output (default: False)
- `concurrent` (bool): Process stories in parallel (experimental, default: False)
- `use_claude` (bool): Use Claude Code CLI for real implementation (default: True)
- `source_dir` (str): Source code directory for QA checks (default: "src")
- `test_dir` (str): Test directory for QA checks (default: "tests")
- `skip_quality` (bool): Skip code quality gates (default: False)
- `skip_tests` (bool): Skip test automation (default: False)

**Example:**
```python
driver = EpicDriver(
    epic_path="docs/epics/my-epic.md",
    source_dir="src",
    test_dir="tests",
    skip_quality=False,
    skip_tests=False,
    verbose=True
)
```

#### Methods

##### run()

Execute the complete 5-phase workflow.

```python
async def run(self) -> bool
```

**Returns:**
- `bool`: True if epic completed successfully, False otherwise

**Raises:**
- `FileNotFoundError`: If epic file doesn't exist
- `Exception`: Any error during execution

**Example:**
```python
result = await driver.run()
if result:
    print("Epic completed successfully")
else:
    print("Epic failed")
```

---

## CodeQualityAgent

Orchestrates basedpyright and ruff quality checks.

### Class: CodeQualityAgent

```python
class CodeQualityAgent:
    """
    Orchestrates basedpyright and ruff quality checks.

    This agent executes code quality gates after all stories in an epic
    complete the SM-Dev-QA cycle. It runs basedpyright type checking and
    ruff linting, invokes Claude agents to fix issues, and tracks progress
    in the state manager.

    Attributes:
        state_manager: StateManager instance for progress tracking
        epic_id: Unique identifier for the epic being processed
        max_iterations: Maximum retry attempts (default: 3)
        skip_quality: Whether to skip quality gates
        logger: Logger instance
    """
```

#### Constructor

```python
def __init__(
    self,
    state_manager: StateManager,
    epic_id: str,
    skip_quality: bool = False
)
```

**Parameters:**
- `state_manager` (StateManager): StateManager instance for progress tracking
- `epic_id` (str): Unique identifier for the epic being processed
- `skip_quality` (bool): Skip quality gates (default: False)

**Example:**
```python
agent = CodeQualityAgent(
    state_manager=state_manager,
    epic_id="epic-001",
    skip_quality=False
)
```

#### run_quality_gates()

Execute complete quality gate workflow.

```python
async def run_quality_gates(
    self,
    source_dir: str = "src",
    skip_quality: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `source_dir` (str): Directory containing .py files to check (default: "src")
- `skip_quality` (bool): If True, bypass quality gates (default: False)

**Returns:**
Dict with:
- `status` (str): 'completed', 'failed', 'skipped', or 'in_progress'
- `epic_id` (str): Epic identifier
- `source_dir` (str): Source directory checked
- `file_count` (int): Number of Python files checked
- `basedpyright` (dict): Results from type checking
- `ruff` (dict): Results from linting
- `iterations` (int): Number of retry attempts
- `errors` (list): List of error messages

**Raises:**
- `QualityGateError`: If quality gates fail after max iterations

**Example:**
```python
results = await agent.run_quality_gates("src/")
print(f"Status: {results['status']}")
print(f"Files checked: {results['file_count']}")
print(f"Errors: {results['errors']}")
```

**Example Output:**
```python
{
    "status": "completed",
    "epic_id": "epic-001",
    "source_dir": "src",
    "file_count": 15,
    "basedpyright": {
        "status": "completed",
        "errors": 0,
        "execution_time": 12.5
    },
    "ruff": {
        "status": "completed",
        "errors_fixed": 5,
        "execution_time": 2.3
    },
    "iterations": 1,
    "errors": []
}
```

---

## TestAutomationAgent

Orchestrates pytest test execution and debugging.

### Class: TestAutomationAgent

```python
class TestAutomationAgent:
    """
    Orchestrates pytest test execution and debugging.

    This agent executes test automation after quality gates complete.
    It runs pytest on all test files, invokes Claude agents to fix failures,
    and uses debugpy for persistent test failures.

    Attributes:
        state_manager: StateManager instance for progress tracking
        epic_id: Unique identifier for the epic being processed
        max_retry_attempts: Maximum retry attempts (default: 5)
        debugpy_timeout: Debugpy session timeout in seconds (default: 300)
        skip_tests: Whether to skip test automation
        logger: Logger instance
    """
```

#### Constructor

```python
def __init__(
    self,
    state_manager: StateManager,
    epic_id: str,
    skip_tests: bool = False
)
```

**Parameters:**
- `state_manager` (StateManager): StateManager instance for progress tracking
- `epic_id` (str): Unique identifier for the epic being processed
- `skip_tests` (bool): Skip test automation (default: False)

**Example:**
```python
agent = TestAutomationAgent(
    state_manager=state_manager,
    epic_id="epic-001",
    skip_tests=False
)
```

#### run_test_automation()

Execute complete test automation workflow.

```python
async def run_test_automation(
    self,
    test_dir: str = "tests",
    skip_tests: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `test_dir` (str): Directory containing tests to execute (default: "tests")
- `skip_tests` (bool): If True, bypass test automation (default: False)

**Returns:**
Dict with:
- `status` (str): 'completed', 'failed', 'skipped', or 'in_progress'
- `epic_id` (str): Epic identifier
- `test_dir` (str): Test directory executed
- `pytest` (dict): Results from test execution
- `iterations` (int): Number of retry attempts
- `retry_attempts` (int): Number of retries
- `debugpy_sessions` (list): List of debugpy sessions
- `errors` (list): List of error messages

**Raises:**
- `TestAutomationError`: If tests fail after max retries

**Example:**
```python
results = await agent.run_test_automation("tests/")
print(f"Status: {results['status']}")
print(f"Tests passed: {results['pytest']['passed']}")
print(f"Tests failed: {results['pytest']['failed']}")
```

**Example Output:**
```python
{
    "status": "completed",
    "epic_id": "epic-001",
    "test_dir": "tests",
    "pytest": {
        "status": "completed",
        "passed": 45,
        "failed": 0,
        "skipped": 2,
        "execution_time": 45.2
    },
    "iterations": 1,
    "retry_attempts": 0,
    "debugpy_sessions": [],
    "errors": []
}
```

---

## StateManager

SQLite-based state manager for tracking story progress.

### Class: StateManager

```python
class StateManager:
    """
    SQLite-based state manager for tracking story progress.

    Manages state persistence for the BMAD automation system.
    Tracks story status, quality gate results, and test automation results.

    Attributes:
        db_path: Path to SQLite database file
        _lock: Async lock for thread-safe operations
    """
```

#### Constructor

```python
def __init__(self, db_path: str = "progress.db")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file (default: "progress.db")

**Example:**
```python
state_manager = StateManager("progress.db")
```

#### update_story_status()

Update story status in the database.

```python
async def update_story_status(
    self,
    story_path: str,
    status: str,
    phase: str | None = None,
    iteration: int | None = None,
    qa_result: dict[str, Any] | None = None,
    error: str | None = None,
    epic_path: str | None = None
) -> bool
```

**Parameters:**
- `story_path` (str): Path to the story file
- `status` (str): Status (e.g., "completed", "failed", "in_progress")
- `phase` (str | None): Current phase (e.g., "sm", "dev", "qa", "quality", "test")
- `iteration` (int | None): Current iteration number
- `qa_result` (dict | None): QA result data
- `error` (str | None): Error message if any
- `epic_path` (str | None): Epic file path

**Returns:**
- `bool`: True if update successful, False otherwise

**Example:**
```python
await state_manager.update_story_status(
    story_path="docs/stories/001.md",
    status="completed",
    phase="qa",
    iteration=1,
    qa_result={"passed": True},
    epic_path="docs/epics/my-epic.md"
)
```

#### update_quality_phase_status()

Update quality gate phase status.

```python
async def update_quality_phase_status(
    self,
    epic_id: str,
    file_path: str,
    error_count: int,
    fix_status: str = "pending",
    basedpyright_errors: str | None = None,
    ruff_errors: str | None = None
) -> bool
```

**Parameters:**
- `epic_id` (str): Epic identifier
- `file_path` (str): Path to file being checked
- `error_count` (int): Number of errors found
- `fix_status` (str): Fix status (default: "pending")
- `basedpyright_errors` (str | None): Basedpyright error details
- `ruff_errors` (str | None): Ruff error details

**Returns:**
- `bool`: True if update successful, False otherwise

**Example:**
```python
await state_manager.update_quality_phase_status(
    epic_id="epic-001",
    file_path="src/module.py",
    error_count=3,
    fix_status="in_progress",
    basedpyright_errors="Missing type annotation",
    ruff_errors="Line too long"
)
```

#### update_test_automation_status()

Update test automation phase status.

```python
async def update_test_automation_status(
    self,
    epic_id: str,
    test_file_path: str,
    failure_count: int,
    fix_status: str = "pending",
    debug_info: str | None = None
) -> bool
```

**Parameters:**
- `epic_id` (str): Epic identifier
- `test_file_path` (str): Path to test file
- `failure_count` (int): Number of failures
- `fix_status` (str): Fix status (default: "pending")
- `debug_info` (str | None): Debug information

**Returns:**
- `bool`: True if update successful, False otherwise

**Example:**
```python
await state_manager.update_test_automation_status(
    epic_id="epic-001",
    test_file_path="tests/test_module.py",
    failure_count=2,
    fix_status="in_progress",
    debug_info="AssertionError on line 45"
)
```

#### get_story_status()

Get story status from database.

```python
async def get_story_status(self, story_path: str) -> dict[str, Any] | None
```

**Parameters:**
- `story_path` (str): Path to the story file

**Returns:**
- `dict | None`: Story status data or None if not found

**Example:**
```python
status = await state_manager.get_story_status("docs/stories/001.md")
if status:
    print(f"Status: {status['status']}")
    print(f"Phase: {status['phase']}")
```

#### get_all_stories()

Get all stories for an epic.

```python
async def get_all_stories(self, epic_path: str) -> list[dict[str, Any]]
```

**Parameters:**
- `epic_path` (str): Path to the epic file

**Returns:**
- `list[dict]`: List of story status data

**Example:**
```python
stories = await state_manager.get_all_stories("docs/epics/my-epic.md")
for story in stories:
    print(f"{story['story_path']}: {story['status']}")
```

#### get_epic_summary()

Get epic-level summary.

```python
async def get_epic_summary(self, epic_id: str) -> dict[str, Any] | None
```

**Parameters:**
- `epic_id` (str): Epic identifier

**Returns:**
- `dict | None`: Epic summary data or None if not found

**Example:**
```python
summary = await state_manager.get_epic_summary("epic-001")
if summary:
    print(f"Total stories: {summary['total_stories']}")
    print(f"Completed: {summary['completed_stories']}")
    print(f"Quality phase: {summary['quality_phase_status']}")
    print(f"Test phase: {summary['test_phase_status']}")
```

---

## Data Models

### Story Status

```python
{
    "id": int,
    "epic_path": str,
    "story_path": str,
    "status": str,  # "completed", "failed", "in_progress", "pending"
    "iteration": int,
    "qa_result": str | None,
    "error_message": str | None,
    "created_at": str,
    "updated_at": str,
    "phase": str | None  # "sm", "dev", "qa", "quality", "test"
}
```

### Quality Gate Results

```python
{
    "status": str,  # "completed", "failed", "skipped", "in_progress"
    "epic_id": str,
    "source_dir": str,
    "file_count": int,
    "basedpyright": {
        "status": str,
        "errors": int,
        "execution_time": float,
        "files_checked": int
    },
    "ruff": {
        "status": str,
        "errors_fixed": int,
        "execution_time": float,
        "files_checked": int
    },
    "iterations": int,
    "errors": list[str]
}
```

### Test Automation Results

```python
{
    "status": str,  # "completed", "failed", "skipped", "in_progress"
    "epic_id": str,
    "test_dir": str,
    "pytest": {
        "status": str,
        "passed": int,
        "failed": int,
        "skipped": int,
        "execution_time": float,
        "test_files": int
    },
    "iterations": int,
    "retry_attempts": int,
    "debugpy_sessions": list[dict],
    "errors": list[str]
}
```

---

## Error Handling

### Exceptions

#### QualityGateError

Raised when quality gates fail after max iterations.

```python
class QualityGateError(Exception):
    """Quality gate failure exception."""
    pass
```

#### TestAutomationError

Raised when test automation fails after max retries.

```python
class TestAutomationError(Exception):
    """Test automation failure exception."""
    pass
```

### Error Codes

| Code | Description | Action |
|------|-------------|--------|
| 0 | Success | No action needed |
| 1 | General error | Check logs |
| 2 | Configuration error | Fix configuration |
| 3 | Quality gate failed | Fix code quality issues |
| 4 | Test failure | Fix tests |
| 5 | State error | Check database |

---

## Usage Examples

### Complete Workflow Example

```python
import asyncio
from autoBMAD.epic_automation import (
    EpicDriver,
    CodeQualityAgent,
    TestAutomationAgent,
    StateManager
)

async def main():
    # Initialize components
    state_manager = StateManager("progress.db")
    driver = EpicDriver(
        epic_path="docs/epics/my-epic.md",
        source_dir="src",
        test_dir="tests",
        skip_quality=False,
        skip_tests=False,
        verbose=True
    )

    # Run complete workflow
    result = await driver.run()

    if result:
        print("Epic completed successfully!")
    else:
        print("Epic failed!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Quality Gates Only Example

```python
import asyncio
from autoBMAD.epic_automation import (
    CodeQualityAgent,
    StateManager
)

async def main():
    state_manager = StateManager("progress.db")
    agent = CodeQualityAgent(
        state_manager=state_manager,
        epic_id="epic-001",
        skip_quality=False
    )

    results = await agent.run_quality_gates("src/")

    print(f"Quality gates status: {results['status']}")
    print(f"Basedpyright errors: {results['basedpyright']['errors']}")
    print(f"Ruff errors fixed: {results['ruff']['errors_fixed']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Test Automation Only Example

```python
import asyncio
from autoBMAD.epic_automation import (
    TestAutomationAgent,
    StateManager
)

async def main():
    state_manager = StateManager("progress.db")
    agent = TestAutomationAgent(
        state_manager=state_manager,
        epic_id="epic-001",
        skip_tests=False
    )

    results = await agent.run_test_automation("tests/")

    print(f"Test automation status: {results['status']}")
    print(f"Tests passed: {results['pytest']['passed']}")
    print(f"Tests failed: {results['pytest']['failed']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### 1. Error Handling

Always wrap API calls in try-except blocks:

```python
try:
    results = await agent.run_quality_gates("src/")
except QualityGateError as e:
    logger.error(f"Quality gates failed: {e}")
    # Handle error appropriately
```

### 2. State Management

Use StateManager to track progress:

```python
# Update status during execution
await state_manager.update_story_status(
    story_path="docs/stories/001.md",
    status="in_progress",
    phase="quality"
)

# Check status before proceeding
status = await state_manager.get_story_status("docs/stories/001.md")
if status["status"] == "completed":
    # Move to next step
    pass
```

### 3. Configuration

Use appropriate configuration for your use case:

```python
# For development - skip quality gates
driver = EpicDriver(
    epic_path="docs/epics/my-epic.md",
    skip_quality=True,
    skip_tests=False
)

# For production - run all checks
driver = EpicDriver(
    epic_path="docs/epics/my-epic.md",
    skip_quality=False,
    skip_tests=False,
    max_iterations=5,
    retry_failed=True
)
```

### 4. Logging

Enable verbose logging for debugging:

```python
driver = EpicDriver(
    epic_path="docs/epics/my-epic.md",
    verbose=True  # Enable detailed logs
)
```

### 5. Async/Await

Always use async/await pattern:

```python
# Correct
results = await agent.run_quality_gates("src/")

# Incorrect - will cause issues
results = agent.run_quality_gates("src/")
```

---

## Support

For API issues:

1. Check the [troubleshooting guide](../troubleshooting/quality-gates.md)
2. Review the [user guide](../user-guide/quality-gates.md)
3. Check example epics in `docs/examples/`
4. Enable verbose logging with `--verbose`
5. Review logs for detailed error information

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-05 | 1.0 | Initial API documentation | BMAD Team |

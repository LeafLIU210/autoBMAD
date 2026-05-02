# DocuSwarm Coding Standards

**Version**: 2.1  
**Date**: 2026-02-20  
**Status**: Approved  

---

## 1. Overview

This document defines the coding standards and conventions for the DocuSwarm project. All contributors must follow these guidelines to maintain code quality and consistency.

---

## 2. Python Code Style

### 2.1 General Guidelines

| Rule | Standard |
|------|----------|
| **Python Version** | 3.10+ |
| **Line Length** | 100 characters max |
| **Indentation** | 4 spaces (no tabs) |
| **Encoding** | UTF-8 |
| **Formatter** | Black |
| **Linter** | Ruff |
| **Type Checker** | Basedpyright |

### 2.2 Imports

```python
# Standard library imports (alphabetical)
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

# Third-party imports (alphabetical)
from kimi_agent_sdk import Session, prompt
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Local imports (alphabetical)
from docuswarm.agents import IndependentAgent, EvaluatorAgent
from docuswarm.context import ContextManager
from docuswarm.storage import StateManager
```

**Import Rules**:
- Group imports: stdlib → third-party → local
- One blank line between groups
- Alphabetical within groups
- Prefer explicit imports over `from module import *`
- Use absolute imports

### 2.3 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Module** | lowercase_with_underscores | `state_manager.py` |
| **Class** | PascalCase | `IndependentAgent` |
| **Function** | lowercase_with_underscores | `build_context()` |
| **Method** | lowercase_with_underscores | `execute_node()` |
| **Variable** | lowercase_with_underscores | `run_id` |
| **Constant** | UPPERCASE_WITH_UNDERSCORES | `MAX_ITERATIONS` |
| **Private** | _leading_underscore | `_internal_method()` |
| **Type Alias** | PascalCase | `NodeState` |

### 2.4 Type Hints

```python
# Always use type hints for function signatures
def execute_node(
    node_id: str,
    context: dict,
    max_iterations: int = 3
) -> NodeResult:
    ...

# Use TypedDict for complex state objects
class NodeRunState(TypedDict):
    run_id: str
    subject_context: dict
    completed_nodes: List[str]
    deliverables: Dict[str, dict]

# Use Optional for nullable types
def get_result(node_id: str) -> Optional[dict]:
    ...

# Use Union for multiple types (prefer | syntax in 3.10+)
def process(data: str | bytes) -> dict:
    ...
```

### 2.5 Docstrings

```python
def execute_node_run(
    initial_context: dict,
    run_id: str | None = None
) -> NodeRunState:
    """Execute the DocuSwarm node run.
    
    Runs all nodes sequentially from Analyst to PO,
    with dual-agent quality control at each node.
    
    Args:
        initial_context: Project context including requirements.
        run_id: Optional run ID. Generated if not provided.
    
    Returns:
        Final node run state with all deliverables.
    
    Raises:
        NodeExecutionError: If a node fails after max iterations.
        ValidationError: If initial_context is invalid.
    
    Example:
        >>> result = await execute_node_run({"project_name": "MyApp"})
        >>> print(result["deliverables"]["analyst"]["title"])
    """
    ...


class IndependentAgent:
    """Agent responsible for creating deliverables.
    
    The Independent Agent uses BMAD personas to generate
    high-quality documents and clarifying questions.
    
    Attributes:
        node_id: The node this agent belongs to.
        persona: BMAD persona configuration.
        llm: LangChain LLM instance.
    """
    ...
```

**Docstring Rules**:
- Use Google-style docstrings
- Required for all public functions, classes, and modules
- Include Args, Returns, Raises sections as applicable
- Include Example section for complex functions

---

## 3. Async Programming

### 3.1 Async/Await Patterns

```python
# Always use async for I/O operations
async def fetch_llm_response(prompt: str) -> str:
    response = await llm.ainvoke(prompt)
    return response.content

# Use asyncio.gather for parallel operations
async def execute_parallel_nodes(nodes: List[str]) -> List[dict]:
    tasks = [execute_node(n) for n in nodes]
    return await asyncio.gather(*tasks)

# Handle exceptions in async code
async def safe_execute(operation):
    try:
        return await operation()
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### 3.2 Async Context Managers

```python
# Use async context managers for resources
async with aiofiles.open(path, 'r') as f:
    content = await f.read()

# Create async context managers
class AsyncDatabaseConnection:
    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.db_path)
        return self.conn
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()
```

---

## 4. Error Handling

### 4.1 Exception Hierarchy

```python
# Base exception for DocuSwarm
class DocuSwarmError(Exception):
    """Base exception for all DocuSwarm errors."""
    pass

# Specific exceptions
class NodeExecutionError(DocuSwarmError):
    """Node execution error."""
    pass

class NodeError(DocuSwarmError):
    """Node execution error."""
    def __init__(self, node_id: str, message: str):
        self.node_id = node_id
        super().__init__(f"Node {node_id}: {message}")

class ValidationError(DocuSwarmError):
    """Input validation error."""
    pass

class ContextIsolationError(DocuSwarmError):
    """Context isolation violation."""
    pass
```

### 4.2 Error Handling Patterns

```python
# Specific exception handling
try:
    result = await execute_node(node_id)
except NodeError as e:
    logger.error(f"Node failed: {e.node_id}")
    raise
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return None

# Never use bare except
# BAD:
try:
    ...
except:  # Never do this
    pass

# GOOD:
try:
    ...
except Exception as e:
    logger.exception("Unexpected error")
    raise

# Use context for additional info
try:
    result = await llm.ainvoke(prompt)
except Exception as e:
    raise NodeError(node_id, f"LLM call failed: {e}") from e
```

---

## 5. Logging

### 5.1 Logger Configuration

```python
import logging

# Configure at module level
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug info: %s", data)
logger.info("Node run started: %s", run_id)
logger.warning("Iteration %d exceeded threshold", iteration)
logger.error("Node %s failed: %s", node_id, error)
logger.exception("Unexpected error")  # Includes traceback
```

### 5.2 Log Message Format

```python
# Include context in log messages
logger.info(
    "Node completed",
    extra={
        "run_id": run_id,
        "node_id": node_id,
        "score": alignment_score,
        "iterations": iteration_count
    }
)

# Use structured logging format
LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] %(name)s "
    "[%(run_id)s:%(node_id)s] %(message)s"
)
```

---

## 6. Testing Standards

### 6.1 Test Structure

```python
# tests/test_node_execution.py
import pytest
from docuswarm.node_execution import SequentialNodeExecution

class TestSequentialNodeExecution:
    """Tests for SequentialNodeExecution class."""
    
    @pytest.fixture
    def node_execution(self, tmp_path):
        """Create node execution instance for testing."""
        db_path = tmp_path / "test.db"
        return SequentialNodeExecution(str(db_path))
    
    def test_node_execution_initialization(self, node_execution):
        """Test node execution initializes with correct sequence."""
        assert node_execution.SEQUENCE == ["analyst", "pm", "ux", "architect", "po"]
    
    @pytest.mark.asyncio
    async def test_execute_returns_state(self, node_execution):
        """Test execute returns complete node run state."""
        context = {"project_name": "Test"}
        result = await node_execution.run(context)
        
        assert "run_id" in result
        assert result["status"] == "completed"
    
    @pytest.mark.parametrize("status", ["running", "paused", "completed"])
    def test_valid_status_values(self, node_run, status):
        """Test all valid status values are accepted."""
        assert status in ["running", "paused", "completed", "failed"]
```

### 6.2 Test Naming

| Pattern | Example |
|---------|---------|
| `test_<method>_<scenario>` | `test_execute_returns_state` |
| `test_<method>_when_<condition>` | `test_execute_when_context_empty` |
| `test_<method>_raises_<exception>` | `test_execute_raises_validation_error` |

### 6.3 Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation completes successfully."""
    result = await async_function()
    assert result is not None

# Use pytest-asyncio fixtures
@pytest.fixture
async def async_client():
    client = AsyncClient()
    yield client
    await client.close()
```

---

## 7. Code Organization

### 7.1 Module Structure

```python
# docuswarm/agents/independent.py

"""Independent Agent implementation.

This module contains the IndependentAgent class responsible
for creating deliverables and generating questions.
"""

from __future__ import annotations

# Imports...

# Constants
MAX_TOKENS = 32768
DEFAULT_TEMPERATURE = 0.7

# Type definitions
class AgentConfig(TypedDict):
    persona_path: str
    model_config: dict

# Main class
class IndependentAgent:
    """Independent Agent for deliverable creation."""
    
    def __init__(self, config: AgentConfig):
        ...
    
    async def execute(self, context: dict) -> dict:
        ...
    
    # Private methods
    def _build_prompt(self) -> str:
        ...
    
    def _validate_output(self, output: dict) -> bool:
        ...

# Module-level functions (if needed)
def create_agent(node_id: str) -> IndependentAgent:
    """Factory function to create agent."""
    ...
```

### 7.2 File Size Guidelines

| Guideline | Limit |
|-----------|-------|
| Lines per file | < 500 |
| Functions per class | < 20 |
| Lines per function | < 50 |
| Cyclomatic complexity | < 10 |

---

## 8. Configuration

### 8.1 Environment Variables

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration from environment."""
    
    # Required - P1-2: Only ANTHROPIC_API_KEY is supported
    api_key: str = os.environ["ANTHROPIC_API_KEY"]
    
    # Optional with defaults
    database_path: str = os.getenv("DATABASE_PATH", "docuswarm.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "3"))
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
```

### 8.2 YAML Configuration

```yaml
# config/docuswarm.yaml
node_execution:
  max_iterations: 3
  
llm:
  provider: kimi
  models:
    independent:
      temperature: 0.7
      max_tokens: 32768
```

```python
# Loading configuration
import yaml
from pathlib import Path

def load_config(config_path: str = "config/docuswarm.yaml") -> dict:
    """Load YAML configuration."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)
```

---

## 9. Security Guidelines

### 9.1 Secrets Management

```python
# NEVER hardcode secrets
# BAD:
api_key = "sk-xxxxx"

# GOOD: P1-2 - Use ANTHROPIC_API_KEY
api_key = os.environ["ANTHROPIC_API_KEY"]

# GOOD: Use .env file with python-dotenv
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ["ANTHROPIC_API_KEY"]
```

### 9.2 Input Validation

```python
import re
from typing import Any

def validate_run_id(run_id: str) -> bool:
    """Validate run ID format."""
    # UUID format
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, run_id))

def sanitize_input(data: Any) -> Any:
    """Sanitize user input."""
    if isinstance(data, str):
        # Remove potential injection patterns
        return data.replace("{{", "").replace("}}", "")
    return data
```

### 9.3 Context Isolation

```python
# Always use ContextFilter before Evaluator
filter_result = context_filter.filter_for_evaluator(
    independent_output,
    context
)

# Never pass private_reasoning to Evaluator
evaluator_input = {
    "subject_context": context,
    "deliverable": deliverable
    # NO private_reasoning
}
```

---

## 10. Documentation

### 10.1 Code Comments

```python
# Good: Explain WHY, not WHAT
# Calculate exponential backoff with jitter to prevent thundering herd
delay = base_delay * (2 ** attempt) + random.uniform(0, 1)

# Bad: Redundant comment
# Increment counter by 1
counter += 1

# Good: Complex algorithm explanation
# Kahn's algorithm for topological sort:
# 1. Find all nodes with no incoming edges
# 2. Remove these nodes and their outgoing edges
# 3. Repeat until graph is empty
```

### 10.2 TODO Comments

```python
# TODO(username): Description of what needs to be done
# TODO(john): Add retry logic for rate limit errors

# FIXME: Known issue that needs fixing
# FIXME: Race condition when concurrent node runs update same context

# HACK: Temporary workaround
# HACK: Using sleep instead of proper rate limiter (Phase 2)
```

---

## 11. Git Conventions

### 11.1 Commit Messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tools

**Examples**:
```
feat(node-execution): add checkpoint resume capability

Implement LangGraph checkpointing for node run recovery.
Checkpoints are stored in SQLite using SqliteSaver.

Closes #123
```

### 11.2 Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<ticket>-<description>` | `feature/DS-123-add-resume` |
| Bugfix | `fix/<ticket>-<description>` | `fix/DS-456-context-leak` |
| Hotfix | `hotfix/<description>` | `hotfix/rate-limit-crash` |

---

## 12. Tools Configuration

### 12.1 pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ["py310"]
include = '\.pyi?$'

[tool.ruff]
line-length = 100
target-version = "py310"
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
    "E501",  # line too long (handled by black)
]

[tool.basedpyright]
pythonVersion = "3.10"
typeCheckingMode = "standard"
reportMissingImports = true
reportMissingTypeStubs = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

### 12.2 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: local
    hooks:
      - id: basedpyright
        name: basedpyright
        entry: basedpyright
        language: system
        types: [python]
```

---

## 13. Quick Reference

### 13.1 Commands

```bash
# Format code
black src/ tests/

# Lint code
ruff check --fix src/

# Type check
basedpyright src/

# Run tests
pytest -v

# Run all checks
pre-commit run --all-files
```

### 13.2 Checklist

Before committing:
- [ ] Code formatted with Black
- [ ] No Ruff warnings
- [ ] Type hints added
- [ ] Docstrings for public APIs
- [ ] Tests written/updated
- [ ] No secrets in code
- [ ] Context isolation verified (if agent code)

---

**Document End**

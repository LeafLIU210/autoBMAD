# AGENTS.md — DocuSwarm Multi-Agent Document Orchestration System

> This file is intended for AI coding agents. It assumes zero prior knowledge of the project.

---

## Project Overview

**DocuSwarm** is a multi-agent document orchestration system that automates BMAD (Breakthrough Method of Agile AI-driven Development) workflows. It orchestrates 5 specialist agents (Analyst, PM, UX Designer, Architect, PO) through a sequential pipeline to produce comprehensive project documentation.

- **Package name**: `docuswarm` (PyPI distribution name)
- **Code namespace**: `autoBMAD.docuswarm`
- **Version**: 1.0.0
- **Python**: >=3.12
- **License**: MIT

The architecture is built on:
- **LangGraph** (0.2.x) — state-machine framework for multi-agent workflows
- **claude-agent-sdk** (0.1.x) — Anthropic Claude Agent SDK
- **Anthropic Claude** (Sonnet, 200K context window) — primary LLM
- **SQLite with WAL mode** — state persistence and checkpointing
- **Dual-Agent Pattern** — Independent Agent (creates deliverables) + Evaluator Agent (reviews with context isolation)

---

## Directory Structure

```
autoBMAD/
├── docuswarm/              # Core DocuSwarm system
│   ├── agents/             # Agent implementations (independent + evaluator)
│   ├── cli/                # Click-based CLI commands and entry point
│   ├── config/             # Configuration module (summary agent config)
│   ├── context/            # Context isolation (filter, audit, validator, permissions)
│   ├── llm/                # LLM integration (session manager, tool filter, response)
│   ├── node_execution/     # Node execution engine (executor, contracts, state, metrics)
│   ├── nodes/              # Node definitions (DualAgentNode, iteration logic)
│   ├── pipeline/           # Pipeline orchestration (LangGraph graph, transitions, quality)
│   ├── prompts/            # Prompt templates (YAML + Markdown + Python loaders)
│   ├── storage/            # State persistence (SQLite checkpoints, state manager, files)
│   ├── templates/          # Node template configurations (per-persona YAML)
│   ├── tools/              # Tool system (deliverables, file tools, search tools, registry)
│   ├── utils/              # Utilities (logging, session IDs)
│   ├── config.py           # Configuration management (env + YAML + defaults)
│   ├── exceptions.py       # Comprehensive exception hierarchy
│   └── public_api.py       # Stable public API facade
├── epic_automation/        # Epic automation system (SM-Dev-QA cycle, quality gates)
└── nodes/                  # Node configurations for BMAD personas
    ├── analyst/
    ├── pm/
    ├── ux/
    ├── architect/
    └── po/

src/                        # Minimal/legacy core (models, config, services, logger, ui)

tests/                      # pytest test suite
├── conftest.py             # Shared fixtures (isolated StateManager, temp nodes, etc.)
└── test_docuswarm_p{0-4}_*.py   # Priority-based test files

docs-test/                  # Test example documents (calc-one-plus-one, bubble-sort)
docs-doc/                   # Project documentation (solution, research, architecture)
claude_docs/                # Development guides (in Chinese)
scripts/                    # Utility scripts (post-commit hooks, etc.)
tools/                      # Standalone tooling scripts
```

---

## Technology Stack

### Production Dependencies
| Package | Purpose |
|---------|---------|
| `langgraph` (0.2.x) | Multi-agent workflow state machine |
| `langchain` / `langchain-core` (0.3.x) | LLM integration framework |
| `claude-agent-sdk` (0.1.x) | Anthropic Claude Agent SDK |
| `pydantic` (>=2.0) | Data validation and settings |
| `PyYAML` (6.0.3) | YAML configuration files |
| `python-dotenv` | `.env` file loading |
| `click` (>=8.1) | CLI framework |
| `rich` (14.2.0) | Terminal output formatting |
| `structlog` (>=24.0) | Structured logging |
| `aiofiles` / `aiosqlite` | Async file I/O and SQLite |

### Development Dependencies
| Package | Purpose |
|---------|---------|
| `pytest` + `pytest-asyncio` + `pytest-cov` + `pytest-timeout` + `pytest-mock` | Testing framework |
| `typeguard` | Runtime type checking |
| `ruff` (>=0.5.0, <0.6.0) | Linter and formatter |
| `basedpyright` (>=1.1.0, <2.0.0) | Static type checker |
| `black` (>=24.0) | Code formatter |
| `pre-commit` | Git pre-commit hooks |

---

## Build and Run Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt        # production only
pip install -r requirements-dev.txt    # production + dev
```

### Running the Application
```bash
# CLI entry point
python -m autoBMAD.docuswarm --help

# Start a new pipeline
python -m autoBMAD.docuswarm start --context docs-test/calc-one-plus-one/calc-context.md

# Check pipeline status
python -m autoBMAD.docuswarm status <pipeline-id>

# Resume an interrupted pipeline
python -m autoBMAD.docuswarm resume <pipeline-id>
```

### Epic Automation
```bash
# Full 5-phase BMAD workflow with quality gates
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

# Skip quality gates (faster iteration)
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality
```

---

## Testing Instructions

### Running Tests
```bash
# Run all tests
pytest -v --tb=short

# Run with coverage (HTML + terminal)
pytest --cov=autoBMAD.docuswarm --cov-report=html --cov-report=term-missing

# Run specific priority tests
pytest -k "p0"        # P0 (critical) tests
pytest -k "p1"        # P1 tests
pytest -m "not slow"  # Exclude slow tests

# Debug a specific test
pytest tests/test_specific.py -s --pdb
```

### Test Configuration (`pyproject.toml`)
- **asyncio_mode**: `auto`
- **timeout**: 300 seconds per test
- **basetemp**: `.pytest-temp` (avoids temp directory permission issues)
- **pythonpath**: `.`, `autoBMAD`

### Test Markers
| Marker | Meaning |
|--------|---------|
| `slow` | Slow tests (deselect with `-m "not slow"`) |
| `integration` | Integration tests |
| `unit` | Unit tests |
| `e2e` | End-to-end tests |
| `agent` | Agent-related tests |
| `pipeline` | Pipeline tests |
| `smoke` | SDK smoke tests |
| `llm` | Tests requiring real LLM API calls |

### Test Conventions
- Test files: `test_*.py`
- Test functions: `test_*`
- Use **AAA pattern**: Arrange → Act → Assert
- Use `pytest.fixture` for test data and resources
- Avoid test files larger than ~1500 lines
- The `conftest.py` provides an `isolated_state_manager` fixture that resets `DatabaseManager` singletons to prevent cross-test contamination.

---

## Code Style Guidelines

### Import Rules
1. **Use absolute imports only** — never relative imports (`from ..module import ...` is forbidden).
2. **Import path must not include the source directory name** — use `autoBMAD.docuswarm.config` not `Project_recorder.services.config`.
3. **Import order**:
   ```python
   # 1. Standard library
   import os
   from pathlib import Path

   # 2. Third-party
   import yaml
   import pytest

   # 3. Local application (absolute)
   from autoBMAD.docuswarm.config import Config
   from autoBMAD.docuswarm.storage.state_manager import StateManager
   ```

### Formatting and Linting
- **Line length**: 100 characters (`tool.ruff.line-length = 100`)
- **Target Python**: 3.12 (`tool.ruff.target-version = "py312"`)
- **Ruff rules**: E, W, F, I, B, C4, UP
- **Ignored rules**: E501 (handled by formatter), B008 (function calls in defaults)

### Quality Gate Commands
```bash
# Type checking
basedpyright autoBMAD/

# Linting
ruff check autoBMAD/

# Auto-fix issues
ruff check --fix autoBMAD/

# Formatting
ruff format autoBMAD/

# Pre-commit (all checks)
pre-commit run --all-files
```

### Naming Conventions
- **Variables**: `snake_case`, descriptive (`user_count`, not `x`)
- **Functions**: verb-first, descriptive (`calculate_total_price`, not `process`)
- **Classes**: `PascalCase`

### Type Checking
- All public functions and methods **must** have return type annotations.
- Function parameters should have type annotations.
- `basedpyright` is configured with many strict checks **disabled** in `pyproject.toml` (e.g., `reportMissingImports`, `reportAny`, `reportUnknownVariableType`). Do not assume the project enforces full strict mode.

### Encoding
- All Python source files use **UTF-8**.
- Use human-readable text directly (e.g., `"欢迎"`), never Unicode escape sequences (`\u6b22\u8fce`).

---

## Development Principles

The project follows four core principles (documented in `claude_docs/core_principles.md`):

1. **Occam's Razor** — prefer the simplest solution with the fewest assumptions.
2. **DRY** — eliminate repeated logic by extracting functions/classes.
3. **KISS** — one function, one responsibility; use guard clauses to flatten nesting.
4. **YAGNI** — implement only what is explicitly needed now.

### AI Agent Workflow
When contributing code, follow the three-phase workflow from `claude_docs/ai_workflow.md`:
1. **Analyze** — understand requirements, search all relevant code, identify root causes.
2. **Plan** — list changed files, eliminate duplication, ensure DRY.
3. **Execute** — implement strictly according to plan, then run type checks.

---

## Configuration

### Environment Variables (`.env` file)
Copy `.env.example` to `.env` and set:

```bash
# REQUIRED
ANTHROPIC_API_KEY=your_key_here

# Optional
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
DOCUSWARM_DB_PATH=docuswarm.db
DOCUSWARM_OUTPUT_DIR=output
DOCUSWARM_LOG_LEVEL=INFO
DOCUSWARM_MAX_ITERATIONS=100
DOCUSWARM_AGENT_TIMEOUT=7200
```

### YAML Configuration
`autoBMAD/docuswarm/config/summary_agent.yaml` provides agent-specific defaults. Precedence:
**Environment Variables > `.env` file > YAML config > defaults**

### `pyproject.toml` Key Sections
- `[project]` — metadata, dependencies, entry points
- `[project.optional-dependencies] dev` — dev tools
- `[tool.pytest.ini_options]` — test configuration
- `[tool.ruff]` / `[tool.ruff.lint]` — linting rules
- `[tool.basedpyright]` — type checker settings (relaxed, not strict)
- `[tool.coverage.run]` / `[tool.coverage.report]` — coverage settings

---

## Security Considerations

- **API Key handling**: `ANTHROPIC_API_KEY` is **never** read from YAML config for security. It must come from environment variables or the `.env` file.
- **Path traversal protection**: File tools enforce allowed-directory boundaries (`PathNotAllowedError`).
- **Context isolation**: The architecture enforces a three-layer defense (runtime access control, prompt template isolation, message filtering). Violations raise `ContextIsolationError`.
- **SQLite WAL mode**: Enabled for safe concurrent access and crash recovery.
- **Sensitive log redaction**: The logging utility in `autoBMAD/docuswarm/utils/logging.py` redacts API keys from log output.

---

## Key Architectural Patterns

### Dual-Agent Node
Each BMAD phase runs as a `DualAgentNode`:
1. **Independent Agent** — creates deliverables and generates clarifying questions.
2. **Evaluator Agent** — reviews output with context isolation and provides a verdict.

### State Management
- `StateManager` + `DatabaseManager` (SQLite) handle pipeline state.
- LangGraph checkpointing enables resume after interruption.
- Optimistic locking prevents concurrent pipeline corruption.

### Tool System
- Tools are registered in `ToolRegistry`.
- SDK-native Tool Use Block pattern is used.
- Tool results are wrapped in `ToolResult` for uniform handling.

---

## Notes for Agents

- The project has **no CI/CD pipelines** (no `.github/workflows/`). All quality checks run locally.
- There is a **legacy `src/` directory** with minimal code (`src/core/models.py`, etc.). Most active development happens under `autoBMAD/docuswarm/` and `autoBMAD/epic_automation/`.
- The `autoBMAD/epic_automation/` directory contains a separate but related system for epic-level BMAD workflow automation. It has its own agents, controllers, and state management.
- When modifying code, always check if there are corresponding tests in `tests/` following the `test_docuswarm_p{N}_*.py` naming convention.
- The `__init__.py` in `autoBMAD/docuswarm/` uses **lazy imports** via `__getattr__` to avoid `ImportError` during partial implementations.

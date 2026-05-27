# autoBMAD Epic Automation System

**Version**: 3.2  
**Status**: Production Ready

A comprehensive automation system for the BMAD (Breakthrough Method of Agile AI-driven Development) workflow. This tool processes epic markdown files through a complete 5-phase workflow with state-driven execution, quality gates, and test automation.

---

## Overview

autoBMAD Epic Automation is a self-contained Python automation engine that enables teams to quickly set up and use the BMAD methodology in their projects. It features a five-layer architecture with Controllers, Agents, Core infrastructure, and persistent State management.

### System Architecture

- **Five-Layer Architecture**: Epic Driver -> Controllers -> Agents -> Core -> State & Logging
- **State-Driven Workflow**: Story status from markdown drives execution decisions
- **Controller Pattern**: Specialized controllers for SM, DevQA, Quality Gates, and Pytest
- **SQLite Persistence**: Progress tracking with WAL mode and optimistic locking
- **Dual-Write Logging**: Console and file logging with structured output

### Key Features

- Complete 5-Phase Workflow: SM-Dev-QA cycle followed by quality gates and test automation
- AI-Powered Story Creation: SM Agent uses Claude Agent SDK to create stories from epic documents
- Claude Agent SDK Integration: Direct SDK integration with `permission_mode="bypassPermissions"`
- Quality Gates: Basedpyright type checking and Ruff linting with auto-fix capabilities
- Test Automation: Pytest execution with retry logic for persistent failures
- CLI Interface: Subcommand-based interface (`run-epic`, `run-quality`)
- Retry Logic: Configurable retry attempts for failed stories (default: 5 iterations)
- State Persistence: SQLite with WAL mode for crash recovery and resume
- Portable: Self-contained solution requiring only Python and the Claude SDK

---

## Quick Start

### Prerequisites

- Python 3.12+
- `ANTHROPIC_API_KEY` environment variable (or `.env` file)

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set:
#   ANTHROPIC_API_KEY=your_api_key_here
#   EPIC_SOURCE_DIR=src        # Source directory for quality checks
#   EPIC_TEST_DIR=tests        # Test directory for pytest

# Verify installation
python -c "import claude_agent_sdk; print('Claude Agent SDK ready')"
basedpyright --version
ruff --version
pytest --version
```

### Basic Usage

#### Using the Venv Wrapper Script (Recommended)

The `run_epic_with_venv.sh` script automatically handles virtual environment setup and dependency installation:

```bash
# Full workflow with automatic dependency management
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --verbose

# With log file output
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --verbose 2>&1 | tee autoBMAD/epic_automation/logs/epic_run.log

# Skip quality gates for faster development
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --skip-quality --verbose

# Custom directories and options
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md \
  --source-dir src --test-dir tests --max-iterations 5 --verbose

# Show help
autoBMAD/epic_automation/run_epic_with_venv.sh --help
```

#### Manual Execution

```bash
# Activate virtual environment
source .venv/bin/activate

# Full workflow (SM-Dev-QA + Quality Gates + Tests)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --verbose

# Or use module syntax
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-epic docs/epics/my-epic.md --verbose

# Skip quality gates
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --skip-quality --verbose

# Skip test automation
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --skip-tests --verbose

# Skip both quality gates and tests (fastest)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --skip-quality --skip-tests --verbose
```

#### Standalone Quality Gates

```bash
# Run quality gates only (Ruff + BasedPyright + Pytest)
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-quality --verbose

# Skip tests, run only code quality checks
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-quality --skip-tests

# Skip static checks, run only pytest
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-quality --skip-quality

# Custom directories
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-quality \
  --source-dir autoBMAD/epic_automation --test-dir tests/epic_automation

# With log file
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver run-quality --verbose --log-file
```

---

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `run-epic <epic_path>` | Run full epic workflow (SM-Dev-QA + Quality Gates) |
| `run-quality` | Run quality gates only (Ruff, BasedPyright, Pytest) |

Backward-compatible mode: passing a positional argument without a subcommand is automatically treated as `run-epic`.

### run-epic Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `epic_path` | positional | required | Path to epic markdown file |
| `--max-iterations` | int | 5 | Maximum retry attempts for failed stories |
| `--retry-failed` | flag | False | Enable automatic retry of failed stories |
| `--verbose` | flag | False | Enable detailed logging output |
| `--concurrent` | flag | False | Process stories in parallel (experimental) |
| `--no-claude` | flag | False | Disable Claude Code CLI (simulation mode) |
| `--source-dir` | str | `$EPIC_SOURCE_DIR` or "src" | Source code directory for QA checks |
| `--test-dir` | str | `$EPIC_TEST_DIR` or "tests" | Test directory for QA checks |
| `--skip-quality` | flag | False | Skip quality gates (ruff/basedpyright) |
| `--skip-tests` | flag | False | Skip test automation (pytest) |
| `--log-file` | flag | False | Create timestamped log file |

### run-quality Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--source-dir` | str | `$EPIC_SOURCE_DIR` or "src" | Source code directory |
| `--test-dir` | str | `$EPIC_TEST_DIR` or "tests" | Test directory |
| `--epic-id` | str | "standalone-quality" | Identifier for error summary JSON |
| `--skip-quality` | flag | False | Skip ruff and basedpyright checks |
| `--skip-tests` | flag | False | Skip pytest execution |
| `--max-cycles` | int | 5 | Maximum fix cycles |
| `--verbose` | flag | False | Enable verbose logging |
| `--log-file` | flag | False | Create timestamped log file |

---

## Workflow Phases

The system executes epics through 5 distinct phases:

```
Phase 1: SM-Dev-QA Cycle
  - Story Creation (SM Agent)
  - Implementation (Dev Agent)
  - Validation (QA Agent)
         |
Phase 2: Quality Gates
  - Ruff Linting with Auto-fix
  - BasedPyright Type Checking
  - Max 5 fix cycles
         |
Phase 3: Test Automation
  - Pytest Test Execution
  - Batch processing for efficiency
  - Max 5 retry cycles
         |
Phase 4: Orchestration
  - Epic Driver manages complete workflow
  - Phase-gated execution
  - Progress tracking (SQLite)
         |
Phase 5: Documentation & Reporting
  - Error summary JSON reports
  - Quality gate result logs
```

---

## Configuration

### Environment Variables (.env)

The tool supports configuration via `.env` file (loaded with `python-dotenv`).

| Variable | Default | Description |
|----------|---------|-------------|
| `EPIC_SOURCE_DIR` | `"src"` | Source code directory for quality checks |
| `EPIC_TEST_DIR` | `"tests"` | Test directory for pytest execution |
| `ANTHROPIC_API_KEY` | (required) | Claude Agent SDK API key |

**Priority Order:**
1. Command-line arguments (highest)
2. Environment variables / `.env` file
3. Default values (lowest)

### Task Guidance Files

The `.bmad-core/tasks/` directory contains task guidance files that customize agent behavior:

| File | Agent | Purpose |
|------|-------|---------|
| `create-next-story.md` | SM Agent | Story creation guidance |
| `develop-story.md` | Dev Agent | Development implementation standards |
| `review-story.md` | QA Agent | Code review and quality checklist |

---

## Architecture

### Five-Layer Architecture

```
+-------------------------------------+
|   Epic Driver (Orchestration)       |  <- Entry point + workflow coordination
+-------------------------------------+
|   Controllers (Process Control)     |  <- Business workflow orchestration
+-------------------------------------+
|   Agents (Business Logic)           |  <- Core business operations
+-------------------------------------+
|   Core (Infrastructure)             |  <- SDK executor, cancellation manager
+-------------------------------------+
|   State & Logging                   |  <- StateManager, LogManager, Database
+-------------------------------------+
```

### Directory Structure

```
autoBMAD/epic_automation/
├── epic_driver.py              # Main orchestrator and CLI entry point
├── run_epic_with_venv.sh       # Venv wrapper script
├── state_manager.py            # State persistence (SQLite with WAL mode)
├── sdk_wrapper.py              # SafeClaudeSDK wrapper
├── log_manager.py              # Dual-write logging system
├── init_db.py                  # Database initialization
├── doc_parser.py               # Epic/story document parsing
├── spec_state_manager.py       # Specification state tracking
├── .env.example                # Environment variable template
│
├── controllers/                # Workflow Controllers
│   ├── base_controller.py             # Base controller class
│   ├── sm_controller.py               # Story Management coordination
│   ├── devqa_controller.py            # Dev-QA cycle coordination
│   ├── quality_check_controller.py    # Quality gate controller
│   ├── quality_controller.py          # Quality orchestration
│   └── pytest_controller.py           # Test automation controller
│
├── agents/                     # Business Logic Agents
│   ├── base_agent.py                  # Base agent class
│   ├── sm_agent.py                    # Story creation from epics
│   ├── dev_agent.py                   # Development implementation
│   ├── qa_agent.py                    # Quality assurance validation
│   ├── state_agent.py                 # Status parsing and state management
│   ├── status_update_agent.py         # Story status updates
│   ├── quality_agents.py             # Ruff, BasedPyright, Pytest agents
│   ├── pytest_batch_executor.py       # Pytest batch execution
│   ├── config.py                      # Agent configuration
│   └── sdk_helper.py                  # SDK utilities
│
├── core/                       # Core Infrastructure
│   ├── sdk_executor.py                # Async SDK executor
│   ├── sdk_result.py                  # SDK result types
│   └── cancellation_manager.py        # Cancellation handling
│
├── monitoring/                 # Performance Monitoring
│   └── resource_monitor.py            # Resource usage monitoring
│
├── reports/                    # Quality Reports
├── architecture/               # Architecture Documentation
└── logs/                       # Log Files (auto-created)
```

### Agent Roles

| Agent | File | Responsibility |
|-------|------|----------------|
| SM Agent | `agents/sm_agent.py` | Epic analysis, AI story creation via Claude SDK |
| Dev Agent | `agents/dev_agent.py` | Code implementation, test writing |
| QA Agent | `agents/qa_agent.py` | Code review, acceptance validation |
| State Agent | `agents/state_agent.py` | Status parsing from markdown, state mapping |
| Status Update Agent | `agents/status_update_agent.py` | Story status transitions |
| Quality Agents | `agents/quality_agents.py` | Ruff, BasedPyright, Pytest execution |
| Pytest Batch Executor | `agents/pytest_batch_executor.py` | Parallel test execution |

### State-Driven Workflow

For each story, the state drives execution:

- **Draft / Ready for SM**: SMController creates the story
- **Ready for Development**: DevQaController starts Dev-QA cycle
- **In Progress**: DevAgent implements the story
- **Ready for Review**: QAAgent validates implementation
- **Ready for Done / Done**: Triggers quality gates and test automation

---

## Dependencies

### Required (Production)

| Package | Purpose |
|---------|---------|
| `claude-agent-sdk>=0.1.0,<0.2.0` | AI agent functionality (SM, Dev, QA agents) |
| `python-dotenv>=1.0.0,<2.0.0` | `.env` file loading |
| `structlog>=24.0.0,<25.0.0` | Structured logging |

### Quality Gate Tools (Development)

| Package | Purpose |
|---------|---------|
| `basedpyright>=1.1.0,<2.0.0` | Advanced type checking |
| `ruff>=0.5.0,<0.6.0` | Fast Python linter and formatter |
| `pytest>=8.0.0,<9.0.0` | Testing framework |

### Built-in (No Installation Required)

- `sqlite3`: State persistence with WAL mode
- `asyncio`: Async execution framework
- `pathlib`: Path manipulation
- `argparse`: CLI argument parsing

### Installation

```bash
# Install all dependencies (recommended)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or install epic_automation dependencies individually
pip install claude-agent-sdk python-dotenv structlog
pip install basedpyright ruff pytest
```

### Graceful Fallback

If quality gate tools are not available, the system will:
1. Log a warning about missing tools
2. Continue with reduced QA capabilities
3. Allow the workflow to proceed without quality checks

---

## Venv Wrapper Script

The `run_epic_with_venv.sh` script provides automatic environment management:

- Zero-Config Setup: Automatically creates virtual environment if needed
- Smart Dependency Management: Installs/updates dependencies from requirements.txt
- Path Auto-Detection: Finds project root from script location
- PYTHONPATH: Set automatically
- Full Compatibility: Supports all `epic_driver.py` command-line options

### Usage

```bash
# Basic usage
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --verbose

# With log capture
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --verbose 2>&1 | tee logs/epic.log

# Skip quality gates
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --skip-quality --verbose

# Show help
autoBMAD/epic_automation/run_epic_with_venv.sh --help
```

---

## Quality Gates

Quality gates ensure code quality after the SM-Dev-QA cycle completes.

### Ruff Linting

- Fast Python linting with auto-fix capabilities
- Covers PEP 8, complexity, imports, and more
- Automatically fixes fixable issues

### BasedPyright Type Checking

- Static type checking to catch type-related errors
- Configured via `pyproject.toml`

### Pytest Execution

- Runs test suite with batch processing
- Detailed reporting with failure analysis
- Configurable retry cycles (default: 5)

---

## Troubleshooting

### Common Issues

#### Epic file not found

```
ERROR - Epic file not found: docs/epics/my-epic.md
```

Verify the file path is correct and use absolute path if needed.

#### Module import error

```
ERROR - Failed to import agent classes: No module named 'autoBMAD'
```

Set PYTHONPATH correctly:

```bash
export PYTHONPATH=.
# Or use absolute path
export PYTHONPATH=/path/to/your/project
```

#### Quality gate tools not found

```
WARNING - Quality gate tools not available
```

Install the tools or use skip flags:

```bash
pip install basedpyright ruff pytest

# Or bypass with flags
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --skip-quality --skip-tests
```

#### Database errors or state corruption

```bash
# Check database integrity
sqlite3 progress.db "PRAGMA integrity_check;"

# Reset state (backup first)
cp progress.db progress.db.backup
rm progress.db
# System will create new database on next run
```

#### SDK timeout or connection errors

```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check SDK version
pip show claude-agent-sdk

# Enable debug logging
export ANTHROPIC_LOG=debug
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --verbose
```

### Debug Mode

```bash
# Maximum verbosity with single iteration
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/my-epic.md --verbose --max-iterations 1
```

---

## FAQ

**Q: Can I run the tool without internet?**  
A: No, internet access is required for the Claude Agent SDK.

**Q: Can I pause and resume processing?**  
A: Yes, progress is persisted in `progress.db`. Stop with Ctrl+C and run the same command to resume.

**Q: Is it safe to run multiple times on the same epic?**  
A: Yes, the tool is idempotent. It tracks state and skips completed stories.

**Q: How do I specify custom source and test directories?**  
A: Use `--source-dir` and `--test-dir` flags, or set `EPIC_SOURCE_DIR` and `EPIC_TEST_DIR` in `.env`.

**Q: What happens if the process crashes?**  
A: SQLite WAL mode ensures state persistence. Restart the process to resume from the last saved state.

**Q: Where are logs stored?**  
A: Console output (always) + `autoBMAD/epic_automation/logs/` (if `--log-file` is enabled).

**Q: What Python version is required?**  
A: Python 3.12 or higher.

---

## Version History

### Version 3.2 (2026-02-17)
- `run_epic_with_venv.sh` bash wrapper for automatic venv management
- Automatic virtual environment creation and activation
- Automatic dependency installation from requirements.txt
- Project root auto-detection from script location
- Migrated from scripts/ to epic_automation/ directory

### Version 3.1 (2026-01-23)
- `run-quality` subcommand for standalone quality gates
- CLI subcommand architecture (`run-epic`, `run-quality`)
- Backward compatible with positional epic_path argument

### Version 3.0 (2026-01-14)
- Five-layer architecture with Controllers pattern
- State-driven workflow execution
- Enhanced quality gates with error reporting
- Batch test execution support
- SQLite with WAL mode and optimistic locking

### Version 2.0
- Claude Agent SDK integration
- Async story creation
- Removed hardcoded story templates

### Version 1.0
- Initial release
- Basic SM-Dev-QA cycle

---

**Built with**: Python 3.12+ | Claude Agent SDK | SQLite | structlog  
**License**: Part of the BMAD methodology

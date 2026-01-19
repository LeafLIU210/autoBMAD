---
name: autoBMAD-epic-automation
description: "Complete 5-phase BMAD development workflow automation with SM-Dev-QA cycle, quality gates (BasedPyright, Ruff), and test automation (Pytest). Use when processing epic documents through AI-powered story creation, implementation, validation, and quality assurance. Located at autoBMAD/epic_automation/epic_driver.py"
---

# autoBMAD Epic Automation

## Quick Start

Run complete 5-phase workflow:
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

## Workflow Phases

1. **SM-Dev-QA Cycle**: AI-driven story creation, implementation, and validation
2. **Quality Gates**: Type checking (BasedPyright) + linting (Ruff) with auto-fix
3. **Test Automation**: Pytest execution with retry logic (max 5 attempts)
4. **State Management**: SQLite persistence with WAL mode and crash recovery
5. **Reporting**: Dual-write logging (console + file) with detailed metrics

## CLI Options

### Required
- `epic_path`: Path to epic markdown file

### Optional Flags
- `--max-iterations N`: Retry attempts (default: 3)
- `--verbose`: Detailed logging
- `--source-dir DIR`: Source code dir (default: "src")
- `--test-dir DIR`: Test directory (default: "tests")

### Skip Options
- `--skip-quality`: Bypass quality gates (BasedPyright, Ruff)
- `--skip-tests`: Bypass test automation (Pytest)

## Usage Patterns

### Full Workflow
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```
Process complete 5-phase workflow: SM-Dev-QA + Quality Gates + Tests

### Fast Development (Skip Quality)
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --verbose
```
Use for prototyping, experimental code, or rapid iteration

### Quick Validation (Skip Tests)
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests --verbose
```
Use for code quality validation, type checking, quick linting feedback

### Initial Development (Skip Both)
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests --verbose
```
Use for initial story implementation, rapid prototyping, core functionality first

## Environment Setup

### Dependencies
```bash
pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio
```

### Environment Variables
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/macOS
export ANTHROPIC_API_KEY="your_api_key_here"
```

## Architecture

### Five-Layer Architecture
1. **Epic Driver**: Orchestration and workflow coordination
2. **Controllers**: Business workflow orchestration (SM, DevQA, Quality, Pytest)
3. **Agents**: Core business logic (SM, Dev, QA, State, Quality agents)
4. **Core**: Infrastructure (SDK executor, cancellation manager)
5. **State & Logging**: Persistence (SQLite) and monitoring (LogManager)

### Agent Roles
- **SM Agent**: AI story creation from epics using Claude SDK
- **Dev Agent**: Implementation and test writing
- **QA Agent**: Code review and validation
- **State Agent**: Status parsing and state management
- **Quality Agents**: Ruff linting, BasedPyright type checking, Pytest execution

## State Management

### Database: progress.db (SQLite with WAL)
- Tracks story execution status
- Phase completion tracking
- Iteration counts and timestamps
- Error history and recovery
- Optimistic locking for concurrency

### State-Driven Execution
- **Draft/Ready for SM**: SMController creates stories
- **Ready for Development**: DevQaController starts Dev-QA cycle
- **In Progress**: DevAgent implements
- **Ready for Review**: QAAgent validates
- **Ready for Done**: Triggers quality gates and tests

## Quality Gates

### Ruff Linting
- Auto-fixes fixable issues
- Checks PEP 8, complexity, imports
- Max 3 retry cycles
- Errors saved to `autoBMAD/epic_automation/errors/ruff_*.json`

### BasedPyright Type Checking
- Static type checking
- Max 3 retry cycles
- Agent attempts fixes via SDK
- Errors saved to `autoBMAD/epic_automation/errors/basedpyright_*.json`

### Quality Status
- **PASS**: All requirements met
- **CONCERNS**: Non-critical issues found
- **FAIL**: Critical issues found (must fix)
- **WAIVED**: Issues accepted with reason

## Test Automation

### Pytest Execution
- Runs all tests in test suite
- Batch execution for efficiency
- Max 5 retry cycles
- Debugpy integration for persistent failures

### Retry Logic
- Quality gates: 3 attempts
- Tests: 5 attempts
- Automatic backoff between retries
- Persistent failures trigger debug mode

## Epic Format

```markdown
# Epic: Core Algorithm Foundation

## Stories
- [Story 001: Basic Sort Implementation](docs/stories/story-001.md)
- [Story 002: Performance Optimization](docs/stories/story-002.md)
- [Story 003: Comprehensive Test Suite](docs/stories/story-003.md)
```

## Troubleshooting

### Epic file not found
- Verify file path is correct
- Use absolute path if relative doesn't work

### Tasks directory missing
```bash
mkdir -p .bmad-core/tasks
# Add task guidance files (create-next-story.md, develop-story.md, review-story.md)
```

### Quality tools not found
```bash
# Install all tools
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0

# Or skip quality gates
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests
```

### Import errors
```bash
# Set PYTHONPATH
$env:PYTHONPATH="."  # Windows PowerShell
export PYTHONPATH=.  # Linux/macOS
```

### Database corruption
```bash
# Backup and reset
cp progress.db progress.db.backup
rm progress.db
# System creates new database on next run
```

## Best Practices

1. **Idempotent**: Safe to run multiple times on same epic
2. **State Persistence**: Progress saved automatically, supports interruption recovery
3. **Verbose Logging**: Use `--verbose` for debugging
4. **Task Guidance**: Customize agent behavior via `.bmad-core/tasks/` files
5. **Quality First**: Use quality gates before production deployment

## Output Files

- `progress.db`: SQLite state database
- `autoBMAD/epic_automation/logs/`: Timestamped log files
- `autoBMAD/epic_automation/errors/`: Quality gate error reports (JSON)

## Debug Mode

```bash
# Max verbosity, single iteration for quick feedback
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose --max-iterations 1

# Enable SDK debug logging
$env:ANTHROPIC_LOG="debug"
```

## Key Features

- **Claude Agent SDK Integration**: Direct SDK calls with `permission_mode="bypassPermissions"`
- **Async Execution**: Non-blocking story generation and processing
- **Smart Parsing**: Regex + AI-based story extraction from epics
- **Batch Processing**: Efficient parallel test execution
- **Graceful Fallback**: Continues without quality tools (marked as WAIVED)
- **Portable**: Self-contained, copy folder to any project
- **No Complex Setup**: Requires only Python + Claude SDK

This skill encapsulates a production-ready BMAD automation system providing end-to-end development workflow from story creation to deployment.
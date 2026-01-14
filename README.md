# autoBMAD Epic Automation System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**autoBMAD** (Breakthrough Method of Agile AI-driven Development) is an intelligent automation system that processes epics through a complete 5-phase workflow with integrated code quality gates and test automation.

## 🎯 Project Overview

**Note:** This project was originally created as a development template for Python Qt applications. However, its primary and most powerful feature is the **autoBMAD workflow system**. 

The design relies on:
- **[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)** - AI-powered agent orchestration
- **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** - Agile AI-driven development methodology

The system targets **fully automated development** of epic documents created by Product Owners (PO), including:
- **SM-Dev-QA BMAD development cycle** - Story creation, implementation, and validation
- **Quality gate checks and auto-fixing** - Type checking, linting, and code quality assurance
- **Test automation** - Comprehensive test execution and reporting

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pytQt_template
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -m autoBMAD.epic_automation.epic_driver --help
   ```

### Basic Usage

Process an epic through the complete workflow:

```bash
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md
```

Skip quality gates for faster iteration:

```bash
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality
```

Skip test automation:

```bash
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests
```

## 📊 Complete Workflow

The autoBMAD system processes epics through **5 integrated phases**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Epic Processing                         │
│                                                              │
│  Phase 1: SM-Dev-QA Cycle                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Story Master │→ │   Developer  │→ │ QA Validator │     │
│  │   (Create)   │  │ (Implement)  │  │  (Review)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │                    │              │           │
│           └────────────────────┴──────────────┘           │
│                           ↓                                 │
│  Phase 2: Quality Gates                                      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ BasedPyRight │→ │    Ruff      │                        │
│  │   (Types)    │  │  (Lint/AutoFix)                      │
│  └──────────────┘  └──────────────┘                        │
│                           ↓                                 │
│  Phase 3: Test Automation                                   │
│  ┌──────────────────────────────────────┐                  │
│  │           Pytest (Execute)           │                  │
│  └──────────────────────────────────────┘                  │
│                           ↓                                 │
│  Phase 4: Orchestration                                    │
│  ┌──────────────────────────────────────┐                  │
│  │      Epic Driver (Manage All)        │                  │
│  └──────────────────────────────────────┘                  │
│                           ↓                                 │
│  Phase 5: Documentation & Integration                      │
│  ┌──────────────────────────────────────┐                  │
│  │   Auto-Doc + Integration Testing     │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Phase Details

**Phase 1: SM-Dev-QA Cycle**
- Story creation by Story Master agent
- Implementation by Developer agent
- Validation by QA agent
- Automatic retry on failures (up to 3 attempts)

**Phase 2: Quality Gates**
- **BasedPyRight**: Static type checking
- **Ruff**: Fast linting with automatic fixes
- Maximum 3 retry attempts
- Blocks progression if quality gates fail

**Phase 3: Test Automation**
- **Pytest**: Comprehensive test execution
- Maximum 5 retry attempts
- Detailed test reports
- Automatic retry logic for failed tests

**Phase 4: Orchestration**
- Manages complete workflow execution
- Tracks progress across all phases
- Handles phase-gated execution
- Reports status in real-time

**Phase 5: Documentation & Integration**
- Auto-generates documentation
- Runs integration tests
- Validates complete workflow
- Ensures system consistency

## 🔧 Quality Gates

Quality gates add automated code quality validation to epic processing. After the Dev-QA cycle completes successfully, the system automatically runs three sequential quality agents:

1. **Ruff Agent** - Code linting and auto-fix
2. **BasedPyright Agent** - Type checking and validation
3. **Pytest Agent** - Test automation with debugging

### Quality Gates Workflow

Quality gates execute automatically after QA completion:

```bash
# Process epic with full quality gates
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Skip quality gates for faster iteration
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality

# Skip only pytest execution
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests
```

**Quality Gate Sequence:**
```
Phase 1: SM-Dev-QA Cycle
         ↓
Phase 2: Quality Gates (Ruff → BasedPyright → Pytest)
         ↓
Phase 3: Documentation & Integration
```

**Important: Cancel Scope Safety**
- Quality gates use SDK max_turns=150 (no external timeouts)
- Cancel scope errors are prevented through simplified timeout handling
- See `docs/evaluation/cancel-scope-error-analysis.md` for technical details

### Ruff Agent

Ruff provides fast linting with automatic fix capabilities:

```bash
# Run linting with auto-fix
ruff check --fix src/

# Check only (no auto-fix)
ruff check src/

# Format code
ruff format src/
```

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| `F401` (unused import) | Remove unused imports or use `# noqa` |
| `E501` (line too long) | Break long lines or increase limit |
| `B007` (loop control) | Use meaningful variable names |

**Auto-fix Examples:**
```bash
# Fix all auto-fixable issues
ruff check --fix src/

# Format code to Ruff standards
ruff format src/
```

### BasedPyright Agent

BasedPyright provides static type checking for Python code:

```bash
# Run type checking manually
basedpyright src/

# Configure in pyproject.toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
```

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| `reportMissingImports` | Add `# type: ignore` or fix imports |
| `reportOptionalMemberAccess` | Add None checks |
| `reportGeneralTypeIssues` | Fix type annotations |

**Type Hinting Examples:**
```python
# Function parameters and return types
def process_data(data: str) -> str:
    return data.strip()

# List type annotation
def process_list(items: list[str]) -> list[str]:
    return [item.strip() for item in items]

# Optional type annotation
def get_user(user_id: int) -> str | None:
    return db.get_user(user_id)
```

### Pytest Agent

Pytest executes comprehensive test suites with automatic retry logic:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run GUI tests
pytest tests/gui/ -v
```

**Test Features:**
- Automatic retry for failed tests (max 5 attempts)
- Detailed test reports and failure analysis
- Batch execution for efficiency

### Quality Agents Configuration

Quality agents can be configured via CLI flags:

```bash
# Skip all quality gates
python -m autoBMAD.epic_automation.epic_driver my-epic.md --skip-quality

# Skip only tests
python -m autoBMAD.epic_automation.epic_driver my-epic.md --skip-tests

# Custom source and test directories
python -m autoBMAD.epic_automation.epic_driver my-epic.md --source-dir src --test-dir tests

# Verbose quality gate output
python -m autoBMAD.epic_automation.epic_driver my-epic.md --verbose
```

**Flag Combinations:**
```bash
# Development mode - skip quality gates, run tests
python -m autoBMAD.epic_automation.epic_driver my-epic.md --skip-quality

# Quick validation - skip tests, run quality gates
python -m autoBMAD.epic_automation.epic_driver my-epic.md --skip-tests

# Full pipeline - all quality gates and tests
python -m autoBMAD.epic_automation.epic_driver my-epic.md
```

### Troubleshooting Quality Gates

For detailed troubleshooting, see:
- [Quality Gates Troubleshooting](docs/troubleshooting/quality-gates.md)
- [Cancel Scope Error Analysis](docs/evaluation/cancel-scope-error-analysis.md)

**Quick Fix Commands:**
```bash
# Check quality gate status
python -m autoBMAD.epic_automation.epic_driver my-epic.md --verbose

# Fix ruff issues automatically
ruff check --fix src/

# Type check with detailed output
basedpyright src/ --output-format=json

# Run tests with verbose output
pytest tests/ -v --tb=long
```

## 🧪 Test Automation

Test automation executes comprehensive test suites after quality gates pass.

### Pytest Execution

Pytest runs all tests in the `tests/` directory:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_epic_driver.py

# Run with coverage
pytest --cov=src

# Run GUI tests
pytest tests/gui/ -v
```

### CLI Test Options

```bash
# Skip test automation
python epic_driver.py my-epic.md --skip-tests

# Custom test directory
python epic_driver.py my-epic.md --test-dir custom_tests/

# Run specific test
python epic_driver.py my-epic.md --test-pattern test_epic_*
```

## ⚙️ Configuration

Configuration is managed through `pyproject.toml` and `requirements.txt`.

### pyproject.toml

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
reportMissingImports = true
reportOptionalMemberAccess = true

[tool.ruff]
line-length = 88
target-version = "py38"
select = ["E", "F", "B", "I"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--verbose --tb=short"
```

### requirements.txt

Core dependencies:

```txt
# Quality Gate Tools
basedpyright>=1.1.0
ruff>=0.1.0

# Test Automation
pytest>=7.0.0
pytest-cov>=4.0.0

# Core System
pyside6>=6.0.0
claude-agent-sdk>=0.1.0
asyncio
sqlite3
```

### Environment Variables

```bash
# Anthropic API (for Claude Agent SDK)
export ANTHROPIC_API_KEY=your_api_key

# Performance Settings
export MAX_ITERATIONS=3
export CONCURRENT_PROCESSING=false
```

## 📝 Examples

### Example Epic with Quality Gates

See `docs/examples/example-epic-with-quality-gates.md` for a complete example.

**Example Epic Structure:**

```markdown
# Epic: Implement Quality Gate System

## Stories

### Story 1: Add Type Hints
**As a** developer,
**I want to** add type hints to all functions,
**So that** BasedPyRight can validate my code.

**Acceptance Criteria**:
- [ ] All functions have type hints
- [ ] BasedPyRight validation passes
- [ ] Tests pass with type hints
```

### Custom Configuration Examples

**Minimal Epic (Skip Quality Gates):**

```bash
python epic_driver.py simple-epic.md --skip-quality --skip-tests
```

**Full Testing Epic:**

```bash
python epic_driver.py full-epic.md --verbose --concurrent
```

**Development Mode:**

```bash
python epic_driver.py dev-epic.md --skip-quality --test-dir tests/ --verbose
```

## 🎯 CLI Reference

```bash
python -m autoBMAD.epic_automation.epic_driver [OPTIONS] EPIC_PATH

Positional Arguments:
  EPIC_PATH              Path to epic markdown file

Options:
  --source-dir DIR       Source code directory for quality gates (default: src)
  --test-dir DIR         Test directory for pytest execution (default: tests)
  --skip-quality         Skip quality gates (Ruff and BasedPyright)
  --skip-tests           Skip pytest execution
  --max-iterations N     Max retry attempts for Dev-QA cycle (default: 3)
  --retry-failed         Enable automatic retry of failed stories
  --verbose              Enable detailed logging output
  --concurrent           Enable concurrent story processing (experimental)
  --no-claude            Disable Claude Code CLI integration
  --help                 Show this message and exit
```

**Quality Gate Flags:**

| Flag | Description | Example |
|------|-------------|---------|
| `--skip-quality` | Skip Ruff and BasedPyright checks | `python epic_driver.py my-epic.md --skip-quality` |
| `--skip-tests` | Skip pytest execution | `python epic_driver.py my-epic.md --skip-tests` |
| `--source-dir DIR` | Specify source directory for quality checks | `python epic_driver.py my-epic.md --source-dir src` |
| `--test-dir DIR` | Specify test directory for pytest | `python epic_driver.py my-epic.md --test-dir tests` |

**Common Usage Patterns:**

```bash
# Full pipeline with quality gates
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Development mode - skip quality gates
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality

# Quality check only - skip tests
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests

# Verbose mode for debugging
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

# Custom directories
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --source-dir src --test-dir tests

# With retry enabled
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --retry-failed
```

## ⚠️ Cancel Scope Error Prevention

The autoBMAD system uses the **Claude Agent SDK** for AI-driven development. To prevent Cancel Scope errors (related to anyio's async context management), the system implements specific safety requirements:

### Critical Safety Requirements

**1. NO External Timeouts**
- External `asyncio.wait_for()` timeouts have been removed
- System relies solely on SDK's built-in `max_turns` limit (150 turns)
- This prevents cancel scope conflicts during async operations

**2. Sequential Execution**
- Quality gates execute sequentially (Ruff → BasedPyright → Pytest)
- No concurrent execution that could trigger scope conflicts
- Each phase completes fully before the next begins

**3. SDK Configuration**
```python
# All agents use this configuration
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    max_turns=150,  # Maximum conversation turns (not time-based)
    cwd=str(Path.cwd())
)
```

**4. Error Handling**
- Cancel Scope errors are suppressed and logged
- System continues execution after scope-related errors
- Errors don't propagate to crash the application

### What This Means for Users

- **No manual timeout configuration needed** - SDK handles all timing
- **No external timeout flags** - removed from CLI
- **Sequential processing** - quality gates run one after another
- **Graceful degradation** - errors are caught and reported, not propagated

For detailed analysis, see: `docs/evaluation/cancel-scope-error-analysis.md`

## 🔍 Troubleshooting

### Common Issues

**Quality Gates Fail:**

```bash
# Check BasedPyRight errors
basedpyright src/ --output-format=json

# Check Ruff errors
ruff check src/ --output-format=json

# Fix all issues automatically
ruff check --fix src/
```

**Test Failures:**

```bash
# Run tests with verbose output
pytest tests/ -v --tb=long

# Debug specific test
pytest tests/test_specific.py -s --pdb
```

**Installation Issues:**

```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Cancel Scope Errors (Technical):**

If you see Cancel Scope errors in logs:
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

**This is expected and handled automatically:**
- Errors are suppressed by the system
- Processing continues normally
- No action required from users
- See `docs/evaluation/cancel-scope-error-analysis.md` for technical details

See `docs/troubleshooting/quality-gates.md` for detailed troubleshooting.

## 🔌 Claude Code Integration - Skills

The autoBMAD system can be integrated into Claude Code as a **Skill** for seamless AI-powered development.

### Installing the Skill

The autoBMAD skill package is located at `autoBMAD/Skill/`:

```bash
# Copy skill to Claude Code skills directory
cp autoBMAD/Skill/autoBMAD-epic-automation.skill ~/.claude/skills/

# Or use the installation script
# Windows PowerShell
.\autoBMAD\Skill\install_autoBMAD_skill.ps1

# Linux/macOS
./autoBMAD/Skill/install_autoBMAD_skill.sh
```

### Skill Documentation

- **[SKILL.md](autoBMAD/Skill/SKILL.md)** - Complete skill reference and usage guide
- **[SKILL_INSTALLATION_GUIDE.md](autoBMAD/Skill/SKILL_INSTALLATION_GUIDE.md)** - Step-by-step installation instructions

### Using the Skill in Claude Code

Once installed, Claude Code can invoke the autoBMAD workflow directly:

```
Please process the epic file docs/epics/my-epic.md using the autoBMAD workflow
```

The skill provides:
- ✅ Complete 5-phase workflow automation
- ✅ SM-Dev-QA cycle orchestration
- ✅ Quality gates (BasedPyright + Ruff)
- ✅ Test automation (Pytest)
- ✅ State management and recovery
- ✅ Detailed logging and reporting

## 📚 Documentation

- [Setup Guide](SETUP.md) - Installation and setup
- [Claude Code Guide](CLAUDE.md) - AI-assisted development guide
- [Workflow Tools](claude_docs/workflow_tools.md) - autoBMAD workflow details
- [Quality Assurance](claude_docs/quality_assurance.md) - QA processes and gates
- [BMAD Methodology](claude_docs/bmad_methodology.md) - Development methodology

## 🤝 Contributing

1. Follow the [Development Rules](claude_docs/development_rules.md)
2. Run quality gates before submitting
3. Add tests for new features
4. Update documentation

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Create an issue for bugs or feature requests
- Check [troubleshooting guide](docs/troubleshooting/)
- Review [quality gate documentation](docs/user-guide/quality-gates.md)

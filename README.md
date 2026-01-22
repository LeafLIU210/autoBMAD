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
│                    EPIC PROCESSING                          │
└─────────────────────────────────────────────────────────────┘

Phase 1: SM TaskGroup
├── SM Agent (Story Creation via Claude SDK)
├── Epic Document Analysis
├── Story ID Extraction
└── Story File Generation
         ↓
Phase 2: Dev-QA Cycle
├── DevQA Controller (State-Driven Workflow)
├── Dev Agent (Implementation)
├── QA Agent (Validation)
└── Status-Based Iteration (max 3 attempts)
         ↓
Phase 3: Quality Gates
├── Ruff Code Check & Auto-Fix
├── BasedPyright Type Checking
├── Ruff Format (Final)
└── Max 3 Retry Cycles per Tool
         ↓
Phase 4: Test Automation
├── Pytest Execution (Batch Processing)
├── Test Result Analysis
├── Debugpy for Persistent Failures
└── Max 5 Retry Cycles
         ↓
Phase 5: Orchestration & Documentation
├── Epic Driver (Workflow Management)
├── State Manager (SQLite Persistence)
├── Log Manager (Dual-Write Logging)
└── Quality Reports & Error Summaries
```

### Phase Details

**Phase 1: SM TaskGroup**
- SM Agent creates stories from epic documents using Claude SDK
- Extracts story IDs via regex patterns
- Generates complete story markdown files with AI
- Validates story structure and requirements
- **Must execute** even if story files already exist (per Memory)

**Phase 2: Dev-QA Cycle**
- **DevQA Controller** orchestrates state-driven workflow
- **Dev Agent**: Implements story according to specifications
- **QA Agent**: Validates implementation against acceptance criteria
- **State Agent**: Parses story status to drive workflow decisions
- **Status Update Agent**: Updates story status via SDK
- Automatic retry on failures (up to 3 attempts)
- Loop continues until story reaches "Ready for Done" or "Done"

**Phase 3: Quality Gates**
- **Ruff Check**: Linting with auto-fix (Cycle 1)
- **BasedPyright**: Static type checking (Cycle 2)
- **Ruff Format**: Final code formatting (Cycle 3)
- Maximum 3 retry cycles per tool
- Non-blocking: continues even with quality warnings
- Error summaries saved to JSON files

**Phase 4: Test Automation**
- **Pytest Controller**: Manages test execution pipeline
- **Batch Executor**: Runs tests efficiently
- **Test Automation Agent**: Fixes persistent failures via SDK
- **Debugpy Integration**: Debug complex test failures
- Maximum 5 retry cycles
- Detailed test reports and failure analysis

**Phase 5: Orchestration & Documentation**
- **Epic Driver**: Central orchestrator for complete workflow
- **State Manager**: SQLite-based persistence with WAL mode
- **Log Manager**: Dual-write logging (console + file)
- **Progress Tracking**: Real-time status across all phases
- **Quality Reports**: JSON error summaries and recommendations
- **Resource Monitoring**: CPU and memory usage tracking

## 📋 Phase-by-Phase Usage Guide

### Phase 1: SM TaskGroup

**Purpose**: AI-powered story creation from epic documents

```bash
# SM Agent extracts and creates stories automatically
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md
```

**What Happens:**
- Parses epic markdown to extract story IDs
- Uses Claude SDK to generate complete story files
- Creates story structure with acceptance criteria
- Validates requirements completeness

**Key Point**: Always executes even if story files exist (ensures state initialization)

### Phase 2: Dev-QA Cycle

**Purpose**: State-driven implementation and validation loop

```bash
# DevQA Controller manages the cycle automatically
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --max-iterations 3
```

**Workflow:**
1. **State Agent** reads current story status from markdown
2. **Dev Agent** implements if status = "Ready for Development"
3. **QA Agent** validates if status = "Ready for Review"
4. **Status Update Agent** updates story via SDK
5. Loops until status = "Ready for Done" or "Done"

**Retry Logic**: Up to 3 iterations per story

### Phase 3: Quality Gates

**Purpose**: Automated code quality checks (non-blocking)

```bash
# Run all quality gates (default)
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Skip quality gates for faster iteration
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality
```

**Three-Cycle Process:**

**Cycle 1: Ruff Check**
```bash
ruff check --fix src/  # Auto-fixes linting issues
```
- Checks PEP 8 compliance, unused imports, code complexity
- Automatic fixes applied where possible
- Max 3 retry cycles

**Cycle 2: BasedPyright**
```bash
basedpyright src/  # Type checking
```
- Static type validation
- Reports type errors and missing annotations
- Max 3 retry cycles

**Cycle 3: Ruff Format**
```bash
ruff format src/  # Final formatting
```
- Applies consistent code style
- Final polish before tests

**Error Handling:**
- Non-blocking: continues even with warnings
- Error summaries saved to `autoBMAD/epic_automation/errors/*.json`
- Quality warnings logged but don't halt pipeline

### Phase 4: Test Automation

**Purpose**: Comprehensive test execution with intelligent retry

```bash
# Run pytest automation (default)
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Skip tests for quick validation
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests

# Custom test directory
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --test-dir tests/
```

**Test Pipeline:**
1. **Pytest Controller** discovers and batches tests
2. **Batch Executor** runs tests efficiently
3. **Test Automation Agent** analyzes failures and fixes via SDK
4. **Debugpy** activates for persistent failures (300s timeout)
5. Max 5 retry cycles

**Batch Execution:**
- Dynamic directory scanning (no hardcoded paths)
- Automatic batch grouping by test type
- Parallel execution support

### Phase 5: Orchestration & Documentation

**Purpose**: Workflow management and persistent state tracking

**Components:**

**Epic Driver** (Central Orchestrator)
- Coordinates all phase execution
- Manages phase-gated progression
- Handles retry logic and error recovery

**State Manager** (SQLite Persistence)
- WAL mode for concurrent access
- Optimistic locking for consistency
- Tracks epic/story progress across phases

**Log Manager** (Dual-Write Logging)
```bash
# Enable log file creation
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --log-file
```
- Console output (always on)
- File logging (optional, timestamped)
- Structured logging with phase context

**Quality Reports**
- JSON error summaries in `errors/` directory
- Includes tool name, cycles, remaining issues
- Recommendations for manual fixes

**Resource Monitoring**
- CPU and memory usage tracking
- Performance metrics collection
- Bottleneck identification

## ⚙️ Configuration

### pyproject.toml

```toml
[tool.basedpyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"

[tool.ruff]
line-length = 88
target-version = "py312"
select = ["E", "F", "B", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--verbose"
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY=your_api_key  # Required for Claude SDK
export PYTHONPATH=.  # Required for imports
```

## 🎯 CLI Reference

```bash
python -m autoBMAD.epic_automation.epic_driver [OPTIONS] EPIC_PATH
```

**Essential Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `EPIC_PATH` | Path to epic markdown file | *required* |
| `--skip-quality` | Skip Phase 3 (Quality Gates) | false |
| `--skip-tests` | Skip Phase 4 (Test Automation) | false |
| `--max-iterations N` | Phase 2 retry limit | 3 |
| `--verbose` | Detailed logging | false |
| `--log-file` | Create timestamped log files | false |
| `--source-dir DIR` | Source code directory | src |
| `--test-dir DIR` | Test directory | tests |

**Common Patterns:**

```bash
# Full 5-phase pipeline
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Fast iteration (skip Phase 3 & 4)
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality --skip-tests

# Debug mode with logs
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose --log-file
```

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

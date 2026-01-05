# autoBMAD Epic Automation System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**autoBMAD** (Breakthrough Method of Agile AI-driven Development) is an intelligent automation system that processes epics through a complete 5-phase workflow with integrated code quality gates and test automation.

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
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    Pytest    │→ │   Debugpy    │                        │
│  │  (Execute)   │  │ (Debug Failures)                      │
│  └──────────────┘  └──────────────┘                        │
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
- **Debugpy**: Persistent debugging for failing tests
- Maximum 5 retry attempts
- Detailed test reports

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

Quality gates ensure code quality before proceeding to test automation.

### BasedPyRight Type Checking

BasedPyRight provides static type checking for Python code:

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

### Ruff Linting

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

### CLI Quality Gate Options

```bash
# Skip all quality gates
python epic_driver.py my-epic.md --skip-quality

# Custom retry attempts
python epic_driver.py my-epic.md --max-iterations 5

# Verbose quality gate output
python epic_driver.py my-epic.md --verbose
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

### Debugpy Integration

Debugpy provides persistent debugging for test failures:

```bash
# Run tests with debugging
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client pytest tests/

# Or use the built-in runner
python epic_driver.py my-epic.py --verbose
```

**Debugpy Features:**
- Attach debugger to running tests
- Inspect test state
- Step through failing tests
- Set breakpoints dynamically

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
debugpy>=1.6.0

# Core System
pyside6>=6.0.0
claude-api>=1.0.0
asyncio
sqlite3
```

### Environment Variables

```bash
# Claude API
export CLAUDE_API_KEY=your_api_key

# Debug Settings
export DEBUGPY_ENABLED=true
export DEBUGPY_PORT=5678

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
  --source-dir DIR       Source code directory (default: src)
  --test-dir DIR         Test directory (default: tests)
  --skip-quality         Skip code quality gates
  --skip-tests           Skip test automation
  --max-iterations N     Max retry attempts (default: 3)
  --verbose              Enable verbose logging
  --concurrent           Enable concurrent processing
  --help                 Show this message and exit
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

## 📚 Documentation

- [Setup Guide](SETUP.md) - Installation and setup
- [User Guide](docs/user-guide/) - Detailed usage guides
  - [Quality Gates](docs/user-guide/quality-gates.md)
  - [Test Automation](docs/user-guide/test-automation.md)
- [Architecture](docs/architecture/) - System design
- [API Reference](docs/api/) - Developer documentation
- [BMAD Workflow](bmad-workflow/) - Workflow automation

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

# autoBMAD Epic Automation System - AI Agent Guide

**Project**: PyQt Windows应用程序开发模板 (PyQt Windows Application Development Template)  
**Version**: 2.0.0  
**Language**: 中文/English (Bilingual)  
**Architecture**: BMAD (Breakthrough Method of Agile AI-driven Development)  

## 🎯 Project Overview

This is an intelligent automation system that processes software development epics through a complete 5-phase workflow with integrated code quality gates and test automation. The system uses AI agents to implement the BMAD methodology for PyQt Windows application development.

### Core Philosophy: "Vibe CEO" Model
- **You as CEO**: Provide vision and decisions
- **AI as Execution Team**: Implement through specialized agents
- **Structured Workflow**: Proven patterns from idea to deployment
- **Clear Handoffs**: Fresh context windows every time

## 🏗️ Project Architecture

### Technology Stack
```
├── Frontend: PySide6 (Qt6) - Modern cross-platform GUI framework
├── Backend: Python 3.8+ with async/await support
├── AI Integration: Claude API SDK for intelligent development
├── Quality Gates: BasedPyRight (type checking) + Ruff (linting/auto-fix)
├── Testing: pytest + pytest-cov + pytest-qt + debugpy
├── Build: Nuitka (high-performance Python compilation)
├── Database: SQLite (progress tracking)
└── Workflow: PowerShell + Python automation scripts
```

### Directory Structure
```
project/
├── src/                          # Source code (minimal - only bubblesort.py)
├── autoBMAD/                     # Main automation system
│   └── epic_automation/          # 5-phase workflow implementation
├── tests/                        # Comprehensive test suite (45+ test files)
├── docs/                         # Epic and story documentation
├── claude_docs/                  # Detailed methodology documentation
├── bmad-workflow/                # BMAD automation tools
├── basedpyright-workflow/        # Type checking and code quality
├── fixtest-workflow/             # Test automation and debugging
├── build/                        # Build configurations
├── logs/                         # Execution logs
├── progress.db                   # SQLite database for tracking
└── Configuration files...
```

## 🔧 Key Configuration Files

### pyproject.toml
- **Build System**: Hatchling backend
- **Python Requirements**: >=3.8, Windows-focused
- **Testing**: pytest with comprehensive markers (slow, integration, unit, e2e, performance, documentation, epic, gui)
- **Code Quality**: Black (line-length: 88), isort, mypy strict mode
- **Package Structure**: autoBMAD as main package

### requirements.txt (Production)
- PySide6>=6.5.0 (Qt framework)
- loguru>=0.7.0 (logging)
- claude_agent_sdk>=0.1.0 (AI integration)
- basedpyright>=1.1.0 (type checking)
- ruff>=0.1.0 (linting)
- pytest>=7.0.0 (testing)
- debugpy>=1.6.0 (debugging)

### requirements-dev.txt (Development)
- All production dependencies
- pytest-cov, pytest-qt, pytest-timeout, pytest-mock
- nuitka>=1.8.0 (build tool)

## 🚀 5-Phase Workflow Architecture

### Phase 1: SM-Dev-QA Cycle
```
Story Master → Developer → QA Validator
   (Create)    (Implement)   (Review)
```
- **SMAgent**: Creates user stories from epics
- **DevAgent**: Implements code using Claude API
- **QAAgent**: Validates implementation quality
- **Retry Logic**: Up to 3 attempts per phase

### Phase 2: Quality Gates
- **BasedPyRight**: Static type checking with strict mode
- **Ruff**: Fast linting with automatic fixes
- **Max Retries**: 3 attempts before failure
- **Blocking**: Prevents progression if quality gates fail

### Phase 3: Test Automation
- **pytest**: Comprehensive test execution
- **debugpy**: Persistent debugging for failures
- **Max Retries**: 5 attempts with detailed reporting
- **Coverage**: HTML and terminal coverage reports

### Phase 4: Orchestration
- **EpicDriver**: Main workflow orchestrator
- **StateManager**: Progress tracking in SQLite
- **Concurrent Processing**: Optional parallel story processing
- **Real-time Reporting**: Status updates throughout execution

### Phase 5: Documentation & Integration
- **Auto-documentation**: Generated from implementation
- **Integration Testing**: Complete workflow validation
- **System Consistency**: Ensures all components work together

## 🛠️ Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m autoBMAD.epic_automation.epic_driver --help
```

### Quality Gates
```bash
# Type checking
basedpyright src/

# Linting with auto-fix
ruff check --fix src/

# Code formatting
ruff format src/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/gui/ -v              # GUI tests
pytest -m "not slow"              # Exclude slow tests
pytest tests/unit/ -v             # Unit tests only
```

### Epic Processing
```bash
# Process epic through complete workflow
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md

# Skip quality gates for faster iteration
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality

# Skip test automation
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests

# Verbose output with custom iterations
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose --max-iterations 5
```

## 🧪 Testing Strategy

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component workflow testing
- **E2E Tests**: Complete epic processing workflows
- **GUI Tests**: PySide6 interface testing with pytest-qt
- **Performance Tests**: Benchmark and load testing
- **Quality Gate Tests**: BasedPyRight and Ruff integration

### Test Markers
- `slow`: Long-running tests
- `integration`: Integration test suite
- `unit`: Unit test suite
- `e2e`: End-to-end tests
- `performance`: Performance benchmarks
- `documentation`: Documentation tests
- `epic`: Epic automation tests
- `gui`: GUI-specific tests

### Test Automation Features
- **Automatic Retry**: Failed tests retry up to 5 times
- **Debug Integration**: debugpy attaches to failing tests
- **JSON Reporting**: Test results in machine-readable format
- **Coverage Tracking**: HTML and terminal coverage reports

## 📋 Code Style Guidelines

### Import Rules (Critical)
```python
# ✅ CORRECT - Absolute imports, no source directory name
from services.config_service import ConfigService
from ui.widgets.button import CustomButton

# ❌ INCORRECT - Never do this
from Project_recorder.services.config_service import ConfigService  # Includes source dir
from ..services.config_service import ConfigService                 # Relative import
```

### Type Annotations
- **Strict Mode**: basedpyright configured for strict type checking
- **All Functions**: Must have complete type annotations
- **No Any Types**: Avoid `Any` unless absolutely necessary
- **Return Types**: Always specify return types explicitly

### Code Quality Standards
- **Line Length**: 88 characters (Black configuration)
- **Import Sorting**: isort with black profile
- **Docstrings**: Required for all public functions
- **Error Handling**: Specific exception types, not broad catches

## 🔍 Quality Gate Configuration

### BasedPyRight Settings
```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
reportMissingImports = true
reportOptionalMemberAccess = true
reportGeneralTypeIssues = true
```

### Ruff Configuration
```toml
[tool.ruff]
line-length = 88
target-version = "py38"
select = ["E", "F", "B", "I", "C4", "UP"]
ignore = ["E501", "B008"]
```

## 🚨 Common Issues & Solutions

### Quality Gate Failures
```bash
# Check specific errors
basedpyright src/ --output-format=json
ruff check src/ --output-format=json

# Auto-fix available issues
ruff check --fix src/

# Skip quality gates temporarily (development only)
python epic_driver.py my-epic.md --skip-quality
```

### Test Failures
```bash
# Verbose test output
pytest tests/ -v --tb=long

# Debug specific test
pytest tests/test_specific.py -s --pdb

# Run with debugpy
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client pytest tests/
```

### Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 📚 Key Documentation

### Detailed Guides (claude_docs/)
- **core_principles.md**: DRY, KISS, YAGNI, 奥卡姆剃刀 principles
- **bmad_methodology.md**: Complete BMAD development methodology
- **ai_workflow.md**: 3-stage AI assistant workflow
- **development_rules.md**: Coding standards and import rules
- **testing_guide.md**: Testing practices and pytest usage
- **quality_assurance.md**: QA processes and quality gates
- **technical_specs.md**: Dependencies and configuration
- **workflow_tools.md**: Three workflow tools detailed explanation

### Quick References
- **quick_reference.md**: All commands quick lookup
- **project_tree.md**: Detailed directory structure
- **venv.md**: Virtual environment management

## 🔐 Security Considerations

### Environment Variables
```bash
# Claude API (required for AI functionality)
CLAUDE_API_KEY=your_api_key_here

# Debug Settings
DEBUGPY_ENABLED=true
DEBUGPY_PORT=5678

# Quality Gate Settings
MAX_ITERATIONS=3
SKIP_QUALITY_ON_ERROR=false
```

### Safe Practices
- **Never commit API keys** to version control
- **Use environment variables** for sensitive configuration
- **Validate all inputs** from epic files
- **Sandbox test execution** with proper isolation

## 🎯 Success Metrics

### Quality Indicators
- ✅ All quality gates pass (BasedPyRight + Ruff)
- ✅ Test coverage > 80% for core modules
- ✅ All epics process successfully through 5-phase workflow
- ✅ No critical security vulnerabilities
- ✅ Documentation auto-generated and up-to-date

### Performance Targets
- Epic processing: < 5 minutes for standard epics
- Quality gates: < 30 seconds per phase
- Test execution: < 2 minutes for full suite
- Memory usage: < 1GB during normal operation

---

**Remember**: This system implements the "Vibe CEO" model where you provide vision and AI executes through structured workflows. Always follow the 4 golden principles: DRY, KISS, YAGNI, and 奥卡姆剃刀 (Occam's Razor).
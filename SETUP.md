# Setup and Installation Guide

This guide covers complete installation and setup for the autoBMAD Epic Automation System with quality gates and test automation.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.8 or higher
- **Git**: Version 2.20 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: At least 2GB free space

### Check Your Versions

```bash
# Check Python version
python --version

# Check Git version
git --version
```

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd pytQt_template
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Verify Activation:**
```bash
# Should show (.venv) in prompt
which python
# Should point to .venv directory
```

### 3. Install Dependencies

#### Core Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Quality Gate Tools

**BasedPyRight (Type Checking):**
```bash
pip install basedpyright>=1.1.0

# Verify installation
basedpyright --version
```

**Ruff (Linting & Auto-fix):**
```bash
pip install ruff>=0.1.0

# Verify installation
ruff --version
```

#### Test Automation Tools

**Pytest (Testing Framework):**
```bash
pip install pytest>=7.0.0 pytest-cov>=4.0.0

# Verify installation
pytest --version
```

**Debugpy (Debugging):**
```bash
pip install debugpy>=1.6.0

# Verify installation
python -m debugpy --version
```

#### Core System Dependencies

**PySide6 (GUI Framework):**
```bash
pip install PySide6>=6.0.0

# Verify installation
python -c "import PySide6; print(PySide6.__version__)"
```

**Claude API:**
```bash
pip install claude-api>=1.0.0

# Verify installation
python -c "import claude_api; print(claude_api.__version__)"
```

### 4. Verify Installation

Run the verification script:

```bash
python -c "
import sys
print('Python version:', sys.version)

# Test imports
try:
    import basedpyright
    print('✓ BasedPyRight installed')
except ImportError:
    print('✗ BasedPyRight NOT installed')

try:
    import ruff
    print('✓ Ruff installed')
except ImportError:
    print('✗ Ruff NOT installed')

try:
    import pytest
    print('✓ Pytest installed')
except ImportError:
    print('✗ Pytest NOT installed')

try:
    import debugpy
    print('✓ Debugpy installed')
except ImportError:
    print('✗ Debugpy NOT installed')

try:
    import PySide6
    print('✓ PySide6 installed')
except ImportError:
    print('✗ PySide6 NOT installed')

# Test CLI commands
import subprocess
try:
    result = subprocess.run(['basedpyright', '--version'],
                          capture_output=True, text=True)
    print('✓ BasedPyRight CLI:', result.stdout.strip())
except:
    print('✗ BasedPyRight CLI failed')

try:
    result = subprocess.run(['ruff', '--version'],
                          capture_output=True, text=True)
    print('✓ Ruff CLI:', result.stdout.strip())
except:
    print('✗ Ruff CLI failed')
"
```

Expected output should show all tools as "✓ installed" and CLIs with version numbers.

## Quality Gate Setup

### BasedPyRight Configuration

Create or update `pyproject.toml`:

```toml
[tool.basedpyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"

# Type checking options
reportMissingImports = true
reportOptionalMemberAccess = true
reportGeneralTypeIssues = true

# Pyright compatible settings
useLibraryCodeForTypes = true
verboseOutput = false
```

Test BasedPyRight:

```bash
# Check entire project
basedpyright src/

# Check specific file
basedpyright src/autoBMAD/epic_automation/epic_driver.py

# Output JSON format
basedpyright src/ --output-format=json
```

### Ruff Configuration

Update `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py38"
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "B",    # flake8-bugbear
    "I",    # isort
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = [
    "E501", # line too long, handled by black
    "B008", # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

Test Ruff:

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# View detailed report
ruff check --output-format=full src/
```

## Test Automation Setup

### Pytest Configuration

Update `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
    "gui: GUI tests",
]
```

### Pytest Verification

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_epic_driver.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run GUI tests
pytest tests/gui/ -v

# Run specific marker
pytest -m "not slow"
```

### Debugpy Configuration

Debugpy is automatically configured, but you can customize:

```python
# debugpy_config.py
import debugpy

# Configure debugpy
debugpy.configure({
    "python": "/path/to/.venv/python.exe"
})

# Listen on specific port
debugpy.listen(5678)

# Wait for debugger attachment
debugpy.wait_for_client()
```

Test Debugpy:

```bash
# Start test with debugging
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client pytest tests/

# In VS Code, attach to debugger
# F5 or Debug > Attach to Process
```

## Environment Variables

Create `.env` file in project root:

```bash
# Claude API Configuration
CLAUDE_API_KEY=your_api_key_here
CLAUDE_API_BASE=https://api.anthropic.com

# Debug Settings
DEBUGPY_ENABLED=true
DEBUGPY_PORT=5678
DEBUGPY_WAIT_FOR_CLIENT=false

# Quality Gate Settings
MAX_ITERATIONS=3
SKIP_QUALITY_ON_ERROR=false
SKIP_TESTS_ON_ERROR=false

# Performance Settings
CONCURRENT_PROCESSING=false
MAX_CONCURRENT_STORIES=3

# Logging
LOG_LEVEL=INFO
VERBOSE=false

# Database
DATABASE_URL=sqlite:///./progress.db
```

Load environment variables:

```bash
# Install python-dotenv
pip install python-dotenv

# In your code
from dotenv import load_dotenv
load_dotenv()
```

## Project Structure Setup

Ensure directory structure exists:

```bash
mkdir -p src/autoBMAD/epic_automation
mkdir -p tests/{unit,integration,e2e,gui,performance}
mkdir -p docs/{examples,user-guide,architecture,troubleshooting}
mkdir -p logs
mkdir -p build
```

## Troubleshooting

### Common Installation Issues

**Issue: Virtual environment activation fails (Windows)**

```cmd
# Use full path to activate
C:\path\to\pytQt_template\.venv\Scripts\activate

# Or enable execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue: pip install fails with permission error**

```bash
# Use --user flag
pip install --user basedpyright

# Or fix permissions
sudo chown -R $USER ~/.local
```

**Issue: BasedPyRight not found**

```bash
# Check PATH
echo $PATH

# Reinstall
pip uninstall basedpyright
pip install basedpyright

# Or use full path
~/.venv/bin/basedpyright src/
```

**Issue: Ruff command not found**

```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall
pip uninstall ruff
pip install ruff

# Check installation
which ruff
```

**Issue: PySide6 installation fails**

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev qtbase5-dev

# Or use conda
conda install -c conda-forge pyside6

# Verify
python -c "import PySide6.QtWidgets; print('Success')"
```

### Quality Gate Issues

**Issue: BasedPyRight reports too many errors**

Check `pyproject.toml` settings:
```toml
[tool.basedpyright]
typeCheckingMode = "basic"  # Try "off" for minimal checking
reportMissingImports = false  # Disable if needed
reportOptionalMemberAccess = false  # Disable if needed
```

**Issue: Ruff auto-fix doesn't work**

```bash
# Check if auto-fix is enabled
ruff check --fix --show-fixes src/

# Manual fix specific issue
ruff check src/ --select E501  # Fix specific error code
```

### Test Automation Issues

**Issue: pytest not found**

```bash
# Ensure virtual environment is activated
which pytest

# Reinstall pytest
pip uninstall pytest pytest-cov
pip install pytest pytest-cov
```

**Issue: debugpy connection fails**

```bash
# Check if port is available
netstat -an | grep 5678

# Use different port
python -m debugpy --listen 0.0.0.0:5679 pytest tests/

# Update client to connect to 5679
```

### Performance Issues

**Issue: Slow type checking**

- Exclude test files: `basedpyright src/ --exclude tests/`
- Reduce file count: Check only modified files
- Adjust `typeCheckingMode` to "basic" or "off"

**Issue: Slow linting**

- Enable file caching: Set `RUFF_CACHE_DIR` environment variable
- Use `--exclude` to skip large directories
- Run linting incrementally: `ruff check --diff`

**Issue: Slow test execution**

- Use markers: `pytest -m "not slow"`
- Parallel execution: `pytest -n auto`
- Increase timeout: `pytest --timeout=300`

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from `requirements.txt`
- [ ] BasedPyRight working: `basedpyright --version`
- [ ] Ruff working: `ruff --version`
- [ ] Pytest working: `pytest --version`
- [ ] Debugpy working: `python -m debugpy --version`
- [ ] PySide6 working: `python -c "import PySide6"`
- [ ] Epic driver working: `python -m autoBMAD.epic_automation.epic_driver --help`
- [ ] Configuration files created (`pyproject.toml`)
- [ ] Environment variables set (`.env`)

## Next Steps

After successful installation:

1. Read [README.md](README.md) for quick start
2. Review [User Guide](docs/user-guide/)
3. Check [Architecture](docs/architecture/)
4. Run example epic: `python -m autoBMAD.epic_automation.epic_driver docs/examples/example-epic-with-quality-gates.md`
5. Review [Troubleshooting](docs/troubleshooting/)

## Getting Help

- Check [Troubleshooting Guide](docs/troubleshooting/quality-gates.md)
- Review existing issues in the repository
- Create a new issue with:
  - Operating system and version
  - Python version
  - Error messages (full traceback)
  - Steps to reproduce
- Run diagnostics: `python -c "import sys; print(sys.version); import site; print(site.getsitepackages())"`

## Uninstall

To completely remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf .venv

# Remove project directory
cd ..
rm -rf pytQt_template
```

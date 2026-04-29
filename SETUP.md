# Setup and Installation Guide

DocuSwarm Multi-Agent Document Orchestration System 的安装与配置指南。

## Prerequisites

### System Requirements

- **Operating System**: WSL2 (Ubuntu 24.04+), Linux, or macOS
- **Python**: 3.12+
- **Git**: 2.20+
- **Memory**: 4GB RAM (8GB recommended)
- **Disk Space**: 2GB free

### Check Your Versions

```bash
python3 --version   # Should be 3.12+
git --version        # Should be 2.20+
```

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/LeafLIU210/autoBMAD.git
cd autoBMAD
```

### 2. Create Virtual Environment

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

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Configure API Keys

```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

### 5. Verify Installation

```bash
# Check CLI
python -m autoBMAD.docuswarm --help

# Quick verification
python -c "
import sys
print('Python version:', sys.version)

modules = [
    'langgraph', 'langchain', 'pydantic',
    'click', 'rich', 'structlog', 'aiofiles', 'aiosqlite',
    'yaml', 'dotenv'
]
for mod in modules:
    try:
        __import__(mod)
        print(f'  {mod} OK')
    except ImportError:
        print(f'  {mod} MISSING')
"
```

## Quality Gate Setup

### BasedPyRight (Type Checking)

已在 `pyproject.toml` 中配置：

```bash
# Check entire project
basedpyright autoBMAD/

# Check specific file
basedpyright autoBMAD/docuswarm/config.py
```

### Ruff (Linting & Formatting)

已在 `pyproject.toml` 中配置（line-length=100, target-version="py312"）：

```bash
# Check for issues
ruff check autoBMAD/

# Auto-fix issues
ruff check --fix autoBMAD/

# Format code
ruff format autoBMAD/
```

## Test Automation

### Running Tests

```bash
# Run all tests
pytest -v --tb=short

# Run with coverage
pytest --cov=autoBMAD/docuswarm --cov-report=html

# Run specific marker
pytest -m "not slow"
```

## Environment Variables

Create `.env` file in project root:

```bash
# Required - Anthropic API Key
ANTHROPIC_API_KEY=your_api_key_here

# Optional - Custom API Base URL
# ANTHROPIC_BASE_URL=https://custom-api-url/

# Optional - DocuSwarm Configuration
DOCUSWARM_DB_PATH=docuswarm.db
DOCUSWARM_OUTPUT_DIR=output
DOCUSWARM_LOG_LEVEL=INFO
DOCUSWARM_MAX_ITERATIONS=100
```

## Troubleshooting

### Common Issues

**Issue: pip install fails with permission error**

```bash
pip install --user -r requirements.txt
# Or fix permissions
sudo chown -R $USER ~/.local
```

**Issue: BasedPyRight not found**

```bash
pip install basedpyright
which basedpyright
```

**Issue: Ruff command not found**

```bash
source .venv/bin/activate
pip install ruff
which ruff
```

**Issue: Database locked**

```bash
sqlite3 docuswarm.db "PRAGMA journal_mode=WAL;"
```

## Verification Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from `requirements.txt`
- [ ] BasedPyRight working: `basedpyright --version`
- [ ] Ruff working: `ruff --version`
- [ ] Pytest working: `pytest --version`
- [ ] `.env` file configured with `ANTHROPIC_API_KEY`
- [ ] CLI working: `python -m autoBMAD.docuswarm --help`

## Next Steps

1. Read [README.md](README.md) for project overview and CLI reference
2. Read [DocuSwarm Guide](autoBMAD/docuswarm/README.md) for detailed usage
3. Read [CLAUDE.md](CLAUDE.md) for development guidelines
4. Try a pipeline: `python -m autoBMAD.docuswarm start --context docs-test/calc-one-plus-one/calc-context.md`

## Uninstall

```bash
deactivate
rm -rf .venv
cd ..
rm -rf autoBMAD
```

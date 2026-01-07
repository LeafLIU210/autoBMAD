# autoBMAD Tech Stack Documentation

**Version**: 2.0
**Date**: 2026-01-05
**Project**: autoBMAD Epic Automation System

---

## Overview

This document defines the complete technology stack for the autoBMAD epic automation system, including the integration of code quality and test automation workflows.

---

## Core Technology Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Core Language** | Python | 3.8+ | Primary development language | Wide adoption, extensive library ecosystem, excellent CLI support |
| **CLI Framework** | argparse | Built-in | Command-line interface parsing | Standard library, no external dependencies, full-featured |
| **Async Framework** | asyncio | Built-in | Concurrent story processing | Built-in async support for experimental concurrency |
| **Database** | SQLite | 3.x | State management | Self-contained, zero-configuration, persistent storage, ACID compliant |
| **State Management** | Custom ORM | N/A | Progress tracking | Lightweight, tailored to epic automation needs, no external ORM dependencies |
| **Code Quality** | basedpyright | Latest | Type checking | Enhanced Pyright with better Python support, strict type checking |
| **Code Quality** | ruff | Latest | Linting & auto-fix | Extremely fast (10-100x faster than flake8), comprehensive rules, auto-fix capability |
| **Testing** | pytest | Latest | Test execution framework | Industry standard, extensive plugin ecosystem, fixture support |
| **Debugging** | debugpy | Latest | Test failure diagnosis | Remote debugging capabilities, VS Code integration |
| **Virtual Environment** | venv | Built-in | Dependency isolation | Standard library, cross-platform, recommended by Python.org |
| **Logging** | logging | Built-in | System logging | Standard library, configurable levels, production-ready |
| **Path Handling** | pathlib | Built-in | Cross-platform path operations | Modern, object-oriented path handling, Python 3.4+ |

---

## Development Dependencies

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Claude SDK | Latest | AI agent integration for automated fixes | `pip install anthropic` |
| pip | Latest | Package management | Built-in with Python |
| virtualenv/venv | Built-in | Environment isolation | `python -m venv .venv` |

## Quality Gate Tool Integration

**Two Integration Modes Available:**

### Option A: Workflow Directory Integration
```bash
# Copy workflow directories to project root
cp -r /path/to/basedpyright-workflow /your/project/
cp -r /path/to/fixtest-workflow /your/project/
```
**Benefits**: Complete toolchain, pre-configured, includes automation scripts

### Option B: Pip Installation
```bash
# Install quality gate tools
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0
```
**Benefits**: Standard Python dependency management, version control via requirements.txt

**Graceful Fallback**: If tools unavailable, system continues with WAIVED QA status

## Standalone Systems

**NOT Required:**
- **bmad-workflow**: autoBMAD is a standalone system with its own orchestrator
- **External CI/CD**: Self-contained with SQLite state management

---

## Dependency Versions

### requirements.txt

```
# Core automation
# (Python standard library - no installation needed)

# Code Quality Tools
basedpyright>=1.1.0
ruff>=0.1.0

# Testing Tools
pytest>=7.0.0
debugpy>=1.6.0

# Development Tools
anthropic>=0.7.0
```

### Version Constraints

**Minimum Python Version**: 3.8
- Rationale: asyncio support, pathlib maturity, f-string enhancements
- Check: `python --version`

**Basedpyright Version**: >= 1.1.0
- Rationale: Stable Python 3.8+ support, enhanced type checking
- Config: `--pythonversion 3.8`

**Ruff Version**: >= 0.1.0
- Rationale: Fast implementation, comprehensive rule set
- Config: `--target-version py38`

**Pytest Version**: >= 7.0.0
- Rationale: Modern fixture system, asyncio support
- Config: `--asyncio-mode=auto`

**Debugpy Version**: >= 1.6.0
- Rationale: Stable remote debugging, VS Code integration
- Config: `--listen localhost:5678`

---

## Technology Selection Rationale

### Why Python 3.8+?

1. **Broad Compatibility**: Python 3.8 is widely available across platforms
2. **Async Support**: Native asyncio support for concurrent processing
3. **Modern Features**: f-strings, pathlib, dataclasses reduce boilerplate
4. **Ecosystem**: Extensive library support for CLI tools and automation
5. **Claude SDK**: Official Anthropic SDK supports Python 3.8+

### Why SQLite?

1. **Zero Configuration**: No database server setup required
2. **Self-Contained**: Single file database, portable across systems
3. **ACID Compliant**: Reliable transactions for state management
4. **Performance**: Fast enough for epic automation use cases
5. **Cross-Platform**: Native support on all platforms

### Why Basedpyright + Ruff?

**Basedpyright**:
- Superior to mypy for modern Python
- Better error messages and type inference
- Faster performance
- Active development

**Ruff**:
- 10-100x faster than flake8/pylint
- Comprehensive rule set (300+ rules)
- Auto-fix capability
- Single binary deployment

### Why Pytest?

1. **Industry Standard**: Widely adopted in Python community
2. **Fixture System**: Powerful dependency injection
3. **Plugin Ecosystem**: Extensive third-party plugins
4. **Async Support**: Built-in async test support
5. **Reporting**: Rich output and reporting options

### Why Debugpy?

1. **Remote Debugging**: Attach debugger to running processes
2. **VS Code Integration**: Native IDE support
3. **Scriptable**: Can be invoked programmatically
4. **Production Ready**: Used by Microsoft and others

---

## Platform Compatibility

### Supported Platforms

| Platform | Python Version | Status |
|----------|----------------|--------|
| Windows 10/11 | 3.8+ | ✅ Fully Supported |
| macOS 10.15+ | 3.8+ | ✅ Fully Supported |
| Linux (Ubuntu 18.04+) | 3.8+ | ✅ Fully Supported |

### Virtual Environment Setup

**Windows**:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration Files

### pyproject.toml

```toml
[tool.basedpyright]
pythonVersion = "3.8"
pythonPlatform = "All"
typeCheckingMode = "strict"
reportGeneralTypeIssues = true
reportOptionalMemberAccess = true
reportOptionalSubscript = true
reportPrivateImportUsage = true
exclude = [
    "**/__pycache__",
    "**/.venv",
    "**/venv",
    "build/",
    "dist/"
]

[tool.ruff]
target-version = "py38"
line-length = 88
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
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"test_*.py" = ["B018", "B017"]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"
```

---

## Performance Characteristics

### Expected Performance

| Operation | Expected Time | Maximum Time | Notes |
|-----------|---------------|--------------|-------|
| **Start Epic** | < 1 second | 5 seconds | Database initialization |
| **Create Story** | < 1 minute | 5 minutes | Claude agent execution |
| **Develop Story** | Variable | N/A | Depends on complexity |
| **QA Validation** | < 30 seconds | 2 minutes | File analysis |
| **Basedpyright Check** | < 10 seconds/.py file | 30 seconds/.py file | Depends on file size |
| **Ruff Check** | < 5 seconds/.py file | 15 seconds/.py file | Very fast, mostly I/O |
| **Pytest Execution** | < 5 minutes/test suite | 15 minutes/test suite | Depends on test count |

### Optimization Settings

**Basedpyright**:
- Use `--level error` to filter warnings
- Use `--outputjson` for machine-readable output
- Cache results when possible

**Ruff**:
- Use `--fix` for automatic corrections
- Use `--output-format json` for automation
- Enable parallelism with `--jobs auto`

**Pytest**:
- Use `--tb=short` for concise output
- Use `--maxfail=1` to stop on first failure
- Use `-x` to fail fast
- Use `--json-report` for automation

---

## Security Considerations

### Dependency Security

1. **Pin Versions**: All dependencies have version constraints
2. **Audit Dependencies**: Use `pip-audit` to check for vulnerabilities
3. **Virtual Environment**: Always use venv for isolation
4. **Minimal Dependencies**: Only install necessary packages

### Code Security

1. **Input Validation**: Validate all file paths and inputs
2. **SQL Injection**: Use parameterized queries only
3. **Command Injection**: Sanitize all subprocess arguments
4. **Timeout Controls**: Set timeouts for all external commands

---

## Upgrade Path

### Python Version Upgrades

**To Python 3.9+**:
- Update `pyproject.toml`: `target-version = "py39"`
- Test compatibility with all dependencies
- Update minimum version in requirements.txt

**To Python 3.10+**:
- Update `target-version = "py310"`
- Use new type union syntax: `X | Y` instead of `Union[X, Y]`
- Test performance improvements

### Dependency Upgrades

**Basedpyright**:
```bash
pip install --upgrade basedpyright
basedpyright --version
```

**Ruff**:
```bash
pip install --upgrade ruff
ruff --version
```

**Pytest**:
```bash
pip install --upgrade pytest
pytest --version
```

---

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt
```

**Basedpyright Not Found**:
```bash
# Install basedpyright
pip install basedpyright

# Verify installation
basedpyright --version
```

**Ruff Not Found**:
```bash
# Install ruff
pip install ruff

# Verify installation
ruff --version
```

**Pytest Not Running**:
```bash
# Install pytest
pip install pytest

# Verify installation
pytest --version
```

### Performance Issues

**Slow Quality Checks**:
- Check file count in source directory
- Exclude test files: `basedpyright --exclude **/tests`
- Use caching: set `BASEDPYRIGHT_CACHE` environment variable

**Slow Pytest**:
- Run specific test files: `pytest tests/test_file.py`
- Use parallel execution: `pytest -n auto`
- Disable plugins: `pytest -p no:benchmark`

---

## References

### Documentation Links

- [Python Documentation](https://docs.python.org/3/)
- [SQLite Documentation](https://sqlite.org/docs.html)
- [Basedpyright Documentation](https://github.com/DetachHead/basedpyright)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Debugpy Documentation](https://github.com/microsoft/debugpy)

### Best Practices

- Always use virtual environments
- Pin dependency versions in requirements.txt
- Run quality checks before committing
- Use type hints for better code quality
- Write tests for all new features
- Document complex logic

---

## Summary

The autoBMAD tech stack is designed for:
- **Reliability**: Proven, stable technologies
- **Performance**: Fast tools optimized for developer productivity
- **Maintainability**: Minimal dependencies, clear configuration
- **Security**: Safe practices and dependency management
- **Scalability**: Efficient tools that handle growth

This technology stack provides a solid foundation for automated epic processing with integrated quality assurance, ensuring code quality while maintaining development velocity.

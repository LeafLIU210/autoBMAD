# autoBMAD Dependencies Documentation

**Version**: 1.0  
**Date**: 2026-01-05  
**Project**: autoBMAD Epic Automation System

---

## Overview

This document describes the complete dependency model for autoBMAD, including required and optional dependencies, integration modes, and fallback mechanisms.

---

## Dependency Summary

| Component | Status | Purpose | Integration |
|-----------|--------|---------|-------------|
| **Python 3.8+** | Required | Core runtime | Built-in |
| **Claude SDK** | Required | AI agent functionality | `pip install anthropic` |
| **basedpyright-workflow** | Optional | Type checking & code quality | Copy directory OR pip install |
| **fixtest-workflow** | Optional | Test automation | Copy directory OR pip install |
| **bmad-workflow** | NOT Required | N/A | Standalone system |
| **.bmad-core/tasks/** | Required | Task guidance files | Create directory + add files |

---

## Required Dependencies

### 1. Python 3.8+
- **Purpose**: Core runtime environment
- **Installation**: Download from python.org or use system package manager
- **Verification**: `python --version`

### 2. Claude SDK
- **Purpose**: AI agent integration for automated story processing
- **Installation**: `pip install anthropic`
- **Alternative**: Use `--no-claude` flag for simulation mode

### 3. .bmad-core/tasks/ Directory
- **Purpose**: Task guidance files for SM, Dev, and QA agents
- **Location**: `.bmad-core/tasks/` in project root
- **Files Required**:
  - `create-next-story.md` (SM Agent)
  - `develop-story.md` (Dev Agent)
  - `review-story.md` (QA Agent)
- **Graceful Fallback**: System continues without these files but with reduced capabilities

---

## Optional Quality Gate Tools

### BasedPyright-Workflow

**Two integration modes:**

#### Option A: Directory Copy
```bash
cp -r /path/to/basedpyright-workflow /your/project/
```
- Includes pre-configured automation scripts
- Complete toolchain ready to use
- Location: `/your/project/basedpyright-workflow/`

#### Option B: Pip Installation
```bash
pip install basedpyright>=1.1.0 ruff>=0.1.0
```
- Standard Python dependency management
- Version controlled via requirements.txt
- Direct command-line access

**Fallback Behavior**:
- If unavailable: Logs warning, continues with WAIVED QA status
- Quality score: 20/30 points (partial credit)
- Story processing: Continues without quality gates

### Fixtest-Workflow

**Two integration modes:**

#### Option A: Directory Copy
```bash
cp -r /path/to/fixtest-workflow /your/project/
```
- Includes pytest and debugpy integration
- Pre-configured test automation
- Location: `/your/project/fixtest-workflow/`

#### Option B: Pip Installation
```bash
pip install pytest>=7.0.0 debugpy>=1.6.0
```
- Direct pytest access
- Debugpy for test debugging
- Standard Python testing ecosystem

**Fallback Behavior**:
- If unavailable: Logs warning, continues with WAIVED QA status
- Test automation: Skipped but workflow continues
- Story completion: Marked as complete (reduced QA)

---

## NOT Required Dependencies

### bmad-workflow
- **Status**: NOT required
- **Reason**: autoBMAD is a standalone system with its own orchestrator
- **Alternative**: Has built-in epic_driver.py for workflow management
- **Independence**: Self-contained SQLite state management

### External CI/CD Systems
- **Status**: NOT required
- **Reason**: Self-contained with progress tracking
- **State Management**: SQLite database (progress.db)
- **Persistence**: Automatic checkpointing between runs

---

## Installation Scenarios

### Scenario 1: Full Toolchain (Recommended)
```bash
# 1. Setup autoBMAD
cp -r /path/to/epic_automation /your/project/autoBMAD/

# 2. Copy quality workflows
cp -r /path/to/basedpyright-workflow /your/project/
cp -r /path/to/fixtest-workflow /your/project/

# 3. Create task guidance
mkdir -p .bmad-core/tasks
# Add task guidance files

# 4. Verify
python autoBMAD/epic_automation/epic_driver.py --help
```

### Scenario 2: Minimal Setup
```bash
# 1. Setup autoBMAD
cp -r /path/to/epic_automation /your/project/autoBMAD/

# 2. Install via pip
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 anthropic

# 3. Create task guidance
mkdir -p .bmad-core/tasks
# Add task guidance files

# 4. Verify
python autoBMAD/epic_automation/epic_driver.py --help
```

### Scenario 3: Development Mode (Skip Quality Gates)
```bash
# 1. Setup autoBMAD
cp -r /path/to/epic_automation /your/project/autoBMAD/

# 2. Create task guidance
mkdir -p .bmad-core/tasks
# Add task guidance files

# 3. Run with --skip-quality
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests
```

---

## Dependency Verification

### Check Required Dependencies
```bash
# Check Python
python --version

# Check Claude SDK
python -c "import anthropic; print('Claude SDK OK')"

# Check task guidance
ls -la .bmad-core/tasks/
```

### Check Optional Dependencies
```bash
# Check basedpyright-workflow
ls -d basedpyright-workflow 2>/dev/null && echo "BasedPyright-Workflow: FOUND" || echo "BasedPyright-Workflow: NOT FOUND"

# Check fixtest-workflow
ls -d fixtest-workflow 2>/dev/null && echo "Fixtest-Workflow: FOUND" || echo "Fixtest-Workflow: NOT FOUND"

# Check pip packages
pip list | grep -E "(basedpyright|ruff|pytest|debugpy)"
```

---

## Troubleshooting

### Issue: Quality Gate Tools Not Found
**Symptom**: Warning messages about missing basedpyright-workflow or fixtest-workflow

**Solutions**:
1. Copy workflow directories to project root
2. Install via pip: `pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0`
3. Use `--skip-quality` to bypass quality gates

### Issue: Task Guidance Not Found
**Symptom**: Warning about missing `.bmad-core/tasks/` directory

**Solution**:
```bash
mkdir -p .bmad-core/tasks
# Add create-next-story.md, develop-story.md, review-story.md
```

### Issue: Claude SDK Not Available
**Symptom**: Agent execution failures

**Solutions**:
1. Install: `pip install anthropic`
2. Use simulation mode: `--no-claude` flag

---

## Best Practices

1. **Use virtual environment**: Always use venv for dependency isolation
2. **Version control**: Pin dependencies in requirements.txt
3. **Graceful degradation**: System works even with reduced capabilities
4. **Document setup**: Include dependency setup in project README
5. **Regular updates**: Keep tools updated for security and features

---

## Dependency Graph

```
autoBMAD Epic Automation
├── Python 3.8+ (required)
├── Claude SDK (required)
│   └── anthropic package
├── .bmad-core/tasks/ (required)
│   ├── create-next-story.md
│   ├── develop-story.md
│   └── review-story.md
├── basedpyright-workflow (optional)
│   ├── basedpyright (via pip OR directory)
│   └── ruff (via pip OR directory)
└── fixtest-workflow (optional)
    ├── pytest (via pip OR directory)
    └── debugpy (via pip OR directory)

NOT REQUIRED:
└── bmad-workflow (standalone system)
```

# DocuSwarm Multi-Agent Document Orchestration System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.12.10+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**DocuSwarm** is an intelligent multi-agent orchestration system that automates BMAD (Breakthrough Method of Agile AI-driven Development) workflows through a dual-agent pattern with context isolation.

## 🎯 Project Overview

DocuSwarm 编排 5 个专业 Agent（Analyst、PM、UX Designer、Architect、PO），按照 BMAD 方法论创建全面的项目文档。

架构基于：
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - 多 Agent 工作流状态机
- **[claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk)** - Anthropic Claude Agent SDK
- **[Anthropic Claude](https://docs.anthropic.com/)** - 大上下文窗口 LLM（200K tokens）
- **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** - AI 驱动的敏捷开发方法论
- **上下文隔离** - 运行时访问控制 + 提示模板隔离 + 消息过滤

### Core Features
- **Dual-Agent Pattern** - Independent Agent (creates deliverables + questions) + Evaluator Agent (reviews with context isolation)
- **Sequential Pipeline** - 5 BMAD phases: Analyst → PM → UX → Architect → PO
- **Context Isolation** - Three-layer defense (runtime access control + prompt templates + message filtering)
- **State Persistence** - SQLite with WAL mode for checkpoint/resume
- **Session Management** - Stateless query-based SDK calls
- **Native Tool System** - Standard Tool Use Block pattern
- **Streaming** - AsyncGenerator-based message streaming

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Anthropic API Key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LeafLIU210/autoBMAD.git
   cd autoBMAD
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/macOS/WSL
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   ```bash
   # Create .env file
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   # Optional: Custom API Base URL
   # echo "ANTHROPIC_BASE_URL=https://custom-api-url/" >> .env
   ```

5. **Verify installation**
   ```bash
   python -m autoBMAD.docuswarm --help
   ```

### Basic Usage

Start a new pipeline with a context file:

```bash
python -m autoBMAD.docuswarm start --context docs/examples/project-requirements.md
source .venv/bin/activate && python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

Check pipeline status:

```bash
python -m autoBMAD.docuswarm status <pipeline-id>
```

Resume an interrupted pipeline:

```bash
python -m autoBMAD.docuswarm resume <pipeline-id>
```

## 📊 DocuSwarm 架构

DocuSwarm 通过**5个顺序 BMAD 阶段**处理工作流，采用双 Agent 模式：

```
┌─────────────────────────────────────────────────────────────┐
│                DOCUSWARM PIPELINE (Sequential)              │
└─────────────────────────────────────────────────────────────┘

Phase 1: Analysis
├── Analyst Node (Dual-Agent)
│   ├── Independent Agent
│   │   ├── Creates analyst report
│   │   └── Generates clarifying questions
│   └── Evaluator Agent
│       ├── Reviews report (context isolated)
│       └── Provides feedback + verdict
│
Phase 2: Planning
├── PM Node (Dual-Agent)
│   ├── Creates Product Requirements Document (PRD)
│   └── Evaluator reviews
├── UX Node (Dual-Agent)
│   ├── Creates UX Design
│   └── Evaluator reviews
│
Phase 3: Solutioning
├── Architect Node (Dual-Agent)
│   ├── Creates Architecture Document
│   └── Evaluator reviews
├── PO Node (Dual-Agent)
│   ├── Creates Epics + Stories
│   └── Evaluator reviews
│
State Management:
├── SQLite with WAL mode
├── LangGraph checkpointing
├── Optimistic locking
└── Automatic resume on failure
```

### Project Structure

```
autoBMAD/
├── autoBMAD/                    # Main source code
│   ├── docuswarm/              # DocuSwarm core system
│   │   ├── agents/             # Agent implementations (Independent + Evaluator)
│   │   ├── context/            # Context isolation (filter, audit, memory)
│   │   ├── llm/                # LLM integration (Claude SDK wrapper)
│   │   ├── node_execution/     # Node execution engine
│   │   ├── nodes/              # Node definitions (DualAgentNode)
│   │   ├── pipeline/           # Pipeline orchestration (LangGraph)
│   │   ├── prompts/            # Prompt templates (YAML + Markdown)
│   │   ├── storage/            # State persistence (SQLite + files)
│   │   ├── tools/              # Tool system (deliverables, context)
│   │   ├── utils/              # Utilities (logging, session IDs)
│   │   ├── tests/              # Unit and integration tests
│   │   ├── config.py           # Configuration management
│   │   ├── main.py             # CLI entry point
│   │   └── docuswarm.yaml      # Default YAML configuration
│   └── epic_automation/        # Epic automation system
├── nodes/                       # Node configurations (BMAD personas)
│   ├── analyst/                # Analyst node config
│   ├── pm/                     # PM node config
│   ├── ux/                     # UX node config
│   ├── architect/              # Architect node config
│   └── po/                     # PO node config
├── tests/                       # Additional test suite
├── docs/                        # Documentation & examples
│   └── examples/               # Example context files
├── scripts/                     # Utility scripts
├── claude_docs/                # AI-assisted development guides
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 📋 CLI Reference

```bash
python -m autoBMAD.docuswarm [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `-v, --verbose` | Enable verbose debug output | false |
| `--log-level` | Set logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `--log-file DIR` | Directory for log files | ./logs |
| `--json-log` | Use JSON format for log file output | false |
| `--version` | Show version and exit | - |

**Note**: Use `-v` or `--verbose` for detailed debug output. Useful for troubleshooting.

### Commands

#### `start` - Start a new pipeline

```bash
python -m autoBMAD.docuswarm start --context <file>
```

**Options:**
- `-c, --context FILE` - Path to the context file (required)

**Example:**
```bash
python -m autoBMAD.docuswarm start --context docs/examples/my-project.md
```

#### `status` - Show pipeline status

```bash
python -m autoBMAD.docuswarm status <pipeline-id>
```

**Example:**
```bash
python -m autoBMAD.docuswarm status abc123-def456
```

#### `resume` - Resume an interrupted pipeline

```bash
python -m autoBMAD.docuswarm resume <pipeline-id> [OPTIONS]
```

**Options:**
- `-n, --node NODE` - Restart from a specific node (analyst/pm/ux/architect/po)
- `-f, --force` - Force resume even if pipeline is running

**Examples:**
```bash
# Resume from last checkpoint
python -m autoBMAD.docuswarm resume abc123-def456

# Restart from specific node
python -m autoBMAD.docuswarm resume abc123-def456 --node pm
```

#### `list-pipelines` - List all pipelines

```bash
python -m autoBMAD.docuswarm list-pipelines [OPTIONS]
```

**Options:**
- `-s, --status STATUS` - Filter by status (pending/running/completed/failed/paused)

**Examples:**
```bash
# List all pipelines
python -m autoBMAD.docuswarm list-pipelines

# List only running pipelines
python -m autoBMAD.docuswarm list-pipelines --status running
```

#### `export` - Export deliverables

```bash
python -m autoBMAD.docuswarm export <pipeline-id> [OUTPUT_DIR] [OPTIONS]
```

**Options:**
- `-o, --output PATH` - Custom destination directory
- `--include-metadata` - Include _metadata.json in export

**Examples:**
```bash
# Export to current directory
python -m autoBMAD.docuswarm export abc123-def456

# Export to specific directory
python -m autoBMAD.docuswarm export abc123-def456 ./output --include-metadata
```

#### `questions` - List unanswered questions

```bash
python -m autoBMAD.docuswarm questions <pipeline-id> [OPTIONS]
```

**Options:**
- `-r, --run RUN_ID` - Query a specific run ID instead of latest

**Example:**
```bash
python -m autoBMAD.docuswarm questions abc123-def456
```

#### `answer` - Answer a question

```bash
python -m autoBMAD.docuswarm answer <question-id> [answer] [OPTIONS]
```

**Options:**
- `-t, --text TEXT` - Answer text (alternative to positional argument)

**Example:**
```bash
python -m autoBMAD.docuswarm answer abc123_analyst_0 "Yes, we should use PostgreSQL"
```

#### `cancel` - Cancel a running pipeline

```bash
python -m autoBMAD.docuswarm cancel <pipeline-id>
```

#### `cancel-all` - Cancel all pipelines

```bash
python -m autoBMAD.docuswarm cancel-all [OPTIONS]
```

**Options:**
- `--status STATUS` - Only cancel pipelines with this status
- `--confirm` - Skip confirmation prompt

#### `clean` - Delete pipelines from database

```bash
python -m autoBMAD.docuswarm clean [OPTIONS]
```

**Options:**
- `--status STATUS` - Only delete pipelines with this status
- `--older-than-days N` - Only delete pipelines older than N days
- `--confirm` - Skip confirmation prompt

**Examples:**
```bash
# Delete all cancelled pipelines
python -m autoBMAD.docuswarm clean --status cancelled --confirm

# Delete completed pipelines older than 7 days
python -m autoBMAD.docuswarm clean --status completed --older-than-days 7 --confirm
```

## ⚙️ Configuration

### pyproject.toml

```toml
[tool.basedpyright]
pythonVersion = "3.12.10"

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "B", "I", "W", "C4", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--verbose"
```

### Environment Variables

Create a `.env` file in the project root:

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

### YAML Configuration

You can also configure DocuSwarm via `autoBMAD/docuswarm/docuswarm.yaml`:

```yaml
# API Configuration
base_url: https://api.anthropic.com/v1/

# Database Configuration
db_path: docuswarm.db

# Output Configuration
output_dir: output

# Logging Configuration
log_level: INFO

# Pipeline Configuration
max_iterations: 100
```

**Configuration Priority**: Environment Variables > YAML Config > Default Values

## 🔄 Common Workflows

### Full Pipeline Execution

```bash
# 1. Start pipeline
python -m autoBMAD.docuswarm start --context docs/examples/project.md

# 2. Check status (repeat as needed)
python -m autoBMAD.docuswarm status <pipeline-id>

# 3. Answer any blocking questions
python -m autoBMAD.docuswarm questions <pipeline-id>
python -m autoBMAD.docuswarm answer <question-id> "Your answer"

# 4. Export results when complete
python -m autoBMAD.docuswarm export <pipeline-id> ./output --include-metadata
```

### Pipeline Management

```bash
# List all pipelines
python -m autoBMAD.docuswarm list-pipelines

# Cancel a running pipeline
python -m autoBMAD.docuswarm cancel <pipeline-id>

# Cancel all pending pipelines
python -m autoBMAD.docuswarm cancel-all --status pending --confirm

# Clean up old pipelines
python -m autoBMAD.docuswarm clean --status completed --older-than-days 7 --confirm
```

### Development Workflow

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=autoBMAD.docuswarm --cov-report=html

# Quality checks
ruff check autoBMAD/
basedpyright autoBMAD/

# Format code
ruff format autoBMAD/
```

## 🔍 Troubleshooting

### Pipeline Issues

**Pipeline stuck or failed:**
```bash
# Check status
python -m autoBMAD.docuswarm status <pipeline-id>

# Resume from last checkpoint
python -m autoBMAD.docuswarm resume <pipeline-id>

# Or restart from specific node
python -m autoBMAD.docuswarm resume <pipeline-id> --node analyst --force
```

**Quality Gates Fail:**

```bash
# Check BasedPyRight errors
basedpyright autoBMAD/ --output-format=json

# Check Ruff errors
ruff check autoBMAD/ --output-format=json

# Fix all issues automatically
ruff check --fix autoBMAD/
```

**Test Failures:**

```bash
# Run tests with verbose output
pytest tests/ -v --tb=long

# Debug specific test
pytest tests/test_specific.py -s --pdb
```

### Common Errors

**API Key Error:**
```
ConfigurationError: ANTHROPIC_API_KEY is required
```
**Solution:**
- Ensure `.env` file exists with `ANTHROPIC_API_KEY=your_key`
- Verify the API key is valid and not expired

**Pipeline Not Found:**
```
Error: Pipeline not found: abc123xyz
```
**Solution:**
- Use `list-pipelines` to see all available pipelines
- Check the pipeline ID spelling (case-sensitive)
- Verify the database file exists: `ls docuswarm.db`

**Database Locked:**
```
sqlite3.OperationalError: database is locked
```
**Solution:**
- Ensure only one process is accessing the database
- Enable WAL mode: `sqlite3 docuswarm.db "PRAGMA journal_mode=WAL;"`

### Installation Issues

```bash
# Recreate virtual environment (Windows)
.venv\Scripts\deactivate
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Recreate virtual environment (Linux/macOS)
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📚 Documentation

### User Documentation
- [Setup Guide](SETUP.md) - Installation and setup
- [Claude Code Guide](CLAUDE.md) - AI-assisted development guide
- [DocuSwarm Detailed Guide](autoBMAD/docuswarm/README.md) - Complete usage guide
- [Configuration Guide](autoBMAD/docuswarm/CONFIGURATION.md) - API and configuration details

### Development Guides
- [Core Principles](claude_docs/core_principles.md) - DRY, KISS, YAGNI, Occam's Razor
- [Development Rules](claude_docs/development_rules.md) - Coding standards
- [Testing Guide](claude_docs/testing_guide.md) - Testing practices
- [Quality Assurance](claude_docs/quality_assurance.md) - QA processes
- [AI Workflow](claude_docs/ai_workflow.md) - Three-phase AI workflow

### DocuSwarm Internal Documentation
- [DocuSwarm CLI Research Report](autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md)
- [DocuSwarm TDD Refactor Plan](autoBMAD/docuswarm/docs/DocuSwarm-TDD-Refactor-Plan.md)
- [Pipeline CurrentNode Analysis](autoBMAD/docuswarm/docs/DocuSwarm流水线CurrentNode问题分析与操作指引.md)

## 🤝 Contributing

1. Follow the [Development Rules](claude_docs/development_rules.md)
2. Run quality gates before submitting
3. Add tests for new features
4. Update documentation

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 创建 issue 提交 bug 或功能请求
- 查看 [quality_assurance.md](claude_docs/quality_assurance.md) 了解质量保证流程
- 查看 [workflow_tools.md](claude_docs/workflow_tools.md) 了解 autoBMAD 工作流

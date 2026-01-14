# autoBMAD Epic Automation System

**Version**: 3.0  
**Date**: 2026-01-14  
**Status**: Production Ready

A comprehensive automation system for the BMAD (Breakthrough Method of Agile AI-driven Development) workflow. This tool processes epic markdown files through a complete 5-phase workflow with state-driven execution, quality gates, and test automation.

## Overview

autoBMAD Epic Automation is a self-contained Python automation engine that enables teams to quickly set up and use the BMAD methodology in their projects. It features a five-layer architecture with Controllers, Agents, Core infrastructure, and persistent State management.

### System Architecture

- **Five-Layer Architecture**: Epic Driver → Controllers → Agents → Core → State & Logging
- **State-Driven Workflow**: Story status from markdown drives execution decisions
- **Controller Pattern**: Specialized controllers for SM, DevQA, Quality Gates, and Pytest
- **SQLite Persistence**: Progress tracking with WAL mode and optimistic locking
- **Dual-Write Logging**: Console and file logging with structured output

### Key Features

- **Complete 5-Phase Workflow**: SM-Dev-QA cycle followed by quality gates and test automation
- **AI-Powered Story Creation**: SM Agent uses Claude Agent SDK to create stories from epic documents
- **Claude Agent SDK Integration**: Direct SDK integration with `permission_mode="bypassPermissions"`
- **Quality Gates**: Basedpyright type checking and Ruff linting with auto-fix capabilities
- **Test Automation**: Pytest execution with Debugpy integration for persistent failures
- **CLI Interface**: Simple command-line interface with flexible options
- **Retry Logic**: Configurable retry attempts for failed stories (3 for quality, 5 for tests)
- **Verbose Logging**: Detailed logging for debugging and monitoring
- **Portable**: Self-contained solution requiring only Python and the Claude SDK
- **No Complex Setup**: Copy the folder to your project and start using immediately

## Quick Start

### Installation with Quality Gate Dependencies

```bash
# Clone or copy the project
git clone <your-repo>
cd <your-project>

# Create virtual environment (recommended)
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate

# Install all dependencies including quality gate tools
pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio

# Configure environment variables
# Windows PowerShell:
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/macOS:
export ANTHROPIC_API_KEY="your_api_key_here"

# Verify installation
python -c "import claude_agent_sdk; print('Claude Agent SDK ready')"
basedpyright --version
ruff --version
pytest --version
```

### Basic Usage with Complete Workflow

```bash
# Activate virtual environment
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/macOS

# Full workflow with all phases (SM-Dev-QA + Quality Gates + Tests)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose

# Skip quality gates (for faster development)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --verbose

# Skip test automation (for quick validation)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests --verbose

# Skip both quality gates and tests (fastest)
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests --verbose
```

### Windows PowerShell Example

```powershell
# Set environment and run
$env:ANTHROPIC_API_KEY="your_api_key"; $env:PYTHONPATH="d:\GITHUB\pytQt_template"; python d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py docs\epics\epic-1-core-algorithm-foundation.md --verbose --max-iterations 2 --source-dir src --test-dir tests
```

## Complete Workflow

The system executes epics through 5 distinct phases:

```
┌─────────────────────────────────────────────────────────────┐
│                    EPIC PROCESSING                          │
└─────────────────────────────────────────────────────────────┘

Phase 1: SM-Dev-QA Cycle (Stories 001-004 foundation)
├── Story Creation (SM Agent)
├── Implementation (Dev Agent)
└── Validation (QA Agent)
         ↓
Phase 2: Quality Gates (Story 002)
├── Basedpyright Type Checking
├── Ruff Linting with Auto-fix
└── Max 3 Retry Attempts
         ↓
Phase 3: Test Automation (Story 003)
├── Pytest Test Execution
├── Debugpy for Persistent Failures
└── Max 5 Retry Attempts
         ↓
Phase 4: Orchestration (Story 004)
├── Epic Driver Manages Complete Workflow
├── Phase-gated Execution
└── Progress Tracking
         ↓
Phase 5: Documentation & Testing (Story 005)
├── Comprehensive Documentation
├── Integration Tests
└── User Guidance
```

## Quality Gates

Quality gates ensure code quality after the SM-Dev-QA cycle completes.

### Basedpyright Type Checking

- **Purpose**: Static type checking to catch type-related errors
- **Retry Logic**: Up to 3 automatic retry attempts
- **Auto-fix**: Ruff can fix many issues automatically
- **Configuration**: Configured via `pyproject.toml`

```bash
# Run with quality gates (default)
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md

# Check only quality gates
cd basedpyright-workflow
basedpyright-workflow check
```

### Ruff Linting

- **Purpose**: Fast Python linting with auto-fix capabilities
- **Coverage**: PEP 8, complexity, imports, and more
- **Auto-fix**: Automatically fixes fixable issues
- **Performance**: Very fast, mostly I/O bound

```bash
# Check and auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

### CLI Quality Gate Options

- `--skip-quality`: Bypass quality gates entirely
- `--max-iterations`: Control retry attempts (default: 3)

## Test Automation

Test automation runs after quality gates complete successfully.

### Pytest Execution

- **Purpose**: Run all tests in the test suite
- **Coverage**: Unit, integration, and E2E tests
- **Reporting**: Detailed test reports with failure analysis

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_my_feature.py -v
```

### Debugpy Integration

- **Purpose**: Debug persistent test failures
- **Timeout**: 300 seconds (5 minutes) per debug session
- **Integration**: Automatic activation for failing tests

```bash
# Debugpy is automatically used for persistent failures
# No manual configuration required

# Run tests with debugpy enabled
pytest tests/ --pdb
```

### CLI Test Automation Options

- `--skip-tests`: Bypass test automation
- `--test-dir`: Specify custom test directory (default: "tests")

## Installation

### Requirements

#### Core Requirements
- **Python 3.12+**: Required for latest type hints and async features
- **Claude Agent SDK** (`claude-agent-sdk>=0.1.0`): AI agent functionality
- **AnyIO**: Async framework for portable async/await code
- **Loguru**: Advanced logging with better formatting

#### Quality Gate Tools (Recommended)
- **BasedPyright** (`basedpyright>=1.1.0`): Advanced type checking
- **Ruff** (`ruff>=0.1.0`): Fast Python linter and formatter
- **Pytest** (`pytest>=7.0.0`): Testing framework
- **Debugpy** (`debugpy>=1.6.0`): Python debugger for VS Code

#### Infrastructure
- **SQLite3**: Built-in Python module for state persistence
- **Progress.db**: Automatically created SQLite database with WAL mode
- **Logs Directory**: Automatically created for log file storage

### Setup Steps

1. **Copy the epic_automation folder** to your project directory:
   ```bash
   cp -r /path/to/epic_automation /your/project/
   ```

2. **Ensure quality gate tools are available** (one of the following):
   ```bash
   # Option A: Copy quality gate tools to your project
   cp -r /path/to/basedpyright-workflow /your/project/
   cp -r /path/to/fixtest-workflow /your/project/

   # Option B: Install dependencies manually
   pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0
   ```

3. **Install Claude Agent SDK**:
   ```bash
   pip install claude-agent-sdk
   ```

4. **Configure environment variables**:
   ```bash
   # Windows PowerShell:
   $env:ANTHROPIC_API_KEY="your_api_key_here"

   # Linux/macOS:
   export ANTHROPIC_API_KEY="your_api_key_here"
   ```

5. **Create task guidance files** in `.bmad-core/tasks/`:
   ```bash
   mkdir -p .bmad-core/tasks
   # Copy the task guidance files (see Task Guidance Files section below)
   ```

6. **Verify the setup** by running the help command:
   ```bash
   cd /your/project
   source venv/Scripts/activate
   PYTHONPATH=autoBMAD python -m epic_automation.epic_driver --help
   ```

### Configuration

No additional configuration required! The tool automatically:
- Locates task guidance files in `.bmad-core/tasks/`
- Parses epic markdown files
- Manages state between runs
- Handles logging and error reporting

### Task Guidance Files

The `.bmad-core/tasks/` directory contains task guidance files that customize the behavior of SM, Dev, and QA agents. Create these files with the following content:

#### `.bmad-core/tasks/create-next-story.md` (SM Agent)
```markdown
# Story Creation Guidance

## Story Structure Requirements
- Clear user story format (As a... I want... So that...)
- Comprehensive acceptance criteria
- Detailed task breakdown
- Definition of done

## Story Quality Standards
- Stories should be atomic and focused
- Acceptance criteria should be testable
- Technical details should be documented
```

#### `.bmad-core/tasks/develop-story.md` (Dev Agent)
```markdown
# Development Guidance

## Implementation Standards
- Follow Ralph's four principles (DRY, KISS, YAGNI, Occam's Razor)
- Write clean, maintainable code
- Include comprehensive tests
- Document all changes

## Code Quality Requirements
- Type hints for all functions
- Docstrings for public APIs
- Unit test coverage > 80%
- No linting errors
```

#### `.bmad-core/tasks/review-story.md` (QA Agent)
```markdown
# QA Review Guidance

## Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Type checking passes
- [ ] No linting errors
- [ ] Documentation is complete
- [ ] Security considerations addressed

## Quality Gates
- BasedPyright: 0 errors, minimal warnings
- Fixtest: All tests pass
- Code coverage: > 80%
```

### Dependencies

**Required Dependencies:**
- **Python 3.12+**: Core runtime environment
- **claude-agent-sdk>=0.1.0**: For AI agent functionality (SM, Dev, QA agents)
- **anyio**: Async framework (replaced trio for better portability)
- **loguru**: Advanced logging with structured output

**Quality Gate Tools** (Optional but Recommended):
- **basedpyright>=1.1.0**: Advanced type checking with better performance than mypy
- **ruff>=0.1.0**: Fast Python linter and formatter (replaces flake8, black)
- **pytest>=7.0.0**: Testing framework with rich assertion introspection
- **debugpy>=1.6.0**: Python debugger for VS Code integration

**Infrastructure** (Built-in):
- **sqlite3**: Built-in Python module for state persistence
- **asyncio**: Built-in async framework
- **pathlib**: Built-in path manipulation

### Dependency Installation

Install all required dependencies:

```bash
# Install all dependencies at once (recommended)
pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio

# Or install separately
pip install claude-agent-sdk>=0.1.0  # Core AI functionality
pip install basedpyright>=1.1.0 ruff>=0.1.0  # Quality gates
pip install pytest>=7.0.0 debugpy>=1.6.0  # Testing
pip install loguru anyio  # Utilities
```

**Note**: The `claude-agent-sdk` package is **required** for all agent functionality (SM, Dev, QA).

### Graceful Fallback

If quality gate tools are not available, the system will:
1. Log a warning about missing tools
2. Continue with reduced QA capabilities
3. Mark QA status as "WAIVED"
4. Provide partial credit for QA score
5. Allow the workflow to continue

This ensures the system can still be used for development even without the full toolchain.
## Usage

### Basic Usage

Process an epic file with default settings:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

### CLI Options

#### Positional Arguments

- `epic_path` (required): Path to the epic markdown file

#### Optional Flags

- `--max-iterations N`: Maximum retry attempts for failed stories (default: 3)
- `--retry-failed`: Enable automatic retry of failed stories
- `--verbose`: Enable detailed logging output
- `--concurrent`: Process stories in parallel (experimental feature)
- `--no-claude`: Disable Claude Code CLI integration (use simulation mode)
- `--source-dir DIR`: Source code directory for QA checks (default: "src")
- `--test-dir DIR`: Test directory for QA checks (default: "tests")

#### Quality Gate and Test Options

- `--skip-quality`: Skip code quality gates (basedpyright and ruff)
- `--skip-tests`: Skip test automation (pytest)

### Usage Examples

#### Example 1: Complete Workflow with Quality Gates

```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

This will process all stories in `my-epic.md` through the complete 5-phase workflow:
- Phase 1: SM-Dev-QA cycle for all stories (state-driven execution)
- Phase 2: Quality gates (Ruff linting + BasedPyright type checking)
- Phase 3: Test automation (Pytest execution with batch processing)
- Max 3 retry cycles for quality gates
- Max 5 retry cycles for test automation
- Results saved to `progress.db` SQLite database
- Logs written to console and file (if enabled)

#### Example 2: Skip Quality Gates (Faster Development)

```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --verbose
```

Processes stories through SM-Dev-QA cycle and test automation, but skips quality gates for faster iteration during development. Useful when:
- Prototyping new features
- Working on experimental code
- Quality tools not installed
- Need quick feedback on functionality

#### Example 3: Skip Test Automation (Quick Validation)

```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests --verbose
```

Processes stories through SM-Dev-QA cycle and quality gates, but skips test automation for quick validation without running tests. Useful when:
- Validating code quality before tests
- Tests are broken or incomplete
- Need quick type checking and linting feedback
- Working on documentation-only changes

#### Example 4: Skip Both Quality Gates and Tests

```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests --verbose
```

Processes only the SM-Dev-QA cycle, skipping both quality gates and test automation for maximum speed during initial development. Useful when:
- Creating initial story implementations
- Rapid prototyping
- Quality tools not available
- Focus on core functionality first

#### Example 5: Custom Directories and Max Iterations

```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --source-dir src --test-dir tests --max-iterations 5 --verbose
```

Customizes source and test directories while increasing retry attempts. This configuration:
- Uses `src/` for source code quality checks
- Uses `tests/` for test discovery
- Allows up to 5 retry cycles for quality gates
- Provides detailed logging output
- Saves complete execution history to database

## Architecture

### Component Overview

The BMAD Epic Automation system follows a **Five-Layer Architecture** pattern:

```
┌─────────────────────────────────────┐
│   Epic Driver (Orchestration)      │  ← Entry point + workflow coordination
├─────────────────────────────────────┤
│   Controllers (Process Control)    │  ← Business workflow orchestration
├─────────────────────────────────────┤
│   Agents (Business Logic)          │  ← Core business operations
├─────────────────────────────────────┤
│   Core (Infrastructure)            │  ← SDK executor, cancellation manager
├─────────────────────────────────────┤
│   State & Logging                  │  ← StateManager, LogManager, Database
└─────────────────────────────────────┘
```

### Directory Structure

```
autoBMAD/epic_automation/
├── epic_driver.py           # Main orchestrator (2601 lines)
├── state_manager.py         # State persistence (SQLite-based)
├── sdk_wrapper.py           # SafeClaudeSDK wrapper
├── log_manager.py           # Dual-write logging system
├── init_db.py               # Database initialization
├── doc_parser.py            # Epic/story document parsing
├── spec_state_manager.py    # Specification state tracking
├── test_automation_agent.py # Test execution agent
│
├── controllers/             # Workflow Controllers
│   ├── base_controller.py          # Base controller class
│   ├── sm_controller.py            # Story Management coordination
│   ├── devqa_controller.py         # Dev-QA cycle coordination
│   ├── quality_check_controller.py # Quality gate controller
│   ├── pytest_controller.py        # Test automation controller
│   └── quality_controller.py       # Quality orchestration
│
├── agents/                  # Business Logic Agents
│   ├── base_agent.py               # Base agent class
│   ├── sm_agent.py                 # Story creation from epics
│   ├── dev_agent.py                # Development implementation
│   ├── qa_agent.py                 # Quality assurance validation
│   ├── state_agent.py              # Status parsing and state management
│   ├── status_update_agent.py      # Story status updates
│   ├── quality_agents.py           # Ruff, BasedPyright, Pytest agents
│   ├── pytest_batch_executor.py    # Pytest batch execution
│   ├── config.py                   # Agent configuration
│   └── sdk_helper.py               # SDK utilities
│
├── core/                    # Core Infrastructure
│   ├── sdk_executor.py             # Async SDK executor
│   ├── sdk_result.py               # SDK result types
│   ├── cancellation_manager.py     # Cancellation handling
│   └── API_USAGE.md                # Core API documentation
│
├── errors/                  # Error Handling
│   └── quality_errors_*.json       # Quality gate error reports
│
├── monitoring/              # Performance Monitoring
│   └── resource_monitor.py         # Resource usage monitoring
│
├── reports/                 # Quality Reports
│   └── CLAUDE_AGENT_SDK_REPORT.md
│
├── architecture/            # Architecture Documentation
│   ├── architecture.md             # Brownfield architecture document
│   ├── brownfield-architecture.md  # Current implementation details
│   └── source-tree.md              # Complete source tree
│
├── agentdocs/              # Claude Agent SDK Documentation
│   └── (SDK integration guides)
│
└── logs/                   # Log Files
    └── (Timestamped log files)
```

### Key Features (v3.0)

#### Five-Layer Architecture
- **Epic Driver Layer**: Central orchestrator for complete workflow pipeline
- **Controllers Layer**: Business workflow orchestration (SM, DevQA, Quality, Pytest)
- **Agents Layer**: Core business logic with specialized agents
- **Core Layer**: Infrastructure components (SDK executor, cancellation manager)
- **State & Logging Layer**: Persistence and monitoring

#### SM Agent Enhancements

**New Features:**
- ✅ **Claude Agent SDK Integration**: Direct SDK calls replace hardcoded story creation
- ✅ **Async Story Creation**: `create_stories_from_epic()` method for non-blocking story generation
- ✅ **Epic Parsing**: Built-in regex-based story ID extraction from epic documents
- ✅ **Smart Prompting**: Automatic prompt construction with proper formatting
- ✅ **Permission Management**: Automatic `bypassPermissions` mode for seamless execution

**Removed Features:**
- ❌ `_create_missing_story()` - Hardcoded template-based story creation (replaced by AI)
- ❌ `_extract_story_section_from_epic()` - Manual content extraction (replaced by AI)
- ❌ **Backward Compatibility**: All fallback mechanisms removed per Occam's Razor principle

**Benefits:**
- 🎯 More accurate and context-aware story generation
- 🎯 Follows BMAD methodology more closely (SM Agent owns story creation)
- 🎯 Simpler codebase (fewer methods, clearer responsibilities)
- 🎯 Better adherence to Occam's Razor (no unnecessary complexity)

#### Controllers Architecture
- **SMController**: Orchestrates story creation phase
- **DevQaController**: Manages Dev-QA cycle with state-driven workflow
- **QualityCheckController**: Executes quality gates (Ruff, BasedPyright)
- **PytestController**: Handles test automation with retry logic

#### State Management Improvements
- **SQLite with WAL Mode**: Fast concurrent read/write operations
- **Optimistic Locking**: Version-based concurrency control
- **State-Driven Workflow**: Story status from markdown drives execution
- **Dual-Write Logging**: Console and file logging simultaneously

#### Quality Gate Integration
- **Ruff Agent**: Fast linting with auto-fix capabilities
- **BasedPyright Agent**: Advanced type checking
- **Pytest Agent**: Comprehensive test execution
- **Batch Executor**: Efficient parallel test execution
- **Error Reporting**: JSON-based error summaries with recommendations

### Project Structure

```
project/
├── autoBMAD/epic_automation/     # Main automation package
│   ├── epic_driver.py            # CLI entry point (2601 lines)
│   ├── state_manager.py          # State persistence (SQLite)
│   ├── sdk_wrapper.py            # SafeClaudeSDK wrapper
│   ├── log_manager.py            # Dual-write logging
│   ├── controllers/              # Workflow controllers
│   ├── agents/                   # Business logic agents
│   ├── core/                     # Infrastructure components
│   ├── errors/                   # Error handling
│   ├── monitoring/               # Performance monitoring
│   ├── reports/                  # Quality reports
│   ├── architecture/             # Architecture docs
│   ├── agentdocs/               # SDK documentation
│   ├── logs/                    # Log files
│   ├── README.md                # This file
│   └── SETUP.md                 # Setup guide
├── .bmad-core/tasks/             # Task guidance files
│   ├── create-next-story.md     # SM agent guidance
│   ├── develop-story.md         # Dev agent guidance
│   └── review-story.md          # QA agent guidance
├── docs/epics/                   # Epic documents
│   ├── my-epic.md               # Your epic files
│   └── stories/                 # Story documents
├── progress.db                   # State database (SQLite)
└── pyproject.toml               # Project configuration
```

### How It Works

#### 1. Initialization Phase
- `epic_driver.py` parses CLI arguments
- Initializes LogManager with dual-write logging
- Sets up StateManager with SQLite database
- Configures SafeClaudeSDK wrapper
- Initializes controllers and agents

#### 2. Epic Parsing Phase
- Reads epic markdown file
- Extracts story references using regex patterns
- Resolves story file paths with fallback mechanisms
- Parses story status using StateAgent
- Validates epic structure and dependencies

#### 3. Story Processing Loop
For each story, state-driven workflow:

**State-Driven Execution**:
- **Draft/Ready for SM**: SMController executes story creation
- **Ready for Development**: DevQaController starts Dev-QA cycle
- **In Progress**: DevAgent implements the story
- **Ready for Review**: QAAgent validates implementation
- **Ready for Done/Done**: Triggers quality gates and test automation

**Dev-QA Cycle**:
1. StateAgent parses current status from story markdown
2. Based on status, execute Dev or QA phase
3. Agent updates story through SDK
4. StatusUpdateAgent verifies update success
5. Loop continues until "Ready for Done" or "Done"

#### 4. Quality Gates Phase
Executed after story reaches "Ready for Done":

**Phase 1: Ruff Linting**
- Runs Ruff check with auto-fix
- Collects linting errors
- Fixes auto-fixable issues
- Max 3 retry cycles

**Phase 2: BasedPyright Type Checking**
- Runs type checking
- Collects type errors
- Agent attempts fixes through SDK
- Max 3 retry cycles

**Phase 3: Ruff Format**
- Applies code formatting
- Ensures consistent style

**Error Handling**:
- Errors saved to JSON files in `errors/` directory
- Quality warnings if max cycles exceeded with residual errors
- Summary report generated

#### 5. Test Automation Phase
Executed after quality gates pass:

**Test Execution**:
- PytestController runs test suite
- Batch execution for efficiency
- Collects test results and failures
- Max 5 retry cycles

**Failure Handling**:
- TestAutomationAgent fixes persistent failures
- Uses Claude SDK to analyze and fix
- Debugpy integration for complex failures

#### 6. State Management
`state_manager.py` maintains persistent state:

**Database Schema** (SQLite with WAL mode):
- Story execution records
- Phase completion status
- Iteration counts and timestamps
- Error history and recovery attempts

**Features**:
- Optimistic locking (version-based)
- Connection pooling
- Transaction management
- Automatic recovery from crashes

#### 7. Logging and Monitoring

**LogManager** (`log_manager.py`):
- Dual-write: console + file
- Timestamped log files
- Structured logging
- Error categorization

**ResourceMonitor** (`monitoring/resource_monitor.py`):
- CPU and memory usage tracking
- Performance metrics collection
- Resource usage reports

#### 8. Reporting
- Summary statistics for epic execution
- Detailed phase-by-phase logs (with `--verbose`)
- Quality gate error reports (JSON)
- Test execution results
- Performance metrics

### Agent Roles

#### Agents Layer

**Story Master (SM) Agent** (`agents/sm_agent.py` - 30.9KB)
- **Epic Analysis**: Extracts story IDs from epic documents using regex patterns
- **AI Story Creation**: Uses Claude Agent SDK to generate complete story documents
- **SDK Integration**: Direct integration with `claude_agent_sdk.query()` and `ClaudeAgentOptions`
- **Automatic Prompt Generation**: Builds prompts with proper formatting
- **Permission Handling**: Automatically sets `permission_mode="bypassPermissions"`
- **Story Refinement**: Validates and refines story requirements
- **Task Breakdown**: Creates comprehensive task lists

**Development (Dev) Agent** (`agents/dev_agent.py` - 16.7KB)
- **Code Implementation**: Implements stories according to specifications
- **Test Writing**: Creates unit and integration tests
- **Documentation**: Updates code and story documentation
- **Standards Compliance**: Follows coding best practices
- **Progress Tracking**: Updates story status through SDK

**Quality Assurance (QA) Agent** (`agents/qa_agent.py` - 6.5KB)
- **Code Review**: Reviews implementation quality
- **Acceptance Validation**: Validates against acceptance criteria
- **Standards Check**: Verifies coding standards compliance
- **Test Validation**: Ensures test coverage and quality
- **Feedback Generation**: Provides detailed feedback

**State Agent** (`agents/state_agent.py` - 12.4KB)
- **Status Parsing**: Extracts status from story markdown files
- **AI-based Parsing**: Uses Claude SDK for intelligent parsing
- **Regex Fallback**: Falls back to regex for performance
- **State Mapping**: Maps core status to processing status
- **Caching**: Implements parsing cache for efficiency

**Status Update Agent** (`agents/status_update_agent.py` - 14.5KB)
- **Status Updates**: Updates story status through SDK
- **Markdown Updates**: Modifies story markdown files
- **Validation**: Validates status transitions
- **Error Handling**: Robust error handling and recovery

**Quality Agents** (`agents/quality_agents.py` - 36.3KB)
- **Ruff Agent**: Fast linting with auto-fix
- **BasedPyright Agent**: Advanced type checking
- **Pytest Agent**: Test execution with detailed reporting
- **Error Aggregation**: Collects and reports errors
- **Retry Logic**: Intelligent retry with backoff

**Pytest Batch Executor** (`agents/pytest_batch_executor.py` - 10.6KB)
- **Batch Execution**: Runs multiple test files efficiently
- **Parallel Execution**: Supports parallel test runs
- **Result Aggregation**: Combines results from all tests
- **Progress Tracking**: Real-time progress updates

## Troubleshooting

### Common Issues

#### Issue: "Epic file not found"

**Error Message**:
```
ERROR - Epic file not found: docs/epics/my-epic.md
```

**Solution**:
- Verify the file path is correct
- Ensure the file exists before running
- Use an absolute path if relative paths don't work

#### Issue: "Tasks directory not found"

**Error Message**:
```
WARNING - Tasks directory not found: .bmad-core/tasks
```

**Solution**:
- Create the directory: `mkdir -p .bmad-core/tasks`
- Add task guidance files (see "Task Guidance Files" section above)
- The system will continue without them but with reduced capabilities

#### Issue: "Quality gate tools not found"

**Error Message**:
```
WARNING - Quality gate tools not available: basedpyright, ruff, or pytest not found
```

**Solution**:
- **Option A**: Install all tools at once:
  ```bash
  pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0
  ```
- **Option B**: Use `--skip-quality` or `--skip-tests` flags to bypass:
  ```bash
  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests
  ```
- **Option C**: Install individually:
  ```bash
  pip install basedpyright  # For type checking
  pip install ruff          # For linting
  pip install pytest        # For testing
  ```

Note: The system has graceful fallback - it will continue even without these tools but with reduced QA capabilities.

#### Issue: "Failed to import agent classes"

**Error Message**:
```
ERROR - Failed to import agent classes: No module named 'autoBMAD'
```

**Solution**:
- Set PYTHONPATH correctly:
  ```bash
  # From project root
  export PYTHONPATH=.  # On Linux/macOS
  $env:PYTHONPATH="."  # On Windows PowerShell
  ```
- Or use absolute paths:
  ```bash
  export PYTHONPATH=/path/to/your/project
  ```
- Or run from project root:
  ```bash
  cd /path/to/your/project
  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
  ```
- Verify all dependencies are installed:
  ```bash
  pip list | grep -E "claude-agent-sdk|loguru|anyio"
  ```

#### Issue: Stories not being processed

**Symptoms**:
- No stories found in epic
- Stories exist but aren't being executed

**Solution**:
- Verify epic file contains properly formatted story references
- Use the pattern: `[Story xxx: ...](path)`
- Check that story files actually exist at referenced paths

#### Issue: QA failures on first attempt

**Symptoms**:
- Stories fail QA and stop processing

**Solution**:
- Use `--retry-failed` flag to enable automatic retries
- Increase `--max-iterations` for more attempts
- Use `--verbose` to see detailed QA feedback

#### Issue: Max iterations reached

**Error Message**:
```
ERROR - Max iterations (3) reached for story-path.md
```

**Solution**:
- Increase `--max-iterations` value
- Check QA feedback to fix underlying issues
- Review story requirements for clarity

#### Issue: Database errors or state corruption

**Symptoms**:
- SQLite errors ("database is locked", "database disk image is malformed")
- Inconsistent story states
- Progress not being saved

**Solution**:
- **Reset state database**:
  ```bash
  # Backup current state
  cp progress.db progress.db.backup
  
  # Remove corrupted database
  rm progress.db
  
  # System will create new database on next run
  ```
- **Check database integrity**:
  ```bash
  sqlite3 progress.db "PRAGMA integrity_check;"
  ```
- **Enable WAL mode** (if not already enabled):
  ```bash
  sqlite3 progress.db "PRAGMA journal_mode=WAL;"
  ```
- **Check file permissions**:
  ```bash
  ls -l progress.db  # On Linux/macOS
  icacls progress.db  # On Windows
  ```

#### Issue: SDK timeout or connection errors

**Error Message**:
```
ERROR - SDK execution timeout after 300 seconds
ERROR - Failed to connect to Claude Agent SDK
```

**Solution**:
- Verify API key is set:
  ```bash
  echo $ANTHROPIC_API_KEY  # On Linux/macOS
  echo $env:ANTHROPIC_API_KEY  # On Windows PowerShell
  ```
- Check internet connection
- Increase timeout in `epic_driver.py` if needed
- Check SDK version:
  ```bash
  pip show claude-agent-sdk
  ```
- Reinstall SDK:
  ```bash
  pip uninstall claude-agent-sdk
  pip install claude-agent-sdk>=0.1.0
  ```

#### Issue: Log files accumulating

**Symptoms**:
- Large number of log files in `logs/` directory
- Disk space issues

**Solution**:
- Clean up old logs manually:
  ```bash
  # Keep only last 7 days
  find autoBMAD/epic_automation/logs/ -name "*.log" -mtime +7 -delete
  ```
- Disable file logging (edit `epic_driver.py`):
  ```python
  log_manager = LogManager(create_log_file=False)  # Only console output
  ```
- Implement log rotation (future enhancement)

#### Issue: Concurrent processing not available

**Warning Message**:
```
WARNING - Concurrent processing is experimental and not yet implemented
```

**Solution**:
- This is expected behavior - the feature is not yet implemented
- Remove the `--concurrent` flag for now
- Stories will be processed sequentially (current implementation)
- Concurrent processing is a planned future enhancement

### Debug Mode

For detailed debugging information:

```bash
# Maximum verbosity with single iteration for quick feedback
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose --max-iterations 1

# Enable Anthropic SDK debug logging
export ANTHROPIC_LOG=debug  # On Linux/macOS
$env:ANTHROPIC_LOG="debug"  # On Windows PowerShell

# Then run with verbose
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

This will:
- Show all log messages at DEBUG level
- Limit retries to 1 for quick feedback
- Display detailed progress for each phase

### Logging Levels

- **INFO** (default): Basic progress and summary messages
- **DEBUG** (with --verbose): Detailed phase execution, state transitions, and agent communications

### Getting Help

If you encounter issues not covered here:

1. Run with `--verbose` flag for detailed logs
2. Check the example epic file: `test-docs/epics/example-epic.md`
3. Review task guidance files in `.bmad-core/tasks/`
4. Verify your epic format matches the expected pattern

### FAQ

**Q: Can I run the tool without internet?**
A: No, the tool requires internet access to communicate with the Claude Agent SDK.

**Q: Can I pause and resume processing?**
A: Yes, the state manager persists progress in `progress.db`. You can stop the process (Ctrl+C) and run the same command again to continue from where you left off.

**Q: Can I skip already completed stories?**
A: Yes, the system automatically skips stories marked as "Done" in the state database.

**Q: Is it safe to run multiple times on the same epic?**
A: Yes, the tool is designed to be idempotent. It tracks state in `progress.db` and will skip completed stories.

**Q: Can I customize the agent behavior?**
A: Yes, modify the task guidance files in `.bmad-core/tasks/` to customize how SM, Dev, and QA agents work.

**Q: How do I specify custom source and test directories for QA checks?**
A: Use the `--source-dir` and `--test-dir` flags:
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --source-dir my_src --test-dir my_tests
```
The default directories are `src` and `tests` respectively.

**Q: What happens if the process crashes?**
A: The SQLite database (`progress.db`) maintains persistent state with WAL mode enabled. Simply restart the process and it will resume from the last saved state.

**Q: Can I run multiple epic processing jobs in parallel?**
A: Not currently. Concurrent processing is marked as experimental. SQLite database locking may cause issues with parallel runs.

**Q: Where are logs stored?**
A: Logs are written to:
- Console output (always)
- `autoBMAD/epic_automation/logs/` directory (if file logging enabled)
- Timestamped log files with format: `epic_automation_YYYYMMDD_HHMMSS.log`

**Q: How do I reset the system state?**
A: 
```bash
# Backup first
cp progress.db progress.db.backup

# Remove state database
rm progress.db

# Next run will start fresh
```

**Q: What Python version is required?**
A: Python 3.12 or higher is required for latest type hints and async features.

**Q: Can I use this in a CI/CD pipeline?**
A: Yes, but ensure:
- ANTHROPIC_API_KEY is set as environment variable
- All dependencies are installed
- Use `--skip-quality` and `--skip-tests` if tools not available in CI environment
- Consider timeout limits for long-running processes

## Example Epic

See `test-docs/epics/example-epic.md` for a complete example of an epic document with multiple stories.

## License

This template is part of the BMAD methodology and is provided as-is for use in BMAD projects.

## Support

For issues and questions:

1. **Documentation**:
   - Review this [README.md](README.md) for comprehensive documentation
   - Check [SETUP.md](SETUP.md) for detailed setup instructions
   - Read [architecture/architecture.md](architecture/architecture.md) for system architecture

2. **Troubleshooting**:
   - Enable verbose logging with `--verbose` flag
   - Check the Troubleshooting section above
   - Review log files in `autoBMAD/epic_automation/logs/`
   - Inspect `progress.db` for state information

3. **Examples**:
   - See example usage in the Quick Start section
   - Check `docs-test/epics/` for example epic files
   - Review `tests/` directory for test examples

4. **Community**:
   - Report issues on GitHub
   - Contribute improvements via pull requests
   - Share your experiences and best practices

## Version History

### Version 3.0 (2026-01-14)
- Five-layer architecture with Controllers pattern
- State-driven workflow execution
- Enhanced quality gates with error reporting
- Batch test execution support
- Improved logging and monitoring
- SQLite with WAL mode and optimistic locking

### Version 2.0
- Claude Agent SDK integration
- Async story creation
- Removed hardcoded story templates
- Simplified codebase per Occam's Razor

### Version 1.0
- Initial release
- Basic SM-Dev-QA cycle
- Manual story creation

---

**Built with**: Python 3.12+ | Claude Agent SDK | SQLite | Loguru  
**License**: Part of the BMAD methodology  
**Maintained by**: BMAD Development Team

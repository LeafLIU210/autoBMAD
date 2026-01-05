# autoBMAD Epic Automation System

A comprehensive automation system for the BMAD (Breakthrough Method of Agile AI-driven Development) workflow. This tool processes epic markdown files through a complete 5-phase workflow including SM-Dev-QA cycle, quality gates, and test automation.

## Overview

autoBMAD Epic Automation is a portable template that enables teams to quickly set up and use the BMAD methodology in their projects. It reads epic markdown files, identifies stories, and orchestrates the automated execution through all five phases of the complete development workflow.

### Key Features

- **Complete 5-Phase Workflow**: SM-Dev-QA cycle followed by quality gates and test automation
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
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including quality gate tools
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0

# Verify installation
python autoBMAD/epic_automation/epic_driver.py --help
```

### Basic Usage with Complete 5-Phase Workflow

```bash
# Process an epic through all 5 phases
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md

# Skip quality gates (for faster development)
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality

# Skip test automation (for quick validation)
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests
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

- Python 3.8 or higher
- Claude SDK (for AI agent functionality)
- Basedpyright>=1.1.0 (for type checking)
- Ruff>=0.1.0 (for linting)
- Pytest>=7.0.0 (for testing)
- Debugpy>=1.6.0 (for debugging)

### Setup Steps

1. **Copy the epic_automation folder** to your project directory:
   ```bash
   cp -r /path/to/epic_automation /your/project/
   ```

2. **Ensure Claude SDK is configured** in your environment

3. **Verify the setup** by running the help command:
   ```bash
   cd /your/project
   source venv/Scripts/activate
   python autoBMAD/epic_automation/epic_driver.py --help
   ```

4. **Ensure task guidance files exist** in `.bmad-core/tasks/`:
   - `create-next-story.md` (for SM agent)
   - `develop-story.md` (for Dev agent)
   - `review-story.md` (for QA agent)

### Configuration

No additional configuration required! The tool automatically:
- Locates task guidance files in `.bmad-core/tasks/`
- Parses epic markdown files
- Manages state between runs
- Handles logging and error reporting

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
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

This will process all stories in `my-epic.md` through the complete 5-phase workflow:
- Phase 1: SM-Dev-QA cycle for all stories
- Phase 2: Quality gates (basedpyright + ruff)
- Phase 3: Test automation (pytest)
- Max 3 retry attempts for quality gates
- Max 5 retry attempts for test automation

#### Example 2: Skip Quality Gates (Faster Development)

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality
```

Processes stories through SM-Dev-QA cycle and test automation, but skips quality gates for faster iteration during development.

#### Example 3: Skip Test Automation (Quick Validation)

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests
```

Processes stories through SM-Dev-QA cycle and quality gates, but skips test automation for quick validation without running tests.

#### Example 4: Skip Both Quality Gates and Tests

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests
```

Processes only the SM-Dev-QA cycle, skipping both quality gates and test automation for maximum speed during initial development.

#### Example 5: Enable Automatic Retry

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
```

Enables automatic retry of failed stories and provides detailed logging output.

## Architecture

### Component Overview

The BMAD Epic Automation system consists of the following components:

```
autoBMAD/epic_automation/
├── epic_driver.py          # Main orchestrator and CLI interface
├── sm_agent.py            # Story Master agent
├── dev_agent.py           # Development agent
├── qa_agent.py            # Quality Assurance agent
└── state_manager.py       # State persistence and tracking
```

### File Structure

```
project/
├── autoBMAD/epic_automation/     # Main automation package
│   ├── epic_driver.py            # CLI entry point
│   ├── sm_agent.py               # Story Master implementation
│   ├── dev_agent.py              # Development agent implementation
│   ├── qa_agent.py               # QA agent implementation
│   ├── state_manager.py          # State persistence
│   └── README.md                 # This file
├── .bmad-core/tasks/              # Task guidance files
│   ├── create-next-story.md      # SM agent guidance
│   ├── develop-story.md          # Dev agent guidance
│   └── review-story.md           # QA agent guidance
└── docs/epics/                    # Epic documents
    ├── my-epic.md                # Your epic files
    └── example-epic.md           # Example epic (see below)
```

### How It Works

1. **Initialization**: The `epic_driver.py` parses CLI arguments and initializes the EpicDriver with configuration options.

2. **Epic Parsing**: The system reads the epic markdown file and extracts story references using regex patterns.

3. **Story Processing Loop**: For each story:
   - **SM Phase**: Story Master agent refines and validates the story
   - **Dev Phase**: Development agent implements the story according to specifications
   - **QA Phase**: Quality Assurance agent validates the implementation

4. **Retry Logic**: If a story fails QA:
   - If `--retry-failed` is enabled, the Dev phase is retried up to `--max-iterations` times
   - If `--retry-failed` is disabled, the story is marked as failed and processing continues

5. **State Management**: The `state_manager.py` tracks the status of each story, including:
   - Completion status
   - Current phase
   - Iteration count
   - QA results
   - Error messages

6. **Reporting**: The system provides summary statistics and detailed logging based on the `--verbose` flag.

### Agent Roles

#### Story Master (SM) Agent

- Refines story requirements
- Ensures story completeness
- Validates acceptance criteria
- Creates task breakdowns

#### Development (Dev) Agent

- Implements the story according to specifications
- Writes code, tests, and documentation
- Follows best practices and coding standards
- Updates story files with progress

#### Quality Assurance (QA) Agent

- Reviews implementation quality
- Validates against acceptance criteria
- Checks code standards and testing
- Provides feedback and pass/fail decisions

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
- Ensure the `.bmad-core/tasks/` directory exists
- Verify task guidance files are present:
  - `create-next-story.md`
  - `develop-story.md`
  - `review-story.md`

#### Issue: "Failed to import agent classes"

**Error Message**:
```
ERROR - Failed to import agent classes: No module named 'sm_agent'
```

**Solution**:
- Ensure all agent files are in the same directory as `epic_driver.py`
- Check that Python path includes the automation directory
- Verify all dependencies are installed

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

#### Issue: Concurrent processing not available

**Warning Message**:
```
WARNING - Concurrent processing is experimental and not yet implemented
```

**Solution**:
- This is expected behavior - the feature is not yet implemented
- Remove the `--concurrent` flag for now
- Stories will be processed sequentially

### Debug Mode

For detailed debugging, run with maximum verbosity:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose --max-iterations 1
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
A: No, the tool requires internet access to communicate with the Claude SDK.

**Q: Can I pause and resume processing?**
A: Yes, the state manager persists progress. You can run the same command again to continue.

**Q: Can I skip already completed stories?**
A: Yes, the system automatically skips stories marked as "completed" in the state.

**Q: Is it safe to run multiple times on the same epic?**
A: Yes, the tool is designed to be idempotent and will skip completed stories.

**Q: Can I customize the agent behavior?**
A: Yes, modify the task guidance files in `.bmad-core/tasks/` to customize agent behavior.

**Q: How do I specify custom source and test directories for QA checks?**
A: Use the `--source-dir` and `--test-dir` flags when running epic_driver.py. For example: `python epic_driver.py docs/epics/my-epic.md --source-dir my_src --test-dir my_tests`. The default directories are "src" and "tests" respectively.

## Example Epic

See `test-docs/epics/example-epic.md` for a complete example of an epic document with multiple stories.

## License

This template is part of the BMAD methodology and is provided as-is for use in BMAD projects.

## Support

For issues and questions:
- Review this README
- Check the example epic
- Enable verbose logging for detailed diagnostics

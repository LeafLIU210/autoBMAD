# BMAD Epic Automation

A self-contained automation system for the BMAD (Breakthrough Method of Agile AI-driven Development) workflow. This tool processes epic markdown files through the complete SM-Dev-QA cycle, automating story development and quality assurance.

## Overview

BMAD Epic Automation is a portable template that enables teams to quickly set up and use the BMAD methodology in their projects. It reads epic markdown files, identifies stories, and orchestrates the automated execution of the SM (Story Master), Dev (Development), and QA (Quality Assurance) phases for each story.

### Key Features

- **Automated SM-Dev-QA Cycle**: Processes stories through all three phases automatically
- **CLI Interface**: Simple command-line interface with flexible options
- **Retry Logic**: Configurable retry attempts for failed stories
- **Verbose Logging**: Detailed logging for debugging and monitoring
- **Portable**: Self-contained solution requiring only Python and the Claude SDK
- **No Complex Setup**: Copy the folder to your project and start using immediately

## Installation

### Requirements

- Python 3.8 or higher
- Claude SDK (for AI agent functionality)
- No other external dependencies required

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

### Usage Examples

#### Example 1: Basic Processing

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

This will process all stories in `my-epic.md` with default settings:
- Max 3 retry attempts per story
- No automatic retry on QA failures
- Standard logging level

#### Example 2: Custom Retry Limit

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --max-iterations 5
```

Increases the maximum retry attempts to 5 for each failed story.

#### Example 3: Enable Automatic Retry

```bash
python autoBMAD/epic_automation/epic_automation/epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
```

Enables automatic retry of failed stories and provides detailed logging output.

#### Example 4: Full Configuration

```bash
python autoBMAD/epic_automation/epic_driver.py \
  docs/epics/my-epic.md \
  --max-iterations 10 \
  --retry-failed \
  --verbose \
  --concurrent
```

Applies all available options for maximum control and visibility.

#### Example 5: Debug Mode

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose --max-iterations 1
```

Run with verbose logging and only 1 retry attempt to quickly identify issues.

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

## Example Epic

See `test-docs/epics/example-epic.md` for a complete example of an epic document with multiple stories.

## License

This template is part of the BMAD methodology and is provided as-is for use in BMAD projects.

## Support

For issues and questions:
- Review this README
- Check the example epic
- Enable verbose logging for detailed diagnostics

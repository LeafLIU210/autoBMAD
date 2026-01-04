# BMAD Epic Automation - Setup Guide

This guide explains how to set up and use the BMAD Epic Automation template in your project.

## Quick Start

### Step 1: Copy the Template

Copy the entire `epic_automation` folder to your project:

```bash
# From the template location
cp -r /path/to/epic_automation /your/project/autoBMAD/

# Or on Windows
xcopy /E /I epic_automation \your\project\autoBMAD\epic_automation
```

Your project structure should look like:

```
your-project/
├── autoBMAD/
│   └── epic_automation/
│       ├── epic_driver.py
│       ├── sm_agent.py
│       ├── dev_agent.py
│       ├── qa_agent.py
│       ├── state_manager.py
│       ├── README.md
│       └── SETUP.md (this file)
├── .bmad-core/
│   └── tasks/
│       ├── create-next-story.md
│       ├── develop-story.md
│       └── review-story.md
└── docs/
    └── epics/
        └── your-epic.md
```

### Step 2: Verify Dependencies

Ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Claude SDK** configured and working
   - The SDK should be accessible from your project directory
   - No additional Python packages required

3. **Task Guidance Files**
   - Ensure `.bmad-core/tasks/` directory exists
   - Verify these files are present:
     - `create-next-story.md` (for SM agent)
     - `develop-story.md` (for Dev agent)
     - `review-story.md` (for QA agent)

### Step 3: Test the Setup

Run the help command to verify everything works:

```bash
cd /your/project
python autoBMAD/epic_automation/epic_driver.py --help
```

You should see the help message with all available options.

### Step 4: Create Your First Epic

Create an epic file in `docs/epics/`:

```bash
mkdir -p docs/epics
```

Create `docs/epics/my-first-epic.md`:

```markdown
# Epic: My First Epic

## Stories

- **[Story 001: Example Story](story-001.md)**

---

## Story 001: Example Story

**As a** developer,
**I want to** use the automation system,
**So that** I can streamline my workflow.

**Acceptance Criteria**:
- [ ] Story is processed successfully
- [ ] All phases complete

```

Create `docs/epics/story-001.md` with a simple story following the BMAD template.

### Step 5: Run Your First Epic

Process your epic:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-first-epic.md --verbose
```

## Detailed Setup Instructions

### Prerequisites

#### Required Software

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure Python is in your PATH

2. **Claude SDK**
   - Install and configure the Claude SDK
   - Verify with: `claude --version`

3. **Git** (recommended)
   - For version controlling your epics and stories
   - Download from [git-scm.com](https://git-scm.com/)

#### Optional Software

- **Virtual Environment** (recommended)
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

### Directory Structure

The template requires this minimal directory structure:

```
project/
├── autoBMAD/epic_automation/     # Automation package (REQUIRED)
├── .bmad-core/tasks/              # Task guidance (REQUIRED)
└── docs/epics/                    # Epic files (RECOMMENDED)
```

#### Required Components

1. **`autoBMAD/epic_automation/`** directory
   - Contains all automation logic
   - Must be in the project root
   - Should not be modified unless customizing

2. **`.bmad-core/tasks/`** directory
   - Contains task guidance files
   - Files must be markdown (.md) format
   - These files guide the AI agents

3. **Epic markdown files**
   - Stored in any directory
   - Referenced from command line
   - Format: Markdown with story references

### Configuration

#### Environment Variables

No environment variables are required! The template is self-contained.

However, you may optionally set:

- `CLAUDE_API_KEY`: If not using default Claude SDK configuration
- `BMAD_DEBUG`: Set to "true" for debug logging

#### Task Guidance Files

The `.bmad-core/tasks/` directory should contain:

1. **`create-next-story.md`**
   - Guidance for the Story Master (SM) agent
   - Used for story creation and refinement

2. **`develop-story.md`**
   - Guidance for the Development (Dev) agent
   - Used for implementation tasks

3. **`review-story.md`**
   - Guidance for the Quality Assurance (QA) agent
   - Used for validation and review

These files should be copied from the template's `.bmad-core/tasks/` directory.

### Usage

#### Basic Usage

```bash
python autoBMAD/epic_automation/epic_driver.py <epic_path>
```

#### With Options

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md \
  --max-iterations 5 \
  --retry-failed \
  --verbose
```

#### Options Reference

- `epic_path` (required): Path to your epic markdown file
- `--max-iterations N`: Maximum retry attempts (default: 3)
- `--retry-failed`: Enable automatic retry of failed stories
- `--verbose`: Enable detailed logging
- `--concurrent`: Experimental parallel processing

### Customization

#### Custom Task Guidance

To customize agent behavior, edit the files in `.bmad-core/tasks/`:

- Modify prompts to change how agents work
- Add specific requirements for your domain
- Include company-specific standards

**Warning**: Only modify these files if you understand the BMAD methodology.

#### Custom Agent Logic

To modify the automation logic:

1. Edit files in `autoBMAD/epic_automation/`
2. Python knowledge required
3. Test thoroughly after changes
4. Keep backups of original files

**Warning**: This is advanced customization. Most users should not need to modify these files.

### Troubleshooting

#### Issue: "Module not found" errors

**Solution**:
```bash
# Ensure you're in the project root
cd /your/project

# Run from the correct location
python autoBMAD/epic_automation/epic_driver.py --help
```

#### Issue: "Tasks directory not found"

**Solution**:
```bash
# Create the tasks directory
mkdir -p .bmad-core/tasks

# Copy task files from template
cp /path/to/template/.bmad-core/tasks/* .bmad-core/tasks/
```

#### Issue: "Epic file not found"

**Solution**:
- Check the file path is correct
- Use absolute path if relative path doesn't work
- Ensure file has `.md` extension

#### Issue: Stories not being processed

**Solution**:
- Verify epic file format matches expected pattern
- Check that story files exist at referenced paths
- Use `--verbose` for detailed logging

#### Issue: Claude SDK errors

**Solution**:
- Verify Claude SDK is installed: `claude --version`
- Check API credentials are configured
- Ensure internet connection is available
- Try running a simple Claude command: `claude "Hello"`

### Best Practices

1. **Version Control**
   - Commit epic and story files to git
   - Don't commit `.ai/` directory (contains temporary state)
   - Track changes to task guidance files

2. **Epic Organization**
   - Group related stories in single epics
   - Use descriptive epic names
   - Keep epics focused on a single feature or domain

3. **Story Structure**
   - Follow the BMAD story template
   - Include clear acceptance criteria
   - Break down complex tasks into subtasks

4. **Testing**
   - Start with simple stories to test setup
   - Use `--verbose` flag for debugging
   - Keep backups of working epic files

5. **State Management**
   - State is saved in `.ai/` directory
   - Safe to delete `.ai/` to reset state
   - Epics can be re-run safely

### Migration from Other Versions

If you're migrating from an older version:

1. **Backup your data**
   ```bash
   cp -r .ai .ai-backup
   cp -r docs/epics docs-epics-backup
   ```

2. **Copy new template**
   ```bash
   cp -r /path/to/new/epic_automation autoBMAD/
   ```

3. **Test with a simple epic**
   ```bash
   python autoBMAD/epic_automation/epic_driver.py docs/epics/test-epic.md --verbose
   ```

4. **Restore your data if needed**
   ```bash
   cp -r .ai-backup .ai
   ```

### Support

If you encounter issues:

1. Check the [README.md](README.md) for detailed documentation
2. Review the [example epic](../test-docs/epics/example-epic.md)
3. Run with `--verbose` for detailed logs
4. Check the troubleshooting section above

### FAQ

**Q: Can I use this without Claude SDK?**
A: No, the Claude SDK is required for AI agent functionality.

**Q: Is internet required?**
A: Yes, internet is required to communicate with Claude.

**Q: Can I run this on any operating system?**
A: Yes, it works on Windows, macOS, and Linux.

**Q: Can I customize the agents?**
A: Yes, by modifying task guidance files in `.bmad-core/tasks/`.

**Q: Is this safe for production?**
A: This is a template for development automation. Review and test before production use.

**Q: Can I integrate with CI/CD?**
A: Yes, you can run it in CI/CD pipelines with proper Claude SDK configuration.

**Q: How do I update to a new version?**
A: Copy the new template over the old one, keeping your task guidance files.

**Q: Can I use my own database or storage?**
A: Yes, by modifying the state_manager.py file.

---

## Summary

The BMAD Epic Automation template is designed to be:

- ✅ **Self-contained**: No external dependencies beyond Python and Claude SDK
- ✅ **Portable**: Copy the folder and start using immediately
- ✅ **Simple**: Minimal setup required
- ✅ **Flexible**: Customizable through task guidance files
- ✅ **Safe**: Can be run multiple times without side effects

For more information, see the [README.md](README.md).

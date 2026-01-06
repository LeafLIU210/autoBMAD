# Database Initialization Script

## Overview

This directory contains an independent database initialization script (`init_db.py`) for the autoBMAD Epic Automation system. This script creates and initializes the `progress.db` SQLite database with all required tables and indexes.

## Features

- **Create Database**: Creates a new SQLite database with all required tables
- **Verify Database**: Verifies the structure of an existing database
- **Force Recreation**: Allows overwriting existing databases
- **Verbose Output**: Detailed output showing table structure and indexes
- **Error Handling**: Comprehensive error handling and reporting

## Database Schema

The script creates the following tables:

### 1. stories
Stores story processing status and metadata.
- Tracks story progress through SM-Dev-QA cycles
- Stores iteration counts and QA results
- Links stories to their parent epics

### 2. code_quality_phase
Tracks code quality gate results.
- Stores basedpyright and ruff error counts
- Tracks fix status for each file
- Links to epic processing records

### 3. test_automation_phase
Tracks test automation results.
- Stores pytest failure counts
- Tracks debug information
- Links to epic processing records

### 4. epic_processing
Tracks epic-level processing status.
- Stores overall epic status
- Tracks completion statistics
- Links quality and test phase statuses

## Usage

### Basic Usage

```bash
# Create database in default location (progress.db)
python init_db.py

# Create database at specific path
python init_db.py --db-path /path/to/progress.db
```

### Advanced Options

```bash
# Force recreation of existing database
python init_db.py --force

# Verify existing database without creating
python init_db.py --verify

# Enable verbose output
python init_db.py --verbose

# Combine options
python init_db.py --force --verbose
```

### Examples

```bash
# Initialize a new database
cd autoBMAD/epic_automation
python init_db.py

# Verify an existing database
python init_db.py --verify --verbose

# Recreate database from scratch
python init_db.py --force

# Initialize database at custom location
python init_db.py --db-path /tmp/my_progress.db
```

## Exit Codes

- **0**: Success
- **1**: Failure (error occurred)

## Output Messages

- `[OK]`: Operation completed successfully
- `[WARNING]`: Important information (e.g., database exists)
- `[ERROR]`: Error occurred

## Requirements

- Python 3.6+
- SQLite3 (included with Python)

## Integration

This script is designed to be used independently or as part of the BMAD workflow. It can be run:

1. **Standalone**: Directly execute to initialize a new database
2. **Pre-flight Check**: Run `--verify` to check existing database health
3. **Maintenance**: Use `--force` to reset database to clean state

## Notes

- The script uses ASCII characters for maximum compatibility with Windows command prompt
- Database file is created with proper permissions
- All tables include proper indexes for optimal performance
- Foreign key constraints are defined where appropriate

## Troubleshooting

### Permission Denied
If you encounter permission errors:
- Ensure you have write access to the target directory
- Check if the database file is locked by another process

### Database Already Exists
If a database already exists:
- Use `--verify` to check its structure
- Use `--force` to overwrite it
- The script will prompt for confirmation if neither flag is set

### Unicode Errors
The script uses ASCII characters to avoid Unicode encoding issues on Windows.

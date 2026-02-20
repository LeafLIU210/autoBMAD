#!/bin/bash
# BMAD Epic Automation - Venv Wrapper Script
# Ensures virtual environment activation and dependency installation
# Version: 2.0
# Updated: 2026-02-17

set -e  # Exit on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Project root: $PROJECT_ROOT"

# Check and activate virtual environment
check_venv() {
    cd "$PROJECT_ROOT"
    
    if [ ! -d "venv" ]; then
        log_warning "Virtual environment not found, creating..."
        python -m venv venv
        log_success "Virtual environment created"
    fi

    # Activate virtual environment
    if [ -f "venv/Scripts/activate" ]; then
        # Windows (Git Bash)
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        # Linux/macOS
        source venv/bin/activate
    else
        log_error "Unable to find virtual environment activation script"
        exit 1
    fi

    log_success "Virtual environment activated"
    log_info "Python path: $(which python)"
    log_info "Python version: $(python --version)"
}

# Install dependencies
install_dependencies() {
    log_info "Checking and installing dependencies..."

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install project dependencies
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log_info "Installing from requirements.txt..."
        python -m pip install -r "$PROJECT_ROOT/requirements.txt" || {
            log_warning "Full dependency install failed, trying core packages..."
            python -m pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio duckdb PyYAML requests tqdm
        }
    else
        log_warning "requirements.txt not found, installing core dependencies..."
        python -m pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio duckdb PyYAML requests tqdm
    fi

    log_success "Dependencies installed"

    # Verify key packages
    log_info "Verifying key dependencies..."
    python -m pip list | grep -E "(claude-agent-sdk|basedpyright|ruff|pytest|loguru|anyio)" || log_warning "Some packages may not be installed correctly"
}

# Run epic automation
run_epic() {
    local epic_file=$1
    shift  # Remove first argument
    local extra_args="$@"

    if [ -z "$epic_file" ]; then
        log_error "Please provide Epic file path"
        echo "Usage: $0 <epic-file> [options]"
        echo ""
        echo "Options:"
        echo "  --verbose, -v          Enable verbose logging"
        echo "  --skip-quality         Skip quality gates (ruff/basedpyright)"
        echo "  --skip-tests           Skip test automation (pytest)"
        echo "  --max-iterations N     Maximum retry attempts (default: 3)"
        echo "  --source-dir DIR       Source directory (default: src)"
        echo "  --test-dir DIR         Test directory (default: tests)"
        echo "  --log-file             Create timestamped log file"
        echo "  -h, --help             Show help"
        exit 1
    fi

    if [ ! -f "$epic_file" ]; then
        log_error "Epic file not found: $epic_file"
        exit 1
    fi

    log_info "Starting Epic automation..."
    log_info "Epic file: $epic_file"

    # Build command with proper PYTHONPATH
    cd "$PROJECT_ROOT"
    export PYTHONPATH="$PROJECT_ROOT"
    
    local cmd="python -m autoBMAD.epic_automation.epic_driver run-epic $epic_file $extra_args"

    log_info "Executing: $cmd"
    log_info "Working directory: $(pwd)"

    # Execute
    eval $cmd
}

# Show help
show_help() {
    echo "=============================================="
    echo "  BMAD Epic Automation - Venv Wrapper"
    echo "=============================================="
    echo ""
    echo "Usage: $0 <epic-file> [options]"
    echo ""
    echo "Arguments:"
    echo "  epic-file              Path to epic markdown file"
    echo ""
    echo "Options:"
    echo "  --verbose, -v          Enable verbose logging"
    echo "  --skip-quality         Skip quality gates (ruff/basedpyright)"
    echo "  --skip-tests           Skip test automation (pytest)"
    echo "  --max-iterations N     Maximum retry attempts (default: 3)"
    echo "  --source-dir DIR       Source directory (default: src)"
    echo "  --test-dir DIR         Test directory (default: tests)"
    echo "  --log-file             Create timestamped log file"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Full workflow with verbose output"
    echo "  $0 docs/epics/epic-01.md --verbose"
    echo ""
    echo "  # Skip quality gates for faster development"
    echo "  $0 docs/epics/epic-01.md --skip-quality --verbose"
    echo ""
    echo "  # Custom directories and max iterations"
    echo "  $0 docs/epics/epic-01.md --source-dir src --test-dir tests --max-iterations 5"
    echo ""
}

# Main function
main() {
    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_help
        exit 0
    fi

    echo "=============================================="
    echo "  BMAD Epic Automation - Venv Wrapper"
    echo "=============================================="
    echo ""

    # Check and activate virtual environment
    check_venv

    # Install dependencies
    install_dependencies

    # Run epic automation
    run_epic "$@"

    log_success "Epic automation completed!"
}

# Execute main function
main "$@"

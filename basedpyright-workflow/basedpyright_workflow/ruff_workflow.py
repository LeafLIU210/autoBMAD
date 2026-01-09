"""
Ruff Workflow - Linting integration for BMAD automation.

Executes ruff linting with optional auto-fix on Python files and generates structured reports.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)


async def run_ruff_check(
    source_dir: str,
    auto_fix: bool = True,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute ruff linting with optional auto-fix.

    Args:
        source_dir: Directory to check
        auto_fix: If True, apply automatic fixes
        config_path: Optional path to pyproject.toml

    Returns:
        Dict containing:
            - success: Boolean indicating if check passed
            - errors: Dict mapping file paths to error lists
            - file_count: Number of files checked
            - error_count: Total number of errors
            - fixed_count: Number of errors auto-fixed
            - json_output: Raw JSON from ruff
    """
    logger.info(f"Running ruff check on: {source_dir} (auto_fix={auto_fix})")

    # Check if ruff is available
    if not shutil.which("ruff"):
        logger.error("ruff not found in PATH")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "fixed_count": 0,
            "message": "ruff not installed"
        }

    source_path = Path(source_dir)
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "fixed_count": 0,
            "message": f"Directory not found: {source_dir}"
        }

    # Build command
    cmd = ["ruff", "check", "--output-format=json"]

    # Add auto-fix flag
    if auto_fix:
        cmd.append("--fix")

    # Use config if provided
    if config_path and Path(config_path).exists():
        cmd.extend(["--config", str(config_path)])
    else:
        # Look for pyproject.toml in source directory or parent
        pyproject_path = source_path / "pyproject.toml"
        if not pyproject_path.exists():
            pyproject_path = source_path.parent / "pyproject.toml"

        if pyproject_path.exists():
            cmd.extend(["--config", str(pyproject_path)])
            logger.info(f"Using config: {pyproject_path}")

    cmd.append(str(source_path))

    logger.info(f"Command: {' '.join(cmd)}")

    try:
        # Execute ruff
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Decode output
        stdout_text = stdout.decode("utf-8") if stdout else ""
        stderr_text = stderr.decode("utf-8") if stderr else ""

        logger.debug(f"Ruff stdout: {stdout_text}")
        logger.debug(f"Ruff stderr: {stderr_text}")

        # Parse JSON output
        try:
            result_data = json.loads(stdout_text) if stdout_text else []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ruff JSON output: {e}")
            logger.error(f"Raw output: {stdout_text}")
            return {
                "success": False,
                "errors": {},
                "file_count": 0,
                "error_count": 0,
                "fixed_count": 0,
                "message": f"JSON parse error: {str(e)}"
            }

        # Process errors
        errors_by_file = {}
        total_errors = 0
        fixed_count = 0

        # Handle both list and dict output formats
        if isinstance(result_data, list):
            diagnostic_list = result_data
        elif isinstance(result_data, dict):
            diagnostic_list = result_data.get("results", [])
        else:
            logger.error(f"Unexpected ruff output format: {type(result_data)}")
            diagnostic_list = []

        for diagnostic in diagnostic_list:
            file_path = diagnostic.get("filename", "")
            if not file_path:
                continue

            # Normalize file path
            file_path = str(Path(file_path).resolve())

            if file_path not in errors_by_file:
                errors_by_file[file_path] = []

            errors_by_file[file_path].append(diagnostic)
            total_errors += 1

            # Count fixes
            if diagnostic.get("fix"):
                fixed_count += 1

        # Count files checked
        file_count = len(errors_by_file)

        # Determine success
        success = total_errors == 0

        result = {
            "success": success,
            "errors": errors_by_file,
            "file_count": file_count,
            "error_count": total_errors,
            "fixed_count": fixed_count,
            "json_output": result_data
        }

        if success:
            logger.info(f"Ruff check passed: {file_count} files checked")
        else:
            logger.warning(
                f"Ruff check found {total_errors} issues in {file_count} files"
            )
            if auto_fix:
                logger.info(f"Auto-fixed {fixed_count} issues")

        return result

    except asyncio.TimeoutError:
        logger.error("Ruff check timed out")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "fixed_count": 0,
            "message": "Check timed out"
        }
    except Exception as e:
        logger.error(f"Ruff check failed: {e}")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "fixed_count": 0,
            "message": str(e)
        }


def parse_ruff_json(json_output: str) -> List[Dict[str, Any]]:
    """
    Parse ruff JSON output into structured errors.

    Args:
        json_output: Raw JSON string from ruff

    Returns:
        List of error dictionaries
    """
    try:
        data = json.loads(json_output)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("results", [])
        else:
            logger.error(f"Unexpected ruff JSON format: {type(data)}")
            return []
    except json.JSONDecodeError:
        logger.error("Invalid JSON output from ruff")
        return []

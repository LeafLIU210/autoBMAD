"""
Basedpyright Workflow - Type checking integration for BMAD automation.

Executes basedpyright type checking on Python files and generates structured reports.
"""

import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)


async def run_basedpyright_check(
    source_dir: str,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute basedpyright type checking.

    Args:
        source_dir: Directory to check
        config_path: Optional path to pyproject.toml

    Returns:
        Dict containing:
            - success: Boolean indicating if check passed
            - errors: Dict mapping file paths to error lists
            - file_count: Number of files checked
            - error_count: Total number of errors
            - json_output: Raw JSON from basedpyright
    """
    logger.info(f"Running basedpyright check on: {source_dir}")

    # Check if basedpyright is available
    if not shutil.which("basedpyright"):
        logger.error("basedpyright not found in PATH")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "message": "basedpyright not installed"
        }

    source_path = Path(source_dir)
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "message": f"Directory not found: {source_dir}"
        }

    # Build command
    cmd = ["basedpyright", "--outputjson"]

    # Use config if provided
    if config_path and Path(config_path).exists():
        cmd.extend(["--project", str(config_path)])
    else:
        # Look for pyproject.toml in source directory or parent
        pyproject_path = source_path / "pyproject.toml"
        if not pyproject_path.exists():
            pyproject_path = source_path.parent / "pyproject.toml"

        if pyproject_path.exists():
            cmd.extend(["--project", str(pyproject_path)])
            logger.info(f"Using config: {pyproject_path}")

    cmd.append(str(source_path))

    logger.info(f"Command: {' '.join(cmd)}")

    try:
        # Execute basedpyright
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Decode output
        stdout_text = stdout.decode("utf-8") if stdout else ""
        stderr_text = stderr.decode("utf-8") if stderr else ""

        logger.debug(f"Basedpyright stdout: {stdout_text}")
        logger.debug(f"Basedpyright stderr: {stderr_text}")

        # Parse JSON output
        try:
            result_data = json.loads(stdout_text) if stdout_text else {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse basedpyright JSON output: {e}")
            logger.error(f"Raw output: {stdout_text}")
            return {
                "success": False,
                "errors": {},
                "file_count": 0,
                "error_count": 0,
                "message": f"JSON parse error: {str(e)}"
            }

        # Process errors
        errors_by_file = {}
        total_errors = 0

        general_diagnostics = result_data.get("generalDiagnostics", [])

        for diagnostic in general_diagnostics:
            file_path = diagnostic.get("file", "")
            if not file_path:
                continue

            # Normalize file path
            file_path = str(Path(file_path).resolve())

            if file_path not in errors_by_file:
                errors_by_file[file_path] = []

            errors_by_file[file_path].append(diagnostic)
            total_errors += 1

        # Count files checked
        file_count = len(errors_by_file)

        # Determine success
        success = total_errors == 0

        result = {
            "success": success,
            "errors": errors_by_file,
            "file_count": file_count,
            "error_count": total_errors,
            "json_output": result_data
        }

        if success:
            logger.info(f"Basedpyright check passed: {file_count} files checked")
        else:
            logger.warning(
                f"Basedpyright check found {total_errors} issues in {file_count} files"
            )

        return result

    except asyncio.TimeoutError:
        logger.error("Basedpyright check timed out")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "message": "Check timed out"
        }
    except Exception as e:
        logger.error(f"Basedpyright check failed: {e}")
        return {
            "success": False,
            "errors": {},
            "file_count": 0,
            "error_count": 0,
            "message": str(e)
        }


def parse_basedpyright_json(json_output: str) -> List[Dict[str, Any]]:
    """
    Parse basedpyright JSON output into structured errors.

    Args:
        json_output: Raw JSON string from basedpyright

    Returns:
        List of error dictionaries
    """
    try:
        data = json.loads(json_output)
        return data.get("generalDiagnostics", [])
    except json.JSONDecodeError:
        logger.error("Invalid JSON output from basedpyright")
        return []

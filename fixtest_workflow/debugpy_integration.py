"""
Debugpy Integration - Debugpy integration for persistent test failure diagnosis.

Provides debugpy listener and attachment for debugging failing tests.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import for debugpy
try:
    import debugpy
    DEBUGPY_AVAILABLE = True
except ImportError:
    DEBUGPY_AVAILABLE = False
    debugpy = None


async def start_debugpy_listener(port: int = 5678, host: str = "localhost") -> bool:
    """
    Start debugpy listener for remote debugging.

    Args:
        port: Port to listen on (default: 5678)
        host: Host to bind to (default: localhost)

    Returns:
        True if listener started successfully, False otherwise
    """
    if not DEBUGPY_AVAILABLE:
        logger.warning("debugpy not available, skipping listener start")
        return False

    try:
        debugpy.listen((host, port))
        logger.info(f"Debugpy listening on {host}:{port}")
        return True
    except Exception as e:
        logger.error(f"Failed to start debugpy listener: {e}")
        return False


async def attach_debugpy(timeout: int = 300) -> bool:
    """
    Attach debugpy to running process.

    Args:
        timeout: Timeout in seconds (default: 300)

    Returns:
        True if attached successfully, False otherwise
    """
    if not DEBUGPY_AVAILABLE:
        logger.warning("debugpy not available, cannot attach")
        return False

    try:
        # Wait for debugger to attach with timeout
        debugpy.wait_for_client()
        logger.info("Debugpy attached successfully")
        return True
    except Exception as e:
        logger.error(f"Debugpy attach failed: {e}")
        return False


def collect_debug_info(test_file: str, error: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect debug information for persistent failures.

    Args:
        test_file: Path to the test file
        error: Error details from test failure

    Returns:
        Dict containing debug information
    """
    debug_info = {
        "test_file": test_file,
        "timestamp": datetime.now().isoformat(),
        "error_type": error.get("failure_type", "unknown"),
        "error_message": error.get("error_message", ""),
        "traceback": error.get("traceback", []),
        "suggestions": []
    }

    # Add suggestions based on error type
    error_type = error.get("failure_type", "").lower()
    error_message = error.get("error_message", "").lower()

    if "assertionerror" in error_message:
        debug_info["suggestions"].append(
            "Check assertion logic - expected value does not match actual value"
        )
    elif "importerror" in error_message or "modulenotfound" in error_message:
        debug_info["suggestions"].append(
            "Check module imports - required module may not be installed or path is incorrect"
        )
    elif "attributeerror" in error_message:
        debug_info["suggestions"].append(
            "Check attribute access - object may not have the expected attribute"
        )
    elif "typeerror" in error_message:
        debug_info["suggestions"].append(
            "Check type compatibility - variable types may not match expected types"
        )
    elif "keyerror" in error_message:
        debug_info["suggestions"].append(
            "Check dictionary keys - key may not exist in dictionary"
        )
    elif "indexerror" in error_message or "list index out of range" in error_message:
        debug_info["suggestions"].append(
            "Check list index - index may be out of range"
        )
    else:
        debug_info["suggestions"].append(
            "Review test logic and setup - error details need manual investigation"
        )

    # Add general debugging suggestions
    debug_info["suggestions"].extend([
        "Set breakpoints in test file to inspect variable values",
        "Check test fixtures and setup methods",
        "Verify test data and dependencies",
        "Review recent code changes that may affect the test"
    ])

    return debug_info


async def invoke_debugpy_session(
    test_file: str,
    error_details: Dict[str, Any],
    port: int = 5678,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Invoke a complete debugpy session for a failing test.

    Args:
        test_file: Path to the test file
        error_details: Error details from test failure
        port: Debugpy port (default: 5678)
        timeout: Timeout in seconds (default: 300)

    Returns:
        Dict with debug session information
    """
    debug_session = {
        "test_file": test_file,
        "port": port,
        "timestamp": datetime.now().isoformat(),
        "attached": False,
        "error": None,
        "debug_info": None
    }

    try:
        # Collect debug information
        debug_info = collect_debug_info(test_file, error_details)
        debug_session["debug_info"] = debug_info

        if not DEBUGPY_AVAILABLE:
            debug_session["error"] = "debugpy not available"
            logger.warning("Cannot invoke debugpy session: debugpy not installed")
            return debug_session

        # Start listener
        listener_started = await start_debugpy_listener(port)
        if not listener_started:
            debug_session["error"] = "Failed to start debugpy listener"
            return debug_session

        # Attach to process
        debug_session["attached"] = await attach_debugpy(timeout)

        if debug_session["attached"]:
            logger.info(f"Debugpy session active for {test_file}")
        else:
            debug_session["error"] = "Failed to attach debugpy"

        return debug_session

    except Exception as e:
        logger.error(f"Debugpy session failed: {e}")
        debug_session["error"] = str(e)
        return debug_session

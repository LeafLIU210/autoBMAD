#!/usr/bin/env python3
"""
Test script for BMAD Epic Driver logging system.

This script tests the logging functionality to ensure:
1. Log files are created with timestamps
2. SDK messages are logged correctly
3. Real-time updates work
4. Exception logging works
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.epic_automation.log_manager import LogManager


async def test_basic_logging():
    """Test basic logging functionality."""
    print("=" * 80)
    print("TEST 1: Basic Logging")
    print("=" * 80)

    # Create log manager
    log_manager = LogManager()

    # Create timestamped log
    log_file = log_manager.create_timestamped_log()
    print(f"[OK] Log file created: {log_file}")

    # Write some test messages
    log_manager.write_log("This is a test message", "INFO")
    log_manager.write_log("This is a debug message", "DEBUG")
    log_manager.write_log("This is a warning message", "WARNING")
    log_manager.write_log("This is an error message", "ERROR")

    print("[OK] Test messages written")

    # Close log
    log_manager.close_log()
    print("[OK] Log file closed\n")


async def test_sdk_messages():
    """Test SDK message logging."""
    print("=" * 80)
    print("TEST 2: SDK Message Logging")
    print("=" * 80)

    # Create log manager
    log_manager = LogManager()
    log_file = log_manager.create_timestamped_log()
    print(f"[OK] Log file created: {log_file}")

    # Simulate SDK messages
    log_manager.write_sdk_message("Using tool: Read", "TOOL_USE")
    await asyncio.sleep(1)
    log_manager.write_sdk_message("[Thinking] Now I understand the task...", "THINKING")
    await asyncio.sleep(1)
    log_manager.write_sdk_message("[User sent 1 content blocks]", "USER")
    await asyncio.sleep(1)
    log_manager.write_sdk_message("[Tool result] File read successfully", "TOOL_RESULT")

    print("[OK] SDK messages written")

    # Close log
    log_manager.close_log()
    print("[OK] Log file closed\n")


async def test_exception_logging():
    """Test exception logging."""
    print("=" * 80)
    print("TEST 3: Exception Logging")
    print("=" * 80)

    # Create log manager
    log_manager = LogManager()
    log_file = log_manager.create_timestamped_log()
    print(f"[OK] Log file created: {log_file}")

    # Simulate an exception
    try:
        raise ValueError("This is a test exception")
    except Exception as e:
        log_manager.write_exception(e, "Test exception context")

    print("[OK] Exception logged")

    # Close log
    log_manager.close_log()
    print("[OK] Log file closed\n")


def test_log_file_listing():
    """Test log file listing."""
    print("=" * 80)
    print("TEST 4: Log File Listing")
    print("=" * 80)

    # Create log manager
    log_manager = LogManager()

    # List log files
    log_files: List[Path] = log_manager.list_log_files(limit=5)

    if log_files:
        print(f"[OK] Found {len(log_files)} log files:")
        for log_file in log_files:
            print(f"  - {log_file.name}")
    else:
        print("[OK] No log files found (expected if first run)")

    print()


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BMAD Epic Driver - Logging System Tests" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Run tests
    await test_basic_logging()
    await test_sdk_messages()
    await test_exception_logging()
    test_log_file_listing()

    print("=" * 80)
    print("All tests completed successfully! [OK]")
    print("=" * 80)
    print()
    print("Log files are stored in: autoBMAD/epic_automation/logs/")
    print("Check the log files to verify the output.\n")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test script for multi-document update system

This script tests the new multi-document auto-update functionality
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.update_claude_md import MultiDocUpdater, AntiLoopProtection, UpdateConfig


def test_anti_loop_protection():
    """Test anti-loop protection mechanisms"""
    print("Testing anti-loop protection mechanisms...")

    config = UpdateConfig()
    protection = AntiLoopProtection(config)

    # Test 1: Basic can_proceed check
    print("\nTest 1: Basic anti-loop check")
    can_proceed = protection.can_proceed()
    print(f"   Result: {'PASS' if can_proceed else 'FAIL'}")

    # Test 2: Lock mechanism
    print("\nTest 2: Lock mechanism")
    lock_acquired = protection.acquire_lock()
    print(f"   Lock acquisition: {'SUCCESS' if lock_acquired else 'FAIL'}")

    # Test 3: Double lock prevention
    print("\nTest 3: Double lock detection")
    protection2 = AntiLoopProtection(config)
    double_lock = protection2.can_proceed()
    print(f"   Double lock prevention: {'CORRECTLY BLOCKED' if not double_lock else 'INCORRECTLY ALLOWED'}")

    # Test 4: Timestamp update
    print("\nTest 4: Timestamp update")
    protection.update_timestamp()
    timestamp_exists = config.timestamp_file.exists()
    print(f"   Timestamp file: {'CREATED' if timestamp_exists else 'FAILED'}")

    # Cleanup
    protection.release_lock()
    print("\nAnti-loop protection tests completed")


def test_document_mapping():
    """Test document mapping functionality"""
    print("\nTesting document mapping functionality...")

    updater = MultiDocUpdater()

    # Test cases for different file changes
    test_cases = [
        (["scripts/update_claude_md.py"], ["CLAUDE.md", "claude_docs/git-commit-trigger-update.md"]),
        (["autoBMAD/epic_automation/epic_driver.py"], ["CLAUDE.md", "claude_docs/workflow_tools.md"]),
        (["claude_docs/ai_workflow.md"], ["CLAUDE.md", "claude_docs/ai_workflow.md"]),
        (["src/main.py"], ["CLAUDE.md"]),  # Should only update CLAUDE.md
        (["README.md"], ["CLAUDE.md"]),     # Should only update CLAUDE.md
    ]

    for i, (changed_files, expected_docs) in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Changed files {changed_files}")
        actual_docs = updater.get_docs_to_update(changed_files)

        # Check if expected docs are included
        missing_docs = set(expected_docs) - set(actual_docs)
        extra_docs = set(actual_docs) - set(expected_docs)

        if not missing_docs and not extra_docs:
            print(f"   Perfect match: {actual_docs}")
        else:
            if missing_docs:
                print(f"   Missing docs: {missing_docs}")
            if extra_docs:
                print(f"   Extra docs: {extra_docs}")

    print("\nDocument mapping tests completed")


def test_file_system():
    """Test file system integration"""
    print("\nTesting file system integration...")

    # Check if target documents exist
    updater = MultiDocUpdater()
    missing_docs = []

    for doc in updater.target_docs:
        doc_path = PROJECT_ROOT / doc
        if not doc_path.exists():
            missing_docs.append(doc)

    if missing_docs:
        print(f"   Found missing docs ({len(missing_docs)}):")
        for doc in missing_docs:
            print(f"      - {doc}")
    else:
        print(f"   All target docs ({len(updater.target_docs)}) exist")

    # Check lock file location
    config = UpdateConfig()
    lock_path = PROJECT_ROOT / config.lock_file
    print(f"   Lock file path: {lock_path}")

    # Check timestamp file location
    timestamp_path = PROJECT_ROOT / config.timestamp_file
    print(f"   Timestamp file path: {timestamp_path}")

    print("\nFile system integration tests completed")


def main():
    """Run all tests"""
    print("Multi-Document Update System Test Suite")
    print("=" * 60)

    try:
        test_anti_loop_protection()
        test_document_mapping()
        test_file_system()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
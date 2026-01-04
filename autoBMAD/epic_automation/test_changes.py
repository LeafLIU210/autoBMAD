#!/usr/bin/env python3
"""Test script for epic_automation changes."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all modules import successfully."""
    print("Testing imports...")

    try:
        import qa_tools_integration  # type: ignore[import-untyped,import]
        print("  [PASS] qa_tools_integration")
    except Exception as e:
        print(f"  [FAIL] qa_tools_integration: {e}")
        return False

    try:
        import qa_agent  # type: ignore[import-untyped,import]
        print("  [PASS] qa_agent")
    except Exception as e:
        print(f"  [FAIL] qa_agent: {e}")
        return False

    try:
        import epic_driver  # type: ignore[import-untyped,import]
        print("  [PASS] epic_driver")
    except Exception as e:
        print(f"  [FAIL] epic_driver: {e}")
        return False

    return True


def test_qa_tools():
    """Test QA tools integration."""
    print("\nTesting QA tools integration...")

    try:
        from qa_tools_integration import QAAutomationWorkflow, QAStatus  # type: ignore[import-untyped,import]
        print("  [PASS] QAStatus enum imported")

        # Initialize workflow
        workflow = QAAutomationWorkflow(
            basedpyright_dir="basedpyright-workflow",
            fixtest_dir="fixtest-workflow",
            timeout=300,
            max_retries=2
        )
        print("  [PASS] QAAutomationWorkflow initialized")

        # Check availability
        bp_available = workflow.basedpyright_runner.available
        ft_available = workflow.fixtest_runner.available
        print(f"  [INFO] BasedPyright available: {bp_available}")
        print(f"  [INFO] Fixtest available: {ft_available}")

        return True
    except Exception as e:
        print(f"  [FAIL] QA tools test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_epic_parsing():
    """Test epic parsing logic."""
    print("\nTesting epic parsing...")

    try:
        from epic_driver import EpicDriver  # type: ignore[import-untyped,import]

        # Test with docs-copy/epics/epic-bmad-automation.md
        epic_path = Path("../../docs-copy/epics/epic-bmad-automation.md")

        if epic_path.exists():
            print(f"  [INFO] Testing with: {epic_path}")
            driver = EpicDriver(str(epic_path))
            stories = driver.parse_epic()

            print(f"  [PASS] Parsed {len(stories)} stories")
            for story in stories:
                print(f"    - ID: {story['id']}, File: {Path(story['path']).name}")
        else:
            print(f"  [INFO] Epic file not found: {epic_path}")
            print(f"  [INFO] This is expected if docs-copy is not available")

        return True
    except Exception as e:
        print(f"  [FAIL] Epic parsing test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qa_agent():
    """Test QA agent integration."""
    print("\nTesting QA agent integration...")

    try:
        import asyncio
        from qa_agent import QAAgent  # type: ignore[import-untyped,import]

        async def run_test():
            agent = QAAgent()

            # Test story content
            story_content = """# Story 001: Test Story

**Epic**: Test Epic

## Status
**Status**: Done

## Story
**As a** test user,
**I want to** test QA,
**So that** we can verify it works.

## Acceptance Criteria
- [x] Test criterion 1
- [x] Test criterion 2

## Tasks
- [x] Task 1: Test task
"""

            # Execute QA (without tools for testing)
            result = await agent.execute(
                story_content,
                use_qa_tools=False  # Disable tools for basic test
            )

            print(f"  [PASS] QA agent executed successfully")
            print(f"    - Score: {result.get('score', 0)}")
            print(f"    - Passed: {result.get('passed', False)}")
            print(f"    - Completeness: {result.get('completeness', 0):.0%}")

            return True

        # Run async test
        success = asyncio.run(run_test())
        return success

    except Exception as e:
        print(f"  [FAIL] QA agent test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("EPIC AUTOMATION CHANGES TEST SUITE")
    print("=" * 60)

    all_passed = True

    # Test 1: Imports
    if not test_imports():
        all_passed = False

    # Test 2: QA Tools
    if not test_qa_tools():
        all_passed = False

    # Test 3: Epic Parsing
    if not test_epic_parsing():
        all_passed = False

    # Test 4: QA Agent
    if not test_qa_agent():
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - Review output above")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

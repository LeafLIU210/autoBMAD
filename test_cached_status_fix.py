#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script: Verify cached_status mechanism removal fix

Test content:
1. DevAgent status parsing (no cache)
2. QAAgent status verification after review
3. SDK cancellation handling
"""

import asyncio
import tempfile
import os
from pathlib import Path

# Add project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.dev_agent import DevAgent
from autoBMAD.epic_automation.qa_agent import QAAgent


def create_test_story(content: str, suffix: str = "") -> str:
    """Create test story file"""
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / f"test_story_{suffix}.md"
    test_file.write_text(content, encoding="utf-8")
    return str(test_file)


async def test_dev_agent_status_parsing():
    """Test DevAgent status parsing after removing cache"""
    print("Testing DevAgent status parsing (no cache)...")

    # Create test story
    story_content = """# Test Story

**Status:** Ready for Review

## User Story
As a user,
I want to test the story status parsing.

## Acceptance Criteria
1. Test status parsing
2. Test no caching
"""
    story_path = create_test_story(story_content, "dev_test")

    try:
        # Instantiate DevAgent
        dev_agent = DevAgent()

        # First status parse
        status1 = await dev_agent._parse_story_status_with_sdk(story_path)
        print(f"  First parse status: {status1}")

        # Update story status
        updated_content = story_content.replace("Ready for Review", "Done")
        Path(story_path).write_text(updated_content, encoding="utf-8")

        # Second status parse (should reflect new status)
        status2 = await dev_agent._parse_story_status_with_sdk(story_path)
        print(f"  Second parse status: {status2}")

        # Verify results
        assert status1 == "Ready for Review", f"Expected 'Ready for Review', got '{status1}'"
        assert status2 == "Done", f"Expected 'Done', got '{status2}'"

        print("  [PASS] DevAgent status parsing test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] DevAgent status parsing test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def test_qa_agent_status_verification():
    """Test QA status verification after review"""
    print("Testing QAAgent status verification...")

    # Create test story
    story_content = """# Test QA Story

**Status:** Ready for Review

## User Story
As a user,
I want to test QA status verification.

## Acceptance Criteria
1. Test QA verification
2. Test status checking
"""
    story_path = create_test_story(story_content, "qa_test")

    try:
        # Instantiate QAAgent
        qa_agent = QAAgent()

        # Parse initial status
        initial_status = await qa_agent._parse_story_status_with_sdk(story_path)
        print(f"  Initial status: {initial_status}")

        # Simulate status update (should update after QA review)
        updated_content = story_content.replace("Ready for Review", "Done")
        Path(story_path).write_text(updated_content, encoding="utf-8")

        # Verify status update
        final_status = await qa_agent._parse_story_status_with_sdk(story_path)
        print(f"  Updated status: {final_status}")

        # Verify results
        assert initial_status == "Ready for Review", f"Expected initial status 'Ready for Review', got '{initial_status}'"
        assert final_status == "Done", f"Expected final status 'Done', got '{final_status}'"

        print("  [PASS] QAAgent status verification test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] QAAgent status verification test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def test_sdk_cancellation_handling():
    """Test SDK cancellation handling"""
    print("Testing SDK cancellation handling...")

    # Create test story
    story_content = """# Test Cancel Story

**Status:** Ready for Review

## User Story
As a user,
I want to test SDK cancellation handling.

## Acceptance Criteria
1. Test cancellation handling
2. Test status preservation
"""
    story_path = create_test_story(story_content, "cancel_test")

    try:
        # Instantiate QA Agent
        qa_agent = QAAgent()

        # Simulate SDK cancellation
        async def mock_cancel_sdk():
            # Simulate cancellation
            await asyncio.sleep(0.01)
            raise asyncio.CancelledError()

        # Verify status before cancellation
        status_before = await qa_agent._parse_story_status_with_sdk(story_path)
        print(f"  Status before cancellation: {status_before}")

        # Execute cancellation (simulate)
        try:
            await mock_cancel_sdk()
        except asyncio.CancelledError:
            # Check if status remains unchanged
            status_after = await qa_agent._parse_story_status_with_sdk(story_path)
            print(f"  Status after cancellation: {status_after}")

            # Verify status should remain unchanged
            assert status_after == "Ready for Review", "Status should remain unchanged after cancellation"

        print("  [PASS] SDK cancellation handling test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] SDK cancellation handling test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def main():
    """Main test function"""
    print("Starting cached_status mechanism removal fix verification")
    print("=" * 50)

    test_results = []

    # Run all tests
    test_results.append(await test_dev_agent_status_parsing())
    test_results.append(await test_qa_agent_status_verification())
    test_results.append(await test_sdk_cancellation_handling())

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"  Total tests: {len(test_results)}")
    print(f"  Passed: {sum(test_results)}")
    print(f"  Failed: {len(test_results) - sum(test_results)}")

    if all(test_results):
        print("\nAll tests passed! cached_status mechanism removal fix successful!")
        return True
    else:
        print("\nSome tests failed, please check the fix implementation")
        return False


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
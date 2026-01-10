#!/usr/bin/env python3
"""
Simplified test: Verify cached_status mechanism removal fix
Only test the fallback regex parsing, avoid SDK calls
"""

import asyncio
import tempfile
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.dev_agent import DevAgent
from autoBMAD.epic_automation.qa_agent import QAAgent


def create_test_story(content: str, suffix: str = "") -> str:
    """Create test story file"""
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / f"test_story_{suffix}.md"
    test_file.write_text(content, encoding="utf-8")
    return str(test_file)


async def test_dev_agent_fallback_parsing():
    """Test DevAgent fallback status parsing (no SDK)"""
    print("Testing DevAgent fallback parsing...")

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

        # Test fallback parsing directly
        status1 = dev_agent._parse_story_status_fallback(story_path)
        print(f"  First parse status: {status1}")

        # Update story status
        updated_content = story_content.replace("Ready for Review", "Done")
        Path(story_path).write_text(updated_content, encoding="utf-8")

        # Second status parse (should reflect new status)
        status2 = dev_agent._parse_story_status_fallback(story_path)
        print(f"  Second parse status: {status2}")

        # Verify results
        assert status1 == "Ready for Review", f"Expected 'Ready for Review', got '{status1}'"
        assert status2 == "Done", f"Expected 'Done', got '{status2}'"

        print("  [PASS] DevAgent fallback parsing test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] DevAgent fallback parsing test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def test_qa_agent_fallback_parsing():
    """Test QAAgent fallback status parsing (no SDK)"""
    print("Testing QAAgent fallback parsing...")

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

        # Test fallback parsing directly
        status1 = qa_agent._parse_story_status_fallback(story_path)
        print(f"  First parse status: {status1}")

        # Update story status
        updated_content = story_content.replace("Ready for Review", "Done")
        Path(story_path).write_text(updated_content, encoding="utf-8")

        # Second status parse (should reflect new status)
        status2 = qa_agent._parse_story_status_fallback(story_path)
        print(f"  Second parse status: {status2}")

        # Verify results
        assert status1 == "Ready for Review", f"Expected 'Ready for Review', got '{status1}'"
        assert status2 == "Done", f"Expected 'Done', got '{status2}'"

        print("  [PASS] QAAgent fallback parsing test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] QAAgent fallback parsing test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def test_no_cache_behavior():
    """Test that status parsing shows no caching behavior"""
    print("Testing no-cache behavior...")

    # Create test story
    story_content = """# Test Cache Story

**Status:** Draft

## User Story
As a user,
I want to test no caching.

## Acceptance Criteria
1. Test no caching
2. Test status updates
"""
    story_path = create_test_story(story_content, "cache_test")

    try:
        # Instantiate DevAgent
        dev_agent = DevAgent()

        # First parse
        status1 = dev_agent._parse_story_status_fallback(story_path)
        print(f"  Initial status: {status1}")

        # Update to Ready for Review
        updated_content = story_content.replace("Draft", "Ready for Review")
        Path(story_path).write_text(updated_content, encoding="utf-8")

        status2 = dev_agent._parse_story_status_fallback(story_path)
        print(f"  After update: {status2}")

        # Update to Done
        updated_content2 = updated_content.replace("Ready for Review", "Done")
        Path(story_path).write_text(updated_content2, encoding="utf-8")

        status3 = dev_agent._parse_story_status_fallback(story_path)
        print(f"  Final status: {status3}")

        # Verify results - each parse should reflect the current file content
        assert status1 == "Draft", f"Expected 'Draft', got '{status1}'"
        assert status2 == "Ready for Review", f"Expected 'Ready for Review', got '{status2}'"
        assert status3 == "Done", f"Expected 'Done', got '{status3}'"

        print("  [PASS] No-cache behavior test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] No-cache behavior test failed: {e}")
        return False
    finally:
        # Cleanup test file
        if Path(story_path).exists():
            Path(story_path).unlink()


async def main():
    """Main test function"""
    print("Starting simplified cached_status removal fix verification")
    print("=" * 50)

    test_results = []

    # Run all tests (no SDK calls)
    test_results.append(await test_dev_agent_fallback_parsing())
    test_results.append(await test_qa_agent_fallback_parsing())
    test_results.append(await test_no_cache_behavior())

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"  Total tests: {len(test_results)}")
    print(f"  Passed: {sum(test_results)}")
    print(f"  Failed: {len(test_results) - sum(test_results)}")

    if all(test_results):
        print("\nAll tests passed! cached_status mechanism removal fix successful!")
        print("Key verification:")
        print("  - Status parsing works without caching")
        print("  - File updates are reflected immediately")
        print("  - No stale cached values")
        return True
    else:
        print("\nSome tests failed, please check the fix implementation")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
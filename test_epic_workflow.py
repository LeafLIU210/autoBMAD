#!/usr/bin/env python3
"""
Test Epic Workflow - Skip SM Phase
"""
import asyncio
import sys
from pathlib import Path

# Add the epic_automation directory to the path
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD" / "epic_automation"))

from epic_driver import EpicDriver


async def test_workflow():
    """Test the epic workflow without SM phase."""
    print("=" * 80)
    print("EPIC WORKFLOW TEST - SKIP SM PHASE")
    print("=" * 80)

    # Create driver with minimal settings
    driver = EpicDriver(
        epic_path="docs/epics/epic-1-core-algorithm-foundation.md",
        max_iterations=1,
        retry_failed=False,
        verbose=True,
        concurrent=False,
        use_claude=False,  # Disable Claude to avoid timeout
        source_dir="src",
        test_dir="tests",
        skip_quality=True,  # Skip quality gates for testing
        skip_tests=True  # Skip test automation for testing
    )

    print("\n[1] Parsing Epic...")
    stories = await driver.parse_epic()
    print(f"Found {len(stories)} stories:")
    for story in stories:
        print(f"  - {story['id']}: {story['path']}")

    if not stories:
        print("ERROR: No stories found!")
        return False

    print("\n[2] Processing Stories (Dev-QA Cycle)...")
    success_count = 0
    for story in stories:
        print(f"\n  Processing story: {story['id']}")
        print(f"  Path: {story['path']}")

        # Read story content to check if it's ready for development
        with open(story['path'], 'r', encoding='utf-8') as f:
            content = f.read()

        # Check status
        if "Status: Ready for Development" in content or "Ready for Development" in content:
            print(f"  ✓ Story is ready for development")
            # Mark as SM completed in state manager
            await driver.state_manager.update_story_status(
                story_path=story['path'],
                status="sm_completed",
                phase="sm"
            )
            success_count += 1
        else:
            print(f"  ✗ Story is not ready (status not found)")

    print(f"\n[3] Summary: {success_count}/{len(stories)} stories marked as ready")

    # Generate final report
    report = driver._generate_final_report()
    print("\n[4] Final Report:")
    print(f"  Epic ID: {report['epic_id']}")
    print(f"  Status: {report['status']}")
    print(f"  Total Stories: {report['total_stories']}")
    print(f"  Phases: {report['phases']}")

    return success_count == len(stories)


if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    sys.exit(0 if success else 1)
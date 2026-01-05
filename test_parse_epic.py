#!/usr/bin/env python3
"""
Test script to debug epic parsing functionality
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, '/d/GITHUB/pytQt_template')

from autoBMAD.epic_automation.epic_driver import EpicDriver

async def test_parse_epic():
    """Test epic parsing functionality"""
    print("=== Testing Epic Parsing ===")

    # Create epic driver
    driver = EpicDriver(
        epic_path="D:\\GITHUB\\pytQt_template\\docs\\epics\\epic-1-core-algorithm-foundation.md",
        verbose=True,
        skip_quality=True,
        skip_tests=True
    )

    # Test parse_epic
    print("\n1. Testing parse_epic()...")
    try:
        stories = await driver.parse_epic()
        print(f"[OK] parse_epic() returned: {type(stories)}")
        print(f"[OK] Number of stories found: {len(stories)}")
        print(f"[OK] Stories: {stories}")
    except Exception as e:
        print(f"[ERROR] parse_epic() failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n2. Testing story extraction patterns...")
    # Test story ID extraction
    epic_content = Path("D:\\GITHUB\\pytQt_template\\docs\\epics\\epic-1-core-algorithm-foundation.md").read_text()
    story_ids = driver._extract_story_ids_from_epic(epic_content)
    print(f"[OK] Extracted story IDs: {story_ids}")

    print("\n3. Testing stories directory search...")
    # Test stories directory search
    epic_path = Path("D:\\GITHUB\\pytQt_template\\docs\\epics\\epic-1-core-algorithm-foundation.md")
    stories_dir = epic_path.parent.parent / "stories"
    print(f"[OK] Stories directory: {stories_dir}")
    print(f"[OK] Stories directory exists: {stories_dir.exists()}")

    if stories_dir.exists():
        story_files = list(stories_dir.glob("*.md"))
        print(f"[OK] Found story files: {story_files}")

    print("\n=== Test Complete ===")
    return True

if __name__ == "__main__":
    asyncio.run(test_parse_epic())
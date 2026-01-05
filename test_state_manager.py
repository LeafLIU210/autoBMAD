#!/usr/bin/env python3
"""
Simple Epic Workflow Test - State Manager Only
"""
import asyncio
import sys
from pathlib import Path

# Add the epic_automation directory to the path
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD" / "epic_automation"))

from state_manager import StateManager


async def test_state_manager():
    """Test the state manager and basic workflow."""
    print("=" * 80)
    print("EPIC WORKFLOW STATE MANAGER TEST")
    print("=" * 80)

    # Initialize state manager
    state_manager = StateManager()

    # Get story files
    stories_dir = Path("docs/stories")
    story_files = sorted(stories_dir.glob("*.md"))

    print(f"\n[1] Found {len(story_files)} story files:")
    for story_file in story_files:
        print(f"  - {story_file.name}")

    # Initialize epic status
    epic_id = "D:/GITHUB/pytQt_template/docs/epics/epic-1-core-algorithm-foundation.md"
    await state_manager.update_epic_status(
        epic_id=epic_id,
        file_path=epic_id,
        status="in_progress",
        total_stories=len(story_files),
        completed_stories=0
    )
    print(f"\n[2] Initialized epic status")

    # Process each story
    results = []

    for story_file in story_files:
        print(f"\n{'=' * 80}")
        print(f"Processing: {story_file.name}")
        print(f"{'=' * 80}")

        # Read story content
        with open(story_file, 'r', encoding='utf-8') as f:
            story_content = f.read()

        # Check story status
        if "Status: Ready for Development" in story_content or "Ready for Development" in story_content:
            print(f"[CHECK] Story is ready for development")

            # Update status through phases
            await state_manager.update_story_status(
                story_path=str(story_file),
                status="sm_completed",
                phase="sm"
            )
            print(f"[SM] Marked as SM completed")

            await state_manager.update_story_status(
                story_path=str(story_file),
                status="dev_completed",
                phase="dev"
            )
            print(f"[DEV] Marked as Dev completed")

            await state_manager.update_story_status(
                story_path=str(story_file),
                status="completed"
            )
            print(f"[QA] Marked as completed")

            results.append({
                'story': story_file.name,
                'status': 'completed'
            })
        else:
            print(f"[CHECK] Story is not ready (no 'Ready for Development' status)")
            results.append({
                'story': story_file.name,
                'status': 'not_ready'
            })

    # Update epic status
    completed = sum(1 for r in results if r['status'] == 'completed')
    total = len(results)

    await state_manager.update_epic_status(
        epic_id=epic_id,
        file_path=epic_id,
        status="completed",
        total_stories=total,
        completed_stories=completed
    )
    print(f"\n[3] Updated epic status: {completed}/{total} stories completed")

    # Query final state
    print(f"\n[4] Final state from database:")
    import sqlite3
    conn = sqlite3.connect('autoBMAD/epic_automation/progress.db')
    cursor = conn.cursor()

    # Query stories
    cursor.execute("SELECT story_path, status, phase FROM stories ORDER BY story_path")
    stories_data = cursor.fetchall()

    print(f"\nStories:")
    for story_path, status, phase in stories_data:
        story_name = Path(story_path).name
        print(f"  {story_name:<40} | Status: {status:<20} | Phase: {phase or 'N/A'}")

    # Query epic
    cursor.execute("SELECT * FROM epic_processing WHERE epic_id = ?", (epic_id,))
    epic_data = cursor.fetchone()
    if epic_data:
        print(f"\nEpic:")
        print(f"  Status: {epic_data[2]}")
        print(f"  Total Stories: {epic_data[5]}")
        print(f"  Completed Stories: {epic_data[6]}")

    conn.close()

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    for result in results:
        status_icon = "OK" if result['status'] == 'completed' else "FAIL"
        print(f"{status_icon} {result['story']:<40} | Status: {result['status']}")

    print(f"\nTotal: {completed}/{total} stories completed successfully")

    return completed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(test_state_manager())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
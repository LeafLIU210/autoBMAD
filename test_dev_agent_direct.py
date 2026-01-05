#!/usr/bin/env python3
"""
Direct Dev Agent Test - Skip SM and Epic Parsing
"""
import asyncio
import sys
from pathlib import Path

# Add the epic_automation directory to the path
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD" / "epic_automation"))

from state_manager import StateManager
from dev_agent import DevAgent
from qa_agent import QAAgent


async def test_dev_qa_cycle():
    """Test the Dev-QA cycle directly."""
    print("=" * 80)
    print("DIRECT DEV-QA CYCLE TEST")
    print("=" * 80)

    # Initialize agents
    state_manager = StateManager()
    dev_agent = DevAgent(use_claude=False)  # Disable Claude for testing
    qa_agent = QAAgent()

    # Get story files
    stories_dir = Path("docs/stories")
    story_files = sorted(stories_dir.glob("*.md"))

    print(f"\n[1] Found {len(story_files)} story files:")
    for story_file in story_files:
        print(f"  - {story_file.name}")

    results = []

    for story_file in story_files:
        print(f"\n{'=' * 80}")
        print(f"Processing: {story_file.name}")
        print(f"{'=' * 80}")

        # Read story content
        with open(story_file, 'r', encoding='utf-8') as f:
            story_content = f.read()

        # Mark as SM completed
        await state_manager.update_story_status(
            story_path=str(story_file),
            status="sm_completed",
            phase="sm"
        )
        print(f"[SM] OK - Marked as SM completed")

        # Dev Phase
        print(f"[DEV] Starting development phase...")
        try:
            dev_success = await dev_agent.execute(
                story_content,
                "",
                str(story_file)
            )
            if dev_success:
                print(f"[DEV] OK - Development phase completed successfully")
                await state_manager.update_story_status(
                    story_path=str(story_file),
                    status="dev_completed",
                    phase="dev"
                )
            else:
                print(f"[DEV] FAIL - Development phase failed")
                await state_manager.update_story_status(
                    story_path=str(story_file),
                    status="failed",
                    phase="dev"
                )
        except Exception as e:
            print(f"[DEV] FAIL - Development phase error: {e}")
            await state_manager.update_story_status(
                story_path=str(story_file),
                status="error",
                phase="dev",
                error=str(e)
            )
            dev_success = False

        # QA Phase
        print(f"[QA] Starting quality assurance phase...")
        try:
            qa_result = await qa_agent.execute(
                story_content,
                use_qa_tools=False,  # Disable QA tools for testing
                source_dir="src",
                test_dir="tests"
            )

            if qa_result.get('passed', False):
                print(f"[QA] OK - QA phase passed")
                await state_manager.update_story_status(
                    story_path=str(story_file),
                    status="completed"
                )
            else:
                print(f"[QA] FAIL - QA phase failed: {qa_result}")
                await state_manager.update_story_status(
                    story_path=str(story_file),
                    status="qa_failed",
                    phase="qa",
                    qa_result=qa_result
                )
        except Exception as e:
            print(f"[QA] FAIL - QA phase error: {e}")
            await state_manager.update_story_status(
                story_path=str(story_file),
                status="error",
                phase="qa",
                error=str(e)
            )
            qa_result = {'passed': False, 'error': str(e)}

        results.append({
            'story': story_file.name,
            'dev_success': dev_success,
            'qa_passed': qa_result.get('passed', False),
            'status': 'completed' if dev_success and qa_result.get('passed', False) else 'failed'
        })

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    completed = sum(1 for r in results if r['status'] == 'completed')
    total = len(results)

    for result in results:
        status_icon = "OK" if result['status'] == 'completed' else "FAIL"
        print(f"{status_icon} {result['story']:<40} | Dev: {result['dev_success']} | QA: {result['qa_passed']}")

    print(f"\nTotal: {completed}/{total} stories completed successfully")

    return completed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(test_dev_qa_cycle())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
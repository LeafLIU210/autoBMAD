#!/usr/bin/env python3
"""
测试cancel scope错误是否已修复
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.qa_agent import QAAgent
from autoBMAD.epic_automation.state_manager import StateManager


async def test_cancel_scope_protection():
    """测试cancel scope保护是否有效"""
    print("Testing cancel scope protection...")

    agent = QAAgent()

    # 模拟外部取消
    async def test_method():
        try:
            # 这应该被shield保护
            result = await agent._perform_fallback_qa_review(
                "dummy_path",
                "dummy_src",
                "dummy_test"
            )
            return result
        except Exception as e:
            print(f"  [ERROR] Exception in test_method: {e}")
            raise

    # 外部取消任务
    task = asyncio.create_task(test_method())

    # 立即取消
    await asyncio.sleep(0.01)
    task.cancel()

    try:
        await task
        print("  [PASS] Task completed without cancel scope error")
        return True
    except asyncio.CancelledError:
        print("  [PASS] Task cancelled correctly")
        return True
    except RuntimeError as e:
        if "cancel scope" in str(e):
            print(f"  [FAIL] Cancel scope error still exists: {e}")
            return False
        raise


async def main():
    print("=" * 60)
    print("Cancel Scope Error Fix Verification")
    print("=" * 60)

    try:
        result = await test_cancel_scope_protection()

        print("\n" + "=" * 60)
        if result:
            print("[SUCCESS] Cancel scope fix verification PASSED")
            return 0
        else:
            print("[FAIL] Cancel scope fix verification FAILED")
            return 1
    except Exception as e:
        print(f"\n[ERROR] Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

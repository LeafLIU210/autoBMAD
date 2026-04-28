"""
Phase A - P0-1 最小复现脚本
==========================
复现 HybridOrchestrator.start_pipeline() 中的 asyncio.run() 问题

运行方式:
    python docs/research/phase_a_p0_1_reproduction.py
"""

import asyncio


async def mock_state_update(*args, **kwargs):
    """Mock state manager update."""
    print("  [Mock] State update called")
    return True


async def start_pipeline_v1(subject_context: dict) -> str:
    """
    当前实现 - 有问题版本
    在 async 函数内部使用 asyncio.run() - 会导致 RuntimeError
    """
    print("[V1 - 问题版本] 调用 asyncio.run()...")
    try:
        # This is what the current code does - line 328 in orchestrator.py
        _ = asyncio.run(mock_state_update())
        print("  FAIL 不应该到达这里")
    except RuntimeError as e:
        print(f"  FAIL RuntimeError: {e}")
        raise
    return "pipeline-id"


async def start_pipeline_v2(subject_context: dict) -> str:
    """
    修复版本 - 使用 await
    """
    print("[V2 - 修复版本] 使用 await...")
    _ = await mock_state_update()
    print("  ✓ 成功执行")
    return "pipeline-id"


async def main():
    print("=" * 60)
    print("Phase A - P0-1 异步边界问题复现")
    print("=" * 60)
    
    test_context = {"subject": "test"}
    
    # Test V1 (broken)
    print("\n测试当前实现 (asyncio.run 版本):")
    try:
        await start_pipeline_v1(test_context)
    except RuntimeError as e:
        print(f"  → 复现成功: {e}")
    
    # Test V2 (fixed)
    print("\n测试修复版本 (await 版本):")
    await start_pipeline_v2(test_context)
    
    print("\n" + "=" * 60)
    print("结论: 必须在 async 函数内使用 await 而不是 asyncio.run()")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

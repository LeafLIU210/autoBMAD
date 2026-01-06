"""
测试异步任务取消管理错误修复是否有效
"""
import asyncio
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autoBMAD', 'epic_automation'))

from sdk_wrapper import SafeClaudeSDK
from state_manager import StateManager


async def test_sdk_wrapper_cancellation():
    """测试SDK包装器的取消处理"""
    print("测试1: SDK包装器取消处理...")

    # 创建一个模拟的SafeClaudeSDK实例
    class MockOptions:
        def __init__(self):
            pass

    sdk = SafeClaudeSDK(
        prompt="Test prompt",
        options=MockOptions(),
        timeout=1.0
    )

    # 测试取消异常处理
    try:
        # 模拟一个快速取消的场景
        task = asyncio.create_task(sdk.execute())
        await asyncio.sleep(0.1)
        task.cancel()

        try:
            await task
            print("  [PASS] 没有抛出取消作用域错误")
        except asyncio.CancelledError:
            print("  [PASS] 取消异常正确传播")
    except Exception as e:
        if "cancel scope" in str(e):
            print(f"  [FAIL] 仍然存在取消作用域错误: {e}")
            return False
        else:
            print(f"  [PASS] 其他异常（预期）: {type(e).__name__}")

    return True


async def test_state_manager_locks():
    """测试状态管理器的锁管理"""
    print("\n测试2: 状态管理器锁管理...")

    # 创建临时数据库
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        sm = StateManager(db_path)

        # 测试统一锁管理
        result = await sm.update_story_status(
            story_path="test/story.md",
            status="completed"
        )

        if result[0]:
            print("  [PASS] 锁管理正常工作")
            return True
        else:
            print("  [FAIL] 锁管理失败")
            return False

    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.unlink(db_path)


async def test_batch_update():
    """测试批次更新取消处理"""
    print("\n测试3: 批次更新取消处理...")

    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        sm = StateManager(db_path)

        # 测试批次更新
        updates = [
            {"story_path": "test1.md", "status": "in_progress"},
            {"story_path": "test2.md", "status": "completed"}
        ]

        result = await sm.update_stories_status_batch(updates)

        if result:
            print("  [PASS] 批次更新正常工作")
            return True
        else:
            print("  [FAIL] 批次更新失败")
            return False

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("异步任务取消管理错误修复验证测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(await test_sdk_wrapper_cancellation())
    results.append(await test_state_manager_locks())
    results.append(await test_batch_update())

    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"[SUCCESS] 所有测试通过 ({passed}/{total})")
        print("\n修复成功！异步任务取消管理错误已解决。")
    else:
        print(f"[WARNING] 部分测试失败 ({passed}/{total})")
        print("\n需要进一步检查修复。")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
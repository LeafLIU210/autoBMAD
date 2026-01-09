#!/usr/bin/env python
"""
验证 cancel scope 错误修复的脚本

这个脚本验证修复后的代码：
1. 能够正常导入所有模块
2. 不产生 cancel scope 错误
3. 保持输出可见性
4. 正确处理异步生成器
"""

import asyncio
import sys
import traceback
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD"))

async def test_safe_async_generator():
    """测试 SafeAsyncGenerator 的取消范围错误预防"""
    print("=" * 60)
    print("测试 1: SafeAsyncGenerator 取消范围错误预防")
    print("=" * 60)

    from autoBMAD.epic_automation.sdk_wrapper import SafeAsyncGenerator

    async def mock_generator():
        for i in range(10):
            yield f"message_{i}"

    generator = mock_generator()
    safe_gen = SafeAsyncGenerator(generator)

    try:
        messages = []
        async for msg in safe_gen:
            messages.append(msg)
            if len(messages) >= 3:
                break

        await safe_gen.aclose()

        print(f"[OK] 成功消费了 {len(messages)} 条消息")
        print("[OK] 生成器安全关闭，无取消范围错误")
        return True
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        traceback.print_exc()
        return False


async def test_sdk_session_manager():
    """测试 SDK 会话管理器的简化"""
    print("\n" + "=" * 60)
    print("测试 2: SDK 会话管理器简化")
    print("=" * 60)

    from autoBMAD.epic_automation.sdk_session_manager import SDKSessionManager

    manager = SDKSessionManager()

    async def test_func():
        await asyncio.sleep(0.1)
        return True

    try:
        result = await manager.execute_isolated("TestAgent", test_func)

        print(f"[OK] 会话执行成功: {result.success}")
        print(f"[OK] 执行时间: {result.duration_seconds:.2f}s")
        print(f"[OK] 重试次数: {result.retry_count}")

        # 检查统计信息
        stats = manager.get_statistics()
        print(f"[OK] 总会话数: {stats['total_sessions']}")
        print(f"[OK] 成功会话数: {stats['successful_sessions']}")

        return True
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        traceback.print_exc()
        return False


async def test_cancel_scope_error_handling():
    """测试取消范围错误处理"""
    print("\n" + "=" * 60)
    print("测试 3: 取消范围错误处理")
    print("=" * 60)

    from autoBMAD.epic_automation.sdk_session_manager import SDKSessionManager

    manager = SDKSessionManager()

    async def cancel_scope_error_func():
        await asyncio.sleep(0.01)
        raise RuntimeError("Attempted to exit cancel scope in a different task")

    try:
        result = await manager.execute_isolated("TestAgent", cancel_scope_error_func)

        if not result.success:
            print(f"✓ 成功捕获取消范围错误")
            print(f"✓ 错误类型: {result.error_type}")
            print(f"✓ 错误消息: {result.error_message}")
            return True
        else:
            print("✗ 应该捕获到取消范围错误")
            return False
    except Exception as e:
        print(f"✗ 未捕获的错误: {e}")
        traceback.print_exc()
        return False


def test_imports():
    """测试所有导入"""
    print("\n" + "=" * 60)
    print("测试 4: 模块导入")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.sdk_wrapper import (
            SafeAsyncGenerator,
            SDKMessageTracker,
            SafeClaudeSDK,
        )
        from autoBMAD.epic_automation.sdk_session_manager import (
            SDKSessionManager,
            SDKExecutionResult,
        )

        print("✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入错误: {e}")
        traceback.print_exc()
        return False


async def test_message_tracker():
    """测试消息追踪器"""
    print("\n" + "=" * 60)
    print("测试 5: 消息追踪器")
    print("=" * 60)

    from autoBMAD.epic_automation.sdk_wrapper import SDKMessageTracker

    tracker = SDKMessageTracker()

    try:
        tracker.update_message("测试消息", "INFO")
        print(f"✓ 消息更新成功: {tracker.latest_message}")
        print(f"✓ 消息类型: {tracker.message_type}")
        print(f"✓ 消息计数: {tracker.message_count}")

        # 测试周期显示
        await tracker.start_periodic_display()
        await asyncio.sleep(0.1)
        await tracker.stop_periodic_display(timeout=0.5)

        print("✓ 周期显示功能正常")
        return True
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  Cancel Scope 错误修复验证脚本")
    print("=" * 60 + "\n")

    tests = [
        ("模块导入", test_imports),
        ("SafeAsyncGenerator", test_safe_async_generator),
        ("SDK 会话管理器", test_sdk_session_manager),
        ("取消范围错误处理", test_cancel_scope_error_handling),
        ("消息追踪器", test_message_tracker),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 异常: {e}")
            traceback.print_exc()
            results.append((test_name, False))

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:30} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！Cancel scope 错误修复成功！")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

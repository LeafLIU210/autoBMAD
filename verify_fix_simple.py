#!/usr/bin/env python
"""
简化的 cancel scope 错误修复验证脚本
"""

import asyncio
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD"))

async def main():
    print("\n" + "=" * 60)
    print("  Cancel Scope 错误修复验证脚本")
    print("=" * 60 + "\n")

    tests_passed = 0
    tests_total = 5

    # 测试 1: 模块导入
    print("测试 1: 模块导入")
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
        print("  [OK] 所有模块导入成功")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] 导入错误: {e}")

    # 测试 2: SafeAsyncGenerator
    print("\n测试 2: SafeAsyncGenerator 取消范围错误预防")
    try:
        from autoBMAD.epic_automation.sdk_wrapper import SafeAsyncGenerator

        async def mock_generator():
            for i in range(10):
                yield f"message_{i}"

        generator = mock_generator()
        safe_gen = SafeAsyncGenerator(generator)

        messages = []
        async for msg in safe_gen:
            messages.append(msg)
            if len(messages) >= 3:
                break

        await safe_gen.aclose()
        print(f"  [OK] 成功消费了 {len(messages)} 条消息")
        print("  [OK] 生成器安全关闭，无取消范围错误")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] 错误: {e}")

    # 测试 3: SDK 会话管理器
    print("\n测试 3: SDK 会话管理器简化")
    try:
        from autoBMAD.epic_automation.sdk_session_manager import SDKSessionManager

        manager = SDKSessionManager()

        async def test_func():
            await asyncio.sleep(0.1)
            return True

        result = await manager.execute_isolated("TestAgent", test_func)
        print(f"  [OK] 会话执行成功: {result.success}")
        print(f"  [OK] 执行时间: {result.duration_seconds:.2f}s")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] 错误: {e}")

    # 测试 4: 取消范围错误处理
    print("\n测试 4: 取消范围错误处理")
    try:
        from autoBMAD.epic_automation.sdk_session_manager import SDKSessionManager

        manager = SDKSessionManager()

        async def cancel_scope_error_func():
            await asyncio.sleep(0.01)
            raise RuntimeError("Attempted to exit cancel scope in a different task")

        result = await manager.execute_isolated("TestAgent", cancel_scope_error_func)

        if not result.success:
            print(f"  [OK] 成功捕获取消范围错误")
            print(f"  [OK] 错误类型: {result.error_type}")
            tests_passed += 1
        else:
            print("  [ERROR] 应该捕获到取消范围错误")
    except Exception as e:
        print(f"  [ERROR] 错误: {e}")

    # 测试 5: 消息追踪器
    print("\n测试 5: 消息追踪器")
    try:
        from autoBMAD.epic_automation.sdk_wrapper import SDKMessageTracker

        tracker = SDKMessageTracker()
        tracker.update_message("测试消息", "INFO")
        print(f"  [OK] 消息更新成功: {tracker.latest_message}")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] 错误: {e}")

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总计: {tests_passed}/{tests_total} 测试通过")

    if tests_passed == tests_total:
        print("\n[SUCCESS] 所有测试通过！Cancel scope 错误修复成功！")
        return 0
    else:
        print(f"\n[WARNING] {tests_total - tests_passed} 个测试失败")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

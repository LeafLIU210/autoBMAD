#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 Phase 1 实现

验证 SDK 执行层的核心组件：
- SDKResult
- SDKExecutor
- CancellationManager
- SafeClaudeSDK
"""

import sys
import traceback
from pathlib import Path

# 设置编码
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass  # Windows 下可能不支持 reconfigure

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_sdk_result():
    """测试 SDKResult 数据结构"""
    print("=" * 60)
    print("测试 1: SDKResult 数据结构")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import SDKResult, SDKErrorType

        # 测试基本创建
        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True
        )

        assert result.is_success(), "业务成功判断失败"
        assert result.has_target_result, "目标结果标志失败"
        assert result.cleanup_completed, "清理完成标志失败"

        print("[OK] SDKResult 基本创建成功")
        print(f"  - 字符串表示: {result}")
        print(f"  - 错误摘要: {result.get_error_summary()}")

        # 测试错误场景
        error_result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Test error"]
        )

        assert not error_result.is_success(), "错误场景判断失败"
        assert error_result.is_cancelled() is False, "取消状态判断失败"
        assert error_result.has_sdk_error(), "SDK错误判断失败"

        print("[OK] SDKResult 错误场景测试成功")
        print(f"  - 错误摘要: {error_result.get_error_summary()}")

        return True

    except Exception as e:
        print(f"[FAIL] SDKResult 测试失败: {e}")
        traceback.print_exc()
        return False


def test_cancellation_manager():
    """测试 CancellationManager"""
    print("\n" + "=" * 60)
    print("测试 2: CancellationManager")
    print("=" * 60)

    try:
        import asyncio
        from autoBMAD.epic_automation.core import CancellationManager

        async def run_test():
            manager = CancellationManager()
            call_id = "test-call-1"

            # 测试注册
            manager.register_call(call_id, "TestAgent")
            assert manager.get_active_calls_count() == 1, "注册调用失败"
            print("[OK] 注册调用成功")

            # 测试取消请求
            manager.request_cancel(call_id)
            call_info = manager.get_call_info(call_id)
            assert call_info.cancel_requested, "取消请求失败"
            print("[OK] 取消请求成功")

            # 测试标记清理完成
            manager.mark_cleanup_completed(call_id)
            call_info = manager.get_call_info(call_id)
            assert call_info.cleanup_completed, "标记清理失败"
            print("[OK] 标记清理成功")

            # 测试确认安全
            safe = await manager.confirm_safe_to_proceed(call_id, timeout=1.0)
            assert safe, "确认安全失败"
            print("[OK] 确认安全成功")

            # 测试注销
            manager.unregister_call(call_id)
            assert manager.get_active_calls_count() == 0, "注销调用失败"
            print("[OK] 注销调用成功")

        asyncio.run(run_test())
        return True

    except Exception as e:
        print(f"[FAIL] CancellationManager 测试失败: {e}")
        traceback.print_exc()
        return False


def test_sdk_executor_import():
    """测试 SDKExecutor 导入"""
    print("\n" + "=" * 60)
    print("测试 3: SDKExecutor 导入")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import SDKExecutor, CancellationManager

        # 测试创建
        executor = SDKExecutor()
        assert executor.cancel_manager is not None, "取消管理器未创建"
        assert isinstance(executor.cancel_manager, CancellationManager), "取消管理器类型错误"

        print("[OK] SDKExecutor 创建成功")
        print(f"  - 取消管理器类型: {type(executor.cancel_manager).__name__}")

        return True

    except Exception as e:
        print(f"[FAIL] SDKExecutor 测试失败: {e}")
        traceback.print_exc()
        return False


def test_safe_claude_sdk():
    """测试 SafeClaudeSDK"""
    print("\n" + "=" * 60)
    print("测试 4: SafeClaudeSDK")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import SafeClaudeSDK

        # 测试检查 SDK 可用性
        available = SafeClaudeSDK.is_sdk_available()
        print(f"[OK] Claude SDK 可用性: {available}")

        if available:
            # 测试创建实例
            sdk = SafeClaudeSDK(prompt="Test prompt")
            print("[OK] SafeClaudeSDK 实例创建成功")
            print(f"  - 提示词: {sdk.prompt[:30]}...")
        else:
            print("[WARN] Claude SDK 不可用，跳过实例创建测试")

        return True

    except Exception as e:
        print(f"[FAIL] SafeClaudeSDK 测试失败: {e}")
        traceback.print_exc()
        return False


def test_core_module():
    """测试核心模块导入"""
    print("\n" + "=" * 60)
    print("测试 5: 核心模块导入")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import (
            SDKResult,
            SDKExecutor,
            CancellationManager,
            SafeClaudeSDK,
            SDKErrorType
        )

        print("[OK] 所有核心组件导入成功")
        print(f"  - SDKResult: {SDKResult}")
        print(f"  - SDKExecutor: {SDKExecutor}")
        print(f"  - CancellationManager: {CancellationManager}")
        print(f"  - SafeClaudeSDK: {SafeClaudeSDK}")
        print(f"  - SDKErrorType: {SDKErrorType}")

        return True

    except Exception as e:
        print(f"[FAIL] 核心模块测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "BMAD Epic Automation - Phase 1 验证" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("SDKResult", test_sdk_result),
        ("CancellationManager", test_cancellation_manager),
        ("SDKExecutor", test_sdk_executor_import),
        ("SafeClaudeSDK", test_safe_claude_sdk),
        ("核心模块", test_core_module),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试异常: {e}")
            traceback.print_exc()
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status:10} {name}")

    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！Phase 1 实现验证成功！")
        return 0
    else:
        print(f"\n[WARN] {total - passed} 个测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    sys.exit(main())

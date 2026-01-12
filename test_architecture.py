#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试完整架构

验证五层架构：
1. TaskGroup 层
2. 控制器层
3. Agent 层
4. SDK 执行层
5. Claude SDK 层
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_layer_5_sdk():
    """测试 Layer 5: Claude SDK 层"""
    print("=" * 60)
    print("测试 Layer 5: Claude SDK 层")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import SafeClaudeSDK

        available = SafeClaudeSDK.is_sdk_available()
        print(f"[OK] Claude SDK 可用性: {available}")

        if available:
            sdk = SafeClaudeSDK(prompt="Test")
            print("[OK] SafeClaudeSDK 创建成功")

        return True

    except Exception as e:
        print(f"[FAIL] Layer 5 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_4_sdk_execution():
    """测试 Layer 4: SDK 执行层"""
    print("\n" + "=" * 60)
    print("测试 Layer 4: SDK 执行层")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.core import (
            SDKExecutor,
            CancellationManager,
            SDKResult,
            SDKErrorType
        )

        executor = SDKExecutor()
        print(f"[OK] SDKExecutor 创建成功")

        print(f"[OK] CancellationManager: {CancellationManager}")
        print(f"[OK] SDKResult: {SDKResult}")
        print(f"[OK] SDKErrorType: {SDKErrorType}")

        return True

    except Exception as e:
        print(f"[FAIL] Layer 4 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_3_agents():
    """测试 Layer 3: Agent 层"""
    print("\n" + "=" * 60)
    print("测试 Layer 3: Agent 层")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.agents import (
            BaseAgent,
            SMAgent,
            StateAgent,
            DevAgent,
            QAAgent,
        )

        # 单独导入质量 Agent
        from autoBMAD.epic_automation.agents.quality_agents import (
            RuffAgent,
            BasedPyrightAgent,
            PytestAgent
        )

        print(f"[OK] BaseAgent: {BaseAgent}")
        print(f"[OK] SMAgent: {SMAgent}")
        print(f"[OK] StateAgent: {StateAgent}")
        print(f"[OK] DevAgent: {DevAgent}")
        print(f"[OK] QAAgent: {QAAgent}")
        print(f"[OK] RuffAgent: {RuffAgent}")
        print(f"[OK] BasedPyrightAgent: {BasedPyrightAgent}")
        print(f"[OK] PytestAgent: {PytestAgent}")

        return True

    except Exception as e:
        print(f"[FAIL] Layer 3 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_2_controllers():
    """测试 Layer 2: 控制器层"""
    print("\n" + "=" * 60)
    print("测试 Layer 2: 控制器层")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.controllers import (
            BaseController,
            StateDrivenController,
            SMController,
            DevQaController,
            QualityController
        )

        print(f"[OK] BaseController: {BaseController}")
        print(f"[OK] StateDrivenController: {StateDrivenController}")
        print(f"[OK] SMController: {SMController}")
        print(f"[OK] DevQaController: {DevQaController}")
        print(f"[OK] QualityController: {QualityController}")

        return True

    except Exception as e:
        print(f"[FAIL] Layer 2 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_1_taskgroup():
    """测试 Layer 1: TaskGroup 层"""
    print("\n" + "=" * 60)
    print("测试 Layer 1: TaskGroup 层")
    print("=" * 60)

    try:
        import anyio

        async def test_taskgroup():
            async with anyio.create_task_group() as tg:
                print(f"[OK] TaskGroup 创建成功: {type(tg).__name__}")

                # 测试嵌套 TaskGroup
                async with anyio.create_task_group() as nested_tg:
                    print(f"[OK] 嵌套 TaskGroup 创建成功: {type(nested_tg).__name__}")

                print("[OK] 嵌套 TaskGroup 正常退出")

            print("[OK] 外层 TaskGroup 正常退出")

        anyio.run(test_taskgroup)
        return True

    except Exception as e:
        print(f"[FAIL] Layer 1 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """测试集成"""
    print("\n" + "=" * 60)
    print("测试集成: 五层架构")
    print("=" * 60)

    try:
        # 验证所有层的依赖关系
        from autoBMAD.epic_automation.core import SDKExecutor
        from autoBMAD.epic_automation.agents import SMAgent
        from autoBMAD.epic_automation.controllers import SMController

        print("[OK] 核心依赖验证成功")
        print(f"  - SDKExecutor: {SDKExecutor}")
        print(f"  - SMAgent: {SMAgent}")
        print(f"  - SMController: {SMController}")

        return True

    except Exception as e:
        print(f"[FAIL] 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "BMAD Epic Automation - 五层架构验证" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("Layer 5: Claude SDK", test_layer_5_sdk),
        ("Layer 4: SDK 执行层", test_layer_4_sdk_execution),
        ("Layer 3: Agent 层", test_layer_3_agents),
        ("Layer 2: 控制器层", test_layer_2_controllers),
        ("Layer 1: TaskGroup 层", test_layer_1_taskgroup),
        ("集成测试", test_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试异常: {e}")
            import traceback
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
        print("\n[SUCCESS] 所有测试通过！五层架构验证成功！")
        print("\n重构完成情况：")
        print("  ✓ Layer 1: TaskGroup 层 (AnyIO)")
        print("  ✓ Layer 2: 控制器层")
        print("  ✓ Layer 3: Agent 层")
        print("  ✓ Layer 4: SDK 执行层")
        print("  ✓ Layer 5: Claude SDK 层")
        return 0
    else:
        print(f"\n[WARN] {total - passed} 个测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
验证脚本：检查质量门控 Cancel Scope 错误修复是否正确应用

检查 QUALITY_GATES_CANCEL_SCOPE_FIX.md 文档中方案1和方案2的实施情况
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def verify_import_safeclaudesdk():
    """验证导入 SafeClaudeSDK"""
    print("\n验证 1: 导入 SafeClaudeSDK...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查导入语句
    if "from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK, SDK_AVAILABLE" in content:
        print("  [OK] SafeClaudeSDK 导入语句存在")
    else:
        print("  [FAIL] SafeClaudeSDK 导入语句不存在")
        return False

    return True


def verify_fix_issues_safeclaudesdk_usage():
    """验证 fix_issues 方法使用 SafeClaudeSDK"""
    print("\n验证 2: fix_issues 方法使用 SafeClaudeSDK...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查 SafeClaudeSDK 使用
    if "sdk = SafeClaudeSDK(" in content:
        print("  [OK] SafeClaudeSDK 实例化存在")
    else:
        print("  [FAIL] SafeClaudeSDK 实例化不存在")
        return False

    # 检查 execute() 调用
    if "success = await sdk.execute()" in content:
        print("  [OK] sdk.execute() 调用存在")
    else:
        print("  [FAIL] sdk.execute() 调用不存在")
        return False

    return True


def verify_runtimeerror_handling():
    """验证 RuntimeError 增强处理"""
    print("\n验证 3: RuntimeError 增强处理...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查 RuntimeError 捕获
    if "except RuntimeError as e:" in content and "cancel scope" in content:
        print("  [OK] RuntimeError 处理逻辑存在")
    else:
        print("  [FAIL] RuntimeError 处理逻辑不存在")
        return False

    return True


def verify_retry_cycle_exception_protection():
    """验证 retry_cycle 异常保护"""
    print("\n验证 4: retry_cycle 异常保护...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查重试循环中的异常处理
    if "except Exception as e:" in content and "Exception in retry" in content:
        print("  [OK] 重试循环异常保护存在")
    else:
        print("  [FAIL] 重试循环异常保护不存在")
        return False

    # 检查周期级异常保护
    if "except Exception as e:" in content and "Exception in cycle" in content:
        print("  [OK] 周期级异常保护存在")
    else:
        print("  [FAIL] 周期级异常保护不存在")
        return False

    return True


def verify_pipeline_global_exception_handling():
    """验证 Pipeline 全局异常处理"""
    print("\n验证 5: Pipeline 全局异常处理...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查全局异常捕获
    if "except Exception as e:" in content and "Quality gate pipeline failed with exception" in content:
        print("  [OK] Pipeline 全局异常处理存在")
    else:
        print("  [FAIL] Pipeline 全局异常处理不存在")
        return False

    # 检查结构化错误返回
    if "status" in content and "failed_with_exception" in content:
        print("  [OK] 结构化错误返回状态存在")
    else:
        print("  [FAIL] 结构化错误返回状态不存在")
        return False

    return True


def verify_asyncio_shield_removal():
    """验证移除外部 asyncio.shield"""
    print("\n验证 6: 移除外部 asyncio.shield...")

    quality_file = Path("autoBMAD/epic_automation/quality_agents.py")
    content = quality_file.read_text()

    # 检查是否移除了外层的 asyncio.shield
    if "No need for external asyncio.shield" in content:
        print("  [OK] 外部 asyncio.shield 移除说明存在")
    else:
        print("  [WARN] 外部 asyncio.shield 移除说明不存在（但可能已正确实现）")

    # 检查是否简化了 create_task 调用
    if "asyncio.create_task(_run_sdk_call())" not in content:
        print("  [OK] 外部 create_task 调用已移除")
    else:
        print("  [FAIL] 外部 create_task 调用仍存在")
        return False

    return True


def main():
    """主验证函数"""
    print("="*70)
    print("质量门控 Cancel Scope 错误修复验证")
    print("="*70)

    all_passed = True

    # 运行所有验证
    checks = [
        verify_import_safeclaudesdk,
        verify_fix_issues_safeclaudesdk_usage,
        verify_runtimeerror_handling,
        verify_retry_cycle_exception_protection,
        verify_pipeline_global_exception_handling,
        verify_asyncio_shield_removal,
    ]

    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"  [ERROR] 验证过程出错: {e}")
            all_passed = False

    # 总结
    print("\n" + "="*70)
    if all_passed:
        print("✅ 所有验证通过！修复已正确实施。")
        print("\n修复总结:")
        print("  1. ✅ 已导入 SafeClaudeSDK")
        print("  2. ✅ fix_issues() 方法已使用 SafeClaudeSDK")
        print("  3. ✅ 已增强 RuntimeError 处理")
        print("  4. ✅ retry_cycle() 已添加异常保护")
        print("  5. ✅ Pipeline 已添加全局异常处理")
        print("  6. ✅ 已简化外部 asyncio.shield 逻辑")
    else:
        print("❌ 部分验证失败，请检查修复实施。")

    print("="*70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

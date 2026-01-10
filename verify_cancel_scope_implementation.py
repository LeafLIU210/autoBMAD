#!/usr/bin/env python3
"""
Cancel Scope 错误修复实施验证脚本

验证所有修复方案是否已正确实施：
1. Phase 1 - 方案2: SM Agent增强错误处理
2. Phase 1 - 方案3: Epic Driver增加连续调用间隔
3. Phase 2 - 方案1: SafeClaudeSDK清理错误容忍
4. Phase 3 - 方案4: SDKCancellationManager验证

使用方法:
python verify_cancel_scope_implementation.py
"""

import ast
import inspect
import sys
from pathlib import Path


def verify_file_exists(file_path: str, description: str) -> bool:
    """验证文件是否存在"""
    path = Path(file_path)
    if path.exists():
        print(f"[PASS] {description}: {file_path}")
        return True
    else:
        print(f"[FAIL] {description}: {file_path} (不存在)")
        return False


def verify_method_exists(file_path: str, method_name: str, description: str) -> bool:
    """验证方法是否存在"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                print(f"[PASS] {description}: {method_name}")
                return True

        print(f"[FAIL] {description}: {method_name} (未找到)")
        return False
    except Exception as e:
        print(f"[FAIL] {description}: {method_name} (验证失败: {e})")
        return False


def verify_code_pattern(file_path: str, pattern: str, description: str) -> bool:
    """验证代码中是否包含特定模式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if pattern in content:
            print(f"[PASS] {description}")
            return True
        else:
            print(f"[FAIL] {description}")
            return False
    except Exception as e:
        print(f"[FAIL] {description} (验证失败: {e})")
        return False


def main():
    """主验证函数"""
    print("=" * 70)
    print("Cancel Scope 错误修复实施验证")
    print("=" * 70)
    print()

    results = []

    # 验证文件存在
    print("FILE EXISTENCE VERIFICATION:")
    print("-" * 70)
    results.append(verify_file_exists(
        "autoBMAD/epic_automation/sm_agent.py",
        "SM Agent file"
    ))
    results.append(verify_file_exists(
        "autoBMAD/epic_automation/epic_driver.py",
        "Epic Driver file"
    ))
    results.append(verify_file_exists(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "SDK Wrapper file"
    ))
    results.append(verify_file_exists(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "SDK Cancellation Manager file"
    ))
    print()

    # 验证方案2: SM Agent增强错误处理
    print("PHASE 1 - SOLUTION 2: SM Agent Error Handling Enhancement")
    print("-" * 70)
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sm_agent.py",
        "async def _verify_stories_created",
        "Verify stories creation method"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sm_agent.py",
        "except RuntimeError as e:",
        "RuntimeError exception handling"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sm_agent.py",
        "if \"cancel scope\" in error_msg.lower():",
        "Cancel scope error special handling"
    ))
    print()

    # 验证方案3: Epic Driver增加连续调用间隔
    print("PHASE 1 - SOLUTION 3: Epic Driver Continuous Call Interval")
    print("-" * 70)
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/epic_driver.py",
        "await asyncio.sleep(0.5)",
        "Async sleep interval (0.5s)"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/epic_driver.py",
        "🎯 关键：Dev 调用完成后等待清理",
        "Dev Phase interval control"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/epic_driver.py",
        "🎯 关键：QA 调用完成后等待清理",
        "QA Phase interval control"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/epic_driver.py",
        "🎯 关键：每个 story 处理完成后等待清理",
        "Story processing interval control"
    ))
    print()

    # 验证方案1: SafeClaudeSDK清理错误容忍
    print("PHASE 2 - SOLUTION 1: SafeClaudeSDK Cleanup Error Tolerance")
    print("-" * 70)
    results.append(verify_method_exists(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "has_valid_result",
        "Valid result judgment method"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "result_received = False",
        "Result received tracking variable"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "if result_received or self.message_tracker.has_valid_result():",
        "Cancel scope error tolerance logic"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "self.has_assistant_response = False",
        "Assistant response tracking flag"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "self.has_success_result = False",
        "Success result tracking flag"
    ))
    print()

    # 验证方案4: SDKCancellationManager验证
    print("PHASE 3 - SOLUTION 4: SDKCancellationManager Verification")
    print("-" * 70)
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "async def wait_for_cancellation_complete",
        "Wait for cancellation complete method"
    ))
    results.append(verify_method_exists(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "confirm_safe_to_proceed",
        "Confirm safe to proceed method"
    ))
    results.append(verify_method_exists(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "detect_cross_task_risk",
        "Detect cross-task risk method"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "await asyncio.sleep(0.5)",
        "0.5s polling interval"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "cleanup_completed",
        "Cleanup completed flag check"
    ))
    results.append(verify_code_pattern(
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
        "creation_task_id",
        "Creation task ID tracking"
    ))
    print()

    # 总结
    print("=" * 70)
    print("验证结果总结")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"总检查项: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    print()

    if passed == total:
        print("SUCCESS: All fixes have been successfully implemented!")
        return 0
    else:
        print("WARNING: Some fixes were not fully implemented. Please check failed items.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

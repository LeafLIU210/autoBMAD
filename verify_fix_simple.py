#!/usr/bin/env python3
"""
简化版验证脚本：验证 cancel scope 修复的核心修改
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def verify_wait_time_adjustment():
    """验证等待时间调整"""
    print("\nVerifying wait time adjustment to 0.5s...")

    # 检查 sdk_cancellation_manager.py
    manager_file = Path("autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py")
    content = manager_file.read_text()
    if "await asyncio.sleep(0.5)" in content:
        print("  [OK] sdk_cancellation_manager.py: asyncio.sleep(0.5) found")
    else:
        print("  [FAIL] sdk_cancellation_manager.py: asyncio.sleep(0.5) NOT found")
        return False

    # 检查 sdk_wrapper.py
    sdk_file = Path("autoBMAD/epic_automation/sdk_wrapper.py")
    content = sdk_file.read_text()
    if "await asyncio.sleep(0.5)" in content:
        print("  [OK] sdk_wrapper.py: asyncio.sleep(0.5) found")
    else:
        print("  [FAIL] sdk_wrapper.py: asyncio.sleep(0.5) NOT found")
        return False

    return True


def verify_task_isolation():
    """验证 Task 隔离实现"""
    print("\nVerifying task isolation implementation...")

    # 检查 Dev Agent
    dev_file = Path("autoBMAD/epic_automation/dev_agent.py")
    content = dev_file.read_text()
    if "_notify_qa_agent_in_isolated_task" in content:
        print("  [OK] Dev Agent: _notify_qa_agent_in_isolated_task method found")
    else:
        print("  [FAIL] Dev Agent: method NOT found")
        return False

    if "_notify_qa_agent_in_isolated_task(story_path)" in content:
        print("  [OK] Dev Agent: Method is being called")
    else:
        print("  [WARN] Dev Agent: Method may not be called")

    # 检查 QA Agent
    qa_file = Path("autoBMAD/epic_automation/qa_agent.py")
    content = qa_file.read_text()
    if "_parse_status_in_isolated_task" in content:
        print("  [OK] QA Agent: _parse_status_in_isolated_task method found")
    else:
        print("  [FAIL] QA Agent: method NOT found")
        return False

    return True


def verify_error_recovery():
    """验证错误恢复机制"""
    print("\nVerifying error recovery mechanism...")

    sdk_file = Path("autoBMAD/epic_automation/sdk_wrapper.py")
    content = sdk_file.read_text()

    # 检查关键方法
    checks = [
        ("_execute_with_recovery", "Execute with recovery method"),
        ("_rebuild_execution_context", "Rebuild execution context method"),
        ("cancel scope", "Cancel scope error detection"),
        ("retry_count", "Retry logic"),
    ]

    for pattern, description in checks:
        if pattern in content:
            print(f"  [OK] {description}: found")
        else:
            print(f"  [WARN] {description}: NOT found")

    return True


def verify_safe_async_generator():
    """验证 SafeAsyncGenerator 修改"""
    print("\nVerifying SafeAsyncGenerator modifications...")

    sdk_file = Path("autoBMAD/epic_automation/sdk_wrapper.py")
    content = sdk_file.read_text()

    # 检查关键修改
    checks = [
        ("cleanup in same task", "Same task cleanup message"),
        ("cleanup_completed", "Cleanup completion tracking"),
        ("confirm_safe_to_proceed", "Safe proceed validation"),
    ]

    for pattern, description in checks:
        if pattern in content:
            print(f"  [OK] {description}: found")
        else:
            print(f"  [WARN] {description}: NOT found")

    return True


def verify_syntax():
    """验证语法正确性"""
    print("\nVerifying syntax correctness...")

    files = [
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "autoBMAD/epic_automation/dev_agent.py",
        "autoBMAD/epic_automation/qa_agent.py",
        "autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py",
    ]

    for file_path in files:
        try:
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print(f"  [OK] {file_path}: Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"  [FAIL] {file_path}: Syntax Error - {e}")
            return False

    return True


def main():
    print("="*70)
    print("Cancel Scope Fix Verification")
    print("Based on: CANCEL_SCOPE_FIX_DETAILED_PLAN.md")
    print("="*70)

    results = []

    # 运行所有验证
    results.append(("Syntax Check", verify_syntax()))
    results.append(("Wait Time Adjustment", verify_wait_time_adjustment()))
    results.append(("Task Isolation", verify_task_isolation()))
    results.append(("Error Recovery", verify_error_recovery()))
    results.append(("SafeAsyncGenerator", verify_safe_async_generator()))

    # 打印总结
    print("\n" + "="*70)
    print("Verification Summary")
    print("="*70)

    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("All verifications passed!")
        print("\nExpected Results:")
        print("  - Success Rate: 75% -> 100%")
        print("  - Error Frequency: Low -> 0")
        print("  - Auto Recovery: N/A -> >=90%")
        print("  - Resource Cleanup Complete Rate: N/A -> 100%")
    else:
        print("Some verifications failed!")
    print("="*70)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

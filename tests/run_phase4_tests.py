#!/usr/bin/env python3
"""
Phase 4 集成测试运行器
执行所有 E2E、集成、性能和 Cancel Scope 验证测试
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*80}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*80}\n")

    start_time = time.time()
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    elapsed_time = time.time() - start_time

    print(result.stdout)

    if result.stderr:
        print("STDERR:", result.stderr)

    print(f"\n执行时间: {elapsed_time:.2f}s")
    print(f"返回码: {result.returncode}")

    return {
        "command": cmd,
        "description": description,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_time": elapsed_time,
        "success": result.returncode == 0
    }


def main():
    """主函数"""
    print("\n" + "="*80)
    print("Phase 4: 集成测试执行")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 测试结果汇总
    test_results = []

    # 1. 运行 Cancel Scope 验证测试
    result = run_command(
        "python -m pytest tests/e2e/test_cancel_scope_verification.py -v --tb=short",
        "Cancel Scope 跨 Task 错误验证测试"
    )
    test_results.append(("Cancel Scope 验证", result))

    # 2. 运行 E2E 测试
    result = run_command(
        "python -m pytest tests/e2e/test_complete_story_lifecycle.py -v --tb=short",
        "完整 Story 生命周期 E2E 测试"
    )
    test_results.append(("E2E 测试", result))

    # 3. 运行集成验证测试
    result = run_command(
        "python -m pytest tests/e2e/test_integration_verification.py -v --tb=short",
        "集成验证测试"
    )
    test_results.append(("集成验证", result))

    # 4. 运行性能基准测试
    result = run_command(
        "python -m pytest tests/performance/test_performance_baseline.py -v --tb=short -m performance",
        "性能基准测试"
    )
    test_results.append(("性能基准", result))

    # 5. 运行集成测试套件
    result = run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "集成测试套件"
    )
    test_results.append(("集成测试", result))

    # 6. 运行单元测试（验证重构没有破坏现有功能）
    result = run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "单元测试套件"
    )
    test_results.append(("单元测试", result))

    # 7. 运行 Cancel Scope 修复测试
    result = run_command(
        "python -m pytest tests/test_cancel_scope_fix.py -v --tb=short",
        "Cancel Scope 修复验证测试"
    )
    test_results.append(("Cancel Scope 修复", result))

    # 生成报告
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_name, result in test_results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"\n{test_name:30s} {status:10s} ({result['elapsed_time']:6.2f}s)")

        total_tests += 1
        if result["success"]:
            passed_tests += 1
        else:
            failed_tests += 1

    print("\n" + "="*80)
    print(f"总计: {total_tests} 个测试套件")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
    print("="*80)

    # 保存详细报告
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 4 - Integration Testing",
        "summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0
        },
        "results": [
            {
                "test_name": test_name,
                "command": result["command"],
                "success": result["success"],
                "returncode": result["returncode"],
                "elapsed_time": result["elapsed_time"],
                "stdout": result["stdout"],
                "stderr": result["stderr"]
            }
            for test_name, result in test_results
        ]
    }

    report_file = Path("test_results_phase4.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\n详细报告已保存到: {report_file}")

    # 总结
    print("\n" + "="*80)
    if failed_tests == 0:
        print("🎉 所有测试通过！Phase 4 集成测试完成。")
        print("✅ Cancel Scope 跨 Task 错误已完全消除")
        print("✅ 所有组件集成正确")
        print("✅ 性能指标符合预期")
    else:
        print(f"⚠️  {failed_tests} 个测试套件失败")
        print("请检查失败原因并修复问题")

    print("="*80)

    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

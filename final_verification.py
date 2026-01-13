#!/usr/bin/env python
"""
最终验证测试 - 完整功能验证
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.agents.pytest_batch_executor import PytestBatchExecutor


async def main():
    """最终验证"""
    print("\n" + "="*80)
    print("Pytest目录遍历分批执行器 - 最终验证")
    print("="*80)

    # 使用真实的tests目录
    test_dir = Path("tests")
    source_dir = Path("src")

    if not test_dir.exists():
        print("[FAIL] tests目录不存在")
        return False

    executor = PytestBatchExecutor(test_dir, source_dir)

    # 1. 验证批次发现
    print("\n[1] 验证批次发现...")
    batches = executor.discover_batches()

    if len(batches) == 0:
        print("[FAIL] 未发现任何批次")
        return False

    print(f"[PASS] 发现 {len(batches)} 个批次")

    # 2. 验证批次类型
    print("\n[2] 验证批次类型...")
    expected_types = []
    for batch in batches:
        if "unit" in batch.name.lower():
            expected_types.append("unit")
        elif "integration" in batch.name.lower():
            expected_types.append("integration")
        elif "e2e" in batch.name.lower():
            expected_types.append("e2e")
        elif batch.name == "loose_tests":
            expected_types.append("loose")

    print(f"[PASS] 批次类型: {set(expected_types)}")

    # 3. 验证优先级排序
    print("\n[3] 验证优先级排序...")
    priorities = [b.priority for b in batches]
    if priorities == sorted(priorities):
        print(f"[PASS] 优先级正确排序: {priorities}")
    else:
        print(f"[FAIL] 优先级未排序: {priorities}")
        return False

    # 4. 验证启发式规则
    print("\n[4] 验证启发式规则...")
    for batch in batches:
        if "unit" in batch.name.lower():
            if batch.timeout != 60 or batch.priority != 2:
                print(f"[FAIL] unit批次配置错误")
                return False
        elif "integration" in batch.name.lower():
            if batch.timeout != 120 or batch.priority != 3:
                print(f"[FAIL] integration批次配置错误")
                return False
        elif "e2e" in batch.name.lower():
            if batch.timeout != 600 or batch.parallel:
                print(f"[FAIL] e2e批次配置错误")
                return False

    print("[PASS] 启发式规则正确应用")

    # 5. 验证排除目录
    print("\n[5] 验证排除目录...")
    batch_names = [b.name for b in batches]
    excluded = ["__pycache__", "htmlcov"]
    for exc in excluded:
        if exc in batch_names:
            print(f"[FAIL] 错误包含了排除目录: {exc}")
            return False

    print(f"[PASS] 正确排除了 {excluded} 等目录")

    # 6. 验证散装文件批次
    print("\n[6] 验证散装文件批次...")
    loose_batch = next((b for b in batches if b.name == "loose_tests"), None)
    if loose_batch:
        if loose_batch.timeout != 90 or loose_batch.priority != 2:
            print("[FAIL] loose_tests批次配置错误")
            return False
        print("[PASS] 散装文件批次正确配置")
    else:
        print("[INFO] 未发现散装文件批次（正常，如果无散装文件）")

    print("\n" + "="*80)
    print("[SUCCESS] 所有验证通过！")
    print("="*80)
    print("\n总结:")
    print(f"  - 发现批次: {len(batches)}")
    print(f"  - 优先级范围: {min(priorities)} - {max(priorities)}")
    print(f"  - 批次类型: {', '.join(set(expected_types))}")
    print(f"  - 启发式规则: ✅")
    print(f"  - 目录过滤: ✅")
    print(f"  - 散装文件支持: ✅")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

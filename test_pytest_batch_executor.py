#!/usr/bin/env python
"""
测试PytestBatchExecutor的脚本
验证动态目录扫描和批次执行功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.agents.pytest_batch_executor import PytestBatchExecutor


async def test_batch_discovery():
    """测试批次发现功能"""
    print("\n" + "="*80)
    print("测试1: 批次发现功能")
    print("="*80)

    # 使用现有的tests目录
    test_dir = Path("tests")
    source_dir = Path("src")

    executor = PytestBatchExecutor(test_dir, source_dir)

    # 发现批次
    batches = executor.discover_batches()

    print(f"\n发现的测试批次数量: {len(batches)}")
    print("\n批次详情:")
    for batch in batches:
        print(f"  - {batch.name:20s} | 优先级: {batch.priority} | 超时: {batch.timeout}s | "
              f"并行: {str(batch.parallel):5s} | 阻断: {str(batch.blocking):5s}")
        print(f"    路径: {batch.path}")

    return batches


async def test_batch_execution():
    """测试批次执行功能（使用小超时）"""
    print("\n" + "="*80)
    print("测试2: 批次执行功能（单元测试批次）")
    print("="*80)

    test_dir = Path("tests")
    source_dir = Path("src")

    executor = PytestBatchExecutor(test_dir, source_dir)

    # 只执行单元测试批次
    batches = executor.discover_batches()
    unit_batches = [b for b in batches if "unit" in b.name.lower()]

    if not unit_batches:
        print("未找到单元测试批次，跳过执行测试")
        return

    print(f"\n将执行 {len(unit_batches)} 个单元测试批次")
    for batch in unit_batches[:1]:  # 只执行第一个
        print(f"\n执行批次: {batch.name}")
        result = await executor._execute_batch(batch)
        print(f"  状态: {'成功' if result['success'] else '失败'}")
        print(f"  通过: {result.get('tests_passed', 0)} 个测试")
        print(f"  失败: {result.get('tests_failed', 0)} 个测试")


async def test_loose_files():
    """测试散装文件批次"""
    print("\n" + "="*80)
    print("测试3: 散装文件批次发现")
    print("="*80)

    test_dir = Path("tests")
    source_dir = Path("src")

    executor = PytestBatchExecutor(test_dir, source_dir)
    batches = executor.discover_batches()

    loose_batches = [b for b in batches if b.name == "loose_tests"]

    if loose_batches:
        print(f"\n发现散装文件批次: {loose_batches[0].name}")
        print(f"  超时: {loose_batches[0].timeout}s")
        print(f"  并行: {loose_batches[0].parallel}")
    else:
        print("\n未发现散装文件批次")


async def test_heuristic_matching():
    """测试启发式规则匹配"""
    print("\n" + "="*80)
    print("测试4: 启发式规则匹配")
    print("="*80)

    test_dir = Path("tests")
    source_dir = Path("src")

    executor = PytestBatchExecutor(test_dir, source_dir)

    # 测试各种目录名
    test_cases = [
        ("unit", "应该匹配unit规则"),
        ("unit_tests", "应该匹配unit规则"),
        ("integration", "应该匹配integration规则"),
        ("api_tests", "应该匹配api规则"),
        ("e2e", "应该匹配e2e规则"),
        ("end_to_end", "应该匹配e2e规则"),
        ("gui", "应该匹配gui规则"),
        ("performance", "应该匹配performance规则"),
        ("custom_dir", "应该使用默认规则"),
    ]

    for dir_name, description in test_cases:
        config = executor._match_config_by_heuristic(dir_name)
        print(f"\n{dir_name:20s} - {description}")
        print(f"  匹配配置: timeout={config['timeout']}s, parallel={config['parallel']}, "
              f"priority={config['priority']}")


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("PytestBatchExecutor 测试套件")
    print("="*80)

    # 检查目录是否存在
    if not Path("tests").exists():
        print("错误: tests目录不存在")
        return 1

    if not Path("src").exists():
        print("错误: src目录不存在")
        return 1

    try:
        # 运行测试
        await test_batch_discovery()
        await test_heuristic_matching()
        await test_loose_files()
        # await test_batch_execution()  # 注释掉，因为可能耗时较长

        print("\n" + "="*80)
        print("所有测试完成!")
        print("="*80)
        return 0

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

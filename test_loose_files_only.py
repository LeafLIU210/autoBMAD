#!/usr/bin/env python
"""
测试散装文件场景的脚本
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.agents.pytest_batch_executor import PytestBatchExecutor


async def test_loose_files_only():
    """测试只有散装文件的情况"""
    print("\n" + "="*80)
    print("测试: 散装文件场景")
    print("="*80)

    # 创建一个临时目录，只包含散装文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 创建散装测试文件
        test_file1 = tmpdir / "test_sample1.py"
        test_file2 = tmpdir / "test_sample2.py"

        test_file1.write_text("""
def test_addition():
    assert 1 + 1 == 2

def test_multiplication():
    assert 2 * 3 == 6
""")

        test_file2.write_text("""
def test_string():
    assert "hello" == "hello"

def test_list():
    assert [1, 2, 3] == [1, 2, 3]
""")

        # 创建批次执行器
        executor = PytestBatchExecutor(tmpdir, Path("."))

        # 发现批次
        batches = executor.discover_batches()

        print(f"\n发现的测试批次数量: {len(batches)}")

        if batches:
            batch = batches[0]
            print(f"\n批次详情:")
            print(f"  名称: {batch.name}")
            print(f"  路径: {batch.path}")
            print(f"  超时: {batch.timeout}s")
            print(f"  并行: {batch.parallel}")
            print(f"  优先级: {batch.priority}")

            # 尝试执行
            print(f"\n尝试执行批次...")
            result = await executor._execute_batch(batch)

            print(f"\n执行结果:")
            print(f"  成功: {result['success']}")
            print(f"  通过: {result.get('tests_passed', 0)} 个测试")
            print(f"  失败: {result.get('tests_failed', 0)} 个测试")

            if result.get('stdout'):
                print(f"\n输出:")
                print(result['stdout'][:500])

            return result['success']
        else:
            print("未发现任何批次")
            return False


async def test_empty_directory():
    """测试空目录的情况"""
    print("\n" + "="*80)
    print("测试: 空目录场景")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        executor = PytestBatchExecutor(tmpdir, Path("."))
        batches = executor.discover_batches()

        print(f"\n发现的测试批次数量: {len(batches)}")

        if len(batches) == 0:
            print("[PASS] 正确处理了空目录（无批次）")
            return True
        else:
            print("[FAIL] 空目录应该没有批次")
            return False


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("散装文件场景测试套件")
    print("="*80)

    results = []

    try:
        # 测试散装文件场景
        result1 = await test_loose_files_only()
        results.append(("散装文件场景", result1))

        # 测试空目录场景
        result2 = await test_empty_directory()
        results.append(("空目录场景", result2))

        print("\n" + "="*80)
        print("测试结果汇总")
        print("="*80)

        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{name:30s}: {status}")

        all_passed = all(result for _, result in results)

        if all_passed:
            print("\n[PASS] 所有散装文件场景测试通过!")
            return 0
        else:
            print("\n[FAIL] 部分测试失败")
            return 1

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

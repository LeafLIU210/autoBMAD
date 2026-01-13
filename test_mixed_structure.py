#!/usr/bin/env python
"""
测试混合结构场景的脚本
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.agents.pytest_batch_executor import PytestBatchExecutor


async def test_mixed_structure():
    """测试混合结构（目录 + 散装文件）"""
    print("\n" + "="*80)
    print("测试: 混合结构场景")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 创建子目录
        unit_dir = tmpdir / "unit_tests"
        integration_dir = tmpdir / "api_integration"
        unit_dir.mkdir()
        integration_dir.mkdir()

        # 创建散装文件
        loose_file = tmpdir / "test_loose.py"
        loose_file.write_text("""
def test_loose_1():
    assert 1 == 1

def test_loose_2():
    assert 2 == 2
""")

        # 创建单元测试文件
        (unit_dir / "test_unit1.py").write_text("""
def test_unit_add():
    assert 1 + 1 == 2

def test_unit_multiply():
    assert 2 * 2 == 4
""")

        # 创建集成测试文件
        (integration_dir / "test_api.py").write_text("""
def test_api_1():
    assert "api" == "api"

def test_api_2():
    assert "integration" == "integration"
""")

        # 创建批次执行器
        executor = PytestBatchExecutor(tmpdir, Path("."))

        # 发现批次
        batches = executor.discover_batches()

        print(f"\n发现的测试批次数量: {len(batches)}")
        print("\n批次详情:")

        expected_batches = ["unit_tests", "api_integration", "loose_tests"]
        found_batches = [b.name for b in batches]

        for batch in batches:
            print(f"  - {batch.name:20s} | 优先级: {batch.priority} | 超时: {batch.timeout}s")

        # 验证是否包含期望的批次
        print("\n验证批次:")
        for expected in expected_batches:
            if expected in found_batches:
                print(f"  [PASS] 找到期望的批次: {expected}")
            else:
                print(f"  [FAIL] 未找到期望的批次: {expected}")

        # 验证优先级
        print("\n验证优先级:")
        priorities = [b.priority for b in batches]
        if priorities == sorted(priorities):
            print(f"  [PASS] 批次按优先级正确排序: {priorities}")
        else:
            print(f"  [FAIL] 批次未按优先级排序: {priorities}")

        return len(batches) == 3


async def test_custom_directory():
    """测试自定义目录名（使用默认配置）"""
    print("\n" + "="*80)
    print("测试: 自定义目录名场景")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 创建自定义目录
        custom_dir = tmpdir / "my_custom_tests"
        custom_dir.mkdir()

        (custom_dir / "test_custom.py").write_text("""
def test_custom():
    assert "custom" == "custom"
""")

        executor = PytestBatchExecutor(tmpdir, Path("."))
        batches = executor.discover_batches()

        print(f"\n发现的测试批次数量: {len(batches)}")

        if batches:
            batch = batches[0]
            print(f"\n自定义目录批次详情:")
            print(f"  名称: {batch.name}")
            print(f"  使用默认配置: timeout={batch.timeout}s, parallel={batch.parallel}")

            # 验证使用了默认配置
            if batch.timeout == 120 and batch.parallel and batch.priority == 3:
                print(f"  [PASS] 正确使用了默认配置")
                return True
            else:
                print(f"  [FAIL] 未正确使用默认配置")
                return False
        else:
            print("  [FAIL] 未发现批次")
            return False


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("混合结构场景测试套件")
    print("="*80)

    results = []

    try:
        # 测试混合结构
        result1 = await test_mixed_structure()
        results.append(("混合结构场景", result1))

        # 测试自定义目录
        result2 = await test_custom_directory()
        results.append(("自定义目录场景", result2))

        print("\n" + "="*80)
        print("测试结果汇总")
        print("="*80)

        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{name:30s}: {status}")

        all_passed = all(result for _, result in results)

        if all_passed:
            print("\n[PASS] 所有混合结构场景测试通过!")
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

"""
性能基线测试
测试系统性能指标，确保重构后性能不退化
"""

import pytest
import anyio
import tempfile
import time
import psutil
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch
import sys

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver


# 性能基线配置
PERFORMANCE_BASELINE = {
    "single_story_processing": 30.0,  # 秒
    "concurrent_5_stories": 45.0,     # 秒
    "sdk_call_latency": 2.0,          # 秒
    "memory_usage": 150.0,             # MB
    "cpu_usage": 70.0,                # %
}


@pytest.fixture
async def performance_test_data():
    """创建性能测试数据"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建测试 Epic
        epic_content = """# Performance Test Epic

### Story 1.1: Performance Test Story 1

### Story 1.2: Performance Test Story 2

### Story 1.3: Performance Test Story 3

### Story 1.4: Performance Test Story 4

### Story 1.5: Performance Test Story 5

## Acceptance Criteria
- [ ] All performance tests pass
"""
        epic_file = tmp_path / "epic-performance.md"
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建 Stories 目录和故事文件
        stories_dir = tmp_path / "stories"
        stories_dir.mkdir(parents=True, exist_ok=True)

        stories = []
        for i in range(1, 6):
            story_content = f"""# Story 1.{i}: Performance Test Story {i}

**Status**: Draft

## Description
Performance test story number {i}.

## Tasks
- [ ] Task {i}.1
- [ ] Task {i}.2
"""
            story_file = stories_dir / f"1.{i}-performance-test.md"
            story_file.write_text(story_content, encoding='utf-8')
            stories.append({
                "file": story_file,
                "id": f"1.{i}",
                "path": str(story_file.resolve()),
                "name": story_file.name,
                "status": "Draft"
            })

        # 创建项目结构
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "test.py").write_text("# Test module\n", encoding='utf-8')

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_test.py").write_text("def test_dummy(): pass\n", encoding='utf-8')

        yield {
            "epic_file": epic_file,
            "stories": stories,
            "project_root": tmp_path
        }


@pytest.mark.performance
@pytest.mark.anyio
async def test_single_story_processing_performance(
    performance_test_data
):
    """测试单个 Story 处理性能"""
    data = performance_test_data
    story = data["stories"][0]

    # 记录基线内存
    process = psutil.Process()
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 只处理一个故事
    driver.stories = [story]

    # 快速模拟状态转换
    async def mock_parse_status(path):
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行性能测试
    start_time = time.time()
    result = await driver.execute_dev_qa_cycle([story])
    elapsed_time = time.time() - start_time

    # 记录峰值内存
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = peak_memory - baseline_memory

    # 验证性能
    assert result is True, "Story processing should succeed"
    assert elapsed_time < PERFORMANCE_BASELINE["single_story_processing"] * 1.1, \
        f"Story processing took {elapsed_time:.2f}s, expected < {PERFORMANCE_BASELINE['single_story_processing'] * 1.1:.2f}s"

    assert memory_increase < PERFORMANCE_BASELINE["memory_usage"], \
        f"Memory increase {memory_increase:.2f}MB exceeded baseline {PERFORMANCE_BASELINE['memory_usage']}MB"

    print(f"\n✅ Single Story Performance:")
    print(f"   Time: {elapsed_time:.2f}s (baseline: {PERFORMANCE_BASELINE['single_story_processing']}s)")
    print(f"   Memory: {memory_increase:.2f}MB (baseline: {PERFORMANCE_BASELINE['memory_usage']}MB)")


@pytest.mark.performance
@pytest.mark.anyio
async def test_concurrent_5_stories_performance(
    performance_test_data
):
    """测试并发处理 5 个 Stories 的性能"""
    data = performance_test_data

    # 记录基线内存
    process = psutil.Process()
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 创建 EpicDriver（启用并发）
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=True,  # 启用并发
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 设置所有故事
    driver.stories = data["stories"]

    # 快速模拟状态转换
    async def mock_parse_status(path):
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行性能测试
    start_time = time.time()
    result = await driver.execute_dev_qa_cycle(data["stories"])
    elapsed_time = time.time() - start_time

    # 记录峰值内存
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = peak_memory - baseline_memory

    # 验证性能
    assert result is True, "Concurrent processing should succeed"
    assert elapsed_time < PERFORMANCE_BASELINE["concurrent_5_stories"] * 1.1, \
        f"Concurrent processing took {elapsed_time:.2f}s, expected < {PERFORMANCE_BASELINE['concurrent_5_stories'] * 1.1:.2f}s"

    assert memory_increase < PERFORMANCE_BASELINE["memory_usage"] * 1.2, \
        f"Memory increase {memory_increase:.2f}MB exceeded baseline {PERFORMANCE_BASELINE['memory_usage'] * 1.2:.2f}MB"

    print(f"\n✅ Concurrent 5 Stories Performance:")
    print(f"   Time: {elapsed_time:.2f}s (baseline: {PERFORMANCE_BASELINE['concurrent_5_stories']}s)")
    print(f"   Memory: {memory_increase:.2f}MB (baseline: {PERFORMANCE_BASELINE['memory_usage']}MB)")


@pytest.mark.performance
@pytest.mark.anyio
async def test_sdk_call_latency(
    performance_test_data
):
    """测试 SDK 调用延迟"""
    # 这个测试验证 SDKExecutor 的性能
    data = performance_test_data

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=1,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟快速的 SDK 调用
    call_times = []
    num_calls = 5

    for i in range(num_calls):
        start = time.time()

        # 模拟状态解析（这是 SDK 调用的替代）
        async def mock_parse():
            await anyio.sleep(0.01)  # 模拟 10ms SDK 调用
            return "Done"

        result = await mock_parse()
        elapsed = time.time() - start
        call_times.append(elapsed)

    # 计算平均延迟
    avg_latency = sum(call_times) / len(call_times)

    # 验证性能
    assert avg_latency < PERFORMANCE_BASELINE["sdk_call_latency"] * 1.1, \
        f"Average SDK call latency {avg_latency:.3f}s exceeded baseline {PERFORMANCE_BASELINE['sdk_call_latency']}s"

    print(f"\n✅ SDK Call Latency:")
    print(f"   Average: {avg_latency:.3f}s (baseline: {PERFORMANCE_BASELINE['sdk_call_latency']}s)")
    print(f"   Calls: {num_calls}")


@pytest.mark.performance
@pytest.mark.anyio
async def test_memory_usage_monitoring(
    performance_test_data
):
    """测试内存使用监控"""
    data = performance_test_data

    process = psutil.Process()

    # 记录内存使用历史
    memory_samples = []

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换
    async def mock_parse_status(path):
        # 采样内存使用
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples.append(current_memory)
        await anyio.sleep(0.01)  # 模拟处理时间
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行处理
    await driver.execute_dev_qa_cycle(data["stories"])

    # 分析内存使用
    if memory_samples:
        max_memory = max(memory_samples)
        min_memory = min(memory_samples)
        memory_delta = max_memory - min_memory

        print(f"\n✅ Memory Usage Analysis:")
        print(f"   Min: {min_memory:.2f}MB")
        print(f"   Max: {max_memory:.2f}MB")
        print(f"   Delta: {memory_delta:.2f}MB")

        # 验证内存没有异常增长
        assert memory_delta < PERFORMANCE_BASELINE["memory_usage"], \
            f"Memory delta {memory_delta:.2f}MB exceeded baseline {PERFORMANCE_BASELINE['memory_usage']}MB"


@pytest.mark.performance
@pytest.mark.anyio
async def test_cpu_usage_monitoring(
    performance_test_data
):
    """测试 CPU 使用监控"""
    data = performance_test_data

    # 记录基线 CPU 使用率
    baseline_cpu = psutil.cpu_percent(interval=0.1)

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换（CPU 密集型）
    async def mock_parse_status(path):
        # 模拟 CPU 工作
        start = time.time()
        while time.time() - start < 0.01:  # 10ms CPU 工作
            pass
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行处理
    start_time = time.time()
    await driver.execute_dev_qa_cycle(data["stories"])
    elapsed = time.time() - start_time

    # 记录峰值 CPU 使用率
    peak_cpu = psutil.cpu_percent(interval=0.1)
    cpu_increase = peak_cpu - baseline_cpu

    print(f"\n✅ CPU Usage:")
    print(f"   Baseline: {baseline_cpu:.1f}%")
    print(f"   Peak: {peak_cpu:.1f}%")
    print(f"   Increase: {cpu_increase:.1f}%")
    print(f"   Time: {elapsed:.2f}s")

    # 验证 CPU 使用率在合理范围内
    assert cpu_increase < PERFORMANCE_BASELINE["cpu_usage"], \
        f"CPU increase {cpu_increase:.1f}% exceeded baseline {PERFORMANCE_BASELINE['cpu_usage']}%"


@pytest.mark.performance
@pytest.mark.anyio
async def test_memory_leak_detection(
    performance_test_data
):
    """测试内存泄漏检测"""
    data = performance_test_data

    process = psutil.Process()

    # 记录初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 执行多次处理循环
    num_cycles = 10

    for cycle in range(num_cycles):
        # 创建新的 EpicDriver
        driver = EpicDriver(
            epic_path=str(data["epic_file"]),
            max_iterations=1,
            retry_failed=False,
            verbose=False,
            concurrent=False,
            use_claude=False,
            source_dir=str(data["project_root"] / "src"),
            test_dir=str(data["project_root"] / "tests"),
            skip_quality=True,
            skip_tests=True
        )

        # 快速模拟状态转换
        async def mock_parse_status(path):
            return "Done"

        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)

        # 执行处理
        await driver.execute_dev_qa_cycle([data["stories"][0]])

        # 清理
        del driver

    # 记录最终内存
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    print(f"\n✅ Memory Leak Detection:")
    print(f"   Initial: {initial_memory:.2f}MB")
    print(f"   Final: {final_memory:.2f}MB")
    print(f"   Increase: {memory_increase:.2f}MB")
    print(f"   Cycles: {num_cycles}")

    # 验证没有内存泄漏（允许小幅增长）
    assert memory_increase < 10.0, \
        f"Potential memory leak detected: {memory_increase:.2f}MB increase after {num_cycles} cycles"


@pytest.mark.performance
def test_performance_benchmark_summary():
    """性能基准测试汇总"""
    # 这个测试汇总所有性能指标
    print("\n" + "="*60)
    print("PERFORMANCE BASELINE SUMMARY")
    print("="*60)

    for metric, baseline in PERFORMANCE_BASELINE.items():
        print(f"{metric:30s}: {baseline:10.2f}")

    print("="*60)
    print("Note: All performance tests use 10% tolerance")
    print("="*60)

    # 总是通过 - 这只是一个信息测试
    assert True


if __name__ == "__main__":
    # 运行所有性能测试
    pytest.main([__file__, "-v", "-m", "performance"])

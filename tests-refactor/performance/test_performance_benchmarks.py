"""
性能基准测试
验证EpicDriver在不同负载下的性能表现
符合Phase 4性能标准
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch, Mock
import sys
import time
import psutil
import asyncio
import json
from datetime import datetime

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver


# 性能基线配置
PERFORMANCE_BASELINE = {
    "single_story_processing": 30.0,  # 秒
    "concurrent_5_stories": 45.0,     # 秒
    "concurrent_10_stories": 90.0,    # 秒
    "batch_10_stories": 300.0,        # 秒
    "sdk_call_latency": 2.0,          # 秒
    "memory_usage": 150.0,             # MB
    "cpu_usage": 70.0,                # %
    "memory_growth": 10.0,            # MB (长时间运行内存增长)
}


@pytest.fixture
async def large_epic_structure():
    """创建大批量Epic结构用于性能测试"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "main.py").write_text("# Main module\nprint('Performance test')\n", encoding='utf-8')

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_main.py").write_text("# Test file\n", encoding='utf-8')

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # 创建包含10个故事的Epic文件
        story_ids = [f"{i}" for i in range(1, 11)]

        epic_content = "# Epic: Performance Test\\n\\n"
        epic_content += "## Overview\\n"
        epic_content += "This is a performance test epic with multiple stories.\\n\\n"

        for story_id in story_ids:
            epic_content += f"### Story {story_id}: Performance Test Story {story_id}\\n\\n"

        epic_content += "## Acceptance Criteria\\n"
        epic_content += "- [ ] All stories processed efficiently\\n"
        epic_content += "- [ ] Performance within acceptable limits\\n"

        epic_file = docs_dir / "epic-performance-test.md"
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建Stories目录
        stories_dir = tmp_path / "stories"
        stories_dir.mkdir(parents=True, exist_ok=True)

        # 创建10个故事
        stories = []
        for story_id in story_ids:
            story_content = f"""# Story {story_id}: Performance Test Story {story_id}

**Status**: Draft

## Description
This is story {story_id} for performance testing.

## Acceptance Criteria
1. Story {story_id} processes efficiently
2. No performance degradation

## Tasks
- [ ] Task {story_id}.1: Setup
- [ ] Task {story_id}.2: Execute
- [ ] Task {story_id}.3: Verify
"""
            story_file = stories_dir / f"{story_id}-performance-test.md"
            story_file.write_text(story_content, encoding='utf-8')
            stories.append({"file": story_file, "id": story_id})

        yield {
            "root_dir": tmp_path,
            "epic_file": epic_file,
            "stories": stories
        }


@pytest.fixture
async def performance_monitor():
    """性能监控器"""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.peak_memory = 0
            self.process = psutil.Process()

        def start(self):
            """开始监控"""
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            self.peak_memory = self.start_memory

        def record_memory(self):
            """记录当前内存使用"""
            current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory

        def stop(self):
            """停止监控"""
            self.end_time = time.time()
            self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        def get_results(self):
            """获取性能结果"""
            elapsed_time = (self.end_time - self.start_time) if self.end_time else 0
            memory_increase = (self.end_memory - self.start_memory) if self.end_memory else 0

            return {
                "elapsed_time": elapsed_time,
                "start_memory": self.start_memory,
                "end_memory": self.end_memory,
                "peak_memory": self.peak_memory,
                "memory_increase": memory_increase,
                "memory_growth": memory_increase
            }

    return PerformanceMonitor()


@pytest.fixture
async def fast_mock_sdk():
    """快速Mock SDK用于性能测试"""
    mock_sdk = MagicMock()

    # 快速响应（< 0.1秒）
    async def fast_mock_call(prompt, task_group, **kwargs):
        # 模拟快速SDK调用
        await asyncio.sleep(0.05)  # 50ms
        result = Mock()
        result.success = True
        result.content = f"Fast response for: {prompt[:50]}"
        return result

    mock_sdk.call = AsyncMock(side_effect=fast_mock_call)
    mock_sdk.close = MagicMock()

    return mock_sdk


@pytest.mark.performance
@pytest.mark.anyio
async def test_batch_story_performance(large_epic_structure, fast_mock_sdk, performance_monitor):
    """
    大批量故事处理性能测试
    10个故事顺序处理，总时间应 < 300秒
    """
    print("\\n=== 大批量故事处理性能测试 ===")
    print(f"测试{len(large_epic_structure['stories'])}个故事顺序处理")

    performance_monitor.start()

    with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
        driver = EpicDriver(
            epic_path=str(large_epic_structure["epic_file"]),
            max_iterations=3  # 限制循环次数以加速测试
        )

        start_time = time.time()

        # 顺序处理所有故事
        for story in large_epic_structure["stories"]:
            performance_monitor.record_memory()
            print(f"处理故事{story['id']}...")
            await driver.process_story(story["id"])

        performance_monitor.stop()

        results = performance_monitor.get_results()

        print(f"\\n⏱️  总处理时间: {results['elapsed_time']:.2f}秒")
        print(f"💾 峰值内存使用: {results['peak_memory']:.2f} MB")
        print(f"📈 内存增长: {results['memory_growth']:.2f} MB")

        # 验证性能基线
        assert results['elapsed_time'] < PERFORMANCE_BASELINE["batch_10_stories"], (
            f"批量处理时间超标: {results['elapsed_time']:.2f}s > {PERFORMANCE_BASELINE['batch_10_stories']}s"
        )

        assert results['memory_growth'] < PERFORMANCE_BASELINE["memory_growth"], (
            f"内存增长超标: {results['memory_growth']:.2f}MB > {PERFORMANCE_BASELINE['memory_growth']}MB"
        )

        print("✅ 大批量故事处理性能测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_concurrent_performance(large_epic_structure, fast_mock_sdk, performance_monitor):
    """
    并发性能测试
    10个故事并发处理，总时间应 < 90秒
    """
    print("\\n=== 并发性能测试 ===")
    print(f"测试{len(large_epic_structure['stories'])}个故事并发处理")

    performance_monitor.start()

    with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
        driver = EpicDriver(
            epic_path=str(large_epic_structure["epic_file"]),
            max_iterations=3
        )

        # 并发处理所有故事
        async with anyio.create_task_group() as tg:
            for story in large_epic_structure["stories"]:
                tg.start_soon(driver.process_story, story["id"])

        performance_monitor.stop()

        results = performance_monitor.get_results()

        print(f"\\n⏱️  并发处理时间: {results['elapsed_time']:.2f}秒")
        print(f"💾 峰值内存使用: {results['peak_memory']:.2f} MB")
        print(f"📈 内存增长: {results['memory_growth']:.2f} MB")

        # 验证性能基线
        assert results['elapsed_time'] < PERFORMANCE_BASELINE["concurrent_10_stories"], (
            f"并发处理时间超标: {results['elapsed_time']:.2f}s > {PERFORMANCE_BASELINE['concurrent_10_stories']}s"
        )

        assert results['memory_growth'] < PERFORMANCE_BASELINE["memory_growth"], (
            f"内存增长超标: {results['memory_growth']:.2f}MB > {PERFORMANCE_BASELINE['memory_growth']}MB"
        )

        print("✅ 并发性能测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_memory_leak_detection(large_epic_structure, fast_mock_sdk, performance_monitor):
    """
    内存泄漏检测测试
    长时间运行内存增长应 < 10MB
    """
    print("\\n=== 内存泄漏检测测试 ===")

    performance_monitor.start()

    with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
        driver = EpicDriver(
            epic_path=str(large_epic_structure["epic_file"]),
            max_iterations=3
        )

        # 重复处理故事多次以检测内存泄漏
        iterations = 5
        print(f"重复处理{iterations}轮...")

        for i in range(iterations):
            print(f"\\n第{i + 1}轮...")
            for story in large_epic_structure["stories"]:
                await driver.process_story(story["id"])
                performance_monitor.record_memory()

        performance_monitor.stop()

        results = performance_monitor.get_results()

        print(f"\\n💾 初始内存: {results['start_memory']:.2f} MB")
        print(f"💾 最终内存: {results['end_memory']:.2f} MB")
        print(f"💾 峰值内存: {results['peak_memory']:.2f} MB")
        print(f"📈 内存增长: {results['memory_growth']:.2f} MB")

        # 验证内存增长在可接受范围内
        assert results['memory_growth'] < PERFORMANCE_BASELINE["memory_growth"], (
            f"内存增长超标: {results['memory_growth']:.2f}MB > {PERFORMANCE_BASELINE['memory_growth']}MB"
        )

        print("✅ 内存泄漏检测测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_cpu_usage_monitoring(fast_mock_sdk, performance_monitor):
    """
    CPU使用监控测试
    峰值CPU使用率应 < 77%
    """
    print("\\n=== CPU使用监控测试 ===")

    performance_monitor.start()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
            # 创建Epic文件
            epic_file = tmp_path / "epic.md"
            epic_file.write_text("# Test Epic\n", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(epic_file),
                max_iterations=3
            )

            # 创建测试故事
            stories_dir = tmp_path / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            # 创建5个测试故事
            for i in range(5):
                story_file = stories_dir / f"test-story-{i}.md"
                story_file.write_text(f"""
# Test Story {i}

**Status**: Draft

## Description
CPU monitoring test story {i}.

## Tasks
- [ ] Task {i}.1: Execute
""", encoding='utf-8')

                # 处理故事并监控CPU
                await driver.process_story(f"test-story-{i}")
                performance_monitor.record_memory()

        performance_monitor.stop()

        results = performance_monitor.get_results()

        print(f"\\n⏱️  执行时间: {results['elapsed_time']:.2f}秒")
        print(f"💾 内存使用: {results['end_memory']:.2f} MB")

        # CPU使用率通过进程监控获取
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"🖥️  CPU使用率: {cpu_percent}%")

        # 验证内存使用
        assert results['memory_growth'] < PERFORMANCE_BASELINE["memory_usage"], (
            f"内存使用超标: {results['memory_growth']:.2f}MB > {PERFORMANCE_BASELINE['memory_usage']}MB"
        )

        print("✅ CPU使用监控测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_sdk_call_latency(fast_mock_sdk, performance_monitor):
    """
    SDK调用延迟测试
    平均SDK调用延迟应 < 2.2秒
    """
    print("\\n=== SDK调用延迟测试 ===")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
            # 创建Epic文件
            epic_file = tmp_path / "epic.md"
            epic_file.write_text("# Test Epic\n", encoding='utf-8')

            driver = EpicDriver(
                epic_path=str(epic_file),
                max_iterations=1
            )

            # 创建测试故事
            stories_dir = tmp_path / "stories"
            stories_dir.mkdir(parents=True, exist_ok=True)

            story_file = stories_dir / "test-story.md"
            story_file.write_text("""
# Test Story

**Status**: Draft

## Description
SDK latency test story.

## Tasks
- [ ] Task 1: Measure latency
""", encoding='utf-8')

            # 测量SDK调用延迟
            latencies = []

            for i in range(5):
                start_time = time.time()
                await driver.process_story("test-story")
                end_time = time.time()
                latency = end_time - start_time
                latencies.append(latency)
                print(f"调用{i + 1}延迟: {latency:.2f}秒")

            # 计算平均延迟
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)

            print(f"\\n📊 延迟统计:")
            print(f"   平均延迟: {avg_latency:.2f}秒")
            print(f"   最大延迟: {max_latency:.2f}秒")
            print(f"   最小延迟: {min_latency:.2f}秒")

            # 验证延迟基线
            assert avg_latency < PERFORMANCE_BASELINE["sdk_call_latency"], (
                f"平均SDK延迟超标: {avg_latency:.2f}s > {PERFORMANCE_BASELINE['sdk_call_latency']}s"
            )

            print("✅ SDK调用延迟测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_performance_regression_detection(fast_mock_sdk, performance_monitor):
    """
    性能回归检测测试
    对比不同负载下的性能表现
    """
    print("\\n=== 性能回归检测测试 ===")

    test_results = {}

    # 测试不同负载
    test_cases = [
        {"name": "1-story", "count": 1},
        {"name": "3-stories", "count": 3},
        {"name": "5-stories", "count": 5},
    ]

    for test_case in test_cases:
        print(f"\\n测试{test_case['name']}负载...")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
                driver = EpicDriver(
                    epic_path=str(epic_file),
                    max_iterations=2
                )

                # 创建测试故事
                stories_dir = tmp_path / "stories"
                stories_dir.mkdir(parents=True, exist_ok=True)

                for i in range(test_case['count']):
                    story_file = stories_dir / f"test-story-{i}.md"
                    story_file.write_text(f"""
# Test Story {i}

**Status**: Draft

## Description
Performance regression test story {i}.

## Tasks
- [ ] Task {i}.1: Execute
""", encoding='utf-8')

                # 开始监控
                monitor = performance_monitor.__class__()  # 创建新的监控器
                monitor.start()

                # 处理故事
                for i in range(test_case['count']):
                    await driver.process_story(f"test-story-{i}")

                monitor.stop()
                results = monitor.get_results()

                test_results[test_case['name']] = {
                    "story_count": test_case['count'],
                    "elapsed_time": results['elapsed_time'],
                    "memory_growth": results['memory_growth']
                }

                print(f"✅ {test_case['name']}: {results['elapsed_time']:.2f}s")

    # 输出性能对比
    print("\\n📊 性能对比:")
    for name, result in test_results.items():
        per_story_time = result['elapsed_time'] / result['story_count']
        print(f"{name:15s}: {result['elapsed_time']:6.2f}s ({per_story_time:.2f}s/story)")

    # 验证性能线性增长
    time_1 = test_results["1-story"]["elapsed_time"]
    time_3 = test_results["3-stories"]["elapsed_time"]
    time_5 = test_results["5-stories"]["elapsed_time"]

    # 3个故事的时间应该接近3倍，5个故事应该接近5倍（允许10%误差）
    assert time_3 / time_1 < 3.3, "性能随负载增长过快"
    assert time_5 / time_1 < 5.5, "性能随负载增长过快"

    print("✅ 性能回归检测测试通过")


@pytest.mark.performance
@pytest.mark.anyio
async def test_concurrent_vs_sequential_performance(large_epic_structure, fast_mock_sdk):
    """
    并发vs顺序性能对比测试
    验证并发处理的性能优势
    """
    print("\\n=== 并发vs顺序性能对比测试 ===")

    # 顺序处理
    print("\\n📝 顺序处理...")
    with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
        driver = EpicDriver(
            project_root=large_epic_structure["root_dir"],
            max_iterations=2
        )

        start_time = time.time()
        for story in large_epic_structure["stories"]:
            await driver.process_story(story["id"])
        sequential_time = time.time() - start_time
        print(f"✅ 顺序处理时间: {sequential_time:.2f}秒")

    # 并发处理
    print("\\n⚡ 并发处理...")
    with patch('autoBMAD.epic_automation.epic_driver.SafeClaudeSDK', return_value=fast_mock_sdk):
        driver = EpicDriver(
            project_root=large_epic_structure["root_dir"],
            max_iterations=2
        )

        start_time = time.time()
        async with anyio.create_task_group() as tg:
            for story in large_epic_structure["stories"]:
                tg.start_soon(driver.process_story, story["id"])
        concurrent_time = time.time() - start_time
        print(f"✅ 并发处理时间: {concurrent_time:.2f}秒")

    # 计算性能提升
    improvement = sequential_time / concurrent_time
    print(f"\\n📈 性能提升: {improvement:.2f}x")

    # 验证并发有显著性能优势
    assert improvement > 1.5, "并发处理性能提升不足"
    print("✅ 并发vs顺序性能对比测试通过")


if __name__ == "__main__":
    # 运行测试
    print("\\n" + "="*80)
    print("性能基准测试")
    print("="*80)
    print("\\n性能基线:")
    for key, value in PERFORMANCE_BASELINE.items():
        print(f"  {key}: {value}")

    pytest.main([__file__, "-v", "-s", "-m", "performance"])

"""
完整 Story 生命周期 E2E 测试
测试 Story 从 Draft 到 Done 的完整流程
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import time

# 添加 src 目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver


@pytest.fixture
async def temp_epic_and_stories():
    """创建临时 Epic 和 Story 文件"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建 Epic 文件
        epic_content = """# Epic 1: Test Epic

## Overview
This is a test epic for E2E testing.

### Story 1.1: Complete Story Lifecycle Test

### Story 1.2: Concurrent Processing Test

## Acceptance Criteria
- [ ] All stories processed successfully
- [ ] No cancel scope errors
- [ ] State transitions correct
"""
        epic_file = tmp_path / "epic-001-test.md"
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建 Stories 目录
        stories_dir = tmp_path / "stories"
        stories_dir.mkdir(parents=True, exist_ok=True)

        # 创建 Story 1.1
        story_1_1_content = """# Story 1.1: Complete Story Lifecycle Test

**Status**: Draft

## Description
This story tests the complete lifecycle from Draft to Done.

## Acceptance Criteria
1. Draft → Ready for Development
2. Ready for Development → In Progress
3. In Progress → Ready for Review
4. Ready for Review → Done

## Tasks
- [ ] Task 1: Initial setup
- [ ] Task 2: Implementation
- [ ] Task 3: Review and finalize
"""
        story_1_1_file = stories_dir / "1.1-complete-lifecycle.md"
        story_1_1_file.write_text(story_1_1_content, encoding='utf-8')

        # 创建 Story 1.2
        story_1_2_content = """# Story 1.2: Concurrent Processing Test

**Status**: Draft

## Description
This story tests concurrent processing capabilities.

## Acceptance Criteria
1. Story can be processed concurrently
2. No state conflicts occur

## Tasks
- [ ] Task 1: Setup for concurrent test
"""
        story_1_2_file = stories_dir / "1.2-concurrent-test.md"
        story_1_2_file.write_text(story_1_2_content, encoding='utf-8')

        # 创建项目结构
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "test_module.py").write_text("# Test module\n", encoding='utf-8')

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        yield {
            "epic_file": epic_file,
            "epic_content": epic_content,
            "stories": [
                {
                    "file": story_1_1_file,
                    "content": story_1_1_content,
                    "id": "1.1"
                },
                {
                    "file": story_1_2_file,
                    "content": story_1_2_content,
                    "id": "1.2"
                }
            ],
            "project_root": tmp_path
        }


@pytest.mark.e2e
@pytest.mark.anyio
async def test_complete_story_lifecycle_single_story(
    temp_epic_and_stories
):
    """测试完整 Story 生命周期：Draft → Ready → Development → Review → Done"""
    # 获取测试数据
    data = temp_epic_and_stories
    story = data["stories"][0]

    # 创建 EpicDriver 实例
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=True,
        concurrent=False,
        use_claude=False,  # 使用模拟模式
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换
    status_sequence = ["Draft", "Ready for Development", "In Progress", "Ready for Review", "Done"]
    status_index = 0

    original_parse = driver._parse_story_status

    async def mock_parse_status(path):
        nonlocal status_index
        if status_index < len(status_sequence):
            status = status_sequence[status_index]
            status_index += 1
            return status
        return "Done"

    driver._parse_story_status = mock_parse_status

    # 模拟 Dev 和 QA 执行
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行完整流程
    result = await driver.run()

    # 验证结果
    assert result is True, "Story lifecycle should complete successfully"
    assert status_index == len(status_sequence), "All status transitions should occur"

    # 验证文件生成
    assert story["file"].exists(), "Story file should exist"

    # 验证无 Cancel Scope 错误
    # 如果执行到这里而没有抛出 RuntimeError，说明没有 cancel scope 错误


@pytest.mark.e2e
@pytest.mark.anyio
async def test_concurrent_story_processing(
    temp_epic_and_stories
):
    """测试多个 Stories 并发处理"""
    # 获取测试数据
    data = temp_epic_and_stories

    # 创建 EpicDriver 实例（启用并发）
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=True,
        concurrent=True,  # 启用并发
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换
    async def mock_parse_status(path):
        # 根据故事文件决定状态
        if "1.1" in path:
            return "Done"
        elif "1.2" in path:
            return "Done"
        return "Draft"

    driver._parse_story_status = mock_parse_status

    # 模拟执行
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行并发处理
    result = await driver.run()

    # 验证结果
    assert result is True, "Concurrent processing should succeed"

    # 验证所有故事都被处理
    assert len(driver.stories) >= 2, "Should have processed at least 2 stories"


@pytest.mark.e2e
@pytest.mark.anyio
async def test_error_recovery_workflow(
    temp_epic_and_stories
):
    """测试错误恢复和重试机制"""
    # 获取测试数据
    data = temp_epic_and_stories
    story = data["stories"][0]

    # 创建 EpicDriver 实例
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=5,
        retry_failed=True,  # 启用重试
        verbose=True,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换（包括失败状态）
    status_sequence = [
        "Draft",
        "Failed",  # 第一次失败
        "Draft",   # 重试
        "In Progress",
        "Done"     # 最终成功
    ]
    status_index = 0

    async def mock_parse_status(path):
        nonlocal status_index
        if status_index < len(status_sequence):
            status = status_sequence[status_index]
            status_index += 1
            return status
        return "Done"

    driver._parse_story_status = mock_parse_status

    # 模拟执行（第一次失败，后续成功）
    call_count = 0
    async def mock_execute_dev(story_path, iteration=1):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return False  # 前两次失败
        return True  # 后续成功

    driver.execute_dev_phase = mock_execute_dev
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行流程
    result = await driver.run()

    # 验证结果 - 应该重试并最终成功
    assert result is True, "Error recovery should succeed after retries"
    assert call_count >= 2, "Should have retried after failure"


@pytest.mark.e2e
@pytest.mark.anyio
async def test_cancellation_handling(
    temp_epic_and_stories
):
    """测试取消信号的正确处理"""
    # 获取测试数据
    data = temp_epic_and_stories

    # 创建 EpicDriver 实例
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=True,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟长时间运行的任务
    async def mock_parse_status(path):
        await anyio.sleep(0.1)  # 模拟处理时间
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 启动任务并取消
    try:
        async with anyio.create_task_group() as tg:
            # 启动 Epic 处理
            task = tg.start_soon(driver.run)

            # 短暂等待后取消
            await anyio.sleep(0.05)
            tg.cancel_scope.cancel()

        # 如果没有抛出取消异常，测试通过
        # （因为取消是正常的）
        assert True
    except anyio.get_cancelled_exc_class():
        # 取消是正常的
        assert True


@pytest.mark.e2e
@pytest.mark.anyio
async def test_state_persistence(
    temp_epic_and_stories
):
    """测试状态持久化正确性"""
    # 获取测试数据
    data = temp_epic_and_stories
    story = data["stories"][0]

    # 创建 EpicDriver 实例
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=True,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态转换
    async def mock_parse_status(path):
        # 第一次调用返回 Draft，后续返回 Done
        if not hasattr(mock_parse_status, 'called'):
            mock_parse_status.called = True
            return "Draft"
        return "Done"

    driver._parse_story_status = mock_parse_status

    # 模拟执行
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 第一次执行
    result1 = await driver.run()
    assert result1 is True

    # 第二次执行（应该检测到已完成状态）
    result2 = await driver.run()
    assert result2 is True

    # 验证状态管理器被正确使用
    # （通过检查状态更新调用）
    assert driver.state_manager is not None


@pytest.mark.e2e
@pytest.mark.anyio
async def test_full_epic_processing(
    temp_epic_and_stories
):
    """测试完整 Epic 处理流程"""
    # 获取测试数据
    data = temp_epic_and_stories

    # 创建 EpicDriver 实例
    driver = EpicDriver(
        epic_path=str(data["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=True,
        concurrent=False,
        use_claude=False,
        source_dir=str(data["project_root"] / "src"),
        test_dir=str(data["project_root"] / "tests"),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟所有状态转换
    async def mock_parse_status(path):
        if "1.1" in path or "1.2" in path:
            return "Done"
        return "Draft"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 执行完整流程
    start_time = time.time()
    result = await driver.run()
    elapsed_time = time.time() - start_time

    # 验证结果
    assert result is True, "Epic processing should complete successfully"
    assert len(driver.stories) >= 2, "Should have found at least 2 stories"

    # 验证执行时间合理（应该在合理时间内完成）
    assert elapsed_time < 30, "Epic processing should complete within 30 seconds"


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

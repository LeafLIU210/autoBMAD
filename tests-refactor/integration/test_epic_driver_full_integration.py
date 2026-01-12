"""
EpicDriver 完整流程集成测试
测试 EpicDriver 的完整功能和集成点
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver


@pytest.fixture
def temp_epic_environment():
    """创建临时 Epic 环境"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        epic_dir = tmp_path / "docs" / "epics"
        stories_dir = tmp_path / "docs" / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建 Epic 文件
        epic_file = epic_dir / "test-epic.md"
        epic_content = """# Epic 1: 测试 Epic

## Stories
### Story 1.1: 测试故事 1
### Story 1.2: 测试故事 2
"""
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建 Story 文件
        story1_file = stories_dir / "1.1-test-story-1.md"
        story1_content = """# Story 1.1: 测试故事 1

**Status**: Draft

## Description
这是一个测试故事。
"""
        story1_file.write_text(story1_content, encoding='utf-8')

        story2_file = stories_dir / "1.2-test-story-2.md"
        story2_content = """# Story 1.2: 测试故事 2

**Status**: Draft

## Description
这是另一个测试故事。
"""
        story2_file.write_text(story2_content, encoding='utf-8')

        # 创建源码和测试文件
        (src_dir / "test_module.py").write_text("def hello(): return 'world'\n", encoding='utf-8')
        (tests_dir / "test_test_module.py").write_text("def test_hello(): assert True\n", encoding='utf-8')

        yield {
            "epic_file": epic_file,
            "stories": [story1_file, story2_file],
            "src_dir": src_dir,
            "tests_dir": tests_dir
        }


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_complete_workflow(temp_epic_environment):
    """测试 EpicDriver 完整工作流程"""
    env = temp_epic_environment

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态解析：第一次为Draft，第二次为Done
    async def mock_parse_status(path):
        if not hasattr(mock_parse_status, 'call_count'):
            mock_parse_status.call_count = 0
        mock_parse_status.call_count += 1

        # 第一次调用返回Draft触发开发，第二次返回Done
        if mock_parse_status.call_count <= 2:
            return "Draft"
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 模拟状态管理器
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行完整流程
    result = await driver.run()

    # 验证结果
    assert result is True
    assert len(driver.stories) > 0
    assert driver.execute_dev_phase.call_count >= 1


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_with_multiple_stories(temp_epic_environment):
    """测试 EpicDriver 处理多个故事"""
    env = temp_epic_environment

    # 创建有多个故事的 Epic
    epic_file = env["epic_file"]
    epic_content = """# Epic 2: 多故事测试

## Stories
### Story 2.1: 故事 1
### Story 2.2: 故事 2
### Story 2.3: 故事 3
### Story 2.4: 故事 4
"""
    epic_file.write_text(epic_content, encoding='utf-8')

    # 创建对应的故事文件
    for i in range(1, 5):
        story_file = env["epic_file"].parent.parent / "stories" / f"2.{i}-story-{i}.md"
        story_content = f"""# Story 2.{i}: 故事 {i}

**Status**: Draft

## Description
这是第 {i} 个故事。
"""
        story_file.write_text(story_content, encoding='utf-8')

    # 创建 EpicDriver
    driver = EpicDriver(
        epic_path=str(epic_file),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态解析为完成
    driver._parse_story_status = AsyncMock(return_value="Done")
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行流程
    result = await driver.run()

    # 验证结果
    assert result is True
    assert len(driver.stories) == 4


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_cancellation_handling(temp_epic_environment):
    """测试 EpicDriver 取消信号处理"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟取消信号
    async def mock_parse_status(path):
        # 模拟在第二次调用时抛出取消异常
        if not hasattr(mock_parse_status, 'call_count'):
            mock_parse_status.call_count = 0
        mock_parse_status.call_count += 1

        if mock_parse_status.call_count > 1:
            raise asyncio.CancelledError("Task cancelled")
        return "Done"

    driver._parse_story_status = mock_parse_status
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行流程并处理取消
    try:
        result = await driver.run()
        # 如果没有抛出异常，验证结果
        assert result is True
    except asyncio.CancelledError:
        # 取消是正常的，测试通过
        pass


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_error_recovery(temp_epic_environment):
    """测试 EpicDriver 错误恢复机制"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=3,
        retry_failed=True,  # 启用重试
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟第一次失败，第二次成功的开发阶段
    call_count = 0
    async def mock_execute_dev_phase(story_path, iteration=1):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # 第一次调用失败
            raise Exception("Simulated failure")
        # 第二次调用成功
        return True

    driver._parse_story_status = AsyncMock(return_value="Done")
    driver.execute_dev_phase = mock_execute_dev_phase
    driver.execute_qa_phase = AsyncMock(return_value=True)
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行流程
    result = await driver.run()

    # 验证结果 - 重试机制应该使其成功
    assert result is True
    assert call_count >= 2  # 至少重试一次


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_parse_epic_integration(temp_epic_environment):
    """测试 EpicDriver Epic 解析集成"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        use_claude=False
    )

    # 解析 Epic
    stories = await driver.parse_epic()

    # 验证解析结果
    assert len(stories) == 2
    assert stories[0]["id"] == "1.1"
    assert stories[1]["id"] == "1.2"
    assert all("path" in story for story in stories)


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_quality_gates_integration(temp_epic_environment):
    """测试 EpicDriver 质量门控集成"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=False,  # 启用质量门控
        skip_tests=True
    )

    # 模拟状态为完成
    driver._parse_story_status = AsyncMock(return_value="Done")
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行流程
    result = await driver.run()

    # 验证结果
    assert result is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_state_consistency(temp_epic_environment):
    """测试 EpicDriver 状态一致性"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=3,
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态为完成
    driver._parse_story_status = AsyncMock(return_value="Done")
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)

    # 模拟状态管理器返回一致状态
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value={"status": "completed"})
    driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
        "success_count": 1,
        "error_count": 0
    })

    # 执行流程
    result = await driver.run()

    # 验证结果
    assert result is True
    # 验证状态同步被调用
    driver.state_manager.sync_story_statuses_to_markdown.assert_called_once()


@pytest.mark.integration
@pytest.mark.anyio
async def test_epic_driver_max_iterations_enforcement(temp_epic_environment):
    """测试 EpicDriver 最大迭代次数强制执行"""
    env = temp_epic_environment

    driver = EpicDriver(
        epic_path=str(env["epic_file"]),
        max_iterations=2,  # 设置低迭代次数
        retry_failed=False,
        verbose=False,
        concurrent=False,
        use_claude=False,
        source_dir=str(env["src_dir"]),
        test_dir=str(env["tests_dir"]),
        skip_quality=True,
        skip_tests=True
    )

    # 模拟状态始终为草稿（不会完成）
    driver._parse_story_status = AsyncMock(return_value="Draft")
    driver.execute_dev_phase = AsyncMock(return_value=True)
    driver.execute_qa_phase = AsyncMock(return_value=True)
    driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
    driver.state_manager.get_story_status = AsyncMock(return_value=None)

    # 执行流程
    result = await driver.run()

    # 验证结果 - 应该因为达到最大迭代次数而返回 False
    assert result is False


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-m", "integration"])

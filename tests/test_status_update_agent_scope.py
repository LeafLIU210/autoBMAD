"""测试 StatusUpdateAgent 的范围限制功能"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import the classes we need to test
from autoBMAD.epic_automation.agents.status_update_agent import StatusUpdateAgent, BatchUpdateResults
from autoBMAD.epic_automation.state_manager import StateManager


@pytest.fixture
def temp_db_path(tmp_path):
    """创建临时数据库路径"""
    return str(tmp_path / "test.db")


@pytest.fixture
def state_manager(temp_db_path):
    """创建 StateManager 实例"""
    sm = StateManager(db_path=temp_db_path, use_connection_pool=False)
    yield sm
    # 清理
    db_file = Path(temp_db_path)
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
async def async_state_manager(temp_db_path):
    """创建异步 StateManager 实例"""
    sm = StateManager(db_path=temp_db_path, use_connection_pool=False)
    yield sm
    # 清理
    db_file = Path(temp_db_path)
    if db_file.exists():
        db_file.unlink()


@pytest.mark.asyncio
async def test_get_stories_by_ids_with_valid_ids():
    """测试 get_stories_by_ids 方法 - 正常场景"""
    # 创建临时数据库
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        async_state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)

        # 准备测试数据
        epic_path = "docs/epics/epic-001-test.md"

        # 插入多个故事记录
        await async_state_manager.update_story_status(
            story_path="docs/stories/001.1-test-story.md",
            status="completed",
            epic_path=epic_path,
            phase="dev"
        )
        await async_state_manager.update_story_status(
            story_path="docs/stories/001.2-test-story.md",
            status="in_progress",
            epic_path=epic_path,
            phase="dev"
        )
        await async_state_manager.update_story_status(
            story_path="docs/stories/002.1-test-story.md",  # 不同epic
            status="completed",
            epic_path="docs/epics/epic-002-test.md",
            phase="dev"
        )

        # 测试查询 - 只查询当前epic的两个故事
        story_ids = ["docs/stories/001.1-test-story.md", "docs/stories/001.2-test-story.md"]
        results = await async_state_manager.get_stories_by_ids(epic_path, story_ids)

        # 验证结果
        assert len(results) == 2

        # 验证返回的故事路径
        returned_paths = [r["story_path"] for r in results]
        assert "docs/stories/001.1-test-story.md" in returned_paths
        assert "docs/stories/001.2-test-story.md" in returned_paths

        # 验证状态正确
        for result in results:
            if result["story_path"] == "docs/stories/001.1-test-story.md":
                assert result["status"] == "completed"
            elif result["story_path"] == "docs/stories/001.2-test-story.md":
                assert result["status"] == "in_progress"


@pytest.mark.asyncio
async def test_get_stories_by_ids_with_empty_list():
    """测试 get_stories_by_ids 方法 - 空列表"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        async_state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)

        epic_path = "docs/epics/epic-001-test.md"
        results = await async_state_manager.get_stories_by_ids(epic_path, [])
        assert results == []


@pytest.mark.asyncio
async def test_get_stories_by_ids_nonexistent_epic():
    """测试 get_stories_by_ids 方法 - 不存在的epic"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        async_state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)

        epic_path = "docs/epics/epic-999-nonexistent.md"
        story_ids = ["docs/stories/999.1-test-story.md"]
        results = await async_state_manager.get_stories_by_ids(epic_path, story_ids)
        assert results == []


@pytest.mark.asyncio
async def test_get_stories_by_ids_partial_match():
    """测试 get_stories_by_ids 方法 - 部分匹配"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        async_state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)

        epic_path = "docs/epics/epic-001-test.md"

        # 插入三个故事
        await async_state_manager.update_story_status(
            story_path="docs/stories/001.1-test-story.md",
            status="completed",
            epic_path=epic_path,
            phase="dev"
        )
        await async_state_manager.update_story_status(
            story_path="docs/stories/001.2-test-story.md",
            status="in_progress",
            epic_path=epic_path,
            phase="dev"
        )
        await async_state_manager.update_story_status(
            story_path="docs/stories/001.3-test-story.md",
            status="pending",
            epic_path=epic_path,
            phase="dev"
        )

        # 只查询其中两个
        story_ids = [
            "docs/stories/001.1-test-story.md",
            "docs/stories/001.3-test-story.md"
        ]
        results = await async_state_manager.get_stories_by_ids(epic_path, story_ids)

        # 验证只返回了查询的两个
        assert len(results) == 2
        returned_paths = [r["story_path"] for r in results]
        assert "docs/stories/001.1-test-story.md" in returned_paths
        assert "docs/stories/001.3-test-story.md" in returned_paths
        assert "docs/stories/001.2-test-story.md" not in returned_paths


@pytest.mark.asyncio
async def test_status_update_agent_scoped_sync():
    """测试 StatusUpdateAgent 的范围限制同步功能"""
    # 创建模拟的 StateManager
    mock_state_manager = AsyncMock()
    mock_state_manager.get_stories_by_ids = AsyncMock()
    mock_state_manager.get_stories_by_ids.return_value = [
        {
            "story_path": "docs/stories/001.1-test-story.md",
            "status": "completed",
        },
        {
            "story_path": "docs/stories/001.2-test-story.md",
            "status": "in_progress",
        },
    ]
    
    # 创建 StatusUpdateAgent 实例
    agent = StatusUpdateAgent()
    
    # 模拟 batch_update_statuses 方法
    agent.batch_update_statuses = AsyncMock(return_value={
        "success_count": 2,
        "error_count": 0,
        "errors": []
    })
    
    # 执行范围限制同步
    epic_id = "docs/epics/epic-001-test.md"
    story_ids = ["001.1", "001.2"]
    
    result = await agent.sync_from_database(
        state_manager=mock_state_manager,
        epic_id=epic_id,
        story_ids=story_ids
    )
    
    # 验证调用了 get_stories_by_ids
    mock_state_manager.get_stories_by_ids.assert_called_once_with(epic_id, story_ids)
    
    # 验证结果
    assert result["success_count"] == 2
    assert result["error_count"] == 0


@pytest.mark.asyncio
async def test_status_update_agent_backward_compatibility():
    """测试 StatusUpdateAgent 向后兼容性（全库同步）"""
    # 创建模拟的 StateManager
    mock_state_manager = AsyncMock()
    mock_state_manager.get_all_stories = AsyncMock()
    mock_state_manager.get_all_stories.return_value = [
        {
            "story_path": "docs/stories/001.1-test-story.md",
            "status": "completed",
        },
    ]
    
    # 创建 StatusUpdateAgent 实例
    agent = StatusUpdateAgent()
    
    # 模拟 batch_update_statuses 方法
    agent.batch_update_statuses = AsyncMock(return_value={
        "success_count": 1,
        "error_count": 0,
        "errors": []
    })
    
    # 不传递范围参数，使用全库同步（向后兼容）
    result = await agent.sync_from_database(
        state_manager=mock_state_manager
    )
    
    # 验证调用了 get_all_stories
    mock_state_manager.get_all_stories.assert_called_once()
    
    # 验证结果
    assert result["success_count"] == 1
    assert result["error_count"] == 0


@pytest.mark.asyncio
async def test_status_update_agent_filter_statuses():
    """测试 StatusUpdateAgent 的状态过滤功能"""
    # 创建模拟的 StateManager
    mock_state_manager = AsyncMock()
    mock_state_manager.get_stories_by_ids = AsyncMock()
    mock_state_manager.get_stories_by_ids.return_value = [
        {
            "story_path": "docs/stories/001.1-test-story.md",
            "status": "completed",
        },
        {
            "story_path": "docs/stories/001.2-test-story.md",
            "status": "in_progress",
        },
        {
            "story_path": "docs/stories/001.3-test-story.md",
            "status": "completed",
        },
    ]
    
    # 创建 StatusUpdateAgent 实例
    agent = StatusUpdateAgent()
    
    # 模拟 batch_update_statuses 方法
    agent.batch_update_statuses = AsyncMock(return_value={
        "success_count": 2,
        "error_count": 0,
        "errors": []
    })
    
    # 执行范围限制同步 + 状态过滤
    epic_id = "docs/epics/epic-001-test.md"
    story_ids = ["001.1", "001.2", "001.3"]
    
    result = await agent.sync_from_database(
        state_manager=mock_state_manager,
        epic_id=epic_id,
        story_ids=story_ids,
        filter_statuses=["completed"]  # 只同步 completed 状态
    )
    
    # 验证结果 - 3个故事都应该被查询，但batch_update只处理符合过滤条件的
    assert result["success_count"] == 2  # 2个completed状态的故事
    assert result["error_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

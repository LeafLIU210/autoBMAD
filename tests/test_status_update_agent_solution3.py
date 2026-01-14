"""测试 StatusUpdateAgent 方案3实现

测试覆盖：
1. 状态映射逻辑（PROCESSING_TO_CORE_STATUS）
2. 映射方法（_map_to_core_status）
3. 完整同步流程（sync_from_database）
4. 边界场景处理
5. 端到端验证

遵循方案3：单一真源原则
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil

# Import the classes we need to test
from autoBMAD.epic_automation.agents.status_update_agent import StatusUpdateAgent, BatchUpdateResults
from autoBMAD.epic_automation.state_manager import StateManager


class TestStatusUpdateAgentMapping:
    """测试状态映射逻辑"""

    def test_processing_to_core_status_mapping_complete(self):
        """测试映射表覆盖所有合法处理状态"""
        agent = StatusUpdateAgent()

        # 所有可能的处理状态（来自方案3）
        expected_statuses = {'in_progress', 'review', 'completed', 'cancelled', 'error'}
        actual_statuses = set(agent.PROCESSING_TO_CORE_STATUS.keys())

        assert actual_statuses == expected_statuses, \
            f"Missing statuses: {expected_statuses - actual_statuses}, " \
            f"Extra statuses: {actual_statuses - expected_statuses}"

    def test_map_to_core_status_standard_mappings(self):
        """测试标准处理状态的映射"""
        agent = StatusUpdateAgent()

        assert agent._map_to_core_status('in_progress') == 'Ready for Development'
        assert agent._map_to_core_status('review') == 'Ready for Review'
        assert agent._map_to_core_status('completed') == 'Ready for Done'

    def test_map_to_core_status_error_handling(self):
        """测试错误状态的容错映射"""
        agent = StatusUpdateAgent()

        # cancelled 和 error 应该映射回 'Ready for Development'（容错机制）
        assert agent._map_to_core_status('cancelled') == 'Ready for Development'
        assert agent._map_to_core_status('error') == 'Ready for Development'

    def test_map_to_core_status_invalid(self):
        """测试非法状态的处理"""
        agent = StatusUpdateAgent()

        # 非法状态应该返回默认值（容错）
        result = agent._map_to_core_status('unknown_status')
        assert result == 'Ready for Development'

        # 应该记录警告日志
        with patch('autoBMAD.epic_automation.agents.status_update_agent.logger') as mock_logger:
            agent._map_to_core_status('invalid_status')
            mock_logger.warning.assert_called_once()

    def test_core_to_processing_reverse_mapping(self):
        """测试反向映射的完整性"""
        agent = StatusUpdateAgent()

        # 验证反向映射包含主要状态
        assert 'Ready for Development' in agent.CORE_TO_PROCESSING_STATUS
        assert 'Ready for Review' in agent.CORE_TO_PROCESSING_STATUS
        assert 'Ready for Done' in agent.CORE_TO_PROCESSING_STATUS
        assert 'Done' in agent.CORE_TO_PROCESSING_STATUS

    def test_generate_status_markdown(self):
        """测试Markdown状态文本生成"""
        agent = StatusUpdateAgent()

        status_text = agent._generate_status_markdown('Ready for Review')

        assert 'Ready for Review' in status_text
        assert '## Status' in status_text
        assert '**Status**: Ready for Review' in status_text
        assert '**Last Updated**:' in status_text


class TestStatusUpdateAgentValidation:
    """测试状态验证逻辑"""

    def test_validate_processing_statuses_valid(self):
        """测试合法状态验证"""
        agent = StatusUpdateAgent()

        records = [
            {'story_path': 'docs/stories/001.1.md', 'status': 'completed'},
            {'story_path': 'docs/stories/001.2.md', 'status': 'review'},
            {'story_path': 'docs/stories/001.3.md', 'status': 'in_progress'},
        ]

        valid_count, invalid = agent.validate_processing_statuses(
            epic_id='test-epic',
            story_ids=['001.1', '001.2', '001.3'],
            records=records
        )

        assert valid_count == 3
        assert len(invalid) == 0

    def test_validate_processing_statuses_invalid(self):
        """测试非法状态验证"""
        agent = StatusUpdateAgent()

        records = [
            {'story_path': 'docs/stories/001.1.md', 'status': 'completed'},
            {'story_path': 'docs/stories/001.2.md', 'status': 'failed'},  # 非法状态
            {'story_path': 'docs/stories/001.3.md', 'status': 'unknown'},  # 非法状态
        ]

        valid_count, invalid = agent.validate_processing_statuses(
            epic_id='test-epic',
            story_ids=['001.1', '001.2', '001.3'],
            records=records
        )

        assert valid_count == 1
        assert len(invalid) == 2
        assert invalid[0]['processing_status'] == 'failed'
        assert invalid[1]['processing_status'] == 'unknown'


class TestStatusUpdateAgentSync:
    """测试状态同步功能"""

    @pytest.mark.asyncio
    async def test_sync_from_database_scoped_with_mapping(self):
        """测试范围限制同步 + 状态映射"""
        # 创建模拟的 StateManager
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {
                "story_path": "docs/stories/001.1-test-story.md",
                "status": "completed",  # processing_status
            },
            {
                "story_path": "docs/stories/001.2-test-story.md",
                "status": "review",  # processing_status
            },
            {
                "story_path": "docs/stories/001.3-test-story.md",
                "status": "in_progress",  # processing_status
            },
        ]

        # 创建 StatusUpdateAgent 实例
        agent = StatusUpdateAgent()

        # 模拟 batch_update_statuses 方法
        agent.batch_update_statuses = AsyncMock(return_value={
            "success_count": 3,
            "error_count": 0,
            "errors": []
        })

        # 执行范围限制同步
        epic_id = "docs/epics/epic-001-test.md"
        story_ids = ["001.1", "001.2", "001.3"]

        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id=epic_id,
            story_ids=story_ids
        )

        # 验证调用了 get_stories_by_ids
        mock_state_manager.get_stories_by_ids.assert_called_once_with(epic_id, story_ids)

        # 验证结果
        assert result["success_count"] == 3
        assert result["error_count"] == 0

        # 验证映射：batch_update_statuses 应该接收映射后的核心状态
        call_args = agent.batch_update_statuses.call_args
        status_mappings = call_args[0][0]  # 第一个位置参数

        # 验证映射正确
        assert len(status_mappings) == 3

        paths = [m[0] for m in status_mappings]
        statuses = [m[1] for m in status_mappings]

        assert "docs/stories/001.1-test-story.md" in paths
        assert "docs/stories/001.2-test-story.md" in paths
        assert "docs/stories/001.3-test-story.md" in paths

        # 验证状态映射正确（方案3）
        assert 'Ready for Done' in statuses  # completed -> Ready for Done
        assert 'Ready for Review' in statuses  # review -> Ready for Review
        assert 'Ready for Development' in statuses  # in_progress -> Ready for Development

    @pytest.mark.asyncio
    async def test_sync_with_error_and_cancelled_states(self):
        """测试错误和取消状态的容错映射"""
        # 创建模拟的 StateManager
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {
                "story_path": "docs/stories/001.1-error-story.md",
                "status": "error",
            },
            {
                "story_path": "docs/stories/001.2-cancelled-story.md",
                "status": "cancelled",
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

        # 执行同步
        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id="test-epic",
            story_ids=["001.1", "001.2"]
        )

        # 验证结果
        assert result["success_count"] == 2

        # 验证映射：error 和 cancelled 都应该映射为 'Ready for Development'
        call_args = agent.batch_update_statuses.call_args
        status_mappings = call_args[0][0]

        statuses = [m[1] for m in status_mappings]
        assert all(status == 'Ready for Development' for status in statuses)

    @pytest.mark.asyncio
    async def test_sync_with_filter_statuses(self):
        """测试状态过滤功能"""
        # 创建模拟的 StateManager
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {"story_path": "docs/stories/001.1.md", "status": "completed"},
            {"story_path": "docs/stories/001.2.md", "status": "review"},
            {"story_path": "docs/stories/001.3.md", "status": "completed"},
        ]

        # 创建 StatusUpdateAgent 实例
        agent = StatusUpdateAgent()
        agent.batch_update_statuses = AsyncMock(return_value={
            "success_count": 2,
            "error_count": 0,
            "errors": []
        })

        # 执行同步 + 状态过滤
        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id="test-epic",
            story_ids=["001.1", "001.2", "001.3"],
            filter_statuses=["completed"]  # 只同步 completed 状态
        )

        # 验证结果：只处理了 2 个 completed 状态的故事
        assert result["success_count"] == 2

        # 验证过滤生效
        call_args = agent.batch_update_statuses.call_args
        status_mappings = call_args[0][0]
        assert len(status_mappings) == 2

        # 验证只处理了 completed 状态的故事
        for path, status in status_mappings:
            assert status == 'Ready for Done'  # completed -> Ready for Done

    @pytest.mark.asyncio
    async def test_sync_missing_story_path(self):
        """测试缺少 story_path 的处理"""
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {"story_path": "docs/stories/001.1.md", "status": "completed"},
            {"status": "completed"},  # 缺少 story_path
            {"story_path": "docs/stories/001.3.md", "status": "review"},
        ]

        agent = StatusUpdateAgent()
        agent.batch_update_statuses = AsyncMock(return_value={
            "success_count": 2,
            "error_count": 0,
            "errors": []
        })

        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id="test-epic",
            story_ids=["001.1", "001.2", "001.3"]
        )

        # 验证只处理了 2 个有效的故事（跳过缺少 story_path 的）
        assert result["success_count"] == 2

    @pytest.mark.asyncio
    async def test_sync_missing_status(self):
        """测试缺少 status 的处理"""
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {"story_path": "docs/stories/001.1.md", "status": "completed"},
            {"story_path": "docs/stories/001.2.md"},  # 缺少 status
            {"story_path": "docs/stories/001.3.md", "status": "review"},
        ]

        agent = StatusUpdateAgent()
        agent.batch_update_statuses = AsyncMock(return_value={
            "success_count": 2,
            "error_count": 0,
            "errors": []
        })

        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id="test-epic",
            story_ids=["001.1", "001.2", "001.3"]
        )

        # 验证只处理了 2 个有效的故事（跳过缺少 status 的）
        assert result["success_count"] == 2

    @pytest.mark.asyncio
    async def test_sync_empty_results(self):
        """测试空结果的处理"""
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock(return_value=[])

        agent = StatusUpdateAgent()

        result = await agent.sync_from_database(
            state_manager=mock_state_manager,
            epic_id="test-epic",
            story_ids=[]
        )

        # 验证返回空结果
        assert result["success_count"] == 0
        assert result["error_count"] == 0
        assert len(result["errors"]) == 0


class TestStatusUpdateAgentIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_end_to_end_success_scenario(self):
        """
        端到端测试：成功场景
        验证：成功 Story 不再被回写为 Failed
        """
        # 创建临时数据库
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)

            # 准备测试数据
            epic_path = "docs/epics/epic-001-test.md"

            # 插入 3 个故事，都标记为 completed
            await state_manager.update_story_status(
                story_path="docs/stories/001.1-test-story.md",
                status="completed",
                epic_path=epic_path,
                phase="dev"
            )
            await state_manager.update_story_status(
                story_path="docs/stories/001.2-test-story.md",
                status="completed",
                epic_path=epic_path,
                phase="dev"
            )
            await state_manager.update_story_status(
                story_path="docs/stories/001.3-test-story.md",
                status="completed",
                epic_path=epic_path,
                phase="dev"
            )

            # 创建 StatusUpdateAgent
            agent = StatusUpdateAgent()

            # 模拟 SDK 更新（不实际调用 SDK）
            with patch.object(agent, 'update_story_status_via_sdk', new_callable=AsyncMock) as mock_sdk:
                mock_sdk.return_value = True

                # 执行同步
                result = await agent.sync_from_database(
                    state_manager=state_manager,
                    epic_id=epic_path,
                    story_ids=[
                        "docs/stories/001.1-test-story.md",
                        "docs/stories/001.2-test-story.md",
                        "docs/stories/001.3-test-story.md"
                    ]
                )

                # 验证结果
                assert result["success_count"] == 3
                assert result["error_count"] == 0

                # 验证所有故事都被更新为 'Ready for Done'（不是 'Failed'）
                for call in mock_sdk.call_args_list:
                    args, kwargs = call
                    target_status = args[1]  # 第二个参数是 target_status
                    assert target_status == 'Ready for Done', \
                        f"Expected 'Ready for Done', got '{target_status}'"
                    assert target_status != 'Failed', \
                        "Success story should NOT be updated to 'Failed'"


class TestStatusUpdateAgentBackwardCompatibility:
    """向后兼容性测试"""

    @pytest.mark.asyncio
    async def test_full_database_sync_backward_compatibility(self):
        """测试全库同步向后兼容性"""
        # 创建模拟的 StateManager
        mock_state_manager = AsyncMock()
        mock_state_manager.get_all_stories = AsyncMock()
        mock_state_manager.get_all_stories.return_value = [
            {"story_path": "docs/stories/001.1.md", "status": "completed"},
        ]

        # 创建 StatusUpdateAgent 实例
        agent = StatusUpdateAgent()
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


class TestStatusUpdateAgentLogs:
    """日志测试"""

    @pytest.mark.asyncio
    async def test_sync_logs_mapping_progress(self):
        """测试同步过程中的映射日志"""
        mock_state_manager = AsyncMock()
        mock_state_manager.get_stories_by_ids = AsyncMock()
        mock_state_manager.get_stories_by_ids.return_value = [
            {"story_path": "docs/stories/001.1.md", "status": "completed"},
        ]

        agent = StatusUpdateAgent()
        agent.batch_update_statuses = AsyncMock(return_value={
            "success_count": 1,
            "error_count": 0,
            "errors": []
        })

        with patch('autoBMAD.epic_automation.agents.status_update_agent.logger') as mock_logger:
            await agent.sync_from_database(
                state_manager=mock_state_manager,
                epic_id="test-epic",
                story_ids=["001.1"]
            )

            # 验证记录了映射日志
            mock_logger.info.assert_any_call(
                "[StatusUpdate] docs/stories/001.1.md: completed → Ready for Done"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

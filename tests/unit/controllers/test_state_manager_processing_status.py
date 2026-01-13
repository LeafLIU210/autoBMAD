"""
StateManager processing_status 测试（方案2）

测试 StateManager 的 update_story_processing_status 方法的功能：
1. 基本状态更新
2. 参数验证
3. 状态值验证
4. 错误处理
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path as PathLib

# 添加项目路径
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.state_manager import StateManager


@pytest.fixture
async def state_manager():
    """StateManager fixture，使用临时文件数据库"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test.db"
        state_manager = StateManager(db_path=str(db_path), use_connection_pool=False)
        yield state_manager


class TestStateManagerProcessingStatus:
    """StateManager processing_status 测试类（方案2）"""

    @pytest.mark.anyio
    async def test_update_story_processing_status_basic(self, state_manager):
        """测试基本状态更新功能"""
        # 更新状态
        result = await state_manager.update_story_processing_status(
            story_id="test-story-1.1",
            processing_status='in_progress',
            timestamp=datetime.now()
        )

        # 验证结果
        assert result is True

        # 验证数据库中的状态
        story_status = await state_manager.get_story_status("test-story-1.1")
        assert story_status is not None
        assert story_status['status'] == 'in_progress'
        assert story_status['phase'] == 'in_progress'

    @pytest.mark.anyio
    async def test_update_story_processing_status_all_valid_statuses(self, state_manager):
        """测试所有有效状态值"""
        valid_statuses = ['in_progress', 'review', 'completed']

        for status in valid_statuses:
            story_id = f"test-story-{status}"
            result = await state_manager.update_story_processing_status(
                story_id=story_id,
                processing_status=status,
                timestamp=datetime.now()
            )
            assert result is True, f"Failed to update status to {status}"

            # 验证数据库中的状态
            story_status = await state_manager.get_story_status(story_id)
            assert story_status is not None
            assert story_status['status'] == status
            assert story_status['phase'] == status

    @pytest.mark.anyio
    async def test_update_story_processing_status_invalid_status(self, state_manager):
        """测试无效状态值"""
        # 测试无效状态值
        with pytest.raises(ValueError) as exc_info:
            await state_manager.update_story_processing_status(
                story_id="test-story-invalid",
                processing_status='invalid_status',
                timestamp=datetime.now()
            )

        assert "Invalid processing_status" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_update_story_processing_status_with_metadata(self, state_manager):
        """测试带元数据的状态更新"""
        metadata = {
            'context': 'Dev completed successfully',
            'retry_count': 1,
            'error_message': None
        }

        result = await state_manager.update_story_processing_status(
            story_id="test-story-with-metadata",
            processing_status='review',
            timestamp=datetime.now(),
            metadata=metadata
        )

        # 验证结果
        assert result is True

        # 验证数据库中的状态
        story_status = await state_manager.get_story_status("test-story-with-metadata")
        assert story_status is not None
        assert story_status['status'] == 'review'

    @pytest.mark.anyio
    async def test_update_story_processing_status_with_epic_id(self, state_manager):
        """测试带Epic ID的状态更新"""
        result = await state_manager.update_story_processing_status(
            story_id="test-story-1.1",
            processing_status='in_progress',
            timestamp=datetime.now(),
            epic_id="test-epic"
        )

        # 验证结果
        assert result is True

        # 验证数据库中的状态
        story_status = await state_manager.get_story_status("test-story-1.1")
        assert story_status is not None
        assert story_status['status'] == 'in_progress'
        assert story_status['epic_path'] == "test-epic"

    @pytest.mark.anyio
    async def test_update_story_processing_status_update_existing(self, state_manager):
        """测试更新已存在的故事状态"""
        # 第一次更新
        result1 = await state_manager.update_story_processing_status(
            story_id="test-story-existing",
            processing_status='in_progress',
            timestamp=datetime.now()
        )
        assert result1 is True

        # 第二次更新
        result2 = await state_manager.update_story_processing_status(
            story_id="test-story-existing",
            processing_status='review',
            timestamp=datetime.now()
        )
        assert result2 is True

        # 验证最终状态
        story_status = await state_manager.get_story_status("test-story-existing")
        assert story_status is not None
        assert story_status['status'] == 'review'
        assert story_status['phase'] == 'review'

    @pytest.mark.anyio
    async def test_update_story_processing_status_invalid_metadata(self, state_manager):
        """测试无效元数据的处理"""
        # 测试无效元数据（不可序列化的对象）
        class NonSerializable:
            pass

        metadata = {
            'context': 'test',
            'non_serializable': NonSerializable()
        }

        # 应该能处理无效元数据
        result = await state_manager.update_story_processing_status(
            story_id="test-story-invalid-metadata",
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata=metadata
        )

        # 验证结果（应该成功，但元数据可能被清理）
        assert result is True

    @pytest.mark.anyio
    async def test_update_story_processing_status_none_metadata(self, state_manager):
        """测试None元数据的处理"""
        result = await state_manager.update_story_processing_status(
            story_id="test-story-none-metadata",
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata=None
        )

        # 验证结果
        assert result is True

        # 验证数据库中的状态
        story_status = await state_manager.get_story_status("test-story-none-metadata")
        assert story_status is not None
        assert story_status['status'] == 'in_progress'

    @pytest.mark.anyio
    async def test_update_story_processing_status_empty_metadata(self, state_manager):
        """测试空元数据的处理"""
        result = await state_manager.update_story_processing_status(
            story_id="test-story-empty-metadata",
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata={}
        )

        # 验证结果
        assert result is True

        # 验证数据库中的状态
        story_status = await state_manager.get_story_status("test-story-empty-metadata")
        assert story_status is not None
        assert story_status['status'] == 'in_progress'

    @pytest.mark.anyio
    async def test_state_transition_sequence(self, state_manager):
        """测试状态转换序列（方案2流程）"""
        story_id = "test-story-sequence"

        # 状态转换序列：
        # 1. 开始处理
        result1 = await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata={'context': 'Dev-QA cycle started'}
        )
        assert result1 is True

        # 2. Dev成功，进入评审
        result2 = await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='review',
            timestamp=datetime.now(),
            metadata={'context': 'Dev completed successfully'}
        )
        assert result2 is True

        # 3. QA成功，完成
        result3 = await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='completed',
            timestamp=datetime.now(),
            metadata={'context': 'QA passed, story completed'}
        )
        assert result3 is True

        # 验证最终状态
        story_status = await state_manager.get_story_status(story_id)
        assert story_status is not None
        assert story_status['status'] == 'completed'

    @pytest.mark.anyio
    async def test_state_transition_with_retry(self, state_manager):
        """测试带重试的状态转换"""
        story_id = "test-story-retry"

        # 状态转换序列（带重试）：
        # 1. 开始处理
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='in_progress',
            timestamp=datetime.now()
        )

        # 2. Dev失败，继续开发
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata={'context': 'Dev failed, continuing development', 'retry_count': 1}
        )

        # 3. Dev重试成功，进入评审
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='review',
            timestamp=datetime.now(),
            metadata={'context': 'Dev completed successfully', 'retry_count': 2}
        )

        # 4. QA成功，完成
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='completed',
            timestamp=datetime.now()
        )

        # 验证最终状态
        story_status = await state_manager.get_story_status(story_id)
        assert story_status is not None
        assert story_status['status'] == 'completed'

    @pytest.mark.anyio
    async def test_state_transition_with_qa_rejection(self, state_manager):
        """测试QA拒绝的状态转换"""
        story_id = "test-story-qa-rejection"

        # 状态转换序列（QA拒绝）：
        # 1. 开始处理
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='in_progress',
            timestamp=datetime.now()
        )

        # 2. Dev成功，进入评审
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='review',
            timestamp=datetime.now()
        )

        # 3. QA拒绝，返回开发
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='in_progress',
            timestamp=datetime.now(),
            metadata={'context': 'QA rejected, returning to development'}
        )

        # 4. Dev返工成功，进入评审
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='review',
            timestamp=datetime.now()
        )

        # 5. QA通过，完成
        await state_manager.update_story_processing_status(
            story_id=story_id,
            processing_status='completed',
            timestamp=datetime.now()
        )

        # 验证最终状态
        story_status = await state_manager.get_story_status(story_id)
        assert story_status is not None
        assert story_status['status'] == 'completed'

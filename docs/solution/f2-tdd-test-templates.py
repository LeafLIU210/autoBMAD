#!/usr/bin/env python3
"""F2 问题 TDD 测试模板

此文件包含所有测试用例的完整实现模板，可以直接复制到 tests/ 目录下使用。

使用方法:
    1. 复制对应 Phase 的测试到 tests/ 目录
    2. 运行测试确认失败 (Red)
    3. 实现功能使测试通过 (Green)
    4. 重构优化 (Refactor)
"""

# ============================================================================
# Phase 1: 止血阶段 (P0) - 一致性检查与修复
# ============================================================================

# tests/storage/test_state_consistency_detection.py
PHASE1_TEST_CONSISTENCY_DETECTION = '''
"""Phase 1 P0: 状态不一致检测测试"""

import pytest
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStateConsistencyDetection:
    """测试状态不一致检测能力 - Phase 1 P0"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """创建临时数据库"""
        db_path = tmp_path / "test.db"
        return str(db_path)
    
    @pytest.fixture
    def state_manager(self, temp_db):
        """创建 StateManager 实例"""
        return StateManager(db_path=temp_db)
    
    def test_detect_inconsistency_top_level_vs_state_json(self, state_manager, temp_db):
        """TC-P0-001-01: 检测顶层与 state_json 的 current_node 不一致"""
        # Arrange: 创建 pipeline
        pipeline_id = state_manager.create_pipeline(subject="Test Subject")
        
        # Arrange: 手动制造不一致（模拟历史数据问题）
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "UPDATE pipelines SET current_node = ? WHERE pipeline_id = ?",
            ("analyst", pipeline_id)
        )
        conn.commit()
        conn.close()
        
        # Act & Assert: 验证一致性检查能发现问题
        with patch('autoBMAD.docuswarm.storage.state_manager.logger') as mock_logger:
            state_manager._verify_state_consistency(pipeline_id)
            
            # 验证警告被记录
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            assert call_args.kwargs['pipeline_id'] == pipeline_id
            assert call_args.kwargs['top_current_node'] == 'analyst'
            assert call_args.kwargs['state_current_node'] is None
    
    def test_no_inconsistency_when_values_match(self, state_manager):
        """TC-P0-001-02: 数据一致时不应触发告警"""
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 通过正常 API 更新状态（模拟同步更新）
        # 注意：这里假设 update_pipeline_status 已经修复
        # 在初始测试中，这个测试可能会失败，需要配合实现
        
        # Act & Assert
        with patch('autoBMAD.docuswarm.storage.state_manager.logger') as mock_logger:
            state_manager._verify_state_consistency(pipeline_id)
            mock_logger.warning.assert_not_called()
    
    def test_consistency_check_with_null_values(self, state_manager):
        """TC-P0-001-03: 处理 null 值情况"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 初始状态两者都应为 null/None
        with patch('autoBMAD.docuswarm.storage.state_manager.logger') as mock_logger:
            state_manager._verify_state_consistency(pipeline_id)
            mock_logger.warning.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


PHASE1_TEST_SYNC_UPDATE = '''
# tests/storage/test_state_manager_sync_update.py

"""Phase 1 P0: StateManager 同步更新测试"""

import pytest
import sqlite3
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStateManagerSyncUpdate:
    """测试 update_pipeline_status 同步更新 state_json - Phase 1 P0"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test.db")
    
    @pytest.fixture
    def state_manager(self, temp_db):
        return StateManager(db_path=temp_db)
    
    def test_update_pipeline_status_syncs_to_state_json(self, state_manager):
        """TC-P0-002-01: update_pipeline_status 应同步更新 state_json"""
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # Act
        result = state_manager.update_pipeline_status(
            pipeline_id,
            status="running",
            current_node="analyst"
        )
        
        # Assert
        assert result is True
        
        # 验证读取时两者一致
        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["status"] == "running"
        assert pipeline["current_node"] == "analyst"
        assert pipeline["state"]["status"] == "running"
        assert pipeline["state"]["current_node"] == "analyst"
    
    def test_update_status_only_does_not_affect_other_state_fields(self, state_manager):
        """TC-P0-002-02: 仅更新 status 不应影响 state_json 其他字段"""
        # Arrange: 创建并设置完整状态
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 先设置一些状态数据
        state_manager._update_state_json_direct(
            pipeline_id,
            {
                "completed_nodes": ["analyst"],
                "deliverables": {"analyst": {"doc": "content"}},
                "current_node": "pm"
            }
        )
        
        # Act: 仅更新 status
        state_manager.update_pipeline_status(pipeline_id, status="completed")
        
        # Assert
        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["state"]["status"] == "completed"
        assert pipeline["state"]["completed_nodes"] == ["analyst"]
        assert pipeline["state"]["deliverables"]["analyst"]["doc"] == "content"
        assert pipeline["state"]["current_node"] == "pm"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


# ============================================================================
# Phase 2: 迁移阶段 (P1) - 统一状态访问
# ============================================================================

PHASE2_TEST_STATE_ACCESS_VIEW = '''
# tests/storage/test_state_access_view.py

"""Phase 2 P1: PipelineStateView 测试"""

import pytest
from autoBMAD.docuswarm.storage.state_access import PipelineStateView


class TestPipelineStateView:
    """测试 PipelineStateView 状态访问视图 - Phase 2 P1"""
    
    def test_view_reads_current_node_from_state_json(self):
        """TC-P1-001-01: current_node 应从 state_json 读取"""
        # Arrange: 模拟双重来源不一致的情况
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "subject": "Test",
            "current_node": "analyst",  # 顶层值（过时）
            "state": {
                "current_node": "pm",    # state_json 值（正确）
                "status": "running",
                "completed_nodes": ["analyst"]
            }
        }
        
        # Act
        view = PipelineStateView(pipeline_data)
        
        # Assert: 应该从 state_json 读取
        assert view.current_node == "pm"
        assert view.status == "running"
    
    def test_view_handles_missing_state_gracefully(self):
        """TC-P1-001-02: 处理缺失 state 字段的情况"""
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "subject": "Test"
        }
        
        view = PipelineStateView(pipeline_data)
        
        assert view.current_node is None
        assert view.status == "unknown"
        assert view.completed_nodes == []
    
    def test_view_is_node_completed_method(self):
        """TC-P1-001-03: is_node_completed 方法应正确判断"""
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "state": {
                "completed_nodes": ["analyst", "pm"],
                "current_node": "ux"
            }
        }
        
        view = PipelineStateView(pipeline_data)
        
        assert view.is_node_completed("analyst") is True
        assert view.is_node_completed("pm") is True
        assert view.is_node_completed("ux") is False
        assert view.is_node_completed("architect") is False
    
    def test_view_get_node_deliverable(self):
        """TC-P1-001-04: 获取节点交付物"""
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "state": {
                "deliverables": {
                    "analyst": {"doc": "analysis.md"},
                    "pm": {"doc": "plan.md"}
                }
            }
        }
        
        view = PipelineStateView(pipeline_data)
        
        assert view.get_node_deliverable("analyst") == {"doc": "analysis.md"}
        assert view.get_node_deliverable("pm") == {"doc": "plan.md"}
        assert view.get_node_deliverable("ux") is None
    
    def test_view_to_dict_serialization(self):
        """TC-P1-001-05: to_dict 应正确序列化"""
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "subject": "Test Subject",
            "state": {
                "current_node": "pm",
                "status": "running",
                "completed_nodes": ["analyst"]
            }
        }
        
        view = PipelineStateView(pipeline_data)
        result = view.to_dict()
        
        assert result["pipeline_id"] == "pipe-001"
        assert result["subject"] == "Test Subject"
        assert result["current_node"] == "pm"
        assert result["status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


PHASE2_TEST_UNIFIED_READ = '''
# tests/storage/test_unified_state_read.py

"""Phase 2 P1: 统一状态读取 API 测试"""

import pytest
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestUnifiedStateReadAPI:
    """测试统一状态读取 API - Phase 2 P1"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test.db")
    
    @pytest.fixture
    def state_manager(self, temp_db):
        return StateManager(db_path=temp_db)
    
    def test_get_current_node_reads_from_state_json(self, state_manager):
        """TC-P1-002-01: get_current_node 应从 state_json 读取"""
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager._update_state_json_direct(
            pipeline_id,
            {"current_node": "analyst"}
        )
        
        # Act
        result = state_manager.get_current_node(pipeline_id)
        
        # Assert
        assert result == "analyst"
    
    def test_get_pipeline_status_reads_from_state_json(self, state_manager):
        """TC-P1-002-02: get_pipeline_status 应从 state_json 读取"""
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager._update_state_json_direct(
            pipeline_id,
            {"status": "completed"}
        )
        
        # Act
        result = state_manager.get_pipeline_status(pipeline_id)
        
        # Assert
        assert result == "completed"
    
    def test_get_pipeline_returns_flattened_state(self, state_manager):
        """TC-P1-002-03: get_pipeline 应返回展开后的状态"""
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_state(
            pipeline_id,
            {
                "current_node": "pm",
                "status": "running",
                "completed_nodes": ["analyst"]
            }
        )
        
        # Act
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # Assert: 新格式 - 展开 state 字段
        assert pipeline["current_node"] == "pm"
        assert pipeline["status"] == "running"
        assert pipeline["completed_nodes"] == ["analyst"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


PHASE2_TEST_BACKWARD_COMPAT = '''
# tests/storage/test_backward_compatibility.py

"""Phase 2 P1: 向后兼容性测试"""

import pytest
import warnings
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestBackwardCompatibility:
    """测试向后兼容性 - Phase 2 P1"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test.db")
    
    @pytest.fixture
    def state_manager(self, temp_db):
        return StateManager(db_path=temp_db)
    
    def test_deprecated_update_pipeline_status_emits_warning(self, state_manager):
        """TC-P1-003-01: 废弃方法应发出警告"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        with pytest.warns(DeprecationWarning, match="update_pipeline_status.*deprecated"):
            result = state_manager.update_pipeline_status(
                pipeline_id,
                status="running",
                current_node="analyst"
            )
        
        assert result is True
    
    def test_old_get_pipeline_format_still_works(self, state_manager):
        """TC-P1-003-02: 旧版 get_pipeline 格式仍可用"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # 旧格式兼容
        assert "state" in pipeline
        assert isinstance(pipeline["state"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


# ============================================================================
# Phase 3: 清理阶段 (P2) - 最终一致性
# ============================================================================

PHASE3_TEST_FINAL_CONSISTENCY = '''
# tests/storage/test_final_state_consistency.py

"""Phase 3 P2: 最终一致性测试"""

import pytest
import sqlite3
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestFinalStateConsistency:
    """最终一致性测试 - Phase 3 P2"""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test.db")
    
    @pytest.fixture
    def state_manager(self, temp_db):
        return StateManager(db_path=temp_db)
    
    def test_no_top_level_current_node_column(self, temp_db):
        """TC-P2-001: 验证 current_node 列已删除"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("PRAGMA table_info(pipelines)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        assert "current_node" not in columns
    
    def test_all_reads_use_state_json_only(self, state_manager):
        """TC-P2-002: 验证所有读取只使用 state_json"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_state(
            pipeline_id,
            {"current_node": "analyst", "status": "running"}
        )
        
        # 各种读取操作
        pipeline = state_manager.get_pipeline(pipeline_id)
        current_node = state_manager.get_current_node(pipeline_id)
        status = state_manager.get_pipeline_status(pipeline_id)
        
        # 验证都从 state_json 读取
        assert pipeline["current_node"] == "analyst"
        assert current_node == "analyst"
        assert status == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


# ============================================================================
# 集成测试
# ============================================================================

INTEGRATION_TEST_LIFECYCLE = '''
# tests/integration/test_pipeline_lifecycle_state_consistency.py

"""Pipeline 全生命周期状态一致性集成测试"""

import pytest
import asyncio


class TestPipelineLifecycleStateConsistency:
    """Pipeline 全生命周期状态一致性集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle_maintains_consistency(self, orchestrator):
        """完整生命周期状态一致性测试"""
        # TODO: 实现完整生命周期测试
        pass
    
    @pytest.mark.asyncio
    async def test_restart_from_node_maintains_consistency(self, orchestrator):
        """重启后状态一致性测试"""
        # TODO: 实现重启一致性测试
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


# ============================================================================
# 主函数：输出所有测试模板
# ============================================================================

def print_test_templates():
    """打印所有测试模板"""
    
    print("=" * 80)
    print("F2 问题 TDD 测试模板")
    print("=" * 80)
    print()
    
    templates = [
        ("Phase 1 - 一致性检测", "tests/storage/test_state_consistency_detection.py", PHASE1_TEST_CONSISTENCY_DETECTION),
        ("Phase 1 - 同步更新", "tests/storage/test_state_manager_sync_update.py", PHASE1_TEST_SYNC_UPDATE),
        ("Phase 2 - StateView", "tests/storage/test_state_access_view.py", PHASE2_TEST_STATE_ACCESS_VIEW),
        ("Phase 2 - 统一读取", "tests/storage/test_unified_state_read.py", PHASE2_TEST_UNIFIED_READ),
        ("Phase 2 - 向后兼容", "tests/storage/test_backward_compatibility.py", PHASE2_TEST_BACKWARD_COMPAT),
        ("Phase 3 - 最终一致性", "tests/storage/test_final_state_consistency.py", PHASE3_TEST_FINAL_CONSISTENCY),
        ("集成测试", "tests/integration/test_pipeline_lifecycle_state_consistency.py", INTEGRATION_TEST_LIFECYCLE),
    ]
    
    for name, path, template in templates:
        print(f"\n{'=' * 80}")
        print(f"{name}")
        print(f"文件: {path}")
        print(f"{'=' * 80}\n")
        print(template)


if __name__ == "__main__":
    print_test_templates()

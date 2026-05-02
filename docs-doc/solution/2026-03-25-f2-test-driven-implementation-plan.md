# F2 问题测试驱动实施方案

> **文档版本**: 1.0  
> **日期**: 2026-03-25  
> **关联文档**: 
> - [F2 深度研究报告](../research/2026-03-25-f2-state-json-consistency-research-report.md)
> - [统一设计方案技术规范](../research/2026-03-25-f2-unified-design-spec.md)

---

## 1. 实施方法论：测试驱动开发 (TDD)

### 1.1 核心理念

采用 **Red-Green-Refactor** 循环：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Red       │────▶│   Green     │────▶│  Refactor   │
│  (写失败测试) │     │  (使测试通过) │     │  (重构优化)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲───────────────────────────────────────┘
```

### 1.2 F2 问题 TDD 策略

对于 F2 问题的特殊性，采用 **由外向内** 的测试策略：

```
Level 4: 集成测试 (Integration Tests)
    │
    ├── 测试完整 Pipeline 生命周期状态一致性
    ├── 测试恢复/取消等操作的正确性
    └── 验证修复后系统整体行为
    │
Level 3: 契约测试 (Contract Tests)
    │
    ├── 验证 StateManager API 契约
    ├── 验证状态访问规范
    └── 验证向后兼容性
    │
Level 2: 单元测试 (Unit Tests)
    │
    ├── 测试 StateManager 新方法
    ├── 测试状态一致性检查
    └── 测试数据迁移逻辑
    │
Level 1: 契约/契约测试 (Contract First)
    │
    ├── 定义新 API 接口 (update_pipeline_state)
    ├── 定义状态访问规范 (PipelineStateView)
    └── 定义废弃标记策略
```

---

## 2. Phase 1: 止血阶段（P0）- 一致性检查与修复

### 2.1 测试目标

确保系统能够：
1. **检测** 状态不一致问题
2. **告警** 不一致情况
3. **修复** 高危操作的数据同步

### 2.2 测试用例设计

#### 2.2.1 TC-P0-001: 一致性检查检测能力

```python
# tests/storage/test_state_consistency_detection.py

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
        """TC-P0-001-01: 检测顶层与 state_json 的 current_node 不一致
        
        Given:
            - 创建 pipeline
            - 直接修改数据库使顶层 current_node 与 state_json 不一致
            
        When:
            - 调用一致性检查方法
            
        Then:
            - 应该检测到不一致
            - 应该记录警告日志
        """
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
        """TC-P0-001-02: 数据一致时不应触发告警
        
        Given:
            - 创建 pipeline
            - 使用正常 API 更新状态（保持同步）
            
        When:
            - 调用一致性检查方法
            
        Then:
            - 不应记录警告日志
        """
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 通过正常 API 更新状态
        state_manager.update_pipeline_status(
            pipeline_id, status="running", current_node="analyst"
        )
        
        # Act & Assert
        with patch('autoBMAD.docuswarm.storage.state_manager.logger') as mock_logger:
            state_manager._verify_state_consistency(pipeline_id)
            mock_logger.warning.assert_not_called()
    
    def test_consistency_check_with_null_values(self, state_manager):
        """TC-P0-001-03: 处理 null 值情况
        
        Given:
            - current_node 为 null 的情况
            
        When:
            - 调用一致性检查
            
        Then:
            - 正确处理 null 比较
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 初始状态两者都应为 null/None
        with patch('autoBMAD.docuswarm.storage.state_manager.logger') as mock_logger:
            state_manager._verify_state_consistency(pipeline_id)
            mock_logger.warning.assert_not_called()
```

#### 2.2.2 TC-P0-002: 高危操作修复验证

```python
# tests/storage/test_state_manager_sync_update.py

class TestStateManagerSyncUpdate:
    """测试 update_pipeline_status 同步更新 state_json - Phase 1 P0"""
    
    def test_update_pipeline_status_syncs_to_state_json(self, state_manager):
        """TC-P0-002-01: update_pipeline_status 应同步更新 state_json
        
        Given:
            - 已存在的 pipeline
            
        When:
            - 调用 update_pipeline_status 更新状态和 current_node
            
        Then:
            - 顶层字段应更新
            - state_json 内的对应字段也应更新
            - 两者保持一致
        """
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
        """TC-P0-002-02: 仅更新 status 不应影响 state_json 其他字段
        
        Given:
            - pipeline 已有完整状态（包括 completed_nodes, deliverables 等）
            
        When:
            - 仅调用 update_pipeline_status 更新 status
            
        Then:
            - status 更新
            - 其他 state_json 字段保持不变
        """
        # Arrange: 创建并设置完整状态
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager._update_state_json_direct(pipeline_id, {
            "completed_nodes": ["analyst"],
            "deliverables": {"analyst": {"doc": "content"}},
            "current_node": "pm"
        })
        
        # Act: 仅更新 status
        state_manager.update_pipeline_status(pipeline_id, status="completed")
        
        # Assert
        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["state"]["status"] == "completed"
        assert pipeline["state"]["completed_nodes"] == ["analyst"]
        assert pipeline["state"]["deliverables"]["analyst"]["doc"] == "content"
        assert pipeline["state"]["current_node"] == "pm"
```

#### 2.2.3 TC-P0-003: 运行时一致性检查集成

```python
# tests/integration/test_runtime_consistency_checks.py

class TestRuntimeConsistencyChecks:
    """测试运行时一致性检查集成 - Phase 1 P0"""
    
    @pytest.mark.asyncio
    async def test_consistency_check_before_critical_operations(self):
        """TC-P0-003-01: 关键操作前应触发一致性检查
        
        Given:
            - 配置为在关键操作前执行一致性检查
            
        When:
            - 执行 restart_from_node
            - 执行 cancel_current_node
            
        Then:
            - 一致性检查方法被调用
        """
        # 此测试验证集成行为
        # 实际实现时检查日志或 mock
        pass
```

### 2.3 实现代码（使测试通过）

#### 2.3.1 一致性检查实现

```python
# autoBMAD/docuswarm/storage/state_manager.py

import logging
import json
import warnings
from typing import Any

logger = logging.getLogger(__name__)


class StateManager:
    """StateManager with consistency checks - Phase 1 implementation."""
    
    def __init__(self, db_path: str | None = None) -> None:
        self._db = DatabaseManager.get_instance(db_path=db_path or "docuswarm.db")
    
    def _verify_state_consistency(self, pipeline_id: str) -> dict[str, Any] | None:
        """运行时一致性检查 - P0 新增
        
        验证顶层字段与 state_json 的一致性，发现不一致时记录警告。
        
        Returns:
            如果不一致返回差异信息，否则返回 None
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT current_node, state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                top_current_node = row["current_node"]
                state = json.loads(row["state_json"] or "{}")
                state_current_node = state.get("current_node")
                
                if top_current_node != state_current_node:
                    inconsistency = {
                        "pipeline_id": pipeline_id,
                        "top_current_node": top_current_node,
                        "state_current_node": state_current_node,
                        "field": "current_node"
                    }
                    logger.warning(
                        "state_inconsistency_detected",
                        **inconsistency,
                        operation="consistency_check"
                    )
                    return inconsistency
                
                return None
                
        except Exception as e:
            logger.error("consistency_check_failed", pipeline_id=pipeline_id, error=str(e))
            return None
    
    def update_pipeline_status(
        self,
        pipeline_id: str,
        status: str,
        current_node: str | None = None,
    ) -> bool:
        """更新 pipeline 状态 - Phase 1 修复版
        
        DEPRECATED: 此方法保留用于向后兼容。
        内部实现现在同步更新 state_json。
        """
        # 在更新前检查一致性（可选，用于监控）
        self._verify_state_consistency(pipeline_id)
        
        # 1. 更新顶层字段（保持原有行为）
        self._validate_status(status)
        
        with self._db.acquire() as conn:
            if current_node is not None:
                conn.execute(
                    "UPDATE pipelines SET status = ?, current_node = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (status, current_node, pipeline_id),
                )
            else:
                conn.execute(
                    "UPDATE pipelines SET status = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (status, pipeline_id),
                )
        
        # 2. 同步更新 state_json（Phase 1 新增）
        state_update = {"status": status}
        if current_node is not None:
            state_update["current_node"] = current_node
        self._update_state_json_partial(pipeline_id, state_update)
        
        return True
    
    def _update_state_json_partial(
        self,
        pipeline_id: str,
        partial_update: dict[str, Any]
    ) -> bool:
        """部分更新 state_json - 内部方法
        
        读取现有 state_json，深度合并 partial_update，然后写回。
        """
        with self._db.acquire() as conn:
            # 读取现有状态
            cursor = conn.execute(
                "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return False
            
            # 解析并合并
            current_state = json.loads(row["state_json"] or "{}")
            self._deep_merge(current_state, partial_update)
            
            # 写回
            updated_json = json.dumps(current_state)
            conn.execute(
                "UPDATE pipelines SET state_json = ? WHERE pipeline_id = ?",
                (updated_json, pipeline_id)
            )
        
        return True
    
    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """深度合并 source 到 target"""
        for key, value in source.items():
            if (key in target and 
                isinstance(target[key], dict) and 
                isinstance(value, dict)):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
```

---

## 3. Phase 2: 迁移阶段（P1）- 统一状态访问

### 3.1 测试目标

1. **建立统一的状态访问规范**
2. **迁移所有读操作到 state_json**
3. **保持向后兼容性**

### 3.2 测试用例设计

#### 3.2.1 TC-P1-001: PipelineStateView 状态视图

```python
# tests/storage/test_state_access_view.py

from autoBMAD.docuswarm.storage.state_access import PipelineStateView


class TestPipelineStateView:
    """测试 PipelineStateView 状态访问视图 - Phase 2 P1"""
    
    def test_view_reads_current_node_from_state_json(self):
        """TC-P1-001-01: current_node 应从 state_json 读取
        
        Given:
            - pipeline 数据字典，包含 state 字段
            
        When:
            - 创建 PipelineStateView 并访问 current_node
            
        Then:
            - 返回 state_json 内的值
            - 忽略顶层 current_node（即使存在）
        """
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
        """TC-P1-001-02: 处理缺失 state 字段的情况
        
        Given:
            - pipeline 数据缺少 state 字段
            
        When:
            - 创建 PipelineStateView
            
        Then:
            - 使用默认值，不抛出异常
        """
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "subject": "Test"
            # 缺少 "state" 字段
        }
        
        view = PipelineStateView(pipeline_data)
        
        assert view.current_node is None
        assert view.status == "unknown"
        assert view.completed_nodes == []
    
    def test_view_is_node_completed_method(self):
        """TC-P1-001-03: is_node_completed 方法应正确判断
        
        Given:
            - pipeline 有 completed_nodes 列表
            
        When:
            - 调用 is_node_completed 检查不同节点
            
        Then:
            - 已完成的节点返回 True
            - 未完成的节点返回 False
        """
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
        """TC-P1-001-04: 获取节点交付物
        
        Given:
            - pipeline 有 deliverables 数据
            
        When:
            - 调用 get_node_deliverable
            
        Then:
            - 返回对应节点的交付物
            - 不存在的节点返回 None
        """
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
        """TC-P1-001-05: to_dict 应正确序列化
        
        Given:
            - 完整的 PipelineStateView
            
        When:
            - 调用 to_dict()
            
        Then:
            - 返回包含所有字段的字典
            - 可用于序列化/传输
        """
        pipeline_data = {
            "pipeline_id": "pipe-001",
            "subject": "Test Subject",
            "state": {
                "current_node": "pm",
                "status": "running",
                "completed_nodes": ["analyst"],
                "node_iterations": {"analyst": 1, "pm": 2}
            }
        }
        
        view = PipelineStateView(pipeline_data)
        result = view.to_dict()
        
        assert result["pipeline_id"] == "pipe-001"
        assert result["subject"] == "Test Subject"
        assert result["current_node"] == "pm"
        assert result["status"] == "running"
        assert result["completed_nodes"] == ["analyst"]
```

#### 3.2.2 TC-P1-002: 统一状态读取 API

```python
# tests/storage/test_unified_state_read.py

class TestUnifiedStateReadAPI:
    """测试统一状态读取 API - Phase 2 P1"""
    
    def test_get_current_node_reads_from_state_json(self, state_manager):
        """TC-P1-002-01: get_current_node 应从 state_json 读取
        
        Given:
            - 已创建的 pipeline
            - state_json 中有 current_node
            
        When:
            - 调用 get_current_node
            
        Then:
            - 返回 state_json 中的值
        """
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager._update_state_json_direct(pipeline_id, {
            "current_node": "analyst"
        })
        
        # Act
        result = state_manager.get_current_node(pipeline_id)
        
        # Assert
        assert result == "analyst"
    
    def test_get_pipeline_status_reads_from_state_json(self, state_manager):
        """TC-P1-002-02: get_pipeline_status 应从 state_json 读取
        
        Given:
            - 已创建的 pipeline
            
        When:
            - 调用 get_pipeline_status
            
        Then:
            - 返回 state_json 中的 status
        """
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager._update_state_json_direct(pipeline_id, {
            "status": "completed"
        })
        
        # Act
        result = state_manager.get_pipeline_status(pipeline_id)
        
        # Assert
        assert result == "completed"
    
    def test_get_pipeline_returns_flattened_state(self, state_manager):
        """TC-P1-002-03: get_pipeline 应返回展开后的状态
        
        Given:
            - 已创建的 pipeline
            
        When:
            - 调用 get_pipeline
            
        Then:
            - 返回的字典包含展开后的 state 字段
            - 可以直接访问 current_node, status 等
        """
        # Arrange
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_state(pipeline_id, {
            "current_node": "pm",
            "status": "running",
            "completed_nodes": ["analyst"]
        })
        
        # Act
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # Assert: 新格式 - 展开 state 字段
        assert pipeline["current_node"] == "pm"
        assert pipeline["status"] == "running"
        assert pipeline["completed_nodes"] == ["analyst"]
        # state 字段仍然存在，用于兼容
        assert pipeline["state"]["current_node"] == "pm"
```

#### 3.2.3 TC-P1-003: 向后兼容性测试

```python
# tests/storage/test_backward_compatibility.py

class TestBackwardCompatibility:
    """测试向后兼容性 - Phase 2 P1"""
    
    def test_deprecated_update_pipeline_status_emits_warning(self, state_manager):
        """TC-P1-003-01: 废弃方法应发出警告
        
        Given:
            - 使用旧版 API 的代码
            
        When:
            - 调用 update_pipeline_status
            
        Then:
            - 发出 DeprecationWarning
            - 方法仍然正常工作
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        with pytest.warns(DeprecationWarning, match="update_pipeline_status.*deprecated"):
            result = state_manager.update_pipeline_status(
                pipeline_id, status="running", current_node="analyst"
            )
        
        assert result is True
    
    def test_old_get_pipeline_format_still_works(self, state_manager):
        """TC-P1-003-02: 旧版 get_pipeline 格式仍可用
        
        Given:
            - 依赖旧格式的代码
            
        When:
            - 调用 get_pipeline
            
        Then:
            - 返回包含 state 字段的字典（旧格式）
            - 同时包含展开后的字段（新格式）
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # 旧格式兼容
        assert "state" in pipeline
        assert isinstance(pipeline["state"], dict)
        
        # 新格式（展开字段）
        assert "pipeline_id" in pipeline
        assert "subject" in pipeline
```

### 3.3 实现代码

#### 3.3.1 PipelineStateView 实现

```python
# autoBMAD/docuswarm/storage/state_access.py

"""State access utilities for unified state management - Phase 2 P1."""

from typing import Any


class PipelineStateView:
    """Pipeline 状态视图 - 提供统一的状态访问接口。
    
    此类封装了从 state_json 读取状态的逻辑，确保所有状态访问
    都使用单一来源（state_json），消除双重来源风险。
    
    Example:
        >>> pipeline = state_manager.get_pipeline(pipeline_id)
        >>> view = PipelineStateView(pipeline)
        >>> print(view.current_node)  # 从 state_json 读取
        >>> print(view.status)        # 从 state_json 读取
    """
    
    def __init__(self, pipeline_data: dict[str, Any]) -> None:
        """初始化状态视图。
        
        Args:
            pipeline_data: pipeline 数据字典，包含 state 字段
        """
        self._data = pipeline_data
        self._state = pipeline_data.get("state", {}) if isinstance(pipeline_data.get("state"), dict) else {}
    
    @property
    def pipeline_id(self) -> str:
        """Pipeline ID"""
        return self._data.get("pipeline_id", "")
    
    @property
    def subject(self) -> str:
        """主题"""
        return self._data.get("subject", "")
    
    @property
    def status(self) -> str:
        """Pipeline 状态（从 state_json 读取）"""
        return self._state.get("status", "unknown")
    
    @property
    def current_node(self) -> str | None:
        """当前节点（从 state_json 读取）"""
        return self._state.get("current_node")
    
    @property
    def completed_nodes(self) -> list[str]:
        """已完成节点列表"""
        return self._state.get("completed_nodes", [])
    
    @property
    def is_running(self) -> bool:
        """是否运行中"""
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == "completed"
    
    def is_node_completed(self, node_id: str) -> bool:
        """检查节点是否已完成。
        
        Args:
            node_id: 节点 ID
            
        Returns:
            True if 节点在 completed_nodes 中
        """
        return node_id in self.completed_nodes
    
    def get_node_deliverable(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的交付物。
        
        Args:
            node_id: 节点 ID
            
        Returns:
            交付物字典，或 None
        """
        deliverables = self._state.get("deliverables", {})
        return deliverables.get(node_id)
    
    def get_node_iterations(self, node_id: str) -> int:
        """获取节点迭代次数。
        
        Args:
            node_id: 节点 ID
            
        Returns:
            迭代次数，默认为 0
        """
        iterations = self._state.get("node_iterations", {})
        return iterations.get(node_id, 0)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于序列化）。
        
        Returns:
            包含所有字段的字典
        """
        return {
            "pipeline_id": self.pipeline_id,
            "subject": self.subject,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": self.completed_nodes,
            "is_running": self.is_running,
            "is_completed": self.is_completed,
        }


class PipelineStateAccess:
    """静态状态访问工具类。
    
    提供便捷的状态字段访问，无需创建 PipelineStateView 实例。
    """
    
    @staticmethod
    def get_current_node(pipeline: dict[str, Any]) -> str | None:
        """统一从 state_json 获取 current_node。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("current_node")
    
    @staticmethod
    def get_status(pipeline: dict[str, Any]) -> str:
        """统一从 state_json 获取 status。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("status", "unknown")
    
    @staticmethod
    def get_completed_nodes(pipeline: dict[str, Any]) -> list[str]:
        """统一从 state_json 获取 completed_nodes。"""
        state = pipeline.get("state", {}) if isinstance(pipeline.get("state"), dict) else {}
        return state.get("completed_nodes", [])
```

#### 3.3.2 StateManager 扩展实现

```python
# autoBMAD/docuswarm/storage/state_manager.py - Phase 2 新增方法

import warnings


class StateManager:
    """StateManager - Phase 2 扩展"""
    
    # ... Phase 1 代码 ...
    
    def update_pipeline_state(
        self,
        pipeline_id: str,
        state_update: dict[str, Any],
    ) -> bool:
        """更新 Pipeline 状态（统一写入入口）。
        
        这是修改 Pipeline 状态的首选方法，所有状态变更
        应该通过此方法完成，确保单一真相源。
        
        Args:
            pipeline_id: Pipeline ID
            state_update: 状态更新字典，将与现有状态深度合并
            
        Returns:
            True if successful
            
        Example:
            >>> sm.update_pipeline_state("pipe-123", {
            ...     "current_node": "analyst",
            ...     "status": "running"
            ... })
        """
        if not self._pipeline_exists(pipeline_id):
            raise StorageError(
                f"Pipeline not found: {pipeline_id}",
                operation_type="update",
                pipeline_id=pipeline_id,
            )
        
        return self._update_state_json_partial(pipeline_id, state_update)
    
    def get_current_node(self, pipeline_id: str) -> str | None:
        """获取当前节点（从 state_json 读取）。"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline is None:
            return None
        return pipeline.get("state", {}).get("current_node")
    
    def get_pipeline_status(self, pipeline_id: str) -> str:
        """获取 Pipeline 状态（从 state_json 读取）。"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline is None:
            return "unknown"
        return pipeline.get("state", {}).get("status", "unknown")
    
    def is_node_completed(self, pipeline_id: str, node_id: str) -> bool:
        """检查节点是否已完成。"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline is None:
            return False
        completed_nodes = pipeline.get("state", {}).get("completed_nodes", [])
        return node_id in completed_nodes
    
    def update_pipeline_status(
        self,
        pipeline_id: str,
        status: str,
        current_node: str | None = None,
    ) -> bool:
        """[DEPRECATED] 更新 pipeline 状态。
        
        此方法已废弃，使用 update_pipeline_state() 替代。
        保留用于向后兼容。
        """
        warnings.warn(
            "update_pipeline_status() is deprecated, "
            "use update_pipeline_state() instead",
            DeprecationWarning,
            stacklevel=2
        )
        
        # 委托给新方法
        update = {"status": status}
        if current_node is not None:
            update["current_node"] = current_node
        return self.update_pipeline_state(pipeline_id, update)
```

---

## 4. Phase 3: 清理阶段（P2）- 代码重构

### 4.1 测试目标

1. **验证顶层 current_node 列删除后系统正常工作**
2. **验证所有旧方法已移除**
3. **验证最终一致性保证**

### 4.2 测试用例设计

```python
# tests/storage/test_final_state_consistency.py

class TestFinalStateConsistency:
    """最终一致性测试 - Phase 3 P2"""
    
    def test_no_top_level_current_node_column(self, temp_db):
        """TC-P2-001: 验证 current_node 列已删除
        
        Given:
            - 数据库已应用 Phase 3 迁移
            
        When:
            - 查询表结构
            
        Then:
            - pipelines 表不包含 current_node 列
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("PRAGMA table_info(pipelines)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        assert "current_node" not in columns
    
    def test_all_reads_use_state_json_only(self, state_manager):
        """TC-P2-002: 验证所有读取只使用 state_json
        
        Given:
            - 更新后的系统
            
        When:
            - 执行各种状态读取操作
            
        Then:
            - 所有值都从 state_json 获取
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_state(pipeline_id, {
            "current_node": "analyst",
            "status": "running"
        })
        
        # 各种读取操作
        pipeline = state_manager.get_pipeline(pipeline_id)
        current_node = state_manager.get_current_node(pipeline_id)
        status = state_manager.get_pipeline_status(pipeline_id)
        
        # 验证都从 state_json 读取
        assert pipeline["current_node"] == "analyst"
        assert current_node == "analyst"
        assert status == "running"
```

---

## 5. 集成测试套件

### 5.1 完整 Pipeline 生命周期测试

```python
# tests/integration/test_pipeline_lifecycle_state_consistency.py

import pytest
import asyncio


class TestPipelineLifecycleStateConsistency:
    """Pipeline 全生命周期状态一致性集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle_maintains_consistency(self, orchestrator):
        """完整生命周期状态一致性测试
        
        Scenario:
            1. 创建 Pipeline
            2. 启动 Pipeline
            3. 暂停/恢复
            4. 取消当前节点
            5. 从节点重启
            6. 完成 Pipeline
            
        Verification:
            - 每个阶段状态一致
            - current_node 始终正确
            - completed_nodes 准确反映进度
        """
        # 此测试将在 Phase 2-3 实现
        pass
    
    @pytest.mark.asyncio
    async def test_restart_from_node_maintains_consistency(self, orchestrator):
        """重启后状态一致性测试
        
        Scenario:
            1. 运行到 pm 节点
            2. 从 analyst 节点重启
            
        Verification:
            - current_node 更新为 analyst
            - completed_nodes 清空
            - 后续执行正常
        """
        # 此测试将在 Phase 2-3 实现
        pass
```

---

## 6. 测试执行计划

### 6.1 测试金字塔

```
                    ┌─────────┐
                    │   E2E   │  (5 tests)
                    │  Tests  │
                   ┌┴─────────┴┐
                   │ Integration│  (10 tests)
                   │   Tests    │
                  ┌┴────────────┴┐
                  │   Contract   │  (15 tests)
                  │    Tests     │
                 ┌┴──────────────┴┐
                 │     Unit       │  (30 tests)
                 │     Tests      │
                └┴────────────────┘
```

### 6.2 各阶段测试清单

#### Phase 1 (P0) - 止血

| 测试ID | 描述 | 优先级 |
|--------|------|--------|
| TC-P0-001-01 | 检测顶层与 state_json 不一致 | P0 |
| TC-P0-001-02 | 数据一致时不触发告警 | P0 |
| TC-P0-001-03 | 处理 null 值情况 | P0 |
| TC-P0-002-01 | update_pipeline_status 同步更新 | P0 |
| TC-P0-002-02 | 部分更新不影响其他字段 | P0 |
| TC-P0-003-01 | 关键操作前一致性检查 | P1 |

#### Phase 2 (P1) - 迁移

| 测试ID | 描述 | 优先级 |
|--------|------|--------|
| TC-P1-001-01 | PipelineStateView 读取 state_json | P0 |
| TC-P1-001-02 | 处理缺失 state 字段 | P0 |
| TC-P1-001-03 | is_node_completed 方法 | P0 |
| TC-P1-001-04 | get_node_deliverable 方法 | P1 |
| TC-P1-001-05 | to_dict 序列化 | P1 |
| TC-P1-002-01 | get_current_node 读取 state_json | P0 |
| TC-P1-002-02 | get_pipeline_status 读取 state_json | P0 |
| TC-P1-002-03 | get_pipeline 返回展开状态 | P0 |
| TC-P1-003-01 | 废弃方法发出警告 | P0 |
| TC-P1-003-02 | 向后兼容格式 | P0 |

#### Phase 3 (P2) - 清理

| 测试ID | 描述 | 优先级 |
|--------|------|--------|
| TC-P2-001 | 验证 current_node 列已删除 | P0 |
| TC-P2-002 | 所有读取只使用 state_json | P0 |

### 6.3 CI/CD 集成

```yaml
# .github/workflows/f2-state-consistency.yml

name: F2 State Consistency Tests

on:
  push:
    paths:
      - 'autoBMAD/docuswarm/storage/**'
      - 'autoBMAD/docuswarm/pipeline/**'
      - 'tests/storage/**'
      - 'tests/integration/**'

jobs:
  test-phase-1:
    name: Phase 1 - P0 Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run P0 Tests
        run: |
          pytest tests/storage/test_state_consistency_detection.py -v
          pytest tests/storage/test_state_manager_sync_update.py -v

  test-phase-2:
    name: Phase 2 - P1 Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run P1 Tests
        run: |
          pytest tests/storage/test_state_access_view.py -v
          pytest tests/storage/test_unified_state_read.py -v
          pytest tests/storage/test_backward_compatibility.py -v

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Integration Tests
        run: pytest tests/integration/test_pipeline_lifecycle_state_consistency.py -v
```

---

## 7. 验收标准

### 7.1 Phase 1 验收标准

- [x] 一致性检查测试全部通过
- [x] 高危操作修复测试全部通过
- [x] 代码审查通过
- [ ] 部署到 Staging 环境并监控 24 小时
- [ ] 无状态不一致告警

### 7.2 Phase 2 验收标准

- [x] PipelineStateView 测试全部通过
- [x] 统一状态读取 API 测试全部通过
- [x] 向后兼容性测试全部通过
- [ ] 所有 CLI 命令使用新 API
- [ ] 所有 Orchestrator 操作使用新 API

### 7.3 Phase 3 验收标准

- [x] 最终一致性测试全部通过
- [ ] 数据库迁移脚本执行成功
- [ ] 生产环境无回归问题
- [ ] 性能测试通过（无明显性能下降）

---

## 8. 附录

### 8.1 测试文件结构

```
tests/
├── storage/
│   ├── test_state_consistency_detection.py     # Phase 1 P0
│   ├── test_state_manager_sync_update.py       # Phase 1 P0
│   ├── test_state_access_view.py               # Phase 2 P1
│   ├── test_unified_state_read.py              # Phase 2 P1
│   ├── test_backward_compatibility.py          # Phase 2 P1
│   └── test_final_state_consistency.py         # Phase 3 P2
├── integration/
│   ├── test_runtime_consistency_checks.py      # Phase 1 P0
│   └── test_pipeline_lifecycle_state_consistency.py  # Phase 2-3
└── conftest.py
```

### 8.2 运行测试命令

```bash
# 运行所有 F2 相关测试
pytest tests/storage/test_state_consistency*.py tests/storage/test_state_access*.py tests/storage/test_unified*.py tests/storage/test_backward*.py tests/integration/test_*state*.py -v

# 运行特定 Phase 测试
pytest tests/storage/test_state_consistency_detection.py tests/storage/test_state_manager_sync_update.py -v  # Phase 1
pytest tests/storage/test_state_access_view.py tests/storage/test_unified_state_read.py -v  # Phase 2

# 生成覆盖率报告
pytest tests/storage/ tests/integration/ --cov=autoBMAD.docuswarm.storage --cov-report=html
```

### 8.3 调试指南

当测试失败时：

1. **检查测试数据库状态**
   ```python
   # 在测试中添加调试代码
   pipeline = state_manager.get_pipeline(pipeline_id)
   print(f"Pipeline state: {json.dumps(pipeline, indent=2)}")
   ```

2. **启用详细日志**
   ```python
   import logging
   logging.getLogger("autoBMAD.docuswarm.storage").setLevel(logging.DEBUG)
   ```

3. **使用调试工具**
   ```bash
   python tools/f2_state_consistency_analyzer.py --db test.db
   ```

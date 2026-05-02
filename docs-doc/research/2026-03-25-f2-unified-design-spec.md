# F2 统一设计方案技术规范

> **文档版本**: 1.0  
> **日期**: 2026-03-25  
> **关联文档**: [F2 深度研究报告](./2026-03-25-f2-state-json-consistency-research-report.md)

---

## 1. 设计目标

将 DocuSwarm 的 Pipeline 状态管理从**双重来源**改造为**单一真相源**，彻底消除 `state_json` 与顶层字段之间的不一致风险。

### 1.1 核心原则

1. **单一写入点**: 所有状态变更必须通过统一的 `update_pipeline_state()` 方法
2. **单一读取点**: 所有状态读取必须使用 `pipeline["state"]` 路径
3. **无冗余字段**: 删除 `pipelines.current_node`，所有状态信息存储在 `state_json`
4. **向后兼容**: 提供平滑迁移路径，避免破坏性变更

---

## 2. 数据模型设计

### 2.1 新 Schema 设计

```sql
-- 改造后的 pipelines 表
CREATE TABLE IF NOT EXISTS pipelines (
    pipeline_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    -- status 保留用于数据库查询过滤，但不参与业务逻辑
    status TEXT NOT NULL DEFAULT 'pending',
    -- current_node 将被删除，数据迁移到 state_json
    -- current_node TEXT,  -- DEPRECATED: to be removed
    state_json TEXT NOT NULL,  -- 唯一真相源，非空约束
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为常用查询创建索引
CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);

-- 使用 SQLite JSON1 扩展索引 state_json 内的字段（可选优化）
-- CREATE INDEX IF NOT EXISTS idx_state_current_node 
-- ON pipelines(json_extract(state_json, '$.current_node'));
```

### 2.2 PipelineState 类型（保持不变）

```python
# pipeline/state.py

class PipelineState(TypedDict):
    """Pipeline 状态的唯一真相源。
    
    所有状态信息必须存储在此结构中，并通过 state_json 持久化。
    """
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None          # 当前执行节点
    completed_nodes: list[str]        # 已完成节点列表
    deliverables: dict[str, dict[str, Any]]
    questions: dict[str, list[dict[str, Any]]]
    evaluations: dict[str, dict[str, Any]]
    node_iterations: dict[str, int]
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None
    status: str                       # pipeline 状态
    error: dict[str, Any] | None
    shared_context: dict[str, Any]
```

---

## 3. API 设计

### 3.1 StateManager 新接口

```python
# storage/state_manager.py

class StateManager:
    """Pipeline 状态管理器 - 单一真相源实现。"""
    
    # ==================== 核心状态操作 ====================
    
    def update_pipeline_state(
        self,
        pipeline_id: str,
        state_update: dict[str, Any],
    ) -> bool:
        """更新 Pipeline 状态（唯一写入入口）。
        
        这是修改 Pipeline 状态的唯一合法方式。所有状态变更
        必须通过此方法完成，确保单一真相源。
        
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
        # 实现：
        # 1. 读取现有 state_json
        # 2. 深度合并 state_update
        # 3. 验证新状态的完整性
        # 4. 写入数据库
        # 5. 可选：同步更新顶层 status 字段（仅用于查询）
        pass
    
    def get_pipeline_state(self, pipeline_id: str) -> PipelineState | None:
        """获取 Pipeline 完整状态（推荐读取方式）。
        
        Returns:
            PipelineState 对象，或 None if not found
        """
        pass
    
    def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
        """获取 Pipeline 完整信息（向后兼容）。
        
        返回的字典包含所有信息，但调用者应该优先使用
        get_pipeline_state() 获取类型安全的状态。
        """
        pass
    
    # ==================== 便捷查询方法 ====================
    
    def get_current_node(self, pipeline_id: str) -> str | None:
        """获取当前节点（从 state_json 读取）。"""
        state = self.get_pipeline_state(pipeline_id)
        return state.get("current_node") if state else None
    
    def get_pipeline_status(self, pipeline_id: str) -> str:
        """获取 Pipeline 状态（从 state_json 读取）。"""
        state = self.get_pipeline_state(pipeline_id)
        return state.get("status", "unknown") if state else "unknown"
    
    def is_node_completed(self, pipeline_id: str, node_id: str) -> bool:
        """检查节点是否已完成。"""
        state = self.get_pipeline_state(pipeline_id)
        if not state:
            return False
        return node_id in state.get("completed_nodes", [])
    
    # ==================== 已废弃方法（保留兼容）====================
    
    def update_pipeline_status(
        self,
        pipeline_id: str,
        status: str,
        current_node: str | None = None,
    ) -> bool:
        """[DEPRECATED] 使用 update_pipeline_state() 替代。
        
        此方法保留用于向后兼容，内部实现委托给 update_pipeline_state()。
        """
        warnings.warn(
            "update_pipeline_status() is deprecated, "
            "use update_pipeline_state() instead",
            DeprecationWarning,
            stacklevel=2
        )
        update = {"status": status}
        if current_node is not None:
            update["current_node"] = current_node
        return self.update_pipeline_state(pipeline_id, update)
```

### 3.2 状态访问帮助类

```python
# storage/state_access.py

class PipelineStateView:
    """Pipeline 状态视图 - 提供类型安全的状态访问。
    
    此类封装了从 state_json 读取状态的逻辑，提供便捷的
    属性访问方式。
    """
    
    def __init__(self, pipeline_data: dict[str, Any]) -> None:
        self._data = pipeline_data
        self._state = pipeline_data.get("state", {})
    
    @property
    def pipeline_id(self) -> str:
        return self._data["pipeline_id"]
    
    @property
    def subject(self) -> str:
        return self._data["subject"]
    
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
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        return self.status == "completed"
    
    def get_node_deliverable(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的交付物"""
        deliverables = self._state.get("deliverables", {})
        return deliverables.get(node_id)
    
    def get_node_iterations(self, node_id: str) -> int:
        """获取节点迭代次数"""
        iterations = self._state.get("node_iterations", {})
        return iterations.get(node_id, 0)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "pipeline_id": self.pipeline_id,
            "subject": self.subject,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": self.completed_nodes,
            # ... 其他字段
        }
```

---

## 4. 调用点改造

### 4.1 Orchestrator 改造

```python
# pipeline/orchestrator.py

class HybridOrchestrator:
    """改造后的 Orchestrator - 使用单一真相源。"""
    
    async def start_pipeline(self, ...) -> str:
        # ... 创建 pipeline ...
        
        # BEFORE: 分开更新顶层字段和 state_json
        # self._state_manager.update_pipeline_status(
        #     final_pipeline_id, status=RUNNING, current_node=PIPELINE_NODES[0]
        # )
        
        # AFTER: 统一通过 update_pipeline_state 更新
        await self._state_manager.update_pipeline_state(
            final_pipeline_id,
            {
                "status": RUNNING,
                "current_node": PIPELINE_NODES[0],
            }
        )
        
        # ... 执行 graph ...
        
        # AFTER: 从 result 获取最终状态并统一更新
        final_state_update = {
            "status": COMPLETED,
            "current_node": result.get("current_node", "po"),
            "completed_nodes": result.get("completed_nodes", []),
            "deliverables": result.get("deliverables", {}),
        }
        await self._state_manager.update_pipeline_state(
            final_pipeline_id, final_state_update
        )
        
        return final_pipeline_id
    
    async def restart_from_node(self, pipeline_id: str, node_id: str) -> dict[str, Any]:
        """从指定节点重启 Pipeline。"""
        # BEFORE: 从 pipeline["state"] 读取
        # pipeline = self._state_manager.get_pipeline(pipeline_id)
        # checkpoint_state = pipeline.get("state", {})
        
        # AFTER: 使用类型安全的 StateView
        pipeline = self._state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")
        
        state_view = PipelineStateView(pipeline)
        
        # 使用便捷属性访问状态
        completed_nodes = state_view.completed_nodes
        current_node = state_view.current_node
        
        # ... 重启逻辑 ...
        
        # AFTER: 统一更新状态
        await self._state_manager.update_pipeline_state(
            pipeline_id,
            {
                "status": RUNNING,
                "current_node": node_id,
                "completed_nodes": new_completed_nodes,
            }
        )
```

### 4.2 CLI Status 命令改造

```python
# cli/commands/status.py

@click.command()
@click.argument("pipeline_id")
def status(pipeline_id: str) -> None:
    """Show detailed progress of the specified pipeline."""
    service = PipelineService()
    
    try:
        pipeline = service.status(pipeline_id)
        
        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")
        
        # BEFORE: 混合来源读取
        # pipeline_state = pipeline.get("state", {})
        # current_node = pipeline.get("current_node", "")  # 从顶层读取！
        # completed_nodes = pipeline_state.get("completed_nodes", [])
        
        # AFTER: 统一从 state_json 读取
        state_view = PipelineStateView(pipeline)
        current_node = state_view.current_node
        completed_nodes = state_view.completed_nodes
        node_iterations = state_view._state.get("node_iterations", {})
        
        # 使用 state_view 属性显示状态
        table = Table(title=f"Pipeline Status: {pipeline_id}", show_header=True)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Pipeline ID", state_view.pipeline_id)
        table.add_row("Subject", state_view.subject)
        table.add_row("Status", f"[bold]{state_view.status}[/bold]")
        table.add_row("Current Node", current_node or "N/A")
        
        console.print(table)
        
        # 节点状态表
        nodes_table = Table(title="Node Status", show_header=True)
        nodes_table.add_column("Node", style="cyan")
        nodes_table.add_column("Status", style="green")
        nodes_table.add_column("Iteration", style="yellow")
        
        for node_id in PIPELINE_NODES:
            if state_view.is_node_completed(node_id):
                status_display = "[green]✓ Completed[/green]"
                iteration = str(state_view.get_node_iterations(node_id) or 1)
            elif node_id == current_node:
                status_display = "[yellow]→ Running[/yellow]"
                iteration = str(state_view.get_node_iterations(node_id) or 1)
            else:
                status_display = "[dim]○ Pending[/dim]"
                iteration = "-"
            
            nodes_table.add_row(node_id, status_display, iteration)
        
        console.print(nodes_table)
        
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(f"Failed to get pipeline status: {e}")
```

---

## 5. 数据迁移策略

### 5.1 迁移脚本

```python
# scripts/migrate_f2_state_consistency.py

"""F2 数据迁移脚本：确保顶层 current_node 与 state_json 一致。

迁移步骤：
1. 扫描所有 pipeline，检查不一致
2. 以 state_json 为准，修复顶层字段
3. 生成迁移报告
"""

import json
import sqlite3
from pathlib import Path


def migrate_pipeline_state(db_path: str, dry_run: bool = True) -> dict[str, Any]:
    """执行数据迁移。
    
    Args:
        db_path: 数据库路径
        dry_run: 如果 True，只报告不执行修改
        
    Returns:
        迁移报告
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute(
        "SELECT pipeline_id, status, current_node, state_json "
        "FROM pipelines WHERE state_json IS NOT NULL"
    )
    
    report = {
        "total": 0,
        "consistent": 0,
        "inconsistent": 0,
        "fixed": 0,
        "errors": [],
        "details": []
    }
    
    for row in cursor.fetchall():
        report["total"] += 1
        pipeline_id = row["pipeline_id"]
        
        try:
            state = json.loads(row["state_json"])
            state_current_node = state.get("current_node")
            top_current_node = row["current_node"]
            
            if top_current_node == state_current_node:
                report["consistent"] += 1
                continue
            
            # 不一致，需要修复
            report["inconsistent"] += 1
            detail = {
                "pipeline_id": pipeline_id,
                "top_current_node": top_current_node,
                "state_current_node": state_current_node,
                "action": "update_top_to_match_state" if not dry_run else "would_update"
            }
            report["details"].append(detail)
            
            if not dry_run:
                # 以 state_json 为准，更新顶层字段
                conn.execute(
                    "UPDATE pipelines SET current_node = ? WHERE pipeline_id = ?",
                    (state_current_node, pipeline_id)
                )
                report["fixed"] += 1
                
        except Exception as e:
            report["errors"].append({
                "pipeline_id": pipeline_id,
                "error": str(e)
            })
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="docuswarm.db")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", dest="dry_run", 
                       help="Apply migration (disable dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.dry_run
    print(f"Running migration (dry_run={dry_run})...")
    
    report = migrate_pipeline_state(args.db, dry_run=dry_run)
    
    print(f"\nMigration Report:")
    print(f"  Total pipelines: {report['total']}")
    print(f"  Consistent: {report['consistent']}")
    print(f"  Inconsistent: {report['inconsistent']}")
    print(f"  Fixed: {report['fixed']}")
    
    if report['details']:
        print(f"\nInconsistent details:")
        for d in report['details'][:10]:
            print(f"  {d['pipeline_id']}: top={d['top_current_node']}, state={d['state_current_node']}")
```

---

## 6. 测试规范

### 6.1 单元测试

```python
# tests/storage/test_state_manager_v2.py

import pytest
from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.storage.state_access import PipelineStateView


class TestStateManagerSingleSourceOfTruth:
    """验证 StateManager 单一真相源实现。"""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        db_path = tmp_path / "test.db"
        return StateManager(db_path=str(db_path))
    
    def test_update_pipeline_state_updates_state_json(self, state_manager):
        """验证 update_pipeline_state 正确更新 state_json"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 更新状态
        state_manager.update_pipeline_state(pipeline_id, {
            "current_node": "analyst",
            "status": "running"
        })
        
        # 验证：读取时应该看到更新后的值
        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline["state"]
        
        assert state["current_node"] == "analyst"
        assert state["status"] == "running"
    
    def test_no_direct_top_level_update(self, state_manager):
        """验证不存在直接更新顶层字段的代码路径"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # 使用新方法更新
        state_manager.update_pipeline_state(pipeline_id, {
            "current_node": "pm"
        })
        
        # 验证：顶层字段（如果存在）应该与 state_json 一致
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # 注意：此测试用于验证旧方法已被移除
        # 如果 current_node 仍在 schema 中，它应该与 state_json 一致
        if "current_node" in pipeline:
            assert pipeline["current_node"] == pipeline["state"]["current_node"]
    
    def test_state_view_reads_from_state_json(self, state_manager):
        """验证 PipelineStateView 从 state_json 读取"""
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_state(pipeline_id, {
            "current_node": "ux",
            "status": "completed",
            "completed_nodes": ["analyst", "pm"]
        })
        
        pipeline = state_manager.get_pipeline(pipeline_id)
        view = PipelineStateView(pipeline)
        
        assert view.current_node == "ux"
        assert view.status == "completed"
        assert view.completed_nodes == ["analyst", "pm"]
        assert view.is_node_completed("analyst") is True
        assert view.is_node_completed("ux") is False


class TestStateConsistency:
    """验证状态一致性。"""
    
    def test_concurrent_updates_maintain_consistency(self, state_manager):
        """验证并发更新不会导致不一致"""
        # 使用线程/协程模拟并发更新
        # 验证最终状态一致
        pass
    
    def test_state_json_always_has_priority(self, state_manager):
        """验证 state_json 始终优先于顶层字段"""
        # 如果两者不一致，业务逻辑应该使用 state_json
        pass
```

### 6.2 集成测试

```python
# tests/integration/test_pipeline_state_integration.py

import pytest


class TestPipelineStateIntegration:
    """Pipeline 状态集成测试。"""
    
    async def test_full_pipeline_lifecycle_state_consistency(self):
        """测试完整 Pipeline 生命周期中的状态一致性。"""
        # 1. 创建 Pipeline
        # 2. 启动 Pipeline
        # 3. 验证状态
        # 4. 模拟节点完成
        # 5. 验证 completed_nodes 和 current_node
        # 6. 暂停/恢复
        # 7. 验证状态仍然一致
        # 8. 取消
        # 9. 验证最终状态
        pass
    
    async def test_restart_maintains_state_consistency(self):
        """测试重启后状态一致性。"""
        # 1. 运行 Pipeline 到某个节点
        # 2. 从 earlier 节点重启
        # 3. 验证 current_node 和 completed_nodes 正确更新
        # 4. 验证所有来源读取的值一致
        pass
```

---

## 7. 实施路线图

### Phase 1: 基础设施（1-2周）

- [ ] 创建 `PipelineStateView` 类
- [ ] 实现新的 `update_pipeline_state()` 方法
- [ ] 添加运行时一致性检查
- [ ] 编写数据迁移脚本
- [ ] 添加 deprecation 警告到旧方法

### Phase 2: 调用点迁移（2-3周）

- [ ] 迁移 `orchestrator.py` 所有写操作
- [ ] 迁移 `orchestrator.py` 所有读操作
- [ ] 迁移 `cli/commands/status.py`
- [ ] 迁移其他 CLI 命令
- [ ] 迁移 `graph.py` 中的状态更新

### Phase 3: 数据迁移（1周）

- [ ] 在 staging 环境测试数据迁移
- [ ] 在生产环境执行迁移
- [ ] 验证所有数据一致性

### Phase 4: 清理（1周）

- [ ] 删除 `pipelines.current_node` 列
- [ ] 删除 `update_pipeline_status()` 方法
- [ ] 删除其他废弃方法
- [ ] 更新文档

### Phase 5: 验证（1周）

- [ ] 运行全量测试
- [ ] 进行手工回归测试
- [ ] 监控系统稳定性

---

## 8. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 数据迁移失败 | 低 | 高 | 完整备份；dry-run 验证；分阶段执行 |
| 代码遗漏 | 中 | 高 | 静态分析工具检查；代码审查；运行时检查 |
| 性能下降 | 低 | 中 | JSON 解析优化；数据库索引；缓存策略 |
| 向后兼容破坏 | 低 | 高 | 保持旧 API；deprecation 周期；灰度发布 |

---

## 9. 附录

### 9.1 废弃方法清单

| 方法 | 位置 | 替代方法 | 删除版本 |
|------|------|----------|----------|
| `update_pipeline_status()` | `state_manager.py` | `update_pipeline_state()` | v2.1 |
| `current_node` 顶层字段 | `database.py` | `state.current_node` | v2.1 |

### 9.2 代码审查检查清单

- [ ] 所有状态写入使用 `update_pipeline_state()`
- [ ] 所有状态读取使用 `PipelineStateView` 或 `pipeline["state"]`
- [ ] 没有直接访问 `pipeline["current_node"]`（顶层）
- [ ] 新方法有完整的类型注解
- [ ] 新方法有完整的 docstring
- [ ] 添加了对应的单元测试

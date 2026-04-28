# F2 问题深度研究报告：state_json 单一真相源收口分析

> **报告日期**: 2026-03-25  
> **研究对象**: DocuSwarm Pipeline 状态管理（state_json vs 顶层字段）  
> **评估来源**: `docs/evaluation/2026-03-25-docuswarm-deep-evaluation-report.md` - F2 发现  
> **研究工具**: `tools/f2_state_consistency_analyzer.py`

---

## 执行摘要

本报告针对评估报告中的 **F2 问题**（`state_json` 单一真相源方向正确，但实现仍未完全收口）进行深度研究。通过静态代码分析和调试工具验证，我们发现系统存在**双重状态来源**问题：

- **顶层字段**（`pipelines.current_node`, `pipelines.status`）
- **state_json 内部字段**（`state_json.current_node`, `state_json.status`）

这种双重来源导致状态读写路径混乱，存在严重的**状态不一致风险**。

### 核心发现

| 指标 | 数值 | 严重程度 |
|------|------|----------|
| 已知状态访问路径 | 18 处 | - |
| 双重来源访问 | 1 处 | **Critical** |
| 仅顶层写入操作 | 5 处 | **High** |
| 仅顶层读取操作 | 2 处 | **High** |
| 风险操作组合 | 2 组 | **High** |

---

## 1. 问题背景

### 1.1 设计意图

根据代码注释和架构方向，DocuSwarm 正朝着 **`state_json` 作为单一真相源** 演进：

```python
# storage/state_manager.py:118
# Create complete PipelineState (F1: state_json as single source of truth)
initial_state = create_initial_state(pipeline_id, subject_context or {})
state_json = json.dumps(initial_state)
```

`PipelineState` 类型定义（`pipeline/state.py:57-78`）包含了完整的状态信息：

```python
class PipelineState(TypedDict):
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]
    # ... 更多字段
```

### 1.2 现实偏离

尽管设计意图清晰，但数据库schema仍保留了**顶层字段**：

```sql
-- storage/database.py:162-172
CREATE TABLE IF NOT EXISTS pipelines (
    pipeline_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    current_node TEXT,        -- 冗余顶层字段
    state_json TEXT,          -- 真相源
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 2. 代码分析

### 2.1 双重来源写操作

#### 2.1.1 写入顶层 current_node（危险）

| 操作 | 文件位置 | 行号 | 场景 |
|------|----------|------|------|
| `update_pipeline_status()` | `storage/state_manager.py` | 171 | 状态更新时 |
| `start_pipeline()` | `pipeline/orchestrator.py` | 449, 498 | 启动/完成时 |
| `restart_from_node()` | `pipeline/orchestrator.py` | 721 | 重启节点时 |
| `cancel_current_node()` | `pipeline/orchestrator.py` | 1044 | 取消时 |

**代码示例**:

```python
# storage/state_manager.py:167-174
if current_node is not None:
    _ = conn.execute(
        "UPDATE pipelines SET status = ?, current_node = ?, "
        + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
        (status, current_node, pipeline_id),
    )
# 注意：此处仅更新顶层字段，不更新 state_json
```

#### 2.1.2 写入 state_json（正确）

| 操作 | 文件位置 | 行号 | 场景 |
|------|----------|------|------|
| `create_pipeline()` | `storage/state_manager.py` | 118-127 | 创建 pipeline |
| `node_executor` | `pipeline/graph.py` | 103 | 节点执行 |
| `integrated_executor` | `pipeline/graph.py` | 354 | 集成执行器 |

**代码示例**:

```python
# pipeline/graph.py:102-103
# Update current_node
new_state["current_node"] = node_id
```

### 2.2 双重来源读操作

#### 2.2.1 仅从顶层读取（风险）

```python
# cli/commands/status.py:41-45
pipeline_state = pipeline.get("state", {})
current_node = pipeline.get("current_node", "")  # 从顶层读取
completed_nodes = pipeline_state.get("completed_nodes", [])  # 从 state_json 读取
```

**问题分析**:
- `current_node` 从顶层读取
- `completed_nodes` 从 `state_json` 读取
- 两者可能不一致，导致 UI 显示错误

#### 2.2.2 仅从 state_json 读取（部分正确）

```python
# pipeline/orchestrator.py:685-694
# Get the current checkpoint state
checkpoint_state = pipeline.get("state", {})
subject_context = checkpoint_state.get("subject_context", {})
completed_nodes = checkpoint_state.get("completed_nodes", [])
```

**问题分析**:
- `restart_from_node()` 正确地从 `state_json` 读取状态
- 但 `current_node` 仍从顶层写入，可能不一致

### 2.3 最危险的操作：`get_pipeline()`

```python
# storage/state_manager.py:253-319
def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
    # ... 查询 ...
    return {
        "pipeline_id": row["pipeline_id"],
        "subject": row["subject"],
        "status": row["status"],                    # 顶层 status
        "current_node": row["current_node"],        # 顶层 current_node
        "state": json.loads(row["state_json"]),     # state_json 解析
        # ...
    }
```

**问题**:
- 同时返回 `current_node`（顶层）和 `state.current_node`
- 调用者可能使用错误的来源

---

## 3. 状态读写路径矩阵

### 3.1 current_node 访问矩阵

| 操作 | 读来源 | 写目标 | 风险等级 |
|------|--------|--------|----------|
| `update_pipeline_status` | - | TOP | **HIGH** |
| `start_pipeline` | - | TOP | **HIGH** |
| `restart_from_node` | JSON | TOP+JSON | **CRITICAL** |
| `cancel_current_node` | JSON | TOP | **CRITICAL** |
| `get_pipeline` | BOTH | - | **CRITICAL** |
| `get_pipeline_status` | TOP | - | **HIGH** |
| `status_command` | BOTH | - | **CRITICAL** |
| `node_executor` | - | JSON | LOW |
| `resume_pipeline` | JSON | - | LOW |

### 3.2 风险场景分析

#### 场景1：恢复路径不一致（restart_from_node）

```
1. Pipeline 运行到 pm 节点时失败
2. state_json.current_node = "pm" (通过 graph.py 写入)
3. 顶层 current_node = "pm" (通过 orchestrator 写入)

4. 用户调用 restart_from_node("analyst")
5. orchestrator 从 state_json 读取状态（正确）
6. orchestrator 写入顶层 current_node="analyst"（危险）
7. 但 state_json 内的 current_node 仍是 "pm"

结果：
- 顶层: current_node = "analyst"
- state_json: current_node = "pm"
- status 命令显示 "analyst"，但实际逻辑可能使用 "pm"
```

#### 场景2：取消操作数据丢失

```
1. Pipeline 运行中，current_node="ux"
2. 用户调用 cancel_current_node()
3. 方法从 state_json 读取 current_node（正确）
4. 方法写入顶层 current_node="ux"（冗余）
5. state_json 内的状态未更新为 cancelled

结果：
- 取消操作仅更新了顶层 status
- state_json 仍保留 "running" 状态
- 恢复时可能读取到错误状态
```

---

## 4. 统一设计方案

### 4.1 方案A：state_json 作为唯一真相源（推荐）

**核心原则**: 删除冗余顶层字段，所有状态信息只通过 `state_json` 存储。

#### 4.1.1 数据库变更

```sql
-- 迁移脚本：删除冗余字段
ALTER TABLE pipelines DROP COLUMN current_node;
-- status 可以保留作为查询索引，但不作为业务逻辑来源
CREATE INDEX idx_pipeline_status ON pipelines(status);
```

#### 4.1.2 API 变更

```python
# storage/state_manager.py
# 新方法：统一通过 state_json 更新
def update_pipeline_state(
    self,
    pipeline_id: str,
    state_update: dict[str, Any],
) -> bool:
    """Update complete PipelineState in state_json.
    
    This is the ONLY way to update pipeline state.
    All state changes must go through this method.
    """
    # 实现深度合并并写入 state_json
    # 不再提供 update_pipeline_status() 方法

# 查询时只返回解析后的 state
def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
    row = ...
    state = json.loads(row["state_json"])
    return {
        "pipeline_id": row["pipeline_id"],
        "subject": row["subject"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        **state,  # 展开所有状态字段
    }
```

#### 4.1.3 优势

| 优势 | 说明 |
|------|------|
| 数据一致性 | 单一写入点，消除不一致风险 |
| 代码简化 | 删除所有双重来源逻辑 |
| 扩展性 | 新增状态字段只需修改 PipelineState |
| 可测试性 | 状态逻辑集中，易于测试 |

#### 4.1.4 实施步骤

```
Phase 1: 准备（1个迭代）
1. 创建新的 update_pipeline_state() 方法
2. 标记 update_pipeline_status() 为 deprecated
3. 添加运行时一致性检查（发现不一致时告警）

Phase 2: 迁移（1个迭代）
1. 将所有写操作迁移到 update_pipeline_state()
2. 更新所有读操作，统一从 state_json 读取
3. 数据迁移：修复现有的不一致数据

Phase 3: 清理（1个迭代）
1. 删除 pipelines.current_node 列
2. 删除 update_pipeline_status() 方法
3. 更新所有调用点
```

### 4.2 方案B：顶层字段作为查询优化

**核心原则**: 保留顶层字段作为索引/缓存，但业务逻辑只使用 `state_json`。

#### 4.2.1 一致性保证

```python
# 使用数据库触发器或应用层逻辑保持同步

# 应用层实现示例
def update_pipeline_state(self, pipeline_id: str, state_update: dict[str, Any]) -> bool:
    # 1. 先更新 state_json
    state = self._get_state_json(pipeline_id)
    deep_merge(state, state_update)
    
    # 2. 同步更新顶层字段（仅作为缓存）
    top_level_status = state.get("status")
    top_level_current_node = state.get("current_node")
    
    self._update_top_level(pipeline_id, top_level_status, top_level_current_node)
    self._update_state_json(pipeline_id, state)
    
    # 3. 确保原子性
```

#### 4.2.2 优势与劣势

| 方面 | 说明 |
|------|------|
| 优势 | 保留顶层字段的查询性能优势 |
| 劣势 | 增加复杂度，需要维护同步逻辑 |
| 风险 | 同步逻辑bug会导致不一致 |

### 4.3 方案对比

| 维度 | 方案A（推荐） | 方案B |
|------|--------------|-------|
| 实现复杂度 | 低 | 中 |
| 数据一致性 | 强 | 中（依赖同步逻辑） |
| 查询性能 | 可接受（可添加JSON索引） | 优 |
| 维护成本 | 低 | 高 |
| 迁移成本 | 中 | 低 |

---

## 5. 修复建议

### 5.1 立即行动（P0）

#### 5.1.1 添加一致性检查

```python
# 在关键操作前添加检查
def _verify_state_consistency(self, pipeline_id: str) -> None:
    """运行时一致性检查，发现不一致时告警"""
    pipeline = self._get_raw_pipeline(pipeline_id)
    if not pipeline:
        return
    
    top_current_node = pipeline["current_node"]
    state = json.loads(pipeline["state_json"] or "{}")
    state_current_node = state.get("current_node")
    
    if top_current_node != state_current_node:
        logger.warning(
            "state_inconsistency_detected",
            pipeline_id=pipeline_id,
            top_current_node=top_current_node,
            state_current_node=state_current_node,
            operation="consistency_check"
        )
```

#### 5.1.2 修复高危操作

```python
# storage/state_manager.py
# 修改 update_pipeline_status 方法，同步更新 state_json

def update_pipeline_status(
    self,
    pipeline_id: str,
    status: str,
    current_node: str | None = None,
) -> bool:
    """Update pipeline status and optionally current node.
    
    DEPRECATED: This method updates top-level fields only.
    Use update_pipeline_state() for new code.
    """
    # 1. 更新顶层字段（保持兼容）
    self._update_top_level(pipeline_id, status, current_node)
    
    # 2. 同步更新 state_json（新增）
    state_update = {"status": status}
    if current_node is not None:
        state_update["current_node"] = current_node
    self._update_state_json_partial(pipeline_id, state_update)
    
    return True
```

### 5.2 短期行动（P1）

#### 5.2.1 统一状态读取

```python
# cli/commands/status.py
# 修改前
pipeline_state = pipeline.get("state", {})
current_node = pipeline.get("current_node", "")  # 从顶层

# 修改后
pipeline_state = pipeline.get("state", {})
current_node = pipeline_state.get("current_node", "")  # 从 state_json
```

#### 5.2.2 建立状态访问规范

```python
# 新的状态访问模块
# storage/state_access.py

class PipelineStateAccess:
    """统一的状态访问接口，封装所有状态读写逻辑"""
    
    @staticmethod
    def get_current_node(pipeline: dict[str, Any]) -> str | None:
        """统一从 state_json 获取 current_node"""
        state = pipeline.get("state", {})
        return state.get("current_node")
    
    @staticmethod
    def get_status(pipeline: dict[str, Any]) -> str:
        """统一从 state_json 获取 status"""
        state = pipeline.get("state", {})
        return state.get("status", "unknown")
```

### 5.3 长期行动（P2）

1. **数据库迁移**：删除 `pipelines.current_node` 列
2. **代码清理**：删除 `update_pipeline_status()` 等旧方法
3. **测试覆盖**：添加状态一致性集成测试
4. **文档更新**：更新架构文档，明确状态管理规范

---

## 6. 测试策略

### 6.1 一致性测试

```python
# tests/storage/test_state_consistency.py

async def test_state_json_single_source_of_truth():
    """验证 state_json 是唯一的真相源"""
    sm = StateManager(db_path=temp_db)
    
    # 创建 pipeline
    pipeline_id = sm.create_pipeline(subject="Test")
    
    # 模拟节点执行
    await sm.update_pipeline_state(pipeline_id, {
        "current_node": "analyst",
        "status": "running"
    })
    
    # 验证：无论从哪个方法读取，结果应该一致
    pipeline = sm.get_pipeline(pipeline_id)
    
    # 所有 current_node 应该来自 state_json
    assert pipeline["state"]["current_node"] == "analyst"
    
    # 验证：顶层字段（如果存在）应该与 state_json 一致
    if "current_node" in pipeline:
        assert pipeline["current_node"] == pipeline["state"]["current_node"]
```

### 6.2 并发测试

```python
async def test_concurrent_state_updates():
    """测试并发状态更新的正确性"""
    # 模拟多个节点同时更新的场景
    # 验证最终一致性
```

---

## 7. 结论

### 7.1 核心问题

F2 问题的本质是**架构演进过程中的过渡态**：

1. **设计意图明确**：`state_json` 应该作为单一真相源
2. **实现未完全收敛**：顶层字段仍在承担业务逻辑责任
3. **读写路径混乱**：不同操作使用不同的数据来源

### 7.2 风险评估

| 风险场景 | 发生概率 | 影响程度 | 紧急度 |
|----------|----------|----------|--------|
| 恢复路径使用错误的 current_node | 中 | 高 | P0 |
| 状态显示不一致 | 高 | 中 | P1 |
| 取消操作后状态丢失 | 低 | 中 | P1 |
| 并发更新导致数据损坏 | 低 | 高 | P1 |

### 7.3 推荐方案

**采用方案A（state_json 作为唯一真相源）**，理由：

1. 符合原始设计意图
2. 彻底消除不一致风险
3. 长期维护成本最低
4. 与 LangGraph/SqliteSaver 架构更契合

### 7.4 实施路线图

```
迭代1（止血）：添加一致性检查，修复高危操作
迭代2（迁移）：统一所有读操作到 state_json
迭代3（清理）：删除顶层字段，完成收口
```

---

## 附录

### A. 调试工具使用

```bash
# 运行一致性分析
python tools/f2_state_consistency_analyzer.py --db docuswarm.db

# 生成完整报告
python tools/f2_state_consistency_analyzer.py --generate-report

# 输出 JSON 格式（用于自动化）
python tools/f2_state_consistency_analyzer.py --json > f2_report.json
```

### B. 相关文件清单

| 文件 | 责任 | 修改优先级 |
|------|------|-----------|
| `storage/state_manager.py` | 核心状态管理 | P0 |
| `pipeline/orchestrator.py` | 编排逻辑 | P0 |
| `cli/commands/status.py` | 状态显示 | P1 |
| `pipeline/graph.py` | 节点执行 | P1 |
| `storage/database.py` | Schema | P2 |

### C. 参考文档

- [评估报告原文](../evaluation/2026-03-25-docuswarm-deep-evaluation-report.md)
- [Pipeline State 定义](../../autoBMAD/docuswarm/pipeline/state.py)
- [StateManager 实现](../../autoBMAD/docuswarm/storage/state_manager.py)

# F1: 状态持久化与恢复链路闭环深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm 状态管理机制
> 核心问题: state_json 与 LangGraph checkpoint 双重真相源问题

---

## 1. 执行摘要

### 1.1 核心发现

当前系统存在**双重真相源**问题：`state_json`（数据库）和 `LangGraph checkpoint`（框架内部）同时承载业务状态，导致：

1. **真相源不一致**: state_json 只存储了 `subject_context` 的基础字段，而 checkpoint 包含了完整的 PipelineState
2. **恢复逻辑依赖框架**: resume/restart 操作依赖 checkpoint_state，而非自有的 state_json
3. **运维困难**: 数据库中的 state_json 无法直接用于业务审计和状态诊断

### 1.2 关键代码证据

```python
# autoBMAD/docuswarm/storage/state_manager.py:116
state_json = json.dumps(subject_context or {})  # 只存储了基础上下文

# autoBMAD/docuswarm/storage/state_manager.py:311
"state": json.loads(cast(str, row["state_json"])) if row["state_json"] else {},

# autoBMAD/docuswarm/pipeline/orchestrator.py:550
checkpoint_state = pipeline.get("state", {})  # 恢复时优先读取 checkpoint
```

---

## 2. 详细分析

### 2.1 数据库存储现状

#### 2.1.1 当前 state_json 结构

```json
{
  "subject": "项目名称",
  "context_file": "上下文文件路径",
  "content": "上下文内容"
}
```

**问题**: 这只是 `subject_context` 的子集，不是完整的 `PipelineState`。

#### 2.1.2 PipelineState 完整字段

```python
class PipelineState(TypedDict):
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]
    questions: dict[str, list[dict[str, Any]]]
    evaluations: dict[str, dict[str, Any]]
    node_iterations: dict[str, int]
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None
    status: str
    error: dict[str, Any] | None
    shared_context: dict[str, Any]
```

#### 2.1.3 Checkpoint 数据结构

从数据库采样观察，checkpoint channel 包含以下键：
- `pipeline_id`, `subject_context`, `current_node`
- `completed_nodes`, `deliverables`, `questions`
- `evaluations`, `node_iterations`, `session_ids`
- `session_metadata`, `current_node_session_id`, `status`, `error`, `__finalize__`

**结论**: checkpoint 比 state_json 更完整，这是问题的核心。

### 2.2 恢复链路分析

#### 2.2.1 Resume 流程

```python
# orchestrator.py:517-647 resume_pipeline 方法
checkpoint_state = pipeline.get("state", {})  # 从 state_json 获取
last_node = checkpoint_state.get("current_node")
session_id = checkpoint_state.get("current_node_session_id")

# 恢复时重建 initial_state
initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])
initial_state["deliverables"] = checkpoint_state.get("deliverables", {})
initial_state["session_ids"] = checkpoint_state.get("session_ids", {})
```

**问题**: 恢复逻辑依赖 `pipeline.get("state")`，而这来自不完整存储的 state_json。

#### 2.2.2 Restart 流程

```python
# orchestrator.py:649-788 restart_from_node 方法
completed_nodes: list[str] = checkpoint_state.get("completed_nodes", [])
deliverables: dict[str, Any] = checkpoint_state.get("deliverables", {})
# ... 其他字段同样来自 checkpoint_state
```

### 2.3 决策矩阵对比

| 维度 | state_json (当前) | LangGraph checkpoint |
|------|-------------------|---------------------|
| 业务真相 | 低 - 字段不完整 | 中 - 框架恢复态 |
| 稳定性 | 高 - 自控制 | 中低 - 依赖框架格式 |
| 可运维性 | 高 - 易查询 | 低 - BLOB/msgpack |
| 与框架耦合 | 低 | 高 |
| 当前状态 | 不完整 | 最完整 |

---

## 3. 收敛方案

### 3.1 奥卡姆剃刀决策

**原则**: 选择更简单、更直接的方案作为业务真相源。

**决策**: 
- `state_json` 成为唯一业务真相源
- `checkpoint` 降级为运行期恢复快照

**理由**:
1. 固定五节点顺序流水线的业务语义，明显比 LangGraph 内部 channel 语义更简单
2. 维护双重一致性会增加持续复杂度
3. state_json 更易审计、查询、做运维界面

### 3.2 具体收敛动作

#### 3.2.1 修改 StateManager.create_pipeline

```python
# 当前问题: 只存储 subject_context
def create_pipeline(self, subject: str, subject_context: dict | None = None) -> str:
    state_json = json.dumps(subject_context or {})  # ❌ 不完整
    
# 目标: 存储完整的 PipelineState
def create_pipeline(self, subject: str, subject_context: dict | None = None) -> str:
    from autoBMAD.docuswarm.pipeline.state import create_initial_state
    initial_state = create_initial_state(pipeline_id, subject_context or {})
    state_json = json.dumps(initial_state)  # ✅ 完整状态
```

#### 3.2.2 新增 StateManager.update_pipeline_state

```python
async def update_pipeline_state(
    self,
    pipeline_id: str,
    state_update: dict[str, Any],
) -> bool:
    """更新完整的 PipelineState 到 state_json."""
    # 读取当前 state_json
    current_state = self._get_pipeline_state_json(pipeline_id)
    
    # 深度合并更新
    merged_state = {**current_state, **state_update}
    
    # 写回数据库
    return self._save_pipeline_state_json(pipeline_id, merged_state)
```

#### 3.2.3 修改恢复逻辑

```python
# orchestrator.py resume_pipeline
# 当前: 从 checkpoint_state 恢复
# 目标: 从 state_json 恢复，checkpoint 作为备份

async def resume_pipeline(self, pipeline_id: str) -> dict[str, Any]:
    # 1. 优先从 state_json 读取业务真相
    pipeline = self._state_manager.get_pipeline(pipeline_id)
    business_state = pipeline.get("state", {})
    
    # 2. checkpoint 作为运行时恢复机制
    # 如果 state_json 和 checkpoint 冲突，以 state_json 为准
    
    # 3. 恢复时能够依据 state_json 重建 PipelineState
    initial_state = create_initial_state(pipeline_id, business_state.get("subject_context", {}))
    initial_state.update(business_state)  # 合并完整状态
```

### 3.3 状态写入时序图

```
Pipeline Execution:
    
    1. create_pipeline()
       ├── 创建 PipelineState (完整)
       ├── state_json = dump(PipelineState)  → 写入 DB
       └── checkpoint (LangGraph 自动)
    
    2. Node Execution (per node)
       ├── 节点执行
       ├── update_pipeline_state()  → 更新 state_json
       └── checkpoint (LangGraph 自动)
    
    3. resume/restart
       ├── 读取 state_json (业务真相源)
       ├── 可选: 对比 checkpoint 一致性检查
       └── 重建 PipelineState
```

---

## 4. 测试建议

### 4.1 契约测试

```python
async def test_state_json_is_complete_source():
    """验证 state_json 包含完整的 PipelineState."""
    # 创建 pipeline
    pipeline_id = state_manager.create_pipeline(subject="test")
    
    # 模拟节点执行更新
    await state_manager.update_pipeline_state(pipeline_id, {
        "current_node": "analyst",
        "completed_nodes": ["analyst"],
        "deliverables": {"analyst": {...}},
        "shared_context": {"facts": {"key": "value"}},
    })
    
    # 验证 state_json 完整性
    pipeline = state_manager.get_pipeline(pipeline_id)
    state = pipeline["state"]
    
    required_fields = [
        "pipeline_id", "subject_context", "current_node",
        "completed_nodes", "deliverables", "shared_context"
    ]
    for field in required_fields:
        assert field in state, f"Missing field: {field}"
```

### 4.2 恢复测试

```python
async def test_resume_from_state_json():
    """验证可以从 state_json 恢复执行."""
    # 创建并执行部分 pipeline
    pipeline_id = await orchestrator.start_pipeline(subject_context)
    
    # 模拟中断
    state_manager.update_pipeline_status(pipeline_id, status="paused")
    
    # resume
    result = await orchestrator.resume_pipeline(pipeline_id)
    
    # 验证状态一致性
    pipeline = state_manager.get_pipeline(pipeline_id)
    assert pipeline["state"]["status"] == "completed"
```

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| state_json 写入失败 | 高 | 使用事务，失败时回滚并标记 pipeline 失败 |
| checkpoint 与 state_json 不一致 | 中 | 添加一致性检查，日志告警 |
| 性能问题（频繁序列化） | 低 | 批量更新，减少写入频率 |
| 迁移成本 | 中 | 分阶段迁移，保留 checkpoint 作为备份 |

---

## 6. 结论

1. **state_json 必须成为唯一业务真相源**，这是简化架构的必然选择
2. **checkpoint 降级为运行时辅助机制**，不作为业务决策依据
3. **收敛动作需分阶段执行**：先补齐 state_json 写入，再调整恢复逻辑
4. **测试体系需要优先补齐**状态持久化和恢复的契约测试

---

## 附录: 代码修改清单

### A.1 StateManager 修改

- [ ] `create_pipeline()`: 写入完整 PipelineState
- [ ] 新增 `update_pipeline_state()`: 更新完整状态
- [ ] `get_pipeline()`: 确保返回完整状态

### A.2 Orchestrator 修改

- [ ] `start_pipeline()`: 启动时同步写入完整状态
- [ ] `resume_pipeline()`: 优先从 state_json 恢复
- [ ] `restart_from_node()`: 优先从 state_json 恢复
- [ ] `_restart_node()`: 优先从 state_json 恢复

### A.3 新增工具

- [ ] 状态一致性检查工具
- [ ] state_json 完整性验证工具

---

## 相关文档 (2026-03-18 更新)

### TD-1 技术债务关联

本研究报告与 **TD-1: current_node 与运行状态存在重复表示** 直接相关：

| 文档 | 说明 |
|------|------|
| [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md) | TD-1 问题定义与评估 |
| [技术债务深度研究报告](2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md) | TD-1 深度分析与方案 |
| [P0/P1 TDD 主方案](../solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md) | TD-1 测试驱动实施方案 |

**TD-1 核心问题**: `current_node` 同时存在于 `pipelines` 表顶层列和 `state_json` 内部，形成重复表示。

**收敛方案**: 
- `state_json` 成为唯一业务真相源
- `pipelines.current_node` 降级为派生字段（查询优化）
- 恢复逻辑优先从 `state_json` 读取

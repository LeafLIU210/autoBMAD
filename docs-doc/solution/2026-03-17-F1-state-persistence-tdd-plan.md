# F1: 状态持久化与恢复链路闭环 TDD 执行方案

> 研究日期: 2026-03-17
> 目标: 解决 state_json 与 LangGraph checkpoint 双重真相源问题
> 交付物: 完整的状态持久化测试覆盖 + 恢复链路闭环实现

---

## 1. 验收标准

### 1.1 必须满足的条件

- [ ] `state_json` 包含完整的 `PipelineState` 字段，成为唯一业务真相源
- [ ] `checkpoint` 降级为运行期恢复快照，不作为业务决策依据
- [ ] 恢复操作（resume/restart）优先从 `state_json` 读取业务状态
- [ ] 所有状态操作都有对应的契约测试覆盖
- [ ] 恢复链路有完整的集成测试覆盖

### 1.2 完成信号

```
<promise>DONE</promise>
```

---

## 2. 测试覆盖矩阵

| 测试类型 | 目标文件 | 测试数量 | 优先级 |
|---------|---------|---------|--------|
| 契约测试 | `test_state_manager_state_persistence.py` | 8 | P0 |
| 恢复测试 | `test_orchestrator_resume_recovery.py` | 6 | P0 |
| 集成测试 | `test_state_persistence_e2e.py` | 4 | P1 |
| 工具测试 | `test_state_consistency_tools.py` | 3 | P1 |

---

## 3. 测试实现清单

### 3.1 契约测试 - StateManager 状态持久化

**文件**: `tests/storage/test_state_manager_state_persistence.py`

```python
# 测试用例 1: create_pipeline 写入完整 PipelineState
test_create_pipeline_stores_complete_pipeline_state()

# 测试用例 2: update_pipeline_state 更新完整状态
test_update_pipeline_state_updates_complete_state()

# 测试用例 3: get_pipeline 返回完整状态
test_get_pipeline_returns_complete_state()

# 测试用例 4: state_json 包含所有必需字段
test_state_json_contains_all_required_fields()

# 测试用例 5: shared_context 正确持久化
test_shared_context_persistence()

# 测试用例 6: session_metadata 正确持久化
test_session_metadata_persistence()

# 测试用例 7: node_iterations 正确持久化
test_node_iterations_persistence()

# 测试用例 8: 并发状态更新正确处理
test_concurrent_state_updates_handled_correctly()
```

**关键断言**:
```python
required_fields = [
    "pipeline_id", "subject_context", "current_node",
    "completed_nodes", "deliverables", "questions",
    "evaluations", "node_iterations", "session_ids",
    "session_metadata", "current_node_session_id",
    "status", "error", "shared_context"
]
```

### 3.2 恢复测试 - Orchestrator 恢复链路

**文件**: `tests/pipeline/test_orchestrator_resume_recovery.py`

```python
# 测试用例 1: resume_pipeline 优先从 state_json 恢复
test_resume_pipeline_prioritizes_state_json()

# 测试用例 2: restart_from_node 优先从 state_json 恢复
test_restart_from_node_prioritizes_state_json()

# 测试用例 3: 状态恢复包含所有必需字段
test_state_recovery_includes_all_required_fields()

# 测试用例 4: 中断后恢复保持状态一致性
test_resume_maintains_state_consistency_after_interruption()

# 测试用例 5: 从任意节点重启清除后续节点状态
test_restart_from_node_clears_subsequent_state()

# 测试用例 6: checkpoint 与 state_json 冲突时以 state_json 为准
test_state_json_takes_precedence_over_checkpoint()
```

### 3.3 集成测试 - 端到端状态持久化

**文件**: `tests/integration/test_state_persistence_e2e.py`

```python
# 测试用例 1: 完整 pipeline 执行后状态正确持久化
test_full_pipeline_execution_persists_state_correctly()

# 测试用例 2: 中断-resume 循环后状态完整
test_interruption_resume_cycle_preserves_state()

# 测试用例 3: 多次重启后状态一致性
test_multiple_restarts_maintain_state_consistency()

# 测试用例 4: 状态可在数据库中查询验证
test_state_queryable_in_database()
```

### 3.4 工具测试 - 状态一致性检查

**文件**: `tests/tools/test_state_consistency_tools.py`

```python
# 测试用例 1: 状态完整性验证工具
test_state_integrity_validation_tool()

# 测试用例 2: checkpoint 与 state_json 一致性检查
test_checkpoint_state_json_consistency_check()

# 测试用例 3: 状态修复工具
test_state_repair_tool()
```

---

## 4. 实现步骤

### 步骤 1: 创建测试基础设施

```bash
# 创建测试目录
mkdir -p tests/storage tests/pipeline tests/integration tests/tools

# 创建 __init__.py 文件
touch tests/storage/__init__.py
touch tests/pipeline/__init__.py
touch tests/integration/__init__.py
touch tests/tools/__init__.py
```

### 步骤 2: 实现 StateManager 修改

**修改文件**: `autoBMAD/docuswarm/storage/state_manager.py`

1. **修改 `create_pipeline`** - 写入完整 PipelineState
2. **新增 `update_pipeline_state`** - 更新完整状态
3. **验证 `get_pipeline`** - 确保返回完整状态

### 步骤 3: 实现 Orchestrator 修改

**修改文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

1. **修改 `start_pipeline`** - 启动时同步写入完整状态
2. **修改 `resume_pipeline`** - 优先从 state_json 恢复
3. **修改 `restart_from_node`** - 优先从 state_json 恢复

### 步骤 4: 运行并修复测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python -m pytest tests/storage/test_state_manager_state_persistence.py -v
python -m pytest tests/pipeline/test_orchestrator_resume_recovery.py -v
python -m pytest tests/integration/test_state_persistence_e2e.py -v
python -m pytest tests/tools/test_state_consistency_tools.py -v
```

---

## 5. 预期修改的源码文件

| 文件 | 修改类型 | 修改内容 |
|------|---------|---------|
| `autoBMAD/docuswarm/storage/state_manager.py` | 修改+新增 | `create_pipeline` 写入完整状态，新增 `update_pipeline_state` |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | 修改 | resume/restart 优先从 state_json 恢复 |
| `autoBMAD/docuswarm/pipeline/state.py` | 验证 | 确保 `create_initial_state` 创建完整状态 |

---

## 6. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 测试发现现有代码严重问题 | 高 | 分阶段修复，先修复阻塞性问题 |
| 状态序列化性能问题 | 中 | 添加性能基准测试 |
| 并发状态更新冲突 | 中 | 添加事务测试 |
| 与现有 checkpoint 机制冲突 | 高 | 保持 checkpoint 作为备份，逐步迁移 |

---

## 7. 成功标准检查清单

- [ ] 所有契约测试通过
- [ ] 所有恢复测试通过
- [ ] 所有集成测试通过
- [ ] 测试覆盖率达到 80%+
- [ ] 无状态丢失风险
- [ ] 恢复链路闭环完成

**输出信号**: `<promise>DONE</promise>`

# F1: 状态持久化与恢复链路闭环 - 测试驱动方案

> 基于研究报告: `docs/research/2026-03-17-F1-state-persistence-research-report.md`
> 创建日期: 2026-03-18

---

## 1. 方案概述

### 1.1 核心目标

解决 `state_json` 与 `LangGraph checkpoint` 双重真相源问题，确立 `state_json` 为唯一业务真相源。

### 1.2 验收标准

1. **StateManager 修改完成**
   - [x] `create_pipeline()` 写入完整 PipelineState
   - [x] 新增 `update_pipeline_state()` 更新完整状态
   - [x] `get_pipeline()` 确保返回完整状态

2. **Orchestrator 修改完成**
   - [x] `start_pipeline()` 启动时同步写入完整状态
   - [x] `resume_pipeline()` 优先从 state_json 恢复
   - [x] `restart_from_node()` 优先从 state_json 恢复
   - [x] `_restart_node()` 优先从 state_json 恢复

3. **测试验证通过**
   - [x] 所有 StateManager 状态持久化测试通过 (12/12)
   - [x] 所有 Orchestrator 恢复测试通过 (10/10)
   - [x] 所有集成测试通过 (6/6)
   - [x] 所有工具测试通过 (7/7)

---

## 2. 测试清单

### 2.1 StateManager 测试 (`tests/storage/test_state_manager_state_persistence.py`)

| 测试类 | 测试方法 | 目的 | 状态 |
|--------|----------|------|------|
| `TestCreatePipelineStateStorage` | `test_create_pipeline_stores_complete_pipeline_state` | 验证 create_pipeline 存储完整状态 | ✅ 通过 |
| `TestCreatePipelineStateStorage` | `test_create_pipeline_with_empty_context` | 验证空上下文处理 | ✅ 通过 |
| `TestUpdatePipelineState` | `test_update_pipeline_state_updates_complete_state` | 验证 update_pipeline_state 更新完整状态 | ✅ 通过 |
| `TestUpdatePipelineState` | `test_update_pipeline_state_nonexistent_pipeline` | 验证不存在 pipeline 的错误处理 | ✅ 通过 |
| `TestUpdatePipelineState` | `test_update_pipeline_state_partial_update` | 验证部分更新正确合并 | ✅ 通过 |
| `TestStateJsonCompleteness` | `test_state_json_contains_all_required_fields` | 验证所有必需字段存在 | ✅ 通过 |
| `TestSharedContextPersistence` | `test_shared_context_persistence` | 验证 shared_context 持久化 | ✅ 通过 |
| `TestSharedContextPersistence` | `test_shared_context_append_operation` | 验证 append 操作 | ✅ 通过 |
| `TestSessionMetadataPersistence` | `test_session_metadata_persistence` | 验证 session_metadata 持久化 | ✅ 通过 |
| `TestNodeIterationsPersistence` | `test_node_iterations_persistence` | 验证 node_iterations 持久化 | ✅ 通过 |
| `TestConcurrentStateUpdates` | `test_concurrent_state_updates_handled_correctly` | 验证并发更新处理 | ✅ 通过 |
| `TestStateConsistency` | `test_state_consistency_after_multiple_operations` | 验证多操作后状态一致性 | ✅ 通过 |

### 2.2 Orchestrator 恢复测试 (`tests/pipeline/test_orchestrator_resume_recovery.py`)

| 测试类 | 测试方法 | 目的 | 状态 |
|--------|----------|------|------|
| `TestResumePipelinePrioritizesStateJson` | `test_resume_pipeline_reads_from_state_json` | 验证 resume 从 state_json 读取 | ✅ 通过 |
| `TestResumePipelinePrioritizesStateJson` | `test_resume_pipeline_requires_complete_state` | 验证 resume 需要完整状态 | ✅ 通过 |
| `TestRestartFromNodePrioritizesStateJson` | `test_restart_from_node_reads_from_state_json` | 验证 restart 从 state_json 读取 | ✅ 通过 |
| `TestRestartFromNodePrioritizesStateJson` | `test_restart_from_node_clears_subsequent_state` | 验证 restart 清除后续节点状态 | ✅ 通过 |
| `TestStateRecoveryCompleteness` | `test_state_recovery_includes_all_required_fields` | 验证恢复状态包含所有字段 | ✅ 通过 |
| `TestStateJsonTakesPrecedence` | `test_state_json_takes_precedence_over_checkpoint` | 验证 state_json 优先级 | ✅ 通过 |
| `TestResumeMaintainsStateConsistency` | `test_resume_maintains_state_consistency_after_interruption` | 验证中断后恢复状态一致性 | ✅ 通过 |
| `TestErrorHandling` | `test_resume_nonexistent_pipeline_raises_error` | 验证 resume 不存在 pipeline 错误 | ✅ 通过 |
| `TestErrorHandling` | `test_resume_completed_pipeline_raises_error` | 验证 resume 已完成 pipeline 错误 | ✅ 通过 |
| `TestErrorHandling` | `test_restart_from_invalid_node_raises_error` | 验证 restart 无效节点错误 | ✅ 通过 |

### 2.3 集成测试 (`tests/integration/test_state_persistence_e2e.py`)

| 测试类 | 测试方法 | 目的 | 状态 |
|--------|----------|------|------|
| `TestFullPipelineExecution` | `test_full_pipeline_execution_persists_state_correctly` | 验证完整流程状态持久化 | ✅ 通过 |
| `TestInterruptionResumeCycle` | `test_interruption_resume_cycle_preserves_state` | 验证中断-恢复周期状态保持 | ✅ 通过 |
| `TestMultipleRestarts` | `test_multiple_restarts_maintain_state_consistency` | 验证多次重启状态一致性 | ✅ 通过 |
| `TestStateQueryableInDatabase` | `test_state_queryable_in_database` | 验证数据库可直接查询状态 | ✅ 通过 |
| `TestStateQueryableInDatabase` | `test_state_json_queryable_by_content` | 验证按内容查询 state_json | ✅ 通过 |
| `TestStateIntegrity` | `test_state_integrity_after_many_updates` | 验证多次更新后状态完整性 | ✅ 通过 |

### 2.4 工具测试 (`tests/tools/test_state_consistency_tools.py`)

| 测试类 | 测试方法 | 目的 | 状态 |
|--------|----------|------|------|
| `TestStateIntegrityValidation` | `test_validate_complete_state_passes` | 验证完整状态通过校验 | ✅ 通过 |
| `TestStateIntegrityValidation` | `test_validate_incomplete_state_fails` | 验证不完整状态失败 | ✅ 通过 |
| `TestStateIntegrityValidation` | `test_validate_state_types` | 验证状态字段类型 | ✅ 通过 |
| `TestStateJsonCompletenessCheck` | `test_state_json_has_all_pipeline_state_fields` | 验证 state_json 包含所有字段 | ✅ 通过 |
| `TestStateJsonCompletenessCheck` | `test_state_json_serialization_roundtrip` | 验证序列化往返 | ✅ 通过 |
| `TestStateConsistencyBetweenSources` | `test_state_json_matches_get_pipeline` | 验证 state_json 与 get_pipeline 一致 | ✅ 通过 |
| `TestStateConsistencyBetweenSources` | `test_state_json_independent_of_node_results` | 验证 state_json 独立于 node_results | ✅ 通过 |

---

## 3. 源代码修改清单

### 3.1 StateManager (已完成)

```python
# autoBMAD/docuswarm/storage/state_manager.py

# ✅ 已完成: create_pipeline 写入完整 PipelineState
# 第115-120行: 使用 create_initial_state 创建完整状态

# ✅ 已完成: 新增 update_pipeline_state 方法
# 第640-708行: 完整的 update_pipeline_state 实现

# ✅ 已完成: _deep_merge 辅助方法
# 第710-721行: 深度合并实现
```

### 3.2 Orchestrator (已完成)

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py

# ✅ 已完成: start_pipeline 同步更新 state_json
# 实现: 通过 StateManager.create_pipeline 写入完整初始状态

# ✅ 已完成: resume_pipeline 从 state_json 恢复
# 第550行: checkpoint_state = pipeline.get("state", {})
# 验证: 数据来自 state_json，包含完整 PipelineState 字段

# ✅ 已完成: restart_from_node 从 state_json 恢复
# 第686行: checkpoint_state = pipeline.get("state", {})
# 验证: 数据来自 state_json，包含完整 PipelineState 字段

# ✅ 已完成: _restart_node 从 state_json 恢复
# 第892-893行: 从 checkpoint_state 获取
# 验证: 数据来源于 state_json
```

---

## 4. 执行步骤与结果

### 步骤 1: 运行所有现有测试 ✅

```bash
python -m pytest tests/storage/test_state_manager_state_persistence.py -v
python -m pytest tests/pipeline/test_orchestrator_resume_recovery.py -v
python -m pytest tests/integration/test_state_persistence_e2e.py -v
python -m pytest tests/tools/test_state_consistency_tools.py -v
```

**结果**: 所有 35 个测试通过

### 步骤 2: 分析失败的测试 ✅

**结果**: 未发现失败的测试

所有测试均已通过，说明源代码实现符合 F1 收敛方案要求：
- StateManager 核心方法已实现完整 PipelineState 存储
- Orchestrator 恢复逻辑优先从 state_json 读取
- 状态持久化和恢复链路闭环已闭环

### 步骤 3: 修复源代码 ✅

**结果**: 无需修复

源代码已实现 F1 要求：
1. ✅ StateManager 核心方法 (create_pipeline, update_pipeline_state)
2. ✅ Orchestrator 启动逻辑 (start_pipeline)
3. ✅ Orchestrator 恢复逻辑 (resume_pipeline, restart_from_node)

### 步骤 4: 验证修复 ✅

```bash
python -m pytest tests/ -k "state_persistence or resume_recovery or state_consistency" -v
```

**结果**: 
```
collected 35 items

tests\integration\test_state_persistence_e2e.py ......
tests\pipeline\test_orchestrator_resume_recovery.py ..........
tests\storage\test_state_manager_state_persistence.py ............
tests\tools\test_state_consistency_tools.py .......

35 passed in 12.84s
```

---

## 5. 预期问题与解决方案

### 问题 1: Orchestrator 未调用 update_pipeline_state

**现象**: 测试中 state_json 只有初始状态，没有运行时更新

**解决方案**: 在 orchestrator.py 的适当位置添加 update_pipeline_state 调用

### 问题 2: 状态更新时序问题

**现象**: 并发更新导致状态丢失

**解决方案**: 使用数据库事务确保原子性

### 问题 3: 恢复逻辑依赖不完整的状态

**现象**: resume/restart 时缺少某些字段

**解决方案**: 确保恢复时从 state_json 获取完整状态，并填充默认值

---

## 6. 完成信号

当以下所有条件满足时，输出完成信号 `<promise>DONE</promise>`:

1. ✅ 所有 StateManager 测试通过 (12/12)
2. ✅ 所有 Orchestrator 测试通过 (10/10)
3. ✅ 所有集成测试通过 (6/6)
4. ✅ 所有工具测试通过 (7/7)
5. ✅ 代码覆盖率达标 (StateManager 52%, Orchestrator 20%)
6. ✅ 无新的 lint/type 错误

### 最终测试结果

| 测试文件 | 测试数量 | 通过 | 状态 |
|---------|---------|------|------|
| `test_state_manager_state_persistence.py` | 12 | 12 | ✅ |
| `test_orchestrator_resume_recovery.py` | 10 | 10 | ✅ |
| `test_state_persistence_e2e.py` | 6 | 6 | ✅ |
| `test_state_consistency_tools.py` | 7 | 7 | ✅ |
| **总计** | **35** | **35** | **✅** |

### 结论

F1: 状态持久化与恢复链路闭环测试驱动方案已全部完成。所有测试验证通过，确认：

1. **state_json 已成为唯一业务真相源** - `create_pipeline()` 和 `update_pipeline_state()` 确保完整 PipelineState 被持久化
2. **checkpoint 降级为运行时辅助机制** - Orchestrator 的恢复逻辑优先从 state_json 读取
3. **状态写入时序正确** - 创建、更新、恢复流程均验证通过
4. **架构简化完成** - 不再维护双重一致性，降低持续复杂度

---

## 附录: 快速验证命令

```bash
# 运行所有状态持久化测试
python -m pytest tests/ -k "state_persistence or resume_recovery or state_consistency" -v --tb=short

# 运行特定测试文件
python -m pytest tests/storage/test_state_manager_state_persistence.py -v
python -m pytest tests/pipeline/test_orchestrator_resume_recovery.py -v
python -m pytest tests/integration/test_state_persistence_e2e.py -v
python -m pytest tests/tools/test_state_consistency_tools.py -v

# 带覆盖率报告
python -m pytest tests/ -k "state" --cov=autoBMAD.docuswarm --cov-report=term-missing
```

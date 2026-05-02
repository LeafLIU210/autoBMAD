# TD-003 深度分析报告: 测试覆盖率不足

## 问题概述

**问题**: 测试覆盖率 < 20%，核心模块缺乏测试
**影响**: 回归风险高，重构困难，难以验证正确性
**目标**: 核心模块达到 60% 覆盖率

## 缺失测试统计

- **高优先级缺失**: 11 项
- **中优先级缺失**: 0 项
- **低优先级缺失**: 0 项

## 当前测试状态

```
autoBMAD/docuswarm/tests/
├── conftest.py              # Fixtures 完善
├── unit/
│   └── test_message_extraction.py  # 仅 1 个测试文件
├── integration/
│   └── (空)
└── cli/
    └── (空)
```

## 高优先级测试缺口 (P0)

### pipeline/orchestrator.py -> HybridOrchestrator

**类型**: class
**原因**: TD-003: Orchestrator 4 种操作 (start/resume/restart/pause) 无测试
**建议**: 创建 test_orchestrator.py 测试所有 4 种操作

### pipeline/orchestrator.py -> start_pipeline

**类型**: method
**原因**: Core orchestration logic untested
**建议**: Mock LangGraph and test full pipeline flow

### pipeline/orchestrator.py -> resume_pipeline

**类型**: method
**原因**: Session recovery logic untested
**建议**: Test checkpoint resume and session restoration

### pipeline/orchestrator.py -> restart_from_node

**类型**: method
**原因**: Node restart logic untested
**建议**: Test node state clearing and restart

### context/isolation.py -> ContextManager

**类型**: class
**原因**: TD-003: ContextManager 隔离验证无测试
**建议**: 创建 test_isolation.py 测试三层隔离

### context/isolation.py -> _validate_no_private_fields

**类型**: method
**原因**: Private field validation untested
**建议**: Test private field detection at all nesting levels

### context/isolation.py -> _check_for_private_fields

**类型**: function
**原因**: Recursive private field check untested
**建议**: Test nested dict/list structures

### pipeline/quality.py -> VerdictDeterminer

**类型**: class
**原因**: TD-003: QualityGate 逻辑无测试
**建议**: 创建 test_quality.py 测试所有 verdict 分支

### pipeline/quality.py -> determine_verdict

**类型**: method
**原因**: All verdict branches need testing
**建议**: Test APPROVED/NEEDS_REVISION/FORCE_APPROVED/BLOCKED

### llm/approval.py -> DocuSwarmApprovalHandler

**类型**: class
**原因**: TD-003: ApprovalHandler 决策无测试
**建议**: 创建 test_approval.py 测试决策逻辑

### llm/approval.py -> handle

**类型**: method
**原因**: Approval decision logic untested
**建议**: Test all action types and policies

## 测试实现计划

### Phase 1: 核心编排器测试 (Week 1)

创建 `tests/unit/test_orchestrator.py`:

```python
class TestHybridOrchestrator:
    # Test HybridOrchestrator 4 core operations

    async def test_start_pipeline_success(self): ...
    async def test_start_pipeline_validation_failure(self): ...
    async def test_resume_pipeline_with_session_recovery(self): ...
    async def test_resume_pipeline_fallback_to_restart(self): ...
    async def test_restart_from_node_clears_subsequent_state(self): ...
    async def test_pause_pipeline_preserves_state(self): ...
    async def test_cancel_current_node_triggers_cancellation(self): ...
```

### Phase 2: 上下文隔离测试 (Week 1)

创建 `tests/unit/test_isolation.py`:

```python
class TestContextManager:
    # Test ContextManager 3-layer isolation

    def test_build_independent_context_full_access(self): ...
    def test_build_evaluator_context_restricted_access(self): ...
    def test_validate_no_private_fields_detects_leak(self): ...
    def test_check_for_private_fields_recursive(self): ...
    def test_private_fields_at_different_nesting_levels(self): ...
```

### Phase 3: 质量门控测试 (Week 2)

创建 `tests/unit/test_quality.py`:

```python
class TestVerdictDeterminer:
    # Test QualityGate decision logic

    def test_determine_verdict_approved(self): ...
    def test_determine_verdict_needs_revision(self): ...
    def test_determine_verdict_force_approved_at_max_iter(self): ...
    def test_determine_verdict_blocked_at_max_iter(self): ...
    def test_node_specific_thresholds(self): ...
```

### Phase 4: 审批处理器测试 (Week 2)

创建 `tests/unit/test_approval.py`:

```python
class TestDocuSwarmApprovalHandler:
    # Test ApprovalHandler decision logic

    def test_handle_auto_approve_safe_actions(self): ...
    def test_handle_reject_dangerous_actions(self): ...
    def test_handle_yolo_mode_approves_all(self): ...
    def test_handle_unknown_action_policy(self): ...
```

## 预期覆盖率目标

| 模块 | 当前 | 目标 | 优先级 |
|------|------|------|--------|
| pipeline/orchestrator.py | <5% | 60% | P0 |
| context/isolation.py | 0% | 80% | P0 |
| pipeline/quality.py | 0% | 80% | P0 |
| llm/approval.py | 0% | 80% | P0 |
| storage/checkpoints.py | <10% | 60% | P1 |
| agents/*.py | <5% | 50% | P1 |

## 测试策略

### 单元测试原则

1. **Mock 外部依赖**: LangGraph, Kimi SDK, SQLite
2. **测试边界条件**: 空输入、异常输入、边界值
3. **验证副作用**: 状态变更、数据库写入、日志输出

### 集成测试策略

1. **内存数据库**: 使用 `:memory:` SQLite 避免磁盘 IO
2. **Mock LLM 响应**: 使用 conftest.py 中的 mock_session_manager
3. **状态验证**: 检查 checkpoint 和 pipeline 状态一致性

# Epic 24: 双代理流程集成与端到端测试

**Epic ID**: EPIC-24  
**Version**: 1.0  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days

---

## 1. Epic Overview

### 1.1 Summary

验证双代理流程（Independent + Evaluator）完整执行链路，确保系统各组件协同工作正常。

### 1.2 Business Value

- **流程验证**: 确保双代理迭代循环正常工作
- **上下文隔离**: 验证 private_reasoning 正确隔离
- **状态管理**: 验证 PipelineState 正确更新
- **交付物保存**: 验证双层保存机制工作正常

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 单次迭代 | DualAgentNode 单次迭代成功完成 |
| 多迭代 | 最多3次迭代后完成或强制结束 |
| 上下文隔离 | Evaluator 从未收到 private_reasoning |
| State 更新 | PipelineState 正确记录交付物和迭代次数 |
| 交付物保存 | 双层保存机制正常工作 |
| 性能 | 单次迭代 < 60s，完整节点 < 180s |

### 1.4 Dependencies

- **Prerequisites**: EPIC-21, EPIC-22, EPIC-23 完成
- **Blocks**: 无 (这是最后一个 Epic)

---

## 2. Stories

### Story 24.1: DualAgentNode 单次迭代测试

As a developer,  
I want to write tests for DualAgentNode completing in a single iteration,  
So that we can verify the basic execution flow works.

**Acceptance Criteria:**

**Given** a DualAgentNode instance with mocked agents  
**When** independent_agent.execute returns a deliverable with questions  
**And** evaluator_agent.execute returns APPROVED verdict  
**Then** the node execution completes in iteration 1  
**And** the result contains the deliverable  
**And** the result contains the evaluation with APPROVED verdict

**Given** a successful single iteration execution  
**When** I examine the NodeResult  
**Then** it contains iteration count = 1  
**And** it contains the questions from independent agent  
**And** force_completion is None

**Technical Notes:**
- Mock IndependentAgent to return deliverable with questions
- Mock EvaluatorAgent to return APPROVED verdict
- Verify NodeResult structure and fields

**Test File**: `tests/nodes/test_dual_agent_single_iteration.py`

---

### Story 24.2: DualAgentNode 多迭代测试

As a developer,  
I want to write tests for DualAgentNode handling multiple iterations,  
So that we can verify the revision loop works correctly.

**Acceptance Criteria:**

**Given** a DualAgentNode instance  
**When** first evaluation returns NEEDS_REVISION verdict  
**And** second evaluation returns APPROVED verdict  
**Then** the node executes independent agent twice  
**And** the final result has iteration count = 2  
**And** the second independent call includes iteration feedback

**Given** a DualAgentNode with max iterations = 3  
**When** all evaluations return NEEDS_REVISION  
**And** scores are above escalation threshold (0.5)  
**Then** the node executes for 3 iterations  
**And** then force completes  
**And** force_completion is not None in result

**Technical Notes:**
- Test two iterations with NEEDS_REVISION → APPROVED transition
- Test max iterations (3) with force completion
- Verify iteration_feedback is passed to subsequent independent calls

**Test File**: `tests/nodes/test_dual_agent_multi_iteration.py`

---

### Story 24.3: 上下文隔离测试

As a developer,  
I want to write tests for context isolation between agents,  
So that private information never leaks to the evaluator.

**Acceptance Criteria:**

**Given** an IndependentAgent output containing private_reasoning  
**When** ContextFilter.filter_for_evaluator is called  
**Then** the filtered output does not contain private_reasoning  
**And** it does not contain tool_call_history  
**And** it does not contain internal_notes  
**And** it does not contain iteration_feedback  
**And** public fields (deliverable, questions) are preserved

**Given** a complete DualAgentNode execution  
**When** I capture all evaluator_agent.execute inputs  
**Then** none of the inputs contain private_reasoning  
**And** the independent agent's private fields are never passed to evaluator

**Technical Notes:**
- Private fields to filter: private_reasoning, tool_call_history, internal_notes, iteration_feedback
- Public fields to preserve: deliverable, questions
- Capture and verify all evaluator inputs during execution

**Test File**: `tests/nodes/test_context_isolation.py`

---

### Story 24.4: PipelineState 更新测试

As a developer,  
I want to write tests for PipelineState updates during execution,  
So that we can verify state management works correctly.

**Acceptance Criteria:**

**Given** an initial PipelineState with empty deliverables  
**When** a node execution completes with a deliverable  
**Then** the new state contains the deliverable in deliverables[node_id]

**Given** a PipelineState with a completed node  
**When** I examine the updated state  
**Then** completed_nodes includes the node_id  
**And** node_iterations[node_id] equals the iteration count  
**And** evaluations[node_id] contains the final evaluation

**Given** a PipelineState  
**When** state is copied using deep copy  
**Then** modifications to the copy do not affect the original  
**And** mutations are prevented

**Technical Notes:**
- Verify state updates after node execution
- Test deep copy behavior to prevent mutation
- Check completed_nodes, node_iterations, evaluations, deliverables fields

**Test File**: `tests/pipeline/test_state_updates.py`

---

### Story 24.5: 交付物双层保存测试

As a developer,  
I want to write tests for the dual-layer deliverable saving mechanism,  
So that we can verify both layers work correctly.

**Acceptance Criteria:**

**Given** the create_deliverable tool is called with valid params  
**When** the tool executes  
**Then** a file is created in the work_dir  
**And** the file contains the deliverable content  
**And** the tool returns success status

**Given** the FileStorage.save_deliverable is called  
**When** it saves content with pipeline_id and node_type  
**Then** a file is created at output/{pipeline_id}/{filename}  
**And** the file has the correct canonical name (e.g., analyst-report.md)  
**And** frontmatter is added when requested

**Given** FileStorage uses atomic write  
**When** a save operation completes  
**Then** no .tmp files remain in the directory  
**And** the file is fully written or not created at all

**Technical Notes:**
- Layer 1: create_deliverable tool saves to work_dir
- Layer 2: FileStorage saves to output/{pipeline_id}/ with canonical name
- Atomic write: temp file first, then rename to final name

**Test File**: `tests/storage/test_dual_layer_save.py`

---

### Story 24.6: 文件名映射测试

As a developer,  
I want to write tests for deliverable filename mapping,  
So that each node type maps to the correct filename.

**Acceptance Criteria:**

**Given** the FILENAME_MAP  
**When** I look up "analyst"  
**Then** it returns "analyst-report.md"

**Given** the FILENAME_MAP  
**When** I look up "pm" or "prd"  
**Then** it returns "prd.md"

**Given** the FILENAME_MAP  
**When** I look up "ux"  
**Then** it returns "ux-design.md"

**Given** the FILENAME_MAP  
**When** I look up "architect" or "architecture"  
**Then** it returns "architecture.md"

**Given** the FILENAME_MAP  
**When** I look up "po" or "epics"  
**Then** it returns "epics-stories.md"

**Technical Notes:**
- Use pytest.mark.parametrize for testing multiple node types
- Support aliases: pm/prd, architect/architecture, po/epics

**Filename Mapping Table:**

| Node Type | Filename |
|-----------|----------|
| analyst | analyst-report.md |
| pm, prd | prd.md |
| ux | ux-design.md |
| architect, architecture | architecture.md |
| po, epics | epics-stories.md |

**Test File**: `tests/storage/test_filename_mapping.py`

---

### Story 24.7: 上下文链式传递测试

As a developer,  
I want to write tests for context chaining between nodes,  
So that each node receives appropriate predecessor context.

**Acceptance Criteria:**

**Given** the accumulate_context function  
**When** called for "analyst" node with subject context  
**Then** it returns only subject_context  
**And** no predecessor deliverables are included

**Given** the accumulate_context function  
**When** called for "pm" node with analyst deliverable available  
**Then** it returns subject_context plus analyst_deliverable

**Given** the accumulate_context function  
**When** called for "po" node with all predecessor deliverables  
**Then** it returns subject_context plus all four predecessor deliverables  
**And** the structure matches expectations for po node

**Technical Notes:**
- analyst: only subject_context
- pm: subject_context + analyst_deliverable
- ux: subject_context + analyst_deliverable + pm_deliverable
- architect: subject_context + analyst_deliverable + pm_deliverable + ux_deliverable
- po: all four predecessor deliverables

**Test File**: `tests/pipeline/test_context_chaining.py`

---

### Story 24.8: 端到端集成测试

As a developer,  
I want to write end-to-end tests for complete node execution,  
So that we can verify the entire flow works together.

**Acceptance Criteria:**

**Given** a complete pipeline setup with session manager  
**When** I execute the analyst node end-to-end  
**Then** the graph executes without errors  
**And** a deliverable file is created  
**And** PipelineState is properly updated

**Given** a pipeline state transitions test  
**When** I simulate node execution from start to completion  
**Then** state transitions follow the expected sequence:  
  - status starts as "running"  
  - current_node is set correctly  
  - completed_nodes is updated after execution  
  - deliverables contains the output

**Given** the performance benchmarks  
**When** I measure execution times  
**Then** single iteration completes in < 60s  
**And** complete node execution (3 iterations) completes in < 180s  
**And** state updates take < 100ms  
**And** file saves take < 50ms

**Technical Notes:**
- Test complete flow with mocked LLM calls
- Verify state transitions: running → completed
- Check file creation and state updates

**Test File**: `tests/integration/test_e2e_node_execution.py`

---

### Story 24.9: 性能基准测试

As a developer,  
I want to establish performance benchmarks for the system,  
So that we can detect performance regressions.

**Acceptance Criteria:**

**Given** the test environment  
**When** I run the single iteration benchmark  
**Then** it records the execution time  
**And** asserts it is under 60 seconds

**Given** the test environment  
**When** I run the complete node benchmark  
**Then** it records the total execution time  
**And** asserts it is under 180 seconds for 3 iterations

**Given** the test environment  
**When** I run the state update benchmark  
**Then** it records state mutation time  
**And** asserts it is under 100 milliseconds

**Given** the test environment  
**When** I run the file save benchmark  
**Then** it records file write time  
**And** asserts it is under 50 milliseconds

**Technical Notes:**
- Performance targets:
  - Single iteration: < 60s
  - Complete node (3 iterations): < 180s
  - State update: < 100ms
  - File save: < 50ms

**Performance Benchmarks Table:**

| Metric | Target | Test Method |
|--------|--------|-------------|
| 单次迭代执行 | < 60s | test_single_iteration_approved |
| 完整节点执行 (3迭代) | < 180s | test_max_iterations_force_complete |
| State 更新 | < 100ms | test_deliverable_added_to_state |
| 文件保存 | < 50ms | test_first_layer_tool_save |

---

## 3. Test Coverage Matrix

| 组件 | 单元测试 | 集成测试 | E2E测试 | 目标覆盖率 |
|------|---------|---------|---------|-----------|
| DualAgentNode | ✅ | ✅ | ✅ | >90% |
| IndependentAgent | ✅ | ✅ | - | >90% |
| EvaluatorAgent | ✅ | ✅ | - | >90% |
| ContextFilter | ✅ | ✅ | - | >90% |
| PipelineState | ✅ | ✅ | ✅ | >90% |
| FileStorage | ✅ | ✅ | - | >90% |

---

## 4. Implementation Notes

### 4.1 Dual-Agent Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dual-Agent Execution Flow                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DualAgentNode.execute(subject_context, task, pipeline_id)       │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Iteration Loop (max 3)                       │   │
│  │                                                           │   │
│  │  ① IndependentAgent.execute(context)                     │   │
│  │       ├── Setup work_dir: output/{pipeline_id}/          │   │
│  │       ├── Call LLM with BMM system prompt                │   │
│  │       ├── Tool: create_deliverable (第一层保存)           │   │
│  │       └── Parse response → IndependentOutput             │   │
│  │                                                           │   │
│  │  ② ContextFilter.filter_for_evaluator(output)            │   │
│  │       └── Remove: private_reasoning, tool_call_history   │   │
│  │                                                           │   │
│  │  ③ EvaluatorAgent.execute(filtered_context)              │   │
│  │       └── Return: verdict, score, issues, suggestions    │   │
│  │                                                           │   │
│  │  ④ VerdictHandler.decide()                               │   │
│  │       ├── APPROVED → break                               │   │
│  │       ├── FORCE_APPROVED → force completion              │   │
│  │       ├── BLOCKED → break                                │   │
│  │       └── NEEDS_REVISION → continue with feedback        │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                          │
│       ▼                                                          │
│  Return NodeResult(deliverable, questions, evaluation, ...)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Verdict Types

| Verdict | Action |
|---------|--------|
| APPROVED | Exit loop, return result |
| FORCE_APPROVED | Force completion after max iterations |
| BLOCKED | Exit loop, return with error |
| NEEDS_REVISION | Continue loop with feedback |

### 4.3 Context Accumulation Rules

| Node | Receives Context |
|------|------------------|
| analyst | subject_context only |
| pm | subject_context + analyst_deliverable |
| ux | subject_context + analyst_deliverable + pm_deliverable |
| architect | subject_context + analyst_deliverable + pm_deliverable + ux_deliverable |
| po | All four predecessor deliverables |

---

## 5. Verification Commands

```bash
# 运行双代理相关测试
pytest tests/nodes/test_dual_agent_single_iteration.py -v
pytest tests/nodes/test_dual_agent_multi_iteration.py -v
pytest tests/nodes/test_context_isolation.py -v

# 运行 PipelineState 测试
pytest tests/pipeline/test_state_updates.py -v
pytest tests/pipeline/test_context_chaining.py -v

# 运行存储测试
pytest tests/storage/test_dual_layer_save.py -v
pytest tests/storage/test_filename_mapping.py -v

# 运行集成测试
pytest tests/integration/test_e2e_node_execution.py -v

# 全部测试
pytest tests/ -v --tb=short
```

---

## 6. Dependencies

```
EPIC-21 (Configuration System)
       │
       ▼
EPIC-22 (Persona Refactoring) ─────┐
       │                          │
       ▼                          │
EPIC-23 (Code Cleanup) ←─────────┤
       │                          │
       ▼                          │
EPIC-24 (本 Epic) ←───────────────┘
```

---

## 7. Related Documents

- [TDD-BMM-04: 双代理流程集成与端到端测试](../solution/TDD-BMM-04-DualAgent-Integration-E2E.md)
- [EPIC-21: NodeLoader 配置加载系统重构](./EPIC-21-NodeLoader-Config-Refactor.md)
- [EPIC-22: Persona 角色上下文与 System Prompt 重构](./EPIC-22-Persona-SystemPrompt-Refactor.md)
- [EPIC-23: 废弃代码移除与功能精简](./EPIC-23-Deprecated-Code-Removal.md)

---

**Document End**

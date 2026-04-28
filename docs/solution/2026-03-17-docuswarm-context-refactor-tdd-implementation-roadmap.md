# DocuSwarm Context Refactor TDD 实施路线图

> 文档: 测试驱动实施方案总览  
> 日期: 2026-03-17  
> 范围: autoBMAD/docuswarm Context Refactor

## 文档导航

| 文档 | 描述 |
|------|------|
| **本路线图** | 实施顺序、依赖关系、验收标准 |
| [深度研究报告](../research/2026-03-17-docuswarm-context-refactor-deep-research-report.md) | 问题发现与分析 |
| [TDD 主方案](./2026-03-17-docuswarm-context-refactor-tdd-master-plan.md) | 完整测试驱动方案 |
| [Phase 1: P1-1](./2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md) | update_context 持久化 |
| [Phase 2: P0-3](./2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md) | 单一交付物真相 |
| [Phase 3: P0-2](./2026-03-17-phase3-p0-2-evaluator-context-tdd-execution-plan.md) | Evaluator 上下文补完 |

---

## 实施顺序

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: P1-1 - update_context 持久化真闭环  (优先级: 🔴 最高)  │
│  ├─ Week 1: Tool 绑定 + Agent Input + Prompt 渲染 + State 恢复   │
│  └─ 输出: shared_context 跨节点可用                              │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: P0-3 - 单一交付物真相收口  (优先级: 🔴 最高)           │
│  ├─ Week 2: 强制验证 + 字段统一 + 禁止 fallback + 传播限制       │
│  └─ 输出: Evaluator 始终评审文件正文                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: P0-2 - Evaluator 上下文补完  (优先级: 🟡 中)           │
│  ├─ Week 3 (前半): EvaluatorAgentInput + Prompt 渲染            │
│  └─ 输出: Evaluator prompt 包含原始需求摘要                      │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4: P0-1/P1-2 - 清理与收敛  (优先级: 🟢 低)               │
│  ├─ Week 3 (后半): 状态层收敛 + docs-free 清理                  │
│  └─ 输出: 代码库整洁一致                                         │
├─────────────────────────────────────────────────────────────────┤
│  Phase 5: TEST - 测试补全与回归  (优先级: 🔴 最高)               │
│  ├─ Week 4: 单元测试 + 集成测试 + 回归测试 + 文档               │
│  └─ 输出: 完整测试护栏                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 依赖关系图

```
P1-1 (update_context 持久化)
    │
    ├──► P0-3 (单一交付物真相)
    │       │
    │       └──► P0-2 (Evaluator 上下文)
    │               │
    │               └──► P0-1/P1-2 (清理)
    │
    └──► Phase 5 (测试补全) ──► 依赖所有 Phase
```

**关键依赖**:
1. **P1-1 必须在 P0-3 之前**: shared_context 持久化为状态管理基础
2. **P0-3 必须在 P0-2 之前**: Evaluator 输入依赖单一真相的文件读取
3. **所有 Phase 必须在 Phase 5 之前**: 测试补全需要最终代码结构

---

## 各 Phase 详细任务

### Phase 1: P1-1 - update_context 持久化真闭环

**持续时间**: Week 1 (5 个工作日)

| 天 | 任务 | 测试文件 | 实现文件 |
|----|------|----------|----------|
| 1 | Tool 强制依赖注入 | `test_update_context_binding.py` | `update_context.py` |
| 2 | Agent Input 添加字段 | `test_contracts.py` | `contracts.py` |
| 3 | ContextManager 传递 | `test_isolation.py` | `isolation.py` |
| 4 | Prompt 渲染 | `test_contract_builder.py` | `contract_builder.py` |
| 5 | State 恢复 + 集成 | `test_state_shared_context.py` + 集成测试 | `state.py` + `executor.py` |

**关键测试**:
```python
# 必须通过的测试
test_tool_requires_state_manager
test_tool_accepts_valid_dependencies
test_tool_call_uses_state_manager
test_independent_agent_input_has_shared_context
test_build_independent_input_includes_shared_context
test_build_context_section_includes_shared_context
test_pipeline_state_has_shared_context
test_shared_context_persists_across_nodes  # 集成
```

**完成标准**:
- [ ] `UpdateContextTool` 初始化必须提供 `StateManager` 和 `pipeline_id`
- [ ] `UpdateContextTool` 调用实际写入 `StateManager.update_shared_context()`
- [ ] `IndependentAgentInput` 包含 `shared_context` 字段
- [ ] `ContextManager.build_independent_input()` 传递 `shared_context`
- [ ] `PipelineState` 声明并初始化 `shared_context`
- [ ] 跨节点 `shared_context` 持久化通过集成测试

---

### Phase 2: P0-3 - 单一交付物真相收口

**持续时间**: Week 2 (5 个工作日)

| 天 | 任务 | 测试文件 | 实现文件 |
|----|------|----------|----------|
| 1 | 强制验证 file_path/sha256 | `test_response_validation.py` | `response.py` |
| 2 | DeliverableArtifact 字段统一 | `test_contracts.py` | `contracts.py` |
| 3 | 代码迁移 content → summary | 回归测试 | `isolation.py` 等 |
| 4 | Evaluator 禁止 fallback | `test_isolation.py` | `isolation.py` |
| 5 | 传播限制 + 集成 | `test_state_accumulation.py` + 集成测试 | `state.py` |

**关键测试**:
```python
# 必须通过的测试
test_file_path_is_required
test_sha256_is_required
test_accepts_valid_metadata_only_deliverable
test_uses_summary_field
test_build_evaluator_input_reads_file_content
test_raises_if_file_missing
test_raises_if_file_path_missing
test_accumulate_context_excludes_full_content
```

**完成标准**:
- [ ] `validate_independent_output()` 强制要求 `file_path` 和 `sha256`
- [ ] `DeliverableArtifact` 使用 `summary` 而非 `content`
- [ ] 所有代码从 `content` 迁移到 `summary`
- [ ] `build_evaluator_input()` 总是从文件读取正文
- [ ] `build_evaluator_input()` 不使用 `deliverable.get("content")` fallback
- [ ] 链式上下文只传播 metadata + summary

---

### Phase 3: P0-2 - Evaluator 上下文补完

**持续时间**: Week 3 前半 (2-3 个工作日)

| 天 | 任务 | 测试文件 | 实现文件 |
|----|------|----------|----------|
| 1 | EvaluatorAgentInput 添加字段 | `test_contracts.py` | `contracts.py` |
| 2 | ContextManager 传递 | `test_isolation.py` | `isolation.py` |
| 3 | Prompt 渲染 + Agent 使用 | `test_contract_builder.py` + `test_evaluator.py` | `contract_builder.py` + `evaluator.py` |

**关键测试**:
```python
# 必须通过的测试
test_has_original_context_field
test_original_context_summary_is_optional
test_includes_original_context_from_execution_context
test_build_evaluator_context_section_includes_original
test_render_evaluator_prompt_includes_original_context
```

**完成标准**:
- [ ] `EvaluatorAgentInput` 包含 `original_context_summary` 字段
- [ ] `build_evaluator_input()` 传递原始上下文
- [ ] Evaluator prompt 稳定出现"原始需求摘要"章节
- [ ] `EvaluatorAgent.execute_with_input()` 使用原始上下文

---

### Phase 4: P0-1/P1-2 - 清理与收敛

**持续时间**: Week 3 后半 (2-3 个工作日)

| 天 | 任务 | 描述 |
|----|------|------|
| 4 | PipelineState 收敛 | 可选: 添加 `execution_context` 字段 |
| 5 | docs-free 清理 | 更新 CLI 和 README，移除 docs/ 引用 |

**完成标准**:
- [ ] (可选) `PipelineState` 显式持有 `execution_context`
- [ ] CLI 不再引用 `docs/` 路径作为示例
- [ ] README 更新为 docs-free 描述

---

### Phase 5: TEST - 测试补全与回归

**持续时间**: Week 4 (5 个工作日)

| 天 | 任务 | 产出 |
|----|------|------|
| 1 | 单元测试补全 | 覆盖所有修改的模块 |
| 2 | 集成测试 | 跨节点 flow、shared_context、单一真相 |
| 3 | 回归测试 | 验证旧问题不再出现 |
| 4 | 端到端测试 | 完整 workflow 验证 |
| 5 | 文档更新 | 测试文档、API 文档更新 |

**必须创建的测试文件**:
```
tests/
├── unit/
│   ├── node_execution/
│   │   ├── test_contracts.py           # ✅ contracts
│   │   ├── test_context_builder.py     # builder
│   │   └── test_executor.py            # executor
│   ├── prompts/
│   │   └── test_contract_builder.py    # ✅ contract_builder
│   ├── tools/
│   │   └── test_update_context.py      # ✅ update_context
│   ├── context/
│   │   └── test_isolation.py           # ✅ isolation
│   ├── pipeline/
│   │   └── test_state_shared_context.py # ✅ state
│   └── llm/
│       └── test_response_validation.py  # ✅ response
├── integration/
│   ├── test_shared_context_cross_node.py    # ✅ Phase 1
│   ├── test_single_truth_deliverable.py     # ✅ Phase 2
│   └── test_evaluator_original_context.py   # ✅ Phase 3
└── regression/
    └── test_context_refactor.py        # 回归测试
```

**覆盖率要求**:
| 模块 | 目标覆盖率 |
|------|-----------|
| `node_execution/contracts.py` | 100% |
| `node_execution/context_builder.py` | 90% |
| `tools/update_context.py` | 90% |
| `context/isolation.py` | 85% |
| `prompts/contract_builder.py` | 85% |
| `llm/response.py` | 90% |

---

## 每日 TDD 工作流

```
09:00 - 09:30  审查昨日代码，规划今日任务
09:30 - 10:30  Red: 编写失败的测试
10:30 - 11:00  运行测试确认失败
11:00 - 12:00  Green: 最小实现通过测试
12:00 - 13:00  午餐
13:00 - 14:00  运行测试确认通过
14:00 - 16:00  Refactor: 重构代码
16:00 - 17:00  类型检查 + 静态检查
17:00 - 17:30  提交代码，写提交信息
17:30 - 18:00  更新进度文档
```

**提交信息格式**:
```
[TDD-PhaseX][Red/Green/Refactor] <message>

- 关联研究: P<X>-<XXX>
- 测试: <test_name>
- 变更: <brief description>
```

---

## 风险缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 向后兼容性破坏 | 中 | 高 | 使用 `total=False` TypedDict；渐进式迁移 |
| 测试不稳定 | 低 | 中 | 使用 mocks；避免外部依赖 |
| 进度延迟 | 中 | 中 | 每 Phase 有明确的验收标准；可跳过 Phase 4 |
| 代码审查阻塞 | 中 | 低 | 每 2-3 天提交一次 PR；小步快跑 |
| LLM 调用成本 | 低 | 低 | 集成测试使用 mocks；不调用真实 LLM |

---

## 验收总清单

### Phase 1 验收
- [ ] `UpdateContextTool` 强制依赖注入
- [ ] `shared_context` 进入 `IndependentAgentInput`
- [ ] `shared_context` 渲染到 prompt
- [ ] `PipelineState` 恢复 `shared_context`
- [ ] 集成测试: 跨节点 `shared_context` 持久化

### Phase 2 验收
- [ ] `file_path` 和 `sha256` 强制验证
- [ ] `summary` 替代 `content`
- [ ] Evaluator 禁止 fallback 到摘要
- [ ] 链式上下文只传播 metadata + summary
- [ ] 集成测试: 单一真相端到端

### Phase 3 验收
- [ ] `EvaluatorAgentInput` 包含 `original_context_summary`
- [ ] `build_evaluator_input()` 传递原始上下文
- [ ] Evaluator prompt 包含"原始需求摘要"
- [ ] 集成测试: Evaluator 看到原始上下文

### Phase 4 验收
- [ ] (可选) PipelineState 收敛
- [ ] docs-free 边界清理

### Phase 5 验收
- [ ] 所有测试文件创建完成
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试全部通过
- [ ] 回归测试无失败
- [ ] 类型检查通过
- [ ] 静态检查通过

---

## 参考文档

1. **深度研究报告**: `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`
2. **TDD 主方案**: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
3. **Phase 1 计划**: `docs/solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md`
4. **Phase 2 计划**: `docs/solution/2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md`
5. **Phase 3 计划**: `docs/solution/2026-03-17-phase3-p0-2-evaluator-context-tdd-execution-plan.md`

---

## 团队分工建议

| 角色 | 职责 | 主要文件 |
|------|------|----------|
| 开发者 A | Phase 1 + State 管理 | `update_context.py`, `state.py`, `executor.py` |
| 开发者 B | Phase 2 + 验证逻辑 | `response.py`, `isolation.py`, `contracts.py` |
| 开发者 C | Phase 3 + Prompt | `contract_builder.py`, `evaluator.py` |
| 开发者 D | Phase 5 + 集成测试 | 所有测试文件 |

**Code Review 轮替**: 每 Phase 完成后进行交叉审查

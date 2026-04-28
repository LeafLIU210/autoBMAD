# DocuSwarm Context Refactor 深度研究报告

> 研究日期: 2026-03-17
> 基于评估: `docs/evaluation/2026-03-17-docuswarm-context-refactor-implementation-evaluation.md`
> 研究范围: `autoBMAD/docuswarm`

## 执行摘要

- **总体完成度**: 68%
- **研究发现总数**: 18
- **严重 (Critical)**: 0
- **高危 (High)**: 6
- **中等 (Medium)**: 2
- **低危 (Low)**: 10

## 实现状态总览

| 主题 | 目标 | 当前状态 | 完成度 | 阻塞项 |
|------|------|----------|--------|--------|
| P0-1 | 收敛为单一上下文协议 | 已验证: 3, 部分: 1, 未验证: 0 | 87% | 无 |
| P0-2 | 让 node.yaml 真正进入 prompt | 已验证: 3, 部分: 1, 未验证: 0 | 87% | EvaluatorAgentInput 缺少原始上下文摘要字段 |
| P0-3 | 消除摘要/正式文档双轨 | 已验证: 1, 部分: 3, 未验证: 0 | 62% | file_path 和 sha256 不是强制验证字段; DeliverableArtifact 目标结构与运行时验证不一致; Evaluator 在 file_path 缺失时会退回到 deliverable.content |
| P1-1 | 让 update_context 接入 StateManager | 已验证: 1, 部分: 0, 未验证: 2 | 33% | shared_context 未进入 IndependentAgentInput |
| P1-2 | docs-free workflow | 已验证: 1, 部分: 1, 未验证: 0 | 75% | 无 |

## 详细研究发现

### P0-1 相关发现

#### [LOW] P0-1-001: NodeExecutionContext 核心数据结构已定义

**验证状态**: [OK] verified

**问题描述**: NodeExecutionContext、IndependentAgentInput、EvaluatorAgentInput TypedDict 已在 contracts.py 中定义

**当前状态**:
> 核心数据结构已落地

**期望状态**:
> 完整协议定义

**证据**:
- `autoBMAD\docuswarm\node_execution\contracts.py:117`: `NodeExecutionContext TypedDict defined`

**建议**: 已满足基本要求

---

#### [LOW] P0-1-002: NodeExecutionContextBuilder 已实现

**验证状态**: [OK] verified

**问题描述**: 上下文构建器已实现，用于从 node.yaml 和 runtime state 构建统一上下文

**当前状态**:
> Builder 已落地

**期望状态**:
> 完整构建逻辑

**建议**: 已满足基本要求

---

#### [LOW] P0-1-003: Executor 已接入单一上下文协议

**验证状态**: [OK] verified

**问题描述**: executor.py 已通过 context_builder 构建 execution_context 并调用 execute_with_context

**当前状态**:
> Executor 已接入新协议

**期望状态**:
> 全流程统一协议

**建议**: 已满足基本要求

---

#### [MED] P0-1-004: PipelineState 尚未显式持有 execution_context

**验证状态**: [~] partial

**问题描述**: 当前 PipelineState 仍以 context_file/chained_context/deliverables 为主，而非显式持有 execution_context

**当前状态**:
> 旧状态结构

**期望状态**:
> PipelineState.execution_context 字段

**证据**:
- `autoBMAD\docuswarm\pipeline\state.py:57`: `class PipelineState(TypedDict):`
- `autoBMAD\docuswarm\pipeline\state.py:79`: `def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> P`
- `autoBMAD\docuswarm\pipeline\state.py:80`: `"""Create an initial PipelineState with default values.`

**建议**: 考虑在 PipelineState 中显式添加 execution_context 字段以统一协议

---

### P0-2 相关发现

#### [HIGH] P0-2-003: EvaluatorAgentInput 缺少原始上下文摘要字段

**验证状态**: [~] partial

**问题描述**: EvaluatorAgentInput 当前只包含 task_name, task_description, deliverable_artifact, deliverable_body, criteria，没有原始上下文字段

**当前状态**:
> Evaluator 输入缺少原始上下文

**期望状态**:
> EvaluatorAgentInput 包含 original_context_summary

**证据**:
- `autoBMAD/docuswarm/node_execution/contracts.py:2428`: `class EvaluatorAgentInput(TypedDict):`

**建议**: 在 EvaluatorAgentInput 中添加原始上下文摘要字段，让 Evaluator prompt 能渲染'原始需求摘要'章节

---

#### [LOW] P0-2-001: NodePromptContractBuilder 已实现 prompt 契约构建

**验证状态**: [OK] verified

**问题描述**: contract_builder.py 已实现 Independent 和 Evaluator 的 prompt 契约构建

**当前状态**:
> Prompt Contract Builder 已落地

**期望状态**:
> 完整 prompt 注入

**建议**: 已满足基本要求

---

#### [LOW] P0-2-002: IndependentAgent 已使用 contract builder 组装 prompt

**验证状态**: [OK] verified

**问题描述**: IndependentAgent.execute_with_input() 已使用 NodePromptContractBuilder 构建 prompt

**当前状态**:
> Independent prompt 注入基本完成

**期望状态**:
> 完整闭环

**建议**: 已满足基本要求

---

#### [LOW] P0-2-004: node.yaml 已普遍采用新 schema

**验证状态**: [OK] verified

**问题描述**: 根目录 nodes/*/node.yaml 已普遍采用带 task / deliverable 子结构的新形态

**当前状态**:
> 新 schema 已落地

**期望状态**:
> 完整契约注入

**建议**: 与 overview 文档同步，更新研究结论

---

### P0-3 相关发现

#### [HIGH] P0-3-002: file_path 和 sha256 不是强制验证字段

**验证状态**: [~] partial

**问题描述**: 当前验证只要求 deliverable.title 和 deliverable.content，file_path/sha256 仅'如果存在则校验类型'。这意味着模型可以返回只有摘要、没有 artifact metadata 的输出，仍然通过验证。

**当前状态**:
> file_path/sha256 可选

**期望状态**:
> file_path/sha256 强制

**证据**:
- `autoBMAD\docuswarm\llm\response.py:145`: `- deliverable: {title: str, content: str, file_path: str, sha256: str, metadata:`
- `autoBMAD\docuswarm\llm\response.py:149`: `P0 Single Truth: file_path and sha256 are now included in deliverable.`
- `autoBMAD\docuswarm\llm\response.py:175`: `# P0 Single Truth: Validate file_path (optional, but if present must be string)`

**建议**: 将 file_path 和 sha256 提升为强制字段，确保单一真相

---

#### [HIGH] P0-3-003: DeliverableArtifact 目标结构与运行时验证不一致

**验证状态**: [~] partial

**问题描述**: 目标类型使用 'summary'，但运行时验证仍使用 'deliverable.content'。代码库同时存在两套语义：文档层用 summary，运行时/验证层用 content。

**当前状态**:
> summary/content 双轨并存

**期望状态**:
> 统一使用 summary

**证据**:
- `autoBMAD/docuswarm/node_execution/contracts.py:695`: `summary: str  # 简短摘要`
- `autoBMAD\docuswarm\llm\response.py:169`: `# Validate deliverable.content (required, must be string)`
- `autoBMAD\docuswarm\llm\response.py:171`: `raise ValidationError("deliverable.content: required field missing")`

**建议**: 统一使用 summary 字段，去掉 deliverable.content 的双重语义

---

#### [HIGH] P0-3-004: Evaluator 在 file_path 缺失时会退回到 deliverable.content

**验证状态**: [~] partial

**问题描述**: build_evaluator_input() 中当 file_path 缺失或不可读时会退回到 deliverable.get('content', '')，这意味着 Evaluator 可能评审摘要而非正式正文。

**当前状态**:
> 存在 fallback 到摘要的逻辑

**期望状态**:
> 强制从文件读取正文

**证据**:
- `autoBMAD\docuswarm\context\isolation.py:96`: `"title": deliverable.get("title", "Untitled"),`
- `autoBMAD\docuswarm\context\isolation.py:97`: `"summary": deliverable.get("content", "")[:200],  # 只取摘要`
- `autoBMAD\docuswarm\context\isolation.py:130`: `file_path = deliverable.get("file_path")`

**建议**: 禁止 Evaluator 退回到摘要作为正式评审正文，确保评审对象始终来自工具写盘后的正式文档

---

#### [LOW] P0-3-001: create_deliverable 已实现 metadata-first 返回

**验证状态**: [OK] verified

**问题描述**: create_deliverable 工具已写盘并返回 metadata，而非正文

**当前状态**:
> metadata-first 已实现

**期望状态**:
> 强制 metadata-only

**建议**: 已满足基本要求

---

### P1-1 相关发现

#### [HIGH] P1-1-002: shared_context 未进入 IndependentAgentInput

**验证状态**: [X] unverified

**问题描述**: IndependentAgentInput 当前未包含 shared_context 字段，导致即使 StateManager 写入 shared_context，也不会进入 agent 输入。

**当前状态**:
> shared_context 未接入 Agent 输入

**期望状态**:
> IndependentAgentInput 包含 shared_context

**证据**:
- `autoBMAD/docuswarm/node_execution/contracts.py:1983`: `class IndependentAgentInput(TypedDict):`

**建议**: 在 IndependentAgentInput 中添加 shared_context 字段，在 build_independent_input() 中显式渲染

---

#### [LOW] P1-1-004: StateManager.update_shared_context 已实现真实写库

**验证状态**: [OK] verified

**问题描述**: StateManager 已实现 update_shared_context 方法，支持 set/append/remove 操作和嵌套 key_path

**当前状态**:
> 持久化层已实现

**期望状态**:
> 完整运行时闭环

**证据**:
- `autoBMAD\docuswarm\storage\state_manager.py:480`: `async def update_shared_context(`

**建议**: 与工具层绑定完成闭环

---

#### [MED] P1-1-003: 恢复链路不会回填 shared_context

**验证状态**: [X] unverified

**问题描述**: PipelineState 和 create_initial_state 未声明/初始化 shared_context，恢复路径重建 state 时不会把 shared_context 放回去。

**当前状态**:
> shared_context 不在恢复链路

**期望状态**:
> resume/restart 恢复 shared_context

**证据**:
- `autoBMAD\docuswarm\pipeline\state.py:79`: `def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> P`
- `autoBMAD\docuswarm\pipeline\state.py:282`: `>>> state = create_initial_state("pipeline-1", {"task": "Build X"})`
- `autoBMAD\docuswarm\pipeline\state.py:316`: `current_state = create_initial_state(pipeline_id, {})`

**建议**: 在 PipelineState 中声明 shared_context，在 create_initial_state 中初始化

---

### P1-2 相关发现

#### [LOW] P1-2-001: docs_context 已固定为空列表

**验证状态**: [OK] verified

**问题描述**: NodeExecutionContextBuilder 当前固定 docs_context=[]，符合 docs-free 决策

**当前状态**:
> docs_context 已停用

**期望状态**:
> 完全移除 docs 相关代码

**建议**: 继续清理 docs 相关残余代码

---

#### [LOW] P1-2-003: README 仍把 docs/*.md 作为标准工作流示例

**验证状态**: [~] partial

**问题描述**: README 仍引用 docs/epics/EPIC-01.md、docs/proposal.md 作为标准工作流示例，与 docs-free 决策不一致

**当前状态**:
> 文档未同步

**期望状态**:
> 文档更新为 docs-free

**建议**: 更新 README，移除 docs/ 路径示例

---

### TEST 相关发现

#### [HIGH] TEST-001: 本轮重构几乎没有成体系的自动化回归测试

**验证状态**: [X] unverified

**问题描述**: 当前 tests 目录下未发现与重构目标直接对应的 source test 文件。缺失: test_node_execution_context.py, test_prompt_contract_builder.py, test_single_truth_deliverable.py, test_update_context_persistence.py, test_shared_context_cross_node.py, test_docs_free_boundary.py

**当前状态**:
> 强依赖人工审查与局部验证

**期望状态**:
> 完整测试护栏

**证据**:
- `autoBMAD/docuswarm/tests:0`: `Existing: None`

**建议**: 补上 prompt contract、single truth、update_context persistence、shared_context cross-node、docs-free boundary 的单元/集成测试

---

## 后续建议

### 建议的实施顺序

1. **先完成 P1-1 真闭环**
   - 为 UpdateContextTool 提供真实的 StateManager / pipeline_id 绑定机制
   - 把 shared_context 带入 IndependentAgentInput
   - 在 prompt builder 中显式渲染 shared_context
   - 在 resume/restart 路径恢复 shared_context

2. **再收口 P0-3 单一交付物真相**
   - 统一使用 summary，去掉 deliverable.content 的双重语义
   - 将 file_path / sha256 提升为强制字段
   - 禁止 Evaluator 退回到摘要作为正式评审正文
   - 限制下游链式上下文只传播 metadata + summary

3. **然后补完 P0-2 的 Evaluator 上下文**
   - 在 EvaluatorAgentInput 中加入原始上下文摘要
   - 让 Evaluator prompt 稳定出现'原始需求摘要'章节

4. **最后清理 P0-1 与 P1-2 的尾巴**
   - 视需要把状态层进一步收敛到 execution_context 主协议
   - 清理 README / CLI 中仍鼓励以 docs/*.md 作为标准入口的表述

5. **补测试**
   - 至少补上 prompt contract、single truth、update_context persistence、shared_context cross-node、docs-free boundary 的单元/集成测试


---

## TDD 测试驱动实施方案 (2026-03-17)

基于本研究报告的发现和建议，已制定详细的测试驱动实施方案：

### 核心文档

| 文档 | 描述 |
|------|------|
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md` | **TDD 主方案** - 完整的测试驱动实施指南，包含所有 Phase 的详细设计和测试模板 |
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-implementation-roadmap.md` | **实施路线图** - 4周执行计划、依赖关系和验收标准 |
| `../solution/2026-03-17-tdd-test-templates.py` | **测试模板** - 可直接使用的 pytest 测试代码 |

### Phase 详细计划

| Phase | 对应研究发现 | 计划文档 |
|-------|-------------|----------|
| Phase 1 | P1-1-001, P1-1-002, P1-1-003 | `../solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md` |
| Phase 2 | P0-3-002, P0-3-003, P0-3-004 | `../solution/2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md` |
| Phase 3 | P0-2-003 | `../solution/2026-03-17-phase3-p0-2-evaluator-context-tdd-execution-plan.md` |

### 实施顺序

```
Week 1: Phase 1 (P1-1) ──► Week 2: Phase 2 (P0-3) ──► Week 3: Phase 3 (P0-2) ──► Week 4: 测试补全
```

### 测试模板

测试模板已准备就绪，位于 `../solution/2026-03-17-tdd-test-templates.py`，包含：

- **Template 1**: UpdateContextTool 绑定测试 (Phase 1)
- **Template 2**: IndependentAgentInput shared_context 测试 (Phase 1)
- **Template 3**: ContextManager shared_context 测试 (Phase 1)
- **Template 4**: 单一交付物验证测试 (Phase 2)
- **Template 5**: Evaluator 禁止 fallback 测试 (Phase 2)
- **Template 6**: EvaluatorAgentInput 原始上下文测试 (Phase 3)
- **Template 7**: Prompt Contract Builder 测试 (Phase 3)
- **Template 8**: 集成测试模板
- **Template 9**: 回归测试模板

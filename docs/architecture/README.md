# DocuSwarm Architecture Alignment Index

## 2026-03-13 对齐说明

`docs/architecture/*` 中的多数文档描述了目标状态，但当前代码仍处于过渡态。  
从 2026-03-13 起，与上下文注入相关的理解应分成两层:

- "当前代码真实行为": 以 `docs/evaluation/*` 和 `docs/research/2026-03-13-context-injection-audit.md` 为准
- "推荐重构目标": 以 `docs/research/2026-03-13-*.md` 方案系列为准

## 重要决策更新 (2026-03-25)

### F5: Pipeline & Node Execution Convergence (P1)

**问题**: `pipeline` 与 `node_execution` 两个模块并行承载主语义，存在 deprecated fallback 路径和边界违规。

| 文档 | 说明 |
|------|------|
| [F5 TDD Implementation Plan](../solution/2026-03-25-f5-test-driven-implementation-plan.md) | 测试驱动实施方案 (3 Phase × 1周) |
| [F5 Research Report](../research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md) | 深度研究报告 |
| [F5 Design Spec](../research/2026-03-25-f5-unified-design-spec.md) | 统一设计规范 |

**关键变更**:
- `create_pipeline_graph(session_manager=None)` → `ValueError` (硬失败)
- 删除 `_create_default_node_executor()` 和 `create_enhanced_node_executor()`
- 强制使用 `PipelineAdapter` 作为唯一边界
- 状态转换责任移至 `PipelineAdapter`

**实施状态**: 🔄 Phase 1 In Progress

### TDD SDK Migration (P0 - CRITICAL)

当前存在严重的依赖漂移问题 (Drift Score 85/100)。

| 文档 | 说明 |
|------|------|
| [TDD SDK Migration](../solution/TDD-SDK-Migration-2026-03-25.md) | 测试驱动迁移方案 |
| [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md) | 依赖漂移深度研究 |

**关键信息**:
- 声明依赖: `claude-agent-sdk` ✅
- 实际使用: `kimi-agent-sdk` + `kaos.path` ❌
- 受影响文件: 7个 kimi + 3个 kaos
- 迁移进度: 0% → 目标 100%

### P0-2/P0-3 Legacy Code Retirement (P0 - CRITICAL)

**问题**: 系统存在多条执行主干和脆弱的同步/异步边界。

| 文档 | 说明 |
|------|------|
| [Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md) | 测试驱动退役方案 |
| [Deep Research Report](../research/2026-04-03-p0-2-p0-3-deep-research-report.md) | 问题深度研究 |

**关键信息**:
- **P0-2**: 两套 `create_node_executor`、两套图工厂 → **物理删除历史路径**
- **P0-3**: `await` 同步方法、`run_until_complete` 嵌套 → **统一契约**
- **原则**: 彻底删除、零兼容、测试先行
- **状态**: 🔄 In Progress

### P1-2 Config Semantics Unification (P1)

**问题**: 配置命名严重分裂，同时存在 `KIMI_API_KEY`、`ANTHROPIC_API_KEY`、`CLAUDE_API_KEY` 三种命名，架构层职责错位。

| 文档 | 说明 |
|------|------|
| [P1-2 Test-Driven Plan](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md) | 测试驱动实施方案 |
| [Deep Research Report](../research/2026-04-03-p1-2-config-semantics-analysis-report.md) | 配置语义深度研究报告 |

**关键信息**:
- **清理原则**: 无兼容层、主路径唯一、命名一致性、代码即文档
- **配置层** (`config.py`): 仅使用 `ANTHROPIC_API_KEY`，移除 `KIMI_*` 兼容
- **会话层** (`session_manager.py`): 统一从 `Config` 获取，移除 `_api_key`/`_base_url` 字段
- **别名移除**: `KimiSessionManager` 别名已移除，统一使用 `SessionManager`

**环境变量映射（最终状态）**:
| 旧配置 | 新配置 | 处理方式 |
|--------|--------|----------|
| `KIMI_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `KIMI_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `CLAUDE_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_MODEL_NAME` | `ANTHROPIC_MODEL_NAME` | 统一重命名 |

**状态**: ✅ Completed (Phase 10)

### P1-2 已移除

产品已决定工作流**完全不读取 `docs/`** 目录。因此：

- 所有 docs 相关读取/写入能力应进入**清理范围**，而非建设范围
- 不再推进 `ContextResolver` 和 `@path` 注入功能
- 架构文档中关于 docs 扩展的描述应被视为**待清理**而非待实现

### Deep Reform (2026-04-06) - 重大架构改革

基于 `docs/research/docuswarm-deep-reform` 系列研究，正在实施以下重大架构改革：

| 改革领域 | 核心变更 | 状态 |
|----------|----------|------|
| **技能引入** | Claude Agent SDK Skills 集成，混合方案实施 | 🔄 In Progress |
| **任务重构** | Analyst 从数据分析改为产品简介创建 | 🔄 In Progress |
| **文档约束** | 单/多文档创建约束机制 | 🔄 In Progress |
| **多文档支持** | architect/po 支持创建多份文档 | ⏳ Pending |
| **模板对齐** | BMAD 模板运行时接线修复 | ⏳ Pending |
| **实现缺口** | F3/F4/F5/F6/F7/F8 修复 | 🔄 In Progress |

**关键设计决策**:

1. **Skills 混合方案**: SDK原生discovery (`setting_sources: ["project"]`) + system prompt快速参考 + node.yaml whitelist控制
2. **Analyst 职责转变**: 从"Data Analyst"改为"Product Discovery Facilitator"，使用 `bmad-product-brief` skill
3. **文档约束三层实施**: node.yaml配置 → Validator检查 → Orchestrator追踪
4. **多文档向后兼容**: 采用包装方式，保持现有JSON结构

**参考文档**:
- [Deep Reform 研究目录](../research/docuswarm-deep-reform/README.md)
- [F3/F4/F5 实现缺口](../research/docuswarm-deep-reform/F3-F4-F5-implementation-gap-research-report.md)
- [F6/F7/F8 深度研究](../research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md)

### 推荐重构路径 (方案 C)

采用 `protocol-first, adapter-second` 策略:

1. **P0-1**: 定义统一的 `NodeExecutionContext`
2. **P0-2**: 让 `node.yaml` 真正进入 prompt (使用 `NodePromptContractBuilder`)
3. **P0-3**: 消除摘要/正式文档双轨 (工具写盘为唯一真相)
4. **P1-1**: 让 `update_context` 接入真实持久化

## 关键入口

- `01_SYSTEM_ARCHITECTURE.md`
- `02_AGENT_ARCHITECTURE.md`
- `03_PIPELINE_ARCHITECTURE.md`
- `04_STATE_ARCHITECTURE.md`
- `05_LLM_INTEGRATION.md`
- `06_CONTEXT_ISOLATION.md`

## 推荐配套阅读

1. `../evaluation/docuswarm-agent-context-injection-evaluation-2026-03-13.md`
2. `../research/2026-03-13-context-injection-audit.md`
3. `../research/2026-03-13-docuswarm-context-refactor-overview.md`
4. `../research/2026-03-17-docs-free-workflow-dependency-research.md`

## 目标架构摘要

```text
CLI / Orchestrator
  -> PipelineState.execution_context
  -> NodeExecutionContextBuilder
  -> DualAgentNode
      -> IndependentInput (from NodeExecutionContext)
      -> create_deliverable writes canonical file
      -> DeliverableArtifact metadata
      -> EvaluatorInput loads canonical file content
  -> StateManager persists metadata only
  -> shared_context persisted via update_context
  -> workflow never reads docs/
```

## TDD 测试驱动实施方案 (2026-03-17)

重构实施采用 **测试驱动开发 (TDD)** 方法，详细方案见：

| 文档 | 描述 |
|------|------|
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md` | TDD 主方案 - 完整实施指南 |
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-implementation-roadmap.md` | 实施路线图 - 4周执行计划 |
| `../solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md` | Phase 1: P1-1 update_context 持久化 |
| `../solution/2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md` | Phase 2: P0-3 单一交付物真相 |
| `../solution/2026-03-17-phase3-p0-2-evaluator-context-tdd-execution-plan.md` | Phase 3: P0-2 Evaluator 上下文补完 |

### 实施顺序
```
Phase 1 (P1-1) ──► Phase 2 (P0-3) ──► Phase 3 (P0-2) ──► Phase 4/5
Week 1            Week 2             Week 3             Week 4
```

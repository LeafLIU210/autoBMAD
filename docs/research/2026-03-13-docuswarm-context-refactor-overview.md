---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史概述文档，已被 F1-F8 决策体系取代。当前决策以 `docs/DECISIONS.md` 为准。
---

# DocuSwarm Context Refactor Overview

> Date: 2026-03-13 (已归档 2026-03-17)  
> Basis: `docs/evaluation/docuswarm-agent-context-injection-evaluation-2026-03-13.md` and `docs/research/2026-03-13-context-injection-audit.md`

## 1. Executive Summary

本轮重构建议遵循奥卡姆剃刀原则:

1. 不新增新的 Agent 类型。
2. 不先做全量 `node.yaml` 格式迁移。
3. 不先引入新的复杂中间件或事件总线。
4. 先把当前链路收敛成一条单一、可验证、可落盘、可审计的主链。

建议采用 `protocol-first, adapter-second` 策略:

- 先定义统一的 `NodeExecutionContext`
- 再让 `executor / DualAgentNode / IndependentAgent / EvaluatorAgent / tools / state` 全部围绕该协议对齐
- 对旧 `node.yaml` 做兼容适配，而不是先重写全部配置

## 2. 审计结论压缩

来自审计工具的高优先级结论:

- `F001/F002`: 节点配置已加载，但任务语义仍来自运行时序列化 state。
- `F003`: `DualAgentNode` 二次包装上下文，迫使 `IndependentAgent` 重新猜测结构。
- `F004`: `deliverable.content` 同时被当作摘要和正式文档，存在双轨真相。
- `F005`: `update_context` 目前是 no-op。
- `F006/F007`: docs 工具与 `ContextResolver` 路线不再继续推进；产品已决定工作流完全不读取 `docs/`，相关能力应转入清理范围。

额外重要事实:

- 当前 `autoBMAD/nodes/*/node.yaml` 仍是旧 schema。
- 但 `deliverable.required_sections` 仍然存在，可作为最小可用契约直接注入 prompt。

## 3. 推荐重构顺序

### P0-1: 收敛为单一上下文协议

目标: 消除字符串化、重复包装、隐式猜测。

对应报告:
- `2026-03-13-p0-single-context-protocol-plan.md` - 原始方案B计划
- `2026-03-13-p0-single-context-protocol-deep-research-report.md` - **深度研究报告** (新增)
- `2026-03-13-p0-single-context-protocol-implementation-design.md` - **实施设计文档** (新增)

**核心组件**:
- `NodeExecutionContextBuilder` - 构建统一上下文
- `NodeExecutionContext` - 跨层协议数据结构
- `ContextManager` - 裁剪为 Agent 特定输入

**设计文档**:
- [Architecture Document](../architecture.md)
- [Design Document](../design.md)

### P0-2: 让 node.yaml 真正进入 prompt

目标: 让 Independent/Evaluator 的输入边界重新回到“节点契约”。

对应报告:
- `2026-03-13-p0-node-prompt-injection-plan.md`

### P0-3: 消除摘要/正式文档双轨

目标: 工具写盘为唯一真相，状态层只存 metadata。

对应报告:
- `2026-03-13-p0-single-truth-deliverable-plan.md`

### P1-1: 让 update_context 接入 StateManager

目标: 让 agent 的上下文更新具备真实持久化语义。

对应报告:
- `2026-03-13-p1-update-context-persistence-plan.md`

### P1-2: 移除 docs 上下文扩展议题（已决策）

目标: 产品已决定工作流完全不读取 `docs/`，因此移除 `P1-2`，并将所有 docs 相关读取/写入能力视为待清理范围，而非待建设能力。

对应报告:
- `../evaluation/2026-03-17-p1-2-controlled-docs-context-strategy-evaluation.md`
- `2026-03-17-docs-free-workflow-dependency-research.md`

## 4. 方案比较

### 方案 A: 全量重写后一次性切换

优点:
- 文档和代码可以一次性对齐

缺点:
- 风险最高
- 难以定位回归来源
- 与当前仓库存在的大量文档漂移叠加后，实施成本过大

### 方案 B: 维持现状，仅修补局部 bug

优点:
- 改动小

缺点:
- 无法解决协议断裂
- 继续保留双轨真相和 no-op 工具
- 后续每次修复都会继续在错误协议上叠 patch

### 方案 C: 协议优先的渐进式收敛

优点:
- 改动最小但收益最大
- 能兼容当前旧 `node.yaml`
- 适合逐层验证

缺点:
- 需要短期接受“适配层存在”

推荐: 方案 C（整体重构路径）；但 `P1-2` 已按产品决策移除

## 5. 目标架构摘要

```text
CLI / Orchestrator
  -> PipelineState.execution_context
  -> NodeExecutionContextBuilder
  -> DualAgentNode
      -> IndependentInput
      -> create_deliverable writes canonical file
      -> DeliverableArtifact metadata
      -> EvaluatorInput loads canonical file content
  -> StateManager persists metadata only
  -> shared_context persisted via update_context
  -> workflow never reads docs/
```

## 6. 实施依赖

依赖顺序必须是:

1. 单一上下文协议 (P0-1)
2. prompt 注入 (P0-2) - 使用 `NodePromptContractBuilder`
3. 单一交付物真相 (P0-3)
4. `update_context` 持久化 (P1-1)

原因:

- 如果没有统一协议，`node.yaml` 无法稳定进入 prompt。
- 如果没有单一真相，`update_context` 会继续写入不可信的状态。
- 产品已决定工作流完全不读取 `docs/`，因此 docs 扩展策略不再是实施项，剩余相关代码与测试应进入审计和清理流程。

## 7. 验收标准

- 任一节点运行时，Independent prompt 中能稳定看到节点契约信息。
- Evaluator 评审对象始终来自工具写盘后的正式文档正文，而非摘要字段。
- pipeline state 不再保存完整 markdown 正文，仅保存 metadata。
- `update_context` 可真实写入并在下一节点读取。
- 工作流运行过程中不读取 `docs/`，所有执行产物只进入 `output/`。


## 8. TDD 测试驱动实施方案 (2026-03-17)

详细的测试驱动实施方案已制定，包含完整的测试模板和执行计划：

### 核心文档

| 文档 | 描述 |
|------|------|
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md` | **TDD 主方案** - 完整的测试驱动实施指南 |
| `../solution/2026-03-17-docuswarm-context-refactor-tdd-implementation-roadmap.md` | **实施路线图** - 4周执行计划与依赖关系 |
| `../solution/2026-03-17-tdd-test-templates.py` | **测试模板** - 可直接使用的 pytest 测试代码 |

### Phase 详细计划

| Phase | 目标 | 计划文档 |
|-------|------|----------|
| Phase 1 | P1-1 update_context 持久化真闭环 | `../solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md` |
| Phase 2 | P0-3 单一交付物真相收口 | `../solution/2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md` |
| Phase 3 | P0-2 Evaluator 上下文补完 | `../solution/2026-03-17-phase3-p0-2-evaluator-context-tdd-execution-plan.md` |

### 实施顺序

```
Week 1: Phase 1 (P1-1) ──► Week 2: Phase 2 (P0-3) ──► Week 3: Phase 3 (P0-2)
```

### 关键测试文件清单

```
tests/
├── unit/
│   ├── node_execution/test_contracts.py           # NodeExecutionContext
│   ├── tools/test_update_context.py               # UpdateContextTool
│   ├── context/test_isolation.py                  # ContextManager
│   ├── prompts/test_contract_builder.py           # NodePromptContractBuilder
│   └── llm/test_response_validation.py            # Single Truth
├── integration/
│   ├── test_shared_context_cross_node.py          # P1-1 集成
│   ├── test_single_truth_deliverable.py           # P0-3 集成
│   └── test_evaluator_original_context.py         # P0-2 集成
└── regression/
    └── test_context_refactor.py                   # 回归测试
```

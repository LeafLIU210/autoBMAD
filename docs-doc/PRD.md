# DocuSwarm Product Requirements Document (PRD)

**Version**: 5.0 (完全移除 kimi-agent-sdk)  
**Date**: 2026-03-02  
**Status**: PO Approved  
**Author**: Product Manager  

> **Migration Notice**: 项目已**完全移除** `kimi-agent-sdk`，使用 `claude-agent-sdk` + Kimi Code API。零向后兼容。详见 [迁移研究报告](../research/migration/README.md)。  

---

## 1. Executive Summary

### 1.1 Product Vision

DocuSwarm is a **Multi-Agent Document Orchestration System** that automates the BMAD (Breakthrough Method of Agile AI-driven Development) workflow through intelligent agent collaboration. The system leverages LangGraph for state management and Kimi K2.5 for LLM capabilities to deliver high-quality, context-isolated document generation across the software development lifecycle.

### 1.2 Value Proposition

| Stakeholder | Problem | Solution |
|-------------|---------|----------|
| **Development Teams** | Manual BMAD workflow execution is time-consuming | Node-driven execution with dual-agent quality control, automatic context chaining |
| **Product Managers** | Document quality varies, inconsistent outputs | Evaluator Agent ensures standardized quality thresholds per node |
| **Architects** | Context contamination between phases | Three-layer context isolation prevents information leakage |

### 1.3 Key Differentiators

1. **Dual-Agent Pattern**: Independent Agent (creation) + Evaluator Agent (review) ensures quality
2. **Context Isolation**: Three-layer security prevents evaluator bias from creator reasoning
3. **Occam's Razor Design**: Simplified architecture reduces development time by 30-45%
4. **BMAD Alignment**: Full methodology compliance with automated persona execution

---

## 2. Product Overview

### 2.1 Product Scope

**In Scope (MVP)**:
- **Pipeline-first execution**: Sequential execution of 5 nodes: `analyst` → `pm` / `ux` (parallel) → `architect` → `po`
- Dual-agent pattern with context isolation per node
- Automatic context chaining: predecessor node deliverables auto-injected
- SQLite-based state persistence with WAL mode (`node_runs` table)
- Kimi K2.5 LLM integration (via claude-agent-sdk + Kimi Code API)
- Max 3 iterations per node with escalation
- Node run history and resume capability

**Out of Scope (Deferred to Phase 2)**:
- DAG-based parallel execution
- RAG knowledge retrieval system
- ~~MCP protocol integration~~ → **已完成 SDK MCP 迁移** (FastMCP → SDK MCP，解决 `TypeError: Object of type FastMCP is not JSON serializable` 兼容性问题。详见 [FastMCP SDK 兼容性研究报告](../research/fastmcp-sdk-compatibility-issue.md) 和 [SDK MCP 迁移方案 A](../research/sdk-mcp-migration-plan-a.md))
- Multi-provider fallback
- ~~Third Questioner Agent~~ → **已在重构计划中移除** (详见 [TDD重构方案](../solution/README.md))

### 2.4 Architecture Evolution (Refactoring Plan)

**Current Focus**: Systematic refactoring to address technical debt and align with 12-Factor Agents methodology.

| Phase | Focus | Key Deliverables | Status |
|-------|-------|------------------|--------|
| **Phase 1 (P0)** | Core Module Refactoring | [TDD-01](../solution/TDD-01-CheckpointManager-Refactor.md), [TDD-02](../solution/TDD-02-ContextValidator-Refactor.md) | ✅ Completed |
| **Phase 2 (P1)** | SDK Migration & Feature Enhancement | [TDD-03](../solution/TDD-03-ToolResultExtractor-Refactor.md), [TDD-04](../solution/TDD-04-ContextResolver-Refactor.md), [TDD-05](../solution/TDD-05-SDKWrapper-Refactor.md) | ✅ Completed |
| **Phase 3 (P2)** | SDK Complete Removal | [迁移研究报告](../research/migration/README.md) - kimi-agent-sdk 完全移除 | ✅ Completed |
| **Phase 4 (P3)** | **SDK TDD Migration** | **[TDD SDK Migration](../solution/TDD-SDK-Migration-2026-03-25.md)** - 依赖漂移修复与测试驱动迁移 | 🔄 **In Progress** |
| **Phase 5 (P4)** | **Single Context Protocol** | **引入 NodeExecutionContext 统一上下文协议** | ⏳ **Pending** |
| **Phase 6 (P5)** | **F2 State Consistency** | **[F2 Test-Driven Implementation](../solution/2026-03-25-f2-test-driven-implementation-plan.md)** - state_json 单一真相源收口 | 🔄 **In Progress** |
| **Phase 7 (P6)** | **2026-03-28 Refactor Implementation** | **[Test-Driven Implementation](../solution/refactor-2026-03-28-test-driven-implementation.md)** - 5项关键要求实施 | 🔄 **In Progress** |
| **Phase 8 (P7)** | **P0 Runtime Consumption Fix** | **[P0 Runtime Consumption Test-Driven Plan](../solution/2026-04-03-p0-runtime-consumption-test-driven-plan.md)** - 运行时配置消费修复与测试驱动验证 | ✅ **Completed** |
| **Phase 9 (P8)** | **P0-2/P0-3 Legacy Code Retirement** | **[Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md)** - 旧执行主干彻底退役与同步/异步契约统一 | 🔄 **In Progress** |
| **Phase 10 (P9)** | **P1-2 Config Semantics Unification** | **[P1-2 Test-Driven Plan](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md)** - 配置语义统一 (Kimi/Claude 命名债清理) | 🔄 **In Progress** |
| **Phase 11 (P10)** | **Phase A/B Technical Debt Resolution** | **[Phase A/B Test-Driven Solution](../solution/phase_a_b_test_driven_solution_plan.md)** - 异步边界修复与测试缺口补充 | 🔄 **Critical** |
| **Phase 12 (P11)** | **Finding B: Compatibility Layer Cleanup** | **[Finding B TDD Plan](../solution/2026-04-04-finding-b-compatibility-cleanup-tdd-plan.md)** - 完全移除所有兼容层代码，零容忍遗留 | 🔴 **Priority** |
| **Phase 13 (P12)** | **Reference Docs Preload (Step 2)** | **[Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)** - 引用文档自动预加载功能 | 🔄 **In Progress** |
| **Phase 14 (P13)** | **SDK MCP 格式迁移** | **[Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md)** - FastMCP → SDK MCP 迁移，解决 `TypeError: Object of type FastMCP is not JSON serializable` 兼容性问题 | 🔴 **Critical** |
| **Phase 15 (P14)** | **Kimi Message Extraction Fix** | **[Message Extraction TDD Plan](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md)** - 修复 SDK 消息类型判断问题，使用 `isinstance()` 替代 `getattr()` | 🔴 **P0 Critical** |

#### Phase 15 (P14) - Kimi Message Extraction Fix

**核心目标**: 修复 `claude_agent_sdk v0.1.68` 消息类型判断问题，解决 `no_text_extracted` 导致 pipeline 完全失效的问题。

**问题背景**: 代码错误地假设 SDK 消息对象有 `role` 属性，但 `AssistantMessage`/`TextBlock` 等类型根本没有这些字段，导致所有消息被过滤，返回空列表。

| 优先级 | 问题 | 根因 | 修复方式 | 测试覆盖 |
|--------|------|------|----------|----------|
| **P0** | `no_text_extracted` 警告 | `AssistantMessage` 无 `role` 属性，`getattr(msg, "role", "")` 返回空字符串 | 使用 `isinstance(msg, AssistantMessage)` 判断 | `tests/llm/test_response_message_extraction.py` |
| **P0** | `single_prompt` 返回空列表 | `_message_to_dict()` 因 `role is None` 过滤所有消息 | 使用 `isinstance()` 判断消息类型，手动设置 role | `tests/llm/test_session_manager_message_conversion.py` |
| **P1** | 文本内容无法提取 | `TextBlock` 无 `type` 属性，`getattr(item, "type", "")` 无法匹配 | 使用 `isinstance(item, TextBlock)` 判断 | `tests/llm/test_response_message_extraction.py` |
| **P2** | Pipeline 静默挂起 | Agent 层消息处理同样依赖 `role` 属性 | 统一使用 `SessionManager._message_to_dict()` 转换 | `tests/agents/test_independent_agent_message_handling.py` |

**修复原则**:
1. **使用 `isinstance()` 类型检查**: 替代 `getattr(msg, "role", "")`，与官方文档示例一致
2. **保持向后兼容**: 旧格式（带 role 属性的 dict）消息仍被正确处理
3. **统一消息转换**: Agent 层统一使用 `SessionManager._message_to_dict()` 进行消息转换

**关键代码变更**:
```python
# 修复前 (错误)
msg_role = getattr(msg, "role", "")
if msg_role != "assistant":
    continue  # AssistantMessage 没有 role，被错误跳过

# 修复后 (正确)
from claude_agent_sdk.types import AssistantMessage
if isinstance(msg, AssistantMessage):
    role = "assistant"
elif isinstance(msg, UserMessage):
    role = "user"
# ... 正确处理
```

**验收标准**:
- ✅ `extract_text_from_messages` 能正确处理无 `role` 属性的 `AssistantMessage`
- ✅ `_message_to_dict` 能正确识别 `AssistantMessage` 并设置 `role="assistant"`
- ✅ `single_prompt` 返回非空消息列表（正常响应时）
- ✅ Pipeline 完整执行后生成预期的 `.md` 交付物
- ✅ 无 `no_text_extracted` warning（正常响应时）

**参考文档**:
- [Root Cause Analysis](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md) - 根因分析报告
- [Test-Driven Plan](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md) - 测试驱动修复方案

#### Phase 9 (P8) - P0-2/P0-3 Legacy Code Retirement

**核心目标**: 彻底删除历史执行主干，统一同步/异步契约，零向后兼容。

| 问题 | 描述 | 修复方式 | 测试覆盖 |
|------|------|----------|----------|
| **P0-2 执行主干分叉** | 系统存在两套 `create_node_executor` 和图构建工厂 | **物理删除** `nodes/dual_agent.py` 中的旧实现、`node_execution/graph.py`、`node_execution/flow.py` | `tests/architecture/test_p0_2_execution_trunk_retirement.py` |
| **P0-3 同步/异步契约不一致** | `await` 同步方法、`run_until_complete` 嵌套、`_run_async` 桥接 | 修复 `chaining.py` 非法 `await`、移除 `pipeline/graph.py` 自举逻辑、删除 `_run_async`、统一 `StateManager` 为同步接口 | `tests/architecture/test_p0_3_async_sync_contract.py` |

**核心原则**:
1. **彻底删除、零兼容**: 旧代码物理删除，不存在 `compat/` 或 `legacy/` shim 层
2. **测试先行**: 所有变更遵循 Red-Green-Refactor，新增架构守护测试
3. **单主干原则**: 全代码库只允许存在一套 `create_node_executor` (`node_execution/executor.py`)

**验收标准**:
- ✅ 旧实现不可访问（`ImportError`/`AttributeError`）
- ✅ 非法 `await` 被 AST 扫描禁止
- ✅ `pipeline/graph.py` 无 `run_until_complete`、无 `_run_async`
- ✅ `StateManager` 全同步接口（上层 async 代码通过 `asyncio.to_thread()` 桥接）
- ✅ 架构测试数量 >= 15

**参考文档**:
- [P0-2/P0-3 Deep Research](../research/2026-04-03-p0-2-p0-3-deep-research-report.md) - 问题深度研究
- [Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md) - 测试驱动退役方案

#### Phase 10 (P9) - P1-2 Config Semantics Unification

**核心目标**: 统一配置命名，消除 `KIMI_API_KEY`/`CLAUDE_API_KEY`/`ANTHROPIC_API_KEY` 混用问题，建立单一真相源。

| 问题 | 描述 | 修复方式 | 测试覆盖 |
|------|------|----------|----------|
| **配置命名分裂** | `config.py` 使用 `KIMI_API_KEY`，`session_manager.py` 使用 `CLAUDE_API_KEY`，文档使用 `ANTHROPIC_API_KEY` | **统一使用 `ANTHROPIC_*`**：`config.py` 仅读取 `ANTHROPIC_API_KEY`，移除 `KIMI_*` 和 `CLAUDE_*` 兼容层 | `tests/unit/docuswarm/test_config_semantics_unified.py` |
| **未消费字段残留** | `SessionManager._api_key`、`_base_url` 被赋值但未被消费 | **移除未消费字段**：`SessionManager` 统一从 `Config` 获取凭证，不再直接读取环境变量 | `tests/unit/docuswarm/llm/test_session_manager_semantics.py` |
| **配置来源不一致** | `dual_agent.py` 直接读取 `ANTHROPIC_API_KEY` 但传入期望 `KIMI_API_KEY` 的 `Config` | **统一配置链路**：`_get_config()` 使用 `Config.from_env_and_yaml()`，单一入口 | `tests/unit/docuswarm/nodes/test_dual_agent_config.py` |

**环境变量映射（最终状态）**:
| 旧配置 | 新配置 | 处理方式 |
|--------|--------|----------|
| `KIMI_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `KIMI_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `CLAUDE_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_MODEL_NAME` | *(已移除)* | 模型由 API 网关统一管理，详见 [Session Execution Failure Solution](../research/session-execution-failure-solution.md) |

**清理原则**:
1. **无兼容层原则**: 不再保留任何兼容性别名或兼容层
2. **主路径唯一原则**: 每个功能只有一个主路径入口
3. **命名一致性原则**: 统一使用 `ANTHROPIC_*` 和 `SessionManager`
4. **代码即文档原则**: 删除的代码比废弃标记更清晰

**验收标准**:
- ✅ 仅 `ANTHROPIC_API_KEY` 被读取，`KIMI_API_KEY`/`CLAUDE_API_KEY` 不再支持
- ✅ 错误消息提示 `ANTHROPIC_API_KEY is required`
- ✅ `SessionManager` 不再直接读取环境变量，统一从 `Config` 获取
- ✅ `dual_agent._get_config()` 使用统一 `Config.from_env_and_yaml()`
- ✅ `KimiSessionManager` 别名已移除，所有导入改为 `SessionManager`
- ✅ 新增测试覆盖率 > 90%

**参考文档**:
- [P1-2 Deep Research](../research/2026-04-03-p1-2-config-semantics-analysis-report.md) - 配置语义深度研究报告
- [P1-2 Test-Driven Plan](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md) - 测试驱动方案

#### Phase 11 (P10) - Phase A/B Technical Debt Resolution

**核心目标**: 修复确定性运行时缺陷，恢复测试可信度，统一文档/配置口径。

基于 [技术债务审计报告](../evaluation/2026-04-04-docuswarm-tech-debt-audit.md)，分两阶段修复：

**Phase A (1周止血)**:

| 问题 | 严重性 | 描述 | 修复方式 | 测试覆盖 |
|------|--------|------|----------|----------|
| **P0-1** | 🔴 Critical | `start_pipeline()` 内部使用 `asyncio.run()` 导致运行时错误 | 改为 `await` | `tests/architecture/test_p0_1_asyncio_run_regression.py` |
| **P0-2** | 🔴 Critical | `PipelineService._run_async()` bridge 违反架构契约 | 移除 bridge，改为 `async def` | `tests/architecture/test_p0_3_async_sync_contract.py` |
| **P1-1** | 🟠 High | `DualAgentNode` 中 `escalate()` 未 `await` | 添加 `await` | `tests/architecture/test_p1_1_escalation_await_regression.py` |
| **P1-3** | 🟠 High | 测试环境权限问题阻断全量测试 | 配置 `basetemp` | `tests/architecture/test_environment_setup.py` |

**Phase B (1个迭代收口)**:

| 问题 | 严重性 | 描述 | 修复方式 | 测试覆盖 |
|------|--------|------|----------|----------|
| **P1-2** | 🟠 High | 文档/配置口径漂移 (`KIMI_*` vs `ANTHROPIC_*`) | 更新 README.md, CONFIGURATION.md | `tests/architecture/test_documentation_consistency.py` |
| **P1-3** | 🟠 High | 热点模块覆盖率过低 | 补充冒烟测试 | `tests/smoke/test_*.py` |

**环境变量最终状态**:
| 变量 | 说明 | 必需 |
|------|------|------|
| `ANTHROPIC_API_KEY` | LLM API 密钥 | ✅ 必需 |
| `ANTHROPIC_BASE_URL` | API Base URL | ❌ 可选，默认 `https://api.kimi.com/coding/` |

**关键修复代码**:
```python
# P0-1: orchestrator.py
# 修复前: _ = asyncio.run(self._state_manager.update_pipeline_state(...))
# 修复后: _ = await self._state_manager.update_pipeline_state(...)

# P0-2: pipeline_service.py
# 删除: def _run_async(coro): ...
# 修改: async def cancel(self, ...): ...
#       return await self._state_manager.update_pipeline_state(...)

# P1-1: dual_agent.py
# 修复前: self.escalation_handler.escalate(...)
# 修复后: await self.escalation_handler.escalate(...)
```

**验收标准**:
- ✅ `asyncio.run()` 在 async def 中调用数为 0
- ✅ `_run_async` bridge 不存在
- ✅ `escalate()` 调用全部被 `await`
- ✅ 文档中 `KIMI_*` 引用数为 0
- ✅ 冒烟测试 4 个全部通过
- ✅ 架构测试 100% 通过
- ✅ 热点模块覆盖率 >= 40%

**参考文档**:
- [Phase A/B Research Report](../research/phase_a_b_technical_debt_research_report.md) - 深度研究报告
- [Phase A/B TDD Solution](../solution/phase_a_b_test_driven_solution_plan.md) - 测试驱动方案
- [Phase A/B TDD Execution Guide](../solution/TDD_EXECUTION_GUIDE.md) - 快速执行参考

#### Phase 13 (P12) - Reference Docs Preload (Step 2)

**核心目标**: 实现 `docs_context` 字段的自动填充，让 DocuSwarm Agent 无需主动调用工具即可直接获得 context file 中引用的所有支撑文档内容。

**背景**: 基于 [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md)，决定采用**步骤二方案**（预加载注入）而非依赖 Agent 主动调用工具。

| 改动文件 | 改动类型 | 说明 |
|----------|----------|------|
| `context_builder.py` | 新增 `_resolve_reference_docs()` | 递归扫描 `docs/` 目录，提取并读取引用文档 |
| `contract_builder.py` | 修改 `_build_context_section()` | 渲染 `docs_context` 到 Agent 提示词 |
| `executor.py` | 修改 `build()` 调用 | 传递 `repo_root` 参数 |

**引用文档提取规则**:
- 提取反引号格式 `` `filename.md` `` 和裸文件名 `filename.md`
- 支持扩展名: `.md`, `.txt`, `.yaml`, `.yml`, `.json`
- 递归搜索 `docs/` 及所有子目录
- 同名文件取路径最浅的版本
- 内容超过 10,000 字符自动截断

**数据流**:
```
bubble-sort-context.md (引用 algorithm-spec.md)
    │
    ▼ _resolve_reference_docs()
    ┌─────────────────────────────┐
    │ 1. 正则提取文件名            │
    │ 2. 递归搜索 docs/           │
    │ 3. 读取内容（截断保护）      │
    └─────────────────────────────┘
    │
    ▼ NodeExecutionContext
    docs_context: [{"filename": "...", "content": "..."}]
    │
    ▼ ContractBuilder
    user_prompt 包含 "## 引用文档" 章节
```

**验收标准**:
- ✅ `docs_context` 正确填充所有引用文档
- ✅ ContractBuilder 正确渲染引用文档章节
- ✅ 单元测试覆盖率 > 90%
- ✅ 集成测试通过 Bubble Sort 场景

**参考文档**:
- [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md)
- [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)

#### Phase 16 (P15) - DocuSwarm Deep Reform

**核心目标**: 基于 `docs/research/docuswarm-deep-reform` 系列研究，实施 DocuSwarm 深度改革，包括技能引入、节点任务重构、文档创建约束、多文档支持等关键架构改进。

**改革范围**:

| 领域 | 改革内容 | 相关文档 |
|------|----------|----------|
| **技能引入** | Claude Agent SDK Skills 集成 | `01-skills-introduction-mechanism.md` |
| **任务重构** | Analyst 节点任务语义重构 | `02-node-task-skill-mapping.md` |
| **文档约束** | 单/多文档创建约束机制 | `03-document-creation-constraints.md` |
| **工具权限** | Shared Context 更新机制 | `04-tool-permissions-configuration.md`, `05-shared-context-update-mechanism.md` |
| **摘要 Agent** | 引用文档摘要预生成 | `06-summary-agent-design.md`, `07-docs-context-persistence.md` |
| **实现缺口** | F3/F4/F5/F6/F7/F8 修复 | `F3-F4-F5-*.md`, `F6-F7-F8-*.md` |

**关键改革点**:

1. **技能引入机制 (F1/F6/F7)**:
   - SDK原生discovery + system prompt快速参考 + node.yaml whitelist控制
   - 新增 `NodeSkillsConfig` 配置类
   - SessionManager 启用 `setting_sources: ["project"]` 和 `"Skill"` 工具
   - `SkillInjector` 构建技能快速参考注入提示词

2. **节点任务重构 (F7)**:
   - Analyst: `create-business-analysis-report` → `create-product-brief`
   - Persona更新: name="Mary", role="Strategic Business Analyst & Product Discovery Expert"
   - 所有节点添加 `task.skill_ref` 和 `tools.skills.whitelist`

3. **文档创建约束 (F3)**:
   - 单文档约束: analyst/pm/ux `max_deliverables: 1`
   - 多文档支持: architect/po 支持2-5份文档
   - `CreateDeliverableParams` 扩展: `document_index`, `document_total`, `document_type`
   - Validator 添加 `max_deliverables` 规则检查

4. **实现缺口修复**:
   - F3: MCP Schema 暴露 multi-document 参数，支持多文档存储
   - F4: `docs_context_summary` 传递链修复，3处断点修复
   - F5: `SummaryAgent` 返回类型统一为 `list[dict]`
   - F6: `update_context` 工具 MCP 暴露链路修复
   - F7: Analyst 任务语义重构
   - F8: 模板对齐运行时接线修复

**实施路线图**:

| 阶段 | 内容 | 工作量 | 状态 |
|------|------|--------|------|
| **Phase 1** | 技能引入基础设施 | 2天 | ⏳ Pending |
| **Phase 2** | Analyst 任务重构 | 1天 | ⏳ Pending |
| **Phase 3** | 单文档约束实施 | 1周 | ⏳ Pending |
| **Phase 4** | 多文档支持 | 2周 | ⏳ Pending |
| **Phase 5** | F3/F4/F5/F6/F7/F8 修复 | 1周 | ⏳ Pending |
| **Phase 6** | 集成测试与验证 | 1周 | ⏳ Pending |

**验收标准**:
- ✅ Skills 机制正常工作，Agent 可调用 BMAD Skills
- ✅ Analyst 节点正确执行 `create-product-brief` 任务
- ✅ 单文档约束有效，多文档支持正常工作
- ✅ F3-F8 实现缺口全部修复
- ✅ 所有节点端到端测试通过

**参考文档**:
- [Deep Reform 研究目录](../research/docuswarm-deep-reform/README.md)
- [执行摘要](../research/docuswarm-deep-reform/REPORT_SUMMARY.md)
- [F3/F4/F5 实现缺口研究](../research/docuswarm-deep-reform/F3-F4-F5-implementation-gap-research-report.md)
- [F6/F7/F8 深度研究](../research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md)

#### Phase 12 (P11) - Finding B: Compatibility Layer Cleanup

**核心目标**: 完全移除所有兼容层代码，实现零容忍遗留，统一 API 入口。

基于 [Finding B 深度研究报告](../research/2026-04-04-finding-b-compatibility-layer-deep-dive.md)，清理以下兼容层：

**P0 - 立即清理（主路径高风险）**:

| 兼容层 | 位置 | 清理方式 | 替代方案 |
|--------|------|----------|----------|
| **SessionManager legacy 参数** | `llm/session_manager.py` | **完全移除** `api_key`, `base_url`, `allowed_dirs` 参数 | 统一使用 `config` + `tool_permissions` |
| **DualAgentNode legacy 执行链** | `nodes/dual_agent.py` | **完全移除** `execute()` 方法及桥接方法 | 统一使用 `execute_with_context()` |

**P1 - 近期清理（中风险）**:

| 兼容层 | 位置 | 清理方式 | 替代方案 |
|--------|------|----------|----------|
| **Validator 兼容参数** | `context/validator.py` | **完全移除** `node_id` 参数 | 直接使用 `context` 参数 |
| **StateManager state 字段冗余** | `storage/state_manager.py` | **完全移除** 冗余 `state` 字段 | 使用扁平化字段 |

**P2 - 计划清理（低风险）**:

| 兼容层 | 位置 | 清理方式 |
|--------|------|----------|
| **Tools function-style API** | `tools/*.py` | **完全移除** 函数式 API |
| **SDK Adapter 别名** | `tools/sdk_adapter.py` | **完全移除** `adapt_to_sdk`/`adapt_from_sdk` |
| **兼容异常类** | `exceptions.py` | **完全移除** `AgentError`/`ValidationError` 兼容类 |
| **CLI 命令别名** | `cli/main.py` | **完全移除** `list-pipelines` 别名 |
| **Node Loader facade** | `nodes/loader.py` | **完全移除** re-export facade |

**核心原则**:
1. **零容忍原则**: 不保留 deprecation 警告，直接移除代码
2. **零容忍遗留**: 所有标记为 deprecated/legacy/compatibility 的代码必须完全移除
3. **单一入口原则**: 每个功能只有一个主路径入口
4. **测试先行**: 所有清理遵循 TDD 流程（红→绿→重构）

**验收标准**:
- ✅ `grep -r "deprecated" autoBMAD/docuswarm --include="*.py"` 返回空结果
- ✅ `grep -r "backward compatibility" autoBMAD/docuswarm --include="*.py"` 返回空结果
- ✅ `grep -r "_legacy_" autoBMAD/docuswarm --include="*.py"` 返回空结果
- ✅ SessionManager 无 `api_key`/`base_url`/`allowed_dirs` 参数
- ✅ DualAgentNode 无 `execute()` 方法
- ✅ 所有单元测试通过，新增兼容性守护测试

**参考文档**:
- [Finding B Deep Research](../research/2026-04-04-finding-b-compatibility-layer-deep-dive.md) - 深度研究报告
- [Finding B TDD Plan](../solution/2026-04-04-finding-b-compatibility-cleanup-tdd-plan.md) - 测试驱动方案

#### Phase 14 (P13) - SDK MCP 格式迁移

**核心目标**: 将 FastMCP 格式的 MCP 服务器迁移到 SDK MCP 格式，解决 `TypeError: Object of type FastMCP is not JSON serializable` 兼容性问题。

**问题背景**:
- **错误现象**: `ClaudeSDKClient.connect()` 调用期间抛出 `TypeError: Object of type FastMCP is not JSON serializable`
- **根因**: Claude Agent SDK 使用子进程模式与 Claude Code CLI 通信，配置需要 JSON 序列化，但 FastMCP 对象不可序列化
- **影响**: 所有使用 MCP 工具的节点执行失败，流水线完全阻塞

**迁移范围**:

| 文件 | 当前格式 | 目标格式 | 状态 |
|-----|---------|---------|------|
| `tools/file_tools.py` | FastMCP | SDK MCP | ⏳ Pending |
| `tools/search_tools.py` | FastMCP | SDK MCP | ⏳ Pending |
| `llm/tool_filter.py` | 返回 FastMCP 列表 | 返回 SDK MCP dict | ⏳ Pending |
| `llm/session_manager.py` | 使用 FastMCP | 使用 SDK MCP | ⏳ Pending |

**技术变更**:

```python
# 迁移前 (FastMCP)
from mcp.server.fastmcp import FastMCP
server = FastMCP(f"mcp__docuswarm-files-{node_id}")
@server.tool(name=f"{server.name}__read_document")
async def mcp_read_document(path: str) -> str:
    return str(result.result)
return server  # FastMCP 对象，无法 JSON 序列化

# 迁移后 (SDK MCP)
from claude_agent_sdk import create_sdk_mcp_server, tool
@tool('read_document', 'Read a document', {'path': str})
async def read_document_tool(args):
    return {'content': [{'type': 'text', 'text': str(result.result)}]}
return create_sdk_mcp_server(
    name=f"docuswarm-files-{node_id}",
    version="1.0.0",
    tools=[read_document_tool]
)  # dict 类型，SDK 内部处理序列化
```

**工具命名约定变更**:

| 组件 | FastMCP (旧) | SDK MCP (新) |
|-----|-------------|-------------|
| Server name | `mcp__docuswarm-files-{node_id}` | `docuswarm-files-{node_id}` |
| Tool name | `mcp__docuswarm-files-analyst__read_document` | `read_document` |
| MCP 工具全名 | `mcp__mcp__...` (重复前缀) | `mcp__docuswarm-files-{node_id}__read_document` |

**验收标准**:
- ✅ `create_file_read_server()` 返回 `dict` 类型 (不是 FastMCP 对象)
- ✅ `create_search_server()` 返回 `dict` 类型
- ✅ `ClaudeSDKClient.connect()` 调用成功，无 JSON 序列化错误
- ✅ 工具命名符合 SDK 约定: `mcp__{server_name}__{tool_name}`
- ✅ 26项测试全部通过 (12单元测试 + 5集成测试 + 3端到端测试 + 6兼容性测试)

**参考文档**:
- [FastMCP SDK 兼容性研究报告](../research/fastmcp-sdk-compatibility-issue.md) - 问题根因分析
- [SDK MCP 迁移方案 A](../research/sdk-mcp-migration-plan-a.md) - 详细迁移方案
- [Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md) - 测试驱动迁移方案

#### Phase 8 (P7) - P0 Runtime Consumption Fix

基于运行时配置消费链路评估报告，完成5个P0级问题的修复与测试驱动验证：

| 问题 | 描述 | 修复文件 | 测试覆盖 |
|------|------|----------|----------|
| **MCP Server Key 命名冲突** | SessionManager 使用与 NodeToolFilter 一致的命名规范 | `session_manager.py` | `tests/unit/llm/test_session_manager_mcp_keys.py` |
| **NodeToolPermissions 传递丢失** | 完整传递 `allowed_builtin_tools` 到运行时 | `session_manager.py`, `independent.py` | `tests/unit/agents/test_independent_agent_permissions.py` |
| **目录解析基准错误** | 使用仓库根目录而非 autoBMAD/ 子目录 | `independent.py`, `executor.py` | `tests/unit/agents/test_directory_resolution.py` |
| **Evaluator 阈值配置未消费** | 从节点 evaluator.yaml 加载阈值 | `evaluator.py` | `tests/unit/agents/test_evaluator_threshold_consumption.py` |
| **max_iterations 未从配置注入** | 从节点配置加载 max_iterations | `dual_agent.py` | `tests/unit/nodes/test_dual_agent_max_iterations.py` |

**核心目标**:
1. **配置即行为**: 运行时消费的阈值、权限、迭代次数必须与配置文件完全一致
2. **单一真相源**: `NodeLoader` 作为配置唯一入口，所有运行时组件必须消费其输出
3. **无回归风险**: 已修复的 5 个 P0 问题必须有自动化测试守护

**验收标准**:
- ✅ 5个P0问题每个至少有3个单元测试守护
- ✅ 集成测试 `test_runtime_config_consistency.py` 对 architect 和 analyst 节点全部通过
- ✅ 运行时行为与 `node.yaml` / `evaluator.yaml` 配置完全一致

**参考文档**:
- [P0 Runtime Consumption Research](../research/2026-04-03-p0-runtime-consumption-fix-research-report.md) - 修复研究报告
- [P0 Test-Driven Plan](../solution/2026-04-03-p0-runtime-consumption-test-driven-plan.md) - 测试驱动方案

#### Phase 7 (P6) - 2026-03-28 Refactor Implementation

基于审查报告的深度重构实施，包含5项关键要求：

| 要求 | 描述 | 状态 | 参考 |
|------|------|------|------|
| **REQ-001** | Claude Agent SDK system_prompt preset/append 高级结构 | 🔄 In Progress | [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#1-claude-agent-sdk-system_prompt-presetappend-高级结构) |
| **REQ-002** | node.yaml evaluator 内联引用段 | 🔄 In Progress | [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#2-nodeyaml-evaluator-内联引用段) |
| **REQ-003** | 主执行链 SessionManager 接入 node_id 和 tool_permissions | 🔄 In Progress | [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#3-主执行链-sessionmanager-接入-node_id-和-tool_permissions) |
| **REQ-004** | 修复 tests/__init__.py 语法错误 | 🔄 In Progress | [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#4-修复-testsinitpy-语法错误) |
| **REQ-005** | NodeDeliverableConfig 扩展字段 (template_title/output_filename/format_hints) | 🔄 In Progress | [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#5-nodedeliverableconfig-扩展字段) |

**设计原则（拒绝向后兼容）**:
- 不保留字符串形式的 system_prompt 直接赋值
- 所有调用方必须适配新的 dict 格式或接受自动包装
- node.yaml 作为唯一配置真相源
- 工具权限从 node.yaml 读取并注入主执行链

**参考文档**:
- [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md) - 详细实施研究
- [Test-Driven Implementation](../solution/refactor-2026-03-28-test-driven-implementation.md) - TDD 实施方案
- [Implementation Auditor](../../tools/refactor_implementation_auditor.py) - 自动化验证工具

**Key Architectural Changes**:
1. **SDK Migration**: kimi-agent-sdk → claude-agent-sdk via Kimi Code API ([TDD-05](../solution/TDD-05-SDKWrapper-Refactor.md)) ✅ Completed
2. **Question Agent Removal**: Simplifying system by removing QuestionHandler ([Part 2](../research/DocuSwarm-重构详细研究报告-Part2.md) 第2节) ✅ Completed
3. **Pure Tool Output Mode**: Eliminating JSON parsing from LLM responses ([TDD-03](../solution/TDD-03-ToolResultExtractor-Refactor.md)) ✅ Completed
4. **@ Path Context Injection**: Enabling document references in context files ([TDD-04](../solution/TDD-04-ContextResolver-Refactor.md)) ✅ Completed
5. **SDK Complete Removal**: Complete removal of kimi-agent-sdk dependencies per [Occam's Razor principle](../research/migration/README.md) - ✅ Completed
6. **SDK TDD Migration**: Test-driven migration from kimi-agent-sdk to claude-agent-sdk addressing dependency drift ([TDD-SDK-Migration](../solution/TDD-SDK-Migration-2026-03-25.md), [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md)) - 🔄 **In Progress**
7. **Single Context Protocol**: Introducing `NodeExecutionContext` as the unified context contract across executor → DualAgentNode → Agents layer - ⏳ **Pending** (详见 [方案B实施设计](../research/2026-03-13-p0-single-context-protocol-implementation-design.md))
8. **F2 State Consistency**: Fixing dual-source state issue where `current_node` exists in both top-level column and `state_json`. Implementing single source of truth with `state_json` and `PipelineStateView` for unified access (详见 [F2 Test-Driven Plan](../solution/2026-03-25-f2-test-driven-implementation-plan.md), [F2 Research Report](../research/2026-03-25-f2-state-json-consistency-research-report.md)) - 🔄 **In Progress**

**Phase 4 (P3) - Single Context Protocol 详细规划**:

当前上下文链路存在三个根问题需要解决：
1. `executor` 从 state 里"猜 task"，而不是从节点契约构建任务
2. `DualAgentNode` 把已有结构重新包装成 `{subject, task}`
3. `IndependentAgent` 再次尝试从字符串或嵌套 dict 里恢复上下文

**目标协议**: 统一 `NodeExecutionContext` 数据结构，跨越 executor → DualAgentNode → IndependentAgent/EvaluatorAgent 层，消除猜测逻辑和重复包装。

**核心组件**:
- `NodeExecutionContextBuilder`: 从 node.yaml + state 构建统一上下文
- `NodeExecutionContext`: TypedDict 定义的标准协议
- `ContextManager`: 基于 execution_context 裁剪不同 Agent 的输入

**设计约束**:
- 不允许在层间传 `str(context_json)` 作为主协议
- 不允许 agent 端再去"猜字段"
- 不允许 `task` 与 `subject_context` 重复承载同一含义

**参考文档**:
- [TDD SDK Migration](../solution/TDD-SDK-Migration-2026-03-25.md) - 测试驱动 SDK 迁移方案
- [TDD SDK Implementation Guide](../solution/TDD-SDK-Migration-Implementation-Guide.md) - 详细实施指南
- [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md) - 依赖漂移深度研究报告
- [NodeExecutionContext 深度研究报告](../research/2026-03-13-p0-single-context-protocol-deep-research-report.md) - 问题分析与流转链路
- [方案B实施设计](../research/2026-03-13-p0-single-context-protocol-implementation-design.md) - 代码实现方案
- [P0 重构总览](../research/2026-03-13-docuswarm-context-refactor-overview.md) - 重构顺序与依赖关系
- [Refactoring Roadmap](../solution/README.md) - Complete TDD plan
- [Research Part 1](../research/DocuSwarm-重构详细研究报告.md) - Core architecture analysis
- [Research Part 2](../research/DocuSwarm-重构详细研究报告-Part2.md) - Feature changes
- [Research Part 3](../research/DocuSwarm-重构详细研究报告-Part3.md) - SDK migration analysis
- [SDK Migration Research](../research/migration/README.md) - Complete kimi-agent-sdk removal migration reports

### 2.2 Target Users

| User Persona | Description | Primary Use Case |
|--------------|-------------|------------------|
| **Solo Developer** | Individual building projects with BMAD methodology | End-to-end document generation |
| **Tech Lead** | Team leader coordinating development efforts | Quality review and approval workflows |
| **Product Manager** | Non-technical stakeholder needing structured documentation | PRD and requirement tracking |

### 2.3 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Node Success Rate** | ≥ 85% | Completed node runs / Total node runs |
| **Quality Score** | ≥ 0.70 average | Evaluator Agent alignment scores per node |
| **Time to First Value** | 8-9 weeks | Development milestone tracking |
| **Cost per Node Run** | < $0.10 | Token usage × Kimi K2.5 pricing |

---

## 3. Functional Requirements

### 3.1 Core Node Execution

#### FR-001: Pipeline-Centric Execution
**Priority**: Critical  
**Description**: The system shall execute a complete pipeline via a single command, orchestrating multiple nodes sequentially with automatic context chaining.

**Acceptance Criteria**:
- User starts a complete pipeline via `docuswarm start --context <file>`
- Pipeline automatically orchestrates nodes in predefined order: analyst → (pm/ux parallel) → architect → po
- Automatic context chaining: predecessor node deliverables auto-injected via `context_hash`
- Pipeline supports resume from checkpoint on failure
- Node run results persisted to `node_runs` table

#### FR-002: Dual-Agent Node Execution
**Priority**: Critical  
**Description**: Each node shall use a dual-agent pattern with Independent and Evaluator agents.

**Acceptance Criteria**:
- Independent Agent creates deliverable and generates questions
- Evaluator Agent reviews deliverable without access to private reasoning
- Context isolation enforced between agents
- Iteration continues until APPROVED or max iterations reached

#### FR-003: Node Run History and Resume
**Priority**: High  
**Description**: The system shall persist all node run history and support re-execution.

**Acceptance Criteria**:
- Each `docuswarm start --context <file>` creates a new pipeline with unique `pipeline_id`
- All node run results (deliverable, questions, evaluation) stored per `(pipeline_id, node_id, run_id)`
- User can view pipeline status via `docuswarm status <pipeline_id>`
- User can resume a failed pipeline via `docuswarm resume <pipeline_id>`

### 3.2 Agent System

#### FR-004: Independent Agent Capabilities
**Priority**: Critical  
**Description**: Independent Agent shall create deliverables and generate clarifying questions.

**Acceptance Criteria**:
- Load BMAD persona from configuration
- Generate deliverable content in markdown format
- Generate minimum 3 questions (1 blocking required)
- Support iteration with evaluator feedback
- Private reasoning not shared with Evaluator

#### FR-005: Evaluator Agent Capabilities
**Priority**: Critical  
**Description**: Evaluator Agent shall review deliverables against criteria.

**Acceptance Criteria**:
- Apply node-specific evaluation weights
- Generate verdict: APPROVED, NEEDS_REVISION, or BLOCKED
- Calculate alignment score (0.0-1.0)
- Provide specific, actionable feedback
- No access to Independent Agent's reasoning

#### FR-006: Context Isolation Enforcement
**Priority**: Critical  
**Description**: The system shall enforce three-layer context isolation.

**Acceptance Criteria**:
- Layer 1: Separate prompt templates per agent
- Layer 2: Runtime access control
- Layer 3: Message-level filtering
- Audit trail for isolation verification
- Zero private data leakage to Evaluator

### 3.3 State Management

#### FR-007: Node Run State Persistence
**Priority**: High  
**Description**: The system shall persist node run state to SQLite `node_runs` table.

**Acceptance Criteria**:
- WAL mode enabled for concurrent read access
- `node_runs` table stores: `run_id`, `node_id`, `context_hash`, `status`, `deliverable`, `questions`, `evaluation`, `answers`, `chained_context`
- ACID transaction guarantees
- State queryable by node, by run, by context_hash

#### FR-007-B: Pipeline State Consistency (F2)
**Priority**: Critical  
**Description**: The system shall maintain state consistency by using `state_json` as the single source of truth for all pipeline state.

**Acceptance Criteria**:
- `state_json` is the single source of truth for pipeline state (current_node, status, completed_nodes, etc.)
- `PipelineStateView` provides unified read access to state fields from `state_json`
- `update_pipeline_state()` is the single write entry point for all state modifications
- Runtime consistency checks detect and warn about state mismatches
- ~~Deprecated `update_pipeline_status()`~~ **REMOVED** per P1-1 cleanup (use `update_pipeline_state()`)
- Top-level `current_node` column is removed after migration (Phase 3)

**Reference**: [F2 Implementation Plan](../solution/2026-03-25-f2-test-driven-implementation-plan.md)

#### FR-008: Context Chaining
**Priority**: High  
**Description**: The system shall automatically chain predecessor node deliverables as input context.

**Acceptance Criteria**:
- When running a node, system queries latest successful run of each predecessor node with matching `context_hash`
- Predecessor deliverables injected into node input context
- Warning issued if predecessor nodes have no successful runs
- User can opt-out via `--no-chain` flag

### 3.4 LLM Integration

#### FR-009: Kimi K2.5 Integration
**Priority**: Critical  
**Description**: The system shall integrate with Kimi K2.5 LLM provider via claude-agent-sdk and Kimi Code API.

**Acceptance Criteria**:
- Support Instant, Thinking, and Agent modes (via claude-agent-sdk)
- Handle 256K context window
- SDK 内部处理连接管理和基础重试
- SessionManager with ClaudeSDKWrapper for unified SDK interface
- SafeAsyncGenerator for proper cancellation handling
- **Environment**: `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`, `ANTHROPIC_API_KEY`

> **Note**: Migration from kimi-agent-sdk to claude-agent-sdk completed. See [TDD-05](../solution/TDD-05-SDKWrapper-Refactor.md).

#### FR-010: Tool Calling Support
**Priority**: Critical (upgraded from Medium)  
**Description**: The system shall support tool calling via claude-agent-sdk standard Tool Use Block format, and tools MUST be actively invoked during node execution to produce deliverable files.

**Acceptance Criteria**:
- create_deliverable tool (standard format + Pydantic) for document creation
- update_context tool (standard format + Pydantic) for state updates
- Tools passed via SessionManager.execute_with_tools()
- Pydantic 参数验证保证类型安全
- SDK result handling via SDKResult
- Agent 提示词明确要求使用工具写入 deliverable（而非返回 JSON 格式）
- Deliverable 文件实际写入 `output/{pipeline_id}/` 目录
- **Tool Implementation**: 纯函数式工具，无 CallableTool2 继承
- **Migration Path**: 已完全移除 CallableTool2，使用函数式工具 per [迁移报告 #2](../research/migration/02-tool-calling-mechanism-migration-report.md)

> **Implementation Note**: **已完全移除** kimi-agent-sdk CallableTool2。工具现在使用纯函数实现，通过 ToolRegistry 注册。详见 [TDD-03](../solution/TDD-03-ToolResultExtractor-Refactor.md) 和 [迁移报告](../research/migration/README.md)。

### 3.5 Quality Control

#### FR-011: Iteration Handling
**Priority**: High  
**Description**: The system shall handle node iterations for quality improvement.

**Acceptance Criteria**:
- Maximum 3 iterations per node
- Feedback accumulated across iterations
- Escalation at iteration 3 (critical review)
- Force completion at max iterations with warning

#### FR-012: Evaluation Criteria
**Priority**: High  
**Description**: The system shall apply standardized evaluation criteria.

**Acceptance Criteria**:
- Universal criteria: completeness, clarity, consistency, actionability, evidence quality
- Node-specific weight overrides
- Approval threshold: ≥ 0.70
- Escalation threshold: ≥ 0.50

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| **Node Execution Time** | < 2 minutes | Acceptable user wait time |
| **Full 5-Node Run** | < 15 minutes | User-driven sequential execution |
| **API Response Time** | < 30 seconds | Kimi K2.5 Thinking mode limit |
| **Concurrent Node Runs** | ≥ 5 | SQLite WAL + thread isolation |

### 4.2 Reliability

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| **System Availability** | 99% | Development tool tolerance |
| **Data Durability** | 100% | SQLite WAL mode guarantees |
| **Checkpoint Recovery** | 100% | No lost work on resume |
| **API Retry Success** | 95% | After 3 retry attempts |

### 4.3 Security

| Requirement | Description |
|-------------|-------------|
| **Context Isolation** | Evaluator cannot access Independent Agent reasoning |
| **API Key Protection** | Environment variable storage |
| **Input Validation** | JSON schema validation for all inputs |
| **Output Sanitization** | Remove private markers from outputs |

### 4.4 Scalability

| Requirement | MVP Target | Phase 2 Target |
|-------------|-----------|----------------|
| **Concurrent Users** | 1 | 10 |
| **Node Run Throughput** | 5/hour | 50/hour |
| **Database Size** | 1GB | 10GB |
| **Context Window Usage** | 100K tokens | 200K tokens |

---

## 5. Technical Architecture

### 5.1 System Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      DocuSwarm MVP                              │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  CLI Layer   │───▶│  LangGraph   │───▶│   SQLite     │     │
│  │  (Commands)  │    │  StateGraph  │    │   WAL Mode   │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                    │             │
│         ▼                   ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              Node Execution Layer                    │      │
│  │  ┌─────────┐  ┌────────┐  ┌────────┐  ┌──────────┐ │      │
│  │  │ Analyst │  │   PM   │  │   UX   │  │ Architect │ │      │
│  │  └─────────┘  └────────┘  └────────┘  └──────────┘ │      │
│  │                                             │       │      │
│  │  (Pipeline-orchestrated, sequential execution)│      │      │
│  │                                        ┌────▼───┐   │      │
│  │                                        │   PO   │   │      │
│  │                                        └────────┘   │      │
│  └─────────────────────────────────────────────────────┘      │
│                          │                                     │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              Dual-Agent Node                         │      │
│  │  ┌─────────────────┐    ┌─────────────────┐        │      │
│  │  │ Independent     │───▶│ Evaluator       │        │      │
│  │  │ Agent           │    │ Agent           │        │      │
│  │  │ • Deliverable   │    │ • Review        │        │      │
│  │  │ • Questions     │    │ • Verdict       │        │      │
│  │  │ • Reasoning*    │    │ • Feedback      │        │      │
│  │  └─────────────────┘    └─────────────────┘        │      │
│  │         * Context Isolated (not shared)             │      │
│  └─────────────────────────────────────────────────────┘      │
│                          │                                     │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────────────┐      │
│  │                 Kimi K2.5 LLM                        │      │
│  │  • Instant Mode (Routing/Validation)                 │      │
│  │  • Agent Mode (Independent)                          │      │
│  │  • Thinking Mode (Evaluator)                         │      │
│  └─────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.10+ | LangGraph native support |
| **Framework** | LangGraph | Multi-agent orchestration |
| **LLM** | Kimi K2.5 | 256K context, cost-effective |
| **Database** | SQLite + WAL | Simple, reliable persistence |
| **Checkpointing** | LangGraph SqliteSaver | Native integration |

### 5.3 Data Flow

#### 5.3.1 High-Level Flow

```
User Command: docuswarm start --context <file>
          │
          ▼
┌─────────────────────┐
│   Pipeline Init     │  ← Create pipeline, compute context_hash
│  + Orchestrator     │  ← LangGraph StateGraph for node orchestration
└─────────────────────┘
          │
          ▼ (Pipeline Orchestration)
┌─────────────────────┐
│  Node Execution     │  ← Sequential node execution
│  • analyst          │    (pm/ux in parallel)
│  • pm / ux          │
│  • architect        │
│  • po               │
└─────────────────────┘
          │
          ▼ (Per-Node Dual-Agent Execution)
┌─────────────────────┐
│  Independent Agent  │  ← Kimi Agent Mode
│  • Create Deliverable│
│  • Generate Questions│
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Context Filter    │  ← Remove private reasoning
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Evaluator Agent   │  ← Kimi Thinking Mode
│  • Review           │
│  • Score (0-1)      │
│  • Verdict          │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Pipeline Progress  │  ← Continue to next node or complete
└─────────────────────┘
```

#### 5.3.2 NodeExecutionContext Protocol Flow (Phase 4/P3)

在 P3 阶段引入 `NodeExecutionContext` 作为统一的上下文协议，消除猜测逻辑：

```
┌─────────────────────────────────────────────────────────────────┐
│                     NodeExecutionContext                         │
│                     统一节点执行上下文协议                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │   NodeLoader    │───▶ node.yaml (name, description,          │
│  │                 │           deliverable.required_sections)   │
│  └─────────────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────┐                                    │
│  │ NodeExecutionContext    │◀─── state (context_file,           │
│  │        Builder          │           chained_context)         │
│  └─────────────────────────┘                                    │
│           │                                                      │
│           ▼ NodeExecutionContext (统一协议)                      │
│  ┌─────────────────────────┐                                    │
│  │     DualAgentNode       │                                    │
│  │  ┌─────────────────┐    │                                    │
│  │  │ ContextManager  │    │◀─── 裁剪为                         │
│  │  │  .build_independent_input() │   IndependentAgentInput     │
│  │  └─────────────────┘    │                                    │
│  │           │             │                                    │
│  │           ▼             │                                    │
│  │  ┌─────────────────┐    │                                    │
│  │  │ IndependentAgent│    │                                    │
│  │  │  • 直接使用字段  │    │◀─── 无需猜测/解析                  │
│  │  │  • 创建交付物    │    │                                    │
│  │  └─────────────────┘    │                                    │
│  │           │             │                                    │
│  │           ▼ (过滤)      │                                    │
│  │  ┌─────────────────┐    │                                    │
│  │  │ ContextManager  │    │◀─── 裁剪为                         │
│  │  │  .build_evaluator_input() │   EvaluatorAgentInput        │
│  │  └─────────────────┘    │                                    │
│  │           │             │                                    │
│  │           ▼             │                                    │
│  │  ┌─────────────────┐    │                                    │
│  │  │ EvaluatorAgent  │    │                                    │
│  │  │  • 评审交付物    │    │                                    │
│  │  └─────────────────┘    │                                    │
│  └─────────────────────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**NodeExecutionContext 核心字段**:
- `pipeline_id`, `node_id`, `node_name`, `node_order` - 身份标识
- `task_name`, `task_description`, `role_supplement` - 任务契约
- `deliverable_type`, `deliverable_requirements` - 交付物契约
- `original_context`, `chained_deliverables` - 上下文数据
- `iteration_feedback` - 迭代反馈
- `docs_context` - 引用文档预加载内容 (Phase 13 - Step 2 实现)

**设计约束**:
- 不允许在层间传 `str(context_json)` 作为主协议
- 不允许 agent 端再去"猜字段"
- `ContextManager` 负责裁剪，而非 Agents 自行解析

#### 5.3.3 Reference Docs Preload (Step 2)

> **Phase**: 13 (P12)  
> **Status**: 🔄 In Progress  
> **Reference**: [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)

引用文档预加载功能让 Agent 无需主动调用工具即可直接获得 context file 中引用的支撑文档内容。

**数据流**:
```
Context File (引用 algorithm-spec.md, requirements.md)
    │
    ▼ NodeExecutionContextBuilder._resolve_reference_docs()
    ┌─────────────────────────────────────┐
    │ 1. 提取文件名 (反引号/裸文件名)      │
    │ 2. 递归搜索 docs/ 目录               │
    │ 3. 读取内容 (10K字符截断保护)        │
    └─────────────────────────────────────┘
    │
    ▼ NodeExecutionContext.docs_context
    │
    ▼ ContractBuilder._build_context_section()
    渲染 "## 引用文档" 章节到 prompt
```

**关键实现**:
- 文件名提取: `` `file.md` `` 和 `file.md` 格式
- 支持扩展名: `.md`, `.txt`, `.yaml`, `.yml`, `.json`
- 搜索策略: `docs/` 递归，同名取最浅路径
- 内容保护: 单文件最大 10,000 字符
          │
          ▼
┌─────────────────────┐
│  Iteration Logic    │
│  APPROVED → Done    │
│  NEEDS_REVISION →   │
│    Iterate (max 3)  │
│  BLOCKED → Stop     │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Node Run Output   │
│  • Deliverable      │
│  • Questions        │
│  • Evaluation       │
│  → Stored in        │
│    node_runs table  │
└─────────────────────┘
```

---

## 6. User Stories

### 6.1 Epic 1: Node Execution

#### US-001: Execute a Complete Pipeline
**As a** developer  
**I want to** execute a complete BMAD pipeline with my project context  
**So that** I can generate all project documents end-to-end

**Acceptance Criteria**:
- Start pipeline via `docuswarm start --context <file>`
- Pipeline auto-executes nodes in order: analyst → pm/ux → architect → po
- System auto-chains predecessor deliverables between nodes
- New `pipeline_id` created for each pipeline run
- Progress and results visible via `docuswarm status <pipeline_id>`

#### US-002: View Node Run Status
**As a** developer  
**I want to** see the current status of a node run  
**So that** I can track document generation progress

**Acceptance Criteria**:
- Current iteration count displayed
- Evaluation scores shown per run
- Verdict (APPROVED / NEEDS_REVISION / BLOCKED) clearly indicated
- Latest run shown by default, specific run selectable via `--run`

#### US-003: View Pipeline Run History
**As a** developer  
**I want to** see all historical pipeline runs  
**So that** I can track execution history and compare outputs

**Acceptance Criteria**:
- List all pipelines via `docuswarm list-pipelines`
- Show pipeline_id, status, current_node, timestamp
- Sorted by creation time (newest first)
- Filterable by status

### 6.2 Epic 2: Document Generation

#### US-004: Generate Analyst Report
**As a** developer  
**I want to** automatically generate a comprehensive analyst report  
**So that** I have a solid foundation for my project

**Acceptance Criteria**:
- Report includes market analysis, requirements, and recommendations
- Questions identify gaps in initial context
- Evaluation ensures completeness and evidence quality
- Output in markdown format

#### US-005: Generate PRD
**As a** product manager  
**I want to** automatically generate a PRD from analyst findings  
**So that** I have a standardized product requirements document

**Acceptance Criteria**:
- PRD references analyst deliverables
- Includes user stories and acceptance criteria
- Questions clarify ambiguous requirements
- Evaluation checks completeness and clarity

#### US-006: Generate UX Design
**As a** designer  
**I want to** automatically generate UX design documentation  
**So that** I have a clear user experience specification

**Acceptance Criteria**:
- Design aligns with PRD requirements
- Includes user flows and wireframe descriptions
- Questions address user interaction edge cases
- Evaluation checks design consistency

#### US-007: Generate Architecture Document
**As an** architect  
**I want to** automatically generate architecture documentation  
**So that** I have a technical specification for implementation

**Acceptance Criteria**:
- Architecture aligns with PRD and UX
- Includes component diagrams and API specifications
- Questions identify technical trade-offs
- Evaluation checks consistency and completeness

#### US-008: Generate Epics and Stories
**As a** product owner  
**I want to** automatically generate implementation epics and stories  
**So that** development can begin with clear tasks

**Acceptance Criteria**:
- Stories traceable to PRD requirements
- Include acceptance criteria
- Questions clarify implementation details
- Evaluation checks completeness and actionability

### 6.3 Epic 3: Quality Control

#### US-009: Review Deliverable Quality
**As a** quality-conscious developer  
**I want to** see evaluation scores for each deliverable  
**So that** I can trust the document quality

**Acceptance Criteria**:
- Alignment score (0-1) displayed per node
- Issues and suggestions listed
- Verdict clearly indicated
- Iteration history available

#### US-010: Answer Clarifying Questions
**As a** developer  
**I want to** answer questions generated during node execution  
**So that** subsequent nodes have complete context

**Acceptance Criteria**:
- Questions categorized by priority (blocking, clarifying, optional)
- Can provide answers to individual questions
- Answers incorporated into subject context
- Blocking questions flagged for user attention before re-running node

---

## 7. Release Planning

### 7.1 MVP (Phase 1) - 8-9 Weeks

**Scope**:
- Pipeline-first execution with 5 sequential BMAD nodes
- Dual-agent pattern (Independent + Evaluator) per node
- Automatic context chaining between nodes
- SQLite state persistence (`pipelines` and `node_runs` tables)
- Kimi K2.5 integration (via claude-agent-sdk + Kimi Code API)
- CLI interface (start, status, resume, list-pipelines, export, questions, answer, cancel, clean)
- **SDK Migration**: claude-agent-sdk with SessionManager/ClaudeSDKWrapper architecture

**Milestones**:

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1-2 | Infrastructure | LangGraph setup, SQLite schema |
| 3-4 | Agent System | Independent Agent, Evaluator Agent |
| 5-6 | Node Execution | Pipeline orchestration with 5 sequential nodes |
| 7-8 | Integration | End-to-end node workflow, CLI |
| 9 | Testing & Polish | Test coverage, documentation |

### 7.2 Phase 2 - 3-4 Weeks

**Scope**:
- Add Questioner Agent (if quality issues)
- DAG-based parallel execution
- Multi-provider fallback
- Improved caching

### 7.3 Phase 3 - 3-4 Weeks

**Scope**:
- RAG knowledge retrieval
- ~~MCP protocol migration~~ → 已由 claude-agent-sdk 标准工具替代
- Web UI interface
- Extended node types
- **SDK Complete Removal**: Final removal of all kimi-agent-sdk legacy code per [迁移路线图](../research/migration/README.md)

---

## 8. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Node Executor Integration Gap** | Confirmed | Critical | 方案C: agent_file + work_dir 修复。详见研究报告 |
| **Kimi K2.5 API Instability** | Medium | High | claude-agent-sdk 内部重试 + 统一异常体系处理 |
| **Context Isolation Leakage** | Low | High | Three-layer defense, audit logging |
| **Quality Score Inconsistency** | Medium | Medium | Calibrated evaluation prompts, threshold tuning |
| **LangGraph Learning Curve** | Low | Low | Well-documented framework, active community |
| **Iteration Loops** | Medium | Medium | Max 3 iterations, escalation mechanism |

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **BMAD** | Breakthrough Method of Agile AI-driven Development |
| **Dual-Agent Pattern** | Architecture with Independent Agent (creation) and Evaluator Agent (review) |
| **Context Isolation** | Security mechanism preventing information leakage between agents |
| **LangGraph** | Framework for building stateful multi-agent applications |
| **Node** | Single BMAD execution unit (e.g., Analyst, PM, UX), user-driven |
| **Deliverable** | Output document generated by Independent Agent |
| **Alignment Score** | Quality metric (0.0-1.0) assigned by Evaluator Agent |
| **WAL Mode** | SQLite Write-Ahead Logging for concurrent access |

---

## 10. Appendices

### Appendix A: Evaluation Criteria Weights

| Node | Completeness | Clarity | Consistency | Actionability | Evidence |
|------|-------------|---------|-------------|---------------|----------|
| Analyst | 0.30 | 0.20 | 0.20 | 0.30 | 0.40 |
| PM | 0.40 | 0.30 | 0.20 | 0.30 | 0.20 |
| UX | 0.30 | 0.30 | 0.30 | 0.20 | 0.20 |
| Architect | 0.35 | 0.30 | 0.35 | 0.20 | 0.20 |
| PO | 0.40 | 0.20 | 0.20 | 0.40 | 0.20 |

### Appendix B: Kimi K2.5 Mode Configuration

| Agent Type | Kimi Mode | Temperature | Max Tokens |
|------------|-----------|-------------|------------|
| Context Validation | Instant | 0.3 | 4,096 |
| Independent | Agent | 0.7 | 32,768 |
| Evaluator | Thinking | 0.5 | 8,000 |

---

**Document End**

*Generated with DocuSwarm BMAD Workflow*
> **2026-03-13 Alignment Notice**: 当前代码实现与本文档在上下文协议、SDK 迁移、`ContextResolver`、`@` 路径注入、纯函数工具等方面存在明显漂移。涉及上下文注入和重构落地时，应以 `docs/evaluation/docuswarm-agent-context-injection-evaluation-2026-03-13.md`、`docs/research/2026-03-13-context-injection-audit.md` 与 `docs/research/2026-03-13-*.md` 方案系列为当前基准。

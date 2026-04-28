# DocuSwarm 文档对齐索引

**日期**: 2026-03-28  
**版本**: v1.0  
**关联方案**: [Test-Driven Implementation](./solution/refactor-2026-03-28-test-driven-implementation.md)

---

## 概述

本文档索引跟踪所有与 [2026-03-28 重构实施方案](./solution/refactor-2026-03-28-test-driven-implementation.md) 对齐的文档状态。

---

## 5项关键要求与文档对齐状态

| 要求 | 描述 | 已对齐文档 | 状态 |
|------|------|------------|------|
| **REQ-001** | system_prompt preset/append 结构 | [05_LLM_INTEGRATION.md](#llm_integrationmd) | ✅ 已对齐 |
| **REQ-002** | node.yaml evaluator 内联段 | [03_PIPELINE_ARCHITECTURE.md](#pipeline_architecturemd) | ✅ 已对齐 |
| **REQ-003** | SessionManager 主执行链接入 | [02_AGENT_ARCHITECTURE.md](#agent_architecturemd), [05_LLM_INTEGRATION.md](#llm_integrationmd) | ✅ 已对齐 |
| **REQ-004** | tests/__init__.py 修复 | [实施方案](./solution/refactor-2026-03-28-test-driven-implementation.md) | ✅ 已记录 |
| **REQ-005** | NodeDeliverableConfig 扩展 | [03_PIPELINE_ARCHITECTURE.md](#pipeline_architecturemd) | ✅ 已对齐 |

## Phase A/B 技术债务修复对齐状态

| 问题 | 描述 | 已对齐文档 | 状态 |
|------|------|------------|------|
| **P0-1** | `asyncio.run()` in async context | [PRD.md](#prdmd-phase-11), [architecture.md](#architecturemd-async-contract) | ✅ 已对齐 |
| **P0-2** | `_run_async` bridge removal | [PRD.md](#prdmd-phase-11), [design/README.md](#designreadmemd-phase-ab) | ✅ 已对齐 |
| **P1-1** | `escalate()` await | [PRD.md](#prdmd-phase-11), [design/README.md](#designreadmemd-phase-ab) | ✅ 已对齐 |
| **P1-2** | 文档/配置口径统一 | [PRD.md](#prdmd-phase-11), [design/README.md](#designreadmemd-phase-ab) | ✅ 已对齐 |
| **P1-3** | 冒烟测试补充 | [solution/README.md](#solutionreadmemd) | ✅ 已对齐 |

---

## Phase A/B 技术债务修复详情

### PRD.md (Phase 11)

**对齐内容**:
- 添加 Phase 11 (P10) - Phase A/B Technical Debt Resolution
- 添加 Phase A (1周止血) 问题表格 (P0-1, P0-2, P1-1, P1-3)
- 添加 Phase B (1个迭代收口) 问题表格 (P1-2, P1-3)
- 添加关键修复代码示例
- 添加验收标准

**关键更新**:
```markdown
| **Phase 11 (P10)** | **Phase A/B Technical Debt Resolution** | ... | 🔄 **Critical** |
```

**位置**: [PRD.md Section 2.4 - Phase 11](./PRD.md#phase-11-p10---phase-ab-technical-debt-resolution)

### architecture.md

**对齐内容**:
- 添加 Section 3.6 - Async/Sync Contract (Phase A P0-1, P0-2, P1-1)
- 添加异步边界契约图示
- 添加契约规则表格
- 添加修复状态表格

**关键更新**:
```
┌─────────────────────────────────────────────────────────────┐
│                 Async/Sync Boundary Contract                 │
├─────────────────────────────────────────────────────────────┤
│  CLI Entry          sync def               commands/*.py      │
│  Service Layer      async def              PipelineService    │
│  Orchestrator       async def              HybridOrchestrator │
│  State Manager      sync def               StateManager       │
│  Bridge (Banned)    ❌ _run_async()         REMOVED (P0-2)   │
└─────────────────────────────────────────────────────────────┘
```

**位置**: [architecture.md Section 3.6](./architecture.md#36-asyncsync-contract-phase-a-p0-1-p0-2-p1-1)

### design/README.md

**对齐内容**:
- 添加 "Phase A/B Technical Debt Resolution 设计约束 (2026-04-04)" 章节
- 添加 P0-1, P0-2, P1-1 修复代码示例
- 添加 Phase B 测试与文档修复规范
- 添加验收标准表格

**位置**: [design/README.md - Phase A/B](./design/README.md#phase-ab-technical-debt-resolution-设计约束-2026-04-04)

### solution/README.md

**对齐内容**:
- 添加 Phase A/B TDD 方案链接
- 添加冒烟测试列表
- 添加验证脚本说明

**位置**: [solution/README.md - Phase A/B](./solution/README.md#phase-a--b-技术债务修复)

---

## 文档对齐详情

### PRD.md

**对齐内容**:
- 添加 Phase 7 (P6) - 2026-03-28 Refactor Implementation
- 添加5项关键要求表格
- 添加设计原则（拒绝向后兼容）
- 链接到详细实施文档

**关键更新**:
```markdown
| **Phase 7 (P6)** | **2026-03-28 Refactor Implementation** | ... | 🔄 **In Progress** |
```

**位置**: [PRD.md Section 2.4](./PRD.md#24-architecture-evolution-refactoring-plan)

---

### 05_LLM_INTEGRATION.md

**对齐内容**:
- 更新 SessionManager 构造函数参数（node_id, file_dirs, search_dirs）
- 添加 Four-Layer System Prompt Architecture 章节
- 添加 preset/append 结构示例
- 更新 create_session 签名支持 dict system_prompt

**关键更新**:
```python
def __init__(
    self,
    ...
    node_id: str | None = None,  # Added for MCP tool isolation
    file_dirs: list[str] | None = None,  # File permissions
    search_dirs: list[str] | None = None,  # Search permissions
) -> None:
```

**位置**: 
- [SessionManager Compatibility Layer](./architecture/05_LLM_INTEGRATION.md#22-sessionmanager-compatibility-layer)
- [Four-Layer Architecture](./architecture/05_LLM_INTEGRATION.md#23-four-layer-system-prompt-architecture)

---

### 02_AGENT_ARCHITECTURE.md

**对齐内容**:
- 添加 IndependentAgent.execute_with_input 完整配置注入章节
- 添加 node_id 和 tool_permissions 注入示例
- 链接到实现需求文档

**关键更新**:
```python
# Create SessionManager with full configuration
pipeline_session_manager = SessionManager(
    work_dir=output_dir,
    agent_file=self._agent_file,
    node_id=self.node_id,        # Injected for MCP server naming
    file_dirs=file_dirs,         # File read permissions
    search_dirs=search_dirs,     # Search permissions
)
```

**位置**: [Section 3.5](./architecture/02_AGENT_ARCHITECTURE.md#35-execution-with-full-configuration-2026-03-28)

---

### 03_PIPELINE_ARCHITECTURE.md

**对齐内容**:
- 更新 node.yaml 示例为 Schema v2.1
- 添加 deliverable 扩展字段（template_title, output_filename, format_hints）
- 添加 evaluator 内联配置结构
- 添加 NodeDeliverableConfig 和 NodeEvaluatorConfig 数据类定义

**关键更新**:
```yaml
deliverable:
  template_title: "Business Analysis Report"
  output_filename: "analyst-report.md"
  format_hints:
    max_words: 3000

evaluator:
  criteria_file: evaluator.yaml
  threshold:
    approval: 0.70
    escalation: 0.50
```

**位置**: [Section 4.2](./architecture/03_PIPELINE_ARCHITECTURE.md#42-node-configuration-bmm-aligned-format)

---

### design/README.md

**对齐内容**:
- 添加 2026-03-28 重构实施设计约束章节
- 添加5项要求的设计约束表格
- 添加 system_prompt 结构约束
- 添加 node.yaml Schema v2.1 约束
- 添加工具权限注入约束

**位置**: [2026-03-28 重构实施设计约束](./design/README.md#2026-03-28-重构实施设计约束)

---

## 实施验证

### 自动化验证工具

**工具**: [refactor_implementation_auditor.py](../tools/refactor_implementation_auditor.py)

**用法**:
```bash
python tools/refactor_implementation_auditor.py
```

**预期输出**（全部完成后）:
```
================================================================================
统计
================================================================================
  通过: 8
  失败: 0
  警告: 0
  未找到: 0

[OK] 所有关键检查通过！
```

---

## F9: Kimi Message Extraction Fix 对齐状态

### 新增文档

| 文档 | 类型 | 说明 |
|------|------|------|
| [Kimi Message Extraction TDD Plan](./solution/2026-04-06-kimi-message-extraction-tdd-plan.md) | 解决方案 | 测试驱动修复方案 |
| [Root Cause Analysis](./research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md) | 研究报告 | 根因分析报告 |
| [Document Alignment Update](./DOCUMENT_ALIGNMENT_UPDATE_2026-04-06.md) | 对齐报告 | 本文档对齐更新汇总 |

### 更新文档

| 文档 | 更新内容 | 关键变更 |
|------|----------|----------|
| [PRD.md](./PRD.md) | Phase 15 新增 | P14 - Kimi Message Extraction Fix |
| [architecture.md](./architecture.md) | F9 架构决策 | `isinstance()` 强制使用 |
| [05_LLM_INTEGRATION.md](./architecture/05_LLM_INTEGRATION.md) | 第 10 节新增 | SDK Message Type Handling 最佳实践 |
| [design/README.md](./design/README.md) | F9 设计约束 | 4 项设计约束 |

### 核心设计约束

| 约束 | 禁止 | 强制使用 |
|------|------|----------|
| 消息类型检查 | `getattr(msg, "role", "")` | `isinstance(msg, AssistantMessage)` |
| ContentBlock 检查 | `getattr(item, "type", "")` | `isinstance(item, TextBlock)` |
| 消息转换 | 自行实现转换 | `SessionManager._message_to_dict()` |

---

## 文档依赖关系

### 2026-03-28 重构

```
refactor-2026-03-28-test-driven-implementation.md (方案)
    │
    ├──► PRD.md (Phase 7 添加)
    │
    ├──► architecture/05_LLM_INTEGRATION.md (Layer 4 架构)
    │
    ├──► architecture/02_AGENT_ARCHITECTURE.md (执行注入)
    │
    ├──► architecture/03_PIPELINE_ARCHITECTURE.md (配置扩展)
    │
    ├──► design/README.md (设计约束)
    │
    └──► DOCUMENT_ALIGNMENT_INDEX.md (本文档)
```

### 2026-04-06 F9 Message Extraction Fix

```
2026-04-06-kimi-message-extraction-tdd-plan.md (方案)
    │
    ├──► PRD.md (Phase 15 添加)
    │
    ├──► architecture.md (F9 决策添加)
    │
    ├──► architecture/05_LLM_INTEGRATION.md (第 10 节新增)
    │
    ├──► design/README.md (F9 设计约束)
    │
    ├──► DOCUMENT_ALIGNMENT_UPDATE_2026-04-06.md (对齐报告)
    │
    └──► DOCUMENT_ALIGNMENT_INDEX.md (本文档更新)
```

### 2026-04-04 Phase A/B 技术债务修复

```
phase_a_b_technical_debt_research_report.md (研究报告)
    │
    ├──► phase_a_b_test_driven_solution_plan.md (TDD 方案)
    │       │
    │       ├──► PRD.md (Phase 11 添加)
    │       │
    │       ├──► architecture.md (Async Contract)
    │       │
    │       ├──► design/README.md (设计约束)
    │       │
    │       ├──► tests/smoke/*.py (冒烟测试)
    │       │
    │       └──► solution/README.md (索引更新)
    │
    └──► 2026-04-04-docuswarm-tech-debt-audit.md (审计报告)
```

---

## 变更历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-04 | v1.1 | 添加 Phase A/B 技术债务修复对齐 |
| 2026-03-28 | v1.0 | 初始创建，对齐5项关键要求 |

---

## 参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 实施方案 | [./solution/refactor-2026-03-28-test-driven-implementation.md](./solution/refactor-2026-03-28-test-driven-implementation.md) | TDD 实施方案 |
| 实施研究 | [./research/refactor-2026-03-28-implementation-requirements.md](./research/refactor-2026-03-28-implementation-requirements.md) | 详细实施研究 |
| 审查报告 | [./evaluation/2026-03-28-refactor-2026-03-26-implementation-review.md](./evaluation/2026-03-28-refactor-2026-03-26-implementation-review.md) | 原始审查报告 |

### Phase A/B 技术债务修复

| 文档 | 路径 | 说明 |
|------|------|------|
| 技术债务审计 | [./evaluation/2026-04-04-docuswarm-tech-debt-audit.md](./evaluation/2026-04-04-docuswarm-tech-debt-audit.md) | 原始审计报告 |
| 深度研究 | [./research/phase_a_b_technical_debt_research_report.md](./research/phase_a_b_technical_debt_research_report.md) | 问题深度研究 |
| TDD 方案 | [./solution/phase_a_b_test_driven_solution_plan.md](./solution/phase_a_b_test_driven_solution_plan.md) | 测试驱动方案 |
| 执行指南 | [./solution/TDD_EXECUTION_GUIDE.md](./solution/TDD_EXECUTION_GUIDE.md) | 快速执行参考 |

---

**维护者**: Implementation Team  
**审核周期**: 每两周或重大变更后

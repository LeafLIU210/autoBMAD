# DocuSwarm 节点技术债深度分析报告
# Nodes Tech Debt & Dependency Analysis

**报告日期**: 2026-04-07  
**研究范围**: `autoBMAD/docuswarm/nodes/`、`autoBMAD/nodes/`、`nodes/` 三个目录  
**研究目的**: 为 EPIC-31 至 EPIC-38 的实施提供当前代码状态基准，识别已完成与待完成工作

---

## 1. 三目录职责分层（依赖链图）

```
nodes/                              ← 已废弃的旧目录（兼容层）
  __init__.py                       ← 发出 DeprecationWarning，re-export nodes.loader
  loader.py                         ← 旧版 NodeLoader（缺少多个新字段）
  {analyst,pm,ux,architect,po}/     ← 旧版 node.yaml（部分已更新）

autoBMAD/nodes/                     ← 权威配置层（新版）
  loader.py                         ← 新版 NodeLoader（含所有新 dataclass）
  {analyst,pm,ux,architect,po}/     ← 新版 node.yaml（大部分已实现 EPIC-31/32/34 要求）

autoBMAD/docuswarm/nodes/           ← 执行层（核心引擎）
  dual_agent.py                     ← DualAgentNode 主类
  iteration.py                      ← IterationController
  loader.py                         ← 已废弃（raise ImportError）
  __init__.py                       ← 从 autoBMAD.nodes.loader 导入 NodeConfig/NodeLoader
```

**关键依赖关系**：
- `autoBMAD/docuswarm/nodes/dual_agent.py` → `from autoBMAD.nodes.loader import NodeLoader`（第820行）
- `autoBMAD/docuswarm/nodes/__init__.py` → `from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError`
- 全系统 23 处 `from autoBMAD.nodes.loader import ...` 导入
- `nodes/__init__.py` 发出弃用警告，但 `nodes/loader.py` 仍被 nodes 目录内部引用

---

## 2. 已实现状态总览（EPIC 31-38 交叉验证）

### EPIC-31: Skills Introduction Hybrid ✅ **大部分已完成**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 31.1 | `autoBMAD/nodes/loader.py` | ✅ 完成 | `NodeSkillsConfig` 已实现（第122-141行），含 `sdk_native`, `whitelist`, `quick_reference_enabled`, `quick_reference_include_descriptions` |
| 31.2 | `autoBMAD/docuswarm/llm/session_manager.py` | ✅ 完成 | `setting_sources: ["project"]` 已配置（第235-237行），`"Skill"` 已加入 `allowed_tools`（第186-187行） |
| 31.3 | `autoBMAD/docuswarm/prompts/skill_injector.py` | ✅ 完成 | `SkillInjector` 已实现并在 `independent.py` 第31行导入 |
| 31.4 | `autoBMAD/nodes/{5个节点}/node.yaml` | ✅ 完成 | 所有5个节点的 `tools.skills` 节已配置 |
| 31.5 | `autoBMAD/docuswarm/agents/independent.py` | ✅ 完成 | `SkillInjector.build_skills_quick_reference()` 已在第321行调用 |
| 31.6 | `tests/test_skills_integration.py` | ❓ 未确认 | 需独立验证 |

**⚠️ 技术债发现**：
- `nodes/` 旧目录的 5 个 `node.yaml` **与 `autoBMAD/nodes/` 不完全同步**。`nodes/analyst/node.yaml` 缺少 `allowed_builtin_tools` 和 `file_permissions`（仅有 skills），而 `autoBMAD/nodes/analyst/node.yaml` 有完整的 tools 配置。EPIC-31 的 Story 31.4 指向的是 `nodes/` 目录，但实际权威配置在 `autoBMAD/nodes/`。

---

### EPIC-32: Node Task Refactor Skill Mapping ✅ **大部分已完成**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 32.1 | `autoBMAD/nodes/loader.py` | ✅ 完成 | `NodeTaskConfig.skill_ref: str \| None = None`（第57行），解析逻辑在第411行 |
| 32.2 | `nodes/analyst/node.yaml` | ✅ 完成 | `task.skill_ref: bmad-product-brief`，`deliverable_type: product-brief`；`autoBMAD/nodes/analyst/node.yaml` 也已更新 |
| 32.3-32.6 | 其余4个节点 | ✅ 完成 | `nodes/` 和 `autoBMAD/nodes/` 中的 pm, ux, architect, po 均有 `skill_ref` |
| 32.7 | `autoBMAD/docuswarm/agents/independent.py` | ✅ 完成 | SkillInjector 集成已完成 |
| 32.8 | `nodes/analyst/evaluator.yaml` | ❓ 未确认 | 需检查权重是否对齐 product brief 评估 |

**⚠️ 技术债发现**：
- **两套 node.yaml 不同步（关键）**：`nodes/` 目录和 `autoBMAD/nodes/` 目录均维护同名节点配置，但内容存在差异：
  - `nodes/pm/node.yaml`：有 `allowed_builtin_tools`, `file_permissions`, `search_permissions`
  - `nodes/analyst/node.yaml`：**缺少** `allowed_builtin_tools` 和 `file_permissions`
  - `nodes/architect/node.yaml`：缺少 `allowed_builtin_tools` 和 `file_permissions`
  - `nodes/ux/node.yaml`：有部分配置
- `NodeLoader._get_base_path()` 在 `autoBMAD/nodes/loader.py` 中默认路径为 `Path(__file__).parent.parent`（即 `autoBMAD/`），而 `nodes/loader.py` 默认路径为 `Path(__file__).parent.parent`（即项目根）—— 这意味着两个 loader **分别加载不同目录的配置**，形成双轨制技术债。

---

### EPIC-33: Document Creation Constraints MultiDoc ❌ **未实现**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 33.1 | `autoBMAD/docuswarm/tools/create_deliverable.py` | ❌ 未实现 | `CreateDeliverableParams` 无 `document_index`, `document_total`, `document_type` 字段 |
| 33.2 | `autoBMAD/docuswarm/context/validator.py` | ❌ 未实现 | 无 `max_deliverables` 验证规则 |
| 33.3 | `nodes/*/node.yaml` | ❌ 未实现 | 所有 5 个节点无 `deliverable.max_deliverables` 配置 |
| 33.4 | `autoBMAD/docuswarm/templates/` | ❌ 未实现 | 无 `architect_templates.yaml`, `po_templates.yaml` |
| 33.5 | `NodeResult` / `contracts.py` | ❌ 未实现 | `NodeResult` 无 `is_multi_document`, `all_documents`, `total_word_count` |
| 33.6 | `orchestrator.py` | ❌ 未实现 | 无多文档收集逻辑 |
| 33.7 | `nodes/architect/node.yaml`, `nodes/po/node.yaml` | ❌ 未实现 | 无 `deliverable.max_deliverables` 和 `document_types` |
| 33.8 | `prompts/contract_builder.py` | ❌ 未实现 | 无文档数量引导提示 |
| 33.9 | 测试 | ❌ 未实现 | 无约束测试 |

**⚠️ 技术债风险评估**：
- 当前所有节点（包括应只创建1个文档的 analyst/pm/ux）均无创建数量约束
- `NodeResult` 的 `deliverable` 字段是单一 `dict[str, Any]`，架构上不支持多文档
- 这是 8 个 EPIC 中**实现进度最低**的一个（0% 完成）

---

### EPIC-34: Tool Permissions Full Open ⚠️ **部分完成**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 34.1 | `nodes/analyst/node.yaml` | ❌ 不完整 | 仅有 `tools.skills`，**缺少** `allowed_builtin_tools` 和 `file_permissions` |
| 34.2 | `nodes/pm/node.yaml` | ✅ 完成 | 有完整 tools 配置（`allowed_builtin_tools`, `file_permissions`, `search_permissions`） |
| 34.3 | `nodes/ux/node.yaml` | ⚠️ 部分 | 有部分配置，需验证 |
| 34.4 | `nodes/architect/node.yaml` | ❌ 不完整 | 仅有 `tools.skills`，缺少 `allowed_builtin_tools` 和 `file_permissions` |
| 34.5 | `nodes/po/node.yaml` | ✅ 完成 | 有完整 tools 配置 |
| 34.6 | `session_manager.py` | ✅ 完成 | 工具配置日志已实现 |
| 34.7 | `independent.py` | ✅ 完成 | SkillInjector 已注入工具信息 |
| 34.8 | 测试 | ❓ 未确认 | 需独立验证 |

**⚠️ 关键发现：`nodes/` vs `autoBMAD/nodes/` 配置分叉**

| 节点 | `nodes/` 目录 | `autoBMAD/nodes/` 目录 |
|------|-------------|----------------------|
| analyst | 无 `allowed_builtin_tools` | 有完整 tools 配置 |
| pm | 有完整 tools 配置 | 有完整 tools 配置 |
| ux | 有部分配置 | 有完整 tools 配置 |
| architect | 无 `allowed_builtin_tools` | 有完整 tools 配置 |
| po | 有完整 tools 配置 | 有完整 tools 配置 |

**核心问题**：EPIC-34 的 Stories 指向 `nodes/` 目录修改，但实际执行时 `NodeLoader` 读取的是 `autoBMAD/nodes/`。两个目录的配置不一致造成潜在的调试困惑。

---

### EPIC-35: SharedContext Update Mechanism ⚠️ **P0 已完成，P1/P2 未实现**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 35.1 | `autoBMAD/docuswarm/node_execution/executor.py` | ✅ 完成 | `_refresh_shared_context_from_db()` 函数已存在（第360行），P0 修复已完成 |
| 35.2 | `nodes/*/node.yaml` | ❌ 未实现 | 5个节点均无 `tools.shared_context` 配置段 |
| 35.3 | `autoBMAD/nodes/loader.py` | ❌ 未实现 | 无 `NodeSharedContextConfig` dataclass，无 `shared_context` 字段 |
| 35.4 | `autoBMAD/docuswarm/tools/update_context.py` | ❌ 未实现 | 无版本控制逻辑 |
| 35.5 | `autoBMAD/docuswarm/tools/update_context.py` | ❌ 未实现 | whitelist 仍为硬编码 |
| 35.6 | `autoBMAD/docuswarm/storage/state_manager.py` | ❌ 未实现 | 无 `shared_context_history` 表 |
| 35.7 | 测试 | ❌ 未实现 | 无集成测试 |

---

### EPIC-36: Summary Agent Context Builder Refactor ✅ **主体已完成**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 36.1 | `autoBMAD/docuswarm/agents/summary.py` | ✅ 完成 | `SummaryAgent` 类已完整实现（25.9KB） |
| 36.2 | `autoBMAD/docuswarm/config/summary_agent.yaml` | ✅ 完成 | 配置文件已存在 |
| 36.3 | `autoBMAD/docuswarm/pipeline/orchestrator.py` | ❓ 未确认 | 需验证 `_summarize_referenced_documents` 集成 |
| 36.4 | `autoBMAD/docuswarm/node_execution/context_builder.py` | ✅ 完成 | 第61-63行已实现 cache 优先读取 |
| 36.5 | `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` | ✅ 完成 | 第176-212行已实现 summary 传播 |
| 36.6 | `orchestrator.py` | ❓ 未确认 | resume 支持需验证 |
| 36.7 | 测试 | ❓ 未确认 | 需独立验证测试覆盖 |

---

### EPIC-37: docs_context Persistence PipelineState ✅ **已完成**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 37.1 | `autoBMAD/docuswarm/pipeline/state.py` | ✅ 完成 | `docs_context_summary: list[dict[str, Any]]` 已在第79行添加 |
| 37.2 | `autoBMAD/docuswarm/pipeline/state.py` | ✅ 完成 | `create_initial_state()` 已接受 `docs_context_summary` 参数（第85行） |
| 37.3 | `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` | ✅ 完成 | 第176-212行已实现 summary 注入 |
| 37.4 | `autoBMAD/docuswarm/node_execution/context_builder.py` | ✅ 完成 | 缓存优先读取已实现 |
| 37.5 | `autoBMAD/docuswarm/pipeline/graph.py` | ❓ 未确认 | 需验证 |
| 37.6 | `autoBMAD/docuswarm/pipeline/orchestrator.py` | ❓ 未确认 | resume 支持需验证 |
| 37.7 | 测试 | ❓ 未确认 | 需独立验证 |

---

### EPIC-38: JSON Output Schema Constraint ❌ **未实现**

| Story | 文件 | 状态 | 说明 |
|-------|------|------|------|
| 38.1 | `autoBMAD/docuswarm/llm/session_manager.py` | ❌ 未实现 | `single_prompt()` 无 `output_format` 参数 |
| 38.2 | `autoBMAD/docuswarm/agents/evaluator_config/schemas.py` | ❌ 未实现 | 仅有 `CriteriaWeights`, `EvaluationCriteria`, `ThresholdConfig`；**缺少** `EVALUATOR_OUTPUT_SCHEMA` |
| 38.3 | `autoBMAD/docuswarm/tools/create_deliverable_sdk.py` | ❌ 未实现 | 无 `submit_execution_report` 工具（仅有 `create_deliverable_tool`） |
| 38.4 | `autoBMAD/docuswarm/agents/independent.py` | ❌ 未实现 | 系统提示无 `submit_execution_report` 调用顺序说明 |
| 38.5 | `autoBMAD/docuswarm/context/validator.py` | ❌ 未实现 | `IndependentOutputValidationStrategy` 无工具结果格式支持 |

**⚠️ 这是当前最高风险的未实现 EPIC**：
- `EvaluatorAgent._parse_response()` 依然零容错（JSON 解析失败 → 直接 raise）
- `verdict` enum 字段（pipeline 核心决策）完全无约束
- `questions[].priority` enum 从未被验证
- `EVALUATOR_OUTPUT_SCHEMA` 常量**不存在**

---

## 3. 核心技术债汇总

### TD-001: 双目录 NodeLoader 双轨制（HIGH）

**现象**：
- `nodes/loader.py`（旧版）：缺少 `NodeValidationError`, `NodeRuntimeConfig`, `NodeSkillsConfig`, `NodeToolPermissions`，`NodeEvaluatorConfig` 使用 `thresholds` 而新版使用 `threshold`
- `autoBMAD/nodes/loader.py`（新版）：包含所有新 dataclass
- `nodes/__init__.py` 重新导出旧版 loader，并发出 DeprecationWarning
- 实际 docuswarm 代码（23处）全部导入新版 `autoBMAD.nodes.loader`

**影响**：
- `nodes/` 目录下的 `node.yaml` 文件由旧版 loader 读取（当使用 `nodes.NodeLoader.load()` 时）
- 但实际执行路径走新版 loader，读取 `autoBMAD/nodes/` 的配置
- **任何对 `nodes/` 下配置文件的修改，均不会影响实际执行行为**

**解决方案**：
1. 短期：删除 `nodes/` 目录（或仅保留废弃警告的 `__init__.py`），统一使用 `autoBMAD/nodes/`
2. EPIC-31/32/33/34/35 中对 `nodes/*/node.yaml` 的修改计划需要**重定向到 `autoBMAD/nodes/*/node.yaml`**

---

### TD-002: nodes/analyst 和 nodes/architect 缺少完整 tools 配置（MEDIUM）

**现象**：
```yaml
# nodes/analyst/node.yaml - 缺少这些
tools:
  allowed_builtin_tools: ["Read", "Glob"]  # 缺失
  file_permissions:
    allowed_read_dirs:
      - "docs/"  # 缺失
  search_permissions:
    search_dirs:
      - "docs/"  # 缺失
  skills:  # 存在
    sdk_native: true
    ...
```

**对应 EPIC-34 Stories 34.1/34.4 需要补充这些配置。**

---

### TD-003: EPIC-33 (多文档支持) 完全缺失（CRITICAL for architect/po）

**现象**：
- `NodeResult.deliverable` 是单一 `dict[str, Any]`
- `DualAgentNode` 只处理一个 deliverable
- architect 和 po 节点需要创建 2-5 个文档，但架构不支持

**影响**：
- architect 节点无法区分 "系统架构" 和 "API 设计" 文档
- po 节点无法区分 "epic 列表" 和 "user story 文档"
- 当前所有节点的 `deliverable` 实际上是无结构的

---

### TD-004: EPIC-38 零容错 JSON 解析（CRITICAL - 运行时崩溃风险）

**现象**：
```python
# evaluator.py::_parse_response() 当前行为
try:
    data: dict[str, Any] = extract_json(content_str)
except ResponseParseError as e:
    raise EvaluationError(f"Failed to parse response: {e}") from e
    # → pipeline FAILED，无任何 fallback
```

**影响**：
- 任何 LLM JSON 格式错误（幻觉、截断、多余文本）→ pipeline 立即失败
- `verdict` 字段返回非法值（如 "PASS" 而非 "APPROVED"）→ DualAgentNode 迭代循环进入错误状态
- `alignment_score` 超出 0-1 范围无法被捕获

---

### TD-005: EPIC-35 P1/P2 共享上下文版本控制缺失（MEDIUM）

**现象**：
- `update_context.py` 的 whitelist 硬编码（`facts.*`, `decisions.*`, etc.）
- 无版本控制，并发重试场景可能丢失更新
- 节点无法配置私有的 shared_context 权限

---

## 4. 依赖关系图（EPIC 实施顺序建议）

```
EPIC-37 (PipelineState 字段)  ← 已完成
    ↓
EPIC-36 (SummaryAgent)        ← 主体已完成，需验证 orchestrator 集成
    ↓
EPIC-38 (JSON Schema 约束)    ← 未实现 ← 最高风险，建议优先
    ↓
EPIC-31 (Skills 机制)         ← 已完成
    ↓
EPIC-32 (Node Task Refactor)  ← 已完成
    ↓
EPIC-34 (Tool Permissions)    ← 部分完成（analyst/architect 缺配置）
    ↓
EPIC-35 (SharedContext P1/P2) ← P0已完成，P1/P2未实现
    ↓
EPIC-33 (MultiDoc Support)    ← 未实现（最复杂，建议最后）
```

---

## 5. 针对各 EPIC 的修改建议

### EPIC-31 修改建议
**状态**：代码层已完成。

**需修正**：
- Story 31.4 指向 `nodes/*/node.yaml`，但实际权威文件是 `autoBMAD/nodes/*/node.yaml`
- 建议在 EPIC-31 文档中添加注释：`nodes/` 目录为废弃目录，所有配置变更应在 `autoBMAD/nodes/` 执行

### EPIC-32 修改建议
**状态**：代码层已完成。

**需修正**：
- Story 32.2 中的 `nodes/analyst/persona.json` 修改，需确认同步修改 `autoBMAD/nodes/analyst/persona.json`
- Story 32.8 的 evaluator.yaml 更新需验证权重求和为 1.0

### EPIC-33 修改建议（全新实现）
**建议实施顺序**：
1. 先扩展 `NodeDeliverableConfig` (in `autoBMAD/nodes/loader.py`) 增加 `max_deliverables: int = 1` 字段
2. 扩展 `CreateDeliverableParams` 增加多文档字段
3. 在 Validator 中添加计数检查
4. 更新 `autoBMAD/nodes/*/node.yaml`（非 `nodes/`）添加 `deliverable.max_deliverables`
5. 最后处理 `NodeResult` 多文档包装

**关键约束**：
- `NodeDeliverableConfig` 在旧版 `nodes/loader.py` 中无 `max_deliverables` 字段，需同步或弃用旧版
- 新 `NodeConfig` 的 `deliverable.format` 在旧版是 `str`，新版是可选项，注意兼容性

### EPIC-34 修改建议
**立即行动**：
- 在 `autoBMAD/nodes/analyst/node.yaml` 添加 `allowed_builtin_tools: ["Read", "Glob"]` 和 `file_permissions`
- 在 `autoBMAD/nodes/architect/node.yaml` 添加相同配置
- EPIC 文档中所有 `nodes/` 路径引用修正为 `autoBMAD/nodes/`

### EPIC-35 修改建议
**P0 已完成**，P1 实施建议：
1. 在 `autoBMAD/nodes/loader.py` 中新增 `NodeSharedContextConfig` dataclass
2. 在 `NodeToolPermissions` 中添加 `shared_context` 字段
3. 所有 `autoBMAD/nodes/*/node.yaml` 添加 `tools.shared_context` 段
4. 更新 `update_context.py` 支持版本控制

### EPIC-36 修改建议
**主体已完成**，需验证：
1. `orchestrator.py` 中 `start_pipeline()` 是否真正调用 `_summarize_referenced_documents()`
2. `resume_pipeline()` 对缺失 summary 的处理逻辑
3. 运行现有测试套件确认 `SummaryAgent` 行为

### EPIC-37 修改建议
**主体已完成**，需验证：
1. `graph.py` 是否正确提取并传递 `docs_context_summary`
2. 测试覆盖率是否达到要求

### EPIC-38 修改建议（优先级最高，立即实施）

**Phase 1（立即）**：
1. 在 `autoBMAD/docuswarm/agents/evaluator_config/schemas.py` 末尾添加 `EVALUATOR_OUTPUT_SCHEMA` 常量
2. 修改 `autoBMAD/docuswarm/llm/session_manager.py::single_prompt()` 添加 `output_format: dict | None = None` 参数
3. 修改 `evaluator.py::_call_llm_with_prompt()` 传入 schema
4. 修改 `evaluator.py::_parse_response()` 优先读取 `structured_output`

**Phase 2**：
1. 在 `create_deliverable_sdk.py` 添加 `submit_execution_report` 工具
2. 更新系统提示
3. 更新 Validator

---

## 6. 工具辅助分析：调试工具推荐

以下工具已存在于 `tools/` 目录，可用于进一步研究：

### 已有工具
- `autoBMAD/docuswarm/tools/file_tools_sdk.py` - 文件读取工具（可用于验证 node.yaml 加载）
- `autoBMAD/docuswarm/tools/search_tools_sdk.py` - 搜索工具（可用于依赖分析）
- `autoBMAD/docuswarm/context/validator.py` - 上下文验证器（需扩展）

### 建议创建的调试工具（针对 EPIC-38）
```python
# tools/debug_evaluator_output.py
# 用于验证 EvaluatorAgent 的实际输出格式
# 对比 structured_output 路径 vs extract_json 路径

async def debug_evaluator_output(pipeline_id: str, node_id: str) -> dict:
    """从 DB 中提取指定 pipeline 的 evaluator 原始输出，分析格式问题"""
    ...
```

---

## 7. 关键文件路径对照表

| EPIC 引用路径 | 实际权威路径 | 状态 |
|-------------|-----------|------|
| `nodes/analyst/node.yaml` | `autoBMAD/nodes/analyst/node.yaml` | 需同步 |
| `nodes/pm/node.yaml` | `autoBMAD/nodes/pm/node.yaml` | 基本同步 |
| `nodes/ux/node.yaml` | `autoBMAD/nodes/ux/node.yaml` | 需验证 |
| `nodes/architect/node.yaml` | `autoBMAD/nodes/architect/node.yaml` | 需同步 |
| `nodes/po/node.yaml` | `autoBMAD/nodes/po/node.yaml` | 基本同步 |
| `autoBMAD/nodes/loader.py` | `autoBMAD/nodes/loader.py` | 权威 |
| `autoBMAD/docuswarm/nodes/loader.py` | **已删除（raise ImportError）** | 废弃 |

---

## 8. 结论与优先级矩阵

| EPIC | 实现进度 | 风险级别 | 建议优先级 |
|------|---------|---------|---------|
| EPIC-37 (docs_context Persistence) | ~90% | LOW | 验证并收尾 |
| EPIC-36 (Summary Agent) | ~80% | LOW | 验证 orchestrator 集成 |
| EPIC-31 (Skills Introduction) | ~95% | LOW | 验收测试 |
| EPIC-32 (Node Task Refactor) | ~90% | LOW | 验收测试 |
| EPIC-38 (JSON Schema Constraint) | 0% | **CRITICAL** | **立即实施 Phase 1** |
| EPIC-34 (Tool Permissions) | ~70% | MEDIUM | 补全 analyst/architect 配置 |
| EPIC-35 (SharedContext P1/P2) | 30% (P0完成) | MEDIUM | P1 下一个冲刺 |
| EPIC-33 (MultiDoc Support) | 0% | HIGH | 架构重设计后实施 |

**最重要的横切关注点**：EPIC-31 至 EPIC-35 的所有 `nodes/` 目录引用，均需重定向到 `autoBMAD/nodes/` 目录，否则配置修改无效。

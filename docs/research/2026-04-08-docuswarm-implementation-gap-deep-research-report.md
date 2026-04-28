# DocuSwarm Deep Reform 实现缺口深度研究报告

**报告日期**: 2026-04-08  
**基于审计文档**: `docs/evaluation/2026-04-08-docuswarm-deep-reform-full-implementation-audit.md`  
**研究范围**: `autoBMAD/docuswarm`  

---

## 执行摘要

本报告基于详细的代码审查和调试工具验证，对 `autoBMAD/docuswarm` 相对于 `docs/research/docuswarm-deep-reform` 方案文档的实现缺口进行了深度研究。

**核心结论**: 当前实现状态为**部分实现，未完成全部方案要求**。

- ✅ 已实现: F4/F5/F7 + docs_context 持久化链路已基本闭环
- ⚠️ 部分实现: Skills 原生发现、多文档验证、shared_context 运行时接线、模板运行时映射
- ❌ 关键缺口: 多文档端到端闭环、update_context 默认运行时、SDK 原生发现机制

---

## 主要发现 (F1-F6)

### F1: Critical - 多文档验证器未适配 Multi-Document 格式

**问题描述**:  
多文档方案仍未形成可运行的端到端闭环。`IndependentAgent` 会正确包装多文档格式，但验证器仍强制要求单文档字段。

**调试结果**:
```
多文档格式验证: valid=False
发现问题:
  - [MISSING_FILE_PATH] deliverable.file_path: required field missing
  - [MISSING_SHA256] deliverable.sha256: required field missing

MaxDeliverablesValidationStrategy:
  - 检测到的文档数: 1 (期望: 4)
  - 未读取 documents[] 数组长度
```

**问题根源**:
1. `IndependentOutputValidationStrategy._validate_deliverable()` (validator.py:668-756)
   - 强制要求顶层 `file_path` 和 `sha256`
   - 未处理 `type: "multi-document"` 的特殊情况

2. `MaxDeliverablesValidationStrategy._detect_document_count()` (validator.py:1288-1306)
   - 只读取 `document_total` 字段
   - 未检查 `documents` 数组的实际长度

3. `IndependentAgent` 包装多文档时未设置 `document_total`

**影响**:
- `architect` / `po` 的多文档工作流可能在验证阶段失败
- `03-document-creation-constraints.md` 的多文档核心目标未完成
- 多文档数据结构存在，但验证器未跟进

**修复建议**:
```python
# 在 _validate_deliverable() 中添加 multi-document 检测
if deliverable.get("type") == "multi-document":
    documents = deliverable.get("documents", [])
    for i, doc in enumerate(documents):
        # 验证每个文档的 file_path 和 sha256
        validate_doc_fields(doc, index=i)
else:
    # 现有的单文档验证逻辑
```

**优先级**: HIGH

---

### F2: High - update_context MCP Server 未在默认运行时创建

**问题描述**:  
`update_context` 工具名已加入 `allowed_tools`，但默认运行时不会创建对应的 MCP server。

**调试结果**:
```
测试 1: NodeToolFilter.get_allowed_tools()
  - update_context 工具: ['mcp__docuswarm-shared-context-analyst__update_context']
  - 结果: update_context 已加入 [OK] allowed_tools

测试 2: create_mcp_servers() 不传 pipeline_id
  - 创建的 servers: ['docuswarm-files-analyst', 'docuswarm-search-analyst', 'docuswarm-deliverable-analyst']
  - shared-context server: [FAIL] 未创建

测试 3: create_mcp_servers(pipeline_id='pipe-123')
  - 创建的 servers: ['docuswarm-files-analyst', 'docuswarm-search-analyst', 'docuswarm-deliverable-analyst', 'docuswarm-shared-context-analyst']
  - shared-context server: [OK] 已创建
```

**问题根源**:
1. `NodeToolFilter.get_allowed_tools()` - 只要 `shared_context.enabled == true` 就加入工具名
2. `NodeToolFilter.create_mcp_servers()` - 只有传入 `pipeline_id` 时才创建 shared-context server
3. `SessionManager._create_options()` - 调用 `node_filter.create_mcp_servers()` 时不传 `pipeline_id`
4. `IndependentAgent._create_pipeline_session_manager()` - 未传递 `pipeline_id` 给 SessionManager

**调用链断裂**:
```
Pipeline (知道 pipeline_id)
  -> IndependentAgent.execute() (有 pipeline_id)
    -> _create_pipeline_session_manager() (不传 pipeline_id)
      -> SessionManager.__init__() (无 pipeline_id 参数)
        -> _create_options()
          -> node_filter.create_mcp_servers() (无 pipeline_id 参数)
            -> 不创建 shared-context server
```

**修复建议**:
1. 修改 `SessionManager.__init__()` 添加 `pipeline_id` 参数
2. `IndependentAgent._create_pipeline_session_manager()` 传递 `pipeline_id`
3. `SessionManager._create_options()` 使用 `self._pipeline_id`

**优先级**: HIGH

---

### F3: High - SDK 原生 Skills 发现机制因 cwd 路径问题失效

**问题描述**:  
SDK 原生 Skills 配置已写入，但 `cwd` 指向 pipeline 输出目录而非项目根目录，导致原生发现机制失效。

**调试结果**:
```
项目结构:
  - 项目根目录: D:\GITHUB\DocuSwarm
  - Skills 目录: D:\GITHUB\DocuSwarm\.claude\skills
  - 模拟输出目录: D:\GITHUB\DocuSwarm\output\pipe-123

发现 Skills: 45 个
  - bmad-advanced-elicitation
  - bmad-product-brief
  ...

测试 1: 旧方式创建 SessionManager (仅 work_dir)
  cwd: D:\GITHUB\DocuSwarm\output\pipe-123
  output_dir: D:\GITHUB\DocuSwarm\output\pipe-123
  cwd 指向项目根目录: [FAIL] 否

测试 2: 新方式创建 SessionManager (cwd + output_dir)
  cwd: D:\GITHUB\DocuSwarm
  output_dir: D:\GITHUB\DocuSwarm\output\pipe-123
  cwd 指向项目根目录: [OK] 是

测试 3: allowed_tools 配置
  包含 'Skill' 工具: [FAIL] 否 (sdk_native_skills_disabled)
```

**问题根源**:
1. `Orchestrator._create_session_manager()` - 只传 `work_dir`，不传 `cwd`
2. `IndependentAgent._create_pipeline_session_manager()` - 同样只传 `work_dir`
3. `SessionManager.__init__()` - 当只传 `work_dir` 时，`cwd = work_dir`

**SDK Skills 发现机制**:
- `setting_sources = ["project"]` 时，SDK 从 `cwd` 查找 `.claude/skills/`
- 当前 `cwd = output/pipe-xxx`，而非项目根目录
- 结果: 原生 Skills 自动发现失败

**修复建议**:
方案 A (推荐): 显式传递 cwd
```python
SessionManager(
    cwd=project_root,           # 项目根目录
    output_dir=work_dir,        # pipeline 输出目录
    node_id=node_id,
    ...
)
```

方案 B: SessionManager 自动检测项目根目录
- 向上查找包含 `.claude/skills/` 的目录

**优先级**: HIGH

---

### F4: High - 模板运行时映射率低 (仅 20%)

**问题描述**:  
模板体系只完成了路径修复，节点配置与模板 ID 大量不匹配，运行时模板映射率仅 20%。

**调试结果**:
```
发现模板文件:
  - analyst_templates.yaml: 3 个模板
    - market_research, user_personas, risk_assessment
  - architect_templates.yaml: 3 个模板
    - system_architecture, api_specification, database_schema
  - pm_templates.yaml: 2 个模板
    - prd, risk_assessment
  - po_templates.yaml: 4 个模板
    - product_vision, roadmap, epic_list, story_list
  - ux_templates.yaml: 4 个模板
    - user_personas, user_flows, wireframes, usability_testing

发现节点配置:
  - analyst: deliverable_type='product-brief'
  - architect: deliverable_type='architecture'
  - pm: deliverable_type='prd'
  - po: deliverable_type='epics-stories'
  - ux: deliverable_type='ux-design'

模板匹配测试:
  analyst: lookup='product-brief' -> [FAIL] 未匹配
  architect: lookup='architecture' -> [FAIL] 未匹配
  pm: lookup='prd' -> [OK] 匹配 (template='prd')
  po: lookup='epics-stories' -> [FAIL] 未匹配
  ux: lookup='ux-design' -> [FAIL] 未匹配

模板匹配率: 1/5 (20.0%)
```

**问题根源**:
1. 查找 key 不匹配
   - 节点配置使用 `deliverable_type: "product-brief"`
   - 但模板文件使用 `template_id: "market_research"`
   - 两者命名空间不一致

2. 多文档模板映射缺失
   - PO 节点配置 `document_types: [product-vision, roadmap, epic-list, story-list]`
   - 但 `ContractBuilder._load_node_template()` 只按单个 key 查找
   - 无法为多文档分别加载对应模板

3. `ContractBuilder` 查找逻辑
   - 使用 `template_title` 或回退到 `deliverable_type`
   - 与模板文件中的 `template_id` 不匹配

**修复建议**:
1. 标准化模板 ID 或添加显式 `template_id` 配置
2. 多文档节点支持 `template_mapping` 配置
3. 改进 `ContractBuilder` 的查找逻辑，支持模糊匹配

**优先级**: MEDIUM

---

### F5: Medium - shared_context.allowed_keys 未传递到 UpdateContextTool

**问题描述**:  
节点级 `allowed_keys` 配置已存在，但运行时 MCP server 仍只使用全局白名单。

**调试结果**:
```
测试 1: UpdateContextTool 构造函数
  自定义 allowed_keys: ['custom.facts.*', 'custom.decisions.*']
  Effective whitelist: ['facts.', 'decisions.', 'open_questions', 'doc_summaries.', 'notes', 'custom.facts.*', 'custom.decisions.*']
  自定义 key 是否生效: [OK] 是
  Whitelist 来源: node_extended

测试 2: create_update_context_server 参数
  参数: ['pipeline_id', 'node_id', 'allowed_operations']
  包含 allowed_keys 参数: [FAIL] 否

测试 3: NodeToolFilter.create_mcp_servers() 调用
  create_update_context_server 调用:
    create_update_context_server(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        allowed_operations=self.tool_permissions.shared_context.operations,
    )
  传递 allowed_keys: [FAIL] 否

配置了 allowed_keys 的节点数: 0
```

**问题根源**:
```python
# NodeToolFilter.create_mcp_servers() (llm/tool_filter.py:259-266)
update_server = create_update_context_server(
    pipeline_id=pipeline_id,
    node_id=self.node_id,
    allowed_operations=self.tool_permissions.shared_context.operations,
    # ❌ 没有传递 allowed_keys!
)

# create_update_context_server (tools/update_context_sdk.py:19-23)
def create_update_context_server(
    pipeline_id: str,
    node_id: str,
    allowed_operations: list[str] | None = None,
    # ❌ 没有 allowed_keys 参数!
):
    tool = UpdateContextTool(
        state_manager=StateManager(),
        pipeline_id=pipeline_id,
        # ❌ 没有传递 allowed_keys!
    )
```

**数据流断裂**:
```
node.yaml (有 allowed_keys)
  -> NodeLoader (解析 allowed_keys)
    -> NodeSharedContextConfig (存储 allowed_keys)
      -> NodeToolFilter (可读取 allowed_keys)
        -> create_update_context_server (❌ 不接收 allowed_keys)
          -> UpdateContextTool (❌ 收不到 allowed_keys)
```

**修复建议**:
1. `create_update_context_server()` 添加 `allowed_keys` 参数
2. `NodeToolFilter.create_mcp_servers()` 传递 `allowed_keys`
3. 确保 `UpdateContextTool` 正确接收

**优先级**: MEDIUM

---

### F6: Resolved - Analyst 节点配置已确认为设计决策

**状态**: ✅ **已解决** - 经审查确认，当前配置为有意设计决策

**说明**:  
Analyst 节点的 `deliverable.required_sections` 配置与早期参考文档存在差异，但这**不是实现缺口**，而是 F7 Fix 后的**有意设计决策**。

**配置对比**:
| 配置项 | 旧参考文档 | 当前实现 (analyst/node.yaml) | 说明 |
|--------|-----------|------------------------------|------|
| `task.name` | conduct-product-discovery | create-product-brief | F7 Fix: 任务语义重构 |
| `task.skill_ref` | bmad-product-discovery | bmad-product-brief | F7 Fix: 使用实际存在的 skill |
| `required_sections` | product_overview, market_context, competitive_landscape... | executive_summary, product_vision, target_users, value_proposition, key_features, success_metrics | 设计决策：聚焦产品简报 |
| `questions` | 关注已有材料 | 关注产品愿景/价值主张 | 与 skill 语义一致 |

**设计意图**:  
当前配置聚焦于**产品简报 (Product Brief)** 的创建，而非传统的市场研究。章节设计更符合 `bmad-product-brief` skill 的输出要求：
- `executive_summary` - 执行摘要
- `product_vision` - 产品愿景
- `target_users` - 目标用户
- `value_proposition` - 价值主张
- `key_features` - 关键特性
- `success_metrics` - 成功指标

**结论**:  
- ✅ 当前 `analyst/node.yaml` 配置是**正确且有意的设计**
- ✅ `02-node-configurations-reference.md` 已更新以反映实际实现
- ✅ 与 `bmad-product-brief` skill 语义完全一致

**优先级**: N/A (已解决)

---

## 已实现部分验证

### ✅ docs_context_summary 传递链已闭环

验证结果: 完整实现

- `PipelineState` 包含 `docs_context_summary`
- `orchestrator` 在 summary 阶段转换 `DocumentSummary`
- `PipelineAdapter` 注入 `docs_context_summary` 到 `original_context`
- `IndependentAgentInput` 包含 `docs_context`
- `IndependentAgent.execute_with_input()` 传递 `docs_context`

### ✅ SummaryAgent 返回类型问题已修复

验证结果: 已修复

- `SummaryAgent.summarize_context()` 返回 `list[DocumentSummary]`
- `orchestrator` 在进入 state 前调用 `to_dict()`

### ✅ Analyst 任务语义重构已落地 (F7)

验证结果: 已实现

- `task.name = create-product-brief`
- `skill_ref = bmad-product-brief`
- 节点白名单包含目标 skill

### ✅ shared_context 持久化基础设施已实现

验证结果: 已实现

- `StateManager.update_shared_context()` 管理版本和时间戳
- `shared_context_history` 表已存在
- 节点执行后从 DB 刷新最新 `shared_context`

### ✅ 多文档基础数据结构已补入

验证结果: 结构已存在

- `CreateDeliverableParams` 支持多文档字段
- MCP schema 已补入多文档字段
- `NodeResult` 具备多文档属性

**注意**: 数据结构已准备，但验证器未跟进

---

## 文档覆盖矩阵

| 文档 | 实现状态 | 主要缺口 |
|------|----------|----------|
| 01-skills-introduction-mechanism.md | 部分实现 | cwd 未指向项目根，原生发现链路可疑 |
| 02-node-task-skill-mapping.md | 大部分实现 | 少量配置细节漂移 |
| 02-node-configurations-reference.md | 部分实现 | Analyst 详细章节与参考不一致 |
| 03-document-creation-constraints.md | 部分实现 | 多文档 validator、模板映射未闭环 |
| 04-tool-permissions-configuration.md | 大部分实现 | shared-context runtime server 缺口 |
| 05-shared-context-update-mechanism.md | 部分实现 | 运行时 server 暴露、allowed_keys 未落地 |
| 06-summary-agent-design.md | 已实现 | 无 |
| 07-docs-context-persistence.md | 已实现 | 无 |
| F6-F7-F8-executive-summary.md | 部分实现 | ~~F6~~ ✅ 已解决 / F8 未完全闭环 |

---

## 修复优先级建议

### P0 (立即修复)
1. **F1 - 多文档验证器**: 修复 `validator.py` 以支持 multi-document 格式
2. **F2 - update_context 链路**: 打通 `pipeline_id` 传递链
3. **F3 - SDK Skills 发现**: 确保 `cwd` 指向项目根目录

### P1 (短期修复)
4. **F4 - 模板映射**: 标准化模板 ID 或添加显式映射配置
5. **F5 - allowed_keys 传递**: 补全参数传递链

### P2 (长期优化)
6. ~~**F6 - 配置同步**: 更新参考文档或调整配置~~ ✅ **已解决** - 确认为设计决策，参考文档已更新

---

## 调试工具清单

本次研究创建了以下调试工具:

| 工具 | 用途 | 位置 |
|------|------|------|
| docuswarm_f1_multidoc_validator_debugger.py | 验证多文档格式问题 | tools/ |
| docuswarm_f2_update_context_debugger.py | 测试 update_context server 创建 | tools/ |
| docuswarm_f3_sdk_skills_debugger.py | 验证 SDK Skills cwd 路径问题 | tools/ |
| docuswarm_f4_template_mapping_debugger.py | 分析模板映射率 | tools/ |
| docuswarm_f5_allowed_keys_debugger.py | 测试 allowed_keys 传递 | tools/ |
| docuswarm_f6_config_drift_debugger.py | 对比 Analyst 配置漂移 | tools/ |
| docuswarm_all_findings_runner.py | 批量运行所有调试工具 | tools/ |

---

## 结论

`autoBMAD/docuswarm` **尚未满足** `docs/research/docuswarm-deep-reform` 全部方案文档的实现要求。

**判定**: 未完成

**已通过**:
- `SummaryAgent + docs_context_summary + persistence`
- `Analyst task/skill_ref 重构`
- `shared_context` 的持久化与版本化基础设施

**未通过**:
- `多文档端到端运行时闭环` (F1)
- `update_context 默认运行时接线` (F2)
- `SDK 原生 Skills 的项目级自动发现` (F3)
- `大多数节点的模板运行时映射` (F4)
- `shared_context.allowed_keys 细粒度权限接线` (F5)

建议按优先级逐步修复上述问题，以完成 Deep Reform 方案的全部实现。

---

*报告由深度研究调试工具生成*
*基于审计文档: 2026-04-08-docuswarm-deep-reform-full-implementation-audit.md*

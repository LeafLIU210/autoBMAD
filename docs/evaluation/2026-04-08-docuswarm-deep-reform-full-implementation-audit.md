# 2026-04-08 DocuSwarm Deep Reform 全量实现审查报告

## 总结论

`autoBMAD/docuswarm` **尚未满足** `docs/research/docuswarm-deep-reform` 全部方案文档的全部实现要求。

当前状态更准确地说是：

- `F4 / F5 / F7 / docs_context 持久化链路` 已基本闭环
- `Skills 原生发现`、`多文档端到端闭环`、`shared_context 运行时接线`、`模板运行时映射` 仍有关键缺口
- `03-document-creation-constraints.md` 和 `05-shared-context-update-mechanism.md` 中的若干核心方案只完成了“配置层/数据结构层”，尚未完全落到默认运行时链路

结论判定：**部分实现，未达“全部文档方案内容全部实现”**

---

## 审查范围

本次审查覆盖以下方案文档与对应实现：

- `docs/research/docuswarm-deep-reform/01-skills-introduction-mechanism.md`
- `docs/research/docuswarm-deep-reform/02-node-task-skill-mapping.md`
- `docs/research/docuswarm-deep-reform/02-node-configurations-reference.md`
- `docs/research/docuswarm-deep-reform/03-document-creation-constraints.md`
- `docs/research/docuswarm-deep-reform/04-tool-permissions-configuration.md`
- `docs/research/docuswarm-deep-reform/05-shared-context-update-mechanism.md`
- `docs/research/docuswarm-deep-reform/06-summary-agent-design.md`
- `docs/research/docuswarm-deep-reform/07-docs-context-persistence.md`
- `docs/research/docuswarm-deep-reform/F6-F7-F8-executive-summary.md`
- `docs/research/docuswarm-deep-reform/F3-F4-F5-implementation-gap-research-report.md`

对应代码审查范围包括：

- `autoBMAD/nodes/*.yaml`
- `autoBMAD/nodes/loader.py`
- `autoBMAD/docuswarm/agents/*.py`
- `autoBMAD/docuswarm/context/*.py`
- `autoBMAD/docuswarm/llm/*.py`
- `autoBMAD/docuswarm/node_execution/*.py`
- `autoBMAD/docuswarm/pipeline/*.py`
- `autoBMAD/docuswarm/prompts/*.py`
- `autoBMAD/docuswarm/storage/*.py`
- `autoBMAD/docuswarm/tools/*.py`
- `autoBMAD/docuswarm/templates/*.yaml`

---

## 审查方法

本报告基于三类证据：

1. 方案文档逐项提炼后的代码走读
2. 关键调用链的静态路径追踪
3. 最小复现实验

本次实际执行的最小复现实验包括：

- 用 `ContextValidator.validate_independent_output()` 验证当前多文档包装格式
- 用 `NodeToolFilter` 对比 `allowed_tools` 与 `create_mcp_servers()` 的实际 server 输出
- 用 `ContractBuilder._load_node_template()` 验证当前节点配置对模板 YAML 的命中情况

未执行完整 `pytest` 全量回归；结论以源码证据和针对性验证脚本为主。

---

## 主要发现

### F1. Critical: 多文档方案仍未形成可运行的端到端闭环

`03-document-creation-constraints.md` 明确要求 validator 能识别并验证多文档包装格式，尤其是 `deliverable.type == "multi-document"` 时应校验 `deliverable.documents[]`（`03-document-creation-constraints.md:1302-1338`）。

当前实现的问题链条如下：

- `IndependentAgent` 在解析多个 `submit_execution_report` 结果时，会把它们包装成：
  - `deliverable.type = "multi-document"`
  - `deliverable.documents = [...]`
  - 见 `autoBMAD/docuswarm/agents/independent.py:622-636`
- 但 `IndependentOutputValidationStrategy._validate_deliverable()` 仍然强制要求顶层 `deliverable.file_path` 和 `deliverable.sha256`
  - 见 `autoBMAD/docuswarm/context/validator.py:668-756`
- 同一个 validator 的 `MaxDeliverablesValidationStrategy` 仍只通过顶层 `document_total` 推断文档数量，不读取 `deliverable.documents[]`
  - 见 `autoBMAD/docuswarm/context/validator.py:1237-1306`
- `IndependentAgent` 对 LLM 的强制工具使用示例依然是单文档版 `submit_execution_report`
  - 见 `autoBMAD/docuswarm/agents/independent.py:150-271`

最小复现实验结果：

```text
valid= False
deliverable.file_path MISSING_FILE_PATH deliverable.file_path: required field missing
deliverable.sha256 MISSING_SHA256 deliverable.sha256: required field missing
```

影响：

- `architect` / `po` 的多文档工作流仍可能在解析或校验阶段失败
- `03-document-creation-constraints.md` 的“向后兼容多文档包装”方案没有真正跑通
- 现有 `NodeResult.documents`、`create_deliverable` 多文档参数、`submit_execution_report` 多文档 schema 只完成了局部结构，未形成完整运行时闭环

判定：**`03-document-creation-constraints.md` 的多文档核心目标未完成**

---

### F2. High: `update_context` 被加入 allowed_tools，但默认运行时并不会创建对应 MCP server

`05-shared-context-update-mechanism.md` 和 `F6-F7-F8-executive-summary.md` 的目标是让 `update_context` 进入真实运行时链路，而不是只停留在“有 server factory / 有工具名”。

当前链路存在明显断裂：

- `NodeToolFilter.get_allowed_tools()` 只要 `shared_context.enabled == true`，就会把 `mcp__docuswarm-shared-context-{node}__update_context` 放入 `allowed_tools`
  - 见 `autoBMAD/docuswarm/llm/tool_filter.py:170-176`
- 但 `NodeToolFilter.create_mcp_servers()` 只有在显式传入 `pipeline_id` 时才会创建 shared-context server
  - 见 `autoBMAD/docuswarm/llm/tool_filter.py:181-276`
- `SessionManager._create_options()` 实际调用的是 `node_filter.create_mcp_servers()`，没有传 `pipeline_id`
  - 见 `autoBMAD/docuswarm/llm/session_manager.py:303-305`
- `IndependentAgent._create_pipeline_session_manager()` 也没有把 `pipeline_id` 传给 `SessionManager`
  - 见 `autoBMAD/docuswarm/agents/independent.py:1061-1080`

最小复现实验结果：

```text
allowed_tools_update= ['mcp__docuswarm-shared-context-analyst__update_context']
servers_without_pipeline_id= ['docuswarm-deliverable-analyst', 'docuswarm-files-analyst', 'docuswarm-search-analyst']
servers_with_pipeline_id= ['docuswarm-deliverable-analyst', 'docuswarm-files-analyst', 'docuswarm-search-analyst', 'docuswarm-shared-context-analyst']
```

影响：

- 默认执行路径下，Agent 看到 `update_context` 工具名，但 runtime 不一定真的有对应 server
- `05-shared-context-update-mechanism.md` 的“运行时 MCP 暴露链路”仍未闭环
- `04-tool-permissions-configuration.md` 中“所有节点统一开放工具”的 shared-context 部分只能算部分实现

判定：**F6 在当前代码中仍是部分修复，不是完全完成**

---

### F3. High: SDK 原生 Skills 配置已经写入，但 `cwd` 仍不指向项目根目录，原生发现机制大概率失效

`01-skills-introduction-mechanism.md` 明确写到，SDK 通过 `setting_sources=["project"]` 发现 `.claude/skills/` 的前提，是 `cwd` 必须指向包含 `.claude/skills/` 的项目根目录（`01-skills-introduction-mechanism.md:93-113`、`730-745`、`1011-1014`）。

当前代码状态：

- `SessionManager` 已经在 options 中设置：
  - `setting_sources = ["project"]`
  - `allowed_tools` 里包含 `"Skill"`
  - 见 `autoBMAD/docuswarm/llm/session_manager.py:249-253`
- 但 orchestrator 和 independent agent 创建 `SessionManager` 时，传入的都是 pipeline 目录 / output 目录作为 `work_dir`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:171-180`
  - `autoBMAD/docuswarm/agents/independent.py:1072-1080`
- `SessionManager.__init__()` 在只传 `work_dir` 时，会把 `_cwd` 和 `_output_dir` 都设为 `work_dir`
  - 见 `autoBMAD/docuswarm/llm/session_manager.py:91-107`

最小复现实验结果：

```text
cwd= D:\GITHUB\DocuSwarm\output\pipe-123
output_dir= D:\GITHUB\DocuSwarm\output\pipe-123
```

而项目技能实际位于：

- `D:\GITHUB\DocuSwarm\.claude\skills`

这意味着：

- quick reference 注入可能工作
- 但 SDK 原生 `Skill` 工具的项目级自动发现，仍很可能从错误目录启动

影响：

- `01-skills-introduction-mechanism.md` 的“原生 Skills 自动发现机制”没有完成最后一公里
- `02-node-task-skill-mapping.md` 中 `skill_ref -> SDK Skills` 的运行时承诺只能算“部分实现”

判定：**Skills 方案是“配置完成，运行时路径仍可疑”**

说明：这里的“失效”是基于文档约束与当前 `cwd` 路径的强推断，未在真实 SDK 会话里做联网交互验证。

---

### F4. High: 模板体系只完成了路径修复，尚未完成运行时模板映射和多模板注入

`03-document-creation-constraints.md` 的模板方案要求：

- `TemplateLoader` 能读取模板目录
- `contract_builder` 能把模板内容注入 prompt
- 各节点配置能映射到正确模板
- `po` / `architect` 等多文档节点支持多模板/多文档模板元数据

当前实现只完成了其中一部分：

- `TemplateLoader.DEFAULT_TEMPLATES_DIR` 已修正到 `docuswarm/templates`
  - 见 `autoBMAD/docuswarm/prompts/template_loader.py:88-99`
- `ContractBuilder` 仍只按单个 key 查模板：
  - `template_title` 或回退到 `deliverable_type`
  - 见 `autoBMAD/docuswarm/prompts/contract_builder.py:219-244`
- `ContextManager` 默认把 `template_title` 回退为 `node_config.deliverable_type`
  - 见 `autoBMAD/docuswarm/context/isolation.py:143-161`

但当前节点配置与模板 ID 大量不匹配：

- `analyst`: `product-brief`，无匹配模板
- `ux`: `ux-design`，无匹配模板
- `architect`: `Technical Specification: {project_name}`，无匹配模板
- `po`: `epics-stories`，无匹配模板
- `pm`: `prd`，可命中

最小复现实验结果：

```text
analyst lookup= product-brief matched= None
pm lookup= prd matched= prd
ux lookup= ux-design matched= None
architect lookup= Technical Specification: {project_name} matched= None
po lookup= epics-stories matched= None
```

另外，研究文档为 `po_templates.yaml` 提出的多文档元数据结构包含：

- `document_index`
- `document_total`
- `required_sections`

但当前模板 YAML 仍主要是 `sections` 描述，尚未承担方案里定义的多文档模板元数据职责。

影响：

- 模板资产“存在于仓库”并不等于“被运行时消费”
- `03-document-creation-constraints.md` 的模板对齐目标只完成了文件落地，没有完成大多数节点的有效接线
- `F8` 当前应判定为“部分修复”，不是“已完成”

---

### F5. Medium: `shared_context.allowed_keys` 已可配置，但运行时没有真正传给 `UpdateContextTool`

方案文档要求 `shared_context` 白名单可配置，节点级配置应能覆盖/扩展全局规则。

当前代码显示：

- `NodeLoader` 已能解析 `tools.shared_context.allowed_keys`
  - 见 `autoBMAD/nodes/loader.py:152-166`、`488-520`
- `UpdateContextTool` 构造函数也支持 `allowed_keys`
  - 见 `autoBMAD/docuswarm/tools/update_context.py:70-126`
- 但 `NodeToolFilter.create_mcp_servers()` 只把 `allowed_operations` 传给 `create_update_context_server()`
  - 见 `autoBMAD/docuswarm/llm/tool_filter.py:259-266`
- `create_update_context_server()` 又只用 `pipeline_id` 和 `allowed_operations` 构造 `UpdateContextTool`
  - 见 `autoBMAD/docuswarm/tools/update_context_sdk.py:19-23`、`91-95`

结果就是：

- 节点级 `allowed_keys` 已在配置层和工具类层存在
- 但默认运行时 MCP server 仍只使用全局白名单

影响：

- `05-shared-context-update-mechanism.md` 的“可配置白名单”没有完整落地
- 节点级细粒度共享上下文权限仍未真正生效

判定：**shared_context 细粒度权限仍是未闭环项**

---

### F6. Medium: Analyst 节点虽已完成任务语义重构，但仍与配置参考文档存在内容漂移

`02-node-configurations-reference.md` 给出了 Analyst 的详细配置参考：

- `required_sections` 为：
  - `product_overview`
  - `market_context`
  - `competitive_landscape`
  - `value_proposition`
  - `target_users`
  - `executive_summary`
  - 见 `02-node-configurations-reference.md:25-33`
- 问题项以“产品想法/目标用户/是否有已有材料”为核心
  - 见 `02-node-configurations-reference.md:44-53`

当前 `autoBMAD/nodes/analyst/node.yaml` 已经完成：

- `task.name = create-product-brief`
- `skill_ref = bmad-product-brief`

但交付物章节和问题集合已经明显改写：

- 当前 `required_sections` 是：
  - `executive_summary`
  - `product_vision`
  - `target_users`
  - `value_proposition`
  - `key_features`
  - `success_metrics`
  - 见 `autoBMAD/nodes/analyst/node.yaml:43-51`
- 当前问题是“product vision / target users / unique value proposition”
  - 见 `autoBMAD/nodes/analyst/node.yaml:62-69`

影响：

- 如果把 `02-node-configurations-reference.md` 视为需要严格兑现的方案文档，则 Analyst 配置仍与参考实现不一致
- 如果团队接受后续方案漂移，则该项可降级为“文档过时 / 需要同步更新”

判定：**F7 主问题已修复，但详细配置参考未完全对齐**

---

## 已实现或基本实现的部分

以下内容已经能在当前代码中确认成立：

### 1. `docs_context_summary` 传递链已闭环

- `PipelineState` 已包含 `docs_context_summary`
  - `autoBMAD/docuswarm/pipeline/state.py:79-120`
- `orchestrator` 在 summary 阶段已将 `DocumentSummary` 转成 `dict`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:237-292`
- `PipelineAdapter` 会把 `docs_context_summary` 注入 `original_context`
  - `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:204-212`
- `NodeExecutionContextBuilder` 优先读取缓存摘要
  - `autoBMAD/docuswarm/node_execution/context_builder.py:58-88`
- `IndependentAgentInput` 已正式包含 `docs_context`
  - `autoBMAD/docuswarm/node_execution/contracts.py:41-53`
- `ContextManager` 和 `IndependentAgent.execute_with_input()` 已把 `docs_context` 向下传递
  - `autoBMAD/docuswarm/context/isolation.py:166-179`
  - `autoBMAD/docuswarm/agents/independent.py:966-981`

判定：**`06-summary-agent-design.md` 与 `07-docs-context-persistence.md` 的主链路已实现**

### 2. SummaryAgent 返回类型不一致问题已修复

- `SummaryAgent.summarize_context()` 仍返回 `list[DocumentSummary]`
  - `autoBMAD/docuswarm/agents/summary.py:564-581`
- 但 `orchestrator` 已在进入 state 前做 `to_dict()`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:282-292`

判定：**原 F5 缺口已关闭**

### 3. Analyst 任务语义重构已落地

- `task.name = create-product-brief`
- `skill_ref = bmad-product-brief`
- 节点白名单包含目标 skill

对应代码：

- `autoBMAD/nodes/analyst/node.yaml:15-40`

判定：**原 F7 主问题已关闭**

### 4. shared_context 的版本控制、历史表和执行后 DB 刷新已实现

- `StateManager.update_shared_context()` 已管理 `_metadata.version` / `_metadata.updated_at`
  - `autoBMAD/docuswarm/storage/state_manager.py:557-758`
- `shared_context_history` 表已存在
  - `autoBMAD/docuswarm/storage/database.py:238-264`
- 节点执行后会从 DB 刷新最新 `shared_context`
  - `autoBMAD/docuswarm/node_execution/executor.py:213-233`
  - `autoBMAD/docuswarm/node_execution/executor.py:357-413`

判定：**`05-shared-context-update-mechanism.md` 的持久化基础设施已实现**

### 5. 多文档基础数据结构已补入

- `CreateDeliverableParams` 已支持：
  - `document_index`
  - `document_total`
  - `document_type`
  - `autoBMAD/docuswarm/tools/create_deliverable.py:28-89`
- MCP `create_deliverable` / `submit_execution_report` schema 已补入多文档字段
  - `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:28-117`
  - `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:293-340`
- `NodeResult` 已具备 `documents` / `is_multi_document` / `all_documents`
  - `autoBMAD/docuswarm/nodes/dual_agent.py:51-87`

判定：**多文档的“数据结构准备”已做，但“校验与运行时闭环”未完成**

---

## 文档覆盖矩阵

| 文档 | 实现状态 | 结论 |
|------|----------|------|
| `01-skills-introduction-mechanism.md` | 部分实现 | `Skill` 工具、`setting_sources`、白名单、quick reference 已落地，但 `cwd` 未指向项目根，原生发现链路仍可疑 |
| `02-node-task-skill-mapping.md` | 大部分实现 | `skill_ref`、节点白名单、Analyst 任务语义已落地；少量配置细节与参考文档漂移 |
| `02-node-configurations-reference.md` | 部分实现 | 核心字段大多到位，但 Analyst 详细章节/问题项与参考配置不一致 |
| `03-document-creation-constraints.md` | 部分实现 | 单文档约束与多文档数据结构已做；多文档 validator、模板映射、多模板注入未闭环 |
| `04-tool-permissions-configuration.md` | 大部分实现 | 文件/搜索/交付物权限链路已通；shared-context runtime server 仍受 `pipeline_id` 传递缺口影响 |
| `05-shared-context-update-mechanism.md` | 部分实现 | 持久化、版本控制、历史记录、DB 刷新已实现；运行时 server 暴露与 `allowed_keys` 仍未完全落地 |
| `06-summary-agent-design.md` | 已实现 | Pre-pipeline summary、state 注入、下游读取链路已完成 |
| `07-docs-context-persistence.md` | 已实现 | `PipelineState`、adapter 注入、resume 恢复已完成 |
| `F6-F7-F8-executive-summary.md` | 部分实现 | F7 已修复，F6/F8 仍未完全闭环 |
| `F3-F4-F5-implementation-gap-research-report.md` | 部分实现 | F4/F5 已修复；F3 仍存在，但表现形态已从“完全缺失”变成“结构已补、validator 未跟进” |

---

## 最终判定

从“是否满足全部深改方案内容”的角度，本仓库当前应判定为：

**未完成**

更具体地说：

- 方案级通过项：
  - `SummaryAgent + docs_context_summary + persistence`
  - `Analyst task/skill_ref 重构`
  - `shared_context` 的持久化与版本化基础设施
- 方案级未通过项：
  - `多文档端到端运行时闭环`
  - `update_context` 默认运行时接线
  - `SDK 原生 Skills 的项目级自动发现`
  - `大多数节点的模板运行时映射`
  - `shared_context.allowed_keys` 细粒度权限接线

---

## 建议整改顺序

1. 先修复多文档 validator 与多文档 prompt/submit 报告指导，使 `architect` / `po` 真正可运行。
2. 再修复 `SessionManager -> NodeToolFilter.create_mcp_servers()` 的 `pipeline_id` 传递，打通 `update_context` 默认 runtime 链路。
3. 把 `SessionManager.cwd` 改为仓库根目录，`output_dir` 单独保留为输出路径，完成 SDK native skills 的最后一公里。
4. 重做模板映射策略，不再把 `deliverable_type` / 展示标题直接当模板 key；应显式配置 `template_id` 或多模板映射。
5. 将 `shared_context.allowed_keys` 透传到 `create_update_context_server()` 和 `UpdateContextTool()`。
6. 决定 `02-node-configurations-reference.md` 是“仍需兑现”还是“已过时”，然后同步代码或同步文档，消除 Analyst 配置漂移。

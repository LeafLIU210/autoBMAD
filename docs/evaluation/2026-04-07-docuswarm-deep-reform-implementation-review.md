# DocuSwarm Deep Reform 实现审查报告

日期: 2026-04-07  
审查对象: `autoBMAD/docuswarm`  
审查基线: `docs/research/docuswarm-deep-reform/` 全部方案文档

## 总结论

结论: **未满足 `docs/research/docuswarm-deep-reform` 全部文档方案内容的全部实现。**

当前代码库已经完成了不少结构层改造，包括:

- `node.yaml` 已扩展 `skill_ref`、`max_deliverables`、`document_types`、`shared_context`
- Evaluator 已接入 SDK `output_format` 结构化输出
- SummaryAgent、`docs_context_summary`、shared context 持久化、multi-document 辅助函数都已落地一部分

但从“方案要求是否真正进入运行时闭环”这个标准看，仍存在数条关键链路未打通，导致若按方案文档宣称的能力理解系统，当前实现会高估实际能力。

## 审查范围

本次审查对照以下研究文档与汇总文档:

- `docs/research/docuswarm-deep-reform/README.md`
- `docs/research/docuswarm-deep-reform/REPORT_SUMMARY.md`
- `docs/research/docuswarm-deep-reform/01-skills-introduction-mechanism.md`
- `docs/research/docuswarm-deep-reform/02-node-task-skill-mapping.md`
- `docs/research/docuswarm-deep-reform/02-node-configurations-reference.md`
- `docs/research/docuswarm-deep-reform/03-document-creation-constraints.md`
- `docs/research/docuswarm-deep-reform/04-tool-permissions-configuration.md`
- `docs/research/docuswarm-deep-reform/05-shared-context-update-mechanism.md`
- `docs/research/docuswarm-deep-reform/06-summary-agent-design.md`
- `docs/research/docuswarm-deep-reform/07-docs-context-persistence.md`
- `docs/research/docuswarm-deep-reform/2026-04-06-json-retry-mcp-schema-constraint-research-report.md`

审查方法:

- 静态核对方案文档与运行时代码路径
- 重点核查“配置是否真正进入 Session / MCP / Prompt / State / Orchestrator”
- 运行定向 pytest，验证关键故事的实现状态

## 主要发现

### F1. Critical: Skills 白名单与 `sdk_native` 开关没有在运行时真正生效

影响文档:

- `01-skills-introduction-mechanism.md`
- `02-node-task-skill-mapping.md`
- `02-node-configurations-reference.md`

方案期望:

- Skills 是否启用应由节点级 `tools.skills.sdk_native` 控制
- Skills 可见范围应受 `tools.skills.whitelist` 限制
- `node.yaml -> SessionManager/ClaudeAgentOptions` 应形成完整闭环

实际实现:

- `SessionManager._build_allowed_tools()` 无条件加入 `"Skill"`，未检查节点 `sdk_native`
- `SessionManager._create_options()` 无条件启用 `setting_sources=["project"]`
- `IndependentAgent.execute_with_input()` 重建 `NodeToolPermissions` 时丢失了 `skills` 与 `shared_context` 子配置，仅保留 builtin/file/search
- `skills.whitelist` 当前只用于 prompt quick reference 注入，不是运行时权限边界

证据:

- `autoBMAD/docuswarm/llm/session_manager.py:173-217`
- `autoBMAD/docuswarm/llm/session_manager.py:238-243`
- `autoBMAD/docuswarm/agents/independent.py:356-376`
- `autoBMAD/docuswarm/agents/independent.py:967-978`
- `autoBMAD/nodes/loader.py:128-188`
- `autoBMAD/nodes/loader.py:488-520`

风险:

- 节点配置声明的 skill 访问边界与实际运行边界不一致
- 方案文档强调的“白名单控制”目前只是提示词约束，不是工具权限约束
- 审计上无法证明某节点只暴露了其被允许的 Skills

### F2. Critical: `submit_execution_report` 已实现但未被允许调用，JSON/MCP 闭环断裂

影响文档:

- `2026-04-06-json-retry-mcp-schema-constraint-research-report.md`
- `03-document-creation-constraints.md`

方案期望:

- IndependentAgent 使用 `create_deliverable` 之后，必须继续调用 `submit_execution_report`
- `submit_execution_report` 应成为结构化 execution report 的主路径

实际实现:

- Agent 系统提示中明确要求两步工具调用序列
- MCP deliverable server 确实注册了 `submit_execution_report`
- 但 `NodeToolFilter.get_allowed_tools()` 只放行 `create_deliverable`，没有放行 `submit_execution_report`
- 结果是: 提示要求调用的工具，运行时 allowed tools 不一定可用

证据:

- `autoBMAD/docuswarm/agents/independent.py:148-171`
- `autoBMAD/docuswarm/agents/independent.py:176-199`
- `autoBMAD/docuswarm/agents/independent.py:248-271`
- `autoBMAD/docuswarm/llm/tool_filter.py:153-159`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:28-83`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:288-318`

风险:

- JSON/MCP 方案文档要求的最小约束路径没有真正可执行
- 运行时会回退到旧的自由文本/JSON 解析路径，削弱方案希望达到的稳定性

### F3. High: Multi-document 方案只实现了局部结构，未形成端到端运行时支持

影响文档:

- `03-document-creation-constraints.md`
- `REPORT_SUMMARY.md`

方案期望:

- Architect / PO 支持多文档
- `create_deliverable`、execution report、state、orchestrator、validator 应共同支持 multi-document

实际实现:

- Python 版 `CreateDeliverableParams` 已支持 `document_index`、`document_total`、`document_type`
- Python 工具返回值也会回填这三个字段
- 但 MCP `create_deliverable` schema 没有暴露这些参数
- `submit_execution_report` schema 仍是单一 `deliverable` 对象，不支持 document set
- IndependentAgent 对 `submit_execution_report` 的提取逻辑只返回第一个报告
- `DualAgentNode` 运行态只维护单个 `final_deliverable`

证据:

- `autoBMAD/docuswarm/tools/create_deliverable.py:24-91`
- `autoBMAD/docuswarm/tools/create_deliverable.py:222-228`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:243-276`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:28-83`
- `autoBMAD/docuswarm/agents/independent.py:545-573`
- `autoBMAD/docuswarm/agents/independent.py:590-612`
- `autoBMAD/docuswarm/nodes/dual_agent.py:284-289`
- `autoBMAD/docuswarm/nodes/dual_agent.py:327-336`
- `autoBMAD/nodes/architect/node.yaml:23-35`
- `autoBMAD/nodes/po/node.yaml:18-32`

风险:

- 节点配置与测试基线已假定 multi-document 能力存在，但真实运行链路仍按 single deliverable 工作
- 方案文档中的多文档约束目前更像“数据模型准备中”，不是“已投产能力”

### F4. High: `docs_context_summary` 已生成并注入 state，但在 IndependentAgent 提示词构建前被丢弃

影响文档:

- `06-summary-agent-design.md`
- `07-docs-context-persistence.md`

方案期望:

- Pipeline 启动时由 SummaryAgent 一次性生成文档摘要
- `docs_context_summary` 持久化进 PipelineState
- 节点执行时复用缓存摘要进入最终 prompt

实际实现:

- `NodeExecutionContextBuilder.build()` 已优先使用 `original_context["docs_context_summary"]`
- `contract_builder` 也确实会把 `docs_context` 渲染进 prompt
- 但 `ContextManager.build_independent_input()` 返回的 `IndependentAgentInput` 不包含 `docs_context`
- `IndependentAgent.execute_with_input()` 重新构造 `NodeExecutionContext` 时，把 `docs_context` 强制设为空列表

证据:

- `autoBMAD/docuswarm/node_execution/context_builder.py:58-88`
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:204-213`
- `autoBMAD/docuswarm/prompts/contract_builder.py:253-259`
- `autoBMAD/docuswarm/context/isolation.py:166-175`
- `autoBMAD/docuswarm/agents/independent.py:923-937`

风险:

- SummaryAgent 与 docs_context 持久化即使成功，也不会进入 IndependentAgent 的实际提示词
- 当前“摘要缓存”更多是 state 层存在，不是 agent 消费链路存在

### F5. High: SummaryAgent 返回类型与 `PipelineState.docs_context_summary` 声明不一致

影响文档:

- `06-summary-agent-design.md`
- `07-docs-context-persistence.md`

方案期望:

- `docs_context_summary` 应为可序列化、可恢复、可消费的统一数据结构

实际实现:

- `PipelineState` 将 `docs_context_summary` 声明为 `list[dict[str, Any]]`
- `create_initial_state()` 也按 dict summary 文档说明实现
- 但 orchestrator 实际存入的是 `list[DocumentSummary]`
- `SummaryAgent.summarize_context()` 返回值也是 `list[DocumentSummary]`
- 若后续代码按 dict 下标读取，将与 dataclass 对象形态冲突

证据:

- `autoBMAD/docuswarm/pipeline/state.py:77-85`
- `autoBMAD/docuswarm/pipeline/state.py:82-120`
- `autoBMAD/docuswarm/agents/summary.py:69-117`
- `autoBMAD/docuswarm/agents/summary.py:564-581`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:237-289`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:422-438`

风险:

- 这会造成 state 持久化/恢复、prompt 渲染、后续序列化之间的契约不稳定
- F4 一旦修复，这个类型不一致会立刻成为下一层运行时问题

### F6. High: `update_context` 工具已实现并有配置入口，但未进入运行时 MCP 暴露链路

影响文档:

- `05-shared-context-update-mechanism.md`
- `04-tool-permissions-configuration.md`

方案期望:

- 节点可按 `shared_context` 权限配置使用 `update_context`
- tool permissions、state persistence、agent runtime 三者闭环

实际实现:

- `UpdateContextTool` 本身实现完整，具备 whitelist、set/append/remove、StateManager 持久化
- 旧 `independent_agent.yaml` 也声明了该工具
- 但 `SessionManager` 明确跳过 `agent_file` 工具接入
- `NodeToolFilter.create_mcp_servers()` 只创建 file/search/deliverable server，没有 update_context server
- `IndependentAgent.execute_with_input()` 重建 `NodeToolPermissions` 时也没有携带 `shared_context`

证据:

- `autoBMAD/docuswarm/tools/update_context.py:21-28`
- `autoBMAD/docuswarm/tools/update_context.py:54-64`
- `autoBMAD/docuswarm/tools/update_context.py:186-215`
- `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:10-15`
- `autoBMAD/docuswarm/llm/session_manager.py:398-406`
- `autoBMAD/docuswarm/llm/tool_filter.py:164-238`
- `autoBMAD/docuswarm/agents/independent.py:967-978`

风险:

- shared context 的状态层与持久化层已经做了，但“Agent 如何在运行时更新它”仍然缺最后一跳
- 方案文档里的共享上下文更新机制当前只能算部分实现

### F7. Medium: Analyst 节点任务语义仍未按研究方案完成重构

影响文档:

- `02-node-task-skill-mapping.md`
- `02-node-configurations-reference.md`

方案期望:

- Analyst 从 `create-business-analysis-report` 重构为 `create-product-brief`
- 任务语义与 `bmad-product-brief` skill 对齐

实际实现:

- 当前 Analyst 仍保留 `create-business-analysis-report`
- 但同时配置了 `skill_ref: bmad-product-brief`

证据:

- `autoBMAD/nodes/analyst/node.yaml:12-16`
- `docs/research/docuswarm-deep-reform/02-node-task-skill-mapping.md`
- `docs/research/docuswarm-deep-reform/02-node-configurations-reference.md`

风险:

- 任务描述、persona、skill 工作流三者仍存在语义错位
- 这会让节点行为落在“旧 analyst 职责 + 新 skill 能力”的混合态

### F8. Medium: 模板对齐更多停留在配置字段层，未形成独立模板目录到运行时提示词的明确接线

影响文档:

- `03-document-creation-constraints.md`
- `02-node-configurations-reference.md`

方案期望:

- BMAD 模板对齐不应只停留在 `template_title` 文字提示，独立模板资源应可被运行时消费

实际实现:

- 节点配置中的 `template_title`、`output_filename`、`format_hints` 已能进入 deliverable requirements
- 但 `TemplateLoader.DEFAULT_TEMPLATES_DIR` 指向 `autoBMAD/docuswarm/prompts/templates`
- 研究中新增的节点模板文件位于 `autoBMAD/docuswarm/templates/`
- 当前运行时路径没有证据表明这些节点模板 YAML 被实际装载进 IndependentAgent prompt 生成流程

证据:

- `autoBMAD/docuswarm/context/isolation.py:141-161`
- `autoBMAD/docuswarm/prompts/contract_builder.py:216-237`
- `autoBMAD/docuswarm/prompts/template_loader.py:88-100`
- `autoBMAD/nodes/architect/node.yaml:34-35`

风险:

- 方案文档所说的“模板对齐”目前主要体现为字段透传和文案提示，不是模板资产的运行时强约束

## 已实现或基本实现的部分

以下内容可以确认已经有明确实现，不应在结论里被误判为“完全缺失”:

- 节点配置模型已支持 `skill_ref`、`max_deliverables`、`document_types`、`skills`、`shared_context`
  - `autoBMAD/nodes/loader.py:52-70`
  - `autoBMAD/nodes/loader.py:128-188`
  - `autoBMAD/nodes/loader.py:450-520`
- 各节点 `node.yaml` 已补充大部分新配置字段
  - `autoBMAD/nodes/pm/node.yaml:11-27`
  - `autoBMAD/nodes/ux/node.yaml:12-26`
  - `autoBMAD/nodes/architect/node.yaml:12-35`
  - `autoBMAD/nodes/po/node.yaml:12-32`
- Evaluator 结构化输出路径已落地
  - `autoBMAD/docuswarm/agents/evaluator.py:373-401`
  - `autoBMAD/docuswarm/agents/evaluator.py:462-513`
- SummaryAgent 已落地并具备并发/重试/关键文件优先机制
  - `autoBMAD/docuswarm/agents/summary.py:1-9`
  - `autoBMAD/docuswarm/agents/summary.py:564-581`
- PipelineState 已预留 `shared_context` 与 `docs_context_summary`
  - `autoBMAD/docuswarm/pipeline/state.py:77-80`
- multi-document 辅助测试和帮助函数已存在，说明方案曾被认真推进
  - `tests/test_document_creation_constraints.py:1-16`
  - `tests/test_document_creation_constraints.py:128-154`

## 研究文档覆盖矩阵

| 文档 | 审查结论 | 说明 |
|---|---|---|
| `01-skills-introduction-mechanism.md` | 部分实现 | Skills 发现与 prompt quick reference 已做，但运行时未按 `sdk_native + whitelist` 真正收口 |
| `02-node-task-skill-mapping.md` | 部分实现 | PM/UX/Architect/PO 基本对齐，Analyst 仍保留旧任务语义 |
| `02-node-configurations-reference.md` | 部分实现 | 配置字段大多存在，但配置到运行时能力的闭环不完整 |
| `03-document-creation-constraints.md` | 部分实现 | 单文档约束与参数扩展存在，多文档端到端运行时未闭环 |
| `04-tool-permissions-configuration.md` | 大体实现 | file/search/deliverable 权限体系已接入，但 shared-context/update-context 这一支未打通 |
| `05-shared-context-update-mechanism.md` | 部分实现 | 持久化与工具实现存在，运行时 MCP 暴露缺失 |
| `06-summary-agent-design.md` | 部分实现 | SummaryAgent 与预缓存存在，但摘要未真正进入 IndependentAgent prompt |
| `07-docs-context-persistence.md` | 部分实现 | state 中已有持久化字段，消费链路断裂且类型契约不稳 |
| `2026-04-06-json-retry-mcp-schema-constraint-research-report.md` | 部分实现 | Evaluator 结构化输出已实现，IndependentAgent 的 `submit_execution_report` 主路径未打通 |
| `README.md` / `REPORT_SUMMARY.md` | 未完全达成 | 汇总文档描述的整体改革成果被部分代码支持，但未达到“全部方案内容均已实现” |

## 测试与验证说明

已尝试运行定向测试:

- `pytest tests/test_submit_execution_report_tool.py tests/test_document_creation_constraints.py tests/test_shared_context.py -q`
- `pytest tests/test_document_creation_constraints.py -x -vv --basetemp .tmp/pytest-review2`

结果:

- 多项早期测试可通过
- 但在当前 Windows 环境下，pytest session teardown 反复触发 temp 目录清理 `PermissionError: [WinError 5]`
- 一次中断点显示运行在 `TestMultiDocumentFieldsHandling::test_metadata_includes_document_fields` 附近时出错，但 teardown 失败导致完整 traceback 未可靠保留

因此，本次测试结论应表述为:

- **定向测试已尝试，但结果不完全可采信**
- **本报告的主结论仍以运行时代码链路审查为准**

## 最终判定

若评判标准是“`docs/research/docuswarm-deep-reform` 全部方案内容是否已经全部实现”，当前答案是:

**否。**

更准确的表述是:

- 配置模型层: 已完成较多
- 数据结构层: 已完成较多
- 单点能力层: 已完成一部分
- 运行时闭环层: 仍有多处关键缺口

最影响结论的阻断项是:

1. Skills 白名单未真正进入运行时权限控制
2. `submit_execution_report` 主路径未真正可调用
3. multi-document 仍未形成端到端能力
4. `docs_context_summary` 生成后未进入 IndependentAgent prompt
5. `update_context` 未进入 MCP 运行时工具链

## 建议整改顺序

1. 先修正 `NodeToolPermissions` 在 `IndependentAgent.execute_with_input()` 中的重建逻辑，保留 `skills` 与 `shared_context`
2. 在 `NodeToolFilter.get_allowed_tools()` 中放行 `submit_execution_report`，并补充其测试
3. 明确 multi-document 的权威数据结构，统一 MCP schema、agent 提取逻辑、DualAgentNode 存储逻辑
4. 打通 `docs_context_summary -> IndependentAgentInput -> NodeExecutionContext -> contract_builder` 的传递链
5. 统一 `docs_context_summary` 的真实类型，选择 `dict` 或 `DocumentSummary.to_dict()`，避免 state 契约漂移
6. 为 `update_context` 增加 MCP server 暴露与权限控制接线
7. 完成 Analyst 节点任务语义重构，并重新核对 persona 与 skill 配置


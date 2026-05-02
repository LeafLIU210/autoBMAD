# refactor-2026-03-26 实现审查报告

**审查对象**
- 方案文档：`docs/research/refactor-2026-03-26/00-refactoring-roadmap.md`
- 子报告：`01-context-validator-extraction.md`、`02-memory-manager-removal.md`、`03-task-contract-removal.md`、`04-node-configuration-reform.md`、`05-claude-agent-sdk-reform.md`
- 实现范围：`autoBMAD/docuswarm`、`autoBMAD/nodes`

**审查日期**
- 2026-04-03

**审查方法**
- 静态代码审查
- 节点配置与运行时调用链对照
- 定向 Python 验证脚本
- 定向 `pytest` 验证

**审查限制**
- 本次 `pytest` 受到当前环境权限限制，`pytest-qt` 在临时目录创建 `pytest-of-Administrator` 时触发 `PermissionError [WinError 5]`，因此 Phase 5 不能仅凭本次会话宣称“已完成闭环验证”。

---

## 1. 执行结论

当前实现相较 `2026-03-28` 之前的状态已经明显推进，尤其是以下几项已经有充分证据表明落地：

- `MemoryManager` 已被彻底移除
- `ContextValidator` 已从分散逻辑中提取为独立组件，并进入主调用链
- Task 契约瘦身基本完成，任务信息已经主要从 `NodeLoader`/`node.yaml` 读取
- v2 `deliverable` 扩展字段已经进入 `NodeLoader` 和 `ContextManager`，旧报告中“字段只写进 YAML、未被运行时消费”的结论已不再成立
- 四层提示词架构和 BMAD 技能注入已进入 IndependentAgent 的主路径

但对照 `refactor-2026-03-26` 的目标，当前实现仍不能判定为“全量完成”。最关键的未闭环点集中在 Phase 4 和 Phase 5：

- **T-G 文件/搜索工具接入仍有关键接线缺陷**
- **节点级 evaluator 配置已可加载，但运行时并未真正按配置消费**
- **测试门禁无法证明完整通过，且现有测试未覆盖这两个关键集成风险**

综合判断：

- **Phase 1：完成**
- **Phase 2：完成**
- **Phase 3：大体完成**
- **Phase 4：部分完成，仍有高优先级缺陷**
- **Phase 5：未能证实完成**

---

## 2. 最高优先级发现

### Finding 1：MCP server 注册存在覆盖风险，T-G 不能视为完成

**严重级别**：高

**结论**

`SessionManager` 已经开始把节点级文件/搜索权限接入主执行链，但当前 `mcp_servers` 的构建方式会把两个不同用途的 FastMCP server 压成一个字典键，导致 T-G 的“文件读取 + 搜索工具完整接入”不能视为可靠完成。

**证据**

1. `IndependentAgent.execute_with_input()` 已从节点配置读取工具权限，并把 `file_dirs` / `search_dirs` 传给新的 `SessionManager`
   - `autoBMAD/docuswarm/agents/independent.py:683-704`

2. `SessionManager._create_options()` 在有 `node_id` 和目录权限时会创建 MCP servers
   - `autoBMAD/docuswarm/llm/session_manager.py:173-248`

3. 但 `mcp_servers` 字典键使用的是 `server.__class__.__name__.lower()`
   - `autoBMAD/docuswarm/llm/session_manager.py:207-209`

4. 文件工具和搜索工具都返回 `FastMCP` 实例
   - `autoBMAD/docuswarm/tools/file_tools.py:454-500`
   - `autoBMAD/docuswarm/tools/search_tools.py:434-514`

5. 本次实测：
   - `allowed_tools` 共 4 个
   - `mcp_servers` 实际只有 1 个键：`docuswarm-fastmcp-analyst`
   - 说明两个 server 在字典化阶段发生了覆盖

**影响**

- 文件工具与搜索工具不能保证同时注册到 SDK
- `05-claude-agent-sdk-reform.md` 中“按节点受控接入 file/search MCP 工具”的目标没有真正闭环
- 这会直接影响节点在真实运行时是否既能读文件又能做搜索

**补充判断**

`NodeToolFilter` 期望的工具命名格式是：

- `mcp__docuswarm-files-{node_id}__...`
- `mcp__docuswarm-search-{node_id}__...`

对应代码在：
- `autoBMAD/docuswarm/llm/tool_filter.py:35-37`
- `autoBMAD/docuswarm/llm/tool_filter.py:124-143`

而 `SessionManager` 当前放进 `mcp_servers` 字典的键却是 `docuswarm-fastmcp-{node_id}`。如果 Claude SDK 使用字典键作为 server 名称，则 `allowed_tools` 与实际 server 名称还会进一步失配。这一点是**基于当前命名约定的高概率推断**，但即使不考虑这层推断，单看“2 个 server 最终只剩 1 个键”就已经足够判定接线存在缺陷。

**建议**

- `mcp_servers` 字典键必须使用稳定且互不冲突的 server 名称，而不是类名
- 建议直接使用 `NodeToolFilter` 的命名约定生成键，确保 server key 与 `allowed_tools` 同源
- 为 `SessionManager` 增加测试：断言 `file + search` 同时存在时 `mcp_servers` 数量为 2，且键名与 `allowed_tools` 前缀一致

---

### Finding 2：节点级 evaluator 阈值和迭代配置已加载，但运行时没有真正消费

**严重级别**：高

**结论**

`NodeLoader` 已经能解析 `evaluator.threshold`、`evaluator.max_iterations`、`criteria_file`、`model` 等字段，但这些配置并没有进入实际 verdict/迭代决策主链。当前运行时仍主要依赖硬编码阈值与默认迭代次数。

**证据**

1. `NodeLoader` 已明确加载 evaluator 配置
   - `autoBMAD/nodes/loader.py:226-236`
   - `autoBMAD/nodes/loader.py:422-428`

2. 节点配置中确实定义了阈值与最大迭代次数
   - `autoBMAD/nodes/analyst/evaluator.yaml:5,24-26`
   - `autoBMAD/nodes/architect/evaluator.yaml:23-27`

3. `EvaluatorAgent` 仍使用硬编码阈值
   - `APPROVAL_THRESHOLD = 0.70`
   - `BLOCKED_THRESHOLD = 0.50`
   - `autoBMAD/docuswarm/agents/evaluator.py:67-69`
   - `autoBMAD/docuswarm/agents/evaluator.py:269-283`

4. `EvaluatorAgent._load_criteria()` 只读取 `criteria`，并不读取阈值
   - `autoBMAD/docuswarm/agents/evaluator.py:105-155`

5. `DualAgentNode` / `create_dual_agent_node()` 没有从 `NodeLoader` 注入节点级 `max_iterations`
   - `autoBMAD/docuswarm/nodes/dual_agent.py:123-155`
   - `autoBMAD/docuswarm/nodes/dual_agent.py:868-910`
   - `autoBMAD/docuswarm/node_execution/executor.py:139-147`

6. `QualityConfig` 仍使用代码内建阈值，不是节点配置
   - `autoBMAD/docuswarm/pipeline/quality.py:56-99`

**影响**

- 节点配置中的 evaluator 字段变成“可解析但不驱动行为”的半落地状态
- Phase 3/Phase 4 中“配置即行为”的目标没有完全达成
- 运行时阈值可能与配置文件不一致

**已确认的不一致**

- `architect` 节点配置文件声明：
  - `approval: 0.75`
  - `escalation: 0.50`
  - `autoBMAD/nodes/architect/evaluator.yaml:23-27`

- 但 `QualityConfig` 中 `architect` 使用硬编码升级阈值 `0.55`
  - `autoBMAD/docuswarm/pipeline/quality.py:60-62`

这意味着即使 evaluator 配置文件写的是 `0.50`，DualAgentNode 在“达到最大迭代后是否 FORCE_APPROVED”这一步仍会按 `0.55` 处理，已经构成了实质性的配置-代码偏差。

**建议**

- 由 `NodeLoader` 作为唯一配置入口，把 `threshold` / `max_iterations` 注入 `DualAgentNode` 和 `EvaluatorAgent`
- 删除 `EvaluatorAgent` 与 `QualityConfig` 中对节点阈值的硬编码，或者把它们降为明确的 fallback
- 增加面向真实节点配置的集成测试，至少覆盖 `architect` 的特殊阈值

---

## 3. 重要发现

### Finding 3：`allowed_builtin_tools` 已写入 node.yaml，但未接入 SessionManager 运行时权限

**严重级别**：中

**结论**

节点配置中的 `allowed_builtin_tools` 已进入 schema，但当前 `SessionManager._create_options()` 自建 `NodeToolPermissions` 时只注入了文件目录和搜索目录，没有把 builtin tool 白名单一起带入。

**证据**

1. 节点配置声明了 builtin tool 白名单
   - `autoBMAD/nodes/analyst/node.yaml:49-58`
   - 其他 5 个节点也都有 `allowed_builtin_tools: ["Read", "Glob"]`

2. `SessionManager._create_options()` 构造 `NodeToolPermissions` 时只填了：
   - `file_permissions`
   - `search_permissions`
   - 没有填 `allowed_builtin_tools`
   - `autoBMAD/docuswarm/llm/session_manager.py:190-194`

3. 本次实测 `allowed_tools` 只出现 MCP 工具，没有 `Read` / `Glob`

**影响**

- `04-node-configuration-reform.md` / `05-claude-agent-sdk-reform.md` 中的统一工具权限模型只落地了一部分
- 配置层声明与运行时实际可用工具不一致

**建议**

- `IndependentAgent` 创建 pipeline session 时应传递完整 `NodeToolPermissions`，而不是拆成 `file_dirs`/`search_dirs`
- 或者在 `SessionManager` 内部重新加载 `NodeLoader.load(node_id)`，直接复用完整配置对象

---

### Finding 4：Phase 5 目前不能声称完成，且现有测试未覆盖关键集成风险

**严重级别**：中

**结论**

当前仓库中确实存在针对 NodeLoader 与 SessionManager 的测试，但这并不足以证明 `refactor-2026-03-26` 已完成端到端闭环。一方面，本次测试运行被环境权限阻断；另一方面，现有断言没有覆盖本次发现的关键接线缺陷。

**证据**

1. 本次运行：
   - `python -m pytest tests/unit/context tests/unit/llm tests/unit/nodes tests/unit/prompts -q`
   - 多个测试在 `pytest_runtest_setup` 阶段即因临时目录权限失败
   - 错误来源：`pytestqt` 试图创建 `pytest-of-Administrator`

2. `tests/unit/llm/test_session_manager_mcp_config.py` 只断言：
   - `options.mcp_servers` 非空
   - 没有断言 `mcp_servers` 数量
   - 没有断言 server key 与 `allowed_tools` 前缀一致

3. `tests/unit/nodes/test_node_loader_evaluator.py` 验证了 loader 能读取 inline evaluator 配置，但没有验证这些配置被 `DualAgentNode` / `EvaluatorAgent` 真正消费

**影响**

- 当前测试资产更像“部件存在性证明”，不是“主链路行为证明”
- 不能据此确认 Phase 5 的“端到端测试与回归验证”已经完成

**建议**

- 补充集成测试：
  - `file + search` server 同时存在时，`mcp_servers` 必须为 2
  - `allowed_tools` 与 server 命名必须一致
  - `architect` 节点阈值必须来自配置，而不是硬编码
  - `max_iterations` 必须能由节点 evaluator 配置驱动
- 清理当前环境下的测试临时目录/权限前置条件，保证质量门禁可重复执行

---

## 4. 已确认落地的部分

### 4.1 MemoryManager 已清理完成

- 在 `autoBMAD/docuswarm` 范围内搜索 `MemoryManager|MemoryScope` 无源码命中
- `autoBMAD/docuswarm/context/__init__.py:16-46` 仅导出新的 context 组件，没有旧 memory 导出

结论：`02-memory-manager-removal.md` 的目标已完成。

### 4.2 ContextValidator 独立组件已进入主链路

- 独立实现位于 `autoBMAD/docuswarm/context/validator.py`
- `ContextManager` 使用其做隔离校验
  - `autoBMAD/docuswarm/context/isolation.py:299-310`
- `HybridOrchestrator` 用其做 LLM 上下文验证
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:128-132`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:313-314`
- Independent/Evaluator 输出解析后都委托它做校验
  - `autoBMAD/docuswarm/agents/independent.py:430-445`
  - `autoBMAD/docuswarm/agents/evaluator.py:433-454`

结论：`01-context-validator-extraction.md` 的核心目标已完成。

### 4.3 Task 契约瘦身基本完成

- `NodeExecutionContext` 现在以运行时字段为主
  - `autoBMAD/docuswarm/node_execution/contracts.py:25-39`
- `ContextManager.build_independent_input()` 从 `NodeLoader` 读取任务信息
  - `autoBMAD/docuswarm/context/isolation.py:116-175`
- `ContextManager.build_evaluator_input()` 也从 `NodeLoader` 读取任务与 criteria
  - `autoBMAD/docuswarm/context/isolation.py:217-235`

结论：`03-task-contract-removal.md` 的方向基本完成。

### 4.4 deliverable v2 扩展字段已真正进入运行时

这是相对旧报告最重要的变化之一。

- `NodeLoader` 已解析：
  - `template_title`
  - `output_filename`
  - `format_hints`
  - `autoBMAD/nodes/loader.py:395-403`

- `ContextManager.build_independent_input()` 已把这些字段注入 `deliverable_requirements`
  - `autoBMAD/docuswarm/context/isolation.py:141-162`

- `contract_builder` 已把这些字段写入最终提示词合同
  - `autoBMAD/docuswarm/prompts/contract_builder.py:175-206`

本次直接验证 `architect` 节点得到的输入为：

- `task_name = create-system-architecture-document`
- `deliverable_requirements = {'required_sections': [...], 'template_title': 'Technical Specification: {project_name}', 'output_filename': 'tech-spec-{project_name}.md'}`

结论：旧结论“字段只停留在 YAML 层”已失效，应更新为“字段已进入运行时，但 schema 仍有其他配置消费缺口”。

### 4.5 四层提示词架构与技能注入已基本落地

- `IndependentAgent` 已使用 `PromptTemplateEngine`
  - `autoBMAD/docuswarm/agents/independent.py:111-112`
  - `autoBMAD/docuswarm/agents/independent.py:246-320`

- `create_session()` 已把字符串 system prompt 包装为 `preset + append`
  - `autoBMAD/docuswarm/llm/session_manager.py:297-308`

- `SkillInjector` 已从 `.claude/skills` 读取技能描述
  - `autoBMAD/docuswarm/prompts/skill_injector.py:82-216`

- 本次实测 `architect`、`analyst`、`pm`、`ux`、`po` 都能生成非空技能段落

结论：`05-claude-agent-sdk-reform.md` 的 T-H 主体已落地，但 T-G 仍有关键缺陷，因此整个 SDK 改造不能判定为 fully done。

---

## 5. 与研究方案的偏差清单

### 5.1 已被当前代码修正的旧偏差

- 旧报告中“`deliverable.template_title/output_filename` 未进入运行时”的问题已修复
- 旧报告中“IndependentAgent 主路径未接入节点工具权限”的问题已修复到“部分接线”状态，现在真正的问题变成了 MCP server 注册细节缺陷

### 5.2 仍存在的偏差

- 节点 evaluator 配置已加载，但 verdict/迭代决策未完全以配置为准
- builtin tool 白名单未进入运行时
- SDK 工具注册存在 server 覆盖风险
- Phase 5 测试门禁缺乏可重复、可闭环的证据

### 5.3 文档与实现的设计偏差

`NodeLoader` 已支持 `node.yaml` 中的 inline evaluator / `criteria_file` 模式，但当前真实节点配置仍然全部使用独立 `evaluator.yaml`，未全面迁移到研究文档中更强调的“内联/引用式 node.yaml v2”形态。

这更像**设计偏差**而不是当前的功能性 bug，但建议同步更新研究文档或补齐真实配置迁移，避免“代码支持一套、生产配置还是另一套”。

---

## 6. 分项状态评估

| 工作项 | 目标 | 当前状态 | 结论 |
|---|---|---|---|
| T-A MemoryManager 移除 | 删除死代码与导出 | 已无源码引用 | 完成 |
| T-B Task 死字段清理 | 运行时上下文瘦身 | 主体已完成 | 完成 |
| T-C Schema v2 基础层 | task/runtime/tools/evaluator 可加载 | 已完成 | 完成 |
| T-D ContextValidator 独立化 | 统一验证入口 | 已进入主链路 | 完成 |
| T-E Task 向 persona/node 统一迁移 | 单一配置源 | 主体完成 | 完成 |
| T-F 节点配置文件升级 | 5 节点 v2 升级 | 基本完成 | 大体完成 |
| T-G 文件/搜索工具接入 | 节点受控工具真实可用 | 有关键缺陷 | 部分完成 |
| T-H 四层提示词架构 | preset + append + skill injection | 主体完成 | 大体完成 |
| T-I 端到端验证 | 测试门禁与回归完成 | 无法证实 | 未完成 |

---

## 7. 建议的整改优先级

### P0

1. 修复 `SessionManager._create_options()` 的 `mcp_servers` 命名与去重逻辑，确保文件 server 和搜索 server 可以同时注册。
2. 让 `allowed_tools` 与最终 MCP server 命名严格同源，消除工具名失配风险。
3. 让 `DualAgentNode` / `EvaluatorAgent` 真正消费 `NodeLoader` 解析出的 `threshold` 和 `max_iterations`。

### P1

1. 把 `allowed_builtin_tools` 接回运行时。
2. 为 `architect` 节点增加配置驱动阈值的集成测试，防止 0.50/0.55 这类偏差再次出现。
3. 决定 `evaluator` 配置是否要继续支持 inline 模式，并同步文档与真实节点配置。

### P2

1. 修复当前测试环境下的临时目录权限问题，让 `pytest` 可以稳定跑完。
2. 补全 Phase 5 所需的端到端证据，而不只是部件级测试。

---

## 8. 最终判断

这轮实现已经不适合再被描述为“研究方案基本没落地”。更准确的表述是：

- **架构清理和配置建模部分已经明显落地**
- **提示词架构和技能注入已经进入主路径**
- **真正阻碍“宣称完成”的，是 SDK 工具接线细节和配置驱动执行未闭环**

因此，若要对外表述当前状态，推荐使用：

> `refactor-2026-03-26` 已完成大部分结构性重构，但在节点级 SDK 工具注册、配置驱动评估阈值/迭代控制、以及端到端验证闭环方面仍有高优先级缺口，尚不宜宣称全量完成。

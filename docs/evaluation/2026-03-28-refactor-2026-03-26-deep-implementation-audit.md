# DocuSwarm 重构方案实施深度审查报告（二次核查）

**审查对象**
- 方案目录：`docs/research/refactor-2026-03-26/00-refactoring-roadmap.md`
- 子方案：`01-context-validator-extraction.md` 至 `05-claude-agent-sdk-reform.md`
- 实现范围：`autoBMAD/docuswarm`、`autoBMAD/nodes`

**审查日期**
- 2026-03-28

**审查方法**
- 静态代码审查
- 配置与调用链交叉核对
- 目标性命令验证
- 现有测试与检查器抽样执行
- 以技术债治理视角评估“结构完成度”与“运行闭环完成度”

---

## 1. 审查结论

这轮重构不是“纸面完成”，也不是“端到端 fully done”。

更准确的判断是：

| 方案 | 当前判断 | 结论 |
|------|----------|------|
| 01 ContextValidator 提取 | 主体已落地，但节点级规则注册与实际校验实例未闭环 | **部分完成** |
| 02 MemoryManager 移除 | 死代码已清理干净 | **完成** |
| 03 Task 契约移除 | 运行时上下文已瘦身，但交付物契约在主执行链被丢失 | **部分完成** |
| 04 节点配置体系改革 | v2 配置文件已成型，但配置消费仍有断层，诊断分数偏乐观 | **部分完成** |
| 05 Claude Agent SDK 改造 | MCP/系统提示能力已接入，但 BMAD 技能注入未进入主执行链 | **部分完成** |

**总体判断**

- 结构性重构完成度：**高**
- 主执行链闭环完成度：**中等**
- 文档与代码一致性：**中等偏低**
- 残余技术债类型：**接线债、验证债、治理债、文档债**

如果按路线图的原始目标来评估，我认为当前状态更接近：

- Phase 1：完成
- Phase 2：大体��成
- Phase 3：部分完成
- Phase 4：部分完成
- Phase 5：不能宣称完成

---

## 2. 已确认落地的部分

### 2.1 MemoryManager 已真实移除

- 代码树内已无 `MemoryManager` / `MemoryScope` 引用。
- `rg -n "MemoryManager|MemoryScope" autoBMAD` 无结果。
- `autoBMAD/docuswarm/context/__init__.py` 已导出 `ContextValidator`，不再暴露内存管理遗留接口。

**判断**：方案 02 已完成，且是“真实清理”，不是“保留废弃兼容层”。

### 2.2 NodeExecutionContext 已按运行时字段瘦身

`autoBMAD/docuswarm/node_execution/contracts.py` 中的 `NodeExecutionContext` 仅保留运行时字段：

- `pipeline_id`
- `node_id`
- `node_name`
- `node_order`
- `original_context`
- `chained_deliverables`
- `shared_context`
- `iteration_feedback`
- `docs_context`

这说明方案 03 的“静态配置不再塞进运行时上下文”方向已经成立。

### 2.3 v2 节点配置骨架已落地

5 个节点的 `node.yaml` / `persona.json` / `evaluator.yaml` 均已体现 v2 改造方向：

- `schema_version: "2.0"`
- `task.name`
- `task.description`
- `runtime.*`
- `tools.*`
- `threshold`
- `max_iterations`
- `communication_style`
- `critical_actions`
- `memories`

`python tools/node_config_completeness_checker.py` 返回：

- 平均 v2 完整度 100%
- 0 个关键问题

但这个 100% 只能说明“字段存在”，不能直接说明“运行时闭环成立”，见后文 Finding 4。

### 2.4 MCP 基础接线已进入主执行链

与旧审查结论不同，这次核查确认 `IndependentAgent.execute_with_input()` 已经把节点权限传给 `SessionManager`：

- `autoBMAD/docuswarm/agents/independent.py:675-695`
- `autoBMAD/docuswarm/llm/session_manager.py:173-242`

抽样测试结果：

- `tests/unit/llm/test_session_manager_mcp_config.py` 通过
- `tests/unit/llm/test_session_manager_injection.py` 通���

**判断**：方案 05 中“节点级 MCP 权限接线”不是空壳，已进入真实执行路径。

---

## 3. 最高优先级发现

## Finding 1: Structured 执行路径会丢失交付物契约，导致节点提示词缺少 `required_sections` / `template_title` / `output_filename`

**严重级别**：高

### 证据链

`ContextManager.build_independent_input()` 已经正确构建了 `deliverable_requirements`：

- `autoBMAD/docuswarm/context/isolation.py:167-170`

但 `IndependentAgent.execute_with_input()` 读取 `agent_input` 后，只把以下字段重建进 `NodeExecutionContext`：

- `task_name`
- `original_context_summary`
- `chained_deliverables_summary`
- `shared_context`
- `iteration_feedback`

关键代码：

- `autoBMAD/docuswarm/agents/independent.py:630-666`

这里**没有**把 `deliverable_requirements` 放回 `context`。

随后 `contract_builder` 构建交付物章节时，仍然从 `context` 中读取：

- `autoBMAD/docuswarm/prompts/contract_builder.py:175-205`

尤其是：

- `reqs = context.get("deliverable_requirements", {})`
- `deliverable_type = context.get("deliverable_type", "")`

而 `render_independent_user_prompt()` 又明确把 `deliverable_section` 作为用户提示词的一部分：

- `autoBMAD/docuswarm/prompts/contract_builder.py:388-398`

### 最小复现

执行以下验证后，`architect` 节点的 `agent_input` 中明明有交付物要求，但重建 contract 后：

- `agent_input["deliverable_requirements"]` 为  
  `{'required_sections': ['architecture', 'api_design', 'data_model', 'security'], 'template_title': 'Technical Specification: {project_name}', 'output_filename': 'tech-spec-{project_name}.md'}`
- `contract["deliverable_section"] == ''`

这说明主执行链提示词**实际丢失了交付物契约**。

### 影响

- `required_sections` 不能稳定进入真实生成提示词
- `template_title` / `output_filename` 即使在 `NodeLoader` 中已解析，也不会进入主执行提示
- 方案 03 与方案 04 的核心收益被主执行链削弱

### 判断

这不是“可选增强未做”，而是**单一事实源重构后的接线断裂**。

### 建议

- 在 `IndependentAgent.execute_with_input()` 中直接使用 `agent_input["deliverable_requirements"]`
- 或让 `NodePromptContractBuilder._build_deliverable_section()` 改为从 `NodeLoader.load(node_id)` 读取，不再依赖运行时上下文

---

## Finding 2: BMAD 技能注入没有进入主执行链，四层提示词架构只在旁路存在

**严重级别**：高

### 证据链

仓库中确实已经有：

- `PromptTemplateEngine`
- `SkillInjector`
- `SessionManager.create_session(system_prompt=...)` 的 preset/append 包装

相关代码：

- `autoBMAD/docuswarm/prompts/template_engine.py`
- `autoBMAD/docuswarm/prompts/skill_injector.py:82-91`
- `autoBMAD/docuswarm/llm/session_manager.py:297-307`

`SkillInjector` 也能正常从 `.claude/skills` 读取技能描述，最小验证结果为：

- `SKILLS_PRESENT True`

但是主执行链 `execute_with_input()` 并**没有**走 `PromptTemplateEngine.build_system_prompt_append()`，而是走 `contract_builder`：

- `autoBMAD/docuswarm/agents/independent.py:668-705`

其中：

- `contract = self.contract_builder.build_independent_contract(context)`
- `system_prompt = self._format_system_prompt_with_contract(contract)`

而 `render_independent_system_prompt()` 只拼接：

- `persona_section`
- `instructions_section`

代码位置：

- `autoBMAD/docuswarm/prompts/contract_builder.py:377-386`

这里没有任何技能章节。

### 最小复现

对 `analyst` 节点重建主执行链 contract 后，验证结果为：

- `HAS_SKILLS False`

### 影响

- 路线图 05 所说的 Layer 4 技能注入，没有真正进入真实节点执行流
- `SkillInjector` 更像“存在但未接线”的旁路实现
- 方案 05 的完成度被高估

### 判断

方案 05 已完成 SDK 能力基础设施，但**未完成 BMAD 技能进入主链**。

### 建议

- 统一 `execute_with_input()` 的 system prompt 生成路径，改走 `PromptTemplateEngine`
- 或在 `NodePromptContractBuilder` 内显式接入 `SkillInjector`

---

## Finding 3: `criteria_loader.py` 仍读取废弃的 `thresholds`，会静默忽略 v2 `threshold`

**严重级别**：中高

### 证据链

`NodeLoader` 已按 v2 读取 `threshold`：

- `autoBMAD/nodes/loader.py:422-428`

但 `CriteriaLoader` 仍然写死读取：

- `autoBMAD/docuswarm/agents/evaluator_config/criteria_loader.py:104-105`

即：

```python
thresholds = self._validate_thresholds(data.get("thresholds"))
```

当前节点配置已经全部改为 `threshold`，例如：

- `autoBMAD/nodes/architect/evaluator.yaml`

### 最小复现

执行：

```python
CriteriaLoader(Path("autoBMAD")).load("architect")["thresholds"]
```

返回结果是：

```python
{'approval': 0.7, 'escalation': 0.5}
```

但 `architect` 节点配置实际是：

```yaml
threshold:
  approval: 0.75
  escalation: 0.50
```

也就是说，`criteria_loader.py` 会**静默回退到默认值**，把更严格的架构评审阈值抹掉。

### 影响

- 目前如果任何代码路径重新启用 `CriteriaLoader`，会立即引入行为回退
- 这是典型的“死分支式技术债”：今天没爆，明天非常容易炸

### 判断

方案 04 的 schema 迁移没有完成全仓收口。

### 建议

- 将 `criteria_loader.py` 升级为优先读 `threshold`，兼容读 `thresholds`
- 或明确废弃整个 `evaluator_config` 子模块，避免形成错误备用路径

---

## Finding 4: ContextValidator 的“节点级规则注册”与“实际校验实例”分裂，扩展能力未真正接线

**严重级别**：中

### 证据链

`NodeLoader` 将节点级验证规则注册到 singleton：

- `autoBMAD/nodes/loader.py:241-245`

```python
validator = ContextValidator.get_instance()
validator.load_node_rules(node_id, validation_rules)
```

但真实校验时，多处直接新建实例而不是复用 singleton：

- `autoBMAD/docuswarm/context/isolation.py:90-95`
- `autoBMAD/docuswarm/agents/independent.py:430-432`
- `autoBMAD/docuswarm/agents/evaluator.py:433-437`

### 最小复现

将 singleton 注册规则：

```python
ContextValidator.get_instance().load_node_rules("demo", {"min_word_count": 999})
```

然后比较：

- singleton 校验 warning 为 `minimum (999)`
- fresh `ContextValidator()` 校验 warning 为 `minimum (100)`

这说明注册规则**不会流入实际执行中那些临时创建的 validator**。

### 影响

- `ValidationRuleRegistry` 的可配置价值没有真正落到消费端
- 节点级 validation 机制当前只有“注册动作”，缺少“统一消费动作”
- 当前节点配置里虽然还没有 `validation:` 段，但一旦以后补上，会出现“看上去配置生效，实际不生效”的隐性产品债

### 判断

方案 01 的架构框架已落地，但“统一入口”还不彻底。

### 建议

- 全仓统一使用 `ContextValidator.get_instance()`
- 或通过依赖注入把 validator 从 orchestrator/context manager 传到底层，而不是临时 `ContextValidator()`

---

## Finding 5: 节点配置检查器对“语义不一致”过于乐观，100% v2 compliance 不能作为完成证据

**严重级别**：中

### 证据链

`python tools/node_config_completeness_checker.py` 输出：

- 平均 v2 完整度 100%
- 0 个关键问题

但 `.tmp/node_config_report.json` 同时显示 `architect` 存在跨文件不一致：

- `node.yaml` 的 `required_sections` 只有 4 项  
  `architecture` / `api_design` / `data_model` / `security`
- `persona.json` 的 `output_format.sections` 有 9 项  
  `system_overview` / `architectural_pattern` / `component_diagram` / `data_model` / `api_design` / `security` / `scalability` / `integration_points` / `technology_stack`

对应配置位置：

- `autoBMAD/nodes/architect/node.yaml:22-29`
- `autoBMAD/nodes/architect/persona.json:45-57`

检查器在详细 JSON 中把这件事记为 warning，但总体分数仍保持 1.0。

### 影响

- “字段存在率”掩盖了“契约一致性”问题
- 审查和治理层容易被 100% 分数误导
- 这属于治理债，不只是实现债

### 判断

方案 04 的配套诊断工具还不足以作为验收门禁。

### 建议

- 将跨文件语义一致性纳入得分
- architect 这种 section mismatch 应至少降低 compliance 分

---

## Finding 6: `SessionManager.allowed_dirs` 属性存在未定义字段访问

**严重级别**：低

### 证据链

属性实现如下：

- `autoBMAD/docuswarm/llm/session_manager.py:129-131`

```python
return self._file_dirs or self._allowed_dirs
```

但 `__init__` 中并未定义 `self._allowed_dirs`。

最小复现：

```python
SessionManager(work_dir=Path("output")).allowed_dirs
```

结果：

- `AttributeError: 'SessionManager' object has no attribute '_allowed_dirs'`

### 影响

- 属于 API 面的残余裂缝
- 当前主流程未明显依赖它，但这是典型的小型维护债

### 建议

- 直接删除该兼容属性
- 或在 `__init__` 中显式保存 `allowed_dirs`

---

## 4. 方案实施状态矩阵

| 方案 | 文档目标 | 代码状态 | 审查结论 |
|------|----------|----------|----------|
| 01 | 统一验证逻辑与节点级规则 | `context/validator.py` 已落地；LLM 校验已接入 orchestrator；规则注册与实例消费分裂 | 部分完成 |
| 02 | 移除 MemoryManager 死代码 | 已移除且无活引用 | 完成 |
| 03 | 删除 task contract 冗余，保留单一运行时上下文 | 上下文字段已瘦身，但 deliverable contract 在主执行链丢失 | 部分完成 |
| 04 | 节点配置 v2 完整迁移并对齐代码 | v2 文件层完成；运行消费与诊断门禁仍有断层 | 部分完成 |
| 05 | Claude Agent SDK 工具、system prompt、BMAD 技能全面激活 | MCP/系统提示已接入；BMAD skills 未进入主链；旧阈值加载器仍残留 | 部分完成 |

---

## 5. 抽样验证记录

### 已成功执行

- `python tools/node_config_completeness_checker.py`
- `python -m pytest tests/unit/nodes/test_node_deliverable_config.py -q`
- `python -m pytest tests/unit/llm/test_session_manager_mcp_config.py -q`
- `python -m pytest tests/unit/llm/test_session_manager_injection.py -q`
- `python -m pytest tests/test_syntax_validation.py -q`

### 受环境影响未形成有效断言

- `python -m pytest tests/unit/nodes/test_node_loader_parsing.py -q`

阻断原因不是业务断言失败，而是 `pytestqt` 在系统临时目录下创建测试目录时遇到权限错误：

- `PermissionError: [WinError 5]`
- 临时目录：`C:\\Users\\Administrator\\AppData\\Local\\Temp\\pytest-of-Administrator`

### 测试资产观察

- 现有测试更偏向“模块存在性 / 基础解析 / SessionManager 接线”
- 对于本次审查发现的两个关键问题，目前没有直接覆盖：
  - 主执行链交付物契约丢失
  - 主执行链技能注入缺失

---

## 6. 技术债视角总结

这次重构已经偿还了大量**结构债**，尤其是：

- 死代码清理
- 上下文协议瘦身
- 节点配置 v2 化
- SDK 工具权限建模

但它同时留下了几类新的或尚未收口的债：

| 债务类型 | 表现 |
|---------|------|
| 接线债 | 配置/能力已存在，但主执行链没有完整消费 |
| 验证债 | 规则注册存在，但校验实例未统一 |
| 治理债 | 完整度检查器对语义不一致不敏感 |
| 备用路径债 | `criteria_loader.py` 仍沿用旧 schema |
| API 维护债 | `SessionManager.allowed_dirs` 有悬空引用 |

---

## 7. 优先级建议

### P0

1. 修复 `execute_with_input()` 到 `contract_builder` 的交付物契约传递问题。
2. 让主执行链真正包含 BMAD skill injection。
3. 修复 `criteria_loader.py` 对 `threshold` / `thresholds` 的兼容读取。

### P1

1. 统一 `ContextValidator` 的实例来源，消除 singleton 与临时实例分裂。
2. 升级 `node_config_completeness_checker.py`，把跨文件语义一致性纳入评分。
3. 增加针对主执行链 prompt 内容的测试，而不是只测 SessionManager 构造。

### P2

1. 清理 `SessionManager.allowed_dirs` 残余兼容接口。
2. 对 architect 节点的 `node.yaml` 与 `persona.json` sections 重新对齐。

---

## 8. 最终判断

如果对外表述为“`refactor-2026-03-26` 重构方案已全部实施完成”，我认为**证据不足**。

如果表述为：

> 已完成大部分结构性重构，主执行链仍有若干高优先级接线缺口和治理型技术债待收口

那么这与当前代码现实更一致。

本轮最值得肯定的是，团队已经把架构方向推到了正确轨道上；当前最需要的不是推翻重来，而是把剩余 20% 的闭环问题快速收口，否则这些“半接线能力”会开始反向积累新的技术债利息。

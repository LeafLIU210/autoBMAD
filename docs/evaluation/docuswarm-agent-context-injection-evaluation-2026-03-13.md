# DocuSwarm Agent 上下文注入安排深度评估报告

> 评估日期: 2026-03-13  
> 评估对象: `autoBMAD/docuswarm` 当前代码实现  
> 评估重点: 各 agent 的上下文注入安排、注入链路、合理性与偏差  
> 参考范围:
> - `docs/plan/PRD.md`
> - `docs/architecture/*`
> - `docs/plan/UX_DESIGN.md`
> - `docs/research/*`
> - `autoBMAD/docuswarm/docs/*`
> - `docs/evaluation/docuswarm-agent-framework-evaluation-2026-03-13.md`

## 1. 结论摘要

### 总体判断

当前 `DocuSwarm` 的 agent 上下文注入安排属于:

> “隔离设计较强，但任务注入、文档注入、工具注入与状态注入没有收敛成单一一致模型。”

如果只评价“Evaluator 不被污染”这一点，方案是合理的；但如果评价“每个节点 agent 是否拿到了自己应该拿到的业务上下文，并且按 PRD/架构文档预期工作”，当前安排只能算 **部分合理，整体不够闭环**。

### 综合评分

| 维度 | 评分 | 结论 |
|------|------|------|
| 上下文隔离合理性 | 8.5/10 | 三层隔离思路基本成立，Evaluator 侧约束清晰 |
| 角色区分合理性 | 6.5/10 | 5 个节点有人设差异，但任务契约没有真正注入 |
| 任务注入完整性 | 3.5/10 | `node.yaml` 的 task/deliverable 配置几乎未进入运行时 prompt |
| 链式上下文利用率 | 4.5/10 | 管道层有累积，Agent 层消费方式失真 |
| 工具驱动上下文更新 | 2.0/10 | `update_context` 实际是 no-op |
| 文档与实现一致性 | 2.0/10 | PRD/架构文档与代码现状有显著漂移 |
| 总体合理性 | 4.8/10 | 可继续演进，但当前不是稳定可依赖的“上下文注入体系” |

### 一句话结论

当前实现最合理的部分是“把 Evaluator 变成最小上下文消费者”；最不合理的部分是“Independent Agent 实际拿到的任务上下文，与节点配置、设计文档、工具系统三者都没有真正对齐”。

---

## 2. 评估边界与说明

### 2.1 参考文档的实际可用性

本次评估中，用户指定的两个路径在仓库中不存在:

- `docs/prd.md` 不存在
- `docs/design` 目录不存在

因此本报告实际采用以下替代来源:

- 将 `docs/plan/PRD.md` 视为当前 PRD
- 将 `docs/plan/UX_DESIGN.md` 视为当前 design/UX 设计文档

这本身也是一个信号: “文档入口约定”已经和仓库真实结构发生漂移。

### 2.2 本报告关注的“上下文注入”定义

本报告把以下内容都视为上下文注入的一部分:

1. CLI 把用户上下文文件送入系统
2. Pipeline/Graph 把前序节点产物累积到后续节点
3. DualAgentNode 把上下文分别发给 Independent / Evaluator
4. Persona / evaluator criteria / node task / deliverable schema 如何进入 prompt
5. tools 是否扩展或修改上下文
6. docs 文件、`@` 引用、问答补充是否真正进入后续 agent

---

## 3. 当前实现的真实注入链路

### 3.1 从 CLI 到 agent 的实际路径

当前代码的真实链路如下:

```text
用户 context 文件
  -> main.py 读取 content
  -> subject_context = {subject, context_file, content}
  -> orchestrator.start_pipeline(subject_context)
  -> PipelineState.subject_context
  -> pipeline.graph.accumulate_context()
  -> context_file(JSON string)
  -> node_execution.executor._extract_task_from_state()
  -> DualAgentNode.execute(subject_context=str(context_file), task=提取出的字符串)
  -> ContextManager.build_independent_context()
  -> IndependentAgent.execute()
  -> ContextFilter / ContextManager.build_evaluator_context()
  -> EvaluatorAgent.execute()
```

### 3.2 关键实现证据

#### CLI 注入

`main.py` 只做了最基础的三项注入:

- `subject`
- `context_file`
- `content`

见 `autoBMAD/docuswarm/main.py:106-138`。

#### Pipeline 累积

`accumulate_context()` 会把当前 `subject_context` 与前序节点 deliverable 合并，形成:

- `subject_context`
- `analyst_deliverable`
- `pm_deliverable`
- ...

见 `autoBMAD/docuswarm/pipeline/state.py:158-200`。

#### Node executor 的“任务提取”

`_extract_task_from_state()` 的逻辑不是读取 `node.yaml.task.description`，而是优先从 `context_file` 的 `subject_context.content` 取整段原始文本；否则退化成拿链式 deliverable 的字符串。

见 `autoBMAD/docuswarm/node_execution/executor.py:217-264`。

这意味着:

- 节点任务没有被精确注入
- “原始上下文内容”常常直接被当成“task”

#### DualAgentNode 的再次包装

`DualAgentNode.execute()` 又把传进来的 `subject_context` 包成:

```python
{
  "subject": subject_context,
  "task": task,
}
```

见 `autoBMAD/docuswarm/nodes/dual_agent.py:320-329`。

这一步没有保留 `subject_context.content` 的结构，而是把完整 JSON 字符串塞进了 `subject` 字段。

#### IndependentAgent 的消费方式

`IndependentAgent.execute()` 只会尝试从下面两条路径提取 `context_content`:

- `subject_context.subject_context.content`
- `subject_context.content`

见 `autoBMAD/docuswarm/agents/independent.py:453-545`。

但 `DualAgentNode` 实际传入的是:

```python
{
  "subject": "<json string>",
  "task": "<task string>"
}
```

所以:

- 结构化 `content` 大概率提取不到
- 真正起作用的通常只有 `task`
- 而这个 `task` 又往往只是原始 context 文本，不是节点任务定义

#### EvaluatorAgent 的消费方式

`EvaluatorAgent` 接收:

- `subject_context`
- `deliverable`
- `criteria`

见 `autoBMAD/docuswarm/context/isolation.py:95-134` 与 `autoBMAD/docuswarm/agents/evaluator.py:155-325`。

这部分的约束是清晰的，但 `subject_context` 最终经常只是 `dict -> str()` 后的字符串，不是精心裁剪过的评审上下文。

---

## 4. 各 agent 的上下文注入安排

## 4.1 Independent Agent 的共性安排

所有节点的 Independent Agent 都共享同一套运行机制，差异主要来自 persona 文件。

### 静态注入

会被加载:

- `nodes/{node_id}/persona.json`
- `agents/configs/independent_agent.yaml`

不会真正进入 prompt 或仅部分进入:

- `nodes/{node_id}/node.yaml.task`
- `nodes/{node_id}/node.yaml.deliverable`
- `required_sections`
- `template_title`
- `role_supplement`

### 实际进入 system prompt 的内容

当前 `IndependentAgent._format_system_prompt()` 实际注入的是:

- persona 的 `name`
- `role`
- `identity`
- `expertise`
- `principles`
- 通用工具/JSON 输出指令

见 `autoBMAD/docuswarm/agents/independent.py:125-211` 与 `autoBMAD/docuswarm/agents/persona.py:187-239`。

### 实际进入 user prompt 的内容

运行时只会传入一个 `user_message`:

- 优先是 `enriched_task`
- 否则是 `task`

见 `autoBMAD/docuswarm/agents/independent.py:533-550`。

它没有显式拼接:

- 节点 task name / description
- 节点 deliverable required_sections
- 前序节点 deliverable 摘要的结构化说明
- 用户已回答问题的归纳上下文

### 合理性评价

这套安排的优点是“简单”，但缺点是“节点特异性非常弱”。  
从效果上看，5 个节点的 Independent Agent 更像是:

> “同一个通用写作 agent + 五套 persona 外观”

而不是:

> “五个拥有清晰任务契约、交付物结构和上下游上下文协议的专用 agent”

---

## 4.2 Evaluator Agent 的共性安排

所有节点的 Evaluator Agent 共享同一套机制，差异主要来自 `evaluator.yaml`。

### 静态注入

会被加载:

- `nodes/{node_id}/evaluator.yaml`

见 `autoBMAD/docuswarm/agents/evaluator.py:103-153`。

### 动态注入

运行时会收到:

- `subject_context`
- `deliverable.title`
- `deliverable.content`
- criteria 列表及其权重

见 `autoBMAD/docuswarm/agents/evaluator.py:155-229`。

### 合理性评价

Evaluator 的注入设计整体比 Independent 更合理，原因有三点:

1. 输入边界清楚
2. criteria 明确来自节点配置
3. 对 `private_reasoning` 有显式拒绝逻辑

见 `autoBMAD/docuswarm/agents/evaluator.py:448-470`。

但它仍有两个明显问题:

1. `subject_context` 没有经过摘要/裁剪/结构化整理，信息噪声大
2. 它评审的 `deliverable.content` 并不总是“完整文档正文”

第二点尤其关键，因为 Independent prompt 明确要求:

> `deliverable.content` 只返回 1-2 句摘要，而不是完整文档

见 `autoBMAD/docuswarm/agents/independent.py:172-176`。

这会让 Evaluator 的评审对象与真实交付物发生偏移。

---

## 4.3 五个业务节点的具体评价

### 共性结论

`analyst / pm / ux / architect / po` 这五个节点的真正差异，目前主要只体现在两处:

1. persona 不同
2. evaluator criteria 不同

而本应形成节点个性的下列信息，当前并未真正注入执行链:

1. `node.yaml.task.description`
2. `node.yaml.task.role_supplement`
3. `node.yaml.deliverable.required_sections`
4. `node.yaml.deliverable.template_title`
5. `node.yaml.deliverable.output_filename`

### 节点级矩阵

| 节点 | 已生效的注入 | 未生效或弱生效的注入 | 评价 |
|------|--------------|----------------------|------|
| analyst | persona、analyst evaluator criteria | analyst task 与 deliverable schema | 只像“分析人设”，不像真正 analyst node |
| pm | persona、pm evaluator criteria | PM 任务定义、PRD 结构要求 | 能体现 PM 语气，不能保证 PRD 契约 |
| ux | persona、ux evaluator criteria | UX 文档结构、交互/可访问性要求 | 设计目标在文档里，运行时注入不足 |
| architect | persona、architect evaluator criteria | 架构文档章节、技术取舍模板 | 更像泛化技术写作，而非架构节点 |
| po | persona、po evaluator criteria | backlog/story 格式与拆分规范 | 角色有了，交付格式契约很弱 |

### 结论

当前“五节点”更接近“同构 agent 的五次运行”，而不是“五种不同上下文协议的 agent”。

---

## 4.4 tools 作为“扩展上下文注入”的安排

Independent Agent 注册了 6 个工具:

- `create_deliverable`
- `update_context`
- `read_docs_file`
- `update_docs_file`
- `list_docs_files`
- `create_document_set`

见 `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:1-15`。

### 其中真正可用的部分

- `create_deliverable` 会把内容写到 `Path.cwd()` 下
- `read_docs_file` 能按需读取 `docs/` 下文件
- `list_docs_files` / `update_docs_file` 也具备一定实用性

### 其中不合理的部分

#### `update_context` 实际是 no-op

`update_context` 只是返回 acknowledged，并没有真实状态存储行为。

见 `autoBMAD/docuswarm/tools/update_context.py:56-60`。

这意味着:

- agent 虽然“看起来”能更新上下文
- 但实际无法把新的上下文可靠写回共享状态

这是当前上下文注入安排里最明显的“假能力”之一。

#### docs 工具没有被策略化使用

虽然 agent_file 注册了 `read_docs_file` 等工具，但当前 prompt 并没有明确告诉 agent:

- 何时先列出 docs
- 何时读取某类设计文档
- 何时把 docs 信息提炼后并入交付物

因此 docs 工具更像“可选外挂”，不是“受控的上下文扩展层”。

---

## 5. 当前安排中最合理的部分

## 5.1 Evaluator 最小上下文原则

这是当前系统最成熟的一部分。

`ContextManager` 与 `ContextFilter` 共同限制 Evaluator 只能看到:

- `subject_context`
- `deliverable`
- `criteria`

并递归拦截:

- `private_reasoning`
- `tool_call_history`
- `iteration_feedback`
- `internal_notes`

见 `autoBMAD/docuswarm/context/isolation.py:18-24, 95-152`。

这套设计非常符合“评审 agent 应该只看作品，不看作者脑内草稿”的原则。

## 5.2 Persona 与 criteria 外置到 nodes 目录

把节点差异放在:

- `nodes/{node}/persona.json`
- `nodes/{node}/evaluator.yaml`

本身是合理的，因为它降低了角色定义的硬编码程度。  
问题不在“外置配置”这个方向，而在“只外置了一半，另一半没有进入 prompt”。

## 5.3 pipeline 级上下文累积思路是对的

`accumulate_context()` 把前序节点 deliverable 注入后续节点，这是正确方向。  
问题在后半段消费链路上被重新打散、串化和弱化了。

---

## 6. 当前安排中最不合理的部分

## 6.1 `node.yaml` 任务契约没有真正注入

`NodeLoader.load()` 会读取 `node.yaml / persona.json / evaluator.yaml`，但在 `node_execution/executor.py` 里，`node_config` 只被加载并记录日志，后续没有把 `task.description`、`role_supplement`、`required_sections` 等注入给 agent。

见 `autoBMAD/docuswarm/node_execution/executor.py:107-145`。

这导致:

- 配置层很丰富
- prompt 层却只消化了 persona 和 criteria
- “节点定义”与“节点执行”是脱节的

这不是局部瑕疵，而是上下文注入设计的结构性问题。

## 6.2 任务语义退化成“原始上下文全文”

`_extract_task_from_state()` 当前把 `subject_context.content` 当 task。

见 `autoBMAD/docuswarm/node_execution/executor.py:228-243`。

这样会造成两个后果:

1. 原始上下文承担了“任务说明”的职责
2. 节点特有任务被淹没

结果是:

- analyst 没有真正被告知“你要产出 Product Brief”
- pm 没有真正被告知“你要产出 PRD”
- architect 没有真正被告知“你要产出技术架构说明”

它们只是拿着同一份大上下文，用不同 persona 去写。

## 6.3 DualAgentNode 再包装破坏了内容结构

`DualAgentNode` 把 `subject_context` 包成:

```python
{"subject": subject_context, "task": task}
```

见 `autoBMAD/docuswarm/nodes/dual_agent.py:320-327`。

这让 `IndependentAgent` 的“按路径提取 content”逻辑失去稳定前提。  
这类“先结构化、再串化、再重建结构”的做法，本身就是不合理的上下文注入方式。

## 6.4 “完整交付物”和“摘要交付物”双轨并存

Independent prompt 明确规定:

- 完整文档应通过工具写盘
- `deliverable.content` 只返回摘要

见 `autoBMAD/docuswarm/agents/independent.py:143-176`。

但 `pipeline/graph.py` 又会在节点成功后，把 `executed_node_state["deliverable"]` 里的 `content` 再写入 `FileStorage`:

- `deliverable.get("content") or deliverable.get("markdown")`

见 `autoBMAD/docuswarm/pipeline/graph.py:381-458`。

这会导致两种并行产物:

1. 工具写出的“完整文档”
2. 状态层再写出的“摘要文档”

这是当前最危险的上下文污染源之一，因为后续节点的链式上下文很可能拿到的是摘要，不是完整 deliverable。

## 6.5 `update_context` 是假的共享记忆接口

名义上系统支持 agent 更新共享上下文，实际上工具什么都不写。

这意味着:

- agent 不能通过工具把新事实注回系统
- “问答-补充-再执行”闭环无法依赖工具层完成
- 文档里承诺的上下文可演化能力没有真正落地

## 6.6 `@` 路径注入和 docs 注入没有形成闭环

PRD 与研究文档多次宣称:

- `@ Path Context Injection` 已完成
- `ContextResolver` 已完成

但当前代码中:

- `autoBMAD/docuswarm/utils/context_resolver.py` 文件不存在
- `main.py` 的 `start` 命令也没有任何 `ContextResolver` 调用

见 `autoBMAD/docuswarm/main.py:92-138`。

因此当前系统的“文档引用注入”实际上只有两种能力:

1. 用户自己把内容贴进 context 文件
2. agent 运行时自行调用 `read_docs_file`

这不等于“系统级上下文注入机制”。

## 6.7 文档与代码的 SDK/工具承诺严重漂移

`PRD.md` 和架构文档大量声明:

- 已迁移到 `claude-agent-sdk`
- 已移除 `kimi-agent-sdk`
- 工具已改为纯函数 + ToolRegistry

但当前实现仍然广泛使用:

- `kimi_agent_sdk`
- `CallableTool2`
- `KIMI_API_KEY`
- `KimiSessionManager`

见:

- `docs/plan/PRD.md:44, 66-70, 194-221`
- `autoBMAD/docuswarm/llm/session_manager.py:26-38, 97-127`
- `autoBMAD/docuswarm/tools/create_deliverable.py:10, 53-95`
- `autoBMAD/docuswarm/tools/update_context.py:7, 28-60`

这会直接削弱“上下文注入安排”的可评估性，因为文档描述的系统和真实系统不是同一套。

---

## 7. 与设计文档的偏差评估

## 7.1 相对 PRD 的偏差

PRD 期望的是:

1. 5 个节点独立执行
2. 自动 context chaining
3. `@` 路径注入
4. 工具主动产出 deliverable
5. 已迁移到 `claude-agent-sdk`

当前实现的真实状态是:

1. 5 节点确实顺序执行
2. chaining 在管道层存在
3. `@` 路径注入未见真实实现
4. 工具产出与状态层产出是双轨
5. 仍使用 `kimi-agent-sdk`

结论:

> PRD 对“能力完成度”的描述显著领先于当前代码实现。

## 7.2 相对架构文档的偏差

架构文档强调:

- BMM-aligned system prompt
- task / deliverable / role_supplement 注入
- prompt template separation

当前代码中:

- prompt 是 agent 类中内联字符串构造
- `prompts/*.md` 模板存在，但运行时未被实际使用
- BMM task/deliverable 配置没有接入 prompt

因此:

> 架构层已经定义了更好的注入模型，但实现层没有真正落地到同一条执行链。

## 7.3 相对 UX 设计文档的偏差

UX 设计文档隐含的前提是:

- 每个节点的输出具备明确类型和质量界面
- 用户能信任节点身份与交付结构

当前由于节点 task / deliverable schema 注入不足，用户实际上拿到的是:

- “由某 persona 写的文档”

而不是稳定的:

- “遵循该节点契约产出的文档”

这会降低可预测性与信任感。

---

## 8. 对现有安排是否合理的最终评价

### 8.1 合理的部分

以下安排是合理的，建议保留:

1. Evaluator 最小输入面
2. 三层上下文隔离思想
3. persona 与 evaluator criteria 外置到 `nodes/`
4. pipeline 层自动累积前序节点输出
5. work_dir 按 pipeline 隔离

### 8.2 不合理的部分

以下安排不合理，且已影响系统正确性:

1. `node.yaml` 被加载但不参与 prompt 构建
2. task 被退化为原始 context 文本
3. DualAgentNode 二次包装破坏上下文结构
4. 完整交付物与摘要交付物双轨并存
5. `update_context` 无真实持久化
6. docs 工具缺少使用策略
7. `@` 注入与 SDK 迁移文档承诺未落地

### 8.3 最终判断

如果只问“现在这样能不能跑起来”，答案是“多数情况下能勉强跑”。  
如果问“现在这样是否是一个合理、可维护、与文档一致的 agent 上下文注入架构”，答案是:

> 不算合理，最多算一个过渡中的半成品架构。

---

## 9. 建议的整改方向

## 9.1 P0：收敛为单一上下文协议

建议定义统一的 `AgentInput` / `NodeExecutionContext`，至少包含:

- `node_id`
- `node_task`
- `role_supplement`
- `deliverable_requirements`
- `original_context`
- `chained_deliverables`
- `answered_questions`
- `iteration_feedback`

然后禁止:

- 把结构化上下文先转成字符串再传
- 在不同层反复重包装相同数据

## 9.2 P0：让 `node.yaml` 真正进入 prompt

IndependentAgent prompt 至少应显式包含:

1. 节点任务名
2. 节点任务描述
3. role supplement
4. deliverable required sections
5. 文件命名或模板标题要求

否则 5 个节点只是“不同 persona 的通用写作模式”。

## 9.3 P0：消除摘要/正式文档双轨

二选一即可:

1. 工具写盘为唯一真相，状态层只存 metadata
2. 状态层持有完整 markdown，工具只负责副本落盘

当前这种“工具写全文 + 状态写摘要”的模式必须移除。

## 9.4 P1：让 `update_context` 真的接入 StateManager

否则它不应继续作为“可用工具”暴露给 agent。  
当前更合理的做法是:

- 要么实现真实持久化
- 要么暂时移出 agent_file

## 9.5 P1：把 docs 工具升级成受控上下文扩展策略

建议为 IndependentAgent 加入明确规则:

- 先用 `list_docs_files`
- 再按节点需求用 `read_docs_file`
- 只把摘要并入 prompt，不把整库 docs 无差别灌入

这比“工具注册了，但 agent 自己随机决定要不要用”更可控。

## 9.6 P1：恢复文档与实现一致性

必须尽快统一以下两组事实:

1. PRD/架构文档里宣称的 SDK、工具系统、ContextResolver 状态
2. 仓库中真实存在并运行的代码

否则任何后续关于“上下文注入是否合理”的讨论，都会被文档漂移持续干扰。

---

## 10. 最终结论

当前 `@autoBMAD/docuswarm` 的各个 agent 上下文注入安排，优点是“隔离意识强”，缺点是“业务契约弱、执行链不收敛、文档与实现漂移大”。

更准确地说:

- **Evaluator 注入安排**: 基本合理，且是系统当前最健康的部分。
- **Independent 注入安排**: 只有 persona 注入相对稳定，任务/交付物/文档/状态注入都不够闭环。
- **节点级差异化**: 主要停留在 persona 与 criteria，尚未升级为真正的“节点专属上下文协议”。
- **整体架构合理性**: 适合继续重构，不适合被当作已定型方案。

如果要把 DocuSwarm 的 agent 体系从“能跑”提升到“可信赖”，优先级最高的工作不是再加新 agent，而是先把上下文注入协议收敛成一条真实、单一、可验证的主链。

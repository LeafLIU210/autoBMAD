# DocuSwarm Blocking Question 机制移除评估报告

日期: 2026-05-01  
审查对象: `autoBMAD/docuswarm`  
依据报告: `docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md`  
审查方法: `code-review-pro`，重点评估 blocking question 是否应保留、移除范围、替代设计和回归风险。  

## 执行摘要

结论:

**建议移除“交互式 blocking question / answer / pause-resume”机制，不建议完全删除所有 `questions` 数据字段。**

原因是当前实现和用户实际使用模式之间存在根本错位:

- 用户不会在 pipeline 运行中回答代理问题。
- 当前 `QuestionHandler` 是内存态，CLI 每次新建 handler，无法读取 pipeline 运行时收集的问题。
- `answer` 命令无法命中历史问题，也不会触发真正恢复执行。
- README 描述的“blocking 问题自动暂停、回答后恢复”并未在实际执行路径中成立。
- 本次 pipeline final state 已证明: PO 产生了 blocking question，但 pipeline 仍 completed。

因此，与其补齐一个用户不会使用的交互系统，不如把它降级为**非阻塞诊断/风险记录**:

- 保留节点输出里的 `questions` 或改名为 `open_issues` / `follow_ups`。
- 移除 `blocking` 优先级的执行语义。
- 移除或隐藏 CLI `questions` / `answer` 命令。
- 删除 `QuestionHandler` 的 answer/pause 相关代码，避免制造“可交互恢复”的错觉。
- 若某个问题真的会阻断执行，应由 evaluator 返回 `BLOCKED` 或由 node executor 抛出结构化错误，而不是通过用户回答流程解决。

## 背景与触发点

上一份评估报告将 “blocking question 没有 gating” 列为 High Priority，建议在节点 approved 后检查 unanswered blocking questions。该建议在“交互式、人类会回答问题”的产品假设下成立。

但用户明确指出: **实际使用过程中用户不会回答这些问题。**

在这个前提下，继续补齐 gating 会带来反效果:

- pipeline 会因为代理自发问题而暂停。
- 用户不会回答，pipeline 会卡住。
- 自动化文档流水线会变成人工交互流程。
- 系统复杂度上升，但没有实际用户价值。

因此本报告重新评估: blocking question 机制是否应删除。

## 关键发现

### Finding 1: `QuestionHandler` 没有持久化，CLI 查询/回答在真实运行后不可用

Severity: High  
Evidence:

- `autoBMAD/docuswarm/pipeline/questions.py:89-97`
- `autoBMAD/docuswarm/cli/commands/questions.py:29-32`
- `autoBMAD/docuswarm/cli/commands/answer.py:44-50`

`QuestionHandler` 只维护:

```python
self._questions: dict[str, list[Question]] = {}
```

CLI `questions` 和 `answer` 每次执行都会新建:

```python
question_handler = QuestionHandler(state_manager=state_manager)
```

这意味着 CLI 进程里没有 pipeline 运行时收集的内存问题。除非同一 Python 对象生命周期内立即调用，否则 `get_unanswered_questions()` 返回空，`answer_question()` 找不到问题。

Impact:

- README 宣称的 `questions <pipeline_id>` / `answer <question_id>` 工作流基本不可达。
- 用户即使想回答，也拿不到问题。
- 补齐 blocking gating 前必须先做问题持久化，否则会阻断但无法恢复。

Recommendation:

不要补齐这个交互系统。删除 `QuestionHandler.answer_question()`、CLI `answer`、CLI `questions` 的交互承诺。若保留问题展示，应直接从 pipeline final state 的 `questions` 字段读取，作为只读诊断。

### Finding 2: create_dual_agent_node 默认没有注入 QuestionHandler，问题收集器不是主路径组件

Severity: High  
Evidence:

- `autoBMAD/docuswarm/nodes/dual_agent.py:136-151`
- `autoBMAD/docuswarm/nodes/dual_agent.py:181-186`
- `autoBMAD/docuswarm/nodes/dual_agent.py:830-888`

`DualAgentNode` 支持传入 `question_handler`，但 `create_dual_agent_node()` 创建节点时只传入 config、agents、node_id、max_iterations:

```python
return DualAgentNode(
    config=config,
    independent_agent=independent_agent,
    evaluator_agent=evaluator_agent,
    node_id=node_id,
    max_iterations=max_iterations,
)
```

因此运行主路径没有启用 `QuestionHandler.collect_questions()`。问题仍会通过 `NodeResult.questions` 进入 pipeline state，但不会进入 `QuestionHandler` 的内存管理。

Impact:

- `has_blocking_questions()` 从未成为执行决策的一部分。
- CLI question 管理与 pipeline state 中的 `questions` 是两套不相连的数据模型。
- 继续保留 QuestionHandler 会让维护者误以为有一个可用问题系统。

Recommendation:

删除 `QuestionHandler` 执行组件，保留 pipeline state 的 `questions` 作为交付物元数据或改名为 `follow_ups`。

### Finding 3: README 描述的 paused/answer/resume 流程与代码不一致

Severity: High  
Evidence:

- `autoBMAD/docuswarm/README.md:314-328`
- `autoBMAD/docuswarm/README.md:613-620`
- `autoBMAD/docuswarm/README.md:672-690`
- `autoBMAD/docuswarm/storage/state_manager.py:37-38`

README 描述:

- `questions` 命令列出未回答问题。
- `answer` 命令回答问题。
- `paused` 表示等待回答。
- blocking 问题会自动暂停。
- 回答后自动恢复。

实际代码:

- `QuestionHandler` 不持久化。
- `create_dual_agent_node()` 不接入 `QuestionHandler`。
- pipeline 没有基于 blocking question 转为 `paused` 的主路径。
- `StateManager` 合法状态包含 `paused`，但没有看到 blocking question 驱动的暂停逻辑。

Impact:

- 文档承诺高于实现能力。
- 用户可能尝试一个不可用工作流。
- 后续开发会围绕错误架构假设继续堆代码。

Recommendation:

如果决定移除交互式问题机制，应同步更新 README:

- 删除“管理问题与回答”章节。
- 删除 `paused (有阻塞问题)` 状态说明，或改为仅由显式 `pause` 命令触发。
- 将“问题优先级与升级机制”改为“节点诊断与后续事项”。

### Finding 4: `blocking` 语义鼓励代理提问，但用户不回答时会污染成功输出

Severity: Medium  
Evidence:

- `autoBMAD/docuswarm/prompts/contract_builder.py:688-723`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:96-115`
- `autoBMAD/docuswarm/context/validator.py:585-586`

IndependentAgent prompt 明确要求生成 follow-up questions，并提供 `blocking | clarifying | optional`。工具 schema 和 validator 也接受这三类。

在用户不回答的产品模式下，`blocking` 会变成一种无效标签:

- 如果不阻断，标签语义是假的。
- 如果阻断，pipeline 会卡住。
- 如果让 evaluator 忽略，代理仍会持续生成“阻塞但不阻塞”的噪音。

Recommendation:

移除 `blocking` 优先级，改为只允许:

- `risk`: 影响实现/验收的风险，记录但不等待回答。
- `assumption`: 代理采取的默认假设。
- `follow_up`: 未来可改进项。

最小兼容版本可以保留字段名 `questions`，但把 priority enum 改为 `clarifying | optional`，并在 prompt 中禁止使用 blocking。

### Finding 5: 存在第二套 `QuestionPriority` 定义，priority 语义已经分叉

Severity: Medium  
Evidence:

- `autoBMAD/docuswarm/pipeline/questions.py:30-41` 定义 `QuestionPriority = {BLOCKING, CLARIFYING, OPTIONAL}`
- `autoBMAD/docuswarm/llm/response.py:13` 定义 `QuestionPriority = Literal["low", "medium", "high", "critical"]`
- `autoBMAD/docuswarm/context/validator.py:586` 使用小写枚举 `{"blocking", "clarifying", "optional"}`
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:107-108` 工具 schema enum 使用 `["blocking", "clarifying", "optional"]`

Issue:

项目中同时存在两套命名体系（`BLOCKING/CLARIFYING/OPTIONAL` vs `low/medium/high/critical`）。两者互不兼容，在维护上容易踩坑:

- 下游读取 state 时需要预判到底会拿到哪一套字符串。
- 新手会误以为 `llm/response.py` 的 `QuestionPriority` 也参与执行决策。
- `.upper()` 兼容层进一步掩盖了设计分歧。

Impact:

- 清理 blocking priority 时必须同步处理两套枚举，避免遗漏。
- 如果只删除 `pipeline/questions.py` 的 BLOCKING，`llm/response.py` 的 critical 会被误当作下一代阻断值继续扩散。

Recommendation:

- 在 Phase 1 同步删除 `llm/response.py` 中未被真正使用的 `QuestionPriority` 类型别名，或标记为 `deprecated`。
- 统一对外口径: 节点输出侧一律使用小写 `{clarifying, optional}`；内部枚举统一命名，不再 `.upper()` 兼容。

### Finding 6: 完全删除 `questions` 字段会损失有用的审计信号

Severity: Medium  
Evidence:

- `autoBMAD/docuswarm/node_execution/executor.py:157-160`
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:303-308`
- `autoBMAD/docuswarm/storage/state_manager.py:263-320`
- 上一份评估报告中 pipeline final state 的 PO blocking question 暴露了上游交付物可见性问题。

虽然交互式回答机制不适合当前使用模式，但代理提出的问题本身仍有审计价值。它能暴露:

- 上游上下文缺口。
- 文档追溯歧义。
- 代理做了哪些默认假设。
- 后续自动化改进点。

Recommendation:

不要一刀切删除所有 `questions` 数据流。建议改为:

- `questions` -> `diagnostics` 或 `follow_ups`
- 去掉“必须回答”的语义。
- 作为 report metadata 保存和导出。
- 不进入 pipeline routing。

## 是否应当移除

### 应移除的部分

1. `QuestionHandler` 的交互式内存管理职责。
2. `QuestionPriority.BLOCKING` 的阻断含义。
3. CLI `answer` 命令。
4. CLI `questions` 命令的“未回答问题”语义。
5. README 中“blocking 问题自动暂停、回答后恢复”的承诺。
6. prompt 中“blocking: Must be answered before proceeding”的描述。
7. schema / validator 中对 `blocking` priority 的接受。

### 应保留或重命名的部分

1. NodeResult 中的 `questions` 列表，短期可保留以兼容测试和现有 pipeline state。
2. StateManager 的 `questions_json` 字段，短期保留以避免 DB migration 过大。
3. pipeline state 的 `questions` 字段，建议逐步迁移为 `diagnostics` / `follow_ups`。
4. create_deliverable / submit_execution_report 的 `questions` 字段，短期改语义，长期改名。

## 推荐目标设计

### 新语义: 非阻塞诊断

将 agent 输出从:

```json
{
  "questions": [
    {
      "question": "Should we support X?",
      "priority": "blocking",
      "context": "Need this before proceeding"
    }
  ]
}
```

改为:

```json
{
  "diagnostics": [
    {
      "type": "assumption",
      "message": "Assumed X is out of scope.",
      "impact": "May need revision if scope changes."
    }
  ]
}
```

如果为了兼容暂时保留 `questions`:

```json
{
  "questions": [
    {
      "question": "Assumption: X is out of scope. Confirm in future if needed.",
      "priority": "clarifying",
      "context": "Recorded for review; does not block execution."
    }
  ]
}
```

### 真正阻断的场景由 evaluator / executor 表达

若缺少信息导致不能继续，应采用现有质量控制路径:

- IndependentAgent 仍生成交付物时: evaluator 返回 `NEEDS_REVISION` 或 `BLOCKED`。
- IndependentAgent 无法生成交付物时: executor 抛出结构化错误，pipeline status = `failed` 或 `blocked`。
- 用户提供更多信息的方式: 修改 context 文件后重新运行或 resume/restart，而不是回答单个 question。

## 代码影响映射

本节根据 `grep` 验证结果整理所有需要改动的文件与关注点，便于实施者一次性评估范围。

### 需要修改的核心文件

| 文件 | 当前职责 | 改动方向 | 阶段 |
|------|---------|---------|------|
| `autoBMAD/docuswarm/pipeline/questions.py` | `QuestionPriority` / `Question` / `QuestionHandler` | 删除 `BLOCKING`，移除 `answer_question()` / `has_blocking_questions()` / `_incorporate_answer()`，或整个模块替换为 read-only shim | P1 + P2 |
| `autoBMAD/docuswarm/cli/commands/answer.py` | `docuswarm answer` 命令 | **整文件删除** | P2 |
| `autoBMAD/docuswarm/cli/commands/questions.py` | `docuswarm questions` 命令，构造内存 `QuestionHandler` | 改造为读 pipeline final state 的只读展示；重命名为 `diagnostics` | P2 |
| `autoBMAD/docuswarm/cli/main.py:13-24,85-86` | 注册 `answer`, `questions` | 取消注册 `answer`；`questions` 改为 `diagnostics` | P2 |
| `autoBMAD/docuswarm/nodes/dual_agent.py:148,181-186,662-674` | `DualAgentNode` 的 `question_handler` 参数与 `collect_questions()` 调用 | 参数与调用全部删除；`NodeResult.questions` 直接原样入 state | P2 |
| `autoBMAD/docuswarm/prompts/contract_builder.py:688-723` | Prompt 中关于问题优先级的说明 | 删除 `blocking` 行，说明改为 non-blocking follow-ups | P1 |
| `autoBMAD/docuswarm/agents/independent.py:228,242,283` | IndependentAgent system prompt 内置 `blocking \| clarifying \| optional` | 删除 `blocking`；调整示例 JSON 去掉 blocking 优先级 | P1 |
| `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:107-108` | `submit_execution_report` 工具 schema 的 priority enum | enum 删除 `blocking`，description 改为非阻塞措辞 | P1 |
| `autoBMAD/docuswarm/context/validator.py:585-586` | `VALID_PRIORITIES` 集合 | 删除 `blocking`；未知值不再默认映射为 blocking | P1 |
| `autoBMAD/docuswarm/llm/response.py:13` | 冗余 `QuestionPriority = Literal["low"...]` | 标记 deprecated 或直接删除 | P1 |
| `autoBMAD/docuswarm/README.md:314-328, 613-620, 672-690` | 交互式问答工作流说明 | 删除 paused/answer 章节；新增 diagnostics 说明 | P1 |

### 可以保留但需留意的文件

| 文件 | 说明 |
|------|------|
| `autoBMAD/docuswarm/pipeline/state.py:54,73,115,149` | `PipelineState` TypedDict 中的 `questions` 字段，短期保留以兼容现有 state |
| `autoBMAD/docuswarm/pipeline/orchestrator.py:682,771-828,979` | checkpoint 恢复中读取/写入 `questions`，保留字段读写即可 |
| `autoBMAD/docuswarm/pipeline/graph.py:92-93,342-385` | graph 初始化和 mock 节点的 `questions` 字段 |
| `autoBMAD/docuswarm/storage/state_manager.py:299-371,1026-1057` | SQLite `questions_json` 列写入/读取，短期保留避免 DB 迁移 |
| `autoBMAD/docuswarm/storage/database.py:197,217` | schema 定义的 `questions_json TEXT` 列，保留至少一个版本 |

---

## 数据库与持久化兼容性分析

### 现状

- `node_iterations` 和 `pipelines` 两张表均有 `questions_json TEXT` 列。
- `StateManager` 写入的是 IndependentAgent 返回的 raw `questions` 列表。
- 历史 pipeline 可能已落盘 `priority='blocking'` 的数据。

### 兼容策略（与 Phase 对齐）

1. **Phase 1（停止产生 blocking）** 不涉及 DB 结构变更，只影响新写入的数据。旧数据中的 `blocking` 值**必须在读取侧容忍**:
   - 读取 `questions_json` 时，若 `priority='blocking'`，降级为 `clarifying` 并在日志中告警一次。
2. **Phase 2（移除 CLI + QuestionHandler）** 不动 DB。`state_manager.get_node_iteration_history()` 等方法仍读取 `questions_json`，作为诊断输出。
3. **Phase 3（重命名）** 采用 **dual-read / single-write**:
   - 新代码写 `diagnostics_json`。
   - 读取时优先读 `diagnostics_json`，fallback 读 `questions_json`。
   - 至少保留两个 release 后再清理旧列。

### 不能做的事

- 不得直接 `DROP COLUMN questions_json`，否则无法恢复历史 pipeline。
- 不得在单次 migration 中重命名列并删除旧数据。
- 不得让 ORM 层强制要求 `diagnostics_json` 非空，否则老数据读取会报错。

---

## 迁移方案

### Phase 1: 停止生成 blocking question

Scope: prompt/schema/validator/docs  
Risk: Low

修改点:

- `autoBMAD/docuswarm/prompts/contract_builder.py`
  - 删除 `blocking` 说明。
  - 将 “Generate Questions” 改为 “Record Non-blocking Follow-ups”。
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py`
  - priority enum 删除 `blocking`。
  - description 改为非阻塞。
- `autoBMAD/docuswarm/context/validator.py`
  - `VALID_PRIORITIES` 删除 `blocking`。
- `autoBMAD/docuswarm/agents/independent.py`
  - 若仍有内置 prompt，删除 blocking 表述。
- README 删除 paused/answer/questions 的交互承诺。

验收标准（Definition of Done）:

- [ ] 新 pipeline final state 中 `questions[*].priority` 不出现 `blocking`。
- [ ] agent prompt 源文件 grep `blocking` 无结果（大小写均检查）。
- [ ] `autoBMAD/docuswarm/context/validator.py` 的 `VALID_PRIORITIES` 仅含 `{clarifying, optional}`。
- [ ] 工具 schema 对 `priority=blocking` 直接拒绝。
- [ ] README 不再提及 "must be answered before proceeding"。
- [ ] 存在读取侧兼容逻辑，能把历史 `blocking` 值降级为 `clarifying`。
- [ ] 新增回归用例: `test_independent_prompt_has_no_blocking_questions`、`test_submit_execution_report_rejects_blocking_priority`。

### Phase 2: 移除不可用 CLI 和 QuestionHandler

Scope: CLI / pipeline question module  
Risk: Medium

修改点:

- 移除 `autoBMAD/docuswarm/cli/commands/answer.py`。
- 移除或改造 `autoBMAD/docuswarm/cli/commands/questions.py`。
- 从 `autoBMAD/docuswarm/cli/main.py` 取消注册 `answer`。
- 删除 `autoBMAD/docuswarm/pipeline/questions.py`，或保留一个只读 compatibility shim。
- 清理 `DualAgentNode` 的 `question_handler` 参数和收集逻辑。

兼容策略:

- 若用户仍想查看问题，新增 `docuswarm diagnostics <pipeline_id>`，直接读取 pipeline state 的 `questions` / `diagnostics`。
- 保留 DB `questions_json` 字段至少一个版本，不做破坏性 migration。

验收标准（Definition of Done）:

- [ ] `docuswarm --help` 不再展示 `answer` 子命令。
- [ ] `docuswarm answer` 执行报 `Unknown command`。
- [ ] `docuswarm diagnostics <pipeline_id>` 可直接读取 pipeline state，列出 follow-ups。
- [ ] `DualAgentNode.__init__` 签名不再包含 `question_handler` 参数；或参数保留但内部未被使用且带有 `deprecated` 警告。
- [ ] `pipeline/questions.py` 要么被删除，要么只剩一个不含 `answer_question()` 的 read-only shim。
- [ ] 没有任何主路径代码调用 `has_blocking_questions()`。
- [ ] 新增回归用例: `test_cli_no_answer_command`、`test_diagnostics_export_includes_followups`。

### Phase 3: 字段重命名

Scope: schema / state / storage / tests  
Risk: Medium-High

长期将:

- `questions` -> `diagnostics`
- `priority` -> `type` 或 `severity`
- `question` -> `message`

并保留旧字段读取兼容:

```python
diagnostics = state.get("diagnostics") or state.get("questions", {})
```

验收标准（Definition of Done）:

- [ ] 新代码一律写 `diagnostics` / `diagnostics_json`。
- [ ] 读取侧同时支持 `diagnostics` 和 `questions` 两个字段至少两个 release。
- [ ] DB schema 保留 `questions_json` 列，不做 `DROP COLUMN`。
- [ ] 历史 pipeline export 不损失任何信息。
- [ ] 迁移窗口明确（如 v0.x -> v0.x+2 清理），并在 CHANGELOG 中标注。

---

## 回滚方案

所有 Phase 都应保证可回滚。关键原则: **删除行为不得触碰数据库结构**。

| Phase | 回滚代价 | 回滚动作 |
|-------|---------|---------|
| P1 | 低 | `git revert` prompt/schema/validator 改动即可，DB 层未动 |
| P2 | 中 | 恢复 `answer.py`、`questions.py` 注册；`DualAgentNode` 参数回迁；historical state 仍可读 |
| P3 | 高 | 必须保留 dual-read 代码路径 + 旧列不可删除，否则回滚会丢数据。**Phase 3 不得独立上线，必须等 Phase 1/2 稳定两个 release 后再执行** |

若用户在某 release 后要求恢复交互式问答系统，需要从头设计 **持久化 + paused 状态机 + resume 注入 + node restart** 四件套（参考「不推荐 2」小节的清单），无法仅靠回滚现有代码完成。

## 不推荐方案

### 不推荐 1: 补齐 blocking gating

在当前用户不会回答问题的前提下，不建议实现:

```python
if has_blocking_questions:
    status = "paused"
```

这会把自动化流水线变成不可恢复的人工等待状态。

### 不推荐 2: 保留 `answer` 命令但修持久化

修复这个流程至少需要:

- questions 表或 questions_json 索引。
- paused 状态机。
- resume 时 context 注入。
- 回答后的 node restart 语义。
- CLI/UX 文档。

这套成本很高，而用户明确不会使用。

### 不推荐 3: 完全删除所有 questions 字段

这样会损失 useful diagnostics，也会制造大范围 schema/test/storage 迁移。更稳妥的是先删除 blocking 和交互式回答，再逐步迁移字段名。

## Code Review Findings

### Critical Issues

未发现与 blocking question 机制相关的直接安全漏洞。

### High Priority Issues

1. **不可用的 CLI 工作流**  
   `questions` / `answer` 依赖新建的内存 `QuestionHandler`，无法读取 pipeline 运行时问题。

2. **文档承诺与实现不一致**  
   README 声称 blocking 会暂停并等待回答，但主执行路径不支持。

3. **错误产品假设**  
   在用户不会回答问题的使用模式下，blocking priority 是错误抽象。

### Medium Priority Issues

4. **Prompt 诱导代理产生无效阻塞项**  
   contract_builder 明确要求生成 follow-up questions，并赋予 blocking 语义。

5. **Schema / validator 扩散了无效语义**  
   `blocking` 已进入 tool schema、output validator、README、agent prompt，删除需要成组处理。

6. **问题和诊断混在同一字段**  
   当前 `questions` 既像用户交互项，又像审计诊断项。建议拆语义或重命名。

### Low Priority Issues

7. **Question ID 格式脆弱**  
   `answer.py` 用 `rsplit("_", 2)` 解析 ID，pipeline_id/node_id 中包含 `_` 时风险较高。若移除 answer 命令，该问题自然消失。

8. **大小写语义不一致**  
   enum 是 `BLOCKING`，schema 是 `blocking`，handler 通过 `.upper()` 兼容。若保留，需统一；若移除，直接消除。

## 回归测试建议

如果按本报告移除交互式 blocking question，应新增或更新:

1. `test_independent_prompt_has_no_blocking_questions`
   - 断言 prompt 不包含 `blocking` 和 `Must be answered before proceeding`。

2. `test_submit_execution_report_rejects_blocking_priority`
   - validator 对 `priority='blocking'` 给出明确错误，或将其降级为 `clarifying` 并记录 warning。

3. `test_pipeline_completes_with_followups`
   - agent 返回 `clarifying` / `optional` follow-ups 时 pipeline 仍 completed。

4. `test_cli_no_answer_command`
   - CLI 不再注册 `answer`。

5. `test_diagnostics_export_includes_followups`
   - export/status 能展示非阻塞 follow-ups，避免丢失审计信号。

如果短期只禁用 blocking、不删除命令，也至少需要:

1. `test_questions_cli_reads_pipeline_state_not_memory_handler`
2. `test_answer_command_disabled_with_clear_message`

## 推荐决策

建议采用 **Option B: 删除交互机制，保留非阻塞诊断字段**。

| 选项 | 描述 | 评价 |
|------|------|------|
| A | 补齐 blocking gating + pause/answer/resume | 不推荐。用户不会回答，成本高且会卡 pipeline |
| B | 移除 blocking/answer/pause，保留 follow-up diagnostics | 推荐。符合自动化使用模式，风险可控 |
| C | 完全删除 questions 字段和所有相关存储 | 不推荐。破坏范围大，丢失审计信息 |
| D | 什么都不做 | 不推荐。继续保留虚假交互承诺 |

## 实施清单（建议 checklist）

实施者可按此顺序推进，每步独立可 review、可回滚。

### Sprint 1: 停止扩散（对应 Phase 1，风险低）

- [ ] 删除 `prompts/contract_builder.py` 中 `blocking` 说明行。
- [ ] 删除 `agents/independent.py` 内置 prompt 的 `blocking` 示例与描述。
- [ ] 修改 `tools/create_deliverable_sdk.py` priority enum。
- [ ] 修改 `context/validator.py` 的 `VALID_PRIORITIES`。
- [ ] 在 `QuestionHandler.collect_questions()` 读取侧将 `blocking` 降级为 `clarifying` 并告警。
- [ ] 删除或弃用 `llm/response.py` 的冗余 `QuestionPriority` 类型。
- [ ] 更新 README 中 paused/answer 章节。
- [ ] 新增 Phase 1 所列回归用例。
- [ ] 使用 `docs/calc-one-plus-one/calc-context.md` 跑一次 pipeline，确认 final state 中无 `blocking` 值。

### Sprint 2: 下线交互系统（对应 Phase 2，风险中）

- [ ] 从 `cli/main.py` 移除 `answer` 注册。
- [ ] 删除 `cli/commands/answer.py`。
- [ ] 将 `cli/commands/questions.py` 改写为读取 pipeline state 的只读命令，重命名为 `diagnostics`（保留 `questions` 别名一个 release）。
- [ ] `DualAgentNode` 移除 `question_handler` 参数与 `collect_questions()` 调用。
- [ ] `pipeline/questions.py` 保留 `Question` dataclass 和常量，删除 `answer_question()` / `_incorporate_answer()` / `has_blocking_questions()`。
- [ ] 更新 `CONFIGURATION.md` / README。
- [ ] 新增 Phase 2 所列回归用例。

### Sprint 3（可选，长周期）: 字段重命名（对应 Phase 3，风险中-高）

- [ ] 新增 `diagnostics_json` 列（ALTER TABLE ADD COLUMN，不删除旧列）。
- [ ] 写入侧同时写 `questions_json` 与 `diagnostics_json`。
- [ ] 读取侧优先读 `diagnostics_json`，fallback 读 `questions_json`。
- [ ] 至少一个 release 后，写入侧停止写 `questions_json`，仅保留读兼容。
- [ ] CHANGELOG 明确迁移周期。

---

## 风险矩阵

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 历史 pipeline 中的 `blocking` 值导致读取报错 | 中 | 中 | 读取侧兼容降级 + 单测覆盖 |
| 外部脚本依赖 `docuswarm answer` | 低 | 中 | 在 Sprint 1 发版时 deprecation 警告一个 release 周期后再删 |
| `questions_json` DB 列被第三方工具直接查询 | 低 | 低 | 保留列名 + 文档注明字段语义已改为非阻塞 |
| 代理仍尝试返回 `priority='blocking'` | 高 | 低 | validator 强拒或自动降级，日志 warning |
| 重命名 Phase 3 未完成就被其他特性覆盖 | 中 | 低 | Phase 3 独立 epic 管理，不与业务特性混排 |

---

## 最终结论

应当移除 blocking question 相关交互代码和模块，但不应删除所有问题/后续事项信息。

最合理的方向是:

1. **废弃 blocking priority**，禁止代理再生成 “must answer before proceeding”。
2. **移除 answer/questions 交互 CLI**，或改为只读 diagnostics。
3. **删除 QuestionHandler 的内存态回答机制**。
4. **把问题语义改为非阻塞 diagnostics / follow-ups / assumptions**。
5. **真正阻断执行的情况交给 evaluator verdict 或 executor error 处理**。

这会让 DocuSwarm 更符合实际使用: 用户提供一个上下文文件，系统自动跑完整个文档流水线；有疑问就作为报告中的假设和风险呈现，而不是等待用户中途回答。

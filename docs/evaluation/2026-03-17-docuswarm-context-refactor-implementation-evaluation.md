# 2026-03-17 DocuSwarm Context Refactor 实现评估报告

> 评估日期：2026-03-17
> 评估对象：`docs/research/2026-03-13-docuswarm-context-refactor-overview.md`
> 审查范围：`autoBMAD/docuswarm` 及其运行时依赖的根目录 `nodes/*`
> 评估结论：**部分实现，未完成**
> 综合完成度判断：**约 62%**

## 1. 执行摘要

对照总览文档当前定义的五条主线：

1. `P0-1` 单一上下文协议：**部分完成**
2. `P0-2` `node.yaml` prompt 注入：**大体完成，但 Evaluator 链路仍缺一环**
3. `P0-3` 单一交付物真相：**部分完成**
4. `P1-1` `update_context` 持久化：**未完成**
5. `P1-2` docs-free workflow 清理：**大体朝正确方向推进，但边界尚未完全收口**

当前代码库已经把 `NodeExecutionContext`、`NodeExecutionContextBuilder`、`DualAgentNode.execute_with_context()`、`IndependentAgent.execute_with_input()`、`EvaluatorAgent.execute_with_input()`、`NodePromptContractBuilder`、`create_deliverable` metadata 化返回等关键骨架落地，说明这轮重构并不是停留在文档层。

但从“Overview”要求的验收口径看，还不能判定为完成。当前最大的缺口不在“有没有新类”，而在“闭环是否真正成立”：

- `update_context` 在真实 agent 运行时仍不可用。
- `shared_context` 即使写入，也不会进入下一节点 prompt。
- `DeliverableArtifact` 的目标结构与真实运行结构仍不一致，Evaluator 仍可能评审摘要而不是正式正文。
- Evaluator 的新 prompt 合同里没有原始上下文摘要。
- docs-free 的产品决策已经反映到部分代码和注释，但 CLI/README 仍继续把 `docs/*.md` 当标准输入路径。

因此，本次评估判断：**重构主线已经进入中后段，但距离总览文档中的“可验证、可落盘、可审计的单一主链”还有明显差距。**

## 2. 评估依据

本次评估基于以下代码与文档：

- `docs/research/2026-03-13-docuswarm-context-refactor-overview.md`
- `docs/research/2026-03-13-p0-node-prompt-injection-plan.md`
- `docs/research/2026-03-13-p0-single-truth-deliverable-plan.md`
- `docs/research/2026-03-13-p1-update-context-persistence-plan.md`
- `autoBMAD/docuswarm/node_execution/contracts.py`
- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/prompts/contract_builder.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/tools/create_deliverable.py`
- `autoBMAD/docuswarm/tools/update_context.py`
- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/storage/state_manager.py`
- `autoBMAD/docuswarm/llm/response.py`
- `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`
- `nodes/*/node.yaml`

说明：

- 本次未运行完整 `pytest` 套件。
- 评估结论来自代码静态审查，以及若干最小复现脚本。
- 当前 `autoBMAD/docuswarm/tests` 目录下未发现与本轮重构目标直接对应的 source test 文件，这本身也是本报告的结论之一。

## 3. 状态总览

| 主题 | 目标 | 当前判断 | 完成度 |
| --- | --- | --- | --- |
| P0-1 | 收敛为单一上下文协议 | 已接入主执行链，但未收敛到状态层与恢复链路 | 75% |
| P0-2 | 让 `node.yaml` 真正进入 prompt | Independent 基本完成，Evaluator 仍缺最小上下文注入 | 78% |
| P0-3 | 消除摘要/正式文档双轨 | 文件写盘与文件读取已落地，但 contract/验证/下游传播仍不严格 | 55% |
| P1-1 | 让 `update_context` 接入 StateManager | 代码存在，但真实运行链路未闭环 | 25% |
| P1-2 | docs-free workflow | `docs_context`/`ContextResolver` 已基本停止推进，但入口边界仍宽松 | 70% |

## 4. 关键发现

以下发现按严重程度排序。

### F001. `update_context` 仍未形成可用的运行时闭环

这是当前最严重的问题，也是总览文档中 `P1-1` 仍不能判定完成的核心原因。

证据一：`UpdateContextTool` 运行时依赖 `state_manager` 与 `pipeline_id`，但默认 agent 配置只声明了类路径，没有看到任何绑定逻辑。

- `autoBMAD/docuswarm/tools/update_context.py:63-76`
- `autoBMAD/docuswarm/tools/update_context.py:125-136`
- `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:12-15`

最小复现结果：

```text
ToolError
StateManager not available. Cannot update context.
```

证据二：即使 `StateManager.update_shared_context()` 已实现真实写库，`shared_context` 也没有真正进入下一节点的 agent 输入。

- `autoBMAD/docuswarm/node_execution/contracts.py:64-74` 定义了 `shared_context`
- `autoBMAD/docuswarm/context/isolation.py:70-109` 的 `build_independent_input()` 没有输出 `shared_context`
- `autoBMAD/docuswarm/prompts/contract_builder.py:187-219` 的 `_build_context_section()` 也没有渲染 `shared_context`

最小复现结果：

```text
{'task_name': 'create-product-brief', ..., 'original_context_summary': 'ORIGINAL CONTEXT', ...}
```

上面的实际输出里没有任何 `shared_context` 字段。

证据三：恢复链路不会回填 `shared_context`。

- `autoBMAD/docuswarm/pipeline/state.py:57-77` 的 `PipelineState` 未声明 `shared_context`
- `autoBMAD/docuswarm/pipeline/state.py:94-108` 的 `create_initial_state()` 未初始化 `shared_context`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:601-613`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:745-754`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:896-907`

这些恢复路径都会重建 state，但没有把 `shared_context` 放回去。

结论：

- `update_context` 不只是“还有点没打磨”，而是**真实执行语义仍未成立**。
- 下一节点读取上一节点共享上下文这一验收标准当前未满足。

### F002. 单一交付物真相仍未闭环，Evaluator 仍可能评审摘要

当前实现已经迈出了正确的一步，但距离 `P0-3` 的验收标准还有明显差距。

已完成的部分：

- `create_deliverable` 已写盘并返回 metadata，而不是正文
  - `autoBMAD/docuswarm/tools/create_deliverable.py:141-172`
- `ContextManager.build_evaluator_input()` 会在 `file_path` 存在时尝试读正式正文
  - `autoBMAD/docuswarm/context/isolation.py:127-146`

未闭环的部分：

1. `DeliverableArtifact` 目标结构与真实运行结构不一致。

- 目标类型使用 `summary`
  - `autoBMAD/docuswarm/node_execution/contracts.py:22-37`
- 运行时验证仍使用 `deliverable.content`
  - `autoBMAD/docuswarm/llm/response.py:145-181`
- 上游摘要传播也仍读 `deliverable.content`
  - `autoBMAD/docuswarm/context/isolation.py:91-98`

这说明代码库里仍然同时存在两套语义：

- 文档/类型层：`summary`
- 运行时/验证层：`content`

2. `file_path` 和 `sha256` 不是强制字段。

- `autoBMAD/docuswarm/llm/response.py:175-181`

当前验证只要求：

- `deliverable.title`
- `deliverable.content`

而 `file_path` / `sha256` 仅“如果存在则校验类型”。这意味着模型完全可以返回一份只有摘要、没有 artifact metadata 的输出，仍然通过验证。

最小复现结果：

```text
validated
```

对应输入只是：

```json
{
  "deliverable": {
    "title": "T",
    "content": "FULL MARKDOWN BODY WITHOUT FILEPATH"
  },
  "questions": []
}
```

3. Evaluator 在 `file_path` 缺失或不可读时会退回到 `deliverable.content`。

- `autoBMAD/docuswarm/context/isolation.py:130-139`

最小复现结果：

```text
'deliverable_body': 'summary only'
```

这意味着“Evaluator 评分对象始终来自工具写盘后的正式正文”这一标准当前不成立，它只是“尽量如此”。

4. 下游上下文传播仍复制整个 deliverable dict。

- `autoBMAD/docuswarm/pipeline/state.py:220-228`

只要上游 deliverable 里混入了长正文，后续链路仍会继续传播那份正文。

结论：

- `P0-3` 的方向正确，但还没有实现“强约束的单一真相”。
- 当前状态更接近“支持 metadata-first，但仍兼容 summary/body 混用”。

### F003. Prompt 合同链路大体成立，但 Evaluator 仍缺原始上下文摘要

这是 `P0-2` 已有明显进展、但还不能完全判定完成的关键原因。

已完成的部分：

- `NodePromptContractBuilder` 已实现
  - `autoBMAD/docuswarm/prompts/contract_builder.py:46-369`
- `IndependentAgent.execute_with_input()` 已使用 contract builder 组装 prompt
  - `autoBMAD/docuswarm/agents/independent.py:613-726`
- `EvaluatorAgent.execute_with_input()` 已使用 contract builder 组装 prompt
  - `autoBMAD/docuswarm/agents/evaluator.py:519-599`
- 根目录 `nodes/*/node.yaml` 已包含 `task.name`、`task.description`、`role_supplement`、`deliverable.required_sections`、`template_title`、`output_filename`
  - 例如 `nodes/analyst/node.yaml`
  - 例如 `nodes/pm/node.yaml`

这说明当前实现实际上已经部分走到了“节点契约显式化”这一步，且已不完全依赖 overview 写作时提到的旧 schema 假设。

未完成的部分：

1. Evaluator 输入结构没有携带原始上下文摘要。

- `autoBMAD/docuswarm/node_execution/contracts.py:97-106`
- `autoBMAD/docuswarm/context/isolation.py:111-147`

`EvaluatorAgentInput` 当前只包括：

- `task_name`
- `task_description`
- `deliverable_artifact`
- `deliverable_body`
- `criteria`

没有原始上下文字段。

2. `EvaluatorAgent.execute_with_input()` 重建 `NodeExecutionContext` 时直接把 `original_context={}`。

- `autoBMAD/docuswarm/agents/evaluator.py:557-576`

3. `NodePromptContractBuilder` 虽然支持 Evaluator 的最小上下文 section，但由于 `original_context` 被置空，最终渲染不出任何内容。

- `autoBMAD/docuswarm/prompts/contract_builder.py:310-325`

最小复现结果：

```text
## 评审任务
...
## 评分标准
...
## 待评审交付物
BODY
```

中间没有“原始需求摘要”章节。

结论：

- Independent prompt 注入已经相当接近完成。
- Evaluator prompt 仍缺“最小必要上下文摘要”这一关键一环，因此 `P0-2` 应判定为**大体完成但未闭环**。

### F004. 单一上下文协议已经进入主执行链，但尚未收敛到状态层

`P0-1` 的代码落地比 2026-03-13 时更进一步，但还没有完全达到总览文档的目标架构。

已完成的部分：

- `NodeExecutionContext` 与相关 TypedDict 已定义
  - `autoBMAD/docuswarm/node_execution/contracts.py:39-106`
- `NodeExecutionContextBuilder` 已实现
  - `autoBMAD/docuswarm/node_execution/context_builder.py:16-109`
- `executor` 已显式构建 `execution_context`
  - `autoBMAD/docuswarm/node_execution/executor.py:107-147`
- `DualAgentNode.execute_with_context()` 已成为新的主执行入口
  - `autoBMAD/docuswarm/nodes/dual_agent.py:336-585`

而且之前“原始上下文丢失”的问题现在已经被修正：

- `autoBMAD/docuswarm/node_execution/executor.py:269-307`

最小复现结果：

```text
{'subject_context': {'task': 'Build app', 'content': 'User wants a collaborative task app'}, 'content': 'User wants a collaborative task app'}
```

说明 `subject_context.content` 已能被归一化到顶层 `content`。

但未完成的部分仍然明确存在：

1. `PipelineState` / `NodeRunState` 仍然不是 overview 里的目标协议形态。

- `autoBMAD/docuswarm/pipeline/state.py:57-77`
- `autoBMAD/docuswarm/node_execution/state.py:44-61`

当前状态层仍以：

- `context_file`
- `chained_context`
- `deliverables`

为主，而不是显式持有 `execution_context`。

2. `pipeline/graph.py` 到 `executor.py` 之间仍靠旧状态结构适配。

- `autoBMAD/docuswarm/pipeline/graph.py:191-223`
- `autoBMAD/docuswarm/node_execution/executor.py:113-123`

这说明当前更接近：

- “新协议已经成为 executor 之后的主链”

而不是：

- “从 pipeline state 开始就已经全链统一”

结论：

- `P0-1` 应判定为**部分完成且完成度较高**。
- 但如果按 overview 第 5 节的目标架构看，状态层收敛仍未到位。

### F005. docs-free workflow 已停止推进 docs 扩展方案，但入口边界尚未完全收口

按总览文档 2026-03-17 的更新口径，`P1-2` 已被移除，重点变成“工作流不再读取 `docs/` 作为运行时扩展上下文”。

朝正确方向推进的证据：

- `NodeExecutionContextBuilder` 当前固定 `docs_context=[]`
  - `autoBMAD/docuswarm/node_execution/context_builder.py:74-76`
- `NodeExecutionContext` 仍保留 `docs_context` 字段，但未见 `ContextResolver` 实装接入
  - `autoBMAD/docuswarm/node_execution/contracts.py:72-74`
- 当前仓库检索中未见新的 runtime `ContextResolver` / docs tools 主链集成

但边界尚未完全收口：

- CLI 仍直接读取用户提供的 context file
  - `autoBMAD/docuswarm/main.py:97-134`
- README 仍把 `docs/epics/EPIC-01.md`、`docs/proposal.md` 作为标准工作流示例
  - `autoBMAD/docuswarm/README.md:157-158`
  - `autoBMAD/docuswarm/README.md:371`

结论：

- “不再做 docs 上下文扩展能力”基本已反映到代码主线。
- 但“workflow never reads docs/”这句如果按字面严格执行，当前 CLI 和文档仍未完全对齐。

### F006. 本轮重构几乎没有成体系的自动化回归测试

这是一个明显的实施风险。

当前 `autoBMAD/docuswarm/tests` 目录下可见的 source test 主要是：

- `tests/unit/test_checkpointer_refactor.py`
- `tests/unit/test_message_extraction.py`
- 若干 CLI 目录骨架

未发现与以下主题直接对应的 source test 文件：

- `NodeExecutionContext`
- `NodePromptContractBuilder`
- single truth deliverable
- `update_context` persistence
- docs-free workflow

这与研究/计划文档中明确提出的测试建议不一致：

- `docs/research/2026-03-13-p0-node-prompt-injection-plan.md:151-157`
- `docs/research/2026-03-13-p0-single-truth-deliverable-plan.md:151-156`
- `docs/research/2026-03-13-p1-update-context-persistence-plan.md:117-122`

结论：

- 当前实现强依赖人工审查与局部验证。
- 在继续推进 P0-3 / P1-1 前，没有测试护栏会显著提高回归风险。

## 5. 已完成项

虽然总体结论是“未完成”，但以下部分已经明显落地，值得单独确认：

### 5.1 节点契约注入已经进入主路径

- `executor -> execute_with_context -> execute_with_input -> contract_builder` 这条链是真实存在且被主执行流调用的。
- 根目录 `nodes/*/node.yaml` 已经拥有 `task` / `deliverable` 子结构，Independent prompt 能稳定拿到任务名、描述、角色补充、必选章节、标题模板和输出文件名。

### 5.2 文件层 metadata-first 已开始落地

- `create_deliverable` 已不再把正文直接作为返回值的一部分，而是写盘后返回文件 metadata。
- Evaluator 也已经具备“优先读文件正文”的实现。

### 5.3 docs 扩展议题已基本退出主链

- `docs_context` 目前只是占位字段。
- 没有看到继续推进 `ContextResolver`/docs 注入策略的真实实现痕迹。

## 6. 与 Overview 的偏差说明

本次评估还发现一个值得记录的实现偏差：

总览文档第 1 节强调“不先做全量 `node.yaml` 格式迁移”，但当前根目录 `nodes/*/node.yaml` 实际已经普遍采用了带 `task` / `deliverable` 子结构的新形态。

这件事的影响有两面：

- 正面：`P0-2` prompt 注入因此推进得更快、更直接。
- 风险：代码实现已经部分脱离 overview 当时假设的“旧 schema 兼容优先”路径，后续需要补一份文档同步，否则研究结论和仓库现实会继续漂移。

## 7. 建议的下一步顺序

结合总览文档的依赖顺序，以及当前实现现状，建议继续按下面顺序收口：

1. 先完成 `P1-1` 真闭环。
   - 为 `UpdateContextTool` 提供真实的 `StateManager` / `pipeline_id` 绑定机制。
   - 把 `shared_context` 带入 `IndependentAgentInput`。
   - 在 prompt builder 中显式渲染 `shared_context`。
   - 在 resume/restart 路径恢复 `shared_context`。

2. 再收口 `P0-3` 单一交付物真相。
   - 统一使用 `summary`，去掉 `deliverable.content` 的双重语义。
   - 将 `file_path` / `sha256` 提升为强制字段。
   - 禁止 Evaluator 退回到摘要作为正式评审正文。
   - 限制下游链式上下文只传播 metadata + summary。

3. 然后补完 `P0-2` 的 Evaluator 上下文。
   - 在 `EvaluatorAgentInput` 中加入原始上下文摘要。
   - 让 Evaluator prompt 稳定出现“原始需求摘要”章节。

4. 最后清理 `P0-1` 与 docs-free 的尾巴。
   - 视需要把状态层进一步收敛到 `execution_context` 主协议。
   - 清理 README / CLI 中仍鼓励以 `docs/*.md` 作为标准入口的表述。

5. 补测试。
   - 至少补上 prompt contract、single truth、update_context persistence、shared_context cross-node、docs-free boundary 的单元/集成测试。

## 8. 最终结论

`autoBMAD/docuswarm` 当前对 `2026-03-13` 重构总览的落实情况，可以概括为：

- **P0-1、P0-2 已经进入可运行阶段**
- **P0-3 只完成了一半**
- **P1-1 仍停留在“接口存在但运行闭环未成立”**
- **P1-2 已基本从主链退出，但产品边界尚未完全收口**

因此，这份实现不能被判定为“已完成总览重构”，但也不是“停留在设计稿”。更准确的判断是：

**主链骨架已经成形，真正阻塞验收的是 `shared_context` 闭环和 deliverable 单一真相这两处。**

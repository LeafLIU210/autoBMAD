# DocuSwarm calc-one-plus-one 日志驱动根因审查报告

日期: 2026-05-01  
审查对象: `autoBMAD/docuswarm`  
触发命令: `source .venv/bin/activate && python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md`  
主要日志: `logs/docuswarm-2026-05-01.log`  
Pipeline ID: `pipeline-1777568337821-ac4426e4`  
方法: `systematic-debugging` 四阶段取证，不先提修复，先定位根因。

## 执行摘要

这次 pipeline 失败不是单一的“LLM idle timeout”。日志显示 IndependentAgent 在收到 `ResultMessage` 后又空等 359.2 秒并报 `Transport idle`，但随后仍从 partial messages 中解析出 analyst 交付物，并进入 evaluator。真正让 pipeline 最终失败的是 evaluator 将 analyst 交付物判为 `BLOCKED`，alignment score 为 `0.315`，原因是 analyst 输出严重跑偏: 它把“极小 1+1 CLI 的 DocuSwarm 端到端流水线验证任务”写成了“开发者工具市场研究报告”。

根因是两条链路叠加:

1. P0: Analyst 节点契约漂移。`autoBMAD/nodes/analyst` 的 persona、task、required sections、template fallback、evaluator criteria 仍然围绕数据/市场分析，而输入上下文要求的是业务需求分析和流水线验证。系统把正确上下文传进来了，但节点契约把模型拉向错误文档类型。
2. P0: `ClaudeSessionWrapper.prompt()` 没有把 SDK 的 `ResultMessage` 当作本轮完成信号，导致一次已经结束的 agent 调用被 idle watchdog 延迟约 6 分钟并包装成 `LLMError`。IndependentAgent 又在捕获异常后返回 partial messages，因此该错误被降级为噪声，但它会污染日志、拖慢 pipeline、关闭 session，并掩盖真实失败点。

结论: 需要先修节点契约和 transport 完成语义，再谈提升 evaluator 或 retry 策略。单纯增加 timeout、放宽 evaluator 阈值、或让 BLOCKED 强行继续，都会遮住根因。

## Phase 1: 根因取证

### 现象时间线

关键日志链路:

- `00:58:46`: context validation 通过。上下文目标、约束、输出格式和五阶段 pipeline 成功标准都被 LLM 识别为清晰。
- `00:58:57-00:59:22`: SummaryAgent 成功总结 `calc-context.md`，明确指出这是最小化 DocuSwarm E2E 验证任务，并列出五个节点产物要求。
- `00:59:22`: analyst 节点开始，使用 cached docs summary。
- `00:59:23-01:00:56`: IndependentAgent 收到 10 条 SDK 消息，最后一条是 `ResultMessage`。
- `01:07:02`: `ClaudeSessionWrapper` 报 `prompt_idle_exceeded`, `idle_seconds=359.2`, `messages_received=10`。
- `01:07:02`: IndependentAgent 记录 `llm_call_error`，但随后又记录 `independent_agent_completed`，说明异常没有使 agent 失败。
- `01:07:45`: Evaluator 给出 `alignment_score=0.315`，判定为 `BLOCKED`。
- `01:07:46`: pipeline failed，failed node 为 `analyst`。

### 关键证据

1. 输入上下文本身没有缺失。日志中的 context validation 结果为 valid，SummaryAgent 也准确总结了项目本质: 这是一个用于验证 DocuSwarm 文档流水线的最小 Python CLI 任务。
2. IndependentAgent 的输出文件确实跑偏。`output/pipeline-1777568337821-ac4426e4/analyst-report.md` 标题是 `Minimal Python CLI Environment Validation Tool`，正文包含 `Market Overview`、`Target Segments`、`Competitive Landscape`、`Market Opportunities` 等市场研究章节。
3. Evaluator 的阻断理由与输出文件一致: scope misalignment、missing core deliverable、lack of evidence、over-engineered recommendations、absence of pipeline validation focus。
4. Transport idle 是真实问题，但不是最终阻断点。日志显示 `ResultMessage` 已在 `01:00:56` 收到；`01:07:02` 才 idle 报错；随后 evaluator 仍被调用并完成评分。

## Phase 2: 模式分析

### 工作正常的链路

`SessionManager.single_prompt()` 对 one-shot 调用会识别 `ResultMessage`，记录 `single_prompt_result`，然后正常完成。context validation、SummaryAgent、Evaluator 都走这条路径，日志中均正常返回。

### 异常链路

IndependentAgent 使用 `SessionManager.create_session()` 创建 `ClaudeSessionWrapper`，再调用 `session.prompt()` 流式接收消息。该 wrapper 的循环只在 `StopAsyncIteration`、整体 timeout 或 idle timeout 时退出，没有在 `ResultMessage` 到达时结束本轮。于是已经完成的 SDK turn 会继续等待下一条消息，直到 idle watchdog 触发。

这解释了为什么:

- `ResultMessage` 已出现，但 `prompt_idle_exceeded` 仍发生。
- `llm_call_error` 之后仍有 `independent_agent_completed`。
- pipeline 没有因 LLMError 直接进入 failed，而是进入 evaluator 后被 BLOCKED。

### 节点契约漂移模式

Analyst 节点配置整体偏向错误方向:

- `autoBMAD/nodes/analyst/node.yaml` 将节点描述为 `Data Analyst & Business Intelligence Specialist`，required sections 是 `data_sources`、`analysis_methodology`、`findings`、`recommendations`、`limitations`。
- `autoBMAD/nodes/analyst/persona.json` 角色是统计分析、BI、趋势识别、数据质量评估。
- `autoBMAD/docuswarm/templates/analyst_templates.yaml` 第一个模板是 `market_research`，包含 `Market Overview`、`Target Segments`、`Competitive Landscape`、`Market Opportunities`。
- `contract_builder._find_best_template_match()` 在找不到精确模板时返回第一个模板，导致 `analyst-report` 容易落入 `market_research`。
- `autoBMAD/nodes/analyst/evaluator.yaml` 最高权重为 `evidence_quality=0.40`、`actionability=0.30`，更像数据/研究质量门，而不是“需求背景分析/流水线验证需求追踪”的质量门。

这不是模型偶发幻觉，而是系统提示契约和节点资产共同把模型推向市场研究。

## Phase 3: 单一假设与验证

假设 A: pipeline 失败的直接根因是 transport idle。

验证结果: 不成立。idle 发生后 IndependentAgent 返回 partial messages，解析出 deliverable，并进入 evaluator。最终 CLI 输出的失败原因是 `Node analyst finished with status blocked`，不是 `LLM call failed`。

假设 B: pipeline 失败的直接根因是 analyst 交付物与任务目标错位，导致 evaluator 判 BLOCKED。

验证结果: 成立。evaluator 输出逐条指出该报告把最小 pipeline 验证任务写成商业开发者工具市场机会分析；pipeline final state 中 failed node 为 analyst，error message 是 `Node analyst finished with status blocked`。

假设 C: analyst 跑偏的根因是原始上下文没有传入 IndependentAgent。

验证结果: 不成立。日志显示 `using_cached_docs_summary count=1`，SummaryAgent 正确总结了上下文；`ContextManager` 会把 original context summary 和 docs context 传入 IndependentAgent。更吻合证据的是节点契约漂移。

## Phase 4: 修复方向与验证建议

### P0-1: 修正 Analyst 节点契约

目标不是“让 evaluator 放行当前报告”，而是让 analyst 生成正确类型的报告。

建议:

- 将 analyst task 从 Data Analyst/BI 改为“业务需求分析与上下文澄清”，聚焦目标、范围、功能需求、非功能约束、验收标准、下游节点输入。
- 将 required sections 改为适配 DocuSwarm 第一阶段: `objective_and_scope`、`stakeholders_or_users`、`functional_requirements`、`non_functional_constraints`、`acceptance_criteria`、`pipeline_validation_risks`、`downstream_guidance`。
- 增加 analyst 专用需求分析模板，避免 `analyst-report` fallback 到 `market_research`。
- 将 evaluator criteria 改为 requirement alignment、traceability、scope control、downstream usefulness、clarity。

最小验证:

- 构造无 LLM 单测或 prompt contract snapshot，断言 analyst system/user prompt 不包含 `Market Overview`、`Competitive Landscape`、`Target Segments`，且包含 `Functional Requirements`、`Acceptance Criteria`、`Pipeline Validation`。
- 使用 mock LLM 或 fixture 输出一个需求分析报告，断言 evaluator 对 calc-context 的合格报告 `APPROVED`，对当前 market research fixture `BLOCKED`。

### P0-2: 修正 `ClaudeSessionWrapper.prompt()` 完成语义

建议:

- 在 `ClaudeSessionWrapper.prompt()` 接收循环中，yield `ResultMessage` 后立即结束本轮，或在转换层记录 result 并 break。
- 保留 idle watchdog 作为“没有终止消息”的防护，而不是正常完成后的退出机制。
- 与 `single_prompt()` 的 ResultMessage 处理保持一致，避免 one-shot 和 session mode 行为分叉。

最小验证:

- 用 fake SDK client 模拟 `AssistantMessage -> UserMessage(tool_result) -> ResultMessage`，断言 `prompt()` 在收到 ResultMessage 后结束，不等待 `IDLE_TIMEOUT`。
- 断言没有记录 `prompt_idle_exceeded`，且不会关闭健康 session。
- 用一个没有 ResultMessage 的 fake stream 验证 idle watchdog 仍会触发。

### P1-1: BLOCKED 与 NEEDS_REVISION 的策略需要明确

当前 `execute_with_context()` 在 evaluator 返回 `BLOCKED` 时立刻 break，不进入下一轮修订。对于 alignment score `0.315` 的报告，这可能是合理的；但日志中 `max_iterations=3` 会让人误以为会修订三轮，而实际只有一轮。

建议:

- 文档化 `BLOCKED` 是终止状态，`NEEDS_REVISION` 才进入迭代。
- 或者把“低于阈值但可根据 evaluator 建议重写”的情况从 `BLOCKED` 改为 `NEEDS_REVISION`，只在缺失上下文、工具失败、违反安全/格式约束时 BLOCKED。
- 修正最终 `node_iterations` 统计。日志 final state 中 `node_iterations: {'analyst': 3}` 与实际 `iteration_start iteration=1` 不一致，容易误导排障。

### P1-2: project_root / cwd / agent_file 语义仍有漂移

日志中 IndependentAgent session 的 `cwd=/home/leafliu`，`agent_file=/home/leafliu/autoBMAD/docuswarm/agents/configs/independent_agent.yaml`。实际仓库中的路径是 `autoBMAD/docuswarm/agents/configs/...`，少了一层 `autoBMAD/` 包目录。当前代码会跳过 agent_file 作为 tools 来源，所以它不是本次阻断根因，但它说明 repo root、package root、SDK cwd、output_dir 的边界仍不干净。

建议:

- 明确四个路径概念: repo root、package root、SDK cwd、pipeline output dir。
- 给 `create_dual_agent_node(project_root=...)` 和 `IndependentAgent._build_agent_file_path()` 加路径 snapshot 测试。
- 日志里输出 `repo_root`、`package_root`、`sdk_cwd`、`output_dir` 四个字段，避免只靠 `cwd` 猜测。

## 推荐修复顺序

1. 先写两个失败测试: `ResultMessage ends prompt stream` 与 `analyst prompt contract is requirements-analysis, not market-research`。
2. 修 `ClaudeSessionWrapper.prompt()` 的 ResultMessage 终止语义，消除 359 秒空等和误导性 `LLMError`。
3. 修 analyst node.yaml/persona/template/evaluator，使 calc-context 生成需求背景分析，而不是市场研究。
4. 修 iteration 统计和 BLOCKED/NEEDS_REVISION 策略文档，保证日志状态与实际执行一致。
5. 再跑同一命令，期望 analyst 通过或进入可解释的 NEEDS_REVISION，而不是直接输出 market research 并 BLOCKED。

## 风险评级

- P0: 节点契约漂移导致 DocuSwarm 第一节点在最小任务上失败。影响所有依赖 analyst 产物的完整流水线。
- P0: ResultMessage 完成语义错误导致每次 agent-mode 成功调用都可能多等 idle timeout，显著拖慢并污染错误信号。
- P1: BLOCKED 终止语义和 node_iterations 统计不一致，降低可观察性。
- P1: 路径语义漂移尚未触发本次阻断，但会继续制造平台/环境相关故障。

## 附录: 关键代码指针

- `autoBMAD/docuswarm/llm/session_manager.py`: `ClaudeSessionWrapper.prompt()` 的循环等待和 idle watchdog。
- `autoBMAD/docuswarm/agents/independent.py`: `_call_llm_with_prompts()` 捕获异常后在已有 messages 时返回 partial messages。
- `autoBMAD/nodes/analyst/node.yaml`: analyst task 与 required sections 当前仍为 Data Analyst/BI 风格。
- `autoBMAD/nodes/analyst/persona.json`: persona 为统计/BI/数据质量方向。
- `autoBMAD/docuswarm/templates/analyst_templates.yaml`: 默认 analyst 模板为 market research。
- `autoBMAD/docuswarm/prompts/contract_builder.py`: template fallback 返回第一个模板，以及 Independent prompt 的 system/user 渲染。
- `autoBMAD/docuswarm/nodes/dual_agent.py`: `BLOCKED` 在 `execute_with_context()` 中为终止状态。
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` 与 `autoBMAD/docuswarm/pipeline/graph.py`: iteration 统计与 pipeline state 回写。

## 最终判断

本次失败的直接原因是 analyst 输出被 evaluator 判定为 `BLOCKED`；更深层根因是 analyst 节点资产与当前 DocuSwarm 文档流水线角色不匹配。`prompt_idle_exceeded` 是并发暴露出的 transport 完成语义 bug，它不是最终失败原因，但必须优先修，因为它会制造长时间假挂起、误导日志和 session 清理副作用。两者都修完后，再用同一 `calc-context.md` 做端到端回归，才算真正处理了这次故障。

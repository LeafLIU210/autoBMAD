# 2026-04-29 DocuSwarm SummaryAgent JSON 解析失败深度评估报告

审查对象: `autoBMAD/docuswarm`  
触发日志: `logs/docuswarm-2026-04-29.log`  
输出目录: `output/pipeline-1777439345215-46a35fb3`  
报告目录: `docs-doc/evaluation`  
审查方法: `systematic-debugging` 根因追踪 + 代码审查视角  
审查时间: 2026-04-29 CST

## 结论摘要

本次失败的直接原因不是输入文档不可读、不是 API 凭证无效、不是模型没有返回内容，也不是 SummaryAgent 找不到 `docs/calc-one-plus-one/calc-context.md`。根因是:

**SummaryAgent 要求 LLM 返回 JSON，但实际模型返回了 markdown fenced JSON；`SummaryAgent._call_llm_for_summary()` 使用 `json.loads(summary_text)` 直接解析整段文本，未使用项目已有的 `extract_json()`，也未启用 SDK `output_format` 结构化输出。**

日志中模型返回的 JSON 内容本身是完整且符合 SummaryAgent 需要的字段的；失败只发生在第一字符是反引号而不是 `{`。这使 SummaryAgent 把一个可恢复、常见、已有通用解析器支持的响应格式误判为 `LLMSummaryError`。

当前 pipeline 影响:

- `context` LLM 校验已通过。
- pipeline work dir 已创建。
- SummaryAgent 找到了 `docs/calc-one-plus-one/calc-context.md` 并成功调用 LLM。
- SummaryAgent 在解析阶段失败，`docs_context_summary` 未写入。
- 用户中断后，DB 中该 pipeline 仍停在 `running / analyst`，没有任何 node result 或交付物文件。

风险判断:

- 严重性: High。它阻断了当前命令继续执行，且会在任意返回 fenced JSON 的模型/代理上复现。
- 修复复杂度: Low。已有 `autoBMAD.docuswarm.llm.response.extract_json()` 支持直接 JSON、markdown code block、嵌入式 JSON。
- 回归测试缺口: High。现有 `tests/test_docuswarm_p1_summary_agent.py` 只覆盖 `context_file` 提取，没有覆盖 SummaryAgent 的 LLM 响应解析。

## Systematic Debugging 过程

### Phase 1: Root Cause Investigation

#### 1. 读取错误信息

用户终端错误:

```text
llm_call_failed agent=SummaryAgent attempt=1
error=Invalid JSON response: Expecting value: line 1 column 1 (char 0)
error_type=LLMSummaryError
filename=docs/calc-one-plus-one/calc-context.md
```

日志关键事实:

- `logs/docuswarm-2026-04-29.log:11`: 上下文验证 LLM 返回 `{"valid": true, ...}`。
- `logs/docuswarm-2026-04-29.log:23`: 创建 `output/pipeline-1777439345215-46a35fb3`。
- `logs/docuswarm-2026-04-29.log:27`: SummaryAgent 开始总结 1 个文件。
- `logs/docuswarm-2026-04-29.log:33`: 正在处理 `docs/calc-one-plus-one/calc-context.md`，大小 1796 bytes。
- `logs/docuswarm-2026-04-29.log:41` 到 `:80`: LLM 返回 fenced JSON。
- `logs/docuswarm-2026-04-29.log:84`: SummaryAgent 报 `Invalid JSON response: Expecting value: line 1 column 1 (char 0)`。

关键判断:

`line 1 column 1 char 0` 对应 JSON parser 在第一个字符失败。日志中的第一个字符是 markdown code fence 的反引号，而不是 JSON object 的 `{`。

#### 2. 复现一致性

使用无网络最小复现，模拟日志中的 LLM 响应形态:

```text
.venv/bin/python -c 'import json; s="```json\n{\"summary\":\"ok\",\"key_points\":[\"a\"],\"structure\":{\"sections\":[],\"concepts\":[]}}\n```"; json.loads(s)'
```

结果:

```text
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

用假的 `session_manager` 调 `SummaryAgent._call_llm_for_summary()`，返回同样的 fenced JSON:

```text
llm_call_failed agent=SummaryAgent error=Invalid JSON response: Expecting value: line 1 column 1 (char 0)
llm_retries_exhausted agent=SummaryAgent
None
```

同一文本交给项目已有通用解析器:

```text
from autoBMAD.docuswarm.llm.response import extract_json
extract_json(fenced_json)["summary"] == "ok"
```

结果: 成功。

这把问题分离得很干净:

- 模型摘要内容可用。
- fenced JSON 是触发条件。
- `json.loads()` 直接解析是失败点。
- `extract_json()` 已有能力处理该格式。

#### 3. 检查输出与持久化状态

`output/pipeline-1777439345215-46a35fb3` 为空，没有交付物文件。

DB 中该 pipeline 当前状态:

```text
status: running
current_node: analyst
completed_nodes: []
failed_nodes: []
deliverables: {}
docs_context_summary: []
error: None
node_results: []
node_runs_count: 0
```

含义:

SummaryAgent 失败发生在 graph 节点执行之前。系统还没有进入 analyst/pm/ux/architect/po 五节点阶段。

#### 4. 调用链追踪

入口链路:

1. `autoBMAD/docuswarm/cli/commands/start.py:29` 调用 `PipelineService.start()`。
2. `autoBMAD/docuswarm/cli/services/pipeline_service.py:54` 到 `:58` 构造 `subject_context`，包含 `subject`、`context_file`、`content`。
3. `autoBMAD/docuswarm/pipeline/orchestrator.py:420` 到 `:421` 先做 LLM context validation。
4. `autoBMAD/docuswarm/pipeline/orchestrator.py:451` 到 `:457` 在 graph 执行前调用 `_summarize_referenced_documents()`。
5. `autoBMAD/docuswarm/pipeline/orchestrator.py:299` 到 `:307` 实例化 `SummaryAgent` 并调用 `summarize_context()`。
6. `autoBMAD/docuswarm/agents/summary.py:272` 到 `:275` 从 `subject_context.context_file` 提取 `docs/calc-one-plus-one/calc-context.md`。
7. `autoBMAD/docuswarm/agents/summary.py:452` 到 `:458` 调 `session_manager.single_prompt()`。
8. `autoBMAD/docuswarm/agents/summary.py:463` 到 `:471` 提取文本并直接 `json.loads(summary_text)`。
9. `json.loads()` 遇到 opening fence 失败，包装为 `LLMSummaryError`。

错误源头不是 `_extract_text_from_response()`。它正确取到了 assistant text。坏值的来源是“可解析 JSON 被包在 markdown fence 内”，真正的失败边界是 SummaryAgent 的 JSON 解析策略。

### Phase 2: Pattern Analysis

#### 工作范式 1: `llm/response.py` 已提供通用 JSON 提取

`autoBMAD/docuswarm/llm/response.py:51` 到 `:103` 的 `extract_json()` 支持:

- 直接 JSON。
- markdown code block。
- 嵌入式 JSON。

`autoBMAD/docuswarm/llm/response.py:106` 到 `:137` 的 `extract_json_from_markdown()` 明确匹配:

```text
```json
{...}
```
```

这与日志中的响应形态完全一致。

#### 工作范式 2: EvaluatorAgent 已使用 structured output + fallback parser

`autoBMAD/docuswarm/agents/evaluator.py:387` 到 `:393` 调用 `single_prompt(... output_format=EVALUATOR_OUTPUT_SCHEMA)`。

`autoBMAD/docuswarm/agents/evaluator.py:475` 到 `:483` 优先消费 SDK structured output。

`autoBMAD/docuswarm/agents/evaluator.py:498` 到 `:503` fallback 到 `extract_json(content_str)`。

EvaluatorAgent 的设计比 SummaryAgent 更稳健: 先要求结构化输出，失败时用容错 JSON 提取。

#### 工作范式 3: IndependentAgent 已使用 `extract_json()`

`autoBMAD/docuswarm/agents/independent.py:708` 到 `:710` 使用 `extract_json(content)`，并在非 JSON 文本时有额外 fallback。

#### 工作范式 4: ContextValidator 也知道要清理 markdown code block

`autoBMAD/docuswarm/context/validator.py:1601` 到 `:1627` 的 LLM validation parser 会先提取文本，再清理 markdown code block，再 `json.loads()`。

结论:

SummaryAgent 是同一代码库中解析策略最脆弱的离群点。它拥有最严格的 prompt 文案，却没有使用同项目已有的解析防线或 SDK structured output。

### Phase 3: Hypothesis and Testing

假设:

SummaryAgent 失败的根因是“直接 `json.loads()` 不支持 fenced JSON”，而不是 LLM 结果无效。

验证:

- `json.loads(fenced_json)` 复现同样 `Expecting value: line 1 column 1`。
- `SummaryAgent._call_llm_for_summary()` + FakeSession 复现同样 `LLMSummaryError`。
- `extract_json(fenced_json)` 成功。
- 日志中的 fenced JSON 包含 SummaryAgent 需要的 `summary`、`key_points`、`structure` 三个字段。

假设成立。

### Phase 4: Implementation Guidance

本次用户要求是“创建评估报告”，本报告不直接修改业务代码。但若进入修复，应先写失败测试，再做单点修复。

最小失败测试应覆盖:

1. SummaryAgent 接收直接 JSON，成功。
2. SummaryAgent 接收 ```json fenced JSON，成功。
3. SummaryAgent 接收 narrative + embedded JSON，若采用 `extract_json()`，成功或按策略明确失败。
4. SummaryAgent 接收 malformed JSON，仍失败并记录可诊断错误。
5. SummaryAgent 接收 SDK structured output，若启用 `output_format`，优先使用 structured data。

## 关键问题清单

### P0-1: SummaryAgent 直接 `json.loads()`，无法解析常见 fenced JSON

严重性: High  
文件: `autoBMAD/docuswarm/agents/summary.py:467` 到 `:471`

当前逻辑:

```python
try:
    data = json.loads(summary_text)
except json.JSONDecodeError as e:
    raise LLMSummaryError(f"Invalid JSON response: {e}") from e
```

问题:

LLM 已返回有效 JSON object，但被包在 markdown code fence 里。直接 `json.loads()` 会在第一个反引号处失败。

影响:

- SummaryAgent 对真实 LLM 输出过度脆弱。
- 一次可恢复解析错误会触发重试，浪费 LLM 调用。
- 多次失败后返回 `None`，导致 `docs_context_summary` 为空。
- 在当前命令中，用户中断后 pipeline 停在 `running / analyst` 且没有交付物。

建议:

优先把 SummaryAgent 的解析改为:

```python
from autoBMAD.docuswarm.llm.response import ResponseParseError, extract_json

try:
    data = extract_json(summary_text)
except ResponseParseError as e:
    raise LLMSummaryError(f"Invalid JSON response: {e}") from e
```

这属于低风险修复，因为同项目 EvaluatorAgent 和 IndependentAgent 已经采用 `extract_json()`。

### P0-2: SummaryAgent 没有启用 SDK `output_format`

严重性: High  
文件: `autoBMAD/docuswarm/agents/summary.py:452` 到 `:458`  
对照: `autoBMAD/docuswarm/llm/session_manager.py:464` 到 `:469`

SessionManager 已支持:

```python
output_format={
    "type": "json_schema",
    "schema": output_format,
}
```

EvaluatorAgent 已使用该能力，但 SummaryAgent 仍只靠 prompt 文案约束。

问题:

- prompt 写了“ONLY valid JSON”，但没有结构化输出约束。
- 日志证明模型仍会返回 fenced JSON。
- `has_output_format=False` 出现在 SummaryAgent 的 `single_prompt_start` 日志中。

建议:

为 SummaryAgent 定义真正 JSON Schema，而不是当前示例型 `SUMMARY_SCHEMA`。

当前 `SUMMARY_SCHEMA` 是示例对象:

```python
{
    "summary": "2-5 sentence core summary of the document",
    "key_points": ["3-7 key points extracted from the document"],
    "structure": {
        "sections": ["list of main sections"],
        "concepts": ["key concepts mentioned"],
    },
}
```

这适合作为 prompt 示例，不适合作为 SDK JSON schema。应新增类似:

```python
SUMMARY_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "key_points", "structure"],
    "properties": {
        "summary": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
        "structure": {
            "type": "object",
            "additionalProperties": False,
            "required": ["sections", "concepts"],
            "properties": {
                "sections": {"type": "array", "items": {"type": "string"}},
                "concepts": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}
```

然后调用:

```python
self.session_manager.single_prompt(
    prompt=user_prompt,
    mode=llm_config.mode,
    yolo=True,
    system_prompt=system_prompt,
    output_format=SUMMARY_OUTPUT_SCHEMA,
)
```

并在解析处优先接受 `{"type": "structured", "data": ...}`。

### P0-3: SummaryAgent 响应解析没有复用统一消息提取工具

严重性: Medium  
文件: `autoBMAD/docuswarm/agents/summary.py:518` 到 `:535`

SummaryAgent 自己实现 `_extract_text_from_response()`，只处理:

- dict message 的 `content` list。
- content block type 为 `text`。
- content 为字符串。

但 `autoBMAD/docuswarm/llm/response.py:149` 到 `:345` 已有 `extract_text_from_messages()`，处理 SDK message object、dict、TextBlock、content list 等多种形态，并有调试日志。

影响:

当前日志里 `_extract_text_from_response()` 碰巧能取到文本，但后续 SDK 返回形态变化时，SummaryAgent 会再次成为解析离群点。

建议:

统一使用 `extract_text_from_messages()`，或者至少让 SummaryAgent 支持 structured output message:

```python
for msg in response:
    if msg.get("type") == "structured":
        return msg["data"]
```

### P1-1: SummaryAgent schema validation 太浅

严重性: Medium  
文件: `autoBMAD/docuswarm/agents/summary.py:378` 到 `:400`

当前验证只检查:

- `summary` 存在且为 str。
- `key_points` 存在且为 list。
- `structure` 存在且为 dict。

未检查:

- `key_points` 元素是否为 str。
- `structure.sections` 是否存在。
- `structure.concepts` 是否存在。
- `sections/concepts` 元素类型。
- 是否允许额外字段。
- 空列表是否可接受。

影响:

即使修复 fenced JSON 解析，SummaryAgent 仍可能接受结构不完整的数据，污染 `docs_context_summary`。后续节点依赖该上下文时，错误会变成更难定位的 Agent 输出质量问题。

建议:

用 JSON Schema validator，或在 `_validate_summary_schema()` 中完整校验 nested fields。配置文件 `autoBMAD/docuswarm/config/summary_agent.yaml:90` 到 `:97` 已列出 required fields 和 structure fields，可以成为验证规则来源。

### P1-2: SummaryAgent 重试策略会把确定性解析错误当作 LLM 调用错误重试

严重性: Medium  
文件: `autoBMAD/docuswarm/agents/summary.py:443` 到 `:516`

当前所有异常都进入同一 `except Exception` 分支:

```python
self.logger.warning("llm_call_failed", ...)
...
await asyncio.sleep(backoff)
```

问题:

对于 fenced JSON 这种确定性解析错误，重试同一个 prompt 很可能再次返回同形 fenced JSON。它消耗时间和 API 调用，但不增加成功概率。

建议:

分类处理:

- transport/API/timeout: 可重试。
- JSON extraction 失败: 可做一次 repair prompt 或 fallback parser。
- schema validation 失败: 可用 corrective prompt，明确缺字段。
- empty response: 可重试。

至少应把日志名从 `llm_call_failed` 拆成 `llm_call_failed` 与 `llm_response_parse_failed`，避免误导排查。

### P1-3: 用户中断后 pipeline 状态没有标记 cancelled/failed

严重性: Medium  
文件: `autoBMAD/docuswarm/cli/services/pipeline_service.py:75` 到 `:78`  
状态证据: DB 中 pipeline 仍为 `running / analyst`

日志 `logs/docuswarm-2026-04-29.log:86` 到 `:88` 显示用户中断后只关闭了 session，没有更新 pipeline 状态。当前 `PipelineService.start()` 的 `finally` 只调用 `session_manager.close_all()`。

影响:

- `docuswarm status/list` 会看到悬挂 running pipeline。
- 后续 resume/cancel 语义会混乱。
- 用户无法从状态判断这是被中断，而不是仍在执行。

建议:

在 CLI start 层捕获 `KeyboardInterrupt`/`asyncio.CancelledError` 时:

- 若 pipeline_id 已创建，写入 `status=cancelled` 或 `failed`，并记录 `error_type=KeyboardInterrupt`。
- 保留 `last_event=interrupted_by_user`。
- 确保 session close 和 state update 都执行。

### P1-4: SummaryAgent 配置声明了 caching，但实现没有使用缓存

严重性: Low to Medium  
文件: `autoBMAD/docuswarm/config/summary_agent.yaml:55` 到 `:66`

配置:

```yaml
caching:
  enable: true
  ttl_hours: 24
  invalidate_on_doc_change: true
  backend: "memory"
```

当前 `SummaryAgent` 每次 pipeline start 都重新调用 LLM，没有看到缓存 key、读取、写入或失效逻辑。

影响:

- 同一 context 文件反复运行会重复消耗 LLM。
- 解析类失败无法通过已知好缓存短路。
- “cached summary” 的架构意图与运行时行为不一致。

建议:

如果近期不实现缓存，应把配置注释标为 planned。若要实现，应以 `path + mtime + sha256 + schema_version` 作为缓存 key，避免文档变更后复用旧摘要。

### P2-1: SummaryAgent 测试覆盖不足

严重性: Medium  
文件: `tests/test_docuswarm_p1_summary_agent.py`

当前测试只覆盖:

- `context_file` 被 `_extract_referenced_files()` 提取。
- SummaryAgent 和 ContextBuilder 都存在解析方法。

执行结果:

```text
.venv/bin/python -m pytest tests/test_docuswarm_p1_summary_agent.py --no-cov -q
.. [100%]
```

缺失测试:

- `_call_llm_for_summary()` 解析 fenced JSON。
- `_call_llm_for_summary()` 解析 direct JSON。
- `_extract_text_from_response()` 对 structured output 的处理。
- `_validate_summary_schema()` 对 nested schema 的校验。
- SummaryAgent 失败后 orchestrator 是否 fail-open 并继续，或是否正确记录 degraded 状态。

Ruff 还显示该测试文件有两个 unused imports:

```text
tests/test_docuswarm_p1_summary_agent.py:9 F401 typing.Any imported but unused
tests/test_docuswarm_p1_summary_agent.py:12 F401 pytest imported but unused
```

这不是本次故障根因，但说明该测试文件较薄，没有经历足够严格的质量门。

### P2-2: NodeExecutionContextBuilder fallback 仍不读取 `context_file`

严重性: Low to Medium  
文件: `autoBMAD/docuswarm/node_execution/context_builder.py:90` 到 `:172`

SummaryAgent 已在 `autoBMAD/docuswarm/agents/summary.py:272` 到 `:275` 支持从 `subject_context.context_file` 提取文件。但 `NodeExecutionContextBuilder._resolve_reference_docs()` 只扫描 `content` 中出现的文件名，不读取 explicit `context_file`。

影响:

当 SummaryAgent 失败或被关闭时，fallback docs_context 可能再次变空。当前 calc context 的正文没有反向引用自身文件名，因此 fallback 无法恢复。

建议:

抽出统一的 referenced-file resolver，供 SummaryAgent 和 ContextBuilder 共用，确保 `context_file`、backtick 引用、bare filename、相对路径解析行为一致。

## 输出目录与 DB 状态评估

`output/pipeline-1777439345215-46a35fb3` 当前为空。这与日志吻合: pipeline 在 SummaryAgent 阶段被中断，尚未进入任何节点执行，所以没有生成:

- `analyst` 交付物。
- `pm` 交付物。
- `ux` 交付物。
- `architect` 交付物。
- `po` backlog。

DB 中 `docs_context_summary` 为空，`node_results` 为空，`node_runs_count` 为 0。这说明不是“节点生成失败后文件丢失”，而是“graph 前置摘要阶段阻塞/中断”。

需要注意: `status=running` 会让这个 pipeline 在用户视角上像仍在执行。实际已经因用户中断停止。建议后续清理或状态修复时不要把它当成仍活跃任务。

## 推荐修复路线

### Fix 1: SummaryAgent 使用 `extract_json()`

优先级: P0  
风险: Low  
预期收益: 立即修复当前 fenced JSON 失败

修改点:

- `autoBMAD/docuswarm/agents/summary.py`
- 引入 `extract_json` 和 `ResponseParseError`
- 替换 `json.loads(summary_text)`

测试:

- fake session 返回 direct JSON -> success。
- fake session 返回 fenced JSON -> success。
- fake session 返回 malformed JSON -> returns None after configured retries or raises internal error then exhausted。

### Fix 2: 为 SummaryAgent 启用 SDK `output_format`

优先级: P0/P1  
风险: Medium  
预期收益: 从源头减少 markdown fence、缺字段和 schema drift

修改点:

- 新增真正 JSON Schema `SUMMARY_OUTPUT_SCHEMA`。
- `single_prompt(... output_format=SUMMARY_OUTPUT_SCHEMA)`。
- `_call_llm_for_summary()` 先识别 structured message。
- fallback 仍保留 `extract_json()`，兼容 SDK/模型差异。

测试:

- fake session 返回 `[{"type": "structured", "data": {...}}]` -> success。
- structured output 缺字段 -> validation fail。
- SDK structured retries exhausted -> 错误信息保留。

### Fix 3: 完整 schema 校验

优先级: P1  
风险: Low to Medium

修改点:

- `_validate_summary_schema()` 校验 nested fields。
- 或引入已有 schema validator。

验收标准:

- `structure.sections` 缺失必须失败。
- `structure.concepts` 缺失必须失败。
- `key_points=["a"]` 成功。
- `key_points=[1]` 失败。

### Fix 4: 中断状态落库

优先级: P1  
风险: Medium

修改点:

- CLI/service/orchestrator 之间要能拿到已创建 pipeline id。
- 捕获 `KeyboardInterrupt` 或 cancellation 后写入 cancelled/failed。

验收标准:

- 用户 Ctrl-C 后 `docuswarm status <pipeline_id>` 不再显示 running。
- session close 仍执行。
- output 目录保留，DB 记录可解释。

### Fix 5: 共用 referenced document resolver

优先级: P2  
风险: Medium

修改点:

- 将 SummaryAgent `_extract_referenced_files()` 与 ContextBuilder `_resolve_reference_docs()` 的文件引用提取逻辑收敛。
- 明确 `context_file` 是一级输入，不依赖正文自引用。

验收标准:

- SummaryAgent disabled 或失败时，ContextBuilder fallback 仍能读 `docs/calc-one-plus-one/calc-context.md`。

## 建议的测试矩阵

### Unit

1. `test_summary_agent_parses_direct_json_response`
2. `test_summary_agent_parses_markdown_fenced_json_response`
3. `test_summary_agent_uses_structured_output_when_present`
4. `test_summary_agent_rejects_missing_structure_sections`
5. `test_summary_agent_rejects_non_string_key_points`
6. `test_context_builder_resolves_subject_context_file`

### Integration

1. `start --context docs/calc-one-plus-one/calc-context.md` with fake SummaryAgent response as fenced JSON.
2. `start` with SummaryAgent returning `None`: pipeline should either continue with explicit degraded summary state or fail with a clear error, not hang silently.
3. Ctrl-C during SummaryAgent: pipeline status becomes `cancelled`.

### Regression

1. `tests/test_docuswarm_p1_summary_agent.py`
2. A no-network graph smoke test using fake Independent/Evaluator agents.
3. Full CLI smoke in mock LLM mode, verifying five deliverables exist in output.

## 本次已执行验证

```text
sed -n '1,260p' logs/docuswarm-2026-04-29.log
结果: 定位到 SummaryAgent fenced JSON 响应和 json.loads 失败。

find output -maxdepth 4 -print
结果: 只有 output/pipeline-1777439345215-46a35fb3 空目录。

.venv/bin/python -c '... json.loads(fenced_json) ...'
结果: JSONDecodeError: Expecting value: line 1 column 1 (char 0)。

.venv/bin/python -c '... extract_json(fenced_json) ...'
结果: 成功解析 summary=ok。

.venv/bin/python -c '... FakeSession + SummaryAgent._call_llm_for_summary ...'
结果: 复现 LLMSummaryError，返回 None。

.venv/bin/python -m pytest tests/test_docuswarm_p1_summary_agent.py --no-cov -q
结果: 2 passed，但没有覆盖本次失败形态。

.venv/bin/python -m compileall -q autoBMAD/docuswarm
结果: 通过。

.venv/bin/ruff check autoBMAD/docuswarm/agents/summary.py autoBMAD/docuswarm/llm/response.py autoBMAD/docuswarm/llm/session_manager.py tests/test_docuswarm_p1_summary_agent.py
结果: 2 个 F401，均在 tests/test_docuswarm_p1_summary_agent.py。
```

另外尝试运行 `tests/test_docuswarm_p1_runtime_contract.py` 时，30 秒无输出且继续运行；该现象与现有历史评估中提到的 runtime contract 测试挂起风险一致。本报告不把它作为本次 SummaryAgent JSON 失败的根因，只作为后续 E2E 回归稳定性风险记录。

## 最终判断

当前问题应按“解析合同缺陷”处理，不应归咎于模型输出质量。模型返回的是人类可读、机器可提取、字段完整的 JSON；系统内也已经存在能处理该格式的解析器。SummaryAgent 没有复用这条成熟路径，才使一个正常的 LLM 响应阻断了 pipeline。

最小正确修复是:

1. SummaryAgent 用 `extract_json()` 替代直接 `json.loads()`。
2. 为 SummaryAgent 加 fenced JSON 回归测试。
3. 随后补上 SDK `output_format` 和完整 schema validation。
4. 处理中断后 pipeline 状态仍为 running 的运维可见性问题。

完成 Fix 1 和对应测试后，当前 `calc-one-plus-one` 命令应至少能越过 SummaryAgent 阶段；若后续节点再失败，应基于新的日志继续按同样方法追踪，而不是把多个层次的问题混在一次修复里。

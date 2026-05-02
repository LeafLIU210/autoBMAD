# JSON 解析重试机制与 MCP Schema 约束深度研究报告

**研究日期**: 2026-04-06  
**研究工具**: `tools/json_retry_mcp_schema_analyzer.py`  
**分析产物**: `.tmp/json_retry_mcp_schema_analysis.json`  
**研究范围**: `autoBMAD/docuswarm` 核心模块 + `agentdocs` SDK 文档  
**参考文档**: `docs/architecture/`, `docs/design/`, `docs/PRD.md`

---

## 执行摘要（奥卡姆剃刀修订版）

本次研究基于静态代码分析 + agentdocs 文档比对，目标是**用最少的新机制约束所有 JSON 输出**。

**问题本质**：两个 Agent 调用模式不同，需要两种不同的最小化约束手段——两种手段都是对已有机制的直接延伸，无需引入第三种机制。

| Agent | LLM 调用模式 | JSON 输出 | 最小约束手段 |
|-------|-------------|-----------|-------------|
| EvaluatorAgent | `single_prompt()` → `query()` | 5字段（无工具调用） | SDK `output_format` |
| IndependentAgent | `ClaudeSDKClient.prompt()` (session) | 6字段 execution report | `submit_execution_report` MCP 工具 |

**推荐方案**：两步，各用其最适配的单一机制，无额外兜底层。

---

## 关键发现（精简为 3 条）

| ID | 严重程度 | 标题 |
|----|----------|------|
| F1 | CRITICAL | JSON 解析失败导致 pipeline 完全终止，无恢复路径 |
| F2 | HIGH | EvaluatorAgent 零容错，适合用 `output_format` 直接修复 |
| F3 | HIGH | IndependentAgent execution report 依赖自由文本，MCP 工具是同类约束的自然延伸 |

---

## 第一部分：两个 Agent 的 JSON 输出现状

### 1.1 EvaluatorAgent：零容错，5字段

调用链：`evaluator.py::_call_llm_with_prompt()` → `session_manager.single_prompt()` → SDK `query()`

**输出字段（5个，全部依赖自由文本解析）：**

| 字段 | 类型 | 风险 |
|------|------|------|
| `criterion_scores` | object（动态key: float） | key 拼写错误 / 类型错误 |
| `alignment_score` | float: 0.0-1.0 | 超出范围（如 1.5）/ 字符串型 |
| `verdict` | enum: APPROVED/NEEDS_REVISION/BLOCKED | 小写 `"approved"` / `"PASS"` 等非法值 |
| `issues_found` | array[string] | 返回 null / 非数组 |
| `suggestions` | array[string] | 返回 null / 非数组 |

**零容错代码证据：**
```python
# agents/evaluator.py :: _parse_response()
try:
    data: dict[str, Any] = extract_json(content_str)
except ResponseParseError as e:
    raise EvaluationError(f"Failed to parse response: {e}") from e
    # ← 无任何 fallback，直接 raise → pipeline FAILED
```

`verdict` 是 `DualAgentNode` 迭代循环的核心判断依据，一旦 JSON 解析失败，整个节点立即 FAILED，pipeline 终止。

### 1.2 IndependentAgent：有兜底但不完整，6字段

调用链：`independent.py::_call_llm_with_prompts()` → `SessionManager.create_session()` → `ClaudeSDKClient.prompt()`（**session 模式**）

**输出字段（6个，execution report）：**

| 字段 | 类型 | 风险 |
|------|------|------|
| `deliverable.file_path` | string | create_deliverable 工具返回值，依赖工具已被调用 |
| `deliverable.sha256` | string | 同上 |
| `questions[].question` | string | 格式不一致 |
| `questions[].priority` | enum: blocking/clarifying/optional | 非法 enum 值 |
| `questions[].context` | string | 缺失字段 |
| `action` | enum: create_deliverable | 缺失或值错误 |

**现有兜底路径：**
```python
# agents/independent.py :: _parse_response()
if is_non_json_text:
    file_path, sha256 = self._extract_create_deliverable_result(response)
    if file_path:  # ← 仅当 create_deliverable 工具已成功调用时有效
        data = {"deliverable": {"file_path": file_path, "sha256": sha256}, ...}
    else:
        raise ResponseParseAgentError(...)  # LLM 连工具都未调用则失败
```

**兜底的局限**：只在 `create_deliverable` 已被调用时生效；`questions[].priority` 的 enum 约束从未被验证。

---

## 第二部分：为何两种机制都需要（奥卡姆剖刀论证）

### 2.1 调用模式决定约束手段（不可绕过）

| Agent | LLM 调用模式 | `output_format` 适用性 | MCP 工具适用性 |
|-------|-------------|-------------------|-----------------|
| EvaluatorAgent | `single_prompt()` → `query()` | **直接适用** | 无工具调用，不需要 |
| IndependentAgent | `ClaudeSDKClient.prompt()` (session) | 文档未明确支持 | **直接适用**，与现有工具同类 |

**奉卡姆剖刀结论**：两种手段都是**对已有机制的直接延伸**，无需引入第三种机制：
- `output_format` 在 `agentdocs/14` 有文档，项目已在用 `query()` 调用中
- `@tool` 装饰器有 `create_deliverable` 先例，直接复用同模式

### 2.2 被裁剪的内容（延伸无益的复杂度）

| 被裁剪 | 原因 |
|--------|------|
| Option 1 Python 层兜底重试 | SDK 已内置重试（`output_format` 起作用后），再加 Python 层冗余 |
| Phase 3 独立重试层 | 引入新状态机，复杂度增加远大于收益 |
| F5 DualAgentNode 双层循环 | 属于长期优化，与当前目标无关 |

**保留**：Step 1（EvaluatorAgent `output_format`）+ Step 2（`submit_execution_report` MCP 工具），第三种机制不需要。

### 2.3 现有迭代机制（`nodes/dual_agent.py`）

```python
while iteration < self.max_iterations:  # 默认 max_iterations=3
    iteration += 1
    try:
        independent_output = await self.independent_agent.execute_with_input(...)
    except Exception as e:
        self.logger.error("independent_agent_failed", ...)
        raise IndependentExecutionError(...)  # ← 直接抛出，不继续循环
    ...
    verdict = evaluator_output.verdict
    if verdict == "APPROVED":
        break
    elif verdict == "BLOCKED":
        break
    elif verdict == "NEEDS_REVISION":
        previous_feedback = {...}  # 携带改进意见，继续下一次迭代
```

**结论**：`while iteration < max_iterations` 是纯业务质量迭代循环（仅 `NEEDS_REVISION` 触发），**不处理技术失败**（JSON 解析错误立即 raise 并退出循环）。

### 2.4 JSON 约束缺口摘要

```
❌ output_format 未被使用（SDK 提供但项目未集成）
   - usage_locations: []   ← 扫描 session_manager.py，0处使用
✅ 受约束字段: 3 个（create_deliverable 工具参数: title, content, metadata）
❌ 未受约束字段: 11 个（execution report 6字段 + evaluator output 5字段）
```

---

## 第三部分：两步方案

### Step 1：EvaluatorAgent — SDK `output_format`

**涉及文件**：3个

| 文件 | 改动 |
|------|------|
| `llm/session_manager.py` | `single_prompt()` 新增 `output_format: dict \| None = None` 参数；`_create_options()` 支持注入 |
| `agents/evaluator_config/schemas.py` | 新建，定义 `EVALUATOR_OUTPUT_SCHEMA` |
| `agents/evaluator.py` | `_parse_response()` 使用 `message.structured_output`；处理 `error_max_structured_output_retries` |

**EVALUATOR_OUTPUT_SCHEMA：**
```json
{
  "type": "object",
  "required": ["criterion_scores", "alignment_score", "verdict", "issues_found", "suggestions"],
  "properties": {
    "criterion_scores": {
      "type": "object",
      "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "alignment_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "verdict": {"type": "string", "enum": ["APPROVED", "NEEDS_REVISION", "BLOCKED"]},
    "issues_found": {"type": "array", "items": {"type": "string"}},
    "suggestions": {"type": "array", "items": {"type": "string"}}
  }
}
```

**关键代码改动：**
```python
# session_manager.py
async def single_prompt(
    self,
    prompt: str,
    mode: str = "agent",
    yolo: bool = True,
    system_prompt: str | None = None,
    output_format: dict | None = None,  # 新增
) -> list[dict[str, Any]]:
    options = self._create_options(mode=mode, yolo=yolo)
    if output_format:
        options.output_format = output_format
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.structured_output:
            return message.structured_output  # 直接返回 dict
        elif getattr(message, 'subtype', None) == "error_max_structured_output_retries":
            raise EvaluationError("SDK structured output retries exhausted")
```

**实施清单**：
- [ ] `session_manager.py::single_prompt()` 增加 `output_format` 参数
- [ ] `agents/evaluator_config/schemas.py` 定义 `EVALUATOR_OUTPUT_SCHEMA`
- [ ] `agents/evaluator.py::_call_llm_with_prompt()` 传入 schema
- [ ] `agents/evaluator.py::_parse_response()` 使用 `structured_output`，删除 `extract_json()` 调用
- [ ] 处理 `error_max_structured_output_retries` 子类型消息

---

### Step 2：IndependentAgent — `submit_execution_report` MCP 工具

**涉及文件**：5个

| 文件 | 改动 |
|------|------|
| `tools/create_deliverable_sdk.py` | 新增 `submit_execution_report` 工具定义 |
| `llm/session_manager.py` | 在 MCP Server 注册新工具 |
| `agents/independent.py` (system prompt) | 追加「创建交付物后必须调用 submit_execution_report」指引 |
| `agents/independent.py::_parse_response()` | 优先从工具调用结果获取 execution report |
| `context/validator.py` | 更新 `IndependentOutputValidationStrategy` 支持工具结果格式 |

**`submit_execution_report` Schema：**
```python
@tool(
    "submit_execution_report",
    "提交执行报告，记录 create_deliverable 的执行结果和后续问题",
    {
        "type": "object",
        "required": ["deliverable", "action"],
        "properties": {
            "deliverable": {
                "type": "object",
                "required": ["title", "file_path", "sha256"],
                "properties": {
                    "title": {"type": "string"},
                    "file_path": {"type": "string"},
                    "sha256": {"type": "string"},
                    "content_summary": {"type": "string"}
                }
            },
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["question", "priority", "context"],
                    "properties": {
                        "question": {"type": "string"},
                        "priority": {"type": "string", "enum": ["blocking", "clarifying", "optional"]},
                        "context": {"type": "string"}
                    }
                }
            },
            "action": {"type": "string", "enum": ["create_deliverable"]}
        }
    }
)
async def submit_execution_report(deliverable: dict, action: str, questions: list | None = None) -> dict:
    ...
```

**实施清单**：
- [ ] `tools/create_deliverable_sdk.py` 添加 `submit_execution_report` 工具
- [ ] `llm/session_manager.py` 注册新工具
- [ ] `agents/independent.py` system prompt 增加工具调用要求
- [ ] `agents/independent.py::_parse_response()` 优先从工具结果解析
- [ ] `context/validator.py` 更新输出验证策略

---

## 第四部分：实施后约束覆盖率

| 阶段 | 覆盖字段数 | 覆盖率 | 新增覆盖 |
|------|-----------|----------|----------|
| 当前 | 3/14 | 21% | title, content, metadata |
| Step 1 完成 | 8/14 | 57% | + criterion_scores, alignment_score, verdict, issues_found, suggestions |
| Step 2 完成 | 14/14 | **100%** | + deliverable.file_path, sha256, questions[3字段], action |

**Step 1 后最关键预期收益**：`verdict` enum 约束初始化，`DualAgentNode` 迭代循环崩溃可能性极大降低。

**Step 2 后最关键预期收益**：`questions[].priority` enum 约束使 LLM 无法提交非法优先级字符串；`file_path` 和 `sha256` 直接源自工具返回值。

---

## 第五部分：已知局限与风险

| 局限 | 风险 | 说明 |
|------|------|------|
| `output_format` 与 session 模式兼容性未验证 | LOW | Step 1 仅用于 EvaluatorAgent 的 `query()` 模式，Step 2 绕过此限制 |
| SDK 内置重试次数不透明 | LOW | `error_max_structured_output_retries` 触发时手动抗拓 |
| `criterion_scores` key 名称无法约束 | LOW | 接受；key 来自 criteria 定义，相对稳定 |
| Prompt 调整可能影响 LLM 工具调用行为 | MEDIUM | Step 2 需要辭证测试，配合 system prompt 示例 |

---

## 附录 A：调试工具使用说明

```bash
# 运行调试工具（生成 .tmp/json_retry_mcp_schema_analysis.json）
cd d:/GITHUB/DocuSwarm
python tools/json_retry_mcp_schema_analyzer.py

# 工具输出摘要示例：
# 🔴 JSON 重试状态: NOT IMPLEMENTED
# 🟡 MCP 约束状态: PARTIAL (3/14 字段)
# 🟢 SDK 结构化输出: 可用（未集成）
# ✅ 推荐方案: Step1(EvaluatorAgent output_format) + Step2(submit_execution_report)
```

---

## 附录 B：相关文件索引

| 文件 | 作用 |
|------|------|
| `autoBMAD/docuswarm/agents/evaluator.py` | `_parse_response()` 零容错实现，`single_prompt()` 调用 |
| `autoBMAD/docuswarm/agents/independent.py` | `_parse_response()` + 工具兜底逻辑 |
| `autoBMAD/docuswarm/llm/session_manager.py` | `single_prompt()` + `_create_options()`，Step 1 改动主战场 |
| `autoBMAD/docuswarm/tools/create_deliverable_sdk.py` | 现有 MCP 工具 schema，Step 2 添加新工具 |
| `autoBMAD/docuswarm/context/validator.py` | `IndependentOutputValidationStrategy`，Step 2 涉及 |
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 业务迭代循环（不改动） |
| `autoBMAD/agentdocs/14_structured_outputs.md` | SDK `output_format` 使用文档 |
| `autoBMAD/agentdocs/19_custom_tools.md` | `@tool` 装饰器 JSON Schema 格式 |
| `tools/json_retry_mcp_schema_analyzer.py` | 本次研究的调试分析工具 |

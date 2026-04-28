# EPIC-38: JSON 输出 Schema 约束 —— output_format + submit_execution_report

**Epic ID**: EPIC-38  
**Epic 名称**: JSON 输出 Schema 约束双步方案  
**优先级**: HIGH（CRITICAL 级缺陷修复）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-07）  
**创建日期**: 2026-04-06  
**研究来源**: `docs/research/docuswarm-deep-reform/2026-04-06-json-retry-mcp-schema-constraint-research-report.md`  
**补充研究**: `docs/research/2026-04-07-nodes-tech-debt-dependency-analysis.md`（TD-004 节）

---

## Epic 概述

当前 DocuSwarm 中两个 Agent 的 JSON 输出均缺乏 Schema 约束，14个输出字段中有 11 个完全依赖自由文本解析，一旦 LLM 返回格式错误，pipeline 立即终止，无恢复路径。

**核心问题**：
- `EvaluatorAgent._parse_response()` 零容错：JSON 解析失败直接 `raise EvaluationError` → pipeline FAILED
- `IndependentAgent` execution report 的 `questions[].priority` enum 从未被验证
- SDK 的 `output_format` 机制已可用但项目未集成（扫描结果：0处使用）

> **⚠️ 2026-04-07 代码状态确认（TD-004）**：
> - `autoBMAD/docuswarm/agents/evaluator_config/schemas.py` 存在 `CriteriaWeights`、`EvaluationCriteria`、`ThresholdConfig` 等类型，**缺少 `EVALUATOR_OUTPUT_SCHEMA` 常量**（Story 38.2 的核心工作）
> - `autoBMAD/docuswarm/llm/session_manager.py::single_prompt()` **缺少 `output_format: dict | None = None` 参数**（Story 38.1 核心修改）
> - `autoBMAD/docuswarm/tools/create_deliverable_sdk.py` **无 `submit_execution_report` 工具**，仅有 `create_deliverable_tool`（Story 38.3 核心工作）
> - **这是 8 个 EPIC 中优先级最高的未实现 EPIC**，零容错 JSON 解析是运行时崩溃的最大风险来源

**推荐方案**（奥卡姆剃刀原则）：两步各用最适配的单一机制，无额外兜底层。

| Agent | 约束手段 | 原理 |
|-------|---------|------|
| EvaluatorAgent | SDK `output_format` | 调用模式为 `query()`，直接适用 |
| IndependentAgent | `submit_execution_report` MCP 工具 | 与现有 `create_deliverable` 同类，直接延伸 |

**实施后覆盖率**：3/14 字段（21%）→ 14/14 字段（**100%**）

---

## 背景与技术分析

### 当前输出字段覆盖状态

```
✅ 受约束字段 (3/14)：create_deliverable 工具参数
   - title, content, metadata

❌ 未受约束字段 (11/14)：
   EvaluatorAgent (5个):
   - criterion_scores (dynamic key: float)
   - alignment_score (float: 0.0-1.0)
   - verdict (enum: APPROVED/NEEDS_REVISION/BLOCKED)  ← pipeline 核心决策
   - issues_found (array[string])
   - suggestions (array[string])

   IndependentAgent execution report (6个):
   - deliverable.file_path
   - deliverable.sha256
   - questions[].question
   - questions[].priority (enum: blocking/clarifying/optional)  ← 从未验证
   - questions[].context
   - action (enum: create_deliverable)
```

### 关键代码现状

**EvaluatorAgent 零容错点** (`agents/evaluator.py::_parse_response()`):
```python
try:
    data: dict[str, Any] = extract_json(content_str)
except ResponseParseError as e:
    raise EvaluationError(f"Failed to parse response: {e}") from e
    # ← 无任何 fallback，直接 raise → pipeline FAILED
```

**现有 `single_prompt()` 签名** (`llm/session_manager.py:467`):
```python
async def single_prompt(
    self, prompt: str, mode: str = "agent", yolo: bool = True,
    system_prompt: str | None = None,
) -> list[dict[str, Any]]:
```

**`output_format` 使用情况**: 项目中 0 处使用（SDK 文档见 `agentdocs/14_structured_outputs.md`）

---

## Stories

### Story 38.1: EvaluatorAgent — SDK `output_format` 集成

**目标**：通过 SDK 原生 `output_format` 机制约束 EvaluatorAgent 的 5 个输出字段，消除 JSON 解析失败导致 pipeline 终止的风险。

**涉及文件**：3 个

### 验收标准

- [ ] `session_manager.py::single_prompt()` 接受可选的 `output_format: dict | None = None` 参数
- [ ] `_create_options()` 在 `output_format` 非 None 时将其注入 `ClaudeAgentOptions`
- [ ] `evaluator_config/schemas.py` 新增 `EVALUATOR_OUTPUT_SCHEMA` 常量（JSON Schema 格式）
- [ ] `evaluator.py::_call_llm_with_prompt()` 向 `single_prompt()` 传入 `output_format=EVALUATOR_OUTPUT_SCHEMA`
- [ ] `evaluator.py::_parse_response()` 优先从 `ResultMessage.structured_output` 读取结构化输出
- [ ] 处理 `error_max_structured_output_retries` 子类型消息（抛出 `EvaluationError` 并记录日志）
- [ ] 原有 `extract_json()` 调用在 `structured_output` 可用时被跳过（保留作兜底）

### 技术规格

**EVALUATOR_OUTPUT_SCHEMA**（新增至 `agents/evaluator_config/schemas.py`）：

```python
EVALUATOR_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["criterion_scores", "alignment_score", "verdict", "issues_found", "suggestions"],
    "properties": {
        "criterion_scores": {
            "type": "object",
            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0}
        },
        "alignment_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "verdict": {
            "type": "string",
            "enum": ["APPROVED", "NEEDS_REVISION", "BLOCKED"]
        },
        "issues_found": {"type": "array", "items": {"type": "string"}},
        "suggestions": {"type": "array", "items": {"type": "string"}}
    }
}
```

**`session_manager.py` 改动**：

```python
async def single_prompt(
    self,
    prompt: str,
    mode: str = "agent",
    yolo: bool = True,
    system_prompt: str | None = None,
    output_format: dict | None = None,  # NEW: Step 1
) -> list[dict[str, Any]]:
    ...
    options = self._create_options(mode=mode, yolo=yolo)
    if output_format:
        options.output_format = output_format
    ...
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            if message.structured_output:
                return [{"type": "structured", "data": message.structured_output}]
        elif getattr(message, 'subtype', None) == "error_max_structured_output_retries":
            raise EvaluationError("SDK structured output retries exhausted")
```

**`evaluator.py::_parse_response()` 改动**：

```python
def _parse_response(self, response: list[dict[str, Any]]) -> dict[str, Any]:
    # 优先使用 SDK 结构化输出
    if response and response[0].get("type") == "structured":
        data = response[0]["data"]
        # 仍执行 clamp 和 alignment_score 重算
        ...
        return data

    # 兜底：原有 extract_json() 路径
    content_str = self._extract_text_content(response)
    try:
        data = extract_json(content_str)
    except ResponseParseError as e:
        raise EvaluationError(f"Failed to parse response: {e}") from e
    ...
```

### 测试要求

- 单元测试：`tests/test_evaluator_output_schema.py`
  - 测试 `structured_output` 路径（Mock SDK 返回 `structured_output`）
  - 测试 `error_max_structured_output_retries` 处理
  - 测试 verdict enum 非法值被 SDK 拒绝（回归）
  - 测试 `alignment_score` 超出范围被 SDK 约束

---

### Story 38.2: 定义 `EVALUATOR_OUTPUT_SCHEMA` 常量

**目标**：将 Schema 定义集中在 `evaluator_config/schemas.py`，避免散落在多处。

**涉及文件**：1 个（`agents/evaluator_config/schemas.py`）

### 验收标准

- [ ] `EVALUATOR_OUTPUT_SCHEMA` 常量定义在 `schemas.py` 模块级别
- [ ] `EVALUATOR_OUTPUT_SCHEMA` 导出到 `__all__`
- [ ] Schema 的 `verdict` 枚举值与 `EvaluatorAgent` 中的硬编码字符串一致（`APPROVED`、`NEEDS_REVISION`、`BLOCKED`）
- [ ] Schema 的数值约束（minimum/maximum）与 `DEFAULT_THRESHOLDS` 和 `WEIGHT_SUM_TOLERANCE` 语义对齐

### 技术规格

在现有 `schemas.py` 中追加（已有 `CriteriaWeights`、`EvaluationCriteria` 等类型）：

```python
from typing import Any

# SDK output_format schema for EvaluatorAgent structured output
EVALUATOR_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "criterion_scores",
        "alignment_score",
        "verdict",
        "issues_found",
        "suggestions",
    ],
    "properties": {
        "criterion_scores": {
            "type": "object",
            "description": "Scores for each evaluation criterion (0.0-1.0)",
            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
        "alignment_score": {
            "type": "number",
            "description": "Overall weighted alignment score (0.0-1.0)",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "verdict": {
            "type": "string",
            "description": "Evaluation verdict",
            "enum": ["APPROVED", "NEEDS_REVISION", "BLOCKED"],
        },
        "issues_found": {
            "type": "array",
            "description": "List of issues found during evaluation",
            "items": {"type": "string"},
        },
        "suggestions": {
            "type": "array",
            "description": "List of improvement suggestions",
            "items": {"type": "string"},
        },
    },
}
```

---

### Story 38.3: IndependentAgent — `submit_execution_report` MCP 工具

**目标**：新增 `submit_execution_report` MCP 工具，通过工具 Schema 约束 IndependentAgent 的 6 个 execution report 字段，将约束覆盖率从 57% 提升至 100%。

**涉及文件**：4 个

### 验收标准

- [ ] `tools/create_deliverable_sdk.py` 新增 `submit_execution_report` 工具函数（`@tool` 装饰器）
- [ ] `submit_execution_report` 工具的 Schema 约束所有 6 个 execution report 字段
- [ ] `questions[].priority` 枚举值限定为 `["blocking", "clarifying", "optional"]`
- [ ] `action` 枚举值限定为 `["create_deliverable"]`
- [ ] 工具注册到 `create_deliverable_server()` 返回的 MCP Server 中（同服务器，复用注册）
- [ ] `agents/independent.py::_parse_response()` 优先从 `submit_execution_report` 工具调用结果中解析 execution report
- [ ] 工具导出到 `__all__`

### 技术规格

**`submit_execution_report` 工具定义**（新增至 `tools/create_deliverable_sdk.py`）：

```python
@tool(
    "submit_execution_report",
    "提交执行报告，记录 create_deliverable 的执行结果和后续问题。"
    "必须在调用 create_deliverable 之后立即调用。",
    {
        "type": "object",
        "required": ["deliverable", "action"],
        "properties": {
            "deliverable": {
                "type": "object",
                "required": ["title", "file_path", "sha256"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "交付物标题，与 create_deliverable 的 title 一致"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "create_deliverable 返回的 file_path 原值"
                    },
                    "sha256": {
                        "type": "string",
                        "description": "create_deliverable 返回的 sha256 原值"
                    },
                    "content_summary": {
                        "type": "string",
                        "description": "交付物内容摘要（可选）"
                    },
                },
            },
            "questions": {
                "type": "array",
                "description": "后续问题列表（可选）",
                "items": {
                    "type": "object",
                    "required": ["question", "priority", "context"],
                    "properties": {
                        "question": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["blocking", "clarifying", "optional"]
                        },
                        "context": {"type": "string"},
                    },
                },
            },
            "action": {
                "type": "string",
                "enum": ["create_deliverable"],
                "description": "操作类型，固定值 create_deliverable"
            },
        },
    },
)
async def submit_execution_report_tool(args: dict[str, Any]) -> dict[str, Any]:
    """MCP tool handler for submit_execution_report."""
    import json
    # Store the report in a shared state accessible to _parse_response
    # Returns confirmation to the LLM
    report = {
        "deliverable": args["deliverable"],
        "questions": args.get("questions", []),
        "action": args["action"],
    }
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {"status": "report_received", "report": report},
                    ensure_ascii=False,
                ),
            }
        ]
    }
```

**工具注册**（修改 `create_deliverable_server()`）：

```python
return create_sdk_mcp_server(
    name=server_name,
    version="1.0.0",
    tools=[create_deliverable_tool, submit_execution_report_tool],  # 添加新工具
)
```

**`independent.py::_parse_response()` 改动**：

```python
def _parse_response(self, response: list[dict[str, Any]]) -> dict[str, Any]:
    # 优先：从 submit_execution_report 工具调用结果提取
    tool_report = self._extract_submit_report_result(response)
    if tool_report:
        return {
            "deliverable": tool_report["deliverable"],
            "questions": tool_report.get("questions", []),
            "action": tool_report["action"],
        }

    # 兜底：原有 create_deliverable 结果提取路径
    ...
```

### 测试要求

- 单元测试：`tests/test_submit_execution_report.py`
  - 测试 `questions[].priority` 非法枚举值被 Schema 拒绝
  - 测试 `action` 非法枚举值被 Schema 拒绝
  - 测试工具成功注册到 MCP Server
  - 测试 `_parse_response()` 优先选择 `submit_execution_report` 结果

---

### Story 38.4: IndependentAgent System Prompt 更新

**目标**：在 IndependentAgent 的系统提示中明确要求在 `create_deliverable` 之后调用 `submit_execution_report`，确保工具调用顺序正确。

**涉及文件**：1 个（`agents/independent.py` 或 `prompts/independent_agent.md`）

### 验收标准

- [ ] 系统提示中包含明确指引：必须先调用 `create_deliverable`，再调用 `submit_execution_report`
- [ ] 指引中包含 `file_path` 和 `sha256` 使用说明（从 `create_deliverable` 返回值获取）
- [ ] 至少提供一个工具调用序列示例（示例格式：create_deliverable → submit_execution_report）
- [ ] 提示中说明 `questions[].priority` 的三个合法枚举值
- [ ] 更新不破坏现有系统提示结构（追加方式，不替换）

### 技术规格

在 `prompts/independent_agent.md` 末尾追加（或在 `independent.py` 的系统提示构建处注入）：

```markdown
## 执行报告提交规则

在成功调用 `create_deliverable` 后，**必须立即**调用 `submit_execution_report` 工具：

1. 使用 `create_deliverable` 返回的 `file_path` 和 `sha256` 原值（不得修改）
2. `action` 字段固定填写 `"create_deliverable"`
3. 如有后续问题，通过 `questions` 数组提交，`priority` 仅限：
   - `"blocking"` - 阻塞后续工作的关键问题
   - `"clarifying"` - 需要澄清的非阻塞问题
   - `"optional"` - 可选的优化建议问题

工具调用顺序示例：
```
create_deliverable(title="...", content="...")
→ 获取返回值中的 file_path 和 sha256
→ submit_execution_report(
    deliverable={"title": "...", "file_path": "<原值>", "sha256": "<原值>"},
    action="create_deliverable"
  )
```
```

### 测试要求

- 集成测试：验证 Mock LLM 在接收更新后的系统提示时，工具调用顺序符合预期

---

### Story 38.5: 更新 Validator 支持工具结果格式

**目标**：更新 `context/validator.py` 中的 `IndependentOutputValidationStrategy`，使其支持来自 `submit_execution_report` 工具的结果格式。

**涉及文件**：1 个（`context/validator.py`）

### 验收标准

- [ ] `IndependentOutputValidationStrategy` 能够验证来自 `submit_execution_report` 工具结果的 execution report
- [ ] 向后兼容：原有 `create_deliverable` 结果路径继续有效
- [ ] 验证逻辑检查 `deliverable.file_path` 和 `deliverable.sha256` 非空
- [ ] 验证逻辑检查 `action` 值为合法枚举值
- [ ] 验证逻辑检查 `questions[].priority` 值为合法枚举值（`blocking`/`clarifying`/`optional`）

### 测试要求

- 单元测试：测试新旧两种输出格式的验证路径

---

## 依赖关系

```
Story 38.2 → Story 38.1  (Schema 常量先定义，再集成到 single_prompt)
Story 38.3 → Story 38.4  (MCP 工具先定义，再更新系统提示)
Story 38.5 → Story 38.3  (Validator 更新依赖新工具格式确定)
```

Story 38.1 和 Story 38.3 可**并行**实施（两个 Agent 改动相互独立）。

---

## 实施阶段划分

### 阶段 1（CRITICAL 修复，优先级最高）

- **Story 38.2**：定义 `EVALUATOR_OUTPUT_SCHEMA`（无风险，纯新增）
- **Story 38.1**：集成 `output_format` 到 `single_prompt()` 和 `evaluator.py`

**预期收益**：`verdict` enum 约束初始化，`DualAgentNode` 迭代循环崩溃可能性极大降低。

### 阶段 2（完整覆盖）

- **Story 38.3**：添加 `submit_execution_report` MCP 工具
- **Story 38.4**：更新系统提示
- **Story 38.5**：更新 Validator

**预期收益**：14/14 字段全部受约束，`questions[].priority` enum 约束生效。

---

## 覆盖率里程碑

| 阶段 | 覆盖字段 | 覆盖率 | 关键新增 |
|------|---------|--------|---------|
| 当前 | 3/14 | 21% | create_deliverable: title, content, metadata |
| 阶段 1 完成 | 8/14 | 57% | + criterion_scores, alignment_score, verdict, issues_found, suggestions |
| 阶段 2 完成 | 14/14 | **100%** | + deliverable.file_path, sha256, questions[3字段], action |

---

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| `output_format` 与 `query()` 模式实际兼容性 | LOW | 仅用于 EvaluatorAgent（非 session 模式），SDK 文档明确支持 |
| SDK 内置重试次数不透明 | LOW | 捕获 `error_max_structured_output_retries` 子类型消息，手动降级 |
| `criterion_scores` 动态 key 无法完全约束 | ACCEPTED | key 来自 criteria 定义，相对稳定；value 类型已约束 |
| 系统提示修改影响 LLM 工具调用行为 | MEDIUM | Story 38.4 需经测试验证，配合示例确保行为稳定 |

---

## 排除范围（已裁剪）

研究报告已论证以下方案**不纳入本 Epic**：

| 排除项 | 排除原因 |
|--------|---------|
| Python 层兜底重试机制 | SDK `output_format` 已内置重试，Python 层重复 |
| 独立重试状态机 | 引入新状态机复杂度远大于收益 |
| DualAgentNode 双层循环重构 | 属于长期优化，与本 Epic 目标无关 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `autoBMAD/docuswarm/agents/evaluator.py` | Story 38.1 主战场（`_parse_response` 改动） |
| `autoBMAD/docuswarm/agents/evaluator_config/schemas.py` | Story 38.2 新增 `EVALUATOR_OUTPUT_SCHEMA` |
| `autoBMAD/docuswarm/llm/session_manager.py` | Story 38.1（`single_prompt` + `_create_options` 改动） |
| `autoBMAD/docuswarm/tools/create_deliverable_sdk.py` | Story 38.3 新增 `submit_execution_report` 工具 |
| `autoBMAD/docuswarm/agents/independent.py` | Story 38.3/38.4（`_parse_response` + 系统提示） |
| `autoBMAD/docuswarm/context/validator.py` | Story 38.5（验证策略更新） |
| `autoBMAD/agentdocs/14_structured_outputs.md` | SDK `output_format` 使用文档参考 |
| `autoBMAD/agentdocs/19_custom_tools.md` | `@tool` 装饰器 JSON Schema 参考 |

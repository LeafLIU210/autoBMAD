# DocuSwarm Kimi 消息提取失败根因分析报告

**日期**: 2026-04-06  
**严重程度**: CRITICAL  
**状态**: 根因已确认，修复方案已验证  
**调试工具**: `tools/kimi_message_probe.py`  
**SDK 参考**: `autoBMAD/agentdocs/` (官方文档，2026-03-26)

---

## 1. 问题描述

执行 `python -m autoBMAD.docuswarm start --context docs/bubble-sort/bubble-sort-context.md` 后，终端输出：

```
2026-04-06T09:21:11.044230 [warning] no_text_extracted
  has_assistant_message=False
  hint=Check if LLM returned valid assistant messages with text content
  message_count=0
  role_list=[]
```

日志显示 pipeline 在 `analyst` 节点的 `llm_message_received` 后静默中断（日志截断于第 106 行），没有任何错误抛出，也没有进一步的输出文件生成。

---

## 2. 失败链时序分析

```
09:20:56  hybrid_orchestrator_initialized
09:20:56  starting_pipeline
09:20:56  single_prompt_start         ← ContextValidator LLM 上下文校验
09:21:11  single_prompt_result        ← SDK 返回了 ResultMessage（有内容）
09:21:11  single_prompt_complete      message_count=0  ← 但 messages 为空!
09:21:11  [WARNING] no_text_extracted  ← 提取失败
09:21:11  pipeline_work_dir_created
09:21:11  node_execution_started (analyst)
09:21:11  creating_session
09:21:11  session_created             ← 会话建立成功
09:21:11  llm_message_received × N   ← 收到多条消息
(日志中断，无后续输出)
```

**关键现象**：
- `single_prompt_result` 中 `result=Hello`（Kimi 实际有响应）
- `single_prompt_complete` 中 `message_count=0`（但 messages 列表为空）
- `no_text_extracted` 中 `has_assistant_message=False`（无 assistant 角色消息）

---

## 3. 根因分析

### 3.1 根因 1（CRITICAL）：AssistantMessage 无 `role` 属性

**问题位置**：`autoBMAD/docuswarm/llm/response.py` → `extract_text_from_messages()`，第 190 行

**现象**：  
`claude_agent_sdk v0.1.68` 的 `AssistantMessage` dataclass 定义如下：

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None
    # 注意：没有 role 字段！
```

而代码中的过滤逻辑是：

```python
# response.py L190
msg_role: str = getattr(msg, "role", "")
if msg_role != "assistant":
    continue  # ← AssistantMessage 没有 role，msg_role="" != "assistant"，全部跳过！
```

**结果**：所有 `AssistantMessage` 被跳过，`messages` 返回空列表，导致 `no_text_extracted`。

### 3.2 根因 2（HIGH）：`_message_to_dict` 过滤丢弃所有消息

**问题位置**：`autoBMAD/docuswarm/llm/session_manager.py` → `_message_to_dict()`，第 537 行

```python
def _message_to_dict(self, msg: Any) -> dict[str, Any] | None:
    role = getattr(msg, "role", None)
    if role is None:
        return None  # ← AssistantMessage.role 不存在，getattr 返回 None，丢弃！
```

`single_prompt()` 调用 `_message_to_dict()` 对每条消息转换，由于 `AssistantMessage` 无 `role` 属性，所有消息都被返回 `None` 并被过滤，导致 `messages` 列表为空（`message_count=0`）。

### 3.3 根因 3（MEDIUM）：TextBlock/ThinkingBlock 无 `type` 属性

**现象**：  
代码中存在 `getattr(item, "type", "") == "text"` 的判断逻辑，但：

```python
@dataclass
class TextBlock:
    text: str
    # 无 type 字段

@dataclass  
class ThinkingBlock:
    thinking: str
    signature: str
    # 无 type 字段
```

即使通过了 role 检查，后续按 `type` 属性区分 TextBlock 的逻辑也会失效。

### 3.4 pipeline 后续静默挂起

在 `analyst` 节点，`session_created` 成功后（日志第 47 行），`ClaudeSessionWrapper.prompt()` 调用：

1. `await self._client.query(message)` — 发送成功
2. `async for msg in self._client.receive_messages()` — 开始接收消息

收到消息（`llm_message_received` × N），但由于 `independent.py` 中对 `session.prompt()` 返回消息的处理同样依赖 `msg_dict` 转换（转换结果为空），最终 `_parse_response([])` 抛出 `LLMCallError("No messages returned from session")`，被 `execute()` 的 `finally` 块捕获后静默退出，日志不再继续。

---

## 4. 受影响的代码路径

| 文件 | 位置 | 问题描述 |
|------|------|----------|
| `autoBMAD/docuswarm/llm/response.py` | `extract_text_from_messages()` L187-190 | `msg_role != "assistant"` 过滤掉所有 AssistantMessage |
| `autoBMAD/docuswarm/llm/session_manager.py` | `_message_to_dict()` L537 | `role is None` 时返回 None，AssistantMessage 全部丢弃 |
| `autoBMAD/docuswarm/agents/independent.py` | `_extract_content_from_messages()` L389 | 同上，依赖 role 字段提取内容 |
| `autoBMAD/docuswarm/context/validator.py` | `_parse_validation_response()` L1248 | 调用 `extract_text_from_messages()`，间接受影响 |

---

## 5. SDK 消息结构对比

### 5.1 实测结果（`tools/kimi_message_probe.py`）

通过调试工具实测（`claude_agent_sdk v0.1.68` + Kimi endpoint）：

```
[0] SystemMessage        has_role=False  subtype='init'
[1] AssistantMessage     has_role=False  content=[ThinkingBlock(thinking=...)]
[2] AssistantMessage     has_role=False  content=[TextBlock(text='Hello')]
[3] ResultMessage        has_role=False  result='Hello'
```

### 5.2 官方文档定义（`agentdocs/05_python.md`）

官方文档明确定义的消息类型联合体：

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent

# 内容块
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

各消息类型字段（**均无 `role` 字段**）：

| 消息类型 | 关键字段 | 说明 |
|----------|----------|------|
| `UserMessage` | `content: str \| list[ContentBlock]` | 用户输入 |
| `AssistantMessage` | `content: list[ContentBlock]`, `model: str` | 模型响应 |
| `SystemMessage` | `subtype: str`, `data: dict` | 系统事件（如 `subtype='init'`） |
| `ResultMessage` | `subtype`, `duration_ms`, `is_error`, `num_turns`, `session_id`, `result`, `structured_output` | 最终结果 |
| `StreamEvent` | `uuid`, `session_id`, `event`, `parent_tool_use_id` | 流式事件（需开启 `include_partial_messages=True`） |

**官方推荐的消息处理模式**（来自 `agentdocs/05_python.md` 示例）：

```python
# 官方示例 — 使用 isinstance() 判断消息类型
async for message in query(...):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock):
                print(f"Using tool: {block.name}")
            if isinstance(block, TextBlock):
                print(f"Text: {block.text}")
```

**官方文档从未使用 `getattr(msg, 'role', '')` 模式**，这是 DocuSwarm 代码引入缺陷的根本原因。

### 5.3 关键发现

- 所有消息类型均**无 `role` 属性**（官方文档设计如此）
- `TextBlock` / `ThinkingBlock` 均**无 `type` 属性**（只有 `text` / `thinking` 字段）
- `ResultMessage.result` 有完整内容（说明 Kimi API 响应正常）
- 官方唯一推荐的类型判断方式：`isinstance()`

---

## 6. 修复方案

### Fix-1：`_message_to_dict()` — 用 isinstance 替代 role 检查

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
# 当前（有缺陷）
def _message_to_dict(self, msg: Any) -> dict[str, Any] | None:
    if isinstance(msg, ResultMessage):
        return None
    role = getattr(msg, "role", None)
    if role is None:
        return None  # ← 丢弃所有无 role 属性的消息

# 修复后（符合官方文档推荐模式）
from claude_agent_sdk.types import AssistantMessage, UserMessage, SystemMessage

def _message_to_dict(self, msg: Any) -> dict[str, Any] | None:
    if isinstance(msg, ResultMessage):
        return None
    if isinstance(msg, SystemMessage):
        return None  # 系统初始化消息，跳过（subtype='init' 等）

    # Fix: 用 isinstance 判断消息类型，符合官方文档设计
    if isinstance(msg, AssistantMessage):
        role = "assistant"
    elif isinstance(msg, UserMessage):
        role = "user"
    else:
        role = getattr(msg, "role", None)
        if role is None:
            return None

    content = getattr(msg, "content", None)
    # ... 后续内容转换逻辑保持不变
```

### Fix-2：`extract_text_from_messages()` — 用 isinstance 替代 role 字符串比较

**文件**: `autoBMAD/docuswarm/llm/response.py`

```python
# 当前（有缺陷）
msg_role: str = getattr(msg, "role", "")
if msg_role != "assistant":
    continue

# 修复后（符合官方文档推荐模式）
from claude_agent_sdk.types import AssistantMessage

# 优先用 isinstance 检查，fallback 到 role 字符串（兼容旧格式字典）
is_assistant = isinstance(msg, AssistantMessage) or getattr(msg, "role", "") == "assistant"
if not is_assistant:
    continue
```

### Fix-3：TextBlock 提取 — 用 isinstance 替代 type 属性比较

**文件**: `autoBMAD/docuswarm/llm/response.py`，`_message_to_dict()` 内容转换部分

```python
# 当前（有缺陷）
if item_type == "text":  # ← TextBlock 没有 type 属性，item_type 永远不是 "text"

# 修复后（符合官方文档 ContentBlock 类型定义）
# ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
from claude_agent_sdk.types import TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock

if isinstance(item, TextBlock):
    converted_content.append({"type": "text", "text": item.text})
elif isinstance(item, ThinkingBlock):
    # ThinkingBlock 字段：thinking: str, signature: str
    # 可根据业务需求保留或跳过
    pass
elif isinstance(item, ToolUseBlock):
    converted_content.append({
        "type": "tool_use",
        "name": getattr(item, "name", ""),
        "input": getattr(item, "input", {}),
        "id": getattr(item, "id", ""),
    })
elif isinstance(item, ToolResultBlock):
    converted_content.append({
        "type": "tool_result",
        "tool_use_id": getattr(item, "tool_use_id", ""),
        "content": getattr(item, "content", []),
    })
```

### Fix-4（已验证有效）：直接用 isinstance 提取文本

通过 `tools/kimi_message_probe.py` 的修复验证模块确认，与**官方文档示例模式完全一致**：

```python
from claude_agent_sdk.types import AssistantMessage, TextBlock

async for msg in query(prompt=prompt, options=opts):
    if isinstance(msg, AssistantMessage):          # Fix-1: 不用 role（官方推荐）
        for item in msg.content:
            if isinstance(item, TextBlock):         # Fix-2: 不用 type attr（官方推荐）
                print(item.text)                    # 正确提取文本
# 输出: 'Hello!'  ← 验证通过
```

### Fix-5（补充）：StreamEvent 处理

若代码中启用了 `include_partial_messages=True`，还需处理 `StreamEvent` 类型，避免将其误判为 AssistantMessage：

```python
from claude_agent_sdk.types import AssistantMessage, StreamEvent, ResultMessage

async for msg in query(prompt=prompt, options=opts):
    if isinstance(msg, StreamEvent):
        continue   # 流式增量事件，跳过（或按需处理 delta）
    if isinstance(msg, ResultMessage):
        break      # 最终结果，终止迭代
    if isinstance(msg, AssistantMessage):
        ...        # 处理完整消息块
```

---

## 7. 环境状态

| 变量 | 值 | 状态 |
|------|----|------|
| `ANTHROPIC_BASE_URL` | `https://api.kimi.com/coding/` | 已配置 |
| `ANTHROPIC_API_KEY` | `sk-kimi-...` | 已配置 |
| `ENABLE_TOOL_SEARCH` | NOT SET | 正常（不需要） |
| `ANTHROPIC_MODEL_NAME` | NOT SET | 正确（已移除，禁用） |
| `claude_agent_sdk` | `0.1.68` | 已安装 |
| Claude Code CLI | `2.1.92` | 已安装 |

**Kimi API 连通性**：正常（`ResultMessage.result='Hello'` 证明 API 调用成功）

> **注意**：`ClaudeAgentOptions` 有 `model` 字段（`str | None`），但 DocuSwarm **禁止配置模型名称**——`model` 应保持 `None`，模型选择统一由 API 网关侧（Kimi）管理，不在客户端指定。

---

## 8. 影响范围

本问题导致以下功能**全部失效**：

1. **ContextValidator LLM 校验** (`validate_context_with_llm`) — 虽然设计为 fail-open，但文本提取返回空导致 JSON 解析失败后 fallback 跳过，状态不可靠
2. **IndependentAgent 执行** — `_call_llm_with_prompts()` 返回空 messages，`_parse_response([])` 抛出 `LLMCallError`，节点静默失败
3. **EvaluatorAgent 执行** — 相同路径受影响
4. **所有节点输出文件** — 不会生成任何 `.md` 交付物

---

## 9. 紧急程度

**P0 - 阻断性缺陷**：整个 pipeline 无法产生任何输出，系统处于完全不可用状态。

修复优先级：
1. **立即** 修复 `session_manager.py:_message_to_dict()` — 影响 `single_prompt()` 全链路
2. **立即** 修复 `response.py:extract_text_from_messages()` — 影响上下文校验和文本提取
3. **跟进** 修复 `response.py` 中的 `_message_to_dict` 内容转换（TextBlock isinstance 检查）
4. **跟进** 补充 `StreamEvent` 类型守卫（若启用流式输出）

**修复原则**：所有修复应以 `isinstance()` 类型检查为主，`getattr` 为 fallback，与官方文档（`agentdocs/05_python.md`）示例保持一致。

---

## 10. SDK 命名迁移说明

根据 `agentdocs/06_migration_guide.md`，SDK 已从 `claude-code-sdk` 更名为 `claude-agent-sdk`：

| 方面 | 旧版 | 新版（当前） |
|------|------|------|
| Python 包名 | `claude-code-sdk` | `claude-agent-sdk` |
| 导入路径 | `from claude_code_sdk import ...` | `from claude_agent_sdk import ...` |
| Options 类 | `ClaudeCodeOptions` | `ClaudeAgentOptions` |

**破坏性变更**：
- 系统提示词不再默认使用，需显式设置 `system_prompt`
- 设置源不再默认加载，需显式设置 `setting_sources`

若项目中仍有旧包名导入（如 `from claude_code_sdk import ...`），需一并迁移，否则运行时报 `ModuleNotFoundError`。

---

## 11. 调试工具

**`tools/kimi_message_probe.py`** — 新增的专项诊断工具

```bash
# 基础探测（验证消息结构）
python tools/kimi_message_probe.py

# 指定提示词
python tools/kimi_message_probe.py --prompt "你好，用一个词回复"

# 完整 pipeline 流程探测
python tools/kimi_message_probe.py --full-pipeline

# 保存 JSON 报告
python tools/kimi_message_probe.py --output .tmp/probe_report.json
```

工具功能：
1. **RAW SDK 消息结构探测** — 打印每条消息的完整属性
2. **问题自动检测** — 识别 ISSUE-001（role 缺失）、ISSUE-002（文本提取失败）
3. **`single_prompt()` 仿真** — 复现实际调用路径
4. **修复方案验证** — 用 `isinstance` 方式验证文本可正确提取

---

*报告生成于 2026-04-06 | 基于 `tools/kimi_message_probe.py` 实测数据 + `autoBMAD/agentdocs/` 官方文档（2026-03-26）*

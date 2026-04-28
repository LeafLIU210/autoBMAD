# DocuSwarm 超时 + ThinkingBlock 解析失败根因研究报告

**日期**: 2026-04-06
**分析人**: 自动化调试分析
**严重等级**: P0 (阻塞流水线执行)

---

## 1. 问题描述

执行命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 时，
analyst 节点在第 1 次迭代即失败，错误链如下：

```
prompt_timeout (60s, 21 messages received)
  → llm_call_error (LLMError: Session prompt timed out)
    → llm_returned_plain_text_fallback (content: ThinkingBlock repr)
      → independent_agent_failed (no create_deliverable tool result)
        → node_execution_failed (IndependentExecutionError)
```

## 2. 日志时间线分析

| 时间戳 | 事件 | 说明 |
|--------|------|------|
| 17:53:14.930 | session_created | analyst 会话创建成功 |
| 17:53:14.980 | message_received #1 | 首条消息 (SystemMessage) |
| 17:53:18.680 | message_received #2 | AssistantMessage (thinking) |
| 17:53:19.833-27.981 | messages #3-#16 | 快速消息流 (tool calls) |
| 17:53:30.703-32.578 | messages #17-#20 | 继续处理 |
| 17:53:42.549 | message_received #21 | **最后一条消息** |
| 17:54:14.945 | **prompt_timeout** | 60 秒超时触发 (距 session 创建正好 60s) |

**关键观察**: 
- 21 条消息在 28 秒内接收完毕
- 最后一条消息到超时之间有 **32.4 秒的空白期**
- Agent 正在执行 create_deliverable 工具调用或生成最终响应时被中断

## 3. 根因分析

### RC-1: 60 秒超时对 Agent 模式不足 (PRIMARY)

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:762`

```python
class ClaudeSessionWrapper:
    DEFAULT_PROMPT_TIMEOUT: int = 60  # ← 硬编码 60 秒
```

**问题**: Claude Agent SDK 在 agent 模式下执行多步操作：
1. 接收 system prompt + user prompt
2. ThinkingBlock (模型思考)
3. ToolUseBlock (调用 create_deliverable 工具)
4. ToolResultBlock (等待工具返回)
5. TextBlock (生成最终 JSON 响应)

`asyncio.timeout(60)` 包裹整个 `receive_messages()` 流，从第一条消息开始计时。
Agent 在 28 秒内完成了 21 条消息交互，但 create_deliverable 工具执行 + 最终 JSON 生成
需要额外时间，60 秒总窗口不够。

**证据**: 日志显示最后一条消息在 17:53:42.549，超时在 17:54:14.945，
中间的 32 秒 SDK 正在等待工具完成。

### RC-2: ThinkingBlock 内容泄露到文本提取 (SECONDARY)

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:620-621`

```python
# _message_to_dict() 的 else 分支
else:
    content = [{"type": "text", "text": str(content)}]
```

**问题**: 当 SDK 返回的消息 content 不是 str 也不是 list 时（例如单个 ThinkingBlock 对象），
代码会对其执行 `str()` 转换，产生 `"ThinkingBlock(thinking='I need to create...')"` 字符串，
然后包装为 `{"type": "text", "text": "ThinkingBlock(thinking='...')"}` 字典。

这导致 `_extract_content_from_messages()` 在后续处理中将 ThinkingBlock 的 repr 作为文本返回，
触发 `_parse_response()` 中的非 JSON 回退逻辑。

**影响链**:
1. `_message_to_dict()` 将 ThinkingBlock 对象 str() 化为文本
2. `_extract_content_from_messages()` 返回 `"ThinkingBlock(thinking='...')"` 
3. `extract_json()` 失败（非 JSON 文本）
4. `_parse_response()` 尝试回退，检查 create_deliverable 工具结果
5. 工具结果不存在（因为 RC-1 超时中断了工具调用）
6. 抛出 `ResponseParseAgentError`

### RC-3: DualAgentNode 未传递 timeout 参数 (CONTRIBUTING)

**位置**: `autoBMAD/docuswarm/nodes/dual_agent.py:321-323`

```python
# execute_with_context() 调用 execute_with_input() 时不传 timeout
independent_output = await self.independent_agent.execute_with_input(
    agent_input=independent_input,
    pipeline_id=pipeline_id,
    # ← 缺少 timeout 参数，默认 60s
)
```

**问题**: `execute_with_input()` 方法签名有 `timeout: int = 60` 参数，
但 `DualAgentNode.execute_with_context()` 调用时未传递此参数。
从 pipeline 级别到 session 级别，没有任何配置入口可以调整超时时间。

## 4. _convert_content_block() ThinkingBlock 处理验证

当前代码在 `session_manager.py:651-655` 通过 isinstance 正确过滤 ThinkingBlock：

```python
elif isinstance(item, ThinkingBlock):
    converted = None  # 正确：跳过 ThinkingBlock
```

但此过滤仅在 content 为 **list** 类型时生效。当 content 是**单个对象**时，
走 `_message_to_dict()` 的 else 分支 (line 620)，`isinstance` 检查被绕过。

## 5. 修复建议

### Fix-1: 增加默认超时至 300 秒

```python
# session_manager.py
class ClaudeSessionWrapper:
    DEFAULT_PROMPT_TIMEOUT: int = 300  # 从 60 → 300
```

### Fix-2: 处理单个 ContentBlock 内容

```python
# session_manager.py _message_to_dict() 中，在 else 分支前添加：
elif hasattr(content, 'type'):
    # 单个 content block（不在 list 中）
    converted_block = self._convert_content_block(content)
    if converted_block:
        content = [converted_block]
    else:
        content = []  # ThinkingBlock 等被过滤
```

### Fix-3: DualAgentNode 传递可配置 timeout

```python
# dual_agent.py execute_with_context() 中传递 timeout
independent_output = await self.independent_agent.execute_with_input(
    agent_input=independent_input,
    pipeline_id=pipeline_id,
    timeout=self._get_agent_timeout(),  # 新增
)
```

## 6. 影响范围

| 组件 | 文件 | 修改类型 |
|------|------|----------|
| ClaudeSessionWrapper | `llm/session_manager.py` | DEFAULT_PROMPT_TIMEOUT 300s + 单 content block 处理 |
| DualAgentNode | `nodes/dual_agent.py` | 传递 timeout 参数 |
| Config | `config.py` | 新增 agent_timeout 配置字段 |

## 7. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 增大超时导致长时间等待 | 中 | 低 | 用户可通过配置覆盖 |
| content block 处理引入新 bug | 低 | 中 | 单元测试覆盖 |
| 向后兼容性 | 低 | 低 | 默认值变更，不影响 API |

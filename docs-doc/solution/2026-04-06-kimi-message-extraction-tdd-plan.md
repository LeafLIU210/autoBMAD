# DocuSwarm Kimi 消息提取修复 - 测试驱动开发方案

**日期**: 2026-04-06  
**严重级别**: P0 - 阻断性  
**关联分析**: [根因分析报告](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md)  
**SDK 版本**: `claude_agent_sdk==0.1.68`  

---

## 1. 概述

### 1.1 问题背景

DocuSwarm 在使用 Kimi API 时出现 `no_text_extracted` 警告，整个 pipeline 无法产生任何输出。根本原因是代码错误地假设 SDK 消息对象有 `role` 属性，而 `claude_agent_sdk v0.1.68` 的 `AssistantMessage` 等消息类型**根本没有 `role` 字段**。

### 1.2 核心问题

| 优先级 | 问题 | 影响文件 | 症状 |
|--------|------|----------|------|
| P0 | AssistantMessage 无 `role` 属性 | `response.py`, `session_manager.py` | 所有消息被过滤，返回空列表 |
| P1 | TextBlock 无 `type` 属性 | `response.py`, `session_manager.py` | 无法提取文本内容 |
| P2 | Pipeline 静默挂起 | `independent.py` | 无错误抛出，无输出文件 |

### 1.3 修复原则

**使用 `isinstance()` 类型检查代替 `getattr()` 属性访问**，与官方文档示例保持一致：

```python
# ❌ 错误方式（当前代码）
msg_role = getattr(msg, "role", "")
if msg_role == "assistant": ...

# ✅ 正确方式（官方推荐）
from claude_agent_sdk.types import AssistantMessage
if isinstance(msg, AssistantMessage): ...
```

---

## 2. 测试策略（TDD 流程）

### 2.1 TDD 循环

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. 写失败测试   │ -> │  2. 实现修复    │ -> │  3. 验证通过    │
│  (Red)          │    │  (Green)        │    │  (Refactor)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ^                                             │
         └─────────────────────────────────────────────┘
                        4. 重构优化
```

### 2.2 测试金字塔

```
         /\
        /  \
       / E2E \          端到端测试 (1个)
      /────────\         - 完整 pipeline 验证
     /          \        
    / Integration \      集成测试 (3个)
   /────────────────\     - SessionManager + SDK
  /                  \    - Agent 执行流程
 /    Unit Tests       \   单元测试 (15+个)
/────────────────────────\  - 消息类型判断
                          - 文本提取逻辑
                          - 边界条件
```

---

## 3. 测试用例详细设计

### 3.1 单元测试 - `test_response_message_extraction.py`

#### 测试组 A: AssistantMessage 识别（P0）

```python
# Test A1: AssistantMessage 应被正确识别
# 目标: 验证 extract_text_from_messages 能处理无 role 属性的 AssistantMessage
def test_extract_text_from_assistant_message_without_role():
    """
    Given: AssistantMessage(content=[TextBlock(text="Hello")], model="kimi")
    When: 调用 extract_text_from_messages([msg])
    Then: 返回 "Hello"
    """
    pass  # TODO: 实现

# Test A2: 混合消息列表处理
def test_extract_text_from_mixed_message_types():
    """
    Given: [SystemMessage, AssistantMessage, ResultMessage]
    When: 调用 extract_text_from_messages
    Then: 正确提取 AssistantMessage 的文本，跳过其他类型
    """
    pass  # TODO: 实现

# Test A3: 空 content 处理
def test_extract_text_with_empty_content():
    """
    Given: AssistantMessage(content=[], model="kimi")
    When: 调用 extract_text_from_messages
    Then: 返回空字符串，记录 warning
    """
    pass  # TODO: 实现
```

#### 测试组 B: TextBlock 内容提取（P1）

```python
# Test B1: TextBlock 文本提取
def test_extract_text_from_text_block():
    """
    Given: AssistantMessage(content=[TextBlock(text="Hello World")])
    When: 调用 extract_text_from_messages
    Then: 返回 "Hello World"
    """
    pass  # TODO: 实现

# Test B2: 多个 TextBlock 合并
def test_extract_text_from_multiple_text_blocks():
    """
    Given: AssistantMessage(content=[
        TextBlock(text="Part 1 "),
        TextBlock(text="Part 2")
    ])
    When: 调用 extract_text_from_messages
    Then: 返回 "Part 1 Part 2"
    """
    pass  # TODO: 实现

# Test B3: ThinkingBlock 应被跳过
def test_thinking_block_skipped():
    """
    Given: AssistantMessage(content=[
        ThinkingBlock(thinking="Internal thought", signature="sig"),
        TextBlock(text="Actual response")
    ])
    When: 调用 extract_text_from_messages
    Then: 返回 "Actual response"
    """
    pass  # TODO: 实现

# Test B4: ToolUseBlock 处理
def test_tool_use_block_handling():
    """
    Given: AssistantMessage(content=[
        TextBlock(text="Using tool..."),
        ToolUseBlock(name="create_deliverable", input={"title": "Test"}, id="123")
    ])
    When: 调用 extract_text_from_messages
    Then: 返回包含 tool_use 信息的 dict 列表
    """
    pass  # TODO: 实现
```

#### 测试组 C: 边界条件和回退逻辑

```python
# Test C1: 旧格式兼容（有 role 属性的 dict）
def test_backward_compatibility_with_role_attr():
    """
    Given: {"role": "assistant", "content": [{"type": "text", "text": "Legacy"}]}
    When: 调用 extract_text_from_messages
    Then: 返回 "Legacy"
    """
    pass  # TODO: 实现

# Test C2: 字符串 content 处理
def test_string_content_handling():
    """
    Given: AssistantMessage(content="Direct string", model="kimi")
    When: 调用 extract_text_from_messages
    Then: 返回 "Direct string"
    """
    pass  # TODO: 实现

# Test C3: extract_text() 方法优先
def test_extract_text_method_priority():
    """
    Given: AssistantMessage 有 extract_text() 方法
    When: 调用 extract_text_from_messages
    Then: 优先使用 extract_text() 方法返回值
    """
    pass  # TODO: 实现
```

### 3.2 单元测试 - `test_session_manager_message_conversion.py`

#### 测试组 D: `_message_to_dict` 修复

```python
# Test D1: AssistantMessage 转 dict
def test_assistant_message_to_dict():
    """
    Given: AssistantMessage(content=[TextBlock(text="Hi")], model="kimi")
    When: 调用 _message_to_dict(msg)
    Then: 返回 {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]}
    """
    pass  # TODO: 实现

# Test D2: UserMessage 转 dict
def test_user_message_to_dict():
    """
    Given: UserMessage(content="User input")
    When: 调用 _message_to_dict(msg)
    Then: 返回 {"role": "user", "content": [{"type": "text", "text": "User input"}]}
    """
    pass  # TODO: 实现

# Test D3: SystemMessage 应被过滤
def test_system_message_filtered():
    """
    Given: SystemMessage(subtype="init", data={})
    When: 调用 _message_to_dict(msg)
    Then: 返回 None
    """
    pass  # TODO: 实现

# Test D4: ResultMessage 应被过滤
def test_result_message_filtered():
    """
    Given: ResultMessage(result="Final", is_error=False)
    When: 调用 _message_to_dict(msg)
    Then: 返回 None
    """
    pass  # TODO: 实现

# Test D5: ContentBlock 类型转换
def test_content_block_conversion():
    """
    Given: AssistantMessage(content=[
        TextBlock(text="Hello"),
        ToolUseBlock(name="tool", input={}, id="1"),
        ToolResultBlock(tool_use_id="1", content="Result", is_error=False)
    ])
    When: 调用 _message_to_dict(msg)
    Then: content 列表包含正确类型的 dict
    """
    pass  # TODO: 实现
```

### 3.3 单元测试 - `test_independent_agent_message_handling.py`

#### 测试组 E: Agent 消息处理

```python
# Test E1: _call_llm_with_prompts 消息收集
def test_call_llm_message_collection():
    """
    Given: session.prompt() 返回混合类型消息流
    When: 调用 _call_llm_with_prompts
    Then: 正确收集所有 AssistantMessage，过滤其他类型
    """
    pass  # TODO: 实现

# Test E2: 无消息返回时抛出 LLMCallError
def test_no_messages_raises_error():
    """
    Given: session.prompt() 返回空流
    When: 调用 _call_llm_with_prompts
    Then: 抛出 LLMCallError("No messages returned from session")
    """
    pass  # TODO: 实现

# Test E3: _extract_content_from_messages 修复
def test_extract_content_from_converted_messages():
    """
    Given: messages 包含 _message_to_dict 转换后的 dict
    When: 调用 _extract_content_from_messages
    Then: 正确提取文本内容
    """
    pass  # TODO: 实现
```

### 3.4 集成测试 - `test_sdk_integration.py`

```python
# Test I1: 完整 single_prompt 流程
@pytest.mark.asyncio
async def test_single_prompt_end_to_end():
    """
    Given: 配置好的 SessionManager
    When: 调用 single_prompt("Hello")
    Then: 返回非空消息列表，包含 assistant role 消息
    """
    pass  # TODO: 实现

# Test I2: Session prompt 流式接收
@pytest.mark.asyncio
async def test_session_prompt_streaming():
    """
    Given: 创建的 session
    When: 调用 session.prompt("Hello") 并遍历
    Then: 正确接收并处理所有消息类型
    """
    pass  # TODO: 实现

# Test I3: IndependentAgent 完整执行
@pytest.mark.asyncio
async def test_independent_agent_execution():
    """
    Given: 配置好的 IndependentAgent 和 mock LLM 响应
    When: 调用 execute(context)
    Then: 返回有效的 IndependentOutput，包含 deliverable 和 questions
    """
    pass  # TODO: 实现
```

### 3.5 端到端测试 - `test_pipeline_e2e.py`

```python
# Test E2E1: 完整 pipeline 执行
@pytest.mark.asyncio
@pytest.mark.e2e
async def test_full_pipeline_with_kimi():
    """
    Given: 有效的 context 文件和配置
    When: 执行 python -m autoBMAD.docuswarm start --context docs/bubble-sort/bubble-sort-context.md
    Then: 
        - pipeline 完成无错误
        - 生成预期的 .md 交付物
        - 日志无 no_text_extracted 警告
    """
    pass  # TODO: 实现
```

---

## 4. 实现步骤（按优先级）

### Phase 1: 核心修复（P0 - 阻断性）

#### Step 1.1: 修复 `session_manager.py` 的 `_message_to_dict`

```python
# 文件: autoBMAD/docuswarm/llm/session_manager.py
# 添加导入
from claude_agent_sdk.types import AssistantMessage, UserMessage, SystemMessage

def _message_to_dict(self, msg: Any) -> dict[str, Any] | None:
    """Convert SDK message to dict format.
    
    Fix: 使用 isinstance 判断消息类型，而非依赖 role 属性。
    """
    if msg is None:
        return None

    # If it's already a dict, return it
    if isinstance(msg, dict):
        return msg

    # Handle ResultMessage - skip it (it's metadata)
    if isinstance(msg, ResultMessage):
        return None

    # Handle SystemMessage - skip it (subtype='init', etc.)
    if isinstance(msg, SystemMessage):
        return None

    # Fix: 使用 isinstance 判断消息类型，而非 getattr(msg, "role", None)
    if isinstance(msg, AssistantMessage):
        role = "assistant"
    elif isinstance(msg, UserMessage):
        role = "user"
    else:
        # Fallback: 尝试获取 role 属性（兼容旧格式）
        role = getattr(msg, "role", None)
        if role is None:
            return None

    content = getattr(msg, "content", None)
    
    # Convert content to list format...
    # [保持原有逻辑，但使用 isinstance 检查 content items]
```

#### Step 1.2: 修复 `response.py` 的 `extract_text_from_messages`

```python
# 文件: autoBMAD/docuswarm/llm/response.py
# 添加导入
from claude_agent_sdk.types import AssistantMessage, TextBlock, ThinkingBlock

def extract_text_from_messages(messages: list[MessageLike]) -> str:
    """Extract text content from the last assistant Message.
    
    Fix: 使用 isinstance 判断 AssistantMessage，而非 role 属性。
    """
    import structlog
    logger = structlog.get_logger(__name__)
    
    logger.debug("extract_text_debug", total_messages=len(messages))

    for idx, msg in enumerate(reversed(messages)):
        # Fix: 优先使用 isinstance 检查，fallback 到 role 字符串
        is_assistant = isinstance(msg, AssistantMessage)
        if not is_assistant:
            # Fallback: 检查 role 属性（兼容旧格式）
            msg_role = getattr(msg, "role", "")
            if msg_role != "assistant":
                logger.debug("skip_message", reason=f"not_assistant")
                continue
        
        msg_content: Any = getattr(msg, "content", None)
        # ... 后续内容提取逻辑
```

#### Step 1.3: 修复 ContentBlock 类型判断

```python
# 在 _message_to_dict 和 extract_text_from_messages 中

from claude_agent_sdk.types import TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock

# 修复前（错误）
item_type = getattr(item, "type", "text")
if item_type == "text": ...

# 修复后（正确）
if isinstance(item, TextBlock):
    converted_content.append({"type": "text", "text": item.text})
elif isinstance(item, ThinkingBlock):
    # ThinkingBlock 无 text 属性，根据需求跳过或转换
    pass
elif isinstance(item, ToolUseBlock):
    converted_content.append({
        "type": "tool_use",
        "name": item.name,
        "input": item.input,
        "id": item.id,
    })
elif isinstance(item, ToolResultBlock):
    converted_content.append({
        "type": "tool_result",
        "tool_use_id": item.tool_use_id,
        "content": item.content,
        "is_error": getattr(item, "is_error", False),
    })
```

### Phase 2: Agent 层修复（P1 - 高优先级）

#### Step 2.1: 修复 `independent.py` 的消息处理

```python
# 文件: autoBMAD/docuswarm/agents/independent.py
# 在 _call_llm_with_prompts 方法中

async for msg in session.prompt(user_prompt):
    message_count += 1
    
    if isinstance(msg, dict):
        messages.append(msg)
    else:
        # Fix: 使用 SessionManager._message_to_dict 进行转换
        # 而非直接 getattr
        msg_dict = self.session_manager._message_to_dict(msg)
        if msg_dict:
            messages.append(msg_dict)
```

#### Step 2.2: 修复 `_extract_content_from_messages`

```python
# 文件: autoBMAD/docuswarm/agents/independent.py

def _extract_content_from_messages(self, messages: list[dict[str, Any]]) -> str:
    """Extract text content from messages.
    
    Fix: 确保与 _message_to_dict 输出格式兼容。
    """
    for msg in reversed(messages):
        content = msg.get("content", [])
        if content:
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                texts = []
                for part in content:
                    # content 已由 _message_to_dict 转换为 dict
                    if isinstance(part, dict) and part.get("type") == "text":
                        texts.append(part.get("text", ""))
                return " ".join(texts)
    return ""
```

### Phase 3: 测试验证（所有测试通过）

#### Step 3.1: 运行单元测试

```bash
# 测试 response.py 修复
python -m pytest tests/llm/test_response_message_extraction.py -v

# 测试 session_manager.py 修复
python -m pytest tests/llm/test_session_manager_message_conversion.py -v

# 测试 independent.py 修复
python -m pytest tests/agents/test_independent_agent_message_handling.py -v
```

#### Step 3.2: 运行集成测试

```bash
# 测试 SDK 集成
python -m pytest tests/integration/test_sdk_integration.py -v
```

#### Step 3.3: 运行端到端测试

```bash
# 完整 pipeline 测试
python -m pytest tests/e2e/test_pipeline_e2e.py -v --e2e
```

---

## 5. 测试固件（Fixtures）

### 5.1 SDK 消息模拟

```python
# tests/conftest.py

import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class MockTextBlock:
    """模拟 SDK 的 TextBlock"""
    text: str
    # 注意：无 type 属性

@dataclass
class MockThinkingBlock:
    """模拟 SDK 的 ThinkingBlock"""
    thinking: str
    signature: str
    # 注意：无 type 属性

@dataclass
class MockToolUseBlock:
    """模拟 SDK 的 ToolUseBlock"""
    name: str
    input: dict[str, Any]
    id: str

@dataclass
class MockToolResultBlock:
    """模拟 SDK 的 ToolResultBlock"""
    tool_use_id: str
    content: str | list[dict[str, Any]]
    is_error: bool = False

@dataclass
class MockAssistantMessage:
    """模拟 SDK 的 AssistantMessage - 无 role 属性"""
    content: list[Any]
    model: str = "kimi"
    parent_tool_use_id: Optional[str] = None
    error: Optional[Any] = None
    # 注意：无 role 属性

@dataclass
class MockUserMessage:
    """模拟 SDK 的 UserMessage - 无 role 属性"""
    content: str | list[Any]
    # 注意：无 role 属性

@dataclass
class MockSystemMessage:
    """模拟 SDK 的 SystemMessage"""
    subtype: str
    data: dict[str, Any] = field(default_factory=dict)
    # 注意：无 role 属性

@dataclass
class MockResultMessage:
    """模拟 SDK 的 ResultMessage"""
    result: str
    is_error: bool = False
    duration_ms: int = 0
    num_turns: int = 0
    session_id: str = ""
    structured_output: Optional[dict] = None

@pytest.fixture
def sdk_message_factory():
    """工厂函数，创建各种 SDK 消息用于测试"""
    def factory(message_type: str, **kwargs):
        factories = {
            "assistant": MockAssistantMessage,
            "user": MockUserMessage,
            "system": MockSystemMessage,
            "result": MockResultMessage,
            "text_block": MockTextBlock,
            "thinking_block": MockThinkingBlock,
            "tool_use": MockToolUseBlock,
            "tool_result": MockToolResultBlock,
        }
        return factories[message_type](**kwargs)
    return factory

@pytest.fixture
def sample_assistant_message():
    """示例 AssistantMessage，包含 TextBlock"""
    return MockAssistantMessage(
        content=[MockTextBlock(text="Hello from Kimi!")],
        model="kimi"
    )

@pytest.fixture
def sample_mixed_content_message():
    """包含多种 content block 的 AssistantMessage"""
    return MockAssistantMessage(
        content=[
            MockThinkingBlock(thinking="Let me think...", signature="sig123"),
            MockTextBlock(text="Here is my response."),
            MockToolUseBlock(name="create_deliverable", input={"title": "Test"}, id="tool_1"),
        ],
        model="kimi"
    )
```

### 5.2 异步迭代器模拟

```python
# tests/conftest.py

class AsyncIteratorMock:
    """模拟异步迭代器，用于测试 session.prompt()"""
    
    def __init__(self, items: list[Any]):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item

@pytest.fixture
def mock_session_prompt():
    """创建 mock 的 session.prompt 方法"""
    def create_mock(messages: list[Any]):
        async def mock_prompt(*args, **kwargs):
            return AsyncIteratorMock(messages)
        return mock_prompt
    return create_mock
```

---

## 6. 验证清单

### 6.1 功能验证

- [ ] `extract_text_from_messages` 能正确处理 `AssistantMessage`（无 role 属性）
- [ ] `extract_text_from_messages` 能正确处理 `TextBlock`（无 type 属性）
- [ ] `_message_to_dict` 能正确识别 `AssistantMessage` 并设置 role="assistant"
- [ ] `_message_to_dict` 能正确识别 `UserMessage` 并设置 role="user"
- [ ] `_message_to_dict` 正确过滤 `SystemMessage` 和 `ResultMessage`
- [ ] `single_prompt` 返回非空消息列表
- [ ] `session.prompt()` 的消息能被正确收集和转换
- [ ] `IndependentAgent.execute()` 成功返回 `deliverable` 和 `questions`
- [ ] 完整 pipeline 执行后生成预期的 `.md` 文件

### 6.2 回归验证

- [ ] 旧格式（带 role 属性的 dict）消息仍被正确处理
- [ ] 字符串 content 仍被正确处理
- [ ] 空 content 列表不会导致崩溃
- [ ] 仅包含 ThinkingBlock 的消息返回空字符串（而非崩溃）
- [ ] 包含 ToolUseBlock 的消息正确提取文本

### 6.3 日志验证

- [ ] 无 `no_text_extracted` warning（正常响应时）
- [ ] `single_prompt_complete` 显示 `message_count > 0`
- [ ] `llm_prompt_complete` 显示正确的消息统计
- [ ] Pipeline 完成日志包含 `independent_agent_completed`

---

## 7. 风险与回滚

### 7.1 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| SDK 类型导入失败 | 低 | 高 | 使用 try/except 包装导入，提供 fallback |
| isinstance 检查与旧 SDK 不兼容 | 中 | 中 | 保持 getattr fallback 逻辑 |
| 性能下降（类型检查） | 低 | 低 | 类型检查是 O(1) 操作，影响可忽略 |

### 7.2 回滚方案

```bash
# 如果修复导致问题，快速回滚
git revert HEAD  # 假设修复是一个 commit

# 或者使用 feature flag（如果需要）
export DOCUSWARM_USE_ISINSTANCE_CHECK=false  # 回退到旧逻辑
```

---

## 8. 时间线

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|----------|--------|
| Day 1 AM | 编写失败测试（Red）| 2h | Developer |
| Day 1 PM | 实现 Phase 1 修复 | 3h | Developer |
| Day 2 AM | 实现 Phase 2 修复 | 2h | Developer |
| Day 2 PM | 运行所有测试，验证通过 | 3h | Developer |
| Day 3 AM | E2E 测试，回归验证 | 2h | QA |
| Day 3 PM | 文档更新，代码审查 | 2h | Team |

---

## 9. 附录

### 9.1 SDK 类型参考

```python
# claude_agent_sdk.types (v0.1.68)

@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None

@dataclass
class UserMessage:
    content: str | list[ContentBlock]

@dataclass
class SystemMessage:
    subtype: str
    data: dict = field(default_factory=dict)

@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    result: str
    structured_output: dict | None = None

@dataclass
class TextBlock:
    text: str

@dataclass
class ThinkingBlock:
    thinking: str
    signature: str

ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
```

### 9.2 官方文档示例

```python
# 来自 agentdocs/05_python.md

from claude_agent_sdk.types import AssistantMessage, TextBlock, ToolUseBlock

async for message in query(prompt=prompt, options=opts):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock):
                print(f"Using tool: {block.name}")
            if isinstance(block, TextBlock):
                print(f"Text: {block.text}")
```

---

*方案版本: 1.0*  
*最后更新: 2026-04-06*  
*状态: 待实施*

# DocuSwarm Message 格式完全移除报告

> **奥卡姆剃刀原则**: 如无必要，勿增实体  
> **决策**: 完全移除 kimi-agent-sdk Message，使用 Claude SDK 格式  
> **研究日期**: 2026-03-02  
> **主题**: 从 kimi-agent-sdk Message 格式迁移到 Claude SDK 格式

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [当前 Message 格式分析](#2-当前-message-格式分析)
3. [目标 Message 格式](#3-目标-message-格式)
4. [完全移除方案](#4-完全移除方案)
5. [代码迁移示例](#5-代码迁移示例)
6. [文件修改清单](#6-文件修改清单)
7. [风险评估](#7-风险评估)
8. [测试策略](#8-测试策略)
9. [结论](#9-结论)

---

## 1. 执行摘要

### 1.1 目标

完全移除 DocuSwarm 项目中 `kimi-agent-sdk` 的 Message 格式依赖。

### 1.2 关键发现

| 维度 | 评估 |
|-----|------|
| **格式差异程度** | 🔴 高 - 两种完全不同的数据模型 |
| **影响文件数** | 23 个文件 |
| **核心依赖点** | 4 个（独立Agent、评估Agent、工具提取器、上下文摘要器）|
| **迁移复杂度** | 🔴 高 |
| **策略** | **完全移除，无适配层** |

### 1.3 决策

**不使用适配器，完全移除**:
- ❌ 不创建 UnifiedMessage 适配层
- ❌ 不保留 Kimi 格式支持
- ❌ 不提供向后兼容
- ✅ 直接使用 Claude SDK 格式
- ✅ 所有代码统一到新格式

---

## 2. 当前 Message 格式分析

### 2.1 Kimi SDK Message 使用位置

```python
# agents/independent.py (将被移除)
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator

async def _call_llm_via_session(self, user_message: str) -> list[Message]:
    messages: list[Any] = []
    aggregator: MessageAggregator = MessageAggregator()
    
    async for wire_msg in session.prompt(full_prompt):
        for msg in aggregator.feed(wire_msg):
            messages.append(msg)
    
    return messages
```

```python
# agents/evaluator.py (将被移除)
from kimi_agent_sdk import Message

async def _call_llm(...) -> list[Message]:
    sdk_response: list[Message] = await self.session_manager.single_prompt(...)
    return sdk_response
```

### 2.2 Kimi Message 使用统计

| 文件 | Message 类型使用 | 操作 |
|-----|-----------------|------|
| `agents/independent.py` | `Message`, `MessageAggregator` | **完全移除** |
| `agents/evaluator.py` | `Message` | **完全移除** |
| `tools/tool_result_extractor.py` | Kimi 格式兼容 | **完全移除** |
| `pipeline/context_summarizer.py` | `list[dict]` | **已符合新格式** |

---

## 3. 目标 Message 格式

### 3.1 Claude SDK ResultMessage 结构

```python
# Claude SDK 格式

@dataclass
class SDKResult:
    """Claude SDK 执行结果"""
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any]
    tool_calls: list[dict]
```

### 3.2 SessionManager 返回格式

```python
# llm/session_manager.py

class SessionManager:
    async def single_prompt(...) -> list[dict[str, Any]]:
        """返回 dict 列表"""
        result = await self._sdk_wrapper.execute(...)
        
        messages: list[dict[str, Any]] = []
        for msg in result.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        return messages
```

---

## 4. 完全移除方案

### 4.1 差异对比

| 特性 | Kimi SDK (移除) | Claude SDK (新) |
|-----|----------------|-----------------|
| **基础类型** | `Message` 类 | `ResultMessage` + Block |
| **content 类型** | `str \| list[ContentPart]` | `list[Block]` |
| **工具调用表示** | `ContentPart(type="tool_use")` | `ToolUseBlock` |
| **流式处理** | `WireMessage` + `MessageAggregator` | `AsyncIterator[ResultMessage]` |
| **错误表示** | 异常抛出 | `is_error` 字段 |

### 4.2 移除内容清单

**完全移除（无替代）**:
- `kimi_agent_sdk.Message` 类导入
- `kimi_agent_sdk._aggregator.MessageAggregator` 导入
- `WireMessage` 处理逻辑
- `MessageAggregator.feed()` 调用
- `MessageAggregator.flush()` 调用

**替换为 Claude SDK**:
- `list[Message]` → `list[dict[str, Any]]`
- `MessageAggregator` 流式处理 → `SDKResult.messages`

---

## 5. 代码迁移示例

### 5.1 IndependentAgent 迁移

```python
# BEFORE: 完全移除

from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator

async def _call_llm_via_session(self, user_message: str) -> list[Message]:
    messages: list[Any] = []
    aggregator: MessageAggregator = MessageAggregator()
    
    async for wire_msg in session.prompt(full_prompt):
        for msg in aggregator.feed(wire_msg):
            messages.append(msg)
    
    return messages

def _parse_response(self, response: list[Message]) -> IndependentOutput:
    extractor = ToolResultExtractor()
    metadata_list = extractor.extract_from_messages(response)
    ...
```

```python
# AFTER: 新实现

from autoBMAD.docuswarm.llm.response import ResponseMessage

async def _call_llm_via_session(self, user_message: str) -> list[dict[str, Any]]:
    """使用 Claude SDK 直接返回结果"""
    result = await self._session_manager.execute(prompt=full_prompt)
    return result.messages

def _parse_response(self, response: list[dict[str, Any]]) -> IndependentOutput:
    """使用 dict 格式解析"""
    extractor = ToolResultExtractor()
    metadata_list = extractor.extract_from_dicts(response)
    ...
```

### 5.2 ToolResultExtractor 迁移

```python
# BEFORE: 完全移除

def extract_from_messages(self, messages: list[Any]) -> list[DeliverableMetadata]:
    results: list[DeliverableMetadata] = []
    
    for message in messages:
        # 移除 Kimi 格式支持
        kimi_result = self._extract_kimi_format(message)
        if kimi_result:
            results.extend(kimi_result)
            continue
        
        claude_result = self.extract_claude_tool_use_block(message)
        if claude_result:
            results.extend(claude_result)
    
    return results
```

```python
# AFTER: 仅支持 Claude 格式

def extract_from_dicts(
    self, 
    messages: list[dict[str, Any]]
) -> list[DeliverableMetadata]:
    """仅支持 dict 格式提取"""
    results: list[DeliverableMetadata] = []
    
    for message in messages:
        content = message.get("content", [])
        
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    tool_name = block.get("name", "")
                    params = block.get("input", {})
                    metadata = self.parse_tool_params(tool_name, params)
                    results.extend(metadata)
    
    return results
```

---

## 6. 文件修改清单

| 优先级 | 文件 | 修改类型 | 说明 |
|-------|------|---------|------|
| 🔴 高 | `agents/independent.py` | 修改 | 移除 Message/MessageAggregator |
| 🔴 高 | `agents/evaluator.py` | 修改 | 移除 Message 导入 |
| 🔴 高 | `llm/session_manager.py` | 修改 | 统一返回 dict 列表 |
| 🔴 高 | `tools/tool_result_extractor.py` | 重构 | 移除 Kimi 格式支持 |
| 🟡 中 | `pipeline/context_summarizer.py` | 验证 | 确认已使用新格式 |
| 🔴 高 | `tests/conftest.py` | 修改 | 移除 Message mock |
| 🔴 高 | 所有测试文件 | 更新 | 使用新格式 |

---

## 7. 风险评估

### 7.1 技术风险矩阵

| 风险项 | 概率 | 影响 | 等级 | 缓解措施 |
|-------|------|------|------|---------|
| content 类型转换错误 | 高 | 高 | 🔴 极高 | 全面单元测试 |
| 工具调用信息丢失 | 中 | 高 | 🔴 高 | 集成测试覆盖 |
| 流式消息顺序错乱 | 中 | 中 | 🟡 中 | 消息序列验证 |
| 性能下降 | 低 | 中 | 🟢 低 | 基准测试 |

### 7.2 关键风险点

**风险: Content 类型多样性**

Kimi SDK 中 `Message.content` 可以是 `str`、`list[ContentPart]` 或 `None`。

**缓解**: 新代码统一使用 `list[dict]` 格式，通过类型检查确保一致性。

---

## 8. 测试策略

### 8.1 单元测试

```python
# tests/unit/test_message_format.py

import pytest
from autoBMAD.docuswarm.tools.tool_result_extractor import ToolResultExtractor


class TestMessageFormat:
    """Message 格式单元测试"""
    
    def test_extract_from_dicts(self):
        """测试 dict 格式提取"""
        extractor = ToolResultExtractor()
        
        messages = [
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Creating deliverable"},
                    {
                        "type": "tool_use",
                        "name": "create_deliverable",
                        "input": {"title": "Test", "content": "Content"}
                    }
                ]
            }
        ]
        
        result = extractor.extract_from_dicts(messages)
        assert len(result) == 1
        assert result[0].title == "Test"
```

### 8.2 集成测试

```python
# tests/integration/test_message_flow.py

import pytest


class TestMessageFlow:
    """消息流集成测试"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_message_flow(self):
        """测试端到端消息流"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir="/tmp/test")
        
        # 执行 prompt
        messages = await sm.single_prompt("Test prompt")
        
        # 验证返回格式
        assert isinstance(messages, list)
        assert all(isinstance(m, dict) for m in messages)
        assert all("role" in m for m in messages)
        assert all("content" in m for m in messages)
```

---

## 9. 结论

### 9.1 结论

1. **Message 格式差异是迁移的核心难点**：Kimi 和 Claude SDK 的 Message 模型差异显著。

2. **完全移除是最佳方案**：通过直接替换，避免维护适配层的技术债务。

3. **迁移需要 4 周左右**：包括代码修改和测试更新。

4. **风险可控但需要充分测试**：content 类型转换是风险点。

### 9.2 建议

**立即执行**:
1. 在独立分支上开始移除工作
2. 编写完整的单元测试
3. 分模块逐步替换

**监控指标**:
- 工具调用提取成功率
- 端到端测试通过率
- 性能指标（延迟、内存）

---

*报告完成日期: 2026-03-02*  
*文档版本: 2.0 (完全移除版)*

# Epic 17: Message Format Migration

> **⚠️ 完全移除**: 本 Epic 完全移除 `kimi-agent-sdk` Message 格式，使用 Claude SDK 格式  
> **决策**: 零向后兼容，完全移除，无适配层  
> **参考**: [Message 格式迁移研究报告](../research/migration/01-message-format-migration-report.md)

**Epic ID**: EPIC-17  
**Version**: 1.0 (完全移除版)  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 2 (Kimi SDK Removal)

---

## 1. Epic Overview

### 1.1 Summary

**完全移除** `kimi-agent-sdk` 的 `Message` 类和 `MessageAggregator` 类，将 DocuSwarm 项目中所有 Message 格式迁移到 `dict[str, Any]` 格式。这是 Kimi SDK 完全移除的核心步骤之一。

### 1.2 Business Value

- **完全移除 Kimi SDK**: 消除对 `kimi_agent_sdk.Message` 的依赖
- **统一数据格式**: 使用标准 Python dict 替代自定义类
- **简化代码**: 移除 `MessageAggregator` 流式处理复杂性
- **架构一致性**: 与 Claude SDK 结果格式保持一致

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Kimi Message 移除 | 项目中无 `kimi_agent_sdk.Message` 导入 |
| MessageAggregator 移除 | 项目中无 `MessageAggregator` 使用 |
| 格式统一 | 所有消息处理使用 `list[dict[str, Any]]` |
| 功能保持 | 所有现有功能正常工作 |

### 1.4 Dependencies

- **Requires**: Epic 16 (SDK Wrapper) completed
- **Blocks**: Epic 18 (Tool Migration)

---

## 2. Architecture Context

### 2.1 Migration Overview

```
Before (v4.x - 迁移中):
  ┌─────────────────────────────────────────────────────────────┐
  │  Kimi SDK Message Format                                    │
  │  ┌─────────────┐    ┌──────────────────┐                   │
  │  │ Message     │    │ MessageAggregator │                  │
  │  │ (class)     │    │ (Wire→Message)    │                  │
  │  └──────┬──────┘    └────────┬─────────┘                   │
  │         │                    │                             │
  │         ▼                    ▼                             │
  │  ┌──────────────────────────────────────┐                 │
  │  │ list[Message]                        │                 │
  │  └──────────────────────────────────────┘                 │
  └─────────────────────────────────────────────────────────────┘

After (v5.0 - 完全移除):
  ┌─────────────────────────────────────────────────────────────┐
  │  Claude SDK Format (dict)                                   │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │ SDKResult.messages → list[dict[str, Any]]            │  │
  │  │                                                      │  │
  │  │ [{"role": "assistant", "content": [...]}, ...]       │  │
  │  └──────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Changes

| 组件 | 当前 (Kimi SDK) | 目标 (Claude SDK) |
|------|----------------|-------------------|
| Message 类型 | `kimi_agent_sdk.Message` | `dict[str, Any]` |
| 消息聚合 | `MessageAggregator` | 直接返回 `SDKResult.messages` |
| 流式处理 | `WireMessage` + 聚合 | `AsyncIterator[ResultMessage]` |
| 返回格式 | `list[Message]` | `list[dict[str, Any]]` |

### 2.3 Key Files

| File | Operation | Purpose |
|------|-----------|---------|
| `docuswarm/agents/independent.py` | **MODIFY** | 移除 Message/MessageAggregator 导入 |
| `docuswarm/agents/evaluator.py` | **MODIFY** | 移除 Message 导入，改用 dict |
| `docuswarm/llm/session_manager.py` | **MODIFY** | 统一返回 dict 列表 |
| `docuswarm/tools/tool_result_extractor.py` | **MODIFY** | 移除 Kimi 格式支持 |
| `docuswarm/llm/response.py` | **VERIFY** | 确认已使用新格式 |

---

## 3. User Stories

### Story 17.1: IndependentAgent Message Migration

**ID**: US-17.1  
**As a** developer  
**I want to** remove Kimi SDK Message from IndependentAgent  
**So that** it uses standard dict format for message handling

**Acceptance Criteria**:
- [ ] 移除 `from kimi_agent_sdk import Message` 导入
- [ ] 移除 `from kimi_agent_sdk._aggregator import MessageAggregator` 导入
- [ ] `_call_llm_via_session()` 返回 `list[dict[str, Any]]` 而非 `list[Message]`
- [ ] `_parse_response()` 使用 dict 格式解析
- [ ] 移除 `MaxStepsReached` 和 `RunCancelled` 异常导入（移至 Story 20）

**Technical Tasks**:
1. 修改 `docuswarm/agents/independent.py` 导入部分
2. 修改 `_call_llm_via_session()` 返回类型和实现
3. 修改 `_parse_response()` 处理 dict 格式
4. 更新相关类型提示
5. 更新单元测试

**Before/After**:

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

**Definition of Done**:
- IndependentAgent 无 Kimi SDK Message 导入
- 所有消息处理使用 dict 格式
- 单元测试通过
- 集成测试通过

---

### Story 17.2: EvaluatorAgent Message Migration

**ID**: US-17.2  
**As a** developer  
**I want to** remove Kimi SDK Message from EvaluatorAgent  
**So that** it uses standard dict format for message handling

**Acceptance Criteria**:
- [ ] 移除 `from kimi_agent_sdk import Message` 导入
- [ ] `_call_llm()` 返回 `list[dict[str, Any]]` 而非 `list[Message]`
- [ ] `_parse_response()` 使用 dict 格式解析
- [ ] 处理 `content` 字段的多种类型（str, list）

**Technical Tasks**:
1. 修改 `docuswarm/agents/evaluator.py` 导入部分
2. 修改 `_call_llm()` 返回类型
3. 修改 `_parse_response()` 处理 dict 格式
4. 更新相关类型提示
5. 更新单元测试

**Before/After**:

```python
# BEFORE: 完全移除

from kimi_agent_sdk import Message

async def _call_llm(...) -> list[Message]:
    sdk_response: list[Message] = await self.session_manager.single_prompt(...)
    return sdk_response

def _parse_response(self, response: list[Message]) -> dict[str, Any]:
    # 处理 Message 对象
    for msg in reversed(response):
        if msg.role == "assistant" and msg.content:
            content_raw = msg.content
            break
```

```python
# AFTER: 新实现

async def _call_llm(...) -> list[dict[str, Any]]:
    result = await self.session_manager.single_prompt(...)
    return result

def _parse_response(self, response: list[dict[str, Any]]) -> dict[str, Any]:
    # 处理 dict 格式
    for msg in reversed(response):
        if msg.get("role") == "assistant":
            content_raw = msg.get("content")
            break
```

**Definition of Done**:
- EvaluatorAgent 无 Kimi SDK Message 导入
- 所有消息处理使用 dict 格式
- 单元测试通过
- 集成测试通过

---

### Story 17.3: SessionManager Return Format Update

**ID**: US-17.3  
**As a** developer  
**I want to** update SessionManager to return dict format  
**So that** all agents receive consistent message format

**Acceptance Criteria**:
- [ ] `single_prompt()` 返回 `list[dict[str, Any]]`
- [ ] `execute_with_tools()` 返回结果中的 messages 为 dict 格式
- [ ] 消息格式包含 `role` 和 `content` 字段
- [ ] 处理 content 字段的多种类型（str, list）

**Technical Tasks**:
1. 修改 `docuswarm/llm/session_manager.py`
2. 更新 `single_prompt()` 返回类型
3. 更新 `execute_with_tools()` 返回类型
4. 实现 `Message` 到 `dict` 的转换逻辑
5. 更新单元测试

**API Design**:

```python
# docuswarm/llm/session_manager.py

class SessionManager:
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
    ) -> list[dict[str, Any]]:
        """返回 dict 列表格式的消息"""
        result = await self._sdk_wrapper.execute(...)
        
        # 转换为 dict 格式
        messages: list[dict[str, Any]] = []
        for msg in result.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        return messages
```

**Definition of Done**:
- SessionManager 返回 dict 格式
- 所有调用方正常工作
- 单元测试通过

---

### Story 17.4: ToolResultExtractor Migration

**ID**: US-17.4  
**As a** developer  
**I want to** update ToolResultExtractor to work with dict format  
**So that** it extracts deliverables from new message format

**Acceptance Criteria**:
- [ ] 添加 `extract_from_dicts()` 方法
- [ ] 移除 Kimi 格式兼容代码
- [ ] 支持从 dict 中提取 tool_use block
- [ ] 所有现有提取功能正常工作

**Technical Tasks**:
1. 修改 `docuswarm/tools/tool_result_extractor.py`
2. 添加 `extract_from_dicts()` 方法
3. 移除 `_extract_kimi_format()` 方法
4. 更新所有调用方使用新方法
5. 更新单元测试

**Before/After**:

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
# AFTER: 新实现

def extract_from_dicts(
    self, 
    messages: list[dict[str, Any]]
) -> list[DeliverableMetadata]:
    """仅从 dict 格式提取"""
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

**Definition of Done**:
- ToolResultExtractor 支持 dict 格式
- 所有提取功能正常工作
- 单元测试通过

---

## 4. Technical Specifications

### 4.1 Modified Modules

| Module | Location | Changes |
|--------|----------|---------|
| `IndependentAgent` | `docuswarm/agents/independent.py` | 移除 Message 导入，使用 dict |
| `EvaluatorAgent` | `docuswarm/agents/evaluator.py` | 移除 Message 导入，使用 dict |
| `SessionManager` | `docuswarm/llm/session_manager.py` | 返回 dict 格式 |
| `ToolResultExtractor` | `docuswarm/tools/tool_result_extractor.py` | 添加 dict 支持 |

### 4.2 Message Dict Format

```python
# 标准消息 dict 格式

{
    "role": "assistant",  # "user" | "assistant" | "system"
    "content": [
        {"type": "text", "text": "..."},
        {
            "type": "tool_use",
            "name": "create_deliverable",
            "input": {"title": "...", "content": "..."},
            "id": "call_123"
        }
    ]
}
```

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/` | 100% pass |
| Integration tests | `pytest tests/integration/` | Pass |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Content 类型转换错误 | 高 | 高 | 全面单元测试覆盖所有 content 类型 |
| 工具调用信息丢失 | 中 | 高 | 集成测试验证工具调用提取 |
| 消息顺序错乱 | 低 | 中 | 消息序列验证测试 |
| 性能下降 | 低 | 低 | 基准测试监控 |

---

## 6. Definition of Done (Epic Level)

- [ ] 所有 Story 完成并测试通过
- [ ] 项目中无 `kimi_agent_sdk.Message` 导入
- [ ] 项目中无 `MessageAggregator` 使用
- [ ] 所有消息处理使用 `list[dict[str, Any]]` 格式
- [ ] IndependentAgent 使用新格式
- [ ] EvaluatorAgent 使用新格式
- [ ] ToolResultExtractor 使用新格式
- [ ] SessionManager 返回新格式
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 类型检查通过
- [ ] Linting 通过

---

## 7. References

| Document | Location |
|----------|----------|
| Message 格式迁移报告 | `docs/research/migration/01-message-format-migration-report.md` |
| Epic 16 SDK Wrapper | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |
| LLM Integration | `docs/architecture/05_LLM_INTEGRATION.md` |

---

**Epic End**

# Epic 14: Tool Result Extractor（纯工具输出模式）

**Epic ID**: EPIC-14  
**关联方案**: [TDD-03-ToolResultExtractor-Refactor.md](../solution/TDD-03-ToolResultExtractor-Refactor.md)  
**Version**: 1.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days  
**Priority**: P1 - 重要

---

## 1. Epic Overview

### 1.1 Summary

实现 `ToolResultExtractor` 组件，从 SDK 工具调用记录中提取交付物元数据。移除对 LLM JSON 输出的依赖，实现纯工具输出模式（12-Factor Agents Factor 4）。

### 1.2 Business Value

- **确定性输出**: 工具调用参数是结构化数据，无需 JSON 解析
- **可靠性提升**: 消除 LLM 忘记返回 JSON 的问题
- **12-Factor 对齐**: 遵循 "Tools Are Just Structured Outputs" 原则
- **SDK 兼容性**: 同时支持 Kimi 和 Claude SDK 格式

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| JSON 回退移除 | agents/independent.py 中无 markdown_fallback |
| 提取成功率 | 100%（确定性提取） |
| 测试覆盖率 | ToolResultExtractor >= 90% |
| SDK 格式 | Claude SDK (Kimi Code API) |

### 1.4 Dependencies

- **Requires**: EPIC-16 (SDK Wrapper) - 需要理解 SDK message 格式
- **Blocks**: 无

---

## 2. Architecture Context

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ToolResultExtractor 组件架构                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IndependentAgent.execute()                                                 │
│      │                                                                      │
│      ▼                                                                      │
│  messages = await session_manager.single_prompt(prompt, tools)             │
│      │                                                                      │
│      ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   ToolResultExtractor                                │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │ extract_from_messages(messages)                               │  │   │
│  │  │   ├─→ _extract_kimi_format()          # Kimi SDK             │  │   │
│  │  │   ├─→ _extract_claude_format()        # Claude SDK           │  │   │
│  │  │   └─→ _extract_from_result_message()  # ResultMessage        │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                              ↓                                     │   │
│  │                     list[DeliverableMetadata]                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│      │                                                                      │
│      ▼                                                                      │
│  构建 IndependentOutput（无 JSON 解析）                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `tools/tool_result_extractor.py` | 新增：ToolResultExtractor 实现 |
| `tools/__init__.py` | 修改：导出新组件 |
| `agents/independent.py` | 修改：使用新的提取器 |
| `tests/unit/test_tool_result_extractor.py` | 新增：单元测试 |

---

## 3. User Stories

### Story 14.1: DeliverableMetadata 数据类

**ID**: US-14.1  
**As a** developer  
**I want to** 定义 DeliverableMetadata 数据类  
**So that** 交付物元数据结构标准化

**Acceptance Criteria**:
- [ ] `DeliverableMetadata` frozen dataclass 定义完成
- [ ] 包含 `title`, `content`, `content_summary`, `file_path`
- [ ] 包含 `metadata`, `tool_name` 字段
- [ ] 定义 `ToolExtractionError` 异常

**Technical Tasks**:
1. 创建 `tools/tool_result_extractor.py`
2. 定义 `DeliverableMetadata` 数据类
3. 定义 `ToolExtractionError` 异常

**Implementation**:
```python
@dataclass(frozen=True)
class DeliverableMetadata:
    title: str
    content: str
    content_summary: str
    file_path: str
    metadata: dict[str, Any]
    tool_name: str

class ToolExtractionError(Exception):
    pass
```

**Definition of Done**:
- [ ] 数据类定义完整
- [ ] frozen=True 保证不可变性
- [ ] 文档字符串清晰

---

### Story 14.2: Kimi SDK 格式支持

**ID**: US-14.2  
**As a** developer  
**I want to** 实现 Kimi SDK 格式提取  
**So that** 支持当前使用的 SDK

**Acceptance Criteria**:
- [ ] 解析 `message.content` 列表
- [ ] 识别 `type="tool_use"` 的 content parts
- [ ] 提取 `name`, `input` 字段
- [ ] 支持 `create_deliverable` 和 `create_document_set`

**Technical Tasks**:
1. 实现 `_extract_kimi_format` 方法
2. 处理 `message.content` 列表结构
3. 提取工具调用参数

**Implementation**:
```python
def _extract_kimi_format(self, message: Any) -> list[DeliverableMetadata]:
    if not hasattr(message, "content"):
        return []
    
    content = message.content
    if not isinstance(content, list):
        return []
    
    results: list[DeliverableMetadata] = []
    for part in content:
        if getattr(part, "type", None) == "tool_use":
            tool_name = getattr(part, "name", "")
            if tool_name in self.SUPPORTED_TOOLS:
                params = getattr(part, "input", {}) or {}
                extracted = self._parse_tool_params(tool_name, params)
                results.extend(extracted)
    return results
```

**Definition of Done**:
- [ ] Kimi 格式测试通过
- [ ] 支持 create_deliverable
- [ ] 支持 create_document_set

---

### Story 14.3: create_document_set 多文档提取

**ID**: US-14.3  
**As a** developer  
**I want to** 处理 create_document_set 的多文档  
**So that** 批量文档创建可以被正确提取

**Acceptance Criteria**:
- [ ] 解析 `documents` 数组
- [ ] 为每个文档创建独立的 `DeliverableMetadata`
- [ ] 保持文档顺序
- [ ] 正确处理每个文档的 metadata

**Technical Tasks**:
1. 实现 `_parse_tool_params` 中的 `create_document_set` 处理
2. 遍历 `documents` 数组
3. 为每个文档创建 metadata

**Implementation**:
```python
def _parse_tool_params(
    self, tool_name: str, params: dict[str, Any]
) -> list[DeliverableMetadata]:
    if tool_name == "create_deliverable":
        return [self._create_metadata(tool_name, params)]
    elif tool_name == "create_document_set":
        documents = params.get("documents", [])
        return [
            self._create_metadata(tool_name, doc)
            for doc in documents
        ]
    return []
```

**Definition of Done**:
- [ ] 多文档提取测试通过
- [ ] 空文档列表处理正确
- [ ] 文档顺序保持正确

---

### Story 14.4: Claude SDK 格式支持

**ID**: US-14.4  
**As a** developer  
**I want to** 实现 Claude SDK 格式提取  
**So that** 兼容未来的 SDK 替换

**Acceptance Criteria**:
- [ ] 解析 `ToolUseBlock` 类型
- [ ] 解析 `ResultMessage` 类型
- [ ] 处理不同的 message 结构
- [ ] 统一返回 `DeliverableMetadata`

**Technical Tasks**:
1. 实现 `_extract_claude_format` 方法
2. 实现 `_extract_from_result_message` 方法
3. 处理 `ToolUseBlock` 的特殊结构

**Implementation**:
```python
def _extract_claude_format(self, message: Any) -> list[DeliverableMetadata]:
    if not hasattr(message, "content"):
        return []
    
    content = message.content
    if not isinstance(content, list):
        return []
    
    results: list[DeliverableMetadata] = []
    for block in content:
        block_type = type(block).__name__
        if block_type == "ToolUseBlock" or hasattr(block, "name"):
            tool_name = getattr(block, "name", "")
            if tool_name in self.SUPPORTED_TOOLS:
                params = getattr(block, "input", {}) or {}
                extracted = self._parse_tool_params(tool_name, params)
                results.extend(extracted)
    return results

def _extract_from_result_message(self, message: Any) -> list[DeliverableMetadata]:
    if type(message).__name__ != "ResultMessage":
        return []
    
    results: list[DeliverableMetadata] = []
    tool_calls = getattr(message, "tool_calls", []) or []
    for call in tool_calls:
        tool_name = call.get("name", "")
        if tool_name in self.SUPPORTED_TOOLS:
            params = call.get("parameters", {}) or call.get("input", {}) or {}
            extracted = self._parse_tool_params(tool_name, params)
            results.extend(extracted)
    return results
```

**Definition of Done**:
- [ ] Claude SDK 格式测试通过
- [ ] ResultMessage 测试通过
- [ ] 与 Kimi 格式统一返回

---

### Story 14.5: 文件名生成

**ID**: US-14.5  
**As a** developer  
**I want to** 从标题生成文件名  
**So that** 文件路径标准化

**Acceptance Criteria**:
- [ ] 小写转换
- [ ] 空格替换为连字符
- [ ] 特殊字符去除
- [ ] 多连字符合并
- [ ] 首尾连字符去除

**Technical Tasks**:
1. 实现 `_slugify` 静态方法
2. 在 `_create_metadata` 中使用
3. 生成 `.md` 扩展名

**Implementation**:
```python
@staticmethod
def _slugify(title: str) -> str:
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug or "document"

def _create_metadata(self, tool_name: str, params: dict[str, Any]) -> DeliverableMetadata:
    title = params.get("title", "Untitled")
    content = params.get("content", "")
    metadata = params.get("metadata", {})
    file_path = self._slugify(title) + ".md"
    content_summary = content[:self._max_summary_length]
    if len(content) > self._max_summary_length:
        content_summary += "\n\n[... content truncated ...]"
    
    return DeliverableMetadata(
        title=title,
        content=content,
        content_summary=content_summary,
        file_path=file_path,
        metadata=metadata,
        tool_name=tool_name,
    )
```

**Definition of Done**:
- [ ] 各种标题格式测试通过
- [ ] 空标题默认为 "document"
- [ ] 特殊字符正确处理

---

### Story 14.6: IndependentAgent 重构

**ID**: US-14.6  
**As a** developer  
**I want to** 重构 IndependentAgent  
**So that** 使用纯工具输出模式

**Acceptance Criteria**:
- [ ] 移除 JSON 解析回退逻辑
- [ ] 使用 `ToolResultExtractor` 提取元数据
- [ ] 从工具参数构建 `IndependentOutput`
- [ ] 移除 `extract_json` 依赖

**Technical Tasks**:
1. 修改 `_handle_agent_response` 方法
2. 移除 `extract_json` 调用
3. 移除 markdown fallback 逻辑
4. 使用 ToolResultExtractor

**Implementation**:
```python
async def _handle_agent_response(self, messages: list[Any]) -> IndependentOutput:
    """Handle agent response with tool-only output mode (Claude SDK)."""
    from autoBMAD.docuswarm.tools.tool_result_extractor import ToolResultExtractor
    
    extractor = ToolResultExtractor()
    deliverable_meta = extractor.extract_single_deliverable(messages)
    
    if deliverable_meta is None:
        raise IndependentAgentError("Agent did not call create_deliverable tool")
    
    return {
        "deliverable": {
            "title": deliverable_meta.title,
            "content": deliverable_meta.content_summary,
            "metadata": deliverable_meta.metadata,
        },
        "tool_calls": [
            {
                "tool": deliverable_meta.tool_name,
                "file_path": deliverable_meta.file_path,
            }
        ],
    }
```

**Definition of Done**:
- [ ] JSON 回退代码已删除
- [ ] ToolResultExtractor 集成完成
- [ ] 纯工具输出模式工作正常

---

## 4. Technical Specifications

### 4.1 API Reference

| Class/Method | Signature | Description |
|--------------|-----------|-------------|
| `DeliverableMetadata` | `frozen dataclass` | 交付物元数据 |
| `ToolResultExtractor.__init__` | `(max_summary_length: int = 500)` | 初始化 |
| `ToolResultExtractor.extract_from_messages` | `(messages: list[Any]) -> list[DeliverableMetadata]` | 批量提取 |
| `ToolResultExtractor.extract_single_deliverable` | `(messages: list[Any]) -> DeliverableMetadata \| None` | 单条提取 |

### 4.2 Supported Tools

| Tool Name | Description |
|-----------|-------------|
| `create_deliverable` | 创建单个交付物 |
| `create_document_set` | 批量创建交付物 |

### 4.3 SDK Formats

| SDK | Format | Extraction Method |
|-----|--------|-------------------|
| claude-agent-sdk | `ResultMessage.tool_calls` | `_extract_from_result_message` |
| claude-agent-sdk | `content: list[ToolUseBlock \| TextBlock]` | `_extract_claude_format` |
| claude-agent-sdk | `ResultMessage.tool_calls` | `_extract_from_result_message` |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test Class | Description |
|------------|-------------|
| `TestToolResultExtractorBasic` | Kimi SDK 基础提取测试 |
| `TestToolResultExtractorDocumentSet` | create_document_set 测试 |
| `TestToolResultExtractorClaudeSDK` | Claude SDK 兼容测试 |
| `TestToolResultExtractorEdgeCases` | 边界情况测试 |
| `TestToolResultExtractorErrors` | 错误处理测试 |

### 5.2 Key Test Cases

```python
# 关键测试：Kimi 格式提取
def test_extract_from_kimi_create_deliverable(self):
    mock_message = Mock()
    mock_message.content = [
        Mock(
            type="tool_use",
            name="create_deliverable",
            input={"title": "Test", "content": "# Content"}
        )
    ]
    results = extractor.extract_from_messages([mock_message])
    assert results[0].title == "Test"

# 关键测试：Claude 格式提取
def test_extract_from_claude_tool_use_block(self):
    mock_message = Mock()
    mock_message.content = [
        TextBlock(text="I'll create..."),
        ToolUseBlock(id="tool_123", name="create_deliverable", input={...})
    ]
    results = extractor.extract_from_messages([mock_message])
    assert len(results) == 1
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ToolResultExtractor 无法解析 SDK message | 中 | 高 | 同时支持 Kimi 和 Claude SDK 格式 |
| Agent 不调用工具 | 低 | 高 | 验证失败时抛出清晰错误 |
| 多 SDK 格式冲突 | 低 | 中 | 按顺序尝试不同提取方法 |

---

## 7. Definition of Done (Epic Level)

- [ ] US-14.1 完成：DeliverableMetadata 数据类
- [ ] US-14.2 完成：Kimi SDK 格式支持
- [ ] US-14.3 完成：create_document_set 多文档提取
- [ ] US-14.4 完成：Claude SDK 格式支持
- [ ] US-14.5 完成：文件名生成
- [ ] US-14.6 完成：IndependentAgent 重构
- [ ] 单元测试覆盖率 >= 90%
- [ ] 集成测试 100% 通过
- [ ] `markdown_fallback` 出现 0 次
- [ ] basedpyright 0 错误
- [ ] ruff 0 违反

---

## 8. References

| Document | Location |
|----------|----------|
| TDD 方案 | `docs/solution/TDD-03-ToolResultExtractor-Refactor.md` |
| 12-Factor Agents | `12-factor-agents/` |
| Epic 16 | `docs/epics/EPIC-16-SDK-WRAPPER.md` |

---

**Epic End**

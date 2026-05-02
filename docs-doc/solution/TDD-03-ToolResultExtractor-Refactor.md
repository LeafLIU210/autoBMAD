# TDD 重构方案: Tool Result Extractor（纯工具输出模式）

> **关联研究报告**: 
> - [DocuSwarm-重构详细研究报告-Part2.md](../research/DocuSwarm-重构详细研究报告-Part2.md) 第3节
> - [DocuSwarm-重构详细研究报告-Part3.md](../research/DocuSwarm-重构详细研究报告-Part3.md) 第5节  
> **优先级**: P1 - 重要  
> **预估工期**: 2-3 天  
> **影响范围**: `tools/tool_result_extractor.py` (新增), `agents/independent.py`, `nodes/dual_agent.py`

---

## 1. 问题分析

### 1.1 当前问题

当前 `IndependentAgent` 要求 LLM 在同一次调用中：
1. 调用 `create_deliverable` 工具写入文件
2. 返回 JSON 元数据（title, content, questions, action）

**问题根因**：LLM 经常忘记步骤 2，返回纯 Markdown 而不是 JSON。

**当前处理逻辑**（`independent.py` 第370-397行）：
```python
async def _handle_agent_response(self, messages: list[Message]) -> IndependentOutput:
    """Handle agent response with fallback logic."""
    content = extract_text_from_messages(messages)
    
    # Try JSON extraction first
    try:
        result = extract_json(content)
        return self._normalize_output(result)
    except (json.JSONDecodeError, ResponseParseError):
        # FALLBACK: Treat as markdown content
        logger.warning("json_extraction_failed_using_markdown_fallback")
        return {
            "deliverable": {
                "title": "Auto-generated",
                "content": content,
            },
            "questions": [],
            "action": "create_deliverable",
        }
```

**违反原则**: 12-Factor Agents Factor 4 - "Tools Are Just Structured Outputs"

### 1.2 理想模式

```
Agent 唯一输出方式：工具调用
    ↓
工具调用参数 = 结构化输出（确定性）
    ↓
代码从工具调用记录中提取元数据（无需 JSON 解析）
```

---

## 2. 目标设计

### 2.1 ToolResultExtractor 职责

```
┌─────────────────────────────────────────────────────────────┐
│                  ToolResultExtractor                         │
├─────────────────────────────────────────────────────────────┤
│  - 解析 Claude SDK Message 列表                              │
│  - 提取 create_deliverable 工具调用参数                      │
│  - 提取 create_document_set 工具调用参数                     │
│  - 构建标准化 DeliverableMetadata                          │
│  - 基于 claude-agent-sdk + Kimi Code API                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 API 设计

```python
@dataclass
class DeliverableMetadata:
    """标准化交付物元数据。"""
    title: str
    content: str  # 完整内容或摘要
    content_summary: str  # 前500字符摘要
    file_path: str
    metadata: dict[str, Any]
    tool_name: str  # "create_deliverable" | "create_document_set"


class ToolResultExtractor:
    """Deterministic extractor for tool call metadata.
    
    Implements 12-Factor Agents Factor 4: Extract structured data
    from tool calls instead of parsing JSON from LLM text output.
    
    Supports claude-agent-sdk message format through Kimi Code API.
    """
    
    def __init__(self, max_summary_length: int = 500) -> None:
        """Initialize extractor.
        
        Args:
            max_summary_length: Maximum length for content summary
        """
    
    def extract_from_messages(
        self,
        messages: list[Any],  # Kimi or Claude SDK messages
    ) -> list[DeliverableMetadata]:
        """Extract all deliverable metadata from message list.
        
        Args:
            messages: SDK message list (kimi_agent_sdk.Message or
                     claude_agent_sdk message types)
                     
        Returns:
            List of DeliverableMetadata (may be empty if no tool calls)
            
        Raises:
            ToolExtractionError: If messages format is invalid
        """
    
    def extract_single_deliverable(
        self,
        messages: list[Any],
    ) -> DeliverableMetadata | None:
        """Extract single deliverable (convenience method).
        
        Returns:
            First deliverable found, or None if no tool calls
        """
```

---

## 3. 测试驱动开发计划

### Phase 1: 编写测试（红阶段）

#### Test 1: 基础提取测试
```python
# tests/unit/test_tool_result_extractor.py

import pytest
from unittest.mock import Mock
from autoBMAD.docuswarm.tools.tool_result_extractor import (
    ToolResultExtractor,
    DeliverableMetadata,
    ToolExtractionError,
)


class TestToolResultExtractorBasic:
    """Test basic extraction from claude-agent-sdk messages."""
    
    def test_extract_from_claude_create_deliverable(self):
        """Test extracting from claude-agent-sdk create_deliverable tool call."""
        # Arrange - Simulate claude-agent-sdk message structure with ToolUseBlock
        mock_message = Mock()
        mock_message.content = [
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="create_deliverable",
                input={
                    "title": "Test Document",
                    "content": "# Test\n\nThis is test content.",
                    "metadata": {"node": "analyst"},
                }
            )
        ]
        
        extractor = ToolResultExtractor()
        
        # Act
        results = extractor.extract_from_messages([mock_message])
        
        # Assert
        assert len(results) == 1
        assert results[0].title == "Test Document"
        assert results[0].content == "# Test\n\nThis is test content."
        assert results[0].tool_name == "create_deliverable"
        assert results[0].metadata["node"] == "analyst"
    
    def test_extract_content_summary_truncation(self):
        """Test that long content is properly summarized."""
        long_content = "A" * 1000
        
        mock_message = Mock()
        mock_message.content = [
            Mock(
                type="tool_use",
                name="create_deliverable",
                input={
                    "title": "Long Doc",
                    "content": long_content,
                }
            )
        ]
        
        extractor = ToolResultExtractor(max_summary_length=100)
        results = extractor.extract_from_messages([mock_message])
        
        assert len(results[0].content_summary) == 100
        assert results[0].content == long_content  # Full content preserved
```

#### Test 2: create_document_set 测试
```python
class TestToolResultExtractorDocumentSet:
    """Test extraction from create_document_set tool calls."""
    
    def test_extract_multiple_documents(self):
        """Test extracting multiple documents from create_document_set."""
        mock_message = Mock()
        mock_message.content = [
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="create_document_set",
                input={
                    "documents": [
                        {
                            "title": "Doc 1",
                            "content": "Content 1",
                            "metadata": {"type": "analysis"},
                        },
                        {
                            "title": "Doc 2",
                            "content": "Content 2",
                            "metadata": {"type": "summary"},
                        },
                    ]
                }
            )
        ]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        
        assert len(results) == 2
        assert results[0].title == "Doc 1"
        assert results[1].title == "Doc 2"
        assert all(r.tool_name == "create_document_set" for r in results)
```

#### Test 3: Claude SDK 兼容测试（Part 3 准备）
```python
class TestToolResultExtractorClaudeSDK:
    """Test extraction from claude-agent-sdk ResultMessage."""
    
    def test_extract_from_result_message(self):
        """Test extracting from claude-agent-sdk ResultMessage."""
        from claude_agent_sdk import ResultMessage
        
        result_msg = ResultMessage(
            result="Document created",
            tool_calls=[
                {
                    "name": "create_deliverable",
                    "parameters": {
                        "title": "Claude Doc",
                        "content": "# Claude Generated\n\nContent here.",
                    }
                }
            ]
        )
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([result_msg])
        
        assert len(results) == 1
        assert results[0].title == "Claude Doc"
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        
        assert len(results) == 1
        assert results[0].title == "Claude Doc"
    
    def test_extract_from_tool_use_block(self):
        """Test extracting from claude-agent-sdk ToolUseBlock."""
        from claude_agent_sdk import ToolUseBlock, TextBlock
        
        mock_message = Mock()
        mock_message.content = [
            TextBlock(text="I'll create the document for you."),
            ToolUseBlock(
                id="tool_123",
                name="create_deliverable",
                input={
                    "title": "Claude Doc",
                    "content": "# Claude Generated\n\nContent here.",
                }
            )
        ]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        
        assert len(results) == 1
        assert results[0].title == "Claude Doc"
```

#### Test 4: 边界情况测试
```python
class TestToolResultExtractorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_messages(self):
        """Test handling empty message list."""
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([])
        assert results == []
    
    def test_no_tool_calls(self):
        """Test messages without tool calls."""
        mock_message = Mock()
        mock_message.content = [Mock(type="text", text="Just a text response")]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        assert results == []
    
    def test_mixed_content(self):
        """Test messages with both text and tool calls."""
        mock_message = Mock()
        mock_message.content = [
            Mock(__class__=Mock(__name__="TextBlock"), text="I'll create the document"),
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="create_deliverable",
                input={"title": "Mixed", "content": "Content"}
            ),
            Mock(__class__=Mock(__name__="TextBlock"), text="Done!"),
        ]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        
        assert len(results) == 1
        assert results[0].title == "Mixed"
    
    def test_missing_content_field(self):
        """Test message without content attribute."""
        mock_message = Mock(spec=[])  # No content attribute
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        assert results == []
    
    def test_slugify_filename_generation(self):
        """Test filename generation from title."""
        mock_message = Mock()
        mock_message.content = [
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="create_deliverable",
                input={
                    "title": "My Special Report 2024!",
                    "content": "Content",
                }
            )
        ]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        
        assert results[0].file_path == "my-special-report-2024.md"
```

#### Test 5: 错误处理测试
```python
class TestToolResultExtractorErrors:
    """Test error handling."""
    
    def test_invalid_tool_input_structure(self):
        """Test handling malformed tool input."""
        mock_message = Mock()
        mock_message.content = [
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="create_deliverable",
                input=None,  # Invalid input
            )
        ]
        
        extractor = ToolResultExtractor()
        # Should not raise, should skip invalid
        results = extractor.extract_from_messages([mock_message])
        assert results == []
    
    def test_unknown_tool_name(self):
        """Test ignoring unknown tool calls."""
        mock_message = Mock()
        mock_message.content = [
            Mock(
                __class__=Mock(__name__="ToolUseBlock"),
                name="unknown_tool",
                input={"data": "value"},
            )
        ]
        
        extractor = ToolResultExtractor()
        results = extractor.extract_from_messages([mock_message])
        assert results == []  # Only extract known deliverable tools
```

### Phase 2: 实现代码（绿阶段）

```python
"""Tool Result Extractor - Deterministic metadata extraction from tool calls.

Implements 12-Factor Agents Factor 4: Tools Are Just Structured Outputs.
Extracts deliverable metadata from SDK tool call records instead of parsing
JSON from LLM text responses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class DeliverableMetadata:
    """Standardized deliverable metadata extracted from tool calls.
    
    Attributes:
        title: Document title
        content: Full document content
        content_summary: Truncated summary (max 500 chars by default)
        file_path: Generated file path from title
        metadata: Additional metadata from tool call
        tool_name: Name of the tool that created this deliverable
    """
    title: str
    content: str
    content_summary: str
    file_path: str
    metadata: dict[str, Any]
    tool_name: str


class ToolExtractionError(Exception):
    """Raised when tool result extraction fails."""
    pass


class ToolResultExtractor:
    """Extract deliverable metadata from SDK tool call records.
    
    This class implements deterministic extraction of structured data
    from tool calls, eliminating the need for JSON parsing from LLM
    text output. Supports claude-agent-sdk through Kimi Code API.
    
    Example:
        >>> extractor = ToolResultExtractor()
        >>> messages = await session_manager.single_prompt(prompt)
        >>> metadata_list = extractor.extract_from_messages(messages)
        >>> for meta in metadata_list:
        ...     print(f"Created: {meta.title} -> {meta.file_path}")
    """
    
    # Tool names we know how to extract from
    SUPPORTED_TOOLS = {"create_deliverable", "create_document_set"}
    
    def __init__(self, max_summary_length: int = 500) -> None:
        """Initialize extractor.
        
        Args:
            max_summary_length: Maximum length for content summary
        """
        self._max_summary_length = max_summary_length
        self._logger = logger.bind(component="ToolResultExtractor")
    
    def extract_from_messages(
        self,
        messages: list[Any],
    ) -> list[DeliverableMetadata]:
        """Extract all deliverable metadata from message list.
        
        Supports claude-agent-sdk message format through Kimi Code API.
        
        Args:
            messages: List of SDK messages
            
        Returns:
            List of DeliverableMetadata (may be empty)
        """
        results: list[DeliverableMetadata] = []
        
        for message in messages:
            try:
                extracted = self._extract_from_single_message(message)
                results.extend(extracted)
            except Exception as e:
                self._logger.warning(
                    "message_extraction_failed",
                    error=str(e),
                    message_type=type(message).__name__,
                )
                continue
        
        return results
    
    def extract_single_deliverable(
        self,
        messages: list[Any],
    ) -> DeliverableMetadata | None:
        """Extract first deliverable (convenience method).
        
        Args:
            messages: List of SDK messages
            
        Returns:
            First deliverable found, or None
        """
        results = self.extract_from_messages(messages)
        return results[0] if results else None
    
    def _extract_from_single_message(
        self,
        message: Any,
    ) -> list[DeliverableMetadata]:
        """Extract from a single message.
        
        Handles both kimi and claude SDK formats.
        """
        results: list[DeliverableMetadata] = []
        
        # Try different message formats (Claude SDK)
        extraction_methods = [
            self._extract_from_result_message,
            self._extract_from_tool_use_block,
        ]
        
        for method in extraction_methods:
            try:
                extracted = method(message)
                if extracted:
                    results.extend(extracted)
                    break  # Successfully extracted
            except Exception:
                continue  # Try next format
        
        return results
    
    def _extract_from_result_message(self, message: Any) -> list[DeliverableMetadata]:
        """Extract from claude-agent-sdk ResultMessage."""
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
    
    def _extract_from_tool_use_block(self, message: Any) -> list[DeliverableMetadata]:
        """Extract from claude-agent-sdk message with ToolUseBlock."""
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
        
        return results
    
    def _extract_from_result_message(self, message: Any) -> list[DeliverableMetadata]:
        """Extract from claude-agent-sdk ResultMessage."""
        if not hasattr(message, "content"):
            return []
        
        content = message.content
        if not isinstance(content, list):
            return []
        
        results: list[DeliverableMetadata] = []
        
        for part in content:
            if not hasattr(part, "type"):
                continue
            
            if part.type == "tool_use":
                tool_name = getattr(part, "name", "")
                if tool_name in self.SUPPORTED_TOOLS:
                    params = getattr(part, "input", {}) or {}
                    extracted = self._parse_tool_params(tool_name, params)
                    results.extend(extracted)
        
        return results
    
    def _extract_from_tool_use_block(self, message: Any) -> list[DeliverableMetadata]:
        """Extract from claude-agent-sdk ToolUseBlock message format."""
        # Claude SDK uses ToolUseBlock
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
        """Extract from claude-agent-sdk ResultMessage."""
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
    
    def _parse_tool_params(
        self,
        tool_name: str,
        params: dict[str, Any],
    ) -> list[DeliverableMetadata]:
        """Parse tool parameters into DeliverableMetadata."""
        if tool_name == "create_deliverable":
            return [self._create_metadata(tool_name, params)]
        
        elif tool_name == "create_document_set":
            documents = params.get("documents", [])
            return [
                self._create_metadata(tool_name, doc)
                for doc in documents
            ]
        
        return []
    
    def _create_metadata(
        self,
        tool_name: str,
        params: dict[str, Any],
    ) -> DeliverableMetadata:
        """Create DeliverableMetadata from tool parameters."""
        title = params.get("title", "Untitled")
        content = params.get("content", "")
        metadata = params.get("metadata", {})
        
        # Generate file path from title
        file_path = self._slugify(title) + ".md"
        
        # Create summary
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
    
    @staticmethod
    def _slugify(title: str) -> str:
        """Convert title to filename-safe slug.
        
        Args:
            title: Document title
            
        Returns:
            Filename-safe string
        """
        # Convert to lowercase
        slug = title.lower()
        # Replace spaces with hyphens
        slug = slug.replace(" ", "-")
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Strip leading/trailing hyphens
        slug = slug.strip("-")
        
        return slug or "document"
```

---

## 4. 重构 Agent 代码

### 重构 IndependentAgent.execute()

```python
class IndependentAgent:
    async def execute(self, context: dict[str, Any]) -> IndependentOutput:
        """Execute with tool-only output mode (no JSON parsing)."""
        # Build and send prompt
        system_prompt = self._format_system_prompt()
        user_message = self._build_user_message(context)
        
        # Call LLM - SDK handles tool dispatch
        messages = await self._call_llm(system_prompt, user_message)
        
        # NEW: Extract metadata from tool calls (deterministic)
        from autoBMAD.docuswarm.tools.tool_result_extractor import ToolResultExtractor
        
        extractor = ToolResultExtractor()
        deliverable_meta = extractor.extract_single_deliverable(messages)
        
        if deliverable_meta is None:
            raise IndependentAgentError("Agent did not call create_deliverable tool")
        
        # Build output from tool parameters (not JSON parsing)
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

---

## 5. 验收标准

| 检查项 | 工具 | 标准 |
|--------|------|------|
| 单元测试通过 | `pytest tests/unit/test_tool_result_extractor.py -v` | 100% 通过 |
| 覆盖率 | `--cov=autoBMAD.docuswarm.tools.tool_result_extractor` | >= 90% |
| 类型检查 | `basedpyright` | 0 错误 |
| 集成测试 | `pytest tests/integration/test_tool_output.py` | 100% 通过 |
| 移除 JSON 回退 | `grep -n "markdown_fallback" agents/independent.py` | 0 处 |

---

## 6. 与 Part 3 的协调

此组件需与 SDK 替换（Part 3）协调：

1. **Phase 1**: 实现 ToolResultExtractor，支持 claude-agent-sdk 格式 (通过 Kimi Code API)
2. **Phase 2**: 迁移 IndependentAgent 使用新提取器

```python
# 在 extractor 中支持 Claude SDK 格式
EXTRACTION_METHODS = [
    self._extract_from_result_message,  # Claude SDK ResultMessage
    self._extract_from_tool_use_block,  # Claude SDK ToolUseBlock
]
```

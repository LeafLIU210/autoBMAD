# TDD 重构方案: Context Resolver（"@" 路径注入）

> **关联研究报告**: [DocuSwarm-重构详细研究报告-Part2.md](../research/DocuSwarm-重构详细研究报告-Part2.md) 第4节  
> **优先级**: P1 - 重要  
> **预估工期**: 2-3 天  
> **影响范围**: `utils/context_resolver.py` (新增), `pipeline/context_summarizer.py` (新增), `main.py`, `pipeline/orchestrator.py`

---

## 1. 问题分析

### 1.1 当前问题

当前系统缺少对上下文文件中 "@" 路径引用的支持：
- 用户无法方便地在 context_file 中引用其他文档
- 长文档直接注入会导致上下文窗口溢出
- 缺少文档摘要机制

### 1.2 目标方案

实现**三层混合方案**：

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: CLI 层（确定性）                                        │
│  - 解析 @ 路径语法                                                │
│  - 预读取所有引用文档                                              │
│  - 构建 ReferencedDocument 列表                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Orchestrator 层（Agent 摘要）                           │
│  - 调用 SDK instant 模式生成摘要                                  │
│  - 注入 summaries 到 PipelineState                                │
│  - 清理完整内容（节省存储）                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: 节点层（继承 + 按需）                                    │
│  - 通过 accumulate_context 获得摘要                              │
│  - 需要详细信息时调用 read_docs_file 工具                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 目标设计

### 2.1 ContextResolver 职责

```python
@dataclass
class ReferencedDocument:
    """被引用的文档信息。"""
    original_reference: str      # 原始 @ 引用，如 "@docs/research/报告.md"
    resolved_path: Path          # 解析后的绝对路径
    content: str                 # 文档完整内容
    summary: str = ""            # 摘要（由 Agent 生成）
    exists: bool = True          # 文件是否存在
    error: str | None = None     # 解析错误信息


@dataclass  
class ResolvedContext:
    """解析后的上下文。"""
    original_content: str                    # 原始 context_file 内容
    cleaned_content: str                     # 移除 @ 引用后的内容
    referenced_documents: list[ReferencedDocument] = field(default_factory=list)
    total_tokens_estimate: int = 0           # 预估 token 数


class ContextResolver:
    """解析 context_file 中的 @ 路径引用。
    
    Supports formats:
    - @docs/research/报告.md     → 相对于项目 docs/ 目录
    - @./local/file.md           → 相对于 context_file 所在目录  
    - @/absolute/path/file.md    → 绝对路径（不推荐）
    """
    
    PATH_PATTERN = re.compile(
        r"@([\w./\-\u4e00-\u9fff]+\.(?:md|txt|yaml|json))", 
        re.UNICODE
    )
    
    def resolve(self, content: str, context_file_path: Path | None = None) -> ResolvedContext:
        """解析 context_file 内容中的 @ 路径。"""
```

### 2.2 ContextSummarizer 职责

```python
class ContextSummarizer:
    """使用 LLM 生成文档摘要。"""
    
    SUMMARIZE_PROMPT = """You are a technical document summarizer.
    
    **Document**: {title}
    **Content**: {content}
    
    Create a concise summary (200-500 words):
    1. Capture key points and main arguments
    2. Preserve technical accuracy  
    3. Use bullet points for clarity
    4. Output ONLY the summary, no commentary
    """
    
    async def summarize_document(self, document: ReferencedDocument) -> str:
        """为单个文档生成摘要。"""
        
    async def summarize_all(self, documents: list[ReferencedDocument]) -> dict[str, str]:
        """为所有文档生成摘要，返回 {reference: summary}。"""
```

---

## 3. 测试驱动开发计划

### Phase 1: ContextResolver 测试

```python
# tests/unit/test_context_resolver.py

import pytest
from pathlib import Path
from autoBMAD.docuswarm.utils.context_resolver import (
    ContextResolver,
    ReferencedDocument,
    ResolvedContext,
)


class TestContextResolverBasic:
    """Test basic path resolution."""
    
    def test_resolve_single_at_path(self, tmp_path):
        """Test resolving single @ path."""
        # Setup - create test file
        docs_dir = tmp_path / "docs" / "research"
        docs_dir.mkdir(parents=True)
        test_file = docs_dir / "report.md"
        test_file.write_text("# Test Report\n\nContent here.")
        
        # Resolve
        resolver = ContextResolver(project_root=tmp_path)
        content = "Please read @docs/research/report.md for details."
        result = resolver.resolve(content)
        
        # Assert
        assert len(result.referenced_documents) == 1
        assert result.referenced_documents[0].original_reference == "@docs/research/report.md"
        assert result.referenced_documents[0].content == "# Test Report\n\nContent here."
        assert result.referenced_documents[0].exists is True
    
    def test_resolve_multiple_paths(self, tmp_path):
        """Test resolving multiple @ paths in one content."""
        # Setup
        (tmp_path / "docs" / "a.md").write_text("A content")
        (tmp_path / "docs" / "b.md").write_text("B content")
        
        resolver = ContextResolver(project_root=tmp_path)
        content = "Read @docs/a.md and @docs/b.md"
        result = resolver.resolve(content)
        
        assert len(result.referenced_documents) == 2
        assert result.referenced_documents[0].resolved_path.name == "a.md"
        assert result.referenced_documents[1].resolved_path.name == "b.md"
    
    def test_resolve_relative_to_context_file(self, tmp_path):
        """Test @./path resolved relative to context_file location."""
        # Setup
        context_dir = tmp_path / "contexts"
        context_dir.mkdir()
        (context_dir / "local.md").write_text("Local content")
        
        resolver = ContextResolver(project_root=tmp_path)
        content = "See @./local.md"
        result = resolver.resolve(content, context_file_path=context_dir / "main.md")
        
        assert result.referenced_documents[0].exists is True
        assert "local.md" in str(result.referenced_documents[0].resolved_path)


class TestContextResolverSecurity:
    """Test path traversal prevention."""
    
    def test_path_traversal_blocked(self, tmp_path):
        """Test that path traversal attacks are blocked."""
        resolver = ContextResolver(project_root=tmp_path)
        content = "@../outside/project.md"
        result = resolver.resolve(content)
        
        assert result.referenced_documents[0].exists is False
        assert "traversal" in result.referenced_documents[0].error.lower()
    
    def test_absolute_path_outside_project_blocked(self, tmp_path):
        """Test absolute paths outside project are blocked."""
        resolver = ContextResolver(project_root=tmp_path)
        content = "@/etc/passwd"
        result = resolver.resolve(content)
        
        assert result.referenced_documents[0].exists is False
        assert "traversal" in result.referenced_documents[0].error.lower()


class TestContextResolverCleaning:
    """Test content cleaning."""
    
    def test_at_references_removed_from_cleaned_content(self, tmp_path):
        """Test that @ references are removed from cleaned_content."""
        (tmp_path / "docs" / "ref.md").write_text("Ref content")
        
        resolver = ContextResolver(project_root=tmp_path)
        content = """# Context

Please read @docs/ref.md.

## Details
More text here."""
        
        result = resolver.resolve(content)
        
        assert "@docs/ref.md" not in result.cleaned_content
        assert "Please read" in result.cleaned_content
        assert "## Details" in result.cleaned_content
    
    def test_token_estimation(self, tmp_path):
        """Test token count estimation."""
        (tmp_path / "docs" / "long.md").write_text("A" * 4000)  # ~1000 tokens
        
        resolver = ContextResolver(project_root=tmp_path)
        result = resolver.resolve("Read @docs/long.md")
        
        # Rough estimate: 4 chars ≈ 1 token
        assert result.total_tokens_estimate >= 900
        assert result.total_tokens_estimate <= 1100
```

### Phase 2: ContextSummarizer 测试

```python
# tests/unit/test_context_summarizer.py

import pytest
from unittest.mock import AsyncMock, Mock
from autoBMAD.docuswarm.pipeline.context_summarizer import (
    ContextSummarizer,
    SUMMARIZE_PROMPT,
)
from autoBMAD.docuswarm.utils.context_resolver import ReferencedDocument


class TestContextSummarizerBasic:
    """Test basic summarization."""
    
    @pytest.mark.asyncio
    async def test_summarize_document_success(self):
        """Test successful document summarization."""
        # Arrange
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content="Key points: 1. Architecture is solid 2. Needs more tests",
            is_success=lambda: True
        ))
        
        doc = ReferencedDocument(
            original_reference="@docs/arch.md",
            resolved_path=Path("/docs/arch.md"),
            content="# Architecture\n\nThis is the architecture doc.",
            exists=True,
        )
        
        summarizer = ContextSummarizer(mock_session)
        
        # Act
        summary = await summarizer.summarize_document(doc)
        
        # Assert
        assert "Key points" in summary
        # Verify prompt includes document content
        call_args = mock_session.single_prompt.call_args
        prompt = call_args.kwargs.get('prompt')
        assert "Architecture" in prompt
        assert "architecture doc" in prompt
    
    @pytest.mark.asyncio
    async def test_summarize_truncates_long_content(self):
        """Test that very long content is truncated before summarization."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True, content="Summary", is_success=lambda: True
        ))
        
        doc = ReferencedDocument(
            original_reference="@docs/long.md",
            resolved_path=Path("/docs/long.md"),
            content="A" * 100000,  # 100K chars
            exists=True,
        )
        
        summarizer = ContextSummarizer(mock_session, max_content_length=50000)
        await summarizer.summarize_document(doc)
        
        # Verify truncated content in prompt
        call_args = mock_session.single_prompt.call_args
        prompt = call_args.kwargs.get('prompt')
        assert "[... content truncated ...]" in prompt
    
    @pytest.mark.asyncio
    async def test_summarize_nonexistent_document(self):
        """Test handling of non-existent document."""
        mock_session = Mock()
        
        doc = ReferencedDocument(
            original_reference="@docs/missing.md",
            resolved_path=Path("/docs/missing.md"),
            content="",
            exists=False,
            error="File not found",
        )
        
        summarizer = ContextSummarizer(mock_session)
        summary = await summarizer.summarize_document(doc)
        
        assert "not available" in summary
        assert mock_session.single_prompt.called is False  # Should not call LLM


class TestContextSummarizerBatch:
    """Test batch summarization."""
    
    @pytest.mark.asyncio
    async def test_summarize_all_multiple_documents(self):
        """Test summarizing multiple documents."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(side_effect=[
            Mock(success=True, content="Summary A", is_success=lambda: True),
            Mock(success=True, content="Summary B", is_success=lambda: True),
        ])
        
        docs = [
            ReferencedDocument(
                original_reference="@docs/a.md",
                resolved_path=Path("/docs/a.md"),
                content="Doc A",
                exists=True,
            ),
            ReferencedDocument(
                original_reference="@docs/b.md",
                resolved_path=Path("/docs/b.md"),
                content="Doc B",
                exists=True,
            ),
        ]
        
        summarizer = ContextSummarizer(mock_session)
        summaries = await summarizer.summarize_all(docs)
        
        assert len(summaries) == 2
        assert summaries["@docs/a.md"] == "Summary A"
        assert summaries["@docs/b.md"] == "Summary B"
        
        # Verify documents updated
        assert docs[0].summary == "Summary A"
        assert docs[1].summary == "Summary B"
```

### Phase 3: 实现代码

```python
# utils/context_resolver.py
"""Context Resolver - Parse @ path references in context files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ReferencedDocument:
    """Referenced document information."""
    original_reference: str
    resolved_path: Path
    content: str
    summary: str = ""
    exists: bool = True
    error: str | None = None


@dataclass
class ResolvedContext:
    """Resolved context with extracted references."""
    original_content: str
    cleaned_content: str
    referenced_documents: list[ReferencedDocument] = field(default_factory=list)
    total_tokens_estimate: int = 0


class ContextResolver:
    """Parse @ path references in context files.
    
    Supports:
    - @docs/...     → Relative to project root docs/
    - @./...        → Relative to context_file directory
    - @/...         → Absolute path (blocked if outside project)
    
    Example:
        >>> resolver = ContextResolver(project_root=Path.cwd())
        >>> result = resolver.resolve(
        ...     content="See @docs/research/report.md",
        ...     context_file_path=Path("contexts/main.md")
        ... )
        >>> print(result.referenced_documents[0].content)
    """
    
    # Match @path/to/file.md (supports Unicode)
    PATH_PATTERN = re.compile(
        r"@([\w./\-\u4e00-\u9fff]+\.(?:md|txt|yaml|json))",
        re.UNICODE
    )
    
    # Token estimation: ~4 chars per token
    CHARS_PER_TOKEN = 4
    
    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize resolver.
        
        Args:
            project_root: Project root for resolving @docs/ paths
        """
        self.project_root = project_root or Path.cwd()
        self.docs_root = self.project_root / "docs"
        self._logger = logger.bind(component="ContextResolver")
    
    def resolve(
        self,
        content: str,
        context_file_path: Path | None = None,
    ) -> ResolvedContext:
        """Resolve @ paths in content.
        
        Args:
            content: Context file content
            context_file_path: Path to context file (for relative resolution)
            
        Returns:
            ResolvedContext with extracted documents
        """
        result = ResolvedContext(
            original_content=content,
            cleaned_content=content,
            referenced_documents=[],
            total_tokens_estimate=0,
        )
        
        # Find all @ references
        matches = self.PATH_PATTERN.findall(content)
        
        for ref_path in matches:
            doc = self._resolve_single_reference(ref_path, context_file_path)
            result.referenced_documents.append(doc)
            
            # Update cleaned content (remove @ reference)
            result.cleaned_content = result.cleaned_content.replace(
                f"@{ref_path}", ""
            )
            
            # Estimate tokens
            if doc.exists:
                result.total_tokens_estimate += len(doc.content) // self.CHARS_PER_TOKEN
        
        # Clean up multiple consecutive newlines
        result.cleaned_content = self._cleanup_content(result.cleaned_content)
        
        self._logger.info(
            "context_resolved",
            references_found=len(matches),
            documents_resolved=len([d for d in result.referenced_documents if d.exists]),
            estimated_tokens=result.total_tokens_estimate,
        )
        
        return result
    
    def _resolve_single_reference(
        self,
        ref_path: str,
        context_file_path: Path | None,
    ) -> ReferencedDocument:
        """Resolve single @ reference."""
        try:
            # Determine resolution strategy
            if ref_path.startswith("docs/"):
                # @docs/... → Relative to project_root
                resolved = self.project_root / ref_path
            elif ref_path.startswith("./"):
                # @./... → Relative to context_file
                if context_file_path:
                    resolved = context_file_path.parent / ref_path[2:]
                else:
                    resolved = Path.cwd() / ref_path[2:]
            elif ref_path.startswith("/"):
                # Absolute path
                resolved = Path(ref_path)
            else:
                # Default: Relative to docs/
                resolved = self.docs_root / ref_path
            
            resolved = resolved.resolve()
            
            # Security check: Must be within project_root
            if not self._is_safe_path(resolved):
                return ReferencedDocument(
                    original_reference=f"@{ref_path}",
                    resolved_path=resolved,
                    content="",
                    exists=False,
                    error="Path traversal denied: must be within project directory",
                )
            
            # Check existence and read
            if not resolved.exists():
                return ReferencedDocument(
                    original_reference=f"@{ref_path}",
                    resolved_path=resolved,
                    content="",
                    exists=False,
                    error=f"File not found: {resolved}",
                )
            
            content = resolved.read_text(encoding="utf-8")
            
            return ReferencedDocument(
                original_reference=f"@{ref_path}",
                resolved_path=resolved,
                content=content,
                exists=True,
            )
            
        except Exception as e:
            return ReferencedDocument(
                original_reference=f"@{ref_path}",
                resolved_path=Path(ref_path),
                content="",
                exists=False,
                error=str(e),
            )
    
    def _is_safe_path(self, resolved: Path) -> bool:
        """Check if path is within project_root."""
        try:
            resolved.relative_to(self.project_root)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _cleanup_content(content: str) -> str:
        """Clean up content by removing excessive newlines."""
        # Remove multiple consecutive newlines
        content = re.sub(r"\n{3,}", "\n\n", content)
        # Strip leading/trailing whitespace
        return content.strip()
```

```python
# pipeline/context_summarizer.py
"""Context Summarizer - Generate document summaries using LLM."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog

from autoBMAD.docuswarm.llm.response import extract_text_from_messages
from autoBMAD.docuswarm.utils.context_resolver import ReferencedDocument

if TYPE_CHECKING:
    from autoBMAD.docuswarm.llm.session_manager import SessionManager

logger = structlog.get_logger(__name__)


SUMMARIZE_PROMPT = """You are a technical document summarizer. Create a concise summary of the following document.

**Document Title**: {title}

**Document Content**:
{content}

**Requirements**:
1. Summary should be 200-500 words
2. Capture key points, main arguments, and conclusions
3. Preserve technical accuracy
4. Use bullet points for clarity
5. Output ONLY the summary, no additional commentary

**Summary**:"""


class ContextSummarizer:
    """Generate document summaries using LLM.
    
    Uses instant mode for fast summarization of referenced documents.
    
    Example:
        >>> summarizer = ContextSummarizer(session_manager)
        >>> summary = await summarizer.summarize_document(doc)
        >>> summaries = await summarizer.summarize_all(docs)
    """
    
    def __init__(
        self,
        session_manager: SessionManager,
        max_content_length: int = 50000,
    ) -> None:
        """Initialize summarizer.
        
        Args:
            session_manager: SessionManager for LLM interactions (Claude SDK based)
            max_content_length: Maximum chars to include in prompt
        """
        self._session_manager = session_manager
        self._max_content_length = max_content_length
        self._logger = logger.bind(component="ContextSummarizer")
    
    async def summarize_document(self, document: ReferencedDocument) -> str:
        """Generate summary for single document.
        
        Args:
            document: Document to summarize
            
        Returns:
            Summary text (or error message if failed)
        """
        if not document.exists or not document.content:
            return f"[Document not available: {document.error}]"
        
        # Truncate if needed
        content = document.content
        if len(content) > self._max_content_length:
            content = content[:self._max_content_length] + "\n\n[... content truncated ...]"
        
        # Extract title from content or filename
        title = document.resolved_path.stem
        first_line = content.split("\n")[0].strip()
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
        
        # Build prompt
        prompt = SUMMARIZE_PROMPT.format(title=title, content=content)
        
        try:
            # Use instant mode for fast summary
            result = await self._session_manager.single_prompt(
                prompt=prompt,
                agent_name="context_summarizer",
            )
            
            summary = result.content if result.is_success() else "[Empty summary]"
            
            self._logger.info(
                "document_summarized",
                title=title,
                content_length=len(document.content),
                summary_length=len(summary),
            )
            
            return summary
            
        except Exception as e:
            self._logger.error(
                "summarization_failed",
                document=str(document.resolved_path),
                error=str(e),
            )
            return f"[Summarization failed: {e}]"
    
    async def summarize_all(
        self,
        documents: list[ReferencedDocument],
    ) -> dict[str, str]:
        """Summarize all documents.
        
        Args:
            documents: List of documents to summarize
            
        Returns:
            Dictionary mapping original_reference to summary
        """
        summaries: dict[str, str] = {}
        
        for doc in documents:
            summary = await self.summarize_document(doc)
            doc.summary = summary
            summaries[doc.original_reference] = summary
        
        self._logger.info(
            "all_documents_summarized",
            count=len(documents),
            successful=len([s for s in summaries.values() if not s.startswith("[")]),
        )
        
        return summaries
```

---

## 4. 集成到 Orchestrator

```python
class HybridOrchestrator:
    async def start_pipeline(self, subject_context, pipeline_id=None):
        # ... existing validation code ...
        
        # NEW: Generate summaries for referenced documents
        referenced_docs = subject_context.get("referenced_documents", [])
        if referenced_docs:
            from autoBMAD.docuswarm.utils.context_resolver import ReferencedDocument
            from autoBMAD.docuswarm.pipeline.context_summarizer import ContextSummarizer
            
            # Reconstruct ReferencedDocument objects
            docs = [
                ReferencedDocument(
                    original_reference=d["reference"],
                    resolved_path=Path(d["path"]),
                    content=d["content"],
                    exists=d["exists"],
                    error=d.get("error"),
                )
                for d in referenced_docs
            ]
            
            # Generate summaries
            summarizer = ContextSummarizer(session_manager)
            summaries = await summarizer.summarize_all(docs)
            
            # Update subject_context with summaries
            subject_context["referenced_document_summaries"] = summaries
            
            # Clear full content to save state space
            for doc_dict in subject_context["referenced_documents"]:
                doc_dict["content"] = ""
                doc_dict["summary"] = summaries.get(doc_dict["reference"], "")
```

---

## 5. 验收标准

| 检查项 | 标准 |
|--------|------|
| @ 路径解析 | 支持 `docs/`, `./`, 绝对路径 |
| 路径遍历防护 | 所有外部路径被拒绝 |
| 摘要生成 | 成功为文档生成200-500字摘要 |
| 长文档截断 | >50K字符文档被截断后摘要 |
| 清理后内容 | @引用被移除，无多余空行 |

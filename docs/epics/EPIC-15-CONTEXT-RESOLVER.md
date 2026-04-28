# Epic 15: Context Resolver（"@" 路径注入）

**Epic ID**: EPIC-15  
**关联方案**: [TDD-04-ContextResolver-Refactor.md](../solution/TDD-04-ContextResolver-Refactor.md)  
**Version**: 1.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days  
**Priority**: P1 - 重要

---

## 1. Epic Overview

### 1.1 Summary

实现三层混合的 `@` 路径引用系统：CLI 层解析路径、Orchestrator 层生成摘要、节点层按需读取。支持 `@docs/`、`@./`、`@/absolute` 三种路径格式，并提供路径遍历防护。

### 1.2 Business Value

- **用户体验**: 用户可以在 context 文件中方便地引用其他文档
- **上下文管理**: 自动摘要长文档，避免上下文窗口溢出
- **安全性**: 路径遍历防护，防止访问项目外文件
- **灵活性**: 三层架构支持不同使用场景

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 路径解析成功率 | 100%（存在的文件） |
| 路径遍历阻断率 | 100%（外部路径） |
| 摘要质量 | 200-500 字，保留关键点 |
| 测试覆盖率 | ContextResolver >= 90%, ContextSummarizer >= 85% |

### 1.4 Dependencies

- **Requires**: EPIC-16 (SDK Wrapper) - Summarizer 需要 LLM
- **Blocks**: 无

---

## 2. Architecture Context

### 2.1 Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Context Resolver 三层架构                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: CLI Layer (Deterministic)                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ContextResolver                                                      │   │
│  │   ├─→ resolve(content, context_file_path) → ResolvedContext          │   │
│  │   ├─→ @docs/ → relative to project_root                            │   │
│  │   ├─→ @./ → relative to context_file                               │   │
│  │   ├─→ @/absolute → absolute path (blocked if outside)              │   │
│  │   └─→ Path traversal prevention                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 2: Orchestrator Layer (Agent Summary)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ContextSummarizer                                                    │   │
│  │   ├─→ summarize_document(doc) → summary                            │   │
│  │   ├─→ summarize_all(docs) → {reference: summary}                   │   │
│  │   ├─→ Truncate >50K content                                        │   │
│  │   └─→ Update PipelineState with summaries                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  Layer 3: Node Layer (Inheritance + On-Demand)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Node Execution                                                       │   │
│  │   ├─→ Access summaries via PipelineState                           │   │
│  │   └─→ Call read_docs_file tool for detailed content                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `utils/context_resolver.py` | 新增：ContextResolver 实现 |
| `pipeline/context_summarizer.py` | 新增：ContextSummarizer 实现 |
| `main.py` | 修改：CLI 层集成 |
| `pipeline/orchestrator.py` | 修改：Orchestrator 层集成 |
| `tests/unit/test_context_resolver.py` | 新增：单元测试 |
| `tests/unit/test_context_summarizer.py` | 新增：单元测试 |

---

## 3. User Stories

### Story 15.1: ReferencedDocument 数据类

**ID**: US-15.1  
**As a** developer  
**I want to** 定义 ReferencedDocument 数据类  
**So that** 引用文档信息结构化

**Acceptance Criteria**:
- [ ] `ReferencedDocument` dataclass 定义完成
- [ ] 包含 `original_reference`, `resolved_path`, `content`
- [ ] 包含 `summary`, `exists`, `error` 字段
- [ ] 定义 `ResolvedContext` 数据类

**Technical Tasks**:
1. 创建 `utils/context_resolver.py`
2. 定义 `ReferencedDocument` 数据类
3. 定义 `ResolvedContext` 数据类

**Implementation**:
```python
@dataclass
class ReferencedDocument:
    original_reference: str
    resolved_path: Path
    content: str
    summary: str = ""
    exists: bool = True
    error: str | None = None

@dataclass
class ResolvedContext:
    original_content: str
    cleaned_content: str
    referenced_documents: list[ReferencedDocument] = field(default_factory=list)
    total_tokens_estimate: int = 0
```

**Definition of Done**:
- [ ] 数据类定义完整
- [ ] 默认值设置正确
- [ ] 文档字符串清晰

---

### Story 15.2: @docs/ 路径解析

**ID**: US-15.2  
**As a** developer  
**I want to** 实现 @docs/ 路径解析  
**So that** 用户可以引用 docs 目录下的文件

**Acceptance Criteria**:
- [ ] `@docs/path/to/file.md` 解析到 `{project_root}/docs/path/to/file.md`
- [ ] 支持多种扩展名（md, txt, yaml, json）
- [ ] 文件不存在时标记 `exists=False`
- [ ] 内容正确读取

**Technical Tasks**:
1. 实现 `ContextResolver.__init__` 接收 `project_root`
2. 实现 `_resolve_single_reference` 方法
3. 处理 `docs/` 前缀

**Implementation**:
```python
class ContextResolver:
    PATH_PATTERN = re.compile(
        r"@([\w./\-\u4e00-\u9fff]+\.(?:md|txt|yaml|json))",
        re.UNICODE
    )
    
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.docs_root = self.project_root / "docs"
    
    def _resolve_single_reference(
        self, ref_path: str, context_file_path: Path | None
    ) -> ReferencedDocument:
        if ref_path.startswith("docs/"):
            resolved = self.project_root / ref_path
        # ... other cases
```

**Definition of Done**:
- [ ] @docs/ 路径测试通过
- [ ] 多种扩展名测试通过
- [ ] 文件不存在处理正确

---

### Story 15.3: @./ 相对路径解析

**ID**: US-15.3  
**As a** developer  
**I want to** 实现 @./ 相对路径解析  
**So that** 用户可以引用 context_file 所在目录的文件

**Acceptance Criteria**:
- [ ] `@./local/file.md` 解析到相对于 context_file 的路径
- [ ] 未提供 context_file_path 时默认使用 cwd
- [ ] 正确解析相对路径

**Technical Tasks**:
1. 在 `_resolve_single_reference` 中处理 `./` 前缀
2. 使用 `context_file_path.parent` 作为基准

**Implementation**:
```python
def _resolve_single_reference(...):
    if ref_path.startswith("./"):
        if context_file_path:
            resolved = context_file_path.parent / ref_path[2:]
        else:
            resolved = Path.cwd() / ref_path[2:]
    # ... other cases
```

**Definition of Done**:
- [ ] @./ 路径测试通过
- [ ] 无 context_file_path 时默认 cwd
- [ ] 相对路径解析正确

---

### Story 15.4: 路径遍历防护

**ID**: US-15.4  
**As a** developer  
**I want to** 实现路径遍历防护  
**So that** 防止访问项目外的敏感文件

**Acceptance Criteria**:
- [ ] `../` 路径被拒绝
- [ ] 绝对路径如果超出 project_root 被拒绝
- [ ] 拒绝时设置 `error` 字段
- [ ] 日志记录安全事件

**Technical Tasks**:
1. 实现 `_is_safe_path` 方法
2. 使用 `Path.relative_to` 检查
3. 拒绝时返回适当的错误信息

**Implementation**:
```python
def _is_safe_path(self, resolved: Path) -> bool:
    try:
        resolved.relative_to(self.project_root)
        return True
    except ValueError:
        return False

def _resolve_single_reference(...):
    # ... resolve path
    resolved = resolved.resolve()
    
    if not self._is_safe_path(resolved):
        return ReferencedDocument(
            original_reference=f"@{ref_path}",
            resolved_path=resolved,
            content="",
            exists=False,
            error="Path traversal denied: must be within project directory",
        )
    # ... check existence and read
```

**Definition of Done**:
- [ ] 路径遍历测试通过
- [ ] 绝对路径越界测试通过
- [ ] 错误信息清晰

---

### Story 15.5: 内容清理

**ID**: US-15.5  
**As a** developer  
**I want to** 实现内容清理  
**So that** 移除 @ 引用后的内容整洁

**Acceptance Criteria**:
- [ ] `@path` 引用从内容中移除
- [ ] 多个连续空行合并为两个
- [ ] 首尾空白去除
- [ ] Token 数量估算

**Technical Tasks**:
1. 在 `resolve` 中实现内容清理
2. 实现 `_cleanup_content` 方法
3. 计算 token 估算值

**Implementation**:
```python
def resolve(self, content: str, context_file_path: Path | None = None) -> ResolvedContext:
    result = ResolvedContext(
        original_content=content,
        cleaned_content=content,
        referenced_documents=[],
        total_tokens_estimate=0,
    )
    
    matches = self.PATH_PATTERN.findall(content)
    for ref_path in matches:
        doc = self._resolve_single_reference(ref_path, context_file_path)
        result.referenced_documents.append(doc)
        result.cleaned_content = result.cleaned_content.replace(f"@{ref_path}", "")
        if doc.exists:
            result.total_tokens_estimate += len(doc.content) // self.CHARS_PER_TOKEN
    
    result.cleaned_content = self._cleanup_content(result.cleaned_content)
    return result

@staticmethod
def _cleanup_content(content: str) -> str:
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()
```

**Definition of Done**:
- [ ] @引用移除测试通过
- [ ] 空行合并测试通过
- [ ] Token 估算测试通过

---

### Story 15.6: ContextSummarizer 实现

**ID**: US-15.6  
**As a** developer  
**I want to** 实现 ContextSummarizer  
**So that** 可以为长文档生成摘要

**Acceptance Criteria**:
- [ ] `summarize_document` 方法实现
- [ ] `summarize_all` 批量处理方法实现
- [ ] 长文档自动截断（>50K）
- [ ] 不存在的文档返回错误消息

**Technical Tasks**:
1. 创建 `pipeline/context_summarizer.py`
2. 实现 `ContextSummarizer` 类
3. 实现摘要提示模板
4. 实现批量处理

**Implementation**:
```python
class ContextSummarizer:
    SUMMARIZE_PROMPT = """You are a technical document summarizer...

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
    
    def __init__(
        self,
        session_manager: SessionManager,
        max_content_length: int = 50000,
    ) -> None:
        self._session_manager = session_manager  # Claude SDK based SessionManager
        self._max_content_length = max_content_length
    
    async def summarize_document(self, document: ReferencedDocument) -> str:
        if not document.exists or not document.content:
            return f"[Document not available: {document.error}]"
        
        content = document.content
        if len(content) > self._max_content_length:
            content = content[:self._max_content_length] + "\n\n[... content truncated ...]"
        
        title = document.resolved_path.stem
        first_line = content.split("\n")[0].strip()
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
        
        prompt = self.SUMMARIZE_PROMPT.format(title=title, content=content)
        
        messages = await self._session_manager.single_prompt(
            prompt=prompt, mode="instant", yolo=True
        )
        return extract_text_from_messages(messages) or "[Empty summary]"
    
    async def summarize_all(self, documents: list[ReferencedDocument]) -> dict[str, str]:
        summaries = {}
        for doc in documents:
            summary = await self.summarize_document(doc)
            doc.summary = summary
            summaries[doc.original_reference] = summary
        return summaries
```

**Definition of Done**:
- [ ] 单文档摘要测试通过
- [ ] 批量摘要测试通过
- [ ] 长文档截断测试通过
- [ ] 不存在文档处理测试通过

---

### Story 15.7: Orchestrator 集成

**ID**: US-15.7  
**As a** developer  
**I want to** 集成到 Orchestrator  
**So that** 引用文档摘要自动注入 PipelineState

**Acceptance Criteria**:
- [ ] 在 `start_pipeline` 中生成摘要
- [ ] 摘要存储到 `referenced_document_summaries`
- [ ] 清理完整内容以节省空间
- [ ] 保留摘要供节点使用

**Technical Tasks**:
1. 修改 `start_pipeline` 方法
2. 重构 `ReferencedDocument` 对象
3. 调用 ContextSummarizer
4. 更新 subject_context

**Implementation**:
```python
class HybridOrchestrator:
    async def start_pipeline(self, subject_context, pipeline_id=None):
        # ... existing validation code ...
        
        # NEW: Generate summaries for referenced documents
        referenced_docs = subject_context.get("referenced_documents", [])
        if referenced_docs:
            from autoBMAD.docuswarm.utils.context_resolver import ReferencedDocument
            from autoBMAD.docuswarm.pipeline.context_summarizer import ContextSummarizer
            
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
            
            summarizer = ContextSummarizer(session_manager)
            summaries = await summarizer.summarize_all(docs)
            
            subject_context["referenced_document_summaries"] = summaries
            for doc_dict in subject_context["referenced_documents"]:
                doc_dict["content"] = ""
                doc_dict["summary"] = summaries.get(doc_dict["reference"], "")
```

**Definition of Done**:
- [ ] 摘要注入测试通过
- [ ] 内容清理测试通过
- [ ] 节点可以访问摘要

---

## 4. Technical Specifications

### 4.1 API Reference

#### ContextResolver

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(project_root: Path \| None = None)` | 初始化解析器 |
| `resolve` | `(content: str, context_file_path: Path \| None) -> ResolvedContext` | 解析内容 |

#### ContextSummarizer

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(session_manager: SessionManager, max_content_length: int = 50000)` | 初始化摘要器 |
| `summarize_document` | `(document: ReferencedDocument) -> str` | 单文档摘要 |
| `summarize_all` | `(documents: list[ReferencedDocument]) -> dict[str, str]` | 批量摘要 |

### 4.2 Path Formats

| Format | Resolution | Example |
|--------|------------|---------|
| `@docs/...` | Relative to `project_root` | `@docs/research/report.md` |
| `@./...` | Relative to `context_file` | `@./local/context.md` |
| `@/...` | Absolute (blocked if outside) | `@/etc/passwd` → Blocked |

### 4.3 Security

| Check | Implementation |
|-------|----------------|
| Path traversal | `Path.relative_to(project_root)` |
| Symlink | `Path.resolve()` before check |
| File existence | `Path.exists()` before read |

---

## 5. Testing Strategy

### 5.1 Unit Tests - ContextResolver

| Test Class | Description |
|------------|-------------|
| `TestContextResolverBasic` | 基础路径解析测试 |
| `TestContextResolverSecurity` | 路径遍历防护测试 |
| `TestContextResolverCleaning` | 内容清理测试 |

### 5.2 Unit Tests - ContextSummarizer

| Test Class | Description |
|------------|-------------|
| `TestContextSummarizerBasic` | 基础摘要测试 |
| `TestContextSummarizerBatch` | 批量处理测试 |

### 5.3 Key Test Cases

```python
# 路径遍历防护
def test_path_traversal_blocked(self, tmp_path):
    resolver = ContextResolver(project_root=tmp_path)
    result = resolver.resolve("@../outside/project.md")
    assert result.referenced_documents[0].exists is False
    assert "traversal" in result.referenced_documents[0].error.lower()

# 摘要截断
async def test_summarize_truncates_long_content(self):
    doc = ReferencedDocument(..., content="A" * 100000)
    summarizer = ContextSummarizer(mock_session, max_content_length=50000)
    await summarizer.summarize_document(doc)
    assert "[... content truncated ...]" in mock_session.single_prompt.call_args[1]["prompt"]
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| @ 路径解析安全漏洞 | 低 | 高 | 严格测试：所有外部路径被拒绝 |
| 摘要生成失败 | 中 | 中 | 错误恢复，返回错误消息 |
| 大文件读取导致内存问题 | 低 | 中 | 读取时限制文件大小 |

---

## 7. Definition of Done (Epic Level)

- [ ] US-15.1 完成：ReferencedDocument 数据类
- [ ] US-15.2 完成：@docs/ 路径解析
- [ ] US-15.3 完成：@./ 相对路径解析
- [ ] US-15.4 完成：路径遍历防护
- [ ] US-15.5 完成：内容清理
- [ ] US-15.6 完成：ContextSummarizer 实现
- [ ] US-15.7 完成：Orchestrator 集成
- [ ] ContextResolver 覆盖率 >= 90%
- [ ] ContextSummarizer 覆盖率 >= 85%
- [ ] 路径遍历防护 100% 测试
- [ ] basedpyright 0 错误
- [ ] ruff 0 违反

---

## 8. References

| Document | Location |
|----------|----------|
| TDD 方案 | `docs/solution/TDD-04-ContextResolver-Refactor.md` |
| Epic 16 | `docs/epics/EPIC-16-SDK-WRAPPER.md` |

---

**Epic End**

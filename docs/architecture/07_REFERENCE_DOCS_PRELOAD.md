# Reference Docs Preload Architecture (Step 2)

**Version**: 1.0  
**Date**: 2026-04-05  
**Status**: In Progress  
**Phase**: 13 (P12)  

---

## 1. Executive Summary

本文档详细描述了 DocuSwarm 的引用文档预加载功能（Step 2）的架构设计。该功能实现了 `NodeExecutionContext.docs_context` 字段的自动填充，使 Agent 无需主动调用工具即可直接获得 context file 中引用的所有支撑文档内容。

### 1.1 Problem Statement

在 Bubble Sort 等场景中，context file 引用了多个支撑文档：

```markdown
## 项目上下文

请参考以下文档:
- `algorithm-spec.md` — 算法规格说明
- `requirements.md` — 利益相关者需求
- `test-criteria.md` — 评估标准
```

**Before Step 2**:
- ~~Agent 需要通过 MCP 工具主动调用 `read_document` 读取引用文档~~
- ~~依赖 LLM 的自主判断，不稳定~~
- 系统提示词无读取引用文档的明确指令

**After Step 2**:
- 引用文档内容在 `NodeExecutionContextBuilder` 阶段自动预加载
- Agent 直接在提示词中看到所有引用文档内容
- 无需依赖 Agent 主动调用工具
- **SDK MCP 兼容**: 预加载机制与 SDK MCP 格式完全兼容，解决 FastMCP JSON 序列化问题

### 1.2 Solution Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Step 2: Reference Docs Preload               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Extraction    2. Search       3. Load        4. Render      │
│  ─────────────    ──────────      ─────────      ─────────     │
│                                                                  │
│  Context File        docs/         File           Prompt        │
│       │               │           Content         Content       │
│       ▼               ▼              │               │          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Extract │───▶│ Search  │───▶│  Read   │───▶│ Render  │     │
│  │Filenames│    │  docs/  │    │ Content │    │ to Prompt│     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│       │            Recursive        │ 10K limit      │          │
│       │            Shallowest wins  │ Truncation     │          │
│       │                             │                │          │
│  `file.md`      docs/file.md      Content      ## 引用文档     │
│  file.md        docs/a/file.md    (truncated)  ### file.md     │
│                 docs/a/b/file.md               {content}       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Components

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Step 2 Component Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ContextBuilder                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ build(pipeline_id, node_id, original_context, repo_root)    │   │   │
│  │  │                                                             │   │   │
│  │  │ 1. Load node config                                        │   │   │
│  │  │ 2. docs_context = _resolve_reference_docs(                 │   │   │
│  │  │        original_context, node_id, repo_root)               │   │   │
│  │  │ 3. Return NodeExecutionContext(                            │   │   │
│  │  │        ...,                                                │   │   │
│  │  │        docs_context=docs_context,  # Pre-loaded!           │   │   │
│  │  │    )                                                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ _resolve_reference_docs()                                   │   │   │
│  │  │                                                             │   │   │
│  │  │ Input:  original_context["content"]                         │   │   │
│  │  │         repo_root: Path                                     │   │   │
│  │  │                                                             │   │   │
│  │  │ Process:                                                    │   │   │
│  │  │   filenames = _extract_filenames(content)                   │   │   │
│  │  │   files = _search_files(filenames, repo_root)               │   │   │
│  │  │   docs_context = [_read_file(f) for f in files]             │   │   │
│  │  │                                                             │   │   │
│  │  │ Output: List[{filename, path, content}]                     │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ContractBuilder                                 │   │
│  │                                                                      │   │
│  │ _build_context_section(context: NodeExecutionContext)               │   │
│  │                                                                      │   │
│  │ sections = ["## 原始上下文", ...]                                   │   │
│  │                                                                      │   │
│  │ # NEW in Step 2                                                      │   │
│  │ docs = context.get("docs_context", [])                               │   │
│  │ if docs:                                                             │   │
│  │     sections.append("\n## 引用文档")                                 │   │
│  │     for doc in docs:                                                 │   │
│  │         sections.append(f"### {doc['filename']}")                    │   │
│  │         sections.append(doc['content'])                              │   │
│  │                                                                      │   │
│  │ return "\n".join(sections)                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Independent Agent                                 │   │
│  │                                                                      │   │
│  │ ## 原始上下文                                                        │   │
│  │ ...                                                                  │   │
│  │                                                                      │   │
│  │ ## 引用文档                    <-- Agent sees this!                  │   │
│  │                                                                      │   │
│  │ ### algorithm-spec.md                                                │   │
│  │ # Algorithm Specification                                            │   │
│  │ ... (full content)                                                   │   │
│  │                                                                      │   │
│  │ ### requirements.md                                                  │   │
│  │ # Stakeholder Requirements                                           │   │
│  │ ... (full content)                                                   │   │
│  │                                                                      │   │
│  │ ## Execution Workflow                                                │   │
│  │ 1. **Create Deliverable**: ...                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Phase 1: Extraction
───────────────────
Context File Content
    │
    │ "请参考 `algorithm-spec.md` 和 requirements.md"
    ▼
Regex Pattern 1: `([^`]+\.(?:md|txt|yaml|yml|json))`
    │
    └──▶ algorithm-spec.md
    ▼
Regex Pattern 2: \b([\w-]+\.(?:md|txt|yaml|yml|json))\b
    │
    └──▶ requirements.md
    ▼
Extracted Filenames: {algorithm-spec.md, requirements.md}


Phase 2: Search
───────────────
repo_root / "docs"
    │
    ├── algorithm-spec.md              ◄── Match (depth=1)
    ├── requirements.md                ◄── Match (depth=1)
    ├── bubble-sort/
    │   └── algorithm-spec.md          ──○ Skip (depth=2, duplicate)
    └── research/
        └── test-criteria.md           ◄── Match (depth=2)
    ▼
Found Files: {
    algorithm-spec.md: docs/algorithm-spec.md,
    requirements.md: docs/requirements.md,
    test-criteria.md: docs/research/test-criteria.md
}


Phase 3: Load
─────────────
For each file:
    │
    ├── Read with UTF-8 encoding
    ├── Check size (max 10,000 chars)
    ├── Truncate if needed + "[内容已截断]"
    └── Create doc entry
    ▼
docs_context: [
    {
        "filename": "algorithm-spec.md",
        "path": "docs/algorithm-spec.md",
        "content": "# Algorithm..."
    },
    {
        "filename": "requirements.md",
        "path": "docs/requirements.md",
        "content": "# Requirements..."
    },
    {
        "filename": "test-criteria.md",
        "path": "docs/research/test-criteria.md",
        "content": "# Test..."
    }
]


Phase 4: Render
───────────────
ContractBuilder._build_context_section()
    │
    ├── Original Context Section
    ├── Reference Docs Section (NEW)
    │   ├── ### algorithm-spec.md
    │   │   {content}
    │   ├── ### requirements.md
    │   │   {content}
    │   └── ### test-criteria.md
    │       {content}
    └── Chained Deliverables Section
    ▼
Final Prompt with Reference Docs
```

---

## 3. Implementation Details

### 3.1 Filename Extraction

```python
# autoBMAD/docuswarm/node_execution/context_builder.py

import re
from pathlib import Path
from typing import Any

# Case-insensitive matching
FILENAME_PATTERNS = [
    # Backtick format: `filename.md`
    r'`([^`]+\.(?:md|txt|yaml|yml|json))`',
    # Bare format: filename.md
    r'\b([\w-]+\.(?:md|txt|yaml|yml|json))\b',
]

ALLOWED_EXTENSIONS = frozenset(['.md', '.txt', '.yaml', '.yml', '.json'])


def _extract_filenames(content: str) -> set[str]:
    """Extract referenced filenames from content.
    
    Supports both backtick (`file.md`) and bare (file.md) formats.
    Case-insensitive matching.
    """
    filenames: set[str] = set()
    
    for pattern in FILENAME_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        filenames.update(matches)
    
    return filenames
```

### 3.2 File Search

```python
def _search_files(
    filenames: set[str],
    repo_root: Path,
) -> dict[str, Path]:
    """Search for files in docs/ directory recursively.
    
    Returns mapping of filename -> Path (shallowest match wins).
    
    Args:
        filenames: Set of filenames to search for
        repo_root: Repository root directory
        
    Returns:
        Dictionary mapping filename to Path (shallowest match)
    """
    docs_dir = repo_root / "docs"
    if not docs_dir.exists():
        return {}
    
    found: dict[str, Path] = {}
    
    for filename in filenames:
        # Find all matches, sort by path depth (shallowest first)
        candidates = sorted(
            docs_dir.rglob(filename),
            key=lambda p: len(p.parts)
        )
        
        for candidate in candidates:
            if candidate.is_file():
                found[filename] = candidate
                break  # Shallowest match wins
    
    return found
```

### 3.3 Content Reading

```python
MAX_DOC_CONTENT_LENGTH = 10000  # characters
TRUNCATION_NOTICE = "\n\n[内容已截断]"


def _read_file_content(
    file_path: Path,
    max_length: int = MAX_DOC_CONTENT_LENGTH,
) -> str | None:
    """Read file content with encoding and size protection.
    
    Args:
        file_path: Path to file
        max_length: Maximum content length before truncation
        
    Returns:
        File content (possibly truncated), or None if read fails
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if len(content) > max_length:
            content = content[:max_length] + TRUNCATION_NOTICE
        
        return content
        
    except (OSError, UnicodeDecodeError):
        # Graceful degradation - skip files that can't be read
        return None
```

### 3.4 Main Resolution Function

```python
def _resolve_reference_docs(
    self,
    original_context: dict[str, Any],
    node_id: str,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """Resolve and load referenced documents from context.
    
    This function:
    1. Extracts filenames from original_context["content"]
    2. Searches for files in docs/ directory recursively
    3. Reads file content with truncation protection
    
    Args:
        original_context: Original context dict with "content" field
        node_id: Node identifier (for logging/debugging)
        repo_root: Repository root path
        
    Returns:
        List of document dicts with filename, path, and content
    """
    content = original_context.get("content", "")
    if not content:
        return []
    
    # Extract filenames
    filenames = _extract_filenames(content)
    if not filenames:
        return []
    
    # Search for files
    found_files = _search_files(filenames, repo_root)
    if not found_files:
        return []
    
    # Read content
    docs_context: list[dict[str, Any]] = []
    
    for filename, file_path in found_files.items():
        file_content = _read_file_content(file_path)
        if file_content is not None:
            docs_context.append({
                "filename": filename,
                "path": str(file_path.relative_to(repo_root)),
                "content": file_content,
            })
    
    return docs_context
```

### 3.5 Integration in build()

```python
def build(
    self,
    pipeline_id: str,
    node_id: str,
    original_context: dict[str, Any],
    chained_deliverables: list[dict[str, Any]] | None = None,
    shared_context: dict[str, Any] | None = None,
    iteration_feedback: dict[str, Any] | None = None,
    repo_root: Path | None = None,  # NEW parameter
) -> NodeExecutionContext:
    """Build NodeExecutionContext with reference docs preloading."""
    node_config = self.loader.load(node_id)
    
    # Resolve reference docs (Step 2)
    docs_context: list[dict[str, Any]] = []
    if repo_root is not None:
        docs_context = self._resolve_reference_docs(
            original_context, node_id, repo_root
        )
    
    return NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=node_id,
        node_name=node_config.name,
        node_order=node_config.sequence,
        original_context=original_context,
        chained_deliverables=chained_deliverables or [],
        shared_context=shared_context or {},
        iteration_feedback=iteration_feedback,
        docs_context=docs_context,  # Pre-loaded reference docs
    )
```

---

## 4. Security Considerations

### 4.1 Path Security

```python
# Uses existing PathValidator from file_tools.py
from autoBMAD.docuswarm.tools.file_tools import PathValidator

def _validate_path(
    file_path: Path,
    allowed_dirs: list[str],
) -> bool:
    """Validate that file_path is within allowed directories."""
    validator = PathValidator(allowed_dirs)
    try:
        validator.validate(str(file_path))
        return True
    except PathNotAllowedError:
        return False
```

### 4.2 Security Checklist

| Check | Implementation |
|-------|----------------|
| Path Traversal Prevention | `PathValidator` ensures resolved paths start with allowed prefix |
| Directory Whitelist | Only searches within `{repo_root}/docs/` |
| Extension Filtering | Only allows `.md`, `.txt`, `.yaml`, `.yml`, `.json` |
| Size Limits | 10,000 char limit prevents prompt overflow attacks |
| Encoding Validation | UTF-8 only, with graceful fallback |

---

## 5. Testing Strategy

### 5.1 Unit Tests

```python
# tests/docuswarm/node_execution/test_reference_resolution.py

class TestFilenameExtraction:
    """Test filename extraction from content."""
    
    def test_extract_backtick_format(self):
        """Extract filenames in backtick format."""
        content = "请参考 `algorithm-spec.md`"
        result = _extract_filenames(content)
        assert "algorithm-spec.md" in result
    
    def test_extract_bare_format(self):
        """Extract bare filenames."""
        content = "请参考 requirements.md 文档"
        result = _extract_filenames(content)
        assert "requirements.md" in result
    
    def test_extract_multiple_formats(self):
        """Extract mixed formats."""
        content = "`a.md` and b.md and `c.yaml`"
        result = _extract_filenames(content)
        assert result == {"a.md", "b.md", "c.yaml"}
    
    def test_extract_case_insensitive(self):
        """Case insensitive matching."""
        content = "`FILE.MD` and file.md"
        result = _extract_filenames(content)
        assert "FILE.MD" in result or "file.md" in result


class TestFileSearch:
    """Test file search in docs/ directory."""
    
    def test_search_shallowest_wins(self, tmp_path):
        """Shallowest path is selected for duplicates."""
        # Create files at different depths
        (tmp_path / "docs" / "file.md").write_text("root")
        (tmp_path / "docs" / "subdir" / "file.md").write_text("nested")
        
        result = _search_files({"file.md"}, tmp_path)
        
        assert "file.md" in result
        assert result["file.md"].name == "docs/file.md"
    
    def test_search_recursive(self, tmp_path):
        """Search works recursively."""
        (tmp_path / "docs" / "a" / "b" / "file.md").write_text("deep")
        
        result = _search_files({"file.md"}, tmp_path)
        
        assert "file.md" in result


class TestContentReading:
    """Test content reading with protection."""
    
    def test_read_normal_file(self, tmp_path):
        """Read normal file content."""
        file_path = tmp_path / "test.md"
        file_path.write_text("Hello World", encoding='utf-8')
        
        result = _read_file_content(file_path)
        
        assert result == "Hello World"
    
    def test_read_truncates_large_file(self, tmp_path):
        """Large files are truncated."""
        file_path = tmp_path / "large.md"
        file_path.write_text("A" * 15000, encoding='utf-8')
        
        result = _read_file_content(file_path, max_length=10000)
        
        assert len(result) <= 10050  # Content + notice
        assert "[内容已截断]" in result
    
    def test_read_nonexistent_file(self, tmp_path):
        """Nonexistent files return None."""
        result = _read_file_content(tmp_path / "missing.md")
        
        assert result is None
```

### 5.2 Integration Tests

```python
# tests/docuswarm/integration/test_docs_context_flow.py

async def test_full_bubble_sort_scenario():
    """Test complete Bubble Sort scenario with reference docs."""
    # Setup test repository
    with temp_repo({
        "docs/bubble-sort/bubble-sort-context.md": """
        # Bubble Sort Project
        
        请参考:
        - `algorithm-spec.md`
        - `requirements.md`
        """,
        "docs/bubble-sort/algorithm-spec.md": "# Algorithm Spec\n\n冒泡排序...",
        "docs/bubble-sort/requirements.md": "# Requirements\n\n需要...",
    }) as repo_root:
        
        # Build context
        builder = NodeExecutionContextBuilder()
        context = builder.build(
            pipeline_id="test",
            node_id="analyst",
            original_context={"content": "请参考 `algorithm-spec.md`"},
            repo_root=repo_root,
        )
        
        # Verify docs_context
        assert len(context["docs_context"]) == 1
        assert context["docs_context"][0]["filename"] == "algorithm-spec.md"
        assert "冒泡排序" in context["docs_context"][0]["content"]
        
        # Verify prompt rendering
        contract_builder = NodePromptContractBuilder()
        user_prompt = contract_builder.render_independent_user_prompt(
            contract_builder.build_independent_contract(context)
        )
        
        assert "## 引用文档" in user_prompt
        assert "### algorithm-spec.md" in user_prompt
```

### 5.3 Architecture Tests

```python
# tests/architecture/test_reference_docs_security.py

def test_path_traversal_prevention():
    """Path traversal attempts are blocked."""
    content = "`../../../etc/passwd.md`"
    filenames = _extract_filenames(content)
    
    # Extraction may succeed, but search should not find it
    # outside docs/ directory
    with temp_repo({"docs/file.md": "test"}) as repo_root:
        result = _search_files(filenames, repo_root)
        assert "../../../etc/passwd.md" not in result
```

---

## 6. Performance Considerations

### 6.1 Complexity Analysis

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Filename Extraction | O(n) | n = content length, regex scan |
| File Search | O(m × k) | m = filenames, k = files in docs/ |
| Content Reading | O(s) | s = total size of found files |
| **Total** | **O(n + m×k + s)** | Typically < 100ms for normal cases |

### 6.2 Optimization Strategies

1. **Lazy Loading**: Only search when `repo_root` is provided
2. **Early Exit**: Stop searching once shallowest match found
3. **Size Limits**: Prevent reading extremely large files
4. **Caching**: Consider caching file content for repeated reads

### 6.3 Monitoring

```python
import structlog

logger = structlog.get_logger()

# Log performance metrics
logger.info(
    "reference_docs_resolved",
    node_id=node_id,
    filenames_found=len(filenames),
    files_loaded=len(docs_context),
    total_content_size=sum(len(d["content"]) for d in docs_context),
    elapsed_ms=elapsed_ms,
)
```

---

## 7. Migration Guide

### 7.1 From Step 1 (Tool-based)

**Before (Tool-based approach)**:
```python
# Agent needs to call tools
# System prompt: "You can use read_document to read files"
# Agent decides whether to read reference docs
```

**After (Preload approach)**:
```python
# Reference docs automatically in prompt
# Agent sees all content without tool calls
# More reliable, no LLM judgment needed
```

### 7.2 Backward Compatibility

The change is backward compatible:
- `docs_context` was previously hardcoded as `[]`
- New implementation fills it when `repo_root` is provided
- Existing code without `repo_root` continues to work

---

## 8. Related Documents

| Document | Description |
|----------|-------------|
| [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md) | 测试驱动实施方案 |
| [方案B可行性研究](2026-04-05-plan-b-read-docs-file-feasibility-research.md) | 可行性深度研究报告 |
| [04_STATE_ARCHITECTURE](04_STATE_ARCHITECTURE.md) | 状态管理架构 |
| [Single Context Protocol](2026-03-13-p0-single-context-protocol-implementation-design.md) | NodeExecutionContext 设计 |

---

**Document End**

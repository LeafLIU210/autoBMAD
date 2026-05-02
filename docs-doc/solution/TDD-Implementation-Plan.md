# DocuSwarm TDD 调试驱动实施计划

> **创建日期**: 2026-03-02  
> **目标项目**: @autoBMAD/docuswarm  
> **实施方式**: 调试驱动开发 (Test-Driven Development)

---

## 1. 当前状态概述

### 1.1 TDD 重构方案完成情况

| TDD方案 | 组件实现 | 测试覆盖 | 集成状态 | 总体状态 |
|---------|---------|---------|---------|---------|
| TDD-01 CheckpointManager | ✅ | ✅ | ✅ 已集成到orchestrator.py | **完成** |
| TDD-02 ContextValidator | ✅ | ✅ | ✅ 已集成到orchestrator.py | **完成** |
| TDD-03 ToolResultExtractor | ✅ | ✅ | ✅ 已集成到agents/independent.py | **完成** |
| TDD-04 ContextResolver | ✅ | ✅ | ⚠️ **CLI层未集成** | **待完成** |
| TDD-05 ClaudeSDKWrapper | ✅ | ✅ | ✅ 已集成，但KimiSessionManager仍在使用 | **部分完成** |

### 1.2 架构现状

```
当前架构状态
─────────────────────────────────────────────────────────────
HybridOrchestrator (门面)
├── CheckpointManager → ✅ 已集成 (TDD-01)
├── ContextValidator → ✅ 已集成 (TDD-02)
├── SessionManager → ⚠️ 双重实现 (KimiSessionManager + SessionManager)
│   ├── KimiSessionManager → 需要移除
│   └── SessionManager (ClaudeSDKWrapper) → 目标实现
├── ToolResultExtractor → ✅ 已集成 (TDD-03)
├── ContextResolver → ⚠️ 未集成到CLI (TDD-04)
└── ContextSummarizer → ✅ 已实现，但接口需适配

CLI Layer (main.py)
└── ContextResolver → ❌ 未调用 (需要添加)
```

---

## 2. 待完成工作

### 2.1 P0: TDD-04 ContextResolver CLI 层集成

**问题**: ContextResolver 和 ContextSummarizer 组件已实现，但未在 CLI 层调用。

**需要修改的文件**:
- `autoBMAD/docuswarm/main.py` - `start` 命令

**实施步骤**:

```python
# 在 main.py start 命令中，读取 context file 后添加：

from autoBMAD.docuswarm.utils.context_resolver import ContextResolver

# 1. 读取 context file 内容后，调用 ContextResolver
resolver = ContextResolver(project_root=Path.cwd())
resolved = resolver.resolve(content, context_file_path=context_path)

# 2. 构建 subject_context 时包含解析结果
subject_context = {
    "subject": subject,
    "context_file": str(context_path),
    "content": resolved.cleaned_content,  # 使用清理后的内容
    "referenced_documents": [
        {
            "original_reference": doc.original_reference,
            "resolved_path": str(doc.resolved_path),
            "content": doc.content,
            "exists": doc.exists,
            "error": doc.error,
            "is_relative": doc.is_relative,
        }
        for doc in resolved.referenced_documents
    ],
    "total_tokens_estimate": resolved.total_tokens_estimate,
}
```

### 2.2 P1: ContextSummarizer 接口适配

**问题**: ContextSummarizer 当前调用 `session_manager.single_prompt()`，但新 SessionManager 返回 `list[dict]` 而非 `list[Message]`。

**需要修改的文件**:
- `autoBMAD/docuswarm/pipeline/context_summarizer.py`

**适配方案**:

```python
# 修改 summarize_document 方法，处理新的返回格式
async def summarize_document(self, document: ReferencedDocument) -> str:
    # ... 前置代码不变 ...
    
    # 调用 LLM
    messages = await self._session_manager.single_prompt(
        prompt=prompt, mode="instant", yolo=True
    )
    
    # 适配新格式：list[dict] vs list[Message]
    if messages and len(messages) > 0:
        msg = messages[-1]
        # 新格式是 dict
        if isinstance(msg, dict):
            content = msg.get("content", "")
            # 检查是否是错误消息
            if msg.get("is_error"):
                return f"[Summarization failed: {content}]"
            return content.strip()
        # 旧格式是 Message 对象
        elif hasattr(msg, "content"):
            content = msg.content
            if isinstance(content, str):
                return content.strip()
    
    return "[Document not available: No response from LLM]"
```

### 2.3 P1: SDK 统一 (KimiSessionManager → SessionManager)

**问题**: 代码库中同时存在 `KimiSessionManager` 和新的 `SessionManager`。

**使用 KimiSessionManager 的文件**:
- `autoBMAD/docuswarm/pipeline/orchestrator.py` - 导入和类型注解
- `autoBMAD/docuswarm/pipeline/context_validator.py` - 导入和类型注解
- `autoBMAD/docuswarm/agents/base.py` - 导入和类型注解
- `autoBMAD/docuswarm/agents/independent.py` - 导入和使用
- `autoBMAD/docuswarm/agents/evaluator.py` - 导入和使用
- `autoBMAD/docuswarm/nodes/dual_agent.py` - 导入和使用
- `autoBMAD/docuswarm/node_execution/executor.py` - 导入和使用
- `autoBMAD/docuswarm/pipeline/graph.py` - 文档字符串

**迁移策略**:

由于 `SessionManager` 已设计为兼容层（保持相同接口），迁移步骤：

1. **更新导入**:
   ```python
   # 从
   from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
   
   # 改为
   from autoBMAD.docuswarm.llm.session_manager import SessionManager
   ```

2. **更新类型注解**:
   ```python
   # 从
   session_manager: KimiSessionManager
   
   # 改为
   session_manager: SessionManager
   ```

3. **更新实例化**:
   ```python
   # 从
   session_manager = KimiSessionManager(work_dir=...)
   
   # 改为
   session_manager = SessionManager(work_dir=...)
   ```

4. **移除 KimiSessionManager 类** (完成迁移后):
   从 `autoBMAD/docuswarm/llm/session_manager.py` 中移除整个 `KimiSessionManager` 类。

---

## 3. 详细实施步骤

### Phase 1: TDD-04 CLI 集成 (1-2天)

#### Step 1.1: 编写集成测试

```python
# tests/integration/test_context_resolver_cli.py

import pytest
from pathlib import Path
from click.testing import CliRunner
from autoBMAD.docuswarm.main import cli


class TestContextResolverCLI:
    """Test @ path resolution in CLI start command."""
    
    def test_start_with_at_reference(self, tmp_path):
        """Test that @ path references are resolved in start command."""
        # Setup: Create context file with @ reference
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "reference.md").write_text("# Reference\n\nThis is reference content.")
        
        context_file = tmp_path / "context.md"
        context_file.write_text("Please read @docs/reference.md for details.")
        
        # Mock environment/config
        runner = CliRunner()
        
        # Note: This would need proper mocking of orchestrator
        # to avoid actual LLM calls
        result = runner.invoke(cli, ['start', '-c', str(context_file)])
        
        # Assert: Should succeed without errors
        assert "Error" not in result.output
```

#### Step 1.2: 实现 CLI 集成

修改 `autoBMAD/docuswarm/main.py`:

```python
# Add import at the top
from autoBMAD.docuswarm.utils.context_resolver import ContextResolver

# Modify start command
def start(ctx: click.Context, context_file: str) -> None:
    # ... existing validation code ...
    
    # Read context file
    try:
        with open(context_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        console.print(f"[red]Error: Failed to read context file: {e}[/red]")
        raise click.ClickException(f"Failed to read context file: {e}") from e
    
    # NEW: Resolve @ path references (TDD-04)
    try:
        resolver = ContextResolver(project_root=Path.cwd())
        resolved = resolver.resolve(content, context_file_path=context_path)
        
        if resolved.referenced_documents:
            console.print(f"[dim]Resolved {len(resolved.referenced_documents)} @ reference(s)[/dim]")
            for doc in resolved.referenced_documents:
                status = "✓" if doc.exists else "✗"
                console.print(f"[dim]  {status} {doc.original_reference}[/dim]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to resolve @ references: {e}[/yellow]")
        # Fall back to original content
        resolved = None
    
    # Prepare subject_context with referenced documents
    subject_context = {
        "subject": subject,
        "context_file": str(context_path),
        "content": resolved.cleaned_content if resolved else content,
    }
    
    # Add referenced_documents if resolved
    if resolved and resolved.referenced_documents:
        subject_context["referenced_documents"] = [
            {
                "original_reference": doc.original_reference,
                "resolved_path": str(doc.resolved_path),
                "content": doc.content,
                "exists": doc.exists,
                "error": doc.error,
                "is_relative": doc.is_relative,
            }
            for doc in resolved.referenced_documents
        ]
        subject_context["total_tokens_estimate"] = resolved.total_tokens_estimate
    
    # ... rest of the function ...
```

### Phase 2: ContextSummarizer 适配 (0.5天)

修改 `autoBMAD/docuswarm/pipeline/context_summarizer.py`:

```python
async def summarize_document(self, document: ReferencedDocument) -> str:
    """Generate summary for single document."""
    if not document.exists or not document.content:
        return f"[Document not available: {document.error or 'File does not exist'}]"
    
    if not document.content.strip():
        return "[Document not available: Content is empty]"
    
    # Extract title and truncate content
    title = self._extract_title(document.content, document.resolved_path)
    truncated_content = self._truncate_content(document.content)
    
    # Build prompt
    prompt = SUMMARIZE_PROMPT.format(title=title, content=truncated_content)
    
    try:
        # Call LLM - compatible with both old and new session manager
        messages = await self._session_manager.single_prompt(
            prompt=prompt, mode="instant", yolo=True
        )
        
        # Extract summary from response - handle both formats
        if messages and len(messages) > 0:
            msg = messages[-1]
            
            # Handle dict format (new SessionManager)
            if isinstance(msg, dict):
                if msg.get("is_error"):
                    return f"[Summarization failed: {msg.get('content', '')}]"
                content = msg.get("content", "")
                return content.strip()
            
            # Handle object format (old KimiSessionManager)
            elif hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, str):
                    return content.strip()
                elif isinstance(content, list) and content:
                    # Handle TextBlock objects
                    first = content[0]
                    if hasattr(first, "text"):
                        return first.text.strip()
        
        return "[Document not available: No response from LLM]"
        
    except Exception as e:
        self._logger.error("summarization_failed", error=str(e))
        return f"[Summarization failed: {e}]"
```

### Phase 3: SDK 统一迁移 (1-2天)

#### Step 3.1: 创建迁移脚本

创建脚本验证所有导入点：

```bash
#!/bin/bash
# scripts/check_kimi_imports.sh

echo "Checking for KimiSessionManager imports..."
grep -r "KimiSessionManager" autoBMAD/docuswarm --include="*.py" | grep -v "__pycache__" | grep -v ".pyc"

echo ""
echo "Files that need to be updated:"
grep -rl "from.*KimiSessionManager" autoBMAD/docuswarm --include="*.py" | grep -v "__pycache__"
```

#### Step 3.2: 更新导入 (按依赖顺序)

1. **pipeline/context_validator.py** - 底层组件
2. **agents/base.py** - 基础 Agent 类
3. **agents/independent.py** - Independent Agent
4. **agents/evaluator.py** - Evaluator Agent
5. **nodes/dual_agent.py** - 节点实现
6. **node_execution/executor.py** - 执行器
7. **pipeline/orchestrator.py** - Orchestrator

每个文件的修改模式：

```python
# File: autoBMAD/docuswarm/pipeline/context_validator.py

# Change line 14:
# FROM:
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

# TO:
from autoBMAD.docuswarm.llm.session_manager import SessionManager

# Change line 80:
# FROM:
session_manager: KimiSessionManager,

# TO:
session_manager: SessionManager,
```

#### Step 3.3: 更新实例化调用

```python
# File: autoBMAD/docuswarm/agents/independent.py

# Around line 491:
# FROM:
pipeline_session_manager = KimiSessionManager(
    work_dir=KaosPath(str(pipeline_output_dir)),
    api_key=api_key,
    base_url=base_url,
)

# TO:
pipeline_session_manager = SessionManager(
    work_dir=pipeline_output_dir,  # Note: SessionManager accepts Path
    api_key=api_key,
    base_url=base_url,
)
```

#### Step 3.4: 更新 orchestrator.py

```python
# File: autoBMAD/docuswarm/pipeline/orchestrator.py

# Change line 17:
# FROM:
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

# TO:
from autoBMAD.docuswarm.llm.session_manager import SessionManager

# Change line 89:
# FROM:
session_manager: Optional KimiSessionManager for session resume and LLM calls.

# TO:
session_manager: Optional SessionManager for session resume and LLM calls.

# Change line 102:
# FROM:
session_manager: KimiSessionManager | None = None,

# TO:
session_manager: SessionManager | None = None,

# Change line 152-166:
# FROM:
def session_manager(self) -> KimiSessionManager | None:
    ...
def _get_or_create_session_manager(...) -> KimiSessionManager:
    ...
    session_manager = KimiSessionManager(...)

# TO:
def session_manager(self) -> SessionManager | None:
    ...
def _get_or_create_session_manager(...) -> SessionManager:
    ...
    # Note: SessionManager uses Path, not KaosPath
    from pathlib import Path
    work_dir = Path(self._work_dir)
    if pipeline_id:
        work_dir = work_dir / pipeline_id
    
    session_manager = SessionManager(
        work_dir=work_dir,
        api_key=self._api_key,
        base_url=self._base_url,
    )
```

#### Step 3.5: 移除 KimiSessionManager

完成所有迁移后，从 `session_manager.py` 中移除 `KimiSessionManager` 类。

---

## 4. 测试策略

### 4.1 单元测试

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific component tests
pytest tests/unit/test_checkpoint_manager.py -v
pytest tests/unit/test_context_validator.py -v
pytest tests/unit/test_context_resolver.py -v
pytest tests/unit/test_claude_sdk_wrapper.py -v
```

### 4.2 集成测试

```bash
# Run integration tests
pytest tests/integration/ -v

# Test CLI with @ path resolution
python -m autoBMAD.docuswarm start -c docs/test_context.md
```

### 4.3 代码质量检查

```bash
# Type checking
basedpyright autoBMAD/docuswarm/

# Code style
ruff check autoBMAD/docuswarm/
ruff format autoBMAD/docuswarm/

# Test coverage
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=term-missing
```

---

## 5. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|---------|
| SDK 接口不兼容 | 中 | 高 | SessionManager 已设计为兼容层，保留 mode/yolo 参数但忽略 |
| ContextResolver 破坏现有流程 | 低 | 中 | 添加 try/except 包装，失败时回退到原始内容 |
| 测试覆盖率下降 | 中 | 中 | 每修改一个文件就运行相关测试 |
| 导入循环 | 低 | 高 | 按依赖顺序更新，使用 TYPE_CHECKING 注解 |
| KimiSessionManager 移除后功能缺失 | 中 | 高 | 保留 KimiSessionManager 直到所有测试通过 |

---

## 6. 验收标准

### 6.1 TDD-04 完成标准

- [ ] `main.py start` 命令能够解析 `@docs/file.md` 路径引用
- [ ] `@./relative/path.md` 相对路径解析正常工作
- [ ] 路径遍历攻击被阻止（如 `@../outside/project.md`）
- [ ] ContextSummarizer 能够为引用的文档生成摘要
- [ ] 引用文档的摘要显示在 pipeline 输出中

### 6.2 SDK 统一完成标准

- [ ] 所有文件导入 `SessionManager` 而非 `KimiSessionManager`
- [ ] `basedpyright` 0 类型错误
- [ ] `ruff check` 0 代码风格问题
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] `KimiSessionManager` 类从代码库中移除

### 6.3 最终验证

```bash
# 完整验证脚本
#!/bin/bash
echo "=== Type Check ==="
basedpyright autoBMAD/docuswarm/ || exit 1

echo "=== Style Check ==="
ruff check autoBMAD/docuswarm/ || exit 1

echo "=== Unit Tests ==="
pytest tests/unit/ -v || exit 1

echo "=== Integration Tests ==="
pytest tests/integration/ -v || exit 1

echo "=== Coverage Check ==="
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=term-missing || exit 1

echo "=== All Checks Passed ==="
```

---

## 7. 附录

### 7.1 相关文档

- [TDD-Refactoring-Review-Report.md](../evaluation/TDD-Refactoring-Review-Report.md) - 审查报告
- [TDD-01-CheckpointManager-Refactor.md](TDD-01-CheckpointManager-Refactor.md)
- [TDD-02-ContextValidator-Refactor.md](TDD-02-ContextValidator-Refactor.md)
- [TDD-03-ToolResultExtractor-Refactor.md](TDD-03-ToolResultExtractor-Refactor.md)
- [TDD-04-ContextResolver-Refactor.md](TDD-04-ContextResolver-Refactor.md)
- [TDD-05-SDKWrapper-Refactor.md](TDD-05-SDKWrapper-Refactor.md)

### 7.2 快速参考

```python
# ContextResolver 使用示例
from autoBMAD.docuswarm.utils.context_resolver import ContextResolver
from pathlib import Path

resolver = ContextResolver(project_root=Path.cwd())
resolved = resolver.resolve("See @docs/guide.md", context_file_path=Path("context.md"))

print(f"Cleaned content: {resolved.cleaned_content}")
print(f"Documents: {len(resolved.referenced_documents)}")
for doc in resolved.referenced_documents:
    print(f"  {doc.original_reference} -> {doc.resolved_path} (exists={doc.exists})")
```

```python
# SessionManager 使用示例 (claude-agent-sdk)
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from pathlib import Path

session_manager = SessionManager(work_dir=Path("/path/to/work"))
messages = await session_manager.single_prompt(
    prompt="Hello!",
    mode="agent",  # Retained for compatibility, ignored
    yolo=True,     # Retained for compatibility, ignored
)
# Returns: list[dict[str, Any]]
```

---

**计划编制完成** - 可开始实施 Phase 1 (TDD-04 CLI 集成)

# 步骤二方案：引用文档预加载功能 - 测试驱动开发方案

**日期**: 2026-04-05  
**类型**: 实施方案 + TDD 计划  
**主题**: DocuSwarm Agent 引用文档自动预加载功能  
**范围**: P0 改动 - context_builder.py + contract_builder.py + executor.py  

---

## 1. 方案概述

### 1.1 目标

实现 `docs_context` 字段的自动填充，让 DocuSwarm Agent 在无需主动调用工具的情况下，直接获得 context file 中引用的所有支撑文档内容。

### 1.2 核心改动

| 优先级 | 文件 | 改动类型 | 说明 |
|--------|------|----------|------|
| P0 | `autoBMAD/docuswarm/node_execution/context_builder.py` | 新增 `_resolve_reference_docs()` + 修改 `build()` | 递归扫描 `docs/` 及子目录，提取并读取引用文档 |
| P0 | `autoBMAD/docuswarm/prompts/contract_builder.py` | 修改 `_build_context_section()` | 渲染 `docs_context` 到 Agent 提示词 |
| P0 | `autoBMAD/docuswarm/node_execution/executor.py` | 修改 `context_builder.build()` 调用 | 传递 `repo_root` 参数 |

### 1.3 数据流示意

```
bubble-sort-context.md (包含 algorithm-spec.md 等引用)
    │
    ▼ NodeExecutionContextBuilder.build()
    ┌─────────────────────────────────────┐
    │ _resolve_reference_docs()           │
    │  1. 提取反引号/裸文件名              │
    │  2. 递归搜索 docs/ 目录              │
    │  3. 读取文件内容（截断保护）          │
    └─────────────────────────────────────┘
    │
    ▼ NodeExecutionContext
    {
        original_context: {...},
        docs_context: [                    ← 新增：预加载内容
            {"filename": "algorithm-spec.md", "content": "..."},
            {"filename": "requirements.md", "content": "..."},
        ]
    }
    │
    ▼ ContractBuilder._build_context_section()
    user_prompt = """
    ## 原始上下文
    ...
    
    ## 引用文档                         ← 新增章节
    
    ### algorithm-spec.md
    ...（全文）...
    
    ### requirements.md
    ...（全文）...
    """
```

---

## 2. 测试策略

### 2.1 测试金字塔

```
        /\
       /  \      E2E 测试 (1-2个)
      /----\     验证完整链路
     /      \
    /--------\   集成测试 (3-4个)
   /          \  验证模块交互
  /------------\ 单元测试 (10-15个)
 /              \ 验证独立函数
/________________\
```

### 2.2 测试文件结构

```
tests/
└── docuswarm/
    ├── __init__.py
    ├── conftest.py                    # 共享 fixtures
    └── node_execution/
        ├── __init__.py
        ├── test_context_builder.py     # ContextBuilder 单元测试
        └── test_reference_resolution.py # 引用解析专项测试
    └── prompts/
        ├── __init__.py
        └── test_contract_builder.py    # ContractBuilder 单元测试
    └── integration/
        ├── __init__.py
        └── test_docs_context_flow.py   # 端到端集成测试
```

---

## 3. 单元测试详细设计

### 3.1 Context Builder 测试 (`test_context_builder.py`)

#### 测试 1: build() 基础功能
```python
def test_build_basic_context():
    """测试基础上下文构建，无引用文档时 docs_context 为空列表。"""
    builder = NodeExecutionContextBuilder()
    
    result = builder.build(
        pipeline_id="pipe_001",
        node_id="analyst",
        original_context={"content": "简单上下文，无引用"},
        repo_root=Path("/tmp/test_repo"),
    )
    
    assert result["pipeline_id"] == "pipe_001"
    assert result["node_id"] == "analyst"
    assert result["docs_context"] == []
```

#### 测试 2: _resolve_reference_docs 提取反引号引用
```python
def test_resolve_reference_docs_backtick_format():
    """测试从反引号格式提取文件名。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `algorithm-spec.md` 和 `requirements.md`"
    }
    
    # 使用临时文件系统
    with temp_docs_structure({
        "algorithm-spec.md": "# 算法文档",
        "requirements.md": "# 需求文档"
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        assert len(result) == 2
        assert result[0]["filename"] == "algorithm-spec.md"
        assert "# 算法文档" in result[0]["content"]
```

#### 测试 3: _resolve_reference_docs 裸文件名
```python
def test_resolve_reference_docs_bare_filenames():
    """测试从裸文件名格式提取（如 'algorithm-spec.md' 不带反引号）。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 algorithm-spec.md 和 test-criteria.md 文档"
    }
    
    with temp_docs_structure({
        "algorithm-spec.md": "算法内容",
        "test-criteria.md": "测试标准"
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        filenames = [r["filename"] for r in result]
        assert "algorithm-spec.md" in filenames
        assert "test-criteria.md" in filenames
```

#### 测试 4: 递归子目录搜索
```python
def test_resolve_reference_docs_recursive_search():
    """测试递归搜索 docs/ 子目录。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `nested-spec.md`"
    }
    
    with temp_docs_structure({
        "subdir/nested-spec.md": "# 嵌套文档",
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        assert len(result) == 1
        assert result[0]["filename"] == "nested-spec.md"
        assert "subdir/nested-spec.md" in result[0]["path"]
```

#### 测试 5: 内容截断保护
```python
def test_resolve_reference_docs_content_truncation():
    """测试大文件内容截断机制。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `large-file.md`"
    }
    
    large_content = "A" * 15000  # 超过 10000 字符限制
    with temp_docs_structure({
        "large-file.md": large_content
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        assert len(result[0]["content"]) <= 10050  # 包含截断提示
        assert "[内容已截断]" in result[0]["content"]
```

#### 测试 6: 同名文件优先级
```python
def test_resolve_reference_docs_same_name_priority():
    """测试同名文件取路径最浅的版本。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `config.md`"
    }
    
    with temp_docs_structure({
        "config.md": "根目录版本",
        "subdir/config.md": "子目录版本"
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        assert len(result) == 1
        assert result[0]["content"] == "根目录版本"
```

#### 测试 7: 文件不存在处理
```python
def test_resolve_reference_docs_file_not_found():
    """测试引用的文件不存在时优雅处理。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `non-existent.md`"
    }
    
    with temp_docs_structure({}) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        assert result == []  # 不存在的文件不产生错误
```

#### 测试 8: 扩展名过滤
```python
def test_resolve_reference_docs_extension_filter():
    """测试只处理允许的扩展名。"""
    builder = NodeExecutionContextBuilder()
    original_context = {
        "content": "请参考 `valid.md` 和 `invalid.exe`"
    }
    
    with temp_docs_structure({
        "valid.md": "有效内容",
        "invalid.exe": "无效内容"
    }) as repo_root:
        result = builder._resolve_reference_docs(
            original_context, "analyst", repo_root
        )
        
        filenames = [r["filename"] for r in result]
        assert "valid.md" in filenames
        assert "invalid.exe" not in filenames
```

### 3.2 Contract Builder 测试 (`test_contract_builder.py`)

#### 测试 9: _build_context_section 包含 docs_context
```python
def test_build_context_section_with_docs():
    """测试上下文章节渲染包含 docs_context。"""
    builder = NodePromptContractBuilder()
    context = {
        "original_context": {"content": "原始内容"},
        "docs_context": [
            {"filename": "ref1.md", "content": "引用内容1"},
            {"filename": "ref2.md", "content": "引用内容2"}
        ]
    }
    
    result = builder._build_context_section(context)
    
    assert "## 原始上下文" in result
    assert "## 引用文档" in result
    assert "### ref1.md" in result
    assert "### ref2.md" in result
    assert "引用内容1" in result
    assert "引用内容2" in result
```

#### 测试 10: _build_context_section 空 docs_context
```python
def test_build_context_section_empty_docs():
    """测试 docs_context 为空时不渲染引用文档章节。"""
    builder = NodePromptContractBuilder()
    context = {
        "original_context": {"content": "原始内容"},
        "docs_context": []
    }
    
    result = builder._build_context_section(context)
    
    assert "## 原始上下文" in result
    assert "## 引用文档" not in result
```

#### 测试 11: _build_context_section 无 docs_context 字段
```python
def test_build_context_section_missing_docs():
    """测试没有 docs_context 字段时正常渲染。"""
    builder = NodePromptContractBuilder()
    context = {
        "original_context": {"content": "原始内容"}
        # 没有 docs_context 字段
    }
    
    result = builder._build_context_section(context)
    
    assert "## 原始上下文" in result
    assert "## 引用文档" not in result
```

---

## 4. 集成测试设计

### 4.1 端到端流程测试 (`test_docs_context_flow.py`)

#### 测试 12: 完整流程 - Bubble Sort 场景
```python
async def test_full_bubble_sort_scenario():
    """
    完整测试 Bubble Sort 场景的引用文档预加载。
    
    场景:
    - bubble-sort-context.md 引用 algorithm-spec.md, requirements.md, test-criteria.md
    - 所有文档位于 docs/bubble-sort/
    
    验证点:
    1. context_builder 正确提取所有引用
    2. docs_context 包含所有文件内容
    3. contract_builder 正确渲染到提示词
    """
    # 设置测试仓库结构
    repo_root = setup_test_repo({
        "docs/bubble-sort/bubble-sort-context.md": """
        # Bubble Sort 项目
        
        请参考以下文档:
        - `algorithm-spec.md` — 算法规格说明
        - `requirements.md` — 利益相关者需求  
        - `test-criteria.md` — 评估标准
        """,
        "docs/bubble-sort/algorithm-spec.md": "# 算法规格\n\n冒泡排序...",
        "docs/bubble-sort/requirements.md": "# 需求\n\n需要...",
        "docs/bubble-sort/test-criteria.md": "# 测试标准\n\n必须..."
    })
    
    # 执行完整链路
    context_builder = NodeExecutionContextBuilder()
    execution_context = context_builder.build(
        pipeline_id="test_pipe",
        node_id="analyst",
        original_context={"content": "请参考 `algorithm-spec.md`"},
        repo_root=repo_root,
    )
    
    # 验证
    assert len(execution_context["docs_context"]) == 1
    
    contract_builder = NodePromptContractBuilder()
    user_prompt = contract_builder.render_independent_user_prompt(
        contract_builder.build_independent_contract(execution_context)
    )
    
    assert "## 引用文档" in user_prompt
    assert "### algorithm-spec.md" in user_prompt
    assert "冒泡排序" in user_prompt
```

#### 测试 13: Executor 集成
```python
async def test_executor_passes_repo_root():
    """测试 executor 正确传递 repo_root 参数。"""
    with patch("autoBMAD.docuswarm.node_execution.executor.create_context_builder") as mock_builder:
        mock_context = {
            "pipeline_id": "test",
            "node_id": "analyst",
            "docs_context": []
        }
        mock_instance = Mock()
        mock_instance.build = Mock(return_value=mock_context)
        mock_builder.return_value = mock_instance
        
        # 创建模拟 state
        state = create_mock_state()
        
        # 执行
        executor = create_node_executor("analyst", Mock())
        await executor(state)
        
        # 验证 build 被调用且包含 repo_root
        call_kwargs = mock_instance.build.call_args.kwargs
        assert "repo_root" in call_kwargs
        assert isinstance(call_kwargs["repo_root"], Path)
```

---

## 5. 实现步骤 (Red-Green-Refactor)

### Phase 1: Red - 编写失败测试

1. **创建测试文件骨架**
   ```bash
   mkdir -p tests/docuswarm/{node_execution,prompts,integration}
   touch tests/__init__.py
   touch tests/docuswarm/__init__.py
   touch tests/docuswarm/conftest.py
   touch tests/docuswarm/node_execution/__init__.py
   touch tests/docuswarm/node_execution/test_context_builder.py
   touch tests/docuswarm/node_execution/test_reference_resolution.py
   touch tests/docuswarm/prompts/__init__.py
   touch tests/docuswarm/prompts/test_contract_builder.py
   touch tests/docuswarm/integration/__init__.py
   touch tests/docuswarm/integration/test_docs_context_flow.py
   ```

2. **实现测试 fixtures** (conftest.py)
   - `temp_docs_structure`: 创建临时文档结构
   - `mock_repo_root`: 模拟仓库根目录
   - `sample_context_files`: 示例上下文文件内容

3. **编写所有测试用例** (先不运行)

### Phase 2: Green - 最小实现通过测试

#### Step 2.1: 实现 `_resolve_reference_docs` 方法

```python
# autoBMAD/docuswarm/node_execution/context_builder.py

import re
from pathlib import Path

def _resolve_reference_docs(
    self,
    original_context: dict[str, Any],
    node_id: str,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """从 original_context 中提取并读取引用文档。
    
    搜索策略:
    1. 从 content 字段提取文件名（反引号格式和裸文件名）
    2. 在 docs/ 目录下递归查找文件
    3. 同名文件取路径最浅的版本
    4. 内容超过 10000 字符自动截断
    
    Args:
        original_context: 原始上下文字典
        node_id: 节点 ID（用于日志/权限）
        repo_root: 仓库根目录路径
        
    Returns:
        引用文档列表，每项包含 filename, path, content
    """
    content = original_context.get("content", "")
    if not content:
        return []
    
    # 提取文件名：反引号格式 `filename.md` 和裸文件名
    patterns = [
        r'`([^`]+\.(?:md|txt|yaml|yml|json))`',  # 反引号格式
        r'\b([\w-]+\.(?:md|txt|yaml|yml|json))\b',  # 裸文件名
    ]
    
    referenced_files: set[str] = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        referenced_files.update(matches)
    
    if not referenced_files:
        return []
    
    # 在 docs/ 目录下递归查找
    docs_dir = repo_root / "docs"
    if not docs_dir.exists():
        return []
    
    docs_context: list[dict[str, Any]] = []
    
    for filename in referenced_files:
        # 查找所有匹配的文件（按路径深度排序，浅的优先）
        candidates = sorted(
            docs_dir.rglob(filename),
            key=lambda p: len(p.parts)
        )
        
        for candidate in candidates:
            if not candidate.is_file():
                continue
                
            try:
                file_content = candidate.read_text(encoding="utf-8")
                
                # 截断保护
                if len(file_content) > 10000:
                    file_content = file_content[:10000] + "\n\n[内容已截断]"
                
                docs_context.append({
                    "filename": filename,
                    "path": str(candidate.relative_to(repo_root)),
                    "content": file_content,
                })
                break  # 找到最浅的版本就停止
                
            except (OSError, UnicodeDecodeError):
                continue  # 读取失败则尝试下一个
    
    return docs_context
```

#### Step 2.2: 修改 `build()` 方法

```python
def build(
    self,
    pipeline_id: str,
    node_id: str,
    original_context: dict[str, Any],
    chained_deliverables: list[dict[str, Any]] | None = None,
    shared_context: dict[str, Any] | None = None,
    iteration_feedback: dict[str, Any] | None = None,
    repo_root: Path | None = None,  # 新增参数
) -> NodeExecutionContext:
    """Build NodeExecutionContext with runtime fields only."""
    node_config = self.loader.load(node_id)
    
    # 解析引用文档
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
        docs_context=docs_context,  # 使用解析结果
    )
```

#### Step 2.3: 修改 `_build_context_section` 渲染

```python
def _build_context_section(self, context: NodeExecutionContext) -> str:
    """构建上下文章节."""
    sections: list[str] = []

    # 原始上下文
    original_context = context.get("original_context", {})
    if original_context:
        content = original_context.get("content", "")
        if content:
            sections.append(f"## 原始上下文\n{content}")

    # 引用文档（新增）
    docs = context.get("docs_context", [])
    if docs:
        sections.append("\n## 引用文档")
        for doc in docs:
            sections.append(f"\n### {doc['filename']}\n")
            sections.append(doc['content'])

    # 上游交付物摘要
    chained = context.get("chained_deliverables", [])
    if chained:
        sections.append("\n## 上游交付物摘要")
        for item in chained:
            node_id = item.get("node_id", "unknown")
            title = item.get("title", "未命名")
            sections.append(f"- **{node_id}**: {title}")

    # 迭代反馈
    feedback = context.get("iteration_feedback")
    if feedback:
        sections.append("\n## 迭代反馈")
        score = feedback.get("alignment_score", 0)
        sections.append(f"上一轮评分: {score}")
        issues = feedback.get("issues_found", [])
        if issues:
            sections.append("需要改进的问题:")
            for issue in issues:
                sections.append(f"- {issue}")

    return "\n".join(sections)
```

#### Step 2.4: 修改 executor 传递 repo_root

```python
# autoBMAD/docuswarm/node_execution/executor.py

# 在 _execute_node 函数中

# P0 Fix: Use repo root as project_root
auto_bmad_root = Path(__file__).parent.parent.parent.resolve()
repo_root = auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD" else auto_bmad_root

# 构建统一的执行上下文
execution_context = context_builder.build(
    pipeline_id=pipeline_id,
    node_id=node_id,
    original_context=original_context,
    chained_deliverables=_extract_chained_deliverables(state),
    shared_context=state.get("shared_context", {}),
    repo_root=repo_root,  # 新增参数
)
```

### Phase 3: Refactor - 优化与清理

1. **性能优化**
   - 考虑添加文件缓存机制
   - 并行读取多个引用文档

2. **错误处理增强**
   - 添加结构化日志记录
   - 完善边界情况处理

3. **代码质量**
   - 提取常量到配置
   - 添加类型注解完善

---

## 6. 验证清单

### 功能验证

- [ ] `docs_context` 正确填充所有引用文档
- [ ] 反引号格式文件名正确提取
- [ ] 裸文件名格式正确提取
- [ ] 递归子目录搜索正常
- [ ] 同名文件取最浅路径
- [ ] 大文件自动截断并添加提示
- [ ] 不存在的文件不报错
- [ ] ContractBuilder 正确渲染引用文档章节
- [ ] Executor 正确传递 repo_root

### 边缘情况

- [ ] original_context 为空
- [ ] original_context 无 content 字段
- [ ] docs/ 目录不存在
- [ ] 所有引用文件都不存在
- [ ] 文件编码异常
- [ ] 文件权限不足
- [ ] 路径包含特殊字符

### 集成验证

- [ ] 完整 Bubble Sort 场景通过
- [ ] 完整 LangGraph 节点执行通过
- [ ] 与现有 pipeline 兼容

---

## 7. 风险与缓解

| 风险 | 严重度 | 缓解措施 |
|------|--------|----------|
| 文件读取性能问题 | 中 | 实现截断保护；考虑后续添加缓存 |
| 路径安全问题 | 低 | 复用现有 PathValidator，严格限制在 docs/ 目录 |
| 与现有功能冲突 | 低 | 保持接口向后兼容，新增可选参数 |
| 测试覆盖不足 | 中 | TDD 流程确保每行代码都有测试覆盖 |

---

## 8. 附录

### A. 引用文件扩展名白名单

```python
ALLOWED_REF_EXTENSIONS = frozenset([
    ".md", ".txt", ".yaml", ".yml", ".json"
])
```

### B. 搜索路径优先级

1. `docs/` 根目录
2. `docs/*/` 一级子目录
3. `docs/*/*/` 二级子目录（递归）

### C. 内容截断配置

```python
MAX_DOC_CONTENT_LENGTH = 10000  # 字符
TRUNCATION_NOTICE = "\n\n[内容已截断]"
```

---

**文档版本**: 1.0  
**作者**: AI Assistant  
**审核**: 待补充

# F3/F4/F5 解决方案建议书

**文档编号**: DS-2026-04-07-F345-SOLUTION  
**研究日期**: 2026-04-07  
**文档类型**: 技术实施方案  

---

## 执行摘要

本文档提供针对 F3、F4、F5 三个高优先级问题的具体实施方案。每个方案包含：
- 问题摘要
- 推荐解决方案
- 备选方案
- 实施步骤
- 风险评估
- 验证方法

---

## 1. F3: Multi-document 端到端实现

### 1.1 问题摘要

Multi-document 方案的 Python 参数层已实现，但 MCP Schema 层、Agent 提取层和 Node 存储层未完成，导致 LLM 无法真正创建多份文档。

### 1.2 推荐方案：渐进式多文档支持

#### 阶段 1: MCP Schema 扩展 (P0)

**目标**: 让 LLM 能够通过 MCP 工具传递 multi-document 参数

**实施步骤**:

1. **修改 create_deliverable_sdk.py**

```python
# autoBMAD/docuswarm/tools/create_deliverable_sdk.py

CREATE_DELIVERABLE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Deliverable title"},
        "content": {"type": "string", "description": "Markdown content"},
        "metadata": {"type": "object", "description": "Optional metadata"},
        # 新增 multi-document 参数
        "document_index": {
            "type": "integer",
            "minimum": 1,
            "description": "1-based position in multi-document set",
        },
        "document_total": {
            "type": "integer",
            "minimum": 1,
            "description": "Total number of documents in set",
        },
        "document_type": {
            "type": "string",
            "description": "Document type identifier (e.g., 'epic-list', 'api-design')",
        },
    },
    "required": ["title", "content"],
}

@tool("create_deliverable", "Create deliverable...", CREATE_DELIVERABLE_SCHEMA)
async def create_deliverable_tool(args: dict[str, Any]) -> dict[str, Any]:
    # 传递所有参数给底层实现
    result = create_deliverable(
        title=args["title"],
        content=args["content"],
        output_dir=output_dir,
        metadata=args.get("metadata", {}),
        document_index=args.get("document_index"),  # 新增
        document_total=args.get("document_total"),   # 新增
        document_type=args.get("document_type"),     # 新增
    )
    ...
```

2. **修改 submit_execution_report Schema**

```python
# 方案 A: 向后兼容 (推荐)
SUBMIT_EXECUTION_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "deliverable": {...},  # 保持原有单文档字段
        "deliverables": {       # 新增多文档字段
            "type": "array",
            "items": {
                "type": "object",
                "properties": {...},
            },
            "description": "Multiple deliverables (for multi-document workflows)",
        },
        "questions": {...},
        "action": {...},
    },
    # 使用 oneOf 确保至少一个存在
    "oneOf": [
        {"required": ["deliverable"]},
        {"required": ["deliverables"]},
    ],
}
```

3. **验证步骤**

```python
# test_multi_document_schema.py

def test_create_deliverable_schema():
    schema = CREATE_DELIVERABLE_SCHEMA
    assert "document_index" in schema["properties"]
    assert "document_total" in schema["properties"]
    assert "document_type" in schema["properties"]

def test_submit_report_schema():
    schema = SUBMIT_EXECUTION_REPORT_SCHEMA
    assert "deliverables" in schema["properties"]
```

#### 阶段 2: IndependentAgent 多文档提取 (P1)

**目标**: 支持从 submit_execution_report 提取多个 deliverable

```python
# autoBMAD/docuswarm/agents/independent.py

def _extract_submit_report_result(
    self,
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:  # 返回列表而非单个
    """Extract all execution reports from response messages."""
    reports = []
    
    for msg in messages:
        content_blocks = msg.get("content", [])
        for block in content_blocks:
            if block.get("type") != "tool_result":
                continue
                
            tool_output = block.get("content", {})
            if isinstance(tool_output, str):
                tool_output = json.loads(tool_output)
            
            if tool_output.get("status") == "success":
                report = tool_output.get("report", {})
                
                # 收集所有 deliverables
                if "deliverables" in report:
                    reports.extend(report["deliverables"])
                elif "deliverable" in report:
                    reports.append(report["deliverable"])
    
    return reports

def _parse_response(self, response: list[dict]) -> IndependentOutput:
    # 获取所有 reports
    reports = self._extract_submit_report_result(response)
    
    if reports:
        if len(reports) == 1:
            # 单文档: 保持原有格式
            data = {"deliverable": reports[0], ...}
        else:
            # 多文档: 使用新的包装格式
            data = {
                "deliverable": {
                    "title": f"{self.node_id.upper()} Deliverables Set",
                    "type": "multi-document",
                    "documents": reports,
                    "total_word_count": sum(r.get("word_count", 0) for r in reports),
                },
                ...
            }
    ...
```

#### 阶段 3: DualAgentNode 多文档存储 (P1)

**目标**: 支持存储和返回多文档结果

```python
# autoBMAD/docuswarm/nodes/dual_agent.py

@dataclass
class NodeResult:
    """Result from DualAgentNode execution."""
    deliverable: dict[str, Any]  # 保持向后兼容
    documents: list[dict[str, Any]] = field(default_factory=list)  # 新增
    questions: list[dict[str, Any]] = field(default_factory=list)
    evaluation: dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_multi_document(self) -> bool:
        """Check if result contains multiple documents."""
        return len(self.documents) > 1 or \
               (self.deliverable.get("type") == "multi-document")
    
    @property
    def all_documents(self) -> list[dict[str, Any]]:
        """Get all documents (single or multi)."""
        if self.documents:
            return self.documents
        if self.deliverable.get("type") == "multi-document":
            return self.deliverable.get("documents", [])
        return [self.deliverable] if self.deliverable else []

class DualAgentNode:
    async def execute(self, execution_context: NodeExecutionContext) -> NodeResult:
        # ...
        all_deliverables: list[dict[str, Any]] = []  # 收集所有 deliverables
        
        while iteration < self.max_iterations:
            # ...
            independent_output = await self.independent_agent.execute_with_input(...)
            
            # 处理多文档结果
            deliverable = independent_output.get("deliverable", {})
            if deliverable.get("type") == "multi-document":
                all_deliverables = deliverable.get("documents", [])
            else:
                all_deliverables = [deliverable]
            
            # ...
        
        return NodeResult(
            deliverable=all_deliverables[0] if all_deliverables else {},
            documents=all_deliverables,  # 存储所有文档
            questions=final_questions,
            evaluation=final_evaluation,
            iteration=iteration,
        )
```

### 1.3 备选方案：简单多文档（快速实现）

如果完整方案工作量过大，可先实现简化版：

```python
# 简化版：不修改 schema，使用 metadata 传递 multi-document 信息

# LLM 调用:
# create_deliverable(
#     title="Epic List",
#     content="...",
#     metadata={
#         "document_index": 1,
#         "document_total": 3,
#         "document_type": "epic-list",
#     }
# )

# Python 层提取 metadata 并回填到返回结果
metadata = params.metadata
document_index = metadata.get("document_index")
document_total = metadata.get("document_total")
document_type = metadata.get("document_type")
```

**优点**: 无需修改 MCP Schema，快速实现  
**缺点**: 依赖 LLM 正确使用 metadata，不够直观

---

## 2. F4: docs_context_summary 传递链修复

### 2.1 问题摘要

docs_context_summary 已生成并注入 PipelineState，但在到达 IndependentAgent Prompt 前，经过 3 个断点被丢弃。

### 2.2 推荐方案：完整传递链修复

#### 步骤 1: 扩展 IndependentAgentInput (P0)

```python
# autoBMAD/docuswarm/node_execution/contracts.py

class IndependentAgentInput(TypedDict, total=False):
    """IndependentAgent 输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: dict[str, Any]
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    shared_context: dict[str, Any]
    docs_context: list[dict[str, Any]]  # ✅ 新增字段
```

#### 步骤 2: 修复 ContextManager (P0)

```python
# autoBMAD/docuswarm/context/isolation.py

class ContextManager:
    def build_independent_input(
        self,
        execution_context: NodeExecutionContext,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> IndependentAgentInput:
        node_config = self.loader.load(execution_context["node_id"])
        
        # 读取所有需要的数据
        original_context = execution_context.get("original_context", {})
        shared_context = execution_context.get("shared_context", {})
        docs_context = execution_context.get("docs_context", [])  # ✅ 新增
        
        # 构建 chained_deliverables_summary
        chained_deliverables = execution_context.get("chained_deliverables", [])
        chained_summary = self._summarize_chained_deliverables(chained_deliverables)
        
        # 构建 deliverable_requirements
        deliverable_reqs = {...}
        
        return IndependentAgentInput(
            task_name=node_config.task.name,
            task_description=node_config.task.description,
            role_supplement=node_config.task.role_supplement,
            deliverable_requirements=deliverable_reqs,
            original_context_summary=original_context.get("content", ""),
            chained_deliverables_summary=chained_summary,
            iteration_feedback=iteration_feedback,
            shared_context=shared_context,
            docs_context=docs_context,  # ✅ 新增
        )
```

#### 步骤 3: 修复 IndependentAgent (P0)

```python
# autoBMAD/docuswarm/agents/independent.py

async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
    timeout: int = 300,
) -> IndependentOutput:
    """Execute the Independent Agent with structured input."""
    
    # 从 agent_input 读取所有字段
    task_name = agent_input.get("task_name", "")
    original_context = agent_input.get("original_context_summary", "")
    chained_deliverables = agent_input.get("chained_deliverables_summary", [])
    iteration_feedback = agent_input.get("iteration_feedback")
    shared_context = agent_input.get("shared_context", {})
    deliverable_requirements = agent_input.get("deliverable_requirements", {})
    
    # ✅ 修复: 读取 docs_context
    docs_context = agent_input.get("docs_context", [])
    
    # ...
    
    # 构建 NodeExecutionContext
    context = NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        node_name=task_name,
        node_order=0,
        original_context={"content": original_context},
        chained_deliverables=chained_deliverables,
        shared_context=shared_context,
        iteration_feedback=iteration_feedback,
        docs_context=docs_context,  # ✅ 使用读取的值，而非空列表
        deliverable_requirements=deliverable_requirements,
    )
    
    # ...
```

#### 步骤 4: 验证传递链

```python
# test_docs_context_flow.py

async def test_docs_context_flow():
    """验证 docs_context 完整传递链。"""
    
    # 1. 构建包含 docs_context 的 execution_context
    execution_context = NodeExecutionContext(
        pipeline_id="test-pipeline",
        node_id="analyst",
        docs_context=[
            {
                "filename": "requirements.md",
                "path": "docs/requirements.md",
                "summary": "System requirements",
            }
        ],
        # ... 其他字段
    )
    
    # 2. ContextManager 转换
    context_manager = ContextManager()
    agent_input = context_manager.build_independent_input(execution_context)
    
    # 3. 验证 agent_input 包含 docs_context
    assert "docs_context" in agent_input
    assert agent_input["docs_context"] == execution_context["docs_context"]
    
    # 4. IndependentAgent 执行
    agent = IndependentAgent(node_id="analyst")
    output = await agent.execute_with_input(
        agent_input=agent_input,
        pipeline_id="test-pipeline",
    )
    
    # 5. 验证 docs_context 到达 ContractBuilder
    # (可通过检查生成的 prompt 内容验证)
```

### 2.3 备选方案：直接传递

如果 ContextManager 的抽象层成为阻碍，可以绕过它直接传递：

```python
# DualAgentNode.execute()

# 构建 execution_context 时直接包含所有必要信息
execution_context = context_builder.build(...)

# 直接传递给 IndependentAgent，不经过 ContextManager 转换
independent_output = await self.independent_agent.execute_with_context(
    context=execution_context,  # 直接传递完整 context
    pipeline_id=pipeline_id,
)
```

**优点**: 减少转换层，降低出错概率  
**缺点**: 破坏 Single Context Protocol 的设计，需要重构更多代码

---

## 3. F5: 类型一致性修复

### 3.1 问题摘要

SummaryAgent 返回 `list[DocumentSummary]`，但 PipelineState 期望 `list[dict[str, Any]]`，导致类型不匹配和潜在序列化问题。

### 3.2 推荐方案：Orchestrator 层转换

在数据存入 PipelineState 之前进行转换：

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py

async def _summarize_referenced_documents(
    self,
    subject_context: dict[str, Any],
    repo_root: Path,
    session_manager: SessionManager,
    timeout: int = 120,
) -> list[dict[str, Any]]:  # 修改返回类型为 list[dict]
    """Generate document summaries as dictionaries."""
    try:
        summary_agent = SummaryAgent(...)
        
        # 获取 DocumentSummary 对象列表
        result = await asyncio.wait_for(
            summary_agent.summarize_context(subject_context),
            timeout=timeout,
        )
        
        # ✅ 转换为 dict 列表
        docs_context_summary = [d.to_dict() for d in result]
        
        logger.info(
            "documents_summarized",
            count=len(docs_context_summary),
            total_tokens=sum(d.get("llm_tokens_used", 0) for d in docs_context_summary),
        )
        
        return docs_context_summary  # 现在返回 list[dict]
        
    except TimeoutError:
        logger.warning("summary_generation_timeout", timeout_seconds=timeout)
        return []
    except Exception as e:
        logger.error("summary_generation_failed", error=str(e))
        return []

async def start_pipeline(self, subject_context, pipeline_id=None):
    # ...
    
    docs_context_summary = await self._summarize_referenced_documents(...)
    # 类型: list[dict[str, Any]] ✅
    
    initial_state = create_initial_state(
        final_pipeline_id,
        subject_context,
        docs_context_summary=docs_context_summary,  # 类型匹配 ✅
    )
```

### 3.3 备选方案：修改 PipelineState 声明

将 PipelineState 声明改为使用 DocumentSummary：

```python
# autoBMAD/docuswarm/pipeline/state.py

from autoBMAD.docuswarm.agents.summary import DocumentSummary

class PipelineState(TypedDict):
    # ...
    docs_context_summary: list[DocumentSummary]  # 改为 dataclass
```

**优点**: 无需转换，类型一致  
**缺点**: 
- DocumentSummary 是内部实现细节，不应暴露在 state 层
- LangGraph Checkpoint 可能无法正确序列化 dataclass
- 其他代码需要改为 attribute 访问方式（`doc.summary` 而非 `doc["summary"]`）

### 3.4 混合方案：保持灵活性

允许两种类型，在消费时统一处理：

```python
# utils.py

def normalize_docs_context(
    docs_context: list[dict[str, Any]] | list[DocumentSummary]
) -> list[dict[str, Any]]:
    """Normalize docs_context to list[dict]."""
    if not docs_context:
        return []
    
    first = docs_context[0]
    if isinstance(first, DocumentSummary):
        return [d.to_dict() for d in docs_context]
    return docs_context  # 已经是 dict 列表

# 在所有消费点使用
normalized = normalize_docs_context(state.get("docs_context_summary", []))
```

**优点**: 容错性强，兼容两种类型  
**缺点**: 增加运行时开销和代码复杂度

---

## 4. 综合实施计划

### 4.1 实施顺序

```
Phase 1: 基础修复 (1-2 天)
├── F4-1: 扩展 IndependentAgentInput ✅
├── F4-2: 修复 ContextManager ✅
├── F4-3: 修复 IndependentAgent ✅
└── F5: Orchestrator 层转换 ✅

Phase 2: 多文档支持 (2-3 天)
├── F3-1: MCP Schema 扩展
├── F3-2: IndependentAgent 多文档提取
└── F3-3: DualAgentNode 多文档存储

Phase 3: 验证与优化 (1-2 天)
├── 单元测试
├── 集成测试
└── 性能测试
```

### 4.2 依赖关系

```
F5 (类型修复)
    ↓
F4 (传递链修复) 依赖 F5
    ↓
F3 (多文档) 依赖 F4 (多文档需要 docs_context 传递)
```

### 4.3 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| MCP Schema 变更破坏现有调用 | 中 | 高 | 添加向后兼容的默认值 |
| F4 修复引入新的传递 bug | 中 | 高 | 增加详尽的单元测试 |
| 多文档存储结构变更影响下游 | 高 | 中 | 保持 deliverable 字段向后兼容 |
| 序列化问题导致 Checkpoint 失败 | 低 | 高 | F5 修复确保使用 dict |

### 4.4 回滚策略

每个阶段独立可回滚：

```python
# 使用 feature flag 控制
ENABLE_MULTI_DOCUMENT = os.getenv("ENABLE_MULTI_DOCUMENT", "false") == "true"
ENABLE_DOCS_CONTEXT = os.getenv("ENABLE_DOCS_CONTEXT", "false") == "true"

# 在代码中检查
if ENABLE_DOCS_CONTEXT and "docs_context" in agent_input:
    docs_context = agent_input["docs_context"]
else:
    docs_context = []  # 回退到空列表
```

---

## 5. 验证策略

### 5.1 单元测试

```python
# test_f3_multi_document.py

def test_create_deliverable_schema_has_multi_doc_fields():
    schema = CREATE_DELIVERABLE_SCHEMA
    assert "document_index" in schema["properties"]
    assert "document_total" in schema["properties"]
    assert "document_type" in schema["properties"]

def test_extract_multiple_reports():
    agent = IndependentAgent(node_id="test")
    messages = [
        {"content": [{"type": "tool_result", "content": {"report": {"deliverables": [{"title": "Doc1"}, {"title": "Doc2"}]}}}]}
    ]
    reports = agent._extract_submit_report_result(messages)
    assert len(reports) == 2

# test_f4_docs_context_flow.py

def test_context_manager_passes_docs_context():
    context_manager = ContextManager()
    execution_context = NodeExecutionContext(
        docs_context=[{"summary": "test"}],
        # ...
    )
    agent_input = context_manager.build_independent_input(execution_context)
    assert agent_input.get("docs_context") == [{"summary": "test"}]

def test_independent_agent_reads_docs_context():
    agent = IndependentAgent(node_id="test")
    agent_input = IndependentAgentInput(
        docs_context=[{"summary": "test"}],
        # ...
    )
    # Mock 内部方法验证 docs_context 被使用
    
# test_f5_type_consistency.py

def test_orchestrator_returns_dict_list():
    orchestrator = HybridOrchestrator(...)
    result = orchestrator._summarize_referenced_documents(...)
    assert all(isinstance(d, dict) for d in result)
```

### 5.2 集成测试

```python
# test_integration.py

async def test_full_pipeline_with_docs_context():
    """验证完整的 Pipeline 能正确传递 docs_context。"""
    orchestrator = HybridOrchestrator(...)
    
    # 启动 Pipeline
    pipeline_id = await orchestrator.start_pipeline(
        subject_context={
            "content": "See `requirements.md` for details",
        }
    )
    
    # 检查生成的文档中是否引用了 requirements.md 的内容
    # (这需要更复杂的验证机制)
```

### 5.3 手动验证清单

- [ ] MCP Schema 包含 multi-document 参数
- [ ] IndependentAgent 能读取 docs_context
- [ ] 生成的 Prompt 包含 docs_context 内容
- [ ] PipelineState 存储的是 dict 而非对象
- [ ] 多文档创建时，每个文档都有正确的 index/type
- [ ] LangGraph Checkpoint 能正常序列化/反序列化

---

## 6. 附录

### 6.1 修改文件清单

| 文件 | 修改类型 | 相关 Issue |
|------|----------|------------|
| `tools/create_deliverable_sdk.py` | 修改 | F3 |
| `agents/independent.py` | 修改 | F3, F4 |
| `nodes/dual_agent.py` | 修改 | F3 |
| `node_execution/contracts.py` | 修改 | F4 |
| `context/isolation.py` | 修改 | F4 |
| `pipeline/orchestrator.py` | 修改 | F5 |

### 6.2 新增测试文件

- `tests/test_f3_multi_document.py`
- `tests/test_f4_docs_context_flow.py`
- `tests/test_f5_type_consistency.py`
- `tests/test_integration_multi_document.py`

### 6.3 参考文档

- F3 完整研究: `03-document-creation-constraints.md`
- F4 完整研究: `06-summary-agent-design.md`, `07-docs-context-persistence.md`
- 代码路径追踪: `F3-F4-F5-code-path-trace.md`

---

**文档完成时间**: 2026-04-07  
**建议实施时间**: 分阶段实施，预计总工期 4-7 天

# F3/F4/F5 实现缺口深度研究报告

**报告编号**: DS-2026-04-07-F345  
**研究日期**: 2026-04-07  
**研究范围**: DocuSwarm Deep Reform 实现审查 - F3/F4/F5 专项  
**研究方法**: 静态代码分析 + 数据流追踪 + 运行时验证  

---

## 执行摘要

本报告针对 `docs/evaluation/2026-04-07-docuswarm-deep-reform-implementation-review.md` 中指出的三个高优先级问题（F3、F4、F5）进行了深度技术调研。通过自动化分析工具和手动代码审查，确认了以下关键发现：

| 问题 | 状态 | 严重程度 | 关键缺口 |
|------|------|----------|----------|
| **F3** | 未实现端到端 | High | MCP Schema 未暴露参数、单文档存储结构 |
| **F4** | 数据流断裂 | High | 3处断点导致摘要无法到达 Prompt |
| **F5** | 类型不一致 | High | DocumentSummary vs dict 类型冲突 |

**核心结论**：当前实现完成了配置模型层和数据结构层的部分工作，但运行时闭环层存在多处关键缺口，导致方案文档宣称的能力未真正进入生产可用状态。

---

## 1. F3: Multi-document 方案只实现了局部结构

### 1.1 方案期望 vs 实际实现

#### 方案期望（来自 03-document-creation-constraints.md）

```
Architect / PO 节点支持多文档创建
├── CreateDeliverableParams 支持 document_index/document_total/document_type
├── MCP create_deliverable 暴露 multi-document 参数
├── submit_execution_report 支持多文档报告
├── IndependentAgent 处理多文档响应
├── DualAgentNode 存储多文档结果
└── Validator 验证多文档结构
```

#### 实际实现

| 组件 | 实现状态 | 问题 |
|------|----------|------|
| `CreateDeliverableParams` | ✅ 已实现 | Python 参数类完整支持 multi-document 字段 |
| MCP `create_deliverable` | ❌ **未实现** | Schema 未暴露 document_index 等参数 |
| `submit_execution_report` | ❌ **未实现** | Schema 只支持单个 deliverable |
| IndependentAgent 提取 | ❌ **未实现** | 只提取单个 report |
| DualAgentNode 存储 | ❌ **未实现** | 只维护单个 final_deliverable |

### 1.2 详细代码分析

#### 1.2.1 Python 参数支持（已实现）

```python
# autoBMAD/docuswarm/tools/create_deliverable.py:24-91
class CreateDeliverableParams(BaseModel):
    title: str
    content: str
    metadata: dict[str, Any]
    document_index: int | None = Field(...)  # ✅ 已添加
    document_total: int | None = Field(...)  # ✅ 已添加
    document_type: str | None = Field(...)   # ✅ 已添加
```

#### 1.2.2 MCP Schema 缺口（关键阻断）

```python
# autoBMAD/docuswarm/tools/create_deliverable_sdk.py:243-266
@tool(
    "create_deliverable",
    "Create a node deliverable document...",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", ...},
            "content": {"type": "string", ...},
            "metadata": {"type": "object", ...},
            # ❌ 缺少: document_index
            # ❌ 缺少: document_total
            # ❌ 缺少: document_type
        },
        "required": ["title", "content"],
    },
)
```

**影响**：LLM 无法通过 MCP 工具调用传递 multi-document 参数，即使 Python 层已支持。

#### 1.2.3 submit_execution_report Schema 缺口

```python
# autoBMAD/docuswarm/tools/create_deliverable_sdk.py:28-83
SUBMIT_EXECUTION_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "deliverable": {          # ❌ 单数形式，只支持一个
            "type": "object",
            "properties": {...},
        },
        # ❌ 缺少: "deliverables": {"type": "array", ...}
    },
}
```

#### 1.2.4 IndependentAgent 提取逻辑限制

```python
# autoBMAD/docuswarm/agents/independent.py:545-573
def _extract_submit_report_result(self, messages: list[dict]) -> dict | None:
    for msg in messages:
        for block in content_blocks:
            if block.get("type") == "tool_result":
                tool_output = block.get("content", {})
                if "report" in tool_output:
                    return report  # ❌ 只返回第一个，未收集所有
    return None
```

#### 1.2.5 DualAgentNode 单文档存储

```python
# autoBMAD/docuswarm/nodes/dual_agent.py:284-289
class DualAgentNode:
    async def execute(self, execution_context: NodeExecutionContext) -> NodeResult:
        final_deliverable: dict[str, Any] = {}  # ❌ 单数类型
        # ... 循环中更新 ...
        final_deliverable.update(independent_deliverable)  # ❌ 只能存一个
```

### 1.3 数据流图

```
预期 Multi-document 数据流:
┌─────────────────────────────────────────────────────────────────┐
│ LLM 意图: 创建 3 份文档 (epic-list, story-list, release-plan)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ MCP Tool Call (预期)                                            │
│ create_deliverable(title="...", document_index=1,               │
│                     document_total=3, document_type="epic-list")│
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ❌ Schema 阻断 ❌
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 实际: 只能传递 title, content, metadata                         │
│ LLM 无法表达 "这是第1/3个文档"                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 修复建议

#### 优先级 P0: MCP Schema 扩展

```python
# create_deliverable_sdk.py
@tool(
    "create_deliverable",
    "...",
    {
        "type": "object",
        "properties": {
            "title": {...},
            "content": {...},
            "metadata": {...},
            # 新增 multi-document 参数
            "document_index": {
                "type": "integer",
                "description": "Position in multi-document set (1-based)",
                "minimum": 1,
            },
            "document_total": {
                "type": "integer",
                "description": "Total documents in set",
                "minimum": 1,
            },
            "document_type": {
                "type": "string",
                "description": "Type identifier (e.g., 'epic-list')",
            },
        },
    },
)
```

#### 优先级 P1: submit_execution_report 多文档支持

```python
SUBMIT_EXECUTION_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "deliverables": {  # 改为复数形式
            "type": "array",
            "items": {
                "type": "object",
                "properties": {...},
            },
        },
        "questions": {...},
        "action": {...},
    },
    "required": ["deliverables", "action"],
}
```

#### 优先级 P1: DualAgentNode 多文档存储

```python
# dual_agent.py
class NodeResult:
    deliverable: dict[str, Any]  # 保持向后兼容
    # 新增多文档支持
    documents: list[dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_multi_document(self) -> bool:
        return len(self.documents) > 1
    
    @property
    def all_documents(self) -> list[dict[str, Any]]:
        return self.documents if self.documents else [self.deliverable]
```

---

## 2. F4: docs_context_summary 传递链断裂

### 2.1 数据流全景图

```
完整传递链 (预期):
PipelineState.docs_context_summary
    ↓ [orchestrator.py:438]
create_initial_state(docs_context_summary=...)
    ↓ [LangGraph Checkpoint]
PipelineState (持久化)
    ↓ [pipeline_adapter.py:209]
PipelineAdapter.convert_pipeline_to_node_state
    ↓ [pipeline_adapter.py:212]
accumulated["docs_context_summary"] = docs_summary
    ↓ [pipeline_adapter.py:214]
context_file = json.dumps(accumulated)
    ↓ [executor.py:45]
_parse_original_context(state["context_file"])
    ↓ [executor.py:52]
context_builder.build(original_context=...)
    ↓ [context_builder.py:62]
if "docs_context_summary" in original_context:
    docs_context = original_context["docs_context_summary"] ✅
    ↓ [context_builder.py:78]
NodeExecutionContext(docs_context=docs_context) ✅
    ↓ [isolation.py:120]
ContextManager.build_independent_input
    ↓
IndependentAgentInput ??? ❌ (此处断裂)
    ↓ [independent.py:924]
IndependentAgent.execute_with_input
    ↓
NodeExecutionContext(docs_context=[]) ❌ (强制设空)
    ↓ [contract_builder.py:253]
contract_builder.build_independent_contract
    ↓
System Prompt (期望包含 docs_context) ❌ (未包含)
```

### 2.2 断点详细分析

#### 断点 1: ContextManager.build_independent_input

```python
# autoBMAD/docuswarm/context/isolation.py:120-175
class ContextManager:
    def build_independent_input(
        self,
        execution_context: NodeExecutionContext,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> IndependentAgentInput:
        # 从 execution_context 读取数据
        node_config = self.loader.load(execution_context["node_id"])
        
        # ❌ 未读取 docs_context
        # execution_context.get("docs_context", [])  # 这行不存在
        
        return IndependentAgentInput(
            task_name=node_config.task.name,
            task_description=node_config.task.description,
            # ... 其他字段 ...
            # ❌ 未包含 docs_context
        )
```

**影响**：即使 `NodeExecutionContext` 包含 `docs_context`，转换后的 `IndependentAgentInput` 也不包含，导致后续步骤无法访问。

#### 断点 2: IndependentAgentInput 类型定义

```python
# autoBMAD/docuswarm/node_execution/contracts.py:41-52
class IndependentAgentInput(TypedDict, total=False):
    """IndependentAgent 输入"""
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: dict[str, Any]
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    shared_context: dict[str, Any]
    # ❌ 缺少: docs_context: list[dict[str, Any]]
```

**影响**：类型系统未定义 `docs_context` 字段，导致无法通过类型检查。

#### 断点 3: IndependentAgent.execute_with_input 强制设空

```python
# autoBMAD/docuswarm/agents/independent.py:920-938
def execute_with_input(self, agent_input: IndependentAgentInput, ...):
    # ...
    
    # P0: Build NodeExecutionContext from agent_input
    docs_context: list[dict[str, Any]] = []  # ❌ 强制设为空列表
    
    context = NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        # ...
        docs_context=docs_context,  # ❌ 使用空列表，而非从 agent_input 读取
    )
```

**影响**：即使前序步骤正确传递了 `docs_context`，在此处被强制重置为空列表。

### 2.3 修复建议

#### 修复断点 1 & 2: 扩展类型定义和方法

```python
# contracts.py
class IndependentAgentInput(TypedDict, total=False):
    # ... 现有字段 ...
    docs_context: list[dict[str, Any]]  # 新增

# isolation.py
class ContextManager:
    def build_independent_input(self, execution_context, ...):
        # 提取 docs_context
        docs_context = execution_context.get("docs_context", [])
        
        return IndependentAgentInput(
            # ... 现有字段 ...
            docs_context=docs_context,  # 新增
        )
```

#### 修复断点 3: 从 agent_input 读取

```python
# independent.py
def execute_with_input(self, agent_input: IndependentAgentInput, ...):
    # 从 agent_input 读取 docs_context
    docs_context = agent_input.get("docs_context", [])  # 修复
    
    context = NodeExecutionContext(
        # ...
        docs_context=docs_context,  # 使用读取的值
    )
```

---

## 3. F5: SummaryAgent 返回类型与声明不一致

### 3.1 类型冲突矩阵

| 组件 | 声明类型 | 实际类型 | 状态 |
|------|----------|----------|------|
| `PipelineState.docs_context_summary` | `list[dict[str, Any]]` | - | ✅ 声明正确 |
| `SummaryAgent.summarize_context` | - | `list[DocumentSummary]` | ⚠️ 未声明 |
| Orchestrator 存储 | - | `list[DocumentSummary]` | ❌ 实际存储对象 |
| Context Builder 消费 | `list[dict[str, Any]]` | `list[DocumentSummary]` | ❌ 类型不匹配 |

### 3.2 代码证据

#### SummaryAgent 返回 DocumentSummary 对象

```python
# autoBMAD/docuswarm/agents/summary.py:564-581
class SummaryAgent:
    async def summarize_context(
        self,
        original_context: dict[str, Any],
    ) -> list[DocumentSummary]:  # ✅ 返回 dataclass 对象列表
        # ...
        return summaries  # list[DocumentSummary]

@dataclass
class DocumentSummary:
    filename: str
    path: str
    size_bytes: int
    summary: str
    key_points: list[str]
    structure: dict[str, Any]
    # ...
    
    def to_dict(self) -> dict[str, Any]:  # ✅ 有转换方法
        return {...}
```

#### Orchestrator 直接存储对象

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py:422-439
docs_context_summary = await self._summarize_referenced_documents(...)
# 返回类型: list[DocumentSummary]

initial_state = create_initial_state(
    final_pipeline_id,
    subject_context,
    docs_context_summary=docs_context_summary,  # ❌ 直接存储对象，未转换
)
```

#### create_initial_state 期望 dict

```python
# autoBMAD/docuswarm/pipeline/state.py:82-121
def create_initial_state(
    pipeline_id: str,
    subject_context: dict[str, Any],
    docs_context_summary: list[dict[str, Any]] | None = None,  # 期望 dict
) -> PipelineState:
    return PipelineState(
        # ...
        docs_context_summary=docs_context_summary or [],  # 实际传入 DocumentSummary
    )
```

### 3.3 潜在运行时问题

虽然 Python 是动态类型语言，但这种不一致会导致：

1. **序列化问题**：LangGraph Checkpoint 序列化时，`DocumentSummary` dataclass 可能无法正确序列化为 JSON
2. **访问方式不一致**：有些代码可能按 `doc["summary"]` 访问，有些可能按 `doc.summary` 访问
3. **IDE 类型提示混乱**：开发者不知道应该使用哪种访问方式

### 3.4 修复建议

#### 方案 A: 在 Orchestrator 层转换（推荐）

```python
# orchestrator.py
result = await summary_agent.summarize_context(subject_context)
docs_context_summary = [d.to_dict() for d in result]  # 转换为 dict

initial_state = create_initial_state(
    pipeline_id,
    subject_context,
    docs_context_summary=docs_context_summary,  # 现在是 list[dict]
)
```

#### 方案 B: 修改 PipelineState 声明

```python
# state.py
from autoBMAD.docuswarm.agents.summary import DocumentSummary

class PipelineState(TypedDict):
    # ...
    docs_context_summary: list[DocumentSummary]  # 改为 dataclass
```

**不推荐方案 B**，因为：`DocumentSummary` 是内部实现细节，不应暴露在 state 层；dataclass 在序列化时可能有问题。

---

## 4. 综合修复路线图

### 4.1 修复优先级

```
P0 (必须修复，阻塞核心功能):
├── F3: MCP Schema 扩展 (create_deliverable + submit_execution_report)
├── F4: IndependentAgentInput 添加 docs_context 字段
├── F4: ContextManager.build_independent_input 传递 docs_context
└── F4: IndependentAgent.execute_with_input 读取 docs_context

P1 (重要修复，完善功能):
├── F3: DualAgentNode 多文档存储结构
├── F3: IndependentAgent 多文档提取逻辑
├── F5: Orchestrator 存储前调用 to_dict()
└── F5: 统一类型声明

P2 (优化改进):
└── F3: Validator 多文档验证规则
```

### 4.2 预计工作量

| 任务 | 工作量 | 风险 |
|------|--------|------|
| MCP Schema 扩展 | 2 小时 | 低 |
| F4 传递链修复 | 4 小时 | 中 (需测试所有节点) |
| F5 类型统一 | 1 小时 | 低 |
| DualAgentNode 多文档 | 6 小时 | 高 (涉及存储层) |
| 综合测试 | 4 小时 | 中 |
| **总计** | **~17 小时** | - |

### 4.3 验证检查点

修复完成后，需要通过以下验证：

1. **F3 验证**:
   ```python
   # 测试 MCP schema 暴露
   schema = get_create_deliverable_schema()
   assert "document_index" in schema["properties"]
   assert "document_total" in schema["properties"]
   assert "document_type" in schema["properties"]
   ```

2. **F4 验证**:
   ```python
   # 测试传递链
   execution_context = NodeExecutionContext(docs_context=[{"summary": "test"}])
   agent_input = context_manager.build_independent_input(execution_context)
   assert "docs_context" in agent_input
   assert agent_input["docs_context"] == [{"summary": "test"}]
   ```

3. **F5 验证**:
   ```python
   # 测试类型一致
   state = create_initial_state(..., docs_context_summary=[{"key": "value"}])
   assert all(isinstance(d, dict) for d in state["docs_context_summary"])
   ```

---

## 5. 附录

### 5.1 自动化分析工具

本报告基于自研的 `f3_f4_f5_deep_researcher.py` 工具生成，该工具能够：

1. 自动扫描代码库中的相关文件
2. 识别关键代码位置和类型声明
3. 追踪数据流路径
4. 生成结构化分析报告

使用方法：
```bash
python tools/f3_f4_f5_deep_researcher.py --verbose --output results.json
```

### 5.2 相关文件索引

| 文件 | 行号范围 | 相关 Issue |
|------|----------|------------|
| `tools/create_deliverable.py` | 24-91 | F3 |
| `tools/create_deliverable_sdk.py` | 243-320 | F3 |
| `agents/independent.py` | 545-573, 920-938 | F3, F4 |
| `nodes/dual_agent.py` | 284-336 | F3 |
| `context/isolation.py` | 120-175 | F4 |
| `node_execution/contracts.py` | 41-52 | F4 |
| `pipeline/state.py` | 77-121 | F5 |
| `agents/summary.py` | 564-581 | F5 |
| `pipeline/orchestrator.py` | 422-439 | F5 |

### 5.3 参考文档

- `docs/evaluation/2026-04-07-docuswarm-deep-reform-implementation-review.md`
- `docs/research/docuswarm-deep-reform/03-document-creation-constraints.md`
- `docs/research/docuswarm-deep-reform/06-summary-agent-design.md`
- `docs/research/docuswarm-deep-reform/07-docs-context-persistence.md`

---

**报告完成时间**: 2026-04-07  
**下次审查建议**: 修复完成后进行回归验证

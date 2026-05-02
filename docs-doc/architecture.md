---
**文档状态**: 🟡 迁移中 (In Migration)  
**最后更新**: 2026-03-17  
**对应决策**: F1-F8  
**说明**: 本文档已根据 2026-03-17 F1-F8 深度决策研究更新。
---

# DocuSwarm Architecture Document

> **Version**: 3.0 (Aligned with F1-F8 Decisions)  
> **Date**: 2026-03-17  
> **Status**: Phase 4 (P3) - Single Context Protocol Implementation

## 架构决策索引

参见 [DECISIONS.md](./DECISIONS.md) 获取当前生效的 F1-F8 架构决策详情。

| 决策 | 状态 | 架构影响 |
|------|------|----------|
| **F1** | 🟢 生效 | state_json 是业务真相源，checkpoint 仅运行辅助 |
| **F2** | 🟡 迁移中 | shared_context 贯穿写入-消费-恢复链路 |
| **F3** | 🟡 迁移中 | Evaluator 直接消费 EvaluatorAgentInput |
| **F4** | 🟢 生效 | docs-free，仅 3 个核心工具 |
| **F5** | 🟡 迁移中 | ToolResult 结构化协议 |
| **F8** | 🟢 生效 | 本文档已更新对齐 |
| **F9** | 🔴 新增 | SDK 消息类型检查必须使用 `isinstance()` |

**F9: SDK Message Type Checking (2026-04-06)**

| 决策 | 状态 | 说明 |
|------|------|------|
| **禁止使用 `getattr(msg, "role", "")`** | 🔴 强制 | `AssistantMessage` 无 `role` 属性，使用 `isinstance(msg, AssistantMessage)` |
| **禁止使用 `getattr(item, "type", "")`** | 🔴 强制 | `TextBlock` 无 `type` 属性，使用 `isinstance(item, TextBlock)` |
| **统一消息转换入口** | 🔴 强制 | 所有消息转换必须通过 `SessionManager._message_to_dict()` |

**参考**: [Kimi Message Extraction Fix](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md)

## 1. Architecture Overview

DocuSwarm is a **Multi-Agent Document Orchestration System** that automates the BMAD workflow through intelligent agent collaboration. The architecture follows the **Single Context Protocol** principle, ensuring a unified context contract across all layers.

### 1.1 Key Architectural Principles

1. **Single Source of Truth (F1)**: `state_json` is the sole business truth source; checkpoint is runtime recovery only
2. **Single Context Protocol**: `NodeExecutionContext` is the unified contract across executor → DualAgentNode → Agents
3. **Shared Context Propagation (F2)**: `shared_context` flows through write → consumption → recovery chains
4. **Context Isolation**: Three-layer defense prevents information leakage between Independent and Evaluator agents
5. **Dual-Agent Pattern**: Independent Agent (creation) + Evaluator Agent (review) ensures quality
6. **Pipeline-Centric Execution**: Pipeline orchestrates sequential node execution with automatic context chaining
7. **Tool-Written Artifacts**: File system is the single source of truth for deliverables
8. **Docs-Free Tools (F4)**: Only 3 core tools: `create_deliverable`, `update_context`, `create_document_set`
9. **Structured ToolResult (F5)**: Internal protocol uses structured dataclass, SDK boundary uses adapter

### 1.2 System Context Diagram (F1-F8 Aligned)

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Systems                          │
│  ┌─────────────┐  ┌─────────────────────────┐  ┌─────────────┐  │
│  │  Kimi K2.5  │  │  SQLite DB              │  │  File System│  │
│  │    LLM      │  │  ┌───────────────────┐  │  │  (output/)  │  │
│  └─────────────┘  │  │ state_json (Truth)│  │  └─────────────┘  │
│                   │  │ checkpoint (Aux)  │  │                   │
│                   │  └───────────────────┘  │                   │
│                   └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                        ▲                    ▲
                        │     F1: state_json │
                        │     is sole truth  │
                        └────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DocuSwarm Core System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  CLI Layer (Commands)                    │   │
│  │  docuswarm start --context │ status │ resume │ export    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Node Execution Layer                        │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │      NodeExecutionContextBuilder                 │    │   │
│  │  │  • Load node.yaml (name, description,            │    │   │
│  │  │    deliverable.required_sections)                │    │   │
│  │  │  • Parse state (context_file, chained_context)   │    │   │
│  │  │  • Build unified NodeExecutionContext            │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │                          │                               │   │
│  │                          ▼                               │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │      NodePromptContractBuilder                   │    │   │
│  │  │  • Build IndependentPromptContract               │    │   │
│  │  │  • Build EvaluatorPromptContract                 │    │   │
│  │  │  • Render system/user prompts                    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │                          │                               │   │
│  │                          ▼                               │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │           DualAgentNode                          │    │   │
│  │  │                                                  │    │   │
│  │  │  ┌─────────────────┐    ┌─────────────────┐    │    │   │
│  │  │  │ ContextManager  │    │ ContextFilter   │    │    │   │
│  │  │  │ • build_indep.  │───▶│ • filter_for_   │    │    │   │
│  │  │  │   _input()      │    │   evaluator()   │    │    │   │
│  │  │  │ • build_eval.   │    │                 │    │    │   │
│  │  │  │   _input()      │    │                 │    │    │   │
│  │  │  └─────────────────┘    └─────────────────┘    │    │   │
│  │  │           │                      │              │    │   │
│  │  │           ▼                      ▼              │    │   │
│  │  │  ┌─────────────────┐    ┌─────────────────┐    │    │   │
│  │  │  │ IndependentAgent│    │ EvaluatorAgent  │    │    │   │
│  │  │  │ • Create output │───▶│ • Review output │    │    │   │
│  │  │  │ • Use tools     │    │ • Score (0-1)   │    │    │   │
│  │  │  └─────────────────┘    └─────────────────┘    │    │   │
│  │  │                                                  │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              State Persistence Layer                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │ SQLite WAL  │  │  Deliverable│  │   Node Runs     │  │   │
│  │  │  Mode       │  │  Metadata   │  │   History       │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Core Components

### 2.1 NodePromptContractBuilder (Prompt Injection Layer)

New component for P0-2 that builds structured prompt contracts from NodeExecutionContext:

```python
class NodePromptContractBuilder:
    """Builds prompt contracts for Independent and Evaluator Agents."""
    
    def build_independent_contract(
        self, 
        context: NodeExecutionContext
    ) -> IndependentPromptContract:
        """Build contract with persona, task, deliverable, context sections."""
        
    def build_evaluator_contract(
        self, 
        context: NodeExecutionContext,
        deliverable_body: str
    ) -> EvaluatorPromptContract:
        """Build contract with task, criteria, deliverable sections."""
```

**Key Design Principle**: System prompt contains stable persona/instructions; User prompt contains dynamic task contract.

### 2.2 NodeExecutionContext (Unified Protocol)

The central data structure that flows through all layers:

```python
class NodeExecutionContext(TypedDict):
    # Identity
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    
    # Task Contract (from node.yaml)
    task_name: str              # <- node.name
    task_description: str       # <- node.description
    role_supplement: str        # <- "" (default for old schema)
    
    # Deliverable Contract (from node.yaml)
    deliverable_type: str
    deliverable_requirements: Dict  # <- node.deliverable.required_sections
    
    # Context Data (from state)
    original_context: Dict      # <- context_file
    chained_deliverables: List  # <- chained_context
    shared_context: Dict
    
    # Iteration & Extension
    iteration_feedback: Optional[Dict]
    docs_context: List[Dict]
```

**Design Constraints**:
- No `str(context_json)` passing between layers
- No field "guessing" in agents
- No duplicate wrapping/unwrapping

### 2.3 NodeExecutionContextBuilder

Responsible for constructing the unified context from node configuration and state:

```python
class NodeExecutionContextBuilder:
    def build(
        self,
        pipeline_id: str,
        node_id: str,
        original_context: Dict[str, Any],
        chained_deliverables: Optional[List] = None,
        # ...
    ) -> NodeExecutionContext:
        # 1. Load node.yaml via NodeLoader
        # 2. Map old schema to new fields
        # 3. Assemble unified context
```

**Old Schema Compatibility Mapping**:
- `task_name` ← `node.name`
- `task_description` ← `node.description`
- `role_supplement` ← `""` (default)
- `deliverable_requirements.required_sections` ← `node.deliverable.required_sections`

### 2.4 ContextManager

Transforms `NodeExecutionContext` into agent-specific inputs:

```python
class ContextManager:
    def build_independent_input(
        self,
        execution_context: NodeExecutionContext,
        iteration_feedback: Optional[Dict] = None
    ) -> IndependentAgentInput:
        # Extract and format fields for Independent Agent
        
    def build_evaluator_input(
        self,
        execution_context: NodeExecutionContext,
        deliverable: Dict[str, Any]
    ) -> EvaluatorAgentInput:
        # Extract and format fields for Evaluator Agent
        # Load full content from file_path if available
```

### 2.5 Dual-Agent Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    DualAgentNode                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Iteration Loop (max 3):                                     │
│                                                              │
│  1. Build Independent Input                                  │
│     └─▶ NodeExecutionContext ──▶ IndependentAgentInput      │
│                                                              │
│  2. Execute Independent Agent                                │
│     └─▶ Creates deliverable via tools                       │
│     └─▶ Returns deliverable metadata + questions            │
│                                                              │
│  3. Filter Context                                           │
│     └─▶ Remove private_reasoning                            │
│     └─▶ Validate no private fields leak                     │
│                                                              │
│  4. Build Evaluator Input                                    │
│     └─▶ Load full content from file_path                    │
│     └─▶ NodeExecutionContext ──▶ EvaluatorAgentInput        │
│                                                              │
│  5. Execute Evaluator Agent                                  │
│     └─▶ Scores deliverable (0-1)                            │
│     └─▶ Returns verdict: APPROVED/NEEDS_REVISION/BLOCKED    │
│                                                              │
│  6. Check Verdict                                            │
│     ├─▶ APPROVED ──▶ Exit loop                              │
│     ├─▶ BLOCKED ──▶ Exit loop                               │
│     └─▶ NEEDS_REVISION ──▶ Continue loop with feedback      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 3. Data Flow

### 3.0 State Persistence (F1)

```
┌─────────────────────────────────────────────────────────────┐
│                     State Management (F1)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Pipeline Execution          state_json (Business Truth)   │
│         │                      ┌──────────────────┐        │
│         │                      │ pipeline_id      │        │
│         │                      │ subject_context  │        │
│         ▼                      │ current_node     │        │
│   ┌─────────────┐              │ completed_nodes  │        │
│   │ create_pipe │─────────────▶│ deliverables     │        │
│   │   line()    │   UPDATE     │ questions        │        │
│   └─────────────┘              │ evaluations      │        │
│         │                      │ node_iterations  │        │
│         │                      │ session_ids      │        │
│         ▼                      │ shared_context   │◀──┐    │
│   ┌─────────────┐              │ status, error    │   │    │
│   │ Node Exec   │─────────────▶│                  │   │    │
│   │   ution     │   UPDATE     └──────────────────┘   │    │
│   └─────────────┘                                     │    │
│         │                                             │    │
│         │         checkpoint (Runtime Recovery)       │    │
│         │         ┌──────────────────┐                │    │
│         └────────▶│ LangGraph BLOB   │                │    │
│                   │ (msgpack)        │                │    │
│                   └──────────────────┘                │    │
│                                                       │    │
│                   F2: shared_context ◄────────────────┘    │
│                   written via update_context tool          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**F1 Principle**: All business decisions use `state_json`; `checkpoint` is only for runtime recovery.

### 3.1 Context Flow (Old vs New)

**Old Flow (Problems)**:
```
executor._extract_task_from_state()  # Guess task from JSON
       ↓ [unwrap/guess]
DualAgentNode.execute(subject, task)
       ↓ [wrap as {subject, task}]
ContextManager.build_independent_context()
       ↓ [pass wrapped]
IndependentAgent.execute()
       ↓ [unwrap/guess again]
Actual Usage (fragile)
```

**New Flow (Single Context Protocol)**:
```
NodeExecutionContextBuilder.build()
       ↓ [unified NodeExecutionContext]
DualAgentNode.execute_with_context()
       ↓ [pass through]
ContextManager.build_independent_input()  # Crop fields
       ↓ [structured input]
IndependentAgent.execute(agent_input)
       ↓ [direct field access]
Actual Usage (stable)
```

### 3.2 State Persistence

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Node Run      │────▶│   State Layer   │────▶│   File System   │
│   Execution     │     │   (SQLite)      │     │   (Truth)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ create_deliverable│    │ DeliverableArtifact│    │  *.md files    │
│ tool execution  │     │ metadata only    │     │  full content  │
│                 │     │ (title, summary, │     │                │
│                 │     │  file_path,     │     │                │
│                 │     │  sha256)        │     │                │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Principle**: File system is the single source of truth. State layer only stores metadata.

### 3.3 Shared Context Flow (F2)

```
update_context Tool (Agent Execution)
       │
       ▼
StateManager.update_shared_context()
       │
       ▼
state_json.shared_context (Persisted) ◄────┐
       │                                    │
       │    Next Node Execution             │
       │         │                          │
       │         ▼                          │
       │   ContextManager                   │
       │   .build_independent_input()       │
       │         │                          │
       │         ▼                          │
       │   IndependentAgentInput            │
       │   shared_context field ────────────┤
       │         │                          │
       │         ▼                          │
       │   IndependentAgent                 │
       │   .execute_with_input()            │
       │         │                          │
       └─────────┴──────────────────────────┘
                 │
                 ▼
    NodeExecutionContext.shared_context
                 │
                 ▼
    Prompt Contract Builder (included in prompt)
```

**F2 Status**: ⚠️ Write layer ✅, Transfer layer ✅, **Consumption layer needs fix** (see F2 report)

### 3.4 Evaluator Input Contract (F3)

```
ContextManager.build_evaluator_input()
       │
       ├──▶ Load full content from file_path (disk)
       │
       └──▶ EvaluatorAgentInput
              ├── task_name
              ├── task_description
              ├── original_context_summary  ◄── P0-2
              ├── deliverable_artifact (metadata)
              ├── deliverable_body (full content)  ◄── from disk
              └── criteria
```

**F3 Status**: ⚠️ Build layer ✅, **Consumption layer needs fix** (see F3 report)

### 3.5 Tools Layer (F4, F5)

```
┌─────────────────────────────────────────────────────────────┐
│                     Tools Package (F4/F5)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Internal Protocol (F5)                  │   │
│   │         ┌─────────────────────────┐                 │   │
│   │         │     ToolResult          │                 │   │
│   │         │  (structured dataclass) │                 │   │
│   │         └─────────────────────────┘                 │   │
│   │                      ▲                              │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────────┐     │   │
│   │   │  create  │  │  update  │  │    create    │     │   │
│   │   │_deliverab│  │_context  │  │_document_set │     │   │
│   │   │   le     │  │          │  │              │     │   │
│   │   └──────────┘  └──────────┘  └──────────────┘     │   │
│   │         │                │                │         │   │
│   │         └────────────────┴────────────────┘         │   │
│   │                          │                          │   │
│   │              SDK Adapter Layer                      │   │
│   │                    (Boundary)                       │   │
│   │                          │                          │   │
│   │                          ▼                          │   │
│   │              ToolOk / ToolError                     │   │
│   │         (SDK-specific, not internal)                │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   F4: Only 3 core tools (docs-free)                          │
│   F5: Internal uses ToolResult, SDK uses adapter             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.6 Async/Sync Contract (Phase A P0-1, P0-2, P1-1)

**核心原则**: 明确的异步边界，禁止嵌套事件循环。

```
┌─────────────────────────────────────────────────────────────┐
│                 Async/Sync Boundary Contract                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer              Pattern                Example           │
│  ─────────────────────────────────────────────────────────  │
│  CLI Entry          sync def               commands/*.py      │
│  └─▶ asyncio.run()                                             │
│                                                              │
│  Service Layer      async def              PipelineService    │
│  └─▶ await async_func()                                        │
│                                                              │
│  Orchestrator       async def              HybridOrchestrator │
│  └─▶ await state_manager.update_*()                            │
│                                                              │
│  State Manager      sync def               StateManager       │
│  └─▶ sqlite3 operations (sync only)                            │
│                                                              │
│  Bridge (Banned)    ❌ _run_async()         REMOVED (P0-2)   │
│  └─▶ ThreadPoolExecutor + asyncio.run                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**契约规则**:
1. **CLI 是唯一同步边界**: 只有 `cli/commands/*.py` 使用 `asyncio.run()`
2. **服务层全异步**: `PipelineService`, `HybridOrchestrator` 全部是 `async def`
3. **StateManager 全同步**: 数据库操作使用同步接口，上层通过 `await` 调用
4. **禁止 _run_async bridge**: 任何 `ThreadPoolExecutor + asyncio.run` 模式都被禁止
5. **必须 await 异步函数**: 如 `escalation_handler.escalate()` 必须被 `await`

**修复状态 (Phase A)**:
| 问题 | 位置 | 修复前 | 修复后 |
|------|------|--------|--------|
| P0-1 | orchestrator.py:328,391 | `asyncio.run(...)` | `await ...` |
| P0-2 | pipeline_service.py:20-39 | `def _run_async(): ...` | **REMOVED** |
| P0-2 | pipeline_service.py:129,163 | `def cancel(): ...` | `async def cancel(): ...` |
| P1-1 | dual_agent.py:807,845 | `self.escalation_handler.escalate(...)` | `await self.escalation_handler.escalate(...)` |

**参考文档**:
- [Phase A/B Technical Debt Research](../research/phase_a_b_technical_debt_research_report.md)
- [Phase A/B TDD Solution](../solution/phase_a_b_test_driven_solution_plan.md)
- [P0-1 Regression Test](../../tests/architecture/test_p0_1_asyncio_run_regression.py)
- [P0-3 Async Contract Test](../../tests/architecture/test_p0_3_async_sync_contract.py)

## 4. Context Isolation

### 4.1 Three-Layer Defense

| Layer | Mechanism | Implementation |
|-------|-----------|----------------|
| **Layer 1** | Separate Prompt Templates | Different system prompts for Independent vs Evaluator |
| **Layer 2** | Runtime Access Control | `ContextManager` crops fields based on agent type |
| **Layer 3** | Message-Level Filtering | `ContextFilter` removes private fields before passing to Evaluator |

### 4.2 Private Fields

The following fields are considered private and must never reach Evaluator:
- `private_reasoning`
- `tool_call_history`
- `iteration_feedback`
- `internal_notes`

## 5. Component Interactions

### 5.1 Sequence Diagram

```
User          CLI          Executor    ContextBuilder  DualAgentNode   ContextManager   IndependentAgent
 |              |              |              |              |              |              |
 |──start node─▶|              |              |              |              |              |
 |              |──execute───▶|              |              |              |              |
 |              |              |──build ctx──▶|              |              |              |
 |              |              |              │──NodeExecutionContext──▶|              |
 |              |              |◀─────────────│              |              |              |
 |              |              │──────────NodeExecutionContext──────────▶|              |
 |              |              |              |              │──build input▶|              |
 |              |              |              |              |              │──execute───▶|
 |              |              |              |              |              |              │──create
 |              |              |              |              |              |              │  deliverable
 |              |              |              |              |              |◀─────────────│
 |              |              |              |              |◀─────────────│              |
 |              |              |◀─────────────────────────────│              |              |
 |              |◀────────────────────────────────────────────│              |              |
 |◀──────────────────────────────────────────────────────────│              |              |
```

## 6. Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Core implementation |
| Framework | LangGraph | Latest | State machine & orchestration |
| LLM | Kimi K2.5 | Latest | Document generation & evaluation |
| SDK | claude-agent-sdk | Latest | LLM interaction |
| Database | SQLite | 3.35+ | State persistence (WAL mode) |
| Checkpointing | LangGraph SqliteSaver | Latest | Resume capability |

## 7. Implementation Status (F1-F8 & TD-1~TD-5)

### TD-1: State Duplication Resolution (P0) 🟡

- **Status**: In Progress (TDD Phase 2)
- **Problem**: current_node 重复表示在 pipelines 表和 state_json
- **Solution**: state_json 为唯一业务真相源
- **TDD Reference**: [P0/P1 TDD Master Plan](solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md#31-td-1-state_json-唯一真相源)
- **Key Changes**:
  - `StateManager.create_pipeline()` writes full `PipelineState`
  - `StateManager.update_pipeline_status()` syncs to state_json
  - `Orchestrator.resume_pipeline()` reads from state_json
  - `pipelines.current_node` becomes derived field only

### TD-2: Tool Layer CWD Decoupling (P0) 🟡

- **Status**: In Progress (TDD Phase 1)
- **Problem**: Tools depend on `Path.cwd()`, tests use `os.chdir()`
- **Solution**: Explicit `output_dir` injection
- **TDD Reference**: [P0/P1 TDD Master Plan](solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md#21-td-2-工具层-pathcwd-解耦)
- **Key Changes**:
  - `CreateDeliverableTool(output_dir: Path | None)`
  - `CreateDocumentSetTool(output_dir: Path | None)`
  - Tests use temp dir fixtures instead of `os.chdir()`

### TD-3: Models Compatibility Layer (P1) 🟡

- **Status**: In Progress (TDD Phase 1)
- **Problem**: `models` module on main path with import-time warnings
- **Solution**: Remove or lazy deprecation
- **TDD Reference**: [P0/P1 TDD Master Plan](solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md#22-td-3-models-兼容层清理)
- **Key Changes**:
  - Remove `autoBMAD/docuswarm/models/` directory
  - Update all imports to use `tools` directly

### TD-4: Execution Skeleton Convergence (P1) 🟡

- **Status**: Planning (TDD Phase 4)
- **Problem**: pipeline/node_execution/nodes skeleton duplication
- **Solution**: Single boundary adapter
- **TDD Reference**: [P0/P1 TDD Master Plan](solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md#51-td-4-执行骨架收敛)
- **Key Changes**:
  - Create `PipelineAdapter` boundary layer
  - Synthetic ID logic restricted to adapter
  - No new parallel modules

### TD-5: CLI Refactoring (P1) 🟡

- **Status**: In Progress (TDD Phase 3)
- **Problem**: main.py 825 lines, 0% coverage
- **Solution**: Split to commands/* + services/*
- **TDD Reference**: [P0/P1 TDD Master Plan](solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md#41-td-5-cli-拆分)
- **Key Changes**:
  - `cli/commands/` - Command definitions
  - `cli/services/` - Business logic
  - `main.py` < 100 lines
  - Smoke tests for all commands

### F1: State Persistence ✅

- **Status**: Decision made, implementation in progress (aligned with TD-1)
- **Key Changes**:
  - `state_json` stores full `PipelineState`
  - `checkpoint` is runtime recovery only
  - Resume/restart read from `state_json`

### F2: Shared Context 🔄

- **Status**: Write✅, Transfer✅, **Consume❌ needs fix**
- **Fix Required**: `IndependentAgent.execute_with_input()` line 681
- **Change**: `shared_context={}` → `shared_context=agent_input.get("shared_context", {})`

### F3: Evaluator Input 🔄

- **Status**: Build✅, **Consume❌ needs fix**
- **Fix Required**: `EvaluatorAgent.execute_with_input()` lines 571-573
- **Change**: Stop rebuilding empty context, use `EvaluatorAgentInput` directly

### F4: Tools Convergence ✅

- **Status**: Decision made, cleanup pending
- **Actions**:
  - Remove `parse_deliverable_metadata`
  - Merge `ToolRegistry` into single API
  - Confirm YAML config has only 3 tools

### F5: ToolResult Protocol 🔄

- **Status**: Protocol defined✅, **Migration pending**
- **Actions**:
  - Tools return `ToolResult` internally
  - SDK adapter converts to `ToolOk`/`ToolError`
  - Remove `ToolOk` from internal protocol

### F9: SDK Message Type Checking 🔴

- **Status**: Critical fix required (2026-04-06)
- **Problem**: Code incorrectly assumes SDK message objects have `role` attribute
- **Root Cause**: `AssistantMessage`, `TextBlock` etc. have no `role`/`type` attributes in `claude_agent_sdk v0.1.68`
- **Impact**: All messages filtered, pipeline returns empty responses
- **Solution**:
  - Use `isinstance(msg, AssistantMessage)` instead of `getattr(msg, "role", "")`
  - Use `isinstance(item, TextBlock)` instead of `getattr(item, "type", "")`
  - Unified message conversion via `SessionManager._message_to_dict()`
- **Files Affected**:
  - `llm/response.py` - `extract_text_from_messages()`
  - `llm/session_manager.py` - `_message_to_dict()`
  - `agents/independent.py` - Message handling
- **TDD Reference**: [Message Extraction TDD Plan](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md)
- **Root Cause Analysis**: [Research Report](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md)

## 8. Migration Path

### Phase 4 (P3) - Single Context Protocol + F1-F3 Fixes

1. **Step 1**: F1 - Update `StateManager` to write full `PipelineState` to `state_json`
2. **Step 2**: F1 - Update `orchestrator.py` resume/restart to use `state_json`
3. **Step 3**: F2 - Fix `IndependentAgent.execute_with_input()` to read `shared_context`
4. **Step 4**: F3 - Fix `EvaluatorAgent.execute_with_input()` to use `EvaluatorAgentInput` directly
5. **Step 5**: Create `NodePromptContractBuilder` and update Agents
6. **Step 6**: Verify all nodes include contract info in prompts

1. **Step 1**: Create `contracts.py` and `context_builder.py`
2. **Step 2**: Update `executor.py` to use `NodeExecutionContextBuilder`
3. **Step 3**: Update `DualAgentNode` to receive `execution_context`
4. **Step 4**: Update `ContextManager` methods
5. **Step 5**: Create `NodePromptContractBuilder` and update Agents
6. **Step 6**: Update `IndependentAgent` and `EvaluatorAgent` to use contracts
7. **Step 7**: Verify all nodes include contract info in prompts

### Phase 5 (P4) - Node Prompt Injection

1. **Step 1**: Create `prompts/contract_builder.py` with TDD
2. **Step 2**: Update `IndependentAgent._format_system_prompt()` to support contract
3. **Step 3**: Update Agents to use contract builder for prompt rendering
4. **Step 4**: Verify prompt differences come from node.yaml contract, not just persona

### Completion Criteria

- [ ] No `_extract_task_from_state()` in codebase
- [ ] No `{subject, task}` wrapping in `DualAgentNode`
- [ ] No JSON parsing/unwrapping in `IndependentAgent`
- [ ] Node contract (name, description, required_sections) in every prompt
- [ ] Prompt differences come from node.yaml, not just persona
- [ ] `NodePromptContractBuilder` implemented with TDD
- [ ] Independent/Evaluator use contract-based prompt rendering

## 9. References

### TD-1~TD-5 技术债务文档 (2026-03-18)

- [技术债务评估报告](./evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md) - P0/P1 问题评估
- [技术债务深度研究报告](research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md) - 深度研究
- [P0/P1 TDD 主方案](../solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md) - 测试驱动实施方案
- [P0/P1 TDD 执行摘要](../solution/2026-03-18-docuswarm-p0-p1-tdd-execution-summary.md) - 快速参考

### F1-F9 决策文档

- [DECISIONS.md](./DECISIONS.md) - 架构决策索引
- [F1-F8 深度决策研究报告](research/2026-03-17-docuswarm-decision-research-report.md)
- [F1 状态持久化研究](research/2026-03-17-F1-state-persistence-research-report.md)
- [F2 Shared Context 研究](research/2026-03-17-F2-shared-context-research-report.md)
- [F3 Evaluator 输入契约研究](research/2026-03-17-F3-evaluator-input-contract-research-report.md)
- [F4 工具层收敛研究](research/2026-03-17-F4-tools-convergence-research-report.md)
- [F5 ToolResult 协议研究](research/2026-03-17-F5-toolresult-protocol-research-report.md)
- **F9 SDK Message Type Checking**:
  - [Root Cause Analysis](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md)
  - [Test-Driven Fix Plan](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md)

### 历史参考 (已归档)

- [NodeExecutionContext 深度研究报告](research/2026-03-13-p0-single-context-protocol-deep-research-report.md) 🗄️
- [方案B实施设计](research/2026-03-13-p0-single-context-protocol-implementation-design.md) 🗄️
- [节点Prompt注入计划](research/2026-03-13-p0-node-prompt-injection-plan.md) 🗄️
- [节点Prompt契约构建器TDD方案](../solution/TDD-P0-NodePromptContractBuilder.md) 🗄️
- [P0 重构总览](research/2026-03-13-docuswarm-context-refactor-overview.md) 🗄️
- [上下文注入审计](research/2026-03-13-context-injection-audit.md) 🗄️
- [PRD](plan/PRD.md)

# DocuSwarm Node Execution Architecture

**Version**: 2.3 (BMM NodeExecutor Refactor)  
**Date**: 2026-03-02  
**Status**: Approved  
**Author**: Solution Architect  

> **Note**: 本文档已更新以反映 BMM NodeExecutor 重构后的架构。详见 [TDD-BMM-01](../solution/TDD-BMM-01-NodeLoader-Config-Refactor.md) 和 [TDD-BMM-03](../solution/TDD-BMM-03-Deprecated-Code-Removal.md)。  

---

## 1. Overview

This document details the node execution architecture using LangGraph StateGraph for individual BMAD workflow node execution with context chaining.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **User-Driven** | User explicitly selects which node to execute |
| **Checkpoint Native** | LangGraph checkpointing for node run recovery |
| **Node Encapsulation** | Each node is self-contained |
| **State Immutable** | State updates via reducer functions |

### 1.2 BMAD Nodes

| Node | Phase | Deliverable |
|------|-------|-------------|
| **Analyst** | 1-Analysis | Analyst Report |
| **PM** | 2-Planning | PRD |
| **UX** | 2-Planning | UX Design |
| **Architect** | 3-Solutioning | Architecture Document |
| **PO** | 3-Solutioning | Epics and Stories |

---

## 2. Node Execution Architecture

> **P0-2 Update**: 节点执行现已收敛到单主干模式。
> - 唯一活跃实现: `node_execution/executor.py:create_node_executor`
> - 唯一图工厂: `pipeline/graph.py:create_pipeline_graph`
> - 历史路径 (`node_execution/graph.py`, `node_execution/flow.py`, `nodes/dual_agent.py:create_node_executor`) 已物理删除
> See: [P0-2/P0-3 Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md)

### 2.1 High-Level Flow

```
User Command: docuswarm start <node> --context <file>
    │
    ▼
Context Loader (read file, compute context_hash)
    │
    ▼
Context Chaining (auto-inject predecessor deliverables for same context_hash)
    │
    ▼
LangGraph StateGraph (single node execution)
    │
    ▼
Dual-Agent Loop (Independent → Evaluator → iterate if needed, max 3)
    │
    ▼
Node Run Output (deliverable, questions, evaluation → stored in node_runs)
```

### 2.2 LangGraph StateGraph Definition

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        StateGraph Structure                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  graph = StateGraph(NodeRunState)                                           │
│                                                                             │
│  Nodes:                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  graph.add_node("independent_agent", independent_agent_fn)            │ │
│  │  graph.add_node("context_filter", context_filter_fn)                  │ │
│  │  graph.add_node("evaluator_agent", evaluator_agent_fn)                │ │
│  │  graph.add_node("iteration_router", iteration_router_fn)              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Entry Point:                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  graph.set_entry_point("independent_agent")                           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Edges:                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  graph.add_edge("independent_agent", "context_filter")                │ │
│  │  graph.add_edge("context_filter", "evaluator_agent")                  │ │
│  │  graph.add_edge("evaluator_agent", "iteration_router")                │ │
│  │                                                                        │ │
│  │  # Conditional edges from iteration_router:                           │ │
│  │  # - APPROVED → END                                                   │ │
│  │  # - NEEDS_REVISION → independent_agent (iterate)                     │ │
│  │  # - BLOCKED → END                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Checkpointer:                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  checkpointer = SqliteSaver.from_conn_string("docuswarm.db")         │ │
│  │  compiled = graph.compile(checkpointer=checkpointer)                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Node Run State

### 3.1 State Schema

```python
from typing import TypedDict, List, Dict, Optional, Annotated
import operator

class NodeRunState(TypedDict):
    # Run identification
    run_id: str
    node: str  # analyst | pm | ux | architect | po
    
    # Context tracking
    context_hash: str
    context_data: dict
    chained_deliverables: Dict[str, str]  # predecessor_node -> deliverable
    
    # Iteration tracking
    iteration: int
    max_iterations: int
    
    # Results storage
    deliverable: Optional[dict]
    questions: Optional[List[dict]]
    private_reasoning: Optional[str]
    evaluation: Optional[dict]
    
    # Run status
    status: str  # pending | running | completed | failed | blocked
```

### 3.2 State Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    State Flow Through Node Iterations                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Initial State                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  {                                                                     │ │
│  │    run_id: "a3f7b2c1",                                                │ │
│  │    node: "pm",                                                        │ │
│  │    context_hash: "abc123...",                                         │ │
│  │    context_data: { project_name: "...", requirements: [...] },       │ │
│  │    chained_deliverables: {                                            │ │
│  │      analyst: { title: "...", content: "..." }                       │ │
│  │    },                                                                 │ │
│  │    iteration: 0,                                                      │ │
│  │    max_iterations: 3,                                                 │ │
│  │    deliverable: null,                                                 │ │
│  │    questions: null,                                                   │ │
│  │    evaluation: null,                                                  │ │
│  │    status: "pending"                                                  │ │
│  │  }                                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                          │                                                  │
│                          ▼                                                  │
│  After Iteration 1                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  {                                                                     │ │
│  │    ...                                                                │ │
│  │    iteration: 1,                                                      │ │
│  │    deliverable: { title: "PRD v1", content: "..." },                 │ │
│  │    questions: [{ id: "q1", category: "blocking", ... }],             │ │
│  │    evaluation: {                                                      │ │
│  │      alignment_score: 0.65,                                           │ │
│  │      verdict: "NEEDS_REVISION",                                       │ │
│  │      feedback: "Add user stories section"                            │ │
│  │    },                                                                 │ │
│  │    status: "running"                                                  │ │
│  │  }                                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                          │                                                  │
│                          ▼                                                  │
│  After Iteration 2 (Approved)                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  {                                                                     │ │
│  │    ...                                                                │ │
│  │    iteration: 2,                                                      │ │
│  │    deliverable: { title: "PRD v2", content: "..." },                 │ │
│  │    evaluation: {                                                      │ │
│  │      alignment_score: 0.87,                                           │ │
│  │      verdict: "APPROVED"                                              │ │
│  │    },                                                                 │ │
│  │    status: "completed"                                                │ │
│  │  }                                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Node Execution

### 4.1 Node Function Template

```python
async def execute_node(state: NodeRunState) -> NodeRunState:
    """Template for node execution function."""
    
    node_id = state["node"]  # Current node identifier
    
    # 1. Load node configuration
    config = load_node_config(node_id)
    
    # 2. Build context for Independent Agent
    context = {
        "context_data": state["context_data"],
        "chained_deliverables": state["chained_deliverables"]
    }
    
    # 3. Execute dual-agent pattern
    dual_node = DualAgentNode(node_id, config)
    result = await dual_node.execute(context)
    
    # 4. Return state updates (immutable)
    return {
        "iteration": state["iteration"] + 1,
        "deliverable": result["deliverable"],
        "questions": result["questions"],
        "evaluation": result["evaluation"],
        "private_reasoning": result["private_reasoning"],
        "status": "running" if result["verdict"] == "NEEDS_REVISION" else "completed"
    }
```

### 4.2 Node Configuration (BMM-Aligned Format)

```yaml
# nodes/analyst/node.yaml (Schema v2.1)
schema_version: "2.1"
node_id: analyst
name: Analyst
sequence: 1

# Agent configuration
agent:
  type: independent
  model: sonnet
  temperature: 0.7

# Task configuration (from BMM workflow)
task:
  name: create-business-analysis-report
  description: Transform raw data into actionable business insights
  role_supplement: Focus on evidence-based conclusions

# Deliverable configuration with extended fields
deliverable:
  type: analyst-report
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
  template_title: "Business Analysis Report"           # EXTENDED
  output_filename: "analyst-report.md"                 # EXTENDED
  format_hints:                                        # EXTENDED
    max_words: 3000
    target_audience: "Product and Engineering teams"
    tone: "analytical, evidence-based"

# Evaluator configuration (INLINE - 2026-03-28)
evaluator:
  criteria_file: evaluator.yaml                        # Reference to criteria file
  threshold:                                           # Renamed from thresholds
    approval: 0.70
    escalation: 0.50
  max_iterations: 3
  model: sonnet                                        # Optional override

# Tool Permissions (2026-03-28)
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs:
      - "docs/"
      - "docs/research/"
  search_permissions:
    search_dirs:
      - "docs/"
```

#### NodeDeliverableConfig Extended Fields

**Data Class Definition**:
```python
@dataclass
class NodeDeliverableConfig:
    """Configuration for the node's deliverable (v2.1)."""
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)
    template_title: str | None = None      # EXTENDED: Dynamic title template
    output_filename: str | None = None     # EXTENDED: Output file name pattern
    format_hints: dict[str, Any] = field(default_factory=dict)  # EXTENDED: Format guidance
```

#### NodeEvaluatorConfig Inline Structure

> **2026-04-03 P0 Fix Update**: `max_iterations` 现在从节点配置自动注入运行时，配置即行为。

**Data Class Definition**:
```python
@dataclass
class NodeEvaluatorConfig:
    """Configuration for the evaluator agent (v2.1)."""
    criteria: list[dict[str, Any]] = field(default_factory=list)
    threshold: dict[str, float] = field(default_factory=dict)  # Renamed from thresholds
    max_iterations: int = 3
    model: str | None = None           # NEW: Optional model override
    criteria_file: str | None = None   # NEW: Reference to external criteria file
```

**Configuration Loading**:
```python
# NodeLoader merges inline config with external file
evaluator_data = config.get("evaluator", {})
if evaluator_data.get("criteria_file"):
    file_evaluator = load_yaml(evaluator_data["criteria_file"])
    # node.yaml takes precedence over file
    evaluator_data = {**file_evaluator, **evaluator_data}
```

**Runtime Consumption (P0 Fix)**:
```python
# create_dual_agent_node() now loads max_iterations from node config
def create_dual_agent_node(
    config: AgentConfig,
    session_manager: SessionManager,  # P1-2: Use SessionManager (KimiSessionManager removed)
    node_id: str,
    max_iterations: int | None = None,  # P0 Fix: None triggers config loading
) -> DualAgentNode:
    # P0 Fix: Load max_iterations from node config if not explicitly provided
    if max_iterations is None:
        try:
            node_config = NodeLoader.load(node_id)
            if node_config.evaluator:
                max_iterations = node_config.evaluator.max_iterations
            else:
                max_iterations = DualAgentNode.DEFAULT_MAX_ITERATIONS
        except Exception:
            max_iterations = DualAgentNode.DEFAULT_MAX_ITERATIONS
    
    # ... create DualAgentNode with config-driven max_iterations
```

**Priority**: 显式参数 > 节点配置 > 默认值 (`DEFAULT_MAX_ITERATIONS = 3`)

**References**:
- [NodeDeliverableConfig Extension](../research/refactor-2026-03-28-implementation-requirements.md#5-nodedeliverableconfig-扩展字段)
- [Evaluator Inline Config](../research/refactor-2026-03-28-implementation-requirements.md#2-nodeyaml-evaluator-内联引用段)
- [P0 Runtime Consumption Fix](../solution/2026-04-03-p0-runtime-consumption-test-driven-plan.md)

#### Configuration Changes Summary

| Aspect | Old Format | New Format | Rationale |
|--------|-----------|------------|-----------|
| **description** | Top-level field | Moved to `task.description` | Better organization |
| **questions** | `questions` block | Removed | Auto-generated by Agent |
| **dependencies** | `dependencies` block | Removed | Managed by graph edges |
| **task** | N/A | New block | BMM workflow alignment |
| **template_title** | N/A | New field | Dynamic title generation |
| **output_filename** | N/A | New field | Consistent file naming |
| **template** | Path to external file | Removed | Embedded in deliverable block |

> **Migration**: Old format without `task` block is still supported for backward compatibility.

> **Reference**: [TDD-BMM-01: NodeLoader 配置加载系统重构](../solution/TDD-BMM-01-NodeLoader-Config-Refactor.md)

---

## 5. Checkpoint and Resume

### 5.1 Checkpoint Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Checkpoint Architecture                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LangGraph Automatic Checkpointing                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Each iteration automatically creates a checkpoint                    │ │
│  │                                                                        │ │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                          │ │
│  │  │Iteration│───▶│Checkpoint│───▶│  Next   │                          │ │
│  │  │  Exec   │    │  Save   │    │Iteration│                          │ │
│  │  └─────────┘    └─────────┘    └─────────┘                          │ │
│  │                      │                                                │ │
│  │                      ▼                                                │ │
│  │               ┌─────────────┐                                        │ │
│  │               │   SQLite    │                                        │ │
│  │               │  Database   │                                        │ │
│  │               └─────────────┘                                        │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Checkpoint Data Structure                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  {                                                                     │ │
│  │    "id": "checkpoint_uuid",                                           │ │
│  │    "thread_id": "{node}_{run_id}",                                    │ │
│  │    "ts": "2026-02-20T10:30:00Z",                                     │ │
│  │    "channel_values": {                                                │ │
│  │      "node_run_state": { ... full state ... }                        │ │
│  │    },                                                                 │ │
│  │    "parent_config": {                                                 │ │
│  │      "configurable": {                                               │ │
│  │        "checkpoint_id": "previous_checkpoint_uuid"                   │ │
│  │      }                                                                │ │
│  │    }                                                                  │ │
│  │  }                                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Resume Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Resume Flow                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Load Last Checkpoint                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  thread_id = f"{node}_{run_id}"                                       │ │
│  │  config = {"configurable": {"thread_id": thread_id}}                 │ │
│  │  # LangGraph automatically finds latest checkpoint                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                          │                                                  │
│                          ▼                                                  │
│  Step 2: Resume Execution                                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  # Pass None to resume from checkpoint                               │ │
│  │  result = await compiled_graph.ainvoke(None, config)                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                          │                                                  │
│                          ▼                                                  │
│  Step 3: Continue from Next Iteration                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Node run resumes from where it left off                             │ │
│  │                                                                        │ │
│  │  Example:                                                             │ │
│  │  iteration: 1, verdict: "NEEDS_REVISION"                             │ │
│  │  ───▶ Resume starts iteration 2                                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Checkpoint History

```python
async def get_checkpoint_history(node: str, run_id: str) -> List[dict]:
    """Get checkpoint history for debugging and auditing."""
    thread_id = f"{node}_{run_id}"
    config = {"configurable": {"thread_id": thread_id}}
    
    checkpoints = []
    for checkpoint in checkpointer.list(config):
        checkpoints.append({
            "id": checkpoint.id,
            "timestamp": checkpoint.ts,
            "iteration": checkpoint.channel_values.get("iteration"),
            "verdict": checkpoint.channel_values.get("evaluation", {}).get("verdict"),
            "parent_id": checkpoint.parent_config.get("configurable", {}).get("checkpoint_id")
        })
    
    return checkpoints
```

---

## 6. Error Handling

### 6.1 Node-Level Errors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Node-Level Error Handling                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Error Types and Recovery                                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Error Type          │ Recovery Strategy                              │ │
│  │  ─────────────────────────────────────────────────────────────────── │ │
│  │  LLM API Error       │ Retry with backoff (3 attempts)               │ │
│  │  Invalid JSON        │ Retry with guidance                           │ │
│  │  Quality Failure     │ Iterate (up to 3 times)                       │ │
│  │  Max Iterations      │ Force complete or escalate                    │ │
│  │  Unexpected Error    │ Checkpoint and pause                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Node Wrapper with Error Handling                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  async def safe_node_execution(node_fn, state):                       │ │
│  │      try:                                                             │ │
│  │          return await node_fn(state)                                  │ │
│  │      except RetryableError as e:                                      │ │
│  │          # Retry logic handled by agent executor                      │ │
│  │          raise                                                        │ │
│  │      except NonRetryableError as e:                                   │ │
│  │          # Mark run as failed, preserve checkpoint               │ │
│  │          return {                                                     │ │
│  │              **state,                                                 │ │
│  │              "status": "failed",                                      │ │
│  │              "error": str(e)                                          │ │
│  │          }                                                            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Run-Level Error Handling

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Run-Level Error Handling                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Error Escalation Path                                                      │
│                                                                             │
│  Node Error                                                                 │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────┐                                                       │
│  │ Retry at Node   │  ← Up to 3 retries                                    │
│  └────────┬────────┘                                                       │
│           │ Still failing                                                   │
│           ▼                                                                 │
│  ┌─────────────────┐                                                       │
│  │ Iterate Node    │  ← Up to 3 iterations                                 │
│  └────────┬────────┘                                                       │
│           │ Quality issues persist                                          │
│           ▼                                                                 │
│  ┌─────────────────┐                                                       │
│  │ Force Complete  │  ← If score >= 0.50                                   │
│  │ with Warning    │                                                       │
│  └────────┬────────┘                                                       │
│           │ Score < 0.50                                                    │
│           ▼                                                                 │
│  ┌─────────────────┐                                                       │
│  │  Mark Run Failed│  ← Save checkpoint                                    │
│  │ Escalate to User│                                                       │
│  └─────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Node Run Operations

### 7.1 Start Node Run

```python
async def start_node_run(node: str, context_file: str, no_chain: bool = False) -> str:
    """Start a new node execution run."""
    import uuid
    import hashlib
    
    # 1. Generate run ID
    run_id = str(uuid.uuid4())[:8]
    
    # 2. Load and hash context
    context_data = load_context_file(context_file)
    context_hash = hashlib.sha256(
        json.dumps(context_data, sort_keys=True).encode()
    ).hexdigest()
    
    # 3. Auto-inject predecessor deliverables (context chaining)
    chained = {}
    if not no_chain:
        chained = load_predecessor_deliverables(node, context_hash)
    
    # 4. Create initial state
    initial_state: NodeRunState = {
        "run_id": run_id,
        "node": node,
        "context_hash": context_hash,
        "context_data": context_data,
        "chained_deliverables": chained,
        "iteration": 0,
        "max_iterations": 3,
        "deliverable": None,
        "questions": None,
        "private_reasoning": None,
        "evaluation": None,
        "status": "pending"
    }
    
    # 5. Configure thread for checkpointing
    thread_id = f"{node}_{run_id}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # 6. Execute node
    result = await compiled_graph.ainvoke(initial_state, config)
    
    # 7. Store run in database
    await store_node_run(result)
    
    return run_id


def load_predecessor_deliverables(node: str, context_hash: str) -> dict:
    """Load predecessor node deliverables for context chaining."""
    SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    current_idx = SEQUENCE.index(node)
    previous_nodes = SEQUENCE[:current_idx]
    
    chained = {}
    for prev_node in previous_nodes:
        latest_run = db.execute(
            "SELECT deliverable FROM node_runs "
            "WHERE node_id = ? AND context_hash = ? AND status = 'completed' "
            "ORDER BY created_at DESC LIMIT 1",
            (prev_node, context_hash)
        ).fetchone()
        
        if latest_run and latest_run["deliverable"]:
            chained[f"{prev_node}_deliverable"] = json.loads(latest_run["deliverable"])
        else:
            logger.warning(f"⚠ No successful run found for {prev_node}")
    
    return chained
```

### 7.2 Get Node Status

```python
async def get_node_status(node: str, context_hash: str, run_id: str = None) -> dict:
    """Get current node run status."""
    
    # If no run_id specified, get latest run for this node + context
    if not run_id:
        latest = db.execute(
            "SELECT * FROM node_runs "
            "WHERE node_id = ? AND context_hash = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (node, context_hash)
        ).fetchone()
        
        if not latest:
            raise NodeRunNotFoundError(node, context_hash)
        
        run_id = latest["run_id"]
        state = latest
    else:
        state = db.execute(
            "SELECT * FROM node_runs WHERE run_id = ?",
            (run_id,)
        ).fetchone()
        
        if not state:
            raise NodeRunNotFoundError(run_id=run_id)
    
    # Parse evaluation
    evaluation = json.loads(state["evaluation"]) if state["evaluation"] else {}
    
    return {
        "run_id": run_id,
        "node": state["node_id"],
        "status": state["status"],
        "iteration": state["iteration"],
        "max_iterations": 3,
        "verdict": evaluation.get("verdict"),
        "alignment_score": evaluation.get("alignment_score"),
        "created_at": state["created_at"],
        "updated_at": state["updated_at"]
    }
```

---

## 8. Context Validator

> **Implementation**: [TDD-02: ContextValidator 提取](../solution/TDD-02-ContextValidator-Refactor.md)
> 
> The ContextValidator is being extracted from HybridOrchestrator as part of the P0 refactoring.

### 8.1 Context Validation Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Context Validator                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      LLM Component                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Model: Kimi K2.5 (Instant Mode)                                │  │ │
│  │  │  Temperature: 0.3                                               │  │ │
│  │  │  Purpose: Context validation, completeness check                │  │ │
│  │  │                                                                 │  │ │
│  │  │  Responsibilities:                                              │  │ │
│  │  │  • Validate subject context completeness                       │  │ │
│  │  │  • Identify missing critical information                       │  │ │
│  │  │  • Suggest initial questions if context insufficient          │  │ │
│  │  │  • Compute context hash for chaining                           │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Context Validator Implementation (Refactored)

```python
# New: pipeline/context_validator.py (TDD-02)
@dataclass
class ValidationResult:
    """Result of context validation."""
    valid: bool
    reason: str
    missing_info: list[str]
    raw_response: str | None = None
    attempts: int = 1
    fallback_used: bool = False

class ContextValidator:
    """Context file validator using LLM for completeness check.
    
    Extracted from HybridOrchestrator to follow Single Responsibility Principle.
    Implements structured retry logic and configurable error handling.
    
    Ref: TDD-02
    """
    
    DEFAULT_MAX_RETRIES = 2  # Total 3 attempts
    DEFAULT_FAIL_OPEN = False  # Safer default
    
    def __init__(
        self,
        session_manager: SessionManager,  # Now uses SessionManager (TDD-05)
        prompt_template: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        fail_open: bool = DEFAULT_FAIL_OPEN,
    ) -> None:
        self._session_manager = session_manager
        self._prompt_template = prompt_template or DEFAULT_VALIDATION_PROMPT
        self._max_retries = max_retries
        self._fail_open = fail_open
    
    async def validate(self, subject_context: dict[str, Any]) -> ValidationResult:
        """Validate context file before node execution."""
        
        # Load context file
        context_data = load_context_file(context_file)
        
        # Compute context hash for chaining
        context_hash = hashlib.sha256(
            json.dumps(context_data, sort_keys=True).encode()
        ).hexdigest()
        
        # LLM validation for completeness
        validation = await self._validate_completeness(context_data)
        
        return {
            "context_hash": context_hash,
            "context_data": context_data,
            "is_valid": validation["is_valid"],
            "completeness_score": validation["completeness_score"],
            "missing_info": validation.get("missing_info", []),
            "suggested_questions": validation.get("suggested_questions", [])
        }
    
    async def _validate_completeness(self, context: dict) -> dict:
        """Validate subject context completeness using LLM."""
        prompt = """
        Analyze the following project context for completeness.
        
        Context:
        {context}
        
        Check for:
        1. Project name/description
        2. Key requirements
        3. Target audience
        4. Technology preferences (optional)
        
        Return JSON:
        {
            "is_valid": true/false,
            "completeness_score": 0.0-1.0,
            "missing_info": ["list of missing items"],
            "suggested_questions": ["questions to ask if incomplete"]
        }
        """
        
        response = await self.llm.chat([
            {"role": "user", "content": prompt.format(context=context)}
        ])
        
        return json.loads(response.content)
```

---

## 9. Phase 2: DAG Support

### 9.1 DAG Dependencies (Future)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 2: DAG-Based Execution                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Dependency Configuration                                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  dependencies:                                                         │ │
│  │    analyst: []           # No dependencies                            │ │
│  │    pm: [analyst]         # Depends on analyst                         │ │
│  │    ux: [analyst]         # Depends on analyst (parallel with PM)     │ │
│  │    architect: [pm, ux]   # Depends on both PM and UX                 │ │
│  │    po: [architect]       # Depends on architect                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Execution Layers                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Layer 1: [analyst]           # Execute alone                         │ │
│  │  Layer 2: [pm, ux]            # Execute in parallel                   │ │
│  │  Layer 3: [architect]         # Wait for layer 2                      │ │
│  │  Layer 4: [po]                # Execute last                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Visual Representation                                                      │
│                                                                             │
│              ┌─────────┐                                                   │
│              │ Analyst │                                                   │
│              └────┬────┘                                                   │
│           ┌──────┴───────┐                                                 │
│           ▼              ▼                                                 │
│      ┌─────────┐    ┌─────────┐                                           │
│      │   PM    │    │   UX    │    ← Parallel                             │
│      └────┬────┘    └────┬────┘                                           │
│           └──────┬───────┘                                                 │
│                  ▼                                                         │
│            ┌─────────┐                                                     │
│            │Architect│                                                     │
│            └────┬────┘                                                     │
│                 ▼                                                          │
│            ┌─────────┐                                                     │
│            │   PO    │                                                     │
│            └─────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Parallel Execution Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max Concurrent Nodes | 3 | Kimi rate limit |
| Max Concurrent Requests | 20 | Kimi Tier 3 |
| TPM Budget | 5M | Kimi Tier 3 |

---

## 10. Implementation Reference

### 10.1 File Structure

```
docuswarm/node_execution/
├── __init__.py
├── executor.py           # Single Context Protocol executor (唯一活跃实现)
├── chaining.py           # Context chaining (StateManager 同步调用)
├── validator.py          # Context validator
├── state.py              # State type definitions
├── checkpoint.py         # Checkpoint management
└── operations.py         # Node run CRUD operations

# REMOVED (P0-2/P0-3 Retirement):
# - node_execution/graph.py → 空壳图构建，已物理删除
# - node_execution/flow.py → 废弃执行链路，已物理删除

docuswarm/pipeline/       # Refactored structure (TDD-01, TDD-02)
├── __init__.py
├── orchestrator.py       # HybridOrchestrator (facade, ~200 lines)
├── context_validator.py  # ContextValidator (~150 lines) - TDD-02
├── checkpoint_manager.py # CheckpointManager (~150 lines) - TDD-01
├── context_summarizer.py # ContextSummarizer (~150 lines) - TDD-04
├── pipeline_lifecycle.py # PipelineLifecycle (~400 lines)
├── session_recovery.py   # SessionRecovery (~200 lines)
├── graph.py              # StateGraph definition (REMOVED deprecated functions, P0-3: no run_until_complete)
└── state.py              # PipelineState definitions

docuswarm/utils/          # New utilities (TDD-04)
└── context_resolver.py   # ContextResolver for @ path injection

docuswarm/llm/            # SDK integration (TDD-05)
├── __init__.py
├── claude_sdk_wrapper.py # ClaudeSDKWrapper (~300 lines)
├── session_manager.py    # SessionManager compatible layer (~150 lines)
└── response.py           # Message extraction utilities

docuswarm/tools/          # Tool system (TDD-03)
├── __init__.py
├── tool_result_extractor.py  # ToolResultExtractor (~280 lines)
├── create_deliverable.py     # Refactored for standard functions
└── create_document_set.py    # Refactored for standard functions

# REMOVED (TDD-BMM-03):
# docuswarm/templates/      # Removed - DRY violation, contained _bmad references
```

### 10.2 New Components (Post-Refactor)

| Component | File | TDD | Description |
|-----------|------|-----|-------------|
| CheckpointManager | `pipeline/checkpoint_manager.py` | TDD-01 | Centralized checkpointer lifecycle |
| ContextValidator | `pipeline/context_validator.py` | TDD-02 | LLM-based validation with retry |
| ToolResultExtractor | `tools/tool_result_extractor.py` | TDD-03 | Deterministic metadata extraction |
| ContextResolver | `utils/context_resolver.py` | TDD-04 | @ path injection support |
| ContextSummarizer | `pipeline/context_summarizer.py` | TDD-04 | Agent-based document summarization |
| ClaudeSDKWrapper | `llm/claude_sdk_wrapper.py` | TDD-05 | SDK wrapper for claude-agent-sdk |
| NodeTaskConfig | `nodes/loader.py` | TDD-BMM-01 | BMM task configuration |

### 10.3 Removed Components (BMM Refactor)

| Component | Removal Reason | TDD Reference |
|-----------|---------------|---------------|
| `templates/*.yaml` | DRY violation, contained `_bmad` references | TDD-BMM-03 |
| `_create_default_node_executor()` | Created empty deliverable placeholders | TDD-BMM-03 |
| `create_enhanced_node_executor()` | Called deprecated function | TDD-BMM-03 |
| `NodeQuestionConfig` | Automation doesn't use manual questions | TDD-BMM-03 |
| `NodeQuestionsConfig` | Questions generated by Independent Agent | TDD-BMM-03 |
| `NodeDependenciesConfig` | Managed by graph edges | TDD-BMM-03 |
| `description` field | Redundant with task description | TDD-BMM-01 |

### 10.3 Key Classes (Updated)

```python
# node_execution/graph.py
class NodeExecutionGraph:
    def __init__(self, db_path: str)
    def build_graph(self) -> StateGraph
    async def execute(self, initial_state: NodeRunState) -> NodeRunState
    async def resume(self, node: str, run_id: str) -> NodeRunState

# pipeline/checkpoint_manager.py (TDD-01)
class CheckpointManager:
    """Centralized checkpointer lifecycle management."""
    def __init__(self, db_path: str, external_checkpointer: BaseCheckpointSaver | None = None)
    async def get_or_create(self, pipeline_id: str) -> tuple[BaseCheckpointSaver, RunnableConfig]
    async def close(self, pipeline_id: str | None = None) -> None

# pipeline/context_validator.py (TDD-02)
class ContextValidator:
    """LLM-based context validation with structured retry."""
    def __init__(self, session_manager: SessionManager, max_retries: int = 2, fail_open: bool = False)  # P1-2: SessionManager (KimiSessionManager removed)
    async def validate(self, subject_context: dict[str, Any]) -> ValidationResult

# pipeline/context_summarizer.py (TDD-04)
class ContextSummarizer:
    """Agent-based document summarization."""
    def __init__(self, session_manager: SessionManager, max_content_length: int = 50000)
    async def summarize_document(self, document: ReferencedDocument) -> str
    async def summarize_all(self, documents: list[ReferencedDocument]) -> dict[str, str]

# utils/context_resolver.py (TDD-04)
class ContextResolver:
    """@ path injection support for context files."""
    def __init__(self, project_root: Path | None = None)
    def resolve(self, content: str, context_file_path: Path | None = None) -> ResolvedContext

# tools/tool_result_extractor.py (TDD-03)
class ToolResultExtractor:
    """Deterministic extraction of deliverable metadata from tool calls."""
    def __init__(self, max_summary_length: int = 500)
    def extract_from_messages(self, messages: list[Any]) -> list[DeliverableMetadata]
    def extract_single_deliverable(self, messages: list[Any]) -> DeliverableMetadata | None

# llm/claude_sdk_wrapper.py (TDD-05)
class ClaudeSDKWrapper:
    """SDK wrapper for claude-agent-sdk via Kimi Code API."""
    def __init__(self, base_url: str | None = None, api_key: str | None = None)
    async def execute(self, prompt: str, agent_name: str = "docuswarm", timeout: float | None = 1800.0) -> SDKResult

# llm/session_manager.py (TDD-05)
class SessionManager:
    """Unified session manager using ClaudeSDKWrapper.
    
    P1-2 Note: KimiSessionManager alias has been removed.
    """
    def __init__(self, work_dir: Path | None = None, base_url: str | None = None, api_key: str | None = None)
    async def single_prompt(self, prompt: str, mode: str = "agent", yolo: bool = True, agent_name: str = "docuswarm") -> SDKResult
```

---

## 11. Critical Implementation Gap: Node Executor Integration

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

### 11.1 Problem Statement

The node execution architecture described in this document represents the **target design**. The current implementation has a critical integration gap:

**Current State**: `pipeline/graph.py` uses `_create_default_node_executor()` which receives `node_executor_func=None` by default. This causes each LangGraph node to create an empty deliverable placeholder `{}` instead of invoking the DualAgentNode dual-agent loop.

**Desired State**: Each LangGraph node should invoke `node_execution/executor.py` → `create_node_executor()` → `DualAgentNode.execute()`, producing actual LLM-generated deliverables.

### 11.2 Two Systems Comparison

```
System A (Active, Broken):
  graph.py → _create_default_node_executor(node_id)
           → node_executor_func is None
           → deliverables[node_id] = {}  # Empty placeholder
           → status = "completed"        # False success

System B (Complete, Unused):
  node_execution/executor.py → create_node_executor(node_id, session_manager)
                             → DualAgentNode.execute()
                             → IndependentAgent → EvaluatorAgent → iterate
                             → Real deliverable content
```

### 11.3 Fix Strategy: 方案C (SDK Agent File + work_dir)

Recommended approach per research report:

1. **IndependentAgent Session**: Pass `agent_file` (path to `independent_agent.yaml`) and `work_dir` (`output/{pipeline_id}/`) when creating SDK Session
2. **Prompt Modification**: Remove "Respond only with JSON" directive; require "MUST use create_deliverable tool"
3. **CreateDeliverableTool**: Modify to write files relative to `work_dir`
4. **Integration Test**: Verify `proposal.md` → `output/{pipeline_id}/*.md` file generation

### 11.4 File Output Architecture

```
output/
└── {pipeline_id}/           # Per-execution isolation
    ├── analyst-report.md    # Created by CreateDeliverableTool via SDK
    ├── prd.md
    ├── ux-design.md
    ├── architecture.md
    └── epics-stories.md
```

The `output/{pipeline_id}/` path is set as `work_dir` for the SDK Session. CreateDeliverableTool writes files into this directory. This approach:
- Leverages SDK native agent_file + work_dir mechanism
- Eliminates false success (tool call failure produces explicit errors)
- Provides per-execution directory isolation

---

## 12. F5: Pipeline & Node Execution Convergence (2026-03-25)

> **Status**: In Progress | **Priority**: P1 | **TDD Plan**: `../solution/2026-03-25-f5-test-driven-implementation-plan.md`

### 12.1 Problem Statement

The system currently has **two parallel execution backbones**:

| Module | LOC | Responsibility | Issue |
|--------|-----|----------------|-------|
| `pipeline/` | 3,120 | Business orchestration | Contains deprecated fallback paths |
| `node_execution/` | 2,255 | Node execution | Not fully integrated |

**Critical Issues**:
1. **Silent Fallback**: `create_pipeline_graph()` silently falls back to deprecated `_create_default_node_executor()` when `session_manager=None`
2. **Boundary Violations**: Direct `f"node-{...}"` string formatting instead of using `PipelineAdapter`
3. **State Conversion**: Bidirectional state conversion logic concentrated in `pipeline/graph.py` instead of `PipelineAdapter`

### 12.2 Convergence Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    F5 Unified Execution Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pipeline Layer (Orchestration)                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  HybridOrchestrator                                                  │ │
│  │  └── create_pipeline_graph(                                          │ │
│  │        session_manager: KimiSessionManager  # REQUIRED (P0)          │ │
│  │      )                                                               │ │
│  └───────────────────────────┬───────────────────────────────────────────┘ │
│                              │                                              │
│                              │ session_manager (no fallback)               │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  PipelineAdapter (Single Boundary)                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │ │
│  │  │ create_pipeline │  │ convert_pipeline│  │ convert_node_to_    │   │ │
│  │  │ _id()           │  │ _to_node_state()│  │ pipeline_state()    │   │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘   │ │
│  └───────────────────────────┬───────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│  Node Execution Layer (Execution)                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  create_node_executor() → DualAgentNode.execute()                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.3 Implementation Phases

| Phase | Duration | Key Changes | Test File |
|-------|----------|-------------|-----------|
| **Phase 1 (P0)** | Week 1 | • Make `session_manager` required<br>• Remove `_create_default_node_executor()`<br>• Enforce `PipelineAdapter` usage | `test_create_pipeline_graph_signature.py`<br>`test_no_deprecated_executor.py`<br>`test_pipeline_adapter_usage.py` |
| **Phase 2 (P1)** | Week 2 | • Move state conversion to `PipelineAdapter`<br>• Update `graph.py` to use Adapter methods | `test_pipeline_adapter_state_conversion.py` |
| **Phase 3 (P1)** | Week 3 | • Rename `escalation.py` → `node_escalation.py`<br>• Add architecture guard tests | `test_no_filename_conflicts.py` |

### 12.4 Key API Changes

#### Before (Deprecated)
```python
# ❌ Deprecated: Optional session_manager with silent fallback
def create_pipeline_graph(
    ...,
    session_manager: Any | None = None,  # Silent fallback to default executor
) -> Any:
    if session_manager is None:
        # Falls back to _create_default_node_executor() - creates empty deliverables!
        ...
```

#### After (F5 Converged)
```python
# ✅ Required: session_manager is mandatory, no fallback
def create_pipeline_graph(
    ...,
    session_manager: KimiSessionManager,  # REQUIRED - no default
) -> Any:
    if session_manager is None:
        raise ValueError(
            "session_manager is required. "
            "The deprecated default executor has been removed."
        )
    # Always uses integrated executor via PipelineAdapter
```

### 12.5 PipelineAdapter Interface

```python
class PipelineAdapter:
    """Single boundary between pipeline and node_execution modules."""
    
    # Synthetic ID Management
    @staticmethod
    def create_pipeline_id(node_id: str, run_id: str) -> str
    @staticmethod
    def create_run_pipeline_id(run_id: str) -> str
    @staticmethod
    def parse_pipeline_id(pipeline_id: str) -> dict | None
    @staticmethod
    def is_synthetic_pipeline_id(pipeline_id: str) -> bool
    
    # State Conversion (moved from pipeline/graph.py)
    @staticmethod
    def convert_pipeline_to_node_state(
        pipeline_state: PipelineState, 
        node_id: str
    ) -> dict[str, Any]
    
    @staticmethod
    def convert_node_to_pipeline_state(
        node_state: dict[str, Any],
        original_state: PipelineState
    ) -> PipelineState
```

### 12.6 Testing Strategy

All F5 changes follow **Test-Driven Development (TDD)**:

1. **Red**: Write failing test documenting the desired behavior
2. **Green**: Implement minimal code to make test pass
3. **Refactor**: Clean up while keeping tests green

**Test Categories**:
- **Unit Tests**: Individual function behavior
- **Architecture Tests**: Code structure constraints (e.g., no direct f-string formatting)
- **Integration Tests**: End-to-end pipeline execution

**Verification**:
```bash
# Run all F5 tests
pytest tests/pipeline/test_create_pipeline_graph_signature.py \
       tests/pipeline/test_no_deprecated_executor.py \
       tests/architecture/test_pipeline_adapter_usage.py \
       tests/node_execution/test_pipeline_adapter_state_conversion.py \
       tests/architecture/test_no_filename_conflicts.py -v

# Verify migration completion
python tools/migrate_f5_convergence.py --verify
```

### 12.7 Migration Checklist

- [ ] **Phase 1 Complete**: `session_manager` is required, deprecated functions removed
- [ ] **Phase 2 Complete**: State conversion moved to `PipelineAdapter`
- [ ] **Phase 3 Complete**: Filename conflicts resolved, architecture guards in place
- [ ] **All Tests Pass**: 100% test success rate for F5 test suite
- [ ] **CI Updated**: Architecture enforcement checks added to CI pipeline

---

## 13. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| Agent Architecture | `02_AGENT_ARCHITECTURE.md` |
| State Management | `04_STATE_ARCHITECTURE.md` |
| **F5 TDD Implementation Plan** | `../solution/2026-03-25-f5-test-driven-implementation-plan.md` |
| **F5 Research Report** | `../research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md` |
| **F5 Design Spec** | `../research/2026-03-25-f5-unified-design-spec.md` |

### External References

- [LangGraph StateGraph](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)

---

**Document End**
> **2026-03-13 Alignment Notice**: 当前 pipeline 的最大偏差不在“是否有 chaining”，而在“chaining 之后没有被单一上下文协议稳定消费”。关于该问题的推荐修复路径，请参考 `../research/2026-03-13-p0-single-context-protocol-plan.md`。

>
> **2026-03-17 Update**: 产品已决定工作流完全不读取 \docs/\ 目录。因此：
> - P1-2 (受控 docs 上下文策略) 已从重构计划中移除
> - 所有 docs 相关读取/写入能力应进入清理范围
> - \ContextResolver\ 和 \@path\ 注入不再推进
> - 本文档中关于 docs 扩展的描述应被视为待清理而非待实现
> - 推荐的重构路径请参考 \../research/2026-03-13-docuswarm-context-refactor-overview.md

>
> **2026-03-25 F2 Update**: Pipeline 状态管理正在实施单一真相源改造：
> - `state_json` 作为 pipeline 状态的唯一真相源
> - 所有状态读取应通过 `PipelineStateView` 或 `pipeline["state"]`
> - 避免直接访问顶层 `current_node` 字段
> - 实施详情参考 `../solution/2026-03-25-f2-test-driven-implementation-plan.md`
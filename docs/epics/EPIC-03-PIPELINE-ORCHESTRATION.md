# Epic 3: Node Execution Orchestration

**Epic ID**: EPIC-03  
**Version**: 2.0  
**Date**: 2026-02-20  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2 Weeks (Week 5-6)

---

## 1. Epic Overview

### 1.1 Summary

Implement user-driven node execution system using LangGraph StateGraph, including context validation, node configuration loading, checkpoint capability, and the per-node execution workflow where users explicitly choose which nodes to run.

### 1.2 Business Value

- **User Control**: Users execute specific nodes on-demand rather than auto-sequential pipeline
- **Resilience**: Per-node checkpointing prevents lost work
- **Flexibility**: Execute any node independently with context chaining
- **Cost Efficiency**: Run only the nodes you need, reducing LLM costs

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Node execution | Individual nodes execute successfully |
| Context chaining | Predecessor deliverables auto-injected correctly |
| Node runs | Multiple runs tracked per node |
| Per-node output | Output stored in `output/{node}/{run-id}/` |

### 1.4 Dependencies

- **Requires**: Epic 1 (Core Infrastructure), Epic 2 (Agent System) completed
- **Blocks**: Epic 4 (Context Isolation), Epic 5 (Quality Control)

---

## 2. Architecture Context

### 2.1 Node Execution Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Node Execution Orchestration (Epic 3)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Context File (Input)                                                       │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     CONTEXT VALIDATOR                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │   Context File Validation (structure, completeness)      │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   USER NODE SELECTION                                │   │
│  │  `docuswarm start <node> --context <file> [--no-chain]`            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   CONTEXT CHAINING                                   │   │
│  │  Auto-inject predecessor node deliverables based on context_hash    │   │
│  │  (unless --no-chain specified)                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   LANGGRAPH NODE EXECUTION                           │   │
│  │                                                                      │   │
│  │  User chooses one of:                                                │   │
│  │  ┌────────┐   ┌────────┐   ┌────────┐   ┌──────────┐   ┌────────┐ │   │
│  │  │Analyst │   │   PM   │   │   UX   │   │Architect │   │   PO   │ │   │
│  │  │  Node  │   │  Node  │   │  Node  │   │   Node   │   │  Node  │ │   │
│  │  └────────┘   └────────┘   └────────┘   └──────────┘   └────────┘ │   │
│  │      │            │            │            │             │        │   │
│  │      ▼            ▼            ▼            ▼             ▼        │   │
│  │  ┌────────┐   ┌────────┐   ┌────────┐   ┌──────────┐   ┌────────┐ │   │
│  │  │Analyst │   │  PRD   │   │   UX   │   │  Arch    │   │ Epics  │ │   │
│  │  │Report  │   │        │   │ Design │   │  Doc     │   │Stories │ │   │
│  │  └────────┘   └────────┘   └────────┘   └──────────┘   └────────┘ │   │
│  │                                                                      │   │
│  │  [Checkpointer: SqliteSaver for per-node state]                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Output: output/{node}/{run-id}/                                    │   │
│  │    ├── deliverable.md                                                │   │
│  │    ├── evaluation.json                                               │   │
│  │    └── questions.json                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `docuswarm/node_execution/graph.py` | LangGraph StateGraph for single node execution |
| `docuswarm/node_execution/validator.py` | Context validator |
| `docuswarm/node_execution/state.py` | State schema definitions |
| `docuswarm/node_execution/chaining.py` | Context chaining logic |
| `docuswarm/nodes/loader.py` | Node configuration loader |
| `docuswarm/storage/checkpoints.py` | SqliteSaver integration |
| `nodes/*/node.yaml` | Node configurations |

---

## 3. User Stories

### Story 3.1: Node Run State Schema

**ID**: US-3.1  
**As a** developer  
**I want to** have a well-defined node run state schema  
**So that** LangGraph can manage individual node execution correctly

**Acceptance Criteria**:
- [ ] NodeRunState TypedDict defined
- [ ] All fields have appropriate types
- [ ] State serializable to JSON
- [ ] State compatible with SqliteSaver

**Technical Tasks**:
1. Create `node_execution/state.py`
2. Define NodeRunState schema
3. Add validation helpers

**State Schema**:
```python
from typing import TypedDict, Optional, List, Dict, Any

class NodeResult(TypedDict):
    """Result from a single node execution."""
    deliverable: Dict[str, Any]
    questions: List[Dict[str, Any]]
    evaluation: Dict[str, Any]
    iteration: int
    status: str  # "approved", "needs_revision", "blocked"

class NodeRunState(TypedDict):
    """Node run state for LangGraph."""
    run_id: str
    node_id: str
    context_hash: str
    context_file: str
    iteration: int
    deliverable: Optional[Dict[str, Any]]
    questions: List[Dict[str, Any]]
    evaluation: Optional[Dict[str, Any]]
    answers: Dict[str, str]
    chained_context: Dict[str, Dict[str, Any]]  # Predecessor deliverables
    status: str  # "pending", "running", "completed", "failed", "blocked"
```

**Definition of Done**:
- State schema defined with type hints
- JSON serialization verified
- SqliteSaver compatibility tested
- Context chaining fields included

---

### Story 3.2: Node Configuration Loader

**ID**: US-3.2  
**As a** developer  
**I want to** load node configurations from YAML files  
**So that** each node is configured correctly

**Acceptance Criteria**:
- [ ] Load `node.yaml` from `nodes/{node_id}/`
- [ ] Load `persona.json` for Independent Agent
- [ ] Load `evaluator.yaml` for Evaluator Agent
- [ ] Validate required fields
- [ ] Support all 5 nodes

**Technical Tasks**:
1. Create `nodes/loader.py`
2. Define NodeConfig schema
3. Implement YAML loading
4. Create all 5 node configurations
5. Write validation tests

**Node Configuration Schema**:
```yaml
# nodes/analyst/node.yaml
node_id: analyst
name: "Analyst"
description: "Business Analyst performing market research"
sequence: 1

agent:
  persona_file: persona.json
  mode: agent
  temperature: 0.7
  max_tokens: 32768

deliverable:
  type: analyst-report
  format: markdown
  required_sections:
    - executive_summary
    - market_analysis
    - requirements
    - recommendations

questions:
  min_required: 3
  blocking_required: 1

dependencies:
  predecessors: []  # Analyst has no predecessors
```

**All Nodes**:
| Node ID | Sequence | Deliverable Type |
|---------|----------|------------------|
| `analyst` | 1 | Analyst Report |
| `pm` | 2 | PRD |
| `ux` | 3 | UX Design |
| `architect` | 4 | Architecture Doc |
| `po` | 5 | Epics & Stories |

**Definition of Done**:
- All 5 node configurations created
- Configurations load without error
- Validation catches missing fields

---

### Story 3.3: LangGraph Node Execution Definition

**ID**: US-3.3  
**As a** developer  
**I want to** define LangGraph node execution  
**So that** individual nodes execute on-demand

**Acceptance Criteria**:
- [ ] StateGraph supports single-node execution
- [ ] Node execution isolated per run_id
- [ ] SqliteSaver checkpointer attached
- [ ] Thread configuration for per-node isolation

**Technical Tasks**:
1. Create `node_execution/graph.py`
2. Define node execution function
3. Integrate SqliteSaver for node runs
4. Write integration tests

**Implementation**:
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from docuswarm.node_execution.state import NodeRunState
from docuswarm.nodes.dual_agent import create_node_executor

def create_node_execution_graph(node_id: str, db_path: str = "docuswarm.db") -> StateGraph:
    """Create a single-node execution graph."""
    
    # Create checkpointer
    checkpointer = SqliteSaver.from_conn_string(db_path)
    
    # Create graph
    graph = StateGraph(NodeRunState)
    
    # Add single node
    graph.add_node(node_id, create_node_executor(node_id))
    
    # Simple flow: START → node → END
    graph.add_edge(START, node_id)
    graph.add_edge(node_id, END)
    
    # Compile with checkpointer
    return graph.compile(checkpointer=checkpointer)
```

**Definition of Done**:
- Graph created for single-node execution
- Node execution verified
- Checkpointing works per node run

---

### Story 3.4: Node Executor Function

**ID**: US-3.4  
**As a** developer  
**I want to** have a node executor function  
**So that** LangGraph can execute each node

**Acceptance Criteria**:
- [ ] Factory function creates node executors
- [ ] Executor loads node configuration
- [ ] Executor creates DualAgentNode
- [ ] Executor updates node run state
- [ ] Handle iteration within node

**Technical Tasks**:
1. Update `nodes/dual_agent.py` with factory
2. Implement state update logic
3. Implement iteration handling (basic)
4. Write tests

**Implementation**:
```python
from docuswarm.node_execution.state import NodeRunState

def create_node_executor(node_id: str):
    """Create a node executor function for LangGraph."""
    
    async def node_executor(state: NodeRunState) -> NodeRunState:
        """Execute node and update state."""
        logger = structlog.get_logger().bind(node_id=node_id, run_id=state["run_id"])
        logger.info("Node execution started")
        
        # Load configuration
        config = NodeLoader.load(node_id)
        
        # Create dual-agent node
        node = DualAgentNode(node_id, llm_client)
        
        # Get iteration count
        iteration = state["iteration"] + 1
        
        # Execute
        result = await node.execute(state, iteration)
        
        # Update state
        new_state = state.copy()
        new_state["deliverable"] = result.deliverable
        new_state["questions"] = result.questions
        new_state["evaluation"] = result.evaluation
        new_state["iteration"] = iteration
        
        if result.evaluation["verdict"] == "APPROVED":
            new_state["status"] = "completed"
        
        logger.info("Node execution completed", verdict=result.evaluation["verdict"])
        return new_state
    
    return node_executor
```

**Definition of Done**:
- Factory creates valid executors
- State updated correctly after execution
- Iteration count tracked

---

### Story 3.5: Context Validator Implementation

**ID**: US-3.5  
**As a** developer  
**I want to** implement context validation  
**So that** node execution starts with valid input

**Acceptance Criteria**:
- [ ] Validate context file structure
- [ ] Validate context completeness
- [ ] Generate context_hash for chaining
- [ ] Support for node execution start

**Technical Tasks**:
1. Create `node_execution/validator.py`
2. Implement context validation
3. Implement context_hash generation
4. Write validation tests

**Implementation**:
```python
import hashlib
import json

class ContextValidator:
    """Validates context files for node execution."""
    
    async def validate_context(self, context_file: str) -> dict:
        """Validate context file and return parsed content."""
        # Read and parse context file
        with open(context_file, 'r', encoding='utf-8') as f:
            context = json.load(f)
        
        # Validate structure
        required_fields = ["project_description", "requirements"]
        missing = [f for f in required_fields if f not in context]
        
        if missing:
            raise ValueError(f"Context missing required fields: {missing}")
        
        return context
    
    def generate_context_hash(self, context_file: str) -> str:
        """Generate hash of context file for chaining."""
        with open(context_file, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()[:16]
```

**Definition of Done**:
- Context validation works
- Context hash generation reliable
- Node execution starts successfully

---

### Story 3.6: Context Chaining Implementation

**ID**: US-3.6  
**As a** developer  
**I want to** implement context chaining logic  
**So that** nodes automatically receive predecessor deliverables

**Acceptance Criteria**:
- [ ] Query predecessor nodes by context_hash
- [ ] Inject deliverables into node context
- [ ] Support --no-chain flag to skip chaining
- [ ] Handle missing predecessor runs gracefully

**Technical Tasks**:
1. Create `node_execution/chaining.py`
2. Implement predecessor query logic
3. Implement deliverable injection
4. Write chaining tests

**Implementation**:
```python
class ContextChainer:
    """Manages context chaining between nodes."""
    
    SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    async def get_chained_deliverables(
        self, 
        node_id: str, 
        context_hash: str,
        no_chain: bool = False
    ) -> dict:
        """Get predecessor deliverables for context chaining."""
        if no_chain:
            return {}
        
        current_idx = self.SEQUENCE.index(node_id)
        previous_nodes = self.SEQUENCE[:current_idx]
        
        chained = {}
        for prev_node in previous_nodes:
            latest_run = await self.state_manager.get_latest_successful_run(
                node_id=prev_node,
                context_hash=context_hash
            )
            if latest_run and latest_run.deliverable:
                chained[f"{prev_node}_deliverable"] = latest_run.deliverable
        
        return chained
```

**Definition of Done**:
- Checkpoints saved automatically per node run
- Checkpoints retrievable by run_id
- Context chaining works correctly
- No data loss on interruption

---

### Story 3.7: Node Execution Flow

**ID**: US-3.7  
**As a** developer  
**I want to** implement the full node execution flow  
**So that** individual nodes execute with proper context

**Acceptance Criteria**:
- [ ] Node execution starts from context file
- [ ] Context chaining injects predecessor deliverables
- [ ] State persists to database
- [ ] Output saved to `output/{node}/{run-id}/`

**Technical Tasks**:
1. Implement context loading and validation
2. Implement context chaining integration
3. Implement state persistence
4. Write end-to-end test

**Context Flow**:
```
Context File (--context project.yaml)
         │
         ▼
┌─────────────────────────────────────┐
│ Context Validation                  │
│ - Parse context file                │
│ - Generate context_hash             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Context Chaining (unless --no-chain)│
│ - Query predecessor nodes           │
│ - Inject deliverables into context  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Node Execution                      │
│ Input: context + chained_context    │
│ Output: deliverable, questions      │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ State Persistence                   │
│ - Save to node_runs table           │
│ - Export to output/{node}/{run-id}/ │
└─────────────────────────────────────┘
```

**Definition of Done**:
- Node execution completes successfully
- Context chaining works correctly
- State persists to database
- Output files created in correct location

---

### Story 3.8: Node Configuration Files

**ID**: US-3.8  
**As a** developer  
**I want to** create all node configuration files  
**So that** each node is properly configured

**Acceptance Criteria**:
- [ ] All 5 `node.yaml` files created
- [ ] All 5 `persona.json` files created
- [ ] All 5 `evaluator.yaml` files created
- [ ] Configurations valid and complete

**Technical Tasks**:
1. Create `nodes/analyst/` directory and files
2. Create `nodes/pm/` directory and files
3. Create `nodes/ux/` directory and files
4. Create `nodes/architect/` directory and files
5. Create `nodes/po/` directory and files

**Node Configurations**:

**Analyst Node** (`nodes/analyst/node.yaml`):
```yaml
node_id: analyst
name: "Analyst"
description: "Business Analyst performing market research and requirements analysis"
sequence: 1

agent:
  persona_file: persona.json
  mode: agent
  temperature: 0.7
  max_tokens: 32768

deliverable:
  type: analyst-report
  format: markdown
  filename: analyst-report.md
  required_sections:
    - executive_summary
    - market_analysis
    - competitive_landscape
    - requirements
    - recommendations

questions:
  min_required: 3
  blocking_required: 1
  categories: [blocking, clarifying, optional]
```

**PM Node** (`nodes/pm/node.yaml`):
```yaml
node_id: pm
name: "Product Manager"
description: "Product Manager creating PRD from analyst findings"
sequence: 2

agent:
  persona_file: persona.json
  mode: agent
  temperature: 0.7
  max_tokens: 32768

deliverable:
  type: prd
  format: markdown
  filename: prd.md
  required_sections:
    - product_overview
    - functional_requirements
    - non_functional_requirements
    - user_stories
    - success_metrics

dependencies:
  predecessors: [analyst]
```

**Definition of Done**:
- All configuration files created
- Files load without error
- Dependencies correctly specified

---

### Story 3.9: Per-Node Run Tracking

**ID**: US-3.9  
**As a** developer  
**I want to** track multiple runs per node  
**So that** users can execute nodes multiple times and view history

**Acceptance Criteria**:
- [ ] Each node execution creates unique run_id
- [ ] Multiple runs tracked independently
- [ ] Run history queryable by node_id
- [ ] Latest run easily retrievable

**Technical Tasks**:
1. Create `node_execution/run_tracker.py`
2. Implement run_id generation
3. Implement run history queries
4. Write tracking tests

**Implementation**:
```python
import uuid

class NodeRunTracker:
    """Tracks node execution runs."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def generate_run_id(self) -> str:
        """Generate 8-character run ID."""
        return str(uuid.uuid4())[:8]
    
    async def list_runs(
        self, 
        node_id: str, 
        limit: int = 10
    ) -> List[dict]:
        """List run history for a node."""
        return await self.state_manager.list_node_runs(
            node_id=node_id,
            limit=limit
        )
    
    async def get_latest_run(
        self, 
        node_id: str,
        context_hash: str = None
    ) -> Optional[dict]:
        """Get latest run for a node, optionally filtered by context_hash."""
        runs = await self.state_manager.list_node_runs(
            node_id=node_id,
            context_hash=context_hash,
            limit=1
        )
        return runs[0] if runs else None
```

**Definition of Done**:
- run_id generation works reliably
- Multiple runs tracked independently
- Run history queries work correctly

---

## 4. Technical Specifications

### 4.1 Node Execution Order (User-Driven)

| Sequence | Node | Predecessor Dependencies | Output |
|----------|------|-------------------------|--------|
| 1 | Analyst | None | Analyst Report |
| 2 | PM | Analyst | PRD |
| 3 | UX | Analyst, PM | UX Design |
| 4 | Architect | Analyst, PM, UX | Architecture Doc |
| 5 | PO | Analyst, PM, UX, Architect | Epics & Stories |

**Note**: Users execute nodes manually in any order. Context chaining auto-injects predecessor deliverables based on `context_hash`.

### 4.2 Thread Configuration

```python
# Thread isolation for per-node runs
config = {
    "configurable": {
        "thread_id": run_id  # Unique per node run
    }
}
```

### 4.3 Performance Targets

| Metric | Target |
|--------|--------|
| Node execution | < 2 minutes |
| Context chaining | < 1 second |
| Checkpoint save | < 1 second |
| Run history query | < 500ms |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test | Description |
|------|-------------|
| `test_state_schema` | Verify node run state serialization |
| `test_node_loader` | Verify configuration loading |
| `test_context_chaining` | Verify predecessor injection |
| `test_graph_definition` | Verify single-node graph structure |

### 5.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_single_node_execution` | One node executes correctly |
| `test_context_chaining_integration` | Node receives predecessor deliverables |
| `test_checkpoint_per_run` | Checkpoint per run_id works |
| `test_multiple_runs_same_node` | Multiple runs tracked independently |

### 5.3 End-to-End Tests

| Test | Description |
|------|-------------|
| `test_node_execution_start_to_finish` | Complete node execution with chaining |
| `test_no_chain_flag` | Execute without predecessor injection |
| `test_node_with_iterations` | Node iterates on NEEDS_REVISION |

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LangGraph upgrade breaks API | Low | High | Pin version, test before upgrade |
| Context hash collision | Low | Medium | Use SHA256, sufficient length |
| Missing predecessor runs | Medium | Low | Warn user, allow execution anyway |
| State size exceeds limits | Low | Low | Compress large deliverables |

---

## 7. Definition of Done (Epic Level)

- [ ] All 9 stories completed and tested
- [ ] All 5 node configurations created
- [ ] Individual nodes execute on user command
- [ ] Context chaining works correctly
- [ ] Context validator validates input files
- [ ] Multiple runs tracked per node
- [ ] Integration tests pass
- [ ] End-to-end test passes
- [ ] Documentation complete

---

## 8. References

| Document | Location |
|----------|----------|
| Node Execution Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` |
| System Architecture | `docs/architecture/01_SYSTEM_ARCHITECTURE.md` |
| State Management | `docs/architecture/04_STATE_ARCHITECTURE.md` |
| Correct Course | `docs/plan/CORRECT_COURSE.md` |

---

**Epic End**

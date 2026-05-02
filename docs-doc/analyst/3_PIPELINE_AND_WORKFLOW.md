# DocuSwarm Pipeline & Workflow Analysis

**Version**: 2.0 (Occam's Razor Simplified)  
**Date**: 2026-02-19  
**Category**: Pipeline & Workflow  
**Topics Covered**: 3.1 - 3.8  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 8 topics related to pipeline orchestration and workflow management in DocuSwarm. The focus is on sequential execution, state persistence with SQLite, and iteration handling.

**Key Simplifications from Occam's Razor Analysis**:
- Sequential execution only for MVP (DAG-based parallel execution deferred to Phase 2)
- LangGraph StateGraph for pipeline orchestration (replaces custom NodeExecutor)
- SQLite with WAL mode for state persistence (replaces YAML + file locks)
- Dual-agent iteration loop (Independent + Evaluator)
- Transaction-level persistence via LangGraph checkpointer

**Key Findings**:
- Fixed sequential ordering (Analyst → PM → UX → Architect → PO) is sufficient for MVP
- LangGraph's built-in checkpointing eliminates custom checkpoint/resume logic
- Max 3 iterations per node with simplified escalation prevents infinite loops
- Cross-node validation deferred to Phase 2 for MVP simplicity

**Critical Dependencies**: Architecture decisions (Section 1) with LangGraph framework.

**Development Time Savings**: ~4-6 weeks compared to DAG-based parallel design.

---

## Topic 3.1: Pipeline Node Sequence (Sequential Only)

### Context

BMAD defines clear phase ordering:
- **Phase 1**: Analysis (Analyst)
- **Phase 2**: Planning (PM, UX)
- **Phase 3**: Solutioning (Architect, PO)

**Occam's Razor Decision**: MVP uses fixed sequential execution only. DAG-based parallel execution deferred to Phase 2.

### Research Findings

**Workflow Sequencing Patterns**:

| Pattern | Flexibility | Complexity | MVP Fit |
|---------|-------------|------------|---------|
| **Fixed Sequence** | None | Lowest | Excellent |
| **DAG-Based** | High | Medium | Deferred |
| **Dynamic Routing** | Maximum | High | Overkill |

**Sequential vs Parallel Trade-offs**:

| Aspect | Sequential | Parallel |
|--------|------------|----------|
| Implementation | Simple | Complex |
| Debugging | Easy | Harder |
| Execution Time | Longer | Shorter |
| MVP Time-to-Market | Fast | Slow |

### Implementation Guidance

**Sequential Pipeline Configuration**:

```yaml
# pipeline-config.yaml (MVP)
pipeline:
  execution_mode: sequential  # Only mode for MVP
  
  sequence:
    - analyst      # Phase 1: Analysis
    - pm           # Phase 2: Planning
    - ux           # Phase 2: Planning
    - architect    # Phase 3: Solutioning
    - po           # Phase 3: Solutioning
  
  # DAG dependencies documented for Phase 2
  # Not used in MVP sequential execution
  future_dag_dependencies:
    pm: [analyst]
    ux: [analyst]
    architect: [pm, ux]
    po: [architect]
```

**LangGraph Sequential Pipeline**:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Optional, List
import sqlite3

class PipelineState(TypedDict):
    pipeline_id: str
    subject_context: dict
    current_node: Optional[str]
    completed_nodes: List[str]
    deliverables: dict
    questions: dict
    evaluation_history: dict

class SequentialPipeline:
    """MVP Sequential Pipeline using LangGraph."""
    
    SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    
    def __init__(self, db_path: str = "docuswarm.db"):
        # SQLite with WAL mode for persistence
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.checkpointer = SqliteSaver(self.conn)
        
        # Build pipeline graph
        self.graph = StateGraph(PipelineState)
        self._build_graph()
        self.compiled = self.graph.compile(checkpointer=self.checkpointer)
    
    def _build_graph(self):
        """Build sequential pipeline graph."""
        # Add nodes
        for node_id in self.SEQUENCE:
            self.graph.add_node(node_id, self._create_node_executor(node_id))
        
        # Set entry point
        self.graph.set_entry_point(self.SEQUENCE[0])
        
        # Add sequential edges
        for i, node_id in enumerate(self.SEQUENCE[:-1]):
            self.graph.add_edge(node_id, self.SEQUENCE[i + 1])
        
        # Final node to END
        self.graph.add_edge(self.SEQUENCE[-1], END)
    
    def _create_node_executor(self, node_id: str):
        """Create executor function for a node."""
        async def execute_node(state: PipelineState) -> PipelineState:
            from .nodes import DualAgentNode
            
            # Load node configuration
            node = DualAgentNode(node_id, self._load_node_config(node_id))
            
            # Execute dual-agent pattern
            result = await node.execute(state["subject_context"])
            
            # Update state
            return {
                **state,
                "current_node": node_id,
                "completed_nodes": state["completed_nodes"] + [node_id],
                "deliverables": {
                    **state["deliverables"],
                    node_id: result["deliverable"]
                },
                "questions": {
                    **state["questions"],
                    node_id: result["questions"]
                },
                "evaluation_history": {
                    **state["evaluation_history"],
                    node_id: result["evaluation"]
                }
            }
        
        return execute_node
    
    def _load_node_config(self, node_id: str) -> dict:
        """Load configuration for a specific node."""
        # Implementation: load from nodes/{node_id}/node.yaml
        pass
    
    async def run(self, initial_context: dict) -> PipelineState:
        """Run the sequential pipeline."""
        import uuid
        
        initial_state: PipelineState = {
            "pipeline_id": str(uuid.uuid4()),
            "subject_context": initial_context,
            "current_node": None,
            "completed_nodes": [],
            "deliverables": {},
            "questions": {},
            "evaluation_history": {}
        }
        
        config = {"configurable": {"thread_id": initial_state["pipeline_id"]}}
        final_state = await self.compiled.ainvoke(initial_state, config)
        
        return final_state
    
    async def resume(self, pipeline_id: str) -> PipelineState:
        """Resume a pipeline from checkpoint."""
        config = {"configurable": {"thread_id": pipeline_id}}
        
        # LangGraph automatically resumes from last checkpoint
        final_state = await self.compiled.ainvoke(None, config)
        
        return final_state
```

### Recommendation

**Fixed Sequential Execution** for MVP.

Benefits:
- Predictable, easy to debug
- No race conditions or coordination complexity
- LangGraph handles state persistence automatically
- Clear path to Phase 2 DAG enhancement

---

## Topic 3.2: Dependency Graph Algorithm (Deferred)

### Context

**Occam's Razor Decision**: DAG-based dependency resolution is deferred to Phase 2. MVP uses fixed sequential order.

### Research Summary (For Phase 2 Reference)

**Algorithm Recommendation for Phase 2**: Kahn's Algorithm with layered output.

```python
# Phase 2: DAG Dependency Resolver
class DependencyResolver:
    """Deferred to Phase 2 - DAG-based parallel execution."""
    
    def resolve(self, nodes: list, dependencies: list) -> list:
        """
        Kahn's algorithm for topological sorting.
        Returns execution layers for parallel execution.
        """
        # Implementation deferred to Phase 2
        pass
```

### MVP Implementation

For MVP, dependency resolution is trivial (sequential):

```python
class SequentialDependencyResolver:
    """MVP: Simple sequential order."""
    
    SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    
    def get_next_node(self, completed_nodes: list) -> Optional[str]:
        """Get the next node to execute."""
        for node_id in self.SEQUENCE:
            if node_id not in completed_nodes:
                return node_id
        return None  # All nodes completed
    
    def is_complete(self, completed_nodes: list) -> bool:
        """Check if pipeline is complete."""
        return set(completed_nodes) >= set(self.SEQUENCE)
```

### Recommendation

**Sequential order for MVP**, Kahn's Algorithm for Phase 2 DAG support.

---

## Topic 3.3: Parallel Execution Strategy (Deferred)

### Context

**Occam's Razor Decision**: Parallel execution is deferred to Phase 2. MVP executes nodes sequentially.

### Research Summary (For Phase 2 Reference)

**Recommended Phase 2 Configuration**:
- Max concurrent: 3 nodes
- RPM limit: 200 (Kimi Tier 3)
- TPM limit: 5M (Kimi Tier 3)

### MVP Implementation

No parallel execution in MVP - sequential only:

```python
class MVPPipelineExecutor:
    """MVP: Sequential node execution."""
    
    async def execute_pipeline(self, initial_context: dict) -> dict:
        """Execute all nodes sequentially."""
        pipeline = SequentialPipeline()
        return await pipeline.run(initial_context)
```

### Recommendation

**Sequential execution only** for MVP. Parallel execution adds complexity with limited MVP benefit.

---

## Topic 3.4: Workflow Step-File Architecture

### Context

BMAD uses micro-file architecture where each workflow step is an isolated file. DocuSwarm adopts a simplified version for MVP.

### Research Findings

**Micro-File Benefits**:

| Benefit | Description | MVP Relevance |
|---------|-------------|---------------|
| **Isolation** | Each step self-contained | High |
| **Maintainability** | Edit one step without affecting others | High |
| **Memory Efficiency** | Just-in-time loading | Medium |

### Implementation Guidance

**Simplified Directory Structure (MVP)**:

```
nodes/
├── analyst/
│   ├── node.yaml                    # Node metadata + config
│   ├── persona.md                   # BMAD agent persona
│   └── evaluator.yaml               # Evaluation criteria
│
├── pm/
│   ├── node.yaml
│   ├── persona.md
│   └── evaluator.yaml
│
├── ux/
│   ├── node.yaml
│   ├── persona.md
│   └── evaluator.yaml
│
├── architect/
│   ├── node.yaml
│   ├── persona.md
│   └── evaluator.yaml
│
└── po/
    ├── node.yaml
    ├── persona.md
    └── evaluator.yaml
```

**Node Configuration Schema**:

```yaml
# nodes/analyst/node.yaml
node_id: analyst
display_name: "Business Analyst"
persona_path: "./persona.md"
evaluator_config: "./evaluator.yaml"

# Dual-agent configuration (MVP)
agents:
  independent:
    model: "kimi-k2.5-thinking"
    temperature: 0.7
    max_tokens: 8000
  evaluator:
    model: "kimi-k2.5-instant"
    temperature: 0.3
    max_tokens: 2000

# Iteration settings
iteration:
  max_iterations: 3
  approval_threshold: 0.70
  escalation_threshold: 0.50

# Output configuration
output:
  deliverable_type: "analyst_report"
  template_path: "../templates/analyst-report-template.md"
```

**Node Loader**:

```python
import yaml
from pathlib import Path

class NodeLoader:
    """Load node configuration from file system."""
    
    def __init__(self, nodes_path: str = "nodes"):
        self.base_path = Path(nodes_path)
    
    def load_node_config(self, node_id: str) -> dict:
        """Load complete node configuration."""
        node_path = self.base_path / node_id
        
        # Load main config
        config_path = node_path / "node.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Load persona
        persona_path = node_path / config.get("persona_path", "persona.md")
        with open(persona_path, 'r', encoding='utf-8') as f:
            config["persona_content"] = f.read()
        
        # Load evaluator criteria
        evaluator_path = node_path / config.get("evaluator_config", "evaluator.yaml")
        with open(evaluator_path, 'r', encoding='utf-8') as f:
            config["evaluator_criteria"] = yaml.safe_load(f)
        
        return config
    
    def list_nodes(self) -> list:
        """List all available nodes."""
        return [
            d.name for d in self.base_path.iterdir() 
            if d.is_dir() and (d / "node.yaml").exists()
        ]
```

### Recommendation

**Simplified step-file pattern** - one config file per node instead of multiple step files.

Benefits:
- BMAD alignment maintained
- Lower complexity for MVP
- Easy to extend with steps in Phase 2

---

## Topic 3.5: Pipeline State Persistence (SQLite)

### Context

**Occam's Razor Decision**: SQLite with WAL mode replaces YAML + file locks for state persistence.

### Research Findings

**Persistence Strategy Comparison**:

| Strategy | Consistency | Recovery | Complexity |
|----------|-------------|----------|------------|
| **YAML + File Lock** | Medium | Manual | Medium |
| **SQLite + WAL** | Strong | Automatic | Low |
| **Git-Based** | Very Strong | Full history | High |

**SQLite Benefits**:
- ACID transactions built-in
- WAL mode allows concurrent reads during write
- LangGraph checkpointer integration
- No custom locking code needed

### Implementation Guidance

**SQLite State Manager**:

```python
import sqlite3
import json
from datetime import datetime
from typing import Optional

class StateManager:
    """SQLite-based state management for DocuSwarm."""
    
    def __init__(self, db_path: str = "docuswarm.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize database schema."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS pipelines (
                pipeline_id TEXT PRIMARY KEY,
                subject_context TEXT NOT NULL,
                current_node TEXT,
                status TEXT DEFAULT 'running',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS node_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                iteration INTEGER DEFAULT 1,
                deliverable TEXT,
                questions TEXT,
                evaluation TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id),
                UNIQUE(pipeline_id, node_id, iteration)
            );
            
            CREATE INDEX IF NOT EXISTS idx_node_results_pipeline 
            ON node_results(pipeline_id, node_id);
        """)
        self.conn.commit()
    
    def create_pipeline(self, pipeline_id: str, subject_context: dict) -> str:
        """Create a new pipeline."""
        self.conn.execute(
            """INSERT INTO pipelines (pipeline_id, subject_context, status) 
               VALUES (?, ?, 'running')""",
            (pipeline_id, json.dumps(subject_context, ensure_ascii=False))
        )
        self.conn.commit()
        return pipeline_id
    
    def update_pipeline_status(self, pipeline_id: str, status: str, current_node: str = None):
        """Update pipeline status."""
        self.conn.execute(
            """UPDATE pipelines 
               SET status = ?, current_node = ?, updated_at = CURRENT_TIMESTAMP
               WHERE pipeline_id = ?""",
            (status, current_node, pipeline_id)
        )
        self.conn.commit()
    
    def save_node_result(
        self, 
        pipeline_id: str, 
        node_id: str, 
        iteration: int,
        deliverable: dict,
        questions: list,
        evaluation: dict,
        status: str
    ):
        """Save node execution result."""
        self.conn.execute(
            """INSERT OR REPLACE INTO node_results 
               (pipeline_id, node_id, iteration, deliverable, questions, evaluation, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                pipeline_id, 
                node_id, 
                iteration,
                json.dumps(deliverable, ensure_ascii=False),
                json.dumps(questions, ensure_ascii=False),
                json.dumps(evaluation, ensure_ascii=False),
                status
            )
        )
        self.conn.commit()
    
    def get_pipeline_state(self, pipeline_id: str) -> Optional[dict]:
        """Get complete pipeline state."""
        cursor = self.conn.execute(
            "SELECT * FROM pipelines WHERE pipeline_id = ?",
            (pipeline_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        pipeline = {
            "pipeline_id": row[0],
            "subject_context": json.loads(row[1]),
            "current_node": row[2],
            "status": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "nodes": {}
        }
        
        # Load node results
        cursor = self.conn.execute(
            """SELECT node_id, MAX(iteration), deliverable, questions, evaluation, status
               FROM node_results 
               WHERE pipeline_id = ?
               GROUP BY node_id""",
            (pipeline_id,)
        )
        
        for row in cursor:
            pipeline["nodes"][row[0]] = {
                "iteration": row[1],
                "deliverable": json.loads(row[2]) if row[2] else None,
                "questions": json.loads(row[3]) if row[3] else None,
                "evaluation": json.loads(row[4]) if row[4] else None,
                "status": row[5]
            }
        
        return pipeline
    
    def get_completed_nodes(self, pipeline_id: str) -> list:
        """Get list of completed node IDs."""
        cursor = self.conn.execute(
            """SELECT DISTINCT node_id FROM node_results 
               WHERE pipeline_id = ? AND status = 'completed'""",
            (pipeline_id,)
        )
        return [row[0] for row in cursor]
```

### Recommendation

**SQLite with WAL mode** for state persistence.

Benefits:
- ACID transactions ensure data integrity
- WAL mode allows concurrent access
- LangGraph checkpointer integration
- No custom file locking code
- Easy backup (single file)

---

## Topic 3.6: Checkpoint and Resume (LangGraph Native)

### Context

**Occam's Razor Decision**: Use LangGraph's built-in checkpointing instead of custom checkpoint/resume logic.

### Research Findings

**LangGraph Checkpointing Benefits**:
- Automatic state persistence at node boundaries
- Built-in resume from any checkpoint
- SQLite backend for durability
- Thread-based isolation for concurrent pipelines

### Implementation Guidance

**LangGraph Checkpoint Integration**:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

class CheckpointedPipeline:
    """Pipeline with automatic checkpointing via LangGraph."""
    
    def __init__(self, db_path: str = "docuswarm.db"):
        # SQLite checkpointer with WAL mode
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        self.checkpointer = SqliteSaver(conn)
        
        # Build and compile graph with checkpointer
        self.graph = self._build_graph()
        self.compiled = self.graph.compile(checkpointer=self.checkpointer)
    
    async def run(self, initial_state: dict, thread_id: str) -> dict:
        """Run pipeline with automatic checkpointing."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # LangGraph automatically checkpoints after each node
        result = await self.compiled.ainvoke(initial_state, config)
        
        return result
    
    async def resume(self, thread_id: str) -> dict:
        """Resume from last checkpoint."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Pass None to resume from checkpoint
        result = await self.compiled.ainvoke(None, config)
        
        return result
    
    def get_checkpoint_history(self, thread_id: str) -> list:
        """Get checkpoint history for debugging."""
        config = {"configurable": {"thread_id": thread_id}}
        
        checkpoints = []
        for checkpoint in self.checkpointer.list(config):
            checkpoints.append({
                "id": checkpoint.id,
                "timestamp": checkpoint.ts,
                "parent_id": checkpoint.parent_config.get("configurable", {}).get("checkpoint_id")
            })
        
        return checkpoints
```

**Resume with State Inspection**:

```python
class PipelineResumeManager:
    """Manage pipeline resume operations."""
    
    def __init__(self, pipeline: CheckpointedPipeline, state_manager: StateManager):
        self.pipeline = pipeline
        self.state_manager = state_manager
    
    async def resume_pipeline(self, pipeline_id: str) -> dict:
        """Resume a pipeline with status reporting."""
        # Check pipeline exists
        state = self.state_manager.get_pipeline_state(pipeline_id)
        if not state:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        if state["status"] == "completed":
            return {"status": "already_completed", "state": state}
        
        # Get completed nodes for reporting
        completed = self.state_manager.get_completed_nodes(pipeline_id)
        print(f"Resuming pipeline {pipeline_id}")
        print(f"Completed nodes: {completed}")
        print(f"Current node: {state['current_node']}")
        
        # Resume execution
        result = await self.pipeline.resume(pipeline_id)
        
        return {"status": "completed", "result": result}
```

### Recommendation

**LangGraph native checkpointing** - no custom checkpoint logic needed.

Benefits:
- Zero custom code for checkpoint/resume
- Automatic persistence after each node
- Thread isolation for concurrent pipelines
- Built-in checkpoint history

---

## Topic 3.7: Node Iteration Handling (Dual-Agent)

### Context

When Evaluator marks deliverable as NEEDS_REVISION, the node iterates:
1. Independent Agent revises with feedback
2. Evaluator re-reviews
3. Repeat until APPROVED or max iterations

**Occam's Razor Update**: Simplified for dual-agent pattern (no Questioner in loop).

### Research Findings

**Iteration Control Patterns**:

| Pattern | Loop Prevention | Complexity |
|---------|----------------|------------|
| **Fixed Max** | Strong | Low |
| **Dynamic Threshold** | Moderate | Medium |
| **Human Escalation** | Strongest | High |

### Implementation Guidance

**Dual-Agent Iteration Manager**:

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Verdict(Enum):
    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    BLOCKED = "BLOCKED"

@dataclass
class IterationResult:
    success: bool
    deliverable: dict
    questions: list
    evaluation: dict
    iterations: int
    warning: Optional[str] = None

class DualAgentIterationManager:
    """Manage iteration loop for dual-agent pattern."""
    
    def __init__(
        self, 
        max_iterations: int = 3,
        approval_threshold: float = 0.70,
        escalation_threshold: float = 0.50
    ):
        self.max_iterations = max_iterations
        self.approval_threshold = approval_threshold
        self.escalation_threshold = escalation_threshold
    
    async def execute_with_iteration(
        self, 
        independent_agent,
        evaluator_agent,
        initial_context: dict
    ) -> IterationResult:
        """Execute dual-agent pattern with iteration."""
        
        context = initial_context.copy()
        last_evaluation = None
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"Iteration {iteration}/{self.max_iterations}")
            
            # Build iteration context with feedback
            if last_evaluation and iteration > 1:
                context["iteration_feedback"] = self._build_feedback(
                    last_evaluation, iteration
                )
            
            # Execute Independent Agent (creates deliverable + questions)
            independent_result = await independent_agent.execute(context)
            deliverable = independent_result["deliverable"]
            questions = independent_result["questions"]
            
            # Execute Evaluator Agent (context isolated)
            evaluation = await evaluator_agent.evaluate({
                "subject_context": context.get("subject_context", context),
                "deliverable": deliverable
                # Note: NO access to independent_result["private_reasoning"]
            })
            last_evaluation = evaluation
            
            # Check verdict
            verdict = Verdict(evaluation["verdict"])
            
            if verdict == Verdict.APPROVED:
                return IterationResult(
                    success=True,
                    deliverable=deliverable,
                    questions=questions,
                    evaluation=evaluation,
                    iterations=iteration
                )
            
            if verdict == Verdict.BLOCKED:
                return IterationResult(
                    success=False,
                    deliverable=deliverable,
                    questions=questions,
                    evaluation=evaluation,
                    iterations=iteration
                )
            
            # NEEDS_REVISION: check if we should continue
            if iteration == self.max_iterations:
                score = evaluation["alignment_score"]
                
                if score >= self.escalation_threshold:
                    # Acceptable quality, proceed with warning
                    return IterationResult(
                        success=True,
                        deliverable=deliverable,
                        questions=questions,
                        evaluation=evaluation,
                        iterations=iteration,
                        warning=f"max_iterations_reached (score: {score:.2f})"
                    )
                else:
                    # Quality too low
                    return IterationResult(
                        success=False,
                        deliverable=deliverable,
                        questions=questions,
                        evaluation=evaluation,
                        iterations=iteration,
                        warning="quality_below_threshold"
                    )
        
        # Should not reach here
        raise RuntimeError("Iteration loop exited unexpectedly")
    
    def _build_feedback(self, evaluation: dict, iteration: int) -> dict:
        """Build feedback context for next iteration."""
        return {
            "iteration_number": iteration,
            "previous_score": evaluation["alignment_score"],
            "issues_to_address": evaluation.get("issues_found", []),
            "suggestions": evaluation.get("suggestions", []),
            "instruction": self._format_feedback_instruction(evaluation)
        }
    
    def _format_feedback_instruction(self, evaluation: dict) -> str:
        """Format feedback as instruction for Independent Agent."""
        issues = evaluation.get("issues_found", [])
        suggestions = evaluation.get("suggestions", [])
        
        instruction = "Please revise the deliverable addressing the following:\n\n"
        
        if issues:
            instruction += "Issues Found:\n"
            for issue in issues:
                instruction += f"- {issue.get('description', issue)}\n"
            instruction += "\n"
        
        if suggestions:
            instruction += "Suggestions:\n"
            for suggestion in suggestions:
                instruction += f"- {suggestion}\n"
        
        return instruction
```

**LangGraph Node with Iteration**:

```python
from langgraph.graph import StateGraph, END

class IteratingNode:
    """LangGraph node with built-in iteration support."""
    
    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.iteration_manager = DualAgentIterationManager(
            max_iterations=config.get("max_iterations", 3),
            approval_threshold=config.get("approval_threshold", 0.70),
            escalation_threshold=config.get("escalation_threshold", 0.50)
        )
        
        # Build internal iteration graph
        self.graph = StateGraph(dict)
        self.graph.add_node("independent", self._run_independent)
        self.graph.add_node("evaluator", self._run_evaluator)
        self.graph.add_node("decide", self._decide)
        
        self.graph.set_entry_point("independent")
        self.graph.add_edge("independent", "evaluator")
        self.graph.add_edge("evaluator", "decide")
        self.graph.add_conditional_edges(
            "decide",
            self._should_iterate,
            {"iterate": "independent", "complete": END}
        )
        
        self.compiled = self.graph.compile()
    
    def _should_iterate(self, state: dict) -> str:
        """Decide whether to iterate or complete."""
        verdict = state.get("verdict")
        iteration = state.get("iteration", 1)
        
        if verdict == "APPROVED":
            return "complete"
        elif verdict == "BLOCKED":
            return "complete"
        elif iteration >= self.iteration_manager.max_iterations:
            return "complete"
        else:
            return "iterate"
```

### Recommendation

**Max 3 Iterations with Dual-Agent Pattern**.

Configuration:
- Max iterations: 3
- Approval threshold: 0.70 (70%)
- Escalation threshold: 0.50 (50%)
- Proceed with warning if score >= 0.50 at max iterations

Benefits:
- Prevents infinite loops
- Quality improvement through feedback
- Clear thresholds for decision-making
- Simplified for dual-agent (no Questioner in loop)

---

## Topic 3.8: Cross-Node Validation (Simplified)

### Context

**Occam's Razor Decision**: Complex cross-node validation is simplified for MVP. Basic validation at pipeline end only.

### Research Summary

**BMAD Validation Patterns**:
- `validate-prd`: After PM
- `check-implementation-readiness`: After Architect
- `review-adversarial-general`: Optional anywhere

**MVP Simplification**: Single end-of-pipeline validation instead of milestone validations.

### Implementation Guidance

**Simplified End-of-Pipeline Validation**:

```python
class SimplifiedValidator:
    """MVP: Basic validation at pipeline completion."""
    
    def __init__(self, session_manager):
        self.session_mgr = session_manager  # KimiSessionManager
    
    async def validate_pipeline(self, deliverables: dict) -> dict:
        """Validate alignment across all deliverables."""
        prompt = f"""
Review the following DocuSwarm pipeline deliverables for consistency and completeness.

## Analyst Report
{deliverables.get('analyst', 'Not available')}

## PRD
{deliverables.get('pm', 'Not available')}

## UX Design
{deliverables.get('ux', 'Not available')}

## Architecture
{deliverables.get('architect', 'Not available')}

## Epics/Stories
{deliverables.get('po', 'Not available')}

---

Check for:
1. Requirements traceability (all requirements have implementing components)
2. Design consistency (UX aligns with architecture)
3. Completeness (no major gaps)

Return JSON:
{{
  "valid": true/false,
  "alignment_score": 0.0-1.0,
  "issues": ["list of issues found"],
  "summary": "brief summary"
}}
"""
        
        response = await self.llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        return json.loads(response.content)
    
    async def validate_if_needed(
        self, 
        pipeline_state: dict, 
        validate_threshold: float = 0.80
    ) -> dict:
        """Conditionally validate based on evaluation scores."""
        # Check if all nodes had good scores
        all_scores = [
            node.get("evaluation", {}).get("alignment_score", 0)
            for node in pipeline_state.get("nodes", {}).values()
        ]
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        if avg_score >= validate_threshold:
            return {"skipped": True, "reason": "high_quality_scores"}
        
        # Run validation
        deliverables = {
            node_id: node.get("deliverable", {}).get("content", "")
            for node_id, node in pipeline_state.get("nodes", {}).items()
        }
        
        return await self.validate_pipeline(deliverables)
```

### Recommendation

**End-of-pipeline validation only** for MVP.

Benefits:
- Single validation point reduces complexity
- Sufficient for catching major alignment issues
- Clear path to Phase 2 milestone validations

Phase 2 Enhancement Path:
- Add milestone validations after PM, Architect, PO
- Implement BMAD-style `check-implementation-readiness`
- Add configurable validation thresholds

---

## Cross-Topic Dependencies (Updated)

```
3.1 Pipeline Sequence
 └─→ 1.7 Sequential Execution (MVP only)
 └─→ 1.3 LangGraph Framework

3.2 DAG Algorithm
 └─→ Deferred to Phase 2

3.3 Parallel Strategy
 └─→ Deferred to Phase 2

3.4 Step-File Architecture
 └─→ 1.3 Node Encapsulation
 └─→ 2.1 Persona Extraction

3.5 State Persistence
 └─→ 1.6 SQLite WAL Mode
 └─→ 5.1 State Storage

3.6 Checkpoint and Resume
 └─→ 1.3 LangGraph Checkpointer
 └─→ 3.5 SQLite Persistence

3.7 Iteration Handling
 └─→ 2.2 Evaluator Criteria
 └─→ 1.1 Dual-Agent Pattern

3.8 Cross-Node Validation
 └─→ Simplified for MVP
 └─→ 7.1 Alignment Scoring
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 3.1 Sequence | DAG + Sequential | Sequential only | ~2 weeks |
| 3.2 DAG Algorithm | Kahn's implementation | Deferred | ~1 week |
| 3.3 Parallel | Semaphore + rate limiter | Deferred | ~2 weeks |
| 3.5 Persistence | YAML + file locks | SQLite + WAL | ~1 week |
| 3.6 Checkpoint | Custom checkpoint logic | LangGraph native | ~1 week |
| 3.7 Iteration | Triple-agent loop | Dual-agent loop | Simpler |
| 3.8 Validation | Milestone validations | End-of-pipeline | ~1 week |

**Total Estimated Savings**: ~4-6 weeks development time

---

## Post-Implementation Gap Analysis (2026-02-23)

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

### Critical Finding: Pipeline Executor Integration

The pipeline implementation (Topic 3.1) contains a critical gap between the sequential pipeline graph and the actual node execution logic:

**Designed flow** (Topic 3.1 code sample, `_create_node_executor`):
```
SequentialPipeline._create_node_executor(node_id)
  → DualAgentNode(node_id, config)
  → node.execute(subject_context)
  → Real deliverable + questions + evaluation
```

**Actual implementation** (`pipeline/graph.py`):
```
_create_default_node_executor(node_id, node_executor_func=None)
  → node_executor_func is None
  → deliverables[node_id] = {}  # Empty placeholder
  → completed_nodes += [node_id]  # False success
```

### Analysis of the Gap

The code sample in Topic 3.1 (above, line 138-168) correctly shows `_create_node_executor` importing and calling `DualAgentNode`. However, the actual `pipeline/graph.py` implementation diverged:

1. `_create_default_node_executor()` accepts an optional `node_executor_func` parameter (default `None`)
2. No code path passes an actual function for this parameter
3. When `None`, the executor creates empty deliverable `{}` instead of calling DualAgentNode
4. All 5 nodes show `completed` status with zero content

### Node-Centric Model Alignment

Per `docs/plan/CORRECT_COURSE.md` v2.2, the system is transitioning from pipeline-centric to **node-centric execution**:

| Aspect | This Analysis (v2.0) | CORRECT_COURSE (v2.2) | Gap |
|--------|---------------------|----------------------|-----|
| **Data Model** | `PipelineState` with `pipeline_id` | `NodeRunState` with `run_id` per node | Terminology mismatch |
| **Execution** | Auto-sequential 5 nodes | User-driven per-node | Execution model shift |
| **Storage** | `pipelines` + `node_results` tables | `node_runs` table | Schema migration needed |
| **Output** | `output/{pipeline_id}/` | `output/<node>/<run-id>/` | Path structure change |

The analysis in Topics 3.1-3.8 remains valid for understanding the LangGraph integration approach, but the **execution model** should be read in conjunction with CORRECT_COURSE v2.2 for the current direction.

### Recommended Fix: 方案C

Per the research report, the recommended approach is **方案C (SDK Agent File + work_dir)**:
- Pass `agent_file` to IndependentAgent Session to activate CallableTool2
- Set `work_dir` for file output  
- Modify prompt: remove JSON-only requirement, require tool usage
- This aligns with the original design intent shown in Topic 3.1 code samples

---

## References

### Research Sources
- LangGraph Documentation (langchain-ai.github.io, 2026)
- SQLite WAL Mode Documentation (sqlite.org)
- BMAD Workflow Architecture Analysis (internal)

### Related Analysis Documents
- [1_ARCHITECTURE_AND_DESIGN.md](1_ARCHITECTURE_AND_DESIGN.md) - Foundation decisions (v2.0)
- [5_STATE_MANAGEMENT.md](5_STATE_MANAGEMENT.md) - SQLite state management
- [7_QUALITY_AND_TESTING.md](7_QUALITY_AND_TESTING.md) - Quality gate criteria

---

**Document Status**: Version 2.1 - Updated with post-implementation gap analysis  
**Key Change**: Sequential execution only, LangGraph native checkpointing; critical executor integration gap identified  
**Development Time Savings**: ~4-6 weeks compared to DAG-based parallel design

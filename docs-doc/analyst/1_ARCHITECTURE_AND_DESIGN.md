# DocuSwarm Architecture & Design Analysis

**Version**: 2.0 (Occam's Razor Simplified)  
**Date**: 2026-02-19  
**Category**: Architecture & Design  
**Topics Covered**: 1.1 - 1.9  
**Status**: Analysis Complete - Simplified per Occam's Razor

---

## Executive Summary

This analysis covers 9 critical architectural decisions for DocuSwarm's multi-agent orchestration system. Following **Occam's Razor principles**, the architecture has been significantly simplified for MVP.

**Key Simplifications (Occam's Razor Applied)**:
- **Dual-Agent Pattern** (not Triple): Independent Agent + Evaluator Agent only; question generation is embedded in Independent Agent
- **LangGraph Framework**: Use battle-tested framework instead of custom NodeExecutor (saves 8-12 weeks)
- **SQLite with WAL + Optimistic Locking**: Replace YAML + file locks for robust state management
- **Sequential Execution Only**: MVP uses sequential mode; DAG-based parallelism deferred
- **Hybrid Orchestration**: LLM-driven decisions + rule engine for execution gating

**Development Time Savings**: ~12-18 weeks compared to original design  
**Complexity Reduction**: ~33% fewer components

**Critical Dependencies**: Technology Stack decisions (Section 4) must be finalized before architecture implementation.

---

## Topic 1.1: Dual-Agent Pattern Implementation

### Context

DocuSwarm's core architecture uses a **Dual-Agent Pattern** (simplified from original Triple-Agent):
1. **Independent Agent**: Creates deliverables with full context access + generates clarifying questions
2. **Evaluator Agent**: Reviews deliverables without access to private reasoning

The Questioner Agent has been eliminated; question generation is now embedded within the Independent Agent.

### Occam's Razor Rationale

| Aspect | Triple-Agent (Original) | Dual-Agent (Simplified) |
|--------|------------------------|------------------------|
| **Components** | 3 agents per node | 2 agents per node |
| **Development Time** | Baseline | -4 to 6 weeks |
| **Complexity** | 100% | ~67% |
| **Question Quality** | Dedicated agent | Embedded in Independent |

**Upgrade Condition**: Add third Questioner Agent only if:
- Question quality is poor, OR
- Question generation interferes with deliverable creation

### Research Findings

**Framework Comparison** (2025-2026 landscape):

| Framework | Dual-Agent Support | Context Isolation | Production Readiness |
|-----------|-------------------|-------------------|---------------------|
| **LangGraph** | Native support | Built-in state management | High |
| **CrewAI** | Role-based | Shared context | Medium-High |
| **AutoGen** | Conversational | Not applicable | Medium |

**LangGraph** is the recommended framework for DocuSwarm because:
- Native graph-based workflow management
- Built-in state persistence and recovery
- Battle-tested in production environments
- Saves 8-12 weeks of infrastructure development

### Options Analysis

| Option | Development Effort | Alignment | Maintainability |
|--------|-------------------|-----------|-----------------|
| **LangGraph + Dual-Agent** | Low (2-4 weeks) | 95% | High (framework support) |
| **Custom NodeExecutor** | High (8-12 weeks) | 100% | Medium (custom maintenance) |
| **CrewAI Adaptation** | Medium (4-6 weeks) | 70% | Low (fighting framework) |

### Implementation Guidance

**Recommended Architecture**:

```
DocuSwarmNode (LangGraph StateGraph)
├── IndependentAgent
│   ├── persona (BMAD agent)
│   ├── tools (document creation)
│   ├── questionGeneration (embedded)
│   └── privateContext (reasoning, drafts)
├── EvaluatorAgent
│   ├── reviewCriteria
│   └── restrictedContext (subject + deliverable only)
└── LangGraph StateManager
    ├── checkpointer (SQLite)
    └── stateSchema
```

**LangGraph Implementation**:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class DocuSwarmNode:
    def __init__(self, node_config):
        self.graph = StateGraph(NodeState)
        self.checkpointer = SqliteSaver.from_conn_string("docuswarm.db")
        
        # Define dual-agent workflow
        self.graph.add_node("independent", self.run_independent)
        self.graph.add_node("evaluator", self.run_evaluator)
        
        # Define edges
        self.graph.add_edge("independent", "evaluator")
        self.graph.add_conditional_edges(
            "evaluator",
            self.should_iterate,
            {"iterate": "independent", "complete": END}
        )
        
        self.graph.set_entry_point("independent")
        self.compiled = self.graph.compile(checkpointer=self.checkpointer)
    
    async def run_independent(self, state: NodeState) -> NodeState:
        """Independent Agent: Create deliverable + generate questions"""
        # Create deliverable
        deliverable = await self.create_deliverable(state)
        
        # Generate questions (embedded, not separate agent)
        questions = await self.generate_questions(state, deliverable)
        
        return {
            **state,
            "deliverable": deliverable,
            "questions": questions,
            "private_reasoning": self.capture_reasoning()
        }
    
    async def run_evaluator(self, state: NodeState) -> NodeState:
        """Evaluator Agent: Review with restricted context"""
        # Build restricted context (no private reasoning)
        restricted_context = self.build_restricted_context(state)
        
        review = await self.evaluate(restricted_context, state["deliverable"])
        
        return {
            **state,
            "review": review,
            "iteration": state.get("iteration", 0) + 1
        }
```

### Recommendation

**Adopt LangGraph with Dual-Agent Pattern**

Benefits:
- 33% complexity reduction (2 agents vs 3)
- 8-12 weeks saved on workflow infrastructure
- Battle-tested state management and recovery
- Question generation still available (embedded in Independent)

**Migration Path**: If question quality becomes problematic, extract to dedicated Questioner Agent.

---

## Topic 1.2: Context Isolation Enforcement

### Context

The Evaluator Agent MUST NOT access:
- Independent Agent's private reasoning
- Draft versions of deliverables
- Tool call history and intermediate results

Only the Subject Context (project requirements, constraints) and final deliverable are shared.

### Occam's Razor Approach

**Three-Layer Hybrid Isolation** (not simplified to single layer):
1. **Runtime Access Control**: Code-level enforcement
2. **Separate Prompt Templates**: Different system prompts per agent
3. **Message-Level Filtering**: Strip private data before passing to Evaluator

### Implementation Guidance

**Hybrid Isolation Pattern**:

```python
class ContextIsolationManager:
    """Three-layer context isolation for dual-agent pattern"""
    
    # Layer 1: Separate prompt templates
    INDEPENDENT_SYSTEM = """You are an Independent Agent creating deliverables.
    You have full access to context and can reason privately.
    Also generate 3-5 clarifying questions at the end."""
    
    EVALUATOR_SYSTEM = """You are an Evaluator Agent reviewing deliverables.
    You only see the subject context and final deliverable.
    You do NOT have access to the author's reasoning process."""
    
    def build_independent_context(self, subject, history):
        """Full context for Independent Agent"""
        return {
            "system": self.INDEPENDENT_SYSTEM,
            "subject": subject,
            "private_history": history  # Full access
        }
    
    def build_evaluator_context(self, subject, deliverable):
        """Restricted context for Evaluator - Layer 2 & 3"""
        # Layer 2: Filter private data
        sanitized_deliverable = self.sanitize(deliverable)
        
        # Layer 3: Runtime validation
        self.assert_no_private_data(sanitized_deliverable)
        
        return {
            "system": self.EVALUATOR_SYSTEM,
            "subject": subject,
            "deliverable": sanitized_deliverable
            # NO private_history - isolation enforced
        }
    
    def sanitize(self, content):
        """Remove any private markers from content"""
        patterns = [
            r'<private>.*?</private>',
            r'<reasoning>.*?</reasoning>',
            r'<draft>.*?</draft>'
        ]
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content
    
    def assert_no_private_data(self, content):
        """Runtime check for private data leakage"""
        leak_patterns = [r'reasoning:', r'draft:', r'tool_call:', r'intermediate:']
        for pattern in leak_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ContextLeakageError(f"Private data detected: {pattern}")
```

### Recommendation

**Three-Layer Hybrid Isolation** (maintained, not simplified)

Context isolation is security-critical and should NOT be simplified. The three-layer approach provides:
- Defense in depth
- Multiple validation points
- Clear audit trail

---

## Topic 1.3: Node Encapsulation Strategy

### Context

Each DocuSwarm node (Analyst, PM, UX, Architect, PO) represents a workflow stage. 

### Occam's Razor Approach

**Use LangGraph's StateGraph** instead of custom NodeExecutor:
- Pre-built state management
- Built-in checkpointing
- Conditional edge routing
- Saves 8-12 weeks development

### Implementation Guidance

**LangGraph-Based Node Structure**:

```
nodes/
├── analyst/
│   ├── config.yaml          # Node metadata
│   ├── persona.md           # BMAD persona
│   └── evaluator_criteria.yaml
├── pm/
│   └── ...
└── shared/
    └── langgraph_executor.py  # Shared LangGraph workflow
```

**Node Configuration**:

```yaml
# nodes/analyst/config.yaml
node:
  id: analyst
  name: "Business Analyst"
  persona_path: bmm/agents/analyst.md
  
  dependencies: []
  
  outputs:
    primary: analyst-report.md
  
  evaluator:
    criteria:
      evidence_quality: 0.4
      completeness: 0.3
      actionability: 0.3
    
  questions:
    embedded: true  # Generated by Independent Agent
    min_count: 3
    categories: [blocking, clarifying, optional]
```

### Recommendation

**LangGraph StateGraph + YAML Configuration**

Benefits:
- Framework handles workflow complexity
- YAML remains editable by non-technical users
- Focus development effort on business logic
- 8-12 weeks saved on infrastructure

---

## Topic 1.4: Orchestrator Agent Design

### Context

The Orchestrator Agent handles intent recognition, node routing, and pipeline coordination.

### Occam's Razor Approach

**Hybrid Orchestration**: LLM-driven decisions + Rule engine execution gating

NOT a simple state machine - retains intelligence for complex routing decisions.

### Implementation Guidance

**Hybrid Orchestrator Architecture**:

```python
class OrchestratorAgent:
    """Hybrid: LLM decisions + Rule engine execution"""
    
    def __init__(self, config):
        self.session_mgr = KimiSessionManager()  # kimi-agent-sdk
        self.rule_engine = RuleEngine(config.rules)
    
    async def route(self, user_request, pipeline_state):
        # Phase 1: LLM-driven intent recognition
        intent = await self.llm_classify_intent(user_request)
        
        # Phase 2: Rule engine validates and executes
        if self.rule_engine.can_execute(intent, pipeline_state):
            return self.rule_engine.get_next_node(intent)
        else:
            # Rule engine blocks - return reason
            return self.rule_engine.get_blocking_reason(intent, pipeline_state)
    
    async def llm_classify_intent(self, request):
        """LLM determines intent (flexible)"""
        response = await self.session_mgr.single_prompt(
            model='kimi-k2.5',
            temperature=0.3,
            messages=[
                {"role": "system", "content": ORCHESTRATOR_PROMPT},
                {"role": "user", "content": request}
            ]
        )
        return self.parse_intent(response)
    
    class RuleEngine:
        """Rule engine for execution gating (predictable)"""
        
        def can_execute(self, intent, state):
            """Check if execution is allowed"""
            node = self.intent_to_node[intent]
            
            # Check dependencies
            for dep in self.dependencies[node]:
                if state.nodes[dep].status != 'completed':
                    return False
            return True
        
        def get_next_node(self, intent):
            return self.intent_to_node[intent]
```

**Rule Engine Configuration**:

```yaml
# orchestrator-rules.yaml
rules:
  intent_mapping:
    create_prd: pm
    analyze_market: analyst
    design_architecture: architect
    create_ux: ux
    
  dependencies:
    analyst: []
    pm: [analyst]
    ux: [analyst]
    architect: [pm, ux]
    po: [architect]
    
  gating:
    require_approval: false  # MVP: no human approval gates
    max_iterations: 3
```

### Recommendation

**Hybrid Orchestration: LLM + Rule Engine**

Benefits:
- LLM provides flexible intent understanding
- Rule engine ensures predictable execution
- Not a simple state machine - retains intelligence
- Clear separation of concerns

---

## Topic 1.5: Response Compiler Architecture

### Context

Every DocuSwarm response includes output from the Dual-Agent pattern.

### Occam's Razor Approach

**Simplified Response Structure** (2 components instead of 3):
1. **Deliverable + Questions**: From Independent Agent
2. **Review**: From Evaluator Agent

### Implementation Guidance

**Updated Response Schema**:

```typescript
// types/response.d.ts
interface DualAgentResponse {
  // From Independent Agent
  deliverable: {
    content: string;
    format: 'markdown';
    metadata: DeliverableMetadata;
  };
  
  questions: {
    blocking: Question[];
    clarifying: Question[];
    optional: Question[];
  };
  
  // From Evaluator Agent
  review: {
    verdict: 'APPROVED' | 'NEEDS_REVISION' | 'BLOCKED';
    alignment_score: number;  // 0.0-1.0
    issues_found: Issue[];
    suggestions: Suggestion[];
  };
  
  // Pipeline status
  node_status: {
    current_node: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    iteration: number;
  };
}
```

### Recommendation

**Dual-Agent Response Compiler**

Benefits:
- Simpler schema (2 agent outputs vs 3)
- Questions still included (from Independent Agent)
- Maintains all necessary information

---

## Topic 1.6: State Agent Design

### Context

State management for pipeline execution and recovery.

### Occam's Razor Approach

**SQLite with WAL mode + Optimistic Locking** (replaces YAML + file locks)

Benefits:
- ACID transactions
- Better concurrency handling
- Built-in query capabilities
- LangGraph native support

### Implementation Guidance

**SQLite State Manager**:

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

class StateManager:
    """SQLite-based state management with WAL mode"""
    
    def __init__(self, db_path="docuswarm.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._init_schema()
        
        # LangGraph checkpointer
        self.checkpointer = SqliteSaver(self.conn)
    
    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS pipeline_state (
                pipeline_id TEXT PRIMARY KEY,
                current_node TEXT,
                execution_mode TEXT DEFAULT 'sequential',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS node_state (
                pipeline_id TEXT,
                node_id TEXT,
                status TEXT DEFAULT 'pending',
                iteration INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                version INTEGER DEFAULT 1,
                PRIMARY KEY (pipeline_id, node_id)
            );
            
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_id TEXT,
                node_id TEXT,
                iteration INTEGER,
                verdict TEXT,
                alignment_score REAL,
                issues TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
    def update_node(self, pipeline_id, node_id, updates):
        """Optimistic locking update"""
        current = self.get_node(pipeline_id, node_id)
        expected_version = current['version']
        
        result = self.conn.execute("""
            UPDATE node_state 
            SET status = ?, iteration = ?, version = version + 1
            WHERE pipeline_id = ? AND node_id = ? AND version = ?
        """, (updates['status'], updates['iteration'], 
              pipeline_id, node_id, expected_version))
        
        if result.rowcount == 0:
            raise OptimisticLockError("Concurrent modification detected")
        
        self.conn.commit()
```

### Recommendation

**SQLite WAL + Optimistic Locking**

Benefits:
- ACID guarantees
- No file lock complexity
- LangGraph native integration
- Better concurrent access handling

---

## Topic 1.7: DAG vs Sequential Execution

### Context

Pipeline execution ordering strategy.

### Occam's Razor Approach

**Sequential Only for MVP** - DAG-based parallelism deferred

Rationale:
- Sequential is simpler to debug
- MVP nodes typically < 2 minutes each
- Total pipeline time acceptable (~10 minutes)
- Parallelism adds significant complexity

### Implementation Guidance

**Sequential Executor**:

```python
class SequentialPipelineExecutor:
    """Simple sequential execution for MVP"""
    
    SEQUENCE = ['analyst', 'pm', 'ux', 'architect', 'po']
    
    async def run(self, intent, state_manager):
        state = state_manager.create_pipeline(intent)
        
        for node_id in self.SEQUENCE:
            # Execute node
            result = await self.execute_node(node_id, state)
            
            # Update state
            state_manager.update_node(
                state.pipeline_id, 
                node_id, 
                {'status': 'completed', 'iteration': result.iteration}
            )
            
            # Check if blocked
            if result.review.verdict == 'BLOCKED':
                return self.handle_blocked(state, node_id, result)
        
        return state
```

**Upgrade Path**:

```yaml
# Future: Configurable execution mode
pipeline:
  execution_mode: sequential  # MVP
  # execution_mode: dag  # Future Phase 2
  
  # DAG dependencies (for future use)
  dependencies:
    analyst: []
    pm: [analyst]
    ux: [analyst]      # Can parallel with PM
    architect: [pm, ux]
    po: [architect]
```

### Recommendation

**Sequential Execution for MVP**

Upgrade Condition: Implement DAG when:
- Pipeline execution time > 20 minutes, OR
- User feedback demands parallelism

---

## Topic 1.8: Module vs Plugin Architecture

### Context

Deployment architecture choices.

### Occam's Razor Approach

**Standalone Python Application** with LangGraph - simplest deployment

No VCPToolBox plugin or BMAD module integration for MVP.

### Implementation Guidance

**Simplified Deployment Structure**:

```
docuswarm/
├── src/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── nodes/
│   │   ├── base.py
│   │   ├── analyst.py
│   │   ├── pm.py
│   │   └── ...
│   ├── agents/
│   │   ├── independent.py
│   │   └── evaluator.py
│   └── state/
│       └── sqlite_manager.py
├── config/
│   ├── nodes/
│   └── personas/
├── pyproject.toml
└── README.md
```

### Recommendation

**Standalone Python + LangGraph**

Benefits:
- Simplest deployment path
- No plugin infrastructure needed
- Focus on core functionality
- VCP/BMAD integration can be added later

---

## Topic 1.9: Autonomous vs Interactive Mode

### Context

Execution mode for pipeline operations.

### Occam's Razor Approach

**Autonomous Only for MVP** - Interactive debugging deferred

The Evaluator Agent replaces manual confirmation. Debug mode adds complexity not needed for initial release.

### Implementation Guidance

**Autonomous Executor**:

```python
class AutonomousNodeExecutor:
    """Fully autonomous execution - no user interaction"""
    
    async def execute(self, node, context):
        # Independent Agent (creates deliverable + questions)
        independent_result = await node.independent.execute(context)
        
        # Evaluator Agent (reviews)
        review = await node.evaluator.review(
            context,
            independent_result.deliverable
        )
        
        # Automatic iteration handling
        if review.verdict == 'NEEDS_REVISION':
            if context.iteration < MAX_ITERATIONS:
                return await self.execute(node, context.with_feedback(review))
            else:
                return self.escalate(node, context, review)
        
        return DualAgentResponse(
            deliverable=independent_result.deliverable,
            questions=independent_result.questions,
            review=review
        )
```

### Recommendation

**Autonomous Execution Only**

Upgrade Condition: Add interactive debug mode when:
- Development workflow requires step-through debugging
- Quality issues require manual inspection

---

## Cross-Topic Dependencies (Updated)

```
1.1 Dual-Agent Pattern (SIMPLIFIED)
 └─→ 1.2 Context Isolation (maintained - security critical)
 └─→ 2.1 Persona Extraction

1.2 Context Isolation (THREE-LAYER - not simplified)
 └─→ 2.5 Agent Memory
 └─→ 7.5 Security Audit

1.3 Node Encapsulation (LANGGRAPH)
 └─→ 4.3 BMAD Reuse (deferred)

1.4 Orchestrator Design (HYBRID: LLM + Rules)
 └─→ 4.1 LLM Provider Selection

1.5 Response Compiler (DUAL-AGENT OUTPUT)
 └─→ 7.2 Quality Gates

1.6 State Agent (SQLITE WAL + OPTIMISTIC LOCK)
 └─→ 5.1 State Storage Format
 └─→ 5.2 Concurrency Control

1.7 Sequential Execution (MVP - DAG deferred)
 └─→ 3.2 DAG Algorithm (future)

1.8 Standalone App (VCP/BMAD deferred)

1.9 Autonomous Mode (Debug mode deferred)
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original | Simplified | Savings |
|-------|----------|------------|---------|
| 1.1 Agent Pattern | Triple-Agent | Dual-Agent | 4-6 weeks |
| 1.3 Node Executor | Custom build | LangGraph | 8-12 weeks |
| 1.6 State Storage | YAML + file locks | SQLite WAL | Reliability |
| 1.7 Execution | DAG optional | Sequential only | Complexity |
| 1.8 Deployment | VCP Plugin | Standalone | Faster MVP |
| 1.9 Mode | Interactive option | Autonomous only | Complexity |

**Total Development Savings**: ~12-18 weeks  
**Maintained Complexity**: Context Isolation (security-critical)

---

## Post-Implementation Gap Analysis (2026-02-23)

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

### Discovery: Dual Execution System

Deep code analysis revealed that the architecture simplification (Topic 1.3: LangGraph over custom NodeExecutor) was not fully realized in the implementation. Two parallel execution systems coexist without integration:

| System | Design Intent | Actual Status |
|--------|--------------|---------------|
| `pipeline/graph.py` | LangGraph pipeline orchestration | Active but creates empty deliverable placeholders |
| `node_execution/executor.py` | Node-level DualAgentNode execution | Complete but never invoked |

### Impact on Architecture Decisions

| ADR | Decision | Implementation Status |
|-----|----------|----------------------|
| LangGraph Framework (Topic 1.1) | Use LangGraph for orchestration | Partial: graph structure works, but node executors are stubs |
| Dual-Agent Pattern (Topic 1.1) | Independent + Evaluator per node | Implemented but unreachable from pipeline |
| Node Encapsulation (Topic 1.3) | Each node self-contained | Implemented in `node_execution/`, but `graph.py` bypasses it |

### Recommended Action

**方案C: SDK Agent File + work_dir** - Leverage kimi-agent-sdk native capabilities:
1. Pass `agent_file` to IndependentAgent Session to activate CallableTool2 tools
2. Set `work_dir` to `output/{pipeline_id}/` for file output
3. Modify prompt to require tool-based deliverable creation
4. Integrate `node_execution/executor.py` into `pipeline/graph.py` node functions

This fix aligns the implementation with the intended architecture design of using LangGraph + DualAgentNode + CallableTool2 as a unified execution path.

---

## References

### Research Sources
- LangGraph Documentation (langchain.com, 2026)
- SQLite WAL Mode Performance Analysis
- Kimi K2.5 Technical Documentation (kimi.com, 2026)

### Related Analysis Documents
- [2_AGENT_SYSTEM_DESIGN.md](2_AGENT_SYSTEM_DESIGN.md) - Dual-Agent implementation
- [3_PIPELINE_AND_WORKFLOW.md](3_PIPELINE_AND_WORKFLOW.md) - Sequential workflow
- [4_TECHNOLOGY_STACK.md](4_TECHNOLOGY_STACK.md) - LangGraph integration

---

**Document Status**: Updated with post-implementation gap analysis  
**Version**: 2.1  
**Next Review**: After 方案C implementation

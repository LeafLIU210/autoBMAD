# DocuSwarm Technology Stack Analysis

**Version**: 3.0 (kimi-agent-sdk)  
**Date**: 2026-02-20  
**Category**: Technology Stack  
**Topics Covered**: 4.1 - 4.7  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 7 technology decisions for DocuSwarm's implementation. The focus is on LLM provider selection, framework integration, and simplified infrastructure choices.

**Key Simplifications from Occam's Razor Analysis**:
- LangGraph framework for pipeline orchestration (Python-native)
- RAG system deferred to Phase 2 (not needed for MVP)
- Standalone Python application (VCPToolBox plugin deferred)
- SQLite with WAL mode for all persistence needs
- kimi-agent-sdk 的 CallableTool2 替代手动 OpenAI Functions JSON Schema
- Dual-agent model configuration (no Questioner)

**Key Findings**:
- Kimi K2.5 is the recommended primary LLM (9.25/10 DocuSwarm fit score)
- LangGraph provides battle-tested multi-agent orchestration (~8-12 weeks saved)
- Python + LangGraph simplifies implementation vs TypeScript + custom NodeExecutor
- MVP can launch without RAG - direct context passing is sufficient

**Critical Dependencies**: These decisions impact all other architectural choices.

**Development Time Savings**: ~8-12 weeks compared to original VCPToolBox plugin architecture.

---

## Topic 4.1: LLM Provider Selection

### Context

DocuSwarm requires an LLM provider with:
- Large context window (agent personas + documents)
- Agent/tool calling capabilities
- Cost-effective for multi-agent workflows
- Reliable API availability

### Research Findings

**Kimi K2.5 Specifications** (2026):

| Feature | Specification |
|---------|--------------|
| **Architecture** | 1T total params, 32B active (MoE) |
| **Context Window** | 256K tokens |
| **Training Data** | 15T tokens (unified visual-textual) |
| **Modes** | Instant, Thinking, Agent, Agent Swarm |
| **Pricing** | $0.60/M input, $2.50/M output |
| **Agent Capabilities** | 200-300 tool calls, 100 parallel agents |

**Provider Comparison**:

| Provider | Context | Agent Support | Cost (per M) | DocuSwarm Fit |
|----------|---------|---------------|--------------|---------------|
| **Kimi K2.5** | 256K | Native (Swarm) | $0.60 in / $2.50 out | 9.25/10 |
| **Claude 3.5 Sonnet** | 200K | Tool Use | $3.00 in / $15.00 out | 8.5/10 |
| **GPT-4o** | 128K | Function Calling | $2.50 in / $10.00 out | 7.5/10 |

**Kimi K2.5 Mode Analysis for Dual-Agent Pattern**:

| Mode | Response Time | Use Case | DocuSwarm Mapping |
|------|--------------|----------|-------------------|
| **Instant** | 3-8s | Quick classification | Orchestrator intent routing |
| **Thinking** | Variable | Detailed reasoning | Evaluator Agent reviews |
| **Agent** | Variable | Tool calling workflows | Independent Agent (deliverable + questions) |

### Implementation Guidance

**Provider Configuration (Dual-Agent, kimi-agent-sdk)**:

```yaml
# llm-providers.yaml (MVP - kimi-agent-sdk)
kimi_sdk:
  # kimi-agent-sdk 通过 kimi-cli 子进程与 Kimi K2.5 通信
  # 无需直接指定 api_base / api_key (由 SDK Config 管理)
  
  modes:
    orchestrator:
      # SDK Params
      model: kimi
      thinking: false
      max_steps_per_turn: 5
      # 对应 prompt() 单次 API
      
    independent:
      # SDK Params
      model: kimi
      thinking: false
      max_steps_per_turn: 50
      # 对应 Session.prompt() 多轮 API
      # 工具通过 agent_file.yaml 注册 CallableTool2
      
    evaluator:
      # SDK Params
      model: kimi
      thinking: true
      max_steps_per_turn: 10
      # 对应 prompt() 单次 API (thinking 模式)
      
rate_limits:
  kimi:
    tier: 3
    concurrent_requests: 20
    rpm: 200
    tpm: 5000000
```

**Python LLM Client (kimi-agent-sdk)**:

```python
from kimi_agent_sdk import Session, prompt, Config
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SDKModeParams:
    model: str
    thinking: bool
    max_steps_per_turn: int | None

MODE_MAP = {
    "orchestrator": SDKModeParams(model="kimi", thinking=False, max_steps_per_turn=5),
    "independent": SDKModeParams(model="kimi", thinking=False, max_steps_per_turn=50),
    "evaluator": SDKModeParams(model="kimi", thinking=True, max_steps_per_turn=10),
}

class KimiSessionManager:
    """基于 kimi-agent-sdk 的 LLM 接入层 (替代原 LLMProvider + ChatOpenAI)。"""

    def __init__(self, work_dir: Path | None = None, agent_file: Path | None = None):
        self._work_dir = work_dir or Path.cwd()
        self._agent_file = agent_file

    async def create_session(self, session_id: str, mode: str = "independent") -> Session:
        """创建 SDK Session (对应 Independent Agent 多轮对话)"""
        params = MODE_MAP[mode]
        return await Session.create(
            work_dir=self._work_dir,
            session_id=session_id,
            model=params.model,
            thinking=params.thinking,
            max_steps_per_turn=params.max_steps_per_turn,
            agent_file=self._agent_file,
        )

    async def single_prompt(self, user_input: str, mode: str = "orchestrator") -> list:
        """单次 prompt API (对应 Orchestrator / Evaluator)"""
        params = MODE_MAP[mode]
        messages = []
        async for msg in prompt(
            user_input,
            work_dir=self._work_dir,
            model=params.model,
            thinking=params.thinking,
            agent_file=self._agent_file,
        ):
            messages.append(msg)
        return messages
```

### Recommendation

**Kimi K2.5 as single provider for MVP** (no fallback complexity).

Cost Analysis (per pipeline):
- Estimated tokens: 300K input, 80K output (dual-agent is more efficient)
- Kimi cost: (300K × $0.60 + 80K × $2.50) / 1M = $0.38
- With caching (60% hit rate): ~$0.23 per pipeline

Benefits:
- Native agent mode for Independent Agent
- Thinking mode for high-quality Evaluator reviews
- 76% lower cost than Claude
- OpenAI-compatible API simplifies LangGraph integration
- kimi-agent-sdk 提供原生 Python Session/prompt API

---

## Topic 4.2: Framework Selection (LangGraph)

### Context

**Occam's Razor Decision**: LangGraph replaces custom NodeExecutor and VCPToolBox plugin architecture.

### Research Findings

**Framework Comparison**:

| Framework | Multi-Agent Support | State Management | Maturity |
|-----------|--------------------|-----------------| ---------|
| **LangGraph** | Excellent (native) | Built-in checkpointing | Production |
| **Custom NodeExecutor** | Needs building | Custom implementation | None |
| **AutoGen** | Good | External | Production |
| **CrewAI** | Good | Limited | Maturing |

**LangGraph Benefits**:

| Benefit | Description | Time Saved |
|---------|-------------|------------|
| **StateGraph** | Native state machine for pipelines | 4-6 weeks |
| **Checkpointing** | SQLite/PostgreSQL persistence | 2-3 weeks |
| **Message passing** | Agent communication built-in | 1-2 weeks |
| **Conditional edges** | Iteration/routing logic | 1-2 weeks |

### Implementation Guidance

**LangGraph Pipeline Structure**:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, List, Optional, Annotated
import operator

class PipelineState(TypedDict):
    # Pipeline metadata
    pipeline_id: str
    subject_context: dict
    
    # Current execution state
    current_node: Optional[str]
    completed_nodes: Annotated[List[str], operator.add]
    
    # Results storage
    deliverables: dict
    questions: dict
    evaluations: dict
    
    # Iteration tracking per node
    node_iterations: dict

def create_pipeline_graph(db_path: str = "docuswarm.db") -> StateGraph:
    """Create the main pipeline StateGraph."""
    
    # Create graph with state schema
    graph = StateGraph(PipelineState)
    
    # Define node sequence
    nodes = ["analyst", "pm", "ux", "architect", "po"]
    
    # Add nodes
    for node_id in nodes:
        graph.add_node(node_id, create_node_executor(node_id))
    
    # Add orchestrator as entry
    graph.add_node("orchestrator", orchestrator_router)
    graph.set_entry_point("orchestrator")
    
    # Add edges (orchestrator routes to first node, then sequential)
    graph.add_edge("orchestrator", nodes[0])
    for i in range(len(nodes) - 1):
        graph.add_edge(nodes[i], nodes[i + 1])
    graph.add_edge(nodes[-1], END)
    
    # Compile with SQLite checkpointer
    checkpointer = SqliteSaver.from_conn_string(db_path)
    return graph.compile(checkpointer=checkpointer)

def create_node_executor(node_id: str):
    """Create executor function for a specific node."""
    async def execute(state: PipelineState) -> PipelineState:
        from .nodes import DualAgentNode
        
        # Create and execute dual-agent node
        node = DualAgentNode(node_id)
        result = await node.execute(state["subject_context"])
        
        return {
            "current_node": node_id,
            "completed_nodes": [node_id],
            "deliverables": {node_id: result["deliverable"]},
            "questions": {node_id: result["questions"]},
            "evaluations": {node_id: result["evaluation"]}
        }
    
    return execute
```

**Dual-Agent Node Graph**:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class NodeState(TypedDict):
    subject_context: dict
    iteration: int
    deliverable: Optional[dict]
    questions: Optional[List[dict]]
    private_reasoning: Optional[str]
    evaluation: Optional[dict]

class DualAgentNode:
    """Single node with dual-agent pattern (Independent + Evaluator)."""
    
    MAX_ITERATIONS = 3
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(NodeState)
        
        # Add agents
        graph.add_node("independent", self._run_independent)
        graph.add_node("evaluator", self._run_evaluator)
        
        # Edges
        graph.set_entry_point("independent")
        graph.add_edge("independent", "evaluator")
        
        # Conditional iteration
        graph.add_conditional_edges(
            "evaluator",
            self._should_iterate,
            {"iterate": "independent", "complete": END}
        )
        
        return graph.compile()
    
    async def _run_independent(self, state: NodeState) -> NodeState:
        """Execute Independent Agent: deliverable + questions."""
        # Implementation from section 2.1
        pass
    
    async def _run_evaluator(self, state: NodeState) -> NodeState:
        """Execute Evaluator Agent (context isolated)."""
        # Implementation from section 2.2
        pass
    
    def _should_iterate(self, state: NodeState) -> str:
        """Decide iteration vs completion."""
        verdict = state.get("evaluation", {}).get("verdict", "NEEDS_REVISION")
        iteration = state.get("iteration", 1)
        
        if verdict == "APPROVED":
            return "complete"
        elif iteration >= self.MAX_ITERATIONS:
            return "complete"
        else:
            return "iterate"
    
    async def execute(self, context: dict) -> dict:
        """Execute the dual-agent node."""
        initial_state: NodeState = {
            "subject_context": context,
            "iteration": 0,
            "deliverable": None,
            "questions": None,
            "private_reasoning": None,
            "evaluation": None
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result
```

### Recommendation

**LangGraph as primary framework**.

Benefits:
- ~8-12 weeks development time saved
- Production-ready state management
- Native checkpointing to SQLite
- Active community and documentation

---

## Topic 4.3: BMAD Framework Reuse (Simplified)

### Context

BMAD provides rich agent personas. DocuSwarm extracts these as static configuration without runtime BMAD dependency.

**Occam's Razor Decision**: Extract patterns only - no BMAD runtime module or VCP plugin wrapper.

### Implementation Guidance

**Persona Extraction Script**:

```python
# scripts/extract_personas.py
import re
from pathlib import Path
import json

BMAD_AGENTS = [
    ("analyst", "_bmad/bmm/agents/analyst.md"),
    ("pm", "_bmad/bmm/agents/pm.md"),
    ("designer", "_bmad/bmm/agents/designer.md"),
    ("architect", "_bmad/bmm/agents/architect.md"),
    ("po", "_bmad/bmm/agents/po.md")
]

def extract_persona(content: str) -> dict:
    """Extract persona from BMAD agent markdown."""
    def extract_tag(xml: str, tag: str) -> str:
        match = re.search(rf'<{tag}>([\s\S]*?)</{tag}>', xml)
        return match.group(1).strip() if match else ""
    
    persona_match = re.search(r'<persona>([\s\S]*?)</persona>', content)
    if not persona_match:
        return {}
    
    xml = persona_match.group(1)
    
    return {
        "role": extract_tag(xml, "role"),
        "identity": extract_tag(xml, "identity"),
        "expertise": extract_tag(xml, "expertise"),
        "communication_style": extract_tag(xml, "communication_style") or extract_tag(xml, "communication-style"),
        "principles": extract_tag(xml, "principles")
    }

def main():
    output_dir = Path("nodes")
    
    for agent_id, source_path in BMAD_AGENTS:
        if not Path(source_path).exists():
            print(f"Warning: {source_path} not found")
            continue
        
        content = Path(source_path).read_text(encoding="utf-8")
        persona = extract_persona(content)
        
        # Create node directory
        node_dir = output_dir / agent_id
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # Write persona
        (node_dir / "persona.json").write_text(
            json.dumps(persona, indent=2, ensure_ascii=False)
        )
        
        print(f"Extracted {agent_id} persona")

if __name__ == "__main__":
    main()
```

**Static Persona Usage**:

```python
import json
from pathlib import Path

class PersonaLoader:
    """Load pre-extracted BMAD personas."""
    
    def __init__(self, nodes_path: str = "nodes"):
        self.base_path = Path(nodes_path)
    
    def load_persona(self, node_id: str) -> dict:
        """Load persona for a specific node."""
        persona_path = self.base_path / node_id / "persona.json"
        
        if not persona_path.exists():
            raise FileNotFoundError(f"Persona not found: {persona_path}")
        
        return json.loads(persona_path.read_text(encoding="utf-8"))
    
    def build_system_prompt(self, node_id: str) -> str:
        """Build system prompt from persona."""
        persona = self.load_persona(node_id)
        
        return f"""
# Agent Identity

You are {persona.get('identity', 'a professional agent')}.

## Role
{persona.get('role', '')}

## Expertise
{persona.get('expertise', '')}

## Communication Style
{persona.get('communication_style', '')}

## Guiding Principles
{persona.get('principles', '')}
""".strip()
```

### Recommendation

**Extract patterns as static JSON** - no BMAD runtime dependency.

Benefits:
- Zero runtime coupling
- Simple JSON loading
- One-time extraction (manual sync if BMAD updates)
- DocuSwarm can evolve independently

---

## Topic 4.4: RAG System (Deferred)

### Context

**Occam's Razor Decision**: RAG is deferred to Phase 2. MVP uses direct context passing.

### Research Summary

**Why Defer RAG?**

| Factor | With RAG | Without RAG (MVP) |
|--------|----------|-------------------|
| Implementation Time | +3-4 weeks | Baseline |
| Context Management | Smart retrieval | Direct passing |
| MVP Sufficient? | Overkill | Yes |
| Token Usage | Lower (retrieval) | Higher (full context) |

**MVP Context Strategy**:
- Pipeline state stored in SQLite
- Subject context passed directly to each node
- Previous node deliverables available via state
- 256K context window sufficient for all content

### Implementation Guidance

**Direct Context Passing (MVP)**:

```python
class ContextManager:
    """MVP: Direct context management without RAG."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def build_node_context(self, pipeline_id: str, node_id: str) -> dict:
        """Build context for a node from pipeline state."""
        state = self.state_manager.get_pipeline_state(pipeline_id)
        
        return {
            "subject_context": state["subject_context"],
            "previous_deliverables": {
                nid: node["deliverable"]
                for nid, node in state.get("nodes", {}).items()
                if node.get("status") == "completed"
            },
            "pipeline_metadata": {
                "pipeline_id": pipeline_id,
                "current_node": node_id,
                "completed_nodes": list(state.get("nodes", {}).keys())
            }
        }
```

**Phase 2 RAG Integration Path**:

```python
# Phase 2: Add RAG when needed
class RAGContextManager(ContextManager):
    """Phase 2: RAG-enhanced context management."""
    
    def __init__(self, state_manager, rag_client):
        super().__init__(state_manager)
        self.rag = rag_client
    
    async def build_node_context(self, pipeline_id: str, node_id: str) -> dict:
        """Build context with RAG enhancement."""
        base_context = super().build_node_context(pipeline_id, node_id)
        
        # Add RAG retrieval
        relevant_docs = await self.rag.query(
            query=base_context["subject_context"].get("project_name", ""),
            filters={"pipeline_id": pipeline_id}
        )
        
        base_context["retrieved_context"] = relevant_docs
        return base_context
```

### Recommendation

**Defer RAG to Phase 2** - MVP uses direct context passing.

Benefits:
- ~3-4 weeks development time saved
- Simpler architecture for MVP
- 256K context window is sufficient
- Clear upgrade path when needed

---

## Topic 4.5: Tool Calling (CallableTool2 via kimi-agent-sdk)

### Context

**kimi-agent-sdk 改造**: 使用 SDK 原生 CallableTool2 + Pydantic BaseModel 替代手动 OpenAI Functions JSON Schema。工具通过 agent_file.yaml 注册，SDK 自动调度。

### Research Summary

**工具定义方式对比**:

| 方式 | Token 开销 | 类型安全 | 自动调度 | MVP 适配 |
|------|-----------|---------|---------|---------|
| **手动 JSON Schema (旧)** | 中等 | 无 | 否 (需手动解析) | 已废弃 |
| **CallableTool2 + Pydantic (新)** | 低 | 强 (Pydantic) | 是 (SDK 内部) | 当前方案 |
| **MCP** | 低 | 中等 | 是 | 不再需要 |

### Implementation Guidance

**CallableTool2 工具定义**:

```python
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue

class CreateDeliverableParams(BaseModel):
    title: str = Field(description="Document title")
    content: str = Field(description="Document content (markdown)")

class CreateDeliverableTool(CallableTool2):
    name: str = "create_deliverable"
    description: str = "Create the node's deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        # ... 保存可交付物逻辑
        return ToolOk(output=f"Deliverable '{params.title}' created")

class UpdateContextParams(BaseModel):
    key: str = Field(description="Context key")
    value: dict = Field(description="Value to store")

class UpdateContextTool(CallableTool2):
    name: str = "update_context"
    description: str = "Update shared subject context"
    params: type[UpdateContextParams] = UpdateContextParams

    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        # ... 更新上下文逻辑
        return ToolOk(output=f"Context '{params.key}' updated")
```

**agent_file.yaml 工具注册**:

```yaml
version: 1
agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
```

### Recommendation

**CallableTool2 + agent_file.yaml** — SDK 原生工具体系。

优势:
- Pydantic 参数验证 (类型安全)
- SDK 自动调度 (无需手动解析 tool_calls)
- YAML 声明式注册 (代码与配置分离)
- MCP 迁移不再需要

### Implementation Gap (2026-02-23)

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

**发现**: CallableTool2 工具定义和 agent_file.yaml 配置均已正确实现，但**运行时从未被激活**：

| 组件 | 实现状态 | 运行时状态 | 原因 |
|------|---------|-----------|------|
| `CreateDeliverableTool` 类 | 完整 | 未实例化 | Session 未传入 `agent_file` |
| `independent_agent.yaml` | 完整 | 未加载 | `IndependentAgent` 创建 Session 时未传入 |
| `KimiSessionManager.create_session()` | 支持 `agent_file` 参数 | 未被使用 | 调用方未传入该参数 |

**根本原因**: IndependentAgent 的提示词同时要求"使用工具"和"只返回JSON"，造成冲突。且 Session 创建时未传入 `agent_file` 和 `work_dir`，导致 SDK 无法注册工具。

**修复方案 (方案C)**: 
1. 创建 Session 时传入 `agent_file` 路径和 `work_dir`（`output/{pipeline_id}/`）
2. 修改提示词：移除 JSON-only 输出要求，明确要求使用 `create_deliverable` 工具
3. 设置 `yolo=True` 自动批准文件写入

---

## Topic 4.6: Programming Language (Python)

### Context

**Occam's Razor Decision**: Python with LangGraph (not TypeScript + VCPToolBox).

### Research Findings

**Language Choice Impact**:

| Aspect | TypeScript + VCPToolBox | Python + LangGraph |
|--------|------------------------|-------------------|
| Framework Native | No (custom build) | Yes |
| Multi-Agent Support | Build yourself | Built-in |
| State Management | Build yourself | Built-in |
| Implementation Time | +8-12 weeks | Baseline |

### Implementation Guidance

**Python Project Structure**:

```
docuswarm/
├── pyproject.toml              # Project configuration
├── README.md
├── docuswarm/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration loading
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── graph.py            # LangGraph pipeline
│   │   └── state.py            # State definitions
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── session_manager.py  # KimiSessionManager (SDK 适配层)
│   │   ├── mode_mapper.py      # SDKModeParams + MODE_MAP
│   │   ├── approval.py         # ApprovalRequest 处理
│   │   └── service.py          # LLMService 统一服务
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── independent.py      # Independent Agent (Session.prompt)
│   │   ├── evaluator.py        # Evaluator Agent (prompt + thinking)
│   │   └── orchestrator.py     # Orchestrator
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── create_deliverable.py  # CallableTool2
│   │   └── update_context.py      # CallableTool2
│   │
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── dual_agent.py       # Dual-agent node
│   │   └── loader.py           # Node configuration
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── sqlite.py           # SQLite state manager
│   │   └── memory.py           # Memory management
│   │
│   └── utils/
│       ├── __init__.py
│       └── persona.py          # Persona extraction
│
├── nodes/                      # Node configurations
│   ├── analyst/
│   │   ├── node.yaml
│   │   ├── persona.json
│   │   └── evaluator.yaml
│   ├── pm/
│   ├── ux/
│   ├── architect/
│   └── po/
│
└── tests/
    ├── __init__.py
    ├── test_pipeline.py
    ├── test_agents.py
    └── test_nodes.py
```

**pyproject.toml**:

```toml
[project]
name = "docuswarm"
version = "1.0.0"
description = "Multi-agent document orchestration system"
requires-python = ">=3.10"
dependencies = [
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "kimi-agent-sdk>=0.1.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Recommendation

**Python 3.10+ with LangGraph**.

Benefits:
- LangGraph is Python-native
- Rich async support for LLM calls
- Strong typing with Pydantic
- Simpler deployment (no build step)

---

## Topic 4.7: Database Selection (SQLite)

### Context

**Occam's Razor Decision**: SQLite for all persistence (state, checkpoints). No separate vector database for MVP.

### Research Findings

**Storage Requirements**:

| Data Type | Volume | Solution |
|-----------|--------|----------|
| Pipeline State | Small (JSON) | SQLite |
| Checkpoints | Medium | SQLite (LangGraph native) |
| Deliverables | Medium (markdown) | SQLite + files |
| Vectors | N/A (deferred) | N/A |

### Implementation Guidance

**SQLite Configuration**:

```python
import sqlite3
from pathlib import Path

class DatabaseManager:
    """SQLite database manager with WAL mode."""
    
    def __init__(self, db_path: str = "docuswarm.db"):
        self.db_path = Path(db_path)
        self.conn = self._create_connection()
        self._initialize_schema()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create SQLite connection with WAL mode."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False  # Allow multi-thread access
        )
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Set busy timeout (5 seconds)
        conn.execute("PRAGMA busy_timeout=5000")
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        
        return conn
    
    def _initialize_schema(self):
        """Initialize database schema."""
        self.conn.executescript("""
            -- Pipelines table
            CREATE TABLE IF NOT EXISTS pipelines (
                pipeline_id TEXT PRIMARY KEY,
                subject_context TEXT NOT NULL,
                status TEXT DEFAULT 'running',
                current_node TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Node results table
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
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id)
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_node_pipeline 
            ON node_results(pipeline_id, node_id);
            
            CREATE INDEX IF NOT EXISTS idx_pipeline_status 
            ON pipelines(status);
        """)
        self.conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return self.conn
```

**LangGraph SQLite Checkpointer**:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

def create_checkpointer(db_manager: DatabaseManager) -> SqliteSaver:
    """Create LangGraph checkpointer using existing connection."""
    return SqliteSaver(db_manager.get_connection())
```

### Recommendation

**SQLite with WAL mode** for all MVP persistence.

Benefits:
- Single database for all needs
- LangGraph checkpointer integration
- No external services to manage
- Easy backup (single file)
- WAL mode enables concurrent access

---

## Cross-Topic Dependencies (Updated)

```
4.1 LLM Provider
 └─→ 1.4 Orchestrator Design (Kimi Instant mode)
 └─→ 2.1 Independent Agent (Kimi Agent mode)
 └─→ 2.2 Evaluator Agent (Kimi Thinking mode)

4.2 Framework (LangGraph)
 └─→ 1.3 Pipeline Orchestration
 └─→ 3.5 State Persistence
 └─→ 3.6 Checkpoint/Resume

4.3 BMAD Reuse
 └─→ 2.1 Persona Extraction
 └─→ Static JSON (no runtime dependency)

4.4 RAG System
 └─→ Deferred to Phase 2
 └─→ MVP: Direct context passing

4.5 Tool Calling (CallableTool2)
 └─→ kimi-agent-sdk 原生工具体系
 └─→ agent_file.yaml 声明式注册
 └─→ MCP 迁移不再需要

4.6 Programming Language
 └─→ Python (LangGraph native)
 └─→ 7.3 Testing Strategy (pytest)

4.7 Database
 └─→ SQLite for all persistence
 └─→ LangGraph checkpointer integration
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 4.2 Framework | Custom NodeExecutor | LangGraph | ~8-12 weeks |
| 4.3 BMAD | Runtime module + VCP plugin | Static JSON extraction | ~2 weeks |
| 4.4 RAG | TagMemo V5 integration | Deferred (direct context) | ~3-4 weeks |
| 4.5 Protocol | Abstraction layer + MCP path | CallableTool2 (kimi-agent-sdk 原生) | ~1 week |
| 4.6 Language | TypeScript + VCPToolBox | Python + LangGraph | Simpler |
| 4.7 Database | SQLite + vexus-lite | SQLite only | ~1 week |

**Total Estimated Savings**: ~8-12 weeks development time

---

## References

### Research Sources
- Kimi K2.5 Complete Guide (codecademy.com, 2026)
- LangGraph Documentation (langchain-ai.github.io, 2026)
- SQLite WAL Mode Documentation (sqlite.org)

### Related Analysis Documents
- [1_ARCHITECTURE_AND_DESIGN.md](1_ARCHITECTURE_AND_DESIGN.md) - Architecture decisions (v2.0)
- [5_STATE_MANAGEMENT.md](5_STATE_MANAGEMENT.md) - SQLite state management
- [6_INTEGRATION_AND_API.md](6_INTEGRATION_AND_API.md) - API integration

---

**Document Status**: Version 3.1 - Updated with tool integration gap analysis  
**Key Change**: KimiSessionManager 替代 LLMProvider + ChatOpenAI; CallableTool2 替代手动 JSON Schema; 发现 agent_file 未激活问题  
**Development Time Savings**: ~8-12 weeks compared to original design

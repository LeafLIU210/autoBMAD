# DocuSwarm System Architecture

**Version**: 3.0 (BMM NodeExecutor Refactor)  
**Date**: 2026-03-02  
**Status**: Approved  
**Author**: Solution Architect  

> **Note**: 本文档已更新以反映 BMM NodeExecutor 重构后的架构。详见 [TDD-BMM-05: 主实施指南](../solution/TDD-BMM-05-Master-Implementation-Guide.md)。  

---

## 1. Executive Summary

DocuSwarm is a **Multi-Agent Document Orchestration System** built on the BMAD methodology. This document provides the high-level system architecture overview.

### 1.1 Architecture Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **Occam's Razor** | Simplest solution that achieves goals | LangGraph over custom NodeExecutor |
| **Defense in Depth** | Multiple security layers | Three-layer context isolation |
| **Separation of Concerns** | Clear module boundaries | Agent, Node Execution, State modules |
| **Fail-Safe Defaults** | Safe behavior on failure | Max iterations, escalation |

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | LangGraph | Battle-tested, saves 8-12 weeks |
| **Agent Pattern** | Dual-Agent | Independent + Evaluator, 33% simpler |
| **LLM Provider** | Kimi K2.5 | 256K context, cost-effective |
| **Persistence** | SQLite WAL | ACID, simple deployment |
| **Node Config** | YAML + JSON | Preprocessed BMM content embedded in node configs |
| **Execution** | User-driven per-node | User selects which node to run, context auto-chaining |

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DocuSwarm System                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        User Interface Layer                          │   │
│  │  ┌──────────────────┐                                               │   │
│  │  │   CLI Interface  │  (MVP - Python argparse/click)                │   │
│  │  └──────────────────┘                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CLI Layer                                       │   │
│  │  ┌──────────────────┐    ┌─────────────────┐    ┌───────────────┐  │   │
│  │  │  CLI Commands    │───▶│  LangGraph      │───▶│  Checkpoint   │  │   │
│  │  │                  │    │  StateGraph     │    │  Manager      │  │   │
│  │  └──────────────────┘    └─────────────────┘    └───────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Node Execution Layer                            │   │
│  │                     (User-driven, auto context chain)                │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────┐│
│  │  │  Analyst  │  │    PM     │  │    UX     │  │ Architect │  │  PO   ││
│  │  │   Node    │  │   Node    │  │   Node    │  │   Node    │  │ Node  ││
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘  └───────┘│
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          Agent Layer                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                   Dual-Agent Node                            │    │   │
│  │  │  ┌─────────────────┐         ┌─────────────────┐           │    │   │
│  │  │  │  Independent    │────────▶│   Evaluator     │           │    │   │
│  │  │  │  Agent          │         │   Agent         │           │    │   │
│  │  │  │  • Deliverable  │         │   • Review      │           │    │   │
│  │  │  │  • Questions    │         │   • Score       │           │    │   │
│  │  │  │  • Reasoning*   │         │   • Verdict     │           │    │   │
│  │  │  └─────────────────┘         └─────────────────┘           │    │   │
│  │  │            * Context Isolated                               │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Integration Layer                            │   │
│  │  ┌──────────────────┐    ┌─────────────────┐    ┌───────────────┐  │   │
│  │  │   LLM Client     │    │  Context        │    │   Tool        │  │   │
│  │  │   (Kimi K2.5)    │    │  Manager        │    │   Executor    │  │   │
│  │  └──────────────────┘    └─────────────────┘    └───────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Persistence Layer                             │   │
│  │  ┌──────────────────┐    ┌─────────────────┐    ┌───────────────┐  │   │
│  │  │   SQLite WAL     │    │  State Manager  │    │   File        │  │   │
│  │  │   Database       │    │                 │    │   Storage     │  │   │
│  │  └──────────────────┘    └─────────────────┘    └───────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Inventory

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| CLI Interface | Python Click | User commands (start/status/export/questions/answer per node) |
| Context Validator | Python + Kimi Instant | Context file validation |
| LangGraph Node | LangGraph StateGraph | Per-node dual-agent execution |
| Dual-Agent Node | Python + LangGraph | Document creation and evaluation |
| LLM Client | claude-agent-sdk | Kimi K2.5 API interaction via Kimi Code API (ANTHROPIC_API_KEY) |
| Context Manager | Python | Context isolation enforcement |
| State Manager | SQLite + WAL | State persistence |
| Checkpoint Manager | LangGraph SqliteSaver | Node run checkpointing |

---

## 3. Architecture Layers

### 3.1 User Interface Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MVP: CLI Interface                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Commands:                                           │   │
│  │  • docuswarm init --context <file>                  │   │
│  │  • docuswarm start <node> --context <file>          │   │
│  │  • docuswarm status <node>                          │   │
│  │  • docuswarm export <node>                          │   │
│  │  • docuswarm questions <node>                       │   │
│  │  • docuswarm answer <node> <question-id> <answer>   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Future: Web UI                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Dashboard (node overview per context)            │   │
│  │  • Node Execution View                              │   │
│  │  • Node Detail View                                 │   │
│  │  • Question Answering Panel                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Context Validation Layer

```
┌─────────────────────────────────────────────────────────────┐
│                 Context Validation Layer                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Context Validator                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────┐        │   │
│  │  │   Validate context file                 │        │   │
│  │  │   Compute context_hash                  │        │   │
│  │  │   Chain predecessor deliverables        │        │   │
│  │  └─────────────┬───────────────────────────┘        │   │
│  │                │                                     │   │
│  │                ▼                                     │   │
│  │  ┌─────────────────────────────────────────┐        │   │
│  │  │        LangGraph StateGraph             │        │   │
│  │  │  (Single node dual-agent execution)     │        │   │
│  │  │  ┌─────────────────────────────────┐    │        │   │
│  │  │  │  User-selected Node             │    │        │   │
│  │  │  │  Independent → Evaluator loop   │    │        │   │
│  │  │  │  Checkpointer: SQLite           │    │        │   │
│  │  │  └─────────────────────────────────┘    │        │   │
│  │  └─────────────────────────────────────────┘        │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Node Execution Layer

```
┌─────────────────────────────────────────────────────────────┐
│                   Node Execution Layer                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User-Driven Node Execution (MVP)                           │
│  User drives execution order. Context chaining auto-injects │
│  predecessor deliverables.                                  │
│                                                             │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────┐   │
│  │Analyst │  │   PM   │  │   UX   │  │Archit. │  │ PO │   │
│  │  Node  │  │  Node  │  │  Node  │  │  Node  │  │Node│   │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────┘   │
│      │           │           │           │          │      │
│      ▼           ▼           ▼           ▼          ▼      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────┐  │
│  │Analyst │  │  PRD   │  │   UX   │  │Archit. │  │Epic│  │
│  │Report  │  │        │  │ Design │  │  Doc   │  │Docs│  │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────┘  │
│                                                             │
│  Phase 2: DAG-Based Parallel (Deferred)                    │
│                                                             │
│           ┌────────┐                                        │
│           │Analyst │                                        │
│           │  Node  │                                        │
│           └────┬───┘                                        │
│                │                                            │
│         ┌──────┴──────┐                                     │
│         ▼             ▼                                     │
│     ┌────────┐   ┌────────┐                                │
│     │   PM   │   │   UX   │  ← Parallel                    │
│     │  Node  │   │  Node  │                                │
│     └────┬───┘   └────┬───┘                                │
│          └──────┬─────┘                                     │
│                 ▼                                           │
│           ┌────────┐                                        │
│           │Archit. │                                        │
│           │  Node  │                                        │
│           └────┬───┘                                        │
│                ▼                                            │
│           ┌────────┐                                        │
│           │   PO   │                                        │
│           │  Node  │                                        │
│           └────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Agent Layer

```
┌─────────────────────────────────────────────────────────────┐
│                       Agent Layer                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dual-Agent Pattern (Per Node)                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  Subject Context                                     │   │
│  │        │                                             │   │
│  │        ▼                                             │   │
│  │  ┌─────────────────────┐                            │   │
│  │  │  Independent Agent  │  ← Kimi Agent Mode         │   │
│  │  │  ├── BMAD Persona   │                            │   │
│  │  │  ├── Deliverable    │                            │   │
│  │  │  ├── Questions      │                            │   │
│  │  │  └── Reasoning*     │  * Private                 │   │
│  │  └──────────┬──────────┘                            │   │
│  │             │                                        │   │
│  │             │  Context Filter                        │   │
│  │             │  (Remove private reasoning)            │   │
│  │             ▼                                        │   │
│  │  ┌─────────────────────┐                            │   │
│  │  │   Evaluator Agent   │  ← Kimi Thinking Mode      │   │
│  │  │  ├── Review         │                            │   │
│  │  │  ├── Criterion Scores│                           │   │
│  │  │  ├── Verdict        │                            │   │
│  │  │  └── Feedback       │                            │   │
│  │  └──────────┬──────────┘                            │   │
│  │             │                                        │   │
│  │             ▼                                        │   │
│  │  ┌─────────────────────┐                            │   │
│  │  │   Iteration Logic   │                            │   │
│  │  │  APPROVED → Next    │                            │   │
│  │  │  REVISION → Iterate │  (max 3)                   │   │
│  │  │  BLOCKED → Stop     │                            │   │
│  │  └─────────────────────┘                            │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 Integration Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     Integration Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   LLM Client                         │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Provider: Kimi K2.5                          │  │   │
│  │  │  ├── Context Validation: Instant Mode (0.3 temp)│  │   │
│  │  │  ├── Independent: Agent Mode (0.7 temp)      │  │   │
│  │  │  └── Evaluator: Thinking Mode (0.5 temp)     │  │   │
│  │  │                                               │  │   │
│  │  │  Rate Limiting: 200 RPM, 5M TPM              │  │   │
│  │  │  Retry: 3 attempts, exponential backoff      │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Context Manager                      │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Three-Layer Isolation:                       │  │   │
│  │  │  1. Separate Prompt Templates                 │  │   │
│  │  │  2. Runtime Access Control                    │  │   │
│  │  │  3. Message-Level Filtering                   │  │   │
│  │  │                                               │  │   │
│  │  │  build_independent_context() → Full access   │  │   │
│  │  │  build_evaluator_context() → Restricted      │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Tool Executor                       │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  MVP Tools (CallableTool2):                │  │   │
│  │  │  • create_deliverable                         │  │   │
│  │  │  • update_context                             │  │   │
│  │  │                                               │  │   │
│  │  │  ~~Phase 2: MCP Protocol Migration~~ → SDK MCP 格式迁移完成 │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.6 Persistence Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     Persistence Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  SQLite Database                     │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Configuration:                               │  │   │
│  │  │  • WAL Mode (concurrent reads)               │  │   │
│  │  │  • Busy Timeout: 5000ms                      │  │   │
│  │  │  • Foreign Keys: ON                          │  │   │
│  │  │                                               │  │   │
│  │  │  Tables:                                      │  │   │
│  │  │  • node_runs (per-node execution results)   │  │   │
│  │  │  • pipelines (with state_json as single     │  │   │
│  │  │                source of truth - F2)         │  │   │
│  │  │  • subject_context (cached context,         │  │   │
│  │  │                      keyed by context_hash)  │  │   │
│  │  │  • checkpoints (LangGraph managed)           │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   File Storage                       │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │  Output Structure:                            │  │   │
│  │  │  output/                                      │  │   │
│  │  │  ├── {node}/{run-id}/                        │  │   │
│  │  │  │   ├── deliverable.md                      │  │   │
│  │  │  │   ├── evaluation.json                     │  │   │
│  │  │  │   └── questions.json                      │  │   │
│  │  │  └── ...                                      │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Architecture

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Data Model Overview                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐       ┌──────────────────┐           │
│  │   Node Runs      │       │  Subject Context │           │
│  ├──────────────────┤       ├──────────────────┤           │
│  │ run_id (PK)      │       │ context_hash (PK)│           │
│  │ node (TEXT)      │       │ context_data     │           │
│  │ context_hash     │──────▶│ updated_at       │           │
│  │ context_file     │       └──────────────────┘           │
│  │ iteration        │                                      │
│  │ status           │                                      │
│  │ deliverable      │                                      │
│  │ questions        │                                      │
│  │ evaluation       │                                      │
│  │ answers          │                                      │
│  │ created_at       │                                      │
│  │ updated_at       │                                      │
│  └──────────────────┘                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 State Schema

```python
# LangGraph Node Run State
class NodeRunState(TypedDict):
    run_id: str
    node: str
    context_hash: str
    context_data: dict
    chained_deliverables: Dict[str, str]  # predecessor deliverables
    iteration: int
    deliverable: Optional[dict]
    questions: Optional[List[dict]]
    private_reasoning: Optional[str]
    evaluation: Optional[dict]
    status: str  # pending | running | completed | failed | blocked
```

---

## 5. Deployment Architecture

### 5.1 MVP Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                  MVP Deployment (Single Machine)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Host Machine                      │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │         Python Virtual Environment          │    │   │
│  │  │                                              │    │   │
│  │  │  ┌────────────────────────────────────┐     │    │   │
│  │  │  │        DocuSwarm Application       │     │    │   │
│  │  │  │  ├── docuswarm/                    │     │    │   │
│  │  │  │  ├── nodes/                        │     │    │   │
│  │  │  │  └── output/                       │     │    │   │
│  │  │  └────────────────────────────────────┘     │    │   │
│  │  │                                              │    │   │
│  │  │  ┌────────────────┐  ┌─────────────────┐   │    │   │
│  │  │  │ docuswarm.db   │  │ .env            │   │    │   │
│  │  │  │ (SQLite)       │  │ (ANTHROPIC_API_│   │    │   │
│  │  │  └────────────────┘  └─────────────────┘   │    │   │
│  │  │                                              │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Kimi K2.5 API (External)               │   │
│  │              https://api.moonshot.cn/v1             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Directory Structure

```
docuswarm/
├── pyproject.toml                # Project configuration
├── README.md                     # Project documentation
├── .env                          # Environment variables
├── docuswarm.db                  # SQLite database (created at runtime)
│
├── docuswarm/                    # Main package
│   ├── __init__.py
│   ├── main.py                   # CLI entry point
│   ├── config.py                 # Configuration loading
│   │
│   ├── node_execution/           # Node execution
│   │   ├── __init__.py
│   │   ├── graph.py              # LangGraph node execution
│   │   ├── context_validator.py # Context validation
│   │   └── state.py              # State definitions
│   │
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── independent.py        # Independent Agent
│   │   ├── evaluator.py          # Evaluator Agent
│   │   └── persona.py            # Persona loading
│   │
│   ├── nodes/                    # Node implementations
│   │   ├── __init__.py
│   │   ├── dual_agent.py         # Dual-agent node
│   │   └── loader.py             # Node configuration
│   │
│   ├── context/                  # Context management
│   │   ├── __init__.py
│   │   ├── isolation.py          # Context isolation
│   │   └── memory.py             # Memory management
│   │
│   ├── storage/                  # Persistence
│   │   ├── __init__.py
│   │   ├── sqlite.py             # SQLite state manager
│   │   └── files.py              # File storage
│   │
│   └── llm/                      # LLM integration
│       ├── __init__.py
│       ├── client.py             # LLM client
│       └── tools.py              # Tool definitions
│
├── nodes/                        # Node configurations (BMM-aligned)
│   ├── analyst/
│   │   ├── node.yaml          # 包含 task 块和 deliverable 配置
│   │   ├── persona.json       # BMM 角色上下文 (Mary)
│   │   └── evaluator.yaml     # 评估标准
│   ├── pm/                    # John - Product Manager
│   ├── ux/                    # Sally - UX Designer
│   ├── architect/             # Winston - System Architect
│   └── po/                    # PO - Epic/Story Specialist
│
├── output/                       # Generated deliverables
│   └── {node}/{run-id}/
│
└── tests/                        # Test suite
    ├── __init__.py
    ├── test_node_execution.py
    ├── test_agents.py
    └── test_nodes.py
```

---

## 6. Cross-Cutting Concerns

### 6.1 Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Strategy                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Level 1: LLM API Errors                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Retry with exponential backoff (max 3)           │   │
│  │  • Rate limit: wait and retry                       │   │
│  │  • Timeout: extend timeout, retry                   │   │
│  │  • Permanent failure: escalate to user              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 2: Node Execution Errors                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Iteration exceeded: force complete with warning  │   │
│  │  • Blocked verdict: escalate to user                │   │
│  │  • Invalid output: retry with guidance              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Level 3: Run-Level Errors                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Run failure: checkpoint and report               │   │
│  │  • Database error: rollback, report                 │   │
│  │  • Unexpected: log details, mark run failed         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Logging Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                     Logging Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Log Levels:                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  DEBUG   │ Agent prompts, LLM responses             │   │
│  │  INFO    │ Node run progress, node completion          │   │
│  │  WARNING │ Iterations, quality below threshold      │   │
│  │  ERROR   │ API failures, validation errors          │   │
│  │  CRITICAL│ Database corruption, unrecoverable       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Log Format:                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  {timestamp} [{level}] {node} {run_id}              │   │
│  │  {message}                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Output Destinations:                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Console (INFO and above)                         │   │
│  │  • File: docuswarm.log (DEBUG and above)           │   │
│  │  • Structured JSON for tooling                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Configuration Management

```yaml
# config/docuswarm.yaml
node_execution:
  max_iterations: 3
  approval_threshold: 0.70
  escalation_threshold: 0.50

llm:
  provider: kimi
  api_base: https://api.moonshot.cn/v1
  models:
    orchestrator: { mode: instant, temperature: 0.3 }
    independent: { mode: agent, temperature: 0.7 }
    evaluator: { mode: thinking, temperature: 0.5 }
  rate_limit:
    rpm: 200
    tpm: 5000000
  retry:
    max_attempts: 3
    backoff_base: 1.0

storage:
  database: docuswarm.db
  output_dir: output

logging:
  level: INFO
  file: docuswarm.log
  format: structured
```

---

## 7. Quality Attributes

### 7.1 Performance

| Metric | Target | Strategy |
|--------|--------|----------|
| Node execution | < 2 min | Kimi K2.5 Agent mode |
| Per-node total | < 3 min | Single node dual-agent loop |
| API latency | < 30s | Timeout handling |
| Checkpoint time | < 1s | SQLite WAL mode |

### 7.2 Reliability

| Metric | Target | Strategy |
|--------|--------|----------|
| System uptime | 99% | Stateless components |
| Data durability | 100% | SQLite ACID |
| Recovery success | 100% | LangGraph checkpoints |
| API retry success | 95% | Exponential backoff |

### 7.3 Security

| Concern | Mitigation |
|---------|------------|
| API key exposure | Environment variables |
| Context leakage | Three-layer isolation |
| Input validation | JSON schema validation |
| Output sanitization | Private marker removal |

---

## 8. Architecture Decision Records (ADRs)

### ADR-001: LangGraph Framework

**Status**: Accepted  
**Context**: Need multi-agent orchestration framework  
**Decision**: Use LangGraph instead of custom NodeExecutor  
**Consequences**: +8-12 weeks saved, dependency on LangChain ecosystem

### ADR-002: Dual-Agent Pattern

**Status**: Accepted  
**Context**: Quality control mechanism needed  
**Decision**: Independent + Evaluator (defer Questioner)  
**Consequences**: +33% simpler, questions embedded in Independent

### ADR-003: Kimi K2.5 Single Provider

**Status**: Accepted  
**Context**: LLM provider selection  
**Decision**: Kimi K2.5 only for MVP  
**Consequences**: No fallback, 256K context sufficient

### ADR-004: SQLite Persistence

**Status**: Accepted  
**Context**: State persistence requirement  
**Decision**: SQLite with WAL mode  
**Consequences**: Simple deployment, ACID guarantees

### ADR-005: User-Driven Node Execution

**Status**: Accepted  
**Context**: Node execution strategy  
**Decision**: User chooses which node to execute, context auto-chaining  
**Consequences**: Fine-grained control, no automatic sequential execution

### ADR-006: BMM NodeExecutor Refactor

**Status**: Accepted  
**Context**: Node configuration and persona system needs alignment with BMM methodology  
**Decision**: 
1. Preprocess all BMM content from `_bmad/bmm/` into `autoBMAD/nodes/*/persona.json`
2. Add `communication_style` field to Persona for unique character expression
3. Add `task` block to node.yaml for BMM workflow alignment
4. Extend `deliverable` config with `template_title` and `output_filename`
5. Remove deprecated fields (`description`, `questions`, `dependencies`)
6. Remove `templates/` directory (DRY violation, `_bmad` reference)

**Consequences**: 
- Runtime zero external dependency on `_bmad/`
- Persona-driven system prompt construction
- Consistent 5-node persona mapping (Mary/John/Sally/Winston/PO)

### ADR-007: Single Execution Trunk (P0-2)

**Status**: Accepted  
**Context**: Multiple execution trunks (`create_node_executor` implementations, graph factories) create cognitive overhead and regression risk  
**Decision**: 
1. **Physical deletion** of all secondary implementations (no compat/legacy layer)
2. `node_execution/executor.py:create_node_executor` is the **sole** implementation
3. `pipeline/graph.py:create_pipeline_graph` is the **sole** graph factory
4. Remove `node_execution/graph.py`, `node_execution/flow.py`
5. Remove `nodes/dual_agent.py:create_node_executor`

**Consequences**: 
- Zero ambiguity about which path is "the" path
- Import errors for any code referencing old symbols
- Architecture tests enforce single-trunk invariant

### ADR-008: Sync/Async Contract Unification (P0-3)

**Status**: Accepted  
**Context**: `await` on sync methods, `run_until_complete` nesting, and `_run_async` bridges create fragile async boundaries  
**Decision**: 
1. `StateManager` is **synchronous** (because underlying storage is `sqlite3`)
2. Upper async layers bridge via `asyncio.to_thread()` (no custom `_run_async`)
3. `pipeline/graph.py` **rejects** self-bootstrapping checkpointer (hard fail)
4. AST-based architecture tests enforce contract compliance

**Consequences**: 
- Clear contract: sync storage, async orchestration with explicit bridging
- No hidden event loop nesting
- CI fails on any `await <sync_method>` or `run_until_complete` in async contexts

---

## 9. BMM NodeExecutor Refactor (Completed)

> **Implementation Guide**: [TDD-BMM-05: 主实施指南](../solution/TDD-BMM-05-Master-Implementation-Guide.md)

### 9.1 Refactor Scope

**Status**: ✅ Implemented

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | NodeLoader config refactor (TDD-BMM-01) | ✅ Complete |
| **Phase 2** | Persona & System Prompt refactor (TDD-BMM-02) | ✅ Complete |
| **Phase 3** | Deprecated code removal (TDD-BMM-03) | ✅ Complete |
| **Phase 4** | Integration & E2E testing (TDD-BMM-04) | ✅ Complete |

### 9.2 Key Changes

**Configuration Structure**:
```yaml
# nodes/analyst/node.yaml (New Format)
node_id: analyst
name: Analyst
sequence: 1

agent:
  type: independent
  model: sonnet
  temperature: 0.7

task:                          # NEW
  name: create-product-brief
  description: Create comprehensive product briefs...
  role_supplement: You are a product-focused Business Analyst...

deliverable:                   # EXTENDED
  type: product-brief
  template_title: "Product Brief: {project_name}"      # NEW
  required_sections: [executive_summary, core_vision, ...]
  output_filename: "product-brief-{project_name}.md"   # NEW
```

**Persona Structure**:
```json
{
  "name": "Mary",
  "role": "Strategic Business Analyst + Requirements Expert",
  "identity": "Senior analyst with deep expertise...",
  "communication_style": "Speaks with the excitement of a treasure hunter...",
  "expertise": ["Market research", "SWOT analysis", ...],
  "principles": ["Ground findings in evidence", ...]
}
```

**Five-Node Persona Mapping**:
| Node | Persona | Name | Key Trait |
|------|---------|------|-----------|
| Analyst | Mary | Strategic Business Analyst | Treasure hunter excitement |
| PM | John | Product Manager | Asks WHY relentlessly |
| UX | Sally | UX Designer | Paints pictures with words |
| Architect | Winston | System Architect | Calm, pragmatic tones |
| PO | PO | Product Owner | Epic/story specialist |

### 9.3 Removed Components

| Component | Removal Reason |
|-----------|---------------|
| `templates/*.yaml` | DRY violation, contained `_bmad` references |
| `NodeQuestionConfig` | Automation doesn't use manual questions |
| `NodeQuestionsConfig` | Questions generated by Independent Agent |
| `NodeDependenciesConfig` | Managed by graph.py edges |
| `_create_default_node_executor()` | Created empty deliverables |
| `description` field | Redundant with task description |

### 9.4 Architecture Constraints

**Zero External Dependency Rule**:
- `autoBMAD/docuswarm` runtime MUST NOT reference `_bmad/` or external folders
- All BMM content preprocessed into `autoBMAD/nodes/*/persona.json`
- Template information embedded in `node.yaml` deliverable block

---

## 10. References

### Related Documents

| Document | Location |
|----------|----------|
| Agent System Architecture | `02_AGENT_ARCHITECTURE.md` |
| Node Execution Architecture | `03_PIPELINE_ARCHITECTURE.md` |
| State Management | `04_STATE_ARCHITECTURE.md` |
| LLM Integration | `05_LLM_INTEGRATION.md` |
| Context Isolation | `06_CONTEXT_ISOLATION.md` |

### External References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Kimi K2.5 API Reference](https://platform.moonshot.cn/docs)
- [SQLite WAL Mode](https://sqlite.org/wal.html)

---

**Document End**
> **2026-03-13 Alignment Notice**: 当前系统的真实主链应理解为“旧 `node.yaml` + 运行时 task 抽取 + DualAgentNode 二次包装 + 文件/状态双写”的过渡实现，而非本文档描述的稳定目标态。后续重构以 `../research/2026-03-13-docuswarm-context-refactor-overview.md` 为总览入口。

>
> **2026-03-17 Update**: 产品已决定工作流完全不读取 \docs/\ 目录。因此：
> - P1-2 (受控 docs 上下文策略) 已从重构计划中移除
> - 所有 docs 相关读取/写入能力应进入清理范围
> - \ContextResolver\ 和 \@path\ 注入不再推进
> - 本文档中关于 docs 扩展的描述应被视为待清理而非待实现

>
> **2026-03-25 F2 Update**: Pipeline 状态管理正在实施单一真相源改造：
> - `state_json` 作为 pipeline 状态的唯一真相源
> - `PipelineStateView` 提供统一的状态读取接口
> - `update_pipeline_state()` 作为唯一状态写入入口
> - 实施详情参考 `../solution/2026-03-25-f2-test-driven-implementation-plan.md`
>
> **2026-03-29 Priority Issues Fix Update**: 基于 `../research/2026-03-28-docuswarm-priority-issues-deep-research.md` 的6个关键问题已制定测试驱动修复方案：
> - **F1 (P0)**: 交付物契约传递修复 - `NodeExecutionContext` 现在正确传递 `deliverable_requirements` 和 `deliverable_type`
> - **F2 (P0)**: BMAD 技能注入修复 - 主执行链统一使用 `PromptTemplateEngine` 注入技能
> - **F3 (P0)**: 阈值读取修复 - `CriteriaLoader` 优先读取 v2 `threshold`（单数）配置
> - **F4 (P1)**: ContextValidator 统一 - 全仓统一使用 `ContextValidator.get_instance()` 单例
> - **F5 (P1)**: 检查器语义验证增强 - `node_config_completeness_checker` 新增跨文件语义一致性检测
> - **F6 (P2)**: SessionManager 清理 - **完全移除** `allowed_dirs` 参数和属性，统一使用 `file_dirs` 和 `tool_permissions`
> - 实施详情参考 `../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md`
>
> **2026-04-06 Deep Reform Update**: 基于 `../research/docuswarm-deep-reform` 系列研究，实施重大架构改革：
> - **技能引入机制**: SDK原生discovery (`setting_sources: ["project"]`) + system prompt快速参考 + node.yaml whitelist控制
> - **Analyst任务重构**: `create-business-analysis-report` → `create-product-brief`，Persona改为"Mary"，role改为"Product Discovery Facilitator"
> - **文档创建约束**: 单文档约束(analyst/pm/ux: max_deliverables=1) + 多文档支持(architect/po)
> - **多文档参数扩展**: `CreateDeliverableParams` 新增 `document_index`, `document_total`, `document_type`
> - **F3实现缺口**: MCP Schema暴露multi-document参数，DualAgentNode支持多文档存储
> - **F4实现缺口**: `docs_context_summary`传递链修复，3处断点修复
> - **F5实现缺口**: `SummaryAgent`返回类型统一为`list[dict]`
> - **F6实现缺口**: `update_context`工具MCP暴露链路修复，新增`create_update_context_server()`
> - **F7实现缺口**: Analyst任务语义重构
> - **F8实现缺口**: 模板对齐运行时接线修复
> - 详细改革内容参考 `../research/docuswarm-deep-reform/README.md`

# DocuSwarm Project Structure

**Version**: 2.1  
**Date**: 2026-02-20  
**Status**: Approved  
**Author**: Solution Architect  

---

## 1. Overview

This document defines the directory structure, file organization patterns, and module responsibilities for the DocuSwarm project.

### 1.1 Organization Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **Feature-based** | Group by feature, not type | `agents/`, `node_execution/`, `storage/` |
| **Flat when possible** | Avoid deep nesting | Max 3 levels of directories |
| **Explicit over implicit** | Clear naming conventions | `independent.py`, `evaluator.py` |
| **Separation of concerns** | Single responsibility per module | One class per file for core components |

### 1.2 Structure Summary

```
docuswarm/
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── docuswarm.db             # SQLite database (runtime)
│
├── docuswarm/               # Main application package
├── nodes/                   # Node configurations
├── output/                  # Generated deliverables
├── tests/                   # Test suite
└── docs/                    # Documentation
```

---

## 2. Complete Directory Tree

```
docuswarm/
│
├── pyproject.toml                    # Project configuration, dependencies
├── README.md                         # Project overview and quick start
├── LICENSE                           # License file
├── .gitignore                        # Git ignore patterns
│
├── .env.example                      # Environment variable template
├── .pre-commit-config.yaml           # Pre-commit hooks
│
├── docuswarm/                        # Main application package
│   ├── __init__.py                   # Package initialization, version
│   ├── __main__.py                   # CLI entry: python -m docuswarm
│   ├── main.py                       # CLI implementation (click)
│   ├── config.py                     # Configuration loading
│   ├── exceptions.py                 # Custom exceptions
│   │
│   ├── node_execution/               # Node execution orchestration
│   │   ├── __init__.py
│   │   ├── graph.py                  # LangGraph node execution definition
│   │   ├── context_validator.py      # Context validation (LLM + rules)
│   │   ├── state.py                  # State schema definitions
│   │   └── transitions.py            # State transition logic
│   │
│   ├── agents/                       # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseAgent abstract class
│   │   ├── independent.py            # Independent Agent implementation
│   │   ├── evaluator.py              # Evaluator Agent implementation
│   │   └── persona.py                # BMAD persona loading
│   │
│   ├── nodes/                        # Node execution logic
│   │   ├── __init__.py
│   │   ├── dual_agent.py             # Dual-agent node executor
│   │   ├── loader.py                 # Node configuration loader
│   │   └── iteration.py              # Iteration control logic
│   │
│   ├── context/                      # Context management
│   │   ├── __init__.py
│   │   ├── isolation.py              # Three-layer context isolation
│   │   ├── filter.py                 # Message filtering
│   │   ├── memory.py                 # Memory management
│   │   └── audit.py                  # Isolation audit logging
│   │
│   ├── storage/                      # Persistence layer
│   │   ├── __init__.py
│   │   ├── database.py               # SQLite database connection
│   │   ├── state_manager.py          # Node run state persistence
│   │   ├── checkpoints.py            # LangGraph checkpoint integration
│   │   └── files.py                  # File storage for deliverables
│   │
│   ├── llm/                          # LLM integration
│   │   ├── __init__.py
│   │   ├── config.py                 # LLM configuration constants
│   │   ├── client.py                 # LLM client wrapper
│   │   ├── request.py                # Request formatting
│   │   ├── response.py               # Response parsing
│   │   ├── tools.py                  # Tool definitions
│   │   ├── rate_limit.py             # Rate limiter
│   │   ├── retry.py                  # Retry handler
│   │   └── optimizer.py              # Token optimization
│   │
│   └── utils/                        # Shared utilities
│       ├── __init__.py
│       ├── logging.py                # Structured logging setup
│       ├── validation.py             # JSON schema validation
│       └── formatting.py             # Output formatting
│
├── nodes/                            # Node configuration files
│   ├── analyst/
│   │   ├── node.yaml                 # Node configuration
│   │   ├── persona.json              # BMAD persona definition
│   │   └── evaluator.yaml            # Evaluation criteria
│   ├── pm/
│   │   ├── node.yaml
│   │   ├── persona.json
│   │   └── evaluator.yaml
│   ├── ux/
│   │   ├── node.yaml
│   │   ├── persona.json
│   │   └── evaluator.yaml
│   ├── architect/
│   │   ├── node.yaml
│   │   ├── persona.json
│   │   └── evaluator.yaml
│   └── po/
│       ├── node.yaml
│       ├── persona.json
│       └── evaluator.yaml
│
├── output/                           # Generated deliverables (runtime)
│   └── {node}/{run-id}/              # Per-node per-run output
│       ├── analyst-report.md
│       ├── prd.md
│       ├── ux-design.md
│       ├── architecture.md
│       └── epics-stories.md
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   │
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_agents.py
│   │   ├── test_context.py
│   │   ├── test_llm.py
│   │   ├── test_nodes.py
│   │   └── test_storage.py
│   │
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_node_execution.py
│   │   ├── test_dual_agent.py
│   │   └── test_checkpoints.py
│   │
│   └── e2e/                          # End-to-end tests
│       ├── __init__.py
│       └── test_full_node_execution.py
│
├── docs/                             # Documentation
│   ├── plan/                         # PRD and UX design
│   │   ├── PRD.md
│   │   └── UX_DESIGN.md
│   │
│   └── architecture/                 # Architecture documentation
│       ├── 01_SYSTEM_ARCHITECTURE.md
│       ├── 02_AGENT_ARCHITECTURE.md
│       ├── 03_PIPELINE_ARCHITECTURE.md
│       ├── 04_STATE_ARCHITECTURE.md
│       ├── 05_LLM_INTEGRATION.md
│       ├── 06_CONTEXT_ISOLATION.md
│       ├── coding-standards.md
│       ├── tech-stack.md
│       └── project-structure.md
│
└── scripts/                          # Utility scripts
    ├── setup_dev.py                  # Development environment setup
    ├── migrate_db.py                 # Database migrations
    └── export_docs.py                # Export deliverables
```

---

## 3. Module Responsibilities

### 3.1 Core Application (`docuswarm/`)

#### Entry Points

| File | Responsibility |
|------|----------------|
| `__init__.py` | Package metadata, version export |
| `__main__.py` | Enable `python -m docuswarm` |
| `main.py` | CLI commands (start, status, resume, export) |
| `config.py` | Load environment variables, configuration |
| `exceptions.py` | Custom exception hierarchy |

```python
# docuswarm/__init__.py
"""DocuSwarm Multi-Agent Document Orchestration System."""
__version__ = "1.0.0"

# docuswarm/__main__.py
"""CLI entry point."""
from docuswarm.main import cli

if __name__ == "__main__":
    cli()
```

### 3.2 Node Execution Module (`docuswarm/node_execution/`)

| File | Responsibility |
|------|----------------|
| `graph.py` | LangGraph StateGraph definition |
| `context_validator.py` | Context validation (LLM + rule-based) |
| `state.py` | NodeRunState and NodeState TypedDicts |
| `transitions.py` | State transition logic |

```python
# docuswarm/node_execution/state.py
from typing import TypedDict, Optional, List, Dict

class NodeRunState(TypedDict):
    """Main node run state schema."""
    run_id: str
    subject_context: dict
    current_node: Optional[str]
    completed_nodes: List[str]
    deliverables: Dict[str, dict]
    questions: Dict[str, List[dict]]
    evaluations: Dict[str, dict]
    node_iterations: Dict[str, int]
```

### 3.3 Agents Module (`docuswarm/agents/`)

| File | Responsibility |
|------|----------------|
| `base.py` | BaseAgent abstract class |
| `independent.py` | Independent Agent (creates deliverables) |
| `evaluator.py` | Evaluator Agent (reviews deliverables) |
| `persona.py` | Load BMAD persona from configuration |

```python
# docuswarm/agents/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    async def execute(self, context: dict) -> dict:
        """Execute agent logic."""
        pass
```

### 3.4 Nodes Module (`docuswarm/nodes/`)

| File | Responsibility |
|------|----------------|
| `dual_agent.py` | Coordinate Independent + Evaluator |
| `loader.py` | Load node configuration from YAML |
| `iteration.py` | Handle max iterations, escalation |

### 3.5 Context Module (`docuswarm/context/`)

| File | Responsibility |
|------|----------------|
| `isolation.py` | Three-layer context isolation |
| `filter.py` | Remove private fields from messages |
| `memory.py` | Shared vs private memory management |
| `audit.py` | Log context access for verification |

### 3.6 Storage Module (`docuswarm/storage/`)

| File | Responsibility |
|------|----------------|
| `database.py` | SQLite connection, WAL configuration |
| `state_manager.py` | Save/load node run state |
| `checkpoints.py` | LangGraph SqliteSaver integration |
| `files.py` | Write deliverables to output directory |

### 3.7 LLM Module (`docuswarm/llm/`)

| File | Responsibility |
|------|----------------|
| `session_manager.py` | SessionManager (SDK 适配层, P1-2: KimiSessionManager alias removed) |
| `mode_mapper.py` | SDKModeParams + MODE_MAP |
| `approval.py` | ApprovalRequest 处理 |
| `config.py` | SDK Config 适配 |
| `rate_limit.py` | 外层限流 (评估是否保留) |
| `service.py` | LLMService 统一服务 |

### 3.8 Utils Module (`docuswarm/utils/`)

| File | Responsibility |
|------|----------------|
| `logging.py` | Configure structlog |
| `validation.py` | JSON schema validation |
| `formatting.py` | Format output for CLI |

---

## 4. Configuration Files

### 4.1 Node Configuration (`nodes/*/node.yaml`)

```yaml
# nodes/analyst/node.yaml
node_id: analyst
name: "Analyst"
description: "Business Analyst performing market research and requirements analysis"

# Agent configuration
agent:
  persona_file: persona.json
  mode: agent
  temperature: 0.7
  max_tokens: 32768

# Deliverable configuration  
deliverable:
  type: analyst-report
  format: markdown
  required_sections:
    - executive_summary
    - market_analysis
    - requirements
    - recommendations

# Question configuration
questions:
  min_required: 3
  blocking_required: 1
  categories:
    - blocking
    - clarifying
    - optional
```

### 4.2 Evaluation Configuration (`nodes/*/evaluator.yaml`)

```yaml
# nodes/analyst/evaluator.yaml
node_id: analyst
evaluation_type: analyst_evaluation

# Criteria weights (must sum to 1.0)
criteria_weights:
  completeness: 0.30
  clarity: 0.20
  consistency: 0.20
  actionability: 0.30
  evidence_quality: 0.40

# Thresholds
thresholds:
  approval: 0.70
  escalation: 0.50

# Node-specific criteria
specific_criteria:
  - market_data_quality
  - requirement_traceability
  - risk_assessment
```

### 4.3 Persona Configuration (`nodes/*/persona.json`)

```json
{
  "name": "BMAD Analyst",
  "role": "Business Analyst",
  "expertise": [
    "Market research",
    "Requirements analysis",
    "Stakeholder interviews",
    "Competitive analysis"
  ],
  "communication_style": "Professional, analytical, evidence-based",
  "output_format": "Structured markdown with clear sections",
  "special_instructions": [
    "Always cite sources for market data",
    "Prioritize requirements by business value",
    "Identify risks early"
  ]
}
```

---

## 5. File Naming Conventions

### 5.1 Python Files

| Convention | Example | Description |
|------------|---------|-------------|
| **Modules** | `snake_case.py` | All lowercase, underscores |
| **Classes** | `PascalCase` | In code, not file names |
| **Constants** | `UPPER_SNAKE_CASE` | In code |
| **Private** | `_private.py` | Leading underscore |

### 5.2 Configuration Files

| Type | Pattern | Example |
|------|---------|---------|
| **Node config** | `node.yaml` | `nodes/analyst/node.yaml` |
| **Evaluator config** | `evaluator.yaml` | `nodes/analyst/evaluator.yaml` |
| **Persona** | `persona.json` | `nodes/analyst/persona.json` |

### 5.3 Output Files

| Type | Pattern | Example |
|------|---------|---------|
| **Deliverables** | `kebab-case.md` | `analyst-report.md` |
| **Node run output** | `{node}/{run-id}/` | `output/analyst/a3f7b2c1/` |

### 5.4 Test Files

| Type | Pattern | Example |
|------|---------|---------|
| **Unit tests** | `test_{module}.py` | `test_agents.py` |
| **Integration** | `test_{feature}.py` | `test_node_execution.py` |
| **Fixtures** | `conftest.py` | `tests/conftest.py` |

---

## 6. Import Organization

### 6.1 Import Order

```python
# 1. Standard library imports
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party imports
from kimi_agent_sdk import Session, prompt
from langgraph.graph import StateGraph
from pydantic import BaseModel
import structlog

# 3. Local application imports
from docuswarm.config import Config
from docuswarm.node_execution.state import NodeRunState
from docuswarm.agents.independent import IndependentAgent
```

### 6.2 Package Exports

```python
# docuswarm/__init__.py
"""DocuSwarm - Multi-Agent Document Orchestration System."""

from docuswarm.config import Config
from docuswarm.node_execution.graph import create_node_execution
from docuswarm.agents.independent import IndependentAgent
from docuswarm.agents.evaluator import EvaluatorAgent

__version__ = "1.0.0"
__all__ = [
    "Config",
    "create_node_execution",
    "IndependentAgent",
    "EvaluatorAgent",
]
```

---

## 7. Directory Size Guidelines

### 7.1 Recommended Limits

| Directory | Max Files | Max Lines/File | Action if Exceeded |
|-----------|-----------|----------------|-------------------|
| `docuswarm/` | 10 | 500 | Split into submodules |
| `docuswarm/*/` | 8 | 300 | Split large modules |
| `tests/unit/` | 15 | 400 | Group by feature |
| `nodes/*/` | 3 | - | Fixed structure |

### 7.2 When to Create Submodules

Create a submodule when:
- A file exceeds 500 lines
- More than 5 closely related files exist
- A clear single responsibility can be extracted

```
# Before: docuswarm/storage.py (800 lines)
# After: docuswarm/storage/
#        ├── __init__.py
#        ├── database.py
#        ├── state_manager.py
#        └── files.py
```

---

## 8. Output Directory Structure

### 8.1 Runtime Output

```
output/
├── {node}/{run-id}/              # Per-node per-run
│   ├── analyst-report.md         # Analyst deliverable
│   ├── prd.md                    # PM deliverable
│   ├── ux-design.md              # UX deliverable
│   ├── architecture.md           # Architect deliverable
│   ├── epics-stories.md          # PO deliverable
│   └── _metadata.json            # Run metadata
│
└── .gitkeep                      # Keep directory in git
```

### 8.2 Metadata File

```json
{
  "run_id": "abc123xyz",
  "node_id": "analyst",
  "created_at": "2026-02-20T10:00:00Z",
  "completed_at": "2026-02-20T10:12:00Z",
  "status": "completed",
  "total_iterations": 2,
  "final_score": 0.85
}
```

---

## 9. Git Configuration

### 9.1 `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
venv/
*.egg-info/
dist/
build/

# Environment
.env
.env.local

# Database
*.db
*.db-journal
*.db-wal
*.db-shm

# Output
output/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Type checking
.basedpyright/
.mypy_cache/

# OS
.DS_Store
Thumbs.db
```

### 9.2 `.gitkeep` Files

Keep empty directories in git:
```
nodes/analyst/.gitkeep
output/.gitkeep
```

---

## 10. Development vs Production

### 10.1 Development Structure

```
docuswarm/                        # Repository root
├── .env                          # Local environment (not in git)
├── .pre-commit-config.yaml       # Pre-commit hooks
├── pyproject.toml                # Project config
│
├── docuswarm/                    # Source code
├── tests/                        # Tests
├── docs/                         # Documentation
│
└── docuswarm.db                  # Local database (not in git)
```

### 10.2 Production Deployment

```
/opt/docuswarm/                   # Installation directory
├── docuswarm/                    # Package (pip installed)
├── nodes/                        # Node configurations
├── output/                       # Generated output
├── docuswarm.db                  # SQLite database
└── docuswarm.log                 # Log file
```

---

## 11. Creating New Modules

### 11.1 Adding a New Agent Type

1. Create agent file:
```python
# docuswarm/agents/questioner.py
from docuswarm.agents.base import BaseAgent

class QuestionerAgent(BaseAgent):
    """Agent for generating clarifying questions."""
    
    async def execute(self, context: dict) -> dict:
        # Implementation
        pass
```

2. Export from package:
```python
# docuswarm/agents/__init__.py
from docuswarm.agents.base import BaseAgent
from docuswarm.agents.independent import IndependentAgent
from docuswarm.agents.evaluator import EvaluatorAgent
from docuswarm.agents.questioner import QuestionerAgent  # New

__all__ = ["BaseAgent", "IndependentAgent", "EvaluatorAgent", "QuestionerAgent"]
```

3. Add tests:
```python
# tests/unit/test_agents.py
class TestQuestionerAgent:
    async def test_execute(self):
        # Test implementation
        pass
```

### 11.2 Adding a New Node Type

1. Create node configuration:
```
nodes/
└── new_node/
    ├── node.yaml
    ├── persona.json
    └── evaluator.yaml
```

2. Register in node execution graph:
```python
# docuswarm/node_execution/graph.py
def create_node_execution_graph() -> StateGraph:
    graph = StateGraph(NodeRunState)
    
    # Add new node
    graph.add_node("new_node", create_node("new_node"))
    
    # Update edges
    graph.add_edge("previous_node", "new_node")
    graph.add_edge("new_node", "next_node")
    
    return graph
```

---

## 12. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| Coding Standards | `coding-standards.md` |
| Tech Stack | `tech-stack.md` |

### External References

- [Python Packaging Guide](https://packaging.python.org/)
- [LangGraph Project Structure](https://langchain-ai.github.io/langgraph/)
- [src Layout vs Flat Layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

---

**Document End**
> **2026-03-13 Alignment Notice**: 当前项目结构文档中涉及 `ContextResolver`、纯函数工具迁移和部分节点配置新 schema 的内容，与代码现实存在偏差。目录阅读应结合 `README.md` 与 `../research/2026-03-13-context-injection-audit.md`。

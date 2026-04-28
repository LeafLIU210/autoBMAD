# Epic 1: Core Infrastructure

**Epic ID**: EPIC-01  
**Version**: 1.0  
**Date**: 2026-02-19  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2 Weeks (Week 1-2)

---

## 1. Epic Overview

### 1.1 Summary

Build the foundational infrastructure for DocuSwarm including the project structure, LangGraph integration, SQLite persistence layer, configuration management, and CLI interface. This epic establishes the technical foundation upon which all other epics depend.

### 1.2 Business Value

- **Foundation First**: Enables parallel development of agents and node execution
- **Proven Stack**: Uses battle-tested technologies (LangGraph, SQLite)
- **Developer Experience**: Clean project structure and CLI interface
- **Time Savings**: LangGraph saves 8-12 weeks vs custom implementation

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Project bootstrapped | `python -m docuswarm --help` works |
| Database operational | WAL mode active, tables created |
| Configuration loaded | Environment variables parsed |
| CLI functional | All commands execute without error |

### 1.4 Dependencies

- **Prerequisites**: Python 3.14+ installed
- **Blocks**: All other epics depend on this infrastructure

---

## 2. Architecture Context

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Core Infrastructure (Epic 1)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Configuration Layer                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  config.py      │  exceptions.py    │  .env loading                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Persistence Layer                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  SQLite WAL Mode │  State Manager    │  File Storage                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  CLI Layer                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Click Commands  │  Rich Output      │  Progress Display             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  LangGraph Foundation                                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  StateGraph      │  SqliteSaver      │  Thread Config                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project configuration, dependencies |
| `docuswarm/__init__.py` | Package initialization |
| `docuswarm/__main__.py` | CLI entry point |
| `docuswarm/main.py` | CLI commands |
| `docuswarm/config.py` | Configuration loading (see [P1-2 Config Semantics](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md)) |
| `docuswarm/exceptions.py` | Custom exception hierarchy |
| `docuswarm/storage/database.py` | SQLite connection |
| `docuswarm/storage/state_manager.py` | State persistence |
| `docuswarm/storage/files.py` | File output |

---

## 3. User Stories

### Story 1.1: Project Structure Setup

**ID**: US-1.1  
**As a** developer  
**I want to** have a clean, well-organized project structure  
**So that** I can easily navigate and extend the codebase

**Acceptance Criteria**:
- [ ] Project follows Python packaging best practices
- [ ] `pyproject.toml` contains all dependencies
- [ ] `__init__.py` exports version and key classes
- [ ] `__main__.py` enables `python -m docuswarm`
- [ ] `.gitignore` excludes appropriate files

**Technical Tasks**:
1. Create project directory structure per `project-structure.md`
2. Write `pyproject.toml` with dependencies from `tech-stack.md`
3. Create package `__init__.py` with version export
4. Create `__main__.py` entry point
5. Add `.gitignore` with Python, IDE, and database patterns

**Definition of Done**:
- `pip install -e .` succeeds
- `python -m docuswarm` executes (even if only shows help)
- All imports resolve without errors

---

### Story 1.2: Configuration Management

**ID**: US-1.2  
**As a** developer  
**I want to** load configuration from environment variables and YAML  
**So that** I can configure the system without code changes

**Acceptance Criteria**:
- [ ] Environment variables loaded from `.env`
- [ ] `KIMI_API_KEY` required and validated
- [ ] Optional config from `config/docuswarm.yaml`
- [ ] Config class with type hints
- [ ] Sensible defaults for all settings

**Technical Tasks**:
1. Create `config.py` with `Config` dataclass
2. Implement `.env` loading with `python-dotenv`
3. Add YAML config loading with `pyyaml`
4. Validate required settings (API key)
5. Create `.env.example` template

**Configuration Schema**:
```python
@dataclass
class Config:
    # Required
    kimi_api_key: str
    
    # Persistence
    db_path: str = "docuswarm.db"
    output_dir: str = "output"
    
    # Node Execution
    max_iterations: int = 3
    approval_threshold: float = 0.70
    escalation_threshold: float = 0.50
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "docuswarm.log"
```

**Definition of Done**:
- Config loads without `.env` file (fails gracefully with message)
- Config loads with `.env` file (succeeds)
- All settings accessible as typed attributes
- Missing API key raises clear error

---

### Story 1.3: Exception Hierarchy

**ID**: US-1.3  
**As a** developer  
**I want to** have a clear exception hierarchy  
**So that** I can handle errors appropriately throughout the system

**Acceptance Criteria**:
- [ ] Base `DocuSwarmError` for all custom exceptions
- [ ] Specific exceptions for config, storage, LLM, node execution errors
- [ ] Exceptions include context information
- [ ] Documented exception types

**Technical Tasks**:
1. Create `exceptions.py` with hierarchy
2. Define context-carrying exception classes
3. Add exception docstrings

**Exception Hierarchy**:
```python
class DocuSwarmError(Exception):
    """Base exception for DocuSwarm."""
    pass

class ConfigurationError(DocuSwarmError):
    """Configuration-related errors."""
    pass

class StorageError(DocuSwarmError):
    """Database and file storage errors."""
    pass

class LLMError(DocuSwarmError):
    """LLM API-related errors."""
    pass

class NodeExecutionError(DocuSwarmError):
    """Node execution errors."""
    pass

class ContextIsolationError(DocuSwarmError):
    """Context isolation violations."""
    pass
```

**Definition of Done**:
- All exceptions importable from package
- Each exception type has clear use case
- Tests verify exception hierarchy

---

### Story 1.4: SQLite Database Setup

**ID**: US-1.4  
**As a** developer  
**I want to** have a properly configured SQLite database  
**So that** I can persist node run state reliably

**Acceptance Criteria**:
- [ ] WAL mode enabled for concurrent reads
- [ ] Foreign keys enforced
- [ ] Busy timeout configured (5000ms)
- [ ] Tables created on first run
- [ ] Connection pooling for efficiency

**Technical Tasks**:
1. Create `storage/database.py` with connection management
2. Implement WAL mode configuration
3. Create schema initialization
4. Add connection context manager

**Database Configuration**:
```sql
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;
```

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS node_runs (
    run_id TEXT PRIMARY KEY,           -- 8-char short UUID
    node_id TEXT NOT NULL,             -- analyst / pm / ux / architect / po
    context_hash TEXT NOT NULL,        -- context file hash for chaining
    context_file TEXT,                 -- original context file path
    status TEXT NOT NULL DEFAULT 'pending',
    iteration INTEGER NOT NULL DEFAULT 0,
    deliverable TEXT,                  -- JSON
    questions TEXT,                    -- JSON array
    evaluation TEXT,                   -- JSON
    answers TEXT,                      -- JSON (user answers)
    chained_context TEXT,              -- JSON (auto-injected predecessor deliverables)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'blocked')),
    CHECK (node_id IN ('analyst', 'pm', 'ux', 'architect', 'po'))
);

CREATE INDEX idx_node_runs_node ON node_runs(node_id, created_at DESC);
CREATE INDEX idx_node_runs_context ON node_runs(context_hash, node_id);
CREATE INDEX idx_node_runs_status ON node_runs(status);
```

**Definition of Done**:
- Database file created on first access
- WAL mode verified with PRAGMA query
- Tables created successfully
- Foreign key constraint works

---

### Story 1.5: State Manager Implementation

**ID**: US-1.5  
**As a** developer  
**I want to** save and retrieve node run state  
**So that** node runs can be recovered after interruption

**Acceptance Criteria**:
- [ ] Create new node run with unique run_id
- [ ] Update run status and iteration
- [ ] Save node results (deliverable, questions, evaluation)
- [ ] Query runs by node and context_hash
- [ ] Retrieve complete node run state

**Technical Tasks**:
1. Create `storage/state_manager.py`
2. Implement CRUD operations for node runs
3. Implement node result storage
4. Add transaction support
5. Write unit tests

**API Design**:
```python
class StateManager:
    async def create_node_run(self, node_id: str, context_hash: str, context_file: str) -> str:
        """Create new node run, return run_id."""
        
    async def update_node_run_status(
        self, run_id: str, status: str
    ) -> None:
        """Update node run status."""
        
    async def save_node_result(
        self, run_id: str, iteration: int, result: NodeResult
    ) -> None:
        """Save node execution result."""
        
    async def get_node_run(self, run_id: str) -> NodeRun:
        """Retrieve node run with all results."""
        
    async def list_node_runs(self, node_id: str = None, status: str = None) -> List[NodeRun]:
        """List node runs, optionally filtered by node_id and status."""
        
    async def get_chained_deliverables(self, node_id: str, context_hash: str) -> dict:
        """Get predecessor node deliverables for context chaining."""
```

**Acceptance Criteria**:
- [ ] All CRUD operations tested
- [ ] Transactions rollback on error
- [ ] JSON serialization works for complex types
- [ ] Node run state fully recoverable
- [ ] Context chaining logic correctly retrieves predecessor deliverables

---

### Story 1.6: File Storage for Deliverables

**ID**: US-1.6  
**As a** developer  
**I want to** save deliverables to markdown files  
**So that** outputs are accessible and version-controllable

**Acceptance Criteria**:
- [ ] Create node run output directory
- [ ] Save deliverable as named markdown file
- [ ] Generate metadata JSON
- [ ] Support file export command

**Technical Tasks**:
1. Create `storage/files.py`
2. Implement directory creation
3. Implement markdown file writing
4. Add metadata generation

**Output Structure**:
```
output/
└── {node}/
    └── {run-id}/
        ├── deliverable.md
        ├── evaluation.json
        └── questions.json
```

**Definition of Done**:
- Directories created automatically
- Files written with correct encoding (UTF-8)
- Metadata includes timestamps and scores
- Files readable by standard markdown viewers

---

### Story 1.7: CLI Implementation

**ID**: US-1.7  
**As a** user  
**I want to** interact with DocuSwarm via command line  
**So that** I can start, monitor, and manage node runs

**Acceptance Criteria**:
- [ ] `docuswarm init` initializes project configuration
- [ ] `docuswarm nodes` lists available nodes
- [ ] `docuswarm start <node> --context <file>` starts node execution
- [ ] `docuswarm runs <node>` shows node run history
- [ ] `docuswarm status <node>` shows node status
- [ ] `docuswarm export <node>` exports node deliverables
- [ ] `docuswarm questions <node>` shows node questions
- [ ] `docuswarm answer <question-id> <answer>` answers questions
- [ ] Rich output with colors and progress bars

**Technical Tasks**:
1. Create `main.py` with Click commands
2. Implement `init` command
3. Implement `nodes` command
4. Implement `start` command
5. Implement `runs` command
6. Implement `status` command
7. Implement `export` command
8. Implement `questions` command
9. Implement `answer` command
10. Add Rich formatting

**CLI Commands**:
```bash
# Initialize project
docuswarm init

# List available nodes
docuswarm nodes

# Start node execution
docuswarm start <node> --context project.md [--no-chain]

# View node run history
docuswarm runs <node>

# Check node status
docuswarm status <node> [--run <run-id>]

# Export node deliverables
docuswarm export <node> [--run <run-id>] [--output ./docs]

# View node questions
docuswarm questions <node> [--run <run-id>]

# Answer a question
docuswarm answer <question-id> "<answer>"
```

**Definition of Done**:
- All commands execute without error
- Help text available for all commands
- Progress displayed during execution
- Errors displayed clearly

---

### Story 1.8: LangGraph Foundation Setup

**ID**: US-1.8  
**As a** developer  
**I want to** have LangGraph properly configured  
**So that** node execution orchestration works correctly

**Acceptance Criteria**:
- [ ] LangGraph StateGraph can be created
- [ ] SqliteSaver integrated for checkpointing
- [ ] Thread configuration for isolation
- [ ] State schema defined

**Technical Tasks**:
1. Create `node_execution/state.py` with state schemas
2. Create `storage/checkpoints.py` with SqliteSaver setup
3. Verify LangGraph imports and basic operations
4. Write integration test for checkpoint/resume

**State Schema**:
```python
from typing import TypedDict, Optional, List, Dict

class NodeRunState(TypedDict):
    run_id: str
    node_id: str
    context_hash: str
    context_file: str
    iteration: int
    deliverable: Optional[dict]
    questions: List[dict]
    evaluation: Optional[dict]
    answers: Dict[str, str]
    chained_context: Dict[str, dict]  # Predecessor deliverables
```

**Definition of Done**:
- LangGraph StateGraph can be instantiated
- State can be saved and restored via SqliteSaver
- Thread isolation verified
- State schema validated

---

### Story 1.9: Logging Infrastructure

**ID**: US-1.9  
**As a** developer  
**I want to** have structured logging throughout the system  
**So that** I can debug issues and monitor node execution

**Acceptance Criteria**:
- [ ] Structured logging with structlog
- [ ] Console output for INFO and above
- [ ] File output for DEBUG and above
- [ ] Node and run_id context in all logs
- [ ] JSON format option for tooling

**Technical Tasks**:
1. Create `utils/logging.py`
2. Configure structlog processors
3. Add context binding for node/run_id
4. Integrate with CLI

**Log Format**:
```
2026-02-19T10:00:00 [INFO] run_id=a3f7b2c1 node_id=analyst message="Node execution started"
```

**Acceptance Criteria**:
- [ ] Logs appear in console and file
- [ ] Context (run_id, node_id) included
- [ ] Log level configurable via environment
- [ ] No sensitive data in logs

---

## 4. Technical Specifications

### 4.1 Dependencies

```toml
[project.dependencies]
langgraph = ">=0.2.0"
langchain-core = ">=0.2.0"
langchain-openai = ">=0.1.0"
pydantic = ">=2.0.0"
click = ">=8.1.0"
rich = ">=13.0.0"
python-dotenv = ">=1.0.0"
pyyaml = ">=6.0.0"
structlog = ">=24.0.0"
aiofiles = ">=23.0.0"
```

### 4.2 Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "basedpyright>=1.10.0",
    "ruff>=0.3.0",
    "black>=24.0.0",
]
```

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Tests | `pytest tests/unit/` | 100% pass |
| Coverage | `pytest --cov=docuswarm` | ≥80% |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LangGraph version incompatibility | Low | High | Pin to 0.2.x, test before upgrade |
| SQLite concurrency issues | Low | Medium | WAL mode, proper locking |
| Configuration complexity | Medium | Low | Clear documentation, defaults |

---

## 6. Definition of Done (Epic Level)

- [ ] All 9 stories completed and tested
- [ ] `python -m docuswarm --help` works
- [ ] `python -m docuswarm init` initializes project
- [ ] `python -m docuswarm start <node> --context test.md` executes node
- [ ] Database created with WAL mode and `node_runs` table
- [ ] Configuration loaded from environment
- [ ] Unit test coverage ≥80%
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Documentation in docstrings

---

## 7. References

| Document | Location |
|----------|----------|
| System Architecture | `docs/architecture/01_SYSTEM_ARCHITECTURE.md` |
| Tech Stack | `docs/architecture/tech-stack.md` |
| Project Structure | `docs/architecture/project-structure.md` |
| Coding Standards | `docs/architecture/coding-standards.md` |

---

**Epic End**

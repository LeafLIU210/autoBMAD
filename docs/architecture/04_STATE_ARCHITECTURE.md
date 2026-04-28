# DocuSwarm State Management Architecture

**Version**: 2.1  
**Date**: 2026-02-20  
**Status**: Approved  
**Author**: Solution Architect  

> **Note**: 本文档描述的状态管理架构不受 BMM NodeExecutor 重构影响。配置加载和 Persona 重构 (TDD-BMM-01, TDD-BMM-02) 不改变状态管理接口。  

---

## 1. Overview

This document details the state management architecture using SQLite with WAL mode for persistence and LangGraph checkpointing for node run recovery.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **ACID Compliance** | SQLite transactions ensure data integrity |
| **WAL Mode** | Concurrent reads during writes |
| **Single Source** | SQLite for all persistence needs |
| **Native Checkpointing** | LangGraph SqliteSaver integration |
| **State JSON Single Source** | `state_json` as single source of truth (F2) |

### 1.2 Storage Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Node Runs** | SQLite | Per-node execution results and metadata |
| **Subject Context** | SQLite | Cached context, keyed by context_hash |
| **Checkpoints** | SQLite (LangGraph) | Node run recovery points |
| **Pipeline State** | SQLite (state_json) | Pipeline-level state (single source of truth) |

---

## 2. Database Architecture

### 2.1 Schema Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Database Schema                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        node_runs                                      │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ run_id (PK)           TEXT                                           │   │
│  │ node                  TEXT NOT NULL                                   │   │
│  │ context_hash          TEXT NOT NULL                                   │   │
│  │ context_file          TEXT NOT NULL                                   │   │
│  │ iteration             INTEGER NOT NULL DEFAULT 0                      │   │
│  │ status                TEXT NOT NULL DEFAULT 'pending'                 │   │
│  │                       CHECK (status IN ('pending','running',          │   │
│  │                             'completed','failed','blocked'))          │   │
│  │ deliverable           TEXT  -- JSON                                   │   │
│  │ questions             TEXT  -- JSON array                             │   │
│  │ evaluation            TEXT  -- JSON                                   │   │
│  │ answers               TEXT  -- JSON                                   │   │
│  │ created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP             │   │
│  │ updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP             │   │
│  └────────────┬─────────────────────────────────────────────────────────┘   │
│               │                                                               │
│               │ indexed by (node, context_hash)                               │
│               │                                                               │
│  ┌────────────▼─────────────────────────────────────────────────────────┐   │
│  │                     subject_context                                   │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ context_hash (PK)     TEXT                                           │   │
│  │ context_data          TEXT NOT NULL  -- JSON                         │   │
│  │ updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                   checkpoints (LangGraph Managed)                     │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ • Automatically managed by LangGraph SqliteSaver                     │   │
│  │ • Thread-based isolation (thread_id = run_id)                        │   │
│  │ • Contains node run state at each checkpoint                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Indexes:                                                                   │
│  • idx_node_runs_node_hash ON node_runs(node, context_hash)                │
│  • idx_node_runs_status ON node_runs(status)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Table Definitions

```sql
-- node_runs: Per-node execution results
CREATE TABLE node_runs (
    run_id       TEXT PRIMARY KEY,
    node         TEXT NOT NULL,
    context_hash TEXT NOT NULL,
    context_file TEXT NOT NULL,
    iteration    INTEGER NOT NULL DEFAULT 0,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','running','completed','failed','blocked')),
    deliverable  TEXT,          -- JSON
    questions    TEXT,          -- JSON array
    evaluation   TEXT,          -- JSON
    answers      TEXT,          -- JSON
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- subject_context: Cached parsed context data
CREATE TABLE subject_context (
    context_hash TEXT PRIMARY KEY,
    context_data TEXT NOT NULL,  -- JSON
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_node_runs_node_hash ON node_runs(node, context_hash);
CREATE INDEX idx_node_runs_status ON node_runs(status);
```

---

## 3. SQLite Configuration

### 3.1 WAL Mode

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WAL Mode Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional (Rollback Journal)           WAL Mode                          │
│  ┌─────────────────────────────┐         ┌─────────────────────────────┐   │
│  │                             │         │                             │   │
│  │  Write blocks all readers   │         │  Write does not block reads│   │
│  │                             │         │                             │   │
│  │  ┌─────┐                    │         │  ┌─────┐   ┌─────┐         │   │
│  │  │Write│ ──X──▶ │Read│      │         │  │Write│   │Read │  ✓      │   │
│  │  └─────┘        │Read│      │         │  └─────┘   │Read │         │   │
│  │                 │Read│      │         │     ↓      │Read │         │   │
│  │                             │         │  ┌─────┐   └─────┘         │   │
│  │                             │         │  │ WAL │                   │   │
│  │                             │         │  │File │                   │   │
│  │                             │         │  └─────┘                   │   │
│  └─────────────────────────────┘         └─────────────────────────────┘   │
│                                                                             │
│  WAL Benefits:                                                              │
│  • Concurrent reads during writes                                          │
│  • Better write performance                                                 │
│  • Crash recovery (WAL file contains uncommitted writes)                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Connection Configuration

```python
import sqlite3
from pathlib import Path

class DatabaseConfig:
    """SQLite database configuration."""
    
    # PRAGMA settings
    PRAGMAS = {
        "journal_mode": "WAL",        # Write-Ahead Logging
        "busy_timeout": 5000,         # 5 second timeout
        "foreign_keys": "ON",         # Enforce foreign keys
        "synchronous": "NORMAL",      # Balance durability/performance
        "cache_size": -64000,         # 64MB cache
    }
    
    @classmethod
    def create_connection(cls, db_path: str) -> sqlite3.Connection:
        """Create configured SQLite connection."""
        conn = sqlite3.connect(
            db_path,
            check_same_thread=False,  # Allow multi-thread access
            isolation_level=None      # Autocommit mode for explicit transactions
        )
        
        # Apply PRAGMA settings
        for pragma, value in cls.PRAGMAS.items():
            conn.execute(f"PRAGMA {pragma}={value}")
        
        # Row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        return conn
```

---

## 4. State Manager

### 4.1 Class Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        StateManager Class                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  class StateManager:                                                   │ │
│  │      """Manages all DocuSwarm state persistence."""                   │ │
│  │                                                                        │ │
│  │      Attributes:                                                       │ │
│  │      ├── conn: sqlite3.Connection                                     │ │
│  │      └── db_path: str                                                 │ │
│  │                                                                        │ │
│  │      Node Run Methods:                                                 │ │
│  │      ├── create_node_run(run_id, node, context_hash, context_file)   │ │
│  │      ├── get_node_run(run_id) -> dict                                │ │
│  │      ├── update_run_status(run_id, status, iteration)                │ │
│  │      ├── get_latest_run(node, context_hash) -> dict                  │ │
│  │      ├── list_runs(node, context_hash) -> List[dict]                 │ │
│  │      ├── update_node_run(run_id, deliverable, questions, evaluation) │ │
│  │      ├── get_all_runs(context_hash) -> Dict[str, dict]               │ │
│  │      └── get_completed_nodes(context_hash) -> List[str]              │ │
│  │                                                                        │ │
│  │      Subject Context Methods:                                          │ │
│  │      ├── load_context(context_hash) -> dict                          │ │
│  │      ├── save_context(context_hash, context)                         │ │
│  │      └── update_context(context_hash, key, value, operation)         │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Implementation

```python
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class StateManager:
    """SQLite-based state manager for DocuSwarm.
    
    **P0-3 Sync Contract**: StateManager provides SYNCHRONOUS storage operations.
    All public methods are regular `def` (not `async def`) because the underlying
    storage is SQLite (`sqlite3`). Callers in async contexts must use 
    `asyncio.to_thread()` or an explicit executor if they need non-blocking I/O.
    
    This is an architectural constraint enforced by `test_p0_3_async_sync_contract.py`.
    See: ../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md
    """
    
    def __init__(self, db_path: str = "docuswarm.db"):
        self.db_path = db_path
        self.conn = DatabaseConfig.create_connection(db_path)
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize database schema."""
        with open("schema.sql") as f:
            self.conn.executescript(f.read())
    
    # === Node Run Operations ===
    
    def create_node_run(
        self, 
        run_id: str, 
        node: str, 
        context_hash: str, 
        context_file: str
    ) -> str:
        """Create a new node run."""
        with self.conn:
            self.conn.execute(
                """INSERT INTO node_runs (run_id, node, context_hash, context_file, status)
                   VALUES (?, ?, ?, ?, 'pending')""",
                (run_id, node, context_hash, context_file)
            )
        return run_id
    
    def get_node_run(self, run_id: str) -> Optional[dict]:
        """Get node run by run_id."""
        cursor = self.conn.execute(
            "SELECT * FROM node_runs WHERE run_id = ?",
            (run_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "run_id": row["run_id"],
            "node": row["node"],
            "context_hash": row["context_hash"],
            "context_file": row["context_file"],
            "iteration": row["iteration"],
            "status": row["status"],
            "deliverable": json.loads(row["deliverable"]) if row["deliverable"] else None,
            "questions": json.loads(row["questions"]) if row["questions"] else [],
            "evaluation": json.loads(row["evaluation"]) if row["evaluation"] else None,
            "answers": json.loads(row["answers"]) if row["answers"] else None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    def update_run_status(
        self, 
        run_id: str, 
        status: str, 
        iteration: int = None
    ):
        """Update node run status."""
        if iteration is not None:
            self.conn.execute(
                """UPDATE node_runs 
                   SET status = ?, iteration = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE run_id = ?""",
                (status, iteration, run_id)
            )
        else:
            self.conn.execute(
                """UPDATE node_runs 
                   SET status = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE run_id = ?""",
                (status, run_id)
            )
        self.conn.commit()
    
    def get_latest_run(self, node: str, context_hash: str) -> Optional[dict]:
        """Get latest run for a node with specific context."""
        cursor = self.conn.execute(
            """SELECT * FROM node_runs 
               WHERE node = ? AND context_hash = ?
               ORDER BY created_at DESC LIMIT 1""",
            (node, context_hash)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "run_id": row["run_id"],
            "node": row["node"],
            "context_hash": row["context_hash"],
            "iteration": row["iteration"],
            "status": row["status"],
            "deliverable": json.loads(row["deliverable"]) if row["deliverable"] else None,
            "questions": json.loads(row["questions"]) if row["questions"] else [],
            "evaluation": json.loads(row["evaluation"]) if row["evaluation"] else None,
            "created_at": row["created_at"]
        }
    
    def list_runs(self, node: str, context_hash: str) -> List[dict]:
        """List all runs for a node with specific context."""
        cursor = self.conn.execute(
            """SELECT * FROM node_runs 
               WHERE node = ? AND context_hash = ?
               ORDER BY created_at DESC""",
            (node, context_hash)
        )
        
        return [dict(row) for row in cursor]
    
    def update_node_run(
        self,
        run_id: str,
        deliverable: dict = None,
        questions: List[dict] = None,
        evaluation: dict = None,
        answers: dict = None,
        status: str = None
    ):
        """Update node run result fields."""
        updates = []
        values = []
        
        if deliverable is not None:
            updates.append("deliverable = ?")
            values.append(json.dumps(deliverable, ensure_ascii=False))
        if questions is not None:
            updates.append("questions = ?")
            values.append(json.dumps(questions, ensure_ascii=False))
        if evaluation is not None:
            updates.append("evaluation = ?")
            values.append(json.dumps(evaluation, ensure_ascii=False))
        if answers is not None:
            updates.append("answers = ?")
            values.append(json.dumps(answers, ensure_ascii=False))
        if status is not None:
            updates.append("status = ?")
            values.append(status)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(run_id)
            
            self.conn.execute(
                f"UPDATE node_runs SET {', '.join(updates)} WHERE run_id = ?",
                values
            )
            self.conn.commit()
    
    def get_all_runs(self, context_hash: str) -> Dict[str, dict]:
        """Get latest run for each node with specific context."""
        cursor = self.conn.execute(
            """SELECT node, MAX(created_at) as latest, run_id, iteration, 
                      deliverable, questions, evaluation, status
               FROM node_runs
               WHERE context_hash = ?
               GROUP BY node""",
            (context_hash,)
        )
        
        results = {}
        for row in cursor:
            results[row["node"]] = {
                "run_id": row["run_id"],
                "iteration": row["iteration"],
                "deliverable": json.loads(row["deliverable"]) if row["deliverable"] else None,
                "questions": json.loads(row["questions"]) if row["questions"] else [],
                "evaluation": json.loads(row["evaluation"]) if row["evaluation"] else None,
                "status": row["status"]
            }
        
        return results
    
    def get_completed_nodes(self, context_hash: str) -> List[str]:
        """Get list of completed nodes for specific context."""
        cursor = self.conn.execute(
            """SELECT DISTINCT node FROM node_runs 
               WHERE context_hash = ? AND status = 'completed'""",
            (context_hash,)
        )
        return [row["node"] for row in cursor]
    
    # === Subject Context Operations ===
    
    def load_context(self, context_hash: str) -> dict:
        """Load subject context by hash."""
        cursor = self.conn.execute(
            "SELECT context_data FROM subject_context WHERE context_hash = ?",
            (context_hash,)
        )
        row = cursor.fetchone()
        return json.loads(row["context_data"]) if row else {}
    
    def save_context(self, context_hash: str, context: dict):
        """Save subject context."""
        self.conn.execute(
            """INSERT OR REPLACE INTO subject_context (context_hash, context_data, updated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)""",
            (context_hash, json.dumps(context, ensure_ascii=False))
        )
        self.conn.commit()
    
    def update_context(
        self, 
        context_hash: str, 
        key: str, 
        value: Any, 
        operation: str = "set"
    ):
        """Update specific key in subject context."""
        context = self.load_context(context_hash)
        
        if operation == "set":
            context[key] = value
        elif operation == "append":
            if key not in context:
                context[key] = []
            context[key].append(value)
        elif operation == "remove":
            context.pop(key, None)
        
        self.save_context(context_hash, context)
```

---

## 4.5 Pipeline State Consistency (F2)

> **Reference**: [F2 Test-Driven Implementation Plan](../solution/2026-03-25-f2-test-driven-implementation-plan.md)

### 4.5.1 Problem Statement

The system previously had a **dual-source state problem** where `current_node` and other state fields existed in both:
- **Top-level columns** (`pipelines.current_node`, `pipelines.status`)
- **state_json internal fields** (`state_json.current_node`, `state_json.status`)

This created inconsistency risks where different code paths used different data sources.

### 4.5.2 Solution: Single Source of Truth

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    F2 Single Source of Truth Architecture                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     StateManager (Unified API)                       │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐        ┌─────────────────────────────────────┐ │   │
│  │  │  Write Path     │        │  Read Path                          │ │   │
│  │  │                 │        │                                     │ │   │
│  │  │ update_pipeline_│───────▶│ ┌─────────────────┐    ┌──────────┐ │ │   │
│  │  │ state()         │        │ │ PipelineStateView│   │Direct    │ │ │   │
│  │  │ (single entry)  │        │ │                 │    │Access    │ │ │   │
│  │  └─────────────────┘        │ │ • current_node  │    │          │ │ │   │
│  │           │                 │ │ • status        │◀───│ pipeline │ │ │   │
│  │           ▼                 │ │ • completed_    │    │["state"]  │ │ │   │
│  │  ┌─────────────────┐        │ │   nodes         │    │          │ │ │   │
│  │  │ state_json      │        │ │ • deliverables  │    │          │ │ │   │
│  │  │ (single source) │◀───────│ │ • ...           │    │          │ │ │   │
│  │  │                 │        │ └─────────────────┘    └──────────┘ │ │   │
│  │  │ All state data  │        └─────────────────────────────────────┘ │   │
│  │  │ in one JSON     │                                                │   │
│  │  │ column          │                                                │   │
│  │  └─────────────────┘                                                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Key Principles:                                                            │
│  1. All writes go through update_pipeline_state()                          │
│  2. All reads use PipelineStateView or pipeline["state"]                   │
│  3. No direct access to top-level current_node column                      │
│  4. Runtime consistency checks detect mismatches                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5.3 PipelineStateView

```python
# storage/state_access.py

class PipelineStateView:
    """Pipeline state view - unified read interface for state_json.
    
    Encapsulates all state reading logic to ensure single source access.
    All state fields are read from state_json, never from top-level columns.
    
    Example:
        >>> pipeline = state_manager.get_pipeline(pipeline_id)
        >>> view = PipelineStateView(pipeline)
        >>> print(view.current_node)  # Read from state_json
        >>> print(view.status)        # Read from state_json
    """
    
    def __init__(self, pipeline_data: dict[str, Any]) -> None:
        self._data = pipeline_data
        self._state = pipeline_data.get("state", {}) if isinstance(
            pipeline_data.get("state"), dict
        ) else {}
    
    @property
    def pipeline_id(self) -> str:
        return self._data.get("pipeline_id", "")
    
    @property
    def subject(self) -> str:
        return self._data.get("subject", "")
    
    @property
    def status(self) -> str:
        """Pipeline status (read from state_json)"""
        return self._state.get("status", "unknown")
    
    @property
    def current_node(self) -> str | None:
        """Current node (read from state_json)"""
        return self._state.get("current_node")
    
    @property
    def completed_nodes(self) -> list[str]:
        """Completed nodes list"""
        return self._state.get("completed_nodes", [])
    
    @property
    def is_running(self) -> bool:
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        return self.status == "completed"
    
    def is_node_completed(self, node_id: str) -> bool:
        """Check if node is completed."""
        return node_id in self.completed_nodes
    
    def get_node_deliverable(self, node_id: str) -> dict[str, Any] | None:
        """Get node deliverable."""
        deliverables = self._state.get("deliverables", {})
        return deliverables.get(node_id)
    
    def get_node_iterations(self, node_id: str) -> int:
        """Get node iteration count."""
        iterations = self._state.get("node_iterations", {})
        return iterations.get(node_id, 0)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (for serialization)."""
        return {
            "pipeline_id": self.pipeline_id,
            "subject": self.subject,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": self.completed_nodes,
            "is_running": self.is_running,
            "is_completed": self.is_completed,
        }
```

### 4.5.4 StateManager API (F2 Updated)

```python
# storage/state_manager.py

class StateManager:
    """StateManager - F2 Single Source of Truth Implementation."""
    
    # ==================== Core State Operations ====================
    
    def update_pipeline_state(
        self,
        pipeline_id: str,
        state_update: dict[str, Any],
    ) -> bool:
        """Update Pipeline state (single write entry point).
        
        This is the ONLY way to modify pipeline state. All state changes
        must go through this method to ensure single source of truth.
        
        Args:
            pipeline_id: Pipeline ID
            state_update: State update dict, will be deep merged with existing state
            
        Returns:
            True if successful
            
        Example:
            >>> sm.update_pipeline_state("pipe-123", {
            ...     "current_node": "analyst",
            ...     "status": "running"
            ... })
        """
        # Implementation:
        # 1. Read existing state_json
        # 2. Deep merge state_update
        # 3. Validate new state integrity
        # 4. Write to database
        pass
    
    def get_pipeline_state(self, pipeline_id: str) -> PipelineState | None:
        """Get complete Pipeline state (recommended read method).
        
        Returns:
            PipelineState object, or None if not found
        """
        pass
    
    # ==================== Convenience Query Methods ====================
    
    def get_current_node(self, pipeline_id: str) -> str | None:
        """Get current node (read from state_json)."""
        state = self.get_pipeline_state(pipeline_id)
        return state.get("current_node") if state else None
    
    def get_pipeline_status(self, pipeline_id: str) -> str:
        """Get Pipeline status (read from state_json)."""
        state = self.get_pipeline_state(pipeline_id)
        return state.get("status", "unknown") if state else "unknown"
    
    def is_node_completed(self, pipeline_id: str, node_id: str) -> bool:
        """Check if node is completed."""
        state = self.get_pipeline_state(pipeline_id)
        if not state:
            return False
        return node_id in state.get("completed_nodes", [])
    
    # ==================== Removed Methods (P1-1 Cleanup) ====================
    
    # P1-1 Note: update_pipeline_status() has been removed.
    # Use update_pipeline_state() directly instead.
    # 
    # Before (deprecated pattern):
    #   update_pipeline_status(pipeline_id, status, current_node)
    #
    # After (current pattern):
    #   update_pipeline_state(pipeline_id, {
    #       "status": status,
    #       "current_node": current_node,
    #   })
    
    # ==================== Consistency Checking ====================
    
    def _verify_state_consistency(self, pipeline_id: str) -> dict[str, Any] | None:
        """Runtime consistency check - P0 addition.
        
        Verifies consistency between top-level fields and state_json.
        Logs warnings when inconsistencies are detected.
        
        Returns:
            Inconsistency info if found, None otherwise
        """
        try:
            with self._db.acquire() as conn:
                cursor = conn.execute(
                    "SELECT current_node, state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                top_current_node = row["current_node"]
                state = json.loads(row["state_json"] or "{}")
                state_current_node = state.get("current_node")
                
                if top_current_node != state_current_node:
                    inconsistency = {
                        "pipeline_id": pipeline_id,
                        "top_current_node": top_current_node,
                        "state_current_node": state_current_node,
                        "field": "current_node"
                    }
                    logger.warning(
                        "state_inconsistency_detected",
                        **inconsistency,
                        operation="consistency_check"
                    )
                    return inconsistency
                
                return None
                
        except Exception as e:
            logger.error("consistency_check_failed", pipeline_id=pipeline_id, error=str(e))
            return None
```

### 4.5.5 Migration Phases

| Phase | Duration | Actions | Status |
|-------|----------|---------|--------|
| **Phase 1 (P0)** | 1-2 weeks | Add consistency checks, fix high-risk operations, sync updates | 🔄 In Progress |
| **Phase 2 (P1)** | 2-3 weeks | Create PipelineStateView, migrate all reads to state_json, add deprecation warnings | ⏳ Pending |
| **Phase 3 (P2)** | 1 week | Drop current_node column, remove deprecated methods | ⏳ Pending |

---

## 4.6 F5: Pipeline & Node Execution State Conversion

> **Reference**: [F5 Unified Design Spec](../research/2026-03-25-f5-unified-design-spec.md)  
> **TDD Plan**: [F5 TDD Implementation Plan](../solution/2026-03-25-f5-test-driven-implementation-plan.md)

### 4.6.1 Responsibility Shift

As part of F5 convergence, **state conversion responsibility** has been moved from `pipeline/graph.py` to `PipelineAdapter`:

| Conversion | Before (F5) | After (F5) |
|------------|-------------|------------|
| PipelineState → NodeRunState | `pipeline/graph.py:_convert_pipeline_to_node_state()` | `PipelineAdapter.convert_pipeline_to_node_state()` |
| NodeRunState → PipelineState | `pipeline/graph.py:_convert_node_to_pipeline_state()` | `PipelineAdapter.convert_node_to_pipeline_state()` |

### 4.6.2 PipelineAdapter State Conversion API

```python
# node_execution/pipeline_adapter.py

class PipelineAdapter:
    """Single boundary for pipeline <-> node_execution integration."""
    
    @staticmethod
    def convert_pipeline_to_node_state(
        pipeline_state: PipelineState,
        node_id: str,
    ) -> dict[str, Any]:
        """Convert PipelineState to NodeRunState for node execution.
        
        Transforms pipeline-level state into node execution format,
        including context accumulation and chained deliverables.
        
        Args:
            pipeline_state: Current PipelineState from LangGraph
            node_id: Target node identifier (e.g., "analyst", "pm")
            
        Returns:
            NodeRunState dictionary for node execution
            
        Example:
            >>> node_state = PipelineAdapter.convert_pipeline_to_node_state(
            ...     pipeline_state, "analyst"
            ... )
            >>> node_state["pipeline_id"]
            'pipeline-123'
            >>> node_state["node_id"]
            'analyst'
        """
        # 1. Extract subject_context and deliverables
        # 2. Compute context_hash
        # 3. Build accumulated context with predecessor deliverables
        # 4. Construct NodeRunState
        ...
    
    @staticmethod
    def convert_node_to_pipeline_state(
        node_state: dict[str, Any],
        original_state: PipelineState,
    ) -> PipelineState:
        """Convert NodeRunState back to PipelineState after execution.
        
        Merges node execution results into pipeline state,
        preserving all existing data and updating node-specific fields.
        
        Args:
            node_state: NodeRunState after node execution
            original_state: Original PipelineState before execution
            
        Returns:
            Updated PipelineState with execution results
            
        Example:
            >>> result_state = PipelineAdapter.convert_node_to_pipeline_state(
            ...     node_state, original_state
            ... )
            >>> "analyst" in result_state["deliverables"]
            True
            >>> result_state["current_node"]
            'analyst'
        """
        # 1. Deep copy original state
        # 2. Update deliverables, questions, evaluation
        # 3. Update iteration count and completed_nodes
        # 4. Set current_node
        ...
```

### 4.6.3 State Flow with F5

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    F5 State Conversion Flow                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pipeline Execution                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  create_pipeline_graph()                                              │ │
│  │  └── _create_integrated_node_executor()                              │ │
│  │       │                                                               │ │
│  │       ▼                                                               │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ PipelineAdapter.convert_pipeline_to_node_state()                │  │ │
│  │  │                                                                 │  │ │
│  │  │ Input:  PipelineState + node_id                                 │  │ │
│  │  │ Output: NodeRunState                                            │  │ │
│  │  │                                                                 │  │ │
│  │  │ • Extract subject_context                                       │  │ │
│  │  │ • Compute context_hash                                          │  │ │
│  │  │ • Accumulate predecessor deliverables                           │  │ │
│  │  │ • Build chained_context                                         │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │       │                                                               │ │
│  │       ▼                                                               │ │
│  │  node_execution/executor.py                                          │ │
│  │  └── DualAgentNode.execute()                                         │ │
│  │       │                                                               │ │
│  │       ▼                                                               │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │ PipelineAdapter.convert_node_to_pipeline_state()                │  │ │
│  │  │                                                                 │  │ │
│  │  │ Input:  NodeRunState + original PipelineState                   │  │ │
│  │  │ Output: Updated PipelineState                                   │  │ │
│  │  │                                                                 │  │ │
│  │  │ • Merge deliverable into deliverables                           │  │ │
│  │  │ • Update questions, evaluation                                  │  │ │
│  │  │ • Update iteration, completed_nodes                             │  │ │
│  │  │ • Set current_node                                              │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  │       │                                                               │ │
│  │       ▼                                                               │ │
│  │  Return updated PipelineState                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.6.4 Key Principles

1. **Single Responsibility**: 
   - `pipeline/` handles orchestration
   - `node_execution/` handles execution
   - `PipelineAdapter` handles state conversion

2. **Immutable State**:
   - All conversions create new state objects
   - Original state is never mutated
   - Deep copy used for nested structures

3. **Boundary Enforcement**:
   - No direct state manipulation across modules
   - All cross-module interactions through Adapter
   - Type safety with TypedDict schemas

---

## 5. Memory Management

### 5.1 Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Memory Architecture                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Two Memory Types:                                                          │
│                                                                             │
│  1. SHARED MEMORY (Subject Context)                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Persisted in SQLite                                                │ │
│  │  • Keyed by context_hash                                              │ │
│  │  • Accessible by all agents                                           │ │
│  │  • Contains project information, requirements, answers                │ │
│  │  • Updated via update_context operations                              │ │
│  │  • Survives restarts                                                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  2. PRIVATE MEMORY (Agent Reasoning)                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Ephemeral (in-memory only)                                         │ │
│  │  • Per-agent, not shared                                              │ │
│  │  • Contains reasoning traces, tool call history                       │ │
│  │  • Cleared after node completion                                      │ │
│  │  • NOT accessible by Evaluator Agent (isolation)                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Memory Flow:                                                               │
│                                                                             │
│  ┌─────────────────┐                                                       │
│  │ Subject Context │ ◀───── Shared ─────▶ All Agents                      │
│  │   (SQLite)      │        (keyed by context_hash)                        │
│  └─────────────────┘                                                       │
│                                                                             │
│  ┌─────────────────┐                                                       │
│  │ Private Memory  │ ◀───── Isolated ──▶ Independent Agent Only           │
│  │  (In-Memory)    │          ❌         NOT Evaluator Agent               │
│  └─────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Memory Manager Implementation

```python
from typing import Dict, Any, Optional

class MemoryManager:
    """Manages shared and private memory for agents."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.private_memory: Dict[str, dict] = {}  # In-memory, ephemeral
    
    # === Shared Memory (Subject Context) ===
    
    def load_shared_memory(self, context_hash: str) -> dict:
        """Load shared subject context."""
        return self.state_manager.load_context(context_hash)
    
    def save_shared_memory(self, context_hash: str, context: dict):
        """Save shared subject context."""
        self.state_manager.save_context(context_hash, context)
    
    def update_shared_memory(
        self, 
        context_hash: str, 
        key: str, 
        value: Any, 
        operation: str = "set"
    ):
        """Update shared memory."""
        self.state_manager.update_context(context_hash, key, value, operation)
    
    # === Private Memory (Agent Reasoning) ===
    
    def initialize_private_memory(self, agent_id: str):
        """Initialize ephemeral private memory for agent."""
        self.private_memory[agent_id] = {
            "reasoning": [],
            "tool_calls": [],
            "intermediate_results": []
        }
    
    def append_private_memory(
        self, 
        agent_id: str, 
        memory_type: str, 
        content: Any
    ):
        """Append to agent's private memory."""
        if agent_id not in self.private_memory:
            self.initialize_private_memory(agent_id)
        
        if memory_type in self.private_memory[agent_id]:
            self.private_memory[agent_id][memory_type].append(content)
    
    def get_private_memory(self, agent_id: str) -> Optional[dict]:
        """Get agent's private memory."""
        return self.private_memory.get(agent_id)
    
    def clear_private_memory(self, agent_id: str):
        """Clear private memory after node completion."""
        self.private_memory.pop(agent_id, None)
    
    # === Context Building ===
    
    def build_agent_context(
        self, 
        agent_id: str, 
        agent_type: str, 
        context_hash: str
    ) -> dict:
        """Build context for agent with appropriate access control."""
        shared_context = self.load_shared_memory(context_hash)
        
        if agent_type == "independent":
            # Independent Agent: Full access
            return {
                "subject": shared_context,
                "private": self.get_private_memory(agent_id)
            }
        else:
            # Evaluator Agent: Subject only (isolation enforced)
            return {
                "subject": shared_context
                # NO private memory - context isolation
            }
```

---

## 6. LangGraph Checkpoint Integration

### 6.1 SqliteSaver Configuration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   LangGraph Checkpoint Integration                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Checkpoint Storage                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  LangGraph SqliteSaver stores checkpoints in the same database       │ │
│  │                                                                        │ │
│  │  Tables created by LangGraph:                                         │ │
│  │  • checkpoints (checkpoint data)                                      │ │
│  │  • checkpoint_writes (pending writes)                                 │ │
│  │  • checkpoint_blobs (large data blobs)                               │ │
│  │                                                                        │ │
│  │  Thread Isolation:                                                    │ │
│  │  • Each node run uses thread_id = run_id                             │ │
│  │  • Checkpoints are isolated per thread                               │ │
│  │  • Resume uses thread_id to find correct checkpoint                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Checkpoint Content                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  {                                                                     │ │
│  │    "id": "checkpoint_uuid",                                           │ │
│  │    "thread_id": "run_id",                                             │ │
│  │    "checkpoint_ns": "",                                               │ │
│  │    "channel_values": {                                                │ │
│  │      // NodeRunState fields                                           │ │
│  │      "run_id": "...",                                                 │ │
│  │      "node": "analyst",                                               │ │
│  │      "context_hash": "...",                                           │ │
│  │      "iteration": 0,                                                  │ │
│  │      "status": "running",                                             │ │
│  │      "deliverable": {...},                                            │ │
│  │      "questions": [...],                                              │ │
│  │      "evaluation": {...},                                             │ │
│  │      ...                                                              │ │
│  │    },                                                                 │ │
│  │    "versions_seen": {...},                                            │ │
│  │    "pending_sends": []                                                │ │
│  │  }                                                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Checkpointer Setup

```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class CheckpointManager:
    """Manages LangGraph checkpointing."""
    
    def __init__(self, db_path: str = "docuswarm.db"):
        # Reuse existing connection with WAL mode
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        
        # Create LangGraph checkpointer
        self.checkpointer = SqliteSaver(self.conn)
    
    def get_checkpointer(self) -> SqliteSaver:
        """Get checkpointer for graph compilation."""
        return self.checkpointer
    
    def get_checkpoint_history(self, run_id: str) -> list:
        """Get checkpoint history for a node run."""
        config = {"configurable": {"thread_id": run_id}}
        
        checkpoints = []
        for cp in self.checkpointer.list(config):
            state = cp.channel_values
            checkpoints.append({
                "id": cp.id,
                "timestamp": cp.ts,
                "node": state.get("node"),
                "iteration": state.get("iteration"),
                "status": state.get("status")
            })
        
        return checkpoints
    
    def get_latest_checkpoint(self, run_id: str) -> dict:
        """Get the latest checkpoint state."""
        config = {"configurable": {"thread_id": run_id}}
        checkpoint = self.checkpointer.get(config)
        
        if checkpoint:
            return checkpoint.channel_values
        return None
```

---

## 7. Transaction Management

### 7.1 Transaction Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Transaction Patterns                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern 1: Node Run Update (Atomic)                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  with state_manager.conn:  # Implicit transaction                     │ │
│  │      # All operations in transaction                                  │ │
│  │      state_manager.update_node_run(...)                               │ │
│  │      state_manager.update_run_status(...)                             │ │
│  │      memory_manager.update_shared_memory(...)                         │ │
│  │  # Auto-commit on exit, rollback on exception                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Pattern 2: Node Run Creation (Multi-table)                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  try:                                                                 │ │
│  │      conn.execute("BEGIN IMMEDIATE")                                  │ │
│  │      conn.execute("INSERT INTO node_runs ...")                        │ │
│  │      conn.execute("INSERT INTO subject_context ...")                  │ │
│  │      conn.execute("COMMIT")                                           │ │
│  │  except Exception:                                                    │ │
│  │      conn.execute("ROLLBACK")                                         │ │
│  │      raise                                                            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Pattern 3: Optimistic Locking                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  # Read with version                                                  │ │
│  │  row = conn.execute("SELECT *, updated_at FROM node_runs ...").fetchone()│ │
│  │  original_updated = row["updated_at"]                                 │ │
│  │                                                                        │ │
│  │  # Update with version check                                          │ │
│  │  result = conn.execute(                                               │ │
│  │      "UPDATE node_runs SET ... WHERE run_id = ? AND updated_at = ?",  │ │
│  │      (run_id, original_updated)                                       │ │
│  │  )                                                                    │ │
│  │                                                                        │ │
│  │  if result.rowcount == 0:                                             │ │
│  │      raise ConcurrentModificationError()                              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Concurrency Handling

```python
class ConcurrencyManager:
    """Handles concurrent access patterns."""
    
    BUSY_TIMEOUT = 5000  # 5 seconds
    MAX_RETRIES = 3
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.execute(f"PRAGMA busy_timeout={self.BUSY_TIMEOUT}")
    
    def execute_with_retry(self, operation):
        """Execute operation with retry on lock."""
        for attempt in range(self.MAX_RETRIES):
            try:
                return operation()
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < self.MAX_RETRIES - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                raise
    
    def optimistic_update(
        self, 
        table: str, 
        id_column: str, 
        id_value: str, 
        updates: dict, 
        expected_version: str
    ) -> bool:
        """Perform optimistic locking update."""
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        sql = f"""
            UPDATE {table} 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE {id_column} = ? AND updated_at = ?
        """
        
        values = list(updates.values()) + [id_value, expected_version]
        result = self.conn.execute(sql, values)
        self.conn.commit()
        
        return result.rowcount > 0
```

---

## 8. Data Integrity

### 8.1 Validation

```python
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

class StateValidator:
    """Validates state data before persistence."""
    
    def validate_node_run_state(self, state: dict) -> ValidationResult:
        """Validate complete node run state."""
        errors = []
        
        # Required fields
        required = ["run_id", "node", "context_hash", "status"]
        for field in required:
            if field not in state:
                errors.append(f"Missing required field: {field}")
        
        # Status value
        valid_statuses = ["pending", "running", "completed", "failed", "blocked"]
        if state.get("status") not in valid_statuses:
            errors.append(f"Invalid status: {state.get('status')}")
        
        # Context hash must exist
        if not state.get("context_hash"):
            errors.append("Context hash is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_node_result(self, result: dict) -> ValidationResult:
        """Validate node result before save."""
        errors = []
        
        # Required fields
        required = ["node", "iteration", "status"]
        for field in required:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        # Deliverable structure
        if result.get("deliverable"):
            if not isinstance(result["deliverable"], dict):
                errors.append("Deliverable must be a dict")
            elif "content" not in result["deliverable"]:
                errors.append("Deliverable missing content")
        
        # Questions structure
        if result.get("questions"):
            if not isinstance(result["questions"], list):
                errors.append("Questions must be a list")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
```

### 8.2 Backup and Recovery

```python
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    """Manages database backups."""
    
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> str:
        """Create a timestamped backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"docuswarm_{timestamp}.db"
        
        # SQLite backup API for consistent backup
        source = sqlite3.connect(self.db_path)
        dest = sqlite3.connect(backup_path)
        
        source.backup(dest)
        
        source.close()
        dest.close()
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str):
        """Restore from backup."""
        backup = Path(backup_path)
        if not backup.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Close existing connections
        # Copy backup to main database
        shutil.copy(backup, self.db_path)
    
    def list_backups(self) -> List[dict]:
        """List available backups."""
        backups = []
        for backup in self.backup_dir.glob("docuswarm_*.db"):
            stat = backup.stat()
            backups.append({
                "path": str(backup),
                "name": backup.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
```

---

## 9. File Structure

```
docuswarm/storage/
├── __init__.py
├── database.py          # Database configuration
├── state_manager.py     # StateManager class
├── memory_manager.py    # MemoryManager class
├── checkpoint.py        # CheckpointManager class
├── validation.py        # StateValidator class
├── backup.py            # BackupManager class
└── schema.sql           # Database schema
```

---

## 10. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| Node Execution Architecture | `03_PIPELINE_ARCHITECTURE.md` |
| Context Isolation | `06_CONTEXT_ISOLATION.md` |
| F2 Test-Driven Implementation Plan | `../solution/2026-03-25-f2-test-driven-implementation-plan.md` |
| F2 State Consistency Research | `../research/2026-03-25-f2-state-json-consistency-research-report.md` |
| F2 Unified Design Spec | `../research/2026-03-25-f2-unified-design-spec.md` |

### External References

- [SQLite WAL Mode](https://sqlite.org/wal.html)
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

---

**Document End**
> **2026-03-13 Alignment Notice**: 当前状态层仍混合保存摘要式 deliverable 与运行时结构，且 `update_context` 尚未接入真实持久化。后续状态语义以 `../research/2026-03-13-p0-single-truth-deliverable-plan.md` 和 `../research/2026-03-13-p1-update-context-persistence-plan.md` 为准。

>
> **2026-03-17 Update**: 产品已决定工作流完全不读取 \docs/\ 目录。因此：
> - P1-2 (受控 docs 上下文策略) 已从重构计划中移除
> - 所有 docs 相关读取/写入能力应进入清理范围
> - \ContextResolver\ 和 \@path\ 注入不再推进
> - 本文档中关于 docs 扩展的描述应被视为待清理而非待实现
> - 推荐的重构路径请参考 \../research/2026-03-13-docuswarm-context-refactor-overview.md

>
> **2026-03-17 TDD Implementation Plan**: 测试驱动实施方案已制定，详见：
> - `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
> - `../solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md` (PipelineState shared_context 字段)

>
> **2026-03-25 F2 Update**: Pipeline 状态管理正在实施单一真相源改造：
> - `state_json` 作为 pipeline 状态的唯一真相源
> - `PipelineStateView` 提供统一的状态读取接口
> - `update_pipeline_state()` 作为唯一状态写入入口
> - 实施详情参考 `../solution/2026-03-25-f2-test-driven-implementation-plan.md`
---

## 6. Reference Docs Preload Architecture (Step 2)

> **Phase**: 13 (P12)  
> **Status**: 🔄 In Progress  
> **Reference**: [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)  
> **Based on**: [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md)

### 6.1 Overview

引用文档预加载功能实现了 `NodeExecutionContext.docs_context` 字段的自动填充。当 context file（如 `bubble-sort-context.md`）引用了其他支撑文档（如 `algorithm-spec.md`）时，系统会自动：

1. 从 context file 内容中提取引用的文件名
2. 在 `docs/` 目录下递归搜索这些文件
3. 读取文件内容并注入到 Agent 的提示词中

这使得 Agent 无需主动调用 `read_document` 工具即可看到所有引用文档的完整内容。

### 6.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Reference Docs Preload Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Input: Context File with References                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ## Bubble Sort Project                                               │   │
│  │                                                                      │   │
│  │ Please refer to:                                                     │   │
│  │ - `algorithm-spec.md` — Algorithm specification                      │   │
│  │ - `requirements.md` — Stakeholder requirements                       │   │
│  │ - `test-criteria.md` — Evaluation criteria                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ NodeExecutionContextBuilder.build()                                  │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ _resolve_reference_docs()                                    │    │   │
│  │  │                                                              │    │   │
│  │  │ Step 1: Extract Filenames                                    │    │   │
│  │  │   Pattern 1: `([^`]+\.(?:md|txt|yaml|yml|json))`             │    │   │
│  │  │              Matches: `algorithm-spec.md`                    │    │   │
│  │  │   Pattern 2: \b([\w-]+\.(?:md|txt|yaml|yml|json))\b          │    │   │
│  │  │              Matches: requirements.md (bare format)          │    │   │
│  │  │                                                              │    │   │
│  │  │ Step 2: Recursive Search in docs/                            │    │   │
│  │  │   Search paths (sorted by depth):                            │    │   │
│  │  │     - docs/algorithm-spec.md              ← Shallowest        │    │   │
│  │  │     - docs/bubble-sort/algorithm-spec.md  ← Deeper            │    │   │
│  │  │     - docs/research/algorithm-spec.md     ← Deepest           │    │   │
│  │  │   Selection: Shallowest wins                                 │    │   │
│  │  │                                                              │    │   │
│  │  │ Step 3: Read Content with Protection                         │    │   │
│  │  │   - Encoding: UTF-8 (required)                               │    │   │
│  │  │   - Max size: 10,000 characters                              │    │   │
│  │  │   - Truncation notice: "\n\n[内容已截断]"                     │    │   │
│  │  │                                                              │    │   │
│  │  │ Output: List[{filename, path, content}]                      │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  docs_context = _resolve_reference_docs(...)                         │   │
│  │                                                                      │   │
│  │  return NodeExecutionContext(                                        │   │
│  │      pipeline_id=...,                                                │   │
│  │      node_id=...,                                                    │   │
│  │      docs_context=docs_context,  # Pre-loaded reference docs        │   │
│  │      ...                                                             │   │
│  │  )                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ NodePromptContractBuilder._build_context_section()                   │   │
│  │                                                                      │   │
│  │ sections = []                                                        │   │
│  │                                                                      │   │
│  │ # Original context                                                   │   │
│  │ if original_context:                                                 │   │
│  │     sections.append(f"## 原始上下文\n{content}")                     │   │
│  │                                                                      │   │
│  │ # Reference docs (NEW)                                               │   │
│  │ docs = context.get("docs_context", [])                               │   │
│  │ if docs:                                                             │   │
│  │     sections.append("\n## 引用文档")          # NEW SECTION          │   │
│  │     for doc in docs:                                                 │   │
│  │         sections.append(f"\n### {doc['filename']}\n")                │   │
│  │         sections.append(doc['content'])                              │   │
│  │                                                                      │   │
│  │ # Chained deliverables                                               │   │
│  │ if chained_deliverables:                                             │   │
│  │     sections.append("\n## 上游交付物摘要")                           │   │
│  │     ...                                                              │   │
│  │                                                                      │   │
│  │ return "\n".join(sections)                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Independent Agent Prompt                                             │   │
│  │                                                                      │   │
│  │ ...                                                                  │   │
│  │ ## 引用文档                     <-- Agent sees this section          │   │
│  │                                                                      │   │
│  │ ### algorithm-spec.md                                                │   │
│  │ # Algorithm Specification                                            │   │
│  │ ## Overview                                                          │   │
│  │ Bubble sort is a simple sorting algorithm...                         │   │
│  │ (Full content up to 10K chars)                                       │   │
│  │                                                                      │   │
│  │ ### requirements.md                                                  │   │
│  │ # Stakeholder Requirements                                           │   │
│  │ ...                                                                  │   │
│  │                                                                      │   │
│  │ ## Execution Workflow                                                │   │
│  │ 1. **Create Deliverable**: ...                                       │   │
│  │ ...                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Component Details

#### 6.3.1 Filename Extraction

```python
# autoBMAD/docuswarm/node_execution/context_builder.py

import re
from pathlib import Path
from typing import Any

# Supported filename patterns (case-insensitive)
FILENAME_PATTERNS = [
    # Backtick format: `filename.md`
    r'`([^`]+\.(?:md|txt|yaml|yml|json))`',
    # Bare format: filename.md
    r'\b([\w-]+\.(?:md|txt|yaml|yml|json))\b',
]

ALLOWED_EXTENSIONS = frozenset(['.md', '.txt', '.yaml', '.yml', '.json'])

def _extract_filenames(content: str) -> set[str]:
    """Extract referenced filenames from content."""
    filenames: set[str] = set()
    
    for pattern in FILENAME_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        filenames.update(matches)
    
    return filenames
```

#### 6.3.2 File Search Strategy

```python
def _search_files(
    filenames: set[str],
    repo_root: Path,
) -> dict[str, Path]:
    """Search for files in docs/ directory recursively.
    
    Returns mapping of filename -> Path (shallowest match wins).
    """
    docs_dir = repo_root / "docs"
    if not docs_dir.exists():
        return {}
    
    found: dict[str, Path] = {}
    
    for filename in filenames:
        # Find all matches, sort by path depth
        candidates = sorted(
            docs_dir.rglob(filename),
            key=lambda p: len(p.parts)
        )
        
        for candidate in candidates:
            if candidate.is_file():
                found[filename] = candidate
                break  # Shallowest wins
    
    return found
```

#### 6.3.3 Content Reading with Protection

```python
MAX_DOC_CONTENT_LENGTH = 10000  # characters
TRUNCATION_NOTICE = "\n\n[内容已截断]"

def _read_file_content(
    file_path: Path,
    max_length: int = MAX_DOC_CONTENT_LENGTH,
) -> str | None:
    """Read file content with encoding and size protection."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if len(content) > max_length:
            content = content[:max_length] + TRUNCATION_NOTICE
        
        return content
        
    except (OSError, UnicodeDecodeError):
        return None  # Graceful degradation
```

### 6.4 Security Considerations

| Aspect | Implementation |
|--------|----------------|
| Path Validation | Uses existing `PathValidator` from `file_tools.py` |
| Directory Whitelist | Only searches within `{repo_root}/docs/` |
| Path Traversal Prevention | Resolved paths must start with docs/ directory |
| Extension Filtering | Only allows `.md`, `.txt`, `.yaml`, `.yml`, `.json` |
| Size Limits | 10,000 char limit per file prevents prompt overflow |

### 6.5 Testing Strategy

| Test Category | Test Cases |
|---------------|------------|
| **Unit Tests** | Filename extraction (backtick + bare formats) |
| | Recursive search (shallowest wins) |
| | Content truncation (boundary conditions) |
| | Extension filtering |
| **Integration Tests** | End-to-end with temporary filesystem |
| | Bubble Sort scenario (3 reference docs) |
| | Same-name files in different directories |
| **Architecture Tests** | Path traversal prevention |
| | Security boundary validation |

### 6.6 Migration Notes

**Before (Step 2 implementation)**:
```python
# context_builder.py L43
docs_context=[],  # Hardcoded empty list
```

**After (Step 2 implementation)**:
```python
# context_builder.py build() method
docs_context = self._resolve_reference_docs(
    original_context, node_id, repo_root
) if repo_root else [],
```

### 6.7 Related Documents

| Document | Description |
|----------|-------------|
| [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md) | 测试驱动实施方案 |
| [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md) | 可行性深度分析 |
| [Single Context Protocol](2026-03-13-p0-single-context-protocol-implementation-design.md) | NodeExecutionContext 设计 |

---

**Document End**

> **2026-04-05 Update**: Phase 13 (Step 2) - Reference Docs Preload Architecture 已添加。
> 
> **2026-03-17 Update**: 产品已决定工作流完全不读取 `docs/` 目录。因此：
> - P1-2 (受控 docs 上下文策略) 已从重构计划中移除
> - 所有 docs 相关读取/写入能力应进入清理范围
> - `ContextResolver` 和 `@path` 注入不再推进
> - 本文档中关于 docs 扩展的描述应被视为待清理而非待实现
> - 推荐的重构路径请参考 `../research/2026-03-13-docuswarm-context-refactor-overview.md`
>
> **2026-03-17 TDD Implementation Plan**: 测试驱动实施方案已制定，详见：
> - `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
> - `../solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md` (PipelineState shared_context 字段)
>
> **2026-03-25 F2 Update**: Pipeline 状态管理正在实施单一真相源改造：
> - `state_json` 作为 pipeline 状态的唯一真相源
> - `PipelineStateView` 提供统一的状态读取接口
> - `update_pipeline_state()` 作为唯一状态写入入口
> - 实施详情参考 `../solution/2026-03-25-f2-test-driven-implementation-plan.md`

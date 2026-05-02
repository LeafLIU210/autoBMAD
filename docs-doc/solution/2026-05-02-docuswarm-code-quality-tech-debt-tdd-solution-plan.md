# DocuSwarm Code Quality & Technical Debt — Test-Driven Solution Plan

**Based on:** `docs-doc/research/2026-05-02-docuswarm-code-quality-tech-debt-deep-research-report.md`
**Date:** 2026-05-02
**Target:** Resolve all 10 ISSUEs via TDD (red-green-refactor) in `.venv`

---

## Executive Summary

This plan maps every recommendation from the deep research report to concrete test cases, organized in 3 phases matching the Remediation Roadmap. Each phase follows TDD: write failing test → fix code → verify green.

| Phase | Goal | ISSUEs Covered | Exit Criteria |
|---|---|---|---|
| Phase 1 | Stop The Hangs | ISSUE-1, ISSUE-2, ISSUE-3, ISSUE-4, ISSUE-9 | All new unit tests pass in <5s each; no shared singleton pollution |
| Phase 2 | Reduce Drift | ISSUE-5, ISSUE-6, ISSUE-7, ISSUE-8 | State contract tests pass; tool security gap closed; logging redacted |
| Phase 3 | Enforce Quality | ISSUE-10 | Ruff baseline clean; mandatory gate configured |

---

## Phase 1: Stop The Hangs

### P1.1 ISSUE-1 — `StateManager.update_pipeline_state` Deadlock/Hang

**Problem:** `_update_pipeline_state_sync` calls `_pipeline_exists` (which acquires a connection) before acquiring another connection in the same method. Under concurrent test execution with shared `DatabaseManager` singleton, this can hang.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T1.1 | `tests/test_docuswarm_p0_state_manager_isolation.py` | `update_pipeline_state` on temporary DB completes in <1s (no LangGraph, no SDK) |
| T1.2 | `tests/test_docuswarm_p0_state_manager_isolation.py` | 100 sequential `create → update → get` calls complete in <3s total |
| T1.3 | `tests/test_docuswarm_p0_state_manager_isolation.py` | `DatabaseManager.reset_instance()` clears all cached instances and closes connections |
| T1.4 | `tests/test_docuswarm_p0_state_manager_isolation.py` | Replace nested `_pipeline_exists` + `UPDATE` with single `UPDATE ... WHERE` + `rowcount` check |

**Code Fix:**
1. In `_update_pipeline_state_sync`: remove `self._pipeline_exists(pipeline_id)` call at the start.
2. Inside the `with self._db.acquire()` block, execute `UPDATE pipelines SET state_json=?, status=?, current_node=?, updated_at=CURRENT_TIMESTAMP WHERE pipeline_id=?` and check `conn.total_changes == 0` to raise `StorageError` if pipeline not found.
3. Same pattern for `_replace_pipeline_state_sync`.

### P1.2 ISSUE-2 — LangGraph Lifecycle Leaks

**Problem:** Graph invocation, checkpointer, and session managers have no single lifecycle owner. Cancelled executions leave pending tasks and open connections.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T2.1 | `tests/test_docuswarm_p0_graph_lifecycle.py` | After `start_pipeline` with mocked graph that raises `CancelledError`, assert no pending asyncio tasks remain |
| T2.2 | `tests/test_docuswarm_p0_graph_lifecycle.py` | After mocked graph completion, assert checkpointer connection is closed |
| T2.3 | `tests/test_docuswarm_p0_graph_lifecycle.py` | Mocked graph that raises `Exception` still triggers checkpointer close in `finally` |

**Code Fix:**
1. Track all `asyncio.create_task` calls in `HybridOrchestrator`.
2. In `finally` block of `start_pipeline`, cancel and await all tracked tasks before closing checkpointer.
3. Ensure `checkpointer.conn.close()` is always awaited.

### P1.3 ISSUE-3 — Missing `asyncio` Import in `independent.py`

**Problem:** `_on_session_created` calls `asyncio.get_running_loop()` but `asyncio` is not imported. Confirmed by Ruff F821.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T3.1 | `tests/test_docuswarm_p0_session_persistence.py` | Import `asyncio` in `independent.py`; verify no F821 on that file |
| T3.2 | `tests/test_docuswarm_p0_session_persistence.py` | Mock `_call_llm_with_prompts` to invoke `_on_session_created` callback; assert `state_manager.update_pipeline_state` is called with session_id |

**Code Fix:**
1. Add `import asyncio` at top of `autoBMAD/docuswarm/agents/independent.py`.
2. Replace bare `except Exception:` in `_on_session_created` with `except (RuntimeError, StorageError):` or at minimum log exception type + session id.

### P1.4 ISSUE-4 — Explicit Pipeline ID Handling

**Problem:** `start_pipeline` creates a DB pipeline with generated id, then swaps to caller-provided `pipeline_id`. If caller provides one, the row with that id may not exist before `update_pipeline_state` is called.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T4.1 | `tests/test_docuswarm_p0_state_manager_consistency.py` | `start_pipeline(..., pipeline_id="p-custom")` must complete in <5s and DB primary key == `"p-custom"` |
| T4.2 | `tests/test_docuswarm_p0_state_manager_consistency.py` | `create_pipeline(..., pipeline_id="p-custom")` uses exact id |

**Code Fix:**
1. In `HybridOrchestrator.start_pipeline`: pass `pipeline_id=pipeline_id` to `self._state_manager.create_pipeline(...)`.
2. Remove the `db_pipeline_id / final_pipeline_id` swap logic.

### P1.5 ISSUE-9 — Fire-and-Forget State Writes

**Problem:** `_on_session_created` schedules `state_manager.update_pipeline_state` with `loop.create_task` but does not await it. Pipeline can continue before session metadata is durable.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T9.1 | `tests/test_docuswarm_p0_session_persistence.py` | After `_on_session_created` fires, state must be durable before node execution continues |
| T9.2 | `tests/test_docuswarm_p0_session_persistence.py` | Cancellation during session persistence must not lose session id |

**Code Fix (ADR-STATE-001 aligned):**
1. Change `_on_session_created` from fire-and-forget to return the created task.
2. In the caller (`_call_llm_with_prompts` boundary), collect and await all pending tasks before returning.
3. Alternatively, make session persistence part of `SessionManager` lifecycle with explicit await.

---

## Phase 2: Reduce Drift

### P2.1 ISSUE-5 — State Single Source of Truth (ADR-STATE-001)

**Decision:** `state_json` is the sole logical authority (SSOT). Top-level `status` / `current_node` are materialized projection columns.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T5.1 | `tests/test_docuswarm_p0_state_projection_consistency.py` | After every `update_pipeline_state`, assert `top_status == json_extract(state_json,'$.status')` and same for `current_node` |
| T5.2 | `tests/test_docuswarm_p0_state_projection_consistency.py` | `get_pipeline` returns `state["status"]` directly; no fallback to `row["status"]` |
| T5.3 | `tests/test_docuswarm_p0_state_projection_consistency.py` | `state_json` NULL triggers `StorageError` (data corruption), not silent fallback |
| T5.4 | `tests/test_docuswarm_p0_state_projection_consistency.py` | `update_pipeline_state` with missing `status` key raises `StorageError` (no NULL write) |
| T5.5 | `tests/test_docuswarm_p0_state_projection_consistency.py` | Health check `SELECT ... WHERE status != json_extract(state_json,'$.status')` detects mismatch and repairs from `state_json` |

**Code Fix:**
1. `update_pipeline_state`:
   - Remove `_pipeline_exists` prefix (see P1.1).
   - `top_status = current_state["status"]` (dict access, not `.get(..., None)`). Missing → `StorageError`.
   - Single `UPDATE` writes both `state_json` and top-level columns atomically.
2. `get_pipeline`:
   - `"status": state.get("status", row["status"])` → `"status": state["status"]`.
   - Same for `current_node`.
   - If `state_json` is NULL/empty → raise `StorageError`.
3. `list_pipelines`:
   - Continue reading top-level columns (for B-tree index), but treat as read-only projection.
4. Add `StateManager.health_check_repair()` method that runs the mismatch query and repairs.

### P2.2 ISSUE-6 — SummaryAgent Pre-Graph Blocking

**Problem:** `start_pipeline` calls `_summarize_referenced_documents` before graph execution. A summary timeout prevents any node execution.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T6.1 | `tests/test_docuswarm_p1_summary_agent_timeout.py` | `_summarize_referenced_documents` timeout (0.01s) raises `TimeoutError` but pipeline still starts graph with `docs_context_summary=[]` |
| T6.2 | `tests/test_docuswarm_p1_summary_sync.py` | `start_pipeline` persists `summary_status` field (`skipped` / `ready` / `failed`) |

**Code Fix:**
1. Make summaries optional: catch timeout, set `docs_context_summary=[]`, persist `summary_status="skipped"`.
2. Only block on summary if `require_summary=True` is passed (default `False`).

### P2.3 ISSUE-7 — Dual Tool Implementations

**Problem:** Both legacy and SDK variants exist. Security tests run against SDK `PathValidator`, but legacy `PathValidator` lacks `is_relative_to` guard.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T7.1 | `tests/test_docuswarm_p4_security_hardening.py` | `file_tools.PathValidator` also uses `resolve().is_relative_to()` (or delegate to shared validator) |
| T7.2 | `tests/test_docuswarm_p4_security_hardening.py` | `search_tools.PathValidator` uses same robust check |

**Code Fix:**
1. Extract shared `PathValidator` into `autoBMAD/docuswarm/tools/_shared_validation.py`.
2. Make both `file_tools.py` and `file_tools_sdk.py` import from shared module.
3. Add deprecation warning to legacy module.

### P2.4 ISSUE-8 — Logging Exposes Raw User Context

**Problem:** `HybridOrchestrator.start_pipeline` logs `subject_context` which may contain credentials or proprietary text.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T8.1 | `tests/test_docuswarm_p0_logging_redaction.py` | `start_pipeline` log event contains `subject`, `context_keys`, `content_length`, `content_hash` — NOT full `subject_context` |

**Code Fix:**
1. Replace `logger.info("starting_pipeline", subject_context=subject_context)` with redacted metadata.
2. Use `utils/logging.py` redaction helpers if available, or compute simple hash/length.

---

## Phase 3: Enforce Quality

### P3.1 ISSUE-10 — Ruff Quality Gate

**Problem:** 91 ruff error lines including F821 in runtime code. Quality gate not enforced.

**Tests:**

| Test ID | File | Description |
|---|---|---|
| T10.1 | `tests/test_docuswarm_p3_quality_gates.py` | `ruff check autoBMAD/docuswarm/agents/independent.py` returns 0 (F821 fixed) |
| T10.2 | `tests/test_docuswarm_p3_quality_gates.py` | `ruff check autoBMAD/docuswarm` total errors <= baseline (target: clean or documented ignores) |

**Code Fix:**
1. Fix F821 (`import asyncio` in `independent.py`).
2. Fix or explicitly configure E402 for intentional runtime import ordering (e.g., add per-file ignores in `pyproject.toml` for files that need `TYPE_CHECKING` pattern).
3. Fix remaining low-risk issues (unused imports, whitespace).

---

## Test Execution Order

```bash
# Phase 1 — isolation + lifecycle
pytest tests/test_docuswarm_p0_state_manager_isolation.py -v --timeout=10
pytest tests/test_docuswarm_p0_graph_lifecycle.py -v --timeout=10
pytest tests/test_docuswarm_p0_session_persistence.py -v --timeout=10
pytest tests/test_docuswarm_p0_state_manager_consistency.py -v --timeout=10

# Phase 2 — state contract + security + logging
pytest tests/test_docuswarm_p0_state_projection_consistency.py -v --timeout=10
pytest tests/test_docuswarm_p1_summary_agent_timeout.py -v --timeout=10
pytest tests/test_docuswarm_p4_security_hardening.py -v --timeout=10
pytest tests/test_docuswarm_p0_logging_redaction.py -v --timeout=10

# Phase 3 — quality gates
pytest tests/test_docuswarm_p3_quality_gates.py -v --timeout=30

# Full regression
pytest tests/test_docuswarm_p0_*.py tests/test_docuswarm_p1_*.py -v --timeout=60
```

---

## Fixture Requirements

Add to `tests/conftest.py` or new `tests/fixtures/database.py`:

```python
@pytest.fixture
def isolated_state_manager(tmp_path: Path) -> StateManager:
    """Return a StateManager backed by a temporary, isolated database."""
    db_path = tmp_path / "isolated.db"
    # Ensure no singleton contamination from other tests
    DatabaseManager.reset_instance()
    sm = StateManager(db_path=str(db_path))
    yield sm
    DatabaseManager.reset_instance()
```

---

## Success Criteria

1. Every new test starts red (confirms issue exists) and ends green (confirms fix works).
2. All existing tests continue to pass.
3. `ruff check autoBMAD/docuswarm/agents/independent.py` is clean.
4. `StateManager.update_pipeline_state` completes in <1s on isolated DB.
5. No `asyncio` task leaks after mocked graph cancellation.

---

## Risk Mitigation

- **Low risk:** Most changes are additive (new tests) or tighten existing contracts.
- **Medium risk:** Removing `_pipeline_exists` prefix from `update_pipeline_state` changes error timing. Mitigation: test both "not found" and "success" paths.
- **Medium risk:** `get_pipeline` no longer falls back to top-level columns. Mitigation: ensure all writes go through `update_pipeline_state` (which syncs both).
- **High risk:** Changing `_on_session_created` from fire-and-forget to awaited may slow node execution. Mitigation: make it configurable or return task for upper-layer await.

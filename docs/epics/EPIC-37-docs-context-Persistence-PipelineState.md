# EPIC-37: docs_context Persistence (Method A: PipelineState)

**Epic ID**: EPIC-37  
**Source Research**: `docs/research/docuswarm-deep-reform/07-docs-context-persistence.md`  
**Recommended Solution**: Method A - Store in PipelineState, leveraged by LangGraph automatic checkpointing  
**Priority**: P0  
**Estimated Effort**: ~7 hours (~1 day)  
**Status**: Ready for Implementation  
**Depends On**: EPIC-36 (SummaryAgent generates the summaries to be persisted)

---

## Overview

`docs_context` is currently rebuilt by every node (5 times per pipeline), wasting ~2.5 seconds and preventing proper cross-node sharing. This epic implements the persistence layer for `docs_context` by adding a `docs_context_summary` field to `PipelineState`. Since LangGraph automatically manages `PipelineState` checkpointing, this provides free persistence, cross-node sharing, and pipeline resume support with minimal code changes.

## Problem Statement

**Repeated Construction Evidence**:
```
Pipeline execution:
  analyst → context_builder._resolve_reference_docs() → 1st construction
  pm      → context_builder._resolve_reference_docs() → 2nd construction (DUPLICATE)
  ux      → context_builder._resolve_reference_docs() → 3rd construction (DUPLICATE)
  architect → context_builder._resolve_reference_docs() → 4th construction (DUPLICATE)
  po      → context_builder._resolve_reference_docs() → 5th construction (DUPLICATE)

Performance: ~500ms × 5 = 2.5 seconds wasted per pipeline
```

**Current Cross-Node Transfer**:
- `docs_context` is NOT included in `PipelineState → NodeRunState` conversion
- Each node must independently rebuild `docs_context` from scratch
- Pipeline resume cannot restore `docs_context` state

## Goals

1. Add `docs_context_summary: list[dict[str, Any]]` field to `PipelineState` TypedDict
2. Update `create_initial_state()` to accept `docs_context_summary` parameter
3. Update `PipelineAdapter` to inject summary into node's `original_context`
4. Update `context_builder.build()` to read from cache first, fallback second
5. Update `orchestrator.resume_pipeline()` to restore summary from checkpoint

## Recommended Solution: Method A (PipelineState)

**Why Method A over B (SQLite) and C (Filesystem)**:

| Criteria | Method A (PipelineState) | Method B (SQLite) | Method C (Filesystem) |
|---------|------------------------|------------------|---------------------|
| Implementation complexity | ⭐ Minimal | ⭐⭐⭐ Complex | ⭐⭐ Medium |
| Performance | ⭐⭐⭐⭐⭐ In-memory | ⭐⭐⭐ DB IO | ⭐⭐⭐ File IO |
| Reliability | ⭐⭐⭐⭐⭐ LangGraph managed | ⭐⭐⭐ Manual | ⭐⭐⭐⭐ File |
| Auto-recovery | ⭐⭐⭐⭐⭐ Automatic | ⭐⭐ Manual | ⭐⭐ Manual |
| Cross-pipeline reuse | ❌ | ✅ | ❌ |

**Method A selected** because: minimal changes, automatic LangGraph persistence, highest performance, best reliability.

## Stories

### Story 37.1: Add docs_context_summary to PipelineState TypedDict
**File**: `autoBMAD/docuswarm/pipeline/state.py`  
**Changes**:
```python
class PipelineState(TypedDict):
    """Main pipeline state schema for LangGraph StateGraph."""
    
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]
    questions: dict[str, list[dict[str, Any]]]
    evaluations: dict[str, dict[str, Any]]
    node_iterations: dict[str, int]
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None
    status: str
    error: dict[str, Any] | None
    shared_context: dict[str, Any]
    
    # NEW: Document summary cache - set once at pipeline start, read-only after
    docs_context_summary: list[dict[str, Any]]
```

**Acceptance Criteria**:
- [ ] `docs_context_summary` field added to `PipelineState` TypedDict
- [ ] Field type is `list[dict[str, Any]]`
- [ ] Existing pipeline state serialization/deserialization still works
- [ ] Unit test: `test_pipeline_state_with_docs_context.py`
- [ ] BasedPyright type checking passes (no new type errors)

### Story 37.2: Update create_initial_state() Function
**File**: `autoBMAD/docuswarm/pipeline/state.py`  
**Changes**:
```python
def create_initial_state(
    pipeline_id: str,
    subject_context: dict[str, Any],
    docs_context_summary: list[dict[str, Any]] | None = None,  # NEW parameter
) -> PipelineState:
    """Create an initial PipelineState with default values."""
    
    from autoBMAD.docuswarm.utils.session_ids import generate_session_id
    
    pipeline_session_id = generate_session_id(pipeline_id)
    
    return PipelineState(
        pipeline_id=pipeline_id,
        subject_context=subject_context,
        current_node=None,
        completed_nodes=[],
        deliverables={},
        questions={},
        evaluations={},
        node_iterations={},
        session_ids={"pipeline": pipeline_session_id},
        session_metadata={},
        current_node_session_id=None,
        status=PENDING,
        error=None,
        shared_context={},
        docs_context_summary=docs_context_summary or [],  # NEW field
    )
```

**Acceptance Criteria**:
- [ ] `create_initial_state()` accepts optional `docs_context_summary` parameter
- [ ] Default value is empty list `[]`
- [ ] All existing callers without the new parameter still work
- [ ] Unit test verifies correct initialization with and without summaries

### Story 37.3: Update PipelineAdapter for Summary Propagation
**File**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py`  
**Changes**:
```python
@staticmethod
def convert_pipeline_to_node_state(
    pipeline_state: PipelineState,
    node_id: str,
) -> NodeRunState:
    """Convert PipelineState to NodeRunState."""
    
    subject_context = pipeline_state.get("subject_context", {})
    docs_summary = pipeline_state.get("docs_context_summary", [])
    
    # Inject docs_context_summary into original_context so context_builder can find it
    if docs_summary:
        original_context = {
            **subject_context,
            "docs_context_summary": docs_summary,
        }
    else:
        original_context = subject_context
    
    context_file = serialize_context(original_context)
    
    node_run_state = NodeRunState(
        run_id=pipeline_state["pipeline_id"],
        pipeline_id=pipeline_state["pipeline_id"],
        node_id=node_id,
        context_file=context_file,
        # ... other existing fields ...
    )
    
    return node_run_state
```

**Acceptance Criteria**:
- [ ] `docs_context_summary` from PipelineState is injected into `original_context`
- [ ] When PipelineState has no summary, `original_context` is unchanged
- [ ] Serialized `context_file` includes the summary data
- [ ] Unit test: verify adapter correctly propagates summary

### Story 37.4: Update Context Builder to Use Cached Summary
**File**: `autoBMAD/docuswarm/node_execution/context_builder.py`  
**Changes**:
```python
def build(
    self,
    pipeline_id: str,
    node_id: str,
    original_context: dict[str, Any],
    chained_deliverables: list[dict[str, Any]] | None = None,
    shared_context: dict[str, Any] | None = None,
    iteration_feedback: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> NodeExecutionContext:
    """Build NodeExecutionContext with runtime fields only."""
    
    node_config = self.loader.load(node_id)
    
    docs_context: list[dict[str, Any]] = []
    
    # NEW: Prioritize cached summary (injected by PipelineAdapter)
    if "docs_context_summary" in original_context:
        docs_context = original_context["docs_context_summary"]
        logger.info(
            "using_cached_docs_summary",
            node_id=node_id,
            count=len(docs_context),
        )
    elif repo_root is not None:
        # Fallback: rare case when no cache available (pipeline recovery, etc.)
        docs_context = self._resolve_reference_docs(original_context, node_id, repo_root)
        logger.warning(
            "missing_cached_docs_summary_using_fallback",
            node_id=node_id,
            count=len(docs_context),
        )
    
    return NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=node_id,
        node_name=node_config.name,
        node_order=node_config.sequence,
        original_context=original_context,
        chained_deliverables=chained_deliverables or [],
        shared_context=shared_context or {},
        iteration_feedback=iteration_feedback,
        docs_context=docs_context,
    )
```

**Acceptance Criteria**:
- [ ] Builder reads from `original_context["docs_context_summary"]` when present
- [ ] Falls back to `_resolve_reference_docs()` when cache missing (with warning log)
- [ ] `_resolve_reference_docs()` method is PRESERVED (not deleted)
- [ ] Original caching behavior not changed for non-summary case
- [ ] Unit tests: cache hit case, cache miss fallback case

### Story 37.5: Update graph.py to Pass Summary to NodeRunState
**File**: `autoBMAD/docuswarm/pipeline/graph.py`  
**Changes**:
- In `_create_integrated_node_executor()`, extract `docs_context_summary` from pipeline state
- Pass it through to the `PipelineAdapter.convert_pipeline_to_node_state()` call

**Acceptance Criteria**:
- [ ] `docs_context_summary` is correctly extracted from LangGraph state
- [ ] Passed to PipelineAdapter for node state conversion
- [ ] Does not break existing graph execution flow

### Story 37.6: Support Pipeline Resume with Cached Summaries
**File**: `autoBMAD/docuswarm/pipeline/orchestrator.py`  
**Changes**:
- In `resume_pipeline()`, verify `docs_context_summary` is present in checkpoint state
- If missing: log warning that fallback will be used
- Document the recovery behavior in code comments

**Acceptance Criteria**:
- [ ] Resume correctly restores `docs_context_summary` from LangGraph checkpoint
- [ ] Warning logged when summary missing from checkpoint
- [ ] No error thrown when summary missing (graceful fallback)
- [ ] Integration test: pipeline resume preserves summary cache

### Story 37.7: Integration Tests for docs_context Persistence
**Files**:
- `tests/test_pipeline_state_with_docs_context.py` (new)
- `tests/test_graph_with_docs_context_cache.py` (new)
- `tests/test_context_builder_cached.py` (new)
- `tests/test_pipeline_resume_with_cache.py` (new)
- `tests/test_e2e_docs_context_cache.py` (new)

**Key Test Cases**:
- `test_pipeline_state_serialization_with_docs_context()` - state serializes correctly
- `test_docs_context_propagated_to_all_nodes()` - all 5 nodes receive same cache
- `test_context_builder_uses_cache_not_disk()` - verify no disk reads when cache present
- `test_context_builder_fallback_on_missing_cache()` - fallback triggers correctly
- `test_pipeline_resume_restores_docs_context()` - resume recovers from checkpoint
- `test_e2e_pipeline_with_docs_context_cache()` - full pipeline end-to-end

**Acceptance Criteria**:
- [ ] All 6 test cases pass
- [ ] Performance: node execution time unchanged (uses cache)
- [ ] docs_context built only once per pipeline (not 5 times)
- [ ] Pipeline resume correctly restores cache

## Performance Targets

| Metric | Current | Target |
|--------|---------|--------|
| docs_context build count | 5 per pipeline | 1 per pipeline |
| Node execution overhead | ~500ms per node | < 10ms per node |
| Total pipeline time reduction | 0 | ~2.5 seconds |
| Context Builder call time | ~500ms | < 10ms |
| Cache hit rate | 0% | > 95% |

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| PipelineState becomes larger | Low | Summaries are compact JSON, not raw docs |
| Backward compatibility (old pipelines without field) | Low | `dict.get("docs_context_summary", [])` returns empty list |
| Cache stale (doc changed mid-pipeline) | Low | Single pipeline lifecycle - no mid-run changes |
| Pipeline resume cache missing | Medium | Fallback to re-processing; log warning |
| LangGraph checkpoint format change | Low | Monitor SDK changelog; maintain compat wrapper |

## Implementation Phases

### Phase 1: State Schema (1 hour)
- Story 37.1: Add `docs_context_summary` to `PipelineState`
- Story 37.2: Update `create_initial_state()`
- Unit test: state serialization/deserialization

### Phase 2: Pipeline Integration (2 hours)
- Story 37.3: Update `PipelineAdapter`
- Story 37.5: Update `graph.py`
- Story 37.6: Update `resume_pipeline()`
- Integration test: pipeline with summaries

### Phase 3: Context Builder Optimization (1 hour)
- Story 37.4: Update `context_builder.build()`
- Unit test: cache hit and miss cases

### Phase 4: Testing (2 hours)
- Story 37.7: Complete test suite
- Performance benchmarks
- Verify 5x reduction in docs_context builds

## Files Changed

| File | Change Type | Priority |
|------|------------|---------|
| `autoBMAD/docuswarm/pipeline/state.py` | Extend | P0 |
| `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` | Update | P0 |
| `autoBMAD/docuswarm/node_execution/context_builder.py` | Update | P0 |
| `autoBMAD/docuswarm/pipeline/graph.py` | Update | P1 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Update | P1 |
| `tests/test_pipeline_state_with_docs_context.py` | New | P0 |
| `tests/test_graph_with_docs_context_cache.py` | New | P1 |
| `tests/test_context_builder_cached.py` | New | P0 |
| `tests/test_pipeline_resume_with_cache.py` | New | P1 |
| `tests/test_e2e_docs_context_cache.py` | New | P1 |

## Dependency Note

This epic (EPIC-37) provides the **persistence layer** for docs_context summaries.  
EPIC-36 provides the **generation layer** (SummaryAgent creates the summaries).  
These two epics should be implemented together, with EPIC-37 first (add the field) then EPIC-36 (generate the data).

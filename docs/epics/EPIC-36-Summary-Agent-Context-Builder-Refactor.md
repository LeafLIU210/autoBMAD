# EPIC-36: Summary Agent Design and Context Builder Refactoring

**Epic ID**: EPIC-36  
**Source Research**: `docs/research/docuswarm-deep-reform/06-summary-agent-design.md`  
**Recommended Solution**: Pre-Pipeline Summary Agent (Option 1) + PipelineState caching (Option 3) hybrid  
**Priority**: P1  
**Estimated Effort**: ~8 hours (~1 day)  
**Status**: Ready for Implementation  
**Depends On**: EPIC-37 (PipelineState docs_context_summary field must be added first)

---

## Overview

Currently, each of the 5 nodes independently builds `docs_context` by recursively scanning `docs/` directory and reading reference files. This causes ~2.5 seconds of redundant processing per pipeline (5 × ~500ms). This epic introduces a **Summary Agent** that runs once before the pipeline starts, generates structured LLM summaries for all referenced documents, and caches them in `PipelineState` for all nodes to reuse.

## Problem Statement

**Current Flow** (repeated 5 times):
```
analyst node → context_builder reads docs/ → truncates to 10k chars → injects to prompt
pm node → context_builder reads docs/ AGAIN → truncates to 10k chars → injects to prompt
... (repeated 5 times)
```

**Issues**:
1. **Repeated computation**: `_resolve_reference_docs()` runs 5 times per pipeline
2. **Performance waste**: Recursive directory scan (~500ms) × 5 = 2.5s wasted
3. **No caching**: Even unchanged documents are re-processed
4. **No LLM participation**: Raw truncation loses context and understanding
5. **Poor quality**: 10k char hard truncation may cut sentences mid-way

## Goals

1. Create `SummaryAgent` class that pre-processes referenced documents
2. Integrate Summary Agent into `HybridOrchestrator.start_pipeline()`
3. Refactor `context_builder.build()` to use cached summaries from `PipelineState`
4. Implement graceful fallback to raw document processing when cache missing
5. Support pipeline resume with cached summaries

## Recommended Solution: Pre-Pipeline + PipelineState Caching

**Flow**:
```
HybridOrchestrator.start_pipeline()
    ↓
[NEW] SummaryAgent.summarize_context(subject_context)
    ↓ reads original_context to find referenced filenames
    ↓ reads each file completely (no truncation)
    ↓ calls LLM to generate structured JSON summary per file
    ↓ returns list[DocumentSummary]
    ↓
initial_state["docs_context_summary"] = docs_summary   [cached]
    ↓
graph.ainvoke(initial_state)
    ↓
Each node: context_builder reads from cache (no re-processing)
```

## Stories

### Story 36.1: Create SummaryAgent Class
**File**: `autoBMAD/docuswarm/agents/summary.py` (new file)  
**Key Classes**:
```python
@dataclass
class DocumentSummary:
    filename: str
    path: str
    size_bytes: int
    summary: str           # 2-5 sentence core summary
    key_points: list[str]  # 3-7 key points
    structure: dict[str, Any]  # {sections, concepts}
    truncated: bool
    llm_tokens_used: int

class SummaryAgent:
    async def summarize_context(
        self,
        original_context: dict[str, Any],
    ) -> list[DocumentSummary]:
        """Main entry: generate summaries for all referenced documents"""
```

**LLM Prompt Design**:
- System: "You are a professional technical document analyst"
- User: provide file content + request structured JSON output
- JSON schema: `{summary, key_points, structure: {sections, concepts}}`
- Temperature: 0.3 (deterministic output)
- Max tokens: 1000 per document

**Processing Strategy**:
- Critical files (containing "requirement") → sequential processing
- Normal files → concurrent batch (max 3 simultaneous)
- Timeout: 30 seconds per document
- Max retries: 2

**Acceptance Criteria**:
- [ ] `SummaryAgent` class exists with `summarize_context()` method
- [ ] `DocumentSummary` dataclass with all required fields
- [ ] LLM generates valid JSON output for test documents
- [ ] Batch processing with max 3 concurrent LLM calls
- [ ] Graceful error handling: returns None for failed files
- [ ] Unit tests: `test_summary_agent.py`

### Story 36.2: Create Summary Agent Configuration
**File**: `autoBMAD/docuswarm/config/summary_agent.yaml` (new file)  
**Content**:
```yaml
agent_id: _summary
name: Document Summary Agent
description: Generates structured summaries of referenced documents

type: summary
mode: instant
temperature: 0.3
max_tokens: 1000

tools:
  allowed_builtin_tools:
    - ListDocuments
    - ReadDocument

performance:
  max_concurrent_documents: 3
  batch_size: 5
  timeout_per_document_seconds: 30
  max_retries: 2

caching:
  enable: true
  ttl_hours: 24
  invalidate_on_doc_change: true
```

**Acceptance Criteria**:
- [ ] YAML file exists and validates
- [ ] Config values are read correctly by SummaryAgent
- [ ] Timeout and concurrency limits are enforced

### Story 36.3: Integrate SummaryAgent into HybridOrchestrator
**File**: `autoBMAD/docuswarm/pipeline/orchestrator.py`  
**Changes**:
```python
async def start_pipeline(self, subject_context: dict, ...) -> str:
    # ... existing validation ...
    
    # NEW: Generate document summaries before pipeline starts
    docs_summary = await self._summarize_referenced_documents(
        subject_context=subject_context,
        repo_root=repo_root,
        session_manager=session_manager,
        timeout=120,
    )
    
    # Create initial_state with summaries injected
    initial_state = create_initial_state(
        final_pipeline_id,
        subject_context,
        docs_context_summary=docs_summary,  # NEW parameter
    )
    
    result = await graph.ainvoke(initial_state, config)
    return final_pipeline_id

async def _summarize_referenced_documents(
    self,
    subject_context: dict,
    repo_root: Path,
    session_manager: SessionManager,
    timeout: int = 120,
) -> list[dict]:
    """Run SummaryAgent with timeout"""
    summary_agent = SummaryAgent(
        config=self._config,
        session_manager=session_manager,
        project_root=repo_root,
    )
    result = await asyncio.wait_for(
        summary_agent.summarize_context(subject_context),
        timeout=timeout
    )
    return result
```

**Acceptance Criteria**:
- [ ] `start_pipeline()` calls `_summarize_referenced_documents()` before graph execution
- [ ] 120-second timeout prevents pipeline blocking
- [ ] On timeout/error: fallback to empty list (pipeline continues without summaries)
- [ ] Logging: `documents_summarized count=N total_tokens=N`
- [ ] Integration test: pipeline starts with pre-computed summaries

### Story 36.4: Refactor Context Builder to Use Cached Summaries
**File**: `autoBMAD/docuswarm/node_execution/context_builder.py`  
**Changes**:
```python
def build(self, ..., original_context, ...) -> NodeExecutionContext:
    docs_context: list[dict] = []
    
    # NEW: Check for cached summaries first
    if "docs_context_summary" in original_context:
        docs_context = original_context["docs_context_summary"]
        logger.info("using_cached_docs_summary", node_id=node_id, count=len(docs_context))
    elif repo_root is not None:
        # Fallback: use original processing (rare case)
        docs_context = self._resolve_reference_docs(original_context, node_id, repo_root)
        logger.warning("missing_cached_docs_summary_using_fallback", node_id=node_id)
    
    return NodeExecutionContext(..., docs_context=docs_context)
```

**Acceptance Criteria**:
- [ ] Context builder reads from cache when `docs_context_summary` exists in original_context
- [ ] Falls back to `_resolve_reference_docs()` when cache missing
- [ ] Fallback warning is logged
- [ ] `_resolve_reference_docs()` method is preserved (not deleted) for backward compat
- [ ] Unit test: `test_context_builder_with_cache.py`

### Story 36.5: Update PipelineAdapter to Propagate Summaries
**File**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py`  
**Changes**:
```python
@staticmethod
def convert_pipeline_to_node_state(pipeline_state, node_id) -> NodeRunState:
    subject_context = pipeline_state.get("subject_context", {})
    docs_summary = pipeline_state.get("docs_context_summary", [])
    
    # Inject summary into original_context for context_builder to find
    if docs_summary:
        original_context = {
            **subject_context,
            "docs_context_summary": docs_summary,
        }
    else:
        original_context = subject_context
    
    # Build node state with enriched context
    context_file = serialize_context(original_context)
    node_run_state = NodeRunState(
        context_file=context_file,
        # ... other fields ...
    )
    return node_run_state
```

**Acceptance Criteria**:
- [ ] `docs_context_summary` from PipelineState is injected into `original_context`
- [ ] Context file serialization includes summary data
- [ ] Unit test: verify summary propagation through adapter

### Story 36.6: Support Pipeline Resume with Cached Summaries
**File**: `autoBMAD/docuswarm/pipeline/orchestrator.py`  
**Changes**:
- In `resume_pipeline()`, check if checkpoint state has `docs_context_summary`
- If missing (e.g., older pipeline), attempt to restore from DB or regenerate
- Log warning if summary cannot be restored

**Acceptance Criteria**:
- [ ] Resume works correctly when `docs_context_summary` exists in checkpoint
- [ ] Resume falls back gracefully when summary missing
- [ ] Warning log when fallback is used

### Story 36.7: End-to-End Tests
**Files**: 
- `tests/test_summary_agent.py` (new)
- `tests/test_context_builder_with_cache.py` (new)
- `tests/test_orchestrator_with_summary.py` (new)

**Key Tests**:
- `test_summary_agent_generates_valid_json()` - LLM returns valid JSON summary
- `test_summary_agent_handles_large_file()` - large files summarized correctly
- `test_summary_agent_handles_missing_file()` - missing files return None gracefully
- `test_context_builder_uses_cache()` - builder reads from cache, not disk
- `test_context_builder_fallback()` - fallback when no cache
- `test_pipeline_with_summary_e2e()` - full pipeline with pre-computed summaries
- `test_pipeline_resume_with_summary()` - resume preserves summary cache

**Acceptance Criteria**:
- [ ] All 7 test cases pass
- [ ] Performance test: summary generation < 30 seconds
- [ ] Pipeline execution without summary cache falls back gracefully

## Performance Targets

| Metric | Target |
|--------|--------|
| Summary generation time | < 30 seconds per pipeline |
| Pipeline startup additional delay | < 5 seconds |
| Node execution time change | No increase (uses cache) |
| Summary accuracy | > 80% (manual review) |
| Referenced doc coverage | 100% (all mentioned files) |
| Document truncation rate | 0% (full documents processed) |

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| LLM timeout blocks pipeline startup | High | 120s timeout + fallback to empty list |
| Binary/corrupt document causes failure | High | LLM returns "unable to read" summary |
| Token explosion from many large docs | High | Max 3 concurrent; skip files >500kb |
| Summary quality low | Medium | Human review; add quality scoring |
| Cache consistency on doc change | Medium | File modification monitoring; manual refresh |
| Pipeline resume missing cache | Medium | Implement fallback to re-summarize |

## Implementation Phases

### Phase 1: Infrastructure (3 hours)
- Story 36.1: `SummaryAgent` class + `DocumentSummary` dataclass
- Story 36.2: `summary_agent.yaml` config file
- Unit tests for summary generation

### Phase 2: Pipeline Integration (2 hours)
- Story 36.5: `PipelineAdapter` summary propagation
- Story 36.3: `HybridOrchestrator` integration
- Story 36.6: Pipeline resume support

### Phase 3: Context Builder Optimization (1 hour)
- Story 36.4: `context_builder.build()` cache reading
- Fallback logic implementation

### Phase 4: Testing and Documentation (2 hours)
- Story 36.7: End-to-end tests
- Performance benchmarks
- Developer documentation

## Files Changed

| File | Change Type | Priority |
|------|------------|---------|
| `autoBMAD/docuswarm/agents/summary.py` | New | P0 |
| `autoBMAD/docuswarm/config/summary_agent.yaml` | New | P0 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Update | P0 |
| `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` | Update | P1 |
| `autoBMAD/docuswarm/node_execution/context_builder.py` | Update | P1 |
| `autoBMAD/docuswarm/agents/base.py` | Update | P1 |
| `tests/test_summary_agent.py` | New | P1 |
| `tests/test_context_builder_with_cache.py` | New | P1 |
| `tests/test_orchestrator_with_summary.py` | New | P1 |

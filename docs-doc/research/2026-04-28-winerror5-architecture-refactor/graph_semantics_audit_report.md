# LangGraph Node Completion Semantics Audit Report

**File**: `D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\pipeline\graph.py`
**Adapter logic correct**: ✅
**Graph override detected**: ❌ YES
**Finalizer blind complete**: ❌ YES

## Contradiction Scenarios
- Adapter correctly routes FAILED nodes to failed_nodes, but graph.py overrides by adding them to completed_nodes.
- Finalizer always marks COMPLETED even when failed_nodes present, creating status contradiction.

## Findings
### R2-001 — CRITICAL
**Category**: graph_completion_override
**Title**: graph.py unconditionally appends node to completed_nodes after adapter conversion

PipelineAdapter.convert_node_to_pipeline_state() already implements P0-F1 logic: only COMPLETED nodes enter completed_nodes. However, graph.py executor then runs 'if node_id not in result_state["completed_nodes"]: result_state["completed_nodes"] = ... + [node_id]' regardless of adapter result. This overwrites the adapter's failure semantics.

**Evidence**:
- `graph.py lines ~146-152: unconditional completed_nodes append after try/except`
- `pipeline_adapter.py lines ~322-337: conditional logic based on node_status == COMPLETED`

**Recommendation**: Remove or conditionally gate the post-adapter completed_nodes append in graph.py.

### R3-001 — CRITICAL
**Category**: finalizer_blind_complete
**Title**: finalize_pipeline_state() unconditionally sets status=COMPLETED

finalize_pipeline_state() in state.py sets status=COMPLETED without inspecting failed_nodes or error fields. Although orchestrator._determine_final_status() later corrects DB status to failed, the LangGraph checkpoint and returned result still carry the contradictory status=COMPLETED. This pollutes resume, export, and debugging paths.

**Evidence**:
- `state.py finalize_pipeline_state() line ~310: result['status'] = COMPLETED`
- `orchestrator.py _determine_final_status() lines ~153-169: post-hoc correction`

**Recommendation**: finalize_pipeline_state() must inspect failed_nodes/error before setting COMPLETED.

# SDK Tool Dispatch Failure: create_deliverable Not Registered

**Date**: 2026-04-06
**Iteration**: 2 (Ralph Wiggum Loop)
**Severity**: P0 - Pipeline Blocked
**Status**: Root Cause Confirmed

---

## 1. Symptom Summary

Second pipeline run (with 300s timeout fix applied) produced:

```
evaluator_agent_failed error=Deliverable file not found: docs/calc-one-plus-one/analyst-report.md
```

Key observations:
- Independent Agent received 20 messages in 33 seconds
- Then 60-second tool execution gap (agent attempting tool call)
- 207-second complete silence from `receive_messages()`
- Timeout at 300s
- Output directory `output/<pipeline_id>/` was **empty** for ALL pipeline runs
- ThinkingBlock leak was FIXED (no more `llm_returned_plain_text_fallback`)

---

## 2. Root Causes

### RC-4: `independent_agent.yaml` uses kimi-agent-sdk format incompatible with claude-agent-sdk

**File**: `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`

```yaml
agent:
  extend: default
  tools:
    - "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "autoBMAD.docuswarm.tools.update_context:UpdateContextTool"
    - "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool"
```

This `module.path:ClassName` format is **kimi-agent-sdk specific**. After TDD-05 SDK migration to claude-agent-sdk, this format is NOT supported. The file is passed to `ClaudeAgentOptions.tools` but the SDK cannot parse it.

**Code trace**:
```
session_manager.py:184  options_dict["tools"] = [str(self._agent_file)]
session_manager.py:320  options.tools = [str(effective_agent_file)]
```

### RC-5: `create_deliverable` is not registered as MCP server tool

`NodeToolFilter.create_mcp_servers()` only creates:
- `docuswarm-files-{node_id}` - file read server
- `docuswarm-search-{node_id}` - search server

No MCP server exists for `create_deliverable`. The tool is defined as a Python class (`CreateDeliverableTool`) but never registered with claude-agent-sdk as an MCP tool.

### RC-6: `allowed_tools` whitelist blocks `create_deliverable`

`NodeToolFilter.get_allowed_tools()` returns:
```python
["Read", "Glob",
 "mcp__docuswarm-files-analyst__read_document",
 "mcp__docuswarm-files-analyst__list_documents",
 "mcp__docuswarm-search-analyst__grep_search",
 "mcp__docuswarm-search-analyst__glob_search"]
```

`create_deliverable` is NOT in this list. Even if the tool were registered, the SDK would block it.

### RC-7: SDK agent gets stuck when dispatching unregistered tool

1. System prompt tells agent: "Use the 'create_deliverable' tool"
2. Agent attempts `tool_use` for `create_deliverable`
3. SDK can't find the tool in its registry
4. Agent enters a stuck state (207s silence in `receive_messages()`)
5. Timeout at 300s
6. File is never written to disk

---

## 3. Impact Chain

```
independent_agent.yaml (kimi format) ──→ SDK ignores/fails silently
                                         ↓
create_deliverable not in MCP registry ──→ Agent tool_use dispatched to void
                                           ↓
207s silence in receive_messages() ───────→ prompt_timeout at 300s
                                            ↓
Output directory empty ──────────────────→ Evaluator: FileNotFoundError
                                            ↓
                                    node_execution_failed (EvaluatorExecutionError)
```

---

## 4. Evidence

### Log Timeline (Second Run)
```
18:04:07.430 - messages 1-18 (33 seconds, normal)
18:04:40.xxx - messages 19 (60s gap - tool call attempt)
18:05:41.xxx - message 20 (last message)
18:05:41 → 18:09:08 = 207 seconds of SILENCE
18:09:08.xxx - prompt_timeout (300s limit reached)
```

### Empty Output Directories
```
output/pipeline-20260406-175620/ - EMPTY
output/pipeline-20260406-180044/ - EMPTY (multiple runs, all empty)
```

### Node Configuration
`autoBMAD/nodes/analyst/node.yaml` tools section:
```yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]  # No Write, no create_deliverable
```

---

## 5. Fix Recommendation

Create `create_deliverable` as an MCP server tool following the existing `file_tools_sdk.py` / `search_tools_sdk.py` pattern:

1. **New file**: `create_deliverable_sdk.py` with `create_deliverable_server()` factory
2. **Update**: `NodeToolFilter` to register deliverable MCP server and add to allowed_tools
3. **Remove**: kimi-agent-sdk `independent_agent.yaml` from `options.tools`
4. **Update**: System prompt to reference correct MCP tool name

See: `docs/solution/TDD-07-SDK-Tool-Dispatch-Fix.md`

# TDD-07: SDK Tool Dispatch Fix - create_deliverable as MCP Server

**Date**: 2026-04-06
**Root Cause**: docs/research/2026-04-06-sdk-tool-dispatch-root-cause.md
**Priority**: P0 - Pipeline Blocked

---

## 1. Problem Statement

After TDD-05 SDK migration (kimi -> claude), `create_deliverable` Python tool is never
registered with claude-agent-sdk. The agent attempts to call it, SDK gets stuck for 207s,
files are never written, and Evaluator fails with `FileNotFoundError`.

## 2. Solution Overview

Convert `create_deliverable` from a kimi-agent-sdk Python tool to a claude-agent-sdk MCP
server tool, following the existing pattern of `file_tools_sdk.py` and `search_tools_sdk.py`.

## 3. Implementation Steps

### Step 1: Create `create_deliverable_sdk.py` (New File)

**File**: `autoBMAD/docuswarm/tools/create_deliverable_sdk.py`

Create MCP server factory `create_deliverable_server(output_dir, node_id)` using:
- `claude_agent_sdk.create_sdk_mcp_server` and `@tool` decorator
- Tool: `create_deliverable(title, content, metadata)` -> writes file, returns metadata
- Reuses `_slugify_filename`, `_compute_sha256`, `_count_words`, `_extract_section_index`

### Step 2: Update `NodeToolFilter` (Edit)

**File**: `autoBMAD/docuswarm/llm/tool_filter.py`

- Add `output_dir: str | None = None` parameter to `__init__` and `from_node_config`
- Add `DELIVERABLE_SERVER_NAME_FORMAT = "docuswarm-deliverable-{node_id}"`
- In `create_mcp_servers()`: Create deliverable server when `output_dir` is set
- In `get_allowed_tools()`: Add deliverable MCP tool name

### Step 3: Update `SessionManager._create_options()` (Edit)

**File**: `autoBMAD/docuswarm/llm/session_manager.py`

- Remove `options_dict["tools"] = [str(self._agent_file)]` (kimi-agent-sdk format)
- Remove `options.tools = [str(effective_agent_file)]` override in `create_session()`
- Pass `output_dir=str(self._output_dir)` to `NodeToolFilter` constructor

### Step 4: Update System Prompt (Edit)

**File**: `autoBMAD/docuswarm/prompts/contract_builder.py`

- Update `_build_instructions_section()` to accept `node_id` parameter
- Generate correct MCP tool name: `mcp__docuswarm-deliverable-{node_id}__create_deliverable`
- Update tool reference in instructions

### Step 5: Update `independent.py` (Edit)

**File**: `autoBMAD/docuswarm/agents/independent.py`

- In `_format_system_prompt()`: Update tool name to MCP format
- Remove `self._agent_file` from being passed to `SessionManager` as tool config

## 4. Test Cases

### Test File: `tests/test_tdd07_sdk_tool_dispatch.py`

```python
# T1: create_deliverable_server creates valid MCP server config
# T2: Deliverable tool writes file and returns metadata with file_path and sha256
# T3: NodeToolFilter includes deliverable MCP tool in allowed_tools
# T4: NodeToolFilter creates deliverable MCP server when output_dir is set
# T5: SessionManager._create_options() does NOT include agent_file in options.tools
# T6: System prompt contains correct MCP tool name
# T7: _slugify_filename produces correct filenames
# T8: _compute_sha256 produces correct hash
```

## 5. Acceptance Criteria

- [ ] `create_deliverable` available as MCP server tool in SDK agent mode
- [ ] Files written to `output/<pipeline_id>/` directory
- [ ] Evaluator receives valid `file_path` pointing to existing file
- [ ] `independent_agent.yaml` no longer passed to `options.tools`
- [ ] All 8 tests pass
- [ ] `ruff check` passes
- [ ] Pipeline runs without `evaluator_agent_failed` error

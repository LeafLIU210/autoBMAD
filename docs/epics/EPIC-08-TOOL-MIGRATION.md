> **⚠️ 已更新**: 本 Epic 已更新为使用 claude-agent-sdk + Kimi Code API 方案。工具调用使用标准 Tool Use Block 模式。

# Epic 8: Tool Migration to Standard Tool Use Block

**Epic ID**: EPIC-08  
**Version**: 2.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 2 (Tool Migration)

---

## 1. Epic Overview

### 1.1 Summary

Migrate all DocuSwarm custom tools from manual JSON Schema definitions to claude-agent-sdk's standard Tool Use Block format. This includes rewriting `create_deliverable` and `update_context` tools as standard tool definitions compatible with Claude SDK, and removing legacy JSON Schema tool definitions. After this epic, the SDK handles tool calls via standard Tool Use Block pattern.

### 1.2 Business Value

- **Type Safety**: Standard tool parameter validation
- **Standard Pattern**: Uses Claude SDK's native Tool Use Block format
- **Maintainability**: Tool definitions are clear and consistent
- **Error Handling**: Standard SDK error handling patterns
- **Reduced Code**: Eliminate manual `tool_calls` parsing and result construction

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| CreateDeliverableTool | Standard format, SDK-compatible |
| UpdateContextTool | Standard format, SDK-compatible |
| Tool registration | Via `execute_with_tools()` method |
| Legacy removal | JSON Schema tool definitions removed |
| End-to-end | IndependentAgent creates deliverable via Tool Use Block |

### 1.4 Dependencies

- **Requires**: Epic 7 (Core Layer Transformation) completed
- **Requires**: Epic 16 (SDK Wrapper) completed for SessionManager
- **Blocks**: Epic 9 (Session & Cancellation) — tools must work before advanced session features

### 1.5 Source Reference

Based on: `docs/epics/EPIC-16-SDK-WRAPPER.md` - claude-agent-sdk integration

---

## 2. Architecture Context

### 2.1 Tool System Transformation

```
Before (Manual JSON Schema):
  Agent → define JSON Schema → pass to KimiClient.chat(tools=[...])
       → parse tool_calls from response → execute manually → construct result message

After (Standard Tool Use Block):
  Agent → define standard tool dict → pass to SessionManager.execute_with_tools()
       → SDK handles Tool Use Block → execute callback → return result
```

### 2.2 Tool Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tool Layer (Epic 8)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Standard Tool Definitions                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  CreateDeliverableTool                                     │ │
│  │  ├── Tool definition (dict with name, description,         │ │
│  │  │                    input_schema)                        │ │
│  │  └── Callback function → returns tool result              │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  UpdateContextTool                                         │ │
│  │  ├── Tool definition (dict with name, description,         │ │
│  │  │                    input_schema)                        │ │
│  │  └── Callback function → returns tool result              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Tool Registration                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  SessionManager.execute_with_tools(                        │ │
│  │      prompt="...",                                          │ │
│  │      tools=[create_deliverable_tool, update_context_tool]  │ │
│  │  )                                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Key Files

| File | Operation | Purpose |
|------|-----------|---------|
| `docuswarm/tools/__init__.py` | **NEW** | Tools package initialization |
| `docuswarm/tools/create_deliverable.py` | **NEW** | CreateDeliverableTool (standard format) |
| `docuswarm/tools/update_context.py` | **NEW** | UpdateContextTool (standard format) |
| `docuswarm/llm/tools.py` | **REMOVE** | Legacy JSON Schema definitions |
| `docuswarm/agents/independent.py` | **MODIFY** | Use execute_with_tools() |

---

## 3. User Stories

### Story 8.1: CreateDeliverableTool Implementation

**ID**: US-8.1  
**As a** developer  
**I want to** have a standard CreateDeliverableTool  
**So that** the SDK can handle deliverable creation via Tool Use Block

**Acceptance Criteria**:
- [ ] Tool definition dict with name, description, input_schema
- [ ] Callback function saves deliverable via output handler
- [ ] Returns tool result on success with confirmation message
- [ ] Returns error result on failure with error details
- [ ] Output handler injected via constructor/closure

**Technical Tasks**:
1. Create `docuswarm/tools/__init__.py`
2. Create `docuswarm/tools/create_deliverable.py`
3. Implement tool definition dict
4. Implement callback function
5. Write unit tests with mock output handler

**Implementation**:
```python
from typing import Any

# Tool definition
CREATE_DELIVERABLE_TOOL = {
    "name": "create_deliverable",
    "description": "Create a node deliverable document with title, content, and metadata",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Deliverable title"
            },
            "content": {
                "type": "string",
                "description": "Deliverable content (Markdown)"
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata",
                "default": {}
            }
        },
        "required": ["title", "content"]
    }
}

# Callback function
async def create_deliverable_callback(
    output_handler,
    params: dict[str, Any]
) -> dict[str, Any]:
    """Callback for create_deliverable tool."""
    try:
        output_handler.save_deliverable(
            title=params["title"],
            content=params["content"],
            metadata=params.get("metadata", {})
        )
        return {
            "success": True,
            "message": f"Deliverable '{params['title']}' created successfully"
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "message": "Failed to create deliverable"
        }
```

**Definition of Done**:
- Tool definition importable and usable
- Validation works for all parameter types
- Success/error results returned correctly
- Unit tests pass with mock output handler

---

### Story 8.2: UpdateContextTool Implementation

**ID**: US-8.2  
**As a** developer  
**I want to** have a standard UpdateContextTool  
**So that** the SDK can handle context updates via Tool Use Block

**Acceptance Criteria**:
- [ ] Tool definition dict with name, description, input_schema
- [ ] `operation` field supports "set", "append", "remove"
- [ ] Callback function updates shared context via context store
- [ ] Returns success/error result appropriately
- [ ] Context store injected via constructor/closure

**Technical Tasks**:
1. Create `docuswarm/tools/update_context.py`
2. Implement tool definition dict
3. Implement callback function
4. Write unit tests with mock context store

**Implementation**:
```python
from typing import Any, Literal

# Tool definition
UPDATE_CONTEXT_TOOL = {
    "name": "update_context",
    "description": "Update shared execution context with key-value pairs",
    "input_schema": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Context key name"
            },
            "value": {
                "type": "object",
                "description": "Value to set"
            },
            "operation": {
                "type": "string",
                "enum": ["set", "append", "remove"],
                "description": "Operation type",
                "default": "set"
            }
        },
        "required": ["key", "value"]
    }
}

# Callback function
async def update_context_callback(
    context_store,
    params: dict[str, Any]
) -> dict[str, Any]:
    """Callback for update_context tool."""
    try:
        operation = params.get("operation", "set")
        context_store.update(
            key=params["key"],
            value=params["value"],
            operation=operation
        )
        return {
            "success": True,
            "message": f"Context '{params['key']}' updated ({operation})"
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "message": "Context update failed"
        }
```

**Definition of Done**:
- Tool definition importable and usable
- All three operation types (set, append, remove) work
- Validation enforces enum type
- Unit tests pass

---

### Story 8.3: Tool Registration with SessionManager

**ID**: US-8.3  
**As a** developer  
**I want to** register tools via SessionManager.execute_with_tools()  
**So that** the SDK knows which tools are available for the agent

**Acceptance Criteria**:
- [ ] Tools passed to `execute_with_tools()` method
- [ ] Tool definitions formatted for Claude SDK compatibility
- [ ] SDK successfully processes Tool Use Block requests
- [ ] Evaluator agent calls without tools (empty list)

**Technical Tasks**:
1. Update tool definitions to Claude SDK format
2. Modify IndependentAgent to use `execute_with_tools()`
3. Verify SDK processes tools correctly
4. Write integration test

**Tool Registration**:
```python
# In IndependentAgent
from docuswarm.tools.create_deliverable import (
    CREATE_DELIVERABLE_TOOL, create_deliverable_callback
)
from docuswarm.tools.update_context import (
    UPDATE_CONTEXT_TOOL, update_context_callback
)

async def _call_llm_with_tools(self, prompt: str) -> SDKResult:
    """Call LLM with tool support."""
    tools = [
        {
            "definition": CREATE_DELIVERABLE_TOOL,
            "callback": lambda p: create_deliverable_callback(
                self.output_handler, p
            )
        },
        {
            "definition": UPDATE_CONTEXT_TOOL,
            "callback": lambda p: update_context_callback(
                self.context_store, p
            )
        }
    ]
    
    return await self.session_manager.execute_with_tools(
        prompt=prompt,
        tools=tools,
        agent_name="independent_agent"
    )
```

**Definition of Done**:
- Tools passed correctly to execute_with_tools()
- SDK recognizes and processes tools
- Tool results returned in conversation flow
- Integration test verifies tool availability

---

### Story 8.4: Remove Manual Tool Parsing from IndependentAgent

**ID**: US-8.4  
**As a** developer  
**I want to** remove manual tool_calls parsing from IndependentAgent  
**So that** the SDK handles tool dispatch entirely via Tool Use Block

**Acceptance Criteria**:
- [ ] Manual `tool_calls` response parsing removed
- [ ] Manual tool execution logic removed
- [ ] Manual tool result message construction removed
- [ ] Tool dispatch handled by SDK via Tool Use Block
- [ ] IndependentAgent processes SDKResult from SessionManager

**Technical Tasks**:
1. Remove `_parse_tool_calls()` method from IndependentAgent
2. Remove `_execute_tool()` method
3. Remove `_construct_tool_result_message()` method
4. Update `_call_llm()` to use `execute_with_tools()`
5. Update unit tests

**Before/After**:
```python
# Before: Manual tool handling
async def _call_llm(self, ...):
    response = await self.llm.chat(messages, tools=DOCUSWARM_TOOLS)
    if response.has_tool_calls:
        for tool_call in response.tool_calls:
            result = self._execute_tool(tool_call)
            # ... manual result handling

# After: SDK Tool Use Block handling
async def _call_llm(self, ...):
    result = await self.session_manager.execute_with_tools(
        prompt=user_message,
        tools=self._get_tools(),
        agent_name="independent_agent"
    )
    # SDK handles all tool calls via Tool Use Block
    if result.success:
        self._process_result(result)
```

**Definition of Done**:
- No manual tool parsing code remains in IndependentAgent
- SDK handles all tool calls automatically
- Agent processes SDKResult directly
- All tests updated and passing

---

### Story 8.5: Remove Legacy JSON Schema Tool Definitions

**ID**: US-8.5  
**As a** developer  
**I want to** remove the legacy `docuswarm/llm/tools.py` JSON Schema definitions  
**So that** there is a single source of truth for tool definitions (standard format)

**Acceptance Criteria**:
- [ ] `docuswarm/llm/tools.py` removed or emptied
- [ ] All imports of `DOCUSWARM_TOOLS` removed
- [ ] No remaining references to legacy tool definitions
- [ ] Standard tool definitions are the sole source

**Technical Tasks**:
1. Search for all imports of `docuswarm.llm.tools`
2. Remove or update all import references
3. Remove `docuswarm/llm/tools.py` file
4. Verify no remaining references with grep
5. Run type checking and tests

**Definition of Done**:
- No legacy JSON Schema tool definitions in codebase
- All tool definitions use standard format
- `grep -r "DOCUSWARM_TOOLS" docuswarm/` returns no results
- Type checking passes
- All tests pass

---

### Story 8.6: Tool Use Block Integration Test

**ID**: US-8.6  
**As a** developer  
**I want to** verify that the SDK correctly handles Tool Use Block  
**So that** I have confidence the tool migration is complete and correct

**Acceptance Criteria**:
- [ ] Integration test creates session with tools
- [ ] Prompt triggers tool call (e.g., "Create a deliverable titled 'Test'")
- [ ] SDK processes Tool Use Block
- [ ] Tool callback receives correct parameters
- [ ] Tool result returned to SDK
- [ ] SDK includes tool result in conversation flow

**Technical Tasks**:
1. Create integration test in `tests/integration/test_tool_dispatch.py`
2. Set up mock output handler and context store
3. Create session with tools via execute_with_tools()
4. Send prompt that triggers tool call
5. Verify tool was called with correct parameters
6. Verify tool result was returned

**Definition of Done**:
- Integration test passes with real Kimi Code API
- Tool Use Block processing verified end-to-end
- No manual intervention in tool call flow
- Parameter validation works (invalid params handled)

---

## 4. Technical Specifications

### 4.1 New Modules

| Module | Location | Purpose |
|--------|----------|---------|
| `tools/__init__.py` | `docuswarm/tools/` | Package init, tool exports |
| `CreateDeliverableTool` | `docuswarm/tools/create_deliverable.py` | Deliverable creation tool |
| `UpdateContextTool` | `docuswarm/tools/update_context.py` | Context update tool |

### 4.2 Removed Modules

| Module | Location | Reason |
|--------|----------|--------|
| `tools.py` | `docuswarm/llm/tools.py` | Replaced by standard tool definitions |

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/` | 100% pass |
| Integration | `pytest tests/integration/test_tool_dispatch.py` | Pass |
| Legacy check | `grep -r "DOCUSWARM_TOOLS" docuswarm/` | No matches |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK Tool Use Block format differs from expected | Medium | High | Thorough integration testing with real API |
| Parameter validation incompatibility | Low | Medium | Test with SDK's exact parameter handling |
| Tool callback pattern changes | Low | Medium | Keep callback interface simple and standard |
| SessionManager execute_with_tools changes | Low | High | Verify interface compatibility with Epic 16 |

---

## 6. Definition of Done (Epic Level)

- [ ] All 6 stories completed and tested
- [ ] `CreateDeliverableTool` fully functional with standard format
- [ ] `UpdateContextTool` fully functional with standard format
- [ ] Tool registration via SessionManager.execute_with_tools() working
- [ ] Manual tool parsing removed from IndependentAgent
- [ ] Legacy JSON Schema definitions removed
- [ ] Tool Use Block verified end-to-end
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Unit test coverage ≥80% for tool modules

---

## 7. References

| Document | Location |
|----------|----------|
| SDK Migration Plan | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| Tool Migration Details | Epic 16 Section 3 |
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |
| Technology Stack | `docs/analyst/4_TECHNOLOGY_STACK.md` |

---

**Epic End**

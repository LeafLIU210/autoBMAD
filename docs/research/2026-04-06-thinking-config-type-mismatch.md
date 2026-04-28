# Research Report: ThinkingConfig Type Mismatch (RC-8)

**Date**: 2026-04-06
**Iteration**: 3
**Severity**: Critical - Blocks Evaluator Agent execution

## Summary

The Evaluator Agent fails with `'bool' object is not subscriptable` because
`session_manager.py` sets `options_dict["thinking"] = True` (a boolean), but the
Claude Agent SDK expects `ThinkingConfig | None` (a TypedDict).

## Error Log

```
[error] single_prompt_error  component=SessionManager  error='bool' object is not subscriptable  node_id=None
[error] llm_call_failed      agent=EvaluatorAgent  error=Single prompt failed: 'bool' object is not subscriptable
```

## Root Cause Analysis

### RC-8: ThinkingConfig Type Mismatch

**Location**: `autoBMAD/docuswarm/llm/session_manager.py` line 186-187

```python
if mode == "thinking":
    options_dict["thinking"] = True  # BUG: bool, not ThinkingConfig
```

**SDK Type Definition** (`claude_agent_sdk/types.py` lines 1146-1223):

```python
class ThinkingConfigAdaptive(TypedDict):
    type: Literal["adaptive"]

class ThinkingConfigEnabled(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int

class ThinkingConfigDisabled(TypedDict):
    type: Literal["disabled"]

ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled

@dataclass
class ClaudeAgentOptions:
    thinking: ThinkingConfig | None = None  # NOT bool
```

**Failure Mechanism**: The SDK internally accesses `options.thinking["type"]` to
determine the thinking mode. When `thinking=True`, Python raises
`TypeError: 'bool' object is not subscriptable`.

### Impact Chain

1. `EvaluatorAgent._call_llm_with_prompt()` calls `session_manager.single_prompt(mode="thinking")`
2. `SessionManager.single_prompt()` calls `self._create_options(mode="thinking")`
3. `_create_options()` sets `options_dict["thinking"] = True`
4. `query(prompt=prompt, options=options)` inside `single_prompt()` passes bool to SDK
5. SDK tries `thinking["type"]` -> `TypeError: 'bool' object is not subscriptable`
6. Caught by `except Exception as e:` in `single_prompt()`, logged as `single_prompt_error`
7. Re-raised as `LLMError`, caught by `EvaluatorAgent` as `EvaluationError`
8. `DualAgentNode` catches as `EvaluatorExecutionError`
9. Pipeline node execution fails

### Secondary Observation: Independent Agent Timeout (300s)

The Independent Agent for the analyst node still times out at 300 seconds with 25
messages received. This suggests the agent IS working (tools are dispatching) but
cannot complete within the timeout. This may resolve once the evaluator works and
the full loop functions correctly, or the timeout may need further adjustment.

## Affected Code Paths

| Component | File | Issue |
|-----------|------|-------|
| SessionManager._create_options() | session_manager.py:187 | `thinking=True` instead of ThinkingConfig |
| EvaluatorAgent._call_llm_with_prompt() | evaluator.py:382 | Calls single_prompt(mode="thinking") |
| SessionManager.single_prompt() | session_manager.py:496 | Passes bad options to query() |

## Recommended Fix

Change `options_dict["thinking"] = True` to use proper `ThinkingConfig`:

```python
if mode == "thinking":
    options_dict["thinking"] = {"type": "enabled", "budget_tokens": 10000}
```

Or use adaptive mode which lets the model decide:

```python
if mode == "thinking":
    options_dict["thinking"] = {"type": "adaptive"}
```

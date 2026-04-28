# TDD-08: ThinkingConfig Type Fix

**Date**: 2026-04-06
**Root Cause**: RC-8 (ThinkingConfig type mismatch)
**Priority**: P0 - Blocks Evaluator Agent

## Problem

`SessionManager._create_options()` sets `thinking=True` (boolean) when
`mode="thinking"`, but the Claude Agent SDK expects `ThinkingConfig` (TypedDict).
This causes `'bool' object is not subscriptable` when the SDK tries to access
`thinking["type"]`.

## Solution

### Step 1: Fix ThinkingConfig in _create_options()

**File**: `autoBMAD/docuswarm/llm/session_manager.py`

Change:
```python
if mode == "thinking":
    options_dict["thinking"] = True
```

To:
```python
if mode == "thinking":
    options_dict["thinking"] = {"type": "enabled", "budget_tokens": 10000}
```

Using `"enabled"` with explicit budget (10000 tokens) for evaluator thinking.
This matches the SDK's `ThinkingConfigEnabled` TypedDict format.

## Test Cases

### T-08-01: thinking mode produces ThinkingConfig dict
Verify `_create_options(mode="thinking")` sets `thinking` to a dict with
`type` key (not a boolean).

### T-08-02: agent mode does not set thinking
Verify `_create_options(mode="agent")` does not set `thinking` at all.

### T-08-03: thinking config has correct structure
Verify the thinking config dict has `type="enabled"` and integer `budget_tokens`.

### T-08-04: single_prompt with thinking mode succeeds
Verify `single_prompt(mode="thinking")` does not raise TypeError.

## Acceptance Criteria

- [ ] `_create_options(mode="thinking")` returns options with `thinking` as dict
- [ ] `_create_options(mode="agent")` does not set `thinking`
- [ ] Evaluator Agent's `single_prompt(mode="thinking")` no longer raises TypeError
- [ ] All existing TDD-06 and TDD-07 tests pass (regression)
- [ ] New TDD-08 tests pass

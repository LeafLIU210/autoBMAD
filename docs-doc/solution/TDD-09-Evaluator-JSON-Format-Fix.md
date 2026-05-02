# TDD-09: Evaluator JSON Output Format Fix

**Date**: 2026-04-06
**Root Causes**: RC-9 (missing JSON format), RC-10 (missing system_prompt)
**Priority**: P0 - Evaluator always fails to parse response

## Problem

The Evaluator's `execute_with_input()` path uses `contract_builder.render_evaluator_prompt()`
which lacks JSON output format instructions. The LLM responds in markdown instead of JSON.
Additionally, `single_prompt()` doesn't support passing a system prompt.

## Solution

### Step 1: Add output format section to contract builder

**File**: `autoBMAD/docuswarm/prompts/contract_builder.py`

Add `_build_evaluator_output_format()` that returns the JSON schema instruction.
Include it in `render_evaluator_prompt()`.

### Step 2: Add system_prompt to single_prompt()

**File**: `autoBMAD/docuswarm/llm/session_manager.py`

Add optional `system_prompt` parameter to `single_prompt()`.
Set `options.system_prompt` when provided.

### Step 3: Pass system_prompt from evaluator

**File**: `autoBMAD/docuswarm/agents/evaluator.py`

Update `_call_llm_with_prompt()` to pass system prompt to `single_prompt()`.

## Test Cases

### T-09-01: render_evaluator_prompt includes JSON format
### T-09-02: render_evaluator_prompt includes criterion_scores schema
### T-09-03: single_prompt accepts system_prompt parameter
### T-09-04: evaluator _call_llm_with_prompt passes system_prompt

## Acceptance Criteria

- [ ] Evaluator prompt includes JSON output format instructions
- [ ] single_prompt() supports system_prompt parameter
- [ ] All existing TDD-06/07/08 tests pass
- [ ] New TDD-09 tests pass

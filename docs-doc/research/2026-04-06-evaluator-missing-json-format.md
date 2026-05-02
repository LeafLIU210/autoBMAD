# Research Report: Evaluator Missing JSON Output Format (RC-9/RC-10)

**Date**: 2026-04-06
**Iteration**: 4
**Severity**: Critical - Evaluator cannot parse LLM response

## Summary

The Evaluator Agent's `execute_with_input()` path builds a prompt via
`contract_builder.render_evaluator_prompt()` that lacks JSON output format
instructions. The LLM responds in Chinese markdown instead of JSON, causing
`ResponseParseError: No JSON found in response`.

## Error Log

```
[error] response_parse_failed  agent=EvaluatorAgent  error=No JSON found in response  node_id=analyst
```

## Root Cause Analysis

### RC-9: Missing JSON Output Format in Evaluator Contract

**Location**: `autoBMAD/docuswarm/prompts/contract_builder.py` lines 427-435

`render_evaluator_prompt()` renders only:
1. task_section
2. criteria_section
3. context_section
4. deliverable_section

There is NO output format section telling the LLM to respond with JSON.

Compare with `evaluator.py:_format_evaluation_prompt()` (lines 244-294) which
DOES include `## Output Format` with JSON schema. But `execute_with_input()`
does NOT use `_format_evaluation_prompt()` - it uses the contract builder.

### RC-10: Missing System Prompt in single_prompt()

The evaluator calls `session_manager.single_prompt()` which passes the prompt
to `query(prompt=prompt, options=options)`. The `options` has no `system_prompt`
set, so the LLM has no role/persona context. The `_call_llm()` method has a
system prompt ("You are an expert evaluator agent...") but `_call_llm_with_prompt()`
does not.

### Impact Chain

1. `DualAgentNode.execute_with_context()` calls `evaluator_agent.execute_with_input()`
2. `execute_with_input()` calls `contract_builder.render_evaluator_prompt()` (NO JSON format)
3. Rendered prompt passed to `_call_llm_with_prompt()` (NO system prompt)
4. `single_prompt()` calls `query()` (NO system_prompt in options)
5. LLM responds in Chinese markdown (no JSON output instruction)
6. `_parse_response()` calls `extract_json()` which finds no JSON
7. Raises `ResponseParseError: No JSON found in response`
8. Caught by `DualAgentNode` as `EvaluatorExecutionError`

## Fix

1. Add `_build_evaluator_output_format()` method to contract_builder.py
2. Include it in `render_evaluator_prompt()`
3. Add `system_prompt` parameter to `single_prompt()` method
4. Have evaluator pass system prompt through `_call_llm_with_prompt()`

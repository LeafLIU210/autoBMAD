# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-08

### Breaking Changes

This version removes external timeout wrappers and simplifies the retry mechanism to eliminate Cancel Scope errors.

#### Removed External Timeouts

- **sdk_wrapper.py**: Removed `asyncio.wait_for` from `execute()` method
- **dev_agent.py**: Removed `asyncio.wait_for` and `asyncio.shield` from `_execute_single_claude_sdk()`
- **qa_agent.py**: Removed `asyncio.wait_for` and `asyncio.shield` from `_execute_ai_qa_review()`
- **sm_agent.py**: Removed `asyncio.wait_for` and `asyncio.shield` from `_execute_sdk_with_logging()`
- **sdk_session_manager.py**: Removed `asyncio.wait_for` from `execute_isolated()`
- **epic_driver.py**: Removed `asyncio.wait_for` from `process_story()` and `asyncio.shield` from `_process_story_impl()`

#### Simplified Retry Mechanism

- **dev_agent.py**: Removed retry loop in `_execute_single_claude_sdk()` method
- **qa_agent.py**: Removed retry loop in `execute()` method
- **sm_agent.py**: Removed retry loop in `_execute_claude_sdk()` method
- **sdk_session_manager.py**: Simplified `execute_isolated()` to single execution without retries

#### Deprecated Constants

All timeout constants in `epic_driver.py` are now set to `None`:
- `STORY_TIMEOUT`
- `CYCLE_TIMEOUT`
- `DEV_TIMEOUT`
- `QA_TIMEOUT`
- `SM_TIMEOUT`

### New Features

- **SDK Configuration**: Uses `max_turns` parameter in `ClaudeAgentOptions` for conversation limits instead of external timeouts
- **Simplified Architecture**: Reduced code complexity by removing nested retry mechanisms
- **Preserved Protection**: Epic-level `max_iterations` and Dev-QA cycle limits remain active

### Migration Guide

#### Before (v1.x)

```python
# External timeout wrapping
sdk = SafeClaudeSDK(prompt, options, timeout=1800.0)
result = await asyncio.wait_for(
    asyncio.shield(sdk.execute()),
    timeout=2800.0
)
```

#### After (v2.0)

```python
# No external timeout - use max_turns instead
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    max_turns=1000,  # Limit conversation turns
    cwd=str(Path.cwd())
)
sdk = SafeClaudeSDK(prompt, options, timeout=None)
result = await sdk.execute()
```

### Benefits

1. **Eliminated Cancel Scope Errors**: No more `RuntimeError: Attempted to exit cancel scope in a different task`
2. **Reduced Code Complexity**: Simplified from 5 retry layers to 2 (Epic and Dev-QA cycle)
3. **Better Maintainability**: Clearer control flow without nested shields and wait_for
4. **Preserved Functionality**: All core protection mechanisms (max_iterations, max_dev_qa_cycles) remain

### Testing

All modified files have been:
- ✅ Compiled successfully
- ✅ Imported without errors
- ✅ Verified for syntax correctness

### Files Modified

- `sdk_wrapper.py`
- `dev_agent.py`
- `qa_agent.py`
- `sm_agent.py`
- `sdk_session_manager.py`
- `epic_driver.py`

### References

- Based on analysis from `docs/evaluation/cancel-scope-error-analysis.md`
- Implementation follows design from `docs/evaluation/retry-mechanism-design.md`
- Follows Occam's Razor principle: remove unnecessary complexity

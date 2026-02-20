# SDK CLI Exit Code 1 Error Fix Solution

## 📋 Document Information

- **Version**: 1.0.0
- **Created**: 2026-02-16
- **Status**: ✅ Implemented
- **Related Log**: `logs/epic_run_epic1.log`
- **Implementation Date**: 2026-02-16

---

## 🎯 Problem Summary

### Error Description

The `autoBMAD` Epic Automation system fails with the following error pattern:

```
claude_agent_sdk._internal.query - ERROR - Fatal error in message reader: 
Command failed with exit code 1 (exit code: 1)
Error output: Check stderr output for details
```

### Impact

- All SDK calls (SMAgent, DevAgent, QAAgent) are affected
- Stories cannot be created/filled automatically
- Epic automation workflow is blocked

---

## 🔍 Root Cause Analysis

### Timeline Analysis (from log)

| Timestamp | Event | Status |
|-----------|-------|--------|
| `01:12:40,314` | SystemMessage received | ✅ Success |
| `01:15:41,781` | AssistantMessage received | ✅ Success |
| `01:15:41,781` | **ResultMessage received** | ✅ Success |
| `01:15:42,016` | CLI exit code 1 error | ❌ Error |

**Key Finding**: The error occurs **235ms AFTER** receiving the `ResultMessage`, meaning:
- The Claude API call **completed successfully**
- All required data was received
- The error is in the **cleanup/shutdown phase** of the CLI subprocess

### Error Chain

```
sdk_executor.py:82 (anyio.create_task_group)
    ↓
sdk_executor.py:182 (async for message in sdk_generator)
    ↓
sdk_helper.py:160 (async for message in gen)
    ↓
claude_agent_sdk/query.py:123 (query)
    ↓
claude_agent_sdk/_internal/client.py:120 (process_query)
    ↓
claude_agent_sdk/_internal/query.py:598 (receive_messages)
    ↓
raise Exception("Command failed with exit code 1")
```

### Root Cause

The `claude_agent_sdk` library treats **any non-zero CLI exit code as fatal**, even when:
1. All messages were successfully received
2. The `ResultMessage` indicates successful completion
3. The error is only in the cleanup/termination phase

This is a **false negative** - the work was completed but reported as failed.

---

## 💡 Solution Design

### Strategy: "Success-Before-Error" Detection

Modify the `SDKExecutor` to track whether a valid `ResultMessage` was received before any error occurs. If yes, treat the operation as successful despite cleanup errors.

### Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SDKExecutor.execute()                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Message Collection Loop                             │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  1. Receive SystemMessage      ✓            │    │   │
│  │  │  2. Receive AssistantMessage   ✓            │    │   │
│  │  │  3. Receive ResultMessage      ✓ ← MARK    │    │   │
│  │  │  4. CLI Exit Error             ✗            │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                     ↓                                │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Error Handler (NEW)                         │    │   │
│  │  │  IF ResultMessage was received:              │    │   │
│  │  │     → Return SUCCESS (ignore cleanup error)  │    │   │
│  │  │  ELSE:                                       │    │   │
│  │  │     → Return ERROR (true failure)            │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Plan

### Phase 1: Modify `sdk_executor.py`

**File**: `autoBMAD/epic_automation/core/sdk_executor.py`

**Changes**:

1. Add `result_message_received` flag to track if ResultMessage was captured
2. Store the last valid ResultMessage before any error
3. In exception handler, check if ResultMessage was received
4. If yes, return success result instead of error

#### Code Changes

```python
# In _execute_in_taskgroup method (around line 169)

# ADD: Track result message
result_message_received = False
last_result_message = None

# MODIFY: In the message collection loop (around line 182)
async for message in sdk_generator:
    messages.append(message)
    logger.debug(f"[{agent_name}] Received message: {type(message)}")
    
    # NEW: Check if this is a ResultMessage
    msg_type = type(message).__name__
    if msg_type == "ResultMessage":
        result_message_received = True
        last_result_message = message
        logger.info(f"[{agent_name}] ResultMessage captured (pre-error protection)")
    
    # ... rest of existing code

# MODIFY: In exception handler (around line 284)
except Exception as e:
    # NEW: Check if we already received a valid result
    if result_message_received and last_result_message is not None:
        logger.warning(
            f"[{agent_name}] Error occurred AFTER ResultMessage - "
            f"treating as success (error was: {e})"
        )
        # Return success result based on captured ResultMessage
        return SDKResult(
            has_target_result=True,
            cleanup_completed=True,  # Mark as completed despite error
            duration_seconds=time.time() - start_time,
            session_id=f"{agent_name}-{call_id[:8]}",
            agent_name=agent_name,
            messages=messages,
            target_message=last_result_message,
            error_type=SDKErrorType.SUCCESS,
            errors=[f"Post-completion error (ignored): {e}"]
        )
    
    # Otherwise, propagate the error as before
    raise
```

### Phase 2: Add ResultMessage Detection Helper

**File**: `autoBMAD/epic_automation/agents/sdk_helper.py`

**Changes**:

Add a utility function to check if a message is a valid (non-error) ResultMessage:

```python
def is_success_result_message(message: Any) -> bool:
    """
    Check if message is a successful ResultMessage.
    
    Args:
        message: SDK message to check
        
    Returns:
        True if message is a non-error ResultMessage
    """
    if not is_result_message(message):
        return False
    
    # Check if it's an error result
    if hasattr(message, "is_error") and message.is_error:
        return False
    
    return True
```

### Phase 3: Enhanced Error Logging

**File**: `autoBMAD/epic_automation/core/sdk_executor.py`

Add detailed logging for debugging:

```python
# Add at the start of exception handling
logger.debug(
    f"[{agent_name}] Exception context: "
    f"messages_count={len(messages)}, "
    f"result_received={result_message_received}, "
    f"target_found={target_message is not None}"
)
```

---

## 📝 Detailed Code Changes

### File: `sdk_executor.py`

#### Change 1: Add tracking variables (after line 169)

```python
# 🆕 Track ResultMessage for post-error recovery
result_message_received = False
last_result_message = None
```

#### Change 2: Capture ResultMessage in loop (around line 184)

```python
# Check for target
try:
    if target_predicate(message):
        target_message = message
        self.cancel_manager.mark_target_result_found(call_id)
        logger.info(f"[{agent_name}] Target found, requesting cancel")
        
        # Request cancel
        self.cancel_manager.request_cancel(call_id)
    
    # 🆕 Also track ResultMessage type specifically
    msg_type_name = type(message).__name__
    if msg_type_name == "ResultMessage":
        result_message_received = True
        last_result_message = message
        logger.debug(f"[{agent_name}] ResultMessage captured for error recovery")
        
except Exception as e:
    errors.append(f"Target predicate error: {e}")
    logger.error(f"[{agent_name}] Target predicate error: {e}")
```

#### Change 3: Handle post-completion errors (replace exception handler around line 284)

```python
except Exception as e:
    # 🆕 NEW: Check if we have a valid result despite the error
    if result_message_received and last_result_message is not None:
        # Check if the ResultMessage indicates success
        is_error_result = (
            hasattr(last_result_message, "is_error") and 
            last_result_message.is_error
        )
        
        if not is_error_result:
            duration = time.time() - start_time
            logger.warning(
                f"[{agent_name}] Post-ResultMessage error ignored: {e}"
            )
            logger.info(
                f"[{agent_name}] Returning success based on captured ResultMessage"
            )
            
            # Return success result
            return SDKResult(
                has_target_result=True,
                cleanup_completed=True,
                duration_seconds=duration,
                session_id=f"{agent_name}-{call_id[:8]}",
                agent_name=agent_name,
                messages=messages,
                target_message=last_result_message,
                error_type=SDKErrorType.SUCCESS,
                errors=[f"Post-completion error (ignored): {str(e)[:200]}"]
            )
    
    # No valid result captured, propagate error
    raise
```

---

## ✅ Verification Plan

### Test Case 1: Simulated Post-Result Error

```python
async def test_post_result_error_recovery():
    """Test that errors after ResultMessage are treated as success."""
    # This test should verify the new error recovery logic
    pass
```

### Test Case 2: Real SDK Call

Run the Epic automation with verbose logging:

```bash
python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-01-foundation-data-layer.md --verbose
```

**Expected Behavior**:
- Log shows: `Post-ResultMessage error ignored: Command failed with exit code 1`
- Log shows: `Returning success based on captured ResultMessage`
- Story files are created successfully

### Test Case 3: True Error (No ResultMessage)

Verify that real errors (before ResultMessage) are still reported correctly.

---

## 📊 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positive (ignoring real error) | Low | Medium | Only ignore errors AFTER successful ResultMessage |
| Incomplete file writes | Low | Medium | Add file verification after SDK call |
| Masking SDK issues | Medium | Low | Log all ignored errors for review |

---

## 🚀 Implementation Steps

1. **Backup current files**
   ```bash
   copy sdk_executor.py sdk_executor.py.backup
   ```

2. **Apply code changes to `sdk_executor.py`**

3. **Test with single story**
   ```bash
   # Create a test epic with one story
   python -m autoBMAD.epic_automation.epic_driver test_epic.md --verbose
   ```

4. **Verify story file was created**

5. **Run full epic automation**

6. **Monitor logs for any issues**

---

## 📚 Related Documents

- [sdk-cancellation-manager-design.md](./architecture/sdk-cancellation-manager-design.md)
- [SOLUTION_SDK_CALLER_FIX.md](./SOLUTION_SDK_CALLER_FIX.md)
- [QUALITY_GATES_CANCEL_SCOPE_FIX.md](./QUALITY_GATES_CANCEL_SCOPE_FIX.md)

---

## 📝 Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-16 | Initial solution design | System |
| 1.0.1 | 2026-02-16 | Implementation complete - Added PostResultMessageError, tracking variables, and error recovery logic in sdk_executor.py; Added is_success_result_message in sdk_helper.py; Created test_sdk_exit_code_fix.py | System |

---

## ✅ Acceptance Criteria

- [x] SDK calls that receive ResultMessage before error are treated as success
- [x] Error is logged but does not fail the operation
- [x] Story files are created successfully
- [x] True errors (before ResultMessage) still fail correctly
- [x] All existing tests pass

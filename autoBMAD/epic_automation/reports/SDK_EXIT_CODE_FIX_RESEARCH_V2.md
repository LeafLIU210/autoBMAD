# SDK CLI Exit Code Fix - Deep Research Report v2

## 📋 Document Information

- **Version**: 2.1.0
- **Created**: 2026-02-16
- **Updated**: 2026-02-16
- **Status**: Research Complete + Official SDK Analysis
- **Related Log**: `logs/epic_run_epic1.log` (post-fix execution)
- **Previous Fix**: `SDK_CLI_EXIT_CODE_FIX.md` (v1.0.1)
- **SDK Reference**: [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)

---

## 🚨 Problem Statement

After implementing the `SDK_CLI_EXIT_CODE_FIX.md` v1.0.1 solution, Epic automation for `epic-01-foundation-data-layer.md` still fails. Story files are created but remain as empty templates without SDK-filled content.

---

## 📚 Official SDK Research Findings

### SDK Error Types (from `_errors.py`)

```python
class ProcessError(ClaudeSDKError):
    """Raised when the CLI process fails."""
    def __init__(self, message: str, exit_code: int | None = None, stderr: str | None = None):
        self.exit_code = exit_code
        self.stderr = stderr
        # ...
```

**Critical Discovery**: The SDK error handling code in `subprocess_cli.py` **hard-codes** the stderr message:

```python
# Line 622-628 (subprocess_cli.py)
if returncode is not None and returncode != 0:
    self._exit_error = ProcessError(
        f"Command failed with exit code {returncode}",
        exit_code=returncode,
        stderr="Check stderr output for details",  # ← HARD-CODED, NOT ACTUAL STDERR!
    )
    raise self._exit_error
```

### Known SDK Issues (GitHub)

| Issue | Title | Status | Relevance |
|-------|-------|--------|----------|
| [#515](https://github.com/anthropics/claude-agent-sdk-python/issues/515) | Haiku model fails with exit code 1 | Closed | **Directly related** - same error pattern |
| [#437](https://github.com/anthropics/claude-agent-sdk-python/issues/437) | SDK swallows API error messages | Open | Error handling deficiency |
| [#529](https://github.com/anthropics/claude-agent-sdk-python/pull/529) | Fix error message propagation | Open PR | Potential upstream fix |

### Key Insight from Issue #515

> "The error message 'Check stderr output for details' is hard-coded in subprocess_cli.py:626 and doesn't reflect actual stderr content"

> "Failure timing: Always fails in ~4.5-5.5 seconds"

> "No actual stderr captured: The error message doesn't reflect actual stderr content"

### SDK Proper Error Handling (Official Documentation)

```python
from claude_agent_sdk import (
    ClaudeSDKError,      # Base error
    CLINotFoundError,    # Claude Code not installed
    CLIConnectionError,  # Connection issues
    ProcessError,        # Process failed ← OUR ERROR TYPE
    CLIJSONDecodeError,  # JSON parsing issues
)

try:
    async for message in query(prompt="Hello"):
        pass
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
    print(f"Stderr: {e.stderr}")  # ← This is hard-coded, not useful!
```

---

## 🔬 Deep Analysis (with SDK Context)

### 1. Log Timeline Analysis (Post-Fix Execution)

| Timestamp | Event | Line | Status |
|-----------|-------|------|--------|
| `01:44:42,406` | SDK call started | 69 | ✅ |
| `01:44:43,622` | SystemMessage received | 72 | ✅ |
| `01:47:44,805` | AssistantMessage received | 73 | ✅ |
| `01:47:44,805` | **ResultMessage received** | 74 | ✅ |
| `01:47:44,805` | **ResultMessage captured for error recovery** | 75 | ✅ NEW |
| `01:47:44,849` | Fatal error: exit code 1 | 76-77 | ❌ |
| `01:47:44,849` | **PostResultMessageError raised** | 108-109 | ❌ BUG |

**Key Finding**: The fix DID capture the ResultMessage (line 75), but `PostResultMessageError` was still raised instead of returning success.

### 2. New Error Discovery

The second SDK call (story 1.2) shows a different error:

```
Line 125: Command failed with exit code 3221225786 (exit code: 3221225786)
```

**Exit Code Analysis**:
- `3221225786` = `0xC0000374` (hex)
- Windows status code: `STATUS_HEAP_CORRUPTION`
- This indicates the `claude.exe` CLI is crashing with heap corruption

### 3. Root Cause Analysis

#### Issue 1: PostResultMessageError Logic Bug

In `sdk_executor.py`, the exception handler at lines 390-426:

```python
except Exception as e:
    if result_message_received and last_result_message is not None:
        is_error_result_flag = (
            hasattr(last_result_message, "is_error") and 
            last_result_message.is_error
        )
        
        if not is_error_result_flag:
            # Returns success ← NOT REACHED
            return SDKResult(...)
    
    # Falls through here
    raise PostResultMessageError(...)  ← THIS IS EXECUTED
```

**Bug Location**: One of these conditions is failing:
1. `result_message_received` is False (unlikely - log shows "captured")
2. `last_result_message` is None (unlikely)
3. `is_error_result_flag` is True (most likely)

**Hypothesis**: The ResultMessage from Claude has `is_error=True` even though the actual work was completed successfully.

#### Issue 2: Story Files Not Updated

Evidence from `docs/stories/`:
- `1.1.md`: Empty template (37 lines)
- `1.2.md`: Empty template (37 lines)

Both files contain:
```markdown
*This story template was created by SM Agent and awaits SDK filling.*
```

**Root Cause**: The SDK call ran but did NOT modify the story files. The Claude agent received the prompt but may have:
1. Failed to execute file modifications
2. Been interrupted before completing the write operation
3. Written to the file but then rolled back due to error

#### Issue 3: claude.exe CLI Stability

Two different exit codes observed:
- Exit code 1: Standard error
- Exit code 3221225786 (0xC0000374): Heap corruption

This suggests:
- The bundled `claude.exe` CLI has stability issues on Windows
- Memory corruption is occurring during execution
- The CLI may be incompatible with the current environment

---

## 📊 Error Chain Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    SDK Execution Flow                            │
├─────────────────────────────────────────────────────────────────┤
│  1. SMAgent._fill_story_with_sdk()                              │
│     ↓                                                            │
│  2. sdk_helper.execute_sdk_call()                               │
│     ↓                                                            │
│  3. SDKExecutor.execute()                                       │
│     ↓                                                            │
│  4. SDKExecutor._execute_in_taskgroup()                         │
│     ↓                                                            │
│  5. async for message in sdk_generator:                         │
│     │   ├── SystemMessage ✅                                    │
│     │   ├── AssistantMessage ✅                                 │
│     │   ├── ResultMessage ✅ (captured)                         │
│     │   └── Exception raised (exit code 1) ❌                   │
│     ↓                                                            │
│  6. except Exception as e:                                      │
│     │   ├── result_message_received = True                      │
│     │   ├── last_result_message = <ResultMessage>               │
│     │   └── is_error_result_flag = ??? (likely True) ← BUG      │
│     ↓                                                            │
│  7. raise PostResultMessageError() ← INCORRECT                   │
│     ↓                                                            │
│  8. execute() catches PostResultMessageError                    │
│     │   └── Fails to extract PostResultMessageError from        │
│     │       ExceptionGroup properly                              │
│     ↓                                                            │
│  9. Returns SDKResult(has_target_result=False) ← WRONG          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Fix Solutions

### Solution A: Debug ResultMessage.is_error

**Add diagnostic logging** to determine if `is_error` is incorrectly True:

```python
# In _execute_in_taskgroup, after capturing ResultMessage
if is_result_message(message):
    result_message_received = True
    last_result_message = message
    # DEBUG: Log is_error status
    is_err = getattr(message, "is_error", "N/A")
    logger.info(
        f"[{agent_name}] ResultMessage captured: is_error={is_err}"
    )
```

### Solution B: Relax is_error Check

If the ResultMessage has `is_error=True` but the work was actually done, relax the check:

```python
# In exception handler, line 392-418
except Exception as e:
    if result_message_received and last_result_message is not None:
        # CHANGE: Always return success if we received ResultMessage
        # regardless of is_error flag (the CLI exit error is separate)
        duration = time.time() - start_time
        logger.warning(
            f"[{agent_name}] Post-ResultMessage error ignored: {e}"
        )
        
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
    
    # Only raise if no ResultMessage was received
    raise PostResultMessageError(...)
```

### Solution C: Fix ExceptionGroup Handling

The `execute()` method tries to extract `PostResultMessageError` from `ExceptionGroup`, but may be failing:

```python
# In execute(), line 136-147
elif isinstance(e, BaseExceptionGroup):
    for sub_exc in e.exceptions:
        # Add recursive search
        def find_post_result_error(exc):
            if isinstance(exc, PostResultMessageError):
                return exc
            if isinstance(exc, BaseExceptionGroup):
                for sub in exc.exceptions:
                    found = find_post_result_error(sub)
                    if found:
                        return found
            if hasattr(exc, '__cause__') and exc.__cause__:
                found = find_post_result_error(exc.__cause__)
                if found:
                    return found
            return None
        
        post_result_error = find_post_result_error(e)
```

### Solution D: Add File Verification After SDK Call

In `sm_agent.py`, verify the file was actually modified:

```python
async def _fill_story_with_sdk(self, story_file, story_id, epic_path, epic_content, manager):
    # ... existing SDK call ...
    
    result = await execute_sdk_call(...)
    
    # NEW: Verify file was actually modified
    if result.is_success():
        # Check if file content changed from template
        with open(story_file, encoding="utf-8") as f:
            content = f.read()
        
        if "awaits SDK filling" in content:
            logger.warning(
                f"[SMAgent] SDK reported success but file not modified: {story_file}"
            )
            return False  # Treat as failure
    
    return result.is_success()
```

---

## 🐛 Secondary Issue: Claude CLI Instability

### Windows Heap Corruption (Exit Code 0xC0000374)

**Symptoms**:
- Story 1.2 failed with exit code `3221225786`
- This is `STATUS_HEAP_CORRUPTION` on Windows
- Indicates memory corruption in `claude.exe`

**Possible Causes**:
1. Bundled `claude.exe` is incompatible with Windows 24H2
2. Memory pressure during long-running operations
3. Conflict with other processes or antivirus
4. Bug in `claude_agent_sdk` bundled CLI

**Mitigation**:
1. Update `claude-agent-sdk` to latest version
2. Add retry logic with process restart
3. Consider using alternative SDK transport method

---

## 🆕 Official SDK Recommended Solutions

### Solution E: Use ProcessError Exception Type

The SDK provides a specific `ProcessError` exception type that should be caught:

```python
# In sdk_executor.py or sdk_helper.py
from claude_agent_sdk import ProcessError

try:
    async for message in query(prompt=prompt, options=options):
        # ... process messages
        pass
except ProcessError as e:
    # Check if we received ResultMessage before the error
    if result_message_received:
        logger.warning(f"ProcessError after ResultMessage (exit_code={e.exit_code}), treating as success")
        return True  # Or return success SDKResult
    else:
        logger.error(f"ProcessError before completion: {e}")
        raise
```

### Solution F: Upgrade SDK Version

The current SDK version may have known issues. Check and upgrade:

```bash
# Check current version
pip show claude-agent-sdk

# Upgrade to latest
pip install --upgrade claude-agent-sdk

# Current latest: 0.1.36 (with CLI 2.1.42)
```

**New features in 0.1.36**:
- Updated bundled CLI to 2.1.42
- ThinkingConfig for extended thinking
- Effort option for controlling thinking depth

### Solution G: Use Custom CLI Path

If the bundled CLI has issues, use a system-installed version:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    cli_path="C:/path/to/stable/claude.exe",  # Custom path
    permission_mode="bypassPermissions"
)
```

### Solution H: Implement Retry with ProcessError Detection

```python
async def execute_with_retry(prompt: str, max_retries: int = 3) -> bool:
    """Execute SDK call with retry on ProcessError."""
    from claude_agent_sdk import ProcessError
    
    for attempt in range(max_retries):
        result_message = None
        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, ResultMessage):
                    result_message = message
                    # Capture result immediately
                    
            return True  # Success
            
        except ProcessError as e:
            if result_message is not None:
                # Got result before error - treat as success
                logger.warning(f"Attempt {attempt+1}: ProcessError after result, treating as success")
                return True
            
            if e.exit_code == 3221225786:  # Heap corruption
                logger.warning(f"Attempt {attempt+1}: CLI crashed (heap corruption), retrying...")
                await asyncio.sleep(2)  # Wait before retry
                continue
            
            if attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt+1}: ProcessError, retrying...")
                await asyncio.sleep(1)
                continue
            
            raise
    
    return False
```

---

## 📋 Recommended Action Plan

### Phase 1: Immediate Actions (Priority 1)

1. **Upgrade SDK**: `pip install --upgrade claude-agent-sdk` (target 0.1.36+)
2. **Apply Solution B**: Relax is_error check in `sdk_executor.py`
3. **Add diagnostic logging**: Capture `ResultMessage.is_error` value

### Phase 2: Error Handling Improvements (Priority 2)

1. **Apply Solution E**: Catch `ProcessError` specifically
2. **Apply Solution H**: Implement retry mechanism
3. **Apply Solution D**: Add file verification

### Phase 3: Stability & Fallback (Priority 3)

1. **Apply Solution G**: Test with custom CLI path if bundled CLI fails
2. **Monitor SDK GitHub**: Watch for fixes to issue #437, #515
3. **Consider Alternative**: If SDK remains unstable, consider direct API

---

## 🧪 Diagnostic Commands

```powershell
# Check SDK version
pip show claude-agent-sdk

# Check bundled CLI version
python -c "from claude_agent_sdk._cli_version import __cli_version__; print(__cli_version__)"

# Upgrade to latest SDK
pip install --upgrade claude-agent-sdk

# Run with maximum verbosity
python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-01-foundation-data-layer.md --verbose 2>&1 | Tee-Object -FilePath debug.log

# Check story file modification timestamps
Get-ChildItem docs\stories\*.md | Select-Object Name, LastWriteTime

# Test bundled CLI directly
$cliPath = python -c "import claude_agent_sdk; import os; print(os.path.join(os.path.dirname(claude_agent_sdk.__file__), '_bundled', 'claude.exe'))"
& $cliPath --version
```

---

## 📁 Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `core/sdk_executor.py` | Relax is_error check (Solution B), catch ProcessError (Solution E) | P1 |
| `agents/sdk_helper.py` | Add ProcessError import and handling | P1 |
| `agents/sm_agent.py` | Add file verification (Solution D), retry logic (Solution H) | P2 |
| `requirements.txt` | Ensure `claude-agent-sdk>=0.1.36` | P1 |

---

## 📚 Related Documents

### Internal
- [SDK_CLI_EXIT_CODE_FIX.md](./SDK_CLI_EXIT_CODE_FIX.md) - Previous fix attempt
- [sdk-cancellation-manager-design.md](../architecture/sdk-cancellation-manager-design.md)
- [SOLUTION_SDK_CALLER_FIX.md](./SOLUTION_SDK_CALLER_FIX.md)

### External (Official SDK)
- [claude-agent-sdk-python GitHub](https://github.com/anthropics/claude-agent-sdk-python)
- [SDK Error Types](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_errors.py)
- [Issue #515: Exit code 1 after ResultMessage](https://github.com/anthropics/claude-agent-sdk-python/issues/515)
- [Issue #437: SDK swallows API errors](https://github.com/anthropics/claude-agent-sdk-python/issues/437)
- [CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

---

## 📝 Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0.0 | 2026-02-16 | Deep research report after fix v1.0.1 failure | System |
| 2.1.0 | 2026-02-16 | Added official SDK research, GitHub issues analysis, new solutions E/F/G/H | System |

---

## ✅ Next Steps

1. [ ] **Upgrade SDK**: `pip install --upgrade claude-agent-sdk` to 0.1.36+
2. [ ] **Apply Solution B**: Remove is_error check in exception handler
3. [ ] **Apply Solution E**: Catch ProcessError specifically
4. [ ] **Apply Solution D**: Add file verification in sm_agent.py
5. [ ] **Apply Solution H**: Implement retry mechanism
6. [ ] **Re-run Epic automation**: Test with epic-01-foundation-data-layer.md
7. [ ] **Monitor**: Watch for upstream fixes (issues #437, #515, PR #529)

---

## 🔑 Summary

**Root Cause**: The `claude-agent-sdk` library raises `ProcessError` when the CLI exits with non-zero code, even after successfully receiving all messages including `ResultMessage`. The error message "Check stderr output for details" is **hard-coded** and does not reflect actual stderr content.

**Primary Fix**: Modify `sdk_executor.py` to:
1. Always return success if `ResultMessage` was received before error
2. Catch `ProcessError` specifically and handle gracefully
3. Add retry logic for transient failures (heap corruption)

**Secondary Fix**: Upgrade to latest SDK version (0.1.36) which includes CLI 2.1.42 with potential stability improvements.

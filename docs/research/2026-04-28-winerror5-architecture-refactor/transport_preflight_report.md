        # Transport Preflight Diagnostic Report

        **Generated**: 2026-04-28 10:53:16
        **Platform**: win32

        ## Summary

        | Check | Result | Detail |
        |-------|--------|--------|
        | Direct CLI (`claude --version`) | ✅ PASS | 2.1.92 (Claude Code) |
        | `subprocess.Popen` with PIPEs | ✅ PASS | OK |
        | `anyio.open_process` with PIPEs | ❌ FAIL | EndOfStream:  |
        | `ClaudeSDKClient.connect()` | ✅ PASS | OK |

        ## Diagnosis

        CRITICAL: Direct CLI and subprocess.Popen succeed, but anyio.open_process fails. This matches the WinError 5 pattern observed in production.

        ## Recommendations

        - Implement runtime preflight before pipeline start to detect anyio spawn failure early.
- Consider using subprocess.Popen wrapper as fallback transport on Windows.
- Investigate Windows-specific anyio backend (trio vs asyncio) behavior.

        ## Structured Data

        See `transport_preflight_result.json` for machine-readable output.

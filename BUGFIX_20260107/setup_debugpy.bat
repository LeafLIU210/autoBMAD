@echo off
REM ================================================================================
REM BUGFIX_20260107 debugpy Integration Setup Script
REM
REM This script sets up the debugpy integration for the BUGFIX_20260107 framework.
REM ================================================================================

echo.
echo ================================================================================
echo BUGFIX_20260107 DEBUGPY INTEGRATION SETUP
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Install dependencies
echo [2/4] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements-debug.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Run verification
echo [3/4] Running verification...
python quick_verify.py
if errorlevel 1 (
    echo WARNING: Verification completed with warnings
    echo Please review the output above
) else (
    echo SUCCESS: Verification passed
)
echo.

REM Create logs directory
if not exist "logs" mkdir logs
echo [4/4] Created logs directory
echo.

REM Summary
echo ================================================================================
echo SETUP COMPLETED
echo ================================================================================
echo.
echo Next steps:
echo   1. Run demo: python demo_debugpy.py
echo   2. Start debug server: python -c "from debugpy_integration import DebugpyServer; import asyncio; asyncio.run(DebugpyServer().start())"
echo   3. Connect your IDE to localhost:5678
echo.
echo For more information, see:
echo   - README_DEBUGPY.md
echo   - DEBUGPY_INTEGRATION_FINAL_REPORT.md
echo.
pause

@echo off
REM 测试套件运行脚本

echo.
echo ========================================
echo Epic自动化系统修复测试套件
echo ========================================
echo.

REM 设置Python路径
set PYTHONPATH=%cd%;%PYTHONPATH%

REM 运行Cancel Scope测试
echo 1. 运行Cancel Scope测试...
echo ----------------------------------------
python tests\test_cancel_scope.py
if %errorlevel% equ 0 (
    echo ✅ Cancel Scope测试通过
) else (
    echo ❌ Cancel Scope测试失败
)
echo.

REM 运行SDK会话测试
echo 2. 运行SDK会话测试...
echo ----------------------------------------
python tests\test_sdk_sessions.py
if %errorlevel% equ 0 (
    echo ✅ SDK会话测试通过
) else (
    echo ❌ SDK会话测试失败
)
echo.

REM 运行超时处理测试
echo 3. 运行超时处理测试...
echo ----------------------------------------
python tests\test_timeout_handling.py
if %errorlevel% equ 0 (
    echo ✅ 超时处理测试通过
) else (
    echo ❌ 超时处理测试失败
)
echo.

REM 运行资源清理测试
echo 4. 运行资源清理测试...
echo ----------------------------------------
python tests\test_resource_cleanup.py
if %errorlevel% equ 0 (
    echo ✅ 资源清理测试通过
) else (
    echo ❌ 资源清理测试失败
)
echo.

echo ========================================
echo 测试套件执行完成!
echo ========================================
echo.
echo 如需查看详细报告，请检查生成的日志文件
echo.

REM 询问是否运行pytest
echo 是否运行pytest? (y/n)
set /p run_pytest=
if /i "%run_pytest%"=="y" (
    echo.
    echo 运行pytest...
    pytest tests\ -v --tb=short
)

pause

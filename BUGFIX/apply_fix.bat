@echo off
REM Epic自动化系统修复应用脚本
REM 用于快速应用修复到生产环境

echo.
echo ========================================
echo Epic自动化系统修复应用脚本
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "autoBMAD\epic_automation" (
    echo 错误: 未找到autoBMAD\epic_automation目录
    echo 请确保在项目根目录运行此脚本
    echo.
    pause
    exit /b 1
)

REM 创建备份目录
echo 创建备份目录...
if not exist "autoBMAD\epic_automation\backup" mkdir "autoBMAD\epic_automation\backup"
if not exist "autoBMAD\epic_automation\backup\%date:~0,4%%date:~5,2%%date:~8,2%" mkdir "autoBMAD\epic_automation\backup\%date:~0,4%%date:~5,2%%date:~8,2%"
set backup_dir=autoBMAD\epic_automation\backup\%date:~0,4%%date:~5,2%%date:~8,2%
echo 备份目录: %backup_dir%
echo.

REM 备份原始文件
echo 备份原始文件...
copy /Y "autoBMAD\epic_automation\sdk_wrapper.py" "%backup_dir%\sdk_wrapper.py.backup" >nul
if %errorlevel% equ 0 (
    echo ✅ sdk_wrapper.py 备份成功
) else (
    echo ❌ sdk_wrapper.py 备份失败
)

copy /Y "autoBMAD\epic_automation\sdk_session_manager.py" "%backup_dir%\sdk_session_manager.py.backup" >nul
if %errorlevel% equ 0 (
    echo ✅ sdk_session_manager.py 备份成功
) else (
    echo ❌ sdk_session_manager.py 备份失败
)

copy /Y "autoBMAD\epic_automation\state_manager.py" "%backup_dir%\state_manager.py.backup" >nul
if %errorlevel% equ 0 (
    echo ✅ state_manager.py 备份成功
) else (
    echo ❌ state_manager.py 备份失败
)

copy /Y "autoBMAD\epic_automation\qa_agent.py" "%backup_dir%\qa_agent.py.backup" >nul
if %errorlevel% equ 0 (
    echo ✅ qa_agent.py 备份成功
) else (
    echo ❌ qa_agent.py 备份失败
)

echo.
echo 备份完成! 备份位置: %backup_dir%
echo.

REM 应用修复文件
echo 应用修复文件...
if exist "fixed_modules\sdk_wrapper_fixed.py" (
    copy /Y "fixed_modules\sdk_wrapper_fixed.py" "autoBMAD\epic_automation\sdk_wrapper.py" >nul
    if %errorlevel% equ 0 (
        echo ✅ sdk_wrapper.py 修复已应用
    ) else (
        echo ❌ sdk_wrapper.py 修复应用失败
    )
) else (
    echo ❌ 未找到 sdk_wrapper_fixed.py
)

if exist "fixed_modules\sdk_session_manager_fixed.py" (
    copy /Y "fixed_modules\sdk_session_manager_fixed.py" "autoBMAD\epic_automation\sdk_session_manager.py" >nul
    if %errorlevel% equ 0 (
        echo ✅ sdk_session_manager.py 修复已应用
    ) else (
        echo ❌ sdk_session_manager.py 修复应用失败
    )
) else (
    echo ❌ 未找到 sdk_session_manager_fixed.py
)

if exist "fixed_modules\state_manager_fixed.py" (
    copy /Y "fixed_modules\state_manager_fixed.py" "autoBMAD\epic_automation\state_manager.py" >nul
    if %errorlevel% equ 0 (
        echo ✅ state_manager.py 修复已应用
    ) else (
        echo ❌ state_manager.py 修复应用失败
    )
) else (
    echo ❌ 未找到 state_manager_fixed.py
)

if exist "fixed_modules\qa_agent_fixed.py" (
    copy /Y "fixed_modules\qa_agent_fixed.py" "autoBMAD\epic_automation\qa_agent.py" >nul
    if %errorlevel% equ 0 (
        echo ✅ qa_agent.py 修复已应用
    ) else (
        echo ❌ qa_agent.py 修复应用失败
    )
) else (
    echo ❌ 未找到 qa_agent_fixed.py
)

echo.
echo 修复文件应用完成!
echo.

REM 询问是否运行验证测试
echo 是否运行验证测试? (y/n)
set /p run_tests=
if /i "%run_tests%"=="y" (
    echo.
    echo 运行验证测试...
    echo.

    REM 运行修复验证
    echo 1. 运行修复验证...
    cd validation_scripts
    python validate_fixes.py
    if %errorlevel% equ 0 (
        echo ✅ 修复验证通过
    ) else (
        echo ❌ 修复验证失败
    )
    echo.

    REM 运行系统诊断
    echo 2. 运行系统诊断...
    python run_diagnostic.py
    if %errorlevel% equ 0 (
        echo ✅ 系统诊断通过
    ) else (
        echo ⚠️  系统诊断发现问题
    )
    echo.

    REM 运行性能测试
    echo 3. 运行性能测试...
    python performance_test.py
    if %errorlevel% equ 0 (
        echo ✅ 性能测试通过
    ) else (
        echo ⚠️  性能测试发现问题
    )
    echo.

    echo 验证测试完成!
) else (
    echo 跳过验证测试
)

echo.
echo ========================================
echo 修复应用完成!
echo ========================================
echo.
echo 备份位置: %backup_dir%
echo.
echo 如需回滚，请使用以下命令:
echo copy "%backup_dir%\sdk_wrapper.py.backup" "autoBMAD\epic_automation\sdk_wrapper.py"
echo copy "%backup_dir%\sdk_session_manager.py.backup" "autoBMAD\epic_automation\sdk_session_manager.py"
echo copy "%backup_dir%\state_manager.py.backup" "autoBMAD\epic_automation\state_manager.py"
echo copy "%backup_dir%\qa_agent.py.backup" "autoBMAD\epic_automation\qa_agent.py"
echo.
pause

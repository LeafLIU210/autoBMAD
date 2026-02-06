#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

[CmdletBinding()]
param(
    [switch]$SkipDependencies,
    [switch]$SkipApiKeyConfig,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$ScriptVersion = "1.0.0"
$ScriptName = "CLAUDE.md 自动更新安装程序"

# 颜色配置
$Colors = @{
    Green = "#2ECC71"
    Yellow = "#F1C40F"
    Red = "#E74C3C"
    Blue = "#3498DB"
    Reset = ""
}

# 路径配置
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$GitHooksDir = Join-Path $ProjectRoot ".git\hooks"
$ScriptsDir = Join-Path $ProjectRoot "scripts"
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$VenvPip = Join-Path $ProjectRoot "venv\Scripts\pip.exe"
$UpdateScript = Join-Path $ScriptsDir "update_claude_md.py"
$PostCommitSource = Join-Path $ScriptsDir "post-commit"
$PostCommitTarget = Join-Path $GitHooksDir "post-commit"

function Write-Section {
    <#
    .SYNOPSIS
        输出章节标题
    #>
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $Colors.Green
    Write-Host "  $Title" -ForegroundColor $Colors.Green
    Write-Host ("=" * 60) -ForegroundColor $Colors.Green
    Write-Host ""
}

function Write-Step {
    <#
    .SYNOPSIS
        输出步骤信息
    #>
    param(
        [int]$Step,
        [string]$Message
    )
    Write-Host "[$Step] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    <#
    .SYNOPSIS
        输出成功消息
    #>
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    <#
    .SYNOPSIS
        输出警告消息
    #>
    param([string]$Message)
    Write-Host "! $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    <#
    .SYNOPSIS
        输出错误消息
    #>
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Colors.Red
}

function Test-Administrator {
    <#
    .SYNOPSIS
        检查是否以管理员身份运行
    #>
    $currentUser = New-Object System.Security.Principal.WindowsPrincipal(
        [System.Security.Principal.WindowsIdentity]::GetCurrent()
    )
    return $currentUser.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-UserChoice {
    <#
    .SYNOPSIS
        获取用户选择
    #>
    param(
        [string]$Prompt,
        [char[]]$Options = @('y', 'n')
    )
    
    $validOptions = $Options.ToLower()
    
    while ($true) {
        $response = Read-Host "$Prompt [$($Options -join '/')]"
        $response = $response.ToLower().Trim()
        
        if ($response -in $validOptions) {
            return $response
        }
        
        Write-Warning "无效选项，请输入: $($Options -join ' 或 ')"
    }
}

# ============================================================
# 安装步骤
# ============================================================

function Test-Prerequisites {
    <#
    .SYNOPSIS
        检查系统先决条件
    #>
    Write-Section "步骤 1/5: 检查系统先决条件"
    
    # 检查 PowerShell 版本
    $psVersion = $PSVersionTable.PSVersion
    Write-Step 1 "PowerShell 版本: $psVersion"
    
    if ($psVersion.Major -lt 5) {
        Write-Error "需要 PowerShell 5.1 或更高版本"
        Write-Host "当前版本: $psVersion" -ForegroundColor Yellow
        Write-Host "请升级 PowerShell 后再试" -ForegroundColor Yellow
        return $false
    }
    Write-Success "PowerShell 版本满足要求"
    
    # 检查 Git
    try {
        $gitVersion = (git --version)
        Write-Step 2 $gitVersion
        Write-Success "Git 已安装"
    }
    catch {
        Write-Error "Git 未安装或未配置"
        Write-Host "请先安装 Git (https://git-scm.com/)" -ForegroundColor Yellow
        return $false
    }
    
    # 检查项目结构
    if (-not (Test-Path $ProjectRoot)) {
        Write-Error "项目根目录不存在: $ProjectRoot"
        return $false
    }
    Write-Success "项目目录存在"
    
    if (-not (Test-Path $GitHooksDir)) {
        Write-Error "Git hooks 目录不存在: $GitHooksDir"
        return $false
    }
    Write-Success "Git hooks 目录存在"
    
    return $true
}

function Install-Dependencies {
    <#
    .SYNOPSIS
        安装 Python 依赖
    #>
    Write-Section "步骤 2/5: 安装 Python 依赖"
    
    if ($SkipDependencies) {
        Write-Warning "跳过依赖安装"
        return $true
    }
    
    # 检查虚拟环境
    if (-not (Test-Path $VenvPython)) {
        Write-Error "虚拟环境 Python 未找到: $VenvPython"
        Write-Host "请先创建虚拟环境: python -m venv venv" -ForegroundColor Yellow
        return $false
    }
    Write-Success "虚拟环境存在"
    
    # 安装依赖
    Write-Step 1 "安装 anthropic SDK..."
    
    try {
        & $VenvPip install "anthropic>=0.25.0" "python-dotenv>=1.0.0"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "依赖安装成功"
        }
        else {
            Write-Error "依赖安装失败"
            return $false
        }
    }
    catch {
        Write-Error "安装过程中发生错误: $_"
        return $false
    }
    
    # 验证安装
    Write-Step 2 "验证安装..."
    
    try {
        $verifyResult = & $VenvPython -c "from anthropic import Anthropic; print('SDK 安装成功')" 2>&1
        if ($verifyResult -contains "SDK 安装成功") {
            Write-Success "anthropic SDK 验证通过"
        }
        else {
            Write-Warning "SDK 验证结果: $verifyResult"
        }
    }
    catch {
        Write-Warning "SDK 验证时发生异常: $_"
    }
    
    return $true
}

function Install-Hook {
    <#
    .SYNOPSIS
        安装 Git hook
    #>
    Write-Section "步骤 3/5: 安装 Git Hook"
    
    # 检查源文件
    if (-not (Test-Path $PostCommitSource)) {
        Write-Error "Hook 源文件不存在: $PostCommitSource"
        return $false
    }
    Write-Success "Hook 源文件存在"
    
    # 备份现有 hook
    if (Test-Path $PostCommitTarget) {
        $backupPath = $PostCommitTarget + ".backup." + (Get-Date -Format "yyyyMMdd_HHmmss")
        Write-Step 1 "备份现有 hook 到: $backupPath"
        Copy-Item $PostCommitTarget $backupPath
        Write-Success "备份完成"
    }
    
    # 复制新 hook
    Write-Step 2 "复制 hook 到 .git/hooks..."
    
    try {
        Copy-Item $PostCommitSource $PostCommitTarget -Force
        
        # 确保文件属性正确
        $hookFile = Get-Item $PostCommitTarget
        $hookFile.IsReadOnly = $false
        
        Write-Success "Hook 安装成功"
    }
    catch {
        Write-Error "复制 hook 失败: $_"
        return $false
    }
    
    # 验证 hook
    Write-Step 3 "验证 hook 文件..."
    
    if (Test-Path $PostCommitTarget) {
        Write-Success "Hook 文件存在"
    }
    else {
        Write-Error "Hook 文件不存在"
        return $false
    }
    
    return $true
}

function Configure-ApiKey {
    <#
    .SYNOPSIS
        配置 Anthropic API Key
    #>
    Write-Section "步骤 4/5: 配置 Anthropic API Key"
    
    if ($SkipApiKeyConfig) {
        Write-Warning "跳过 API Key 配置"
        Write-Host "可以通过以下方式配置 API Key：" -ForegroundColor Yellow
        Write-Host "  1. 设置环境变量: \$env:ANTHROPIC_API_KEY='your-key'" -ForegroundColor Yellow
        Write-Host "  2. 创建 .env 文件" -ForegroundColor Yellow
        Write-Host "  3. 编辑 .claude/settings.local.json" -ForegroundColor Yellow
        return $true
    }
    
    # 检查是否已有 API Key
    $existingKey = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
    
    if ($existingKey) {
        Write-Success "已配置环境变量中的 API Key"
    }
    else {
        Write-Host "需要配置 Anthropic API Key 来使用 AI 更新功能" -ForegroundColor Yellow
        Write-Host ""
        
        $choice = Get-UserChoice -Prompt "是否现在配置 API Key" -Options @('y', 'n')
        
        if ($choice -eq 'y') {
            $apiKey = Read-Host "请输入 Anthropic API Key" -AsSecureString
            
            if ($apiKey) {
                $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
                )
                
                [Environment]::SetEnvironmentVariable(
                    "ANTHROPIC_API_KEY",
                    $plainKey,
                    "User"
                )
                
                Write-Success "API Key 已保存到用户环境变量"
                Write-Warning "需要重启终端或运行: \$env:ANTHROPIC_API_KEY='$plainKey'"
            }
        }
        else {
            Write-Host "跳过 API Key 配置，将使用基础更新模式" -ForegroundColor Yellow
        }
    }
    
    return $true
}

function Test-Installation {
    <#
    .SYNOPSIS
        测试安装结果
    #>
    Write-Section "步骤 5/5: 测试安装"
    
    if ($SkipTests) {
        Write-Warning "跳过安装测试"
        return $true
    }
    
    # 测试 Python 脚本
    Write-Step 1 "测试 Python 更新脚本..."
    
    if (Test-Path $UpdateScript) {
        try {
            & $VenvPython $UpdateScript --version 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python 脚本测试通过"
            }
            else {
                Write-Warning "Python 脚本返回非零退出码"
            }
        }
        catch {
            Write-Warning "Python 脚本测试时发生异常: $_"
        }
    }
    else {
        Write-Error "更新脚本不存在: $UpdateScript"
    }
    
    # 测试 Git 命令
    Write-Step 2 "测试 Git 命令..."
    
    try {
        $testResult = git log -1 --oneline 2>&1
        if ($?) {
            Write-Success "Git 命令测试通过"
        }
        else {
            Write-Warning "Git 命令测试失败"
        }
    }
    catch {
        Write-Warning "Git 命令测试时发生异常: $_"
    }
    
    return $true
}

function Show-CompletionMessage {
    <#
    .SYNOPSIS
        显示完成消息
    #>
    Write-Section "安装完成"
    
    Write-Host "CLAUDE.md 自动更新功能已成功安装！" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "后续操作：" -ForegroundColor $Colors.Blue
    Write-Host "  1. 每次执行 git commit 后会自动更新 CLAUDE.md" -ForegroundColor White
    Write-Host "  2. 更新记录会保存在 '## 更新记录' 部分" -ForegroundColor White
    Write-Host "  3. 可以通过查看脚本日志了解更新详情" -ForegroundColor White
    Write-Host ""
    Write-Host "常用命令：" -ForegroundColor $Colors.Blue
    Write-Host "  查看 CLAUDE.md: Get-Content CLAUDE.md | Select-Object -Last 30" -ForegroundColor White
    Write-Host "  手动触发更新: .\venv\Scripts\python.exe .\scripts\update_claude_md.py" -ForegroundColor White
    Write-Host "  查看日志: Get-Content .\scripts\post-commit.log" -ForegroundColor White
    Write-Host ""
    Write-Host "如有问题，请参考文档：" -ForegroundColor $Colors.Blue
    Write-Host "  claude_docs/git-commit-trigger-update.md" -ForegroundColor White
    Write-Host ""
}

# ============================================================
# 主安装流程
# ============================================================

function Start-Installation {
    <#
    .SYNOPSIS
        开始安装流程
    #>
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $Colors.Green
    Write-Host "  $ScriptName v$ScriptVersion" -ForegroundColor $Colors.Green
    Write-Host ("=" * 60) -ForegroundColor $Colors.Green
    Write-Host ""
    
    Write-Host "项目根目录: $ProjectRoot" -ForegroundColor $Colors.Blue
    Write-Host ""
    
    # 执行安装步骤
    $success = $true
    
    $success = Test-Prerequisites
    if (-not $success) {
        Write-Error "系统先决条件检查失败"
        exit 1
    }
    
    $success = Install-Dependencies
    if (-not $success) {
        Write-Error "依赖安装失败"
        exit 1
    }
    
    $success = Install-Hook
    if (-not $success) {
        Write-Error "Hook 安装失败"
        exit 1
    }
    
    $success = Configure-ApiKey
    if (-not $success) {
        Write-Error "API Key 配置失败"
        exit 1
    }
    
    $success = Test-Installation
    if (-not $success) {
        Write-Warning "安装测试失败，但核心功能应该正常"
    }
    
    Show-CompletionMessage
    }

try {
    Start-Installation
    exit 0
    }
    
catch {
    Write-Error "安装过程中发生未预期的错误: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
    }

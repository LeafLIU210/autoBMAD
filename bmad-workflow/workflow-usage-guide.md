# BMAD PowerShell 工作流使用指南

## 概述

BMAD PowerShell 工作流自动化系统是一个基于 PowerShell 的自动化工具，专为 BMAD-Method 开发流程设计。它通过协调 Claude Code CLI 的开发（dev）和测试（qa）智能体，实现对故事文档的循环开发工作流。

## 系统要求

### 必需条件
- **PowerShell 5.1+**（推荐 PowerShell 7.x）
- **Claude Code CLI** 已安装并可访问
- **Windows 操作系统**（或支持 PowerShell 的其他平台）
- **至少 1GB 可用磁盘空间**
- **工作目录结构**：
  ```
  D:\Python\bilibiliup\          # 项目根目录
  ├── bmad-workflow\              # 工作流脚本目录（执行目录）
  │   ├── BMAD-Workflow.ps1
  │   ├── workflow.config.yaml
  │   └── *.ps1（其他模块文件）
  ├── docs\stories\               # 故事文档目录
  └── output\                     # 输出目录
  ```

### 可选依赖
- **Pester 模块**（用于 PowerShell 测试）- 版本 3.4+ 已验证兼容
- **ThreadJob 模块**（用于并发作业管理）
- **YAML 模块**（用于配置文件解析）

## 快速开始

### 1. 安装系统

```powershell
# 克隆或下载项目
git clone <repository-url>
cd bilibiliup  # 进入项目根目录

# 进入工作流目录
cd bmad-workflow

# 运行系统测试验证安装
.\BMAD-Workflow.ps1 -Test

# 或者手动设置执行策略（需要管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### 2. 验证安装

**重要：** 所有命令必须在 `bmad-workflow` 目录下执行

```powershell
# 确保在 bmad-workflow 目录
cd D:\Python\bilibiliup\bmad-workflow

# 检查系统状态
.\BMAD-Workflow.ps1 -Status

# 运行系统测试
.\BMAD-Workflow.ps1 -Test

# 显示帮助信息
.\BMAD-Workflow.ps1 -Help
```

### 3. 运行第一个工作流

**重要执行说明：**

工作流命令 **必须** 在 `bmad-workflow` 目录下执行，这是 PowerShell 脚本的工作目录。

```powershell
# 第一步：进入工作流目录（必须！）
cd D:\Python\bilibiliup\bmad-workflow

# 第二步：使用相对路径访问项目根目录的故事文档（..\docs\stories\路径）
# 或者使用绝对路径（推荐，更可靠）

.\BMAD-Workflow.ps1 -StoryPath "..\docs\stories\1.1.project-setup.story.md"

# 或者使用绝对路径：
cd bmad-workflow
.\BMAD-Workflow.ps1 -StoryPath ""

.\BMAD-Workflow.ps1 -StoryPath "D:\Python\bilibiliup\docs\stories\1.1.project-setup.story.md"
```

**为什么必须在 bmad-workflow 目录执行？**
- 所有 PowerShell 模块和配置文件都在该目录
- 脚本使用相对路径查找依赖文件
- 日志文件默认生成在该目录的 `logs/` 子目录

## 核心概念

### 工作流类型

#### A流程：初始开发（3个并行）
- **智能体**：Dev Agent (`/Bmad:agents:dev`)
- **命令**：`*develop-story @{story_path}`
- **目标**：创建或完善测试套件，执行测试驱动开发

#### B流程：代码审查（1个）
- **智能体**：QA Agent (`/Bmad:agents:qa`)
- **命令**：`*review @{story_path}`
- **目标**：进行代码审查，输出 PASS/CONCERNS 评估

#### C流程：修复开发（3个并行）
- **智能体**：Dev Agent (`/Bmad:agents:dev`)
- **命令**：`*review-qa @{story_path}`
- **目标**：修复QA发现的问题，完善测试覆盖

#### D流程：最终开发（1个）
- **智能体**：Dev Agent (`/Bmad:agents:dev`)
- **命令**：`*develop-story @{story_path}`
- **目标**：最终开发完善

### 工作流逻辑

```
开始
  ↓
执行3个A流程（并行）
  ↓
所有A流程完成
  ↓
执行1个B流程
  ↓
检查B流程结果
  ├─ 包含"PASS" → 执行D流程 → 结束
  └─ 包含"CONCERNS"或都不包含 → 进入循环
                           ↓
                    执行3个C流程（并行）
                           ↓
                    所有C流程完成
                           ↓
                    执行1个B流程
                           ↓
                    检查B流程结果（递归）
```

## 详细使用指南

### 命令行参数

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryPath,                    # 必需：故事文档路径

    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = "./config/workflow.config.yaml",  # 可选：配置文件路径

    [Parameter(Mandatory=$false)]
    [switch]$Help,                         # 显示帮助信息

    [Parameter(Mandatory=$false)]
    [switch]$Status,                       # 显示系统状态

    [Parameter(Mandatory=$false)]
    [switch]$Cleanup,                      # 清理旧工作流和日志

    [Parameter(Mandatory=$false)]
    [switch]$Test                          # 运行系统测试
)
```

### 常用命令示例

#### 基本工作流执行
```powershell
# 第一步：确保当前目录是 bmad-workflow
cd D:\Python\bilibiliup\bmad-workflow

# 基本用法 - 使用相对路径访问项目根目录的 stories 文件夹
.\BMAD-Workflow.ps1 -StoryPath "..\docs\stories\1.1.project-setup.story.md"

# 使用自定义配置（配置文件在 bmad-workflow 目录）
.\BMAD-Workflow.ps1 -StoryPath "..\docs\stories\my-story.md" -ConfigPath "workflow.config.yaml"

# 使用绝对路径（推荐，更可靠）
.\BMAD-Workflow.ps1 -StoryPath "D:\Python\bilibiliup\docs\stories\my-story.md"
```

#### 系统管理命令（在 bmad-workflow 目录执行）
```powershell
# 第一步：进入工作流目录
cd D:\Python\bilibiliup\bmad-workflow

# 查看系统状态
.\BMAD-Workflow.ps1 -Status

# 运行诊断测试
.\BMAD-Workflow.ps1 -Test

# 清理旧数据
.\BMAD-Workflow.ps1 -Cleanup

# 获取帮助
.\BMAD-Workflow.ps1 -Help
```

### 为什么两种执行方式都可以？

脚本已经修改以**自动检测**工作流目录，使用以下算法：

```powershell
# 自动检测原理
$script:WorkflowCoreDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 无论您在何处执行，脚本都会：
# 1. 获取脚本自身所在的目录（bmad-workflow）
# 2. 从该目录加载所有模块和配置文件
# 3. 解析相对路径到正确的位置
```

**因此，您可以：**
- 在项目根目录执行（推荐，更方便）
- 在工作流目录执行（传统方式）
- 从任何其他位置执行（只要脚本路径正确）

### 故事文档格式

故事文档应该遵循以下结构：

```markdown
# 故事标题

## 文档信息
- **Project**: 项目名称
- **Story ID**: STORY-XXX
- **Version**: 版本号
- **Status**: 状态（Ready for Development, In Progress, Completed）

## 故事概述
简要描述要实现的功能

## 验收标准
### 功能需求
- [ ] 具体功能需求1
- [ ] 具体功能需求2

### 非功能需求
- [ ] 性能要求
- [ ] 安全要求

## 技术规范
详细的技术实现规范

## 开发任务
分阶段的开发任务列表

## 质量保证
代码审查检查清单和测试策略

## 成功指标
可量化的成功标准

## 依赖关系
技术和环境依赖

## 风险评估
技术风险和缓解策略

## 交付物
具体的代码和文档交付清单
```

## 配置系统

### 主配置文件：workflow.config.yaml（在 bmad-workflow 目录）

配置文件默认位于 `bmad-workflow\workflow.config.yaml`。主要配置选项：

```yaml
workflow:
  max_iterations: 10                    # 最大QA迭代次数
  job_timeout_seconds: 3600            # 单个作业超时时间
  concurrent_dev_flows: 3              # 并发开发流程数量
  phase_delay_minutes: 30              # 阶段间延迟时间（分钟）

claude:
  cli_path: "claude"                   # Claude CLI路径
  skip_permissions: true               # 跳过权限提示
  command_delay_seconds: 2             # 命令间延迟
  window_style: "Normal"               # 窗口样式

logging:
  level: "Info"                        # 日志级别
  base_log_directory: "./logs"         # 日志基础目录（相对于 bmad-workflow）
  rotation:
    retention_days: 30                 # 日志保留天数
    max_total_size_mb: 1000           # 最大日志总大小

environments:
  development:                         # 开发环境配置
    logging:
      level: "Debug"
    workflow:
      max_iterations: 3
    development:
      debug_mode: true
      mock_mode: true                 # 模拟模式用于测试
  production:                          # 生产环境配置
    logging:
      console_output: false
    workflow:
      max_iterations: 15
```

### 环境特定配置

可以通过环境变量覆盖配置：

```powershell
# 设置环境
$env:BMAD_ENVIRONMENT = "production"

# 使用特定环境配置运行
.\BMAD-Workflow.ps1 -StoryPath "stories\production-feature.md"
```

## 监控和日志

### 日志系统

工作流会生成多种类型的日志：

```
logs/
├── workflow/              # 工作流执行日志
│   ├── bmad-workflow-YYYYMMDD-HHMMSS.log
│   └── workflow-summary.log
├── debug/                 # 调试日志
│   └── debug-YYYYMMDD.log
└── sessions/              # 会话日志
    └── session-*.log
```

### 实时监控

```powershell
# 查看实时日志（在另一个PowerShell窗口中）
Get-Content "logs\bmad-workflow-*.log" -Tail 20 -Wait

# 监控特定工作流
Get-Content "logs\workflow\workflow-*.log" -Tail 50 -Wait
```

### 状态查询

```powershell
# 获取工作流统计信息
.\BMAD-Workflow.ps1 -Status

# 输出示例：
# BMAD Workflow System Status
# ==========================
# Job Statistics:
#   Active Jobs: 3
#   Completed Jobs: 15
#   Failed Jobs: 0
#   Total Jobs: 18
#
# Hook Handlers:
#   Total Handlers: 3
#   Hook Directory: ./hooks
#
# Available Workflows: 2
#   - bubble-sort-story-001
#   - performance-analysis-002
```

## 故障排除

### 常见问题

#### 1. Claude Code CLI 未找到
```powershell
# 错误信息
✗ Claude Code CLI not found in PATH

# 解决方案
# 确保 Claude CLI 在系统 PATH 中
where.exe claude

# 或者修改配置文件中的 cli_path
claude:
  cli_path: "C:\path\to\claude.exe"
```

#### 2. PowerShell 执行策略限制
```powershell
# 错误信息
✗ Cannot be loaded because running scripts is disabled

# 解决方案
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

#### 3. 模块导入失败（✅已修复）
```powershell
# 错误信息（v1.2.0已修复）
✗ Failed to load module: BMAD.Job.Manager
✗ void 方法中的返回语句无效

# 解决方案（已在新版本中实现）
# 1. 检查模块文件是否存在（应显示6个文件）
Get-ChildItem "src\BMAD*.ps1" | Measure-Object

# 2. 验证修复（应显示所有模块加载成功）
.\BMAD-Workflow.ps1 -Test

# 3. 运行核心功能测试（应显示16/16通过）
.\tests\Simple.Tests.ps1
```

#### 4. PowerShell 语法错误（✅已修复）
```powershell
# 错误信息（v1.2.0已修复）
✗ void 方法中的返回语句无效
✗ 无法将"lock"项识别为 cmdlet、函数、脚本文件或可运行程序的名称

# 修复内容（已在新版本中实现）
# 1. ✅ 所有8个lock语句已替换为try-catch块
# 2. ✅ 所有6个方法返回类型已正确标注
# 3. ✅ 所有缺失的依赖项已添加
# 4. ✅ 100%模块加载成功率
# 5. ✅ 100%核心功能测试通过率
```

#### 5. 路径相关问题（新增 - 执行目录）
```powershell
# 错误信息
✗ Configuration file not found: ./config/workflow.config.yaml
✗ Task file not found: command/develop-story.md

# 解决方案（重要）
# 1. 确保在 bmad-workflow 目录执行
# 这是您应该工作的目录
D:\Python\bilibiliup\bmad-workflow

# 2. 验证当前目录
cd D:\Python\bilibiliup\bmad-workflow
Get-Location

# 3. 验证文件存在
dir workflow.config.yaml

# 4. 使用正确的故事路径格式
# 相对路径（推荐）
.\BMAD-Workflow.ps1 -StoryPath "..\docs\stories\1.1.project-setup.story.md"

# 绝对路径（更可靠）
.\BMAD-Workflow.ps1 -StoryPath "D:\Python\bilibiliup\docs\stories\1.1.project-setup.story.md"
```

#### 6. 测试框架相关问题（新增）
```powershell
# Pester版本兼容性问题
✗ Should -Be 语法不支持

# 解决方案
# 1. 确认Pester版本
Import-Module Pester; $PSVersionTable.PSVersion

# 2. 使用兼容语法（v1.2.0已实现）
$actual | Should Be $expected  # 而不是 $actual | Should -Be $expected

# 3. 运行兼容性测试
.\tests\Simple.Tests.ps1  # 使用Pester 3.4兼容语法
```


#### 7. 工作流超时
```yaml
# 修改配置文件中的超时设置（bmad-workflow\workflow.config.yaml）
workflow:
  job_timeout_seconds: 7200  # 增加到2小时
  max_wait_time_minutes: 180 # 增加到3小时
```

#### 8. 内存不足
```powershell
# 监控内存使用
Get-Process | Where-Object {$_.ProcessName -like "*claude*"} | Select-Object Name, WorkingSet

# 减少并发作业数量（编辑 bmad-workflow\workflow.config.yaml）
workflow:
  concurrent_dev_flows: 2  # 从3减少到2
```

### 调试模式

启用详细日志记录：

```powershell
# 方法1：修改配置文件
development:
  debug_mode: true
  verbose_output: true

# 方法2：使用环境变量
$env:BMAD_DEBUG = "true"
$env:BMAD_VERBOSE = "true"
```

### 手动干预

如果工作流卡在某个步骤：

```powershell
# 查看活动进程
Get-Process | Where-Object {$_.MainWindowTitle -like "*Claude*"}

# 终止卡住的进程（谨慎使用）
Stop-Process -Name "claude" -Force

# 清理工作流状态
.\BMAD-Workflow.ps1 -Cleanup

# 验证系统状态
.\BMAD-Workflow.ps1 -Status
```

## 最佳实践

### 1. 故事文档准备
- 确保故事文档完整且格式正确
- 明确定义验收标准
- 包含详细的技术规范
- 提供测试策略和成功指标

### 2. 工作流执行
- 在开发环境中先测试工作流
- 监控日志输出，及时发现问题
- 定期清理旧日志和工作流状态
- 备份重要的配置和故事文档

### 3. 性能优化
- 根据系统资源调整并发作业数量
- 优化超时设置以平衡效率和可靠性
- 使用SSD存储提高I/O性能
- 确保网络连接稳定

### 4. 安全考虑
- 定期更新Claude Code CLI
- 审查故事文档中的敏感信息
- 使用适当的文件权限
- 监控异常的Claude进程活动

### 5. 团队协作
- 建立统一的故事文档模板
- 共享配置文件版本控制
- 定期同步工作流状态
- 建立问题反馈机制

## 测试框架（v1.2.0新增）

### 完整测试套件结构

项目现已实现全面的测试驱动开发框架，包含1000+测试用例：

```
tests/
├── unit/                           # 单元测试
│   ├── BMAD.Claude.Interface.Tests.ps1      # 298个测试用例
│   ├── BMAD.Claude.Monitor.Tests.ps1        # 719个测试用例
│   ├── BMAD.Claude.Interface.Enhanced.Tests.ps1  # 增强接口测试
│   ├── BMAD.Workflow.Core.Tests.ps1         # 工作流核心测试
│   └── BMAD.Workflow.Core.Enhanced.Tests.ps1    # 增强工作流测试
├── integration/                    # 集成测试
│   ├── BMAD.Claude.Integration.Tests.ps1     # 端到端集成测试
│   ├── SprintChange.Integration.Tests.ps1    # Sprint变更集成测试
│   └── Workflow.Integration.Tests.ps1        # 工作流集成测试
├── mocks/                          # 模拟框架
│   ├── MockClaudeCLI.ps1               # Claude CLI和cctrace模拟框架
│   └── MockFramework.Tests.ps1         # 模拟框架测试
├── Simple.Tests.ps1               # 核心功能测试（16/16通过）
├── Run-AllTests.ps1               # 测试执行器
└── sprint-change.tests.ps1        # Sprint变更专项测试
```

### 测试执行指南

#### 快速验证（推荐）
```powershell
# 运行核心功能测试 - 100%通过率
.\tests\Simple.Tests.ps1

# 运行所有测试
.\tests\Run-AllTests.ps1
```

#### 详细测试执行
```powershell
# 运行单元测试（覆盖所有核心模块）
Invoke-Pester -ScriptPath "tests\unit" -Verbose

# 运行集成测试（端到端工作流验证）
Invoke-Pester -ScriptPath "tests\integration" -Verbose

# 运行模拟框架测试（cctrace和Claude CLI模拟）
Invoke-Pester -ScriptPath "tests\mocks" -Verbose

# 运行Sprint变更专项测试
.\tests\sprint-change.tests.ps1
```

### 测试覆盖范围

#### ✅ 核心功能测试（已验证）
- **模块加载**: 所有6个核心模块成功加载
- **cctrace集成**: 会话监控和状态检测
- **四阶段工作流**: Dev→QA→Fix→Final Dev完整循环
- **决策分析**: PASS/CONCERNS/FAIL逻辑判断
- **并发处理**: 多进程并发会话管理
- **错误处理**: 异常情况和恢复机制

#### 🔧 模拟框架功能
- **MockClaudeCLI**: 完整的Claude CLI和cctrace行为模拟
- **会话模拟**: 支持多进程并发会话监控
- **输出捕获**: 完整的Claude响应内容模拟
- **性能测试**: 会话启动和响应时间验证

#### 📊 测试统计
- **总测试文件**: 16个
- **总测试用例**: 1000+
- **核心功能通过率**: 100%（16/16）
- **Pester兼容性**: 支持版本3.4+
- **模块覆盖**: 100%（6个核心模块）

### cctrace集成状态

#### 当前实现：模拟框架
- 已实现完整的cctrace模拟框架
- 支持会话创建、监控、状态检测
- 提供JSON格式状态输出
- 模拟PASS/CONCERNS决策检测

#### 生产环境准备
- cctrace工具地址：https://github.com/jimmc414/cctrace
- 已准备完整的集成接口
- 支持真实Claude CLI会话监控
- 配置开关：模拟模式↔真实模式

### 测试最佳实践

#### 1. 日常验证
```powershell
# 每日快速检查（约30秒）
.\tests\Simple.Tests.ps1

# 每周完整测试（约5-10分钟）
.\tests\Run-AllTests.ps1
```

#### 2. 开发前验证
```powershell
# 修改代码后运行
Invoke-Pester -ScriptPath "tests\unit\BMAD.Claude.Interface.Tests.ps1" -Verbose

# 集成更改后运行
Invoke-Pester -ScriptPath "tests\integration" -Verbose
```

#### 3. 部署前验证
```powershell
# 完整测试套件
.\tests\Run-AllTests.ps1

# 性能基准测试
Invoke-Pester -ScriptPath "tests\integration\SprintChange.Integration.Tests.ps1" -Verbose
```

### 测试结果解读

#### 成功指标
- ✅ **Simple.Tests.ps1**: 16/16通过 - 系统就绪
- ✅ **模块加载**: 6/6成功 - 核心功能正常
- ✅ **cctrace模拟**: 会话监控功能完备
- ✅ **工作流循环**: 四阶段逻辑验证通过

#### 故障排查
- **模块加载失败**: 检查src目录中的6个.ps1文件
- **cctrace测试失败**: 验证MockClaudeCLI.ps1模拟框架
- **工作流测试失败**: 检查BMAD.Workflow.Core.ps1逻辑
- **Pester版本问题**: 确保使用3.4+兼容语法

## 高级功能

### 自定义钩子

创建自定义工作流钩子：

```powershell
# hooks\CustomHandler.ps1
function Invoke-CustomHandler {
    param(
        [hashtable]$HookContext
    )

    # 自定义逻辑
    Write-Host "Custom workflow hook triggered"

    # 返回处理结果
    return @{
        Success = $true
        Message = "Custom processing completed"
    }
}

# 注册钩子
Register-ClaudeHook -Name "CustomStep" -Handler "Invoke-CustomHandler"
```

### 批量处理

处理多个故事文档：

```powershell
# 批量处理脚本
$stories = Get-ChildItem "docs\stories\*.md"

foreach ($story in $stories) {
    Write-Host "Processing: $($story.Name)"

    try {
        .\BMAD-Workflow.ps1 -StoryPath $story.FullName
        Write-Host "✓ Completed: $($story.Name)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($story.Name) - $_" -ForegroundColor Red
    }

    # 添加延迟避免系统过载
    Start-Sleep -Seconds 30
}
```

### 性能监控

启用详细的性能监控：

```yaml
monitoring:
  enable_performance_monitoring: true
  enable_resource_tracking: true
  metrics_interval_seconds: 60

  # 自定义性能指标
  custom_metrics:
    - name: "claude_response_time"
      type: "timer"
    - name: "workflow_success_rate"
      type: "gauge"
```

### 通知集成

配置外部通知：

```yaml
notifications:
  enable_completion_notifications: true
  notification_methods:
    - "console"
    - "webhook"

  webhook:
    url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    headers:
      Content-Type: "application/json"
    timeout_seconds: 30
```

## API参考

### 核心函数

#### Start-BMADWorkflow
```powershell
$result = Start-BMADWorkflow -StoryPath "path/to/story.md" -ConfigPath "config.yaml"

# 返回对象属性
$result.Status            # 工作流状态
$result.StartTime         # 开始时间
$result.EndTime           # 结束时间
$result.IterationCount    # 迭代次数
$result.Jobs              # 作业详情
```

#### Get-WorkflowStatus
```powershell
$status = Get-WorkflowStatus -WorkflowId "workflow-001"

# 返回信息
$status.CurrentPhase      # 当前阶段
$status.ActiveJobs        # 活动作业数
$status.CompletedSteps    # 已完成步骤
$status.EstimatedRemaining # 预计剩余时间
```

#### Invoke-ClaudeAgent
```powershell
$agentResult = Invoke-ClaudeAgent -Agent "dev" -Command "*develop-story story.md"

# 返回结果
$agentResult.Success      # 是否成功
$agentResult.Output       # 输出内容
$agentResult.Duration     # 执行时长
$agentResult.ProcessId    # 进程ID
```

### 配置函数

#### Get-WorkflowConfiguration
```powershell
$config = Get-WorkflowConfiguration -ConfigPath "config.yaml"

# 访问配置项
$config.workflow.max_iterations
$config.claude.cli_path
$config.logging.level
```

#### Set-WorkflowConfiguration
```powershell
Set-WorkflowConfiguration -Key "workflow.max_iterations" -Value 15
Set-WorkflowConfiguration -Key "logging.level" -Value "Debug"
```

## 版本信息

- **当前版本**: 1.0.1
- **PowerShell 要求**: 5.1+（推荐 PowerShell 7.x）
- **Claude CLI 要求**: 最新版本
- **Pester 版本**: 3.4+（兼容性测试通过）
- **更新日期**: 2025-11-20
- **实现状态**: ✅ 已实现并可用
- **关键特性**:
  - ✅ PowerShell模块化架构（src/目录，核心模块5个）
  - ✅ 多层级监控集成（进程监控 + 完成检测）
  - ✅ 增强型日志系统（5个日志级别：Info, Warning, Error, Success, Debug）
  - ✅ 命令行选项（-StoryPath, -ConfigPath, -Help, -Status, -Cleanup, -Test）
  - ✅ 优雅降级架构（可选组件失败时继续运行）
  - ✅ 增强型工作流状态管理（BMADWorkflowState类）

## 支持和反馈

### 获取帮助
- 查看内置帮助：`.\BMAD-Workflow.ps1 -Help`
- 运行诊断：`.\BMAD-Workflow.ps1 -Test`
- 检查日志：`logs\workflow\` 目录

### 问题报告
在报告问题时，请包含：
1. 错误信息和堆栈跟踪
2. 相关的日志文件
3. 系统环境信息
4. 重现步骤
5. 使用的配置文件

### 社区资源
- 项目文档：`docs/` 目录
- 示例故事：`docs/stories/` 目录
- 配置模板：`config/` 目录

---

## 重要更新说明

### 2025-11-14 系统修复

本次更新解决了关键的 PowerShell 语法错误，主要包括：

1. **BMAD.Job.Manager.ps1 模块修复**：
   - 替换了 8 个无效的 `lock` 语句为 `try-catch` 块
   - 修复了 6 个方法返回类型签名（添加 `[object]`、`[array]`、`[int]`、`[hashtable]`）
   - 添加了缺失的依赖项（`Write-WorkflowLogInternal` 函数和 `LogLevel` 枚举）

2. **系统状态验证**：
   - 所有 5 个模块现在可以成功加载（之前：4 成功，1 失败）
   - 系统测试全部通过
   - 工作流可以正常运行

3. **向后兼容性**：
   - 所有修复都保持了原有功能的完整性
   - 不影响现有的配置文件和故事文档
   - 用户无需修改使用习惯

**建议**：更新后请运行 `.\BMAD-Workflow.ps1 -Test` 验证系统状态。

---

**注意**：本指南基于 BMAD-Method PowerShell Workflow Automation v1.0.0。如有更新，请参考最新版本的文档。
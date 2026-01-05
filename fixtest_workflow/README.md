# 测试工作流使用说明

## 概述

本工作流包含三个脚本，基于奥卡姆剃刀原则设计，实现测试文件的扫描、测试和自动修复：

1. **scan_test_files.py** - 扫描测试文件生成JSON列表，自动检测测试框架
2. **run_tests.py** - 执行pytest和unittest测试并收集ERROR/FAIL
3. **fix_tests.ps1** - 调用Claude自动修复测试

**新增功能**：支持pytest和unittest双测试框架，根据文件导入语句自动选择执行方式

## 文件结构

```
fixtest-workflow/
├── scan_test_files.py           # 脚本1：扫描测试文件
├── run_tests.py                 # 脚本2：执行pytest和unittest测试
├── demo_run_tests.py            # 演示版脚本（只测试前3个文件）
├── fix_tests.ps1                # 脚本3：Claude修复脚本
├── fileslist/                   # 固定文件夹：存放测试文件列表
│   ├── test_files_list_20260102_182150.json
│   └── ...
├── summaries/                   # 固定文件夹：存放测试结果汇总
│   ├── test_results_summary_20260102_182324.json
│   └── ...
└── USAGE.md                     # 本文档
```

## 执行流程

### 步骤1：扫描测试文件

```bash
cd fixtest-workflow
python scan_test_files.py
```

**输出**：
- 在 `fileslist/` 文件夹中生成 `test_files_list_{timestamp}.json`
- 包含所有测试文件的相对路径、绝对路径和文件大小

**示例输出**：
```
正在扫描测试文件...
项目根目录: D:\GITHUB\wuwa_actionseq_recorder_v2026
找到 1383 个测试文件
[OK] 测试文件列表已保存到: fixtest-workflow/fileslist/test_files_list_20260102_182150.json
  - 总计: 1383 个文件
  - 时间戳: 20260102_182150
```

### 步骤2：执行测试

#### 完整测试（推荐用于实际使用）
```bash
python run_tests.py
```

#### 演示测试（只测试前3个文件，快速演示）
```bash
python demo_run_tests.py
```

**输出**：
- 在 `summaries/` 文件夹中生成 `test_results_summary_{timestamp}.json`
- **仅记录有ERROR、FAIL或TIMEOUT的文件**
- 通过的文件**不**写入汇总JSON

**示例输出**：
```
使用测试文件列表: test_files_list_20260102_182150.json
正在加载测试文件列表...
[DEMO模式] 只测试前 3 个文件进行演示
实际使用时请将 demo_mode 设置为 False
超时设置: 120秒

[1/3] (33.3%) 正在测试: test_action_dropdown.py
  [ERROR] 错误 - 1 个错误
[2/3] (66.7%) 正在测试: test_format_fix.py
  [ERROR] 错误 - 1 个错误
[3/3] (100.0%) 正在测试: test_input_styles_optimized.py
  [ERROR] 错误 - 1 个错误

[OK] 演示测试结果汇总已保存到: summaries/test_results_summary_demo_20260102_182324.json

=== 演示测试汇总 ===
总计测试文件: 3 个
通过: 0 个
失败: 0 个
错误: 3 个
超时: 0 个
有问题文件: 3 个

[INFO] 有问题的文件已保存到汇总JSON中
请运行 fix_tests.ps1 进行自动修复
```

### 步骤3：自动修复

在PowerShell中运行：

```powershell
cd fixtest-workflow
.\fix_tests.ps1
```

**功能**：
1. 读取最新的 `test_results_summary_*.json` 文件
2. 获取 `files_with_errors` 中的所有测试文件
3. 对每个文件调用 `claude --dangerously-skip-permissions`
4. Claude提示词包含循环逻辑：
   - 修复→测试→验证→如果失败则继续修复
   - 直到所有ERROR和FAIL消除才停止
5. 显示Claude命令行窗口，观察修复过程

**示例输出**：
```
=== 测试文件自动修复脚本 ===

[INFO] 使用最新的汇总文件: test_results_summary_demo_20260102_182324.json
[INFO] 发现 3 个有问题的测试文件

=== 处理文件 1/3 ===
文件: test_action_dropdown.py
  错误数量: 1
    - ERROR: [1mcollecting ... [0mERROR: file or directory not found: test_action_dropdown.py

[INFO] 正在调用Claude进行修复...

=== Claude 修复过程 ===
（此时会打开Claude命令行窗口，显示修复过程）

[OK] Claude修复完成
=== 文件 1 处理完成 ===
```

### 步骤4：验证修复

```bash
python run_tests.py
```

检查是否所有ERROR和FAIL已修复（`files_with_errors`应为空）

## JSON文件格式

### test_files_list_{timestamp}.json
```json
{
  "scan_timestamp": "2026-01-02T18:21:50.744914",
  "timestamp": "20260102_182150",
  "project_root": "D:\\GITHUB\\wuwa_actionseq_recorder_v2026",
  "total_files": 1383,
  "test_files": [
    {
      "relative_path": "tests/services/test_input_service.py",
      "absolute_path": "D:\\GITHUB\\wuwa_actionseq_recorder_v2026\\tests\\services\\test_input_service.py",
      "file_size": 12345,
      "file_name": "test_input_service.py"
    }
  ]
}
```

### test_results_summary_{timestamp}.json
```json
{
  "scan_timestamp": "2026-01-02T18:21:50.744914",
  "test_start_time": "2026-01-02T18:23:23.798598",
  "timestamp": "20260102_182323",
  "total_files": 1383,
  "demo_files_tested": 3,
  "files_with_errors": [
    {
      "relative_path": "test_action_dropdown.py",
      "status": "completed",
      "result": "error",
      "errors": [
        {
          "type": "ERROR",
          "message": "[1mcollecting ... [0mERROR: file or directory not found: test_action_dropdown.py",
          "line": 8,
          "details": [
            "collected 0 items",
            "[33m============================ [0mno tests ran[0m in 0.00s [0m"
          ]
        }
      ],
      "failures": [],
      "execution_time": 0.21178221702575684,
      "timestamp": "2026-01-02T18:23:23.798598",
      "timeout": false
    }
  ],
  "summary": {
    "total": 3,
    "passed": 0,
    "failed": 0,
    "errors": 3,
    "timeouts": 0
  }
}
```

## 关键特性

### 1. 奥卡姆剃刀原则应用
- **最小化组件**：仅3个脚本，无额外依赖
- **最简逻辑**：直接扫描→测试→修复，无复杂状态管理
- **无持久化**：不维护复杂状态，每次重新扫描
- **直接委托**：Claude负责复杂修复逻辑

### 2. 文件管理
- 固定的 `fileslist/` 和 `summaries/` 文件夹
- 文件名包含时间戳（YYYYMMDD_HHMMSS格式）
- 避免文件名冲突

### 3. 错误处理
- 120秒超时设置
- 超时文件也记录到汇总JSON
- 完善的异常捕获和错误报告

### 4. Claude集成
- 显示命令行窗口，观察修复过程
- 提示词嵌入循环逻辑
- 自动验证修复结果

## 常见问题

### Q: 如何修改超时时间？
A: 在 `run_tests.py` 的 `run_pytest_with_timeout` 函数中修改 `timeout` 参数（默认120秒）

### Q: 如何测试所有文件而不是只测试前3个？
A: 将 `demo_run_tests.py` 中的 `demo_mode = True` 改为 `demo_mode = False`，然后运行 `python run_tests.py`

### Q: 如果claude命令不存在怎么办？
A: 确保已安装Claude CLI工具并添加到PATH中。安装方法：`npm install -g @anthropic-ai/claude`

### Q: 如何跳过某个测试文件？
A: 修改 `run_tests.py` 中的测试文件列表，过滤掉不需要的文件

### Q: 修复后如何验证？
A: 重新运行 `python run_tests.py`，检查 `files_with_errors` 是否为空

## 演示结果

**最新演示结果**：
- 测试文件数量：1383个
- 演示测试文件：3个
- 演示测试结果：3个错误
- 汇总JSON已生成：`summaries/test_results_summary_demo_20260102_182324.json`
- 可以运行 `.\fix_tests.ps1` 进行自动修复

## 总结

本工作流提供了一个完整的测试自动化解决方案，从扫描到修复全程自动化，符合奥卡姆剃刀原则，简洁高效。

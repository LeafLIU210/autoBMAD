# BasedPyright 自动化检查系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![BasedPyright](https://img.shields.io/badge/BasedPyright-Latest-green.svg)](https://github.com/DetachHead/basedpyright)

## 🎯 项目简介

这是一套完整的Python代码质量自动化检查系统，基于BasedPyright类型检查器。系统能够：

- ✅ 递归扫描项目中的所有Python文件
- ✅ 执行静态类型检查
- ✅ 生成UTF-8格式的详细检查报告
- ✅ 提供Markdown和HTML两种报告格式
- ✅ 统计和分类所有问题

## 📦 系统组成

| 文件 | 说明 | 类型 |
|------|------|------|
| `run_basedpyright_check.py` | 主检查脚本 | Python |
| `generate_basedpyright_report.py` | 报告生成脚本 | Python |
| `quick_basedpyright_check.py` | 快速一键工具 | Python |
| `run_basedpyright_full_check.ps1` | PowerShell一键脚本 | PowerShell |
| `BASEDPYRIGHT_CHECK_GUIDE.md` | 详细使用指南 | 文档 |

## 🚀 快速开始

### 方法1: Python快速工具（推荐）

```bash
python quick_basedpyright_check.py
```

### 方法2: PowerShell脚本

```powershell
.\run_basedpyright_full_check.ps1
```

### 方法3: 手动分步执行

```bash
# 步骤1: 运行检查
python run_basedpyright_check.py

# 步骤2: 生成报告
python generate_basedpyright_report.py
```

## 📋 前置要求

### 必需

- Python 3.8 或更高版本
- BasedPyright

### 安装BasedPyright

```bash
pip install basedpyright
```

## 📊 输出文件

### 检查结果文件

执行检查后会生成以下文件：

```
basedpyright_check_result_YYYYMMDD_HHMMSS.txt    # 文本格式详细结果
basedpyright_check_result_YYYYMMDD_HHMMSS.json   # JSON格式结构化数据
```

**文本文件内容：**
- 检查时间和元数据
- 所有被检查的Python文件列表
- 完整的BasedPyright输出
- 错误和警告统计

**JSON文件内容：**
- 结构化的诊断信息
- 按文件和规则分类的问题
- 详细的位置信息（行号、列号）
- 元数据（检查时间、文件列表等）

### 分析报告文件

生成报告后会创建：

```
basedpyright_report_YYYYMMDD_HHMMSS.md      # Markdown格式报告
basedpyright_report_YYYYMMDD_HHMMSS.html    # HTML格式可视化报告
```

**Markdown报告特性：**
- 📊 执行摘要表格
- 🔴 按文件和规则分组的错误
- ⚠️ 警告详情
- 📁 完整文件列表
- 📄 原始检查输出

**HTML报告特性：**
- 🎨 美观的Web界面
- 📈 可视化统计卡片
- 📋 交互式表格
- 🔍 便于浏览的错误列表
- 📱 响应式设计

## 🔧 使用示例

### 示例1: 检查默认src目录

```bash
$ python run_basedpyright_check.py
开始运行BasedPyright检查...
检查目录: src
================================================================================
找到 125 个Python文件
--------------------------------------------------------------------------------
运行文本格式检查...
✓ 文本结果已保存到: basedpyright_check_result_20251029_153045.txt
运行JSON格式检查...
✓ JSON结果已保存到: basedpyright_check_result_20251029_153045.json

================================================================================
检查完成统计:
--------------------------------------------------------------------------------
检查文件数: 125
错误 (Error): 15
警告 (Warning): 8
信息 (Information): 3
================================================================================
```

### 示例2: 检查自定义目录

```bash
python run_basedpyright_check.py src/models
```

### 示例3: 生成报告

```bash
$ python generate_basedpyright_report.py
BasedPyright 报告生成器
================================================================================
未指定输入文件，正在查找最新的检查结果...
使用文件:
  - 文本结果: basedpyright_check_result_20251029_153045.txt
  - JSON结果: basedpyright_check_result_20251029_153045.json

✓ 已加载文本结果: basedpyright_check_result_20251029_153045.txt
✓ 已加载JSON结果: basedpyright_check_result_20251029_153045.json
✓ Markdown报告已生成: basedpyright_report_20251029_153120.md
✓ HTML报告已生成: basedpyright_report_20251029_153120.html

================================================================================
报告生成完成!
  - Markdown: basedpyright_report_20251029_153120.md
  - HTML: basedpyright_report_20251029_153120.html
================================================================================
```

## 📈 报告示例

### Markdown报告片段

```markdown
## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 125 |
| ❌ 错误 (Error) | 15 |
| ⚠️ 警告 (Warning) | 8 |
| ℹ️ 信息 (Information) | 3 |
| ⏱️ 检查耗时 | 2.35 秒 |

## 🔴 错误详情

### 按规则分组

- `reportMissingTypeArgument`: 8 次
- `reportOptionalMemberAccess`: 4 次
- `reportUnknownMemberType`: 3 次

### 详细错误列表

#### 1. src/models/database.py:45

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 45 行, 第 12 列
- **错误信息**: "dict" 泛型类应有类型参数
```

### HTML报告界面

HTML报告提供：
- 彩色统计卡片（文件数、错误、警告、信息）
- 按规则分组的表格
- 可点击的错误详情
- 美观的视觉设计

## ⚙️ 配置

### BasedPyright配置

在项目根目录的 `pyproject.toml` 中配置：

```toml
[tool.basedpyright]
typeCheckingMode = "standard"  # 或 "basic", "strict"
include = ["src"]
exclude = ["tests", "build", "dist", "__pycache__"]
reportMissingTypeStubs = false
```

### 自定义检查范围

修改 `run_basedpyright_check.py` 的主函数：

```python
# 默认检查src目录
src_dir = "src"

# 可以修改为其他目录
src_dir = "src/models"
```

## 🎓 高级用法

### 1. CI/CD集成

**GitHub Actions示例：**

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  basedpyright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install basedpyright
      - name: Run BasedPyright Check
        run: |
          python run_basedpyright_check.py
      - name: Generate Report
        run: |
          python generate_basedpyright_report.py
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: basedpyright-reports
          path: basedpyright_report_*.html
```

### 2. 定时任务

**Windows计划任务（PowerShell）：**

```powershell
# 创建每日检查任务
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File D:\Python\fcmrawler\run_basedpyright_full_check.ps1"
  
$trigger = New-ScheduledTaskTrigger -Daily -At 9am

Register-ScheduledTask -Action $action -Trigger $trigger `
  -TaskName "BasedPyright Daily Check" `
  -Description "每日代码质量检查"
```

### 3. 与其他工具结合

```bash
# 运行多种代码质量检查
python run_basedpyright_check.py  # 类型检查
flake8 src/                        # 代码风格
mypy src/                          # 另一种类型检查
pylint src/                        # 代码规范
```

## 🔍 故障排除

### 问题1: ModuleNotFoundError: No module named 'basedpyright'

**原因**: 未安装basedpyright

**解决方案**:
```bash
pip install basedpyright
```

### 问题2: UnicodeDecodeError

**原因**: 编码问题

**解决方案**:
- Windows PowerShell: 在脚本开始添加
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```
- Python: 所有文件已使用UTF-8编码

### 问题3: 未找到检查结果文件

**原因**: 检查脚本未成功执行

**解决方案**:
1. 先运行 `python run_basedpyright_check.py`
2. 确认生成了 `.txt` 和 `.json` 文件
3. 再运行报告生成脚本

### 问题4: PowerShell脚本执行策略

**原因**: Windows默认禁止脚本执行

**解决方案**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 详细文档

完整的使用指南请参考：[BASEDPYRIGHT_CHECK_GUIDE.md](BASEDPYRIGHT_CHECK_GUIDE.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📄 许可证

本项目遵循主项目的许可证。

## 🔗 相关链接

- [BasedPyright官方仓库](https://github.com/DetachHead/basedpyright)
- [Pyright文档](https://github.com/microsoft/pyright)
- [Python类型提示指南](https://docs.python.org/3/library/typing.html)

---

**最后更新**: 2025-10-29  
**版本**: 1.0.0  
**维护者**: FCMRawler Team

# BasedPyright 检查系统使用指南

## 📋 概述

这是一套完整的BasedPyright代码检查和报告生成系统，用于自动化Python代码质量检查。

## 🎯 功能特性

- ✅ 递归扫描src文件夹及其所有子文件夹中的Python文件
- ✅ 生成UTF-8编码的文本检查结果
- ✅ 生成JSON格式的详细检查数据
- ✅ 自动生成Markdown和HTML格式的分析报告
- ✅ 统计错误、警告、信息的数量和分布
- ✅ 按文件、按规则分组展示问题
- ✅ 一键执行检查和报告生成

## 📦 组件说明

### 1. `run_basedpyright_check.py` - 检查脚本

**功能：**
- 遍历检查指定目录下的所有Python文件
- 运行basedpyright进行类型检查
- 生成UTF-8格式的txt和json结果文件

**使用方法：**
```bash
# 检查src目录（默认）
python run_basedpyright_check.py

# 检查指定目录
python run_basedpyright_check.py <目录路径>
```

**输出文件：**
- `basedpyright_check_result_YYYYMMDD_HHMMSS.txt` - 文本格式结果
- `basedpyright_check_result_YYYYMMDD_HHMMSS.json` - JSON格式结果

**文件内容：**
- 检查时间和基本信息
- 检查的文件列表
- 完整的检查输出
- 统计摘要

### 2. `generate_basedpyright_report.py` - 报告生成脚本

**功能：**
- 从检查结果文件生成详细分析报告
- 支持Markdown和HTML两种格式
- 提供统计图表和详细错误列表

**使用方法：**
```bash
# 自动使用最新的检查结果
python generate_basedpyright_report.py

# 指定txt文件
python generate_basedpyright_report.py <txt文件>

# 指定txt和json文件
python generate_basedpyright_report.py <txt文件> <json文件>
```

**输出文件：**
- `basedpyright_report_YYYYMMDD_HHMMSS.md` - Markdown报告
- `basedpyright_report_YYYYMMDD_HHMMSS.html` - HTML报告

**报告内容：**
- 📊 执行摘要（文件数、错误数、警告数等）
- 🔴 错误详情（按文件、按规则分组）
- ⚠️ 警告详情
- 📁 检查的文件列表
- 📄 原始检查输出

### 3. `run_basedpyright_full_check.ps1` - 一键执行脚本（PowerShell）

**功能：**
- 检查Python和basedpyright环境
- 自动执行检查和报告生成
- 显示生成的文件列表

**使用方法：**
```powershell
# 在PowerShell中运行
.\run_basedpyright_full_check.ps1
```

## 🚀 快速开始

### 方式一：使用一键脚本（推荐）

```powershell
# Windows PowerShell
.\run_basedpyright_full_check.ps1
```

### 方式二：手动执行

```bash
# 步骤1：运行检查
python run_basedpyright_check.py

# 步骤2：生成报告
python generate_basedpyright_report.py
```

## 📊 报告示例

### Markdown报告结构

```markdown
# BasedPyright 检查报告

**生成时间**: 2025-10-29 15:30:00

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 120 |
| ❌ 错误 | 15 |
| ⚠️ 警告 | 8 |
| ℹ️ 信息 | 3 |

## 🔴 错误详情

### 按文件分组
- `src/models/database.py`: 5 个错误
- `src/services/config_service.py`: 3 个错误
...

### 按规则分组
- `reportMissingTypeArgument`: 8 次
- `reportOptionalMemberAccess`: 4 次
...

### 详细错误列表
1. src/models/database.py:45
   - **规则**: reportMissingTypeArgument
   - **错误信息**: "dict" 泛型类应有类型参数
...
```

### HTML报告特性

- 🎨 美观的可视化界面
- 📈 统计卡片展示
- 📋 交互式表格
- 🔍 易于浏览的错误列表

## ⚙️ 配置

### basedpyright配置文件

项目根目录的 `pyproject.toml` 中可以配置basedpyright：

```toml
[tool.basedpyright]
typeCheckingMode = "standard"
include = ["src"]
exclude = ["tests", "build", "dist"]
```

### 环境要求

- Python 3.8+
- basedpyright (`pip install basedpyright`)

## 📝 使用场景

### 1. 日常开发检查

```bash
# 在提交代码前运行检查
python run_basedpyright_check.py
```

### 2. CI/CD集成

```yaml
# .github/workflows/check.yml
- name: Run BasedPyright Check
  run: |
    python run_basedpyright_check.py
    python generate_basedpyright_report.py
```

### 3. 定期代码质量审查

```powershell
# 每周运行完整检查
.\run_basedpyright_full_check.ps1
```

## 🔧 故障排除

### 问题1: 找不到basedpyright

**解决方案：**
```bash
pip install basedpyright
```

### 问题2: 编码错误

**解决方案：**
- 确保使用UTF-8编码
- Windows PowerShell中设置编码：
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### 问题3: 权限问题

**解决方案：**
```powershell
# 允许运行PowerShell脚本
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📈 最佳实践

1. **定期检查**：每天或每次提交前运行检查
2. **保存报告**：将报告存档以跟踪代码质量趋势
3. **修复优先级**：先修复ERROR级别问题，再处理WARNING
4. **团队协作**：将报告分享给团队成员
5. **CI集成**：集成到持续集成流程中

## 🎓 进阶用法

### 自定义检查范围

```bash
# 只检查特定子目录
python run_basedpyright_check.py src/models

# 检查多个目录（需修改脚本）
```

### 过滤特定规则

在 `pyproject.toml` 中配置：

```toml
[tool.basedpyright]
reportMissingTypeStubs = false
reportUnknownMemberType = false
```

### 结合其他工具

```bash
# 运行多种检查工具
python run_basedpyright_check.py
flake8 src/
mypy src/
```

## 📞 支持

如有问题或建议，请：
1. 查看basedpyright官方文档
2. 检查项目的 `CODE_QUALITY_TOOLS_README.md`
3. 提交Issue到项目仓库

## 📄 许可

本工具遵循项目主许可证。

---

**最后更新**: 2025-10-29
**版本**: 1.0.0

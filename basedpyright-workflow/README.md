# BasedPyright-Workflow - 通用 Python 代码质量工作流工具

## 🎯 简介

BasedPyright-Workflow 是一个通用的 Python 代码质量检查、报告生成和错误修复工作流工具，基于奥卡姆剃刀原则设计。

**重要提示：** 工具需要在 `basedpyright-workflow` 子目录中运行，确保配置文件 `.bpr.json` 能够被正确加载。

**核心特性：**
- ✅ **完整的类型检查**：基于 basedpyright
- ✅ **Ruff 集成**：代码检查、格式化、自动修复
- ✅ **智能冲突解决**：类型错误优先于代码风格
- ✅ **Markdown 报告**：详细的分析报告
- ✅ **错误提取**：结构化错误数据用于修复
- ✅ **Claude 集成**：与 Claude Code 无缝集成
- ✅ **项目本地化**：直接在项目文件夹中使用
- ✅ **简单高效**：遵循 DRY/KISS/YAGNI 原则

cd basedpyright-workflow/
python -m basedpyright_workflow workflow --include-ruff --format-after-fix
python -m basedpyright_workflow workflow --include-ruff
.\fix_project_errors.ps1 -IncludeRuff

## 📦 安装

### 方式1：项目内安装（推荐）

```bash
# 在项目根目录安装
cd your-project/
pip install -e basedpyright-workflow
```

### 方式2：直接运行模块

```bash
# 无需安装，直接在子目录中运行模块
cd basedpyright-workflow/
python -m basedpyright_workflow --help
```

## 🚀 快速开始

**重要说明：** 所有命令都需要在 `basedpyright-workflow` 子目录中运行：

```bash
cd basedpyright-workflow/
python -m basedpyright_workflow <命令>
```

### 完整工作流（推荐）

```bash
# 在项目根目录运行完整工作流
# 包括：类型检查 → 报告 → 提取错误
cd my-python-project/
cd basedpyright-workflow/

python -m basedpyright_workflow workflow

# 输出：
# - .bpr/results/basedpyright_check_result_*.txt
# - .bpr/results/basedpyright_check_result_*.json
# - .bpr/reports/basedpyright_report_*.md
# - .bpr/results/basedpyright_errors_only_*.json
```

### Ruff 集成工作流

```bash
# 包含 Ruff 代码检查和格式化
python -m basedpyright_workflow workflow --include-ruff

# 包含 Ruff 检查、自动修复和格式化
python -m basedpyright_workflow workflow --include-ruff --format-after-fix
```

### 分步执行

#### 1. 类型检查

```bash
# 检查 src/ 目录（默认）
python -m basedpyright_workflow check

# 指定源目录
python -m basedpyright_workflow check --path ./lib

# 输出：
# .bpr/results/basedpyright_check_result_YYYYMMDD_HHMMSS.txt
# .bpr/results/basedpyright_check_result_YYYYMMDD_HHMMSS.json
```

#### 2. 生成报告

```bash
# 自动查找最新的检查结果，生成 Markdown 报告
python -m basedpyright_workflow report

# 输出：
# .bpr/reports/basedpyright_report_YYYYMMDD_HHMMSS.md
```

#### 3. 提取错误

```bash
# 从检查结果中提取 ERROR 级别错误
python -m basedpyright_workflow fix

# 输出：
# .bpr/results/basedpyright_errors_only_YYYYMMDD_HHMMSS.json
```

#### 4. 自动修复

```powershell
# 运行 PowerShell 脚本进行自动修复（项目本地版本）
# 自动查找最新错误文件
powershell .\basedpyright-workflow\fix_project_errors.ps1
.\basedpyright-workflow\fix_project_errors.ps1

# 包含 Ruff 错误
powershell .\basedpyright-workflow\fix_project_errors.ps1 -IncludeRuff

# 手动指定错误文件
powershell .\basedpyright-workflow\fix_project_errors.ps1 -ErrorsFile ".bpr\results\errors.json"
```

## 📖 命令详解

### `basedpyright check` - 类型检查

运行 basedpyright 类型检查，生成文本和 JSON 结果。

**参数：**
- `--path PATH` - 源代码目录（默认：src）

**示例：**
```bash
python -m basedpyright_workflow check --path ./src
```

**退出码：**
- 0 - 检查成功，无错误
- 1 - 检查完成，发现错误
- 其他 - 错误

**输出示例：**
```
================================================================================
开始运行 BasedPyright 检查...
检查目录: src
================================================================================
找到 89 个 Python 文件
--------------------------------------------------------------------------------
运行文本格式检查...
运行 JSON 格式检查...
JSON 结果已保存到: .bpr\results\basedpyright_check_result_20251129_102544.json

检查完成统计:
--------------------------------------------------------------------------------
检查文件数: 89
错误 (Error): 886
警告 (Warning): 7158
信息 (Information): 0

详细统计 (来自 JSON):
  分析文件数: 89
  错误数: 886
  警告数: 7158
  检查耗时: 7.08 秒
================================================================================
```

### `basedpyright report` - 生成报告

从检查结果生成详细的 Markdown 分析报告。

**示例：**
```bash
python -m basedpyright_workflow report
```

**报告格式：**
- 执行摘要（文件数、错误/警告/信息数）
- 错误详情（按文件、按规则分组）
- 详细错误列表（文件:行号、规则、消息）
- 警告详情（按严重程度分类）
- 检查的文件列表

**报告示例：**
```markdown
# BasedPyright 检查报告
**生成时间**: 2025-11-29 10:27:34
**检查时间**: 2025-11-29T10:26:07.625198
**检查目录**: `..\src`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 89 |
| ❌ 错误 (Error) | 886 |
| ⚠️ 警告 (Warning) | 7158 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 7.08 秒 |

## 🔴 错误详情

### 按文件分组

- `d:\Python\bilibiliup\src\utils\logging.py`: 168 个错误
- `d:\Python\bilibiliup\src\storage\repositories.py`: 94 个错误
...

### 按规则分组

- `unknown`: 884 次
- `reportMissingTypeArgument`: 2 次

### 详细错误列表

#### 1. d:\Python\bilibiliup\src\utils\logging.py:45

- **规则**: `unknown`
- **位置**: 第 45 行, 第 12 列
- **错误信息**: "Logger | None" 类型的条件值无效
```

### `basedpyright fix` - 提取错误

从检查结果中提取 ERROR 级别错误，生成结构化 JSON 数据。

**示例：**
```bash
python -m basedpyright_workflow fix
```

**输出格式：**
```json
{
  "metadata": {
    "source_file": ".bpr/results/basedpyright_check_result_*.txt",
    "extraction_time": "2025-11-29T10:32:49.305355",
    "total_files_with_errors": 61,
    "total_errors": 884
  },
  "errors_by_file": [
    {
      "file": "d:\\Python\\bilibiliup\\src\\utils\\logging.py",
      "error_count": 168,
      "errors_by_rule": {
        "unknown": 168
      },
      "errors": [
        {
          "line": 45,
          "column": 12,
          "message": "条件值无效",
          "rule": "unknown"
        }
      ]
    }
  ]
}
```

### `basedpyright workflow` - 完整工作流

顺序执行完整工作流：check → report → fix。

**参数：**
- `--path PATH` - 源代码目录（默认：src）
- `--include-ruff` - 包含 Ruff 代码检查
- `--format-after-fix` - 在修复后应用格式化

**示例：**
```bash
# 基础工作流
python -m basedpyright_workflow workflow --path ./src

# 包含 Ruff 检查
python -m basedpyright_workflow workflow --include-ruff

# 完整工作流：检查 + Ruff + 格式化
python -m basedpyright_workflow workflow --include-ruff --format-after-fix
```

**执行流程：**
```
Step 1/3: 运行类型检查...
  ✓ TXT结果: .bpr/results/basedpyright_check_result_*.txt
  ✓ JSON结果: .bpr/results/basedpyright_check_result_*.json

Step 2/3: 生成分析报告...
  ✓ Markdown报告: .bpr/reports/basedpyright_report_*.md

Step 3/3: 提取错误数据...
  ✓ 错误JSON: .bpr/results/basedpyright_errors_only_*.json

完整工作流完成！下一步：运行 PowerShell 脚本开始自动修复

    powershell .\fix_project_errors.ps1
```

## 🔧 PowerShell 脚本

`fix_project_errors.ps1` - 项目本地版本，与 Claude Code 集成，自动修复错误。

### 特点

- ✅ 项目本地化设计，直接在项目根目录使用
- ✅ 支持 BasedPyright 和 Ruff 错误
- ✅ 智能冲突解决（类型错误优先）
- ✅ 逐文件顺序处理（避免并发问题）
- ✅ Ruff 自动修复集成
- ✅ 自动查找错误文件
- ✅ UTF-8 编码支持
- ✅ 增强日志系统

### 使用

```powershell
# 自动查找最新错误文件
powershell .\fix_project_errors.ps1

# 包含 Ruff 错误和自动修复
powershell .\fix_project_errors.ps1 -IncludeRuff -ApplyRuffFixes

# 指定错误文件和间隔时间
powershell .\fix_project_errors.ps1 -ErrorsFile ".bpr\results\errors.json"
```

### 参数说明

- `-IncludeRuff` - 包含 Ruff 错误处理
- `-ApplyRuffFixes` - 应用 Ruff 自动修复
- `-PreferRuff` - 在冲突时优先选择 Ruff 修复建议
- `-IntervalSeconds` - 文件处理间隔时间（默认60秒）
- `-ProjectPath` - 项目根目录路径（默认当前目录）

### 自动查找逻辑

脚本会在 `.bpr/results/` 目录中查找错误文件：
1. 优先查找 `unified_errors_only_*.json`（Ruff 集成）
2. 回退到 `basedpyright_errors_only_*.json`

## 📊 实际测试结果

### 测试项目：bilibiliup

```bash
# 运行完整工作流
$ python -m basedpyright_workflow workflow --path ../src

[1/3] 运行类型检查...
  ✓ 找到 89 个 Python 文件
  ✓ TXT结果: .bpr\results\basedpyright_check_result_20251129_102544.txt
  ✓ JSON结果: .bpr\results\basedpyright_check_result_20251129_102544.json
  发现 886 个错误

[2/3] 生成分析报告...
  ✓ Markdown报告: .bpr\reports\basedpyright_report_20251129_102734.md

[3/3] 提取错误数据...
  ✓ 错误JSON: .bpr\results\basedpyright_errors_only_20251129_103249.json
  有错误的文件数: 61
  错误总数: 884

[OK] 完整工作流完成！
下一步：运行 PowerShell 脚本开始自动修复

    powershell .\fix_project_errors.ps1

# 查看生成的文件
$ ls .bpr/results/
basedpyright_check_result_20251129_102544.txt
basedpyright_check_result_20251129_102544.json
basedpyright_errors_only_20251129_103249.json

$ ls .bpr/reports/
basedpyright_report_20251129_102734.md
```

### Ruff 集成测试

```bash
# 运行包含 Ruff 的工作流
$ python -m basedpyright_workflow workflow --include-ruff

[1/4] 运行类型检查...
  ✓ BasedPyright 检查完成

[2/4] 运行 Ruff 检查...
  ✓ Ruff 检查完成
  ✓ 发现 245 个 Ruff 问题

[3/4] 生成分析报告...
  ✓ 合并报告: .bpr\reports\basedpyright_report_*.md

[4/4] 提取错误数据...
  ✓ 统一错误JSON: .bpr\results\unified_errors_only_*.json
  ✓ BasedPyright 错误: 884 个
  ✓ Ruff 错误: 245 个

[OK] Ruff 集成工作流完成！
下一步：运行 PowerShell 脚本开始自动修复

    powershell .\fix_project_errors.ps1 -IncludeRuff -ApplyRuffFixes
```

### 检查结果统计

- **检查文件数**: 89 个 Python 文件
- **错误 (Error)**: 886 个
- **警告 (Warning)**: 7158 个
- **信息 (Information)**: 0 个
- **检查耗时**: 7.08 秒

### 主要错误文件（Top 5）

| 文件 | 错误数 |
|------|--------|
| `src/utils/logging.py` | 168 |
| `src/storage/repositories.py` | 94 |
| `src/ai/engagement_quality_scorer.py` | 59 |
| `src/output/html_generator.py` | 40 |
| `src/storage/migrations.py` | 37 |

## ⚙️ 配置文件

### `.bpr.json` 配置格式

在 `basedpyright-workflow` 子目录中创建 `.bpr.json` 文件来自定义工作流：

```json
{
  "project_name": "你的项目名称",
  "source_directory": "src",
  "ruff": {
    "enabled": true,
    "check_enabled": true,
    "format_enabled": true,
    "fix_enabled": true,
    "line_length": 88,
    "target_version": "py311",
    "select_rules": ["E", "W", "F", "I", "B", "C4", "UP", "N"],
    "ignore_rules": ["E501"]
  },
  "checker": {
    "python_version": "3.11",
    "strict_mode": false,
    "type_check_mode": "basic"
  },
  "unified": {
    "conflict_resolution": "basedpyright_priority"
  }
}
```

### 主要配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `source_directory` | `src` | 源代码目录 |
| `ruff.enabled` | `true` | 是否启用 Ruff |
| `ruff.line_length` | `88` | 代码行长度限制 |
| `ruff.target_version` | `py311` | Python 目标版本 |
| `checker.strict_mode` | `false` | 是否启用严格模式 |

### 冲突解决策略

- `basedpyright_priority`: 类型错误优先（推荐）
- `ruff_priority`: Ruff 优先
- `smart`: 智能决策

## 🎯 通用化特性

### 适用于任意 Python 项目

```bash
# 在任何 Python 项目根目录
cd any-python-project/
cd basedpyright-workflow/

# 运行检查（默认检查 src/ 目录）
python -m basedpyright_workflow check

# 或指定源码目录
python -m basedpyright_workflow check --path ./lib

# 生成报告
python -m basedpyright_workflow report

# 如果你的项目没有 src/ 目录
python -m basedpyright_workflow check --path ..
```

### 不依赖项目特定配置

- ✅ 不硬编码项目名称
- ✅ 不依赖特定目录结构
- ✅ 支持任意源码目录
- ✅ 可配置输出位置
- ✅ 纯 Python 实现，无外部依赖

## 📝 开发者指南

### 项目结构

```
basedpyright-workflow/
├── basedpyright_workflow/          # Python 包
│   ├── cli.py                     # CLI 接口
│   ├── config/                    # 配置系统
│   │   └── settings.py           # 配置管理
│   ├── core/                      # 核心模块
│   │   ├── checker.py            # 类型检查
│   │   ├── reporter.py           # 报告生成
│   │   ├── extractor.py          # 错误提取
│   │   └── ruff_integration.py   # Ruff 集成
│   └── utils/                     # 工具函数
│       ├── scanner.py            # 文件扫描
│       ├── paths.py              # 路径处理
│       └── ruff_utils.py         # Ruff 工具
├── fix_project_errors.ps1        # 项目本地 PowerShell 修复脚本
├── .bpr.example.json             # 示例配置文件
├── PROJECT_USAGE.md               # 项目使用文档
├── pyproject.toml                # 包配置
└── README.md                     # 本文档
```

### 核心模块

**config/settings.py** - 配置管理系统
- `ConfigManager` - 配置管理器，支持文件、环境变量、CLI参数
- `BMADWorkflowConfig` - 完整工作流配置
- `RuffConfig` - Ruff 专用配置

**utils/ruff_utils.py** - Ruff 工具函数
- `check_ruff_installation()` - 检查 Ruff 安装
- `run_ruff_check()` - 执行 Ruff 检查
- `parse_ruff_output()` - 解析 Ruff 输出

**core/ruff_integration.py** - Ruff 集成核心
- `RuffIntegrator` - Ruff 集成器
- `ResultMerger` - 结果合并器
- `ConflictResolver` - 冲突解决器
- `FixSuggestionMerger` - 修复建议合并器

**core/checker.py** - 类型检查器
- `TypeChecker(source_dir, output_dir)` - 初始化检查器
- `run_check()` - 运行完整检查流程
- 支持 Ruff 并行检查

**core/reporter.py** - 报告生成器
- `ReportGenerator(txt_file, json_file)` - 初始化生成器
- `load_results()` - 加载检查结果
- `generate_markdown(output_file)` - 生成统一 Markdown 报告

**core/extractor.py** - 错误提取器
- `ErrorExtractor(txt_file, json_file)` - 初始化提取器
- `extract_errors()` - 提取错误数据
- 支持统一错误格式（BasedPyright + Ruff）

**cli.py** - 命令行接口
- `cmd_check(args)` - 处理 check 命令
- `cmd_report(args)` - 处理 report 命令
- `cmd_fix(args)` - 处理 fix 命令
- `cmd_workflow(args)` - 处理 workflow 命令，支持 Ruff 集成

## 📚 文档

- **PROJECT_USAGE.md** - 项目内使用详细文档
- **.bpr.example.json** - 示例配置文件
- **pyproject.toml** - 包配置和依赖

## 🔍 故障排查

### 问题1：找不到 basedpyright-workflow 命令

```bash
# 错误信息
FileNotFoundError: 未找到 basedpyright-workflow 命令

# 解决方案
# 确保在项目根目录安装了工具
pip install -e path/to/basedpyright-workflow

# 或直接运行模块（需要进入子目录）
cd basedpyright-workflow/
python -m basedpyright_workflow --help
```

### 问题2：找不到 basedpyright 命令

```bash
# 错误信息
FileNotFoundError: 未找到 basedpyright 命令

# 解决方案
pip install basedpyright
```

### 问题3：找不到 ruff 命令

```bash
# 错误信息
FileNotFoundError: 未找到 ruff 命令

# 解决方案
pip install ruff

# 或使用 --include-ruff 时会自动提示安装
```

### 问题4：源目录不存在

```bash
# 错误信息
FileNotFoundError: 源目录不存在: src

# 解决方案
basedpyright-workflow check --path ./my_source_dir
```

### 问题5：编码错误

```bash
# 在 Windows PowerShell 中运行
# 确保 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 问题6：找不到检查结果文件

```bash
# 错误信息
未找到检查结果文件

# 解决方案
# 1. 先运行检查
basedpyright-workflow check

# 2. 再运行报告或提取
basedpyright-workflow report
basedpyright-workflow fix
```

### 问题7：配置文件不生效

```bash
# 检查配置文件位置（位于basedpyright-workflow子目录中）
cd basedpyright-workflow/
ls -la .bpr.json

# 验证配置格式
python -c "import json; print(json.load(open('.bpr.json')))"
```

### 问题8：Ruff 集成问题

```bash
# 检查 Ruff 是否安装
python -m ruff --version

# 手动测试 Ruff
python -m ruff check src/

# 查看详细错误信息
basedpyright-workflow workflow --include-ruff --verbose
```

## 📈 性能

### 检查性能

- **文件扫描**：O(n) 线性时间复杂度
- **类型检查**：基于 basedpyright 原生性能
- **报告生成**：优化后的模板渲染

**实测数据：**
- 89 个文件，7.08 秒完成
- 平均每个文件 ~80ms
- 包含 886 个错误 + 7158 个警告

### 内存使用

- **检查结果**：JSON 文件约 100KB-1MB
- **错误提取**：仅提取 ERROR，约 10-100KB
- **报告文件**：Markdown 文件约 50-200KB

## 🔄 版本历史

### v2.0.0 (2025-12-17)

✅ Ruff 深度集成完成
- 集成 Ruff 代码检查、格式化、自动修复
- 智能冲突解决（类型错误优先）
- 项目本地化设计（.bpr/ 目录）
- 统一错误格式和报告
- 增强的 PowerShell 修复脚本
- 完整的配置系统支持

### v1.0.0 (2025-11-29)

✅ 通用化重构完成
- 删除 640+ 行冗余代码
- 重构为模块化 Python 包
- 实现完整 CLI 接口
- 仅支持 Markdown 报告
- PowerShell 脚本增强到 v2.0
- 所有命令测试验证

### v0.5.0 (旧版本)

- 项目专用工具
- 8个脚本文件
- PowerShell 包装器
- 支持 HTML 和 Markdown

## 🎉 总结

BasedPyright-Workflow 已经从 `bilibiliup` 项目专用工具成功重构为**通用 Python 代码质量工作流工具**：

- **深度集成**：BasedPyright + Ruff 双引擎
- **项目本地化**：直接在项目文件夹中使用
- **智能解决**：类型错误优先于代码风格冲突
- **配置灵活**：支持文件、环境变量、CLI参数
- **功能完整**：检查、报告、修复、格式化一体化
- **输出一致**：保持现有格式，平滑升级

**核心价值：一个命令，双重保障，智能修复。**

## 📞 支持

遇到问题或有建议？请查看：
- **PROJECT_USAGE.md** - 详细使用文档
- **.bpr.example.json** - 配置示例

## 📄 许可证

MIT License

---

**Ruff 集成完成时间**：2025-12-17
**总开发时间**：约14小时
**当前版本**：v2.0.0
**状态**：✅ 生产可用，Ruff 深度集成

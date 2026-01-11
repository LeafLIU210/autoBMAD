# 在项目中使用 BasedPyright-Workflow

## 概述

BasedPyright-Workflow 现已支持直接在项目文件夹中使用，无需复杂的安装配置。只需在项目根目录运行命令即可。

## 快速开始

### 1. 安装

```bash
# 在项目根目录安装
pip install -e path/to/basedpyright-workflow
```

### 2. 基本使用

```bash
# 在项目根目录运行类型检查
basedpyright-workflow workflow

# 指定源代码目录
basedpyright-workflow workflow --path src

# 指定不同的源代码目录
basedpyright-workflow workflow --path app
```

### 3. 包含 Ruff 检查

```bash
# 包含 ruff 代码检查
basedpyright-workflow workflow --include-ruff

# 包含 ruff 检查和格式化
basedpyright-workflow workflow --include-ruff --format-after-fix
```

## 目录结构

在项目中运行时，会在项目根目录创建以下结构：

```
your-project/
├── src/                           # 源代码
├── .bpr.json                     # 配置文件
├── .bpr/                          # 输出目录
│   ├── results/                  # 检查结果
│   │   ├── basedpyright_check_result_*.json
│   │   ├── basedpyright_check_result_*.txt
│   │   ├── basedpyright_errors_only_*.json
│   │   └── ruff_check_result_*.json
│   └── reports/                  # 报告文件
│       └── basedpyright_report_*.md
├── fix_project_errors.ps1        # PowerShell修复脚本（复制到项目）
└── ...                           # 其他项目文件
```

## 配置文件

### 创建配置文件

在项目根目录创建 `.bpr.json`：

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
    "target_version": "py311"
  },
  "checker": {
    "python_version": "3.11",
    "strict_mode": false,
    "type_check_mode": "basic"
  }
}
```

### 配置选项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `source_directory` | `src` | 源代码目录 |
| `ruff.enabled` | `true` | 是否启用 ruff |
| `ruff.line_length` | `88` | 代码行长度限制 |
| `ruff.target_version` | `py311` | Python 目标版本 |
| `checker.strict_mode` | `false` | 是否启用严格模式 |

## 完整工作流程

### 1. 仅类型检查

```bash
basedpyright-workflow workflow
```

执行步骤：
1. 运行 BasedPyright 类型检查
2. 生成 Markdown 报告
3. 提取错误用于修复

### 2. 类型检查 + Ruff 代码检查

```bash
basedpyright-workflow workflow --include-ruff
```

执行步骤：
1. 运行 BasedPyright 类型检查
2. 运行 Ruff 代码检查
3. 生成合并的报告
4. 提取错误用于修复

### 3. 完整代码质量工作流

```bash
basedpyright-workflow workflow --include-ruff --format-after-fix
```

执行步骤：
1. 运行 BasedPyright 类型检查
2. 运行 Ruff 自动修复
3. 应用代码格式化
4. 生成报告
5. 提取剩余错误

## 错误修复

### 1. 使用 PowerShell 脚本

```bash
# 基础修复
powershell .\fix_project_errors.ps1

# 包含 Ruff 错误
powershell .\fix_project_errors.ps1 -IncludeRuff

# 包含 Ruff 自动修复
powershell .\fix_project_errors.ps1 -IncludeRuff -ApplyRuffFixes
```

### 2. 指定错误文件

```bash
powershell .\fix_project_errors.ps1 -ErrorsFile ".bmad\results\basedpyright_errors_only_20241201_120000.json"
```

## 实际使用示例

### 示例 1: Web 项目

```bash
# 项目结构：
# my-web-app/
# ├── src/
# │   ├── api/
# │   └── models/
# ├── tests/
# └── .bpr.json

# 在项目根目录运行
cd my-web-app
basedpyright-workflow workflow --include-ruff
```

### 示例 2: 多模块项目

```bash
# 项目结构：
# my-service/
# ├── services/
# │   ├── auth/
# │   ├── api/
# │   └── utils/
# ├── shared/
# └── .bpr.json

# 配置文件指定多个源目录：
# {
#   "source_directory": "services"
# }

cd my-service
basedpyright-workflow workflow --include-ruff
```

### 示例 3: Python 包开发

```bash
# 项目结构：
# my-package/
# ├── my_package/
# ├── tests/
# └── .bpr.json

cd my-package
basedpyright-workflow workflow --path my_package
```

## 常见问题

### Q: 如何修改默认的输出目录？

A: 在 `.bpr.json` 中配置：
```json
{
  "output_directory": ".quality",
  "results_directory": ".quality/results",
  "reports_directory": ".quality/reports"
}
```

### Q: 如何排除某些文件或目录？

A: 在 `.bpr.json` 中配置：
```json
{
  "ruff": {
    "extend_exclude": ["tests/**", "migrations/**"]
  },
  "checker": {
    "exclude_files": ["**/__pycache__/**", "**/node_modules/**"]
  }
}
```

### Q: 如何使用不同的 Python 版本？

A: 在 `.bpr.json` 中配置：
```json
{
  "ruff": {
    "target_version": "py310"
  },
  "checker": {
    "python_version": "3.10"
  }
}
```

### Q: 如何集成到 CI/CD？

A: 在 CI/CD 脚本中：
```bash
pip install -e basedpyright-workflow ruff
basedpyright-workflow workflow --include-ruff
```

## 与现有工具的兼容性

基于pyright-workflow 与其他工具兼容，可以同时使用：

- **pre-commit hooks**: 可以在 pre-commit 配置中添加
- **IDE 集成**: 支持 VS Code、PyCharm 等
- **CI/CD 平台**: 支持 GitHub Actions、GitLab CI 等
- **其他 linter**: 可以与 flake8、pylint 等并存

## 高级配置

### 冲突解决策略

```json
{
  "unified": {
    "conflict_resolution": "basedpyright_priority"
  }
}
```

选项：
- `basedpyright_priority`: 基于 pyright 优先（推荐）
- `ruff_priority`: ruff 优先
- `smart`: 智能决策

### 环境变量配置

```bash
export BMAD_RUFF_ENABLED=true
export BMAD_RUFF_LINE_LENGTH=120
export BMAD_PYTHON_VERSION=py311
```

## 故障排除

### 1. 找不到 basedpyright 命令

**问题**: `ImportError: No module named 'basedpyright_workflow'`

**解决方案**:
```bash
# 确保在项目根目录
pwd  # 应该是项目根目录

# 检查安装
pip list | grep basedpyright-workflow

# 重新安装
pip install -e .
```

### 2. 配置文件不生效

**问题**: 配置更改没有反映在执行结果中

**解决方案**:
```bash
# 检查配置文件位置
ls -la .bpr.json

# 验证配置格式
python -c "import json; print(json.load(open('.bpr.json'))"
```

### 3. 输出目录创建失败

**问题**: 没有权限创建 `.bmad` 目录

**解决方案**:
```bash
# 检查权限
ls -la .

# 手动创建目录
mkdir .bmad
mkdir .bmad/results
mkdir .bmad/reports
```

## 更新和维护

定期更新 basedpyright-workflow：

```bash
# 更新到最新版本
pip install --upgrade -e .
```

查看更新日志和迁移指南：
- 检查项目的 CHANGELOG.md
- 查看版本兼容性说明
- 根据迁移指南更新配置
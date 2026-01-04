# 常用命令速查

**版本**: 1.0
**最后更新**: 2026-01-04

---

## 目录

1. [开发环境](#1-开发环境)
2. [测试](#2-测试)
3. [代码质量](#3-代码质量)
4. [构建和部署](#4-构建和部署)
5. [工作流工具](#5-工作流工具)

---

## 1. 开发环境

### 虚拟环境
```bash
# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 停用虚拟环境
deactivate
```

### 运行应用
```bash
# 作为模块运行
python -m my_qt_app

# 直接运行
python src/my_qt_app/__main__.py
```

---

## 2. 测试

### 基本测试命令
```bash
# 运行所有测试
pytest

# 详细输出
pytest -v --tb=short

# 显示标准输出
pytest -v --tb=short -s

# 运行特定测试
pytest -v --tb=short -k "test_name"

# 首次失败后停止
pytest -v --tb=short --maxfail=1

# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# GUI测试
pytest tests/gui/ -v
```

### Fixtest-Workflow
```bash
cd fixtest-workflow

# 扫描测试文件
python scan_test_files.py

# 运行所有测试
python run_tests.py

# 演示模式（仅3个文件）
python demo_run_tests.py

# PowerShell中自动修复
.\fix_tests.ps1

# 验证修复
python run_tests.py
```

---

## 3. 代码质量

### 类型检查
```bash
cd basedpyright-workflow

# 类型检查
basedpyright-workflow check

# 生成报告
basedpyright-workflow report

# 提取错误
basedpyright-workflow fix

# 完整工作流
basedpyright-workflow workflow
```

### 代码风格
```bash
# 检查代码风格
ruff check src/

# 自动修复
ruff check --fix src/

# 格式化代码
ruff format src/

# 检查导入排序
isort src/ tests/
```

### Black格式化
```bash
# 格式化代码
black src/ tests/

# 检查但不修改
black --check src/ tests/

# 显示差异
black --diff src/ tests/
```

### 自动化修复
```powershell
# PowerShell中运行
cd basedpyright-workflow
.\fix_unified_errors_new.ps1
```

---

## 4. 构建和部署

### Nuitka构建
```bash
# 使用构建脚本
python build/build.py

# 使用spec文件
python -m nuitka --onefile build/build.spec

# 启用控制台（调试用）
python -m nuitka --onefile --windows-enable-console src/my_qt_app/__main__.py

# 添加图标
python -m nuitka --onefile --windows-icon-from-ico=build/app.ico src/my_qt_app/__main__.py
```

### Pre-commit钩子
```bash
# 安装钩子
pre-commit install

# 运行所有钩子
pre-commit run --all-files

# 更新钩子
pre-commit autoupdate
```

---

## 5. 工作流工具

### BMAD-Workflow
```powershell
cd bmad-workflow

# 基本执行
.\BMAD-Workflow.ps1 -StoryPath "docs/stories/my-story.md"

# 系统测试
.\BMAD-Workflow.ps1 -Test

# 检查状态
.\BMAD-Workflow.ps1 -Status

# 清理临时文件
.\BMAD-Workflow.ps1 -Cleanup

# 静默模式
.\BMAD-Workflow.ps1 -StoryPath "story.md" -Silent
```

### Claude AI代理命令

#### 核心代理
```bash
# Scrum Master - 创建故事
@sm *create

# Developer - 实现故事
@dev

# QA - 审查故事
@qa *review

# Product Owner - 验证故事
@po

# Architect - 设计架构
/architect create-doc architecture

# Product Manager - 创建PRD
/pm create-doc prd
```

#### QA命令
```bash
# 风险评估
@qa *risk {story}

# 测试设计
@qa *design {story}

# 需求跟踪
@qa *trace {story}

# 非功能需求验证
@qa *nfr {story}

# 门控更新
@qa *gate {story}
```

---

## 6. 常用工具

### Git
```bash
# 初始化仓库
git init

# 添加文件
git add .

# 提交
git commit -m "Initial commit"

# 查看状态
git status

# 查看日志
git log --oneline
```

### Python包管理
```bash
# 导出依赖
pip freeze > requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装可编辑模式
pip install -e .
```

---

## 7. 故障排除

### 常见问题

#### 虚拟环境问题
```bash
# 删除虚拟环境
rm -rf .venv/  # Linux/macOS
rmdir /s .venv  # Windows

# 重新创建
python -m venv .venv
```

#### 导入错误
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 确保在项目根目录运行
pwd  # Linux/macOS
cd  # Windows
```

#### 测试超时
```bash
# 增加超时时间
pytest --timeout=300

# 跳过慢速测试
pytest -m "not slow"
```

---

## 8. 快速参考卡片

### 日常开发
```bash
# 1. 激活环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 2. 运行测试
pytest -v

# 3. 代码格式化
ruff check --fix src/
black src/

# 4. 类型检查
cd basedpyright-workflow && basedpyright-workflow check

# 5. 提交前检查
pre-commit run --all-files
```

### CI/CD流程
```bash
# 代码质量检查
ruff check src/
basedpyright-workflow check

# 运行测试
pytest --cov=src

# 构建
python build/build.py
```

---

**参考文档**:
- [核心原则](./core_principles.md)
- [BMAD开发方法论](./bmad_methodology.md)
- [质量保证流程](./quality_assurance.md)
- [技术规范](./technical_specs.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的常用命令速查

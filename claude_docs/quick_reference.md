# 常用命令速查

**版本**: 1.0
**最后更新**: 2026-01-22

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
# 运行所有测试
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_specific.py -v

# 通过autoBMAD自动执行
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md
```

---

## 3. 代码质量

### 类型检查
```bash
# BasedPyright类型检查
basedpyright src/

# 通过autoBMAD工作流自动执行
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md
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
```bash
# 通过autoBMAD工作流自动修复
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose
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

### autoBMAD Epic自动化
```bash
# 完整5阶段工作流
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

# 跳过质量门控（快速开发）
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality

# 跳过测试自动化
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-tests

# 同时跳过质量门控和测试
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality --skip-tests
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
ruff format src/

# 4. 类型检查
basedpyright src/

# 5. 提交前检查
pre-commit run --all-files
```

### autoBMAD工作流
```bash
# 完整工作流
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

# 跳过质量门控
python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality
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

# 技术规范详细说明

**版本**: 1.1
**最后更新**: 2026-01-14

---

## 目录

1. [核心依赖](#1-核心依赖)
2. [配置文件](#2-配置文件)
3. [代码质量检查](#3-代码质量检查)
4. [打包和部署](#4-打包和部署)
5. [开发工具](#5-开发工具)
6. [类型检查配置](#6-类型检查配置)
7. [代码风格检查](#7-代码风格检查)
8. [虚拟环境管理](#8-虚拟环境管理)

---

## 1. 核心依赖

### 1.1 项目依赖框架

本项目依赖以下核心技术：

#### Claude Agent SDK
- **版本**: >=0.1.0
- **用途**: AI代理编排和执行
- **链接**: [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- **特性**:
  - AI驱动的代理系统
  - 异步任务执行
  - 权限管理和安全控制

#### BMAD Method
- **用途**: AI驱动的敏捷开发方法论
- **链接**: [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
- **特性**:
  - 结构化的开发流程
  - SM-Dev-QA循环
  - 质量门控集成

### 1.2 生产依赖

#### PySide6
- **版本**: 最新稳定版
- **用途**: Qt for Python，现代Qt框架
- **特性**:
  - 跨平台GUI开发
  - 完整的Qt 6 API
  - 高性能渲染
  - 丰富的UI组件

#### loguru
- **版本**: 最新稳定版
- **用途**: 日志处理
- **特性**:
  - 零配置日志记录
  - 彩色输出
  - 自动日志轮转
  - 异常捕获

### 1.3 开发依赖

#### pytest
- **版本**: 最新稳定版
- **用途**: 测试框架
- **常用插件**:
  - pytest-cov: 代码覆盖率
  - pytest-qt: Qt应用测试
  - pytest-timeout: 超时控制
  - pytest-mock: 模拟对象

#### pytest-qt
- **用途**: Qt应用测试插件
- **特性**:
  - Qt事件循环集成
  - 信号和槽测试
  - GUI测试支持

#### nuitka
- **版本**: 最新稳定版
- **用途**: Python打包工具
- **优势**:
  - 高性能编译
  - 小体积分发
  - 跨平台支持

#### black
- **版本**: 最新稳定版
- **用途**: 代码格式化
- **特性**:
  - 一致的代码风格
  - 最小的配置
  - 自动格式化

### 1.4 依赖管理

#### requirements.txt (生产依赖)
```
PySide6>=6.5.0
loguru>=0.7.0
claude-agent-sdk>=0.1.0
```

#### requirements-dev.txt (开发依赖)
```
# 测试
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-qt>=4.0.0
pytest-timeout>=2.1.0
pytest-mock>=3.10.0

# 构建
nuitka>=1.8.0

# 代码质量
black>=23.0.0
ruff>=0.1.0
basedpyright>=1.0.0

# 开发工具
pre-commit>=3.0.0
```

---

## 2. 配置文件

### 2.1 pyproject.toml

现代Python项目的核心配置文件：

```toml
[project]
name = "my-qt-app"
version = "1.0.0"
description = "PyQt Windows应用程序"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.12"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "PySide6>=6.5.0",
    "loguru>=0.7.0",
    "claude-agent-sdk>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-qt>=4.0.0",
    "pytest-timeout>=2.1.0",
    "pytest-mock>=3.10.0",
    "nuitka>=1.8.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "basedpyright>=1.0.0",
    "pre-commit>=3.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
timeout = 120
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]

[tool.black]
line-length = 88
target-version = ["py312"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 88
target-version = "py312"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["B011"]

[tool.basedpyright]
include = ["src/**/*"]
exclude = ["tests/**/*", "build/**/*", "dist/**/*"]
report = {
    enable = true,
    format = "json"
}
```

### 2.2 pytest.ini

pytest测试框架配置：

```ini
[pytest]
minversion = 7.0
addopts = -ra -q --strict-markers --strict-config
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
timeout = 120
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning:pytest_qt.qtbot
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    gui: marks tests as GUI tests
    unit: marks tests as unit tests
    integration: marks tests as integration tests
```

### 2.3 .gitignore

Git版本控制忽略规则：

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# PySide6
resource_rc.py
```

### 2.4 .pre-commit-config.yaml

代码质量预检查钩子：

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 3. 代码质量检查

### 3.1 基于pyright的类型检查

#### 类型检查要求

1. **类型注解**:
   - 所有公共函数和方法必须有返回类型注解
   - 函数参数建议添加类型注解
   - 类属性建议添加类型注解

```python
# ✅ 正确示例
def calculate_area(radius: float) -> float:
    """计算圆的面积"""
    return 3.14 * radius * radius

class UserService:
    def __init__(self, config: ConfigService) -> None:
        self.config = config

    def get_user(self, user_id: int) -> User:
        """获取用户信息"""
        return self._repository.get_by_id(user_id)
```

2. **配置文件**:
   - 项目根目录创建 `.bpr.json` 配置文件
   - 定义检查范围和规则

```json
{
    "include": ["src/**/*"],
    "exclude": ["tests/**/*", "build/**/*"],
    "report": {
        "enable": true,
        "format": "json"
    }
}
```

3. **检查执行**:
```bash
# 运行类型检查
cd basedpyright-workflow
basedpyright-workflow check

# 生成详细报告
basedpyright-workflow report

# 完整工作流
basedpyright-workflow workflow
```

### 3.2 Ruff代码风格检查

#### Ruff配置 (pyproject.toml)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

#### 执行命令
```bash
# 检查代码风格
ruff check src/

# 自动修复可修复的问题
ruff check --fix src/

# 格式化代码
ruff format src/
```

### 3.3 智能冲突解决

BasedPyright-Workflow 提供智能冲突解决机制：

1. **优先级策略**:
   - 类型错误 (Type Error) > 代码风格 (Style)
   - 逻辑错误 (Logic Error) > 格式错误 (Format)
   - 安全问题 (Security) > 性能问题 (Performance)

2. **自动化决策**:
   - 优先修复类型错误
   - 然后处理代码风格问题
   - 避免重复修复

3. **手动干预**:
```powershell
# 使用PowerShell脚本进行自动修复
cd basedpyright-workflow
.\fix_unified_errors_new.ps1
```

### 3.4 集成到开发流程

#### 预提交检查
```bash
#!/bin/bash
# pre-commit.sh
echo "运行类型检查..."
basedpyright-workflow check

echo "检查代码风格..."
ruff check --fix src/

echo "运行测试..."
pytest tests/
```

#### CI/CD集成
```yaml
# .github/workflows/quality-check.yml
- name: Run BasedPyright
  run: |
    cd basedpyright-workflow
    basedpyright-workflow check

- name: Run Ruff
  run: |
    ruff check src/
    ruff format --check src/
```

---

## 4. 打包和部署

### 4.1 使用Nuitka构建

#### 构建目录结构
```
build/
├── build.py               # 一键构建脚本
├── build.spec             # Nuitka参数配置
├── app.ico                # Windows程序图标
└── version_info.py        # Windows版本信息（FILEVERSION等）
```

#### build.py
```python
#!/usr/bin/env python3
"""一键构建脚本"""

import subprocess
import sys
from pathlib import Path

def build():
    """执行Nuitka构建"""
    print("开始构建...")

    # 执行Nuitka构建
    result = subprocess.run([
        sys.executable, "-m", "nuitka",
        "--onefile",
        "--windows-disable-console",
        "--windows-icon-from-ico=build/app.ico",
        "--company-name=Your Company",
        "--file-description=My Qt Application",
        "--product-name=My Qt App",
        "--product-version=1.0.0",
        "src/my_qt_app/__main__.py"
    ], check=True)

    print("构建完成！")

if __name__ == "__main__":
    build()
```

#### build.spec
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/my_qt_app/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyQtApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='build/app.ico',
)
```

#### version_info.py
```python
# Windows版本信息
# FILEVERSION & PRODUCTVERSION format: major,minor,patch,build

VERSION_INFO = {
    "version": "1.0.0.0",
    "company_name": "Your Company",
    "file_description": "My Qt Application",
    "internal_name": "MyQtApp",
    "legal_copyright": "Copyright © 2024 Your Company",
    "original_filename": "MyQtApp.exe",
    "product_name": "My Qt App",
    "product_version": "1.0.0.0",
}
```

#### 构建命令
```bash
# 安装Nuitka
pip install nuitka

# 执行构建
python build/build.py

# 或使用spec文件
python -m nuitka --onefile build/build.spec
```

### 4.2 输出结构

#### dist/ 目录
```
dist/
├── MyQtApp.exe          # 可执行文件
└── build.log            # 构建日志
```

---

## 5. 开发工具

### 5.1 Pre-commit hooks

`.pre-commit-config.yaml` - 代码质量预检查钩子

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix]
```

#### 安装和使用
```bash
# 安装pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

### 5.2 IDE配置

#### VS Code推荐插件
- Python
- Pylance
- Qt for Python
- GitLens
- Error Lens

#### VS Code设置 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.pyrightEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

---

## 6. 类型检查配置

### 6.1 .bpr.json

基于pyright的配置文件：

```json
{
    "include": ["src/**/*"],
    "exclude": ["tests/**/*", "build/**/*", "dist/**/*", ".venv/**/*"],
    "report": {
        "enable": true,
        "format": "json",
        "file": "results/basedpyright_results.json"
    },
    "typeCheckingMode": "basic",
    "useLibraryCodeForTypes": true,
    "verboseOutput": true
}
```

### 6.2 类型检查最佳实践

#### 1. 逐步添加类型注解
```python
# 从简单类型开始
def process_data(data: list) -> list:
    return [item for item in data if item]

# 然后添加泛型
from typing import List, Dict, Optional

def get_user(user_id: int) -> Optional[Dict]:
    """获取用户信息，可能返回None"""
    pass
```

#### 2. 使用Protocol定义接口
```python
from typing import Protocol

class Serializable(Protocol):
    def serialize(self) -> str:
        ...

def save_data(data: Serializable) -> None:
    """可以接受任何实现serialize方法的对象"""
    data.serialize()
```

#### 3. 类型别名提高可读性
```python
from typing import NewType

UserId = NewType('UserId', int)
UserName = NewType('UserName', str)

def get_user(user_id: UserId) -> UserName:
    ...
```

---

## 7. 代码风格检查

### 7.1 Black配置

#### pyproject.toml中的配置
```toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### 使用示例
```bash
# 格式化所有文件
black src/ tests/

# 检查但不修改
black --check src/ tests/

# 显示差异
black --diff src/ tests/
```

### 7.2 isort配置

#### pyproject.toml中的配置
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

#### 使用示例
```bash
# 排序导入
isort src/ tests/

# 检查但不修改
isort --check-only src/ tests/

# 显示差异
isort --diff src/ tests/
```

---

## 8. 虚拟环境管理

### 8.1 虚拟环境信息

- **Python版本**: 3.12.10
- **环境路径**: `./.venv/`
- **创建日期**: 2026-01-04

### 8.2 使用方法

#### 激活虚拟环境
```cmd
# Windows
.venv\Scripts\activate
```

#### 安装依赖包
```bash
pip install package_name
```

#### 导出依赖列表
```bash
pip freeze > requirements.txt
```

#### 从依赖列表安装
```bash
pip install -r requirements.txt
```

#### 停用虚拟环境
```bash
deactivate
```

### 8.3 最佳实践

1. 每次工作前记得激活虚拟环境
2. 提交代码时，不要包含`.venv/`目录
3. 使用`requirements.txt`管理项目依赖
4. 在IDE中将Python解释器路径指向虚拟环境

---

## 9. 项目特定规则

### 9.1 Python模块导入规范

#### 核心要求

1. **使用绝对导入**: 禁止使用相对导入
2. **导入路径不包含源代码目录名**: 从源代码目录的内容开始

```python
# ❌ 错误示例
from Project_recorder.services.config_service import ConfigService
from ..services.config_service import ConfigService

# ✅ 正确示例
from services.config_service import ConfigService
from ui.widgets.button import CustomButton
```

#### 导入顺序规范
```python
# 1. 标准库导入
import os
import sys
from pathlib import Path

# 2. 第三方库导入
from PySide6.QtWidgets import QWidget
import pytest

# 3. 本地应用/库导入（使用绝对导入）
from services.config_service import ConfigService
from ui.widgets.button import CustomButton
from core.recorder import Recorder
```

### 9.2 字符编码要求

1. **禁止使用Unicode编码**: 代码中不要创建或使用Unicode转义序列
2. **字符编码统一**: 所有Python源文件使用UTF-8编码
3. **可读性优先**: 字符串常量、注释、文档字符串使用人类可读的文本

```python
# ❌ 反面例子
message = "\u6b22\u8fce"  # Unicode编码的"欢迎"

# ✅ 正面例子
message = "欢迎"  # 直接使用中文字符
```

---

**参考文档**:
- [开发规则与实践](./development_rules.md)
- [工作流工具集](./workflow_tools.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的技术规范说明

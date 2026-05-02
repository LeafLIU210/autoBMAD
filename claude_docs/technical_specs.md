# 技术规范详细说明 - DocuSwarm

**版本**: 3.2
**最后更新**: 2026-05-02
**项目**: DocuSwarm Multi-Agent Orchestration System (claude-agent-sdk architecture)

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

#### LangGraph (多代理工作流)
- **版本**: >=0.2.0
- **用途**: 状态机和多代理工作流编排
- **链接**: [LangGraph](https://langchain-ai.github.io/langgraph/)
- **特性**:
  - 原生状态图(StateGraph)支持
  - SQLite检查点持久化
  - 消息传递和代理通信
  - 条件边和工作流路由

#### LangChain (LLM集成框架)
- **版本**: >=0.3.0
- **用途**: LLM抽象和集成
- **链接**: [LangChain](https://python.langchain.com/)
- **特性**:
  - 统一LLM接口
  - 提示模板管理
  - 输出解析器
  - 异步支持

#### Anthropic Claude (主要LLM提供商)
- **提供商**: Anthropic
- **集成方式**: claude-agent-sdk (Anthropic 官方 SDK)
- **上下文窗口**: 200K tokens
- **链接**: [Anthropic API](https://docs.anthropic.com/)

#### claude-agent-sdk (LLM集成SDK)
- **版本**: >=0.1.0,<0.2.0
- **用途**: Anthropic Claude Agent SDK
- **核心能力**:
  - `query()` — 无状态查询 API
  - `ClaudeAgentOptions` — 配置选项
  - 标准工具调用支持
  - 异步生成器支持

#### BMAD Method (方法论来源)
- **用途**: Agent persona提取和工作流模式
- **链接**: [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
- **特性**:
  - 5阶段开发流程(Analyst → PM → UX → Architect → PO)
  - Agent persona定义
  - 质量门控模式

### 1.2 生产依赖

#### langgraph
- **版本**: >=0.2.0
- **用途**: 多代理工作流状态机
- **特性**:
  - StateGraph工作流定义
  - 原生检查点支持
  - 条件边和路由
  - 异步执行

#### langchain
- **版本**: >=0.3.0
- **用途**: LLM集成和提示管理
- **特性**:
  - 统一LLM接口
  - 提示模板
  - 输出解析
  - 链式调用

#### kimi-agent-sdk (已移除)
- **状态**: 已由 claude-agent-sdk 完全替代
- **迁移完成**: 2026-04-05
- ****替代方案**: claude-agent-sdk (Anthropic 官方 SDK)

#### pyyaml
- **版本**: >=6.0.0
- **用途**: 配置文件管理
- **特性**:
  - YAML解析
  - 配置加载
  - 结构化数据

#### pydantic
- **版本**: >=2.0.0
- **用途**: 数据验证和模式定义
- **特性**:
  - 类型验证
  - 自动文档
  - JSON Schema生成
  - 性能优化

#### python-dotenv
- **版本**: >=1.0.0
- **用途**: 环境变量管理
- **特性**:
  - .env文件加载
  - 配置隔离
  - 安全凭据管理

#### structlog
- **版本**: >=24.0.0
- **用途**: 结构化日志处理
- **特性**:
  - 结构化日志输出
  - JSON格式日志
  - 处理器链式配置
  - 上下文绑定
  - 线程安全

### 1.3 开发依赖

#### pytest
- **版本**: >=8.0.0
- **用途**: 测试框架
- **常用插件**:
  - pytest-cov: 代码覆盖率
  - pytest-asyncio: 异步测试支持
  - pytest-timeout: 超时控制
  - pytest-mock: 模拟对象
  - pytest-json-report: JSON报告

#### pytest-asyncio
- **版本**: >=0.23.0
- **用途**: 异步测试支持
- **特性**:
  - async/await测试
  - 事件循环管理
  - LangGraph异步节点测试

#### ruff
- **版本**: >=0.5.0
- **用途**: Python代码检查和格式化
- **特性**:
  - 极速代码检查(比Flake8快10-100倍)
  - 自动修复
  - PEP 8合规
  - Import排序
  - 代码复杂度检查

#### basedpyright
- **版本**: >=1.1.0
- **用途**: 静态类型检查
- **特性**:
  - Pyright的增强版本
  - 类型推导
  - 配置灵活
  - VS Code集成

### 1.4 依赖管理

#### requirements.txt (生产依赖)
```txt
# DocuSwarm Multi-Agent Orchestration System
# Production Dependencies
# Updated: 2026-04-28 (claude-agent-sdk architecture)
# Python: >=3.12

# === Core Framework ===
langgraph>=0.2.50,<0.3.0
langgraph-checkpoint-sqlite>=2.0.4,<3.0.0
langchain>=0.3.0,<0.4.0
langchain-core>=0.3.0,<0.4.0

# === LLM Integration ===
claude-agent-sdk>=0.1.0,<0.2.0

# === Configuration & Data ===
PyYAML==6.0.3
pydantic>=2.0.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0

# === Database ===
aiosqlite>=0.19.0,<1.0.0

# === Logging ===
structlog>=24.0.0,<25.0.0

# === CLI & UI ===
click>=8.1.0,<9.0.0
rich==14.2.0

# === Async IO ===
aiofiles>=24.0.0,<26.0.0
```

#### requirements-dev.txt (开发依赖)
```txt
# DocuSwarm Development Dependencies
# Updated: 2026-04-28

# ========== Production Dependencies ==========
-r requirements.txt

# ========== Testing Framework ==========
pytest>=8.0.0,<9.0.0
pytest-asyncio>=0.23.0,<0.24.0
pytest-cov>=4.0.0,<5.0.0
pytest-timeout>=2.1.0,<3.0.0
pytest-mock>=3.12.0,<4.0.0
typeguard>=4.0.0,<5.0.0

# ========== Code Quality ==========
ruff>=0.5.0,<0.6.0
basedpyright>=1.1.0,<2.0.0
black>=24.0.0,<25.0.0
pre-commit>=3.6.0,<4.0.0
```

---

## 2. 配置文件

### 2.1 pyproject.toml

DocuSwarm项目的核心配置文件：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "docuswarm"
version = "1.0.0"
description = "Multi-agent document orchestration system with BMAD methodology"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "DocuSwarm Team"},
]
keywords = ["multi-agent", "LangGraph", "BMAD", "document-automation", "AI", "claude-agent-sdk"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dependencies = [
    "langgraph>=0.2.50,<0.3.0",
    "langgraph-checkpoint-sqlite>=2.0.4,<3.0.0",
    "langchain>=0.3.0,<0.4.0",
    "langchain-core>=0.3.0,<0.4.0",
    "claude-agent-sdk>=0.1.0,<0.2.0",
    "pyyaml==6.0.3",
    "pydantic>=2.0.0,<3.0.0",
    "python-dotenv>=1.0.0,<2.0.0",
    "rich==14.2.0",
    "click>=8.1.0,<9.0.0",
    "structlog>=24.0.0,<25.0.0",
    "aiofiles>=24.0.0,<26.0.0",
    "aiosqlite>=0.19.0,<1.0.0",
]

[project.scripts]
docuswarm = "autoBMAD.docuswarm.cli.main:cli"

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0,<9.0.0",
    "pytest-cov>=4.0.0,<5.0.0",
    "pytest-asyncio>=0.23.0,<0.24.0",
    "pytest-timeout>=2.1.0,<3.0.0",
    "pytest-mock>=3.12.0,<4.0.0",
    "typeguard>=4.0.0,<5.0.0",
    "ruff>=0.5.0,<0.6.0",
    "basedpyright>=1.1.0,<2.0.0",
    "black>=24.0.0,<25.0.0",
    "pre-commit>=3.6.0,<4.0.0",
]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers --cov=autoBMAD.docuswarm --cov-report=term-missing --cov-report=html --tb=short --basetemp=.pytest-temp"
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = [".", "autoBMAD"]
timeout = 300
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end tests",
    "agent: marks tests as agent-related tests",
    "pipeline: marks tests as pipeline tests",
    "smoke: marks tests as SDK smoke tests",
    "llm: marks tests that require real LLM API calls",
]

[tool.coverage.run]
source = ["autoBMAD.docuswarm"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
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
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["B018", "B017"]

[tool.basedpyright]
pythonVersion = "3.12.10"
reportMissingImports = false
reportMissingModuleSource = false
reportImplicitRelativeImport = false
reportArgumentType = false
reportAttributeAccessIssue = false
reportExplicitAny = false
reportUnannotatedClassAttribute = false
reportAssignmentType = false
reportAny = false
reportMissingTypeStubs = false
reportUnknownVariableType = false
reportUnknownMemberType = false
reportUnusedCallResult = false
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
    ignore::DeprecationWarning
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
venv/
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

# Generated files
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

2. **检查执行**:
```bash
# 运行类型检查
basedpyright autoBMAD/

# 生成详细报告（JSON 格式）
basedpyright autoBMAD/ --outputjson
```

### 3.2 Ruff代码风格检查

#### Ruff配置 (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
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
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

#### 执行命令
```bash
# 检查代码风格
ruff check docuswarm/

# 自动修复可修复的问题
ruff check --fix docuswarm/

# 格式化代码
ruff format docuswarm/
```

### 3.3 冲突解决策略

1. **优先级策略**:
   - 类型错误 (Type Error) > 代码风格 (Style)
   - 逻辑错误 (Logic Error) > 格式错误 (Format)
   - 安全问题 (Security) > 性能问题 (Performance)

2. **自动化决策**:
   - 优先修复类型错误
   - 然后处理代码风格问题
   - 避免重复修复

### 3.4 集成到开发流程

#### 预提交检查
```bash
#!/bin/bash
# pre-commit.sh
echo "运行类型检查..."
basedpyright autoBMAD/

echo "检查代码风格..."
ruff check --fix autoBMAD/

echo "运行测试..."
pytest tests/
```

#### CI/CD集成
```yaml
# .github/workflows/quality-check.yml
- name: Run BasedPyright
  run: basedpyright autoBMAD/

- name: Run Ruff
  run: |
    ruff check autoBMAD/
    ruff format --check autoBMAD/
```

---

## 4. 打包和部署

### 4.1 运行方式

DocuSwarm 作为 CLI 工具运行，无需打包构建：

```bash
# 直接运行
python -m autoBMAD.docuswarm --help

# 启动流水线
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
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

### 6.1 basedpyright 配置

基于pyright的配置通过 `pyproject.toml` 管理：

```toml
[tool.basedpyright]
pythonVersion = "3.12.10"
reportMissingImports = false
reportMissingModuleSource = false
reportImplicitRelativeImport = false
reportArgumentType = false
reportAttributeAccessIssue = false
reportExplicitAny = false
reportUnannotatedClassAttribute = false
reportAssignmentType = false
reportAny = false
reportMissingTypeStubs = false
reportUnknownVariableType = false
reportUnknownMemberType = false
reportUnusedCallResult = false
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

### 7.1 Ruff 格式化

#### 使用示例
```bash
# 格式化所有文件
ruff format autoBMAD/ tests/

# 检查但不修改
ruff format --check autoBMAD/ tests/

# 显示差异
ruff format --diff autoBMAD/ tests/
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
ruff check --select I --fix autoBMAD/ tests/

# 检查但不修改
ruff check --select I autoBMAD/ tests/

# 显示差异
ruff check --select I --diff autoBMAD/ tests/
```

---

## 8. 虚拟环境管理

### 8.1 虚拟环境信息

- **Python版本**: 3.12.10+
- **环境路径**: `./.venv/`

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
2. 提交代码时，不要包含`venv/`目录
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
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
```

#### 导入顺序规范
```python
# 1. 标准库导入
import os
import sys
from pathlib import Path

# 2. 第三方库导入
from autoBMAD.docuswarm.config import DocuSwarmConfig
import pytest

# 3. 本地应用/库导入（使用绝对导入）
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
from autoBMAD.docuswarm.storage.state_manager import StateManager
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
- v3.2 (2026-05-02): 根据实际代码对齐更新依赖版本、配置示例，移除过时工具引用
- v3.0 (2026-02-20): claude-agent-sdk 架构升级，替换 kimi-agent-sdk，更新依赖和配置
- v2.0 (2026-02-19): DocuSwarm 项目适配
- v1.0 (2026-01-04): 初始版本，完整的技术规范说明

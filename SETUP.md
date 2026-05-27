# 安装与配置指南

DocuSwarm Multi-Agent Document Orchestration System 的安装与配置指南。

本项目包含两个子系统：
- **DocuSwarm** - 多 Agent 文档编排流水线（5 阶段 BMAD 工作流）
- **Epic Automation** - Epic 级别 BMAD 自动化（SM-Dev-QA 循环）

---

## 前提条件

### 系统要求

- **操作系统**: Linux (Ubuntu 22.04+)、WSL2 (Ubuntu 24.04+)、macOS
- **Python**: >= 3.12（项目要求 `requires-python = ">=3.12"`）
- **Git**: 2.20+
- **内存**: 4GB RAM（推荐 8GB）
- **磁盘空间**: 2GB 可用

### 版本检查

```bash
python3 --version   # 要求 3.12+
git --version       # 要求 2.20+
pip --version       # 确认 pip 可用
```

预期输出示例：
```
Python 3.12.10
git version 2.43.0
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/LeafLIU210/autoBMAD.git
cd autoBMAD
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

验证激活状态：
```bash
which python
# 预期输出: /path/to/autoBMAD/.venv/bin/python
```

终端提示符应显示 `(.venv)` 前缀。

### 3. 安装依赖

**生产环境（仅运行）：**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**开发环境（运行 + 开发工具）：**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt
```

**开发模式安装（可选，推荐开发者使用）：**
```bash
pip install -e .
```

开发模式安装会将项目以可编辑方式安装到虚拟环境中，代码修改后无需重新安装即可生效。安装后可直接使用 `docuswarm` 命令（等同于 `python -m autoBMAD.docuswarm`）。

### 4. 配置环境变量

复制示例配置文件并填写 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必需的 API 密钥：

```bash
# 必需 - Anthropic API 密钥
ANTHROPIC_API_KEY=your_actual_api_key_here
```

也可以直接创建：
```bash
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env
```

### 5. 验证安装

#### 验证 DocuSwarm CLI

```bash
python -m autoBMAD.docuswarm --help
```

预期输出：
```
Usage: python -m autoBMAD.docuswarm [OPTIONS] COMMAND [ARGS]...

  DocuSwarm - Multi-Agent Document Orchestration System

Options:
  -v, --verbose        Enable verbose debug output
  --log-level TEXT     Set logging level
  --log-file TEXT      Directory for log files
  --json-log           Use JSON format for log file output
  --version            Show version and exit
  --help               Show this message and exit.

Commands:
  cancel          Cancel a running pipeline
  cancel-all      Cancel all pipelines
  clean           Delete pipelines from database
  diagnostics     Run pipeline diagnostics
  export          Export deliverables
  list-pipelines  List all pipelines
  resume          Resume an interrupted pipeline
  start           Start a new pipeline
  status          Show pipeline status
```

#### 验证 Epic Automation

```bash
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver --help
```

预期输出（部分）：
```
usage: epic_driver.py [-h] [--verbose] [--skip-quality] ...
```

#### 验证核心依赖

```bash
python -c "
import sys
print('Python version:', sys.version)
print()

modules = [
    'langgraph', 'langchain', 'pydantic',
    'click', 'rich', 'structlog', 'aiofiles', 'aiosqlite',
    'yaml', 'dotenv', 'claude_agent_sdk'
]
all_ok = True
for mod in modules:
    try:
        __import__(mod)
        print(f'  {mod}: OK')
    except ImportError:
        print(f'  {mod}: MISSING')
        all_ok = False

print()
print('Result:', 'ALL PASS' if all_ok else 'SOME MISSING - run pip install -r requirements.txt')
"
```

预期输出（所有模块显示 OK）：
```
Python version: 3.12.10 (...)

  langgraph: OK
  langchain: OK
  pydantic: OK
  click: OK
  rich: OK
  structlog: OK
  aiofiles: OK
  aiosqlite: OK
  yaml: OK
  dotenv: OK
  claude_agent_sdk: OK

Result: ALL PASS
```

---

## Epic Automation 额外配置

Epic Automation 子系统需要额外的环境变量来指定源码和测试目录。在 `.env` 文件中追加：

```bash
# Epic Automation 配置
# 源代码目录（用于质量检查），默认值: "src"
EPIC_SOURCE_DIR=docuswarm

# 测试目录（用于 pytest 执行），默认值: "tests"
EPIC_TEST_DIR=tests
```

### Epic Automation 运行方式

```bash
# 运行完整 5 阶段 BMAD 工作流（带质量门禁）
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --verbose

# 跳过质量门禁（快速迭代）
PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver docs/epics/my-epic.md --skip-quality
```

---

## 环境变量完整参考

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```bash
# =============================================================================
# 必需配置
# =============================================================================
# Anthropic API 密钥（必须设置，否则无法启动）
ANTHROPIC_API_KEY=your_api_key_here

# =============================================================================
# 可选 - API 配置
# =============================================================================
# 自定义 API 端点（使用代理或第三方兼容服务时设置）
# ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/

# 模型名称（使用非默认模型时设置）
# ANTHROPIC_MODEL_NAME=deepseek-v4-pro

# =============================================================================
# 可选 - DocuSwarm 运行时配置
# =============================================================================
# SQLite 数据库路径（默认: docuswarm.db）
# DOCUSWARM_DB_PATH=docuswarm.db

# 输出目录（默认: output）
# DOCUSWARM_OUTPUT_DIR=output

# 日志级别（DEBUG, INFO, WARNING, ERROR，默认: INFO）
# DOCUSWARM_LOG_LEVEL=INFO

# 每个节点最大迭代次数（默认: 10）
# DOCUSWARM_MAX_ITERATIONS=10

# Agent 执行超时秒数（默认: 7200，即 2 小时）
# DOCUSWARM_AGENT_TIMEOUT=7200

# =============================================================================
# 可选 - Epic Automation 配置
# =============================================================================
# 源码目录（质量检查使用，默认: "src"）
# EPIC_SOURCE_DIR=docuswarm

# 测试目录（pytest 执行使用，默认: "tests"）
# EPIC_TEST_DIR=tests
```

配置优先级: **环境变量 > .env 文件 > 默认值**

---

## 开发工具配置

以下工具需要安装开发依赖（`pip install -r requirements-dev.txt`）。

### BasedPyRight（类型检查）

已在 `pyproject.toml` 中配置（pythonVersion = "3.12.10"）：

```bash
# 检查整个项目
basedpyright autoBMAD/

# 检查单个文件
basedpyright autoBMAD/docuswarm/config.py
```

### Ruff（代码检查与格式化）

已在 `pyproject.toml` 中配置（line-length=100, target-version="py312"）：

```bash
# 检查代码问题
ruff check autoBMAD/

# 自动修复问题
ruff check --fix autoBMAD/

# 格式化代码
ruff format autoBMAD/
```

### Pytest（测试）

```bash
# 运行所有测试
pytest -v --tb=short

# 运行并生成覆盖率报告
pytest --cov=autoBMAD.docuswarm --cov-report=html --cov-report=term-missing

# 按标记筛选
pytest -m "not slow"      # 排除慢速测试
pytest -k "p0"            # 仅运行 P0 级别测试

# 调试特定测试
pytest tests/test_specific.py -s --pdb
```

---

## 故障排除

### 常见问题

**问题: pip install 权限错误**

```bash
# 确认虚拟环境已激活
source .venv/bin/activate
pip install -r requirements.txt
```

**问题: basedpyright / ruff 命令未找到**

```bash
# 确认已安装开发依赖
source .venv/bin/activate
pip install -r requirements-dev.txt
which basedpyright
which ruff
```

**问题: 数据库锁定**

```bash
sqlite3 docuswarm.db "PRAGMA journal_mode=WAL;"
```

**问题: ModuleNotFoundError: No module named 'autoBMAD'**

```bash
# 方法 1: 设置 PYTHONPATH
PYTHONPATH=. python -m autoBMAD.docuswarm --help

# 方法 2: 使用开发模式安装（推荐）
pip install -e .
python -m autoBMAD.docuswarm --help
```

---

## 安装验证清单

- [ ] Python 3.12+ 已安装
- [ ] 虚拟环境 `.venv` 已创建并激活
- [ ] 生产依赖已安装（`pip install -r requirements.txt`）
- [ ] `.env` 文件已配置 `ANTHROPIC_API_KEY`
- [ ] DocuSwarm CLI 可用: `python -m autoBMAD.docuswarm --help`
- [ ] Epic Automation 可用: `PYTHONPATH=. python -m autoBMAD.epic_automation.epic_driver --help`

开发者额外检查：
- [ ] 开发依赖已安装（`pip install -r requirements-dev.txt`）
- [ ] BasedPyRight 可用: `basedpyright --version`
- [ ] Ruff 可用: `ruff --version`
- [ ] Pytest 可用: `pytest --version`
- [ ] 开发模式安装: `pip install -e .`

---

## 后续步骤

1. 阅读 [README.md](README.md) 了解项目概览与 CLI 参考
2. 阅读 [DocuSwarm 详细指南](autoBMAD/docuswarm/README.md) 了解完整用法
3. 阅读 [CLAUDE.md](CLAUDE.md) 了解开发规范
4. 试运行流水线: `python -m autoBMAD.docuswarm start --context docs-test/calc-one-plus-one/calc-context.md`

---

## 卸载

```bash
deactivate
rm -rf .venv
cd ..
rm -rf autoBMAD
```

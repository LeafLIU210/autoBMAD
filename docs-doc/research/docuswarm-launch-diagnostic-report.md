# DocuSwarm 启动失败深度诊断报告

**诊断日期**: 2026-04-28
**诊断工具**: `tools/debug/docuswarm_launch_diagnostic.py`
**项目根目录**: `/home/leafliu/autoBMAD`
**Python 解释器**: `/home/leafliu/autoBMAD/.venv/bin/python`
**Python 版本**: `3.12.10`

---

## 执行摘要

本次诊断共发现 **17** 个问题:
- **CRITICAL**: 12
- **HIGH**: 4
- **MEDIUM**: 1
- **LOW**: 0

> **结论**: 存在阻断性错误，`python -m autoBMAD.docuswarm start` 目前无法成功启动。

## 导入链追踪

| 模块 | 状态 | 路径 | 错误 |
|------|------|------|------|
| `autoBMAD.docuswarm.__main__` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |
| `autoBMAD.docuswarm.cli.main` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |
| `autoBMAD.docuswarm.cli.commands` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |
| `autoBMAD.docuswarm.cli.commands.start` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |
| `autoBMAD.docuswarm.cli.services.pipeline_service` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |
| `autoBMAD.docuswarm.pipeline.orchestrator` | FAIL | `N/A` | ModuleNotFoundError: No module named 'kaos' |

## 依赖状态

| 模块 | 状态 |
|------|------|
| `aiofiles` | OK |
| `aiosqlite` | OK |
| `claude_agent_sdk` | OK |
| `click` | OK |
| `dotenv` | OK |
| `jsonschema` | OK |
| `kaos` | FAIL |
| `kimi_agent_sdk` | FAIL |
| `langchain_core` | OK |
| `langgraph` | OK |
| `mcp` | OK |
| `pydantic` | OK |
| `rich` | OK |
| `structlog` | OK |
| `yaml` | OK |

## 导入失败

### [CRITICAL] Import failed: autoBMAD.docuswarm.__main__

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

### [CRITICAL] Import failed: autoBMAD.docuswarm.cli.main

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

### [CRITICAL] Import failed: autoBMAD.docuswarm.cli.commands

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

### [CRITICAL] Import failed: autoBMAD.docuswarm.cli.commands.start

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

### [CRITICAL] Import failed: autoBMAD.docuswarm.cli.services.pipeline_service

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

### [CRITICAL] Import failed: autoBMAD.docuswarm.pipeline.orchestrator

**详情**: ModuleNotFoundError: No module named 'kaos'

**修复建议**: Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency.

---

## 依赖问题

### [CRITICAL] Missing dependency: kaos

**详情**: No module named 'kaos'

**修复建议**: Install `kaos` or remove the import if deprecated.

---

### [CRITICAL] Missing dependency: kimi_agent_sdk

**详情**: No module named 'kimi_agent_sdk'

**修复建议**: Install `kimi_agent_sdk` or remove the import if deprecated.

---

### [HIGH] 'kaos' imported but not declared in pyproject.toml

**详情**: Module kaos is imported in source code but missing from dependencies.

**修复建议**: Either add kaos to dependencies or remove the import.

---

### [HIGH] 'kimi_agent_sdk' imported but not declared in pyproject.toml

**详情**: Module kimi_agent_sdk is imported in source code but missing from dependencies.

**修复建议**: Either add kimi_agent_sdk to dependencies or remove the import.

---

## 配置问题

### [CRITICAL] Missing .env file

**详情**: Expected .env at /home/leafliu/autoBMAD/.env

**修复建议**: Create .env with ANTHROPIC_API_KEY=your_api_key

---

### [CRITICAL] ANTHROPIC_API_KEY not in environment

**详情**: Environment variable ANTHROPIC_API_KEY is empty or not set.

**修复建议**: Export ANTHROPIC_API_KEY or create .env file.

---

## 代码质量问题

### [CRITICAL] Undeclared dependency 'kaos' in orchestrator.py (`orchestrator.py:L16`)

**详情**: Line 16: from kaos.path import KaosPath

**修复建议**: Replace `KaosPath` with `pathlib.Path`. Remove all kaos imports.

---

### [HIGH] Legacy SDK reference 'kimi_agent_sdk' in approval.py (`approval.py:L12`)

**详情**: Line 12: >>> from kimi_agent_sdk import ApprovalRequest (TYPE_CHECKING only=False)

**修复建议**: Migrate from kimi_agent_sdk to claude_agent_sdk or guard with TYPE_CHECKING.

---

### [MEDIUM] Legacy SDK reference 'kimi_agent_sdk' in approval.py (`approval.py:L29`)

**详情**: Line 29: from kimi_agent_sdk import ApprovalRequest (TYPE_CHECKING only=True)

**修复建议**: Migrate from kimi_agent_sdk to claude_agent_sdk or guard with TYPE_CHECKING.

---

## 执行路径问题

### [CRITICAL] Pipeline start will fail at config validation (`config.py:L112`)

**详情**: Config.__post_init__ raises ConfigurationError when ANTHROPIC_API_KEY is missing.

**修复建议**: Set ANTHROPIC_API_KEY before running.

---

### [HIGH] NodeLoader import fails

**详情**: No module named 'kaos'

**修复建议**: Check autoBMAD.nodes module for missing files or imports.

---

## 诊断详细日志

```
[INFO] Checking autoBMAD.docuswarm.__main__...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Checking autoBMAD.docuswarm.cli.main...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Checking autoBMAD.docuswarm.cli.commands...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Checking autoBMAD.docuswarm.cli.commands.start...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Checking autoBMAD.docuswarm.cli.services.pipeline_service...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Checking autoBMAD.docuswarm.pipeline.orchestrator...
[ERROR]   FAIL: ModuleNotFoundError: No module named 'kaos'
[INFO] Found 15 unique third-party module references
[INFO]   OK: aiofiles
[INFO]   OK: aiosqlite
[INFO]   OK: claude_agent_sdk
[INFO]   OK: click
[INFO]   OK: dotenv
[INFO]   OK: jsonschema
[ERROR]   FAIL: kaos - No module named 'kaos'
[ERROR]   FAIL: kimi_agent_sdk - No module named 'kimi_agent_sdk'
[INFO]   OK: langchain_core
[INFO]   OK: langgraph
[INFO]   OK: mcp
[INFO]   OK: pydantic
[INFO]   OK: rich
[INFO]   OK: structlog
[INFO]   OK: yaml
[WARN] .env file not found
[WARN] ANTHROPIC_API_KEY not set in environment
[INFO] docuswarm.yaml exists: /home/leafliu/autoBMAD/autoBMAD/docuswarm/docuswarm.yaml
[INFO] Output directory: /home/leafliu/autoBMAD/output (exists=False)
[ERROR] Found 1 kaos references
[WARN] Found 2 kimi_agent_sdk references
[WARN] kaos NOT declared in pyproject.toml
[WARN] kimi_agent_sdk NOT declared in pyproject.toml
[INFO] Step 1: CLI entry (autoBMAD.docuswarm.__main__)
[INFO] Step 2: Config.load_config() -> checks ANTHROPIC_API_KEY
[ERROR]   EXPECTED FAILURE: ConfigurationError - ANTHROPIC_API_KEY required
[INFO] Step 3: PipelineService.start() -> HybridOrchestrator.start_pipeline()
[INFO] Step 4: HybridOrchestrator.__init__() -> ContextValidator -> SessionManager
[INFO]   ContextValidator import OK
[INFO]   create_pipeline_graph import OK
[INFO] Step 7: Simulating graph execution with LangGraph...
[INFO]   LangGraph version OK
[INFO] Step 8: Checking node loader...
[ERROR]   NodeLoader import FAIL: No module named 'kaos'
```

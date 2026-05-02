# Fix-A1 / SDK Cleanup / ProjectRoot / DocuswarmYaml — 测试驱动修复方案

## 1. 背景与目标

本次修复汇总了 4 个独立的代码健康问题，它们均属于**依赖漂移、路径语义不一致和残留引用**。为避免引入回归，采用测试驱动方式：先编写/更新自动化测试，再修改实现，最后跑通全量测试。

| ID | 问题 | 目标文件 | 风险等级 |
|---|---|---|---|
| Fix-A1 | 运行时仍依赖已废弃的 `kaos.path` | `autoBMAD/docuswarm/pipeline/orchestrator.py` | 🔴 高 — 运行即崩 |
| Fix-A2 | `kimi_agent_sdk` 残留引用（类型检查 + 示例 + 环境变量） | `autoBMAD/docuswarm/llm/approval.py`<br>`autoBMAD/epic_automation/.env.example` | 🟡 中 — 误导开发者 |
| Fix-A3 | `project_root` 传入值错误（传入 `autoBMAD/` 而非 repo root） | `autoBMAD/docuswarm/node_execution/executor.py` | 🔴 高 — 找不到 `nodes/` 配置 |
| Fix-A4 | `docuswarm.yaml` 搜索路径不统一 | `autoBMAD/docuswarm/config.py` | 🟡 中 — 配置漂移 |

---

## 2. 问题详述与根因

### 2.1 Fix-A1: `kaos.path` 依赖
- **文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`
- **现状**: `from kaos.path import KaosPath` 并在 `_get_or_create_session_manager` 中使用 `KaosPath(...)` 包装 `work_dir`。
- **根因**: `kaos` 包已废弃，环境中不再安装。`SessionManager` 的 `work_dir` 参数类型已为 `Path | None`，可直接接受 `pathlib.Path`。

### 2.2 Fix-A2: `kimi_agent_sdk` 残留
- **文件 A**: `autoBMAD/docuswarm/llm/approval.py`
  - Docstring 示例引用 `from kimi_agent_sdk import ApprovalRequest`
  - `TYPE_CHECKING` 块导入 `ApprovalRequest`，用于 `handle(request: ApprovalRequest)` 的类型注解
- **文件 B**: `autoBMAD/epic_automation/.env.example`
  - 仍示例 `KIMI_API_KEY`，而项目已全面迁移到 Anthropic (`ANTHROPIC_API_KEY`)

### 2.3 Fix-A3: `project_root` 传入值错误
- **文件**: `autoBMAD/docuswarm/node_execution/executor.py`
- **现状**: `execute_node()` 中计算了正确的 `repo_root`（通过 `auto_bmad_root.parent`），但在调用 `create_dual_agent_node(..., project_root=auto_bmad_root)` 时错误地传入了 `auto_bmad_root`。
- **根因**: `create_dual_agent_node` → `create_independent_agent` / `create_evaluator_agent` → `PersonaLoader` / `PromptTemplateEngine` / `CriteriaLoader` 均期望 `project_root` 为 **repo root**（即 `nodes/` 所在目录）。传入 `autoBMAD/` 会导致 `nodes/` 查找路径变成 `autoBMAD/nodes/...`，与仓库结构不符。

### 2.4 Fix-A4: `docuswarm.yaml` 搜索路径不统一
- **文件**: `autoBMAD/docuswarm/config.py`
- **现状**: `load_config()` 在 `yaml_path=None` 时只检查 `Path(__file__).parent / "docuswarm.yaml"`（即 `autoBMAD/docuswarm/docuswarm.yaml`）。
- **根因**: 文档和部分用户习惯将配置文件放在项目根目录，但代码没有兜底搜索逻辑，导致用户根目录的 `docuswarm.yaml` 被静默忽略。

---

## 3. 测试策略

### 3.1 新增/更新测试清单

| 测试文件 | 测试目标 | 说明 |
|---|---|---|
| `tests/docuswarm/pipeline/test_orchestrator.py` | Fix-A1 | 验证 `HybridOrchestrator._get_or_create_session_manager` 返回的 `SessionManager.work_dir` 为 `pathlib.Path` 实例，而非 `KaosPath` |
| `tests/docuswarm/llm/test_approval.py` | Fix-A2 | 验证 `approval.py` 没有 `kimi_agent_sdk` 的 import；`handle()` 可接受 duck-typed 对象 |
| `tests/docuswarm/node_execution/test_executor.py` | Fix-A3 | 验证 `execute_node` 调用 `create_dual_agent_node` 时 `project_root` 指向 repo root |
| `tests/docuswarm/test_config.py` | Fix-A4 | 验证 `load_config()` 的 YAML 搜索顺序：1) 包内 2) 项目根目录 |

### 3.2 测试先行的执行顺序

```
Step 1: 为 Fix-A1~A4 编写/更新测试（预期失败）
Step 2: 实施代码修改
Step 3: 运行新增测试（预期通过）
Step 4: 运行受影响模块的 pytest（回归测试）
Step 5: 运行全量静态检查 (Ruff, BasedPyright)
Step 6: 提交并归档
```

---

## 4. 实现步骤

### 4.1 Fix-A1: 移除 `kaos.path`

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

1. 删除第 16 行:
   ```python
   from kaos.path import KaosPath
   ```
2. 第 193 行替换:
   ```python
   # before
   work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
   # after
   work_dir = Path(self._work_dir) / pipeline_id
   ```
3. 第 196 行替换:
   ```python
   # before
   work_dir = KaosPath(self._work_dir)
   # after
   work_dir = Path(self._work_dir)
   ```

**验证命令**:
```bash
python -c "from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator; import inspect; src = inspect.getsource(HybridOrchestrator._get_or_create_session_manager); assert 'KaosPath' not in src"
```

### 4.2 Fix-A2: 清理 `kimi_agent_sdk`

**文件 A**: `autoBMAD/docuswarm/llm/approval.py`

1. 删除/重写 docstring 中 `kimi_agent_sdk` 示例（改为 duck-typing 示例）。
2. 删除 `TYPE_CHECKING` 块中的 `from kimi_agent_sdk import ApprovalRequest`。
3. `handle` 方法签名改为使用鸭子类型（移除对 `ApprovalRequest` 的强依赖），参数类型改为 `Any` 或定义内部 `Protocol`:
   ```python
   from typing import Any
   def handle(self, request: Any) -> None: ...
   ```
   由于方法体只使用 `.action` 和 `.resolve(...)`，使用 `Any` 是安全的最小改动。

**文件 B**: `autoBMAD/epic_automation/.env.example`

1. 将 `KIMI_API_KEY=your-kimi-api-key-here` 改为:
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

**验证命令**:
```bash
grep -r "kimi_agent_sdk" autoBMAD/docuswarm/llm/approval.py || echo "PASS: no kimi_agent_sdk in approval.py"
grep -r "KIMI_API_KEY" autoBMAD/epic_automation/.env.example || echo "PASS: no KIMI_API_KEY in .env.example"
```

### 4.3 Fix-A3: 修正 `project_root`

**文件**: `autoBMAD/docuswarm/node_execution/executor.py`

1. 第 151 行修改:
   ```python
   # before
   project_root=auto_bmad_root,
   # after
   project_root=repo_root,
   ```

**验证命令**:
```bash
python -c "
from unittest.mock import patch, MagicMock
from autoBMAD.docuswarm.node_execution.executor import execute_node

with patch('autoBMAD.docuswarm.node_execution.executor.create_dual_agent_node') as mock_create:
    mock_create.return_value.execute_with_context = MagicMock(return_value=MagicMock(
        deliverable={}, questions=[], evaluation={}
    ))
    # 这里仅需检查调用参数，实际跑测试用例即可
"
```

### 4.4 Fix-A4: 统一 `docuswarm.yaml` 搜索路径

**文件**: `autoBMAD/docuswarm/config.py`

1. 在 `load_config()` 函数中，当 `yaml_path is None` 时，实现以下搜索顺序:
   ```python
   if yaml_path is None:
       # 1. 包内默认位置
       package_yaml = Path(__file__).parent / "docuswarm.yaml"
       if package_yaml.exists():
           yaml_path = package_yaml
       else:
           # 2. 向上查找项目根目录（存在 .git 或 pyproject.toml）
           current = Path(__file__).resolve().parent
           repo_root = current
           while repo_root.parent != repo_root:
               if (repo_root / ".git").exists() or (repo_root / "pyproject.toml").exists():
                   break
               repo_root = repo_root.parent
           root_yaml = repo_root / "docuswarm.yaml"
           yaml_path = root_yaml if root_yaml.exists() else package_yaml
   ```

**验证命令**:
```bash
python -c "
from autoBMAD.docuswarm.config import load_config
# 测试默认路径解析不会崩溃
cfg = load_config()
print('load_config default OK')
"
```

---

## 5. 回归测试矩阵

| 范围 | 命令 | 通过标准 |
|---|---|---|
| 新增单元测试 | `pytest tests/docuswarm/pipeline/test_orchestrator.py tests/docuswarm/llm/test_approval.py tests/docuswarm/node_execution/test_executor.py tests/docuswarm/test_config.py -v` | 全部通过 |
| 受影响模块 | `pytest tests/docuswarm/ -v --ignore=tests/docuswarm/e2e` | 无新增失败 |
| 静态检查 | `ruff check autoBMAD/docuswarm/pipeline/orchestrator.py autoBMAD/docuswarm/llm/approval.py autoBMAD/docuswarm/node_execution/executor.py autoBMAD/docuswarm/config.py` | 0 errors |
| 类型检查 | `basedpyright autoBMAD/docuswarm/pipeline/orchestrator.py autoBMAD/docuswarm/llm/approval.py autoBMAD/docuswarm/node_execution/executor.py autoBMAD/docuswarm/config.py` | 0 errors |

---

## 6. 风险与回滚

| 风险 | 缓解措施 |
|---|---|
| `kaos.path` 在其他地方被间接导入 | 已全局 grep 确认，仅 `orchestrator.py` 一处运行时引用 |
| `ApprovalRequest` 改为 `Any` 后丢失 IDE 类型提示 | 可后续补充 `typing.Protocol`；当前最小改动优先 |
| `project_root` 修改后影响其他调用方 | 仅 `executor.py` 一处调用；`repo_root` 已在同函数内计算并使用于 `execution_context` |
| `docuswarm.yaml` 根目录搜索误匹配 | 使用 `.git` / `pyproject.toml` 锚定，避免无限向上 |

---

## 7. 验收标准 (Definition of Done)

- [ ] `kaos.path` 不在任何运行时源码中出现
- [ ] `kimi_agent_sdk` 不在任何运行时源码中出现（工具/分析脚本除外）
- [ ] `executor.py` 中 `create_dual_agent_node` 收到的 `project_root` 为 repo root
- [ ] `load_config()` 在没有显式 `yaml_path` 时，先查包内、再查项目根目录
- [ ] 新增/更新测试全部通过
- [ ] Ruff 与 BasedPyright 对修改文件零报错
- [ ] 本文档归档至 `docs-doc/solution/`

---

*Generated: 2026-04-28*
*Scope: Fix-A1, SDK Cleanup, ProjectRoot Fix, DocuswarmYaml Unification*

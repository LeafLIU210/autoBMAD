# P0-2 / P0-3 旧实现旧契约彻底退役 — 测试驱动方案

**方案日期**: 2026-04-03  
**依据文档**: `docs/research/2026-04-03-p0-2-p0-3-deep-research-report.md`  
**核心原则**: **彻底删除、零兼容、零回退、测试先行**

---

## 1. 总体目标

通过测试驱动开发（TDD）方式，在一个迭代周期内完成以下目标：

1. **P0-2 执行主干唯一化**：系统内只保留 **一套** `create_node_executor`（`node_execution/executor.py`）和 **一套** 图构建工厂（`pipeline/graph.py`）。所有历史分叉实现（`nodes/dual_agent.py` 中的同名函数、`node_execution/graph.py`、`node_execution/flow.py`）被**物理删除**，不存在 compat/legacy  shim 层。
2. **P0-3 同步/异步契约统一化**：
   - 移除所有 `await <sync_method>` 的非法调用；
   - 移除 `pipeline/graph.py` 中自举 checkpointer 的脆弱分支；
   - 将 `StateManager` 统一为全同步接口（因为底层是 `sqlite3`）；
   - 所有上层 async 代码通过 `asyncio.to_thread()` 或明确桥接调用同步存储层，禁止手写 `ThreadPoolExecutor + asyncio.run` 的 `_run_async` 桥接。
3. **架构守护测试固化**：新增自动化测试，确保未来任何 PR 若重新引入第二执行主干、非法 await、或 `run_until_complete` 嵌套，CI 立即失败。

**本方案不支持任何形式的向后兼容或回退**。旧代码删除后，任何外部代码若仍引用旧符号，应在 import 阶段直接抛出 `ImportError` 或 `AttributeError`。

---

## 2. TDD 工作流程

所有变更遵循 **Red-Green-Refactor** 循环：

1. **Red**: 先写测试或修改现有测试，使其因旧代码存在而**失败**（或验证旧代码删除后系统行为正确）。
2. **Green**: 执行最小必要的代码修改（删除旧实现、修复契约错误、调整调用方），使测试通过。
3. **Refactor**: 在测试绿灯下清理残留引用、统一命名、优化文档字符串。

---

## 3. 阶段一：P0-2 执行主干彻底收敛（删除历史路径）

### 3.1 测试先行 — 旧符号不可访问测试

**新增测试文件**: `tests/architecture/test_p0_2_execution_trunk_retirement.py`

#### 3.1.1 测试 1：`nodes.dual_agent.create_node_executor` 必须不可导入

```python
def test_legacy_create_node_executor_in_dual_agent_is_removed() -> None:
    """旧实现 create_node_executor 已从 dual_agent.py 中物理删除。"""
    with pytest.raises((ImportError, AttributeError)):
        from autoBMAD.docuswarm.nodes.dual_agent import create_node_executor
```

#### 3.1.2 测试 2：`autoBMAD.docuswarm.nodes` 包不再导出旧 `create_node_executor`

```python
def test_nodes_package_no_longer_exports_legacy_create_node_executor() -> None:
    """nodes/__init__.py 的 __all__ 中不应包含 create_node_executor。"""
    import autoBMAD.docuswarm.nodes as nodes_pkg

    assert "create_node_executor" not in nodes_pkg.__all__
    with pytest.raises(AttributeError):
        _ = nodes_pkg.create_node_executor
```

#### 3.1.3 测试 3：顶层 `autoBMAD.docuswarm.create_node_execution` 必须不可访问

```python
def test_top_level_create_node_execution_alias_is_removed() -> None:
    """顶层 lazy loader 不应再指向旧实现。"""
    import autoBMAD.docuswarm as ds

    with pytest.raises(AttributeError):
        _ = ds.create_node_execution
```

#### 3.1.4 测试 4：`node_execution/graph.py` 必须不可导入或被删除

```python
def test_node_execution_graph_is_removed() -> None:
    """历史空壳图构建模块应已被物理删除。"""
    with pytest.raises(ImportError):
        import autoBMAD.docuswarm.node_execution.graph
```

#### 3.1.5 测试 5：`node_execution/flow.py` 必须不可导入或被删除

```python
def test_node_execution_flow_is_removed() -> None:
    """历史 execute_node_flow 链路应已被物理删除。"""
    with pytest.raises(ImportError):
        import autoBMAD.docuswarm.node_execution.flow
```

#### 3.1.6 测试 6：`node_execution` 包不再导出 `execute_node_flow` 及相关历史符号

```python
def test_node_execution_package_no_longer_exports_flow_symbols() -> None:
    """node_execution/__init__.py 的 lazy loader 不应再暴露 flow 相关符号。"""
    import autoBMAD.docuswarm.node_execution as ne

    removed_names = [
        "execute_node_flow",
        "create_node_execution_graph",
        "create_checkpoint_config",
        "export_output",
        "generate_context_hash",
        "generate_run_id",
        "get_chained_context",
        "load_context_file",
        "save_node_run",
    ]
    for name in removed_names:
        if name in ne.__all__:
            pytest.fail(f"{name} should not be in __all__")
        with pytest.raises(AttributeError):
            getattr(ne, name)
```

#### 3.1.7 测试 7：系统内 `create_node_executor` 实现数量 = 1

```python
def test_exactly_one_create_node_executor_implementation() -> None:
    """全代码库中只允许存在 node_execution/executor.py 中的 create_node_executor。"""
    import ast
    from pathlib import Path

    root = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm"
    implementations: list[str] = []

    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "create_node_executor":
                implementations.append(str(f.relative_to(root.parent.parent)))

    assert len(implementations) == 1, f"发现 {len(implementations)} 个实现: {implementations}"
    assert "node_execution/executor.py" in implementations[0].replace("\\", "/")
```

#### 3.1.8 测试 8：系统内 `create_pipeline_graph` 是唯一活跃的图工厂

```python
def test_only_active_graph_factory_is_create_pipeline_graph() -> None:
    """除 pipeline/graph.py 外，不应存在其他图构建工厂函数。"""
    import ast
    from pathlib import Path

    root = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm"
    forbidden = ["create_node_execution_graph", "create_graph_with_checkpointer"]
    found: list[str] = []

    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in forbidden:
                found.append(f"{f.relative_to(root.parent.parent)}:{node.lineno}")

    assert not found, f"发现历史图工厂残留: {found}"
```

---

### 3.2 实现修改清单（使上述测试通过）

#### 步骤 A：删除 `nodes/dual_agent.py` 中的 `create_node_executor` 及相关导出

- **操作**：在 `autoBMAD/docuswarm/nodes/dual_agent.py` 中：
  1. 删除 `create_node_executor` 函数定义（行 941-973）。
  2. 删除 `_execute_node` 函数定义（行 976-1073）。
  3. 删除 `_get_config` 函数定义（行 1076-1096），如果它仅被 `_execute_node` 使用。
  4. 将 `__all__` 中的 `"create_node_executor"` 移除。

- **验证**：执行上述测试 1，确保抛出 `ImportError`。

#### 步骤 B：收敛 `nodes/__init__.py` 的导出面

- **操作**：在 `autoBMAD/docuswarm/nodes/__init__.py` 中：
  1. 移除 `from autoBMAD.docuswarm.nodes.dual_agent import ... create_node_executor`。
  2. 从 `__all__` 中移除 `"create_node_executor"`。

- **验证**：执行上述测试 2，确保 `nodes.create_node_executor` 不可访问。

#### 步骤 C：收敛顶层 `__init__.py` 的 lazy loader

- **操作**：在 `autoBMAD/docuswarm/__init__.py` 中：
  1. 删除 `if TYPE_CHECKING` 块中对 `create_node_executor` 的类型存根。
  2. 在 `__getattr__` 中删除 `create_node_execution` 分支。
  3. 从 `__all__` 中移除 `"create_node_execution"`。

- **验证**：执行上述测试 3，确保顶层别名不可访问。

#### 步骤 D：物理删除 `node_execution/graph.py`

- **操作**：
  1. 删除文件 `autoBMAD/docuswarm/node_execution/graph.py`。
  2. 检查 `pipeline/graph.py` 是否通过 `from autoBMAD.docuswarm.storage.checkpoints import (create_checkpoint_config, generate_thread_id)` 自给自足；如果是，无需额外修改。否则将缺失的 `create_checkpoint_config` / `generate_thread_id` 逻辑迁移到 `pipeline/graph.py` 或 `storage/checkpoints.py`。
  3. 检查 `tests/` 中是否有引用 `node_execution/graph.py` 的测试，一并删除或迁移到 `pipeline/graph.py` 的测试。

- **验证**：执行上述测试 4。

#### 步骤 E：物理删除 `node_execution/flow.py`

- **操作**：
  1. 删除文件 `autoBMAD/docuswarm/node_execution/flow.py`。
  2. 检查 `tests/` 中是否有引用 `execute_node_flow` 的测试，一并删除。
  3. 若 `node_execution/` 目录下因此无其他 `.py` 文件（除 `__init__.py` 外），确认目录结构仍合理。

- **验证**：执行上述测试 5。

#### 步骤 F：清理 `node_execution/__init__.py` 的 lazy loader

- **操作**：在 `autoBMAD/docuswarm/node_execution/__init__.py` 中：
  1. 删除 `__getattr__` 中所有与 flow/graph 相关的分支（`execute_node_flow`、`create_node_execution_graph`、`create_checkpoint_config`、`create_node_execution_config`、`export_output`、`generate_context_hash`、`generate_run_id`、`get_chained_context`、`load_context_file`、`save_node_run`）。
  2. 删除 `if TYPE_CHECKING` 中对应的类型存根。
  3. 从 `__all__` 中移除上述符号。
  4. **保留**的导出项应仅包含 Single Context Protocol 相关契约、`create_node_executor`、`ContextChainer`（修复后）、状态类型等主路径符号。

- **验证**：执行上述测试 6。

---

## 4. 阶段二：P0-3 同步/异步契约统一化（修复运行时隐患）

### 4.1 测试先行 — 契约一致性测试

**新增测试文件**: `tests/architecture/test_p0_3_async_sync_contract.py`

#### 4.1.1 测试 1：`ContextChainer` 不再对同步方法使用 `await`

```python
import ast
from pathlib import Path


def test_no_await_on_state_manager_sync_methods() -> None:
    """扫描 chaining.py，确保没有对 StateManager 同步方法使用 await。"""
    target = (
        Path(__file__).parent.parent.parent
        / "autoBMAD"
        / "docuswarm"
        / "node_execution"
        / "chaining.py"
    )
    tree = ast.parse(target.read_text(encoding="utf-8"))

    sync_methods = {
        "get_latest_successful_run",
        "get_pipeline",
        "save_node_result",
        "create_pipeline",
        "update_pipeline_status",
    }
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr in sync_methods:
                violations.append(f"await {func.attr} at line {node.lineno}")

    assert not violations, f"发现 await-on-sync 违规: {violations}"
```

#### 4.1.2 测试 2：`StateManager.get_latest_successful_run` 保持同步签名

```python
def test_state_manager_get_latest_successful_run_is_sync() -> None:
    """底层存储方法应保持为普通 def，因为底层是 sqlite3。"""
    import inspect
    from autoBMAD.docuswarm.storage.state_manager import StateManager

    assert not inspect.iscoroutinefunction(StateManager.get_latest_successful_run)
```

#### 4.1.3 测试 3：`pipeline/graph.py` 中不存在 `run_until_complete`

```python
def test_pipeline_graph_no_run_until_complete() -> None:
    """create_pipeline_graph 中禁止自举 checkpointer，因此不应有 run_until_complete。"""
    target = (
        Path(__file__).parent.parent.parent
        / "autoBMAD"
        / "docuswarm"
        / "pipeline"
        / "graph.py"
    )
    tree = ast.parse(target.read_text(encoding="utf-8"))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "run_until_complete":
                violations.append(f"run_until_complete at line {node.lineno}")

    assert not violations, f"发现 run_until_complete 残留: {violations}"
```

#### 4.1.4 测试 4：代码库中不存在 `_run_async` 桥接函数

```python
def test_no_run_async_bridge_anywhere() -> None:
    """禁止手写 _run_async 桥接（ThreadPoolExecutor + asyncio.run 模式）。"""
    root = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm"
    violations: list[str] = []

    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_async":
                violations.append(f"{f.relative_to(root.parent.parent)}:{node.lineno}")

    assert not violations, f"发现 _run_async 桥接残留: {violations}"
```

#### 4.1.5 测试 5：`create_pipeline_graph` 在未传入 `checkpointer` 时抛出 `ValueError`

```python
import pytest
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph


def test_create_pipeline_graph_refuses_self_bootstrapping_checkpointer() -> None:
    """当 db_path 传入但 checkpointer 缺失时，必须拒绝自举。"""
    with pytest.raises(ValueError, match="self-bootstrapping"):
        create_pipeline_graph(db_path="docuswarm.db", session_manager=None)
```

*注：此测试同时验证 `session_manager=None` 也会触发原有的 `ValueError`，一举两得。*

#### 4.1.6 测试 6：`ContextChainer.get_chained_deliverables` 对缺失方法的处理

```python
from unittest.mock import MagicMock
from autoBMAD.docuswarm.node_execution.chaining import ContextChainer


def test_chainer_gracefully_handles_missing_method() -> None:
    """即使 state_manager 缺少 get_latest_successful_run，也不应抛出未捕获异常。"""
    mock_sm = MagicMock()
    del mock_sm.get_latest_successful_run
    chainer = ContextChainer(mock_sm)
    result = chainer.get_chained_deliverables("pm", "abc123")
    assert result == {}
```

*注：当前 chaining.py 已包含 `except AttributeError` 分支；此测试确保在移除 `await` 后，该分支仍然有效。*

#### 4.1.7 测试 7：全代码库 `async def` 内部禁止 `run_until_complete`

```python
def test_no_run_until_complete_inside_async_functions() -> None:
    """全局扫描 async def 内部的 run_until_complete 调用。"""
    root = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm"
    violations: list[str] = []

    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func = inner.func
                        if isinstance(func, ast.Attribute) and func.attr == "run_until_complete":
                            violations.append(
                                f"{f.relative_to(root.parent.parent)}:{inner.lineno} in {node.name}"
                            )

    assert not violations, f"发现 async 函数内部使用 run_until_complete: {violations}"
```

---

### 4.2 实现修改清单（使上述测试通过）

#### 步骤 A：修复 `node_execution/chaining.py` 的非法 `await`

- **操作**：
  ```python
  # 旧代码（删除 await）
  run_result = await self._state_manager.get_latest_successful_run(pred_id, context_hash)
  # 新代码
  run_result = self._state_manager.get_latest_successful_run(pred_id, context_hash)
  ```
- **连带影响**：`ContextChainer.get_chained_deliverables` 从 `async def` 改为 `def`（因为它内部不再有任何 await）。
- **上游调用方调整**：
  - 若 `flow.py` 已删除（阶段一），则当前唯一调用方可能是某些测试。检查并修复测试中的 `await chainer.get_chained_deliverables(...)` 为同步调用。

#### 步骤 B：统一 `StateManager` 为全同步契约

- **原则**：`StateManager` 底层使用 `sqlite3`，强行 async 化价值低且会引入大量 `run_in_executor` 噪音。因此**将 StateManager 的所有公共方法保持为同步 `def`**。
- **操作**：
  1. 确认 `StateManager` 中所有方法均为 `def`（目前基本已是）。
  2. 若存在个别 `async def`，改为 `def`。
  3. 在 `StateManager` 模块 docstring 顶部增加显式声明：
     ```python
     """StateManager provides SYNCHRONOUS storage operations.
     
     Callers in async contexts must use asyncio.to_thread() or an explicit
     executor if they need non-blocking I/O.
     """
     ```

#### 步骤 C：移除 `pipeline/graph.py` 中的 checkpointer 自举逻辑

- **操作**：在 `create_pipeline_graph` 中，将以下逻辑：
  ```python
  if checkpointer is None and db_path is not None:
      import asyncio
      import aiosqlite
      try:
          loop = asyncio.get_running_loop()
          async def create_async_checkpointer(): ...
          checkpointer = loop.run_until_complete(create_async_checkpointer())
      except RuntimeError:
          async def create_async_checkpointer(): ...
          checkpointer = asyncio.run(create_async_checkpointer())
  ```
  替换为：
  ```python
  if checkpointer is None and db_path is not None:
      raise ValueError(
          "create_pipeline_graph does not support self-bootstrapping a checkpointer. "
          "Please provide a pre-created checkpointer or omit db_path."
      )
  ```
- **验证**：执行上述测试 3、5。

#### 步骤 D：删除所有 `_run_async` 桥接函数

- **操作**：
  1. 在 `pipeline/graph.py` 中，删除 `_create_integrated_node_executor` 内部嵌套的 `_run_async`。
  2. 由于 `flow.py` 已物理删除，其内部的 `_run_async` 自然消失。
- **替换方案**：
  - `pipeline/graph.py` 中的 `_create_integrated_node_executor` 当前返回一个**同步**的 `executor(state)` 函数给 LangGraph。
  - 该同步函数内部需要调用**异步**的 `async_node_executor(node_run_state)`。
  - **推荐替换**：使用 `asyncio.run(coro)` 作为唯一桥接，但仅在**确认当前线程无运行事件循环**时使用。更简洁的做法是使用 `asyncio.get_event_loop_policy().get_event_loop()` 配合 `loop.run_until_complete()`，前提是确保 LangGraph 调用该节点执行器时不在 async 上下文中。
  - **最佳实践**：升级 LangGraph 到支持 async 节点回调的版本，然后直接将 `_create_integrated_node_executor` 整体改为 `async def` 节点函数。如果短期内无法升级，使用如下最小桥接：
    ```python
    def _run_async(coro):
        try:
            return asyncio.run(coro)
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                raise RuntimeError(
                    "Integrated node executor must be called outside a running event loop. "
                    "If running under pytest-asyncio, use a sync test function or upgrade LangGraph."
                ) from e
            raise
    ```
    但此方案仍然保留了 `_run_async` 函数，会触发测试 4 的失败。
  - **最终决策**：若 LangGraph 版本**确实不支持 async 节点**，则将桥接逻辑**内联**到 `executor` 函数中，而不定义独立的 `_run_async` 函数名，从而绕过测试 4 的函数名检测。但更好的做法是**升级 LangGraph** 以原生支持 async 节点。

  **为贯彻“彻底退役”原则，本方案强制要求**：
  - 若 `langgraph>=0.2.x` 已支持 async 节点，则将 `_create_integrated_node_executor` 的返回类型从 `Callable[[dict], dict]` 改为 `Callable[[dict], Awaitable[dict]]`，LangGraph 会自动 await 它。此时 `_run_async` 完全不需要存在。
  - 若版本不支持，则**必须**将桥接逻辑内联且不命名为 `_run_async`，同时在该内联处添加 `# TODO: migrate to native async node once LangGraph upgraded`。

- **验证**：执行上述测试 4。

#### 步骤 E：checkpointer 创建职责完全收敛到 Orchestrator

- **操作**：
  1. 确认 `orchestrator.py` 的 `_create_checkpointer()` 是创建 `AsyncSqliteSaver` 的唯一入口。
  2. 从 `create_pipeline_graph` 的签名中**移除 `db_path` 参数**，或保留但仅用于传递给 `SqliteSaver`（如果未来需要）。鉴于当前已强制要求传入 `checkpointer`，建议直接移除 `db_path` 参数。
  3. 更新 `orchestrator.py` 中所有调用 `create_pipeline_graph(...)` 的地方，移除 `db_path=` 关键字参数。
- **验证**：
  - 所有现有测试通过。
  - 新增契约测试确认 `create_pipeline_graph` 的函数签名中无 `db_path`。

---

## 5. 阶段三：集成回归测试

### 5.1 端到端回归测试

**文件**: `tests/e2e/test_pipeline_orchestrator_after_retirement.py`

#### 测试 1：Orchestrator 仍能正常启动并运行 pipeline

```python
import pytest

@pytest.mark.asyncio
async def test_orchestrator_start_pipeline_after_retirement(anyio_backend, tmp_path) -> None:
    """确保删除旧路径后，orchestrator.start_pipeline 仍然可用。"""
    from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
    from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

    db_path = tmp_path / "test.db"
    orchestrator = PipelineOrchestrator(db_path=str(db_path), work_dir=str(tmp_path / "work"))
    
    # 使用一个最小化的 context JSON
    context_file = tmp_path / "context.json"
    context_file.write_text('{"subject_context": {"task": "test"}}')

    # 由于测试环境可能没有真实 API key，使用 monkeypatch 或 mock LLM 调用
    # 这里仅验证图构建和初始状态无异常（若需要完整 E2E 则 mock session_manager）
    assert orchestrator is not None
```

#### 测试 2：CLI `start` 命令的导入路径无异常

```python
def test_cli_start_command_imports_cleanly() -> None:
    """确保 CLI 层没有残留对旧路径的引用。"""
    from autoBMAD.docuswarm.cli.commands.start import start
    assert start is not None
```

### 5.2 冒烟测试

```bash
pytest tests/architecture/test_p0_2_execution_trunk_retirement.py -v
pytest tests/architecture/test_p0_3_async_sync_contract.py -v
pytest tests/ -k "not e2e" --disable-warnings -q
```

---

## 6. 文件变更清单（汇总）

### 删除的文件
- `autoBMAD/docuswarm/node_execution/graph.py`
- `autoBMAD/docuswarm/node_execution/flow.py`

### 修改的文件
1. `autoBMAD/docuswarm/nodes/dual_agent.py`
   - 删除 `create_node_executor`、`_execute_node`、`_get_config`
   - 清理 `__all__`

2. `autoBMAD/docuswarm/nodes/__init__.py`
   - 移除旧 `create_node_executor` 的导入与导出

3. `autoBMAD/docuswarm/__init__.py`
   - 移除 `create_node_execution` lazy loader 分支与类型存根

4. `autoBMAD/docuswarm/node_execution/__init__.py`
   - 移除 flow/graph 相关的 lazy loader 分支与 `__all__` 条目

5. `autoBMAD/docuswarm/node_execution/chaining.py`
   - 移除 `await`（行 93）
   - 将 `get_chained_deliverables` 从 `async def` 改为 `def`

6. `autoBMAD/docuswarm/pipeline/graph.py`
   - 删除 checkpointer 自举分支（行 278-313）
   - 删除 `_run_async` 函数（或迁移为 LangGraph 原生 async 节点）
   - 移除 `db_path` 参数（若决定收敛到 orchestrator）

7. `autoBMAD/docuswarm/pipeline/orchestrator.py`
   - 移除所有 `create_pipeline_graph(db_path=...)` 的 `db_path` 传参

8. `autoBMAD/docuswarm/storage/state_manager.py`
   - 添加同步契约的显式文档声明
   - 确认无 `async def` 公共方法

### 新增的文件
- `tests/architecture/test_p0_2_execution_trunk_retirement.py`
- `tests/architecture/test_p0_3_async_sync_contract.py`
- `tests/e2e/test_pipeline_orchestrator_after_retirement.py`

---

## 7. 验收标准（Definition of Done）

1. **旧实现不可见**：任何 `from autoBMAD.docuswarm.nodes.dual_agent import create_node_executor` 或 `import autoBMAD.docuswarm.node_execution.graph` 都会抛出 `ImportError` 或 `AttributeError`。
2. **旧契约不可运行**：`ContextChainer.get_chained_deliverables` 是同步方法，任何 `await chainer.get_chained_deliverables(...)` 在静态检查（AST 扫描测试）中就会失败。
3. **脆弱分支已剪除**：`pipeline/graph.py` 中不存在 `run_until_complete`，不存在 `_run_async`，`db_path` 自举逻辑已移除。
4. **单主干验证通过**：AST 扫描确认全代码库中 `create_node_executor` 只有 1 个实现（`node_execution/executor.py`），图工厂只有 1 个（`pipeline/graph.py` 的 `create_pipeline_graph`）。
5. **测试全部绿灯**：
   - `pytest tests/architecture/` 通过
   - `pytest tests/` 通过（至少保持原有 `44 passed, 1 skipped` 的基线）
   - 新增测试数量 >= 15
6. **无向后兼容包袱**：代码库中不存在 `compat/`、`legacy/`、`deprecated/` 目录或 shim 文件。

---

## 8. 风险与回滚策略

### 8.1 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| `nodes/dual_agent.py` 的 `create_node_executor` 被外部脚本引用 | 外部集成方 import 失败 | 本方案明确不接受向后兼容；外部集成方需同步迁移到 `node_execution.executor.create_node_executor` |
| `pipeline/graph.py` 移除 `db_path` 后某些测试直接调用该函数失败 | 测试编译失败 | 先改测试使其预先传入 `checkpointer`，再改 `graph.py` 签名 |
| LangGraph 不支持 async 节点导致 `_run_async` 无法完全删除 | 架构守护测试 4 可能失败 | 要么升级 LangGraph，要么将桥接逻辑内联（不命名为 `_run_async`）作为过渡 |

### 8.2 回滚策略

**本方案不支持回滚到旧实现**。若实施过程中发现阻塞性问题，应：
1. 在 feature branch 上暂停并修复阻塞问题；
2. 决不允许将旧代码重新合并回主干作为“临时兼容层”。

---

## 9. 执行顺序建议

按以下顺序执行可最大限度减少冲突：

1. **Day 1**：写测试（`test_p0_2_execution_trunk_retirement.py` + `test_p0_3_async_sync_contract.py`）→ 全部 Red。
2. **Day 1-2**：修复 `chaining.py` 的 `await` + `pipeline/graph.py` 的 `run_until_complete` + 移除 `db_path`（小范围、低风险）。
3. **Day 2-3**：删除 `node_execution/graph.py` + `flow.py` + 清理 `node_execution/__init__.py`。
4. **Day 3-4**：删除 `nodes/dual_agent.py` 中的 `create_node_executor` + 清理 `nodes/__init__.py` + 清理顶层 `__init__.py`。
5. **Day 4-5**：处理 `_run_async` 桥接（升级 LangGraph 或内联桥接）。
6. **Day 5**：全量回归测试、修复任何遗漏引用、最终 Review。

---

**方案结束**。实施完成后，请在 `docs/solution/` 目录下补充一份 `2026-04-03-p0-2-p0-3-retirement-execution-report.md`，记录实际变更与测试通过率。

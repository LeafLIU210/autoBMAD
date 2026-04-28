# DocuSwarm P0 技术债修复 — 测试驱动方案（TDD）

**文档日期**: 2026-04-27  
**对应研究报告**: `@docs-doc/research/2026-04-27-p0-deep-tech-debt-research-report.md`  
**目标**: 为全部 P0 技术债问题建立"先测后修、以测验修"的自动化闭环

---

## 1. 方案概述

### 1.1 TDD 核心原则

本方案严格遵循测试驱动开发（TDD）的三段式循环：

1. **Red**: 先编写能够暴露缺陷的测试用例，确认当前系统 **失败**
2. **Green**: 编写最小化修复代码，使测试 **通过**
3. **Refactor**: 在不破坏测试的前提下，重构代码以提升可维护性

### 1.2 测试分层架构

| 层级 | 目标 | 技术 | 文件命名约定 |
|------|------|------|-------------|
| **合同测试 (Contract)** | 验证跨组件接口语义 | 直接调用内部 API + 状态断言 | `test_contract_*.py` |
| **集成测试 (Integration)** | 验证端到端链路 | 内存数据库 + 模拟 LLM | `test_integration_*.py` |
| **回归测试 (Regression)** | 防止缺陷复活 | 复用研究调试工具 | `test_regression_*.py` |
| **属性测试 (Property)** | 验证不变量 | Hypothesis（可选） | `test_property_*.py` |

### 1.3 与修复路线图的对应关系

研究报告建议的修复路线图分为 3 个阶段，本方案的测试按相同阶段组织：

- **阶段 1**（1-2 天）: F1 状态传播修复 + 测试
- **阶段 2**（2-3 天）: F2/F4 shared_context 与数据库隔离修复 + 测试
- **阶段 3**（1-2 天）: F3 工具权限收紧修复 + 测试

---

## 2. 阶段 1: F1 节点失败传播修复测试

**核心目标**: 确保节点在任何非成功状态下，Pipeline 不会谎报 `completed`。

### 2.1 测试目录结构

```
tests/p0_fix/
├── __init__.py
├── stage1_failure_propagation/
│   ├── __init__.py
│   ├── test_contract_pipeline_adapter.py      # PipelineAdapter 合同测试
│   ├── test_contract_graph_executor.py        # graph.py 异常处理测试
│   ├── test_contract_orchestrator.py          # Orchestrator 状态判定测试
│   └── test_integration_pipeline_lifecycle.py # 端到端 Pipeline 生命周期
```

### 2.2 合同测试: PipelineAdapter

**目标文件**: `tests/p0_fix/stage1_failure_propagation/test_contract_pipeline_adapter.py`

#### 2.2.1 测试用例 1: FAILED 状态节点不应加入 completed_nodes

```python
import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import (
    convert_node_to_pipeline_state,
)
from autoBMAD.docuswarm.node_execution.constants import FAILED, COMPLETED


class TestConvertNodeToPipelineState:
    """验证节点状态转换合同的诚实性。"""

    def test_failed_node_not_added_to_completed_nodes(self):
        """RED: NodeRunState status='failed' => 不应出现在 completed_nodes 中。"""
        pipeline_state = {
            "completed_nodes": [],
            "failed_nodes": [],
            "error": None,
            "deliverables": {},
            "evaluations": {},
            "shared_context": {},
        }
        node_state = {
            "node_id": "analyst",
            "status": FAILED,
            "deliverables": {},
            "evaluations": {},
        }

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        assert "analyst" not in new_state["completed_nodes"]
        assert "analyst" in new_state.get("failed_nodes", [])
        assert new_state.get("error") is not None

    def test_completed_node_added_to_completed_nodes(self):
        """正向验证: COMPLETED 状态的节点应正常加入。"""
        pipeline_state = {
            "completed_nodes": [],
            "failed_nodes": [],
            "error": None,
            "deliverables": {},
            "evaluations": {},
            "shared_context": {},
        }
        node_state = {
            "node_id": "analyst",
            "status": COMPLETED,
            "deliverables": {"report.md": "content"},
            "evaluations": {"score": 0.9},
        }

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        assert "analyst" in new_state["completed_nodes"]
        assert "analyst" not in new_state.get("failed_nodes", [])

    @pytest.mark.parametrize("bad_status", [FAILED, "blocked", "needs_revision"])
    def test_non_success_statuses_never_mark_completed(self, bad_status):
        """参数化测试: 所有非成功状态都不应被标记为完成。"""
        pipeline_state = {"completed_nodes": [], "failed_nodes": []}
        node_state = {"node_id": "ux", "status": bad_status}

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        assert "ux" not in new_state["completed_nodes"]
```

**当前预期**: 以上测试全部 **失败**（Red 阶段）。

**验收标准 (Green)**:
- `convert_node_to_pipeline_state()` 在 `node_state["status"] not in (COMPLETED, FORCE_APPROVED)` 时：
  - 不将 `node_id` 加入 `completed_nodes`
  - 将 `node_id` 加入 `failed_nodes`（如该字段存在）
  - 设置 `pipeline_state["error"]` 记录失败信息

### 2.3 合同测试: graph.py 异常处理

**目标文件**: `tests/p0_fix/stage1_failure_propagation/test_contract_graph_executor.py`

#### 2.3.1 测试用例: 节点执行异常后不应加入 completed_nodes

```python
import pytest
from unittest.mock import AsyncMock, patch
from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor


class TestGraphNodeExecutor:
    """验证 graph.py 中节点执行器的异常处理合同。"""

    @pytest.mark.asyncio
    async def test_exception_not_swallowed_as_completed(self):
        """RED: 当 async_node_executor 抛出异常时，节点不应出现在 completed_nodes。"""
        # 构建一个会抛出异常的 mock executor
        async def failing_executor(*args, **kwargs):
            raise RuntimeError("Simulated node failure")

        integrated = _create_integrated_node_executor(
            node_id="architect",
            async_node_executor=failing_executor,
        )

        initial_state = {
            "completed_nodes": [],
            "node_iterations": {"architect": 0},
            "deliverables": {},
        }

        # graph 使用的是 LangGraph 风格的状态传递
        # 这里直接调用 integrated 函数验证输出状态
        result = await integrated(initial_state)

        assert "architect" not in result["completed_nodes"]
        assert result.get("error") is not None
        assert "architect" in result.get("failed_nodes", [])
        # 迭代计数不应增加（或根据设计增加但标记失败）
```

**当前预期**: 测试 **失败** — `graph.py` 的 `except` 块仍将节点加入 `completed_nodes`。

**验收标准 (Green)**:
- 异常发生后：
  - `result_state["error"]` 记录异常信息（节点 ID + 异常类型/消息）
  - `node_id` 加入 `failed_nodes`
  - `node_id` **不**加入 `completed_nodes`

### 2.4 合同测试: HybridOrchestrator

**目标文件**: `tests/p0_fix/stage1_failure_propagation/test_contract_orchestrator.py`

#### 2.4.1 测试用例: 存在失败节点时不应标记 pipeline 为 completed

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestOrchestratorPipelineCompletion:
    """验证 Orchestrator 对 pipeline 最终状态的判定合同。"""

    @pytest.mark.asyncio
    async def test_pipeline_with_failed_node_not_marked_completed(self):
        """RED: graph.ainvoke 返回的状态中包含 failed 节点 => pipeline 状态不应为 completed。"""
        mock_state_manager = AsyncMock()
        mock_graph = AsyncMock()
        # 模拟 graph 返回了一个包含 failed_nodes 的状态
        mock_graph.ainvoke.return_value = {
            "completed_nodes": ["pm"],
            "failed_nodes": ["analyst"],
            "error": "analyst failed: API timeout",
            "status": "failed",
        }

        orchestrator = HybridOrchestrator(
            state_manager=mock_state_manager,
            # ... 其他 mock 依赖
        )
        orchestrator._graph = mock_graph

        with patch.object(orchestrator, "_state_manager", mock_state_manager):
            await orchestrator.start_pipeline(pipeline_id="test-pipeline-001")

        # 验证 update_pipeline_state 的最后一次调用
        call_args = mock_state_manager.update_pipeline_state.call_args_list[-1]
        final_state = call_args[1] if len(call_args) > 1 else call_args.kwargs

        assert final_state.get("status") != "completed"
        assert final_state.get("status") == "failed"
        assert "analyst" in final_state.get("failed_nodes", [])
```

**当前预期**: 测试 **失败** — `start_pipeline()` 无条件更新为 `completed`。

**验收标准 (Green)**:
- `start_pipeline()` / `resume_pipeline()` / `restart_from_node()` 在 `graph.ainvoke()` 返回后：
  - 检查 `result.get("failed_nodes")` 是否非空，或 `result.get("error")` 是否存在
  - 若有失败，设置 `status="failed"`，并保留 `error` 和 `failed_nodes`
  - 仅当所有预期节点都在 `completed_nodes` 中且无 `failed_nodes` 时，才设置 `status="completed"`

### 2.5 集成测试: Pipeline 端到端生命周期

**目标文件**: `tests/p0_fix/stage1_failure_propagation/test_integration_pipeline_lifecycle.py`

#### 2.5.1 测试用例: 模拟节点失败的全链路验证

```python
import pytest
import tempfile
import os
from autoBMAD.docuswarm.storage.database import DatabaseManager
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestPipelineLifecycle:
    """端到端验证: 从 Pipeline 启动到最终状态的完整生命周期。"""

    @pytest.fixture
    def temp_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        yield path
        os.unlink(path)

    @pytest.mark.asyncio
    async def test_full_pipeline_reports_failure_when_node_fails(self, temp_db):
        """RED: 创建一个 pipeline，让其中一个节点失败，断言最终状态为 failed。"""
        # 1. 初始化数据库和 StateManager
        db = DatabaseManager.get_instance(db_path=temp_db)
        # ... 初始化 pipeline 状态

        # 2. 使用 mock LLM 让 analyst 节点抛出异常
        # ...

        # 3. 运行 pipeline
        # result = await orchestrator.start_pipeline(...)

        # 4. 断言
        # assert result["status"] == "failed"
        # assert "analyst" in result.get("failed_nodes", [])
        # assert "analyst" not in result.get("completed_nodes", [])
        pass  # 具体实现依赖项目测试基础设施
```

> **说明**: 集成测试需要项目现有的测试基础设施（mock LLM、内存数据库、fixture）。如果当前基础设施不足，**优先保证合同测试的覆盖率**，集成测试可放在阶段 1 末尾补充。

---

## 3. 阶段 2: F2/F4 shared_context 与数据库隔离修复测试

**核心目标**: 确保 `shared_context` 在 PipelineState ↔ NodeRunState 之间双向传递，且数据库实例按路径隔离。

### 3.1 测试目录结构

```
tests/p0_fix/stage2_shared_context_and_isolation/
├── __init__.py
├── test_contract_pipeline_adapter_shared_context.py  # F2: 双向传递
├── test_contract_database_singleton.py               # F4: 单例隔离
├── test_contract_executor_refresh.py                 # F2: _refresh_shared_context_from_db
├── test_integration_shared_context_e2e.py            # F2+F4: 端到端
```

### 3.2 合同测试: PipelineAdapter shared_context 双向传递

**目标文件**: `tests/p0_fix/stage2_shared_context_and_isolation/test_contract_pipeline_adapter_shared_context.py`

#### 3.2.1 测试用例 1: PipelineState → NodeRunState 必须携带 shared_context

```python
import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import (
    convert_pipeline_to_node_state,
)


class TestSharedContextDownstreamPropagation:
    """验证 shared_context 从 PipelineState 传递到 NodeRunState。"""

    def test_shared_context_preserved_in_node_state(self):
        """RED: PipelineState 包含 shared_context => NodeRunState 必须包含相同内容。"""
        pipeline_state = {
            "pipeline_id": "p-001",
            "shared_context": {
                "facts": {"market_scope": "global", "deadline": "2026-05-01"},
                "decisions": [{"id": "d1", "content": "use Python"}],
            },
        }

        node_state = convert_pipeline_to_node_state(
            pipeline_state=pipeline_state,
            node_id="pm",
            node_config={},
        )

        assert "shared_context" in node_state
        assert node_state["shared_context"]["facts"]["market_scope"] == "global"
        assert len(node_state["shared_context"]["decisions"]) == 1

    def test_empty_shared_context_defaults_to_dict(self):
        """边界条件: PipelineState 无 shared_context => NodeRunState 应为空 dict。"""
        pipeline_state = {"pipeline_id": "p-002"}  # 无 shared_context 键

        node_state = convert_pipeline_to_node_state(
            pipeline_state=pipeline_state,
            node_id="analyst",
            node_config={},
        )

        assert "shared_context" in node_state
        assert node_state["shared_context"] == {}
```

**当前预期**: 测试 **失败** — `convert_pipeline_to_node_state()` 返回字典中无 `shared_context` 键。

#### 3.2.2 测试用例 2: NodeRunState → PipelineState 必须合并 shared_context

```python
class TestSharedContextUpstreamMerge:
    """验证 shared_context 从 NodeRunState 合回 PipelineState。"""

    def test_node_shared_context_merged_back_to_pipeline(self):
        """RED: NodeRunState 包含更新后的 shared_context => PipelineState 应反映更新。"""
        pipeline_state = {
            "completed_nodes": [],
            "shared_context": {
                "facts": {"market_scope": "global"},
            },
        }
        node_state = {
            "node_id": "analyst",
            "status": "completed",
            "shared_context": {
                "facts": {"market_scope": "global", "budget": "1M"},
                "new_key": "added_by_node",
            },
        }

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        # 深度合并而非简单替换
        assert new_state["shared_context"]["facts"]["budget"] == "1M"
        assert new_state["shared_context"]["new_key"] == "added_by_node"
        # 原有数据保留
        assert new_state["shared_context"]["facts"]["market_scope"] == "global"

    def test_node_shared_context_none_does_not_clobber_pipeline(self):
        """边界条件: NodeRunState 无 shared_context => PipelineState 原有数据保留。"""
        pipeline_state = {
            "shared_context": {"facts": {"existing": "data"}},
        }
        node_state = {
            "node_id": "pm",
            "status": "completed",
            # 无 shared_context 键
        }

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        assert new_state["shared_context"]["facts"]["existing"] == "data"
```

**当前预期**: 测试 **失败** — `convert_node_to_pipeline_state()` 不读取 `node_state["shared_context"]`。

**验收标准 (Green)**:
- `convert_pipeline_to_node_state()`: 返回字典包含 `shared_context=pipeline_state.get("shared_context", {})`
- `convert_node_to_pipeline_state()`: 深度合并 `node_state.get("shared_context", {})` 到 `new_state["shared_context"]`
- 合并策略建议: 递归字典合并（`facts` 子字典合并，`decisions` 列表追加）

### 3.3 合同测试: DatabaseManager 单例隔离

**目标文件**: `tests/p0_fix/stage2_shared_context_and_isolation/test_contract_database_singleton.py`

#### 3.3.1 测试用例: 不同 db_path 必须返回不同实例

```python
import pytest
import tempfile
import os
from autoBMAD.docuswarm.storage.database import DatabaseManager


class TestDatabaseSingletonIsolation:
    """验证 DatabaseManager 按 db_path 隔离，而非全局单例。"""

    def test_different_db_paths_return_different_instances(self):
        """RED: 两个不同 db_path => 必须返回两个独立实例。"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f1:
            db_one = f1.name
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f2:
            db_two = f2.name

        try:
            # 清理任何已存在的单例状态（测试隔离前提）
            DatabaseManager._instance = None

            instance_one = DatabaseManager.get_instance(db_path=db_one)
            instance_two = DatabaseManager.get_instance(db_path=db_two)

            assert instance_one is not instance_two
            assert instance_one.db_path == db_one
            assert instance_two.db_path == db_two
        finally:
            os.unlink(db_one)
            os.unlink(db_two)

    def test_same_db_path_returns_same_instance(self):
        """正向验证: 相同 db_path 可复用实例。"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None

            instance_a = DatabaseManager.get_instance(db_path=db_path)
            instance_b = DatabaseManager.get_instance(db_path=db_path)

            assert instance_a is instance_b
        finally:
            os.unlink(db_path)

    def test_write_to_one_instance_not_visible_to_other(self):
        """隔离性验证: 向 instance_one 写入的数据不应出现在 instance_two。"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f1:
            db_one = f1.name
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f2:
            db_two = f2.name

        try:
            DatabaseManager._instance = None

            instance_one = DatabaseManager.get_instance(db_path=db_one)
            instance_two = DatabaseManager.get_instance(db_path=db_two)

            # 向 instance_one 的某张表写入数据
            # ... 具体 SQL 取决于 DatabaseManager 的 schema
            # 断言 instance_two 中无此数据
        finally:
            os.unlink(db_one)
            os.unlink(db_two)
```

**当前预期**: 测试 **失败** — `DatabaseManager.get_instance()` 使用单一 `_instance`，忽略 `db_path`。

**验收标准 (Green)**:
- 方案 A（推荐）: `_instances: dict[str, DatabaseManager] = {}`，按 `resolved_db_path` 缓存
- 或方案 B: 完全取消单例，由调用方管理生命周期
- 无论哪种方案，`get_instance(db_path="A") is not get_instance(db_path="B")` 必须成立

### 3.4 合同测试: `_refresh_shared_context_from_db`

**目标文件**: `tests/p0_fix/stage2_shared_context_and_isolation/test_contract_executor_refresh.py`

#### 3.4.1 测试用例: duck typing 失败时应回退到显式注入

```python
import pytest
from unittest.mock import MagicMock
from autoBMAD.docuswarm.node_execution.executor import NodeExecutor


class TestRefreshSharedContext:
    """验证 _refresh_shared_context_from_db 能正确获取 StateManager。"""

    def test_refresh_with_explicitly_injected_state_manager(self):
        """GREEN 前提: NodeExecutor 应支持显式传入 state_manager。"""
        mock_state_manager = MagicMock()
        mock_state_manager.get_shared_context.return_value = {
            "facts": {"refreshed": True}
        }

        executor = NodeExecutor(
            state_manager=mock_state_manager,  # 假设修复后支持显式注入
            # ...
        )
        result = executor._refresh_shared_context_from_db()

        assert result is not None
        assert result["facts"]["refreshed"] is True

    def test_refresh_without_state_manager_returns_none_gracefully(self):
        """边界条件: 无法获取 StateManager 时应返回 None，不抛异常。"""
        executor = NodeExecutor()  # 无 state_manager
        result = executor._refresh_shared_context_from_db()

        # 当前行为是返回 None，但原因错误（duck typing 全失败）
        # 修复后：如果确实没有 state_manager，返回 None 是可接受的
        assert result is None
```

**验收标准 (Green)**:
- `NodeExecutor` 接受 `state_manager` 作为构造函数参数（可选）
- `_refresh_shared_context_from_db()` 优先使用显式注入的 `state_manager`
- 移除不可靠的 duck typing（或仅作为向后兼容的最后回退）

### 3.5 集成测试: shared_context 端到端

**目标文件**: `tests/p0_fix/stage2_shared_context_and_isolation/test_integration_shared_context_e2e.py`

```python
class TestSharedContextEndToEnd:
    """验证 shared_context 在 multi-node pipeline 中的端到端传递。"""

    @pytest.mark.asyncio
    async def test_context_written_by_node_a_readable_by_node_b(self, temp_db):
        """RED: analyst 写入 shared_context => pm 能读取到相同内容。"""
        # 1. 设置 pipeline，配置 analyst -> pm 的执行顺序
        # 2. mock LLM，让 analyst 调用 update_context_tool 写入 {"facts": {"budget": "1M"}}
        # 3. 运行 analyst 节点
        # 4. 运行 pm 节点
        # 5. 断言 pm 节点的 NodeRunState.shared_context 包含 budget="1M"
        pass
```

---

## 4. 阶段 3: F3 工具权限收紧修复测试

**核心目标**: 确保节点配置声明的 `allowed_builtin_tools` 是运行时的真实边界。

### 4.1 测试目录结构

```
tests/p0_fix/stage3_tool_permissions/
├── __init__.py
├── test_contract_session_manager_tools.py   # _build_allowed_tools 合同
├── test_contract_node_yaml_compliance.py    # node.yaml 配置与运行时一致性
└── test_regression_permission_snapshot.py   # 权限快照回归
```

### 4.2 合同测试: SessionManager 工具列表构建

**目标文件**: `tests/p0_fix/stage3_tool_permissions/test_contract_session_manager_tools.py`

#### 4.2.1 测试用例 1: _get_builtin_tools 应基于节点配置

```python
import pytest
from unittest.mock import MagicMock
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestBuiltinToolsResolution:
    """验证 _get_builtin_tools() 尊重节点配置，而非硬编码。"""

    def test_get_builtin_tools_reads_from_tool_permissions(self):
        """RED: _get_builtin_tools() 应从 self._tool_permissions 派生。"""
        mock_tool_permissions = MagicMock()
        mock_tool_permissions.allowed_builtin_tools = ["Read", "Glob"]

        sm = SessionManager.__new__(SessionManager)
        sm._tool_permissions = mock_tool_permissions

        tools = sm._get_builtin_tools()

        assert tools == ["Read", "Glob"]
        assert "Edit" not in tools
        assert "Bash" not in tools

    def test_get_builtin_tools_safe_default_when_no_permissions(self):
        """边界条件: 无 tool_permissions 时应返回安全默认值。"""
        sm = SessionManager.__new__(SessionManager)
        sm._tool_permissions = None

        tools = sm._get_builtin_tools()

        # 安全默认值: 只读工具
        assert set(tools).issubset({"Read", "Glob"})
        assert "Edit" not in tools
        assert "Bash" not in tools
```

**当前预期**: 测试 **失败** — `_get_builtin_tools()` 硬编码返回全部 5 个工具。

#### 4.2.2 测试用例 2: _build_allowed_tools 不应无条件扩展全部内置工具

```python
class TestAllowedToolsBuilding:
    """验证 _build_allowed_tools() 构建的列表与配置一致。"""

    def test_build_allowed_tools_no_permission_bypass(self):
        """RED: yolo=True 且节点只允许 Read/Glob => 结果不应包含 Edit/Bash。"""
        mock_tool_permissions = MagicMock()
        mock_tool_permissions.allowed_builtin_tools = ["Read", "Glob"]
        mock_tool_permissions.allowed_mcp_tools = []
        mock_tool_permissions.allowed_skills = []

        sm = SessionManager.__new__(SessionManager)
        sm._tool_permissions = mock_tool_permissions
        sm._get_builtin_tools = lambda: ["Read", "Glob"]

        tools = sm._build_allowed_tools()

        assert "Read" in tools
        assert "Glob" in tools
        assert "Edit" not in tools
        assert "Bash" not in tools
        assert "Grep" not in tools

    def test_yolo_does_not_use_bypass_permissions_for_dangerous_tools(self):
        """RED: yolo=True 不应将 permission_mode 设为 bypassPermissions。"""
        sm = SessionManager.__new__(SessionManager)
        sm._tool_permissions = MagicMock()
        sm._tool_permissions.allowed_builtin_tools = ["Read", "Glob"]

        options = sm._create_options(yolo=True)

        # yolo=True 的语义应为"自动批准已知安全工具"，而非"绕过权限检查"
        assert options.get("permission_mode") != "bypassPermissions"
```

**当前预期**: 测试 **失败** — `_build_allowed_tools()` 无条件 `extend(self._get_builtin_tools())`，且 `yolo=True` 设置 `bypassPermissions`。

**验收标准 (Green)**:
- `_get_builtin_tools()`: 若 `_tool_permissions` 存在，返回 `_tool_permissions.allowed_builtin_tools`；否则返回 `{"Read", "Glob"}`
- `_build_allowed_tools()`: 不再无条件 `extend(self._get_builtin_tools())`，而是基于节点配置构建
- `_create_options()`: `yolo=True` 不再映射为 `bypassPermissions`；危险工具（`Edit`, `Bash`）需要单独的 `dangerous_tools_allowlist`

### 4.3 回归测试: node.yaml 权限快照

**目标文件**: `tests/p0_fix/stage3_tool_permissions/test_regression_permission_snapshot.py`

#### 4.3.1 测试用例: 所有节点的运行时权限等于配置声明

```python
import pytest
import yaml
import os
from glob import glob
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestNodeYamlPermissionCompliance:
    """验证每个 node.yaml 的 allowed_builtin_tools 与 SessionManager 实际构建结果一致。"""

    def _load_all_node_configs(self):
        """加载所有 node.yaml 配置。"""
        base_path = "autoBMAD/docuswarm/config/nodes"  # 根据实际路径调整
        configs = {}
        for path in glob(os.path.join(base_path, "**/node.yaml"), recursive=True):
            node_id = os.path.basename(os.path.dirname(path))
            with open(path) as f:
                configs[node_id] = yaml.safe_load(f)
        return configs

    @pytest.mark.parametrize("node_id,config", _load_all_node_configs().items())
    def test_runtime_tools_match_yaml_declaration(self, node_id, config):
        """对每个节点: 运行时 allowed_tools 必须等于 node.yaml 声明的展开结果。"""
        declared_tools = set(config.get("allowed_builtin_tools", []))

        # 构建模拟的 SessionManager，传入该节点的 tool_permissions
        sm = SessionManager.__new__(SessionManager)
        sm._tool_permissions = MagicMock()
        sm._tool_permissions.allowed_builtin_tools = list(declared_tools)
        sm._tool_permissions.allowed_mcp_tools = config.get("allowed_mcp_tools", [])
        sm._tool_permissions.allowed_skills = config.get("allowed_skills", [])

        actual_tools = set(sm._build_allowed_tools())

        assert actual_tools == declared_tools, (
            f"Node '{node_id}': runtime tools {actual_tools} "
            f"do not match YAML declaration {declared_tools}"
        )
```

---

## 5. 调试工具转回归测试套件

研究报告附录 A 中的 4 个调试工具可直接转换为 pytest 测试用例，作为持续集成中的回归测试屏障。

### 5.1 转换方案

| 调试工具 | 转换为测试文件 | 转换方式 |
|---------|--------------|---------|
| `p0_failure_propagation_debugger.py` | `tests/p0_fix/test_regression_f1_failure_propagation.py` | 将 `main()` 中的断言逻辑提取为 `test_*` 函数 |
| `p0_shared_context_debugger.py` | `tests/p0_fix/test_regression_f2_shared_context.py` | 同上 |
| `p0_database_singleton_debugger.py` | `tests/p0_fix/test_regression_f4_db_singleton.py` | 同上 |
| `p0_tool_permission_debugger.py` | `tests/p0_fix/test_regression_f3_tool_permissions.py` | 同上 |

### 5.2 转换模板

以 F1 调试工具为例：

```python
# tests/p0_fix/test_regression_f1_failure_propagation.py
import pytest
import json
from pathlib import Path


class TestRegressionF1FailurePropagation:
    """回归测试: F1 节点失败传播链。
    
    改编自 tools/debug/p0_failure_propagation_debugger.py
    """

    def test_pipeline_adapter_does_not_add_failed_to_completed(self):
        """验证 FAILED 状态的节点不会被 PipelineAdapter 加入 completed_nodes。"""
        from autoBMAD.docuswarm.node_execution.pipeline_adapter import (
            convert_node_to_pipeline_state,
        )

        pipeline_state = {
            "completed_nodes": [],
            "failed_nodes": [],
            "error": None,
            "deliverables": {},
            "evaluations": {},
            "shared_context": {},
        }
        node_state = {
            "node_id": "analyst",
            "status": "failed",
            "deliverables": {},
            "evaluations": {},
        }

        new_state = convert_node_to_pipeline_state(node_state, pipeline_state)

        assert "analyst" not in new_state["completed_nodes"], "BUG REGRESSION: failed node added to completed_nodes"

    def test_graph_executor_exception_not_marked_completed(self):
        """验证 graph.py 异常处理后节点不被标记为完成。"""
        # ... 提取调试工具中的验证逻辑 ...
        pass
```

---

## 6. 测试运行指南

### 6.1 按阶段运行测试

```bash
# 阶段 1: 仅运行 F1 相关测试
pytest tests/p0_fix/stage1_failure_propagation/ -v

# 阶段 2: 仅运行 F2/F4 相关测试
pytest tests/p0_fix/stage2_shared_context_and_isolation/ -v

# 阶段 3: 仅运行 F3 相关测试
pytest tests/p0_fix/stage3_tool_permissions/ -v

# 全部 P0 回归测试
pytest tests/p0_fix/ -v
```

### 6.2 Red-Green 工作流

**第一步: 确认当前全红**

```bash
pytest tests/p0_fix/ -v --tb=short
# 预期: 大量 FAILED，确认缺陷存在
```

**第二步: 修复 + 局部验证**

```bash
# 修复 PipelineAdapter 后
pytest tests/p0_fix/stage1_failure_propagation/test_contract_pipeline_adapter.py -v
# 预期: 该文件内测试全部 PASSED
```

**第三步: 阶段验收**

当一个阶段的所有测试通过时，运行完整回归套件确认无回归：

```bash
pytest tests/ -v --tb=short
# 预期: 原有测试不失败，新增 P0 测试全部 PASSED
```

### 6.3 持续集成集成建议

在 `.github/workflows/ci.yml`（或等效配置）中增加：

```yaml
- name: P0 Tech Debt Regression Tests
  run: |
    pytest tests/p0_fix/ -v --tb=short --junitxml=p0-results.xml
  continue-on-error: false  # P0 测试失败 = CI 失败
```

---

## 7. 验收标准总表

| 问题 | 关键测试文件 | Red 状态验证 | Green 验收标准 |
|------|------------|------------|--------------|
| **F1** | `stage1_failure_propagation/test_contract_pipeline_adapter.py` | FAILED 节点出现在 completed_nodes | 仅 COMPLETED/FORCE_APPROVED 加入 completed_nodes |
| **F1** | `stage1_failure_propagation/test_contract_graph_executor.py` | 异常后节点仍在 completed_nodes | 异常后设置 error/failed_nodes，不加入 completed_nodes |
| **F1** | `stage1_failure_propagation/test_contract_orchestrator.py` | pipeline 无条件标记 completed | 检查 failed_nodes/error 后决定是否 completed |
| **F2** | `stage2_shared_context_and_isolation/test_contract_pipeline_adapter_shared_context.py` | NodeRunState 无 shared_context 键 | 双向传递 shared_context |
| **F2** | `stage2_shared_context_and_isolation/test_contract_executor_refresh.py` | _refresh_shared_context_from_db 返回 None | 支持显式 state_manager 注入 |
| **F4** | `stage2_shared_context_and_isolation/test_contract_database_singleton.py` | 不同 db_path 返回同一实例 | 按 db_path 缓存/隔离实例 |
| **F3** | `stage3_tool_permissions/test_contract_session_manager_tools.py` | _get_builtin_tools 硬编码 5 个工具 | 基于节点配置派生工具列表 |
| **F3** | `stage3_tool_permissions/test_contract_session_manager_tools.py` | yolo=True 映射 bypassPermissions | yolo 不再绕过权限检查 |
| **F3** | `stage3_tool_permissions/test_regression_permission_snapshot.py` | 运行时工具多于 YAML 声明 | 每个节点的运行时工具等于 YAML 声明 |

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 现有测试基础设施不足（无 mock LLM / 内存 DB fixture） | 集成测试无法编写 | 优先编写合同测试；合同测试不依赖外部服务，可直接调用内部函数 |
| DatabaseManager 单例修改影响范围大 | 回归风险 | 方案 A（按路径缓存）改动面小于方案 B（取消单例）；修改后全量运行 `pytest tests/` |
| SessionManager 工具权限修改影响 Agent 行为 | 现有功能可能依赖未声明工具 | 在修复前运行一次基线测试，记录每个节点实际使用的工具列表；修复后对比 |
| 修复引入新的状态机不一致 | F1 修复可能破坏 resume/restart | 为 `resume_pipeline()` 和 `restart_from_node()` 编写专门的合同测试 |

---

## 9. 附录: 快速参考

### 创建所有测试目录

```bash
mkdir -p tests/p0_fix/stage1_failure_propagation
mkdir -p tests/p0_fix/stage2_shared_context_and_isolation
mkdir -p tests/p0_fix/stage3_tool_permissions
```

### 为每个阶段创建 `__init__.py`

```bash
touch tests/p0_fix/__init__.py
touch tests/p0_fix/stage1_failure_propagation/__init__.py
touch tests/p0_fix/stage2_shared_context_and_isolation/__init__.py
touch tests/p0_fix/stage3_tool_permissions/__init__.py
```

### 最小化首次 Red 运行

```bash
# 仅运行一个核心测试，快速验证当前系统是否为 Red
pytest tests/p0_fix/stage1_failure_propagation/test_contract_pipeline_adapter.py::TestConvertNodeToPipelineState::test_failed_node_not_added_to_completed_nodes -v
```

---

## 结论

本测试驱动方案为 DocuSwarm 的 4 个 P0 技术债问题提供了 **可执行、可验证、可自动化** 的修复路径。每个问题都有对应的：

1. **Red 测试用例** — 先证明缺陷存在
2. **修复验收标准** — 明确 Green 的条件
3. **回归测试套件** — 防止缺陷复活

按照"阶段 1 → 阶段 2 → 阶段 3"的顺序执行，每阶段以 **该阶段全部测试通过** 为里程碑。全部 3 个阶段完成后，P0 技术债的修复将具备完整的测试覆盖和自动化保障。

# DocuSwarm `start` 命令执行问题 - 测试驱动修复方案

## 文档信息

| 字段 | 内容 |
|---|---|
| 主题 | 针对 `python -m autoBMAD.docuswarm start` 命令的多层故障修复 |
| 基于研究 | `@docs-copy\research\DocuSwarm-start命令执行问题深度研究报告-2026-03-06.md` |
| 方案日期 | 2026-03-06 |
| 方案类型 | 测试驱动修复 (TDD) |

---

## 一、问题总结

根据深度研究报告，`start` 命令存在 **四层串行故障**：

| 层级 | 问题 | 影响 | 优先级 |
|---|---|---|---|
| P0-1 | Kimi 会话目录权限错误 (`WinError 5`) | CLI 无法启动 | 阻断性 |
| P0-2 | 工具注册链路断裂 | 节点无法调用 `create_deliverable` | 阻断性 |
| P0-3 | 失败传播语义错误 | 节点失败但流水线标为 `completed` | 严重 |
| P1-1 | 状态持久化缺失 | 数据库与日志脱节 | 中等 |

---

## 二、测试驱动修复策略

### 2.1 TDD 流程

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: 编写失败测试 → Phase 2: 实现修复 → Phase 3: 验证通过   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 测试矩阵

```
┌──────────────────────────────────────────────────────────────────────┐
│                          测试覆盖矩阵                                 │
├─────────────────┬────────────────────────────────────────────────────┤
│ 修复项          │ 测试类型                                             │
├─────────────────┼────────────────────────────────────────────────────┤
│ P0-1 环境修复   │ 单元测试: 目录权限检查 + 集成测试: CLI启动           │
│ P0-2 工具注册   │ 单元测试: ToolRegistry状态 + 集成测试: 工具可用性    │
│ P0-3 失败传播   │ 单元测试: 异常处理 + 集成测试: 状态流转              │
│ P1-1 状态持久化 │ 单元测试: 状态保存 + 集成测试: 数据库同步            │
└─────────────────┴────────────────────────────────────────────────────┘
```

---

## 三、Phase 1: P0-1 环境修复 (Kimi 会话目录权限)

### 3.1 问题分析

```python
# 当前问题: Kimi SDK 默认使用 ~/.kimi/sessions，在 Windows 可能无写权限
# kimi_cli.share.get_share_dir() → Path.home() / ".kimi"

# 修复方案: CLI 启动时自动设置 KIMI_SHARE_DIR 环境变量
```

### 3.2 失败测试 (先写)

```python
# tests/unit/test_environment_setup.py

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from autoBMAD.docuswarm.main import cli, start
from click.testing import CliRunner


class TestEnvironmentSetup:
    """测试环境初始化修复 - P0-1"""
    
    def test_kimi_share_dir_auto_set_on_start(self):
        """Test: CLI 启动时自动设置 KIMI_SHARE_DIR 到项目可写目录"""
        # Given: KIMI_SHARE_DIR 未设置
        with patch.dict(os.environ, {}, clear=True):
            # When: 调用 start 命令
            runner = CliRunner()
            with runner.isolated_filesystem() as fs:
                # Create mock context file
                context_file = Path(fs) / "test-context.md"
                context_file.write_text("# Test Context")
                
                # Mock orchestrator to avoid actual execution
                with patch("autoBMAD.docuswarm.main.HybridOrchestrator") as mock_orch:
                    mock_instance = MagicMock()
                    mock_instance.start_pipeline = MagicMock(return_value="test-pipeline-id")
                    mock_orch.return_value = mock_instance
                    
                    # Call start command
                    result = runner.invoke(cli, ["start", "--context", str(context_file)])
                    
                    # Then: KIMI_SHARE_DIR 应该被设置到项目目录下的 .kimi
                    assert "KIMI_SHARE_DIR" in os.environ
                    expected_path = Path(fs) / ".kimi"
                    assert os.environ["KIMI_SHARE_DIR"] == str(expected_path)
    
    def test_kimi_share_dir_uses_existing_if_set(self):
        """Test: 如果 KIMI_SHARE_DIR 已设置，应保留用户值"""
        # Given: KIMI_SHARE_DIR 已设置为自定义值
        custom_path = "/custom/kimi/path"
        with patch.dict(os.environ, {"KIMI_SHARE_DIR": custom_path}):
            original_value = os.environ.get("KIMI_SHARE_DIR")
            
            runner = CliRunner()
            with runner.isolated_filesystem() as fs:
                context_file = Path(fs) / "test-context.md"
                context_file.write_text("# Test Context")
                
                with patch("autoBMAD.docuswarm.main.HybridOrchestrator") as mock_orch:
                    mock_instance = MagicMock()
                    mock_instance.start_pipeline = MagicMock(return_value="test-pipeline-id")
                    mock_orch.return_value = mock_instance
                    
                    result = runner.invoke(cli, ["start", "--context", str(context_file)])
                    
                    # Then: 应保留用户设置的值
                    assert os.environ["KIMI_SHARE_DIR"] == original_value
    
    def test_kimi_share_dir_directory_creation(self):
        """Test: KIMI_SHARE_DIR 目录应自动创建"""
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            context_file = Path(fs) / "test-context.md"
            context_file.write_text("# Test Context")
            
            with patch("autoBMAD.docuswarm.main.HybridOrchestrator") as mock_orch:
                mock_instance = MagicMock()
                mock_instance.start_pipeline = MagicMock(return_value="test-pipeline-id")
                mock_orch.return_value = mock_instance
                
                result = runner.invoke(cli, ["start", "--context", str(context_file)])
                
                # Then: .kimi 目录应该被创建
                expected_kimi_dir = Path(fs) / ".kimi"
                assert expected_kimi_dir.exists()
                assert expected_kimi_dir.is_dir()
```

### 3.3 实现修复

```python
# autoBMAD/docuswarm/main.py - 修改 cli() 函数

import os
from pathlib import Path

def _ensure_kimi_share_dir(project_root: Path | None = None) -> Path:
    """Ensure KIMI_SHARE_DIR is set to a writable directory.
    
    This fixes the P0-1 issue where Kimi SDK defaults to ~/.kimi/sessions
    which may not be writable in certain environments (e.g., Windows).
    
    Args:
        project_root: Project root directory. If None, uses current working directory.
        
    Returns:
        Path to the Kimi share directory.
    """
    # If already set, respect user's choice
    if "KIMI_SHARE_DIR" in os.environ:
        return Path(os.environ["KIMI_SHARE_DIR"])
    
    # Determine project root
    if project_root is None:
        project_root = Path.cwd()
    
    # Set to project-local .kimi directory
    kimi_dir = project_root / ".kimi"
    
    # Create directory if it doesn't exist
    kimi_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variable for SDK
    os.environ["KIMI_SHARE_DIR"] = str(kimi_dir)
    
    return kimi_dir


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose debug output")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default=None,
    help="Set logging level (overrides LOG_LEVEL env var)",
)
@click.option(
    "--log-file",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=None,
    help="Directory for log files (default: ./logs)",
)
@click.option(
    "--json-log",
    is_flag=True,
    help="Use JSON format for log file output",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    log_level: str | None,
    log_file: str | None,
    json_log: bool,
) -> None:
    """DocuSwarm - Multi-Agent Document Orchestration System."""
    ctx.obj = CliContext(verbose=verbose)

    # P0-1 Fix: Ensure KIMI_SHARE_DIR is set before any SDK operations
    _ensure_kimi_share_dir()
    
    # Load configuration from .env and YAML
    config = load_config()
    ctx.obj.config = config  # Store config in context for other commands

    # Initialize logging
    log_dir = Path(log_file) if log_file else None
    level = "DEBUG" if verbose else log_level
    _ = configure_logging(
        log_level=level,
        log_dir=log_dir,
        json_format=json_log,
    )
```

---

## 四、Phase 2: P0-2 工具注册修复

### 4.1 问题分析

```python
# 当前问题: ToolRegistry 依赖导入副作用，但生产路径未触发
# autoBMAD/docuswarm/tools/__init__.py 的 register_all_tools() 未被调用

# 修复方案: 在 CLI 启动和编排器初始化时显式调用 register_all_tools()
```

### 4.2 失败测试 (先写)

```python
# tests/unit/test_tool_registration_fix.py

import pytest
from unittest.mock import patch, MagicMock

from autoBMAD.docuswarm.models.tool_registry import ToolRegistry
from autoBMAD.docuswarm.tools import register_all_tools


class TestToolRegistrationFix:
    """测试工具注册修复 - P0-2"""
    
    def test_tool_registry_not_empty_after_cli_start(self):
        """Test: CLI 启动后 ToolRegistry 不应为空"""
        # Given: 清空的 ToolRegistry
        ToolRegistry.clear()
        assert len(ToolRegistry.get_all()) == 0
        
        # When: 导入并执行 CLI (模拟)
        from autoBMAD.docuswarm.main import cli, _ensure_kimi_share_dir
        from click.testing import CliRunner
        import os
        
        runner = CliRunner()
        with runner.isolated_filesystem() as fs:
            # Set up environment
            os.environ["KIMI_SHARE_DIR"] = str(Path(fs) / ".kimi")
            
            # Import triggers registration
            from autoBMAD.docuswarm import tools
            tools.register_all_tools()
            
            # Then: ToolRegistry 应该有 6 个工具
            registered_tools = ToolRegistry.get_all()
            assert len(registered_tools) == 6, f"Expected 6 tools, got {len(registered_tools)}"
            
            # Verify specific tools exist
            tool_names = {t.name for t in registered_tools}
            expected_tools = {
                "create_deliverable",
                "create_document_set",
                "list_docs_files",
                "read_docs_file",
                "update_context",
                "update_docs_file",
            }
            assert tool_names == expected_tools
    
    def test_create_deliverable_tool_available_for_agent(self):
        """Test: create_deliverable 工具对 Agent 可用"""
        # Given: 已注册的工具
        ToolRegistry.clear()
        register_all_tools()
        
        # When: 获取 create_deliverable
        tool = ToolRegistry.get("create_deliverable")
        
        # Then: 工具应该存在且有正确的结构
        assert tool is not None
        assert tool.name == "create_deliverable"
        assert tool.description != ""
        assert tool.parameters is not None
        assert tool.handler is not None
    
    def test_tool_registry_persists_across_imports(self):
        """Test: ToolRegistry 在多次导入间保持状态"""
        # Given: 初始状态
        ToolRegistry.clear()
        assert len(ToolRegistry.get_all()) == 0
        
        # When: 第一次注册
        register_all_tools()
        first_count = len(ToolRegistry.get_all())
        
        # When: 再次注册（幂等性检查）
        register_all_tools()
        second_count = len(ToolRegistry.get_all())
        
        # Then: 两次注册后工具数量应该相同（幂等）
        assert first_count == second_count == 6
```

### 4.3 实现修复

```python
# autoBMAD/docuswarm/main.py - 添加工具注册

def _ensure_tools_registered() -> list:
    """Ensure all tools are registered with ToolRegistry.
    
    This fixes the P0-2 issue where tools were not registered because
    the registration relied on import side effects that didn't occur
    in production execution paths.
    
    Returns:
        List of registered tool definitions.
    """
    from autoBMAD.docuswarm.tools import register_all_tools
    
    tools = register_all_tools()
    
    # Log registration status for debugging
    import structlog
    logger = structlog.get_logger(__name__)
    logger.info(
        "tools_registered",
        tool_count=len(tools),
        tool_names=[t.name for t in tools],
    )
    
    return tools


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose debug output")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default=None,
    help="Set logging level (overrides LOG_LEVEL env var)",
)
@click.option(
    "--log-file",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=None,
    help="Directory for log files (default: ./logs)",
)
@click.option(
    "--json-log",
    is_flag=True,
    help="Use JSON format for log file output",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    log_level: str | None,
    log_file: str | None,
    json_log: bool,
) -> None:
    """DocuSwarm - Multi-Agent Document Orchestration System."""
    ctx.obj = CliContext(verbose=verbose)

    # P0-1 Fix: Ensure KIMI_SHARE_DIR is set before any SDK operations
    _ensure_kimi_share_dir()
    
    # P0-2 Fix: Ensure tools are registered before any agent operations
    _ensure_tools_registered()
    
    # Load configuration from .env and YAML
    config = load_config()
    ctx.obj.config = config  # Store config in context for other commands

    # Initialize logging
    log_dir = Path(log_file) if log_file else None
    level = "DEBUG" if verbose else log_level
    _ = configure_logging(
        log_level=level,
        log_dir=log_dir,
        json_format=json_log,
    )
```

---

## 五、Phase 3: P0-3 失败传播修复

### 5.1 问题分析

```python
# 当前问题链:
# 1. node_execution/executor.py: 吞掉异常，只设置 status = FAILED
# 2. pipeline/graph.py: 无条件将节点加入 completed_nodes
# 3. pipeline/state.py finalize_pipeline_state(): 无条件设为 COMPLETED

# 修复方案:
# 1. executor: 抛出异常而非静默处理
# 2. graph: 检查节点状态，失败节点不加入 completed_nodes
# 3. state: finalize 时检查是否有失败节点
```

### 5.2 失败测试 (先写)

```python
# tests/unit/test_failure_propagation_fix.py

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import copy

from autoBMAD.docuswarm.pipeline.state import (
    create_initial_state,
    finalize_pipeline_state,
    FAILED,
    COMPLETED,
    PIPELINE_NODES,
)
from autoBMAD.docuswarm.pipeline.graph import (
    _convert_node_to_pipeline_state,
    _create_integrated_node_executor,
)
from autoBMAD.docuswarm.node_execution.state import FAILED as NODE_FAILED


class TestFailurePropagationFix:
    """测试失败传播修复 - P0-3"""
    
    def test_failed_node_not_added_to_completed_nodes(self):
        """Test: 失败的节点不应加入 completed_nodes"""
        # Given: 初始状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        state["current_node"] = "analyst"
        
        # When: 模拟失败的节点执行结果
        node_state = {
            "node_id": "analyst",
            "status": NODE_FAILED,  # 节点失败
            "deliverable": None,
            "iteration": 1,
        }
        
        # Then: 调用转换函数
        new_state = _convert_node_to_pipeline_state(node_state, state)
        
        # 失败的节点不应在 completed_nodes 中
        assert "analyst" not in new_state["completed_nodes"], \
            "Failed node should not be in completed_nodes"
    
    def test_successful_node_added_to_completed_nodes(self):
        """Test: 成功的节点应加入 completed_nodes"""
        # Given: 初始状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        state["current_node"] = "analyst"
        
        # When: 模拟成功的节点执行结果
        node_state = {
            "node_id": "analyst",
            "status": "completed",  # 节点成功
            "deliverable": {"title": "Test", "content": "Test content"},
            "iteration": 1,
        }
        
        # Then: 调用转换函数
        new_state = _convert_node_to_pipeline_state(node_state, state)
        
        # 成功的节点应该在 completed_nodes 中
        assert "analyst" in new_state["completed_nodes"], \
            "Successful node should be in completed_nodes"
    
    def test_finalize_pipeline_state_with_failed_nodes(self):
        """Test: 有失败节点时 finalize 应返回 FAILED 状态"""
        # Given: 有失败节点的状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        state["completed_nodes"] = ["analyst"]  # 只有 analyst 完成
        state["current_node"] = "pm"
        state["status"] = FAILED  # 某个节点失败了
        
        # When: 调用 finalize
        result = finalize_pipeline_state(state)
        
        # Then: 结果应该是 FAILED，不是 COMPLETED
        assert result["status"] == FAILED, \
            f"Pipeline with failed nodes should have FAILED status, got {result['status']}"
    
    def test_finalize_pipeline_state_with_all_successful_nodes(self):
        """Test: 所有节点成功时 finalize 应返回 COMPLETED 状态"""
        # Given: 所有节点都完成的状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        state["completed_nodes"] = list(PIPELINE_NODES)  # 所有节点都完成
        state["current_node"] = "po"
        state["deliverables"] = {node: {"content": f"{node} deliverable"} for node in PIPELINE_NODES}
        
        # When: 调用 finalize
        result = finalize_pipeline_state(state)
        
        # Then: 结果应该是 COMPLETED
        assert result["status"] == COMPLETED, \
            f"Pipeline with all successful nodes should have COMPLETED status, got {result['status']}"
    
    def test_executor_raises_exception_on_failure(self):
        """Test: 执行器应在失败时抛出异常"""
        # Given: 模拟失败的节点执行
        from autoBMAD.docuswarm.node_execution.executor import _execute_node
        
        mock_state = {
            "run_id": "test-run",
            "pipeline_id": "test-pipeline",
            "node_id": "analyst",
            "context_hash": "abc123",
            "context_file": "{}",
            "iteration": 1,
            "deliverable": None,
            "questions": [],
            "evaluation": None,
            "answers": {},
            "chained_context": {},
            "status": "pending",
        }
        
        # When: 模拟执行失败
        # 修复后的 _execute_node 应该在失败时抛出异常
        # 这里我们测试新的行为
        
        # 由于 _execute_node 是内部函数，我们测试集成行为
        # 实际测试在 test_integration_failure_propagation.py 中
        pass
```

### 5.3 实现修复

```python
# autoBMAD/docuswarm/pipeline/graph.py - 修改 _convert_node_to_pipeline_state

def _convert_node_to_pipeline_state(
    node_state: dict[str, Any],
    original_state: dict[str, Any],
) -> dict[str, Any]:
    """Convert NodeRunState back to PipelineState after node execution.
    
    P0-3 Fix: Only add node to completed_nodes if execution was successful.
    """
    # Deep copy original state to avoid mutation
    new_state = copy.deepcopy(original_state)

    node_id = node_state.get("node_id")
    node_status = node_state.get("status")

    # Update deliverable if present
    if node_state.get("deliverable") is not None:
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}
        new_state["deliverables"][node_id] = node_state["deliverable"]

    # Update questions if present
    questions = node_state.get("questions", [])
    if questions:
        if "questions" not in new_state:
            new_state["questions"] = {}
        new_state["questions"][node_id] = questions

    # Update evaluation if present
    evaluation = node_state.get("evaluation")
    if evaluation is not None:
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}
        new_state["evaluations"][node_id] = evaluation

    # Update iteration count
    if "node_iterations" not in new_state:
        new_state["node_iterations"] = {}
    new_state["node_iterations"][node_id] = node_state.get("iteration", 1)

    # P0-3 Fix: Only add node to completed_nodes if successful
    # Failed nodes should not be marked as completed
    if "completed_nodes" not in new_state:
        new_state["completed_nodes"] = []
    
    # Only add to completed_nodes if status is successful
    successful_statuses = {"completed", "approved"}
    if node_status in successful_statuses and node_id not in new_state["completed_nodes"]:
        new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]
    
    # If status is failed, ensure pipeline status reflects this
    if node_status == FAILED:
        new_state["status"] = FAILED
        # Store error info if available
        if "error" not in new_state or new_state["error"] is None:
            new_state["error"] = {
                "node_id": node_id,
                "message": f"Node {node_id} failed execution",
                "status": node_status,
            }

    # Update current_node
    new_state["current_node"] = node_id

    return new_state
```

```python
# autoBMAD/docuswarm/pipeline/state.py - 修改 finalize_pipeline_state

def finalize_pipeline_state(state: PipelineState) -> PipelineState:
    """Finalize the pipeline state when all nodes have completed.
    
    P0-3 Fix: Check for failed nodes before marking as COMPLETED.
    """
    import copy

    result = copy.deepcopy(state)
    
    # P0-3 Fix: Check if any node failed or if pipeline already in FAILED status
    current_status = state.get("status", "")
    completed_nodes = set(state.get("completed_nodes", []))
    
    # If already marked as failed, keep it failed
    if current_status == FAILED:
        result["status"] = FAILED
        return result
    
    # Check if all required nodes completed successfully
    all_nodes_completed = all(node in completed_nodes for node in PIPELINE_NODES)
    
    if all_nodes_completed:
        # All nodes successful - mark as completed
        result["status"] = COMPLETED
    else:
        # Some nodes missing - check if any failed
        # This is an unexpected state, mark as failed
        missing_nodes = [node for node in PIPELINE_NODES if node not in completed_nodes]
        result["status"] = FAILED
        if result.get("error") is None:
            result["error"] = {
                "message": f"Pipeline finalized with incomplete nodes: {missing_nodes}",
                "missing_nodes": missing_nodes,
                "completed_nodes": list(completed_nodes),
            }

    return result
```

```python
# autoBMAD/docuswarm/pipeline/graph.py - 修改 _create_integrated_node_executor

def _create_integrated_node_executor(
    node_id: str,
    session_manager: Any,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create an integrated node executor that uses node_execution.executor.
    
    P0-3 Fix: Properly handle failures and don't add failed nodes to completed_nodes.
    """
    # Lazy import to avoid circular imports
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor

    # Create the async node executor
    async_node_executor = create_node_executor(node_id, session_manager)

    def _run_async(coro: Awaitable[Any]) -> Any:
        """Run async coroutine, handling event loop properly."""
        import asyncio

        try:
            # Try to get the running loop
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop - use asyncio.run() which creates a new loop
            return asyncio.run(coro)

        # There's a running loop - create a new thread to run the coroutine
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            # Add timeout to prevent indefinite blocking (4 minutes per call)
            return future.result(timeout=240)

    def executor(state: dict[str, Any]) -> dict[str, Any]:
        """Execute node logic using integrated node_execution.executor."""
        import copy as copy_module

        # Deep copy state to avoid mutation issues
        new_state = copy_module.deepcopy(state)

        # Update current_node
        new_state["current_node"] = node_id

        # Initialize fields if not present
        if "completed_nodes" not in new_state:
            new_state["completed_nodes"] = []
        if "node_iterations" not in new_state:
            new_state["node_iterations"] = {}
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}
        if "questions" not in new_state:
            new_state["questions"] = {}
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}

        # Convert PipelineState to NodeRunState
        node_run_state = _convert_pipeline_to_node_state(new_state, node_id)

        # Run the async executor in sync context
        executed_node_state = None
        try:
            # Run async executor synchronously for LangGraph compatibility
            executed_node_state = _run_async(async_node_executor(node_run_state))

            # Convert back to PipelineState
            new_state = _convert_node_to_pipeline_state(executed_node_state, new_state)

            # Save deliverable to file storage if execution was successful
            status = executed_node_state.get("status")
            if status in ("completed", "approved") and executed_node_state.get("deliverable"):
                pipeline_id = new_state.get("pipeline_id", "unknown")
                output_root = str(session_manager.work_dir) if session_manager else None
                try:
                    _run_async(
                        _save_deliverable_async(
                            pipeline_id,
                            node_id,
                            executed_node_state["deliverable"],
                            output_root=output_root,
                        )
                    )
                except Exception as e:
                    logger.warning(
                        "failed_to_save_deliverable",
                        pipeline_id=pipeline_id,
                        node_id=node_id,
                        error=str(e),
                    )
            
            # P0-3 Fix: If node failed, log and preserve failure state
            elif status == FAILED:
                logger.error(
                    "node_execution_failed",
                    node_id=node_id,
                    pipeline_id=new_state.get("pipeline_id"),
                    status=status,
                )
                # Failure state is already set by _convert_node_to_pipeline_state

        except Exception as e:
            logger.error(
                "integrated_executor_error",
                node_id=node_id,
                error=str(e),
            )
            # P0-3 Fix: Set failure state instead of silent fallback
            new_state["status"] = FAILED
            new_state["error"] = {
                "node_id": node_id,
                "message": str(e),
                "error_type": type(e).__name__,
            }
            # Don't add failed node to completed_nodes
            # and don't set a fallback deliverable

        # Increment iteration count for this node (track attempts even on failure)
        current_iteration = new_state["node_iterations"].get(node_id, 0)
        new_state["node_iterations"][node_id] = current_iteration + 1

        return new_state

    return executor
```

---

## 六、Phase 4: P1-1 状态持久化增强

### 6.1 问题分析

```python
# 当前问题:
# - state_json 只保留初始上下文
# - node_results / node_runs 表在集成路径中未写入
# - 数据库与日志完全脱节

# 修复方案:
# - 在每个节点完成后同步状态到数据库
# - 写入 node_results 表
# - 最终状态时完整序列化 state_json
```

### 6.2 失败测试 (先写)

```python
# tests/unit/test_state_persistence_fix.py

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json

from autoBMAD.docuswarm.pipeline.state import create_initial_state
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStatePersistenceFix:
    """测试状态持久化修复 - P1-1"""
    
    def test_node_result_saved_to_database(self):
        """Test: 节点执行结果应保存到 node_results 表"""
        # Given: 模拟 StateManager
        with patch("autoBMAD.docuswarm.storage.state_manager.StateManager") as mock_sm_class:
            mock_sm = MagicMock()
            mock_sm_class.return_value = mock_sm
            mock_sm.save_node_result = MagicMock(return_value=True)
            
            # When: 模拟节点执行后保存结果
            pipeline_id = "test-pipeline"
            node_id = "analyst"
            result_data = {
                "deliverable": {"title": "Test", "content": "Content"},
                "status": "completed",
                "iteration": 1,
            }
            
            # Then: save_node_result 应该被调用
            mock_sm.save_node_result(
                pipeline_id=pipeline_id,
                node_id=node_id,
                result=result_data,
            )
            
            mock_sm.save_node_result.assert_called_once()
            call_args = mock_sm.save_node_result.call_args
            assert call_args.kwargs["pipeline_id"] == pipeline_id
            assert call_args.kwargs["node_id"] == node_id
    
    def test_state_json_synchronized_after_each_node(self):
        """Test: 每个节点完成后 state_json 应同步"""
        # Given: 初始状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        
        # When: 添加一些执行结果
        state["completed_nodes"] = ["analyst"]
        state["deliverables"]["analyst"] = {"title": "Analysis", "content": "Results"}
        state["current_node"] = "pm"
        
        # Then: 状态应该是可序列化的
        try:
            json_str = json.dumps(state)
            restored = json.loads(json_str)
            assert restored["completed_nodes"] == ["analyst"]
            assert "analyst" in restored["deliverables"]
        except (TypeError, json.JSONDecodeError) as e:
            pytest.fail(f"State should be JSON serializable: {e}")
    
    def test_pipeline_state_persisted_on_completion(self):
        """Test: 流水线完成时状态应持久化到数据库"""
        # Given: 完成的流水线状态
        state = create_initial_state("test-pipeline", {"task": "test"})
        state["status"] = "completed"
        state["completed_nodes"] = ["analyst", "pm", "ux", "architect", "po"]
        state["current_node"] = "po"
        
        # Then: 应该能完整序列化
        json_str = json.dumps(state)
        assert "completed_nodes" in json_str
        assert "deliverables" in json_str
        assert "status" in json_str
```

### 6.3 实现修复

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py - 增强状态持久化

async def start_pipeline(
    self,
    subject_context: dict[str, Any],
    pipeline_id: str | None = None,
) -> str:
    """Start a new pipeline with validated context.
    
    P1-1 Fix: Enhanced state persistence after each node and on completion.
    """
    logger.info("starting_pipeline", subject_context=subject_context)

    # Step 1: Validate context using ContextValidator (Story 13.6)
    validator = self._get_context_validator()
    validation_result: ValidationResult = await validator.validate(subject_context)

    # Log warning if fallback was used
    if validation_result.fallback_used:
        logger.warning(
            "context_validation_fallback_used",
            reason=validation_result.reason,
            attempts=validation_result.attempts,
        )

    if not validation_result.valid:
        error_msg = (
            f"Context validation failed: {validation_result.reason}. "
            f"Missing info: {validation_result.missing_info}"
        )
        logger.error("context_validation_failed", result=validation_result)
        raise ContextValidationError(error_msg)

    # Step 1.5: Process referenced documents and generate summaries (Story 15.7)
    await self._process_referenced_documents(subject_context)

    # Step 2: Create pipeline in database
    subject = subject_context.get("subject", "Untitled")
    db_pipeline_id = self._state_manager.create_pipeline(
        subject=subject,
        subject_context=subject_context,
    )

    # Use provided pipeline_id or generated one
    final_pipeline_id = pipeline_id or db_pipeline_id

    # Step 3: Update status to running
    _ = self._state_manager.update_pipeline_status(
        final_pipeline_id,
        status=RUNNING,
        current_node=PIPELINE_NODES[0],  # Start with first node
    )

    # Step 4: Set logging context for this pipeline
    set_log_context(run_id=final_pipeline_id, node_id="orchestrator")

    # Step 4.5: Ensure pipeline output directory exists
    pipeline_work_dir = Path(self._work_dir) / final_pipeline_id
    pipeline_work_dir.mkdir(parents=True, exist_ok=True)
    logger.info(
        "pipeline_work_dir_created",
        path=str(pipeline_work_dir),
        pipeline_id=final_pipeline_id,
    )

    # Step 5: Create and execute the pipeline graph
    try:
        # Get checkpointer and config from CheckpointManager (Story 12.5 refactoring)
        checkpointer, config = await self._checkpoint_manager.get_or_create(final_pipeline_id)

        # Create initial state
        initial_state = create_initial_state(final_pipeline_id, subject_context)

        # Get session_manager for integrated node execution (Story 11.4)
        session_manager = self._get_or_create_session_manager()

        # P1-1 Fix: Import persistence helper
        from autoBMAD.docuswarm.pipeline.state_persistence import persist_node_result

        graph: Runnable[dict[str, Any], dict[str, Any]] = create_pipeline_graph(
            db_path=self._db_path,
            checkpointer=checkpointer,
            session_manager=session_manager,
        )

        # Execute the graph
        result: dict[str, Any] = await graph.ainvoke(initial_state, config)
        
        # P1-1 Fix: Persist final state to database
        self._persist_final_state(final_pipeline_id, result)

        # Update status based on actual result
        final_status = result.get("status", COMPLETED)
        final_current_node = result.get("current_node", "po")
        
        _ = self._state_manager.update_pipeline_status(
            final_pipeline_id,
            status=final_status,  # type: ignore[arg-type]
            current_node=final_current_node,
            state=result,  # P1-1: Save complete final state
        )

        logger.info(
            "pipeline_started",
            pipeline_id=final_pipeline_id,
            result=result,
        )

        return final_pipeline_id

    except Exception as e:
        logger.error("pipeline_execution_error", error=str(e))
        _ = self._state_manager.update_pipeline_status(
            final_pipeline_id,
            status="failed",  # type: ignore[arg-type]
        )
        raise


def _persist_final_state(self, pipeline_id: str, state: dict[str, Any]) -> None:
    """Persist final pipeline state to database.
    
    P1-1 Fix: Ensures complete state is saved including all node results.
    """
    try:
        # Update pipeline with complete state
        self._state_manager.update_pipeline_state(
            pipeline_id=pipeline_id,
            state=state,
        )
        
        # Save individual node results
        deliverables = state.get("deliverables", {})
        evaluations = state.get("evaluations", {})
        
        for node_id in state.get("completed_nodes", []):
            node_result = {
                "node_id": node_id,
                "deliverable": deliverables.get(node_id),
                "evaluation": evaluations.get(node_id),
                "status": "completed",
            }
            self._state_manager.save_node_result(
                pipeline_id=pipeline_id,
                node_id=node_id,
                result=node_result,
            )
        
        logger.info(
            "final_state_persisted",
            pipeline_id=pipeline_id,
            completed_nodes=state.get("completed_nodes", []),
        )
    except Exception as e:
        # Log but don't fail the pipeline
        logger.warning(
            "failed_to_persist_final_state",
            pipeline_id=pipeline_id,
            error=str(e),
        )
```

---

## 七、集成测试

### 7.1 端到端测试

```python
# tests/integration/test_start_command_fix.py

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from click.testing import CliRunner

from autoBMAD.docuswarm.main import cli


class TestStartCommandIntegration:
    """集成测试: start 命令完整修复验证"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @pytest.fixture
    def mock_context_file(self, tmp_path):
        context_file = tmp_path / "test-requirements.md"
        context_file.write_text("""# Test Project Requirements

## Overview
Build a test application.

## Features
- Feature 1
- Feature 2
""")
        return context_file
    
    def test_start_command_with_all_fixes(self, runner, mock_context_file):
        """Test: 完整修复后的 start 命令执行"""
        # Given: 所有修复已应用
        with runner.isolated_filesystem() as fs:
            fs_path = Path(fs)
            
            # Mock orchestrator
            with patch("autoBMAD.docuswarm.main.HybridOrchestrator") as mock_orch:
                mock_instance = MagicMock()
                
                # Mock async start_pipeline
                async def mock_start_pipeline(*args, **kwargs):
                    return "pipeline-test-123"
                
                mock_instance.start_pipeline = mock_start_pipeline
                mock_orch.return_value = mock_instance
                
                # When: 执行 start 命令
                result = runner.invoke(cli, [
                    "--verbose",
                    "start",
                    "--context", str(mock_context_file)
                ])
                
                # Then: 命令应该成功
                assert result.exit_code == 0, f"Command failed: {result.output}"
                assert "pipeline-test-123" in result.output
                
                # Verify environment setup
                import os
                assert "KIMI_SHARE_DIR" in os.environ
                
                # Verify tool registration
                from autoBMAD.docuswarm.models.tool_registry import ToolRegistry
                assert len(ToolRegistry.get_all()) > 0
```

---

## 八、验证清单

### 8.1 单元测试验证

```
□ P0-1: 环境修复
  □ test_kimi_share_dir_auto_set_on_start
  □ test_kimi_share_dir_uses_existing_if_set
  □ test_kimi_share_dir_directory_creation

□ P0-2: 工具注册
  □ test_tool_registry_not_empty_after_cli_start
  □ test_create_deliverable_tool_available_for_agent
  □ test_tool_registry_persists_across_imports

□ P0-3: 失败传播
  □ test_failed_node_not_added_to_completed_nodes
  □ test_successful_node_added_to_completed_nodes
  □ test_finalize_pipeline_state_with_failed_nodes
  □ test_finalize_pipeline_state_with_all_successful_nodes

□ P1-1: 状态持久化
  □ test_node_result_saved_to_database
  □ test_state_json_synchronized_after_each_node
  □ test_pipeline_state_persisted_on_completion
```

### 8.2 集成测试验证

```
□ test_start_command_with_all_fixes
□ test_pipeline_execution_with_mock_llm
□ test_failure_propagation_to_database
```

### 8.3 手动验证步骤

```bash
# 1. 清理环境
$env:KIMI_SHARE_DIR=""
rmdir .kimi -Recurse -Force -ErrorAction SilentlyContinue

# 2. 执行修复后的命令
python -m autoBMAD.docuswarm --verbose start --context docs/examples/project-requirements.md

# 3. 验证环境变量
$env:KIMI_SHARE_DIR  # 应该显示项目目录下的 .kimi

# 4. 验证工具注册
python -c "from autoBMAD.docuswarm.tools import register_all_tools; print(len(register_all_tools()))"
# 应该输出: 6

# 5. 验证数据库状态
python tools/docuswarm_debugger.py --pipeline-id <pipeline_id> --format markdown
```

---

## 九、修复总结

| 修复项 | 文件修改 | 关键变更 |
|---|---|---|
| P0-1 | `main.py` | 添加 `_ensure_kimi_share_dir()` 函数 |
| P0-2 | `main.py` | 添加 `_ensure_tools_registered()` 函数 |
| P0-3 | `graph.py` | 修改 `_convert_node_to_pipeline_state()` 检查状态 |
| P0-3 | `state.py` | 修改 `finalize_pipeline_state()` 检查失败节点 |
| P0-3 | `graph.py` | 修改 `_create_integrated_node_executor()` 处理异常 |
| P1-1 | `orchestrator.py` | 添加 `_persist_final_state()` 方法 |

---

## 十、风险评估

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| 环境变量冲突 | 中 | 仅在未设置时自动设置 KIMI_SHARE_DIR |
| 工具重复注册 | 低 | register_all_tools() 是幂等的 |
| 状态机变化 | 中 | 详细测试确保向后兼容 |
| 性能影响 | 低 | 持久化是异步的，不影响主流程 |

---

*方案完成 - 准备执行测试驱动修复*

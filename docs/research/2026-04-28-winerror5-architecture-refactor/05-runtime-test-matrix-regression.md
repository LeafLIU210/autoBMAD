# 研究报告 05：运行时测试矩阵与回归验证方案

**日期**: 2026-04-28  
**研究对象**: `tests/` 目录测试覆盖度，`autoBMAD/docuswarm` 运行时行为  
**关联问题**: 缺少能证明 WinError 5 不再污染流水线状态的回归测试  
**研究工具**: `tools/winerror5_architecture_research_tool.py --mode test-matrix`

---

## 执行摘要

当前测试体系缺少针对以下关键运行时行为的回归测试：

1. **Transport Preflight 区分能力**：没有测试验证 `direct_cli_ok=true` 但 `anyio_open_process_ok=false` 的场景。
2. **Preflight 失败阻止节点执行**：没有测试验证 preflight 失败后 graph 不被调用。
3. **失败节点不进入 completed_nodes**：现有 adapter 逻辑正确，但 graph.py 的覆盖逻辑无测试拦截。
4. **Finalize 状态一致性**：finalize_pipeline_state() 的盲目标记无测试覆盖。
5. **Provider 契约**：没有独立于真实 SDK 的 provider contract tests。
6. **MCP/Skills 配置一致性**：MCP server 注册与 `allowed_tools` 的映射无快照测试。

本报告定义 **8 个必要回归测试**，并提出测试基础设施改进方案。

---

## 1. 当前测试覆盖度审计

### 1.1 测试目录结构

```text
tests/
  test_pipeline/
  test_storage/
  test_node_execution/
  test_agents/
  ...
```

### 1.2 缺失测试清单

使用 `tools/winerror5_architecture_research_tool.py --mode test-matrix` 扫描结果：

| 测试名称 | 当前状态 | 优先级 |
|----------|----------|--------|
| `test_transport_preflight_distinguishes_direct_cli_from_anyio_spawn` | ❌ 缺失 | P0 |
| `test_preflight_failure_prevents_node_execution` | ❌ 缺失 | P0 |
| `test_failed_node_never_enters_completed_nodes_after_adapter` | ❌ 缺失 | P0 |
| `test_finalize_failed_when_failed_nodes_present` | ❌ 缺失 | P0 |
| `test_graph_result_status_matches_orchestrator_final_status` | ❌ 缺失 | P0 |
| `test_provider_contract_for_claude_agent_sdk` | ❌ 缺失 | P1 |
| `test_mcp_allowed_tools_match_registered_servers` | ❌ 缺失 | P1 |
| `test_skills_require_setting_sources_and_skill_tool` | ❌ 缺失 | P1 |

---

## 2. P0 测试详细设计

### 2.1 test_transport_preflight_distinguishes_direct_cli_from_anyio_spawn

**目标**: 验证 preflight 能准确区分不同 transport 层的能力状态。

```python
import pytest
from unittest.mock import patch, AsyncMock

from autoBMAD.docuswarm.llm.runtime_preflight import TransportPreflight

@pytest.mark.asyncio
async def test_preflight_distinguishes_layers():
    """当 direct CLI 和 subprocess 正常但 anyio 失败时，报告准确的诊断。"""
    preflight = TransportPreflight()

    with patch.object(preflight, "_test_direct_cli", return_value=(True, "2.1.92")), \
         patch.object(preflight, "_test_subprocess_popen", return_value=(True, "2.1.92")), \
         patch.object(preflight, "_test_anyio_open_process", return_value=(False, "PermissionError [WinError 5]")), \
         patch.object(preflight, "_test_sdk_connect", return_value=(False, "CLIConnectionError")):

        result = await preflight.check()

    assert result["success"] is False
    assert result["category"] == "transport_permission_denied"
    assert result["direct_cli_ok"] is True
    assert result["subprocess_popen_ok"] is True
    assert result["anyio_open_process_ok"] is False
    assert "WinError 5" in result["error"]
    assert any("anyio" in r.lower() for r in result["recommendations"])
```

### 2.2 test_preflight_failure_prevents_node_execution

**目标**: 验证 preflight 失败后，pipeline 不会进入 LangGraph 执行。

```python
import pytest
from unittest.mock import AsyncMock, patch

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.exceptions import OrchestratorError

@pytest.mark.asyncio
async def test_preflight_failure_prevents_graph_execution():
    """Preflight 失败时，不应调用 graph.ainvoke()。"""
    orchestrator = HybridOrchestrator(db_path=":memory:")

    # Mock runtime with failing preflight
    mock_runtime = AsyncMock()
    mock_runtime.preflight.return_value = {
        "success": False,
        "category": "transport_permission_denied",
        "error": "[WinError 5] 拒绝访问。",
        "recommendations": [],
    }
    orchestrator._runtime = mock_runtime

    with pytest.raises(OrchestratorError, match="Preflight failed"):
        await orchestrator.start_pipeline(
            subject_context={"subject": "test"},
        )

    # 关键断言：graph 从未被创建或调用
    mock_runtime.create_session.assert_not_called()
```

### 2.3 test_failed_node_never_enters_completed_nodes_after_adapter

**目标**: 验证 adapter 将 FAILED 节点路由到 failed_nodes 后，graph.py 不再覆盖。

```python
import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import create_initial_state, PIPELINE_NODES

@pytest.mark.asyncio
async def test_failed_node_stays_in_failed_nodes():
    """当 node_state.status == FAILED 时，不应出现在 completed_nodes。"""
    original = create_initial_state("test-pipeline", {"subject": "test"})
    node_state = {
        "node_id": "analyst",
        "status": "failed",
        "iteration": 1,
        "deliverable": None,
        "questions": [],
        "evaluation": None,
    }

    result = PipelineAdapter.convert_node_to_pipeline_state(node_state, original)

    assert "analyst" in result["failed_nodes"]
    assert "analyst" not in result["completed_nodes"]
    assert result["error"] is not None
```

**扩展**：测试 graph.py 的执行器逻辑（修复后）：

```python
async def test_graph_executor_respects_adapter_failed_nodes():
    """graph.py 不应将 adapter 标记为失败的节点加入 completed_nodes。"""
    from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor

    # Mock runtime that raises on session creation (simulating WinError 5)
    mock_runtime = AsyncMock()
    mock_runtime.create_session.side_effect = PermissionError("[WinError 5]")

    executor = _create_integrated_node_executor("analyst", mock_runtime)
    state = create_initial_state("test", {"subject": "test"})

    result = await executor(state)

    assert "analyst" in result.get("failed_nodes", [])
    assert "analyst" not in result.get("completed_nodes", [])
```

### 2.4 test_finalize_failed_when_failed_nodes_present

**目标**: 验证 `finalize_pipeline_state()` 在存在 `failed_nodes` 时设置 `status=FAILED`。

```python
from autoBMAD.docuswarm.pipeline.state import finalize_pipeline_state, create_initial_state

def test_finalize_sets_failed_when_failed_nodes_present():
    state = create_initial_state("test", {"subject": "test"})
    state["completed_nodes"] = ["analyst", "pm"]
    state["failed_nodes"] = ["ux"]
    state["error"] = {"node_id": "ux", "message": "WinError 5"}

    result = finalize_pipeline_state(state)

    assert result["status"] == "failed"
    # completed_nodes 应当被清理，移除 failed_nodes 中的节点
    assert "ux" not in result["completed_nodes"]

def test_finalize_sets_completed_when_all_success():
    state = create_initial_state("test", {"subject": "test"})
    state["completed_nodes"] = ["analyst", "pm", "ux", "architect", "po"]
    state["failed_nodes"] = []
    state["error"] = None

    result = finalize_pipeline_state(state)

    assert result["status"] == "completed"
```

### 2.5 test_graph_result_status_matches_orchestrator_final_status

**目标**: 验证 graph 返回状态、checkpoint 状态和 orchestrator 修正后的状态三者一致。

```python
@pytest.mark.asyncio
async def test_status_triple_consistency_on_failure():
    """当节点失败时，graph result、projection、DB status 都说 failed。"""
    orchestrator = HybridOrchestrator(db_path=":memory:")

    # Mock runtime that fails preflight
    mock_runtime = AsyncMock()
    mock_runtime.preflight.return_value = {"success": True}
    mock_runtime.create_session.side_effect = PermissionError("[WinError 5]")
    orchestrator._runtime = mock_runtime

    pipeline_id = await orchestrator.start_pipeline(
        subject_context={"subject": "test"},
    )

    # 由于 preflight 通过但节点执行失败，检查最终状态
    status = await orchestrator.get_pipeline_status(pipeline_id)
    assert status["status"] == "failed"

    # 检查 state_json 中的 status 也与 DB 一致
    state = status["state"]
    # 注意：这里需要修复 finalize_pipeline_state 后才能通过
    assert state.get("status") == "failed"
```

---

## 3. P1 测试详细设计

### 3.1 test_provider_contract_for_claude_agent_sdk

**目标**: 验证 `ClaudeAgentSDKProvider` 实现 `AgentRuntime` protocol，且 session 实现 `AgentSession` protocol。

```python
import pytest
from typing import runtime_checkable, Protocol

from autoBMAD.docuswarm.llm.provider import AgentRuntime, AgentSession
from autoBMAD.docuswarm.llm.claude_sdk_provider import ClaudeAgentSDKProvider

def test_claude_provider_implements_runtime():
    """ClaudeAgentSDKProvider 应当满足 AgentRuntime protocol。"""
    provider = ClaudeAgentSDKProvider(cwd=Path.cwd(), output_dir=Path.cwd())
    assert hasattr(provider, "preflight")
    assert hasattr(provider, "create_session")
    assert hasattr(provider, "close_all")
    assert hasattr(provider, "get_capabilities")

def test_claude_session_implements_session():
    """ClaudeSDKSession 应当满足 AgentSession protocol。"""
    from autoBMAD.docuswarm.llm.claude_sdk_provider import ClaudeSDKSession
    mock_client = AsyncMock()
    session = ClaudeSDKSession(client=mock_client, session_id="test", monitor=AsyncMock())
    assert hasattr(session, "session_id")
    assert hasattr(session, "prompt")
    assert hasattr(session, "close")
```

### 3.2 test_mcp_allowed_tools_match_registered_servers

**目标**: 验证 MCP server 注册的工具名与 `allowed_tools` 列表一致。

```python
def test_mcp_tools_snapshot():
    """MCP server 工具名与 allowed_tools 应当一致。"""
    from autoBMAD.docuswarm.llm.claude_options import ClaudeOptionsFactory

    factory = ClaudeOptionsFactory(cwd=Path.cwd(), output_dir=Path.cwd())
    options = factory.build(node_id="analyst")

    mcp_servers = options.get("mcp_servers", {})
    allowed_tools = options.get("allowed_tools", [])

    # 提取所有 MCP 工具名
    mcp_tools = []
    for server_name, server_config in mcp_servers.items():
        for tool in server_config.get("tools", []):
            mcp_tools.append(f"mcp__{server_name}__{tool['name']}")

    for tool in mcp_tools:
        assert tool in allowed_tools, f"MCP tool {tool} not in allowed_tools"
```

### 3.3 test_skills_require_setting_sources_and_skill_tool

**目标**: 验证当 `sdk_native_skills=True` 时，`setting_sources` 和 `Skill` 工具同时存在。

```python
def test_skills_configuration_completeness():
    """Skills 启用时，setting_sources 和 allowed_tools 必须同时包含 Skill。"""
    from autoBMAD.docuswarm.llm.claude_options import ClaudeOptionsFactory

    factory = ClaudeOptionsFactory(cwd=Path.cwd(), output_dir=Path.cwd())
    options = factory.build(node_id="analyst", sdk_native_skills=True)

    assert "setting_sources" in options
    assert "project" in options["setting_sources"]
    assert "Skill" in options.get("allowed_tools", [])
    assert options["allowed_tools"][0] == "Skill"  # Skill 应当排在第一位
```

---

## 4. 测试基础设施改进

### 4.1 MockRuntime / MockSession 工具包

新建 `tests/mocks/runtime_mocks.py`：

```python
from collections.abc import AsyncIterator
from typing import Any

class MockSession:
    def __init__(self, session_id: str = "mock-session"):
        self._session_id = session_id
        self.prompts: list[str] = []

    @property
    def session_id(self) -> str:
        return self._session_id

    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]:
        self.prompts.append(message)
        yield {"role": "assistant", "content": [{"type": "text", "text": "mock response"}]}

    async def close(self) -> None:
        pass

class MockRuntime:
    def __init__(self, preflight_ok: bool = True, fail_create: bool = False):
        self.preflight_ok = preflight_ok
        self.fail_create = fail_create
        self.sessions: list[MockSession] = []

    async def preflight(self) -> dict[str, Any]:
        return {
            "success": self.preflight_ok,
            "category": "ok" if self.preflight_ok else "transport_permission_denied",
            "error": "" if self.preflight_ok else "mock transport failure",
        }

    async def create_session(self, node_id: str, **kwargs) -> MockSession:
        if self.fail_create:
            raise PermissionError("[WinError 5] mock")
        session = MockSession(f"mock-{node_id}")
        self.sessions.append(session)
        return session

    async def close_all(self) -> None:
        for s in self.sessions:
            await s.close()

    def get_capabilities(self) -> dict[str, Any]:
        return {"provider": "mock", "supports_mcp": True}
```

### 4.2 参数化测试：跨平台 transport 行为

```python
import pytest

@pytest.mark.parametrize("platform,direct_ok,popen_ok,anyio_ok,expected_category", [
    ("win32", True, True, False, "transport_permission_denied"),
    ("linux", True, True, True, "ok"),
    ("darwin", True, True, True, "ok"),
    ("win32", False, False, False, "cli_not_found"),
])
@pytest.mark.asyncio
async def test_preflight_parametrized(platform, direct_ok, popen_ok, anyio_ok, expected_category):
    ...
```

### 4.3 CI 集成建议

在 `.github/workflows/` 或本地 CI 中增加：

```yaml
- name: WinError 5 Regression Tests
  run: pytest tests/test_pipeline/test_preflight.py -v -m "winerror5"

- name: State Semantics Tests
  run: pytest tests/test_pipeline/test_state_semantics.py -v

- name: Provider Contract Tests
  run: pytest tests/test_llm/test_provider_contract.py -v
```

---

## 5. 测试与重构的协作关系

```text
重构阶段                测试支撑
─────────────────────────────────────────────────────────
P0: runtime_preflight   test_transport_preflight_...
                        test_preflight_failure_prevents_...

P0: graph.py 修复        test_failed_node_never_enters_...
                        test_graph_executor_respects_...

P0: finalize 修复        test_finalize_failed_when_...
                        test_finalize_sets_completed_...

P1: provider 边界        test_provider_contract_for_...
                        MockRuntime / MockSession 工具包

P1: MCP/Skills           test_mcp_allowed_tools_match_...
                        test_skills_require_setting_sources_...

P1/P2: 状态所有权         test_graph_result_status_matches_...
                        test_resume_does_not_skip_failed_nodes
                        test_export_does_not_export_empty_deliverables
```

---

## 6. 结论

当前测试缺口使得 `WinError 5` 相关的状态污染问题无法在 CI 中被提前捕获。补齐这 8 个回归测试是重构方案的必要组成部分：

- **P0 测试（5 个）** 必须在任何代码变更前编写，作为重构的安全网。
- **P1 测试（3 个）** 在 provider 边界重构后补齐，验证新架构的契约。
- **Mock 工具包** 为后续所有节点执行测试提供脱离真实 SDK 的能力。

没有测试覆盖的重构是盲目的。这 8 个测试将证明：即使 Windows transport 再次失败，DocuSwarm 也能以清晰、一致、不污染状态的方式快速失败。

---

## 参考资料

- `tests/` 目录结构
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/llm/session_manager.py`
- `tools/winerror5_architecture_research_tool.py`

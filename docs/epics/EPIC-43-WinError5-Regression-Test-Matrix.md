# EPIC-43: WinError 5 运行时回归测试矩阵

**Epic ID**: EPIC-43  
**Epic 名称**: WinError 5 运行时回归测试矩阵  
**优先级**: P0（CRITICAL）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-28）  
**创建日期**: 2026-04-28  
**研究来源**: `docs/research/2026-04-28-winerror5-architecture-refactor/05-runtime-test-matrix-regression.md`  
**预估工作量**: ~3 days

---

## Epic 概述

当前测试体系缺少针对 WinError 5 相关关键运行时行为的回归测试。Transport Preflight 区分能力、Preflight 失败阻止节点执行、失败节点不进入 completed_nodes、Finalize 状态一致性、Provider 契约等关键行为均无测试覆盖。这意味着即使代码被修复，也无法在 CI 中防止回归。

**核心问题**：
- 没有测试验证 `direct_cli_ok=true` 但 `anyio_open_process_ok=false` 的场景
- 没有测试验证 preflight 失败后 graph 不被调用
- graph.py 的覆盖逻辑无测试拦截
- `finalize_pipeline_state()` 的盲目标记无测试覆盖
- 没有独立于真实 SDK 的 provider contract tests

**推荐方案**：补齐 8 个必要回归测试 + Mock 工具包 + 参数化测试 + CI 集成。

---

## 背景与技术分析

### 缺失测试清单

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

## Stories

### Story 43.1: P0 回归测试（5个）

**目标**：补齐 5 个 P0 优先级回归测试，覆盖 WinError 5 核心场景。

**涉及文件**：3 个（新建/修改测试文件）

#### 验收标准

- [ ] `test_transport_preflight_distinguishes_direct_cli_from_anyio_spawn`
  - 当 direct CLI 和 subprocess 正常但 anyio 失败时，报告 `category="transport_permission_denied"`
  - 验证 `direct_cli_ok=true`, `subprocess_popen_ok=true`, `anyio_open_process_ok=false`
  - 验证错误消息包含 `WinError 5`
  - 验证建议中包含 `anyio` 相关诊断

- [ ] `test_preflight_failure_prevents_node_execution`
  - Mock runtime 的 `preflight` 返回 `success=False`
  - 验证 `graph.ainvoke()` 从未被调用
  - 验证 `create_session` 从未被调用
  - 验证抛出 `OrchestratorError` 且消息包含 `Preflight failed`

- [ ] `test_failed_node_never_enters_completed_nodes_after_adapter`
  - 构造 `node_state.status == FAILED` 的 adapter 输入
  - 验证 adapter 输出中节点在 `failed_nodes` 中
  - 验证 adapter 输出中节点**不在** `completed_nodes` 中
  - 验证 `error` 字段非空

- [ ] `test_finalize_failed_when_failed_nodes_present`
  - 构造包含 `failed_nodes` 的 state
  - 验证 `finalize_pipeline_state()` 返回 `status=FAILED`
  - 验证 `completed_nodes` 中被清理（移除 `failed_nodes` 中的节点）

- [ ] `test_graph_result_status_matches_orchestrator_final_status`
  - Mock runtime preflight 通过但 `create_session` 抛出 `PermissionError`
  - 验证最终 DB status 为 `failed`
  - 验证 state_json 中的 status 也为 `failed`（需配合 EPIC-40 修复）

#### 技术规格

```python
# tests/test_pipeline/test_preflight_regression.py
@pytest.mark.asyncio
async def test_preflight_distinguishes_direct_cli_from_anyio_spawn():
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

@pytest.mark.asyncio
async def test_preflight_failure_prevents_node_execution():
    orchestrator = HybridOrchestrator(db_path=":memory:")
    mock_runtime = AsyncMock()
    mock_runtime.preflight.return_value = {
        "success": False,
        "category": "transport_permission_denied",
        "error": "[WinError 5] 拒绝访问。",
        "recommendations": [],
    }
    orchestrator._runtime = mock_runtime
    with pytest.raises(OrchestratorError, match="Preflight failed"):
        await orchestrator.start_pipeline(subject_context={"subject": "test"})
    mock_runtime.create_session.assert_not_called()
```

#### 测试要求

- 所有 P0 测试标记为 `@pytest.mark.winerror5`
- 测试不依赖真实 SDK 或真实 Claude CLI
- 测试在 CI 中运行时间 < 5 秒/个

---

### Story 43.2: P1 Provider 契约测试（3个）

**目标**：补齐 3 个 P1 优先级测试，验证 provider 边界重构后的契约。

**涉及文件**：1 个（新建 `tests/test_llm/test_provider_contract.py`）

#### 验收标准

- [ ] `test_provider_contract_for_claude_agent_sdk`
  - 验证 `ClaudeAgentSDKProvider` 实现 `AgentRuntime` protocol
  - 验证 `ClaudeSDKSession` 实现 `AgentSession` protocol
  - 使用 `typing.runtime_checkable` 或属性检查

- [ ] `test_mcp_allowed_tools_match_registered_servers`
  - 验证 MCP server 注册的工具名与 `allowed_tools` 列表一致
  - 使用 `ClaudeOptionsFactory` 生成 options
  - 提取所有 MCP 工具名并与 `allowed_tools` 比较

- [ ] `test_skills_require_setting_sources_and_skill_tool`
  - 验证当 `sdk_native_skills=True` 时，`setting_sources` 和 `Skill` 工具同时存在
  - 验证 `Skill` 排在 `allowed_tools` 第一位

#### 技术规格

```python
# tests/test_llm/test_provider_contract.py
def test_claude_provider_implements_runtime():
    provider = ClaudeAgentSDKProvider(cwd=Path.cwd(), output_dir=Path.cwd())
    assert hasattr(provider, "preflight")
    assert hasattr(provider, "create_session")
    assert hasattr(provider, "close_all")
    assert hasattr(provider, "get_capabilities")

def test_mcp_tools_snapshot():
    factory = ClaudeOptionsFactory(cwd=Path.cwd(), output_dir=Path.cwd())
    options = factory.build(node_id="analyst")
    mcp_servers = options.get("mcp_servers", {})
    allowed_tools = options.get("allowed_tools", [])
    mcp_tools = []
    for server_name, server_config in mcp_servers.items():
        for tool in server_config.get("tools", []):
            mcp_tools.append(f"mcp__{server_name}__{tool['name']}")
    for tool in mcp_tools:
        assert tool in allowed_tools, f"MCP tool {tool} not in allowed_tools"

def test_skills_configuration_completeness():
    factory = ClaudeOptionsFactory(cwd=Path.cwd(), output_dir=Path.cwd())
    options = factory.build(node_id="analyst", sdk_native_skills=True)
    assert "setting_sources" in options
    assert "project" in options["setting_sources"]
    assert "Skill" in options.get("allowed_tools", [])
```

---

### Story 43.3: MockRuntime / MockSession 工具包

**目标**：新建 `tests/mocks/runtime_mocks.py`，为后续所有节点执行测试提供脱离真实 SDK 的能力。

**涉及文件**：1 个（新建 `tests/mocks/runtime_mocks.py`）

#### 验收标准

- [ ] 新建 `MockSession` 类，实现 `AgentSession` protocol
  - `session_id` property
  - `prompt()` 返回固定 mock 响应
  - `close()` 无操作

- [ ] 新建 `MockRuntime` 类，实现 `AgentRuntime` protocol
  - `preflight()` 返回可配置结果
  - `create_session()` 返回 `MockSession`，支持配置失败
  - `close_all()` 关闭所有创建的 session
  - `get_capabilities()` 返回 mock 能力

- [ ] 两个类不依赖 `claude_agent_sdk`
- [ ] 支持 `AsyncMock` 风格的断言

#### 技术规格

```python
# tests/mocks/runtime_mocks.py
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

#### 测试要求

- 单元测试：`tests/test_mocks/test_runtime_mocks.py`
  - 测试 `MockRuntime` 满足 `AgentRuntime` protocol
  - 测试 `MockSession` 满足 `AgentSession` protocol
  - 测试 `fail_create=True` 时抛出 `PermissionError`

---

### Story 43.4: 参数化跨平台 transport 测试

**目标**：为 preflight 行为添加参数化测试，覆盖不同平台场景。

**涉及文件**：1 个（新建 `tests/test_llm/test_preflight_parametrized.py`）

#### 验收标准

- [ ] 使用 `@pytest.mark.parametrize` 覆盖以下场景：
  - `("win32", True, True, False, "transport_permission_denied")`
  - `("linux", True, True, True, "ok")`
  - `("darwin", True, True, True, "ok")`
  - `("win32", False, False, False, "cli_not_found")`
- [ ] 每个场景验证 `category` 和 `success` 正确
- [ ] 测试不依赖真实平台（通过 `patch` 模拟 `sys.platform`）

#### 技术规格

```python
@pytest.mark.parametrize(
    "platform,direct_ok,popen_ok,anyio_ok,expected_category",
    [
        ("win32", True, True, False, "transport_permission_denied"),
        ("linux", True, True, True, "ok"),
        ("darwin", True, True, True, "ok"),
        ("win32", False, False, False, "cli_not_found"),
    ],
)
@pytest.mark.asyncio
async def test_preflight_parametrized(platform, direct_ok, popen_ok, anyio_ok, expected_category):
    with patch("sys.platform", platform):
        preflight = TransportPreflight()
        # patch 各层探针...
        result = await preflight.check()
    assert result["category"] == expected_category
```

---

### Story 43.5: CI 集成与测试标记

**目标**：在 CI 配置中增加 WinError 5 回归测试、状态语义测试、Provider 契约测试的独立运行步骤。

**涉及文件**：1 个（修改 `.github/workflows/*.yml` 或新建本地 CI 配置）

#### 验收标准

- [ ] CI 中增加 `pytest tests/test_pipeline/test_preflight*.py -v -m "winerror5"` 步骤
- [ ] CI 中增加 `pytest tests/test_pipeline/test_state_semantics*.py -v` 步骤
- [ ] CI 中增加 `pytest tests/test_llm/test_provider_contract.py -v` 步骤
- [ ] 本地运行脚本 `scripts/run_regression_tests.sh` 一键执行所有回归测试
- [ ] 测试标记定义：`pytest.mark.winerror5`（P0 回归）、`pytest.mark.state_semantics`（状态语义）、`pytest.mark.provider_contract`（Provider 契约）

#### 技术规格

```yaml
# .github/workflows/ci.yml 新增步骤
- name: WinError 5 Regression Tests
  run: pytest tests/test_pipeline/test_preflight*.py -v -m "winerror5"

- name: State Semantics Tests
  run: pytest tests/test_pipeline/test_state_semantics*.py -v

- name: Provider Contract Tests
  run: pytest tests/test_llm/test_provider_contract.py -v
```

```bash
# scripts/run_regression_tests.sh
#!/bin/bash
set -e
pytest tests/test_pipeline/test_preflight*.py -v -m "winerror5"
pytest tests/test_pipeline/test_state_semantics*.py -v
pytest tests/test_llm/test_provider_contract.py -v
pytest tests/test_pipeline/test_graph_completion_semantics.py -v
pytest tests/test_pipeline/test_finalize_state.py -v
```

---

## 依赖关系

```
Story 43.3 → Story 43.1  (MockRuntime 用于 preflight 失败测试)
Story 43.3 → Story 43.2  (MockRuntime 用于 provider 契约测试)
Story 43.4 可独立实施
Story 43.5 → Story 43.1, 43.2  (CI 配置依赖测试文件存在)
```

**并行路径**：
- Story 43.1（P0 回归）、43.2（P1 契约）、43.3（Mock 工具包）、43.4（参数化）可并行实施
- Story 43.5（CI 集成）在最后实施

---

## 实施阶段划分

### 阶段 1（Mock 工具包 + P0 回归测试）

- **Story 43.3**：MockRuntime / MockSession 工具包
- **Story 43.1**：P0 回归测试（5个）

**预期收益**：WinError 5 相关核心行为有测试安全网。

### 阶段 2（P1 契约 + 参数化 + CI）

- **Story 43.2**：P1 Provider 契约测试（3个）
- **Story 43.4**：参数化跨平台 transport 测试
- **Story 43.5**：CI 集成与测试标记

**预期收益**：Provider 重构后的契约有测试保障，CI 能自动发现回归。

---

## 测试与重构的协作关系

```text
重构阶段                测试支撑
─────────────────────────────────────────────────────────
EPIC-39: runtime_preflight   test_transport_preflight_...
                             test_preflight_failure_prevents_...

EPIC-40: graph.py 修复        test_failed_node_never_enters_...
                             test_graph_executor_respects_...
                             test_finalize_failed_when_...

EPIC-41: provider 边界        test_provider_contract_for_...
                             MockRuntime / MockSession 工具包

EPIC-42: 状态所有权           test_graph_result_status_matches_...
                             test_resume_does_not_skip_failed_nodes
                             test_export_does_not_export_empty_deliverables
```

---

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| Mock 工具包与真实 SDK 行为偏差 | MEDIUM | 保留集成测试覆盖真实路径，Mock 仅用于单元测试 |
| 参数化测试过多导致 CI 变慢 | LOW | 参数化仅 4 个场景，总运行时间 < 1 秒 |
| 测试标记维护成本 | LOW | 使用 pytest 内置标记机制，无额外依赖 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `tests/test_pipeline/test_preflight_regression.py` | Story 43.1 P0 回归测试 |
| `tests/test_llm/test_provider_contract.py` | Story 43.2 P1 契约测试 |
| `tests/mocks/runtime_mocks.py` | Story 43.3 Mock 工具包 |
| `tests/test_llm/test_preflight_parametrized.py` | Story 43.4 参数化测试 |
| `.github/workflows/ci.yml` | Story 43.5 CI 集成 |
| `scripts/run_regression_tests.sh` | Story 43.5 本地回归脚本 |

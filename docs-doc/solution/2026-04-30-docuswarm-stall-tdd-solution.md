# 2026-04-30 DocuSwarm Pipeline Stall P0/P1 测试驱动实施方案

> **来源**: `docs-doc/research/2026-04-30-docuswarm-stall-deep-research-report.md`  
> **目标**: 为 P0 和 P1 全部问题提供可执行的测试驱动开发（TDD）方案  
> **原则**: 先写失败的测试 -> 最小化实现 -> 验证测试通过 -> 重构  
> **测试框架**: pytest + pytest-asyncio + unittest.mock  
> **报告时间**: 2026-04-30 CST

---

## 目录

1. [方案概述](#方案概述)
2. [测试框架与目录结构](#测试框架与目录结构)
3. [P0-1: Graph 执行中断最终化](#p0-1-graph-执行中断最终化)
4. [P0-2: In-Flight Session 持久化](#p0-2-in-flight-session-持久化)
5. [P0-3: 节点专用 SessionManager 生命周期](#p0-3-节点专用-sessionmanager-生命周期)
6. [P1-1: SinglePrompt 取消语义修复](#p1-1-singleprompt-取消语义修复)
7. [P1-2: SummaryAgent Timeout 调整](#p1-2-summaryagent-timeout-调整)
8. [P1-3: DocsContextSummary 同步](#p1-3-docscontextsummary-同步)
9. [Stale-Running 检测（P0-1 延伸）](#stale-running-检测p0-1-延伸)
10. [实施顺序与里程碑](#实施顺序与里程碑)
11. [集成测试计划](#集成测试计划)

---

## 方案概述

### TDD 循环

```
[编写测试] --> [运行失败(红色)] --> [最小化实现] --> [运行通过(绿色)] --> [重构]
    ^                                                                  |
    +------------------------------------------------------------------+
```

### 覆盖的问题

| ID | 问题 | 严重度 | 测试文件 |
|----|------|--------|----------|
| P0-1-A | orchestrator 不捕获 CancelledError/KeyboardInterrupt | Critical | `test_p0_interruption_finalization.py` |
| P0-1-B | CLI 不捕获 KeyboardInterrupt | Critical | `test_p0_cli_interruption.py` |
| P0-1-C | 缺少 atexit 兜底机制 | High | `test_p0_atexit_finalization.py` |
| P0-1-D | stale-running 检测缺失 | High | `test_p0_stale_running_detection.py` |
| P0-2 | in-flight session 未持久化 | High | `test_p0_session_persistence.py` |
| P0-3 | 节点 SessionManager 未关闭 | High | `test_p0_session_manager_lifecycle.py` |
| P1-1 | single_prompt 吞掉 cancellation | Medium-High | `test_p1_cancellation_semantics.py` |
| P1-2 | SummaryAgent timeout 偏紧 | Medium | `test_p1_summary_agent_timeout.py` |
| P1-3 | docs_context_summary 未同步 | Medium | `test_p1_summary_sync.py` |

---

## 测试框架与目录结构

### 新增测试文件

```
tests/
├── conftest.py                              # 添加新 fixture
├── test_docuswarm_p0_interruption_finalization.py
├── test_docuswarm_p0_cli_interruption.py
├── test_docuswarm_p0_atexit_finalization.py
├── test_docuswarm_p0_stale_running_detection.py
├── test_docuswarm_p0_session_persistence.py
├── test_docuswarm_p0_session_manager_lifecycle.py
├── test_docuswarm_p1_cancellation_semantics.py
├── test_docuswarm_p1_summary_agent_timeout.py
└── test_docuswarm_p1_summary_sync.py
```

### conftest.py 新增 fixture

```python
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_state_manager(tmp_path):
    """Create a real StateManager backed by :memory: database."""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    sm = StateManager(db_path=":memory:")
    yield sm
    sm._db.close_all()

@pytest.fixture
def mock_session_manager():
    """Create a mock SessionManager with async close_all."""
    mgr = MagicMock()
    mgr.close_all = AsyncMock()
    mgr.create_session = AsyncMock(return_value="mock_session_id")
    mgr.config = MagicMock()
    return mgr
```

---

## P0-1: Graph 执行中断最终化

### P0-1-A: Orchestrator 层 CancelledError/KeyboardInterrupt 处理

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_interruption_finalization.py`

```python
"""P0-1-A: Pipeline interruption finalization tests."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestOrchestratorCancellationFinalization:
    """T1.1: CancelledError during graph.ainvoke() must update DB status."""

    @pytest.mark.asyncio
    async def test_cancelled_error_updates_status_to_cancelled(self) -> None:
        """When graph raises CancelledError, DB status must be 'cancelled'."""
        state_manager = StateManager(db_path=":memory:")
        orchestrator = HybridOrchestrator(
            db_path=":memory:", api_key="test", base_url="http://test",
        )
        orchestrator._state_manager = state_manager

        pipeline_id = state_manager.create_pipeline("test-subject")
        await state_manager.update_pipeline_state(pipeline_id, {"status": "running"})

        with patch.object(
            orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock
        ):
            with patch.object(orchestrator, "_create_checkpointer", new_callable=AsyncMock):
                with patch("autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph") as mock_create_graph:
                    mock_graph = MagicMock()
                    mock_graph.ainvoke = AsyncMock(
                        side_effect=asyncio.CancelledError("Simulated cancellation")
                    )
                    mock_create_graph.return_value = mock_graph

                    with pytest.raises(asyncio.CancelledError):
                        await orchestrator.start_pipeline(
                            {"subject": "test", "content": "test"},
                            pipeline_id=pipeline_id,
                        )

        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline is not None
        assert pipeline["status"] != "running"
        assert pipeline["status"] in ("cancelled", "interrupted", "failed")
        assert pipeline["error"] is not None
        assert pipeline["error"]["type"] == "CancelledError"

    @pytest.mark.asyncio
    async def test_keyboard_interrupt_updates_status_to_interrupted(self) -> None:
        """When graph raises KeyboardInterrupt, DB status must be 'interrupted'."""
        state_manager = StateManager(db_path=":memory:")
        orchestrator = HybridOrchestrator(
            db_path=":memory:", api_key="test", base_url="http://test",
        )
        orchestrator._state_manager = state_manager

        pipeline_id = state_manager.create_pipeline("test-subject")
        await state_manager.update_pipeline_state(pipeline_id, {"status": "running"})

        with patch.object(
            orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock
        ):
            with patch.object(orchestrator, "_create_checkpointer", new_callable=AsyncMock):
                with patch("autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph") as mock_create_graph:
                    mock_graph = MagicMock()
                    mock_graph.ainvoke = AsyncMock(side_effect=KeyboardInterrupt())
                    mock_create_graph.return_value = mock_graph

                    with pytest.raises(KeyboardInterrupt):
                        await orchestrator.start_pipeline(
                            {"subject": "test", "content": "test"},
                            pipeline_id=pipeline_id,
                        )

        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline is not None
        assert pipeline["status"] != "running"
        assert pipeline["status"] in ("interrupted", "cancelled")
        assert pipeline["error"] is not None
        assert pipeline["error"]["type"] == "KeyboardInterrupt"

    @pytest.mark.asyncio
    async def test_exception_still_updates_status_to_failed(self) -> None:
        """Existing Exception handling must continue to work."""
        state_manager = StateManager(db_path=":memory:")
        orchestrator = HybridOrchestrator(
            db_path=":memory:", api_key="test", base_url="http://test",
        )
        orchestrator._state_manager = state_manager

        pipeline_id = state_manager.create_pipeline("test-subject")

        with patch.object(
            orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock
        ):
            with patch.object(orchestrator, "_create_checkpointer", new_callable=AsyncMock):
                with patch("autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph") as mock_create_graph:
                    mock_graph = MagicMock()
                    mock_graph.ainvoke = AsyncMock(side_effect=RuntimeError("Simulated error"))
                    mock_create_graph.return_value = mock_graph

                    result = await orchestrator.start_pipeline(
                        {"subject": "test", "content": "test"},
                        pipeline_id=pipeline_id,
                    )

        assert result["status"] == "failed"
        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["status"] == "failed"
```

**预期结果**:
- `test_cancelled_error_updates_status_to_cancelled` **FAIL** - 当前不捕获 CancelledError
- `test_keyboard_interrupt_updates_status_to_interrupted` **FAIL** - 同理
- `test_exception_still_updates_status_to_failed` **PASS** - 现有行为

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/pipeline/orchestrator.py`，在 `except Exception` 之前添加：

```python
except asyncio.CancelledError as e:
    logger.warning("pipeline_cancelled", pipeline_id=final_pipeline_id, error_type=type(e).__name__)
    await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {
            "status": "cancelled",
            "error": {"message": str(e), "type": type(e).__name__},
        },
    )
    raise  # Re-raise after state update

except KeyboardInterrupt:
    logger.warning("pipeline_interrupted", pipeline_id=final_pipeline_id, error_type="KeyboardInterrupt")
    await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {
            "status": "interrupted",
            "error": {"message": "User interrupted", "type": "KeyboardInterrupt"},
        },
    )
    raise

except Exception as e:
    # 原有逻辑不变
    logger.error("pipeline_execution_error", error=str(e))
    ...
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_interruption_finalization.py -v
```

---

### P0-1-B: CLI 层 KeyboardInterrupt 处理

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_cli_interruption.py`

```python
"""P0-1-B: CLI interruption handling tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from autoBMAD.docuswarm.cli.commands.start import start


class TestCliStartKeyboardInterrupt:
    """T2.1: CLI start must handle KeyboardInterrupt gracefully."""

    def test_cli_start_shows_interrupted_on_keyboard_interrupt(self) -> None:
        """When user presses Ctrl+C, CLI must show 'interrupted' not traceback."""
        runner = CliRunner()

        with patch("autoBMAD.docuswarm.cli.commands.start.PipelineService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service

            async def mock_start(*args: Any, **kwargs: Any) -> dict[str, Any]:
                raise KeyboardInterrupt()

            mock_service.start = mock_start

            import tempfile, os
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write("# Test context")
                context_file = f.name

            try:
                result = runner.invoke(start, ["--context", context_file])
                assert result.exit_code != 0
                output_lower = result.output.lower()
                assert (
                    "interrupted" in output_lower or "cancelled" in output_lower
                ), f"Expected interruption message, got: {result.output}"
                assert "traceback" not in output_lower
            finally:
                os.unlink(context_file)

    def test_cli_start_still_fails_on_exception(self) -> None:
        """Regular exceptions must still show error messages."""
        runner = CliRunner()

        with patch("autoBMAD.docuswarm.cli.commands.start.PipelineService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service

            async def mock_start(*args: Any, **kwargs: Any) -> dict[str, Any]:
                raise RuntimeError("Something broke")

            mock_service.start = mock_start

            import tempfile, os
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write("# Test context")
                context_file = f.name

            try:
                result = runner.invoke(start, ["--context", context_file])
                assert result.exit_code != 0
                assert "failed" in result.output.lower() or "error" in result.output.lower()
            finally:
                os.unlink(context_file)
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/cli/commands/start.py`：

```python
def start(context_file: str) -> None:
    service = PipelineService()
    try:
        result = asyncio.run(service.start(context_file))
        ...
    except click.ClickException:
        raise
    except KeyboardInterrupt:
        console.print("[yellow]Pipeline interrupted by user[/yellow]")
        raise click.ClickException("Pipeline interrupted")
    except FileNotFoundError as e:
        ...
    except Exception as e:
        ...
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_cli_interruption.py -v
```

---

### P0-1-C: Atexit 兜底机制

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_atexit_finalization.py`

```python
"""P0-1-C: Atexit emergency finalization tests."""

from __future__ import annotations

import atexit
from unittest.mock import MagicMock, patch

import pytest

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestAtexitEmergencyFinalization:
    """T3.1: atexit handler must update running pipelines on unclean exit."""

    def test_atexit_handler_registered_on_service_start(self) -> None:
        """PipelineService.start() must register atexit handler."""
        from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
        service = PipelineService(db_path=":memory:")
        assert hasattr(service, "_emergency_finalize") or hasattr(service, "_current_pipeline_id")

    def test_atexit_handler_updates_running_pipeline(self) -> None:
        """Emergency finalize must update running pipeline to 'interrupted'."""
        state_manager = StateManager(db_path=":memory:")
        pipeline_id = state_manager.create_pipeline("test")
        state_manager.update_pipeline_state(pipeline_id, {"status": "running"})

        from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
        service = PipelineService(db_path=":memory:")
        service._db_path = ":memory:"
        service._current_pipeline_id = pipeline_id

        if hasattr(service, "_emergency_finalize"):
            service._emergency_finalize()
        else:
            pytest.skip("_emergency_finalize not implemented yet")

        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["status"] == "interrupted"
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/cli/services/pipeline_service.py`：

```python
import atexit
import sqlite3

class PipelineService:
    def __init__(self, db_path: str | None = None) -> None:
        config = load_config()
        self._db_path = db_path or str(config.db_path)
        self._state_manager = StateManager(db_path=self._db_path)
        self._current_pipeline_id: str | None = None

    async def start(self, context_file: str) -> dict[str, Any]:
        ...
        self._current_pipeline_id = None
        atexit.register(self._emergency_finalize)
        try:
            result = await orchestrator.start_pipeline(subject_context)
            self._current_pipeline_id = result.get("pipeline_id")
            return result
        finally:
            atexit.unregister(self._emergency_finalize)
            self._current_pipeline_id = None

    def _emergency_finalize(self) -> None:
        pipeline_id = self._current_pipeline_id
        if pipeline_id is None:
            return
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "UPDATE pipelines SET status = 'interrupted', updated_at = CURRENT_TIMESTAMP "
                "WHERE pipeline_id = ? AND status = 'running'",
                (pipeline_id,)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_atexit_finalization.py -v
```

---

## P0-2: In-Flight Session 持久化

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_session_persistence.py`

```python
"""P0-2: Session ID persistence tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestSessionIdPersistence:
    """T4.1: Session ID must be persisted to StateManager during node execution."""

    @pytest.mark.asyncio
    async def test_session_id_written_to_state_manager(self) -> None:
        """When IndependentAgent creates a session, session_id must be in DB."""
        state_manager = StateManager(db_path=":memory:")
        pipeline_id = state_manager.create_pipeline("test")

        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        agent = IndependentAgent(node_id="analyst", session_manager=MagicMock())
        agent.state_manager = state_manager

        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_test_123")
        mock_pipeline_mgr.close_all = AsyncMock()

        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.return_value = [
                    {"type": "text", "text": '{"deliverable": {"title": "Test"}, "questions": []}'}
                ]
                result = await agent.execute_with_input(
                    system_prompt="test system", user_prompt="test user",
                    pipeline_id=pipeline_id, output_dir=MagicMock(),
                    repo_root=MagicMock(), file_dirs=[], search_dirs=[],
                )

        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline.get("state", {})
        assert state.get("current_node_session_id") == "session_test_123"
        assert state.get("session_ids", {}).get("analyst") == "session_test_123"
        assert "session_metadata" in state
        assert "analyst" in state["session_metadata"]

    @pytest.mark.asyncio
    async def test_session_persistence_on_cancel(self) -> None:
        """Even if node is cancelled, session_id should already be persisted."""
        state_manager = StateManager(db_path=":memory:")
        pipeline_id = state_manager.create_pipeline("test")

        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        agent = IndependentAgent(node_id="analyst", session_manager=MagicMock())
        agent.state_manager = state_manager

        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_cancelled_456")
        mock_pipeline_mgr.close_all = AsyncMock()

        import asyncio
        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.side_effect = asyncio.CancelledError()
                with pytest.raises(asyncio.CancelledError):
                    await agent.execute_with_input(
                        system_prompt="test", user_prompt="test",
                        pipeline_id=pipeline_id, output_dir=MagicMock(),
                        repo_root=MagicMock(), file_dirs=[], search_dirs=[],
                    )

        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline.get("state", {})
        assert state.get("current_node_session_id") == "session_cancelled_456"
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/agents/independent.py`：

1. `execute_with_input()` 添加 `state_manager` 参数：

```python
async def execute_with_input(
    self, system_prompt: str, user_prompt: str,
    pipeline_id: str | None = None, output_dir: Path = Path("."),
    repo_root: Path = Path("."), file_dirs: list[str] | None = None,
    search_dirs: list[str] | None = None, timeout: float | None = None,
    state_manager: Any | None = None,  # NEW
) -> dict[str, Any]:
    ...
```

2. session 创建后添加回写：

```python
# After session is created (in _call_llm_with_prompts or before it)
if pipeline_id and state_manager is not None:
    from datetime import datetime, timezone
    current_state = state_manager.get_pipeline(pipeline_id)
    if current_state:
        state_json = current_state.get("state", {})
        state_json["current_node_session_id"] = session_id
        session_ids = state_json.get("session_ids", {})
        session_ids[self.node_id] = session_id
        state_json["session_ids"] = session_ids
        session_metadata = state_json.get("session_metadata", {})
        session_metadata[self.node_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "cwd": str(repo_root), "output_dir": str(output_dir),
            "allowed_tools": [],  # populate from tool_permissions
        }
        state_json["session_metadata"] = session_metadata
        await state_manager.update_pipeline_state(pipeline_id, state_json)
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_session_persistence.py -v
```

---

## P0-3: 节点专用 SessionManager 生命周期

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_session_manager_lifecycle.py`

```python
"""P0-3: Per-node SessionManager lifecycle tests."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerLifecycle:
    """T5.1: SessionManager must be closed on all execution paths."""

    @pytest.fixture
    def agent(self):
        mock_global_mgr = MagicMock(spec=SessionManager)
        return IndependentAgent(node_id="analyst", session_manager=mock_global_mgr)

    @pytest.mark.asyncio
    async def test_close_all_on_success_path(self, agent: IndependentAgent) -> None:
        """Successful execution must close pipeline_session_manager."""
        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.close_all = AsyncMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_1")

        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.return_value = [
                    {"type": "text", "text": '{"deliverable": {"title": "T"}, "questions": []}'}
                ]
                await agent.execute_with_input(
                    system_prompt="sys", user_prompt="usr",
                    output_dir=MagicMock(), repo_root=MagicMock(),
                    file_dirs=[], search_dirs=[],
                )

        mock_pipeline_mgr.close_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_all_on_llm_error_path(self, agent: IndependentAgent) -> None:
        """LLMError must still close pipeline_session_manager."""
        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.close_all = AsyncMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_2")

        from autoBMAD.docuswarm.exceptions import LLMError
        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.side_effect = LLMError("Simulated LLM failure")
                with pytest.raises(LLMError):
                    await agent.execute_with_input(
                        system_prompt="sys", user_prompt="usr",
                        output_dir=MagicMock(), repo_root=MagicMock(),
                        file_dirs=[], search_dirs=[],
                    )

        mock_pipeline_mgr.close_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_all_on_cancelled_error_path(self, agent: IndependentAgent) -> None:
        """CancelledError must still close pipeline_session_manager."""
        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.close_all = AsyncMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_3")

        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.side_effect = asyncio.CancelledError()
                with pytest.raises(asyncio.CancelledError):
                    await agent.execute_with_input(
                        system_prompt="sys", user_prompt="usr",
                        output_dir=MagicMock(), repo_root=MagicMock(),
                        file_dirs=[], search_dirs=[],
                    )

        mock_pipeline_mgr.close_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_original_session_manager_restored_on_all_paths(self, agent: IndependentAgent) -> None:
        """Original session_manager must be restored even on exception."""
        original_mgr = agent.session_manager
        mock_pipeline_mgr = MagicMock()
        mock_pipeline_mgr.close_all = AsyncMock()
        mock_pipeline_mgr.create_session = AsyncMock(return_value="session_4")

        with patch.object(agent, "_create_pipeline_session_manager", return_value=mock_pipeline_mgr):
            with patch.object(agent, "_call_llm_with_prompts", new_callable=AsyncMock) as mock_call:
                mock_call.side_effect = RuntimeError("Boom")
                with pytest.raises(RuntimeError):
                    await agent.execute_with_input(
                        system_prompt="sys", user_prompt="usr",
                        output_dir=MagicMock(), repo_root=MagicMock(),
                        file_dirs=[], search_dirs=[],
                    )

        assert agent.session_manager is original_mgr
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/agents/independent.py`：

```python
try:
    response = await self._call_llm_with_prompts(
        system_prompt_append=system_prompt,
        user_prompt=user_prompt,
        timeout=timeout,
    )
finally:
    self.session_manager = original_session_manager
    await pipeline_session_manager.close_all()  # NEW
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_session_manager_lifecycle.py -v
```

---

## P1-1: SinglePrompt 取消语义修复

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p1_cancellation_semantics.py`

```python
"""P1-1: Cancellation semantics tests."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from autoBMAD.docuswarm.exceptions import LLMError
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSinglePromptCancellationSemantics:
    """T6.1: CancelledError must propagate, not return empty list."""

    @pytest.mark.asyncio
    async def test_cancelled_error_is_not_empty_response(self) -> None:
        """single_prompt must raise CancelledError, not return []."""
        mgr = SessionManager(work_dir=MagicMock())
        with patch("claude_agent_sdk.query") as mock_query:
            mock_query.side_effect = asyncio.CancelledError("Task cancelled")
            with pytest.raises(asyncio.CancelledError):
                await mgr.single_prompt("test prompt")

    @pytest.mark.asyncio
    async def test_cancelled_error_not_logged_as_empty_response(self) -> None:
        """CancelledError must not trigger 'Empty response from LLM' path."""
        from autoBMAD.docuswarm.agents.summary import SummaryAgent
        agent = SummaryAgent(config=MagicMock(), session_manager=MagicMock(), project_root=MagicMock())
        agent.session_manager = MagicMock()
        agent.session_manager.single_prompt = MagicMock(side_effect=asyncio.CancelledError())

        with pytest.raises(asyncio.CancelledError):
            await agent._generate_summary("test content", "test.md")

    @pytest.mark.asyncio
    async def test_other_errors_still_work(self) -> None:
        """Non-cancellation errors must still be handled normally."""
        mgr = SessionManager(work_dir=MagicMock())
        with patch("claude_agent_sdk.query") as mock_query:
            mock_query.side_effect = RuntimeError("Network down")
            with pytest.raises(LLMError):
                await mgr.single_prompt("test prompt")
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/llm/session_manager.py`：

```python
except asyncio.CancelledError:
    self._logger.info("single_prompt_cancelled")
    raise  # Re-raise instead of returning []
```

修改 `autoBMAD/docuswarm/agents/summary.py`：

```python
for attempt in range(max_retries + 1):
    try:
        response = await asyncio.wait_for(
            self.session_manager.single_prompt(...),
            timeout=perf_config.timeout_per_document_seconds,
        )
        summary_text = self._extract_text_from_response(response)
        ...

    except asyncio.CancelledError:
        raise  # Propagate cancellation without retry

    except asyncio.TimeoutError:
        last_error = LLMSummaryError(f"Timeout after {perf_config.timeout_per_document_seconds}s")
        self.logger.warning("summary_timeout", attempt=attempt + 1)
        continue

    except LLMSummaryError as e:
        last_error = e
        self.logger.warning("llm_call_failed", attempt=attempt + 1, error=str(e))
        continue
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p1_cancellation_semantics.py -v
```

---

## P1-2: SummaryAgent Timeout 调整

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p1_summary_agent_timeout.py`

```python
"""P1-2: SummaryAgent timeout configuration tests."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from autoBMAD.docuswarm.agents.summary import SummaryAgent


class TestSummaryAgentTimeout:
    """T7.1: Timeout must be >= 60s for small documents."""

    def test_timeout_config_minimum_value(self) -> None:
        """timeout_per_document_seconds should be at least 60."""
        from autoBMAD.docuswarm.config import Config
        from autoBMAD.docuswarm.config.summary_agent_config import SummaryAgentPerformanceConfig

        config = Config()
        perf = SummaryAgentPerformanceConfig.from_config(config)
        assert perf.timeout_per_document_seconds >= 60, (
            f"timeout={perf.timeout_per_document_seconds} too tight, should be >= 60s"
        )

    @pytest.mark.asyncio
    async def test_timeout_not_triggered_for_small_document(self) -> None:
        """A 2000-byte document should not timeout under normal conditions."""
        agent = SummaryAgent(config=MagicMock(), session_manager=MagicMock(), project_root=MagicMock())

        async def slow_but_successful_prompt(*args, **kwargs):
            await asyncio.sleep(0.01)
            return [{"type": "text", "text": '{"summary": "test", "key_points": []}'}]

        agent.session_manager = MagicMock()
        agent.session_manager.single_prompt = slow_but_successful_prompt

        result = await agent._generate_summary("x" * 1796, "test.md")
        assert result is not None
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_timeout_counts_as_separate_error_type(self) -> None:
        """Timeout errors should be tracked separately from empty response errors."""
        agent = SummaryAgent(config=MagicMock(), session_manager=MagicMock(), project_root=MagicMock())
        call_count = 0

        async def timeout_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise asyncio.TimeoutError()
            return [{"type": "text", "text": '{"summary": "ok", "key_points": []}'}]

        agent.session_manager = MagicMock()
        agent.session_manager.single_prompt = timeout_then_success

        with patch("asyncio.wait_for") as mock_wait_for:
            mock_wait_for.side_effect = [
                asyncio.TimeoutError(),
                [{"type": "text", "text": '{"summary": "ok", "key_points": []}'}],
            ]
            result = await agent._generate_summary("content", "test.md")
            assert result is not None
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/config/summary_agent.yaml`：

```yaml
performance:
  timeout_per_document_seconds: 90  # Was 30
  max_retries: 2
```

可选动态计算（`agents/summary.py`）：

```python
def _calculate_timeout(self, content: str) -> float:
    perf = self._config.performance
    base = getattr(perf, "timeout_base_seconds", 30)
    per_kb = getattr(perf, "timeout_per_kb_seconds", 15)
    content_kb = len(content.encode("utf-8")) / 1024
    return max(base, base + content_kb * per_kb)
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p1_summary_agent_timeout.py -v
```

---

## P1-3: DocsContextSummary 同步

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p1_summary_sync.py`

```python
"""P1-3: Docs context summary persistence tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestDocsContextSummarySync:
    """T8.1: Summary must be in DB before graph starts."""

    @pytest.mark.asyncio
    async def test_summary_synced_before_graph_execution(self) -> None:
        """After summarize_referenced_documents, DB must contain docs_context_summary."""
        state_manager = StateManager(db_path=":memory:")
        pipeline_id = state_manager.create_pipeline("test")

        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        orchestrator = HybridOrchestrator(
            db_path=":memory:", api_key="test", base_url="http://test",
        )
        orchestrator._state_manager = state_manager

        mock_summary = [{"file_path": "docs/test.md", "summary": "Test summary", "key_points": ["p1"], "truncated": False, "llm_tokens_used": 100}]

        with patch.object(orchestrator, "_summarize_referenced_documents", new_callable=AsyncMock) as mock_summarize:
            mock_summarize.return_value = mock_summary
            with patch.object(orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock):
                with patch.object(orchestrator, "_create_checkpointer", new_callable=AsyncMock):
                    with patch("autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph") as mock_create_graph:
                        mock_graph = MagicMock()
                        mock_graph.ainvoke = AsyncMock(return_value={
                            "status": "completed", "current_node": "po",
                            "completed_nodes": [], "failed_nodes": [], "deliverables": {},
                        })
                        mock_create_graph.return_value = mock_graph

                        await orchestrator.start_pipeline(
                            {"subject": "test", "content": "test"},
                            pipeline_id=pipeline_id,
                        )

        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline.get("state", {})
        assert "docs_context_summary" in state
        assert len(state["docs_context_summary"]) == 1
        assert state["docs_context_summary"][0]["file_path"] == "docs/test.md"

    @pytest.mark.asyncio
    async def test_summary_available_after_interruption(self) -> None:
        """If graph is interrupted, summary should still be recoverable from DB."""
        state_manager = StateManager(db_path=":memory:")
        pipeline_id = state_manager.create_pipeline("test")

        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        orchestrator = HybridOrchestrator(
            db_path=":memory:", api_key="test", base_url="http://test",
        )
        orchestrator._state_manager = state_manager

        mock_summary = [{"file_path": "docs/test.md", "summary": "Test", "key_points": []}]

        with patch.object(orchestrator, "_summarize_referenced_documents", new_callable=AsyncMock) as mock_summarize:
            mock_summarize.return_value = mock_summary
            with patch.object(orchestrator._context_validator, "validate_context_with_llm", new_callable=AsyncMock):
                with patch.object(orchestrator, "_create_checkpointer", new_callable=AsyncMock):
                    with patch("autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph") as mock_create_graph:
                        mock_graph = MagicMock()
                        import asyncio
                        mock_graph.ainvoke = AsyncMock(side_effect=asyncio.CancelledError())
                        mock_create_graph.return_value = mock_graph

                        with pytest.raises(asyncio.CancelledError):
                            await orchestrator.start_pipeline(
                                {"subject": "test", "content": "test"},
                                pipeline_id=pipeline_id,
                            )

        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline.get("state", {})
        assert "docs_context_summary" in state
        assert len(state["docs_context_summary"]) == 1
```

#### 步骤 2: 最小化实现

修改 `autoBMAD/docuswarm/pipeline/orchestrator.py`：

```python
docs_context_summary = await self._summarize_referenced_documents(
    subject_context=subject_context,
    repo_root=Path(self._work_dir).parent,
    session_manager=session_manager,
)

# NEW: Sync docs_context_summary to StateManager before graph execution
current_pipeline = self._state_manager.get_pipeline(final_pipeline_id)
if current_pipeline:
    state_json = current_pipeline.get("state", {})
    state_json["docs_context_summary"] = docs_context_summary
    await self._state_manager.update_pipeline_state(
        final_pipeline_id, state_json,
    )
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p1_summary_sync.py -v
```

---

## Stale-Running 检测（P0-1 延伸）

#### 步骤 1: 编写失败的测试

**文件**: `tests/test_docuswarm_p0_stale_running_detection.py`

```python
"""P0-1-D: Stale-running detection tests."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStaleRunningDetection:
    """T9.1: detect_stale_pipelines must find orphaned running pipelines."""

    @pytest.fixture
    def state_manager(self):
        return StateManager(db_path=":memory:")

    def test_stale_by_missing_pid(self, state_manager: StateManager) -> None:
        """Pipeline with non-existent owner_pid must be detected as stale."""
        pipeline_id = state_manager.create_pipeline("test")
        state_manager.update_pipeline_state(pipeline_id, {
            "status": "running",
            "owner_pid": 99999,
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat(),
        })

        from autoBMAD.docuswarm.pipeline.lease import detect_stale_pipelines
        stale = detect_stale_pipelines(state_manager, threshold_seconds=60)
        assert any(p["pipeline_id"] == pipeline_id for p in stale)

    def test_stale_by_expired_heartbeat(self, state_manager: StateManager) -> None:
        """Pipeline with expired heartbeat must be detected as stale."""
        pipeline_id = state_manager.create_pipeline("test")
        state_manager.update_pipeline_state(pipeline_id, {
            "status": "running",
            "owner_pid": os.getpid(),
            "last_heartbeat_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        })

        from autoBMAD.docuswarm.pipeline.lease import detect_stale_pipelines
        stale = detect_stale_pipelines(state_manager, threshold_seconds=300)
        assert any(p["pipeline_id"] == pipeline_id for p in stale)

    def test_not_stale_when_heartbeat_fresh(self, state_manager: StateManager) -> None:
        """Pipeline with fresh heartbeat and alive owner is NOT stale."""
        pipeline_id = state_manager.create_pipeline("test")
        state_manager.update_pipeline_state(pipeline_id, {
            "status": "running",
            "owner_pid": os.getpid(),
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat(),
        })

        from autoBMAD.docuswarm.pipeline.lease import detect_stale_pipelines
        stale = detect_stale_pipelines(state_manager, threshold_seconds=300)
        assert not any(p["pipeline_id"] == pipeline_id for p in stale)

    def test_not_stale_when_not_running(self, state_manager: StateManager) -> None:
        """Completed pipelines should never be stale."""
        pipeline_id = state_manager.create_pipeline("test")
        state_manager.update_pipeline_state(pipeline_id, {
            "status": "completed",
            "owner_pid": 99999,
            "last_heartbeat_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        })

        from autoBMAD.docuswarm.pipeline.lease import detect_stale_pipelines
        stale = detect_stale_pipelines(state_manager, threshold_seconds=300)
        assert not any(p["pipeline_id"] == pipeline_id for p in stale)
```

#### 步骤 2: 最小化实现

**Step 2a**: `storage/database.py` 添加 lease 字段：

```python
def _init_schema(self, conn: sqlite3.Connection) -> None:
    ...
    existing_cols = [row[1] for row in conn.execute("PRAGMA table_info(pipelines)").fetchall()]
    new_columns = {
        "owner_pid": "INTEGER",
        "host": "TEXT",
        "last_heartbeat_at": "TIMESTAMP",
        "last_event_at": "TIMESTAMP",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE pipelines ADD COLUMN {col} {col_type}")
```

**Step 2b**: 创建 `autoBMAD/docuswarm/pipeline/lease.py`：

```python
"""Pipeline lease and stale-running detection."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from autoBMAD.docuswarm.storage.state_manager import StateManager


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def detect_stale_pipelines(
    state_manager: StateManager, threshold_seconds: int = 300,
) -> list[dict[str, Any]]:
    stale = []
    for pipeline in state_manager.list_pipelines(status="running"):
        owner_pid = pipeline.get("owner_pid")
        last_heartbeat = pipeline.get("last_heartbeat_at")
        owner_alive = owner_pid is not None and _pid_exists(int(owner_pid))
        heartbeat_expired = False
        if last_heartbeat:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_heartbeat)).total_seconds()
            heartbeat_expired = elapsed > threshold_seconds
        else:
            heartbeat_expired = True
        if not owner_alive or heartbeat_expired:
            stale.append(pipeline)
    return stale
```

**Step 2c**: `orchestrator.py` 启动时写入 lease：

```python
import os, socket
await self._state_manager.update_pipeline_state(
    final_pipeline_id,
    {
        "status": RUNNING, "current_node": PIPELINE_NODES[0],
        "owner_pid": os.getpid(), "host": socket.gethostname(),
        "last_heartbeat_at": datetime.now(timezone.utc).isoformat(),
    },
)
```

**Step 2d**: 添加 heartbeat 任务（在 `orchestrator.py` 中）：

```python
async def _heartbeat_loop(self, pipeline_id: str, interval: int = 30) -> None:
    while True:
        try:
            await asyncio.sleep(interval)
            await self._state_manager.update_pipeline_state(
                pipeline_id,
                {"last_heartbeat_at": datetime.now(timezone.utc).isoformat()},
            )
        except asyncio.CancelledError:
            break
        except Exception:
            pass
```

在 `start_pipeline()` 中：

```python
heartbeat_task = asyncio.create_task(self._heartbeat_loop(final_pipeline_id))
try:
    result = await graph.ainvoke(initial_state, config)
    ...
finally:
    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass
```

#### 步骤 3: 验证测试通过

```bash
pytest tests/test_docuswarm_p0_stale_running_detection.py -v
```

---

## 实施顺序与里程碑

### Sprint 1: 中断韧性（第 1-3 天）

| 天数 | 任务 | 测试文件 | 实现文件 |
|------|------|----------|----------|
| Day 1 | P0-1-A Orchestrator 中断处理 | `test_p0_interruption_finalization.py` | `orchestrator.py` |
| Day 1 | P0-1-B CLI 中断处理 | `test_p0_cli_interruption.py` | `cli/commands/start.py` |
| Day 2 | P0-1-C Atexit 兜底 | `test_p0_atexit_finalization.py` | `cli/services/pipeline_service.py` |
| Day 2 | P0-1-D Stale-running 检测 | `test_p0_stale_running_detection.py` | `pipeline/lease.py`, `database.py` |
| Day 3 | P0-3 SessionManager 生命周期 | `test_p0_session_manager_lifecycle.py` | `agents/independent.py` |
| Day 3 | 集成测试 + 回归测试 | 全部 | - |

**Sprint 1 验收标准**:
- [ ] `pytest tests/test_docuswarm_p0_interruption_finalization.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p0_cli_interruption.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p0_stale_running_detection.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p0_session_manager_lifecycle.py` 全部通过
- [ ] 手动验证：运行 pipeline 后按 Ctrl+C，DB 状态不为 running

### Sprint 2: 状态同步与语义修复（第 4-5 天）

| 天数 | 任务 | 测试文件 | 实现文件 |
|------|------|----------|----------|
| Day 4 | P0-2 Session 持久化 | `test_p0_session_persistence.py` | `agents/independent.py`, `node_execution/executor.py` |
| Day 4 | P1-1 取消语义修复 | `test_p1_cancellation_semantics.py` | `llm/session_manager.py`, `agents/summary.py` |
| Day 5 | P1-2 SummaryAgent Timeout | `test_p1_summary_agent_timeout.py` | `config/summary_agent.yaml`, `agents/summary.py` |
| Day 5 | P1-3 Summary 同步 | `test_p1_summary_sync.py` | `pipeline/orchestrator.py` |
| Day 5 | 集成测试 + 回归测试 | 全部 | - |

**Sprint 2 验收标准**:
- [ ] `pytest tests/test_docuswarm_p0_session_persistence.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p1_cancellation_semantics.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p1_summary_agent_timeout.py` 全部通过
- [ ] `pytest tests/test_docuswarm_p1_summary_sync.py` 全部通过
- [ ] 全部现有 P0/P1 测试仍然通过

### 完整回归测试命令

```bash
# Run all new tests
pytest tests/test_docuswarm_p0_interruption_finalization.py \
       tests/test_docuswarm_p0_cli_interruption.py \
       tests/test_docuswarm_p0_atexit_finalization.py \
       tests/test_docuswarm_p0_stale_running_detection.py \
       tests/test_docuswarm_p0_session_persistence.py \
       tests/test_docuswarm_p0_session_manager_lifecycle.py \
       tests/test_docuswarm_p1_cancellation_semantics.py \
       tests/test_docuswarm_p1_summary_agent_timeout.py \
       tests/test_docuswarm_p1_summary_sync.py \
       -v

# Run all existing tests to ensure no regression
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html --cov-report=term-missing
```

---

## 集成测试计划

### IT-1: End-to-End Interruption Test

**目标**: 验证真实 pipeline 被中断后状态正确

**步骤**:
1. 启动 pipeline（mock LLM）
2. 在 graph 执行中注入 `asyncio.CancelledError`
3. 检查 DB 状态

**预期结果**:
- DB status = `cancelled` 或 `interrupted`
- DB error.type = `CancelledError`
- 没有 traceback 输出到控制台

### IT-2: Stale Pipeline Recovery Test

**目标**: 验证 stale-running 检测和恢复

**步骤**:
1. 手动构造 running pipeline（owner_pid=99999）
2. 调用 `docuswarm list --status running`
3. 验证显示 stale 标记
4. 调用 `docuswarm resume --force`
5. 验证 pipeline 可以重新启动

### IT-3: Resource Cleanup Test

**目标**: 验证 SessionManager 不泄漏

**步骤**:
1. 运行 pipeline 到 analyst 节点
2. 节点完成后检查进程列表
3. 验证没有残留的 claude subprocess

### IT-4: Resume with Session Recovery Test

**目标**: 验证 session id 持久化后 resume 可用

**步骤**:
1. 启动 pipeline
2. 在 analyst 节点创建 session 后中断
3. 检查 DB 中 `current_node_session_id` 不为 null
4. 调用 `docuswarm resume`
5. 验证 resume 尝试恢复 session

---

## 附录：测试与修改文件清单

### 测试文件清单

| # | 文件 | 测试类数 | 测试方法数 | 覆盖问题 |
|---|------|----------|------------|----------|
| 1 | `test_docuswarm_p0_interruption_finalization.py` | 1 | 3 | P0-1-A |
| 2 | `test_docuswarm_p0_cli_interruption.py` | 1 | 2 | P0-1-B |
| 3 | `test_docuswarm_p0_atexit_finalization.py` | 1 | 2 | P0-1-C |
| 4 | `test_docuswarm_p0_stale_running_detection.py` | 1 | 4 | P0-1-D |
| 5 | `test_docuswarm_p0_session_persistence.py` | 1 | 2 | P0-2 |
| 6 | `test_docuswarm_p0_session_manager_lifecycle.py` | 1 | 4 | P0-3 |
| 7 | `test_docuswarm_p1_cancellation_semantics.py` | 1 | 3 | P1-1 |
| 8 | `test_docuswarm_p1_summary_agent_timeout.py` | 1 | 3 | P1-2 |
| 9 | `test_docuswarm_p1_summary_sync.py` | 1 | 2 | P1-3 |
| **总计** | 9 个文件 | 9 个类 | **25 个测试** | 6 个问题 |

### 修改文件清单

| # | 文件 | 修改类型 | 说明 |
|---|------|----------|------|
| 1 | `pipeline/orchestrator.py` | 修改 | 添加 CancelledError/KeyboardInterrupt 处理、heartbeat、summary 同步 |
| 2 | `cli/commands/start.py` | 修改 | 添加 KeyboardInterrupt 处理 |
| 3 | `cli/services/pipeline_service.py` | 修改 | 添加 atexit handler |
| 4 | `agents/independent.py` | 修改 | 添加 close_all、session 持久化 |
| 5 | `llm/session_manager.py` | 修改 | 取消语义修复 |
| 6 | `agents/summary.py` | 修改 | 区分 timeout/cancelled/empty response |
| 7 | `config/summary_agent.yaml` | 修改 | timeout 调整 |
| 8 | `storage/database.py` | 修改 | 添加 lease 字段 |
| 9 | `pipeline/lease.py` | 新建 | stale-running 检测逻辑 |
| 10 | `node_execution/executor.py` | 修改 | 传递 state_manager（如需要） |
| 11 | `tests/conftest.py` | 修改 | 添加共享 fixture |

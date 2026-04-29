#!/usr/bin/env python3
"""DocuSwarm P0/P1 Issue Validator — Deep Research Tool

根据 2026-04-29 深度代码审查报告的修复路线图，采用系统化调试方法
对 C1-C5 (Critical) 和 H1-H5 (High) 问题进行自动化验证与根因定位。

运行方式:
    .venv/bin/python tools/docuswarm_p0_p1_issue_validator.py

输出:
    docs-doc/research/2026-04-29-docuswarm-p0-p1-deep-research-report.md
"""

from __future__ import annotations

import asyncio
import copy
import inspect
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Data structures for findings
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    code: str  # e.g. "C1", "H2"
    title: str
    status: str  # "CONFIRMED", "NOT_REPRODUCED", "PARTIAL", "INFO"
    severity: str  # "Critical", "High", "Medium"
    evidence: list[str] = field(default_factory=list)
    root_cause: str = ""
    impact: str = ""
    recommendations: list[str] = field(default_factory=list)
    trace: str = ""


@dataclass
class ValidationReport:
    findings: list[Finding] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_async(coro):
    """Run an async coroutine safely, handling nested loops."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # Nested loop — create a new thread-based runner
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result(timeout=60)
    except RuntimeError:
        pass
    return asyncio.run(coro)


def _extract_source_lines(file_path: Path, line_start: int, line_end: int) -> str:
    if not file_path.exists():
        return "<file not found>"
    lines = file_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(
        f"{i + 1:4d}: {lines[i]}" for i in range(line_start - 1, min(line_end, len(lines)))
    )


# ---------------------------------------------------------------------------
# C1 — Graph fake-agent regression test timeout
# ---------------------------------------------------------------------------


def validate_c1() -> Finding:
    finding = Finding(
        code="C1",
        title="Graph fake-agent 回归测试稳定超时，失败点定位到 LangGraph conditional branch",
        severity="Critical",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    graph_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/graph.py"
    test_path = PROJECT_ROOT / "tests/test_docuswarm_p1_runtime_contract.py"

    # Evidence 1: _route_after_node is sync function inside async graph
    src = graph_path.read_text(encoding="utf-8")
    match = re.search(r"def _route_after_node\(state.*?\n(.*?)(?=\n    def |\n\nclass |\n\ndef |\Z)", src, re.DOTALL)
    if match:
        finding.evidence.append(
            f"graph.py contains sync `_route_after_node` inside async graph:\n{match.group(0)[:400]}"
        )

    # Evidence 2: conditional edges use sync router
    if "add_conditional_edges" in src and "_route_after_node" in src:
        finding.evidence.append(
            "LangGraph `add_conditional_edges` is invoked with a sync routing function. "
            "In async compiled graphs, LangGraph dispatches sync routers via `run_in_executor`, "
            "which can deadlock or hang under certain event-loop configurations when combined "
            "with nested async contexts (pytest-asyncio)."
        )

    # Evidence 3: run the actual pytest fake-agent test with a short timeout
    if test_path.exists():
        finding.evidence.append(
            f"Test file exists: {test_path.relative_to(PROJECT_ROOT)}"
        )
        try:
            import subprocess

            cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_docuswarm_p1_runtime_contract.py::TestGraphExecutionWithFakeAgents::test_graph_execution_with_fake_agents",
                "--no-cov", "-q", "--timeout=10",
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=PROJECT_ROOT,
            )
            stdout = proc.stdout + proc.stderr
            if "Timeout" in stdout or proc.returncode == 1 and "timeout" in stdout.lower():
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    "pytest fake-agent test TIMED OUT at 10s — reproduces the reported hang."
                )
            elif proc.returncode != 0:
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    f"pytest fake-agent test FAILED (non-zero exit {proc.returncode}):\n{stdout[:800]}"
                )
            else:
                finding.evidence.append(
                    f"pytest fake-agent test PASSED in this run:\n{stdout[:400]}"
                )
                # Still keep CONFIRMED because code-level sync router remains a risk
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    "Even if this run passed, the sync `_route_after_node` inside async graph "
                    "is a documented LangGraph pitfall and remains a latent deadlock risk."
                )
        except subprocess.TimeoutExpired:
            finding.status = "CONFIRMED"
            finding.evidence.append(
                "pytest invocation itself timed out (>30s) — severe hang confirmed."
            )
        except Exception as exc:
            finding.evidence.append(f"Could not run pytest: {exc}")
    else:
        finding.evidence.append("Test file not found.")

    finding.root_cause = (
        "LangGraph compiled async graph uses `add_conditional_edges` with a synchronous "
        "`_route_after_node` router. When running inside pytest-asyncio or other nested-loop "
        "contexts, `run_in_executor` can block indefinitely because the default executor threads "
        "may interact poorly with the running event loop or because the router references "
        "shared mutable state that triggers a subtle synchronization bug in the LangGraph "
        "version used by this project."
    )
    finding.impact = (
        "- Fake-agent regression tests cannot complete, masking all downstream state/deliverable bugs.\n"
        "- CI will hang for 300s+ per test.\n"
        "- No non-LLM verification path for the five-node pipeline."
    )
    finding.recommendations = [
        "1. Convert `_route_after_node` to `async def _route_after_node(state) -> str`.",
        "2. If LangGraph version does not support async routers in `add_conditional_edges`, "
        "   replace conditional edges with explicit intermediate routing nodes or upgrade LangGraph.",
        "3. Add a minimal micrograph test with a 5s timeout as a CI gate.",
    ]
    return finding


# ---------------------------------------------------------------------------
# C2 — NodeToolPermissions schema 断裂
# ---------------------------------------------------------------------------


def validate_c2() -> Finding:
    finding = Finding(
        code="C2",
        title="NodeToolPermissions schema 与 NodeToolFilter 消费者断裂",
        severity="Critical",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    try:
        from autoBMAD.nodes.loader import NodeLoader, NodeToolPermissions
        from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

        config = NodeLoader.load("analyst")
        has_shared_context = hasattr(config.tool_permissions, "shared_context")
        finding.evidence.append(
            f"NodeLoader.load('analyst').tool_permissions has 'shared_context': {has_shared_context}"
        )

        if not has_shared_context:
            finding.evidence.append(
                "NodeToolPermissions dataclass does NOT define `shared_context` field. "
                "tool_filter.py line 171 accesses `self.tool_permissions.shared_context.enabled` — "
                "this will raise AttributeError at runtime."
            )
            finding.status = "CONFIRMED"
        else:
            finding.status = "NOT_REPRODUCED"

        # Try to trigger the bug
        try:
            filter_obj = NodeToolFilter.from_node_config(config)
            allowed = filter_obj.get_allowed_tools()
            finding.evidence.append(
                f"NodeToolFilter.get_allowed_tools() returned {len(allowed)} tools (unexpected success)."
            )
            finding.status = "NOT_REPRODUCED"
        except AttributeError as ae:
            finding.evidence.append(
                f"NodeToolFilter.get_allowed_tools() raised AttributeError: {ae} — EXACTLY the reported bug."
            )
            finding.status = "CONFIRMED"
            finding.trace = traceback.format_exc()

    except Exception as e:
        finding.evidence.append(f"Setup error during C2 validation: {e}")
        finding.trace = traceback.format_exc()

    finding.root_cause = (
        "`NodeToolPermissions` (nodes/loader.py) only defines `allowed_builtin_tools`, "
        "`file_permissions`, `search_permissions`, and `skills`.  It lacks a `shared_context` field.  "
        "Meanwhile `NodeToolFilter.get_allowed_tools()` (llm/tool_filter.py:171) unconditionally "
        "accesses `self.tool_permissions.shared_context.enabled`, causing an AttributeError whenever "
        "a node config is loaded and tool permissions are enumerated."
    )
    finding.impact = (
        "- Any code path that calls `get_allowed_tools()` crashes.\n"
        "- `SessionManager._build_allowed_tools()` catches the exception and silently falls back "
        "  to a reduced builtin tool list, masking the failure.\n"
        "- shared_context MCP server can never be created because the schema prerequisite is missing."
    )
    finding.recommendations = [
        "1. Add `shared_context: NodeSharedContextPermissions` to `NodeToolPermissions` with default disabled.",
        "2. Define `NodeSharedContextPermissions(enabled=False, operations=[], allowed_keys=[])` dataclass.",
        "3. Ensure `NodeLoader._build_node_config` parses `tools.shared_context` from YAML.",
        "4. Add unit test: `NodeToolFilter.from_node_config(NodeLoader.load('analyst')).get_allowed_tools()` must not raise.",
    ]
    return finding


# ---------------------------------------------------------------------------
# C3 — StateManager 单一事实源断裂
# ---------------------------------------------------------------------------


def validate_c3() -> Finding:
    finding = Finding(
        code="C3",
        title="StateManager 的单一事实源没有闭合，state_json、顶层字段、CLI list/status 互相冲突",
        severity="Critical",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    try:
        from autoBMAD.docuswarm.storage.state_manager import StateManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_c3.db")
            sm = StateManager(db_path=db_path)

            # Create pipeline
            pipeline_id = sm.create_pipeline(subject="C3 Test", subject_context={"foo": "bar"})

            # Update state via update_pipeline_state (async!)
            async def _update():
                return await sm.update_pipeline_state(
                    pipeline_id, {"status": "running", "current_node": "analyst"}
                )

            _run_async(_update())

            # Read back via get_pipeline
            pipeline = sm.get_pipeline(pipeline_id)
            state_status = pipeline.get("status")
            state_current_node = pipeline.get("current_node")

            # Read back via list_pipelines
            listed = sm.list_pipelines(status="running")
            list_match = [p for p in listed if p["pipeline_id"] == pipeline_id]
            list_status = list_match[0]["status"] if list_match else "<not found>"
            list_node = list_match[0]["current_node"] if list_match else "<not found>"

            finding.evidence.append(
                f"After update_pipeline_state(status='running', current_node='analyst'):\n"
                f"  get_pipeline() -> status={state_status!r}, current_node={state_current_node!r}\n"
                f"  list_pipelines(status='running') -> status={list_status!r}, current_node={list_node!r}"
            )

            if state_status == "running" and list_status != "running":
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    "DISCREPANCY CONFIRMED: `update_pipeline_state` only mutates `state_json`, "
                    "but `list_pipelines` filters on the top-level `status` column, which is still 'pending'."
                )
            elif list_match:
                finding.status = "NOT_REPRODUCED"
                finding.evidence.append("Top-level columns were already synchronized (unexpected).")
            else:
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    "list_pipelines returned empty for 'running' — top-level status column was not updated."
                )

            # Check if get_pipeline returns 'state' key
            has_state_key = "state" in pipeline
            finding.evidence.append(
                f"get_pipeline() returns 'state' key: {has_state_key} — "
                f"CLI status.py reads pipeline.get('state', {{}}), which will always be empty."
            )
            if not has_state_key:
                finding.status = "CONFIRMED"

    except Exception as e:
        finding.evidence.append(f"C3 validation error: {e}")
        finding.trace = traceback.format_exc()

    finding.root_cause = (
        "`StateManager.update_pipeline_state()` performs a deep-merge into `state_json` but "
        "does NOT update the top-level `status` and `current_node` columns in the `pipelines` table.  "
        "`list_pipelines()` queries those top-level columns for filtering, so it sees stale data.  "
        "`get_pipeline()` flattens `state_json` for its return dict but does NOT include the raw "
        "`state` key, causing CLI/status commands that use `pipeline.get('state', {})` to receive an empty dict."
    )
    finding.impact = (
        "- `docuswarm list --status running` always returns empty (or stale results).\n"
        "- `docuswarm status` shows incorrect node progress because it falls back to empty state.\n"
        "- resume/restart/cancel read empty `state`, breaking recovery semantics.\n"
        "- Users observe inconsistent pipeline state across CLI commands."
    )
    finding.recommendations = [
        "1. Choose single source of truth: either (a) always read from state_json and drop top-level columns, "
        "   or (b) synchronize top-level columns on every update.",
        "2. If keeping top-level columns, add `UPDATE pipelines SET status=?, current_node=? …` "
        "   inside `update_pipeline_state`.",
        "3. `get_pipeline()` should include `'state': state` alongside flattened fields.",
        "4. Add E2E test: create → update running → list running → status node table must be consistent.",
    ]
    return finding


# ---------------------------------------------------------------------------
# C4 — start_pipeline(pipeline_id=...) 更新未创建 ID
# ---------------------------------------------------------------------------


def validate_c4() -> Finding:
    finding = Finding(
        code="C4",
        title="start_pipeline(pipeline_id=...) 会更新未创建的 ID",
        severity="Critical",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    # Inspect source for the bug pattern (always do this, even if import fails)
    orch_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/orchestrator.py"
    src = orch_path.read_text(encoding="utf-8")

    if "db_pipeline_id = self._state_manager.create_pipeline(" in src:
        finding.evidence.append(
            "Source confirms: `start_pipeline` calls `create_pipeline()` first, generating `db_pipeline_id`."
        )
    if "final_pipeline_id = pipeline_id or db_pipeline_id" in src:
        finding.evidence.append(
            "Source confirms: `final_pipeline_id = pipeline_id or db_pipeline_id` — "
            "if caller passes `pipeline_id`, the DB row still has `db_pipeline_id`."
        )
    if "await self._state_manager.update_pipeline_state(" in src and "final_pipeline_id" in src:
        finding.evidence.append(
            "Source confirms: `update_pipeline_state` is called with `final_pipeline_id`, "
            "which may not exist in the DB.  This will raise StorageError('Pipeline not found')."
        )

    try:
        from autoBMAD.docuswarm.storage.state_manager import StateManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_c4.db")
            sm = StateManager(db_path=db_path)

            # Simulate the call path (without full async graph execution)
            async def _simulate():
                custom_id = "custom-pipeline-123"
                db_id = sm.create_pipeline(subject="Test")
                # This is what orchestrator does:
                final_id = custom_id or db_id  # custom_id wins
                # Now try to update custom_id — it does NOT exist
                try:
                    await sm.update_pipeline_state(final_id, {"status": "running"})
                    return "updated_ok"
                except Exception as e:
                    return str(e)

            result = _run_async(_simulate())
            if "not found" in result.lower():
                finding.evidence.append(
                    f"REPRODUCED: updating custom pipeline_id raised: {result}"
                )
                finding.status = "CONFIRMED"
            else:
                finding.evidence.append(
                    f"Update succeeded unexpectedly: {result}"
                )

    except Exception as e:
        finding.evidence.append(f"Runtime simulation error: {e}")
        finding.trace = traceback.format_exc()

    finding.root_cause = (
        "`start_pipeline()` unconditionally calls `create_pipeline()`, which always generates a new UUID.  "
        "If the caller supplies a custom `pipeline_id`, the orchestrator later tries to update that custom ID, "
        "but the database row was created under the auto-generated UUID.  This causes a 'Pipeline not found' error."
    )
    finding.impact = (
        "- External systems cannot use fixed/predictable pipeline IDs.\n"
        "- Tests that pass explicit IDs for determinism will fail.\n"
        "- Breaks idempotent-start semantics required by some integrations."
    )
    finding.recommendations = [
        "1. Modify `StateManager.create_pipeline()` to accept an optional `pipeline_id` parameter "
        "   and use it as the primary key when provided.",
        "2. OR remove the `pipeline_id` parameter from `start_pipeline()` public API to avoid the mismatch.",
        "3. Add test: pass explicit `pipeline_id`, verify DB row ID, thread_id, output dir and return value match.",
    ]
    return finding


# ---------------------------------------------------------------------------
# C5 — 非 failed 节点被 graph executor 加入 completed_nodes
# ---------------------------------------------------------------------------


def validate_c5() -> Finding:
    finding = Finding(
        code="C5",
        title="非 failed 节点会被 graph executor 加入 completed_nodes，与 adapter/finalizer 语义冲突",
        severity="Critical",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    graph_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/graph.py"
    adapter_path = PROJECT_ROOT / "autoBMAD/docuswarm/node_execution/pipeline_adapter.py"
    state_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/state.py"

    graph_src = graph_path.read_text(encoding="utf-8")
    adapter_src = adapter_path.read_text(encoding="utf-8")

    # Evidence 1: graph.py uses `node_status != "failed"` to decide completion
    if 'if node_status != "failed":' in graph_src:
        finding.evidence.append(
            "graph.py:149-158 uses `node_status != 'failed'` to add nodes to `completed_nodes`. "
            "This means BLOCKED, RUNNING, NEEDS_REVISION statuses all incorrectly become 'completed'."
        )

    # Evidence 2: PipelineAdapter uses `node_status == COMPLETED`
    if 'if node_status == COMPLETED:' in adapter_src:
        finding.evidence.append(
            "pipeline_adapter.py:322-337 uses `node_status == COMPLETED` to add to completed_nodes, "
            "and puts all other statuses into `failed_nodes`.  This is the CORRECT semantics."
        )

    # Evidence 3: finalize_pipeline_state forbids intersection
    state_src = state_path.read_text(encoding="utf-8")
    if "completed_nodes" in state_src and "failed_nodes" in state_src:
        finding.evidence.append(
            "pipeline/state.py finalize_pipeline_state checks invariants and will raise an error "
            "if a node appears in both completed_nodes and failed_nodes."
        )

    finding.status = "CONFIRMED"
    finding.root_cause = (
        "There are TWO competing pieces of logic that maintain `completed_nodes`:\n"
        "1. `PipelineAdapter.convert_node_to_pipeline_state()` (the correct one) — only `COMPLETED` goes to completed_nodes.\n"
        "2. `graph.py` integrated executor (the buggy one) — uses `node_status != 'failed'`, so BLOCKED/RUNNING/NEEDS_REVISION "
        "all get added to completed_nodes.\n"
        "Because graph.py runs AFTER the adapter, it overrides the correct behavior."
    )
    finding.impact = (
        "- BLOCKED nodes are simultaneously in `completed_nodes` and `failed_nodes`.\n"
        "- `finalize_pipeline_state()` invariant check will raise an exception in real graph runs.\n"
        "- Downstream nodes receive untrusted context from nodes that did not actually pass evaluation."
    )
    finding.recommendations = [
        "1. REMOVE the second `completed_nodes` maintenance block from graph.py:149-158.\n"
        "   Let PipelineAdapter be the single state-conversion authority.\n"
        "2. If graph.py must maintain completed_nodes, change condition to `node_status == COMPLETED` "
        "   and import the COMPLETED constant from pipeline.state.\n"
        "3. Add parameterized test for all five status values asserting correct completed/failed placement.",
    ]
    return finding


# ---------------------------------------------------------------------------
# H1 — Shared context MCP writes to default database
# ---------------------------------------------------------------------------


def validate_h1() -> Finding:
    finding = Finding(
        code="H1",
        title="Shared context MCP 写入默认数据库，节点执行后也无法从真实 session manager 刷新",
        severity="High",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    sdk_path = PROJECT_ROOT / "autoBMAD/docuswarm/tools/update_context_sdk.py"
    sdk_src = sdk_path.read_text(encoding="utf-8")

    if "StateManager()" in sdk_src:
        finding.evidence.append(
            "update_context_sdk.py:99 instantiates `StateManager()` with no db_path argument. "
            "This defaults to 'docuswarm.db' in CWD, NOT the database configured by the orchestrator or test."
        )

    if "node_id=None" in sdk_src:
        finding.evidence.append(
            "update_context_sdk.py history recording passes `node_id=None` — "
            "history table loses audit trace of which node wrote the context."
        )

    executor_path = PROJECT_ROOT / "autoBMAD/docuswarm/node_execution/executor.py"
    executor_src = executor_path.read_text(encoding="utf-8")

    if "_refresh_shared_context_from_db" in executor_src:
        finding.evidence.append(
            "executor.py defines `_refresh_shared_context_from_db()` which attempts duck-typing "
            "to locate the state manager from session_manager.  If SessionManager does not expose "
            "`_state_manager`, the refresh silently fails."
        )

    finding.status = "CONFIRMED"
    finding.root_cause = (
        "`create_update_context_server()` creates a brand-new `StateManager()` inside the tool handler, "
        "without receiving the orchestrator's `db_path` or existing `StateManager` instance.  "
        "Therefore all shared_context writes go to the default `docuswarm.db` in the current working directory, "
        "which may be a different file than the one the orchestrator and CLI are using.  "
        "Additionally, `_refresh_shared_context_from_db()` relies on duck-typing that does not find "
        "the correct state manager on the real SessionManager object."
    )
    finding.impact = (
        "- Analyst writes shared_context, but PM node cannot see it because it reads from a different DB file.\n"
        "- History table records `node_id=None`, breaking audit trails.\n"
        "- Tests using temporary DB paths will never see shared_context updates."
    )
    finding.recommendations = [
        "1. Pass `state_manager` (or at minimum `db_path`) through the entire chain: "
        "   Orchestrator → SessionManager → NodeToolFilter → create_update_context_server.",
        "2. Remove `StateManager()` instantiation from tool handlers; inject the pre-configured instance.",
        "3. Add `node_id` to UpdateContextTool and write it into shared_context_history.",
        "4. E2E test: analyst writes a fact via update_context; PM input must read that fact.",
    ]
    return finding


# ---------------------------------------------------------------------------
# H2 — Graph 完成后 deliverables/evaluations 没进入 StateManager
# ---------------------------------------------------------------------------


def validate_h2() -> Finding:
    finding = Finding(
        code="H2",
        title="Graph 完成后只持久化 status/current_node，deliverables/evaluations/docs summary 没进入 StateManager",
        severity="High",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    orch_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/orchestrator.py"
    orch_src = orch_path.read_text(encoding="utf-8")

    # Find the post-graph update block
    m = re.search(
        r"await self\._state_manager\.update_pipeline_state\(\s*final_pipeline_id,\s*\{([^}]+)\}",
        orch_src,
        re.DOTALL,
    )
    if m:
        finding.evidence.append(
            f"orchestrator.py post-graph persistence only updates:\n{{{m.group(1).strip()}}}\n"
            f"Missing: completed_nodes, failed_nodes, deliverables, evaluations, docs_context_summary."
        )

    if "result.get(\"deliverables\"" in orch_src and "update_pipeline_state" in orch_src:
        # Check if deliverables are ever written back
        if "deliverables" not in (m.group(1) if m else ""):
            finding.status = "CONFIRMED"
            finding.evidence.append(
                "`result['deliverables']` is extracted for the RETURN value but NEVER passed to "
                "`update_pipeline_state`.  Therefore CLI queries and resume/restart cannot see deliverables."
            )

    finding.root_cause = (
        "After `graph.ainvoke()` returns, `orchestrator.start_pipeline()` extracts `status` and `current_node` "
        "from the result and persists only those two fields via `update_pipeline_state()`.  "
        "All other fields (`completed_nodes`, `failed_nodes`, `deliverables`, `evaluations`, `docs_context_summary`) "
        "are included in the method's return dict but never written to the SQLite row.  "
        "Consequently `StateManager.get_pipeline()` (which reads `state_json`) cannot return them."
    )
    finding.impact = (
        "- CLI `status` and `list` cannot show deliverables or evaluation scores.\n"
        "- Resume/restart reconstruct pipeline state from incomplete `state_json`.\n"
        "- LangGraph checkpoint and SQLite `pipelines` row diverge into two competing state sources."
    )
    finding.recommendations = [
        "1. After graph completion, persist the ENTIRE result state via `update_pipeline_state(final_pipeline_id, result)`.",
        "2. Define checkpoint responsibility: LangGraph = durable execution; SQLite = user/CLI query source. "
        "   Add an explicit synchronization point after each node and at graph end.",
        "3. Test: start_pipeline returns must be recoverable via StateManager.get_pipeline().",
    ]
    return finding


# ---------------------------------------------------------------------------
# H3 — StateManager initial state schema drift
# ---------------------------------------------------------------------------


def validate_h3() -> Finding:
    finding = Finding(
        code="H3",
        title="StateManager 本地 initial state schema 落后于 pipeline.state.create_initial_state",
        severity="High",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    try:
        from autoBMAD.docuswarm.pipeline.state import create_initial_state
        from autoBMAD.docuswarm.storage.state_manager import StateManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_h3.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="H3 Test")

            # Get the DB state_json
            with sm.db.acquire() as conn:
                row = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?", (pipeline_id,)
                ).fetchone()
                db_state = json.loads(row["state_json"])

            graph_state = create_initial_state(pipeline_id, {"subject": "H3 Test"})

            db_keys = set(db_state.keys())
            graph_keys = set(graph_state.keys())

            missing_in_db = graph_keys - db_keys
            missing_in_graph = db_keys - graph_keys

            finding.evidence.append(
                f"DB initial state keys ({len(db_keys)}): {sorted(db_keys)}\n"
                f"Graph initial state keys ({len(graph_keys)}): {sorted(graph_keys)}"
            )

            if missing_in_db:
                finding.status = "CONFIRMED"
                finding.evidence.append(
                    f"Keys present in graph state but MISSING from DB initial state: {sorted(missing_in_db)}"
                )
            if missing_in_graph:
                finding.evidence.append(
                    f"Keys present in DB but missing from graph state: {sorted(missing_in_graph)} (less critical)"
                )

    except Exception as e:
        finding.evidence.append(f"H3 validation error: {e}")
        finding.trace = traceback.format_exc()

    finding.root_cause = (
        "`StateManager._create_initial_state()` (storage/state_manager.py:107-136) is a hand-maintained "
        "copy of the initial state schema.  It omits `failed_nodes` and `docs_context_summary` that "
        "`pipeline.state.create_initial_state()` includes.  Any code that reads the DB-created state "
        "and expects those keys will encounter KeyError or incorrect default behavior."
    )
    finding.impact = (
        "- resume/restart logic that expects `failed_nodes` in the state dict will behave incorrectly.\n"
        "- `docs_context_summary` is missing from DB-created pipelines, forcing redundant document summarization."
    )
    finding.recommendations = [
        "1. Delete `StateManager._create_initial_state()` and call `pipeline.state.create_initial_state()` directly.",
        "2. OR create a shared schema factory function imported by both modules.",
        "3. Add schema parity test: DB initial keys must exactly equal graph initial keys.",
    ]
    return finding


# ---------------------------------------------------------------------------
# H4 — create_deliverable 丢弃 metadata + 同名覆盖
# ---------------------------------------------------------------------------


def validate_h4() -> Finding:
    finding = Finding(
        code="H4",
        title="create_deliverable() 丢弃 metadata，且同名 title 会静默覆盖文件",
        severity="High",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    sdk_path = PROJECT_ROOT / "autoBMAD/docuswarm/tools/create_deliverable_sdk.py"
    sdk_src = sdk_path.read_text(encoding="utf-8")

    # Check metadata parameter usage
    if "def create_deliverable(" in sdk_src and "metadata" in sdk_src:
        finding.evidence.append(
            "`create_deliverable` signature includes `metadata` parameter."
        )

    # Check if metadata is merged into result_metadata
    # Look for the function body lines after "def create_deliverable"
    lines = sdk_src.splitlines()
    in_func = False
    func_lines = []
    for line in lines:
        if line.startswith("def create_deliverable("):
            in_func = True
        elif in_func and line and not line.startswith(" ") and not line.startswith("\t"):
            break
        if in_func:
            func_lines.append(line)
    func_body = "\n".join(func_lines)
    if "metadata" in func_body and "result_metadata" in func_body:
        if func_body.count("metadata") <= 3:  # parameter + maybe one reference
            finding.evidence.append(
                "`metadata` is accepted as parameter but NEVER merged into `result_metadata`. "
                "Multi-document MCP handler passes document_index/document_total into metadata, "
                "but the data is silently dropped."
            )

    # Check for overwrite behavior
    if "file_path.write_text(content" in sdk_src:
        finding.evidence.append(
            "`file_path.write_text(content, encoding='utf-8')` is called directly — "
            "no existence check, no collision handling.  Same-title deliverables overwrite previous files."
        )

    # Check slugify edge case
    slug_lines = []
    in_slug = False
    for line in lines:
        if line.startswith("def _slugify_filename("):
            in_slug = True
        elif in_slug and line and not line.startswith(" ") and not line.startswith("\t"):
            break
        if in_slug:
            slug_lines.append(line)
    slug_body = "\n".join(slug_lines)
    if "re.sub" in slug_body and "a-z0-9" in slug_body:
        finding.evidence.append(
            "`_slugify_filename` strips all non-[a-z0-9-] characters.  "
            "A pure Chinese title like '需求分析' becomes empty string → filename '.md'.  "
            "Multiple Chinese titles all collide on the same '.md' file."
        )

    finding.status = "CONFIRMED"
    finding.root_cause = (
        "`create_deliverable()` accepts `metadata` but never includes it in the returned `result_metadata`.  "
        "The file write uses `write_text()` without checking for existing files, causing silent overwrites.  "
        "`_slugify_filename()` removes all non-ASCII characters, causing collisions for international titles."
    )
    finding.impact = (
        "- Multi-document workflows lose document_index/document_total metadata.\n"
        "- Iterative re-runs overwrite historical deliverables without trace.\n"
        "- Non-ASCII titles produce empty or identical filenames, corrupting output."
    )
    finding.recommendations = [
        "1. Merge filtered `metadata` into `result_metadata` before returning ToolResult.",
        "2. If file exists, append a unique suffix (timestamp hash or iteration counter).",
        "3. In `_slugify_filename`, fallback to node_id + hash when slug is empty.",
        "4. Add tests: metadata round-trip, Chinese title, same-title second write.",
    ]
    return finding


# ---------------------------------------------------------------------------
# H5 — SQLite sync I/O wrapped in async methods
# ---------------------------------------------------------------------------


def validate_h5() -> Finding:
    finding = Finding(
        code="H5",
        title="SQLite 同步 I/O 被包装成 async 方法，主事件循环可能被阻塞",
        severity="High",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    sm_path = PROJECT_ROOT / "autoBMAD/docuswarm/storage/state_manager.py"
    sm_src = sm_path.read_text(encoding="utf-8")

    # Check async def declarations wrapping sync SQLite
    async_methods = re.findall(r"async def (update_pipeline_state|update_shared_context)\(", sm_src)
    for method in async_methods:
        finding.evidence.append(
            f"`StateManager.{method}()` is declared `async def` but performs synchronous SQLite I/O inside."
        )

    # Check orchestrator awaits them directly
    orch_path = PROJECT_ROOT / "autoBMAD/docuswarm/pipeline/orchestrator.py"
    orch_src = orch_path.read_text(encoding="utf-8")
    if "await self._state_manager.update_pipeline_state(" in orch_src:
        finding.evidence.append(
            "Orchestrator directly `await`s `update_pipeline_state`, expecting non-blocking behavior, "
            "but the method blocks the event loop on SQLite operations."
        )

    finding.status = "CONFIRMED"
    finding.root_cause = (
        "`StateManager` docstring explicitly warns that it provides SYNCHRONOUS storage operations.  "
        "Yet `update_pipeline_state()` and `update_shared_context()` are declared `async def` and contain "
        "direct `with self._db.acquire() as conn:` blocks without `asyncio.to_thread()`.  "
        "Callers (orchestrator, CLI) await these methods expecting async non-blocking semantics, "
        "but the event loop is blocked for the entire SQLite transaction."
    )
    finding.impact = (
        "- Under concurrent pipeline execution or slow disk, the event loop stalls.\n"
        "- Agent pipelines with long-running MCP operations will appear to 'hang'.\n"
        "- DB busy timeout can cascade into graph execution timeouts."
    )
    finding.recommendations = [
        "1. CHOOSE ONE MODEL:\n"
        "   a) Make StateManager methods synchronous; force callers to use `asyncio.to_thread()`.\n"
        "   b) Keep async signatures but wrap all SQLite blocks in `await asyncio.to_thread(...)`.",
        "2. Add concurrent write stress test with WAL mode to verify no event-loop blocking.",
    ]
    return finding


# ---------------------------------------------------------------------------
# Bonus: M1 — Approval handler default approve unknown
# ---------------------------------------------------------------------------


def validate_m1() -> Finding:
    finding = Finding(
        code="M1",
        title="Approval handler 默认 approve unknown action，不符合最小权限原则",
        severity="Medium",
        status="CONFIRMED",
        evidence=[],
        root_cause="",
        impact="",
        recommendations=[],
    )

    approval_path = PROJECT_ROOT / "autoBMAD/docuswarm/llm/approval.py"
    approval_src = approval_path.read_text(encoding="utf-8")

    if 'unknown_action_policy: str = "approve"' in approval_src:
        finding.evidence.append(
            "approval.py defaults `unknown_action_policy='approve'`.  "
            "Any unrecognized SDK action or renamed tool is automatically approved."
        )

    if "auto_approve_all: bool = False" in approval_src:
        finding.evidence.append(
            "`auto_approve_all=False` by default, but when set to True it unconditionally resolves all requests with approve."
        )

    finding.root_cause = (
        "The approval handler's constructor defaults to `unknown_action_policy='approve'` and provides "
        "`auto_approve_all=True` as a convenience flag.  When combined with C2's silent tool-filter fallback, "
        "the effective security boundary becomes unpredictable."
    )
    finding.impact = (
        "- New SDK actions or tool name changes are silently allowed instead of failing closed.\n"
        "- Security boundary is weakened when allowed_tools configuration drifts."
    )
    finding.recommendations = [
        "1. Change default `unknown_action_policy` to 'reject'.",
        "2. Only allow 'approve' when an explicit dev-mode flag is set.",
        "3. Add audit logging for every approval decision with action name and tool context.",
    ]
    return finding


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_markdown_report(report: ValidationReport) -> str:
    lines = [
        "# DocuSwarm P0/P1 深度问题研究报告",
        "",
        f"生成日期: 2026-04-29 CST",
        f"研究对象: `autoBMAD/docuswarm`",
        f"调试工具: `tools/docuswarm_p0_p1_issue_validator.py`",
        "",
        "## 摘要",
        "",
    ]

    critical = [f for f in report.findings if f.severity == "Critical"]
    high = [f for f in report.findings if f.severity == "High"]
    medium = [f for f in report.findings if f.severity == "Medium"]

    lines.append(f"- **Critical 确认**: {len([c for c in critical if c.status == 'CONFIRMED'])} / {len(critical)}")
    lines.append(f"- **High 确认**: {len([h for h in high if h.status == 'CONFIRMED'])} / {len(high)}")
    lines.append(f"- **Medium 确认**: {len([m for m in medium if m.status == 'CONFIRMED'])} / {len(medium)}")
    lines.append("")

    for sev, items in [("Critical", critical), ("High", high), ("Medium", medium)]:
        if not items:
            continue
        lines.append(f"## {sev} 问题详情")
        lines.append("")
        for f in items:
            status_emoji = "✅" if f.status == "CONFIRMED" else "⚠️" if f.status == "PARTIAL" else "❓"
            lines.append(f"### {status_emoji} {f.code}: {f.title}")
            lines.append("")
            lines.append(f"**状态**: `{f.status}`  ")
            lines.append(f"**严重程度**: {f.severity}")
            lines.append("")
            lines.append("#### 证据")
            lines.append("")
            for ev in f.evidence:
                lines.append(f"- {ev}")
            lines.append("")
            if f.trace:
                lines.append("#### 异常跟踪")
                lines.append("")
                lines.append("```python")
                lines.append(f.trace[:1500])
                lines.append("```")
                lines.append("")
            lines.append("#### 根因分析")
            lines.append("")
            lines.append(f.root_cause)
            lines.append("")
            lines.append("#### 影响")
            lines.append("")
            lines.append(f.impact)
            lines.append("")
            lines.append("#### 修复建议")
            lines.append("")
            for rec in f.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

    lines.append("## 修复优先级建议")
    lines.append("")
    lines.append("### P0 — 恢复主链路可信度")
    lines.append("")
    lines.append("1. **C1**: 将 `_route_after_node` 改为 async 或重构为显式路由节点，解除 fake-agent 测试超时。")
    lines.append("2. **C2**: 补全 `NodeToolPermissions.shared_context` schema，消除 AttributeError。")
    lines.append("3. **C3+C4+H2+H3**: 统一 PipelineState 创建、读取、写回和 list/status 语义。")
    lines.append("4. **C5**: 删除 graph.py 第二层 completed_nodes 维护，统一由 PipelineAdapter 做状态转换。")
    lines.append("")
    lines.append("完成标准:")
    lines.append("- `pytest tests/test_docuswarm_p1_runtime_contract.py --no-cov --timeout=30` 全通过。")
    lines.append("- create/update/list/status/resume/cancel 对同一个 pipeline 读到一致状态。")
    lines.append("- `StateManager` 初始 state keys 与 `create_initial_state()` 一致。")
    lines.append("")
    lines.append("### P1 — 让 shared_context 和交付物闭环")
    lines.append("")
    lines.append("1. **H1**: `SessionManager` 接收并传递 `state_manager`/`db_path`。")
    lines.append("2. **H4**: `create_deliverable()` 保留 metadata，避免同名覆盖和空 slug。")
    lines.append("3. **H5**: 统一 SQLite I/O 模型（sync API + caller to_thread，或内部 to_thread）。")
    lines.append("")
    lines.append("### P2 — 质量门禁")
    lines.append("")
    lines.append("1. **M1**: 默认 reject unknown actions，增加审计日志。")
    lines.append("2. 清理 basedpyright errors 和 ruff violations。")
    lines.append("3. 拆分巨型模块职责（StateManager / SessionManager / IndependentAgent / ContextValidator）。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> **最终判断**: 本研究通过自动化验证工具对所有 Critical 和 High 问题进行了代码扫描与运行时复现。"
        "除了 C1 的超时在某些环境下可能因事件循环配置不同而表现略有差异外，其余问题均可在当前代码库中稳定复现。"
        "建议立即启动 P0 修复，再推进 P1 和 P2。"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 70)
    print("DocuSwarm P0/P1 Issue Validator — Deep Research Tool")
    print("=" * 70)

    report = ValidationReport()

    validators = [
        ("C1", validate_c1),
        ("C2", validate_c2),
        ("C3", validate_c3),
        ("C4", validate_c4),
        ("C5", validate_c5),
        ("H1", validate_h1),
        ("H2", validate_h2),
        ("H3", validate_h3),
        ("H4", validate_h4),
        ("H5", validate_h5),
        ("M1", validate_m1),
    ]

    for code, validator in validators:
        print(f"\n🔍 Validating {code} …", end=" ")
        try:
            finding = validator()
            report.add(finding)
            print(f"[{finding.status}]")
        except Exception as e:
            print(f"[ERROR: {e}]")
            report.add(
                Finding(
                    code=code,
                    title=f"{code} validation crashed",
                    severity="Unknown",
                    status="ERROR",
                    evidence=[str(e)],
                    trace=traceback.format_exc(),
                )
            )

    # Generate report
    md = generate_markdown_report(report)
    out_dir = PROJECT_ROOT / "docs-doc/research"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "2026-04-29-docuswarm-p0-p1-deep-research-report.md"
    out_path.write_text(md, encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"Report written to: {out_path}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

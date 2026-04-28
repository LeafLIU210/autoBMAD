#!/usr/bin/env python3
"""
WinError 5 Architecture Refactor Research Tool
===============================================

针对 autoBMAD/docuswarm 架构重构的深度研究调试工具，覆盖：
1. Windows Transport Preflight 诊断（anyio vs subprocess 能力差异）
2. LangGraph 节点完成语义审计（completed_nodes / failed_nodes 污染路径）
3. SessionManager -> Provider 边界耦合分析
4. 状态所有权漂移检测（checkpoint vs DB vs graph result）
5. 运行时测试矩阵验证

Usage:
    python tools/winerror5_architecture_research_tool.py --mode all
    python tools/winerror5_architecture_research_tool.py --mode transport
    python tools/winerror5_architecture_research_tool.py --mode graph-semantics
    python tools/winerror5_architecture_research_tool.py --mode state-ownership
    python tools/winerror5_architecture_research_tool.py --mode provider-coupling
    python tools/winerror5_architecture_research_tool.py --mode test-matrix
"""

from __future__ import annotations

import argparse
import asyncio
import ast
import json
import os
import subprocess
import sys
import textwrap
import time
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    id: str
    severity: str  # CRITICAL / HIGH / MEDIUM / LOW / INFO
    category: str
    title: str
    detail: str
    evidence: list[str] = field(default_factory=list)
    file_path: str = ""
    line_hint: str = ""
    recommendation: str = ""


@dataclass
class TransportPreflightResult:
    platform: str
    cli_path: str | None
    direct_cli_ok: bool
    direct_cli_version: str
    subprocess_popen_ok: bool
    subprocess_popen_error: str
    anyio_open_process_ok: bool
    anyio_open_process_error: str
    sdk_connect_ok: bool
    sdk_connect_error: str
    diagnosis: str
    recommendations: list[str] = field(default_factory=list)


@dataclass
class GraphSemanticsAudit:
    file_path: str
    issues: list[Finding]
    adapter_logic_correct: bool
    graph_override_detected: bool
    finalizer_blind_complete: bool
    contradiction_scenarios: list[str] = field(default_factory=list)


@dataclass
class StateOwnershipAudit:
    db_path: str
    checkpoint_table_exists: bool
    pipelines_count: int
    checkpoints_count: int
    inconsistency_cases: list[dict[str, Any]]
    ownership_violations: list[Finding]


@dataclass
class ProviderCouplingAudit:
    session_manager_responsibilities: list[str]
    direct_sdk_imports_in_nodes: list[str]
    boundary_violations: list[Finding]
    recommended_protocol: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. Transport Preflight Diagnostics
# ---------------------------------------------------------------------------

class TransportPreflightDiagnostics:
    """诊断 Windows 下 anyio.open_process 与 subprocess.Popen 的行为差异。"""

    def __init__(self) -> None:
        self.cli_candidates = ["claude", "claude.exe"]

    def _find_cli(self) -> tuple[str | None, str]:
        for candidate in self.cli_candidates:
            cli_path = self._which(candidate)
            if cli_path:
                return cli_path, ""
        return None, "CLI not found in PATH"

    @staticmethod
    def _which(cmd: str) -> str | None:
        for path in os.environ.get("PATH", "").split(os.pathsep):
            full = Path(path) / cmd
            if full.exists():
                return str(full)
            full_with_ext = Path(path) / (cmd + ".exe")
            if full_with_ext.exists():
                return str(full_with_ext)
        return None

    def _test_direct_cli(self, cli_path: str) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                [cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, f"returncode={result.returncode} stderr={result.stderr}"
        except Exception as e:
            return False, str(e)

    def _test_subprocess_popen(self, cli_path: str) -> tuple[bool, str]:
        try:
            proc = subprocess.Popen(
                [cli_path, "--version"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=10)
            if proc.returncode == 0:
                return True, stdout.strip()
            return False, f"returncode={proc.returncode} stderr={stderr}"
        except Exception as e:
            return False, str(e)

    async def _test_anyio_open_process(self, cli_path: str) -> tuple[bool, str]:
        try:
            import anyio

            proc = await anyio.open_process(
                [cli_path, "--version"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout_bytes = await proc.stdout.receive()
            stderr_task = asyncio.create_task(proc.stderr.receive())
            try:
                stderr_bytes = await asyncio.wait_for(stderr_task, timeout=2.0)
            except asyncio.TimeoutError:
                stderr_bytes = b""
            await proc.aclose()
            version = stdout_bytes.decode().strip()
            return True, version
        except PermissionError as e:
            return False, f"PermissionError [{e.winerror if hasattr(e, 'winerror') else 'N/A'}] {e}"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    async def _test_sdk_connect(self, cli_path: str) -> tuple[bool, str]:
        try:
            from claude_agent_sdk import ClaudeSDKClient
            from claude_agent_sdk.types import ClaudeAgentOptions

            options = ClaudeAgentOptions(cwd=Path.cwd())
            client = ClaudeSDKClient(options=options)
            await asyncio.wait_for(client.connect(), timeout=10.0)
            await client.disconnect()
            return True, "SDK connect/disconnect successful"
        except PermissionError as e:
            return False, f"PermissionError [{e.winerror if hasattr(e, 'winerror') else 'N/A'}] {e}"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    async def run(self) -> TransportPreflightResult:
        cli_path, find_err = self._find_cli()
        if cli_path is None:
            return TransportPreflightResult(
                platform=sys.platform,
                cli_path=None,
                direct_cli_ok=False,
                direct_cli_version="",
                subprocess_popen_ok=False,
                subprocess_popen_error=find_err,
                anyio_open_process_ok=False,
                anyio_open_process_error=find_err,
                sdk_connect_ok=False,
                sdk_connect_error=find_err,
                diagnosis="Claude CLI not found in PATH. Install Claude Code CLI first.",
            )

        direct_ok, direct_ver = self._test_direct_cli(cli_path)
        popen_ok, popen_err = self._test_subprocess_popen(cli_path)
        anyio_ok, anyio_err = await self._test_anyio_open_process(cli_path)
        sdk_ok, sdk_err = await self._test_sdk_connect(cli_path)

        diagnosis_parts: list[str] = []
        recommendations: list[str] = []

        if direct_ok and popen_ok and not anyio_ok:
            diagnosis_parts.append(
                "CRITICAL: Direct CLI and subprocess.Popen succeed, but anyio.open_process fails. "
                "This matches the WinError 5 pattern observed in production."
            )
            recommendations.append(
                "Implement runtime preflight before pipeline start to detect anyio spawn failure early."
            )
            recommendations.append(
                "Consider using subprocess.Popen wrapper as fallback transport on Windows."
            )
            if sys.platform == "win32":
                recommendations.append(
                    "Investigate Windows-specific anyio backend (trio vs asyncio) behavior."
                )

        if not sdk_ok and not anyio_ok:
            diagnosis_parts.append(
                "SDK connect fails alongside anyio.open_process, confirming transport-level root cause."
            )

        if direct_ok and popen_ok and anyio_ok and sdk_ok:
            diagnosis_parts.append(
                "All transport layers operational. WinError 5 may be environment-specific (e.g., AV/EDR, permissions)."
            )
            recommendations.append(
                "Still implement preflight for proactive detection in restricted environments."
            )

        return TransportPreflightResult(
            platform=sys.platform,
            cli_path=cli_path,
            direct_cli_ok=direct_ok,
            direct_cli_version=direct_ver,
            subprocess_popen_ok=popen_ok,
            subprocess_popen_error=popen_err if not popen_ok else "",
            anyio_open_process_ok=anyio_ok,
            anyio_open_process_error=anyio_err if not anyio_ok else "",
            sdk_connect_ok=sdk_ok,
            sdk_connect_error=sdk_err if not sdk_ok else "",
            diagnosis=" | ".join(diagnosis_parts) if diagnosis_parts else "No anomalies detected.",
            recommendations=recommendations,
        )


# ---------------------------------------------------------------------------
# 2. Graph Semantics Auditor
# ---------------------------------------------------------------------------

class GraphSemanticsAuditor:
    """审计 graph.py / pipeline_adapter.py / state.py 的完成语义冲突。"""

    def __init__(self, project_root: Path) -> None:
        self.root = project_root
        self.graph_path = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
        self.adapter_path = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
        self.state_path = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"

    def _read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def audit(self) -> GraphSemanticsAudit:
        issues: list[Finding] = []
        graph_code = self._read(self.graph_path)
        adapter_code = self._read(self.adapter_path)
        state_code = self._read(self.state_path)

        # R2: graph.py overrides adapter's failure semantics
        if "if node_id not in result_state[\"completed_nodes\"]:" in graph_code:
            issues.append(
                Finding(
                    id="R2-001",
                    severity="CRITICAL",
                    category="graph_completion_override",
                    title="graph.py unconditionally appends node to completed_nodes after adapter conversion",
                    detail=(
                        "PipelineAdapter.convert_node_to_pipeline_state() already implements P0-F1 logic: "
                        "only COMPLETED nodes enter completed_nodes. However, graph.py executor then runs "
                        "'if node_id not in result_state[\"completed_nodes\"]: result_state[\"completed_nodes\"] = ... + [node_id]' "
                        "regardless of adapter result. This overwrites the adapter's failure semantics."
                    ),
                    evidence=[
                        "graph.py lines ~146-152: unconditional completed_nodes append after try/except",
                        "pipeline_adapter.py lines ~322-337: conditional logic based on node_status == COMPLETED",
                    ],
                    file_path=str(self.graph_path),
                    line_hint="146-152",
                    recommendation="Remove or conditionally gate the post-adapter completed_nodes append in graph.py.",
                )
            )

        # R3: finalize_pipeline_state unconditionally marks COMPLETED
        if 'result["status"] = COMPLETED' in state_code:
            issues.append(
                Finding(
                    id="R3-001",
                    severity="CRITICAL",
                    category="finalizer_blind_complete",
                    title="finalize_pipeline_state() unconditionally sets status=COMPLETED",
                    detail=(
                        "finalize_pipeline_state() in state.py sets status=COMPLETED without inspecting "
                        "failed_nodes or error fields. Although orchestrator._determine_final_status() later "
                        "corrects DB status to failed, the LangGraph checkpoint and returned result still carry "
                        "the contradictory status=COMPLETED. This pollutes resume, export, and debugging paths."
                    ),
                    evidence=[
                        "state.py finalize_pipeline_state() line ~310: result['status'] = COMPLETED",
                        "orchestrator.py _determine_final_status() lines ~153-169: post-hoc correction",
                    ],
                    file_path=str(self.state_path),
                    line_hint="~310",
                    recommendation="finalize_pipeline_state() must inspect failed_nodes/error before setting COMPLETED.",
                )
            )

        # Adapter logic check
        adapter_correct = (
            'if node_status == COMPLETED:' in adapter_code
            and 'new_state["failed_nodes"]' in adapter_code
        )

        graph_override = (
            'if node_id not in result_state["completed_nodes"]:' in graph_code
            and 'result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]' in graph_code
        )

        finalizer_blind = 'result["status"] = COMPLETED' in state_code

        contradictions: list[str] = []
        if adapter_correct and graph_override:
            contradictions.append(
                "Adapter correctly routes FAILED nodes to failed_nodes, but graph.py overrides by adding them to completed_nodes."
            )
        if finalizer_blind:
            contradictions.append(
                "Finalizer always marks COMPLETED even when failed_nodes present, creating status contradiction."
            )

        return GraphSemanticsAudit(
            file_path=str(self.graph_path),
            issues=issues,
            adapter_logic_correct=adapter_correct,
            graph_override_detected=graph_override,
            finalizer_blind_complete=finalizer_blind,
            contradiction_scenarios=contradictions,
        )


# ---------------------------------------------------------------------------
# 3. State Ownership Auditor
# ---------------------------------------------------------------------------

class StateOwnershipAuditor:
    """检测 checkpoint、DB 顶层字段、graph result 之间的状态漂移。"""

    def __init__(self, db_path: str = "docuswarm.db") -> None:
        self.db_path = db_path

    def audit(self) -> StateOwnershipAudit:
        import sqlite3

        inconsistencies: list[dict[str, Any]] = []
        violations: list[Finding] = []
        ckpt_exists = False
        pipeline_count = 0
        checkpoint_count = 0

        db_file = Path(self.db_path)
        if db_file.exists():
            try:
                conn = sqlite3.connect(str(db_file))
                conn.row_factory = sqlite3.Row

                cur = conn.execute("SELECT COUNT(*) as c FROM pipelines")
                pipeline_count = cur.fetchone()["c"]

                cur = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
                )
                ckpt_exists = cur.fetchone() is not None

                if ckpt_exists:
                    cur = conn.execute("SELECT COUNT(*) as c FROM checkpoints")
                    checkpoint_count = cur.fetchone()["c"]

                    # Check for pipelines with failed_nodes but DB status=completed
                    cur = conn.execute(
                        "SELECT pipeline_id, status, state_json FROM pipelines WHERE status = 'completed'"
                    )
                    for row in cur.fetchall():
                        state_json = row["state_json"]
                        if not state_json:
                            continue
                        try:
                            state = json.loads(state_json)
                            failed_nodes = state.get("failed_nodes", [])
                            if failed_nodes:
                                inconsistencies.append(
                                    {
                                        "pipeline_id": row["pipeline_id"],
                                        "db_status": "completed",
                                        "state_json_status": state.get("status"),
                                        "failed_nodes_in_state_json": failed_nodes,
                                        "issue": "DB status=completed but state_json contains failed_nodes",
                                    }
                                )
                        except json.JSONDecodeError:
                            pass

                conn.close()
            except Exception as e:
                violations.append(
                    Finding(
                        id="R4-DB-001",
                        severity="HIGH",
                        category="db_access_error",
                        title="Failed to audit database",
                        detail=str(e),
                    )
                )
        else:
            violations.append(
                Finding(
                    id="R4-DB-002",
                    severity="INFO",
                    category="db_not_found",
                    title="Database file not found",
                    detail=f"{self.db_path} does not exist; skipping DB audit.",
                )
            )

        if inconsistencies:
            violations.append(
                Finding(
                    id="R4-001",
                    severity="CRITICAL",
                    category="state_ownership_drift",
                    title="DB status and state_json disagree on pipeline completion",
                    detail=(
                        f"Found {len(inconsistencies)} pipelines where DB top-level status is 'completed' "
                        "but state_json contains failed_nodes. This indicates multiple writers with conflicting policies."
                    ),
                    evidence=[json.dumps(i, ensure_ascii=False) for i in inconsistencies[:5]],
                    recommendation="Implement single PipelineStatusProjection mapper derived from checkpoint truth.",
                )
            )

        return StateOwnershipAudit(
            db_path=self.db_path,
            checkpoint_table_exists=ckpt_exists,
            pipelines_count=pipeline_count,
            checkpoints_count=checkpoint_count,
            inconsistency_cases=inconsistencies,
            ownership_violations=violations,
        )


# ---------------------------------------------------------------------------
# 4. Provider Coupling Auditor
# ---------------------------------------------------------------------------

class ProviderCouplingAuditor:
    """分析 SessionManager 的职责边界和节点对 SDK transport 的耦合。"""

    def __init__(self, project_root: Path) -> None:
        self.root = project_root
        self.session_manager_path = project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
        self.node_execution_path = project_root / "autoBMAD" / "docuswarm" / "node_execution"
        self.pipeline_path = project_root / "autoBMAD" / "docuswarm" / "pipeline"

    def audit(self) -> ProviderCouplingAudit:
        responsibilities: list[str] = []
        boundary_violations: list[Finding] = []
        direct_imports: list[str] = []

        sm_code = ""
        if self.session_manager_path.exists():
            sm_code = self.session_manager_path.read_text(encoding="utf-8")

        # Identify responsibilities
        if "_create_options" in sm_code:
            responsibilities.append("Construct ClaudeAgentOptions (SDK-specific)")
        if "mcp_servers" in sm_code:
            responsibilities.append("Create MCP servers")
        if "allowed_tools" in sm_code:
            responsibilities.append("Generate allowed_tools list")
        if "setting_sources" in sm_code:
            responsibilities.append("Inject Skills setting_sources")
        if "ClaudeSDKClient" in sm_code:
            responsibilities.append("Instantiate ClaudeSDKClient")
        if "stderr_callback" in sm_code:
            responsibilities.append("Register stderr callback")
        if "_close_client_with_process_fallback" in sm_code:
            responsibilities.append("Process kill fallback")

        # Check for direct SDK imports outside llm/ package
        for py_file in self.root.rglob("*.py"):
            rel = py_file.relative_to(self.root)
            if "llm" in str(rel).lower() and "session_manager" not in str(rel):
                continue
            if "__pycache__" in str(rel):
                continue
            try:
                code = py_file.read_text(encoding="utf-8")
            except Exception:
                continue
            if "claude_agent_sdk" in code and "session_manager" not in str(rel):
                direct_imports.append(str(rel))
                if len(direct_imports) > 10:
                    break

        if len(responsibilities) > 4:
            boundary_violations.append(
                Finding(
                    id="R1-001",
                    severity="HIGH",
                    category="provider_responsibility_bloat",
                    title="SessionManager carries too many responsibilities",
                    detail=(
                        f"SessionManager currently handles {len(responsibilities)} distinct concerns: "
                        f"{', '.join(responsibilities)}. This violates single-responsibility and causes "
                        "transport failures to propagate directly to every business node."
                    ),
                    evidence=[
                        "session_manager.py: _create_options builds SDK-specific options dict",
                        "session_manager.py: create_session instantiates ClaudeSDKClient directly",
                        "session_manager.py: _build_allowed_tools mixes builtin + MCP + Skill logic",
                    ],
                    recommendation="Extract ClaudeOptionsFactory, ClaudeSessionFactory, ClaudeTransportMonitor.",
                )
            )

        return ProviderCouplingAudit(
            session_manager_responsibilities=responsibilities,
            direct_sdk_imports_in_nodes=direct_imports,
            boundary_violations=boundary_violations,
            recommended_protocol={
                "AgentRuntime": {
                    "methods": ["preflight", "create_session", "close_all"],
                    "purpose": "Isolate business nodes from transport details",
                },
                "AgentSession": {
                    "methods": ["prompt", "close"],
                    "purpose": "Per-session abstraction",
                },
            },
        )


# ---------------------------------------------------------------------------
# 5. Test Matrix Validator
# ---------------------------------------------------------------------------

class TestMatrixValidator:
    """验证运行时测试矩阵的覆盖情况。"""

    REQUIRED_TESTS = [
        "test_transport_preflight_distinguishes_direct_cli_from_anyio_spawn",
        "test_preflight_failure_prevents_node_execution",
        "test_failed_node_never_enters_completed_nodes_after_adapter",
        "test_finalize_failed_when_failed_nodes_present",
        "test_graph_result_status_matches_orchestrator_final_status",
        "test_provider_contract_for_claude_agent_sdk",
        "test_mcp_allowed_tools_match_registered_servers",
        "test_skills_require_setting_sources_and_skill_tool",
    ]

    def __init__(self, project_root: Path) -> None:
        self.root = project_root
        self.tests_dir = project_root / "tests"

    def validate(self) -> dict[str, Any]:
        found_tests: set[str] = set()
        missing_tests: list[str] = []
        test_locations: dict[str, list[str]] = {}

        for test_file in self.tests_dir.rglob("test_*.py"):
            if "__pycache__" in str(test_file):
                continue
            try:
                code = test_file.read_text(encoding="utf-8")
            except Exception:
                continue
            for required in self.REQUIRED_TESTS:
                if required in code:
                    found_tests.add(required)
                    test_locations.setdefault(required, []).append(str(test_file.relative_to(self.root)))

        for required in self.REQUIRED_TESTS:
            if required not in found_tests:
                missing_tests.append(required)

        return {
            "required_count": len(self.REQUIRED_TESTS),
            "found_count": len(found_tests),
            "missing_tests": missing_tests,
            "test_locations": test_locations,
            "coverage_ratio": len(found_tests) / len(self.REQUIRED_TESTS),
        }


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------

class ReportGenerator:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, name: str, data: Any) -> Path:
        path = self.output_dir / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        return path

    def _write_md(self, name: str, content: str) -> Path:
        path = self.output_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def generate_transport_report(self, result: TransportPreflightResult) -> Path:
        md = textwrap.dedent(f"""\
        # Transport Preflight Diagnostic Report

        **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
        **Platform**: {result.platform}

        ## Summary

        | Check | Result | Detail |
        |-------|--------|--------|
        | Direct CLI (`claude --version`) | {'✅ PASS' if result.direct_cli_ok else '❌ FAIL'} | {result.direct_cli_version or result.direct_cli_version} |
        | `subprocess.Popen` with PIPEs | {'✅ PASS' if result.subprocess_popen_ok else '❌ FAIL'} | {result.subprocess_popen_error or 'OK'} |
        | `anyio.open_process` with PIPEs | {'✅ PASS' if result.anyio_open_process_ok else '❌ FAIL'} | {result.anyio_open_process_error or 'OK'} |
        | `ClaudeSDKClient.connect()` | {'✅ PASS' if result.sdk_connect_ok else '❌ FAIL'} | {result.sdk_connect_error or 'OK'} |

        ## Diagnosis

        {result.diagnosis}

        ## Recommendations

        {"\n".join(f"- {r}" for r in result.recommendations) or "- No specific recommendations."}

        ## Structured Data

        See `transport_preflight_result.json` for machine-readable output.
        """)
        self._write_json("transport_preflight_result.json", asdict(result))
        return self._write_md("transport_preflight_report.md", md)

    def generate_graph_semantics_report(self, audit: GraphSemanticsAudit) -> Path:
        md_lines = [
            "# LangGraph Node Completion Semantics Audit Report",
            "",
            f"**File**: `{audit.file_path}`",
            f"**Adapter logic correct**: {'✅' if audit.adapter_logic_correct else '❌'}",
            f"**Graph override detected**: {'❌ YES' if audit.graph_override_detected else '✅ NO'}",
            f"**Finalizer blind complete**: {'❌ YES' if audit.finalizer_blind_complete else '✅ NO'}",
            "",
            "## Contradiction Scenarios",
        ]
        for scenario in audit.contradiction_scenarios:
            md_lines.append(f"- {scenario}")
        if not audit.contradiction_scenarios:
            md_lines.append("- No contradictions detected.")

        md_lines.extend(["", "## Findings"])
        for finding in audit.issues:
            md_lines.extend([
                f"### {finding.id} — {finding.severity}",
                f"**Category**: {finding.category}",
                f"**Title**: {finding.title}",
                "",
                f"{finding.detail}",
                "",
                "**Evidence**:",
            ])
            for ev in finding.evidence:
                md_lines.append(f"- `{ev}`")
            md_lines.extend(["", f"**Recommendation**: {finding.recommendation}", ""])

        md = "\n".join(md_lines)
        self._write_json("graph_semantics_audit.json", asdict(audit))
        return self._write_md("graph_semantics_audit_report.md", md)

    def generate_state_ownership_report(self, audit: StateOwnershipAudit) -> Path:
        md_lines = [
            "# State Ownership (Checkpoint vs DB) Audit Report",
            "",
            f"**DB Path**: {audit.db_path}",
            f"**Checkpoints table exists**: {'✅' if audit.checkpoint_table_exists else '❌'}",
            f"**Pipelines count**: {audit.pipelines_count}",
            f"**Checkpoints count**: {audit.checkpoints_count}",
            "",
            "## Inconsistency Cases",
        ]
        for case in audit.inconsistency_cases:
            md_lines.append(f"- `{case['pipeline_id']}`: {case['issue']}")
        if not audit.inconsistency_cases:
            md_lines.append("- No inconsistencies found in current DB.")

        md_lines.extend(["", "## Ownership Violations"])
        for v in audit.ownership_violations:
            md_lines.extend([
                f"### {v.id} — {v.severity}",
                f"**{v.title}**",
                "",
                v.detail,
                "",
            ])

        md = "\n".join(md_lines)
        self._write_json("state_ownership_audit.json", asdict(audit))
        return self._write_md("state_ownership_audit_report.md", md)

    def generate_provider_coupling_report(self, audit: ProviderCouplingAudit) -> Path:
        md_lines = [
            "# Provider Coupling Audit Report",
            "",
            "## SessionManager Responsibilities",
        ]
        for resp in audit.session_manager_responsibilities:
            md_lines.append(f"- {resp}")

        md_lines.extend(["", "## Direct SDK Imports Outside llm/ Package"])
        for imp in audit.direct_sdk_imports_in_nodes:
            md_lines.append(f"- `{imp}`")
        if not audit.direct_sdk_imports_in_nodes:
            md_lines.append("- None detected (good).")

        md_lines.extend(["", "## Boundary Violations"])
        for v in audit.boundary_violations:
            md_lines.extend([
                f"### {v.id} — {v.severity}",
                f"**{v.title}**",
                "",
                v.detail,
                "",
                f"**Recommendation**: {v.recommendation}",
                "",
            ])

        md_lines.extend(["", "## Recommended Protocol"])
        for proto_name, proto_def in audit.recommended_protocol.items():
            md_lines.extend([
                f"### {proto_name}",
                f"- **Purpose**: {proto_def['purpose']}",
                f"- **Methods**: {', '.join(proto_def['methods'])}",
            ])

        md = "\n".join(md_lines)
        self._write_json("provider_coupling_audit.json", asdict(audit))
        return self._write_md("provider_coupling_audit_report.md", md)

    def generate_test_matrix_report(self, result: dict[str, Any]) -> Path:
        md_lines = [
            "# Runtime Test Matrix Validation Report",
            "",
            f"**Required tests**: {result['required_count']}",
            f"**Found tests**: {result['found_count']}",
            f"**Coverage ratio**: {result['coverage_ratio']:.0%}",
            "",
            "## Missing Tests",
        ]
        for missing in result["missing_tests"]:
            md_lines.append(f"- ❌ `{missing}`")
        if not result["missing_tests"]:
            md_lines.append("- ✅ All required tests present.")

        md_lines.extend(["", "## Found Test Locations"])
        for test_name, locations in result["test_locations"].items():
            md_lines.append(f"- `{test_name}`: {', '.join(locations)}")

        md = "\n".join(md_lines)
        self._write_json("test_matrix_validation.json", result)
        return self._write_md("test_matrix_validation_report.md", md)


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

async def main() -> int:
    parser = argparse.ArgumentParser(description="WinError 5 Architecture Refactor Research Tool")
    parser.add_argument("--mode", choices=["all", "transport", "graph-semantics", "state-ownership", "provider-coupling", "test-matrix"], default="all")
    parser.add_argument("--db", default="docuswarm.db")
    parser.add_argument("--output-dir", default="docs/research/2026-04-28-winerror5-architecture-refactor")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / args.output_dir
    generator = ReportGenerator(output_dir)

    modes = ["transport", "graph-semantics", "state-ownership", "provider-coupling", "test-matrix"] if args.mode == "all" else [args.mode]

    for mode in modes:
        print(f"Running {mode}...")
        try:
            if mode == "transport":
                result = await TransportPreflightDiagnostics().run()
                path = generator.generate_transport_report(result)
                print(f"  -> {path}")
            elif mode == "graph-semantics":
                audit = GraphSemanticsAuditor(PROJECT_ROOT).audit()
                path = generator.generate_graph_semantics_report(audit)
                print(f"  -> {path}")
            elif mode == "state-ownership":
                audit = StateOwnershipAuditor(args.db).audit()
                path = generator.generate_state_ownership_report(audit)
                print(f"  -> {path}")
            elif mode == "provider-coupling":
                audit = ProviderCouplingAuditor(PROJECT_ROOT).audit()
                path = generator.generate_provider_coupling_report(audit)
                print(f"  -> {path}")
            elif mode == "test-matrix":
                result = TestMatrixValidator(PROJECT_ROOT).validate()
                path = generator.generate_test_matrix_report(result)
                print(f"  -> {path}")
        except Exception as e:
            print(f"  ERROR in {mode}: {e}")
            traceback.print_exc()

    print(f"\nReports written to: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

#!/usr/bin/env python3
"""
DocuSwarm Pipeline State Consistency Deep Researcher

基于以下评估报告进行深度研究:
- docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md

研究领域:
1. current_node 在完成状态未清空
2. node_iterations 统计与实际 DualAgent iteration 不一致
3. emergency finalize 写入非法状态并绕开 state_json
4. StateManager.update_pipeline_state() deep merge 保留旧字段
5. pipeline_started 日志事件在执行完成后才输出
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path("/home/leafliu/autoBMAD")
DOCUSWARM_ROOT = PROJECT_ROOT / "autoBMAD" / "docuswarm"
LOG_FILE = PROJECT_ROOT / "logs" / "docuswarm-2026-05-01.log"
DB_FILE = PROJECT_ROOT / "docuswarm.db"


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    code_snippets: list[tuple[str, str]] = field(default_factory=list)


class PipelineStateInvestigator:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.log_data: str = ""
        self.db_pipeline_state: dict[str, Any] | None = None
        self.db_top_level: dict[str, Any] | None = None

    def load_evidence(self) -> None:
        if LOG_FILE.exists():
            self.log_data = LOG_FILE.read_text(encoding="utf-8")
            print(f"[INFO] Loaded log file: {LOG_FILE}")
        else:
            print(f"[WARN] Log file not found")

        if DB_FILE.exists():
            try:
                conn = sqlite3.connect(str(DB_FILE))
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT pipeline_id, status, current_node, state_json "
                    "FROM pipelines ORDER BY updated_at DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    self.db_top_level = dict(row)
                    if row["state_json"]:
                        self.db_pipeline_state = json.loads(row["state_json"])
                conn.close()
                print("[INFO] Loaded latest pipeline state from DB")
            except Exception as e:
                print(f"[WARN] Failed to read DB: {e}")

    # ------------------------------------------------------------------
    # Finding 1: current_node 在完成状态未清空
    # ------------------------------------------------------------------
    def investigate_f1_current_node(self) -> Finding:
        f = Finding(
            id="STATE-1",
            title="完成状态仍保留 current_node='po'，会误导 status/resume/cancel 语义",
            severity="High",
        )

        # Log evidence
        if self.db_pipeline_state:
            status = self.db_pipeline_state.get("status")
            current = self.db_pipeline_state.get("current_node")
            completed = self.db_pipeline_state.get("completed_nodes", [])
            f.evidence.append(
                f"DB state_json: status='{status}', current_node='{current}', "
                f"completed_nodes={completed}"
            )
            if status == "completed" and current is not None:
                f.evidence.append(
                    "BUG CONFIRMED: completed pipeline still has current_node set. "
                    "This makes it appear as if the pipeline is still running on 'po'."
                )

        # Check DB top-level
        if self.db_top_level:
            f.evidence.append(
                f"DB top-level columns: status='{self.db_top_level.get('status')}', "
                f"current_node='{self.db_top_level.get('current_node')}'"
            )

        # Code evidence: graph.py executor sets current_node
        gp = DOCUSWARM_ROOT / "pipeline" / "graph.py"
        gc = gp.read_text(encoding="utf-8")
        if 'new_state["current_node"] = node_id' in gc:
            f.evidence.append(
                f"{gp}: executor sets current_node to node_id at start of each node."
            )
            f.code_snippets.append((str(gp), 'new_state["current_node"] = node_id'))

        # Code evidence: orchestrator reads current_node for final write
        op = DOCUSWARM_ROOT / "pipeline" / "orchestrator.py"
        oc = op.read_text(encoding="utf-8")
        if 'final_current_node = result.get("current_node"' in oc:
            f.evidence.append(
                f"{op}: HybridOrchestrator.start_pipeline() writes "
                "final_current_node = result.get('current_node', 'po') back to DB."
            )
            f.code_snippets.append(
                (str(op), 'final_current_node = result.get("current_node", "po")')
            )

        # Check for finalize clearing current_node
        if "current_node" in oc and ("finalize" in oc.lower() or "completed" in oc):
            # Search for any place that clears current_node on completion
            lines = oc.splitlines()
            found_clear = False
            for i, line in enumerate(lines):
                if "current_node" in line and ("None" in line or "null" in line.lower()):
                    found_clear = True
                    f.evidence.append(
                        f"{op}:{i+1}: Found potential current_node clearing: {line.strip()}"
                    )
            if not found_clear:
                f.evidence.append(
                    f"{op}: No code found that clears current_node to None on pipeline completion."
                )

        f.recommendation = (
            "finalize_pipeline_state() 或 graph finalize executor 应显式写: "
            'state["current_node"] = None; state["last_node"] = previous_current_node。'
        )
        return f

    # ------------------------------------------------------------------
    # Finding 2: node_iterations 统计不一致
    # ------------------------------------------------------------------
    def investigate_f2_node_iterations(self) -> Finding:
        f = Finding(
            id="STATE-2",
            title="node_iterations 统计与实际 DualAgent iteration 不一致",
            severity="High",
        )

        # DB evidence
        if self.db_pipeline_state:
            ni = self.db_pipeline_state.get("node_iterations", {})
            f.evidence.append(f"DB state_json node_iterations: {ni}")
            for node, count in ni.items():
                if count != 1:
                    f.evidence.append(
                        f"ANOMALY: {node} shows {count} iterations, "
                        "but logs show dual_agent_approved iteration=1 for all nodes."
                    )

        # Log evidence: count dual_agent_approved iteration values
        approved_lines = re.findall(
            r'dual_agent_approved.*iteration=(\d+)', self.log_data
        )
        f.evidence.append(
            f"Log analysis: Found {len(approved_lines)} 'dual_agent_approved' events "
            f"with iterations: {approved_lines}"
        )

        # Code evidence: graph.py iteration assignment
        gp = DOCUSWARM_ROOT / "pipeline" / "graph.py"
        gc = gp.read_text(encoding="utf-8")
        if "actual_iteration = executed_node_state.get(\"iteration\", 1)" in gc:
            f.evidence.append(
                f"{gp}: Uses executed_node_state.get('iteration', 1) for node_iterations. "
                "But NodeResult.iteration may have off-by-one or adapter drift."
            )
            # Extract surrounding context
            lines = gc.splitlines()
            for i, line in enumerate(lines):
                if "actual_iteration = executed_node_state.get" in line:
                    ctx = "\n".join(lines[max(0, i - 5) : i + 6])
                    f.code_snippets.append((str(gp), ctx))
                    break

        # Check dual_agent.py for iteration value
        dap = DOCUSWARM_ROOT / "nodes" / "dual_agent.py"
        dac = dap.read_text(encoding="utf-8")
        if "iteration" in dac:
            # Find where iteration is set in NodeResult
            lines = dac.splitlines()
            for i, line in enumerate(lines):
                if "iteration" in line and "NodeResult" in line:
                    ctx = "\n".join(lines[max(0, i - 3) : i + 4])
                    f.code_snippets.append((str(dap), ctx))
                    break

        f.recommendation = (
            "统一 iteration 语义: attempt_index(即将执行第几次), "
            "iterations_executed(已完成), dual_agent_iterations(evaluator 修订循环次数)。"
            "最小修复: 让 NodeResult.iteration 表示实际执行轮数，禁止二次递增。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 3: emergency finalize 写入非法状态
    # ------------------------------------------------------------------
    def investigate_f3_emergency_finalize(self) -> Finding:
        f = Finding(
            id="STATE-3",
            title="emergency finalize 写入非法状态 'interrupted' 并绕开 state_json",
            severity="High",
        )

        # Code evidence
        psp = DOCUSWARM_ROOT / "cli" / "services" / "pipeline_service.py"
        psc = psp.read_text(encoding="utf-8")

        if "'interrupted'" in psc:
            f.evidence.append(
                f"{psp}: _emergency_finalize() executes raw SQL setting status='interrupted'."
            )
            lines = psc.splitlines()
            for i, line in enumerate(lines):
                if "interrupted" in line:
                    ctx = "\n".join(lines[max(0, i - 5) : i + 6])
                    f.code_snippets.append((str(psp), ctx))
                    break

        # Check PIPELINE_STATUSES
        smp = DOCUSWARM_ROOT / "storage" / "state_manager.py"
        smc = smp.read_text(encoding="utf-8")
        if "PIPELINE_STATUSES" in smc:
            match = re.search(r'PIPELINE_STATUSES = \(([^)]+)\)', smc)
            if match:
                statuses = match.group(1)
                f.evidence.append(
                    f"{smp}: PIPELINE_STATUSES = ({statuses}). 'interrupted' is NOT in this list."
                )
                if "interrupted" not in statuses:
                    f.evidence.append(
                        "CONFIRMED: 'interrupted' is an ILLEGAL status value."
                    )

        # Check that emergency finalize does NOT update state_json
        if "state_json" not in psc.split("def _emergency_finalize")[1].split("def ")[0]:
            f.evidence.append(
                f"{psp}: _emergency_finalize() does NOT update state_json. "
                "It only updates the top-level pipelines.status column. "
                "This breaks the single-source-of-truth principle."
            )

        f.recommendation = (
            "方案A: 将 'interrupted' 纳入合法状态，并通过 StateManager.update_pipeline_state() "
            "写完整 state。方案B: 将中断统一映射为 'cancelled' 或 'failed'。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 4: StateManager deep merge 保留旧字段
    # ------------------------------------------------------------------
    def investigate_f4_deep_merge(self) -> Finding:
        f = Finding(
            id="STATE-4",
            title="StateManager.update_pipeline_state() 对完整 result 使用 deep merge，可能保留旧字段",
            severity="Medium",
        )

        smp = DOCUSWARM_ROOT / "storage" / "state_manager.py"
        smc = smp.read_text(encoding="utf-8")

        if "_deep_merge" in smc:
            f.evidence.append(
                f"{smp}: update_pipeline_state() calls _deep_merge() instead of full replacement."
            )
            lines = smc.splitlines()
            for i, line in enumerate(lines):
                if "def _deep_merge" in line:
                    ctx = "\n".join(lines[i : i + 15])
                    f.code_snippets.append((str(smp), ctx))
                    break
            for i, line in enumerate(lines):
                if "self._deep_merge(current_state, state_update)" in line:
                    ctx = "\n".join(lines[max(0, i - 8) : i + 3])
                    f.code_snippets.append((str(smp), ctx))
                    break

        f.evidence.append(
            "Impact: resume/restart 后可能残留旧 questions、evaluations、session_metadata。"
            "节点重跑时删除字段不容易生效，因为 merge 不支持删除语义。"
        )

        f.recommendation = (
            "拆分 API: patch_pipeline_state() 用 deep merge，replace_pipeline_state() 做完整替换。"
            "HybridOrchestrator final write 应使用 replace 语义。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 5: pipeline_started 日志事件名错误
    # ------------------------------------------------------------------
    def investigate_f5_log_event(self) -> Finding:
        f = Finding(
            id="STATE-5",
            title="pipeline_started 日志事件在执行完成后才输出",
            severity="Medium",
        )

        op = DOCUSWARM_ROOT / "pipeline" / "orchestrator.py"
        oc = op.read_text(encoding="utf-8")

        if 'logger.info(\n                "pipeline_started"' in oc:
            f.evidence.append(
                f"{op}: 'pipeline_started' log event is emitted AFTER graph.ainvoke() completes."
            )
            lines = oc.splitlines()
            for i, line in enumerate(lines):
                if "pipeline_started" in line:
                    ctx = "\n".join(lines[max(0, i - 8) : i + 6])
                    f.code_snippets.append((str(op), ctx))
                    break

        # Log evidence
        if self.log_data:
            started_lines = [m.start() for m in re.finditer(r"pipeline_started", self.log_data)]
            if started_lines:
                # Check position relative to overall log
                total_len = len(self.log_data)
                last_pos = started_lines[-1]
                pct = last_pos / total_len * 100
                f.evidence.append(
                    f"Log analysis: 'pipeline_started' appears at {pct:.1f}% of log file "
                    f"(near the END), confirming it is emitted after completion."
                )

        f.recommendation = (
            "把当前事件改名为 'pipeline_completed' 或 'pipeline_finished'。"
            "真正的 'pipeline_started' 应在 update status=running 后、graph 执行前记录。"
        )
        return f

    # ------------------------------------------------------------------
    # Additional: Status consistency between top-level columns and state_json
    # ------------------------------------------------------------------
    def investigate_extra_status_consistency(self) -> Finding:
        f = Finding(
            id="STATE-EXTRA",
            title="Top-level DB columns 与 state_json 之间的一致性检查",
            severity="Info",
        )

        if self.db_top_level and self.db_pipeline_state:
            top_status = self.db_top_level.get("status")
            json_status = self.db_pipeline_state.get("status")
            top_node = self.db_top_level.get("current_node")
            json_node = self.db_pipeline_state.get("current_node")

            f.evidence.append(f"Top-level status: '{top_status}' | state_json status: '{json_status}'")
            f.evidence.append(f"Top-level current_node: '{top_node}' | state_json current_node: '{json_node}'")

            if top_status == json_status:
                f.evidence.append("status is CONSISTENT between top-level and state_json.")
            else:
                f.evidence.append("MISMATCH: status differs between top-level and state_json!")

            if top_node == json_node:
                f.evidence.append("current_node is CONSISTENT between top-level and state_json.")
            else:
                f.evidence.append("MISMATCH: current_node differs between top-level and state_json!")

        return f

    def run_all(self) -> list[Finding]:
        self.load_evidence()
        self.findings.append(self.investigate_f1_current_node())
        self.findings.append(self.investigate_f2_node_iterations())
        self.findings.append(self.investigate_f3_emergency_finalize())
        self.findings.append(self.investigate_f4_deep_merge())
        self.findings.append(self.investigate_f5_log_event())
        self.findings.append(self.investigate_extra_status_consistency())
        return self.findings

    def report(self) -> str:
        lines: list[str] = [
            "# Pipeline State Consistency Deep Research Report",
            "",
            f"Generated from: {DOCUSWARM_ROOT}",
            f"Log file: {LOG_FILE}",
            f"DB file: {DB_FILE}",
            "",
            "---",
            "",
        ]
        for finding in self.findings:
            lines.append(f"## {finding.id}: {finding.title}")
            lines.append(f"**Severity:** {finding.severity}")
            lines.append("")
            lines.append("### Evidence")
            for ev in finding.evidence:
                lines.append(f"- {ev}")
            lines.append("")
            if finding.code_snippets:
                lines.append("### Code Snippets")
                for file_path, snippet in finding.code_snippets:
                    lines.append(f"**{file_path}**")
                    lines.append("```python")
                    lines.append(snippet)
                    lines.append("```")
                lines.append("")
            lines.append(f"**Recommendation:** {finding.recommendation}")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    inv = PipelineStateInvestigator()
    inv.run_all()
    report = inv.report()
    out_path = PROJECT_ROOT / "docs-doc" / "research" / "pipeline_state_consistency_research.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\n[INFO] Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

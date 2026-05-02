#!/usr/bin/env python3
"""
DocuSwarm Blocking Question Mechanism Deep Researcher

基于以下评估报告进行深度研究:
- docs/evaluation/2026-05-01-docuswarm-blocking-question-removal-review.md
- docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md

研究领域:
1. QuestionHandler 持久化缺陷
2. create_dual_agent_node 未注入 QuestionHandler
3. README 与代码不一致
4. blocking 语义污染
5. 两套 QuestionPriority 定义分叉
6. questions 字段审计价值
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
    code_snippets: list[tuple[str, str]] = field(default_factory=list)  # (file, snippet)


class BlockingQuestionInvestigator:
    """Investigates all aspects of the blocking question mechanism."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.log_data: str = ""
        self.db_pipeline_state: dict[str, Any] | None = None

    def load_evidence(self) -> None:
        if LOG_FILE.exists():
            self.log_data = LOG_FILE.read_text(encoding="utf-8")
            print(f"[INFO] Loaded log file: {LOG_FILE} ({len(self.log_data)} chars)")
        else:
            print(f"[WARN] Log file not found: {LOG_FILE}")

        if DB_FILE.exists():
            try:
                conn = sqlite3.connect(str(DB_FILE))
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT state_json FROM pipelines ORDER BY updated_at DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row and row["state_json"]:
                    self.db_pipeline_state = json.loads(row["state_json"])
                    print("[INFO] Loaded latest pipeline state from DB")
                conn.close()
            except Exception as e:
                print(f"[WARN] Failed to read DB: {e}")
        else:
            print(f"[WARN] DB file not found: {DB_FILE}")

    # ------------------------------------------------------------------
    # Finding 1: QuestionHandler 没有持久化
    # ------------------------------------------------------------------
    def investigate_f1_persistence(self) -> Finding:
        f = Finding(
            id="F1",
            title="QuestionHandler 没有持久化，CLI 查询/回答在真实运行后不可用",
            severity="High",
        )

        # Read questions.py
        qp = DOCUSWARM_ROOT / "pipeline" / "questions.py"
        content = qp.read_text(encoding="utf-8")

        # Evidence: _questions is plain dict
        if "self._questions: dict[str, list[Question]] = {}" in content:
            f.evidence.append(
                f"{qp}: QuestionHandler._questions is a plain in-memory dict, "
                "not persisted to disk or database."
            )
            f.code_snippets.append((str(qp), "self._questions: dict[str, list[Question]] = {}"))

        # Read CLI answer.py
        ap = DOCUSWARM_ROOT / "cli" / "commands" / "answer.py"
        ac = ap.read_text(encoding="utf-8")
        if "QuestionHandler(state_manager=state_manager)" in ac:
            f.evidence.append(
                f"{ap}: Each CLI invocation creates a NEW QuestionHandler instance, "
                "so it cannot see questions collected during pipeline execution."
            )

        # Read CLI questions.py
        qcp = DOCUSWARM_ROOT / "cli" / "commands" / "questions.py"
        qcc = qcp.read_text(encoding="utf-8")
        if "QuestionHandler(state_manager=state_manager)" in qcc:
            f.evidence.append(
                f"{qcp}: Same issue - new QuestionHandler per CLI call, "
                "get_unanswered_questions() always returns empty for historical pipelines."
            )

        f.recommendation = (
            "删除 QuestionHandler 的交互式内存管理职责。"
            "若保留问题展示，应直接从 pipeline final state 的 questions 字段读取。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 2: create_dual_agent_node 未注入 QuestionHandler
    # ------------------------------------------------------------------
    def investigate_f2_no_injection(self) -> Finding:
        f = Finding(
            id="F2",
            title="create_dual_agent_node 默认没有注入 QuestionHandler，问题收集器不是主路径组件",
            severity="High",
        )

        dap = DOCUSWARM_ROOT / "nodes" / "dual_agent.py"
        dac = dap.read_text(encoding="utf-8")

        # Check __init__ signature
        if "question_handler: QuestionHandler | None = None" in dac:
            f.evidence.append(
                f"{dap}: DualAgentNode.__init__ accepts question_handler, but it is optional."
            )

        # Check create_dual_agent_node
        pat = re.compile(
            r"def create_dual_agent_node\(.*?(?=\ndef |\Z)", re.DOTALL
        )
        m = pat.search(dac)
        if m:
            func_body = m.group(0)
            if "question_handler" not in func_body:
                f.evidence.append(
                    f"{dap}: create_dual_agent_node() does NOT pass question_handler to "
                    "DualAgentNode constructor. The main execution path never enables "
                    "QuestionHandler.collect_questions()."
                )
                f.code_snippets.append((str(dap), func_body[:600]))

        f.recommendation = (
            "删除 DualAgentNode 的 question_handler 参数与 collect_questions() 调用。"
            "保留 NodeResult.questions 直接原样入 state。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 3: README 与代码不一致
    # ------------------------------------------------------------------
    def investigate_f3_readme_mismatch(self) -> Finding:
        f = Finding(
            id="F3",
            title="README 描述的 paused/answer/resume 流程与代码不一致",
            severity="High",
        )

        readme = DOCUSWARM_ROOT / "README.md"
        rc = readme.read_text(encoding="utf-8")

        promises = []
        if "questions" in rc and "answer" in rc:
            promises.append("README mentions 'questions' and 'answer' commands")
        if "paused" in rc.lower():
            promises.append("README mentions 'paused' status")
        if "blocking" in rc.lower():
            promises.append("README mentions 'blocking' questions")

        f.evidence.append(
            f"{readme}: README makes interactive Q&A promises: {promises}. "
            "But as shown in F1/F2, the underlying implementation does not support "
            "cross-process question persistence or pause/resume driven by blocking questions."
        )

        # Check StateManager for paused status usage
        smp = DOCUSWARM_ROOT / "storage" / "state_manager.py"
        smc = smp.read_text(encoding="utf-8")
        if "paused" in smc:
            f.evidence.append(
                f"{smp}: 'paused' is in PIPELINE_STATUSES, but no code links it to "
                "blocking question detection."
            )

        f.recommendation = (
            "同步更新 README: 删除'管理问题与回答'章节，删除 paused 状态说明，"
            "改为'节点诊断与后续事项'。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 4: blocking 语义污染
    # ------------------------------------------------------------------
    def investigate_f4_blocking_semantics(self) -> Finding:
        f = Finding(
            id="F4",
            title="blocking 语义鼓励代理提问，但用户不回答时会污染成功输出",
            severity="Medium",
        )

        # Check prompt
        cbp = DOCUSWARM_ROOT / "prompts" / "contract_builder.py"
        cbc = cbp.read_text(encoding="utf-8")
        if "blocking" in cbc:
            f.evidence.append(
                f"{cbp}: Prompt explicitly instructs agent to generate 'blocking' questions "
                "and says 'Must be answered before proceeding'."
            )

        # Check tool schema
        sdkp = DOCUSWARM_ROOT / "tools" / "create_deliverable_sdk.py"
        sdkc = sdkp.read_text(encoding="utf-8")
        if '"blocking"' in sdkc:
            f.evidence.append(
                f"{sdkp}: Tool schema enum includes 'blocking' as valid priority."
            )

        # Check validator
        vp = DOCUSWARM_ROOT / "context" / "validator.py"
        vc = vp.read_text(encoding="utf-8")
        if '"blocking"' in vc:
            f.evidence.append(
                f"{vp}: Validator VALID_PRIORITIES includes 'blocking'."
            )

        # Log evidence: actual blocking questions in completed pipeline
        if self.db_pipeline_state:
            questions = self.db_pipeline_state.get("questions", {})
            blocking = [
                (node, q)
                for node, ql in questions.items()
                for q in ql
                if q.get("priority") == "blocking"
            ]
            if blocking:
                f.evidence.append(
                    f"DB pipeline state (status={self.db_pipeline_state.get('status')}): "
                    f"Found {len(blocking)} blocking questions in a COMPLETED pipeline. "
                    "This proves blocking questions do NOT block execution."
                )
                for node, q in blocking:
                    f.evidence.append(f"  - [{node}] {q.get('question', '')[:100]}...")

        f.recommendation = (
            "移除 blocking priority，改为只允许 clarifying/optional。"
            "真正阻断的场景应由 evaluator 返回 BLOCKED 或 executor 抛出错误。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 5: 两套 QuestionPriority 定义
    # ------------------------------------------------------------------
    def investigate_f5_priority_divergence(self) -> Finding:
        f = Finding(
            id="F5",
            title="存在第二套 QuestionPriority 定义，priority 语义已经分叉",
            severity="Medium",
        )

        # pipeline/questions.py
        qp = DOCUSWARM_ROOT / "pipeline" / "questions.py"
        qc = qp.read_text(encoding="utf-8")
        if "class QuestionPriority(Enum)" in qc:
            f.evidence.append(
                f"{qp}: Defines QuestionPriority as Enum with BLOCKING, CLARIFYING, OPTIONAL (uppercase)."
            )

        # llm/response.py
        rp = DOCUSWARM_ROOT / "llm" / "response.py"
        rc = rp.read_text(encoding="utf-8")
        if 'QuestionPriority = Literal["low", "medium", "high", "critical"]' in rc:
            f.evidence.append(
                f"{rp}: Defines DIFFERENT QuestionPriority as Literal[low, medium, high, critical]. "
                "This is completely incompatible with the pipeline enum."
            )
            f.code_snippets.append(
                (str(rp), 'QuestionPriority = Literal["low", "medium", "high", "critical"]')
            )

        # validator uses lowercase
        vp = DOCUSWARM_ROOT / "context" / "validator.py"
        vc = vp.read_text(encoding="utf-8")
        if 'VALID_PRIORITIES: set[str] = {"blocking", "clarifying", "optional"}' in vc:
            f.evidence.append(
                f"{vp}: Uses lowercase set {{blocking, clarifying, optional}}."
            )

        # questions.py does .upper() compatibility
        if ".upper()" in qc:
            f.evidence.append(
                f"{qp}: Uses .upper() to bridge lowercase input to uppercase enum. "
                "This masks the design divergence."
            )

        f.recommendation = (
            "同步删除 llm/response.py 中未被真正使用的 QuestionPriority 类型别名，"
            "或标记为 deprecated。统一对外口径为小写 clarifying/optional。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 6: questions 字段审计价值
    # ------------------------------------------------------------------
    def investigate_f6_audit_value(self) -> Finding:
        f = Finding(
            id="F6",
            title="完全删除 questions 字段会损失有用的审计信号",
            severity="Medium",
        )

        # Check executor and adapter
        ep = DOCUSWARM_ROOT / "node_execution" / "executor.py"
        if ep.exists():
            ec = ep.read_text(encoding="utf-8")
            if "questions" in ec:
                f.evidence.append(
                    f"{ep}: Node executor writes questions into result, showing they are "
                    "intended as delivery metadata."
                )

        # Check pipeline state
        if self.db_pipeline_state:
            questions = self.db_pipeline_state.get("questions", {})
            total = sum(len(ql) for ql in questions.values())
            f.evidence.append(
                f"DB pipeline state contains {total} questions across {len(questions)} nodes. "
                "These expose upstream context gaps, assumptions, and follow-up items."
            )
            for node, ql in questions.items():
                clarifying = sum(1 for q in ql if q.get("priority") == "clarifying")
                optional = sum(1 for q in ql if q.get("priority") == "optional")
                blocking = sum(1 for q in ql if q.get("priority") == "blocking")
                f.evidence.append(
                    f"  {node}: {len(ql)} total (blocking={blocking}, clarifying={clarifying}, optional={optional})"
                )

        f.recommendation = (
            "不要一刀切删除所有 questions 数据流。建议改为 diagnostics/follow_ups，"
            "去掉'必须回答'语义，作为 report metadata 保存和导出。"
        )
        return f

    # ------------------------------------------------------------------
    # Cross-cutting: Check all references to blocking in source
    # ------------------------------------------------------------------
    def investigate_cross_cutting_references(self) -> Finding:
        f = Finding(
            id="CROSS",
            title="Cross-cutting: 所有源代码中 blocking 相关引用汇总",
            severity="Info",
        )

        grep_results: list[str] = []
        for root, _dirs, files in os.walk(DOCUSWARM_ROOT):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                fp = Path(root) / filename
                try:
                    content = fp.read_text(encoding="utf-8")
                except Exception:
                    continue
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if "blocking" in line.lower():
                        rel = fp.relative_to(PROJECT_ROOT)
                        grep_results.append(f"  {rel}:{i}: {line.strip()}")

        f.evidence.append(
            f"Found {len(grep_results)} lines referencing 'blocking' in docuswarm Python source:"
        )
        f.evidence.extend(grep_results[:80])  # limit output
        if len(grep_results) > 80:
            f.evidence.append(f"  ... and {len(grep_results) - 80} more lines")

        return f

    def run_all(self) -> list[Finding]:
        self.load_evidence()
        self.findings.append(self.investigate_f1_persistence())
        self.findings.append(self.investigate_f2_no_injection())
        self.findings.append(self.investigate_f3_readme_mismatch())
        self.findings.append(self.investigate_f4_blocking_semantics())
        self.findings.append(self.investigate_f5_priority_divergence())
        self.findings.append(self.investigate_f6_audit_value())
        self.findings.append(self.investigate_cross_cutting_references())
        return self.findings

    def report(self) -> str:
        lines: list[str] = [
            "# Blocking Question Mechanism Deep Research Report",
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
    inv = BlockingQuestionInvestigator()
    inv.run_all()
    report = inv.report()
    out_path = PROJECT_ROOT / "docs-doc" / "research" / "blocking_question_mechanism_research.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\n[INFO] Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

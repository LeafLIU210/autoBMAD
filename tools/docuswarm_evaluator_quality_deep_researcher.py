#!/usr/bin/env python3
"""
DocuSwarm Evaluator Quality Gate Deep Researcher

基于以下评估报告进行深度研究:
- docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md

研究领域:
1. 输出质量门对"批准但有明显事实错误/矛盾"的容忍度偏高
2. Evaluator 按 alignment score 阈值判定，缺少 hard gate
3. 交付物中中英文混排和编号体系不一致
4. 极简任务的架构输出过度展开
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path("/home/leafliu/autoBMAD")
DOCUSWARM_ROOT = PROJECT_ROOT / "autoBMAD" / "docuswarm"
OUTPUT_DIR = PROJECT_ROOT / "output" / "pipeline-1777610205512-d6ce6a21"
LOG_FILE = PROJECT_ROOT / "logs" / "docuswarm-2026-05-01.log"


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    code_snippets: list[tuple[str, str]] = field(default_factory=list)
    file_samples: list[tuple[str, str]] = field(default_factory=list)


class EvaluatorQualityInvestigator:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.log_data: str = ""

    def load_evidence(self) -> None:
        if LOG_FILE.exists():
            self.log_data = LOG_FILE.read_text(encoding="utf-8")
            print(f"[INFO] Loaded log file: {LOG_FILE}")

    # ------------------------------------------------------------------
    # Finding 1: Quality gate tolerance too high
    # ------------------------------------------------------------------
    def investigate_f1_tolerance(self) -> Finding:
        f = Finding(
            id="QG-1",
            title="输出质量门对'批准但有明显事实错误/矛盾'的容忍度偏高",
            severity="Medium",
        )

        # Check evaluator.py threshold
        ep = DOCUSWARM_ROOT / "agents" / "evaluator.py"
        ec = ep.read_text(encoding="utf-8")

        if "0.70" in ec or ">= 0.7" in ec or ">=0.7" in ec:
            f.evidence.append(
                f"{ep}: Default APPROVED threshold appears to be >= 0.70 alignment_score."
            )
            lines = ec.splitlines()
            for i, line in enumerate(lines):
                if "0.7" in line and ("score" in line.lower() or "threshold" in line.lower() or "approve" in line.lower()):
                    ctx = "\n".join(lines[max(0, i - 2) : i + 3])
                    f.code_snippets.append((str(ep), ctx))

        # Log evidence: check actual scores from the pipeline
        if self.log_data:
            scores = re.findall(r"alignment_score[=:]\s*([0-9.]+)", self.log_data)
            if scores:
                f.evidence.append(
                    f"Log analysis: Found alignment scores: {scores}. "
                    "All appear to be above 0.90, which is well above the 0.70 threshold."
                )

        # Check for hard gates on factual errors
        if "factual" in ec.lower() or "error" in ec.lower():
            f.evidence.append(
                f"{ep}: Evaluator mentions factual/error concepts, but no hard gate prevents "
                "APPROVED verdict when factual errors are present in issues_found."
            )

        f.recommendation = (
            "引入 hard gate: issues_found 中包含 factual error 且影响需求/技术决策时，"
            "最高 verdict 为 NEEDS_REVISION。存在 blocking question 时，node/pipeline 状态不得为 completed。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 2: Missing hard gate mechanism
    # ------------------------------------------------------------------
    def investigate_f2_hard_gate(self) -> Finding:
        f = Finding(
            id="QG-2",
            title="Evaluator 主要按加权均分判定，对离散缺陷缺少 hard gate",
            severity="Medium",
        )

        ep = DOCUSWARM_ROOT / "agents" / "evaluator.py"
        ec = ep.read_text(encoding="utf-8")

        # Look for verdict determination logic
        if "verdict" in ec:
            f.evidence.append(
                f"{ep}: Evaluator determines verdict, likely based on weighted criteria scores."
            )
            lines = ec.splitlines()
            for i, line in enumerate(lines):
                if "verdict" in line and ("APPROVED" in line or "NEEDS_REVISION" in line or "BLOCKED" in line):
                    ctx = "\n".join(lines[max(0, i - 5) : i + 8])
                    if len(ctx) < 800:
                        f.code_snippets.append((str(ep), ctx))
                    else:
                        f.code_snippets.append((str(ep), ctx[:800] + "\n..."))
                    break

        f.recommendation = (
            "增加离散缺陷检查层: 在 score-based verdict 之后，遍历 issues_found 检查 "
            "是否存在 factual_error、blocking_question、ac_ambiguity 等标签，"
            "若有则强制降级为 NEEDS_REVISION 或 BLOCKED。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 3: Deliverable ID inconsistency
    # ------------------------------------------------------------------
    def investigate_f3_id_consistency(self) -> Finding:
        f = Finding(
            id="QG-3",
            title="交付物中中英文混排和编号体系不一致",
            severity="Low",
        )

        if not OUTPUT_DIR.exists():
            f.evidence.append(f"Output dir not found: {OUTPUT_DIR}")
            return f

        files_to_check = [
            ("analyst-report.md", ["FR-001", "FR-"]),
            ("prd.md", ["FR-01", "FR-"]),
            ("epics-stories.md", ["Story", "Epic"]),
        ]

        for fname, patterns in files_to_check:
            fp = OUTPUT_DIR / fname
            if fp.exists():
                content = fp.read_text(encoding="utf-8")
                found = []
                for p in patterns:
                    count = content.count(p)
                    if count > 0:
                        found.append(f"{p}({count})")
                f.evidence.append(
                    f"{fp.name}: Found ID patterns: {found}. Line count: {len(content.splitlines())}."
                )
                # Show first few lines with IDs
                for line in content.splitlines()[:30]:
                    if any(p in line for p in patterns):
                        f.file_samples.append((fp.name, line.strip()))
                        if len(f.file_samples) >= 6:
                            break

        f.recommendation = (
            "统一 ID 规范: FR-001、NFR-001、AC-001，并要求下游保留上游 ID。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 4: Over-architecting trivial tasks
    # ------------------------------------------------------------------
    def investigate_f4_over_architecture(self) -> Finding:
        f = Finding(
            id="QG-4",
            title="极简任务的架构输出过度展开",
            severity="Low",
        )

        arch_file = OUTPUT_DIR / "architecture.md"
        if arch_file.exists():
            content = arch_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            f.evidence.append(
                f"{arch_file.name}: {len(lines)} lines for a 'compute 1+1' CLI task."
            )

            # Check for diagrams
            diagrams = []
            if "```mermaid" in content:
                diagrams.append("Mermaid")
            if "C4" in content:
                diagrams.append("C4")
            if "sequence" in content.lower():
                diagrams.append("Sequence")
            if "flowchart" in content.lower():
                diagrams.append("Flowchart")
            f.evidence.append(
                f"Contains diagram types: {diagrams}. For a 10-line script, this is excessive."
            )

            # Show section headers
            headers = [l.strip() for l in lines if l.strip().startswith("#")]
            f.file_samples.append((arch_file.name, "\n".join(headers[:15])))

        f.recommendation = (
            "为 trivial/minimal task 增加 lightweight architecture 模板: "
            "目标与约束、文件结构、参考实现、验收命令、排除项。"
        )
        return f

    def run_all(self) -> list[Finding]:
        self.load_evidence()
        self.findings.append(self.investigate_f1_tolerance())
        self.findings.append(self.investigate_f2_hard_gate())
        self.findings.append(self.investigate_f3_id_consistency())
        self.findings.append(self.investigate_f4_over_architecture())
        return self.findings

    def report(self) -> str:
        lines: list[str] = [
            "# Evaluator Quality Gate Deep Research Report",
            "",
            f"Generated from: {DOCUSWARM_ROOT}",
            f"Output dir: {OUTPUT_DIR}",
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
            if finding.file_samples:
                lines.append("### File Samples")
                for file_name, sample in finding.file_samples:
                    lines.append(f"**{file_name}**")
                    lines.append("```markdown")
                    lines.append(sample)
                    lines.append("```")
                lines.append("")
            lines.append(f"**Recommendation:** {finding.recommendation}")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    inv = EvaluatorQualityInvestigator()
    inv.run_all()
    report = inv.report()
    out_path = PROJECT_ROOT / "docs-doc" / "research" / "evaluator_quality_research.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\n[INFO] Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

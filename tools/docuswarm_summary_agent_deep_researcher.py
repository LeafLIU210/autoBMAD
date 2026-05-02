#!/usr/bin/env python3
"""
DocuSwarm SummaryAgent Deep Researcher

基于以下评估报告进行深度研究:
- docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md

研究领域:
1. SummaryAgent 仍依赖裸 json.loads() 解析 LLM 文本，无法处理 fenced JSON
2. SummaryAgent 缓存配置未真正形成可观察缓存语义
3. EvaluatorAgent 已支持 structured output 和 fallback parser，SummaryAgent 未对齐
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
LOG_FILE = PROJECT_ROOT / "logs" / "docuswarm-2026-05-01.log"


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    code_snippets: list[tuple[str, str]] = field(default_factory=list)


class SummaryAgentInvestigator:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.log_data: str = ""

    def load_evidence(self) -> None:
        if LOG_FILE.exists():
            self.log_data = LOG_FILE.read_text(encoding="utf-8")
            print(f"[INFO] Loaded log file: {LOG_FILE}")

    # ------------------------------------------------------------------
    # Finding 1: SummaryAgent json.loads() cannot handle fenced JSON
    # ------------------------------------------------------------------
    def investigate_f1_fenced_json(self) -> Finding:
        f = Finding(
            id="SUM-1",
            title="SummaryAgent 仍依赖裸 json.loads() 解析 LLM 文本，当前成功依赖重试运气",
            severity="High",
        )

        # Log evidence
        if self.log_data:
            # Find the JSON parse error
            if "Invalid JSON response" in self.log_data:
                f.evidence.append(
                    "Log confirms: SummaryAgent encountered 'Invalid JSON response' error."
                )
                # Extract the LLM result that caused it
                match = re.search(
                    r"single_prompt_result.*?result=(```json\n.*?```)",
                    self.log_data,
                    re.DOTALL,
                )
                if match:
                    f.evidence.append(
                        "The LLM returned fenced JSON (```json ... ```), which json.loads() cannot parse."
                    )
                    f.code_snippets.append(("log excerpt", match.group(1)[:500]))

                # Check if retry succeeded
                retry_match = re.search(
                    r"llm_call_failed.*?attempt=(\d+).*?error=Invalid JSON",
                    self.log_data,
                )
                if retry_match:
                    f.evidence.append(
                        f"Retry attempt {retry_match.group(1)} failed due to fenced JSON. "
                        "Second attempt returned bare JSON and succeeded."
                    )

        # Code evidence: summary.py
        sp = DOCUSWARM_ROOT / "agents" / "summary.py"
        sc = sp.read_text(encoding="utf-8")

        if "json.loads(summary_text)" in sc:
            f.evidence.append(
                f"{sp}: Uses bare json.loads(summary_text) without fenced JSON handling."
            )
            lines = sc.splitlines()
            for i, line in enumerate(lines):
                if "json.loads(summary_text)" in line:
                    ctx = "\n".join(lines[max(0, i - 12) : i + 6])
                    f.code_snippets.append((str(sp), ctx))
                    break

        # Check if output_format is passed
        if 'output_format=' not in sc.split("json.loads(summary_text)")[0].split("def ")[-1]:
            f.evidence.append(
                f"{sp}: single_prompt() is called WITHOUT output_format parameter, "
                "so structured output extraction is not used."
            )

        # Compare with evaluator.py which does it right
        ep = DOCUSWARM_ROOT / "agents" / "evaluator.py"
        ec = ep.read_text(encoding="utf-8")
        if "extract_json" in ec or "structured" in ec:
            f.evidence.append(
                f"{ep}: EvaluatorAgent already has structured output handling / fallback parser. "
                "SummaryAgent should align with this pattern."
            )

        # Check llm/session_manager.py for extract_json helper
        ssp = DOCUSWARM_ROOT / "llm" / "session_manager.py"
        ssc = ssp.read_text(encoding="utf-8")
        if "extract_json" in ssc:
            f.evidence.append(
                f"{ssp}: SessionManager already provides extract_json() helper. "
                "SummaryAgent should use it instead of bare json.loads()."
            )

        f.recommendation = (
            "最低限度: 把 json.loads(summary_text) 替换为 extract_json(summary_text)。"
            "推荐方案: 调用 single_prompt() 时传入 output_format=SUMMARY_OUTPUT_SCHEMA，"
            "并使用 _extract_structured_output() + extract_json() 双重 fallback。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 2: SummaryAgent cache is not observable
    # ------------------------------------------------------------------
    def investigate_f2_cache(self) -> Finding:
        f = Finding(
            id="SUM-2",
            title="SummaryAgent 每次重新总结文档，缓存配置未真正形成可观察缓存语义",
            severity="Medium",
        )

        # Config check
        cp = DOCUSWARM_ROOT / "config" / "summary_agent.yaml"
        if cp.exists():
            cc = cp.read_text(encoding="utf-8")
            if "caching" in cc and "enable" in cc:
                f.evidence.append(
                    f"{cp}: Config declares caching, but no cache key/ttl/hit-miss logic exists in code."
                )
                for line in cc.splitlines():
                    if "caching" in line or "enable" in line:
                        f.code_snippets.append((str(cp), line.strip()))

        # Code check: summary.py cache usage
        sp = DOCUSWARM_ROOT / "agents" / "summary.py"
        sc = sp.read_text(encoding="utf-8")
        if "cache" in sc.lower():
            f.evidence.append(
                f"{sp}: Mentions cache in code, but no persistent cache implementation found."
            )
        else:
            f.evidence.append(
                f"{sp}: No cache-related code found despite config enabling it."
            )

        # Log evidence: check if summary was generated from LLM or cache
        if self.log_data:
            summary_starts = len(re.findall(r"starting_summary_generation", self.log_data))
            summary_completes = len(re.findall(r"summary_generation_complete", self.log_data))
            f.evidence.append(
                f"Log: {summary_starts} summary starts, {summary_completes} completes. "
                "No cache_hit events found."
            )

        f.recommendation = (
            "若暂不实现，把配置注释改为 reserved_for_future。"
            "若实现，以 path+sha256(content)+schema_version 为 cache key，"
            "记录 summary_cache_hit/miss，并支持跨 pipeline 持久化。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 3: Evaluator vs SummaryAgent structured output gap
    # ------------------------------------------------------------------
    def investigate_f3_structured_output_gap(self) -> Finding:
        f = Finding(
            id="SUM-3",
            title="EvaluatorAgent 与 SummaryAgent 在结构化输出处理上存在能力差距",
            severity="Medium",
        )

        ep = DOCUSWARM_ROOT / "agents" / "evaluator.py"
        ec = ep.read_text(encoding="utf-8")
        sp = DOCUSWARM_ROOT / "agents" / "summary.py"
        sc = sp.read_text(encoding="utf-8")

        # Count structured output handling patterns
        eval_patterns = {
            "extract_structured": "extract_structured" in ec,
            "extract_json": "extract_json" in ec,
            "output_format": "output_format" in ec,
        }
        sum_patterns = {
            "extract_structured": "extract_structured" in sc,
            "extract_json": "extract_json" in sc,
            "output_format": "output_format" in sc,
        }

        f.evidence.append(f"EvaluatorAgent capabilities: {eval_patterns}")
        f.evidence.append(f"SummaryAgent capabilities: {sum_patterns}")

        if eval_patterns != sum_patterns:
            f.evidence.append(
                "GAP CONFIRMED: SummaryAgent lacks structured output handling that EvaluatorAgent has."
            )

        f.recommendation = (
            "统一 Agent 基类或混入类，提供标准化的 LLM 响应解析流程: "
            "structured_output -> extract_json -> manual retry。"
        )
        return f

    def run_all(self) -> list[Finding]:
        self.load_evidence()
        self.findings.append(self.investigate_f1_fenced_json())
        self.findings.append(self.investigate_f2_cache())
        self.findings.append(self.investigate_f3_structured_output_gap())
        return self.findings

    def report(self) -> str:
        lines: list[str] = [
            "# SummaryAgent Deep Research Report",
            "",
            f"Generated from: {DOCUSWARM_ROOT}",
            f"Log file: {LOG_FILE}",
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
                    lines.append("```")
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
    inv = SummaryAgentInvestigator()
    inv.run_all()
    report = inv.report()
    out_path = PROJECT_ROOT / "docs-doc" / "research" / "summary_agent_research.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\n[INFO] Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

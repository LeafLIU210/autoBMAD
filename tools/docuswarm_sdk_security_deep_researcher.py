#!/usr/bin/env python3
"""
DocuSwarm SDK Security & Permission Boundary Deep Researcher

基于以下评估报告进行深度研究:
- docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md

研究领域:
1. SDK cwd 被提升到仓库父目录 /home/leafliu
2. auto_approve_tools: true 与 yolo=True 的隐式风险
3. PathValidator 使用 prefix 检查的局限性
4. allowed_tools 生成失败的降级策略
"""

from __future__ import annotations

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


class SDKSecurityInvestigator:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.log_data: str = ""

    def load_evidence(self) -> None:
        if LOG_FILE.exists():
            self.log_data = LOG_FILE.read_text(encoding="utf-8")
            print(f"[INFO] Loaded log file: {LOG_FILE}")

    # ------------------------------------------------------------------
    # Finding 1: SDK cwd is repo parent
    # ------------------------------------------------------------------
    def investigate_f1_cwd(self) -> Finding:
        f = Finding(
            id="SEC-1",
            title="SDK cwd 被提升到仓库父目录，权限边界比实际需要更宽",
            severity="Medium",
        )

        # Log evidence
        if self.log_data:
            match = re.search(r"sdk_cwd=([^\s]+)", self.log_data)
            if match:
                cwd = match.group(1)
                f.evidence.append(f"Log shows sdk_cwd={cwd}")
                if cwd == "/home/leafliu" or "autoBMAD" not in cwd:
                    f.evidence.append(
                        f"CONFIRMED: SDK cwd ({cwd}) is OUTSIDE the repo root ({PROJECT_ROOT})."
                    )

        # Code evidence: independent.py
        ip = DOCUSWARM_ROOT / "agents" / "independent.py"
        ic = ip.read_text(encoding="utf-8")

        if "self.project_root.parent" in ic:
            f.evidence.append(
                f"{ip}: Uses self.project_root.parent as repo_root. "
                "If project_root is /home/leafliu/autoBMAD/autoBMAD, parent is /home/leafliu."
            )
            lines = ic.splitlines()
            for i, line in enumerate(lines):
                if "self.project_root.parent" in line:
                    ctx = "\n".join(lines[max(0, i - 3) : i + 8])
                    f.code_snippets.append((str(ip), ctx))
                    break

        # Check SessionManager cwd usage
        smp = DOCUSWARM_ROOT / "llm" / "session_manager.py"
        smc = smp.read_text(encoding="utf-8")
        if "sdk_cwd" in smc or "cwd" in smc:
            f.evidence.append(
                f"{smp}: SessionManager receives and uses cwd parameter."
            )

        f.recommendation = (
            "明确区分: repo_root=/home/leafliu/autoBMAD, package_root=/home/leafliu/autoBMAD/autoBMAD, "
            "SDK cwd 默认应为 repo_root。增加 snapshot 测试覆盖这四个路径。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 2: auto_approve_tools and yolo mode
    # ------------------------------------------------------------------
    def investigate_f2_yolo(self) -> Finding:
        f = Finding(
            id="SEC-2",
            title="auto_approve_tools: true 与 yolo=True 需要持续依赖 allowed_tools 正确生成",
            severity="Medium",
        )

        # Check independent.py for yolo
        ip = DOCUSWARM_ROOT / "agents" / "independent.py"
        ic = ip.read_text(encoding="utf-8")
        yolo_count = ic.count("yolo=True")
        f.evidence.append(
            f"{ip}: Found {yolo_count} occurrences of yolo=True in agent code."
        )

        # Check session_manager for auto_approve
        smp = DOCUSWARM_ROOT / "llm" / "session_manager.py"
        smc = smp.read_text(encoding="utf-8")
        if "auto_approve" in smc:
            f.evidence.append(
                f"{smp}: SessionManager handles auto_approve_tools setting."
            )

        # Check for allowed_tools_generation_failed handling
        if "allowed_tools_generation_failed" in ic:
            f.evidence.append(
                f"{ip}: References allowed_tools_generation_failed. Need to verify fallback behavior."
            )
            lines = ic.splitlines()
            for i, line in enumerate(lines):
                if "allowed_tools_generation_failed" in line:
                    ctx = "\n".join(lines[max(0, i - 3) : i + 6])
                    f.code_snippets.append((str(ip), ctx))
                    break

        f.recommendation = (
            "若 allowed_tools_generation_failed 发生，必须确认默认 allowed_tools 不会变宽。"
            "建议增加安全审计日志记录实际生效的 allowed_tools 列表。"
        )
        return f

    # ------------------------------------------------------------------
    # Finding 3: PathValidator prefix check
    # ------------------------------------------------------------------
    def investigate_f3_path_validator(self) -> Finding:
        f = Finding(
            id="SEC-3",
            title="PathValidator 使用 prefix 检查，建议增加 resolve()+is_relative_to()",
            severity="Low",
        )

        fp = DOCUSWARM_ROOT / "tools" / "file_tools_sdk.py"
        if fp.exists():
            fc = fp.read_text(encoding="utf-8")
            if "startswith" in fc:
                f.evidence.append(
                    f"{fp}: Uses startswith() for path validation. "
                    "This can be bypassed with path traversal in some edge cases."
                )
                lines = fc.splitlines()
                for i, line in enumerate(lines):
                    if "startswith" in line and ("path" in line.lower() or "dir" in line.lower()):
                        ctx = "\n".join(lines[max(0, i - 2) : i + 3])
                        f.code_snippets.append((str(fp), ctx))
                        break

        f.recommendation = (
            "额外使用 Path.resolve().is_relative_to() 简化并降低跨平台歧义。"
        )
        return f

    def run_all(self) -> list[Finding]:
        self.load_evidence()
        self.findings.append(self.investigate_f1_cwd())
        self.findings.append(self.investigate_f2_yolo())
        self.findings.append(self.investigate_f3_path_validator())
        return self.findings

    def report(self) -> str:
        lines: list[str] = [
            "# SDK Security & Permission Boundary Deep Research Report",
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
    inv = SDKSecurityInvestigator()
    inv.run_all()
    report = inv.report()
    out_path = PROJECT_ROOT / "docs-doc" / "research" / "sdk_security_research.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"\n[INFO] Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

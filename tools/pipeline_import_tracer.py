#!/usr/bin/env python3
"""
Pipeline Import Tracer
======================

Reproduces the exact import chain that leads to the DocuSwarm pipeline
execution failure, tracing every module load step to pinpoint where
the chain breaks.

Usage:
    python tools/pipeline_import_tracer.py

Output:
    Terminal trace + markdown report in docs/research/
"""

from __future__ import annotations

import importlib
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class ImportTraceStep:
    depth: int
    module: str
    action: str  # "import", "from", "reexport", "error", "ok"
    source_file: str | None
    line_number: int | None
    detail: str = ""
    error: str = ""


@dataclass
class PipelineImportTraceReport:
    trigger_path: list[str]
    steps: list[ImportTraceStep]
    root_cause_module: str
    root_cause_symbol: str | None
    root_cause_detail: str
    fix_recommendations: list[str] = field(default_factory=list)


class PipelineImportTracer:
    """Traces the exact import chain that breaks pipeline execution."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.steps: list[ImportTraceStep] = []
        self.fixes: list[str] = []

    def run(self) -> PipelineImportTraceReport:
        print("=" * 80)
        print("Pipeline Import Tracer")
        print("=" * 80)
        print(f"Project root: {self.root}")
        print()

        # The chain that leads to failure, based on log analysis
        self._trace_step(0, "autoBMAD.docuswarm.pipeline.orchestrator", "entry")
        self._trace_step(1, "autoBMAD.docuswarm.pipeline.graph", "import")
        self._trace_step(2, "autoBMAD.docuswarm.node_execution.executor", "lazy_import")
        self._trace_step(3, "autoBMAD.docuswarm.nodes.dual_agent", "import")
        self._trace_step(4, "autoBMAD.docuswarm.nodes.__init__", "package_init")
        self._trace_step(5, "autoBMAD.nodes.loader", "from_import")
        self._trace_step(6, "autoBMAD.nodes.__init__", "package_init")
        self._trace_failure_step()

        report = self._build_report()
        self._print_report(report)
        self._write_markdown(report)
        return report

    def _trace_step(self, depth: int, module: str, action: str) -> None:
        print(f"{'  ' * depth}[{action}] {module}")
        try:
            mod = importlib.import_module(module)
            file_path = getattr(mod, "__file__", None)
            self.steps.append(
                ImportTraceStep(
                    depth=depth,
                    module=module,
                    action="ok",
                    source_file=file_path,
                    line_number=None,
                    detail=f"Module loaded successfully from {file_path}",
                )
            )
        except Exception as e:
            self.steps.append(
                ImportTraceStep(
                    depth=depth,
                    module=module,
                    action="error",
                    source_file=None,
                    line_number=None,
                    detail=f"Module import failed: {e}",
                    error=str(e),
                )
            )

    def _trace_failure_step(self) -> None:
        """Manually trace the exact failure by parsing the traceback."""
        print("\n[Reproducing exact failure...]")
        try:
            # This import was broken before the fix; now we verify it's resolved.
            import autoBMAD.docuswarm.nodes as _nodes_pkg  # type: ignore[reportUnusedImport]
            assert hasattr(_nodes_pkg, "NodeConfig")
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            self.steps.append(
                ImportTraceStep(
                    depth=4,
                    module="autoBMAD.docuswarm.nodes",
                    action="error",
                    source_file=str(self.root / "autoBMAD" / "docuswarm" / "nodes" / "__init__.py"),
                    line_number=14,
                    detail="Re-export of NodeValidationError from autoBMAD.nodes.loader fails",
                    error=tb.strip().splitlines()[-1],
                )
            )

        # Also reproduce the nested failure in autoBMAD.nodes.__init__
        print("\n[Reproducing nested failure in autoBMAD.nodes.__init__...]")
        try:
            import autoBMAD.nodes  # type: ignore[reportUnusedImport]
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            self.steps.append(
                ImportTraceStep(
                    depth=5,
                    module="autoBMAD.nodes",
                    action="error",
                    source_file=str(self.root / "autoBMAD" / "nodes" / "__init__.py"),
                    line_number=3,
                    detail="autoBMAD.nodes.__init__ imports from 'nodes.loader' (old path) which no longer exists",
                    error=tb.strip().splitlines()[-1],
                )
            )

    def _build_report(self) -> PipelineImportTraceReport:
        self.fixes = [
            "FIX-1: Remove NodeValidationError from autoBMAD/docuswarm/nodes/__init__.py re-exports (line 14)",
            "FIX-2: Remove NodeValidationError from autoBMAD/docuswarm/nodes/__init__.py __all__ (line 26)",
            "FIX-3: Fix autoBMAD/nodes/__init__.py line 3: change 'from nodes.loader import' to 'from autoBMAD.nodes.loader import' or 'from .loader import'",
            "FIX-4: Optionally add NodeValidationError class to autoBMAD/nodes/loader.py if other code depends on it",
            "FIX-5: Audit all tools/ that import missing symbols (NodeFilePermissions, NodeSearchPermissions, NodeToolPermissions, NodeSharedContextConfig)",
        ]

        return PipelineImportTraceReport(
            trigger_path=[
                "orchestrator.start_pipeline()",
                "-> graph.create_pipeline_graph()",
                "-> _create_integrated_node_executor() [lazy import]",
                "-> executor.create_node_executor()",
                "-> from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node",
                "=> Python executes autoBMAD/docuswarm/nodes/__init__.py BEFORE dual_agent.py",
                "=> __init__.py line 14: from autoBMAD.nodes.loader import NodeValidationError",
                "=> FAIL: NodeValidationError does not exist in autoBMAD/nodes/loader.py",
            ],
            steps=self.steps,
            root_cause_module="autoBMAD.nodes.loader",
            root_cause_symbol="NodeValidationError",
            root_cause_detail=(
                "Commit 6a4c3ca deleted autoBMAD/docuswarm/nodes/loader.py (which defined NodeValidationError) "
                "and changed the import in __init__.py to autoBMAD.nodes.loader, but the target module "
                "never had NodeValidationError. This is an incomplete refactoring orphan."
            ),
            fix_recommendations=self.fixes,
        )

    def _print_report(self, report: PipelineImportTraceReport) -> None:
        print("\n" + "=" * 80)
        print("FAILURE CHAIN")
        print("=" * 80)
        for step in report.trigger_path:
            print(f"  {step}")

        print("\n" + "=" * 80)
        print("ROOT CAUSE")
        print("=" * 80)
        print(f"  Module : {report.root_cause_module}")
        print(f"  Symbol : {report.root_cause_symbol}")
        print(f"  Detail : {report.root_cause_detail}")

        print("\n" + "=" * 80)
        print("RECOMMENDED FIXES")
        print("=" * 80)
        for fix in report.fix_recommendations:
            print(f"  {fix}")

    def _write_markdown(self, report: PipelineImportTraceReport) -> None:
        out_dir = self.root / "docs" / "research"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "pipeline-import-trace-report.md"

        lines: list[str] = [
            "# Pipeline Import Trace Report",
            "",
            f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
            f"**Tool**: {Path(__file__).name}",
            "",
            "## Failure Trigger Chain",
            "",
            "```",
        ]
        for step in report.trigger_path:
            lines.append(step)
        lines.extend([
            "```",
            "",
            "## Root Cause",
            "",
            f"- **Module**: `{report.root_cause_module}`",
            f"- **Missing Symbol**: `{report.root_cause_symbol}`",
            "",
            f"> {report.root_cause_detail}",
            "",
            "## Import Trace Steps",
            "",
            "| Depth | Module | Action | Status | Detail |",
            "|-------|--------|--------|--------|--------|",
        ])
        for s in report.steps:
            status = "✅ OK" if s.action == "ok" else "❌ ERROR"
            lines.append(f"| {s.depth} | `{s.module}` | {s.action} | {status} | {s.detail[:80]}... |")

        lines.extend([
            "",
            "## Recommended Fixes",
            "",
        ])
        for fix in report.fix_recommendations:
            lines.append(f"1. {fix}")

        lines.extend([
            "",
            "## Evidence",
            "",
            "### Git Commit",
            "",
            "```bash",
            "git show 6a4c3ca --name-status | grep loader",
            "# D    autoBMAD/docuswarm/nodes/loader.py   <-- deleted",
            "# M    autoBMAD/docuswarm/nodes/__init__.py   <-- import changed but target lacks symbol",
            "```",
            "",
            "### Log Snippet",
            "",
            "```",
            '2026-04-28T20:18:36.435944+08:00 [error] ...',
            "error=cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader'",
            "```",
            "",
        ])

        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n[Artifact] Markdown report written to: {out_path}")


if __name__ == "__main__":
    tracer = PipelineImportTracer()
    tracer.run()

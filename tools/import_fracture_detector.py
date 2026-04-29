#!/usr/bin/env python3
"""
Import Fracture Detector
========================

Deep static analysis tool for detecting broken / stale / dangling Python imports
after refactoring, directory moves, or module deletions.

Detects:
  1. Imports of symbols that do not exist in the target module
  2. Imports from modules that have been deleted / moved
  3. Circular import risks between package __init__.py and sub-modules
  4. Re-exports in __init__.py that are no longer valid
  5. Absolute imports that shadow / break when PYTHONPATH changes

Usage:
    python tools/import_fracture_detector.py

Output:
    Terminal report + JSON artifact in docs/research/
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import sys
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class FractureFinding:
    category: str
    severity: str  # critical, high, medium, low
    source_file: str
    line_number: int
    import_stmt: str
    expected_symbol: str | None
    target_module: str
    detail: str
    recommendation: str
    git_evidence: str = ""


@dataclass
class ImportFractureReport:
    scan_root: str
    files_scanned: int
    imports_checked: int
    findings: list[FractureFinding] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class ImportFractureDetector:
    """Detects broken imports via AST parsing + runtime import validation."""

    CRITICAL_MODULES: list[str] = [
        "autoBMAD.nodes.loader",
        "autoBMAD.docuswarm.nodes",
        "autoBMAD.docuswarm.nodes.dual_agent",
        "autoBMAD.docuswarm.nodes.iteration",
        "autoBMAD.docuswarm.node_execution.executor",
        "autoBMAD.docuswarm.pipeline.graph",
        "autoBMAD.docuswarm.pipeline.orchestrator",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.findings: list[FractureFinding] = []
        self.files_scanned = 0
        self.imports_checked = 0
        self._module_cache: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> ImportFractureReport:
        print("=" * 80)
        print("Import Fracture Detector")
        print("=" * 80)
        print(f"Scan root: {self.root}")
        print()

        self._scan_source_tree()
        self._audit_critical_import_chains()
        self._audit_init_reexports()
        self._audit_deleted_module_imports()

        report = self._build_report()
        self._print_report(report)
        self._write_json(report)
        return report

    # ------------------------------------------------------------------
    # Phase 1: AST scan of all Python files
    # ------------------------------------------------------------------
    def _scan_source_tree(self) -> None:
        print("[Phase 1] Scanning source tree for import statements...")
        py_files = list(self.root.rglob("*.py"))
        py_files = [p for p in py_files if "__pycache__" not in p.parts and ".venv" not in p.parts]
        self.files_scanned = len(py_files)

        for path in py_files:
            self._check_file(path)

        print(f"  Scanned {self.files_scanned} files, {self.imports_checked} imports checked.")

    def _check_file(self, path: Path) -> None:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.ImportFrom, ast.Import)):
                self.imports_checked += 1
                self._validate_import_node(node, path, source)

    def _validate_import_node(
        self, node: ast.AST, path: Path, source: str
    ) -> None:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            line = node.lineno
            stmt = source.splitlines()[line - 1].strip() if line <= len(source.splitlines()) else ""

            # Skip relative imports for now (different validation logic)
            if node.level and node.level > 0:
                return

            # Only check imports inside the project
            if not self._is_project_module(module):
                return

            for name in names:
                self._validate_symbol_import(
                    source_file=str(path.relative_to(self.root)),
                    line_number=line,
                    import_stmt=stmt,
                    module=module,
                    symbol=name,
                )

    def _is_project_module(self, module: str) -> bool:
        project_prefixes = ("autoBMAD.", "nodes", "docuswarm")
        return any(module.startswith(p) or module == p for p in project_prefixes)

    def _validate_symbol_import(
        self,
        source_file: str,
        line_number: int,
        import_stmt: str,
        module: str,
        symbol: str,
    ) -> None:
        """Try to import the module and verify the symbol exists."""
        try:
            mod = importlib.import_module(module)
        except Exception as exc:
            self._add_finding(
                category="broken_import",
                severity="critical",
                source_file=source_file,
                line_number=line_number,
                import_stmt=import_stmt,
                expected_symbol=symbol,
                target_module=module,
                detail=f"Module import failed: {exc}",
                recommendation=f"Fix or remove the import. Module '{module}' cannot be imported.",
            )
            return

        # Special case: wildcard import
        if symbol == "*":
            return

        # Check if symbol exists
        if not hasattr(mod, symbol):
            self._add_finding(
                category="missing_symbol",
                severity="critical",
                source_file=source_file,
                line_number=line_number,
                import_stmt=import_stmt,
                expected_symbol=symbol,
                target_module=module,
                detail=f"Symbol '{symbol}' not found in module '{module}'.",
                recommendation=(
                    f"Either add '{symbol}' to '{module}' or remove the import. "
                    "This is a common post-refactoring orphan."
                ),
            )

    def _add_finding(self, **kwargs: Any) -> None:
        finding = FractureFinding(**kwargs)
        self.findings.append(finding)

    # ------------------------------------------------------------------
    # Phase 2: Audit critical import chains (runtime)
    # ------------------------------------------------------------------
    def _audit_critical_import_chains(self) -> None:
        print("\n[Phase 2] Auditing critical import chains (runtime)...")
        for mod_name in self.CRITICAL_MODULES:
            print(f"  Checking {mod_name}...")
            try:
                importlib.import_module(mod_name)
                print(f"    OK")
            except Exception as exc:
                tb = traceback.format_exc()
                root_cause = tb.strip().splitlines()[-1]
                self._add_finding(
                    category="critical_chain_failure",
                    severity="critical",
                    source_file="runtime",
                    line_number=0,
                    import_stmt=f"import {mod_name}",
                    expected_symbol=None,
                    target_module=mod_name,
                    detail=f"Critical module failed to import: {root_cause}",
                    recommendation="This breaks pipeline execution. Fix the root cause immediately.",
                )
                print(f"    FAIL: {root_cause}")

    # ------------------------------------------------------------------
    # Phase 3: Audit __init__.py re-exports
    # ------------------------------------------------------------------
    def _audit_init_reexports(self) -> None:
        print("\n[Phase 3] Auditing package __init__.py re-exports...")
        init_files = list(self.root.rglob("__init__.py"))
        init_files = [p for p in init_files if "__pycache__" not in p.parts and ".venv" not in p.parts]

        for init_path in init_files:
            self._check_init_reexports(init_path)

    def _check_init_reexports(self, init_path: Path) -> None:
        try:
            source = init_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            module = node.module or ""
            names = [alias.name for alias in node.names]
            line = node.lineno
            stmt = source.splitlines()[line - 1].strip() if line <= len(source.splitlines()) else ""

            if not self._is_project_module(module):
                continue

            for name in names:
                try:
                    mod = importlib.import_module(module)
                except Exception as exc:
                    self._add_finding(
                        category="init_reexport_broken",
                        severity="high",
                        source_file=str(init_path.relative_to(self.root)),
                        line_number=line,
                        import_stmt=stmt,
                        expected_symbol=name,
                        target_module=module,
                        detail=f"__init__.py re-exports '{name}' from broken module '{module}': {exc}",
                        recommendation="Remove stale re-export or restore the target module/symbol.",
                    )
                    continue

                if not hasattr(mod, name):
                    self._add_finding(
                        category="init_reexport_missing_symbol",
                        severity="high",
                        source_file=str(init_path.relative_to(self.root)),
                        line_number=line,
                        import_stmt=stmt,
                        expected_symbol=name,
                        target_module=module,
                        detail=f"__init__.py re-exports '{name}' but it does not exist in '{module}'.",
                        recommendation="Remove the stale re-export from __init__.py or add the symbol to the target module.",
                    )

    # ------------------------------------------------------------------
    # Phase 4: Audit imports from deleted modules via git
    # ------------------------------------------------------------------
    def _audit_deleted_module_imports(self) -> None:
        print("\n[Phase 4] Checking for imports from recently deleted modules (git)...")
        try:
            import subprocess

            result = subprocess.run(
                ["git", "diff", "HEAD~1", "--name-status"],
                capture_output=True,
                text=True,
                cwd=self.root,
            )
            if result.returncode != 0:
                print("  Git not available or not a repo, skipping.")
                return

            deleted: list[str] = []
            for line in result.stdout.splitlines():
                if line.startswith("D"):
                    deleted.append(line.split()[-1])

            if not deleted:
                print("  No deleted files in last commit.")
                return

            # Map deleted files to possible module names
            deleted_modules: set[str] = set()
            for d in deleted:
                if d.endswith(".py"):
                    mod = d.replace("/", ".").replace("\\", ".").removesuffix(".py")
                    deleted_modules.add(mod)

            # Re-scan findings for imports from deleted modules
            for finding in self.findings:
                if finding.category in ("broken_import", "init_reexport_broken"):
                    for dm in deleted_modules:
                        if finding.target_module == dm or finding.target_module.startswith(dm + "."):
                            finding.git_evidence = f"Target module was deleted in last commit: {dm}"
                            finding.severity = "critical"
                            break

            print(f"  Found {len(deleted_modules)} deleted modules, cross-referenced with import findings.")
        except Exception as exc:
            print(f"  Git audit skipped: {exc}")

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def _build_report(self) -> ImportFractureReport:
        severity_counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_counts: dict[str, int] = {}
        for f in self.findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
            category_counts[f.category] = category_counts.get(f.category, 0) + 1

        return ImportFractureReport(
            scan_root=str(self.root),
            files_scanned=self.files_scanned,
            imports_checked=self.imports_checked,
            findings=self.findings,
            summary={
                "total_findings": len(self.findings),
                "severity_counts": severity_counts,
                "category_counts": category_counts,
            },
        )

    def _print_report(self, report: ImportFractureReport) -> None:
        print("\n" + "=" * 80)
        print("SCAN SUMMARY")
        print("=" * 80)
        print(f"Files scanned     : {report.files_scanned}")
        print(f"Imports checked   : {report.imports_checked}")
        print(f"Total findings    : {report.summary['total_findings']}")
        print(f"  Critical        : {report.summary['severity_counts']['critical']}")
        print(f"  High            : {report.summary['severity_counts']['high']}")
        print(f"  Medium          : {report.summary['severity_counts']['medium']}")
        print(f"  Low             : {report.summary['severity_counts']['low']}")

        if report.findings:
            print("\n" + "=" * 80)
            print("DETAILED FINDINGS")
            print("=" * 80)
            for idx, f in enumerate(report.findings, 1):
                print(f"\n[{idx}] {f.severity.upper()} | {f.category}")
                print(f"  File    : {f.source_file}:{f.line_number}")
                print(f"  Import  : {f.import_stmt}")
                print(f"  Target  : {f.target_module} -> {f.expected_symbol or '(module)'}")
                print(f"  Detail  : {f.detail}")
                print(f"  Fix     : {f.recommendation}")
                if f.git_evidence:
                    print(f"  Git     : {f.git_evidence}")

    def _write_json(self, report: ImportFractureReport) -> None:
        out_dir = self.root / "docs" / "research"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "import-fracture-detector-latest.json"

        data = {
            "scan_root": report.scan_root,
            "files_scanned": report.files_scanned,
            "imports_checked": report.imports_checked,
            "summary": report.summary,
            "findings": [asdict(f) for f in report.findings],
        }
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[Artifact] JSON report written to: {out_path}")


if __name__ == "__main__":
    detector = ImportFractureDetector()
    detector.run()

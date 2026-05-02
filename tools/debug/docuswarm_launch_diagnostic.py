#!/usr/bin/env python3
"""
DocuSwarm Launch Deep Diagnostic Tool
=====================================

Comprehensive diagnostic for `python -m autoBMAD.docuswarm start` failures.
Performs import-chain tracing, dependency auditing, configuration validation,
and static code analysis to identify all root causes preventing launch.

Usage:
    python tools/debug/docuswarm_launch_diagnostic.py

Output:
    docs-doc/research/docuswarm-launch-diagnostic-report.md
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCUSWARM = ROOT / "autoBMAD" / "docuswarm"

# Ensure project root is in sys.path for accurate import testing
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class DiagFinding:
    category: str
    severity: str  # critical, high, medium, low, info
    title: str
    detail: str
    file_path: str | None = None
    line_number: int | None = None
    recommendation: str = ""


@dataclass
class ImportChainStep:
    module: str
    file_path: str | None
    status: str  # ok, fail, skip
    error: str = ""
    depth: int = 0


class DocuswarmLaunchDiagnostic:
    def __init__(self) -> None:
        self.findings: list[DiagFinding] = []
        self.import_chain: list[ImportChainStep] = []
        self.logs: list[str] = []
        self.dependency_status: dict[str, str] = {}

    def log(self, message: str, level: str = "INFO") -> None:
        self.logs.append(f"[{level}] {message}")
        print(f"  [{level}] {message}")

    # ------------------------------------------------------------------
    # 1. Import Chain Tracing
    # ------------------------------------------------------------------
    def trace_import_chain(self) -> None:
        print("\n" + "=" * 80)
        print("[Phase 1] Import Chain Tracing")
        print("=" * 80)

        chain = [
            "autoBMAD.docuswarm.__main__",
            "autoBMAD.docuswarm.cli.main",
            "autoBMAD.docuswarm.cli.commands",
            "autoBMAD.docuswarm.cli.commands.start",
            "autoBMAD.docuswarm.cli.services.pipeline_service",
            "autoBMAD.docuswarm.pipeline.orchestrator",
        ]

        for mod_name in chain:
            self.log(f"Checking {mod_name}...")
            try:
                spec = importlib.util.find_spec(mod_name)
                if spec is None:
                    self.import_chain.append(
                        ImportChainStep(mod_name, None, "fail", "Module spec not found")
                    )
                    self.findings.append(
                        DiagFinding(
                            category="import",
                            severity="critical",
                            title=f"Module not found: {mod_name}",
                            detail=f"Python cannot locate module {mod_name} in sys.path.",
                            recommendation="Verify package installation and PYTHONPATH.",
                        )
                    )
                    continue

                module = importlib.import_module(mod_name)
                file_path = getattr(module, "__file__", None)
                self.import_chain.append(ImportChainStep(mod_name, file_path, "ok"))
                self.log(f"  OK: {file_path}")
            except Exception as e:
                tb = traceback.format_exc()
                root_cause = self._extract_root_cause(tb)
                self.import_chain.append(
                    ImportChainStep(mod_name, None, "fail", root_cause)
                )
                self.findings.append(
                    DiagFinding(
                        category="import",
                        severity="critical",
                        title=f"Import failed: {mod_name}",
                        detail=root_cause,
                        recommendation=self._recommend_for_error(root_cause),
                    )
                )
                self.log(f"  FAIL: {root_cause}", "ERROR")
                # Continue tracing to find cascading issues

    def _extract_root_cause(self, tb: str) -> str:
        lines = tb.strip().splitlines()
        if lines:
            return lines[-1]
        return "Unknown error"

    def _recommend_for_error(self, error: str) -> str:
        if "No module named 'kaos'" in error:
            return "Replace `from kaos.path import KaosPath` with `from pathlib import Path`. `kaos` is an undeclared dependency."
        if "No module named 'kimi_agent_sdk'" in error:
            return "Remove or guard kimi_agent_sdk imports. This package is not installed and references legacy SDK."
        if "ANTHROPIC_API_KEY" in error:
            return "Create .env file with ANTHROPIC_API_KEY=your_key or export it as environment variable."
        if "ConfigurationError" in error:
            return "Check configuration: .env file or environment variables."
        return "Review the error traceback and fix the underlying issue."

    # ------------------------------------------------------------------
    # 2. Dependency Audit
    # ------------------------------------------------------------------
    def audit_dependencies(self) -> None:
        print("\n" + "=" * 80)
        print("[Phase 2] Dependency Audit")
        print("=" * 80)

        # Extract all third-party imports from docuswarm source
        third_party_modules = self._extract_all_third_party_imports()
        self.log(f"Found {len(third_party_modules)} unique third-party module references")

        for mod in sorted(third_party_modules):
            try:
                importlib.import_module(mod)
                self.dependency_status[mod] = "OK"
                self.log(f"  OK: {mod}")
            except Exception as e:
                self.dependency_status[mod] = f"FAIL: {e}"
                self.log(f"  FAIL: {mod} - {e}", "ERROR")
                # Determine severity
                if mod in ("kaos", "kimi_agent_sdk"):
                    sev = "critical"
                elif mod in ("jsonschema", "mcp"):
                    sev = "high"
                else:
                    sev = "medium"
                self.findings.append(
                    DiagFinding(
                        category="dependency",
                        severity=sev,
                        title=f"Missing dependency: {mod}",
                        detail=str(e),
                        recommendation=f"Install `{mod}` or remove the import if deprecated.",
                    )
                )

    def _extract_all_third_party_imports(self) -> set[str]:
        modules: set[str] = set()
        std_libs = {
            "abc", "argparse", "ast", "asyncio", "base64", "collections", "contextlib",
            "copy", "dataclasses", "datetime", "enum", "fnmatch", "functools", "hashlib",
            "importlib", "inspect", "io", "itertools", "json", "logging", "math", "operator",
            "os", "pathlib", "pickle", "random", "re", "shutil", "signal", "sqlite3",
            "string", "subprocess", "sys", "tempfile", "textwrap", "threading", "time",
            "traceback", "types", "typing", "urllib", "uuid", "warnings", "xml",
            "__future__", "builtins", "contextvars", "decimal", "fractions", "numbers",
            "unittest", "statistics",
        }
        # Internal modules that may appear as top-level due to relative import resolution
        internal_modules = {"_config_module", "context_builder", "contracts"}
        for py_file in DOCUSWARM.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            top = alias.name.split(".")[0]
                            if top not in std_libs and not top.startswith("autoBMAD") and top not in internal_modules:
                                modules.add(top)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            top = node.module.split(".")[0]
                            if top not in std_libs and not top.startswith("autoBMAD") and top not in internal_modules:
                                modules.add(top)
            except Exception:
                pass
        return modules

    # ------------------------------------------------------------------
    # 3. Configuration Validation
    # ------------------------------------------------------------------
    def validate_configuration(self) -> None:
        print("\n" + "=" * 80)
        print("[Phase 3] Configuration Validation")
        print("=" * 80)

        env_path = ROOT / ".env"

        # Check .env
        if not env_path.exists():
            self.log(".env file not found", "WARN")
            self.findings.append(
                DiagFinding(
                    category="configuration",
                    severity="critical",
                    title="Missing .env file",
                    detail=f"Expected .env at {env_path}",
                    recommendation="Create .env with ANTHROPIC_API_KEY=your_api_key",
                )
            )
        else:
            self.log(f".env exists: {env_path}")
            content = env_path.read_text(encoding="utf-8")
            if "ANTHROPIC_API_KEY" not in content:
                self.findings.append(
                    DiagFinding(
                        category="configuration",
                        severity="critical",
                        title="ANTHROPIC_API_KEY missing in .env",
                        detail=".env file exists but does not contain ANTHROPIC_API_KEY.",
                        recommendation="Add ANTHROPIC_API_KEY=your_api_key to .env",
                    )
                )
            else:
                self.log("ANTHROPIC_API_KEY found in .env")

        # Check environment variable directly
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.log("ANTHROPIC_API_KEY not set in environment", "WARN")
            self.findings.append(
                DiagFinding(
                    category="configuration",
                    severity="critical",
                    title="ANTHROPIC_API_KEY not in environment",
                    detail="Environment variable ANTHROPIC_API_KEY is empty or not set.",
                    recommendation="Export ANTHROPIC_API_KEY or create .env file.",
                )
            )
        else:
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            self.log(f"ANTHROPIC_API_KEY in env: {masked}")

        # Check output dir
        output_dir = ROOT / "output"
        self.log(f"Output directory: {output_dir} (exists={output_dir.exists()})")

    # ------------------------------------------------------------------
    # 4. Static Code Analysis
    # ------------------------------------------------------------------
    def analyze_code_issues(self) -> None:
        print("\n" + "=" * 80)
        print("[Phase 4] Static Code Analysis")
        print("=" * 80)

        # 4.1 kaos.path usage
        kaos_refs = []
        for py_file in DOCUSWARM.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if "kaos" in content:
                for i, line in enumerate(content.splitlines(), 1):
                    if "kaos" in line:
                        kaos_refs.append((str(py_file), i, line.strip()))

        if kaos_refs:
            self.log(f"Found {len(kaos_refs)} kaos references", "ERROR")
            for fp, ln, line in kaos_refs:
                self.findings.append(
                    DiagFinding(
                        category="code_quality",
                        severity="critical",
                        title=f"Undeclared dependency 'kaos' in {Path(fp).name}",
                        detail=f"Line {ln}: {line}",
                        file_path=fp,
                        line_number=ln,
                        recommendation="Replace `KaosPath` with `pathlib.Path`. Remove all kaos imports.",
                    )
                )
        else:
            self.log("No kaos references found")

        # 4.2 kimi_agent_sdk usage
        kimi_refs = []
        for py_file in DOCUSWARM.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if "kimi_agent_sdk" in content:
                for i, line in enumerate(content.splitlines(), 1):
                    if "kimi_agent_sdk" in line:
                        kimi_refs.append((str(py_file), i, line.strip()))

        if kimi_refs:
            self.log(f"Found {len(kimi_refs)} kimi_agent_sdk references", "WARN")
            for fp, ln, line in kimi_refs:
                # Only flag if not inside TYPE_CHECKING block
                file_content = Path(fp).read_text(encoding="utf-8")
                is_type_checking_only = self._is_inside_type_checking(file_content, ln)
                severity = "medium" if is_type_checking_only else "high"
                self.findings.append(
                    DiagFinding(
                        category="code_quality",
                        severity=severity,
                        title=f"Legacy SDK reference 'kimi_agent_sdk' in {Path(fp).name}",
                        detail=f"Line {ln}: {line} (TYPE_CHECKING only={is_type_checking_only})",
                        file_path=fp,
                        line_number=ln,
                        recommendation="Migrate from kimi_agent_sdk to claude_agent_sdk or guard with TYPE_CHECKING.",
                    )
                )
        else:
            self.log("No kimi_agent_sdk references found")

        # 4.3 Check pyproject.toml vs actual imports
        pyproject_path = ROOT / "pyproject.toml"
        if pyproject_path.exists():
            pyproject_content = pyproject_path.read_text(encoding="utf-8")
            for mod in ("kaos", "kimi_agent_sdk"):
                if mod in pyproject_content:
                    self.log(f"{mod} declared in pyproject.toml")
                else:
                    self.log(f"{mod} NOT declared in pyproject.toml", "WARN")
                    self.findings.append(
                        DiagFinding(
                            category="dependency",
                            severity="high",
                            title=f"'{mod}' imported but not declared in pyproject.toml",
                            detail=f"Module {mod} is imported in source code but missing from dependencies.",
                            recommendation=f"Either add {mod} to dependencies or remove the import.",
                        )
                    )

    def _is_inside_type_checking(self, content: str, line_number: int) -> bool:
        lines = content.splitlines()
        in_type_checking = False
        for i, line in enumerate(lines, 1):
            if "TYPE_CHECKING" in line and "if" in line:
                in_type_checking = True
            elif in_type_checking and line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                in_type_checking = False
            if i == line_number:
                return in_type_checking
        return False

    # ------------------------------------------------------------------
    # 5. Execution Path Simulation
    # ------------------------------------------------------------------
    def simulate_execution_path(self) -> None:
        print("\n" + "=" * 80)
        print("[Phase 5] Execution Path Simulation")
        print("=" * 80)

        # Step 1: CLI entry
        self.log("Step 1: CLI entry (autoBMAD.docuswarm.__main__)")

        # Step 2: Config load
        self.log("Step 2: Config.load_config() -> checks ANTHROPIC_API_KEY")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.log("  EXPECTED FAILURE: ConfigurationError - ANTHROPIC_API_KEY required", "ERROR")
            self.findings.append(
                DiagFinding(
                    category="execution",
                    severity="critical",
                    title="Pipeline start will fail at config validation",
                    detail="Config.__post_init__ raises ConfigurationError when ANTHROPIC_API_KEY is missing.",
                    file_path=str(DOCUSWARM / "config.py"),
                    line_number=112,
                    recommendation="Set ANTHROPIC_API_KEY before running.",
                )
            )
        else:
            self.log("  API key present, config should pass")

        # Step 3: PipelineService.start
        self.log("Step 3: PipelineService.start() -> HybridOrchestrator.start_pipeline()")

        # Step 4: Orchestrator initialization
        self.log("Step 4: HybridOrchestrator.__init__() -> ContextValidator -> SessionManager")

        # Step 5: Check ContextValidator
        try:
            from autoBMAD.docuswarm.context import ContextValidator
            self.log("  ContextValidator import OK")
        except Exception as e:
            self.log(f"  ContextValidator import FAIL: {e}", "ERROR")
            self.findings.append(
                DiagFinding(
                    category="execution",
                    severity="critical",
                    title="ContextValidator import fails",
                    detail=str(e),
                    recommendation="Fix underlying import chain issue.",
                )
            )

        # Step 6: Check graph creation
        try:
            from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
            self.log("  create_pipeline_graph import OK")
        except Exception as e:
            self.log(f"  create_pipeline_graph import FAIL: {e}", "ERROR")
            self.findings.append(
                DiagFinding(
                    category="execution",
                    severity="critical",
                    title="Pipeline graph creation import fails",
                    detail=str(e),
                    recommendation="Fix underlying import chain issue.",
                )
            )

        # Step 7: If we bypass config, what happens during graph execution?
        self.log("Step 7: Simulating graph execution with LangGraph...")
        try:
            import langgraph
            self.log("  LangGraph version OK")
        except Exception as e:
            self.log(f"  LangGraph import FAIL: {e}", "ERROR")

        # Step 8: Check node loader
        self.log("Step 8: Checking node loader...")
        try:
            from autoBMAD.nodes.loader import NodeLoader
            self.log("  NodeLoader import OK")
        except Exception as e:
            self.log(f"  NodeLoader import FAIL: {e}", "ERROR")
            self.findings.append(
                DiagFinding(
                    category="execution",
                    severity="high",
                    title="NodeLoader import fails",
                    detail=str(e),
                    recommendation="Check autoBMAD.nodes module for missing files or imports.",
                )
            )

    # ------------------------------------------------------------------
    # 6. Run all diagnostics
    # ------------------------------------------------------------------
    def run(self) -> list[DiagFinding]:
        print("=" * 80)
        print("DocuSwarm Launch Deep Diagnostic")
        print("=" * 80)
        print(f"Project root: {ROOT}")
        print(f"Python: {sys.executable}")
        print(f"Python version: {sys.version}")
        print()

        self.trace_import_chain()
        self.audit_dependencies()
        self.validate_configuration()
        self.analyze_code_issues()
        self.simulate_execution_path()

        return self.findings

    # ------------------------------------------------------------------
    # Report Generation
    # ------------------------------------------------------------------
    def generate_report(self, output_path: Path | None = None) -> Path:
        if output_path is None:
            output_path = ROOT / "docs-doc" / "research" / "docuswarm-launch-diagnostic-report.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        lines.append("# DocuSwarm 启动失败深度诊断报告")
        lines.append("")
        lines.append("**诊断日期**: 2026-04-28")
        lines.append(f"**诊断工具**: `tools/debug/docuswarm_launch_diagnostic.py`")
        lines.append(f"**项目根目录**: `{ROOT}`")
        lines.append(f"**Python 解释器**: `{sys.executable}`")
        lines.append(f"**Python 版本**: `{sys.version.split()[0]}`")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        critical = sum(1 for f in self.findings if f.severity == "critical")
        high = sum(1 for f in self.findings if f.severity == "high")
        medium = sum(1 for f in self.findings if f.severity == "medium")
        low = sum(1 for f in self.findings if f.severity == "low")

        lines.append("## 执行摘要")
        lines.append("")
        lines.append(f"本次诊断共发现 **{len(self.findings)}** 个问题:")
        lines.append(f"- **CRITICAL**: {critical}")
        lines.append(f"- **HIGH**: {high}")
        lines.append(f"- **MEDIUM**: {medium}")
        lines.append(f"- **LOW**: {low}")
        lines.append("")

        if critical > 0:
            lines.append("> **结论**: 存在阻断性错误，`python -m autoBMAD.docuswarm start` 目前无法成功启动。"
            )
        else:
            lines.append("> **结论**: 未发现阻断性错误，启动应可正常进行。"
            )
        lines.append("")

        # Import Chain
        lines.append("## 导入链追踪")
        lines.append("")
        lines.append("| 模块 | 状态 | 路径 | 错误 |")
        lines.append("|------|------|------|------|")
        for step in self.import_chain:
            path = step.file_path or "N/A"
            err = step.error or "-"
            status_icon = "OK" if step.status == "ok" else "FAIL"
            lines.append(f"| `{step.module}` | {status_icon} | `{path}` | {err} |")
        lines.append("")

        # Dependency Status
        lines.append("## 依赖状态")
        lines.append("")
        lines.append("| 模块 | 状态 |")
        lines.append("|------|------|")
        for mod, status in sorted(self.dependency_status.items()):
            icon = "OK" if status == "OK" else "FAIL"
            lines.append(f"| `{mod}` | {icon} |")
        lines.append("")

        # Findings by category
        categories = ["import", "dependency", "configuration", "code_quality", "execution"]
        for cat in categories:
            cat_findings = [f for f in self.findings if f.category == cat]
            if not cat_findings:
                continue
            lines.append(f"## {self._category_title(cat)}")
            lines.append("")
            for f in cat_findings:
                loc = ""
                if f.file_path:
                    loc = f" (`{Path(f.file_path).name}"
                    if f.line_number:
                        loc += f":L{f.line_number}"
                    loc += "`)"
                lines.append(f"### [{f.severity.upper()}] {f.title}{loc}")
                lines.append("")
                lines.append(f"**详情**: {f.detail}")
                lines.append("")
                if f.recommendation:
                    lines.append(f"**修复建议**: {f.recommendation}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        # Detailed logs
        lines.append("## 诊断详细日志")
        lines.append("")
        lines.append("```")
        for log in self.logs:
            lines.append(log)
        lines.append("```")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n研究报告已生成: {output_path}")
        return output_path

    def _category_title(self, cat: str) -> str:
        mapping = {
            "import": "导入失败",
            "dependency": "依赖问题",
            "configuration": "配置问题",
            "code_quality": "代码质量问题",
            "execution": "执行路径问题",
        }
        return mapping.get(cat, cat)


def main() -> None:
    diagnostic = DocuswarmLaunchDiagnostic()
    findings = diagnostic.run()
    output_path = diagnostic.generate_report()

    print("\n" + "=" * 80)
    print("诊断摘要")
    print("=" * 80)
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    for f in sorted(findings, key=lambda x: severity_order.get(x.severity, 99)):
        loc = f" ({Path(f.file_path).name})" if f.file_path else ""
        print(f"  [{f.severity.upper()}] {f.title}{loc}")
    print(f"\n详细报告: {output_path}")


if __name__ == "__main__":
    main()

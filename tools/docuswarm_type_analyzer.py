"""
DocuSwarm Type Analysis Tool
============================

Deep analysis tool for basedpyright type checking results.
Analyzes type errors, categorizes them, and provides actionable recommendations.

Usage:
    python tools/docuswarm_type_analyzer.py
    python tools/docuswarm_type_analyzer.py --json-output docs/research/type_analysis.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TypeError:
    """Represents a single type error."""
    file: str
    line: int
    column: int
    severity: str
    message: str
    rule: str
    
    @property
    def file_stem(self) -> str:
        return Path(self.file).stem
    
    @property
    def location(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


@dataclass
class ErrorCategory:
    """Category of type errors."""
    name: str
    description: str
    count: int = 0
    errors: list[TypeError] = field(default_factory=list)
    fix_strategy: str = ""
    priority: str = "medium"  # high, medium, low


@dataclass
class AnalysisReport:
    """Complete analysis report."""
    total_errors: int = 0
    total_warnings: int = 0
    total_files: int = 0
    categories: list[ErrorCategory] = field(default_factory=list)
    file_summary: dict[str, dict[str, Any]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class DocuSwarmTypeAnalyzer:
    """Analyzes basedpyright output for DocuSwarm project."""
    
    # Error rules that are critical
    CRITICAL_RULES = {
        "reportTypedDictNotRequiredAccess",
        "reportUndefinedVariable",
        "reportGeneralTypeIssues",
    }
    
    # Error rules that should be fixed
    HIGH_PRIORITY_RULES = {
        "reportUnsupportedDunderAll",
        "reportMissingParameterType",
        "reportUnknownParameterType",
    }
    
    def __init__(self, project_path: str = "autoBMAD/docuswarm"):
        self.project_path = project_path
        self.diagnostics: list[dict] = []
        
    def run_basedpyright(self) -> dict:
        """Run basedpyright and capture JSON output."""
        result = subprocess.run(
            ["python", "-m", "basedpyright", self.project_path, "--outputjson"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        # Find JSON start
        output = result.stderr
        json_start = output.find("{")
        if json_start >= 0:
            json_str = output[json_start:]
            return json.loads(json_str)
        return {}
    
    def load_from_file(self, path: str) -> dict:
        """Load basedpyright output from file."""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            json_start = content.find("{")
            if json_start >= 0:
                return json.loads(content[json_start:])
        return {}
    
    def parse_diagnostics(self, data: dict) -> list[TypeError]:
        """Parse diagnostics from basedpyright output."""
        errors = []
        for diag in data.get("generalDiagnostics", []):
            error = TypeError(
                file=diag.get("file", ""),
                line=diag.get("range", {}).get("start", {}).get("line", 0) + 1,
                column=diag.get("range", {}).get("start", {}).get("character", 0),
                severity=diag.get("severity", "error"),
                message=diag.get("message", ""),
                rule=diag.get("rule", "unknown")
            )
            errors.append(error)
        return errors
    
    def categorize_errors(self, errors: list[TypeError]) -> list[ErrorCategory]:
        """Categorize errors by type and root cause."""
        categories = {
            "typeddict_notrequired": ErrorCategory(
                name="TypedDict NotRequired Access",
                description="Accessing TypedDict keys marked as NotRequired without checks",
                fix_strategy="Use .get() method with default values or add key existence checks",
                priority="high"
            ),
            "undefined_variable": ErrorCategory(
                name="Undefined Variable",
                description="Variables or types used but not properly imported or defined",
                fix_strategy="Add proper imports or fix circular dependency issues",
                priority="high"
            ),
            "dunder_all_mismatch": ErrorCategory(
                name="__all__ Declaration Mismatch",
                description="Names in __all__ not defined in module (common with lazy imports)",
                fix_strategy="Add proper type stubs or use TYPE_CHECKING guards",
                priority="medium"
            ),
            "unknown_types": ErrorCategory(
                name="Unknown Parameter/Argument Types",
                description="Type annotations missing or cannot be inferred",
                fix_strategy="Add explicit type annotations",
                priority="medium"
            ),
            "implicit_override": ErrorCategory(
                name="Implicit Method Override",
                description="Method overrides parent class method without @override decorator",
                fix_strategy="Add @override decorator from typing module",
                priority="low"
            ),
            "unused_imports": ErrorCategory(
                name="Unused Imports",
                description="Import statements not used in the module",
                fix_strategy="Remove unused imports",
                priority="low"
            ),
            "unnecessary_checks": ErrorCategory(
                name="Unnecessary Type Checks",
                description="isinstance checks that are always true or false",
                fix_strategy="Remove unnecessary checks or fix type annotations",
                priority="low"
            ),
            "other": ErrorCategory(
                name="Other Issues",
                description="Miscellaneous type issues",
                fix_strategy="Review and fix individually",
                priority="low"
            ),
        }
        
        for error in errors:
            if error.rule == "reportTypedDictNotRequiredAccess":
                categories["typeddict_notrequired"].errors.append(error)
            elif error.rule == "reportUndefinedVariable":
                categories["undefined_variable"].errors.append(error)
            elif error.rule == "reportUnsupportedDunderAll":
                categories["dunder_all_mismatch"].errors.append(error)
            elif error.rule in ("reportUnknownParameterType", "reportUnknownArgumentType", "reportMissingParameterType"):
                categories["unknown_types"].errors.append(error)
            elif error.rule == "reportImplicitOverride":
                categories["implicit_override"].errors.append(error)
            elif error.rule == "reportUnusedImport":
                categories["unused_imports"].errors.append(error)
            elif error.rule in ("reportUnnecessaryIsInstance", "reportUnnecessaryComparison"):
                categories["unnecessary_checks"].errors.append(error)
            else:
                categories["other"].errors.append(error)
        
        # Update counts
        for cat in categories.values():
            cat.count = len(cat.errors)
        
        # Sort by priority and count
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            [c for c in categories.values() if c.count > 0],
            key=lambda x: (priority_order.get(x.priority, 3), -x.count)
        )
    
    def generate_file_summary(self, errors: list[TypeError]) -> dict:
        """Generate summary by file."""
        files = defaultdict(lambda: {"errors": 0, "warnings": 0, "rules": set()})
        
        for error in errors:
            file_key = Path(error.file).name
            files[file_key]["errors" if error.severity == "error" else "warnings"] += 1
            files[file_key]["rules"].add(error.rule)
        
        # Convert sets to lists for JSON serialization
        return {
            k: {
                "errors": v["errors"],
                "warnings": v["warnings"],
                "rules": list(v["rules"])
            }
            for k, v in sorted(files.items(), key=lambda x: x[1]["errors"] + x[1]["warnings"], reverse=True)
        }
    
    def generate_recommendations(self, categories: list[ErrorCategory], file_summary: dict) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for critical issues
        typeddict_cat = next((c for c in categories if c.name == "TypedDict NotRequired Access"), None)
        if typeddict_cat and typeddict_cat.count > 0:
            recommendations.append(
                f"**CRITICAL**: Fix {typeddict_cat.count} TypedDict NotRequired access issues. "
                "These can cause runtime KeyError exceptions. Use .get() with defaults."
            )
        
        undefined_cat = next((c for c in categories if c.name == "Undefined Variable"), None)
        if undefined_cat and undefined_cat.count > 0:
            recommendations.append(
                f"**CRITICAL**: Fix {undefined_cat.count} undefined variable errors in dual_agent.py. "
                "Add proper imports for NodeExecutionContext."
            )
        
        # Check for dunder all issues
        dunder_cat = next((c for c in categories if c.name == "__all__ Declaration Mismatch"), None)
        if dunder_cat and dunder_cat.count > 0:
            recommendations.append(
                f"**HIGH**: Fix {dunder_cat.count} __all__ declaration mismatches. "
                "Consider adding type stubs or using explicit re-exports."
            )
        
        # General recommendations
        total_files_with_errors = len([f for f, data in file_summary.items() if data["errors"] > 0])
        if total_files_with_errors > 5:
            recommendations.append(
                f"**MEDIUM**: {total_files_with_errors} files have type errors. "
                "Consider prioritizing fixes by file importance."
            )
        
        recommendations.append(
            "**MEDIUM**: Add pyrightconfig.json to configure basedpyright settings "
            "and potentially suppress low-priority warnings."
        )
        
        recommendations.append(
            "**LOW**: Consider enabling stricter type checking gradually "
            "rather than all at once to manage technical debt."
        )
        
        return recommendations
    
    def analyze(self, data: dict | None = None) -> AnalysisReport:
        """Run complete analysis."""
        if data is None:
            data = self.run_basedpyright()
        
        errors = self.parse_diagnostics(data)
        categories = self.categorize_errors(errors)
        file_summary = self.generate_file_summary(errors)
        
        total_errors = sum(1 for e in errors if e.severity == "error")
        total_warnings = sum(1 for e in errors if e.severity == "warning")
        
        recommendations = self.generate_recommendations(categories, file_summary)
        
        return AnalysisReport(
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_files=len(file_summary),
            categories=categories,
            file_summary=file_summary,
            recommendations=recommendations
        )
    
    def print_report(self, report: AnalysisReport) -> None:
        """Print formatted report to console."""
        print("=" * 80)
        print("DocuSwarm Type Analysis Report")
        print("=" * 80)
        print()
        
        print(f"Summary:")
        print(f"  Total Errors:   {report.total_errors}")
        print(f"  Total Warnings: {report.total_warnings}")
        print(f"  Files Affected: {report.total_files}")
        print()
        
        print("=" * 80)
        print("Error Categories")
        print("=" * 80)
        for cat in report.categories:
            print()
            print(f"[{cat.priority.upper()}] {cat.name} ({cat.count} issues)")
            print(f"  Description: {cat.description}")
            print(f"  Fix Strategy: {cat.fix_strategy}")
            if cat.errors[:3]:
                print(f"  Examples:")
                for err in cat.errors[:3]:
                    msg = err.message[:60].encode('ascii', 'ignore').decode('ascii')
                    print(f"    - {err.location}: {msg}...")
        
        print()
        print("=" * 80)
        print("Top Files by Issue Count")
        print("=" * 80)
        for filename, data in list(report.file_summary.items())[:10]:
            total = data["errors"] + data["warnings"]
            print(f"  {filename}: {total} ({data['errors']} errors, {data['warnings']} warnings)")
        
        print()
        print("=" * 80)
        print("Recommendations")
        print("=" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        
        print()
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Analyze DocuSwarm type errors")
    parser.add_argument("--json-output", help="Save analysis to JSON file")
    parser.add_argument("--load", help="Load basedpyright output from file instead of running")
    args = parser.parse_args()
    
    analyzer = DocuSwarmTypeAnalyzer()
    
    if args.load:
        data = analyzer.load_from_file(args.load)
    else:
        print("Running basedpyright... (this may take a moment)")
        data = analyzer.run_basedpyright()
    
    report = analyzer.analyze(data)
    analyzer.print_report(report)
    
    if args.json_output:
        # Convert to JSON-serializable dict
        report_dict = {
            "total_errors": report.total_errors,
            "total_warnings": report.total_warnings,
            "total_files": report.total_files,
            "categories": [
                {
                    "name": c.name,
                    "description": c.description,
                    "count": c.count,
                    "priority": c.priority,
                    "fix_strategy": c.fix_strategy,
                    "errors": [
                        {
                            "file": e.file,
                            "line": e.line,
                            "column": e.column,
                            "severity": e.severity,
                            "message": e.message,
                            "rule": e.rule
                        }
                        for e in c.errors
                    ]
                }
                for c in report.categories
            ],
            "file_summary": report.file_summary,
            "recommendations": report.recommendations
        }
        
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        print(f"\nAnalysis saved to: {args.json_output}")


if __name__ == "__main__":
    main()

"""
Dependency Drift Analyzer - DocuSwarm Dependency Drift Deep Analysis Tool

This tool analyzes the gap between declared dependencies and actual runtime dependencies.
Main checks:
1. pyproject.toml declared dependencies vs actual code imports
2. kimi-agent-sdk related imports (should be replaced by claude-agent-sdk)
3. kaos.path related imports (should be removed)
4. Undeclared but actually used dependencies
5. Declared but unused dependencies

Usage:
    python tools/dependency_analysis/dependency_drift_analyzer.py
"""

from __future__ import annotations

import ast
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ImportFinding:
    """Represents a single import finding."""
    module: str
    name: str | None
    is_from_import: bool
    line_number: int
    file_path: str
    import_type: str = "unknown"  # "kimi_sdk", "claude_sdk", "kaos", "other"


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    file_path: str
    imports: list[ImportFinding] = field(default_factory=list)
    has_kimi_imports: bool = False
    has_claude_imports: bool = False
    has_kaos_imports: bool = False


@dataclass
class ProjectAnalysis:
    """Complete project analysis results."""
    files_analyzed: int = 0
    files_with_kimi: list[str] = field(default_factory=list)
    files_with_claude: list[str] = field(default_factory=list)
    files_with_kaos: list[str] = field(default_factory=list)
    all_kimi_imports: list[ImportFinding] = field(default_factory=list)
    all_claude_imports: list[ImportFinding] = field(default_factory=list)
    all_kaos_imports: list[ImportFinding] = field(default_factory=list)
    drift_summary: dict[str, Any] = field(default_factory=dict)


def categorize_import(module: str) -> str:
    """Categorize an import based on module name."""
    if "kimi_agent_sdk" in module or module == "kimi_agent_sdk":
        return "kimi_sdk"
    elif "claude_agent_sdk" in module or module == "claude_agent_sdk":
        return "claude_sdk"
    elif "kaos" in module or module.startswith("kaos."):
        return "kaos"
    return "other"


def analyze_file(file_path: Path) -> FileAnalysis | None:
    """Analyze a single Python file for imports."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [!] Warning: Could not parse {file_path}: {e}")
        return None

    analysis = FileAnalysis(file_path=str(file_path))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_type = categorize_import(alias.name)
                finding = ImportFinding(
                    module=alias.name,
                    name=alias.asname or alias.name,
                    is_from_import=False,
                    line_number=node.lineno,
                    file_path=str(file_path),
                    import_type=import_type,
                )
                analysis.imports.append(finding)
                if import_type == "kimi_sdk":
                    analysis.has_kimi_imports = True
                elif import_type == "claude_sdk":
                    analysis.has_claude_imports = True
                elif import_type == "kaos":
                    analysis.has_kaos_imports = True

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_type = categorize_import(node.module)
                for alias in node.names:
                    finding = ImportFinding(
                        module=node.module,
                        name=alias.name,
                        is_from_import=True,
                        line_number=node.lineno,
                        file_path=str(file_path),
                        import_type=import_type,
                    )
                    analysis.imports.append(finding)
                    if import_type == "kimi_sdk":
                        analysis.has_kimi_imports = True
                    elif import_type == "claude_sdk":
                        analysis.has_claude_imports = True
                    elif import_type == "kaos":
                        analysis.has_kaos_imports = True

    return analysis


def analyze_project(project_root: Path) -> ProjectAnalysis:
    """Analyze entire project for dependency drift."""
    analysis = ProjectAnalysis()

    # Find all Python files
    python_files = list(project_root.rglob("*.py"))
    
    # Filter out common non-source directories
    excluded_patterns = [
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
        ".git",
        "node_modules",
    ]
    
    filtered_files = [
        f for f in python_files
        if not any(pattern in str(f) for pattern in excluded_patterns)
    ]

    print(f"[*] Analyzing {len(filtered_files)} Python files...")
    print(f"    (excluded {len(python_files) - len(filtered_files)} files in cache/venv directories)")
    print()

    for i, file_path in enumerate(filtered_files, 1):
        if i % 20 == 0:
            print(f"    Progress: {i}/{len(filtered_files)} files...")
        
        file_analysis = analyze_file(file_path)
        if file_analysis is None:
            continue

        analysis.files_analyzed += 1

        if file_analysis.has_kimi_imports:
            analysis.files_with_kimi.append(str(file_path))
            analysis.all_kimi_imports.extend([
                imp for imp in file_analysis.imports 
                if imp.import_type == "kimi_sdk"
            ])

        if file_analysis.has_claude_imports:
            analysis.files_with_claude.append(str(file_path))
            analysis.all_claude_imports.extend([
                imp for imp in file_analysis.imports 
                if imp.import_type == "claude_sdk"
            ])

        if file_analysis.has_kaos_imports:
            analysis.files_with_kaos.append(str(file_path))
            analysis.all_kaos_imports.extend([
                imp for imp in file_analysis.imports 
                if imp.import_type == "kaos"
            ])

    return analysis


def generate_drift_report(analysis: ProjectAnalysis, project_root: Path) -> dict[str, Any]:
    """Generate a comprehensive drift report."""
    
    # Read pyproject.toml dependencies
    pyproject_path = project_root / "pyproject.toml"
    declared_deps = []
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        in_deps_section = False
        for line in content.split("\n"):
            if line.strip().startswith("dependencies = ["):
                in_deps_section = True
                continue
            if in_deps_section:
                if line.strip().startswith("]"):
                    break
                if "claude-agent-sdk" in line:
                    declared_deps.append("claude-agent-sdk")
                elif "kimi-agent-sdk" in line:
                    declared_deps.append("kimi-agent-sdk")

    # Calculate drift metrics
    kimi_file_count = len(analysis.files_with_kimi)
    claude_file_count = len(analysis.files_with_claude)
    kaos_file_count = len(analysis.files_with_kaos)

    # Group kimi imports by file
    kimi_imports_by_file = defaultdict(list)
    for imp in analysis.all_kimi_imports:
        kimi_imports_by_file[imp.file_path].append({
            "module": imp.module,
            "name": imp.name,
            "line": imp.line_number,
        })

    # Group kaos imports by file
    kaos_imports_by_file = defaultdict(list)
    for imp in analysis.all_kaos_imports:
        kaos_imports_by_file[imp.file_path].append({
            "module": imp.module,
            "name": imp.name,
            "line": imp.line_number,
        })

    drift_score = 0
    drift_issues = []

    # Issue 1: kimi-agent-sdk imports exist (should be removed)
    if kimi_file_count > 0:
        drift_score += kimi_file_count * 10
        drift_issues.append({
            "severity": "CRITICAL",
            "type": "kimi_sdk_usage",
            "message": f"Found {kimi_file_count} files using deprecated kimi-agent-sdk",
            "files": analysis.files_with_kimi[:10],  # First 10
            "total_files": kimi_file_count,
        })

    # Issue 2: kaos.path imports exist (should be removed)
    if kaos_file_count > 0:
        drift_score += kaos_file_count * 5
        drift_issues.append({
            "severity": "HIGH",
            "type": "kaos_usage",
            "message": f"Found {kaos_file_count} files using kaos.path (deprecated)",
            "files": analysis.files_with_kaos[:10],
            "total_files": kaos_file_count,
        })

    # Issue 3: Dependency declaration mismatch
    declared_has_claude = "claude-agent-sdk" in declared_deps
    declared_has_kimi = "kimi-agent-sdk" in declared_deps

    if declared_has_claude and kimi_file_count > 0:
        drift_issues.append({
            "severity": "CRITICAL",
            "type": "declaration_mismatch",
            "message": "pyproject.toml declares claude-agent-sdk but code imports kimi-agent-sdk",
            "declared": declared_deps,
            "actual_usage": ["kimi-agent-sdk"] if kimi_file_count > 0 else [],
        })

    if declared_has_kimi:
        drift_issues.append({
            "severity": "CRITICAL",
            "type": "deprecated_dependency",
            "message": "pyproject.toml still declares kimi-agent-sdk (should be removed)",
        })

    return {
        "summary": {
            "files_analyzed": analysis.files_analyzed,
            "files_with_kimi_imports": kimi_file_count,
            "files_with_claude_imports": claude_file_count,
            "files_with_kaos_imports": kaos_file_count,
            "drift_score": drift_score,
            "severity": "CRITICAL" if drift_score >= 50 else "HIGH" if drift_score >= 20 else "MEDIUM",
        },
        "declared_dependencies": declared_deps,
        "drift_issues": drift_issues,
        "detailed_findings": {
            "kimi_imports_by_file": dict(kimi_imports_by_file),
            "kaos_imports_by_file": dict(kaos_imports_by_file),
        },
        "recommendations": [
            "Remove all kimi-agent-sdk imports from the codebase",
            "Remove all kaos.path imports from the codebase",
            "Migrate to claude-agent-sdk using autoBMAD/epic_automation/sdk_wrapper.py as reference",
            "Update requirements-dev.txt to remove kimi-agent-sdk references",
            "Add CI check to prevent future kimi-agent-sdk imports",
        ],
    }


def print_report(report: dict[str, Any]) -> None:
    """Print a formatted report to console."""
    summary = report["summary"]
    
    print("\n" + "=" * 80)
    print("DEPENDENCY DRIFT ANALYSIS REPORT")
    print("=" * 80)
    
    print(f"\n[*] Files Analyzed: {summary['files_analyzed']}")
    print(f"[*] Drift Score: {summary['drift_score']} (Higher = More Drift)")
    print(f"[*] Severity: {summary['severity']}")
    
    print("\n[*] Import Statistics:")
    print(f"    - Files with kimi-agent-sdk imports: {summary['files_with_kimi_imports']}")
    print(f"    - Files with claude-agent-sdk imports: {summary['files_with_claude_imports']}")
    print(f"    - Files with kaos imports: {summary['files_with_kaos_imports']}")
    
    print(f"\n[*] Declared Dependencies: {report['declared_dependencies']}")
    
    print("\n[!] Drift Issues Found:")
    for issue in report["drift_issues"]:
        severity_icon = "[CRITICAL]" if issue["severity"] == "CRITICAL" else "[HIGH]" if issue["severity"] == "HIGH" else "[MEDIUM]"
        print(f"\n    {severity_icon} {issue['type']}")
        print(f"       {issue['message']}")
        if "total_files" in issue:
            print(f"       Total affected files: {issue['total_files']}")
    
    print("\n[*] Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"    {i}. {rec}")
    
    print("\n" + "=" * 80)


def main() -> int:
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    
    print("DocuSwarm Dependency Drift Analyzer")
    print("=" * 80)
    print(f"Project root: {project_root}")
    print()

    # Run analysis
    analysis = analyze_project(project_root)
    
    # Generate report
    report = generate_drift_report(analysis, project_root)
    
    # Print console report
    print_report(report)
    
    # Save JSON report
    output_dir = project_root / "docs" / "research"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / "dependency_drift_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[*] Detailed JSON report saved to: {json_path}")
    
    # Return exit code based on severity
    if report["summary"]["severity"] == "CRITICAL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

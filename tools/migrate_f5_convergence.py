#!/usr/bin/env python3
"""F5 Convergence Migration Helper Script.

This script helps automate parts of the F5 migration by:
1. Detecting code patterns that need migration
2. Generating patch suggestions
3. Verifying migration completion

Usage:
    python tools/migrate_f5_convergence.py --check
    python tools/migrate_f5_convergence.py --generate-patch
    python tools/migrate_f5_convergence.py --verify
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class MigrationIssue:
    """Represents a migration issue found in the codebase."""
    file: Path
    line_number: int
    original_code: str
    issue_type: str
    severity: str  # "error", "warning", "info"
    suggestion: str
    auto_fixable: bool = False


@dataclass
class MigrationReport:
    """Complete migration report."""
    issues: list[MigrationIssue] = field(default_factory=list)
    files_checked: int = 0
    
    @property
    def errors(self) -> list[MigrationIssue]:
        return [i for i in self.issues if i.severity == "error"]
    
    @property
    def warnings(self) -> list[MigrationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
    
    @property
    def auto_fixable_issues(self) -> list[MigrationIssue]:
        return [i for i in self.issues if i.auto_fixable]


def check_create_pipeline_graph_signature(file_path: Path) -> list[MigrationIssue]:
    """Check if create_pipeline_graph has the correct signature."""
    issues = []
    
    if file_path.name != "graph.py":
        return issues
    
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Check for old signature with Optional session_manager
            if "session_manager: Any | None = None" in line:
                issues.append(MigrationIssue(
                    file=file_path,
                    line_number=i,
                    original_code=line.strip(),
                    issue_type="deprecated_signature",
                    severity="error",
                    suggestion="Change to: session_manager: KimiSessionManager",
                    auto_fixable=False
                ))
            
            # Check for old fallback logic
            if "use_integrated = session_manager is not None" in line:
                issues.append(MigrationIssue(
                    file=file_path,
                    line_number=i,
                    original_code=line.strip(),
                    issue_type="conditional_executor_selection",
                    severity="error",
                    suggestion="Remove conditional, always use integrated executor",
                    auto_fixable=False
                ))
            
            # Check for default executor fallback message
            if "falling_back_to_default_executor" in line:
                issues.append(MigrationIssue(
                    file=file_path,
                    line_number=i,
                    original_code=line.strip(),
                    issue_type="fallback_warning",
                    severity="error",
                    suggestion="Remove fallback, raise ValueError instead",
                    auto_fixable=False
                ))
    except Exception as e:
        issues.append(MigrationIssue(
            file=file_path,
            line_number=0,
            original_code="",
            issue_type="file_error",
            severity="warning",
            suggestion=f"Could not read file: {e}",
        ))
    
    return issues


def check_default_executor(file_path: Path) -> list[MigrationIssue]:
    """Check for deprecated _create_default_node_executor."""
    issues = []
    
    if file_path.name != "graph.py":
        return issues
    
    try:
        content = file_path.read_text(encoding="utf-8")
        
        if "def _create_default_node_executor(" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "def _create_default_node_executor(" in line:
                    issues.append(MigrationIssue(
                        file=file_path,
                        line_number=i,
                        original_code=line.strip(),
                        issue_type="deprecated_function",
                        severity="error",
                        suggestion="Delete _create_default_node_executor function",
                        auto_fixable=False
                    ))
                    break
        
        if "def create_enhanced_node_executor(" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "def create_enhanced_node_executor(" in line:
                    issues.append(MigrationIssue(
                        file=file_path,
                        line_number=i,
                        original_code=line.strip(),
                        issue_type="deprecated_function",
                        severity="error",
                        suggestion="Delete create_enhanced_node_executor function",
                        auto_fixable=False
                    ))
                    break
    except Exception:
        pass
    
    return issues


def check_synthetic_id_creation(file_path: Path) -> list[MigrationIssue]:
    """Check for direct synthetic pipeline_id creation."""
    issues = []
    
    # Skip the adapter itself
    if file_path.name == "pipeline_adapter.py":
        return issues
    
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        # Pattern for f"node-{...}" or f'node-{...}'
        patterns = [
            (r'f["\']node-\{', "f-string node- prefix"),
            (r'f["\']node-run-\{', "f-string node-run- prefix"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in patterns:
                if re.search(pattern, line) and "PipelineAdapter" not in line:
                    # Check if file imports PipelineAdapter
                    has_adapter_import = "PipelineAdapter" in content[:1000]
                    
                    issues.append(MigrationIssue(
                        file=file_path,
                        line_number=i,
                        original_code=line.strip(),
                        issue_type="direct_synthetic_id",
                        severity="error",
                        suggestion=f"Use PipelineAdapter.create_pipeline_id() instead of {desc}",
                        auto_fixable=False
                    ))
                    break
    except Exception:
        pass
    
    return issues


def check_adapter_usage(file_path: Path) -> list[MigrationIssue]:
    """Check if PipelineAdapter is properly used."""
    issues = []
    
    if file_path.name == "pipeline_adapter.py":
        return issues
    
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # Check if file has synthetic ID patterns but no PipelineAdapter
        has_synthetic_patterns = (
            'f"node-' in content or "f'node-" in content
        )
        has_adapter_import = "PipelineAdapter" in content
        
        if has_synthetic_patterns and not has_adapter_import:
            issues.append(MigrationIssue(
                file=file_path,
                line_number=1,
                original_code="",
                issue_type="missing_adapter_import",
                severity="error",
                suggestion="Add: from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter",
                auto_fixable=True
            ))
    except Exception:
        pass
    
    return issues


def run_full_check() -> MigrationReport:
    """Run all migration checks."""
    report = MigrationReport()
    
    # Define files to check
    pipeline_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline"
    ne_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution"
    
    files_to_check = []
    
    if pipeline_path.exists():
        files_to_check.extend(pipeline_path.glob("*.py"))
    
    if ne_path.exists():
        files_to_check.extend(ne_path.glob("*.py"))
    
    # Run checks
    for file_path in files_to_check:
        if "__pycache__" in str(file_path):
            continue
        
        report.files_checked += 1
        
        # Run all checkers
        report.issues.extend(check_create_pipeline_graph_signature(file_path))
        report.issues.extend(check_default_executor(file_path))
        report.issues.extend(check_synthetic_id_creation(file_path))
        report.issues.extend(check_adapter_usage(file_path))
    
    return report


def generate_patch(issue: MigrationIssue) -> str | None:
    """Generate a patch for an auto-fixable issue."""
    if not issue.auto_fixable:
        return None
    
    if issue.issue_type == "missing_adapter_import":
        return f"""--- a/{issue.file.relative_to(PROJECT_ROOT)}
+++ b/{issue.file.relative_to(PROJECT_ROOT)}
@@ -1,5 +1,7 @@
 # ... existing imports ...
 
+from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
+
 # ... rest of file ...
"""
    
    return None


def print_report(report: MigrationReport) -> None:
    """Print migration report."""
    print("=" * 80)
    print("F5 Convergence Migration Report")
    print("=" * 80)
    print()
    print(f"Files checked: {report.files_checked}")
    print(f"Total issues: {len(report.issues)}")
    print(f"  - Errors: {len(report.errors)}")
    print(f"  - Warnings: {len(report.warnings)}")
    print(f"  - Auto-fixable: {len(report.auto_fixable_issues)}")
    print()
    
    if report.errors:
        print("## Errors (Must Fix)")
        print("-" * 80)
        for issue in report.errors:
            print(f"\n[{issue.issue_type}] {issue.file.name}:{issue.line_number}")
            if issue.original_code:
                print(f"  Code: {issue.original_code[:80]}")
            print(f"  Fix: {issue.suggestion}")
        print()
    
    if report.warnings:
        print("## Warnings (Should Review)")
        print("-" * 80)
        for issue in report.warnings:
            print(f"\n[{issue.issue_type}] {issue.file.name}:{issue.line_number}")
            print(f"  {issue.suggestion}")
        print()
    
    if not report.issues:
        print("✅ No migration issues found! F5 convergence is complete.")


def print_patches(report: MigrationReport) -> None:
    """Print patches for auto-fixable issues."""
    print("=" * 80)
    print("Suggested Patches")
    print("=" * 80)
    print()
    
    for issue in report.auto_fixable_issues:
        patch = generate_patch(issue)
        if patch:
            print(patch)
            print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="F5 Convergence Migration Helper"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run migration checks and print report"
    )
    parser.add_argument(
        "--generate-patch",
        action="store_true",
        help="Generate patches for auto-fixable issues"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration is complete (returns 0 if complete)"
    )
    
    args = parser.parse_args()
    
    if not any([args.check, args.generate_patch, args.verify]):
        args.check = True  # Default action
    
    report = run_full_check()
    
    exit_code = 0
    
    if args.check:
        print_report(report)
        if report.errors:
            exit_code = 1
    
    if args.generate_patch:
        print_patches(report)
    
    if args.verify:
        if report.errors:
            print(f"❌ Migration incomplete: {len(report.errors)} errors remaining")
            exit_code = 1
        else:
            print("✅ Migration complete!")
            exit_code = 0
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

"""
Migration Tracker - 依赖统一迁移进度跟踪工具

跟踪从 kimi-agent-sdk 到 claude-agent-sdk 的迁移进度

Usage:
    python tools/dependency_analysis/migration_tracker.py
    python tools/dependency_analysis/migration_tracker.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MigrationStatus:
    """Migration status for a single file."""
    file_path: str
    kimi_imports: list[dict[str, Any]] = field(default_factory=list)
    kaos_imports: list[dict[str, Any]] = field(default_factory=list)
    is_migrated: bool = False
    notes: str = ""


@dataclass
class MigrationProgress:
    """Overall migration progress."""
    total_files: int = 0
    migrated_files: int = 0
    pending_files: int = 0
    progress_percentage: float = 0.0
    file_statuses: list[MigrationStatus] = field(default_factory=list)
    critical_files: list[str] = field(default_factory=list)


# Files that need to be migrated (based on analysis)
TARGET_FILES = [
    "autoBMAD/docuswarm/agents/evaluator.py",
    "autoBMAD/docuswarm/agents/independent.py",
    "autoBMAD/docuswarm/llm/approval.py",
    "autoBMAD/docuswarm/llm/session_manager.py",
    "autoBMAD/docuswarm/pipeline/orchestrator.py",
    "autoBMAD/docuswarm/tools/callable_tool_wrapper.py",
    "autoBMAD/docuswarm/tools/sdk_adapter.py",
]

# Configuration files
CONFIG_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
]


def load_analysis_report(project_root: Path) -> dict[str, Any] | None:
    """Load the dependency drift analysis report."""
    report_path = project_root / "docs" / "research" / "dependency_drift_analysis.json"
    if not report_path.exists():
        return None
    
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_file_migration_status(
    file_path: str,
    kimi_imports: dict[str, list],
    kaos_imports: dict[str, list]
) -> MigrationStatus:
    """Check migration status for a single file."""
    status = MigrationStatus(file_path=file_path)
    
    # Check kimi imports
    if file_path in kimi_imports:
        status.kimi_imports = kimi_imports[file_path]
    
    # Check kaos imports
    if file_path in kaos_imports:
        status.kaos_imports = kaos_imports[file_path]
    
    # Determine if migrated
    status.is_migrated = len(status.kimi_imports) == 0 and len(status.kaos_imports) == 0
    
    # Add notes
    if status.is_migrated:
        status.notes = "Migrated"
    else:
        issues = []
        if status.kimi_imports:
            imports = [imp["name"] for imp in status.kimi_imports]
            issues.append(f"kimi: {', '.join(imports[:3])}")
        if status.kaos_imports:
            issues.append(f"kaos: {status.kaos_imports[0]['name']}")
        status.notes = "; ".join(issues)
    
    return status


def calculate_progress(file_statuses: list[MigrationStatus]) -> MigrationProgress:
    """Calculate overall migration progress."""
    total = len(file_statuses)
    migrated = sum(1 for s in file_statuses if s.is_migrated)
    pending = total - migrated
    percentage = (migrated / total * 100) if total > 0 else 0
    
    critical = [
        s.file_path for s in file_statuses
        if not s.is_migrated and "session_manager" in s.file_path
    ]
    
    return MigrationProgress(
        total_files=total,
        migrated_files=migrated,
        pending_files=pending,
        progress_percentage=percentage,
        file_statuses=file_statuses,
        critical_files=critical,
    )


def print_progress_report(progress: MigrationProgress) -> None:
    """Print a formatted progress report."""
    print("\n" + "=" * 80)
    print("MIGRATION PROGRESS REPORT")
    print("=" * 80)
    
    print(f"\n[*] Overall Progress: {progress.progress_percentage:.1f}%")
    print(f"    - Total files: {progress.total_files}")
    print(f"    - Migrated: {progress.migrated_files}")
    print(f"    - Pending: {progress.pending_files}")
    
    # Progress bar
    bar_width = 50
    filled = int(bar_width * progress.progress_percentage / 100)
    bar = "[" + "=" * filled + "-" * (bar_width - filled) + "]"
    print(f"    {bar}")
    
    print("\n[*] File Status:")
    for status in progress.file_statuses:
        icon = "[OK]" if status.is_migrated else "[PENDING]"
        file_name = Path(status.file_path).name
        print(f"    {icon} {file_name:40s} {status.notes}")
    
    if progress.critical_files:
        print("\n[!] Critical Files (blockers):")
        for f in progress.critical_files:
            print(f"    - {f}")
    
    print("\n" + "=" * 80)


def check_config_files(project_root: Path) -> list[dict[str, Any]]:
    """Check configuration files for consistency."""
    results = []
    
    # Check pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        has_claude = "claude-agent-sdk" in content
        has_kimi = "kimi-agent-sdk" in content
        results.append({
            "file": "pyproject.toml",
            "has_claude": has_claude,
            "has_kimi": has_kimi,
            "status": "OK" if (has_claude and not has_kimi) else "NEEDS_FIX",
        })
    
    # Check requirements.txt
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        has_claude = "claude-agent-sdk" in content
        has_kimi = "kimi-agent-sdk" in content
        results.append({
            "file": "requirements.txt",
            "has_claude": has_claude,
            "has_kimi": has_kimi,
            "status": "OK" if (has_claude and not has_kimi) else "NEEDS_FIX",
        })
    
    # Check requirements-dev.txt
    req_dev_path = project_root / "requirements-dev.txt"
    if req_dev_path.exists():
        content = req_dev_path.read_text(encoding="utf-8")
        has_claude = "claude-agent-sdk" in content
        has_kimi_decl = "kimi-agent-sdk" in content.lower()
        results.append({
            "file": "requirements-dev.txt",
            "has_claude": has_claude,
            "has_kimi": has_kimi_decl,
            "status": "OK" if (has_claude and not has_kimi_decl) else "NEEDS_FIX",
        })
    
    return results


def print_config_report(results: list[dict[str, Any]]) -> None:
    """Print configuration file report."""
    print("\n[*] Configuration Files:")
    for result in results:
        icon = "[OK]" if result["status"] == "OK" else "[NEEDS_FIX]"
        kimi_status = "has kimi" if result["has_kimi"] else "no kimi"
        claude_status = "has claude" if result["has_claude"] else "no claude"
        print(f"    {icon} {result['file']:25s} ({claude_status}, {kimi_status})")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migration Progress Tracker")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with error code if migration is not complete",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent.parent
    
    # Load analysis report
    report = load_analysis_report(project_root)
    if report is None:
        print("ERROR: Dependency drift analysis report not found.")
        print("Run: python tools/dependency_analysis/dependency_drift_analyzer.py")
        return 1
    
    # Get findings
    kimi_imports = report.get("detailed_findings", {}).get("kimi_imports_by_file", {})
    kaos_imports = report.get("detailed_findings", {}).get("kaos_imports_by_file", {})
    
    # Check each target file
    file_statuses = []
    for file_path in TARGET_FILES:
        full_path = str(project_root / file_path)
        status = check_file_migration_status(full_path, kimi_imports, kaos_imports)
        file_statuses.append(status)
    
    # Calculate progress
    progress = calculate_progress(file_statuses)
    
    # Check config files
    config_results = check_config_files(project_root)
    
    if args.json:
        # Output JSON
        output = {
            "progress": asdict(progress),
            "config_files": config_results,
        }
        print(json.dumps(output, indent=2))
    else:
        # Print report
        print_progress_report(progress)
        print_config_report(config_results)
        
        # Summary
        print("\n[*] Summary:")
        if progress.progress_percentage == 100:
            print("    Migration COMPLETE!")
        elif progress.progress_percentage >= 50:
            print(f"    Migration IN PROGRESS ({progress.progress_percentage:.1f}%)")
        else:
            print(f"    Migration JUST STARTED ({progress.progress_percentage:.1f}%)")
        
        config_ok = all(r["status"] == "OK" for r in config_results)
        if config_ok:
            print("    Configuration files: OK")
        else:
            print("    Configuration files: NEEDS_FIX")
    
    # Exit code for CI
    if args.check:
        if progress.progress_percentage < 100:
            return 1
        config_ok = all(r["status"] == "OK" for r in config_results)
        if not config_ok:
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
P0 Database Singleton Debugger - F2/F4 Critical Issue Research Tool

研究问题：DatabaseManager 单例按路径污染，第一次 db_path 会污染后续 StateManager

目标：
1. 验证 DatabaseManager.get_instance() 第一次调用后，后续不同 db_path 是否仍返回第一次的实例
2. 验证 StateManager() 默认实例化是否会使用错误的 db_path
3. 验证这种污染对 shared_context 和 pipeline 状态的影响
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent.resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from autoBMAD.docuswarm.storage.database import DatabaseManager


def test_singleton_path_pollution() -> dict[str, Any]:
    """Test: DatabaseManager singleton ignores subsequent db_path changes."""
    print("\n" + "=" * 70)
    print("TEST: DatabaseManager Singleton Path Pollution")
    print("=" * 70)

    findings = {
        "test": "singleton_path_pollution",
        "issue": "DatabaseManager.get_instance() returns first-created instance regardless of requested db_path",
        "evidence": [],
        "severity": "CRITICAL",
    }

    # Reset singleton first
    DatabaseManager.reset_instance()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_one = Path(tmpdir) / "one.db"
        db_two = Path(tmpdir) / "two.db"

        # First call with db_one
        instance_one = DatabaseManager.get_instance(db_path=db_one)
        path_one = instance_one.db_path

        print(f"First get_instance(db_one='{db_one}')")
        print(f"  Returned instance.db_path = '{path_one}'")

        # Second call with db_two - should return different instance, but won't
        instance_two = DatabaseManager.get_instance(db_path=db_two)
        path_two = instance_two.db_path

        print(f"\nSecond get_instance(db_two='{db_two}')")
        print(f"  Returned instance.db_path = '{path_two}'")

        # Check if they are the same object
        same_object = instance_one is instance_two
        same_path = path_one == path_two

        print(f"\n  instance_one is instance_two: {same_object}")
        print(f"  path_one == path_two: {same_path}")

        if same_object and same_path:
            print(f"  \n  BUG CONFIRMED: Second call returned SAME instance with FIRST db_path!")
            print(f"  This means ALL pipeline state writes go to '{path_one}' instead of '{db_two}'")

        findings["evidence"].append({
            "location": "autoBMAD/docuswarm/storage/database.py:64-78",
            "first_call_db_path": str(db_one),
            "first_instance_path": str(path_one),
            "second_call_db_path": str(db_two),
            "second_instance_path": str(path_two),
            "same_object": same_object,
            "same_path": same_path,
            "verdict": "BUG CONFIRMED" if (same_object and same_path) else "UNEXPECTED_BEHAVIOR",
        })

    # Reset for clean state
    DatabaseManager.reset_instance()
    return findings


def test_direct_instantiation_vs_singleton() -> dict[str, Any]:
    """Test: Direct DatabaseManager() instantiation vs get_instance()."""
    print("\n" + "=" * 70)
    print("TEST: Direct Instantiation vs Singleton")
    print("=" * 70)

    findings = {
        "test": "direct_instantiation_vs_singleton",
        "issue": "Direct DatabaseManager() creates separate instance but get_instance() still returns singleton",
        "evidence": [],
        "severity": "HIGH",
    }

    DatabaseManager.reset_instance()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_default = Path(tmpdir) / "default.db"
        db_direct = Path(tmpdir) / "direct.db"

        # Create singleton first
        singleton = DatabaseManager.get_instance(db_path=db_default)

        # Direct instantiation
        direct = DatabaseManager(db_path=db_direct)

        print(f"Singleton instance db_path: {singleton.db_path}")
        print(f"Direct instance db_path: {direct.db_path}")
        print(f"singleton is direct: {singleton is direct}")
        print(f"get_instance() returns singleton: {DatabaseManager.get_instance() is singleton}")

        findings["evidence"].append({
            "singleton_path": str(singleton.db_path),
            "direct_path": str(direct.db_path),
            "same_object": singleton is direct,
            "note": "Direct instantiation can create different instance, but get_instance() ignores it",
        })

    DatabaseManager.reset_instance()
    return findings


def test_state_manager_default_instantiation() -> dict[str, Any]:
    """Test: StateManager() default instantiation behavior."""
    print("\n" + "=" * 70)
    print("TEST: StateManager() Default Instantiation")
    print("=" * 70)

    findings = {
        "test": "state_manager_default_instantiation",
        "issue": "StateManager() called without db_path uses default 'docuswarm.db' via DatabaseManager.get_instance()",
        "evidence": [],
        "severity": "CRITICAL",
    }

    DatabaseManager.reset_instance()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_one = Path(tmpdir) / "one.db"
        db_two = Path(tmpdir) / "two.db"

        # Simulate: orchestrator creates StateManager with db_one
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        sm_one = StateManager(db_path=str(db_one))

        # Now simulate: update_context_sdk.py calls StateManager() without db_path
        # This will call DatabaseManager.get_instance() which returns the singleton
        # But what db_path does it use?
        print(f"StateManager(db_path='{db_one}') created")
        print(f"  Internal database path: {sm_one._db.db_path}")

        # Check if update_context_tool's StateManager() would use the same db
        # Look at the code
        sdk_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "tools" / "update_context_sdk.py"
        sdk_source = sdk_path.read_text(encoding="utf-8")

        # Find StateManager() call
        lines = sdk_source.split("\n")
        sm_lines = [l for l in lines if "StateManager()" in l or "StateManager(" in l]

        print(f"\nupdate_context_sdk.py StateManager usage:")
        for line in sm_lines:
            print(f"  {line.strip()}")

        findings["evidence"].append({
            "location": "autoBMAD/docuswarm/tools/update_context_sdk.py:99",
            "code": sm_lines,
            "finding": "update_context_sdk creates StateManager() WITHOUT db_path, so it uses DatabaseManager.get_instance() with default path",
            "orchestrator_db_path": str(db_one),
            "update_context_will_use": "docuswarm.db (default) or existing singleton path",
        })

        print(f"\nFinding: If orchestrator uses db_path='{db_one}', but update_context_tool")
        print(f"  calls StateManager() without db_path, it will NOT write to '{db_one}'.")
        print(f"  Instead it uses the singleton instance with potentially DIFFERENT path.")

    DatabaseManager.reset_instance()
    return findings


def analyze_code_for_singleton_issue() -> dict[str, Any]:
    """Analyze DatabaseManager source code for singleton design flaw."""
    print("\n" + "=" * 70)
    print("CODE ANALYSIS: DatabaseManager Singleton Design")
    print("=" * 70)

    db_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "storage" / "database.py"
    source = db_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Extract get_instance method
    in_method = False
    method_lines = []
    for i, line in enumerate(lines):
        if "def get_instance(cls" in line:
            in_method = True
        if in_method:
            method_lines.append(f"Line {i+1}: {line}")
            if line.strip() == "" and len(method_lines) > 5:
                # Check next line
                if i+1 < len(lines) and not lines[i+1].startswith(" ") and "def " in lines[i+1]:
                    break
            if len(method_lines) > 15:
                break

    print("DatabaseManager.get_instance() source:")
    for line in method_lines:
        print(f"  {line}")

    print("\nDesign flaw analysis:")
    print("  1. _instance is a class-level attribute (single value)")
    print("  2. get_instance() checks 'if cls._instance is None' ONCE")
    print("  3. First call with db_path='one.db' creates instance and stores it")
    print("  4. ALL subsequent calls return the SAME instance, ignoring db_path parameter")
    print("  5. There is NO per-path instance cache")

    findings = {
        "code": method_lines,
        "design_flaws": [
            "Single class-level _instance cannot hold multiple db_path instances",
            "db_path parameter in get_instance() is only used on first call",
            "No cache keyed by resolved_db_path",
            "No warning when requested db_path differs from stored instance's path",
        ],
    }

    return findings


def run_all_tests() -> dict[str, Any]:
    """Run all database singleton tests."""
    print("\n" + "=" * 70)
    print("P0 DATABASE SINGLETON DEBUGGER")
    print("Issue: F2/F4 - DatabaseManager singleton path pollution")
    print("=" * 70)

    results = {
        "issue_id": "F2/F4",
        "severity": "CRITICAL",
        "title": "DatabaseManager单例按路径污染，测试/多pipeline互相污染",
        "tests": [],
        "code_analysis": None,
    }

    results["tests"].append(test_singleton_path_pollution())
    results["tests"].append(test_direct_instantiation_vs_singleton())
    results["tests"].append(test_state_manager_default_instantiation())
    results["code_analysis"] = analyze_code_for_singleton_issue()

    return results


if __name__ == "__main__":
    results = run_all_tests()

    output_path = Path(__file__).parent / "p0_database_singleton_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")

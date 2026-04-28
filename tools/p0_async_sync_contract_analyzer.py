"""
P0-3 Async/Sync Contract Analyzer
=================================
Deep research tool for analyzing the "同步/异步契约不一致，存在运行时隐患" issue.

This tool uses AST analysis to:
1. Find `await` expressions that target synchronous methods
2. Find `asyncio.run()` and `loop.run_until_complete()` calls in async contexts
3. Identify "bridge" patterns like `_run_async` that force async into sync
4. Detect event-loop nesting risks
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
AUTO_BMAD = PROJECT_ROOT / "autoBMAD" / "docuswarm"


def find_python_files(root: Path) -> list[Path]:
    return list(root.rglob("*.py"))


def parse_file(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return None


def get_function_defs(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }


def is_async_function(node: ast.AST) -> bool:
    return isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and getattr(node, "async", False)


def find_await_expressions(tree: ast.AST) -> list[dict[str, Any]]:
    """Find all await expressions and their targets."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Await):
            target = node.value
            info = {"line": node.lineno, "target_type": type(target).__name__}
            if isinstance(target, ast.Call):
                func = target.func
                if isinstance(func, ast.Name):
                    info["func_name"] = func.id
                elif isinstance(func, ast.Attribute):
                    info["func_name"] = func.attr
                    # Try to resolve the receiver
                    if isinstance(func.value, ast.Name):
                        info["receiver"] = func.value.id
                    elif isinstance(func.value, ast.Attribute):
                        info["receiver"] = func.value.attr
                else:
                    info["func_name"] = "<complex>"
            elif isinstance(target, ast.Attribute):
                info["func_name"] = target.attr
            results.append(info)
    return results


def find_event_loop_calls(tree: ast.AST) -> list[dict[str, Any]]:
    """Find asyncio.run, loop.run_until_complete, and _run_async patterns."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr

            if name in ("run", "run_until_complete", "_run_async"):
                results.append({
                    "line": node.lineno,
                    "call": name,
                    "full": ast.dump(func),
                })
    return results


def analyze_state_manager_contract() -> dict[str, Any]:
    """Check if get_latest_successful_run is sync or async."""
    path = AUTO_BMAD / "storage" / "state_manager.py"
    tree = parse_file(path)
    if tree is None:
        return {"error": "parse failed"}

    funcs = get_function_defs(tree)
    target = funcs.get("get_latest_successful_run")
    if target is None:
        return {"found": False}

    return {
        "found": True,
        "is_async": isinstance(target, ast.AsyncFunctionDef),
        "line": target.lineno,
        "file": str(path.relative_to(PROJECT_ROOT)),
    }


def analyze_chaining_awaits() -> dict[str, Any]:
    """Analyze ContextChainer for await-on-sync violations."""
    path = AUTO_BMAD / "node_execution" / "chaining.py"
    tree = parse_file(path)
    if tree is None:
        return {"error": "parse failed"}

    awaits = find_await_expressions(tree)
    violations = []
    for a in awaits:
        if a.get("func_name") == "get_latest_successful_run":
            violations.append(a)

    return {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "total_awaits": len(awaits),
        "violations": violations,
    }


def analyze_pipeline_graph_async_bridges() -> dict[str, Any]:
    """Analyze pipeline/graph.py for event-loop mixing."""
    path = AUTO_BMAD / "pipeline" / "graph.py"
    tree = parse_file(path)
    if tree is None:
        return {"error": "parse failed"}

    el_calls = find_event_loop_calls(tree)

    # Find the _create_integrated_node_executor and its _run_async
    run_async_details = []
    for func in ast.walk(tree):
        if isinstance(func, ast.FunctionDef) and func.name == "_run_async":
            # Find asyncio.run and ThreadPoolExecutor usage inside
            for inner in ast.walk(func):
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Attribute) and inner.func.attr == "run":
                        run_async_details.append({"line": inner.lineno, "type": "asyncio.run"})
                    elif isinstance(inner.func, ast.Name) and inner.func.id == "run":
                        run_async_details.append({"line": inner.lineno, "type": "asyncio.run"})
                    elif isinstance(inner.func, ast.Attribute) and inner.func.attr == "result":
                        run_async_details.append({"line": inner.lineno, "type": "future.result"})

    # Find run_until_complete in create_pipeline_graph
    run_until_complete_lines = []
    for func in ast.walk(tree):
        if isinstance(func, ast.FunctionDef) and func.name == "create_pipeline_graph":
            for inner in ast.walk(func):
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Attribute) and inner.func.attr == "run_until_complete":
                        run_until_complete_lines.append(inner.lineno)

    return {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "event_loop_calls": el_calls,
        "_run_async_details": run_async_details,
        "run_until_complete_in_create_pipeline_graph": run_until_complete_lines,
    }


def analyze_flow_async_bridges() -> dict[str, Any]:
    """Analyze node_execution/flow.py for _run_async and await patterns."""
    path = AUTO_BMAD / "node_execution" / "flow.py"
    tree = parse_file(path)
    if tree is None:
        return {"error": "parse failed"}

    el_calls = find_event_loop_calls(tree)
    awaits = find_await_expressions(tree)

    # Check if _load_context_file_async is awaited inside sync load_context_file via _run_async
    return {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "event_loop_calls": el_calls,
        "total_awaits": len(awaits),
        "sample_awaits": awaits[:5],
    }


def find_all_async_def_sync_await_violations() -> list[dict[str, Any]]:
    """Scan all files for awaits on methods that are known to be sync."""
    # Known sync methods that should NOT be awaited
    known_sync_methods = {
        "get_latest_successful_run",
        "get_pipeline",
        "save_node_result",
        "create_pipeline",
        "update_pipeline_status",
    }
    violations = []
    for f in find_python_files(AUTO_BMAD):
        tree = parse_file(f)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute) and func.attr in known_sync_methods:
                    violations.append({
                        "file": str(f.relative_to(PROJECT_ROOT)),
                        "line": node.lineno,
                        "method": func.attr,
                    })
    return violations


def find_all_run_until_complete_in_async_contexts() -> list[dict[str, Any]]:
    """Find run_until_complete inside async functions (high risk)."""
    findings = []
    for f in find_python_files(AUTO_BMAD):
        tree = parse_file(f)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func = inner.func
                        if isinstance(func, ast.Attribute) and func.attr == "run_until_complete":
                            findings.append({
                                "file": str(f.relative_to(PROJECT_ROOT)),
                                "line": inner.lineno,
                                "inside_async_func": node.name,
                            })
    return findings


def main() -> int:
    report = {
        "title": "P0-3 同步/异步契约不一致深度分析报告",
        "findings": {
            "state_manager_contract": analyze_state_manager_contract(),
            "chaining_awaits": analyze_chaining_awaits(),
            "pipeline_graph_bridges": analyze_pipeline_graph_async_bridges(),
            "flow_bridges": analyze_flow_async_bridges(),
            "all_sync_await_violations": find_all_async_def_sync_await_violations(),
            "run_until_complete_in_async": find_all_run_until_complete_in_async_contexts(),
        },
    }

    output_path = PROJECT_ROOT / "docs" / "research" / "p0-3-async-sync-contract-analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("P0-3 同步/异步契约不一致 — 快速摘要")
    print("=" * 60)

    sm = report["findings"]["state_manager_contract"]
    print(f"\nStateManager.get_latest_successful_run:")
    print(f"  文件: {sm.get('file')}")
    print(f"  行号: {sm.get('line')}")
    print(f"  是否为 async def: {sm.get('is_async')}")

    chain = report["findings"]["chaining_awaits"]
    print(f"\nContextChainer 中的 await 违规:")
    print(f"  总 await 数: {chain['total_awaits']}")
    for v in chain["violations"]:
        print(f"  ! await {v.get('func_name')}() 于 {chain['file']}:{v['line']}")

    pg = report["findings"]["pipeline_graph_bridges"]
    print(f"\npipeline/graph.py 中的事件循环桥接:")
    for d in pg["_run_async_details"]:
        print(f"  - _run_async 内 {d['type']} 于 {pg['file']}:{d['line']}")
    for line in pg["run_until_complete_in_create_pipeline_graph"]:
        print(f"  ! run_until_complete 在 create_pipeline_graph 内 于 {pg['file']}:{line}")

    fb = report["findings"]["flow_bridges"]
    print(f"\nnode_execution/flow.py 中的事件循环桥接:")
    for c in fb["event_loop_calls"]:
        print(f"  - {c['call']} 于 {fb['file']}:{c['line']}")

    all_v = report["findings"]["all_sync_await_violations"]
    print(f"\n全局 await-on-sync 违规 ({len(all_v)} 处):")
    for v in all_v:
        print(f"  ! await {v['method']}() 于 {v['file']}:{v['line']}")

    rtc = report["findings"]["run_until_complete_in_async"]
    print(f"\nasync 函数内部的 run_until_complete ({len(rtc)} 处):")
    for r in rtc:
        print(f"  ! 于 {r['file']}:{r['line']} (在 {r['inside_async_func']} 内)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

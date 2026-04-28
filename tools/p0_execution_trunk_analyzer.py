"""
P0-2 Execution Trunk Divergence Analyzer
========================================
Deep research tool for analyzing the "执行主干分叉，存在历史路径残留" issue.

This tool:
1. Discovers all create_node_executor implementations
2. Maps the graph creation factory functions
3. Traces import/export paths
4. Identifies active vs. legacy/dead code paths
5. Generates a structured evidence report
"""

from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
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


def find_function_definitions(tree: ast.AST, name: str) -> list[ast.FunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]


def find_imports_of(tree: ast.AST, symbol: str) -> list[dict[str, Any]]:
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == symbol or alias.asname == symbol:
                    results.append({
                        "module": node.module,
                        "name": alias.name,
                        "asname": alias.asname,
                        "line": node.lineno,
                    })
    return results


def find_calls(tree: ast.AST, func_name: str) -> list[dict[str, Any]]:
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == func_name:
                results.append({"line": node.lineno, "type": "direct"})
            elif isinstance(node.func, ast.Attribute) and node.func.attr == func_name:
                attr_chain = []
                current = node.func
                while isinstance(current, ast.Attribute):
                    attr_chain.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    attr_chain.append(current.id)
                results.append({
                    "line": node.lineno,
                    "type": "attribute",
                    "chain": ".".join(reversed(attr_chain)),
                })
    return results


def analyze_create_node_executor() -> dict[str, Any]:
    files = find_python_files(AUTO_BMAD)
    implementations = []
    imports = []
    calls = []

    for f in files:
        tree = parse_file(f)
        if tree is None:
            continue
        rel = f.relative_to(PROJECT_ROOT)

        funcs = find_function_definitions(tree, "create_node_executor")
        for func in funcs:
            # Extract signature and docstring
            doc = ast.get_docstring(func) or ""
            args = [a.arg for a in func.args.args]
            implementations.append({
                "file": str(rel),
                "line": func.lineno,
                "args": args,
                "doc_summary": doc.split("\n")[0] if doc else "",
            })

        imps = find_imports_of(tree, "create_node_executor")
        for imp in imps:
            imports.append({"file": str(rel), **imp})

        cs = find_calls(tree, "create_node_executor")
        for c in cs:
            calls.append({"file": str(rel), **c})

    return {
        "implementations": implementations,
        "imports": imports,
        "calls": calls,
    }


def analyze_graph_factories() -> dict[str, Any]:
    targets = ["create_pipeline_graph", "create_node_execution_graph"]
    files = find_python_files(AUTO_BMAD)
    result = {t: {"implementations": [], "calls": []} for t in targets}

    for f in files:
        tree = parse_file(f)
        if tree is None:
            continue
        rel = f.relative_to(PROJECT_ROOT)

        for target in targets:
            funcs = find_function_definitions(tree, target)
            for func in funcs:
                doc = ast.get_docstring(func) or ""
                result[target]["implementations"].append({
                    "file": str(rel),
                    "line": func.lineno,
                    "doc_summary": doc.split("\n")[0] if doc else "",
                })

            cs = find_calls(tree, target)
            for c in cs:
                result[target]["calls"].append({"file": str(rel), **c})

    return result


def analyze_node_execution_graph_body() -> dict[str, Any]:
    """Analyze the body of create_node_execution_graph to see if it uses real DualAgentNode."""
    target_file = AUTO_BMAD / "node_execution" / "graph.py"
    tree = parse_file(target_file)
    if tree is None:
        return {"error": "Could not parse graph.py"}

    findings = {
        "has_dual_agent_import": False,
        "executor_uses_deep_copy_only": False,
        "executor_calls_any_real_node_logic": False,
        "calls_in_executor": [],
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if "dual_agent" in alias.name.lower() or (
                    node.module and "dual_agent" in node.module
                ):
                    findings["has_dual_agent_import"] = True

    # Find _create_node_run_executor
    for func in ast.walk(tree):
        if isinstance(func, ast.FunctionDef) and func.name == "_create_node_run_executor":
            # Walk inner Call nodes
            for inner in ast.walk(func):
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Name):
                        findings["calls_in_executor"].append(inner.func.id)
                    elif isinstance(inner.func, ast.Attribute):
                        findings["calls_in_executor"].append(inner.func.attr)

    # Heuristic: if executor only calls copy.deepcopy and basic dict ops, it's a dummy
    calls = set(findings["calls_in_executor"])
    if calls.issubset({"deepcopy"}):
        findings["executor_uses_deep_copy_only"] = True
    if "execute" in calls or "create_dual_agent_node" in calls or "create_node_executor" in calls:
        findings["executor_calls_any_real_node_logic"] = True

    return findings


def trace_public_exports() -> dict[str, Any]:
    """Trace which __init__.py files export the legacy vs new create_node_executor."""
    result = {}
    for init_file in [AUTO_BMAD / "__init__.py", AUTO_BMAD / "nodes" / "__init__.py", AUTO_BMAD / "node_execution" / "__init__.py"]:
        rel = str(init_file.relative_to(PROJECT_ROOT))
        text = init_file.read_text(encoding="utf-8")
        result[rel] = {
            "exports_legacy_dual_agent": "nodes.dual_agent import" in text and "create_node_executor" in text,
            "exports_new_executor": "node_execution.executor import" in text and "create_node_executor" in text,
            "has_lazy_loader": "__getattr__" in text,
        }
    return result


def find_execute_node_flow_usage() -> dict[str, Any]:
    files = find_python_files(AUTO_BMAD)
    calls = []
    for f in files:
        tree = parse_file(f)
        if tree is None:
            continue
        rel = f.relative_to(PROJECT_ROOT)
        cs = find_calls(tree, "execute_node_flow")
        for c in cs:
            calls.append({"file": str(rel), **c})
    return {"calls": calls}


def main() -> int:
    report = {
        "title": "P0-2 执行主干分叉深度分析报告",
        "findings": {
            "create_node_executor": analyze_create_node_executor(),
            "graph_factories": analyze_graph_factories(),
            "node_execution_graph_body": analyze_node_execution_graph_body(),
            "public_exports": trace_public_exports(),
            "execute_node_flow_usage": find_execute_node_flow_usage(),
        },
    }

    output_path = PROJECT_ROOT / "docs" / "research" / "p0-2-execution-trunk-analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {output_path}")

    # Print human-readable summary
    print("\n" + "=" * 60)
    print("P0-2 执行主干分叉 — 快速摘要")
    print("=" * 60)

    ce = report["findings"]["create_node_executor"]
    print(f"\n发现 {len(ce['implementations'])} 个 create_node_executor 实现:")
    for impl in ce["implementations"]:
        print(f"  - {impl['file']}:{impl['line']}  args={impl['args']}")

    print(f"\n发现 {len(ce['calls'])} 处调用 create_node_executor:")
    for c in ce["calls"]:
        print(f"  - {c['file']}:{c['line']} ({c.get('chain', 'direct')})")

    gf = report["findings"]["graph_factories"]
    for name, data in gf.items():
        print(f"\n{name}: {len(data['implementations'])} 实现, {len(data['calls'])} 调用")
        for impl in data["implementations"]:
            print(f"  实现: {impl['file']}:{impl['line']}")
        for c in data["calls"]:
            print(f"  调用: {c['file']}:{c['line']}")

    body = report["findings"]["node_execution_graph_body"]
    print(f"\nnode_execution/graph.py 中的 _create_node_run_executor:")
    print(f"  - 是否仅 deep_copy? {body['executor_uses_deep_copy_only']}")
    print(f"  - 是否调用真实节点逻辑? {body['executor_calls_any_real_node_logic']}")

    usage = report["findings"]["execute_node_flow_usage"]
    print(f"\nexecute_node_flow 调用点: {len(usage['calls'])}")
    for c in usage["calls"]:
        print(f"  - {c['file']}:{c['line']}")

    exports = report["findings"]["public_exports"]
    print(f"\n公共导出分析:")
    for path, info in exports.items():
        print(f"  {path}: legacy={info['exports_legacy_dual_agent']}, new={info['exports_new_executor']}, lazy={info['has_lazy_loader']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Phase A - P0 异步边界问题深度调试工具
=====================================
针对 Finding P0-1 和 P0-2 的深度研究：
1. start_pipeline() 内部 asyncio.run() 运行时缺陷
2. PipelineService._run_async() bridge 残留

使用方法:
    python tools/phase_a_research/p0_async_boundary_debugger.py
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
AUTO_BMAD = PROJECT_ROOT / "autoBMAD" / "docuswarm"


def parse_file(path: Path) -> ast.AST | None:
    """Parse Python file to AST."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as e:
        print(f"  [ERROR] Syntax error in {path}: {e}")
        return None


def find_async_function_calls(tree: ast.AST, func_name: str) -> list[dict[str, Any]]:
    """Find calls to a specific async function."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    func = inner.func
                    if isinstance(func, ast.Attribute) and func.attr == func_name:
                        results.append({
                            "line": inner.lineno,
                            "inside_async_func": node.name,
                            "receiver": func.value.id if isinstance(func.value, ast.Name) else "<complex>",
                        })
                    elif isinstance(func, ast.Name) and func.id == func_name:
                        results.append({
                            "line": inner.lineno,
                            "inside_async_func": node.name,
                            "receiver": None,
                        })
    return results


def analyze_start_pipeline_asyncio_run() -> dict[str, Any]:
    """
    分析 Finding P0-1: start_pipeline() 内部的 asyncio.run() 调用
    
    问题：async 函数内部调用 asyncio.run() 会导致 RuntimeError
    """
    print("\n[Phase A - P0-1] 分析 start_pipeline() 异步边界...")
    path = AUTO_BMAD / "pipeline" / "orchestrator.py"
    tree = parse_file(path)
    
    if tree is None:
        return {"error": "parse failed"}
    
    findings = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "asyncio_run_violations": [],
        "state_manager_calls": [],
        "context": {},
    }
    
    # Find start_pipeline function
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "start_pipeline":
            findings["context"]["start_pipeline_line"] = node.lineno
            findings["context"]["start_pipeline_end"] = node.end_lineno
            
            # Look for asyncio.run calls inside
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    func = inner.func
                    # Check for asyncio.run
                    if isinstance(func, ast.Attribute) and func.attr == "run":
                        if isinstance(func.value, ast.Name) and func.value.id == "asyncio":
                            findings["asyncio_run_violations"].append({
                                "line": inner.lineno,
                                "context": "Inside async start_pipeline()",
                            })
                    # Check for direct asyncio.run import
                    elif isinstance(func, ast.Name) and func.id == "run":
                        # Check if asyncio was imported
                        findings["asyncio_run_violations"].append({
                            "line": inner.lineno,
                            "context": "Possible asyncio.run()",
                        })
                    
                    # Check for update_pipeline_state calls
                    if isinstance(func, ast.Attribute) and func.attr == "update_pipeline_state":
                        findings["state_manager_calls"].append({
                            "line": inner.lineno,
                            "type": "call",
                        })
            break
    
    print(f"  发现 {len(findings['asyncio_run_violations'])} 处 asyncio.run() 违规")
    for v in findings["asyncio_run_violations"]:
        print(f"    - 第 {v['line']} 行: {v['context']}")
    
    return findings


def analyze_run_async_bridge() -> dict[str, Any]:
    """
    分析 Finding P0-2: PipelineService._run_async() bridge 残留
    
    问题：使用 ThreadPoolExecutor + asyncio.run 的手动桥接被架构测试禁止
    """
    print("\n[Phase A - P0-2] 分析 PipelineService._run_async() bridge...")
    path = AUTO_BMAD / "cli" / "services" / "pipeline_service.py"
    tree = parse_file(path)
    
    if tree is None:
        return {"error": "parse failed"}
    
    findings = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "run_async_found": False,
        "run_async_line": None,
        "thread_pool_usage": [],
        "asyncio_run_in_bridge": [],
        "usage_locations": [],
    }
    
    # Find _run_async function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_async":
            findings["run_async_found"] = True
            findings["run_async_line"] = node.lineno
            findings["run_async_end"] = node.end_lineno
            
            # Analyze its implementation
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    func = inner.func
                    # Check for ThreadPoolExecutor
                    if isinstance(func, ast.Name) and func.id == "ThreadPoolExecutor":
                        findings["thread_pool_usage"].append({
                            "line": inner.lineno,
                            "type": "constructor",
                        })
                    elif isinstance(func, ast.Attribute) and func.attr == "submit":
                        findings["thread_pool_usage"].append({
                            "line": inner.lineno,
                            "type": "submit",
                        })
                    # Check for asyncio.run
                    elif isinstance(func, ast.Attribute) and func.attr == "run":
                        findings["asyncio_run_in_bridge"].append({
                            "line": inner.lineno,
                        })
    
    # Find all usages of _run_async
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "_run_async":
                # Find the enclosing function
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.FunctionDef) or isinstance(parent, ast.AsyncFunctionDef):
                        if any(inner is node for inner in ast.walk(parent)):
                            findings["usage_locations"].append({
                                "line": node.lineno,
                                "inside_function": parent.name,
                            })
                            break
    
    print(f"  _run_async 函数: {'发现' if findings['run_async_found'] else '未找到'}")
    if findings["run_async_found"]:
        print(f"    - 位置: 第 {findings['run_async_line']} 行")
        print(f"    - ThreadPoolExecutor 使用: {len(findings['thread_pool_usage'])} 处")
        print(f"    - 内部 asyncio.run: {len(findings['asyncio_run_in_bridge'])} 处")
        print(f"    - 调用点: {len(findings['usage_locations'])} 处")
        for loc in findings["usage_locations"]:
            print(f"      - 第 {loc['line']} 行 (在 {loc['inside_function']} 内)")
    
    return findings


def analyze_escalation_missing_await() -> dict[str, Any]:
    """
    分析 Finding P1-1: DualAgentNode 中 escalate() 未 await
    
    问题：异步函数被调用但没有 await，导致 coroutine 被丢弃
    """
    print("\n[Phase A - P1-1] 分析 DualAgentNode escalate() 未 await 问题...")
    path = AUTO_BMAD / "nodes" / "dual_agent.py"
    tree = parse_file(path)
    
    if tree is None:
        return {"error": "parse failed"}
    
    findings = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "unawaited_escalate_calls": [],
        "awaited_escalate_calls": [],
        "escalation_handler_checks": [],
    }
    
    # Find all escalate calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "escalate":
                # Check if this is awaited by looking at parent context
                # This is tricky with AST - we'll note the line and analyze manually
                findings["escalation_handler_checks"].append({
                    "line": node.lineno,
                })
    
    # Specifically check lines 807 and 845 from audit report
    target_lines = [807, 845]
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    for i, line in enumerate(lines, 1):
        if i in target_lines and "escalate(" in line:
            has_await = line.strip().startswith("await ") or "await self.escalation_handler" in line
            findings["unawaited_escalate_calls"].append({
                "line": i,
                "code": line.strip(),
                "has_await": has_await,
            })
    
    print(f"  发现 {len(findings['unawaited_escalate_calls'])} 处 escalate 调用:")
    for call in findings["unawaited_escalate_calls"]:
        status = "OK 已 await" if call["has_await"] else "FAIL 未 await (BUG!)"
                    # Unicode removed for Windows compatibility
        print(f"    - 第 {call['line']} 行: {status}")
        print(f"      代码: {call['code'][:80]}...")
    
    return findings


def verify_escalation_is_async() -> dict[str, Any]:
    """Verify that EscalationHandler.escalate is indeed async."""
    print("\n[Phase A - P1-1 验证] 确认 EscalationHandler.escalate 是 async...")
    path = AUTO_BMAD / "pipeline" / "escalation.py"
    tree = parse_file(path)
    
    if tree is None:
        return {"error": "parse failed"}
    
    findings = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "escalate_is_async": False,
        "escalate_line": None,
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "escalate":
            findings["escalate_is_async"] = True
            findings["escalate_line"] = node.lineno
            break
    
    status = "是 async" if findings["escalate_is_async"] else "不是 async"
    print(f"  EscalationHandler.escalate: {status}")
    if findings["escalate_line"]:
        print(f"    - 定义位置: 第 {findings['escalate_line']} 行")
    
    return findings


def create_minimal_reproduction_script() -> str:
    """Create a minimal reproduction script for the asyncio.run issue."""
    script_content = '''"""
Phase A - P0-1 最小复现脚本
==========================
复现 HybridOrchestrator.start_pipeline() 中的 asyncio.run() 问题

运行方式:
    python docs/research/phase_a_p0_1_reproduction.py
"""

import asyncio


async def mock_state_update(*args, **kwargs):
    """Mock state manager update."""
    print("  [Mock] State update called")
    return True


async def start_pipeline_v1(subject_context: dict) -> str:
    """
    当前实现 - 有问题版本
    在 async 函数内部使用 asyncio.run() - 会导致 RuntimeError
    """
    print("[V1 - 问题版本] 调用 asyncio.run()...")
    try:
        # This is what the current code does - line 328 in orchestrator.py
        _ = asyncio.run(mock_state_update())
        print("  FAIL 不应该到达这里")
    except RuntimeError as e:
        print(f"  FAIL RuntimeError: {e}")
        raise
    return "pipeline-id"


async def start_pipeline_v2(subject_context: dict) -> str:
    """
    修复版本 - 使用 await
    """
    print("[V2 - 修复版本] 使用 await...")
    _ = await mock_state_update()
    print("  OK 成功执行")
    return "pipeline-id"


async def main():
    print("=" * 60)
    print("Phase A - P0-1 异步边界问题复现")
    print("=" * 60)
    
    test_context = {"subject": "test"}
    
    # Test V1 (broken)
    print("\\n测试当前实现 (asyncio.run 版本):")
    try:
        await start_pipeline_v1(test_context)
    except RuntimeError as e:
        print(f"  → 复现成功: {e}")
    
    # Test V2 (fixed)
    print("\\n测试修复版本 (await 版本):")
    await start_pipeline_v2(test_context)
    
    print("\\n" + "=" * 60)
    print("结论: 必须在 async 函数内使用 await 而不是 asyncio.run()")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
'''
    return script_content


def main() -> int:
    """Run all Phase A debugging analysis."""
    print("=" * 70)
    print("Phase A 异步边界问题深度调试")
    print("=" * 70)
    print("目标: 识别和复现 P0-1, P0-2, P1-1 问题的根因")
    
    report = {
        "title": "Phase A 异步边界问题深度研究报告",
        "description": "针对 Finding P0-1, P0-2, P1-1 的代码分析和问题复现",
        "timestamp": "2026-04-04",
        "findings": {},
    }
    
    # Analyze P0-1
    report["findings"]["p0_1_start_pipeline_asyncio_run"] = analyze_start_pipeline_asyncio_run()
    
    # Analyze P0-2
    report["findings"]["p0_2_run_async_bridge"] = analyze_run_async_bridge()
    
    # Analyze P1-1
    report["findings"]["p1_1_escalation_missing_await"] = analyze_escalation_missing_await()
    report["findings"]["p1_1_escalation_is_async"] = verify_escalation_is_async()
    
    # Write report
    output_path = PROJECT_ROOT / "docs" / "research" / "phase_a_async_boundary_analysis.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[完成] 分析报告已保存: {output_path}")
    
    # Create minimal reproduction script
    repro_script = create_minimal_reproduction_script()
    repro_path = PROJECT_ROOT / "docs" / "research" / "phase_a_p0_1_reproduction.py"
    repro_path.write_text(repro_script, encoding="utf-8")
    print(f"[完成] 复现脚本已保存: {repro_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Phase A 调试摘要")
    print("=" * 70)
    
    p0_1 = report["findings"]["p0_1_start_pipeline_asyncio_run"]
    print(f"\n[P0-1] start_pipeline() asyncio.run 违规:")
    print(f"  - 违规数量: {len(p0_1.get('asyncio_run_violations', []))}")
    for v in p0_1.get("asyncio_run_violations", []):
        print(f"    - 第 {v['line']} 行")
    print(f"  - 影响: 在运行中的事件循环内调用 asyncio.run() 会导致 RuntimeError")
    
    p0_2 = report["findings"]["p0_2_run_async_bridge"]
    print(f"\n[P0-2] PipelineService._run_async bridge:")
    print(f"  - 发现: {'是' if p0_2.get('run_async_found') else '否'}")
    if p0_2.get('run_async_found'):
        print(f"  - 位置: 第 {p0_2.get('run_async_line')} 行")
        print(f"  - 架构测试状态: 失败 (test_no_run_async_bridge_anywhere)")
    
    p1_1 = report["findings"]["p1_1_escalation_missing_await"]
    unawaited = [c for c in p1_1.get("unawaited_escalate_calls", []) if not c["has_await"]]
    print(f"\n[P1-1] DualAgentNode escalate() 未 await:")
    print(f"  - 未 await 调用: {len(unawaited)} 处")
    for call in unawaited:
        print(f"    - 第 {call['line']} 行")
    print(f"  - 影响: 升级动作可能不会真正执行，导致状态不一致")
    
    print("\n" + "=" * 70)
    print("建议修复顺序:")
    print("  1. 立即修复 P0-1: 将 orchestrator.py:328,391 的 asyncio.run() 改为 await")
    print("  2. 立即修复 P0-2: 移除 pipeline_service.py 的 _run_async() bridge")
    print("  3. 立即修复 P1-1: 为 dual_agent.py:807,845 的 escalate() 添加 await")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

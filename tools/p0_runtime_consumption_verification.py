"""
P0 Runtime Consumption Fix Verification - 修复验证工具

用于验证P0问题修复是否生效
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def setup_paths():
    """设置导入路径"""
    project_root = Path(__file__).parent.parent.resolve()
    auto_bmad_path = project_root / "autoBMAD"
    if str(auto_bmad_path) not in sys.path:
        sys.path.insert(0, str(auto_bmad_path))
    return project_root, auto_bmad_path


def verify_mcp_key_naming():
    """验证MCP Server Key命名修复"""
    print("=" * 80)
    print("Verification 1: MCP Server Key Naming Fix")
    print("=" * 80)
    
    from autoBMAD.docuswarm.llm.tool_filter import (
        FILE_SERVER_NAME_FORMAT,
        SEARCH_SERVER_NAME_FORMAT,
    )
    
    node_id = "analyst"
    
    # 验证命名格式常量存在且正确
    file_key = FILE_SERVER_NAME_FORMAT.format(node_id=node_id)
    search_key = SEARCH_SERVER_NAME_FORMAT.format(node_id=node_id)
    
    print(f"\nNodeToolFilter naming formats:")
    print(f"  File Server Key: {file_key}")
    print(f"  Search Server Key: {search_key}")
    print(f"  Keys Equal? {file_key == search_key}")
    
    if file_key != search_key:
        print("  [PASS] Server keys are different - no conflict!")
        return {"check": "mcp_key_naming", "status": "PASS", "file_key": file_key, "search_key": search_key}
    else:
        print("  [FAIL] Server keys are still the same!")
        return {"check": "mcp_key_naming", "status": "FAIL", "error": "Keys still conflict"}


def verify_session_manager_accepts_tool_permissions():
    """验证SessionManager接受tool_permissions参数"""
    print("\n" + "=" * 80)
    print("Verification 2: SessionManager tool_permissions Parameter")
    print("=" * 80)
    
    import inspect
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    
    sig = inspect.signature(SessionManager.__init__)
    params = list(sig.parameters.keys())
    
    print(f"\nSessionManager.__init__ parameters:")
    for p in params:
        print(f"  - {p}")
    
    if "tool_permissions" in params:
        print("\n  [PASS] SessionManager accepts tool_permissions parameter!")
        return {"check": "session_manager_params", "status": "PASS", "has_tool_permissions": True}
    else:
        print("\n  [FAIL] SessionManager does not accept tool_permissions!")
        return {"check": "session_manager_params", "status": "FAIL", "has_tool_permissions": False}


def verify_evaluator_agent_uses_instance_thresholds():
    """验证EvaluatorAgent使用实例阈值"""
    print("\n" + "=" * 80)
    print("Verification 3: EvaluatorAgent Instance Thresholds")
    print("=" * 80)
    
    from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
    
    # 检查类常量已重命名为DEFAULT_*
    has_default_approval = hasattr(EvaluatorAgent, 'DEFAULT_APPROVAL_THRESHOLD')
    has_default_blocked = hasattr(EvaluatorAgent, 'DEFAULT_BLOCKED_THRESHOLD')
    has_old_approval = hasattr(EvaluatorAgent, 'APPROVAL_THRESHOLD') and not has_default_approval
    
    print(f"\nEvaluatorAgent class attributes:")
    print(f"  DEFAULT_APPROVAL_THRESHOLD: {has_default_approval}")
    print(f"  DEFAULT_BLOCKED_THRESHOLD: {has_default_blocked}")
    print(f"  Old APPROVAL_THRESHOLD (bad): {has_old_approval}")
    
    # 检查_load_thresholds方法存在
    has_load_thresholds = hasattr(EvaluatorAgent, '_load_thresholds')
    print(f"  _load_thresholds method: {has_load_thresholds}")
    
    if has_default_approval and has_load_thresholds:
        print("\n  [PASS] EvaluatorAgent uses instance thresholds with fallback defaults!")
        return {"check": "evaluator_thresholds", "status": "PASS", "uses_instance_thresholds": True}
    else:
        print("\n  [FAIL] EvaluatorAgent still uses class constants!")
        return {"check": "evaluator_thresholds", "status": "FAIL", "uses_instance_thresholds": False}


def verify_dual_agent_node_loads_max_iterations():
    """验证create_dual_agent_node加载max_iterations"""
    print("\n" + "=" * 80)
    print("Verification 4: create_dual_agent_node max_iterations Loading")
    print("=" * 80)
    
    import inspect
    from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
    
    sig = inspect.signature(create_dual_agent_node)
    max_iter_param = sig.parameters.get('max_iterations')
    
    print(f"\ncreate_dual_agent_node max_iterations parameter:")
    print(f"  Default value: {max_iter_param.default if max_iter_param else 'NOT FOUND'}")
    
    # 检查源代码中是否调用了NodeLoader.load
    import ast
    source_file = Path(create_dual_agent_node.__code__.co_filename)
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    has_node_loader_load = 'NodeLoader.load' in source and 'max_iterations' in source
    print(f"  Source references NodeLoader.load for max_iterations: {has_node_loader_load}")
    
    if max_iter_param and max_iter_param.default is None and has_node_loader_load:
        print("\n  [PASS] create_dual_agent_node loads max_iterations from config!")
        return {"check": "max_iterations_loading", "status": "PASS", "loads_from_config": True}
    else:
        print("\n  [FAIL] create_dual_agent_node does not load from config!")
        return {"check": "max_iterations_loading", "status": "FAIL", "loads_from_config": False}


def verify_executor_uses_repo_root():
    """验证executor使用仓库根目录"""
    print("\n" + "=" * 80)
    print("Verification 5: executor.py Uses Repo Root")
    print("=" * 80)
    
    source_file = Path(__file__).parent.parent / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # 检查关键修复代码
    has_repo_root = 'repo_root' in source and 'auto_bmad_root.parent' in source
    has_p0_fix_comment = 'P0 Fix' in source and 'repo root' in source.lower()
    
    print(f"\nexecutor.py analysis:")
    print(f"  Has repo_root variable: {'repo_root' in source}")
    print(f"  Uses auto_bmad_root.parent: {'auto_bmad_root.parent' in source}")
    print(f"  Has P0 Fix comment: {has_p0_fix_comment}")
    
    if has_repo_root:
        print("\n  [PASS] executor.py uses repo root for project_root!")
        return {"check": "executor_repo_root", "status": "PASS", "uses_repo_root": True}
    else:
        print("\n  [FAIL] executor.py still uses autoBMAD as project_root!")
        return {"check": "executor_repo_root", "status": "FAIL", "uses_repo_root": False}


def verify_independent_agent_passes_full_permissions():
    """验证IndependentAgent传递完整tool_permissions"""
    print("\n" + "=" * 80)
    print("Verification 6: IndependentAgent Full Tool Permissions")
    print("=" * 80)
    
    source_file = Path(__file__).parent.parent / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # 检查关键修复代码
    has_full_tool_permissions = 'full_tool_permissions' in source
    has_allowed_builtin_tools = 'allowed_builtin_tools' in source and 'node_config.tool_permissions' in source
    has_tool_permissions_param = 'tool_permissions=full_tool_permissions' in source
    
    print(f"\nindependent.py analysis:")
    print(f"  Creates full_tool_permissions: {has_full_tool_permissions}")
    print(f"  Includes allowed_builtin_tools: {has_allowed_builtin_tools}")
    print(f"  Passes tool_permissions to SessionManager: {has_tool_permissions_param}")
    
    if has_full_tool_permissions and has_allowed_builtin_tools and has_tool_permissions_param:
        print("\n  [PASS] IndependentAgent passes full tool_permissions!")
        return {"check": "independent_agent_permissions", "status": "PASS", "passes_full_permissions": True}
    else:
        print("\n  [FAIL] IndependentAgent does not pass full permissions!")
        return {"check": "independent_agent_permissions", "status": "FAIL", "passes_full_permissions": False}


def run_all_verifications():
    """运行所有验证"""
    print("\n" + "=" * 80)
    print("P0 Runtime Consumption Fix Verification Summary")
    print("=" * 80)
    
    results = []
    
    checks = [
        verify_mcp_key_naming,
        verify_session_manager_accepts_tool_permissions,
        verify_evaluator_agent_uses_instance_thresholds,
        verify_dual_agent_node_loads_max_iterations,
        verify_executor_uses_repo_root,
        verify_independent_agent_passes_full_permissions,
    ]
    
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"\n[ERROR] {check.__name__}: {e}")
            results.append({"check": check.__name__, "status": "ERROR", "error": str(e)})
    
    # 保存报告
    report_path = Path(__file__).parent.parent / "docs" / "research" / "p0_runtime_consumption_verification_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n验证报告已保存: {report_path}")
    
    # 打印汇总
    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80)
    
    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    fail_count = sum(1 for r in results if r.get("status") == "FAIL")
    error_count = sum(1 for r in results if r.get("status") == "ERROR")
    
    for r in results:
        status = r.get("status", "UNKNOWN")
        check_name = r.get("check", "unknown")
        symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERROR]"
        print(f"  {symbol} {check_name}")
    
    print(f"\n总计: {pass_count} 通过, {fail_count} 失败, {error_count} 错误")
    
    if fail_count == 0 and error_count == 0:
        print("\n[ALL PASSED] All P0 fixes are in place!")
    else:
        print("\n[WARNING] Some P0 fixes may not be complete.")
    
    return results


if __name__ == "__main__":
    setup_paths()
    run_all_verifications()

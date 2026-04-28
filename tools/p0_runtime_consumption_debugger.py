"""
P0 Runtime Consumption Debugger - 运行时消费链路深度调试工具

用于研究和诊断以下P0问题：
1. MCP servers key 命名冲突
2. NodeToolPermissions 传递丢失 allowed_builtin_tools
3. Evaluator 阈值配置未正确消费
4. 节点权限目录解析基准错误
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


def setup_paths():
    """设置导入路径"""
    project_root = Path(__file__).parent.parent.resolve()
    auto_bmad_path = project_root / "autoBMAD"
    if str(auto_bmad_path) not in sys.path:
        sys.path.insert(0, str(auto_bmad_path))
    return project_root, auto_bmad_path


def analyze_mcp_key_naming():
    """分析MCP server key命名问题
    
    P0 Issue 1: SessionManager._create_options() 使用类名生成key导致冲突
    """
    print("=" * 80)
    print("P0 Issue 1: MCP Server Key Naming Analysis")
    print("=" * 80)
    
    # 模拟当前实现的问题
    node_id = "analyst"
    file_server_class = "FastMCP"  # 文件server的类名
    search_server_class = "FastMCP"  # 搜索server的类名
    
    # 当前问题实现
    current_key_format = "docuswarm-{class_name.lower()}-{node_id}"
    file_key_current = current_key_format.format(class_name=file_server_class, node_id=node_id)
    search_key_current = current_key_format.format(class_name=search_server_class, node_id=node_id)
    
    print(f"\n当前实现 (问题):")
    print(f"  File Server Key: {file_key_current}")
    print(f"  Search Server Key: {search_key_current}")
    print(f"  Keys Equal? {file_key_current == search_key_current}")
    print(f"  问题: 两个server映射到同一个key，导致后覆盖前!")
    
    # NodeToolFilter的正确命名
    file_key_correct = f"docuswarm-files-{node_id}"
    search_key_correct = f"docuswarm-search-{node_id}"
    
    print(f"\n正确实现 (应与NodeToolFilter一致):")
    print(f"  File Server Key: {file_key_correct}")
    print(f"  Search Server Key: {search_key_correct}")
    print(f"  Keys Equal? {file_key_correct == search_key_correct}")
    
    # allowed_tools中的工具名
    print(f"\nallowed_tools工具名格式:")
    print(f"  File Tool: mcp__docuswarm-files-{node_id}__read_document")
    print(f"  Search Tool: mcp__docuswarm-search-{node_id}__grep_search")
    
    return {
        "issue": "mcp_key_naming_conflict",
        "current_file_key": file_key_current,
        "current_search_key": search_key_current,
        "correct_file_key": file_key_correct,
        "correct_search_key": search_key_correct,
        "has_conflict": file_key_current == search_key_current,
    }


def analyze_tool_permissions_propagation():
    """分析NodeToolPermissions传递问题
    
    P0 Issue 2: IndependentAgent只传递file_dirs/search_dirs，丢失allowed_builtin_tools
    """
    print("\n" + "=" * 80)
    print("P0 Issue 2: NodeToolPermissions Propagation Analysis")
    print("=" * 80)
    
    from autoBMAD.nodes.loader import NodeLoader
    
    project_root = Path(__file__).parent.parent.resolve()
    auto_bmad_path = project_root / "autoBMAD"
    NodeLoader.set_base_path(auto_bmad_path)
    
    node_id = "analyst"
    config = NodeLoader.load(node_id)
    
    print(f"\nNodeLoader加载的完整配置 (node_id={node_id}):")
    print(f"  allowed_builtin_tools: {config.tool_permissions.allowed_builtin_tools}")
    print(f"  file_permissions.allowed_read_dirs: {config.tool_permissions.file_permissions.allowed_read_dirs}")
    print(f"  search_permissions.search_dirs: {config.tool_permissions.search_permissions.search_dirs}")
    
    # 模拟当前IndependentAgent的行为 (只传递dirs)
    print(f"\n当前IndependentAgent.execute_with_input()行为:")
    file_dirs = [
        str(auto_bmad_path / d)
        for d in config.tool_permissions.file_permissions.allowed_read_dirs
    ]
    search_dirs = [
        str(auto_bmad_path / d)
        for d in config.tool_permissions.search_permissions.search_dirs
    ]
    print(f"  file_dirs: {file_dirs}")
    print(f"  search_dirs: {search_dirs}")
    print(f"  allowed_builtin_tools: <NOT PASSED>")
    
    # SessionManager重建的NodeToolPermissions
    print(f"\nSessionManager._create_options()重建的权限:")
    from autoBMAD.nodes.loader import NodeFilePermissions, NodeSearchPermissions, NodeToolPermissions
    
    reconstructed = NodeToolPermissions(
        file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
        search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
    )
    print(f"  allowed_builtin_tools: {reconstructed.allowed_builtin_tools} (应该是 {config.tool_permissions.allowed_builtin_tools})")
    print(f"  问题: allowed_builtin_tools丢失了!")
    
    return {
        "issue": "tool_permissions_propagation_loss",
        "node_id": node_id,
        "config_builtin_tools": config.tool_permissions.allowed_builtin_tools,
        "reconstructed_builtin_tools": reconstructed.allowed_builtin_tools,
        "has_loss": reconstructed.allowed_builtin_tools != config.tool_permissions.allowed_builtin_tools,
    }


def analyze_directory_resolution():
    """分析目录解析基准问题
    
    P0 Issue 3: 节点权限目录解析基准错误，docs/被解析为autoBMAD/docs/而非仓库根下的docs/
    """
    print("\n" + "=" * 80)
    print("P0 Issue 3: Directory Resolution Baseline Analysis")
    print("=" * 80)
    
    # 模拟当前实现
    node_config_dir = "docs/"
    
    # 当前实现的问题
    auto_bmad_path = Path(__file__).parent.parent.resolve() / "autoBMAD"
    current_resolved = auto_bmad_path / node_config_dir
    
    # 正确的仓库根路径
    repo_root = Path(__file__).parent.parent.resolve()
    correct_resolved = repo_root / node_config_dir
    
    print(f"\n当前实现 (问题):")
    print(f"  project_root: {auto_bmad_path}")
    print(f"  node_config_dir: {node_config_dir}")
    print(f"  resolved_path: {current_resolved}")
    print(f"  exists: {current_resolved.exists()}")
    
    print(f"\n正确实现:")
    print(f"  repo_root: {repo_root}")
    print(f"  node_config_dir: {node_config_dir}")
    print(f"  resolved_path: {correct_resolved}")
    print(f"  exists: {correct_resolved.exists()}")
    
    print(f"\n结论:")
    if current_resolved.exists():
        print("  当前实现路径存在 (但可能只是巧合)")
    else:
        print("  当前实现路径不存在! 这是运行时权限失效的原因")
    
    if correct_resolved.exists():
        print("  仓库根路径存在，这是正确的基准")
    else:
        print("  仓库根路径也不存在，需要检查配置")
    
    return {
        "issue": "directory_resolution_baseline",
        "current_path": str(current_resolved),
        "current_exists": current_resolved.exists(),
        "correct_path": str(correct_resolved),
        "correct_exists": correct_resolved.exists(),
    }


def analyze_evaluator_threshold_consumption():
    """分析Evaluator阈值配置消费问题
    
    P0 Issue 4: Evaluator阈值和max_iterations配置没有正确进入运行时
    """
    print("\n" + "=" * 80)
    print("P0 Issue 4: Evaluator Threshold Configuration Consumption")
    print("=" * 80)
    
    from autoBMAD.nodes.loader import NodeLoader
    from autoBMAD.docuswarm.pipeline.quality import QualityConfig
    from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
    
    project_root = Path(__file__).parent.parent.resolve()
    auto_bmad_path = project_root / "autoBMAD"
    NodeLoader.set_base_path(auto_bmad_path)
    
    node_id = "architect"
    config = NodeLoader.load(node_id)
    
    print(f"\nNodeLoader加载的evaluator配置 (node_id={node_id}):")
    if config.evaluator:
        print(f"  threshold: {config.evaluator.threshold}")
        print(f"  max_iterations: {config.evaluator.max_iterations}")
    else:
        print("  无evaluator配置")
    
    # EvaluatorAgent的硬编码阈值
    print(f"\nEvaluatorAgent的硬编码阈值:")
    print(f"  APPROVAL_THRESHOLD: {EvaluatorAgent.APPROVAL_THRESHOLD}")
    print(f"  BLOCKED_THRESHOLD: {EvaluatorAgent.BLOCKED_THRESHOLD}")
    
    # QualityConfig的阈值
    qc = QualityConfig()
    thresholds = qc.get_thresholds(node_id)
    print(f"\nQualityConfig.get_thresholds('{node_id}'):")
    print(f"  approval: {thresholds.approval}")
    print(f"  escalation: {thresholds.escalation}")
    
    # 对比
    print(f"\n配置对比 (应该一致但实际不一致):")
    if config.evaluator:
            print(f"  NodeLoader threshold.approval: {config.evaluator.threshold.get('approval', 'N/A')}")
            print(f"  EvaluatorAgent.APPROVAL_THRESHOLD: {EvaluatorAgent.APPROVAL_THRESHOLD}")
            print(f"  QualityConfig approval: {thresholds.approval}")
            print(f"  NodeLoader threshold.escalation: {config.evaluator.threshold.get('escalation', 'N/A')}")
            print(f"  EvaluatorAgent.BLOCKED_THRESHOLD: {EvaluatorAgent.BLOCKED_THRESHOLD}")
            print(f"  QualityConfig escalation: {thresholds.escalation}")
    
    # max_iterations
    print(f"\nmax_iterations对比:")
    if config.evaluator:
        print(f"  NodeLoader max_iterations: {config.evaluator.max_iterations}")
    print(f"  DualAgentNode.DEFAULT_MAX_ITERATIONS: 3 (硬编码)")
    
    return {
        "issue": "evaluator_threshold_not_consumed",
        "node_id": node_id,
        "node_loader_threshold": config.evaluator.threshold if config.evaluator else None,
        "node_loader_max_iterations": config.evaluator.max_iterations if config.evaluator else None,
        "evaluator_agent_approval": EvaluatorAgent.APPROVAL_THRESHOLD,
        "evaluator_agent_blocked": EvaluatorAgent.BLOCKED_THRESHOLD,
        "quality_config_approval": thresholds.approval,
        "quality_config_escalation": thresholds.escalation,
    }


def analyze_allowed_tools_generation():
    """分析allowed_tools生成，验证builtin tools是否被包含"""
    print("\n" + "=" * 80)
    print("Analysis: allowed_tools Generation Verification")
    print("=" * 80)
    
    from autoBMAD.nodes.loader import NodeLoader
    from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
    
    project_root = Path(__file__).parent.parent.resolve()
    auto_bmad_path = project_root / "autoBMAD"
    NodeLoader.set_base_path(auto_bmad_path)
    
    node_id = "analyst"
    config = NodeLoader.load(node_id)
    
    print(f"\nNodeToolFilter从NodeConfig生成的allowed_tools:")
    filter_obj = NodeToolFilter.from_node_config(config)
    allowed_tools = filter_obj.get_allowed_tools()
    
    print(f"  allowed_tools ({len(allowed_tools)} items):")
    for tool in allowed_tools:
        print(f"    - {tool}")
    
    # 检查builtin tools
    builtin_tools = config.tool_permissions.allowed_builtin_tools
    print(f"\n  期望的builtin tools: {builtin_tools}")
    
    for tool in builtin_tools:
        if tool in allowed_tools:
            print(f"    ✓ {tool} 已包含在allowed_tools中")
        else:
            print(f"    ✗ {tool} 丢失!")
    
    # 问题根源
    print(f"\n问题根源分析:")
    print(f"  NodeToolFilter.get_allowed_tools()第1步: tools.extend(self.tool_permissions.allowed_builtin_tools)")
    print(f"  但SessionManager._create_options()重建NodeToolPermissions时没有设置allowed_builtin_tools")
    print(f"  所以实际运行时allowed_tools中只有MCP工具，没有builtin工具")
    
    return {
        "issue": "allowed_tools_generation",
        "node_id": node_id,
        "expected_builtin_tools": builtin_tools,
        "actual_allowed_tools": allowed_tools,
        "builtin_tools_present": all(t in allowed_tools for t in builtin_tools),
    }


def generate_full_diagnostic_report():
    """生成完整诊断报告"""
    print("\n" + "=" * 80)
    print("P0 Runtime Consumption Diagnostic Report Summary")
    print("=" * 80)
    
    results = []
    
    try:
        results.append(analyze_mcp_key_naming())
    except Exception as e:
        print(f"MCP Key Naming Analysis Failed: {e}")
        results.append({"issue": "mcp_key_naming_conflict", "error": str(e)})
    
    try:
        results.append(analyze_tool_permissions_propagation())
    except Exception as e:
        print(f"Tool Permissions Propagation Analysis Failed: {e}")
        results.append({"issue": "tool_permissions_propagation_loss", "error": str(e)})
    
    try:
        results.append(analyze_directory_resolution())
    except Exception as e:
        print(f"Directory Resolution Analysis Failed: {e}")
        results.append({"issue": "directory_resolution_baseline", "error": str(e)})
    
    try:
        results.append(analyze_evaluator_threshold_consumption())
    except Exception as e:
        print(f"Evaluator Threshold Analysis Failed: {e}")
        results.append({"issue": "evaluator_threshold_not_consumed", "error": str(e)})
    
    try:
        results.append(analyze_allowed_tools_generation())
    except Exception as e:
        print(f"Allowed Tools Generation Analysis Failed: {e}")
        results.append({"issue": "allowed_tools_generation", "error": str(e)})
    
    # 保存JSON报告
    report_path = Path(__file__).parent.parent / "docs" / "research" / "p0_runtime_consumption_diagnostic_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n\n完整诊断报告已保存: {report_path}")
    
    # 打印汇总
    print("\n" + "=" * 80)
    print("问题汇总 (P0优先级)")
    print("=" * 80)
    
    for r in results:
        issue = r.get("issue", "unknown")
        if "error" in r:
            print(f"  [ERROR] {issue}: {r['error']}")
        elif issue == "mcp_key_naming_conflict":
            print(f"  [{'CRITICAL' if r.get('has_conflict') else 'OK'}] MCP key命名冲突: {r.get('has_conflict')}")
        elif issue == "tool_permissions_propagation_loss":
            print(f"  [{'CRITICAL' if r.get('has_loss') else 'OK'}] ToolPermissions丢失: {r.get('has_loss')}")
        elif issue == "directory_resolution_baseline":
            print(f"  [{'CRITICAL' if not r.get('current_exists') and r.get('correct_exists') else 'OK'}] 目录解析错误: current_exists={r.get('current_exists')}, correct_exists={r.get('correct_exists')}")
        elif issue == "evaluator_threshold_not_consumed":
            nl_thresh = r.get("node_loader_threshold", {}) or {}
            print(f"  [CRITICAL] Evaluator阈值不一致: NodeLoader.approval={nl_thresh.get('approval')}, EvaluatorAgent={r.get('evaluator_agent_approval')}, QualityConfig={r.get('quality_config_approval')}")
        elif issue == "allowed_tools_generation":
            print(f"  [{'CRITICAL' if not r.get('builtin_tools_present') else 'OK'}] Builtin tools缺失: {not r.get('builtin_tools_present')}")
    
    return results


if __name__ == "__main__":
    setup_paths()
    generate_full_diagnostic_report()

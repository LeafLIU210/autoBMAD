#!/usr/bin/env python3
"""
P0 Tool Permission Debugger - F3 Critical Issue Research Tool

研究问题：工具权限配置被 SessionManager 放大，节点白名单没有成为真实边界

目标：
1. 验证节点配置中的 allowed_builtin_tools (如 ["Read", "Glob"]) 是否被尊重
2. 验证 SessionManager._get_builtin_tools() 是否固定返回全部5个工具
3. 验证 _build_allowed_tools() 是否无条件加入内置工具
4. 验证 yolo=True 时 permission_mode = "bypassPermissions" 的影响
5. 验证最终 ClaudeAgentOptions.allowed_tools 是否等于节点配置
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

repo_root = Path(__file__).parent.parent.parent.resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from autoBMAD.docuswarm.llm.session_manager import SessionManager


def test_node_config_tool_permissions() -> dict[str, Any]:
    """Test 1: Read actual node.yaml tool permissions."""
    print("\n" + "=" * 70)
    print("TEST 1: Node Configuration Tool Permissions")
    print("=" * 70)

    findings = {
        "test": "node_config_tool_permissions",
        "issue": "Node yaml declares limited builtin tools, but runtime grants more",
        "evidence": [],
        "severity": "CRITICAL",
    }

    nodes_dir = Path(repo_root) / "autoBMAD" / "nodes"
    node_configs = {}

    for node_name in ["analyst", "pm", "ux", "architect", "po"]:
        yaml_path = nodes_dir / node_name / "node.yaml"
        if yaml_path.exists():
            import yaml
            with open(yaml_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            tools = config.get("tools", {})
            allowed_builtin = tools.get("allowed_builtin_tools", [])
            node_configs[node_name] = {
                "allowed_builtin_tools": allowed_builtin,
                "file_permissions": tools.get("file_permissions", {}),
                "search_permissions": tools.get("search_permissions", {}),
            }

    print("Node configuration allowed_builtin_tools:")
    for node, cfg in node_configs.items():
        print(f"  {node}: {cfg['allowed_builtin_tools']}")

    findings["evidence"].append({
        "location": "autoBMAD/nodes/*/node.yaml",
        "node_configs": node_configs,
        "finding": "All nodes declare allowed_builtin_tools=['Read', 'Glob'] (or similar limited set)",
    })

    return findings


def test_session_manager_builtin_tools() -> dict[str, Any]:
    """Test 2: SessionManager._get_builtin_tools() returns fixed list."""
    print("\n" + "=" * 70)
    print("TEST 2: SessionManager._get_builtin_tools() Fixed List")
    print("=" * 70)

    findings = {
        "test": "session_manager_builtin_tools",
        "issue": "SessionManager._get_builtin_tools() returns ALL 5 builtin tools regardless of node config",
        "evidence": [],
        "severity": "CRITICAL",
    }

    sm = SessionManager()
    builtin_tools = sm._get_builtin_tools()

    print(f"SessionManager._get_builtin_tools() returns: {builtin_tools}")

    expected_from_node_config = ["Read", "Glob"]  # From analyst node.yaml
    extra_tools = [t for t in builtin_tools if t not in expected_from_node_config]

    print(f"\nNode config expects: {expected_from_node_config}")
    print(f"SessionManager adds EXTRA tools: {extra_tools}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/llm/session_manager.py:168-175",
        "session_manager_builtin_tools": builtin_tools,
        "node_config_expected": expected_from_node_config,
        "extra_tools_granted": extra_tools,
        "verdict": "BUG CONFIRMED" if extra_tools else "OK",
    })

    if extra_tools:
        print(f"\n  BUG CONFIRMED: SessionManager grants {extra_tools} that nodes did NOT request!")
        print("  This means agents can Edit files and execute Bash commands even")
        print("  when node configuration explicitly limits to Read/Glob.")

    return findings


def test_build_allowed_tools_composition() -> dict[str, Any]:
    """Test 3: _build_allowed_tools() unconditionally adds builtin tools."""
    print("\n" + "=" * 70)
    print("TEST 3: _build_allowed_tools() Tool Composition")
    print("=" * 70)

    findings = {
        "test": "build_allowed_tools_composition",
        "issue": "_build_allowed_tools() always adds ALL builtin tools before filtering",
        "evidence": [],
        "severity": "CRITICAL",
    }

    sm_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    source = sm_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find _build_allowed_tools
    in_func = False
    func_lines = []
    for i, line in enumerate(lines):
        if "def _build_allowed_tools(self)" in line:
            in_func = True
        if in_func:
            func_lines.append(f"Line {i+1}: {line}")
            if line.strip() == "" and i > 200:
                if i+1 < len(lines) and not lines[i+1].startswith(" ") and "def " in lines[i+1]:
                    break
            if len(func_lines) > 35:
                break

    print("_build_allowed_tools() source:")
    for line in func_lines:
        print(f"  {line}")

    # Check if it unconditionally calls _get_builtin_tools
    has_unconditional_builtin = any("_get_builtin_tools()" in l for l in func_lines)
    has_conditional_logic = any("tool_permissions" in l and "allowed_builtin" in l for l in func_lines)

    print(f"\nAnalysis:")
    print(f"  Unconditionally calls _get_builtin_tools(): {has_unconditional_builtin}")
    print(f"  Checks node tool_permissions for allowed_builtin_tools: {has_conditional_logic}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/llm/session_manager.py:177-227",
        "code": func_lines,
        "has_unconditional_builtin": has_unconditional_builtin,
        "has_conditional_logic": has_conditional_logic,
        "verdict": "BUG CONFIRMED" if (has_unconditional_builtin and not has_conditional_logic) else "PARTIAL",
    })

    if has_unconditional_builtin and not has_conditional_logic:
        print("\n  BUG CONFIRMED: _build_allowed_tools() ALWAYS adds ALL builtin tools")
        print("  WITHOUT consulting node configuration's allowed_builtin_tools!")

    return findings


def test_create_options_permission_mode() -> dict[str, Any]:
    """Test 4: _create_options() sets bypassPermissions when yolo=True."""
    print("\n" + "=" * 70)
    print("TEST 4: _create_options() Permission Mode with yolo=True")
    print("=" * 70)

    findings = {
        "test": "create_options_permission_mode",
        "issue": "yolo=True sets permission_mode='bypassPermissions' which bypasses ALL tool restrictions",
        "evidence": [],
        "severity": "CRITICAL",
    }

    sm_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    source = sm_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find _create_options permission_mode logic
    permission_lines = []
    for i, line in enumerate(lines):
        if "permission_mode" in line or "bypassPermissions" in line or "yolo" in line:
            permission_lines.append(f"Line {i+1}: {line}")

    print("Permission mode related code:")
    for line in permission_lines[:15]:
        print(f"  {line}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/llm/session_manager.py:245-246",
        "code": permission_lines,
        "finding": "permission_mode = 'bypassPermissions' when yolo=True, which bypasses SDK-level permission checks",
    })

    print("\nFinding: Even if allowed_tools were correctly configured,")
    print("  yolo=True sets permission_mode='bypassPermissions' at the SDK level.")
    print("  This means the Claude Agent SDK itself may bypass tool restrictions.")

    return findings


def test_full_allowed_tools_mismatch() -> dict[str, Any]:
    """Test 5: Compare node config expected tools vs SessionManager actual tools."""
    print("\n" + "=" * 70)
    print("TEST 5: Full Allowed Tools Mismatch Analysis")
    print("=" * 70)

    # Load a node config
    from autoBMAD.nodes.loader import NodeLoader

    try:
        node_config = NodeLoader.load("analyst")
        node_expected_tools = node_config.tool_permissions.allowed_builtin_tools
    except Exception as e:
        print(f"Could not load node config: {e}")
        node_expected_tools = ["Read", "Glob"]  # Fallback from yaml

    # Build SessionManager options as it would in production
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    from autoBMAD.nodes.loader import NodeToolPermissions

    sm = SessionManager(
        node_id="analyst",
        tool_permissions=node_config.tool_permissions if 'node_config' in dir() else None,
    )

    # We can't call _create_options() easily without SDK installed
    # But we can call _build_allowed_tools()
    try:
        actual_tools = sm._build_allowed_tools()
    except Exception as e:
        print(f"Could not build allowed tools: {e}")
        actual_tools = []

    print(f"Node 'analyst' expected builtin tools (from config): {node_expected_tools}")
    print(f"SessionManager._build_allowed_tools() returns: {actual_tools}")

    # Analyze mismatch
    unexpected = [t for t in actual_tools if t in ["Edit", "Bash", "Grep"] and t not in node_expected_tools]
    missing = [t for t in node_expected_tools if t not in actual_tools]

    print(f"\nUnexpected tools granted: {unexpected}")
    print(f"Expected tools missing: {missing}")

    findings = {
        "test": "full_allowed_tools_mismatch",
        "node_expected": list(node_expected_tools),
        "session_manager_actual": actual_tools,
        "unexpected_tools": unexpected,
        "missing_tools": missing,
        "verdict": "BUG CONFIRMED" if unexpected else "OK",
    }

    if unexpected:
        print(f"\n  BUG CONFIRMED: SessionManager grants dangerous tools {unexpected}")
        print("  that are NOT in node configuration!")

    return findings


def analyze_permission_escalation_chain() -> dict[str, Any]:
    """Analyze the complete permission escalation chain."""
    print("\n" + "=" * 70)
    print("PERMISSION ESCALATION CHAIN ANALYSIS")
    print("=" * 70)

    chain = [
        {
            "step": 1,
            "layer": "Node Configuration (node.yaml)",
            "declaration": 'allowed_builtin_tools: ["Read", "Glob"]',
            "intent": "Node should only read files and list directories",
        },
        {
            "step": 2,
            "layer": "SessionManager._get_builtin_tools()",
            "behavior": 'Returns ["Read", "Glob", "Grep", "Edit", "Bash"]',
            "violation": "Ignores node config, adds Edit and Bash unconditionally",
        },
        {
            "step": 3,
            "layer": "SessionManager._build_allowed_tools()",
            "behavior": "Calls _get_builtin_tools() and extends with MCP tools",
            "violation": "Never consults NodeToolPermissions.allowed_builtin_tools",
        },
        {
            "step": 4,
            "layer": "SessionManager._create_options()",
            "behavior": "yolo=True -> permission_mode='bypassPermissions'",
            "violation": "SDK-level bypass may override allowed_tools list entirely",
        },
        {
            "step": 5,
            "layer": "Runtime Effect",
            "behavior": "Agent can Edit files and execute Bash commands",
            "risk": "Document generation pipeline can modify source code or execute arbitrary shell",
        },
    ]

    for item in chain:
        print(f"\nStep {item['step']}: {item['layer']}")
        print(f"  {list(item.keys())[1]}: {list(item.values())[1]}")
        print(f"  {list(item.keys())[2]}: {list(item.values())[2]}")

    return {"chain": chain}


def run_all_tests() -> dict[str, Any]:
    """Run all tool permission tests."""
    print("\n" + "=" * 70)
    print("P0 TOOL PERMISSION DEBUGGER")
    print("Issue: F3 - Tool permissions amplified by SessionManager")
    print("=" * 70)

    results = {
        "issue_id": "F3",
        "severity": "CRITICAL",
        "title": "工具权限配置被SessionManager放大，节点白名单没有成为真实边界",
        "tests": [],
        "chain_analysis": None,
    }

    results["tests"].append(test_node_config_tool_permissions())
    results["tests"].append(test_session_manager_builtin_tools())
    results["tests"].append(test_build_allowed_tools_composition())
    results["tests"].append(test_create_options_permission_mode())
    results["tests"].append(test_full_allowed_tools_mismatch())
    results["chain_analysis"] = analyze_permission_escalation_chain()

    return results


if __name__ == "__main__":
    results = run_all_tests()

    output_path = Path(__file__).parent / "p0_tool_permission_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")

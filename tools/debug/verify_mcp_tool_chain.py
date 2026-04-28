#!/usr/bin/env python3
"""
MCP 工具链完整性验证脚本

用于验证 F6 问题: update_context 工具是否已进入 MCP 运行时链路

Usage:
    python tools/debug/verify_mcp_tool_chain.py [node_id]
    python tools/debug/verify_mcp_tool_chain.py --all

Example:
    python tools/debug/verify_mcp_tool_chain.py analyst
    python tools/debug/verify_mcp_tool_chain.py --all
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter


def check_update_context_in_allowed_tools(filter_obj: NodeToolFilter, node_id: str) -> bool:
    """Check if update_context tool is in allowed tools list."""
    allowed = filter_obj.get_allowed_tools()
    has_update_context = any("update_context" in t for t in allowed)
    
    print(f"\n  📋 Allowed tools ({len(allowed)} total):")
    for tool in allowed:
        marker = " ✅" if "update_context" in tool else ""
        print(f"     - {tool}{marker}")
    
    return has_update_context


def check_update_context_server(filter_obj: NodeToolFilter, node_id: str) -> bool:
    """Check if update_context MCP server is created."""
    try:
        servers = filter_obj.create_mcp_servers()
        
        print(f"\n  🔌 MCP Servers ({len(servers)} total):")
        for name in servers.keys():
            marker = " ✅" if "shared-context" in name or "update" in name else ""
            print(f"     - {name}{marker}")
        
        has_shared_context_server = any(
            "shared-context" in k or "update" in k for k in servers.keys()
        )
        return has_shared_context_server
    except Exception as e:
        print(f"\n  ❌ Error creating MCP servers: {e}")
        return False


def verify_node_mcp_chain(node_id: str) -> dict:
    """Verify MCP tool chain for a specific node."""
    print(f"\n{'='*60}")
    print(f"🔍 验证节点: {node_id.upper()}")
    print(f"{'='*60}")
    
    config = NodeLoader.load(node_id)
    filter_obj = NodeToolFilter.from_node_config(config)
    
    # Check configuration layer
    print("\n📊 1. 配置层检查")
    print("-" * 40)
    sc = config.tool_permissions.shared_context
    print(f"   shared_context.enabled: {sc.enabled}")
    print(f"   shared_context.operations: {sc.operations}")
    print(f"   shared_context.allowed_keys: {sc.allowed_keys}")
    
    # Check allowed tools
    print("\n📊 2. 允许的工具列表检查")
    print("-" * 40)
    has_tool = check_update_context_in_allowed_tools(filter_obj, node_id)
    
    # Check MCP servers
    print("\n📊 3. MCP Server 检查")
    print("-" * 40)
    has_server = check_update_context_server(filter_obj, node_id)
    
    # Summary
    print("\n📊 4. 验证结果汇总")
    print("-" * 40)
    
    issues = []
    if sc.enabled and not has_tool:
        issues.append("❌ shared_context 已启用，但 update_context 工具未暴露")
    if sc.enabled and not has_server:
        issues.append("❌ shared_context 已启用，但 update_context server 未创建")
    if not sc.enabled:
        issues.append("⚠️ shared_context 未启用")
    
    if issues:
        for issue in issues:
            print(f"   {issue}")
    else:
        print("   ✅ 所有检查通过")
    
    return {
        "node_id": node_id,
        "shared_context_enabled": sc.enabled,
        "has_update_context_tool": has_tool,
        "has_update_context_server": has_server,
        "issues": issues,
        "passed": len(issues) == 0 if sc.enabled else True
    }


def print_summary(results: list[dict]):
    """Print verification summary."""
    print(f"\n{'='*60}")
    print("📋 验证汇总")
    print(f"{'='*60}")
    
    all_passed = True
    for r in results:
        status = "✅" if r["passed"] else "❌"
        enabled = "启用" if r["shared_context_enabled"] else "禁用"
        
        if r["shared_context_enabled"]:
            tool_status = "✅" if r["has_update_context_tool"] else "❌"
            server_status = "✅" if r["has_update_context_server"] else "❌"
            print(f"\n{status} {r['node_id'].upper()}")
            print(f"   Shared Context: {enabled}")
            print(f"   update_context 工具: {tool_status}")
            print(f"   update_context server: {server_status}")
            
            if r["issues"]:
                for issue in r["issues"]:
                    print(f"   {issue}")
                all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ 所有检查通过 - F6 问题已修复")
    else:
        print("❌ 发现 F6 问题 - 需要修复 update_context MCP 链路")
    print(f"{'='*60}")


def main():
    """Main entry point."""
    nodes = ["analyst", "pm", "ux", "architect", "po"]
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            pass  # Use all nodes
        else:
            nodes = [sys.argv[1]]
    
    print("🔧 MCP 工具链完整性验证")
    print("=" * 60)
    print("验证目标: F6 - update_context 工具是否进入运行时 MCP 链路")
    
    results = []
    for node_id in nodes:
        try:
            result = verify_node_mcp_chain(node_id)
            results.append(result)
        except Exception as e:
            print(f"\n❌ 验证 {node_id} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print_summary(results)
    
    # Exit with error code if any check failed
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

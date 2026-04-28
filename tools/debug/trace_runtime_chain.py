#!/usr/bin/env python3
"""
运行时链路追踪工具

用于深度追踪 IndependentAgent 执行时的完整链路，
验证配置是否真正进入运行时。

Usage:
    python tools/debug/trace_runtime_chain.py --node analyst --pipeline test-001

This will trace:
1. Node config loading
2. Tool permissions extraction
3. SessionManager initialization
4. MCP server creation
5. Allowed tools list
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class RuntimeChainTracer:
    """Tracer for runtime tool chain."""
    
    def __init__(self, node_id: str, pipeline_id: str):
        self.node_id = node_id
        self.pipeline_id = pipeline_id
        self.trace_logs: list[dict] = []
    
    def log(self, stage: str, message: str, data: dict | None = None, status: str = "info"):
        """Log a trace entry."""
        entry = {
            "stage": stage,
            "message": message,
            "data": data or {},
            "status": status,
        }
        self.trace_logs.append(entry)
        
        # Print immediately
        icon = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(status, "ℹ️")
        print(f"\n{icon} [{stage}] {message}")
        if data:
            for key, value in data.items():
                print(f"   {key}: {value}")
    
    def trace_node_config_loading(self):
        """Trace step 1: Node config loading."""
        print("\n" + "="*60)
        print("📋 步骤 1: 加载节点配置")
        print("="*60)
        
        try:
            from autoBMAD.nodes.loader import NodeLoader
            
            config = NodeLoader.load(self.node_id)
            
            self.log(
                "ConfigLoader",
                f"成功加载 {self.node_id} 配置",
                {
                    "task_name": config.task.name,
                    "task_skill_ref": config.task.skill_ref,
                    "deliverable_type": config.deliverable.type,
                },
                "success"
            )
            
            # Tool permissions detail
            tp = config.tool_permissions
            self.log(
                "ToolPermissions",
                "工具权限配置详情",
                {
                    "allowed_builtin_tools": tp.allowed_builtin_tools,
                    "file_read_dirs": tp.file_permissions.allowed_read_dirs,
                    "search_dirs": tp.search_permissions.search_dirs,
                    "skills.sdk_native": tp.skills.sdk_native,
                    "skills.whitelist": tp.skills.whitelist,
                    "shared_context.enabled": tp.shared_context.enabled,
                    "shared_context.operations": tp.shared_context.operations,
                }
            )
            
            return config
            
        except Exception as e:
            self.log("ConfigLoader", f"配置加载失败: {e}", {}, "error")
            raise
    
    def trace_tool_filter_creation(self, config):
        """Trace step 2: NodeToolFilter creation."""
        print("\n" + "="*60)
        print("📋 步骤 2: 创建 NodeToolFilter")
        print("="*60)
        
        try:
            from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
            
            filter_obj = NodeToolFilter.from_node_config(config)
            
            self.log(
                "ToolFilter",
                "NodeToolFilter 创建成功",
                {"node_id": filter_obj.node_id},
                "success"
            )
            
            return filter_obj
            
        except Exception as e:
            self.log("ToolFilter", f"ToolFilter 创建失败: {e}", {}, "error")
            raise
    
    def trace_allowed_tools(self, filter_obj):
        """Trace step 3: Allowed tools generation."""
        print("\n" + "="*60)
        print("📋 步骤 3: 生成允许的工具列表")
        print("="*60)
        
        try:
            allowed_tools = filter_obj.get_allowed_tools()
            
            # Categorize tools
            builtin_tools = [t for t in allowed_tools if not t.startswith("mcp__")]
            mcp_tools = [t for t in allowed_tools if t.startswith("mcp__")]
            
            # Check for update_context
            update_context_tools = [t for t in allowed_tools if "update" in t.lower()]
            shared_context_tools = [t for t in allowed_tools if "shared" in t.lower()]
            
            self.log(
                "AllowedTools",
                f"允许的工具列表 ({len(allowed_tools)} 个)",
                {
                    "builtin_tools": builtin_tools,
                    "mcp_tools_count": len(mcp_tools),
                }
            )
            
            if mcp_tools:
                print("\n   MCP 工具详情:")
                for tool in mcp_tools:
                    print(f"     - {tool}")
            
            # Check for F6 issue
            if not update_context_tools and not shared_context_tools:
                self.log(
                    "F6-Check",
                    "❌ 未找到 update_context 或 shared-context 工具",
                    {
                        "hint": "需要在 tool_filter.py 的 get_allowed_tools() 中添加",
                        "expected_pattern": "mcp__docuswarm-shared-context-{node_id}__update_context"
                    },
                    "error"
                )
            else:
                self.log(
                    "F6-Check",
                    "✅ 找到 shared context 相关工具",
                    {"tools": update_context_tools + shared_context_tools},
                    "success"
                )
            
            return allowed_tools
            
        except Exception as e:
            self.log("AllowedTools", f"生成工具列表失败: {e}", {}, "error")
            raise
    
    def trace_mcp_servers(self, filter_obj):
        """Trace step 4: MCP server creation."""
        print("\n" + "="*60)
        print("📋 步骤 4: 创建 MCP Servers")
        print("="*60)
        
        try:
            servers = filter_obj.create_mcp_servers()
            
            self.log(
                "MCPServers",
                f"创建了 {len(servers)} 个 MCP server",
                {"server_names": list(servers.keys())},
                "success"
            )
            
            # Check for shared context server
            shared_context_servers = [
                name for name in servers.keys()
                if "shared" in name.lower() or "context" in name.lower()
            ]
            
            if not shared_context_servers:
                self.log(
                    "F6-Check",
                    "❌ 未创建 shared-context MCP server",
                    {
                        "hint": "需要在 tool_filter.py 的 create_mcp_servers() 中添加",
                        "expected_name_pattern": "docuswarm-shared-context-{node_id}"
                    },
                    "error"
                )
            else:
                self.log(
                    "F6-Check",
                    "✅ 找到 shared-context MCP server",
                    {"servers": shared_context_servers},
                    "success"
                )
            
            # Detail each server
            for name, server in servers.items():
                tools = []
                if isinstance(server, dict):
                    tools = server.get("tools", [])
                
                self.log(
                    "ServerDetail",
                    f"Server: {name}",
                    {
                        "tools_count": len(tools) if tools else "unknown",
                        "has_tools_attr": "tools" in str(server),
                    }
                )
            
            return servers
            
        except Exception as e:
            self.log("MCPServers", f"创建 MCP servers 失败: {e}", {}, "error")
            raise
    
    def trace_session_manager_creation(self, config, allowed_tools):
        """Trace step 5: SessionManager creation."""
        print("\n" + "="*60)
        print("📋 步骤 5: 创建 SessionManager")
        print("="*60)
        
        try:
            from autoBMAD.docuswarm.llm.session_manager import SessionManager
            
            # Get paths
            output_dir = project_root / "output" / self.pipeline_id
            
            session_manager = SessionManager(
                cwd=project_root,
                output_dir=output_dir,
                node_id=self.node_id,
                tool_permissions=config.tool_permissions,
            )
            
            self.log(
                "SessionManager",
                "SessionManager 创建成功",
                {
                    "cwd": str(session_manager.cwd),
                    "output_dir": str(session_manager.output_dir),
                    "node_id": session_manager.node_id,
                },
                "success"
            )
            
            # Check _build_allowed_tools
            built_tools = session_manager._build_allowed_tools()
            
            self.log(
                "SessionManager",
                f"_build_allowed_tools() 返回 {len(built_tools)} 个工具",
                {
                    "tools_sample": built_tools[:10] if len(built_tools) > 10 else built_tools,
                    "has_skill_tool": "Skill" in built_tools,
                }
            )
            
            return session_manager
            
        except Exception as e:
            self.log("SessionManager", f"创建 SessionManager 失败: {e}", {}, "error")
            raise
    
    def generate_report(self):
        """Generate final trace report."""
        print("\n" + "="*60)
        print("📊 运行时链路追踪报告")
        print("="*60)
        
        errors = [log for log in self.trace_logs if log["status"] == "error"]
        warnings = [log for log in self.trace_logs if log["status"] == "warning"]
        
        print(f"\n追踪阶段数: {len(self.trace_logs)}")
        print(f"错误数: {len(errors)}")
        print(f"警告数: {len(warnings)}")
        
        if errors:
            print("\n❌ 发现的关键问题:")
            for err in errors:
                print(f"   [{err['stage']}] {err['message']}")
        
        # F6 specific diagnosis
        print("\n🔍 F6 问题诊断:")
        f6_issues = [e for e in errors if e['stage'].startswith('F6')]
        if f6_issues:
            print("   ❌ update_context 工具未进入 MCP 运行时链路")
            print("   修复建议:")
            print("   1. 在 tool_filter.py:create_mcp_servers() 中添加 update_context server 创建")
            print("   2. 在 tool_filter.py:get_allowed_tools() 中添加 update_context 工具名")
            print("   3. 新建 update_context_sdk.py 实现 create_update_context_server()")
        else:
            print("   ✅ update_context MCP 链路完整")
        
        return len(errors) == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="运行时链路追踪工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tools/debug/trace_runtime_chain.py --node analyst
    python tools/debug/trace_runtime_chain.py --node analyst --pipeline test-001
        """
    )
    
    parser.add_argument(
        "--node", "-n",
        default="analyst",
        help="节点 ID (默认: analyst)"
    )
    parser.add_argument(
        "--pipeline", "-p",
        default="debug-pipeline",
        help="Pipeline ID (默认: debug-pipeline)"
    )
    
    args = parser.parse_args()
    
    print("🔧 运行时链路追踪工具")
    print("=" * 60)
    print(f"目标节点: {args.node}")
    print(f"Pipeline: {args.pipeline}")
    
    tracer = RuntimeChainTracer(args.node, args.pipeline)
    
    try:
        # Run trace steps
        config = tracer.trace_node_config_loading()
        filter_obj = tracer.trace_tool_filter_creation(config)
        allowed_tools = tracer.trace_allowed_tools(filter_obj)
        servers = tracer.trace_mcp_servers(filter_obj)
        session_manager = tracer.trace_session_manager_creation(config, allowed_tools)
        
        # Generate report
        success = tracer.generate_report()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ 追踪失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
F2: update_context MCP Server [ICON]

[ICON]update_context [ICON] allowed_tools[ICON] MCP server

[ICON]
- NodeToolFilter.get_allowed_tools() [ICON] shared_context.enabled == true[ICON]
  [ICON] update_context [ICON] allowed_tools
- [ICON] NodeToolFilter.create_mcp_servers() [ICON] pipeline_id [ICON] shared-context server
- SessionManager._create_options() [ICON] node_filter.create_mcp_servers() [ICON] pipeline_id
- IndependentAgent._create_pipeline_session_manager() [ICON] pipeline_id [ICON] SessionManager

[ICON]:
    python tools/docuswarm_f2_update_context_debugger.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.docuswarm.context.permissions import (
    NodeFilePermissions,
    NodeSearchPermissions,
    NodeToolPermissions,
)
from autoBMAD.nodes.loader import NodeSharedContextConfig
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter


def test_tool_filter_without_pipeline_id():
    """[ICON] pipeline_id [ICON] MCP server [ICON]."""
    print("=" * 80)
    print("F2 update_context MCP Server [ICON]")
    print("=" * 80)
    
    # [ICON] shared_context [ICON] ToolFilter
    tool_permissions = NodeToolPermissions(
        file_permissions=NodeFilePermissions(allowed_read_dirs=["docs/"]),
        search_permissions=NodeSearchPermissions(search_dirs=["docs/"]),
        shared_context=NodeSharedContextConfig(
            enabled=True,
            operations=["set", "append", "remove"],
        ),
    )
    
    node_filter = NodeToolFilter(
        node_id="analyst",
        tool_permissions=tool_permissions,
        output_dir="output/pipe-123/analyst",
    )
    
    print("\n[ICON] [ICON]:")
    print(f"  - node_id: analyst")
    print(f"  - shared_context.enabled: True")
    print(f"  - shared_context.operations: ['set', 'append', 'remove']")
    
    # [ICON] get_allowed_tools()
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 1: NodeToolFilter.get_allowed_tools()")
    print("-" * 60)
    
    allowed_tools = node_filter.get_allowed_tools()
    update_context_tools = [t for t in allowed_tools if "update_context" in t]
    
    print(f"\n[ICON]: {len(allowed_tools)}")
    print(f"update_context [ICON]: {update_context_tools}")
    
    has_update_context_in_allowed = len(update_context_tools) > 0
    print(f"\n[ICON]: update_context {'[ICON] [OK]' if has_update_context_in_allowed else '[ICON] [FAIL]'} allowed_tools")
    
    # [ICON] create_mcp_servers() [ICON] pipeline_id
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 2: create_mcp_servers() [ICON] pipeline_id")
    print("-" * 60)
    
    servers_no_pipeline = node_filter.create_mcp_servers()
    server_names_no_pipeline = list(servers_no_pipeline.keys())
    
    print(f"\n[ICON] servers: {server_names_no_pipeline}")
    has_shared_context_server_no_pipeline = any(
        "shared-context" in name for name in server_names_no_pipeline
    )
    print(f"shared-context server: {'[ICON] [OK]' if has_shared_context_server_no_pipeline else '[ICON] [FAIL]'}\n")
    
    # [ICON] create_mcp_servers() [ICON] pipeline_id
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 3: create_mcp_servers(pipeline_id='pipe-123')")
    print("-" * 60)
    
    servers_with_pipeline = node_filter.create_mcp_servers(pipeline_id="pipe-123")
    server_names_with_pipeline = list(servers_with_pipeline.keys())
    
    print(f"\n[ICON] servers: {server_names_with_pipeline}")
    has_shared_context_server_with_pipeline = any(
        "shared-context" in name for name in server_names_with_pipeline
    )
    print(f"shared-context server: {'[ICON] [OK]' if has_shared_context_server_with_pipeline else '[ICON] [FAIL]'}\n")
    
    return {
        "has_update_context_in_allowed": has_update_context_in_allowed,
        "has_shared_context_server_no_pipeline": has_shared_context_server_no_pipeline,
        "has_shared_context_server_with_pipeline": has_shared_context_server_with_pipeline,
        "allowed_tools_count": len(allowed_tools),
        "servers_without_pipeline": server_names_no_pipeline,
        "servers_with_pipeline": server_names_with_pipeline,
    }


def analyze_session_manager_calls():
    """[ICON] SessionManager [ICON]."""
    print("\n" + "=" * 80)
    print("F2 SessionManager [ICON]")
    print("=" * 80)
    
    # [ICON]
    session_manager_file = project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    independent_agent_file = project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    
    print("""
[ICON]:

1. SessionManager._create_options() (session_manager.py:303-305)
   ```python
   mcp_servers = node_filter.create_mcp_servers()  # [ICON] [ICON] pipeline_id
   ```

2. IndependentAgent._create_pipeline_session_manager() (independent.py:1072-1080)
   ```python
   return SessionManager(
       work_dir=work_dir,
       agent_file=self._agent_file,
       config=...,
       node_id=node_id,
       file_dirs=file_dirs,
       search_dirs=search_dirs,
       tool_permissions=tool_permissions,
       # [ICON] [ICON] pipeline_id [ICON]
   )
   ```

3. IndependentAgent.execute() [ICON]:
   - execute() [ICON] pipeline_id ([ICON] context)
   - [ICON] _create_pipeline_session_manager() [ICON] pipeline_id
   - SessionManager.__init__() [ICON] pipeline_id [ICON]

[ICON]:
- pipeline_id [ICON] (PipelineState, NodeExecutionContext)
- [ICON] SessionManager [ICON] NodeToolFilter [ICON] pipeline_id
- [ICON] create_mcp_servers() [ICON] pipeline_id[ICON] update_context server

[ICON]:

[ICON] A: [ICON] pipeline_id
   1. SessionManager.__init__() [ICON] pipeline_id [ICON]
   2. IndependentAgent._create_pipeline_session_manager() [ICON] pipeline_id
   3. SessionManager._create_options() [ICON] self._pipeline_id

[ICON] B: [ICON] shared-context server
   1. [ICON] NodeToolFilter.create_mcp_servers() [ICON]
   2. [ICON] create_shared_context_server(pipeline_id) [ICON]
   3. [ICON] MCP server

[ICON] C: [ICON] server [ICON]
   1. [ICON] PipelineAdapter [ICON] NodeExecutionExecutor [ICON] MCP servers
   2. [ICON] pipeline_id [ICON]
""")


def check_code_paths():
    """[ICON]."""
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    session_manager_file = project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    
    with open(session_manager_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # [ICON] create_mcp_servers [ICON]
    if "node_filter.create_mcp_servers()" in content:
        print("[ICON] [ICON]: node_filter.create_mcp_servers() [ICON] pipeline_id [ICON]")
    elif "node_filter.create_mcp_servers(pipeline_id" in content:
        print("[ICON] [ICON]: node_filter.create_mcp_servers() [ICON] pipeline_id [ICON]")
    else:
        print("? [ICON] create_mcp_servers [ICON]")
    
    # [ICON] create_options [ICON]
    if "def _create_options" in content:
        print("[ICON] [ICON]: _create_options [ICON]")
        if "pipeline_id" in content.split("def _create_options")[1].split("def ")[0]:
            print("  - _create_options [ICON] pipeline_id [ICON]")
        else:
            print("  - _create_options [ICON] pipeline_id [ICON]")


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F2 update_context MCP Server [ICON]\n")
    
    results = test_tool_filter_without_pipeline_id()
    analyze_session_manager_calls()
    check_code_paths()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F2 [ICON]")
    print("=" * 80)
    print(f"""
[ICON]:
- update_context [ICON] allowed_tools [ICON]: {'[ICON] [ICON]' if results['has_update_context_in_allowed'] else '[ICON] [ICON]'}
- [ICON] pipeline_id [ICON] shared-context server: {'[ICON] [ICON]' if results['has_shared_context_server_no_pipeline'] else '[ICON] [ICON]'}
- [ICON] pipeline_id [ICON] shared-context server: {'[ICON] [ICON]' if results['has_shared_context_server_with_pipeline'] else '[ICON] [ICON]'}

[ICON] Servers ([ICON] pipeline_id):
  {results['servers_without_pipeline']}

[ICON] Servers ([ICON] pipeline_id):
  {results['servers_with_pipeline']}

[ICON]:
{"[ICON] [ICON] - update_context [ICON] allowed_tools[ICON] MCP server" 
if results['has_update_context_in_allowed'] and not results['has_shared_context_server_no_pipeline'] else 
"[ICON] [ICON]"}

[ICON]:
- [ICON]Agent [ICON] update_context [ICON] runtime [ICON] server
- 05-shared-context-update-mechanism.md [ICON]"[ICON] MCP [ICON]"[ICON]
- 04-tool-permissions-configuration.md [ICON] shared-context [ICON]

[ICON]: HIGH
""")
    
    is_ok = results['has_update_context_in_allowed'] == results['has_shared_context_server_no_pipeline']
    return 0 if is_ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""
F5: shared_context.allowed_keys [ICON]

[ICON]shared_context.allowed_keys [ICON] UpdateContextTool

[ICON]
- NodeLoader [ICON] tools.shared_context.allowed_keys
- UpdateContextTool [ICON] allowed_keys
- [ICON] NodeToolFilter.create_mcp_servers() [ICON] allowed_operations [ICON] create_update_context_server()
- create_update_context_server() [ICON] pipeline_id [ICON] allowed_operations [ICON] UpdateContextTool

[ICON]:
    python tools/docuswarm_f5_allowed_keys_debugger.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.docuswarm.context.permissions import NodeToolPermissions
from autoBMAD.nodes.loader import NodeSharedContextConfig
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server


def test_allowed_keys_propagation():
    """[ICON] allowed_keys [ICON]."""
    print("=" * 80)
    print("F5 shared_context.allowed_keys [ICON]")
    print("=" * 80)
    
    # [ICON] UpdateContextTool [ICON] allowed_keys
    print("\n[ICON] [ICON] 1: UpdateContextTool [ICON]")
    print("-" * 60)
    
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    
    # [ICON] allowed_keys [ICON] tool
    custom_keys = ["custom.facts.*", "custom.decisions.*"]
    tool_with_keys = UpdateContextTool(
        state_manager=StateManager(),
        pipeline_id="pipe-test",
        allowed_keys=custom_keys,
    )
    
    # [ICON] whitelist [ICON]
    effective_whitelist = tool_with_keys._build_effective_whitelist()
    
    print(f"\n[ICON] allowed_keys: {custom_keys}")
    print(f"Effective whitelist: {effective_whitelist}")
    
    # [ICON] key [ICON]
    has_custom_keys = all(
        any(k.startswith(ck.replace("*", "")) for k in effective_whitelist)
        for ck in custom_keys
    )
    
    print(f"\n[ICON] key [ICON]: {'[OK] [ICON]' if has_custom_keys else '[FAIL] [ICON]'}")
    print(f"Whitelist [ICON]: {tool_with_keys._whitelist_source}")
    
    # [ICON] create_update_context_server [ICON] allowed_keys
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 2: create_update_context_server [ICON]")
    print("-" * 60)
    
    import inspect
    
    sig = inspect.signature(create_update_context_server)
    params = list(sig.parameters.keys())
    
    print(f"\ncreate_update_context_server [ICON]: {params}")
    has_allowed_keys_param = "allowed_keys" in params
    print(f"[ICON] allowed_keys [ICON]: {'[OK] [ICON]' if has_allowed_keys_param else '[FAIL] [ICON]'}")
    
    # [ICON] NodeToolFilter [ICON] allowed_keys
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 3: NodeToolFilter.create_mcp_servers() [ICON]")
    print("-" * 60)
    
    tool_permissions = NodeToolPermissions(
        shared_context=NodeSharedContextConfig(
            enabled=True,
            operations=["set", "append"],
            allowed_keys=["node.specific.*", "facts.custom.*"],  # [ICON]
        ),
    )
    
    node_filter = NodeToolFilter(
        node_id="test-node",
        tool_permissions=tool_permissions,
    )
    
    print(f"\n[ICON] allowed_keys: {tool_permissions.shared_context.allowed_keys}")
    
    # [ICON] create_mcp_servers [ICON] allowed_keys
    tool_filter_file = project_root / "autoBMAD" / "docuswarm" / "llm" / "tool_filter.py"
    with open(tool_filter_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # [ICON] create_update_context_server [ICON]
    if "create_update_context_server(" in content:
        # [ICON]
        call_section = content.split("create_update_context_server(")[1].split(")")[0]
        print(f"\ncreate_update_context_server [ICON]:\n  create_update_context_server({call_section})")
        
        passes_allowed_keys = "allowed_keys" in call_section
        print(f"\n[ICON] allowed_keys: {'[ICON] [ICON]' if passes_allowed_keys else '[ICON] [ICON]'}")
    else:
        print("\n[ICON] create_update_context_server [ICON]")
        passes_allowed_keys = False
    
    return {
        "tool_supports_allowed_keys": True,
        "server_has_allowed_keys_param": has_allowed_keys_param,
        "filter_passes_allowed_keys": passes_allowed_keys,
        "effective_whitelist": effective_whitelist,
    }


def analyze_allowed_keys_flow():
    """[ICON] allowed_keys [ICON]."""
    print("\n" + "=" * 80)
    print("F5 allowed_keys [ICON]")
    print("=" * 80)
    
    print("""
[ICON]:

1. node.yaml [ICON] (e.g., analyst/node.yaml:102-104)
   ```yaml
   shared_context:
     enabled: true
     operations: ["set", "append", "remove"]
     allowed_keys:
       - "facts.*"
       - "decisions.*"
   ```

2. NodeLoader [ICON] (nodes/loader.py:152-166, 488-520)
   - [ICON] tools.shared_context.allowed_keys
   - [ICON] NodeSharedContextPermissions.allowed_keys

3. NodeToolFilter [ICON] (llm/tool_filter.py:259-266)
   ```python
   update_server = create_update_context_server(
       pipeline_id=pipeline_id,
       node_id=self.node_id,
       allowed_operations=self.tool_permissions.shared_context.operations,
       # [ICON] [ICON] allowed_keys!
   )
   ```

4. create_update_context_server (tools/update_context_sdk.py:19-23, 91-95)
   ```python
   def create_update_context_server(
       pipeline_id: str,
       node_id: str,
       allowed_operations: list[str] | None = None,
       # [ICON] [ICON] allowed_keys [ICON]!
   ):
       tool = UpdateContextTool(
           state_manager=StateManager(),
           pipeline_id=pipeline_id,
           # [ICON] [ICON] allowed_keys!
       )
   ```

5. UpdateContextTool [ICON] (tools/update_context.py:70-126)
   ```python
   def __init__(
       self,
       state_manager: StateManager | None = None,
       pipeline_id: str | None = None,
       allowed_keys: list[str] | None = None,  # [ICON] [ICON] allowed_keys
   ):
       self._node_allowed_keys = allowed_keys
   ```

[ICON]:
- UpdateContextTool [ICON] allowed_keys
- [ICON] create_update_context_server [ICON] allowed_keys [ICON]
- NodeToolFilter [ICON] allowed_keys
- [ICON]: [ICON] allowed_keys [ICON]

[ICON]:

[ICON] A: [ICON] allowed_keys [ICON]
   1. create_update_context_server [ICON] allowed_keys [ICON]
   2. NodeToolFilter.create_mcp_servers() [ICON] allowed_keys
   3. [ICON] UpdateContextTool [ICON]

[ICON] B: [ICON]
   1. [ICON] NodeToolPermissions [ICON]
   2. UpdateContextTool [ICON] NodeToolPermissions [ICON]
   3. [ICON]
""")


def check_node_yaml_configs():
    """[ICON] YAML [ICON] allowed_keys [ICON]."""
    print("\n" + "-" * 60)
    print("[ICON] [ICON] allowed_keys [ICON]")
    print("-" * 60)
    
    nodes_dir = project_root / "autoBMAD" / "nodes"
    
    configs_with_allowed_keys = []
    
    for node_dir in nodes_dir.iterdir():
        if node_dir.is_dir():
            node_yaml = node_dir / "node.yaml"
            if node_yaml.exists():
                with open(node_yaml, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                
                tools_config = data.get("tools", {})
                shared_context = tools_config.get("shared_context", {})
                allowed_keys = shared_context.get("allowed_keys")
                
                if allowed_keys:
                    configs_with_allowed_keys.append({
                        "node_id": data.get("node_id", node_dir.name),
                        "allowed_keys": allowed_keys,
                    })
    
    print(f"\n[ICON] {len(configs_with_allowed_keys)} [ICON] allowed_keys:")
    for config in configs_with_allowed_keys:
        print(f"  - {config['node_id']}: {config['allowed_keys']}")
    
    if not configs_with_allowed_keys:
        print("\n  [ICON] allowed_keys[ICON]")
    
    return configs_with_allowed_keys


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F5 shared_context.allowed_keys [ICON]\n")
    
    results = test_allowed_keys_propagation()
    analyze_allowed_keys_flow()
    configs = check_node_yaml_configs()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F5 [ICON]")
    print("=" * 80)
    print(f"""
[ICON]:
- UpdateContextTool [ICON] allowed_keys: {'[ICON] [ICON]' if results['tool_supports_allowed_keys'] else '[ICON] [ICON]'}
- create_update_context_server [ICON] allowed_keys [ICON]: {'[ICON] [ICON]' if results['server_has_allowed_keys_param'] else '[ICON] [ICON]'}
- NodeToolFilter [ICON] allowed_keys: {'[ICON] [ICON]' if results['filter_passes_allowed_keys'] else '[ICON] [ICON]'}
- [ICON] allowed_keys [ICON]: {len(configs)}

[ICON]:
{"[ICON] [ICON] - UpdateContextTool [ICON] allowed_keys[ICON]"
if results['tool_supports_allowed_keys'] and not results['filter_passes_allowed_keys'] else 
"[ICON] allowed_keys [ICON]" if results['filter_passes_allowed_keys'] else 
"[ICON] [ICON] allowed_keys"}

[ICON]:
- 05-shared-context-update-mechanism.md [ICON]"[ICON]"[ICON]
- [ICON]
- [ICON]

[ICON]: MEDIUM
""")
    
    is_ok = results['tool_supports_allowed_keys'] and results['filter_passes_allowed_keys']
    return 0 if is_ok else 1


if __name__ == "__main__":
    sys.exit(main())

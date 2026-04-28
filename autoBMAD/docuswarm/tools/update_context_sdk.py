"""SDK MCP 格式的 update_context 工具实现.

F6 Fix: 将 update_context 工具暴露为 MCP SDK server，
使 Agent 能够在运行时调用 update_context 更新共享上下文。
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from claude_agent_sdk import McpSdkServerConfig

logger = logging.getLogger(__name__)


def create_update_context_server(
    pipeline_id: str,
    node_id: str,
    allowed_operations: list[str] | None = None,
    allowed_keys: list[str] | None = None,  # F5 Fix: 添加 allowed_keys 参数
) -> dict[str, Any]:
    """Create an SDK MCP server for update_context tool.

    F5 Fix: 添加 allowed_keys 参数支持节点级白名单

    This factory function creates an SDK MCP server configured with the
    update_context tool, scoped to the specified pipeline.

    Args:
        pipeline_id: Pipeline ID for context updates.
        node_id: Unique identifier for the node. Used in server naming.
        allowed_operations: List of allowed operations (set, append, remove).
            Defaults to ["set", "append", "remove"].
        allowed_keys: Optional list of node-specific allowed key patterns.
            These are merged with the global whitelist.

    Returns:
        Dict with MCP SDK server configuration including name, transport, and server.

    Raises:
        ValueError: If pipeline_id or node_id is not provided.
        RuntimeError: If claude_agent_sdk is not installed.
    """
    if not pipeline_id:
        raise ValueError("pipeline_id is required")

    if not node_id:
        raise ValueError("node_id is required")

    try:
        from claude_agent_sdk import create_sdk_mcp_server, tool
    except ImportError as e:
        raise RuntimeError(
            "claude_agent_sdk is required for create_update_context_server. "
            "Install with: pip install claude-agent-sdk"
        ) from e

    # Default operations if not specified
    operations = allowed_operations or ["set", "append", "remove"]
    server_name = f"docuswarm-shared-context-{node_id}"

    @tool(
        "update_context",
        "Update shared context with key-value operations. "
        "Supports set (replace), append (add to list), and remove (delete key) operations. "
        "Keys must match allowed whitelist patterns.",
        {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Context key to update (supports dot notation like 'facts.market_scope')",
                },
                "value": {
                    "type": ["string", "number", "boolean", "array", "object"],
                    "description": "Value to set, append, or remove",
                },
                "operation": {
                    "type": "string",
                    "enum": operations,
                    "default": "set",
                    "description": "Operation to perform: 'set' replaces value, 'append' adds to list, 'remove' deletes key",
                },
            },
            "required": ["key", "value"],
        },
    )
    async def update_context_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool handler for update_context."""
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool

        try:
            # F5 Fix: 传递 allowed_keys 到 UpdateContextTool
            tool = UpdateContextTool(
                state_manager=StateManager(),
                pipeline_id=pipeline_id,
                allowed_keys=allowed_keys,
            )

            # Execute the tool
            from autoBMAD.docuswarm.tools.update_context import UpdateContextParams

            params = UpdateContextParams(
                key=args["key"],
                value=args["value"],
                operation=args.get("operation", "set"),
            )

            result = await tool._execute(params)

            if result.success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.result, ensure_ascii=False),
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"error": result.error}, ensure_ascii=False
                            ),
                        }
                    ],
                    "isError": True,
                }

        except Exception as e:
            logger.error(f"update_context tool error: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"error": f"Tool execution failed: {str(e)}"},
                            ensure_ascii=False,
                        ),
                    }
                ],
                "isError": True,
            }

    logger.info(
        f"Created SDK MCP update_context server for node '{node_id}' "
        f"with pipeline_id: {pipeline_id}, operations: {operations}"
    )

    server = create_sdk_mcp_server(
        name=server_name,
        version="1.0.0",
        tools=[update_context_tool],
    )

    return {
        "name": server_name,
        "transport": "sdk",
        "server": server,
    }


__all__ = [
    "create_update_context_server",
]

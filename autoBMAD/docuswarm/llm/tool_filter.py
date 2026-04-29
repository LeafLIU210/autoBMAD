"""Tool Filter for Node Tool Permissions.

This module provides the NodeToolFilter class which manages tool permissions
for nodes, including creating MCP servers and generating allowed tool lists.

Example:
    >>> from autoBMAD.nodes.loader import NodeLoader
    >>> from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
    >>>
    >>> config = NodeLoader.load("analyst")
    >>> filter_obj = NodeToolFilter.from_node_config(config)
    >>> allowed_tools = filter_obj.get_allowed_tools()
    >>> mcp_servers = filter_obj.create_mcp_servers()

Attributes:
    MCP_TOOL_NAME_FORMAT: Format string for MCP tool names.
    FILE_SERVER_NAME_FORMAT: Format string for file MCP server names.
    SEARCH_SERVER_NAME_FORMAT: Format string for search MCP server names.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from autoBMAD.docuswarm.tools.create_deliverable_sdk import create_deliverable_server
from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server

if TYPE_CHECKING:
    from autoBMAD.nodes.loader import NodeConfig, NodeToolPermissions

logger = logging.getLogger(__name__)

# MCP naming conventions
MCP_TOOL_NAME_FORMAT = "mcp__docuswarm-{type}-{node_id}__{tool_name}"
FILE_SERVER_NAME_FORMAT = "docuswarm-files-{node_id}"
SEARCH_SERVER_NAME_FORMAT = "docuswarm-search-{node_id}"
DELIVERABLE_SERVER_NAME_FORMAT = "docuswarm-deliverable-{node_id}"
SHARED_CONTEXT_SERVER_NAME_FORMAT = "docuswarm-shared-context-{node_id}"


class NodeToolFilter:
    """Manages tool permissions and MCP server creation for nodes.

    This class provides a unified interface for:
    - Determining which tools a node is allowed to use
    - Creating MCP servers with appropriate permissions
    - Generating tool names following naming conventions

    Attributes:
        node_id: Unique identifier for the node.
        tool_permissions: Tool permissions configuration.

    Example:
        >>> filter_obj = NodeToolFilter.from_node_config(node_config)
        >>> tools = filter_obj.get_allowed_tools()
        >>> print(tools)
        ['mcp__docuswarm-files-analyst__read_document', ...]
    """

    def __init__(
        self,
        node_id: str,
        tool_permissions: NodeToolPermissions | None = None,
        output_dir: str | None = None,
        db_path: str | None = None,  # H1 Fix: pass configured DB path
    ) -> None:
        """Initialize NodeToolFilter.

        Args:
            node_id: Unique identifier for the node.
            tool_permissions: Tool permissions configuration.
                                     Defaults to empty permissions if None.
            output_dir: Output directory for deliverable files.
                       If set, a deliverable MCP server will be created.
            db_path: Optional database path for shared_context MCP server.
        """
        from autoBMAD.nodes.loader import NodeToolPermissions

        self.node_id = node_id
        self.tool_permissions = tool_permissions or NodeToolPermissions()
        self.output_dir = output_dir
        self.db_path = db_path

    @classmethod
    def from_node_config(cls, config: NodeConfig) -> NodeToolFilter:
        """Create a NodeToolFilter from a NodeConfig.

        Args:
            config: The node configuration containing tool permissions.

        Returns:
            Configured NodeToolFilter instance.

        Example:
            >>> config = NodeLoader.load("analyst")
            >>> filter_obj = NodeToolFilter.from_node_config(config)
        """
        return cls(
            node_id=config.node_id,
            tool_permissions=config.tool_permissions,
        )

    def get_allowed_tools(self) -> list[str]:
        """Get the list of allowed tool names for this node.

        This method generates the complete list of tool names that the node
        is permitted to use, including:
        - Builtin tools (e.g., "Read", "Glob")
        - MCP file tools (read_document, list_documents)
        - MCP search tools (grep_search, glob_search)

        Returns:
            List of allowed tool names. Returns empty list if no permissions
            are configured.

        Example:
            >>> filter_obj = NodeToolFilter(node_id="analyst", tool_permissions=perms)
            >>> tools = filter_obj.get_allowed_tools()
            >>> print(tools)
            ['Read', 'mcp__docuswarm-files-analyst__read_document', ...]
        """
        tools: list[str] = []

        # Add builtin tools
        tools.extend(self.tool_permissions.allowed_builtin_tools)

        # Add MCP file tools if file permissions are configured
        file_dirs = self.tool_permissions.file_permissions.allowed_read_dirs
        if file_dirs:
            tools.extend(
                [
                    MCP_TOOL_NAME_FORMAT.format(
                        type="files", node_id=self.node_id, tool_name="read_document"
                    ),
                    MCP_TOOL_NAME_FORMAT.format(
                        type="files", node_id=self.node_id, tool_name="list_documents"
                    ),
                ]
            )

        # Add MCP search tools if search permissions are configured
        search_dirs = self.tool_permissions.search_permissions.search_dirs
        if search_dirs:
            tools.extend(
                [
                    MCP_TOOL_NAME_FORMAT.format(
                        type="search", node_id=self.node_id, tool_name="grep_search"
                    ),
                    MCP_TOOL_NAME_FORMAT.format(
                        type="search", node_id=self.node_id, tool_name="glob_search"
                    ),
                ]
            )

        # TDD-07: Always add deliverable MCP tool when output_dir is configured
        # F2 Fix: Add both create_deliverable and submit_execution_report
        if self.output_dir:
            tools.append(
                MCP_TOOL_NAME_FORMAT.format(
                    type="deliverable", node_id=self.node_id, tool_name="create_deliverable"
                )
            )
            # F2 Fix: Add submit_execution_report tool for JSON/MCP closed loop
            tools.append(
                MCP_TOOL_NAME_FORMAT.format(
                    type="deliverable", node_id=self.node_id, tool_name="submit_execution_report"
                )
            )

        # F6 Fix: Add update_context tool when shared_context is enabled
        if self.tool_permissions.shared_context.enabled:
            tools.append(
                MCP_TOOL_NAME_FORMAT.format(
                    type="shared-context", node_id=self.node_id, tool_name="update_context"
                )
            )

        logger.debug(f"Node {self.node_id} has {len(tools)} allowed tools: {tools}")
        return tools

    def create_mcp_servers(
        self, pipeline_id: str | None = None, db_path: str | None = None
    ) -> dict[str, Any]:
        """Create SDK MCP servers based on configured permissions.

        This method creates and returns SDK MCP server dicts for file reading
        and search tools based on the node's permissions. The servers can be
        registered with ClaudeAgentOptions.

        Args:
            pipeline_id: Optional pipeline ID for shared context server.
                Required when shared_context is enabled.
            db_path: Optional database path for shared_context MCP server.

        Returns:
            Dict mapping server names to SDK MCP server dicts.
            Format: {server_name: sdk_mcp_server_dict}

        Raises:
            FileToolError: If file server creation fails.
            SearchToolError: If search server creation fails.

        Example:
            >>> filter_obj = NodeToolFilter.from_node_config(config)
            >>> servers = filter_obj.create_mcp_servers(pipeline_id="pipe-123")
            >>> options = ClaudeAgentOptions(mcp_servers=servers)
        """
        servers: dict[str, Any] = {}

        # Create file read server if file permissions are configured
        file_dirs = self.tool_permissions.file_permissions.allowed_read_dirs
        if file_dirs:
            try:
                file_server = create_file_read_server(
                    allowed_dirs=file_dirs,
                    node_id=self.node_id,
                )
                # SDK MCP server is a dict with 'name' key
                server_name = file_server["name"]
                servers[server_name] = file_server
                logger.info(
                    f"Created file read server for node '{self.node_id}' with dirs: {file_dirs}"
                )
            except Exception as e:
                logger.error(f"Failed to create file read server for node '{self.node_id}': {e}")
                raise

        # Create search server if search permissions are configured
        search_dirs = self.tool_permissions.search_permissions.search_dirs
        if search_dirs:
            try:
                search_server = create_search_server(
                    search_dirs=search_dirs,
                    node_id=self.node_id,
                )
                server_name = search_server["name"]
                servers[server_name] = search_server
                logger.info(
                    f"Created search server for node '{self.node_id}' with dirs: {search_dirs}"
                )
            except Exception as e:
                logger.error(f"Failed to create search server for node '{self.node_id}': {e}")
                raise

        # TDD-07: Create deliverable server when output_dir is configured
        if self.output_dir:
            try:
                deliverable_server = create_deliverable_server(
                    output_dir=self.output_dir,
                    node_id=self.node_id,
                )
                server_name = deliverable_server["name"]
                servers[server_name] = deliverable_server
                logger.info(
                    f"Created deliverable server for node '{self.node_id}' "
                    f"with output_dir: {self.output_dir}"
                )
            except Exception as e:
                logger.error(f"Failed to create deliverable server for node '{self.node_id}': {e}")
                raise

        # F6 Fix: Create update_context server when shared_context is enabled and pipeline_id is provided
        if pipeline_id and self.tool_permissions.shared_context.enabled:
            try:
                # F5 Fix: 传递 allowed_keys 到 update_context server
                # H1 Fix: 传递 db_path 避免写入默认数据库
                update_server = create_update_context_server(
                    pipeline_id=pipeline_id,
                    node_id=self.node_id,
                    allowed_operations=self.tool_permissions.shared_context.operations,
                    allowed_keys=self.tool_permissions.shared_context.allowed_keys,  # F5 Fix
                    db_path=db_path or self.db_path,  # H1 Fix
                )
                server_name = update_server["name"]
                # P0 Fix: Extract the actual SDK server config for mcp_servers
                servers[server_name] = update_server["server"]
                logger.info(
                    f"Created update_context server for node '{self.node_id}' "
                    f"with pipeline_id: {pipeline_id}"
                )
            except Exception as e:
                logger.error(f"Failed to create update_context server for node '{self.node_id}': {e}")
                raise

        return servers

    def has_file_permissions(self) -> bool:
        """Check if the node has file read permissions configured.

        Returns:
            True if allowed_read_dirs is not empty, False otherwise.
        """
        return bool(self.tool_permissions.file_permissions.allowed_read_dirs)

    def has_search_permissions(self) -> bool:
        """Check if the node has search permissions configured.

        Returns:
            True if search_dirs is not empty, False otherwise.
        """
        return bool(self.tool_permissions.search_permissions.search_dirs)

    def get_file_dirs(self) -> list[str]:
        """Get the list of allowed file read directories.

        Returns:
            List of directory paths allowed for file reading.
        """
        return list(self.tool_permissions.file_permissions.allowed_read_dirs)

    def get_search_dirs(self) -> list[str]:
        """Get the list of allowed search directories.

        Returns:
            List of directory paths allowed for searching.
        """
        return list(self.tool_permissions.search_permissions.search_dirs)


# Export public API
__all__ = [
    "NodeToolFilter",
    "MCP_TOOL_NAME_FORMAT",
    "FILE_SERVER_NAME_FORMAT",
    "SEARCH_SERVER_NAME_FORMAT",
    "DELIVERABLE_SERVER_NAME_FORMAT",
    "SHARED_CONTEXT_SERVER_NAME_FORMAT",
]

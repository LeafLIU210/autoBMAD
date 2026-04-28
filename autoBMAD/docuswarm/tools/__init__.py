"""DocuSwarm tools package.

This package contains CallableTool2-based tools for the DocuSwarm SDK.
All tools internally use ToolResult and adapt to SDK format at boundary.

P0 Single Truth: Tools return structured metadata, not full content.
SDK Boundary: ToolResult is adapted to ToolOk/ToolError via sdk_adapter.

Available Tools:
    - CreateDeliverableTool: Create node deliverable documents
    - UpdateContextTool: Update shared context with persistence
    - CreateDocumentSetTool: Create multiple related documents
    - File Tools: Secure file reading with MCP server support

Available Adapters:
    - sdk_adapter: SDK boundary adaptation (ToolResult <-> ToolOk/ToolError)
    - callable_tool_wrapper: Base class for ToolResult-based tools
"""

from autoBMAD.docuswarm.tools.callable_tool_wrapper import (
    CallableToolBase,
    ToolResultCallableTool,
)
from autoBMAD.docuswarm.tools.create_deliverable import (
    CreateDeliverableParams,
    CreateDeliverableTool,
    create_deliverable,
)
from autoBMAD.docuswarm.tools.create_document_set import (
    CreateDocumentSetParams,
    CreateDocumentSetTool,
    create_document_set,
)
from autoBMAD.docuswarm.tools.file_tools import (
    ALLOWED_EXTENSIONS,
    BLOCKED_EXTENSIONS,
    BLOCKED_PATTERNS,
    MAX_FILE_SIZE,
    PathValidator,
    create_file_read_server,
    list_documents,
    read_document,
)
from autoBMAD.docuswarm.tools.sdk_adapter import (
    adapt_result_to_metadata,
)
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
from autoBMAD.docuswarm.tools.tool_result import ToolResult
from autoBMAD.docuswarm.tools.update_context import (
    UpdateContextParams,
    UpdateContextTool,
    update_context,
)

__all__ = [
    # 核心工具类
    "CreateDeliverableTool",
    "CreateDocumentSetTool",
    "UpdateContextTool",
    # 文件工具
    "PathValidator",
    "read_document",
    "list_documents",
    "create_file_read_server",
    "MAX_FILE_SIZE",
    "ALLOWED_EXTENSIONS",
    "BLOCKED_PATTERNS",
    "BLOCKED_EXTENSIONS",
    # 参数类型
    "CreateDeliverableParams",
    "CreateDocumentSetParams",
    "UpdateContextParams",
    # 函数式API（向后兼容）
    "create_deliverable",
    "create_document_set",
    "update_context",
    # SDK适配层
    "adapt_result_to_metadata",
    # 包装器基类
    "ToolResultCallableTool",
    "CallableToolBase",
    # ToolResult类型
    "ToolResult",
    # ToolRegistry
    "ToolRegistry",
]

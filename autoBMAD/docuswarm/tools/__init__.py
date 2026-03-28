"""DocuSwarm tools package.

This package contains CallableTool2-based tools for the DocuSwarm SDK.
All tools internally use ToolResult and adapt to SDK format at boundary.

P0 Single Truth: Tools return structured metadata, not full content.
SDK Boundary: ToolResult is adapted to ToolOk/ToolError via sdk_adapter.

Available Tools:
    - CreateDeliverableTool: Create node deliverable documents
    - UpdateContextTool: Update shared context with persistence
    - CreateDocumentSetTool: Create multiple related documents

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
from autoBMAD.docuswarm.tools.sdk_adapter import (
    adapt_from_sdk,
    adapt_result_to_metadata,
    adapt_to_sdk,
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
    # 参数类型
    "CreateDeliverableParams",
    "CreateDocumentSetParams",
    "UpdateContextParams",
    # 函数式API（向后兼容）
    "create_deliverable",
    "create_document_set",
    "update_context",
    # SDK适配层
    "adapt_to_sdk",
    "adapt_from_sdk",
    "adapt_result_to_metadata",
    # 包装器基类
    "ToolResultCallableTool",
    "CallableToolBase",
    # ToolResult类型
    "ToolResult",
    # ToolRegistry
    "ToolRegistry",
]

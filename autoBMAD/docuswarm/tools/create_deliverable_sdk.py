"""SDK MCP 格式的 create_deliverable 工具实现.

TDD-07: 将 create_deliverable 从 kimi-agent-sdk Python 工具
迁移为 claude-agent-sdk MCP server 工具。

遵循 file_tools_sdk.py / search_tools_sdk.py 的相同模式。
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from autoBMAD.docuswarm.tools.tool_result import ToolResult

if TYPE_CHECKING:
    from claude_agent_sdk import McpSdkServerConfig

# Import ValidationError at module level to avoid possibly unbound variable
try:
    from jsonschema import ValidationError
except ImportError:
    ValidationError = Exception  # type: ignore[misc,assignment]

# JSON Schema for submit_execution_report tool (Story 38.3)
# F3: 更新为支持多文档格式
SUBMIT_EXECUTION_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        # 单文档格式（向后兼容）
        "deliverable": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Brief title of the deliverable",
                },
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the deliverable file",
                },
                "sha256": {
                    "type": "string",
                    "description": "SHA256 hash of the deliverable content",
                },
                "content_summary": {
                    "type": "string",
                    "description": "Brief summary of the deliverable content (optional)",
                },
            },
            "required": ["title", "file_path", "sha256"],
        },
        # F3: 多文档格式（新增）
        "deliverables": {
            "type": "array",
            "description": "Multiple deliverables (for multi-document workflows)",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title of the deliverable",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the deliverable file",
                    },
                    "sha256": {
                        "type": "string",
                        "description": "SHA256 hash of the deliverable content",
                    },
                    "content_summary": {
                        "type": "string",
                        "description": "Brief summary of the deliverable content (optional)",
                    },
                    # F3: Multi-document 元数据
                    "document_index": {
                        "type": "integer",
                        "description": "Position in multi-document set (1-based)",
                    },
                    "document_total": {
                        "type": "integer",
                        "description": "Total documents in set",
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Document type identifier (e.g., 'epic-list')",
                    },
                },
                "required": ["title", "file_path", "sha256"],
            },
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question text",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["blocking", "clarifying", "optional"],
                        "description": "Priority level: blocking (must answer), clarifying (help refine), optional (nice-to-have)",
                    },
                    "context": {
                        "type": "string",
                        "description": "Context or rationale for this question",
                    },
                },
                "required": ["question", "priority", "context"],
            },
        },
        "action": {
            "type": "string",
            "enum": ["create_deliverable"],
            "description": "Action type - currently only supports create_deliverable",
        },
    },
    # F3: 使用 oneOf 确保至少一个存在（deliverable 或 deliverables）
    "oneOf": [
        {"required": ["deliverable", "action"]},
        {"required": ["deliverables", "action"]},
    ],
}

logger = logging.getLogger(__name__)


def _slugify_filename(title: str) -> str:
    """Convert title to a valid filename slug.

    Args:
        title: The deliverable title.

    Returns:
        A slugified filename with .md extension.
    """
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md"


def _compute_sha256(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _count_words(content: str) -> int:
    """Count words in content."""
    return len(content.split())


def _extract_section_index(content: str) -> list[str]:
    """Extract section headings (##) from markdown content."""
    pattern = r"^##\s+(.+)$"
    return re.findall(pattern, content, re.MULTILINE)


def create_deliverable(
    title: str,
    content: str,
    output_dir: str,
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    """Create a deliverable file and return metadata.

    Args:
        title: Deliverable title.
        content: Deliverable content in Markdown format.
        output_dir: Directory to write the file to.
        metadata: Optional additional metadata.

    Returns:
        ToolResult with metadata on success, error on failure.
    """
    try:
        filename = _slugify_filename(title)
        dir_path = Path(output_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / filename

        # Write content to file (synchronous for MCP tool compatibility)
        file_path.write_text(content, encoding="utf-8")

        # Compute metadata
        sha256_hash = _compute_sha256(content)
        word_count = _count_words(content)
        section_index = _extract_section_index(content)

        result_metadata = {
            "title": title,
            "file_path": str(file_path),
            "sha256": sha256_hash,
            "word_count": word_count,
            "section_index": section_index,
            "content_type": "markdown",
        }

        return ToolResult(success=True, result=result_metadata)

    except Exception as exc:
        return ToolResult(success=False, error=str(exc))


def submit_execution_report(report: dict[str, Any]) -> ToolResult:
    """Submit an execution report with deliverable metadata and questions.

    Validates the report against SUBMIT_EXECUTION_REPORT_SCHEMA and returns
    a confirmation with the validated report.

    Story 38.3: IndependentAgent — submit_execution_report MCP tool

    Args:
        report: Execution report containing:
            - deliverable: {title, file_path, sha256, content_summary?}
            - questions: List of {question, priority, context} (optional)
            - action: "create_deliverable"

    Returns:
        ToolResult with status and validated report on success, error on failure.
    """
    try:
        from jsonschema import validate

        validate(instance=report, schema=SUBMIT_EXECUTION_REPORT_SCHEMA)

        return ToolResult(
            success=True,
            result={
                "status": "success",
                "report": report,
            },
        )
    except ValidationError as exc:
        return ToolResult(
            success=False,
            error=f"Schema validation failed: {exc.message} at {list(exc.path)}",
        )
    except Exception as exc:
        return ToolResult(success=False, error=str(exc))


def create_deliverable_server(
    output_dir: str,
    node_id: str,
) -> McpSdkServerConfig:
    """Create an SDK MCP deliverable server.

    This factory function creates an SDK MCP server configured with the
    create_deliverable tool, scoped to the specified output directory.

    Args:
        output_dir: Directory for output files.
        node_id: Unique identifier for the node. Used in tool naming.

    Returns:
        McpSdkServerConfig server configuration.

    Raises:
        ValueError: If output_dir or node_id is not provided.
    """
    if not node_id:
        raise ValueError("node_id is required")

    if not output_dir:
        raise ValueError("output_dir is required")

    try:
        from claude_agent_sdk import create_sdk_mcp_server, tool
    except ImportError as e:
        raise RuntimeError(
            "claude_agent_sdk is required for create_deliverable_server. "
            "Install with: pip install claude-agent-sdk"
        ) from e

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    server_name = f"docuswarm-deliverable-{node_id}"

    @tool(
        "create_deliverable",
        "Create a node deliverable document. Writes a Markdown file to the output directory "
        "and returns metadata including file_path, sha256 hash, word_count, and section_index.",
        {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Deliverable title (used for filename generation)",
                },
                "content": {
                    "type": "string",
                    "description": "Deliverable content in Markdown format",
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional additional metadata",
                    "default": {},
                },
                # F3: Multi-document 参数
                "document_index": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "1-based position in multi-document set (for multi-document workflows)",
                },
                "document_total": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Total number of documents in the set (for multi-document workflows)",
                },
                "document_type": {
                    "type": "string",
                    "description": "Document type identifier, e.g., 'epic-list', 'api-design' (for multi-document workflows)",
                },
            },
            "required": ["title", "content"],
        },
    )
    async def create_deliverable_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool handler for create_deliverable."""
        import json

        # F3: 提取 multi-document 参数
        metadata = args.get("metadata", {})
        # 将 multi-document 参数合并到 metadata
        if args.get("document_index"):
            metadata["document_index"] = args["document_index"]
        if args.get("document_total"):
            metadata["document_total"] = args["document_total"]
        if args.get("document_type"):
            metadata["document_type"] = args["document_type"]

        result = create_deliverable(
            title=args["title"],
            content=args["content"],
            output_dir=output_dir,
            metadata=metadata,
        )
        if result.success:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result.result, ensure_ascii=False),
                    }
                ]
            }
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    @tool(
        "submit_execution_report",
        "Submit an execution report with deliverable metadata and follow-up questions. "
        "Validates the report structure and returns confirmation.",
        SUBMIT_EXECUTION_REPORT_SCHEMA,
    )
    async def submit_execution_report_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool handler for submit_execution_report."""
        import json

        result = submit_execution_report(report=args)
        if result.success:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result.result, ensure_ascii=False),
                    }
                ]
            }
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    logger.info(
        f"Created SDK MCP deliverable server for node '{node_id}' " f"with output_dir: {output_dir}"
    )

    server = create_sdk_mcp_server(
        name=server_name,
        version="1.0.0",
        tools=[create_deliverable_tool, submit_execution_report_tool],
    )

    return server


__all__ = [
    "create_deliverable",
    "create_deliverable_server",
    "submit_execution_report",
    "SUBMIT_EXECUTION_REPORT_SCHEMA",
    "_slugify_filename",
    "_compute_sha256",
    "_count_words",
    "_extract_section_index",
]

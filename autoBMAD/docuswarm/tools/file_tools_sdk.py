"""SDK MCP 格式的文件工具实现

实现目标:
1. 完全兼容 claude_agent_sdk 的 @tool 装饰器
2. 返回 dict 类型的服务器配置
3. 遵循 SDK MCP 工具命名约定
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from autoBMAD.docuswarm.exceptions import FileToolError, PathNotAllowedError
from autoBMAD.docuswarm.tools.tool_result import ToolResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    from claude_agent_sdk import McpSdkServerConfig

logger = logging.getLogger(__name__)

# Maximum file size in characters
MAX_FILE_SIZE = 50000

# Allowed file extensions
ALLOWED_EXTENSIONS = frozenset(
    [".md", ".txt", ".yaml", ".yml", ".json", ".py", ".js", ".ts", ".tsx", ".jsx"]
)

# Blocked patterns (security sensitive)
BLOCKED_PATTERNS = frozenset(
    [
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    ]
)

# Blocked file extensions
BLOCKED_EXTENSIONS = frozenset(
    [
        ".db",
        ".sqlite",
        ".sqlite3",
        ".db3",
        ".s3db",
        ".sl3",
        ".key",
        ".pem",
        ".p12",
        ".pfx",
        ".crt",
        ".cer",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wav",
        ".flac",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    ]
)


class PathValidator:
    """Validates file paths against allowed directories."""

    def __init__(self, allowed_dirs: Sequence[str]) -> None:
        """Initialize PathValidator with allowed directories."""
        if not allowed_dirs:
            raise ValueError("At least one allowed directory must be provided")

        # Normalize all paths to absolute paths
        self._allowed_dirs: tuple[str, ...] = tuple(
            os.path.abspath(os.path.expanduser(d)) for d in allowed_dirs
        )

    @property
    def allowed_dirs(self) -> list[str]:
        """Get list of allowed directories."""
        return list(self._allowed_dirs)

    def validate(self, request_path: str) -> str:
        """Validate and normalize a path against allowed directories."""
        # Normalize the requested path
        abs_path = os.path.abspath(os.path.expanduser(request_path))

        # Resolve symlinks to prevent symlink attacks
        try:
            resolved_path = os.path.realpath(abs_path)
        except OSError as e:
            raise PathNotAllowedError(
                f"Cannot resolve path: {request_path}",
                requested_path=abs_path,
                allowed_dirs=self.allowed_dirs,
            ) from e

        # Check if resolved path is within any allowed directory
        for allowed_dir in self._allowed_dirs:
            # Ensure allowed_dir ends with separator for prefix matching
            allowed_prefix = allowed_dir.rstrip(os.sep) + os.sep
            resolved_prefix = resolved_path.rstrip(os.sep) + os.sep

            if resolved_prefix.startswith(allowed_prefix) or resolved_path == allowed_dir:
                # Phase 4 Fix: Secondary check with resolve().is_relative_to()
                if Path(resolved_path).resolve().is_relative_to(Path(allowed_dir).resolve()):
                    return resolved_path

        # Path is outside allowed directories
        raise PathNotAllowedError(
            f"Path not in allowed directories: {request_path}",
            requested_path=resolved_path,
            allowed_dirs=self.allowed_dirs,
        )

    def is_allowed(self, request_path: str) -> bool:
        """Check if a path is allowed without raising an exception."""
        try:
            self.validate(request_path)
            return True
        except PathNotAllowedError:
            return False


def _is_blocked_file(file_path: Path) -> tuple[bool, str | None]:
    """Check if a file should be blocked based on security rules."""
    path_str = str(file_path)
    suffix = file_path.suffix.lower()

    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern in path_str.split(os.sep):
            return True, f"Access to '{pattern}' is not allowed"

    # Check blocked extensions
    if suffix in BLOCKED_EXTENSIONS:
        return True, f"Files with extension '{suffix}' are not allowed"

    # Check if extension is in allowed list
    if suffix and suffix not in ALLOWED_EXTENSIONS:
        return True, f"Files with extension '{suffix}' are not supported"

    return False, None


def read_document(
    path: str,
    validator: PathValidator | None = None,
    max_size: int = MAX_FILE_SIZE,
) -> ToolResult:
    """Read the content of a document within allowed directories."""
    if validator is None:
        return ToolResult(success=False, error="Path validator is required")

    try:
        # Validate path
        abs_path = validator.validate(path)
        file_path = Path(abs_path)

        # Check if path is a file
        if not file_path.is_file():
            return ToolResult(success=False, error=f"Path is not a file or does not exist: {path}")

        # Check for blocked files
        is_blocked, reason = _is_blocked_file(file_path)
        if is_blocked:
            return ToolResult(success=False, error=reason or "Access to this file is not allowed")

        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with different encoding or return error
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                return ToolResult(success=False, error=f"Cannot read file (encoding error): {e}")
        except OSError as e:
            return ToolResult(success=False, error=f"Cannot read file: {e}")

        # Check size and truncate if necessary
        if len(content) > max_size:
            truncated_content = content[:max_size]
            truncated_content += "\n\n[文件已截断 - 超过50000字符限制]"
            return ToolResult(success=True, result=truncated_content)

        return ToolResult(success=True, result=content)

    except PathNotAllowedError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        logger.exception("Unexpected error reading document")
        return ToolResult(success=False, error=f"Unexpected error: {e}")


def list_documents(
    directory: str,
    recursive: bool = False,
    extensions: Sequence[str] | None = None,
    validator: PathValidator | None = None,
) -> ToolResult:
    """List all documents in an allowed directory."""
    if validator is None:
        return ToolResult(success=False, error="Path validator is required")

    try:
        # Validate path
        abs_path = validator.validate(directory)
        dir_path = Path(abs_path)

        # Check if path is a directory
        if not dir_path.is_dir():
            return ToolResult(
                success=False, error=f"Path is not a directory or does not exist: {directory}"
            )

        # Collect files
        files: list[str] = []

        if recursive:
            # Walk directory tree
            for root, dirs, filenames in os.walk(abs_path):
                # Filter out blocked directories in-place
                dirs[:] = [
                    d for d in dirs if not any(p in str(Path(root) / d) for p in BLOCKED_PATTERNS)
                ]

                for filename in filenames:
                    file_path = Path(root) / filename

                    # Check if file is blocked
                    is_blocked, _ = _is_blocked_file(file_path)
                    if is_blocked:
                        continue

                    # Check extension filter
                    if extensions:
                        suffix = file_path.suffix.lower()
                        if suffix not in [ext.lower() for ext in extensions]:
                            continue

                    files.append(str(file_path.resolve()))
        else:
            # List only immediate directory contents
            try:
                for item in dir_path.iterdir():
                    if item.is_file():
                        # Check if file is blocked
                        is_blocked, _ = _is_blocked_file(item)
                        if is_blocked:
                            continue

                        # Check extension filter
                        if extensions:
                            suffix = item.suffix.lower()
                            if suffix not in [ext.lower() for ext in extensions]:
                                continue

                        files.append(str(item.resolve()))
            except OSError as e:
                return ToolResult(success=False, error=f"Cannot list directory: {e}")

        # Sort files for consistent ordering
        files.sort()

        return ToolResult(success=True, result=files)

    except PathNotAllowedError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        logger.exception("Unexpected error listing documents")
        return ToolResult(success=False, error=f"Unexpected error: {e}")


def create_file_read_server(
    allowed_dirs: Sequence[str],
    node_id: str,
) -> McpSdkServerConfig:
    """Create an SDK MCP file reading server.

    This factory function creates an SDK MCP server configured
    with read_document and list_documents tools, scoped to the specified
    allowed directories for a specific node.

    Args:
        allowed_dirs: Sequence of directory paths that the node is allowed
                     to access. All paths will be validated.
        node_id: Unique identifier for the node. Used in tool naming.

    Returns:
        McpSdkServerConfig server configuration object with type, name, instance, and tools.

    Raises:
        ValueError: If allowed_dirs is empty or node_id is not provided.
        FileToolError: If there's an error creating the server.
    """
    if not node_id:
        raise ValueError("node_id is required")

    if not allowed_dirs:
        raise ValueError("At least one allowed directory must be provided")

    # Validate all directories exist
    valid_dirs: list[str] = []
    for d in allowed_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Allowed directory does not exist: {d}")
        valid_dirs.append(abs_path)

    if not valid_dirs:
        raise FileToolError(
            "No valid allowed directories provided", allowed_dirs=list(allowed_dirs)
        )

    try:
        # Import SDK MCP utilities
        from claude_agent_sdk import create_sdk_mcp_server, tool
    except ImportError as e:
        raise FileToolError(
            "claude_agent_sdk is required for create_file_read_server. "
            "Install with: pip install claude-agent-sdk"
        ) from e

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Server name (without mcp__ prefix)
    server_name = f"docuswarm-files-{node_id}"

    @tool(
        "read_document",
        "Read the content of a document within allowed directories",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative or absolute path to the file"}
            },
            "required": ["path"],
        },
    )
    async def read_document_tool(args: dict[str, Any]) -> dict[str, Any]:
        """读取文档工具"""
        result = read_document(args["path"], validator=validator)
        if result.success:
            return {"content": [{"type": "text", "text": str(result.result)}]}
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    @tool(
        "list_documents",
        "List all documents in an allowed directory",
        {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to list"},
                "recursive": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include subdirectories",
                },
            },
            "required": ["directory"],
        },
    )
    async def list_documents_tool(args: dict[str, Any]) -> dict[str, Any]:
        """列出文档工具"""
        recursive = args.get("recursive", False)
        result = list_documents(args["directory"], recursive=recursive, validator=validator)
        if result.success:
            files_str = "\n".join(result.result) if result.result else "No files found"
            return {"content": [{"type": "text", "text": files_str}]}
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    logger.info(f"Created SDK MCP file server for node '{node_id}' with dirs: {valid_dirs}")

    return create_sdk_mcp_server(
        name=server_name, version="1.0.0", tools=[read_document_tool, list_documents_tool]
    )


# Export public API
__all__ = [
    "MAX_FILE_SIZE",
    "ALLOWED_EXTENSIONS",
    "BLOCKED_PATTERNS",
    "BLOCKED_EXTENSIONS",
    "PathValidator",
    "read_document",
    "list_documents",
    "create_file_read_server",
]

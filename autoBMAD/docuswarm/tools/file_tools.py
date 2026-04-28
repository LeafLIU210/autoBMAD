"""File reading MCP tools for DocuSwarm.

This module provides secure file reading capabilities through MCP (Model Context Protocol)
tools. It implements path validation, file size limits, and access control to ensure
safe document access within allowed directories.

Example:
    >>> from autoBMAD.docuswarm.tools.file_tools import create_file_read_server
    >>> server = create_file_read_server(["/docs", "/docs/research"], "analyst")
    >>> # Server can be registered with ClaudeAgentOptions

Attributes:
    MAX_FILE_SIZE: Maximum allowed file size in characters (50,000).
    ALLOWED_EXTENSIONS: Set of allowed file extensions for reading.
    BLOCKED_PATTERNS: Patterns that are blocked from file access.
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
    """Validates file paths against allowed directories.

    This class provides secure path validation to prevent path traversal attacks
    and ensure files can only be accessed within whitelisted directories.

    Attributes:
        allowed_dirs: List of absolute paths to allowed directories.

    Example:
        >>> validator = PathValidator(["/docs", "/docs/research"])
        >>> validator.validate("/docs/file.txt")  # Returns absolute path
        '/docs/file.txt'
        >>> validator.validate("/etc/passwd")  # Raises PathNotAllowedError
    """

    def __init__(self, allowed_dirs: Sequence[str]) -> None:
        """Initialize PathValidator with allowed directories.

        Args:
            allowed_dirs: Sequence of directory paths that are allowed for access.
                         Paths will be normalized to absolute paths.

        Raises:
            ValueError: If allowed_dirs is empty.
        """
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
        """Validate and normalize a path against allowed directories.

        Args:
            request_path: The requested file or directory path.
                         Can be relative or absolute.

        Returns:
            Absolute path if validation succeeds.

        Raises:
            PathNotAllowedError: If the path is outside all allowed directories.
        """
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
                return resolved_path

        # Path is outside allowed directories
        raise PathNotAllowedError(
            f"Path not in allowed directories: {request_path}",
            requested_path=resolved_path,
            allowed_dirs=self.allowed_dirs,
        )

    def is_allowed(self, request_path: str) -> bool:
        """Check if a path is allowed without raising an exception.

        Args:
            request_path: The path to check.

        Returns:
            True if the path is within allowed directories, False otherwise.
        """
        try:
            self.validate(request_path)
            return True
        except PathNotAllowedError:
            return False


def _is_blocked_file(file_path: Path) -> tuple[bool, str | None]:
    """Check if a file should be blocked based on security rules.

    Args:
        file_path: Path to the file to check.

    Returns:
        Tuple of (is_blocked, reason).
    """
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
    """Read the content of a document within allowed directories.

    This function securely reads a file after validating the path against
    allowed directories. It also enforces file size limits and blocks
    access to sensitive file types.

    Args:
        path: Relative or absolute path to the file.
        validator: PathValidator instance for path validation.
                   If None, a default validator must be provided via context.
        max_size: Maximum file size in characters. Files larger than this
                 will be truncated with a notice.

    Returns:
        ToolResult with success=True and file content in result,
        or success=False and error message in error.

    Example:
        >>> validator = PathValidator(["/docs"])
        >>> result = read_document("/docs/readme.md", validator=validator)
        >>> if result.success:
        ...     print(result.result)
    """
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
    """List all documents in an allowed directory.

    This function securely lists files within allowed directories,
    optionally recursively. It filters out blocked files and sensitive
    directories.

    Args:
        directory: Directory path to list.
        recursive: Whether to include subdirectories.
        extensions: Optional sequence of extensions to filter by (e.g., [".md", ".txt"]).
        validator: PathValidator instance for path validation.

    Returns:
        ToolResult with success=True and list of file paths in result,
        or success=False and error message in error.

    Example:
        >>> validator = PathValidator(["/docs"])
        >>> result = list_documents("/docs", recursive=True, validator=validator)
        >>> if result.success:
        ...     for file_path in result.result:
        ...         print(file_path)
    """
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
) -> Any:
    """Create an MCP server with file reading tools.

    This factory function creates a FastMCP server instance configured
    with read_document and list_documents tools, scoped to the specified
    allowed directories for a specific node.

    Args:
        allowed_dirs: Sequence of directory paths that the node is allowed
                     to access. All paths will be validated.
        node_id: Unique identifier for the node. Used in tool naming.

    Returns:
        Configured FastMCP server instance.

    Raises:
        ValueError: If allowed_dirs is empty or node_id is not provided.
        FileToolError: If there's an error creating the server.

    Example:
        >>> server = create_file_read_server(
        ...     ["/docs", "/docs/research"],
        ...     "analyst"
        ... )
        >>> # Register server with ClaudeAgentOptions
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
        # Import here to avoid hard dependency on mcp
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        raise FileToolError(
            "MCP SDK is required for create_file_read_server. " "Install with: pip install mcp"
        ) from e

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Create server with naming convention: mcp__docuswarm-files-{node_id}
    server_name = f"mcp__docuswarm-files-{node_id}"
    server = FastMCP(server_name)

    @server.tool(name=f"{server_name}__read_document")
    async def mcp_read_document(path: str) -> str:
        """Read the content of a document within allowed directories.

        Args:
            path: Relative or absolute path to the file.

        Returns:
            File content or error message.
        """
        result = read_document(path, validator=validator)
        if result.success:
            return str(result.result)
        return f"Error: {result.error}"

    @server.tool(name=f"{server_name}__list_documents")
    async def mcp_list_documents(directory: str, recursive: bool = False) -> list[str] | str:
        """List all documents in an allowed directory.

        Args:
            directory: Directory path to list.
            recursive: Whether to include subdirectories.

        Returns:
            List of file paths or error message.
        """
        result = list_documents(directory, recursive=recursive, validator=validator)
        if result.success:
            return result.result  # type: ignore[return-value]
        return f"Error: {result.error}"

    logger.info(f"Created file read server for node '{node_id}' with dirs: {valid_dirs}")

    return server


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

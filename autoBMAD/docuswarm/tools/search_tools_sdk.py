"""SDK MCP 格式的搜索工具实现"""

from __future__ import annotations

import fnmatch
import json
import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from autoBMAD.docuswarm.exceptions import PathNotAllowedError, SearchToolError
from autoBMAD.docuswarm.tools.file_tools_sdk import PathValidator
from autoBMAD.docuswarm.tools.tool_result import ToolResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    from claude_agent_sdk import McpSdkServerConfig

logger = logging.getLogger(__name__)

# Maximum search results
MAX_RESULTS_DEFAULT = 20
MAX_RESULTS_LIMIT = 50

# Maximum file size to search (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class SearchResult:
    """Result of a search operation."""

    def __init__(
        self,
        results: list[dict[str, Any]],
        total_matches: int,
        truncated: bool = False,
    ) -> None:
        """Initialize SearchResult."""
        self.results = results
        self.total_matches = total_matches
        self.truncated = truncated

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "results": self.results,
            "total_matches": self.total_matches,
            "truncated": self.truncated,
        }


def _is_binary_file(file_path: Path, sample_size: int = 1024) -> bool:
    """Check if a file is binary by looking for null bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" in chunk
    except OSError:
        return True  # Treat unreadable files as binary


def _should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped during search."""
    # Skip blocked patterns
    path_str = str(file_path)
    blocked_patterns = [
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".env",
        ".svn",
        ".hg",
        ".DS_Store",
    ]

    for pattern in blocked_patterns:
        if pattern in path_str.split(os.sep):
            return True

    # Check file size
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return True
    except OSError:
        return True

    # Check if binary
    if _is_binary_file(file_path):
        return True

    return False


def grep_search(
    pattern: str,
    path: str,
    validator: PathValidator | None = None,
    max_results: int = MAX_RESULTS_DEFAULT,
) -> ToolResult:
    """Search file contents using regex pattern."""
    if validator is None:
        return ToolResult(success=False, error="Path validator is required")

    # Clamp max_results
    if max_results < 1:
        max_results = MAX_RESULTS_DEFAULT
    elif max_results > MAX_RESULTS_LIMIT:
        max_results = MAX_RESULTS_LIMIT

    # Validate and compile regex pattern
    try:
        compiled_pattern = re.compile(pattern, re.MULTILINE)
    except re.error as e:
        return ToolResult(
            success=False, error=f"Invalid regex pattern: {e.msg} at position {e.pos}"
        )

    try:
        # Validate path
        abs_path = validator.validate(path)
        dir_path = Path(abs_path)

        # Check if path is a directory
        if not dir_path.is_dir():
            return ToolResult(
                success=False, error=f"Path is not a directory or does not exist: {path}"
            )

        # Search files
        results: list[dict[str, Any]] = []
        total_matches = 0

        for root, dirs, filenames in os.walk(abs_path, followlinks=False):
            # Filter out blocked directories in-place
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    ".git",
                    "node_modules",
                    "__pycache__",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".env",
                    ".svn",
                    ".hg",
                    ".DS_Store",
                ]
            ]

            for filename in filenames:
                file_path = Path(root) / filename

                # Validate the file path is still within allowed directories
                # (prevents symlink attacks where a symlink points outside allowed dirs)
                try:
                    validator.validate(str(file_path))
                except PathNotAllowedError:
                    continue

                # Skip binary/large files
                if _should_skip_file(file_path):
                    continue

                # Search file content
                try:
                    with open(file_path, encoding="utf-8", errors="replace") as f:
                        for line_num, line in enumerate(f, 1):
                            if compiled_pattern.search(line):
                                total_matches += 1

                                if len(results) < max_results:
                                    results.append(
                                        {
                                            "file": str(file_path),
                                            "line": line_num,
                                            "content": line.rstrip("\n\r"),
                                        }
                                    )

                                # Early termination if we've collected enough
                                if len(results) >= max_results:
                                    # Still count remaining matches
                                    for remaining_line in f:
                                        if compiled_pattern.search(remaining_line):
                                            total_matches += 1
                                    break

                except OSError as e:
                    logger.debug(f"Skipping file {file_path}: {e}")
                    continue

        search_result = SearchResult(
            results=results,
            total_matches=total_matches,
            truncated=total_matches > max_results,
        )

        return ToolResult(success=True, result=search_result.to_dict())

    except PathNotAllowedError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        logger.exception("Unexpected error in grep_search")
        return ToolResult(success=False, error=f"Unexpected error: {e}")


def glob_search(
    pattern: str,
    path: str,
    validator: PathValidator | None = None,
    max_results: int = MAX_RESULTS_DEFAULT,
) -> ToolResult:
    """Search files using glob pattern matching."""
    if validator is None:
        return ToolResult(success=False, error="Path validator is required")

    # Clamp max_results
    if max_results < 1:
        max_results = MAX_RESULTS_DEFAULT
    elif max_results > MAX_RESULTS_LIMIT:
        max_results = MAX_RESULTS_LIMIT

    try:
        # Validate path
        abs_path = validator.validate(path)
        dir_path = Path(abs_path)

        # Check if path is a directory
        if not dir_path.is_dir():
            return ToolResult(
                success=False, error=f"Path is not a directory or does not exist: {path}"
            )

        # Perform glob search
        matches: list[str] = []

        # Handle recursive glob patterns
        if "**" in pattern:
            # Walk directory tree
            for root, dirs, filenames in os.walk(abs_path, followlinks=False):
                # Filter out blocked directories in-place
                dirs[:] = [
                    d
                    for d in dirs
                    if d
                    not in [
                        ".git",
                        "node_modules",
                        "__pycache__",
                        ".pytest_cache",
                        ".mypy_cache",
                        ".env",
                        ".svn",
                        ".hg",
                        ".DS_Store",
                    ]
                ]

                for filename in filenames:
                    file_path = Path(root) / filename

                    # Validate the file path is still within allowed directories
                    try:
                        validator.validate(str(file_path))
                    except PathNotAllowedError:
                        continue

                    # Check if file matches pattern
                    rel_path = file_path.relative_to(dir_path)
                    if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(
                        filename, pattern
                    ):
                        matches.append(str(file_path))

                        if len(matches) >= max_results:
                            break

                if len(matches) >= max_results:
                    break
        else:
            # Non-recursive glob
            for item in dir_path.iterdir():
                if item.is_file():
                    if fnmatch.fnmatch(item.name, pattern):
                        matches.append(str(item))

                        if len(matches) >= max_results:
                            break

        return ToolResult(success=True, result=matches)

    except PathNotAllowedError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        logger.exception("Unexpected error in glob_search")
        return ToolResult(success=False, error=f"Unexpected error: {e}")


def create_search_server(
    search_dirs: Sequence[str],
    node_id: str,
) -> McpSdkServerConfig:
    """Create an SDK MCP search server.

    This factory function creates an SDK MCP server configured
    with grep_search and glob_search tools, scoped to the specified
    allowed directories for a specific node.

    Args:
        search_dirs: List of directory paths that the node is allowed
                     to search within. All paths will be validated.
        node_id: Unique identifier for the node. Used in tool naming.

    Returns:
        SDK MCP server configuration with type, name, instance, and tools.

    Raises:
        ValueError: If search_dirs is empty or node_id is not provided.
        SearchToolError: If there's an error creating the server.
    """
    if not node_id:
        raise ValueError("node_id is required")

    if not search_dirs:
        raise ValueError("At least one search directory must be provided")

    # Validate all directories exist
    valid_dirs: list[str] = []
    for d in search_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Search directory does not exist: {d}")
        valid_dirs.append(abs_path)

    if not valid_dirs:
        raise SearchToolError("No valid search directories provided", search_dirs=list(search_dirs))

    try:
        # Import SDK MCP utilities
        from claude_agent_sdk import create_sdk_mcp_server, tool
    except ImportError as e:
        raise SearchToolError(
            "claude_agent_sdk is required for create_search_server. "
            "Install with: pip install claude-agent-sdk"
        ) from e

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Server name (without mcp__ prefix)
    server_name = f"docuswarm-search-{node_id}"

    @tool(
        "grep_search",
        "Search file contents using regex pattern within allowed directories",
        {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": 'Regex pattern to search for (e.g., "API", "def ", "class.*:")',
                },
                "path": {"type": "string", "description": "Directory path to search within"},
                "max_results": {
                    "type": "integer",
                    "default": MAX_RESULTS_DEFAULT,
                    "minimum": 1,
                    "maximum": MAX_RESULTS_LIMIT,
                    "description": "Maximum number of results to return",
                },
            },
            "required": ["pattern", "path"],
        },
    )
    async def grep_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        """Grep 搜索工具"""
        max_results = min(args.get("max_results", MAX_RESULTS_DEFAULT), MAX_RESULTS_LIMIT)
        result = grep_search(
            pattern=args["pattern"],
            path=args["path"],
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            return {"content": [{"type": "text", "text": json.dumps(result.result, indent=2)}]}
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    @tool(
        "glob_search",
        "Search files using glob pattern matching within allowed directories",
        {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": 'Glob pattern to match (e.g., "**/*.md", "*.txt")',
                },
                "path": {"type": "string", "description": "Directory path to search within"},
                "max_results": {
                    "type": "integer",
                    "default": MAX_RESULTS_DEFAULT,
                    "minimum": 1,
                    "maximum": MAX_RESULTS_LIMIT,
                    "description": "Maximum number of results to return",
                },
            },
            "required": ["pattern", "path"],
        },
    )
    async def glob_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        """Glob 搜索工具"""
        max_results = min(args.get("max_results", MAX_RESULTS_DEFAULT), MAX_RESULTS_LIMIT)
        result = glob_search(
            pattern=args["pattern"],
            path=args["path"],
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            files_str = "\n".join(result.result) if result.result else "No files found"
            return {"content": [{"type": "text", "text": files_str}]}
        return {"content": [{"type": "text", "text": f"Error: {result.error}"}]}

    logger.info(f"Created SDK MCP search server for node '{node_id}' with dirs: {valid_dirs}")

    return create_sdk_mcp_server(
        name=server_name, version="1.0.0", tools=[grep_search_tool, glob_search_tool]
    )


# Export public API
__all__ = [
    "MAX_RESULTS_DEFAULT",
    "MAX_RESULTS_LIMIT",
    "MAX_FILE_SIZE",
    "SearchResult",
    "grep_search",
    "glob_search",
    "create_search_server",
]

"""Search Tools MCP Server for DocuSwarm.

This module provides MCP (Model Context Protocol) tools for searching document
contents and file patterns within allowed directories. It implements secure
grep-style content search and glob pattern matching with permission checking.

Example:
    >>> from autoBMAD.docuswarm.tools.search_tools import create_search_server
    >>> server = create_search_server(["/docs", "/docs/research"], "analyst")
    >>> # Server can be registered with ClaudeAgentOptions

Attributes:
    MAX_RESULTS_DEFAULT: Default maximum number of search results (20).
    MAX_RESULTS_LIMIT: Absolute maximum number of search results (50).
    MAX_FILE_SIZE: Maximum file size to search in bytes (10MB).
"""

from __future__ import annotations

import fnmatch
import logging
import os
import re
from pathlib import Path
from typing import Any

from autoBMAD.docuswarm.exceptions import PathNotAllowedError, SearchToolError
from autoBMAD.docuswarm.tools.file_tools import PathValidator
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

# Maximum search results
MAX_RESULTS_DEFAULT = 20
MAX_RESULTS_LIMIT = 50

# Maximum file size to search (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class SearchResult:
    """Result of a search operation.

    Attributes:
        results: List of match dictionaries containing file, line, and content.
        total_matches: Total number of matches found.
        truncated: Whether results were truncated due to limit.
    """

    def __init__(
        self,
        results: list[dict[str, Any]],
        total_matches: int,
        truncated: bool = False,
    ) -> None:
        """Initialize SearchResult.

        Args:
            results: List of match dictionaries.
            total_matches: Total number of matches found.
            truncated: Whether results were truncated.
        """
        self.results = results
        self.total_matches = total_matches
        self.truncated = truncated

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format.

        Returns:
            Dictionary with results, total_matches, and truncated fields.
        """
        return {
            "results": self.results,
            "total_matches": self.total_matches,
            "truncated": self.truncated,
        }


def _is_binary_file(file_path: Path, sample_size: int = 1024) -> bool:
    """Check if a file is binary by looking for null bytes.

    Args:
        file_path: Path to the file to check.
        sample_size: Number of bytes to read for detection.

    Returns:
        True if file appears to be binary, False otherwise.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" in chunk
    except OSError:
        return True  # Treat unreadable files as binary


def _should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped during search.

    Args:
        file_path: Path to the file.

    Returns:
        True if file should be skipped, False otherwise.
    """
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
    """Search file contents using regex pattern.

    This function performs a recursive grep-style search within allowed directories,
    finding lines that match the provided regex pattern.

    Args:
        pattern: Regex pattern to search for.
        path: Directory path to search within.
        validator: PathValidator instance for permission checking.
        max_results: Maximum number of results to return (default 20, max 50).

    Returns:
        ToolResult with SearchResult dictionary on success, or error message.

    Example:
        >>> validator = PathValidator(["/docs"])
        >>> result = grep_search(r"API", "/docs", validator=validator)
        >>> if result.success:
        ...     for match in result.result["results"]:
        ...         print(f"{match['file']}:{match['line']}: {match['content']}")
    """
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
    """Search files using glob pattern matching.

    This function performs pattern matching to find files within allowed directories,
    supporting standard glob patterns like **/*.md, *.txt, etc.

    Args:
        pattern: Glob pattern to match (e.g., "**/*.md", "*.txt").
        path: Directory path to search within.
        validator: PathValidator instance for permission checking.
        max_results: Maximum number of results to return (default 20, max 50).

    Returns:
        ToolResult with list of matching file paths on success, or error message.

    Example:
        >>> validator = PathValidator(["/docs"])
        >>> result = glob_search("**/*.md", "/docs", validator=validator)
        >>> if result.success:
        ...     for file_path in result.result:
        ...         print(file_path)
    """
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
    search_dirs: list[str],
    node_id: str,
) -> Any:
    """Create an MCP server with search tools.

    This factory function creates a FastMCP server instance configured
    with grep_search and glob_search tools, scoped to the specified
    allowed directories for a specific node.

    Args:
        search_dirs: List of directory paths that the node is allowed
                     to search within. All paths will be validated.
        node_id: Unique identifier for the node. Used in tool naming.

    Returns:
        Configured FastMCP server instance.

    Raises:
        ValueError: If search_dirs is empty or node_id is not provided.
        SearchToolError: If there's an error creating the server.

    Example:
        >>> server = create_search_server(
        ...     ["/docs", "/docs/research"],
        ...     "analyst"
        ... )
        >>> # Register server with ClaudeAgentOptions
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
        # Import here to avoid hard dependency on mcp
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:
        raise SearchToolError(
            "MCP SDK is required for create_search_server. " "Install with: pip install mcp"
        ) from e

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Create server with naming convention: mcp__docuswarm-search-{node_id}
    server_name = f"mcp__docuswarm-search-{node_id}"
    server = FastMCP(server_name)

    @server.tool(name=f"{server_name}__grep_search")
    async def mcp_grep_search(
        pattern: str,
        path: str,
        max_results: int = MAX_RESULTS_DEFAULT,
    ) -> dict[str, Any] | str:
        """Search file contents using regex pattern within allowed directories.

        Args:
            pattern: Regex pattern to search for (e.g., "API", "def ", "class.*:").
            path: Directory path to search within (must be within allowed directories).
            max_results: Maximum number of results to return (default: 20, max: 50).

        Returns:
            Dictionary with search results:
            - results: List of matches, each with file, line, and content
            - total_matches: Total number of matches found
            - truncated: True if more results exist beyond the limit
            Or error message string on failure.

        Example:
            Search for "authentication" in docs:
            >>> result = grep_search("authentication", "/docs")
        """
        result = grep_search(
            pattern=pattern,
            path=path,
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            return result.result  # type: ignore[return-value]
        return f"Error: {result.error}"

    @server.tool(name=f"{server_name}__glob_search")
    async def mcp_glob_search(
        pattern: str,
        path: str,
        max_results: int = MAX_RESULTS_DEFAULT,
    ) -> list[str] | str:
        """Search files using glob pattern matching within allowed directories.

        Args:
            pattern: Glob pattern to match (e.g., "**/*.md" for all markdown files,
                    "*.txt" for text files in the specified directory).
            path: Directory path to search within (must be within allowed directories).
            max_results: Maximum number of results to return (default: 20, max: 50).

        Returns:
            List of matching file paths, or error message string on failure.

        Example:
            Find all markdown files:
            >>> result = glob_search("**/*.md", "/docs")
        """
        result = glob_search(
            pattern=pattern,
            path=path,
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            return result.result  # type: ignore[return-value]
        return f"Error: {result.error}"

    logger.info(f"Created search server for node '{node_id}' with dirs: {valid_dirs}")

    return server


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

"""
Claude Session Manager Module

Provides a high-level wrapper around the Claude Agent SDK for agent interactions.
This module enables agents to interact with Claude through the SDK with proper
session management, exception handling, and structured logging.

Example:
    >>> from autoBMAD.docuswarm.llm.session_manager import SessionManager
    >>> from pathlib import Path
    >>>
    >>> async with SessionManager(work_dir=Path.cwd()) as manager:
    ...     messages = await manager.single_prompt("Hello, Claude!")
"""

from __future__ import annotations

import asyncio
import types
from collections.abc import AsyncIterator
from contextlib import suppress
from pathlib import Path
from typing import Any

import structlog
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeSDKError,
    ResultMessage,
    query,
)
from claude_agent_sdk.types import ClaudeAgentOptions

from autoBMAD.docuswarm.exceptions import LLMError
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

# Structured logger for this module
logger: structlog.BoundLogger = structlog.get_logger(__name__)


async def _close_client_with_process_fallback(
    client: ClaudeSDKClient,
    log: structlog.BoundLogger,
    disconnect_timeout: float = 10.0,
    kill_wait_timeout: float = 5.0,
) -> None:
    """Close a client with subprocess fallback.

    P0 Fix:
    1. 在 disconnect() 前预先捕获 _transport._process。
    2. 给 disconnect() 加 asyncio.wait_for() timeout。
    3. 如果 disconnect() 超时或返回后进程仍存活，执行 kill() 并等待。
    """
    # Pre-capture transport/process before disconnect() may clear them
    transport = getattr(client, "_transport", None)
    process = getattr(transport, "_process", None) if transport is not None else None

    # Attempt graceful disconnect with timeout
    try:
        await asyncio.wait_for(client.disconnect(), timeout=disconnect_timeout)
    except asyncio.TimeoutError:
        log.warning("disconnect_timeout", disconnect_timeout=disconnect_timeout)
    except Exception as e:
        log.warning("disconnect_error", error=str(e))

    # Force-kill fallback if process is still alive
    if process is not None and process.returncode is None:
        log.warning(
            "force_kill_cli_subprocess",
            pid=getattr(process, "pid", None),
        )
        try:
            process.kill()
            await asyncio.wait_for(process.wait(), timeout=kill_wait_timeout)
        except asyncio.TimeoutError:
            log.error("force_kill_wait_timeout")
        except Exception as e:
            log.error("force_kill_error", error=str(e))


class SessionManager:
    """
    Manages Claude Agent SDK sessions for DocuSwarm agents.

    This class provides a high-level interface to create, resume, and manage
    Claude sessions through the SDK. It handles:
    - Session lifecycle (create, resume, close)
    - Exception mapping (SDK -> DocuSwarm exceptions)
    - Active session tracking
    - Structured logging for all operations

    Attributes:
        work_dir: Working directory for sessions (Path).
        agent_file: Optional path to agent specification file.
        config: Optional configuration object.

    Example:
        >>> from pathlib import Path
        >>> from autoBMAD.docuswarm.llm.session_manager import SessionManager
        >>>
        >>> async with SessionManager(work_dir=Path.cwd()) as manager:
        ...     # Use single prompt for quick interactions
        ...     messages = await manager.single_prompt("What is 2+2?")
    """

    def __init__(
        self,
        work_dir: Path | None = None,
        agent_file: Path | None = None,
        config: Any | None = None,
        node_id: str | None = None,
        file_dirs: list[str] | None = None,
        search_dirs: list[str] | None = None,
        tool_permissions: Any | None = None,
        cwd: Path | None = None,
        output_dir: Path | None = None,
        pipeline_id: str | None = None,  # F2 Fix: 添加 pipeline_id 参数
    ) -> None:
        """
        Initialize the SessionManager.

        Args:
            work_dir: Working directory for sessions (Path). Deprecated, use cwd or output_dir instead.
            agent_file: Optional path to agent specification file.
            config: Optional configuration object or path to config file.
            node_id: Optional node identifier for MCP tool isolation.
            file_dirs: Optional list of allowed directories for file tools.
            search_dirs: Optional list of allowed directories for search tools.
            tool_permissions: Optional NodeToolPermissions object for complete tool permission config.
            cwd: Working directory for SDK (should be repo root for import).
            output_dir: Directory for file output (e.g., output/pipeline_id).
            pipeline_id: Optional pipeline identifier for shared-context MCP server creation.
        """
        # Handle backward compatibility and new cwd/output_dir split
        # Convert string paths to Path objects
        if work_dir is not None:
            work_dir = Path(work_dir) if not isinstance(work_dir, Path) else work_dir
        if cwd is not None:
            cwd = Path(cwd) if not isinstance(cwd, Path) else cwd
        if output_dir is not None:
            output_dir = Path(output_dir) if not isinstance(output_dir, Path) else output_dir

        if work_dir is not None:
            # Deprecated: work_dir used for both cwd and output_dir
            self._cwd = cwd or work_dir
            self._output_dir = output_dir or work_dir
        else:
            # New style: separate cwd and output_dir
            self._cwd = cwd or Path.cwd()
            self._output_dir = output_dir or self._cwd

        self._agent_file = agent_file
        self._config = config
        self._node_id = node_id
        self._tool_permissions = tool_permissions
        self._file_dirs = file_dirs or []
        self._search_dirs = search_dirs or []
        self._pipeline_id = pipeline_id  # F2 Fix: 存储 pipeline_id
        self._active_clients: dict[str, ClaudeSDKClient] = {}
        # P0 Fix: 跟踪 wrapper 以在 close_all() 时同步 _closed 状态
        self._active_wrappers: dict[str, ClaudeSessionWrapper] = {}
        self._logger = logger.bind(
            component="SessionManager",
            cwd=str(self._cwd),
            output_dir=str(self._output_dir),
            agent_file=str(agent_file) if agent_file else None,
            node_id=node_id,
            pipeline_id=pipeline_id,  # F2 Fix: 记录 pipeline_id
        )

    def _stderr_callback(self, line: str) -> None:
        """A-3 Fix: SDK CLI stderr callback.

        Receives lines from the CLI subprocess stderr stream and routes them
        to structlog for observability.
        """
        line_preview = line[:200]
        line_length = len(line)
        # Use error level for lines that look like actual errors
        lower = line.lower()
        if any(keyword in lower for keyword in ("error", "fail", "timeout", "exception", "econnreset")):
            self._logger.error(
                "cli_subprocess_stderr",
                line_preview=line_preview,
                line_length=line_length,
            )
        else:
            self._logger.debug(
                "cli_subprocess_stderr",
                line_preview=line_preview,
                line_length=line_length,
            )

    @property
    def work_dir(self) -> Path:
        """Get the working directory (deprecated, use cwd or output_dir)."""
        return self._output_dir  # For backward compatibility, return output_dir

    @property
    def cwd(self) -> Path:
        """Get cwd for SDK import."""
        return self._cwd

    @property
    def output_dir(self) -> Path:
        """Get output directory for file operations."""
        return self._output_dir

    @property
    def agent_file(self) -> Path | None:
        """Get the agent file path."""
        return self._agent_file

    @property
    def config(self) -> Any | None:
        """Get the configuration."""
        return self._config

    @property
    def node_id(self) -> str | None:
        """Get the node ID."""
        return self._node_id

    @property
    def file_dirs(self) -> list[str]:
        """Get the file directories."""
        return self._file_dirs

    @property
    def search_dirs(self) -> list[str]:
        """Get the search directories."""
        return self._search_dirs

    def _get_builtin_tools(self) -> list[str]:
        """Get the list of built-in tools available to all sessions.

        P0-F3: Returns tools from node configuration instead of hardcoded list.
        Falls back to safe read-only defaults when no permissions are configured.

        Returns:
            List of built-in tool names (e.g., "Read", "Glob")
        """
        if self._tool_permissions is not None:
            allowed = getattr(self._tool_permissions, "allowed_builtin_tools", None)
            if allowed is not None:
                return list(allowed)
        # Safe fallback: read-only tools only
        return ["Read", "Glob"]

    def _build_allowed_tools(self) -> list[str]:
        """Build the complete list of allowed tools.

        This method combines:
        1. "Skill" tool (first for priority access to SDK native skills, if enabled)
        2. Built-in tools (Read, Glob, Grep, Edit, Bash)
        3. MCP tools from NodeToolFilter (if configured)

        Returns:
            List of allowed tool names with "Skill" as the first entry when enabled.
        """
        tools: list[str] = []

        # F1 Fix: Conditionally add "Skill" tool based on sdk_native setting
        if (self._tool_permissions is not None and 
            self._tool_permissions.skills.sdk_native):
            # Add "Skill" tool as first entry for SDK native skills priority
            tools.append("Skill")
            self._logger.debug("sdk_native_skills_enabled", node_id=self._node_id)
        else:
            self._logger.debug("sdk_native_skills_disabled", node_id=self._node_id)

        # Add built-in tools
        tools.extend(self._get_builtin_tools())

        # Add MCP tools if node_id and tool_permissions are configured
        if self._node_id and self._tool_permissions is not None:
            try:
                from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

                node_filter = NodeToolFilter(
                    node_id=self._node_id,
                    tool_permissions=self._tool_permissions,
                    output_dir=str(self._output_dir) if self._output_dir else None,
                )

                # Get MCP tool names (excluding builtin tools which we already added)
                mcp_tools = node_filter.get_allowed_tools()
                # Filter out builtin tools to avoid duplication
                builtin_tools = self._get_builtin_tools()
                mcp_only_tools = [t for t in mcp_tools if t not in builtin_tools]
                tools.extend(mcp_only_tools)

            except Exception as e:
                self._logger.warning(
                    "mcp_tools_build_failed",
                    node_id=self._node_id,
                    error=str(e),
                )

        return tools

    def _create_options(
        self,
        mode: str = "agent",
        yolo: bool = True,
        output_format: dict[str, Any] | None = None,
    ) -> ClaudeAgentOptions:
        """Create ClaudeAgentOptions from configuration.

        Args:
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls.
            output_format: Optional JSON schema for structured output (Story 38.1).

        Returns:
            ClaudeAgentOptions instance with MCP server configuration.
        """
        # P0-F3: yolo=True should not bypass permissions entirely.
        # Use "default" permission mode and rely on allowed_tools for restriction.
        permission_mode = "default"

        options_dict: dict[str, Any] = {
            "cwd": self._cwd,  # FIX-2B: Use _cwd instead of _work_dir for SDK import
            "permission_mode": permission_mode,
        }

        # F1 Fix: Conditionally set setting_sources based on sdk_native setting
        if (self._tool_permissions is not None and 
            self._tool_permissions.skills.sdk_native):
            options_dict["setting_sources"] = ["project"]  # Enable SDK auto-discovery of skills
            self._logger.debug("setting_sources_enabled", node_id=self._node_id)

        # TDD-07: Removed agent_file from options.tools - kimi-agent-sdk format
        # is not compatible with claude-agent-sdk. Tools are now registered as MCP servers.

        # Add thinking mode if requested
        # TDD-08: Use ThinkingConfig dict, not bool (RC-8 fix)
        if mode == "thinking":
            options_dict["thinking"] = {"type": "enabled", "budget_tokens": 10000}

        # Configure MCP servers and allowed tools if node_id and file_dirs are provided
        has_tool_permissions = self._tool_permissions is not None
        has_dirs = self._file_dirs or self._search_dirs

        if self._node_id and (has_tool_permissions or has_dirs):
            self._logger.debug(
                "configuring_mcp_servers",
                node_id=self._node_id,
                file_dirs=self._file_dirs,
                search_dirs=self._search_dirs,
                has_full_tool_permissions=has_tool_permissions,
            )

            try:
                # Create NodeToolFilter to manage tool permissions and MCP servers
                from autoBMAD.nodes.loader import (
                    NodeFilePermissions,
                    NodeSearchPermissions,
                    NodeToolPermissions,
                )

                # Use full tool_permissions if provided, otherwise build from file/search dirs
                if self._tool_permissions is not None:
                    # Use the complete NodeToolPermissions passed from caller
                    tool_permissions = self._tool_permissions
                else:
                    # Build tool permissions from file and search directories
                    tool_permissions = NodeToolPermissions(
                        file_permissions=NodeFilePermissions(allowed_read_dirs=self._file_dirs),
                        search_permissions=NodeSearchPermissions(search_dirs=self._search_dirs),
                    )

                # Create NodeToolFilter for this node
                # TDD-07: Pass output_dir for deliverable MCP server creation
                node_filter = NodeToolFilter(
                    node_id=self._node_id,
                    tool_permissions=tool_permissions,
                    output_dir=str(self._output_dir),
                )

                # Create MCP servers for this node
                try:
                    # F2 Fix: 传递 pipeline_id 以创建 shared-context server
                    mcp_servers = node_filter.create_mcp_servers(pipeline_id=self._pipeline_id)
                    if mcp_servers:
                        # SDK MCP servers are already returned as dict: {server_name: server_dict}
                        options_dict["mcp_servers"] = mcp_servers

                        self._logger.debug(
                            "mcp_servers_created",
                            node_id=self._node_id,
                            server_count=len(mcp_servers),
                            server_keys=list(mcp_servers.keys()),
                        )
                except Exception as e:
                    self._logger.warning(
                        "mcp_server_creation_failed",
                        node_id=self._node_id,
                        error=str(e),
                    )

                # Generate allowed tools list with MCP tool names
                try:
                    # Use _build_allowed_tools() to ensure "Skill" is first
                    # and builtin tools are properly included
                    allowed_tools = self._build_allowed_tools()
                    if allowed_tools:
                        options_dict["allowed_tools"] = allowed_tools
                        self._logger.debug(
                            "allowed_tools_configured",
                            node_id=self._node_id,
                            tool_count=len(allowed_tools),
                            tools=allowed_tools,
                        )
                except Exception as e:
                    self._logger.warning(
                        "allowed_tools_generation_failed",
                        node_id=self._node_id,
                        error=str(e),
                    )

            except Exception as e:
                self._logger.warning(
                    "mcp_configuration_failed",
                    node_id=self._node_id,
                    error=str(e),
                )

        # Ensure allowed_tools is set even without node_id/tool_permissions
        # This ensures "Skill" tool is always available for SDK native skills
        if "allowed_tools" not in options_dict:
            options_dict["allowed_tools"] = self._build_allowed_tools()

        # Story 38.1: Inject output_format for structured output if provided
        if output_format is not None:
            options_dict["output_format"] = {
                "type": "json_schema",
                "schema": output_format,
            }

        # A-3 Fix: Register stderr callback for CLI subprocess observability
        options_dict["stderr"] = self._stderr_callback

        return ClaudeAgentOptions(**options_dict)

    async def create_session(
        self,
        mode: str = "agent",
        yolo: bool = True,
        max_steps: int | None = None,
        agent_file: Path | None = None,
        approval_handler_fn: Any | None = None,
        system_prompt: str | dict[str, Any] | None = None,
    ) -> ClaudeSessionWrapper:
        """
        Create a new Claude session.

        Args:
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls (True for IndependentAgent).
            max_steps: Maximum steps per turn (optional).
            agent_file: Optional path to agent specification file. Overrides the
                agent_file set in the constructor if provided.
            approval_handler_fn: Optional approval handler callback for custom
                approval logic. If provided and yolo=False, this handler will
                be used instead of the default prompt-based approval.
            system_prompt: Optional system prompt to provide context to the model.

        Returns:
            ClaudeSessionWrapper: A wrapper around SDK client.

        Raises:
            LLMError: On SDK errors.
        """
        try:
            self._logger.info(
                "creating_session",
                mode=mode,
                yolo=yolo,
                max_steps=max_steps,
            )

            # Use per-session agent_file if provided
            effective_agent_file = agent_file if agent_file is not None else self._agent_file

            # Create options
            options = self._create_options(mode=mode, yolo=yolo)

            # TDD-07: Removed options.tools override with agent_file
            # The kimi-agent-sdk YAML format is not compatible with claude-agent-sdk.
            # Tools are now registered as MCP servers via NodeToolFilter.
            if effective_agent_file:
                self._logger.debug(
                    "agent_file_skipped_for_tools",
                    agent_file=str(effective_agent_file),
                    reason="kimi-agent-sdk format not compatible with claude-agent-sdk",
                )

            # Set system_prompt if provided
            if system_prompt is not None:
                if isinstance(system_prompt, dict):
                    # Dict format (preset/append) - use as-is
                    options.system_prompt = system_prompt
                else:
                    # String format - wrap to preset/append structure
                    options.system_prompt = {
                        "type": "preset",
                        "preset": "claude_code",
                        "append": system_prompt,
                    }

            # Create client
            client = ClaudeSDKClient(options=options)

            # Connect the client
            await client.connect()

            # Generate a session ID
            import uuid

            session_id = f"session_{uuid.uuid4().hex[:12]}"

            # Wrap the client - P1 Fix: 传递 options 供 prompt() 使用
            wrapper = ClaudeSessionWrapper(
                client=client,
                session_id=session_id,
                work_dir=self._output_dir,  # FIX: 使用 _output_dir，_work_dir 已不存在
                options=options,  # P1 Fix: 保存 options 供 prompt() 使用
            )

            # Track the session
            self._active_clients[session_id] = client
            self._active_wrappers[session_id] = wrapper  # P0 Fix: 同步跟踪 wrapper

            self._logger.info(
                "session_created",
                session_id=session_id,
                mode=mode,
            )

            # Log tool configuration summary if node_id and tool_permissions are configured
            if self._node_id and self._tool_permissions is not None:
                self._logger.info(
                    "tools_configured",
                    mcp_servers=len(options.mcp_servers)
                    if hasattr(options, "mcp_servers") and options.mcp_servers
                    else 0,
                    allowed_tools=options.allowed_tools
                    if hasattr(options, "allowed_tools")
                    else [],
                    file_dirs=self._tool_permissions.file_permissions.allowed_read_dirs
                    if hasattr(self._tool_permissions, "file_permissions")
                    else [],
                    search_dirs=self._tool_permissions.search_permissions.search_dirs
                    if hasattr(self._tool_permissions, "search_permissions")
                    else [],
                )

            return wrapper

        except Exception as e:
            self._logger.error("session_creation_failed", error=str(e))
            raise LLMError(
                f"Failed to create session: {e}",
                api_error_type=type(e).__name__,
            ) from e

    async def resume_session(self, session_id: str | None = None) -> ClaudeSessionWrapper | None:
        """
        Resume an existing session.

        Args:
            session_id: Session ID to resume. If None, resumes the most recent.

        Returns:
            ClaudeSessionWrapper | None: The resumed session, or None if not found.

        Raises:
            LLMError: On SDK errors.
        """
        try:
            self._logger.info("resuming_session", session_id=session_id)

            # Check if session exists
            if session_id and session_id in self._active_clients:
                client = self._active_clients[session_id]
                wrapper = ClaudeSessionWrapper(
                    client=client,
                    session_id=session_id,
                    work_dir=self._output_dir,  # FIX: 使用 _output_dir，_work_dir 已不存在
                )

                # P0 Fix: 跟踪 resumed wrapper
                self._active_wrappers[session_id] = wrapper

                self._logger.info(
                    "session_resumed",
                    session_id=session_id,
                )
                return wrapper

            self._logger.warning("session_not_found", session_id=session_id)
            return None

        except Exception as e:
            self._logger.error("session_resume_failed", error=str(e))
            raise LLMError(
                f"Failed to resume session: {e}",
                api_error_type=type(e).__name__,
            ) from e

    async def resume_or_create(
        self,
        session_id: str | None = None,
        mode: str = "agent",
        yolo: bool = True,
        max_steps: int | None = None,
        approval_handler_fn: Any | None = None,
    ) -> ClaudeSessionWrapper:
        """
        Resume an existing session or create a new one.

        Args:
            session_id: Session ID to resume.
            mode: Session mode for new session.
            yolo: Whether to auto-approve tool calls.
            max_steps: Maximum steps per turn.
            approval_handler_fn: Optional approval handler.

        Returns:
            ClaudeSessionWrapper: The resumed or newly created session.
        """
        # First try to resume
        session = await self.resume_session(session_id)

        if session is not None:
            self._logger.info(
                "session_resume_success",
                session_id=session_id,
                mode=mode,
            )
            return session

        # Session not found - create new one
        self._logger.warning(
            "session_not_found_creating_new",
            session_id=session_id,
            requested_mode=mode,
        )

        return await self.create_session(
            mode=mode,
            yolo=yolo,
            max_steps=max_steps,
            approval_handler_fn=approval_handler_fn,
        )

    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        system_prompt: str | None = None,
        output_format: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a single prompt and return messages as dicts (one-shot API).

        Args:
            prompt: The prompt to send.
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls.
            system_prompt: Optional system prompt for model context (TDD-09).
            output_format: Optional JSON schema for structured output (Story 38.1).

        Returns:
            list[dict[str, Any]]: List of message dicts from the response.
            Returns empty list if execution is cancelled.
            When output_format is provided and successful, returns structured output
            in format: [{"type": "structured", "data": <validated_data>}]

        Raises:
            LLMError: On SDK errors.
            ConfigurationError: On SDK configuration errors.
        """
        self._logger.info(
            "single_prompt_start",
            prompt_length=len(prompt),
            mode=mode,
            has_output_format=output_format is not None,
        )

        messages: list[dict[str, Any]] = []
        message_count = 0
        tool_call_count = 0
        structured_output: dict[str, Any] | None = None

        try:
            # Create options for the query
            options = self._create_options(mode=mode, yolo=yolo, output_format=output_format)

            # Log tool configuration summary if node_id and tool_permissions are configured
            if self._node_id and self._tool_permissions is not None:
                self._logger.info(
                    "tools_configured",
                    mcp_servers=len(options.mcp_servers)
                    if hasattr(options, "mcp_servers") and options.mcp_servers
                    else 0,
                    allowed_tools=options.allowed_tools
                    if hasattr(options, "allowed_tools")
                    else [],
                    file_dirs=self._tool_permissions.file_permissions.allowed_read_dirs
                    if hasattr(self._tool_permissions, "file_permissions")
                    else [],
                    search_dirs=self._tool_permissions.search_permissions.search_dirs
                    if hasattr(self._tool_permissions, "search_permissions")
                    else [],
                )

            # TDD-09: Set system_prompt on options if provided
            if system_prompt is not None:
                options.system_prompt = {
                    "type": "preset",
                    "preset": "claude_code",
                    "append": system_prompt,
                }

            # Use the claude_agent_sdk.query() function directly
            async for msg in query(prompt=prompt, options=options):
                message_count += 1

                # Convert message to dict format
                msg_dict = self._message_to_dict(msg)
                if msg_dict:
                    messages.append(msg_dict)

                    # Track tool calls
                    content = msg_dict.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "tool_use":
                                tool_call_count += 1
                                self._logger.info(
                                    "llm_tool_call",
                                    message_index=message_count,
                                    tool_name=item.get("name", "unknown"),
                                )

                # Check for result message
                if isinstance(msg, ResultMessage):
                    # Story 38.1: Handle structured output and retry exhaustion
                    msg_subtype = getattr(msg, "subtype", None)
                    msg_structured_output = getattr(msg, "structured_output", None)

                    self._logger.info(
                        "single_prompt_result",
                        result=getattr(msg, "result", None),
                        is_error=getattr(msg, "is_error", False),
                        subtype=msg_subtype,
                        has_structured_output=msg_structured_output is not None,
                    )

                    # Store structured output if available
                    if msg_structured_output is not None:
                        structured_output = msg_structured_output

                    # Handle error_max_structured_output_retries subtype
                    if msg_subtype == "error_max_structured_output_retries":
                        self._logger.error(
                            "structured_output_retries_exhausted",
                            subtype=msg_subtype,
                        )
                        raise LLMError(
                            "SDK structured output retries exhausted",
                            api_error_type="error_max_structured_output_retries",
                        )

            # Story 38.1: If structured output is available, return it in standard format
            if structured_output is not None:
                self._logger.info(
                    "returning_structured_output",
                    data_keys=list(structured_output.keys()),
                )
                return [{"type": "structured", "data": structured_output}]

            self._logger.info(
                "single_prompt_complete",
                message_count=len(messages),
                tool_calls=tool_call_count,
            )

            return messages

        except asyncio.CancelledError:
            self._logger.info("single_prompt_cancelled")
            return []

        except LLMError:
            # Re-raise LLMError as-is (includes error_max_structured_output_retries)
            raise

        except ClaudeSDKError as e:
            self._logger.error("single_prompt_sdk_error", error=str(e))
            raise LLMError(
                f"SDK error: {e}",
                api_error_type="ClaudeSDKError",
            ) from e

        except Exception as e:
            self._logger.error("single_prompt_error", error=str(e))
            raise LLMError(
                f"Single prompt failed: {e}",
            ) from e

    def _message_to_dict(self, msg: Any) -> dict[str, Any] | None:
        """Convert SDK message to dict format.

        Fix: 使用 isinstance 判断消息类型，而非依赖 role 属性。
        官方文档推荐模式：通过类型检查识别 AssistantMessage/UserMessage。

        Args:
            msg: Message object from SDK.

        Returns:
            Dict representation of message or None.
        """
        if msg is None:
            return None

        # If it's already a dict, return it
        if isinstance(msg, dict):
            return msg

        # Handle ResultMessage - skip it (it's metadata)
        if isinstance(msg, ResultMessage):
            return None

        # Fix: 使用 isinstance 判断消息类型，符合官方文档设计
        role = None
        # Try to import SDK types for isinstance checks
        try:
            from claude_agent_sdk.types import AssistantMessage, SystemMessage, UserMessage

            # Handle SystemMessage - skip it (subtype='init', etc.)
            if isinstance(msg, SystemMessage):
                return None

            # Fix: 使用 isinstance 判断消息类型，而非 getattr(msg, "role", None)
            if isinstance(msg, AssistantMessage):
                role = "assistant"
            elif isinstance(msg, UserMessage):
                role = "user"
        except ImportError:
            pass  # SDK types not available, will try fallback below

        # Fallback: 如果 isinstance 检查失败，尝试 role 属性或 duck typing
        if role is None:
            role = getattr(msg, "role", None)

            # Fix: 如果仍无 role，尝试通过 duck typing 推断
            # AssistantMessage 和 UserMessage 都有 content，但 SystemMessage 有 subtype
            if role is None and hasattr(msg, "content"):
                # 如果有 model 属性，很可能是 AssistantMessage
                if hasattr(msg, "model"):
                    role = "assistant"
                # 否则如果 content 是字符串，可能是 UserMessage
                elif isinstance(getattr(msg, "content", None), str):
                    role = "user"

            if role is None:
                return None

        content = getattr(msg, "content", None)

        # Convert content to list format if needed
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        elif isinstance(content, list):
            # Already in list format, ensure each item is a dict
            converted_content = []
            for item in content:
                if isinstance(item, dict):
                    converted_content.append(item)
                else:
                    # Fix: 使用 isinstance 检查 content block 类型
                    converted_block = self._convert_content_block(item)
                    if converted_block:
                        converted_content.append(converted_block)
            content = converted_content
        elif hasattr(content, "type"):
            # RC-2 Fix: 处理单个 content block（不在 list 中）
            # 避免 str(ThinkingBlock(...)) 泄露到文本内容
            converted_block = self._convert_content_block(content)
            if converted_block:
                content = [converted_block]
            else:
                content = []  # ThinkingBlock 等被过滤为空
        else:
            content = [{"type": "text", "text": str(content)}]

        return {
            "role": role,
            "content": content,
        }

    def _convert_content_block(self, item: Any) -> dict[str, Any] | None:
        """Convert a content block to dict format.

        Fix: 使用 isinstance 判断类型，而非依赖 type 属性。
        ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock

        Args:
            item: Content block from SDK.

        Returns:
            Dict representation of content block or None.
        """
        converted = None

        try:
            from claude_agent_sdk.types import (
                TextBlock,
                ThinkingBlock,
                ToolResultBlock,
                ToolUseBlock,
            )

            if isinstance(item, TextBlock):
                converted = {"type": "text", "text": item.text}
            elif isinstance(item, ThinkingBlock):
                # ThinkingBlock 无 text 属性，根据需求跳过
                # 如需保留，可改为: return {"type": "thinking", "thinking": item.thinking}
                converted = None
            elif isinstance(item, ToolUseBlock):
                converted = {
                    "type": "tool_use",
                    "name": getattr(item, "name", ""),
                    "input": getattr(item, "input", {}),
                    "id": getattr(item, "id", ""),
                }
            elif isinstance(item, ToolResultBlock):
                converted = {
                    "type": "tool_result",
                    "tool_use_id": getattr(item, "tool_use_id", ""),
                    "content": getattr(item, "content", ""),
                    "is_error": getattr(item, "is_error", False),
                }
        except ImportError:
            pass  # SDK types not available, will try duck typing below

        # Fix: 如果 isinstance 检查失败，尝试 duck typing 识别
        if converted is None:
            # Duck typing: ToolUseBlock 有 name 和 input 属性
            if hasattr(item, "name") and hasattr(item, "input") and hasattr(item, "id"):
                converted = {
                    "type": "tool_use",
                    "name": getattr(item, "name", ""),
                    "input": getattr(item, "input", {}),
                    "id": getattr(item, "id", ""),
                }
            # Duck typing: ToolResultBlock 有 tool_use_id 属性
            elif hasattr(item, "tool_use_id"):
                converted = {
                    "type": "tool_result",
                    "tool_use_id": getattr(item, "tool_use_id", ""),
                    "content": getattr(item, "content", ""),
                    "is_error": getattr(item, "is_error", False),
                }
            # Duck typing: TextBlock 有 text 属性但没有 tool_use_id 或 name
            elif (
                hasattr(item, "text")
                and not hasattr(item, "tool_use_id")
                and not hasattr(item, "name")
            ):
                converted = {"type": "text", "text": item.text}
            # RC-2 Fix: Duck typing for ThinkingBlock - 有 .thinking 属性或 type="thinking"
            elif hasattr(item, "thinking") or getattr(item, "type", "") == "thinking":
                converted = None  # 过滤 ThinkingBlock
            # Final fallback: try getattr
            else:
                item_type = getattr(item, "type", "text")
                if item_type == "text":
                    converted = {"type": "text", "text": getattr(item, "text", str(item))}
                else:
                    converted = {"type": item_type, "content": str(item)}

        return converted

    async def _close_wrapper(self, wrapper: ClaudeSessionWrapper) -> None:
        """Close a single wrapper using the shared fallback logic."""
        try:
            await wrapper.close()
            self._logger.debug("session_closed", session_id=wrapper.id)
        except Exception as e:
            self._logger.error(
                "session_close_error",
                session_id=wrapper.id,
                error=str(e),
            )

    async def close_all(self) -> None:
        """
        Close all active sessions.
        """
        self._logger.info(
            "closing_all_sessions",
            session_count=len(self._active_clients),
        )

        # P0 Fix: Close wrappers first to sync _closed state
        for session_id, wrapper in list(self._active_wrappers.items()):
            try:
                await wrapper.close()
                self._logger.debug("session_closed", session_id=session_id)
            except Exception as e:
                self._logger.error(
                    "session_close_error",
                    session_id=session_id,
                    error=str(e),
                )

        # Fallback: close any remaining clients not tracked via wrappers
        for session_id, client in list(self._active_clients.items()):
            if session_id not in self._active_wrappers:
                try:
                    await _close_client_with_process_fallback(
                        client,
                        self._logger,
                    )
                    self._logger.debug("session_closed", session_id=session_id)
                except Exception as e:
                    self._logger.error(
                        "session_close_error",
                        session_id=session_id,
                        error=str(e),
                    )

        # Clear both tracking dicts
        self._active_wrappers.clear()
        self._active_clients.clear()

        self._logger.info("all_sessions_closed")

    def get_active(self, session_id: str) -> ClaudeSDKClient | None:
        """Get an active client by ID."""
        return self._active_clients.get(session_id)

    def get_active_session_ids(self) -> list[str]:
        """Get list of all active session IDs."""
        return list(self._active_clients.keys())

    async def __aenter__(self) -> SessionManager:
        """Async context manager entry."""
        self._logger.debug("context_manager_enter")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        self._logger.debug("context_manager_exit", exc_type=exc_type)
        await self.close_all()


class ClaudeSessionWrapper:
    """Wrapper around ClaudeSDKClient to provide a session-like interface."""

    # P0 Fix: 可配置的超时时间（秒）- 默认 300 秒 (RC-1: 60s 不足以完成 agent 模式工具调用)
    DEFAULT_PROMPT_TIMEOUT: int = 900
    # A-1 Fix: 消息间最大空闲时间（秒）
    IDLE_TIMEOUT: int = 300

    def __init__(
        self,
        client: ClaudeSDKClient,
        session_id: str,
        work_dir: Path,
        options: ClaudeAgentOptions | None = None,  # P1 Fix: 保存 options
    ) -> None:
        """Initialize the wrapper.

        Args:
            client: The ClaudeSDKClient instance.
            session_id: Unique session identifier.
            work_dir: Working directory for the session.
            options: Optional ClaudeAgentOptions for unified API usage.
        """
        self._client = client
        self._id = session_id
        self._work_dir = work_dir
        self._options = options  # P1 Fix: 保存 options
        self._logger = logger.bind(
            component="ClaudeSessionWrapper",
            session_id=session_id,
        )
        # A-1 Fix: 防止并发 prompt() 调用
        self._prompt_lock = asyncio.Lock()
        # P0 Fix: session 状态标记
        self._closed = False

    @property
    def id(self) -> str:
        """Get the session ID."""
        return self._id

    async def prompt(
        self,
        message: str,
        timeout: int | None = None,
    ) -> AsyncIterator[Any]:
        """Send a prompt and yield streaming responses via SDK query API.

        P0 Fix: 添加 asyncio.timeout 保护，防止 receive_messages 永久阻塞。
        A-1 Fix: 添加 idle watchdog，检测消息间空闲超时。
        P0 Fix: timeout 后主动关闭 session，防止异常 transport 残留。

        Args:
            message: The message to send.
            timeout: Optional timeout in seconds. Defaults to DEFAULT_PROMPT_TIMEOUT.

        Yields:
            Message responses from Claude.

        Raises:
            LLMError: 当超时或 SDK 调用失败时抛出。
        """
        # P0 Fix: 拒绝已关闭 session 的复用
        if self._closed:
            raise LLMError(
                "Session is closed/unusable. Create a new session."
            )

        # A-1 Fix: 拒绝并发 prompt 调用
        if self._prompt_lock.locked():
            raise LLMError(
                "Concurrent prompt() call detected on the same session. "
                "ClaudeSessionWrapper does not support concurrent prompts."
            )

        async with self._prompt_lock:
            # 使用指定的超时或默认值
            effective_timeout = timeout if timeout is not None else self.DEFAULT_PROMPT_TIMEOUT

            try:
                await self._client.query(message)
            except Exception as e:
                self._logger.error("query_failed", error=str(e))
                raise LLMError(f"Failed to send query: {e}") from e

            # A-1 Fix: 启动 idle watchdog（使用 Event 通知主循环）
            last_msg_at = asyncio.get_event_loop().time()
            messages_received = 0
            idle_event = asyncio.Event()
            idle_reason = ""

            async def _idle_watchdog() -> None:
                nonlocal idle_reason
                while True:
                    await asyncio.sleep(self.IDLE_TIMEOUT / 2)
                    idle = asyncio.get_event_loop().time() - last_msg_at
                    if idle > self.IDLE_TIMEOUT:
                        idle_reason = (
                            f"Transport idle: no message for {idle:.1f}s "
                            f"(received {messages_received} msgs)"
                        )
                        self._logger.error(
                            "prompt_idle_exceeded",
                            idle_seconds=round(idle, 1),
                            messages_received=messages_received,
                        )
                        idle_event.set()
                        return

            watchdog = asyncio.create_task(_idle_watchdog())
            receive_gen = self._client.receive_messages()

            try:
                async with asyncio.timeout(effective_timeout):
                    while True:
                        # 竞争：下一条消息 vs idle watchdog
                        anext_task = asyncio.create_task(receive_gen.__anext__())
                        event_task = asyncio.create_task(idle_event.wait())
                        done, pending = await asyncio.wait(
                            [anext_task, event_task],
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        for p in pending:
                            p.cancel()
                            with suppress(asyncio.CancelledError):
                                await p
                        if idle_event.is_set():
                            raise LLMError(idle_reason)
                        try:
                            msg = await anext_task
                        except StopAsyncIteration:
                            break
                        last_msg_at = asyncio.get_event_loop().time()
                        messages_received += 1
                        # A-4 Fix: 记录消息元数据
                        self._logger.info(
                            "llm_message_received",
                            msg_type=type(msg).__name__,
                            message_index=messages_received,
                            has_role=getattr(msg, "role", None) is not None,
                        )
                        yield msg
            except LLMError:
                # P0 Fix: idle timeout 后主动清理 session
                self._closed = True
                await self.close()
                raise
            except TimeoutError as e:
                self._logger.error(
                    "prompt_timeout",
                    timeout_seconds=effective_timeout,
                    message_length=len(message),
                    messages_received_before_timeout=messages_received,
                )
                # P0 Fix: total timeout 后主动清理 session
                self._closed = True
                await self.close()
                raise LLMError(
                    f"Session prompt timed out after {effective_timeout} seconds"
                ) from e
            except Exception as e:
                self._logger.error("receive_messages_error", error=str(e))
                # P0 Fix: 异常路径也应关闭 session，防止 transport 残留
                self._closed = True
                await self.close()
                raise LLMError(f"Failed to receive messages: {e}") from e
            finally:
                watchdog.cancel()
                with suppress(asyncio.CancelledError):
                    await watchdog

    async def close(self) -> None:
        """Close the session.

        P0 Fix: 使用共享 helper 实现 disconnect 前捕获 process、timeout 后硬杀兜底。
        """
        self._closed = True
        await _close_client_with_process_fallback(
            self._client,
            self._logger,
        )


# Define public API - KimiSessionManager removed
__all__ = [
    "SessionManager",
    "ClaudeSessionWrapper",
]

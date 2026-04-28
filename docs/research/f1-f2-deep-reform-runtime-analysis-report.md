# F1/F2 问题深度研究报告

**生成时间**: 2026-04-07T20:46:19.158203
**分析工具**: tools/f1_f2_deep_dive_analyzer.py

## 执行摘要

| 严重级别 | 数量 |
|---------|------|
| CRITICAL | 3 |
| HIGH | 1 |
| MEDIUM | 5 |
| LOW | 0 |

---

## 详细发现

### F1-001: SessionManager._build_allowed_tools() 无条件添加 Skill 工具

**类别**: F1
**严重级别**: CRITICAL
**影响文件**: autoBMAD/docuswarm/llm/session_manager.py

**描述**:
> SessionManager._build_allowed_tools() 方法无条件地将 'Skill' 添加到 allowed_tools 列表中，没有检查 NodeSkillsConfig.sdk_native 开关。这意味着即使 sdk_native=False，Skills 仍然会被启用。

**证据**:

- 代码中直接执行 tools.append("Skill")，没有条件判断
- 方法内没有引用 self._tool_permissions.skills.sdk_native

**修复建议**:
```
在添加 'Skill' 之前检查 self._tool_permissions.skills.sdk_native 是否为 True
```

---

### F1-003: IndependentAgent.execute_with_input() 重建 NodeToolPermissions 时丢失配置

**类别**: F1
**严重级别**: CRITICAL
**影响文件**: autoBMAD/docuswarm/agents/independent.py

**描述**:
> IndependentAgent.execute_with_input() 方法在创建 full_tool_permissions 时，缺少 skills 配置 缺少 shared_context 配置。这导致从 node.yaml 加载的 skills 和 shared_context 配置在运行时丢失。

**证据**:

- 代码片段显示只传递了 allowed_builtin_tools, file_permissions, search_permissions
- node_config.tool_permissions.skills 没有被传递到新的 NodeToolPermissions
- node_config.tool_permissions.shared_context 没有被传递到新的 NodeToolPermissions

**修复建议**:
```
在创建 full_tool_permissions 时，从 node_config.tool_permissions 复制所有字段，
或者使用 dataclasses.replace() 来保留所有现有配置。
```

---

### F2-001: NodeToolFilter.get_allowed_tools() 未放行 submit_execution_report

**类别**: F2
**严重级别**: CRITICAL
**影响文件**: autoBMAD/docuswarm/llm/tool_filter.py

**描述**:
> NodeToolFilter.get_allowed_tools() 方法只放行 create_deliverable 工具，但没有放行 submit_execution_report 工具。尽管 submit_execution_report 工具已在 create_deliverable_sdk.py 中实现并在 MCP server 中注册，但由于不在 allowed_tools 列表中，Claude SDK 无法调用它。

**证据**:

- get_allowed_tools() 方法中只有 create_deliverable 被添加到 tools 列表
- submit_execution_report 没有在 get_allowed_tools() 中被添加
- 工具在 MCP server 中注册但不放行，导致运行时无法调用

**修复建议**:
```
在 get_allowed_tools() 方法中添加 submit_execution_report 工具：
if self.output_dir:
    tools.append(...)  # create_deliverable
    tools.append(MCP_TOOL_NAME_FORMAT.format(...submit_execution_report...))
```

---

### F2-002: submit_execution_report 工具实现状态

**类别**: F2
**严重级别**: INFO
**影响文件**: autoBMAD/docuswarm/tools/create_deliverable_sdk.py

**描述**:
> submit_execution_report 工具已在 create_deliverable_sdk.py 中完整实现：
- 函数定义: ✓ 存在
- MCP 注册: ✓ 存在
- 在 tools 列表: ✓ 存在
但由于 NodeToolFilter 不放行，运行时仍无法调用。

**证据**:

- SUBMIT_EXECUTION_REPORT_SCHEMA 已定义 (line 28-83)
- submit_execution_report 函数已定义 (line 167-202)
- submit_execution_report_tool MCP handler 已定义 (line 288-308)
- 在 create_deliverable_server 中注册到 tools 列表 (line 317)

**修复建议**:
```
修复 NodeToolFilter.get_allowed_tools() 以放行此工具
```

---

### F1-004: skills.whitelist 仅用于 prompt 注入，不是运行时权限边界

**类别**: F1
**严重级别**: HIGH
**影响文件**: autoBMAD/docuswarm/prompts/skill_injector.py, autoBMAD/docuswarm/llm/session_manager.py

**描述**:
> skills.whitelist 配置仅在 SkillInjector.build_skills_quick_reference() 中使用，用于在 system prompt 中注入可用技能列表。但这只是提示词层面的'建议'，不是真正的运行时权限边界。由于 SessionManager 无条件启用所有 Skills，LLM 仍然可以调用不在 whitelist 中的技能。

**证据**:

- skill_injector.py 只构建 quick reference 文本
- whitelist 不传递给 ClaudeAgentOptions 的任何权限控制参数
- SDK 的 Skills 机制目前不支持细粒度的单个技能控制

**修复建议**:
```
方案1: 使用 SDK 原生 Skill 工具时，所有技能都会暴露，whitelist 仅作为提示
方案2: 考虑在 Skill 内容加载层添加过滤（如果 SDK 支持）
方案3: 更新文档明确说明 whitelist 的局限性
```

---

### F1-NODE-analyst: 节点 analyst 的 sdk_native=true 但运行时未生效

**类别**: F1
**严重级别**: MEDIUM
**影响文件**: autoBMAD/nodes/analyst/node.yaml

**描述**:
> 节点 analyst 的 node.yaml 设置了 sdk_native=true，whitelist=['bmad-product-brief', 'bmad-domain-research', 'bmad-market-research', 'bmad-advanced-elicitation']，但由于 SessionManager 无条件启用 Skill，这个配置实际上被忽略了。

**证据**:

- node.yaml 设置: sdk_native=True
- node.yaml 设置: whitelist=['bmad-product-brief', 'bmad-domain-research', 'bmad-market-research', 'bmad-advanced-elicitation']
- 但 SessionManager 不检查这些设置

**修复建议**:
```
修复 SessionManager 以尊重 node.yaml 的 skills 配置
```

---

### F1-NODE-architect: 节点 architect 的 sdk_native=true 但运行时未生效

**类别**: F1
**严重级别**: MEDIUM
**影响文件**: autoBMAD/nodes/architect/node.yaml

**描述**:
> 节点 architect 的 node.yaml 设置了 sdk_native=true，whitelist=['bmad-create-architecture', 'bmad-technical-research', 'bmad-advanced-elicitation']，但由于 SessionManager 无条件启用 Skill，这个配置实际上被忽略了。

**证据**:

- node.yaml 设置: sdk_native=True
- node.yaml 设置: whitelist=['bmad-create-architecture', 'bmad-technical-research', 'bmad-advanced-elicitation']
- 但 SessionManager 不检查这些设置

**修复建议**:
```
修复 SessionManager 以尊重 node.yaml 的 skills 配置
```

---

### F1-NODE-pm: 节点 pm 的 sdk_native=true 但运行时未生效

**类别**: F1
**严重级别**: MEDIUM
**影响文件**: autoBMAD/nodes/pm/node.yaml

**描述**:
> 节点 pm 的 node.yaml 设置了 sdk_native=true，whitelist=['bmad-create-prd', 'bmad-edit-prd', 'bmad-validate-prd', 'bmad-advanced-elicitation']，但由于 SessionManager 无条件启用 Skill，这个配置实际上被忽略了。

**证据**:

- node.yaml 设置: sdk_native=True
- node.yaml 设置: whitelist=['bmad-create-prd', 'bmad-edit-prd', 'bmad-validate-prd', 'bmad-advanced-elicitation']
- 但 SessionManager 不检查这些设置

**修复建议**:
```
修复 SessionManager 以尊重 node.yaml 的 skills 配置
```

---

### F1-NODE-po: 节点 po 的 sdk_native=true 但运行时未生效

**类别**: F1
**严重级别**: MEDIUM
**影响文件**: autoBMAD/nodes/po/node.yaml

**描述**:
> 节点 po 的 node.yaml 设置了 sdk_native=true，whitelist=['bmad-create-epics-and-stories', 'bmad-sprint-planning', 'bmad-advanced-elicitation']，但由于 SessionManager 无条件启用 Skill，这个配置实际上被忽略了。

**证据**:

- node.yaml 设置: sdk_native=True
- node.yaml 设置: whitelist=['bmad-create-epics-and-stories', 'bmad-sprint-planning', 'bmad-advanced-elicitation']
- 但 SessionManager 不检查这些设置

**修复建议**:
```
修复 SessionManager 以尊重 node.yaml 的 skills 配置
```

---

### F1-NODE-ux: 节点 ux 的 sdk_native=true 但运行时未生效

**类别**: F1
**严重级别**: MEDIUM
**影响文件**: autoBMAD/nodes/ux/node.yaml

**描述**:
> 节点 ux 的 node.yaml 设置了 sdk_native=true，whitelist=['bmad-create-ux-design', 'bmad-advanced-elicitation']，但由于 SessionManager 无条件启用 Skill，这个配置实际上被忽略了。

**证据**:

- node.yaml 设置: sdk_native=True
- node.yaml 设置: whitelist=['bmad-create-ux-design', 'bmad-advanced-elicitation']
- 但 SessionManager 不检查这些设置

**修复建议**:
```
修复 SessionManager 以尊重 node.yaml 的 skills 配置
```

---

## 关键代码片段

### SessionManager._build_allowed_tools

```python
    def _build_allowed_tools(self) -> list[str]:
        """Build the complete list of allowed tools.

        This method combines:
        1. "Skill" tool (first for priority access to SDK native skills)
        2. Built-in tools (Read, Glob, Grep, Edit, Bash)
        3. MCP tools from NodeToolFilter (if configured)

        Returns:
            List of allowed tool names with "Skill" as the first entry.
        """
        tools: list[str] = []

        # Add "Skill" tool as first entry for SDK native skills priority
        tools.append("Skill")

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
        # Determine permission mode based on yolo
        permission_mode = "bypassPermissions" if yolo else "default"

        options_dict: dict[str, Any] = {
            "cwd": self._cwd,  # FIX-2B: Use _cwd instead of _work_dir for SDK import
            "permission_mode": permission_mode,
            "setting_sources": [
                "project"
            ],  # Enable SDK auto-discovery of skills from .claude/skills/
        }

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
                    mcp_servers = node_filter.create_mcp_servers()
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

    async def close_all(self) -> None:
        """
        Close all active sessions.
        """
        self._logger.info(
            "closing_all_sessions",
            session_count=len(self._active_clients),
        )

        # Close all tracked clients
        for session_id, client in list(self._active_clients.items()):
            try:
                await client.disconnect()
                self._logger.debug("session_closed", session_id=session_id)
            except Exception as e:
                self._logger.error(
                    "session_close_error",
                    session_id=session_id,
                    error=str(e),
                )

        # Clear the active clients dict
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


```

### SessionManager._create_options (setting_sources)

```python
            "cwd": self._cwd,  # FIX-2B: Use _cwd instead of _work_dir for SDK import
            "permission_mode": permission_mode,
            "setting_sources": [
                "project"
            ],  # Enable SDK auto-discovery of skills from .claude/skills/
```

### NodeToolFilter.get_allowed_tools

```python
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
        if self.output_dir:
            tools.append(
                MCP_TOOL_NAME_FORMAT.format(
                    type="deliverable", node_id=self.node_id, tool_name="create_deliverable"
                )
            )

        logger.debug(f"Node {self.node_id} has {len(tools)} allowed tools: {tools}")
        return tools

    def create_mcp_servers(self) -> dict[str, Any]:
        """Create SDK MCP servers based on configured permissions.

        This method creates and returns SDK MCP server dicts for file reading
        and search tools based on the node's permissions. The servers can be
        registered with ClaudeAgentOptions.

        Returns:
            Dict mapping server names to SDK MCP server dicts.
            Format: {server_name: sdk_mcp_server_dict}

        Raises:
            FileToolError: If file server creation fails.
            SearchToolError: If search server creation fails.

        Example:
            >>> filter_obj = NodeToolFilter.from_node_config(config)
            >>> servers = filter_obj.create_mcp_servers()
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


```

### IndependentAgent NodeToolPermissions 重建

```python
            NodeFilePermissions,
            NodeSearchPermissions,
            NodeToolPermissions,
        )

        full_tool_permissions = NodeToolPermissions(
            allowed_builtin_tools=node_config.tool_permissions.allowed_builtin_tools,
            file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
            search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
        )

        # Create new session manager with full configuration for this pipeline execution
        # P0 Fix: Pass complete tool_permissions instead of just file_dirs/search_dirs
        pipeline_session_manager = self._create_pipeline_session_manager(
            work_dir=output_dir,
            node_id=self.node_id,
            file_dirs=file_dirs,
            search_dirs=search_dirs,
            tool_permissions=full_tool_permissions,
        )
```

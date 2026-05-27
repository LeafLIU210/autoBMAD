"""Independent Agent Implementation - Story 2.6, Updated for Story 7.3, 7.4, and 8.4.

This module provides the IndependentAgent class which:
- Loads BMAD persona from nodes/{node_id}/persona.json
- Calls LLM with Claude Agent mode (temperature 0.7, max_tokens 32768)
- Tool calling handled entirely by SDK auto-dispatch (Story 8.4)
- Generates questions with priorities: clarifying, optional
- Preserves private reasoning (NOT shared with Evaluator)
- Returns structured output matching IndependentOutput schema
- Updated to support SessionManager (Story 7.3)
- Updated to use Session API (Story 7.4)
- Removed manual tool parsing - SDK handles all tool dispatch (Story 8.4)
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, override

import structlog

from autoBMAD.docuswarm.agents.base import BaseAgent
from autoBMAD.docuswarm.agents.persona import PersonaLoader
from autoBMAD.docuswarm.context import ContextValidator
from autoBMAD.docuswarm.llm.response import (
    ResponseParseError,
    extract_json,
)
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.prompts.contract_builder import create_contract_builder
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector
from autoBMAD.docuswarm.prompts.template_engine import PromptBuildConfig, PromptTemplateEngine

if TYPE_CHECKING:
    from autoBMAD.docuswarm.node_execution.contracts import IndependentAgentInput
    from autoBMAD.docuswarm.prompts.contract_builder import IndependentPromptContract

# Type alias for independent agent output
IndependentOutput = dict[str, Any]


class IndependentAgentError(Exception):
    """Base exception for IndependentAgent errors."""

    pass


class PersonaLoadError(IndependentAgentError):
    """Raised when persona loading fails."""

    pass


class LLMCallError(IndependentAgentError):
    """Raised when LLM API call fails."""

    pass


class SessionError(IndependentAgentError):
    """Raised when session creation or management fails (Story 7.4)."""

    pass


class ResponseParseAgentError(IndependentAgentError):
    """Raised when response parsing fails."""

    pass


class IndependentAgent(BaseAgent):
    """Independent Agent for creating deliverables and generating questions.

    This agent loads a BMAD persona, calls the LLM with SDK auto-dispatch,
    and produces structured output with deliverables and questions.

    Attributes:
        node_id: The node identifier for persona loading.
    """

    def __init__(
        self,
        # NOTE: Using Any because the config package shadows config.py and
        # dynamically imports Config, which basedpyright cannot resolve as a type.
        config: Any,
        session_manager: SessionManager,
        node_id: str = "dev",
        project_root: Path | None = None,
    ) -> None:
        """Initialize the IndependentAgent.

        Args:
            config: Agent configuration object (Config instance).
            session_manager: SessionManager for SDK interactions.
            node_id: The node identifier for loading persona from nodes/{node_id}/persona.json.
            project_root: Root directory of the project. If None, uses cwd.

        Raises:
            PersonaLoadError: If persona loading fails.
        """
        super().__init__(config, session_manager=session_manager)
        self.node_id = node_id
        self.project_root = project_root or Path.cwd()

        # Story 11.1: Instance variables for agent_file and work_dir
        self._agent_file: Path | None = self._build_agent_file_path()
        self._work_dir: Path | None = None

        # Initialize contract builder (P0: Node Prompt Contract Builder)
        self.contract_builder = create_contract_builder()

        # Story 29.6: Initialize PromptTemplateEngine for Four-Layer Architecture
        self._prompt_engine = PromptTemplateEngine(self.project_root)

        # Load persona
        try:
            self.persona = PersonaLoader.load(
                node_id=node_id,
                project_root=self.project_root,
                use_cache=True,
            )
        except Exception as e:
            raise PersonaLoadError(f"Failed to load persona for node '{node_id}': {e}") from e

        # Rebind logger with agent name
        self.logger: structlog.stdlib.BoundLogger = structlog.get_logger().bind(
            agent=self.__class__.__name__,
            node_id=node_id,
        )

    def _build_agent_file_path(self) -> Path | None:
        """Build agent file path based on project_root.

        P1-2 Fix: Uses path existence instead of fragile string matching.
        Tries both repo_root and package_root conventions.
        """
        # Try package-root convention first (project_root is the autoBMAD/ dir)
        path_via_package = (
            self.project_root
            / "docuswarm"
            / "agents"
            / "configs"
            / "independent_agent.yaml"
        )
        if path_via_package.exists():
            return path_via_package

        # Try repo-root convention (project_root is the repo root)
        path_via_repo = (
            self.project_root
            / "autoBMAD"
            / "docuswarm"
            / "agents"
            / "configs"
            / "independent_agent.yaml"
        )
        if path_via_repo.exists():
            return path_via_repo

        # Fallback: return the most likely path without existence check
        # (caller can handle missing file gracefully)
        return path_via_repo

    @override
    def _format_system_prompt(self) -> str:
        """Format system prompt with persona details and agent instructions.

        Returns:
            Formatted system prompt string including persona name, role,
            identity, expertise, principles, and agent-specific instructions.
        """
        # Use PersonaLoader's method to format persona
        persona_prompt = PersonaLoader.format_system_prompt(self.persona, max_tokens=2000)

        # Build complete system prompt with agent instructions
        # Story 11.2: Modified to use create_deliverable tool instead of inline JSON
        # P0 Single Truth: Include file_path and sha256 from tool output
        # TDD-07: Use MCP tool name format
        # Story 38.4: Added explicit submit_execution_report tool instructions
        create_deliverable_tool = f"mcp__docuswarm-deliverable-{self.node_id}__create_deliverable"
        submit_report_tool = f"mcp__docuswarm-deliverable-{self.node_id}__submit_execution_report"
        instructions = f"""## Agent Instructions

You are an Independent Agent that creates deliverables and generates questions.

## CRITICAL: Mandatory Tool Call Sequence (Story 38.4)

You MUST follow this exact tool call sequence:

### Step 1: Create Deliverable
Use the '{create_deliverable_tool}' tool to save your document:
- Parameters: title (string), content (Markdown string)
- Returns: file_path, sha256, word_count, section_index
- **IMPORTANT**: Save the returned file_path and sha256 for Step 2

### Step 2: Submit Execution Report (MANDATORY)
Use the '{submit_report_tool}' tool to submit your execution report:
- **WHEN**: Immediately AFTER successfully calling create_deliverable
- **WHY**: This provides structured metadata about your work and any questions

## Execution Workflow

1. **Create Deliverable**: Use '{create_deliverable_tool}' to save your document
   - The tool accepts: title (string) and content (Markdown string)
   - This writes the deliverable to a .md file
   - **CAPTURE**: file_path and sha256 from the tool result

2. **Submit Execution Report**: Use '{submit_report_tool}' to submit structured report
   - **REQUIRED**: Use the EXACT file_path and sha256 from Step 1
   - **REQUIRED**: Use the SAME title as provided to create_deliverable
   - **OPTIONAL**: Include clarifying questions with valid priority values

## submit_execution_report Tool Parameters

The execution report must contain:

```json
{{
  "deliverable": {{
    "title": "Same title used in create_deliverable",
    "file_path": "EXACT path from create_deliverable result - DO NOT MODIFY",
    "sha256": "EXACT hash from create_deliverable result - DO NOT MODIFY"
  }},
  "questions": [
    {{
      "question": "Your question text here?",
      "priority": "clarifying | optional",
      "context": "Why this question is relevant"
    }}
  ],
  "action": "create_deliverable"
}}
```

## Question Priority Enum Values (Story 38.4)

The questions[].priority field MUST be one of these three values:

| Priority | Description | When to Use |
|----------|-------------|-------------|
| **blocking** | Must be answered before proceeding | Use when missing critical information that prevents task completion. You MUST have an answer to proceed. |
| **clarifying** | Help refine the deliverable | Use for ambiguities or areas needing more detail to improve the document quality. |
| **optional** | Nice-to-have for future consideration | Use for suggestions or improvements that are not required now but may help in future. |

**IMPORTANT**: Any other value (e.g., "urgent", "high", "medium", "low") will be REJECTED.

## Tool Call Sequence Example (Story 38.4)

Here is the CORRECT sequence:

```
1. Call Tool: {create_deliverable_tool}
   Input: {{"title": "API Design Document", "content": "# API Design..."}}
   Output: {{
     "file_path": "/output/pipeline-123/api-design-document.md",
     "sha256": "a3f5c8e9d2b1f4e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0"
   }}

2. Call Tool: {submit_report_tool}
   Input: {{
     "deliverable": {{
       "title": "API Design Document",
       "file_path": "/output/pipeline-123/api-design-document.md",
       "sha256": "a3f5c8e9d2b1f4e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0"
     }},
     "questions": [
       {{
         "question": "Should we include rate limiting specifications?",
         "priority": "clarifying",
         "context": "Important for API scalability planning"
       }}
     ],
     "action": "create_deliverable"
   }}
   Output: {{"status": "success", "report": <your_report>}}
```

## CRITICAL REMINDERS

1. **ALWAYS call submit_execution_report AFTER create_deliverable** - Never skip this step
2. **Use EXACT file_path and sha256 values** - Do not modify or guess these values
3. **Use ONLY valid priority values**: "clarifying", "optional"
4. **action must be exactly**: "create_deliverable"
5. **The document content goes ONLY to create_deliverable** - submit_execution_report only needs metadata

## Hard Fallback Contract (when tools fail)

If and ONLY if BOTH tools fail (create_deliverable returns is_error:true
or submit_execution_report is unavailable), end your message with EXACTLY
these two lines on separate lines:

File: <absolute path you would have written>
SHA256: <64-hex-digit placeholder "0"*64>

Do NOT use this fallback if your tool calls succeeded.
"""
        return f"{persona_prompt}\n\n{instructions}"

    def _format_system_prompt_with_contract(
        self,
        contract: IndependentPromptContract,
    ) -> str:
        """Format system prompt using contract.

        P0: Node Prompt Contract Builder - 使用 contract 渲染 system prompt。

        Args:
            contract: Pre-built IndependentPromptContract.

        Returns:
            Formatted system prompt string.
        """
        return self.contract_builder.render_independent_system_prompt(contract)

    async def _call_llm(self, user_message: str) -> list[dict[str, Any]]:
        """Call the LLM using Four-Layer Architecture (Story 29.6).

        Uses session_manager.create_session() with mode="agent" and yolo=True
        for automatic tool call approval. Creates prompts using PromptTemplateEngine
        with Layers 2+3+4 for system_prompt_append.

        Args:
            user_message: The user message to send.

        Returns:
            list[dict[str, Any]] from the LLM.

        Raises:
            LLMCallError: If the LLM call fails.
            SessionError: If session creation fails.
        """
        # Story 29.6: Build prompts using Four-Layer Architecture
        # Layer 2+3+4: Build system_prompt_append using PromptTemplateEngine
        config = PromptBuildConfig(
            persona_id=self.node_id,
            task_name=user_message[:100],  # Use message preview as task name
            deliverables=[],  # Can be populated from context if available
            skills=[self.node_id],  # Use node_id as skill identifier
        )
        system_prompt_append = self._prompt_engine.build_system_prompt_append(config)

        # User prompt is the pure task content
        user_prompt = user_message

        return await self._call_llm_with_prompts(
            system_prompt_append=system_prompt_append,
            user_prompt=user_prompt,
        )

    async def _call_llm_with_prompts(
        self,
        system_prompt_append: str,
        user_prompt: str,
        timeout: int = 900,  # RC-1 Fix: timeout parameter with 900s default (was 60)
        on_session_created: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Call LLM with Four-Layer Architecture prompts (Story 29.6).

        Uses ClaudeAgentOptions preset format with system_prompt_append containing
        Layers 2+3+4 (Persona, Task Context, Skills). Layer 1 (claude_code preset)
        is provided by the SDK.

        Creates a session with mode="agent" and yolo=True for auto-approval.
        Uses SessionManager to collect messages.

        Story 29.6: This method receives system_prompt_append (Layers 2+3+4) and
        user_prompt separately, passing them to the SDK via preset format.

        Args:
            system_prompt_append: System prompt append containing Layers 2+3+4
                (Persona + Task Context + Skills) to append to claude_code preset.
            user_prompt: The user prompt with pure task content.

        Returns:
            list[dict[str, Any]] from the LLM.

        Raises:
            SessionError: If session creation or message processing fails.
            LLMCallError: On SDK exceptions like MaxStepsReached, RunCancelled.
        """
        # Story 31.5: Inject skills quick reference into system prompt
        # Load node config to get skill permissions and append skills section
        try:
            from autoBMAD.nodes.loader import NodeLoader

            node_config = NodeLoader.load(self.node_id)
            skills_config = node_config.tool_permissions.skills

            # Check if quick reference is enabled and we have a whitelist
            if skills_config.quick_reference_enabled and skills_config.whitelist:
                skills_quick_ref = SkillInjector.build_skills_quick_reference(
                    skills_config.whitelist
                )
                if skills_quick_ref:
                    # Append skills section after Layer 3 (task section)
                    system_prompt_append = f"{system_prompt_append}\n\n{skills_quick_ref}"
                    self.logger.debug(
                        "skills_quick_reference_injected",
                        node_id=self.node_id,
                        skill_count=len(skills_config.whitelist),
                    )
        except Exception as e:
            # Graceful handling: log warning and continue without skills section
            self.logger.warning(
                "skills_injection_failed",
                node_id=self.node_id,
                error=str(e),
                error_type=type(e).__name__,
            )

        messages: list[dict[str, Any]] = []

        try:
            # P2 Fix: 记录 prompt 开始
            self.logger.info(
                "llm_prompt_start",
                user_prompt_length=len(user_prompt),
                system_prompt_length=len(system_prompt_append),
            )

            # Create session with mode="agent" and yolo=True for auto-approval (Story 7.4)
            # Story 29.6: Use preset format with system_prompt_append
            sm = self.session_manager
            assert sm is not None

            # Story 29.6: Pass system_prompt to create_session
            # The SDK will use claude_code preset + system_prompt (Layers 2+3+4)
            session = await sm.create_session(
                mode="agent",
                yolo=True,
                agent_file=self._agent_file,
                system_prompt=system_prompt_append,
            )
            # P0-2 Fix: Notify caller of session creation for persistence
            if on_session_created is not None:
                try:
                    on_session_created(session.id)
                except Exception:
                    self.logger.warning("session_created_callback_failed", exc_info=True)

            # P2 Fix: 记录每个收到的消息
            message_count = 0
            async for msg in session.prompt(user_prompt, timeout=timeout):  # FIX-1: pass timeout
                message_count += 1

                # 记录消息类型
                msg_type = type(msg).__name__
                self.logger.debug(
                    "llm_message_received",
                    message_index=message_count,
                    msg_type=msg_type,
                    has_role=hasattr(msg, "role"),
                )

                if isinstance(msg, dict):
                    messages.append(msg)
                else:
                    # Fix: 使用 SessionManager._message_to_dict 进行转换
                    # 而非直接 getattr，以正确处理无 role 属性的 SDK 消息
                    # 使用 sm 变量 (已通过 assert 验证不为 None)
                    msg_dict = sm._message_to_dict(msg)
                    if msg_dict:
                        messages.append(msg_dict)

            # P2 Fix: 记录 prompt 完成
            self.logger.info(
                "llm_prompt_complete",
                message_count=len(messages),
                total_received=message_count,
            )

            # Return messages
            if not messages:
                raise LLMCallError("No messages returned from session")

            return messages

        except Exception as e:
            # Handle errors gracefully
            self.logger.warning("llm_call_error", error=str(e), error_type=type(e).__name__)
            # Return partial messages if available
            if messages:
                return messages
            raise LLMCallError(f"LLM call failed: {e}") from e

    def _extract_content_from_messages(self, messages: list[dict[str, Any]]) -> str:
        """Extract text content from messages.

        Args:
            messages: List of message dicts.

        Returns:
            Extracted text content, or empty string if none found.
        """
        # Get content from the last message with content
        for msg in reversed(messages):
            content = msg.get("content", [])
            if content:
                # Handle different content formats
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Extract text from content parts
                    texts = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            texts.append(part.get("text", ""))
                    return "".join(texts)
        return ""

    @staticmethod
    def _unwrap_tool_result_content(content_list: list[Any]) -> dict[str, Any] | None:
        """解包 MCP SDK tool_result 的 list[dict] content 为 dict.

        MCP SDK 契约 (claude-agent-sdk create_sdk_mcp_server):
            tool_result["content"] = [{"type":"text","text": json.dumps(result)}]
        本方法遍历 list，取第一个 type=='text' 的 text 字段并 json.loads。

        Args:
            content_list: tool_result block 的 content 字段（list 形态）。

        Returns:
            解析后的 dict，或 None（无可解析 text block）。
        """
        import json as json_module

        for b in content_list:
            if isinstance(b, dict) and b.get("type") == "text":
                try:
                    return json_module.loads(b.get("text", ""))
                except json_module.JSONDecodeError:
                    continue
        return None

    _FILE_SHA_RE = re.compile(
        r"^\s*File:\s*(?P<file>\S+)\s*\n\s*SHA256:\s*(?P<sha>[0-9a-fA-F]{64})\s*$",
        re.MULTILINE,
    )

    def _extract_file_sha_from_markdown(
        self, content: str
    ) -> tuple[str | None, str | None]:
        """从 Markdown 文本中正则抓取 File:/SHA256: 作为最后一道防线.

        Args:
            content: LLM 返回的文本内容。

        Returns:
            (file_path, sha256) 元组，未找到时返回 (None, None)。
        """
        m = self._FILE_SHA_RE.search(content or "")
        if not m:
            return None, None
        return m.group("file"), m.group("sha").lower()

    def _extract_create_deliverable_result(
        self, messages: list[dict[str, Any]]
    ) -> tuple[str | None, str | None]:
        """从 messages 中提取 create_deliverable 工具的返回结果.

        数据链路验证 (来自 tools/timeout_root_cause_analyzer.py):
          sdk_adapter.adapt_to_claude() 将 metadata dict 序列化为 JSON字符串存入 content。
          因此 tool_result["content"] 是字符串，必须先 json.loads() 再检查 dict。

        Returns:
            (file_path, sha256) 元组，未找到时返回 (None, None)
        """
        import json as json_module

        for msg in messages:
            content_blocks = msg.get("content", [])
            if not isinstance(content_blocks, list):
                continue

            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                if block.get("is_error", False):
                    continue  # 跳过错误结果

                tool_output = block.get("content", {})

                # MCP SDK 契约：create_sdk_mcp_server 工具返回
                #   {"content":[{"type":"text","text": json.dumps(result)}]}
                # 必须先解包 list -> 第一个 type=='text' 的 text 字段 -> json.loads。
                if isinstance(tool_output, list):
                    decoded = self._unwrap_tool_result_content(tool_output)
                    if decoded is None:
                        continue
                    tool_output = decoded

                # 向后兼容: content 是 JSON字符串 (sdk_adapter 序列化结果)
                if isinstance(tool_output, str):
                    try:
                        tool_output = json_module.loads(tool_output)
                    except json_module.JSONDecodeError:
                        continue

                if isinstance(tool_output, dict) and "file_path" in tool_output:
                    return (
                        str(tool_output["file_path"]),
                        str(tool_output.get("sha256", "")),
                    )
        return None, None

    def _extract_submit_report_result(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract execution reports from submit_execution_report tool results.

        Story 38.3: Prioritizes submit_execution_report tool results over old parsing paths.
        F3: Updated to support multi-document workflows (returns list of reports).

        The tool returns: {"status": "success", "report": <execution_report>}
        where execution_report contains:
        - deliverable: {title, file_path, sha256, content_summary?} (single)
        - deliverables: List of {title, file_path, sha256, ...} (multi-document)
        - questions: List of {question, priority, context}
        - action: "create_deliverable"

        Args:
            messages: List of message dicts from LLM response.

        Returns:
            List of execution report dicts (may contain multiple for multi-document).
        """
        import json as json_module

        reports: list[dict[str, Any]] = []

        for msg in messages:
            content_blocks = msg.get("content", [])
            if not isinstance(content_blocks, list):
                continue

            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                if block.get("is_error", False):
                    continue  # Skip error results

                tool_output = block.get("content", {})

                # MCP SDK 契约：list[dict] 解包（同 _extract_create_deliverable_result）
                if isinstance(tool_output, list):
                    decoded = self._unwrap_tool_result_content(tool_output)
                    if decoded is None:
                        continue
                    tool_output = decoded

                # Handle JSON string content (SDK serialization)
                if isinstance(tool_output, str):
                    try:
                        tool_output = json_module.loads(tool_output)
                    except json_module.JSONDecodeError:
                        continue

                # Check for submit_execution_report result structure
                if isinstance(tool_output, dict):
                    if tool_output.get("status") == "success" and "report" in tool_output:
                        report = tool_output["report"]
                        if not isinstance(report, dict):
                            continue

                        # F3: 支持多文档格式 (deliverables 数组)
                        if "deliverables" in report and isinstance(report["deliverables"], list):
                            # 多文档格式：展开每个 deliverable 为独立 report
                            for i, deliverable in enumerate(report["deliverables"]):
                                reports.append({
                                    "deliverable": deliverable,
                                    "questions": report.get("questions", []) if i == 0 else [],
                                    "action": report.get("action", "create_deliverable"),
                                })
                        # F3: 支持单文档格式 (向后兼容)
                        elif "deliverable" in report:
                            reports.append(report)

        return reports

    def _parse_response(self, response: list[dict[str, Any]]) -> IndependentOutput:
        """Parse and validate LLM response against IndependentOutput schema.

        Story 38.3: Prioritizes submit_execution_report tool results over old parsing paths.
        Falls back to JSON content extraction if tool result is not available.

        Args:
            response: The list[dict[str, Any]] from the LLM.

        Returns:
            Parsed and validated output dictionary.

        Raises:
            ResponseParseAgentError: If parsing or validation fails.
        """
        # Story 38.3: First try to extract from submit_execution_report tool result
        # F3: Now returns list of reports (supports multi-document)
        submit_reports = self._extract_submit_report_result(response)
        if submit_reports:
            # F3: 处理多文档情况
            if len(submit_reports) == 1:
                # 单文档：保持原有格式
                data = submit_reports[0]
                self.logger.info(
                    "parse_response_using_submit_report",
                    deliverable_title=data.get("deliverable", {}).get("title"),
                    questions_count=len(data.get("questions", [])),
                )
            else:
                # F3: 多文档：包装为特殊格式
                first_report = submit_reports[0]
                data = {
                    "deliverable": {
                        "title": f"{self.node_id.upper()} Deliverables Set",
                        "type": "multi-document",
                        "documents": [r.get("deliverable", {}) for r in submit_reports],
                        "total_word_count": sum(
                            r.get("deliverable", {}).get("word_count", 0)
                            for r in submit_reports
                        ),
                    },
                    "questions": first_report.get("questions", []),
                    "action": "create_deliverable",
                }
                self.logger.info(
                    "parse_response_multi_document",
                    document_count=len(submit_reports),
                    questions_count=len(data.get("questions", [])),
                )
        else:
            # Fall back to extracting JSON from content
            content = self._extract_content_from_messages(response)

            if not content or not content.strip():
                raise ResponseParseAgentError("Empty response from LLM")

            # Try to extract JSON from the response
            data = self._extract_data_from_content(response, content)

        # Validate against IndependentOutput schema using ContextValidator
        validator = ContextValidator()
        validation_result = validator.validate_independent_output(data, node_id=self.node_id)
        if not validation_result.valid:
            # Log the first error for debugging
            if validation_result.issues:
                first_issue = validation_result.issues[0]
                self.logger.error(
                    "response_validation_failed",
                    field=first_issue.field,
                    message=first_issue.message,
                    code=first_issue.code,
                )
            raise ResponseParseAgentError(
                f"Response validation failed: {validation_result.issues[0].message if validation_result.issues else 'Unknown error'}"
            )

        return data

    def _extract_data_from_content(
        self, response: list[dict[str, Any]], content: str
    ) -> dict[str, Any]:
        """Extract execution report data from message content (fallback path).

        Args:
            response: The list[dict[str, Any]] from the LLM.
            content: Extracted text content from messages.

        Returns:
            Parsed data dictionary.

        Raises:
            ResponseParseAgentError: If extraction fails.
        """
        try:
            data: dict[str, Any] = extract_json(content)
            return data
        except ResponseParseError as e:
            # FIX-3: Extended fallback condition - handle any non-JSON content
            is_non_json_text = (
                content.strip().startswith(("#", "##", "###"))
                or "Summary" in content[:100]
                or not content.strip().startswith("{")  # NEW: Any non-JSON content
            )

            if is_non_json_text:
                content_type = "markdown" if content.strip().startswith("#") else "plain_text"
                self.logger.warning(
                    f"llm_returned_{content_type}_fallback",
                    attempting_fallback=True,
                    content_preview=content[:200],
                )

                # Fix-2: 先从工具调用历史中提取 file_path/sha256
                file_path, sha256 = self._extract_create_deliverable_result(response)

                if file_path:
                    # 工具已成功执行，补全 LLM 遗漏的字段
                    import re as re_module

                    title_match = re_module.search(r"^#+\s*(.+)$", content, re_module.MULTILINE)
                    title = title_match.group(1) if title_match else "LLM Generated Document"

                    data: dict[str, Any] = {
                        "deliverable": {
                            "title": title,
                            "content": content[:500] + "..." if len(content) > 500 else content,
                            "file_path": file_path,  # ✅ 来自工具真实返回
                            "sha256": sha256 or "",  # ✅ 来自工具真实返回
                        },
                        "questions": [],
                        "action": "create_deliverable",
                    }

                    self.logger.info(
                        f"{content_type}_fallback_success_with_tool_result",
                        constructed_title=title,
                        file_path=file_path,
                        content_length=len(content),
                    )
                    return data
                else:
                    # §7.4: 正则兜底 - 从 Markdown 文本中抓取 File:/SHA256:
                    file_path, sha256 = self._extract_file_sha_from_markdown(content)
                    if file_path:
                        self.logger.info(
                            "markdown_regex_fallback_hit",
                            file_path=file_path,
                            sha=sha256,
                        )

                        title_match = re.search(r"^#+\s*(.+)$", content, re.MULTILINE)
                        title = title_match.group(1) if title_match else "LLM Generated Document"

                        data: dict[str, Any] = {
                            "deliverable": {
                                "title": title,
                                "content": content[:500] + "..." if len(content) > 500 else content,
                                "file_path": file_path,
                                "sha256": sha256 or "",
                            },
                            "questions": [],
                            "action": "create_deliverable",
                        }
                        return data

                    # 工具未执行或结果丢失，拒绝处理，触发重试
                    raise ResponseParseAgentError(
                        f"LLM returned {content_type} instead of JSON, and no create_deliverable "
                        "tool result found in messages. LLM must call create_deliverable "
                        f"tool and include file_path in JSON response. Preview: {content[:200]}"
                    ) from e
            else:
                self.logger.error("response_parse_failed", error=str(e), content=content[:200])
                raise ResponseParseAgentError(f"Failed to parse response: {e}") from e

    @override
    async def execute(self, context: dict[str, Any]) -> IndependentOutput:
        """Execute the Independent Agent to create deliverables and generate questions.

        Args:
            context: Execution context containing:
                - task: The task description or user request
                - pipeline_id: Required for Story 11.1 - used to create work directory

        Returns:
            Dict containing:
                - deliverable: {title, content, metadata}
                - questions: List of {priority, question, context}
                - private_reasoning: Optional[str]

        Raises:
            IndependentAgentError: If execution fails.
        """
        # Extract task from context
        # Task can be at top level or inside subject_context
        task: str = ""
        raw_task = context.get("task")
        if isinstance(raw_task, str):
            task = raw_task
        if not task:
            # Try to get from subject_context
            subject_ctx = context.get("subject_context", {})
            if isinstance(subject_ctx, dict):
                raw_task = subject_ctx.get("task")
                if isinstance(raw_task, str):
                    task = raw_task
        if not task:
            raise IndependentAgentError("No task provided in context")

        # Story 11.1: Extract pipeline_id and setup work directory
        pipeline_id: str = context.get("pipeline_id", "")
        if not pipeline_id:
            raise IndependentAgentError("pipeline_id is required in context for Story 11.1")

        # ===== P1 Fix: Extract original context content =====
        import json as json_module

        subject_context_raw = context.get("subject_context", {})

        # Normalize subject_context (could be dict or JSON string)
        if isinstance(subject_context_raw, str):
            try:
                subject_context_data = json_module.loads(subject_context_raw)
            except json_module.JSONDecodeError:
                # If not valid JSON, wrap as simple dict
                subject_context_data = {"context": subject_context_raw}
        elif isinstance(subject_context_raw, dict):
            subject_context_data = subject_context_raw
        else:
            subject_context_data = {}

        # Extract context_content with explicit str type
        context_content: str = ""

        # Extract original context file content (support nested or flat structure)

        # Try path 1: subject_context.subject_context.content
        nested_ctx = subject_context_data.get("subject_context", {})
        if isinstance(nested_ctx, dict):
            raw_content = nested_ctx.get("content")
            if isinstance(raw_content, str):
                context_content = raw_content

        # Try path 2: subject_context.content (flat structure)
        if not context_content:
            raw_content = subject_context_data.get("content")
            if isinstance(raw_content, str):
                context_content = raw_content

        self.logger.info(
            "extracted_context_content",
            task_preview=task[:100] if task else "",
            has_context_content=bool(context_content),
            context_length=len(context_content) if context_content else 0,
        )
        # ===== End P1 Fix =====

        # Compute output directory: project_root / output / pipeline_id
        output_dir = self.project_root / "output" / pipeline_id

        # Create output directory with parents=True, exist_ok=True
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set instance variables for session creation (Story 11.1)
        self._agent_file = self._build_agent_file_path()
        self._work_dir = output_dir

        self.logger.info(
            "executing_independent_agent",
            node_id=self.node_id,
            task=task[:100],
            pipeline_id=pipeline_id,
            work_dir=str(self._work_dir),
            agent_file=str(self._agent_file),
        )

        # Story 11.1: Create a new session manager with the correct work_dir
        # The work_dir must be set on SessionManager constructor, not create_session()
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        # Create new session manager with work_dir for this pipeline execution
        pipeline_session_manager = SessionManager(
            work_dir=output_dir,
            agent_file=self._agent_file,
            config=self.session_manager.config if self.session_manager else None,
        )

        # Temporarily replace session_manager for this execution
        original_session_manager = self.session_manager
        self.session_manager = pipeline_session_manager

        # ===== P1 Fix: Build enriched_task with context =====
        if context_content:
            enriched_task = f"""## Original Context

{context_content}

## Task

{task}

Please create the deliverable based on the original context above. Reference specific details from the context in your analysis."""
        else:
            enriched_task = task
        # ===== End P1 Fix =====

        try:
            # Call LLM with enriched task (includes original context)
            response = await self._call_llm(user_message=enriched_task)
        finally:
            # Restore original session_manager
            self.session_manager = original_session_manager

        # Parse and validate response
        output = self._parse_response(response)

        self.logger.info(
            "independent_agent_completed",
            deliverable_title=output.get("deliverable", {}).get("title", "unknown"),  # type: ignore[reportAny]
            questions_count=len(output.get("questions", [])),  # type: ignore[arg-type]
        )

        return output

    async def execute_with_input(
        self,
        agent_input: IndependentAgentInput,
        pipeline_id: str,
        timeout: int = 900,  # RC-1 Fix: timeout parameter with 900s default (was 60)
        state_manager: Any | None = None,
    ) -> IndependentOutput:
        """Execute the Independent Agent with structured input (Single Context Protocol).

        This method receives a structured IndependentAgentInput instead of a raw context dict,
        eliminating the need for guessing and parsing.

        P0: Uses NodePromptContractBuilder to build structured prompts from node contract.

        Args:
            agent_input: Structured input containing task_name, task_description,
                deliverable_requirements, original_context_summary, etc.
            pipeline_id: The pipeline identifier for file output.
            timeout: Timeout in seconds for LLM calls (default: 900).

        Returns:
            Dict containing:
                - deliverable: {title, content, metadata}
                - questions: List of {priority, question, context}
                - private_reasoning: Optional[str]

        Raises:
            IndependentAgentError: If execution fails.
        """
        # Single Context Protocol: 直接从结构化输入读取字段
        # 使用 .get() 安全访问 TypedDict 的可选字段 (基于类型安全修复)
        task_name = agent_input.get("task_name", "")
        original_context = agent_input.get("original_context_summary", "")
        chained_deliverables = agent_input.get("chained_deliverables_summary", [])
        iteration_feedback = agent_input.get("iteration_feedback")
        shared_context = agent_input.get("shared_context", {})
        # F1 Fix: 获取 deliverable_requirements 和 deliverable_type
        deliverable_requirements = agent_input.get("deliverable_requirements", {})
        deliverable_type = agent_input.get("deliverable_type", "")

        # Compute output directory: project_root / output / pipeline_id
        output_dir = self.project_root / "output" / pipeline_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set instance variables for session creation
        self._agent_file = self._build_agent_file_path()
        self._work_dir = output_dir

        self.logger.info(
            "executing_independent_agent_with_input",
            node_id=self.node_id,
            task_name=task_name,
            pipeline_id=pipeline_id,
        )

        # P0: Build NodeExecutionContext from agent_input
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext

        # F4: 从 agent_input 读取 docs_context，而非强制设为空列表
        docs_context: list[dict[str, Any]] = agent_input.get("docs_context", [])
        context = NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=self.node_id,
            node_name=task_name,  # Fallback to task_name if node_name not in agent_input
            node_order=0,
            original_context={"content": original_context},
            chained_deliverables=chained_deliverables,
            shared_context=shared_context,
            iteration_feedback=iteration_feedback,
            docs_context=docs_context,
            # F1 Fix: 传递 deliverable_requirements 和 deliverable_type
            deliverable_requirements=deliverable_requirements,
            deliverable_type=deliverable_type,
        )

        # P0: Build contract from context using NodePromptContractBuilder
        contract = self.contract_builder.build_independent_contract(context)

        # P0: Render system and user prompts from contract
        system_prompt = self._format_system_prompt_with_contract(contract)
        user_prompt = self.contract_builder.render_independent_user_prompt(contract)

        # Load node config to get tool_permissions
        from autoBMAD.nodes.loader import NodeLoader

        node_config = NodeLoader.load(self.node_id)

        # Phase 4 Fix: Use project_root directly as repo root.
        # Removed dangerous .parent escape that could set cwd outside the repository.
        repo_root = self.project_root

        # Prepare permission directories (absolute paths from repo root)
        file_dirs = [
            str(repo_root / d)
            for d in node_config.tool_permissions.file_permissions.allowed_read_dirs
        ]
        search_dirs = [
            str(repo_root / d) for d in node_config.tool_permissions.search_permissions.search_dirs
        ]

        # P0 Fix: Build complete NodeToolPermissions with allowed_builtin_tools
        # F1 Fix: Use dataclasses.replace to preserve skills and shared_context
        from dataclasses import replace

        from autoBMAD.nodes.loader import (
            NodeFilePermissions,
            NodeSearchPermissions,
        )

        full_tool_permissions = replace(
            node_config.tool_permissions,
            file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
            search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
        )

        # Create new session manager with full configuration for this pipeline execution
        # P0 Fix: Pass complete tool_permissions instead of just file_dirs/search_dirs
        # F2 Fix: 传递 pipeline_id 以创建 shared-context MCP server
        # F3 Fix: 传递 repo_root 作为 project_root 以正确设置 SDK Skills 发现路径
        pipeline_session_manager = self._create_pipeline_session_manager(
            work_dir=output_dir,
            node_id=self.node_id,
            file_dirs=file_dirs,
            search_dirs=search_dirs,
            tool_permissions=full_tool_permissions,
            pipeline_id=pipeline_id,  # F2 Fix
            project_root=repo_root,  # F3 Fix
        )

        # Temporarily replace session_manager for this execution
        original_session_manager = self.session_manager
        self.session_manager = pipeline_session_manager

        try:
            # Story 29.6: Call LLM with Four-Layer Architecture
            # system_prompt from contract becomes system_prompt_append (Layers 2+3+4)
            # P0-2 Fix: Pass callback to persist session_id to state_manager
            def _on_session_created(session_id: str) -> None:
                if state_manager is not None:
                    try:
                        # Use asyncio.create_task to fire-and-forget the async update
                        # since we're inside an async call stack and _call_llm_with_prompts
                        # will continue immediately after this callback returns.
                        loop = asyncio.get_running_loop()
                        loop.create_task(
                            state_manager.update_pipeline_state(
                                pipeline_id,
                                {
                                    "current_node_session_id": session_id,
                                    "session_ids": [session_id],  # appended by StateManager merge
                                },
                            )
                        )
                    except Exception:
                        self.logger.warning("session_persistence_update_failed", exc_info=True)

            response = await self._call_llm_with_prompts(
                system_prompt_append=system_prompt,
                user_prompt=user_prompt,
                timeout=timeout,  # FIX-1: pass timeout
                on_session_created=_on_session_created,
            )
        finally:
            # Restore original session_manager
            self.session_manager = original_session_manager
            # Close the pipeline-scoped session manager to prevent resource leaks
            await pipeline_session_manager.close_all()

        # Parse and validate response
        output = self._parse_response(response)

        self.logger.info(
            "independent_agent_completed",
            deliverable_title=output.get("deliverable", {}).get("title", "unknown"),
            questions_count=len(output.get("questions", [])),
        )

        return output

    def _create_pipeline_session_manager(
        self,
        work_dir: Path,
        node_id: str,
        file_dirs: list[str],
        search_dirs: list[str],
        tool_permissions: Any | None = None,
        pipeline_id: str | None = None,  # F2 Fix: 添加 pipeline_id 参数
        project_root: Path | None = None,  # F3 Fix: 添加 project_root 参数
        db_path: str | None = None,  # H1 Fix: 传递数据库路径
    ):
        """Factory method for creating pipeline SessionManager - allows testing.

        F2 Fix: 支持 pipeline_id 参数以创建 shared-context MCP server
        F3 Fix: 支持 project_root 参数以正确设置 SDK Skills 发现路径
        H1 Fix: 支持 db_path 参数以写入配置的数据库
        """
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        return SessionManager(
            work_dir=work_dir,
            cwd=project_root or work_dir,  # F3 Fix: 使用 project_root 作为 cwd
            output_dir=work_dir,
            agent_file=self._agent_file,
            config=self.session_manager.config if self.session_manager else None,
            node_id=node_id,
            file_dirs=file_dirs,
            search_dirs=search_dirs,
            tool_permissions=tool_permissions,
            pipeline_id=pipeline_id,  # F2 Fix: 传递 pipeline_id
            db_path=db_path,  # H1 Fix: 传递 db_path
        )

    def _build_user_message(
        self,
        task_name: str,
        task_description: str,
        role_supplement: str,
        deliverable_reqs: dict[str, Any],
        original_context: str,
        chained_deliverables: list[dict[str, Any]],
        iteration_feedback: dict[str, Any] | None,
    ) -> str:
        """Build user message from structured fields (Single Context Protocol).

        Args:
            task_name: Task name from node config
            task_description: Task description from node config
            role_supplement: Role supplement from node config
            deliverable_reqs: Deliverable requirements dict
            original_context: Original context content
            chained_deliverables: List of upstream deliverable summaries
            iteration_feedback: Optional iteration feedback

        Returns:
            Formatted user message string
        """
        sections: list[str] = []

        # 任务契约
        sections.append(f"## 任务: {task_name}")
        sections.append(task_description)
        if role_supplement:
            sections.append(f"\n**角色补充**: {role_supplement}")

        # 交付物要求
        sections.append("\n## 交付物要求")
        if "required_sections" in deliverable_reqs:
            sections.append("必须包含以下章节:")
            for section in deliverable_reqs["required_sections"]:
                sections.append(f"- {section}")

        # 原始上下文
        if original_context:
            sections.append(f"\n## 原始上下文\n{original_context}")

        # 上游交付物
        if chained_deliverables:
            sections.append("\n## 上游交付物摘要")
            for item in chained_deliverables:
                sections.append(f"- **{item['node_id']}**: {item['title']}")

        # 迭代反馈
        if iteration_feedback:
            sections.append("\n## 迭代反馈")
            sections.append(f"上一轮评分: {iteration_feedback.get('alignment_score', 0)}")
            sections.append("需要改进的问题:")
            for issue in iteration_feedback.get("issues_found", []):
                sections.append(f"- {issue}")

        return "\n".join(sections)


# Convenience function for creating IndependentAgent
def create_independent_agent(
    # NOTE: Using Any because the config package shadows config.py and
    # dynamically imports Config, which basedpyright cannot resolve as a type.
    config: Any,
    session_manager: SessionManager,
    node_id: str = "dev",
    project_root: Path | None = None,
) -> IndependentAgent:
    """Create an IndependentAgent with configured session manager.

    Args:
        config: Agent configuration (Config instance).
        session_manager: SessionManager for SDK interactions.
        node_id: The node identifier for persona loading.
        project_root: Root directory of the project.

    Returns:
        Configured IndependentAgent instance.
    """
    return IndependentAgent(
        config=config,
        session_manager=session_manager,
        node_id=node_id,
        project_root=project_root,
    )


__all__ = [
    "IndependentAgent",
    "IndependentAgentError",
    "PersonaLoadError",
    "LLMCallError",
    "SessionError",
    "ResponseParseAgentError",
    "IndependentOutput",
    "create_independent_agent",
]
